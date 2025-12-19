"""KV Store inspector view."""

import json

from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Tree

from kryten_shell.client import KrytenClientWrapper


class KVInspectorView(Vertical):
    """View for inspecting NATS KV store contents.

    Shows:
    - Available KV buckets
    - Keys within each bucket
    - Values (with JSON formatting)
    """

    DEFAULT_CSS = """
    KVInspectorView {
        height: 100%;
    }

    #kv-header {
        height: 3;
        background: #073642;
        padding: 0 1;
        border-bottom: solid #586e75;
    }

    #kv-content {
        height: 1fr;
    }

    #kv-tree {
        width: 40;
        height: 100%;
        border-right: solid #586e75;
    }

    #kv-value {
        width: 1fr;
        height: 100%;
        padding: 1;
        overflow-y: auto;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the KV inspector view."""
        super().__init__(*args, **kwargs)
        self._client: KrytenClientWrapper | None = None
        self._selected_bucket: str | None = None
        self._selected_key: str | None = None

    def compose(self):
        """Compose the KV inspector view widgets."""
        yield Static(
            "[bold]KV Store Inspector[/] | Select a bucket to explore",
            id="kv-header",
        )
        with Horizontal(id="kv-content"):
            yield Tree("KV Buckets", id="kv-tree")
            yield Static(
                "[dim]Select a key to view its value[/]",
                id="kv-value",
            )

    def on_mount(self) -> None:
        """Initialize the tree on mount."""
        tree = self.query_one("#kv-tree", Tree)
        tree.root.expand()

    def set_client(self, client: KrytenClientWrapper) -> None:
        """Set the Kryten client reference.

        Args:
            client: The Kryten client wrapper.
        """
        self._client = client

    async def reload_data(self) -> None:
        """Reload the KV store tree data."""
        if not self._client:
            return

        tree = self.query_one("#kv-tree", Tree)
        tree.clear()

        # Get available buckets
        buckets = await self._client.list_kv_buckets()

        for bucket_name in buckets:
            bucket_node = tree.root.add(
                f"[bold cyan]📦 {bucket_name}[/]",
                data={"type": "bucket", "name": bucket_name},
            )

            # Get keys in bucket
            keys = await self._client.list_kv_keys(bucket_name)
            for key in keys:
                bucket_node.add_leaf(
                    f"[blue]🔑 {key}[/]",
                    data={"type": "key", "bucket": bucket_name, "key": key},
                )

        tree.root.expand()
        self._update_header(len(buckets))

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection.

        Args:
            event: The node selected event.
        """
        node_data = event.node.data
        if not node_data:
            return

        if node_data.get("type") == "key":
            # Fetch and display the value
            bucket = node_data["bucket"]
            key = node_data["key"]
            self._selected_bucket = bucket
            self._selected_key = key
            self.app.call_later(self._load_value, bucket, key)

    async def _load_value(self, bucket: str, key: str) -> None:
        """Load and display a KV value.

        Args:
            bucket: The bucket name.
            key: The key name.
        """
        if not self._client:
            return

        value_display = self.query_one("#kv-value", Static)

        try:
            value = await self._client.kv_get(bucket, key)

            if value is None:
                value_display.update("[yellow]Key not found or empty[/]")
                return

            # Try to format as JSON
            if isinstance(value, (dict, list)):
                formatted = json.dumps(value, indent=2)
            elif isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    formatted = json.dumps(parsed, indent=2)
                except json.JSONDecodeError:
                    formatted = value
            else:
                formatted = str(value)

            # Limit display size
            if len(formatted) > 10000:
                formatted = formatted[:10000] + "\n\n[dim]... truncated ...[/]"

            value_display.update(f"[bold cyan]{bucket}[/] / [blue]{key}[/]\n\n{formatted}")

        except Exception as e:
            value_display.update(f"[red]Error loading value: {e}[/]")

    def _update_header(self, bucket_count: int) -> None:
        """Update the header with bucket count.

        Args:
            bucket_count: Number of buckets.
        """
        header = self.query_one("#kv-header", Static)
        header.update(f"[bold]KV Store Inspector[/] | Buckets: {bucket_count}")

    def add_bucket(self, name: str, keys: list[str] | None = None) -> None:
        """Add a bucket to the tree.

        Args:
            name: Bucket name.
            keys: Optional list of keys in the bucket.
        """
        tree = self.query_one("#kv-tree", Tree)

        bucket_node = tree.root.add(
            f"[bold cyan]📦 {name}[/]",
            data={"type": "bucket", "name": name},
        )

        if keys:
            for key in keys:
                bucket_node.add_leaf(
                    f"[blue]🔑 {key}[/]",
                    data={"type": "key", "bucket": name, "key": key},
                )
