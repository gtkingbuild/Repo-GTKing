# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://entrepeliculasyseries.pro/'



def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                data = httptools.downloadpage(url, post=post, headers=headers).data
        except:
            pass

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas-mas-valoradas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'peliculas-mas-vistas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href=(.*?)>(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)>TOP ESTRENOS<')
    if not bloque: bloque = scrapertools.find_single_match(data, '</h1>(.*?)TOP ESTRENOS')

    if not bloque: bloque = scrapertools.find_single_match(data, '</h1>(.*?)>PELÍCULAS DESTACADAS<')
    if not bloque: bloque = scrapertools.find_single_match(data, '</h1>(.*?)PELÍCULAS DESTACADAS')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="TPost C post-(.*?)</div> </div>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<div class="TPost C post type-post(.*?)</div> </div>')

    for match in matches:
        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        url = scrapertools.find_single_match(match, 'href=(.*?)>').strip()

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, 'data-src=(.*?)class=').strip()
        if not thumb: thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"').strip()

        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, '<span class=Year>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '<span class="Date">(.*?)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(match, '<span class=Qlty>(.*?)</span>')
        if not qlty: qlty = scrapertools.find_single_match(match, '<span class="Qlty">(.*?)</span>')

        if qlty == 'SERIE': qlty = ''

        tipo = 'movie' if '/peli/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, qualities = qlty, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, qualities = qlty, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<nav class="navigation pagination">' in data or 'navigation pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<a class="current page-link">.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('"', '').strip()

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<option value="(.*?)"')

    for nro_season in matches:
        title = 'Temporada ' + nro_season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = nro_season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = nro_season ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.contentSeason)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    season = scrapertools.find_single_match(data, '<ul id="season-' + str(item.contentSeason) + '"(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(season, '<article(.*?)</article>')

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('EntrePeliculasySeriesPro', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EntrePeliculasySeriesPro', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EntrePeliculasySeriesPro', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EntrePeliculasySeriesPro', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('EntrePeliculasySeriesPro', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        nro_epi = scrapertools.find_single_match(match, '<span class="Year">.*?x(.*?)</span>')

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        titulo = str(item.contentSeason) + 'x' + nro_epi + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = nro_epi ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    options = scrapertools.find_multiple_matches(data, 'data-embed="(.*?)".*?alt="(.*?)".*?<span> CALIDAD (.*?)<span>')

    ses = 0

    for embed, lang, qlty in options:
        ses += 1

        if '</span>' in qlty: qlty = scrapertools.find_single_match(qlty, '(.*?)</span>').strip()

        if lang == 'Array': lang = scrapertools.find_single_match(data, embed + '.*?"><span>(.*?)<span>').strip()

        if lang == 'Subtitulado': lang = 'Vose'
        elif lang == 'Español Latino': lang = 'Lat'
        elif lang == 'Español de España': lang = 'Esp'

        url = base64.b64decode(embed).decode("utf-8")

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

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

