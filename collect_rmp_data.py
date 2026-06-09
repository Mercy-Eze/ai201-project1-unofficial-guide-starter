"""
collect_rmp_data.py
-------------------
Fetches all CS and Math professor reviews from Rate My Professors
for Berea College using the school ID directly (no name search needed).

Usage:
    pip install ratemyprofessors-client
    python collect_rmp_data.py

Output:
    data/raw/<ProfessorName>.json  — one file per professor
    data/raw/all_reviews.json      — all professors combined
"""

import json
import os

try:
    from rmp_client import RMPClient
except ImportError:
    raise SystemExit("Run: pip install ratemyprofessors-client")

# ── Config ────────────────────────────────────────────────────────────────────

BEREA_SCHOOL_ID = "104"  # from https://www.ratemyprofessors.com/school/104

# Only keep professors in these departments (case-insensitive substring match).
# Leave empty to collect ALL professors at Berea.
TARGET_DEPARTMENTS = ["computer science", "mathematics"]

OUTPUT_DIR = "data/raw"

# ── Helpers ───────────────────────────────────────────────────────────────────

def rating_to_dict(r):
    return {
        "comment":          r.comment or "",
        "quality":          r.quality,
        "difficulty":       r.difficulty,
        "course":           getattr(r, "class_name", None) or "",
        "grade":            getattr(r, "grade", None) or "",
        "date":             str(r.date) if r.date else "",
        "tags":             list(getattr(r, "tags", []) or []),
        "would_take_again": getattr(r, "would_take_again", None),
        "attendance":       getattr(r, "attendance_mandatory", None),
        "thumbs_up":        getattr(r, "thumbs_up", None),
        "thumbs_down":      getattr(r, "thumbs_down", None),
    }

def build_plain_text(doc):
    """Readable text blob — this is what your chunker will split."""
    lines = [
        f"Professor: {doc['professor_name']}",
        f"Department: {doc['department']}",
        f"School: {doc['school']}",
        f"Overall Rating: {doc['overall_rating']} / 5",
        f"Difficulty: {doc['difficulty']} / 5",
        f"Would Take Again: {doc['would_take_again_pct']}%",
        f"Number of Ratings: {doc['num_ratings']}",
        "",
        "--- Student Reviews ---",
        "",
    ]
    for i, r in enumerate(doc["reviews"], 1):
        if not r["comment"].strip():
            continue
        lines.append(f"Review {i}:")
        if r["course"]:
            lines.append(f"  Course: {r['course']}")
        lines.append(f"  Quality: {r['quality']} | Difficulty: {r['difficulty']}")
        if r["date"]:
            lines.append(f"  Date: {r['date']}")
        lines.append(f"  Comment: {r['comment']}")
        if r["tags"]:
            lines.append(f"  Tags: {', '.join(r['tags'])}")
        lines.append("")
    return "\n".join(lines)

def in_target_dept(department: str) -> bool:
    if not TARGET_DEPARTMENTS:
        return True
    dept_lower = (department or "").lower()
    return any(t in dept_lower for t in TARGET_DEPARTMENTS)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_documents = []

    with RMPClient() as client:

        # 1. Confirm the school exists
        school = client.get_school(BEREA_SCHOOL_ID)
        print(f"School: {school.name}, {school.location}\n")

        # 2. Iterate every professor at Berea
        print("Scanning all professors at Berea College...")
        all_profs = list(client.iter_professors_for_school(int(BEREA_SCHOOL_ID), page_size=50))
        print(f"Found {len(all_profs)} total professors on RMP.\n")

        # 3. Filter to CS and Math
        target_profs = [p for p in all_profs if in_target_dept(p.department)]
        print(f"Professors in target departments ({', '.join(TARGET_DEPARTMENTS)}): {len(target_profs)}\n")

        # 4. Fetch reviews for each
        for prof in target_profs:
            print(f"  Fetching: {prof.name} ({prof.department}) — {prof.num_ratings} ratings ...", end=" ", flush=True)

            if prof.num_ratings == 0:
                print("skipped (no ratings)")
                continue

            ratings = [
                rating_to_dict(r)
                for r in client.iter_professor_ratings(prof.id)
            ]
            non_empty = [r for r in ratings if r["comment"].strip()]
            print(f"{len(ratings)} ratings, {len(non_empty)} with comments")

            doc = {
                "professor_name":    prof.name,
                "department":        prof.department,
                "school":            school.name,
                "overall_rating":    prof.overall_rating,
                "difficulty":        getattr(prof, "level_of_difficulty", None),
                "would_take_again_pct": getattr(prof, "percent_take_again", None),
                "num_ratings":       prof.num_ratings,
                "reviews":           ratings,
            }
            doc["plain_text"] = build_plain_text(doc)

            safe_name = prof.name.replace(" ", "_").replace("/", "-")
            filepath = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)

            all_documents.append(doc)

    # 5. Save combined file
    combined_path = os.path.join(OUTPUT_DIR, "all_reviews.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(all_documents, f, indent=2, ensure_ascii=False)

    # 6. Summary
    print("\n" + "=" * 50)
    print(f"Saved {len(all_documents)} professor document(s) to {OUTPUT_DIR}/")
    if len(all_documents) < 10:
        shortfall = 10 - len(all_documents)
        print(f"\n⚠️  Only {len(all_documents)} docs — need {shortfall} more for the 10-document minimum.")
        print("   Supplement with Reddit threads, the student newspaper (The Pinnacle),")
        print("   or department pages from the Berea College website.")
    print("=" * 50)


if __name__ == "__main__":
    main()