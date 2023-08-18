# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://areliux.com/'


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'anime/', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Dibujos animados', action = 'list_all', url = host + 'dibujo/', search_type = 'tvshow', text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<section class="layout home-s">(.*?)<div class="navigation ignore-select">')
    if not bloque: bloque = scrapertools.find_single_match(data, '<section class="layout home-s">(.*?)<!-- sidebar -->')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if '-capitulo-' in url or '/main/' in url:
            season = scrapertools.find_single_match(url, '-temporada-(.*?)-')
            if not season: season = '1'

            epis =  scrapertools.find_single_match(url, '-capitulo-(.*?).')
            if not epis: epis = '1'

            SerieName = title

            if "Capitulo" in title: SerieName = title.split("Capitulo")[0]
            if "Temporada" in title: SerieName = title.split("Temporada")[0]

            SerieName = SerieName.strip()

            if '/main/' in url:
                itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))
            else:
                itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb, contentSerieName=SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        else:
            SerieName = title

            if "Temporada" in title: SerieName = title.split("Temporada")[0]

            SerieName = SerieName.strip()

            serie = scrapertools.find_single_match(url, host + '(.*?)/')
            url = host + serie + '/'

            title = title.replace('Temporada', '[COLOR hotpink]Temporada[/COLOR]')

            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, contentType='tvshow', contentSerieName=SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="navigation ignore-select">' in data:
            if '/page/' in item.url:
                nro_page = scrapertools.find_single_match(item.url, '/page/(.*?)/')
                next_page = scrapertools.find_single_match(data, '<div class="navigation ignore-select">.*?<span>' + nro_page + '</span>.*?<a href="(.*?)"')
            else:
                next_page = scrapertools.find_single_match(data, '<div class="navigation ignore-select">.*?</span>.*?<a href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if not '[COLOR hotpink]Temporada[/COLOR]' in item.title:
        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin Temporadas')

    item.page = 0
    item.dialog = False
    item.contentType = 'season'
    item.contentSeason = 1
    itemlist = episodios(item)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<div class="col-lg-8 col-md-12">(.*?)<div class="navigation ignore-select">')
    if not bloque: bloque = scrapertools.find_single_match(data, '<div class="col-lg-8 col-md-12">(.*?)<!-- sidebar -->')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        if not '-capitulo-' in url: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        season = scrapertools.find_single_match(url, '-temporada-(.*?)-')
        if not season: season = '1'

        epis =  scrapertools.find_single_match(url, '-capitulo-(.*?).')
        if not epis: epis = '1'

        SerieName = title

        if "Capitulo" in title: SerieName = title.split("Capitulo")[0]
        if "Temporada" in title: SerieName = title.split("Temporada")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb,
                                    contentSerieName=SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="navigation ignore-select">' in data:
            if '/page/' in item.url:
                nro_page = scrapertools.find_single_match(item.url, '/page/(.*?)/')
                next_page = scrapertools.find_single_match(data, '<div class="navigation ignore-select">.*?<span>' + nro_page + '</span>.*?<a href="(.*?)"')
            else:
                next_page = scrapertools.find_single_match(data, '<div class="navigation ignore-select">.*?</span>.*?<a href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='episodios', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<iframe.*?src="(.*?)"', re.DOTALL).findall(data)

    for url in matches:
        if not url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, language = 'Lat', title = '', url = url )) 

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'index.php?do=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
