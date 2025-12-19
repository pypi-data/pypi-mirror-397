import asyncio

import aiohttp

from rotarex_api import RotarexApi


async def main():
    async with aiohttp.ClientSession() as session:
        api = RotarexApi(session)
        api.set_credentials("test4433@site.com", "123456")
        tanks = await api.fetch_tanks()
        print(tanks)


if __name__ == "__main__":
    asyncio.run(main())
