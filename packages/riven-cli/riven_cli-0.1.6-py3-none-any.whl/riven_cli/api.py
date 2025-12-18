from typing import Any

import aiohttp

from riven_cli.config import settings
from riven_cli.http_client import BaseClient


class RivenClient(BaseClient):
    def __init__(self):
        super().__init__(base_url=settings.api_url)

    def refresh_settings(self):
        self.base_url = settings.api_url.rstrip("/")
        self.headers = {
            "x-api-key": settings.api_key or "",
            "Content-Type": "application/json",
        }

    async def get_session(self) -> aiohttp.ClientSession:
        self.refresh_settings()
        if self.session and not self.session.closed:
            self.session._default_headers.update(self.headers)

        return await super().get_session()

    async def __aenter__(self):
        await self.get_session()
        return self

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        if not endpoint.startswith("/api/v1"):
            endpoint = f"api/v1/{endpoint.lstrip('/')}"
        return await super()._request(method, endpoint, **kwargs)

    async def get_logs(self) -> dict[str, Any]:
        return await self.get("/logs")

    async def stream_logs(self):
        session = await self.get_session()
        url = f"{self.base_url}/api/v1/stream/logging"

        # Disable timeout for streaming
        timeout = aiohttp.ClientTimeout(
            total=None, connect=None, sock_read=None, sock_connect=None
        )
        async with session.get(
            url, headers={"Accept": "text/event-stream"}, timeout=timeout
        ) as resp:
            if not resp.ok:
                text = await resp.text()
                raise Exception(f"{resp.status} {resp.reason}: {text}")

            async for line in resp.content:
                yield line.decode("utf-8")

    async def upload_logs(self) -> dict[str, Any]:
        return await self.post("/upload_logs")

    async def check_health(self) -> bool:
        try:
            await self.get("/health")
            return True
        except Exception:
            return False

    async def get_all_settings(self) -> dict[str, Any]:
        return await self.get("/settings/get/all")

    async def set_all_settings(self, settings: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/settings/set/all", json=settings)


client = RivenClient()
