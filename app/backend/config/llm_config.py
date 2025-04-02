import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

"""
Configuration for LLM providers.
"""


class LLMProviderSettings(BaseSettings):
    """Base settings for LLM providers."""

    temperature: float = 0.0
    max_tokens: Optional[int] = None
    max_retries: int = 3


class OpenAISettings(LLMProviderSettings):
    """Settings for OpenAI."""

    api_key: str | None = os.getenv("OPENAI_API_KEY")
    default_model: str = "gpt-4o-mini-2024-07-18"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    embedding_column: str = "te3s_embedding"


class AzureOpenAISettings(LLMProviderSettings):
    """Settings for AzureOpenAI."""

    api_key: str | None = os.getenv("AZURE_OPENAI_API_KEY")
    default_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    embedding_column: str = "te3s_embedding"
    api_version: str = "2024-02-01"
    azure_endpoint: str | None = os.getenv("AZURE_OPENAI_ENDPOINT")


class AnthropicSettings(LLMProviderSettings):
    """Settings for Anthropic."""

    api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    default_model: str = "claude-3-5-sonnet-20240620"
    # default_model: str = "claude-3-5-haiku-20241022"
    max_tokens: int | None = 16384  # 16k


class LlamaSettings(LLMProviderSettings):
    """Settings for Llama."""

    api_key: str = "key"  # required, but not used
    default_model: str = "llama3"
    base_url: str = "http://localhost:11434/v1"


class StSettings(LLMProviderSettings):
    """Settings for Sentence transformers."""

    embedding_model: str = (
        "NetherlandsForensicInstitute/robbert-2022-dutch-sentence-transformers"
    )
    embedding_dimension: int = 768
    embedding_column: str = "nfi_embedding"


class LLMConfig(BaseSettings):
    """Configuration for all LLM providers."""

    openai: OpenAISettings = OpenAISettings()
    azureopenai: AzureOpenAISettings = AzureOpenAISettings()
    anthropic: AnthropicSettings = AnthropicSettings()
    llama: LlamaSettings = LlamaSettings()
    sentence_transformer: StSettings = StSettings()
