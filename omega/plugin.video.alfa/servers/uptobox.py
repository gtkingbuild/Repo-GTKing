# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    #from future import standard_library
    #standard_library.install_aliases()
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido

from core import httptools
from core import scrapertools
from platformcode import logger

data = ''


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data

    response = httptools.downloadpage(page_url)
    if response.sucess:
        data = response.data

    if "Streaming link:" in data:
        return True, ""
    elif "Unfortunately, the file you want is not available." in data or "Unfortunately, the video you want to see is not available" in data or "This stream doesn" in data\
         or "Page not found" in data or "Archivo no encontrado" in data or not data:
        return False, "[Uptobox] El archivo no existe o ha sido borrado"
    wait = scrapertools.find_single_match(data, "You have to wait ([0-9]+) (minute|second)")
    if len(wait) > 0:
        tiempo = wait[1].replace("minute", "minuto/s").replace("second", "segundos")
        return False, "[Uptobox] Alcanzado límite de descarga.<br/>Tiempo de espera: " + wait[0] + " " + tiempo

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    global data
    
    # Si el enlace es directo de upstream
    if "uptobox" not in page_url:
        if not data: data = httptools.downloadpage(page_url).data
        if "Video not found" in data:
            page_url = page_url.replace("uptostream.com/iframe/", "uptobox.com/")
            data = httptools.downloadpage(page_url).data
            video_urls = uptobox(page_url, data)
        else:
            video_urls = uptostream(data)
    else:
        if not data: data = httptools.downloadpage(page_url).data
        # Si el archivo tiene enlace de streaming se redirige a upstream
        if "Streaming link:" in data:
            page_url = "http://uptostream.com/iframe/" + scrapertools.find_single_match(page_url,
                                                                                      'uptobox.com/([a-z0-9]+)')
            data = httptools.downloadpage(page_url).data
            video_urls = uptostream(data)
        else:
            # Si no lo tiene se utiliza la descarga normal
            video_urls = uptobox(page_url, data)

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))
    return video_urls


def uptostream(data):
    
    video_id = scrapertools.find_single_match(data,"var videoId\s*=\s*'([^']+)';")
    subtitle = scrapertools.find_single_match(data, "kind='subtitles' src='//([^']+)'")
    if subtitle:
        subtitle = "http://" + subtitle
    video_urls = []
    api_url = "https://uptostream.com/api/streaming/source/get?token=null&file_code=%s" % video_id
    
    api_data = httptools.downloadpage(api_url).json
    js_code = api_data.get('data', '').get('sources', '')
    
    from lib import js2py
    
    context = js2py.EvalJs({'atob': atob})
    context.execute(js_code)
    result = context.sources

    for x in result:
        media_url = x.get('src', '')
        tipo = x.get('type', '')
        res = x.get('label', '')
        #lang = x.get('lang', '')
        tipo = tipo.replace("video/","")
        extension = ".%s (%s)" % (tipo, res)
        #if lang:
        #    extension = extension.replace(")", "/%s)" % lang[:3])
        video_urls.append([extension + " [uptostream]", media_url, 0, subtitle])
    return video_urls

def atob(s):
    import base64
    return base64.b64decode('{}'.format(s)).decode('utf-8')

def uptobox(url, data):
    
    video_urls = []
    matches = scrapertools.find_multiple_matches(data, """input name=["']([^"']+)["'] value=["']([^"]+)["'] type=["']hidden["']""")
    matches = ["{}={}".format(name, value) for name, value in matches]
    post = "&".join(matches)
    base = scrapertools.find_single_match(url, "\w+://.+?[^/]")
    
    data = httptools.downloadpage(url, post=post, headers={'origin': base}, referer=url, random_headers=True, hide_infobox=False).data
    media = scrapertools.find_multiple_matches(data, """<a href=["']([^"']+)["'] class=["']big-button-green.+?>""")

    # Solo es necesario codificar la ultima parte de la url
    for m in media:
        if "uptobox.com" in m:
            media = m
            url_strip = urllib.quote(media.rsplit('/', 1)[1])
            media_url = media.rsplit('/', 1)[0] + "/" + url_strip
            video_urls.append([media_url[-4:] + " [uptobox]", media_url])
            break

    return video_urls
