# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://entrepeliculasyseries.nz/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://entrepeliculasyseries.com/', 'https://entrepeliculasyseries.io/', 'https://entrepeliculasyseries.nu/']


domain = config.get_setting('dominio', 'entrepeliculasyseries', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'entrepeliculasyseries')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'entrepeliculasyseries')
    else: host = domain


perpage = 21


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_entrepeliculasyseries_proxies', default=''):
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

    if '/peliculas-del' in url: raise_weberror = False

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('entrepeliculasyseries', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                data = httptools.downloadpage_proxy('entrepeliculasyseries', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        except:
            pass

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'entrepeliculasyseries', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_entrepeliculasyseries', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='entrepeliculasyseries', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_entrepeliculasyseries', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'peliculas-de-netflix/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas recientes', action = 'list_all', url = host + 'series-recientes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    matches = scrapertools.find_multiple_matches(data, 'menu-item"><a href="([^"]+)">(.*?)</a>')

    for url, title in matches:
        if item.search_type == 'movie':
           if '/series-' in url: continue
        else:
           if '/peliculas-' in url: continue
           elif '/documentales' in url: continue

           if title == 'Series Documentales': title = 'Documentales'

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    if itemlist:
        if item.search_type == 'movie':
            itemlist.append(item.clone( action = 'list_all', title = 'Western', url = host + 'peliculas-de-western/' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 2008, -1):
        url = host + 'peliculas-del-' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    productoras = [
        ('amazon-prime-video', 'Amazon Prime Video'),
        ('dc-comic', 'Dc Comic'),
        ('disney', 'Disney +'),
        ('hbo', 'HBO'),
        ('hulu', 'Hulu'),
        ('marvel', 'Marvel'),
        ('netflix', 'Netflix')
        ]

    for opc, tit in productoras:
        url = host + 'series-de-' + opc + '/'

        itemlist.append(item.clone( title = tit, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<figcaption(.*?)</figcaption')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>').strip()
        if not title: title = scrapertools.find_single_match(match, '<h2>(.*?)</h2>').strip()

        url = scrapertools.find_single_match(match, 'href="([^"]+)"')
        if url == '#': url =  scrapertools.find_single_match(match, '<div class="title">.*?href="([^"]+)"')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, 'src="([^"]+)"')

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'

        if tipo == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        if tipo == 'tvshow':
            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            if "<span aria-current='page' class='current'>" in data:
                if '>Ultima »</a>' in data:
                    next_page_link = scrapertools.find_single_match(data, "<span aria-current='page' class='current'>.*?href=(.*?)>")

                    if next_page_link != '':
                        next_page_link =  next_page_link.replace('"', '')
                        itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page_link, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<option value="(.*?)"')

    for nro_season in matches:
        title = 'Temporada ' + nro_season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = nro_season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = nro_season ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.contentSeason)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    season = scrapertools.find_single_match(data, '<ul id="season-' + str(item.contentSeason) + '"(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(season, '<a href="(.*?)"')

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('EntrePeliculasySeries', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EntrePeliculasySeries', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EntrePeliculasySeries', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EntrePeliculasySeries', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('EntrePeliculasySeries', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for url in matches[item.page * item.perpage:]:
        title = item.contentSerieName.replace('&#038;', '&')
        nro_epi = scrapertools.find_single_match(url, '-capitulo-(.*?)/')

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

    options = scrapertools.find_multiple_matches(data, '<h3 class="select-idioma">(.*?)<div class="')

    ses = 0

    for option in options:
        ses += 1

        language = scrapertools.find_single_match(option, '</span>(.*?)<i').strip()

        if language == 'Subtitulado': language = 'Vose'
        elif language == 'Latino': language = 'Lat'
        elif language == 'Castellano': language = 'Esp'

        links = scrapertools.find_multiple_matches(option, '<li class="option".*?data-link="(.*?)".*?</span>(.*?)</li>')

        for url, servidor in links:
            servidor = servertools.corregir_servidor(servidor)

            if servidor:
               itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = language ))

    # Descargas
    if '>Enlaces de descarga<' in data:
        patron = '<tr><td>(.*?)</td><td>(.*?)</td><td><span>(.*?)</span>.*?href="(.*?)"'

        descargas = scrapertools.find_multiple_matches(data, patron)

        for servidor, language, qlty, url in descargas:
            ses += 1

            language = language.strip()

            if language == 'Subtitulado': language = 'Vose'
            elif language == 'Latino': language = 'Lat'
            elif language == 'Castellano': language = 'Esp'

            qlty = qlty.replace(' - ', ' ').strip()

            servidor = servertools.corregir_servidor(servidor)

            if servidor:
                if servidor == '1fitchier': continue

                if servidor:
                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = language,
                                          quality = qlty, other = 'D' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url
    servidor = item.server

    if item.other == 'D':
       if '/go.php?' in url:
           data = do_downloadpage(url)
           url = scrapertools.find_single_match(data, '<a id="DownloadScript" href="([^"]+)"')

           if '//cuon.io/' in url or '/uii.io/' in url: return itemlist

           if url:
               servidor = servertools.get_server_from_url(url)
               servidor = servertools.corregir_servidor(servidor)

    elif url.startswith(host):
       if '/ir.php?' in url:
           data = do_downloadpage(url)

           url = scrapertools.find_single_match(data, 'window.location="([^"]+)"')

           if url:
               servidor = servertools.get_server_from_url(url)
               servidor = servertools.corregir_servidor(servidor)

       elif '/player.php?' in url:
           url = url.replace('.html', '')

           data = do_downloadpage(url)

           vid = scrapertools.find_single_match(data, 'name="h" value="(.*?)"')

           if vid:
               post = {'h': vid}
               ref = url.replace('.html', '')
               headers = {'Referer': ref}

               # ~ url = httptools.downloadpage(host + 'r.php', post = post, headers= headers, follow_redirects=False).headers.get('location', '')
               url = httptools.downloadpage_proxy('entrepeliculasyseries', host + 'r.php', post = post, headers= headers, follow_redirects=False).headers.get('location', '')

               if url:
                   servidor = servertools.get_server_from_url(url)
                   servidor = servertools.corregir_servidor(servidor)

    if url:
        if not url.startswith('http'): url = 'https:' + url

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="TPost C">(.*?)</li')

    for match in matches:
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        title = title.replace('ver ', '').replace('Online', '').strip()
        if not title: title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if not title or not url: continue

        title = title.replace('Ver ', '').strip()

        thumb = scrapertools.find_single_match(match, 'src="([^"]+)"')

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if '/pelicula/' in url:
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        if '/serie/' in url:
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))

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

