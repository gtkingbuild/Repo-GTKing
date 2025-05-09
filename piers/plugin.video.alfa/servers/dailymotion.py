# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger



def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global response

    response = httptools.downloadpage(page_url)
    logger.error(response.json)
    if response.json.get("error", ""):
        return False, "[Dailymotion] El archivo no existe o ha sido borrado"
    if response.code == 404:
        return False, "[Dailymotion] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    subtitle = ""
    data = response.json
    #logger.error(data['subtitles'])
    sub_data = data['subtitles'].get('data', '')

    try:

        sub_es = sub_data.get('es') or sub_data.get('en')
        subtitle = sub_es.get('urls', [])[0]
    except:
        pass
    # for s in sub_data:
    #     surl = sub_data[s].get('urls', [])[0]
    #     subtitle.append(surl)
    #subtitle = scrapertools.find_single_match(data, '"subtitles":.*?"es":.*?urls":\["([^"]+)"')
    #qualities = scrapertools.find_multiple_matches(data, '"([^"]+)":(\[\{"type":".*?\}\])')
    stream_url = data['qualities']['auto'][0]['url']

    #logger.error(stream_url)
    data_m3u8 = httptools.downloadpage(stream_url).data.decode('utf-8')

    patron = 'NAME="([^"]+)",PROGRESSIVE-URI="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data_m3u8, patron)

    for calidad, url in matches:
        calidad = calidad.replace("@60","")
        url = httptools.get_url_headers(url, forced=True, dom='dailymotion.com')
        video_urls.append(["%sp .mp4 [dailymotion]" % calidad, url, 0, subtitle])
    return video_urls
