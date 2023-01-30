# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://felizestreno.com/'


perpage = 20


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/estreno/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'peliculas-destacadas/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'raking-imdb/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Generos<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        title = title.capitalize()

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist, key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1989, -1):
        url = host + '/estreno/' + str(x) + '/'

        itemlist.append(item.clone( title=str(x), url=url, action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="ml-item">(.*?)</div></div></div>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(match, '<div class="jt-info">(.*?)</div>')
        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title = title, thumbnail = thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if num_matches < perpage: return itemlist

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', url= item.url, page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, "<span aria-current='page'.*?" + 'href="(.*?)"')

            if '/page/' in next_page:
               itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', page=0, text_color='coral' ))


    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<div id="reproductor(.*?)</div>')

    ses = 0

    for match in matches:
        ses += 1

        num_player = scrapertools.find_single_match(match, '(.*?)"')

        other = scrapertools.find_single_match(data, '<li><a href="#reproductor' + num_player + '">(.*?)</a>')
        other = other.replace('Servidor', '').strip()

        if other == '3': other = 'fembed'

        if 'fembed' in other: pass
        elif 'streamlare' in other: pass
        elif 'streamtape' in other: pass
        elif 'zplayer' in other: pass
        else: continue

        lang = 'Esp'

        url = scrapertools.find_single_match(data, '<div id="reproductor' + num_player + '.*?src="(.*?)"')

        if url:
           itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', url = url,
                                 language = lang, other = other.capitalize() ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if '/irgoto.php?url=' in url:
        hash = scrapertools.find_single_match(url, 'url=(.*?)$')

        post = {'url': hash, 'sub': ''}

        url = httptools.downloadpage('https://player.cuevana2.io/r.php', post = post, follow_redirects=False).headers.get('location', '')

        if url.endswith('r.php'):
            new_url = httptools.downloadpage(url, post = post, follow_redirects=False).headers.get('location', '')
            if new_url: url = new_url

    elif '/sc/?h=' in url:
        hash = scrapertools.find_single_match(url, 'h=(.*?)$')

        post = {'h': hash}

        url = httptools.downloadpage('https://player.cuevana2.io/sc/r.php', post = post, follow_redirects=False).headers.get('location', '')

        if url.endswith('r.php'):
            new_url = httptools.downloadpage(url, post = post, follow_redirects=False).headers.get('location', '')
            if new_url: url = new_url

    elif '/irgoto.php?v=2&url=' in url:
        if url.startswith('//'): new_url = 'https:' + url
        else: new_url = url

        data = do_downloadpage(new_url, headers = {'Referer': host})

        new_url = scrapertools.find_single_match(data, "location.href='(.*?)'")

        if new_url: url = new_url

    elif '/index.php?file=' in url: url = ''

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor and not servidor == 'directo':
            url = servertools.normalize_url(servidor, url)

            if '.zplayer.' in url: url = url + "|https://player.cuevana2.io/"

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
