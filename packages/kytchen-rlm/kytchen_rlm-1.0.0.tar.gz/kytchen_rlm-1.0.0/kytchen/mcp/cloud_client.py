"""Thin-client MCP server that proxies tool calls to Kytchen Cloud.

This is the default entry point for commercial use: it performs **no local
reasoning or sandbox execution**. It simply exposes MCP tools and forwards each
call to the Kytchen Cloud API over HTTPS.

Environment variables:
- `KYTCHEN_API_KEY` (required): Cloud API key (prefix: `kyt_sk_...`)
- `KYTCHEN_API_URL` (optional): defaults to `https://api.kytchen.dev`
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any, Literal

import httpx


DEFAULT_API_URL = "https://api.kytchen.dev"


@dataclass(slots=True)
class CloudClientConfig:
    api_url: str = DEFAULT_API_URL
    api_key: str | None = None
    timeout_seconds: float = 60.0


class KytchenCloudMCPServer:
    """MCP server that proxies tool calls to Kytchen Cloud."""

    def __init__(self, config: CloudClientConfig | None = None) -> None:
        self.config = config or CloudClientConfig(
            api_url=os.getenv("KYTCHEN_API_URL", DEFAULT_API_URL),
            api_key=os.getenv("KYTCHEN_API_KEY"),
        )

        if not self.config.api_key:
            raise RuntimeError(
                "Missing `KYTCHEN_API_KEY`. Set it to your Kytchen Cloud key (prefix `kyt_sk_...`)."
            )

        try:
            from mcp.server.fastmcp import FastMCP
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "MCP support requires the `mcp` package. Install with `pip install kytchen[mcp]`."
            ) from e

        self.server = FastMCP("kytchen")
        self._register_tools()

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.config.api_key}"}

    async def _post_tool(self, name: str, payload: dict[str, Any]) -> str:
        url = f"{self.config.api_url.rstrip('/')}/v1/tool/{name}"
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            resp = await client.post(url, json=payload, headers=self._headers())
        if resp.status_code >= 400:
            return f"Error ({resp.status_code}): {resp.text}"

        # Prefer JSON {result: "..."} but fall back to raw text.
        try:
            data = resp.json()
            if isinstance(data, dict) and "result" in data:
                return str(data["result"])
        except Exception:
            pass
        return resp.text

    def _register_tools(self) -> None:
        # The cloud API defines the canonical tool set. We proxy the local/dev
        # tool names so MCP hosts can switch between `kytchen` and
        # `kytchen-local` without changing prompts.

        @self.server.tool()
        async def load_context(context: str, context_id: str = "default", format: str = "auto") -> str:
            return await self._post_tool(
                "load_context",
                {"context": context, "context_id": context_id, "format": format},
            )

        @self.server.tool()
        async def peek_context(
            start: int = 0,
            end: int | None = None,
            context_id: str = "default",
            unit: Literal["chars", "lines"] = "chars",
        ) -> str:
            return await self._post_tool(
                "peek_context",
                {"start": start, "end": end, "context_id": context_id, "unit": unit},
            )

        @self.server.tool()
        async def search_context(
            pattern: str,
            context_id: str = "default",
            max_results: int = 10,
            context_lines: int = 2,
        ) -> str:
            return await self._post_tool(
                "search_context",
                {
                    "pattern": pattern,
                    "context_id": context_id,
                    "max_results": max_results,
                    "context_lines": context_lines,
                },
            )

        @self.server.tool()
        async def exec_python(code: str, context_id: str = "default") -> str:
            return await self._post_tool("exec_python", {"code": code, "context_id": context_id})

        @self.server.tool()
        async def get_variable(name: str, context_id: str = "default") -> str:
            return await self._post_tool("get_variable", {"name": name, "context_id": context_id})

        @self.server.tool()
        async def think(question: str, context_id: str = "default") -> str:
            return await self._post_tool("think", {"question": question, "context_id": context_id})

        @self.server.tool()
        async def get_status(context_id: str = "default") -> str:
            return await self._post_tool("get_status", {"context_id": context_id})

        @self.server.tool()
        async def get_evidence(
            context_id: str = "default",
            limit: int = 20,
            offset: int = 0,
            source: str = "any",
            output: Literal["json", "markdown"] = "markdown",
        ) -> str:
            return await self._post_tool(
                "get_evidence",
                {
                    "context_id": context_id,
                    "limit": limit,
                    "offset": offset,
                    "source": source,
                    "output": output,
                },
            )

        @self.server.tool()
        async def finalize(answer: str, context_id: str = "default", confidence: str = "medium") -> str:
            return await self._post_tool(
                "finalize", {"answer": answer, "context_id": context_id, "confidence": confidence}
            )

        @self.server.tool()
        async def chunk_context(
            context_id: str = "default",
            chunk_size: int = 2000,
            overlap: int = 200,
        ) -> str:
            return await self._post_tool(
                "chunk_context",
                {"context_id": context_id, "chunk_size": chunk_size, "overlap": overlap},
            )

        @self.server.tool()
        async def evaluate_progress(
            context_id: str = "default",
            confidence: float = 0.5,
            notes: str | None = None,
        ) -> str:
            return await self._post_tool(
                "evaluate_progress",
                {"context_id": context_id, "confidence": confidence, "notes": notes},
            )

        @self.server.tool()
        async def summarize_so_far(context_id: str = "default", max_chars: int = 2000) -> str:
            return await self._post_tool(
                "summarize_so_far",
                {"context_id": context_id, "max_chars": max_chars},
            )

    async def run(self, transport: str = "stdio") -> None:
        if transport != "stdio":
            raise ValueError("Only stdio transport is supported")
        await self.server.run_stdio_async()


def main() -> None:
    """CLI entry point: `kytchen` (thin client)."""
    asyncio.run(KytchenCloudMCPServer().run())

