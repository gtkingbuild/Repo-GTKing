# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger
from bs4 import BeautifulSoup

kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'ignore_response_code': True, 'cf_assistant': False}

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data, server
    data = httptools.downloadpage(page_url, **kwargs).data
    server = scrapertools.get_domain_from_url(page_url).split(".")[-2]
    # server = scrapertools.find_single_match(page_url, '//(?:www.|es.|)([A-z0-9-]+).(?:com|net|nl|xxx|cz)')
    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return False, "[%s] El fichero no existe o ha sido borrado" %server
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    matches  = soup.video.find_all('source')
    quality = ""
    for elem in matches:
        url = elem['src']
        if elem.get("data-res", ""):
            quality = elem['data-res']
        if elem.get("title", ""):
            quality = elem['title']
        if elem.get("label", ""):
            quality = elem['label']
        if "sd" in quality.lower(): quality = "480p"
        if "hd" in quality.lower(): quality = "720p"
        if "lq" in quality.lower(): quality = "360p"
        if "hq" in quality.lower(): quality = "720p"
        if not quality:
            quality = "480p"
        if not url.startswith("http"):
            url = "http:%s" % url
        url += "|Referer=%s" % page_url
        video_urls.append(["[%s] %s" %(server,quality), url])
    video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return video_urls

