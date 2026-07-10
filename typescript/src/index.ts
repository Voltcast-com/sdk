/**
 * Official TypeScript SDK for the Voltcast API (https://voltcast.com/docs).
 *
 *   import { Voltcast } from "@voltcast/sdk";
 *   const vc = new Voltcast("YOUR_API_KEY");
 *   const prices = await vc.prices("DE-LU", { from: "2026-07-10", to: "2026-07-12" });
 */

const DEFAULT_BASE_URL = "https://voltcast.com/api";

export interface PriceRow {
    delivery_start: string;
    delivery_end: string;
    price_eur_mwh: number;
    resolution_flag: "PT15M" | "PT60M";
    source: string;
}

export interface ForecastRow {
    target_start: string;
    resolution_flag: "PT15M";
    p50: number;
    p10?: number;
    p90?: number;
}

export interface Zone {
    code: string;
    eic_code: string;
    name: string;
    country_code: string;
    timezone: string;
    currency: string;
    native_resolution: "PT15M" | "PT60M";
    fifteen_min_since: string | null;
    launch_zone: boolean;
}

export interface CheapestWindow {
    start: string;
    end: string;
    avg_price_eur_mwh: number;
    basis: "published" | "forecast";
}

export interface ScheduleSlot {
    start: string;
    end: string;
    power_kw: number;
    energy_kwh: number;
    price_eur_mwh: number;
    basis: "published" | "forecast";
}

export interface Schedule {
    schedule: ScheduleSlot[];
    energy_kwh: number;
    expected_cost_eur: number;
    baseline_cost_eur: number;
    savings_eur: number;
    savings_pct: number | null;
}

export interface ExportFile {
    year: number;
    format: "parquet" | "csv";
    size_bytes: number;
    url: string;
    expires_at: string;
}

export interface ApiResponse<T> {
    data: T;
    meta: Record<string, unknown>;
}

export class VoltcastError extends Error {
    readonly status: number;

    readonly code: string | null;

    constructor(status: number, code: string | null, message: string) {
        super(`[${status}${code ? ` ${code}` : ""}] ${message}`);
        this.name = "VoltcastError";
        this.status = status;
        this.code = code;
    }
}

export class Voltcast {
    readonly #apiKey: string;

    readonly #baseUrl: string;

    constructor(apiKey: string, baseUrl: string = DEFAULT_BASE_URL) {
        this.#apiKey = apiKey;
        this.#baseUrl = baseUrl;
    }

    /** All bidding zones with EIC codes and resolution metadata. */
    zones(): Promise<ApiResponse<Zone[]>> {
        return this.request("GET", "/v1/zones");
    }

    /** Day-ahead prices (defaults: yesterday → tomorrow, native resolution). */
    prices(
        zone: string,
        options: { from?: string; to?: string; resolution?: "native" | "hourly" } = {},
    ): Promise<ApiResponse<PriceRow[]>> {
        return this.request("GET", `/v1/prices/${zone}`, { query: options });
    }

    /** Latest probabilistic forecast curve. */
    forecast(zone: string, options: { horizon?: "48h" | "7d" } = {}): Promise<ApiResponse<ForecastRow[]>> {
        return this.request("GET", `/v1/forecasts/${zone}`, { query: options });
    }

    /** Cheapest contiguous windows over the forward curve (Pro+). */
    cheapestWindow(body: {
        zone: string;
        duration_minutes: number;
        from?: string;
        to?: string;
        count?: number;
    }): Promise<ApiResponse<CheapestWindow[]>> {
        return this.request("POST", "/v1/optimize/cheapest-window", { body });
    }

    /** Cost-optimal charge/dispatch schedule (Pro+). */
    schedule(body: {
        zone: string;
        energy_kwh: number;
        max_power_kw: number;
        deadline: string;
        start?: string;
    }): Promise<ApiResponse<Schedule>> {
        return this.request("POST", "/v1/optimize/schedule", { body });
    }

    /** Signed bulk-export URLs for zone-year files (Pro+). */
    exportUrls(query: {
        zone: string;
        from: string;
        to: string;
        format?: "parquet" | "csv";
    }): Promise<ApiResponse<ExportFile[]>> {
        return this.request("GET", "/v1/history/export", { query });
    }

    private async request<T>(
        method: string,
        path: string,
        options: { query?: Record<string, unknown>; body?: unknown } = {},
    ): Promise<T> {
        const url = new URL(this.#baseUrl + path);
        for (const [key, value] of Object.entries(options.query ?? {})) {
            if (value !== undefined) url.searchParams.set(key, String(value));
        }

        const response = await fetch(url, {
            method,
            headers: {
                Authorization: `Bearer ${this.#apiKey}`,
                Accept: "application/json",
                ...(options.body ? { "Content-Type": "application/json" } : {}),
            },
            body: options.body ? JSON.stringify(options.body) : undefined,
        });

        if (!response.ok) {
            let code: string | null = null;
            let message = response.statusText;
            try {
                const parsed = (await response.json()) as { error?: { code?: string; message?: string } };
                code = parsed.error?.code ?? null;
                message = parsed.error?.message ?? message;
            } catch {
                /* non-JSON error body */
            }
            throw new VoltcastError(response.status, code, message);
        }

        return (await response.json()) as T;
    }
}
