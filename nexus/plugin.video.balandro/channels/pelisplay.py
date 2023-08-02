# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3: import urllib
else: import urllib.parse as urllib


import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.pelisplay.co/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_pelisplay_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www.pelisplay.tv/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ por si viene de enlaces guardados
    url = url.replace('pelisplay.co/ver-peliculas', 'pelisplay.co/peliculas')

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('pelisplay', url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_pelis', url = host + 'peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_pelis', url = host + 'peliculas/estrenos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Netflix', action = 'list_pelis', url = host + 'peliculas/netflix', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_pelis', url = host + 'peliculas?filtro=visitas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_series', url = host + 'series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_series', url = host + 'series/estrenos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Netflix', action = 'list_series', url = host + 'series/netflix', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_series', url = host + 'series?filtro=visitas', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if item.search_type == 'movie': url = host + 'peliculas'
    else: url = host + 'series'

    data = do_downloadpage(url)

    patron = '<a href="([^"]+)" class="category">.*?<div class="category-name">([^<]+)</div>\s*<div class="category-description">(\d+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, cantidad in matches:
        if '/estrenos' in url or '/netflix' in url: continue

        if descartar_xxx and scrapertools.es_genero_xxx(title): continue

        if item.search_type == 'movie':
            itemlist.append(item.clone( action="list_pelis", title='%s (%s)' % (title, cantidad), url=url ))
        else:
            itemlist.append(item.clone( action="list_series", title='%s (%s)' % (title, cantidad), url=url ))

    return sorted(itemlist, key=lambda it: it.title)


def list_pelis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<figure>(.*?)</figure>', re.DOTALL).findall(data)

    for article in matches:
        title = scrapertools.find_single_match(article, '<div class="Title">(.*?)</div>').strip()
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        if thumb.startswith('/'): thumb = host[:-1] + thumb

        plot = scrapertools.find_single_match(article, '<div class="Description">\s*<div>(.*?)</div>').strip()

        year = scrapertools.find_single_match(title, '\((\d{4})\)')
        if year: title = title.replace('(%s)' % year, '').strip()
        else: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" rel="next"')

        if next_page:
           itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_pelis', text_color='coral' ))

    return itemlist


def list_series(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<figure>(.*?)</figure>', re.DOTALL).findall(data)

    for article in matches:
        title = scrapertools.find_single_match(article, '<h2>(.*?)</h2>').strip()
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, 'img src="([^"]+)"')
        if thumb.startswith('/'): thumb = host[:-1] + thumb

        plot = scrapertools.find_single_match(article, '<span class="lg margin-bottom">(.*?)</span>').strip()

        year = scrapertools.find_single_match(article, 'Año: (\d{4})')
        if not year: year = '-'

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                    contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" rel="next"')

        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_series', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile(' class="abrir_temporada" href="([^"]+)">\s*<h4 class="name-movie"><strong>Temporada (\d+)', re.DOTALL).findall(data)

    for url, numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.url = url
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, page = 0, contentType = 'season', contentSeason = numtempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    matches = re.compile('<figure>(.*?)</figure>', re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PelisPlay', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlay', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlay', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlay', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PelisPlay', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for article in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')

        s_e = scrapertools.find_single_match(url, '/temporada-(\d+)/episodio-(\d+)')
        if not s_e: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        if thumb.startswith('/'): thumb = host[:-1] + thumb

        title = scrapertools.find_single_match(article, '<div class="Title">(.*?)</div>').strip()
        plot = scrapertools.find_single_match(article, '<div class="Description">\s*<div>(.*?)</div>').strip()

        titulo = '%sx%s %s' % (s_e[0], s_e[1], title)

        itemlist.append(item.clone( action='findvideos', title = titulo, url = url, thumbnail=thumb, plot = plot,
                                    contentType = 'episode', contentSeason = s_e[0], contentEpisodeNumber = s_e[1] ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    if txt in ['hd1080p', 'hd1080']: txt = '1080p'
    if txt in ['hd720p', 'hd720']: txt = '720p'
    orden = ['cam', 'screener', 'tshd', '360p', 'sd', '480p', 'hd', 'rip', 'dvdrip', '720p', '1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose', 'Original': 'VO'}

    data = do_downloadpage(item.url)

    data = scrapertools.find_single_match(data, '<div id="lista_online"(.*?)</table>')

    token = scrapertools.find_single_match(data, 'data-token="([^"]+)')

    matches = re.compile('<tr(.*?)</tr>', re.DOTALL).findall(data)

    for enlace in matches:
        if 'data-lang="Publicidad"' in enlace: continue

        tds = scrapertools.find_multiple_matches(enlace, '<td[^>]*>(.*?)</td>')
        if len(tds) != 6: continue
        if 'data-player=' not in tds[0]: continue

        calidad = tds[1].capitalize()
        lang = tds[2]
        agregado = tds[4]

        data_player = scrapertools.find_single_match(tds[0], 'data-player="([^"]+)')
        post = {'data': data_player, 'tipo': 'videohost', '_token': token}
        url = 'https://www.pelisplay.tv/entradas/procesar_player?' + urllib.urlencode(post)

        servidor = scrapertools.find_single_match(tds[0], '>([^<]+)</div>').lower().replace(' ', '')

        if servidor in ['tazmania', 'zeus', 'tiburon', 'mega', 'turbo']:
            agregado += ', ' + servidor.capitalize()
            servidor = 'm3u8hls' if servidor == 'turbo' else 'directo'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                              language = IDIOMAS.get(lang, lang), quality = calidad, quality_num = puntuar_calidad(calidad), other = agregado ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.split('?')[0]
    post = item.url.split('?')[1]

    data = do_downloadpage(url, post=post, raise_weberror=False).replace('\\/', '/')

    url = scrapertools.find_single_match(data, '"data":"([^"]+)')

    if 'pelisplay.tv' in url:
        data = do_downloadpage(url)
        if 'gkpluginsphp' in data:
            url = host + 'private/plugins/gkpluginsphp.php'
            post = {'link': scrapertools.find_single_match(data, 'link:"([^"]+)')}.replace('\\/', '/')
            data = do_downloadpage(url, post=post, raise_weberror=False)
            url = scrapertools.find_single_match(data, '"link":"([^"]+)')
            if url:
                itemlist.append(['mp4', url])

        elif 'start_jwplayer(JSON.parse(' in data:
            data = data.replace('\\/', '/')

            matches = scrapertools.find_multiple_matches(data, '"file"\s*:\s*"([^"]+)"\s*,\s*"label"\s*:\s*"([^"]*)"\s*,\s*"type"\s*:\s*"([^"]*)"')
            if matches:
                for url, lbl, typ in sorted(matches, key=lambda x: int(x[1][:-1]) if x[1].endswith('P') else x[1]):
                    itemlist.append(['%s [%s]' % (lbl, typ), url])

    elif 'tutumeme.net' in url:
        data = do_downloadpage(url, raise_weberror=False)
        f = scrapertools.find_single_match(data, '"file"\s*:\s*"([^"]+)')
        if f:
            itemlist.append(item.clone(url = 'https://tutumeme.net/embed/' + f, server = 'm3u8hls'))

    elif url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone(url=url, server=servidor))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<figure>(.*?)</figure>', re.DOTALL).findall(data)

    for article in matches:
        title = scrapertools.find_single_match(article, '<div class="Title">(.*?)</div>').strip()
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        if thumb.startswith('/'): thumb = host[:-1] + thumb

        plot = scrapertools.find_single_match(article, '<div class="Description">\s*<div>(.*?)</div>').strip()

        year = scrapertools.find_single_match(title, '\((\d{4})\)')
        if year: title = title.replace('(%s)' % year, '').strip()
        else: year = '-'

        tipo = 'tvshow' if 'span class="stick_serie"' in article else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" rel="next"')

        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_search', text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.search_type == 'movie':
            item.url = host + 'peliculas?buscar=' + texto.replace(" ", "+")
            return list_pelis(item)
        elif item.search_type == 'tvshow':
            item.url = host + 'series?buscar=' + texto.replace(" ", "+")
            return list_series(item)
        else:
            item.url = host + 'buscar?q=' + texto.replace(" ", "+")
            return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
