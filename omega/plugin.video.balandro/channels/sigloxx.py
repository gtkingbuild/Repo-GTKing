# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://2000peliculassigloxx.com/'


perpage = 25


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar película ...[COLOR plum](excepto en YouTube)[/COLOR]', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'YouTube', action = 'youtubes', thumbnail=config.get_thumb('youtube'), search_type = 'movie', text_color = 'moccasin' ))

    itemlist.append(item.clone ( title = 'Sagas', action = 'sagas', url = host + 'sagas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por actor', action = 'listas', url = host + 'actores/', group = 'Actores' ))
    itemlist.append(item.clone ( title = 'Por actriz', action = 'listas', url = host + 'actrices/', group = 'Actrices' ))
    itemlist.append(item.clone ( title = 'Por dirección, guionistas, productores', action = 'listas', url = host + 'directores/', group = 'Directores' ))
    itemlist.append(item.clone ( title = 'Por compositores, escritores, novelistas', action = 'listas', url = host + 'otras-biografias/', group = 'Otras biografías' ))

    return itemlist


def youtubes(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Cine Clásico', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=r9y9RcsBv9k&list=PL5Elc2OLiWk6pkscyMTC6DCbE4GIeqfAe&index=2' ))

    itemlist.append(item.clone ( title = 'Cine Clásico Español', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=OVjZTR0w_n4&list=PLhgZbivoHwSViCGE5ljvi8cYTgouloz_-' ))

    itemlist.append(item.clone ( title = 'Otras de Cine Clásico', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=_ppHqkSS_uQ&list=PL5Elc2OLiWk6pkscyMTC6DCbE4GIeqfAe' ))

    itemlist.append(item.clone ( title = 'Bud Spencer & Terence Hill', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=PuMlIOHBaqg&list=PLy-qmp54bpB2yopTCH_4G5WLnniNQerQf' ))

    itemlist.append(item.clone ( title = 'Cantinflas', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=U5neiehwYMk&list=PLEN1o4MXDPxA-o78qTZRqEU-XgRUyh76u' ))

    itemlist.append(item.clone ( title = 'Westerns', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=1g_SGZn4_-c&list=PLLxxgrF1QnBjEvwkfWLPkr-CLEeEHJuWl' ))

    return itemlist


def list_tubes(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(str(data), '"playlist":.*?"playlist":.*?"title":(.*?)$')

    matches = scrapertools.find_multiple_matches(str(bloque), 'playlistPanelVideoRenderer":.*?simpleText":"(.*?)".*?"videoId":"(.*?)".*?"playlistId"')

    for title, _id in matches:
        if not _id or not title: continue

        thumb = 'https://i.ytimg.com/vi/' + _id + '/hqdefault.jpg'

        url = 'https://www.youtube.com/watch?v=' + _id

        itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb, group = 'youtubes' ))

    return itemlist



def sagas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div class="col">.*?<a href="(.*?)".*?data-src="(.*?)".*?alt="(.*?)"')

    for url, thumb, title in matches:
        if not title or not url: continue

        itemlist.append(item.clone( action = 'list_films', title = title, url = url, thumbnail = thumb, text_color = 'moccasin' ))

    if itemlist:
        if len(itemlist) <= 16:
            next_page = scrapertools.find_single_match(data, '<li class="page-item active">.*?<li class="page-item">.*?href="(.*?)"')

            if next_page:
                if '-pag' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', url = next_page, action = 'sagas', text_color='coral' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '>Décadas<(.*?)>Biografías<')

    matches = scrapertools.find_multiple_matches(bloque, '<li id=".*?<a href="([^"]+)">(.*?)</a>')

    for url, title in matches:
        if not url or not title: continue

        if not '/anos-' in url: continue

        itemlist.append(item.clone( action = 'list_films', title = title, url = url, text_color = 'deepskyblue' ))

    return itemlist


def listas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '>' + item.group + '<(.*?)</main>')

    if '/otras-biografias' in item.url:
        matches = scrapertools.find_multiple_matches(bloque, '<li><a href="([^"]+)".*?rel="noopener noreferrer">(.*?)</a>')

        for url, title in matches:
            if not url or not title: continue

            itemlist.append(item.clone( action= 'list_films', title = title, url = url, text_color='tan' ))
    else:
       matches = scrapertools.find_multiple_matches(bloque, 'data-src="(.*?)".*?alt="(.*?)".*?href="(.*?)"')

       for thumb, title, url in matches:
           if not url or not title: continue

           itemlist.append(item.clone( action = 'list_films', title = title, url = url, thumbnail = thumb, text_color='moccasin' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="page-item active">.*?<li class="page-item">.*?href="(.*?)"')

        if next_page:
            if '-pag' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', url = next_page, action = 'listas', text_color='coral' ))

    if not item.group == 'Directores':
       return sorted(itemlist, key = lambda it: it.title)
    else:
       return itemlist


def list_films(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<tr class="row-.*?src="(.*?)".*?alt="(.*?)".*?<a href="(.*?)"')

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for thumb, title, url in matches[desde:hasta]:
        if not url or not title: continue

        if title == '2000PeliculasSigloXX': continue

        name = title.strip()

        try:
            year = title.split('(')[1]
            year = year.split(',')[0]

            if year:
                title = title.replace(year + ', ', '')

                name = title
                name = name.split('(')[0]
                name = name.strip()
        except:
            year = ''

        if not year: year = '-'

        itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb, contentType = 'movie', contentTitle = name, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > hasta:
            next_page = item.page + 1

            itemlist.append(item.clone( title='Siguientes ...', page = next_page, action = 'list_films', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.group == 'youtubes':
        itemlist.append(Item( channel = item.channel, action = 'play', server = 'youtube', language = 'Esp', url = item.url ))
        return itemlist

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, '<source src="(.*?)"')
    if not url: url = scrapertools.find_single_match(data, '<source type="video/mp4".*?src="(.*?)"')

    url = url.replace('https://www.adf.ly/6680622/banner/', '').replace('&amp;', '&')

    if url.startswith('https://ipfs.infura.io/'):
        headers = {'referer': host}
        url = httptools.downloadpage(url, headers = headers, only_headers = True, follow_redirects = False).headers.get('location')

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', language = 'Esp', url = url ))
            return itemlist

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''
        if servidor == 'directo':
            if url.startswith('https://odysee.com'): other = 'Odysee'

        if servidor:
            url = servertools.normalize_url(servidor, url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, language = 'Esp', url = url, other = other ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div><a href="(.*?)".*?">(.*?)</a>')

    for url, title in matches:
        if not url or not title: continue

        itemlist.append(item.clone( action = 'list_films', url = url, title = title ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
