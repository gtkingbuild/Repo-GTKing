# -*- coding: utf-8 -*-
# -*- Server ZPlayer -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    referer = page_url
    if "|" in page_url:
        referer = page_url.split("|")[1]
        page_url = page_url.split("|")[0]
    data = httptools.downloadpage(page_url, headers={"Referer":referer}).data
    if "File is no longer available" in data or "Video link direct restricted" in data:
        return False, "[ZPlayer] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    pat = r'tracks:\[\{\s*file:"([^"]+)"'
    sub = scrapertools.find_single_match(data, pat)
    
    if not 'v2.zplayer' in page_url:
        patron = '"file": "([^"]+)",.*?"type": "([^"]+)"'
        matches = scrapertools.find_multiple_matches(data, patron)
        for video_url, ext in matches:
            ref = scrapertools.find_single_match(video_url, '(.*?&)') + "shared=%s" % page_url
            headers = {"Referer":page_url}
            if "redirect"  in video_url: 
                url = httptools.downloadpage(video_url, headers=headers, follow_redirects=False, only_headers=True).headers.get("location", "")
                url += "|Referer=%s" %page_url
            else:
                url = video_url + "|Referer=%s" % ref
            video_urls.append(["[zplayer] %s" % ext, url, 0, sub])
    else:
        packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
        if packed:
            unpacked = jsunpack.unpack(packed)
        else:
            unpacked = data
        patron = r'sources:\s*\[\{\s*file:"([^"]+)"'
        matches = scrapertools.find_multiple_matches(unpacked, patron)
        for video_url in matches:
            ext = video_url[-4:]
            video_url += "|Referer=https://v2.zplayer.live/"
            video_urls.append(["[zplayer] %s" % ext, video_url, 0, sub])
    return video_urls
