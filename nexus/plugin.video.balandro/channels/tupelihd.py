# -*- coding: utf-8 -*-

import re

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.pelitorrent.com/'


IDIOMAS = {'Español': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose'}


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_tupelihd_proxies', default=''):
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
    ant_hosts = ['https://www.tupelihd.com/', 'https://senininternetin.com/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    raise_weberror = True
    if '/peliculas/estrenos-' in url: raise_weberror = False

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        data = httptools.downloadpage_proxy('tupelihd', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='tupelihd', folder=False, text_color='chartreuse' ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'torrents-peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'estrenos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'movie' ))

    return itemlist


def estrenos(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 2017, -1):
        itemlist.append(item.clone( title = 'Estrenos ' + str(x), action = 'list_all', url = host + 'peliculas/estrenos-' + str(x) +'/', text_color='moccasin' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En 4K UHD Micro', action = 'list_all', url = host + 'peliculas/4k-uhdmicro/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 4K UHD Remux', action = 'list_all', url = host + 'peliculas/4k-uhdremux/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 4K UHD Rip', action = 'list_all', url = host + 'peliculas/4k-uhdrip/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 4K WEB Rip', action = 'list_all', url = host + 'peliculas/4kwebrip/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En BDremux', action = 'list_all', url = host + 'peliculas/bdremux/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En Bluray 1080p', action = 'list_all', url = host + 'peliculas/bluray-1080p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En Bluray MicroHD', action = 'list_all', url = host + 'peliculas/bluray-microhd/', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'Generos</span></a>\s*<ul class="sub-menu">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"><i[^>]*></i><span>([^<]+)')
    for url, title in matches:
        title = title.replace('&amp;', '&')

        if '/estrenos/' in url: continue

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'release/' + str(x) + '/', action='list_all', text_color = 'deepskyblue' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        letras = letra.lower()
        if letras == '#': letras = '0-9'

        url = host + 'letters/' + letras + '/'

        itemlist.append(item.clone( action = 'list_all', title = letra, url = url, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)<h3')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')

        title = scrapertools.find_single_match(article, '<div class="Title">(.*?)</div>')
        if not title: title = scrapertools.find_single_match(article, '<h2 class=.*?>(.*?)</h2>')

        if not url or not title: continue

        if '/series/' in url: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = '-'

        qlty_lang = scrapertools.find_single_match(article, '<span class="calidad">(.*?)</span')
        if '|' in qlty_lang:
            qlty = qlty_lang.split('|')[0].strip()
            lang = qlty_lang.split('|')[1].strip()
        else:
            qlty = qlty_lang
            lang = ''

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, languages=IDIOMAS.get(lang, lang),
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '>SIGUIENTE<' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?<a class="page-link".*?href="(.*?)"')

            if next_page:
               itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()

    orden = [
          'cam',
          'camrip',
          'hdcam',
          'webscreener',
          'tsscreener',
          'hdtcscreener',
          'brscreener',
          'hdtv',
          'hdtv720p',
          'microhd',
          'dvdrip',
          'blurayrip1080p',
          'bluraymicrohd',
          'blurayrip',
          'bdremux',
          'hdrip',
          'hd720',
          'hd1080',
          '4kwebrip',
          '4kuhdmicro',
          '4kuhdrip',
          '4kuhdremux'
          ]

    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def normalize_server(server):
    server = servertools.corregir_servidor(server)

    server = server.replace('.com', '').replace('.net', '').replace('.to', '')

    if server == 'uploaded': return 'uploadedto'

    return server


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<section class="section player(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, ' href="#options-(.*?)".*?class="server">(.*?)</span>')

    ses = 0

    # enlaces
    for opt, server_idioma in matches:
        ses += 1

        s_i = scrapertools.find_single_match(server_idioma, '(.*?)-(.*?)$')
        if not s_i: continue

        servidor = s_i[0].strip().lower()
        if not servidor: continue
        elif servidor == 'youtube': continue

        lang = s_i[1].strip()

        url = scrapertools.find_single_match(bloque, '<div id="options-' + opt + '.*?<iframe src="(.*?)"')
        if not url: url = scrapertools.find_single_match(bloque, '<div id="options-' + opt + '.*?<iframe data-src="(.*?)"')

        if not url: continue

        servidor = normalize_server(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = 'e', language = IDIOMAS.get(lang, lang) ))

    # ~ descargas
    if '>Descargar Torrent<' in data:
        bloque = scrapertools.find_single_match(data, '<table>(.*?)</table>')

        matches = re.compile('<td><span class="num">(.*?)</tr>', re.DOTALL).findall(bloque)

        for match in matches:
            ses += 1

            url = scrapertools.find_single_match(match, ' href="([^"]+)"')
            if url.startswith('//'): url = 'https:' + url

            if not url: continue

            servidor = scrapertools.find_single_match(match, 'class=".*?">(.*?)</a>').strip()

            if not servidor: continue

            lang = scrapertools.find_single_match(match, '</td>.*?<td>(.*?)</td>').strip()
            qlty = scrapertools.find_single_match(match, '<td><span>(.*?)</span>').strip()

            other = ''

            if servidor.lower() != 'torrent': other = 't'

            if servidor:
                servidor = normalize_server(servidor)

                if servertools.is_server_available(servidor):
                   if not servertools.is_server_enabled(servidor): continue
                else:
                   if not config.get_setting('developer_mode', default=False): continue

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = other,
                                  language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&').replace(' class=', '')

    url = ''

    if item.other:
        if not item.url.startswith == host: return itemlist

    if item.server == 'torrent':
        itemlist.append(item.clone( url = item.url, server = 'torrent' ))
        return itemlist

    elif item.other == 't':
        if not item.url.startswith(host):
            url = httptools.downloadpage(item.url, only_headers = True, follow_redirects = False).headers.get('location')
        else:
            url = httptools.downloadpage_proxy('tupelihd', item.url, only_headers = True, follow_redirects = False).headers.get('location')

        if url:
            if url.endswith('.torrent'):
               itemlist.append(item.clone( url = url, server = 'torrent' ))
               return itemlist

    else:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')

    if url:
       if item.server == 'torrent':
            itemlist.append(item.clone(url = url, server = item.server))
       else:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor and servidor != 'directo':
                url = servertools.normalize_url(servidor, url)

                itemlist.append(item.clone( url = url, server = servidor ))

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
