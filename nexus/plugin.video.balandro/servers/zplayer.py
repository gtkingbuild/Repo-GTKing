# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    referer = page_url

    if '|' in page_url:
        referer = page_url.split('|')[1]
        page_url = page_url.split('|')[0]

    if '/download/' in page_url:
         page_url = page_url.replace('/download/', '/embed/')

    data = httptools.downloadpage(page_url, headers={"Referer": referer}).data

    if "File is no longer available" in data:
        return 'El fichero no existe o ha sido borrado'
    elif "Video link direct restricted" in data:
        return 'El fichero está restringido'

    if not 'v2.zplayer' in page_url:
        matches = scrapertools.find_multiple_matches(data, '"file": "([^"]+)",.*?"type": "([^"]+)"')

        for video_url, ext in matches:
            ref = scrapertools.find_single_match(video_url, '(.*?&)') + "shared=%s" % page_url
            headers = {"Referer":page_url}

            if "redirect"  in video_url: 
                url = httptools.downloadpage(video_url, headers=headers, follow_redirects=False, only_headers=True).headers.get("location", "")
                if not url: continue

                url += "|Referer=%s" % page_url
            else:
                url = video_url + "|Referer=%s" % ref

            video_urls.append([ext, url])
    else:
        packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
        if packed:
            unpacked = jsunpack.unpack(packed)
        else:
            unpacked = data

        matches = scrapertools.find_multiple_matches(unpacked, r'sources:\s*\[\{\s*file:"([^"]+)"')

        for video_url in matches:
            ext = video_url[-4:]
            video_url += "|Referer=https://v2.zplayer.live/"

            video_urls.append([ext, video_url])

    return video_urls
