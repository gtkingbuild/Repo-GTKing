# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger

kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'ignore_response_code': True, 
          'timeout': 5, 'cf_assistant': False}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url, **kwargs).data
    #logger.debug(data)
    if "This video is no longer available" in data or 'no está disponible' in data:
        return False, "[spankbang] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url, **kwargs).data
    # url = scrapertools.find_single_match(data,'<source src="(.*?)"')
    # video_urls.append(['[.mp4]', url])
    if "embed" in page_url:
        page_url = scrapertools.find_single_match(data,'<link rel="canonical" href="([^"]+)"')
    skey = scrapertools.find_single_match(data,'data-streamkey="([^"]+)"')
    # session="523034c1c1fc14aabde7335e4f9d9006b0b1e4984bf919d1381316adef299d1e"
    post = {"id": skey, "data": 0}
    headers = {'Referer': page_url}
    url = "https://spankbang.com/api/videos/stream_embed"
    data = httptools.downloadpage(url, post=post, headers=headers, **kwargs).data
    patron = '"(\d+(?:p|k))":\["([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        if "4k" in quality:
            quality = "2160p"
        video_urls.append(['[spankbang] %s' %quality, url])
    video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return video_urls

