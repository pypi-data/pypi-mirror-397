"""Command input widget with history and autocompletion."""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Input, Static

from kryten_shell.commands.base import CommandRegistry
from kryten_shell.commands.builtins import register_builtin_commands
from kryten_shell.commands.parser import CommandParser

if TYPE_CHECKING:
    from kryten_shell.app import KrytenShellApp
    from kryten_shell.client import KrytenClientWrapper

logger = logging.getLogger(__name__)


class CommandInput(Horizontal):
    """Command input widget with prompt, history, and autocompletion.

    Features:
    - Natural syntax command parsing
    - Command history (up/down arrows)
    - Persistent history across sessions
    - Tab completion for commands
    """

    DEFAULT_CSS = """
    CommandInput {
        height: 3;
        dock: bottom;
        background: #073642;
        padding: 0 1;
        layout: horizontal;
    }

    #command-prompt {
        width: auto;
        height: 1;
        color: #2aa198;
        text-style: bold;
        padding: 0 1 0 0;
    }

    #command-input-field {
        width: 1fr;
        height: 1;
        border: none;
        background: transparent;
        color: #839496;
        padding: 0;
    }

    #command-input-field:focus {
        border: none;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the command input."""
        super().__init__(*args, **kwargs)

        self._client: "KrytenClientWrapper | None" = None
        self._app_ref: "KrytenShellApp | None" = None

        # Command system
        self._registry = CommandRegistry()
        register_builtin_commands(self._registry)
        self._parser: CommandParser | None = None

        # History
        self._history: list[str] = []
        self._history_index: int = 0
        self._history_file: Path | None = None
        self._max_history: int = 1000

    def compose(self):
        """Compose the command input widgets."""
        yield Static("kryten>", id="command-prompt")
        yield Input(
            placeholder="Enter command (type 'help' for available commands)",
            id="command-input-field",
        )

    def on_mount(self) -> None:
        """Load history on mount."""
        self._load_history()

    def set_client(self, client: "KrytenClientWrapper") -> None:
        """Set the Kryten client.

        Args:
            client: The Kryten client wrapper.
        """
        self._client = client
        if self._app_ref:
            self._parser = CommandParser(self._registry, self._app_ref, client)

    def set_app_ref(self, app: "KrytenShellApp") -> None:
        """Set the application reference.

        Args:
            app: The main application.
        """
        self._app_ref = app
        if self._client:
            self._parser = CommandParser(self._registry, app, self._client)
        else:
            self._parser = CommandParser(self._registry, app)

        # Get history file from config
        if app.config.history_file:
            self._history_file = app.config.history_file
            self._max_history = app.config.max_history
            self._load_history()

    def focus(self) -> None:
        """Focus the input field."""
        input_field = self.query_one("#command-input-field", Input)
        input_field.focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission.

        Args:
            event: The input submitted event.
        """
        command_text = event.value.strip()

        if not command_text:
            return

        # Clear input
        input_field = self.query_one("#command-input-field", Input)
        input_field.value = ""

        # Add to history
        self._add_to_history(command_text)

        # Execute command
        if self._parser:
            result = await self._parser.execute(command_text)

            if result.message:
                # Log result to global output log (visible from any tab)
                if self._app_ref:
                    self._app_ref.log_output(result.message, error=not result.success)
                else:
                    # Fallback to notification
                    self.notify(result.message)

    def on_key(self, event) -> None:
        """Handle key events for history navigation.

        Args:
            event: The key event.
        """
        if event.key == "up":
            self._history_up()
            event.stop()
        elif event.key == "down":
            self._history_down()
            event.stop()
        elif event.key == "tab":
            # Run async completion
            self.run_worker(self._complete_async(), exclusive=True)
            event.stop()

    def _history_up(self) -> None:
        """Navigate up in history."""
        if not self._history:
            return

        if self._history_index > 0:
            self._history_index -= 1
            input_field = self.query_one("#command-input-field", Input)
            input_field.value = self._history[self._history_index]
            # Move cursor to end
            input_field.cursor_position = len(input_field.value)

    def _history_down(self) -> None:
        """Navigate down in history."""
        if not self._history:
            return

        input_field = self.query_one("#command-input-field", Input)

        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            input_field.value = self._history[self._history_index]
        else:
            self._history_index = len(self._history)
            input_field.value = ""

        input_field.cursor_position = len(input_field.value)

    async def _complete_async(self) -> None:
        """Tab completion for commands and arguments (async with fetching)."""
        if not self._parser:
            return

        input_field = self.query_one("#command-input-field", Input)
        partial = input_field.value

        # Use async completions for better read-ahead
        completions = await self._parser.get_completions_async(partial)

        if len(completions) == 1:
            # Check if we're completing a command or an argument
            if " " in partial:
                # Completing an argument - preserve command prefix
                parts = partial.rsplit(" ", 1)
                prefix = parts[0] + " "
                input_field.value = prefix + completions[0] + " "
            else:
                # Completing a command name
                input_field.value = completions[0] + " "
            input_field.cursor_position = len(input_field.value)
        elif len(completions) > 1:
            # Find common prefix for multiple completions
            common = completions[0]
            for c in completions[1:]:
                while not c.lower().startswith(common.lower()):
                    common = common[:-1]
                    if not common:
                        break
            
            # If there's a common prefix longer than what we typed, complete to it
            if " " in partial:
                parts = partial.rsplit(" ", 1)
                prefix = parts[0] + " "
                current_arg = parts[1] if len(parts) > 1 else ""
                if len(common) > len(current_arg):
                    input_field.value = prefix + common
                    input_field.cursor_position = len(input_field.value)
            else:
                if len(common) > len(partial):
                    input_field.value = common
                    input_field.cursor_position = len(input_field.value)
            
            # Show completions in status
            self.notify(f"Completions: {', '.join(completions[:10])}")

    def _add_to_history(self, command: str) -> None:
        """Add a command to history.

        Args:
            command: The command string.
        """
        # Don't add duplicates in a row
        if self._history and self._history[-1] == command:
            return

        self._history.append(command)

        # Trim to max size
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Reset index to end
        self._history_index = len(self._history)

        # Save history
        self._save_history()

    def _load_history(self) -> None:
        """Load command history from file."""
        if not self._history_file or not self._history_file.exists():
            return

        try:
            with open(self._history_file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._history = data[-self._max_history:]
                    self._history_index = len(self._history)
        except Exception as e:
            logger.warning(f"Failed to load history: {e}")

    def _save_history(self) -> None:
        """Save command history to file."""
        if not self._history_file:
            return

        try:
            self._history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._history_file, "w") as f:
                json.dump(self._history, f)
        except Exception as e:
            logger.warning(f"Failed to save history: {e}")
