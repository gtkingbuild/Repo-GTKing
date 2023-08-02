# -*- coding: utf-8 -*-
from core import httptools
from core import scrapertools
from platformcode import logger

def test_video_exists(page_url):
    logger.info()
    global server, vid
    server = scrapertools.get_domain_from_url(page_url).split(".")[-2]
    # server = scrapertools.find_single_match(page_url, '(?:www.|)([A-z0-9-]+).com')
    vid = scrapertools.find_single_match(page_url, '([0-9]+)')

    data = httptools.downloadpage(page_url).data
    if "File was deleted" in data\
       or "not Found" in data:
       # or "small" in data:
        return False, "[%s] El video ha sido borrado o no existe" % server
    return True, ""

def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    url= "https://www.%s.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=null&check_speed=0" %(server,vid)
    data = httptools.downloadpage(url).data
    data = scrapertools.find_single_match(data, '"files":(.*?)"quality"')
    patron  = '"([lh])q":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, scrapedurl in matches:
        url =  scrapedurl.replace("\/", "/")
        if "l" in quality: quality = "360p"
        if "h" in quality: quality = "720p"
        video_urls.append(["[%s] %s" %(server,quality), url])
    return video_urls

