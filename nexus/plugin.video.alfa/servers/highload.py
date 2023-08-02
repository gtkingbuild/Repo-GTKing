# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Highload By Alfa development Group
# --------------------------------------------------------
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from core import httptools
from core import jsontools
from core import scrapertools
from platformcode import logger
if not PY3: from lib import alfaresolver
else: from lib import alfaresolver_py3 as alfaresolver


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if data.code == 404 or "We can't find the video" in data.data:
        return False, "[HighLoad] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []

    media_url, sub = alfaresolver.get_hl_data(page_url)
    ext = media_url[-4:]
    video_urls.append(['%s [highload]' % ext, media_url,0, sub])
    return video_urls





