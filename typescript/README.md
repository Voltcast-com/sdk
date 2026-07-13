# @voltcast/sdk

Official TypeScript/JavaScript SDK for the [Voltcast API](https://voltcast.com/docs) —
European electricity prices, probabilistic forecasts and station-exact weather data,
from the only vendor that [publishes its forecast accuracy every single day](https://voltcast.com/accuracy),
losses included.

```bash
npm install @voltcast/sdk
```

Works in Node 18+, Bun, Deno and the browser (ESM + CJS). Zero dependencies. Full TypeScript types.

## What you get

- **Day-ahead prices** — ~40 EU bidding zones + GB, native 15-minute resolution, history to 2015
- **Price forecasts** — P10/P50/P90 quantiles, 1h–7d ahead, scored publicly against a naive baseline daily
- **Intraday auctions** — IDA1/2/3 for ES/PT (OMIE) and all 7 Italian zones (GME), plus DA-vs-IDA spreads
- **Temperature (Volt Temp)** — station-exact daily Tmax/Tmin distributions in 1°C buckets on the exact
  airport gauges weather markets settle on, CME-city degree-day trackers, population-weighted zone temperature
- **Renewables** — our wind/solar model scored head-to-head against the TSO's forecast in every response
- **Balancing** — imbalance prices (7 markets, revision-aware), FCR/aFRR/mFRR reserve prices, outages
- **Grid** — load, generation mix, carbon intensity, cross-border physical flows
- **Optimization** — cheapest charging window, load schedules, battery arbitrage simulation
- **Webhooks & SSE** — auction results pushed seconds after publication (13:00 CET SDAC + IDA sessions)

Get a **free API key** at [voltcast.com/register](https://voltcast.com/register) — no card required.

## Quickstart

```ts
import { Voltcast } from "@voltcast/sdk";

const vc = new Voltcast("YOUR_API_KEY");

// Tomorrow's prices, native 15-minute periods
const { data } = await vc.prices("DE-LU");

// P10/P50/P90 forecast, 7 days out
const forecast = await vc.forecast("DE-LU", { horizon: "7d" });

// Cheapest 3-hour window in the next 24h (EV charging, batteries)
const window = await vc.cheapestWindow({ zone: "DE-LU", duration_minutes: 180 });

// Our wind/solar model vs the TSO's — verification included in the response
const res = await vc.renewables("DE-LU");
```

### Temperature markets (Volt Temp)

```ts
// Station-exact Tmax distribution for Paris–Le Bourget (the gauge daily
// temperature markets actually settle on — NOT city-center weather)
const paris = await vc.temperature("LFPB", { kind: "tmax" });
// -> quantiles P05–P95 + per-1°C bucket probabilities, verified daily vs METAR

// CME-city degree-day tracker with a probabilistic settle projection
const hdd = await vc.degreeDays("london", { contract: "HDD" });

// Population-weighted zone temperature — the demand metric
const demand = await vc.zoneTemperature("FR");
```

### Error handling

```ts
import { Voltcast, VoltcastError } from "@voltcast/sdk";

try {
  await vc.prices("XX");
} catch (e) {
  if (e instanceof VoltcastError) {
    console.error(e.status, e.code, e.message); // 404 zone_not_found …
  }
}
```

## Why Voltcast

Every forecast we sell is scored in public, every day, against a free
naive-persistence baseline — wins **and losses** — at
[voltcast.com/accuracy](https://voltcast.com/accuracy). If our forecast doesn't
beat the baseline in your zone for a month, that zone is credited automatically.
No other European power-data vendor makes that commitment.

- Live interactive map: [voltcast.com/terminal](https://voltcast.com/terminal)
- Data-backed research: [voltcast.com/research](https://voltcast.com/research)
- Full API reference: [voltcast.com/docs](https://voltcast.com/docs)
- OpenAPI spec: [voltcast.com/openapi.json](https://voltcast.com/openapi.json)
- MCP server for AI agents: `https://voltcast.com/api/mcp`
- Python SDK: [`pip install voltcast`](https://pypi.org/project/voltcast/)

## Plans

Free (1 zone) · Home €9/mo · Starter €49/mo · Volt Temp €99/mo · Pro €199/mo ·
Balancing €299/mo · Scale €499/mo · Quant €999/mo — all self-serve, annual −15%.
Details: [voltcast.com/#pricing](https://voltcast.com/#pricing).

## License

MIT. Data licensing (attribution requirements per source):
[voltcast.com/legal/data-licensing](https://voltcast.com/legal/data-licensing).
