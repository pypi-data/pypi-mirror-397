"""Playlist view for displaying the channel playlist."""

from textual.containers import Vertical
from textual.widgets import DataTable, Static

from kryten_shell.client import KrytenClientWrapper


class PlaylistView(Vertical):
    """View for displaying and managing the channel playlist.

    Shows:
    - Currently playing item (highlighted)
    - Full playlist with title, duration, and queued by info
    - Playlist statistics
    """

    DEFAULT_CSS = """
    PlaylistView {
        height: 100%;
    }

    #playlist-stats {
        height: 3;
        background: #073642;
        padding: 0 1;
        border-bottom: solid #586e75;
    }

    #playlist-table {
        height: 1fr;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the playlist view."""
        super().__init__(*args, **kwargs)
        self._client: KrytenClientWrapper | None = None
        self._current_uid: int | None = None

    def compose(self):
        """Compose the playlist view widgets."""
        yield Static(
            "[bold]Playlist[/] | Items: 0 | Duration: 0:00:00",
            id="playlist-stats",
        )
        yield DataTable(id="playlist-table", cursor_type="row")

    def on_mount(self) -> None:
        """Set up the data table columns."""
        table = self.query_one("#playlist-table", DataTable)
        table.add_column("#", width=4)
        table.add_column("Title", width=60)
        table.add_column("Duration", width=10)
        table.add_column("Queued By", width=15)

    def set_client(self, client: KrytenClientWrapper) -> None:
        """Set the Kryten client reference.

        Args:
            client: The Kryten client wrapper.
        """
        self._client = client

    def update_playlist(self, items: list[dict], current_uid: int | str | None = None) -> None:
        """Update the playlist display.

        Args:
            items: List of playlist items.
            current_uid: UID of the currently playing item (int or str).
        """
        # Normalize current_uid to int for comparison
        if current_uid is not None:
            try:
                current_uid = int(current_uid)
            except (ValueError, TypeError):
                current_uid = None

        self._current_uid = current_uid
        table = self.query_one("#playlist-table", DataTable)
        table.clear()

        total_seconds = 0

        for idx, item in enumerate(items, 1):
            # Extract item data
            media = item.get("media", item)
            title = media.get("title", "Unknown")
            seconds = media.get("seconds", 0)
            queued_by = item.get("queueby", "Unknown")
            uid = item.get("uid")

            # Normalize uid to int for comparison
            if uid is not None:
                try:
                    uid = int(uid)
                except (ValueError, TypeError):
                    uid = None

            total_seconds += seconds

            # Format duration
            duration = self._format_duration(seconds)

            # Highlight current item
            if uid is not None and uid == current_uid:
                prefix = "▶ "
            else:
                prefix = ""

            table.add_row(
                str(idx),
                f"{prefix}{title}",
                duration,
                queued_by,
                key=str(uid) if uid else str(idx),
            )

        # Update stats
        self._update_stats(len(items), total_seconds)

    def set_current(self, uid: int | str | None) -> None:
        """Set the currently playing item.

        Args:
            uid: UID of the current item.
        """
        # Normalize to int
        if uid is not None:
            try:
                uid = int(uid)
            except (ValueError, TypeError):
                uid = None
        self._current_uid = uid
        # Would need to refresh display to show new current item
        # For now, call refresh_playlist to update

    async def refresh_playlist(self) -> None:
        """Refresh the playlist from the server."""
        if self._client:
            playlist = await self._client.get_playlist()
            current = await self._client.get_current_media()
            current_uid = current.get("uid") if current else None
            self.update_playlist(playlist, current_uid)

    def _update_stats(self, count: int, total_seconds: int) -> None:
        """Update the playlist statistics display.

        Args:
            count: Number of items.
            total_seconds: Total duration in seconds.
        """
        stats = self.query_one("#playlist-stats", Static)
        duration = self._format_duration(total_seconds)
        stats.update(f"[bold]Playlist[/] | Items: {count} | Duration: {duration}")

    def _format_duration(self, seconds: int) -> str:
        """Format seconds as H:MM:SS or M:SS.

        Args:
            seconds: Duration in seconds.

        Returns:
            Formatted duration string.
        """
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)

        if hours:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
