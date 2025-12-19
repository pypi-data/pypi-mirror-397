"""Kryten client wrapper for the TUI application.

Wraps kryten-py with TUI-specific event handling and state management.
"""

import logging
from typing import TYPE_CHECKING, Any

from kryten import KrytenClient  # type: ignore[import-untyped]

from kryten_shell.config import ShellConfig

if TYPE_CHECKING:
    from kryten_shell.app import KrytenShellApp

logger = logging.getLogger(__name__)


def _build_client_config(
    nats_url: str,
    channel: str = "_discovery",
    domain: str = "cytu.be",
) -> dict[str, Any]:
    """Build a KrytenClient-compatible config dict.

    Args:
        nats_url: NATS server URL.
        channel: Channel name (use "_discovery" for discovery).
        domain: CyTube domain.

    Returns:
        Config dict for KrytenClient.
    """
    return {
        "nats": {
            "servers": [nats_url],
        },
        "channels": [
            {
                "domain": domain,
                "channel": channel,
            }
        ],
    }


class KrytenClientWrapper:
    """Wrapper around KrytenClient for TUI integration.

    Provides:
    - Connection management with status updates
    - Event subscription and routing to views
    - High-level API for common operations
    - KV store access
    - Cached data for tab completion
    """

    def __init__(
        self,
        config: ShellConfig,
        app: "KrytenShellApp",
    ) -> None:
        """Initialize the client wrapper.

        Args:
            config: Shell configuration.
            app: The main TUI application.
        """
        self.config = config
        self.app = app
        self._client: KrytenClient | None = None
        self._connected: bool = False
        self._current_channel: str | None = config.channel
        self._current_domain: str = config.domain or "cytu.be"

        # Cached data for tab completion (non-blocking access)
        self._cached_userlist: list[dict[str, Any]] = []
        self._cached_buckets: list[str] = []
        self._cached_keys: dict[str, list[str]] = {}
        self._cached_channels: list[dict[str, str]] = []

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS."""
        return self._connected

    @property
    def current_channel(self) -> str | None:
        """Get the current channel name."""
        return self._current_channel

    async def connect(self) -> bool:
        """Connect to the NATS server.

        Returns:
            True if connection succeeded.
        """
        try:
            logger.info(f"Connecting to {self.config.nats.url}")

            # Build config for KrytenClient
            # Use placeholder channel for initial connection (will discover later)
            client_config = _build_client_config(
                nats_url=self.config.nats.url,
                channel=self._current_channel or "_discovery",
                domain=self._current_domain,
            )

            self._client = KrytenClient(client_config)
            await self._client.connect()

            self._connected = True
            self.app.update_status(connected=True)
            self.app.log_event("connect", {"url": self.config.nats.url})

            # If we have a channel configured, join it
            if self._current_channel:
                await self.join_channel(self._current_channel)

            return True

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self._connected = False
            self.app.update_status(connected=False)
            self.app.log_event("error", {"message": f"Connection failed: {e}"})
            return False

    async def disconnect(self) -> None:
        """Disconnect from the NATS server."""
        if self._client:
            try:
                await self._client.disconnect()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        self._connected = False
        self._client = None
        self.app.update_status(connected=False, channel=None)
        self.app.log_event("disconnect", {})

    async def disconnect_quiet(self) -> None:
        """Disconnect without logging (for shutdown)."""
        if self._client:
            try:
                await self._client.disconnect()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        self._connected = False
        self._client = None

    async def join_channel(self, channel: str, domain: str | None = None) -> None:
        """Join a channel and subscribe to its events.

        Args:
            channel: The channel name to join.
            domain: Optional domain (defaults to current domain).
        """
        if not self._client or not self._connected:
            logger.warning("Cannot join channel: not connected")
            return

        self._current_channel = channel
        if domain:
            self._current_domain = domain
        self.app.update_status(channel=channel)

        # Subscribe to channel events
        await self._subscribe_channel_events(channel)

        # Load initial state
        await self._load_channel_state(channel)

        self.app.log_event("system", {"message": f"Joined channel: {self._current_domain}/{channel}"})

    async def _subscribe_channel_events(self, channel: str) -> None:
        """Subscribe to events for a channel.

        Args:
            channel: The channel name.
        """
        if not self._client:
            return

        # Subscribe to chat events
        await self._client.subscribe(
            f"kryten.events.cytube.{channel}.chat",
            self._handle_chat_event,
        )

        # Subscribe to media change events
        await self._client.subscribe(
            f"kryten.events.cytube.{channel}.changemedia",
            self._handle_media_event,
        )

        # Subscribe to playlist events
        await self._client.subscribe(
            f"kryten.events.cytube.{channel}.queue",
            self._handle_queue_event,
        )

        await self._client.subscribe(
            f"kryten.events.cytube.{channel}.delete",
            self._handle_delete_event,
        )

        # Subscribe to user events
        await self._client.subscribe(
            f"kryten.events.cytube.{channel}.userJoin",
            self._handle_user_join_event,
        )

        await self._client.subscribe(
            f"kryten.events.cytube.{channel}.userLeave",
            self._handle_user_leave_event,
        )

        await self._client.subscribe(
            f"kryten.events.cytube.{channel}.userlist",
            self._handle_userlist_event,
        )

        logger.info(f"Subscribed to channel events: {channel}")

    async def _load_channel_state(self, channel: str) -> None:
        """Load initial channel state from KV store.

        Args:
            channel: The channel name.
        """
        try:
            # Load playlist
            playlist = await self.get_playlist()
            if playlist and self.app._playlist_view:
                current = await self.get_current_media()
                current_uid = current.get("uid") if current else None
                self.app._playlist_view.update_playlist(playlist, current_uid)

            # Load current media
            current = await self.get_current_media()
            if current and self.app._chat_view:
                self.app._chat_view.update_current_video(
                    current.get("title", "Unknown"),
                    current.get("queueby"),
                )

            # Refresh KV view
            if self.app._kv_view:
                await self.app._kv_view.reload_data()

        except Exception as e:
            logger.warning(f"Failed to load channel state: {e}")

    # Event handlers

    async def _handle_chat_event(self, event: Any) -> None:
        """Handle chat message event."""
        data = event.data if hasattr(event, "data") else event
        if isinstance(data, dict):
            username = data.get("username", "?")
            msg = data.get("msg", "")
            self.app.log_chat(username, msg)
            self.app.log_event("chat", data)

    async def _handle_media_event(self, event: Any) -> None:
        """Handle media change event."""
        data = event.data if hasattr(event, "data") else event
        if isinstance(data, dict):
            title = data.get("title", "Unknown")
            if self.app._chat_view:
                self.app._chat_view.update_current_video(title)
            self.app.log_event("changemedia", data)

    async def _handle_queue_event(self, event: Any) -> None:
        """Handle queue add event."""
        data = event.data if hasattr(event, "data") else event
        self.app.log_event("queue", data if isinstance(data, dict) else {})

    async def _handle_delete_event(self, event: Any) -> None:
        """Handle queue delete event."""
        data = event.data if hasattr(event, "data") else event
        self.app.log_event("delete", data if isinstance(data, dict) else {})

    async def _handle_user_join_event(self, event: Any) -> None:
        """Handle user join event."""
        data = event.data if hasattr(event, "data") else event
        self.app.log_event("userJoin", data if isinstance(data, dict) else {})

    async def _handle_user_leave_event(self, event: Any) -> None:
        """Handle user leave event."""
        data = event.data if hasattr(event, "data") else event
        self.app.log_event("userLeave", data if isinstance(data, dict) else {})

    async def _handle_userlist_event(self, event: Any) -> None:
        """Handle userlist event."""
        data = event.data if hasattr(event, "data") else event
        if isinstance(data, list):
            # Cache for tab completion
            self._cached_userlist = data
            self.app.update_status(users=len(data))
            self.app.log_event("userlist", {"count": len(data)})

    # High-level API methods

    async def discover_channels(self) -> list[dict[str, Any]]:
        """Discover available channels from kryten-robot.

        Returns:
            List of channel dicts with 'domain', 'channel', and 'connected' keys.
        """
        if not self._client:
            return []

        try:
            # Use kryten-py's built-in channel discovery
            channels = await self._client.get_channels(timeout=5.0)
            logger.info(f"Discovered {len(channels)} channel(s)")
            # Cache for tab completion
            self._cached_channels = channels
            return channels
        except TimeoutError:
            logger.warning("Channel discovery timed out")
            return []
        except Exception as e:
            logger.warning(f"Channel discovery failed: {e}")
            return []

    async def send_chat(self, message: str) -> None:
        """Send a chat message.

        Args:
            message: The message to send.
        """
        if not self._client or not self._current_channel:
            return

        await self._client.publish(
            f"kryten.commands.cytube.{self._current_channel}.chat",
            {"msg": message},
        )

    async def get_playlist(self) -> list[dict]:
        """Get the current playlist.

        Returns:
            List of playlist items.
        """
        if not self._client or not self._current_channel:
            return []

        bucket = f"kryten_{self._current_channel}_playlist"
        return await self.kv_get(bucket, "items") or []

    async def get_current_media(self) -> dict | None:
        """Get the currently playing media.

        Returns:
            Current media info or None.
        """
        if not self._client or not self._current_channel:
            return None

        bucket = f"kryten_{self._current_channel}_playlist"
        return await self.kv_get(bucket, "current")

    async def add_to_playlist(self, url: str) -> None:
        """Add a URL to the playlist.

        Args:
            url: The video URL to add.
        """
        if not self._client or not self._current_channel:
            return

        await self._client.publish(
            f"kryten.commands.cytube.{self._current_channel}.queue",
            {"url": url},
        )

    async def skip_video(self) -> None:
        """Skip the current video."""
        if not self._client or not self._current_channel:
            return

        await self._client.publish(
            f"kryten.commands.cytube.{self._current_channel}.skip",
            {},
        )

    # KV Store methods

    async def list_kv_buckets(self) -> list[str]:
        """List available KV buckets.

        KV buckets in JetStream are backed by streams prefixed with 'KV_'.

        Returns:
            List of bucket names.
        """
        if not self._client or not self._client._nats:
            return []

        try:
            js = self._client._nats.jetstream()
            streams = await js.streams_info()

            # KV stores are backed by streams prefixed with "KV_"
            buckets = []
            for stream in streams:
                name = stream.config.name
                if name.startswith("KV_"):
                    # Remove the KV_ prefix to get bucket name
                    buckets.append(name[3:])

            result = sorted(buckets)
            # Cache for tab completion
            self._cached_buckets = result
            return result
        except Exception as e:
            logger.warning(f"Failed to list KV buckets: {e}")
            return []

    async def list_kv_keys(self, bucket: str) -> list[str]:
        """List keys in a KV bucket.

        Args:
            bucket: The bucket name.

        Returns:
            List of key names.
        """
        if not self._client:
            return []

        try:
            keys = await self._client.kv_keys(bucket)
            # Cache for tab completion
            self._cached_keys[bucket] = keys
            return keys
        except Exception as e:
            logger.warning(f"Failed to list keys in {bucket}: {e}")
            return []

    async def kv_get(self, bucket: str, key: str) -> Any:
        """Get a value from a KV bucket.

        Args:
            bucket: The bucket name.
            key: The key name.

        Returns:
            The value or None.
        """
        if not self._client:
            return None

        try:
            return await self._client.kv_get(bucket, key, parse_json=True)
        except Exception as e:
            logger.warning(f"Failed to get {bucket}/{key}: {e}")
            return None
    # Userstats service methods

    async def query_userstats(
        self,
        command: str,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Query the userstats service via NATS request/reply.

        Args:
            command: The userstats command (e.g., "user.stats", "channel.top_users").
            **kwargs: Additional command parameters.

        Returns:
            Response data dict or None on failure.
        """
        if not self._client:
            return None

        try:
            request = {
                "service": "userstats",
                "command": command,
                **kwargs,
            }

            response = await self._client.nats_request(
                "kryten.userstats.command",
                request,
                timeout=5.0,
            )

            if response.get("success"):
                return response.get("data", {})
            else:
                error = response.get("error", "Unknown error")
                logger.warning(f"Userstats query failed: {error}")
                return None

        except TimeoutError:
            logger.warning("Userstats query timed out")
            return None
        except Exception as e:
            logger.warning(f"Userstats query failed: {e}")
            return None

    async def get_user_stats(self, username: str) -> dict[str, Any] | None:
        """Get comprehensive stats for a user.

        Args:
            username: The username to query.

        Returns:
            User stats dict or None.
        """
        return await self.query_userstats("user.stats", username=username)

    async def get_channel_stats(self) -> dict[str, Any] | None:
        """Get all channel statistics including top users, leaderboards.

        Returns:
            Channel stats dict or None.
        """
        return await self.query_userstats("channel.all_stats")

    async def get_top_users(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get top users by message count.

        Args:
            limit: Maximum number of users to return.

        Returns:
            List of user dicts with username and count.
        """
        result = await self.query_userstats(
            "channel.top_users",
            channel=self._current_channel,
            limit=limit,
        )
        if result:
            return result.get("top_users", [])
        return []

    async def get_leaderboards(self, limit: int = 10) -> dict[str, list[dict]]:
        """Get leaderboards (kudos, emotes, messages).

        Args:
            limit: Maximum entries per leaderboard.

        Returns:
            Dict with kudos, emotes, messages leaderboards.
        """
        result = await self.query_userstats("leaderboard.all", limit=limit)
        return result or {}

    async def get_user_messages(
        self, username: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get recent messages from a user.

        Args:
            username: The username to query.
            limit: Maximum messages to return.

        Returns:
            List of message dicts.
        """
        result = await self.query_userstats(
            "user.messages", username=username, limit=limit
        )
        if result:
            return result.get("messages", [])
        return []

    async def get_user_activity(self, username: str) -> dict[str, Any] | None:
        """Get activity timeline for a user.

        Args:
            username: The username to query.

        Returns:
            Activity dict with hourly/daily patterns.
        """
        return await self.query_userstats("user.activity", username=username)

    async def get_user_kudos(self, username: str) -> dict[str, Any] | None:
        """Get kudos given/received for a user.

        Args:
            username: The username to query.

        Returns:
            Kudos dict with given/received lists.
        """
        return await self.query_userstats("user.kudos", username=username)

    async def get_channel_population(self) -> dict[str, Any] | None:
        """Get channel population over time.

        Returns:
            Population stats dict.
        """
        return await self.query_userstats(
            "channel.population", channel=self._current_channel
        )

    async def get_media_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent media history for the channel.

        Args:
            limit: Maximum entries to return.

        Returns:
            List of media history entries.
        """
        result = await self.query_userstats(
            "channel.media_history", channel=self._current_channel, limit=limit
        )
        if result:
            return result.get("history", [])
        return []

    async def get_leaderboard_messages(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get message leaderboard.

        Args:
            limit: Maximum entries.

        Returns:
            List of {username, count} dicts.
        """
        result = await self.query_userstats("leaderboard.messages", limit=limit)
        if result:
            return result.get("leaderboard", [])
        return []

    async def get_leaderboard_kudos(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get kudos leaderboard.

        Args:
            limit: Maximum entries.

        Returns:
            List of {username, received, given} dicts.
        """
        result = await self.query_userstats("leaderboard.kudos", limit=limit)
        if result:
            return result.get("leaderboard", [])
        return []

    async def get_leaderboard_emotes(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get emote leaderboard.

        Args:
            limit: Maximum entries.

        Returns:
            List of {emote, count, users} dicts.
        """
        result = await self.query_userstats("leaderboard.emotes", limit=limit)
        if result:
            return result.get("leaderboard", [])
        return []

    async def get_userstats_health(self) -> dict[str, Any] | None:
        """Get userstats service health status.

        Returns:
            Health status dict.
        """
        return await self.query_userstats("system.health")

    async def get_userstats_system_stats(self) -> dict[str, Any] | None:
        """Get userstats system statistics.

        Returns:
            System stats dict.
        """
        return await self.query_userstats("system.stats")

    # ========================================================================
    # Service discovery methods
    # ========================================================================

    async def ping_service(
        self, service_subject: str, timeout: float = 2.0
    ) -> dict[str, Any] | None:
        """Ping a kryten service to check if it's online.

        Tries system.ping first, falls back to system.health for compatibility.

        Args:
            service_subject: NATS subject for the service.
            timeout: Timeout in seconds.

        Returns:
            Service info dict with name, version, uptime or None.
        """
        if not self._client:
            return None

        # Try system.ping first
        try:
            response = await self._client.nats_request(
                service_subject,
                {"service": "system", "command": "system.ping"},
                timeout=timeout,
            )

            if response.get("success"):
                return response.get("data", response)
            # If command not found, try system.health
            if "Unknown command" in response.get("error", ""):
                return await self._ping_service_health(service_subject, timeout)
            return response

        except TimeoutError:
            return None
        except Exception as e:
            logger.debug(f"Ping {service_subject} failed: {e}")
            return None

    async def _ping_service_health(
        self, service_subject: str, timeout: float = 2.0
    ) -> dict[str, Any] | None:
        """Fall back to system.health for services that don't have system.ping.

        Args:
            service_subject: NATS subject for the service.
            timeout: Timeout in seconds.

        Returns:
            Service info dict or None.
        """
        try:
            response = await self._client.nats_request(
                service_subject,
                {"service": "system", "command": "system.health"},
                timeout=timeout,
            )

            if response.get("success"):
                data = response.get("data", {})
                # Normalize to ping-like response
                return {
                    "pong": True,
                    "service": data.get("service", "unknown"),
                    "version": data.get("version", "?"),
                    "uptime_seconds": data.get("uptime_seconds", 0),
                    "status": data.get("status", "unknown"),
                }
            return None

        except Exception:
            return None

    async def discover_services(self) -> dict[str, dict[str, Any]]:
        """Discover all online kryten services.

        Returns:
            Dict mapping service name to info dict.
        """
        services = {
            "robot": "kryten.robot.command",
            "userstats": "kryten.userstats.command",
            "moderator": "kryten.moderator.command",
            "playlist": "kryten.playlist.command",
            "bingo": "kryten.bingo.command",
            "llm": "kryten.llm.command",
            "webui": "kryten.webui.command",
        }

        results = {}

        for name, subject in services.items():
            info = await self.ping_service(subject)
            if info:
                results[name] = {
                    "subject": subject,
                    "online": True,
                    **info,
                }
            else:
                results[name] = {
                    "subject": subject,
                    "online": False,
                }

        return results

    async def get_userlist(self) -> list[dict[str, Any]]:
        """Get current userlist from KV store.

        Returns:
            List of user dicts with name, rank, etc.
        """
        if not self._client or not self._current_channel:
            return []

        bucket = f"kryten_{self._current_channel}_userlist"
        users = await self.kv_get(bucket, "users")
        result = users or []
        # Cache for tab completion
        self._cached_userlist = result
        return result

    # ========================================================================
    # Moderator service methods
    # ========================================================================

    async def moderator_request(
        self,
        command: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a request to kryten-moderator service.

        Args:
            command: Command name (e.g., "entry.add", "entry.list").
            **kwargs: Additional command parameters.

        Returns:
            Response dict with success and data/error.
        """
        if not self._client:
            return {"success": False, "error": "Not connected"}

        request = {
            "service": "moderator",
            "command": command,
            "domain": self._current_domain,
            "channel": self._current_channel,
            **kwargs,
        }

        try:
            response = await self._client.nats_request(
                "kryten.moderator.command",
                request,
                timeout=5.0,
            )
            return response
        except TimeoutError:
            return {"success": False, "error": "Request timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def moderator_add(
        self,
        username: str,
        action: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Add a user to the moderator list.

        Args:
            username: Username to add.
            action: Action type (ban, smute, mute).
            reason: Optional reason.

        Returns:
            Response dict.
        """
        return await self.moderator_request(
            "entry.add",
            username=username,
            action=action,
            reason=reason,
            moderator="shell",
        )

    async def moderator_remove(self, username: str) -> dict[str, Any]:
        """Remove a user from the moderator list.

        Args:
            username: Username to remove.

        Returns:
            Response dict.
        """
        return await self.moderator_request("entry.remove", username=username)

    async def moderator_list(
        self,
        filter_action: str | None = None,
    ) -> dict[str, Any]:
        """List all moderated users.

        Args:
            filter_action: Optional filter (ban, smute, mute).

        Returns:
            Response dict with entries list.
        """
        return await self.moderator_request("entry.list", filter=filter_action)

    async def moderator_check(self, username: str) -> dict[str, Any]:
        """Check moderation status of a user.

        Args:
            username: Username to check.

        Returns:
            Response dict with entry data.
        """
        return await self.moderator_request("entry.get", username=username)

    async def moderator_patterns_list(self) -> dict[str, Any]:
        """List all banned username patterns.

        Returns:
            Response dict with patterns list.
        """
        return await self.moderator_request("pattern.list")

    async def moderator_patterns_add(
        self,
        pattern: str,
        is_regex: bool = False,
        action: str = "ban",
        description: str | None = None,
    ) -> dict[str, Any]:
        """Add a banned username pattern.

        Args:
            pattern: Pattern string (substring or regex).
            is_regex: Whether pattern is a regex.
            action: Action to take on match.
            description: Optional description.

        Returns:
            Response dict.
        """
        return await self.moderator_request(
            "pattern.add",
            pattern=pattern,
            is_regex=is_regex,
            action=action,
            added_by="shell",
            description=description,
        )

    async def moderator_patterns_remove(self, pattern: str) -> dict[str, Any]:
        """Remove a banned username pattern.

        Args:
            pattern: Pattern string to remove.

        Returns:
            Response dict.
        """
        return await self.moderator_request("pattern.remove", pattern=pattern)

    # ========================================================================
    # Playback control methods
    # ========================================================================

    async def pause(self) -> None:
        """Pause playback."""
        if self._client and self._current_channel:
            await self._client.pause(
                self._current_channel,
                domain=self._current_domain,
            )

    async def play(self) -> None:
        """Resume playback."""
        if self._client and self._current_channel:
            await self._client.play(
                self._current_channel,
                domain=self._current_domain,
            )

    async def seek(self, time: float) -> None:
        """Seek to timestamp.

        Args:
            time: Target time in seconds.
        """
        if self._client and self._current_channel:
            await self._client.seek(
                self._current_channel,
                time,
                domain=self._current_domain,
            )

    async def voteskip(self) -> None:
        """Vote to skip current video."""
        if self._client and self._current_channel:
            await self._client.voteskip(
                self._current_channel,
                domain=self._current_domain,
            )

    async def send_pm(self, username: str, message: str) -> None:
        """Send a private message.

        Args:
            username: Target username.
            message: Message text.
        """
        if self._client and self._current_channel:
            await self._client.send_pm(
                self._current_channel,
                username,
                message,
                domain=self._current_domain,
            )

    async def kick_user(self, username: str, reason: str | None = None) -> None:
        """Kick a user from the channel.

        Args:
            username: Username to kick.
            reason: Optional reason.
        """
        if self._client and self._current_channel:
            await self._client.kick_user(
                self._current_channel,
                username,
                reason,
                domain=self._current_domain,
            )

    # ========================================================================
    # LLM service methods
    # ========================================================================

    async def llm_get_context_log(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent LLM context log entries.

        Args:
            limit: Maximum entries to return.

        Returns:
            List of context log entries.
        """
        if not self._client:
            return []

        try:
            response = await self._client.nats_request(
                "kryten.llm.command",
                {"service": "llm", "command": "context.recent", "limit": limit},
                timeout=5.0,
            )

            if response.get("success"):
                return response.get("data", {}).get("entries", [])
            return []

        except Exception as e:
            logger.warning(f"Failed to get LLM context log: {e}")
            return []

    async def llm_get_context_entry(
        self, correlation_id: str | None = None, index: int | None = None
    ) -> dict[str, Any] | None:
        """Get full details for a specific LLM context log entry.

        Args:
            correlation_id: Entry correlation ID.
            index: Entry index (0 = oldest).

        Returns:
            Full context entry or None.
        """
        if not self._client:
            return None

        try:
            request = {"service": "llm", "command": "context.get"}
            if correlation_id:
                request["correlation_id"] = correlation_id
            elif index is not None:
                request["index"] = index
            else:
                return None

            response = await self._client.nats_request(
                "kryten.llm.command",
                request,
                timeout=5.0,
            )

            if response.get("success"):
                return response.get("data")
            return None

        except Exception as e:
            logger.warning(f"Failed to get LLM context entry: {e}")
            return None

    async def subscribe_llm_context_log(
        self, callback: Any
    ) -> Any:
        """Subscribe to live LLM context log stream.

        Args:
            callback: Async callback function for each log entry.

        Returns:
            Subscription object.
        """
        if not self._client:
            return None

        return await self._client.subscribe(
            "kryten.llm.context.log",
            callback,
        )