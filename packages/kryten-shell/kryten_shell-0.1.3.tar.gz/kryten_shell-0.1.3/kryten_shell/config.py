"""Configuration management for Kryten Shell.

Handles NATS connection settings and persisted user preferences.
Uses platformdirs for cross-platform config storage.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import platformdirs

logger = logging.getLogger(__name__)

APP_NAME = "kryten-shell"
APP_AUTHOR = "kryten"


@dataclass
class NATSConfig:
    """NATS connection configuration."""

    host: str = "localhost"
    port: int = 4222

    @property
    def url(self) -> str:
        """Get NATS connection URL."""
        return f"nats://{self.host}:{self.port}"


@dataclass
class ShellConfig:
    """Main shell configuration."""

    nats: NATSConfig = field(default_factory=NATSConfig)
    channel: str | None = None
    domain: str = "cytu.be"
    history_file: Path | None = None
    max_history: int = 1000
    log_level: str = "INFO"

    # UI preferences
    show_timestamps: bool = True
    max_chat_lines: int = 500
    max_event_lines: int = 1000

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get the platform-specific config directory."""
        return Path(platformdirs.user_config_dir(APP_NAME, APP_AUTHOR))

    @classmethod
    def get_data_dir(cls) -> Path:
        """Get the platform-specific data directory."""
        return Path(platformdirs.user_data_dir(APP_NAME, APP_AUTHOR))

    @classmethod
    def get_history_path(cls) -> Path:
        """Get the command history file path."""
        data_dir = cls.get_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / "history.json"

    @classmethod
    def load(cls, path: Path | None = None) -> "ShellConfig":
        """Load configuration from file.

        Args:
            path: Optional config file path. Uses default if not provided.

        Returns:
            Loaded configuration or defaults.
        """
        if path is None:
            config_dir = cls.get_config_dir()
            path = config_dir / "config.json"

        if not path.exists():
            logger.info(f"No config file at {path}, using defaults")
            config = cls()
            config.history_file = cls.get_history_path()
            return config

        try:
            with open(path) as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            config = cls()
            config.history_file = cls.get_history_path()
            return config

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ShellConfig":
        """Create config from dictionary."""
        nats_data = data.get("nats", {})
        nats = NATSConfig(
            host=nats_data.get("host", "localhost"),
            port=nats_data.get("port", 4222),
        )

        history_file = data.get("history_file")
        if history_file:
            history_file = Path(history_file)
        else:
            history_file = cls.get_history_path()

        return cls(
            nats=nats,
            channel=data.get("channel"),
            domain=data.get("domain", "cytu.be"),
            history_file=history_file,
            max_history=data.get("max_history", 1000),
            log_level=data.get("log_level", "INFO"),
            show_timestamps=data.get("show_timestamps", True),
            max_chat_lines=data.get("max_chat_lines", 500),
            max_event_lines=data.get("max_event_lines", 1000),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "nats": {
                "host": self.nats.host,
                "port": self.nats.port,
            },
            "channel": self.channel,
            "domain": self.domain,
            "history_file": str(self.history_file) if self.history_file else None,
            "max_history": self.max_history,
            "log_level": self.log_level,
            "show_timestamps": self.show_timestamps,
            "max_chat_lines": self.max_chat_lines,
            "max_event_lines": self.max_event_lines,
        }

    def save(self, path: Path | None = None) -> None:
        """Save configuration to file.

        Args:
            path: Optional config file path. Uses default if not provided.
        """
        if path is None:
            config_dir = self.get_config_dir()
            config_dir.mkdir(parents=True, exist_ok=True)
            path = config_dir / "config.json"

        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        logger.info(f"Saved config to {path}")
