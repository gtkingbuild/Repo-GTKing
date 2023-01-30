# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import http.server as BaseHTTPServer                                        # Es muy lento en PY2.  En PY3 es nativo
    from socketserver import ThreadingMixIn
else:
    import BaseHTTPServer                                                       # Usamos el nativo de PY2 que es más rápido
    from SocketServer import ThreadingMixIn

import traceback
from threading import Thread

from platformcode import logger


class Server(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    daemon_threads = True
    timeout = 1
    def __init__(self, address, handler, client):
        BaseHTTPServer.HTTPServer.__init__(self,address,handler)
        self._client = client
        self.running = True
        self.request = None

    def stop(self):
        self.running = False

    def serve(self):
        while self.running:
            try:
                self.handle_request()
            except:
                logger.error(traceback.format_exc())

    def run(self):
        t = Thread(target=self.serve, name='HTTP Server')
        t.daemon=self.daemon_threads
        t.start()

    def handle_error(self, request, client_address):
        if not "socket.py" in traceback.format_exc():
            logger.error(traceback.format_exc())