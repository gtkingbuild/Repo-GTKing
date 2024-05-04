# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import time

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, jsontools

from threading import Thread


host = "https://www.porntube.com/"


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_xxx', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'videos?sort=date&hl=es' ))

    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'videos?sort=rating&hl=es&time=month' ))
    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'videos?sort=views&hl=es&time=month' ))

    itemlist.append(item.clone( title = 'Long play', action = 'list_all', url = host + 'videos?sort=duration&hl=es' ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host + 'api/channel/list?filter=%7B%7D&order=rating&ssr=false&orientation=straigh' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'api/pornstar/list?filter=%7B%7D&ssr=false&orientation=straight' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    headers = {'referer': host + 'channels?hl=es'}
    data = httptools.downloadpage(item.url, headers = headers).data

    data = jsontools.load(data).get('channels', {}).get('_embedded', {}).get('items', [])

    for can in data:
        title = can['name']

        thumb = can['thumbUrl']

        url = host + 'channels/%s?hl=es' % can['slug']

        itemlist.append(item.clone( title = title, thumbnail = thumb, url = url, action ='list_all', text_color = 'orange' ))

    return sorted(itemlist, key=lambda it: it.title)


def categorias(item):
    logger.info()
    itemlist = []

    url = host + 'api/tag/list?orientation=straight&hl=es&ssr=false'

    headers = {'referer': host + 'tags?hl=es'}
    data = httptools.downloadpage(url, headers = headers).data

    data = jsontools.load(data).get('tags', {}).get('_embedded', {}).get('items', [])

    for cat in data:
        title = cat['name']
        title = title.capitalize()

        thumb = cat['thumbDesktop']

        url = host + 'tags/%s?hl=es' % cat['slug']

        itemlist.append(item.clone( title = title, thumbnail = thumb, url = url, action ='list_all', text_color='tan' ))

    return sorted(itemlist, key=lambda it: it.title)


def pornstars(item):
    logger.info()
    itemlist = []

    headers = {'referer': host + 'pornstar?hl=es'}
    data = httptools.downloadpage(item.url, headers = headers).data

    data = jsontools.load(data).get('pornstars', {}).get('_embedded', {}).get('items', [])

    for pns in data:
        title = pns['name']

        thumb = pns['thumbUrl']

        url = host + 'pornstars/%s?hl=es' % pns['slug']

        itemlist.append(item.clone( title = title, thumbnail = thumb, url = url, action ='list_all', text_color='moccasin' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    threads = list()

    data = httptools.downloadpage(item.url).data

    i = 0

    matches = scrapertools.find_multiple_matches(data, '<div class="video-item"><a title="([^"]+)" href="([^"]+)">')

    for title, url in matches:
        if url.startswith('/'): url = host + url[1:]

        new_item = item.clone( action = 'findvideos', title = title, url = url, contentType = 'movie', contentTitle = title, contentExtra='adults', pos = i )

        t = Thread(target = get_embed, args = [new_item, itemlist])

        t.setDaemon(True)
        t.start()
        threads.append(t)
        i += 1

    if PY3:
        while [t for t in threads if t.is_alive()]:
            time.sleep(0.5)
    else:
        while [t for t in threads if t.isAlive()]:
            time.sleep(0.5)

    itemlist = sorted(itemlist, key=lambda x: x.pos)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="pagination-item next"><a href="([^"]+)"')

        if next_page:
            if next_page.startswith('/'): next_page = host + next_page[1:]

            itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', text_color='coral' ))

    return itemlist


def get_embed(item, itemlist):
    try:
       if item.query:
           name = scrapertools.find_single_match(item.url, '/videos/([^_]+)_')
           media_embed = item.url.split('_')[1]
       else:
           name, media_embed = scrapertools.find_single_match(item.url, '/videos/([^?]+)').split('_')
    except:
       media_embed = ''
       logger.info("PorTube error get_embed")

    if media_embed:
        url = host + 'api/videos/%s?ssr=true&slug=%s&hl=es&orientation=straight' % (media_embed, name)

        data = httptools.downloadpage(url).data
        result = jsontools.load(data)

        link = '+'.join([str(e['height']) for e in result['video']['encodings']])

        thumb = result['video']['masterThumb']
        title = (item.title + ' [HD]') if result['video']['isHD'] else item.title
        url = 'https://tkn.porntube.com/%s/desktop/%s' % (result['video']['mediaId'], link)

        itemlist.append(item.clone( url = url, title = title, thumbnail = thumb ))


def findvideos(item):
    logger.info()
    itemlist = []

    headers = {'origin': host}
    data = httptools.downloadpage(item.url, headers = headers).data

    data = jsontools.load(data)

    videos = scrapertools.find_multiple_matches(str(data), ".*?'(.*?)'.*?'token'.*?:.*?'(.*?)'")

    for qlty, url in videos:
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, quality = qlty, server = 'directo', language = 'Vo' ))

    return sorted(itemlist, key=lambda it: it.quality)


def search(item, texto):
    logger.info()
    try:
        item.query = texto.replace(" ", "+")
        item.url =  host + 'search?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
