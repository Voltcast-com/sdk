"""aiovoltcast — async client for the Voltcast API, built for Home Assistant.

    from aiovoltcast import VoltcastClient

    async with aiohttp.ClientSession() as session:
        client = VoltcastClient("YOUR_API_KEY", session=session)
        prices = await client.prices("DE-LU")
"""

from .client import (
    VoltcastAuthError,
    VoltcastClient,
    VoltcastConnectionError,
    VoltcastError,
)

__all__ = [
    "VoltcastAuthError",
    "VoltcastClient",
    "VoltcastConnectionError",
    "VoltcastError",
]

__version__ = "0.1.0"
