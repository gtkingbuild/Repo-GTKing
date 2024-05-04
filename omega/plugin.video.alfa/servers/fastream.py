# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Fastream By Alfa Development Group
# --------------------------------------------------------

from core import httptools, scrapertools
from platformcode import config, logger
from lib import jsunpack

from core.httptools import urlparse

kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
          # 'forced_proxy_ifnot_assistant': 'ProxyWeb:hide.me’|’ ProxyWeb:croxyproxy.com', 
          'cf_assistant': False}

data = ''

def test_video_exists(page_url):
    # if '|' in page_url:
        # page_url, referer = page_url.split("|", 1)

    # logger.info("(page_url='{}')".format(page_url))

    # if 'referer' in locals():
        # page_url += referer

    # url_components = urlparse.urlparse(page_url)
    # code = urlparse.parse_qsl(url_components.query)[0][0]

    # origin = "{}://{}".format(url_components.scheme, url_components.hostname)
    # post = {
        # "op": "embed",
        # "file_code": code,
        # "auto": "1",
        # "referer": "",
    # }

    # global data
    # data = httptools.downloadpage(
        # "{}/dl".format(origin),
        # post=post,
        # referer=page_url,
        # cookies=False,
        # **kwargs
    # ).data
    global data
    data = httptools.downloadpage(page_url, **kwargs).data
    if 'File is no longer available as it expired or has been deleted' in data:
        return False, (config.get_localized_string(70449) % "fastream")
    else:
        return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    # logger.info("url1={}".format(page_url))
    # if '|' in page_url:
        # page_url, referer = page_url.split("|", 1)
    global data

    packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
    unpacked = jsunpack.unpack(packed)
    data = scrapertools.find_single_match(unpacked, "(?is)sources.+?\[(.+?)\]")

    video_urls = []
    pattern = 'file:"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, pattern)
    for url in matches:
        if 'referer' in locals():
            url += "|Referer={}".format(referer)
        logger.info(url)
        video_urls.append(['.m3u8 [fastream]', url])
    return video_urls
