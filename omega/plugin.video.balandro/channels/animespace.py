# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

if PY3:
    import urllib.parse as urllib
else:
    import urllib


import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://animespace.club/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    # ~ 30/11/2023
    if data.startswith("b'"):
        if not 'search?q=' in url: platformtools.dialog_notification('AnimeSpace', '[COLOR red]Re-direcciona a Web Maliciosa[/COLOR]')
        data = ''

    return data


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_anime', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'emision', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'categoria/pelicula', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'tvshow' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    text_color = 'springgreen'

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'categoria/anime', search_type = 'tvshow', text_color=text_color ))
    itemlist.append(item.clone( title = 'Caricaturas', action = 'list_all', url = host + 'categoria/caricaturas', search_type = 'tvshow', text_color=text_color ))
    itemlist.append(item.clone( title = 'Cortos', action = 'list_all', url = host + 'categoria/corto', search_type = 'tvshow', text_color=text_color ))
    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + 'categoria/especial', search_type = 'tvshow', text_color=text_color ))
    itemlist.append(item.clone( title = 'Live action', action = 'list_all', url = host + 'categoria/live-action', search_type = 'tvshow', text_color=text_color ))
    itemlist.append(item.clone( title = 'Onas', action = 'list_all', url = host + 'categoria/ona', search_type = 'tvshow', text_color=text_color ))
    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'categoria/ova', search_type = 'tvshow', text_color=text_color ))
    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'categoria/pelicula', search_type = 'movie', text_color=text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<article.*?href="([^"]+)">.*?src="([^"]+)".*?<h3 class="Title">([^<]+)</h3>.*?</i>([^<]+)'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title, type in matches:
        type = type.strip().lower()

        thumb = thumb.replace("200/", "800/").replace("280/", "1120/")

        title = title.replace('&#039;', "'").replace('&quot;', "")

        SerieName = title

        if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]
        if ':' in SerieName: SerieName = SerieName.split(":")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '"page-item active">.*?</a>.*?<a class="page-link" href="([^"]+)">')

        if next_page:
            actual_page = scrapertools.find_single_match(item.url, '([^\?]+)?')

            itemlist.append(item.clone( title = 'Siguientes ...', url = actual_page + next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<section class="caps">.*?</section>')

    patron = '<article.*?<a href="([^"]+)">.*?data-src="([^"]+)".*?<span class="episode">.*?</i>([^<]+)</span>.*?<h2 class="Title">([^<]+)</h2>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for url, thumb, epis, title in matches:
        title = title.replace('&#039;', "'").replace('&quot;', "")

        SerieName = title

        if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]
        if ':' in SerieName: SerieName = SerieName.split(":")[0]

        SerieName = SerieName.strip()

        titulo = '%s - %s' % (title, epis)

        thumb = thumb.replace("290/", "840/").replace("165/", "480/")

        episode = scrapertools.find_single_match(epis, 'Episodio(.*?)$').strip()
        if not episode: episode = 1

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb,
                                            contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=episode,
                                            infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    anime_info = eval(scrapertools.find_single_match(data, "var anime_info = ([^;]+);"))

    if not anime_info: return itemlist

    matches = eval(scrapertools.find_single_match(data, "var episodes = ([^;]+);"))

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimeSpace', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeSpace', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeSpace', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeSpace', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeSpace', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimeSpace', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        epis = match

        title = "1x%s - %s" % (str(epis).zfill(2),str(item.contentSerieName))

        url = '%sver/%s-capitulo-%s' % (host, anime_info[0], epis)

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

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    ses = 0

    matches = re.compile('id="Opt\d+">.*?src=(.*?) frameborder', re.DOTALL).findall(data)

    for url in matches:
        ses += 1

        url = url.replace('&quot;', '')

        if "/stream/" in url:
            new_data = do_downloadpage(url)

            url = scrapertools.find_single_match(new_data, '<source src="([^"]+)"')

        else:
            url = scrapertools.find_single_match(url, '.*?url=([^&]+)?')
            url = urllib.unquote(url)

        if url:
            if url.startswith('//'): url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language='Vose' ))

    # ~ descargas
    bloque = scrapertools.find_single_match(data, '<table class="table">(.*?)</table>')

    matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)"')

    for url in matches:
        ses += 1

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language='Vose' ))


    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

