"""Built-in commands for kryten-shell."""

import json
from typing import TYPE_CHECKING, Any

from kryten_shell.commands.base import Command, CommandArg, CommandResult

if TYPE_CHECKING:
    from kryten_shell.app import KrytenShellApp
    from kryten_shell.client import KrytenClientWrapper


def register_builtin_commands(registry) -> None:
    """Register all built-in commands.

    Args:
        registry: The command registry.
    """
    # ========================================================================
    # Connection commands
    # ========================================================================
    registry.register(Command(
        name="connect",
        description="Connect to the NATS server",
        handler=cmd_connect,
        category="connection",
    ))

    registry.register(Command(
        name="disconnect",
        description="Disconnect from the NATS server",
        handler=cmd_disconnect,
        category="connection",
    ))

    registry.register(Command(
        name="channel",
        description="Join a channel or show current channel",
        handler=cmd_channel,
        args=[
            CommandArg("name", "Channel name to join", required=False),
        ],
        aliases=["ch", "join"],
        category="connection",
    ))

    registry.register(Command(
        name="discover",
        description="Discover available channels from kryten-robot",
        handler=cmd_discover,
        category="connection",
    ))

    # ========================================================================
    # Chat commands
    # ========================================================================
    registry.register(Command(
        name="msg",
        description="Send a chat message",
        handler=cmd_msg,
        args=[
            CommandArg("message", "Message to send"),
        ],
        aliases=["say", "chat"],
        category="chat",
    ))

    registry.register(Command(
        name="pm",
        description="Send a private message",
        handler=cmd_pm,
        args=[
            CommandArg("username", "Username to message"),
            CommandArg("message", "Message to send"),
        ],
        category="chat",
    ))

    # ========================================================================
    # Playlist commands
    # ========================================================================
    registry.register(Command(
        name="playlist",
        description="Show or manage the playlist",
        handler=cmd_playlist,
        args=[
            CommandArg("action", "Action: show, all, top, add, skip", required=False, default="show"),
            CommandArg("url", "URL to add (for add action)", required=False),
        ],
        aliases=["pl", "list"],
        category="playlist",
    ))

    registry.register(Command(
        name="skip",
        description="Skip the current video (voteskip)",
        handler=cmd_skip,
        category="playlist",
    ))

    registry.register(Command(
        name="nowplaying",
        description="Show the currently playing video",
        handler=cmd_nowplaying,
        aliases=["np", "now"],
        category="playlist",
    ))

    registry.register(Command(
        name="pause",
        description="Pause playback",
        handler=cmd_pause,
        category="playlist",
    ))

    registry.register(Command(
        name="play",
        description="Resume playback",
        handler=cmd_play,
        aliases=["resume"],
        category="playlist",
    ))

    registry.register(Command(
        name="seek",
        description="Seek to timestamp in seconds",
        handler=cmd_seek,
        args=[
            CommandArg("time", "Time in seconds"),
        ],
        category="playlist",
    ))

    # ========================================================================
    # KV commands
    # ========================================================================
    registry.register(Command(
        name="kv",
        description="Interact with the KV store",
        handler=cmd_kv,
        args=[
            CommandArg("action", "Action: list, get, buckets, keys"),
            CommandArg("bucket", "Bucket name", required=False),
            CommandArg("key", "Key name", required=False),
        ],
        category="kv",
    ))

    # ========================================================================
    # Users commands
    # ========================================================================
    registry.register(Command(
        name="users",
        description="Show or interact with users",
        handler=cmd_users,
        args=[
            CommandArg("action", "Action: list, stats, leaderboard", required=False, default="list"),
            CommandArg("username", "Username for stats lookup", required=False),
        ],
        aliases=["u", "who"],
        category="users",
    ))

    registry.register(Command(
        name="stats",
        description="Show stats for a user",
        handler=cmd_user_stats,
        args=[
            CommandArg("username", "Username to look up"),
        ],
        category="users",
    ))

    registry.register(Command(
        name="leaderboard",
        description="Show channel leaderboards",
        handler=cmd_leaderboard,
        aliases=["lb", "top"],
        category="users",
    ))

    registry.register(Command(
        name="activity",
        description="Show activity timeline for a user",
        handler=cmd_user_activity,
        args=[
            CommandArg("username", "Username to look up"),
        ],
        category="users",
    ))

    registry.register(Command(
        name="kudos",
        description="Show kudos given/received for a user",
        handler=cmd_user_kudos,
        args=[
            CommandArg("username", "Username to look up"),
        ],
        category="users",
    ))

    registry.register(Command(
        name="messages",
        description="Show recent messages from a user",
        handler=cmd_user_messages,
        args=[
            CommandArg("username", "Username to look up"),
            CommandArg("limit", "Number of messages", required=False, default="20"),
        ],
        category="users",
    ))

    registry.register(Command(
        name="population",
        description="Show channel population stats",
        handler=cmd_population,
        category="users",
    ))

    registry.register(Command(
        name="history",
        description="Show media history for the channel",
        handler=cmd_media_history,
        args=[
            CommandArg("limit", "Number of entries", required=False, default="20"),
        ],
        aliases=["media"],
        category="playlist",
    ))

    # ========================================================================
    # Service discovery commands
    # ========================================================================
    registry.register(Command(
        name="services",
        description="Discover and show status of all kryten services",
        handler=cmd_services,
        aliases=["svc", "ping"],
        category="utility",
    ))

    # ========================================================================
    # LLM debugging commands
    # ========================================================================
    registry.register(Command(
        name="llmlog",
        description="Show recent LLM context log entries",
        handler=cmd_llmlog,
        args=[
            CommandArg("limit", "Number of entries to show", required=False, default="10"),
        ],
        aliases=["llmcontext"],
        category="utility",
    ))

    registry.register(Command(
        name="llmshow",
        description="Show full details of an LLM context entry",
        handler=cmd_llmshow,
        args=[
            CommandArg("identifier", "Index number or correlation ID"),
        ],
        category="utility",
    ))

    # ========================================================================
    # Moderation commands
    # ========================================================================
    registry.register(Command(
        name="kick",
        description="Kick a user from the channel",
        handler=cmd_kick,
        args=[
            CommandArg("username", "Username to kick"),
            CommandArg("reason", "Reason for kick", required=False),
        ],
        category="moderation",
    ))

    registry.register(Command(
        name="ban",
        description="Add user to persistent ban list (kryten-moderator)",
        handler=cmd_mod_ban,
        args=[
            CommandArg("username", "Username to ban"),
            CommandArg("reason", "Reason for ban", required=False),
        ],
        category="moderation",
    ))

    registry.register(Command(
        name="unban",
        description="Remove user from persistent ban list",
        handler=cmd_mod_unban,
        args=[
            CommandArg("username", "Username to unban"),
        ],
        category="moderation",
    ))

    registry.register(Command(
        name="smute",
        description="Shadow mute a user (they don't know they're muted)",
        handler=cmd_mod_smute,
        args=[
            CommandArg("username", "Username to shadow mute"),
            CommandArg("reason", "Reason for mute", required=False),
        ],
        category="moderation",
    ))

    registry.register(Command(
        name="unsmute",
        description="Remove shadow mute from user",
        handler=cmd_mod_unsmute,
        args=[
            CommandArg("username", "Username to unshadow mute"),
        ],
        category="moderation",
    ))

    registry.register(Command(
        name="mute",
        description="Visible mute a user (they are notified)",
        handler=cmd_mod_mute,
        args=[
            CommandArg("username", "Username to mute"),
            CommandArg("reason", "Reason for mute", required=False),
        ],
        category="moderation",
    ))

    registry.register(Command(
        name="unmute",
        description="Remove visible mute from user",
        handler=cmd_mod_unmute,
        args=[
            CommandArg("username", "Username to unmute"),
        ],
        category="moderation",
    ))

    registry.register(Command(
        name="modlist",
        description="List all moderated users",
        handler=cmd_mod_list,
        args=[
            CommandArg("filter", "Filter by action: ban, smute, mute", required=False),
        ],
        aliases=["banlist", "bans"],
        category="moderation",
    ))

    registry.register(Command(
        name="modcheck",
        description="Check moderation status of a user",
        handler=cmd_mod_check,
        args=[
            CommandArg("username", "Username to check"),
        ],
        category="moderation",
    ))

    registry.register(Command(
        name="patterns",
        description="List or manage banned username patterns",
        handler=cmd_mod_patterns,
        args=[
            CommandArg("action", "Action: list, add, remove", required=False, default="list"),
            CommandArg("pattern", "Pattern to add/remove", required=False),
            CommandArg("options", "Options: --regex, --smute, --mute, --desc=TEXT", required=False),
        ],
        category="moderation",
    ))

    # ========================================================================
    # Convenience/show commands
    # ========================================================================
    registry.register(Command(
        name="show",
        description="Show various information (users, playlist, buckets, etc.)",
        handler=cmd_show,
        args=[
            CommandArg("what", "What to show: users, playlist, buckets, status, np"),
            CommandArg("extra", "Extra parameter", required=False),
        ],
        category="utility",
    ))

    # ========================================================================
    # Utility commands
    # ========================================================================
    registry.register(Command(
        name="help",
        description="Show help for commands",
        handler=cmd_help,
        args=[
            CommandArg("command", "Command to get help for", required=False),
        ],
        aliases=["?", "h"],
        category="utility",
    ))

    registry.register(Command(
        name="clear",
        description="Clear the output log",
        handler=cmd_clear,
        aliases=["cls"],
        category="utility",
    ))

    registry.register(Command(
        name="refresh",
        description="Refresh data from server",
        handler=cmd_refresh,
        aliases=["r"],
        category="utility",
    ))

    registry.register(Command(
        name="quit",
        description="Exit the shell",
        handler=cmd_quit,
        aliases=["exit", "q"],
        category="utility",
    ))

    registry.register(Command(
        name="status",
        description="Show connection and system status",
        handler=cmd_status,
        category="utility",
    ))


# ============================================================================
# Command implementations - Connection
# ============================================================================

async def cmd_connect(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Connect to NATS server."""
    if client.is_connected:
        return CommandResult(False, "Already connected")

    await client.connect()
    return CommandResult(True, "Connected to NATS")


async def cmd_disconnect(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Disconnect from NATS server."""
    if not client.is_connected:
        return CommandResult(False, "Not connected")

    await client.disconnect()
    return CommandResult(True, "Disconnected from NATS")


async def cmd_channel(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Join a channel or show current."""
    channel_name = args.get("name", "").strip()

    if not channel_name:
        current = client.current_channel
        if current:
            return CommandResult(True, f"Current channel: {current}")
        return CommandResult(True, "No channel joined")

    await client.join_channel(channel_name)
    return CommandResult(True, f"Joined channel: {channel_name}")


async def cmd_discover(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Discover available channels."""
    channels = await client.discover_channels()
    if not channels:
        return CommandResult(True, "No channels discovered")

    lines = ["[bold cyan]Available channels:[/]"]
    for ch in channels:
        domain = ch.get("domain", "cytu.be")
        channel = ch.get("channel", "?")
        lines.append(f"  • {domain}/{channel}")
    return CommandResult(True, "\n".join(lines))


# ============================================================================
# Command implementations - Chat
# ============================================================================

async def cmd_msg(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Send a chat message."""
    message = args.get("message", "").strip()
    if not message:
        return CommandResult(False, "No message provided")

    await client.send_chat(message)
    return CommandResult(True)


async def cmd_pm(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Send a private message."""
    username = args.get("username", "").strip()
    message = args.get("message", "").strip()
    
    if not username:
        return CommandResult(False, "Usage: pm <username> <message>")
    if not message:
        return CommandResult(False, "No message provided")

    await client.send_pm(username, message)
    return CommandResult(True, f"PM sent to {username}")


# ============================================================================
# Command implementations - Playlist
# ============================================================================

async def cmd_playlist(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show or manage playlist."""
    action = args.get("action", "show").lower()

    if action in ("show", "list", "all", "top", "from"):
        playlist = await client.get_playlist()
        if not playlist:
            return CommandResult(True, "Playlist is empty")
        
        current = await client.get_current_media()
        current_uid = current.get("uid") if current else None
        
        # Find current item index
        current_idx = 0
        for i, item in enumerate(playlist):
            if item.get("uid") == current_uid:
                current_idx = i
                break
        
        # Determine display mode
        show_all = action == "all"
        from_top = action == "top"
        
        if from_top:
            start_idx = 0
            display_items = playlist[:20]
        elif show_all:
            start_idx = 0
            display_items = playlist
        else:
            # Default: start from current, show 20 items
            start_idx = current_idx
            display_items = playlist[current_idx:current_idx + 20]
        
        lines = [f"[bold cyan]Playlist ({len(playlist)} items):[/]"]
        
        for i, item in enumerate(display_items):
            actual_idx = start_idx + i + 1
            media = item.get("media", {})
            title = media.get("title", "Unknown")[:50]
            uid = item.get("uid")
            temp = " [yellow][T][/]" if item.get("temp") else ""
            marker = "[green]▶[/] " if uid == current_uid else "  "
            lines.append(f"{marker}{actual_idx:3}. {title}{temp}")
        
        remaining = len(playlist) - (start_idx + len(display_items))
        if remaining > 0 and not show_all:
            lines.append(f"  [dim]... and {remaining} more (use 'playlist all' to see all)[/]")
        
        return CommandResult(True, "\n".join(lines))

    elif action == "add":
        url = args.get("url", "").strip()
        if not url:
            return CommandResult(False, "No URL provided")
        await client.add_to_playlist(url)
        return CommandResult(True, f"Added to playlist: {url}")

    elif action == "skip":
        await client.skip_video()
        return CommandResult(True, "Voted to skip")

    return CommandResult(False, f"Unknown playlist action: {action}\nUsage: playlist [show|all|top|add|skip]")


async def cmd_skip(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Skip current video."""
    await client.voteskip()
    return CommandResult(True, "Voted to skip")


async def cmd_nowplaying(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show currently playing video."""
    current = await client.get_current_media()
    if not current:
        return CommandResult(True, "Nothing playing")

    title = current.get("title", "Unknown")
    duration = current.get("duration", 0)
    media_type = current.get("type", "?")
    
    # Ensure duration is numeric
    try:
        duration = int(float(duration)) if duration else 0
    except (ValueError, TypeError):
        duration = 0
    
    mins, secs = divmod(duration, 60)
    dur_str = f"{mins}:{secs:02d}"
    
    return CommandResult(True, f"[bold cyan]Now Playing:[/] {title}\n  Duration: {dur_str} | Type: {media_type}")


async def cmd_pause(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Pause playback."""
    await client.pause()
    return CommandResult(True, "Playback paused")


async def cmd_play(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Resume playback."""
    await client.play()
    return CommandResult(True, "Playback resumed")


async def cmd_seek(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Seek to timestamp."""
    time_str = args.get("time", "").strip()
    if not time_str:
        return CommandResult(False, "Usage: seek <seconds>")
    
    try:
        time_val = float(time_str)
    except ValueError:
        return CommandResult(False, f"Invalid time: {time_str}")
    
    await client.seek(time_val)
    return CommandResult(True, f"Seeked to {time_val}s")


# ============================================================================
# Command implementations - KV Store
# ============================================================================

async def cmd_kv(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """KV store operations."""
    action = args.get("action", "").lower()

    if action == "buckets" or action == "list":
        buckets = await client.list_kv_buckets()
        if not buckets:
            return CommandResult(True, "No KV buckets found (is Kryten-Robot running?)")
        lines = [f"[bold cyan]KV Buckets ({len(buckets)}):[/]"]
        for b in buckets:
            lines.append(f"  {b}")
        return CommandResult(True, "\n".join(lines))

    elif action == "get":
        bucket = args.get("bucket", "")
        key = args.get("key", "")
        if not bucket or not key:
            return CommandResult(False, "Usage: kv get <bucket> <key>")

        value = await client.kv_get(bucket, key)
        if value is None:
            return CommandResult(True, f"{bucket}/{key}: (not found)")

        # Pretty print JSON values
        if isinstance(value, (dict, list)):
            try:
                formatted = json.dumps(value, indent=2, ensure_ascii=False)
                return CommandResult(True, f"[bold cyan]{bucket}/{key}:[/]\n{formatted}")
            except (TypeError, ValueError):
                pass
        return CommandResult(True, f"{bucket}/{key}: {value}")

    elif action == "keys":
        bucket = args.get("bucket", "")
        if not bucket:
            return CommandResult(False, "Usage: kv keys <bucket>")

        keys = await client.list_kv_keys(bucket)
        if not keys:
            return CommandResult(True, f"No keys in bucket: {bucket}")
        lines = [f"[bold cyan]Keys in {bucket} ({len(keys)}):[/]"]
        for k in keys:
            lines.append(f"  {k}")
        return CommandResult(True, "\n".join(lines))

    return CommandResult(False, "Usage: kv <buckets|get|keys> [bucket] [key]")


# ============================================================================
# Command implementations - Users
# ============================================================================

async def cmd_users(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show users or user stats."""
    action = args.get("action", "list").lower()

    if action == "list" or action == "refresh":
        users = await client.get_userlist()
        if not users:
            return CommandResult(True, "No users online (or not connected to channel)")
        
        # Sort by rank descending, then name
        users_sorted = sorted(users, key=lambda u: (-u.get("rank", 0), u.get("name", "").lower()))
        
        lines = [f"[bold cyan]Online users ({len(users)}):[/]"]
        for user in users_sorted:
            name = user.get("name", "?")
            rank = user.get("rank", 0)
            afk = user.get("afk", False)
            afk_str = " [dim](AFK)[/]" if afk else ""
            rank_badge = "★" if rank >= 3 else "◆" if rank >= 2 else "○"
            lines.append(f"  {rank_badge} {name}{afk_str}")
        return CommandResult(True, "\n".join(lines))

    elif action == "stats":
        username = args.get("username", "").strip()
        if not username:
            return CommandResult(False, "Usage: users stats <username>")
        return await cmd_user_stats(app, client, {"username": username}, raw_args)

    elif action == "leaderboard" or action == "top":
        return await cmd_leaderboard(app, client, args, raw_args)

    return CommandResult(False, "Usage: users <list|stats|leaderboard> [username]")


async def cmd_user_stats(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show stats for a user."""
    username = args.get("username", "").strip()
    if not username:
        return CommandResult(False, "Usage: stats <username>")

    stats = await client.get_user_stats(username)

    if stats is None:
        return CommandResult(
            True,
            f"Could not load stats for {username}\n"
            "(userstats service may not be running)"
        )

    lines = [f"[bold cyan]Stats for {username}:[/]"]

    # Messages
    messages = stats.get("messages", {})
    if isinstance(messages, dict):
        total = sum(messages.values()) if messages else 0
    elif isinstance(messages, (int, float)):
        total = int(messages)
    else:
        total = 0
    if total:
        lines.append(f"  [bold]Messages:[/] {total:,}")

    # Kudos
    kudos = stats.get("kudos_plusplus", 0) or stats.get("kudos", 0)
    if kudos:
        lines.append(f"  [bold]Kudos:[/] {kudos:,}")

    # Activity time
    activity = stats.get("activity", {})
    if isinstance(activity, dict) and activity:
        total_hours = sum(
            (ch.get("total_seconds", 0) if isinstance(ch, dict) else 0) / 3600
            for ch in activity.values()
        )
        if total_hours > 0:
            lines.append(f"  [bold]Time:[/] {total_hours:.1f} hours")

    # First/last seen
    first_seen = stats.get("first_seen")
    if first_seen:
        lines.append(f"  [bold]First seen:[/] {first_seen}")
    
    last_seen = stats.get("last_seen")
    if last_seen:
        lines.append(f"  [bold]Last seen:[/] {last_seen}")

    if len(lines) == 1:
        lines.append("  (no stats recorded)")
        lines.append(f"  [dim]Raw: {stats}[/]")

    return CommandResult(True, "\n".join(lines))


async def cmd_leaderboard(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show channel leaderboards."""
    top = await client.get_top_users(limit=10)

    if not top:
        return CommandResult(
            True,
            "No leaderboard data available\n"
            "(userstats service may not be running)"
        )

    lines = ["[bold cyan]Top Chatters:[/]"]
    for i, user in enumerate(top, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:2}."
        name = user.get("username", "?")
        count = user.get("count", 0)
        lines.append(f"  {medal} {name}: {count:,}")

    return CommandResult(True, "\n".join(lines))


async def cmd_user_activity(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show activity timeline for a user."""
    username = args.get("username", "").strip()

    if not username:
        return CommandResult(False, "Usage: activity <username>")

    activity = await client.get_user_activity(username)

    if not activity:
        return CommandResult(True, f"No activity data for {username}")

    lines = [f"[bold cyan]Activity for {username}:[/]"]

    # Hourly breakdown if available
    if "hourly" in activity:
        lines.append("\n[bold]Hourly Activity:[/]")
        hourly = activity["hourly"]
        max_val = max(hourly.values()) if hourly else 1
        for hour in range(24):
            count = hourly.get(str(hour), 0)
            bar_len = int((count / max_val) * 20) if max_val else 0
            bar = "█" * bar_len
            lines.append(f"  {hour:02d}:00 [{count:4}] {bar}")

    # Daily breakdown if available
    if "daily" in activity:
        lines.append("\n[bold]Daily Activity:[/]")
        for day, count in activity["daily"].items():
            lines.append(f"  {day}: {count:,}")

    # Peak times
    if "peak_hour" in activity:
        lines.append(f"\n[bold]Peak Hour:[/] {activity['peak_hour']}:00")

    if "first_seen" in activity:
        lines.append(f"[bold]First Seen:[/] {activity['first_seen']}")

    if "last_seen" in activity:
        lines.append(f"[bold]Last Seen:[/] {activity['last_seen']}")

    return CommandResult(True, "\n".join(lines))


async def cmd_user_kudos(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show kudos given/received for a user."""
    username = args.get("username", "").strip()

    if not username:
        return CommandResult(False, "Usage: kudos <username>")

    kudos = await client.get_user_kudos(username)

    if not kudos:
        return CommandResult(True, f"No kudos data for {username}")

    lines = [f"[bold cyan]Kudos for {username}:[/]"]

    received = kudos.get("received", [])
    given = kudos.get("given", [])

    total_received = kudos.get("total_received", len(received))
    total_given = kudos.get("total_given", len(given))

    lines.append(f"\n[bold green]Received:[/] {total_received:,}")
    for item in received[:10]:
        from_user = item.get("from", item.get("username", "?"))
        count = item.get("count", 1)
        lines.append(f"  {from_user}: {count}")

    lines.append(f"\n[bold blue]Given:[/] {total_given:,}")
    for item in given[:10]:
        to_user = item.get("to", item.get("username", "?"))
        count = item.get("count", 1)
        lines.append(f"  {to_user}: {count}")

    return CommandResult(True, "\n".join(lines))


async def cmd_user_messages(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show recent messages from a user."""
    username = args.get("username", "").strip()
    limit = int(args.get("limit", "20"))

    if not username:
        return CommandResult(False, "Usage: messages <username> [limit]")

    messages = await client.get_user_messages(username, limit=limit)

    if not messages:
        return CommandResult(True, f"No messages found for {username}")

    lines = [f"[bold cyan]Recent Messages from {username} ({len(messages)}):[/]"]

    for msg in messages:
        text = msg.get("message", msg.get("text", "?"))[:80]
        timestamp = msg.get("timestamp", "")[:19]  # Trim to datetime
        lines.append(f"  [dim]{timestamp}[/] {text}")

    return CommandResult(True, "\n".join(lines))


async def cmd_population(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show channel population stats."""
    pop = await client.get_channel_population()

    if not pop:
        return CommandResult(
            True,
            "No population data available\n"
            "(userstats service may not be running)"
        )

    lines = ["[bold cyan]Channel Population:[/]"]

    current = pop.get("current", 0)
    peak = pop.get("peak", 0)
    avg = pop.get("average", 0)

    lines.append(f"\n  [bold]Current:[/] {current}")
    lines.append(f"  [bold]Peak:[/] {peak}")
    lines.append(f"  [bold]Average:[/] {avg:.1f}")

    # Hourly if available
    if "hourly" in pop:
        lines.append("\n[bold]Hourly Averages:[/]")
        hourly = pop["hourly"]
        for hour in range(24):
            val = hourly.get(str(hour), 0)
            bar_len = int((val / (peak or 1)) * 15)
            bar = "█" * bar_len
            lines.append(f"  {hour:02d}:00 [{val:4.1f}] {bar}")

    return CommandResult(True, "\n".join(lines))


async def cmd_media_history(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show media history for the channel."""
    limit = int(args.get("limit", "20"))

    history = await client.get_media_history(limit=limit)

    if not history:
        return CommandResult(
            True,
            "No media history available\n"
            "(userstats service may not be running)"
        )

    lines = [f"[bold cyan]Media History ({len(history)} entries):[/]"]

    for entry in history:
        title = entry.get("title", "?")[:50]
        queued_by = entry.get("queuedby", entry.get("queued_by", "?"))
        media_type = entry.get("type", "?")
        timestamp = entry.get("timestamp", "")[:16]

        lines.append(f"  [dim]{timestamp}[/] [{media_type}] {title}")
        lines.append(f"              [dim]queued by {queued_by}[/]")

    return CommandResult(True, "\n".join(lines))


async def cmd_services(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Discover and show status of all kryten services."""
    if not client.is_connected:
        return CommandResult(False, "Not connected")

    services = await client.discover_services()

    if not services:
        return CommandResult(True, "No services responded")

    lines = ["[bold cyan]Kryten Services:[/]"]

    for name, info in services.items():
        if info.get("online"):
            status = "[green]●[/] ONLINE"
            version = info.get("version", "?")
            uptime = info.get("uptime_seconds", info.get("uptime", 0))
            
            # Format uptime
            if uptime:
                hours = int(uptime) // 3600
                mins = (int(uptime) % 3600) // 60
                uptime_str = f"{hours}h {mins}m" if hours else f"{mins}m"
            else:
                uptime_str = "?"
            
            service_name = info.get("service", name)
            lines.append(
                f"  {status} [bold]{service_name:15}[/] "
                f"v{version} (up {uptime_str})"
            )
            
            # Show metrics endpoint if available
            metrics_endpoint = info.get("metrics_endpoint")
            if metrics_endpoint:
                lines.append(f"      [dim]metrics:[/] {metrics_endpoint}")
            
            # Show CyTube connection info for robot
            if name == "robot" and info.get("cytube_connected"):
                channel = info.get("channel", "?")
                domain = info.get("domain", "?")
                lines.append(f"      [dim]channel:[/] {domain}/{channel}")
        else:
            lines.append(f"  [red]○[/] OFFLINE [dim]{name}[/]")

    return CommandResult(True, "\n".join(lines))


# ============================================================================
# Command implementations - LLM debugging
# ============================================================================

async def cmd_llmlog(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show recent LLM context log entries."""
    if not client.is_connected:
        return CommandResult(False, "Not connected")

    try:
        limit = int(args.get("limit", "10"))
    except ValueError:
        limit = 10

    entries = await client.llm_get_context_log(limit=limit)

    if not entries:
        return CommandResult(True, "[dim]No LLM context log entries[/]")

    lines = ["[bold cyan]LLM Context Log[/] (most recent first)"]

    for idx, entry in enumerate(reversed(entries)):
        timestamp = entry.get("timestamp", "?")[:19].replace("T", " ")
        correlation_id = entry.get("correlation_id", "?")[:8]
        username = entry.get("username", "?")
        trigger = entry.get("trigger_type", "?")
        success = entry.get("success", True)
        response = entry.get("response_text", "")[:60]

        if response and len(entry.get("response_text", "")) > 60:
            response += "..."

        status = "[green]✓[/]" if success else "[red]✗[/]"

        lines.append(
            f"\n[dim]{timestamp}[/] {status} [bold]#{idx}[/] "
            f"[cyan]{correlation_id}[/]"
        )
        lines.append(
            f"  User: [yellow]{username}[/] | Trigger: {trigger}"
        )
        if response:
            lines.append(f"  Response: [dim]{response}[/]")

    lines.append(
        f"\n[dim]Use 'llmshow <#>' for full details[/]"
    )

    return CommandResult(True, "\n".join(lines))


async def cmd_llmshow(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show full details of an LLM context entry."""
    if not client.is_connected:
        return CommandResult(False, "Not connected")

    identifier = args.get("identifier", "").strip()
    if not identifier:
        return CommandResult(False, "Usage: llmshow <index or correlation_id>")

    # Try as index first
    entry = None
    if identifier.startswith("#"):
        identifier = identifier[1:]

    try:
        index = int(identifier)
        entry = await client.llm_get_context_entry(index=index)
    except ValueError:
        # Treat as correlation ID
        entry = await client.llm_get_context_entry(correlation_id=identifier)

    if not entry:
        return CommandResult(False, f"Entry not found: {identifier}")

    lines = ["[bold cyan]LLM Context Entry[/]"]
    
    # Header info
    lines.append(f"\n[bold]Correlation ID:[/] {entry.get('correlation_id', '?')}")
    lines.append(f"[bold]Timestamp:[/] {entry.get('timestamp', '?')}")
    lines.append(f"[bold]Username:[/] {entry.get('username', '?')}")
    lines.append(f"[bold]Trigger:[/] {entry.get('trigger_type', '?')}")
    lines.append(f"[bold]Success:[/] {entry.get('success', '?')}")

    # Trigger message
    lines.append(f"\n[bold yellow]Trigger Message:[/]")
    lines.append(f"  {entry.get('trigger_message', '(none)')}")

    # Context/messages sent to LLM
    context = entry.get("context", [])
    if context:
        lines.append(f"\n[bold yellow]Messages Sent to LLM:[/] ({len(context)} messages)")
        for msg in context:
            role = msg.get("role", "?")
            content = msg.get("content", "")
            # Truncate long content
            if len(content) > 200:
                content = content[:200] + "..."
            role_color = {
                "system": "magenta",
                "user": "cyan",
                "assistant": "green",
            }.get(role, "white")
            lines.append(f"  [{role_color}]{role}:[/] {content}")

    # Response
    lines.append(f"\n[bold yellow]Response:[/]")
    response = entry.get("response_text", "(none)")
    lines.append(f"  {response}")

    # Timing info if available
    if "processing_ms" in entry:
        lines.append(f"\n[dim]Processing time: {entry['processing_ms']}ms[/]")

    return CommandResult(True, "\n".join(lines))


# ============================================================================
# Command implementations - Moderation
# ============================================================================

async def cmd_kick(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Kick a user from the channel."""
    username = args.get("username", "").strip()
    reason = args.get("reason", "").strip() or None
    
    if not username:
        return CommandResult(False, "Usage: kick <username> [reason]")

    await client.kick_user(username, reason)
    return CommandResult(True, f"Kicked {username}")


async def cmd_mod_ban(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Add user to persistent ban list."""
    username = args.get("username", "").strip()
    reason = args.get("reason", "").strip() or None
    
    if not username:
        return CommandResult(False, "Usage: ban <username> [reason]")

    response = await client.moderator_add(username, "ban", reason)
    
    if response.get("success"):
        data = response.get("data", {})
        msg = f"[red]Banned[/] {data.get('username', username)}"
        if data.get("reason"):
            msg += f"\n  Reason: {data['reason']}"
        return CommandResult(True, msg)
    else:
        return CommandResult(False, f"Error: {response.get('error')}")


async def cmd_mod_unban(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Remove user from persistent ban list."""
    username = args.get("username", "").strip()
    
    if not username:
        return CommandResult(False, "Usage: unban <username>")

    response = await client.moderator_remove(username)
    
    if response.get("success"):
        return CommandResult(True, f"Unbanned {username}")
    else:
        return CommandResult(False, f"Error: {response.get('error')}")


async def cmd_mod_smute(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Shadow mute a user."""
    username = args.get("username", "").strip()
    reason = args.get("reason", "").strip() or None
    
    if not username:
        return CommandResult(False, "Usage: smute <username> [reason]")

    response = await client.moderator_add(username, "smute", reason)
    
    if response.get("success"):
        data = response.get("data", {})
        msg = f"[yellow]Shadow muted[/] {data.get('username', username)}"
        if data.get("reason"):
            msg += f"\n  Reason: {data['reason']}"
        return CommandResult(True, msg)
    else:
        return CommandResult(False, f"Error: {response.get('error')}")


async def cmd_mod_unsmute(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Remove shadow mute from user."""
    username = args.get("username", "").strip()
    
    if not username:
        return CommandResult(False, "Usage: unsmute <username>")

    response = await client.moderator_remove(username)
    
    if response.get("success"):
        return CommandResult(True, f"Removed shadow mute from {username}")
    else:
        return CommandResult(False, f"Error: {response.get('error')}")


async def cmd_mod_mute(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Visible mute a user."""
    username = args.get("username", "").strip()
    reason = args.get("reason", "").strip() or None
    
    if not username:
        return CommandResult(False, "Usage: mute <username> [reason]")

    response = await client.moderator_add(username, "mute", reason)
    
    if response.get("success"):
        data = response.get("data", {})
        msg = f"[orange3]Muted[/] {data.get('username', username)}"
        if data.get("reason"):
            msg += f"\n  Reason: {data['reason']}"
        return CommandResult(True, msg)
    else:
        return CommandResult(False, f"Error: {response.get('error')}")


async def cmd_mod_unmute(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Remove visible mute from user."""
    username = args.get("username", "").strip()
    
    if not username:
        return CommandResult(False, "Usage: unmute <username>")

    response = await client.moderator_remove(username)
    
    if response.get("success"):
        return CommandResult(True, f"Unmuted {username}")
    else:
        return CommandResult(False, f"Error: {response.get('error')}")


async def cmd_mod_list(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """List all moderated users."""
    filter_action = args.get("filter", "").strip() or None

    response = await client.moderator_list(filter_action)
    
    if not response.get("success"):
        return CommandResult(False, f"Error: {response.get('error')}")

    data = response.get("data", {})
    entries = data.get("entries", [])

    if not entries:
        return CommandResult(True, "No moderation entries found")

    lines = [f"[bold cyan]Moderation List ({len(entries)} entries):[/]"]
    
    for entry in entries:
        action = entry.get("action", "?")
        action_color = {"ban": "red", "smute": "yellow", "mute": "orange3"}.get(action, "white")
        username = entry.get("username", "?")
        reason = entry.get("reason", "")[:30] or "(no reason)"
        lines.append(f"  [{action_color}]{action:6}[/] {username}: {reason}")

    return CommandResult(True, "\n".join(lines))


async def cmd_mod_check(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Check moderation status of a user."""
    username = args.get("username", "").strip()
    
    if not username:
        return CommandResult(False, "Usage: modcheck <username>")

    response = await client.moderator_check(username)
    
    if not response.get("success"):
        return CommandResult(False, f"Error: {response.get('error')}")

    data = response.get("data", {})
    
    if not data.get("entry"):
        return CommandResult(True, f"User {username} is [green]not moderated[/]")

    entry = data["entry"]
    action = entry.get("action", "?")
    action_color = {"ban": "red", "smute": "yellow", "mute": "orange3"}.get(action, "white")
    
    lines = [f"[bold cyan]Moderation Status: {entry.get('username', username)}[/]"]
    lines.append(f"  [bold]Action:[/] [{action_color}]{action}[/]")
    lines.append(f"  [bold]Reason:[/] {entry.get('reason') or '(none)'}")
    lines.append(f"  [bold]Moderator:[/] {entry.get('moderator', '?')}")
    lines.append(f"  [bold]Added:[/] {entry.get('timestamp', '?')}")
    
    if entry.get("ips"):
        # Mask IPs for privacy
        masked = [f"{ip.split('.')[0]}.x.x.x" for ip in entry["ips"]]
        lines.append(f"  [bold]IPs:[/] {', '.join(masked)}")

    return CommandResult(True, "\n".join(lines))


async def cmd_mod_patterns(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """List or manage banned username patterns."""
    action = args.get("action", "list").lower()

    if action == "list":
        response = await client.moderator_patterns_list()
        
        if not response.get("success"):
            return CommandResult(False, f"Error: {response.get('error')}")

        data = response.get("data", {})
        patterns = data.get("patterns", [])

        if not patterns:
            return CommandResult(True, "No patterns configured")

        lines = [f"[bold cyan]Banned Username Patterns ({len(patterns)}):[/]"]
        
        for p in patterns:
            ptype = "[magenta]regex[/]" if p.get("is_regex") else "substring"
            pat_action = p.get("action", "ban")
            action_color = {"ban": "red", "smute": "yellow", "mute": "orange3"}.get(pat_action, "white")
            pattern = p.get("pattern", "?")
            desc = p.get("description", "")[:25]
            lines.append(f"  [{action_color}]{pat_action:6}[/] {ptype:12} {pattern}")
            if desc:
                lines.append(f"         [dim]{desc}[/]")

        return CommandResult(True, "\n".join(lines))

    elif action == "add":
        pattern = args.get("pattern", "").strip()
        if not pattern:
            return CommandResult(False, "Usage: patterns add <pattern> [--regex] [--smute|--mute] [--desc=TEXT]")
        
        # Parse options from raw_args
        is_regex = "--regex" in raw_args
        action_type = "ban"
        if "--smute" in raw_args:
            action_type = "smute"
        elif "--mute" in raw_args:
            action_type = "mute"
        
        description = None
        for arg in raw_args:
            if arg.startswith("--desc="):
                description = arg[7:]
        
        response = await client.moderator_patterns_add(pattern, is_regex, action_type, description)
        
        if response.get("success"):
            return CommandResult(True, f"Added pattern: {pattern}")
        else:
            return CommandResult(False, f"Error: {response.get('error')}")

    elif action == "remove":
        pattern = args.get("pattern", "").strip()
        if not pattern:
            return CommandResult(False, "Usage: patterns remove <pattern>")
        
        response = await client.moderator_patterns_remove(pattern)
        
        if response.get("success"):
            return CommandResult(True, f"Removed pattern: {pattern}")
        else:
            return CommandResult(False, f"Error: {response.get('error')}")

    return CommandResult(False, "Usage: patterns <list|add|remove> [pattern] [options]")


# ============================================================================
# Command implementations - Convenience/Show
# ============================================================================

async def cmd_show(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show various information."""
    what = args.get("what", "").lower()
    extra = args.get("extra", "")

    if what == "users" or what == "user":
        return await cmd_users(app, client, {"action": "list"}, raw_args)
    
    elif what == "playlist" or what == "pl":
        return await cmd_playlist(app, client, {"action": "show"}, raw_args)
    
    elif what == "buckets" or what == "kv":
        return await cmd_kv(app, client, {"action": "buckets"}, raw_args)
    
    elif what == "status":
        return await cmd_status(app, client, args, raw_args)
    
    elif what == "np" or what == "nowplaying" or what == "now":
        return await cmd_nowplaying(app, client, args, raw_args)
    
    elif what == "bans" or what == "modlist":
        return await cmd_mod_list(app, client, {"filter": extra}, raw_args)
    
    elif what == "patterns":
        return await cmd_mod_patterns(app, client, {"action": "list"}, raw_args)
    
    elif what == "leaderboard" or what == "top" or what == "lb":
        return await cmd_leaderboard(app, client, args, raw_args)
    
    elif what == "stats" and extra:
        return await cmd_user_stats(app, client, {"username": extra}, raw_args)

    elif what == "services" or what == "svc":
        return await cmd_services(app, client, args, raw_args)

    elif what == "history" or what == "media":
        return await cmd_media_history(app, client, {"limit": extra or "20"}, raw_args)

    elif what == "population" or what == "pop":
        return await cmd_population(app, client, args, raw_args)

    return CommandResult(False, 
        "Usage: show <users|playlist|buckets|status|np|bans|patterns|leaderboard|services|history|population>\n"
        "       show stats <username>")


# ============================================================================
# Command implementations - Utility
# ============================================================================

async def cmd_help(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show help information."""
    command_name = args.get("command", "").strip()

    if command_name:
        return CommandResult(True, f"Help for '{command_name}' - use 'help' for all commands")

    help_text = """
[bold cyan]Kryten Shell Commands[/]

[bold]Connection:[/]
  connect           Connect to NATS server
  disconnect        Disconnect from server
  channel [name]    Join channel or show current
  discover          Discover available channels
  services          Show status of all kryten services (alias: svc, ping)

[bold]Chat:[/]
  msg <message>     Send a chat message
  pm <user> <msg>   Send a private message

[bold]Playlist:[/]
  playlist          Show playlist (alias: pl, list)
  nowplaying        Show current video (alias: np)
  skip              Vote to skip current video
  pause             Pause playback
  play              Resume playback
  seek <seconds>    Seek to timestamp
  history [n]       Show media history (alias: media)

[bold]Users & Stats (kryten-userstats):[/]
  users             List online users
  stats <user>      Show comprehensive user statistics
  activity <user>   Show activity timeline for a user
  kudos <user>      Show kudos given/received
  messages <user>   Show recent messages from a user
  leaderboard       Show top chatters (alias: top, lb)
  population        Show channel population stats

[bold]Moderation (kryten-moderator):[/]
  kick <user>       Kick user from channel
  ban <user>        Persistent ban (kicks on join)
  unban <user>      Remove from ban list
  smute <user>      Shadow mute (invisible to user)
  unsmute <user>    Remove shadow mute
  mute <user>       Visible mute (user is notified)
  unmute <user>     Remove visible mute
  modlist           List all moderated users
  modcheck <user>   Check user's moderation status
  patterns          Manage banned username patterns

[bold]KV Store:[/]
  kv buckets        List KV buckets
  kv keys <bucket>  List keys in bucket
  kv get <b> <k>    Get value from bucket

[bold]Convenience:[/]
  show <what>       Show users/playlist/buckets/status/np/bans/services

[bold]Utility:[/]
  help [cmd]        Show this help
  clear             Clear output log
  refresh           Refresh data
  status            Show connection status
  quit              Exit shell

[dim]Tab completion available for commands and arguments.[/]
"""
    return CommandResult(True, help_text)


async def cmd_clear(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Clear output log."""
    app.action_clear_output()
    return CommandResult(True)


async def cmd_refresh(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Refresh data from server."""
    # Re-fetch common data
    users = await client.get_userlist()
    playlist = await client.get_playlist()
    
    return CommandResult(True, 
        f"Refreshed: {len(users)} users, {len(playlist)} playlist items")


async def cmd_quit(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Exit the shell."""
    app.exit()
    return CommandResult(True)


async def cmd_status(
    app: "KrytenShellApp",
    client: "KrytenClientWrapper",
    args: dict[str, Any],
    raw_args: list[str],
) -> CommandResult:
    """Show connection status."""
    connected = "[green]Connected[/]" if client.is_connected else "[red]Disconnected[/]"
    channel = client.current_channel or "[dim]None[/]"
    nats_url = client.config.nats.url

    status = f"""[bold cyan]Connection Status[/]
  NATS: {nats_url} ({connected})
  Channel: {channel}"""
    return CommandResult(True, status)
