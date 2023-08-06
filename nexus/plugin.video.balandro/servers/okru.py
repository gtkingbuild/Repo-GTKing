# -*- coding: utf-8 -*-

import re

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    if 'okru.link' in page_url:
        v = scrapertools.find_single_match(page_url, "t=(\w+)")

        data = httptools.downloadpage("https://okru.link/details.php?v=" + v).data

        video = scrapertools.find_single_match(str(data), '"file":"(.*?)"')
        video = video.replace('\\/', '/')

        if video: video_urls.append(['mp4', video])

        return video_urls

    elif '/embed.html' in page_url or  '/embed_vf.html' in page_url:
       if '/embed.html' in page_url: new_page_url = page_url.replace('/embed.html?t=', '/details.php?v=')
       else: new_page_url = page_url.replace('/v2/embed_vf.html?t=', '/details.php?v=')

       post = scrapertools.find_single_match(new_page_url, "v=(.*?)$")

       if post:
           data = httptools.downloadpage(new_page_url, post = {'v': post}).data

           video = scrapertools.find_single_match(data, '"file":"(.*?)"')
           video = video.replace('\\/', '/')

           if video: video_urls.append(['mp4', video])

           return video_urls

    data = httptools.downloadpage(page_url).data

    if "copyrightsRestricted" in data or "COPYRIGHTS_RESTRICTED" in data or "LIMITED_ACCESS" in data:
        return 'El archivo ha sido eliminado por violación del copyright'
    elif "notFound" in data:
        return 'El archivo no existe o ha sido eliminado'

    data = scrapertools.decodeHtmlentities(data).replace('\\', '')

    for tipo, url in re.findall(r'\{"name":"([^"]+)","url":"([^"]+)"', data, re.DOTALL):
        url = url.replace("%3B", ";").replace("u0026", "&")
        video_urls.append([tipo, url])

    return video_urls
