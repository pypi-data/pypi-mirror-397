"""Rendering helpers for streaming CLI output."""

from __future__ import annotations

import hashlib
from typing import Callable, Dict, Optional

from rich.console import Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text


def _hash_content(value: str) -> str:
    """Stable hash for deduping repeated tool output."""
    return hashlib.sha1(value.encode("utf-8"), usedforsecurity=False).hexdigest()


class StreamRenderState:
    """
    Stateful renderer that keeps CLI output clean and deterministic.

    Responsibilities:
    - Keep at most one active spinner (bottom of the stack)
    - Reuse a single panel per tool and dedupe identical payloads
    - Batch updates (mark dirty, then render once per message)
    """

    def __init__(self, new_spinner_panel: Callable[[], Spinner]):
        self.new_spinner_panel = new_spinner_panel
        self.blocks: list = []
        self.current_slot: Optional[int] = None
        self.stream_text = ""
        self.response_blocks: list[int] = []
        self.response_texts: Dict[int, str] = {}
        self.has_text = False
        self.tool_panels: Dict[str, Dict[str, object]] = {}
        self.todo_panel_index: Optional[int] = None
        self.todo_hash: Optional[str] = None
        self.action_log: list[Text] = []
        self.max_action_log = 8
        self.dirty = False
        self.live: Optional[Live] = None

        self.ensure_slot()

    @property
    def group(self) -> Group:
        return Group(*self.blocks)

    def attach_live(self, live: Live) -> None:
        self.live = live

    def ensure_slot(self) -> None:
        if self.current_slot is not None and self.current_slot < len(self.blocks):
            return
        spinner = self.new_spinner_panel()
        self.blocks.append(spinner)
        self.current_slot = len(self.blocks) - 1
        self.dirty = True

    def update_spinner_text(self, text: str) -> None:
        self.ensure_slot()
        self.blocks[self.current_slot] = Spinner("dots", text=text)
        self.dirty = True

    def set_text(self, content: str) -> None:
        if not content:
            return
        self.has_text = True
        self.ensure_slot()
        slot = self.current_slot
        self.stream_text += content
        self.blocks[slot] = Markdown(self.stream_text)
        if slot not in self.response_blocks:
            self.response_blocks.append(slot)
        self.response_texts[slot] = self.stream_text
        self.current_slot = None
        self.ensure_slot()
        self.dirty = True

    def add_thinking(self, panel: Panel) -> None:
        self.blocks.append(panel)
        self.dirty = True

    def _insert_before_spinner(self, renderable) -> int:
        """
        Insert a renderable right before the spinner (current slot).
        Returns the index where it was inserted.
        """
        if self.current_slot is None:
            self.blocks.append(renderable)
            return len(self.blocks) - 1

        self.blocks.insert(self.current_slot, renderable)
        # Spinner moves down one slot
        self.current_slot += 1
        return self.current_slot - 1

    def add_action_log(self, line: Text) -> None:
        """
        Insert a one-line action log above the Todo panel (or before spinner if Todo absent).
        """
        # Ensure the log line is at most one line visually
        line = Text(line.plain.split("\n")[0][:200], style=line.style or "dim")

        insert_at = self.todo_panel_index
        if insert_at is None:
            insert_at = self.current_slot

        if insert_at is None:
            self.blocks.append(line)
            insert_at = len(self.blocks) - 1
        else:
            self.blocks.insert(insert_at, line)
            if self.todo_panel_index is not None:
                self.todo_panel_index += 1
            if self.current_slot is not None and insert_at <= self.current_slot:
                self.current_slot += 1

        self.action_log.append(line)
        if len(self.action_log) > self.max_action_log:
            # Remove the oldest log from blocks
            oldest = self.action_log.pop(0)
            try:
                idx = self.blocks.index(oldest)
                self.blocks.pop(idx)
                # Adjust indices after removal
                if self.todo_panel_index is not None and idx < self.todo_panel_index:
                    self.todo_panel_index -= 1
                if self.current_slot is not None and idx < self.current_slot:
                    self.current_slot -= 1
            except ValueError:
                pass

        self.dirty = True

    def record_tool_use(self, tool_name: str, panel: Panel) -> None:
        name = tool_name or "Tool"
        if self.current_slot is not None and self.current_slot < len(self.blocks):
            target_index = self.current_slot
            self.blocks[target_index] = panel
        else:
            self.blocks.append(panel)
            target_index = len(self.blocks) - 1
        self.tool_panels[name] = {"index": target_index, "last_hash": None}
        self.current_slot = None
        self.ensure_slot()
        self.dirty = True

    def record_tool_result(self, tool_name: str, compact_content, panel: Panel) -> None:
        name = tool_name or "Tool"
        content_str = (
            compact_content.plain if hasattr(compact_content, "plain") else str(compact_content)
        )
        content_hash = _hash_content(content_str)
        state = self.tool_panels.get(name)
        if state and state.get("last_hash") == content_hash:
            return

        if state and isinstance(state.get("index"), int) and state["index"] < len(self.blocks):
            target_index = state["index"]
            self.blocks[target_index] = panel
        elif self.current_slot is not None and self.current_slot < len(self.blocks):
            target_index = self.current_slot
            self.blocks[target_index] = panel
        else:
            self.blocks.append(panel)
            target_index = len(self.blocks) - 1

        self.tool_panels[name] = {"index": target_index, "last_hash": content_hash}
        self.current_slot = None
        self.ensure_slot()
        self.dirty = True

    def record_todo_result(self, compact_content_text, panel: Panel) -> None:
        """
        Keep TodoWrite panel stable: always visible and updated, positioned above the spinner.
        """
        content_str = (
            compact_content_text.plain if hasattr(compact_content_text, "plain") else str(compact_content_text)
        )
        content_hash = _hash_content(content_str)

        if self.todo_hash == content_hash and self.todo_panel_index is not None:
            return

        if self.todo_panel_index is None:
            insert_at = self._insert_before_spinner(panel)
            self.todo_panel_index = insert_at
        else:
            if self.todo_panel_index < len(self.blocks):
                self.blocks[self.todo_panel_index] = panel
            else:
                self.todo_panel_index = self._insert_before_spinner(panel)

        self.todo_hash = content_hash
        self.dirty = True

    def finalize(
        self,
        status: str,
        empty_message: Text,
        error_message: Text,
    ) -> None:
        if status == "success":
            if self.has_text:
                for idx in self.response_blocks:
                    content = self.response_texts.get(idx)
                    if content:
                        self.blocks[idx] = Markdown(content)
            else:
                if self.current_slot is not None and self.current_slot < len(self.blocks):
                    self.blocks[self.current_slot] = empty_message
                else:
                    self.blocks.append(empty_message)
        else:
            if self.current_slot is not None and self.current_slot < len(self.blocks):
                self.blocks[self.current_slot] = error_message
            else:
                self.blocks.append(error_message)

        self.drop_trailing_spinner()
        self.current_slot = None
        self.dirty = True

    def block_count(self) -> int:
        return len(self.blocks)

    def trim_blocks(self, keep_from: int) -> None:
        if keep_from <= 0:
            return
        self.blocks[:] = self.blocks[keep_from:]

        self.response_blocks = [
            idx - keep_from for idx in self.response_blocks if idx >= keep_from
        ]
        self.response_texts = {
            idx - keep_from: value
            for idx, value in self.response_texts.items()
            if idx >= keep_from
        }

        new_tool_panels: Dict[str, Dict[str, object]] = {}
        for name, state in self.tool_panels.items():
            idx = state.get("index")
            if not isinstance(idx, int):
                continue
            new_idx = idx - keep_from
            if 0 <= new_idx < len(self.blocks):
                new_state = dict(state)
                new_state["index"] = new_idx
                new_tool_panels[name] = new_state
        self.tool_panels = new_tool_panels

        if self.current_slot is not None:
            self.current_slot = self.current_slot - keep_from
            if self.current_slot < 0 or self.current_slot >= len(self.blocks):
                self.current_slot = None

        self.dirty = True

    def reset_stream(self) -> None:
        self.stream_text = ""

    def refresh_spinner(self) -> None:
        self.ensure_slot()
        self.blocks[self.current_slot] = self.new_spinner_panel()
        self.dirty = True

    def drop_trailing_spinner(self) -> None:
        while self.blocks and isinstance(self.blocks[-1], Spinner):
            self.blocks.pop()

    def render(self) -> None:
        if not self.dirty or self.live is None:
            return
        self.live.update(self.group, refresh=True)
        self.dirty = False
