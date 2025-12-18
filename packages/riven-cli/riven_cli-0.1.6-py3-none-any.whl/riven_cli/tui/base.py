from typing import Any, Optional

import readchar
from rich.layout import Layout

from riven_cli.api import client
from riven_cli.utils import play_video

ACTION_DEFINITIONS = {
    "d": {"label": "[D] Delete ", "style": "bold bg red"},
    "s": {"label": "[S] Reset ", "style": "bold blue"},
    "t": {"label": "[T] Retry ", "style": "bold green"},
    "p": {"label": "[P] Pause ", "style": "bold magenta"},
    "w": {"label": "[W] Watch ", "style": "bold red"},
}


class Screen:
    def __init__(self, app):
        self.app = app
        self.loading = False
        self.error: Optional[str] = None

    async def on_mount(self):
        pass

    async def shutdown(self):
        pass

    def render(self) -> Layout:
        raise NotImplementedError

    async def handle_input(self, key: str):
        pass


class ItemActionsMixin:
    # These should be set by the using class if they want to display status messages
    message: Optional[str] = None

    async def refresh_view(self, preserve_selection=True):
        pass

    def get_valid_actions(self, item) -> list[str]:
        if not item:
            return []

        actions = ["s", "t", "p"]  # Default actions always available for items
        item_type = item.get("type")
        state = item.get("state", "").lower()

        # Watch: Only for playable items (Movie, Episode) AND state is completed
        if item_type in ["movie", "episode"] and state == "completed":
            actions.append("w")

        # Delete: Only for root types (Movie, Show)
        if item_type in ["movie", "show"]:
            actions.insert(0, "d")

        return actions

    async def delete_item(self, item_id: int, title: str = "item"):
        self.message = f"[yellow]Deleting {title}...[/yellow]"
        try:
            async with client as c:
                await c.delete("/items/remove", json={"ids": [str(item_id)]})
            self.message = f"[green]Deleted {title}[/green]"
            await self.refresh_view(preserve_selection=True)
        except Exception as e:
            self.message = f"[red]Delete Failed: {str(e)}[/red]"

    async def reset_item(self, item_id: int, title: str = "item"):
        self.message = f"[yellow]Resetting {title}...[/yellow]"
        try:
            async with client as c:
                await c.post("/items/reset", json={"ids": [str(item_id)]})
            self.message = f"[green]Reset {title}[/green]"
            await self.refresh_view(preserve_selection=True)
        except Exception as e:
            self.message = f"[red]Reset Failed: {str(e)}[/red]"

    async def retry_item(self, item_id: int, title: str = "item"):
        self.message = f"[yellow]Retrying {title}...[/yellow]"
        try:
            async with client as c:
                await c.post("/items/retry", json={"ids": [str(item_id)]})
            self.message = f"[green]Retrying {title}[/green]"
            await self.refresh_view(preserve_selection=True)
        except Exception as e:
            self.message = f"[red]Retry Failed: {str(e)}[/red]"

    async def pause_item(self, item_id: int, title: str = "item"):
        self.message = f"[yellow]Pausing {title}...[/yellow]"
        try:
            async with client as c:
                await c.post("/items/pause", json={"ids": [str(item_id)]})
            self.message = f"[green]Paused {title}[/green]"
            await self.refresh_view(preserve_selection=True)
        except Exception as e:
            self.message = f"[red]Pause Failed: {str(e)}[/red]"

    async def play_item(
        self, item_id: int, title: str = "item", item_type: str = "movie"
    ):
        self.message = f"[yellow]Launching player for {title}...[/yellow]"
        try:
            self.message = play_video(item_id)
        except Exception as e:
            self.message = f"[red]Play Failed: {str(e)}[/red]"


class PaginatedListScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.items: list[Any] = []
        self.page = 1
        self.total_pages = 1
        self.selected_index = 0
        self.scroll_offset = 0
        self.message: Optional[str] = None
        # Subclasses should set this
        self.available_rows_offset = 12  # Header + Footer + etc

    def calculate_visible_items(self) -> list[Any]:
        available_rows = max(
            5, self.app.console.size.height - self.available_rows_offset
        )

        # Adjust scroll_offset
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + available_rows:
            self.scroll_offset = self.selected_index - available_rows + 1

        # Ensure scroll_offset is valid
        self.scroll_offset = max(
            0, min(self.scroll_offset, len(self.items) - available_rows)
        )
        self.scroll_offset = max(0, self.scroll_offset)  # Double safe

        visible_items = self.items[
            self.scroll_offset : self.scroll_offset + available_rows
        ]
        return visible_items

    async def fetch_items(self, preserve_selection=False):
        raise NotImplementedError

    async def handle_navigation_input(self, key: str):
        if key == readchar.key.DOWN or key == "j":
            if self.selected_index < len(self.items) - 1:
                self.selected_index += 1
            elif self.page < self.total_pages:
                self.page += 1
                await self.fetch_items()
                self.selected_index = 0

        elif key == readchar.key.UP or key == "k":
            if self.selected_index > 0:
                self.selected_index -= 1
            elif self.page > 1:
                self.page -= 1
                await self.fetch_items()
                self.selected_index = (
                    len(self.items) - 1
                )  # This relies on fetch_items populating items immediately

        elif key == readchar.key.RIGHT or key == "n":  # Next Page
            if self.page < self.total_pages:
                self.page += 1
                await self.fetch_items()
                self.selected_index = 0

        elif key == readchar.key.LEFT or key == "p":  # Prev Page
            if self.page > 1:
                self.page -= 1
                await self.fetch_items()
                self.selected_index = 0
