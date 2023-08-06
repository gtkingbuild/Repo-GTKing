# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www1.movidy.mobi/'


perpage = 22


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://movidy.mobi/', 'https://www.movidy.mobi/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if '/fecha/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    # ~ las series estructura diferente  '/browse?type=series'
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelis/peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = host + 'pelis/', group = 'masd', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    generos = [
       'aventura',
       'comedia',
       'crimen',
       'documental',
       'drama',
       'familia',
       'historia',
       'misterio',
       'romance',
       'suspense',
       'terror',
       'western'
       ]

    for genero in generos:
        url = host + 'pelis/category/' + genero + '/'

        itemlist.append(item.clone( action = 'list_all', title = genero.capitalize(), url = url, text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1979, -1):
        url = host + 'pelis/peliculas/fecha/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.post:
        data = do_downloadpage(item.url, item.post)
    else:
        data = do_downloadpage(item.url)

    if not item.group:
        if '</h3>' in data: bloque = scrapertools.find_single_match(data, '</h3>(.*?)</section>')
        elif '</h1>' in data: bloque = scrapertools.find_single_match(data, '</h1>(.*?)</main>')
        else: bloque = data

    else:
        bloque = scrapertools.find_single_match(data, '<div class="grid popular">(.*?)</section>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            url = host + 'pelis/wp-admin/admin-ajax.php'

            if not item.next_page:
                if not '"load-more-ajax"' in data: return itemlist
                item.next_page = 1

            item.next_page = item.next_page + 1

            post = {'action': 'action_sorting_post', 'number': 22, 'page': item.next_page, 'types': 'movie'}

            itemlist.append(item.clone( title = 'Siguientes ...', url = url, post = post, action = 'list_all', page = 0, next = item.next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<li data-playerid="(.*?)".*?/flags/(.*?).png.*?<span style.*?>(.*?)</span>')

    ses = 0

    for url, lang, qlty in matches:
        ses += 1

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue
        elif '/player.cuevana.ac' in url: continue

        if '.mystream.' in url: continue

        if lang == 'es': lang = 'Esp'
        elif lang == 'la': lang = 'Lat'
        elif lang == 'mx': lang = 'Lat'
        elif lang == 'en': lang = 'Vose'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        url = servertools.normalize_url(servidor, url)

        if '/links.' in url:
            data = do_downloadpage(url)

            links = scrapertools.find_multiple_matches(data, '<li onclick="go_to_player.*?' + "'(.*?)'")

            for link in links:
                if '/hqq.' in link or '/waaw.' in link or '/netu.' in link: continue
                elif '/player.cuevana.ac' in link: continue

                servidor = servertools.get_server_from_url(link)
                servidor = servertools.corregir_servidor(servidor)

                link = servertools.normalize_url(servidor, link)

                itemlist.append(Item (channel = item.channel, action = 'play', title = '', server = servidor, url = link, language = lang, quality = qlty ))

            continue

        itemlist.append(Item (channel = item.channel, action = 'play', title = '', server = servidor, url = url, language = lang, quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'pelis/?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
