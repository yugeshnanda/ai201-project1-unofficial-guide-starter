from pathlib import Path
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from sentence_transformers import SentenceTransformer

from ingest import get_chunks

CHROMA_DIR = str(Path(__file__).parent / "chroma_db")
COLLECTION_NAME = "cs_career_guide"

_model = SentenceTransformer("all-MiniLM-L6-v2")


class _STEmbedder(EmbeddingFunction):
    def __init__(self) -> None:
        pass

    def __call__(self, input: Documents) -> Embeddings:
        return _model.encode(list(input), normalize_embeddings=True).tolist()


_client = chromadb.PersistentClient(path=CHROMA_DIR)
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=_STEmbedder(),
    metadata={"hnsw:space": "cosine"},
)


def _build_index() -> None:
    if _collection.count() > 0:
        return
    chunks = get_chunks()
    _collection.upsert(
        ids=[f"{c['source']}::{c['chunk_index']}" for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks],
    )


_build_index()


def retrieve(query: str, k: int = 4) -> list[dict]:
    results = _collection.query(query_texts=[query], n_results=k)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]
    return [
        {"text": doc, "source": meta["source"], "distance": round(dist, 4)}
        for doc, meta, dist in zip(docs, metas, distances)
    ]


if __name__ == "__main__":
    test_queries = [
        "how to get my first internship with no experience",
        "GPA cutoff ATS filter tech companies",
        "how to negotiate an internship offer",
    ]
    for query in test_queries:
        print(f"\nQuery: {query!r}")
        print("-" * 60)
        for chunk in retrieve(query):
            print(f"  source={chunk['source']}  distance={chunk['distance']}")
            print(f"  {chunk['text'][:120].replace(chr(10), ' ')}...")
            print()
