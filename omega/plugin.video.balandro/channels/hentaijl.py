# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://hentaijl.com/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'directorio-hentai' ))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = host, group = 'find', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'directorio-hentai?genre[]=71&order=updated' ))

    itemlist.append(item.clone( title = 'Hentai', action = 'list_all', url = host + 'directorio-hentai?tipo[]=1&tipo[]=7&order=updated' ))
    itemlist.append(item.clone( title = 'Jav', action = 'list_all', url = host + 'directorio-hentai?tipo[]=2&order=updated' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'directorio-hentai').data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = scrapertools.find_single_match(data, '<select name="genre(.*?)</select>')

    matches = re.compile("<option value='(.*?)'.*?>(.*?)</option>", re.DOTALL).findall(bloque)

    for value, title in matches:
        url = host + 'directorio-hentai?genre[]=' + value + '&order=updated'

        itemlist.append(item.clone( action = 'list_all', url = url, title = title, text_color='orange' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1989, -1):
        url = host + 'directorio-hentai?year[]=' + str(x) + '&order=updated'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', text_color='orange' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    bloque = scrapertools.find_single_match(data, '>Hentais Online<(.*?)</main>')
    if not bloque: bloque = scrapertools.find_single_match(data, '>Últimos episodios agregados<(.*?)</main>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)
    if not matches: matches = re.compile('<li>(.*?)</li>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, "<a href='(.*?)'")

        title = scrapertools.find_single_match(match, "<h3 class='Title'>(.*?)</h3>")
        if not title: title = scrapertools.find_single_match(match, "alt='(.*?)'")

        if not url or not title: continue

        title = title.replace('ver', '').strip()

        thumb = scrapertools.find_single_match(match, "<img src='(.*?)'")

        if item.group == 'find':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))
        else:
            itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="page-item active">.*?href="(.*?)"')

        if next_page:
            if 'page=' in next_page:
                next_page = next_page.replace('&amp;', '&')

                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    bloque = scrapertools.find_single_match(data, 'var episodes =(.*?);')

    matches = re.compile('(.*?)],', re.DOTALL).findall(str(bloque))

    for match in matches:
        url = scrapertools.find_single_match(str(match), ',"(.*?)"')

        url = item.url + '/' + url

        title = scrapertools.find_single_match(str(match), '.jpg","(.*?)"')

        thumb = scrapertools.find_single_match(str(match), '","(.*?)"')

        thumb = host + 'imgs/' + thumb

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}', "", data)

    lang = 'Vo'
    if '-latino' in item.url: lang = 'Lat'

    matches = re.compile('<iframe src="(.*?)"', re.DOTALL).findall(data)

    ses = 0

    for url in matches:
        ses += 1

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

    # ~ descargas  ReCaptcha

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'directorio-hentai?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
