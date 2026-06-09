"""
pipeline.py
-----------
Milestone 3: Document ingestion and chunking for the Unofficial Guide RAG system.

Stages:
  1. load_documents()  — reads all JSON files from data/raw/, filters thin professors
  2. clean_review()    — strips junk from individual review comments
  3. chunk_documents() — one chunk per review, with metadata prefix

Usage:
    python pipeline.py

Output:
    Prints a summary and 5 random sample chunks for inspection.
    Returns chunks ready to pass to the embedding stage (Milestone 4).
"""

import json
import os
import random
import html
import re

# ── Config ────────────────────────────────────────────────────────────────────

DATA_DIR = "data/raw"
MIN_REVIEWS = 5          # professors below this are skipped
MIN_COMMENT_LEN = 10     # reviews shorter than this are skipped (noise)


# ── Stage 1: Load Documents ───────────────────────────────────────────────────

def load_documents(data_dir: str = DATA_DIR) -> list[dict]:
    """
    Load all professor JSON files from data_dir.
    Skips all_reviews.json (the combined file) and professors with < MIN_REVIEWS ratings.
    Returns a list of professor dicts, each with their reviews list intact.
    """
    documents = []

    if not os.path.exists(data_dir):
        raise FileNotFoundError(
            f"Directory '{data_dir}' not found. "
            "Run collect_rmp_data.py first to gather raw data."
        )

    json_files = [
        f for f in os.listdir(data_dir)
        if f.endswith(".json") and f != "all_reviews.json"
    ]

    if not json_files:
        raise ValueError(f"No JSON files found in '{data_dir}'.")

    for filename in sorted(json_files):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            doc = json.load(f)

        # Skip thin professors (already filtered at collection time, but double-check)
        if doc.get("num_ratings", 0) < MIN_REVIEWS:
            continue

        documents.append(doc)

    print(f"Loaded {len(documents)} professor documents from '{data_dir}'.")
    return documents


# ── Stage 2: Clean Reviews ────────────────────────────────────────────────────

def clean_review(comment: str) -> str:
    """
    Clean a single review comment.
    - Decode HTML entities (&amp; → &, &quot; → ", &#39; → ', &lt; → <, etc.)
    - Strip leftover HTML tags
    - Normalize whitespace
    - Return empty string if nothing substantive remains
    """
    if not comment or not comment.strip():
        return ""

    # Decode HTML entities (e.g. &quot; &amp; &#39; &lt; &gt; &nbsp;)
    text = html.unescape(comment)

    # Remove any residual HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Normalize whitespace (collapse multiple spaces/newlines)
    text = re.sub(r"\s+", " ", text).strip()

    # Skip very short comments — they carry no signal
    if len(text) < MIN_COMMENT_LEN:
        return ""

    return text


# ── Stage 3: Chunk Documents ──────────────────────────────────────────────────

def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    One chunk per review, with a metadata prefix.

    Each chunk format:
        Professor: <name> | Dept: <dept> | Rating: <X>/5 | Difficulty: <X>/5
        Course: <course>  (omitted if blank)
        Date: <date>
        Review: <comment>
        Tags: <tag1>, <tag2>  (omitted if none)

    Returns a list of chunk dicts:
        {
            "text":             str,   # the full chunk text fed to the embedder
            "professor_name":   str,
            "department":       str,
            "overall_rating":   float,
            "difficulty":       float,
            "review_quality":   float,
            "review_difficulty":float,
            "date":             str,
            "course":           str,
            "tags":             list[str],
            "source_file":      str,   # filename for attribution
        }
    """
    chunks = []
    skipped_empty = 0
    skipped_short = 0

    for doc in documents:
        prof_name   = doc.get("professor_name", "Unknown")
        department  = doc.get("department", "Unknown")
        overall     = doc.get("overall_rating") or 0.0
        difficulty  = doc.get("difficulty") or 0.0
        source_file = f"{prof_name.replace(' ', '_')}.json"

        # Build the metadata prefix — shared by every chunk for this professor
        meta_prefix = (
            f"Professor: {prof_name} | "
            f"Dept: {department} | "
            f"Overall Rating: {overall}/5 | "
            f"Difficulty: {difficulty}/5"
        )

        for review in doc.get("reviews", []):
            raw_comment = review.get("comment", "")
            comment = clean_review(raw_comment)

            if not comment:
                skipped_empty += 1
                continue

            if len(comment) < MIN_COMMENT_LEN:
                skipped_short += 1
                continue

            # Build the chunk text
            lines = [meta_prefix]

            course = (review.get("course") or "").strip()
            if course:
                lines.append(f"Course: {course}")

            date = (review.get("date") or "").strip()
            if date:
                lines.append(f"Date: {date}")

            q    = review.get("quality")
            diff = review.get("difficulty")
            if q is not None and diff is not None:
                lines.append(f"Quality: {q}/5 | Difficulty: {diff}/5")

            lines.append(f"Review: {comment}")

            tags = [t for t in (review.get("tags") or []) if t]
            if tags:
                lines.append(f"Tags: {', '.join(tags)}")

            chunk_text = "\n".join(lines)

            chunks.append({
                "text":              chunk_text,
                "professor_name":    prof_name,
                "department":        department,
                "overall_rating":    overall,
                "difficulty":        difficulty,
                "review_quality":    q,
                "review_difficulty": diff,
                "date":              date,
                "course":            course,
                "tags":              tags,
                "source_file":       source_file,
            })

    print(f"Produced {len(chunks)} chunks.")
    print(f"Skipped {skipped_empty} empty comments, {skipped_short} too-short comments.")
    return chunks


# ── Validation helpers ────────────────────────────────────────────────────────

def validate_chunks(chunks: list[dict]) -> None:
    """
    Milestone 3 checkpoint validation.
    Flags common problems: empty text, missing metadata, HTML leftovers, size issues.
    """
    issues = []

    for i, chunk in enumerate(chunks):
        text = chunk.get("text", "")

        if not text.strip():
            issues.append(f"Chunk {i}: empty text")
            continue

        if not chunk.get("professor_name"):
            issues.append(f"Chunk {i}: missing professor_name")

        if not chunk.get("source_file"):
            issues.append(f"Chunk {i}: missing source_file")

        if "<" in text and ">" in text:
            issues.append(f"Chunk {i}: possible HTML artifact — {text[:80]}")

        if "&amp;" in text or "&quot;" in text or "&#" in text:
            issues.append(f"Chunk {i}: unescaped HTML entity — {text[:80]}")

    if issues:
        print(f"\n⚠️  {len(issues)} validation issue(s) found:")
        for issue in issues[:10]:  # show first 10
            print(f"   {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more.")
    else:
        print("✅  All chunks passed validation.")

    # Size check
    if len(chunks) < 50:
        print(f"⚠️  Only {len(chunks)} chunks — chunks may be too large, "
              "or too many reviews were filtered out.")
    elif len(chunks) > 2000:
        print(f"⚠️  {len(chunks)} chunks — chunks may be too small, "
              "embeddings may not carry enough meaning.")
    else:
        print(f"✅  Chunk count ({len(chunks)}) is in the healthy range (50–2000).")


def print_sample_chunks(chunks: list[dict], n: int = 5) -> None:
    """Print n random chunks for manual inspection."""
    sample = random.sample(chunks, min(n, len(chunks)))
    print(f"\n{'='*60}")
    print(f"SAMPLE CHUNKS ({n} random)")
    print(f"{'='*60}")
    for i, chunk in enumerate(sample, 1):
        print(f"\n--- Chunk {i} (source: {chunk['source_file']}) ---")
        print(chunk["text"])
    print(f"\n{'='*60}")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_pipeline() -> list[dict]:
    """Run the full ingestion + chunking pipeline and return chunks."""
    print("=== Milestone 3: Ingestion and Chunking ===\n")

    # Stage 1: Load
    documents = load_documents()

    # Stage 2 + 3: Chunk (cleaning happens inside chunk_documents per review)
    chunks = chunk_documents(documents)

    # Validate
    print()
    validate_chunks(chunks)

    # Inspect
    print_sample_chunks(chunks)

    # Summary by department
    cs_chunks   = [c for c in chunks if "computer science" in c["department"].lower()]
    math_chunks = [c for c in chunks if "mathematics" in c["department"].lower()]
    print(f"\nChunks by department:")
    print(f"  Computer Science : {len(cs_chunks)}")
    print(f"  Mathematics      : {len(math_chunks)}")
    print(f"  Other            : {len(chunks) - len(cs_chunks) - len(math_chunks)}")

    return chunks


if __name__ == "__main__":
    chunks = run_pipeline()