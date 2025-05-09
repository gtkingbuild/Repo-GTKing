# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://xxxdan.com/es/'


perpage = 50


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

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', search_video = 'adult', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host  + 'newest' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host  + 'straight/popular1' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host  + 'straight/trending' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host  + 'channel/hd' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host + 'channels' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)

    patron = '<a href="([^"]+)" rel="tag".*?'
    patron += 'title="([^"]+)".*?'
    patron += 'data-original="([^"]+)".*?'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, thumb in matches:
        title = title.replace('ánal', 'anal').replace('ánime', 'anime').replace('árabe', 'arabe')

        title = title.capitalize()

        url = url.replace('channel', 'channel30')

        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color = 'moccasin' ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    patron = '<li><figure>\s*<a href="([^"]+)".*?'
    patron += 'data-original="([^"]+)".*?'
    patron += '<time datetime="\w+">([^"]+)</time>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    num_matches = len(matches)

    for url, thumb, time in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(url, host + '.*?/(.*?).html')

        title = title.replace('-', ' ')

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

        if len(itemlist) >= perpage: break

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data,'<link rel="next".*?href="([^"]+)"')

            if next_page:
                itemlist.append(item.clone (action='list_all', title='Siguientes ...', url = next_page, page= 0, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    url = scrapertools.find_single_match(data, 'src:\'([^\']+)\'')

    if url:
        url = url.replace("https", "http")

        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server = 'directo', language = 'Vo') )

    return itemlist


def search(item, texto):
    logger.info()
    try:
        config.set_setting('search_last_video', texto)

        item.url = host + 'search?query=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
