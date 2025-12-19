# coding:utf-8
import asyncio

from makit.lib._event import AsyncEvent


class StartUp(AsyncEvent):
    def __init__(self):
        super().__init__()
        self.app = None

    async def trigger(self, app):
        self.app = app
        await super().trigger(app)


class Application:
    on_startup = StartUp()

    async def start(self):
        async for result in self.on_startup.iter_trigger(self):
            print(f'connect to {result}')
        # await self.on_startup.trigger(self)


app = Application()


@app.on_startup()
async def connect_db(app):
    print('db connecting...')
    return 'demo'


loop = asyncio.get_event_loop()
loop.run_until_complete(app.start())
