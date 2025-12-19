"""Kryten Shell - Interactive TUI for the Kryten ecosystem.

A modern terminal user interface for monitoring, inspecting, and controlling
Kryten ecosystem components via kryten-py.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("kryten-shell")
except PackageNotFoundError:
    __version__ = "0.0.0"

__author__ = "grobertson"

from kryten_shell.app import KrytenShellApp

__all__ = ["KrytenShellApp", "__version__"]
