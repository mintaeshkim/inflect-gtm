import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import openai
from typing import List, Dict, Any, Optional
import os
from .base import Retriever, RetrievedDocument

class RAGRetriever(Retriever):
    """RAG implementation using ChromaDB and OpenAI embeddings."""

    def __init__(
        self,
        collection_name: str = "default",
        persist_directory: str = "./chroma_db",
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the RAG retriever.

        Args:
            collection_name (str): Name of the ChromaDB collection.
            persist_directory (str): Directory to persist the database.
            openai_api_key (Optional[str]): OpenAI API key (defaults to environment variable).
        """
        super().__init__(name="RAGRetriever")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")

        openai.api_key = self.openai_api_key

        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            is_persistent=True
        ))

        # Initialize embedding function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self.openai_api_key,
            model_name="text-embedding-ada-002"
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

    def _retrieve_impl(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[RetrievedDocument]:
        """
        Implementation of document retrieval using ChromaDB.

        Args:
            query (str): The search query.
            top_k (int): Number of documents to retrieve.
            filters (Optional[Dict[str, Any]]): Optional filters to apply.

        Returns:
            List[RetrievedDocument]: List of retrieved documents.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filters
        )

        documents = []
        for i in range(len(results['documents'][0])):
            doc = RetrievedDocument(
                content=results['documents'][0][i],
                metadata=results['metadatas'][0][i],
                score=results['distances'][0][i]
            )
            documents.append(doc)

        return documents

    def _add_documents_impl(
        self,
        documents: List[Dict[str, Any]],
        metadata: Optional[List[Dict[str, Any]]]
    ) -> None:
        """
        Implementation of document addition to ChromaDB.

        Args:
            documents (List[Dict[str, Any]]): Documents to add.
            metadata (Optional[List[Dict[str, Any]]]): Optional metadata for each document.
        """
        if metadata is None:
            metadata = [{} for _ in documents]

        # Prepare documents for ChromaDB
        ids = [str(i) for i in range(len(documents))]
        texts = [doc['content'] for doc in documents]

        self.collection.add(
            documents=texts,
            metadatas=metadata,
            ids=ids
        )

    def _clear_impl(self) -> None:
        """Implementation of index clearing in ChromaDB."""
        self.collection.delete(where={})


if __name__ == "__main__":
    print("🚀 Testing RAG Retriever...")
    retriever = RAGRetriever()

    # Test adding documents
    test_docs = [
        {"content": "This is a test document about AI."},
        {"content": "Another document about machine learning."}
    ]
    result = retriever.add_documents({"documents": test_docs})
    print("📝 Add documents result:", result)

    # Test retrieval
    result = retriever.retrieve({"query": "AI"})
    print("🔍 Retrieval result:", result)

    # Test clearing
    result = retriever.clear({})
    print("🧹 Clear result:", result) 