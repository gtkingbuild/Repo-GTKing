# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://yespornpleasexxx.com/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_yespornplease_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if not config.get_setting('channel_yespornplease_proxies', default=''): raise_weberror=False

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('yespornplease', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                data = httptools.downloadpage_proxy('yespornplease', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        except:
            pass

    if '<title>Just a moment...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

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
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_yespornplease', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host + 'tags/' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars/' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'Categories<p>(.*?)Friends<p>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url ))

    if itemlist:
        itemlist.append(item.clone (action='list_all', title= 'BangBros', url = host + '/bangbros/' ))
        itemlist.append(item.clone (action='list_all', title= 'Brazzers', url = host + '/brazzers/' ))
        itemlist.append(item.clone (action='list_all', title= 'Reality Kings', url = host + '/reality-kings/' ))

    return sorted(itemlist, key=lambda x: x.title)


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="box">.*?<a href="(.*?)".*?<img src="(.*?)".*?">(.*?)</a>', re.DOTALL).findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb) )

    return sorted(itemlist, key=lambda x: x.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="box">.*?<a href="(.*?)".*?<img src="(.*?)".*?">(.*?)</a>', re.DOTALL).findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb) )

    matches2 = re.compile('<figure class="gallery-item">.*?<img src="(.*?)".*?alt="(.*?)".*?<a href="(.*?)"', re.DOTALL).findall(data)

    for thumb, title, url in matches2:
        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb) )

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="post-preview-styling">.*?<a href="(.*?)".*?title="(.*?)".*?src="(.*?)"', re.DOTALL).findall(data)

    for url, title, thumb in matches:
        title = title.replace('&#8211;', '&').replace('&#038;', '&')

        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie',
                                    contentTitle = title, contentExtra='adults') )

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

    matches = re.compile('<iframe src="(.*?)"', re.DOTALL).findall(data)

    for link in matches:
        if host in link:
            data2 = do_downloadpage(link)

            url = scrapertools.find_single_match(data2, '<source type="video/mp4".*?src="(.*?)"')

            if url:
                url += '|Referer=%s' % item.url

                itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, language = 'VO' ))

        servidor = servertools.get_server_from_url(link)
        servidor = servertools.corregir_servidor(servidor)

        link = servertools.normalize_url(servidor, link)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link, language = 'VO' ))

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
