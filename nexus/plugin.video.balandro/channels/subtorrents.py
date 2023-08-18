# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import re, os

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://www.subtorrents.eu/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://www.subtorrents.nl/', 'https://www.subtorrents.ch/', 'https://www.subtorrents.nz/',
             'https://www.subtorrents.in/', 'https://www.subtorrents.li/', 'https://www.subtorrents.do/',
             'https://www.subtorrents.re/']


domain = config.get_setting('dominio', 'subtorrents', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'subtorrents')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'subtorrents')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_subtorrents_proxies', default=''):
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

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers).data
    else:
        data = httptools.downloadpage_proxy('subtorrents', url, post=post, headers=headers).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers).data
                else:
                   data = httptools.downloadpage_proxy('subtorrents', url, post=post, headers=headers).data
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

    domain_memo = config.get_setting('dominio', 'subtorrents', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_subtorrents', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='subtorrents', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_subtorrents', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_subtorrents', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', url = host, search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Versión original:', folder=False, text_color='moccasin' ))

    itemlist.append(item.clone( title = ' - Catálogo', action = 'list_all', url = host + 'peliculas-subtituladas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = ' - Estrenos', action = 'list_all', url = host + 'peliculas-subtituladas/?filtro=estrenos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Otros idiomas:', folder=False, text_color='moccasin' ))

    itemlist.append(item.clone( title = ' - Catálogo', action = 'list_all', url = host + 'peliculas-subtituladas/?filtro=audio-latino', search_type = 'movie' ))

    itemlist.append(item.clone( title = ' - Estrenos', action = 'list_all', url = host + 'peliculas-subtituladas/?filtro=estrenos&filtro2=audio-latino', search_type = 'movie', ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_series', url = host + 'series-2/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En DVD', action = 'list_search', url = host + 'calidad/dvd-full/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 3D', action = 'list_search', url = host + 'peliculas-3d/', text_color='moccasin' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    if item.search_type == 'movie': url_letra = host + 'peliculas-subtituladas/?s=letra-'
    else: url_letra = host + 'series-2/?s=letra-'

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        title = letra
        if letra == '#': letra = '0'

        url = url_letra + letra.lower()

        if item.search_type == 'movie':
            itemlist.append(item.clone( action = "list_all", title = title, url = url, text_color = text_color ))
        else:
            itemlist.append(item.clone( action = "list_series", title = title, url = url, text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<td class="vertThseccion">.*?<img src="(.*?)".*?<a href="(.*?)".*?title="(.*?)".*?<td>.*?<td>(.*?)</td>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for lang, url, title, qlty in matches:
        if not url or not title: continue

        title = title.split("(")[0]
        if "3D" in title: title = title.split("3D")[0]

        if lang.endswith("1.png"): lang = "Esp"
        elif lang.endswith("2.png"): lang = "VO"
        elif lang.endswith("4.png"): lang = "Fr"   
        elif lang.endswith("8.png"): lang = "It"
        elif lang.endswith("512.png"): lang = "Lat"
        else: lang = "Vose"

        itemlist.append(item.clone( action='findvideos', url=url, title=title, qualities=qlty, languages=lang, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, "<span class='current'>\d+<\/span><a href='([^']+)'")

        if '/page/' in next_url:
            itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def list_series(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<table class="tablaseries2">(.*?)</table>')

    matches = re.compile('<td>.*?<a href="(.*?)".*?title="(.*?)".*?src="(.*?)"', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    for url, title, thumb in matches:
        if not url or not title: continue

        title = title.split("(")[0]

        if not host in url: url = host + url

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail = thumb, contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, "<span class='current'>.*?<a href='([^']+)'")

        if '/page/' in next_url:
            itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_series', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, r'">Temporada (\d+)<')

    for tempo in sorted(matches):
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = item.url, page = 0, contentType = 'season', contentSeason = int(tempo), text_color = 'tan' ))

    return itemlist    


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<td\s*class="capitulonombre">\s*<img\s*src="([^"]+)"[^>]+><a[^>]*title="[^"]+"'
    patron += '>\s*([^<]*)<\/a>\s*<\/td>\s*<td\s*class="capitulodescarga">\s*<a[^>]*href="([^"]+)"()()()'

    if not scrapertools.find_single_match(data, patron):
        patron = '<td\s*class="capitulonombre">\s*<img\s*src="([^"]+)[^>]+>(?:<a\s*href="[^>]+>)?'
        patron += '(.*?)<\/a>\s*<\/td>\s*<td\s*class="capitulodescarga">\s*<a\s*href="([^"]+)[^>]+>'
        patron += '.*?(?:<td\s*class="capitulofecha">.*?(\d{4})?.*?<\/td>)?'
        patron += '(?:<td\s*class="capitulosubtitulo">\s*<a\s*href="([^"]+)[^>]+>.*?<\/td>)?'

        if not scrapertools.find_single_match(data, patron):
            patron = '<td\s*class="capitulonombre">\s*<img\s*src="([^"]+)[^>]+><a\s*'
            patron += '(?:target="[^"]*"\s*)?href="[^>]*title="([^"]+)">[^<]*<\/a>\s*<\/td>'
            patron += '\s*<td\s*class="capitulodescarga">\s*<a\s*(?:target="[^"]*"\s*)?'
            patron += 'href="([^"]+)"[^>]+>.*?(?:<td\s*class="capitulofecha">.*?(\d{4})?.*?<\/td>)?'
            patron += '.*?(?:<td\s*class="capitulosubtitulo">\s*<a\s*href="([^"]+)[^>]+>.*?<\/td>)?'
            patron += '.*?(?:<td\s*class="capitulodescarga">\s*<a\s*(?:target="[^"]*"\s*)?href="([^"]+)")?'

    i = 0

    matches = re.compile(patron, re.DOTALL).findall(data)

    for lang, title, url, year, sub_tit, url_2 in matches:
        if not title: continue

        if not year: year = '-'

        s_e = scrapertools.get_season_and_episode(title)

        try:
           season = int(s_e.split("x")[0])
           epis = s_e.split("x")[1]
        except:
           i += 1
           season = 0
           epis = i

        if item.contentSeason:
            if not str(item.contentSeason) == str(season): continue

        if not item.contentSerieName in title: title = title + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url=url, title=title,contentSerieName = item.contentSerieName, contentType = 'episode',
                                    contentSeason = season, contentEpisodeNumber = epis, infoLabels={'year': year} ))

    return sorted(itemlist, key=lambda x: x.contentEpisodeNumber)


def findvideos(item):
    logger.info()
    itemlist = []

    if item.contentType == "movie":
        data = do_downloadpage(item.url)
        url_torrent = scrapertools.find_single_match(data, '<a target="_blank".*?href="(.*?)"')
    else:
        url_torrent = item.url

    if url_torrent:
        itemlist.append(Item( channel = item.channel, action='play', title='', url=url_torrent, server='torrent', quality=item.qualityes, language=item.languages))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        item.url = item.url.replace(ant, host)

    if not item.url.endswith('.torrent'):
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(item.url, host_torrent)

        if url_base64.endswith('.torrent'): item.url = url_base64

    if item.url.endswith('.torrent'):
        if config.get_setting('proxies', item.channel, default=''):
            if PY3:
                from core import requeststools
                data = requeststools.read(item.url, 'subtorrents')
            else:
                data = do_downloadpage(item.url)

            if data:
                try:
                   if 'Página no encontrada</title>' in str(data):
                       platformtools.dialog_ok('Subtorrents', '[COLOR yellow]Archivo no encontrado[/COLOR]')
                       return itemlist
                except:
                   pass

                file_local = os.path.join(config.get_data_path(), "temp.torrent")
                with open(file_local, 'wb') as f: f.write(data); f.close()

                itemlist.append(item.clone( url = file_local, server = 'torrent' ))
        else:
            itemlist.append(item.clone( url = item.url, server = 'torrent' ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<table class="searchResult">(.*?)</table>')
    matches = re.compile('<td class="vertThseccion">(.*?)</tr>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="([^"]+)"')
        title = scrapertools.find_single_match(match, 'href=".*?title="([^"]+)"')
        if not url or not title: continue

        year = scrapertools.find_single_match(match, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(match, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(title, '\((\d{4})\)')

        if year:
            title = title.replace('(%s)' % year, '').strip()
        else:
            year = '-'

        title_clean = re.sub('\([^\)]+\)', '', title).strip()

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, fmt_sufijo=sufijo, contentType='movie', contentTitle=title_clean, infoLabels={'year': year} ))
									
        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, fmt_sufijo=sufijo, contentType='tvshow', contentSerieName=title_clean, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<span class='current'>.*?<a href='(.*?)'")

        if next_page:
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