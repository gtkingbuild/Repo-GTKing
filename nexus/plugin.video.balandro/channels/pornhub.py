# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://es.pornhub.com/'


perpage = 30


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + "video/" ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + "language/spanish" ))

    itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + "video?o=cm" ))
    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + "video?o=mv" ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + "video?o=tr" ))
    itemlist.append(item.clone( title = 'Más candentes', action = 'list_all', url = host + "video?o=ht" ))

    itemlist.append(item.clone( title = 'Long play', action = 'list_all', url = host + "video?o=lg" ))
    itemlist.append(item.clone( title = 'Caseros', action = 'list_all', url = host + "video?p=homemade&o=tr" ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host + 'channels?o=rk' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host + 'categories/' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars?o=t' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('div class="channelsWrapper clearfix">.*?<a href="(.*?)".*?alt="(.*?)".*?src="(.*?)"').findall(data)

    for url, title, thumb in matches:
        itemlist.append(item.clone( action = 'list_channels', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb, text_color = 'orange' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            if '?page' in next_url or 'page=' in next_url:
                next_url = next_url.replace('&amp;', '&')

                itemlist.append(item.clone( action = 'canales', title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url, text_color = 'coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="category-wrapper">.*?<a href="(.*?)".*?alt="(.*?)".*?src="(.*?)"').findall(data)

    for url, title, thumb in matches:
        if title == 'Árabe': title = 'Arabe'

        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb, text_color = 'tan' ))

    return sorted(itemlist, key=lambda x: x.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="subscribe-to-pornstar-icon display-none">.*?href="(.*?)".*?src="(.*?)".*?alt="(.*?)"'

    matches = re.compile(patron).findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone( action = 'list_starvideos', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb, text_color='moccasin' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            if '?page' in next_url or 'page=' in next_url:
                next_url = next_url.replace('&amp;', '&')

                itemlist.append(item.clone( action = 'pornstars', title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url, text_color = 'coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h1>(.*?)<div class="pagination')
    if not bloque: bloque = scrapertools.find_single_match(data, 'id="videoSearchResult"(.*?)div class="pagination')

    if '/video/search?search=' in item.url:
        matches = re.compile('<div class="preloadLine">.*?href="(.*?)".*?title="(.*?)".*?src="(.*?)"').findall(bloque)
    else:
        matches = re.compile('<li class="pcVideoListItem.*?<a href="(.*?)".*?title="(.*?)".*?<imgsrc="(.*?)"').findall(bloque)

    for url, title, thumb, in matches:
        title = title.replace('&quot;', '').replace('&#039;', "'").strip()

        title = title.replace('&ntilde;', 'ñ').replace('&Ntilde;', 'Ñ')

        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            if '?page' in next_url or 'page=' in next_url:
                next_url = next_url.replace('&amp;', '&')

                itemlist.append(item.clone( action = 'list_all', title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url, text_color = 'coral' ))

    return itemlist


def list_channels(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="phimage".*?<a href="(.*?)".*?title="(.*?)".*?src="(.*?)"').findall(data)

    for url, title, thumb in matches:
        itemlist.append(item.clone( action = 'list_categories', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            if '?page' in next_url or 'page=' in next_url:
                next_url = next_url.replace('&amp;', '&')

                itemlist.append(item.clone( action = 'list_channels', title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url, text_color = 'coral' ))

    return itemlist


def list_categories(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="floatLeft"><h2>([^<]+)</h2></div><div class="floatRight"><a class="seeAllButton greyButton light" href="([^"]+)'

    matches = re.compile(patron).findall(data)

    for url, title, thumb in matches:
        if 'premium' in title: continue

        itemlist.append(item.clone( action = 'list_catvideos', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb ))

    return itemlist


def list_catvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="videos row-5-thumbs videosGridWrapper".*?id="showAllChanelVideos">(.*?)</div></div></ul>>')

    matches = re.compile('<a href="([^"]+)" title="([^"]+)"class="[^"]+"[^<]+<imgsrc="([^"]+)"').findall(bloque)

    for url, title, thumb in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            if '?page' in next_url or 'page=' in next_url:
                next_url = next_url.replace('&amp;', '&')

                itemlist.append(item.clone( action = 'list_videos', title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url, text_color = 'coral' ))

    return itemlist


def list_starvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="phimage".*?<a href="(.*?)".*?title="(.*?)".*?src="(.*?)"').findall(data)

    for url, title, thumb in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            if '?page' in next_url or 'page=' in next_url:
                next_url = next_url.replace('&amp;', '&')

                itemlist.append(item.clone( action = 'list_starvideos', title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    headers = {'Referer': item.url}

    data = do_downloadpage(item.url, headers = headers)

    videos = get_video_url(item.url)

    if not videos:
        platformtools.dialog_notification('PornHub', '[COLOR red]El archivo no existe o ha sido borrado[/COLOR]')
        return

    for qlty, url in videos:
        itemlist.append(Item( channel = item.channel, action='play', title = '', url = url, quality = qlty, server='directo', language = 'Vo') )

    return itemlist


def get_video_url(page_url):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    resp = httptools.downloadpage(page_url)

    if not resp.sucess or "Not Found" in resp.data or "File was deleted" in resp.data or "This video has been removed" in resp.data or "Video has been flagged for verification" in resp.data or "is no longer available" in resp.data:
        return video_urls

    data = resp.data

    data = scrapertools.find_single_match(data, '<div id="player"(.*?)</script>')

    data = data.replace('" + "', '')

    matches = scrapertools.find_multiple_matches(data, 'var media_\d+=([^;]+)')

    if not matches: matches = scrapertools.find_multiple_matches(data, '"videoUrl":"(.*?)"')

    for match in matches:
        match =  match.replace('\\/', '/')

        url = match

        if 'master.m3u8' in url or '/hls/' in url:
            if not 'K,' in url and not "get_media" in url:
                qlty = scrapertools.find_single_match(url, '/(\d+P)_')

                video_urls.append([qlty, url])

    return video_urls


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'video/search?search=%s&o=mr' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
