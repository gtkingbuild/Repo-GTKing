# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector ArchiveOrg By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import jsontools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if data.code == 404:
        return False, "[ArchiveOrg] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    host = "https://archive.org/"
    video_urls = []
    data = httptools.downloadpage(page_url).data
    json = jsontools.load( scrapertools.find_single_match(data, """js-play8-playlist" type="hidden" value='([^']+)""") )
    # sobtitles
    subtitle = ""
    for subtitles in json[0]["tracks"]:
        if subtitles["kind"] == "subtitles":  subtitle = host + subtitles["file"]
    # sources
    for url in json[0]["sources"]:
        video_urls.append(['%s %s[ArchiveOrg]' %(url["label"], url["type"]), host + url["file"], 0, subtitle])
    video_urls.sort(key=lambda it: int(it[0].split("p ", 1)[0]))
    return video_urls
