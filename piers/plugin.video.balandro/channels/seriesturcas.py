# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://fhd.seriesturcastv.to/'


perpage = 30


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/ano/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = '[B]Novelas:[/B]', folder=False, text_color='moccasin' ))

    itemlist.append(item.clone( title = ' - Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = ' - En castellano ó latino', action = 'list_all', url = host + 'series-audio/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = ' - Subtituladas', action = 'list_all', url = host + 'series-subtituladas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = '[B]Capítulos:[/B]', folder=False, text_color='moccasin' ))

    itemlist.append(item.clone( title = ' - Episodios', action = 'list_all', url = host + 'capitulos/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = ' - En castellano ó latino', action = 'list_all', url = host + 'capitulos-audio/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = ' - Subtitulados', action = 'list_all', url = host + 'capitulos-subtituladas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, '>GENERO<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?<span>(.*?)</span>')

    for url, title in matches:
        itemlist.append(item.clone( title=title, url= url, action = 'list_all', text_color='hotpink' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        url = host + 'ano/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color ='hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, 'data-tip="(.*?)</h3>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        if '/ano/' in item.url: year = scrapertools.find_single_match(item.url, "/ano/(.*?)/")

        title = title.replace('&#8230;', '').replace('&#8211;', '').replace('&#038;', '').replace('&#8217;s', "'s")

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        lang = ''
        if '-en-espanol' in thumb: lang = 'Esp'

        elif '<div class="subtyp">' in match: lang = 'Vose'
        elif '<div class="audiotyp">' in match: lang = 'Lat'

        SerieName = title

        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]

        SerieName = SerieName.strip()

        title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]')

        itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, languages = lang,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True

        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, pagina = item.pagina, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:

            if "<ul class='pagination'>" in data:
                next_page = scrapertools.find_single_match(data, "<ul class='pagination'>.*?<li class='active'>.*?</a>.*?href='(.*?)'")

                if next_page:
                    if '/page/' in next_page:
                        itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', page = 0, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if config.get_setting('channels_seasons', default=True):
        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]Temporadas[/COLOR]')

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

    if str(item.languages) == 'Esp' or str(item.languages) == 'Lat':
        if '<span class="statuse"> Subtitulado</span>' in data: item.languages = 'Vose'

    bloque = scrapertools.find_single_match(data, '<div id="episodes"(.*?)</div>')

    matches = re.compile('<a class="episod"(.*?)/a>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('SeriesTurcas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesTurcas', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesTurcas', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesTurcas', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesTurcas', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesTurcas', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesTurcas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, 'href=.*?">(.*?)<')

        if not url or not title: continue

        title = title.replace('&#8211;', "").strip()

        epis = scrapertools.find_single_match(title, "Capitulo(.*?)$").strip()
        if not epis: epis = 1

        title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]')

        SerieName = item.contentSerieName

        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]

        SerieName = SerieName.strip()

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + SerieName + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    ses = 0

    matches = scrapertools.find_multiple_matches(data, '<div id="tab.*?src="(.*?)"')

    for url in matches:
        ses += 1

        if 'player1isempty' in url: continue

        elif '/fembuki.' in url:continue
        elif '/esprinahy.' in url: continue
        elif '/argtesa.' in url: continue

        url = url.replace('/netusia.xyz/', '/waaw.to/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor,
                              language = item.languages, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if '/aporodiko.com/' in url:
        data = do_downloadpage(url)

        url = scrapertools.find_single_match(data, 'data-hash="(.*?)"')

    if url:
        if '/cdn4.turboviplay.com/data1/' in url:
            url = url.replace('/cdn4.turboviplay.com/data1/', '/cdn4.turboviplay.com/data2/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url=url, server=servidor ))

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

