# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://creyente.digital/'


perpage = 35


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-cristianas/', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_ser', url = host + 'series-cristianas/', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>PELÍCULAS DISPONIBLES<(.*?)>PELÍCULAS CRISTIANAS<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()

        if not url or not title: continue

        title = title.replace('Película Cristiana', '').replace('en HD Audio Latino', '').replace(' - 1080p', '').strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType = 'movie', contentTitle = title, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))

    return itemlist


def list_ser(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>SERIES CRISTIANAS DISPONIBLES<(.*?)>SERIES CRISTIANAS<')

    matches = scrapertools.find_multiple_matches(bloque, '<figure(.*?)</figure>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        title = title.replace('Serie Cristiana', '').replace('Series Bíblicas', '').strip()

        SerieName = title

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_ser', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    _bloque = ''

    urls = False

    seasons = False

    if 'id="h-temporadas' in data: seasons = True

    temporadas = re.compile('id="temporada-(.*?)"', re.DOTALL).findall(data)
    if not temporadas: temporadas = re.compile('id="h-temporadas(.*?)"', re.DOTALL).findall(data)

    if not temporadas:
       _bloque = scrapertools.find_single_match(data, '</h2>(.*?)<h2 class="wp-block-heading has-text-align-center"')

       temporadas = re.compile('<h2 class="entry-title">.*?Temporada (.*?)</h2>', re.DOTALL).findall(_bloque)

       if temporadas: urls = True

    if not temporadas:
        if config.get_setting('channels_seasons', default=True):
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]Temporadas' + '[/COLOR]')

        item.page = 0

        item.contentType = 'season'
        item.contentSeason = 1
        itemlist = episodios(item)
        return itemlist

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0

            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        if urls:
            links = scrapertools.find_multiple_matches(_bloque, '<article(.*?)</article>')

            for link in links:
                url = scrapertools.find_single_match(link, '<a href="(.*?)"')

                if '-temporada-' + tempo + '/' in url:
                    break

            if not url == item.url:
                itemlist.append(item.clone( action = 'episodios', url = url, title = title, page = 0, urls = urls,
                                            contentSerieName = item.contentSerieName, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))
            continue

        elif seasons:
            bloque = scrapertools.find_single_match(data, 'id="h-temporadas' + str(tempo) + '(.*?)<h2 class="wp-block-heading has-text-align-center"')

            matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

            for match in matches:
                titulo = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

                season = scrapertools.find_single_match(titulo, 'Temporada(.*?)$').strip()

                url = scrapertools.find_single_match(match, '<a href="(.*?)"')

                if '/subtitulada/' in match:
                    titulo = titulo.replace('» Audio Latino »', '» Subtitulada »')
                    if not 'Subtitulada' in titulo: titulo = titulo + ' » Subtitulada »'

                itemlist.append(item.clone( action = 'episodios', url = url, title = titulo, seasons = seasons, page = 0,
                                            contentSerieName = item.contentSerieName, contentType = 'season', contentSeason = season, text_color = 'tan' ))

        else:
            itemlist.append(item.clone( action = 'episodios', title = title, page = 0,
                                        contentSerieName = item.contentSerieName, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    sub = False
    if '/subtitulada/' in item.url: sub = True

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if 'id="temporada-' in data:
        bloque = scrapertools.find_single_match(data, 'id="temporada-' + str(item.contentSeason) + '(.*?)<h2 class="wp-block-heading has-text-align-center"')

        if item.urls:
            bloque = scrapertools.find_single_match(data, '</h2>(.*?)<h2 class="wp-block-heading has-text-align-center"')
        elif item.seasons:
            bloque = scrapertools.find_single_match(data, 'id="temporada-.*?TEMPORADA ' + str(item.contentSeason) + '(.*?)<h2 class="wp-block-heading has-text-align-center"')

    elif 'id="h-temporadas' in data:
        bloque = scrapertools.find_single_match(data, 'id="h-temporadas' + str(item.contentSeason) + '(.*?)<h2 class="wp-block-heading has-text-align-center"')

    else:
        bloque = scrapertools.find_single_match(data, '>TODOS LOS CAPÍTULOS(.*?)</center>')
        if not bloque: bloque = scrapertools.find_single_match(data, '</h2>(.*?)<h2 class="wp-block-heading has-text-align-center"')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Creyente', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Creyente', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Creyente', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Creyente', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Creyente', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Creyente', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if '<h2 class="entry-title">' in match:
            title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        epis = scrapertools.find_single_match(title, 'Capitulo(.*?)$').strip()
        if not epis: epis = 1

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb, sub = sub,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, i = i, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    lang = 'Lat'
    if item.sub: lang = 'Vose'

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    ses = 0

    matches = scrapertools.find_multiple_matches(data, '<iframe.*?data-litespeed-src="(.*?)"')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    for match in matches:
        if '.youtube.' in match: continue

        ses += 1

        url = match

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(url)

        if '/ok.ru' in url: servidor = 'okru'
        elif '/drive.' in url: servidor = 'gvideo'

        url = servertools.normalize_url(servidor, url)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Resultados (.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        if url == host + 'series-cristianas/': continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        title = title.replace('Audio Latino', '').replace('Subtitulada', '').strip()

        SerieName = title

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]
        if 'HD' in SerieName: SerieName = SerieName.split("HD")[0]

        SerieName = SerieName.strip()

        _tipo = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

        tipo = 'tvshow' if 'Series' in _tipo or 'Temporada' in _tipo else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

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

