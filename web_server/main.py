import multiprocessing

import os
from http.server import HTTPServer, CGIHTTPRequestHandler
import builtins


def tprint(*objs, **kwargs):
    my_prefix = "[WebServer]"
    builtins.print(my_prefix, *objs, **kwargs)


class WebServer(multiprocessing.Process):

    def __init__(self):
        self.server_object = None
        super().__init__()

    def run(self):
        tprint("Starting!")
        # Make sure the server is created at current directory
        os.chdir('./web_server/www')

        # Create server object listening the port 80
        self.server_object = HTTPServer(server_address=('', 80), RequestHandlerClass=CGIHTTPRequestHandler)
        # Start the web server
        self.server_object.serve_forever(poll_interval=1)


if __name__ == '__main__':
    server = WebServer()
    server.start()
    try:
        while server.is_alive():
            pass
    except KeyboardInterrupt:
        print("Server shutting down")
        server.kill()
