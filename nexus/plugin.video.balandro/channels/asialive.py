# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://asialiveaction.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'audio-espanol/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'audio-latino/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'anime/', search_type = 'movie', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series-tv/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'audio-espanol/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'audio-latino/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'anime/', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host + 'peliculas/')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = re.compile('<li.*?>([^<]+)<a href="([^"]+)"', re.DOTALL).findall(data)

    for title , url in matches:
        if config.get_setting('descartar_xxx', default=False):
            if title == 'Erótico': continue

        if not url.startswith("http"): url = host + url

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1949, -1):
        url = host + 'estrenos/' + str(x) +'/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'peliculas/')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, '>Calidad<(.*?)</ul>')

    matches = re.compile('<li.*?>([^<]+)<a href="([^"]+)"', re.DOTALL).findall(data)

    for title , url in matches:
        if not url.startswith("http"): url = host + url

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda x: x.title)


def paises(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host + 'peliculas/')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, '>Tipo<(.*?)</ul>')

    matches = re.compile('<li.*?>([^<]+)<a href="([^"]+)"', re.DOTALL).findall(data)

    for title , url in matches:
        if title == 'Películas': continue
        elif title == 'Series': continue
        elif title == 'Animación': continue
        elif 'Audio' in title: continue

        if item.search_type == 'movie': 
            if not 'Movie' in title: continue
        else:
            if not 'Drama' in title: continue

        if not url.startswith("http"): url = host + url

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = text_color ))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron  = '(?is)class="TPost C">.*?href="([^"]+)".*?'
    patron += 'src="([^"]+)".*?>.*?'
    patron += '(?:T|t)itle">([^<]+)<.*?'
    patron += '(?:Y|y)ear">([^<]+)<.*?'
    patron += 'class="Genre">(.*?)</p'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, year, type in matches:
        if not url or not title: continue

        if not thumb.startswith("http"): thumb = "https:" + thumb

        title = title.replace('&#8211;', '').replace('&#8217;', "'")

        tipo = 'movie' if 'Movie' in type else 'tvshow'

        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            SerieName = title

            if "(Completo)" in SerieName: SerieName = SerieName.split("(Completo)")[0]
            if "(Completa)" in SerieName: SerieName = SerieName.split("(Completa)")[0]

            if "Temporada" in SerieName: SerieName = SerieName.split("Temporada")[0]
            if "Completa" in SerieName: SerieName = SerieName.split("Completa")[0]

            if " (" in SerieName: SerieName = SerieName.split(" (")[0]

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentSerieName=SerieName, contentType='tvshow', contentSeason = 1, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'class="next page-numbers" href="([^"]+)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if config.get_setting('channels_seasons', default=True):
        title = 'Sin temporadas'

        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#039;', "'").replace('&#8217;', "'"), '[COLOR tan]' + title + '[/COLOR]')

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

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Ver Online(.*?)</div></div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a target="_blank".*?class="fa fa-download".*?href="(.*?)".*?<span>(.*?)</span>')

    if matches:
        if '<label for="toggle' in data:
            matches2 = scrapertools.find_multiple_matches(bloque, 'class="fa fa-download".*?<span>(.*?)</span>.*?href="(.*?)"')
            if matches2: matches = matches + matches2

    if not matches: matches = scrapertools.find_multiple_matches(bloque, 'class="fa fa-download".*?<span>(.*?)</span>.*?href="(.*?)"')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AsiaLive', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AsiaLive', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AsiaLive', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AsiaLive', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AsiaLive', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AsiaLive', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, epis, in matches[item.page * item.perpage:]:
        e_url = url
        e_epis = epis

        if 'Episodio' in e_url:
            url = e_epis
            epis = e_url

        epis = epis.strip()

        epis = scrapertools.find_single_match(epis, 'Episodio(.*?)$').strip()

        if not epis: epis = 1

        if item.contentSerieName: titulo = item.contentSerieName
        else: titulo = item.contentTitle

        if item.contentType == 'movie': item.contentSeason = 1

        title = str(item.contentSeason) + 'x' + str(epis) + ' ' + titulo

        itemlist.append(item.clone( action='findvideos', url = url, title = title,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

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

    IDIOMAS = {'Esp': "Esp", 'Lat': 'Lat', 'Sub': 'Vose'}

    if '/paste/' in item.url:
        data = do_downloadpage(item.url)
    else:
        item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')

        data = do_downloadpage(item.url)

        data = data.replace('&quot;', '"').replace('&amp;', '&').replace('#038;', '&')

        url = scrapertools.find_single_match(data, '<a rel="nofollow" target="_blank" href="([^"]+)"')
        if not url: url = scrapertools.find_single_match(data, '<a target="_blank" class="fa fa-download" href="([^"]+)"')

        if url:
            data = do_downloadpage(url)

    ses = 0

    matches = scrapertools.find_multiple_matches(data, 'var videos([A-z]{3}) = \[([^<]+)</script>')

    for lang, links in matches:
        ses += 1

        lang = IDIOMAS.get(lang, lang)

        matches  = scrapertools.find_multiple_matches(links, "(http.*?)'")

        for url in matches:
            ses += 1

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            other = ''

            if servidor == 'various': other = servertools.corregir_other(url)
            elif servidor == 'directo':
               if '/bestomanga/' in url: other = 'Mailru'

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')

    if '/bestomanga/' in item.url:
        data = do_downloadpage(item.url)

        _id = scrapertools.find_single_match(data, '"video":.*?/meta/(.*?)"')

        if _id:
            url = 'https://my.mail.ru/video/embed/' + _id

    if url:
        if not url.startswith("http"): url = "https:" + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
