# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seriescalidad.lat/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/tv-series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Nuevos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Telenovelas', action = 'list_all', url = host + 'series/telenovelas/', search_type = 'tvshow', text_color = 'limegreen' ))

    itemlist.append(item.clone( title = 'Reality', action = 'list_all', url = host + 'series/reality-show/', search_type = 'tvshow', text_color = 'greenyellow' ))

    itemlist.append(item.clone( title = 'Doramas', action = 'list_all', url = host + 'series/tv-series-drama/', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'series/animes/', search_type = 'tvshow', text_color = 'springgreen' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, '>Nuevos Capitulos<(.*?)>Series<')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="pm-video-thumb ripple">(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, ' title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        SerieName = scrapertools.find_single_match(match, ' alt="(.*?)"')

        season = scrapertools.find_single_match(url, '-temporada-(.*?)$').strip()

        if not season: season = 1

        epis = scrapertools.find_single_match(url, '-capitulo-(.*?)-').strip()

        if not epis: epis = 1

        titulo = str(season) + 'x' + str(epis) + ' ' + SerieName

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, infoLabels={'year': '-'},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, '<div class="pm-video-thumb ripple">(.*?)</li><li>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="" class="ellipsis">(.*?)</a>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year': '-' } ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination pagination' in data:
            next_page = scrapertools.find_single_match(data, '<ul class="pagination pagination.*?<li class="active">.*?</a>.*?href="(.*?)"')

            if next_page:
                if '/page-' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    seasons = scrapertools.find_multiple_matches(data, 'href="#collapse_(.*?)"')

    for tempo in seasons:
        title = 'Temporada ' + tempo

        if len(seasons) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, 'href="#collapse_' + str(item.contentSeason) + '(.*?)</div></div></div>')

    episodes = scrapertools.find_multiple_matches(bloque, '<li class="pm-episode(.*?)</a></li>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(episodes)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesCalidad', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesCalidad', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesCalidad', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesCalidad', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesCalidad', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesCalidad', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in episodes[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        epis = scrapertools.find_single_match(match, '<span class="identifier text-muted d-inline-flex align-items-center">.*?Capitulo(.*?)</span>').strip()
        if not epis: epis = 1

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title,
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

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    ses = 0

    for url in matches:
        ses += 1

        if '/whos.' in url: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = '', url = url, language = 'Lat' ))

    # ~ Embeds
    matches = scrapertools.find_multiple_matches(data, 'data-ms-id="(.*?)"')

    i = 0

    for embed in matches:
        ses += 1

        i += 1

        url = host + 'episode-player.php?id=560&ms_id=' + embed

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = 'Lat', other = str(i) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    data = do_downloadpage(url)

    new_url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="(.*?)"')
    if not new_url: new_url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')

    if not new_url: new_url = scrapertools.find_single_match(data, 'player.src.*?src:.*?"(.*?)"')

    if new_url: url = new_url

    if '/lanseries.' in url: url = ''
    elif 'player.php?id=' in url: url = ''

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if not new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'search.php?keywords=' + texto.replace(" ", "+") + '&video-id='
       return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

