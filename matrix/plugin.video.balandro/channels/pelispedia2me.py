# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.pelispedia2.me/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/lanzamiento/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>GÉNEROS<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        url = host + 'lanzamiento/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', page = 1 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)<div class="copy">')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="(.*?)"').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, '<img src="([^"]+)"')

        lngs = []
        langs = scrapertools.find_multiple_matches(article, '<img title="(.*?)"')
        if not langs: langs = scrapertools.find_multiple_matches(article, '/flags/(.*?).png')

        for lang in langs:
            lng = ''

            if lang == 'Español' or lang == 'es': lng = 'Esp'
            if lang == 'Latino' or lang == 'mx': lng = 'Lat'
            if lang == 'Subtitulado': lng = 'Vose'
            if lang == 'Ingles' or lang == 'en': lng = 'Voi'

            if lng:
               if not lng in str(lngs):
                   if lng == 'Voi': lng = 'Vo'
                   lngs.append(lng)

        year = scrapertools.find_single_match(article, '</h3>.*?<span>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>')

        year = year.strip()

        if not year: year = '-'
        else:
           if '(' + year + ')' in title: title = title.replace('(' + year + ')', '').strip()

        if ' | ' in title:
            title_alt = title.replace(' | ', ' #')
            title_alt = scrapertools.find_single_match(title_alt, '(.*?) #').strip()
        else: title_alt = title

        plot = scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>')
        if not plot: plot = scrapertools.find_single_match(article, '<div class="contenido"><p>(.*?)</p>')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = ', '.join(lngs),
                                    contentType = 'movie', contentTitle = title_alt, infoLabels = {'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_url = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "<a href='(.*?)'")
            if next_url:
               if '/page/' in next_url:
                   itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<tr id='link-'.*?<a href='(.*?)'.*?<strong class='quality'>(.*?)</strong>.*?/flags/(.*?).png")

    ses = 0

    for url, qlty, lang in matches:
        ses += 1

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue
        elif '/gounlimited.' in url: continue
        elif '/jetload.' in url: continue
        elif '/vidcloud.' in url: continue
        elif '.mystream.' in url: continue
        elif '/katfile.' in url: continue
        elif '/uploaded.' in url: continue
        elif '/ul.' in url: continue
        elif '/rapidgator.' in url: continue
        elif '/1fichier.' in url: continue

        elif 'openload' in url: continue
        elif 'powvideo' in url: continue
        elif 'streamplay' in url: continue
        elif 'rapidvideo' in url: continue
        elif 'streamango' in url: continue
        elif 'verystream' in url: continue
        elif 'vidtodo' in url: continue

        if lang == 'es': lang = 'Esp'
        elif lang == 'la': lang = 'Lat'
        elif lang == 'mx': lang = 'Lat'
        elif lang == 'en': lang = 'Vo'
        elif lang == 'jp': lang = 'Vose'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(Item(channel = item.channel, action = 'play', title = '', server = servidor, url = url, language = lang, quality = qlty ))

    itemlist = servertools.get_servers_itemlist(itemlist)

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
