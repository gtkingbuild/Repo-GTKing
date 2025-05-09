# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'http://zeroanime.xyz'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www4.zeroanime.xyz']

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

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'all', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/search', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + '/search?q=Latino&letra=ALL&genero=ALL&estado=2', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + '/search')

    bloque = scrapertools.find_single_match(data, '<select name="genero"(.*?)</select>')

    matches = re.compile('<option value="(.*?)">(.*?)</option>').findall(bloque)

    url_gen = host + '/search?=&letra=ALL'

    for value, title in matches:
        url = url_gen + '&genero=' + value + '&years=ALL&estado=2'

        itemlist.append(item.clone( action = "list_all", title = title, url = url, text_color='springgreen' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    url_anio = host + '/search?q=&letra=ALL&genero=ALL'

    for x in range(current_year, 1989, -1):
        url = url_anio + '&years=' + str(x) + '&estado=2'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = 'springgreen' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    url_alfa = host + '/search?q='

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        url = url_alfa + '&letra=' + letra + '&genero=ALL&years=ALL&estado=2'

        itemlist.append(item.clone( action = 'list_all', title = letra, url = url, text_color = 'springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article(.*?)</article>').findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        SerieName = corregir_SerieName(title)

        if ' 2nd ' in match: season = 2
        elif ' 3rd ' in match: season = 3
        elif ' 4th ' in match: season = 4
        elif ' 5th ' in match: season = 5
        elif ' 6th ' in match: season = 6
        elif ' 7th ' in match: season = 7
        elif ' 8th ' in match: season = 8
        elif ' 9th ' in match: season = 9
        else: season = 1

        if url.startswith("./"): url = host + url.replace('./', '/')

        if '/ver-anime-en-animeflv-' in url: continue
        elif '/anime-movil-' in url: continue

        lang = 'Vose'
        if 'q=Latino' in item.url: lang = 'Lat'

        title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, lan=lang,
                                    contentType='tvshow', contentSerieName=SerieName, contentSeason=season, infoLabels={'year':'-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination d-inline-flex">' in data:
            if not '&p=' in item.url:
                next_page = scrapertools.find_single_match(data, '<ul class="pagination d-inline-flex">.*?</a>.*?href="(.*?)"')
            else:
                next_page = scrapertools.find_single_match(data, '<ul class="pagination d-inline-flex">.*?<li class="page-item active">.*?</a>.*?ref="(.*?)"')

            if next_page:
                if '&p=' in next_page:
                    if next_page.startswith("./"): next_page = host + next_page.replace('./', '/')

                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Emisión diaria(.*?)$')

    matches = re.compile('<article(.*?)</article>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        SerieName = corregir_SerieName(title)

        if '<h2 class="h-title"' in match:
            SerieName = scrapertools.find_single_match(match, '<h2 class="h-title".*?">(.*?)</h2>')

            SerieName = corregir_SerieName(SerieName)

        if ' 2nd ' in match: season = 2
        elif ' 3rd ' in match: season = 3
        elif ' 4th ' in match: season = 4
        elif ' 5th ' in match: season = 5
        elif ' 6th ' in match: season = 6
        elif ' 7th ' in match: season = 7
        elif ' 8th ' in match: season = 8
        elif ' 9th ' in match: season = 9
        else: season = 1

        epis = scrapertools.find_single_match(match, '<span class="num-episode">Episodio(.*?)</span>').strip()
        if not epis: epis = 1

        titulo = '[COLOR goldenrod]Epis. [/COLOR]' + str(epis) + ' ' + title.replace(' ' + str(epis), '').strip()

        titulo = titulo.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentSerieName=SerieName, contentType='episode', contentSeason=season, contentEpisodeNumber=epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Episodios<(.*?)</ul></div>')

    matches = re.compile('<a href="(.*?)".*?<img src="(.*?)".*?<span class="title">Episodio(.*?)</span>', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('ZeroAnime', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('ZeroAnime', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZeroAnime', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZeroAnime', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZeroAnime', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZeroAnime', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('ZeroAnime', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, thumb, epis in matches[item.page * item.perpage:]:
        epis = epis.strip()

        if not epis: epis = 1

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epis ))

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

    lang = item.lang
    if '-latino-' in item.url: lang = 'Lat'

    matches = re.compile('<button id="embed-.*?data-url="(.*?)".*?">(.*?)</button>', re.DOTALL).findall(data)

    for url, srv in matches:
        srv = srv.strip()

        if url.startswith("../redirect.php?"): url = host + url.replace('../redirect.php?', '/redirect.php?')

        ref = url

        url = scrapertools.find_single_match(url, "url=(.*?)$")

        if url:
            if url.startswith("../video/"): url = host + url.replace('../video/', '/video/')

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, ref = ref,
                                  language = lang, other = srv )) 

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('https:///zeroanime.xyz/', 'http://zeroanime.xyz/').replace('https://zeroanime.xyz/', 'http://zeroanime.xyz/')

    resp = httptools.downloadpage(item.url, headers={'Referer': item.ref})

    url = scrapertools.find_single_match(str(resp.headers), "'refresh': '0; URL=(.*?)'")

    if url.startswith("/drop.php?"):
        url = host + url

        data = do_downloadpage(url)

        url = scrapertools.find_single_match(str(data), '"file":"(.*?)"')

        if url:
            if url.startswith("/dropden."):
               url = host + url

            if '/dropden.' in url:
                itemlist.append(item.clone(url = url, server = 'directo'))

                return itemlist

    if not 'http' in url: url = ''

    if url:
        if '/short.' in url:
            return 'Tiene [COLOR plum]Acortador[/COLOR] del enlace'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def corregir_SerieName(SerieName):
    logger.info()

    if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
    if 'season' in SerieName: SerieName = SerieName.split("season")[0]

    if ' S1 ' in SerieName: SerieName = SerieName.split(" S1 ")[0]
    elif ' S2 ' in SerieName: SerieName = SerieName.split(" S2 ")[0]
    elif ' S3 ' in SerieName: SerieName = SerieName.split(" S3 ")[0]
    elif ' S4 ' in SerieName: SerieName = SerieName.split(" S4 ")[0]
    elif ' S5 ' in SerieName: SerieName = SerieName.split(" S5 ")[0]
    elif ' S6 ' in SerieName: SerieName = SerieName.split(" S6 ")[0]
    elif ' S7 ' in SerieName: SerieName = SerieName.split(" S7 ")[0]
    elif ' S8 ' in SerieName: SerieName = SerieName.split(" S8 ")[0]
    elif ' S9 ' in SerieName: SerieName = SerieName.split(" S9 ")[0]

    if ' T1 ' in SerieName: SerieName = SerieName.split(" T1 ")[0]
    elif ' T2 ' in SerieName: SerieName = SerieName.split(" T2 ")[0]
    elif ' T3 ' in SerieName: SerieName = SerieName.split(" T3 ")[0]
    elif ' T4 ' in SerieName: SerieName = SerieName.split(" T4 ")[0]
    elif ' T5 ' in SerieName: SerieName = SerieName.split(" T5 ")[0]
    elif ' T6 ' in SerieName: SerieName = SerieName.split(" T6 ")[0]
    elif ' T7 ' in SerieName: SerieName = SerieName.split(" T7 ")[0]
    elif ' T8 ' in SerieName: SerieName = SerieName.split(" T8 ")[0]
    elif ' T9 ' in SerieName: SerieName = SerieName.split(" T9 ")[0]

    if '2nd' in SerieName: SerieName = SerieName.split("2nd")[0]
    if '3rd' in SerieName: SerieName = SerieName.split("3rd")[0]
    if '4th' in SerieName: SerieName = SerieName.split("4th")[0]
    if '5th' in SerieName: SerieName = SerieName.split("5th")[0]
    if '6th' in SerieName: SerieName = SerieName.split("6th")[0]
    if '7th' in SerieName: SerieName = SerieName.split("7th")[0]
    if '8th' in SerieName: SerieName = SerieName.split("8th")[0]
    if '9th' in SerieName: SerieName = SerieName.split("9th")[0]

    SerieName = SerieName.strip()

    return SerieName


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/search?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

