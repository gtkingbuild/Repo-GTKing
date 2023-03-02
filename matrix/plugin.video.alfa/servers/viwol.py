# -*- coding: utf-8 -*-
# -*- Server Viwol -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    global json_data
    logger.info("(page_url='%s')" % page_url)
    v_id = scrapertools.find_single_match(page_url, "/e/([A-z0-9]+)")
    base_url = "https://app.viwol.com/api/files/"
    data = httptools.downloadpage("%s%s" % (base_url, v_id), post={})
    json_data = data.json
    if data.code == 404:
        return False, "[Viwol] El archivo no existe o ha sido borrado"

    if not hasattr(json_data["video"], "sources"):
        return False, "[Viwol] El video no se está disponible"

    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):

    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    for info in json_data["video"]["sources"]:
        video_urls.append([" [Viwol]", info["file"]])
    return video_urls
