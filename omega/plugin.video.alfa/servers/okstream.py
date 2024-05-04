# -*- coding: utf-8 -*-


import re
from core import httptools
from platformcode import logger
from core import scrapertools


id_server = "okstream"

def test_video_exists(page_url):

    logger.info("(page_url='%s')" % page_url)

    global data
    data = httptools.downloadpage(page_url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    if "File was deleted" in data\
      or "Page Not Found" in data\
      or data and "|videojs7|" in data:
        return False, "[%s] El video se está procesando." %id_server
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    keys = scrapertools.find_single_match(data, '>var keys="([^"]+)"')
    protection = scrapertools.find_single_match(data, '>var protection="([^"]+)"')
    posturl = "https://www.okstream.cc/request/"
    post = '&morocco=%s&mycountry=%s' %(keys, protection)
    url =  httptools.downloadpage(posturl, post=post, headers={'Referer':page_url}).data
    url = url.strip()
    video_urls.append(["[%s]" %id_server, url])
    return video_urls
