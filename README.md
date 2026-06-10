# The Unofficial Guide — Project 1

---

## Domain

This system covers student reviews of CS and Mathematics professors at Berea College.
This knowledge is valuable because official channels — course catalogs, department websites,
and advising pages — describe what a course covers but say nothing about teaching style,
grading difficulty, how helpful a professor is outside class, or whether students would
take them again. A student choosing between two professors for the same required course has
no official resource to consult. Rate My Professors fills that gap, but its interface only
lets you look up one professor at a time and does not support comparative queries like "who
is the easiest math professor?" or "which CS professor gives the most useful feedback?" This
system makes the collective knowledge of 237 student reviews queryable in plain language.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Jan Pearce — RMP reviews | JSON (45 reviews) | data/raw/Jan_Pearce.json |
| 2 | Larry Gratton — RMP reviews | JSON (26 reviews) | data/raw/Larry_Gratton.json |
| 3 | Mario Nakazawa — RMP reviews | JSON (19 reviews) | data/raw/Mario_Nakazawa.json |
| 4 | Kristen Barnard — RMP reviews | JSON (17 reviews) | data/raw/Kristen_Barnard.json |
| 5 | Elizabeth Kelly — RMP reviews | JSON (13 reviews) | data/raw/Elizabeth_Kelly.json |
| 6 | James Blackburn-Lynch — RMP reviews | JSON (12 reviews) | data/raw/James_Blackburn-Lynch.json |
| 7 | Lisa Jones — RMP reviews | JSON (12 reviews) | data/raw/Lisa_Jones.json |
| 8 | J.P. Lee — RMP reviews | JSON (12 reviews) | data/raw/J.P._Lee.json |
| 9 | Clinton Hines — RMP reviews | JSON (11 reviews) | data/raw/Clinton_Hines.json |
| 10 | Judy Rector — RMP reviews | JSON (11 reviews) | data/raw/Judy_Rector.json |
| 11 | Sara Ellis — RMP reviews | JSON (11 reviews) | data/raw/Sara_Ellis.json |
| 12 | Scott Heggen — RMP reviews | JSON (11 reviews) | data/raw/Scott_Heggen.json |
| 13 | Richard Maiti — RMP reviews | JSON (10 reviews) | data/raw/Richard_Maiti.json |
| 14 | Terri Thesing — RMP reviews | JSON (7 reviews) | data/raw/Terri_Thesing.json |
| 15 | Kenny Siler — RMP reviews | JSON (6 reviews) | data/raw/Kenny_Siler.json |
| 16 | Judy Veranas — RMP reviews | JSON (5 reviews) | data/raw/Judy_Veranas.json |
| 17 | Matt Jadud — RMP reviews | JSON (5 reviews) | data/raw/Matt_Jadud.json |
| 18 | Jasmine Jones — RMP reviews | JSON (5 reviews) | data/raw/Jasmine_Jones.json |

All documents were collected from Rate My Professors (https://www.ratemyprofessors.com/school/104)
using the `ratemyprofessors-client` Python library. Only professors with 5 or more reviews
are included. Reviews span 2003–2026 across 7 CS and 11 Math professors.

---

## Chunking Strategy

**Chunk size:** One chunk per individual student review. Review text averages 150–400
characters; with the metadata prefix the total chunk size averages 300–600 characters.
No fixed character limit is applied — each review is kept intact.

**Overlap:** None. Reviews are self-contained opinion units with no cross-boundary
dependencies. Unlike long prose documents where a sentence at the end of one chunk may
depend on context from the previous one, each review is independently readable from start
to finish.

**Why these choices fit your documents:** The source documents are collections of short,
independent opinions — one student's experience with one professor. Splitting mid-review
would destroy the unit of meaning (a review saying "exams are fair but homework is heavy"
would become two fragments, neither of which is retrievable for either query). Grouping
multiple reviews into one chunk would dilute specificity: a chunk containing five reviews
could match queries about any topic mentioned in any of them. One chunk per review keeps
each embedding focused on a single perspective.

Each chunk is prefixed with structured metadata so the professor's identity, department,
and rating are present in every chunk regardless of which review is retrieved:

```
Professor: <name> | Dept: <department> | Overall Rating: <X>/5 | Difficulty: <X>/5
Date: <date>
Quality: <X>/5 | Difficulty: <X>/5
Review: <comment text>
Tags: <tag1>, <tag2>
```

**Preprocessing:** HTML entities (`&quot;`, `&amp;`, `&#39;`) were decoded using
Python's `html.unescape()`. Residual HTML tags were stripped with a regex. Reviews
shorter than 10 characters were discarded (2 reviews dropped — blank or punctuation-only).

**Final chunk count:** 237 chunks (99 CS, 138 Math).

---

## Sample Chunks

**Chunk 1** (source: `Jan_Pearce.json`)
```
Professor: Jan Pearce | Dept: Computer Science | Overall Rating: 2.2/5 | Difficulty: 3.3/5
Date: 2015-10-29
Quality: 4.0/5 | Difficulty: 5.0/5
Review: Jan is probably the toughest grader at Berea. She takes off a lot of points on her
tests if you fail to answer it EXACTLY the way she wants. She gives out very long,
unnecessary coding homework to illustrate simple concepts. Avoid if possible.
```

**Chunk 2** (source: `Richard_Maiti.json`)
```
Professor: Richard Maiti | Dept: Computer Science | Overall Rating: 4.6/5 | Difficulty: 3.1/5
Date: 2018-12-07
Quality: 5.0/5 | Difficulty: 4.0/5
Review: Wonderful professor! I would say he is the best professor in the whole department!
He truly cares for you and knows what he is talking about! Really smart person, very
knowledgeable and most importantly he knows the field he is teaching!!! He brings a lot
of inspiration in his classes!
Tags: Respected, ACCESSIBLE OUTSIDE CLASS, Amazing lectures
```

**Chunk 3** (source: `Sara_Ellis.json`)
```
Professor: Sara Ellis | Dept: Mathematics | Overall Rating: 4.9/5 | Difficulty: 2.5/5
Date: 2022-12-06
Quality: 5.0/5 | Difficulty: 3.0/5
Review: Sara Ellis is hands down the best math instructor I have ever had. She is incredibly
caring and shows dedication to every student. She is quick to get you through whatever
challenge you have (math related or not). Incredibly high energy and easy to reciprocate.
She has all of my respect as a person and instructor. Highly recommend!
Tags: Clear grading criteria, Caring, Accessible outside class
```

**Chunk 4** (source: `Scott_Heggen.json`)
```
Professor: Scott Heggen | Dept: Computer Science | Overall Rating: 3.2/5 | Difficulty: 2.6/5
Date: 2025-04-16
Quality: 4.0/5 | Difficulty: 2.0/5
Review: He doesn't get in the way of your learning. Homework makes sense. Can't go wrong
with him. In CSC226, you learn a lot without expending an unreasonable amount of effort.
Tags: Accessible outside class
```

**Chunk 5** (source: `Clinton_Hines.json`)
```
Professor: Clinton Hines | Dept: Mathematics | Overall Rating: 3.5/5 | Difficulty: 2.4/5
Date: 2025-08-14
Quality: 5.0/5 | Difficulty: 2.0/5
Review: Dr. Hines is my favorite professor! His lectures are hilarious, he goes around to
help students during class, and goes over most of the answers to homework assignments in
class. His quizzes are not hard. Great class!
Tags: Clear grading criteria
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. Runs locally with no API
key, no rate limits, and no cost per query. Produces 384-dimension vectors. 512-token
context window comfortably fits any individual RMP review.

**Production tradeoff reflection:** For a production deployment I would weigh the following:

- **Accuracy:** `all-MiniLM-L6-v2` was not fine-tuned on academic review text. A model like
  OpenAI's `text-embedding-3-small` or Cohere's `embed-english-v3.0` would likely score
  higher on domain-specific similarity queries like "which professor curves exams."
- **Multilingual support:** Berea enrolls international students and several reviews use
  non-standard English phrasing. A multilingual model like
  `paraphrase-multilingual-MiniLM-L12-v2` would handle this better.
- **Context length:** MiniLM's 512-token limit is fine for individual reviews but would
  truncate longer documents if the domain expanded to syllabi or handbooks.
- **Latency and cost:** Local models have zero per-query cost and no network round-trip,
  which matters at scale. API-based models add latency and per-token cost.
- **Privacy:** For a student-facing tool at a small college, local inference avoids sending
  student query data to a third-party API.

---

## Retrieval Test Results

**Embedding model:** `all-MiniLM-L6-v2` | **Top-k:** 5 | **Distance:** Cosine (lower = more similar)

**Query 1:** "Which CS professor gives the most useful feedback?"

| Rank | Distance | Result |
|------|----------|--------|
| 1 | 0.3415 | Jan Pearce (CS) — 2014-01-20 |
| 2 | 0.3424 | Scott Heggen (CS) — 2016-04-12 |
| 3 | 0.3524 | Jan Pearce (CS) — 2024-05-09 |
| 4 | 0.3681 | Mario Nakazawa (CS) — 2013-11-05 |
| 5 | 0.3750 | Richard Maiti (CS) — 2018-12-07 |

*Relevance:* Partially relevant. All five results are CS professors (correct department
filtering), but results 1 and 3 are negative Jan Pearce reviews that mention "feedback"
as a complaint ("feedback is nonexistent") rather than praise. The embedding model matched
on topic without distinguishing sentiment direction.

**Query 2:** "Who is the easiest math professor at Berea?"

| Rank | Distance | Result |
|------|----------|--------|
| 1 | 0.3314 | Larry Gratton (Math) — 2021-01-14 |
| 2 | 0.3487 | Larry Gratton (Math) — 2018-01-28 |
| 3 | 0.3700 | James Blackburn-Lynch (Math) — 2009-04-29 |
| 4 | 0.3710 | J.P. Lee (Math) — 2014-04-28 |
| 5 | 0.3866 | Kristen Barnard (Math) — 2026-04-24 |

*Relevance:* Relevant. All five results are Math professors. Larry Gratton appearing twice
at the top is appropriate — he has the most reviews and the highest volume of comments
about course difficulty and ease. All retrieved chunks discuss workload or difficulty,
which directly addresses the query.

**Query 3:** "What do students say about Jan Pearce's grading?"

| Rank | Distance | Result |
|------|----------|--------|
| 1 | 0.3356 | Jan Pearce (CS) — 2015-03-16 |
| 2 | 0.3568 | Jan Pearce (CS) — 2022-02-08 |
| 3 | 0.3572 | Jan Pearce (CS) — 2006-03-21 |
| 4 | 0.3705 | Jan Pearce (CS) — 2026-04-05 |
| 5 | 0.3810 | Jan Pearce (CS) — 2013-12-17 |

*Relevance:* Relevant. All five results are Jan Pearce reviews — a perfect named-professor
retrieval. The embedding model correctly identified the proper noun and returned only her
reviews spanning 2006–2026, giving the LLM a range of perspectives to synthesize.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a helpful assistant for Berea College students looking up information about CS and
Math professors based on Rate My Professors reviews.

STRICT RULES:
1. Answer ONLY using the review excerpts provided below. Do not use any outside knowledge.
2. If the provided reviews do not contain enough information to answer the question,
   say exactly: "I don't have enough information in the available reviews to answer that."
3. Never speculate or infer beyond what is explicitly stated in the reviews.
4. Always mention which professor(s) the information comes from in your answer.
5. Keep your answer concise and focused on what the reviews actually say.
6. When citing a review, refer to it as "a student review of [Professor Name]",
   not as "Review 1" or "Review 4".
```

Temperature is set to 0.2 to reduce the model's tendency to elaborate beyond the provided
context. The retrieved chunks are passed verbatim as numbered context blocks in the user
message, each labelled with professor name and date so the model can reference them
accurately.

**How source attribution is surfaced in the response:** Source attribution is handled
programmatically after generation — the pipeline appends the retrieved chunk metadata
(professor name, department, review date, cosine distance score) to the response as a
separate sources list. Attribution is never left to the LLM to produce on its own, which
means it cannot be accidentally omitted from a response.

---

## Example Responses

**Example 1 — Grounded response with source attribution**

*Query:* "Who is the best CS professor in Berea?"

*Answer:*
> According to student reviews of Scott Heggen, he is considered one of the best professors,
> with a student stating he is "one of the best professors currently employed at Berea" and
> another saying "He is just amazing. He is the reason I am pursuing CS." Richard Maiti is
> also frequently described as the best in the department, with students calling him
> "wonderful" and noting he "truly cares for you and knows what he is talking about."
> The reviews do not provide a definitive ranking, but Maiti receives the most consistently
> positive feedback across multiple years.

*Sources:*
- Scott Heggen (Computer Science) — 2018-04-11 [dist: 0.34]
- Richard Maiti (Computer Science) — 2018-12-07 [dist: 0.36]
- Scott Heggen (Computer Science) — 2016-04-12 [dist: 0.37]

---

**Example 2 — Grounded response with source attribution**

*Query:* "What do students say about Jan Pearce's grading?"

*Answer:*
> According to student reviews of Jan Pearce, common complaints include: she knows nothing
> about CS, the material taught is useless, her classes are a joke, she is biased, and she
> gives a lot of homework. Additionally, students have mentioned that she is a tough grader,
> her classes are test heavy, and that she doesn't answer questions or emails. These
> complaints come from multiple reviews of Jan Pearce.

*Sources:*
- Jan Pearce (Computer Science) — 2015-03-16 [dist: 0.34]
- Jan Pearce (Computer Science) — 2022-02-08 [dist: 0.36]
- Jan Pearce (Computer Science) — 2006-03-21 [dist: 0.36]
- Jan Pearce (Computer Science) — 2026-04-05 [dist: 0.37]
- Jan Pearce (Computer Science) — 2013-12-17 [dist: 0.38]

---

**Example 3 — Out-of-scope query showing refusal**

*Query:* "Does Berea College have a swimming pool?"

*Answer:*
> I don't have enough information in the available reviews to answer that.

*Sources:* (none)

---

## Query Interface

The interface is a Gradio web UI launched with `python app.py`, accessible at
`http://localhost:7860`.

**Input fields:**
- **Your question** — plain-language text box. Accepts any natural language query about
  Berea College CS or Math professors. Submits on Enter or by clicking the Ask button.

**Output fields:**
- **Answer** — the LLM's grounded response, synthesized from the top 5 retrieved reviews.
  References specific professors and is constrained to information in the reviews.
- **Retrieved from (sources)** — list of the specific reviews used to generate the answer,
  each showing professor name, department, review date, and cosine distance score.

**Sample interaction transcript:**

```
User: Who is the easiest math professor at Berea?

Answer:
Based on student reviews, Kenny Siler and Sara Ellis are frequently described as the
easiest and most approachable Math professors. Siler gives practice exams before each
test with only different numbers, allows late submissions, and students describe his
class as "an easy A." Sara Ellis is described as making math "easy and fun" and is
especially recommended for students taking remedial math. Larry Gratton is also
mentioned as easy — students note he uses free textbooks and has no real late-work
penalty — though some reviews describe his pace as too slow for students with prior
math experience.

Retrieved from:
• Kenny Siler (Mathematics) — 2025-11-11 [dist: 0.33]
• Sara Ellis (Mathematics) — 2021-11-08 [dist: 0.35]
• Larry Gratton (Mathematics) — 2023-11-08 [dist: 0.36]
• Kenny Siler (Mathematics) — 2024-10-28 [dist: 0.37]
• Larry Gratton (Mathematics) — 2018-01-28 [dist: 0.38]
```

---

## Evaluation Report

| # | Question | Expected answer | System response | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Is Lisa Jones recommended for Math students at Berea College? | No. Reviews describe belittling, humiliating behavior, assigning untaught homework. Rating 1.5/5, 8.3% would take again. | Based on the reviews, it seems that opinions about Lisa Jones are mixed. A student review of Lisa Jones from 2020-09-08 highly recommends her, describing her as "caring, funny, cheerful, and knows her stuff." However, more recent reviews from 2024-12-13, 2025-10-16, and 2026-04-07 express negative experiences, citing unrealistic expectations, belittling behavior, and a condescending attitude. Given these conflicting views, it's difficult to make a definitive recommendation. However, the majority of the recent reviews advise against taking her class. | Relevant | Partially accurate |
| 2 | What do students say about Kenny Siler's grading style? | Lenient and supportive. Practice exams, late submission allowed, exam corrections permitted. 100% would take again. | According to a student review of Kenny Siler, he "is not a harsh grader and will try to ensure you pass every test he grades." Another student review of Kenny Siler mentions that "After an exam he allows you to learn and correct it to have a better grade." Additionally, a student review of Kenny Siler states that "He gives study exam before each one and it's the same the numbers are just different," which suggests that his grading style is transparent and preparatory. These comments come from student reviews of Kenny Siler, indicating that students perceive his grading style as fair and supportive. | Relevant | Accurate |
| 3 | What are common complaints about Jan Pearce's CS classes? | Writing-heavy rather than coding-focused, very tough grader, unhelpful at office hours. Rating 2.2/5. | According to student reviews of Jan Pearce, common complaints about her CS classes include: she knows nothing about CS, the material taught is useless, her classes are a joke, she is biased, and she gives a lot of homework. Additionally, students have mentioned that she is a tough grader, her classes are test heavy, and that she doesn't answer questions or emails. These complaints come from multiple reviews of Jan Pearce. | Partially relevant | Partially accurate |
| 4 | Which Math professor at Berea College do students most recommend? | Sara Ellis and Terri Thesing, both 4.9/5, 100% would take again. | According to the reviews, both Larry Gratton and Clinton Hines are highly recommended by students. A student review of Larry Gratton states "Take him and you won't regret" and a student review of Clinton Hines says "Definitely recommend if you're not a math major." Additionally, a student review of James Blackburn-Lynch also highly praises him, stating "He's simply the best." Therefore, it seems that students recommend Larry Gratton, Clinton Hines, and James Blackburn-Lynch. | Off-target | Inaccurate |
| 5 | What do students say about Larry Gratton's classroom organization? | Mixed. Does not use a calendar; students never know test/homework dates. Uses free textbooks, no late penalty. | A student review of Larry Gratton mentions that he "DOES NOT USE A CALENDAR" and that as a result, students have "no idea what topics you'll go over, homework you'll have, and when you are going to have assessments on any given day." This suggests that some students find his classroom organization to be lacking in terms of planning and communication of the course schedule. | Relevant | Partially accurate |

---

## Failure Case Analysis

**Question that failed:** "Which Math professor at Berea College do students most recommend?"

**What the system returned:** Larry Gratton, Clinton Hines, and James Blackburn-Lynch —
none of whom have the highest ratings. Sara Ellis (4.9/5, 100% would take again) and Terri
Thesing (4.9/5, 100% would take again) were not retrieved.

**Root cause (tied to a specific pipeline stage):** This is a retrieval failure caused by
frequency bias in the embedding stage. Larry Gratton has 26 reviews — the most of any Math
professor — and many contain recommendation-sounding phrases like "Take him and you won't
regret." Clinton Hines (11 reviews) and James Blackburn-Lynch (12 reviews) similarly have
more reviews containing positive language than Sara Ellis (11 reviews) or Terri Thesing
(7 reviews). The embedding model matched the query "most recommend" against the volume of
recommendation-sounding text, so professors with more reviews dominated the top-k results
regardless of their actual aggregate rating.

Sara Ellis and Terri Thesing have the highest overall ratings and 100% would-take-again
scores, but their reviews were not retrieved because the embedding similarity search has no
awareness of aggregate rating metadata — it only sees the text of individual reviews. A
glowing review of a 3.3-rated professor looks the same to the embedder as a glowing review
of a 4.9-rated professor.

**What you would change to fix it:** Include aggregate rating metadata in the retrieval
ranking — for example, re-rank retrieved chunks by multiplying semantic similarity score by
the professor's `overall_rating` before selecting top-k. Alternatively, a hybrid approach
could retrieve candidates by semantic similarity and then sort by `overall_rating`
descending before passing context to the LLM. This failure shows that semantic retrieval
alone is insufficient for comparative "best" or "most recommended" queries when the correct
answer depends on aggregate statistics rather than individual review text.

---

## Spec Reflection

**One way the spec helped you during implementation:** The requirement to write `planning.md`
before any code forced me to think through the chunking strategy before seeing the actual
data. When I later read the reviews and saw that each one was a short, self-contained
opinion, the "one chunk per review" decision was already made and justified. Without the
spec, I would likely have started coding immediately and defaulted to a fixed
character-count splitter that would have cut reviews mid-sentence — destroying the unit of
meaning that makes each review independently retrievable.

**One way your implementation diverged from the spec, and why:** The spec recommended
collecting at least 10 documents from diverse sources. My implementation uses only Rate My
Professors — all 18 documents come from the same platform. This divergence happened because
Berea is a small college and other sources (Reddit, the student newspaper The Pinnacle) had
very little coverage of specific CS and Math professors by name. The trade-off is reduced
source diversity but higher consistency: all documents share the same schema, which made
chunking deterministic and reduced cleaning overhead significantly.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* My Documents section from `planning.md` (18 local JSON files with
  a known schema), my Chunking Strategy section (one chunk per review, metadata prefix, no
  overlap), and one sample JSON file (`Jan_Pearce.json`) to show the exact field names.
- *What it produced:* `load_documents()` and `chunk_documents()` functions in `pipeline.py`.
- *What I changed or overrode:* I added the `MIN_COMMENT_LEN = 10` filter after noticing
  that two reviews in the data were blank or contained only punctuation (e.g., `" ,"`) —
  Claude had not accounted for these because they were not visible in the sample I provided.
  I also changed the chunk text format to include per-review `Quality` and `Difficulty`
  fields, which Claude had omitted from the first version because I had not specified them
  explicitly in my input.

**Instance 2**

- *What I gave the AI:* The grounding requirement from the project spec (answers from
  retrieved context only, source attribution required), the output format of `retrieve()`,
  the Groq model name (`llama-3.3-70b-versatile`), and the Gradio skeleton from the
  Milestone 5 instructions.
- *What it produced:* A working `ask()` function and Gradio UI in `app.py`.
- *What I changed or overrode:* Claude's original system prompt said "try to answer only
  from the provided context" — the word "try" makes grounding a suggestion rather than a
  rule. I changed it to "Answer ONLY using the review excerpts provided below. Do not use
  any outside knowledge." I also added the explicit refusal phrase after testing showed the
  model would generate plausible-sounding answers for out-of-scope questions when no
  explicit refusal instruction was given.

---

## Setup

```bash
git clone https://github.com/Mercy-Eze/ai201-project1-unofficial-guide-starter
cd ai201-project1-unofficial-guide-starter
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
source .venv/Scripts/activate    # Windows (Git Bash)

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your GROQ_API_KEY from console.groq.com

python app.py
# Open http://localhost:7860
```