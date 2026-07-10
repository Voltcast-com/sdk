# voltcast — Python SDK

Official Python client for the [Voltcast API](https://voltcast.com/docs): 15-minute
European day-ahead power prices, P10/P50/P90 forecasts, optimization and bulk export.

```bash
pip install voltcast            # or: pip install voltcast[pandas]
```

```python
import voltcast

vc = voltcast.Client("YOUR_API_KEY")   # keys: https://voltcast.com/dashboard

prices = vc.prices("DE-LU")            # yesterday → tomorrow, 15-minute native
print(len(prices), prices[0])

df = vc.prices("DE-LU", start="2026-07-01", end="2026-07-10").to_pandas()

forecast = vc.forecast("DE-LU", horizon="48h")
print(forecast.meta["model_version"], forecast[0])

# Pro plans: optimization + bulk export
windows = vc.cheapest_window("DE-LU", duration_minutes=120)
plan = vc.schedule("DE-LU", energy_kwh=40, max_power_kw=11, deadline="2026-07-11T07:00:00Z")
files = vc.export_urls("DE-LU", "2018-01-01", "2026-12-31", format="parquet")
```

Errors raise `voltcast.VoltcastError` with `.status` and the API's machine-readable `.code`.
Attribution requirements for verbatim price data: https://voltcast.com/legal/data-licensing
