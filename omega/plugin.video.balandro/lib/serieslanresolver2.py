# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

if PY3:
    import urllib.parse as urllib
else:
    import urllib


import re

from lib.rJs import runJavascript

from platformcode import logger
from core import httptools, scrapertools, servertools


def deco_url(item_slr, item_ord_link):
    logger.info()

    url = ''

    if not item_slr or not item_ord_link: return url

    js = ''

    data = httptools.downloadpage(item_slr).data

    _sa = scrapertools.find_single_match(data, 'var _sa = (true|false);')
    _sl = scrapertools.find_single_match(data, 'var _sl = ([^;]+);')

    sl = eval(_sl)

    buttons = scrapertools.find_multiple_matches(data, '<button.*?class="selop" sl="([^"]+)">')

    ord_link = 0

    if not buttons: buttons = [0, 1, 2]

    for id in buttons:
        ord_link += 1

        if not ord_link == item_ord_link: continue

        new_url = golink(int(id), _sa, sl)

        data_new = httptools.downloadpage(new_url).data

        matches = scrapertools.find_multiple_matches(data_new, 'javascript">(.*?)</script>')

        for part in matches:
            js += part

        try: 
            matches = scrapertools.find_multiple_matches(data_new, '" id="(.*?)" val="(.*?)"')

            for zanga, val in matches:
                js = js.replace('var %s = document.getElementById("%s");' % (zanga, zanga), '')
                js = js.replace('%s.getAttribute("val")' % zanga, '"%s"' % val)
        except:
            pass

        js = re.sub('(document\[.*?)=', 'prem=', js)

        video = scrapertools.find_single_match(js, "sources: \[\{src:(.*?), type")

        js = re.sub(' videojs\((.*?)\);', video+";", js)

        result = runJavascript.runJs().runJsString(js, True)

        url = scrapertools.find_single_match(result, 'src="(.*?)"')

        if not url: url = result.strip()

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

    return url


def golink (num, sa, sl):
    b = [3, 10, 5, 22, 31]

    SVR = 'https://viteca.stream/' if sa == 'true' else 'https://serieslan.com'

    TT = "/" + urllib.quote_plus(sl[3].replace("/", "><")) if num == 0 else ""

    url_end = link(num,sl)

    return SVR + "el/" + sl[0] + "/" + sl[1] + "/" + str(num) + "/" + sl[2] + url_end + TT


def link(ida , sl):
    a = ida
    b = [3, 10, 5, 22, 31]
    c = 1
    d = ''
    e = sl[2]

    for i in range(len(b)):
      d = d + substr(e, b[i] + a, c)

    return d

def substr(st, a, b):
    return st[a:a+b]
