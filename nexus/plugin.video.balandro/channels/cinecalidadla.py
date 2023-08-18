# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://cinecalidad.zip/'


players = ['https://cinecalidad.', '.cinecalidad.']


# ~ por si viene de enlaces guardados
ant_hosts = ['https://cinecalidad.la/', 'https://cinecalidad.fo/', 'https://ww22.cinecalidad.fo/',
             'https://ww3.cinecalidad.do/', 'https://ww4.cinecalidad.do/', 'https://cinecalidad.do/',
             'https://cinecalidad.llc/', 'https://cinecalidad.st/', 'https://cinecalidad.vc/',
             'https://cinecalidad.lc/', 'https://www3.cinecalidad.lc/', 'https://ww1.cinecalidad.lc/',
             'https://ww2.cinecalidad.lc/', 'https://ww4.cinecalidad.lc/', 'https://w1.cinecalidad.lc/',
             'https://w2.cinecalidad.lc/', 'https://w3.cinecalidad.lc/', 'https://w4.cinecalidad.lc/',
             'https://w5.cinecalidad.lc/', 'https://w6.cinecalidad.lc/', 'https://w7.cinecalidad.lc/',
             'https://w9.cinecalidad.lc/', 'https://w10.cinecalidad.lc/', 'https://w8.cinecalidad.lc/',
             'https://w11.cinecalidad.lc/', 'https://w13.cinecalidad.lc/', 'https://c1.cinecalidad.lc/',
             'https://w14.cinecalidad.lc/', 'https://cinecalidad.bz/', 'https://w1.cinecalidad.bz/', 
             'https://w2.cinecalidad.bz/', 'https://w3.cinecalidad.bz/', 'https://w4.cinecalidad.bz/',
             'https://w5.cinecalidad.bz/', 'https://w6.cinecalidad.bz/', 'https://w7.cinecalidad.bz/',
             'https://w8.cinecalidad.bz/', 'https://w9.cinecalidad.bz/', 'https://w10.cinecalidad.bz/',
             'https://w11.cinecalidad.bz/']


domain = config.get_setting('dominio', 'cinecalidadla', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'cinecalidadla')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'cinecalidadla')
    else: host = domain


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    raise_weberror = True
    if '/fecha/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'cinecalidadla', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_cinecalidadla', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='cinecalidadla', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_cinecalidadla', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    itemlist.append(item.clone( title = 'En castellano:', folder=False, text_color='moccasin' ))
    itemlist.append(item.clone( title = ' - Catálogo', action = 'list_all', url = host + 'espana/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En latino:', folder=False, text_color='moccasin' ))

    itemlist.append(item.clone( title = ' - Catálogo', action = 'list_all', url = host, search_type = 'movie' ))
    itemlist.append(item.clone( title = ' - Más destacadas', action = 'destacadas', url = host, search_type = 'movie' ))
    itemlist.append(item.clone( title = ' - En 4K', action = 'list_all', url = host + 'calidad/4k-ultra-hd-hdr/', search_type = 'movie' ))

    itemlist.append(item.clone( title = ' - Por género', action='generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = ' - Por año', action='anios', search_type = 'movie' ))


    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'destacadas', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'anime/', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Por género', action='generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="custom-menu-class">(.*?)</div></div>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        if '#' in url: continue

        if title == '4K Ultra': continue
        elif title == 'Películas por año': continue

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = text_color ))

    return sorted(itemlist, key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1969, -1):
        url = host + 'fecha/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color='deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="home_post_cont post_box">(.*?)</a></div>')

    for match in matches:
        title = scrapertools.find_single_match(match, '<h2>.*?">(.*?)</h2>')
        if not title: title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<div class="in_title">(.*?)</div>')

        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        if '-1-ano' in url: continue
        elif '-premium-12-meses' in url: continue

        if not url or not title: continue

        plot = scrapertools.find_single_match(match, '<p>.*?">(.*?)</p>').strip()
        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        m = re.match(r"^(.*?)\((\d+)\)$", title)
        if m:
            title = m.group(1).strip()
            year = m.group(2)
        else:
            year = '-'

        if not year: year = '-'

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        tipo = 'tvshow' if '/serie/' in url or '/anime/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if item.search_type == 'movie':
            if '/serie/' in url or '/anime/' in url: continue
        elif item.search_type == 'tvshow':
            if not '/serie/' in url and not '/anime/' in url: continue

        if '/espana/' in item.url:
            if not '?castellano=sp' in item.url: url = url + '?castellano=sp'

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title,  infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span class="pages">.*?class="current">.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def destacadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Destacadas<(.*?)>Herramientas')

    matches = scrapertools.find_multiple_matches(bloque, '<a(.*?)</li>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        if item.search_type == 'movie':
            if '/serie/' in url or '/anime/' in url: continue
        else:
            if '/pelicula/' in url: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        m = re.match(r"^(.*?)\((\d+)\)$", title)
        if m:
            title = m.group(1).strip()
            year = m.group(2)
        else:
            year = '-'

        if item.search_type == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))
        else:
            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = title,  infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'data-season="(.*?)"')

    for tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = item.url, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'data-season="' + str(item.contentSeason) + '"(.*?)</script>')

    matches = scrapertools.find_multiple_matches(bloque, 'src="(.*?)".*?<div class="numerando">EP(.*?)</div>.*?<a href="(.*?)"')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('CineCalidadLa', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('CineCalidadLa', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('CineCalidadLa', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('CineCalidadLa', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('CineCalidadLa', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('CineCalidadLa', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, epis, url in matches[item.page * item.perpage:]:
        epis = epis.replace('|', '')
        epis = epis.strip()

        if not epis: epis = '0'

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

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

    lang = 'Lat'

    if '?castellano=sp' in item.url: lang = 'Esp'

    data = do_downloadpage(item.url)

    ses = 0

    if '>VER ONLINE<' in data:
        bloque = scrapertools.find_single_match(data, '>VER ONLINE<(.*?)>DESCARGAR<')

        matches = scrapertools.find_multiple_matches(bloque, 'class="link onlinelink play.*?data-src="(.*?)".*?data-domain="(.*?)"')

        for data_url, servidor in matches:
            ses += 1

            servidor = servidor.lower().strip()

            if 'netu' in servidor or 'waaw' in servidor or 'hqq' in servidor: continue

            elif 'tubesb' in servidor: continue
            elif 'youtube' in servidor: continue
            elif servidor == 'vip': continue

            if servidor == 'ok': servidor = 'okru'

            elif servidor.startswith('sb'): servidor = 'streamsb'
            elif servidor == 'cloudemb': servidor = 'streamsb'
            elif 'lvturbo' in servidor: servidor = 'streamsb'
            elif 'likessb' in servidor: servidor = 'streamsb'

            elif servidor == 'google': servidor = 'gvideo'

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            qlty = '1080'

            itemlist.append(Item (channel = item.channel, action = 'play', server = servidor, title = '', url = item.url, data_url = data_url,
                                  quality = qlty, language = lang ))

    if '>DESCARGAR<' in data:
        bloque = scrapertools.find_single_match(data, '>DESCARGAR<(.*?)<div id="player">')

        matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?service="(.*?)"')

        for url, servidor in matches:
            ses += 1

            if url == '#':
                ses = ses - 1
                continue
            elif not servidor:
                ses = ses - 1
                continue
            elif '<div class="episodiotitle">' in servidor:
                ses = ses - 1
                continue

            if '<span' in servidor: servidor = scrapertools.find_single_match(servidor, '(.*?)<span')

            servidor = servidor.lower().strip()

            qlty = '1080'

            if '4k' in servidor or '4K' in servidor:
               qlty = '4K'
               servidor = servidor.replace('4k', '').replace('4K', '').strip()

            if 'subtítulo' in servidor: continue
            elif 'forzado' in servidor: continue
            elif 'gdtot' in servidor: continue

            elif servidor == 'utorrent': servidor = 'torrent'
            elif 'torrent' in servidor: servidor = 'torrent'

            elif servidor == 'google': servidor = 'gvideo'

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            itemlist.append(Item (channel = item.channel, action = 'play', server = servidor, title = '', url = url, quality = qlty, language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    servidor = item.server

    # ~ por si esta en ant_hosts
    for ant in ant_hosts:
        url = url.replace(ant, host)

    if item.data_url:
        url_play = base64.b64decode(item.data_url).decode("utf-8")

        url = item.url + '?playnow=' + url_play

        data = do_downloadpage(url)

        url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, 'window.location.href = "(.*?)"')

        if url:
            if not 'https' in url: url = ''

        if not url:
            if '/acortalink.' in data:
                return 'Tiene [COLOR plum]Acortador[/COLOR] del enlace'

            return itemlist

        if url.startswith('//'): url = 'https:' + url

    if '/protect/' in item.url:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, 'value="(.*?)"')

        if servidor == 'mega':
            if url.startswith('#'): url = 'https://mega.nz/' + url
            elif not url.startswith('http'): url = 'https://mega.nz/file/' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

    if url:
        if '/acortalink.' in url:
            return 'Tiene [COLOR plum]Acortador[/COLOR] del enlace'

        if url.endswith('.torrent'):
            itemlist.append(item.clone( url = url, server = 'torrent' ))
            return itemlist

        elif 'magnet:?' in url:
            itemlist.append(item.clone( url = url, server = 'torrent' ))
            return itemlist

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'zplayer':  url = url + '|' + host

        itemlist.append(item.clone(url = url, server = servidor))

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
