"""Chat view for displaying and sending chat messages."""

from datetime import datetime

from rich.text import Text
from textual.containers import Vertical
from textual.widgets import RichLog, Static

from kryten_shell.client import KrytenClientWrapper


class ChatView(Vertical):
    """View for displaying chat messages and current video info.

    Shows:
    - Current video being played
    - Rolling chat message log
    - User chat messages with timestamps
    """

    DEFAULT_CSS = """
    ChatView {
        height: 100%;
    }

    #current-video {
        height: 3;
        background: #073642;
        padding: 0 1;
        border-bottom: solid #586e75;
    }

    #chat-log {
        height: 1fr;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the chat view."""
        super().__init__(*args, **kwargs)
        self._client: KrytenClientWrapper | None = None
        self._current_video: str = "No video playing"
        self._show_timestamps: bool = True

    def compose(self):
        """Compose the chat view widgets."""
        yield Static(
            f"[bold cyan]▶[/] {self._current_video}",
            id="current-video",
        )
        yield RichLog(
            highlight=True,
            markup=True,
            wrap=True,
            id="chat-log",
        )

    def set_client(self, client: KrytenClientWrapper) -> None:
        """Set the Kryten client reference.

        Args:
            client: The Kryten client wrapper.
        """
        self._client = client

    def add_message(
        self,
        username: str,
        message: str,
        timestamp: str | None = None,
    ) -> None:
        """Add a chat message to the log.

        Args:
            username: The sender's username.
            message: The chat message content.
            timestamp: Optional timestamp string.
        """
        log = self.query_one("#chat-log", RichLog)

        # Build the message text
        text = Text()

        if self._show_timestamps:
            ts = timestamp or datetime.now().strftime("%H:%M:%S")
            text.append(f"[{ts}] ", style="dim")

        text.append(f"{username}: ", style="bold cyan")
        text.append(message)

        log.write(text)

    def add_system_message(self, message: str) -> None:
        """Add a system message to the chat log.

        Args:
            message: The system message.
        """
        log = self.query_one("#chat-log", RichLog)

        text = Text()
        if self._show_timestamps:
            ts = datetime.now().strftime("%H:%M:%S")
            text.append(f"[{ts}] ", style="dim")

        text.append("★ ", style="bold yellow")
        text.append(message, style="yellow")

        log.write(text)

    def update_current_video(self, title: str, queued_by: str | None = None) -> None:
        """Update the current video display.

        Args:
            title: The video title.
            queued_by: Who queued the video.
        """
        self._current_video = title
        video_display = self.query_one("#current-video", Static)

        if queued_by:
            video_display.update(
                f"[bold cyan]▶[/] {title} [dim](queued by {queued_by})[/]"
            )
        else:
            video_display.update(f"[bold cyan]▶[/] {title}")

    def clear(self) -> None:
        """Clear the chat log."""
        log = self.query_one("#chat-log", RichLog)
        log.clear()
