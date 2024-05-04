# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://yts.mx/'


url_browser = host + "browse-movies"


def do_downloadpage(url, post=None):
    data = httptools.downloadpage(url, post=post).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = url_browser, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Tendencias', action = 'list_all', url = host + 'trending-movies', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = url_browser + '/0/all/all/0/featured/0/all', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = url_browser + '/0/all/all/0/rating/0/all', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = url_browser + '/0/all/all/0/latest/0/es', lang='Esp', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En inglés', action = 'list_all', url = url_browser + '/0/all/all/0/latest/0/en', lang='Ing', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Versión original (subtitulada)', action = 'list_all', url = url_browser + '/0/all/all/0/latest/0/foreign', lang='Vos', search_type = 'movie', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(url_browser)

    bloque = scrapertools.find_single_match(data,'<select name="language">(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque,'<option value="(.*?)">(.*?)</option>')

    for idio, tit in matches:
        if 'Todos' in tit: continue

        url = url_browser + '/0/all/all/0/latest/0/' + idio

        lang = ''
        if tit == 'Spanish': lang= 'Esp'
        elif tit == 'Extranjero': lang= 'Vos'
        elif tit == 'Inglés': lang= 'Ing'

        itemlist.append(item.clone( title = tit.capitalize(), url = url, action = 'list_all', lang=lang, text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(url_browser)

    bloque = scrapertools.find_single_match(data,'<select name="quality">(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque,'<option value="(.*?)">(.*?)</option>')

    for qltys, tit in matches:
        if qltys == 'all': continue

        url = url_browser + '/0/' + qltys + '/all/0/latest/0/all'

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    if itemlist:
        itemlist.append(item.clone( action = 'list_all', title = '480p', url = url_browser + '/0/480p/all/0/latest/0/all', text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(url_browser)

    bloque = scrapertools.find_single_match(data,'<select name="genre">(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque,'<option value="(.*?)">(.*?)</option>')

    for genre, tit in matches:
        if tit == 'Todos': continue

        url = url_browser + '/0/all/' + genre + '/0/latest/0/all'

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(url_browser)

    bloque = scrapertools.find_single_match(data,'<select name="year">(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque,'<option value="(.*?)"')

    for anyos in matches:
        if anyos == '0': continue

        url = url_browser + '/0/all/all/0/latest/' + anyos + '/all'

        itemlist.append(item.clone( title = anyos, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = data.replace('</div></div> </div>', '</div></div></div>')

    matches = re.compile('<div class="browse-movie-wrap col-xs-10 col-sm-4 col-md-5 col-lg-4">(.*?)</div></div></div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'class="browse-movie-title">(.*?)</a>')

        if not url or not title: continue

        if '</span>' in title: 
            title = scrapertools.find_single_match(title, '</span>(.*?)$').strip()

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(match, '<div class="browse-movie-year">(.*?)$')
        if not year: tear = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'class="current">.*?a href="(.*?)"')

        if next_page:
            if '?page=' in next_page:
                next_page = host[:-1] + next_page

                itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="modal-torrent">(.*?)</span></a>', re.DOTALL).findall(data)

    ses = 0

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, '<a data-torrent-id=".*?href="(.*?)"')

        url = url.replace('&amp;', '&').strip()

        if url:
            qlty = scrapertools.find_single_match(match, 'id="modal-quality-.*?<span>(.*?)</span>')

            lang = 'Vo'

            if item.lang: lang = item.lang

            peso = scrapertools.find_single_match(match, '<p>Tamaño del archivo</p><p class="quality-size">(.*?)</p>')

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = lang, quality = qlty, other = peso ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = url_browser + '/' + texto.replace(" ", "+") + '/all/all/0/latest/0/all'
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
