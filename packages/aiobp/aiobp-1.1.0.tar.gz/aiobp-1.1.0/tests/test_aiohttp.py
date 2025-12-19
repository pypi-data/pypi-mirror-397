
from aiobp import runner
from aiobp.aiohttp import Provider, Path, dashed
from aiohttp import web


async def hello(request: web.Request, who: Path[dashed]) -> web.Response:
    return web.Response(text=f"Hello, {who}")


provider = Provider()

async def main():
    app = web.Application(middlewares=[provider.middleware])
    app.add_routes([web.get('/{who}', hello)])
    app_runner = web.AppRunner(app)
    await app_runner.setup()
    site = web.TCPSite(app_runner, '0.0.0.0', 8080)
    await site.start()


if __name__ == "__main__":
    runner(main())