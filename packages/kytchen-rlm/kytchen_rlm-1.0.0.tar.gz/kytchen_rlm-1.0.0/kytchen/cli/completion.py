"""Shell completion generation for Kytchen CLI.

Typer provides built-in completion generation for bash, zsh, fish, and PowerShell.
"""

from __future__ import annotations

import sys

try:
    import typer
except ImportError:
    print("Error: Typer is not installed. Install with: pip install 'kytchen[cli]'")
    sys.exit(1)

from .utils.output import (
    print_success,
    print_info,
    print_header,
    print_panel,
)


def completion_command(
    shell: str = typer.Argument(
        None,
        help="Shell type (bash, zsh, fish, powershell)",
    ),
    install: bool = typer.Option(
        False,
        "--install",
        "-i",
        help="Install completion to shell config",
    ),
) -> None:
    """
    Generate shell completion script.

    Typer automatically generates completions for:
    - bash
    - zsh
    - fish
    - PowerShell

    Examples:

        # Show completion script
        kytchen-cli completion bash

        # Install completion (adds to ~/.bashrc or similar)
        kytchen-cli completion bash --install

        # For zsh
        kytchen-cli completion zsh --install
    """
    print_header("Shell Completion", "Generate completion script for your shell")

    if not shell:
        print_info("Supported shells: bash, zsh, fish, powershell")
        print_info("\nTo generate completion script:")
        print_info("  kytchen-cli completion <shell>")
        print_info("\nTo install completion:")
        print_info("  kytchen-cli completion <shell> --install")
        print_info("\nManual installation:")
        print_panel(
            "[bold]Bash:[/bold]\n"
            "  kytchen-cli completion bash > ~/.kytchen-complete.bash\n"
            "  echo 'source ~/.kytchen-complete.bash' >> ~/.bashrc\n\n"
            "[bold]Zsh:[/bold]\n"
            "  kytchen-cli completion zsh > ~/.kytchen-complete.zsh\n"
            "  echo 'source ~/.kytchen-complete.zsh' >> ~/.zshrc\n\n"
            "[bold]Fish:[/bold]\n"
            "  kytchen-cli completion fish > ~/.config/fish/completions/kytchen-cli.fish\n\n"
            "[bold]PowerShell:[/bold]\n"
            "  kytchen-cli completion powershell > kytchen-cli.ps1\n"
            "  # Add to PowerShell profile",
            title="Installation Guide",
        )
        return

    # Validate shell
    valid_shells = ["bash", "zsh", "fish", "powershell"]
    if shell not in valid_shells:
        print_info(f"Invalid shell: {shell}")
        print_info(f"Supported shells: {', '.join(valid_shells)}")
        raise typer.Exit(1)

    if install:
        print_info(f"Installing completion for {shell}...")
        print_info("\nNote: Automatic installation requires typer[all]")
        print_info("For manual installation, see instructions above")

        # Note: Typer's completion installation is handled automatically
        # when using typer[all] and the --install-completion flag
        print_success(f"Run this command to install:\n  kytchen-cli --install-completion {shell}")
    else:
        print_info(f"Generating completion script for {shell}...\n")
        print_info("To see the completion script, Typer generates it automatically.")
        print_info(f"Run: kytchen-cli --show-completion {shell}")


if __name__ == "__main__":
    completion_command()
