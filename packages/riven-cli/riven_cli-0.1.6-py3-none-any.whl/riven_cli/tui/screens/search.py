import readchar
from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from riven_cli.api import client
from riven_cli.providers.tmdb import tmdb_client
from riven_cli.tui.base import PaginatedListScreen


class SearchScreen(PaginatedListScreen):
    def __init__(self, app):
        super().__init__(app)
        self.query = ""
        # items replaced results
        self.items = []
        self.input_mode = True  # Start in input mode
        self.available_rows_offset = 15

    async def shutdown(self):
        await tmdb_client.close()

    def start_search(self):
        self.page = 1
        self.total_pages = 1
        self.scroll_offset = 0
        self.selected_index = 0
        self.items = []

    async def fetch_items(self, preserve_selection=False):
        self.loading = True
        self.error = None
        self.message = None

        try:
            data = await tmdb_client.search(self.query, page=self.page)
            self.total_pages = data.get("total_pages", 1)

            # Filter for only movie/tv
            self.items = [
                x
                for x in data.get("results", [])
                if x.get("media_type") in ["movie", "tv"]
            ]

            # Scroll offset logic is handled by base class or render, but fetch_wrapper usually resets selection if not preserved
            if not preserve_selection:
                self.selected_index = 0
                self.scroll_offset = 0

        except Exception as e:
            self.error = str(e)
            self.items = []
        finally:
            self.loading = False

    def render(self) -> Layout:
        # Header
        title = "Search & Add New Content"
        if not self.input_mode and self.items:
            title += f" (Page {self.page}/{self.total_pages})"

        header = Panel(
            Align.center(Text(title, style="bold magenta")),
            style="blue",
        )

        # Body
        content = []

        # Search Bar
        search_text = Text()
        search_text.append("Search Query: ", style="bold cyan")
        if self.input_mode:
            search_text.append(self.query + "█", style="white")
        else:
            search_text.append(self.query, style="white")

        content.append(Panel(search_text, title="Find Movies & Shows"))

        # Results
        if self.loading and not self.items:
            content.append(
                Align.center(Text("Searching TMDB...", style="yellow blink"))
            )
        elif self.error:
            content.append(Align.center(Text(f"Error: {self.error}", style="bold red")))
        elif self.items:
            table = Table(box=None, expand=True)
            table.add_column("Index", width=6)
            table.add_column("Type", width=8)
            table.add_column("Title", ratio=1)
            table.add_column("Year", width=6)

            visible_items = self.calculate_visible_items()

            for i, item in enumerate(visible_items):
                actual_index = self.scroll_offset + i
                style = (
                    "reverse"
                    if (not self.input_mode and actual_index == self.selected_index)
                    else ""
                )

                title = item.get("title") or item.get("name") or "Unknown"
                media_type = item.get("media_type")
                date = item.get("release_date") or item.get("first_air_date") or ""
                year = date[:4] if date else ""

                table.add_row(
                    str(actual_index + 1), media_type, title, year, style=style
                )

            content.append(Panel(table, title=f"Results ({len(self.items)})"))
        elif self.query and not self.input_mode:
            content.append(Align.center(Text("No results found.", style="dim")))

        if self.message:
            content.append(Panel(Text(self.message, style="bold green"), style="green"))

        # Footer
        footer_text = Text()
        if self.input_mode:
            footer_text.append("[Enter] Search  ", style="bold green")
            footer_text.append("[CTRL+Q] Cancel", style="bold red")
        else:
            footer_text.append("[Enter] Add Item  ", style="bold green")
            footer_text.append("[Q] Back  ", style="bold red")
            footer_text.append("[S] Search Again  ", style="bold cyan")
            footer_text.append("[Left/Right] Page  ", style="bold yellow")

        footer = Panel(Align.center(footer_text), title="Actions")

        layout = Layout()
        layout.split(
            Layout(header, size=3), Layout(Group(*content)), Layout(footer, size=3)
        )
        return layout

    async def handle_input(self, key: str):
        if self.input_mode:
            if key == readchar.key.ENTER:
                if self.query.strip():
                    self.input_mode = False
                    self.start_search()
                    await self.fetch_items()
            elif key == readchar.key.CTRL_Q:
                self.app.switch_to("dashboard")
            elif key == readchar.key.BACKSPACE:
                self.query = self.query[:-1]
            elif len(key) == 1 and key.isprintable():
                self.query += key
        else:
            # Navigation Mode
            if key == "q":
                self.app.switch_to("dashboard")
            elif key == "s":
                self.input_mode = True
                self.query = ""
                self.items = []
                self.message = None
                self.error = None
            elif key == readchar.key.ENTER:
                if self.items:
                    await self.add_item(self.items[self.selected_index])
            else:
                await super().handle_navigation_input(key)

    async def add_item(self, item):
        self.message = f"Adding {item.get('title') or item.get('name')}..."
        self.loading = True
        try:
            media_type = item["media_type"]
            payload = {"media_type": media_type}

            if media_type == "tv":
                # Fetch TVDB ID because backend requires it for TV shows
                external_ids = await tmdb_client.get_external_ids("tv", item["id"])
                tvdb_id = external_ids.get("tvdb_id")
                if not tvdb_id:
                    raise Exception(
                        "No TVDB ID found for this show (backend requirement)"
                    )
                payload["tvdb_ids"] = [str(tvdb_id)]
            else:
                payload["tmdb_ids"] = [str(item["id"])]

            async with client as c:
                response = await c.post("/items/add", json=payload)
                self.message = response.get("message", "Successfully added item")

        except Exception as e:
            self.error = f"Failed to add: {str(e)}"
            self.message = None
        finally:
            self.loading = False
