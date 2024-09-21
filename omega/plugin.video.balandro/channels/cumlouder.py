# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = 'https://www.cumlouder.com'


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_xxx', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color='orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all' ))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = host +'/2/', page = 1, text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por repertorio', action = 'repertorios' ))
    itemlist.append(item.clone( title = 'Por canal', action = 'canales' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', ))

    return itemlist


def repertorios(item):
    logger.info()
    itemlist = []

    if not item.page:
        item.page = 0
        item.url = host + '/series/'

    data = httptools.downloadpage(item.url).data

    patron = '<div itemprop="itemListElement".*?href="([^"]+)".*?data-src="([^"]+)".*?h2 itemprop="name">([^<]+).*?p>([^<]+)</p>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title, vid in matches:
        vid = vid.lower()
        vid = vid.replace('videos', '').strip()

        title = title.lower().capitalize()

        titulo = '[COLOR orange]%s[/COLOR] (%s)' % (title, vid)

        itemlist.append(item.clone( action = 'list_all', url = url, thumbnail = thumb, title = titulo, page = 1 ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a class="btn-pagination" itemprop="name" href="(.*?)"')

        if next_url:
            next_url = host + next_url

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, page = item.page + 1, action = 'repertorios', text_color = 'coral' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    if not item.page:
        item.page = 0
        item.url = host + '/channels/'

    data = httptools.downloadpage(item.url).data

    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<a channel-url=.*?href="([^"]+)".*?data-src="([^"]+)".*?alt="([^"]+)".*?<span class="ico-videos sprite"></span>([^<]+)</span>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, vid in matches:
        url = host + url + '?show=channels'

        vid = vid.lower()
        vid = vid.replace('videos', '').strip()

        titulo = '[COLOR orange]%s[/COLOR] (%s)' % (title, vid)

        if not thumb.startswith('http'): thumb = 'https:' + thumb

        itemlist.append(item.clone( action = 'list_all', url = url, title = titulo, thumbnail = thumb, page = 1, text_color = 'tan' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a class="btn-pagination" itemprop="name" href="(.*?)"')

        if next_url:
            next_url = host + next_url

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, page = item.page + 1, action = 'canales', text_color = 'coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    if not item.page:
        item.page = 0
        item.url = host + '/categories/'

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<a tag-url=.*?href="([^"]+)".*?data-src="([^"]+)".*?alt="([^"]+)"'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title in matches:
        url = host + url

        if not thumb.startswith('http'): thumb = 'https:' + thumb

        itemlist.append(item.clone( action = 'list_all', url = url, title = title, thumbnail = thumb, page = 1, text_color='tan' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a class="btn-pagination" itemprop="name" href="(.*?)"')

        if next_url:
            next_url = host + next_url

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, page = item.page + 1, action = 'categorias', text_color = 'coral' ))

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    if not item.page:
        item.page = 0
        item.url = host + '/girls/'

    data = httptools.downloadpage(item.url).data

    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = 'class="muestra-escena muestra-pornostar show-girl" href="([^"]+)".*?data-src="([^"]+)".*?' \
             'alt="([^"]+)".*?<span class="videos"> <span class="ico-videos sprite"></span>([^<]+)</span>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, vid in matches:
        url = host + url

        vid = vid.lower()
        vid = vid.replace('videos', '').strip()

        titulo = '[COLOR orange]%s[/COLOR] (%s)' % (title, vid)

        itemlist.append(item.clone( action = 'list_all', url = url, thumbnail = thumb, title = titulo, page = 1, text_color='moccasin' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a class="btn-pagination" itemprop="name" href="(.*?)"')

        if next_url:
            next_url = host + next_url

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, page = item.page + 1, action = 'pornstars', text_color = 'coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page:
        item.page = 0
        item.url = host + '/porn/'

    data = httptools.downloadpage(item.url).data

    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<a class="muestra-escena" href="([^"]+)".*?data-src="([^"]+)".*?alt="([^"]+)".*?<span class="ico-minutos sprite"></span>([^<]+)</span>(.*?)</a>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, durac, qlty in matches:
        url = host + url

        if not thumb.startswith('http'): thumb = 'https:' + thumb

        thumb = thumb.replace('ep1.jpg', 'ep.jpg')

        durac = durac.replace(' m', '').strip()

        titulo = "[COLOR tan]%s[/COLOR] %s" % (durac, title)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, quality = qlty,
                                    contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a class="btn-pagination" itemprop="name" href="(.*?)"')

        if next_url:
            next_url = host + next_url

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, page = item.page + 1, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '''<source src="([^"]+).*?res='([^']+)'''

    matches = scrapertools.find_multiple_matches(data, patron)
    if not matches: matches = scrapertools.find_multiple_matches(data, '<source src="(.*?)".*?res="(.*?)"')

    for url, qlty in matches:
        url = url.replace("&amp;", "&")

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = qlty, url = url, language = 'Vo' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "/search?q=%s" % (texto.replace(" ", "%20"))
        item.page = 1
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
