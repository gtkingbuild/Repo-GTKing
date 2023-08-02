# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack

# Funciona para descargar el vídeo pero falla en ocasiones al reproducir


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    resp = httptools.downloadpage(page_url)

    if not resp.sucess or "Not Found" in resp.data or "File was deleted" in resp.data or "is no longer available" in resp.data:
        return 'El fichero no existe o ha sido borrado'

    unpacked = ""
    data = resp.data

    packed = scrapertools.find_single_match(data, "function\(p,a,c,k.*?</script>")
    if packed:
        unpacked = jsunpack.unpack(packed)

    media_url = scrapertools.find_single_match(unpacked, 'src"value="([^"]+)')
    if not media_url:
        id_ = page_url.rsplit("/", 1)[1]
        rand = scrapertools.find_single_match(data, 'name="rand" value="([^"]+)"')
        post = "op=download2&id=%s&rand=%s&referer=%s&method_free=&method_premium=" % (id_, rand, page_url)
        data = httptools.downloadpage(page_url, post).data

        media_url = scrapertools.find_single_match(data, '<div id="dl_link".*?<a href="([^"]+)"')
        if not media_url: media_url = scrapertools.find_single_match(data, '<a href="([^"]+\.mp4)"')
        if not media_url: media_url = scrapertools.find_single_match(data, '<a href="([^"]+\.m3u8)"')

    if not media_url: return []

    ext = scrapertools.get_filename_from_url(media_url)[-4:]
    video_urls.append([ext, media_url])

    return video_urls
