# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://areshd.com/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Generos<(.*?)</ul>')

    matches = re.compile('<a href="([^"]+)">([^<]+)').findall(bloque)

    for url, title in matches:
        url = host[:-1] + url

        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url ))

    if itemlist:
        itemlist.append(item.clone( title = 'Documental', action = 'list_all', url = host + 'genero/documental' ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)>Copyright ©')

    matches = scrapertools.find_multiple_matches(bloque, '<a class="Posters-link"(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, '<img alt="(.*?)"')

        if not url or not title: continue

        url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'srcSet=".*?url=(.*?)&amp;')

        year = scrapertools.find_single_match(match, '<p>.*? ( <!-- -->(.*?)<!-- -->')
        if not year: year = '-'

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<span class="page-link current">.*?<a href="(.*?)"')

        if next_url:
            if '/pagina/' in next_url:
                next_url = host[:-1] + next_url

                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('data-toggle="tab">.*?<!-- -->(.*?)<!-- -->', re.DOTALL).findall(data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
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

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    block = scrapertools.find_single_match(str(data), '"seasons"(.*?)"titles"')

    if not block: return itemlist

    bloque = scrapertools.find_single_match(str(block), '{"number":' + str(item.contentSeason) + '.*?"episodes"(.*?)}]}')

    matches = re.compile('"title":"(.*?)".*?"number":(.*?),.*?"image":"(.*?)".*?"slug":"(.*?)"', re.DOTALL).findall(str(bloque))

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AresHd', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AresHd', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AresHd', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AresHd', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AresHd', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for title, epis, thumb, url in matches[item.page * item.perpage:]:
        name = scrapertools.find_single_match(url, '/.*?/(.*?)/')

        url = host + 'episodio/' + name + '-temporada-' + str(item.contentSeason) + '-episodio-' + epis

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

    data = do_downloadpage(item.url)

    block = scrapertools.find_single_match(data, '<div class="player"><div class="VideoPlayer Bglg">(.*?)</ul></div>')

    if not block: return itemlist

    idiomas = scrapertools.find_multiple_matches(block, '<li class="pres"><a class="playr">(.*?)</a></li>')

    bloques = scrapertools.find_multiple_matches(data, '<ul class="TbVideoNv nav nav-tabs hide" role="tablist">(.*?)</ul>')

    ses = 0

    i = 0

    for bloque in bloques:
         matches = scrapertools.find_multiple_matches(bloque, '<li class="pres" data-tr="(.*?)".*?a class="playr">(.*?)</a>')

         for link, srv in matches:
             ses += 1

             if i == 0: lang = idiomas[0]
             elif i == 1: lang = idiomas[1]
             elif i == 2: lang = idiomas[2]
             else: lang =''

             if 'Latino' in lang: lang = 'Lat'
             elif 'Castellano' in lang or 'Español' in lang: lang = 'Esp'
             elif 'Subtitulado' in lang or 'VOSE' in lang: lang = 'Vose'
             else: lang = '?'

             if 'youtube' in srv: continue
             elif 'waaw' in srv or 'hqq' in srv or 'netu' in srv: continue

             itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = link,
                                   language = lang, other = srv.capitalize() ))

         i += 1

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    data = do_downloadpage(url)

    vid = scrapertools.find_single_match(data, "var url = '(.*?)'")

    if vid: url = vid

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        if '/cinestart.streams3.com/' in url: return itemlist

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'zplayer': url = url + '|' + host

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search/' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

