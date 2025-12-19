"""Kryten Shell entry point.

Provides CLI interface for launching the TUI application.
"""

import logging
import sys

import click

from kryten_shell import __version__
from kryten_shell.app import KrytenShellApp
from kryten_shell.config import ShellConfig


def setup_logging(level: str) -> None:
    """Configure logging for the application.

    Args:
        level: Log level name (DEBUG, INFO, WARNING, ERROR).
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@click.command()
@click.option(
    "--host",
    "-h",
    default=None,
    help="NATS server host (default: localhost)",
)
@click.option(
    "--port",
    "-p",
    type=int,
    default=None,
    help="NATS server port (default: 4222)",
)
@click.option(
    "--channel",
    "-c",
    default=None,
    help="Channel to join on startup",
)
@click.option(
    "--config",
    "-f",
    "config_file",
    type=click.Path(exists=True),
    default=None,
    help="Path to config file",
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Log level",
)
@click.option(
    "--version",
    "-v",
    is_flag=True,
    help="Show version and exit",
)
def main(
    host: str | None,
    port: int | None,
    channel: str | None,
    config_file: str | None,
    log_level: str,
    version: bool,
) -> None:
    """Kryten Shell - Interactive TUI for the Kryten ecosystem.

    A modern terminal user interface for monitoring, inspecting, and
    controlling Kryten ecosystem components.

    \b
    Examples:
        kryten-shell                          # Start with defaults
        kryten-shell -c cyberia               # Join channel on startup
        kryten-shell -h 192.168.1.10 -p 4222  # Connect to remote NATS
        ksh                                   # Short alias
    """
    if version:
        click.echo(f"kryten-shell v{__version__}")
        sys.exit(0)

    setup_logging(log_level)

    # Load config
    config = ShellConfig.load(config_file) if config_file else ShellConfig.load()
    config.log_level = log_level

    # Create and run the app
    app = KrytenShellApp(
        config=config,
        nats_host=host,
        nats_port=port,
        channel=channel,
    )

    app.run()


if __name__ == "__main__":
    main()
