# -*- coding: utf-8 -*-

from platformcode import logger, platformtools, config
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.genteclic.com/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/page/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'category/peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'movie' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Conspiraciones', action = 'list_all', url = host + 'category/conspiraciones/' ))

    itemlist.append(item.clone( title = 'Curiosidades', action = 'list_all', url = host + 'category/curiosidades/' ))

    itemlist.append(item.clone( title = 'Documentales', action = 'list_all', url = host + 'category/documentales/' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    page_url = item.url + 'page/' + str(item.page) + '/'

    data = do_downloadpage(page_url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')

        title = scrapertools.find_single_match(article, '<h3 class="jeg_post_title">.*?<a href=".*?">(.*?)</a>')
        if not title:
            title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        lang = ''
        if 'latino' in title.lower():
            lang = 'Lat'
        elif 'español' in title.lower():
            lang = 'Esp'

        if not '-' in title:
            title = title.replace('&#8211;', '-')
        else:
            title = title.replace('&#8211;', '')

        if not '/documentales/' in item.url:
            if '-' in title:
                title = scrapertools.find_single_match(title, '(.*?)-')

        if 'pelicula' in title:
            title = scrapertools.find_single_match(title.lower(), '(.*?)pelicula')
        elif 'película' in title:
            title = scrapertools.find_single_match(title.lower(), '(.*?)película')

        title = title.replace('Pelicula', '').replace('Película', '').replace('Online', '').replace('online', '')
        title = title.replace('Latino', '').replace('latino', '').replace('Español', '').replace('español', '').replace('completa en', '')

        title = title.capitalize().strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-src="([^"]+)')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang,  
                                    contentType='movie', infoLabels = {'year': '-'}, contentTitle=title))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(itemlist) == 30:
            itemlist.append(item.clone( title='Siguientes ...', url = item.url, page = item.page + 1, action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, '<source type="video/mp4".*?src="(.*?)"')

    if not links:
        if 'data-type="youtube"' in data:
            patron = '<div class="jeg_featured_big">.*?'
            patron += 'data-src="([^"]+)"'

            links = scrapertools.find_multiple_matches(data, patron)

    if not links:
        links = scrapertools.find_multiple_matches(data, '<div class="jeg_video_container">.*?src="(.*?)"')

    ses = 0

    for url in links:
        ses += 1

        if not url.startswith('http'):
            url = 'https' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = item.languages ))

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
