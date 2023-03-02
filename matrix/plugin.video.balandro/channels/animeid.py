# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://animeid.to/'


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Nuevas temporadas', action = 'list_all', url = host + 'new-season', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'ongoing-series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'popular', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'movies', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h3(.*?)<div class="clr"></div>')

    matches = re.compile('<li class="video-block ">(.*?)</li>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        if item.search_type == 'movie':
            PeliName = title

            if 'Movie' in title: PeliName = title.split("Movie")[0]

            PeliName = PeliName.strip()

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=PeliName, infoLabels={'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<ul class='pagination'" in data:
            next_url = scrapertools.find_single_match(data, "<ul class='pagination'.*?class=active>.*?</li>.*?href='(.*?)'")

            if next_url:
                next_url = host[:-1] + next_url

                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Lista de episodios<(.*?)<div class="clr"></div>')
	
    matches = scrapertools.find_multiple_matches(bloque, '<li class="video-block ">(.*?)</li>')

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimeId', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeId', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeId', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeId', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimeId', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<div class="name">(.*?)</div>').strip()

        if not url or not title: continue

        url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        epis = scrapertools.find_single_match(match, '<div class="type"><span>(.*?)</span>').lower().strip()
        epis = epis.replace('ep', '').strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

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

    link = scrapertools.find_single_match(data, '<iframe src="(.*?)"')

    if not link: return itemlist

    if not link.startswith("http"): link = "https:" + link

    data = httptools.downloadpage(link).data

    ses = 0

    matches = re.compile('<li class="linkserver".*?data-video="(.*?)">(.*?)</li>', re.DOTALL).findall(data)

    for url, srv in matches:
        ses += 1

        srv = srv.lower()

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue

        elif 'jetload.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'directo': other = srv

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vose', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search.html?keyword=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

