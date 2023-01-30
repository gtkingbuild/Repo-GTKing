# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, os, base64

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

from lib import decrypters


host = 'https://www2.ditorrent.com/'


# ~  12/2022 las series Ssin Temporadas y Episodios


# ~ por si viene de enlaces guardados
ant_hosts = ['http://www.torrentdivx.net/', 'https://www.torrentdivx.com/', 'https://www.ditorrent.com/',
             'https://www1.ditorrent.com/']


domain = config.get_setting('dominio', 'torrentdivx', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'torrentdivx')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'torrentdivx')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_torrentdivx_proxies', default=''):
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

    if '/release/' in url: raise_weberror = False

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('torrentdivx', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                data = httptools.downloadpage_proxy('torrentdivx', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        except:
            pass

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'torrentdivx', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_torrentdivx', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='torrentdivx', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_torrentdivx', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'tag/estreno/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tvshows/', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Castellano', action='list_all', url=host + 'tag/castellano/' ))
    itemlist.append(item.clone( title='Latino', action='list_all', url=host + 'tag/latino/' ))
    itemlist.append(item.clone( title='Subtitulado', action='list_all', url=host + 'tag/subtitulado/' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='En Magnet', action='list_all', url=host + 'tag/magnet/', search_type = 'movie' ))
    itemlist.append(item.clone( title='En Torrent', action='list_all', url=host + 'tag/torrent/', search_type = 'movie' ))

    itemlist.append(item.clone( title='En HdRip', action='list_all', url=host + 'tag/hdrip/', search_type = 'movie' ))
    itemlist.append(item.clone( title='En 720p', action='list_all', url=host + 'tag/720p/', search_type = 'movie' ))
    itemlist.append(item.clone( title='En 1080p', action='list_all', url=host + 'tag/1080p/', search_type = 'movie' ))
    itemlist.append(item.clone( title='En 4K', action='list_all', url=host + 'tag/4k/', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'tag/estreno/')

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == 'Próximos Estrenos': continue
        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( action = 'list_all', title = title.capitalize(), url = url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        url = host + 'release/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '</span></a></div></div>' in data:
        bloque = scrapertools.find_single_match(data, '<h2>Añadido(.*?)</span></a></div></div>')
        if not bloque: bloque = scrapertools.find_single_match(data, '(.*?)</span></a></div></div>')
    else:
        bloque = scrapertools.find_single_match(data, '(.*?)>TMDB PROMEDIO<')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, '<img src="(.*?)"')

        year = scrapertools.find_single_match(article, '</span> <span>(.*?)</span>').strip()

        if year: title = title.replace('(%s)' % year, '').strip()
        else:  year = '-'

        plot = scrapertools.find_single_match(article, '<p>(.*?)</p>')

        tipo = 'tvshow' if '/tvshows/' in url else 'movie'

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            qlty = scrapertools.find_single_match(article, '<span class="quality">(.*?)</span>')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            title = title.replace('Completa', '').strip()
			
            SerieName = title

            if 'Todas Las Temporadas' in title: SerieName = title.split("Todas Las")[0]
            if 'Todas las Temporadas' in title: SerieName = title.split("Todas")[0]
            if 'Temporada' in title: SerieName = title.split("Temporada")[0]
            if 'temporada' in title: SerieName = title.split("temporada")[0]

            SerieName = SerieName.strip()

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=SerieName, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?<a href="(.*?)"')
        if not next_page: next_page = scrapertools.find_single_match(data, '<span class="current">.*?' + "<a href='(.*?)'")

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile("<span class='se-t.*?'>(.*?)</span>", re.DOTALL).findall(data)

    for tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + '(.*?)</div></div>')

    bloque = str(bloque).replace("\'", '"')

    matches = re.compile('<li class="mark-(.*?)</div></li>', re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('TorrentDivx', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TorrentDivx', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TorrentDivx', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TorrentDivx', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('TorrentDivx', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for article in matches[item.page * item.perpage:]:
        thumb = scrapertools.find_single_match(article, '<img src="(.*?)"')

        url = scrapertools.find_single_match(article, ' href="([^"]+)"')

        s_e = scrapertools.find_single_match(url, 'temporada-(\d+).*?episodio-(\d+)')
        if not s_e: continue

        title = scrapertools.find_single_match(article, 'href=".*?>(.*?)</a>').strip()

        titulo = '%sx%s %s' % (s_e[0], s_e[1], title)

        itemlist.append(item.clone( action='findvideos', title = titulo, url = url, thumbnail=thumb,
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

    orden = ['cam',
          'ts',
          'webdl',
          'webrip',
          'bdscr',
          'hdtv',
          'hc720p',
          'bdrip',
          'dvdrip',
          'hdrip',
          '720p',
          'hd720p',
          '1080p',
          'fullhd',
          'hd1080p',
          'hd2160p',
          '2160p',
          '4khd2160p',
          '4k']

    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'V.O. Subtitulado': 'Vose', 'Version Original': 'VO',
               'Subtitulo Español': 'Vose', 'Version Original +Sub': 'VOS', 'Latino - Varios': 'Varios', 'Español latino': 'Lat'}

    data = do_downloadpage(item.url)

    link = scrapertools.find_single_match(data, "id='link-.*?<a href='(.*?)'")

    bloque = scrapertools.find_single_match(data, "<div class='links_table'>(.*?)</table>")

    matches = scrapertools.find_multiple_matches(bloque, '<tr(.*?)</tr>')

    ses = 0

    for enlace in matches:
        ses += 1

        if '<th' in enlace or 'torrent' not in enlace: continue
        if "id='link-fake'" in enlace: continue

        url = scrapertools.find_single_match(enlace, " href='([^']+)")
        if not url: continue

        if '&url=' in url:
            url = scrapertools.find_single_match(url, "&url=(.*?)$")

        if url == 'https://adfly.mobi/directlinkg': url = link

        tds = scrapertools.find_multiple_matches(enlace, '<td>(.*?)</td>')
        qlty = scrapertools.find_single_match(tds[1], "<strong class='quality'>([^<]+)")
        lang = tds[2]

        other = tds[3] if tds[3] != '----' else ''
        if other == 'No Aplica': other = '?'

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'torrent', title = '', url = url,
                              language = IDIOMAS.get(lang,lang), quality = qlty, quality_num = puntuar_calidad(qlty), other = other ))

    if len(itemlist) == 0:
        matches = scrapertools.find_multiple_matches(data, ' href="(magnet[^"]+)')
        for url in matches:
            itemlist.append(Item( channel = item.channel, action = 'play', server = 'torrent', title = '', url = url ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if '&urlb64=' in item.url:
        urlb64 = scrapertools.find_single_match(item.url, '&urlb64=(.*?)$')

        urlb64 = base64.b64decode(urlb64).decode('utf-8')

        if '/links/' in urlb64:
            resp = httptools.downloadpage(urlb64, follow_redirects=False, only_headers=True)
		
            if 'location' in resp.headers: url = resp.headers['location']
        else:
            data = do_downloadpage(urlb64)

            url = scrapertools.find_single_match(data, '<a id="link".*?href="(.*?)"')

        if url: item.url = url

    if item.url.startswith(host) and '/links/' in item.url:
        # ~ resp = httptools.downloadpage(item.url, follow_redirects = False, only_headers = True)
        resp = httptools.downloadpage_proxy('torrentdivx', item.url, follow_redirects = False, only_headers = True)

        url = ''

        if 'location' in resp.headers: url = resp.headers['location']

        if not url:
             data = do_downloadpage(item.url)

             url = scrapertools.find_single_match(data, '<a id="link" rel="nofollow" href="([^"]+)')

             if '/www.pastexts' in url or '/tmearn' in url or '/sturl' in url or '/uii' in url or '/down.fast-' in url or '/adshort' in url or '/passgen' in url or '/adfly.' in url:
                 return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        if url.startswith('magnet:') or url.endswith('.torrent'):
            if config.get_setting('proxies', item.channel, default=''):
                if PY3:
                    from core import requeststools
                    data = requeststools.read(url, 'torrentdivx')
                else:
                    data = do_downloadpage(url)

                if data:
                    import os

                    file_local = os.path.join(config.get_data_path(), "temp.torrent")
                    with open(file_local, 'wb') as f: f.write(data); f.close()

                    itemlist.append(item.clone( url = file_local, server = 'torrent' ))
            else:
                itemlist.append(item.clone( url = url, server = 'torrent' ))

            return itemlist

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor and servidor != 'directo':
                itemlist.append(item.clone( url = url, server = servidor ))

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith(".torrent"):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    else:
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(item.url, host_torrent)

        if url_base64.endswith('.torrent'): item.url = url_base64

    if item.url.endswith('.torrent'):
        if PY3:
            from core import requeststools
            data = requeststools.read(item.url, 'torrentdivx')
        else:
            data = do_downloadpage(item.url)

        if data:
            try:
               if 'Página no encontrada</title>' in str(data):
                   platformtools.dialog_ok('DivxTotal', '[COLOR yellow]Archivo no encontrado[/COLOR]')
                   return itemlist
            except:
               pass

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))


    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h1>Resultados encontrados(.*?)<h3>')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        if year:
            if ('(' + year + ')') in title: title = title.replace('(' + year + ')', '').strip()

        tipo = 'tvshow' if '/tvshows/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            title = title.replace('Completa', '').strip()

            SerieName = title

            if 'Todas Las Temporadas' in title: SerieName = title.split("Todas Las")[0]
            if 'Todas las Temporadas' in title: SerieName = title.split("Todas las")[0]
            if 'Temporada' in title: SerieName = title.split("Temporada")[0]
            if 'temporada' in title: SerieName = title.split("temporada")[0]

            SerieName = SerieName.strip()

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=SerieName, infoLabels={'year': year} ))

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
