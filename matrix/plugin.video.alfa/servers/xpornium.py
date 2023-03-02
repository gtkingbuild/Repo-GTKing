# Conector xpornium By Alfa development Group
# --------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re
from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if data.code == 404:
        return False, "[xpornium] El archivo no existe o  ha sido borrado"
    return True, ""

# XPSYS('Ly9kbC1hLTEueHAtY2RuLm5ldC92aWRlby9iZjgxNmVlZDQwYWM5NjI2NjZjYzAwMDZmMzBlYzk4Zi9Mb1JRdXp4X0FOTmIwMy1SQ1BxWUdRLzE2NzI4NTQ4ODE=')

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data, "XPSYS\('([^']+)'")
    import base64
    url = base64.b64decode(url).decode('utf-8')
    url = urlparse.unquote(url)
    if not url.startswith("https"):
        url = "https:%s" % url
    video_urls.append(['[xpornium] mp4' , url])
    return video_urls
