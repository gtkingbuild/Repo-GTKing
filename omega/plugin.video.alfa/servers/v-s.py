# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector v-s By Alfa development Group
# --------------------------------------------------------
import re
from core import httptools, jsontools
from core import scrapertools
from platformcode import logger

video_urls = []


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data

    response = httptools.downloadpage(page_url)
    data = response.data
    if not response.sucess or '<div class="notification">' in data:
        return False, "[v-s] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    json_data = scrapertools.find_single_match(data, r'<script type="application/ld\+json">([^<]+)</script')
    json_data = jsontools.load(json_data)
    media_url = json_data["contentUrl"]
    qlty = "%sx%s" % (json_data["width"], json_data["height"])

    video_urls.append(["%s [v-s]" % qlty, media_url])

    return video_urls
