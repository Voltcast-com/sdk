# aiovoltcast

Async Python client for the [Voltcast API](https://voltcast.com/docs) — European
electricity prices, forecasts and carbon data. Built to Home Assistant core's
library requirements: aiohttp-based, session-injected, typed, no side effects.

```python
import aiohttp
from aiovoltcast import VoltcastClient

async with aiohttp.ClientSession() as session:
    client = VoltcastClient("YOUR_API_KEY", session=session)
    prices = await client.prices("DE-LU")
    forecast = await client.forecast("DE-LU", horizon="48h")
    carbon = await client.carbon("DE-LU")
```

Free API key (no card): https://voltcast.com/register

## Errors

- `VoltcastAuthError` — bad key or plan restriction (401/403)
- `VoltcastError` — any other API error, with `.status` and `.code`
- `VoltcastConnectionError` — network-level failure

## Publishing (maintainers)

```bash
cd python-async && python -m build && twine upload dist/*
```
