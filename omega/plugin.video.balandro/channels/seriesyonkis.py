# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


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


host = 'https://seriesyonkis.cx/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://seriesyonkis.cc/', 'https://seriesyonkis.io/', 'https://seriesyonkis.lat/',
             'https://seriesyonkis.nu/']


domain = config.get_setting('dominio', 'seriesyonkis', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'seriesyonkis')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'seriesyonkis')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_seriesyonkis_proxies', default=''):
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

    hay_proxies = False
    if config.get_setting('channel_seriesyonkis_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('seriesyonkis', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('seriesyonkis', url, post=post, headers=headers, raise_weberror=raise_weberror).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
            except:
                pass

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'seriesyonkis', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_seriesyonkis', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='seriesyonkis', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_seriesyonkis', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone ( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone ( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-p2/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Más vistas', action = 'list_all', url = host + 'mas-vistas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'DC comics', action = 'list_all', url = host + 'category/dc-comics/?tr_post_type=1', search_type = 'movie', text_color='moccasin' ))

    itemlist.append(item.clone ( title = 'Netflix', action = 'list_all', url = host + 'category/netflix/?tr_post_type=1', search_type = 'movie', text_color='moccasin' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'inicio/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'HBO', action = 'list_all', url = host + 'category/hbo/?tr_post_type=2', search_type = 'tvshow', text_color='moccasin' ))

    itemlist.append(item.clone ( title = 'Marvel', action = 'list_all', url = host + 'category/marvel/?tr_post_type=2', search_type = 'tvshow', text_color='moccasin' ))

    itemlist.append(item.clone ( title = 'Netflix', action = 'list_all', url = host + 'category/netflix/?tr_post_type=2', search_type = 'tvshow', text_color='moccasin' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host + 'inicio/')

    bloque =  scrapertools.find_single_match(data, '>Categories<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, tit in matches:
        tit = tit.replace('&amp;', '&')

        if tit == 'Actualizadas': continue
        elif tit == 'DC comics': continue
        elif tit == 'HBO': continue
        elif tit == 'Netflix': continue
        elif tit == 'News': continue

        if config.get_setting('descartar_anime', default=False):
            if title == 'Anime': continue

        if item.search_type == 'movie':
            if tit == 'Anime': continue
            elif tit == 'Marvel': continue
            elif tit == 'Reality': continue
            elif tit == 'Talk': continue

            url += '?tr_post_type=1'
        else:
            url += '?tr_post_type=2'

        itemlist.append(item.clone( title = tit.capitalize(), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque =  scrapertools.find_single_match(data, '</h1>(.*?)<div id="categories')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h3 class="Title">(.*?)</h3>')
        if not url or not title: continue

        if 'Inkaseries' in title: continue

        thumb = scrapertools.find_single_match(article, 'src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(article, 'class="Date AAIco-date_range">(\d+)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(article, '<span class="Qlty">([^<]+)</span>')

        tipo = 'movie' if '/movie/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        title = title.replace("&#8217;", "'")

        if tipo == 'movie':
            if not item.search_type == 'all':
               if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
               if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'class="page-numbers current">.*?href="([^"]+)')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('data-tab="(.*?)"', re.DOTALL).findall(data)

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = numtempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque =  scrapertools.find_single_match(data, 'data-tab="' + str(item.contentSeason) + '"(.*?)</table>')

    if not 'src=&quot;' in bloque:
        patron = '<span class="Num">(.*?)</span>.*?<a href="(.*?)".*?src="(.*?)".*?<td class="MvTbTtl">.*?">(.*?)</a>'
    else:
        patron = '<span class="Num">(.*?)</span>.*?<a href="(.*?)".*?src=(.*?)alt=.*?<td class="MvTbTtl">.*?">(.*?)</a>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesYonkis', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesYonkis', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesYonkis', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesYonkis', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesYonkis', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesYonkis', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for epis, url, thumb, title in matches[item.page * item.perpage:]:
        title = item.contentSeason + 'x' + epis + ' ' + title

        if thumb.startswith('//'): thumb = 'https:' + thumb
        thumb = thumb.replace('&quot;', '').strip()

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, contentType = 'episode', contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color= 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'ESP': 'Esp', 'LAT': 'Lat', 'ESPSUB': 'Vose', 'PLAYER': 'Vose', 'ENG': 'VO', 'ENGSUB': 'VOS'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'data-tplayernv="(.*?)".*?</span>(.*?)</span>')

    ses = 0

    for opt, lang in matches:
        ses += 1

        lang = lang.strip()

        lang = lang.replace('</li></ul>', '?')

        url = scrapertools.find_single_match(data, 'id="' + str(opt) + '".*?<iframe.*?src="(.*?)"')

        if not url or url.startswith('//'):
           new_url = scrapertools.find_single_match(data, 'id="' + str(opt) + '".*?src=&quot;(.*?)&quot;')
           if new_url:
               if '/movie/' in item.url: new_url = new_url.replace('trembed=1', 'trembed=0').replace('trembed=2', 'trembed=0')

               url = new_url

        if url:
            if '/movie/' in item.url:
                new_url = url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

                if '/?trembed=' in new_url:
                    data = do_downloadpage(new_url)

                    new_url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')

                    if '/gnula.club/embed.php?id=' in new_url:
                        data = do_downloadpage(new_url)

                        urls = scrapertools.find_multiple_matches(data, "go_to_player.*?'(.*?)'")
                        if not urls: urls = scrapertools.find_multiple_matches(data, '<a target="_blank" href="(.*?)"')

                        for url in urls:
                            if '/1fichier.' in url: continue

                            servidor = servertools.get_server_from_url(url)
                            servidor = servertools.corregir_servidor(servidor)

                            if servertools.is_server_available(servidor):
                                if not servertools.is_server_enabled(servidor): continue
                            else:
                                if not config.get_setting('developer_mode', default=False): continue

                            url = servertools.normalize_url(servidor, url)

                            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang, lang) ))

                        return itemlist

                itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, language = IDIOMAS.get(lang, lang) ))

            else:
                url = url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

                data2 = do_downloadpage(url)

                url = scrapertools.find_single_match(data2, '<iframe.*?src="([^"]+)')

                if '/gnula.club/embed.php?id=' in url:
                    data = do_downloadpage(url)

                    urls = scrapertools.find_multiple_matches(data, "go_to_player.*?'(.*?)'")
                    if not urls: urls = scrapertools.find_multiple_matches(data, '<a target="_blank" href="(.*?)"')

                    for url in urls:
                        if '/1fichier.' in url: continue

                        servidor = servertools.get_server_from_url(url)
                        servidor = servertools.corregir_servidor(servidor)

                        if servertools.is_server_available(servidor):
                            if not servertools.is_server_enabled(servidor): continue
                            else:
                                if not config.get_setting('developer_mode', default=False): continue

                        url = servertools.normalize_url(servidor, url)

                        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang, lang) ))

                    return itemlist

                if not 'pelispluss' in url and not 'gnula.' in url:
                    servidor = servertools.get_server_from_url(url, disabled_servers=True)

                    if servidor is None: continue

                    servidor = servertools.corregir_servidor(servidor)

                    if servertools.is_server_available(servidor):
                        if not servertools.is_server_enabled(servidor): continue
                    else:
                        if not config.get_setting('developer_mode', default=False): continue

                    url = servertools.normalize_url(servidor, url)

                if not 'pelispluss' in url and not 'gnula.' in url:
                    itemlist.append(Item( channel=item.channel, action='play', server='directo', title='', url=url, language=IDIOMAS.get(lang, lang) ))

                else:
                    data3 = do_downloadpage(url)

                    matches2 = scrapertools.find_multiple_matches(data3, "go_to_player.*?'(.*?)'.*?<span>(.*?)</span>.*?<p>(.*?)-.*?</p>")

                    for url, srv, lng in matches2:
                        srv = srv.replace('.com', '').replace('.net', '').replace('.cc', '').replace('.to', '').replace('.sx', '')

                        if srv == 'nodispounnnerbler': continue

                        srv = servertools.corregir_servidor(srv)

                        if servertools.is_server_available(srv):
                            if not servertools.is_server_enabled(srv): continue
                        else:
                            if not config.get_setting('developer_mode', default=False): continue

                        lng = lng.strip()
                        if lng == 'Espanol': lng = 'Esp'
                        elif lng == 'Latino': lng = 'Lat'
                        elif lng == 'Subtitulado': lng = 'Vose'
                        elif lng == 'Ingles': lng = 'VO'
                        else: lng = '?'

                        itemlist.append(Item( channel = item.channel, action = 'play', server = srv, title = '', url = url, language = lng ))

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

    if item.server == 'directo':
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        vid = scrapertools.find_single_match(url, 'h=(.*?)$')

        if vid:
            post = {'h': vid}
            if 'pelispluss' in url: link = 'https://pelispluss.net/sc/r.php'
            else: link = 'https://gnula.club//sc/r.php'

            if not link.startswith(host):
                 url = httptools.downloadpage(link, post = post, follow_redirects=False).headers.get('location', '')
            else:
                 if config.get_setting('channel_seriesyonkis_proxies', default=''):
                     url = httptools.downloadpage_proxy('seriesyonkis', link, post = post, follow_redirects=False).headers.get('location', '')
                 else:
                     url = httptools.downloadpage(link, post = post, follow_redirects=False).headers.get('location', '')

        else:
            if servidor == 'directo':
                data = do_downloadpage(url)

                url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')

    else:
        if 'pelispluss' in url or 'gnula.' in url:
            vid = scrapertools.find_single_match(url, 'h=(.*?)$')

            if vid:
                post = {'h': vid}

                if 'pelispluss' in url: link = 'https://pelispluss.net/sc/r.php'
                else: link = 'https://gnula.club//sc/r.php'

                if not link.startswith(host):
                    url = httptools.downloadpage(link, post = post, follow_redirects=False).headers.get('location', '')
                else:
                    if config.get_setting('channel_seriesyonkis_proxies', default=''):
                        url = httptools.downloadpage_proxy('seriesyonkis', link, post = post, follow_redirects=False).headers.get('location', '')
                    else:
                        url = httptools.downloadpage(link, post = post, follow_redirects=False).headers.get('location', '')

    if url:
        if 'openload' in url or 'powvideo' in url or 'streamplay' in url or 'rapidvideo' in url or 'streamango' in url or 'verystream' in url or 'vidtodo' in url or 'tutumeme' in url:
            return 'Servidor [COLOR plum]NO soportado[/COLOR]'

        if url.startswith('//'): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor:
            url = servertools.normalize_url(servidor, url)

            itemlist.append(item.clone( url=url, server=servidor ))

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
