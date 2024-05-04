# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.estrenoscinesaa.com/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_estrenoscinesaa_proxies', default=''):
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


def do_downloadpage(url):
    hay_proxies = False
    if config.get_setting('channel_estrenoscinesaa_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('estrenoscinesaa', url).data
        else:
            data = httptools.downloadpage(url).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='estrenoscinesaa', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    # ~ descartadas series solo hay 22
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'genre/netflix/', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + 'genre/marvel/', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'D.C.', action = 'list_all', url = host + 'genre/d-c/', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Star wars', action = 'list_all', url = host + 'genre/starwars/', search_type = 'movie', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<ul class="genres(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">(.*?)</a>\s*<i>(.*?)</i>')

    for url, title, count in matches:
        title = title.replace('&amp;', '&')

        if '/genre/d-c/' in url: continue
        elif '/genre/marvel/' in url: continue
        elif '/genre/netflix/' in url: continue
        elif '/genre/starwars/' in url: continue
        elif '/sci-fi-fantasy/' in url: continue # son series

        if count: title = '[COLOR deepskyblue]' + title + '[/COLOR] (' + count + ')'
        else: title = '[COLOR deepskyblue]' + title + '[/COLOR]'

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    hasta_data = '<div class="pagination">' if '<div class="pagination">' in data else '<nav class="genres">'

    bloque = scrapertools.find_single_match(data, '<h2>Añadido recientemente(.*?)' + hasta_data)
    if not bloque: bloque = scrapertools.find_single_match(data, '<h2>Añadido recientemente(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, '<article id="post-(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)')
        title = scrapertools.find_single_match(match, ' alt="([^"]+)').strip()

        if not url or not title: continue

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)')

        year = scrapertools.find_single_match(match, '<span>(\d{4})</span>')
        if not year: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(match, '<div class="texto">(.*?)</div>'))

        if '/tvshows/' in url:
           if item.search_type == 'movie': continue

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<span class="current".*?' + "<a href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    ses = 0

    matches = scrapertools.find_multiple_matches(data, "(?i)<div class='pframe'><iframe.*?src=(?:'|\")([^'\"]+)")

    for url in matches:
        ses += 1

        if 'youtube.com' in url: continue

        servidor = servertools.get_server_from_url(url)

        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Esp' ))

    # Descarga
    bloque = scrapertools.find_single_match(data, "<div id='download'(.*?)</table></div></div></div>")

    matches = scrapertools.find_multiple_matches(bloque, "<tr id='link-[^']+'>(.*?)</tr>")

    for enlace in matches:
        ses += 1

        url = scrapertools.find_single_match(enlace, " href='([^']+)")

        servidor = scrapertools.find_single_match(enlace, "domain=(?:www.|dl.|)([^'.]+)")
        servidor = servertools.corregir_servidor(servidor)

        if not url or not servidor: continue

        if servidor == 'qiwi': continue

        quality = 'HD'
        lang = 'Esp'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, quality = quality , other = 'd' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if host in item.url:
        data = do_downloadpage(item.url)
        url = scrapertools.find_single_match(data, '<a id="link".*?href="([^"]+)')

        if url:
            servidor = servertools.get_server_from_url(url)
            if servidor and servidor != 'directo':
                servidor = servertools.corregir_servidor(servidor)
                url = servertools.normalize_url(servidor, url)

                itemlist.append(item.clone( url=url, server=servidor ))

    else:
        servidor = servertools.get_server_from_url(item.url)
        if servidor and servidor != 'directo':
            servidor = servertools.corregir_servidor(servidor)
            url = servertools.normalize_url(servidor, item.url)

            itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article>(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)')
        title = scrapertools.find_single_match(match, ' alt="([^"]+)').strip()

        if not url or not title: continue

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)')

        year = scrapertools.find_single_match(match, '<span class="year">(\d{4})</span>')
        if not year: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(match, '<div class="contenido"><p>(.*?)<p></div>'))

        if '/tvshows/' in url:
           if item.search_type == 'movie': continue

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<span class="current".*?' + "<a href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_search', text_color='coral' ))

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

