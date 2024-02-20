# -*- coding: utf-8 -*-

import re, string

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = 'https://www.eporner.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data
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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = host + '/0/', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Los mejores', action = 'list_all', url = host + 'best-videos/' ))
    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'most-viewed/' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'top-rated/' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host + 'cats/', group = 'cats' ))

    itemlist.append(item.clone( title = 'Por estrella (A - Z)', action = 'pornstars', url = host + 'pornstar-list/' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    if item.group == 'cats':
        matches = scrapertools.find_multiple_matches(data, '<div class="categoriesbox"(.*?)</div></div>')
    else:
        matches = scrapertools.find_multiple_matches(data, '<div class="mbprofile">(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        url = host[:-1] + url

        if 'data-src=' in match:
            thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        else:
            thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color = 'tan' ) )

    if item.group == 'cats' or item.group == 'stars':
        return sorted(itemlist,key=lambda x: x.title)

    if itemlist:
        bloque = scrapertools.find_single_match(data, '<div class="numlist2(.*?)</div>')
        next_page = scrapertools.find_single_match(bloque, "<span class='nmhere'>.*?<a href='(.*?)'")

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='categorias', title='Siguientes ...', url=next_page, text_color = 'coral' ) )

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone (action = 'categorias', title = 'Más Populares', url = item.url, group = 'stars', text_color = 'orange' ))

    for letra in string.ascii_uppercase:
        url = item.url + letra + '/'

        itemlist.append(item.clone (title = letra, action = 'categorias', url = url, text_color = 'moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    if '<div id="vidresults"' in data:
        bloque = scrapertools.find_single_match(data, '<div id="vidresults"(.*?)<div class="numlist2')
    elif '<div class="vidresults' in data:
        bloque = scrapertools.find_single_match(data, '<div class="vidresults(.*?)<div class="numlist2')
    else:
        bloque = data

    matches = scrapertools.find_multiple_matches(bloque, 'data-id="(.*?)</p></div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('&amp;', '&')

        url = host[:-1] + url

        if 'data-src=' in match:
            thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        else:
            thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        time = scrapertools.find_single_match(match, 'title="Duration">(.*?)</span>')

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        bloque = scrapertools.find_single_match(data, '<div class="numlist2(.*?)</div>')
        next_page = scrapertools.find_single_match(bloque, "<span class='nmhere'>.*?<a href='(.*?)'")

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="dloaddivcol">(.*?)</div>')

    links = scrapertools.find_multiple_matches(bloque, '(.*?)<br />')

    for link in links:
        qlty = scrapertools.find_single_match(link, "(.*?):")

        qlty = qlty.replace('<u>', '').strip()

        url = scrapertools.find_single_match(link, 'href="(.*?)"')

        if url:
            url = host[:-1] + url

            itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='directo', language = 'Vo', quality = qlty) )

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'search/%s/' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
