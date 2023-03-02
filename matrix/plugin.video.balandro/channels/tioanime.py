# -*- coding: utf-8 -*-

from datetime import datetime

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://tioanime.com'


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    current_year = int(datetime.today().year)

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/directorio', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all',
                                url = host + '/directorio?type%5B%5D=0&year=1950%2C' + str(current_year) +'&status=1&sort=recent', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host, group = 'last_epis', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + '/directorio?type%5B%5D=2', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + '/directorio?type%5B%5D=1', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + '/directorio?type%5B%5D=3', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + '/directorio??genero%5B%5D='

    current_year = int(datetime.today().year)

    data = httptools.downloadpage(host).data

    matches = scrapertools.find_multiple_matches(data, '<a href="/directorio(.*?)".*?>(.*?)</a>')

    for genre, title in matches:
        if not '?genero=' in genre: continue

        genre = genre.replace('?genero=', '')

        url = url_genre + genre + '&year=1950%2C' + str(current_year) + '&status=2&sort=recent'

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    url_anios = host + '/directorio?year='

    current_year = int(datetime.today().year)

    for x in range(current_year, 1949, -1):
        url = url_anios + str(x) + '%2C' + str(x) + '&status=2&sort=recent'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    if item.group == 'last_epis': bloque = scrapertools.find_single_match(data, '(.*?)>Últimas Peliculas<')
    else: bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3 class="title">(.*?)</h3>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        url = host + url

        thumb = host + thumb

        SerieName = title

        if 'Season' in title: SerieName = title.split("Season")[0]
        if 'Movie' in title: SerieName = title.split("Movie")[0]

        SerieName = SerieName.strip()

        if item.group == 'last_epis':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, infoLabels={'year': '-'},
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = 1))

        else:
            itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<li class="page-item active">.*?<li class="page-item">.*?href="(.*?)"')
        if next_page:
            if itemlist:
                next_page = host + next_page

                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data

    info = eval(scrapertools.find_single_match(data, "var anime_info = (\[.*?\])"))
    epis = eval(scrapertools.find_single_match(data, "var episodes = (\[.*?\])"))

    epis = epis[::-1]

    if item.page == 0:
        sum_parts = len(epis)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('TioAnime', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioAnime', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioAnime', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioAnime', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('TioAnime', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for epi in epis[item.page * item.perpage:]:
        url =  host + '/ver/' + '%s-%s' % (info[1], epi)
        epi_num = epi

        titulo = '1x%s - Episodio %s' % (epi_num, epi_num)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, 
                                    contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epi_num ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(epis) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    videos = eval(scrapertools.find_single_match(data, "var videos = (\[.*?);"))

    ses = 0

    for datos in videos:
        ses += 1

        servidor = datos[0]
        servidor = servidor.lower()

        url = datos[1].replace("\\/", "/")

        if servidor == 'netu': continue
        elif servidor == 'streamium': continue
        elif servidor == 'amus': continue
        elif servidor == 'mepu': continue

        if servidor == 'umi':
            url = url.replace("gocdn.html#", "gocdn.php?v=")

            data = httptools.downloadpage(url).data
            url = scrapertools.find_single_match(data, '"file":"(.*?)"')
            url = url.replace("\\/", "/")

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Vose' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "/directorio?q=" + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
