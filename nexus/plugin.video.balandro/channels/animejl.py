# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.anime-jl.net/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'animes?estado%5B%5D=2&order=created', search_type = 'tvshow', text_color = 'moccasin' ))
    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'animes?estado%5B%5D=0&order=created', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Finalizados', action = 'list_all', url = host + 'animes?estado%5B%5D=1&order=created', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'animes?genre[]=46&order=created', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'animes?tipo%5B%5D=3&order=created', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'animes?tipo%5B%5D=1&order=created', search_type = 'tvshow', text_color=text_color ))
    itemlist.append(item.clone( title = 'Donghuas', action = 'list_all', url = host + 'animes?tipo%5B%5D=7&order=created', search_type = 'tvshow', text_color=text_color ))
    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'animes?tipo%5B%5D=2&order=created', search_type = 'tvshow', text_color=text_color ))
    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'animes?tipo%5B%5D=3&order=created', search_type = 'movie', text_color=text_color ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'animes').data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<select name="genre(.*?)</select>')

    matches = re.compile("<option value='(.*?)'.*?>(.*?)</option>").findall(bloque)

    for value, title in matches:
        if title == 'Latino/Español': continue

        url = host + 'animes?genre%5B%5D=' + value + '&order=created'

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1989, -1):
        url = host + 'animes?year%5B%5D=' + str(x) + '&order=created'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = "<article class='Anime alt B'><a href='([^']+)'>.*?class=.*?<img src='([^']+)' alt='([^']+)'>"
    patron += "</figure><span class='Type' .*?>([^']+)</span>.*?star.*?<p>([^<]+)</p>"

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, type, plot in matches:
        thumb = host + thumb

        type = type.strip().lower()

        titulo = title
        titulo = titulo.replace('Español Latino', '').replace('Español latino', '').replace('español Latino', '').replace('español latino', '').replace('Español', '').replace('español', '').strip()

        if type == 'pelicula':
            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, 
                                        contentType = 'movie', contentTitle = titulo, infoLabels={'year': '-', 'plot': plot} ))
        else:
            SerieName = titulo

            if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
            if 'Audio' in SerieName: SerieName = SerieName.split("Audio")[0]

            if 'Español Latino' in SerieName: SerieName = SerieName.split("Español Latino")[0]
            elif 'Español' in SerieName: SerieName = SerieName.split("Español")[0]

            SerieName = SerieName.strip()

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, 
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-', 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="page-link" href="([^"]+)" rel="next">')

        if next_page:
            actual_page = scrapertools.find_single_match(item.url, '([^\?]+)?')

            itemlist.append(item.clone( title = 'Siguientes ...', url = '%s%s' % (host, next_page) if not host in next_page else next_page,
                                        action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, "<h2>Últimos episodios agregados(.*?)</ul>")

    patron = "<li><a href='(.*?)' class.*?<img src='(.*?)' alt='(.*?)'></span><span class='Capi'>(.*?)</span>"

    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, thumb, title, epis in matches:
        title = title.replace('ver ', '')

        thumb = host + thumb

        SerieName = title

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        elif 'episodio' in SerieName: SerieName = SerieName.split("episodio")[0]
        elif 'Audio' in SerieName: SerieName = SerieName.split("Audio")[0]

        if 'Español Latino' in SerieName: SerieName = SerieName.split("Español Latino")[0]
        elif 'Español' in SerieName: SerieName = SerieName.split("Español")[0]

        SerieName = SerieName.strip()

        season = scrapertools.find_single_match(title, 'Temporada (.*?) ')
        if not season: season = 1

        if not epis.lower() in title: titulo = '%s - %s' % (title, epis)
        else: titulo = title

        epis = epis.replace('Episodio', '').strip()

        titulo = titulo.replace('episodio', '[COLOR goldenrod]episodio[/COLOR]')

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb,
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber=epis))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '\[(\d+),"([^"]+)","([^"]+)",[^\]]+\]')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for epis, url, thumb in matches[item.page * item.perpage:]:
        url = "%s/%s" % (item.url, url)

        title = 'Episodio %s' % epis

        titulo = title + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

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

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    ses = 0

    matches = scrapertools.find_multiple_matches(data, 'video\[\d+\]\s*=\s*\'<iframe.*?src="([^"]+)"')

    for url in matches:
        ses += 1

        if url:
            if url.startswith('//'): url = 'https:' + url

            if url.startswith('https://animejl.top/v/'): url = url.replace('https://animejl.top/v/', 'https://vanfem.com/v/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor == 'zplayer': url = url + '|' + host

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language='Vose', other = other ))

    # ~ descargas  no se tratan por anomizador

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'animes?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

