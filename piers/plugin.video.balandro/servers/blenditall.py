# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import os, codecs


from core import httptools, scrapertools
from platformcode import config, logger, platformtools


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    if '|' in page_url:
        referer_url = page_url.split('|')[1]
        page_url = page_url.split('|')[0]
    else: referer_url = ''

    ref = page_url.split('//', 1)

    resp = httptools.downloadpage(page_url, headers = {'Referer': ref[0] + '//' + ref[1]})

    if resp.code == 404:
        return 'Archivo inexistente ó eliminado'

    if resp.data: data = resp.data
    else:
        return 'El archivo no contiene datos'
 
    if PY3 and isinstance(data, bytes):
        data = "".join(chr(x) for x in bytes(data))

    if not isinstance(data, bytes):
        datos = data
        try: data = codecs.decode(str(data), 'utf-8', 'strict')
        except: data = datos

    v_type = 'hls'

    url = page_url

    headers = {'Referer': referer_url}

    if "const source = '" in data: url = scrapertools.find_single_match(data, "const source = '(.*?)'")

    elif '"file": ' in data: url, v_type = scrapertools.find_single_match(data, '"file": "(.*?)",\s+"type": "(.*?)"')

    if v_type == 'mp4':
        url = httptools.downloadpage(url, headers=headers, follow_redirects=False).headers.get('location', '')

        if url:
            url = "%s|Referer=%s&User-Agent=%s" % (url, page_url, httptools.get_user_agent())

            video_urls.append(['mp4', url])

    elif v_type == 'hls':
        if '.hls' in data: hls_data = data
        else:
            hls_data = httptools.downloadpage(url, headers=headers, follow_redirects=False).data

            if PY3 and isinstance(hls_data, bytes):
                hls_data = "".join(chr(x) for x in bytes(hls_data))

            if not isinstance(hls_data, bytes):
                datos = hls_data
                try: hls_data = codecs.decode(hls_data, 'utf-8', 'strict')
                except: hls_data = datos

        base_url = scrapertools.find_single_match(hls_data, "((?:https?:)?\/\/[^\/]+)")

        if base_url: hls_data = hls_data.replace(base_url, 'http://localhost:8781')

        if not base_url.startswith('http'): base_url = 'https:%s' % base_url

        m3u8 = os.path.join(config.get_data_path(), "blenditall.m3u8")

        if hls_data:
            try:
               from lib import serverhls

               outfile = open(m3u8, 'wb')
               outfile.write(codecs.encode(hls_data, "utf-8"))
               outfile.close()

               serverhls.start(base_url)

               video_urls.append(['m3u8', m3u8])
            except:
                pass

            try:
               from lib.m3u8server import Client

               c = Client(url=url, is_playing_fnc=platformtools.is_playing)
               f = c.get_file()
               if f: video_urls.append(['m3u8', f])
            except:
              pass

    return video_urls
