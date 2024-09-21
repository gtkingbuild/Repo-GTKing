# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://dangotoons.com/'


perpage = 25


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://dangotoons.net/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'catalogo.php', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistas', action ='list_all', url = host + 'catalogo.php?t=todos&o=1', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action ='list_all', url = host + 'catalogo.php?t=todos&o=2', search_type = 'tvshow' ))

    if not config.get_setting('descartar_anime', default=False):
        itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'catalogo.php?t=anime', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Dibujos animados', action = 'list_all', url = host + 'catalogo.php?t=series-animadas', search_type = 'tvshow', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Live action', action ='list_all', url = host + 'catalogo.php?t=series-actores', search_type = 'tvshow', text_color='yellowgreen' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'catalogo.php?t=peliculas', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + 'catalogo.php?t=especiales', search_type = 'tvshow', text_color = 'thistle' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por título (A - Z)', action = 'list_all', url = host +  'catalogo.php?t=todos&o=3', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host  + 'catalogo.php')

    bloque = scrapertools.find_single_match(data, '<select name="g">(.*?)<select name="o">')

    matches = re.compile('<option value="(.*?)">(.*?)</option>').findall(bloque)

    for gen, tit in matches:
        url = host + 'catalogo.php?t=todos&g=' + gen

        itemlist.append(item.clone( title = tit, action = 'list_all', url = url, text_color = 'hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<div class="listados">(.*?)<footer>')

    matches = re.compile('<div class="serie">(.*?)<br></div>', re.DOTALL).findall(bloque)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for match in matches[desde:hasta]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'class="titulo">(.*?)</p>')

        if not url or not title: continue

        if url.startswith('/'): url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        if '/pelicula/' in url or '/especial/' in url:
            itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))
        else:
            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb,  contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title='Siguientes ...', page = item.page + 1, action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<div class="titulo">Temporada(.*?)<br>')

    if not matches:
        if '>LISTA DE CAPITULOS<' in data:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR tan] sin Temporadas[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = 0
            itemlist = episodios(item)
            return itemlist

    for temp in matches:
        temp = temp.strip()

        title = 'Temporada ' + temp

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = temp
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action='episodios', title = title, page = 0, contentType = 'season', contentSeason = temp, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    if item.contentSeason == 0:
        bloque = scrapertools.find_single_match(data, '<div class="cajaCapitulos">(.*?)</ul></div>')
    else:
       bloque = scrapertools.find_single_match(data, '<div class="titulo">Temporada ' + item.contentSeason + '(.*?)</div></div>')

    matches = scrapertools.find_multiple_matches(bloque, "<li>(.*?)</li>")

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DangoToons', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DangoToons', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DangoToons', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DangoToons', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DangoToons', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DangoToons', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    i = 0

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<a href=".*?">(.*?)</a>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        season = item.contentSeason
        if item.contentSeason == 0: season = 1

        epis = scrapertools.find_single_match(title, 'Capítulo:(.*?)-').strip()
        if not epis:
            i += 1
            epis = i

        itemlist.append(item.clone( action='findvideos', url= host + url, title = title, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

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

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    url_videos = scrapertools.find_single_match(data, 'var q = \[ \[(.+?)\] \]')

    matches = scrapertools.find_multiple_matches(url_videos, '"(.+?)"')

    ses = 0

    for url in matches:
        ses += 1

        url = url.replace('\/', '/')

        if '/goo.' in url: continue

        if url.startswith('//'): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, language = 'Lat', title = '', url = url ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def sub_search(item):
    logger.info()
    itemlist = []

    post = 'b=' + item.tex

    data = do_downloadpage(item.url, post=post)

    matches = scrapertools.find_multiple_matches(data, "<a href='(.*?)'>(.*?)</a>")

    for url, title in matches:
        tipo = 'movie' if '/pelicula/' in url or '/especial/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url = url, title = title, fmt_sufijo=sufijo, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

        if tipo == 'tvshow':
            itemlist.append(item.clone( action='temporadas', url = url, title = title, fmt_sufijo=sufijo, contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.tex = texto.replace(" ", "+")
        item.url = host + 'php/buscar.php'
        return sub_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
