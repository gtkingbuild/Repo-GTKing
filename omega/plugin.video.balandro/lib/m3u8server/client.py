# -*- coding: utf-8 -*-

import base64, random, time, os
from threading import Thread

from .handler import Handler
from .server import Server

from platformcode import config, logger
from core import httptools


class Client(object):
    def __init__(self, url, port=None, ip=None, auto_shutdown=True, wait_time=20, timeout=5, is_playing_fnc=None):

        self.port = port if port else random.randint(8000,8099)
        self.ip = ip if ip else "127.0.0.1"
        self.url_base = 'https://%s:%s/' % (self.ip, self.port)

        self.connected = False
        self.start_time = None
        self.last_connect = None
        self.is_playing_fnc = is_playing_fnc
        self.auto_shutdown = auto_shutdown
        self.wait_time = wait_time
        self.timeout = timeout
        self.running = False
        self.file_local = None

        self._server = Server((self.ip, self.port), Handler, client=self)

        if url.startswith('http'): self.add_url(url)
        else: self.add_nourl(url)

        if self.file_local: self.start()

    def start(self):
        self.start_time = time.time()
        self.running = True
        self._server.run()
        t = Thread(target=self._auto_shutdown)
        t.setDaemon(True)
        t.start()
        logger.info("M3U8 Server Started " + self.url_base)

    def stop(self):
        self.running = False
        self._server.stop()
        logger.info("M3U8 Server Stopped " + self.url_base)

    def get_file(self):
        return self.file_local

    def add_url(self, url):
        dom = '/'.join(url.split('/')[:3])
        dom_path = '/'.join(url.split('/')[:-1])

        try:
            if '/m3u8/index_' in url: headers = {'Referer': url.replace('/m3u8/index_', '/player.php?id=').replace('.m3u8', '')}
            else: headers = {}

            data = httptools.downloadpage(url, headers=headers).data

            if not data or data == 'error html': raise()

            data_local = ''

            for lin in data.splitlines():
                if lin.startswith('#'): data_local += lin

                elif lin.startswith('//'):
                   lin = lin.replace('//', 'https://')
                   data_local += self.url_base + lin

                elif lin.startswith('http'): data_local += self.url_base + base64.b64encode(lin.encode('utf-8')).decode('utf-8')
                elif lin.startswith('/'): data_local += self.url_base + base64.b64encode(dom + lin)
                else: data_local += self.url_base + base64.b64encode(dom_path + '/' + lin)

                data_local += '\n'

            self.file_local = os.path.join(config.get_data_path(), "m3u8hls.m3u8")
            with open(self.file_local, 'w') as f: f.write(data_local); f.close()
        except:
            self.file_local = None

    def add_nourl(self, url):
        try:
            data_local = ''
            for lin in url.splitlines():
                if lin.startswith('#'): data_local += lin
                elif lin.startswith('http'): data_local += self.url_base + base64.b64encode(lin)

                data_local += '\n'

            self.file_local = os.path.join(config.get_data_path(), "m3u8hls.m3u8")
            with open(self.file_local, 'w') as f: f.write(data_local); f.close()
        except:
            self.file_local = None

    def _auto_shutdown(self):
        while self.running:
            time.sleep(1)

            if self.is_playing_fnc and self.is_playing_fnc(): self.last_connect = time.time()

            if self.auto_shutdown:
                # ~ logger.info("shutdown por haber cerrado el reproductor")
                if self.connected and self.last_connect and self.is_playing_fnc and not self.is_playing_fnc():
                    if time.time() - self.last_connect - 1 > self.timeout: self.stop()

                # ~ logger.info("shutdown por no realizar ninguna conexion")
                if self.start_time and self.wait_time and not self.connected:
                    if time.time() - self.start_time - 1 > self.wait_time: self.stop()
