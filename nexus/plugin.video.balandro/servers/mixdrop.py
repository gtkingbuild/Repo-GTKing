# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    if not 'http' in page_url: return video_urls

    page_url = page_url.replace('mixdrop.to/', 'mixdrop.co/')
    page_url = page_url.replace('mixdrop.sx/', 'mixdrop.co/')
    page_url = page_url.replace('mixdrop.bz/', 'mixdrop.co/')
    page_url = page_url.replace('mixdrop.ch/', 'mixdrop.co/')
    page_url = page_url.replace('mixdrop.gl/', 'mixdrop.co/')
    page_url = page_url.replace('mixdrop.club/', 'mixdrop.co/')

    page_url = page_url.replace('mixdroop.to/', 'mixdrop.co/')
    page_url = page_url.replace('mixdroop.sx/', 'mixdrop.co/')
    page_url = page_url.replace('mixdroop.bz/', 'mixdrop.co/')
    page_url = page_url.replace('mixdroop.ch/', 'mixdrop.co/')
    page_url = page_url.replace('mixdroop.gl/', 'mixdrop.co/')
    page_url = page_url.replace('mixdroop.club/', 'mixdrop.co/')

    page_url = page_url.replace('mixdrp.co/', 'mixdrop.co/')
    page_url = page_url.replace('mixdrp.to/', 'mixdrop.co/')

    page_url = page_url.replace('mixdrop.co/f/', 'mixdrop.co/e/')
    page_url = page_url.replace('mixdrop.co/embed/', 'mixdrop.co/e/')

    headers = {'Referer': page_url.replace('mixdrop.co/e/', 'mixdrop.co/f/')}
    data = httptools.downloadpage(page_url, headers=headers).data

    if '>WE ARE SORRY</h2>' in data or '<title>404 Not Found</title>' in data:
        return 'El archivo no existe o ha sido borrado'

    url = scrapertools.find_single_match(data, 'window\.location\s*=\s*"([^"]+)')
    if url:
        if url.startswith('/e/'): url = 'https://mixdrop.co' + url
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
