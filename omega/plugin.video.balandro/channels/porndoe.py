# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools


host = 'https://porndoe.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'videos' ))

    itemlist.append(item.clone( title = 'Exclusivos', action = 'list_all', url = host + 'category/74/premium-hd', text_color = 'pink' ))

    itemlist.append(item.clone( title = 'Escenas', action = 'list_all', url = host + 'movies', text_color = 'tan' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'videos?sort=views' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'videos?sort=likes' ))

    itemlist.append(item.clone( title = 'Más candentes', action = 'list_all', url = host + 'videos/top-porn-germany' ))

    itemlist.append(item.clone( title = 'Long Play', action = 'list_all', url = host + 'videos?sort=length' ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host + 'channels?sort=ranking' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host + 'categories?sort=name' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = scrapertools.find_single_match(data, '<div class="channels-list">(.*?)</section>')

    matches = re.compile('<div class="channels-item-thumb">.*?title="(.*?)".*?src="(.*?)".*?href="(.*?)"').findall(bloque)

    for title, thumb, url in matches:
        url = host[:-1] + url

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, thumbnail = thumb, text_color = 'violet' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<div class="pager">.*?<span class="pager-item pager-active">.*?href="(.*?)"')

        if next_url:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'canales', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        text_color = 'coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<a class="-ctlc-item".*?href="(.*?)".*?title="(.*?)".*?src="(.*?)"').findall(data)

    for url, title, thumb in matches:
        url = host[:-1] + url

        itemlist.append(item.clone (action='list_all', title = title, url = url, thumbnail = thumb, text_color = 'moccasin' ))

    return sorted(itemlist,key=lambda x: x.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<div class="actors-list-item">.*?href="(.*?)".*?title="(.*?)".*?src="(.*?)"').findall(data)

    for url, title, thumb in matches:
        url = host[:-1] + url

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, thumbnail = thumb, text_color='orange' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<div class="pager">.*?<span class="pager-item pager-active">.*?href="(.*?)"')

        if next_url:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'pornstars', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        text_color = 'coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<div class="video-item"(.*?)</div></div>').findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, 'label="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, 'label=""(.*?)"')

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        time = scrapertools.find_single_match(match, 'duration="(.*?)"')

        url = host[:-1] + url

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="pager-item pager-next".*?href="(.*?)"')

        if next_page:
            if 'page=' in next_page:
                next_page = host[:-1] + next_page

                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    logger.info()
    itemlist = []

    videos = get_video_url(item.url)

    if str(videos) == '': return itemlist

    if not videos:
        platformtools.dialog_notification('Nuvid', '[COLOR red]El archivo no existe o ha sido borrado[/COLOR]')
        return

    for qlty, url in videos:
        itemlist.append(Item( channel = item.channel, action='play', title='', url = url, quality = qlty, server = 'directo', language = 'Vo') )

    return itemlist


def get_video_url(page_url):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = do_downloadpage(page_url)

    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data: return video_urls

    id = scrapertools.find_single_match(data, '"id": "(\d+)"')

    if not id: return ''

    data = do_downloadpage('https://porndoe.com/service/index?device=desktop&page=video&id=' + id, headers = {'Referer': page_url} )

    if not data or str(data) == '[]': return ''

    jdata = jsontools.load(data)

    matches = jdata['payload']['player']['sources']['mp4']

    for elem in matches:
        url = elem['link']

        if "signup" in url: continue

        quality = elem['height']

        video_urls.append(['%s' % quality, url])

    return video_urls


def search(item, texto):
    logger.info()
    try:
        item.tex = texto.replace(" ", "+") + '/'
        item.url = host + 'search?keywords=' + item.tex
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

