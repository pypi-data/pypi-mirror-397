# Kryten Shell

Interactive TUI shell for inspecting and controlling the Kryten ecosystem.

## Features

- **Live Monitoring**: Watch events, chat, and playlist changes in real-time
- **Interactive Commands**: Send messages, manage playlist, query state with natural syntax
- **KV Store Inspector**: Browse and inspect NATS KV store contents
- **Event Streaming**: View all Kryten ecosystem events with filtering
- **Solarized Dark Theme**: Easy on the eyes for extended sessions
- **Command History**: Persistent history across sessions with up/down navigation
- **Tab Completion**: Autocomplete commands as you type

## Installation

```bash
cd kryten-shell
poetry install
```

## Usage

```bash
# Start with defaults (localhost:4222)
poetry run kryten-shell

# Or use the short alias
poetry run ksh

# Connect to specific NATS server
poetry run kryten-shell --host 192.168.1.10 --port 4222

# Join a channel on startup
poetry run kryten-shell --channel cyberia
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `F1` | Show help |
| `F2` | Switch to Chat tab |
| `F3` | Switch to Playlist tab |
| `F4` | Switch to Events tab |
| `F5` | Switch to KV Store tab |
| `Ctrl+R` | Refresh current view |
| `Ctrl+L` | Clear current log |
| `Ctrl+Q` | Quit |
| `Escape` | Focus command input |
| `↑/↓` | Navigate command history |
| `Tab` | Autocomplete command |

## Commands

### Connection
- `connect` - Connect to NATS server
- `disconnect` - Disconnect from server
- `channel [name]` - Join channel or show current
- `discover` - Discover available channels

### Chat
- `msg <message>` - Send a chat message

### Playlist
- `playlist` - Show playlist
- `nowplaying` - Show current video
- `skip` - Skip current video

### KV Store
- `kv buckets` - List KV buckets
- `kv get <bucket> <key>` - Get a value
- `kv keys <bucket>` - List keys in bucket

### Utility
- `help [command]` - Show help
- `clear` - Clear current view
- `refresh` - Refresh current view
- `filter [pattern]` - Filter events by type
- `status` - Show connection status
- `quit` - Exit shell

## Configuration

Configuration is stored in the platform-specific config directory:
- Windows: `%APPDATA%\kryten\kryten-shell\config.json`
- Linux: `~/.config/kryten-shell/config.json`
- macOS: `~/Library/Application Support/kryten-shell/config.json`

Example config:
```json
{
  "nats": {
    "host": "localhost",
    "port": 4222
  },
  "channel": "cyberia",
  "show_timestamps": true,
  "max_chat_lines": 500,
  "max_event_lines": 1000
}
```

## Development

```bash
# Install with dev dependencies
poetry install --with dev

# Run with textual dev tools
poetry run textual run kryten_shell.app:KrytenShellApp

# Run tests
poetry run pytest

# Type checking
poetry run mypy kryten_shell

# Linting
poetry run ruff check kryten_shell
```

## License

MIT
