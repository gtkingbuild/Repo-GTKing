# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seriesretro.com/'


perpage = 20


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'lista-series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host + 'lista-series/episodios-agregados-actualizados/', search_type = 'tvshow', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Animación', action = 'list_all', url = host + 'category/animacion/', search_type = 'tvshow', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Live action', action = 'list_all', url = host + 'category/liveaction/', search_type = 'tvshow', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    patron = 'class="menu-item menu-item-type-taxonomy menu-item-object-category.*?<a href="(.*?)">(.*?)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title in matches:
        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( action = "list_all", title = title, url = url, text_color = 'hotpink' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1935, -1):
        itemlist.append(item.clone( title = str(x), url = host + '?s=trfilter&trfilter=1&years%5B%5D=' + str(x), action = 'list_all', text_color = 'hotpink' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        letras = letra.lower()

        url = host + 'letter/' + letras + '/'

        itemlist.append(item.clone( action = 'list_alfa', title = letra, url = url, text_color = 'hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(match, '<h3 class="Title">(.*?)</h3>')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="([^"]+)"')
        if not thumb: thumb = scrapertools.find_single_match(match, '<img src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, '<span class="Year">(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '<span class=Year>(.*?)</span>')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        title = title.replace('&#038;', '&')

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

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
            if '<div class=wp-pagenavi>' in data:
                next_url = scrapertools.find_single_match(data, 'class="page-numbers current".*?href="(.*?)"')

                if next_url:
                    if '/page/' in next_url:
                        itemlist.append(item.clone( action = 'list_all', page = 0, url = next_url, title = 'Siguientes ...', text_color='coral' ))

    return itemlist


def list_alfa(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</tr>')

    num_matches = len(matches)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<strong>(.*?)</strong>').strip()
        if not url or not title: continue

        if '/aplicacion-oficial-de-seriesretro-com/' in url: continue

        thumb = scrapertools.find_single_match(match, ' data-src="([^"]+)')

        year = scrapertools.find_single_match(match, '<strong>.*?</td><td>Serie</td><td>(\d{4})</span>')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<article (.*?)</article>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

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
        if '<div class="wp-pagenavi"' in data:
            next_url = scrapertools.find_single_match(data, 'class="page-numbers current".*?href="(.*?)"')

            if next_url:
                if '/page/' in next_url:
                    itemlist.append(item.clone (url = next_url, title = 'Siguientes ...', action = 'list_epis', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile(' data-tab="(.*?)">Temporada', re.DOTALL).findall(data)

    for tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    season = str(item.contentSeason)

    bloque = scrapertools.find_single_match(data, ' data-tab="' + season + '">.*?<tbody>(.*?)</tbody>' )

    matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?)</tr>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for data_epi in matches[item.page * item.perpage:]:
        title = scrapertools.find_single_match(data_epi, ' alt="Imagen.*?<a href=.*?>(.*?)</a>')
        if not title: title = scrapertools.find_single_match(data_epi, ' alt=.*?Imagen.*?<a href=.*?>(.*?)</a>')

        url = scrapertools.find_single_match(data_epi, '<a href="(.*?)"')

        if not url or not title: continue

        episode = scrapertools.find_single_match(data_epi, '<span class="Num">(.*?)</span>')

        thumb = scrapertools.find_single_match(data_epi, '<img src="([^"]+)"')
        thumb = 'https:' + thumb

        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

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

    matches = scrapertools.find_multiple_matches(data, 'data-tplayernv="Opt(.*?)"><span>(.*?)</span>')

    ses = 0

    for opt, servidor in matches:
        ses += 1

        servidor = servidor.replace('<strong>', '').replace('</strong>', '')

        srv = servidor.lower().strip()

        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '.*?src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '.*?src=&quot;(.*?)&quot;')

        if url.startswith('//') == True: url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '.*?src=&quot;(.*?)&quot;')

        if not servidor or not url: continue

        if 'opción' in servidor:
            link_other = servidor
            servidor = 'directo'
        elif servidor == 'anavids':
            link_other = servidor
            servidor = 'directo'
        elif servidor == 'analu':
            link_other = servidor
            servidor = 'directo'
        else: link_other = ''

        if servidor == 'various': link_other = servertools.corregir_other(srv)

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = 'Lat', other = link_other ))

    # ~ Descargas
    matches = scrapertools.find_multiple_matches(data, '<span class="Num">(.*?)</tr>')

    for match in matches:
        ses += 1

        servidor = scrapertools.find_single_match(match, 'alt="Descargar(.*?)">')
        servidor = servidor.replace('.', '').lower().strip()

        if not servidor: continue

        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        other = 'D'

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = 'Lat', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    if url.startswith(host):
        if item.other == 'D' or 'D ' in item.other :
            url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get('location', '')
        else:
            data = do_downloadpage(url)

            if item.other == 'anavids':
                url = scrapertools.find_single_match(data.lower(), '<iframe src="(.*?)"')

                data = do_downloadpage(url)

                url = scrapertools.find_single_match(str(data), 'sources.*?"(.*?)"')
            else:
                url = scrapertools.find_single_match(data, 'src="(.*?)"')

    if url:
        if url.startswith('//') == True: url = 'https:' + url

        if '/www.analu.xyz/' in url:
            return 'Servidor [COLOR plum]NO soportado[/COLOR]'
        elif '/gdriveplayer.io/' in url:
            return 'Servidor [COLOR plum]NO soportado[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor:
            url = servertools.normalize_url(servidor, url)

            if 'zplayer' in url: url += "|referer=%s" % host

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
