# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://ww2.tuanime.net/'


perpage = 25


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://ww1.tuanime.net/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_animes(item)

def mainlist_animes(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'lista/anime-tv/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_all', url = host + 'lista/nuevos-animes/', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'lista/anime-mas-vistos/', search_type = 'tvshow' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h1>(.*?)<footer>')

    matches = re.compile('<div class="card-llm">(.*?)</a></div>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        SerieName = title.strip()

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, page = 0,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year':'-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<div class="pagenavi">.*?<span class="current".*?<a href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone (url = next_page, page = 0, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'ÚLTIMOS EPISODIOS(.*?)>Últimos Animes')

    matches = re.compile('<div class="card-box">(.*?)</a></div>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        SerieName = title

        if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]

        SerieName = SerieName.strip()

        epis = scrapertools.find_single_match(match, '<div class="episodio">Episodio (.*?)</div>').strip()

        title = title.replace('Capítulo', '[COLOR goldenrod]Capítulo[/COLOR]')

        if url:
            itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb, page = 0,
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Listado de episodios<(.*?)</div></div>')

    matches = re.compile('<a href="(.*?)".*?>(.*?)<i', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimeClub', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeClub', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeClub', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeClub', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeClub', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimeClub', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    i = 0

    for url, title in matches[item.page * item.perpage:]:
        i += 1

        title = title.strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = title,
                                    contentType = 'episode', contentSeason = 1, contentEpisodeNumber = i ))

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
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    blk = scrapertools.find_single_match(str(data), "let (.*?)</script>")

    if not blk: return itemlist

    blk = str(blk).replace('e[', 'e="').replace(']=', '"=')

    blk = str(blk).replace("'lat'", '-lat-').replace("'sub'", '-sub-').replace("'esp'", '-esp-').replace('];', '-')

    blk_lat = scrapertools.find_single_match(str(blk), "-lat-(.*?)-")
    blk_sub = scrapertools.find_single_match(str(blk), "-sub-(.*?)-")
    blk_esp = scrapertools.find_single_match(str(blk), "-lat-(.*?)-")

    ses = 0

    if blk_lat:
        matches = scrapertools.find_multiple_matches(str(blk_lat), "'(.*?)'")

        for match in matches:
            ses += 1

            lang = 'Lat'

            url = match

            if url.startswith('https://player.ojearanime.com/'): url = url.replace('/player.ojearanime.com/', '/waaw.to/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            link_other = ''
            if servidor == 'various': link_other = servertools.corregir_other(url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, 
                                      language = lang, other = link_other ))

    if blk_sub:
        matches = scrapertools.find_multiple_matches(str(blk_sub), "'(.*?)'")

        for match in matches:
            ses += 1

            lang = 'Vose'

            url = match

            if url.startswith('https://player.ojearanime.com/'): url = url.replace('/player.ojearanime.com/', '/waaw.to/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            link_other = ''
            if servidor == 'various': link_other = servertools.corregir_other(url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, 
                                      language = lang, other = link_other ))

    if blk_esp:
        matches = scrapertools.find_multiple_matches(str(blk_esp), "'(.*?)'")

        for match in matches:
            ses += 1

            lang = 'Esp'

            url = match

            if url.startswith('https://player.ojearanime.com/'): url = url.replace('/player.ojearanime.com/', '/waaw.to/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            link_other = ''
            if servidor == 'various': link_other = servertools.corregir_other(url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, 
                                      language = lang, other = link_other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def list_search(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Resultados encontrados:<(.*?)<footer>')

    matches = re.compile('<div class="card-box">(.*?)</a></div>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        SerieName = title.strip()

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, page = 0,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year':'-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'buscar/?q=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
