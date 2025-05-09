# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://pandamovies.org/'


def do_downloadpage(url, post=None, headers=None):
    raise_weberror = True
    if '/release-year/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host  + 'movies' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host  + 'most-viewed' ))

    itemlist.append(item.clone( title = 'Escenas', action = 'escenas', text_color = 'pink' ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars' ))

    itemlist.append(item.clone( title = 'Por año', action='anios' ))

    return itemlist


def escenas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Repertorio', action = 'list_all', url = host  + 'xxxscenes/movies' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host  + 'xxxscenes/#movie-featured' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host  + 'xxxscenes/#topview-today' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host  + 'xxxscenes/#top-rating' ))

    itemlist.append(item.clone( title = 'Por género', action = 'canales', url = host + 'xxxscenes/' ))
    itemlist.append(item.clone( title = 'Por estudio', action = 'categorias', url = host + 'xxxscenes/'))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Porn Studios<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        title = title.replace('&#038;', '&').replace('&#8217;s', "'s").replace('&#8217;', "'s").replace('&amp;', '&')

        itemlist.append(item.clone (action='list_all', title=title, url=url, text_color = 'violet' ))

    return sorted(itemlist,key=lambda x: x.title)


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Genres<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url, text_color = 'moccasin' ))

    return sorted(itemlist,key=lambda x: x.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Pornstars<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color='orange' ))
  
    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        url = host + 'release-year/' + str(x)

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = 'orange' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<div data-movie-id=(.*?)</div></div></div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2>(.*?)</h2>')

        if not url or not title: continue

        title = title.replace('&#038;', '&').replace('&#8217;s', "'s").replace('&#8217;', "'s").replace('&#8211;', '').replace('&amp;', '')

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        time = scrapertools.find_single_match(match, '<span class="mli-info1">(.*?)</span>').strip()
        time = time.replace('hrs.', 'h').strip()
        time = time.replace('mins.', 'm').strip()

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb,
                                    contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<div id='pagination'.*?<li class='active'>.*?href='(.*?)'")

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    ses = 0

    bloque1 = scrapertools.find_single_match(data, '<div id="pettabs">(.*?)</div></div></div>')

    matches1 = scrapertools.find_multiple_matches(bloque1, 'href="(.*?)"')

    # ~ Download
    bloque2 = scrapertools.find_single_match(data, '>Download<(.*?)</div></div></div>')

    matches2 = scrapertools.find_multiple_matches(bloque2, 'href="(.*?)"')

    matches = matches1 + matches2

    for url in matches:
        ses += 1

        if 'link=' in url: url = scrapertools.find_single_match(url, 'link=(.*?)$')

        if not url: continue

        if '/frdl.' in url: continue
        elif '/snowdayonline.' in url: continue
        elif '/freepopnews.' in url: continue
        elif '/filepv.' in url: continue
        elif '/vinovo.' in url: continue

        elif '/nitroflare.' in url: continue
        elif 'rapidgator.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server=servidor, language = 'Vo', other = other.capitalize()) )

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        config.set_setting('search_last_video', texto)

        item.url =  host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
