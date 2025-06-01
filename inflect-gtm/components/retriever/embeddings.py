from typing import List, Dict, Any
import openai
import tiktoken
from dataclasses import dataclass

@dataclass
class TextChunk:
    """Data class for text chunks with content and metadata."""
    text: str
    metadata: Dict[str, Any]

class EmbeddingUtils:
    """Utility class for text embedding and chunking operations."""

    def __init__(self, model: str = "text-embedding-ada-002"):
        """
        Initialize the embedding utilities.

        Args:
            model (str): The embedding model to use.
        """
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in a text string.

        Args:
            text (str): The text to count tokens for.

        Returns:
            int: Number of tokens.
        """
        return len(self.encoding.encode(text))

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        metadata: Dict[str, Any] = None
    ) -> List[TextChunk]:
        """
        Split text into overlapping chunks.

        Args:
            text (str): The text to split.
            chunk_size (int): Maximum size of each chunk in tokens.
            chunk_overlap (int): Number of tokens to overlap between chunks.
            metadata (Dict[str, Any]): Metadata to attach to each chunk.

        Returns:
            List[TextChunk]: List of text chunks.
        """
        if metadata is None:
            metadata = {}

        tokens = self.encoding.encode(text)
        chunks = []
        start_idx = 0

        while start_idx < len(tokens):
            end_idx = min(start_idx + chunk_size, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)

            chunks.append(TextChunk(
                text=chunk_text,
                metadata=metadata.copy()
            ))

            start_idx = end_idx - chunk_overlap

        return chunks

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts using OpenAI's API.

        Args:
            texts (List[str]): List of texts to embed.

        Returns:
            List[List[float]]: List of embedding vectors.
        """
        response = await openai.Embedding.acreate(
            input=texts,
            model=self.model
        )

        return [data["embedding"] for data in response["data"]]


if __name__ == "__main__":
    print("🚀 Testing Embedding Utilities...")
    utils = EmbeddingUtils()

    # Test token counting
    text = "This is a test sentence for token counting."
    token_count = utils.get_token_count(text)
    print("📊 Token count:", token_count)

    # Test text chunking
    long_text = "This is a longer text that needs to be chunked. " * 10
    chunks = utils.chunk_text(long_text, chunk_size=50, chunk_overlap=10)
    print("📝 Number of chunks:", len(chunks))
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}:", chunk.text[:30] + "...") 