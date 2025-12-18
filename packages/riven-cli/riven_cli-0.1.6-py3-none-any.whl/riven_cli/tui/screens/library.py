import readchar
from rich import box
from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from riven_cli.api import client
from riven_cli.tui.base import (ACTION_DEFINITIONS, ItemActionsMixin,
                                PaginatedListScreen)


class LibraryScreen(PaginatedListScreen, ItemActionsMixin):
    def __init__(self, app):
        super().__init__(app)
        self.selection_stack = []
        self.current_parent = None

    async def on_mount(self):
        if not self.items:
            await self.fetch_items()

    def reset_state(self):
        self.current_parent = None
        self.selection_stack = []
        self.page = 1
        self.items = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = None
        self.error = None

    async def fetch_items(self, preserve_selection=False):
        self.loading = True
        self.message = None
        current_index = self.selected_index
        current_scroll = self.scroll_offset

        try:
            async with client as c:
                # Default to Show and Movie for root view, sorted by title
                params = {
                    "page": self.page,
                    "limit": 20,
                    "type": ["show", "movie"],
                    "sort": ["title_asc"],
                }
                data = await c.get("/items", params=params)
                data = data.get("data", {}) if "data" in data else data
                self.items = data.get("items", [])
                self.total_pages = data.get("total_pages", 1)

                if preserve_selection:
                    self.selected_index = min(
                        current_index, max(0, len(self.items) - 1)
                    )
                    self.scroll_offset = current_scroll
                else:
                    self.selected_index = 0
                    self.scroll_offset = 0
            self.error = None
        except Exception as e:
            self.error = str(e)
            self.loading = False
            self.items = []
        finally:
            self.loading = False

    async def fetch_folder_contents(self, item):
        async with client as c:
            details = await c.get(
                f"/items/{item['id']}",
                params={"extended": "true", "media_type": "item"},
            )

        data = details.get("data", {}) if "data" in details else details
        new_items = []
        if item["type"] == "show":
            new_items = data.get("seasons", [])
            new_items.sort(key=lambda x: x.get("season_number", 0))
        elif item["type"] == "season":
            new_items = data.get("episodes", [])
            new_items.sort(key=lambda x: x.get("episode_number", 0))
        return new_items

    async def refresh_view(self, preserve_selection=True):
        if self.loading:
            return

        current_index = self.selected_index
        current_scroll = self.scroll_offset

        if self.current_parent:
            try:
                self.loading = True
                self.items = await self.fetch_folder_contents(self.current_parent)

                if preserve_selection:
                    self.selected_index = min(
                        current_index, max(0, len(self.items) - 1)
                    )
                    self.scroll_offset = current_scroll
                else:
                    self.selected_index = 0
                    self.scroll_offset = 0
                self.loading = False
            except Exception as e:
                self.error = str(e)
                self.loading = False
        else:
            await self.fetch_items(preserve_selection=preserve_selection)

    def render(self) -> Layout:
        # Header
        header = Panel(
            Align.center(
                Text(
                    f"Riven Library (Page {self.page}/{self.total_pages})",
                    style="bold cyan",
                )
            ),
            style="blue",
        )

        # Body
        if self.loading and not self.items:
            body_content = Align.center(
                Text("Loading library...", style="yellow blink")
            )
        elif self.error:
            body_content = Align.center(
                Text(f"Error fetching library:\n{self.error}", style="bold red")
            )
        else:
            table = Table(box=box.SIMPLE, expand=True)
            table.add_column("ID", width=6, justify="right")
            table.add_column("Title", ratio=1)
            table.add_column("Type", width=8)
            table.add_column("State", width=12)
            table.add_column("Year", width=6)

            visible_items = self.calculate_visible_items()

            for i, item in enumerate(visible_items):
                # Calculate actual index in full list
                actual_index = self.scroll_offset + i
                is_selected = actual_index == self.selected_index
                style = "reverse" if is_selected else ""

                title = item.get("title", "Unknown")
                original_type = item.get("type")

                # Display Type Logic
                display_type = original_type
                if item.get("is_anime"):
                    display_type = "anime"

                # Folder Indicators - Only for structured items
                if original_type in ["show", "season"]:
                    title = f"📁 {title}"
                    style = f"{style} bold" if is_selected else "bold"

                if original_type == "episode" and item.get("parent_title"):
                    # If inside season, just show Ep number - Title
                    if (
                        self.selection_stack
                    ):  # Inside a stack mean we likely have context
                        title = f"E{item.get('episode_number')} - {item.get('title')}"
                    else:
                        title = f"{item.get('parent_title')} S{item.get('season_number')}E{item.get('episode_number')} - {title}"

                if is_selected:
                    title = f"> {title}"

                # Year logic
                year = str(item.get("year", ""))
                if not year and item.get("aired_at"):
                    year = item.get("aired_at")[:4]

                table.add_row(
                    str(item.get("id")),
                    Text(title, style=style, overflow="ellipsis", no_wrap=True),
                    display_type,
                    item.get("state", "Unknown"),
                    year,
                    style=style,
                )

            title_text = "Media Items"
            if self.current_parent:
                title_text = f"Wrapper: {self.current_parent.get('title')}"

            body_content = Panel(table, title=title_text)

        # Compose Layout with Status Message
        final_body = []
        if self.message:
            final_body.append(
                Panel(Text.from_markup(self.message), style="bold yellow")
            )
        final_body.append(body_content)

        body = Group(*final_body)

        # Footer
        footer_text = Text()
        footer_text.append("[Q] Back  ", style="bold red")
        footer_text.append("[Left/Right] Page ", style="bold yellow")
        footer_text.append("[R] Refresh ", style="bold cyan")

        # Dynamic Item Actions
        if self.items:
            selected_item = self.items[self.selected_index]
            valid_actions = self.get_valid_actions(selected_item)

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
            if self.selection_stack:
                # Pop state
                state = self.selection_stack.pop()
                self.items = state["items"]
                self.selected_index = state["selected_index"]
                self.scroll_offset = state["scroll_offset"]
                self.page = state["page"]
                self.total_pages = state["total_pages"]
                self.current_parent = state["current_parent"]
                self.message = None
            else:
                self.app.switch_to("dashboard")
            return

        elif key == readchar.key.ENTER:
            if self.items:
                selected_item = self.items[self.selected_index]
                item_type = selected_item.get("type")

                if item_type in ["show", "season"]:
                    # Enter Folder
                    await self.enter_folder(selected_item)
                else:
                    # Open Details
                    self.app.context["item_id"] = selected_item.get("id")
                    self.app.switch_to("details")
            return

        elif key.lower() == "r":
            await self.refresh_view(preserve_selection=True)
            return

        # Action Keys
        if selected_item := (self.items[self.selected_index] if self.items else None):
            key_lower = key.lower()
            valid_actions = self.get_valid_actions(selected_item)

            if key_lower in valid_actions:
                if key_lower == "d":
                    await self.delete_item(
                        selected_item["id"], selected_item.get("title", "")
                    )
                elif key_lower == "s":
                    await self.reset_item(
                        selected_item["id"], selected_item.get("title", "")
                    )
                elif key_lower == "t":
                    await self.retry_item(
                        selected_item["id"], selected_item.get("title", "")
                    )
                elif key_lower == "p":
                    await self.pause_item(
                        selected_item["id"], selected_item.get("title", "")
                    )
                elif key_lower == "w":
                    await self.play_item(
                        selected_item["id"],
                        selected_item.get("title", ""),
                        selected_item.get("type", "movie"),
                    )

        # Standard Navigation
        await super().handle_navigation_input(key)

    async def enter_folder(self, item):
        try:
            # Save current state
            self.selection_stack.append(
                {
                    "items": self.items,
                    "selected_index": self.selected_index,
                    "scroll_offset": self.scroll_offset,
                    "page": self.page,
                    "total_pages": self.total_pages,
                    "current_parent": self.current_parent,
                }
            )

            # Fetch contents using helper
            new_items = await self.fetch_folder_contents(item)

            self.items = new_items
            self.selected_index = 0
            self.scroll_offset = 0
            self.page = 1
            self.total_pages = 1
            self.current_parent = item
            self.loading = False

        except Exception as e:
            self.error = str(e)
            self.loading = False
            # Revert stack if failed?
            if self.selection_stack:
                self.selection_stack.pop()
