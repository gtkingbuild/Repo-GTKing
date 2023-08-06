# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://pelisplus.cc/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/year/' in url: raise_weberror = False

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas?page=', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas/estrenos?page=', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'peliculas/populares?page=', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series?page=', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'series/estrenos?page=', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'series/populares?page=', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'animes?page=', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Doramas', action = 'list_all', url = host + 'generos/dorama?page=', search_type = 'tvshow', text_color='firebrick' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Generos(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, tit in matches:
        if item.search_type == 'tvshow':
	        if 'Televisión' in tit: continue

        url = host[:-1] + url + '?page='

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = text_color ))

    return sorted(itemlist, key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie': limit = 1930
    else: limit = 1959

    for x in range(current_year, limit, -1):
        url = host + 'year/' + str(x) + '?page='

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    data = do_downloadpage(item.url + str(item.page))

    bloque = scrapertools.find_single_match(data, '<div class="Posters">(.*?)<div class="copyright">')

    matches = scrapertools.find_multiple_matches(bloque, '<a(.*?)</a>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        title = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        if not url or not title: continue

        title =  re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', title)

        if url.startswith('/'): url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = '-'

        if ' (' in title:
            year = title.split(' (')[1]
            year = year.replace(')', '').strip()
        elif ' [' in title:
            year = title.split(' [')[1]
            year = year.replace(']', '').strip()

        if not year == '-':
            if ' (' in title: title = title.replace(' (' + year + ')', '').strip()
            elif ' [' in title: title = title.replace(' [' + year + ']', '').strip()

        if '/pelicula/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(itemlist) == 24:
            itemlist.append(item.clone (url = item.url, page = item.page + 1, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    temporadas = re.compile('data-toggle="tab">(.*?)</a>', re.DOTALL).findall(data)

    tot_tempo = len(temporadas)

    for tempo in temporadas:
        if not 'Temporada' in tempo:
           if not 'TEMPORADA' in tempo: continue

        tempo = tempo.replace('Temporada', '').replace('TEMPORADA', '').strip()

        tempo = tempo.replace('#', '').strip()

        if not tempo: continue
        elif '/descarga/' in tempo: continue

        nro_tempo = tempo
        if tot_tempo >= 10:
            if int(tempo) < 10: nro_tempo = '0' + tempo

        title = 'Temporada ' + nro_tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.title)


def episodios(item):
    logger.info()
    itemlist = []

    tab_epis = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'data-toggle="tab">Temporada.*?' + str(item.contentSeason) + '(.*?)<div class="clear"></div>')
    if not bloque: bloque = scrapertools.find_single_match(data, 'data-toggle="tab">TEMPORADA.*?' + str(item.contentSeason) + '(.*?)<div class="clear"></div>')

    if bloque:
        bloque = scrapertools.find_single_match(bloque, 'id="pills-vertical-' + str(item.contentSeason) + '(.*?)</div>')

    matches = re.compile('<a href="(.*?)".*?">(.*?):(.*?)</a>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PelisPlusCc', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlusCc', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlusCc', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlusCc', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlusCc', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PelisPlusCc', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for url, temp_epis, title in matches:
        if url.startswith('/'): url = host[:-1] + url

        episode = scrapertools.find_single_match(temp_epis, ".*?-(.*?)$").strip()

        episode = episode.replace('E', '').strip()

        ord_epis = str(episode)

        if len(str(ord_epis)) == 1: ord_epis = '0000' + ord_epis
        elif len(str(ord_epis)) == 2: ord_epis = '000' + ord_epis
        elif len(str(ord_epis)) == 3: ord_epis = '00' + ord_epis
        else:
            if num_matches > 50: ord_epis = '0' + ord_epis

        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        if num_matches > 50:
            tab_epis.append([ord_epis, url, titulo, episode])
        else:
            itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                        contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode, orden = ord_epis ))

    if num_matches > 50:
        tab_epis = sorted(tab_epis, key=lambda x: x[0])

        for orden, url, tit, epi in tab_epis[item.page * item.perpage:]:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = tit,
                                        orden = orden, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epi ))

            if len(itemlist) >= item.perpage:
                break

        if itemlist:
            if num_matches > ((item.page + 1) * item.perpage):
                itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", data_epi = item.data_epi, orden = '10000',
                                            page = item.page + 1, perpage = item.perpage, text_color = 'coral' ))

        return itemlist

    else:
        return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'latino': 'Lat', 'subtitulado': 'Vose'}

    lang = 'Lat'

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<span lid="(.*?)".*?url="(.*?)"')

    ses = 0

    for opt, url in matches:
        if not url: continue

        ses += 1

        if '/player.moovies.in/' in url: continue
        elif 'mystream.to' in url: continue

        if url.startswith('/fembed.php?url='): url = url.replace('/fembed.php?url=', 'https://feurl.com/v/')
        elif 'pelisplu.cc' in url: url = url.replace('pelisplus.cc', 'feurl.com')
        elif 'pelisplus.cc/fembed.php' in url: url= url.replace('pelisplus.cc/fembed.php?url=', 'https://feurl.com/v/')
        elif (host + 'fembed.php') in url: url = url.replace(host + 'fembed.php?url=', 'https://feurl.com/v/')
        elif 'plusto.link' in url: url = url.replace('plusto.link', 'feurl.com')

        if url.startswith('/'): url = host[:-1] + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        link_other = ''

        if servidor == 'directo':
            link_other = scrapertools.find_single_match(data, '<a href="#option' + opt + '">(.*?)</a>')

            if link_other == 'Netu' or link_other == 'NETU' or link_other == 'Waaw' or link_other == 'WAAW' or link_other == 'Hqq' or link_other == 'HQQ': continue

            link_other = normalize_other(link_other)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = IDIOMAS.get(lang, lang), other = link_other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def normalize_other(url):
    if 'pelisplus' in url: link_other = 'plus'
    elif 'damedamehoy' in url: link_other = 'dame'
    elif 'tomatomatela' in url: link_other = 'dame'
    else:
       if config.get_setting('developer_mode', default=False): link_other = url
       else: link_other = ''

    return link_other


def resuelve_dame_toma(dame_url):
    data = do_downloadpage(dame_url)

    url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
    if not url:
        checkUrl = dame_url.replace('embed.html#', 'details.php?v=')
        data = do_downloadpage(checkUrl, headers={'Referer': dame_url})
        url = scrapertools.find_single_match(data, '"file":\s*"([^"]+)').replace('\\/', '/')

    return url


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.other == 'dame':
        url = resuelve_dame_toma(item.url)

        if url:
            itemlist.append(item.clone(url=url , server='directo'))
            return itemlist

    elif item.server == 'directo':
        data = do_downloadpage(url)

        urls = scrapertools.find_multiple_matches(data, "sources:\[{file:.*?\'(.*?)\',label")

        for url in urls:
            if not 'error' in url:
                if '/pelisloadtop.com/' in url: continue

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                itemlist.append(item.clone( url = url, server = servidor ))
    else:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<div class="Posters">(.*?)<div class="copyright">')

    matches = scrapertools.find_multiple_matches(bloque, '<a(.*?)</a>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        title = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        if not url or not title: continue

        title =  re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', title)

        if url.startswith('/'): url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = '-'

        if ' (' in title:
            year = title.split(' (')[1]
            year = year.replace(')', '').strip()
        elif ' [' in title:
            year = title.split(' [')[1]
            year = year.replace(']', '').strip()

        if not year == '-':
            if ' (' in title: title = title.replace(' (' + year + ')', '').strip()
            elif ' [' in title: title = title.replace(' [' + year + ']', '').strip()

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'search?s=' + texto.replace(" ", "+")
       return list_search(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
