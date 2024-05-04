# Borrowed and modified from xbmcswift
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import logging
import xbmc
from quasar.addon import ADDON_ID

class XBMCHandler(logging.StreamHandler):
    xbmc_levels = {
        'DEBUG': 0,
        'INFO': 2,
        'WARNING': 3,
        'ERROR': 4,
        'LOGCRITICAL': 5,
    }

    def emit(self, record):
        xbmc_level = self.xbmc_levels.get(record.levelname)
        if isinstance(record.msg, unicode):
            record.msg = record.msg.encode("utf8")
            if PY3: record.msg = record.msg.decode("utf8")
        elif PY3 and isinstance(record.msg, bytes):
            record.msg = record.msg.decode("utf8")
        xbmc.log(self.format(record), xbmc_level)


loggers = {}

def _get_logger(name):
    global loggers

    if loggers.get(name):
        return loggers.get(name)
    else:
        logger = logging.getLogger(ADDON_ID)
        logger.setLevel(logging.DEBUG)
        handler = XBMCHandler()
        handler.setFormatter(logging.Formatter('[%(name)s] %(message)s'))
        logger.addHandler(handler)
        return logger


log = _get_logger(__name__)
