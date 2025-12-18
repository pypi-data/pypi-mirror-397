# Tumeryk Guardrails Client

The Tumeryk Guardrails Client is a Python package that provides an interface to the Tumeryk Guardrails API. The client allows you to easily use the API from your Python code.

## Setup

To install the Tumeryk Guardrails Client, use pip:

```bash
pip install tumeryk_guardrails
```

## Authentication Methods

| Method | Endpoint | Client |
|--------|----------|--------|
| **API Key** (`tmryk_xxx`) | `/openai/v1/chat/completions` | `TumerykOpenAI` or `chat_completions()` |
| **Username/Password** (JWT) | `/v1/chat/completions` | `tumeryk_completions()` |

## Example .env File

```
TUMERYK_USERNAME=sample_username
TUMERYK_PASSWORD=sample_password
TUMERYK_POLICY=hr_policy
TUMERYK_API_KEY=tmryk_your_api_key_here
TUMERYK_BASE_URL=https://chat.tmryk.com
```

---

## OpenAI-Compatible API (API Key Authentication)

### Quick Start with TumerykOpenAI

```python
from tumeryk_guardrails import TumerykOpenAI

# Initialize with API key
client = TumerykOpenAI(
    api_key="tmryk_your_api_key_here",
    base_url="https://chat.tmryk.com"  # or your Guard server URL
)

# Use exactly like OpenAI's client
response = client.chat.completions.create(
    model="your_policy_name",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)

# Access Tumeryk-specific metrics
print(f"Trust Score: {response.metrics.get('trust_score')}")
print(f"Model Score: {response.metrics.get('model_score')}")
```

### Using Environment Variables

```python
from tumeryk_guardrails import TumerykOpenAI

# API key is read from TUMERYK_API_KEY or OPENAI_API_KEY env var
client = TumerykOpenAI()

response = client.chat.completions.create(
    model="my_policy",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Using the Default Client with API Key

```python
import tumeryk_guardrails

# Set API key
tumeryk_guardrails.set_api_key("tmryk_your_api_key_here")
tumeryk_guardrails.set_base_url("https://chat.tmryk.com")

# Use OpenAI-compatible endpoint
response = tumeryk_guardrails.chat_completions(
    messages=[{"role": "user", "content": "Hello!"}],
    model="your_policy_name"
)

print(response)
```

### Drop-in OpenAI Replacement

`TumerykOpenAI` is designed as a drop-in replacement for the OpenAI Python client:

```python
# Before (OpenAI)
from openai import OpenAI
client = OpenAI(api_key="sk-...")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

# After (Tumeryk with guardrails)
from tumeryk_guardrails import TumerykOpenAI
client = TumerykOpenAI(api_key="tmryk_...")
response = client.chat.completions.create(
    model="your_policy_name",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Function Calling / Tools

```python
from tumeryk_guardrails import TumerykOpenAI

client = TumerykOpenAI(api_key="tmryk_...")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="your_policy_name",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"Function: {tool_call['function']['name']}")
        print(f"Arguments: {tool_call['function']['arguments']}")
```

### Streaming Responses

```python
from tumeryk_guardrails import TumerykOpenAI

client = TumerykOpenAI(api_key="tmryk_...")

# Stream the response
for chunk in client.chat.completions.create(
    model="your_policy_name",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### All Supported Parameters

```python
response = client.chat.completions.create(
    model="your_policy_name",
    messages=[{"role": "user", "content": "Hello!"}],
    temperature=0.7,
    top_p=0.9,
    max_tokens=500,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=["\n"],
    user="user-123",
    stream=False,
    tools=None,
    tool_choice=None,
    response_format={"type": "text"}
)
```

### Agent Tracking

Track different agents/workflows using the model namespace format:

```python
# Direct policy reference
response = client.chat.completions.create(
    model="hr_policy",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Explicit policy reference with namespace
response = client.chat.completions.create(
    model="policy:hr_policy",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Agent tracking - looks up agent role and enables run tracking
response = client.chat.completions.create(
    model="agent:research_agent",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Use metadata for additional session tracking
response = client.chat.completions.create(
    model="agent:my_agent",
    messages=[{"role": "user", "content": "Hello!"}],
    metadata={
        "session_id": "user-session-123",
        "workflow_id": "onboarding-flow"
    }
)
```

#### Model Namespace Formats

| Format | Description |
|--------|-------------|
| `policy_name` | Direct config/policy reference |
| `policy:policy_name` | Explicit policy reference |
| `agent:agent_name` | Agent role lookup with run tracking |

### OpenAI-Compatible Response Structure

```python
response = client.chat.completions.create(...)

# Standard OpenAI fields
print(response.id)
print(response.model)
print(response.choices[0].message.content)
print(response.usage.total_tokens)

# Tumeryk metrics
metrics = response.metrics
print(f"Trust Score: {metrics.get('trust_score')}")
print(f"Model Score: {metrics.get('model_score')}")
print(f"Real-time Score: {metrics.get('real_time_score')}")
print(f"Jailbreak Score: {metrics.get('jailbreak_score')}")
print(f"Violation: {metrics.get('violation')}")
print(f"Topic Relevance: {metrics.get('topic_relevance')}")
```

---

## Tumeryk API (Username/Password Authentication)

### Simple Usage

You can use the Tumeryk Guardrails Client with minimal setup. The client will automatically load the configuration from the .env file if it exists. Here's an example of simple usage:

```python
from dotenv import load_dotenv
load_dotenv()

import tumeryk_guardrails

messages = [{"role": "user", "content": "hi"}]

response = tumeryk_guardrails.tumeryk_completions(messages=messages)

print(response)
```

### Manual Usage

The Tumeryk Guardrails Client uses [chat.tmryk.com](https://chat.tmryk.com) as the default base URL. However, you can change this URL if required. Here's how you can set a custom base URL:

```python
import tumeryk_guardrails

# Set a custom base URL
tumeryk_guardrails.set_base_url("https://your-custom-url.com")
```

### Configuration

The Tumeryk Guardrails Client uses environment variables to store credentials and policy. Here's an example of how to use environment variables:

```python
import tumeryk_guardrails
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve credentials and policy from environment variables
username = os.getenv("TUMERYK_USERNAME")
password = os.getenv("TUMERYK_PASSWORD")
policy = os.getenv("TUMERYK_POLICY")

# Authenticate with Tumeryk Guardrails
tumeryk_guardrails.login(username, password)

# Retrieve available policies
policies = tumeryk_guardrails.get_policies()
print("Available Policies:", policies)

# Set the chosen policy
tumeryk_guardrails.set_policy(policy)

# Prepare a message for the guard service
messages = [{"role": "user", "content": "Example input to guard"}]

# Send a request to the guard service
response = tumeryk_guardrails.tumeryk_completions(messages)
print("Guard Response:")
print(response)
```

### Async Usage

For non-blocking requests, you can use the async version of the completions method. This is useful when you need to make multiple requests concurrently or want to avoid blocking your main thread:

```python
import asyncio
import tumeryk_guardrails

async def async_example():
    # Authenticate (this can be done once)
    tumeryk_guardrails.login(username, password)
    tumeryk_guardrails.set_policy(policy)
    
    # Prepare messages
    messages = [{"role": "user", "content": "Example async input"}]
    
    # Send async request
    response = await tumeryk_guardrails.tumeryk_completions_async(messages)
    print("Async Guard Response:")
    print(response)

# Run the async function
asyncio.run(async_example())
```

### Multiple Concurrent Requests

You can also make multiple requests concurrently:

```python
import asyncio
import tumeryk_guardrails

async def multiple_requests():
    # Setup authentication and policy
    tumeryk_guardrails.login(username, password)
    tumeryk_guardrails.set_policy(policy)
    
    # Prepare multiple messages
    messages_list = [
        [{"role": "user", "content": "First request"}],
        [{"role": "user", "content": "Second request"}],
        [{"role": "user", "content": "Third request"}]
    ]
    
    # Make concurrent requests
    tasks = [
        tumeryk_guardrails.tumeryk_completions_async(messages) 
        for messages in messages_list
    ]
    
    responses = await asyncio.gather(*tasks)
    
    for i, response in enumerate(responses):
        print(f"Response {i+1}:", response)

# Run concurrent requests
asyncio.run(multiple_requests())
```

---

## Advanced Features

### Setting a Default Model Score

You can manually set a default model score that will be used for all completion requests. This is useful when you want to override the automatic model scoring:

```python
import tumeryk_guardrails

# Set a default model score for all requests
tumeryk_guardrails.set_model_score(737)

# All subsequent completion calls will use this score
messages = [{"role": "user", "content": "Your prompt here"}]
response = tumeryk_guardrails.tumeryk_completions(messages)
```

You can also override the model score for individual requests:

```python
import tumeryk_guardrails

# Set a default model score
tumeryk_guardrails.set_model_score(737)

messages = [{"role": "user", "content": "Your prompt here"}]

# Override the default score for this specific request
response = tumeryk_guardrails.tumeryk_completions(
    messages,
    manual_model_score=850
)
```

### Controlling Rails Execution with Generation Options

The `generation_options` parameter allows you to control which security rails (input, output, dialog, retrieval) are executed during the guardrail check. This provides fine-grained control over the validation process:

```python
import tumeryk_guardrails

# Example: Run only output and dialog rails, skip input and retrieval
generation_options = {
    "rails": {
        "input": False,    # Skip input validation
        "output": True,    # Run output validation
        "dialog": True,    # Run dialog validation
        "retrieval": False # Skip retrieval validation
    }
}

messages = [
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."}
]

response = tumeryk_guardrails.tumeryk_completions(
    messages,
    generation_options=generation_options
)
```

### Complete Example with All Advanced Features

Here's a comprehensive example demonstrating all advanced features together:

```python
import asyncio
import tumeryk_guardrails
from dotenv import load_dotenv
import os

load_dotenv()

async def advanced_example():
    # Authenticate
    username = os.getenv("TUMERYK_USERNAME")
    password = os.getenv("TUMERYK_PASSWORD")

    tumeryk_guardrails.login(username, password)

    # Set a default model score
    tumeryk_guardrails.set_model_score(737)

    # Define the input prompt
    user_prompt = "What is the capital of Mozambique?"
    input_messages = [{"role": "user", "content": user_prompt}]

    # Run input policy check
    input_response = await tumeryk_guardrails.tumeryk_completions_async(
        input_messages,
        policy_id="your_policy_name"
    )

    print("Input Check Response:", input_response)

    # Simulate LLM response
    llm_response = "The capital of Mozambique is Maputo."

    # Check output with specific rails configuration
    output_messages = [
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": llm_response}
    ]

    # Configure to run only output and dialog rails
    output_rails_config = {
        "rails": {
            "input": False,
            "output": True,
            "dialog": True,
            "retrieval": False
        }
    }

    # Run output policy check with custom configuration
    output_response = await tumeryk_guardrails.tumeryk_completions_async(
        output_messages,
        policy_id="your_policy_name",
        generation_options=output_rails_config,
        manual_model_score=800  # Override default score for this call
    )

    print("Output Check Response:", output_response)

# Run the example
asyncio.run(advanced_example())
```

---

## Response Structure

The response format differs between the two endpoints:

### TumerykOpenAI Response (OpenAI-Compatible)

```python
{
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "your_policy_name",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "The capital of France is Paris."
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 15,
        "completion_tokens": 10,
        "total_tokens": 25
    },
    "metrics": {
        "trust_score": 850,
        "model_score": 800,
        "real_time_score": 825,
        "input": {
            "fairness_score": 990,
            "moderation_score": 1000,
            "moderation_violations": "Safe",
            "topic_relevance": 1000,
            "jailbreak_score": 995
        },
        "output": {
            "fairness_score": 985,
            "moderation_score": 1000,
            "moderation_violations": "Safe",
            "hallucination_score": -1
        },
        "tools": {
            "requested": 0,
            "executed": 0
        }
    }
}
```

**Accessing TumerykOpenAI response:**

```python
response = client.chat.completions.create(...)

# Standard OpenAI fields
print(response.choices[0].message.content)
print(response.usage.total_tokens)

# Tumeryk metrics
print(response.metrics["trust_score"])
print(response.metrics["input"]["jailbreak_score"])
print(response.metrics["output"]["hallucination_score"])
```

### tumeryk_completions Response (Tumeryk API)

```python
{
    "messages": [
        {
            "role": "assistant",
            "content": "The capital of France is Paris.",
            "stats": {
                "total_calls": 1,
                "total_time": 2.5,
                "total_tokens": 25,
                "total_prompt_tokens": 15,
                "total_completion_tokens": 10
            }
        }
    ],
    "metrics": {
        "violation": false,
        "jailbreak_detection": false,
        "topic_relevance": 1000,
        "trust_score": 850,
        "model_score": 800,
        "real_time_score": 825,
        "hallucination_score": -1.0,
        "bias_score": {
            "input": 990,
            "output": 985
        },
        "toxicity_scores": {
            "input": "Safe",
            "output": "Safe"
        },
        "llama_guard_allowed": {
            "input": true,
            "output": true
        },
        "llama_guard_categories": {
            "input": "Safe",
            "output": "Safe"
        },
        "information": {
            "300": "Low Prompt Injection Score"
        },
        "jailbreak_score": 995,
        "moderation_score_input": 1000,
        "moderation_score_output": 1000
    },
    "log": "# General stats\n- Total time: 2.5s\n..."
}
```

**Accessing tumeryk_completions response:**

```python
response = tumeryk_guardrails.tumeryk_completions(messages)

# Message content
print(response["messages"][0]["content"])

# Metrics
print(response["metrics"]["trust_score"])
print(response["metrics"]["jailbreak_score"])
print(response["metrics"]["bias_score"]["input"])
```

### Metrics Field Reference

| Metric | TumerykOpenAI Location | tumeryk_completions Location | Description |
|--------|------------------------|------------------------------|-------------|
| Trust Score | `metrics.trust_score` | `metrics.trust_score` | Overall trust rating (0-1000) |
| Model Score | `metrics.model_score` | `metrics.model_score` | Model quality score (0-1000) |
| Real-time Score | `metrics.real_time_score` | `metrics.real_time_score` | Real-time processing score |
| Jailbreak Score | `metrics.input.jailbreak_score` | `metrics.jailbreak_score` | Protection against jailbreak (0-1000) |
| Bias (Input) | `metrics.input.fairness_score` | `metrics.bias_score.input` | Input fairness score |
| Bias (Output) | `metrics.output.fairness_score` | `metrics.bias_score.output` | Output fairness score |
| Hallucination | `metrics.output.hallucination_score` | `metrics.hallucination_score` | Hallucination detection (-1 if not run) |
| Topic Relevance | `metrics.input.topic_relevance` | `metrics.topic_relevance` | Topic relevance score |
| Moderation (Input) | `metrics.input.moderation_score` | `metrics.moderation_score_input` | Input safety score |
| Moderation (Output) | `metrics.output.moderation_score` | `metrics.moderation_score_output` | Output safety score |
| Violation | N/A | `metrics.violation` | Boolean policy violation flag |

**Log** (tumeryk_completions only): Detailed processing statistics showing:
- Processing time breakdown by rail type (INPUT, DIALOG, OUTPUT)
- LLM call statistics and token usage
- Individual action execution times and details
- Performance metrics for each processing stage

---

## Available Methods

### OpenAI-Compatible (API Key Auth)

| Method | Description |
|--------|-------------|
| `TumerykOpenAI(api_key, base_url)` | Create OpenAI-compatible client |
| `client.chat.completions.create(...)` | Create chat completion |
| `set_api_key(key)` | Set API key for authentication |
| `chat_completions(messages, model, ...)` | OpenAI-compatible completions |
| `chat_completions_async(messages, model, ...)` | Async OpenAI-compatible completions |

### Tumeryk API (Username/Password Auth)

The Tumeryk Guardrails Client provides the following methods to interact with the Tumeryk Guardrails API:

* `login(username, password)`: Authenticate and store access token.
* `set_token(token)`: Set a token directly without authentication.
* `get_policies()`: Fetch available policies and return a list.
* `set_policy(config_id)`: Set the configuration/policy to be used by the user.
* `set_model_score(score)`: Set a default manual model score for all completion calls.
* `tumeryk_completions(messages)`: Send user input to the Guard service.
* `tumeryk_completions_async(messages)`: Async version of tumeryk_completions for non-blocking requests.
* `get_base_url()`: Get the current base URL.
* `set_base_url(base_url)`: Set a new base URL.

### Detailed Parameters for Completion Methods

Both `tumeryk_completions` and `tumeryk_completions_async` support the following parameters:

* `messages` (required): List of message dictionaries with 'role' and 'content' keys.
* `stream` (optional): Boolean to enable streaming responses (default: False).
* `policy_id` (optional): Override the default policy for this specific request.
* `generation_options` (optional): Dictionary to control which rails to execute. Format:
  ```python
  {
      "rails": {
          "input": True/False,
          "output": True/False,
          "dialog": True/False,
          "retrieval": True/False
      }
  }
  ```
* `manual_model_score` (optional): Integer to override the model score for this specific request.

---

## Migration Guide

### From Username/Password to API Key

```python
# Before (username/password)
import tumeryk_guardrails
tumeryk_guardrails.login("user", "pass")
tumeryk_guardrails.set_policy("my_policy")
response = tumeryk_guardrails.tumeryk_completions(messages)

# After (API key with TumerykOpenAI)
from tumeryk_guardrails import TumerykOpenAI
client = TumerykOpenAI(api_key="tmryk_...")
response = client.chat.completions.create(
    model="my_policy",
    messages=messages
)
```

### From OpenAI SDK

```python
# Before
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# After - just change the import and client initialization
from tumeryk_guardrails import TumerykOpenAI
client = TumerykOpenAI(api_key="tmryk_...")
response = client.chat.completions.create(
    model="your_policy",  # Use your Tumeryk policy name
    messages=[{"role": "user", "content": "Hello"}]
)
# Same response format, with additional .metrics field
```

---

## Dependencies

* **requests**: Used for making HTTP requests to the API.
* **aiohttp**: Used for making async HTTP requests to the API.

## Support

For support, contact [support@tumeryk.com](mailto:support@tumeryk.com) or visit [https://tumeryk.com](https://tumeryk.com).
