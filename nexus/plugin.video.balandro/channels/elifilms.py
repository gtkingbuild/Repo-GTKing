# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://allcalidad.ms/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://elifilms.net/', 'https://elifilms.org/', 'https://allcalidad.si/']


domain = config.get_setting('dominio', 'elifilms', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'elifilms')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'elifilms')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_elifilms_proxies', default=''):
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
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    raise_weberror = False if '/year/' in url else True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        data = httptools.downloadpage_proxy('elifilms', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'elifilms', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_elifilms', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='elifilms', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_elifilms', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    itemlist.append(item.clone( title = 'En 4K UHD', action = 'list_all', url = host + '4k-peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Genero<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1993, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'year/' + str(x) + '/', action='list_all', any = str(x), text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<div class="short_header">(.*?)</div>').strip()

        if not url or not title: continue

        if '-1-ano' in url: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = '-'
        if item.any: year = item.any

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('#038;', '')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, 'class="page-numbers current">.*?href="(.*?)"')

        if next_url:
            if '/page/' in next_url:
               itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<ul class="server-list">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'data-id="(.*?)">(.*?)</a>')

    ses = 0

    for dvid, srv in matches:
        ses += 1

        srv = srv.replace('.com', '').replace('.co', '').replace('.live', '').replace('.nz', '').replace('.to', '').replace('v2.', '').replace('.ru', '').replace('.sx', '').lower().strip()

        if 'trailer' in srv: continue

        elif 'hqq' in srv or 'waaw' in srv or 'netu' in srv: continue
        elif 'embed.mystream' in srv: continue

        elif srv == 'vip': continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', dvid = dvid, language = 'Lat', other = srv.capitalize() ))

    # Descarga y Torrents
    bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')

    matches = scrapertools.find_multiple_matches(bloque, 'data-href="(.*?)".*?<img src=.*?/dw/(.*?).png".*?<td>(.*?)</td>.*?<span>(.*?)</span>')

    for dvid, srv, lng, qlty in matches:
        ses += 1

        srv = srv.lower()

        lng = lng.replace('Latino', 'Lat').strip()

        if not lng: lng = 'Lat'

        if servertools.is_server_available(srv):
            if not servertools.is_server_enabled(srv): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', dvid = dvid, quality = qlty, language = lng, other = srv.capitalize() ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = base64.b64decode(item.dvid).decode("utf-8")

    if item.other.lower() == 'torrent':
        itemlist.append(item.clone( url = url, server = 'torrent' ))

        return itemlist

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'zplayer': url = url + '|' + host

        itemlist.append(item.clone(server = servidor, url = url))

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

