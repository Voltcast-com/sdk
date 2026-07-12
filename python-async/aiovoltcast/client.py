"""Async Voltcast API client (aiohttp), typed and dependency-light.

Home Assistant core requires integrations to talk to devices/services through
a published library — this is that library. It deliberately owns no event
loop or session: pass the shared session in (HA's pattern).
"""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

DEFAULT_BASE_URL = "https://voltcast.com/api"
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=30)


class VoltcastError(Exception):
    """Base error with the server's machine-readable code where available."""

    def __init__(self, status: int, code: str | None, message: str) -> None:
        super().__init__(f"[{status}{f' {code}' if code else ''}] {message}")
        self.status = status
        self.code = code


class VoltcastAuthError(VoltcastError):
    """401/403 — bad key or plan limits."""


class VoltcastConnectionError(Exception):
    """Network-level failure (DNS, timeout, refused)."""


class VoltcastClient:
    """Thin async wrapper over the REST API."""

    def __init__(
        self,
        api_key: str,
        session: aiohttp.ClientSession,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "aiovoltcast/0.1.0",
        }

    async def zones(self) -> list[dict[str, Any]]:
        """All bidding zones with metadata. Also the cheapest auth check."""
        body = await self._request("/v1/zones")
        return body["data"]

    async def prices(
        self,
        zone: str,
        *,
        start: str | None = None,
        end: str | None = None,
        resolution: str = "native",
    ) -> dict[str, Any]:
        """Day-ahead prices (defaults: yesterday -> tomorrow)."""
        params: dict[str, str] = {"resolution": resolution}
        if start:
            params["from"] = start
        if end:
            params["to"] = end
        return await self._request(f"/v1/prices/{zone}", params=params)

    async def forecast(self, zone: str, *, horizon: str = "48h") -> dict[str, Any]:
        """Latest probabilistic forecast curve ('48h' or '7d')."""
        return await self._request(f"/v1/forecasts/{zone}", params={"horizon": horizon})

    async def carbon(self, zone: str) -> dict[str, Any]:
        """Carbon intensity + green score from the live generation mix."""
        return await self._request(f"/v1/carbon/{zone}")

    async def validate_key(self, zone: str) -> None:
        """Raise VoltcastAuthError/VoltcastError if the key/zone don't work."""
        await self.prices(zone)

    async def _request(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        try:
            async with self._session.get(
                f"{self._base_url}{path}",
                params=params,
                headers=self._headers,
                timeout=DEFAULT_TIMEOUT,
            ) as response:
                if response.status >= 400:
                    code, message = None, await response.text()
                    try:
                        error = (await response.json()).get("error", {})
                        code = error.get("code")
                        message = error.get("message", message)
                    except Exception:  # noqa: BLE001 — non-JSON error body
                        pass
                    if response.status in (401, 403):
                        raise VoltcastAuthError(response.status, code, message[:200])
                    raise VoltcastError(response.status, code, message[:200])
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise VoltcastConnectionError(str(exc)) from exc
