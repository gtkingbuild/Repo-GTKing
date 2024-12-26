# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://cinemitas.org/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www3.pelisplus.uno/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if '/release/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>Bot Verification</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] reCAPTCHA[/B][/COLOR]')
        return ''

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'genre/peliculas-mas-vistas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catalogo', action = 'list_all', url = host + 'tvshows/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    if item.search_type == 'movie':
        itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'genre/peliculas-castellano/', search_type = 'movie', text_color=text_color ))
        itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'genre/peliculas-espanol-latino/', search_type = 'movie', text_color=text_color ))
        itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'genre/peliculas-subtituladas/', search_type = 'movie', text_color=text_color ))
    else:
        itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'genre/series-castellano', search_type = 'tvshow', text_color=text_color ))
        itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'genre/series-espanol-latino/', search_type = 'tvshow', text_color=text_color ))
        itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'genre/series-subtituladas/', search_type = 'tvshow', text_color=text_color ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
        text_color = 'deepskyblue'
        url_gen = host + 'movies/'
    else:
        text_color = 'hotpink'
        url_gen = host + 'tvshows/'

    data = do_downloadpage(url_gen)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque,'<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if item.search_type == 'movie':
            if 'Peliculas ' in title: continue
            elif 'Series ' in title: continue

        elif item.search_type == 'tvshow':
            if title == 'Película de TV': continue
            elif 'Series ' in title: continue
            elif 'Peliculas ' in title: continue

        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( title = title, url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1969, -1):
        url = host + 'release/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color='deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '>Añadido recientemente<' in data: bloque = scrapertools.find_single_match(data,'>Añadido recientemente<(.*?)<div class="copy">')
    elif '</h1>' in data: bloque = scrapertools.find_single_match(data,'</h1>(.*?)<div class="copy">')
    else: bloque = data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, 'src="(.*?)"')

        year = scrapertools.find_single_match(article, '<span class="imdb">.*?<span>(.*?)</span>')

        if year: title = title.replace('(' + year + ')' , '').strip()
        else: year ='-'

        title = title.replace('&#8217;s', "'s").replace('&#038;', '&').replace('&#8211;', '')

        if '/release/' in item.url: year = scrapertools.find_single_match(item.url, "/release/(.*?)/")

        tipo = 'tvshow' if '/tvshows/' in url else 'movie'

        if tipo == 'movie':
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">' + ".*?<a href='(.*?)'")
            if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data,'>Añadido recientemente<(.*?)<div class="copy">')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, 'src="(.*?)"')

        title = title.replace('&#215;', 'x')

        season = scrapertools.find_single_match(article, '</h3><span>T(.*?)E').strip()
        if not season: season = 1

        episode = scrapertools.find_single_match(article, '</h3><span>T.*?E(.*?)</span>').strip()
        if not episode: episode = 1

        contentSerieName = scrapertools.find_single_match(title, '(.*?) \d')

        tit_epi = scrapertools.find_single_match(article, '<h3>.*?">(.*?)</a>')

        titulo = str(season) + 'x' + str(episode) + ' ' + title.replace(str(season) + 'x' + str(episode), '') + ' ' + tit_epi

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSerieName=contentSerieName, contentSeason = season, contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">' + ".*?<a href='(.*?)'")
            if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'last_epis', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    temporadas = re.compile('<span class="se-t.*?">(.*?)</span>', re.DOTALL).findall(data)
    if not temporadas: temporadas = re.compile("<span class='se-t.*?'>(.*?)</span>", re.DOTALL).findall(data)

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

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<span class="se-t.*?">' + str(item.contentSeason) + '</span>(.*?)</div></div>')
    if not bloque: bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + "</span>(.*?)</div></div><")

    matches = re.compile('<li class="mark-.*?<img src="(.*?)".*?<div class="numerando">(.*?)</div>.*?<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)
    if not matches: matches = re.compile("<li class='mark-.*?<img src='(.*?)'.*?<div class='numerando'>(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>", re.DOTALL).findall(bloque)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('PeliPlusUno', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PeliPlusUno', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PeliPlusUno', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PeliPlusUno', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PeliPlusUno', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PeliPlusUno', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PeliPlusUno', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, temp_epis, url, title,in matches:
        epis = scrapertools.find_single_match(temp_epis, '.*?-(.*?)$').strip()

        if not epis: epis = 1

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, 'id="player-option-(.*?)</li>')
    if not matches: matches = scrapertools.find_multiple_matches(data, "id='player-option-(.*?)</li>")

    ses = 0

    for match in matches:
        ses += 1

        opt = scrapertools.find_single_match(match, '(.*?)"')
        if not opt: opt = scrapertools.find_single_match(match, "(.*?)'")

        if not opt: continue

        # ~ dtype, dpost, dnume
        dtype = scrapertools.find_single_match(match, ' data-type="(.*?)"')
        if not dtype: dtype = scrapertools.find_single_match(match, " data-type='(.*?)'")

        dpost = scrapertools.find_single_match(match, ' data-post="(.*?)"')
        if not dpost: dpost = scrapertools.find_single_match(match, " data-post='(.*?)'")

        dnume = scrapertools.find_single_match(match, ' data-nume="(.*?)"')
        if not dnume: dnume = scrapertools.find_single_match(match, " data-nume='(.*?)'")

        if not dtype or not dpost or not dnume: continue

        if dnume == 'trailer':
            ses = ses - 1
            continue

        post = {'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype}
        data0 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

        embed = scrapertools.find_single_match(str(data0), '"embed_url":.*?"(.*?)"')

        if 'Latino' in match or 'LATINO' in match: lang = 'Lat'
        elif 'Sub Español' in match or 'SUB ESPAÑOL' in match: lang = 'Vose'
        elif 'Castellano' in match or 'CASTELLANO' in match or 'Español' in match or 'ESPAÑOL' in match: lang = 'Esp'
        elif 'Subtitulado' in match or 'SUBTITULADO' in match or 'VOSE' in match or 'Vose' in match: lang = 'Vose'
        else: lang = '?'

        source = scrapertools.find_single_match(data, '<div id="source-player-' + str(opt) + '.*?src="(.*?)"')
        if not source: source = scrapertools.find_single_match(data, "<div id='source-player-" + str(opt) + ".*?src='(.*?)'")

        if '/links.' in source:
            data1 = do_downloadpage(source)

            links1 = scrapertools.find_multiple_matches(str(data1), '<li onclick="go_to_player' + ".*?'(.*?)'")
            links2 = scrapertools.find_multiple_matches(str(data1), '<a href="(.*?)"')

            links = links1 + links2

            for url in links:
                if '/ul.' in url: continue
                elif '/1fichier.' in url: continue
                elif '/ddownload.' in url: continue
                elif '/clk.' in url: continue
                elif '/rapidgator' in url: continue
                elif '/katfile' in url: continue
                elif '/nitro' in url: continue

                elif '/viewsb.' in url: continue
                elif '/www.fembed.' in url: continue

                url = url.replace('/player.cuevana.ac/f/', '/waaw.to/watch_video.php?v=').replace('/player.cuevana3.one/f/', '/waaw.to/watch_video.php?v=')

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                other = ''
                if servidor == 'various': other = servertools.corregir_other(url)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

            continue

        embed = embed.replace('\\/', '/')

        if not embed: continue

        embed = embed.replace('/player.cuevana.ac/f/', '/waaw.to/watch_video.php?v=').replace('/player.cuevana3.one/f/', '/waaw.to/watch_video.php?v=')

        servidor = servertools.get_server_from_url(embed)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, embed)

        if '/viewsb.' in url: continue
        elif '/www.fembed.' in url: continue

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    # ~ Descargas tiene acortadores

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '</h1>' in data: bloque = scrapertools.find_single_match(data,'</h1>(.*?)<div class="copy"')
    else: bloque = data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, 'src="(.*?)"')

        year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>')

        if year: title = title.replace('(' + year + ')' , '').strip()
        else: year ='-'

        title = title.replace('&#8217;s', "'s").replace('&#038;', '&').replace('&#8211;', '')

        tipo = 'tvshow' if '/tvshows/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo = sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_search', text_color='coral' ))

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
