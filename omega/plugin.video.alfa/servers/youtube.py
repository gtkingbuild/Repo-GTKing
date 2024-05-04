# s-*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urlparse
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido
    import urlparse

import re

from core import httptools
from core import jsontools as json
from core import scrapertools
from platformcode import config, logger
if not PY3:
    from lib import alfaresolver
else:
    from lib import alfaresolver_py3 as alfaresolver
itag_list = {1: "video",
             5: "flv 240p",
             6: "flv 270p",
             17: "3gp 144p",
             18: "mp4 360p",
             22: "mp4 720p",
             34: "flv 360p",
             35: "flv 480p",
             36: "3gp 180p",
             37: "mp4 1080p",
             38: "mp4 3072p",
             43: "webm 360p",
             44: "webm 480p",
             45: "webm 720p",
             46: "webm 1080p",
             82: "mp4 360p 3D",
             83: "mp4 480p 3D",
             84: "mp4 720p 3D",
             85: "mp4 1080p 3D",
             92: "hls 240p 3D",
             93: "hls 360p 3D",
             94: "hls 480p 3D",
             95: "hls 720p 3D",
             96: "hls 1080p",
             100: "webm 360p 3D",
             101: "webm 480p 3D",
             102: "webm 720p 3D",
             132: "hls 240p",
             133: "mp4 240p",
             134: "mp4 360p",
             135: "mp4 480p",
             136: "mp4 720p",
             137: "mp4 1080p",
             138: "mp4 2160p",
             160: "mp4 144p",
             167: "webm 360p",
             168: "webm 480p",
             169: "webm 1080p",
             219: "webm 144p",
             242: "webm 240p",
             243: "webm 360p",
             244: "webm 480p",
             245: "webm 480p",
             246: "webm 480p",
             247: "webm 720p",
             248: "webm 1080p",
             266: "mp4 2160p",
             271: "webm 1440p",
             272: "webm 4320p",
             278: "webm 144p",
             298: "mp4 720p",
             299: "mp4 1080p",
             302: "webm 720p",
             303: "webm 1080p",
             308: "webm 1440p",
             313: "webm 2160p",
             315: "webm 2160p",
             330: "webm 144p hdr",
             331: "webm 240p hdr",
             332: "webm 360p hdr",
             333: "webm 480p hdr",
             334: "webm 720p hdr",
             335: "webm 1080p hdr",
             336: "webm 1440p hdr",
             337: "webm 2160p hdr"}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    set_cookie()

    data = httptools.downloadpage(page_url).data

    if "File was deleted" in data or 'El vídeo no está disponible' in data or "privado" in data or "derechos de autor" in data:
        return False, config.get_localized_string(70449) % "Youtube"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    vid = list()
    if not page_url.startswith("http"):
        page_url = "https://www.youtube.com/watch?v=%s" % page_url
        logger.info(" page_url->'%s'" % page_url)

    return alfaresolver.gvd_check(page_url)


def set_cookie():
    dict_cookie = {'domain': '.youtube.com',
                    'name': 'c_locale',
                    'value': '0',
                    'expires': 1}
    
    httptools.set_cookies(dict_cookie, clear=True)
