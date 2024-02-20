# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.seriesantiguas.com/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://www.seriesantiguas.net/', 'https://seriesantiguas.com/']


domain = config.get_setting('dominio', 'seriesantiguas', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'seriesantiguas')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'seriesantiguas')
    else: host = domain


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'seriesantiguas', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_seriesantiguas', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='seriesantiguas', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_seriesantiguas', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = "Las de los 80's", action = 'list_all', url = host + 'media-category/80s/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = "Las de los 90's", action = 'list_all', url = host + 'media-category/90s/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = "Las de los 2000's", action = 'list_all', url = host + 'media-category/00s/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = "Halloween", action = 'episodios', url = host + 'ver/halloween/', special = 'special', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = "Navidad", action = 'episodios', url = host + 'ver/navidad/', special = 'special', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '<div class="progression-studios-elementor-video-post-container">' in data:
         bloque = scrapertools.find_single_match(data, '<div class="progression-studios-elementor-video-post-container">(.*?)</div></div></div></div></div></div></div>')

         if not bloque: bloque = scrapertools.find_single_match(data, '<div class="progression-studios-elementor-video-post-container">(.*?)<div class="aztec-progression-pagination-elementor">')
         if not bloque: bloque = data

    else: bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<div id="post-(.*?)<div class="progression-studios-isotope-animation">')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<div id="post-(.*?)<div class="clearfix-pro"></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="progression-video-title">(.*?)</h2>')

        if not url or not title: continue

        if '/ver/mtv/' in url: continue
        elif '/ver/tooncast/' in url: continue
        elif '/ver/disney-channel/' in url: continue
        elif '/ver/cartoon-network/' in url: continue
        elif '/ver/nick/' in url: continue

        elif 'ver/halloween/' in url: continue
        elif 'ver/navidad/' in url: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if thumb.startswith('/'): thumb = host[:-1] + thumb

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="nav-previous">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="nav-previous">.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, 'href="#aztec-tab-(.*?)"')

    # ~ por el sistema antiguo 13/1/2023
    if not matches:
        if not 'Clic para ver en la antigua' in data: return itemlist

        url_old_serie = scrapertools.find_single_match(data, '<li><a href="(.*?)".*?Clic para ver en la antigua')

        if not url_old_serie: return itemlist

        data = do_downloadpage(url_old_serie)
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

        bloque = scrapertools.find_single_match(data, ">Temporadas<(.*?)>Más Series<")

        matches2 = scrapertools.find_multiple_matches(bloque, "<a href='(.*?)'>Temp(.*?)</a>")

        for url, numtempo in matches2:
            numtempo = numtempo.strip()
            if not numtempo: numtempo = 0

            title = 'Temporada ' + numtempo

            if len(matches) == 1:
                if config.get_setting('channels_seasons', default=True):
                    platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

                item.page = 0
                item.url = url
                item.old = 'old'
                item.contentType = 'season'
                item.contentSeason = numtempo
                itemlist = episodios(item)
                return itemlist

            itemlist.append(item.clone( action = 'episodios', title = title, url = url, old = 'old', page = 0, contentType = 'season', contentSeason = numtempo, text_color = 'tan' ))

    else:

        for numtempo in matches:
            title = 'Temporada ' + numtempo

            url = item.url + '/#aztec-tab-' + numtempo

            if len(matches) == 1:
                if config.get_setting('channels_seasons', default=True):
                    platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

                item.page = 0
                item.url = url
                item.contentType = 'season'
                item.contentSeason = numtempo
                itemlist = episodios(item)
                return itemlist

            itemlist.append(item.clone( action = 'episodios', title = title, url = url, old = '', page = 0, contentType = 'season', contentSeason = numtempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if not item.special:
        bloque = scrapertools.find_single_match(data, '<div id="progression-studios-season-video-list-' + str(item.contentSeason) + '(.*?)</div></div></div></div></div>')
        if not bloque: bloque = scrapertools.find_single_match(data, '<div id="progression-studios-season-video-list-' + str(item.contentSeason) + '(.*?)<div class="clearfix-pro">')
    else: bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<div class="progression-studios-season-item">(.*?)><div class="clearfix-pro">')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<div class="progression-studios-season-item">(.*?)<div class="clearfix-pro">')

    if not matches: matches = scrapertools.find_multiple_matches(data, "<div class='post hentry'>(.*?)</div></div>")

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesAntiguas', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesAntiguas', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesAntiguas', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesAntiguas', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesAntiguas', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesAntiguas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

        if item.old: item.perpage = sum_parts

    for epis in matches[item.page * item.perpage:]:
        if not item.special:
            if not item.old:
                if not '-temporada-' + str(item.contentSeason) in epis: continue

        url = scrapertools.find_single_match(epis, '<a href="([^"]+)"')

        if not item.old:
            episode = scrapertools.find_single_match(epis, '<h2 class="progression-video-title">(.*?). ')

            title = scrapertools.find_single_match(epis, '<h2 class="progression-video-title">.*?. (.*?)</h2').strip()
        else:
            episode = scrapertools.find_single_match(epis, "Temporada.*?x(.*?)'").strip()
            episode = episode.replace(')', '')

            title = scrapertools.find_single_match(epis, "<img alt='(.*?)'")

            if not title: title = scrapertools.find_single_match(epis, '<h2 class="progression-video-title">.*?. (.*?)</h2').strip()

        if not url or not episode: continue

        if not item.old:
            title = str(item.contentSeason) + 'x' + episode + ' ' + title

        thumb = scrapertools.find_single_match(epis, 'src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(epis, "src='(.*?)'")

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if not item.old:
            if len(matches) > (item.page + 1) * item.perpage:
                itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))
        else:
            if "<a class='blog-pager-older-link'" in data:
                next_url = scrapertools.find_single_match(data, "<a class='blog-pager-older-link'.*?" + 'href="(.*?)"')

                if next_url:
                    itemlist.append(item.clone( title="Siguientes ...", action="episodios", url = next_url, old= 'old', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if "<div class='post-body entry-content'>" in data: bloque = scrapertools.find_single_match(data, "<div class='post-body entry-content'>(.*?)<div class='post-footer'>")
    else: bloque = data

    matches0 = scrapertools.find_multiple_matches(bloque, '<iframe.*?src="(.*?)".*?</iframe>')

    matches1 = scrapertools.find_multiple_matches(bloque, '<iframe.*?allow="autoplay".*?data-src="(.*?)".*?</iframe>')

    matches2 = scrapertools.find_multiple_matches(bloque, '<noscript><iframe.*? src="(.*?)".*?</iframe>')

    matches = matches0 + matches1 + matches2

    for url in matches:
        if url.startswith('//'): url = 'https:' + url

        url = url.replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Lat' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?post_type=video_skrn&search_keyword=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
