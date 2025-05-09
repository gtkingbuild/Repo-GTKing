# -*- coding: utf-8 -*-

import re

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.zonapelis.org/'


def do_downloadpage(url, post=None, headers=None):
    raise_weberror = True
    if '/release/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if not data:
        if not '?s=' in url:
            if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('ZonaPelis', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

            timeout = config.get_setting('channels_repeat', default=30)

            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone ( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Cine clásico', action = 'list_all', url = host + 'genre/cine-clasico/', search_type = 'movie', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'imdb/', group = 'imdb', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tvshows/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'imdb/', group = 'imdb', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por plataforma', action= 'plataformas', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Calidad(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color='moccasin' ))

    return sorted(itemlist,key=lambda x: x.title)


def plataformas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Canales<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color='hotpink' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Género<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
        text_color = 'deepskyblue'
        top_year = 1954
    else:
        text_color = 'hotpink'
        top_year = 1999

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, top_year, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'release/' + str(x) + '/', action='list_all', text_color = text_color ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
        search_type = 'movies'
        text_color = 'deepskyblue'
    else:
        search_type = 'tvshows'
        text_color = 'hotpink'

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        url = host + 'wp-json/dooplay/glossary/?term=%s&nonce=ab6f027a0d&type=%s' % (letra.lower(), search_type)

        itemlist.append(item.clone( action = 'list_alfa', title = letra, url = url, text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if item.group:
        bloque = scrapertools.find_single_match(data, '>Ranking IMDb <span>(.*?)>Popular<')
    else:
        bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)>Popular<')
        if not bloque: bloque = scrapertools.find_single_match(data, '>Resultados encontrados(.*?)>Popular<')

    if item.group:
        matches = re.compile("id='top-(.*?)</div></div>", re.DOTALL).findall(bloque)
    else:
        matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')
        if not url: url = scrapertools.find_single_match(article, " href='(.*?)'")

        title = scrapertools.find_single_match(article, ' alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(article, '<h3 class="title">(.*?)</h3>')
        if not title: title = scrapertools.find_single_match(article, " alt='(.*?)'")

        if not url or not title: continue

        title = title.replace('&#038;', '&').replace('&#8216;', '& ').replace('&#8230;', '')

        tipo = 'tvshow' if '/tvshows/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(article, " src='(.*?)'")

        year = scrapertools.find_single_match(article, '</h3><span>(\d+)</span>')
        if not year: year = '-'

        if '/release/' in item.url: year = scrapertools.find_single_match(item.url, "/release/(.*?)/")

        qlty = scrapertools.find_single_match(article, '<span class="quality">(.*?)</span')

        if tipo == 'movie':
            if not item.search_type == 'all':
               if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
               if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">' + ".*?href='(.*?)'.*?<div class='resppages'")

            if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?href="(.*?)"' + ".*?<div class='resppages'>")

            if next_page:
               if '/page/' in next_page:
                   itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def list_alfa(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(str(data), '"(.*?)"imdb":')

    for match in matches:
        url = scrapertools.find_single_match(match, '"url":"(.*?)"')

        title = scrapertools.find_single_match(match, '"title":"(.*?)"')

        if not url or not title: continue

        title = title.replace('&#038;', '&').replace('&#8216;', '& ').replace('&#8230;', '')

        thumb = scrapertools.find_single_match(match, '"img":"(.*?)"')

        thumb = thumb.replace('\\/', '/')

        title = clean_title(title)

        year = scrapertools.find_single_match(match, '"year":"(.*?)"')
        if not year: year = '-'

        tipo = 'movie' if item.search_type == 'movie' else 'tvshow'

        sufijo = '' if item.search_type != 'all' else tipo

        url = url.replace('\\/', '/')

        if tipo == 'tvshow':
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile("<span class='title'>Temporada(.*?)<i>", re.DOTALL).findall(data)

    for numtempo in matches:
        numtempo = numtempo.strip()

        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = numtempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<span class='title'>Temporada " + str(item.contentSeason) + "(.*?)</ul>")

    matches = re.compile("<li class='mark-.*?<img src='(.*?)'.*?<div class='numerando'>(.*?)</div>.*?<a href='(.*?)'.*?>(.*?)</a>", re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('ZonaPelis', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('ZonaPelis', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZonaPelis', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZonaPelis', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZonaPelis', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZonaPelis', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('ZonaPelis', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, epis, url, title in matches[item.page * item.perpage:]:
        epis = scrapertools.find_single_match(epis, '.*?-(.*?)$').strip()

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title.replace(str(item.contentSeason) + 'x' + str(epis),'')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail=thumb, contentType = 'episode', contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color= 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Español': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose', 'V.O.S.E': 'Vose', 'Inglés': 'Ing'}

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Enlaces<(.*?)</table>')

    matches = scrapertools.find_multiple_matches(bloque, "<tr id='link-.*?<a href='(.*?)'.*?<strong class='quality'>(.*?)</strong>.*?</td><td>(.*?)</td>")

    ses = 0

    # enlaces
    for link, qlty, lang in matches:
        ses += 1

        if not link: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server='directo', title = '', link = link, quality = qlty, language = IDIOMAS.get(lang, lang), age='Torrent' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = ''

    data = do_downloadpage(item.link)

    new_url = scrapertools.find_single_match(data, '<a id="link".*?href="(.*?)"')

    if not new_url: return itemlist

    data = do_downloadpage(new_url)

    url = scrapertools.find_single_match(data, '<li id="download">.*?<a href="(.*?)"')

    if url:
        if url.endswith('.torrent'):
            itemlist.append(item.clone(url = url, server = 'torrent'))
        else:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor == 'directo':
                new_server = servertools.corregir_other(url).lower()
                if new_server.startswith("http"): servidor = new_server

            url = servertools.normalize_url(servidor, url)

            itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def clean_title(title):
    logger.info()

    title = title.replace('\\u00e1', 'a').replace('\\u00c1', 'a').replace('\\u00e9', 'e').replace('\\u00c9', 'e').replace('\\u00ed', 'i').replace('\\u00f3', 'o').replace('\\u00fa', 'u')
    title = title.replace('\\u00f1', 'ñ').replace('\\u00bf', '¿').replace('\\u00a1', '¡').replace('\\u00ba', 'º')
    title = title.replace('\\u00eda', 'a').replace('\\u00f3n', 'o').replace('\\u00fal', 'u').replace('\\u00e0', 'a')

    return title


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
