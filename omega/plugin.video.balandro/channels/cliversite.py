# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, time

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


host = 'https://www2.cliver.me'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://cliver.site', 'https://www1.cliver.me']


domain = config.get_setting('dominio', 'cliversite', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'cliversite')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'cliversite')
    else: host = domain


perpage = 30


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_cliversite_proxies', default=''):
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

    hay_proxies = False
    if config.get_setting('channel_cliversite_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('cliversite', url, post=post, headers=headers).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('cliversite', url, post=post, headers=headers).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers).data
            except:
                pass

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'cliversite', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_cliversite', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='cliversite', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_cliversite', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas', search_type = 'movie', tipo = 'index', pagina = 1 ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + '/peliculas/estrenos', search_type = 'movie', tipo = 'estrenos', pagina = 1, text_color='cyan' ))

    itemlist.append(item.clone( title = 'Más Vistas', action = 'list_all', url = host + '/peliculas/mas-vistas', search_type = 'movie', page = 0, pagina = 1 ))  

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + '/peliculas/tendencias', search_type = 'movie', page = 0, pagina = 1 ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/series', search_type = 'tvshow', tipo = 'index', pagina = 1 ))

    itemlist.append(item.clone( title = 'Series con nuevos capítulos', action = 'list_all', url = host + '/series/tendencias', search_type = 'tvshow', pagina = 1, text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Más Vistas', action = 'list_all', url = host + '/series/mas-vistas', search_type = 'tvshow', page = 0, pagina = 1 ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    url = host if item.search_type == 'movie' else host + '/series'

    data = do_downloadpage(url)

    bloque = scrapertools.find_single_match(data, '<div class="generos">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">\s*<span class="cat">([^<]+)')

    for url, title in matches:
        if item.search_type == 'tvshow': url = url.replace('peliculas', 'series')

        url = host + url

        itemlist.append(item.clone( action="list_all", title=title, url=url, pagina = 1, text_color = text_color ))

    if itemlist:
        if item.search_type == 'movie':
            itemlist.append(item.clone( action="list_all", title='Guerra', url=host + '/peliculas/genero/guerra', pagina = 1, text_color = text_color ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie': tope = 1938
    else: tope = 1949

    for ano in range(current_year, tope, -1):
        if item.search_type == 'movie': url = host + '/peliculas/anio/' + str(ano)
        else: url = host + '/series/anio/' + str(ano)

        itemlist.append(item.clone( action="list_all", title=str(ano), url=url, pagina = 1, text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.search_type == 'movie': tipo_web = 'peliculas'
    elif item.search_type == 'tvshow': tipo_web = 'series'
    else: tipo_web = ''

    url_acceso = item.url

    if not '/search.html' in item.url:
        if not '?tipo=' in url_acceso: url_acceso = url_acceso + '?tipo=' + tipo_web
        if not '&page=' in url_acceso: url_acceso = url_acceso + '&page=' + str(item.pagina)

    data = do_downloadpage(url_acceso)

    if item.tipo == 'index': data = scrapertools.find_single_match(data, 'AGREGADAS(.*?)</section>')
    elif '/series/tendencias' in item.url: data = scrapertools.find_single_match(data, 'NUEVOS(.*?)</section>')
    elif '/search.html' in item.url: data = scrapertools.find_single_match(data, 'RESULTADOS(.*?)</section>')

    matches = re.compile('<article class="contenido-p">(.*?)</article>', re.DOTALL).findall(data)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2>(.*?)</h2>').strip()

        if not url or not title: continue

        url = host + url

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span>(\d{4})')
        if not year: year = '-'

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, pagina = item.pagina, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            if not item.tipo == 'estrenos':
                if not '/search.html' in item.url:
                    if item.tipo == 'index': tope = 12
                    else: tope = 18

                    if len(itemlist) >= tope:
                        pagina = item.pagina + 1
                        url = url_acceso.split('?tipo=')[0]
                        url = url + '?tipo=index' + '&page=' + str(pagina)

                        itemlist.append(item.clone( title = 'Siguientes ...', url = url, action = 'list_all', pagina = pagina, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="menu-item " id="temporada(\d+)">', re.DOTALL).findall(data)

    num_matches = len(matches)

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

        if num_matches >= 10:
           if len(numtempo) == 1: nro_temp = '0' + numtempo
           else: nro_temp = numtempo

           title = 'Temporada ' + nro_temp

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = numtempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.title)


def episodios(item):
    logger.info()
    itemlist = []

    tab_epis = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="mic">(.*?)<i class="fa fa-play">', re.DOTALL).findall(data)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('CliverSite', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('CliverSite', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('CliverSite', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('CliverSite', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('CliverSite', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('CliverSite', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches:
        season = scrapertools.find_single_match(match, 'data-season="([^"]+)')

        if not season:
            num_matches = num_matches - 1
            continue

        episode = scrapertools.find_single_match(match, 'data-ep="([^"]+)')

        if item.contentSeason:
            if not str(item.contentSeason) == str(season):
                num_matches = num_matches - 1
                continue

        if len(episode) == 1: nro_epi = '0' + episode
        else: nro_epi = episode

        titulo = season + 'x' + nro_epi + ' Episodio ' + episode

        url = item.url + '/' + season + '/' + episode

        ord_epis = str(nro_epi)

        if len(str(ord_epis)) == 1: ord_epis = '0000' + ord_epis
        elif len(str(ord_epis)) == 2: ord_epis = '000' + ord_epis
        elif len(str(ord_epis)) == 3: ord_epis = '00' + ord_epis
        else:
            if num_matches > 50: ord_epis = '0' + ord_epis

        if num_matches > 50: tab_epis.append([ord_epis, url, titulo, nro_epi])
        else:
           itemlist.append(item.clone( action='findvideos', title = titulo, url = url,
                                       orden = ord_epis, contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

    if num_matches > 50:
        tab_epis = sorted(tab_epis, key=lambda x: x[0])

        for orden, url, tit, epi in tab_epis[item.page * item.perpage:]:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = tit,
                                        orden = orden, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epi ))

            if len(itemlist) >= item.perpage:
                break

        tmdb.set_infoLabels(itemlist)

        if itemlist:
            if num_matches > ((item.page + 1) * item.perpage):
                itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", data_epi = item.data_epi, perpage = item.perpage,
                                            orden = '10000', page = item.page + 1, text_color = 'coral' ))

        return itemlist

    else:
        tmdb.set_infoLabels(itemlist)

        return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'lat': 'Lat', 'es': 'Esp', 'vose': 'Vose', 'en': 'VO'}

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    matches = scrapertools.find_multiple_matches(data, '<img src="/static/img/bg/icon_(.*?)_.*?data-id="(.*?)"')

    ses = 0

    for lang, data_id in matches:
        ses += 1

        bloque = scrapertools.find_single_match(data, 'server-item-' + data_id + '(.*?)</div></div>')

        if bloque:
            if not bloque.startswith('</div>'): bloque = bloque + '</div>'

        enlaces = scrapertools.find_multiple_matches(bloque, 'data-video="(.*?)".*?<img.*?>(.*?)</div>')

        for data_video, srv in enlaces:
            url = data_video

            if url.startswith('//'): url = 'https:' + url

            if url.startswith('https://pelisplay.ioplay?'): url = url.replace('https://pelisplay.ioplay?', 'https://pelisplay.io/play?')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            link_other = ''

            if servidor == 'directo':
                link_other = normalize_other(srv)
                if not link_other: continue
            elif servidor == 'various': link_other = servertools.corregir_other(url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang, lang), other = link_other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def normalize_other(srv):
    # hydrax no es pot resoldre

    srv = srv.replace('.to', '').replace('.com', '').replace('.xyz', '').lower()

    if srv == 'peliscloud': link_other = 'cloud'
    elif srv == 'damedamehoy': link_other = 'dame'
    elif srv == 'tomatomatela': link_other = 'dame'
    elif srv == 'suppervideo': link_other = 'super'
    elif srv == 'apialfa': link_other = 'apialfa'
    else:
       if config.get_setting('developer_mode', default=False): link_other = srv
       else: link_other = ''

    return link_other


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

    domain_memo = config.get_setting('dominio', 'cliversite', default='')

    if domain_memo: host_player = domain_memo
    else: host_player = host

    servidor = item.server

    url = item.url

    if item.other:
        if item.other == 'cloud':
            dom = '/'.join(item.url.split('/')[:3])
            vid = scrapertools.find_single_match(item.url, 'id=([^&]+)$')
            if not dom or not vid: return itemlist

            url = dom + '/playlist/' + vid + '/' + str(int(time.time() * 1000))

            data = do_downloadpage(url)

            matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+)\s*(.*?\.m3u8)')
            if matches:
                for res, url in sorted(matches, key=lambda x: int(x[0]), reverse=True):
                    itemlist.append(item.clone(url = dom + url, server = 'm3u8hls'))
                    break

                return itemlist

        elif item.other == 'dame':
            url = resuelve_dame_toma(item.url)

            if url:
                itemlist.append(item.clone(url=url, server=servidor))
                return itemlist

        elif item.other == 'apialfa':
            fid = scrapertools.find_single_match(item.url, "h=([^&]+)")

            if fid:
                if '/sc/' in item.url:
                    post = {'h': fid}

                    vid = item.url.replace('https://apialfa.tomatomatela.club/sc/index.php', 'https://apialfa.tomatomatela.club/sc/r.php')

                    data = do_downloadpage(vid, post=post)

                    url = scrapertools.find_single_match(data, '<meta name="og:url" content="(.*?)"')

                    if url:
                        servidor = servertools.get_server_from_url(url)
                        servidor = servertools.corregir_servidor(servidor)

                        url = servertools.normalize_url(servidor, url)

                        itemlist.append(item.clone(url=url, server=servidor))

                    return itemlist

                vid = item.url.replace('https://apialfa.tomatomatela.club/ir/player.php', 'https://apialfa.tomatomatela.club/ir/rd.php')

                post = {'url': fid}

                try:
                    if not vid.startswith(host_player):
                        new_url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                    else:
                        if config.get_setting('channel_cliversite_proxies', default=''):
                            new_url = httptools.downloadpage_proxy('cliversite', vid, post=post, follow_redirects=False).headers['location']
                        else:
                            new_url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                except:
                    new_url = ''

                if new_url:
                    if new_url.startswith('//'): new_url = 'https:' + new_url

                    data = do_downloadpage(new_url)
                    vid = scrapertools.find_single_match(data, 'value="(.*?)"')

                    if vid:
                        try:
                            if not vid.startswith(host_player):
                                new_url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                            else:
                                if config.get_setting('channel_cliversite_proxies', default=''):
                                    new_url = httptools.downloadpage_proxy('cliversite', vid, post=post, follow_redirects=False).headers['location']
                                else:
                                    new_url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                        except:
                            new_url = ''

                    if new_url:
                        servidor = servertools.get_server_from_url(new_url)
                        servidor = servertools.corregir_servidor(servidor)

                        if servidor and servidor != 'directo':
                            url = servertools.normalize_url(servidor, new_url)

                            itemlist.append(item.clone(url=url, server=servidor))

                        return itemlist

                else:
                    vid = 'https://apialfa.tomatomatela.club/ir/redirect_ddh.php'

                    try:
                        if not vid.startswith(host_player):
                            url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                        else:
                            if config.get_setting('channel_cliversite_proxies', default=''):
                                url = httptools.downloadpage_proxy('cliversite', vid, post=post, follow_redirects=False).headers['location']
                            else:
                                url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                    except:
                        url = ''

                    if url:
                        if '//damedamehoy.' in url or '//tomatomatela.' in url :
                            url = resuelve_dame_toma(url)

                            if url: itemlist.append(item.clone(url=url, server='directo'))
                            return itemlist

                        servidor = servertools.get_server_from_url(url)
                        servidor = servertools.corregir_servidor(servidor)

                        url = servertools.normalize_url(servidor, url)

                        itemlist.append(item.clone(url=url, server=servidor))
                        return itemlist

        elif item.other == 'super':
            if '/pelisplay.ccplay?' in item.url:
                if not item.url.startswith(host_player):
                    resp = httptools.downloadpage(item.url)
                else:
                    if config.get_setting('channel_cliversite_proxies', default=''):
                        resp = httptools.downloadpage_proxy('cliversite', item.url)
                    else:
                        resp = httptools.downloadpage(item.url)

                if not resp.data: return itemlist
            else:
                data = do_downloadpage(item.url)

            matches = scrapertools.find_multiple_matches(data, 'data-video="(.*?)"')

            if not matches:
                url = scrapertools.find_single_match(data, "sources.*?'(.*?)'")

                if url:
                    servidor = servertools.get_server_from_url(url)
                    servidor = servertools.corregir_servidor(servidor)

                    url = servertools.normalize_url(servidor, url)

                    itemlist.append(item.clone(url=url, server=servidor))
                    return itemlist

            for url in matches:
                if '//damedamehoy.' in url or '//tomatomatela.' in url:
                    url = resuelve_dame_toma(url)

                    if url:
                        itemlist.append(item.clone(url = url, server = 'directo'))
                        return itemlist

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                if servidor and servidor != 'directo':
                    itemlist.append(item.clone(url = url, server = servidor))
                    return itemlist

    if url:
        if '/clonamesta' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/search.html?keyword=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
