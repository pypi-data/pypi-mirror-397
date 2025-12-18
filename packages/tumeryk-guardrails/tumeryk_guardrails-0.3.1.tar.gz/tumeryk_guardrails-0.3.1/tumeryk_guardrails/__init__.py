from .guardrails_client import (
    TumerykGuardrailsClient,
    TumerykOpenAI,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionMessage,
    ChatCompletionUsage,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionDelta,
)

# Alias for backward compatibility
OpenAICompatibleClient = TumerykOpenAI

# Default client instance for simple usage
client = TumerykGuardrailsClient()

# Legacy API (username/password authentication)
login = client.login
get_policies = client.get_policies
set_policy = client.set_policy
tumeryk_completions = client.tumeryk_completions
tumeryk_completions_async = client.tumeryk_completions_async
get_base_url = client.get_base_url
set_base_url = client.set_base_url
set_token = client.set_token
set_model_score = client.set_model_score

# New API (API key authentication)
set_api_key = client.set_api_key

# OpenAI-compatible API
chat_completions = client.chat_completions
chat_completions_async = client.chat_completions_async
chat_completions_stream_async = client.chat_completions_stream_async

__all__ = [
    # Client classes
    "TumerykGuardrailsClient",
    "TumerykOpenAI",
    "OpenAICompatibleClient",  # Alias for backward compatibility
    
    # Response classes
    "ChatCompletionResponse",
    "ChatCompletionChoice", 
    "ChatCompletionMessage",
    "ChatCompletionUsage",
    "ChatCompletionChunk",
    "ChatCompletionChunkChoice",
    "ChatCompletionDelta",
    
    # Legacy functions
    "login",
    "get_policies",
    "set_policy",
    "tumeryk_completions",
    "tumeryk_completions_async",
    "get_base_url",
    "set_base_url",
    "set_token",
    "set_model_score",
    
    # New functions
    "set_api_key",
    "chat_completions",
    "chat_completions_async",
]
