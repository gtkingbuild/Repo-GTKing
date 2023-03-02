# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.doramasjc.com/'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'all', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'category/doblado/?tr_post_type=1', doblado=True, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'category/doblado/?tr_post_type=2', doblado=True, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '>Dramas por Genero<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        if title == 'Doblado': continue

        if item.search_type == 'movie': url = url + '?tr_post_type=1'
        else: url = url + '?tr_post_type=2'

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)>Sobre DoramasJC<')

    matches = re.compile('<article(.*?)</article>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3 class="Title">(.*?)</h3>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, '<span class="Year">(.*?)</span>')
        if not year: year = '-'

        lang = ''
        if item.doblado: lang = 'Lat'

        tipo = 'movie' if '/movie/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = lang, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, languages = lang, fmt_sufijo=sufijo, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="wp-pagenavi">' in data:
            next_url = scrapertools.find_single_match(data, '<div class="wp-pagenavi">.*?class="page-numbers current">.*?href="(.*?)"')
            if next_url:
                if '/page/' in next_url:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    temporadas = re.compile('data-tab="(.*?)"', re.DOTALL).findall(data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = int(tempo)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = int(tempo), page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '&quot;' in data: data = data.replace('&quot;', '"')

    bloque = scrapertools.find_single_match(data, 'data-tab="%s"(.*?)</table>' % (str(item.contentSeason)))

    if '>Capítulo' in data: patron = '<span class="Num">.*?<a href="(.*?)".*?src="(.*?)".*?>Capítulo(.*?)</a>'
    elif '>Episodio' in data: patron = '<span class="Num">.*?<a href="(.*?)".*?src="(.*?)".*?>Episodio(.*?)</a>'
    else: patron = '<span class="Num">.*?<a href="(.*?)".*?src="(.*?)".*?<td class="MvTbTtl">.*?">(.*?)</a>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramasJc', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasJc', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasJc', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasJc', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramasJc', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for url, thumb, epis, in matches[item.page * item.perpage:]:
        epis = epis.strip()
        if not epis: continue

        if thumb.startswith('//'): thumb = 'https:' + thumb

        title = str(item.contentSeason) + 'x' + str(epis) + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
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

    IDIOMAS = {'Latino': 'Lat', 'Castellano': 'Esp', 'Sub': 'Vose', 'Vose': 'Vose', 'VO': 'VO'}

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '&quot;' in data: data = data.replace('&quot;', '"')

    patron = 'data-tplayernv="Opt(.*?)"><span>(.*?)</span>.*?<span>(.*?)</span>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    ses = 0

    for opt, srv, lang_qlty in matches:
        ses += 1

        srv = srv.lower()

        if 'hqq' in srv or 'waaw' in srv or 'netu' in srv: continue
        elif 'ok.ru' in srv: srv = 'okru'

        if item.languages: lang = str(item.languages)
        else:
           lang = scrapertools.find_single_match(lang_qlty, '(.*?)-').strip()
           if 'Sub ' in lang: lang = 'Sub'
           elif ' Latino' in lang: lang = 'Lat'
           elif ' Castellamo' in lang: lang = 'Esp'

        qlty = scrapertools.find_single_match(lang_qlty, '.*?-(.*?)$').strip()

        url = scrapertools.find_single_match(data, 'id="Opt' + str(opt) + '.*?src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, 'src="(.*?)"')

        if url:
            servidor = servertools.corregir_servidor(srv)

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, other = servidor,
                                  quality = qlty, language = IDIOMAS.get(lang, lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, '<div class="Video"><iframe.*?src="(.*?)"')

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

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
