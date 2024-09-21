# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

if PY3:
    import urllib.parse as urlparse
else:
    import urlparse


import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools


host = 'https://www.xvideos.com/'


perpage = 30


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_xxx', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Los mejores', action = 'list_best', url = host + 'best/' ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host + 'channels-index/from/worldwide/top' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars-index/from/worldwide/ever' ))
    itemlist.append(item.clone( title = 'Por modelo', action = 'modelos', url = host + 'erotic-models-index/from/worldwide/ever' ))
    itemlist.append(item.clone( title = 'Por webcam', action = 'webcams', url = host + 'webcam-models-index/from/worldwide/ever' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div id="profile.*?<a href="(.*?)".*?<img src="(.*?)".*?<span class="profile-name">(.*?)</span>').findall(data)

    for url, thumb, title in matches:
        if '</strong>' in title: title = scrapertools.find_single_match(title, '</strong>(.*?)$')

        title = title.replace('&nbsp', '').replace('&ntilde;', 'ñ').strip()

        url += '/videos/new/0'

        itemlist.append(item.clone( action = 'list_canales', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb, text_color = 'orange' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="active".*?</a>.*?<a href="(.*?)"')

        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_page if next_page.startswith('http') else host[:-1] + next_page, action = 'canales', text_color = 'coral' ))

    return itemlist


def list_canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    jdata = jsontools.load(data)

    for vid in jdata["videos"]:
        url = vid["u"]
        title = vid["tf"]
        time = vid["d"]
        thumbnail =  vid["i"]

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        thumb = thumbnail.replace("\/", "/")

        url = scrapertools.find_single_match(url, '/(\d+/[A-z0-9_-]+)')
        url = "/video%s" % url
        url = urlparse.urljoin(item.url,url)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb ))

    if itemlist:
        nb_videos = jdata['nb_videos']
        nb_per_page = jdata['nb_per_page']
        current_page = jdata['current_page']

        current_page += 1

        if nb_videos > (nb_per_page * current_page):
            next_page = current_page
            next_page = re.sub(r"/new/\d+", "/new/{0}".format(next_page), item.url)

            if next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_canales', text_color = 'coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    perpage = 250

    data = do_downloadpage(host + 'tags')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li><a href="(/tags/[^"]+)"><b>([^<]+)').findall(data)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for url, title in matches[desde:hasta]:
        titulo = title.capitalize()

        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = titulo, text_color = 'tan' ))

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'categorias', text_color='coral' ))

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div id="profile.*?<img src="(.*?)".*?<a href="(.*?)">(.*?)</a>').findall(data)

    for thumb, url, title in matches:
        title = title.replace('&ntilde;', 'ñ')

        url += '/videos/new/0'

        itemlist.append(item.clone( action = 'list_stars', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb, text_color = 'moccasin' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="active".*?</a>.*?<a href="(.*?)"')

        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_page if next_page.startswith('http') else host[:-1] + next_page, action = 'pornstars', text_color = 'coral' ))

    return itemlist


def list_stars(item):
    logger.info()
    itemlist = []

    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    jdata = jsontools.load(data)

    for vid in jdata["videos"]:
        url = vid["u"]
        title = vid["tf"]
        time = vid["d"]
        thumb =  vid["i"]

        title = title.replace('&ntilde;', 'ñ')

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        thumb = thumb.replace("\/", "/")

        url = scrapertools.find_single_match(url, '/(\d+/[A-z0-9_-]+)')
        url = "/video%s" % url
        url = urlparse.urljoin(item.url,url)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb ))

    if itemlist:
        nb_videos = jdata['nb_videos']
        nb_per_page = jdata['nb_per_page']
        current_page = jdata['current_page']

        current_page += 1

        if nb_videos > (nb_per_page * current_page):
            next_page = current_page
            next_page = re.sub(r"/new/\d+", "/new/{0}".format(next_page), item.url)

            if next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_stars', text_color = 'coral' ))

    return itemlist


def modelos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div id="profile.*?<img src="(.*?)".*?<a href="(.*?)">(.*?)</a>').findall(data)

    for thumb, url, title in matches:
        title = title.replace('&ntilde;', 'ñ')

        url += '/videos/new/0'

        itemlist.append(item.clone( action = 'list_models', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb, text_color = 'moccasin' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="active".*?</a>.*?<a href="(.*?)"')

        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_page if next_page.startswith('http') else host[:-1] + next_page, action = 'modelos', text_color = 'coral' ))

    return itemlist


def list_models(item):
    logger.info()
    itemlist = []

    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    jdata = jsontools.load(data)

    for vid in jdata["videos"]:
        url = vid["u"]
        title = vid["tf"]
        time = vid["d"]
        thumb =  vid["i"]

        title = title.replace('&ntilde;', 'ñ')

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        thumb = thumb.replace("\/", "/")

        url = scrapertools.find_single_match(url, '/(\d+/[A-z0-9_-]+)')
        url = "/video%s" % url
        url = urlparse.urljoin(item.url,url)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb ))

    if itemlist:
        nb_videos = jdata['nb_videos']
        nb_per_page = jdata['nb_per_page']
        current_page = jdata['current_page']

        current_page += 1

        if nb_videos > (nb_per_page * current_page):
            next_page = current_page
            next_page = re.sub(r"/new/\d+", "/new/{0}".format(next_page), item.url)

            if next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_models', text_color = 'coral' ))

    return itemlist


def webcams(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div id="profile.*?<img src="(.*?)".*?<a href="(.*?)">(.*?)</a>').findall(data)

    for thumb, url, title in matches:
        title = title.replace('&ntilde;', 'ñ')

        url += '/videos/new/0'

        itemlist.append(item.clone( action = 'list_webcams', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb, text_color = 'moccasin' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="active".*?</a>.*?<a href="(.*?)"')

        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_page if next_page.startswith('http') else host[:-1] + next_page, action = 'webcams', text_color = 'coral' ))

    return itemlist


def list_webcams(item):
    logger.info()
    itemlist = []

    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    jdata = jsontools.load(data)

    for vid in jdata["videos"]:
        url = vid["u"]
        title = vid["tf"]
        time = vid["d"]
        thumb =  vid["i"]

        title = title.replace('&ntilde;', 'ñ')

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        thumb = thumb.replace("\/", "/")

        url = scrapertools.find_single_match(url, '/(\d+/[A-z0-9_-]+)')
        url = "/video%s" % url
        url = urlparse.urljoin(item.url,url)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb ))

    if itemlist:
        nb_videos = jdata['nb_videos']
        nb_per_page = jdata['nb_per_page']
        current_page = jdata['current_page']

        current_page += 1

        if nb_videos > (nb_per_page * current_page):
            next_page = current_page
            next_page = re.sub(r"/new/\d+", "/new/{0}".format(next_page), item.url)

            if next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_webcams', text_color = 'coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    external = scrapertools.find_single_match(data, '<a class="external-link" href="(.*?)"')

    matches = re.compile('<div class="thumb"><a href="([^"]+)".*?data-src="([^"]+)".*?title="([^"]+)"').findall(data)

    ses = 0

    for url, thumb, title in matches:
        ses += 1

        if title == 'Modelo verificada':
            title = scrapertools.find_single_match(url, '/video.*?/(.*?)$')
            title = title.replace('_', ' ').strip()
            title = title.capitalize()

        title = title.replace('&aacute;', 'a').replace('&eacute;', 'e').replace('&iacute;', 'e').replace('&oacute;', 'o').replace('&uacute;', 'u')

        title = title.replace('&aacuate;', 'a').replace('&eacuate;', 'e').replace('&iacuate;', 'e').replace('&oacuate;', 'o').replace('&uacuate;', 'u')

        title = title.replace("&#039;", "'").replace('&quot;', '').replace('&iexcl;', '').replace('&ndash;', '').replace('&ntilde;', 'ñ').replace("&rsquo;", "'")

        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" class="no-page next-page">')

        if next_page:
            if not next_page == '#1':
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page if next_page.startswith('http') else host[:-1] + next_page, action = 'list_all', text_color = 'coral' ))

    if not itemlist:
        if ses == 0:
            if external:
                if not host in external:
                    platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Enlace externo al canal No Admitido[/B][/COLOR]')
                    return

    return itemlist


def list_best(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div id="date-links-pagination" class="ordered-label-list">(.*?)<li class="hidden">')

    matches = re.compile('<li>(.*?)</li>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '">(.*?)</a>')

        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = title ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    try:
       m3u8url = re.findall(r"html5player\.setVideoHLS\('([^']+)'", data)[0]
    except:
       return itemlist

    data = do_downloadpage(m3u8url)

    matches = re.compile('(?i)name="([^"]+)"\s*(.*?m3u8)').findall(data)

    for calidad, url in matches:
        if not calidad or not url: continue

        url = m3u8url.replace("hls.m3u8", url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = calidad, url = url, language = 'Vo' ))

    return sorted(itemlist, key=lambda i: i.quality)


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "?k=%s" % (texto.replace(" ", "%20"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
