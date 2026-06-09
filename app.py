"""
app.py
------
Milestone 5: Grounded generation + Gradio interface.

Wires together:
  pipeline.py          → ingestion + chunking
  embed_and_retrieve.py → embedding + retrieval
  Groq API             → llama-3.3-70b-versatile generation

Usage:
    python app.py
    Open http://localhost:7860

Requires:
    pip install groq gradio python-dotenv
"""

import os
from dotenv import load_dotenv
from groq import Groq
import gradio as gr
from sentence_transformers import SentenceTransformer

from pipeline import run_pipeline
from embed_and_retrieve import embed_and_store, retrieve, EMBEDDING_MODEL, TOP_K

# ── Load environment ──────────────────────────────────────────────────────────

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY not found. "
        "Copy .env.example to .env and add your key from console.groq.com."
    )

GROQ_MODEL = "llama-3.3-70b-versatile"

# ── System prompt — grounding is enforced here, not suggested ─────────────────

SYSTEM_PROMPT = """You are a helpful assistant for Berea College students looking up \
information about CS and Math professors based on Rate My Professors reviews.

STRICT RULES:
1. Answer ONLY using the review excerpts provided below. Do not use any outside knowledge.
2. If the provided reviews do not contain enough information to answer the question, \
say exactly: "I don't have enough information in the available reviews to answer that."
3. Never speculate or infer beyond what is explicitly stated in the reviews.
4. Always mention which professor(s) the information comes from in your answer.
5. Keep your answer concise and focused on what the reviews actually say.
6. When citing a review, refer to it as 'a student review of [Professor Name]', not as 'Review 1' or 'Review 4'."""

# ── Build prompt from retrieved chunks ───────────────────────────────────────

def build_prompt(question: str, chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a context block for the LLM.
    Each chunk is labelled with its source so the model can cite it.
    """
    context_lines = []
    for i, chunk in enumerate(chunks, 1):
        context_lines.append(
            f"[Source {i}: {chunk['professor_name']} review, {chunk['date']}]\n"
            f"{chunk['department']}, {chunk['date']}]\n"
            f"{chunk['text']}\n"
        )
    context = "\n".join(context_lines)

    return (
        f"Here are the relevant student reviews:\n\n"
        f"{context}\n"
        f"---\n"
        f"Question: {question}\n\n"
        f"Answer using only the reviews above. "
        f"If the reviews don't cover this question, say so explicitly."
    )


# ── Core ask() function ───────────────────────────────────────────────────────

def ask(question: str, top_k: int = TOP_K) -> dict:
    """
    End-to-end: retrieve relevant chunks, generate a grounded answer.

    Returns:
        {
            "answer":  str,          # LLM response grounded in retrieved chunks
            "sources": list[str],    # human-readable source citations
            "chunks":  list[dict],   # raw retrieved chunks (for inspection)
        }
    """
    # Retrieve
    chunks = retrieve(question, COLLECTION, MODEL, top_k=top_k)

    if not chunks:
        return {
            "answer": "I don't have enough information in the available reviews to answer that.",
            "sources": [],
            "chunks": [],
        }

    # Build prompt
    prompt = build_prompt(question, chunks)

    # Generate
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.2,    # low temperature = more faithful to source material
        max_tokens=512,
    )
    answer = response.choices[0].message.content.strip()

    # Build source list programmatically — not left to the LLM
    seen = set()
    sources = []
    for chunk in chunks:
        label = (
            f"{chunk['professor_name']} "
            f"({chunk['department']}) — "
            f"{chunk['date']} "
            f"[dist: {chunk['distance']}]"
        )
        if label not in seen:
            seen.add(label)
            sources.append(label)

    return {
        "answer":  answer,
        "sources": sources,
        "chunks":  chunks,
    }


# ── Gradio interface ──────────────────────────────────────────────────────────

def handle_query(question: str):
    """Gradio handler — returns (answer, sources) for display."""
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources_text = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources_text


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Berea College Unofficial Guide") as demo:

        gr.Markdown("""
# 📚 Berea College Unofficial Guide
**Ask anything about CS and Math professors — answers drawn from real student reviews.**

*Tip: Try "Who is the easiest math professor?" or "What do students say about Jan Pearce's grading?"*
        """)

        with gr.Row():
            with gr.Column(scale=3):
                question_box = gr.Textbox(
                    label="Your question",
                    placeholder="e.g. Which CS professor gives the most useful feedback?",
                    lines=2,
                )
                ask_btn = gr.Button("Ask", variant="primary")

        with gr.Row():
            with gr.Column(scale=3):
                answer_box = gr.Textbox(
                    label="Answer",
                    lines=10,
                    interactive=False,
                )
            with gr.Column(scale=2):
                sources_box = gr.Textbox(
                    label="Retrieved from (sources)",
                    lines=10,
                    interactive=False,
                )

        # Wire up button and Enter key
        ask_btn.click(
            handle_query,
            inputs=question_box,
            outputs=[answer_box, sources_box],
        )
        question_box.submit(
            handle_query,
            inputs=question_box,
            outputs=[answer_box, sources_box],
        )

        gr.Markdown("""
---
*Answers are grounded in Rate My Professors reviews collected from Berea College's \
CS and Mathematics departments. Sources shown are the specific reviews retrieved \
for each query.*
        """)

    return demo


# ── Startup: load models and collection once ──────────────────────────────────

def startup() -> tuple:
    """
    Load the embedding model and ChromaDB collection once at startup.
    Returns (collection, model) for use in ask().
    """
    print("=== Milestone 5: Generation + Interface ===\n")

    # Run ingestion pipeline
    chunks = run_pipeline()
    print()

    # Load or rebuild ChromaDB collection
    collection = embed_and_store(chunks)
    print()

    # Load embedding model
    print(f"Loading '{EMBEDDING_MODEL}' for retrieval...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Ready.\n")

    return collection, model


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Load shared resources into module-level globals so ask() can use them
    COLLECTION, MODEL = startup()

    # Quick smoke test before launching UI
    print("Running smoke test...\n")
    test_questions = [
        "What do students say about Jan Pearce's grading?",
        "Who is the easiest math professor at Berea?",
        "Does Berea College have a swimming pool?",   # should trigger "not enough info"
    ]
    for q in test_questions:
        print(f"Q: {q}")
        result = ask(q)
        print(f"A: {result['answer'][:300]}")
        print(f"Sources: {result['sources'][:2]}")
        print()

    # Launch Gradio
    print("Launching Gradio UI at http://localhost:7860 ...")
    demo = build_ui()
    demo.launch()