# -*- coding: utf-8 -*-
# -*- Server StreamSB -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from core import httptools
from platformcode import logger
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if not PY3: from lib import alfaresolver
else: from lib import alfaresolver_py3 as alfaresolver


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data

    if "File Not Found" in data or "File is no longer available" in data:
        return False, "[StreamSB] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    return alfaresolver.get_ssb_data(page_url)
