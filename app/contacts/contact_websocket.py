import asyncio
import websockets

from app.utility.base_world import BaseWorld


class Contact(BaseWorld):

    def __init__(self, services):
        self.name = 'websocket'
        self.description = 'Accept data through web sockets'
        self.log = self.create_logger('contact_websocket')
        self.log.level = 100
        self.handler = Handler(services)
        self.stop_future = asyncio.Future()

    async def start(self):
        web_socket = self.get_config('app.contact.websocket')
        try:
            async with websockets.serve(self.handler.handle, *web_socket.split(':'), logger=self.log):
                await self.stop_future

        except OSError as e:
            self.log.error("WebSocket error: {}".format(e))

    async def stop(self):
        self.stop_future.set_result('')


class Handler:

    def __init__(self, services):
        self.services = services
        self.handles = []
        self.log = BaseWorld.create_logger('websocket_handler')

    async def handle(self, connection):
        try:
            path = connection.request.path
            for handle in [h for h in self.handles if path.split('/', 1)[1].startswith(h.tag)]:
                await handle.run(connection, path, self.services)
        except Exception as e:
            self.log.debug(e)
