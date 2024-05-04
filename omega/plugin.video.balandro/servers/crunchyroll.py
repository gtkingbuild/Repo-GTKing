# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


headers = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': '*'}

IDIOMAS = ['deDE', 'ptBR', 'frFR', 'itIT', 'enUS', 'esES', 'esLA']


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url, headers=headers).data

    if 'showmedia-trailer-notice' in data:
        disp = scrapertools.find_single_match(data, '<a href="/freetrial".*?</span>.*?<span>\s*(.*?)</span>').strip()

        if disp: return 'Necesita cuenta gratuita'
        else: return 'Requiere cuenta premium'

    video_urls = []

    media_url = ''

    # idioma_sub = IDIOMAS[index_sub]
    idioma_sub = 'esES'

    data = scrapertools.find_single_match(data, r'"streams":(\[[^\]]+])')

    jdata = jsontools.load(data)

    for elem in jdata:
        formato = elem.get('format', '')

        if formato in ['vo_adaptive_hls', 'adaptive_hls']:
            lang = elem.get('hardsub_lang', '')
            audio_lang = elem.get('audio_lang', '')

            if lang == idioma_sub:
                media_url = elem.get('url', '')
                break

            if not lang and audio_lang != 'jaJP':
                media_url = elem.get('url', '')
                break

    if media_url:
        m3u_data = httptools.downloadpage(media_url, headers=headers).data
        m3u_data = m3u_data.decode('utf-8')

        matches = scrapertools.find_multiple_matches(m3u_data, 'TION=\d+x(\d+).*?\s(.*?)\s')

        filename = scrapertools.get_filename_from_url(media_url)[-4:]

        if matches:
            for quality, media_url in matches:
                video_urls.append(['%s  %sp' % (filename, quality), media_url])
        else:
            video_urls.append(['m3u8', media_url])

    return video_urls
