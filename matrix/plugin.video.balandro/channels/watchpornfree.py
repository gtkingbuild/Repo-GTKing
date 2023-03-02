# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://watchpornfree.info/'

perpage = 30


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'scenes/' ))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = host + 'scenes/category/featured-scenes/' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Parodias', action = 'list_all', url = host + 'category/parodies/' ))

    itemlist.append(item.clone( title = 'Por estudio', action = 'categorias', url = host, group = 'estudios' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host, group = 'categorias'))
    itemlist.append(item.clone( title = 'Por año', action = 'categorias', url = host, group = 'years'))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    if item.group == 'estudios':
        data = scrapertools.find_single_match(data, 'Studios</a>(.*?)</ul>')
    elif item.group == 'years':
        data = scrapertools.find_single_match(data, 'Years</a>(.*?)</ul>')
    else:
        data = scrapertools.find_single_match(data, '>Categories</div>(.*?)</ul>')

    matches = re.compile('href="([^"]+)".*?>([^"]+)</a></li>', re.DOTALL).findall(data)

    for url, title in matches:
        if item.group == 'categorias':
            if title == 'Parodies': continue
            elif title == 'Porn Movies': continue

        itemlist.append(item.clone (action='list_all', title=title, url=url) )

    if item.group == 'estudios':
        return sorted(itemlist, key=lambda x: x.title)
    elif item.group == 'years':
        return sorted(itemlist, key=lambda x: x.title, reverse=True)

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron = '<article class="TPost B">.*?<a href="(.*?)">.*?data-lazy-src="(.*?)".*?<div class="Title">(.*?)</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    num_matches = len(matches)

    for url, thumb, title in matches[item.page * perpage:]:
        if len(itemlist) >= perpage: break

        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie',
                                    contentTitle = title, contentExtra='adults') )

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data,'<a class="next page-numbers" href="([^"]+)">Next &raquo;</a>')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, page= 0, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', '', data)

    bloque = scrapertools.find_single_match(data, '>Watch Online<(.*?)</div></div></div>')

    matches = re.compile('href="(.*?)"', re.DOTALL).findall(bloque)

    ses = 0

    for url in matches:
        ses += 1

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue
        elif 'vev.io' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''
        if servidor == 'directo':
            if '/yodbox.' in url: other = 'Yodbox'
            else: continue

        if servidor == 'various':
            if '/tubeload.' in url: other = 'Tubeload'
            elif '/mvidoo.' in url: other = 'Mvidoo'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'VO', other = other ))

    # ~  Download
    if '>Download<' in data:
        bloque = scrapertools.find_single_match(data, '>Download<(.*?)</div></div></div>')

        matches = re.compile('href="(.*?)"', re.DOTALL).findall(bloque)

        for url in matches:
            ses += 1

            if '/rapidgator.' in url: continue
            elif '/uploaded.' in url: continue
            elif '/nitro.' in url: continue
            elif '/ddownload.' in url: continue
            elif '/hexupload.' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            other = 'D'
            if servidor == 'directo':
               if '/yodbox.' in url: other = 'Yodbox'
               else: continue

            if servidor == 'various':
                if '/tubeload.' in url: other = other + ' Tubeload'
                elif '/mvidoo.' in url: other = other + ' Mvidoo'

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'VO', other = other ))


    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    servidor = item.server

    if item.server == 'directo':
        data = httptools.downloadpage(item.url).data

        url = scrapertools.find_single_match(data, '<source src="(.*?)"')

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

    else:
       if '/drivevideo.' in url:
           if '?link=' in url:
               url = scrapertools.find_single_match(url, '.*?link=(.*?)$')

               servidor = servertools.get_server_from_url(url)
               servidor = servertools.corregir_servidor(servidor)

    itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + '?s=%s' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
