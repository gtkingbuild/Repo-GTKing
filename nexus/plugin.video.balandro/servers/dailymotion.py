# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    if not '/player/' in page_url:
        page_url = page_url.replace('dailymotion.com/embed/video/', 'dailymotion.com/player/metadata/video/')

    resp = httptools.downloadpage(page_url)

    data = jsontools.load(resp.data)

    try:
        sub_data = data['subtitles'].get('data', '')
    except:
        return video_urls

    subtitle = ''

    try:
        sub_es = sub_data.get('es') or sub_data.get('en')
        subtitle = sub_es.get('urls', [])[0]
    except:
        pass

    stream_url = data['qualities']['auto'][0]['url']

    data_m3u8 = httptools.downloadpage(stream_url).data

    matches = scrapertools.find_multiple_matches(data_m3u8, 'NAME="([^"]+)",PROGRESSIVE-URI="([^"]+)"')

    for calidad, url in sorted(matches, key=lambda x: int(x[0])):
        calidad = calidad.replace('@60','')
        url = httptools.get_url_headers(url)
        video_urls.append(["%sp  mp4" % calidad, url, 0, subtitle])

    return video_urls
