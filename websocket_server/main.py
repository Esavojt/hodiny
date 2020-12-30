import asyncio
import websockets
import threading
import builtins
from datetime import datetime

def tprint(*objs, **kwargs):
    my_prefix = "[WebSocketServer]"
    builtins.print(my_prefix, *objs, **kwargs)


class WebSocketServer(threading.Thread):

    def __init__(self, queueWC2WS, queueWS2WC, eventLoop):
        self.queueWC2WS = queueWC2WS
        self.queueWS2WC = queueWS2WC
        self.eventLoop = eventLoop
        super().__init__()

    def run(self):
        tprint("Starting!")
        asyncio.set_event_loop(self.eventLoop)

        async def handle(websocket, path):
            name = await websocket.recv()
            tprint(f"< {name}")

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")

            greeting = f"Hello {name}! {current_time}"

            await websocket.send(greeting)
            tprint(f"> {greeting}")

        start_server = websockets.serve(handle, "0.0.0.0", 8765)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
