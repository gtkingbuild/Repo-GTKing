# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Pcloud By Alfa development Group
# --------------------------------------------------------
import re
from core import httptools
from core import scrapertools
from platformcode import logger
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data

    data = httptools.downloadpage(page_url)

    if data.code == 404:
        return False, "[pcloud] El archivo no existe o ha sido borrado"
    data = data.data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    video_urls = list()
    v_data = scrapertools.find_single_match(data, "var publinkData = (.*?);").replace("true", "True").replace("false", "False")
    v_info = eval(v_data)

    for link in v_info["variants"]:
        for host in link["hosts"]:
            url = "https://" + host +(link["path"]).replace("\\", "") + "|Referer=%s" % page_url
            qlty = "%sx%s" % (link["width"], link["height"])
            video_urls.append(['%s [pCloud]' % qlty, url])
    return video_urls
