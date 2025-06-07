import os
import pickle
from typing import List
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


# Define paths
BASE_DIR = os.path.dirname(__file__)
STORE_DIR = os.path.join(BASE_DIR, "faiss_store")
INDEX_PATH = os.path.join(STORE_DIR, "index.faiss")
METADATA_PATH = os.path.join(STORE_DIR, "metadata.pkl")
MODEL_NAME = "all-MiniLM-L6-v2"

# Load embedding model
embedding_model = SentenceTransformer(MODEL_NAME)

# Load vector store index and metadata
if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
    raise FileNotFoundError("❌ Vector store not found. Please run vector_store.py to build the index first.")

index = faiss.read_index(INDEX_PATH)

with open(METADATA_PATH, "rb") as f:
    metadata_store = pickle.load(f)

def query_similar_documents(query: str, top_k: int = 3) -> List[str]:
    """
    Retrieve the top-k most similar documents to the input query.

    Args:
        query (str): Natural language query string.
        top_k (int): Number of similar documents to return.

    Returns:
        List[str]: List of matched document texts.
    """
    query_vec = embedding_model.encode([query], convert_to_numpy=True).astype("float32")
    distances, indices = index.search(query_vec, top_k)

    results = []
    for idx in indices[0]:
        if idx < len(metadata_store):
            results.append(metadata_store[idx].get("text", ""))
    return results


# Unit test
if __name__ == "__main__":
    print("🚀 Testing Retriever...")
    sample_query = "Slack integration and onboarding discussion"
    top_results = query_similar_documents(sample_query, top_k=3)

    for i, doc in enumerate(top_results, 1):
        print(f"\n--- Result {i} ---\n{doc}")