# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger, platformtools
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    if 'embed-' not in page_url:
        page_url = page_url.replace('upstream.to/', 'upstream.to/embed-') + '.html'

    data = httptools.downloadpage(page_url).data

    if '"title">File Not Found</div>' in data or 'player_blank.jpg' in data or 'assets/images/image-404.png' in data:
        return  "Archivo inexistente ó eliminado"
    elif '_msg">File was locked by administrator</div>' in data:
        return  "El archivo está bloqueado"
    elif 'DDoS protection by DDos-Guard' in data:
        return  "DDos-Guard protection"

    if 'sources:' not in data:
        packed = scrapertools.find_single_match(data, "eval\((function\(p,a,c,k,e,d.*?)\)\s*</script>")
        if not packed: return video_urls

        data = jsunpack.unpack(packed)

    bloque = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')

    matches = scrapertools.find_multiple_matches(bloque, '\{file:"([^"]+)"([^}]*)')

    for url, extra in matches:
        lbl = scrapertools.find_single_match(extra, 'label:"([^"]+)')
        if not lbl: lbl = url[-4:]

        if lbl == '.srt' or lbl == '.jpg': continue

        if lbl == '.mpd':
            if platformtools.is_mpd_enabled():
                video_urls.append([lbl, url + '|Referer=https://upstream.to/', 0, '', True])
        else:
            if not 'http' in url: url = 'https://upstream.to' + url
            video_urls.append([lbl, url + '|Referer=https://upstream.to/'])

    if len(video_urls) == 0:
        url = scrapertools.find_single_match(bloque, '"(http.*?)"')

        if url and 'm3u8' in url:
            data = httptools.downloadpage(url, headers={'Referer': page_url}).data

            matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+).*?(http.*?\.m3u8)')

            if matches:
                for res, url in matches:
                    if '/iframes' in url: continue

                    video_urls.append([res + 'p', url])

        elif url and 'mp4' in url:
            video_urls.append(['mp4', url])

    return video_urls
