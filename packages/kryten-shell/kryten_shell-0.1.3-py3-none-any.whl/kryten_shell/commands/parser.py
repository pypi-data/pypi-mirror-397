"""Command parser for natural syntax commands."""

import asyncio
import shlex
from dataclasses import dataclass
from typing import TYPE_CHECKING

from kryten_shell.commands.base import Command, CommandRegistry, CommandResult

if TYPE_CHECKING:
    from kryten_shell.app import KrytenShellApp
    from kryten_shell.client import KrytenClientWrapper


@dataclass
class ParsedCommand:
    """A parsed command with arguments."""

    command: Command
    args: dict[str, str]
    raw_args: list[str]


class CommandParser:
    """Parser for natural syntax commands.

    Supports commands like:
    - connect
    - channel cyberia
    - playlist add https://youtube.com/...
    - msg hello everyone
    - kv get bucket key
    - help playlist
    """

    def __init__(
        self,
        registry: CommandRegistry,
        app: "KrytenShellApp",
        client: "KrytenClientWrapper | None" = None,
    ) -> None:
        """Initialize the command parser.

        Args:
            registry: The command registry.
            app: The main application.
            client: The Kryten client wrapper.
        """
        self.registry = registry
        self.app = app
        self.client = client

    def set_client(self, client: "KrytenClientWrapper") -> None:
        """Set the Kryten client.

        Args:
            client: The Kryten client wrapper.
        """
        self.client = client

    def parse(self, input_text: str) -> ParsedCommand | None:
        """Parse a command string.

        Args:
            input_text: The raw input text.

        Returns:
            ParsedCommand if valid, None otherwise.
        """
        input_text = input_text.strip()
        if not input_text:
            return None

        # Split into tokens
        try:
            tokens = shlex.split(input_text)
        except ValueError:
            # Handle unbalanced quotes
            tokens = input_text.split()

        if not tokens:
            return None

        # First token is the command name
        command_name = tokens[0].lower()
        raw_args = tokens[1:]

        # Look up the command
        command = self.registry.get(command_name)
        if not command:
            return None

        # Parse arguments
        args = self._parse_args(command, raw_args)

        return ParsedCommand(
            command=command,
            args=args,
            raw_args=raw_args,
        )

    def _parse_args(self, command: Command, raw_args: list[str]) -> dict[str, str]:
        """Parse arguments for a command.

        Args:
            command: The command definition.
            raw_args: Raw argument tokens.

        Returns:
            Dictionary mapping argument names to values.
        """
        args: dict[str, str] = {}

        # For simple commands, map positionally
        for i, cmd_arg in enumerate(command.args):
            if i < len(raw_args):
                # If this is the last argument, join remaining tokens
                if i == len(command.args) - 1:
                    args[cmd_arg.name] = " ".join(raw_args[i:])
                else:
                    args[cmd_arg.name] = raw_args[i]
            elif cmd_arg.default is not None:
                args[cmd_arg.name] = cmd_arg.default
            elif not cmd_arg.required:
                args[cmd_arg.name] = ""

        return args

    async def execute(self, input_text: str) -> CommandResult:
        """Parse and execute a command.

        Args:
            input_text: The raw input text.

        Returns:
            The command result.
        """
        parsed = self.parse(input_text)

        if not parsed:
            # Check if it looks like a command attempt
            if input_text.strip():
                return CommandResult(
                    success=False,
                    message=f"Unknown command: {input_text.split()[0]}",
                )
            return CommandResult(success=True)  # Empty input is OK

        # Execute the command
        try:
            result = await parsed.command.handler(
                app=self.app,
                client=self.client,
                args=parsed.args,
                raw_args=parsed.raw_args,
            )
            return result
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error executing {parsed.command.name}: {e}",
            )

    def get_completions(self, partial: str) -> list[str]:
        """Get command completions for partial input (sync wrapper).

        Args:
            partial: Partial input text.

        Returns:
            List of possible completions.
        """
        # Try to run async version if we have an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, create a task
            # But we can't await here, so return cached/sync results
            return self._get_completions_sync(partial)
        except RuntimeError:
            # No running loop, use sync version
            return self._get_completions_sync(partial)

    async def get_completions_async(self, partial: str) -> list[str]:
        """Get command completions for partial input (async version).

        This version fetches data on demand for better completion.

        Args:
            partial: Partial input text.

        Returns:
            List of possible completions.
        """
        # Preserve trailing space - it indicates user wants next argument
        # Only strip leading whitespace and lowercase for matching
        partial_lower = partial.lstrip().lower()
        completions = []

        # If no space, complete command names
        if " " not in partial_lower:
            partial_stripped = partial_lower.strip()
            for command in self.registry.list_commands():
                if command.name.startswith(partial_stripped):
                    completions.append(command.name)
                for alias in command.aliases:
                    if alias.startswith(partial_stripped):
                        completions.append(alias)
        else:
            # Parse command and get argument completions
            # Keep trailing space intact for proper arg position detection
            completions = await self._get_argument_completions_async(partial_lower)

        return sorted(set(completions))

    def _get_completions_sync(self, partial: str) -> list[str]:
        """Synchronous completion using cached data only.

        Args:
            partial: Partial input text.

        Returns:
            List of possible completions.
        """
        # Preserve trailing space - it indicates user wants next argument
        # Only strip leading whitespace and lowercase for matching
        partial_lower = partial.lstrip().lower()
        completions = []

        # If no space, complete command names
        if " " not in partial_lower:
            partial_stripped = partial_lower.strip()
            for command in self.registry.list_commands():
                if command.name.startswith(partial_stripped):
                    completions.append(command.name)
                for alias in command.aliases:
                    if alias.startswith(partial_stripped):
                        completions.append(alias)
        else:
            # Parse command and get argument completions
            # Keep trailing space intact for proper arg position detection
            completions = self._get_argument_completions(partial_lower)

        return sorted(set(completions))

    def _get_argument_completions(self, partial: str) -> list[str]:
        """Get argument completions for a partial command (sync).

        Args:
            partial: Partial input text with command.

        Returns:
            List of possible argument completions.
        """
        parts = partial.split()
        if not parts:
            return []

        command_name = parts[0]
        command = self.registry.get(command_name)
        if not command:
            return []

        # Determine which argument position we're completing
        arg_index = len(parts) - 1  # Current arg being typed
        if partial.endswith(" "):
            arg_index = len(parts)  # Starting a new arg
            current_partial = ""
        else:
            current_partial = parts[-1] if len(parts) > 1 else ""

        # Get completions based on command and argument position
        return self._get_command_arg_completions(
            command, parts[1:], arg_index - 1, current_partial
        )

    async def _get_argument_completions_async(self, partial: str) -> list[str]:
        """Get argument completions for a partial command (async).

        Args:
            partial: Partial input text with command.

        Returns:
            List of possible argument completions.
        """
        parts = partial.split()
        if not parts:
            return []

        command_name = parts[0]
        command = self.registry.get(command_name)
        if not command:
            return []

        # Determine which argument position we're completing
        arg_index = len(parts) - 1  # Current arg being typed
        if partial.endswith(" "):
            arg_index = len(parts)  # Starting a new arg
            current_partial = ""
        else:
            current_partial = parts[-1] if len(parts) > 1 else ""

        # Get completions based on command and argument position
        return await self._get_command_arg_completions_async(
            command, parts[1:], arg_index - 1, current_partial
        )

    def _get_command_arg_completions(
        self, command: Command, typed_args: list[str], arg_pos: int, partial: str
    ) -> list[str]:
        """Get completions for a specific command argument.

        Args:
            command: The command being completed.
            typed_args: Arguments already typed.
            arg_pos: Position of argument being completed (0-indexed).
            partial: Partial text of current argument.

        Returns:
            List of possible completions.
        """
        completions = []

        # Define argument completions for each command
        completion_defs = self._get_completion_definitions()

        cmd_name = command.name
        if cmd_name in completion_defs:
            arg_completions = completion_defs[cmd_name]
            if arg_pos >= 0 and arg_pos < len(arg_completions):
                candidates = arg_completions[arg_pos]

                # Handle special completion types (string tokens)
                if isinstance(candidates, str):
                    if candidates == "@users":
                        candidates = self._get_online_usernames()
                    elif candidates == "@buckets":
                        candidates = self._get_kv_buckets()
                    elif candidates == "@keys":
                        # Need bucket name from previous arg (for kv get <bucket> <key>)
                        # typed_args[0] is action (get/keys), typed_args[1] is bucket
                        if len(typed_args) >= 2:
                            candidates = self._get_kv_keys(typed_args[1])
                        elif len(typed_args) >= 1 and arg_pos == 2:
                            # kv keys <bucket> case - bucket is typed_args[0] after "keys"
                            candidates = self._get_kv_keys(typed_args[0])
                        else:
                            candidates = []
                    elif candidates == "@channels":
                        candidates = self._get_discovered_channels()
                    else:
                        candidates = []

                # Filter by partial
                if isinstance(candidates, list):
                    for c in candidates:
                        if c.lower().startswith(partial.lower()):
                            completions.append(c)

        return completions

    async def _get_command_arg_completions_async(
        self, command: Command, typed_args: list[str], arg_pos: int, partial: str
    ) -> list[str]:
        """Get completions for a specific command argument (async with fetching).

        Args:
            command: The command being completed.
            typed_args: Arguments already typed.
            arg_pos: Position of argument being completed (0-indexed).
            partial: Partial text of current argument.

        Returns:
            List of possible completions.
        """
        completions = []

        # Define argument completions for each command
        completion_defs = self._get_completion_definitions()

        cmd_name = command.name
        if cmd_name in completion_defs:
            arg_completions = completion_defs[cmd_name]
            if arg_pos >= 0 and arg_pos < len(arg_completions):
                candidates = arg_completions[arg_pos]

                # Handle special completion types (string tokens)
                if isinstance(candidates, str):
                    if candidates == "@users":
                        candidates = await self._get_online_usernames_async()
                    elif candidates == "@buckets":
                        candidates = await self._get_kv_buckets_async()
                    elif candidates == "@keys":
                        # Need bucket name from previous arg (for kv get <bucket> <key>)
                        # typed_args[0] is action (get/keys), typed_args[1] is bucket
                        if len(typed_args) >= 2:
                            candidates = await self._get_kv_keys_async(typed_args[1])
                        elif len(typed_args) >= 1 and arg_pos == 2:
                            # kv keys <bucket> case - bucket is typed_args[0] after "keys"
                            candidates = await self._get_kv_keys_async(typed_args[0])
                        else:
                            candidates = []
                    elif candidates == "@channels":
                        candidates = await self._get_discovered_channels_async()
                    else:
                        candidates = []

                # Filter by partial
                if isinstance(candidates, list):
                    for c in candidates:
                        if c.lower().startswith(partial.lower()):
                            completions.append(c)

        return completions

    def _get_completion_definitions(self) -> dict[str, list]:
        """Define argument completion options for commands.

        Returns:
            Dictionary mapping command names to lists of completions per argument.
            Each entry is a list where each element represents an argument position.
            Elements can be:
            - A list of static strings: ["show", "add", "skip"]
            - A special token: "@users", "@buckets", "@keys", "@channels"
        """
        return {
            # Connection
            "channel": ["@channels"],
            "ch": ["@channels"],
            "join": ["@channels"],

            # Chat - username completion
            "pm": ["@users"],  # First arg is username
            "stats": ["@users"],
            "modcheck": ["@users"],

            # Moderation - username completion
            "kick": ["@users"],
            "ban": ["@users"],
            "unban": ["@users"],
            "smute": ["@users"],
            "unsmute": ["@users"],
            "mute": ["@users"],
            "unmute": ["@users"],

            # KV - action and bucket/key completion
            "kv": [
                ["buckets", "get", "keys", "list"],  # Action
                "@buckets",  # Bucket name
                "@keys",  # Key name (needs bucket from arg 1)
            ],

            # Playlist
            "playlist": [["show", "all", "top", "add", "skip"]],
            "pl": [["show", "all", "top", "add", "skip"]],
            "list": [["show", "all", "top", "add", "skip"]],

            # Users
            "users": [
                ["list", "stats", "leaderboard", "refresh"],
                "@users",  # Username for stats
            ],

            # Userstats commands - username completion
            "stats": ["@users"],
            "activity": ["@users"],
            "kudos": ["@users"],
            "messages": ["@users"],

            # Show - what to show
            "show": [
                ["users", "playlist", "buckets", "status", "np", "bans", "patterns", 
                 "leaderboard", "stats", "services", "history", "population"],
                "@users",  # For "show stats <username>"
            ],

            # Patterns
            "patterns": [
                ["list", "add", "remove"],
            ],

            # Modlist
            "modlist": [["ban", "smute", "mute"]],
            "banlist": [["ban", "smute", "mute"]],
            "bans": [["ban", "smute", "mute"]],

            # Help
            "help": [self._get_all_command_names()],
            "?": [self._get_all_command_names()],
        }

    def _get_all_command_names(self) -> list[str]:
        """Get all registered command names.

        Returns:
            List of command names.
        """
        names = []
        for cmd in self.registry.list_commands():
            names.append(cmd.name)
        return names

    def _get_online_usernames(self) -> list[str]:
        """Get list of online usernames.

        Returns:
            List of usernames currently online.
        """
        if not self.client:
            return []

        # Try to get cached userlist (avoid blocking)
        try:
            users = self.client._cached_userlist or []
            return [u.get("name", "") for u in users if u.get("name")]
        except Exception:
            return []

    def _get_kv_buckets(self) -> list[str]:
        """Get list of KV bucket names.

        Returns:
            List of bucket names.
        """
        if not self.client:
            return []

        try:
            buckets = self.client._cached_buckets or []
            return list(buckets)
        except Exception:
            return []

    def _get_kv_keys(self, bucket: str) -> list[str]:
        """Get list of keys in a KV bucket.

        Args:
            bucket: Bucket name.

        Returns:
            List of key names.
        """
        if not self.client:
            return []

        try:
            keys = self.client._cached_keys.get(bucket, [])
            return list(keys)
        except Exception:
            return []

    def _get_discovered_channels(self) -> list[str]:
        """Get list of discovered channel names.

        Returns:
            List of channel names.
        """
        if not self.client:
            return []

        try:
            channels = self.client._cached_channels or []
            return [f"{c.get('domain', 'cytu.be')}/{c.get('channel', '')}" for c in channels]
        except Exception:
            return []

    # ========================================================================
    # Async fetch methods for tab completion with read-ahead
    # ========================================================================

    async def _get_online_usernames_async(self) -> list[str]:
        """Get list of online usernames (async with fetch).

        Returns:
            List of usernames currently online.
        """
        if not self.client:
            return []

        try:
            # Try cached first
            users = self.client._cached_userlist
            if not users:
                # Fetch if not cached
                users = await self.client.get_userlist()
            return [u.get("name", "") for u in users if u.get("name")]
        except Exception:
            return []

    async def _get_kv_buckets_async(self) -> list[str]:
        """Get list of KV bucket names (async with fetch).

        Returns:
            List of bucket names.
        """
        if not self.client:
            return []

        try:
            # Try cached first
            buckets = self.client._cached_buckets
            if not buckets:
                # Fetch if not cached
                buckets = await self.client.list_kv_buckets()
            return list(buckets) if buckets else []
        except Exception:
            return []

    async def _get_kv_keys_async(self, bucket: str) -> list[str]:
        """Get list of keys in a KV bucket (async with fetch).

        Args:
            bucket: Bucket name.

        Returns:
            List of key names.
        """
        if not self.client:
            return []

        try:
            # Try cached first
            keys = self.client._cached_keys.get(bucket)
            if not keys:
                # Fetch if not cached
                keys = await self.client.list_kv_keys(bucket)
            return list(keys) if keys else []
        except Exception:
            return []

    async def _get_discovered_channels_async(self) -> list[str]:
        """Get list of discovered channel names (async with fetch).

        Returns:
            List of channel names.
        """
        if not self.client:
            return []

        try:
            # Try cached first
            channels = self.client._cached_channels
            if not channels:
                # Fetch if not cached
                channels = await self.client.discover_channels()
            return [f"{c.get('domain', 'cytu.be')}/{c.get('channel', '')}" for c in channels]
        except Exception:
            return []
