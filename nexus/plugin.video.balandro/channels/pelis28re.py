# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ver.pelis28.net/'


def do_downloadpage(url, post=None, headers=None):
    if not headers:
       if '/genero/'in url: headers = {'Referer': url}

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'genero/peliculas-mas-vistas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    if item.search_type == 'movie':
        itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'genero/castellano/', search_type = 'movie', text_color = text_color ))
        itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'genero/latino/', search_type = 'movie', text_color = text_color ))
        itemlist.append(item.clone( title = 'En inglés', action = 'list_all', url = host + 'genero/ingles/', search_type = 'movie', text_color = text_color ))
        itemlist.append(item.clone( title = 'Subtituladas', action = 'list_all', url = host + 'genero/subtituladas/', search_type = 'movie', text_color = text_color ))

        itemlist.append(item.clone( title = 'Otros', action = 'list_all', url = host + 'genero/peliculas-en-ingles/', search_type = 'movie', text_color = text_color ))
    else:
        itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'genero/series-en-castellano/', search_type = 'tvshow', text_color = text_color ))
        itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'genero/series-audio-latino/', search_type = 'tvshow', text_color = text_color ))
        itemlist.append(item.clone( title = 'Subtituladas', action = 'list_all', url = host + 'genero/series-subtituladas/', search_type = 'tvshow', text_color = text_color ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if item.search_type == 'movie':
            if '/series-' in url: continue

            elif '/peliculas-mas-vistas/' in url: continue

            elif '/genero/latino/' in url: continue
            elif '/genero/castellano/' in url: continue
            elif '/genero/ingles/' in url: continue
            elif '/genero/peliculas-en-ingles/' in url: continue
            elif '/genero/subtituladas/' in url: continue

            elif '/genero/reality/' in url: continue
            elif '/genero/soap/' in url: continue
        else:
            if '/peliculas-' in url: continue
            elif '/pelicula-' in url: continue

            elif '/series-' in url: continue

            elif '/genero/latino/' in url: continue
            elif '/genero/castellano/' in url: continue
            elif '/genero/ingles/' in url: continue
            elif '/genero/subtituladas/' in url: continue

            elif '/genero/cinecalidad-' in url: continue
            elif '/genero/repelisplus-' in url: continue

        title = title.replace('&amp;', '&')

        title = title.lower()

        title = title.capitalize()

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1981, -1):
        url = host + 'peliculas/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)<div class="copy">')
    if not bloque: bloque = scrapertools.find_single_match(data, '>Resultados(.*?)<div class="copy">')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<h3 class="title">(.*?)</h3>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '</h3></pan>(.*?)</span>')

        if year: title = title.replace('(', year + ')').strip()
        else: year = '-'

        title = title.replace('&#8217;', "'").replace('&#8211;', '').strip()

        title = title.replace('Ver ', '').replace('ver ', '').replace(' Online', '').replace(' online', '').replace(' Serie', '').replace(' serie', '').strip()

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?</a>.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<div class="se-q">.*?">(.*?)</span>')

    for nro_season in matches:
        title = 'Temporada ' + nro_season

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = nro_season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = nro_season, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    season = scrapertools.find_single_match(data, '<div class="se-c">.*?<span class="se-t.*?">' + str(item.contentSeason) + '(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(season, '<li class="mark-(.*?)</li>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Pelis28Re', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Pelis28Re', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Pelis28Re', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Pelis28Re', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Pelis28Re', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Pelis28Re', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        epis = scrapertools.find_single_match(match, '<div class="numerando">(.*?)</div>')

        nro_epi = scrapertools.find_single_match(epis, '-(.*?)$').strip()

        title = scrapertools.find_single_match(match, '<div class="episodiotitle">.*?">(.*?)</a>')

        title = title.replace('&#8217;', "'").replace('&#8211;', '').strip()

        title = title.replace('Ver ', '').replace('ver ', '').replace(' Online', '').replace(' online', '').replace(' Serie', '').replace(' serie', '').strip()

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

    matches = scrapertools.find_multiple_matches(data, '<li id="player-option-(.*?)<span class="loader">')

    ses = 0

    for match in matches:
        ses += 1

        d_type = scrapertools.find_single_match(match, 'data-type="(.*?)"')
        d_post = scrapertools.find_single_match(match, 'data-post="(.*?)"')
        d_nume = scrapertools.find_single_match(match, 'data-nume="(.*?)"')

        if not d_type or not d_post or not d_nume: continue

        if d_nume == 'trailer': continue

        data1 = do_downloadpage(host + 'wp-json/dooplayer/v2/' + d_post + '/' + d_type + '/' + d_nume)

        lnk = scrapertools.find_single_match(data1, '"embed_url":.*?"(.*?)"')

        lnk = lnk.replace('\\/', '/')

        if '<iframe' in lnk:
            lnk = scrapertools.find_single_match(str(data1), '<iframe.*?src=.*?"(.*?)"')

            lnk = lnk.replace('\\/', '/')

        if not lnk: continue

        if '/media.esplay.one' in lnk: continue

        vid = scrapertools.find_single_match(lnk, '/video/(.*?)$')

        if item.contentType == 'episode':
            if not vid:
                if '.novercine.' in lnk: continue
                elif '.cuevana3.' in lnk: continue
                elif '-ukr-' in lnk: continue

                servidor = servertools.get_server_from_url(lnk)
                servidor = servertools.corregir_servidor(servidor)

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                    if not config.get_setting('developer_mode', default=False): continue

                other = ''

                if servidor == 'various': other = servertools.corregir_other(lnk)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = lnk, language = 'Lat', other = other ))

                continue

        if not vid:
            if not '.xyz/' in lnk:
                if '.novercine.' in lnk: continue
                elif '.cuevana3.' in lnk: continue
                elif '-ukr-' in lnk: continue

                servidor = servertools.get_server_from_url(lnk)
                servidor = servertools.corregir_servidor(servidor)

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                    if not config.get_setting('developer_mode', default=False): continue

                other = ''

                if servidor == 'various': other = servertools.corregir_other(lnk)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = lnk, language = 'Lat', other = other ))

                continue

        data2 = do_downloadpage('https://streamsito.net/video/' + vid)

        options = scrapertools.find_multiple_matches(data2, '<li onclick="go_to_player(.*?)</li>')

        for option in options:
            ses += 1

            if 'data-lang="2"' in option: lang = 'Vose'
            elif 'data-lang="0"' in option: lang = 'Lat'
            elif 'data-lang="1"' in option: lang = 'Esp'
            else: lang = '?'

            url = scrapertools.find_single_match(str(option), "'(.*?)'")

            if '/embedsito.' in url:
               data3 = do_downloadpage(url)
               data3 = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

               url = scrapertools.find_single_match(data1, '<a href="(.*?)"')

            if '.novercine.' in url: continue
            elif '.cuevana3.' in url: continue
            elif '-ukr-' in url: continue

            if not url: continue
            elif '/1fichier.' in url: continue
            elif '/short.' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            other = ''

            if servidor == 'various': other = servertools.corregir_other(url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

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

