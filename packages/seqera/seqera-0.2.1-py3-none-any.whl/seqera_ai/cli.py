#!/usr/bin/env python3
"""Seqera AI CLI client that authenticates via Auth0."""

import os
import sys
import time
import json
import logging
import subprocess
import re
from datetime import datetime
from typing import Callable, Optional
from pathlib import Path

import requests

import click

try:
    from prompt_toolkit.application import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.layout.containers import Window
    from prompt_toolkit.layout.controls import FormattedTextControl

    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False
from rich.console import Console, Group
from rich import box
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from dotenv import load_dotenv
import websocket

from .approval import (
    APPROVAL_MODE_CHOICES,
    APPROVAL_MODES,
    ApprovalDecision,
    ApprovalManager,
)

# Load .env if it exists (for backend URL and default token)
from seqera_ai.auth import AuthError, get_auth_manager
from seqera_ai import __version__

# Load .env if it exists (backend URL + Auth0 settings)
load_dotenv()

console = Console()


class SessionInterrupt(Exception):
    """Raised when user denies approval to interrupt the current session."""

    pass


logger = logging.getLogger(__name__)

# Configuration constants
MAX_TREE_ITEMS = 10
MAX_MAIN_NF_LINES = 500
MAX_MAIN_NF_CHARS = 5000
MAX_LINE_LENGTH = 500
MAX_DIRECTORY_ITEMS = 50
COMMAND_TIMEOUT = 30

# Human-readable rule summaries for each approval mode
APPROVAL_RULES = {
    "basic": "Only safe-list commands auto-run; everything else prompts for approval.",
    "default": "Safe-list commands and in-workspace file edits auto-run; dangerous commands or edits outside the workspace prompt for approval.",
    "full": "Everything auto-runs except commands on the dangerous list.",
}
# Compact display configuration
COMPACT_PREVIEW_LINES = 3  # Lines shown before truncation
COMPACT_MAX_LINE_LENGTH = 80  # Max chars per line in compact mode

# Reserved commands that can be used in the CLI
RESERVED_COMMANDS = {
    "/": "Show available commands",
    "/approval": "Show or set local approval mode (usage: /approval [basic|default|full])",
    "/config": "Generate a nextflow.config file for your pipeline",
    "/schema": "Generate a new Nextflow schema for your pipeline",
    "/debug": "Run nextflow lint and nextflow run -preview to check pipeline syntax",
    "/migrate-from-wdl": "Start an agent workflow to migrate from WDL to Nextflow",
    "/migrate-from-snakemake": "Start an agent workflow to migrate from Snakemake to Nextflow",
    "/convert-jupyter-notebook": "Convert a Jupyter Notebook to a Nextflow process",
    "/convert-r-script": "Convert an R script to a Nextflow process",
    "/convert-python-script": "Convert a Python script to a Nextflow process",
    "/write-nf-test": "Write nf-tests for untested portions of the codebase",
    "/debug-last-run": "Debug the last run on local",
    "/debug-last-run-on-seqera": "Debug the last run on Seqera Platform",
    "/feedback": "Get link to provide feedback about Seqera AI",
    "/help-community": "Get community support",
    "/stickers": "Open Seqera stickers store on Sticker Mule",
    "/credit": "Check your remaining Seqera AI credit balance",
    "/history": "Display conversation history",
}


def format_mcp_tool_name(tool_name: str) -> str:
    """
    Convert MCP tool names to friendly names by removing MCP prefixes.

    Examples:
        mcp__local-execution__write_file -> "Write"
        mcp__local-execution__read_file -> "Read"
        mcp__local-execution__edit_file -> "Edit"
        mcp__local-execution__run_command -> "Bash"
        mcp__seqera-mcp__search_nfcore_module -> "Search nf-core module"
        mcp__seqera-mcp__list_workflows -> "List workflows"

    Args:
        tool_name: Raw tool name that may contain MCP prefixes

    Returns:
        Friendly tool name with MCP prefixes removed and formatted
    """
    if not tool_name:
        return tool_name

    def _format_with_branding_preservation(text: str) -> str:
        """Format text with title case while preserving 'nf-core' as lowercase and 'API' as uppercase."""
        # Normalize nfcore to nf-core (case-insensitive)
        text = re.sub(r"\bnfcore\b", "nf-core", text, flags=re.IGNORECASE)
        # Replace underscores with spaces
        text = text.replace("_", " ")
        # Split into words and apply title case, but preserve special brand terms
        words = text.split()
        formatted_words = []
        for word in words:
            word_lower = word.lower()
            if word_lower == "nf-core":
                formatted_words.append("nf-core")
            elif word_lower == "api":
                formatted_words.append("API")
            else:
                formatted_words.append(word.title())
        return " ".join(formatted_words)

    # Handle local execution tools with special mappings
    if tool_name.startswith("mcp__local-execution__"):
        tool_suffix = tool_name.replace("mcp__local-execution__", "")
        if tool_suffix == "write_file":
            return "Write"
        elif tool_suffix == "read_file":
            return "Read"
        elif tool_suffix == "edit_file":
            return "Edit"
        elif tool_suffix == "run_command":
            return "Bash"
        else:
            return _format_with_branding_preservation(tool_suffix)

    # Handle any other mcp__ prefix (e.g., mcp__seqera-mcp__, mcp__other__)
    if tool_name.startswith("mcp__"):
        # Find the end of the prefix (after the second __)
        parts = tool_name.split("__", 2)
        if len(parts) >= 3:
            # Remove the mcp__ and the server name, keep only the tool name
            tool_suffix = parts[2]
            return _format_with_branding_preservation(tool_suffix)
        else:
            # Fallback: just remove mcp__ prefix
            return _format_with_branding_preservation(tool_name.replace("mcp__", ""))

    return tool_name


def format_tool_input_compact(tool_name: str, tool_input: dict) -> Text:
    """
    Format tool input as a compact single-line or brief summary.

    Args:
        tool_name: Name of the tool (e.g., "Bash", "Read", "Grep")
        tool_input: Tool input dictionary

    Returns:
        Rich Text object with compact formatting
    """
    # Convert MCP tool names to friendly names
    formatted_name = format_mcp_tool_name(tool_name)

    text = Text()
    text.append(formatted_name, style="bold #7B89EE")

    # Tool-specific compact formatting
    if formatted_name == "Bash":
        cmd = tool_input.get("command", "")
        if len(cmd) > 100:
            cmd = cmd[:97] + "..."
        text.append(f" {cmd}", style="dim")

    elif formatted_name == "Read":
        path = tool_input.get("file_path", "")
        filename = path.split("/")[-1] if "/" in path else path
        text.append(f" {filename}", style="dim")

    elif formatted_name == "Grep":
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", ".")
        text.append(f" '{pattern}'", style="")
        text.append(f" in {path}", style="dim")

    elif formatted_name == "Write":
        path = tool_input.get("file_path", "")
        filename = path.split("/")[-1] if "/" in path else path
        content = tool_input.get("content", "")
        lines = content.split("\n") if content else []
        text.append(f" {filename}", style="dim")
        text.append(f" ({len(lines)} lines)", style="dim")

    elif formatted_name == "Edit":
        path = tool_input.get("file_path", "")
        filename = path.split("/")[-1] if "/" in path else path
        old_str = tool_input.get("old_string", "")
        new_str = tool_input.get("new_string", "")
        # Show a longer preview of the edit
        old_preview = old_str[:80].replace("\n", "↵") if old_str else ""
        new_preview = new_str[:80].replace("\n", "↵") if new_str else ""
        text.append(f" {filename}", style="dim")
        if old_preview:
            text.append(f"\n  - {old_preview}...", style="red dim")
        if new_preview:
            text.append(f"\n  + {new_preview}...", style="green dim")

    elif formatted_name == "Glob":
        pattern = tool_input.get("pattern", "")
        text.append(f" {pattern}", style="dim")

    elif formatted_name == "WebFetch":
        url = tool_input.get("url", "")
        if len(url) > 80:
            url = url[:77] + "..."
        text.append(f" {url}", style="dim")

    elif formatted_name == "WebSearch":
        query = tool_input.get("query", "")
        if len(query) > 80:
            query = query[:77] + "..."
        text.append(f" '{query}'", style="dim")

    elif formatted_name == "TodoWrite":
        todos = tool_input.get("todos", [])
        if todos:
            text.append("\n", style="")
            for i, task in enumerate(todos, 1):
                status = task.get("status", "pending")
                content = task.get("content", "")
                status_icon = {
                    "pending": "[ ]",
                    "in_progress": "[~]",
                    "completed": "[x]",
                    "cancelled": "[-]",
                }.get(status, "[ ]")
                status_style = {
                    "pending": "dim",
                    "in_progress": "yellow",
                    "completed": "green",
                    "cancelled": "red dim",
                }.get(status, "dim")
                text.append(f"  {status_icon} ", style=status_style)
                text.append(f"{content}\n", style=status_style)

    else:
        # Generic: show key parameters with their values
        if tool_input:
            text.append("\n", style="")
            # Show up to 5 params
            for key, val in list(tool_input.items())[:5]:
                val_str = str(val)
                if len(val_str) > 100:
                    val_str = val_str[:97] + "..."
                val_str = val_str.replace("\n", "↵")
                text.append(f"  {key}: ", style="dim")
                text.append(f"{val_str}\n", style="dim italic")

    return text


def format_tool_result_compact(
    tool_name: str,
    content: str,
    is_error: bool,
    max_lines: int = COMPACT_PREVIEW_LINES,
) -> Text:
    """
    Format tool result with truncation and summary.

    Args:
        tool_name: Name of the tool
        content: Full output content
        is_error: Whether the result is an error
        max_lines: Maximum lines to show before truncation

    Returns:
        Rich Text object with compact result
    """
    text = Text()

    # Convert MCP tool names to friendly names
    formatted_name = format_mcp_tool_name(tool_name)

    # Status indicator
    if is_error:
        text.append(formatted_name, style="bold red")
        text.append(" failed", style="red")
    else:
        text.append(formatted_name, style="bold green")

    if not content:
        return text

    lines = content.strip().split("\n")
    total_lines = len(lines)

    # Add summary info
    if total_lines > max_lines:
        text.append(f" ({total_lines} lines)", style="dim")
    elif total_lines == 1 and len(lines[0]) < 50:
        # Very short output - show inline
        text.append(f" → {lines[0]}", style="dim")
        return text

    # Add truncated preview
    text.append("\n")
    preview_lines = lines[:max_lines]
    for line in preview_lines:
        # Truncate long lines
        if len(line) > COMPACT_MAX_LINE_LENGTH:
            line = line[: COMPACT_MAX_LINE_LENGTH - 3] + "..."
        text.append(f"  {line}\n", style="dim")

    # Add truncation indicator
    if total_lines > max_lines:
        remaining = total_lines - max_lines
        text.append(f"  ... {remaining} more lines ", style="dim italic")
        text.append("(-v to expand)", style="dim italic #7B89EE")

    return text


def resolve_token_provider(
    token_arg: Optional[str], verbose: bool = False
) -> Callable[[], str]:
    """
    Build a callable that always returns a valid Seqera bearer token.

    Args:
        token_arg: Optional token passed via --token flag (for testing/CI only)
        verbose: Whether to print token source information

    Returns:
        Callable that provides a token when invoked
    """

    if token_arg:
        stripped = token_arg.strip()
        if not stripped:
            raise click.ClickException("Empty --token provided.")
        console.print("[yellow]⚠️  Using token from --token flag (not Auth0)[/yellow]")
        return lambda: stripped

    auth_manager = get_auth_manager(console=console)

    def _provider() -> str:
        try:
            token = auth_manager.get_access_token(prompt_login=True)
            # Show token source in verbose mode only
            if verbose:
                token_type = "JWT" if token.count(".") == 2 else "Opaque"
                console.print(f"[dim]✓ Using Auth0 token ({token_type} format)[/dim]")
            return token
        except AuthError as exc:
            raise click.ClickException(str(exc)) from exc

    # Prime once so we surface login issues before connecting to the backend
    _provider()
    return _provider


def gather_directory_context(cwd: str) -> dict:
    """
    Gather contextual information about the current working directory.

    Args:
        cwd: Current working directory

    Returns:
        Dictionary with directory context information
    """
    context = {
        "cwd": cwd,
        "directory_tree": None,
        "main_nf_path": None,
        "main_nf_content": None,
        "git_status": None,
        "directory_listing": None,
    }

    try:
        # Get directory tree (depth 2)
        try:
            # Try to use tree command if available
            result = subprocess.run(
                ["tree", "-L", "2", "-a", "--noreport"],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT,
            )
            if result.returncode == 0:
                context["directory_tree"] = result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Fallback to manual directory listing if tree is not available
            try:
                tree_lines = []
                path = Path(cwd)
                tree_lines.append(str(path))

                # Level 1
                for item in sorted(path.iterdir()):
                    if item.name.startswith(".") and item.name not in [
                        ".git",
                        ".github",
                        ".nextflow",
                    ]:
                        continue
                    prefix = "├── " if item != list(path.iterdir())[-1] else "└── "
                    tree_lines.append(
                        f"{prefix}{item.name}{'/' if item.is_dir() else ''}"
                    )

                    # Level 2
                    if item.is_dir():
                        try:
                            sub_items = list(item.iterdir())
                            # Limit to MAX_TREE_ITEMS
                            for sub_item in sorted(sub_items[:MAX_TREE_ITEMS]):
                                tree_lines.append(
                                    f"    ├── {sub_item.name}{'/' if sub_item.is_dir() else ''}"
                                )
                            if len(sub_items) > MAX_TREE_ITEMS:
                                tree_lines.append(
                                    f"    └── ... ({len(sub_items) - MAX_TREE_ITEMS} more items)"
                                )
                        except PermissionError:
                            tree_lines.append("    └── [permission denied]")

                context["directory_tree"] = "\n".join(tree_lines)
            except (PermissionError, FileNotFoundError) as e:
                context["directory_tree"] = f"Unable to generate directory tree: {e}"
            except Exception as e:
                logger.warning("Unexpected error generating directory tree: %s", e)
                context["directory_tree"] = "Directory structure unavailable"

        # Find main.nf
        main_nf_candidates = [
            Path(cwd) / "main.nf",
            Path(cwd) / "workflows" / "main.nf",
        ]

        for candidate in main_nf_candidates:
            if candidate.exists():
                context["main_nf_path"] = str(candidate.relative_to(cwd))
                try:
                    # Read first MAX_MAIN_NF_LINES or MAX_MAIN_NF_CHARS of main.nf
                    with open(candidate, "r", encoding="utf-8") as f:
                        content = f.read(MAX_MAIN_NF_CHARS)
                        lines = [
                            line[:MAX_LINE_LENGTH]
                            if len(line) > MAX_LINE_LENGTH
                            else line
                            for line in content.split("\n")[:MAX_MAIN_NF_LINES]
                        ]
                        context["main_nf_content"] = "\n".join(lines)
                        if (
                            len(content) >= MAX_MAIN_NF_CHARS
                            or len(lines) >= MAX_MAIN_NF_LINES
                        ):
                            context["main_nf_content"] += "\n... (truncated)"
                except Exception as e:
                    context["main_nf_content"] = f"Error reading file: {e}"
                break

        # Get git status
        try:
            # Check if it's a git repo
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode == 0:
                # Get git status
                result = subprocess.run(
                    ["git", "status", "--porcelain", "--branch"],
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=COMMAND_TIMEOUT,
                )
                if result.returncode == 0:
                    status_lines = result.stdout.strip().split("\n")
                    branch_info = status_lines[0] if status_lines else ""

                    # Count changes
                    modified = sum(
                        1 for line in status_lines[1:] if line.startswith(" M")
                    )
                    added = sum(1 for line in status_lines[1:] if line.startswith("A "))
                    deleted = sum(
                        1 for line in status_lines[1:] if line.startswith(" D")
                    )
                    untracked = sum(
                        1 for line in status_lines[1:] if line.startswith("??")
                    )

                    has_uncommitted = any(line.strip() for line in status_lines[1:])

                    context["git_status"] = {
                        "is_git_repo": True,
                        "branch": branch_info.replace("## ", ""),
                        "has_uncommitted_changes": has_uncommitted,
                        "modified": modified,
                        "added": added,
                        "deleted": deleted,
                        "untracked": untracked,
                    }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            context["git_status"] = {"is_git_repo": False}

        # Get directory listing (ls -la equivalent)
        try:
            path = Path(cwd)
            listing_lines = []

            for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
                try:
                    stat = item.stat()
                    size = stat.st_size
                    is_dir = item.is_dir()
                    name = item.name + ("/" if is_dir else "")

                    # Format: name, size, type
                    if is_dir:
                        listing_lines.append(f"{name:<40} <DIR>")
                    else:
                        size_str = (
                            f"{size:>10,} bytes"
                            if size < 1024 * 1024
                            else f"{size/(1024*1024):>7.2f} MB"
                        )
                        listing_lines.append(f"{name:<40} {size_str}")

                    if len(listing_lines) >= MAX_DIRECTORY_ITEMS:  # Limit output
                        remaining = len(list(path.iterdir())) - MAX_DIRECTORY_ITEMS
                        if remaining > 0:
                            listing_lines.append(f"... ({remaining} more items)")
                        break
                except Exception:
                    listing_lines.append(f"{item.name:<40} [error reading]")

            context["directory_listing"] = "\n".join(listing_lines)
        except Exception as e:
            context["directory_listing"] = f"Error listing directory: {e}"

    except Exception as e:
        console.print(
            f"[yellow]Warning: Could not gather full directory context: {e}[/yellow]"
        )

    return context


def show_available_commands():
    """Display available reserved commands."""
    console.print(
        "[dim]To get started, describe a task or try one of these commands:[/dim]"
    )

    for cmd, desc in RESERVED_COMMANDS.items():
        # Command in greenish-blue, description in dim grey
        console.print(f"  [bold #7B89EE]{cmd}[/bold #7B89EE] [dim]- {desc}[/dim]")

    console.print()


def show_initial_hint():
    """Display initial hint about commands."""
    console.print("[dim]To get started, describe a task or try:[/dim]")
    console.print(
        "  [bold #7B89EE]/[/bold #7B89EE] [dim]- Show available commands[/dim]"
    )
    console.print()


def show_approval_status(current_mode: str):
    """Display a nicely formatted approval mode status."""
    console.print()
    console.print("[bold #7B89EE]Local Approval Mode[/bold #7B89EE]")
    console.print()

    for mode in APPROVAL_MODE_CHOICES:
        rules = APPROVAL_RULES.get(mode, "")
        if mode == current_mode:
            console.print(
                f"  [bold green]● {mode:<10}[/bold green] [green]{rules}[/green]"
            )
        else:
            console.print(f"  [dim]○ {mode:<10}[/dim] [dim]{rules}[/dim]")

    console.print()
    console.print(
        "[dim]Change with /approval basic|default|full or use "
        "--approval-mode on startup.[/dim]"
    )
    console.print()


def prompt_select_approval_mode(current_mode: str) -> Optional[str]:
    """
    Prompt the user to select an approval mode using arrow keys.
    Returns the selected mode or None if cancelled.
    """
    if not HAS_PROMPT_TOOLKIT:
        return None

    modes = list(APPROVAL_MODE_CHOICES)
    try:
        selected_index = modes.index(current_mode)
    except ValueError:
        selected_index = 0

    result: Optional[str] = None

    def get_formatted_text():
        lines = []
        lines.append(
            (
                "",
                "Select approval mode (↑/↓ to move, Enter to confirm, Esc to cancel):\n\n",
            )
        )
        for i, mode in enumerate(modes):
            rules = APPROVAL_RULES.get(mode, "")
            if i == selected_index:
                lines.append(("bold fg:green", f"  ● {mode:<10}"))
                lines.append(("fg:green", f" {rules}\n"))
            else:
                lines.append(("fg:gray", f"  ○ {mode:<10} {rules}\n"))
        return lines

    kb = KeyBindings()

    @kb.add("up")
    def move_up(event):
        nonlocal selected_index
        selected_index = (selected_index - 1) % len(modes)

    @kb.add("down")
    def move_down(event):
        nonlocal selected_index
        selected_index = (selected_index + 1) % len(modes)

    @kb.add("enter")
    def confirm(event):
        nonlocal result
        result = modes[selected_index]
        event.app.exit()

    @kb.add("escape")
    @kb.add("c-c")
    def cancel(event):
        event.app.exit()

    app = Application(
        layout=Layout(Window(FormattedTextControl(get_formatted_text))),
        key_bindings=kb,
        full_screen=False,
    )

    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        return None

    return result


def handle_reserved_command(command: str, client: "SeqeraClient") -> bool:
    """
    Check if input is a reserved command and handle it.

    Args:
        command: User input to check
        client: SeqeraClient instance for executing commands

    Returns:
        True if command was handled, False otherwise
    """
    command = command.strip()

    # Check if it's a reserved command
    if not command.startswith("/"):
        return False

    # Extract command and arguments
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd not in RESERVED_COMMANDS:
        console.print(f"[bold red]Unknown command:[/bold red] {cmd}")
        console.print("[dim]Type /[/dim]")
        return True

    # Handle / command
    if cmd == "/":
        show_available_commands()
        return True

    # Handle /approval command
    if cmd == "/approval":
        if args:
            new_mode = args.strip().lower()
            success, message = client.set_approval_mode(new_mode)
            if success:
                console.print(
                    f"[bold green]✓[/bold green] {message} (applies to this session)"
                )
            else:
                console.print(f"[bold red]Error:[/bold red] {message}")
        else:
            # Interactive arrow-key selector
            selected = prompt_select_approval_mode(client.approval_mode)
            if selected is None:
                console.print("[dim]Cancelled.[/dim]")
            elif selected == client.approval_mode:
                console.print(
                    f"[dim]Approval mode unchanged ({client.approval_mode}).[/dim]"
                )
            else:
                success, message = client.set_approval_mode(selected)
                if success:
                    console.print(
                        f"[bold green]✓[/bold green] {message} (applies to this session)"
                    )
                else:
                    console.print(f"[bold red]Error:[/bold red] {message}")
        return True

    # Handle /config command
    if cmd == "/config":
        query = "Generate a comprehensive 'nextflow.config' file for this pipeline. Analyze the pipeline logic to identify necessary process resource requirements (cpus, memory, time) and container requirements. Include profiles for different execution environments (e.g., 'standard' for local, 'docker', 'singularity', 'awsbatch'). Follow nf-core best practices for configuration structure."
        if args:
            query += f" Additional context: {args}"
        console.print("[bold cyan]Generating pipeline configuration...[/bold cyan]\n")
        client.send_query_streaming(query)
        return True

    # Handle /schema command
    if cmd == "/schema":
        query = "Help the user generate a Nextflow schema. First, recommend running 'nf-core schema build' as it is the standard tool for this. If 'nf-core' is not available, ask the user if they want to install it (via 'pip install nf-core') or if they prefer you to generate the 'nextflow_schema.json' manually. If manual generation is requested: Generate a comprehensive 'nextflow_schema.json' for this pipeline following the nf-core best practices and JSON Schema Draft 7 specification. Analyze the 'nextflow.config' and 'main.nf' files to identify all pipeline parameters. Structure the schema with appropriate types, default values, descriptions, and help text. Group related parameters (e.g., 'Input/Output', 'Resource Options') using the 'definitions' keyword to create a user-friendly interface in Nextflow Tower/Seqera Platform."
        if args:
            query += f" Additional context: {args}"
        console.print("[bold cyan]Generating pipeline schema...[/bold cyan]\n")
        client.send_query_streaming(query)
        return True

    # Handle /debug command
    if cmd == "/debug":
        query = "Debug this Nextflow pipeline by performing a comprehensive check. 1. Run 'nextflow lint' to identify syntax and best practice issues. 2. Run 'nextflow config' to validate the configuration. 3. Run 'nextflow run . -preview' to ensure the pipeline compilation and DAG generation work correctly. Analyze the outputs, identify any errors, and provide actionable fixes. Assume that nextflow is installed."
        if args:
            query += f" Additional context: {args}"
        console.print("[bold cyan]Running pipeline diagnostics...[/bold cyan]\n")
        client.send_query_streaming(query)
        return True

    # Handle /migrate-from-wdl command
    if cmd == "/migrate-from-wdl":
        query = "Start a migration workflow to convert this WDL pipeline to Nextflow. First, create a comprehensive migration plan. 1. Analyze all WDL files and identify the workflow structure, inputs, tasks, and outputs. 2. List the corresponding Nextflow components (processes, channels, workflows) needed. 3. Review the plan to ensure no logic is missed. 4. Begin a piece-meal execution plan, converting the pipeline step-by-step, starting with the base configuration and input handling, then moving to individual tasks, and finally the workflow logic. IMPORTANT: After each major conversion step (e.g., after converting a process or workflow section), run 'nextflow run . -preview' to verify the pipeline compiles correctly. If there are syntax errors, fix them before proceeding to the next step. Once the full conversion is complete, run both 'nextflow lint' and 'nextflow run . -preview' to ensure everything is working as expected. Assume that nextflow is installed."
        if args:
            query += f" Target files or additional context: {args}"
        console.print(
            "[bold cyan]Starting WDL to Nextflow migration workflow...[/bold cyan]\n"
        )
        client.send_query_streaming(query)
        return True

    # Handle /migrate-from-snakemake command
    if cmd == "/migrate-from-snakemake":
        query = "Start a migration workflow to convert this Snakemake pipeline to Nextflow. First, create a comprehensive migration plan. 1. Analyze the Snakefile and any included rule files to identify the workflow structure, inputs, rules (tasks), and outputs. 2. List the corresponding Nextflow components (processes, channels, workflows) needed. 3. Review the plan to ensure no logic is missed. 4. Begin a piece-meal execution plan, converting the pipeline step-by-step, starting with the base configuration and input handling, then moving to individual rules/processes, and finally the workflow logic. IMPORTANT: After each major conversion step (e.g., after converting a process or workflow section), run 'nextflow run . -preview' to verify the pipeline compiles correctly. If there are syntax errors, fix them before proceeding to the next step. Once the full conversion is complete, run both 'nextflow lint' and 'nextflow run . -preview' to ensure everything is working as expected. Assume that nextflow is installed."
        if args:
            query += f" Target files or additional context: {args}"
        console.print(
            "[bold cyan]Starting Snakemake to Nextflow migration workflow...[/bold cyan]\n"
        )
        client.send_query_streaming(query)
        return True

    # Handle /convert-jupyter-notebook command
    if cmd == "/convert-jupyter-notebook":
        query = "Convert this Jupyter Notebook to a Nextflow process. The notebook should likely be broken up into several proceses if a user is asking you to conver it. Don't just wrap the notebook in Nextflow, break it up into several processes. First, create a plan. 1. Analyze the notebook to understand the analysis steps, inputs, and outputs. 2. Outline the Nextflow process structure and container requirements. 3. Execute the plan: Extract the relevant code cells, create the Nextflow process wrapping this logic, define the input/output channels, and define the container environment. IMPORTANT: After creating the Nextflow process, run 'nextflow run . -preview' to verify the pipeline compiles correctly. If there are syntax errors, fix them. Then run 'nextflow lint' to check for best practice issues. Assume that nextflow is installed."
        if args:
            query += f" Target notebook or additional context: {args}"
        console.print(
            "[bold cyan]Converting Jupyter Notebook to Nextflow...[/bold cyan]\n"
        )
        client.send_query_streaming(query)
        return True

    # Handle /convert-r-script command
    if cmd == "/convert-r-script":
        query = "Convert this R script to a Nextflow process. The script should likely be broken up into several proceses if a user is asking you to conver it. Don't just wrap the script in Nextflow, break it up into several processes. First, create a plan. 1. Analyze the R script to identify input files, parameters, and output files. 2. Outline the Nextflow process structure and dependency requirements. 3. Execute the plan: Create the Nextflow process with correct `input`, `output`, and `script` blocks, and handle R library dependencies by suggesting a container or conda environment. IMPORTANT: After creating the Nextflow process, run 'nextflow run . -preview' to verify the pipeline compiles correctly. If there are syntax errors, fix them. Then run 'nextflow lint' to check for best practice issues. Assume that nextflow is installed."
        if args:
            query += f" Target script or additional context: {args}"
        console.print("[bold cyan]Converting R script to Nextflow...[/bold cyan]\n")
        client.send_query_streaming(query)
        return True

    # Handle /convert-python-script command
    if cmd == "/convert-python-script":
        query = "Convert this Python script to a Nextflow process. The script should likely be broken up into several proceses if a user is asking you to conver it. Don't just wrap the script in Nextflow, break it up into several processes. First, create a plan. 1. Analyze the Python script to identify input files, parameters (argparse/click), and output files. 2. Outline the Nextflow process structure and dependency requirements. 3. Execute the plan: Create the Nextflow process with correct `input`, `output`, and `script` blocks, and handle Python package dependencies by suggesting a container or conda environment. IMPORTANT: After creating the Nextflow process, run 'nextflow run . -preview' to verify the pipeline compiles correctly. If there are syntax errors, fix them. Then run 'nextflow lint' to check for best practice issues. Assume that nextflow is installed."
        if args:
            query += f" Target script or additional context: {args}"
        console.print(
            "[bold cyan]Converting Python script to Nextflow...[/bold cyan]\n"
        )
        client.send_query_streaming(query)
        return True

    # Handle /write-nf-test command
    if cmd == "/write-nf-test":
        query = "Analyze the codebase and write nf-tests for any untested portions. Identify modules and subworkflows that lack test coverage and create comprehensive nf-test files following best practices."
        if args:
            query += f" Additional context: {args}"
        console.print(
            "[bold cyan]Generating nf-tests for untested code...[/bold cyan]\n"
        )
        client.send_query_streaming(query)
        return True

    # Handle /debug-last-run command
    if cmd == "/debug-last-run":
        query = "Debug the last local Nextflow run. Analyze the .nextflow.log file and work directory to identify what went wrong and suggest solutions."
        if args:
            query += f" Additional context: {args}"
        console.print("[bold #7B89EE]Debugging last local run...[/bold #7B89EE]\n")
        client.send_query_streaming(query)
        return True

    # Handle /debug-last-run-on-seqera command
    if cmd == "/debug-last-run-on-seqera":
        query = "Debug the last run on Seqera Platform. Retrieve the most recent workflow run, analyze its status, logs, and any errors, and provide recommendations for fixing issues."
        if args:
            query += f" Additional context: {args}"
        console.print(
            "[bold #7B89EE]Debugging last Seqera Platform run...[/bold #7B89EE]\n"
        )
        client.send_query_streaming(query)
        return True

    # Handle /feedback command
    if cmd == "/feedback":
        console.print("\nVisit: [#7B89EE]https://feedback.seqera.io/[/#7B89EE]")
        return True

    # Handle /help-community command
    if cmd == "/help-community":
        console.print("\nVisit: [#7B89EE]https://community.seqera.io/[/#7B89EE]")
        return True

    # Handle /stickers command
    if cmd == "/stickers":
        import webbrowser

        url = "https://www.stickermule.com/seqera"
        try:
            webbrowser.open(url)
            console.print(
                f"\n[bold green]✓[/bold green] Opening: [#7B89EE]{url}[/#7B89EE]"
            )
        except Exception as e:
            console.print(f"\nVisit: [#7B89EE]{url}[/#7B89EE]")
            console.print(f"[dim]Could not open browser automatically: {e}[/dim]")
        return True

    # Handle /credit command
    if cmd == "/credit":
        import requests

        try:
            token = client._current_token()
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{client.backend_url}/cli-agent/credits",
                headers=headers,
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                balance = data.get("balance", 0)
                is_preview_tester = data.get("is_preview_tester", False)

                console.print()
                console.print(
                    f"[bold #7B89EE]Credit Balance:[/bold #7B89EE] [bold green]${balance:.2f}[/bold green]"
                )

                if is_preview_tester:
                    console.print()
                    console.print(
                        "[dim]You are in the Seqera CLI preview testing group. "
                        "If you run out of credits please contact your Account Manager for more credits.[/dim]"
                    )

                console.print()
                console.print(
                    "[dim]Need more credits?[/dim] [#7B89EE]https://seqera.io/platform/seqera-ai/request-credits/[/#7B89EE]"
                )
            elif response.status_code == 401:
                console.print(
                    "[bold red]Error:[/bold red] Authentication required. Please run `seqera login`."
                )
            else:
                console.print(
                    f"[bold red]Error:[/bold red] Unable to retrieve credit balance (status: {response.status_code})"
                )
        except requests.exceptions.Timeout:
            console.print(
                "[bold red]Error:[/bold red] Request timed out. Please try again."
            )
        except requests.exceptions.ConnectionError:
            console.print(
                "[bold red]Error:[/bold red] Unable to connect to server. Please check your connection."
            )
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return True

    # Handle /history command
    if cmd == "/history":
        if not client.conversation_history:
            console.print("[dim]No conversation history.[/dim]")
            return True

        console.print("[bold #7B89EE]Conversation History:[/bold #7B89EE]\n")
        for i, message in enumerate(client.conversation_history, 1):
            role = message.get("role", "unknown")
            content = message.get("content", "")

            if role == "user":
                role_label = "[bold cyan]User:[/bold cyan]"
            elif role == "assistant":
                role_label = "[bold #5E6FEB]Assistant:[/bold #5E6FEB]"
            else:
                role_label = f"[dim]{role}:[/dim]"

            # Truncate very long messages for display
            display_content = content
            if len(content) > 500:
                display_content = content[:500] + "..."

            console.print(f"{i}. {role_label}")
            console.print(f"   {display_content}\n")

        console.print(f"[dim]Total messages: {len(client.conversation_history)}[/dim]")
        return True

    return True


class SeqeraClient:
    """
    Client for communicating with Seqera AI backend via WebSocket.

    Follows a simple, robust architecture inspired by Claude Code and OpenCode:
    - Connect on first query, reconnect on failure
    - Single retry layer at the query level
    - Clear error messages
    - Minimal state management
    """

    # Connection timeout for establishing WebSocket
    CONNECT_TIMEOUT_SECONDS = 30
    # Receive timeout for waiting for backend responses
    RECEIVE_TIMEOUT_SECONDS = 120
    # Connection idle timeout (reconnect if idle too long)
    IDLE_TIMEOUT_SECONDS = 30 * 60  # 30 minutes
    # Query retry configuration
    MAX_QUERY_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # Exponential backoff in seconds

    def __init__(
        self,
        backend_url: str,
        token_provider: Callable[[], str],
        verbose: bool = False,
        cwd: Optional[str] = None,
        approval_mode: str = "default",
    ):
        """
        Initialize client.

        Args:
            backend_url: URL of the backend server (e.g., http://localhost:8002)
            token_provider: Callable that returns a valid Seqera Platform access token
            verbose: Show detailed tool execution info
            cwd: Current working directory to pass to backend
            approval_mode: How to handle command approvals
        """
        self.backend_url = backend_url.rstrip("/")
        self._token_provider = token_provider
        self.verbose = verbose
        self.cwd = cwd or os.getcwd()
        mode_value = str(approval_mode).lower() if approval_mode else "default"
        self.approval_mode = mode_value if mode_value in APPROVAL_MODES else "default"
        self.session_id: Optional[str] = None
        self.ws_url = self.backend_url.replace("http://", "ws://").replace(
            "https://", "wss://"
        )

        # Conversation history (client-side for context)
        self.conversation_history: list[dict] = []

        self.approval_manager = ApprovalManager(self.approval_mode, self.cwd)

        # Directory context for better AI responses
        if verbose:
            console.print("[dim]Gathering directory context...[/dim]")
        self.directory_context = gather_directory_context(self.cwd)
        if verbose:
            console.print("[dim]Directory context gathered[/dim]")

        # Simple connection state
        self.ws: Optional[websocket.WebSocket] = None
        self.ws_connected_at: Optional[float] = None
        self._query_count = 0

    def get_approval_status(self) -> str:
        rules = APPROVAL_RULES.get(self.approval_mode, "")
        return f"Local approval mode: [bold]{self.approval_mode}[/bold]{f' — {rules}' if rules else ''}"

    def set_approval_mode(self, mode: str) -> tuple[bool, str]:
        normalized = str(mode).strip().lower()
        if normalized not in APPROVAL_MODES:
            choices = ", ".join(APPROVAL_MODE_CHOICES)
            return False, f"Invalid approval mode '{mode}'. Choose from: {choices}."

        self.approval_mode = normalized
        self.approval_manager = ApprovalManager(self.approval_mode, self.cwd)
        # Force a fresh backend session so the new mode is applied
        self.session_id = None
        # Close existing connection to force reconnect with new approval mode
        self._disconnect()
        rules = APPROVAL_RULES.get(self.approval_mode, "")
        return (
            True,
            f"Approval mode set to '{self.approval_mode}'{f' ({rules})' if rules else ''}.",
        )

    def _is_connected(self) -> bool:
        """Check if WebSocket is currently connected."""
        return self.ws is not None and self.ws.connected

    def _should_reconnect(self) -> bool:
        """Check if connection should be refreshed."""
        if not self._is_connected():
            return True

        # Check idle timeout
        if (
            self.ws_connected_at
            and (time.time() - self.ws_connected_at) > self.IDLE_TIMEOUT_SECONDS
        ):
            if self.verbose:
                console.print("[dim]Connection idle too long, reconnecting...[/dim]")
            return True

        return False

    def _connect(self) -> None:
        """
        Establish WebSocket connection to backend.

        Simple and direct - no internal retries here.
        Retries happen at the query level for better error recovery.
        """
        # Close any existing connection
        self._disconnect()

        ws_url = f"{self.ws_url}/cli-agent/ws/query"

        if self.verbose:
            console.print(f"[dim]Connecting to {ws_url}[/dim]")

        # Get token and prepare headers
        token = self._current_token()
        headers = [f"Authorization: Bearer {token}"]

        try:
            self.ws = websocket.create_connection(
                ws_url, timeout=self.CONNECT_TIMEOUT_SECONDS, header=headers
            )
            self.ws_connected_at = time.time()
            self._query_count = 0
        except websocket.WebSocketException as e:
            self.ws = None
            raise ConnectionError(f"WebSocket connection failed: {e}")
        except Exception as e:
            self.ws = None
            raise ConnectionError(f"Connection failed: {e}")

    def _disconnect(self) -> None:
        """Close WebSocket connection cleanly."""
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass  # Ignore close errors
            finally:
                self.ws = None
                self.ws_connected_at = None

    def _ensure_connected(self) -> None:
        """Ensure WebSocket is connected, reconnecting if needed."""
        if self._should_reconnect():
            self._connect()

        if not self._is_connected():
            raise ConnectionError("Failed to establish WebSocket connection")

    def cleanup(self) -> None:
        """Clean up resources. Call this when CLI exits."""
        if self._is_connected() and self._query_count > 0:
            console.print(
                f"\n[dim]Session ended ({self._query_count} {'query' if self._query_count == 1 else 'queries'})[/dim]"
            )
        self._disconnect()

    def _current_token(self) -> str:
        """Return the latest bearer token supplied by the auth provider."""

        token = self._token_provider()
        if not token:
            raise click.ClickException(
                "Unable to obtain a Seqera Platform token. Please run `seqera login`."
            )
        return token

    def check_health(self) -> bool:
        """Check if backend is healthy."""
        import requests

        try:
            response = requests.get(f"{self.backend_url}/cli-agent/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def prepare_session(self) -> bool:
        """
        Pre-establish WebSocket connection and session before first query.
        This makes the first query instant since everything is already set up.

        Returns:
            True if session was successfully established, False otherwise
        """
        try:
            # Only prepare if not already connected
            if self._is_connected():
                return True

            with console.status("[dim]Preparing session...[/dim]", spinner="dots"):
                # Establish connection
                self._connect()

                # Wait for backend to send session message
                try:
                    self.ws.sock.settimeout(5.0)
                    initial_msg = self.ws.recv()
                    if initial_msg and initial_msg.strip():
                        try:
                            session_msg = json.loads(initial_msg)
                            if session_msg.get("type") == "session":
                                self.session_id = session_msg.get("session_id")
                                if self.verbose:
                                    console.print(
                                        f"[dim]✓ Session ready: {self.session_id}[/dim]"
                                    )
                                return True
                        except json.JSONDecodeError:
                            if self.verbose:
                                console.print(
                                    "[dim]⚠ Received non-JSON session message[/dim]"
                                )
                except Exception as e:
                    if self.verbose:
                        console.print(f"[dim]⚠ Session preparation: {e}[/dim]")
                    return False

            return False
        except Exception as e:
            if self.verbose:
                console.print(f"[dim]⚠ Failed to prepare session: {e}[/dim]")
            return False

    def execute_local_command(
        self,
        command: str,
        tool_name: str = "",
        tool_input: Optional[dict] = None,
    ) -> dict:
        """
        Execute a command in the local directory where CLI was launched.

        Args:
            command: Shell command to execute
            tool_name: Optional MCP tool name for better display
            tool_input: Optional MCP tool input dict for better display

        Returns:
            Dictionary with stdout, stderr, and exit_code
        """
        import subprocess

        cleaned_command = command.strip()
        if not cleaned_command:
            return {
                "stdout": "",
                "stderr": "No command provided for execution",
                "exit_code": 1,
            }

        decision = self.approval_manager.evaluate(cleaned_command)

        if decision.requires_prompt:
            try:
                self.prompt_for_approval(
                    cleaned_command,
                    decision,
                    tool_name=tool_name,
                    tool_input=tool_input,
                )
            except SessionInterrupt:
                # Let this propagate up to interrupt the session
                self._log_approval(
                    cleaned_command, "approval_denied_interrupt", decision.reason
                )
                raise
            except (KeyboardInterrupt, EOFError):
                self._log_approval(
                    cleaned_command, "approval_cancelled", decision.reason
                )
                return {
                    "stdout": "",
                    "stderr": "Command blocked: approval prompt cancelled",
                    "exit_code": 1,
                }

            self._log_approval(cleaned_command, "approval_granted", decision.reason)
        else:
            self._log_approval(cleaned_command, "auto_execute", decision.reason)

        try:
            result = subprocess.run(
                cleaned_command,
                shell=True,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Command timed out after 5 minutes",
                "exit_code": 124,
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Error executing command: {str(e)}",
                "exit_code": 1,
            }

    def _format_command_for_display(self, command: str) -> Text:
        """
        Format a command for display in the approval prompt.
        Handles special cases like base64-encoded file writes and MCP local execution commands.
        """
        import base64
        import re

        text = Text()

        # Check for base64 file write pattern: python3 -c "import base64; open('FILE', 'wb').write(base64.b64decode('...'))"
        b64_write_match = re.match(
            r"python3?\s+-c\s+[\"']import base64;\s*open\([\"']([^\"']+)[\"'],\s*[\"']wb?[\"']\)\.write\(base64\.b64decode\([\"']([A-Za-z0-9+/=]+)[\"']\)\)[\"']",
            command,
        )

        if b64_write_match:
            filepath = b64_write_match.group(1)
            b64_content = b64_write_match.group(2)
            try:
                content = base64.b64decode(b64_content).decode(
                    "utf-8", errors="replace"
                )
                return self._format_file_write(filepath, content)
            except Exception:
                pass  # Fall through to default display

        # Check for simple echo/cat file writes
        echo_match = re.match(r"echo\s+[\"'](.+)[\"']\s*>\s*(.+)", command)
        if echo_match:
            content = echo_match.group(1)
            filepath = echo_match.group(2).strip()
            return self._format_file_write(filepath, content)

        # Default: show the command as-is (truncated if very long)
        if len(command) > 500:
            text.append(command[:500], style="cyan")
            text.append(f"... ({len(command) - 500} more chars)", style="dim italic")
        else:
            text.append(command, style="cyan")

        return text

    def _format_file_write(self, filepath: str, content: str) -> Text:
        """Format a file write operation for display."""
        text = Text()
        lines = content.split("\n")
        total_lines = len(lines)

        text.append("Write ", style="bold #7B89EE")
        text.append(filepath, style="cyan")
        text.append(f" ({total_lines} lines)\n", style="dim")

        # Show preview of content (first few lines)
        preview_lines = 8
        for i, line in enumerate(lines[:preview_lines]):
            display_line = line[:100] + "..." if len(line) > 100 else line
            text.append(f"  {i+1:3} │ ", style="dim")
            text.append(f"{display_line}\n", style="")

        if total_lines > preview_lines:
            text.append(
                f"      ... ({total_lines - preview_lines} more lines)",
                style="dim italic",
            )

        return text

    def _format_file_edit(
        self, filepath: str, old_string: str, new_string: str
    ) -> Text:
        """Format a file edit operation for display."""
        text = Text()

        text.append("Edit ", style="bold #7B89EE")
        text.append(filepath, style="cyan")
        text.append("\n", style="")

        # Show old content (what's being replaced)
        if old_string:
            old_lines = old_string.split("\n")[:5]
            for line in old_lines:
                display_line = line[:80] + "..." if len(line) > 80 else line
                text.append(f"  - {display_line}\n", style="red dim")
            if len(old_string.split("\n")) > 5:
                text.append("    ...\n", style="red dim")

        # Show new content (replacement)
        if new_string:
            new_lines = new_string.split("\n")[:5]
            for line in new_lines:
                display_line = line[:80] + "..." if len(line) > 80 else line
                text.append(f"  + {display_line}\n", style="green dim")
            if len(new_string.split("\n")) > 5:
                text.append("    ...\n", style="green dim")

        return text

    def _format_file_read(self, filepath: str) -> Text:
        """Format a file read operation for display."""
        text = Text()
        text.append("Read ", style="bold #7B89EE")
        text.append(filepath, style="cyan")
        return text

    def _format_bash_command(self, command: str) -> Text:
        """Format a bash command for display."""
        text = Text()
        text.append("Bash ", style="bold #7B89EE")

        # Truncate very long commands
        if len(command) > 200:
            text.append(command[:200], style="cyan")
            text.append(f"... ({len(command) - 200} more chars)", style="dim italic")
        else:
            text.append(command, style="cyan")

        return text

    def _format_mcp_tool_for_display(self, tool_name: str, tool_input: dict) -> Text:
        """
        Format an MCP tool call for display in the approval prompt.
        This handles the structured tool calls from the backend.
        """
        text = Text()

        # Handle different MCP local execution tools
        tool_name_lower = tool_name.lower()

        # Check for Edit tool first (before write, since edit has old_string/new_string)
        if (
            "edit" in tool_name_lower
            or "replace" in tool_name_lower
            or ("old_string" in tool_input and "new_string" in tool_input)
        ):
            filepath = tool_input.get("path", tool_input.get("file_path", "unknown"))
            old_string = tool_input.get("old_string", tool_input.get("old", ""))
            new_string = tool_input.get("new_string", tool_input.get("new", ""))
            return self._format_file_edit(filepath, old_string, new_string)

        elif "write" in tool_name_lower or "content" in tool_input:
            filepath = tool_input.get("path", tool_input.get("file_path", "unknown"))
            content = tool_input.get("content", "")
            return self._format_file_write(filepath, content)

        elif "read" in tool_name_lower:
            filepath = tool_input.get("path", tool_input.get("file_path", "unknown"))
            return self._format_file_read(filepath)

        elif (
            "bash" in tool_name_lower
            or "run_command" in tool_name_lower
            or "exec" in tool_name_lower
        ):
            command = tool_input.get("command", tool_input.get("cmd", str(tool_input)))
            return self._format_bash_command(command)

        elif "glob" in tool_name_lower:
            pattern = tool_input.get("pattern", "")
            path = tool_input.get("path", ".")
            text.append("Glob ", style="bold #7B89EE")
            text.append(f"{pattern}", style="cyan")
            text.append(f" in {path}", style="dim")
            return text

        elif "grep" in tool_name_lower or "search" in tool_name_lower:
            pattern = tool_input.get("pattern", "")
            path = tool_input.get("path", ".")
            text.append("Search ", style="bold #7B89EE")
            text.append(f"'{pattern}'", style="cyan")
            text.append(f" in {path}", style="dim")
            return text

        else:
            # Generic MCP tool display
            # Remove MCP prefixes
            display_name = format_mcp_tool_name(tool_name)
            text.append(f"{display_name} ", style="bold #7B89EE")

            # Show key parameters
            if tool_input:
                params = []
                for key, val in list(tool_input.items())[:3]:
                    val_str = str(val)
                    if len(val_str) > 50:
                        val_str = val_str[:47] + "..."
                    params.append(f"{key}={val_str}")
                text.append(", ".join(params), style="dim")

            return text

    def prompt_for_approval(
        self,
        command: str,
        decision: ApprovalDecision,
        tool_name: str = "",
        tool_input: Optional[dict] = None,
    ) -> bool:
        """
        Prompt user to approve a command. Returns True if approved.
        Raises SessionInterrupt if user denies (to end the current query).
        """
        console.print()
        console.print(
            f"[yellow bold]⚠ Approval required[/yellow bold] [dim]({self.approval_mode} mode)[/dim]"
        )
        console.print()

        # Use structured tool info if available, otherwise parse the command
        if tool_name and tool_input:
            formatted_cmd = self._format_mcp_tool_for_display(tool_name, tool_input)
        else:
            formatted_cmd = self._format_command_for_display(command)

        console.print(
            Panel(formatted_cmd, box=box.ROUNDED, border_style="cyan", padding=(0, 1))
        )
        console.print()
        console.print("  [bold]1[/bold] Yes, run this command")
        console.print("  [bold]2[/bold] Yes, and don't ask again this session")
        console.print("  [bold]3[/bold] No, cancel and stop")
        console.print()

        # Use single keypress input (no Enter required)
        response = self._get_single_keypress("[bold]Select [1/2/3]: [/bold]")

        if response == "1":
            return True
        elif response == "2":
            # Switch to full approval mode for this session
            self.approval_mode = "full"
            self.approval_manager = ApprovalManager(self.approval_mode, self.cwd)
            console.print(
                "\n[bold green]✓[/bold green] Switched to [bold]full[/bold] approval mode for this session"
            )
            return True
        elif response == "3":
            raise SessionInterrupt("User denied command approval")
        else:
            # Invalid key, default to deny
            console.print(f"[dim]Invalid selection '{response}', cancelling.[/dim]")
            raise SessionInterrupt("User cancelled command approval")

    def _get_single_keypress(self, prompt_text: str) -> str:
        """
        Get a single keypress from the user without requiring Enter.
        Falls back to regular input if single-char input is not available.
        """
        import sys
        import platform

        console.print(prompt_text, end="")

        try:
            if platform.system() == "Windows":
                import msvcrt

                char = msvcrt.getch().decode("utf-8", errors="ignore")
            else:
                import tty
                import termios

                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    char = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            console.print(char)  # Echo the character
            return char
        except Exception:
            # Fall back to regular input if single-char input fails
            return console.input("").strip()[:1]

    def _log_approval(self, command: str, decision: str, reason: str) -> None:
        # Log full command to logger only (not to console)
        logger.info(
            f"Approval [{self.approval_mode}] -> {decision} "
            f"(reason: {reason}) command: {command}"
        )

    def send_query_streaming(self, query: str):
        """
        Send query and stream responses via WebSocket.
        Automatically retries on connection failures.

        Args:
            query: User's query
        """
        last_error = None

        for attempt in range(self.MAX_QUERY_RETRIES):
            try:
                self._send_query_streaming_impl(query)
                return  # Success!

            except ConnectionError as e:
                # Connection failed - retry
                last_error = e
                self._disconnect()  # Ensure clean state

                if attempt < self.MAX_QUERY_RETRIES - 1:
                    # First retry is immediate (common case: stale connection)
                    # Subsequent retries use exponential backoff
                    if attempt == 0:
                        if self.verbose:
                            console.print("[dim]Reconnecting...[/dim]")
                    else:
                        delay = self.RETRY_DELAYS[attempt]
                        if self.verbose:
                            console.print(f"[yellow]⚠️  {str(e)}[/yellow]")
                            console.print(f"[dim]Retrying in {delay}s...[/dim]")
                        time.sleep(delay)
                else:
                    # All retries exhausted - always show this error
                    console.print("\n[bold red]❌ Connection failed[/bold red]")
                    console.print(f"[dim]{str(last_error)}[/dim]")
                    console.print("\n[yellow]Check that:[/yellow]")
                    console.print("  • Backend server is running")
                    console.print("  • Network connection is stable")
                    console.print(f"  • URL is correct: {self.backend_url}")
                    return

            except SessionInterrupt:
                # User interrupted - don't retry, propagate up
                raise

            except Exception as e:
                # Unexpected error - log and return (don't retry)
                console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
                if self.verbose:
                    import traceback

                    console.print(f"[dim]{traceback.format_exc()}[/dim]")
                self._disconnect()
                return

    def _send_query_streaming_impl(self, query: str):
        """
        Internal implementation of query sending.
        Raises ConnectionError on failure (caught by retry wrapper).

        Args:
            query: User's query
        """
        # Check if reusing existing connection
        was_connected = self._is_connected()

        # Connect if needed
        self._ensure_connected()

        # Track this query
        self._query_count += 1

        # Show connection status only in verbose mode
        if self.verbose:
            if was_connected:
                age = (
                    int(time.time() - self.ws_connected_at)
                    if self.ws_connected_at
                    else 0
                )
                console.print(
                    f"[dim]↻ Reusing connection (query #{self._query_count}, {age}s old)[/dim]"
                )
            else:
                console.print("[dim]🔗 Connected[/dim]")

        # Brief delay for new connections to stabilize
        if not was_connected:
            time.sleep(0.1)

        try:
            # Send query request with local execution enabled and conversation history
            # Backend will use MCP proxy for local operations
            request_data = {
                "query": query,
                "session_id": self.session_id,
                "verbose": self.verbose,
                "cwd": self.cwd,
                "approval_mode": self.approval_mode,
                # Enable local execution via MCP proxy callback
                "local_mcp_command": "enabled",  # Any non-empty value triggers local execution
                # Send conversation history for context
                "conversation_history": self.conversation_history,
                # Send directory context for better AI responses
                "directory_context": self.directory_context,
            }
            self.ws.send(json.dumps(request_data))

            # Receive and process messages sequentially
            current_tool: Optional[str] = None
            # Accumulate full assistant response for history
            full_assistant_response = []

            # Track how long we've been waiting
            query_start_time = time.time()
            console.print("[bold #7B89EE]→ Thinking...[/bold #7B89EE]")
            messages_received = 0
            first_response_received = False
            warned_about_delay = False

            while True:
                try:
                    # Check if we've been waiting too long without any response
                    if not first_response_received and not warned_about_delay:
                        elapsed = time.time() - query_start_time
                        if elapsed > 5.0:  # 5 seconds without response
                            console.print(
                                f"[dim]Still waiting for backend response ({int(elapsed)}s)...[/dim]"
                            )
                            warned_about_delay = True

                    # Set socket timeout for receive
                    self.ws.sock.settimeout(30.0)
                    raw_message = self.ws.recv()
                    messages_received += 1

                    if not first_response_received:
                        first_response_received = True

                    # Handle empty or whitespace-only messages
                    if not raw_message or not raw_message.strip():
                        if self.verbose:
                            console.print("[dim]Received empty message, continuing...[/dim]")
                        continue

                    # Parse JSON message
                    try:
                        message = json.loads(raw_message)
                    except json.JSONDecodeError as e:
                        if self.verbose:
                            console.print(f"[dim]Failed to parse message: {e}[/dim]")
                            console.print(
                                f"[dim]Raw message (first 100 chars): {raw_message[:100]}[/dim]"
                            )
                        # Skip malformed messages and continue
                        continue

                    msg_type = message.get("type")

                    if self.verbose:
                        console.print(f"[dim]← {msg_type}[/dim]")

                    if msg_type == "session":
                        self.session_id = message.get("session_id")
                        if self.verbose:
                            console.print(f"[dim]Session: {self.session_id}[/dim]")

                    elif msg_type == "text":
                        content = message.get("content", "")
                        if content:
                            if messages_received == 1:
                                console.print("[dim]Backend is responding…[/dim]")
                            console.print(Markdown(content))
                            full_assistant_response.append(content)

                    elif msg_type == "thinking" and self.verbose:
                        thinking_title = Text()
                        thinking_title.append("Generating response...", style="bold yellow")
                        thinking_panel = Panel(
                            message.get("content", ""),
                            title=thinking_title,
                            border_style="yellow",
                            padding=(1, 2),
                        )
                        console.print(thinking_panel)

                    elif msg_type == "tool_use":
                        tool_name = message.get("tool_name", "")
                        tool_input = message.get("tool_input", {})
                        friendly_tool_name = format_mcp_tool_name(tool_name)
                        current_tool = friendly_tool_name

                        compact_text = format_tool_input_compact(friendly_tool_name, tool_input)
                        tool_panel = Panel(
                            compact_text,
                            box=box.SIMPLE,
                            border_style="#7B89EE",
                            padding=(0, 1),
                            expand=False,
                        )
                        console.print(tool_panel)

                    elif msg_type == "tool_result":
                        is_error = message.get("is_error", False)
                        output = message.get("content", "")
                        tool_name = message.get("tool_name") or current_tool or "Tool"

                        compact_result = format_tool_result_compact(
                            tool_name,
                            output,
                            is_error,
                            max_lines=COMPACT_PREVIEW_LINES,
                        )
                        tool_result_panel = Panel(
                            compact_result,
                            box=box.SIMPLE,
                            border_style="green" if not is_error else "red",
                            padding=(0, 1),
                            expand=False,
                        )
                        friendly_name = format_mcp_tool_name(tool_name)

                        first_line = (output or "").splitlines()[0] if output else ""
                        preview = first_line[:60] + ("…" if len(first_line) > 60 else "")
                        log_line = Text(
                            f"{friendly_name}: {'error' if is_error else 'ok'}"
                            + (f" — {preview}" if preview else ""),
                            style="red" if is_error else "dim",
                        )
                        console.print(log_line)
                        console.print(tool_result_panel)

                    elif msg_type == "complete":
                        status = message.get("status", "unknown")
                        total_time = int(time.time() - query_start_time)
                        if status != "success":
                            console.print(f"[bold red]Response ended with status: {status}[/bold red]")
                        elif not full_assistant_response:
                            console.print("[dim]Seqera AI completed with no direct response.[/dim]")
                        console.print(f"[dim]Completed in {total_time}s.[/dim]")

                        # Store conversation in history for context in next query
                        self.conversation_history.append({"role": "user", "content": query})
                        if full_assistant_response:
                            self.conversation_history.append(
                                {"role": "assistant", "content": "".join(full_assistant_response)}
                            )

                        break

                    elif msg_type == "execute_local":
                        command = message.get("command", "")
                        request_id = message.get("request_id", "")
                        tool_name = message.get("tool_name", "")
                        tool_input = message.get("tool_input", {})

                        if self.verbose:
                            formatted_tool_name = format_mcp_tool_name(tool_name) if tool_name else ""
                            display_text = formatted_tool_name if tool_name else command[:100]
                            console.print(f"[dim]Executing locally: {display_text}[/dim]")

                        try:
                            result = self.execute_local_command(
                                command,
                                tool_name=tool_name,
                                tool_input=tool_input,
                            )
                        except SessionInterrupt:
                            console.print("\n[yellow]Session interrupted by user.[/yellow]\n")
                            return

                        response_data = {
                            "type": "execute_local_result",
                            "request_id": request_id,
                            "result": result,
                            "approval_mode": self.approval_mode,
                        }
                        self.ws.send(json.dumps(response_data))

                    elif msg_type == "error":
                        error_content = message.get("content", "Unknown error")
                        transient_errors = [
                            "Token validation failed",
                            "Authentication token required",
                            "No Authorization header",
                        ]
                        is_transient = any(te in error_content for te in transient_errors)
                        if is_transient:
                            self.ws = None
                            raise ConnectionError(error_content)
                        console.print(f"[bold red]Error: {error_content}[/bold red]")
                        break

                except websocket.WebSocketConnectionClosedException as e:
                    # Connection closed by server - mark for reconnection and raise for retry
                    if self.verbose:
                        console.print("[dim]Connection closed by server[/dim]")
                    self.ws = None
                    raise ConnectionError(f"Connection closed by server: {e}")
                except websocket.WebSocketTimeoutException:
                    elapsed = int(time.time() - query_start_time)
                    if messages_received == 0:
                        self.ws = None
                        raise ConnectionError(f"Backend timeout - no response after {elapsed}s")
                    else:
                        console.print(
                            f"\n[bold yellow]⚠️  Backend stopped responding (timeout after {elapsed}s)[/bold yellow]"
                        )
                        console.print(
                            f"[dim]Received {messages_received} message(s) before timeout.[/dim]"
                        )
                        console.print(
                            "[dim]The backend may still be processing. Check backend logs.[/dim]"
                        )
                        break

            # Keep connection open for next query

        except websocket.WebSocketConnectionClosedException as e:
            # Server closed connection - convert to ConnectionError for retry
            self.ws = None
            raise ConnectionError(f"Connection lost: {e}")
        except websocket.WebSocketTimeoutException as e:
            # Timeout - convert to ConnectionError for retry
            self.ws = None
            raise ConnectionError(f"Connection timeout: {e}")
        except websocket.WebSocketException as e:
            # Other WebSocket error - convert to ConnectionError for retry
            self.ws = None
            raise ConnectionError(f"WebSocket error: {e}")
        except ConnectionError:
            # Already a ConnectionError - propagate for retry
            self.ws = None
            raise
        except SessionInterrupt:
            # User interrupted - propagate without modifying connection
            raise
        except Exception:
            # Unexpected error - close connection and propagate
            self.ws = None
            raise


def get_latest_version():
    pypi_package_name = os.getenv("SEQERA_AI_CLI_PYPI_PACKAGE_NAME", "seqera")
    try:
        response = requests.get(f"https://pypi.org/pypi/{pypi_package_name}/json", timeout=1)
        data = response.json()
        return data.get("info", {}).get("version")
    except:
        return None

def print_banner(cwd: Optional[str] = None, version: Optional[str] = None):
    """Print the CLI banner."""
    import os

    # Get current directory for display
    if cwd is None:
        cwd = os.getcwd()

    # Use ~ for home directory
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        display_dir = "~" + cwd[len(home) :]
    else:
        display_dir = cwd

    banner_content = Text()
    banner_content.append("✨ ", style="bold #7B89EE")
    banner_content.append("Seqera AI", style="bold #7B89EE")

    if version:
        banner_content.append(f" v{version}", style="dim #7B89EE")

    if (latest_version := get_latest_version()) and (version != latest_version):
        banner_content.append(" (new version ", style="#7B89EE")
        banner_content.append(f"v{latest_version}", style="bold #7B89EE")
        banner_content.append(" available)", style="#7B89EE")



    banner_content.append("\n")
    banner_content.append("📁 ", style="dim")
    banner_content.append(display_dir, style="italic #A0A0A0")

    banner_content.append("\n\n")
    banner_content.append(
        "Helps you generate, debug, and optimize your workflows.", style="dim"
    )
    banner_content.append("\n")
    banner_content.append(
        "Beta – share feedback: https://feedback.seqera.io/", style="dim"
    )

    banner_content.append("\n\n")
    banner_content.append("Start with some ideas:", style="dim")
    banner_content.append("\n  • ", style="dim")
    banner_content.append("Set up nf-core/rnaseq pipeline", style="italic #A0A0A0")
    banner_content.append("\n  • ", style="dim")
    banner_content.append("/debug", style="bold #7B89EE")
    banner_content.append(" - Check pipeline syntax", style="italic #A0A0A0")
    banner_content.append("\n  • ", style="dim")
    banner_content.append("/schema", style="bold #7B89EE")
    banner_content.append(" - Generate Nextflow schema", style="italic #A0A0A0")
    banner_content.append("\n  • ", style="dim")
    banner_content.append("/", style="bold #7B89EE")
    banner_content.append(" - Show all available commands", style="italic #A0A0A0")
    banner_content.append("\n\n")
    # Beta warning
    banner_content.append("Beta version", style="bold yellow")
    banner_content.append(" - AI can make mistakes.\n", style="dim")

    console.print(
        Panel(
            banner_content,
            border_style="#7B89EE",
            box=box.ROUNDED,
            expand=False,
            padding=(0, 2),
        )
    )
    console.print()


def get_backend_url(url_arg: Optional[str]) -> str:
    """
    Get backend URL from arguments or environment.

    Args:
        url_arg: URL from command line argument

    Returns:
        Backend URL
    """
    if url_arg:
        return url_arg

    # Production default; override with SEQERA_AI_BACKEND_URL env var or --backend flag
    return os.getenv("SEQERA_AI_BACKEND_URL", "https://intern.seqera.io")


def resolve_approval_mode(flag_value: Optional[str]) -> tuple[str, Optional[str]]:
    """
    Resolve the approval mode using CLI flag (defaults to 'default').

    Args:
        flag_value: Value provided on the CLI flag

    Returns:
        Tuple of (approval_mode, source_description)
    """
    if flag_value:
        return flag_value.lower(), "flag"

    return "default", None


def print_landing_screen(version: str = __version__):
    """Print the Seqera CLI landing screen with branded gradient border."""

    # Clean, professional title
    banner_text = Text()
    banner_text.append("Seqera CLI", style="bold white")
    banner_text.append(f" v{version}", style="dim")

    if (latest_version := get_latest_version()) and (version != latest_version):
        banner_text.append(" (new version ", style="dim")
        banner_text.append(f"v{latest_version}", style="bold white")
        banner_text.append(" available)", style="dim")

    content = Text()
    content.append("Welcome to ", style="")
    content.append("Seqera CLI (beta)", style="bold white")
    content.append("\n\n", style="")

    # Commands
    content.append("Available commands:\n\n", style="dim")
    content.append("  seqera ", style="")
    content.append("ai", style="bold white")
    content.append("  Start the AI assistant for workflow management\n", style="dim")
    content.append("\n", style="")
    content.append("For more information, visit: ", style="dim")
    content.append("https://seqera.io", style="bold white underline")

    # Create gradient border effect using colored segments
    border_top = Text()
    border_top.append("▀" * 16, style="#1DBEAE")  # Teal
    border_top.append("▀" * 16, style="#FF6B3D")  # Orange
    border_top.append("▀" * 16, style="#FF8A7A")  # Coral
    border_top.append("▀" * 16, style="#4A90E2")  # Blue

    border_bottom = Text()
    border_bottom.append("▄" * 16, style="#1DBEAE")  # Teal
    border_bottom.append("▄" * 16, style="#FF6B3D")  # Orange
    border_bottom.append("▄" * 16, style="#FF8A7A")  # Coral
    border_bottom.append("▄" * 16, style="#4A90E2")  # Blue

    console.print(border_top)
    console.print(
        Panel(
            Group(banner_text, content),
            border_style="white",
            box=box.ROUNDED,
            expand=False,
            padding=(1, 2),
        )
    )
    console.print(border_bottom)
    console.print()


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def seqera(ctx: click.Context):
    """
    Seqera CLI - Command-line tools for Seqera Platform.

    Use 'seqera ai' to start the AI assistant.
    """
    if ctx.invoked_subcommand is None:
        print_landing_screen(__version__)


@seqera.command(name="ai")
@click.argument("query", required=False)
@click.option(
    "-t",
    "--token",
    help="Seqera Platform access token override for testing/CI (use `seqera login` for normal use)",
)
@click.option(
    "-b",
    "--backend",
    envvar="SEQERA_AI_BACKEND_URL",
    help="Backend server URL (default: https://intern.seqera.io)",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=True,
    help="Start interactive chat mode (default)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output with tool execution details",
)
@click.option(
    "-w",
    "--workdir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Working directory for agent operations (default: current directory)",
)
@click.option(
    "-a",
    "--approval-mode",
    type=click.Choice(APPROVAL_MODE_CHOICES, case_sensitive=False),
    help="Approval mode for local command execution (default: 'default')",
)
def seqera_ai(
    query: str,
    token: str,
    backend: str,
    interactive: bool,
    verbose: bool,
    workdir: str,
    approval_mode: Optional[str],
):
    """
    Seqera AI - Terminal assistant for bioinformatics and workflow management.

    Start the AI assistant (default) or use subcommands for authentication.

    Examples:

        # Interactive mode (default)
        seqera ai

        # With token
        seqera ai --token YOUR_TOKEN

        # Single query
        seqera ai "List my running workflows" --token YOUR_TOKEN

        # With working directory
        seqera ai -w /path/to/pipeline --token YOUR_TOKEN

    Reserved Commands (work in both CLI and interactive mode):
        /                           Show available commands
        /help-community             Visit: https://community.seqera.io/ to get community support
        /feedback                   Visit: https://feedback.seqera.io/ to provide feedback
        /stickers                   Open Seqera stickers store on Sticker Mule
        /credit                     Check your remaining Seqera AI credit balance
        /schema                     Generate Nextflow schema
        /debug                      Run pipeline diagnostics
        /migrate-from-wdl           Migrate from WDL to Nextflow
        /migrate-from-snakemake     Migrate from Snakemake to Nextflow
        /write-nf-test              Write nf-tests for untested code
        /debug-last-run             Debug last local run
        /debug-last-run-on-seqera   Debug last Seqera Platform run
        /history                    Display conversation history
    """

    # Get configuration first to determine cwd for banner
    cwd = workdir if workdir else os.getcwd()
    print_banner(cwd, __version__)

    try:
        # Get configuration
        token_provider = resolve_token_provider(token, verbose=verbose)
        backend_url = get_backend_url(backend)
        resolved_mode, mode_source = resolve_approval_mode(approval_mode)

        # Show working directory
        if verbose:
            console.print(f"[dim]Working directory: {cwd}[/dim]")

        # Create client
        client = SeqeraClient(
            backend_url,
            token_provider,
            verbose,
            cwd=cwd,
            approval_mode=resolved_mode,
        )

        # Show approval mode status only in verbose mode
        if verbose:
            mode_origin = f"(from {mode_source})" if mode_source else "(default)"
            console.print(
                f"{client.get_approval_status()} {mode_origin}. "
                "[dim]Change now with /approval; start with --approval-mode to pick the initial mode for this run.[/dim]"
            )

        # Check backend health
        if verbose:
            console.print(f"[dim]Connecting to backend: {backend_url}[/dim]")
        if not client.check_health():
            console.print("[bold red]Backend server is not responding![/bold red]")
            console.print("\n[yellow]Please ensure the backend is running.[/yellow]")
            console.print(f"[dim]Expected backend URL: {backend_url}[/dim]")
            sys.exit(1)

        if verbose:
            console.print("[bold green]✓[/bold green] Connected to backend\n")

        # Interactive or single query mode
        try:
            if query:
                # Single query mode
                if not handle_reserved_command(query, client):
                    client.send_query_streaming(query)
                console.print("\n[bold green]✓[/bold green] Query completed\n")
            else:
                # Interactive mode (default)
                run_interactive(client)
        finally:
            # Always cleanup WebSocket connection on exit
            client.cleanup()

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        sys.exit(1)


@seqera.command()
@click.option(
    "--device",
    "use_device_flow",
    is_flag=True,
    help="Use the Auth0 device-code flow (for headless servers).",
)
def login(use_device_flow: bool):
    """
    Authenticate the Seqera AI CLI via Auth0 and store a refresh token securely.
    """

    manager = get_auth_manager(console=console)
    try:
        metadata = manager.login(use_device_flow=use_device_flow)
    except AuthError as exc:
        raise click.ClickException(str(exc)) from exc

    user = metadata.get("user", {}) if metadata else {}
    identifier = (
        user.get("email") or user.get("name") or user.get("sub") or "Seqera user"
    )
    status = metadata.get("status")
    if status == "already_logged_in":
        console.print(
            f"[bold green]✓ Already logged in; refreshed session for {identifier}[/bold green]"
        )
    else:
        console.print(f"[bold green]✓ Logged in as {identifier}[/bold green]")


@seqera.command()
@click.option(
    "--all",
    "clear_all",
    is_flag=True,
    help="Remove refresh tokens for every stored profile (not just the current domain).",
)
def logout(clear_all: bool):
    """
    Sign out of the Seqera AI CLI and remove stored credentials.
    """

    manager = get_auth_manager(console=console)
    try:
        manager.logout(clear_all=clear_all)
    except AuthError as exc:
        raise click.ClickException(str(exc)) from exc

    scope = "all profiles" if clear_all else "current profile"
    console.print(f"[bold green]✓ Logged out ({scope}).[/bold green]")


@seqera.command(name="status")
def auth_status():
    """
    Show Auth0 session details for the Seqera AI CLI.
    """

    manager = get_auth_manager(console=console)
    info = manager.status()

    metadata = info.get("metadata") or {}
    user = metadata.get("user") or {}
    email = user.get("email") or user.get("name") or user.get("sub") or "Unknown"
    lines = [
        f"Profile: [bold]{info.get('profile')}[/bold]",
        f"Domain: {info.get('domain')}",
        f"Audience: {info.get('audience')}",
        f"Client ID: {info.get('client_id') or 'not configured'}",
        f"Logged in: {'yes' if info.get('logged_in') else 'no'}",
    ]

    if info.get("logged_in"):
        expires_in = info.get("seconds_until_expiry")
        if expires_in is not None:
            lines.append(f"Access token expires in: {expires_in} seconds")
        last_login = metadata.get("last_login")
        if last_login:
            ts = datetime.fromtimestamp(last_login)
            lines.append(f"Last login: {ts.isoformat(timespec='seconds')}")
        if metadata.get("method"):
            lines.append(f"Last method: {metadata['method']}")
        lines.append(f"User: {email}")
    else:
        lines.append("No refresh token stored. Run `seqera login`.")

    console.print(Panel.fit("\n".join(lines), title="Auth status"))


def run_interactive(client: SeqeraClient):
    """
    Run interactive chat mode.

    Args:
        client: SeqeraClient instance
    """
    console.print(
        "[dim]Type your message and press Enter. Type 'exit', 'quit', or press Ctrl+C to exit.[/dim]"
    )
    console.print("[dim]Type '/' for commands, '@' to reference a file.[/dim]\n")

    # Try to use prompt_toolkit for better UX, fall back to basic input if not available
    try:
        from prompt_toolkit import prompt
        from prompt_toolkit.styles import Style
        from prompt_toolkit.formatted_text import HTML
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.keys import Keys
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.completion import Completer, Completion

        class CombinedCompleter(Completer):
            """Completer for slash commands (/) and file paths (@)."""

            def __init__(self, cwd: str):
                self.cwd = cwd

            def _get_files_recursive(self, max_depth: int = 5) -> list[str]:
                """Get all files recursively from cwd.

                Returns list of relative file paths (no directories).
                """
                results = []

                def collect_files(current_dir: Path, depth: int):
                    if depth > max_depth or len(results) >= 200:
                        return

                    try:
                        items = sorted(
                            current_dir.iterdir(), key=lambda x: x.name.lower()
                        )
                        for item in items:
                            if len(results) >= 200:
                                break

                            # Skip hidden files/dirs
                            if item.name.startswith("."):
                                continue

                            if item.is_dir():
                                # Recurse into directories
                                collect_files(item, depth + 1)
                            else:
                                # Only add files, not directories
                                rel_path = str(item.relative_to(self.cwd))
                                results.append(rel_path)
                    except PermissionError:
                        pass

                collect_files(Path(self.cwd), 0)
                return results

            def get_completions(self, document, complete_event):
                text = document.text_before_cursor

                # Handle slash commands
                if text.startswith("/"):
                    # Get the command portion (everything from / to end or first space)
                    parts = text.split(maxsplit=1)
                    cmd_part = parts[0] if parts else text

                    # If user just typed "/", show all commands
                    # Otherwise filter commands that match the typed prefix
                    for cmd, description in RESERVED_COMMANDS.items():
                        if cmd == "/":
                            continue  # Skip the "/" command itself
                        if cmd_part == "/" or cmd.startswith(cmd_part):
                            yield Completion(
                                cmd,
                                start_position=-len(cmd_part),
                                display=cmd,
                                display_meta=description,
                            )
                    return

                # Handle @ file completions - find the last @ in the text
                at_index = text.rfind("@")
                if at_index == -1:
                    return

                # Get the file path portion after @
                file_part = text[at_index + 1 :]

                # Get all files recursively
                files = self._get_files_recursive()

                # Filter files that match the typed text (case-insensitive)
                # Match against: full path, filename, or any part of path
                file_part_lower = file_part.lower()

                for rel_path in files:
                    rel_path_lower = rel_path.lower()
                    filename_lower = rel_path.split("/")[-1].lower()

                    # Match if:
                    # 1. No filter typed yet (show all)
                    # 2. Full path starts with the typed text (e.g., @src/ matches src/foo.py)
                    # 3. Filename starts with the typed text (e.g., @cli matches src/seqera_ai/cli.py)
                    # 4. Typed text appears anywhere in the path (e.g., @seqera matches src/seqera_ai/cli.py)
                    if file_part_lower:
                        if not (
                            rel_path_lower.startswith(file_part_lower)
                            or filename_lower.startswith(file_part_lower)
                            or file_part_lower in rel_path_lower
                        ):
                            continue

                    # Calculate start position from the @ symbol
                    start_pos = -(len(file_part) + 1)  # +1 for the @ symbol

                    yield Completion(
                        rel_path,
                        start_position=start_pos,
                        display=rel_path,
                    )

        style = Style.from_dict(
            {
                "frame.border": "dim",
                "prompt": "#7B89EE bold",
                "bottom-toolbar": "#ffffff bg:#545555",
                "completion-menu.completion": "bg:#3d3d3d #ffffff",
                "completion-menu.completion.current": "bg:#7B89EE #ffffff",
                "completion-menu.meta.completion": "bg:#3d3d3d #888888",
                "completion-menu.meta.completion.current": "bg:#7B89EE #dddddd",
            }
        )
        # Create key bindings for clearing input
        kb = KeyBindings()

        @kb.add(Keys.ControlU)
        def clear_input(event):
            """Clear the current input line."""
            event.app.current_buffer.text = ""

        # Create history for up/down arrow navigation
        history = InMemoryHistory()

        # Create the combined completer for / commands and @ file paths
        command_completer = CombinedCompleter(client.cwd)

        # Format current directory for display
        def format_cwd_for_display(cwd: str) -> str:
            """Format current working directory for display (use ~ for home)."""
            import os

            home = os.path.expanduser("~")
            if cwd.startswith(home):
                return "~" + cwd[len(home) :]
            return cwd

        display_cwd = format_cwd_for_display(client.cwd)

        while True:
            try:
                console.print("─" * console.width, style="dim")
                # Show current directory above input
                console.print(f"[dim]{display_cwd}[/dim]")
                user_input = prompt(
                    [("class:prompt", "> ")],
                    style=style,
                    placeholder="Describe a task or use / for commands",
                    key_bindings=kb,
                    history=history,
                    completer=command_completer,
                    complete_while_typing=True,
                    reserve_space_for_menu=5,
                    bottom_toolbar=HTML(
                        "<b>Ctrl+c</b> to Exit, <b>↑/↓</b> for history, <b>/</b> commands, <b>@</b> files"
                    ),
                ).strip()
                # Print separator line below input
                console.print("─" * console.width, style="dim")

                if user_input.lower() in ["exit", "quit", "bye"]:
                    console.print("\n[#7B89EE]Goodbye! 👋[/#7B89EE]")
                    break

                if user_input.lower() in ["/"]:
                    show_available_commands()
                    continue

                if not user_input:
                    continue

                # Check if it's a reserved command
                if not handle_reserved_command(user_input, client):
                    # Regular query
                    client.send_query_streaming(user_input)
                console.print()  # Add spacing

            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted by user[/yellow]")
                break

            except EOFError:
                console.print("\n\n[#7B89EE]Goodbye! 👋[/#7B89EE]")
                break

            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")

    except ImportError:
        # Fall back to basic console.input if prompt_toolkit is not available
        # Format current directory for display
        import os

        home = os.path.expanduser("~")
        if client.cwd.startswith(home):
            display_cwd = "~" + client.cwd[len(home) :]
        else:
            display_cwd = client.cwd

        while True:
            try:
                console.print(f"[dim]{display_cwd}[/dim]")
                user_input = console.input("[dim]> [/dim]").strip()

                if user_input.lower() in ["exit", "quit", "bye"]:
                    console.print("\n[#7B89EE]Goodbye! 👋[/#7B89EE]")
                    break

                if user_input.lower() in ["/"]:
                    show_available_commands()
                    continue

                if not user_input:
                    continue

                # Check if it's a reserved command
                if not handle_reserved_command(user_input, client):
                    # Regular query
                    client.send_query_streaming(user_input)
                console.print()  # Add spacing

            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted by user[/yellow]")
                break

            except EOFError:
                console.print("\n\n[#7B89EE]Goodbye! 👋[/#7B89EE]")
                break

            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")


# For backward compatibility and direct invocation (deprecated - use 'seqera ai' instead)
def cli():
    """Entry point for the seqera-ai command (deprecated - use 'seqera ai' instead)."""
    seqera_ai()


def cli_seqera():
    """Entry point for the seqera command."""
    seqera()


if __name__ == "__main__":
    seqera()
