# Conector tiwikiwi By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data, server
    response = httptools.downloadpage(page_url)
    data = response.data
    server = scrapertools.get_domain_from_url(page_url).split(".")[-2]

    if response.code == 404:
        return False,  "[%s] El fichero no existe o ha sido borrado" %server
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    # enc_data = scrapertools.find_single_match(data, "type='text/javascript'>(eval.*?)?\s+</script>")
    enc_data = scrapertools.find_multiple_matches(data, "type='text/javascript'>(eval.*?)?\s+</script>")
    dec_data = jsunpack.unpack(enc_data[-1])
    # sources = 'file:"([^"]+)",label:"([^"]+)"'
    sources = 'sources\:\[\{(?:file|src):"([^"]+)"'
    matches = re.compile(sources, re.DOTALL).findall(dec_data)
    for url in matches:
        video_urls.append(['[%s] m3u' %server , url])
    return video_urls
