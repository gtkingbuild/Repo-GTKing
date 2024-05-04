# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from .monitor import Monitor

import traceback

try:
    import xbmc, xbmcgui
except:
    pass

from platformcode import config
LIBTORRENT_PATH = config.get_setting("libtorrent_path", server="torrent", default='')

from servers import torrent as torr
lt, e, e1, e2 = torr.import_libtorrent(LIBTORRENT_PATH)


class Dispatcher(Monitor):
    def __init__(self, client):
        super(Dispatcher, self).__init__(client)

    def do_start(self, th, ses):
        self._th = th
        self._ses = ses
        self.start()

    def run(self):
        if not self._ses:
            raise Exception('Invalid state, session is not initialized')

        while self.running:
            a = self._ses.wait_for_alert(1000)
            if a:
                alerts = self._ses.pop_alerts()
                for alert in alerts:
                    with self.lock:
                        for cb in self.listeners:
                            cb(lt.alert.what(alert), alert)
