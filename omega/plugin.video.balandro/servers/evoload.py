# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger, recaptchav2


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    resp = httptools.downloadpage(page_url, add_referer=True)

    if not resp.sucess:
        return 'Archivo inexistente ó eliminado'

    data = resp.data

    key = scrapertools.find_single_match(data, 'render=([^"]+)"')

    token = recaptchav2.rev2(key, 'aHR0cHM6Ly9ldm9sb2FkLmlvOjQ0Mw', '', 'https://evoload.io')

    code = scrapertools.find_single_match(page_url, "/e/([A-z0-9]+)")
    post = {'code': code, 'token': token}

    data = httptools.downloadpage('https://evoload.io/SecurePlayer', headers={'User-Agent': httptools.get_user_agent(), 'Referer': page_url}, post=post).data

    if 'encoded_src' in data:
        media_url = scrapertools.find_single_match(str(data), '"encoded_src".*?"(.*?)"')
        if media_url: video_urls.append(['mp4 ', media_url])
    else:
        v_data = jsontools.load(data)

        if "stream" in v_data:
            if "backup" in v_data["stream"]: media_url = v_data["stream"]["backup"]
            else: media_url = v_data["stream"]["src"]

            if media_url:
                ext = v_data["name"][-4:]
                video_urls.append(['%s ' % ext, media_url])

    return video_urls

