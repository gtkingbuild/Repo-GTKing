# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seriesbanana.com/'


def do_downloadpage(url, post=None, headers=None):
    headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(host)

    matches = scrapertools.find_multiple_matches(data, 'menu-item-object-category.*?<a href="(.*?)".*?>(.*?)</a>')

    for url, title in matches:
        title = title.replace('&#038;', '&').strip()

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, genre = title, text_color = 'hotpink' ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article class=(.*?)</article>')

    for match in matches:
        title =  scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')
        thumb if thumb.startswith('http') else "https:" + thumb

        itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title,  infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', action='list_all', url = next_page, genre = item.genre, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<div class="Title">.*?<a href="(.*?)".*?>Temporada <span>(.*?)</span>')

    for url, season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            if not config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.url = url
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, page = 0, contentType = 'season', contentSeason = season, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'Temporada ' + str(item.contentSeason) + '</h1>(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, '<tr class="Viewed">(.*?)</a></td></tr>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesBanana', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesBanana', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesBanana', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesBanana', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesBanana', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesBanana', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        title =  scrapertools.find_single_match(match, '<td class="MvTbTtl">.*?">(.*?)</a>')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        thumb if thumb.startswith('http') else "https:" + thumb

        epis =  scrapertools.find_single_match(match, '<span class="Num">(.*?)</span>')

        ord_epis = str(epis)

        if len(str(ord_epis)) == 1: ord_epis = '0000' + ord_epis
        elif len(str(ord_epis)) == 2: ord_epis = '000' + ord_epis
        elif len(str(ord_epis)) == 3: ord_epis = '00' + ord_epis
        else:
            if item.perpage > 50: ord_epis = '0' + ord_epis

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb, 
                                    orden = ord_epis, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", orden = '10000',
                                        page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'Español Latino': 'Lat', 'Español': 'Esp', 'Subtitulado': 'Vose', 'VOSE': 'Vose'}

    data = do_downloadpage(item.url)

    options = scrapertools.find_multiple_matches(data, '<li data-typ="episode"(.*?)</li>')

    for option in options:
        lang = scrapertools.find_single_match(option, '<p class="AAIco-language">(.*?)</p>')

        url_post =  host + 'wp-admin/admin-ajax.php'

        d_id = scrapertools.find_single_match(option, 'data-id="(.*?)"')
        d_key = scrapertools.find_single_match(option, 'data-key="(.*?)"')

        post = {"action": "action_player_change", "id": d_id, "key": d_key, "typ": "episode"}
        data = do_downloadpage(url_post, post = post)

        url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')

        if url:
           other = scrapertools.find_single_match(option, '<p class="AAIco-dns">(.*?)</p>').strip()

           url = url.replace('&#038;', '&').replace('&amp;', '&')

           servidor = servertools.get_server_from_url(url)
           servidor = servertools.corregir_servidor(servidor)

           itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang,lang), other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if not item.server == 'directo':
        itemlist.append(item.clone(server = item.server, url = item.url))

        return itemlist

    if item.url.startswith(host):
        data = do_downloadpage(item.url)

        new_url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')
        if not new_url: new_url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="(.*?)"')

        if new_url:
            servidor = servertools.get_server_from_url(new_url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone(url = new_url, server = servidor))

            return itemlist

    servidor = servertools.get_server_from_url(url)
    servidor = servertools.corregir_servidor(servidor)

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

