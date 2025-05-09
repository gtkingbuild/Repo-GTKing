# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.documentales-online.com'


perpage = 25


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_top', url = host + '/populares/', grupo = 'Populares' ))
    itemlist.append(item.clone( title = 'Top 100', action = 'list_top', url = host +'/top/', grupo = 'Top 100' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Por tema', action = 'series', url = host + '/series-temas/' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<ul class="sub-menu">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, ' href="([^"]+)">([^<]+)')

    for url, title in matches:
        if url.startswith('/'): url = host + url

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color='cyan' ))

    return itemlist


def series(item):
    logger.info()
    itemlist = []

    perpage = 100

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, 'Populares</a>.*?Series / Temas(.*?)</article>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?>(.*?)</a>')

    num_matches = len(matches)

    for url, title in matches[item.page * perpage:]:
        url = host + url
        title = title.split("<")[0].capitalize()

        itemlist.append(item.clone( action='list_series', url=url, title=title, infoLabels = {'year': '-'}, text_color='moccasin' ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage

            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='series', text_color='coral' ))

    return itemlist


def list_series(item):
    logger.info()
    itemlist = []

    datas = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(datas, 'Populares</a>(.*?)>Destacados<')

    matches = scrapertools.find_multiple_matches(data, 'href="([^"]+).*?src="([^"]+).*?bookmark">([^<]+)')

    for url, thumb, title in matches:
        title = title.replace("&#8211;","-").strip()

        if not title: continue

        if url == '#': continue

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, infoLabels = {'year': '-'},
                                    contentType='movie', contentTitle=title, contentExtra='documentary' ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(datas, '<link rel="next" href="(.*?)"')

        if next_url:
            if'/page/' in next_url:
               itemlist.append(item.clone( title='Siguientes ...', url=next_url,  action='list_series', text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, '<a href="([^"]+)"')

        title = scrapertools.find_single_match(article, 'rel="bookmark">(.*?)</a>')

        if not url or not title: continue

        if '/series-temas/' in url: continue

        title = title.replace('&#8230;', '').replace('&#8211;', '')

        thumb = scrapertools.find_single_match(article, 'itemprop="image".*?data-src="(.*?)"')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, plot=plot, infoLabels = {'year': '-'},
                                    contentType='movie', contentTitle=title, contentExtra='documentary' ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page_link = scrapertools.find_single_match(data, '<span aria-current="page" class="page-numbers current">.*?href="(.*?)"')

        if next_page_link:
            itemlist.append(item.clone( title='Siguientes ...', action='list_all', url = next_page_link, text_color='coral' ))

    return itemlist


def list_top(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, 'Populares</a>.*?%s(.*?)>Última revisión' % item.grupo)

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?>(.*?)</a>')

    num_matches = len(matches)

    for url, title in matches[item.page * perpage:]:
        title = title.split("<")[0]

        title = title.replace('&#8230;', '').replace('&#8211;', '')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, infoLabels = {'year': '-'}, contentType='movie', contentTitle=title, contentExtra='documentary' ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage

            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_top', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    ses = 0

    i = 0

    num_matches = len(matches)

    for url in matches:
        ses += 1

        if 'amazon-adsystem.com' in url:
            if num_matches == 1:
                url = scrapertools.find_single_match(data, '<param name="src" value="(.*?)"')
                if not url: continue
            else:
                num_matches = num_matches - 1
                continue

        url = url.replace('&amp;', '&')

        other = ''
        if num_matches > 1:
            i += 1
            other = str(i)

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if not 'http' in url: url = 'https:' + url

        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = '', url = url, language = 'Esp', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
