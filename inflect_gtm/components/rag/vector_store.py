import os
import faiss
import pickle
from typing import List, Dict
from sentence_transformers import SentenceTransformer

# Define storage paths
STORE_DIR = os.path.join(os.path.dirname(__file__), "faiss_store")
INDEX_PATH = os.path.join(STORE_DIR, "index.faiss")
METADATA_PATH = os.path.join(STORE_DIR, "metadata.pkl")

# Load the embedding model (384-dimensional embeddings)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize FAISS index with appropriate dimension
dim = 384
index = faiss.IndexFlatL2(dim)  # L2 (Euclidean) distance
metadata_store = []  # To store metadata associated with each vector


def load_or_initialize():
    """
    Loads existing FAISS index and metadata if they exist,
    otherwise initializes empty index and metadata store.
    """
    global index, metadata_store
    os.makedirs(STORE_DIR, exist_ok=True)

    if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
        print("🔁 Loading existing FAISS index and metadata...")
        index = faiss.read_index(INDEX_PATH)
        with open(METADATA_PATH, "rb") as f:
            metadata_store = pickle.load(f)
    else:
        print("🆕 Initializing new FAISS index and metadata...")


def save():
    """
    Saves the current FAISS index and metadata to disk.
    """
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata_store, f)


def add_documents(texts: List[str], metadatas: List[Dict] = None):
    """
    Adds a list of documents to the vector store.

    Args:
        texts: List of raw text documents to embed and store.
        metadatas: Optional list of dictionaries containing metadata for each document.
    """
    global metadata_store
    if metadatas is None:
        metadatas = [{} for _ in texts]

    embeddings = embedding_model.encode(texts, convert_to_numpy=True)
    index.add(embeddings)
    metadata_store.extend(metadatas)
    save()


def query_similar(text: str, top_k: int = 3) -> List[Dict]:
    """
    Queries the vector store with a new input and returns top_k similar documents.

    Args:
        text: Input query string.
        top_k: Number of most similar documents to return.

    Returns:
        A list of dicts containing matched text, metadata, and distance.
    """
    embedding = embedding_model.encode([text], convert_to_numpy=True)
    distances, indices = index.search(embedding, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < len(metadata_store):
            results.append({
                "text": metadata_store[idx].get("text", ""),
                "metadata": metadata_store[idx],
                "distance": float(dist)
            })
    return results


# Unit test
if __name__ == "__main__":
    print("🚀 Testing FAISS Vector Store...")
    load_or_initialize()

    # Dummy documents to index
    dummy_docs = [
        "We had a meeting with Sarah to discuss Slack integration.",
        "James mentioned pricing tier concerns in the demo call.",
        "Follow-up with technical support was scheduled next week.",
    ]
    dummy_metas = [{"text": t} for t in dummy_docs]

    add_documents(dummy_docs, dummy_metas)

    # Perform a similarity search
    query = "What did James say about pricing?"
    results = query_similar(query)

    print("\n🔍 Top Matches:")
    for r in results:
        print(f"- {r['text']} (distance={r['distance']:.4f})")