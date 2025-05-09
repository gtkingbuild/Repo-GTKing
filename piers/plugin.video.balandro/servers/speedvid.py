# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import aadecode, jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('speedvid.net', 'speedvideo.net')

    data = httptools.downloadpage(page_url).data
    if data == 'File was deleted':
        return 'Archivo inexistente ó eliminado'

    js = scrapertools.find_single_match(data, "<script type='text/javascript'>\s*ﾟωﾟ(.*?)</script>")
    if js:
        decoded = aadecode.decode(js)

        # ~ url = 'http://speedvid.net' + scrapertools.find_single_match(decoded, "'([^']+)")
        url = 'http://speedvideo.net' + scrapertools.find_single_match(decoded, "'([^']+)")

        data = httptools.downloadpage(url).data

        packeds = scrapertools.find_multiple_matches(data, "<script type='text/javascript'>(eval.function.p,a,c,k,e,d..*?)</script>")
        for packed in packeds:
            unpacked = jsunpack.unpack(packed)

            url = scrapertools.find_single_match(unpacked, "http://[^\\\\]+/v\.mp4")
            if url != '': video_urls.append(['mp4', url])

    return video_urls
