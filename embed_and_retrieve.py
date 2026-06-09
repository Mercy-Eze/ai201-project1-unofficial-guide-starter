"""
embed_and_retrieve.py
---------------------
Milestone 4: Embed chunks and store in ChromaDB, then retrieve by query.

Stages:
  1. embed_and_store()  — embeds all chunks and upserts into ChromaDB
  2. retrieve()         — semantic search, returns top-k chunks with metadata

Usage:
    python embed_and_retrieve.py

Requires:
    pip install sentence-transformers chromadb
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer
from pipeline import run_pipeline

# ── Config ────────────────────────────────────────────────────────────────────

CHROMA_DIR      = "data/chroma"       # where ChromaDB persists to disk
COLLECTION_NAME = "berea_rmp"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K           = 5


# ── Stage 1: Embed and Store ──────────────────────────────────────────────────

def embed_and_store(chunks: list[dict], force_rebuild: bool = False) -> chromadb.Collection:
    """
    Embed all chunks with all-MiniLM-L6-v2 and upsert into a local ChromaDB collection.

    Each chunk is stored with:
        - document : the full chunk text (what gets embedded and returned)
        - id       : unique string per chunk
        - metadata : professor_name, department, overall_rating, difficulty,
                     date, course, source_file

    Set force_rebuild=True to wipe and re-embed from scratch.
    Otherwise, if the collection already exists with the right count, it is reused.
    """
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Optionally wipe existing collection
    if force_rebuild:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection '{COLLECTION_NAME}'.")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},   # cosine similarity
    )

    # If already populated and not forcing rebuild, reuse
    existing_count = collection.count()
    if existing_count == len(chunks) and not force_rebuild:
        print(f"Collection '{COLLECTION_NAME}' already contains {existing_count} chunks. "
              "Skipping re-embedding. Pass force_rebuild=True to re-embed.")
        return collection

    print(f"Loading embedding model '{EMBEDDING_MODEL}'...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    texts      = [c["text"] for c in chunks]
    ids        = [f"chunk_{i:04d}" for i in range(len(chunks))]
    metadatas  = [
        {
            "professor_name":    c["professor_name"],
            "department":        c["department"],
            "overall_rating":    float(c["overall_rating"] or 0),
            "difficulty":        float(c["difficulty"] or 0),
            "review_quality":    float(c["review_quality"] or 0),
            "review_difficulty": float(c["review_difficulty"] or 0),
            "date":              c["date"] or "",
            "course":            c["course"] or "",
            "source_file":       c["source_file"],
            "tags":              ", ".join(c["tags"]),
        }
        for c in chunks
    ]

    # Embed in batches to avoid memory spikes
    print(f"Embedding {len(texts)} chunks (batch size 64)...")
    BATCH = 64
    all_embeddings = []
    for start in range(0, len(texts), BATCH):
        batch = texts[start : start + BATCH]
        embeddings = model.encode(batch, show_progress_bar=False).tolist()
        all_embeddings.extend(embeddings)
        print(f"  Embedded {min(start + BATCH, len(texts))} / {len(texts)}")

    # Upsert everything at once
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=all_embeddings,
        metadatas=metadatas,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB at '{CHROMA_DIR}'.")
    return collection


# ── Stage 2: Retrieve ─────────────────────────────────────────────────────────

def retrieve(
    query: str,
    collection: chromadb.Collection,
    model: SentenceTransformer,
    top_k: int = TOP_K,
    department_filter: str | None = None,
) -> list[dict]:
    """
    Embed the query and return the top_k most similar chunks.

    Args:
        query             : plain-language question from the user
        collection        : ChromaDB collection to search
        model             : the same SentenceTransformer used for indexing
        top_k             : number of results to return
        department_filter : optional — "Computer Science" or "Mathematics"

    Returns a list of dicts:
        {
            "text":           str,    # full chunk text
            "distance":       float,  # cosine distance (lower = more similar)
            "professor_name": str,
            "department":     str,
            "overall_rating": float,
            "date":           str,
            "source_file":    str,
        }
    """
    query_embedding = model.encode(query).tolist()

    where_filter = None
    if department_filter:
        where_filter = {"department": {"$eq": department_filter}}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append({
            "text":              text,
            "distance":          round(dist, 4),
            "professor_name":    meta["professor_name"],
            "department":        meta["department"],
            "overall_rating":    meta["overall_rating"],
            "date":              meta["date"],
            "source_file":       meta["source_file"],
            "course":            meta.get("course", ""),
            "tags":              meta.get("tags", ""),
        })

    return retrieved


# ── Test retrieval ────────────────────────────────────────────────────────────

def test_retrieval(collection: chromadb.Collection, model: SentenceTransformer) -> None:
    """
    Run the first 3 evaluation plan questions and print results.
    Milestone 4 checkpoint: top results should score below 0.5 and be on-topic.
    """
    test_queries = [
        "Which CS professor gives the most useful feedback?",
        "Who is the easiest math professor at Berea?",
        "What do students say about Jan Pearce's grading?",
    ]

    print("\n" + "=" * 60)
    print("RETRIEVAL TEST — 3 Evaluation Queries")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        print("-" * 50)
        results = retrieve(query, collection, model)
        for i, r in enumerate(results, 1):
            dist_flag = "✅" if r["distance"] < 0.5 else "⚠️ "
            print(f"  {i}. {dist_flag} [{r['distance']}] "
                  f"{r['professor_name']} ({r['department']}) — {r['date']}")
            # Print first 120 chars of review text
            preview = r["text"].split("Review:")[-1].strip()[:120]
            print(f"     \"{preview}...\"")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=== Milestone 4: Embedding and Retrieval ===\n")

    # Step 1: Run ingestion pipeline to get chunks
    chunks = run_pipeline()
    print()

    # Step 2: Embed and store
    collection = embed_and_store(chunks)

    # Step 3: Load model for retrieval (reuse the same one)
    print(f"\nLoading '{EMBEDDING_MODEL}' for retrieval...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Step 4: Verify collection count matches chunk count
    stored = collection.count()
    print(f"ChromaDB collection count: {stored}")
    if stored == len(chunks):
        print("✅  Collection count matches chunk count.")
    else:
        print(f"⚠️  Mismatch — {len(chunks)} chunks produced but {stored} stored.")

    # Step 5: Test retrieval on evaluation queries
    test_retrieval(collection, model)

    print("\n✅  Milestone 4 complete. Ready for Milestone 5 (generation).")
    return collection, model


if __name__ == "__main__":
    main()