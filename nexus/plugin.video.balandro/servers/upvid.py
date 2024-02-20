# -*- coding: utf-8 -*-

import re, base64

from core import httptools, scrapertools
from platformcode import logger

from lib.aadecode import decode as aadecode


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    if 'embed-' not in page_url:
        page_url = page_url.replace('upvid.co/', 'upvid.co/embed-')
        page_url = page_url.replace('upvid.pro/', 'upvid.pro/embed-')
        page_url = page_url.replace('upvid.live/', 'upvid.live/embed-')
        page_url = page_url.replace('upvid.host/', 'upvid.host/embed-')
        page_url = page_url.replace('upvid.biz/', 'upvid.biz/embed-')
        page_url = page_url.replace('upvid.cloud/', 'upvid.cloud/embed-')
        page_url = page_url.replace('upvid.org/', 'upvid.org/embed-')

        page_url = page_url.replace('opvid.co/', 'opvid.co/embed-')
        page_url = page_url.replace('opvid.pro/', 'opvid.pro/embed-')
        page_url = page_url.replace('opvid.live/', 'opvid.live/embed-')
        page_url = page_url.replace('opvid.host/', 'opvid.host/embed-')
        page_url = page_url.replace('opvid.biz/', 'opvid.biz/embed-')
        page_url = page_url.replace('opvid.cloud/', 'opvid.cloud/embed-')
        page_url = page_url.replace('opvid.org/', 'opvid.org/embed-')

    headers = {'Referer': page_url}

    for i in range(0, 3):
        resp = httptools.downloadpage(page_url, headers=headers)

        if resp.code == 404 or "<title>video is no longer available" in resp.data:
            return 'Archivo inexistente ó eliminado'

        if 'Video embed restricted for this domain site2.net' in resp.data:
            headers['Referer'] = headers['Referer'].replace('upvid.host/', 'site2.net/')
            resp = httptools.downloadpage(page_url, headers=headers)

        data = resp.data

        if 'ﾟωﾟﾉ' in data: break
        else:
            page_url = scrapertools.find_single_match(data, '"iframe" src="([^"]+)')
            if not page_url: page_url = scrapertools.find_single_match(data, '<input type="hidden" id="link" value="([^"]+)')

            if not page_url: break

    if 'ﾟωﾟﾉ' not in data: return video_urls

    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    code = scrapertools.find_single_match(data, '(?s)<script>\s*ﾟωﾟ(.*?)</script>').strip()
    text_decode = aadecode(code)
    funcion, clave = re.findall("func\.innerHTML = (\w*)\('([^']*)', ", text_decode, flags=re.DOTALL)[0]

    oculto = re.findall('<input type=hidden value=([^ ]+) id=func', data, flags=re.DOTALL)[0]
    funciones = resuelve(clave, base64.b64decode(oculto))
    url, tipo = scrapertools.find_single_match(funciones, "setAttribute\('src', '(.*?)'\);\s.*?type', 'video/(.*?)'")
    video_urls.append([tipo, url])

    return video_urls


def resuelve(r, o):
    a = '';
    n = 0
    e = range(256)

    for f in range(256):
        n = (n + e[f] + ord(r[(f % len(r))])) % 256
        t = e[f];
        e[f] = e[n];
        e[n] = t

    f = 0;
    n = 0

    for h in range(len(o)):
        f = (f + 1) % 256
        n = (n + e[f]) % 256
        t = e[f];
        e[f] = e[n];
        e[n] = t
        a += chr(ord(o[h]) ^ e[(e[f] + e[n]) % 256])

    return a
