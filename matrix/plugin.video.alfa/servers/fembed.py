# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Fembed By Alfa Development Group
# --------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from core import httptools
from core import scrapertools
from platformcode import logger

kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'ignore_response_code': True, 'cf_assistant': False}


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    
    _id = scrapertools.find_single_match(page_url, "/(?:f|v)/([A-z0-9_-]+)")
    if _id:
        page_url = 'https://www.fembed.com/api/source/%s' % _id
    post = "r=&d=feurl.com"
    
    data = httptools.downloadpage(page_url, post=post, **kwargs).json
    
    status = data.get('success', '')
    if status == False:
        return False, "[Fembed] El video ha sido borrado"
    elif not status:
        return False, "[Fembed] Error al acceder al video"
    
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    
    video_urls = []
    
    base_sub = "https://thumb.fvs.io/asset/userdata/240560/caption/%s/%s.%s"
    try:
        sub_data = data.get("captions", [])[0]
        subtitle = base_sub % (sub_data['hash'], sub_data['id'], sub_data['extension'])
    except:
        subtitle = ''

    for url in data["data"]:
        try:
            url["file"] = url["file"].replace('https', 'http')
            ua = httptools.get_user_agent(quoted=True)
            headers = httptools.default_headers.copy()
            header_str = "&".join(["%s=%s" % (x, y) for x, y in list(headers.items()) if x!='User-Agent'])
            url["file"] += "|User-Agent=%s&verifypeer=false&%s" % (ua, header_str)
        except:
            pass

        video_urls.append([url["label"] + " [Fembed]", url["file"], 0, subtitle])
    
    return video_urls
