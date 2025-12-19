#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_DIR="$SCRIPT_DIR"
DIST_DIR="$CLI_DIR/dist"

declare -a STEPS=()
declare -a PIPENV_PYTHON_ARGS=()
PYTHON_BIN=""
SHOW_USAGE=false

export PIPENV_NOSPIN=1
export PIPENV_VERBOSITY="${PIPENV_VERBOSITY:--1}"

usage() {
  cat <<'EOF'


🟢 Commands:

  setup                 # Install pipenv dependencies in editable mode (pipenv install -e .)
  package               # Install build tooling and produce wheel + sdist (pipenv run python -m build)
  verify                # Install the latest dist/*.whl in a temporary Pipenv env and run smoke tests
  start                 # Ensure setup is complete, then run seqera ai


🟢 Development:

  ./dev.sh setup    
  pipenv shell
  seqera login


🟢 Build / verify:

  ./dev.sh package   
  ./dev.sh verify


Optional flags:

  --python [value]      # e.g. python3.13 or /usr/bin/python3
  -h, --help            # Show this message


🟢 Examples:

  ./dev.sh setup        # Ensure pipenv, copy .env if missing, run setup
  ./dev.sh package      # Build fresh artifacts
  ./dev.sh verify       # Verify the built package (wheel)
  ./dev.sh start        # Run seqera ai (runs setup if needed)

EOF
}

info()    { printf "\033[1;34m\033[0m %s\n" "$*"; }
success() { printf "\033[1;32m🟢\033[0m %s\n" "$*"; }
warn()    { printf "\033[1;33m🟡\033[0m %s\n" "$*"; }
error()   { printf "\033[1;31m🔴 %s\033[0m\n" "$*" >&2; exit 1; }

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

ensure_pipenv() {
  if command_exists pipenv; then
    info "✓ pipenv already installed"
    return
  fi

  warn "pipenv not found; attempting installation via python3 -m pip --user"
  if ! command_exists python3; then
    error "python3 is required to bootstrap pipenv. Please install Python 3.13+."
  fi

  python3 -m pip install --user pipenv || error "pipenv installation failed"

  if ! command_exists pipenv; then
    warn "pipenv still not on PATH; ensure your user base bin directory is exported, then re-run."
    exit 1
  fi

  success "pipenv installed"
}

ensure_dotenv() {
  local env_file="$CLI_DIR/.env"
  local example_file="$CLI_DIR/.env.example"

  if [[ -f "$env_file" ]]; then
    info "✓ .env already present"
    return
  fi

  [[ -f "$example_file" ]] || error "Missing .env.example template"

  cp "$example_file" "$env_file"
  success "Created .env from .env.example (edit it with your values)"
}

validate_python_version() {
  [[ -n "$PYTHON_BIN" ]] || return 0

  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    error "Python interpreter '$PYTHON_BIN' not found on PATH"
  fi

  if ! "$PYTHON_BIN" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 13) else 1)'; then
    local detected_version
    detected_version="$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
    error "Python interpreter '$PYTHON_BIN' is ${detected_version}; requires >= 3.13"
  fi
}

choose_default_python() {
  # If user explicitly provided --python, respect that.
  if [[ -n "$PYTHON_BIN" ]]; then
    return 0
  fi

  # "Hardcode" our default to python3.13 – this is the version the package requires.
  PYTHON_BIN="python3.13"
}

pipenv_install_quiet() {
  local cmd=(pipenv)
  # Prefer an explicit interpreter if we have one
  if [[ -n "$PYTHON_BIN" ]]; then
    cmd+=(--python "$PYTHON_BIN")
  elif [[ ${#PIPENV_PYTHON_ARGS[@]} -gt 0 ]]; then
    cmd+=("${PIPENV_PYTHON_ARGS[@]}")
  fi
  cmd+=("install")
  "${cmd[@]}" "$@"
}

step_setup() {
  info "Installing editable dependencies (pipenv install -e .)"
  pushd "$CLI_DIR" >/dev/null
  pipenv_install_quiet -e .
  popd >/dev/null
  info ""
  success "Dev CLI ready (changes are reflected without rebuilding)"
  info ""
}

step_package() {
  info "Installing build tooling (pipenv install --dev build)"
  pushd "$CLI_DIR" >/dev/null
  pipenv_install_quiet --dev build
  info "Building wheel and source distribution"
  pipenv run python -m build
  popd >/dev/null
  info ""
  success "Built successfully"
  info ""
}

step_verify() {
  [[ -d "$DIST_DIR" ]] || error "dist/ directory not found. Run ./dev.sh package first."
  local wheel
  wheel="$(ls -t "$DIST_DIR"/seqera_ai-*.whl 2>/dev/null | head -n1 || true)"
  [[ -f "$wheel" ]] || error "No wheel found in dist/. Run ./dev.sh package first."

  local tmp_dir
  tmp_dir="$(mktemp -d -t seqera-ai-wheel-test-XXXXXX)"
  info "Creating temporary Pipenv environment in $tmp_dir"

  pushd "$tmp_dir" >/dev/null
  pipenv_install_quiet "$wheel"
  info "Running CLI smoke tests"
  pipenv run seqera --help >/dev/null
  pipenv run seqera ai --help >/dev/null
  popd >/dev/null

  rm -rf "$tmp_dir"
  info "✓ Package verified in temporary environment"
  info ""
  success "Try out the CLI:"
  info ""
  info "  pipenv run seqera ai           # Try the CLI"
  info "  pipenv shell                   # Start the environment"
  info "  seqera ai                       # Try the CLI"
  info ""
}

step_start() {
  # Check if Pipfile.lock exists to determine if setup has been run
  if [[ ! -f "$CLI_DIR/Pipfile.lock" ]]; then
    info "Pipfile.lock not found. Running setup first..."
    step_setup
  else
    info "✓ Setup already complete (Pipfile.lock found)"
  fi

  info ""
  success "Starting seqera ai CLI..."
  info ""
  
  # Run seqera ai in the pipenv environment
  pushd "$CLI_DIR" >/dev/null
  pipenv run seqera ai
  popd >/dev/null
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      setup|package|verify|start)
        STEPS+=("$1")
        ;;
      --python)
        shift || error "Missing value for --python"
        PYTHON_BIN="$1"
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        error "Unknown argument: $1"
        ;;
    esac
    shift
  done

  if [[ ${#STEPS[@]} -eq 0 ]]; then
    SHOW_USAGE=true
  fi

  if [[ -n "$PYTHON_BIN" ]]; then
    PIPENV_PYTHON_ARGS=(--python "$PYTHON_BIN")
  fi
}

main() {
  parse_args "$@"
  choose_default_python
  validate_python_version
  if "$SHOW_USAGE"; then
    usage
    exit 0
  fi
  ensure_pipenv
  ensure_dotenv

  for step in "${STEPS[@]}"; do
    case "$step" in
      setup) step_setup ;;
      package) step_package ;;
      verify) step_verify ;;
      start) step_start ;;
      *) error "Unhandled step: $step" ;;
    esac
  done

}

main "$@"

