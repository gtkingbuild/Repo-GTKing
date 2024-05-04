# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.doramasyt.com/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'doramas?categoria=pelicula', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'doramas?categoria=dorama', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Episodios recientes', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Live action', action = 'list_all', url = host + 'doramas?categoria=live-action', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'emision', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'firebrick'

    genres = [
       ['policial', 'Policial'],
       ['romance', 'Romance'],
       ['comedia', 'Comedia'],
       ['escolar', 'Escolar'],
       ['accion', 'Acción'],
       ['thriller', 'Thriller'],
       ['drama', 'Drama'],
       ['misterio', 'Misterio'],
       ['fantasia', 'Fantasía'],
       ['historico', 'Histórico'],
       ['belico', 'Bélico'],
       ['militar', 'Militar'],
       ['medico', 'Médico'],
       ['ciencia-ficcion', 'Ciencia Ficción'],
       ['sobrenatural', 'Sobrenatural'],
       ['horror', 'Horror'],
       ['politica', 'Política'],
       ['familiar', 'Familiar'],
       ['melodrama', 'Melodrama'],
       ['deporte', 'Deporte'],
       ['comida', 'Comida'],
       ['supervivencia', 'Supervivencia'],
       ['aventuras', 'Aventuras'],
       ['artes-marciales', 'Artes marciales'],
       ['recuentos-de-la-vida', 'Recuentos de la vida'],
       ['amistad', 'Amistad'],
       ['psicologico', 'Psicológico'],
       ['yuri', 'Yuri'],
       ['k-drama', 'K-Drama'],
       ['j-drama', 'J-Drama'],
       ['c-drama', 'C-Drama'],
       ['hk-drama', 'HK-Drama'],
       ['tw-drama', 'TW-Drama'],
       ['thai-drama', 'Thai-Drama'],
       ['idols', 'Idolos'],
       ['suspenso', 'Suspenso'],
       ['negocios', 'Negocios'],
       ['time-travel', 'Time Travel'],
       ['crimen', 'Crimen '],
       ['yaoi', 'Yaoi'],
       ['legal', 'Legal'],
       ['juvenil', 'Juvenil'],
       ['musical', 'Musical'],
       ['reality-show', 'Reality Show'],
       ['documental', 'Documental']
       ]

    if item.search_type == 'movie':
        url_gen = host + 'doramas?categoria=pelicula&genero='
    else:
        url_gen = host + 'doramas?categoria=dorama&genero='

    for genero in genres:
        url = url_gen + genero[0]

        itemlist.append(item.clone( title = genero[1], action = 'list_all', url = url, text_color = text_color ))

    return sorted(itemlist, key=lambda i: i.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie': url_any = host + 'doramas?categoria=pelicula&fecha='
    else: url_any = host + 'doramas?categoria=dorama&fecha='

    for x in range(current_year, 1981, -1):
        url = url_any + str(x)

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)>DoramasYT')

    matches = re.compile('<div class="col-lg-2 col-md-4 col-6">(.*?)</div></div>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<p>(.*?)</p>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if 'latino' in title.lower(): lang = 'Lat'
        elif 'castellano' in title.lower(): lang = 'Esp'
        else: lang = 'Vose'

        title = re.sub(r'Audio|Latino|Castellano|\((.*?)\)', '', title)
        title = re.sub(r'\s:', ':', title)

        title = title.replace('&#039;', '')

        if '<button class="btnone">Pelicula</button>' in match:
            tipo = 'movie' if '<button class="btnone">Pelicula</button>' in match else 'tvshow'
        else: tipo = item.search_type

        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, languages = lang, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, languages = lang, fmt_sufijo=sufijo, 
                                        contentSerieName = title, contentType = 'tvshow', contentSeason = 1, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination">' in data:
            bloque = scrapertools.find_single_match(data, '<ul class="pagination">(.*?)</nav>')

            next_url = scrapertools.find_single_match(bloque, '<li class="page-item active".*?href="(.*?)"')

            if next_url:
                next_url = next_url.replace('&amp;', '&')
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = r'<div class="col-lg-3 col-md-6 col-6 chaps">.*?<a href="(.*?)".*?<img src="(.*?)".*?alt="(.*?)".*?<h3>(.*?)</h3>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, epis in matches:
        if not url or not title: continue

        title = title.replace('&#039;', '')

        title = title.strip()

        if "capitulo" in title: SerieName = title.split("capitulo")[0]
        else: titulo = SerieName

        SerieName = SerieName.strip()

        season = 1
        if not epis: epis = 0

        title = title.replace('capitulo', '[COLOR goldenrod]capitulo[/COLOR]')

        titulo = str(season) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail = thumb, url = url,
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if config.get_setting('channels_seasons', default=True):
        title = 'Sin temporadas'

        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#039;', "'").replace('&#8217;', "'"), '[COLOR tan]' + title + '[/COLOR]')

    item.page = 0
    item.contentType = 'season'
    item.contentSeason = 1
    itemlist = episodios(item)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="col-item">.*?<a href="(.*?)".*?<img src="(.*?)".*?<p>(.*?)</p>', re.DOTALL).findall(data)
    if not matches: matches = re.compile('<div class="col-item.*?<a href="(.*?)".*?<img src="(.*?)".*?<p>(.*?)</p>', re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, thumb, epis, in matches[item.page * item.perpage:]:
        epis = epis.strip()
        epis = scrapertools.find_single_match(epis, ' (.*?)$').strip()

        if not epis: continue

        if item.contentSerieName: titulo = item.contentSerieName
        else: titulo = item.contentTitle

        if item.contentType == 'movie': item.contentSeason = 1

        title = str(item.contentSeason) + 'x' + str(epis) + ' ' + titulo

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

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

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<p class="play-video" data-player="(.*?)">(.*?)</p>', re.DOTALL).findall(data)

    ses = 0

    for url, srv in matches:
        ses += 1

        srv = srv.lower()

        if 'fireload' in srv: continue

        elif 'ok' in srv: srv = 'okru'
        elif 'mixdropco' in srv: srv = 'mixdrop'

        srv = srv.replace('com/', '')

        if servertools.is_server_available(srv):
            if not servertools.is_server_enabled(srv): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        if url:
            url = base64.b64decode(url).decode("utf-8")

            servidor = servertools.corregir_servidor(srv)

            if servidor == 'various': srv = servertools.corregir_other(url)

            if not servidor == 'directo':
                if srv == servidor: srv = ''

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = srv.capitalize() ))

    # Enlaces descarga

    if '<th>DESCARGAR</th>' in data:
        bloque = scrapertools.find_single_match(data, '<th>DESCARGAR</th>(.*?)</table>')

        matches = re.compile('<td>(.*?)</td>.*?<td><a target="_blank" href="(.*?)"', re.DOTALL).findall(bloque)

        for srv, url in matches:
            ses += 1

            srv = srv.lower()

            if not srv: continue

            elif 'fireload' in srv: continue

            elif srv == 'ok': srv = 'mega'

            if servertools.is_server_available(srv):
                if not servertools.is_server_enabled(srv): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            servidor = servertools.corregir_servidor(srv)

            if not servidor == 'directo':
                if srv == servidor: srv = ''

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = srv.capitalize() + ' (D)' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if 'monoschinos' in item.url:
        data = httptools.downloadpage(item.url).data
        url = scrapertools.find_single_match(data, "file: '([^']+)'")

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

    elif '?url=' in item.url:
        url = item.url.replace(host + 'reproductor?url=', '')
        if '//videa.' in url:
            return 'Servidor [COLOR tan]Videa[/COLOR] NO Soportado'

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'buscar?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
