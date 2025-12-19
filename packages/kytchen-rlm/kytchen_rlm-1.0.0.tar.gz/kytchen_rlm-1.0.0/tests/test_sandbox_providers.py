"""Tests for the sandbox provider abstraction.

Tests cover:
- SandboxProvider protocol compliance
- LocalSandbox wrapper functionality
- E2BSandbox (when available)
- Factory function behavior
"""

from __future__ import annotations

import os
import pytest
from typing import Any

from kytchen.sandbox import (
    SandboxConfig,
    SandboxProvider,
    LocalSandbox,
    get_sandbox,
    is_e2b_available,
    should_use_e2b,
)


class TestSandboxConfig:
    """Tests for SandboxConfig."""

    def test_default_config(self) -> None:
        """Default config has reasonable values."""
        config = SandboxConfig()
        assert config.timeout_seconds == 30.0
        assert config.max_output_chars == 10_000
        assert "json" in config.allowed_imports
        assert "re" in config.allowed_imports

    def test_custom_config(self) -> None:
        """Custom config values are respected."""
        config = SandboxConfig(
            timeout_seconds=60.0,
            max_output_chars=5000,
            allowed_imports=["json"],
        )
        assert config.timeout_seconds == 60.0
        assert config.max_output_chars == 5000
        assert config.allowed_imports == ["json"]


class TestLocalSandbox:
    """Tests for LocalSandbox."""

    @pytest.mark.asyncio
    async def test_protocol_compliance(self) -> None:
        """LocalSandbox implements SandboxProvider protocol."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        assert isinstance(sandbox, SandboxProvider)

    @pytest.mark.asyncio
    async def test_sandbox_id(self) -> None:
        """Sandbox has unique ID."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        assert sandbox.sandbox_id.startswith("local-")
        assert len(sandbox.sandbox_id) > 10

    @pytest.mark.asyncio
    async def test_load_context(self) -> None:
        """Loading context makes it available as ctx."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("hello world")

        result = await sandbox.execute("len(ctx)")
        assert result.return_value == 11 or "11" in result.stdout

    @pytest.mark.asyncio
    async def test_execute_simple(self) -> None:
        """Simple code execution works."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("test context")

        result = await sandbox.execute("print('hello')")
        assert "hello" in result.stdout
        assert result.error is None

    @pytest.mark.asyncio
    async def test_execute_with_return(self) -> None:
        """Code with expression returns value."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("test")

        result = await sandbox.execute("1 + 2")
        assert result.return_value == 3 or "3" in str(result.return_value)

    @pytest.mark.asyncio
    async def test_execute_error(self) -> None:
        """Errors are captured properly."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("test")

        result = await sandbox.execute("undefined_variable")
        assert result.error is not None
        assert "NameError" in result.error or "not defined" in result.error

    @pytest.mark.asyncio
    async def test_get_variable(self) -> None:
        """Can get variables from namespace."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("test")

        await sandbox.execute("x = 42")
        value = await sandbox.get_variable("x")
        assert value == 42

    @pytest.mark.asyncio
    async def test_set_variable(self) -> None:
        """Can set variables in namespace."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("test")

        await sandbox.set_variable("y", 100)
        result = await sandbox.execute("y")
        assert result.return_value == 100 or "100" in str(result.return_value)

    @pytest.mark.asyncio
    async def test_helpers_available(self) -> None:
        """Helper functions are available in sandbox."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("hello world this is a test")

        # Test peek
        result = await sandbox.execute("peek(0, 5)")
        assert "hello" in str(result.return_value) or "hello" in result.stdout

        # Test word_count
        result = await sandbox.execute("word_count()")
        assert result.return_value == 6 or "6" in str(result.return_value)

    @pytest.mark.asyncio
    async def test_security_blocks_forbidden(self) -> None:
        """Security checks block forbidden operations."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("test")

        # Should block eval
        result = await sandbox.execute("eval('1+1')")
        assert result.error is not None

        # Should block open
        result = await sandbox.execute("open('/etc/passwd')")
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        """Close cleans up resources."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("test")

        await sandbox.close()
        # After close, sandbox should be cleared
        assert sandbox._repl is None

    @pytest.mark.asyncio
    async def test_evidence_collection(self) -> None:
        """Evidence is collected via cite()."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("important data here")

        await sandbox.execute("cite('important data', note='key finding')")
        evidence = sandbox.get_evidence()

        assert len(evidence) == 1
        # Evidence items are Citation objects or dicts depending on implementation
        item = evidence[0]
        if hasattr(item, 'snippet'):
            assert item.snippet == "important data"
        else:
            assert item.get("snippet") == "important data" or "important data" in str(item)


class TestSandboxFactory:
    """Tests for get_sandbox factory function."""

    @pytest.mark.asyncio
    async def test_factory_returns_local_in_dev(self, monkeypatch: Any) -> None:
        """Factory returns LocalSandbox in dev mode."""
        monkeypatch.setenv("KYTCHEN_DEV_MODE", "1")
        monkeypatch.delenv("E2B_API_KEY", raising=False)

        sandbox = await get_sandbox(workspace_id="test-ws")
        assert isinstance(sandbox, LocalSandbox)
        await sandbox.close()

    @pytest.mark.asyncio
    async def test_factory_with_context(self) -> None:
        """Factory can pre-load context."""
        sandbox = await get_sandbox(
            workspace_id="test-ws",
            context="pre-loaded content",
            force_local=True,
        )
        result = await sandbox.execute("ctx")
        assert "pre-loaded content" in str(result.return_value) or "pre-loaded" in result.stdout
        await sandbox.close()

    @pytest.mark.asyncio
    async def test_factory_force_local(self, monkeypatch: Any) -> None:
        """force_local=True always returns LocalSandbox."""
        # Even if E2B were configured, force_local should override
        sandbox = await get_sandbox(
            workspace_id="test-ws",
            force_local=True,
        )
        assert isinstance(sandbox, LocalSandbox)
        await sandbox.close()


class TestE2BAvailability:
    """Tests for E2B availability checks."""

    def test_e2b_not_available_without_key(self, monkeypatch: Any) -> None:
        """should_use_e2b returns False without API key."""
        monkeypatch.delenv("E2B_API_KEY", raising=False)
        monkeypatch.delenv("KYTCHEN_DEV_MODE", raising=False)

        # Without API key, should not use E2B
        assert not should_use_e2b()

    def test_e2b_not_used_in_dev_mode(self, monkeypatch: Any) -> None:
        """should_use_e2b returns False in dev mode."""
        monkeypatch.setenv("E2B_API_KEY", "test-key")
        monkeypatch.setenv("KYTCHEN_DEV_MODE", "1")

        assert not should_use_e2b()


@pytest.mark.skipif(
    not is_e2b_available() or not os.getenv("E2B_API_KEY"),
    reason="E2B SDK not installed or API key not set"
)
class TestE2BSandbox:
    """Tests for E2BSandbox (requires E2B SDK and API key)."""

    @pytest.mark.asyncio
    async def test_e2b_create_and_execute(self) -> None:
        """E2B sandbox can be created and execute code."""
        from kytchen.sandbox.e2b import E2BSandbox

        sandbox = await E2BSandbox.create(workspace_id="test-ws")
        try:
            await sandbox.load_context("test content")
            result = await sandbox.execute("print('hello from e2b')")
            assert "hello from e2b" in result.stdout
        finally:
            await sandbox.close()

    @pytest.mark.asyncio
    async def test_e2b_sandbox_id(self) -> None:
        """E2B sandbox has unique ID starting with e2b-."""
        from kytchen.sandbox.e2b import E2BSandbox

        sandbox = await E2BSandbox.create(workspace_id="test-ws")
        try:
            assert sandbox.sandbox_id.startswith("e2b-")
        finally:
            await sandbox.close()


class TestSandboxIntegration:
    """Integration tests for sandbox usage patterns."""

    @pytest.mark.asyncio
    async def test_multi_step_analysis(self) -> None:
        """Sandbox supports multi-step analysis workflow."""
        sandbox = LocalSandbox(workspace_id="test-ws")

        # Step 1: Load document
        document = """
        Revenue for Q1: $1,234,567
        Revenue for Q2: $2,345,678
        Revenue for Q3: $3,456,789
        Total employees: 150
        """
        await sandbox.load_context(document)

        # Step 2: Extract numbers
        result = await sandbox.execute("extract_numbers()")
        assert result.error is None

        # Step 3: Search for specific pattern
        result = await sandbox.execute("search(r'Revenue')")
        assert result.error is None

        # Step 4: Count lines
        result = await sandbox.execute("line_count()")
        assert result.error is None

        await sandbox.close()

    @pytest.mark.asyncio
    async def test_persistent_state(self) -> None:
        """State persists across multiple execute calls."""
        sandbox = LocalSandbox(workspace_id="test-ws")
        await sandbox.load_context("test")

        # Set variable
        await sandbox.execute("counter = 0")

        # Increment multiple times
        for _ in range(5):
            await sandbox.execute("counter += 1")

        # Check final value
        result = await sandbox.execute("counter")
        assert result.return_value == 5

        await sandbox.close()
