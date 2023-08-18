# -*- coding: utf-8 -*-

import codecs

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://pelisforte.nu/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_pelisforte_proxies', default=''):
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


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://pelisforte.co/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if '/release/' in url: raise_weberror = False

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        data = httptools.downloadpage_proxy('pelisforte', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                else:
                    data = httptools.downloadpage_proxy('pelisforte', url, post=post, headers=headers, raise_weberror=raise_weberror).data
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

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='pelisforte', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_pelisforte', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ultimas-peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + 'sg/marvel-mcu/', search_type = 'movie', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'pelis/idiomas/castellano/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'pelis/idiomas/espanol-latino/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'pelis/idiomas/subtituladas/', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'ultimas-peliculas/')

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<a href=(.*?)>(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    url = host + 'release/'

    for x in range(current_year, 1939, -1):
         itemlist.append(item.clone( title=str(x), url = url + str(x), action='list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)>TOP<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        if not url: url = scrapertools.find_single_match(match, '<a href=(.*?) ').strip()

        title = scrapertools.find_single_match(match, 'class="entry-title">(.*?)</')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="Year">(.*?)</span>')
        if not year:  year ='-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '>SIGUIENTE' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?<a class="page-link" .*?href="(.*?)"')
            if not next_page: next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?<a class=page-link.*?href=(.*?)>')

            if next_page:
                next_page = next_page.replace('&#038;', '&')

                if '/page/' in next_page:
                    itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral'))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>OPCIONES<(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, 'href="#options-(.*?)">.*?<span class="server">(.*?)-(.*?)</span>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, 'href=#options-(.*?)>.*?<span class=server>(.*?)-(.*?)</span>')

    ses = 0

    for opt, srv, idioma in matches:
        ses += 1

        srv = srv.lower().strip()

        if not srv: continue
        elif srv == 'trailer': continue

        if '+ veloz' in srv: continue

        idioma = idioma.strip()

        if 'Latino' in idioma: lang = 'Lat'
        elif 'Castellano' in idioma: lang = 'Esp'
        elif 'Subtitulado' in idioma: lang = 'Vose'
        else: lang = idioma

        url = scrapertools.find_single_match(data, '<div id="options-' + opt + '".*?src="([^"]+)"')
        if not url: url = scrapertools.find_single_match(data, '<div id=options-' + opt + '.*?<iframe data-src="(.*?)"')

        if url:
            servidor = 'directo'
            other = srv

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = other.capitalize(), language = lang ))

    # ~ descargas recaptcha

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    url = item.url

    if item.other:
        if '/mp4.nu/' in url:
            new_url = url.replace('/mp4.nu/', '/mp4.nu/r.php')

            if not new_url.startswith(host):
                resp = httptools.downloadpage(new_url, headers={'Referer': host}, follow_redirects=False, only_headers=True)
            else:
                resp = httptools.downloadpage_proxy('pelisforte', new_url, headers={'Referer': host}, follow_redirects=False, only_headers=True)

            if 'location' in resp.headers: url = resp.headers['location']
            else: url = ''

            if url:
                if '/rehd.net/' in url:
                    data = do_downloadpage(url)
                    url = scrapertools.find_single_match(data, '"url": "(.*?)"')

                if '/hqq.' in url or '/waaw.' in url or '/netu.' in url or 'gounlimited' in url:
                    return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'
                elif '/guayhd.me/' in url:
                    return 'Servidor [COLOR plum]No Soportado[/COLOR]'
                elif '/playpf.link/' in url:
                    return 'Servidor [COLOR plum]No Soportado[/COLOR]'
                elif '/vgfplay.' in url:
                    return 'Servidor [COLOR plum]No Soportado[/COLOR]'

                if '/wtfsb.link/' in url:
                    url = url.replace('/wtfsb.link/', '/streamsb.net/')

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                itemlist.append(item.clone(server = servidor, url = url))
                return itemlist

        headers = {'Referer': host}
        data = do_downloadpage(url, headers = headers)

        url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, '<IFRAME SRC="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, 'src=(.*?) ').strip()

        if 'trhide' in url:
            try:
               new_url = scrapertools.find_single_match(url, 'tid=([A-z0-9]+)')[::-1]
               new_url = codecs.decode(new_url, 'hex')

               headers = {'Referer': item.url}
               data = do_downloadpage(new_url, headers = headers)

               if 'grecaptcha.execute' in data:
                   return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

               url = new_url
            except:
               pass

        elif url.startswith(host):
            if url.endswith('&'):
                url = url + '='
                url = url.replace('&=', '')

            headers = {'Referer': item.url}
            data = do_downloadpage(url, headers = headers)

            url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')
            if not url: url = scrapertools.find_single_match(data, '<IFRAME SRC="(.*?)"')

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url or 'gounlimited' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

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
