# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


from lib import decrypters


host = 'https://www2.newpct.net/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www.newpct.net/', 'https://www1.newpct.net/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not headers: headers = {'Referer': host}

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos-4/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='En 720', url=host + 'calidad/720p/', action='list_all' ))
    itemlist.append(item.clone( title='En 1080', url=host + 'calidad/1080p/', action='list_all' ))
    itemlist.append(item.clone( title='En HD Rip', url=host + 'calidad/hdrip/', action='list_all' ))
    itemlist.append(item.clone( title='En Micro HD', url=host + 'peliculas-microhd-2/', action='list_all' ))


    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/castellano/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/latino/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/subtituladas/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<div class="row menu-container menu-content-generos"(.*?)</div></div>')

    matches = re.compile('<a href="(.*?)".*?">(.*?)</a>').findall(bloque)

    for url, title in matches:
        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h3>(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, '<a class="tplve"(.*?)</div></li>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, ' title="(.*?)"')

        if not url or not title: continue

        title = title.replace('torrent', '').strip()

        title = title.replace('(Español)', '').replace('(Latino)', '').replace('(Subtitulado)', '').strip()

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        lang = scrapertools.find_single_match(match, '</div>.*?</b>.*?<b>(.*?)</b>')
        if lang.lower() == 'castellano': lang = 'Esp'
        elif lang.lower() == 'latino': lang = 'Lat'
        elif lang.lower() == 'subtitulado': lang = 'Vose'

        qlty = scrapertools.find_single_match(match, '</div>.*?<b>(.*?)</b>')

        if '<b>4k</b>' in match: qlty = '4K'
        else: qlty = qlty.replace('GBs', ' GB').replace('MBs', ' MB')

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            title = title.replace('&#8211;', '').replace('&#215;', ' ')

            titulo = title

            if "temporada" in titulo: titulo = titulo.split("temporada")[0]
            if "Temporada" in titulo: titulo = titulo.split("Temporada")[0]
            if "episodios" in titulo: titulo = titulo.split("episodios")[0]
            if "Episodios" in titulo: titulo = titulo.split("Episodios")[0]
            if " - " in titulo: titulo = titulo.split(" - ")[0]

            titulo = titulo.replace('&#8211;', '').replace('&#215;', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'episode', contentSerieName = titulo, contentSeason = 1, contentEpisodeNumber = 1,
                                        infoLabels={'year': '-'} ))

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            titulo = title

            if "(Inglés)" in titulo: titulo = titulo.split("(Inglés)")[0]
            if "(Castellano)" in title: titulo = titulo.split("(Castellano)")[0]

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = titulo, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span class="pagina pag_actual">.*?' + "href='(.*?)'")

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<div class="videoWrapperInner">.*?<a href="(.*?)".*?<a href="(.*?)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    ses = 0

    for url1, url2 in matches:
        ses += 1

        if url1:
            if url1.startswith('/'): url1 = host[:-1] + url1

            url1 = url1.replace('&amp;', '&')

            if not url1.startswith('https://ouo.io/'):
               other = ''
               if url1.startswith('magnet:?'): other = 'Magnet'

               itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url1, server = 'torrent',
                                     language = item.languages, quality = item.qualities, other = other ))

        if url2:
            if url2.startswith('/'): url2 = host[:-1] + url2

            url2 = url2.replace('&amp;', '&')

            if not url2.startswith('https://ouo.io/'):
                other = ''
                if url2.startswith('magnet:?'): other = 'Magnet'

                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url2, server = 'torrent',
                                      language = item.languages, quality = item.qualities, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith('/'): item.url = host[:-1] + item.url

    url = item.url

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith(".torrent"):
        data = do_downloadpage(url)

        if not data:
            return 'Archivo [COLOR red]Corrupto[/COLOR]'

        if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
            return 'Archivo [COLOR red]Inexistente[/COLOR]'

        itemlist.append(item.clone( url = url, server = 'torrent' ))

    else:
        if '/ouo.io/' in url:
            url = decrypters.decode_uiiio(url)

            if not url:
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(url, host_torrent)

        if url_base64.startswith('magnet:'):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

        elif url_base64.endswith(".torrent"):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.search_type == 'tvshow':
            item.url = host + '/series/?s=' + texto.replace(" ", "+")
        else:
            item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
