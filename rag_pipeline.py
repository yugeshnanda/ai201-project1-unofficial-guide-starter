import os
from dotenv import load_dotenv
from groq import Groq
from vectorstore import retrieve

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])

_SYSTEM_PROMPT = (
    "You are a CS career advisor. "
    "Answer the student's question using only the provided context. "
    "If the context does not contain enough information, say I don't have enough information on that. "
    "Cite the source document filename for each piece of advice you give."
)


def answer(query: str) -> dict:
    chunks = retrieve(query, k=4)

    context_lines = []
    for i, chunk in enumerate(chunks, start=1):
        context_lines.append(f"[{i}] (source: {chunk['source']})\n{chunk['text']}")
    context_block = "\n\n".join(context_lines)

    user_message = f"Context:\n{context_block}\n\nQuestion: {query}"

    response = _client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    answer_text = response.choices[0].message.content.strip()
    sources = sorted({chunk["source"] for chunk in chunks})

    return {"answer": answer_text, "sources": sources}
