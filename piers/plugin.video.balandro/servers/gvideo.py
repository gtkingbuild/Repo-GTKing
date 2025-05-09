# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    PY3 = False

    import urllib
else:
    PY3 = True

    import urllib.parse as urllib

import codecs

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info('page_url: %s'%page_url)
    video_urls = []
    urls = []
    streams =[]

    if 'googleusercontent' in page_url:
        response = httptools.downloadpage(page_url, follow_redirects = False, cookies=False, headers={"Referer": page_url})

        if PY3 and isinstance(response.data, bytes): response.data = response.data.decode('utf-8')

        try:
           url = response.headers['location']
        except:
           return "Client has issued a malformed or illegal request"

        if "set-cookie" in response.headers:
            try:
                cookies = ""
                cookie = response.headers["set-cookie"].split("HttpOnly, ")

                for c in cookie:
                    cookies += c.split(";", 1)[0] + "; "

                data = response.data.decode('unicode-escape')
                data = urllib.unquote_plus(urllib.unquote_plus(data))
                headers_string = "|Cookie=" + cookies
            except:
                headers_string = ""
        else:
            headers_string = ""

        quality = scrapertools.find_single_match (url, '.itag=(\d+).')

        streams.append((quality, url))

    else:
        vid = scrapertools.find_single_match(page_url, "(?s)http(?:s|)://(?:docs|drive).google.com/file/d/([^/]+)/(?:preview|edit|view)")
        if vid: page_url = 'http://docs.google.com/get_video_info?docid=' + vid

        response = httptools.downloadpage(page_url, cookies=False, headers={"Referer": page_url})

        if PY3 and isinstance(response.data, bytes): response.data = response.data.decode('utf-8')

        if response.code == 429:
            return "Servidor saturado, inténtelo más tarde"

        if "no+existe" in response.data:
            return "Archivo inexistente ó eliminado"
        elif "Se+ha+excedido+el" in response.data:
            return "Excedido el número de reproducciones permitidas"
        elif "No+tienes+permiso" in response.data:
            return "No tiene permiso para acceder al vídeo"
        elif "Se ha producido un error" in response.data:
            return "Error en el reproductor de google"
        elif "No+se+puede+procesar+este" in response.data:
            return "No se puede procesar el vídeo"

        cookies = ""
        cookie = response.headers["set-cookie"].split("HttpOnly, ")

        for c in cookie:
            cookies += c.split(";", 1)[0] + "; "

        data = codecs.decode(response.data, 'unicode-escape')
        data = urllib.unquote_plus(urllib.unquote_plus(data))

        headers_string = "|Cookie=" + cookies
        url_streams = scrapertools.find_single_match(data, 'url_encoded_fmt_stream_map=(.*)')
        streams = scrapertools.find_multiple_matches(url_streams, 'itag=(\d+)&url=(.*?)(?:;.*?quality=.*?(?:,|&)|&quality=.*?(?:,|&))')

    itags = {'18': '360p', '22': '720p', '34': '360p', '35': '480p', '37': '1080p', '43': '360p', '59': '480p'}

    for itag, video_url in streams:
        if not video_url in urls:
            video_url += headers_string
            video_urls.append([itags[itag], video_url])
            urls.append(video_url)

        video_urls.sort(key=lambda video_urls: int(video_urls[0].replace("p", "")))

    return video_urls
