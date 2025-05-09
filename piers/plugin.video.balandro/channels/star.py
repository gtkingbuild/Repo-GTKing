# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.ver-online.info/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_star_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar[/B] ...', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www.ver-online.cc/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if '/series-gratis/año/' in url: raise_weberror = False

    hay_proxies = False
    if config.get_setting('channel_star_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('star', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

        if not data:
            if not 'recherche?q=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('Star', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('star', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='star', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series-gratis.html', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?>(.*?)</a>')

    for url, title in matches:
        title = title.replace('&amp;', '&').strip()

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, genre = title, text_color = 'hotpink' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1954, -1):
        url = host + 'series-gratis/año/' + str(x) + '.html'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', text_color='hotpink' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
        url = host + 'series-gratis/ordenadas/' + letra

        itemlist.append(item.clone ( title = letra, url = url, action = 'list_all', text_color = 'hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<span>Ver-online.cc</span>(.*?)>mas vistas<')

    if not bloque: bloque = scrapertools.find_single_match(data, '<span>ver-online.cc</span>(.*?)>mas vistas<')

    if not bloque: bloque = scrapertools.find_single_match(data, '<span>ver-online</span>(.*?)>mas vistas<')
    if not bloque: bloque = scrapertools.find_single_match(data, '<span>Ver-online</span>(.*?)>mas vistas<')

    if not bloque: bloque = scrapertools.find_single_match(data, '<span>ver-online.*?</span>(.*?)>mas vistas<')
    if not bloque: bloque = scrapertools.find_single_match(data, '<span>Ver-online.*?</span>(.*?)>mas vistas<')

    if not bloque: bloque = scrapertools.find_single_match(data, '<span>Veronline.(.*?)>mas vistas<')

    if not bloque: bloque = scrapertools.find_single_match(data, '<span>veronline.(.*?)>mas vistas<')

    if not bloque: bloque = scrapertools.find_single_match(data, '<span>veronline(.*?)>mas vistas<')
    if not bloque: bloque = scrapertools.find_single_match(data, '<span>Veronline(.*?)>mas vistas<')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="shortstory-in">(.*?)</div></div></div>')

    for match in matches:
        title =  scrapertools.find_single_match(match, 'title="(.*?)"')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        title = title.replace('online gratis', '').replace('&#039;', "'").replace('&amp;', '&').strip()

        year = '-'
        if '/series-gratis/año/' in item.url:
            year = scrapertools.find_single_match(item.url, "/series-gratis/año/(.*?)$")
            if year:
               year = year.replace('.html', '')

               if '/page-' in year: year = scrapertools.find_single_match(year, "(.*?)/page-")

        if not year: year = '-'
        itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb,
                                    contentType='tvshow', contentSerieName=title,  infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="pages-numbers">.*?</a>.*?</div>.*?href="(.*?)"')

        if next_page:
            if '/page-' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, '>Nuevos Capítulos(.*?)>Nuevos Temporadas')

    matches = scrapertools.find_multiple_matches(bloque, '<li>(.*?)</li>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, '<a href=".*?">(.*?)<span>')

        if not url or not title: continue

        title = title.replace('&#039;', "'").replace('&amp;', '&')

        SerieName = scrapertools.find_single_match(title, '(.*?)- T').strip()

        season = scrapertools.find_single_match(title, '- T(.*?)Capítulo').strip()

        if not season: season = 1

        epis = scrapertools.find_single_match(title, 'Capítulo(.*?)$').strip()

        if not epis: epis = 1

        title = title.replace(' T ', '[COLOR tan]Temp.[/COLOR]')

        title = title.replace('Capítulo ', '[COLOR goldenrod]Epis. [/COLOR]')

        titulo = str(season) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, infoLabels={'year': '-'},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="shortstory-in">.*?<a href="(.*?)".*?<img src="(.*?)".*?<figcaption>Temporada(.*?)</figcaption>')

    for url, thumb, season in matches:
        season = season.strip()

        title = 'Temporada ' + season

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.url = url
            item.thumbnail = thumb
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, thumbnail = thumb, page = 0, contentType = 'season', contentSeason = season, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="saision_LI2">(.*?)</div>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('Star', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Star', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Star', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Star', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Star', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Star', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Star', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        title =  scrapertools.find_single_match(match, '<span>(.*?)</span>')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not title or not url: continue

        epis = scrapertools.find_single_match(title, 'Episodio(.*?)$').strip()
        if not epis: epis = scrapertools.find_single_match(title, 'Capítulo(.*?)$').strip()
        if not epis: epis = scrapertools.find_single_match(title, 'Capitulo(.*?)$').strip()
        if not epis: epis = scrapertools.find_single_match(title, 'capítulo(.*?)$').strip()
        if not epis: epis = scrapertools.find_single_match(title, 'capitulo(.*?)$').strip()

        if not epis: epis = 1

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'de': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose', 'vo': 'Vo'}

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    options = scrapertools.find_multiple_matches(data, '<li class="streamer">(.*?)</li>')

    ses = 0

    for option in options:
        ses += 1

        lang = scrapertools.find_single_match(option, '<img src="/icon/(.*?).png')

        d_url = scrapertools.find_single_match(option, 'data-url="(.*?)"')

        if d_url:
            if '/video-streaming.html' in d_url: continue

            d_url = host[:-1] + d_url

            try:
                hay_proxies = False
                if config.get_setting('channel_star_proxies', default=''): hay_proxies = True

                timeout = None
                if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    url = httptools.downloadpage_proxy('star', d_url, follow_redirects=False, timeout=timeout).headers['location']
                else:
                    url = httptools.downloadpage(d_url, follow_redirects=False, timeout=timeout).headers['location']
            except:
                url = ''

            if url:
                url = url.replace('/younetu.com/player/', '/waaw.to/')

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                other = ''
                if servidor == 'various': other = servertools.corregir_other(url)

                itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang,lang), other = other ))

    # ~ Descargas requieren registrarse

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'recherche?q=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []

