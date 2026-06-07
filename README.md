# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers **CS internship and career advice for undergraduate students**, grounded in the kind of candid, experience-based guidance that circulates on forums like Reddit (r/cscareerquestions, r/csMajors) but is absent from official university career center resources.

The knowledge is valuable because it captures unwritten rules of the recruiting process that institutions either don't know or won't say directly: the fact that most FAANG applications close by December while students are still thinking about summer in February; that a 3.1 GPA can bypass ATS filters entirely through an internal referral; that intern offer negotiation is expected by recruiters and carries essentially no downside risk. Students routinely learn these lessons too late — after sitting out a summer, accepting below-market pay, or grinding 400 LeetCode problems the wrong way. Official career center guidance is sanitized and slow to reflect the actual market. Forum-sourced advice, written by students and engineers who lived through the process recently, is not.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | getting_first_internship.txt | Forum Q&A (r/cscareerquestions style) | documents/getting_first_internship.txt |
| 2 | leetcode_preparation.txt | Forum Q&A (r/cscareerquestions style) | documents/leetcode_preparation.txt |
| 3 | gpa_importance.txt | Forum Q&A (r/cscareerquestions style) | documents/gpa_importance.txt |
| 4 | resume_and_projects.txt | Forum Q&A (r/cscareerquestions style) | documents/resume_and_projects.txt |
| 5 | behavioral_interviews.txt | Forum Q&A (r/cscareerquestions style) | documents/behavioral_interviews.txt |
| 6 | online_assessments.txt | Forum Q&A (r/cscareerquestions style) | documents/online_assessments.txt |
| 7 | negotiating_offers.txt | Forum Q&A (r/cscareerquestions style) | documents/negotiating_offers.txt |
| 8 | applying_broadly.txt | Forum Q&A (r/cscareerquestions style) | documents/applying_broadly.txt |
| 9 | faang_interview_process.txt | Forum Q&A (r/cscareerquestions style) | documents/faang_interview_process.txt |
| 10 | career_growth.txt | Forum Q&A (r/cscareerquestions style) | documents/career_growth.txt |

Each document is structured as a top-level question followed by multiple ranked answers (modeled after high-upvote forum threads), covering a distinct subtopic: getting started, technical prep, GPA, resume, behavioral interviews, online assessments, negotiation, application strategy, FAANG-specific process, and long-term career growth.

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 50 characters

**Why these choices fit your documents:**

Each document is a structured Q&A with content organized as numbered lists, bold-header bullet points, and short prose paragraphs — not long continuous prose. A single piece of actionable advice (one bullet from the STAR method explanation, one numbered OA tip, one sentence of negotiation guidance) typically runs 100–300 characters. A 400-character chunk captures one complete thought — a list item plus its immediate surrounding context — without pulling in advice from the next unrelated point.

Going larger (e.g., 800 characters) would dilute relevance by bundling multiple distinct tips into one chunk, making the embedding vector represent a mixture of topics rather than a focused concept. Going smaller (e.g., 150 characters) would fragment individual bullets mid-sentence, producing chunks that begin with dependent clauses and lose their meaning out of context.

The 50-character overlap ensures that a sentence spanning a chunk boundary (rare given the separator priority, but possible in longer prose paragraphs) is still discoverable from both sides. `RecursiveCharacterTextSplitter` is configured with separators in priority order `["\n\n", "\n", ".", " "]`, so splits prefer double newlines (between Q&A comments), then single newlines (between list items), then sentence boundaries — character-level cuts are a last resort.

Preprocessing strips runs of three or more blank lines down to two and collapses multiple spaces to one, so the splitter sees clean paragraph boundaries rather than inconsistent whitespace from copy-paste artifacts.

**Final chunk count:** 106 chunks across 10 documents (avg ~10–11 chunks per document)

---

## Sample Chunks

Three representative chunks drawn from different documents, showing how a 400-character window captures one coherent unit of advice:

**Chunk from `gpa_importance.txt` (chunk 0, 184 chars):**
```
Q: My GPA is a 3.1. Am I cooked for tech internships? Does GPA even matter?

A (top comment, 934 upvotes):
The honest answer: GPA matters at the screening stage and almost never after.
```

**Chunk from `leetcode_preparation.txt` (chunk 0, 382 chars):**
```
Q: How much LeetCode do I actually need to do? I've been grinding for months and still feel unprepared.

A (top comment, 1.2k upvotes):
The dirty secret is that most people are doing LeetCode wrong. They grind 400 problems and still blank
in interviews because they never actually learned the patterns — they just memorized solutions.

**Do fewer problems, understand them deeper.**
```

**Chunk from `negotiating_offers.txt` (chunk 0, 260 chars):**
```
Q: Can I negotiate internship offers? Is it weird to ask for more money as a student?

A (top comment, 1.04k upvotes):
Yes, you can negotiate internship offers. No, it is not weird. Yes, you should probably do it.

**The truth about intern offer negotiation:**
```

Notice that each chunk ends naturally at a structural boundary (a blank line or a bold section header), preserving readability and semantic coherence without mid-sentence cuts.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`

This model produces 384-dimensional dense vectors and runs entirely on CPU with no API dependency. It handles the 400-character English-language chunks well within its 256-token context window (chunks average ~80–100 tokens). Embeddings are `normalize_embeddings=True` so cosine similarity in ChromaDB's HNSW index is computed correctly. The model is fast enough to embed all 106 chunks at startup in under two seconds on a laptop.

**Production tradeoff reflection:**

`all-MiniLM-L6-v2` was the right choice for a local prototype, but a production deployment would prompt a more careful evaluation of four tradeoffs:

- **Accuracy vs. latency:** `bge-large-en-v1.5` and `e5-large-v2` both outperform `all-MiniLM-L6-v2` on BEIR retrieval benchmarks by 3–6 points, at the cost of roughly 4× the inference time and a 335M-parameter model vs. 22M. For a system serving many concurrent users, that latency compounds. For a single-user guide like this, it would be straightforward to upgrade.
- **Domain specificity:** `all-MiniLM-L6-v2` was pre-trained on general English text, not CS recruiting vocabulary. Terms like "LP questions" (Amazon Leadership Principles), "GCA" (CodeSignal's General Coding Assessment), or "Handshake" (the student job platform) may not embed as distinctly as they would in a domain-fine-tuned model. A fine-tuned encoder trained on Q&A pairs from r/cscareerquestions would close this gap directly.
- **Context length:** For longer documents (e.g., PDFs, blog posts), a 256-token limit would force aggressive chunking. `text-embedding-3-large` (OpenAI) supports up to 8,191 tokens, which would allow larger, more coherent chunks — at the cost of per-token API pricing on every query and ingestion run.
- **Multilingual support:** Not a concern here (all documents are English), but relevant if the corpus expanded to include advice for international students from non-English forums.

---

## Grounded Generation

**System prompt grounding instruction:**

The model receives the following system prompt verbatim on every query:

> *"You are a CS career advisor. Answer the student's question using only the provided context. If the context does not contain enough information, say I don't have enough information on that. Cite the source document filename for each piece of advice you give."*

This instruction does three things structurally: it restricts the model to the provided context window rather than its parametric knowledge ("using only the provided context"), it creates an explicit refusal signal for out-of-scope questions rather than allowing hallucination ("say I don't have enough information"), and it requires inline attribution ("cite the source document filename") so responses are verifiable against the originating chunks.

**How source attribution is surfaced in the response:**

The user message presents retrieved chunks in a numbered context block, each labeled with its source filename:

```
[1] (source: negotiating_offers.txt)
<chunk text>

[2] (source: career_growth.txt)
<chunk text>
...

Question: <user query>
```

The model is instructed to cite by filename inline as it synthesizes an answer. The `answer()` function in `rag_pipeline.py` also returns a separate `sources` key containing the deduplicated set of filenames from all 4 retrieved chunks, which the Gradio interface displays in a second output box. This means source attribution is enforced at two levels: the LLM is prompted to cite inline, and the pipeline surface the raw retrieval sources regardless of what the LLM writes.

The model is called at `temperature=0.2` to reduce creative variation and keep answers grounded in the retrieved text rather than paraphrased loosely from training memory.

---

## Retrieval Test Results

Three queries run directly against `vectorstore.retrieve()` to verify that top-4 results are semantically correct before generation:

**Query: "how to get my first internship with no experience"**
| Rank | Source | Distance |
|------|--------|----------|
| 1 | getting_first_internship.txt | 0.192 |
| 2 | getting_first_internship.txt | 0.363 |
| 3 | career_growth.txt | 0.392 |
| 4 | getting_first_internship.txt | 0.409 |

3 of 4 chunks from the correct document; `career_growth.txt` rank 3 is partially relevant (discusses the internship leveling ladder). Strong retrieval.

**Query: "GPA cutoff ATS filter tech companies"**
| Rank | Source | Distance |
|------|--------|----------|
| 1 | gpa_importance.txt | 0.406 |
| 2 | gpa_importance.txt | 0.407 |
| 3 | gpa_importance.txt | 0.435 |
| 4 | gpa_importance.txt | 0.472 |

All 4 chunks from the correct document. Distances cluster tightly (0.41–0.47), indicating the query vocabulary ("ATS," "filter," "cutoff") aligned well with the chunk embeddings.

**Query: "how to negotiate an internship offer"**
| Rank | Source | Distance |
|------|--------|----------|
| 1 | negotiating_offers.txt | 0.290 |
| 2 | negotiating_offers.txt | 0.293 |
| 3 | negotiating_offers.txt | 0.324 |
| 4 | negotiating_offers.txt | 0.440 |

All 4 chunks from the correct document. Very low distances (0.29–0.32 for top 3) indicate strong semantic alignment.

---

## Example Responses

**Example 1 — Question:** "What are the 8 algorithm patterns that cover 80% of coding interviews?"

**System response:**
> According to the leetcode_preparation.txt, the 8 algorithm patterns that cover 80% of coding interviews are: Two pointers, Sliding window, BFS/DFS on trees and graphs, Dynamic programming (knapsack, subsequences, intervals), Binary search (not just sorted arrays — on the answer space too), Monotonic stack, Heap/priority queue, Backtracking.
>
> Source: leetcode_preparation.txt

**Example 2 — Question:** "When do Google and Meta typically open summer internship applications, and what happens if I apply in February?"

**System response:**
> According to faang_interview_process.txt, Google and Meta typically open their recruiting cycles for summer internships in August-September and close by December. If you apply in February, you're late for FAANG companies, as the best teams usually fill early. Additionally, getting_first_internship.txt also mentions that applying in March means you've already missed 80% of the opportunities, implying that applying in February is even later.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What are the 8 algorithm patterns that cover 80% of coding interviews? | All 8 named: two pointers, sliding window, BFS/DFS, DP, binary search, monotonic stack, heap/PQ, backtracking | Listed all 8 correctly with inline citation to leetcode_preparation.txt | Relevant (leetcode_preparation.txt in top-4) | Accurate |
| 2 | If my GPA is a 3.1, what are three concrete strategies to still get tech internship interviews? | List major GPA separately; get a referral to bypass ATS; target companies that don't GPA-filter | Returned: target non-filtering companies ✓; build projects/experience (not in expected top-3); try to improve GPA (not in expected top-3). Missed listing major GPA separately and using referrals entirely. | Relevant (all chunks from gpa_importance.txt) | Partially accurate |
| 3 | When do Google and Meta open summer apps, and what happens if I apply in February? | Opens August-September, closes December; applying in February means you are too late for FAANG | Correctly stated August-September open, December close, and that February is too late; also added corroborating context from getting_first_internship.txt about March being 80% too late | Partially relevant (behavioral_interviews.txt appeared in top-4 but was ignored by model) | Accurate |
| 4 | What is the recommended script for negotiating an internship offer over the phone? | Phone script: express enthusiasm, name specific number 10-15% above offer, cite competing offers, don't apologize | Returned "I don't have enough information on that" — the specific script chunk was not in the retrieved top-4 despite negotiating_offers.txt being retrieved | Partially relevant (negotiating_offers.txt retrieved but wrong chunks) | Inaccurate |
| 5 | What weekly habit separates interns who get return offers from those who don't? | Weekly Friday update message to manager: what finished, what issue resolved, plans for next week | Correctly described the Friday manager update with all three components; cited career_growth.txt | Partially relevant (negotiating_offers.txt in top-4 but unused) | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

Overall: 4 of 5 responses were accurate or partially accurate. The one clear failure (Q4) is a retrieval issue, not a generation issue.

---

## Failure Case Analysis

**Question that failed:**
"What is the recommended script for negotiating an internship offer over the phone?"

**What the system returned:**
> "I don't have enough information on that. The provided context (negotiating_offers.txt and career_growth.txt) does not contain a recommended script for negotiating an internship offer over the phone."

This is incorrect — a word-for-word phone script exists in `negotiating_offers.txt` and is one of the most specific pieces of advice in the entire corpus.

**Root cause (tied to a specific pipeline stage):**

This is a **retrieval-stage failure** caused by within-document chunk competition. The `negotiating_offers.txt` document contains several thematically similar chunks — one about what items are negotiable (base rate, signing bonus, housing stipend), one about the general truth that companies expect negotiation and won't rescind offers, one about using competing offers as leverage, and one containing the actual phone script. When the query "recommended script for negotiating an internship offer over the phone" is embedded, its vector is about equally similar to all four of these chunks because they all concern the same narrow topic. The HNSW index returned the chunks about what is negotiable and the general negotiation truth at ranks 1-3 — not the script chunk — because the word "script" and the phrase "over the phone" are not prominent in the chunk that contains the script itself (it opens with "Don't do it over email if you can help it. Call the recruiter."). The embedding model did not treat "script" as strongly distinguishing from the other negotiation chunks, so the specific chunk lost the ranking competition to the more semantically central chunks from the same document.

**What you would change to fix it:**

Two targeted fixes: (1) **Increase top-k from 4 to 6 or 8** for this class of queries — the script chunk would likely appear at rank 5 or 6 given how close the distances are across `negotiating_offers.txt` chunks. (2) **Add a keyword-boosting re-ranking step** after vector retrieval: if the query contains terms like "script," "word for word," or "exact language," apply a BM25 lexical score that would boost the chunk containing the literal word "Script:" near the top, overriding the embedding similarity tie. A hybrid dense + sparse (BM25) retrieval system would have caught this case where the exact vocabulary of the query matches the answer chunk better than the embeddings indicate.

---

## Spec Reflection

**One way the spec helped you during implementation:**

Writing the chunking strategy section of `planning.md` before touching any code forced an explicit decision about separator priority — `["\n\n", "\n", ".", " "]` — that would have been easy to skip and use the `RecursiveCharacterTextSplitter` defaults. Having that decision written down meant the implementation was a direct transcription of the spec rather than an ad-hoc parameter choice. It also made the chunk count estimate (80–150) a testable prediction; when the actual count came back as 106, it confirmed the chunk size was calibrated correctly for the document structure without needing to re-tune.

**One way your implementation diverged from the spec, and why:**

The spec's Retrieval Approach section described enforcing a minimum cosine similarity threshold of 0.35 to exclude marginally relevant chunks. This was not implemented — ChromaDB's `query()` call returns the top-k results by distance regardless of absolute score, and there is no built-in threshold parameter. Filtering results post-query by distance would have been straightforward (discard any result with `distance > 0.65` in cosine space), but evaluation showed the retrieval distances for correct results ranged from 0.19 to 0.47 — a wide enough band that a fixed threshold would have cut legitimate results on some queries. The threshold idea was sound in theory but required empirical calibration against real query results before it could be applied, which only became visible after running the full evaluation. A future iteration would derive the threshold from the evaluation data rather than specifying it in advance.

---

## AI Usage

**Instance 1 — Implementing `ingest.py`**

- *What I gave the AI:* The Domain, Documents table, and Chunking Strategy sections from `planning.md`, plus the text of one sample document (`getting_first_internship.txt`), with a specific prompt requesting a module that reads `.txt` files from `documents/`, applies `RecursiveCharacterTextSplitter` with `chunk_size=400`, `chunk_overlap=50`, and `separators=["\n\n", "\n", ".", " "]`, attaches `source` and `chunk_index` metadata, and returns a list of dicts.
- *What it produced:* A working `ingest.py` with a `load_chunks()` function, a `_clean()` preprocessing helper that strips excess whitespace and collapses blank lines, and a `__main__` block printing the total chunk count and first 5 chunks. Output on first run: 106 chunks, all within the 400-character limit.
- *What I changed or overrode:* The initial function was named `load_chunks()`. After reviewing the full pipeline spec which called for `get_chunks()`, I directed Claude to rename it in `ingest.py` and update the `__main__` reference before writing `vectorstore.py`, to keep the interface consistent with the documented API.

**Instance 2 — Implementing `vectorstore.py`**

- *What I gave the AI:* The Retrieval Approach section from `planning.md` (embedding model name, top-k value, ChromaDB persistence path), the `get_chunks()` function signature from `ingest.py`, and a spec requiring a `retrieve(query, k=4)` function returning dicts with `text`, `source`, and `distance` keys.
- *What it produced:* A `vectorstore.py` with a custom `_STEmbedder` class implementing ChromaDB's `EmbeddingFunction` interface wrapping `SentenceTransformer("all-MiniLM-L6-v2")`, a `_build_index()` function called at import time that checks `_collection.count() > 0` before re-embedding, and a `retrieve()` function that queries the collection and zips documents, metadata, and distances into the specified dict format. It also included a `__main__` block with 3 test queries.
- *What I changed or overrode:* The first version triggered a `DeprecationWarning` from ChromaDB because `_STEmbedder` did not implement `__init__`. I directed Claude to add an explicit `def __init__(self) -> None: pass` to the class to suppress the warning. I also verified that `normalize_embeddings=True` was set in the encoder call — this is required for cosine distance to be computed correctly in ChromaDB's HNSW index, and the initial output used the default (`False`), which would have returned incorrect similarity rankings.
