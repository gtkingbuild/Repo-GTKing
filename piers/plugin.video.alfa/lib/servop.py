# -*- coding: utf-8 -*-
# --------------------------------------------------------
# By Alfa development Group
# --------------------------------------------------------

import requests
import xbmc
from platformcode import logger

import sys, base64
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    from http.server import BaseHTTPRequestHandler, HTTPServer
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

domain = ""


class HandleRequests(BaseHTTPRequestHandler):

    def do_GET(self):

        url = "%s%s" % (domain, self.path)

        if "redirect.php" in url:
            url = requests.get(url, allow_redirects=False).headers["location"]

        data = requests.get(url, stream=True).raw
        chunk = data.read()[4:]
        self.wfile.write(chunk)
        self.wfile.close()


def run():
    server_address = ('', 8781)
    httpd = HTTPServer(server_address, HandleRequests)
    monitor = xbmc.Monitor()
    httpd.timeout = 1
    while not monitor.abortRequested():
        try:
            httpd.handle_request()
        except Exception as e:
            logger.error(e)
    httpd.socket.close()


def start(base_url):
    global domain

    domain = base_url
    Thread(target=run).start()
