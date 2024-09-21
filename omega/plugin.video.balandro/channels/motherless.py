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
from core import httptools, scrapertools


host = 'https://motherless.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    if '<title>Just a moment...</title>' in data:
        if not '/search/' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host  + 'videos/recent' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host  + 'videos/viewed' ))
    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host  + 'videos/popular' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host  + 'videos/commented' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if PY3 and isinstance(data, bytes): data = data.decode('utf-8')

    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|\\", "", data)

    data = scrapertools.find_single_match(data, '<div class="menu-categories-tab"(.*?)<div class="menu-categories-tab"')

    matches = re.compile('<a href="([^"]+)" class="[^"]+">([^<]+)<', re.DOTALL).findall(data)

    for url, title in matches:
        title = title.strip()
        url = urlparse.urljoin(item.url, url)

        itemlist.append(item.clone (action='list_all', title=title, url=url, text_color = 'tan' ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if PY3 and isinstance(data, bytes): data = data.decode('utf-8')

    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    patron = '<div class="thumb.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<span class="size">([^<]+)<.*?'
    patron += 'src="([^"]+.jpg)".*?'
    patron += 'alt="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, time, thumb, title, in matches:
        url = url.replace('..', '')

        url = urlparse.urljoin(item.url, url)

        thumb += '|verifypeer=false'

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" class="pop" rel="next"')

        if next_page:
            next_page = urlparse.urljoin(item.url, next_page)

            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if PY3 and isinstance(data, bytes): data = data.decode('utf-8')

    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    url = scrapertools.find_single_match(data, 'fileurl = \'([^,\']+)\'')

    if url:
        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server = 'directo', language = 'Vo') )

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'search/videos?term=%s&size=0&range=0&sort=date' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
