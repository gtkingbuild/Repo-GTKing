# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    if not 'http' in page_url: return video_urls

    headers = {'Referer': page_url.replace('mixdrop.ag/e/', 'mixdrop.ag/f/')}
    data = httptools.downloadpage(page_url, headers=headers).data

    if '>WE ARE SORRY</h2>' in data or '<title>404 Not Found</title>' in data:
        return 'Archivo inexistente ó eliminado'

    url = scrapertools.find_single_match(data, 'window\.location\s*=\s*"([^"]+)')
    if url:
        if url.startswith('/e/'): url = 'https://mixdrop.ag' + url
        data = httptools.downloadpage(url).data

    packed = scrapertools.find_multiple_matches(data, "(?s)eval(.*?)\s*</script>")

    for pack in packed:
        try: data = jsunpack.unpack(pack)
        except: data = ''

        if 'MDCore.' in data: break

    urls = scrapertools.find_multiple_matches(data, 'MDCore\.\w+="([^"]+)')

    for url in urls:
        if '/' not in url: continue
        elif url.endswith('.jpg'): continue

        if url.startswith('//'):
            video_urls.append(["mp4", 'https:' + url])
            break

    return video_urls
