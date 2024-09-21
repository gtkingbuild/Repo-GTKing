# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools


host = 'https://es.redtube.com/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'newest/'))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'inyourlanguage/es/'))

    itemlist.append(item.clone( title = 'Tendencias', action = 'list_all', url = host + 'hot/' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'mostviewed/' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'top/' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'redtube/hd/' ))

    itemlist.append(item.clone( title = 'Long Play', action = 'list_all', url = host + 'longest?period=alltime' ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url= host + 'channel/top-rated/' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url= host + 'categories/popular/' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstar/' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron  = '<li class="channel-box channel-box-layout-shift">.*?<a href="([^"]+)".*?alt="([^"]+)".*?data-src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, thumb in matches:
         url = host[:-1] + url

         itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color = 'orange' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a id="wp_navNext".*?href="([^"]+)">')
        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='canales', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron = '<li id="categories_list_block_.*?'

    patron += 'href="([^"]+)".*?data-src\s*=\s*"([^"]+)".*?alt="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title in matches:
         if title == 'Alta Definición': continue

         if title == 'Árabe': title = 'Arabe'

         url = host[:-1] + url

         itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='tan' ))

    return sorted(itemlist,key=lambda x: x.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron  = '<li id="recommended_pornstars_block_ps_.*?'

    patron += 'href="([^"]+)".*?data-src\s*=\s*"([^"]+)".*?alt="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title in matches:
         url = host[:-1] + url

         itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='moccasin' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a id="wp_navNext".*?href="([^"]+)">')
        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='pornstars', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    data = scrapertools.find_single_match(data,'<em class="premium_tab_icon rt_icon rt_Menu_Star">(.*?)<div class="footer">')
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron = '<div class="video_block_wrapper js_mediaBookBounds ">.*?'
    patron += 'data-o_thumb="([^"]+)".*?'
    patron += '<span class="duration">(.*?)</a>.*?'
    patron += '<a title="([^"]+)".*?href="(/\d+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for thumb, duration, title, url in matches:
        url = host[:-1] + url

        duration = scrapertools.find_single_match(duration, '(\d+:\d+)')

        title = title.replace('&ntilde;', 'ñ').replace('&Ntilde;', 'Ñ').replace('&apos;', "'")
        title = title.replace('&amp;', '').strip()

        title = "[COLOR tan]%s[/COLOR] %s" % (duration, title)

        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<a id="wp_navNext".*?href="([^"]+)">').replace("amp;", "")

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    url = item.url

    videos = get_video_url(item.url)

    if not videos:
        platformtools.dialog_notification('RedTube', '[COLOR red]El archivo no existe o ha sido borrado[/COLOR]')
        return

    for vid in videos:
        qlty = vid[0]
        url = vid[1]

        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, quality = qlty, server='directo', language = 'Vo') )

    return itemlist


def get_video_url(page_url):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    resp = httptools.downloadpage(page_url)

    if not resp.sucess or "Not Found" in resp.data or "File was deleted" in resp.data or "This video has been removed" in resp.data or "Video has been flagged for verification" in resp.data or "is no longer available" in resp.data:
        return video_urls

    data = resp.data

    url = scrapertools.find_single_match(data,'"format":"mp4","videoUrl":"([^"]+)"')

    url = url.replace("\\", "")

    if url.startswith('/'): url = host[:-1] + url

    data = httptools.downloadpage(url).data

    matches = scrapertools.find_multiple_matches(data, '"defaultQuality":.*?,"quality":"([^"]+)","videoUrl"\:"([^"]+)"')

    for qlty, url in matches:
        url =  url.replace('\\/', '/')

        video_urls.append([qlty, url])
 
    return video_urls


def search(item, texto):
    logger.info()
    try:
        item.url =  host + '?search=%s' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
