# Kytchen Python SDK

Python client for [Kytchen](https://github.com/Shannon-Labs/Kytchen) - BYOLLM Context Orchestration.

## Installation

```bash
pip install kytchen
```

## Quick Start

```python
import asyncio
from kytchen_sdk import KytchenClient, Budget

async def main():
    # Initialize client
    client = KytchenClient(
        api_key="kyt_sk_...",
        base_url="http://localhost:8000",  # For self-hosted
    )

    # Upload a dataset
    dataset = await client.datasets.create("my-data", "document.txt")

    # Query with your own LLM key (BYOLLM)
    result = await client.query(
        query="What is the main topic?",
        dataset_ids=[dataset.id],
        provider="anthropic",
        provider_api_key="sk-ant-...",  # Your Anthropic key
        budget=Budget(max_iterations=10, max_cost_usd=0.50),
    )

    print(result.answer)

    await client.close()

asyncio.run(main())
```

## Features

- **Async-first**: Built on `httpx` for efficient async HTTP
- **BYOLLM**: Bring your own LLM API key (Anthropic, OpenAI)
- **Streaming**: Real-time query progress via SSE
- **Self-host ready**: Works with Docker self-hosted instances
- **Type-safe**: Full type hints and dataclasses

## API Reference

### KytchenClient

```python
client = KytchenClient(
    api_key="kyt_sk_...",
    base_url="https://api.kytchen.dev",  # Optional
    timeout=60.0,  # Optional
)
```

### Datasets

```python
# Upload
dataset = await client.datasets.create("name", "path/to/file.txt")

# List
datasets = await client.datasets.list()

# Get
dataset = await client.datasets.get("dataset-id")

# Delete
await client.datasets.delete("dataset-id")
```

### Query

```python
# Standard query
result = await client.query(
    query="Your question",
    dataset_ids=["id1", "id2"],
    budget=Budget(max_cost_usd=0.50),
    provider="anthropic",
    provider_api_key="your-llm-key",
)

# Streaming query
async for event in client.query_stream(...):
    print(event.type, event.data)
```

## Self-Hosting

For self-hosted Kytchen instances:

```python
client = KytchenClient(
    api_key="kyt_sk_selfhost_dev_key_12345",
    base_url="http://localhost:8000",
)
```

See the [Docker self-host guide](../docker-compose.yml) for setup instructions.

## License

MIT
