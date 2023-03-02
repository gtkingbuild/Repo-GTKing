# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('/watch/', '/embed/')

    data = httptools.downloadpage(page_url).data

    if "File was deleted" in data or "File not found" in data or 'og:video">' in data:
        return 'El archivo no existe o ha sido borrado'

    url1 = httptools.downloadpage(page_url, follow_redirects=False, only_headers=True).headers.get("location", "")
    referer = {'Referer': page_url}

    url = scrapertools.find_single_match(data, '<meta property="og:video" content="([^"]+)"')

    if not url:
        if "download" in page_url:
            url = httptools.downloadpage("https:" + url1, headers=referer, follow_redirects=False, only_headers=True).headers.get("location", "")
        else:
            url = scrapertools.find_single_match(data, "file:\s*'([^']+)'")

    if url and '/embed/novideo.mp4' not in url:
        if "vidcache" not in url:
            url = "https://www.yourupload.com%s" % url
            location = httptools.downloadpage(url, headers=referer, follow_redirects=False, only_headers=True)
            media_url = location.headers["location"].replace("?start=0", "")
            ext = media_url[-4:]
            media_url += "|Referer=%s" % url
        else:
            ext = url[-4:]
            media_url = url +"|Referer=%s" % page_url

        video_urls.append([ext, media_url])

    return video_urls
