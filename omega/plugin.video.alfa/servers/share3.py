# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector share3 By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)
    if not response.sucess or "Not Found" in response.data or "File was deleted" in response.data or "is no longer available" in response.data:
        return False, "[share3] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    post = scrapertools.find_single_match(page_url, '(data=\w+)')
    url = httptools.downloadpage("https://streams3.com/redirect_post.php", post=post, follow_redirects=False, ignore_response_code = True).headers.get("location", "")
    data = httptools.downloadpage("https://streams3.com" + url, headers={"referer": page_url}).data
    post = "v=" + scrapertools.find_single_match(url, '#(\w+)')
    data = httptools.downloadpage("https://streams3.com/api.php", post=post, headers={"referer": page_url}).data
    uu = scrapertools.find_single_match(data, 'file":"([^"]+)')

    media_url = uu.replace("\\r","").replace("\\","").replace("\r","")
    title = "mp4 [share3]"
    video_urls.append([title, media_url])
    return video_urls
