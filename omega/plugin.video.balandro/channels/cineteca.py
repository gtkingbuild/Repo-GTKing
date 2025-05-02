# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.cinetecagay.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<ul id="primary-menu"(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == 'Home': continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'deepskyblue' ))

    return sorted(itemlist,key=lambda x: x.title)


def paises(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Selección Por Pais<(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?aria-label=".*?>(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'deepskyblue' ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="product-item">(.*?)</li>', re.DOTALL).findall(data)
    if not matches: matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')

        title = scrapertools.find_single_match(article, '<a class="product-title".*?">(.*?)</a>').strip()
        if not title: title = scrapertools.find_single_match(article, 'class="buzz-title">(.*?)</a>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')

        title = title.replace('CIne LGBT Gratis', '').replace('Cine Gay Online', '').replace('Cine Gay', '').replace('CIne Gay', '').replace('LGBT', '').replace('Peliculas', '').replace('Documental', '').replace('Gratis', '').replace('Latinas', '').replace('Online', '').replace('CIne', '').replace('Gay', '').strip()

        title = title.replace('&#8217;', "'").replace('&#8211;', '').replace('&#8230;', '').strip()

        if 'id="post-' in article: year = scrapertools.find_single_match(title, '(\d{4})')
        else: year = scrapertools.find_single_match(article, '(\d{4})')

        if year:
            if year in title: title = title.replace('(' + year +')', '').strip()
            if year in title: title = title.replace('[' + year +']', '').strip()
            if year in title: title = title.replace(year, '').strip()
        else: year = '-'

        if '(Castellano)' in title: lang = 'Esp'
        elif 'Audio Español' in title: lang = 'Esp'
        elif 'Audio Latino' in title: lang = 'Lat'
        elif 'Esp. Latino' in title: lang = 'Lat'
        elif '(Sub Español)' in title: lang = 'Vose'
        elif 'Subt.' in title or 'Subt' in title or 'Subs' in title or 'Sub.' in title: lang = 'Vose'
        else: lang = '?'

        if '(Castellano)' in title: title = title.split("(Castellano)")[0]
        if 'Audio Español' in title: title = title.split("Audio Español")[0]
        if 'Audio Latino' in title: title = title.split("Audio Latino")[0]
        if 'Esp. Latino' in title: title = title.split("Esp. Latino")[0]
        if '(Sub Español)' in title: title = title.split("(Sub Español)")[0]
        if 'Subt.' in title: title = title.split("Subt.")[0]
        if 'Subt' in title: title = title.split("Subt")[0]
        if 'Subs' in title: title = title.split("Subs")[0]
        if 'Sub.' in title: title = title.split("Sub.")[0]
        if 'Audio' in title: title = title.split("Audio")[0]

        title = title.strip()

        PeliName = title

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang, contentType='movie', contentTitle=PeliName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<ul class='page-numbers'>" in data:
            next_page = scrapertools.find_single_match(data, "<ul class='page-numbers'>.*?" 'class="page-numbers current">.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    ses = 0

    matches = re.compile('<iframe.*?src="(.*?)".*?</iframe>', re.DOTALL).findall(data)

    for url in matches:
        ses += 1

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = '', url=url, language=item.languages ))

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
