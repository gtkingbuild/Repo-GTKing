# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import re

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://pasateatorrent.org/'

# ~  03/2022 algunas series No hay enlaces
# ~  04/2022 algunas pelis salta Recaptcha


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://pasateatorrent.net/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not headers: headers = {'Referer': host}

    if '/categoria/' in url: raise_weberror = False

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    opciones = {
        'accion': 'Acción',
        'animacion': 'Animación',
        'aventura': 'Aventura',
        'biografia': 'Biografía',
        'ciencia-ficcion': 'Ciencia ficción',
        'comedia': 'Comedia',
        'crimen': 'Crimen',
        'deporte': 'Deporte',
        'documental': 'Documental',
        'drama': 'Drama',
        'familia': 'Familia',
        'fantasia': 'Fantasía',
        'guerra': 'Guerra',
        'historia': 'Historia',
        'misterio': 'Misterio',
        'musica': 'Música',
        'romance': 'Romance',
        'suspense': 'Suspense',
        'terror': 'Terror',
        'western': 'Western'
        }

    for opc in sorted(opciones):
        itemlist.append(item.clone( title=opciones[opc], url=host + 'categoria/' + opc + '/', action='list_all', text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1949, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'categoria/' + str(x) + '/', action = 'list_all', text_color = text_color ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='En 4K', url=host + 'categoria/4k-2/', action='list_all', text_color='moccasin' ))
    itemlist.append(item.clone( title='En BluRay', url=host + 'categoria/BluRay-1080p/', action='list_all', text_color='moccasin' ))
    itemlist.append(item.clone( title='En Dvd Rip', url=host + 'categoria/dvdrip/', action='list_all', text_color='moccasin' ))
    itemlist.append(item.clone( title='En HD Rip', url=host + 'categoria/HDRip-2/', action='list_all', text_color='moccasin' ))
    itemlist.append(item.clone( title='En Micro HD', url=host + 'categoria/MicroHD-1080p/', action='list_all', text_color='moccasin' ))
    itemlist.append(item.clone( title='En 3D', url=host + 'categoria/3D/', action='list_all', text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="imagen-post">(.*?)<div class="bloque-date">')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, '<div class="bloque-inferior">(.*?)</div>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        lang = scrapertools.find_single_match(match, '<div class="imagen-idioma">.*?/icono_(.*?).png')
        if lang == 'espaniol': lang = 'Esp'

        qlty = scrapertools.find_single_match(match, '<div class="bloque-superior">(.*?)<div')

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            title = title.replace('&#8211;', '').strip()

            if " Temporada" in title: SerieName = title.split(" Temporada ")[0]
            else: SerieName = title

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, languages = lang, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = lang, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<nav class="navigation pagination".*?class="page-numbers current">.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')

    matches = scrapertools.find_multiple_matches(bloque, '<tr class="lol">.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?href="(.*?)"')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PasateaTorrent', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PasateaTorrent', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PasateaTorrent', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PasateaTorrent', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PasateaTorrent', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PasateaTorrent', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for temp_epis, qlty, url in matches[item.page * item.perpage:]:
        temp_epis = temp_epis.replace('&#215;', 'x')

        if 'completa' in temp_epis.lower():
            season = 99
            episode = 99
        else:
           season = scrapertools.find_single_match(temp_epis, '(.*?)x').strip()
           episode = scrapertools.find_single_match(temp_epis, 'x(.*?)$').strip()

           if '(Especial' in episode:
               episode = episode.split("(Especial")[0]
               episode = episode.strip()
           elif 'Final' in episode:
               episode = episode.split("Final")[0]
               episode = episode.strip()
           elif '(Contraseña' in episode:
               episode = episode.split("(Contraseña")[0]
               episode = episode.strip()

        if "Temporada" in item.contentSerieName: SerieName = item.contentSerieName.split("Temporada")[0]
        else: SerieName = item.contentSerieName

        title = SerieName

        titulo = '%sx%s %s' % (season, episode, title)

        if url.startswith("/"): url = host[:-1] + url

        itemlist.append(item.clone( action = 'findvideos', title = titulo, url = url, quality = qlty,
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    lang = 'Esp'

    if '/download_tt.php?'in item.url:
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = item.url, server = 'torrent', language = lang, other = 'D' ))
        return itemlist

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<tbody>.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?href="(.*?)"', re.DOTALL).findall(data)

    for qlty, peso, url in matches:
        if not url.startswith('http'): url = host[:-1] + url

        other = peso.replace('&#8230;', '').strip()

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = lang, quality = qlty, other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if PY3:
        from core import requeststools
        data = requeststools.read(item.url, '')
    else:
        data = do_downloadpage(item.url)

    if data:
        if '<meta name="captcha-bypass" id="captcha-bypass"' in str(data):
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        if '<h1>404 Not Found</h1>' in str(data) or '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data) or '<!doctype' in str(data):
            return 'Archivo [COLOR red]Inexistente[/COLOR]'

        elif 'Página no encontrada</title>' in str(data) or 'no encontrada</title>' in str(data) or '<h1>403 Forbidden</h1>' in str(data):
            return 'Archivo [COLOR red]No encontrado[/COLOR]'

        import os

        file_local = os.path.join(config.get_data_path(), "temp.torrent")
        with open(file_local, 'wb') as f: f.write(data); f.close()

        itemlist.append(item.clone( url = file_local, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.search_type == 'tvshow':
            item.url = host + '/series/?s=' + texto.replace(" ", "+")
        else:
            item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
