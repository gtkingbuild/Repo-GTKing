# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector mangovideo By Alfa development Group
# --------------------------------------------------------
from core import httptools
from core import scrapertools
from platformcode import logger

server = {'1': 'http://www.mangovideo.pw/contents/videos/', '7' : 'http://server9.mangovideo.pw/contents/videos/',
          '8' : 'http://s10.mangovideo.pw/contents/videos/', '9' : 'http://server2.mangovideo.pw/contents/videos/',
          '10' : 'http://server217.mangovideo.pw/contents/videos/', '11' : 'http://234.mangovideo.pw/contents/videos/',
          '12' : 'http://98.mangovideo.pw/contents/videos/', '13' : 'http://68.mangovideo.pw/contents/videos/',
          '14' : 'http://183.mangovideo.pw/contents/videos/', '15' : 'http://45.mangovideo.pw/contents/videos/',
          '16' : 'https://46.mangovideo.pw/contents/videos/',
          '18' : 'https://60.mangovideo.pw/contents/videos/', '19' : 'https://new.mangovideo.pw/contents/videos/'
         }


def test_video_exists(page_url):

    response = httptools.downloadpage(page_url)

    if not response.sucess or \
       "Not Found" in response.data \
       or "File was deleted" in response.data \
       or "is no longer available" in response.data:
        return False, "[mangovideo] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info()
    video_urls = []
    data = httptools.downloadpage(page_url).data
    matches = scrapertools.find_multiple_matches(data, 'function/0/https://mangovideo.pw/get_file/(\d+)/\w+/(.*?.mp4)')
    for scrapedserver,scrapedurl in matches:
        scrapedserver = server.get(scrapedserver, scrapedserver)
        url = scrapedserver + scrapedurl
    video_urls.append(["[mangovideo]", url])
    return video_urls