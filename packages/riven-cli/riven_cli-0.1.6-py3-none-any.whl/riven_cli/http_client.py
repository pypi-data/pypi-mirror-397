from typing import Any, Optional

import aiohttp


class BaseClient:
    def __init__(self, base_url: str, headers: dict[str, str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def close(self):
        if self.session:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        session = await self.get_session()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        async with session.request(method, url, **kwargs) as resp:
            if not resp.ok:
                text = await resp.text()
                raise Exception(f"{resp.status} {resp.reason}: {text}")

            if resp.status == 204:
                return None

            return await resp.json()

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def post(
        self, endpoint: str, json: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        return await self._request("POST", endpoint, json=json, **kwargs)

    async def delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        return await self._request(
            "DELETE", endpoint, params=params, json=json, **kwargs
        )

    async def __aenter__(self):
        await self.get_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
