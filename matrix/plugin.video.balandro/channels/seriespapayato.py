# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://papayaseries.net/'


def do_downloadpage(url, post=None, referer=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://seriespapaya.to/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action='list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action='generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    matches = scrapertools.find_multiple_matches(data, '<li id="menu-item-.*?<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == 'Inicio': continue
        elif title == 'Generos': continue

        title = title.replace('&amp;', '&').strip()

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return sorted(itemlist, key=lambda it: it.title)


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        letras = letra.lower()

        url = host + 'letra/' + letras + '/'

        itemlist.append(item.clone( action = 'list_letra', title = letra, url = url ))

    itemlist.append(item.clone(action = "list_letra", url = host + 'letra/0-9/', title = '0-9'))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article class="(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')
        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' data-src="(.*?)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, ' <span class="Date">(.*?)</span>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<a class="page-link current"' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link" href="(.*?)">')

            if next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def list_letra(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</div>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' <a href="([^"]+)"')
        title = scrapertools.find_single_match(match, ' <strong>(.*?)</strong>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' data-lazy-src="(.*?)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, ' <td>Serie.*?<td>(.*?)</td>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<a class="page-link current"' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?<a class="page-link" href="(.*?)">')

            if next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_letra', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    seasons = scrapertools.find_multiple_matches(data, '<section class="Season.*?<a href="(.*?)".*?<span>(.*?)</span>')

    for url, tempo in seasons:
        title = 'Temporada ' + tempo

        if len(seasons) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.url = url
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, page = 0, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    patron = '<td><span class="Num">(.*?)</span>.*?<a href="(.*?)".*?src="(.*?)".*?<td class="MvTbTtl"><a href=.*?>(.*?)</a>'

    episodes = scrapertools.find_multiple_matches(data, patron)

    if item.page == 0:
        sum_parts = len(episodes)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesPapayaTo', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesPapayaTo', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesPapayaTo', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesPapayaTo', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesPapayaTo', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for epis, url, thumb, title in episodes[item.page * item.perpage:]:
        titulo = str(item.contentSeason) + 'x' + epis + ' ' + title

        if thumb.startswith('//'): thumb = 'https:' + thumb

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(episodes) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['360P', '480P', '720P', '1080P']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Español Latino': 'Lat', 'Castellano': 'Esp', 'VOSE': 'Vose'}

    data = do_downloadpage(item.url)

    patron = '<li data-typ="episode" data-key="(.*?)" data-id="(.*?)".*?<p class="AAIco-language">(.*?)</p>.*?<p class="AAIco-dns">(.*?)</p>.*?<p class="AAIco-equalizer">(.*?)</p>'
    links = scrapertools.find_multiple_matches(data, patron)

    for data_key, data_id, lang, servidor, qlty in links:
        if not data_key or not data_id: continue

        servidor = servertools.corregir_servidor(servidor)

        other = servidor
        if other == 'cinemaupload': other = ''

        url = host + '?trembed=' + data_key + '&trid=' + data_id + '&trtype=2'

        itemlist.append(Item(channel = item.channel, action = 'play', server='directo', title = '', url = url,
                                                     language = IDIOMAS.get(lang,lang), quality = qlty, quality_num = puntuar_calidad(qlty), other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    new_url = scrapertools.find_single_match(data, ' src="(.*?)"')
    if not new_url: new_url = scrapertools.find_single_match(data, ' SRC="(.*?)"')

    if new_url:
        if '/cinemaupload.com/' in new_url:
            new_url = new_url.replace('/cinemaupload.com/', '/embed.cload.video/')

            data = do_downloadpage(new_url, raise_weberror = False)

            url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')

            if url:
                if '/download/' in url:
                    url = url.replace('//download/', '/files/').replace('/download/', '/files/')
                    itemlist.append(item.clone( url = url, server = 'directo' ))
                    return itemlist

                elif '/manifest.mpd' in url:
                    if platformtools.is_mpd_enabled(): itemlist.append(['mpd', url, 0, '', True])
                    itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])

                else: itemlist.append(['m3u8', url])

                return itemlist

        servidor = servertools.get_server_from_url(new_url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor:
           itemlist.append(item.clone(server = servidor, url = new_url))
        else:
           itemlist.append(item.clone(server = 'directo', url = new_url))

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

