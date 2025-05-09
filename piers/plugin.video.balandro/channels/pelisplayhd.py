# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www3.peliplayhd.org/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www.peliplayhd.org/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not headers: headers = {'Referer': url}

    raise_weberror = True
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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '> Géneros<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        if item.search_type == 'movie':
            if title == 'Reality': continue
            elif title == 'Soap': continue
            elif title == 'Talk': continue
            elif title == 'Telenovela': continue

        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url, text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1929, -1):
        url = host + 'release/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '>Mas Popular<' in data:
        bloque = scrapertools.find_single_match(data, '</h1>(.*?)>Mas Popular<')
    else:
        bloque = scrapertools.find_single_match(data, '</h1>(.*?)>Contacto<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

        if not url or not title: continue

        if '/clasicoanimado/' in url: continue

        title = title.replace('&#038;', '&')

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        thumb = host[:-1] + thumb

        qlty = scrapertools.find_single_match(match, '<span class="Qlty">(.*?)</span>')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')

        if year: title = title.replace('(' + year +')', '').strip()
        else: year = '-'

        if '/release/' in item.url: year = scrapertools.find_single_match(item.url, "/release/(.*?)/")

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?<a class="page-link".*?href="(.*?)"')

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('data-season="(.*?)"', re.DOTALL).findall(data)

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

    d_post = scrapertools.find_single_match(str(data), 'data-post="(.*?)"')

    if not d_post: return itemlist

    post = {'action': 'action_select_season', 'season': str(item.contentSeason), 'post': d_post}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('PelisPlayHd', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PelisPlayHd', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlayHd', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlayHd', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlayHd', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlayHd', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PelisPlayHd', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        if thumb: thumb = 'https:' + thumb

        epis = scrapertools.find_single_match(match, '<span class="num-epi">.*?x(.*?)</span>')

        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        titulo = str(item.contentSeason) + 'x' + epis + ' ' + title

        titulo = titulo.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')

        titulo = titulo.replace('Capitulo', '[COLOR goldenrod]Epis..[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Epis.[/COLOR]')

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
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

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, 'href="#options-(.*?)</li>')

    ses = 0

    for match in matches:
        ses += 1

        opt = scrapertools.find_single_match(match, '(.*?)">')

        srv = scrapertools.find_single_match(match, '<span class="server">(.*?)-').strip()
        lng = scrapertools.find_single_match(match, '<span class="server">.*?-(.*?)</span>').strip()

        srv = srv.lower().strip()

        if 'youtube' in srv: continue

        if 'Latino' in lng: lang = 'Lat'
        elif 'Castellano' in lng or 'Español' in lng: lang = 'Esp'
        elif 'Subtitulado' in lng or 'VOSE' in lng: lang = 'Vose'
        elif 'Inglés' in lng: lang = 'Vo'
        else: lang = '?'

        servidor = servertools.corregir_servidor(srv)

        links = scrapertools.find_multiple_matches(data, '<div id="options-' + opt + '.*?<iframe.*?src="(.*?)"')

        if not links: continue

        for url in links:
            ses += 1

            other = srv

            if 'peliplaywish' in srv:
                servidor = 'directo'
                other = 'peliplaywish'
            elif 'mivideoplay' in srv:
                servidor = 'directo'
                other = 'mivideoplay'
            elif 'peliplaymoon' in srv:
                servidor = 'directo'
                other = 'peliplaymoon'
            elif 'fmoonembed' in srv:
                servidor = 'directo'
                other = 'fmoonembed'
            elif 'embedmoon' in srv:
                servidor = 'directo'
                other = 'embedmoon'
            elif 'jodwish' in srv:
                servidor = 'directo'
                other = 'jodwish'
            elif 'swhoi' in srv:
                servidor = 'directo'
                other = 'swhoi'
            elif 'swdyu' in srv:
                servidor = 'directo'
                other = 'swdyu'
            elif 'strwish' in srv:
                servidor = 'directo'
                other = 'strwish'
            elif 'vidhidepre' in srv:
                servidor = 'directo'
                other = 'vidhidepre'
            elif 'playerwish' in srv:
                servidor = 'directo'
                other = 'playerwish'
            elif 'fastream' in srv:
                servidor = 'directo'
                other = 'fastream'

            else:
                if 'wish' in srv:
                    servidor = 'directo'
                    other = 'streamwish'
                elif 'vidhide' in srv:
                    servidor = 'directo'
                    other = 'vidhidepro'
                else:
                    if 'wastream' in srv: continue

                    servidor = 'directo'
                    other = 'indeterminado'

            if servidor == srv: other = ''
            elif not servidor == 'directo':
               if not servidor == 'various': other = ''

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                  language = lang, other = other.capitalize() ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&')

    data = do_downloadpage(item.url)

    url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
    if not url: url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="([^"]+)')

    if item.other == 'Indeterminado' or item.other == 'Peliplaywish' or item.other == 'Mivideoplay' or item.other == 'Peliplaymoon' or item.other == 'Fmoonembed' or item.other == 'Embedmoon' or item.other == 'Jodwish' or item.other == 'Swhoi' or item.other == 'Swdyu' or item.other == 'Strwish' or item.other == 'Vidhidepre' or item.other == 'Playerwish' or item.other == 'Streamwish' or item.other == 'Vidhidepro' or item.other == 'Fastream':
        if '/?trembed' in url:
            data = do_downloadpage(url)

            url = scrapertools.find_single_match(str(data), 'link: "(.*?)"')
            if not url: url = scrapertools.find_single_match(str(data), "location.href = '(.*?)'")
            if not url: url = scrapertools.find_single_match(str(data), 'sources:.*?file:.*?"(.*?)"')

    if url:
        if '//e/' in url: url = url.replace('//e/', '/e/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

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

