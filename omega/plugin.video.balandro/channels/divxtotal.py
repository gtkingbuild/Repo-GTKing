# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import re, os

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://www2.divxtotal.mov/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://www.divxtotal.re/', 'https://www.divxtotal.ac/', 'https://www.divxtotal.dev/',
             'https://www.divxtotal.ms/', 'https://www.divxtotal.fi/', 'https://www.divxtotal.cat/',
             'https://www.divxtotal.pl/', 'https://www.divxtotal.wf/', 'https://www.divxtotal.win/',
             'https://www1.divxtotal.zip/', 'https://www2.divxtotal.zip/']


domain = config.get_setting('dominio', 'divxtotal', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'divxtotal')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'divxtotal')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_divxtotal_proxies', default=''):
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
    if config.get_setting('channel_divxtotal_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('divxtotal', url, post=post, headers=headers).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers).data

        if not data:
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('DivxTotal', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('divxtotal', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'divxtotal', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_divxtotal', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='divxtotal', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_divxtotal', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados ó bloqueos Play)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados ó bloqueos Play)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host, group = 'lasts', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Españolas', action = 'list_all', url = host + 'peliculas/?category_name=espanolas', search_type = 'movie', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie', tipo = 'genero' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados ó bloqueos Play)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series-5/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host, group = 'lasts', search_type = 'tvshow', text_color='cyan' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En DVDR', action = 'list_all', url = host + 'peliculas-dvdr/', search_type = 'movie', text_color = 'moccasin' ))
    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'peliculas-hd-5/', search_type = 'movie', text_color = 'moccasin' ))
    itemlist.append(item.clone( title = 'En 3D', action = 'list_all', url = host + 'peliculas-3-d/', search_type = 'movie', text_color = 'moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'peliculas/')

    bloque = scrapertools.find_single_match(data, '<div id="bloque_cat"(.*?)</div>')

    matches = scrapertools.find_multiple_matches(bloque, "href='(.*?)'.*?'>(.*?)</button>")

    for url, title in matches:
        if title == 'Españolas': continue

        if config.get_setting('descartar_anime', default=False):
            if title == 'Anime': continue

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')
    if not bloque:
        if item.search_type == 'tvshow': bloque = data

    if item.group == 'lasts':
        if item.search_type == 'movie': bloque = scrapertools.find_single_match(data, '>Películas</h3>(.*?)>Series</h3>')
        else: bloque = scrapertools.find_single_match(data, '>Series</h3>(.*?)>Programas</h3>')

    matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?)</tr>')
    if not matches:
        if item.search_type == 'tvshow': matches = scrapertools.find_multiple_matches(bloque, '<div class="col-lg-3 col-md-3 col-md-4 col-xs-6">(.*?)</div>')

    if not matches:
        if item.group == 'lasts': matches = scrapertools.find_multiple_matches(bloque, '<div class="row">(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        if not url: url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        if not host in url: continue

        tipo = 'movie' if '/peliculas/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        title = title.replace('- pelicula torrent', '').strip()
        title = title.replace("&#8217;", "'").replace("&#8230;", ':').replace("&#8211;", ':')

        titulo = title

        titulo = titulo.replace('(720)', '').replace('(720p)', '').replace('(1080)', '').replace('(1080p)', '').replace('(microHD)', '').replace('(BR-Line)', '').strip()
        titulo = titulo.replace('(HDR)', '').replace('(HDRip)', '').replace('(DVDRip)', '').replace('(BR-SCREENER)', '').replace('(TS-SCREENER)', '').replace('(3D)', '').strip()
        titulo = titulo.replace('4K', '').replace('4k', '').replace('(DUAL)', '').replace('[ES-EN]', '').strip()

        thumb = scrapertools.find_single_match(match, "'(.*?)'")

        tipo = 'movie' if '/peliculas/' in url or '/peliculas-' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            if "(" in titulo: titulo = titulo.split("(")[0]

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=titulo, infoLabels={'year': "-" } ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            titulo = titulo.replace(' - serie', '').strip()

            if " - " in titulo: SerieName = titulo.split(" - ")[0]
            else: SerieName = titulo

            itemlist.append(item.clone( action='temporadas', url=url, title=titulo, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': "-" } ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<ul class="pagination">.*?</span></a></li><li>' + "<a href='(.*?)'")

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('class="titulotemporada".*?">(.*?)</a>', re.DOTALL).findall(data)

    for tempo in temporadas:
        tempo = tempo.replace('Temporada', '').strip()

        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '">Temporada ' + str(item.contentSeason) + '</a>(.*?)</tbody>')
    if not bloque: bloque = scrapertools.find_single_match(data, '">Temporada ' + str(item.contentSeason) + '</a>(.*?)</div></div>')

    i = 0

    matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?)</tr>')

    for match in matches:
        title = scrapertools.find_single_match(match, 'title="">(.*?)</a>')
        if not title: title = scrapertools.find_single_match(match, '<a href=.*?title="(.*?)"')

        if not title: continue

        s_e = scrapertools.get_season_and_episode(title)

        try:
           season = int(s_e.split("x")[0])
           episode = s_e.split("x")[1]
        except:
           i += 1
           season = 0
           episode = i

        title = '%sx%s %s' % (str(item.contentSeason), episode, item.contentSerieName)

        itemlist.append(item.clone( action='findvideos', url=match, title=title, match=match,
                                    language = 'Esp', contentSeason = item.contentSeason, contentType = 'episode', contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.match: data = item.match
    else: data = do_downloadpage(item.url)

    lang = ''

    if '<p>Español</p>' in data: lang = 'Esp'
    elif '<p>Latino</p>' in data: lang = 'Lat'
    elif '<p>Ingles</p>' in data: lang = 'VO'
    elif '<p>subtitulado</p>' in data: lang = 'Vose'
    else:
       idioma = scrapertools.find_single_match(data, '<td>.*?<img src=".*?/images/(.*?).png')
       if not idioma: idioma = scrapertools.find_single_match(data, '<td.*?<img src=".*?/images/(.*?).png')

       if idioma == 'ES': lang = 'Esp'
       elif idioma == 'LA': lang = 'Lat'
       elif idioma == 'EN': lang = 'VO'

    qlty = scrapertools.find_single_match(data, '>Formato:.*?<p>(.*?)</p>')

    if item.url.endswith('.torrent'):
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = item.url, server = 'torrent', language = lang, quality = qlty))
        return itemlist

    link1 = scrapertools.find_multiple_matches(data, 'class="linktorrent".*?href="(.*?)"')

    link2 = scrapertools.find_multiple_matches(data, 'class="opcion_2".*?href="(.*?)"')

    link3 =  scrapertools.find_multiple_matches(data, 'class="linktorrent".*?data-src="(.*?)"')

    links = link1 + link2 + link3

    ses = 0

    for link in links:
        ses += 1

        if link.startswith('??'): continue

        other = ''
        if not link.startswith('http'):
            if link.startswith('/'): link = host[:-1] + link
            other = 'Directo'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = link, server = 'torrent', language = lang, quality = qlty, other = other))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.other == 'Directo':
        item.url = host + 'download_tt.php?u=' + item.url

        if PY3:
            from core import requeststools
            data = requeststools.read(item.url, 'divxtotal')
        else:
            data = do_downloadpage(item.url)

        if data:
            try:
               if 'Página no encontrada</title>' in str(data) or 'no encontrada</title>' in str(data) or '<h1>403 Forbidden</h1>' in str(data):
                   return 'Archivo [COLOR red]No encontrado[/COLOR]'
               elif '<p>Por causas ajenas a ' in str(data):
                   if not config.get_setting('proxies', item.channel, default=''):
                       return 'Archivo [COLOR red]bloqueado[/COLOR] [COLOR yellow]Configure proxies a usar ...[/COLOR]'

                   return 'Archivo [COLOR red]bloqueado[/COLOR]'
            except:
               pass

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))

        return itemlist

    if not item.url.endswith('.torrent'):
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(item.url, host_torrent)

        if url_base64.endswith('.torrent'): item.url = url_base64

    if item.url.endswith('.torrent'):
        if PY3:
            from core import requeststools
            data = requeststools.read(item.url, 'divxtotal')
        else:
            data = do_downloadpage(item.url)

        if data:
            try:
               if 'Página no encontrada</title>' in str(data) or 'no encontrada</title>' in str(data) or '<h1>403 Forbidden</h1>' in str(data):
                   return 'Archivo [COLOR red]No encontrado[/COLOR]'
               elif '<p>Por causas ajenas a ' in str(data):
                   if not config.get_setting('proxies', item.channel, default=''):
                       return 'Archivo [COLOR red]bloqueado[/COLOR] [COLOR yellow]Configure proxies a usar ...[/COLOR]'

                   return 'Archivo [COLOR red]bloqueado[/COLOR]'
            except:
               pass

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))

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
