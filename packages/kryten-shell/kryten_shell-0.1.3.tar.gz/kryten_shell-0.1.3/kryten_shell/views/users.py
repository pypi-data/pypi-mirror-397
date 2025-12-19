"""Users view for displaying channel users and statistics."""

from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Static

from kryten_shell.client import KrytenClientWrapper


class UsersView(Vertical):
    """View for displaying channel users and statistics.

    Shows:
    - Current users in the channel
    - User stats when a user is selected
    - Leaderboards (kudos, emotes, messages)
    """

    DEFAULT_CSS = """
    UsersView {
        height: 100%;
    }

    #users-header {
        height: 3;
        background: #073642;
        padding: 0 1;
        border-bottom: solid #586e75;
    }

    #users-content {
        height: 1fr;
    }

    #users-list {
        width: 40;
        height: 100%;
        border-right: solid #586e75;
    }

    #users-detail {
        width: 1fr;
        height: 100%;
        padding: 1;
        overflow-y: auto;
    }

    #users-table {
        height: 100%;
    }

    .leaderboard-section {
        margin-bottom: 1;
    }

    .leaderboard-title {
        color: #2aa198;
        text-style: bold;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the users view."""
        super().__init__(*args, **kwargs)
        self._client: KrytenClientWrapper | None = None
        self._selected_user: str | None = None
        self._users: list[dict] = []

    def compose(self):
        """Compose the users view widgets."""
        yield Static(
            "[bold]Users[/] | Online: 0 | Select a user to view stats",
            id="users-header",
        )
        with Horizontal(id="users-content"):
            with Vertical(id="users-list"):
                yield DataTable(id="users-table", cursor_type="row")
            yield Static(
                "[dim]Select a user to view their statistics[/]\n\n"
                "[cyan]Tip:[/] Use 'users refresh' to update the list",
                id="users-detail",
            )

    def on_mount(self) -> None:
        """Set up the data table columns."""
        table = self.query_one("#users-table", DataTable)
        table.add_column("User", width=25)
        table.add_column("Rank", width=8)

    def set_client(self, client: KrytenClientWrapper) -> None:
        """Set the Kryten client reference.

        Args:
            client: The Kryten client wrapper.
        """
        self._client = client

    def update_users(self, users: list[dict]) -> None:
        """Update the user list display.

        Args:
            users: List of user dicts with name, rank, etc.
        """
        self._users = users
        table = self.query_one("#users-table", DataTable)
        table.clear()

        # Sort by rank (higher first), then by name
        sorted_users = sorted(
            users,
            key=lambda u: (-u.get("rank", 0), u.get("name", "").lower()),
        )

        for user in sorted_users:
            name = user.get("name", "Unknown")
            rank = user.get("rank", 0)
            rank_label = self._rank_label(rank)

            table.add_row(name, rank_label, key=name)

        # Update header
        self._update_header(len(users))

    def _rank_label(self, rank: int) -> str:
        """Get a label for a user rank.

        Args:
            rank: Numeric rank value.

        Returns:
            Human-readable rank label.
        """
        rank_names = {
            0: "Guest",
            1: "User",
            2: "Mod",
            3: "Admin",
            4: "Owner",
            255: "Founder",
        }
        return rank_names.get(rank, f"Rank {rank}")

    def _update_header(self, count: int) -> None:
        """Update the header with user count.

        Args:
            count: Number of online users.
        """
        header = self.query_one("#users-header", Static)
        if self._selected_user:
            header.update(
                f"[bold]Users[/] | Online: {count} | Viewing: {self._selected_user}"
            )
        else:
            header.update(
                f"[bold]Users[/] | Online: {count} | Select a user to view stats"
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle user selection.

        Args:
            event: The row selected event.
        """
        if event.row_key:
            username = str(event.row_key.value)
            self._selected_user = username
            self._update_header(len(self._users))
            # Trigger async load of user stats
            self.app.call_later(self._load_user_stats, username)

    async def _load_user_stats(self, username: str) -> None:
        """Load and display stats for a user.

        Args:
            username: The username to load stats for.
        """
        if not self._client:
            return

        detail = self.query_one("#users-detail", Static)
        detail.update(f"[dim]Loading stats for {username}...[/]")

        stats = await self._client.get_user_stats(username)

        if stats is None:
            detail.update(
                f"[yellow]Could not load stats for {username}[/]\n\n"
                "[dim]The userstats service may not be running.[/]"
            )
            return

        # Format the stats display
        output = self._format_user_stats(username, stats)
        detail.update(output)

    def _format_user_stats(self, username: str, stats: dict) -> str:
        """Format user stats for display.

        Args:
            username: The username.
            stats: Stats dict from userstats service.

        Returns:
            Formatted string for display.
        """
        lines = [
            f"[bold cyan]📊 Stats for {username}[/]",
            "",
        ]

        # Aliases
        aliases = stats.get("aliases", [])
        if aliases:
            lines.append(f"[bold]Aliases:[/] {', '.join(aliases)}")
            lines.append("")

        # Messages
        messages = stats.get("messages", {})
        if messages:
            lines.append("[bold]Messages:[/]")
            total = 0
            for channel, count in messages.items():
                lines.append(f"  {channel}: {count:,}")
                total += count
            if len(messages) > 1:
                lines.append(f"  [dim]Total: {total:,}[/]")
            lines.append("")

        # Activity
        activity = stats.get("activity", {})
        if activity:
            lines.append("[bold]Activity:[/]")
            for channel, data in activity.items():
                total_secs = data.get("total_seconds", 0)
                hours = total_secs / 3600
                lines.append(f"  {channel}: {hours:.1f} hours")
            lines.append("")

        # Kudos
        kudos_pp = stats.get("kudos_plusplus", 0)
        if kudos_pp:
            lines.append(f"[bold]Kudos Received:[/] {kudos_pp:,} ++")
            lines.append("")

        # Top kudos phrases
        kudos_phrases = stats.get("kudos_phrases", [])
        if kudos_phrases:
            lines.append("[bold]Top Kudos Phrases:[/]")
            for phrase in kudos_phrases[:5]:
                p = phrase.get("phrase", "?")
                c = phrase.get("count", 0)
                lines.append(f"  {p}: {c:,}")
            lines.append("")

        # Top emotes
        emotes = stats.get("emotes", [])
        if emotes:
            lines.append("[bold]Top Emotes:[/]")
            for emote in emotes[:5]:
                e = emote.get("emote", "?")
                c = emote.get("count", 0)
                lines.append(f"  {e}: {c:,}")
            lines.append("")

        # PMs
        pms = stats.get("pms", 0)
        if pms:
            lines.append(f"[bold]Private Messages:[/] {pms:,}")

        if len(lines) <= 2:
            lines.append("[dim]No statistics recorded for this user.[/]")

        return "\n".join(lines)

    async def refresh_users(self) -> None:
        """Refresh the user list from the server."""
        if self._client:
            users = await self._client.get_userlist()
            self.update_users(users)

    async def show_leaderboards(self) -> None:
        """Show channel leaderboards in the detail panel."""
        if not self._client:
            return

        detail = self.query_one("#users-detail", Static)
        detail.update("[dim]Loading leaderboards...[/]")

        # Get channel stats
        stats = await self._client.get_channel_stats()

        if stats is None:
            detail.update(
                "[yellow]Could not load leaderboards[/]\n\n"
                "[dim]The userstats service may not be running.[/]"
            )
            return

        # Format leaderboards
        output = self._format_leaderboards(stats)
        detail.update(output)

    def _format_leaderboards(self, stats: dict) -> str:
        """Format leaderboard stats for display.

        Args:
            stats: Stats dict from channel.all_stats command.

        Returns:
            Formatted string for display.
        """
        lines = [
            "[bold cyan]🏆 Channel Leaderboards[/]",
            "",
        ]

        # Top users by messages
        channel = stats.get("channel", {})
        top_users = channel.get("top_users", [])
        if top_users:
            lines.append("[bold]Top Chatters:[/]")
            for i, user in enumerate(top_users[:10], 1):
                medal = self._medal(i)
                name = user.get("username", "?")
                count = user.get("count", 0)
                lines.append(f"  {medal} {name}: {count:,} messages")
            lines.append("")

        # Leaderboards
        leaderboards = stats.get("leaderboards", {})

        # Kudos
        kudos = leaderboards.get("kudos", [])
        if kudos:
            lines.append("[bold]Kudos Leaders:[/]")
            for i, entry in enumerate(kudos[:10], 1):
                medal = self._medal(i)
                name = entry.get("username", "?")
                count = entry.get("count", 0)
                lines.append(f"  {medal} {name}: {count:,} ++")
            lines.append("")

        # Emotes
        emotes = leaderboards.get("emotes", [])
        if emotes:
            lines.append("[bold]Top Emotes:[/]")
            for i, entry in enumerate(emotes[:10], 1):
                medal = self._medal(i)
                emote = entry.get("emote", "?")
                count = entry.get("count", 0)
                lines.append(f"  {medal} {emote}: {count:,} uses")
            lines.append("")

        if len(lines) <= 2:
            lines.append("[dim]No leaderboard data available.[/]")

        return "\n".join(lines)

    def _medal(self, position: int) -> str:
        """Get medal emoji for position.

        Args:
            position: 1-based position.

        Returns:
            Medal string.
        """
        if position == 1:
            return "🥇"
        elif position == 2:
            return "🥈"
        elif position == 3:
            return "🥉"
        else:
            return f"{position:2}."

