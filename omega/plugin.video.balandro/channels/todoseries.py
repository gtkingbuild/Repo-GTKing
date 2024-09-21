# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://todoserieshd.net/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/release/' in url: raise_weberror = False

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catalogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + 'episodios/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'Generos<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque,'<a href="(.*?)".*?</i>(.*?)</a>')

    for url, title in matches:
        title = title.replace('&#038;', '&')

        itemlist.append(item.clone( title = title, url = url, action = 'list_all', text_color = text_color ))

    if itemlist:
        if item.search_type == 'movie':
            itemlist.append(item.clone( title = 'Western', url = host + 'generos/western/', action = 'list_all', text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def plataformas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Plataforma<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque,'<a href="(.*?)".*?</i>(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( title = title, url = url, action = 'list_all', text_color= 'hotpink' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1959, -1):
        url = host + 'release/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color='deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '>Añadido recientemente<' in data: bloque = scrapertools.find_single_match(data,'>Añadido recientemente<(.*?)</aside>')
    elif '</h1>' in data: bloque = scrapertools.find_single_match(data,'</h1>(.*?)</aside>')
    else: bloque = data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, 'data-lazy-src="(.*?)"')

        title = title.replace('&#8217;s', "'s").replace('&#8211;', '').strip()

        year = '-'

        if '/release/' in item.url: year = scrapertools.find_single_match(item.url, "/release/(.*?)/")

        tipo = 'tvshow' if '/series/' in url else 'movie'

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
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "<a href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data,'>Añadido recientemente<(.*?)</aside>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, 'data-lazy-src="(.*?)"')

        title = title.replace('&#215;', 'x')

        season = scrapertools.find_single_match(article, '</h3><span>T(.*?)E')
        if not season: season = 1

        episode = scrapertools.find_single_match(article, '</h3><span>T.*?E(.*?)/').strip()
        if not episode: episode = 1

        contentSerieName = scrapertools.find_single_match(title, '(.*?) \d')

        tit_epi = scrapertools.find_single_match(article, '<h3>.*?">(.*?)</a>')

        titulo = title + ' ' + tit_epi

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSerieName=contentSerieName, contentSeason = season, contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'last_epis', text_color='coral' ))

    return itemlist

def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    temporadas = re.compile("<span class='se-t.*?'>(.*?)</span>", re.DOTALL).findall(data)

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

    bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + '</span>(.*?)</div></div>')

    patron = "<li class='mark-.*?" + 'data-lazy-src="(.*?)".*?' + "<div class='numerando'>(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>"

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('TodoSeries', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TodoSeries', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TodoSeries', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TodoSeries', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TodoSeries', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('TodoSeries', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
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

    matches = scrapertools.find_multiple_matches(data, "id='player-option-(.*?)</li>")

    ses = 0

    for match in matches:
        ses += 1

        # ~ dtype, dpost, dnume
        dtype = scrapertools.find_single_match(match, " data-type='(.*?)'")
        dpost = scrapertools.find_single_match(match, " data-post='(.*?)'")
        dnume = scrapertools.find_single_match(match, " data-nume='(.*?)'")

        if dtype and dpost and dnume:
            post = {'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype}

            data1 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

            embed = scrapertools.find_single_match(str(data1), '"embed_url":.*?"(.*?)"')

            if embed:
                if '<IFRAME SRC=' in embed or '<iframe src=' in embed:
                    data1 = data1.replace('=\\', '=').replace('\\"', '/"')

                    embed = scrapertools.find_single_match(str(data1), '<IFRAME.*?SRC="(.*?)"')
                    if not embed: embed = scrapertools.find_single_match(str(data1), '<iframe.*?src="(.*?)"')
                elif '<IFRAME WIDTH=' in embed or '<iframe width=' in embed:
                    data1 = data1.replace('=\\', '=').replace('\\"', '/"')

                    embed = scrapertools.find_single_match(str(data1), '<IFRAME.*?SRC="(.*?)"')
                    if not embed: embed = scrapertools.find_single_match(str(data1), '<iframe.*?src="(.*?)"')

                if not embed: continue

                ses += 1

                if dnume == 'trailer':
                    ses = ses - 1
                    continue

                embed = embed.replace('\\/', '/')

                if '.2embed.' in embed: continue
                elif 'powvideo' in embed: continue
                elif 'streamplay' in embed or 'stre4mplay' in embed: continue

                if embed.startswith('//'): embed = 'https:' + embed

                if embed.startswith('https://vtbe.'):
                    if '/embed-' in embed: embed = embed.replace('/embed-', '/').strip()
                elif embed.startswith('https://uqload.io//'):
                    embed = embed.replace('https://uqload.io//', 'https://uqload.io/')

                servidor = servertools.get_server_from_url(embed)
                servidor = servertools.corregir_servidor(servidor)

                embed = servertools.normalize_url(servidor, embed)

                lang = scrapertools.find_single_match(match, '/flags/(.*?).png')

                if lang == 'mx': lang = 'Lat'
                elif lang == 'es': lang = 'Esp'
                elif lang == 'sub': lang = 'Vose'
                elif lang == 'en': lang = 'Vo'
                else: lang = '?'

                other = ''
                if servidor == 'various': other = servertools.corregir_other(embed)

                if not servidor == 'directo':
                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = embed, language = lang, other = other ))

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

        title = title.replace('&#8217;s', "'s").replace('&#8211;', '').strip()

        tipo = 'tvshow' if '/series/' in url else 'movie'
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
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "<a href='(.*?)'")

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
