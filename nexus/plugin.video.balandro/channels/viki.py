# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://viki.ws/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www.viki.ws/']

    if not headers: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-online-gratis/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'doramas-online-gratis/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + 'episodios-online-gratis/', search_type = 'tvshow', text_color = 'olive' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if 'Añadido recientemente' in data:
        bloque = scrapertools.find_single_match(data, 'Añadido recientemente(.*?)<div class="copy">')
    else:
        bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    i = 0

    for match in matches:
        i += 1

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('Ver Pelicula', '').replace('Completa', '')

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span>.*?,(.*?)</span>').strip()
        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        langs = []
        if 'title="Español"' in match: langs.append('Esp')
        if 'title="Latino"' in match: langs.append('Lat')
        if 'title="Subtitulado"' in match: langs.append('Vose')

        if "Géneros:" in title:
            title = title.split("Géneros:")[0]
            title = title.strip()

        if '/peliculas-online-gratis/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = ', '.join(langs), contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            if item.search_type == 'movie': continue

            if ' (' in title: SerieName = title.split(" (")[0]
            else: SerieName = title

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

        if i == 30: break

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


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'Añadido recientemente(.*?)<div class="copy">')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')


    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        temp_epis = scrapertools.find_single_match(match, '<span>(.*?)</span>')
        if ' / ' in temp_epis:
            temp_epis = temp_epis.split(" / ")[0]
            temp_epis = temp_epis.strip()

        if not temp_epis: continue

        season = scrapertools.find_single_match(temp_epis, 'T(.*?)E').strip()
        episode = scrapertools.find_single_match(temp_epis, 'E(.*?)$').strip()

        title = title.replace('&#215;', ' ')

        titulo = temp_epis + '  ' + title

        if 'Capitulo' in title: SerieName = title.split("Capitulo")[0]
        elif 'Capítulo' in title: SerieName = title.split("Capítulo")[0]
        elif ': ' in title: SerieName = title.split(": ")[0]
        else: SerieName = title

        titulo = titulo.replace('Capitulo', '[COLOR goldenrod]Capitulo[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Capítulo[/COLOR]')

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb,
                                    contentSerieName=SerieName, contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<span class="current">' in data:
            patron = '<span class="current">.*?'
            patron += "href='(.*?)'"

            next_page = scrapertools.find_single_match(data, patron)

            if next_page:
                if '/page/' in next_page:
                   itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'last_epis', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    seasons = scrapertools.find_multiple_matches(data, "<span class='title'>(.*?)<i>")

    for title in seasons:
        title = title.strip()
        tempo = title.replace('Temporada ', '').strip()

        if len(seasons) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = item.url, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    bloque = scrapertools.find_single_match(data, "<div class='se-q'>.*?<span class='title'>" + str(item.title) + "(.*?)</div></div>")
    if not bloque: bloque = scrapertools.find_single_match(data, "<div class='se-q'>.*?<span class='title'>Temporada(.*?)</div></div>")

    patron = "<div class='imagen'.*?data-id='(.*?)'.*?src='(.*?)'.*?<div class='numerando'(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>.*?</span>(.*?)</div></li>"

    episodes = scrapertools.find_multiple_matches(bloque, patron)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(episodes)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Viki', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Viki', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Viki', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Viki', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Viki', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Viki', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for data_id, thumb, temp_epis, url, title, idiomas in episodes[item.page * item.perpage:]:
        langs = []
        if '<img title="Español"' in idiomas: langs.append('Esp')
        if '<img title="Latino"' in idiomas: langs.append('Lat')
        if '<img title="Subtitulado"' in idiomas: langs.append('Vose')
        if '<img title="Ingles"' in idiomas: langs.append('VO')

        epis = scrapertools.find_single_match(temp_epis, ".*?-(.*?)$").strip()

        titulo = str(item.contentSeason) + 'x' + epis + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, languages = ', '.join(langs),
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(episodes) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

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

    # ~ enlaces
    matches = scrapertools.find_multiple_matches(data, "<tr id='link-'(.*?)</tr>")

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, "<a href='(.*?)'")

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue

        elif 'ul.to' in url: continue

        servidor = servertools.get_server_from_url(url, disabled_servers=True)

        if servidor is None: continue

        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        url = servertools.normalize_url(servidor, url)

        if url:
            qlty = scrapertools.find_single_match(match, "<strong class='quality'>(.*?)</strong>")

            lang = scrapertools.find_single_match(match, " src='.*?/flags/(.*?).png'")

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
            if not url.startswith('http'): url = 'https:' + url

            if '.estrenosdoramas.us' in url or 'estrenosdoramas.us' in url:
                return 'Servidor [COLOR plum]Doramas[/COLOR] NO soportado'

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if not servidor == 'directo':
            url = servertools.normalize_url(servidor, url)

            itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1>Resultados encontrados(.*?)<div class="copy">')

    matches = scrapertools.find_multiple_matches(bloque, '<article>(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')

        title = scrapertools.find_single_match(article, ' alt="(.*?)"')

        title = title.replace('Ver Pelicula', '').replace('Completa', '')

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')

        year = scrapertools.find_single_match(article, '<span class="year">(\d{4})</span>')
        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="contenido"><p>(.*?)</p>'))

        langs = []
        if 'title="Español"' in article: langs.append('Esp')
        if 'title="Latino"' in article: langs.append('Lat')
        if 'title="Subtitulado"' in article: langs.append('Vose')

        if "Géneros:" in title:
            title = title.split("Géneros:")[0]
            title = title.strip()

        tipo = 'movie' if '/peliculas-online-gratis/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
               if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = ', '.join(langs), fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
               if item.search_type == 'movie': continue

            if ' (' in title: SerieName = title.split(" (")[0]
            else: SerieName = title

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

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

