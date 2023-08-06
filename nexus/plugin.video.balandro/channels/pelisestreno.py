# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ww1.pelisestreno.cc/'


# ~ Las series No se tratan solo hay 2 paginas  29/6/2022


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genero/estrenos/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ratings/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>GÉNEROS<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == 'Estrenos': continue

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

    if '<h2>Añadido recientemente' in data:
        bloque = scrapertools.find_single_match(data, '<h2>Añadido recientemente(.*?)© 2022 por Pelisestreno')
    elif '<h1>Tendencias' in data:
        bloque = scrapertools.find_single_match(data, '<h1>Tendencias(.*?)© 2022 por Pelisestreno')
    elif '<h1>Ratings' in data:
        bloque = scrapertools.find_single_match(data, '<h1>Ratings(.*?)© 2022 por Pelisestreno')
    else:
        bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        if not '/pelicula/' in url: continue

        if ('|') in title:
            title = title.split("|")[0]
            title = title.strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="imdb".*?</span>.*?<span>(.*?)</span>')
        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        langs = []
        if 'title="Español"' in match: langs.append('Esp')
        if 'title="Latino"' in match: langs.append('Lat')
        if 'title="Subtitulado"' in match: langs.append('Vose')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = ', '.join(langs), contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<span class="current">' in data:
            patron = '<span class="current">.*?'
            patron += "href='(.*?)'"

            next_page = scrapertools.find_single_match(data, patron)

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    logger.info()
    itemlist = []

    IDIOMAS = {'mx': 'Lat', 'es': 'Esp', 'en': 'Vose', 'jp': 'Vose'}

    data = do_downloadpage(item.url)

    # embeds
    matches = scrapertools.find_multiple_matches(data, "<li id='player-option-(.*?)</li>")

    ses = 0

    for match in matches:
        ses += 1

        servidor = scrapertools.find_single_match(match, "<span class='title'>(.*?)</span>").lower()

        if not servidor: continue

        if 'trailer' in servidor:
            ses = ses - 1
            continue

        elif 'hqq' in servidor or 'waaw' in servidor or 'netu' in servidor: continue

        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        lang = scrapertools.find_single_match(match, " src='.*?/flags/(.*?).png'")

        dpost = scrapertools.find_single_match(match, " data-post='(.*?)'")
        dnume = scrapertools.find_single_match(match, " data-nume='(.*?)'")

        if not dpost or not dnume: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', dpost = dpost, dnume = dnume, other = servidor.capitalize(), language = IDIOMAS.get(lang, lang) ))

    # enlaces
    matches = scrapertools.find_multiple_matches(data, "<tr id='link-'(.*?)</tr>")

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, "<a href='(.*?)'")

        if not url: continue

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue

        elif 'openload' in url: continue
        elif 'powvideo' in url: continue
        elif 'streamplay' in url: continue
        elif 'rapidvideo' in url: continue
        elif 'streamango' in url: continue
        elif 'verystream' in url: continue
        elif 'vidtodo' in url: continue

        elif 'ul.to' in url: continue
        elif 'katfile' in url: continue
        elif 'rapidgator' in url: continue
        elif 'rockfile' in url: continue
        elif 'nitroflare' in url: continue
        elif '1fichier' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        url = servertools.normalize_url(servidor, url)

        if url:
            qlty = scrapertools.find_single_match(match, "<strong class='quality'>(.*?)</strong>")

            lang = scrapertools.find_single_match(match, " src='.*?/flags/(.*?).png'")

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = IDIOMAS.get(lang, lang), quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if not url:
        post = {'action': 'doo_player_ajax', 'post': item.dpost, 'nume': item.dnume, 'type': 'movie'}
        headers = {"Referer": item.url}

        data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)

        url = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        url = url.replace('\\/', '/')

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1>Resultados encontrados(.*?)© 2022 por Pelisestreno')

    matches = scrapertools.find_multiple_matches(bloque, '<article>(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')

        if not '/pelicula/' in url: continue

        title = scrapertools.find_single_match(article, ' alt="(.*?)"')

        if ('|') in title:
            title = title.split("|")[0]
            title = title.strip()

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')

        year = scrapertools.find_single_match(article, '<span class="year">(\d{4})</span>')
        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        langs = []
        if '/flags/es.png' in article: langs.append('Esp')
        if '/flags/mx.png' in article: langs.append('Lat')
        if '/flags/en.png' in article: langs.append('Vose')

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="contenido"><p>(.*?)</p>'))

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = ', '.join(langs), contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

