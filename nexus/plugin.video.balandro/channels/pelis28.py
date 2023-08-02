# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://pelis28.art/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://pelis28.vip/', 'https://pelis28.lol/', 'https://pelis28.app/',
             'https://ww3.pelis28.app/', 'https://ww1.pelis28.app/']


domain = config.get_setting('dominio', 'pelis28', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'pelis28')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'pelis28')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_pelis28_proxies', default=''):
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
    for ant in ant_hosts:
        url = url.replace(ant, host)

    if '/?s=' in url: headers = {'Referer': host}

    if '/fecha-estreno/' in url: raise_weberror = False
    elif '/etiqueta/' in url: raise_weberror = False

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('pelis28', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'pelis28', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_pelis28', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='pelis28', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_pelis28', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    itemlist.append(item.clone( title = 'Estrenos', action = 'news', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Amazon prime video', action = 'list_all', url = host + 'categoria/amazon-prime-video/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'categoria/netflix/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Sagas', action = 'sagas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def news(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    url = scrapertools.find_single_match(data, '<a href="(.*?)">⭐ ESTRENOS</a>')

    if url:
        item.url = url

        return list_all(item)

    return itemlist


def sagas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'SAGAS(.*?)</ul>')
    matches = scrapertools.find_multiple_matches(bloque, '<li id="menu-item-.*?<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque1 = scrapertools.find_single_match(data, '<ul id="menu-menu"(.*?)</ul>')
    matches1 = scrapertools.find_multiple_matches(bloque1, '<li id="menu-item-.*?<a href="(.*?)">(.*?)</a>')

    bloque2 = scrapertools.find_single_match(data, 'PELIS28</a>(.*?)</ul>')
    matches2 = scrapertools.find_multiple_matches(bloque2, '<li id="menu-item-.*?<a href="(.*?)">(.*?)</a>')

    matches = matches1 + matches2

    for url, title in matches:
        if 'ESTRENOS' in title: continue
        elif 'GÉNEROS' in title: continue
        elif 'Netflix' in title: continue
        elif 'Amazon Prime Video' in title: continue
        elif 'Próximos Estrenos' in title: continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1969, -1):
        url = host + 'ver-pelicula/fecha-estreno/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'id="mt-(.*?)</div><div')
    if not matches: matches = scrapertools.find_multiple_matches(data, 'id="mt-(.*?)</div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        if title.startswith('Ver '): title = title.replace('Ver ', '').strip()

        if '[' in title:
            title = title.replace('[', '{').replace(']', '}')
            title = scrapertools.find_single_match(title, '(.*?){').strip()

        qlty = scrapertools.find_single_match(match, '<span class="calidad2">(.*?)</span>')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        thumb = scrapertools.find_single_match(match, '<noscript>.*?<img style=".*?src="(.*?)"')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=(qlty),
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)"')
        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    _id = scrapertools.find_single_match(data, '<div class="movieplay">.*?data-lazy-src="(.*?)"')
    if not _id: _id = scrapertools.find_single_match(data, '<div class="movieplay">.*?src="(.*?)"')

    if not _id: return itemlist

    if _id.startswith('//'):
        _id = 'https:' + _id

        servidor = servertools.get_server_from_url(_id)
        servidor = servertools.corregir_servidor(servidor)

        _id = servertools.normalize_url(servidor, _id)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', url = _id, server = servidor, title = '', language = '?' ))
            return itemlist

    headers = {'Referer': host}

    data = do_downloadpage(_id, headers = headers)

    matches = scrapertools.find_multiple_matches(data, '<li onclick="go_to_player(.*?)</li>')

    ses = 0

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, "'(.*?)'")
        if not url: continue

        if url.startswith('//'): url = 'https:' + url

        lang = scrapertools.find_single_match(match, '<p>(.*?)</p>').strip()

        if 'latino' in lang.lower(): lang = 'Lat'
        elif 'espanol' in lang.lower() or 'español' in lang.lower(): lang = 'Esp'
        elif 'subtitulado' in lang.lower() or 'vose' in lang.lower(): lang = 'Vose'
        else: '?'

        servidor = scrapertools.find_single_match(match, '<span>(.*?)</span>').lower()

        if 'hqq' in servidor or 'waaw' in servidor or 'netu' in servidor: continue
        elif servidor == 'powvideo' or servidor == 'pouvideo' or servidor == 'powvibeo' or servidor == 'povvldeo': continue

        elif servidor == 'stemplay': continue
        elif servidor == 'streamango': continue
        elif servidor == 'servidor vip': continue
        elif servidor == 'pelis': continue

        other = ''

        if servidor == 'dood': servidor = 'doodstream'
        elif servidor == 'suzihaza': servidor = 'fembed'
        elif servidor == 'vanfem': servidor = 'fembed'
        elif servidor == 'ok': servidor = 'okru'

        elif servidor == 'app':
             servidor = 'directo'
             other = 'App'

        elif 'damedamehoy' in servidor or 'tomatomatela' in servidor:
             servidor = 'directo'
             other = 'Dame'

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def resuelve_dame_toma(dame_url):
    data = do_downloadpage(dame_url)

    url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
    if not url:
        checkUrl = dame_url.replace('embed.html#', 'details.php?v=')
        data = do_downloadpage(checkUrl, headers={'Referer': dame_url})
        url = scrapertools.find_single_match(data, '"file":\s*"([^"]+)').replace('\\/', '/')

    return url


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.other == 'App':
            b64_url = base64.b64decode(item.url)

            if b64_url:
                if 'https://apialfa.tomatomatela.com/ir/player.php' in str(b64_url):
                    if "b'" in str(b64_url): b64_url = str(b64_url).replace("b'", '').replace("'", '')

                    h = scrapertools.find_single_match(str(b64_url), 'h=(.*?)$')

                    if h:
                        post = {'url': h}

                        resp = httptools.downloadpage('https://api.cuevana3.me/ir/redirect_ddh.php', post = post, follow_redirects=False, only_headers=True)

                        try: url = resp.headers['location']
                        except: url = ''

    if '?h=' in item.url:
        h =  scrapertools.find_single_match(item.url, '.*?h=(.*?)$')
        post = {'h': h}

        resp = httptools.downloadpage('https://pelis28.click/sc/r.php', post = post, follow_redirects=False, only_headers=True)

        try: url = resp.headers['location']
        except: url = ''

    if '//damedamehoy.' in url or '//tomatomatela.' in url: url = resuelve_dame_toma(url)

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

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

