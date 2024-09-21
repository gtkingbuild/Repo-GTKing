# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = 'https://www.serviporno.com/'


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
    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'mas-vistos/' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'mas-votados/' ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url= host + 'sitios/' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url= host + 'categorias/' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars/' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron = '<div class="wrap-box-escena.*?data-src="([^"]+)".*?<h4.*?<a href="([^"]+)">([^<]+)<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for thumb, url, title in matches:
         url = host[:-1] + url

         itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color = 'orange' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" class="btn-pagination">Siguiente')

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='canales', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron = '<div class="wrap-box-escena.*?data-src="([^"]+)".*?<h4.*?<a href="([^"]+)">([^<]+)<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for thumb, url, title in matches:
         if title == 'Árabes': title = 'Arabes'

         url = host[:-1] + url

         itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='tan' ))

    return sorted(itemlist,key=lambda x: x.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron = '<div class="box-chica">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'data-src="(.*?)".*?'
    patron += '<h4><a href="[^"]+">([^<]+)</a></h4>.*?'
    patron += '<a class="total-videos".*?>([^<]+)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title, videos in matches:
         url = host[:-1] + url

         titulo = '[COLOR moccasin]%s[/COLOR] (%s)' % (title, videos.replace('vídeos', '').strip())

         itemlist.append(item.clone (action='list_all', title=titulo, url=url, thumbnail=thumb ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" class="btn-pagination">Siguiente')

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='pornstars', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron  = '(?s)<div class="wrap-box-escena">.*?'
    patron += '<div class="box-escena">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'src="([^"]+.jpg)".*?'
    patron += '<h4><a href="[^"]+">([^<]+)</a></h4>.*?'
    patron += '<div class="duracion">([^"]+) min</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for url, thumb, title, duration, in matches:
        url = host[:-1] + url

        title = "[COLOR tan]%s[/COLOR] %s" % (duration, title)

        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" class="btn-pagination">Siguiente')

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    url = scrapertools.find_single_match(data, "sendCdnInfo.'([^']+)")

    if not url:
        url = scrapertools.find_single_match(data, '<meta itemprop="embedURL".*?content="(.*?)"')

        if url:
            data = do_downloadpage(url)

            url = scrapertools.find_single_match(data, '<source src="(.*?)"')

    url = url.replace("&amp;", "&")

    if url:
        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='directo', language = 'Vo') )

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'search/?q=%s' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
