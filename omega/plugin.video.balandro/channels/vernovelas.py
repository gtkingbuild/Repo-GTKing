# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.1ennovelas.top/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/release/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'novela/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + 'ver-novela/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Series con temporadas', action = 'list_all', url = host + 'temporada/', group = 'temp', search_type = 'tvshow', text_color = 'yellowgreen' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'tendencias/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('accion', 'Acción'),
       ('action-adventure', 'Acción & Aventura'),
       ('ciencia-ficcion', 'Ciencia Ficción'),
       ('comedia', 'Comedia'),
       ('comedy', 'Comedy'),
       ('crimen', 'Crimen'),
       ('documental', 'Documental'),
       ('drama', 'Drama'),
       ('familia', 'Familia'),
       ('fantasia', 'Fantasía'),
       ('historia', 'Historia'),
       ('misterio', 'Misterio'),
       ('musica', 'Música'),
       ('narcotrafico', 'Narcotráfico'),
       ('novelas', 'Novelas'),
       ('reality', 'Reality'),
       ('romance', 'Romance'),
       ('soap', 'Soap'),
       ('venganza', 'Venganza'),
       ('western', 'Western')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'genero/' + opc + '/', action = 'list_all', text_color='hotpink' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        url = host + 'release/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color ='hotpink' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    productoras = [
        ('amazon', 'Amazon'),
        ('antena-3', 'Antena 3'),
        ('apple-tv', 'Apple TV'),
        ('atresplayer-premium', 'Atresplayer Premium'),
        ('canal', 'Canal+'),
        ('cbc-television', 'CBC Television'),
        ('cbs', 'Cbs'),
        ('caracol-tv', 'Caracol TV'),
        ('disney', 'Disney+'),
        ('elisa-viihde-viaplay', 'Elisa Viihde Viaplay'),
        ('fox', 'FOX'),
        ('globoplay', 'Globoplay'),
        ('hbo', 'HBO'),
        ('hulu', 'Hulu'),
        ('itv', 'ITV'),
        ('jtbc', 'Jtbc'),
        ('kanal-d', 'Kanal D'),
        ('las-estrellas', 'Las Estrellas'),
        ('nbc', 'NBC'),
        ('netflix', 'Netflix'),
        ('novelastv', 'Novelas TV'),
        ('peacock', 'Peacock'),
        ('rcn', 'Rcn'),
        ('rede-globo', 'Rede Globo'),
        ('rtbf-be', 'Rtbf BE'),
        ('showtime', 'Showtime'),
        ('star-tv', 'Star Tv'),
        ('starz', 'Starz'),
        ('telemundo', 'Telemundo'),
        ('tf1', 'TF1'),
        ('the-roku-channel', 'The Roku Channel'),
        ('the-wb', 'The WB'),
        ('tv-globo', 'TV Globo'),
        ('tv8', 'TV8'),
        ('upn', 'UPN')
        ]

    for opc, tit in productoras:
        url = host + 'network/' + opc + '/'

        itemlist.append(item.clone( title = tit, action = 'list_all', url = url, text_color = 'moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, '<h1>(.*?)>ÚLTIMOS EMITIDOS<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<span class="c">(.*?)</span>')

        if not url or not title: continue

        year = scrapertools.find_single_match(match, '<span class="wdate">(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '<div class="metadata">.*?<span>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '<span class="imdb">.*?<span>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '</h3>.*?<span>.*?<span>(.*?)</span>')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year ='-'

        if '/release/' in item.url: year = scrapertools.find_single_match(item.url, "/release/(.*?)/")

        title = title.replace('&#8230;', '').replace('&#8211;', '').replace('&#038;', '').replace('&#8217;s', "'s")

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        SerieName = title

        if " |" in SerieName: SerieName = SerieName.split(" |")[0]

        SerieName = SerieName.strip()

        titulo = title

        if item.group == 'temp':
            tempo = scrapertools.find_single_match(match, '<span class="b">(.*?)</span>')

            titulo = titulo + ' ' + '[COLOR goldenrod]Temporada [/COLOR]' + str(tempo)

        itemlist.append(item.clone( action='temporadas', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<span class="current">.*?href="(.*?)"')

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, '<h1>(.*?)>ÚLTIMOS EMITIDOS<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not url or not title: continue

        year = scrapertools.find_single_match(match, '<span class="wdate">(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '<div class="metadata">.*?<span>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '<span class="imdb">.*?<span>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '</h3>.*?<span>.*?<span>(.*?)</span>')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year ='-'

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        SerieName = scrapertools.find_single_match(match, '<span class="c">(.*?)</span>')

        if not SerieName:
            SerieName = title

            if " |" in SerieName: SerieName = SerieName.split(" |")[0]

            SerieName = SerieName.strip()

        season = scrapertools.find_single_match(match, '<span class="serie">(.*?)x').strip()
        season = season.replace(SerieName, '').replace('(', '').strip()

        if not season: season = 1

        epis = scrapertools.find_single_match(match, '<span class="serie">.*?x(.*?)</span>').strip()
        epis =  epis.replace(')', '').strip()

        if not epis: epis = 1

        titulo = str(season) + 'x' + str(epis) + ' ' + SerieName

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, infoLabels={'year': year},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<span class="current">.*?href="(.*?)"')

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'last_epis', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    id = scrapertools.find_single_match(str(data), 'var id=(.*?);').strip()

    if not id: return itemlist

    url = item.url

    post = {'action': 'seasons', 'id': id}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

    matches = re.compile("<span class='title'>Temporada (.*?)<i>", re.DOTALL).findall(data)

    for numtempo in matches:
        numtempo = numtempo.strip()

        if not numtempo: numtempo = '1'

        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            item.url = url
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, page = 0, contentType = 'season', contentSeason = numtempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    id = scrapertools.find_single_match(str(data), 'var id=(.*?);').strip()

    if not id: return itemlist

    post = {'action': 'seasons', 'id': id}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

    bloque = scrapertools.find_single_match(data, "<span class='title'>Temporada " + str(item.contentSeason) + "(.*?)</ul>")

    matches = re.compile("data-id='(.*?)</div></li>", re.DOTALL).findall(data)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('VerNovelas', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('VerNovelas', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('VerNovelas', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('VerNovelas', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('VerNovelas', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('VerNovelas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
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
        if num_matches > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    postid = scrapertools.find_single_match(str(data), 'postid-(.*?)"').strip()

    if not postid: return itemlist

    lang = 'Lat'
    if '>Español<' in data: lang = 'Esp'

    ses = 0

    # ~ Embeds
    matches = scrapertools.find_multiple_matches(data, "<li id='player-option-.*?data-nume='(.*?)'")

    for match in matches:
        ses += 1

        post = {'action': 'doo_player_ajax', 'post': postid, 'nume': match, 'type': 'tv'}

        headers = {'Referer': item.url}

        data1 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)

        url = scrapertools.find_single_match(data1, "<iframe.*?src='(.*?)'")
        if not url: url = scrapertools.find_single_match(datal, '<IFRAME.*?SRC="(.*?)"')

        if url:
            if url.startswith('//'): url = 'https:' + url

            url = url.replace('&amp;', '&')

            if '/streamplay.' in url or '/streampiay.' in url: continue
            elif '/watchsb.' in url or '/embedsb.' in url: continue
            elif '/powvideo.' in url: continue
            elif '/segavid.' in url: continue

            qlty = scrapertools.find_single_match(data1, "<strong class='quality'>(.*?)</strong>")

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            other = ''

            if servidor == 'various': other = servertools.corregir_other(url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, quality = qlty, other = other ))

    # ~ Watch online
    bloque = scrapertools.find_single_match(data, ">Watch online<(.*?)</table>")

    matches = scrapertools.find_multiple_matches(bloque, "<tr id='link-' data='.*?<a href='(.*?)'")

    for url in matches:
        ses += 1

        if '/streamplay.' in url or '/streampiay.' in url: continue
        elif '/watchsb.' in url or '/embedsb.' in url: continue
        elif '/powvideo.' in url: continue
        elif '/segavid.' in url: continue

        elif '/esfacil.' in url: continue

        qlty = scrapertools.find_single_match(data, "<strong class='quality'>(.*?)</strong>")

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, quality = qlty, other = other ))

    # ~ Downloads
    bloque = scrapertools.find_single_match(data, ">Download<(.*?)</table>")

    matches = scrapertools.find_multiple_matches(bloque, "<tr id='link-' data='.*?<a href='(.*?)'")

    for url in matches:
        ses += 1

        if '/ul.' in url: continue
        elif '/katfile.' in url: continue
        elif '/rapidgator.' in url: continue
        elif '/nitroflare.' in url: continue

        qlty = scrapertools.find_single_match(data, "<strong class='quality'>(.*?)</strong>")

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = 'D'

        if servidor == 'various': other = servertools.corregir_other(url)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, quality = qlty, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

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

