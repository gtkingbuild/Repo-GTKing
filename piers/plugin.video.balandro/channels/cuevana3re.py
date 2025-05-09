# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://cuevana.re/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas/estrenos', search_type = 'movie', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'series/estrenos', search_type = 'tvshow', text_color = 'cyan' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Generos(.*?)</ul>')

    matches = re.compile('<a href="(.*?)".*?>(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        url = host[:-1] + url

        itemlist.append(item.clone( title=title, url=url, action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li class="TPostMv">(.*?)</li>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'srcSet="(.*?)"')
        if thumb: host[:-1] + thumb

        title = title.replace('&#x27;s', "'s").replace('&#x27;', '').replace('&amp;#038;', '&')

        c_year = scrapertools.find_single_match(title, '(\d{4})')
        if c_year: title = title.replace('(' + c_year + ')', '').strip()

        url = host[:-1] + url

        tipo = 'movie' if '/pelicula/' in url or item.search_type == 'movie' else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            if item.search_type == 'tvshows': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            if item.search_type == 'movies': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="next page-numbers".*?.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                next_page = host[:-1] + next_page

                itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    temporadas = re.compile('<option value="(.*?)"', re.DOTALL).findall(data)

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

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    if not str(item.contentSeason) == '1':
        bloque = scrapertools.find_single_match(data, '"number":"' + str(item.contentSeason) + '"(.*?)"otherMovies"')

        matches = re.compile('"TMDbId"(.*?)"serie"', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('Cuevana3In', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Cuevana3In', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3In', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3In', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3In', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3In', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Cuevana3In', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')
        if  not title: title = scrapertools.find_single_match(match, '"title":"(.*?)"')

        if not url:
            if not str(item.contentSeason) == '1':
                num_epis = scrapertools.find_single_match(match, '"episode_number":"(.*?)"')
                if num_epis:
                    url = item.url + '/temporada/' + str(item.contentSeason) + '/episodio/' + str(num_epis)

        if not url or not title: continue

        if not host in url: url = host[:-1] + url

        season = scrapertools.find_single_match(url, '/temporada/(.*?)/')
        epis = scrapertools.find_single_match(url, '/episodio/(.*?)$')

        if not str(item.contentSeason) == str(season): continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        if thumb: host[:-1] + thumb

        titulo = str(season) + 'x' + str(epis) + ' ' + title.replace(str(season) + 'x' + str(epis), '').strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber=epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Latino': 'Lat', 'Español Latino': 'Lat', 'Español': 'Esp', 'Castellano': 'Esp', 'Subtitulado': 'Vose', 'Latino/Inglés': 'Vose'}

    data = do_downloadpage(item.url)

    ses = 0

    # ~ Latino

    bloque = scrapertools.find_single_match(data, '<span>Español Latino </span>(.*?)</ul></div></li>')
    if not bloque: bloque = scrapertools.find_single_match(data, '<span>Latino </span>(.*?)</ul></div></li>')

    matches = re.compile('data-tr="(.*?)"', re.DOTALL).findall(bloque)

    lang = 'Lat'

    for url in matches:
        if not url: continue

        ses += 1

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''

        if servidor == 'various':
            other = servertools.corregir_other(url)

        if lang == other.lower() or lang == servidor: lang = ''

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other )) 

    # ~ Español

    bloque = scrapertools.find_single_match(data, '<span>Español </span>(.*?)</ul></div></li>')
    if not bloque: bloque = scrapertools.find_single_match(data, '<span>Castellano </span>(.*?)</ul></div></li>')

    matches = re.compile('data-tr="(.*?)"', re.DOTALL).findall(bloque)

    lang = 'Esp'

    for url in matches:
        if not url: continue

        ses += 1

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''

        if servidor == 'various':
            other = servertools.corregir_other(url)

        if lang == other.lower() or lang == servidor: lang = ''

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other )) 

    # ~ Subtitulado

    bloque = scrapertools.find_single_match(data, '<span>Subtitulado </span>(.*?)</ul></div></li>')
    if not bloque: bloque = scrapertools.find_single_match(data, '<span>Latino/Inglés </span>(.*?)</ul></div></li>')

    matches = re.compile('data-tr="(.*?)"', re.DOTALL).findall(bloque)

    lang = 'Vose'

    for url in matches:
        if not url: continue

        ses += 1

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''

        if servidor == 'various':
            other = servertools.corregir_other(url)

        if lang == other.lower() or lang == servidor: lang = ''

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other )) 


    # ~ Downloads
    matches = re.compile('<span class="Num">.*?</span> <!-- -->(.*?)</td>.*?<td>(.*?)</td>.*?<span>(.*?)</span>.*?href="(.*?)"', re.DOTALL).findall(data)

    for srv, lang, qlty, url in matches:
        if not url: continue

        ses += 1

        url = host[:-1] + url

        srv = srv.lower().strip()

        servidor = 'directo'

        if '1fichier' in srv: continue

        elif srv == 'bittorrent':
           servidor = 'torrent'
           srv = ''
        elif 'megaup' in srv:
           servidor = 'megaup'
           srv = ''
        elif 'mega' in srv:
           servidor = 'mega'
           srv = ''
        elif 'mediafire' in srv:
           servidor = 'mediafire'
           srv = ''

        lang = IDIOMAS.get(lang, lang)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url=url, server=servidor, quality=qlty, language=lang, other=srv )) 

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.server == 'directo' or '/redirect?' in item.url:
        new_url = scrapertools.find_single_match(item.url, "url=(.*?)$")

        if new_url:
            new_url = base64.b64decode(new_url).decode("utf-8")

            url = new_url

    if '/pelispng.' in url: url = ''
    elif '/watchsb.' in url: url= ''
    elif '/sbfast.' in url: url = ''

    if url:
        if '/plustream.' in url:
            return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    itemlist1 = []
    itemlist2 = []

    try:
        if item.search_type != 'all':
            item.url = host + 'search?q=' + texto.replace(" ", "+")
            return list_all(item)
        else:
            item.search_type = 'movies'
            item.url = host + 'search?q=' + texto.replace(" ", "+")
            itemlist1 = list_all(item)

            if not itemlist1:
                item.search_type = 'tvshows'
                item.url = host + 'search?q=' + texto.replace(" ", "+")
                itemlist2 = list_all(item)

            itemlist = itemlist1 + itemlist2
            return itemlist
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

