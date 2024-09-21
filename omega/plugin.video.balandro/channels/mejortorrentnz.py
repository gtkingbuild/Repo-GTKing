# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://www1.mejortorrent.si'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://mejortorrent.nz', 'https://mejortorrent.cc', 'https://mejortorrent.se']


domain = config.get_setting('dominio', 'mejortorrentnz', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'mejortorrentnz')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'mejortorrentnz')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_mejortorrentnz_proxies', default=''):
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
    if config.get_setting('channel_mejortorrentnz_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('mejortorrentnz', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

        if not data:
            if not '/?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('MejorTorrentNz', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('mejortorrentnz', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'mejortorrentnz', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_mejortorrentnz', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='mejortorrentnz', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_mejortorrentnz', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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
    itemlist.append(item.clone( title = 'Documentales', action = 'mainlist_documentales', text_color = 'cyan' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas-13/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + '/peliculas-hd-3/', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/series-3/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + '/series-hd-2/', search_type = 'tvshow' ))

    return itemlist


def mainlist_documentales(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/documentales-3/', search_type = 'documentary' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h1>(.*?)</div></div></div></div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?src="(.*?)"')

    for url, thumb, in matches:
        if not url: continue

        title = url
        title = title.replace(host, '').replace('-', ' ').replace('/', '').strip()
        title = title.capitalize()

        if title == 'Documentales': continue

        title = title.replace('[720p]', '').strip()

        title = title.replace('&#215;', 'x').replace('&#8211;', '').replace("&#8217;", "'")

        titulo = title.split('-')[0].strip()

        if item.search_type == 'tvshow': 
            if '&#' in titulo: titulo = scrapertools.find_single_match(titulo, '(.*?) ')

        title = re.sub(r' \(.*?\)', '', title)

        if item.search_type == 'movie':
            titulo = titulo.replace('-4K', '').replace('4K', '').replace('[HDRip]', '').replace('[BluRay-', '').replace('[MicroHD-', '').replace('[BdRemux-', '').strip()
            titulo = titulo.replace('720p]', '').replace('1080p]', '').strip()

            titulo = titulo.replace('4k', '').replace('hdrip', '').replace('bluray', '').replace('microhd', '').replace('bdremux', '').strip()
            titulo = titulo.replace('720p', '').replace('1080p', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=titulo, infoLabels={'year': '-'} ))

        elif item.search_type == 'tvshow':
            if " Temporada" in title: SerieName = title.split(" Temporada")[0]
            elif " temporada" in title: SerieName = title.split(" temporada")[0]

            else: SerieName = title

            SerieName = SerieName.replace('720p', '').replace('1080p', '').replace('&#8211;', '').strip()

            if SerieName:
                itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                            contentType='tvshow', contentSerieName=SerieName, infoLabels={'year': '-'} ))

        else:
            if "(" in title: titulo = title.split("(")[0]
            else: titulo = title

            titulo = titulo.strip()

            itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail=thumb,
                                        contentType = 'movie', contentTitle = titulo, contentExtra = 'documentary', infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<nav class='page-navigator'" in data:
            next_page = scrapertools.find_single_match(data, "<nav class='page-navigator'.*?href='#'.*?href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    i = 0

    if item.search_type == 'documentary':
         bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')

         matches = scrapertools.find_multiple_matches(bloque, "bgcolor='#C8DAC8'.*?</td>.*?'>(.*?)</td>.*?name='(.*?)'.*?value='(.*?)'")

         for title, id, value in matches:
             title = title.strip()

             title = title.replace('&amp;', 'al')

             if item.grupo == 'selecc': title = title + '  ' + item.title
             else: title = title + ' ' + str(item.contentSerieName)

             i += 1

             itemlist.append(item.clone( action='findvideos', id = id, value = value, ref = item.url, title = title,
                                         contentType='episode', contentSeason = 1, contentEpisodeNumber = i ))

         if matches: return itemlist


    bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')

    matches = scrapertools.find_multiple_matches(bloque, "bgcolor='#C8DAC8'.*?" + '<a href="(.*?)">(.*?)</a>.*?' + "name='(.*?)'.*?value='(.*?)'")

    for url, temp_epis, id, value in matches:
        title = temp_epis.strip()

        if item.name_search:
           if not title.lower() in item.name_search.lower(): continue

        if item.grupo == 'selecc': title = title + '  ' + item.title
        else: title = title + ' ' + str(item.contentSerieName)

        if 'Temporada' in title:
            title = title.split("Temporada")[0]
            title = title.strip()

        tempo = scrapertools.find_single_match(temp_epis, '(.*?)X')

        if ' y ' in temp_epis: epis = scrapertools.find_single_match(temp_epis, 'X(.*?)y').strip()
        else: epis = scrapertools.find_single_match(temp_epis, 'X(.*?)$')

        SerieName = scrapertools.find_single_match(item.contentSerieName, '(.*?)Temporada').strip()

        itemlist.append(item.clone( action='findvideos', id = id, value = value, ref = item.url, title = title,
                                    contentSerieName = SerieName, contentType='episode', contentSeason = tempo, contentEpisodeNumber = epis ))

    bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')

    matches = scrapertools.find_multiple_matches(bloque, "<tr>(.*?)</tr>")

    for match in matches:
        title = scrapertools.find_single_match(match, "<td style='vertical-align: middle;'>(.*?)</td>")

        title = title.replace('&amp;', 'al')

        SerieName = scrapertools.find_single_match(title, '(.*?)Temporada').strip()

        season = scrapertools.find_single_match(title, 'Temporada(.*?)x').strip()
        if not season: season = 1

        epi = scrapertools.find_single_match(title, 'Temporada.*?x(.*?)$').strip()
        if not epi: epi = 1

        url = scrapertools.find_single_match(match, " href='(.*?)'")

        itemlist.append(item.clone( action='findvideos', url = url, title = title,
                                    contentSerieName = SerieName, contentType='episode', contentSeason = season, contentEpisodeNumber = epi ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    url = ''
    data = ''

    lang = 'Esp'

    if item.search_type == 'movie':
        data = do_downloadpage(item.url)
    else:
        if not item.url:
            if not item.id or not item.value: return itemlist

            if item.search_type == 'documentary':
                data = do_downloadpage(item.url)

                id_post = scrapertools.find_single_match(data, '<input type="hidden" value="(.*?)" name="id_post">')
                if id_post: item.value = id_post

            post = {item.id : item.value}

            try:
               vid = host + '/download_tv.php'

               if not vid.startswith(host):
                   resp = httptools.downloadpage(vid, post = post, headers = {'Referer': item.ref}, raise_weberror=False)
               else:
                   if config.get_setting('channel_mejortorrentnz_proxies', default=''):
                       resp = httptools.downloadpage_proxy('mejortorrentnz', vid, post = post, headers = {'Referer': item.ref}, raise_weberror=False)
                   else:
                       resp = httptools.downloadpage(vid, post = post, headers = {'Referer': item.ref}, raise_weberror=False)

               data = resp.data
            except:
               return itemlist

    if item.search_type == 'movie':
        hash = scrapertools.find_single_match(data, '<input type="submit" value="Descargar".*?name="id_post">.*?<input type="hidden".*?value="(.*?)"')
    else:
        hash = scrapertools.find_single_match(data, '<input type="hidden".*?<input type="hidden".*?value="(.*?)"')

    if not hash: hash = scrapertools.find_single_match(data, '<input type="hidden".*?<input type="hidden".*?value="(.*?)"')
    if not hash: hash = scrapertools.find_single_match(data, '<a class="opcion.*?u=(.*?)"')

    if not hash:
        url = scrapertools.find_single_match(data, "<p><a target='_blank'.*?href='(.*?)'")

        if not url:
            if item.url.endswith('.torrent'): url = item.url

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = lang ))

        return itemlist

    qlty = scrapertools.find_single_match(data, "<b>Formato.*?</b>(.*?)<br>").strip()
    qlty = qlty.replace('&nbsp;', '').strip()

    size = scrapertools.find_single_match(data, "<b>Tamaño.*?</b>(.*?)<br>").strip()
    size = size.replace('&nbsp;', '').strip()

    itemlist.append(Item( channel = item.channel, action = 'play', title = '', hash = hash, server = 'torrent', language = lang, quality = qlty, other = size ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url:
        # ~ por si viene de enlaces guardados
        for ant in ant_hosts:
            item.url = item.url.replace(ant, host)

        itemlist.append(item.clone( url = item.url, server = 'torrent' ))
        return itemlist

    domain_memo = config.get_setting('dominio', 'mejortorrentnz', default='')

    if domain_memo: host_player = domain_memo
    else: host_player = host

    if item.hash:
        url = host_player + '/torrent_dmbk.php?u=' + item.hash

        if not url.startswith(host_player):
            resp = httptools.downloadpage(url, headers={'Referer': host_player + '/download_torrent.php'}, follow_redirects=False)
        else:
            if config.get_setting('channel_mejortorrentnz_proxies', default=''):
                resp = httptools.downloadpage_proxy('mejortorrentnz', url, headers={'Referer': host_player + '/download_torrent.php'}, follow_redirects=False)
            else:
                resp = httptools.downloadpage(url, headers={'Referer': host_player + '/download_torrent.php'}, follow_redirects=False)

        link = ''

        if 'location' in resp.headers: link = resp.headers['location']

        if not link:
            return 'Archivo [COLOR plum]No localizado[/COLOR]'

        data = do_downloadpage(link, headers={'Referer': host_player + '/download_torrent.php'})

        url = link

        if PY3:
            from core import requeststools
            data = requeststools.read(url, 'mejortorrentnz')
        else:
            data = do_downloadpage(url)

        if data:
            if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
                return 'Archivo [COLOR red]Inexistente[/COLOR]'

            import os

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'Has realizado una(.*?)</div></div>')

    matches = scrapertools.find_multiple_matches(bloque, "<a href='(.*?)'.*?" + 'class="text-decoration-none">(.*?)</a>.*?<span class="badge badge-primary float-right">(.*?)</span>')

    for url, title, type in matches:
        if not url: continue

        if type == 'Peliculas': pass 
        elif type == 'Series': pass
        elif type == 'Series HD': pass
        elif type == 'Capitulos': pass
        elif type == 'Documentales': pass
        else: continue

        if item.search_type != 'all':
            if item.search_type == 'movie':
                if type == 'Series' or type == 'Series HD' or type == 'Capitulos': continue
                elif type == 'Documentales': continue
            else:
                if type == 'Peliculas': continue
                elif type == 'Documentales': continue

        sufijo = ''

        search_type = item.search_type

        if item.search_type == 'all':
            if type == 'Peliculas':
               search_type = 'movie'
               sufijo = 'movie'
            elif type == 'Series' or type == 'Series HD' or type == 'Capitulos':
               search_type = 'tvshow'
               sufijo = 'tvshow'
            else:
               sufijo = '[COLOR cyan]Documental[/COLOR]'
               search_type = 'documentary'

        title = title.replace("<font Color='darkblue'>", '').replace('</font>', '').replace("<span style='color:gray;'>", '').replace('</span>', '').strip()
        title = title.replace('[720p]', '').strip()
        title = title.replace('&#215;', 'x')

        titulo = title.split('-')[0].strip()
        title = re.sub(r' \(.*?\)', '', title)

        if type == 'Capitulos': name_search = titulo
        else: name_search = ''

        if search_type == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            titulo = titulo.replace('4K', '').replace('[HDRip]', '').replace('[BluRay', '').replace('[MicroHD', '').strip()

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, fmt_sufijo = sufijo,
                                        search_type = search_type, contentType = 'movie', contentTitle = titulo, infoLabels = {'year': '-'} ))

        if search_type == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            title = title.replace(' &#8211;', '').strip()

            if " Temporada" in title: SerieName = title.split(" Temporada")[0]
            else: SerieName = title

            itemlist.append(item.clone( action='episodios', url = url, title = title, fmt_sufijo = sufijo, name_search = name_search,
                                        search_type = search_type, contentType = 'tvshow', contentSerieName = SerieName, infoLabels = {'year': '-'} ))

        if item.search_type == 'documentary':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            titulo = title

            titulo = titulo.replace('4K', '').replace('[HDRip]', '').replace('[BluRay', '').replace('[MicroHD', '').strip()

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, fmt_sufijo = sufijo,
                                        search_type = search_type, contentType = 'movie', contentTitle = titulo, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<nav class='page-navigator'" in data:
            next_page = scrapertools.find_single_match(data, "<nav class='page-navigator'.*?href='#'.*?href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', action='list_search', url=next_page, text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
