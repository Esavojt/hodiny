import os
import sys
os.system("cp -n config_template.yml config.yml")
os.system("git checkout -- .")
os.system("git pull origin main")
#os.system("sh sync.sh")

import threading
import multiprocessing
import asyncio
from web_server.main import WebServer
from watch_control.main import WatchControl
from websocket_server.main import WebSocketServer
web_server = WebServer()

queueWC2WS = []
queueWS2WC = []

if len(sys.argv) == 2:
    debug = sys.argv[1] == "debug"
else:
    debug = False

watch_control = WatchControl(queueWC2WS, queueWS2WC, debug)
websocket_server = WebSocketServer(queueWC2WS, queueWS2WC, asyncio.get_event_loop(), debug)


if __name__ == '__main__':
    """Get update"""
    
    web_server.start()
    websocket_server.start()
    watch_control.start()
    while True:
        pass
