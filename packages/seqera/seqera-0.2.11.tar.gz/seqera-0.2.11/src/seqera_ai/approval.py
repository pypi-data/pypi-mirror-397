import logging
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)

# Valid approval modes
APPROVAL_MODE_CHOICES = ("basic", "default", "full")
APPROVAL_MODES = set(APPROVAL_MODE_CHOICES)

# Commands that are safe to auto-execute
SAFE_COMMANDS = {
    "cat",
    "date",
    "echo",
    "env",
    "head",
    "ls",
    "printenv",
    "pwd",
    "stat",
    "tail",
    "tree",
    "uptime",
    "whoami",
}

# Commands that should always require an approval prompt in full mode
DANGEROUS_COMMANDS = {
    "chmod",
    "chown",
    "dd",
    "kill",
    "killall",
    "mkfs",
    "mount",
    "pkill",
    "reboot",
    "rm",
    "shutdown",
    "sudo",
    "umount",
}

# Commands that typically modify files
FILE_EDIT_COMMANDS = {
    "chmod",
    "chown",
    "cp",
    "dd",
    "ln",
    "mkdir",
    "mv",
    "rm",
    "rmdir",
    "sed",
    "tee",
    "touch",
    "truncate",
}

REDIRECTION_TOKENS = {">", ">>", "1>", "1>>", "2>", "2>>"}
SEPARATOR_TOKENS = {"&&", "||", ";", "|"}


@dataclass
class ApprovalDecision:
    """Represents the outcome of an approval evaluation."""

    requires_prompt: bool
    reason: str


class ApprovalManager:
    """Encapsulates approval rules for local command execution."""

    def __init__(self, mode: str, workspace: str):
        self.mode = mode if mode in APPROVAL_MODES else "default"
        self.workspace = Path(workspace).resolve()

    def evaluate(self, command: str) -> ApprovalDecision:
        """
        Decide whether a command needs explicit approval before execution.

        Args:
            command: Raw shell command string.

        Returns:
            ApprovalDecision describing whether to prompt and why.
        """
        parts = self._split_command(command)
        base_cmd = parts[0].lower() if parts else ""

        is_safe = base_cmd in SAFE_COMMANDS
        is_dangerous = base_cmd in DANGEROUS_COMMANDS
        is_edit, edit_in_workspace = self._is_file_edit_in_workspace(parts, base_cmd)

        if is_edit:
            is_safe = False

        if self.mode == "basic":
            if is_safe:
                return ApprovalDecision(False, "safe_list")
            return ApprovalDecision(True, "basic_mode_requires_approval")

        if self.mode == "default":
            if is_safe:
                return ApprovalDecision(False, "safe_list")
            if is_dangerous:
                return ApprovalDecision(True, "dangerous_list")
            if is_edit and edit_in_workspace:
                return ApprovalDecision(False, "workspace_file_edit")
            if is_edit and not edit_in_workspace:
                return ApprovalDecision(True, "file_edit_outside_workspace")
            return ApprovalDecision(True, "non_safe_non_edit")

        # Full mode
        if is_dangerous:
            return ApprovalDecision(True, "dangerous_list")
        return ApprovalDecision(False, "full_mode_auto_execute")

    def _split_command(self, command: str) -> list[str]:
        try:
            return shlex.split(command, posix=True)
        except ValueError:
            # Fallback to simple split if shlex fails
            return command.split()

    def _is_file_edit_in_workspace(
        self, parts: list[str], base_cmd: str
    ) -> tuple[bool, bool]:
        # Determine if the command is likely to modify files
        has_redirection = any(token in REDIRECTION_TOKENS for token in parts)
        is_edit_command = base_cmd in FILE_EDIT_COMMANDS
        is_edit = has_redirection or is_edit_command

        if not is_edit:
            return False, False

        edit_paths = set(self._extract_edit_paths(parts, base_cmd))
        if not edit_paths:
            # We detected an editing command but couldn't find paths; require approval
            return True, False

        for path_str in edit_paths:
            if not self._is_within_workspace(path_str):
                return True, False

        return True, True

    def _extract_edit_paths(
        self, parts: list[str], base_cmd: str
    ) -> Iterable[str]:
        paths: list[str] = []

        # Capture redirection targets
        for idx, token in enumerate(parts):
            if token in REDIRECTION_TOKENS and idx + 1 < len(parts):
                paths.append(parts[idx + 1])

        # Capture positional arguments for known file editing commands
        if base_cmd in FILE_EDIT_COMMANDS:
            for token in parts[1:]:
                if token.startswith("-") or token in REDIRECTION_TOKENS | SEPARATOR_TOKENS:
                    continue
                paths.append(token)

        return paths

    def _is_within_workspace(self, path_str: str) -> bool:
        if not path_str:
            return False

        try:
            candidate = Path(path_str).expanduser()
        except RuntimeError:
            return False

        if not candidate.is_absolute():
            candidate = (self.workspace / candidate).resolve()
        else:
            candidate = candidate.resolve()

        try:
            candidate.relative_to(self.workspace)
            return True
        except ValueError:
            return False
