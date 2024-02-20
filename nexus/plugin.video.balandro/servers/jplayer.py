# -*- coding: utf-8 -*-

from core import httptools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if "no longer exists" in data:
        return "Archivo inexistente ó eliminado"
    elif "to copyright issues" in data:
        return "Violación por Derechos Copyright"

    post = {"r":"", "d":"www.jplayer.club"}
    data = httptools.downloadpage(page_url, post=post).data

    try:
       json = jsontools.load(data)["data"]

       for _url in json:
           url = _url["file"]
           label = _url["label"]

           video_urls.append([label, url])
    except:
       pass

    return video_urls
