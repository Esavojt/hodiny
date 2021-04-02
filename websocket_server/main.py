import asyncio
import websockets
import threading
import builtins
from datetime import datetime
import time
import os
import json
import subprocess
import re

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
            
            - 'bye' odepíše bye

            - 'gtn' (get time now) získá UNIX čas na hodinách
            - 'stn' (set time now) nastaví čas z UNIX času
            - 'sta' (set time automatically) nastaví čas hodin z NTP
            - 'sns' (switch ntp state) změní zda čas je sync z NTP nebo ne

            - 'scb' (set clock brightness) změní jas hodin
            - 'gcb' (get clock brightness) získá jas hodin

            - 'gcc' (get clock colors) pošle zpět json z barev
            - 'scc' (set clock color) nastaví barvu pixelu
            - 'sct' (set clock theme) nastaví téma hodin
            - 'gct' (get clock theme) získá téma hodin
            - "gtc' (get theme colors) získá barvy, pokud jsou hodiny nastavené na custom

            - 'std' (shutdown) vypne hodiny
            - 'rst' (restart) restartuje hodiny

            - 'gws' (get wifi ssid) získá ssid wifi sítě
            - 'swc' (set wifi credentials) nastaví wifi credentials
            """

            def bye(args):
                return "bye"

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
                        if response[0:3] == "gcb":
                            data = response.split()
                            self.queueWC2WS.pop(0)
                            tprint(">",data[1])
                            return data[1]
            
            def gcc(args):
                self.queueWS2WC.append('gcc')
                while True:
                    if len(self.queueWC2WS) == 1:
                        response = self.queueWC2WS[0]
                        if response[0:3] == "gcc":
                            self.queueWC2WS.pop(0)
                            data = response[4:]
                            return data

            def scc(args):
                self.queueWS2WC.append(args)

            def sct(args):
                self.queueWS2WC.append(args)

            def std(args):
                self.queueWS2WC.append('std')

            def rst(args):
                self.queueWS2WC.append('rst')

            def gct(args):
                self.queueWS2WC.append('gct')
                while True:
                    if len(self.queueWC2WS) == 1:
                        response = self.queueWC2WS[0]
                        if response[0:3] == "gct":
                            self.queueWC2WS.pop(0)
                            data = response[4:]
                            return data

            def gtc(args):
                self.queueWS2WC.append('gtc')
                while True:
                    if len(self.queueWC2WS) == 1:
                        response = self.queueWC2WS[0]
                        if response[0:3] == "gtc":
                            self.queueWC2WS.pop(0)
                            data = response[4:]
                            return data

            def gws(args):
                cmd = "cat /etc/wpa_supplicant/wpa_supplicant.conf"
                process = subprocess.run(cmd, shell=True, capture_output=True)
                wifis = process.stdout.decode("utf-8")
                return re.findall('ssid=".*"', wifis)[0][6:-1]

            def swc(args):
                combo = json.loads(args[3:])
                wconfigfile = open("wpa_supplicant_template.conf")
                wconfig = wconfigfile.read() 
                wconfig = wconfig.replace("%ssid%",combo["ssid"])
                wconfig = wconfig.replace("%pass%",combo["pass"])
                print(wconfig)
                wpa_supplicant = open("/etc/wpa_supplicant/wpa_supplicant.conf","w")
                wpa_supplicant.write(wconfig)
                wpa_supplicant.close()
                return "ok"
                
            switcher={
                    "bye":bye,
                    "gtn":gtn,
                    "stn":stn,
                    "sta":sta,
                    "sns":sns,
                    "scb":scb,
                    "gcb":gcb,
                    "gcc":gcc,
                    "scc":scc,
                    "rst":rst,
                    "std":std,
                    "sct":sct,
                    "gct":gct,
                    "gtc":gtc,
                    "gws":gws,
                    "swc":swc,
                    }
            tprint("<",args)
            func = switcher.get(args[0:3], lambda args:'Invalid')
            await websocket.send(str(func(args)))
            
        start_server = websockets.serve(handle, "0.0.0.0", 8765)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
