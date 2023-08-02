# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://retrotv.org/'

perpage = 20


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'lista-series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host + 'lista-series/episodios-agregados-actualizados/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data
   
    patron = 'class="menu-item menu-item-type-taxonomy menu-item-object-category.*?<a href="(.*?)">(.*?)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title in matches:
        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( action = "list_all", title = title, url = url ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    current_year = current_year - 10

    for x in range(current_year, 1954, -1):
        itemlist.append(item.clone( title = str(x), url = host + '?s=trfilter&trfilter=1&years%5B%5D=' + str(x), action = 'list_all' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        letras = letra.lower()

        url = host + 'letter/' + letras + '/'

        itemlist.append(item.clone( action = 'list_alfa', title = letra, url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(match, '<h3 class="Title">(.*?)</h3>')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')
        if thumb.startswith('//'):
            thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, '<span class="Year">(.*?)</span>')
        if not year: year = '-'

        name = title.replace('&#038;', '&')

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = name, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            if '<div class="wp-pagenavi">' in data:
                if '<a class="page-numbers"' in data:
                    next_url = scrapertools.find_single_match(data, 'class="page-numbers current".*?href="(.*?)"')

                    if next_url:
                        next_url = next_url.strip()

                        if '/page/' in next_url:
                            itemlist.append(item.clone( action = 'list_all', page = 0, url = next_url, title = 'Siguientes ...', text_color='coral' ))

    return itemlist


def list_alfa(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</tr>')
    num_matches = len(matches)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<strong>(.*?)</strong>').strip()
        if not url or not title: continue

        if '/aplicacion-oficial-de-retrotv-org/' in url: continue

        thumb = scrapertools.find_single_match(match, ' data-src="([^"]+)')

        year = scrapertools.find_single_match(match, '<strong>.*?</td><td>Serie</td><td>(\d{4})</span>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        url = url.strip()

        seas_epis = scrapertools.find_single_match(match, '<span class="ClB">(\d+)x(\d+)</span>')

        if not seas_epis: continue

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)"')
        thumb = 'https:' + thumb

        title = scrapertools.find_single_match(match, '<h3 class="Title">(.*?)</h3>')

        fecha = scrapertools.find_single_match(match, '<span class="Year">(.*?)</span>')

        titulo = seas_epis[0] + 'x' + seas_epis[1] + ' ' + title
        if fecha: titulo = titulo + ' (' + fecha + ')'

        itemlist.append(item.clone( action = 'findvideos', title = titulo, url = url, thumbnail = thumb,
                                    contentType = 'episode', contentSerieName = title, contentSeason = seas_epis[0], contentEpisodeNumber = seas_epis[1] ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="wp-pagenavi">' in data:
             if '<a class="page-numbers"' in data:
                next_url = scrapertools.find_single_match(data, 'class="page-numbers current".*?href="(.*?)"')

                if next_url:
                    next_url = next_url.strip()
                    if '/page/' in next_url:
                        itemlist.append(item.clone (url = next_url, title = 'Siguientes ...', action = 'list_epis', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile(' data-tab="(.*?)">Temporada', re.DOTALL).findall(data)

    for tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data

    season = str(item.contentSeason)

    bloque = scrapertools.find_single_match(data, ' data-tab="' + season + '">.*?<tbody>(.*?)</tbody>' )

    matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?)</tr>')

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('RetroTv', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('RetroTv', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('RetroTv', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('RetroTv', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('RetroTv', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for data_epi in matches[item.page * item.perpage:]:
        title = scrapertools.find_single_match(data_epi, ' alt="Imagen.*?<a href=.*?>(.*?)</a>')
        if not title: title = scrapertools.find_single_match(data_epi, ' alt=.*?Imagen.*?<a href=.*?>(.*?)</a>')

        url = scrapertools.find_single_match(data_epi, '<a href="(.*?)"')

        if not url or not title: continue

        episode = scrapertools.find_single_match(data_epi, '<span class="Num">(.*?)</span>')

        thumb = scrapertools.find_single_match(data_epi, '<img src="([^"]+)"')
        thumb = 'https:' + thumb

        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, 
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

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

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'data-tplayernv="Opt(.*?)"><span>(.*?)</span>')

    ses = 0

    for opt, servidor in matches:
        ses += 1

        servidor = servidor.replace('<strong>', '').replace('</strong>', '')
        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '".*?src="(.*?)"')
        if not url:
            url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '".*?src=&quot;(.*?)&quot;')

        if url.startswith('//') == True:
            url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '".*?src=&quot;(.*?)&quot;')

        if not servidor or not url: continue

        if 'opción' in servidor or 'servidor' in servidor:
            link_other = servidor
            servidor = 'directo'
        elif servidor == 'anavids':
            link_other = servidor
            servidor = 'directo'
        elif servidor == 'blenditall':
            link_other = servidor
            servidor = 'directo'
        else: link_other = ''

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = 'Lat', other = link_other ))

    # Descargas
    matches = scrapertools.find_multiple_matches(data, '<span class="Num">(.*?)</tr>')

    for match in matches:
        ses += 1

        servidor = scrapertools.find_single_match(match, 'alt="Descargar(.*?)"')
        servidor = servidor.replace('.', '').strip()

        if not servidor: continue

        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = 'Lat', other = 'd' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&').strip()

    if url.startswith(host):
        if item.other == 'd':
            url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get('location', '')
        else:
            data = httptools.downloadpage(url).data

            if item.other == 'anavids':
                url = scrapertools.find_single_match(data.lower(), '<iframe src="(.*?)"')

                data = httptools.downloadpage(url).data
                url = scrapertools.find_single_match(str(data), 'sources.*?"(.*?)"')
            else:
                url = scrapertools.find_single_match(data, 'src="(.*?)"')

                if 'blenditall' in url:
                    data = httptools.downloadpage(url).data

                    urlb = scrapertools.find_single_match(data, '"file".*?"(.*?)"')
                    urlb = urlb.replace('\\/', '/')

                    if urlb:
                        if urlb.startswith('//') == True: urlb = 'https:' + urlb

                        if urlb.startswith('https://blenditall.com/playlist.m3u8?data='):
                            itemlist.append(item.clone(server = 'm3u8hls', url = urlb))
                            return itemlist

                        data = httptools.downloadpage(urlb).data

                        new_url = scrapertools.find_single_match(data, '//blenditall.com/playlist.m3u8?data=(.*?)$')

                        if new_url:
                            url = 'https://blenditall.com/playlist.m3u8?data=' + new_url

                            itemlist.append(item.clone(server = 'm3u8hls', url = url))
                            return itemlist

    if '/app.retrotvshows.com/' in url: url = ''
    elif 'blenditall' in url:  url = ''

    if url:
        if url.startswith('//') == True: url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor:
            url = servertools.normalize_url(servidor, url)
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
