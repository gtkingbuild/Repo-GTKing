# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://pelisencastellano.net/'

perpage = 20


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['http://pelisencastellano.com/', 'https://pelisencastellano.com/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data,'>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque,'href="(.*?)".*?>(.*?)</a>')

    for url, tit in matches:
        if "#" in tit: continue

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="card">(.*?)</a></div></div>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        title = scrapertools.find_single_match(match, '<div class="card-title">(.*?)</div>')
        if not url or not title: continue

        title = title.replace('Ver', '').replace('en (Castellano)', '').replace('en Castellano', '').replace('Online', '').strip()

        year = scrapertools.find_single_match(title, '.*?(\d{4})$')
        if year:
            title = title.replace(year, '').strip()
        else:
            year = '-'

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        lang = 'Esp'

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb, languages = lang,
                                            contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

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
            if '<div class="pagination">' in data:
                next_url = scrapertools.find_single_match(data, "<span class=.*?is-.*?href='(.*?)'")
                if next_url:
                    if '/page/' in next_url:
                        itemlist.append(item.clone( title='Siguientes ...', url=next_url, page=0, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    lng = 'Esp'

    data = do_downloadpage(item.url)

    ses = 0

    qlty = scrapertools.find_single_match(data, '<strong>Calidad: </strong> (\d+)p<').strip()

    outputs = scrapertools.find_single_match(data, 'var output = "(.*?)output ').replace('\\', '')
    outputs = outputs.split(';')

    onlines = scrapertools.find_single_match(data, '<div class="centradito"><script>[A-z0-9]+ \(([^\)]+)')
    onlines = onlines.replace('"', '').split(',')

    for elem in outputs:
        ses += 1

        if 'href' in elem:
            href = scrapertools.find_single_match(elem, 'href="([^"]+)"')
            if 'no.html'in href: continue

            iden = scrapertools.find_single_match(elem, 'codigo(\d+)')
            if not iden: continue

            iden = (int(iden)-1)

            if 'codigo' in href: url = onlines[iden]
            else: url = "%s%s" %(href, onlines[iden])

            if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
                continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, quality = qlty, language = lng ))

    # descarga
    url = scrapertools.find_single_match(data, "var abc = '([^']+)'")

    if url:
        ses += 1

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, quality = qlty, language = lng ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

