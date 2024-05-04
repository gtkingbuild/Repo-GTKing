# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
import random
from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger
if not PY3: from lib import alfaresolver
else: from lib import alfaresolver_py3 as alfaresolver


ver = random.randint(66, 67)
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:%s.0) Gecko/20100101 Firefox/%s.0" % (ver, ver)}

DATA = ''
ranw = False
ranv = True

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    
    data = alfaresolver.get_data(page_url, False, ranw=ranw, ranv=ranv)
    if not "|mp4|" in data:
        dict_cookie = {'domain': '.gamovideo.com', 'expires': 0}
        httptools.set_cookies(dict_cookie)
        data = alfaresolver.get_data(page_url, False, ranw=ranw, ranv=ranv)
    
    global DATA
    DATA = data
    if "images/proced.png" in data:
        return False, "[Gamovideo] El archivo no existe o ha sido borrado"
    if "File was deleted" in data or ("Not Found"  in data and not "|mp4|" in data) or "File was locked by administrator" in data:
        return False, "[Gamovideo] El archivo no existe o ha sido borrado"
    if "Video is processing now" in data:
        return False, "[Gamovideo] El video está procesándose en estos momentos. Inténtelo mas tarde."
    if "File is awaiting for moderation" in data:
        return False, "[Gamovideo] El video está esperando por moderación."

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    data = DATA

    packer = scrapertools.find_single_match(data,
                                            "<script type='text/javascript'>(eval.function.p,a,c,k,e,d..*?)</script>")

    if packer != "":
        try:
            data = jsunpack.unpack(packer)
        except:
            pass
    else:
        original = data
        n = 0
        referer = page_url.replace("embed-","").replace(".html", "")
        data = ""
        while n < 3 and not data:
            
            data1 = alfaresolver.get_data(page_url, False, ranw=ranw, ranv=ranv)
            check_c, data = get_gcookie(data1, True)
            if check_c == False:
                logger.error("Error get gcookie")
            n += 1
    data = re.sub(r'\n|\t|\s+', '', data)

    host = scrapertools.find_single_match(data, r'\[\{image:"(http://[^/]+/)')
    mediaurl = scrapertools.find_single_match(data, r',\{file:"([^"]+)"')
    if not mediaurl.startswith(host):
        mediaurl = host + mediaurl

    video_urls = []
    video_urls.append(["RTMP [gamovideo]", mediaurl])
    video_urls.append([scrapertools.get_filename_from_url(mediaurl)[-4:] + " [gamovideo]", mediaurl])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls

def get_gcookie(data, realcheck=False):
    packer = scrapertools.find_single_match(data,
                                            "<script type='text/javascript'>(eval.function.p,a,c,k,e,d..*?)</script>")
    if packer != "" and realcheck:
        try:
            data = jsunpack.unpack(packer)
            return True, data
        except:
            pass
    patron = '\("\d","(\d)",\d\).*?\'(\w+)'
    scraper = scrapertools.find_single_match(data,patron)
    if scraper:
        gcookie = "%s=%s;" % (scraper[1], scraper[0])
        try:
            old_gcookie = headers['Cookie']
            if gcookie != old_gcookie:
                gcookie = old_gcookie+' '+gcookie
        except:
            pass
        headers.update({"Cookie": gcookie})
        return True, ""
    else:
        return False, ""