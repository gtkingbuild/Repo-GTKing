# -*- coding: utf-8 -*-

import re

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://hacktorrent.to/'


per_page = '20'

rut_movies = host + 'wp-json/wpreact/v1/movies?posts_per_page=' + per_page
rut_series = host + 'wp-json/wpreact/v1/series?posts_per_page=' + per_page
rut_animes = host + 'wp-json/wpreact/v1/animes?posts_per_page=' + per_page


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://hacktorrent.men/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))
    itemlist.append(item.clone( title = 'Animes', action = 'mainlist_series', text_color = 'springgreen' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = rut_movies + '&page=1', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = rut_series + '&page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = rut_animes + '&page=1', search_type = 'tvshow', text_color='springgreen' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    text_color = 'deepskyblue'

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = rut_movies + '&language=castellano&page=1', text_color = text_color ))

    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = rut_movies + '&language=latino&page=1', text_color = text_color ))

    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = rut_movies + '&language=subtitulado&page=1', text_color = text_color ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    generos = [
       'acción',
       'animación',
       'aventura',
       'bélica',
       'ciencia ficción',
       'comedia',
       'crimen',
       'documental',
       'drama',
       'familia',
       'fantasía',
       'historia',
       'misterio',
       'música',
       'romance',
       'suspense',
       'terror',
       'western'
       ]

    for genero in generos:
        url = host + '/wp-json/wpreact/v1/category?category=' + genero + '&posts_per_page=' + per_page + '&page=1'

        itemlist.append(item.clone( action = 'list_all', title = genero.capitalize(), url = url, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(str(data), '{"id":(.*?)}.*?,')

    num_matches = len(matches)

    for match in matches:
        url = scrapertools.find_single_match(match, '"slug":"(.*?)"')

        title = scrapertools.find_single_match(match, '"title":"(.*?)"')

        if not url or not title: continue

        title = title.replace('&#8217;', "'")

        thumb = scrapertools.find_single_match(match, '"featured":"(.*?)"')

        thumb = thumb.replace('\\/', '/')

        year = scrapertools.find_single_match(match, '"years":"(.*?)-')
        if not year: year = '-'

        title = clean_title(title)

        tipo = 'movie' if '"type":"pelicula"' in match else 'tvshow'

        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            if '/series?' in item.url:
                ref = host + 'serie/' + url + '/'

                url = host + 'wp-json/wpreact/v1/serie/' + url + '/related/'
            else:
                ref = host + 'anime/' + url + '/'

                url = host + 'wp-json/wpreact/v1/anime/' + url + '/related/'

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            ref = host + 'pelicula/' + url + '/'

            url = host + 'wp-json/wpreact/v1/movie/' + url

            itemlist.append(item.clone( action='findvideos', url=url, ref=ref, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if str(num_matches) == per_page:
            if '"pages":' in data:
                ant_pag = scrapertools.find_single_match(item.url, '&page=(.*?)$')

                if ant_pag:
                    ant_url = scrapertools.find_single_match(item.url, '(.*?)&page=')

                    next_page = int(ant_pag)
                    next_page = next_page + 1

                    next_url = ant_url + '&page=' + str(next_page)

                    itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    seasons = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('"season":(.*?),', re.DOTALL).findall(str(data))

    tot_temps = 0

    for tempo in temporadas:
        tempo = tempo.strip()

        if tempo in seasons:
            continue

        if not tempo in seasons:
            seasons.append(tempo)
            tot_temps += 1

        title = 'Temporada ' + tempo

        if tot_temps == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('"season":' + str(item.contentSeason) + ',"episode":(.*?),"quality":"(.*?)",.*?"size":"(.*?)",.*?"download_link":"(.*?)",.*?"language":"(.*?)"', re.DOTALL).findall(str(data))

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('HackTorrent', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('HackTorrent', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HackTorrent', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HackTorrent', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HackTorrent', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HackTorrent', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('HackTorrent', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for epis, qlty, size, link, lang in matches[item.page * item.perpage:]:
        lang = clean_title(lang)

        lang = lang.replace('\\/', '/')

        if 'Latino/Ingles' in lang: lang = 'Lat'
        elif 'Castellano/Ingles' in lang: lang = 'Esp'
        elif 'Latino/Japones' in lang: lang = 'Vos'

        elif 'Castellano' in lang: lang = 'Esp'
        elif 'Latino' in lang: lang = 'Lat'
        elif 'Subtitulado' in lang: lang = 'Vose'
        elif 'Version Original' in lang: lang = 'VO'

        link = link.replace('\\/', '/')

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'")

        itemlist.append(item.clone( action='findvideos', url=link, title=titulo, language=lang, quality=qlty, size=size,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.contentType == 'episode':
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = item.url, server = 'torrent',
                              language = item.language, quality = item.quality, other = item.size ))

        return itemlist

    headers = {'Referer': item.ref}

    data = do_downloadpage(item.url, headers=headers)

    links = scrapertools.find_multiple_matches(str(data), '"quality":"(.*?)".*?"size":"(.*?)".*?"download_link":"(.*?)".*?"language":"(.*?)"')

    for qlty, size, link, lang in links:
        lang = clean_title(lang)

        lang = lang.replace('\\/', '/')

        if 'Latino/Ingles' in lang: lang = 'Lat'
        elif 'Castellano/Ingles' in lang: lang = 'Esp'
        elif 'Latino/Japones' in lang: lang = 'Vos'

        elif 'Castellano' in lang: lang = 'Esp'
        elif 'Latino' in lang: lang = 'Lat'
        elif 'Subtitulado' in lang: lang = 'Vose'
        elif 'Version Original' in lang: lang = 'VO'

        link = link.replace('\\/', '/')

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = link, server = 'torrent',
                              language = lang, quality = qlty, other = size ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    host_torrent = host[:-1]
    url_base64 = decrypters.decode_url_base64(url, host_torrent)

    if url_base64.startswith('magnet:'):
        itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    elif url_base64.endswith(".torrent"):
        itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    return itemlist


def clean_title(title):
    logger.info()

    title = title.replace('\\u00e1', 'a').replace('\\u00c1', 'a').replace('\\u00e9', 'e').replace('\\u00ed', 'i').replace('\\u00f3', 'o').replace('\\u00fa', 'u')
    title = title.replace('\\u00f1', 'ñ').replace('\\u00bf', '¿').replace('\\u00a1', '¡').replace('\\u00ba', 'º')
    title = title.replace('\\u00eda', 'a').replace('\\u00f3n', 'o').replace('\\u00fal', 'u').replace('\\u00e0', 'a')

    title = title.replace('\\u2019', "'")

    return title


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'wp-json/wpreact/v1/search?query=' + texto.replace(" ", "+") + '&posts_per_page=' + per_page + '&page=1'
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
