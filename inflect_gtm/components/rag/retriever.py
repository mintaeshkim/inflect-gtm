from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os
from typing import List

import os
import pickle
from typing import List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Constants
BASE_DIR = os.path.dirname(__file__)
STORE_DIR = os.path.join(BASE_DIR, "faiss_store")
INDEX_PATH = os.path.join(STORE_DIR, "index.faiss")
METADATA_PATH = os.path.join(STORE_DIR, "metadata.pkl")
MODEL_NAME = "all-MiniLM-L6-v2"

# Load embedding model
model = SentenceTransformer(MODEL_NAME)

# Check existence of vector store files
if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
    raise FileNotFoundError("Vector store not found. Please build it first using vector_store.py")

# Load FAISS index
index = faiss.read_index(INDEX_PATH)

# Load metadata documents
with open(METADATA_PATH, "rb") as f:
    documents = pickle.load(f)

def query_similar_documents(query: str, k: int = 3) -> List[str]:
    """
    Given a query string, retrieve the top-k most similar documents from the FAISS vector store.
    
    Args:
        query (str): Natural language query (e.g. meeting summary)
        k (int): Number of top documents to retrieve

    Returns:
        List[str]: List of top-k similar document texts
    """
    embedding = model.encode([query])
    D, I = index.search(np.array(embedding).astype("float32"), k)
    results = [documents[i] for i in I[0] if i < len(documents)]
    return results

# For testing
if __name__ == "__main__":
    print("🚀 Testing Retriever...")
    test_query = "Slack integration and onboarding discussion"
    results = query_similar_documents(test_query, k=3)
    for idx, doc in enumerate(results, 1):
        print(f"\n--- Result {idx} ---\n{doc}\n")