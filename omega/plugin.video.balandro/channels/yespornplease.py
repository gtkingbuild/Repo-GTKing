# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://yespornpleasexxx.com/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    timeout = None
    if host in url: timeout = config.get_setting('channels_repeat', default=30)

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    if not data:
        if url.startswith(host):
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('YesPornPlease', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host + 'xnxx-tags/' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars/' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'Categories<p>(.*?)Friends<p>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url, text_color = 'orange' ))

    if itemlist:
        itemlist.append(item.clone (action='list_all', title= 'BangBros', url = host + '/bangbros/', text_color = 'orange' ))
        itemlist.append(item.clone (action='list_all', title= 'Brazzers', url = host + '/brazzers/', text_color = 'orange' ))
        itemlist.append(item.clone (action='list_all', title= 'Reality Kings', url = host + '/reality-kings/', text_color = 'orange' ))

    return sorted(itemlist, key=lambda x: x.title)


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Categories<(.*?)Categories<p>')

    matches = re.compile('<a href="(.*?)".*?src="(.*?)".*?<figcaption>(.*?)</figcaption>', re.DOTALL).findall(bloque)

    for url, thumb, title in matches:
        if title == 'All Videos': continue

        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color = 'tan' ))

    return sorted(itemlist, key=lambda x: x.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Pornstars</h1>(.*?)</footer>')

    matches = re.compile('<a(.*?)</a></div>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, '<figcaption>(.*?)</figcaption>')
        if not title: title = scrapertools.find_single_match(match, 'class="wp-caption-text gallery-caption">(.*?)</a>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='moccasin' ))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    if not matches: matches = re.compile('<div class="col-xs-(.*?)</div></div></div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        time = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        title = title.replace('&#8217;', '').replace('&#8211;', '&').replace('&#038;', '&')

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<link rel="next" href="(.*?)"')

        if next_page:
            if'/page/' in next_page:
               itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches0 = re.compile('<iframe.*?data-litespeed-src="(.*?)"', re.DOTALL).findall(data)
    matches1 = re.compile('<iframe.*?src="(.*?)"', re.DOTALL).findall(data)
    matches2 = re.compile('<source type="video/mp4".*?src="(.*?)"', re.DOTALL).findall(data)

    matches = matches0 + matches1 + matches2

    for link in matches:
        if '//a.' in link: continue

        elif link == 'about:blank': continue

        if host in link:
            data2 = do_downloadpage(link)

            url = scrapertools.find_single_match(data2, '<source type="video/mp4".*?src="(.*?)"')

            if url:
                url += '|Referer=%s' % item.url

                itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, language = 'Vo' ))

                return itemlist

        elif 'player-x.php?' in link:
            data2 = do_downloadpage(link)

            url = scrapertools.find_single_match(data2, '<source type="video/mp4".*?src="(.*?)"')

            url = scrapertools.find_single_match(data, 'mp4="(.*?)"')
 
            if url:
                url += '|Referer=%s' % item.url

                itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, language = 'Vo' ))

                return itemlist

        servidor = servertools.get_server_from_url(link)
        servidor = servertools.corregir_servidor(servidor)

        link = servertools.normalize_url(servidor, link)

        if not 'http' in link: link = 'https:' + link

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link, language = 'Vo' ))

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
