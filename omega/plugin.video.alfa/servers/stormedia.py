# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger
from bs4 import BeautifulSoup


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data, server
    data = httptools.downloadpage(page_url).data
    server = scrapertools.get_domain_from_url(page_url).split(".")[-2]
    # server = scrapertools.find_single_match(page_url, '//(?:www.|es.|wwv.|)([A-z0-9-]+).(?:tv|com|vip|xxx|sex)')
    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return False, "[%s] El fichero no existe o ha sido borrado" %server
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    matches = soup.find('div', id='player')
    id= matches["data-id"]
    servidor = matches["data-n"]
    data = matches['data-q']
    for elem in data.split(","):
        elem = elem.split(";")
        quality = elem[0]
        pal = elem[-1]
        num = elem[-2]
        vid = int(int(id)/1000)*1000
        # /cqlvid/  /wqlvid/
        # url = "https://s%s.fapmedia.com/wqpvid/%s/%s/%s/%s/%s_%s.mp4" %(server,s1,s2,id1,id,id,quality)
        url = "https://s%s.stormedia.info/whpvid/%s/%s/%s/%s/%s_%s.mp4"   % (servidor, num, pal,vid, id,id, quality)
        url = url.replace("_720p", "")
        video_urls.append(["[%s] %s" %(server,quality), url])
    video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return video_urls

