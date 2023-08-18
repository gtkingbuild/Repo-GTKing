# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urlparse
else:
    import urllib.parse as urlparse


import os, re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb, jsontools


host = 'https://play.pelishouse.me/'


# ~ Series predominan  Enlaces No Soportados  (30/8/2022)

# ~ por si viene de enlaces guardados
ant_hosts = ['https://pelishouse.com/', 'https://pelishouse.me/', 'https://ww1.pelishouse.me/']


domain = config.get_setting('dominio', 'pelishouse', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'pelishouse')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'pelishouse')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_pelishouse_proxies', default=''):
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

    timeout = None
    if host in url:
        if config.get_setting('channel_pelishouse_proxies', default=''): timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        data = httptools.downloadpage_proxy('pelishouse', url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '?s=' in url:
                platformtools.dialog_notification('PelisHouse', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')
                data = httptools.downloadpage_proxy('pelishouse', url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage_proxy('pelishouse', url, post=post, headers=headers, timeout=timeout).data
        except:
            pass

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'pelishouse', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_pelishouse', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='pelishouse', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_pelishouse', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'genre/mas-vistas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + 'genre/peliculas-marvel-online/', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 3D', action = 'list_3d', url = host + 'quality/3d/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo Series TV', action = 'list_all', url = host + 'tvshows/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Catálogo Series Animadas', action = 'list_all', url = host + 'genre/series-animadas-online-espanol-latino/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    if item.search_type == 'movie':
       itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'genre/espanol-castellano/', text_color = text_color ))
       itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'genre/espanol-latino-online/', text_color = text_color ))
       itemlist.append(item.clone( title = 'En inglés', action = 'list_all', url = host + 'genre/peliculas-en-ingles/', text_color = text_color ))
       itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'genre/peliculas-online-subtituladas/', text_color = text_color ))
    else:
       itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'genre/series-en-espanol-castellano/', text_color = text_color ))
       itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'genre/series-en-espanol-latino-hd/', text_color = text_color ))
       itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'genre/series-subtituladas/', text_color = text_color ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    opciones = [
       ('accion', 'Acción'),
       ('action-adventure', 'Acción aventura'),
       ('animacion', 'Animación'),
       ('aventura', 'Aventura'),
       ('belica', 'Bélica'),
       ('ciencia-ficcion', 'Ciencia ficción'),
       ('cinecalidad', 'Cinecalidad'),
       ('cinecalidad-top', 'Cinecalidad top' ),
       ('comedia', 'Comedia'),
       ('crimen', 'Crimen'),
       ('descargacineclasico-tv', 'Descargacineclasico tv'),
       ('documental', 'Documental'),
       ('drama', 'Drama'),
       ('familia', 'Familia'),
       ('fantasia', 'Fantasía'),
       ('historia', 'Historia'),
       ('kids', 'Kids'),
       ('misterio', 'Misterio'),
       ('musica', 'Música'),
       ('pelicula-de-tv', 'Películas de tv'),
       ('pelicula-de-la-television', 'Películas de la television'),
       ('reality', 'Reality'),
       ('romance', 'Romance'),
       ('sci-fi-fantasy', 'Sci-fi fantasy'),
       ('soap', 'Soap'),
       ('suspense', 'Suspense'),
       ('terror', 'Terror'),
       ('war-politics', 'War -politics'),
       ('western', 'Western')
       ]

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    for opc, tit in opciones:
        if item.search_type == 'tvshow':
           if opc == 'accion': continue
           elif opc == 'aventura': continue
           elif opc == 'belica': continue
           elif opc == 'ciencia-ficcion': continue
           elif opc == 'fantasia': continue
           elif opc == 'musica': continue
           elif opc == 'romance': continue
           elif opc == 'suspense': continue

           if tit == 'Cinecalidad': continue
           elif tit == 'Cinecalidad top': continue
           elif tit == 'Descargacineclasico tv': continue
           elif 'Películas' in tit: continue

        itemlist.append(item.clone( title=tit, url= host + 'genre/' + opc + '/', action = 'list_all', text_color = text_color))

    if itemlist:
        if item.search_type == 'movie':
            if not descartar_xxx:
                itemlist.append(item.clone( action = 'list_all', title = 'xxx / adultos', url = host + 'genre/peliculas-18/', text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'release/' + str(x) + '/', action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<ul class="genres scrolling">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)" title="[^"]+">([^<]+)</a>')

    for url, title in matches:
        if not 'Peliculas ' in title: continue

        if 'En Ingles' in title: continue
        elif 'subtituladas' in title: continue

        title = title.replace('Peliculas', '').strip()

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Australianas', url = host + 'genre/peliculas-australianas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Bolivianas', url = host + 'genre/peliculas-bolivianas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Brasileñas', url = host + 'genre/peliculas-brasilenas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Canadienses', url = host + 'genre/peliculas-canadienses/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Chinas', url = host + 'genre/peliculas-china/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Colombianas', url = host + 'genre/peliculas-colombianas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Coreanas', url = host + 'genre/peliculas-coreanas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Españolas', url = host + 'genre/peliculas-espanolas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Estadounidenses', url = host + 'genre/peliculas-estadounidenses/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Francesas', url = host + 'genre/peliculas-francesas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Indias', url = host + 'genre/peliculas-indias/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Italianas', url = host + 'genre/peliculas-italianas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Japonesas', url = host + 'genre/peliculas-japonesas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Noruegas', url = host + 'genre/peliculas-noruegas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Panameñas', url = host + 'genre/peliculas-panamenas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Peruanas', url = host + 'genre/peliculas-peruanas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Tailandesas', url = host + 'genre/peliculas-tailandesa/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Taiwanesas', url = host + 'genre/peliculas-taiwanesas/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Uruguayas', url = host + 'genre/peliculas-uruguayas/', text_color='moccasin' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Checas', url = host + 'genre/peliculas-de-chequia/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Guatemaltecas', url = host + 'genre/peliculas-de-guatemala/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Islandesas', url = host + 'genre/peliculas-de-islandia/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Inglesas', url = host + 'genre/peliculas-de-reino-unido/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Rusas', url = host + 'genre/peliculas-de-rusia/', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Sudafricanas', url = host + 'genre/peliculas-de-sudafrica/', text_color='moccasin' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(str(data), '<h2>Añadido(.*?)<footer class="main">')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    if item.search_type == 'movie':
        for match in matches:
            url = scrapertools.find_single_match(match, '<a href="(.*?)"')

            if 'tvshows' in url: continue

            thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
            title = scrapertools.find_single_match(match, 'alt="(.*?)"')
            qlty = scrapertools.find_single_match(match, 'class="quality">(.*?)</span>')

            year = scrapertools.find_single_match(match, '</h3>.*?<span>(\d+)</span>')

            if not year: year = '-'
            else:
               if '(' + year + ')' in title: title = title.replace('(' + year + ')', '').strip()
               elif year in title:  title = title.replace(year, '').strip()

            title = title.replace('&#8211;', '').replace('&#8230;', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    else:
        for match in matches:
            url = scrapertools.find_single_match(match, '<a href="(.*?)"')

            if 'movies' in url: continue

            thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
            title = scrapertools.find_single_match(match, 'alt="(.*?)"')

            year = scrapertools.find_single_match(match, '</h3>.*?<span>(\d+)</span>')

            if not year: year = '-'
            else:
               if '(' + year + ')' in title: title = title.replace('(' + year + ')', '').strip()
               elif year in title:  title = title.replace(year, '').strip()

            title = scrapertools.find_single_match(title, '(.*?) Serie.*?nline') or title

            title = title.replace('&#8211;', '').replace('&#8230;', '').replace('Ver ', '').strip()

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if item.search_type == 'movie':
            next_page = scrapertools.find_single_match(data, '<a class=\'arrow_pag\' href="([^"]+)">')
            if not next_page: next_page = scrapertools.find_single_match(data, '<span class="current">.*?</span>' + "<a href='(.*?)'" + '.*?class="inactive">')
            if not next_page: next_page = scrapertools.find_single_match(data, '<span class="current">.*?</span><a href="(.*?)".*?class="inactive">')
        else:
            next_page = scrapertools.find_single_match(data, '<span class="current">.*?</span>' + "<a href='(.*?)'" + '.*?class="inactive">')
            if not next_page: next_page = scrapertools.find_single_match(data, '<span class="current">.*?</span><a href="(.*?)".*?class="inactive">')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone(title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral'))

    return itemlist


def list_3d(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        year = scrapertools.find_single_match(match, '</h3>.*?<span>(\d+)</span>')

        if not year: year = '-'
        else:
           if '(' + year + ')' in title: title = title.replace('(' + year + ')', '').strip()
           elif year in title:  title = title.replace(year, '').strip()

        title = title.replace('&#8211;', '').replace('&#8230;', '').strip()

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<span class='se-t.*?'>(.*?)</span><span class='title'>(.*?)<i>")
    if not matches: matches = scrapertools.find_multiple_matches(data, '<span class="se-t.*?">(.*?)</span><span class="title">(.*?)<i>')

    for numtempo, title in matches:
        title = title.strip()

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = numtempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    patron = "'<li class='mark-.*?src='(.*?)'.*?<div class='numerando'>(\d+) - (\d+).*?href='(.*?)'>(.*?)</a>"

    matches = scrapertools.find_multiple_matches(data, patron)

    if not matches:
        patron = '<li class="mark-.*?src="(.*?)".*?<div class="numerando">(\d+) - (\d+).*?href="(.*?)">(.*?)</a>'

        matches = scrapertools.find_multiple_matches(data, patron)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PelisHouse', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisHouse', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisHouse', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisHouse', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisHouse', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PelisHouse', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, season, episode, url, title in matches[item.page * item.perpage:]:
        if item.contentSeason:
            if not str(season) == str(item.contentSeason): continue

        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail=thumb, contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color= 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = "<li id='player-option-.*?class='dooplay_player_option'.*?data-type='(.*?)'.*?data-post='(.*?)'.*?data-nume='(.*?)'.*?<span class='title'>(.*?)</span>"

    matches = scrapertools.find_multiple_matches(data, patron)

    if not matches:
        patron = '<li id="player-option-.*?class="dooplay_player_option".*?data-type="(.*?)".*?data-post="(.*?)".*?data-nume="(.*?)".*?<span class="title">(.*?)</span>'

        matches = scrapertools.find_multiple_matches(data, patron)

    ses = 0

    for _type, post, nume, tag in matches:
        ses += 1

        url = get_video_url(item, _type, post, nume)

        if not url: continue

        try:
           lang, qlty = tag.strip().split(' ')
        except Exception:
           logger.error('idioma-calidad Desconocidos')
           lang = ''
           qlty = ''

        language = detectar_idiomas(lang)

        url = urlparse.urljoin(item.url, url)

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url or '/www.jplayer.' in url: continue

        elif '.oceanplay.' in url: continue
        elif '/entrepeliculasyseries.' in url: continue
        elif '/demariquita.' in url: continue
        elif '/g-nula.top/' in url: continue
        elif '/media.esplay.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, language = language, quality = qlty ))

    # ~ Download
    patron = "<tr id=.*?src='.*?domain=([^']+)'.*?href='(.*?)'.*?class='quality'>(.*?)</strong></td><td>(.*?)</td><td>"

    matches = scrapertools.find_multiple_matches(data, patron)

    for server, url, qlty, lang in matches:
        ses += 1

        language = detectar_idiomas(lang)

        url = urlparse.urljoin(item.url, url)

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url or '/www.jplayer.' in url: continue

        if url:
            servidor = server.split('.')[0].lower()

            if servidor == 'tenvoi': continue
            elif servidor == 's5': continue
            elif servidor == 'pelipluspeliplus': continue
            elif servidor == 'demariquita': continue
            elif servidor == 'g-nula': continue

            if servidor == 'utorrent': servidor = 'torrent'
            elif servidor == 'uptostream': servidor = 'uptobox'

            servidor = servertools.corregir_servidor(servidor)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, other = 'd', language = language, quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def get_video_url(item, _type, post, nume):
    post = {'action': 'doo_player_ajax', 'post': post, 'nume': nume, 'type': _type}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = {'Referer': item.url})

    try:
       url = jsontools.load(data)['embed_url']

       url = url.replace('\\/', '/')

       if not url.startswith('http'):
           url = scrapertools.find_single_match(str(url), 'src="(.*?)"')
           if not url.startswith('http'): url = ''
    except:
       url = ''

    return url


def detectar_idiomas(tags):
    languages = []

    tags = tags.lower()
    idio = scrapertools.find_multiple_matches(tags, 'rel="tag">(.*?)</a>')

    if idio:
       for idioma in idio:
           if idioma == 'castellano': languages.append('Esp')
           if idioma == 'español': languages.append('Esp')
           if idioma == 'latino': languages.append('Lat')
           if idioma == 'ingles': languages.append('Eng')
           if idioma == 'subtitulado': languages.append('Vose')
    else:
       if tags == 'castellano': return 'Esp'
       elif tags == 'espaÑol': return 'Esp'
       elif tags == 'latino': return 'Lat'
       elif tags == 'ingles': return 'Eng'
       elif tags == 'subtitulado': return 'Vose'

       elif 'ingles' in tags: return 'Eng'
       elif 'subtitulado' in tags: return 'Vose'
       else: return '?'

    return languages


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

    if item.server == 'torrent':
        try:
           if not item.url.startswith(host):
               url = httptools.downloadpage(item.url, follow_redirects=False).headers['location']
           else:
               url = httptools.downloadpage_proxy('pelishouse', item.url, follow_redirects=False).headers['location']
        except:
           data = do_downloadpage(item.url)

           url = scrapertools.find_single_match(data, 'href="(.*?)"')

           if url.startswith('magnet:'): pass
           elif url.endswith(".torrent"): pass
           else: url = ''

        if url:
            itemlist.append(item.clone( url=url, server='torrent'))

    elif item.url.startswith(host):
        if item.other == 'd':
            if '/links/' in item.url:
                try:
                   if not item.url.startswith(host):
                       url = httptools.downloadpage(item.url, follow_redirects=False).headers['location']
                   else:
                       url = httptools.downloadpage_proxy('pelishouse', item.url, follow_redirects=False).headers['location']
                except:
                   data = do_downloadpage(item.url)
                   url = scrapertools.find_single_match(data, 'href="(.*?)"')

                if '/www.jplayer.net/' in url: url = ''

            else:
                data = do_downloadpage(item.url)
                url = scrapertools.find_single_match(str(data), 'href="(.*?)"')

            if url:
                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                itemlist.append(item.clone( url=url, server=servidor))

        else:
            data = do_downloadpage(item.url)

            url = scrapertools.find_single_match(str(data), '"file":"(.*?)"')
            if not url: url = scrapertools.find_single_match(str(data), '<source src="(.*?)"')

            if url:
               url = url.replace('\\/', '/')

               servidor = servertools.get_server_from_url(url)
               servidor = servertools.corregir_servidor(servidor)

               itemlist.append(item.clone( url=url, server=servidor))

    elif item.url.startswith('https://peliscalidad.top/'):
        video_id = item.url.split('/')[-1]

        data = do_downloadpage('https://peliscalidad.top/api/source/%s' % video_id, post={'r': '', 'd': 'peliscalidad.top'})

        data = jsontools.load(data)

        if 'Video not found or has been removed' in str(data):
            return 'Video eliminado'

        if data:
            for video in data['data']:
                if not video['file'].startswith(host):
                    url = httptools.downloadpage(video['file'], follow_redirects=False).headers['location']
                else:
                    url = httptools.downloadpage_proxy('pelishouse', video['file'], follow_redirects=False).headers['location']

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                itemlist.append(item.clone( url=url, server=servidor))

    elif item.url.startswith('https://api.cuevana3.io'):
        fid = scrapertools.find_single_match(item.url, "h=([^&]+)")

        if '/fembed/?h=' in item.url:
            api_url = 'https://api.cuevana3.io/fembed/rd.php'
            api_post = 'h=' + fid + '&ver=si'
        elif '/sc/index.php?h=' in item.url:
            api_url = 'https://api.cuevana3.io/sc/r.php'
            api_post = 'h=' + fid
        elif '/ir/goto_ddh.php?h=' in item.url:
            api_url = 'https://api.cuevana3.io/ir/redirect_ddh.php'
            api_post = 'url=' + fid
        else:
            api_url = 'https://api.cuevana3.io/ir/rd.php'
            api_post = 'url=' + fid

        try:
           if not api_url.startswith(host):
               url = httptools.downloadpage(api_url, post=api_post, follow_redirects=False).headers['location']
           else:
               url = httptools.downloadpage_proxy('pelishouse', api_url, post=api_post, follow_redirects=False).headers['location']
        except:
           url = ''

        if url:
            if url.startswith('//'): url = 'https:' + url

            fid = scrapertools.find_single_match(url, "h=([^&]+)")

            if fid:
                if '/fembed/?h=' in url:
                    api_url = 'https://api.cuevana3.io/fembed/rd.php'
                    api_post = 'h=' + fid + '&ver=si'
                elif '/sc/index.php?h=' in url:
                    api_url = 'https://api.cuevana3.io/sc/r.php'
                    api_post = 'h=' + fid
                elif '/ir/goto_ddh.php?h=' in url:
                    api_url = 'https://api.cuevana3.io/ir/redirect_ddh.php'
                    api_post = 'url=' + fid
                else:
                    api_url = 'https://api.cuevana3.io/ir/rd.php'
                    api_post = 'url=' + fid

                try:
                   if not api_url.startswith(host):
                       url = httptools.downloadpage(api_url, post=api_post, follow_redirects=False).headers['location']
                   else:
                       url = httptools.downloadpage_proxy('pelishouse', api_url, post=api_post, follow_redirects=False).headers['location']
                except:
                   url = ''

            if '//damedamehoy.' in url or '//tomatomatela.' in url: url = resuelve_dame_toma(url)

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone( url=url, server=servidor))

    elif item.url.startswith('https://apialfa.tomatomatela.com'):
        fid = scrapertools.find_single_match(item.url, "h=([^&]+)")

        api_url = 'https://api.cuevana3.io/ir/redirect_ddh.php'
        api_post = 'url=' + fid

        try:
           if not api_url.startswith(host):
               url = httptools.downloadpage(api_url, post=api_post, follow_redirects=False).headers['location']
           else:
               url = httptools.downloadpage_proxy('pelishouse', api_url, post=api_post, follow_redirects=False).headers['location']
        except:
           url = ''

        if '//damedamehoy.' in url or '//tomatomatela.' in url:
            url = resuelve_dame_toma(url)

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone( url=url, server=servidor))

    else:
        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone( url=item.url, server=servidor))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = do_downloadpage(item.url)

    if item.search_type == 'movie' or item.search_type == 'all':
        patron = '<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)" /><span class="movies">Película</span>.*?<span class="year">(\d+)</span>'

        matches = scrapertools.find_multiple_matches(data, patron)

        for url, thumb, title, year in scrapertools.find_multiple_matches(data, patron):
            if descartar_xxx:
                if '/genre/18/' in url: continue

            if not year: year = '-'

            tipo = 'movie' if '/movies/' in url else 'tvshow'
            sufijo = '' if item.search_type != 'all' else tipo

            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            title = title.replace('&#8211;', '').replace('&#8230;', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo = sufijo, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    if item.search_type == 'tvshow' or item.search_type == 'all':
        patron = '<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)" /><span class="tvshows">TV</span>.*?<span class="year">(\d+)</span>'

        matches = scrapertools.find_multiple_matches(data, patron)

        for url, thumb, title, year in matches:
            title = scrapertools.find_single_match(title, '(?:Ver )?(.*?),? Serie.*?nline') or title

            if not year: year = '-'

            tipo = 'tvshow' if '/tvshows/' in url else 'movie'
            sufijo = '' if item.search_type != 'all' else tipo

            if not item.search_type == "all":
                if item.search_type == "movie": continue

            title = title.replace('&#8211;', '').replace('&#8230;', '').replace('Ver ', '').strip()

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo = sufijo, contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

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
