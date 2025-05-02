# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import re, os

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://www29.mejortorrent.eu'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://mejortorrent.app', 'https://mejortorrent.wtf', 'https://www1.mejortorrent.rip',
             'https://www2.mejortorrent.rip', 'https://www3.mejortorrent.rip', 'https://www4.mejortorrent.rip',
             'https://www5.mejortorrent.rip', 'https://www6.mejortorrent.rip', 'https://www7.mejortorrent.rip',
             'https://www8.mejortorrent.rip', 'https://www9.mejortorrent.rip', 'https://www10.mejortorrent.rip',
             'https://www11.mejortorrent.rip', 'https://www12.mejortorrent.rip', 'https://www13.mejortorrent.rip',
             'https://www14.mejortorrent.rip', 'https://www15.mejortorrent.rip', 'https://www16.mejortorrent.rip',
             'https://www17.mejortorrent.zip', 'https://www18.mejortorrent.zip', 'https://www19.mejortorrent.zip',
             'https://www20.mejortorrent.zip', 'https://www21.mejortorrent.zip', 'https://www22.mejortorrent.zip',
             'https://www23.mejortorrent.zip', 'https://www24.mejortorrent.zip', 'https://www25.mejortorrent.zip',
             'https://www26.mejortorrent.eu', 'https://www27.mejortorrent.eu', 'https://www28.mejortorrent.eu']


domain = config.get_setting('dominio', 'mejortorrentapp', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'mejortorrentapp')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'mejortorrentapp')
    else: host = domain


perpage = 30


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_mejortorrentapp_proxies', default=''):
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

    raise_weberror = True
    if '/peliculas/year/' in url: raise_weberror = False

    hay_proxies = False
    if config.get_setting('channel_mejortorrentapp_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('mejortorrentapp', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

        if not data:
            if not '/busqueda?q=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('MejorTorrentApp', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('mejortorrentapp', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'mejortorrentapp', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_mejortorrentapp', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='mejortorrentapp', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_mejortorrentapp', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='actions', action='show_old_domains', title='[COLOR coral][B]Historial Dominios[/B][/COLOR]', channel_id = 'mejortorrentapp', thumbnail=config.get_thumb('mejortorrentapp') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))
    itemlist.append(item.clone( title = 'Documentales', action = 'mainlist_documentales', text_color = 'cyan' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/public/peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_list', url = host + '/public/torrents/', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_list', url = host + '/busqueda/', search_type = 'movie' ))

    itemlist.append(item.clone( action = 'calidades', title = 'Por calidad', search_type = 'movie' ))
    itemlist.append(item.clone( action = 'generos', title = 'Por género', search_type = 'movie' ))
    itemlist.append(item.clone( action = 'anios', title = 'Por año', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/public/series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_list', url = host + '/public/torrents/', search_type = 'tvshow', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_list', url = host + '/busqueda/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + '/series-hd/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def mainlist_documentales(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/documentales/', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_list', url = host + '/public/torrents/', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_list', url = host + '/busqueda/', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'documentary' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En Hd', action = 'list_all', url = host + '/peliculas-hd/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 4k', action = 'list_all', url = host + '/peliculas-4k/', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'En 4K', action = 'list_list', url = host + '/peliculas/quality/4k/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En BDremux 1080', action = 'list_list', url = host + '/peliculas/quality/bdremux-1080p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En BluRay 720', action = 'list_list', url = host + '/peliculas/quality/bluray-7200p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En BluRay 1080', action = 'list_list', url = host + '/peliculas/quality/bluray-1080p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En DVDrip', action = 'list_list', url = host + '/peliculas/quality/dvdrip/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En HDrip', action = 'list_list', url = host + '/peliculas/quality/hdrip/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En MIcroHD 720', action = 'list_list', url = host + '/peliculas/quality/microhd-720p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En MicroHD 1080', action = 'list_list', url = host + '/peliculas/quality/microhd-1080p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En Screener', action = 'list_list', url = host + '/peliculas/quality/screener/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En VHSrip', action = 'list_list', url = host + '/peliculas/quality/vhsrip/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En VHSscreener', action = 'list_list', url = host + '/peliculas/quality/vhsscreener/', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
        ('Acción', 'accion'),
        ('Animación', 'animacion'),
        ('Aventuras', 'aventuras'),
        ('Bélica', 'belica'),
        ('Biográfica', 'biografica'),
        ('Ciencia Ficción', 'ciencia-ficcion'),
        ('Cine Negro', 'cine-negro'),
        ('Comedia', 'comedia'),
        ('Crimen', 'crimen'),
        ('Documental', 'documental'),
        ('Drama', 'drama'),
        ('Fantasía', 'fantasia'),
        ('Intriga', 'intriga'),
        ('Músical', 'musical'),
        ('Romántica', 'romantica'),
        ('Suspense', 'suspense'),
        ('Terror', 'terror'),
        ('Thriller', 'thriller'),
        ('Western', 'western')
        ]

    for opc in opciones:
        title = opc[0]
        url = host + '/peliculas/genre/' + opc[1]

        itemlist.append(item.clone( title = title, url = url, action = 'list_list', text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1919, -1):
        url = host + '/peliculas/year/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_list', text_color = 'deepskyblue' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    elif item.search_type == 'tvshow': text_color = 'hotpink'
    else: text_color = 'cyan'

    if item.search_type == 'movie': url_alfa = host + '/peliculas/letter/'
    elif item.search_type == 'tvshow': url_alfa = host + '/series/letter/'
    else: url_alfa = host + '/documentales/letter/'

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
         url = url_alfa + letra.lower() + '/'

         itemlist.append(item.clone( title = letra, action = 'list_list', url = url, text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class=""><span class="bg-mejortorrent-card-(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, 'href="([^"]+)">([^<]+)</a>.*?<b>(.*?)<')

    num_matches = len(matches)

    for url, title, qlty in matches[item.page * perpage:]:
        qlty = qlty.replace('(', '').replace(')', '').strip()

        thumb = scrapertools.find_single_match(data, url + '.*?<img src="(.*?)"')

        url = host + url

        title = title.replace('-', ' ').strip()

        year = '-'
        if '/peliculas/year/' in item.url: year = scrapertools.find_single_match(item.url, "/peliculas/year/(.*?)/")

        if item.search_type == 'movie':
            titulo = title

            if '4K' in titulo: titulo = title.replace('[4K]', '').replace('4K', '').strip()
            elif '3D' in titulo: titulo = title.replace('[3D]', '').replace('3D', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='movie', contentTitle=titulo, infoLabels={'year': year} ))

        elif item.search_type == 'tvshow':
            SerieName = corregir_SerieName(title)

            if SerieName:
                title = title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')

                itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                            contentType='tvshow', contentSerieName=SerieName, infoLabels={'year': year} ))

        else:
            if "(" in title: titulo = title.split("(")[0]
            else: titulo = title

            titulo = titulo.strip()

            itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail=thumb, qualities=qlty,
                                        contentType = 'movie', contentTitle = titulo, contentExtra = 'documentary', infoLabels={'year': year} ))

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
            next_page = scrapertools.find_single_match(data, '<span aria-current="page">.*?<a href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', page = 0, action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def list_list(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '</aside>(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="flex flex-row mb-2">(.*?)</div>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<a href=.*?">.*?>(.*?)<strong>')

        if not url or not title: continue

        qlty = scrapertools.find_single_match(match, '<strong>(.*?)</strong>')

        qlty = qlty.replace ('(', '').replace (')', '').strip()

        year = '-'
        if '/year/' in item.url:
            year = scrapertools.find_single_match(item.url, '/year/(.*?)/')
            if not year: year = '-'

        type = scrapertools.find_single_match(match, 'capitalize">(.*?)</span>')

        if not type == 'peliculas' and not type == 'series' and not type == 'documentales': continue

        if item.search_type != 'all':
            if item.search_type == 'movie':
                if type == 'series': continue
                elif type == 'documentales': continue
            elif item.search_type == 'tvshow':
                if type == 'peliculas': continue
                elif type == 'documentales': continue
            else:
                if not type == 'documentales': continue

        sufijo = ''

        if item.search_type == 'all':
            if type == 'peliculas': sufijo = 'movie'
            elif type == 'series': sufijo = 'tvshow'
            else: sufijo = '[COLOR yellow]Documental[/COLOR]'

        title = title.replace('-', ' ').strip()

        if item.search_type == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            titulo = title

            if '4K' in titulo: titulo = title.replace('[4K]', '').replace('4K', '').strip()
            elif '3D' in titulo: titulo = title.replace('[3D]', '').replace('3D', '').strip()

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, qualities = qlty, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = titulo, infoLabels = {'year': year} ))

        elif item.search_type == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            SerieName = corregir_SerieName(title)

            title = title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')

            itemlist.append(item.clone( action='episodios', url = url, title = title, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels = {'year': year} ))

        else:
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            titulo = title

            if '4K' in titulo: titulo = title.replace('[4K]', '').replace('4K', '').strip()
            elif '3D' in titulo: titulo = title.replace('[3D]', '').replace('3D', '').strip()

            itemlist.append(item.clone( action = 'episodios', url = url, title = title, qualities = qlty, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = titulo, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action='list_list', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<span aria-current="page">.*?<a href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', page = 0, action='list_list', url=next_page, text_color='coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Episodios:(.*?)</tbody>')

    matches = scrapertools.find_multiple_matches(bloque, '<tr wire:(.*?)</tr>')

    tempo = 0

    for match in matches:
        link = scrapertools.find_single_match(match, '<a href="(.*?)"')

        s_e = scrapertools.get_season_and_episode(link)

        try:
           tempo = scrapertools.find_single_match(match, '<td class="px-2 py-1 whitespace-nowrap text-xs text-neutral-800">(.*?)</td>').strip()
           if tempo: tempo = scrapertools.find_single_match(tempo, '(.*?)x')

           if not tempo: tempo = int(s_e.split("x")[0])
        except:
           pass

        if not tempo == 0:
            break

    i = 0

    matches = scrapertools.find_multiple_matches(bloque, '<tr wire:key="episode-(.*?)".*?<a href="(.*?)"')

    for num_epis, url in matches:
        i += 1

        if not tempo == 0:
            season = tempo
            epis = num_epis
        else:
            if 'Cap. ' in str(item.qualities):
               season = scrapertools.find_single_match(str(item.qualities), 'Cap. (.*?)-').strip()
               epis = scrapertools.find_single_match(str(item.qualities), '-(.*?)$').strip()
            else:
               s_e = scrapertools.get_season_and_episode(url)

               try:
                  season = int(s_e.split("x")[0])
                  epis = s_e.split("x")[1]
               except:
                  i += 1
                  season = 0
                  epis = i

        title = str(season) + 'x' + str(i) + ' ' + item.contentSerieName

        if "Temporada" in title: title = title.split("Temporada")[0]
        else: title = title

        try:
            SerieName = title.replace(season + 'x' + episode, '').strip()
        except:
            SerieName = title

        itemlist.append(item.clone( action='findvideos', url = url, title = title,
                                    contentSerieName = SerieName, contentType='episode', contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    lang = 'Esp'

    url = ''

    if item.search_type == 'movie':
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '>Torrent:<.*?<a href="(.*?)"')

        if not url.startswith(host): url = host + url

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = lang, quality = item.qualities ))

        return itemlist

    if not item.url.startswith(host): item.url = host + item.url

    itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = item.url, server = 'torrent', language = lang ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url.endswith('.torrent'):
        if config.get_setting('proxies', item.channel, default=''):
            if PY3:
                from core import requeststools
                data = requeststools.read(item.url, 'mejortorrentapp')
            else:
                data = do_downloadpage(item.url)

            if data:
                if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
                    return 'Archivo [COLOR red]Inexistente[/COLOR]'

                file_local = os.path.join(config.get_data_path(), "temp.torrent")
                with open(file_local, 'wb') as f: f.write(data); f.close()

                itemlist.append(item.clone( url = file_local, server = 'torrent' ))
        else:
            itemlist.append(item.clone( url = item.url, server = 'torrent' ))
    else:
        itemlist.append(item.clone( url = item.url, server = 'torrent' ))

    return itemlist


def corregir_SerieName(SerieName):
    logger.info()

    if "[" in SerieName: SerieName = SerieName.split("[")[0]
    elif "720p" in SerieName: SerieName = SerieName.split("720p")[0]

    if '1ª' in SerieName: SerieName = SerieName.split("1ª")[0]
    if '2ª' in SerieName: SerieName = SerieName.split("2ª")[0]
    if '3ª' in SerieName: SerieName = SerieName.split("3ª")[0]
    if '4ª' in SerieName: SerieName = SerieName.split("4ª")[0]
    if '5ª' in SerieName: SerieName = SerieName.split("5ª")[0]
    if '6ª' in SerieName: SerieName = SerieName.split("6ª")[0]
    if '7ª' in SerieName: SerieName = SerieName.split("7ª")[0]
    if '8ª' in SerieName: SerieName = SerieName.split("8ª")[0]
    if '9ª' in SerieName: SerieName = SerieName.split("9ª")[0]

    if "1 Temporada" in SerieName: SerieName = SerieName.split("1 Temporada")[0]
    elif "2 Temporada" in SerieName: SerieName = SerieName.split("2 Temporada")[0]
    elif "3 Temporada" in SerieName: SerieName = SerieName.split("3 Temporada")[0]
    elif "4 Temporada" in SerieName: SerieName = SerieName.split("4 Temporada")[0]
    elif "5 Temporada" in SerieName: SerieName = SerieName.split("5 Temporada")[0]
    elif "6 Temporada" in SerieName: SerieName = SerieName.split("6 Temporada")[0]
    elif "7 Temporada" in SerieName: SerieName = SerieName.split("6 Temporada")[0]
    elif "8 Temporada" in SerieName: SerieName = SerieName.split("8 Temporada")[0]
    elif "9 Temporada" in SerieName: SerieName = SerieName.split("9 Temporada")[0]
    elif " Temporada" in SerieName: SerieName = SerieName.split(" Temporada")[0]
    elif " - " in SerieName: SerieName = SerieName.split(" - ")[0]

    SerieName = SerieName.strip()

    return SerieName


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/busqueda?q=' + texto.replace(" ", "+")
        return list_list(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
