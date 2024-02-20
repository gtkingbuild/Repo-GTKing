# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import os
import codecs

from lib import serverhls

from core import httptools, scrapertools
from platformcode import logger, config


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    ref = page_url.split('//', 1)

    resp = httptools.downloadpage(page_url, headers={"referer": ref[0] + "//" + ref[1]})

    if resp.code == 404:
        return "Archivo inexistente ó eliminado"

    data = resp.data

    if PY3 and isinstance(data, bytes):
        data = "".join(chr(x) for x in bytes(data))

    v_type = "hls"

    url = page_url

    video_urls = list()

    if "const source = '" in data:
        url = scrapertools.find_single_match(data, "const source = '([^']+)")
        v_type = "hls"

    if '"file": ' in data:
        url, v_type = scrapertools.find_single_match(data, '"file": "([^"]+)",\s+"type": "([^"]+)"')

    headers = {"referer": page_url}

    if v_type == "mp4":
        url = httptools.downloadpage(url, headers=headers, follow_redirects=False).headers["location"]

        page_url = "%s|Referer=%s&User-Agent=%s" % (url, page_url, httptools.get_user_agent())

    elif v_type == "hls":
        if '.hls' in data: hls_data = data
        else:
            hls_data = httptools.downloadpage(url, headers=headers).data

            if PY3 and isinstance(hls_data, bytes):
                hls_data = "".join(chr(x) for x in bytes(hls_data))

        base_url = scrapertools.find_single_match(hls_data, "((?:https?:)?\/\/[^\/]+)")
        if base_url: hls_data = hls_data.replace(base_url, 'http://localhost:8781')

        if not base_url.startswith('http'): base_url = 'https:%s' % base_url

        m3u8 = os.path.join(config.get_data_path(), "m3u8hls.m3u8")

        outfile = open(m3u8, 'wb')
        outfile.write(codecs.encode(hls_data, "utf-8"))
        outfile.close()

        page_url = m3u8
        v_type = "m3u8"

        serverhls.start(base_url)
    else:
        return video_urls

    video_urls = [["%s" % v_type, page_url]]

    return video_urls
