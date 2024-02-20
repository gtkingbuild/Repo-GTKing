# -*- coding: utf-8 -*-

import re, random

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools, tmdb

from lib import decrypters


host = 'https://yestorrent.org/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://yestorrent.cx/', 'http://yestorrent.org/']

domain = config.get_setting('dominio', 'yestorrent', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'yestorrent')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'yestorrent')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_yestorrent_proxies', default=''):
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


def do_downloadpage(url, post=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    if '/years/' in url: raise_weberror = False

    hay_proxies = False
    if config.get_setting('channel_yestorrent_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, raise_weberror=raise_weberror).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('yestorrent', url, post=post, raise_weberror=raise_weberror).data
        else:
            data = httptools.downloadpage(url, post=post, raise_weberror=raise_weberror).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'yestorrent', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_yestorrent', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='yestorrent', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_yestorrent', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'descargar-peliculas-completas-y002/', search_type = 'movie' ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Castellano', action='list_all', url=host + 'language/castellano/', text_color='moccasin' ))
    itemlist.append(item.clone( title='Latino', action='list_all', url=host + 'language/latino/', text_color='moccasin' ))
    itemlist.append(item.clone( title='Subtitulado', action='list_all', url=host + 'language/subtitulado/', text_color='moccasin' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='En 3D', url = host + 'quality/3d/', action='list_all', text_color='moccasin' ))
    itemlist.append(item.clone( title='En 4K UHD', url = host + 'quality/4k-uhd/', action='list_all', text_color='moccasin' ))

    itemlist.append(item.clone( title='En BD Rip', url = host + 'quality/bdrip/', action='list_all', text_color='moccasin' ))
    itemlist.append(item.clone( title='En BluRay 720', url = host + 'quality/bluRay-720p/', action='list_all', text_color='moccasin' ))
    itemlist.append(item.clone( title='En BluRay 1080', url = host + 'quality/bluRay-1080p/', action='list_all', text_color='moccasin' ))

    itemlist.append(item.clone( title='En Dual 1080', url = host + 'quality/dual-1080p/', action='list_all', text_color='moccasin' ))

    itemlist.append(item.clone( title='En HD', url = host + 'quality/hd/', action='list_all', text_color='moccasin' ))

    itemlist.append(item.clone( title='En Micro HD', url = host + 'quality/MicroHD-1080p/', action='list_all', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data,'>Genero<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque,'<a href="(.*?)".*?>(.*?)</a>')

    for url, tit in matches:
        if not url or not tit: continue

        if not '/category/' in url: continue

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    if itemlist:
        itemlist.append(item.clone( action = 'list_all', title = 'Bélica', url = host + 'category/belica/', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( action = 'list_all', title = 'Documental', url = host + 'category/documental/', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( action = 'list_all', title = 'Historia', url = host + 'category/historia/', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( action = 'list_all', title = 'Western', url = host + 'category/western/', text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1965, -1):
        url = host + 'years/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="col-6 col-sm-4 col-lg-3 col-xl-2">(.*?)<span class="card__rate">', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="([^"]+)')
        title = scrapertools.find_single_match(match, ' alt="([^"]+)')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="([^"]+)')
        qlty = scrapertools.find_single_match(match, '<li>(.*?)</li>').strip()

        lang = scrapertools.find_single_match(match, '</ul>.*?<li>(.*?)</li>').strip()
        if lang == 'Cas': lang = 'Esp'
        elif lang == 'Lat': lang = 'Lat'
        elif lang == 'Sub': lang = 'Vose'
        elif lang == 'VO': lang = 'VO'

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, languages=lang, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')

        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('data-target="#collapse-.*?<span>(.*?)</span>', re.DOTALL).findall(data)

    for title in matches:
        numtempo = title.replace('Temporada ', '').strip()

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.title = title
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

    bloque = scrapertools.find_single_match(data, '<span>' + str(item.title) + '</span>(.*?)</tbody>')

    matches = re.compile('data-season="(.*?)".*?data-serie="(.*?)".*?href="(.*?)"', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('YesTorrent', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('YesTorrent', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('YesTorrent', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('YesTorrent', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('YesTorrent', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('YesTorrent', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for season, episode, url in matches[item.page * item.perpage:]:
        if item.contentSeason:
           if not str(item.contentSeason) == season: continue

        titulo = '%sx%s %s' % (season, episode, item.contentSerieName)

        itemlist.append(item.clone( action='findvideos', title = titulo, url = url, contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<tbody>(.*?)</tbody>', re.DOTALL).findall(data)

    ses = 0

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, ' href="([^"]+)')

        if url:
            qlty = scrapertools.find_single_match(match, '<td>(.*?)</td>')
            if '<b>Notice</b>' in qlty: qlty = ''

            lang = scrapertools.find_single_match(match, '</td>.*?<td>(.*?)</td>')
            if lang == 'Castellano': lang = 'Esp'
            elif lang == 'Latino': lang = 'Lat'
            elif lang == 'Subtitulado': lang = 'Vose'
            elif lang == 'Version Original': lang = 'VO'

            peso = scrapertools.find_single_match(match, '<td class="hide-on-mobile">.*?<td class="hide-on-mobile">(.*?)</td>')

            servidor = 'torrent'
            srv = ''

            if url.endswith(".torrent"): pass
            elif url.startswith('magnet:'): srv = 'magnet'
            else:
                servidor = 'directo'
                if '/acortalink.me/' in url: srv = 'torrent'
                elif '/mega.' in url: srv = 'mega'
                else:
                    srv = servertools.get_server_from_url(url)
                    srv = servertools.corregir_servidor(srv)

            other = peso + ' ' + srv

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, quality = qlty, other = other ))

    if not itemlist:
       url = ''

       servidor = 'torrent'
       other = ''

       if item.url.endswith(".torrent"): url = item.url
       elif item.url.startswith('magnet:'):
          url = item.url
          other = 'magnet'
       else:
           servidor = 'directo'
           if '/acortalink.me/' in item.url:
              url = item.url
              other = 'torrent'
           elif '/mega.' in item.url:
              url = item.url
              other = 'mega'
           else:
              other = servertools.get_server_from_url(item.url)
              other = servertools.corregir_servidor(other)

       if url:
           itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.server == 'torrent':
        itemlist.append(item.clone( url = item.url, server = 'torrent' ))
    else:
        if 'magnet' in item.other:
            itemlist.append(item.clone( url = item.url, server = 'torrent' ))
            return itemlist

        if 'mega' in item.other:
            url = item.url.replace('/file/', '/embed#!')

            try:
                url_id = url.split('#')[1]
                file_id = url_id.split('!')[1]
            except:
                file_id = ''

            if file_id:
                get = ''
                post = {'a': 'g', 'g': 1, 'p': file_id}

                if '/#F!' in url:
                    get = '&n=' + file_id
                    post = {'a': 'f', 'c': 1, 'r': 0}
 
                nro = random.randint(0, 0xFFFFFFFF)

                api = 'https://g.api.mega.co.nz/cs?id=%d%s' % (nro, get)

                resp = httptools.downloadpage(api, post=jsontools.dump([post]), headers={'Referer': 'https://mega.nz/'})

                url = scrapertools.find_single_match(resp.data, '.*?"g":"(.*?)"')
                if url:
                    if url.endswith(".torrent"):
                        itemlist.append(item.clone( url = url, server = 'torrent' ))
                    return itemlist

        servidor = servertools.get_server_from_url(item.url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, item.url)

        if servidor and servidor != 'directo':
            itemlist.append(item.clone( url = url, server = servidor ))
            return itemlist

        if servidor == 'directo':
            host_torrent = host[:-1]
            url_base64 = decrypters.decode_url_base64(url, host_torrent)

            if url_base64.startswith('magnet:'):
               itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

            elif url_base64.endswith(".torrent"):
               itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'buscar/?buscar=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
