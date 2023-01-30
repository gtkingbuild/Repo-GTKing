# -*- coding: utf-8 -*-
# -*- Server Myvi -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from core import httptools
from core import scrapertools
from platformcode import logger
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    #from future import standard_library
    #standard_library.install_aliases()
    import urllib.parse as urllib
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data

    if "Video not available" in data:
        return False, "[Myvi] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    enc_url = scrapertools.find_single_match(data, r'CreatePlayer\("v=([^\\]+)\\u0026')
    url = "https:" + urllib.unquote(enc_url)
    video_urls.append(['[myvi] video', url])

    return video_urls

