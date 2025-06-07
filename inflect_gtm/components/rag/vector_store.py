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
    for text, meta in zip(texts, metadatas):
        meta["text"] = text
        metadata_store.append(meta)
    save()


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
    dummy_metas = [{} for _ in dummy_docs]

    add_documents(dummy_docs, dummy_metas)
    print("✅ Documents added and index saved.")