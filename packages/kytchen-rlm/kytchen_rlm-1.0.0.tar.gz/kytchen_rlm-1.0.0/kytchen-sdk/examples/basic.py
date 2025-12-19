"""Basic example of using the Kytchen Python SDK."""

import asyncio
import os

from kytchen_sdk import KytchenClient, Budget


async def main():
    # Get API key from environment
    api_key = os.environ.get("KYTCHEN_API_KEY", "kyt_sk_...")

    # For self-hosted instances, set the base URL
    base_url = os.environ.get("KYTCHEN_BASE_URL", "http://localhost:8000")

    async with KytchenClient(api_key=api_key, base_url=base_url) as client:
        # List existing datasets
        print("Existing datasets:")
        datasets = await client.datasets.list()
        for ds in datasets:
            print(f"  - {ds.name} ({ds.id}): {ds.size_bytes} bytes, status={ds.status}")

        # Upload a new dataset
        print("\nUploading test dataset...")
        dataset = await client.datasets.create(
            name="example-doc",
            file="example.txt",  # or pass a Path or file-like object
        )
        print(f"Created dataset: {dataset.id}")

        # Query the dataset (requires provider API key for BYOLLM)
        print("\nQuerying dataset...")
        result = await client.query(
            query="What is the main topic of this document?",
            dataset_ids=[dataset.id],
            budget=Budget(max_iterations=5, max_cost_usd=0.10),
            provider="anthropic",  # or "openai"
            provider_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

        if result.success:
            print(f"\nAnswer: {result.answer}")
            print(f"\nEvidence ({len(result.evidence)} items):")
            for ev in result.evidence:
                print(f"  - [{ev.tool_name}] {ev.snippet[:100]}...")
        else:
            print(f"\nQuery failed: {result.error}")

        # Streaming query example
        print("\n\nStreaming query...")
        async for event in client.query_stream(
            query="Summarize the key points",
            dataset_ids=[dataset.id],
            provider="anthropic",
            provider_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        ):
            print(f"  Event: {event.type} - {event.data}")


if __name__ == "__main__":
    asyncio.run(main())
