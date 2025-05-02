# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://www.moviesdvdr.co/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_moviesdvdr_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar ...[/B]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    hay_proxies = False
    if config.get_setting('channel_moviesdvdr_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('moviesdvdr', url, post=post, headers=headers).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers).data

        if not data:
            if not '/?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('MoviesDvdr', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('moviesdvdr', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='moviesdvdr', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En DVDrip', action = 'list_all', url = host + 'genero/dvdrip/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<nav class="menu">(.*?)</nav>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if '/dvdrip/' in url: continue

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '</h2>(.*?)</main>')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="item hitem">(.*?)</a></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<div class="titulo">.*?<span>(.*?)</span>')

        if not url or not title: continue

        title = title.replace('&#8217;s', "'s").replace('&#8217;', '')

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<div class='wp-pagenavi'" in data:
           next_url = scrapertools.find_single_match(data, "<div class='wp-pagenavi'.*?class='current'>.*?" + 'href="(.*?)"')

           if next_url:
               if '/page/' in next_url:
                   itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Version subtitulada': 'Vose'}

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, '<a class="torrent_download linkastro".*?href="(.*?)"')

    for url in links:
        if url.startswith("//"): url = 'https:' + url
        elif url.startswith("/"): url = host[:-1] + url

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = 'Esp', quality = 'DVDRip' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith(".torrent"):
        data = do_downloadpage(item.url)

        if data:
            if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
               return 'Archivo [COLOR red]Inexistente[/COLOR]'

        itemlist.append(item.clone( url = url, server = 'torrent' ))

    else:
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(url, host_torrent)

        if url_base64.startswith('magnet:'):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

        elif url_base64.endswith(".torrent"):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
