# Kytchen CLI

Production-quality Typer-based CLI for Kytchen v1.0, inspired by Vercel's developer experience.

## Installation

```bash
# Install with CLI dependencies
pip install 'kytchen[cli]'

# Or install individual components
pip install kytchen typer[all] rich questionary keyring python-dotenv
```

## Quick Start

```bash
# Initialize a new project
kytchen-cli init

# Run a query
kytchen-cli query "What is 2+2?"

# Query with context
kytchen-cli query "Summarize this document" --context document.txt

# Configure settings
kytchen-cli config set provider anthropic
kytchen-cli config set max_cost_usd 5.0

# Install MCP server
kytchen-cli mcp install claude-desktop

# Check installation
kytchen-cli doctor
```

## Command Structure

```
kytchen-cli
├── auth          Authentication management
│   ├── login       Log in to Kytchen Cloud
│   ├── logout      Log out
│   └── whoami      Show auth status
├── init          Initialize new project
├── config        Configuration management
│   ├── list        List all config values
│   ├── get         Get a config value
│   ├── set         Set a config value
│   ├── delete      Delete a config value
│   └── path        Show config file path
├── query         Execute a one-off query
├── run           Run a kytchenfile
├── mcp           MCP server management
│   ├── install     Install to MCP client
│   └── uninstall   Uninstall from client
├── workspace     Workspace management
│   ├── list        List workspaces
│   ├── create      Create workspace
│   ├── switch      Switch workspace
│   ├── delete      Delete workspace
│   └── current     Show current workspace
├── keys          API key management (Kytchen Cloud)
│   ├── list        List API keys
│   ├── create      Create new key
│   └── revoke      Revoke a key
├── doctor        Diagnose installation
└── completion    Generate shell completion
```

## Architecture

### Phase 1: CLI Skeleton ✅
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/__init__.py` - Package entry point
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/main.py` - Main Typer app with command groups
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/utils/output.py` - Rich helpers with fallback

### Phase 2: Auth Commands ✅
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/auth.py` - Login, logout, whoami
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/utils/credentials.py` - Keyring storage

### Phase 3: Config Commands ✅
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/config_cmd.py` - Config list, get, set, delete
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/utils/config_loader.py` - Two-tier config system

### Phase 4: Core Commands ✅
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/init_cmd.py` - Project setup wizard with questionary
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/query.py` - Query and run commands
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/workspace.py` - Workspace management
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/keys.py` - API key management

### Phase 5: MCP Migration ✅
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/mcp.py` - MCP server installation (migrated from old CLI)
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/doctor.py` - Diagnostics

### Phase 6: Polish ✅
- `/Volumes/VIXinSSD/kytchen/kytchen/cli/completion.py` - Shell completion
- Updated `/Volumes/VIXinSSD/kytchen/pyproject.toml` - New entry points and dependencies
- Deprecated old `/Volumes/VIXinSSD/kytchen/kytchen/cli.py` with warnings

## Configuration

### Two-Tier Config System

1. **Global Config**: `~/.kytchen/config.yaml` (or `.json`)
2. **Project Config**: `./kytchenfile.yaml` (or `.json`)

Project config takes precedence over global config.
Environment variables take precedence over both.

### Example Config

```yaml
# kytchenfile.yaml
provider: anthropic
root_model: claude-sonnet-4-20250514
max_cost_usd: 5.0
max_iterations: 50
max_depth: 2
enable_caching: true
log_trajectory: true
```

### Environment Variables

```bash
KYTCHEN_PROVIDER=anthropic
KYTCHEN_MODEL=claude-sonnet-4-20250514
KYTCHEN_MAX_COST=5.0
KYTCHEN_MAX_ITERATIONS=50
```

## Authentication

Credentials are stored securely using the system keyring:
- **macOS**: Keychain
- **Windows**: Credential Vault
- **Linux**: Secret Service (gnome-keyring, kwallet, etc.)

Falls back to encrypted file storage if keyring is unavailable.

```bash
# Log in with API key
kytchen-cli auth login --api-key kyt_sk_...

# Check auth status
kytchen-cli auth whoami

# Log out
kytchen-cli auth logout
```

## MCP Server Installation

Supports installation to:
- Claude Desktop
- Cursor (global and project)
- Windsurf
- VSCode
- Claude Code

```bash
# Interactive mode
kytchen-cli mcp install

# Specific client
kytchen-cli mcp install claude-desktop

# All detected clients
kytchen-cli mcp install --all

# Uninstall
kytchen-cli mcp uninstall cursor
```

## Shell Completion

```bash
# Bash
kytchen-cli completion bash > ~/.kytchen-complete.bash
echo 'source ~/.kytchen-complete.bash' >> ~/.bashrc

# Zsh
kytchen-cli completion zsh > ~/.kytchen-complete.zsh
echo 'source ~/.kytchen-complete.zsh' >> ~/.zshrc

# Fish
kytchen-cli completion fish > ~/.config/fish/completions/kytchen-cli.fish

# Or use Typer's built-in installer
kytchen-cli --install-completion bash
```

## Migration from Old CLI

The old `kytchen-rlm` command is deprecated but still works:

```bash
# Old (deprecated)
kytchen-rlm install claude-desktop

# New (recommended)
kytchen-cli mcp install claude-desktop
```

## Dependencies

### Required (with `pip install 'kytchen[cli]'`)
- `typer[all]>=0.12.0` - CLI framework
- `rich>=13.0.0` - Beautiful output
- `questionary>=2.0.0` - Interactive prompts
- `keyring>=25.0.0` - Secure credential storage
- `python-dotenv>=1.0.0` - Environment variable management

### Optional
- `PyYAML>=6.0` - YAML config support (install with `kytchen[yaml]`)
- `watchdog` - File watching for `--watch` mode (not yet implemented)

## Development

```bash
# Install in development mode
pip install -e '.[cli,dev]'

# Run CLI
python -m kytchen.cli.main

# Or use entry point
kytchen-cli --help
```

## Design Principles

1. **Vercel-like UX**: Clean, beautiful, informative output
2. **Graceful Degradation**: Works without Rich/questionary
3. **Secure by Default**: Keyring storage with file fallback
4. **Two-Tier Config**: Global + project-level configuration
5. **Discoverable**: Comprehensive help text and examples
6. **Type-Safe**: Full type hints throughout

## Future Enhancements

- [ ] Watch mode for `kytchen-cli run --watch`
- [ ] API integration for `kytchen-cli keys` commands
- [ ] Cloud deployment commands
- [ ] Recipe management (create, list, run templates)
- [ ] Interactive query builder
- [ ] Cost tracking and budgeting dashboard
- [ ] Plugin system for custom commands

## License

See repository LICENSE file.
