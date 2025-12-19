"""Events view for displaying Kryten ecosystem events."""

from datetime import datetime

from rich.text import Text
from textual.containers import Vertical
from textual.widgets import RichLog, Static

from kryten_shell.client import KrytenClientWrapper


class EventsView(Vertical):
    """View for displaying real-time Kryten ecosystem events.

    Shows:
    - NATS events from all subscribed subjects
    - CyTube events (chat, playlist changes, user joins/parts)
    - System events (connections, errors)
    """

    DEFAULT_CSS = """
    EventsView {
        height: 100%;
    }

    #events-filter {
        height: 3;
        background: #073642;
        padding: 0 1;
        border-bottom: solid #586e75;
    }

    #events-log {
        height: 1fr;
    }
    """

    # Event type to style mapping
    EVENT_STYLES = {
        "chat": ("cyan", "💬"),
        "changemedia": ("green", "▶"),
        "queue": ("blue", "➕"),
        "delete": ("red", "➖"),
        "userlist": ("yellow", "👥"),
        "userJoin": ("green", "→"),
        "userLeave": ("red", "←"),
        "error": ("red", "⚠"),
        "system": ("yellow", "★"),
        "connect": ("green", "●"),
        "disconnect": ("red", "○"),
    }

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the events view."""
        super().__init__(*args, **kwargs)
        self._client: KrytenClientWrapper | None = None
        self._event_count: int = 0
        self._filter: str | None = None

    def compose(self):
        """Compose the events view widgets."""
        yield Static(
            "[bold]Events[/] | Total: 0 | Filter: [dim]none[/]",
            id="events-filter",
        )
        yield RichLog(
            highlight=True,
            markup=True,
            wrap=True,
            id="events-log",
        )

    def set_client(self, client: KrytenClientWrapper) -> None:
        """Set the Kryten client reference.

        Args:
            client: The Kryten client wrapper.
        """
        self._client = client

    def add_event(self, event_type: str, data: dict) -> None:
        """Add an event to the log.

        Args:
            event_type: The type of event.
            data: Event data dictionary.
        """
        # Check filter
        if self._filter and self._filter.lower() not in event_type.lower():
            return

        self._event_count += 1

        log = self.query_one("#events-log", RichLog)

        # Get style for event type
        style_info = self.EVENT_STYLES.get(
            event_type,
            ("white", "•"),
        )
        color, icon = style_info

        # Build the event text
        text = Text()

        # Timestamp
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        text.append(f"[{ts}] ", style="dim")

        # Icon and type
        text.append(f"{icon} ", style=color)
        text.append(f"{event_type}", style=f"bold {color}")
        text.append(" | ", style="dim")

        # Event data (simplified)
        summary = self._summarize_event(event_type, data)
        text.append(summary)

        log.write(text)

        # Update header
        self._update_header()

    def add_raw_event(self, subject: str, payload: str) -> None:
        """Add a raw NATS event to the log.

        Args:
            subject: The NATS subject.
            payload: Raw payload string.
        """
        self._event_count += 1

        log = self.query_one("#events-log", RichLog)

        text = Text()
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        text.append(f"[{ts}] ", style="dim")
        text.append("📨 ", style="magenta")
        text.append(f"{subject}", style="bold magenta")
        text.append(" | ", style="dim")
        text.append(payload[:200] + ("..." if len(payload) > 200 else ""))

        log.write(text)
        self._update_header()

    def set_filter(self, filter_text: str | None) -> None:
        """Set the event filter.

        Args:
            filter_text: Filter text or None to clear.
        """
        self._filter = filter_text
        self._update_header()

    def clear(self) -> None:
        """Clear the event log."""
        log = self.query_one("#events-log", RichLog)
        log.clear()
        self._event_count = 0
        self._update_header()

    def _update_header(self) -> None:
        """Update the header with current stats."""
        header = self.query_one("#events-filter", Static)
        filter_text = self._filter if self._filter else "[dim]none[/]"
        header.update(f"[bold]Events[/] | Total: {self._event_count} | Filter: {filter_text}")

    def _summarize_event(self, event_type: str, data: dict) -> str:
        """Create a short summary of event data.

        Args:
            event_type: The type of event.
            data: Event data dictionary.

        Returns:
            Summary string.
        """
        if event_type == "chat":
            user = data.get("username", "?")
            msg = data.get("msg", "")[:50]
            return f"{user}: {msg}"

        elif event_type == "changemedia":
            title = data.get("title", "Unknown")[:40]
            return f"{title}"

        elif event_type == "queue":
            media = data.get("item", {}).get("media", {})
            title = media.get("title", "Unknown")[:40]
            queueby = data.get("item", {}).get("queueby", "?")
            return f"{title} (by {queueby})"

        elif event_type in ("userJoin", "userLeave"):
            name = data.get("name", "?")
            return name

        elif event_type == "userlist":
            count = len(data) if isinstance(data, list) else data.get("count", "?")
            return f"{count} users"

        else:
            # Generic summary
            import json
            try:
                return json.dumps(data)[:100]
            except Exception:
                return str(data)[:100]
