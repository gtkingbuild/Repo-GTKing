# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger, config
import requests

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data

    data = httptools.downloadpage(page_url) #requests.get(page_url)
    if not data.sucess or "Not Found" in data.data or "File was deleted" in data.data or "is no longer available" in data.data:
        return False, "[Userscloud] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    id_ = page_url.rsplit("/", 1)[1]
    fname = scrapertools.find_single_match(data.text, '<h2><b>([^<]+)')
    post = "op=download1&usr_login=&id=%s&fname=%s&referer=&method_free=Descarga Gratis" % (id_, fname)
    data1 = requests.post(page_url, data=post).text
    media_url = scrapertools.find_single_match(data1, '<source src="([^"]+)"')
    ext = scrapertools.get_filename_from_url(media_url)[-4:]
    #config.set_setting("player_mode", 3)
    video_urls.append(["%s [userscloud]" % ext, media_url])
    return video_urls
