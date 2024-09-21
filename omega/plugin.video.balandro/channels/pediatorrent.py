# -*- coding: utf-8 -*-


import re

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://pediatorrent.com/'


def do_downloadpage(url, post=None, headers=None):
    if not headers: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))
    itemlist.append(item.clone( title = 'Documentales', action = 'mainlist_documentary', text_color = 'cyan' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    return itemlist


def mainlist_documentary(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'documentales', search_type = 'documentary' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Calidad<(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque, '<option value="(.*?)">(.*?)</option>')

    for qlty, title in matches:
        url = host + 'peliculas?query=&quality=' + qlty + '&genre=&year='

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color='deepskyblue' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Género<(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque, '<option value="(.*?)">(.*?)</option>')

    for gen, title in matches:
        url = host + 'peliculas?query=&quality=&genre=' + gen + '&year='

        itemlist.append(item.clone( title=title, url = url, action='list_all', text_color='deepskyblue'))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1899, -1):
        url = host + 'peliculas?query=&quality=&genre=&year=' + str(x)

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color='deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if item.search_type == 'movie':
        matches = scrapertools.find_multiple_matches(data, '<div class="relative my-5 md:my-4">(.*?)</div></div></div>')
    else:
        matches = scrapertools.find_multiple_matches(data, '<div class="relative my-5 md:my-4">(.*?)</div></div>')

    if not matches: matches = scrapertools.find_multiple_matches(data, '<div class="relative flex flex-col gap-y-3 my-5 md:my-4">(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        qlty = scrapertools.find_single_match(match, '<span>(.*?)</span>')

        year = scrapertools.find_single_match(match, '<p class="text-sm mt-3 leading-4 truncate text-neutral-400">(.*?)</p>')
        if not year: year = '-'

        tipo = 'movie' if '/peliculas/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            if "Temporada" in title: SerieName = title.split("Temporada ")[0]
            else: SerieName = title

            SerieName = SerieName.replace('[720]', '').strip()

            itemlist.append(item.clone( action='episodios', url = url, title = title, thumbnail = thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue
                elif item.search_type == 'documentary': continue

            PeliName = title

            PeliName = PeliName.replace('[4K]', '').replace('[4k]', '').strip()

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = PeliName, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span aria-current="page">.*?href="(.*?)"')

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

    matches = scrapertools.find_multiple_matches(data, '<tr wire:key="episode-.*?<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-300">(.*?)</td>.*?href="(.*?)"')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-neutral-200">.*?<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-300">(.*?)</td>.*?href="(.*?)"')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PediaTorrent', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PediaTorrent', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PediaTorrent', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PediaTorrent', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PediaTorrent', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PediaTorrent', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for temp_epis,url in matches[item.page * item.perpage:]:
        season = scrapertools.find_single_match(temp_epis, '(.*?)x').strip()
        episode = scrapertools.find_single_match(temp_epis, 'x(.*?)$').strip()

        SerieName = item.contentSerieName

        title = SerieName

        titulo = '%sx%s %s' % (season, episode, title)

        if url.startswith("/"): url = host[:-1] + url

        itemlist.append(item.clone( action = 'findvideos', title = titulo, url = url,
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

    if '/torrents/'in item.url:
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = item.url, server = 'torrent', language = lang ))
        return itemlist

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="flex w-56 items-center justify-center mx-auto lg:mx-0">.*?href="(.*?)"', re.DOTALL).findall(data)

    for url in matches:
        url = host[:-1] + url

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = lang ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.search_type == 'movie':
            item.url = host + 'peliculas?query=' + texto.replace(" ", "+") + '&quality=&genre=&year='
        elif item.search_type == 'tvshow':
            item.url = host + 'series?query=' + texto.replace(" ", "+") + '&format='
        elif item.search_type == 'documentary':
            item.url = host + 'documentales?query=' + texto.replace(" ", "+") + '&format='
        else:
            item.url = host + 'buscar?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
