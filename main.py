import threading
import multiprocessing
import asyncio
from web_server.main import WebServer
from watch_control.main import WatchControl
from websocket_server.main import WebSocketServer
import os
web_server = WebServer()

queueWC2WS = []
queueWS2WC = []

watch_control = WatchControl(queueWC2WS, queueWS2WC)
websocket_server = WebSocketServer(queueWC2WS, queueWS2WC, asyncio.get_event_loop())

if __name__ == '__main__':
    """Get update"""
    os.system("git checkout -- .")
    os.system("git pull origin main")
    
    web_server.start()
    websocket_server.start()
    watch_control.start()
    while True:
        pass
