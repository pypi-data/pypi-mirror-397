"""Status bar widget showing connection state and channel info."""

from textual.widgets import Static

from kryten_shell.client import KrytenClientWrapper


class StatusBar(Static):
    """Status bar showing connection state and current channel.

    Displays:
    - Connection status (connected/disconnected)
    - Current channel name
    - Number of users in channel
    - Current video (optional)
    """

    DEFAULT_CSS = """
    StatusBar {
        background: #073642;
        color: #839496;
        height: 1;
        dock: bottom;
        padding: 0 1;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the status bar."""
        super().__init__("", *args, **kwargs)
        self._client: KrytenClientWrapper | None = None
        self._connected: bool = False
        self._channel: str | None = None
        self._users: int = 0
        self._update_display()

    def set_client(self, client: KrytenClientWrapper) -> None:
        """Set the Kryten client reference.

        Args:
            client: The Kryten client wrapper.
        """
        self._client = client

    def update(
        self,
        connected: bool | None = None,
        channel: str | None = None,
        users: int | None = None,
    ) -> None:
        """Update the status bar values.

        Args:
            connected: Connection state.
            channel: Current channel name.
            users: Number of users in channel.
        """
        if connected is not None:
            self._connected = connected
        if channel is not None:
            self._channel = channel
        if users is not None:
            self._users = users

        self._update_display()

    def _update_display(self) -> None:
        """Update the status bar text."""
        parts = []

        # Connection status
        if self._connected:
            parts.append("[green]● Connected[/]")
        else:
            parts.append("[red]○ Disconnected[/]")

        # Channel
        if self._channel:
            parts.append(f"[bold cyan]{self._channel}[/]")
        else:
            parts.append("[dim]No channel[/]")

        # Users
        if self._users > 0:
            parts.append(f"[yellow]👥 {self._users}[/]")

        super().update(" │ ".join(parts))
