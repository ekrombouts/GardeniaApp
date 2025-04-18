from abc import ABC, abstractmethod
from typing import Any, List

from backend.config.settings import get_settings
from openai import AzureOpenAI, OpenAI
from sentence_transformers import SentenceTransformer


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def _initialize_client(self) -> Any:
        """Initialize the embedding client."""
        pass

    @abstractmethod
    def create_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the embedding dimension."""
        pass

    @abstractmethod
    def get_embedding_column_name(self) -> str:
        """Return the embedding column name."""
        pass


class OpenAIEmbedder(EmbeddingProvider):
    def __init__(self, settings):
        self.settings = settings
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        return OpenAI(api_key=self.settings.api_key)

    def create_embeddings(self, texts, **kwargs) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=texts, model=self.settings.embedding_model
        )
        return [r.embedding for r in response.data]

    def get_dimension(self) -> int:
        return self.settings.embedding_dimension

    def get_embedding_column_name(self) -> str:
        return self.settings.embedding_column


class AzureOpenAIEmbedder(EmbeddingProvider):
    def __init__(self, settings):
        self.settings = settings
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        return AzureOpenAI(
            api_key=self.settings.api_key,
            api_version=self.settings.api_version,
            azure_endpoint=self.settings.azure_endpoint,
        )

    def create_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=texts, model=self.settings.embedding_model
        )
        return [r.embedding for r in response.data]

    def get_dimension(self) -> int:
        return self.settings.embedding_dimension

    def get_embedding_column_name(self) -> str:
        return self.settings.embedding_column


class SentenceTransformerEmbedder(EmbeddingProvider):
    def __init__(self, settings):
        self.settings = settings
        self.client = self._initialize_client()

    def _initialize_client(self) -> SentenceTransformer:
        return SentenceTransformer(self.settings.embedding_model)

    def create_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        return self.client.encode(texts, **kwargs).tolist()

    def get_dimension(self) -> int:
        return self.settings.embedding_dimension

    def get_embedding_column_name(self) -> str:
        return self.settings.embedding_column


class EmbeddingFactory:
    def __init__(self, provider: str):
        self.provider = provider
        settings = get_settings()
        self.settings = getattr(settings.llm, provider)
        self.embedding_provider = self._create_provider()

    def _create_provider(self) -> EmbeddingProvider:
        providers = {
            ## Comment or uncomment the providers you want to use
            # "openai": OpenAIEmbedder,
            "azureopenai": AzureOpenAIEmbedder,
            "sentence_transformer": SentenceTransformerEmbedder,
        }
        provider_class = providers.get(self.provider)
        if provider_class:
            return provider_class(self.settings)
        raise ValueError(f"Unsupported Embedding provider: {self.provider}")

    def create_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        return self.embedding_provider.create_embeddings(texts, **kwargs)

    def get_dimension(self) -> int:
        return self.embedding_provider.get_dimension()

    def get_embedding_column_name(self) -> str:
        return self.settings.embedding_column


# Example usage
if __name__ == "__main__":
    factory = EmbeddingFactory(provider="sentence_transformer")
    texts = ["Hallo, ik heet Eva."]
    embeddings = factory.create_embeddings(texts)
    print(embeddings)
