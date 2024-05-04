# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Streamz By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from platformcode import logger
from lib import jsunpack
from core import scrapertools

def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if "<b>File not found, sorry!</b" in data.data:
        return False, "[Youjizz] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    data = scrapertools.find_single_match(data, 'var dataEncodings(.*?)var')
    patron = '"quality":"(\d+)","filename":"([^"]+)",'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        if ".mp4?" in url: serv= "mp4"
        else: serv="m3u8"
        if not url.startswith("https"):
            url = "https:%s" % url.replace("\\", "")
        video_urls.append(['%sp [%s]' %(quality,serv), url])
    return video_urls

