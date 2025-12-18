from typing import Any

from riven_cli.http_client import BaseClient

TMDB_READ_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlNTkxMmVmOWFhM2IxNzg2Zjk3ZTE1NWY1YmQ3ZjY1MSIsInN1YiI6IjY1M2NjNWUyZTg5NGE2MDBmZjE2N2FmYyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.xrIXsMFJpI1o1j5g2QpQcFP1X3AfRjFA5FlBFO5Naw8"


class TMDBClient(BaseClient):
    def __init__(self):
        super().__init__(
            base_url="https://api.themoviedb.org/3",
            headers={
                "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
        )

    async def search(self, query: str, page: int = 1) -> dict[str, Any]:
        return await self.get(
            "search/multi",
            params={"query": query, "page": str(page), "include_adult": "false"},
        )

    async def get_external_ids(self, media_type: str, tmdb_id: int) -> dict[str, Any]:
        return await self.get(f"{media_type}/{tmdb_id}/external_ids")


tmdb_client = TMDBClient()
