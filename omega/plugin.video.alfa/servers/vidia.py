# -*- coding: utf-8 -*-
# -*- Server Vidia -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from core import httptools
from core import scrapertools
from platformcode import logger
from lib import jsunpack
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data

    if "File Not Found" in data or "File is no longer available" in data:
        return False, "[Vidia] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    packed = scrapertools.find_single_match(data, r"'text/javascript'>(eval.*?)\n")
    unpacked = jsunpack.unpack(packed)
    video_urls = []
    videos = scrapertools.find_multiple_matches(unpacked, r'file:"([^"]+)"')
    subtitulo = scrapertools.find_single_match(unpacked, r'tracks:\s*\[{file:"(.*?)"')

    for video_url in videos:
        extension = scrapertools.get_filename_from_url(video_url)[-4:]
        if extension not in [".vtt", ".srt"]:
            video_url += '|verifypeer=false'
            if extension == ".mpd":
                continue
                #video_urls.append(["[vidia] %s" % extension, video_url, 0, subtitulo, "mpd"])
            else:
                video_urls.append(["[vidia] %s" % extension, video_url, 0, subtitulo])

    return video_urls
