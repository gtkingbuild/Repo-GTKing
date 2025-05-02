# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://doramasmp4.dev/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://doramasmp4.se/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host, group = 'last', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'doramas-en-curso-ubau/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Completados', action = 'list_all', url = host + 'series/?status=Completed', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'series/?type=Anime', search_type = 'tvshow', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    genres = [
       ['action', 'Acción'],
       ['comedy', 'Comedia'],
       ['drama', 'Drama'],
       ['family', 'Familiar'],
       ['fantasy', 'Fantasía'],
       ['historical', 'Histórico'],
       ['life', 'Vida'],
       ['music', 'Música'],
       ['mystery', 'Misterio'],
       ['romance', 'Romance'],
       ['sports', 'Deportes'],
       ['thriller', 'Thriller'],
       ['wuxia', 'Wuxia'],
       ['youth', 'Youth']
       ]

    url_gen = host + 'series/?genre[]='

    for genero in genres:
        url = url_gen + genero[0]

        itemlist.append(item.clone( title = genero[1], action = 'list_all', url = url, text_color = 'firebrick' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    web_paises = [
       ['china', 'China'],
       ['south-korea', 'Corea del sur'],
       ['thailand', 'Tailandia']
       ]

    url_pais = host + 'series/?country[]='

    for x in web_paises:
        url = url_pais + x[0]

        itemlist.append(item.clone( title = x[1], url=url, action='list_all', text_color = 'moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = data

    if '>Latest Release<' in data: pass
    elif '>Última publicación<' in data: pass
    elif '>Doramas en Curso<' in data: pass
    else:
       bloque = scrapertools.find_single_match(data, '<div class="listupd">(.*?)<div class="hpage">')

    if not bloque: bloque = scrapertools.find_single_match(data, '>Latest Release<(.*?)<div class="hpage">')
    if not bloque: bloque = scrapertools.find_single_match(data, '>Última publicación<(.*?)<div class="hpage">')

    if not bloque: bloque = scrapertools.find_single_match(data, '>Doramas en Curso<(.*?)<div class="pagination">')

    if not bloque: bloque = scrapertools.find_single_match(data, '<div class="listupd">(.*?)<div class="pagination">')

    matches = re.compile('<article(.*?)</article>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"').strip()

        if not url or not title: continue

        title = title.replace('&#8217;', "'").replace('&#8220;', '').replace('&#8221;', '').strip()

        SerieName = title

        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]
        if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
        if 'capitulo' in SerieName: SerieName = SerieName.split("capitulo")[0]
        if 'capítulo' in SerieName: SerieName = SerieName.split("capítulo")[0]

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        if 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]
        if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
        if 'season' in SerieName: SerieName = SerieName.split("season")[0]

        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        titulo = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('capitulo', '[COLOR goldenrod]Epis.[/COLOR]')

        titulo = titulo.replace('Episodio', '[COLOR goldenrod]Epis.[/COLOR]').replace('Episode', '[COLOR goldenrod]Epis.[/COLOR]').replace('episodio', '[COLOR goldenrod]Epis.[/COLOR]').replace('episodie', '[COLOR goldenrod]Epis.[/COLOR]')

        if item.group == 'last':
            season = 1

            if '-temporada-' in url: season = scrapertools.find_single_match(url, '-temporada-(.*?)/')
            if not season: season = 1

            epis = scrapertools.find_single_match(url, '-capitulo-(.*?)/')
            if not epis: epis = scrapertools.find_single_match(url, '-capitulo-(.*?)-')

            if not epis: epis = 1

            if '>Upcoming<' in match:
                titulo = '[COLOR cyan][B]Proximamente[/B][/COLOR]' + ' ' + titulo

            itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, contentType = 'episode', contentSerieName = SerieName,
                                        contentSeason = season, contentEpisodeNumber=epis, infoLabels={'year': '-'} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=titulo, thumbnail=thumb, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if item.group == 'last': return itemlist

    if itemlist:
        if '</i> Previous</a>' in data:
           next_page = scrapertools.find_single_match(data, '<div class="hpage">.*?</i> Previous</a>.*?<a href="(.*?)"')
           if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?</i> Previous</a>.*?class="page-numbers current">.*?href="(.*?)"')
        else:
           next_page = scrapertools.find_single_match(data, '<div class="hpage">.*?<a href="(.*?)"')
           if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?class="page-numbers current">.*?href="(.*?)"')

        if next_page:
            if '?page=' in next_page or '/page/' in next_page:
                if not '</i> Anterior</a>' in data:
                    if not '/page/' in next_page:
                        if '/series/' in item.url: next_page = host[:-1] + '/series/' + next_page
                        elif 'doramas-en-curso-ubau' in item.url: next_page = host[:-1] + 'doramas-en-curso-ubau' + next_page
                        else: next_page = host[:-1] + next_page

                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if not '<li data-index="' in data:
        if '>Upcoming<' in data or '>Ongoing<' in data:
            platformtools.dialog_notification(config.__addon_name, '[COLOR cyan][B]Proximamente[/B][/COLOR]')
            return

    if config.get_setting('channels_seasons', default=True):
        title = 'Sin temporadas'

        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR tan]' + title + '[/COLOR]')

    item.contentType = 'season'

    season = 1
    if '-temporada-' in item.url: season = scrapertools.find_single_match(item.url, '-temporada-(.*?)/')

    item.contentSeason = season
    itemlist = episodios(item)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    patron = '<li data-index=".*?href="(.*?)".*?<div class="epl-num">(.*?)</div>.*?<div class="epl-title">(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    if not matches:
        season = item.contentSeason
        if '-temporada-' in item.url: season = scrapertools.find_single_match(item.url, '-temporada-(.*?)/')

        epis = scrapertools.find_single_match(item.url, '-capitulo-(.*?)/')
        if not epis: epis = scrapertools.find_single_match(item.url, '-capitulo-(.*?)-')

        if not epis: epis = 1

        itemlist.append(item.clone( action='findvideos', url=item.url, title=item.title, contentType = 'episode', contentSeason = season, contentEpisodeNumber=epis ))

        return itemlist

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('DoramasMp4Dev', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramasMp4Dev', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasMp4Dev', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasMp4Dev', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts > 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                    platformtools.dialog_notification('DoramasMp4Dev', '[COLOR cyan]Cargando elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasMp4Dev', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramasMp4Dev', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, epis, title, in matches[item.page * item.perpage:]:
        epis = epis.replace('Cap ', '').strip()

        orden = epis

        if len(orden) == 1: orden = '0' + orden

        title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        titulo = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('capitulo', '[COLOR goldenrod]Epis.[/COLOR]')

        titulo = titulo.replace('Episodio', '[COLOR goldenrod]Epis.[/COLOR]').replace('Episode', '[COLOR goldenrod]Epis.[/COLOR]').replace('episodio', '[COLOR goldenrod]Epis.[/COLOR]').replace('episodie', '[COLOR goldenrod]Epis.[/COLOR]')

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, orden = orden,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page= item.page + 1, perpage = item.perpage, text_color='coral', orden = '10000' ))

    return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    ses = 0

    values = scrapertools.find_multiple_matches(data, '<option value="(.*?)"')

    for value in values:
        ses += 1

        if not value: continue

        try: url = base64.b64decode(value).decode("utf-8")
        except: url = value

        if url.startswith("//"): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vose', other = other ))

    matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    for url in matches:
        if url == 'about:blank': continue

        elif 'data:image' in url: continue

        elif '/googleads.' in url: continue

        elif url.endswith('.jpg'): continue

        ses += 1

        if url.startswith("//"): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vose', other = other ))

    if not itemlist:
        if '>Upcoming<' in data or '>Ongoing<' in data:
            platformtools.dialog_notification(config.__addon_name, '[COLOR cyan][B]Proximamente[/B][/COLOR]')
            return

        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&amp;', '&')

    if item.server == 'directo':
        if '/fkplayer.xyz' in url:
            return 'Servidor [COLOR plum]NO Soportado[/COLOR]'

        elif '.mundodrama.' in url:
            data = do_downloadpage(url)

            url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')
            if not url: url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="(.*?)"')

        else: url = ''

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone(url = url, server = servidor))

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
