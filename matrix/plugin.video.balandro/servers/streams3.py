# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    resp = httptools.downloadpage(page_url)
    if not resp.sucess or "Not Found" in resp.data or "File was deleted" in resp.data or "is no longer available" in resp.data:
        return 'El archivo ha sido eliminado o no existe'

    post = scrapertools.find_single_match(page_url, '(data=\w+)')
    url = httptools.downloadpage("https://streams3.com/redirect_post.php", post=post, follow_redirects=False).headers.get("location", "")

    data = httptools.downloadpage("https://streams3.com" + url, headers={"referer": page_url}).data

    post = "v=" + scrapertools.find_single_match(url, '#(\w+)')
    data = httptools.downloadpage("https://streams3.com/api.php", post=post, headers={"referer": page_url}).data

    url = scrapertools.find_single_match(data, 'file":"([^"]+)')
    url = url.replace("\\r","").replace("\\","").replace("\r","")

    if url:
        video_urls.append(['mp4', url])

    return video_urls
