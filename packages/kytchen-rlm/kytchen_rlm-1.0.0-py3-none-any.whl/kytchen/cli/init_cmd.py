"""Project initialization wizard for Kytchen CLI.

Interactive setup wizard using questionary for a beautiful user experience.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

try:
    import typer
except ImportError:
    print("Error: Typer is not installed. Install with: pip install 'kytchen[cli]'")
    sys.exit(1)

try:
    import questionary
    from questionary import Choice

    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False
    questionary = None
    Choice = None

from .utils.output import (
    print_success,
    print_error,
    print_info,
    print_warning,
    print_header,
    print_panel,
)
from .utils.config_loader import (
    find_project_config,
    save_config_file,
)


# Default CHEF.md content for new projects
CHEF_MD_TEMPLATE = '''# CHEF.md

**TL;DR: `load_context` → `search_context` → `peek_context` → `finalize`**

Don't stuff your context. Search first, read second, cite always.

---

You are the **chef**. Kytchen handles the **prep**.

## The Philosophy

Instead of cramming documents into your context window, use tools to surgically find what you need. This is faster, cheaper, and lets you work with documents of any size.

---

## The Prep Station (Your Tools)

| Tool | What it does | When to use |
|------|--------------|-------------|
| `load_context` | Load your document/data | First step - mise en place |
| `search_context` | Regex search with context | Find what you need |
| `peek_context` | View specific sections | Read around matches |
| `chunk_context` | Split into chunks | Large docs - get a map |
| `exec_python` | Run Python in sandbox | Transform, calculate |
| `get_evidence` | Review citations | Before finalizing |
| `finalize` | Complete with answer | When confident |

---

## Cooking Patterns

### Pattern 1: Search-First (Most Common)
```
load_context → search_context → peek_context → finalize
```

### Pattern 2: Chunked Navigation (Large Docs)
```
load_context → chunk_context → peek each chunk → finalize
```

### Pattern 3: Computational (Data Analysis)
```
load_context → exec_python → get_variable → finalize
```

---

## The Sauce (Evidence)

**Sauce = Source**. Every claim needs sauce.

Kytchen automatically collects evidence as you explore:
- `search_context` records what you searched and found
- `peek_context` records what sections you read
- `exec_python` records transformations

Call `get_evidence` before finalizing to review your trail.

---

## Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| Ask for "the whole document" | Search for what you need |
| Read randomly hoping to find something | Search first, then peek |
| Make claims without evidence | Cite your sauce |
| Load multiple huge contexts | One at a time, explore surgically |

---

## Your First Order

**User asks:** "Summarize this 10-K's risk factors"

```
1. load_context(file_content, context_id="10k")
   → Loaded: 450K chars, ~112K tokens

2. search_context(pattern="risk factor|material risk", max_results=20)
   → Found 18 matches, lines 1240-3890

3. peek_context(start=1235, end=1300, unit="lines")
   → Read the risk factors section header + first items

4. exec_python: extract and categorize risks
   → Grouped into: operational, financial, regulatory, market

5. finalize(answer="...", confidence="high")
   → Answer with line citations, evidence bundle complete
```

**Result:** 30 seconds, ~3K tokens used (vs 112K stuffed), full audit trail.

---

## Remember

**Load. Search. Peek. Process. Finalize.**

You're the chef. Kytchen handles the prep.
'''


def init_command(
    template: Optional[str] = typer.Option(
        None,
        "--template",
        "-t",
        help="Template to use (minimal, full, local, cloud)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing config file",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        "-y",
        help="Skip interactive prompts",
    ),
) -> None:
    """
    Initialize a new Kytchen project.

    Creates a kytchenfile.yaml in the current directory with
    recommended configuration.

    Examples:

        kytchen init
        kytchen init --template minimal
        kytchen init --template cloud --force
        kytchen init --non-interactive
    """
    print_header("Kytchen Project Setup", "Let's configure your project")

    # Check for existing config
    existing_config = find_project_config()
    if existing_config and not force:
        print_warning(f"Config file already exists: {existing_config}")
        print_info("\nUse --force to overwrite")
        raise typer.Exit()

    # Interactive mode
    if not non_interactive and QUESTIONARY_AVAILABLE:
        config = _interactive_setup(template)
    else:
        if not QUESTIONARY_AVAILABLE and not non_interactive:
            print_warning("questionary not installed - using non-interactive mode")
            print_info("Install with: pip install 'kytchen[cli]'")

        config = _non_interactive_setup(template or "minimal")

    # Choose file format
    if not non_interactive and QUESTIONARY_AVAILABLE:
        file_format = questionary.select(
            "Config file format:",
            choices=[
                Choice("YAML (.yaml)", value="yaml"),
                Choice("JSON (.json)", value="json"),
            ],
            default="yaml",
        ).ask()
    else:
        file_format = "yaml"

    # Determine output path
    if file_format == "yaml":
        output_path = Path.cwd() / "kytchenfile.yaml"
    else:
        output_path = Path.cwd() / "kytchenfile.json"

    # Save config
    try:
        save_config_file(output_path, config)
        print_success(f"\nCreated config file: {output_path}")

        # Create CHEF.md (AI guide)
        chef_path = Path.cwd() / "CHEF.md"
        if not chef_path.exists() or force:
            chef_path.write_text(CHEF_MD_TEMPLATE, encoding="utf-8")
            print_success(f"Created AI guide: {chef_path}")

        # Show next steps
        print_panel(
            "[bold]Next steps:[/bold]\n\n"
            "1. Edit kytchenfile.yaml to customize settings\n"
            "2. Review CHEF.md - it teaches AIs how to use Kytchen\n"
            "3. Run a query: kytchen query 'Analyze my document'\n"
            "4. Use MCP: kytchen mcp install\n\n"
            "Learn more: https://kytchen.dev/docs/getting-started",
            title="Getting Started",
            style="green",
        )

    except Exception as e:
        print_error(f"Failed to create config file: {e}")
        raise typer.Exit(1)


def _interactive_setup(template: Optional[str]) -> dict:
    """Interactive setup wizard using questionary."""
    if not QUESTIONARY_AVAILABLE or not questionary:
        raise RuntimeError("questionary is required for interactive mode")

    config = {}

    # Template selection
    if not template:
        template = questionary.select(
            "Choose a template:",
            choices=[
                Choice("Minimal - Just the essentials", value="minimal"),
                Choice("Full - All configuration options", value="full"),
                Choice("Local Development - Optimized for local use", value="local"),
                Choice("Cloud - Optimized for Kytchen Cloud", value="cloud"),
            ],
            default="minimal",
        ).ask()

    # Provider selection
    provider = questionary.select(
        "LLM Provider:",
        choices=[
            Choice("Anthropic (Claude)", value="anthropic"),
            Choice("OpenAI (GPT)", value="openai"),
        ],
        default="anthropic",
    ).ask()

    config["provider"] = provider

    # Model selection
    if provider == "anthropic":
        model_choices = [
            Choice("Claude Sonnet 4 (Recommended)", value="claude-sonnet-4-20250514"),
            Choice("Claude Opus 4.5", value="claude-opus-4-5-20251101"),
            Choice("Claude Haiku 4", value="claude-haiku-4-20250611"),
        ]
    else:
        model_choices = [
            Choice("GPT-4 Turbo", value="gpt-4-turbo-preview"),
            Choice("GPT-4", value="gpt-4"),
            Choice("GPT-3.5 Turbo", value="gpt-3.5-turbo"),
        ]

    root_model = questionary.select(
        "Primary model:",
        choices=model_choices,
        default=model_choices[0].value,
    ).ask()

    config["root_model"] = root_model

    # Budget controls
    max_cost = questionary.text(
        "Maximum cost per query (USD):",
        default="5.0",
        validate=lambda x: x.replace(".", "").isdigit(),
    ).ask()

    config["max_cost_usd"] = float(max_cost)

    # Advanced settings
    if template in ("full", "local"):
        advanced = questionary.confirm(
            "Configure advanced settings?",
            default=False,
        ).ask()

        if advanced:
            max_iterations = questionary.text(
                "Maximum iterations:",
                default="50",
                validate=lambda x: x.isdigit(),
            ).ask()
            config["max_iterations"] = int(max_iterations)

            max_depth = questionary.text(
                "Maximum recursion depth:",
                default="2",
                validate=lambda x: x.isdigit(),
            ).ask()
            config["max_depth"] = int(max_depth)

            enable_caching = questionary.confirm(
                "Enable prompt caching?",
                default=True,
            ).ask()
            config["enable_caching"] = enable_caching

            log_trajectory = questionary.confirm(
                "Log trajectory (for debugging)?",
                default=True,
            ).ask()
            config["log_trajectory"] = log_trajectory

    # Add defaults based on template
    if template == "minimal":
        pass  # Just what we collected
    elif template == "full":
        config.setdefault("max_iterations", 50)
        config.setdefault("max_depth", 2)
        config.setdefault("max_wall_time_seconds", 300.0)
        config.setdefault("max_sub_queries", 100)
        config.setdefault("enable_code_execution", True)
        config.setdefault("sandbox_timeout_seconds", 30.0)
        config.setdefault("enable_caching", True)
        config.setdefault("log_trajectory", True)
        config.setdefault("log_level", "INFO")
    elif template == "local":
        config.setdefault("log_trajectory", True)
        config["max_cost_usd"] = min(config.get("max_cost_usd", 1.0), 1.0)
    elif template == "cloud":
        config.setdefault("enable_caching", True)
        config.setdefault("max_cost_usd", 10.0)

    return config


def _non_interactive_setup(template: str) -> dict:
    """Non-interactive setup with template."""
    config = {
        "provider": "anthropic",
        "root_model": "claude-sonnet-4-20250514",
    }

    if template == "minimal":
        config["max_cost_usd"] = 5.0
    elif template == "full":
        config.update(
            {
                "sub_model": "claude-sonnet-4-20250514",
                "max_tokens": None,
                "max_cost_usd": 5.0,
                "max_iterations": 50,
                "max_depth": 2,
                "max_wall_time_seconds": 300.0,
                "max_sub_queries": 100,
                "enable_code_execution": True,
                "sandbox_timeout_seconds": 30.0,
                "enable_caching": True,
                "log_trajectory": True,
                "log_level": "INFO",
            }
        )
    elif template == "local":
        config.update(
            {
                "max_cost_usd": 1.0,
                "log_trajectory": True,
            }
        )
    elif template == "cloud":
        config.update(
            {
                "max_cost_usd": 10.0,
                "enable_caching": True,
            }
        )
    else:
        print_error(f"Unknown template: {template}")
        raise typer.Exit(1)

    return config
