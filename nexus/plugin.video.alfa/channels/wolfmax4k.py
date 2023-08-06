# -*- coding: utf-8 -*-
# -*- Channel WolfMax4K -*-
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

IDIOMAS = AlfaChannelHelper.IDIOMAS_T
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES_T
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS_T
forced_proxy_opt = None

canonical = {
             'channel': 'wolfmax4k', 
             'host': config.get_setting("current_host", 'wolfmax4k', default=''), 
             'host_alt': ["https://wolfmax4k.com/"], 
             'host_black_list': [], 
             'pattern': '<a\s*href="([^"]+)"\s*class="navbar-brand\s*me-xl-4\s*me-lg-3\s*text-gray-900">', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt,  
             'cf_assistant': True, 'CF_stat': True, 'cf_assistant_get_source': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_torrent = host
channel = canonical['channel']
categoria = channel.capitalize()
plot = '[COLOR hotpink][B]Atención:[/B][/COLOR] requiere un browser tipo '
plot +='[COLOR yellow]Chrome, Firefox, Opera[/COLOR] para descargar los archivos [COLOR hotpink].torrent[/COLOR]'

timeout = config.get_setting('timeout_downloadpage', channel)
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas"
tv_path = '/serie'
docu_path = '/documentales'
pr_tv_path = '/programas-tv'
tele_path = '/telenovelas'
language = ['CAST']
url_replace = []

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['col-lg-2']}]}, 
         'sub_menu': {}, 
         'categories': {}, 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/|\/images\/)(\w+)(?:-[^\.]+)?\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\&pg=\d+', '&pg=%s'], ['\/\d+$', '/%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['mod-pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href', '@TEXT': '\/(\d+)'}])]), 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {},
         'season_num': {}, 
         'seasons_search_num_rgx': [], 
         'seasons_search_qty_rgx': [], 
         'episode_url': '', 
         'episodes': {}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['div'], 'class': ['layout-section pb-3']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax', ''],
                         ['(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', ''], 
                         ['(?i)[-|\(]?\s*HDRip\)?|microHD|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?', ''], 
                         ['(?i)\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|[\(|\[]\S*\.*$', ''],
                         ['(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*|\[*\(*dvd\s*r\d*\w*\]*\)*|[\[|\(]*dv\S*[\)|\]]*', ''], 
                         ['(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?', ''], 
                         ['(?i)(?:\s*&#8211;)?\s*-?\s*temp.*?\d+.*', ''], ['\d?\d?&#.*', ''], ['\d+[x|×]\d+.*', ''], 
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)(?:libro|volumen)?\s+\d{1,2}$', ''], ['(?i)\s+ts|\s+sub\w*|\s+\(*vos.*\)*', ''], 
                         ['(?i)s\d{1,2}e\d{1,3}', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', ''], 
                           ['(?i)\d+\.\d+', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 20, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'host_torrent': host_torrent, 'duplicates': [], 'btdigg_service': True},
         'timeout': timeout,
         'btdigg_cfg': [{'url': host + 'peliculas/bluray/', 'c_type': 'peliculas', 'cnt_tot': 1, 'movie_path': '/peliculas'}, 
                        {'url': host + 'peliculas/bluray-1080p/', 'c_type': 'peliculas', 'cnt_tot': 1, 'movie_path': '/cine'}, 
                        {'url': host + 'peliculas/4k-2160p/', 'c_type': 'peliculas', 'cnt_tot': 1, 'movie_path': '/cine'},
                        {'url': host + 'series/720p/', 'c_type': 'series', 'cnt_tot': 3, 'tv_path': '/serie'},
                        {'url': host, 'c_type': 'search_token', 'find': {'find': [{'tag': ['form'], 'class': ['form-search']}], 
                                                                         'find_all': [{'tag': ['input'], '@POS': [1], '@ARG': 'value'}]}}, 
                        {'url': host + 'buscar/', 'post': '_ACTION=buscar&token=%s&pg=1&q=%s', 
                                'c_type': 'search', 'cnt_tot': 3, 'movie_path': '/peliculas', 'tv_path': '/serie', 
                                'find': {'find_all': [{'tag': ['div'], 'class': ['col-lg-2']}]}}]}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, action="submenu", title="Películas", c_type='peliculas', 
                    url=host + 'peliculas/', thumbnail=get_thumb("channels_movie.png"), contentPlot=plot))

    itemlist.append(Item(channel=item.channel, action="submenu", title="Series", c_type='episodios', 
                    url=host + 'series/', thumbnail=get_thumb("channels_tvshow.png"), contentPlot=plot))

    itemlist.append(Item(channel=item.channel, action="submenu", title="Otros", c_type='documentales', 
                    url=host, thumbnail=get_thumb("channels_documentary.png"), contentPlot=plot))

    itemlist.append(Item(channel=item.channel, action="search", title="Buscar", c_type='search', 
                    url=host, thumbnail=get_thumb("search.png")))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                    folder=False, thumbnail=get_thumb("next.png")))
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                    thumbnail=get_thumb("setting_0.png")))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)                                # Activamos Autoplay

    return itemlist
    
    
def configuracion(item):
    from platformcode import platformtools

    ret = platformtools.show_channel_settings()

    return platformtools.itemlist_refresh()
    
    
def submenu(item):
    logger.info()

    itemlist = []

    if item.c_type == 'peliculas':
        itemlist.append(Item(channel=item.channel, title="Todas las Películas", 
                             action="list_all", url=item.url + '1', 
                             thumbnail=get_thumb('movies', auto=True), c_type=item.c_type, contentPlot=item.plot))
        
        itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]por Calidad: Bluray[/COLOR]", 
                             action="list_all", url=item.url + 'bluray/1', 
                             thumbnail=get_thumb('quality', auto=True), c_type=item.c_type, contentPlot=item.plot))

        itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]por Calidad: Bluray 720p[/COLOR]", 
                             action="list_all", url=item.url + 'bluray-720p/1', 
                             thumbnail=get_thumb('quality', auto=True), c_type=item.c_type, contentPlot=item.plot))

        itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]por Calidad: Bluray 1080p[/COLOR]", 
                             action="list_all", url=item.url + 'bluray-1080p/1', 
                             thumbnail=get_thumb('quality', auto=True), c_type=item.c_type, contentPlot=item.plot))

        itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]por Calidad: 4K[/COLOR]", 
                             action="list_all", url=item.url + '4k-2160p/1', 
                             thumbnail=get_thumb('quality', auto=True), c_type=item.c_type, contentPlot=item.plot))

    if item.c_type == 'episodios':
        itemlist.append(Item(channel=item.channel, title="Todas las Series (episodios)", 
                             action="list_all", url=item.url + '1', 
                             thumbnail=get_thumb('movies', auto=True), c_type=item.c_type, contentPlot=item.plot))

        itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]por Calidad: HDTV[/COLOR]", 
                             action="list_all", url=item.url + '480p/1', 
                             thumbnail=get_thumb('quality', auto=True), c_type=item.c_type, contentPlot=item.plot))
                             
        itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]por Calidad: HDTV 720p[/COLOR]", 
                             action="list_all", url=item.url + '720p/1', 
                             thumbnail=get_thumb('quality', auto=True), c_type=item.c_type, contentPlot=item.plot))

        itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]por Calidad: WEB-DL 1080p[/COLOR]", 
                             action="list_all", url=item.url + '1080p/1', 
                             thumbnail=get_thumb('quality', auto=True), c_type=item.c_type, contentPlot=item.plot))

        itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]por Calidad: 4K[/COLOR]", 
                             action="list_all", url=item.url + '4k-2160p/1', 
                             thumbnail=get_thumb('quality', auto=True), c_type=item.c_type, contentPlot=item.plot))

    if item.c_type == 'documentales':
        itemlist.append(Item(channel=item.channel, title="Documentales (episodios)", 
                             action="list_all", url=host + docu_path.lstrip('/') + '/', 
                             thumbnail=get_thumb('documental', auto=True), c_type='documentales', contentPlot=item.plot))

        itemlist.append(Item(channel=item.channel, title="Programas TV (episodios)", 
                             action="list_all", url=host + pr_tv_path.lstrip('/') + '/', 
                             thumbnail=get_thumb('tvshows', auto=True), c_type='documentales', contentPlot=item.plot))

        itemlist.append(Item(channel=item.channel, title="Telenovelas (episodios)", 
                             action="list_all", url=host + tele_path.lstrip('/') + '/', 
                             thumbnail=get_thumb('telenovelas', auto=True), c_type='documentales', contentPlot=item.plot))

    return itemlist


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.category_new == 'newest':
        findS['controls']['cnt_tot'] = 40

    if item.c_type == 'search':
        if '%s' in item.post:
            soup = AlfaChannel.create_soup(host, alfa_s=True, **kwargs)
            token = soup.find('form', class_='form-search').find_all('input')[1].get('value', '') if soup.find('form', class_='form-search') else ''
            if not token: 
                logger.error('No hay TOKEN para búsquedas: %s' % soup.find('form', class_='form-search'))
            item.post = item.post % token
            #item.last_page = 9999
        findS['controls']['force_find_last_page'] = [0, 0, 'post']
                
    return AlfaChannel.list_all(item, matches_post=list_all_matches, finds=findS, generictools=True, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if not elem.find('div', class_='card-body'): continue
            elem_json['url'] = elem.a.get("href", "")
            
            elem_json['mediatype'] = 'movie' if (movie_path in elem_json['url'] or '/cine' in elem_json['url']) else 'episode'
            if item.c_type == 'peliculas' and elem_json['mediatype'] != 'movie': continue
            if item.c_type == 'episodios' and elem_json['mediatype'] != 'episode': continue

            if elem_json['mediatype'] == 'episode':
                try:
                    elem_json['season'] = int(scrapertools.find_single_match(elem.find('div', class_='card-body')\
                                                          .find('span', class_='fdi-item').get_text(strip=True), '(\d+)'))
                    if len(str(elem_json['season'])) > 2:
                         elem_json['season'] = int(scrapertools.find_single_match(elem_json['url'], '/temporada-(\d+)'))

                    elem_json['episode'] = int(scrapertools.find_single_match(elem.find('div', class_='card-body')\
                                                           .find('span', class_='fdi-type').get_text(strip=True), '(\d+)'))
                    if len(str(elem_json['episode'])) > 3:
                         elem_json['episode'] = int(scrapertools.find_single_match(elem_json['url'], '/capitulo-(\d+)'))
                except Exception:
                    logger.error(elem)
                    elem_json['season'] =  1
                    elem_json['episode'] =  1

            elem_json['title'] = elem.find('div', class_='card-body').find('h3', class_='title').get_text(strip=True)
            elem_json['thumbnail'] = elem.find('img').get("src", "")
            elem_json['language'] = language
            elem_json['quality'] = '*%s' % (elem.find('div', class_='quality').get_text(strip=True) or item.extra)
            elem_json['year'] = scrapertools.find_single_match(elem_json['title'], '\((\d{4})\)') or '-'
            elem_json['broadcast'] = plot

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url'): continue

        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        url = AlfaChannel.urljoin(host, elem.form.get('action', ''))
        post_list = elem.find('fieldset').find_all('input')
        post = 'dom=%s&id=%s' % (post_list[0].get('value', ''), post_list[1].get('value', ''))
    if not url or not post_list: return [], []

    soup = AlfaChannel.create_soup(url, post=post, **kwargs)
    if soup:
        matches_int = AlfaChannel.parse_finds_dict(soup, findS.get('findvideos', {}), c_type='peliculas')
    
        for elem in matches_int:
            elem_json = {}
            #logger.error(elem)
            
            try:
                elem_json['url'] = elem.find('a').get('href', '')
                elem_json['server'] = 'torrent'
                elem_json['quality'] = item.quality
                elem_json['language'] = item.language
                elem_json['torrent_info'] = ''
                elem_json['broadcast'] = plot

            except Exception:
                logger.error(elem)
                logger.error(traceback.format_exc())

            if not elem_json.get('url', ''): 
                continue

            matches.append(elem_json.copy())

    return matches, langs


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    texto = texto.replace(" ", "+")

    try:
        if texto:
            item.url = host + "buscar/"
            item.post = '_ACTION=buscar&token=%s&pg=2&q=' + texto
            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except Exception:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
 
 
def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    itemlist = []
    item = Item()
    item.title = "newest"
    item.category_new = "newest"
    item.channel = channel
    item.extra = "novedades"
    item.action = "list_all"
    
    try:
        if categoria in ['peliculas', 'torrent', '4k']:
            item.url = host + 'peliculas/4k-2160p/' if categoria == '4k' else host + 'peliculas/'
            item.c_type = "peliculas"

            itemlist = list_all(item)

            if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except Exception:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
