# pysenz package

[![PyPI](https://img.shields.io/pypi/v/pysenz)](https://pypi.org/project/pysenz) ![PyPI - Downloads](https://img.shields.io/pypi/dm/pysenz) [![PyPI - License](https://img.shields.io/pypi/l/pysenz?color=blue)](https://github.com/nordicopen/pysenz/blob/main/COPYING)

This repo is based on a fork from https://github.com/milanmeu/aiosenz

An async Python wrapper for the nVent (aka Chemelex) Raychem SENZ RestAPI.

## Installation

```bash
pip install pysenz
```

## OAuth2

This package offers an `AbstractSENZAuth`, where you should handle the OAuth2 tokens and provide a valid access token in `get_access_token()`. You can use `SENZAuth` if you don't want to handle the OAuth2 tokens yourself.

## Grant type

`SENZAuth` uses the Authorization Code grant type. This requires a Client ID and Client Secret, more information is available in [the RestAPI documentation](https://api.senzthermostat.nvent.com).

## Scopes

pysenz uses the `restapi`, `openid`, and `offline_access` scope, this is set as default in SENZAuth and should be set in the OAuth2 client if you are using the AbstractSENZAuth class.

## Example

```python
from asyncio import run
from pysenz import SENZAuth, SENZAPI
import httpx

async def main():
    async with httpx.AsyncClient() as httpx_client:
        senz_auth = SENZAuth(
            httpx_client,
            "YOUR_CLIENT_ID",
            "YOUR_CLIENT_SECRET",
            redirect_uri="http://localhost:8080/auth/callback",
        )
        uri, state = await senz_auth.get_authorization_url()
        print("Authorization URI: ", uri)
        authorization_response = input("The authorization response URL: ")
        await senz_auth.set_token_from_authorization_response(authorization_response)

        senz_api = SENZAPI(senz_auth)
        thermostats = await senz_api.get_thermostats()
        for thermostat in thermostats:
            print(f"{thermostat.name} temperature: {thermostat.current_temperatue}")
        await senz_auth.close()

run(main())
```
