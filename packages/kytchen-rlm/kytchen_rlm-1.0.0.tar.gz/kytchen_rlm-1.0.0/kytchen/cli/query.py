"""Query execution commands for Kytchen CLI.

Provides commands to execute one-off queries and run kytchenfiles.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional

try:
    import typer
except ImportError:
    print("Error: Typer is not installed. Install with: pip install 'kytchen[cli]'")
    sys.exit(1)

from .utils.output import (
    print_success,
    print_error,
    print_info,
    print_warning,
    print_header,
    print_panel,
    Spinner,
    rule,
)
from .utils.config_loader import load_merged_config


def query_command(
    query: str = typer.Argument(..., help="Query to execute"),
    context: Optional[str] = typer.Option(
        None,
        "--context",
        "-c",
        help="Context to provide (file path or string)",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Override model from config",
    ),
    max_cost: Optional[float] = typer.Option(
        None,
        "--max-cost",
        help="Override max cost (USD)",
    ),
    max_iterations: Optional[int] = typer.Option(
        None,
        "--max-iterations",
        help="Override max iterations",
    ),
    output_format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format (text, json, markdown)",
    ),
    show_trajectory: bool = typer.Option(
        False,
        "--show-trajectory",
        help="Show execution trajectory",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode",
    ),
) -> None:
    """
    Execute a one-off query.

    Examples:

        kytchen query "What is 2+2?"
        kytchen query "Summarize this document" --context document.txt
        kytchen query "Analyze data" --context data.csv --model gpt-4
        kytchen query "Complex task" --max-cost 1.0 --show-trajectory
    """
    print_header("Kytchen Query", query)

    # Load config
    config = load_merged_config()

    # Apply overrides
    if model:
        config["root_model"] = model
    if max_cost is not None:
        config["max_cost_usd"] = max_cost
    if max_iterations is not None:
        config["max_iterations"] = max_iterations
    if debug:
        config["log_trajectory"] = True

    # Load context if provided
    context_data = None
    if context:
        context_path = Path(context)
        if context_path.exists():
            try:
                with open(context_path, "r", encoding="utf-8") as f:
                    context_data = f.read()
                print_info(f"Loaded context from: {context_path}")
            except Exception as e:
                print_error(f"Failed to load context file: {e}")
                raise typer.Exit(1)
        else:
            # Treat as inline context string
            context_data = context

    # Execute query
    try:
        from kytchen.config import create_kytchen
        from kytchen.types import KytchenConfig

        # Create Kytchen instance
        kytchen_config = KytchenConfig(**config)

        with Spinner("Initializing Kytchen..."):
            kytchen = create_kytchen(kytchen_config)

        # Run query
        with Spinner("Executing query...") as spinner:
            result = kytchen.run(query, context=context_data)

            if show_trajectory:
                spinner.update("Processing results...")

        # Display results
        rule("Result")

        if output_format == "json":
            from .utils.output import print_json

            output = {
                "answer": result.answer,
                "total_cost": result.total_cost_usd,
                "iterations": result.iterations,
                "status": result.status,
            }
            print_json(output)
        elif output_format == "markdown":
            from .utils.output import print_markdown

            print_markdown(f"**Answer:**\n\n{result.answer}")
        else:
            # Text format
            print_panel(result.answer, title="Answer", style="green")

        # Show metadata
        rule()
        print_info(f"Status: {result.status}")
        print_info(f"Iterations: {result.iterations}")
        print_info(f"Total cost: ${result.total_cost_usd:.4f}")

        if result.budget_status.exceeded:
            print_warning("Budget limit exceeded!")

        # Show trajectory if requested
        if show_trajectory and result.trajectory:
            rule("Execution Trajectory")
            for i, step in enumerate(result.trajectory, 1):
                print_info(f"\nStep {i}:")
                print_info(f"  Action: {step.action}")
                if step.code:
                    from .utils.output import print_code

                    print_code(step.code, language="python", title="Code")
                if step.output:
                    print_info(f"  Output: {step.output[:200]}...")

        print_success("\nQuery completed successfully")

    except ImportError as e:
        print_error(f"Failed to import Kytchen: {e}")
        print_info("\nMake sure Kytchen is installed: pip install kytchen")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Query failed: {e}")
        if debug:
            raise
        raise typer.Exit(1)


def run_command(
    kytchenfile: Optional[str] = typer.Argument(
        None,
        help="Path to kytchenfile (default: ./kytchenfile.yaml)",
    ),
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Watch for changes and re-run",
    ),
    output_format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format (text, json, markdown)",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Quiet mode - only output result (useful for CI/CD)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode",
    ),
) -> None:
    """
    Run a kytchenfile (recipe).

    A kytchenfile defines a complete Kytchen workflow including
    configuration, context, and query. Uses schema: kytchen.recipe.v1

    Examples:

        kytchen run
        kytchen run examples/example.kytchenfile.json
        kytchen run --format json --quiet
        kytchen run workflow.yaml --watch
    """
    # Find kytchenfile
    if kytchenfile:
        kytchenfile_path = Path(kytchenfile)
    else:
        # Auto-discover
        from .utils.config_loader import find_project_config

        kytchenfile_path = find_project_config()

    if not kytchenfile_path or not kytchenfile_path.exists():
        if quiet and output_format == "json":
            import json as json_lib
            print(json_lib.dumps({"success": False, "error": "No kytchenfile found"}))
        else:
            print_error("No kytchenfile found")
            print_info("\nTo create one, run: kytchen init")
        raise typer.Exit(1)

    if not quiet:
        print_header("Kytchen Run", str(kytchenfile_path))

    # Watch mode
    if watch:
        if not quiet:
            print_info("Watch mode enabled - press Ctrl+C to stop")
        _run_with_watch(kytchenfile_path, output_format, debug, quiet)
    else:
        _run_recipe(kytchenfile_path, output_format, debug, quiet)


def _run_recipe(
    kytchenfile_path: Path,
    output_format: str,
    debug: bool,
    quiet: bool = False,
) -> None:
    """Execute kytchenfile using the recipe module (SHA-319)."""
    import json as json_lib

    try:
        # Load kytchenfile using recipe module
        from kytchen.recipe import (
            load_kytchenfile,
            RecipeRunner,
        )

        if not quiet:
            with Spinner("Loading kytchenfile..."):
                recipe_config = load_kytchenfile(kytchenfile_path)
        else:
            recipe_config = load_kytchenfile(kytchenfile_path)

        # Create recipe runner
        runner = RecipeRunner(recipe_config)
        runner.start()

        # Load datasets and build context
        if not quiet:
            with Spinner("Loading datasets..."):
                loaded_datasets = runner.load_datasets()
        else:
            loaded_datasets = runner.load_datasets()

        # Verify hashes if present
        failures = runner.verify_datasets()
        if failures and not quiet:
            print_warning(f"Hash verification failed for: {', '.join(failures)}")

        # Build context from datasets
        if len(loaded_datasets) == 1:
            context = list(loaded_datasets.values())[0]
        elif loaded_datasets:
            # Multi-context: combine with labels
            from kytchen.types import ContextCollection
            items = [(ds_id, content) for ds_id, content in loaded_datasets.items()]
            context = ContextCollection(items=items)
        else:
            context = ""

        # Create Kytchen instance
        from kytchen.config import create_kytchen, KytchenConfig

        kytchen_config = KytchenConfig(
            root_model=recipe_config.model if recipe_config.model != "default" else "claude-sonnet-4-20250514",
            max_iterations=recipe_config.max_iterations,
            max_tokens=recipe_config.max_tokens,
            max_cost_usd=recipe_config.max_cost_usd,
            max_wall_time_seconds=recipe_config.timeout_seconds,
            log_trajectory=True,
        )

        if not quiet:
            with Spinner("Initializing Kytchen..."):
                kytchen = create_kytchen(kytchen_config)
        else:
            kytchen = create_kytchen(kytchen_config)

        # Run query
        if not quiet:
            with Spinner(f"Executing: {recipe_config.query[:60]}..."):
                result = kytchen.complete_sync(recipe_config.query, context=context)
        else:
            result = kytchen.complete_sync(recipe_config.query, context=context)

        # Update runner metrics
        runner.update_tokens(result.total_tokens, result.total_cost_usd)
        runner.metrics.iterations = result.total_iterations

        # Collect evidence from trajectory
        evidence_count = 0
        if recipe_config.require_evidence and result.trajectory:
            for step in result.trajectory:
                if hasattr(step, 'result') and step.result:
                    # Add key findings as evidence
                    snippet = str(step.result)[:200] if step.result else ""
                    if snippet and snippet != "(no output)":
                        runner.add_sauce(
                            source="trajectory",
                            snippet=snippet,
                            note=f"Step {step.step_number}",
                        )
                        evidence_count += 1

        # Finalize and compute efficiency
        recipe_result = runner.finalize(
            answer=result.answer,
            success=result.success,
            error=result.error,
        )

        # Build output
        output = {
            "success": recipe_result.success,
            "answer": recipe_result.answer,
            "efficiency_ratio": round(recipe_result.metrics.efficiency_ratio, 4),
            "evidence_count": recipe_result.metrics.evidence_count,
            "tokens_used": recipe_result.metrics.tokens_used,
            "tokens_baseline": recipe_result.metrics.tokens_baseline,
            "tokens_saved": recipe_result.metrics.tokens_saved,
            "iterations": recipe_result.metrics.iterations,
            "cost_usd": round(recipe_result.metrics.cost_usd, 6),
            "wall_time_seconds": round(recipe_result.metrics.wall_time_seconds, 3),
        }

        if recipe_result.error:
            output["error"] = recipe_result.error

        # Display results
        if output_format == "json":
            print(json_lib.dumps(output, ensure_ascii=False))
        elif output_format == "markdown":
            if not quiet:
                from .utils.output import print_markdown
                efficiency_pct = recipe_result.metrics.efficiency_ratio * 100
                md = f"""## Result

**Answer:** {recipe_result.answer}

### Metrics
- **Efficiency:** {efficiency_pct:.1f}% tokens saved
- **Evidence:** {recipe_result.metrics.evidence_count} citations collected
- **Tokens:** {recipe_result.metrics.tokens_used:,} used / {recipe_result.metrics.tokens_baseline:,} baseline
- **Cost:** ${recipe_result.metrics.cost_usd:.4f}
- **Time:** {recipe_result.metrics.wall_time_seconds:.2f}s
"""
                print_markdown(md)
            else:
                print(recipe_result.answer)
        else:
            # Text format
            if not quiet:
                print_panel(recipe_result.answer, title="Answer", style="green")

                rule("Metrics")
                efficiency_pct = recipe_result.metrics.efficiency_ratio * 100
                print_info(f"Efficiency: {efficiency_pct:.1f}% tokens saved")
                print_info(f"Evidence: {recipe_result.metrics.evidence_count} citations collected")
                print_info(f"Tokens: {recipe_result.metrics.tokens_used:,} used / {recipe_result.metrics.tokens_baseline:,} baseline")
                print_info(f"Cost: ${recipe_result.metrics.cost_usd:.4f}")
                print_info(f"Time: {recipe_result.metrics.wall_time_seconds:.2f}s")

                if recipe_result.success:
                    print_success("\nRun completed successfully")
                else:
                    print_error(f"\nRun failed: {recipe_result.error}")
            else:
                print(recipe_result.answer)

        # Exit code based on success
        if not recipe_result.success:
            raise typer.Exit(1)

    except FileNotFoundError as e:
        if quiet and output_format == "json":
            print(json_lib.dumps({"success": False, "error": str(e)}))
        else:
            print_error(f"File not found: {e}")
        raise typer.Exit(1)
    except ValueError as e:
        if quiet and output_format == "json":
            print(json_lib.dumps({"success": False, "error": str(e)}))
        else:
            print_error(f"Invalid kytchenfile: {e}")
        raise typer.Exit(1)
    except Exception as e:
        if quiet and output_format == "json":
            print(json_lib.dumps({"success": False, "error": str(e)}))
        else:
            print_error(f"Run failed: {e}")
        if debug:
            raise
        raise typer.Exit(1)


def _run_once(
    kytchenfile_path: Path,
    output_format: str,
    debug: bool,
) -> None:
    """Execute kytchenfile once (legacy, kept for compatibility)."""
    _run_recipe(kytchenfile_path, output_format, debug, quiet=False)


def _run_with_watch(
    kytchenfile_path: Path,
    output_format: str,
    debug: bool,
    quiet: bool = False,
) -> None:
    """Execute kytchenfile in watch mode."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print_error("Watchdog is not installed. Install with: pip install watchdog")
        sys.exit(1)

    class KytchenFileHandler(FileSystemEventHandler):
        def __init__(self, path: Path):
            self.path = path.resolve()
            self.last_run = 0.0

        def on_modified(self, event):
            # Convert event path to path object
            event_path = Path(event.src_path).resolve()

            # Check if it matches our file
            if event_path == self.path:
                # Debounce (prevent multiple runs for single save)
                current_time = time.time()
                if current_time - self.last_run < 1.0:
                    return
                self.last_run = current_time

                if not quiet:
                    print_info(f"\nChange detected in {self.path.name}")
                    print_info("Re-running recipe...\n")

                try:
                    _run_recipe(kytchenfile_path, output_format, debug, quiet)
                except typer.Exit:
                    # Catch typer exit to keep watcher running
                    pass
                except Exception as e:
                    print_error(f"Error during execution: {e}")

    # Initial run
    try:
        _run_recipe(kytchenfile_path, output_format, debug, quiet)
    except typer.Exit:
        pass
    except Exception as e:
        print_error(f"Error during execution: {e}")

    if not quiet:
        print_info(f"\nWatching {kytchenfile_path.name} for changes...")
        print_info("Press Ctrl+C to stop")

    # Setup observer
    event_handler = KytchenFileHandler(kytchenfile_path)
    observer = Observer()
    observer.schedule(
        event_handler,
        path=str(kytchenfile_path.parent),
        recursive=False
    )
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
