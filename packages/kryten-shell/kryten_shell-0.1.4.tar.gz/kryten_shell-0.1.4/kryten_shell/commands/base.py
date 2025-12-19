"""Command base classes and registry."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Coroutine

if TYPE_CHECKING:
    from kryten_shell.app import KrytenShellApp
    from kryten_shell.client import KrytenClientWrapper


@dataclass
class CommandResult:
    """Result of a command execution."""

    success: bool
    message: str | None = None
    data: Any = None


@dataclass
class CommandArg:
    """Definition of a command argument."""

    name: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class Command:
    """Definition of a shell command."""

    name: str
    description: str
    handler: Callable[..., Coroutine[Any, Any, CommandResult]]
    args: list[CommandArg] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    category: str = "general"

    @property
    def usage(self) -> str:
        """Generate usage string for the command."""
        parts = [self.name]
        for arg in self.args:
            if arg.required:
                parts.append(f"<{arg.name}>")
            else:
                parts.append(f"[{arg.name}]")
        return " ".join(parts)

    @property
    def help_text(self) -> str:
        """Generate help text for the command."""
        lines = [
            f"[bold cyan]{self.name}[/] - {self.description}",
            f"  Usage: {self.usage}",
        ]
        if self.aliases:
            lines.append(f"  Aliases: {', '.join(self.aliases)}")
        if self.args:
            lines.append("  Arguments:")
            for arg in self.args:
                req = "(required)" if arg.required else f"(optional, default: {arg.default})"
                lines.append(f"    {arg.name}: {arg.description} {req}")
        return "\n".join(lines)


class CommandRegistry:
    """Registry of available commands."""

    def __init__(self) -> None:
        """Initialize the command registry."""
        self._commands: dict[str, Command] = {}
        self._aliases: dict[str, str] = {}

    def register(self, command: Command) -> None:
        """Register a command.

        Args:
            command: The command to register.
        """
        self._commands[command.name] = command
        for alias in command.aliases:
            self._aliases[alias] = command.name

    def get(self, name: str) -> Command | None:
        """Get a command by name or alias.

        Args:
            name: Command name or alias.

        Returns:
            The command or None if not found.
        """
        # Check direct name
        if name in self._commands:
            return self._commands[name]

        # Check aliases
        if name in self._aliases:
            return self._commands[self._aliases[name]]

        return None

    def list_commands(self) -> list[Command]:
        """Get all registered commands.

        Returns:
            List of all commands.
        """
        return list(self._commands.values())

    def list_by_category(self) -> dict[str, list[Command]]:
        """Get commands grouped by category.

        Returns:
            Dictionary mapping category to commands.
        """
        by_category: dict[str, list[Command]] = {}
        for command in self._commands.values():
            if command.category not in by_category:
                by_category[command.category] = []
            by_category[command.category].append(command)
        return by_category


class CommandHandler(ABC):
    """Base class for command handlers."""

    def __init__(
        self,
        app: "KrytenShellApp",
        client: "KrytenClientWrapper",
    ) -> None:
        """Initialize the command handler.

        Args:
            app: The main application.
            client: The Kryten client wrapper.
        """
        self.app = app
        self.client = client

    @abstractmethod
    def register_commands(self, registry: CommandRegistry) -> None:
        """Register commands with the registry.

        Args:
            registry: The command registry.
        """
        pass
