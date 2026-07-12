"""aiovoltcast client tests against a local aiohttp test server."""

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from aiovoltcast import VoltcastAuthError, VoltcastClient, VoltcastError


async def make_client(handler_map) -> tuple[TestClient, VoltcastClient]:
    app = web.Application()
    for path, handler in handler_map.items():
        app.router.add_get(path, handler)
    client = TestClient(TestServer(app))
    await client.start_server()
    vc = VoltcastClient("test-key", session=client.session, base_url=str(client.make_url("")))
    return client, vc


@pytest.mark.asyncio
async def test_prices_happy_path():
    async def prices(request):
        assert request.headers["Authorization"] == "Bearer test-key"
        return web.json_response({"data": [{"price_eur_mwh": 42.0}], "meta": {"zone": "DE-LU"}})

    client, vc = await make_client({"/v1/prices/DE-LU": prices})
    try:
        body = await vc.prices("DE-LU")
        assert body["data"][0]["price_eur_mwh"] == 42.0
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_auth_error_maps_to_typed_exception():
    async def denied(request):
        return web.json_response(
            {"error": {"code": "unauthenticated", "message": "bad key"}}, status=401
        )

    client, vc = await make_client({"/v1/prices/DE-LU": denied})
    try:
        with pytest.raises(VoltcastAuthError) as excinfo:
            await vc.validate_key("DE-LU")
        assert excinfo.value.code == "unauthenticated"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_api_error_carries_status_and_code():
    async def missing(request):
        return web.json_response(
            {"error": {"code": "zone_not_found", "message": "nope"}}, status=404
        )

    client, vc = await make_client({"/v1/prices/XX": missing})
    try:
        with pytest.raises(VoltcastError) as excinfo:
            await vc.prices("XX")
        assert excinfo.value.status == 404
        assert excinfo.value.code == "zone_not_found"
    finally:
        await client.close()
