# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector streamlare By Alfa development Group
# --------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from core import httptools
from core import scrapertools
from platformcode import logger

url_new = ''
id = ''
kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
          'timeout': 5, 'cf_assistant': False}


def test_video_exists(page_url):
    global url_new, id
    logger.info("(page_url='%s')" % page_url)
    
    response = httptools.downloadpage(page_url, **kwargs)
    
    if not response.sucess or "Not Found" in response.data or "File was deleted" in response.data or "is no longer available" in response.data:
        return False, "[streamlare] El fichero no existe o ha sido borrado"
    id = scrapertools.find_single_match(page_url,'/e/(\w+)')
    url_new = response.url #if response.url and response.url != page_url else ''
    # if not url_new: id = scrapertools.find_single_match(page_url,'<link\s*href="([^"]+)"')
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    global url_new, id
    
    video_urls = []
    matches = []
    server_url = "%s/api/video/stream/get" %httptools.obtain_domain(url_new, scheme=True)
    
    # if url_new:
    if not id: id = scrapertools.find_single_match(page_url,'/e/(\w+)')
    post = {"id": id}
    
    response = httptools.downloadpage(server_url, post=post, **kwargs)

    if response.json:
        json = response.json
        logger.debug(json)
        media_url = json.get('result', {}).get('file', '')
        
        if "xxxxxxxxxxxxxxmaster.m3u8" in media_url:
            data = httptools.downloadpage(media_url, **kwargs).data
            if PY3 and isinstance(data, bytes):
                data = "".join(chr(x) for x in bytes(data))
            
            if data:
                matches_m3u8 = re.compile('#EXT-X-STREAM-INF\:[^\n]*\n([^\n]*)\n', re.DOTALL).findall(data)
                matches_m3u8.reverse()
                for media_url in matches_m3u8:
                    ext = "m3u8" if "m3u8" in media_url else ''
                    matches.append(["%s [streamlare]" % (ext), urlparse.urljoin(server_url, media_url)])
                    break
        else:
            ext = "m3u8" if "m3u8" in media_url else ''
            matches.append(["%s [streamlare]" % (ext), media_url])
    else:
        data = response.data.replace("\\","")
        if response.url_new:
            url_new = response.url_new
            matches.append(['', url_new])
        else:
            matches = scrapertools.find_multiple_matches(data, 'label":"([^"]+).*?file":"([^"]+)')
    # else:   
        # logger.debug('Aqui')
        # matches.append(['', url_new])
    
    for res, media_url in matches:
        media_url += "|User-Agent=%s" % (httptools.get_user_agent(quoted=True))
        video_urls.append([res, media_url])

    return video_urls
