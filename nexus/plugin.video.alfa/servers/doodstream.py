# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector DoodStream By Alfa development Group
# --------------------------------------------------------
import re
import base64
import time
from lib import js2py
from core import httptools
from core import scrapertools
from platformcode import logger

data = ""
host = "https://dood.la"
count = 3
retries = count
kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'CF': True, 'cf_assistant': False, 'ignore_response_code': True}

def test_video_exists(page_url):
    global data, retries
    
    # page_url = page_url.replace('/d/', '/e/')
    logger.info("(page_url='%s'; retry=%s)" % (page_url, retries))

    response = httptools.downloadpage(page_url, **kwargs)
    if '/d/' in page_url and scrapertools.find_single_match(response.data, ' <iframe src="([^"]+)"'):
        url = scrapertools.find_single_match(response.data, ' <iframe src="([^"]+)"')
        page_url = "%s%s" %(host,url)
        response = httptools.downloadpage(page_url, **kwargs)
    if response.code == 404 or "Video not found" in response.data:
        return False, "[Doodstream] El archivo no existe o ha sido borrado"
    elif not scrapertools.find_single_match(response.data, ("(function\s?makePlay.*?;})")) and retries >= 0:
        retries -= 1
        if retries >= 0:
            time.sleep(count - retries)
            return test_video_exists(page_url)
        return False, "[Doodstream] No se ha podido comprobar si el video existe. Reinténtalo más tarde"
    else:
        data = response.data
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    global data, retries
    retries = count
    logger.info("url=" + page_url)
    video_urls = list()
    label = scrapertools.find_single_match(data, r'type:\s*"video/([^"]+)"')
    js_code = scrapertools.find_single_match(data, ("(function\s?makePlay.*?;})"))

    js_code = re.sub(r"\+Date.now\(\)", '', js_code)
    js = js2py.eval_js(js_code)
    makeplay = js() + str(int(time.time()*1000))

    base_url = scrapertools.find_single_match(data, r"\$.get\('(/pass[^']+)'")
    new_data = httptools.downloadpage("%s%s" % (host, base_url), add_referer=True, **kwargs).data
    
    while "We are checking your browser" in new_data or "5xx-error-landing" in new_data:
        retries -= 1
        time.sleep(count - retries)
        new_data = httptools.downloadpage("%s%s" % (host, base_url), add_referer=True, **kwargs).data
        if retries < 0:
            return video_urls

    new_data = re.sub(r'\s+', '', new_data)
    url = new_data + makeplay + "|Referer=%s" % page_url
    video_urls.append(['%s [doodstream]' % label, url])

    return video_urls
