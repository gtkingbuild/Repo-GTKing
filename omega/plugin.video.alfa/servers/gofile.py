# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector GoFile By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    status = data.sucess
    if status == False:
        return False, "[GoFile] El video ha sido borrado"
    elif not status:
        return False, "[GoFile] Error al acceder al video"
    data = data.data
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    c_id = scrapertools.find_single_match(page_url, "/d/([^$]+)")
    api_url = "https://api.gofile.io/createAccount"
    api_data = httptools.downloadpage(api_url).json

    if "status" in api_data and api_data["status"] == "ok":
        tk = api_data["data"]["token"]
    else:
        return video_urls

    c_url = "https://api.gofile.io/getContent?contentId=%s&token=%s" % (c_id, tk)
    c_data = httptools.downloadpage(c_url).json
    c_info = c_data["data"]["contents"]

    for k, v in c_info.items():
        subtitle = ""
        video_urls.append([v["mimetype"].replace("video/", "") + " [GoFile]", v["link"], 0, subtitle])

    return video_urls
