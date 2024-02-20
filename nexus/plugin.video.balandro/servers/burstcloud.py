# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

if PY3:
    import urllib.parse as urllib
else:
    import urllib


from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = urllib.unquote(page_url)

    resp = httptools.downloadpage(page_url)

    if resp.code == 404:
        return 'Archivo inexistente ó eliminado'

    data = resp.data

    base_url = "https://www.burstcloud.co/file/play-request/"
    fileId = scrapertools.find_single_match(data, 'data-file-id="([^"]+)"')

    if fileId:
        post = {"fileId": fileId}
        data = httptools.downloadpage(base_url, post=post, headers={"Referer": page_url}).data

        url = scrapertools.find_single_match(data, '"cdnUrl".*?"([^"]+)"')

        if url:
            url = httptools.downloadpage(url, headers={'Referer': 'https://www.burstcloud.co/'}, follow_redirects=False).headers.get('location', '')

            if url:
                url = url + '|referer=https://www.burstcloud.co/'

                video_urls.append(['mp4', url])

    return video_urls
