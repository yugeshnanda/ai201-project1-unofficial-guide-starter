import re
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


DOCUMENTS_DIR = Path(__file__).parent / "documents"

SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " "],
)


def _clean(text: str) -> str:
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_chunks():
    chunks = []
    for path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        cleaned = _clean(raw)
        splits = SPLITTER.split_text(cleaned)
        for idx, text in enumerate(splits):
            chunks.append({
                "text": text,
                "source": path.name,
                "chunk_index": idx,
            })
    return chunks


if __name__ == "__main__":
    chunks = get_chunks()
    print(f"Total chunks: {len(chunks)}\n")
    for chunk in chunks[:5]:
        print(f"--- source={chunk['source']}  chunk_index={chunk['chunk_index']} ---")
        print(chunk["text"])
        print()
