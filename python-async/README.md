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
    risk = await client.negative_risk("DE-LU", days=2)
    action = await client.cheapest_window(
        "DE-LU",
        duration_minutes=120,
        objective="balanced",
        tariff={
            "grid_fee_eur_kwh": 0.10,
            "supplier_markup_eur_kwh": 0.02,
            "vat_percent": 25,
        },
    )
```

New keyed access starts with Home at €9/month after a 7-day card-required
trial: https://voltcast.com/register?plan=home. Existing Free keys retain their
original grandfathered limits.

## Errors

- `VoltcastAuthError` — bad key or plan restriction (401/403)
- `VoltcastError` — any other API error, with `.status` and `.code`
- `VoltcastConnectionError` — network-level failure

## Publishing (maintainers)

```bash
cd python-async && python -m build && twine upload dist/*
```
