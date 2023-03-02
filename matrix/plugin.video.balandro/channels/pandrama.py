# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://pandrama.com/'

perpage = 30


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'vodshow/Dramas-----------/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Más vistos', action = 'list_all', url = host + 'vodshow/Dramas--hits---------/', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Más populares', action = 'list_all', url = host + 'vodshow/Dramas--up---------/', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Más valorados', action = 'list_all', url = host + 'vodshow/Dramas--score---------/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Acción', action = 'list_all', url = host + 'vodshow/accion-----------/' ))
    itemlist.append(item.clone ( title = 'Boys love', action = 'list_all', url = host + 'vodshow/boyslove-----------/' ))
    itemlist.append(item.clone ( title = 'Comedia', action = 'list_all', url = host + 'vodshow/comedia-----------/' ))
    itemlist.append(item.clone ( title = 'Crimen', action = 'list_all', url = host + 'vodshow/crimen-----------/' ))
    itemlist.append(item.clone ( title = 'Médico', action = 'list_all', url = host + 'vodshow/medico-----------/' ))
    itemlist.append(item.clone ( title = 'Melodrama', action = 'list_all', url = host + 'vodshow/melodrama-----------/' ))
    itemlist.append(item.clone ( title = 'Misterio', action = 'list_all', url = host + 'vodshow/misterio-----------/' ))
    itemlist.append(item.clone ( title = 'Romance', action = 'list_all', url = host + 'vodshow/romance-----------/' ))
    itemlist.append(item.clone ( title = 'Terror', action = 'list_all', url = host + 'vodshow/terror-----------/' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'En chino', action = 'list_all', url = host + 'vodshow/Dramas----Chino-------/' ))
    itemlist.append(item.clone ( title = 'En coreano', action = 'list_all', url = host + 'vodshow/Dramas----Coreano-------/' ))
    itemlist.append(item.clone ( title = 'En japonés', action = 'list_all', url = host + 'vodshow/Dramas----Japonés-------/' ))
    itemlist.append(item.clone ( title = 'En tailandés', action = 'list_all', url = host + 'vodshow/Dramas----Tailandés-------/' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        url = host + 'vodshow/Dramas-----------' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<li class="vodlist_item num_(.*?)</li>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'data-original="(.*?)"')

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                    contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
                buscar_next = False

        if buscar_next:
            next_url = scrapertools.find_single_match(data, '<li class="hidden_xs active">.*?<li class="hidden_xs "><a href="(.*?)')
            if next_url:
                next_url = host[:-1] + next_url

                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    # ~ No hay temporadas
    title = 'Temporadas'

    platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]' + title + '[/COLOR]')
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

    if item.page == 0: episode = 0
    else: episode = (item.page * item.perpage) + 1

    bloque_color1 = scrapertools.find_single_match(data, '<div class="play_list_box hide show">.*?<div class="player_infotip">.*?Servidor(.*?)</ul>')
    bloque_color2 = scrapertools.find_single_match(data, '<div class="play_list_box hide ">.*?<div class="player_infotip">.*?Servidor(.*?)</ul>')

    bloques = bloque_color1 + bloque_color2

    matches = re.compile('<li><a href="(.*?)"', re.DOTALL).findall(bloques)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PanDrama', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PanDrama', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PanDrama', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PanDrama', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PanDrama', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for url in matches[item.page * item.perpage:]:
        episode += 1

        title = str(item.contentSeason) + 'x' + str(episode) + ' ' + item.contentSerieName

        url = host[:-1] + url

        itemlist.append(item.clone( action='findvideos', url = url, title = title, orden = episode,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage,
                                        text_color='coral', orden = '10000' ))

    return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    url = scrapertools.find_single_match(data, '<script type="text/javascript">var player.*?"url":"(.*?)"')

    if url:
        lang = 'Vose'
        if '-dub-' in item.url: lang = 'Lat'

        url = url.replace('\\/', '/')

        if url.startswith('//'): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'directo':
           if url.endswith('.m3u8'): other = 'm3u8'
           elif url.endswith('.mpd'): other = 'mpd'
           elif '.m3u8' in url: other = 'm3u8'
           elif '.mpd' in url: other = 'mpd'
           elif '/v.pandrama.com/' in url: other = 'vid'
           else: other = '?'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, ref = item.url,
                              language = lang, other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.server == 'directo':
        if item.other == 'm3u8':
            itemlist.append(item.clone(server = item.server, url = item.url + '|referer=' + item.ref))
            return itemlist

        elif item.other == 'mpd':
            if platformtools.is_mpd_enabled(): itemlist.append(['mpd', item.url, 0, '', True])
            return itemlist

        item.url = item.url.replace('https://v.pandrama.com/video/', 'https://v.pandrama.com/player/index.php?data=')

        if not 'https://v.pandrama.com/player/index.php?data=' in item.url: item.url = 'https://v.pandrama.com/player/index.php?data=' + item.url

        data = httptools.downloadpage(item.url, headers = {'Referer': item.ref}).data

        url = scrapertools.find_single_match(data, '<source src="(.*?)"')

        if not url:
            itemlist.append(item.clone(server = item.server, url = item.url + '|referer=' + item.ref))
            return itemlist
        else:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            itemlist.append(item.clone(server = servidor, url = url))
    else:
        itemlist.append(item.clone(server = item.server, url = item.url))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<li class="searchlist_item">(.*?)</li>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'data-original="(.*?)"')

        year = scrapertools.find_single_match(match, '<span>Año：</span>(.*?)</p>')
        year = year.replace('&nbsp;', '').strip()

        if not year: year = '-'

        plot = scrapertools.find_single_match(match, '<span>Sinopsis：</span>(.*?)</p>')

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'vodsearch/-------------/?wd=' + texto.replace(" ", "+") + '&submit='
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
