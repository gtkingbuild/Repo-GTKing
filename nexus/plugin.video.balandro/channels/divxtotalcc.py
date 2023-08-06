# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import re, os

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://www.divxtotal.cc/'


host_play = 'https://www.divxtotal.cat/'


# ~ 11/2022 Para play en peliculas necesita proxies por bloqueo operadoras


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_divxtotalcc_proxies', default=''):
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
    if not url.startswith(host) and not url.startswith(host_play):
        data = httptools.downloadpage(url, post=post, headers=headers).data
    else:
        data = httptools.downloadpage_proxy('divxtotalcc', url, post=post, headers=headers).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='divxtotalcc', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados ó bloqueo Play)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados ó bloqueo Play)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host, group = 'lasts', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Españolas', action = 'list_all', url = host + 'peliculas/?category_name=espanolas', search_type = 'movie', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie', tipo = 'genero' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados ó bloqueo Play)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host, group = 'lasts', search_type = 'tvshow' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En DVDR', action = 'list_all', url = host + 'peliculas-dvdr/', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'peliculas-hd/', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 3D', action = 'list_all', url = host + 'peliculas-3d/', search_type = 'movie', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Todas<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == 'Españolas': continue

        url = host[:-1] + url

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

    if not bloque:
        if item.group == 'lasts':
            if item.search_type == 'movie': bloque = scrapertools.find_single_match(data, '<div class="panel panel-default peliculas-bloque bloque-home">(.*?)>Series</h2>')
            else: bloque = scrapertools.find_single_match(data, '>Series</h2>(.*?)>Programas</h3>')

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

        url = host[:-1] + url

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

            titulo = titulo.replace(' - serie', '').strip()

            if " - " in titulo: SerieName = titulo.split(" - ")[0]
            else: SerieName = titulo

            itemlist.append(item.clone( action='temporadas', url=url, title=titulo, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': "-" } ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<ul class="pagination">.*?</span></a></li></li>.*?href="(.*?)"')

        if next_url:
            if '/page/' in next_url:
                next_url = host[:-1] + next_url

                itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    seasons = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('class="titulotemporada".*?">(.*?)</a>', re.DOTALL).findall(data)

    for tempo in temporadas:
        tempo = tempo.replace('Temporada', '').strip()

        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        if not tempo in str(seasons):
           seasons.append(['Season: ' + tempo])

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

    matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?)</tr>')

    i = 0

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

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if url.startswith('/'): url = host[:-1] + url

        itemlist.append(item.clone( action='findvideos', url=url, title=title, match=match,
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

    link1 = scrapertools.find_multiple_matches(data, 'class="linktorrent".*?.*?href="(.*?)"')

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
        if not item.url.endswith('.torrent'):
            item.url = host_play + 'download_tt.php?u=' + item.url

            if PY3:
                from core import requeststools
                data = requeststools.read(item.url, 'divxtotalcc')
            else:
                data = do_downloadpage(item.url)

            if data:
                try:
                   if 'Página no encontrada</title>' in str(data) or 'no encontrada</title>' in str(data) or '<h1>403 Forbidden</h1>' in str(data):
                       return 'Archivo [COLOR red]No encontrado[/COLOR]'
                   elif '<p>Por causas ajenas a ' in str(data):
                       if not config.get_setting('proxies', item.channel, default=''):
                           return 'Archivo [COLOR cyan]bloqueado[/COLOR] [COLOR red]Configure los proxies[/COLOR]'

                       return 'Archivo [COLOR red]bloqueado[/COLOR]'
                except:
                   pass

                file_local = os.path.join(config.get_data_path(), "temp.torrent")
                with open(file_local, 'wb') as f: f.write(data); f.close()

                itemlist.append(item.clone( url = file_local, server = 'torrent' ))

            return itemlist

    if not item.url.endswith('.torrent'):
        host_torrent = host_play[:-1]
        url_base64 = decrypters.decode_url_base64(item.url, host_torrent)

        if url_base64.endswith('.torrent'): item.url = url_base64

    if item.url.endswith('.torrent'):
        if PY3:
            from core import requeststools
            data = requeststools.read(item.url, 'divxtotalcc')
        else:
            data = do_downloadpage(item.url)

        if data:
            try:
               if 'Página no encontrada</title>' in str(data) or 'no encontrada</title>' in str(data) or '<h1>403 Forbidden</h1>' in str(data):
                   return 'Archivo [COLOR red]No encontrado[/COLOR]'
               elif '<p>Por causas ajenas a ' in str(data):
                   if not config.get_setting('proxies', item.channel, default=''):
                       return 'Archivo [COLOR cyan]bloqueado[/COLOR] [COLOR red]Configure los proxies[/COLOR]'

                   return 'Archivo [COLOR cyan]bloqueado[/COLOR]'
            except:
               pass

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?q=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
