# -*- coding: utf-8 -*-
# -*- Server BurstCloud -*-
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
    page_url = urllib.unquote(page_url)
    data = httptools.downloadpage(page_url)

    if data.code == 404:
        return False, "[burstcloud] El fichero no existe o ha sido borrado"
    data = data.data
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    base_url = "https://www.burstcloud.co/file/play-request/"
    fileId = scrapertools.find_single_match(data, 'data-file-id="([^"]+)"')
    post = {"fileId": fileId}
    v_data = httptools.downloadpage(base_url, post=post, headers={"referer": page_url}).json
    url = httptools.downloadpage(v_data["purchase"]["cdnUrl"]).url + "|referer=https://www.burstcloud.co/"
    video_urls.append(['[burstcloud] MP4', url])

    return video_urls

