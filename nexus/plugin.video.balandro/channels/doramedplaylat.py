# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://doramedplay.com/'


sub_host = 'https://doramedplay.net/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Subtituladas', action = 'list_all', url = sub_host + 'movies/', sub_host = True, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Màs vistas', action = 'list_all', url = host + 'tendencias-2/?get=movies', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Mejor valoradas', action = 'list_all', url = host + 'ratings-2/?get=movies', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tvshows/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Subtituladas', action = 'list_all', url = sub_host + 'tvshows/', sub_host = True, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Destacadas', action = 'list_all', url = sub_host + 'ratings/', sub_host = True, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Màs vistas', action = 'list_all', url = host + 'tendencias-2/?get=tv', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ratings-2/?get=tv', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'firebrick'

    opciones = [
       ('accion', 'Acción'),
       ('action-adventure', 'Acción Aventura'),
       ('animacion', 'Animación'),
       ('aventura', 'Aventura'),
       ('belica', 'Bélica'),
       ('ciencia-ficcion', 'Ciencia ficción'),
       ('comedia', 'Comedia'),
       ('crimen', 'Crimen'),
       ('drama', 'Drama'),
       ('familia', 'Familia'),
       ('fantasia', 'Fantasía'),
       ('historia', 'Historia'),
       ('misterio', 'Misterio'),
       ('musica', 'Música'),
       ('romance', 'Romance'),
       ('sci-fi-fantasy', 'Sci-Fi & Fantasy'),
       ('suspense', 'Suspense'),
       ('terror', 'Terror')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'genre/' + opc + '/', action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '-2/' in item.url or '/ratings/' in item.url:
        if '>Tendencias<' in data: bloque = scrapertools.find_single_match(data, '>Tendencias<(.*?)<div class="copy"')
        elif '>Ratings<' in data: bloque = scrapertools.find_single_match(data, '>Ratings<(.*?)<div class="copy"')
        elif '>Añadido recientemente<' in data: bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)<div class="copy"')
        elif '>Series de TV<' in data: bloque = scrapertools.find_single_match(data, '>Series de TV<(.*?)<div class="copy"')
        else: bloque = scrapertools.find_single_match(data, '<h1>(.*?)<div class="copy"')

    else:
        if '>Añadido recientemente<' in data: bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)<div class="copy"')
        elif '>Series de TV<' in data: bloque = scrapertools.find_single_match(data, '>Series de TV<(.*?)<div class="copy"')
        else: bloque = scrapertools.find_single_match(data, '<h1>(.*?)<div class="copy"')

    matches = re.compile('<article id="(.*?)</article>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<div class="title"> <h4>(.*?)</h4>')

        if not url or not title: continue

        title = title.replace('&#8211;', '').replace('&#8217;', '')

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, 'div class="metadata"> <span>(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(match, '</h3> <span>.*?,(.*?)</span>').strip()
        if not year: year = '-'

        if '/movies/' in url:
            if item.search_type == 'tvshow': continue

            if 'Sub spn' in title: contentTitle = title.split("Sub spn")[0]
            elif 'Sub spa' in title: contentTitle = title.split("Sub spa")[0]
            elif 'Sub eng' in title: contentTitle = title.split("Sub eng")[0]
            elif 'sub spa' in title: contentTitle = title.split("sub spa")[0]
            elif 'sub eng' in title: contentTitle = title.split("sub eng")[0]
            elif 'all subs' in title: contentTitle = title.split("all subs")[0]
            elif 'all sub' in title: contentTitle = title.split("all sub")[0]
            elif 'sub all' in title: contentTitle = title.split("sub all")[0]
            else: contentTitle = title

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=contentTitle, infoLabels={'year': year} ))
        else:
            if item.search_type == 'movie': continue

            if '(Emisión)' in title: SerieName = title.split("(Emisión)")[0]
            elif '(En Emisión)' in title: SerieName = title.split("(En Emisión)")[0]
            elif '(En emisión)' in title: SerieName = title.split("(En emisión)")[0]
            elif '(en emisión)' in title: SerieName = title.split("(en emisión)")[0]
            elif '(En Emision)' in title: SerieName = title.split("(En Emision)")[0]
            elif '(En emision)' in title: SerieName = title.split("(En emision)")[0]
            elif '(en emision)' in title: SerieName = title.split("(en emision)")[0]
            elif '(Finalizado)' in title: SerieName = title.split("(Finalizado)")[0]
            elif '(finalizado)' in title: SerieName = title.split("(finalizado)")[0]
            elif '(China)' in title: SerieName = title.split("(China)")[0]
            elif '(HD)' in title: SerieName = title.split("(HD)")[0]
            else: SerieName = title

            if 'Sub spn' in SerieName: SerieName = SerieName.split("Sub spn")[0]
            elif 'Sub spa' in SerieName: SerieName = SerieName.split("Sub spa")[0]
            elif 'Sub eng' in SerieName: SerieName = SerieName.split("Sub eng")[0]
            elif 'sub spa' in SerieName: SerieName = SerieName.split("sub spa")[0]
            elif 'sub eng' in SerieName: SerieName = SerieName.split("sub eng")[0]
            elif 'all subs' in SerieName: SerieName = SerieName.split("all subs")[0]
            elif 'all sub' in SerieName: SerieName = SerieName.split("all sub")[0]
            elif 'sub all' in SerieName: SerieName = SerieName.split("sub all")[0]

            SerieName = SerieName.strip()

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_url = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "<a href='(.*?)'")
            if not next_url: next_url = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

            if next_url:
                if '/page/' in next_url:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile("<span class='se-t.*?'>(.*?)</span>", re.DOTALL).findall(data)

    if not temporadas: temporadas = re.compile('<span class="se-t.*?">(.*?)</span>', re.DOTALL).findall(data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = int(tempo)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = int(tempo), page = 0, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<div class='se-c'.*?<span class='se-t.*?'>%s</span>(.*?)</div></div>" % (str(item.contentSeason)))

    if not bloque: bloque = scrapertools.find_single_match(data, '<div class="se-c".*?<span class="se-t.*?">%s</span>(.*?)</div></div>' % (str(item.contentSeason)))

    patron = "<li class='mark-.*?<img src='(.*?)'.*?</div><div class='numerando'>(.*?)</div>.*?<a href='(.*?)'"

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    if not matches: matches = re.compile("<li class='mark-.*?data-src='(.*?)'.*?</div><div class='numerando'>(.*?)</div>.*?<a href='(.*?)'", re.DOTALL).findall(bloque)
    if not matches: matches = re.compile('<li class="mark-.*?data-src="(.*?)".*?</div><div class="numerando">(.*?)</div>.*?<a href="(.*?)"', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramedPlayLat', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramedPlayLat', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramedPlayLat', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramedPlayLat', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramedPlayLat', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramedPlayLat', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, numer, url in matches[item.page * item.perpage:]:
        episode = scrapertools.find_single_match(numer, '.*?-(.*?)$').strip()

        title = str(item.contentSeason) + 'x' + str(episode) + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode ))

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

    matches = re.compile('<iframe.*?src="(.*?)"', re.DOTALL).findall(data)

    ses = 0

    for url in matches:
        ses += 1

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if url.startswith('https://player.doramed.top/'):
            data1 = do_downloadpage(url)

            url = scrapertools.find_single_match(str(data1), "'file':'(.*?)'")

            if url:
                url = 'https://player.doramed.top/' + url

                servidor = 'm3u8hls'

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Lat' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def sub_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Resultados encontrados(.*?)<div class="copy"')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<div class="title"> <h4>(.*?)</h4>')

        if not url or not title: continue

        title = title.replace('&#8211;', '').replace('&#8217;', '')

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(\d+)</span>').strip()
        if not year: year = '-'

        tipo = 'tvshow' if '/tvshows/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            if 'Sub spn' in title: contentTitle = title.split("Sub spn")[0]
            elif 'Sub spa' in title: contentTitle = title.split("Sub spa")[0]
            elif 'Sub eng' in title: contentTitle = title.split("Sub eng")[0]
            elif 'sub spa' in title: contentTitle = title.split("sub spa")[0]
            elif 'sub eng' in title: contentTitle = title.split("sub eng")[0]
            elif 'all subs' in title: contentTitle = title.split("all subs")[0]
            elif 'all sub' in title: contentTitle = title.split("all sub")[0]
            elif 'sub all' in title: contentTitle = title.split("sub all")[0]
            else: contentTitle = title

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=contentTitle, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            if '(Emisión)' in title: SerieName = title.split("(Emisión)")[0]
            elif '(En Emisión)' in title: SerieName = title.split("(En Emisión)")[0]
            elif '(En emisión)' in title: SerieName = title.split("(En emisión)")[0]
            elif '(en emisión)' in title: SerieName = title.split("(en emisión)")[0]
            elif '(En Emision)' in title: SerieName = title.split("(En Emision)")[0]
            elif '(En emision)' in title: SerieName = title.split("(En emision)")[0]
            elif '(en emision)' in title: SerieName = title.split("(en emision)")[0]
            elif '(Finalizado)' in title: SerieName = title.split("(Finalizado)")[0]
            elif '(finalizado)' in title: SerieName = title.split("(finalizado)")[0]
            elif '(China)' in title: SerieName = title.split("(China)")[0]
            elif '(HD)' in title: SerieName = title.split("(HD)")[0]
            else: SerieName = title

            if 'Sub spn' in SerieName: SerieName = SerieName.split("Sub spn")[0]
            elif 'Sub spa' in SerieName: SerieName = SerieName.split("Sub spa")[0]
            elif 'Sub eng' in SerieName: SerieName = SerieName.split("Sub eng")[0]
            elif 'sub spa' in SerieName: SerieName = SerieName.split("sub spa")[0]
            elif 'sub eng' in SerieName: SerieName = SerieName.split("sub eng")[0]
            elif 'all subs' in SerieName: SerieName = SerieName.split("all subs")[0]
            elif 'all sub' in SerieName: SerieName = SerieName.split("all sub")[0]
            elif 'sub all' in SerieName: SerieName = SerieName.split("sub all")[0]

            SerieName = SerieName.strip()

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_url = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "<a href='(.*?)'")

            if next_url:
                if '/page/' in next_url:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'sub_search', text_color = 'coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        itemlist = sub_search(item)
        if itemlist: return itemlist

        item.url = sub_host + '?s=' + texto.replace(" ", "+")
        return sub_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
