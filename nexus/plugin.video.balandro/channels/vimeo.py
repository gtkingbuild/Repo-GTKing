# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb


host = "https://vimeo.com/"


unicode = str


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'groups/documentales/videos/', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'groups/documentales/videos/sort:plays/format:thumbnail',
                                search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'groups/documentales/videos/sort:likes/format:thumbnail',
                                search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Por orden de fecha', action = 'list_all', url = host + 'groups/documentales/videos/sort:date/format:thumbnail',
                                search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Por orden alfabético', action = 'list_all',
                                url = host + 'groups/documentales/videos/sort:alphabetical/format:thumbnail', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Por duración', action = 'list_all', url = host + 'groups/documentales/videos/sort:duration/format:thumbnail',
                                search_type = 'documentary' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'id="clip_.*?<a href="(.*?)".*? title="(.*?)".*?<img src="(.*?)"')

    for url, title, thumb in matches:
        url = host[:-1] + url

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, contentExtra='documentary' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'class="selected">.*?<a href="(.*?)"')
        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone( title='Siguientes ...', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    try:
        data = httptools.downloadpage(item.url).data
    except:
        return itemlist

    url = scrapertools.find_single_match(data, '"embedUrl":"(.*?)"')

    if not url: url = scrapertools.find_single_match(data, '<meta property="og:video:url" content="(.*?)"')
    if not url: url = scrapertools.find_single_match(data, '<meta name="twitter:player" content="(.*?)"')

    if url:
        url = url.replace('&amp;', '')

        itemlist.append(Item( channel = item.channel, action = 'play', server='vimeo', title = '', url = url, language = 'Esp' ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(str(data), '"type":"clip","clip":.*?"uri":"(.*?)".*?"name":"(.*?)".*?"pictures".*?"link":"(.*?)"')

    for url, title, thumb in matches:
        title = unicode(title, 'utf8').encode('utf8')

        title = title.replace('\\/', '').strip()

        url = url.replace('\\/', '/')
        url = host[:-1] + url

        url = url.replace('/videos/', '/groups/documentales/videos/')

        thumb = thumb.replace('\\/', '/')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, contentExtra='documentary' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search?category=documentary&q=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
