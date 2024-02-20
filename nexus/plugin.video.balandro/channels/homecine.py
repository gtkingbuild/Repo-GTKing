# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re

from platformcode import config, logger, platformtools, recaptcha
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


LINUX = False
BR = False
BR2 = False

if PY3:
    try:
       import xbmc
       if xbmc.getCondVisibility("system.platform.Linux.RaspberryPi") or xbmc.getCondVisibility("System.Platform.Linux"): LINUX = True
    except: pass
 
try:
   if LINUX:
       try:
          from lib import balandroresolver2 as balandroresolver
          BR2 = True
       except: pass
   else:
       if PY3:
           from lib import balandroresolver
           BR = true
       else:
          try:
             from lib import balandroresolver2 as balandroresolver
             BR2 = True
          except: pass
except:
   try:
      from lib import balandroresolver2 as balandroresolver
      BR2 = True
   except: pass


host = 'https://homecine.tv'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_homecine_proxies', default=''):
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
    hay_proxies = False
    if config.get_setting('channel_homecine_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if '/release-year/' in url: raise_weberror = False

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('homecine', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

        if not data:
            if not '/?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('HomeCine', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('homecine', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('homecine', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not '/?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='homecine', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_homecine', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Búsqueda de personas:', action = '', folder=False, text_color='tan' ))

    itemlist.append(item.clone( title = ' - Buscar intérprete ...', action = 'search', group = 'stars', search_type = 'person',
                                plot = 'Debe indicarse el nombre y apellido/s del intérprete.'))
    itemlist.append(item.clone( title = ' - Buscar dirección ...', action = 'search', group = 'director', search_type = 'person',
                                plot = 'Debe indicarse el nombre y apellido/s del director.'))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + '/top-imdb/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + '/ver/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Por estudio', action = 'estudios', search_type = 'tvshow', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    matches = [
        ['/animacion/', 'Animación'],
        ['/comedia/', 'Comedia'],
        ['/crimen/', 'Crimen'],
        ['/documental/', 'Documental'],
        ['/drama/', 'Drama'],
        ['/familia/', 'Familia'],
        ['/kids/', 'Kids'],
        ['/misterio/', 'Misterio'],
        ['/news/', 'News'],
        ['/reality/', 'Reality'],
        ['/soap/', 'Soap'],
        ['/talk/', 'Talk'],
        ['/western/', 'Western']
        ]

    if item.search_type == 'movie':
        data = do_downloadpage(host)

        matches = scrapertools.find_multiple_matches(data, '><a href="/genre([^"]+)">(.*?)</a>')

    for url, title in matches:
        url = host + '/genre' + url

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = text_color ))

    if itemlist:
        itemlist.append(item.clone( action = "list_all", title = 'Documentales', url = host + '/genre/documentales/', text_color = text_color ))

    return sorted(itemlist, key = lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1939, -1):
        url = host + '/release-year/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    web_paises = [
	   ['argentina', ''],
	   ['australia', ''],
	   ['austria', ''],
	   ['belgium', 'Belgica'],
	   ['bolivia', ''],
	   ['brazil', 'Brasil'],
	   ['bulgaria', ''],
	   ['canada', ''],
	   ['chile', ''],
	   ['china', ''],
	   ['colombia', ''],
	   ['costa-rica', 'Costa Rica'],
	   ['cuba', ''],
	   ['czech-republic', 'Republica Checa'],
	   ['denmark', 'Dinamarca'],
	   ['euador', ''],
	   ['finland', 'Finlandia'],
	   ['france', 'Francia'],
	   ['germany', 'Alemania'],
	   ['greece', 'Grecia'],
	   ['honduras', ''],
	   ['Hong-kong', 'Hong Kong'],
	   ['hungary', 'Hungria'],
	   ['iceland', 'Islandia'],
	   ['india', ''],
	   ['ireland', 'Irlanda'],
	   ['israel', ''],
	   ['italy', 'Italia'],
	   ['japan', 'Japon'],
	   ['lithuania', 'Lituania'],
	   ['malaysia', 'Malasia'],
	   ['mexico', ''],
	   ['netherlands', 'Paises Bajos'],
	   ['new-zealand', 'Nueva Zelanda'],
	   ['norway', 'Noruega'],
	   ['panama', ''],
	   ['paraguay', ''],
	   ['peru', ''],
	   ['poland', 'Polonia'],
	   ['portugal', ''],
	   ['puerto-rico', 'Puerto Rico'],
	   ['romania', 'Rumania'],
	   ['russia', 'Rusia'],
	   ['serbia', ''],
	   ['singapore', 'Singapur'],
	   ['spain', 'España'],
	   ['sweden', 'Suecia'],
	   ['switzerland', 'Suiza'],
	   ['thailand', 'Tailandia'],
	   ['turkey', 'Turquía'],
	   ['ukraine', 'Ucrania'],
	   ['uk', 'Reino Unido'],
	   ['usa', 'Estados Unidos'],
	   ['uruguay', ''],
	   ['venezuela', '']
	   ]

    for x in web_paises:
        title = x[1]
        pais = x[0]

        if title == '': title = pais.capitalize()

        url = url = host + '/country/' + pais + '/'

        itemlist.append(item.clone( title = title, url = url, action ='list_all', text_color='moccasin' ))

    return sorted(itemlist, key = lambda it: it.title)


def plataformas(item):
    logger.info()
    itemlist = []

    web_plataformas = [
	   ['ae', 'A&E'],
	   ['abc', 'ABC'],
	   ['abc-fox', 'ABC, FOX'],
	   ['acorn-tv', 'Acorn TV'],
	   ['adult-swim', 'Adult Swim'],
	   ['amazon', 'Amazon'],
	   ['amc', 'AMC'],
	   ['antena-3', 'Antena 3'],
	   ['apple-tv', 'Apple TV+'],
	   ['axn', 'AXN'],
	   ['bbc-america', 'BBC America'],
	   ['bbc-iplayer', 'BBC iPlayer'],
	   ['bbc-one', 'BBC One'],
	   ['bbc-two', 'BBC Two'],
	   ['caracol-tv', 'Caracol TV'],
	   ['cartoon-network', 'Cartoon Network'],
	   ['cartoon-network-teletoon-tv-tokyo', 'Cartoon Network, Teletoon, TV Tokyo'],
	   ['cbc-television', 'CBC Television'],
	   ['cbs', 'CBS'],
	   ['cbs-all-access', 'CBS All Access'],
	   ['channel-4', 'Channel 4'],
	   ['comedy-central', 'Comedy Central'],
	   ['ctv', 'CTV'],
	   ['cuatro', 'Cuatro'],
	   ['disney-channel', 'Disney Channel'],
	   ['disney-xd', 'Disney XD'],
	   ['disney', 'Disney+'],
	   ['dmax', 'DMax'],
	   ['epix', 'Epix'],
	   ['espn-netflix', 'ESPN Netflix'],
	   ['flooxer', 'Flooxer'],
	   ['fox', 'FOX'],
	   ['fox-espana', 'FOX España'],
	   ['france-3', 'France 3'],
	   ['freeform', 'Freeform'],
	   ['fx', 'FX'],
	   ['hbo', 'HBO'],
	   ['hbo-europe', 'HBO Europe'],
	   ['history', 'History'],
	   ['hulu', 'Hulu'],
	   ['itv', 'ITV'],
	   ['la-1', 'La 1'],
	   ['la-une', 'La Une'],
	   ['lifetime', 'Lifetime'],
	   ['movistar', 'Movistar+'],
	   ['mtv', 'MTV'],
	   ['nbc', 'NBC'],
	   ['netflix', 'Netflix'],
	   ['nickelodeon', 'Nickelodeon'],
	   ['orf', 'ORF'],
	   ['paramount-network', 'Paramount Network'],
	   ['rai-1', 'Rai 1'],
	   ['rai-2', 'Rai 2'],
	   ['ruv', 'RÚV'],
	   ['shudder', 'Shudder'],
	   ['showcase', 'Showcase'],
	   ['showtime', 'Showtime'],
	   ['sky-atlantic', 'Sky Atlantic'],
	   ['sky-one', 'Sky One'],
	   ['syfy', 'Syfy'],
	   ['star-tv', 'Star TV'],
	   ['starz', 'Starz'],
	   ['tbs', 'TBS'],
	   ['the-cw', 'The CW'],
	   ['the-wb', 'The WB'],
	   ['telecinco', 'Telecinco'],
	   ['telemundo', 'Telemundo'],
	   ['televisa', 'Televisa'],
	   ['tnt', 'TNT'],
	   ['tv3', 'TV3'],
	   ['tvn', 'TVN'],
	   ['univision', 'Univision'],
	   ['usa-network', 'USA Network'],
	   ['vh1', 'VH1'],
	   ['viaplay', 'Viaplay'],
	   ['zdf', 'ZDF']
	   ]

    for x in web_plataformas:
        title = x[1]
        title = title.replace('-', ' ')

        url = host + '/networks/' + x[0] + '/'

        itemlist.append(item.clone( title = title, url = url, action ='list_all', text_color = 'hotpink' ))

    return itemlist


def estudios(item):
    logger.info()
    itemlist = []

    web_estudios = [
	   ['26-keys-productions', '26 Keys Productions'],
	   ['abc-studios', 'ABC Studios'],
	   ['amazon-studios', 'Amazon Studios'],
	   ['amblin-television', 'Amblin Television'],
	   ['amc-studios', 'AMC Studios'],
	   ['alloy-entertainment', 'Alloy Entertainment'],
	   ['atlas-entertainment', 'Atlas Entertainment'],
	   ['awesomenesstv', 'AwesomenessTV'],
	   ['bad-robot', 'Bad Robot'],
	   ['bbc', 'BBC'],
	   ['blumhouse-television', 'Blumhouse Television'],
	   ['bonanza-productions', 'Bonanza Productions'],
	   ['cbs-television-studios', 'CBS Television Studios'],
	   ['fox-21', 'Fox 21'],
	   ['fox-21-television-studios', 'Fox 21 Television Studios'],
	   ['fox-television-studios', 'Fox Television Studios'],
	   ['freeform', 'Freeform Studios'],
	   ['fx-productions', 'FX Productions'],
	   ['genre-films', 'Genre Films'],
	   ['hanna-barbera-productions', 'Hanna-Barbera Productions'],
	   ['itv', 'ITV Studios'],
	   ['marvel-entertainment', 'Marvel Entertainment'],
	   ['marvel-television', 'Marvel Television'],
	   ['mgm-television', 'MGM Television'],
	   ['monkeypaw-productions', 'Monkeypaw Productions'],
	   ['movistar', 'Movistar+'],
	   ['neal-street-productions', 'Neal Street Productions'],
	   ['nelvana-limited', 'Nelvana Limited'],
	   ['netflix', 'Netflix'],
	   ['paramount-television', 'Paramount Television'],
	   ['platinum-dunes', 'Platinum Dunes'],
	   ['secret-hideout', 'Secret Hideout'],
	   ['showtime-networks', 'Showtime Networks'],
	   ['sky', 'Sky'],
	   ['syfy', 'Syfy'],
	   ['skydance-television', 'Skydance Television'],
	   ['televisa', 'Televisa'],
	   ['universal-cable-productions', 'Universal Cable Productions'],
	   ['universal-television', 'Universal Television'],
	   ['usa-network', 'USA Network'],
	   ['vertigo-films', 'Vertigo Films'],
	   ['viaplay', 'Viaplay'],
	   ['walt-disney-television', 'Walt Disney Television'],
	   ['warner-bros-animation', 'Warner Bros. Animation'],
	   ['warner-bros-television', 'Warner Bros. Television'],
	   ['zdf', 'ZDF']
	   ]

    for x in web_estudios:
        title = x[1]

        title = title.replace('-', ' ')

        url = host + '/studio/' + x[0] + '/'

        itemlist.append(item.clone( title = title, url = url, action ='list_all', text_color = 'hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('movie-id="\d+".*?<a href="([^"]+)".*?<.*?original="([^"]+)".*?<h2>([^<]+)</h2>.*?jtip(.*?)clearfix', re.DOTALL).findall(data)

    for url, thumb, title, info in matches:
        url = host + url

        if thumb.startswith('//'): thumb = 'https:' + thumb
        elif thumb.startswith('/'): thumb = host + thumb

        title = title.replace('&amp;', '&').replace('&#8211;', '')

        year = scrapertools.find_single_match(info, 'rel="tag">(\d{4})<')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(info, '-quality">(.*?)</div>')

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<li class='active'>.*?class='page larger' href='([^']+)'")

        if next_page:
            next_page = host + next_page

            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('movie-id="\d+".*?<a href="([^"]+)".*?<.*?original="([^"]+)".*?<h2>([^<]+)</h2>.*?jtip(.*?)clearfix', re.DOTALL).findall(data)

    for url, thumb, title, info in matches:
        serie_name = scrapertools.find_single_match(title, '(.*?) Temporada').strip()

        season = scrapertools.find_single_match(info, '-quality">Season(.*?)</div>').strip()
        episode = scrapertools.find_single_match(info, '">Episode:(.*?)</div>').strip()

        if not season or not episode: continue

        url = host + url

        titulo = title

        fecha = scrapertools.find_single_match(info, '<span class="ep_airdate">(.*?)</span>').strip()
        if fecha: titulo = titulo + '  (' + fecha + ')'

        titulo = titulo.replace('Capitulo', '[COLOR goldenrod]Capitulo[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Capítulo[/COLOR]')

        itemlist.append(item.clone( action='findvideos', title = titulo, url = url, thumbnail = thumb,
                                    contentType = 'episode', contentSerieName=serie_name, contentSeason = season, contentEpisodeNumber = episode, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<li class='active'>.*?class='page larger' href='([^']+)'")

        if next_page:
            next_page = host + next_page

            itemlist.append(item.clone( title = 'Siguientes ...', action = 'last_epis', url = next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = r'<strong>(?:Season|Temporada) (\d+)</strong>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for season in matches:
        title = 'Temporada ' + season

        url = item.url

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.url = url
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, page = 0, contentType = 'season', contentSeason = season, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    season = item.contentSeason

    data = do_downloadpage(item.url)

    patron_season = '<strong>(?:Season|Temporada) %s</strong>.*?class="les-content"(.*?)</div>' % season
    data = scrapertools.find_single_match(data, patron_season)

    matches = re.compile('<a href="([^"]+)">(?:Episode|Capitulo) (\d+)', re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, epis in matches[item.page * item.perpage:]:
        url = host + url

        try: titulo = '%sx%s - Capítulo %s' % (season, epis, epis)
        except: titulo = 'Episodio ' + epis

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

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

    IDIOMAS = {'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose', 'Ingles': 'VO', 'Español Latino': 'Lat', 'Español Castellano': 'Esp', 'Español Espellano': 'Esp'}

    data = do_downloadpage(item.url)

    matches = re.compile('<div id="tab(.*?)".*?<iframe src="(.*?)"', re.DOTALL).findall(data)
    if not matches: matches = re.compile('<div id="tab(.*?)".*?<IFRAME SRC="(.*?)"', re.DOTALL).findall(data)

    if not matches: matches = re.compile('<div id="tab(.*?)".*?data-lazy-src="(.*?)"', re.DOTALL).findall(data)

    ses = 0

    for option, url in matches:
        ses += 1

        info = scrapertools.find_single_match(data, '<a href="#tab%s">(.*?)<' % option)

        if '-' in info:
            qlty, lang = scrapertools.find_single_match(info, '(.*?) - (.*)')
            if " / " in lang: lang = lang.split(" / ")[1]
        else:
            lang = ''
            qlty = info

        lang = lang.lower().capitalize()

        if url.startswith('//'): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'youtube': continue

        if not servidor: servidor = 'directo'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, quality = qlty, language = IDIOMAS.get(lang, lang) ))

    if 'href="#list-dl">Descargar</a>' in data:
        bloque = scrapertools.find_single_match(data, 'href="#list-dl">Descargar</a>(.*?)<span>Otros usuarios están viendo:</span>')

        matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)".*?class="flag flag-.*?<span class="lang_tit">(.*?)</span>.*?<span class="lnk lnk-dl" >(.*?)</span>')

        for url, lang, qlty in matches:
            ses += 1

            if url.startswith('//'): url = 'https:' + url

            url = url.replace('?download=1', '')

            lang = lang.replace('Cast', 'Esp').replace('Subtitulado', 'Vose').replace('Sub', 'Vose').replace(' /', ',')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if not servidor: servidor = 'directo'

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, quality = qlty, language = IDIOMAS.get(lang, lang), other = 'D' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.server and item.server != 'directo':
        url = servertools.normalize_url(item.server, item.url)
        itemlist.append(item.clone( url = item.url, server = item.server ))
        return itemlist

    if '/cinemaupload.com/' in item.url or '/pastea.me/':
        if '/cinemaupload.com/' in item.url: item.url = item.url.replace('/cinemaupload.com/', '/embed.cload.video/')

        data = do_downloadpage(item.url)

        sitekey = scrapertools.find_single_match(data, 'data-sitekey="([^"]+)')
        if not sitekey:
            url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
            if url:
                if '/download/' in url:
                    url = url.replace('//download/', '/files/').replace('/download/', '/files/')
                    itemlist.append(item.clone( url = url, server = 'directo' ))
                    return itemlist

                elif '/manifest.mpd' in url:
                    if platformtools.is_mpd_enabled():
                        itemlist.append(['mpd', url, 0, '', True])
                    itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
                else:
                    itemlist.append(['m3u8', url])

                return itemlist

        # Opción sin desarrollar
        response = recaptcha.get_recaptcha_response(sitekey, item.url)
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'


    referer = host + '/'
    headers = {'Referer': referer}

    if not item.url.startswith(host):
        url = httptools.downloadpage(item.url, headers = headers, follow_redirects = False, only_headers = True).headers.get('location', '')
    else:
        if config.get_setting('channel_homecine_proxies', default=''):
            url = httptools.downloadpage_proxy('homecine', item.url, headers = headers, follow_redirects = False, only_headers = True).headers.get('location', '')
        else:
            url = httptools.downloadpage(item.url, headers = headers, follow_redirects = False, only_headers = True).headers.get('location', '')

    if url:
        data = do_downloadpage(url, headers = headers, raise_weberror = False)
        url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')

    if url:
        if '/manifest.mpd' in url:
            if platformtools.is_mpd_enabled(): itemlist.append(['mpd', url, 0, '', True])
            itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
        else: itemlist.append(['mp4', url])

        return itemlist

    if 'embed.cload' in item.url:
        data = do_downloadpage(item.url, headers = headers, raise_weberror = False)

        if '<div class="g-recaptcha"' in data or 'Solo los humanos pueden ver' in data:
            headers = {'Referer': referer, 'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)'}
            data = do_downloadpage(item.url, headers = headers, raise_weberror = False)

            new_url = scrapertools.find_single_match(data, '<div id="option-players".*?src="([^"]+)"')
            if new_url:
                new_url = new_url.replace('/cinemaupload.com/', '/embed.cload.video/')
                data = do_downloadpage(new_url, raise_weberror = False)

            url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')

            if url:
                if '/manifest.mpd' in url:
                    if platformtools.is_mpd_enabled(): itemlist.append(['mpd', url, 0, '', True])
                    itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
                else: itemlist.append(['m3u8', url])

                return itemlist

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.group:
            item.url = host + '/' + item.group + '/' + texto.replace(" ", "-")
        else:
            item.url = host + '/?s=' + texto.replace(" ", "+")

        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

