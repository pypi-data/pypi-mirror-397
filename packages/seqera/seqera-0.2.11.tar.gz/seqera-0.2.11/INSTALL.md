# Installation & Build Guide

A Python “wheel” (`.whl`) is the packaged artifact that `pip install` consumes. The commands below show how to develop locally, build the wheel, and verify that the artifact installs cleanly.

Before starting ensure that our Intern and DB services are running locally if desired, and our `.env` is correctly pointing to the them (i.e. `http://localhost:8002`, or `https://intern.dev-seqera.io`)

## Local development

### Option 1: Using `dev.sh`

You can use the dev script to automate the setup, for example:

```bash
cd services/cli    # Navigate to CLI root
./dev.sh           # Show available commands
./dev.sh setup     # Setup dev environment
pipenv shell       # Start the shell
seqera login    # Use the CLI
# Changes are reflected automatically
```

### Option 2: Manually

```bash
# Install pipenv if needed
pip install --user pipenv

# Install dependencies and package in editable mode
pipenv install -e .

# Activate the environment
pipenv shell

# Configure environment (optional)
cp .env.example .env
# Edit .env to add Auth0 config + backend URL (SEQERA_AUTH0_* + SEQERA_AI_BACKEND_URL)

# Run the CLI
seqera --help
seqera ai
```

## Packaging

### Using `dev.sh`

```bash
cd services/cli
./dev.sh setup                    # Do initial setup
./dev.sh package                  # Builds wheel under /dist
./dev.sh verify                   # Verify the build
./dev.sh setup package verify     # Run everything end-to-end
```

### Build the wheel (package)

```bash
# Install build tool
pipenv install --dev build

# Build wheel and source distribution
pipenv run python -m build
# produces dist/seqera_ai-0.1.0-py3-none-any.whl and .tar.gz
```

> Shortcut: `./dev.sh package` runs the same sequence for you.

### Verify the built wheel

```bash
# Create a new pipenv environment and install the wheel
pipenv --python 3.13 install dist/seqera_ai-0.1.0-py3-none-any.whl
pipenv run seqera --help
pipenv run seqera ai
```

> Shortcut: `./dev.sh verify` spins up a temporary Pipenv environment and runs the smoke tests automatically.

## Project Structure

```
seqera-ai/
├── pyproject.toml          # Build config + dependencies (Hatchling)
├── README.md               # User-facing documentation
├── LICENSE                 # Apache-2.0 license
├── CLAUDE.md              # Development/architecture docs
└── src/
    └── seqera_ai/
        ├── __init__.py     # Package version
        ├── __main__.py     # Entry point for `python -m seqera_ai`
        └── cli.py          # Main CLI logic
```

## Console Command

The package creates a `seqera` command that routes to `seqera_ai.cli:cli_seqera()`, with `ai` as a subcommand:

```bash
seqera --help              # Show help
seqera login               # Auth0 login (stores refresh token securely)
seqera ai                  # Launch interactive mode (default)
seqera ai "query"          # Single query
seqera ai -t TOKEN         # With manual token override (optional)
seqera ai -w /path         # With working directory
```

## Publishing (Future)

When ready to publish to PyPI:

```bash
# Build
python -m build

# Upload to PyPI (requires twine and credentials)
python -m pip install --upgrade twine
python -m twine upload dist/*
```

Then users can install with:

```bash
pipx install seqera-ai
# or
pip install seqera-ai
```

## Development Workflow

### Editable install for development

```bash
# Clone the repo
git clone https://github.com/seqera-labs/seqera-ai.git
cd seqera-ai

# Install in editable mode with pipenv
pipenv install -e .

# Make changes to src/seqera_ai/cli.py

# Test immediately (no rebuild needed)
pipenv run seqera ai
```

### Running without pipenv shell

```bash
# Run directly without activating shell
pipenv run seqera ai

# Or perform Auth0 login inside the pipenv environment (first run)
pipenv run seqera login
```

## Environment Configuration

The CLI supports configuration via `.env` file. Copy `.env.example` and edit the Auth0 + backend values:

```bash
SEQERA_AUTH0_DOMAIN=seqera-development.eu.auth0.com
SEQERA_AUTH0_AUDIENCE=platform
SEQERA_AUTH0_CLI_CLIENT_ID=<native client id from Auth0>
SEQERA_AUTH0_REDIRECT_PORT=53682        # loopback port registered in Auth0
SEQERA_AI_BACKEND_URL=http://localhost:8002
```

The CLI loads `.env` automatically via python-dotenv. For CI or automated testing, pass a Platform token via the `--token` flag when running `seqera ai`.

## Default Backend URL

The CLI defaults to `http://localhost:8002` for the backend server.
To override, use (in order of precedence):

1. `--backend URL` flag
2. `.env` file with `SEQERA_AI_BACKEND_URL=URL`
3. `SEQERA_AI_BACKEND_URL` environment variable

See CLAUDE.md for backend server setup.
