# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector evoload By Alfa development Group
# --------------------------------------------------------

from builtins import range
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from core import httptools
from core import scrapertools
from platformcode import logger
from lib import generictools

def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url, add_referer=True)
    if not data.sucess:
        return False, "[evoload] El fichero no existe o ha sido borrado"
    data = data.data
    return True, ""

def get_video_url(page_url, premium=False, user="", password="", video_password=""):

    video_urls = list()
    key = scrapertools.find_single_match(data, 'render=([^"]+)"')
    co = "aHR0cHM6Ly9ldm9sb2FkLmlvOjQ0Mw"
    loc = "https://evoload.io"
    tk = generictools.rec(key, co, "", loc)
    player_url = "https://evoload.io/SecurePlayer"
    code = scrapertools.find_single_match(page_url, "/e/([A-z0-9]+)")
    post = {"code": code, "token": tk}
    v_data = httptools.downloadpage(player_url, headers={"User-Agent": httptools.get_user_agent(), "Referer": page_url}, post=post).json
    if "stream" in v_data:
        if "backup" in v_data["stream"]:
            media_url = v_data["stream"]["backup"]
        else:
            media_url = v_data["stream"]["src"]
        ext = v_data["name"][-4:]
        video_urls.append(['%s [evoload]' % ext, media_url])
    else:
        pass
    return video_urls
