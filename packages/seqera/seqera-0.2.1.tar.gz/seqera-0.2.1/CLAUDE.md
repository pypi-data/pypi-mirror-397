# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Seqera AI CLI is a lightweight command-line client that connects to a backend server running Claude Agent SDK with integrated Seqera MCP support. This CLI provides an AI-powered terminal interface for bioinformatics and workflow management.

Repository: https://github.com/seqera-labs/seqera-ai

**Architecture**: Client-only repository that connects to a backend server running Claude Agent SDK. The backend uses:

- **MCP Proxy**: In-process MCP server for local execution (bash, file ops) via WebSocket callbacks
- **Seqera MCP**: Remote MCP server for Seqera Platform operations
- **No local AI token required**: Anthropic API key only on backend (enterprise-ready)

## Development Setup

### Install with pipenv (recommended)

```bash
# Install pipenv if needed
pip install --user pipenv

# Install dependencies and package in editable mode
pipenv install -e .

# Activate the environment
pipenv shell

# Run the CLI
seqera --help
seqera ai  # launches interactive mode
```

### Build for distribution

```bash
# Install build tool
pipenv install --dev build

# Build wheel and source distribution
pipenv run python -m build
# Produces: dist/seqera_ai-0.1.0-py3-none-any.whl and .tar.gz
```

### Test the built wheel

```bash
# Install and test the wheel in a new environment
pipenv --python 3.13 install dist/seqera_ai-0.1.0-py3-none-any.whl
pipenv run seqera ai
```

## Project Structure

```
src/seqera_ai/
├── __init__.py      # Package version (__version__ = "0.1.0")
├── __main__.py      # Entry point for `python -m seqera_ai`
└── cli.py           # Main CLI implementation (700+ lines)

.env.example         # Environment variable template (copy to .env)
```

**Entry point**: The `seqera` console script (defined in pyproject.toml) routes to `seqera_ai.cli:cli_seqera()`, with `ai` as a subcommand

## Key Architecture Components

### CLI Client (src/seqera_ai/cli.py)

**SeqeraClient class (lines 155-466)**:

- WebSocket-based communication with backend
- Streaming response handler with live terminal updates
- Session management (session_id persisted across queries)
- Health checks before connecting

**Communication Protocol**:

- Client sends: `{query, seqera_token, session_id?, verbose?, cwd?, local_mcp_command}`
- Server streams: `{type: "session"|"text"|"thinking"|"tool_use"|"tool_result"|"complete"|"error", ...}`
- For local execution: Server sends `{type: "execute_local", command, request_id}` → Client executes → Client returns `{type: "execute_local_result", result, request_id}`

**Display System**:

- Uses Rich library's `Live` for dynamic terminal updates
- Different panel styles for different message types:
  - Text: Blue panel "🧬 Seqera AI"
  - Tool Use: Magenta panel "🔧 Tool • {name}"
  - Tool Result: Green/red panel "📦 Tool Result"
  - TodoWrite: Special formatting with status icons (⭕ pending, 🔄 in_progress, ✅ completed)

### Reserved Commands (lines 29-153)

Built-in shortcuts for common bioinformatics workflows:

- `/schema` - Generate Nextflow schema.json
- `/debug` - Run pipeline diagnostics (nextflow lint, run -help)
- `/migrate-from-wdl` - WDL to Nextflow migration
- `/migrate-from-snakemake` - Snakemake to Nextflow migration
- `/write-nf-test` - Generate nf-tests for untested code
- `/debug-last-run` - Debug last local Nextflow run
- `/debug-last-run-on-seqera` - Debug last Seqera Platform run
- `/help` - Show available commands

**Implementation**: Commands are transformed into detailed prompts for the backend agent in `handle_reserved_command()` function.

### Command Structure

The CLI uses Click framework with a group/command pattern:

```bash
seqera                # Root group (shows landing screen)
  ├── login           # Auth0 authentication
  ├── logout          # Sign out
  ├── status          # Show auth status
  └── ai              # AI assistant (launches interactive experience)
```

**Main command options**:

- `query` (argument): Optional query for single-query mode
- `-t, --token`: Seqera Platform access token
- `-b, --backend`: Backend server URL (default: http://localhost:8002)
- `-i, --interactive`: Interactive mode flag (default: True)
- `-v, --verbose`: Enable verbose output with tool details
- `-w, --workdir`: Working directory for agent operations

## Usage Patterns

### Interactive Mode (default)

```bash
seqera ai
# Prompts for token if not set
# Shows banner and available commands
# Enters conversational loop
```

### Single Query Mode

```bash
seqera ai "List my running workflows" --token YOUR_TOKEN
```

### With Working Directory

```bash
seqera ai -w /path/to/pipeline --token YOUR_TOKEN
# Backend agent will operate in this directory for file operations
```

## Environment Variables

The CLI uses `python-dotenv` to automatically load environment variables from a `.env` file:

```bash
# Create your .env file from the template
cp .env.example .env

# Edit .env and set your values:
SEQERA_AUTH0_DOMAIN        # Auth0 domain (e.g., seqera-development.eu.auth0.com)
SEQERA_AUTH0_AUDIENCE      # API audience ("platform")
SEQERA_AUTH0_CLI_CLIENT_ID # Native client ID registered in Auth0
SEQERA_AUTH0_REDIRECT_PORT # Loopback port allowed in Auth0 (default 53682)
SEQERA_AI_BACKEND_URL      # Backend server URL (default: http://localhost:8002)
```

The `.env` file is ignored by git for security, but `.env.example` provides a template with documentation.

## Common Development Tasks

### Adding a New Reserved Command

1. Add entry to `RESERVED_COMMANDS` dict (line 29):

```python
RESERVED_COMMANDS = {
    "/my-command": "Description of what this command does",
    ...
}
```

2. Add handler in `handle_reserved_command()` function (line 51):

```python
if cmd == "/my-command":
    query = "Detailed prompt for the agent describing what to do..."
    if args:
        query += f" Additional context: {args}"
    console.print(f"[bold cyan]Starting my command...[/bold cyan]\n")
    client.send_query_streaming(query)
    return True
```

### Modifying the Display System

The streaming display is in `send_query_streaming()` (lines 187-466). Key areas:

- **Panel rendering**: Lines 262-330 (text panels)
- **Tool display**: Lines 288-335 (tool_use message type)
- **TodoWrite formatting**: Lines 300-316 (special handling for task lists)
- **Live updates**: Uses Rich's `Live` context manager with `Group` for multiple panels

### Changing Default Backend URL

Update line 531 in `get_backend_url()`:

```python
return os.getenv("SEQERA_AI_BACKEND_URL", "http://localhost:8002")
```

### Updating Package Version

Update version in two places:

1. `src/seqera_ai/__init__.py`: `__version__ = "0.1.0"`
2. `pyproject.toml`: `version = "0.1.0"`

## Backend Integration

This CLI is a **client-only** package. It requires a separate backend server running:

**Backend responsibilities**:

- Claude Agent SDK integration
- Seqera MCP connection (https://mcp.seqera.io/mcp)
- Session management (2-hour timeout per user)
- Tool execution (Bash, Edit, Read, Write, Grep, Glob, WebFetch, WebSearch, TodoWrite)
- MCP tools (74+ Seqera Platform tools)

**Health check endpoint**: `GET {backend_url}/cli-agent/health`

**WebSocket endpoint**: `WS {backend_url}/cli-agent/ws/query`

## Seqera MCP Tools Available

Through the backend's MCP integration, users can access 74+ tools:

**Container & Package Tools**:

- `wave_claim_container` - Create Docker/Singularity containers
- `seqerahub_search_*` - Search Conda, PyPI, and packages

**Platform Tools** (require TOWER_ACCESS_TOKEN):

- Workflow management (list, launch, monitor, cancel, logs, metrics)
- Pipeline operations (nf-core, custom pipelines)
- Data management (datasets, data links, file operations)
- Compute environments (AWS, GCP, Azure, on-premises)
- Organization & workspace management
- Studios (cloud IDE sessions)
- Credentials and secrets management

## Dependencies

From `pyproject.toml`:

```python
requires-python = ">=3.13"
dependencies = [
    "click>=8.1.3",           # CLI framework
    "rich>=13.7.0",           # Terminal UI
    "python-dotenv>=1.0.0",   # Environment variables
    "websocket-client>=1.7.0", # WebSocket communication
    "requests>=2.32.0",       # HTTP requests (health checks)
    "keyring>=24.3.0"         # Secure refresh-token storage
]
```

## Troubleshooting

### Backend Connection Issues

If you see "Backend server is not responding!":

1. Verify backend is running and accessible
2. Check backend URL: `seqera ai -b http://your-backend:port`
3. Test health endpoint: `curl http://localhost:8002/cli-agent/health`
4. Check firewall/network settings

### Authentication Issues

If you see "Unable to obtain a Seqera Platform token":

1. Run `seqera login` (or `seqera login --device` on headless hosts)
2. Ensure `SEQERA_AUTH0_DOMAIN`, `SEQERA_AUTH0_AUDIENCE`, and `SEQERA_AUTH0_CLI_CLIENT_ID` are set
3. For CI or automated testing, use `--token` flag with a valid token

### WebSocket Timeout

If you see "No response from backend (timeout after 30s)":

- Backend may be processing but not streaming updates
- Check backend logs for errors
- Verify WebSocket connections are allowed through firewalls/proxies

### Pipenv Environment Issues

If modules aren't found after installation:

```bash
# Remove and recreate environment
rm -rf ~/.local/share/virtualenvs/seqera_ai_cli_v2-*
pipenv --rm
pipenv install -e .
```

## Testing

Currently no automated tests. Manual testing workflow:

1. Install in editable mode: `pipenv install -e .`
2. Start backend server (separate repository)
3. Test health: `curl http://localhost:8002/cli-agent/health`
4. Authenticate once: `pipenv run seqera login`
5. Test CLI: `pipenv run seqera ai`
6. Try reserved commands: `/help`, `/schema`, etc.
7. Test interactive mode with various queries
