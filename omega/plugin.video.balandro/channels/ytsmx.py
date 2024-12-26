# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://en.yts-official.mx/'


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

    itemlist.append(item.clone( title = 'Tendencias', action = 'list_all', url = url_browser + '?order_by=featured', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = url_browser + '?order_by=likes', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = url_browser + '?order_by=rating', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(url_browser)

    bloque = scrapertools.find_single_match(data,'<select name="quality">(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque,'<option value="(.*?)">(.*?)</option>')

    for qltys, tit in matches:
        if tit == 'All': continue

        url = url_browser + '?quality=' + qltys

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = 'moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(url_browser)

    bloque = scrapertools.find_single_match(data,'<select name="genre">(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque,'<option value="(.*?)">(.*?)</option>')

    for genre, tit in matches:
        if tit == 'All': continue

        url = url_browser + '?genre=' + genre

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(url_browser)

    bloque = scrapertools.find_single_match(data,'<select name="year">(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque,'<option value="(.*?)"')

    for anyos in matches:
        if anyos == '0': continue

        url = url_browser + '?year=' + anyos

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

        url = host[:-1] + url

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'class="current">.*?href="(.*?)"')

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

        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        url = url.replace('&amp;', '&').strip()

        if url:
            if url.startswith("/"): url = host[:-1] + url

            qlty = scrapertools.find_single_match(match, 'id="modal-quality-.*?<span>(.*?)</span>')

            lang = 'Vo'

            if item.lang: lang = item.lang

            peso = scrapertools.find_single_match(match, '<p>File size</p>.*?<p class="quality-size">(.*?)</p>')

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent',
                                  language = lang, quality = qlty, other = peso ))

            if '<a href="magnet:' in match:
                url = scrapertools.find_single_match(match, '<a href="(.*?)"')

                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent',
                                language = lang, quality = qlty, other = peso, age = 'Magnet' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = url_browser + '?keyword=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
