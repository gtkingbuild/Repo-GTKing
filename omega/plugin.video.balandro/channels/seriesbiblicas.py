# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seriesbiblicas.net/'


perpage = 35


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    if not data:
        if not 'search/' in url:
            if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('SeriesBiblicas', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

            # ~ timeout = config.get_setting('channels_repeat', default=30)
            # ~ 5/6/24
            timeout = 50

            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    # ~ itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    # ~ itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    # ~ itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_ser', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos capítulos', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_ser', url = host, search_type = 'tvshow', group = 'lasts', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Recomendadas', action = 'list_ser', url = host, search_type = 'tvshow', group = 'recom' ))

    itemlist.append(item.clone( title = 'Más series', action = 'otras', search_type = 'tvshow' ))

    return itemlist


def otras(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Antorchas heroes de la fé', action = 'temporadas', url = host + 'antorchas-heroes-de-la-fe/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'El superlibro', action = 'temporadas', url = host + 'el-superlibro/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'La vindicación', action = 'temporadas', url = host + 'la-vindicacion-completa/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Tetelestai', action = 'temporadas', url = host + 'tetelestai/', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>PELÍCULAS DISPONIBLES<(.*?)>SIGUENOS<')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="wpb_text_column wpb_content_element(.*?)</div></div>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        link = scrapertools.find_single_match(match, 'data-mfp-src="(.*?)"')

        title = scrapertools.find_single_match(match, '<p><!--(.*?)-->').strip()

        if not link or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(title, '<span>(\d{4})')
        if year:
             title = title.replace('(' + year + ')', '').strip
        else: year = '-'

        if link.startswith("//"): link = 'https:' + link

        itemlist.append(item.clone( action='findvideos', link=link, title=title, thumbnail=thumb,
                                    contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))

    return itemlist


def list_ser(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if item.group == 'recom':
        bloque = scrapertools.find_single_match(data, '>SERIES RECOMENDADAS<(.*?)</script>')
    elif item.group == 'lasts':
        bloque = scrapertools.find_single_match(data, '>SERIES DISPONIBLES<(.*?)</script>')
    else:
        bloque = scrapertools.find_single_match(data, '>SERIES<(.*?)>MÁS SERIES<')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)"')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        if match == '#': continue

        if '#spu-' in match:
            match = match.replace('#spu-', '#spu-bg-')

            match = scrapertools.find_single_match(str(data), match + '.*?<center>.*?<a href="(.*?)"')

            if match == '#': continue

        title = match.replace(host, '').replace('http://seriesbiblicas.net/', '').replace('/', '').strip()

        if not title: continue

        titulo = title.replace('-hd-google-drive', ' ').replace('-google-drive', ' ').replace('-hd-ok-ru', ' ').replace('-ok-ru', ' ').replace('-hd', ' ').replace('-sd', ' ').strip()

        titulo = titulo.replace('-recordtv-subtitulada', ' ').replace('-recordtv', ' ').strip()
        titulo = titulo.replace('-en-espanol-2', ' ').replace('-en-espanol', ' ').replace('-portugues', ' ').replace('-audio-latino', ' ').replace('-latino', ' ').strip()
        titulo = titulo.replace('-sub', ' ').replace('-imagentv', ' ').replace('-unife', ' ').replace(' sub', ' ').replace(' subtitulada', ' ').strip()

        SerieName = titulo.replace('-', ' ').strip()

        title = title.replace('-', ' ').strip().capitalize()

        itemlist.append(item.clone( action='temporadas', url=match, title=title,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_ser', text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>CAPÍTULOS MÁS RECIENTES<(.*?)</div></div>')

    matches = re.compile('<a href="(.*?)".*?data-lazy-src="(.*?)"', re.DOTALL).findall(bloque)

    for url, thumb in matches:
        title = url

        title = url.replace('-hd-google-drive', ' ').replace('-google-drive', ' ').replace('-hd-ok-ru', ' ').replace('-ok-ru', ' ').replace('-hd', ' ').replace('-sd', ' ').strip()

        title = title.replace('-recordtv-subtitulada', ' ').replace('-recordtv', ' ').strip()
        title = title.replace('-en-espanol-2', ' ').replace('-en-espanol', ' ').replace('-portugues', ' ').replace('-audio-latino', ' ').replace('-latino', ' ').strip()
        title = title.replace('-sub', ' ').replace('-imagentv', ' ').replace('-unife', ' ').strip()

        title = title.replace(host, ' ').replace('-', ' ').replace('/', '').strip()

        SerieName = title

        title = title.capitalize()

        itemlist.append(item.clone( action='temporadas', url=url, title=title,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if not ' TEMPORADA<' in data:
        if not '>TEMPORADA ' in data:
            if not '>SEASON ' in data:
                if config.get_setting('channels_seasons', default=True):
                    if not item.contentSerieName: item.contentSerieName = item.title
                    platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR tan]Sin temporadas[/COLOR]')

                item.page = 0
                item.contentSerieName = item.title
                item.contentType = 'season'
                item.contentSeason = 1
                itemlist = episodios(item)
                return itemlist

    temporadas = re.compile('>TEMPORADA (.*?)</span>', re.DOTALL).findall(data)
    if not temporadas: temporadas = re.compile(' TEMPORADA<(.*?)</p>', re.DOTALL).findall(data)
    if not temporadas: temporadas = re.compile('>SEASON (.*?)</span>', re.DOTALL).findall(data)

    i = 0

    for tempo in temporadas:
        if 'Episode' in tempo: continue
        elif 'Capítulo' in tempo: continue

        i +=1

        if tempo == '/span>': tempo = str(i)
        elif '<center>' in tempo: tempo = scrapertools.find_single_match(tempo, '(.*?)</div>').strip()
        elif '</div>' in tempo: tempo = tempo.replace('</div>', '').strip()

        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0

            if not item.contentSerieName: item.contentSerieName = item.title

            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        if not item.contentSerieName: item.contentSerieName = item.title

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0,
                                    contentSerieName = item.contentSerieName, contentType = 'season', contentSeason = tempo, i = i, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '>TEMPORADA ' in data:
        bloque = scrapertools.find_single_match(data, '>TEMPORADA ' + str(item.contentSeason) + '(.*?)</script>')

        if not bloque: bloque = scrapertools.find_single_match(data, '>TEMPORADA ' + str(item.contentSeason) + '(.*?)</div></div></div></center></div></div>')

    elif ' TEMPORADA<' in data:
        text_season = ''

        if item.i == 1: text_season = '>PRIMERA'
        elif item.i == 2: text_season = '>SEGUNDA'
        elif item.i == 3: text_season = '>TERCERA'
        elif item.i == 4: text_season = '>CUARTA'
        elif item.i == 5: text_season = '>QUINTA'
        elif item.i == 6: text_season = '>SEXTA'

        bloque = scrapertools.find_single_match(data, text_season + ' TEMPORADA<.*?</p>(.*?)</center>')
        if not bloque:
            if '>CAPITULOS<' in data:
                bloque = scrapertools.find_single_match(data, '>CAPITULOS</span></center>(.*?)</div></div></div></center>')

    elif '>SEASON ' in data:
        bloque = scrapertools.find_single_match(data, '>SEASON ' + str(item.contentSeason) + '(.*?)</script>')

    elif '>CAPÍTULOS<' in data:
        bloque = scrapertools.find_single_match(data, '>CAPÍTULOS</span>(.*?)</div></div></div></div></div></div></div>')

    else:
        bloque = scrapertools.find_single_match(data, '>CAPITULOS</span></center>(.*?)</center>')
        if not bloque: bloque = scrapertools.find_single_match(data, '>CAPITULOS</span>(.*?)</div></div></div></center>')

    matches = re.compile('<div class="su-spoiler-title">.*?</span>(.*?)</div>.*?<a href="(.*?)".*?</i>(.*?)</div></div>', re.DOTALL).findall(bloque)
    if not matches: matches = re.compile("class='sa_hover_(.*?)'" + '.*?data-mfp-src="(.*?)".*?<noscript>(.*?)</noscript>', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesBiblicas', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesBiblicas', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesBiblicas', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesBiblicas', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesBiblicas', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesBiblicas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    i = 0

    for title, url, resto in matches[item.page * item.perpage:]:
        i += 1

        link = ''
        if url.startswith("//"): url = 'https:' + url

        if title == 'container':
            title = item.contentSerieName
            link = url
            url = ''

        titulo = str(item.contentSeason) + 'x' + str(i) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, link = link, resto = resto,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=str(i) ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, i = i, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    lang = 'Lat'
    if 'PT' in item.title: lang = 'Pt'
    elif ' Sub ' in item.title: lang = 'Vose'
    elif '- Sub' in item.title: lang = 'Vose'

    if item.link:
        if item.link.startswith("//"): item.link = 'https:' + item.link

        servidor = servertools.get_server_from_url(item.link)
        servidor = servertools.corregir_servidor(servidor)

        if '/ok.ru' in item.link: servidor = 'okru'
        elif '/drive.' in item.link: servidor = 'gvideo'

        url = servertools.normalize_url(servidor, item.link)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang ))

        return itemlist

    ses = 0

    if item.url:
        ses += 1

        if item.url.startswith("//"): item.url = 'https:' + item.url

        url = item.url

        if not url == '#':
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(url)

            if '/ok.ru' in url: servidor = 'okru'
            elif '/drive.' in url: servidor = 'gvideo'

            url = servertools.normalize_url(servidor, url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang ))

    if item.resto:
        links = scrapertools.find_multiple_matches(item.resto, '<a href="(.*?)"')
        if 'data-mfp-src="' in item.resto: links = scrapertools.find_multiple_matches(item.resto, 'data-mfp-src="(.*?)"')
        if not links: links = scrapertools.find_multiple_matches(item.resto, 'data-mfp-src="(.*?)"')

        for link in links:
            ses += 1

            if link == '#': continue

            if link.startswith("//"): link = 'https:' + link

            servidor = servertools.get_server_from_url(link)
            servidor = servertools.corregir_servidor(servidor)

            if '/ok.ru' in link: servidor = 'okru'
            elif '/drive.' in link: servidor = 'gvideo'

            link = servertools.normalize_url(servidor, link)

            if not 'http' in link: continue

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link, language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

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

