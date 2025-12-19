"""Main Kryten Shell TUI Application.

A simple command-driven interface for interacting with the Kryten ecosystem.
"""

import logging
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, RichLog

from kryten_shell.client import KrytenClientWrapper
from kryten_shell.config import ShellConfig
from kryten_shell.views.status import StatusBar
from kryten_shell.widgets.command_input import CommandInput

logger = logging.getLogger(__name__)

# Version from single source of truth
VERSION_FILE = Path(__file__).parent.parent / "VERSION"
try:
    VERSION = VERSION_FILE.read_text().strip()
except FileNotFoundError:
    VERSION = "0.0.0"


class KrytenShellApp(App):
    """The main Kryten Shell TUI application.

    A simple command-driven interface with:
    - Single output window for all command results
    - Command input with natural syntax
    - Status bar showing connection state
    """

    CSS_PATH = Path(__file__).parent / "theme.tcss"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("escape", "focus_command", "Command", show=False),
        Binding("f1", "show_help", "Help"),
        Binding("ctrl+l", "clear_output", "Clear"),
        Binding("ctrl+s", "screenshot", "Screenshot"),
    ]

    def __init__(
        self,
        config: ShellConfig | None = None,
        nats_host: str | None = None,
        nats_port: int | None = None,
        channel: str | None = None,
    ):
        """Initialize the Kryten Shell application.

        Args:
            config: Optional pre-loaded configuration.
            nats_host: Override NATS host from CLI.
            nats_port: Override NATS port from CLI.
            channel: Override channel from CLI.
        """
        super().__init__()

        # Set title with version
        self.title = f"Kryten Shell v{VERSION}"
        self.sub_title = ""

        # Load or use provided config
        self.config = config or ShellConfig.load()

        # Apply CLI overrides
        if nats_host:
            self.config.nats.host = nats_host
        if nats_port:
            self.config.nats.port = nats_port
        if channel:
            self.config.channel = channel

        # Client wrapper (initialized on mount)
        self.client: KrytenClientWrapper | None = None

        # Widget references
        self._output_log: RichLog | None = None
        self._status_bar: StatusBar | None = None
        self._command_input: CommandInput | None = None

    def compose(self) -> ComposeResult:
        """Compose the application UI."""
        yield Header()

        # Main output log - takes up most of the screen
        self._output_log = RichLog(
            highlight=True,
            markup=True,
            wrap=True,
            auto_scroll=True,
            id="output-log",
        )
        yield self._output_log

        # Command input at the bottom
        self._command_input = CommandInput(id="command-input")
        yield self._command_input

        # Status bar
        self._status_bar = StatusBar(id="status-bar")
        yield self._status_bar

        yield Footer()

    async def on_mount(self) -> None:
        """Handle application mount - initialize connections."""
        logger.info(f"Kryten Shell v{VERSION} starting...")

        # Show welcome message
        self.log_output(f"Kryten Shell v{VERSION}")
        self.log_output("Type 'help' for available commands, Ctrl+S to save screenshot")
        self.log_output("")

        # Initialize the Kryten client
        self.client = KrytenClientWrapper(self.config, self)

        # Pass client to widgets
        if self._status_bar:
            self._status_bar.set_client(self.client)
        if self._command_input:
            self._command_input.set_client(self.client)
            self._command_input.set_app_ref(self)

        # Attempt connection
        self.log_output(f"Connecting to {self.config.nats.url}...")
        connected = await self.client.connect()

        if connected:
            self.log_output("Connected to NATS", style="green")

            # Auto-discover channels if no channel specified
            if not self.config.channel:
                await self._auto_discover_channel()
        else:
            self.log_output("Failed to connect to NATS", style="red", error=True)

        # Focus the command input
        if self._command_input:
            self._command_input.focus()

    async def _auto_discover_channel(self) -> None:
        """Auto-discover and join a channel if possible."""
        if not self.client:
            return

        self.log_output("Discovering channels...")
        channels = await self.client.discover_channels()

        if not channels:
            self.log_output("No channels discovered. Use 'channel <name>' to join.", style="yellow")
            return

        if len(channels) == 1:
            # Auto-join if only one channel
            ch = channels[0]
            channel_name = ch.get("channel", "unknown")
            domain = ch.get("domain", "cytu.be")
            self.log_output(f"Found channel: {domain}/{channel_name}, joining...")
            await self.client.join_channel(channel_name, domain)
            self.log_output(f"Joined {channel_name}", style="green")
        else:
            # Multiple channels - show list
            self.log_output(f"Found {len(channels)} channels:")
            for ch in channels:
                domain = ch.get("domain", "cytu.be")
                channel = ch.get("channel", "?")
                self.log_output(f"  • {domain}/{channel}")
            self.log_output("Use 'channel <name>' to join one.")

    async def on_unmount(self) -> None:
        """Handle application unmount - cleanup connections."""
        if self.client and self.client.is_connected:
            await self.client.disconnect_quiet()

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_focus_command(self) -> None:
        """Focus the command input."""
        if self._command_input:
            self._command_input.focus()

    def action_show_help(self) -> None:
        """Show help information."""
        self.log_output("")
        self.log_output("═══ Kryten Shell Help ═══", style="bold cyan")
        self.log_output("")
        self.log_output("Commands:", style="bold")
        self.log_output("  help              - Show this help")
        self.log_output("  connect           - Connect to NATS")
        self.log_output("  disconnect        - Disconnect from NATS")
        self.log_output("  channel [name]    - Join channel or show current")
        self.log_output("  discover          - Discover available channels")
        self.log_output("  msg <message>     - Send chat message")
        self.log_output("  playlist          - Show playlist")
        self.log_output("  users             - Show online users")
        self.log_output("  kv buckets        - List KV buckets")
        self.log_output("  kv keys <bucket>  - List keys in bucket")
        self.log_output("  kv get <b> <k>    - Get value from bucket")
        self.log_output("")
        self.log_output("Keyboard Shortcuts:", style="bold")
        self.log_output("  Ctrl+L   - Clear output")
        self.log_output("  Ctrl+S   - Save screenshot (SVG)")
        self.log_output("  Ctrl+Q   - Quit")
        self.log_output("  Escape   - Focus command input")
        self.log_output("  Up/Down  - Command history")
        self.log_output("")

    def action_clear_output(self) -> None:
        """Clear the output log."""
        if self._output_log and self._output_log.is_mounted:
            self._output_log.clear()
            self.log_output("Output cleared")

    async def action_screenshot(self) -> None:
        """Save a screenshot as SVG."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kryten_shell_{timestamp}.svg"

        # Save to current directory or config directory
        path = Path.cwd() / filename
        self.save_screenshot(path=str(path))
        self.log_output(f"Screenshot saved: {path}", style="green")

    def log_output(
        self,
        message: str,
        style: str | None = None,
        error: bool = False,
    ) -> None:
        """Log a message to the output window.

        Args:
            message: The message to display.
            style: Optional Rich style string.
            error: Whether this is an error message.
        """
        if not self._output_log or not self._output_log.is_mounted:
            return

        try:
            if error:
                # Error messages get prefix
                self._output_log.write(f"[bold red]✗[/] [red]{message}[/]")
            elif style:
                # Apply style wrapper
                self._output_log.write(f"[{style}]{message}[/]")
            else:
                # Regular message - markup will be parsed by RichLog
                self._output_log.write(message)
        except Exception:
            pass  # Widget not ready

    def log_event(self, event_type: str, data: dict) -> None:
        """Log an event to the output.

        Args:
            event_type: The type of event.
            data: Event data dictionary.
        """
        # Only log interesting events to avoid spam
        if event_type in ("chatMsg", "userJoin", "userLeave", "changeMedia"):
            if event_type == "chatMsg":
                username = data.get("username", "?")
                msg = data.get("msg", "")
                self.log_output(f"[{username}] {msg}")
            elif event_type == "userJoin":
                username = data.get("name", "?")
                self.log_output(f"→ {username} joined", style="green")
            elif event_type == "userLeave":
                username = data.get("name", "?")
                self.log_output(f"← {username} left", style="dim")
            elif event_type == "changeMedia":
                title = data.get("title", "Unknown")
                self.log_output(f"▶ Now playing: {title}", style="cyan")

    def log_chat(self, username: str, message: str, timestamp: str | None = None) -> None:
        """Log a chat message.

        Args:
            username: The sender's username.
            message: The chat message.
            timestamp: Optional timestamp string.
        """
        from rich.text import Text

        if not self._output_log or not self._output_log.is_mounted:
            return

        try:
            text = Text()
            if timestamp:
                text.append(f"[{timestamp}] ", style="dim")
            text.append(f"{username}: ", style="bold cyan")
            text.append(message)
            self._output_log.write(text)
        except Exception:
            pass

    def update_status(
        self,
        connected: bool | None = None,
        channel: str | None = None,
        users: int | None = None,
    ) -> None:
        """Update the status bar.

        Args:
            connected: Connection state.
            channel: Current channel name.
            users: Number of users in channel.
        """
        if self._status_bar and self._status_bar.is_mounted:
            try:
                self._status_bar.update(connected=connected, channel=channel, users=users)
            except Exception:
                pass
