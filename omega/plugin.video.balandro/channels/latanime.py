# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://latanime.org/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes?p=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_last', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'emision?p=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'generos', group = 'idiomas', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por categorías', action = 'categorias', group = 'cats', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = host + 'animes'

    data = do_downloadpage(url_cat)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'name="categoria"(.*?)>Categoria<')

    matches = re.compile('<option value="(.*?)">(.*?)</option>').findall(bloque)

    for categoria, title in matches:
        if title == "Seleccionar": continue
        elif title == "PREESTRENO": continue

        elif title == 'Castellano': continue
        elif title == 'Latino': continue
        elif title == 'Catalán': continue

        url = url_cat + '?fecha=false&genero=false&letra=false&categoria=' + categoria

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return sorted(itemlist,key=lambda x: x.title)


def generos(item):
    logger.info()
    itemlist = []

    if item.group == 'idiomas': text_color = 'moccasin'
    else: text_color = 'springgreen'

    url_genre = host + 'animes'

    data = do_downloadpage(url_genre)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'name="genero"(.*?)>Géneros<')

    matches = re.compile('<option value="(.*?)">(.*?)</option>').findall(bloque)

    for genre, title in matches:
        title = title.strip()

        if title == 'Seleccionar': continue

        if item.group == 'idiomas':
            if title == 'Castellano': pass
            elif title == 'Latino': pass
            else: continue
        else:
            if title == 'Castellano': continue
            elif title == 'Latino': continue

        url = url_genre + '?fecha=false&genero=' + genre + '&letra=false&categoria=false'

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = text_color ))

    if item.group == 'idiomas':
        url = url_genre + '?fecha=false&genero=false&letra=false&categoria=catalan'

        itemlist.append(item.clone( title = 'Catalán', action = 'list_all', url = url, text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1979, -1):
        url = host + 'animes' + '?fecha=' + str(x) + '&genero=false&letra=false&categoria=false'

        itemlist.append(item.clone( title = str(x), action = 'list_all', url = url, text_color='springgreen' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if letra == '#': letter = '09'
        else: letter = letra.lower()

        url = host + 'animes' + '?fecha=false&genero=false&letra=' + letter + '&categoria=false'

        itemlist.append(item.clone( title = letra, action = 'list_all', url = url, letra = letter, text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="row">(.*?)<nav>')
    if not bloque:
        if item.group == 'cats':
            hay_cat = scrapertools.find_single_match(item.url, '&categoria=(.*?)$')

            if hay_cat:
                bloque = scrapertools.find_single_match(data, '>Categoria<.*?<div class="row">(.*?)<nav>')
                if not bloque: bloque = scrapertools.find_single_match(data, '>Categoria<.*?<div class="row">(.*?)</footer>')
            else: bloque = scrapertools.find_single_match(data, '<div class="row">(.*?)</footer>')

        else: bloque = scrapertools.find_single_match(data, '<div class="row">(.*?)</footer>')

    matches = re.compile('<div class="col-md-4 col-lg-3 col-xl-2 col-6 my-3">(.*?)</div></a></div>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'class="my-1">(.*?)</h3')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '</svg>(.*?)</span>').strip()

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        SerieName = title

        if 'Película' in SerieName: SerieName = SerieName.split("Película")[0]

        if 'Castellano' in SerieName: SerieName = SerieName.split("Castellano")[0]
        elif 'Latino' in SerieName: SerieName = SerieName.split("Latino")[0]
        elif 'Catalán' in SerieName: SerieName = SerieName.split("Catalán")[0]

        if ' S1' in SerieName: SerieName = SerieName.split(" S1")[0]
        elif ' S2' in SerieName: SerieName = SerieName.split(" S2")[0]
        elif ' S3' in SerieName: SerieName = SerieName.split(" S3")[0]
        elif ' S4' in SerieName: SerieName = SerieName.split(" S4")[0]
        elif ' S5' in SerieName: SerieName = SerieName.split(" S5")[0]
        elif ' S6' in SerieName: SerieName = SerieName.split(" S6")[0]
        elif ' S7' in SerieName: SerieName = SerieName.split(" S7")[0]
        elif ' S8' in SerieName: SerieName = SerieName.split(" S8")[0]
        elif ' S9' in SerieName: SerieName = SerieName.split(" S9")[0]

        SerieName = SerieName.strip()

        if '-pelicula-' in url:
            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,  contentType = 'movie', contentTitle = SerieName, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<ul class="pagination">.*?<li class="page-item active".*?</li>.*?href="(.*?)"')

            if next_page:
                if '?p=' in next_page or 'p=' in next_page:
                    next_page = next_page.replace('&amp;', '&')

                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'Añadidos recientemente<(.*?)>Series Recientes<')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="col-6 col-md-6 col-lg-3 mb-3">.*?<a href="(.*?)".*?data-src="(.*?)".*?alt="(.*?)"')

    for url, thumb, title in matches:
        SerieName = title

        if 'Película' in SerieName: SerieName = SerieName.split("Película")[0]

        if 'Castellano' in SerieName: SerieName = SerieName.split("Castellano")[0]
        elif 'Latino' in SerieName: SerieName = SerieName.split("Latino")[0]
        elif 'Catalán' in SerieName: SerieName = SerieName.split("Catalán")[0]

        if ' S1' in SerieName: SerieName = SerieName.split(" S1")[0]
        elif ' S2' in SerieName: SerieName = SerieName.split(" S2")[0]
        elif ' S3' in SerieName: SerieName = SerieName.split(" S3")[0]
        elif ' S4' in SerieName: SerieName = SerieName.split(" S4")[0]
        elif ' S5' in SerieName: SerieName = SerieName.split(" S5")[0]
        elif ' S6' in SerieName: SerieName = SerieName.split(" S6")[0]
        elif ' S7' in SerieName: SerieName = SerieName.split(" S7")[0]
        elif ' S8' in SerieName: SerieName = SerieName.split(" S8")[0]
        elif ' S9' in SerieName: SerieName = SerieName.split(" S9")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Capítulos<(.*?)<script>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?</svg>(.*?)</div>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, title in matches[item.page * item.perpage:]:
        if not url or not title: continue

        epis = scrapertools.find_single_match(title, 'Capitulo(.*?)$').strip()
        if not epis: epis = 1

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

    links = scrapertools.find_multiple_matches(data, 'data-player="(.*?)"')

    if not links: return itemlist

    ses = 0

    for url in links:
        ses += 1

        url = base64.b64decode(url).decode('utf-8')

        if '/lvturbo.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'directo': other = url

        if servidor == 'various': other = servertools.corregir_other(url)

        if '-castellano-' in item.url: lang = 'Esp'
        elif '-latino-' in item.url: lang = 'Lat'
        elif '-catalan-' in item.url: lang = 'Cat'
        else: lang = 'Vose'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'buscar?p=1&q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

