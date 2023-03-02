# -*- coding: utf-8 -*-

import base64

from core import httptools, scrapertools
from platformcode import config, logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    video_id = scrapertools.find_single_match(page_url, '/([A-z0-9]+)\.html')

    url = 'https://www.flashx.tv/playvideo-%s.html?playvid' % video_id
    data = httptools.downloadpage(url, headers={'Referer': 'https://www.flashx.tv/embed-%s.html' % video_id}).data

    if 'Too many views' in data:
        return 'Vídeo no encontrado'
    elif 'NOT FOUND' in data or 'file was deleted or the link is expired' in data:
        return 'El archivo no existe o ha sido borrado'

    if 'normal.mp4' not in data:
        file_id = base64.b64encode(scrapertools.find_single_match(data, "'file_id', '([^']+)'"))

        httptools.downloadpage('https://www.flashx.to/counter.cgi?c2=%s&fx=%s' % (video_id, file_id))
        httptools.downloadpage('https://www.flashx.tv/flashx.php?ss=yes&f=fail&fxfx=6')
        data = httptools.downloadpage(url).data

    # ~ packeds = scrapertools.find_multiple_matches(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")
    # ~ for packed in packeds:
        # ~ unpacked = jsunpack.unpack(packed)
        # ~ logger.info(unpacked)

    matches = scrapertools.find_multiple_matches(data, "{src: '([^']+)'.*?,label: '([^']+)',res: ([\d]+)")
    for url, lbl, res in matches:
        video_urls.append(['%s %sp' % (lbl, res), url])

    return video_urls
