# Conector Cloudvideo By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if data.code == 404 or '<div id="television">' in data.data:
        return False, "[Cloud] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    patron = '<source src="([^"]+)" type="([^"]+)"'
    sub = scrapertools.find_single_match(data, '<track kind="captions" src="([^"]+)"')
    matches = scrapertools.find_single_match(data, patron)
    for url, v_type in matches:
        if 'mpegURL' in v_type:
            v_type = 'm3u8'
        video_urls.append(['cloudvideo [%s]' % v_type, url, 0, sub])
    if not matches:
        enc_data = scrapertools.find_single_match(data, "p,a,c,k,e.*?</script>")
        unpacker = jsunpack.unpack(enc_data)
        url = scrapertools.find_single_match(unpacker, 'src:"([^"]+)"')
        video_urls.append(['cloudvideo [m3u8]', url])

    return video_urls
