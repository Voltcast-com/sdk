"""Voltcast API client.

    import voltcast

    vc = voltcast.Client("YOUR_API_KEY")
    prices = vc.prices("DE-LU", start="2026-07-10", end="2026-07-12")
    df = prices.to_pandas()          # optional, needs voltcast[pandas]

    forecast = vc.forecast("DE-LU", horizon="48h")
    windows = vc.cheapest_window("DE-LU", duration_minutes=120)
"""

from __future__ import annotations

from typing import Any, Iterator, Optional

import httpx

DEFAULT_BASE_URL = "https://voltcast.com/api"


class VoltcastError(Exception):
    """API error with the server's machine-readable code where available."""

    def __init__(self, status: int, code: Optional[str], message: str):
        super().__init__(f"[{status}{f' {code}' if code else ''}] {message}")
        self.status = status
        self.code = code


class Series:
    """A list of row dicts with convenience accessors."""

    def __init__(self, rows: list[dict[str, Any]], meta: dict[str, Any]):
        self.rows = rows
        self.meta = meta

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def to_pandas(self):
        """Return the series as a pandas DataFrame (requires voltcast[pandas])."""
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover
            raise ImportError("install with: pip install voltcast[pandas]") from exc

        df = pd.DataFrame(self.rows)
        for column in ("delivery_start", "delivery_end", "target_start"):
            if column in df.columns:
                df[column] = pd.to_datetime(df[column])
        return df


class Client:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        self._http = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "User-Agent": "voltcast-python/0.1.0",
            },
        )

    # ------------------------------------------------------------- endpoints

    def zones(self) -> Series:
        """All bidding zones with EIC codes and resolution metadata."""
        body = self._request("GET", "/v1/zones")
        return Series(body["data"], body.get("meta", {}))

    def prices(
        self,
        zone: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        resolution: str = "native",
    ) -> Series:
        """Day-ahead prices for a zone (defaults: yesterday → tomorrow)."""
        params = {"resolution": resolution}
        if start:
            params["from"] = start
        if end:
            params["to"] = end
        body = self._request("GET", f"/v1/prices/{zone}", params=params)
        return Series(body["data"], body.get("meta", {}))

    def forecast(self, zone: str, horizon: str = "7d") -> Series:
        """Latest probabilistic forecast curve (horizon: '48h' or '7d')."""
        body = self._request("GET", f"/v1/forecasts/{zone}", params={"horizon": horizon})
        return Series(body["data"], body.get("meta", {}))

    def cheapest_window(
        self,
        zone: str,
        duration_minutes: int,
        start: Optional[str] = None,
        end: Optional[str] = None,
        count: int = 3,
    ) -> Series:
        """Cheapest contiguous windows over the forward curve (Pro+)."""
        payload: dict[str, Any] = {
            "zone": zone,
            "duration_minutes": duration_minutes,
            "count": count,
        }
        if start:
            payload["from"] = start
        if end:
            payload["to"] = end
        body = self._request("POST", "/v1/optimize/cheapest-window", json=payload)
        return Series(body["data"], body.get("meta", {}))

    def schedule(
        self,
        zone: str,
        energy_kwh: float,
        max_power_kw: float,
        deadline: str,
        start: Optional[str] = None,
    ) -> dict[str, Any]:
        """Cost-optimal charge/dispatch schedule before a deadline (Pro+)."""
        payload: dict[str, Any] = {
            "zone": zone,
            "energy_kwh": energy_kwh,
            "max_power_kw": max_power_kw,
            "deadline": deadline,
        }
        if start:
            payload["start"] = start
        body = self._request("POST", "/v1/optimize/schedule", json=payload)
        return body["data"] | {"meta": body.get("meta", {})}

    def export_urls(self, zone: str, start: str, end: str, format: str = "parquet") -> Series:
        """Signed bulk-export URLs for zone-year files (Pro+)."""
        body = self._request("GET", "/v1/history/export", params={
            "zone": zone, "from": start, "to": end, "format": format,
        })
        return Series(body["data"], body.get("meta", {}))

    def accuracy(self) -> dict[str, Any]:
        """The public forecast scorecard."""
        return self._request("GET", "/v1/accuracy")

    # -------------------------------------------------------------- plumbing

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        response = self._http.request(method, path, **kwargs)
        if response.status_code >= 400:
            code, message = None, response.text[:200]
            try:
                error = response.json().get("error", {})
                code, message = error.get("code"), error.get("message", message)
            except Exception:  # noqa: BLE001 — non-JSON error body
                pass
            raise VoltcastError(response.status_code, code, message)
        return response.json()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
