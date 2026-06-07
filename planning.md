# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

This project covers **CS internship and career advice for undergraduate students**, sourced from the kind of candid, experience-based guidance that circulates on forums like Reddit (r/cscareerquestions, r/csMajors) but is never found in official university career center handbooks.

The knowledge is valuable because it reflects what actually works in the current recruiting market — including unwritten rules (ATS GPA cutoffs, when FAANG applications open, how to negotiate as an intern) that universities either don't know or won't say directly. Students often learn these lessons too late: applying in February for positions that closed in October, or turning down a "non-prestigious" first internship and sitting out an entire summer. A retrieval system over this corpus lets students ask natural questions and get answers grounded in real-world experience rather than sanitized institutional advice.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | getting_first_internship.txt | Forum Q&A on how freshmen/sophomores with no experience can land their first internship — covers small companies, career centers, networking, class projects, and timing | documents/getting_first_internship.txt |
| 2 | leetcode_preparation.txt | Forum Q&A on effective LeetCode strategy — covers pattern-based learning, the NeetCode 150 list, company-specific prep, timed practice, and when to attempt Hard problems | documents/leetcode_preparation.txt |
| 3 | gpa_importance.txt | Forum Q&A on how much GPA matters for tech internships — covers ATS hard filters, listing major GPA, referral bypasses, which company tiers filter hardest, and GPA recovery | documents/gpa_importance.txt |
| 4 | resume_and_projects.txt | Forum Q&A on resume format and what makes projects impressive — covers the XYZ bullet format, ATS keyword matching, Jake's Resume template, real-user projects, and GitHub profile hygiene | documents/resume_and_projects.txt |
| 5 | behavioral_interviews.txt | Forum Q&A on behavioral interview preparation — covers the STAR method with correct time ratios, building a story bank, Amazon Leadership Principles, recording yourself, and the "why this company" question | documents/behavioral_interviews.txt |
| 6 | online_assessments.txt | Forum Q&A on passing OAs — covers HackerRank/CodeSignal/Codility platforms, the CodeSignal GCA scoring system, problem-order strategy, partial credit, edge cases, and avoiding cheating | documents/online_assessments.txt |
| 7 | negotiating_offers.txt | Forum Q&A on negotiating internship compensation — covers what is negotiable, a specific phone-call script, using competing offers as leverage, Levels.fyi for market data, and how to decline gracefully | documents/negotiating_offers.txt |
| 8 | applying_broadly.txt | Forum Q&A on application volume and strategy — covers the 50-100 application target, a three-tier system (reach/target/safety), job boards beyond LinkedIn, tracking spreadsheets, and keeping the pipeline full | documents/applying_broadly.txt |
| 9 | faang_interview_process.txt | Forum Q&A walking through the intern interview process at Google, Meta, Amazon, Microsoft, and Apple step by step — covers OA formats, phone screen structure, LP questions, timeline, and system design lite | documents/faang_interview_process.txt |
| 10 | career_growth.txt | Forum Q&A on growing during and after internships — covers what earns return offers, communicating blockers, delivering shippable work, managing up, the three-year leveling framework, and peer network value | documents/career_growth.txt |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 50 characters

**Reasoning:** Each document is a structured forum Q&A with a mix of short bullet points, numbered lists, and brief prose paragraphs. A typical piece of actionable advice — e.g., one bullet from the STAR method explanation or one numbered tip from the OA strategy list — fits comfortably within 200-350 characters. Setting chunk size to 400 characters captures a complete thought (one list item plus its immediate context) without pulling in unrelated advice from the next point. Going much larger (e.g., 800+ characters) would dilute relevance by combining advice about multiple distinct sub-topics in a single chunk, making it harder for the embedder to produce a focused vector. Going smaller (e.g., 150 characters) would fragment individual tips mid-sentence.

The 50-character overlap ensures that a sentence split across a chunk boundary is still findable from either side. Because documents use "\n\n" between Q&A sections and "\n" between bullets, RecursiveCharacterTextSplitter will prefer those natural break points over splitting mid-sentence — the overlap is a safety net for the rare case where a paragraph runs longer than 400 characters and must be cut mid-prose.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 4

**Production tradeoff reflection:**

`all-MiniLM-L6-v2` is a strong default for this corpus: it produces 384-dimensional vectors, runs fast on CPU (no GPU required), and captures semantic similarity well for English-language informal advice text. Its 256-token context window is sufficient for 400-character chunks (which average ~80-100 tokens). The main weakness is domain specificity — it was not fine-tuned on CS career or recruiting vocabulary, so it may not distinguish "negotiating an offer" from "receiving an offer" as precisely as a fine-tuned model would.

If deploying for real users without a cost constraint, the tradeoffs worth weighing are:

- **`text-embedding-3-large` (OpenAI)**: Higher accuracy on nuanced semantic similarity, 8192-token context, multilingual support — but adds API latency and per-token cost on every query and re-ingestion. Not needed here since the corpus is English-only and small.
- **`e5-large-v2` or `bge-large-en`**: Both outperform `all-MiniLM-L6-v2` on MTEB benchmarks for retrieval tasks with a modest latency increase. Worth considering if retrieval precision is low in evaluation.
- **Domain-adapted fine-tuning**: Fine-tuning a base encoder on CS career Q&A pairs (question → relevant passage) would directly address vocabulary gaps. Expensive to do right, but would close the semantic gap between student phrasing and document phrasing most effectively.

Top-k of 4 is chosen to give the LLM enough context to synthesize a complete answer (especially for questions that span multiple documents, like "how do I prepare for a FAANG internship interview") without overloading the prompt. With 400-character chunks, 4 chunks add roughly 320-400 tokens of context — well within llama-3.3-70b-versatile's context window and leaving ample room for the system prompt and generated response.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What are the 8 algorithm patterns that cover 80% of coding interviews, according to experienced engineers? | Two pointers, sliding window, BFS/DFS on trees and graphs, dynamic programming (knapsack/subsequences/intervals), binary search (including on the answer space), monotonic stack, heap/priority queue, and backtracking. The system should name all 8 specifically. |
| 2 | If my GPA is a 3.1, what are three concrete strategies to still get tech internship interviews? | (1) List major GPA separately on the resume if it is higher than overall GPA. (2) Get an internal referral, which bypasses ATS GPA filters. (3) Target startups and mid-size companies that do not use GPA as a hard filter, since the filter hits hardest at FAANG and finance/quant firms. |
| 3 | When do Google and Meta typically open summer internship applications, and what happens if I apply in February? | Google and Meta recruiting for summer internships typically opens in August-September and closes by December. Applying in February means you are too late — most FAANG spots are filled. The system should state August-September as the opening window and December as the closing window. |
| 4 | What is the recommended script for negotiating an internship offer over the phone? | Express genuine enthusiasm and name the company as your top choice, state a specific target number (10-15% above the offer), reference competing offers or market data as justification, and do not apologize for asking. The system should include all four elements and note that "more money" without a specific number is ineffective. |
| 5 | What weekly habit separates interns who get return offers from those who don't, according to the career growth advice? | Sending a brief Friday update to your manager each week: what you finished, what issue you ran into and how you resolved it, and what you plan to work on next week. This "managing up" behavior takes 5 minutes but is described as a massive differentiator because most interns stay quiet and let the manager come to them. |

---

## Anticipated Challenges

1. **Chunk boundaries splitting actionable advice mid-list:** Several documents present their core guidance as numbered or bulleted lists where each item is 100-250 characters. A 400-character chunk boundary can land mid-list, producing a chunk that ends with item 2 and another that begins mid-sentence into item 3 with no context. If the retriever fetches the second chunk, the LLM receives a fragment that reads "rate limiting, and is properly deployed beats a complex app…" without knowing it is advice about what makes projects impressive. The mitigation is to configure `RecursiveCharacterTextSplitter` with separators in priority order `["\n\n", "\n", ". ", " "]` so it prefers splitting at double newlines (between Q&A sections) and single newlines (between list items) before splitting mid-sentence. After ingestion, manually inspect 5-10 chunks that were truncated mid-line to confirm the split logic is behaving as expected.

2. **High-overlap vocabulary causing off-topic retrieval on vague queries:** All 10 documents share a dense vocabulary of common terms — "interview," "company," "offer," "experience," "project," "resume," "recruiter." A student asking something broad like "how do I prepare?" will produce a query embedding that is similarly close to chunks from leetcode_preparation.txt, behavioral_interviews.txt, resume_and_projects.txt, and online_assessments.txt simultaneously. The top-4 result set may include one chunk from each of those documents, giving the LLM four loosely related fragments instead of 4 focused chunks on a single topic, leading to a response that is generically true but not specifically helpful. The mitigation is to enforce a minimum cosine similarity threshold (e.g., 0.35) in the ChromaDB retrieval call so that marginally relevant chunks are excluded even if they fall within the top-k count, and to test this behavior explicitly with 2-3 deliberately vague queries during evaluation.

---

## Architecture

```
  ┌─────────────────────┐
  │   DOCUMENT          │
  │   INGESTION         │
  │                     │
  │  10 .txt files      │
  │  from documents/    │
  │  (plain text,       │
  │  forum Q&A format)  │
  │                     │
  │  Tool: Python       │
  │  pathlib + open()   │
  └──────────┬──────────┘
             │  raw text strings
             ▼
  ┌─────────────────────┐
  │   CHUNKING          │
  │                     │
  │  RecursiveCharacter │
  │  TextSplitter       │
  │  (LangChain)        │
  │                     │
  │  chunk_size = 400   │
  │  chunk_overlap = 50 │
  │  separators:        │
  │  ["\n\n","\n",      │
  │   ". ", " "]        │
  │                     │
  │  Output: list of    │
  │  Document objects   │
  │  with source meta   │
  └──────────┬──────────┘
             │  ~N chunks with metadata
             ▼
  ┌─────────────────────┐
  │   EMBEDDING +       │
  │   VECTOR STORE      │
  │                     │
  │  Embedding:         │
  │  all-MiniLM-L6-v2   │
  │  (sentence-         │
  │  transformers)      │
  │  → 384-dim vectors  │
  │                     │
  │  Store:             │
  │  ChromaDB           │
  │  persisted to       │
  │  ./chroma_db/       │
  └──────────┬──────────┘
             │  vector index on disk
             ▼
  ┌─────────────────────┐
  │   RETRIEVAL         │
  │                     │
  │  User query →       │
  │  embed with         │
  │  all-MiniLM-L6-v2   │
  │                     │
  │  ChromaDB cosine    │
  │  similarity search  │
  │                     │
  │  top-k = 4 chunks   │
  │  (min similarity    │
  │  threshold: 0.35)   │
  └──────────┬──────────┘
             │  4 ranked text chunks
             ▼
  ┌─────────────────────┐
  │   GENERATION        │
  │                     │
  │  Prompt template:   │
  │  system role +      │
  │  retrieved context  │
  │  + user question    │
  │                     │
  │  LLM:               │
  │  llama-3.3-70b-     │
  │  versatile          │
  │  via Groq API       │
  │                     │
  │  Output: grounded   │
  │  answer with        │
  │  source attribution │
  └─────────────────────┘
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**

- **Tool:** Claude Code (claude-sonnet-4-6 via this CLI)
- **Input:** The Domain, Documents table, and Chunking Strategy sections of this planning.md, plus the actual contents of one sample document (getting_first_internship.txt) to give Claude concrete text to reason about
- **Prompt:** "Implement a Python module `ingest.py` that: (1) reads all `.txt` files from a `documents/` directory using `pathlib`, (2) applies LangChain's `RecursiveCharacterTextSplitter` with `chunk_size=400`, `chunk_overlap=50`, and `separators=['\n\n', '\n', '. ', ' ']`, (3) attaches metadata to each chunk with keys `source` (filename) and `chunk_index` (integer), and (4) returns a list of LangChain `Document` objects. Include a `__main__` block that prints the total chunk count and the first 3 chunks with their metadata."
- **Expected output:** A working `ingest.py` that produces 80-150 total chunks (estimated from document lengths), with no chunk exceeding 400 characters and no chunk shorter than 50 characters after overlap
- **Verification:** Run `python ingest.py` and inspect printed output; grep for any chunk longer than 400 characters using `max(len(c.page_content) for c in chunks)`; manually read 3 chunks that span a section boundary (e.g., end of first Q&A answer into the start of the second) to confirm the split fell on a newline not mid-word

**Milestone 4 — Embedding and retrieval:**

- **Tool:** Claude Code
- **Input:** The Retrieval Approach section of this planning.md, plus the `Document` object schema output by `ingest.py`
- **Prompt:** "Implement a Python module `vectorstore.py` that: (1) imports `ingest.py` and calls it to get chunks, (2) initializes a `SentenceTransformer('all-MiniLM-L6-v2')` embedding function, (3) creates a persistent ChromaDB collection at `./chroma_db/` using the sentence-transformers embedding, (4) upserts all chunks (skipping if the collection already exists and is non-empty), and (5) exposes a `retrieve(query: str, k: int = 4) -> list[Document]` function that embeds the query and returns the top-k most similar chunks as LangChain Documents. Use `chromadb.PersistentClient`."
- **Expected output:** A `vectorstore.py` where calling `retrieve('how to get first internship')` returns 4 chunks that include content from `getting_first_internship.txt`, and calling `retrieve('GPA cutoff ATS filter')` returns chunks from `gpa_importance.txt`
- **Verification:** Run both test queries above and print results; confirm source metadata on returned documents; re-run after deleting `./chroma_db/` to confirm re-ingestion works from scratch

**Milestone 5 — Generation and interface:**

- **Tool:** Claude Code for the pipeline module; manual testing for the CLI loop
- **Input:** The Evaluation Plan table (all 5 test questions and expected answers), the `retrieve()` function signature from `vectorstore.py`, and the spec: Groq API, model `llama-3.3-70b-versatile`, system prompt that instructs the model to answer only from the provided context and cite sources by filename
- **Prompt:** "Implement `rag_pipeline.py` with a `answer(query: str) -> str` function that: (1) calls `retrieve(query, k=4)`, (2) formats retrieved chunks into a context block with source labels, (3) calls the Groq API using the `groq` Python client with model `llama-3.3-70b-versatile` and a system prompt that says 'You are a CS career advisor. Answer the student's question using only the provided context. Cite the source document for each piece of advice.', and (4) returns the model's text response. Also implement a CLI loop in `main.py` that reads user input, calls `answer()`, and prints the response until the user types 'quit'."
- **Expected output:** Running `python main.py` starts an interactive Q&A loop; each of the 5 evaluation questions returns an answer that matches the expected answer in the Evaluation Plan table and names at least one source document
- **Verification:** Run all 5 evaluation questions from the Evaluation Plan table by hand; score each response as pass/fail against the expected answer; a response that gives the correct fact but misattributes the source is a partial pass; a response that contradicts the document is a fail requiring prompt revision
