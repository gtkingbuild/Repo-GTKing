# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://cine24h.net/'


perpage = 30

# ~ Las series predominan con servidor Netu, se desprecian


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://cine24h.online/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if '&years%5B%5D=' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'peliculas-mas-vistas/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas-mas-valoradas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('accion', 'Acción'),
       ('animacion', 'Animación'),
       ('aventura', 'Aventura'),
       ('belica', 'Bélica'),
       ('ciencia-ficcion', 'Ciencia ficción'),
       ('comedia', 'Comedia'),
       ('crimen', 'Crimen'),
       ('documental', 'Documental'),
       ('drama', 'Drama'),
       ('familia', 'Familia'),
       ('fantasia', 'Fantasía'),
       ('foreign', 'Foreign'),
       ('guerra', 'Guerra'),
       ('historia', 'Historia'),
       ('misterio', 'Misterio'),
       ('musica', 'Música'),
       ('navidad', 'Navidad'),
       ('romance', 'Romance'),
       ('sci-fi-fantasy', 'Sci-Fi & Fantasy'),
       ('suspense', 'Suspense'),
       ('terror', 'Terror'),
       ('western', 'Western')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'category/' + opc + '/', action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1939, -1):
        url = host + '?s=trfilter&trfilter=1&years%5B%5D=' + str(x)

        itemlist.append(item.clone( title=str(x), url=url, action='list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)>Donar<')

    matches = re.compile('<article(.*?)</article>').findall(bloque)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        title = scrapertools.find_single_match(article, '<h3 class="Title">(.*?)</h3>')

        if not url or not title: continue

        if '/serie/' in url: continue

        title = re.sub(r'\((.*)', '', title)
        title = re.sub(r'\[(.*?)\]', '', title)

        title = title.replace('&#8211;', '')

        thumb = scrapertools.find_single_match(article, '<img src="(.*?)"')

        if not thumb.startswith("http"): thumb = "https:" + thumb

        year = scrapertools.find_single_match(article, '<span class="Year">(.*?)</span>')
        if not year: year = '-'

        lang = 'Lat'
        if '-sub/' in url: lang = 'Vose'
        if '-es/' in url: lang = 'Esp'

        itemlist.append(item.clone( action='findvideos', url=url, title = title, thumbnail = thumb, languages = lang,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if num_matches < perpage: return itemlist

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='Siguientes ...', url= item.url, page=item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        if itemlist:
            if 'class="page-numbers current">' in data:
                 next_page = scrapertools.find_single_match(data, 'class="page-numbers current">.*?<a class="page-numbers".*?href="(.*?)"')
            else:
                 next_page = scrapertools.find_single_match(data, '<a class="page-numbers".*?href="(.*?)"')

            if '/page/' in next_page:
               itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', page=0, text_color='coral' ))


    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'LAT': 'Lat', 'ESP': 'Esp', 'SUB': 'Vose'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<li data-shortcode="(.*?)</li>')

    ses = 0

    for match in matches:
        ses += 1

        other = scrapertools.find_single_match(match, 'data-tplayernv="Opt.*?<span>(.*?)</span>')

        other = other.replace('🥇', '').replace('🥉', '').strip()

        if 'HQQ' in other: continue
        elif 'FMD' in other: other = 'fembed'

        idio = scrapertools.find_single_match(match, 'data-tplayernv="Opt.*?</span><span>(.*?)-.*?</span>').strip()

        lang = IDIOMAS.get(idio, idio)

        qlty = scrapertools.find_single_match(match, 'data-tplayernv="Opt.*?</span><span>.*?-(.*?)</span>').strip()

        opt = scrapertools.find_single_match(match, 'data-tplayernv="(.*?)"')

        url = scrapertools.find_single_match(data, 'id="' + opt + '".*?data-src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, 'id="' + opt + '".*?src=&quot;(.*?)&quot;')

        if url:
           itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', url = url, language = lang, quality = qlty, other = other.capitalize() ))

    # ~ downloads

    matches = scrapertools.find_multiple_matches(data, '<span class="Num">.*?href="(.*?)"')

    for match in matches:
        ses += 1

        if not '/redirect-to/' in match: continue

        url = scrapertools.find_single_match(match, 'redirect=(.*?)$')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if url:
           itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, language = item.languages ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')
    item.url = item.url.replace('amp;#038;', '&').replace('#038;', '&').replace('amp;', '&')

    url = item.url

    if item.server == 'directo':
        data = do_downloadpage(url)

        new_url = scrapertools.find_single_match(data, 'src="(.*?)"')

        if new_url: url = new_url

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if 'mystream.' in url: servidor = ''
        if 'gounlimited.' in url: servidor = ''

        if servidor:
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url=url, server=servidor ))

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
