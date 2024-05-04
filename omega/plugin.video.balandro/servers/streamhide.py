# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger

from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('https://streamhide.to/e/https://streamhide.to/e/', 'https://streamhide.to/e/')
    page_url = page_url.replace('https://streamhide.to/d/https://streamhide.to/d/', 'https://streamhide.to/d/')
    page_url = page_url.replace('https://streamhide.to/w/https://streamhide.to/w/', 'https://streamhide.to/w/')

    page_url = page_url.replace('https://streamhide.to/e/https://playhide.online/e/', 'https://streamhide.to/e/')
    page_url = page_url.replace('https://streamhide.to/d/https://playhide.online/d/', 'https://streamhide.to/d/')
    page_url = page_url.replace('https://streamhide.to/w/https://playhide.online/w/', 'https://streamhide.to/w/')

    page_url = page_url.replace('https://streamhide.to/e/https://streamhide.com/e/', 'https://streamhide.to/e/')
    page_url = page_url.replace('https://streamhide.to/d/https://streamhide.com/d/', 'https://streamhide.to/d/')
    page_url = page_url.replace('https://streamhide.to/w/https://streamhide.com/w/', 'https://streamhide.to/w/')

    page_url = page_url.replace('//playhide.online/e/', '//streamhide.to/e/').replace('//playhide.online/d/', '//streamhide.to/e/').replace('//playhide.online/w/', '//streamhide.to/e/')

    page_url = page_url.replace('//guccihide.com/e/', '//streamhide.to/e/').replace('//guccihide.com/', '//streamhide.to/e/').replace('//guccihide.com/w/', '//streamhide.to/e/')
    page_url = page_url.replace('//moviesm4u.com/e/', '//streamhide.to/e/').replace('//moviesm4u.com/', '//streamhide.to/e/').replace('//moviesm4u.com/w/', '//streamhide.to/e/')
    page_url = page_url.replace('//louishide.com/e/', '//streamhide.to/e/').replace('//louishide.com/', '//streamhide.to/e/').replace('//louishide.com/w/', '//streamhide.to/e/')
    page_url = page_url.replace('//ahvsh.com/e/', '//streamhide.to/e/').replace('//ahvsh.com/', '//streamhide.to/e/').replace('//ahvsh.com/w/', '//streamhide.to/e/')
    page_url = page_url.replace('//movhide.pro/e/', '//streamhide.to/e/').replace('//movhide.pro/', '//streamhide.to/e/').replace('//movhide.pro/w/', '//streamhide.to/e/')

    response = httptools.downloadpage(page_url)

    data = response.data

    if not response.sucess or "Not Found" in data or "File was deleted" in data or "is no longer available" in data:
        return "Archivo inexistente ó eliminado"

    url = scrapertools.find_single_match(data, 'sources: \[{file:"([^"]+)"')

    if not url:
        packed = scrapertools.find_single_match(data, r'"text/javascript"[^>]*>(eval\(.*?)</script>')

        if packed:
           unpacked = jsunpack.unpack(packed)

           url = scrapertools.find_single_match(str(unpacked), 'file:"([^"]+)"')

    if url:
        video_urls.append(['mp4', url])

    return video_urls
