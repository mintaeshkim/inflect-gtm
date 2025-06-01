from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class RetrievedDocument:
    """Data class for retrieved documents with content, metadata, and relevance score."""
    content: str
    metadata: Dict[str, Any]
    score: float

class Retriever:
    """Base class for all retrievers in the system."""

    def __init__(self, name: str):
        """
        Initialize the retriever.

        Args:
            name (str): Name of the retriever.
        """
        self.name = name

    def retrieve(
        self,
        context: Dict[str, Any],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[RetrievedDocument]]:
        """
        Retrieve relevant documents based on the query in context.

        Args:
            context (Dict[str, Any]): Context containing the query and other parameters.
            top_k (int): Number of documents to retrieve.
            filters (Optional[Dict[str, Any]]): Optional filters to apply to the retrieval.

        Returns:
            Dict[str, List[RetrievedDocument]]: Dictionary with retriever name as key and list of retrieved documents as value.
        """
        query = context.get("query", "")
        documents = self._retrieve_impl(query, top_k, filters)
        return {self.name: documents}

    def add_documents(
        self,
        context: Dict[str, Any],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, str]:
        """
        Add documents to the retriever's index.

        Args:
            context (Dict[str, Any]): Context containing documents to add.
            metadata (Optional[List[Dict[str, Any]]]): Optional metadata for each document.

        Returns:
            Dict[str, str]: Dictionary with retriever name as key and status message as value.
        """
        documents = context.get("documents", [])
        self._add_documents_impl(documents, metadata)
        return {self.name: f"Added {len(documents)} documents to index."}

    def clear(self, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Clear all documents from the retriever's index.

        Args:
            context (Dict[str, Any]): Context (unused).

        Returns:
            Dict[str, str]: Dictionary with retriever name as key and status message as value.
        """
        self._clear_impl()
        return {self.name: "Cleared all documents from index."}

    def _retrieve_impl(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[RetrievedDocument]:
        """
        Implementation of document retrieval.

        Args:
            query (str): The search query.
            top_k (int): Number of documents to retrieve.
            filters (Optional[Dict[str, Any]]): Optional filters to apply.

        Returns:
            List[RetrievedDocument]: List of retrieved documents.
        """
        raise NotImplementedError("Subclasses must implement _retrieve_impl")

    def _add_documents_impl(
        self,
        documents: List[Dict[str, Any]],
        metadata: Optional[List[Dict[str, Any]]]
    ) -> None:
        """
        Implementation of document addition.

        Args:
            documents (List[Dict[str, Any]]): Documents to add.
            metadata (Optional[List[Dict[str, Any]]]): Optional metadata for each document.
        """
        raise NotImplementedError("Subclasses must implement _add_documents_impl")

    def _clear_impl(self) -> None:
        """Implementation of index clearing."""
        raise NotImplementedError("Subclasses must implement _clear_impl") 