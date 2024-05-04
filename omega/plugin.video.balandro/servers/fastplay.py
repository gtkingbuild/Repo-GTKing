# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('fastplay.cc/', 'fastplay.to/')

    data = httptools.downloadpage(page_url).data

    if "Object not found" in data or "longer exists on our servers" in data:
        return 'Archivo inexistente ó eliminado'

    if "p,a,c,k,e,d" in data:
        data = jsunpack.unpack(data).replace("\\", "")

    videos = scrapertools.find_multiple_matches(data, 'file\s*:\s*"([^"]+)"\s*,\s*label\s*:\s*"([^"]+)')

    subtitulo = scrapertools.find_single_match(data, 'tracks\s*:\s*\[{file:"(.*?)"')
    if "http" not in subtitulo and subtitulo != '':
        subtitulo = "http://fastplay.to" + subtitulo

    if videos:
        for video_url, video_calidad in videos:
            extension = scrapertools.get_filename_from_url(video_url)[-4:]
            if extension not in [".vtt", ".srt"]:
                video_urls.append(["%s %s" % (extension, video_calidad), video_url, 0, subtitulo])

        try:
            video_urls.sort(key=lambda it: int(it[0].split("p ", 1)[0].rsplit(" ")[1]))
        except:
            pass

    return video_urls
