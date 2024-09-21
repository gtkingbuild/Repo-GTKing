# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://mitorrent.mx/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://mitorrent.org/', 'https://mitorrent.eu/', 'https://mitorrent.me/']


domain = config.get_setting('dominio', 'mitorrent', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'mitorrent')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'mitorrent')
    else: host = domain


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post).data
    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'mitorrent', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_mitorrent', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='mitorrent', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_mitorrent', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<select id="tax_masopciones"(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque, '<option value="(.*?)">(.*?)</option>')

    url_idio = host + 'search-result/?search_query=&audio='

    for value, title in matches:
        if title == 'todos': continue

        url = url_idio + value

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color='moccasin' ))

    return sorted(itemlist,key=lambda x: x.title)


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<select id="tax_calidad"(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque, '<option value="(.*?)">(.*?)</option>')

    url_qlty = host + 'search-result/?search_query=&calidad='

    for value, title in matches:
        if title == 'todos': continue

        url = url_qlty + value

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color='tan' ))

    return sorted(itemlist,key=lambda x: x.title)


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    opciones = {
         'accion': 'Acción',
         'action-adventure': 'Action y Aventura',
         'animacion': 'Animación',
         'aventura': 'Aventura',
         'belica': 'Bélica',
         'ciencia-ficcion': 'Ciencia ficción',
         'comedia': 'Comedia',
         'crimen': 'Crimen',
         'documental': 'Documental',
         'drama': 'Drama',
         'familia': 'Familia',
         'fantasia': 'Fantasía',
         'historia': 'Historia',
         'kids': 'Kids',
         'misterio': 'Misterio',
         'musica': 'Música',
         'occidental': 'Occidental',
         'pelicula-de-tv': 'Película de TV',
         'romance': 'Romance',
         'sci-fi-fantasy': 'Sci-Fi y Fantasy',
         'suspense': 'Suspense',
         'suspenso': 'Suspenso',
         'terror': 'Terror',
         'war-politics': 'War y Politics',
         'western': 'Western'
         }

    for opc in sorted(opciones):
        itemlist.append(item.clone( title = opciones[opc], url = host + 'genero/' + opc + '/', action ='list_all', text_color = text_color ))

    return itemlist



def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<select id="tax_ano"(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque, '<option value="(.*?)">(.*?)</option>')

    url_any = host + 'search-result/?search_query=&dtyear='

    for value, title in matches:
        if title == 'todos': continue

        if item.search_type == 'tvshow':
            if str(title) < '2000': continue

        url = url_any + value

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title, reverse=True)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="browse-movie-wrap(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'class="browse-movie-title">(.*?)</a>')

        if '(Garantía 1 año)' in title or ' 1 año' in title: continue

        if not url or not title: continue

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<div class="browse-movie-year">(.*?)</div>')
        if not year: year = '-'

        if not year == '-':
            if ' (' in title: title = title.replace(' (' + year + ')', '').strip()
            elif ' [' in title: title = title.replace(' [' + year + ']', '').strip()

        lngs = []
        langs = scrapertools.find_multiple_matches(match, '<a rel="tag">(.*?)</a>')

        for lang in langs:
            lng = ''

            if lang == 'espanol' or lang == 'castellano': lng = 'Esp'
            if lang == 'latino': lng = 'Lat'

            if lng:
               if not lng in str(lngs): lngs.append(lng)

        tipo = 'movie' if '/peliculas/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = ', '.join(lngs), fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
               if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, languages = ', '.join(lngs), fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="tsc_pagination">' in data:
            next_url = scrapertools.find_single_match(data, '<div class="tsc_pagination">.*?class="page-numbers current">.*?href="(.*?)"')

            if next_url:
                if '/page/' in next_url:
                    itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    temporadas = re.compile('<div class="accordion active">(.*?)</div>', re.DOTALL).findall(data)

    for tempo in temporadas:
        season = scrapertools.find_single_match(tempo, '(.*?)<a').strip()
        season = season.replace('Temporada', '').strip()

        url = scrapertools.find_single_match(tempo, 'href="(.*?)"')

        title = 'Temporada ' + season

        if len(temporadas) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.url = url
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, page = 0, contentType = 'season', contentSeason = season, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    link = scrapertools.find_single_match(data, '<form action="(.*?)"')
    if not link: link = scrapertools.find_single_match(data, '<a target="_blank".*?href="(.*?)"')

    if not link:
        if '/s.php?' in item.url: link = item.url

    if link:
        link = link.replace('https://short-link.one/#', 'https://short-link.one/s.php?i=')

        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(link, host_torrent)

        data = do_downloadpage(url_base64)

    matches = re.compile('<li>.*?Descargar Capitulo(.*?)<a.*?href="(.*?)"', re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('MiTorrent', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MiTorrent', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MiTorrent', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MiTorrent', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MiTorrent', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('MiTorrent', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for epis, url in matches[item.page * item.perpage:]:
        episode = epis.strip()

        titulo = str(item.contentSeason) + 'x' + str(episode)+ ' ' + item.contentSerieName

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = episode ))

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

    accion = ''
    if item.url.startswith('magnet:'): accion = 'play'
    elif item.url.endswith(".torrent"): accion = 'play'

    if accion == 'play':
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = item.url, server = 'torrent', language = item.languages, quality = item.qualities))
        return itemlist

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, 'target="_blank".*?href="(.*?)"')

    for link in links:
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = link, server = 'torrent', language = item.languages, quality = item.qualities))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith(".torrent"):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    else:
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(url, host_torrent)

        if url_base64.startswith('magnet:'):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

        elif url_base64.endswith(".torrent"):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

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
