import os
os.system("cp -n config_template.yml config.yml")
os.system("git pull origin main")
import threading
import multiprocessing
import asyncio
from web_server.main import WebServer
from watch_control.main import WatchControl
from websocket_server.main import WebSocketServer
web_server = WebServer()

queueWC2WS = []
queueWS2WC = []

watch_control = WatchControl(queueWC2WS, queueWS2WC)
websocket_server = WebSocketServer(queueWC2WS, queueWS2WC, asyncio.get_event_loop())

if __name__ == '__main__':
    """Get update"""
    
    web_server.start()
    websocket_server.start()
    watch_control.start()
    while True:
        pass
