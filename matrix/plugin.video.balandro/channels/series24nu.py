# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ww2.series24.nu/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if not headers: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-serie-completa/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_episodes', url = host + 'ver-serie-online/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ratings/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Novelas', action = 'list_all', url = host + 'series-genero/novelas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>GÉNERO<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return sorted(itemlist, key=lambda it: it.title)


def plataformas(item):
    logger.info()
    itemlist = []

    productoras = [
        ('amazon', 'Amazon'),
        ('antena-3', 'Antena 3'),
        ('apple-tv', 'Apple TV'),
        ('atresplayer-premium', 'Atresplayer Premium'),
        ('canal', 'Canal+'),
        ('cbc-television', 'CBC Television'),
        ('cbs', 'Cbs'),
        ('caracol-tv', 'Caracol TV'),
        ('disney', 'Disney+'),
        ('elisa-viihde-viaplay', 'Elisa Viihde Viaplay'),
        ('fox', 'FOX'),
        ('globoplay', 'Globoplay'),
        ('hbo', 'HBO'),
        ('hulu', 'Hulu'),
        ('itv', 'ITV'),
        ('jtbc', 'Jtbc'),
        ('kanal-d', 'Kanal D'),
        ('las-estrellas', 'Las Estrellas'),
        ('nbc', 'NBC'),
        ('netflix', 'Netflix'),
        ('novelastv', 'Novelas TV'),
        ('peacock', 'Peacock'),
        ('rcn', 'Rcn'),
        ('rede-globo', 'Rede Globo'),
        ('rtbf-be', 'Rtbf BE'),
        ('showtime', 'Showtime'),
        ('star-tv', 'Star Tv'),
        ('starz', 'Starz'),
        ('telemundo', 'Telemundo'),
        ('tf1', 'TF1'),
        ('the-roku-channel', 'The Roku Channel'),
        ('the-wb', 'The WB'),
        ('tv-globo', 'TV Globo'),
        ('tv8', 'TV8'),
        ('upn', 'UPN')
        ]

    for opc, tit in productoras:
        url = host + 'network/' + opc + '/'

        itemlist.append(item.clone( title = tit, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)</h2>')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="imdb".*?</span>.*?<span>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '</span> <span>(.*?)</span>')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        titulo = title

        if " | " in titulo: titulo = titulo.split(" | ")[0]

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = titulo, infoLabels={'year': year} ))

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


def last_episodes(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)</h2>')

    matches = scrapertools.find_multiple_matches(bloque, 'data-ids=(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')

        title = scrapertools.find_single_match(match, '<span class="serie">(.*?)</span>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        temp_epis = scrapertools.find_single_match(match, '<span class="b">(.*?)</span>')

        if not temp_epis: continue

        season = scrapertools.find_single_match(temp_epis, '(.*?)x')
        episode = scrapertools.find_single_match(temp_epis, '.*?x(.*?)$')

        title = title.replace('( ' + str(season) + ' x ' + str(episode) + ' )', '').strip()

        SerieName = title

        if ": " in SerieName: SerieName = SerieName.split(": ")[0]

        titulo = temp_epis + ' ' + title

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, contentSerieName=SerieName,
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
         if '<span class="current">' in data:
             patron = '<span class="current">.*?'
             patron += "href='(.*?)'"

             next_page = scrapertools.find_single_match(data, patron)
             if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'last_episodes', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    data_id = scrapertools.find_single_match(data, 'var id.*?=(.*?);')

    if not data_id:
        return itemlist

    post = {'action': 'seasons', 'id': data_id}
    headers = {'Referer': item.url}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)

    seasons = scrapertools.find_multiple_matches(data, "<span class='title'>(.*?)<i>")

    for title in seasons:
        title = title.strip()
        tempo = title.replace('Temporada ', '').strip()

        if len(seasons) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.data_id = data_id
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, data_id = data_id, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    post = {'action': 'seasons', 'id': item.data_id}
    headers = {'Referer': item.url}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, "<div class='se-q'>.*?<span class='title'>" + str(item.title) + "(.*?)</div></div>")
    if not bloque:
        bloque = scrapertools.find_single_match(data, "<div class='se-q'>.*?<span class='title'>Temporada(.*?)</div></div>")

    patron = "<div class='imagen'.*?data-id='(.*?)'.*?src='(.*?)'.*?<div class='numerando'(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>.*?</span>(.*?)</div></li>"

    episodes = scrapertools.find_multiple_matches(bloque, patron)

    if item.page == 0:
        sum_parts = len(episodes)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Series24Nu', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Series24Nu', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Series24Nu', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Series24Nu', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Series24Nu', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

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

        if 'trailer' in servidor: continue

        elif 'hqq' in servidor or 'waaw' in servidor or 'netu' in servidor: continue
        elif 'openload' in servidor: continue
        elif 'powvideo' in servidor: continue
        elif 'streamplay' in servidor: continue
        elif 'rapidvideo' in servidor: continue
        elif 'streamango' in servidor: continue
        elif 'verystream' in servidor: continue
        elif 'vidtodo' in servidor: continue
        elif 'flix555' in servidor: continue

        lang = scrapertools.find_single_match(match, " src='.*?/flags/(.*?).png'")

        dpost = scrapertools.find_single_match(match, " data-post='(.*?)'")
        dnume = scrapertools.find_single_match(match, " data-nume='(.*?)'")

        if not dpost or not dnume: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', dpost = dpost, dnume = dnume, other = servidor.capitalize(),
                              language = IDIOMAS.get(lang, lang) ))

    # enlaces
    matches = scrapertools.find_multiple_matches(data, "<tr id='link-'(.*?)</tr>")

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, "<a href='(.*?)'")

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue
        elif 'openload' in url: continue
        elif 'powvideo' in url: continue
        elif 'streamplay' in url: continue
        elif 'rapidvideo' in url: continue
        elif 'streamango' in url: continue
        elif 'verystream' in url: continue
        elif 'vidtodo' in url: continue
        elif 'flix555' in url: continue

        elif 'ul.to' in url: continue
        elif 'katfile' in url: continue
        elif 'rapidgator' in url: continue
        elif 'rockfile' in url: continue
        elif 'nitroflare' in url: continue
        elif '1fichier' in url: continue
        elif '.oboom.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

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

        url = scrapertools.find_single_match(data, "src='(.*?)'")

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

    bloque = scrapertools.find_single_match(data, '<h1>Resultados encontrados(.*?)<h2>')

    matches = scrapertools.find_multiple_matches(bloque, '<article>(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')

        title = scrapertools.find_single_match(article, ' alt="(.*?)"')

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')

        year = scrapertools.find_single_match(article, '<span class="year">(\d{4})</span>')
        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="contenido"><p>(.*?)</p>'))

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
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

