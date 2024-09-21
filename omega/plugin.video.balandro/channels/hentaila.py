# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://www4.hentaila.com/'


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_xxx', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color='orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'directorio' ))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = host + 'directorio?filter=recent', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'directorio?filter=popular' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'directorio?status[1]=on' ))
    itemlist.append(item.clone( title = 'Finalizados', action = 'list_all', url = host + 'directorio?status[2]=on' ))

    itemlist.append(item.clone( title = 'Sin censura', action = 'list_all', url = host + 'directorio?uncensored=on' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'directorio').data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = scrapertools.find_single_match(data, '>Generos<(.*?)</section>')

    matches = re.compile('<li.*?<a href="(.*?)".*?class>(.*?)</a>', re.DOTALL).findall(bloque)

    for genre, title in matches:
        url = host[:-1] + genre

        itemlist.append(item.clone( action = 'list_all', url = url, title = title, text_color='orange' ))

    return sorted(itemlist, key=lambda i: i.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="h-title">(.*?)</h2>')
        if not title: title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        thumb = host[:-1] + thumb

        url = host[:-1] + url

        itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        if '"Page navigation"' in data:
            next_page = scrapertools.find_single_match(data, '<span class="btn rnd npd send-btn">.*?href="(.*?)"')

            if next_page:
                if '?p=' in next_page or '&p=' in next_page:
                     next_page = host[:-1] + next_page

                     itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    bloque = scrapertools.find_single_match(data, '>Episodios<(.*?)</section>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(str(bloque))

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        url = host[:-1] + url

        title = scrapertools.find_single_match(match, '<h2 class="h-title">(.*?)</h2>')

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        thumb = host[:-1] + thumb

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}', "", data)

    lang = 'Vose'

    bloque = scrapertools.find_single_match(data, 'var videos =(.*?)</script>')

    matches = re.compile('".*?","(.*?)"', re.DOTALL).findall(str(bloque))

    ses = 0

    for url in matches:
        ses += 1

        url = url.replace('\\/', '/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url, post = {'value': item.texto} ).data
    data = re.sub(r'\n|\r|\t|\s{2}', "", data)

    results = scrapertools.find_multiple_matches(str(data), '"id":"(.*?)".*?"title":"(.*?)".*?"slug":"(.*?)"')

    for id, title, slug in results:
        thumb = host[:-1] + '/uploads/portadas/' + id + '.jpg'

        url = host[:-1] + '/hentai-' + slug

        itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'api/search'
        item.texto = texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
