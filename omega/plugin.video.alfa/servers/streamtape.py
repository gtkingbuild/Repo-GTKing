# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector streamtape By Alfa development Group
# --------------------------------------------------------
import re
from core import httptools
from core import scrapertools
from lib import js2py
from platformcode import logger
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int



def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url, referer=page_url).data

    if "Video not found" in data:
        return False, "[streamtape] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    video_urls = []
    # Code taken from Kodi On Demand (KOD)
    # https://github.com/kodiondemand/addon/blob/master/servers/streamtape.py
    find_url = scrapertools.find_multiple_matches(data, 'innerHTML = ([^;]+)')[-1]
    possible_url = js2py.eval_js(find_url)
    url = "https:" + possible_url
    url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get("location", "")

    video_urls.append(['MP4 [streamtape]', "{}|{}".format(url, "User-Agent=%s" % httptools.get_user_agent())])

    return video_urls
