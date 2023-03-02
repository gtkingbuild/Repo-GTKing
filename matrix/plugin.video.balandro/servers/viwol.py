# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    v_id = scrapertools.find_single_match(page_url, "/e/([A-z0-9]+)")

    base_url = "https://app.viwol.com/api/files/"

    data = httptools.downloadpage("%s%s" % (base_url, v_id), post={}).data
    json_data = jsontools.load(data)

    if 'Video file not found' in data:
        return "El archivo no existe o ha sido borrado"

    for info in json_data["video"]["sources"]:
        video_urls.append(['mp4', info["file"]])

    return video_urls
