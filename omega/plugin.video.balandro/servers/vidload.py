# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
    if url:
        if url.startswith('/'): url = 'https://www.vidload.net' + url
        data = httptools.downloadpage(url).data

        bigbangass = pilla_valor('bigbangass', data)
        tnaketalikom = pilla_valor('tnaketalikom', data)

        if bigbangass and tnaketalikom:
            headers = {"Content-Type": "application/x-www-form-urlencoded", "Referer": url}
            post = 'myreason=' + tnaketalikom + '&saveme='
            url = httptools.downloadpage('https://www.vidload.net/streamurl/' + bigbangass + '/', post=post, headers=headers).data.strip()

            if url:
                if url.startswith('/'): url = 'https://www.vidload.net' + url
                headers = {'Referer': 'https://www.vidload.net/streamurl/' + bigbangass + '/'}
                data = httptools.downloadpage(url, headers=headers).data

                url = scrapertools.find_single_match(data, '<source src="([^"]+)')
                if url and url.startswith('http'):
                    video_urls.append(['mp4', url])

    return video_urls

def pilla_valor(nom, data):
    v1 = scrapertools.find_single_match(data, '%s=document\.getElementById\("([^"]+)' % nom)
    if not v1: return None
    v2 = scrapertools.find_single_match(data, '<input type="hidden" id="%s" value="([^"]+)' % v1)
    return v2
