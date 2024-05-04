# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://doramasqueen.com/'


url_doramas = host + 'doramas.php'
url_lst = host + 'searchBy.php'


perpage = 30


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = url_doramas, search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Últimos episodios', action = 'list_all', url = host + 'ultimoscapitulos.php', group = 'last', search_type = 'tvshow', text_color='cyan' ))

    itemlist.append(item.clone ( title = 'En emisión', action = 'list_lst',
                                 post = {"countries": "", "generos": "", "years": "", "emition": "[\"Si\"]", "submit": ""}, search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Finalizados', action = 'list_lst',
                                 post = {"countries": "", "generos": "", "years": "", "emition": "[\"No\"]", "submit": ""}, search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Películas', action = 'list_all', url = host + 'peliculas.php', search_type = 'movie', text_color='deepskyblue' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Por país', action = 'paises', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
        ('Bixesuales', 'Bixesuales'),
        ('Gays', 'Gays'),
        ('Hetero', 'Hetero'),
        ('Lesbianas', 'Lesbianas'),
        ('Queer', 'Queer'),
        ('Transgénero', 'Transgenero')
        ]

    for tit, opc in opciones:
        genre = '[\"' + str(opc) + '\"]'

        post = {"countries": "", "generos": genre, "years": "", "emition": "", "submit": ""}

        itemlist.append(item.clone( title = tit, post = post, action = 'list_lst', text_color = 'firebrick' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    opciones = [
        ('China', '1'),
        ('Japon', '2'),
        ('Korea', '5'),
        ('Tailandia', '6'),
        ('Taiwan', '4')
        ]

    for tit, opc in opciones:
        pais = '[\"' + str(opc) + '\"]'

        post = {"countries": pais, "generos": "", "years": "", "emition": "", "submit": ""}

        itemlist.append(item.clone( title = tit, post = post, action = 'list_lst', text_color='moccasin' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        any = '[\"' + str(x) + '\"]'

        post = {"countries": "", "generos": "", "years": any, "emition": "", "submit": ""}

        itemlist.append(item.clone( title = str(x), post = post, action = 'list_lst', text_color = 'firebrick' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, '<div class="card card-width">(.*?)</div></div>')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<div class="card">(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3 class="btn btn-default btn-subtitle">(.*?)</h3>')
        if not title: title = scrapertools.find_single_match(match, '<button class="btn btn-default btn-subtitle">(.*?)</button>')

        if not url or not title: continue

        url = host + url

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if thumb.startswith('./'): thumb = thumb.replace('./', '/')
        thumb = host[:-1] + thumb

        title_serie = re.sub(r'(\d{4})$', '', title)
        title_serie = title_serie.strip()

        if "Capitulo" in title_serie: SerieName = title_serie.split("Capitulo")[0]
        else: SerieName = title_serie.strip()

        SerieName = SerieName.strip()

        if title_serie: title = title_serie

        if item.group == 'last':
            episode = scrapertools.find_single_match(title, 'Capitulo(.*?)$').strip()

            if not episode: episode = 1

            SerieName = re.sub(r'(\d{4})$', '', SerieName)
            SerieName = SerieName.strip()

            title = title.replace('Capitulo', '[COLOR goldenrod]Capitulo[/COLOR]')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentSerieName=SerieName,
                                        contentType = 'episode', contentSeason = 1, contentEpisodeNumber=episode, infoLabels={'year': '-'} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, contentSerieName=SerieName, contentType='tvshow', infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, "<li class='active'>.*?" + "<a href='(.*?)'")

        if next_url:
            actu_page = item.url
            if 'page_no=' in item.url: 
                actu_page = scrapertools.find_single_match(item.url, "(.*?)page_no=")
                actu_page = actu_page.replace('?', '')

            next_url = actu_page + next_url

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def list_lst(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if not item.url: item.url = url_doramas

    data = do_downloadpage(url_lst, post=item.post, headers={'Referer': item.url})
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, '<div class="card card-width">(.*?)</div></div>')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<div class="card">(.*?)</div></div>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3 class="btn btn-default btn-subtitle">(.*?)</h3>')
        if not title: title = scrapertools.find_single_match(match, '<button class="btn btn-default btn-subtitle">(.*?)</button>')

        if not url or not title: continue

        url = host + url

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if thumb.startswith('./'): thumb = thumb.replace('./', '/')
        thumb = host[:-1] + thumb

        title_serie = re.sub(r'(\d{4})$', '', title)
        title_serie = title_serie.strip()

        if "Capitulo" in title_serie: SerieName = title_serie.split("Capitulo")[0]
        else: SerieName = title_serie.strip()

        SerieName = SerieName.strip()

        if title_serie: title = title_serie

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, contentType='tvshow', contentSerieName=SerieName, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, pagina = item.pagina, action='list_lst', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if config.get_setting('channels_seasons', default=True):
        title = 'Temporadas'

        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]' + title + '[/COLOR]')

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
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    if item.page == 0: episode = 0
    else: episode = (item.page * item.perpage) + 1

    matches = re.compile('<div class="card-general col-md-2 col-sm-6 col-xs-6">(.*?)</div></a>', re.DOTALL).findall(data)

    if not matches:
        if not '<div id="contentChapters"' in data:
            if not item.search_type == 'movie':
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]Temporadas[/COLOR]')

            itemlist.append(item.clone( action='findvideos', url = item.url, title = '[COLOR yellow]Servidores[/COLOR] ' + item.title,
                                        thumbnail = item.thumbnail, contentType='movie', contentTitle=item.title ))

            return itemlist

    if item.page == 0:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        episode += 1

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        _season = scrapertools.find_single_match(match, '<button class="btn btn-default btn-subtitle temporadacapitulos">(.*?)</button>')
        _season = _season.replace('Temporada', '').strip()

        _episode = scrapertools.find_single_match(match, '<button class="btn btn-default btn-sub-text">(.*?)</button>')
        _episode = _episode.replace('Cap', '').strip()

        title = str(_season) + 'x' + str(_episode) + ' ' + item.contentSerieName

        url = host[:-1] + url

        itemlist.append(item.clone( action='findvideos', url = url, title = title, orden = episode,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage, text_color='coral', orden = '10000' ))

    return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    if not '<div id="contentChapters"' in data:
        _id = scrapertools.find_single_match(item.url, 'nombre=(.*?)$')

        ref = item.url

        data = do_downloadpage(host + 'library/functions.php', post={'action': 'getMoviesDoramas'}, headers={'Referer': ref})

        matches = scrapertools.find_multiple_matches(data, '"url_movie":"(.*?)".*?"url_pelicula":"' + _id + '"')

    else:
        bloque = scrapertools.find_single_match(data, '<div id="contentChapters"(.*?)</li></ul>')

        matches = scrapertools.find_multiple_matches(bloque, '<li onclick=".*?' + "'(.*?)'")

    for url in matches:
        lang = 'Vose'
        if '-dub-' in item.url: lang = 'Lat'

        url = url.replace('\\/', '/')

        if url.startswith('//'): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        elif servidor == 'directo': other = '?'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, ref = item.url, language = lang, other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.server == 'directo':
        data = httptools.downloadpage(item.url, headers = {'Referer': item.ref}).data

        url = scrapertools.find_single_match(data, '<source src="(.*?)"')

        if not url:
            itemlist.append(item.clone(server = item.server, url = item.url + '|referer=' + item.ref))
            return itemlist
        else:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            itemlist.append(item.clone(server = servidor, url = url))
    else:
        itemlist.append(item.clone(server = item.server, url = item.url))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    post = {'action': 'searchByTerm', 'term': item.texto}

    data = do_downloadpage(item.url, post=post)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(str(data), '"id":"(.*?)".*?"label":"(.*?)".*?"icon":"(.*?)"')

    for title, url, thumb in matches:
        if not url or not title: continue

        url = host + 'dorama/' + url

        thumb = host + 'admin/uploads/doramas/' + thumb

        title_serie = re.sub(r'(\d{4})$', '', title)
        title_serie = title_serie.strip()

        if "Capitulo" in title_serie: SerieName = title_serie.split("Capitulo")[0]
        else: SerieName = title_serie.strip()

        SerieName = SerieName.strip()

        if title_serie: title = title_serie

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, contentType='tvshow', contentSerieName=SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'library/functions.php'
        item.texto = texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
