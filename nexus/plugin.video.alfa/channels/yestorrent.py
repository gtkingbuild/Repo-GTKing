# -*- coding: utf-8 -*-
# -*- Channels Magnetpelis, Pelispanda, Yestorrent -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAllChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

# Canal común con Cinetorrent(muerto), Magnetpelis (muerto), Pelispanda, Yestorrent

IDIOMAS = AlfaChannelHelper.IDIOMAS_T
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES_T
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS_T
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'yestorrent', 
             'host': config.get_setting("current_host", 'yestorrent', default=''), 
             'host_alt': ['https://yestorrent.org/'], 
             'host_black_list': ['https://yestorrent.cx/'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)     # Actualización sólo últ. Temporada?
min_temp = modo_ultima_temp if not modo_ultima_temp else 'continue'

weirdo_channels = ['yestorrent']
sufix = '-y002/' if channel in weirdo_channels else ''

timeout = config.get_setting('timeout_downloadpage', channel)
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/torrent"
tv_path = '/series'
language = ['LAT']
url_replace = []

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['col-6 col-sm-4 col-lg-3 col-xl-2']}]}, 
         'categories': {}, 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': dict([('find', [{'tag': ['ul'], 'class': True}]), 
                              ('get_text', [{'tag': '', '@STRIP': True}])]), 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}, 
                                      {'tag': ['a'], 'class': ['next page-numbers']}]), 
                            ('find_previous', [{'tag': ['a'], 'class': ['page-numbers']}]), 
                            ('get_text', [{'@TEXT': '(\d+)'}])]), 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {'find_all': [{'tag': ['div'], 'class': ['card-header']}]}, 
         'season_num': dict([('find', [{'tag': ['span']}]), 
                             ('get_text', [{'@TEXT': '(\d+)'}])]), 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {'find_all': [{'tag': ['div'], 'class': ['accordion__card']}]}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['tr']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': min_temp, 'url_base64': True, 'add_video_to_videolibrary': True, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = []
    
    thumb_pelis = get_thumb("channels_movie.png")
    thumb_series = get_thumb("channels_tvshow.png")
    thumb_genero = get_thumb("genres.png")
    thumb_anno = get_thumb("years.png")
    thumb_calidad = get_thumb("top_rated.png")
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Películas", action="submenu", 
                url=host, thumbnail=thumb_pelis, c_type="peliculas"))
    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Por Género[/COLOR]", action="section", 
                url=host, thumbnail=thumb_genero, extra='Genero', c_type="peliculas"))
    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Por Año[/COLOR]", action="section", 
                url=host, thumbnail=thumb_anno, extra='A.O', c_type="peliculas"))
    if channel not in ['magnetpelis']:
        itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Por Calidad[/COLOR]", action="section", 
                url=host, thumbnail=thumb_calidad, extra='CALIDAD', c_type="peliculas"))
    if channel in weirdo_channels:
        itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Por Idiomas[/COLOR]", action="section", 
                url=host, thumbnail=thumb_calidad, extra='Idioma', c_type="peliculas"))
    
    itemlist.append(Item(channel=item.channel, title="Series", action="submenu", 
                url=host, thumbnail=thumb_series, c_type="series"))
    #itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Por Año[/COLOR]", action="section", 
    #            url=host, thumbnail=thumb_anno, extra='A.O', c_type="series"))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search",
                url=host, thumbnail=thumb_buscar, c_type="search"))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                folder=False, thumbnail=thumb_separador))
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                thumbnail=thumb_settings))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)                                # Activamos Autoplay

    return itemlist
    
    
def configuracion(item):
    from platformcode import platformtools

    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()

    return


def submenu(item):
    logger.info()
    global sufix

    itemlist = []

    if item.c_type == 'peliculas':
        findS = {'find': [{'tag': ['a'], 'class': ['header__nav-link'], 'string': re.compile('Pel.culas'), '@ARG': 'href'}]}
    else:
        findS = {'find': [{'tag': ['a'], 'class': ['header__nav-link'], 'string': re.compile('Series'), '@ARG': 'href'}]}
        sufix = ''

    soup = AlfaChannel.create_soup(item.url, **kwargs)
    item.url = AlfaChannel.parse_finds_dict(soup, findS).rstrip('/') + sufix + '/'

    return list_all(item)


def section(item):
    logger.info()
    
    findS = finds.copy()
    
    findS['controls'] = {
                         'year': True if item.extra in ['A.O'] else False,
                         'reverse': True if channel in weirdo_channels and item.extra in ['A.O'] else False
                        }
    findS['categories'] = dict([('find', [{'tag': ['a'], 'class': ['dropdown-toggle header__nav-link'], 
                                                         'string': re.compile('(?i)%s' % item.extra)}]), 
                                ('find_next', [{'tag': ['ul']}]), 
                                ('find_all', [{'tag': ['li']}])])

    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
                       
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        promos = False
        
        elem_json['url'] = elem.a.get('href', '')
        if item.c_type == 'peliculas' and tv_path in elem_json['url']: continue
        if item.c_type in ['series', 'documentales'] and tv_path not in elem_json['url']: continue
        for promo in ['netflix', 'disney', 'diney', 'hbo', 'spotify']:
            if promo in elem_json['url']:
                promos = True
        if promos: 
            continue
        elem_json['title'] = elem.h3.get_text(strip=True)
        elem_json['title'] = scrapertools.remove_htmltags(elem_json['title']).strip().strip('.').strip()
        elem_json['thumbnail'] = elem.img.get('data-src', '')
        elem_json['quality'] = '*%s' % AlfaChannel.parse_finds_dict(elem, findS.get('get_quality', {}), c_type=item.c_type)
        if item.c_type in ['series', 'documentales'] and 'x' in elem_json['quality'].lower():
            if elem_json['quality'].lower() != 'x': elem_json['title_subs'] = [elem_json['quality'].lower().replace('*', '')]
            elem_json['quality'] = '*'
        elem_json['language'] = elem_json['quality']
        if item.extra == 'Idioma': elem_json['language'] = item.title.lower()

        if item.c_type == 'search' and tv_path not in elem_json['url']:
            elem_json['mediatype'] = 'movie'
        
        matches.append(elem_json.copy())
    
    return matches


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item, **kwargs)


def episodios(item):
    logger.info()

    itemlist = []

    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    kwargs['matches_post_get_video_options'] = findvideos_matches
    kwargs['headers'] = {'Referer': item.url}

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, generictools=True, finds=finds, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem_season in matches_int:
        season = int(scrapertools.find_single_match(elem_season.span.text, '\d+') or '1')
        if season != item.infoLabels['season']: continue
        
        for elem in elem_season.find_all('tr'):
            elem_json = {}
            
            elem_json['server'] = 'torrent'
            elem_json['size'] = ''
            elem_json['torrent_info'] = ''
            elem_json['season'] = item.infoLabels['season']

            for x, td in enumerate(elem.find_all('td')):
                if x == 0: elem_json['episode'] = int(scrapertools.find_single_match(str(td.get_text()), '\d+') or '1')
                if x == 1: elem_json['quality'] = '*%s' % td.get_text()
                if x == 2: elem_json['language'] = '*%s' % td.get_text()
                if x == 5: elem_json['url'] = td.a.get('href', '')

            if not elem_json.get('url', ''): 
                continue

            matches.append(elem_json.copy())
    
    return matches


def findvideos(item):
    logger.info()

    kwargs['matches_post_episodes'] = episodesxseason_matches
    
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=play, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    videolibrary = AHkwargs.get('videolibrary', False)

    if videolibrary:
        for x, (episode_num, _scrapedserver, _scrapedquality, _scrapedlanguage, scrapedsize, scrapedurl) in enumerate(matches_int):
            elem_json = {}

            if item.infoLabels['mediatype'] in ['episode']:
                elem_json['season'] = item.infoLabels['season']
                elem_json['episode'] = episode_num
            if _scrapedserver not in ['torrent', 'Torrent', 'array', 'Array']:
                elem_json['server'] = 'torrent'
                elem_json['quality'] = _scrapedserver
                elem_json['language'] = _scrapedquality
            else:
                elem_json['server'] = _scrapedserver
                elem_json['quality'] = _scrapedquality
                elem_json['language'] = _scrapedlanguage
            if not elem_json['quality'].startswith('*'): elem_json['quality'] = '*%s' % elem_json['quality']
            if not elem_json['language'].startswith('*'): elem_json['language'] = '*%s' % elem_json['language']
            elem_json['url'] = scrapedurl
            elem_json['torrent_info'] = scrapedsize

            matches.append(elem_json.copy())
            item.emergency_urls[1][x] = elem_json.copy()

    else:
        for elem in matches_int:
            elem_json = {}
            #logger.error(elem)
            x = 0
            
            for td in elem.find_all('td'):
                if item.infoLabels['mediatype'] in ['movie']:
                    if x == 0:
                        if len(elem.find_all('td')) < 7:
                            elem_json['server'] = 'torrent'
                            x += 1
                        else:
                            elem_json['server'] = 'torrent' if td.get_text().lower() in ['t', 'torrent', 'array'] else 'directo'
                    if x == 1: elem_json['quality'] = '*%s' % td.get_text()
                    if x == 2: elem_json['language'] = '*%s' % td.get_text()
                    if x == 4: elem_json['torrent_info'] =  td.get_text().replace('-', '')
                    if x == 6: elem_json['url'] = td.a.get('href', '')
                else:
                    elem_json['season'] = item.infoLabels['season']
                    if x == 0: elem_json['episode'] = int(scrapertools.find_single_match(str(td.get_text()), '\d+') or '1')
                    if x == 1: elem_json['quality'] = '*%s' % td.get_text()
                    if x == 2: elem_json['language'] = '*%s' % td.get_text()
                    if x == 5: elem_json['url'] = td.a.get('href', '')
                    elem_json['server'] = 'torrent'
                    elem_json['torrent_info'] = ''
                x += 1

            if not elem_json.get('url', ''): 
                continue

            matches.append(elem_json.copy())
    
    return matches, langs


def play(item):

    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'timeout': 5, 'CF': True, 'canonical': {}, 'soup': False}

    if 'cinestart' in item.url:
        url, post = item.url.split('?')
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Referer': item.url}
        response = AlfaChannel.create_soup(url.replace('player.php', 'r.php'), post=post, headers=headers, 
                                           follow_redirects=False, hide_infobox=True, **kwargs)

        if response.code in AlfaChannel.REDIRECTION_CODES:
            item.url = '%s|Referer=%s' % (response.headers.get('location', ''), AlfaChannel.obtain_domain(item.url, scheme=True))

    return [item]


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    texto = texto.replace(" ", "+")
    
    try:
        item.url = host + 'buscar/?buscar=%s' % texto
        item.extra = 'search'

        if texto:
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc(1))
        return []
 
 
def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    itemlist = []
    item = Item()

    item.title = "newest"
    item.category_new = "newest"
    item.channel = channel
    
    try:
        if categoria in ['peliculas', 'latino', 'torrent']:
            item.url = host + "peliculas/"
            if channel in weirdo_channels:
                item.url = host + "Descargar-peliculas-completas%s/" % sufix
            item.extra = "peliculas"
            item.extra2 = "novedades"
            item.action = "list_all"
            itemlist.extend(list_all(item))
                
        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()
        
        if categoria in ['series', 'latino', 'torrent']:
            item.category_new= 'newest'
            item.url = host + "series/"
            item.extra = "series"
            item.extra2 = "novedades"
            item.action = "list_all"
            itemlist.extend(list_all(item))

        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc(1))

    return itemlist
