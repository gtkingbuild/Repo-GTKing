# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://xmoviesforyou.com/'


def do_downloadpage(url, post=None, headers=None):
    timeout = None
    if host in url: timeout = config.get_setting('channels_repeat', default=30)

    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if not data:
        if url.startswith(host):
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('XmoviesForYou', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

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

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron = '<article id="post-\d+.*?<a href="([^"]+)" rel="bookmark" title="([^"]+)".*?src="([^"]+)"'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, title, thumb, in matches:
        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="(.*?)"')

        if next_page:
            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = scrapertools.find_single_match(data, '<div class="entry-content post_content">(.*?)</span></strong>')

    matches = re.compile('<(?:iframe src|IFRAME SRC|a href)="([^"]+)"', re.DOTALL).findall(bloque)
    if not matches: matches = re.compile('<a href="(.*?)"', re.DOTALL).findall(bloque)

    ses = 0

    for url in matches:
        ses += 1

        # ~ Netu
        if not "0load" in url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server = servidor, language = 'Vo') )

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

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
