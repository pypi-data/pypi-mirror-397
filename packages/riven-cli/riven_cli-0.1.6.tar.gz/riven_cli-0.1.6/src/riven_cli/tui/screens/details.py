from typing import Any

from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from riven_cli.api import client
from riven_cli.tui.base import ACTION_DEFINITIONS, ItemActionsMixin, Screen


class ItemDetailsScreen(Screen, ItemActionsMixin):
    def __init__(self, app):
        super().__init__(app)
        self.item_id: int | None = None
        self.item: dict[str, Any] | None = None
        self.loading = True
        self.error: str | None = None
        self.message: str | None = None  # Unified with Mixin

    async def on_mount(self):
        if hasattr(self.app, "context") and "item_id" in self.app.context:
            self.item_id = self.app.context["item_id"]
            await self.fetch_details()
        else:
            self.error = "No Item ID selected"
            self.loading = False

    async def fetch_details(self):
        if not self.item_id:
            return
        try:
            self.loading = True
            self.message = None
            async with client:
                self.item = await client.get(
                    f"/items/{self.item_id}",
                    params={"extended": "true", "media_type": "item"},
                )
            self.error = None
        except Exception as e:
            self.error = str(e)
            self.item = None
        finally:
            self.loading = False

    async def refresh_view(self, preserve_selection=True):
        await self.fetch_details()

    def render(self):
        # Header
        title = "Item Details"
        if self.item:
            year = self.item.get("year")
            if not year and self.item.get("aired_at"):
                year = str(self.item.get("aired_at"))[:4]
            title = f"{self.item.get('title')} ({year or 'N/A'})"

        header = Panel(Align.center(Text(title, style="bold green")), style="blue")

        # Body
        if self.loading and not self.item:
            body = Align.center(Text("Loading details...", style="yellow blink"))
        elif self.error:
            body = Align.center(Text(f"Error:\n{self.error}", style="bold red"))
        elif self.item:
            # 1. General Info
            general_table = Table(show_header=False, box=None, padding=(0, 2))
            general_table.add_column("Key", style="cyan")
            general_table.add_column("Value", style="white")

            general_table.add_row("Type", self.item.get("type", "N/A").capitalize())
            general_table.add_row("State", self.item.get("state", "N/A"))

            # Format Date
            aired = self.item.get("aired_at")
            if aired:
                aired = str(aired).split(" ")[0]
            general_table.add_row("Aired", aired or "N/A")

            genres = self.item.get("genres", [])
            if genres:
                general_table.add_row("Genres", ", ".join(genres[:3]))

            general_table.add_row("Rating", self.item.get("content_rating", "N/A"))

            # 2. File Info
            fs_entry = self.item.get("filesystem_entry")
            file_table = Table(show_header=False, box=None, padding=(0, 2))
            file_table.add_column("Key", style="cyan")
            file_table.add_column("Value", style="white")

            if fs_entry:
                size_bytes = fs_entry.get("file_size", 0)
                size_gb = f"{size_bytes / (1024**3):.2f} GB" if size_bytes else "N/A"

                file_table.add_row(
                    "Filename",
                    Text(fs_entry.get("original_filename", "N/A"), overflow="ellipsis"),
                )
                file_table.add_row("Size", size_gb)
                file_table.add_row("Provider", fs_entry.get("provider", "N/A"))
                file_table.add_row(
                    "Updated", str(fs_entry.get("updated_at", "")).split("T")[0]
                )
            else:
                file_table.add_row("Status", "No file linked")

            # 3. Media Info
            media_meta = self.item.get("media_metadata", {})
            media_table = Table(show_header=False, box=None, padding=(0, 2))
            media_table.add_column("Key", style="cyan")
            media_table.add_column("Value", style="white")

            if media_meta:
                video = media_meta.get("video")
                if video:
                    res = f"{video.get('resolution_width', '?')}x{video.get('resolution_height', '?')}"
                    codec = video.get("codec", "N/A")
                else:
                    res = "N/A"
                    codec = "N/A"

                media_table.add_row("Resolution", res)
                media_table.add_row("Codec", codec)
                media_table.add_row(
                    "Source", media_meta.get("quality_source", "N/A") or "N/A"
                )
            else:
                media_table.add_row("Info", "No media metadata")

            # Layout grouping

            # Create panels
            p_general = Panel(general_table, title="General", border_style="blue")
            p_file = Panel(file_table, title="File", border_style="green")
            p_media = Panel(media_table, title="Media", border_style="magenta")

            # Stack them
            content = [p_general, p_file, p_media]

            if self.message:
                content.insert(
                    0, Panel(Text(self.message, style="bold yellow"), title="Status")
                )

            body = Group(*content)
        else:
            body = Align.center(Text("Item not found"))

        # Footer
        footer_text = Text()
        footer_text.append("[Q] Back  ", style="bold red")
        footer_text.append("[R] Refresh ", style="bold cyan")

        # Dynamic Item Actions
        if self.item:
            valid_actions = self.get_valid_actions(self.item)
            for action_key in valid_actions:
                action_def = ACTION_DEFINITIONS.get(action_key)
                if action_def:
                    footer_text.append(action_def["label"], style=action_def["style"])

        footer = Panel(Align.center(footer_text), title="Actions")

        layout = Layout()
        layout.split(Layout(header, size=3), Layout(body), Layout(footer, size=3))
        return layout

    async def handle_input(self, key: str):
        if key.lower() == "q":
            self.app.switch_to("library")
        elif key.lower() == "r":
            await self.fetch_details()

        elif self.item:
            key_lower = key.lower()
            valid_actions = self.get_valid_actions(self.item)

            if key_lower in valid_actions:
                if key_lower == "s":
                    if self.item_id:
                        await self.reset_item(self.item_id, title="item")
                elif key_lower == "d":
                    if self.item_id:
                        await self.delete_item(self.item_id, title="item")
                elif key_lower == "t":
                    if self.item_id:
                        await self.retry_item(self.item_id, title="item")
                elif key_lower == "p":
                    if self.item_id:
                        await self.pause_item(self.item_id, title="item")
                elif key_lower == "w":
                    if self.item_id:
                        await self.play_item(self.item_id, title="item")
