# Multi-Agent Coding Workflow

This document describes how to use Claude Code, Jules (Google), and the Kytchen MCP server together for efficient coding.

## Agent Roles

| Agent | Best For | Model |
|-------|----------|-------|
| **Claude Code** | Complex reasoning, architecture, code review, planning | Claude Opus 4.5 |
| **Jules** | Menial tasks, bug fixes, version updates, test writing | Gemini 3 Pro |
| **Kytchen MCP** | Context exploration, code execution, evidence collection | Local (API-free) |

## Setup

### 1. Jules CLI
```bash
# Install
npm install -g @google/jules

# Login (uses OAuth)
jules login

# Check status
jules --version
```

### 2. Kytchen MCP (already configured)
The Kytchen MCP server provides 38 tools for context exploration and code execution:
```bash
# Check connection
claude mcp list
# Should show: kytchen: ✓ Connected
```

### 3. E2B Sandbox (production)
```bash
# Set in .env
E2B_API_KEY=e2b_4c2d88de01f88a0598465c4595e4e7f1e62c209b
```

## Workflow Patterns

### Pattern 1: Claude Plans, Jules Executes

1. **Claude** analyzes the task and breaks it into subtasks
2. **Claude** identifies menial tasks (test writing, dependency updates, etc.)
3. **Claude** delegates to Jules:
   ```bash
   jules new "write unit tests for src/components/Button.tsx"
   ```
4. **Jules** works async, creates PR
5. **Claude** reviews and merges

### Pattern 2: Parallel Agents

```bash
# Start multiple Jules sessions for independent tasks
jules new --parallel 3 "fix all ESLint warnings"

# Meanwhile, Claude handles complex architecture work
```

### Pattern 3: Issue Triage

```bash
# Use Gemini to analyze issues, delegate to Jules
gh issue list --assignee @me --limit 10 --json title,body | \
  gemini -p "find the most tedious issue" | \
  jules new
```

## Jules Commands

```bash
# Create new task
jules new "task description"
jules new --repo owner/repo "task for specific repo"

# List sessions
jules remote list --session

# Get results
jules remote pull --session <id>
jules remote pull --session <id> --apply  # Apply patch locally

# Teleport to session (clone + checkout + apply)
jules teleport <session-id>

# Batch tasks from file
cat TODO.md | while IFS= read -r line; do jules new "$line"; done
```

## Kytchen MCP Tools

### Context Exploration
- `load_context` - Load file/data as context
- `peek_context` - View portion of context
- `search_context` - Regex search
- `chunk_context` - Split into chunks

### Code Execution
- `exec_python` - Run Python in sandbox
- `run_command` - Shell commands (with --enable-actions)
- `run_tests` - Run test suite

### File Operations
- `read_file` - Read files
- `write_file` - Write files

### Reasoning
- `think` - Structure reasoning step
- `evaluate_progress` - Self-evaluate
- `finalize` - Mark task complete

### Remote Orchestration
- `add_remote_server` - Register another MCP server
- `call_remote_tool` - Call tool on remote server

## Best Practices

### When to Use Claude
- Architecture decisions
- Complex refactoring
- Code review
- Security analysis
- Documentation writing

### When to Use Jules
- Writing tests
- Fixing linting errors
- Dependency updates
- Simple bug fixes
- Repetitive changes across files

### When to Use Kytchen MCP
- Large document analysis
- Code exploration
- Evidence collection
- Reproducible analysis runs

## Environment Variables

```bash
# .env
E2B_API_KEY=...          # Production sandbox
JULES_API_KEY=...        # Jules (if API access needed)
ANTHROPIC_API_KEY=...    # Claude (for sub-queries)
```

## Example Session

```
Human: Help me refactor the authentication system

Claude: I'll analyze the auth codebase using Kytchen MCP and plan the refactor.
[Uses mcp__kytchen__load_context to load auth files]
[Uses mcp__kytchen__search_context to find patterns]

Here's my plan:
1. [Complex] Redesign token refresh flow - I'll handle this
2. [Menial] Update all API routes to use new middleware - delegate to Jules
3. [Menial] Write tests for new auth flow - delegate to Jules

Let me delegate the menial tasks:
[Runs: jules new "update all API routes in src/api/ to use the new authMiddleware from src/middleware/auth.ts"]
[Runs: jules new "write comprehensive tests for src/middleware/auth.ts covering token refresh, expiry, and error cases"]

Now I'll focus on the complex token refresh redesign...
```

## Monitoring

```bash
# Check all active Jules sessions
jules remote list --session

# Check Kytchen MCP status
claude mcp list

# View Vercel env vars
vercel env ls
```
