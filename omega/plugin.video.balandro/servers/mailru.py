# -*- coding: utf-8 -*-

import re, time

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % (page_url))

    if re.match('https://my.mail.ru/video/embed/([A-z0-9\-]+)', page_url):
        return get_video_url_embed(page_url, url_referer)
    else:
        return get_video_url_orig(page_url, url_referer)


def get_video_url_orig(page_url, url_referer=''):
    logger.info("(page_url='%s')" % (page_url))
    video_urls = []

    # Carga la página para coger las cookies
    data = httptools.downloadpage(page_url).data

    url = page_url.replace("embed/", "").replace(".html", ".json")

    resp = httptools.downloadpage(url)
    if '"error":"video_not_found"' in resp.data or '"error":"Can\'t find VideoInstance"' in resp.data:
        return 'Archivo inexistente ó eliminado'

    data = jsontools.load(resp.data)

    if 'videos' not in data: return []

    # La cookie video_key necesaria para poder visonar el video
    cookie_video_key = scrapertools.find_single_match(resp.headers["set-cookie"], '(video_key=[a-f0-9]+)')

    # Formar url del video + cookie video_key
    for videos in data['videos']:
        media_url = videos['url'] + "|Referer=https://my1.imgsmail.ru/r/video2/uvpv3.swf?75&Cookie=" + cookie_video_key

        if not media_url.startswith("http"): media_url = "http:" + media_url
        quality = " %s" % videos['key']

        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + quality, media_url])

    try:
        video_urls.sort(key=lambda video_urls: int(video_urls[0].rsplit(" ", 2)[1][:-1]))
    except:
        pass

    return video_urls


def get_video_url_embed(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    vid = scrapertools.find_single_match(page_url, "my.mail.ru/video/embed/([A-z0-9\-]+)")
    if not vid: return video_urls

    ts = int(time.time()*1000)
    url = 'https://my.mail.ru/+/video/meta/%s?xemail=&ajax_call=1&func_name=&mna=&mnb=&ext=1&_=%s' % (vid, ts)

    resp = httptools.downloadpage(url, headers={'Referer': page_url})

    if not 'set-cookie' in resp.headers: return video_urls
    ck = scrapertools.find_single_match(resp.headers['set-cookie'], '(video_key=[^;]+)')
    if not ck: return video_urls

    bloque = scrapertools.find_single_match(resp.data, '"videos":\[(.*?\})\]')

    matches = scrapertools.find_multiple_matches(bloque, '\{(.*?)\}')
    for vid in matches:
        url = scrapertools.find_single_match(vid, '"url":"([^"]+)')
        if not url: continue
        if url.startswith('//'): url = 'https:' + url
        lbl = scrapertools.find_single_match(vid, '"key":"([^"]+)')
        if not lbl: lbl = 'mp4'
        video_urls.append([lbl, url+'|Referer=https://my.mail.ru/&Cookie='+ck])

    try:
        video_urls.sort(key=lambda video_urls: int(video_urls[0].replace('p', '')) if video_urls[0].endswith('p') else 0)
    except:
        pass

    return video_urls
