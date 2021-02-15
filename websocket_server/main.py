import asyncio
import websockets
import threading
import builtins
from datetime import datetime
import time
import os

def tprint(*objs, **kwargs):
    my_prefix = "[WebSocketServer]"
    builtins.print(my_prefix, *objs, **kwargs)


class WebSocketServer(threading.Thread):

    def __init__(self, queueWC2WS, queueWS2WC, eventLoop):
        self.queueWC2WS = queueWC2WS
        self.queueWS2WC = queueWS2WC
        self.eventLoop = eventLoop
        super().__init__()
        self.daemon = True

    def run(self):
        tprint("Starting!")
        asyncio.set_event_loop(self.eventLoop)

        async def handle(websocket, path):
            args = await websocket.recv()
            """
            == Věci ohledně komunikace: ==
            - client se ptá, server odpovídá
            - 'gtn' (get time now) získá UNIX čas na hodinách
            - 'stn' (set time now) nastaví čas z UNIX času
            - 'sta' (set time automatically) nastaví čas hodin z NTP
            """
            def gtn(args):
                output = int(time.time())
                tprint(">",output)
                return output

            def stn(args):
                """I AM TOO LAZY"""

                output = "ok"
                tprint(">",output)
                return output

            def sta(args):
                os.system("sntp -s time.google.com")

                output = "ok"
                tprint(">",output)
                return output

            switcher={
                    "gtn":gtn,
                    "stn":stn,
                    "sta":sta,
                    }
            tprint("<",args)
            func = switcher.get(args[0:3], lambda args:'Invalid')
            await websocket.send(str(func(args)))
            
        start_server = websockets.serve(handle, "0.0.0.0", 8765)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
