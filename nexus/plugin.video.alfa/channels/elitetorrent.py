# -*- coding: utf-8 -*-
# -*- Channel EliteTorrent -*-
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
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'elitetorrent', 
             'host': config.get_setting("current_host", 'elitetorrent', default=''), 
             'host_alt': ['https://www.elitetorrent.com/'], 
             'host_black_list': ['https://www.elitetorrent.dev/', 'https://www.elitetorrent.wtf/', 'https://elitetorrent.la/'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt,  
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_torrent = host
channel = canonical['channel']
categoria = channel.capitalize()
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)     # Actualización sólo últ. Temporada?
min_temp = modo_ultima_temp if not modo_ultima_temp else 'continue'

timeout = config.get_setting('timeout_downloadpage', channel)
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas"
tv_path = '/series'
language = ['CAST']
url_replace = []

finds = {'find': dict([('find', [{'tag': ['ul'], 'class': ['miniboxs-ficha']}]), 
                       ('find_all', [{'tag': ['li']}])]), 
         'sub_menu': dict([('find', [{'tag': ['div'], 'class': ['cab_menu']}]), 
                           ('find_all', [{'tag': ['li']}])]), 
         'categories': {}, 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/|\/images\/)(\w+)(?:-[^\.]+)?\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['paginacion']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href', '@TEXT': '\/(\d+)\/'}])]), 
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
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['ficha_descarga_opciones']}]), 
                             ('find_all', [{'tag': ['a'], 'string': re.compile('Descargar')}])]), 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax', ''],
                         ['(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', ''], 
                         ['(?i)[-|\(]?\s*HDRip\)?|microHD|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?', ''], 
                         ['(?i)\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|[\(|\[]\S*\.*$', ''],
                         ['(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*|\[*\(*dvd\s*r\d*\w*\]*\)*|[\[|\(]*dv\S*[\)|\]]*', ''], 
                         ['(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?', ''], 
                         ['(?i)(?:\s*&#8211;)?\s*temp.*?\d+.*', ''], ['\d?\d?&#.*', ''], ['\d+[x|×]\d+.*', ''], 
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)(?:libro|volumen)?\s+\d{1,2}$', ''], ['(?i)\s+ts|\s+sub\w*|\s+\(*vos.*\)*', ''], 
                         ['(?i)s\d{1,2}e\d{1,3}', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', ''], 
                           ['(?i)\d+\.\d+', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'min_temp': min_temp, 'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 15, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'host_torrent': host_torrent, 'duplicates': []},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, action="submenu", title="Novedades", c_type='novedades', 
                    url=host, thumbnail=get_thumb("channels_movie.png")))

    itemlist.append(Item(channel=item.channel, action="submenu", title="Películas", c_type='peliculas', 
                    url=host, thumbnail=get_thumb("channels_movie.png")))
    
    itemlist.append(Item(channel=item.channel, action="submenu", title="Series", c_type='episodios', 
                    url=host, thumbnail=get_thumb("channels_tvshow.png")))
    
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
    findS = finds.copy()

    soup = AlfaChannel.create_soup(host, **kwargs)

    matches_int = AlfaChannel.parse_finds_dict(soup, findS['sub_menu'])

    if item.c_type == "peliculas":

        # Subtituladas
        findS['sub_menu'] = dict([('find', [{'tag': ['div'], 'id': ['menu_langen']}]), 
                                  ('find_all', [{'tag': ['a']}])])
        matches_int.extend(AlfaChannel.parse_finds_dict(soup, findS['sub_menu']))

        # Géneros
        findS['sub_menu'] = dict([('find', [{'tag': ['div'], 'id': ['cuerpo']}]), 
                                  ('find_all', [{'tag': ['li'], 'id': False}])])
        matches_int.extend(sorted(AlfaChannel.parse_finds_dict(soup, findS['sub_menu']), key=lambda el: el.a.get_text(strip=True)))

    genres = False
    contentType = 'movie' if item.c_type == "peliculas" else 'tvshow'

    for elem in matches_int:
        #logger.error(elem)

        try:
            title = elem.a.get_text(strip=True).title()
            url = AlfaChannel.urljoin(host, elem.a.get('href', ''))
            thumb = "channels_%s_hd.png" % contentType if not genres else 'genres.png'
        except:
            title = elem.get('title', '').replace('Series y peliculas torrent ', '').title()
            url = AlfaChannel.urljoin(host, elem.get('href', ''))
            thumb = "channels_vos.png"

        if item.c_type in ['novedades'] and title == 'Estrenos':
            item.url = url
            item.title = title
            return list_all(item)

        if 'Estrenos' in title: continue

        if item.c_type in ['peliculas'] and 'series' in title.lower(): continue
        if item.c_type in ['episodios'] and not 'series' in title.lower(): continue

        if 'genero' in url and not genres:
            genres = True
            itemlist.append(Item(channel=item.channel, action='', title='[COLOR paleturquoise]Géneros[/COLOR]', url='', 
                                 thumbnail=get_thumb('genres.png')))

        itemlist.append(Item(channel=item.channel, title=title, extra=title if 'calidad' in url or 'Microhd' in title else '', 
                             action="list_all", url=url, thumbnail=get_thumb(thumb), c_type=item.c_type, category=categoria))

        if item.c_type == "episodios":                                          # Añadimos Series VOSE que está fuera del menú principal
            itemlist.append(Item(channel=item.channel, title="Series VOSE", action="list_all", quality='HDTV', 
                             url=host + "series-vose/", thumbnail=get_thumb("channels_vos.png"), 
                             c_type=item.c_type, category=categoria))

    return itemlist


def list_all(item):
    logger.info()
                
    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=True, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.find('div', class_='imagen').a.get("href", "")
            
            elem_json['mediatype'] = 'movie' if movie_path in elem_json['url'] and item.quality != 'HDTV' else 'episode'
            if elem_json['mediatype'] == 'episode':
                try:
                    if scrapertools.find_single_match(elem.find('div', class_='imagen').a.get("title", ""), '(?i)s(\d{1,2})e(\d{1,3})'):
                        elem_json['season'], elem_json['episode'] = scrapertools.find_single_match(elem.find('div', class_='imagen')\
                                                                                                   .a.get("title", ""), '(?i)s(\d{1,2})e(\d{1,3})')
                    else:
                        elem_json['season'], elem_json['episode'] = scrapertools.find_single_match(elem.find('div', class_='imagen')\
                                                                                                   .a.get("title", ""), '(?i)\s+(\d{1,2}).(\d{1,3})')
                    elem_json['season'] =  int(elem_json['season'])
                    elem_json['episode'] =  int(elem_json['episode'])
                except:
                    logger.error(elem)
                    elem_json['season'] =  1
                    elem_json['episode'] =  1

            elem_json['title'] = elem.find('div', class_='imagen').a.get("title", "")
            elem_json['thumbnail'] = elem.find('div', class_='imagen').a.img.get("data-src", "")
            elem_json['language'] = '*%s' % elem.find('span', id=True).img.get("data-src", "")
            elem_json['quality'] = '*%s' % (item.quality or elem.find('span', id=False)\
                                            .get_text(strip=True).replace('---', '') or item.extra)

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if item.c_type == 'peliculas' and movie_path not in elem_json['url']: continue
        if item.c_type == 'episodios' and tv_path not in elem_json['url'] and item.quality != 'HDTV': continue
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
    videolibrary = AHkwargs.get('videolibrary', False)

    if videolibrary:
        if len(item.emergency_urls) > 1: matches_int.insert(0, item.emergency_urls[0][0])
        for x, (scrapedurl) in enumerate(matches_int):
            elem_json = {}
            #logger.error(matches_int[x])

            if item.infoLabels['mediatype'] in ['episode']:
                elem_json['season'] = item.infoLabels['season']
                elem_json['episode'] = item.infoLabels['episode']

            elem_json['url'] = scrapedurl
            elem_json['server'] = 'torrent'
            elem_json['language'] = '*%s' % item.language
            elem_json['quality'] = '*%s' % item.quality
            elem_json['torrent_info'] = ''

            matches.append(elem_json.copy())
            item.emergency_urls[1][x] = elem_json.copy()

    else:
        for elem in matches_int:
            elem_json = {}
            #logger.error(elem)
            
            try:
                elem_json['url'] = elem.get('href', '')
                elem_json['server'] = 'torrent'
                elem_json['quality'] = item.quality
                elem_json['language'] = item.language
                elem_json['torrent_info'] = ''

            except:
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
            item.url = host + "?s=%s&x=0&y=0" % texto
            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
 
 
def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    itemlist = []
    item = Item()
    
    try:
        if categoria == 'peliculas':
            item.url = host + '/estrenos-/'
            item.extra = "peliculas"
            item.category_new= 'newest'

            item.action = "list_all"
            itemlist = list_all(item)

            if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
