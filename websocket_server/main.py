import asyncio
import websockets
import threading
import builtins
from datetime import datetime
import time
import os
import json

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
            - 'sns' (switch ntp state) změní zda čas je sync z NTP nebo ne

            - 'scb' (set clock brightness) změní jas hodin
            - 'gcb' (get clock brightness) získá jas hodin
            """
            def gtn(args):
                output = int(time.time())
                tprint(">",output)
                return output

            def stn(args):
                args = args.split()
                ts = int(args[1])
                time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                os.system(f"timedatectl set-time '{time}'")
                output = "ok"
                tprint(">",output)
                return output

            def sta(args):
                os.system(f"timedatectl set-ntp true")
                output = "ok"
                tprint(">",output)
                return output
            
            def sns(args):
                args = args.split()
                os.system(f"timedatectl set-ntp {args[1]}")
                tprint(">",'ok')
                return 'ok'

            def scb(args):
                self.queueWS2WC.append(args)
                tprint(">",'ok')
                return 'ok̈́'
            
            def gcb(args):
                self.queueWS2WC.append('gcb')
                while True:
                    if len(self.queueWC2WS) == 1:
                        response = self.queueWC2WS[0]
                        if response[0:3] == 'gcb':
                            data = response.split()
                            self.queueWC2WS.pop(0)
                            tprint(">",data[1])
                            return data[1]

            switcher={
                    "gtn":gtn,
                    "stn":stn,
                    "sta":sta,
                    "sns":sns,
                    "scb":scb,
                    "gcb":gcb,
                    }
            tprint("<",args)
            func = switcher.get(args[0:3], lambda args:'Invalid')
            await websocket.send(str(func(args)))
            
        start_server = websockets.serve(handle, "0.0.0.0", 8765)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
