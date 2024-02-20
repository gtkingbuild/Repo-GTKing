# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


if PY3:
    from http.server import BaseHTTPRequestHandler, HTTPServer
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


import xbmc, requests

from threading import Thread

from core import scrapertools
from platformcode import logger


domain = ""


class HandleRequests(BaseHTTPRequestHandler):
    def do_GET(self):
        url = '%s%s' % (domain, self.path)

        if 'redirect.php' in url: url = requests.get(url, allow_redirects=False).headers["location"]

        data = requests.get(url, stream=True).raw

        chunk = data.read()[4:]
        self.wfile.write(chunk)
        self.wfile.close()


def run():
    server_address = ('', 8781)
    httpd = HTTPServer(server_address, HandleRequests)

    monitor = xbmc.Monitor()
    httpd.timeout = 15

    while not monitor.abortRequested():
        try:
            httpd.handle_request()
        except Exception as e:
            logger.error(e)

    httpd.socket.close()


def start(base_url):
    logger.info()

    global domain

    domain = base_url

    Thread(target=run).start()
