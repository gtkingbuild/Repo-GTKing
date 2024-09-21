# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.cuevana3.in/'


perpage = 25


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www1.cuevana3.in/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

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

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)".*?>(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        url = host[:-1] + url

        itemlist.append(item.clone( title=title, url=url, action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))

    if itemlist:
        itemlist.append(item.clone( title='Guerra', url=host + 'category/guerra', action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title='Infantil', url=host + 'category/infantil', action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title='Suspense', url=host + 'category/suspense', action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title='Western', url=host + 'category/western', action='list_all', search_type = item.search_type, text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li class="TPostMv">(.*?)</li>', re.DOTALL).findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        if thumb: thumb = 'https:' + thumb

        url = host[:-1] + url

        tipo = 'movie' if '/peliculas' in item.url or item.search_type == 'movie' else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if not sufijo:
            if item.search_type == 'tvshow': tipo = 'tvshow'

            if item.search_type == 'movies':
                tipo = 'movie'
                sufijo = 'movie'

            if item.search_type == 'tvshows':
               tipo = 'tvshow'
               sufijo = 'tvshow'

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

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?<a href="(.*?)"')

            if next_page:
                next_page = host[:-1] + next_page

                itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('<option value=".*?>Temporada (.*?)</option>', re.DOTALL).findall(data)

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

    bloque = scrapertools.find_single_match(str(data), '<ul id="season-' + str(item.contentSeason) + '(.*?)</ul>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
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

        if not url or not title: continue

        url = host[:-1] + url

        epis = scrapertools.find_single_match(url, '/episodio/.*?/.*?/(.*?)$')

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

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

    IDIOMAS = {'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    matches = re.compile('<li data-video="(.*?)".*?<span>(.*?)</span>', re.DOTALL).findall(data)

    ses = 0

    for url, lang_srv in matches:
        ses += 1

        lang = ''

        if ' - ' in lang_srv: lang = scrapertools.find_single_match(lang_srv, '.*?-(.*?)-').strip()

        if url.startswith('//'): url = 'https:' + url

        if '/play?id=' in url or '/streamhd?id=' in url:
           data2 = do_downloadpage(url)

           matches2 = scrapertools.find_multiple_matches(data2, '<li class="linkserver".*?data-video="(.*?)"')

           for match in matches2:
               servidor = servertools.get_server_from_url(match)
               servidor = servertools.corregir_servidor(servidor)

               other = ''

               if servidor == 'various': other = servertools.corregir_other(match)

               if not servidor == 'directo':
                   itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = match,
                                         server = servidor, language = IDIOMAS.get(lang, lang), other = other ))

           continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''

        if 'HD' in lang:
            other = scrapertools.find_single_match(lang, 'HD.*?(.*?)$').strip()
            lang = '?'

        elif '. ' in lang:
            other = scrapertools.find_single_match(lang, '(.*?). ').strip()
            lang = '?'

        new_server = ''

        if servidor == 'directo':
            if lang == '?': new_server = scrapertools.find_single_match(lang_srv, '. (.*?) -').strip()
            elif not lang in str(IDIOMAS):
               new_server = lang
               lang = '?'
            else: new_server = scrapertools.find_single_match(lang, '. (.*?)').strip()

            if new_server:
                if new_server == 'plustream': new_server = 'directo'
                else: servidor = servertools.corregir_servidor(new_server)

        if servidor == 'various':
            if new_server: other = servertools.corregir_other(new_server)
            else: other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url,
                              server = servidor, language = IDIOMAS.get(lang, lang), other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.server == 'directo' or '/player.php?' in item.url:
        data = do_downloadpage(url)

        new_url = scrapertools.find_single_match(data, "var url = '(.*?)'")

        if new_url: url = new_url

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
            if not new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    itemlist1 = []
    itemlist2 = []

    try:
        if item.search_type != 'all':
            item.url = host + 'search/' + texto.replace(" ", "+")
            return list_all(item)
        else:
            item.search_type = 'movies'
            item.url = host + 'search/' + texto.replace(" ", "+")
            itemlist1 = list_all(item)

            item.search_type = 'tvshows'
            item.url = host + 'search/' + texto.replace(" ", "+")
            itemlist2 = list_all(item)

            itemlist = itemlist1 + itemlist2
            return itemlist
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

