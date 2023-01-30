# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


# ~ las Series todos los links NO so validos

host = 'https://www.vivatorrents.org/'


perpage = 28


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + '?orderby=relevance', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Al azar', action = 'list_all', url = host + '?orderby=rand', search_type = 'movie'))

    itemlist.append(item.clone( title = 'Por alfabético (Z - A)', action = 'list_all', url = host + '?orderby=title', search_type = 'movie'))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<option value="">G&eacute;neros</option>(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque, '<option value="(.*?)" >(.*?)</option>')

    for genre, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = host + genre + '/' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="moviesbox">(.*?)</a></div>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<span class="tooltipbox">(.*?)<i>').strip()
        if not title: title = scrapertools.find_single_match(match, '<span class="tooltipbox">(.*?)</span>').strip()

        if not url or not title: continue

        if len(title) > 99: title = url.replace(host, '').replace('/', '').strip()

        thumb = scrapertools.find_single_match(match, 'style="background-image:url(.*?)"')
        thumb = thumb.replace('(', '').replace(')', '').strip()

        year = scrapertools.find_single_match(match, '<i>(.*?)</i>')
        if not year: year = '-'

        qlty = ''
        if '(720p)' in title:
            qlty = '720p'
            title = title.replace('(720p)', '').strip()
        elif '(1080p)' in title:
            qlty = '1080p'
            title = title.replace('(1080p)', '').strip()
        elif '(DVDrip)' in title:
            qlty = 'DVDrip'
            title = title.replace('(DVDrip)', '').strip()
        elif '(BRS)' in title:
            qlty = 'BRS'
            title = title.replace('(BRS)', '').strip()
        elif '(HDR)' in title:
            qlty = 'HDR'
            title = title.replace('(HDR)', '').strip()
        elif '(TS)' in title:
            qlty = 'TS'
            title = title.replace('(TS)', '').strip()
        elif '3D' in title:
            qlty = '3D'
            title = title.replace('3D', '').strip()

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            titulo = title.replace('&#8211;', 'T:').replace('&#215;', 'E:')
            temp = scrapertools.find_single_match(titulo, "T:(.*?)E:").strip()
            epis = scrapertools.find_single_match(titulo, "E:(.*?)$").strip()

            if not temp or not epis: continue

            SerieName = scrapertools.find_single_match(titulo, "(.*?)T:").strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = temp, contentEpisodeNumber = epis,
                                        infoLabels={'year': year} ))

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break


    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, "<span class='pagination_act'>.*?</span>.*?href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', page = 0, action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, '<div class="detail_torrents">.*?<a href=.*?http:(.*?)".*?<i>(.*?)</i>')
    if not links: links = scrapertools.find_multiple_matches(data, '<div class="detail_torrents">.*?<a href=.*?https:(.*?)".*?<i>(.*?)</i>')

    ses = 0

    for url, qlty in links:
        ses += 1

        url = url.replace('//www.divxtotal2.com/http:', '').strip()

        url = 'https:' + url

        url = url.replace("');", '').strip()

        if not url: continue

        if url.startswith('magnet:'): pass
        elif url.endswith(".torrent"): pass
        else: continue

        if '.php?' in url: continue
        elif '/www.mejortorrent.org/' in url: continue

        qlty = qlty.strip()

        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='torrent', language='Esp', quality=qlty ))

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
