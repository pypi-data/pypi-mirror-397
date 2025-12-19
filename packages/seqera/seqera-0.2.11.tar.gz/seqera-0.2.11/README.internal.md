# Seqera AI CLI - Internal Documentation

Internal development documentation for the Seqera AI CLI.

## Quick Start

The CLI provides two main commands:

- **`seqera`** - Main CLI command that shows a landing screen and provides authentication commands
- **`seqera ai`** - AI assistant command that starts the interactive AI-powered terminal experience

```bash
# Show landing screen
seqera

# Start the AI assistant
seqera ai

# Authenticate (required before using AI assistant)
seqera login
```

## Installation

### Install from PyPI (when published)

```bash
pipx install seqera-ai
# or: pip install --user seqera-ai
```

### Install from source (recommended for development)

```bash
# Install pipenv if you don't have it
pip install --user pipenv

# Install dependencies and the package
pipenv install -e .

# Activate the virtual environment
pipenv shell

# Run the CLI
seqera              # shows landing screen
seqera login         # first-time Auth0 login (opens browser by default)
seqera ai            # launches the interactive AI assistant
```

### Build wheel for distribution

```bash
pipenv install --dev build
pipenv run python -m build
# produces dist/seqera_ai-0.1.0-py3-none-any.whl and .tar.gz
```

## Usage

The CLI provides two main commands:

- **`seqera`** - Main CLI command (shows landing screen)
- **`seqera ai`** - AI assistant command (starts the interactive experience)

```bash
# Show landing screen
seqera

# Authenticate once (stores refresh token securely)
seqera login

# Interactive mode (default)
seqera ai

# With legacy token override (optional; useful for CI)
seqera ai --token YOUR_TOKEN

# Single query
seqera ai "List my running workflows"

# With working directory
seqera ai -w /path/to/pipeline

# Show help
seqera --help
seqera ai --help
```

### Authentication

The CLI authenticates directly with Auth0 (Authorization Code + PKCE) and stores refresh tokens in your OS keychain:

```bash
# Opens a browser window pointing at Auth0
seqera login

# Headless fallback using Auth0's device-code flow
seqera login --device

# Inspect the cached credentials
seqera status

# Revoke the refresh token(s)
seqera logout
seqera logout --all   # wipe every stored profile
```

Configuration lives in `services/cli/.env`:

```ini
SEQERA_AUTH0_DOMAIN=seqera-development.eu.auth0.com
SEQERA_AUTH0_AUDIENCE=platform
SEQERA_AUTH0_CLI_CLIENT_ID=<native client id>
SEQERA_AUTH0_REDIRECT_PORT=53682   # must be an allowed loopback port
SEQERA_AI_BACKEND_URL=http://localhost:8002
```

The CLI hits Auth0 and Platform APIs directly, so no browser-only proxy (like `services/website/devProxy.mjs`) is required for local development. If you need to pass a pre-existing Platform token (for example in CI), you can use the `--token` flag, but the Auth0 flow is the recommended default.

### Command-Line Options

Primary commands:

- `seqera` - Main CLI command (shows landing screen)
- `seqera logout [--all]` - Sign out and remove credentials
- `seqera status` - Show authentication status
- `seqera ai [options]` - Start the AI assistant

```bash
seqera ai options:
  -t, --token TEXT         Legacy Seqera Platform access token override
  -b, --backend TEXT       Backend server URL (default: http://localhost:8002)
  -i, --interactive        Start interactive chat mode (default: true)
  -v, --verbose            Enable verbose output with tool execution details
  -a, --approval-mode [basic|default|full]
                           Approval mode for local command execution (default: 'default')
  -w, --workdir DIRECTORY  Working directory for agent operations (default: current directory)
  --help                   Show this message and exit
```

### Approval Modes

Local commands suggested by the AI go through an approval check before running:

| Mode      | Behavior                                                                                                                                            |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `basic`   | Only safe-list commands run automatically; everything else prompts for approval                                                                     |
| `default` | Safe-list commands and file edits within the current workdir run automatically; dangerous commands or edits outside the workdir prompt for approval |
| `full`    | Everything runs automatically unless the command is on the dangerous list                                                                           |

**Changing the mode:**

- On startup: Use `--approval-mode` flag (e.g., `seqera ai --approval-mode basic`)
- In-session: Type `/approval` to open an interactive selector (use arrow keys to navigate, Enter to confirm)
- Quick change: `/approval basic` or `/approval full` to set directly

**When approval is required:**

```
⚠ Approval required (basic mode)
Reason: basic_mode_requires_approval

  echo "Hello world"

  1 Yes, run this command
  2 No, cancel and stop

Select [1/2]:
```

- Press **1** to approve and run the command
- Press **2** to deny and interrupt the current session

### Reserved Commands

The CLI includes special commands that work in both single-query and interactive mode:

```bash
/                           Show available commands
/approval                   Show or set local approval mode
/feedback                   Get link to provide feedback about Seqera AI
/help-community             Get community support
/stickers                   Open Seqera stickers store on Sticker Mule
/schema                     Generate Nextflow schema
/debug                      Run pipeline diagnostics
/migrate-from-wdl           Migrate from WDL to Nextflow
/migrate-from-snakemake     Migrate from Snakemake to Nextflow
/write-nf-test              Write nf-tests for untested code
/debug-last-run             Debug last local run
/debug-last-run-on-seqera   Debug last Seqera Platform run
/clear                      Clear the conversation history
/history                    List the conversation history
```

### Keyboard Shortcuts

When using interactive mode with `prompt_toolkit` (default), the following keyboard shortcuts are available:

- **Ctrl+U**: Clear the current input line
- **Ctrl+C**: Exit the CLI
- **Enter**: Submit your message

### Examples

**Seqera Workflows:**

```bash
seqera ai "Show me all running workflows"
seqera ai "Get details for workflow 12345"
seqera ai "Launch nf-core/rnaseq pipeline"
```

**Pipeline Management:**

```bash
seqera ai "List available nf-core pipelines"
seqera ai "Show me details about nf-core/rnaseq"
```

**Organization & Workspaces:**

```bash
seqera ai "Show my organizations"
seqera ai "List workspaces in organization 123"
```

**Reserved Commands:**

```bash
seqera ai "/debug" -w /path/to/pipeline
seqera ai "/schema" -w /path/to/pipeline
```

**Interactive Session:**

```bash
$ seqera ai

You: What workflows are running?
🤖 Assistant: [Lists your running workflows]

You: Show me details of the latest one
🤖 Assistant: [Provides detailed information]

You: Can you check if there are any errors in the logs?
🤖 Assistant: [Analyzes logs and reports findings]

You: /debug
🤖 Assistant: [Runs diagnostics on the current working directory]
```

## Architecture

This is a **client-server application** with local execution capabilities:

- **Backend Server**: Runs Claude Agent SDK with Seqera MCP integration and local execution proxy
- **CLI Client**: Lightweight client that executes commands locally (Authenticates via Auth0 and never stores Anthropic keys)

```
┌─────────────────────────────────────────────────────────┐
│  User's Machine                                          │
│  ┌──────────────┐                                       │
│  │  CLI Client  │ • No AI token needed                  │
│  │              │ • Executes bash/file ops locally      │
│  └──────────────┘                                       │
└────────┬─────────────────────────────────────────────────┘
         │ WebSocket (queries & results)
         ▼
┌─────────────────────────────────────────────────────────┐
│  Backend Server (Docker/Cloud)                           │
│  ┌───────────────────────────────────────┐             │
│  │  Claude Agent SDK                      │             │
│  │  ┌──────────────┐  ┌──────────────┐  │             │
│  │  │ MCP Proxy    │  │ Seqera MCP   │  │             │
│  │  │ (local ops)  │  │ (platform)   │  │             │
│  │  └──────┬───────┘  └──────┬───────┘  │             │
│  │         │                  │           │             │
│  └─────────┼──────────────────┼───────────┘             │
│            │                  │                          │
│      Callbacks to CLI   HTTPS to Platform               │
└────────────┼──────────────────┼───────────────────────────┘
             ▲                  ▼
        User's Machine   ┌──────────────┐
                         │   Seqera     │
                         │   Platform   │
                         └──────────────┘
```

**Key Features:**

- **No AI token on client**: Anthropic API key only on backend
- **Local execution**: Bash and file operations run on user's machine
- **Dual MCP architecture**: Local operations via proxy, platform operations via Seqera MCP
- **Enterprise-ready**: Centralized AI key management, works with remote backends

## Features

- 🤖 **AI-Powered Agent**: Leverages Claude's Agent SDK with advanced reasoning capabilities
- 🔧 **Built-in Tools**: Full access to bash, file operations, web search, and more
- 📋 **Task Planning**: Automatic task decomposition and planning for complex operations
- 🧬 **Seqera Integration**: Native support for Seqera Platform workflows, pipelines, and data management
- 💬 **Interactive Chat**: Conversational interface for iterative problem-solving
- 🎨 **Rich Output**: Beautiful terminal UI with progress indicators and syntax highlighting
- 🔒 **Simple Authentication**: Auth0 login with secure refresh-token storage (OS keychain)

## Available Tools

### Local Execution Tools (via MCP Proxy)

Commands run on **your local machine** in the directory where you launched the CLI:

- **execute_bash_local**: Run shell commands locally (ls, cat, grep, nextflow, etc.)
- **read_file_local**: Read files from your local filesystem
- **list_directory_local**: List local directory contents

**How it works:** Backend AI sends commands to CLI via WebSocket → CLI executes locally → results flow back to AI

### Platform Tools (via Seqera MCP)

The backend integrates with **Seqera MCP** (`https://mcp.seqera.io/mcp`) providing **74+ tools**:

**Container & Package Tools:**

- `wave_claim_container` - Create Docker/Singularity containers with conda packages
- `seqerahub_search_conda` - Search Conda packages
- `seqerahub_search_pypi` - Search Python packages
- `seqerahub_search_packages` - General package search

**Platform Tools** (require Auth0-issued Platform bearer tokens managed by `seqera login`):

- **Workflow Management**: List, launch, monitor, cancel workflows; view logs and metrics
- **Pipeline Operations**: Access nf-core and custom pipelines; manage configurations
- **Data Management**: Datasets, data links, pre-signed URLs, file operations
- **Compute Environments**: Configure AWS, GCP, Azure, on-premises clusters
- **Organization & Workspaces**: Manage teams, members, and workspaces
- **Studios**: Cloud IDE operations and session management
- **Credentials**: Secrets and authentication management
- **Labels & Tokens**: Resource tagging and API token management

## Prerequisites

- Python 3.13 or later
- Auth0 native client credentials (domain + client ID) and the ability to sign in to Seqera Platform
- Access to a running backend server (see [CLAUDE.md](CLAUDE.md))

## Troubleshooting

### Backend Connection Issues

**"Backend server is not responding!"**

- Ensure backend is running and accessible
- Check backend URL with `-b` flag or `SEQERA_AI_BACKEND_URL` environment variable
- Verify firewall/network settings

### Authentication Issues

**"No CLI login found" / "Unable to obtain a Seqera Platform token"**

- Run `seqera login` (or `seqera login --device` on headless machines)
- Confirm `SEQERA_AUTH0_DOMAIN`, `SEQERA_AUTH0_AUDIENCE`, and `SEQERA_AUTH0_CLI_CLIENT_ID` are set
- For CI/automated testing, pass tokens via `--token` flag

### Connection Errors

The CLI includes automatic retry logic for transient connection issues:

- **Automatic retry**: Failed queries retry up to 3 times with exponential backoff (1s, 2s, 4s)
- **Transparent reconnection**: Stale connections are automatically refreshed
- **Auth error recovery**: Token validation failures trigger automatic retry

If you still experience issues:

- Check that backend is accessible
- Verify WebSocket connections are allowed
- Check for proxy/firewall issues
- Use `-v` flag to see detailed connection messages

## Security

- **Client**: Authenticates with Auth0 (Authorization Code + PKCE) and stores refresh tokens in the OS keychain
- **Backend**: Anthropic API key stored securely in backend `.env` file
- **Seqera Authentication**: Bearer tokens issued by Auth0; no Tower cookies or secrets on the CLI
- **Session Isolation**: Each user gets their own isolated session
- **Auto-cleanup**: Sessions automatically expire after 2 hours of inactivity

## Testing

### Automated Resilience Tests

Before submitting PRs that modify connection or retry logic, run the resilience test suite:

```bash
cd services/cli
pipenv shell
./tests/test_cli_resilience.sh
```

**Prerequisites:**

- Backend running: `docker compose up api-assistant`
- User authenticated: `seqera login`

**What it tests:**

- Basic connectivity and response handling
- Verbose mode output (`-v` flag)
- Connection reuse across queries
- Retry logic with exponential backoff
- Error message quality
- Ctrl+C interrupt handling
- Security (no token leakage)
- MCP local execution (bash commands, file read, directory list)
- Multi-step tool flows
- Seqera Platform MCP (workspaces, pipelines)
- Response time baseline

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development instructions including:

- Backend server setup
- Architecture details
- Session management
- Adding reserved commands
- MCP integration

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Apache-2.0 License - see LICENSE file for details

## Links

- Seqera Platform: https://seqera.io
- Claude Documentation: https://docs.anthropic.com
- Issues: https://github.com/seqera-labs/seqera-ai/issues
