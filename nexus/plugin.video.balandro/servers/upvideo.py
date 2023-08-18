# -*- coding: utf-8 -*-

import re, base64

from core import httptools, scrapertools
from platformcode import logger

from lib import hunterdecode

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    resp = httptools.downloadpage(page_url)

    if resp.code == 404:
        return "El archivo no existe o ha sido borrado"
    elif "We can't find the video" in resp.data:
        return "El archivo no existe o ha sido borrado"

    data = resp.data

    data_m = httptools.downloadpage("https://highload.to/assets/js/master.js").data
    dec_m = hunterdecode.decode(data_m)
    head_ch = scrapertools.find_single_match(data, '<head>(.*?)<\/head>')
    decoded_m = hunterdecode.decode(head_ch)

    var_res = scrapertools.find_single_match(dec_m, 'var\s*res\s*=\s*([^\.]+)')
    obf_link = scrapertools.find_single_match(decoded_m, '%s="([^"]+)"' % var_res)
    res = re.search('var\s*res\s*=\s*[^\.]+\.replace\(\"([^"]+)"\s*,\s*"(.*?)"', dec_m)
    res2 = re.search('var\s*res2\s*=\s*[^\.]+\.replace\(\"([^"]+)"\s*,\s*"(.*?)"', dec_m)
    obf_link = obf_link.replace(res.group(1), res.group(2)).replace(res2.group(1), res2.group(2))
    mp4 = base64.b64decode(obf_link).decode('utf-8')

    video_urls.append(["mp4", mp4])

    return video_urls
