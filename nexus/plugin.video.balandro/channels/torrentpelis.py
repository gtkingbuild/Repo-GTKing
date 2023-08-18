# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://torrentpelis.org/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://torrentpelis.com/', 'https://www1.torrentpelis.com/', 'https://www2.torrentpelis.com/']


domain = config.get_setting('dominio', 'torrentpelis', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'torrentpelis')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'torrentpelis')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_torrentpelis_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar[/B] ...', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

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

    timeout = None
    if host in url:
        if config.get_setting('channel_torrentpelis_proxies', default=''): timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        data = httptools.downloadpage_proxy('torrentpelis', url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '?s=' in url:
                platformtools.dialog_notification('TorrentPelis', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')
                data = httptools.downloadpage_proxy('torrentpelis', url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage_proxy('torrentpelis', url, post=post, headers=headers, timeout=timeout).data
        except:
            pass

    if '<title>Just a moment...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'torrentpelis', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_torrentpelis', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='torrentpelis', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_torrentpelis', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_torrentpelis', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Tendencias', action = 'list_all', url = host + 'tendencias/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'genero/netflix/', search_type = 'movie', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'GENEROS</a>(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if 'Añadido recientemente' in data:
        bloque = scrapertools.find_single_match(data, 'Añadido recientemente(.*?)<div class="sidebar')
    else:
        bloque = scrapertools.find_single_match(data, 'Peliculas Torrent(.*?)<div class="sidebar')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#038;', '')

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="imdb">.*?<span>(.*?)</span>')
        if not year: year = '-'

        plot = scrapertools.find_single_match(match, '<div class="texto">(.*?)</div>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
           next_url = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

           if next_url:
               if '/page/' in next_url:
                   itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'Dual-LAT': 'Lat (dual)', 'Español latino': 'Lat', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    link = scrapertools.find_single_match(data, "id='link-.*?<a href='(.*?)'")
    if not link: link = scrapertools.find_single_match(data, 'id="link-.*?<a href="(.*?)"')

    links = scrapertools.find_multiple_matches(data, "<tr id='link-.*?href='(.*?)'.*?<strong class='quality'>(.*?)</strong>.*?src='(.*?)'.*?<strong class='quality'>(.*?)</strong>")
    if not links: links = scrapertools.find_multiple_matches(data, '<tr id="link-.*?href="(.*?)".*?<strong class="quality">(.*?)</strong>.*?src="(.*?)".*?<strong class="quality">(.*?)</strong>')

    linksd =  scrapertools.find_multiple_matches(data, "<tr class='downloads'.*?id='.*?<a href='(.*?)'.*?<strong class='quality'>(.*?)</strong>.*?src='(.*?)'.*?<strong class='quality'>(.*?)</strong>")
    if not linksd: linksd =  scrapertools.find_multiple_matches(data, '<tr class="downloads".*?id=".*?<a href="(.*?)".*?<strong class="quality">(.*?)</strong>.*?src="(.*?)".*?<strong class="quality">(.*?)</strong>')

    links = links + linksd

    for url, qlty, lang, size in links:
        if url == 'https://adfly.mobi/directlinkg': url = link

        if '.png' in lang:
            if 'Espanol' in lang: lang = 'Castellano'
            elif 'Latino' in lang: lang = 'Latino'
            elif 'Vose' in lang: lang = 'Subtitulado'
            else: lamg = '?'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = IDIOMAS.get(lang, lang), quality = qlty, other = size))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    urlb64 = scrapertools.find_single_match(url, "urlb64=(.*?)$")

    if urlb64:
        urlb64 = base64.b64decode(urlb64).decode('utf-8')

        if '/enlaces/' in urlb64:
            if not urlb64.startswith(host):
                resp = httptools.downloadpage(urlb64, follow_redirects=False, only_headers=True)
            else:
                resp = httptools.downloadpage_proxy('torrentpelis', urlb64, follow_redirects=False, only_headers=True)

            if 'location' in resp.headers: url = resp.headers['location']
        else:
            data = do_downloadpage(urlb64)
            url = scrapertools.find_single_match(data, '<a id="link".*?href="(.*?)"')

    elif '/enlaces/' in url:
        if not url.startswith(host):
            resp = httptools.downloadpage(url, follow_redirects=False, only_headers=True)
        else:
            resp = httptools.downloadpage_proxy('torrentpelis', url, follow_redirects=False, only_headers=True)

        if 'location' in resp.headers: url = resp.headers['location']

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith(".torrent"):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    else:
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(url, host_torrent)

        if url_base64.startswith('magnet:'):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

        elif url_base64.endswith(".torrent"):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h1>Resultados encontrados(.*?)<h3>')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_search(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
