# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.doramasmp4.cc/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-online/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'doramas-online/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos capítulos', action = 'last_epis', url = host + 'capitulos-online/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host + 'doramas-online/')

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    genres = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in genres:
        if config.get_setting('descartar_xxx', default=False):
            if '+18' in title: continue
            elif title == 'Erótico': continue

        if item.search_type == 'tvshow':
            if '+18' in title: continue
            elif title == 'Cortometraje': continue
            elif title == 'Documental': continue
            elif title == 'Erótico': continue
            elif title == 'Película de TV': continue

        title = title.replace('&amp;', '&').replace('&#8211;', '').replace(',', ', ')

        title = title.capitalize()

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = text_color ))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)<span class="icon-chevron-right">')
    if not bloque: bloque = scrapertools.find_single_match(data, '</h1>(.*?)<div class="sidebar scrolling"')

    matches = re.compile('<article(.*?)</article>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<div class="title"><h4>(.*?)</h4>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        if '?s=' in item.url: year = '-'
        else:
            year = scrapertools.find_single_match(match, '<span class="imdb">.*?<span>(.*?)</span>').strip()
            if not year: year = scrapertools.find_single_match(match, '<div class="metadata">.*?<span>(.*?)</span>').strip()
            if not year: year = scrapertools.find_single_match(title, ' (\d{4})')

            if year: title = title.replace('(' + year + ')', '').strip()
            else: year = '-'

        tipo = 'movie' if '/pelicula-' in url or '/peliculas-' in url else 'tvshow'

        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            title = title.replace('Ver Pelicula', '').replace('Película', '').replace('Completa', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title="Siguientes ...", action="list_all", url = next_page, text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)<span class="icon-chevron-right">')
    if not bloque: bloque = scrapertools.find_single_match(data, '</h1>(.*?)<div class="sidebar scrolling"')

    matches = re.compile('<article(.*?)</article>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<span class="c">(.*?)</span>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        season = scrapertools.find_single_match(match, '<span class="b">(.*?)x').strip()
        if not season: season = 1

        epis = scrapertools.find_single_match(match, '<span class="b">.*?x(.*?)</span>').strip()
        if not epis: epis = 1

        titulo = str(season) + 'x' + str(epis) + ' ' + title

        SerieName = title

        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]
        elif 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail = thumb, url = url, infoLabels={'year': '-'},
                                    contentType = 'episode', contentSerieName = SerieName, contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title="Siguientes ...", action="last_epis", url = next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if config.get_setting('channels_seasons', default=True):
        title = 'Sin temporadas'

        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR tan]' + title + '[/COLOR]')

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

    b64_id = scrapertools.find_single_match(data, '<input type="hidden" name="action" value="dooplay_login">.*?base64,(.*?)"')

    if not b64_id: return itemlist

    id = base64.b64decode(b64_id).decode("utf-8")

    id = scrapertools.find_single_match(id, '=(.*?)$').strip()

    if not id: return itemlist

    post = {'action': 'seasons', 'id': id}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

    bloque = scrapertools.find_single_match(data, "<span class='title'>Temporada " + str(item.contentSeason) + "(.*?)</ul>")

    matches = re.compile("data-id='(.*?)</div></li>", re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramasMp4Cc', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasMp4Cc', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasMp4Cc', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts > 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                    platformtools.dialog_notification('DoramasMp4Cc', '[COLOR cyan]Cargando elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasMp4Cc', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramasMp4Cc', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, "href='(.*?)'")
        title = scrapertools.find_single_match(match, "<a href='.*?'>(.*?)</a>")

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, "<img src='(.*?)'")

        title = title.replace('&#8211;', "").strip()

        temp = scrapertools.find_single_match(match, "<div class='numerando'>(.*?)-").strip()

        if not temp == str(item.contentSeason): continue
        epis = scrapertools.find_single_match(match, "<div class='numerando'>.*?-(.*?)</div>").strip()
        if not epis: epis = 1

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page= item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '>Subtitulado<' in data: lang = 'Vose'
    else: lang = 'Lat'

    matches = scrapertools.find_multiple_matches(data, '<li id="player-option-.*?data-type="(.*?)".*?data-post="(.*?)".*?data-nume="(.*?)"')

    ses = 0

    for d_type, d_post, d_nume in matches:
        ses += 1

        post = {'action': 'doo_player_ajax', 'post': d_post, 'nume': d_nume, 'type': d_type}

        data1 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

        url = scrapertools.find_single_match(data1, "<iframe.*?src='(.*?)'")

        if url:
            if url.startswith('//'): url = 'https:' + url

            if '.estrenosdoramas.' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            other = ''

            if servidor == 'various': other = servertools.corregir_other(url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith(host):
       url = httptools.downloadpage(item.url, follow_redirects=False).headers.get('location', '')

       if url:
           if '/gounlimited.' in url:
               return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

           if url.startswith('https://odysee.com'):
               data = httptools.downloadpage(url).data

               url = scrapertools.find_single_match(data, '"contentUrl": "(.*?)"')

               if url:
                   itemlist.append(item.clone(server = item.server, url = url))

               return itemlist

           servidor = servertools.get_server_from_url(url)
           servidor = servertools.corregir_servidor(servidor)

           url = servertools.normalize_url(servidor, url)

           itemlist.append(item.clone(server = servidor, url = url))
    else:
        itemlist.append(item.clone(server = item.server, url = item.url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        item.text = texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
