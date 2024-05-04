# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    if not "embed" in page_url:
        page_url = page_url.replace("http://vidzi.tv/", "http://vidzi.tv/embed-") + ".html"

    data = httptools.downloadpage(page_url).data

    media_urls = scrapertools.find_multiple_matches(data, 'file\s*:\s*"([^"]+)"')

    if not media_urls:
        data = scrapertools.find_single_match(data, "<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
        if not data: return video_urls

        data = jsunpack.unpack(data)
        media_urls = scrapertools.find_multiple_matches(data, 'file\s*:\s*"([^"]+)"')

    subtitle = ''
    for media_url in media_urls:
        if media_url.endswith('.srt'):
            subtitle = 'http://vidzi.tv' + media_url

    for media_url in media_urls:
        if not media_url.endswith('.vtt') and not media_url.endswith('.srt'):
            ext = scrapertools.get_filename_from_url(media_url)[-4:]
            video_urls.append([ext, media_url, 0, subtitle])

    return video_urls
