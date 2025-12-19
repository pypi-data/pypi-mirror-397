"""Configuration management for Kytchen.

KytchenConfig can be instantiated directly, loaded from env vars, or loaded from a
YAML/JSON config file.

The goal is to make it easy to go from *configuration* -> a ready-to-run Kytchen
instance (the kitchen is prepped and ready to cook).
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

from .types import Budget
from .repl.sandbox import DEFAULT_ALLOWED_IMPORTS, SandboxConfig
from .providers.registry import get_provider
from .core import Kytchen


@dataclass(slots=True)
class KytchenConfig:
    """Complete configuration for a Kytchen instance (the kitchen setup)."""

    # Provider / models (the chef and sous chef)
    provider: str = "anthropic"
    root_model: str = "claude-sonnet-4-20250514"
    sub_model: str | None = None
    api_key: str | None = None

    # Budget defaults (portion control)
    max_tokens: int | None = None
    max_cost_usd: float | None = 5.0
    max_iterations: int = 50
    max_depth: int = 2
    max_wall_time_seconds: float = 300.0
    max_sub_queries: int = 100

    # Sandbox (the prep station)
    enable_code_execution: bool = True
    allowed_imports: list[str] = field(default_factory=lambda: list(DEFAULT_ALLOWED_IMPORTS))
    sandbox_timeout_seconds: float = 30.0
    max_output_chars: int = 10_000

    # REPL
    context_var_name: str = "ctx"

    # Caching
    enable_caching: bool = True
    cache_backend: Literal["memory"] = "memory"

    # Observability (the ticket system)
    log_trajectory: bool = True
    log_level: str = "INFO"

    # Custom prompt
    system_prompt: str | None = None

    @classmethod
    def from_file(cls, path: str | Path) -> "KytchenConfig":
        """Load config from YAML or JSON."""

        path = Path(path)
        content = path.read_text(encoding="utf-8")

        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml
            except Exception as e:  # pragma: no cover
                raise RuntimeError(
                    "YAML support requires PyYAML. Install kytchen[yaml] or `pip install pyyaml`."
                ) from e
            data = yaml.safe_load(content) or {}
        else:
            data = json.loads(content) if content.strip() else {}

        if not isinstance(data, dict):
            raise ValueError(f"Config file must parse to an object/dict, got: {type(data)}")
        return cls(**cast(dict[str, Any], data))

    @classmethod
    def from_env(cls) -> "KytchenConfig":
        """Load config from environment variables.
        """

        def getenv_int(name: str, default: int | None) -> int | None:
            v = os.getenv(name)
            if v is None or v == "":
                return default
            return int(v)

        def getenv_float(name: str, default: float | None) -> float | None:
            v = os.getenv(name)
            if v is None or v == "":
                return default
            return float(v)

        provider_api_key = os.getenv("KYTCHEN_LLM_API_KEY") or os.getenv("KYTCHEN_PROVIDER_API_KEY")
        if provider_api_key and provider_api_key.startswith("kyt_sk_"):
            # Likely a Kytchen Cloud API key; ignore for provider auth.
            provider_api_key = None

        return cls(
            provider=os.getenv("KYTCHEN_PROVIDER", "anthropic"),
            root_model=os.getenv("KYTCHEN_MODEL", "claude-sonnet-4-20250514"),
            sub_model=os.getenv("KYTCHEN_SUB_MODEL"),
            api_key=provider_api_key,
            max_tokens=getenv_int("KYTCHEN_MAX_TOKENS", None),
            max_cost_usd=getenv_float("KYTCHEN_MAX_COST", 5.0),
            max_iterations=int(os.getenv("KYTCHEN_MAX_ITERATIONS", "50")),
            max_depth=int(os.getenv("KYTCHEN_MAX_DEPTH", "2")),
            max_wall_time_seconds=float(os.getenv("KYTCHEN_MAX_WALL_TIME", "300")),
            max_sub_queries=int(os.getenv("KYTCHEN_MAX_SUB_QUERIES", "100")),
            enable_caching=os.getenv("KYTCHEN_ENABLE_CACHING", "true").lower() in {"1", "true", "yes"},
            log_trajectory=os.getenv("KYTCHEN_LOG_TRAJECTORY", "true").lower() in {"1", "true", "yes"},
        )

    def to_budget(self) -> Budget:
        """Convert this config to a :class:`~kytchen.types.Budget` instance (portion control)."""
        return Budget(
            max_tokens=self.max_tokens,
            max_cost_usd=self.max_cost_usd,
            max_iterations=self.max_iterations,
            max_depth=self.max_depth,
            max_wall_time_seconds=self.max_wall_time_seconds,
            max_sub_queries=self.max_sub_queries,
        )

    def to_sandbox_config(self) -> SandboxConfig:
        """Convert this config to a :class:`~kytchen.repl.sandbox.SandboxConfig` (prep station setup)."""
        return SandboxConfig(
            allowed_imports=self.allowed_imports,
            max_output_chars=self.max_output_chars,
            timeout_seconds=self.sandbox_timeout_seconds,
            enable_code_execution=self.enable_code_execution,
        )


def create_kytchen(config: KytchenConfig | Mapping[str, object] | str | Path | None = None) -> Kytchen:
    """Factory to create Kytchen from config sources (open the kitchen)."""

    if config is None:
        cfg = KytchenConfig.from_env()
    elif isinstance(config, KytchenConfig):
        cfg = config
    elif isinstance(config, Mapping):
        cfg = KytchenConfig(**cast(dict[str, Any], dict(config)))
    elif isinstance(config, (str, Path)):
        cfg = KytchenConfig.from_file(config)
    else:
        raise TypeError(f"Invalid config type: {type(config)}")

    # Provider instance (the chef)
    provider = get_provider(cfg.provider, api_key=cfg.api_key)

    return Kytchen(
        provider=provider,
        root_model=cfg.root_model,
        sub_model=cfg.sub_model or cfg.root_model,
        budget=cfg.to_budget(),
        sandbox_config=cfg.to_sandbox_config(),
        system_prompt=cfg.system_prompt,
        enable_caching=cfg.enable_caching,
        log_trajectory=cfg.log_trajectory,
    )
