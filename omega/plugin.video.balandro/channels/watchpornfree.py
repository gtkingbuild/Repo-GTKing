# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://watchpornfree.info/'


perpage = 30


def do_downloadpage(url, post=None, headers=None):
    timeout = None
    if host in url: timeout = config.get_setting('channels_repeat', default=30)

    raise_weberror = True
    if 'release-year/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

    if not data:
        if url.startswith(host):
            if not '?s' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('WatchPornFree', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

    return data


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'scenes/' ))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = host + 'category/featured/', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host, text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Parodias', action = 'list_all', url = host + 'category/parodies/' ))

    itemlist.append(item.clone( title = 'Por estudio', action = 'categorias', url = host, group = 'estudios' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host, group = 'categorias'))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', url = host))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    if item.group == 'estudios':
        data = scrapertools.find_single_match(data, 'Studios</a>(.*?)</ul>')
    else:
        data = scrapertools.find_single_match(data, '>Categories</div>(.*?)</ul>')

    matches = re.compile('href="([^"]+)".*?>([^"]+)</a></li>', re.DOTALL).findall(data)

    for url, title in matches:
        if item.group == 'categorias':
            if title == 'Parodies': continue
            elif title == 'Porn Movies': continue

        itemlist.append(item.clone (action='list_all', title=title, url=url, text_color = 'orange' ))

    if item.group == 'estudios':
        return sorted(itemlist, key=lambda x: x.title)

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1971, -1):
        url = host + 'release-year/' + str(x)

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color='orange' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron = '<article class="TPost B">.*?<a href="(.*?)">.*?data-lazy-src="(.*?)".*?<div class="Title">(.*?)</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    num_matches = len(matches)

    for url, thumb, title in matches[item.page * perpage:]:
        if len(itemlist) >= perpage: break

        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

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

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', '', data)

    bloque = scrapertools.find_single_match(data, '>Watch Online<(.*?)</div></div></div>')

    matches = re.compile('href="(.*?)"', re.DOTALL).findall(bloque)

    ses = 0

    for url in matches:
        ses += 1

        if 'vev.io' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vo', other = other ))

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
            elif '/nitroflare.' in url: continue
            elif '/katfile.' in url: continue
            elif '/fikper.' in url: continue
            elif '/turbobit.' in url: continue
            elif '/hitfile.' in url: continue

            if '/drivevideo.' in url:
                if 'link=' in url: url = scrapertools.find_single_match(url, '.*?link=(.*?)$')

            if url:
                url = url.replace('//filemoon.sx/download/', '//filemoon.sx/d/')

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                other = 'D'

                if servidor == 'various': other = servertools.corregir_other(url)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vo', other = other ))


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
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<source src="(.*?)"')

        if not url: return itemlist

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
