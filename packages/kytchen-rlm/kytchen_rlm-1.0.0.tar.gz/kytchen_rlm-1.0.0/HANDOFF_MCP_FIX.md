# Kytchen MCP Server Fix - Handoff Prompt

## Context
You're continuing work on Kytchen, a production-oriented RLM (Recursive Language Model) implementation. The Kytchen MCP server is supposed to make coding easier for LLMs, but it's currently worse than the Aleph MCP server we forked from.

**Problem**: We should be dogfooding our own product, but it's not set up properly.

## What Was Done
1. ✅ Updated pricing page (Starter/Chef/Sous Chef tiers)
2. ✅ Synced billing page with pricing
3. ✅ Removed Replit auth (now Supabase only)
4. ✅ Committed changes: `6d03f14`
5. ✅ Updated MCP configs to use `local_server.py` instead of basic `server.py`

## What Needs To Be Fixed

### 1. Kytchen MCP Server (`kytchen/mcp/local_server.py`)

The local_server has **38 tools** but is missing compared to Aleph:
- No Git integration (git diff, log, status)
- No database support (SQL queries)
- No dialectical reasoning prompts

**Files**:
- `/Volumes/VIXinSSD/kytchen/kytchen/mcp/local_server.py` (2836 lines) - Full-featured API-free server
- `/Volumes/VIXinSSD/kytchen/kytchen/mcp/server.py` (254 lines) - Basic server (don't use)

**Current Config** (`.mcp.json`):
```json
{
  "mcpServers": {
    "kytchen": {
      "command": "/opt/homebrew/bin/python3",
      "args": ["-m", "kytchen.mcp.local_server", "--enable-actions", "--timeout", "60", "--max-output", "20000"],
      "env": {
        "PYTHONPATH": "/Volumes/VIXinSSD/kytchen"
      }
    }
  }
}
```

### 2. E2B Integration

E2B integration **already exists** at:
- `/Volumes/VIXinSSD/kytchen/kytchen/sandbox/e2b.py` (449 lines)
- `/Volumes/VIXinSSD/kytchen/kytchen/sandbox/__init__.py` (167 lines)

**Selection Logic**: Uses E2B when:
1. `E2B_API_KEY` is set
2. `e2b-code-interpreter` SDK is installed
3. `KYTCHEN_DEV_MODE` is NOT set

**To enable E2B**: Set `E2B_API_KEY` environment variable.

### 3. Make Kytchen MCP Work Like Aleph

The Aleph MCP server (which I'm using now) has these tools that Kytchen should match:
- `load_context` / `peek_context` / `search_context` ✅ (has)
- `exec_python` / `get_variable` ✅ (has)
- `run_command` / `read_file` / `write_file` ✅ (has with --enable-actions)
- `run_tests` ✅ (has)
- `think` / `finalize` / `evaluate_progress` ✅ (has)
- Remote server orchestration ✅ (has)
- Recipe/workflow system ✅ (has)

**Missing from Kytchen that Aleph has**:
- Git-specific tools (git diff, git status, git log)
- Database query tools
- Dialectical reasoning (thesis/antithesis/synthesis)

### 4. Add Kytchen to User's Claude Code

Currently Kytchen MCP is only in project configs. Add to user scope:
```bash
claude mcp add kytchen --scope user \
  -- /opt/homebrew/bin/python3 -m kytchen.mcp.local_server --enable-actions
```

Or manually add to `~/.claude.json`:
```json
{
  "mcpServers": {
    "kytchen": {
      "command": "/opt/homebrew/bin/python3",
      "args": ["-m", "kytchen.mcp.local_server", "--enable-actions"],
      "env": {
        "PYTHONPATH": "/Volumes/VIXinSSD/kytchen"
      }
    }
  }
}
```

## Tasks for Next Session

### Priority 1: Make Kytchen MCP Connect
1. Run `claude mcp list` to check status
2. If fails, debug why `local_server.py` isn't starting
3. Ensure MCP SDK is installed: `pip install 'kytchen[mcp]'`

### Priority 2: Test Kytchen Tools
Once connected, test these tools work:
- `load_context` - Load a file as context
- `exec_python` - Execute Python code
- `read_file` / `write_file` - File operations
- `run_command` - Shell commands

### Priority 3: Add Git Tools
Add git-specific tools to `local_server.py`:
- `git_diff` - Show diff
- `git_status` - Show status
- `git_log` - Show recent commits
- `git_blame` - Blame a file

### Priority 4: Dogfood the Product
Use Kytchen MCP in this session to:
1. Load the codebase as context
2. Use exec_python to analyze code
3. Use the recipe system for reproducible analysis

## Key Files to Read

1. `/Volumes/VIXinSSD/kytchen/kytchen/mcp/local_server.py` - Main MCP server (38 tools)
2. `/Volumes/VIXinSSD/kytchen/kytchen/sandbox/e2b.py` - E2B integration
3. `/Volumes/VIXinSSD/kytchen/.mcp.json` - Claude Code MCP config
4. `/Volumes/VIXinSSD/kytchen/CLAUDE.md` - Project instructions

## Environment Setup

```bash
# Install Kytchen with MCP support
cd /Volumes/VIXinSSD/kytchen
pip install -e '.[mcp]'

# Optional: Enable E2B (for production sandboxing)
export E2B_API_KEY=your_api_key

# Test the server
python -m kytchen.mcp.local_server --help
```

## Linear Issues

- SHA-113: Stripe billing integration (done)
- SHA-117: Line management (E2B integration) - In backlog
- SHA-118: Landing page with positioning - In backlog

## Multi-Agent Setup

### Jules CLI (Google's Coding Agent)
```bash
# Already installed globally
jules --version

# Login (OAuth)
jules login

# Delegate menial tasks
jules new "write unit tests for component X"
jules new --repo owner/repo "fix all ESLint warnings"

# Check sessions
jules remote list --session

# Pull results
jules remote pull --session <id> --apply
```

### E2B Sandbox (Now in Vercel)
```bash
# Added to all Vercel environments
E2B_API_KEY=e2b_4c2d88de01f88a0598465c4595e4e7f1e62c209b
```

### Workflow: Claude + Jules
1. **Claude** handles complex reasoning, architecture, planning
2. **Jules** handles menial tasks (tests, bug fixes, dependency updates)
3. **Kytchen MCP** handles context exploration, code execution

See: `/Volumes/VIXinSSD/kytchen/docs/AGENT_WORKFLOW.md`

## Success Criteria

1. `claude mcp list` shows `kytchen: ✓ Connected`
2. Can use Kytchen tools in Claude Code conversation
3. Kytchen MCP is as capable as Aleph for coding tasks
4. E2B sandboxing works for production use cases
5. Can delegate tasks to Jules and merge results
