# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://alldd.net/'


# ~ Las series No se tratan solo hay 2 paginas  29/6/2022


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://ww1.pelisestreno.cc/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not headers: headers = {'Referer': host}

    if '/release/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Genero<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if config.get_setting('descartar_anime', default=False):
            if title == 'Anime': continue

        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        url = host + 'release/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', page = 1, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '</h2>(.*?)>Titulos Aleatorios<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        if not url or not title: continue

        if not '/movies/' in url: continue

        if ('|') in title:
            title = title.split("|")[0]
            title = title.strip()

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="Qlty Yr">(.*?)</span>')
        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        langs = []
        if 'Castellano' in match: langs.append('Esp')
        if 'Latino' in match: langs.append('Lat')
        if 'Subtitulado' in match: langs.append('Vose')
        if 'Inglés' in match: langs.append('Vo')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = ', '.join(langs), contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<a class="page-link current"' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose', 'Inglés': 'Vo'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<div class="Optntl"(.*?)</li>')

    ses = 0

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        if '/paste/p?' in url:
            data1 = do_downloadpage(url)

            if 'Castellano' in data1: lng = 'Esp'
            elif 'Latino' in data1: lng = 'Lat'
            elif 'Subtitulado' in data1: lng = 'Vose'
            elif 'Inglés' in data1: lng = 'Vo'
            else: lng = '?'

            links = scrapertools.find_multiple_matches(data1, 'target="_blank">(.*?)</a>')

            for link in links:
                if 'doodrive' in link: continue

                elif 'ul.to' in link: continue
                elif 'katfile' in link: continue
                elif 'rapidgator' in link: continue
                elif 'rockfile' in link: continue
                elif 'nitroflare' in link: continue
                elif '1fichier' in link: continue

                servidor = servertools.get_server_from_url(link)
                servidor = servertools.corregir_servidor(servidor)

                if 'magnet' in link: servidor = 'torrent'
                elif link.endswith('.torrent'): servidor = 'torrent'

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                    if not config.get_setting('developer_mode', default=False): continue

                other = servidor

                if servidor == 'various': other = servertools.corregir_other(link)

                if servidor == other: other = ''

                elif not servidor == 'directo':
                 if not servidor == 'various': other = ''

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = link, language = lng, other = other ))

            continue

        if '/doodrive.' in url: continue

        elif 'ul.to' in url: continue
        elif 'katfile' in url: continue
        elif 'rapidgator' in url: continue
        elif 'rockfile' in url: continue
        elif 'nitroflare' in url: continue
        elif '1fichier' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if 'magnet' in url: servidor = 'torrent'
        elif url.endswith('.torrent'): servidor = 'torrent'

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        lang = scrapertools.find_single_match(match, '<p class="AAIco-language">(.*?)</p>')

        other = servidor

        if servidor == 'various': other = servertools.corregir_other(url)

        if servidor == other: other = ''

        elif not servidor == 'directo':
           if not servidor == 'various': other = ''

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = IDIOMAS.get(lang, lang), other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if 'magnet' in item.url or item.url.endswith('.torrent'):
        if PY3:
            from core import requeststools
            data = requeststools.read(item.url, 'pelisestreno')
        else:
            data = do_downloadpage(item.url)

        import os

        file_local = os.path.join(config.get_data_path(), "temp.torrent")
        with open(file_local, 'wb') as f: f.write(data); f.close()

        itemlist.append(item.clone( url = file_local, server = 'torrent' ))

        return itemlist

    url = item.url

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

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

