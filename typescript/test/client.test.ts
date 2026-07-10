import assert from "node:assert/strict";
import { test } from "node:test";

import { Voltcast, VoltcastError } from "../src/index.ts";

test("zones returns the public registry", async () => {
    const vc = new Voltcast("invalid-key");
    const { data, meta } = await vc.zones();
    assert.ok(data.length >= 40);
    assert.ok(data.some((z) => z.code === "DE-LU"));
    assert.ok((meta.count as number) >= 40);
});

test("invalid key surfaces a typed 401", async () => {
    const vc = new Voltcast("invalid-key");
    await assert.rejects(
        () => vc.prices("DE-LU"),
        (err: unknown) => err instanceof VoltcastError && err.status === 401,
    );
});

test("real key fetches prices when VOLTCAST_TEST_KEY is set", { skip: !process.env.VOLTCAST_TEST_KEY }, async () => {
    const vc = new Voltcast(process.env.VOLTCAST_TEST_KEY!);
    const { data } = await vc.prices("DE-LU");
    assert.ok(data.length > 0);
    assert.ok(typeof data[0].price_eur_mwh === "number");
});
