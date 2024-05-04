# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


LINUX = False
BR = False
BR2 = False

if PY3:
    try:
       import xbmc
       if xbmc.getCondVisibility("system.platform.Linux.RaspberryPi") or xbmc.getCondVisibility("System.Platform.Linux"): LINUX = True
    except: pass

try:
   if LINUX:
       try:
          from lib import balandroresolver2 as balandroresolver
          BR2 = True
       except: pass
   else:
       if PY3:
           from lib import balandroresolver
           BR = true
       else:
          try:
             from lib import balandroresolver2 as balandroresolver
             BR2 = True
          except: pass
except:
   try:
      from lib import balandroresolver2 as balandroresolver
      BR2 = True
   except: pass


host = 'https://www.zona-leros.com/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_zonaleros_proxies', default=''):
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
    if not headers: headers ={'Referer': host}

    hay_proxies = False
    if config.get_setting('channel_zonaleros_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if '?year[]=' in url: raise_weberror = False

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('zonaleros', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

        if not data:
            if not 'search?q=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('ZonaLeros', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('zonaleros', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('zonaleros', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
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
                                from_channel='zonaleros', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_zonaleros', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-hd-online-lat', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series-h', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    if item.search_type == 'movie': url = host + 'peliculas-hd-online-lat'
    else: url = host + 'series-h'

    data = do_downloadpage(url)

    bloque = scrapertools.find_single_match(data, '>Géneros(.*?)</div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
        text_color = 'deepskyblue'
        limit = 1949
    else:
        text_color = 'hotpink'
        limit = 1989

    if item.search_type == 'movie': url_any = host + 'peliculas-hd-online-lat'
    else: url_any = host + 'series-h'

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, limit, -1):
        url = url_any + '?year[]=' + str(x) + '&order=created'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        title = scrapertools.find_single_match(match, 'alt="([^"]+)"').strip()

        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if not title or not url: continue

        title = title.replace('Ver', '').replace('ver', '').replace('Descargar', '').replace('descargar', '').replace('&#039;', "'").strip()

        thumb = scrapertools.find_single_match(match, 'src="([^"]+)"')

        tipo = 'movie' if '/peliculas/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<li class="page-item active">' in data:
            next_page = scrapertools.find_single_match(data, '<li class="page-item active">.*?<a class="page-link" href="(.*?)"')

            if next_page:
                if '?page=' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<li id="select-temp-(.*?)"')

    for nro_season in matches:
        title = 'Temporada ' + nro_season

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = nro_season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = nro_season, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    season = scrapertools.find_single_match(data, '<div id="temp-' + str(item.contentSeason) + '"(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(season, '<a href="(.*?)".*?<img src="(.*?)".*?alt="(.*?)".*?<span class="Capi">(.*?)</span>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('ZonaLeros', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZonaLeros', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZonaLeros', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZonaLeros', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ZonaLeros', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('ZonaLeros', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, thumb, title, epis in matches[item.page * item.perpage:]:
        title = title.replace('Ver', '').replace('ver', '').replace('&#039;', "'").strip()

        nro_epi = scrapertools.find_single_match(epis, 'x(.*?)$')

        titulo = str(item.contentSeason) + 'x' + nro_epi + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = nro_epi ))

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

    ses = 0

    if item.contentEpisodeNumber:
        srvs = scrapertools.find_multiple_matches(data, 'data-id="(.*?)".*?title="(.*?)"')

        datar = data.replace('[', '="').replace(']', '"')

        for srv, title in srvs:
            link = scrapertools.find_multiple_matches(str(datar), 'video="' + srv + '".*?<iframe src="(.*?)"')

            if link:
                title = title.lower().strip()

                servidor = servertools.corregir_servidor(title)

                if title == 'googledrive': servidor = 'gvideo'
                elif title == 'hd1' or title == 'hd2': servidor = 'various'

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                    if not config.get_setting('developer_mode', default=False): continue

                other = ''
                if servidor == 'various': other = srv.capitalize()

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link, language = 'Lat', other = other ))

        # ~ Downloads de Series
        block = scrapertools.find_single_match(data, '<th>DESCARGAR</th>(.*?)</table>')

        downs = scrapertools.find_multiple_matches(block, '<tr>(.*?)</tr>')

        for down in downs:
            srv = scrapertools.find_single_match(down, '<td>(.*?)</td>')

            srv = srv.lower().strip()

            if srv == 'dropapk': continue
            elif srv == '1fichier': continue

            if srv == 'googledrive': srv = 'gvideo'

            servidor = servertools.corregir_servidor(srv)

            qlty = scrapertools.find_single_match(down, '</td>.*?</td>.*?</td>.*?<td><strong>(.*?)</strong>')

            link = scrapertools.find_single_match(down, 'href="(.*?)"')

            if link:
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link, quality = qlty, language = 'Lat' ))

    else:
        _token = scrapertools.find_single_match(data, '<meta name="csrf-token" content="(.*?)"')

        if not _token: return itemlist

        calidades = scrapertools.find_multiple_matches(data, 'data-target="#calidad-(.*?)"')

        for calidad in calidades:
            ses += 1

            qlty = scrapertools.find_single_match(data, 'data-target="#calidad-' + calidad + '">.*?<span>(.*?)</span>')

            post = {'calidad_id': calidad, '_token': _token}

            data1 = do_downloadpage(host + 'api/calidades', post = post)
            data1 = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data1)

            _ids = scrapertools.find_multiple_matches(data1, '<li id="option.*?data-id="(.*?)"')

            for _id in _ids:
                ses += 1

                srv = scrapertools.find_single_match(data1, 'data-id="' + _id + '".*?title="(.*?)"')

                datar = data1.replace('[', '="').replace(']', '"')

                url = scrapertools.find_single_match(str(datar), ';video.*?="' + _id + '".*?src="(.*?)"')

                if url:
                    srv = srv.lower().strip()

                    servidor = servertools.corregir_servidor(srv)

                    if srv == 'googledrive': servidor = 'gvideo'
                    elif srv == 'hd1' or srv == 'hd2': servidor = 'various'

                    if servertools.is_server_available(servidor):
                        if not servertools.is_server_enabled(servidor): continue
                    else:
                        if not config.get_setting('developer_mode', default=False): continue

                    other = ''
                    if servidor == 'various': other = srv.capitalize()

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, quality = qlty, language = 'Lat', other = other ))

    # ~ Downloads de Pelis tienen recaptcha

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    servidor = item.server

    url = item.url

    url = str(url).replace('[', '').replace(']', '').replace("'", '').strip()


    try:
        if config.get_setting('channel_zonaleros_proxies', default=''):
            new_url = httptools.downloadpage_proxy('zonaleros', url, follow_redirects=False).headers['location']
        else:
            new_url = httptools.downloadpage(url, follow_redirects=False).headers['location']
    except:
        new_url = ''

    if new_url:
        try:
            if '.zpaste.' in new_url:
                if config.get_setting('channel_zonaleros_proxies', default=''):
                   new_url = httptools.downloadpage_proxy('zonaleros', new_url, follow_redirects=False).headers['location']
                else:
                   new_url = httptools.downloadpage(new_url, follow_redirects=False).headers['location']
        except:
            new_url = ''

    if new_url:
        url = new_url

        servidor = servertools.get_server_from_url(new_url)
        servidor = servertools.corregir_servidor(servidor)

    if servidor == 'directo': url = ''

    elif 'zona-leros.com' in url: url = ''
    elif '.zpaste.' in url: url = ''

    if url:
        if servidor == 'zplayer': url = url + '|' + host

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

