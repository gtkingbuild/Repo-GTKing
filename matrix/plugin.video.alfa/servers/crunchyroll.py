# -*- coding: utf-8 -*-

from builtins import range
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    #from future import standard_library
    #standard_library.install_aliases()
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido

import base64
import struct
import zlib
from hashlib import sha1

from core import filetools
from core import jsontools
from core import httptools
from core import scrapertools
from platformcode import config, logger

GLOBAL_HEADER = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': '*'}
proxy_i = "https://www.usa-proxy.org/index.php"
proxy = "https://www.usa-proxy.org/"


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    
    data = httptools.downloadpage(page_url, headers=GLOBAL_HEADER).data
    #logger.error(data)
    if "showmedia-trailer-notice" in data:
        disp = scrapertools.find_single_match(data, '<a href="/freetrial".*?</span>.*?<span>\s*(.*?)</span>')
        disp = disp.strip()
        if disp:
            disp = "Disponible gratuitamente: %s" % disp
        return False, "[Crunchyroll] Error, se necesita cuenta premium. %s" % disp
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    #page_url='https://www.crunchyroll.com/es-es/one-piece/episode-891-climbing-up-a-waterfall-a-great-journey-through-the-land-of-wanos-sea-zone-786643'
    logger.error("url=" + page_url)
    video_urls = []
    media_url = ''

    file_sub = ""
    
    idiomas = ['deDE', 'ptBR', 'frFR', 'itIT', 'enUS', 'esES', 'esLA']
    index_sub = int(config.get_setting("crunchyrollsub", "crunchyroll"))
    idioma_sub = idiomas[index_sub]
    
    raw_data = scrapertools.find_single_match(data, r'"streams":(\[[^\]]+])')
    
    if idioma_sub == 'esES' and not idioma_sub in raw_data:
        idioma_sub = 'esLA'
    elif idioma_sub == 'esLA' and not idioma_sub in raw_data:
        idioma_sub = 'esES'
    
    if idioma_sub not in raw_data:
        idioma_sub = 'enUS'
    
    json_data = jsontools.load(raw_data)
    #logger.error(json_data)
    for elem in json_data:
        formato = elem.get('format', '')
        if formato in ['vo_adaptive_hls', 'adaptive_hls']:
            lang = elem.get('hardsub_lang', '')
            audio_lang = elem.get('audio_lang', '')

            if lang == idioma_sub:
                media_url = elem.get('url', '')
                break
            if not lang and audio_lang != 'jaJP':
                media_url = elem.get('url', '')
                break
    if not media_url:
        return video_urls

    m3u_data = httptools.downloadpage(media_url, headers=GLOBAL_HEADER).data.decode('utf-8')
        
    matches = scrapertools.find_multiple_matches(m3u_data, 'TION=\d+x(\d+).*?\s(.*?)\s')
    filename = scrapertools.get_filename_from_url(media_url)[-4:]
    
    if matches:
        for quality, media_url in matches:
            video_urls.append(["%s  %sp [crunchyroll]" % (filename, quality), media_url])

    else:
        video_urls.append(["m3u8 [crunchyroll]", media_url])
    return video_urls
