# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import re, os

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


# ~ series solo hay 11

host = 'https://pelisyseries.net/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_pelisyseries_proxies', default=''):
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
    if '/lanzamiento/' in url: raise_weberror = False

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        data = httptools.downloadpage_proxy('pelisyseries', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                else:
                    data = httptools.downloadpage_proxy('pelisyseries', url, post=post, headers=headers, raise_weberror=raise_weberror).data
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
                                from_channel='pelisyseries', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_pelisyseries', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    return mainlist_pelis(item)

    # ~ itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    # ~ itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    # ~ itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    # ~ itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=movies', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ratings/?get=movies', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=tv', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ratings/?get=tv', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '4K 2160p', action = 'list_all', url = host + 'calidad/4k-2160p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'HD 1080p', action = 'list_all', url = host + 'calidad/hd-1080p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'HD 720p', action = 'list_all', url = host + 'calidad/hd-720p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'HD Rip', action = 'list_all', url = host + 'calidad/hd-rip/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'DVD Rip', action = 'list_all', url = host + 'calidad/dvd-rip/', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'Género</a>(.*?)País</a>')

    patron = '<li id="menu-item-\d+" class="menu-item menu-item-type-taxonomy menu-item-object-genres menu-item-\d+"><a href="([^"]+)">([^<]+)'

    matches = re.compile(patron).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url, text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1970, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'lanzamiento/' + str(x) + '/', action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'País</a>(.*?)$')

    patron = '<li id="menu-item-\d+" class="menu-item menu-item-type-taxonomy menu-item-object-genres menu-item-\d+"><a href="([^"]+)">([^<]+)'

    matches = re.compile(patron).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url, text_color='moccasin' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque =  scrapertools.find_single_match(data, '>Networks</a>(.*?)>TENDENCIAS<')
    matches = re.compile('<li id="menu-item-.*?<a href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = 'hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '<h1>' in data: bloque = scrapertools.find_single_match(data, '</h1>(.*?)>Año de lanzamiento<')
    elif '<h2>' in data: bloque = scrapertools.find_single_match(data, '</h2>(.*?)>Año de lanzamiento<')
    else: bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#038;', '&')

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '</h3><span>(.*?)</span>').strip()
        if not year: year = '-'
        else: title = title.replace('(' + year + ')', '').strip()

        qlty = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>')

        if '/peliculas/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<span class="current">' + ".*?<a href='(.*?)'")

        if next_url:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile("<span class='se-t.*?'>(.*?)</span>", re.DOTALL).findall(data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = tempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '/seasons/' in item.url: bloque = data
    else: bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + "</span>(.*?)</div></div>")

    patron = "<li class='mark-.*?src='(.*?)'.*?<div class='numerando'>(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>"

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Cuevana3mu', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisySeries', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisySeries', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisySeries', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PelisySeries', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for thumb, s_e, url, title in matches[item.page * item.perpage:]:
        episode = scrapertools.find_single_match(s_e, ".*? - (.*?)$")

        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, "<div id='playeroptions'(.*?)</div></div>")

    matches = scrapertools.find_multiple_matches(bloque, "<li id='player-option-(.*?)</li>")

    ses = 0

    # Players
    for match in matches:
        ses += 1

        dpost = scrapertools.find_single_match(match, "data-post='(.*?)'")
        dtype = scrapertools.find_single_match(match, "data-type='(.*?)'")
        dnume = scrapertools.find_single_match(match, "data-nume='(.*?)'")

        if not dpost or not dtype or not dnume: continue

        lang = scrapertools.find_single_match(match, "<span class='title'>(.*?)</span>")

        if 'Latino' in lang: lang = 'Lat'
        elif 'Castellano' in lang or 'Español' in lang: lang = 'Esp'
        elif 'Subtitulado' in lang or 'VOSE' in lang: lang = 'Vose'
        else: lang = '?'

        srv = scrapertools.find_single_match(match, "<span class='server'>(.*?)</span>")

        other = normalize_server(srv)

        if not other: continue

        if 'youtube' in other: continue

        elif other == 'ok': other = 'okru'
        elif other == 'feurl' or 'fembad' in other: other = 'fembed'
        elif other == 'dood': other = 'doodstream'
        elif other == 'uptostream': other = 'uptobox'
        elif other == 'archive': other = 'archiveorg'
        elif other == 'zto': other = 'zembed'
        elif other == 'player.vimeo': other = 'vimeo'

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', dpost = dpost, dtype = dtype, dnume = dnume,
                                                      language = lang, quality = item.qualities, other = other.capitalize() ))

    # Descargas y Torrents
    matches = scrapertools.find_multiple_matches(data, "<tr id='link-(.*?)</tr>")

    for match in matches:
        ses += 1

        srv = scrapertools.find_single_match(match, ".*?domain=(.*?)'")

        srv = normalize_server(srv)

        if not srv: continue

        servidor = srv

        size = ''

        if servidor == 'ok': servidor = 'okru'
        elif servidor == 'feurl' or 'fembad' in servidor: servidor = 'fembed'
        elif servidor == 'dood': servidor = 'doodstream'
        elif servidor == 'uptostream': servidor = 'uptobox'
        elif servidor == 'archive': servidor = 'archiveorg'
        elif servidor == 'zto': servidor = 'zembed'
        elif servidor == 'player.vimeo': servidor = 'vimeo'

        elif servidor == 'utorrent':
            servidor = 'torrent'
            size = scrapertools.find_single_match(match, "</strong>.*?</td><td>.*?</td><td>(.*?)</td>")

        qlty = scrapertools.find_single_match(match, "<strong class='quality'>(.*?)</strong>")

        if qlty == 'Subtitulos': continue

        lang = scrapertools.find_single_match(match, "</strong>.*?</td><td>(.*?)</td>")

        if 'Latino' in lang: lang = 'Lat'
        elif 'Castellano' in lang or 'Español' in lang: lang = 'Esp'
        elif 'Subtitulado' in lang or 'VOSE' in lang: lang = 'Vose'
        else: lang = '?'

        url = scrapertools.find_single_match(match, "<a href='(.*?)'")

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = lang, quality = qlty, other = size ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def normalize_server(server):
    server = server.lower()

    server = server.replace('.com', '').replace('.co', '').replace('.cc', '').replace('.ru', '').replace('.tv', '').replace('.to', '').replace('.me', '').replace('.nz', '').replace('.vg', '')
    server = server.replace('.org', '').replace('.net', '').replace('.club', '').replace('.site', '').replace('.watch', '').strip()

    if 'waaw' in server or 'hqq' in server or 'netu' in server: server = ''

    elif 'pelisyseries' in server: server = ''

    elif 'hydrax' in server: server = ''
    elif 'videohost' in server: server = ''
    elif 'embed.mystream' in server: server = ''
    elif 'storage.googleapis' in server: server = ''
    elif 'goo.gl' in server: server = ''
    elif 'jwplayerembed' in server: server = ''
    elif 'vev.io' in server: server = ''
    elif 'pelispng.online' in server: server = ''
    elif 'verlapeliculaonline28.blogspot' in server: server = ''

    elif 'upstream.to' in server:
           server = server.replace('.to', '').strip()
           if '.' in server:
               server = scrapertools.find_single_match(other, "s.*?.(.*?)$")
               server = server.replace('.', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '').strip()

    elif 'viduplayer' in server: server = ''
    elif server == 'ul': server = ''

    if server:
        server = servertools.corregir_servidor(server)

        if not server == 'desconocido':
            if servertools.is_server_available(server):
                if not servertools.is_server_enabled(server): server = ''
            else:
               if not config.get_setting('developer_mode', default=False): server = ''

    return server


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.dpost:
        post = {'action': 'doo_player_ajax', 'post': item.dpost, 'nume': item.dnume, 'type': 'movie'}

        data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

        url = scrapertools.find_single_match(data, "src='(.*?)'")
        if not url: url = scrapertools.find_single_match(data, 'src=.*?"(.*?)"')
        if not url: url = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        url = url.replace('\\/', '/')

        if '/?source=' in url: url = scrapertools.find_single_match(data, '/?source=(.*?)"')

        if '/www.tokyvideo.com/' in url:
            data = do_downloadpage(url)

            url = scrapertools.find_single_match(data, '<source src="(.*?)"')

            if url:
                itemlist.append(item.clone(server = 'directo', url = url))

                return itemlist

    elif item.server:
        data = do_downloadpage(url)

        url = scrapertools.find_single_match(data, '<a id="link".*?href="(.*?)"')

        url = url.replace('&#038;', '&').replace('&amp;', '&')

        if item.server == 'upstream':
            if 'dl?op=download_orig' in url:
                return 'Upstream download [COLOR tan]No soportado[/COLOR]'

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        if url.endswith('.torrent'):
            if PY3:
                if config.get_setting('channel_pelisyseries_proxies', default=''):
                    from core import requeststools
                    data = requeststools.read(url, 'pelisyseries')
                else:
                    data = do_downloadpage(url)
            else:
                data = do_downloadpage(url)

            if data:
                if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
                    return 'Archivo [COLOR red]Inexistente[/COLOR]'

                file_local = os.path.join(config.get_data_path(), "temp.torrent")
                with open(file_local, 'wb') as f: f.write(data); f.close()

                itemlist.append(item.clone( url = file_local, server = 'torrent' ))

            return itemlist

        if 'archive.org' in url: url = url.replace('https%3A%2F%2Farchive.org%2Fdownload%2F', 'https://archive.org/download/').replace('%2F', '/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if not servidor == 'directo':
            itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)>Año de lanzamiento<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#038;', '&')

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'
        else: title = title.replace('(' + year + ')', '').strip()

        langs = []
        lngs = scrapertools.find_multiple_matches(match, '.*?/flags/(.*?).png')

        if 'es' in lngs: langs.append('Esp')
        if 'mx' in lngs: langs.append('Lat')
        if 'en' in lngs: langs.append('Vose')

        plot = scrapertools.htmlclean(scrapertools.find_single_match(match, '<p>(.*?)</p>'))

        tipo = 'movie' if '/peliculas/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=', '.join(langs), fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year, 'plot': plot} ))

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

