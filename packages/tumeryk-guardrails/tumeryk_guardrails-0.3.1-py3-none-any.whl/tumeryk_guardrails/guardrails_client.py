# Copyright Tumeryk 2024

import os
import time
import uuid
import requests
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator
from requests.exceptions import RequestException


class TumerykGuardrailsClient:
    """API Client for Tumeryk Guardrails - Supports both username/password and API key authentication"""

    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize the Tumeryk Guardrails Client.
        
        Args:
            base_url: The base URL for the Tumeryk Guardrails API.
            api_key: Optional API key for authentication (starts with 'tmryk_').
                     Note: API key auth only works with /openai/v1/chat/completions endpoint.
        """
        self.base_url = base_url
        self.token = None
        self.api_key = api_key or os.getenv("TUMERYK_API_KEY")
        self.config_id = None
        self.guard_url = None
        self.openai_url = None
        self.session = requests.Session()
        self.manual_model_score = None

    def _auto_login(self):
        """Automatically login if environment variables are available."""
        # If API key is available, skip username/password login
        if self.api_key:
            return
            
        username = os.getenv("TUMERYK_USERNAME")
        password = os.getenv("TUMERYK_PASSWORD")
        base_url = os.getenv("TUMERYK_BASE_URL")
        
        if not self.base_url:
            if base_url:
                self.set_base_url(base_url)
            else:
                self.set_base_url("https://chat.tmryk.com")
        if username and password:
            try:
                self.login(username, password)
            except RequestException as err:
                print(f"Auto-login failed: {err}")

    def _auto_set_policy(self):
        """Automatically set policy if environment variable is available."""
        policy = os.getenv("TUMERYK_POLICY")
        if policy:
            self.set_policy(policy)

    def _get_headers(self):
        """
        Helper method to get the headers including authorization.
        Note: API key only works with /openai/v1/chat/completions endpoint.
        """
        if self.api_key:
            return {"Authorization": f"Bearer {self.api_key}"}
        if not self.token:
            self._auto_login()
        return {"Authorization": f"Bearer {self.token}"}

    def set_api_key(self, api_key: str):
        """
        Set the API key for authentication.
        
        Note: API key authentication only works with the OpenAI-compatible endpoint
        (/openai/v1/chat/completions). Use chat_completions() or TumerykOpenAI for API key auth.
        
        Args:
            api_key: Tumeryk API key (starts with 'tmryk_').
        """
        self.api_key = api_key
        # Clear token when using API key
        self.token = None

    def login(self, username: str, password: str):
        """Authenticate and store access token."""
        username = username or os.getenv("TUMERYK_USERNAME")
        password = password or os.getenv("TUMERYK_PASSWORD")

        if not self.base_url:
            self.set_base_url(os.getenv("TUMERYK_BASE_URL", "https://chat.tmryk.com"))  

        if not username or not password:
            raise ValueError("Username and password must be provided either as arguments or environment variables.")

        payload = {"grant_type": "password", "username": username, "password": password}
        response = self.session.post(f"{self.base_url}/auth/token", data=payload)
        response.raise_for_status()
        response_data = response.json()

        if "access_token" in response_data:
            self.token = response_data["access_token"]
            # Clear API key when using username/password
            self.api_key = None
        else:
            print("Login failed, no access token in response")
        return response_data

    def get_policies(self) -> str:
        """Fetch available policies and return a list."""
        headers = self._get_headers()
        response = self.session.get(f"{self.base_url}/v1/rails/configs", headers=headers)
        response.raise_for_status()
        return [config['id'] for config in response.json()]

    def set_policy(self, config_id: str) -> str:
        """Set the configuration/policy to be used by the user."""
        self.config_id = config_id
        return {"config": f"Policy being used: {config_id}"}

    def set_model_score(self, score: int):
        """Set a default manual model score for all completion calls."""
        self.manual_model_score = score

    def tumeryk_completions(self, messages, stream: bool = False, policy_id: str = None, generation_options: dict = None, manual_model_score: int = None):
        """
        Send user input to the Guard service using /v1/chat/completions endpoint.
        
        Note: This endpoint requires username/password authentication (JWT).
        For API key authentication, use chat_completions() instead.
        
        A specific policy_id can be passed to override the client's default policy.
        """
        # Check if using API key - redirect to OpenAI endpoint
        if self.api_key and not self.token:
            print("Warning: tumeryk_completions requires JWT auth. Using chat_completions with API key instead.")
            return self.chat_completions(
                messages=messages,
                model=policy_id or self.config_id,
                stream=stream,
            )
        
        headers = self._get_headers()

        # 1. Determine the effective policy to use for this specific call
        effective_policy_id = policy_id
        if effective_policy_id is None:
            # If no override is provided, use the instance's default policy
            if not self.config_id:
                # If the instance's policy isn't set, try loading from ENV
                self._auto_set_policy()
            effective_policy_id = self.config_id

        # 2. Add a check to ensure a policy is actually set
        if not effective_policy_id:
            raise ValueError("No policy specified. Pass a 'policy_id' or set the TUMERYK_POLICY environment variable.")

        # 3. Use the effective_policy_id in the payload
        payload = {"config_id": effective_policy_id, "messages": messages, "stream": stream}

        if generation_options:
            payload["generation_options"] = generation_options

        effective_model_score = manual_model_score
        if effective_model_score is None:
            effective_model_score = self.manual_model_score
            
        if effective_model_score is not None:
            payload["manual_model_score"] = effective_model_score

        try:
            response = self.session.post(self.guard_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except RequestException as err:
            print(f"Request failed: {err}")
            return {"error": f"Request failed: {err}"}
        except Exception as err:
            print(f"An unexpected error occurred: {err}")
            return {"error": f"An unexpected error occurred: {err}"}

    async def tumeryk_completions_async(self, messages, stream: bool = False, policy_id: str = None, generation_options: dict = None, manual_model_score: int = None):
        """
        Async version of tumeryk_completions.
        
        Note: This endpoint requires username/password authentication (JWT).
        For API key authentication, use chat_completions_async() instead.
        
        A specific policy_id can be passed to override the client's default policy.
        """
        # Check if using API key - redirect to OpenAI endpoint
        if self.api_key and not self.token:
            print("Warning: tumeryk_completions_async requires JWT auth. Using chat_completions_async with API key instead.")
            return await self.chat_completions_async(
                messages=messages,
                model=policy_id or self.config_id,
                stream=stream,
            )
        
        headers = self._get_headers()

        # 1. Determine the effective policy to use for this specific call
        effective_policy_id = policy_id
        if effective_policy_id is None:
            # If no override is provided, use the instance's default policy
            if not self.config_id:
                # If the instance's policy isn't set, try loading from ENV
                self._auto_set_policy()
            effective_policy_id = self.config_id

        # 2. Add a check to ensure a policy is actually set
        if not effective_policy_id:
            raise ValueError("No policy specified. Pass a 'policy_id' or set the TUMERYK_POLICY environment variable.")

        # 3. Use the effective_policy_id in the payload
        payload = {"config_id": effective_policy_id, "messages": messages, "stream": stream}

        if generation_options:
            payload["generation_options"] = generation_options

        effective_model_score = manual_model_score
        if effective_model_score is None:
            effective_model_score = self.manual_model_score

        if effective_model_score is not None:
            payload["manual_model_score"] = effective_model_score

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.guard_url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as err:
            print(f"Async request failed: {err}")
            return {"error": f"Async request failed: {err}"}
        except Exception as err:
            print(f"An unexpected async error occurred: {err}")
            return {"error": f"An unexpected async error occurred: {err}"}

    def get_base_url(self):
        """Get the current base URL."""
        return self.base_url

    def set_base_url(self, base_url: str):
        """Set a new base URL."""
        self.base_url = base_url.rstrip('/')
        self.guard_url = f"{self.base_url}/v1/chat/completions"
        self.openai_url = f"{self.base_url}/openai/v1/chat/completions"

    def set_token(self, token: str):
        """Set a new token directly"""
        self.token = token
        # Clear API key when using token
        self.api_key = None

    # =========================================================================
    # OpenAI-Compatible API Methods (supports API key authentication)
    # =========================================================================

    def chat_completions(
        self,
        messages: List[Dict[str, Any]],
        model: str = None,
        policy_id: str = None,
        tools: List[Dict[str, Any]] = None,
        tool_choice: Union[str, Dict] = None,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        stream: bool = False,
        response_format: Dict = None,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        stop: Union[str, List[str]] = None,
        user: str = None,
        metadata: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        OpenAI-compatible chat completions endpoint (/openai/v1/chat/completions).
        
        This method supports API key authentication and provides a drop-in replacement 
        for OpenAI's chat.completions.create() while routing through Tumeryk guardrails.
        
        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: The model/policy to use. Formats: 'policy_name', 'policy:policy_name', or 'agent:agent_name'.
            policy_id: Alternative to model - directly specify the policy ID.
            tools: Optional list of tool definitions for function calling.
            tool_choice: Control tool usage ('auto', 'none', or specific tool).
            temperature: Sampling temperature (0-2).
            top_p: Nucleus sampling parameter.
            max_tokens: Maximum tokens to generate.
            stream: Enable streaming responses.
            response_format: Output format specification.
            frequency_penalty: Penalize frequent tokens.
            presence_penalty: Penalize repeated tokens.
            stop: Stop sequences.
            user: End-user identifier.
            metadata: Additional metadata for tracking.
            
        Returns:
            OpenAI-compatible response dict with additional Tumeryk metrics.
        """
        if not self.base_url:
            self._auto_login()
            if not self.base_url:
                self.set_base_url(os.getenv("TUMERYK_BASE_URL", "https://chat.tmryk.com"))

        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        # Determine model/policy
        effective_model = model or policy_id
        if not effective_model:
            if not self.config_id:
                self._auto_set_policy()
            effective_model = self.config_id

        if not effective_model:
            raise ValueError("No model/policy specified. Pass 'model', 'policy_id', or set TUMERYK_POLICY environment variable.")

        # Build request payload
        payload = {
            "model": effective_model,
            "messages": messages,
            "stream": stream,
        }

        # Add optional parameters
        if tools:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format is not None:
            payload["response_format"] = response_format
        if frequency_penalty != 0:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty != 0:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        if user is not None:
            payload["user"] = user
        if metadata is not None:
            payload["metadata"] = metadata

        try:
            if stream:
                return self._stream_chat_completions(payload, headers)
            else:
                response = self.session.post(self.openai_url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except RequestException as err:
            raise RuntimeError(f"Request failed: {err}")

    def _stream_chat_completions(self, payload: Dict, headers: Dict) -> Iterator[Dict]:
        """Handle streaming chat completions."""
        response = self.session.post(
            self.openai_url,
            json=payload,
            headers=headers,
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        import json
                        yield json.loads(data)
                    except:
                        continue

    async def chat_completions_async(
        self,
        messages: List[Dict[str, Any]],
        model: str = None,
        policy_id: str = None,
        tools: List[Dict[str, Any]] = None,
        tool_choice: Union[str, Dict] = None,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        stream: bool = False,
        response_format: Dict = None,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        stop: Union[str, List[str]] = None,
        user: str = None,
        metadata: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Async OpenAI-compatible chat completions endpoint.
        
        Supports API key authentication. Same parameters as chat_completions().
        
        Note: For streaming, use chat_completions_stream_async() instead.
        """
        if not self.base_url:
            self._auto_login()
            if not self.base_url:
                self.set_base_url(os.getenv("TUMERYK_BASE_URL", "https://chat.tmryk.com"))

        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        # Determine model/policy
        effective_model = model or policy_id
        if not effective_model:
            if not self.config_id:
                self._auto_set_policy()
            effective_model = self.config_id

        if not effective_model:
            raise ValueError("No model/policy specified. Pass 'model', 'policy_id', or set TUMERYK_POLICY environment variable.")

        # Build request payload
        payload = {
            "model": effective_model,
            "messages": messages,
            "stream": stream,
        }

        # Add optional parameters
        if tools:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format is not None:
            payload["response_format"] = response_format
        if frequency_penalty != 0:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty != 0:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        if user is not None:
            payload["user"] = user
        if metadata is not None:
            payload["metadata"] = metadata

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.openai_url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as err:
            raise RuntimeError(f"Async request failed: {err}")

    async def chat_completions_stream_async(
        self,
        messages: List[Dict[str, Any]],
        model: str = None,
        **kwargs
    ) -> AsyncIterator[Dict]:
        """
        Async streaming chat completions.
        
        Yields chunks as they arrive from the server.
        """
        if not self.base_url:
            self._auto_login()
            if not self.base_url:
                self.set_base_url(os.getenv("TUMERYK_BASE_URL", "https://chat.tmryk.com"))

        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        effective_model = model or self.config_id
        if not effective_model:
            self._auto_set_policy()
            effective_model = self.config_id

        if not effective_model:
            raise ValueError("No model/policy specified.")

        payload = {
            "model": effective_model,
            "messages": messages,
            "stream": True,
            **kwargs
        }

        try:
            async with aiohttp.ClientSession() as session:
                async for chunk in self._stream_chat_completions_async(session, payload, headers):
                    yield chunk
        except aiohttp.ClientError as err:
            raise RuntimeError(f"Async stream failed: {err}")

    async def _stream_chat_completions_async(self, session, payload: Dict, headers: Dict) -> AsyncIterator[Dict]:
        """Handle async streaming chat completions."""
        async with session.post(self.openai_url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        import json
                        yield json.loads(data)
                    except:
                        continue


class TumerykOpenAI:
    """
    Drop-in replacement for OpenAI client that routes through Tumeryk guardrails.
    
    Uses the /openai/v1/chat/completions endpoint which supports API key authentication.
    
    Usage:
        from tumeryk_guardrails import TumerykOpenAI
        
        # Initialize with API key
        client = TumerykOpenAI(
            api_key="tmryk_xxx",
            base_url="https://your-guard-server.com"
        )
        
        # Use like OpenAI client
        response = client.chat.completions.create(
            model="your_policy_name",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        **kwargs
    ):
        """
        Initialize OpenAI-compatible client.
        
        Args:
            api_key: Tumeryk API key (starts with 'tmryk_') or set TUMERYK_API_KEY env var.
            base_url: Tumeryk Guard server URL or set TUMERYK_BASE_URL env var.
        """
        self._api_key = api_key or os.getenv("TUMERYK_API_KEY") or os.getenv("OPENAI_API_KEY")
        self._base_url = (base_url or os.getenv("TUMERYK_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://chat.tmryk.com").rstrip('/')
        self._session = requests.Session()
        
        # Create the chat completions interface
        self.chat = self._ChatNamespace(self)

    def _get_headers(self):
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

    class _ChatNamespace:
        """Namespace for chat-related methods."""
        
        def __init__(self, client):
            self._client = client
            self.completions = TumerykOpenAI._CompletionsNamespace(client)
    
    class _CompletionsNamespace:
        """Namespace for completions methods."""
        
        def __init__(self, client):
            self._client = client
        
        def create(
            self,
            messages: List[Dict[str, Any]],
            model: str,
            tools: List[Dict[str, Any]] = None,
            tool_choice: Union[str, Dict] = None,
            temperature: float = None,
            top_p: float = None,
            max_tokens: int = None,
            stream: bool = False,
            response_format: Dict = None,
            frequency_penalty: float = 0,
            presence_penalty: float = 0,
            stop: Union[str, List[str]] = None,
            user: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """
            Create a chat completion.
            
            This mirrors the OpenAI chat.completions.create() interface.
            Uses /openai/v1/chat/completions endpoint with API key authentication.
            
            Args:
                messages: List of message dicts with 'role' and 'content'.
                model: The policy/model to use.
                tools: Optional function calling tools.
                tool_choice: Tool selection mode.
                temperature: Sampling temperature.
                top_p: Nucleus sampling.
                max_tokens: Max tokens to generate.
                stream: Enable streaming.
                response_format: Output format.
                frequency_penalty: Frequency penalty.
                presence_penalty: Presence penalty.
                stop: Stop sequences.
                user: End-user ID.
                
            Returns:
                OpenAI-compatible response with Tumeryk metrics.
            """
            url = f"{self._client._base_url}/openai/v1/chat/completions"
            headers = self._client._get_headers()
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
            }
            
            # Add optional parameters
            if tools:
                payload["tools"] = tools
            if tool_choice is not None:
                payload["tool_choice"] = tool_choice
            if temperature is not None:
                payload["temperature"] = temperature
            if top_p is not None:
                payload["top_p"] = top_p
            if max_tokens is not None:
                payload["max_tokens"] = max_tokens
            if response_format is not None:
                payload["response_format"] = response_format
            if frequency_penalty != 0:
                payload["frequency_penalty"] = frequency_penalty
            if presence_penalty != 0:
                payload["presence_penalty"] = presence_penalty
            if stop is not None:
                payload["stop"] = stop
            if user is not None:
                payload["user"] = user
            
            # Add any extra parameters
            for key, value in kwargs.items():
                if value is not None:
                    payload[key] = value
            
            try:
                if stream:
                    return self._stream(url, payload, headers)
                else:
                    response = self._client._session.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    return ChatCompletionResponse(response.json())
            except RequestException as err:
                raise RuntimeError(f"Request failed: {err}")
        
        def _stream(self, url: str, payload: Dict, headers: Dict) -> Iterator:
            """Handle streaming responses."""
            response = self._client._session.post(
                url,
                json=payload,
                headers=headers,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            import json
                            yield ChatCompletionChunk(json.loads(data))
                        except:
                            continue


# Alias for backward compatibility
OpenAICompatibleClient = TumerykOpenAI


class ChatCompletionResponse:
    """Wrapper for chat completion responses to provide attribute access."""
    
    def __init__(self, data: Dict):
        self._data = data
        self.id = data.get('id', '')
        self.object = data.get('object', 'chat.completion')
        self.created = data.get('created', 0)
        self.model = data.get('model', '')
        self.choices = [ChatCompletionChoice(c) for c in data.get('choices', [])]
        self.usage = ChatCompletionUsage(data.get('usage', {}))
        self.metrics = data.get('metrics', {})
    
    def __getitem__(self, key):
        return self._data[key]
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def to_dict(self) -> Dict:
        return self._data


class ChatCompletionChoice:
    """Wrapper for choice objects."""
    
    def __init__(self, data: Dict):
        self._data = data
        self.index = data.get('index', 0)
        self.message = ChatCompletionMessage(data.get('message', {}))
        self.finish_reason = data.get('finish_reason', '')
        self.logprobs = data.get('logprobs')


class ChatCompletionMessage:
    """Wrapper for message objects."""
    
    def __init__(self, data: Dict):
        self._data = data
        self.role = data.get('role', '')
        self.content = data.get('content', '')
        self.tool_calls = data.get('tool_calls')
        self.function_call = data.get('function_call')


class ChatCompletionUsage:
    """Wrapper for usage objects."""
    
    def __init__(self, data: Dict):
        self._data = data
        self.prompt_tokens = data.get('prompt_tokens', 0)
        self.completion_tokens = data.get('completion_tokens', 0)
        self.total_tokens = data.get('total_tokens', 0)


class ChatCompletionChunk:
    """Wrapper for streaming chunks."""
    
    def __init__(self, data: Dict):
        self._data = data
        self.id = data.get('id', '')
        self.object = data.get('object', 'chat.completion.chunk')
        self.created = data.get('created', 0)
        self.model = data.get('model', '')
        self.choices = [ChatCompletionChunkChoice(c) for c in data.get('choices', [])]


class ChatCompletionChunkChoice:
    """Wrapper for streaming choice objects."""
    
    def __init__(self, data: Dict):
        self._data = data
        self.index = data.get('index', 0)
        self.delta = ChatCompletionDelta(data.get('delta', {}))
        self.finish_reason = data.get('finish_reason')


class ChatCompletionDelta:
    """Wrapper for delta objects in streaming."""
    
    def __init__(self, data: Dict):
        self._data = data
        self.role = data.get('role')
        self.content = data.get('content')
        self.tool_calls = data.get('tool_calls')
