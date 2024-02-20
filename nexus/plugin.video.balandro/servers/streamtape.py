# -*- coding: utf-8 -*-

import time

from platformcode import config, logger, platformtools
from core import httptools, scrapertools


espera = config.get_setting('servers_waiting', default=6)


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    page_url = page_url.replace('/e/e/', '/e/').replace('/v/v/', '/e/').replace('/e/v/', '/e/').replace('/v/e/', '/e/').replace('/v/', '/e/').strip()
    if page_url.endswith('?') == True: page_url = page_url.replace('?', '')

    video_urls = get_aux(page_url)

    if len(video_urls) == 0:
        page_url = page_url.replace('/e/', '/v/').strip()
        video_urls = get_aux(page_url)

    return video_urls

def get_aux(page_url):
    video_urls = []

    referer = {}

    data = httptools.downloadpage(page_url, headers=referer).data

    if "Video not found" in data:
        return  "Archivo inexistente ó eliminado"

    url_data = scrapertools.find_single_match(data, """getElementById\('\w+link'\).innerHTML = "[^"]+" .* \('.+?/([^']+)'\)""")

    if not url_data:
        platformtools.dialog_notification('Cargando [COLOR cyan][B]Streamtape[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
        time.sleep(int(espera))

        data = httptools.downloadpage(page_url, headers={"Referer": page_url}).data

        url_data = scrapertools.find_single_match(data, """getElementById\('\w+link'\).innerHTML = "[^"]+" .* \('.+?/([^']+)'\)""")

    if url_data:
        url = "https://adblockstrtech.link/" + url_data + "&stream=1" + "|User-Agent=" + httptools.get_user_agent()

        video_urls.append(['mp4', url])

    return video_urls

