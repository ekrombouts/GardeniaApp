import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


# Base settings for all LLM providers
class LLMProviderSettings(BaseSettings):
    temperature: float = 0.0  # Controls randomness in model output
    max_tokens: Optional[int] = None  # Maximum number of tokens in the response
    max_retries: int = 3  # Number of retries for failed requests


# Settings specific to OpenAI's LLMs. Inherits from LLMProviderSettings.
class OpenAISettings(LLMProviderSettings):
    api_key: str | None = os.getenv("OPENAI_API_KEY")
    default_model: str = "gpt-4o-mini-2024-07-18"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    # The name of the column that will be created in the database to store the embeddings
    embedding_column: str = "te3s_embedding"


# Settings specific to Azure OpenAI's LLMs
class AzureOpenAISettings(LLMProviderSettings):
    api_key: str | None = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint: str | None = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version: str = "2024-02-01"
    default_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    embedding_column: str = "te3s_embedding"


# Settings specific to Anthropic's LLMs
class AnthropicSettings(LLMProviderSettings):
    api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    default_model: str = "claude-3-5-sonnet-20240620"
    max_tokens: int | None = 16384  # Claude requires max_tokens to be set


# Settings specific to Llama LLMs
class LlamaSettings(LLMProviderSettings):
    api_key: str = "key"  # Placeholder API key (not used)
    base_url: str = "http://localhost:11434/v1"  # Base URL for Llama server
    default_model: str = "llama3"  # Check available local models with `ollama list`


# Settings specific to Sentence Transformers
class StSettings(LLMProviderSettings):
    embedding_model: str = (
        "NetherlandsForensicInstitute/robbert-2022-dutch-sentence-transformers"
    )
    embedding_dimension: int = 768
    embedding_column: str = "nfi_embedding"


# Main configuration class for LLM providers
class LLMConfig(BaseSettings):
    ## Add or remove comments to enable or disable providers

    # openai: OpenAISettings = OpenAISettings()
    azureopenai: AzureOpenAISettings = AzureOpenAISettings()
    # anthropic: AnthropicSettings = AnthropicSettings()
    # llama: LlamaSettings = LlamaSettings()
    sentence_transformer: StSettings = StSettings()
