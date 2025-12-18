# Evoke SDK

AI Observability SDK for tracking LLM execution and agent workflows.

## Features

- **Automatic tracing**: Works with any LLM provider (OpenAI, Anthropic, custom)
- **Zero code changes**: Just initialize and go
- **Comprehensive telemetry**: Tracks tools, models, prompts, reasoning
- **Simple API**: 2 lines of code

## Installation

```bash
pip install evoke-sdk
```

## Quick Start

```python
import evoke

# Initialize once at startup
evoke.init(api_key="evoke_pk_your_api_key")

# All LLM calls are now automatically traced!
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## What Gets Tracked

- **Models**: Which models were used (gpt-4, claude-3, etc.)
- **Prompts & Responses**: Full input and output data
- **Tools**: Which tools/functions were called
- **Knowledge Bases**: Which vector stores/retrievers were accessed
- **Reasoning**: Agent thinking and decision-making
- **Tokens**: Input/output/cached token counts
- **Timing**: Duration and timestamps
- **Errors**: Exceptions and stack traces

## Optional: Explicit Tracing

Use the `@trace` decorator for high-level workflows:

```python
import evoke

@evoke.trace(name="customer_support_agent")
def handle_customer_query(query: str):
    # Your agent logic
    return agent.run(query)
```

## Optional: Add Custom Context

Link telemetry to business entities:

```python
@evoke.trace(name="process_order")
def process_order(order_id: str, user_id: str):
    evoke.add_context(
        user_id=user_id,
        order_id=order_id,
        environment="production"
    )
    return process()
```

## Flush Before Exit

Ensure all data is sent before your app exits:

```python
import evoke

# At the end of your script
evoke.flush()
```

## Supported Frameworks

- OpenAI SDK
- Anthropic SDK
- LangChain
- LlamaIndex
- Any custom LLM implementation

## Configuration

### Environment Variables

```bash
export EVOKE_API_KEY="evoke_pk_your_key"
export EVOKE_ENDPOINT="https://api.evoke.com/v1/traces"
```

### Debug Mode

```python
evoke.init(
    api_key="evoke_pk_...",
    debug=True  # Enable debug logging
)
```

## License

Other/Proprietary License