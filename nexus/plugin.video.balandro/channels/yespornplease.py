# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://yespornpleasexxx.com/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    timeout = None
    if host in url: timeout = config.get_setting('channels_repeat', default=30)

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    if not data:
        if url.startswith(host):
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('YesPornPlease', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

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

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host + 'tags/' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars/' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'Categories<p>(.*?)Friends<p>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url, text_color = 'orange' ))

    if itemlist:
        itemlist.append(item.clone (action='list_all', title= 'BangBros', url = host + '/bangbros/', text_color = 'orange' ))
        itemlist.append(item.clone (action='list_all', title= 'Brazzers', url = host + '/brazzers/', text_color = 'orange' ))
        itemlist.append(item.clone (action='list_all', title= 'Reality Kings', url = host + '/reality-kings/', text_color = 'orange' ))

    return sorted(itemlist, key=lambda x: x.title)


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="box">.*?<a href="(.*?)".*?src="(.*?)".*?">(.*?)</a>', re.DOTALL).findall(data)

    for url, thumb, title in matches:
        if title == 'All Videos': continue

        title = title.replace('</figcaption>', '').strip()

        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color = 'tan' ))

    return sorted(itemlist, key=lambda x: x.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="box">.*?<a href="(.*?)".*?src="(.*?)".*?">(.*?)</a>', re.DOTALL).findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='moccasin' ))

    matches2 = re.compile('<figure class="gallery-item">.*?src="(.*?)".*?alt="(.*?)".*?<a href="(.*?)"', re.DOTALL).findall(data)

    for thumb, title, url in matches2:
        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='moccasin' ))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="post-preview-styling">.*?<a href="(.*?)".*?title="(.*?)".*?data-src="(.*?)".*?<p>(.*?)</p>', re.DOTALL).findall(data)

    for url, title, thumb, time in matches:
        title = title.replace('&#8217;', '').replace('&#8211;', '&').replace('&#038;', '&')

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<link rel="next" href="(.*?)"')

        if next_page:
            if'/page/' in next_page:
               itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<iframe.*?-src="(.*?)"', re.DOTALL).findall(data)

    for link in matches:
        if host in link:
            data2 = do_downloadpage(link)

            url = scrapertools.find_single_match(data2, '<source type="video/mp4".*?src="(.*?)"')

            if url:
                url += '|Referer=%s' % item.url

                itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, language = 'Vo' ))

        servidor = servertools.get_server_from_url(link)
        servidor = servertools.corregir_servidor(servidor)

        link = servertools.normalize_url(servidor, link)

        if not 'http' in link: link = 'https:' + link

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link, language = 'Vo' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + '?s=%s' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
