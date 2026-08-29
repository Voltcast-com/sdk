# Voltcast SDKs

Official client libraries for the [Voltcast API](https://voltcast.com/docs) —
15-minute European day-ahead power prices, P10/P50/P90 probabilistic forecasts
(scored publicly every day), station-exact temperature distributions for weather
markets (Volt Temp), renewables, imbalance, optimization endpoints and bulk export.

| SDK | Package | Install |
|---|---|---|
| [Python](./python) | `voltcast` | `pip install voltcast` |
| [TypeScript](./typescript) | `@voltcast/sdk` | `npm install @voltcast/sdk` |

New accounts start with [Home](https://voltcast.com/register?plan=home&utm_source=github&utm_medium=sdk-repository&utm_campaign=home-sdk)
at €9/month after a 7-day card-required trial. Home includes one selected
European bidding zone, native-resolution prices, a 7-day P50 forecast, 90 days
of history, and one webhook rule. Existing Free accounts remain grandfathered.

## Quick taste

```python
import voltcast

vc = voltcast.Client("YOUR_API_KEY")
prices = vc.prices("DE-LU")                  # yesterday → tomorrow, 15-min native
forecast = vc.forecast("DE-LU", horizon="48h")
res = vc.renewables("DE-LU")            # TSO vs volt-res-1 wind/solar, head-to-head
wx = vc.weather("DE-LU")                # centroid point forecast + ensemble band
```

```ts
import { Voltcast } from "@voltcast/sdk";

const vc = new Voltcast("YOUR_API_KEY");
const { data } = await vc.prices("DE-LU");
const paris = await vc.temperature("LFPB");   // station-exact Tmax distribution
const hdd = await vc.degreeDays("london");    // CME-city degree-day tracker
```

Full endpoint reference, webhook signature verification and error codes:
[voltcast.com/docs](https://voltcast.com/docs).

Task-first examples:
[Home Assistant](https://voltcast.com/integrations/home-assistant?utm_source=github&utm_medium=sdk-repository&utm_campaign=home-assistant) ·
[evcc](https://voltcast.com/integrations/evcc?utm_source=github&utm_medium=sdk-repository&utm_campaign=evcc) ·
[n8n](https://voltcast.com/integrations/n8n?utm_source=github&utm_medium=sdk-repository&utm_campaign=n8n) ·
[AI assistants](https://voltcast.com/ai/local-electricity-price?utm_source=github&utm_medium=sdk-repository&utm_campaign=ai-assistant)

## Forecast accuracy, in the open

Every forecast response links its zone's live scorecard — pinball loss and MAE vs
a naive-persistence baseline, recomputed daily: [voltcast.com/accuracy](https://voltcast.com/accuracy).

## Releases

- Python: GitHub release tagged `sdk-py-vX.Y.Z` → publishes to PyPI (trusted publishing)
- TypeScript: GitHub release tagged `sdk-ts-vX.Y.Z` → publishes to npm

## License

MIT — see [LICENSE](./LICENSE). Data licensing (attribution for verbatim prices):
[voltcast.com/legal/data-licensing](https://voltcast.com/legal/data-licensing).
