# -*- coding: utf-8 -*-


import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.cuevana3.in/'


perpage = 25


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)".*?>(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        url = host[:-1] + url

        itemlist.append(item.clone( title=title, url=url, action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))

    if itemlist:
        itemlist.append(item.clone( title='Guerra', url=host + 'category/guerra', action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title='Infantil', url=host + 'category/infantil', action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title='Suspense', url=host + 'category/suspense', action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title='Western', url=host + 'category/western', action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li class="TPostMv">(.*?)</li>', re.DOTALL).findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        if thumb: thumb = 'https:' + thumb

        url = host[:-1] + url

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?<a href="(.*?)"')

            if next_page:
                next_page = host[:-1] + next_page

                itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    if '<span>Seleccionar temporada</span>' in data:
        platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]NO es una película[/B][/COLOR]')
        return

    matches = re.compile('<li data-video="(.*?)".*?<span>(.*?)</span>', re.DOTALL).findall(data)

    ses = 0

    for url, lang_srv in matches:
        ses += 1

        lang = ''

        if ' - ' in lang_srv: lang = scrapertools.find_single_match(lang_srv, '.*?-(.*?)-').strip()

        if url.startswith('//'): url = 'https:' + url

        if '/play?id=' in url:
           data2 = do_downloadpage(url)

           matches2 = scrapertools.find_multiple_matches(data2, '<li class="linkserver".*?data-video="(.*?)"')

           for match in matches2:
               servidor = servertools.get_server_from_url(match)
               servidor = servertools.corregir_servidor(servidor)

               other = ''

               if servidor == 'various': other = servertools.corregir_other(match)

               if not servidor == 'directo':
                   itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = match, server = servidor, language = IDIOMAS.get(lang, lang), other = other ))

           continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = IDIOMAS.get(lang, lang), other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search/' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

