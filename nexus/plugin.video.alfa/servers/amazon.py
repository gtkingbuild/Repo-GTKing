# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector amazon By Alfa development Group
# --------------------------------------------------------
import re
from core import httptools
from core import scrapertools
from platformcode import logger
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if data.code == 404:
        return False, "[amazon] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    shareid = data.json["shareId"]
    nodeinfo = data.json["nodeInfo"]["id"]
    url = "https://www.amazon.com/drive/v1/nodes/%s/children?resourceVersion=V2&ContentType=JSON&limit=200&asset=ALL&tempLink=true&shareId=%s" %(nodeinfo, shareid)
    json_data = httptools.downloadpage(url).json
    url = json_data["data"][0]["tempLink"]
    video_urls.append(['MP4 [amazon]', url])
    return video_urls
