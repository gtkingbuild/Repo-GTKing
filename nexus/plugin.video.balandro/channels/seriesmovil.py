# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seriesmovil.top/'


def do_downloadpage(url, post=None, headers=None):
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

    generos = [
       'action-adventure',
       'ciencia-ficcion',
       'comedia',
       'crimen',
       'drama',
       'familia',
       'misterio',
       'sci-fi-fantasy',
       'war-politics'
       ]

    for genero in generos:
        url = host + 'category/' + genero + '/'

        itemlist.append(item.clone( action = 'list_all', title = genero.capitalize(), url = url, text_color = 'hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')
        if thumb.startswith('/'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, '<span class="Date">(.*?)</span>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year } ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="nav-links">' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, ' <main>(.*?)<section>')

    seasons = scrapertools.find_multiple_matches(bloque, '<div class="Title">.*?<a href="(.*?)".*?>Temporada.*?<span>(.*?)</span>')

    for url, tempo in seasons:
        title = 'Temporada ' + tempo

        if len(seasons) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.url = url
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    patron = '<td><span class="Num">(.*?)</span>.*?<a href="(.*?)".*?src="(.*?)".*?<td class="MvTbTtl">.*?>(.*?)</a>'

    episodes = scrapertools.find_multiple_matches(data, patron)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(episodes)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for epis, url, thumb, title, in episodes[item.page * item.perpage:]:
        if thumb.startswith('//'): thumb = 'https:' + thumb

        titulo = str(item.contentSeason) + 'x' + epis + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(episodes) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'latino': 'Lat', 'castellano': 'Esp', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<div id="VideoOption(.*?)".*?<iframe src="(.*?)"')

    ses = 0

    for opt, url in matches:
        ses += 1

        if url:
            lang = scrapertools.find_single_match(data, '<span class="nmopt">' + opt + '</span>.*?<span>(.*?)<span>').strip().lower()

            qlty = scrapertools.find_single_match(data, '<span class="nmopt">' + opt + '</span>.*?<span>.*?<span>(.*?)</span>').strip()
            qlty = scrapertools.find_single_match(qlty, '(.*?) •').strip()

            other = scrapertools.find_single_match(data, '<span class="nmopt">' + opt + '</span>.*?<span>.*?<span>(.*?)</span>').strip()
            other = scrapertools.find_single_match(other, ' • (.*?)$').strip().lower()

            other = servertools.corregir_servidor(other)

            if servertools.is_server_available(other):
                if not servertools.is_server_enabled(other): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url,
                                  language = IDIOMAS.get(lang, lang), quality = qlty, other = other.capitalize() ))

    # ~ Embeds
    matches = scrapertools.find_multiple_matches(data, '<li data-typ="episode".*?data-key="(.*?)".*?data-id="(.*?)".*?</div>(.*?)</li>')

    for _key, _id, datos in matches:
        ses += 1

        if not _key or not _id: continue

        lang = scrapertools.find_single_match(datos, '<p class="AAIco-language">(.*?)</p>').strip().lower()

        qlty = scrapertools.find_single_match(datos, '<p class="AAIco-equalizer">(.*?)</p>').strip()

        other = scrapertools.find_single_match(datos, '<p class="AAIco-dns">(.*?)</p>').strip().lower()

        post = {'action': 'action_player_change_new', 'id': _id, 'key': _key, 'typ': 'episode'}

        datae = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

        other = servertools.corregir_servidor(other)

        url = scrapertools.find_single_match(datae, '<IFRAME SRC="(.*?)"')
        if not url: url = scrapertools.find_single_match(datae, '<iframe src="(.*?)"')

        if url:
            if servertools.is_server_available(other):
                if not servertools.is_server_enabled(other): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            other = other.capitalize() + ' E'

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = IDIOMAS.get(lang, lang), quality = qlty, other = other ))

    # ~ Descargas
    bloque = scrapertools.find_single_match(data, '<div class="OptionBx on">(.*?)</section>')

    patron = '<div class="Optntl">Opción.*?<p class="AAIco-language">(.*?)</p>.*?<p class="AAIco-dns">(.*?)</p>.*?<p class="AAIco-equalizer">(.*?)</p>.*?href="(.*?)"'

    matches = scrapertools.find_multiple_matches(bloque, patron)

    for lang, srv, qllty, url in matches:
        ses += 1

        lang = lang.lower()

        if url:
           other = srv  + ' D'

           itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = IDIOMAS.get(lang, lang), quality = qlty, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    url = url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    if '?trdownload=' in url:
        new_url = httptools.downloadpage(url, follow_redirects=False).headers.get('location', '')
    else:
        data = do_downloadpage(url)

        new_url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="(.*?)"')
        if not new_url: new_url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')
 
        if new_url: url = new_url

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

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

