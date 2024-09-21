# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://xmoviesforyou.net/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'page/1/?filter=latest' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'page/1/?filter=most-viewed' ))
    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'page/1/?filter=popular' ))
    itemlist.append(item.clone( title = 'Long Play', action = 'list_all', url = host + 'page/1/?filter=longest' ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url= host + 'categories/page/1/' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url= host + 'tags/' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'actors/page/1/' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)</main>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?">(.*?)</a>')

    for url, title in matches:
        title = title.capitalize()

        itemlist.append(item.clone (action='list_all', title=title, url=url, text_color='tan' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)</main>')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='orange' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li><a class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (action='canales', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)</main>')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='moccasin' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li><a class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (action='pornstars', title='Siguientes ...', url=next_page, text_color = 'coral') )


    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        title = title.replace('[', '').replace(']', '').replace('&#8217;', "'").strip()

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li><a class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = scrapertools.find_single_match(data, 'Mirror(.*?)</table>')

    matches = re.compile('href="(.*?)"', re.DOTALL).findall(bloque)

    ses = 0

    for url in matches:
        ses += 1

        if url == '#content': continue

        elif '/xmoviesforyou.net' in url: continue
        elif '/1fichier' in url: continue

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server = servidor, language = 'Vo', other = other) )

    # ~ Embeds
    matches = re.compile('<meta itemprop="embedURL".*?content="(.*?)"', re.DOTALL).findall(data)

    for url in matches:
        ses += 1

        if url == '#content': continue

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server = servidor, language = 'Vo') )

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'page/1/?s=%s&filter=latest' % texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
