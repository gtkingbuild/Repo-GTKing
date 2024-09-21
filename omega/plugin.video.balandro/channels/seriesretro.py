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


host = 'https://seriesretro.com/'


perpage = 20


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_seriesretro_proxies', default=''):
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
    hay_proxies = False
    if config.get_setting('channel_seriesretro_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('seriesretro', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

        if not data:
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('seriesretro', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
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
                       data = httptools.downloadpage_proxy('seriesretro', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                   else:
                       data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    elif '<title>One moment, please...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection [COLOR plum]Level 2[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='seriesretro', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_seriesretro', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('seriesretro') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'lista-series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host + 'lista-series/episodios-agregados-actualizados/', search_type = 'tvshow', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Animación', action = 'list_all', url = host + 'category/animacion/', search_type = 'tvshow', text_color='greenyellow' ))

    itemlist.append(item.clone( title = 'Live action', action = 'list_all', url = host + 'category/liveaction/', search_type = 'tvshow', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    patron = 'class="menu-item menu-item-type-taxonomy menu-item-object-category.*?<a href="(.*?)">(.*?)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title in matches:
        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( action = "list_all", title = title, url = url, text_color = 'hotpink' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1935, -1):
        itemlist.append(item.clone( title = str(x), url = host + '?s=trfilter&trfilter=1&years%5B%5D=' + str(x), action = 'list_all', text_color = 'hotpink' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        letras = letra.lower()

        url = host + 'letter/' + letras + '/'

        itemlist.append(item.clone( action = 'list_alfa', title = letra, url = url, text_color = 'hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(match, '<h3 class="Title">(.*?)</h3>')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="([^"]+)"')
        if not thumb: thumb = scrapertools.find_single_match(match, '<img src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, '<span class="Year">(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '<span class=Year>(.*?)</span>')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        title = title.replace('&#038;', '&')

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            if '<div class="wp-pagenavi">' in data:
                next_page = scrapertools.find_single_match(data, '<div class="wp-pagenavi">.*?class="page-numbers current".*?href="(.*?)"')

                if next_page:
                    if '/page/' in next_page:
                        itemlist.append(item.clone( action = 'list_all', page = 0, url = next_page, title = 'Siguientes ...', text_color='coral' ))

    return itemlist


def list_alfa(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</tr>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<strong>(.*?)</strong>').strip()
        if not url or not title: continue

        if '/aplicacion-oficial-de-seriesretro-com/' in url: continue

        thumb = scrapertools.find_single_match(match, ' data-src="([^"]+)')

        year = scrapertools.find_single_match(match, '<strong>.*?</td><td>Serie</td><td>(\d{4})</span>')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<article (.*?)</article>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        seas_epis = scrapertools.find_single_match(match, '<span class="ClB">(\d+)x(\d+)</span>')

        if not seas_epis: continue

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)"')
        thumb = 'https:' + thumb

        title = scrapertools.find_single_match(match, '<h3 class="Title">(.*?)</h3>')

        fecha = scrapertools.find_single_match(match, '<span class="Year">(.*?)</span>')

        titulo = seas_epis[0] + 'x' + seas_epis[1] + ' ' + title
        if fecha: titulo = titulo + ' (' + fecha + ')'

        itemlist.append(item.clone( action = 'findvideos', title = titulo, url = url, thumbnail = thumb,
                                    contentType = 'episode', contentSerieName = title, contentSeason = seas_epis[0], contentEpisodeNumber = seas_epis[1] ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="wp-pagenavi">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="wp-pagenavi">.*?class="page-numbers current".*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_epis', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile(' data-tab="(.*?)">Temporada', re.DOTALL).findall(data)

    for tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    season = str(item.contentSeason)

    bloque = scrapertools.find_single_match(data, ' data-tab="' + season + '">.*?<tbody>(.*?)</tbody>' )

    matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?)</tr>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesRetro', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for data_epi in matches[item.page * item.perpage:]:
        title = scrapertools.find_single_match(data_epi, ' alt="Imagen.*?<a href=.*?>(.*?)</a>')
        if not title: title = scrapertools.find_single_match(data_epi, ' alt=.*?Imagen.*?<a href=.*?>(.*?)</a>')

        url = scrapertools.find_single_match(data_epi, '<a href="(.*?)"')

        if not url or not title: continue

        episode = scrapertools.find_single_match(data_epi, '<span class="Num">(.*?)</span>')

        thumb = scrapertools.find_single_match(data_epi, '<img src="([^"]+)"')
        thumb = 'https:' + thumb

        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

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

    matches = scrapertools.find_multiple_matches(data, 'data-tplayernv="Opt(.*?)"><span>(.*?)</span>')

    ses = 0

    for opt, servidor in matches:
        ses += 1

        servidor = servidor.replace('<strong>', '').replace('</strong>', '')

        srv = servidor.lower().strip()

        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '.*?src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '.*?src=&quot;(.*?)&quot;')

        if url.startswith('//') == True: url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '.*?src=&quot;(.*?)&quot;')

        if not servidor or not url: continue

        if 'opción' in servidor:
            link_other = servidor
            servidor = 'directo'
        elif servidor == 'anavids':
            link_other = servidor
            servidor = 'directo'
        elif servidor == 'analu':
            link_other = servidor
            servidor = 'directo'
        else: link_other = ''

        if servidor == 'various': link_other = servertools.corregir_other(srv)

        if url.endswith('.torrent'): servidor = 'torrent'
        elif 'magnet:?' in url: servidor = 'torrent'

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = 'Lat', other = link_other ))

    # ~ Descargas
    matches = scrapertools.find_multiple_matches(data, '<span class="Num">(.*?)</tr>')

    for match in matches:
        ses += 1

        servidor = scrapertools.find_single_match(match, 'alt="Descargar(.*?)">')
        servidor = servidor.replace('.', '').lower().strip()

        if not servidor: continue

        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        if url.endswith('.torrent'): servidor = 'torrent'
        elif 'magnet:?' in url: servidor = 'torrent'

        other = 'D'

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = 'Lat', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    if url.startswith(host):
        if item.other == 'D' or 'D ' in item.other :
            if config.get_setting('channel_seriesretro_proxies', default=''):
                url = httptools.downloadpage_proxy('seriesretro', url, follow_redirects=False, only_headers=True).headers.get('location', '')
            else:
                url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get('location', '')
        else:
            data = do_downloadpage(url)

            if item.other == 'anavids':
                url = scrapertools.find_single_match(data.lower(), '<iframe src="(.*?)"')

                data = do_downloadpage(url)

                url = scrapertools.find_single_match(str(data), 'sources.*?"(.*?)"')
            else:
                url = scrapertools.find_single_match(data, 'src="(.*?)"')

    if url:
        if url.startswith('//') == True: url = 'https:' + url

        if '/www.analu.xyz/' in url:
            return 'Servidor [COLOR plum]NO soportado[/COLOR]'
        elif '/gdriveplayer.io/' in url:
            return 'Servidor [COLOR plum]NO soportado[/COLOR]'

        if url.endswith('.torrent'):
            itemlist.append(item.clone( url = url, server = 'torrent' ))
            return itemlist

        elif 'magnet:?' in url:
            itemlist.append(item.clone( url = url, server = 'torrent' ))
            return itemlist

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if not new_server.startswith("http"): servidor = new_server

        if servidor != 'directo':
            url = servertools.normalize_url(servidor, url)

            if 'zplayer' in url: url += "|referer=%s" % host

            itemlist.append(item.clone(url = url, server = servidor))

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
