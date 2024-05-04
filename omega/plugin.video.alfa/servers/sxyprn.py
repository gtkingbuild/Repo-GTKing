# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger

def test_video_exists(page_url):
    logger.info()
    global data
    data = httptools.downloadpage(page_url).data
    if "Not Found" in data:
        return False, "[sxyprn] El video ha sido borrado o no existe"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    url = scrapertools.find_single_match(data, 'data-vnfo=\'{"\w+":"([^"]+)"')
    url= url.replace("\/", "/")
    vid = url.split('/')
    num1 = sum(int(x) for x in str(re.sub(r'\D', '', vid[6])))
    num2 = sum(int(x) for x in str(re.sub(r'\D', '', vid[7])))
    vid[5] = str(int(vid[5]) - num1 - num2)
    url = '/'.join(vid)
    url = url.replace("/cdn/", "https://www.sxyprn.com/cdn8/")
    url = "%s|verifypeer=false" %url
    video_urls.append(["[sxyprn]", url])
    return video_urls

