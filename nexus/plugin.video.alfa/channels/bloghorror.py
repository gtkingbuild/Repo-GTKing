# -*- coding: utf-8 -*-
# -*- Channel BlogHorror -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

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
list_quality_tvshow = []
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS_T
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'bloghorror', 
             'host': config.get_setting("current_host", 'bloghorror', default=''), 
             'host_alt': ["https://bloghorror.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
fanart = host + 'wp-content/uploads/2015/04/bloghorror-2017-x.jpg'

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas"
tv_path = '/series'
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['div', 'section'], 'id': ['primary']}]), 
                       ('find_all', [{'tag': ['article']}])]), 
         'sub_menu': {}, 
         'categories': {},  
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['navigation']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2]}]), 
                            ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]), 
         'year': dict([('find', [{'tag': ['h3'], 'class': ['article-title']}]), 
                       ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '\((\d{4})\)'}])]), 
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
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['entry-content-wrap']}]), 
                             ('find_all', [{'tag': ['p']}])]), 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax', ''],
                         ['(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', ''], 
                         ['(?i)[-|\(]?\s*HDRip\)?|microHD|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?', ''], 
                         ['(?i)\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|\s*ts|[\(|\[]\S*\.*$', ''],
                         ['(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*|\[*\(*dvd\s*r\d*\w*\]*\)*|[\[|\(]*dv\S*[\)|\]]*', ''], 
                         ['(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?', ''], 
                         ['(?i)(?:\s*&#8211;)?\s*temp.*?\d+.*', ''], ['\d?\d?&#.*', ''], ['\d+[x|×]\d+.*', ''], 
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)(?:libro|volumen)?\s+\d{1,2}$', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'min_temp': '', 'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 15, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'host_torrent': host, 'duplicates': []},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, fanart=fanart, title="Todas", action="list_all", c_type='peliculas', 
                         url=host+'category/terror-2', thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, fanart=fanart, title="Asiaticas", action="list_all", c_type='peliculas', 
                         url=host+'category/asiatico1', thumbnail=get_thumb('asiaticas', auto=True)))

    itemlist.append(Item(channel=item.channel, fanart=fanart, title = 'Buscar', action="search", c_type='search', 
                         url=host, pages=3, thumbnail=get_thumb('search', auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()
                
    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=False, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.find("h3", class_="article-title").a.get("href", "")
            elem_json['title'] = elem.find("h3", class_="article-title").get_text(strip=True)
            elem_json['year'] = elem_json.get('year', AlfaChannel.parse_finds_dict(elem, findS.get('year', {}), year=True, c_type=item.c_type))
            elem_json['thumbnail'] = elem.find("div", class_="data-bg-hover").get("data-background", "")
            cat = elem.find("a", class_="covernews-categories").get("alt", "")
            if cat in ["View all posts in Las Mejores Peliculas de Terror", "View all posts in Editoriales"]:
                continue
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url'): continue

        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}

        try:
            if not 'FICHA TECNICA' in str(elem) and not 'Calidad' in str(elem): continue
            #logger.error(elem)
            info = elem.get_text('|', strip=True).split('|')

            elem_json['quality'] = '*%s' % info[2].replace(': ', '')
            elem_json['language'] = '*%s' % info[4].replace(': ', '')
            if elem.find('a', href=re.compile('subdivx')): elem_json['subtitle'] = elem.find('a', href=re.compile('subdivx'))['href']
            elem_json['url'] = elem.a.get('href', '')
            elem_json['server'] = 'torrent' if 'magnet' in elem_json['url'] or ',torrent' in elem_json['url'] else 'directo'
            if '1fichier' in elem_json['url']: elem_json['server'] = 'onefichier'

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


def play(item):
    logger.info()
    
    if item.subtitle:
        from platformcode import subtitletools
        try:
            sub = subtitletools.get_from_subdivx(item.subtitle)
            return [item.clone(subtitle=sub)]
        except:
            logger.error('ERROR en Subtítulos: %s' % traceback.format_exc())
            return [item]
    else:
        return [item]


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + '?s=' + texto

        if texto:
            item.c_type = 'peliculas'
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
        if categoria in ['peliculas', 'terror', 'torrent']:
            item.url = host
        item.c_type = 'peliculas'
        
        itemlist = list_all(item)
        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
