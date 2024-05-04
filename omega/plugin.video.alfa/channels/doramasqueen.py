# -*- coding: utf-8 -*-
# -*- Channel DoramasQueen -*-
# -*- Created for Alfa Addon -*-
# -*- By the Alfa Development Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAllChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

IDIOMAS = AlfaChannelHelper.IDIOMAS_ANIME
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'doramasqueen', 
             'host': config.get_setting("current_host", 'doramasqueen', default=''), 
             'host_alt': ["https://www.doramasqueen.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "pelicula."
tv_path = 'dorama/'
epi_path = 'capitulo/'
language = ['VOSE']
url_replace = []

finds = {'find': dict([('find', [{'tag': ['div'], 'id': ['contentChapters', 'contentDorama']}]), 
                       ('find_all', [{'tag': ['div'], 'class': ['card card-width', 'card-general']}])]), 
         'categories': {}, 
         'search': dict([('find', [{'tag': ['body']}]), 
                         ('get_text', [{'tag': '', '@STRIP': False, '@JSON': 'DEFAULT'}])]), 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\?page_no\=\d+', '?page_no=%s']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2]}]), 
                            ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]),  
         'year': {}, 
         'season_episode': {}, 
         'seasons': dict([('find', [{'tag': ['div'], 'class': ['seasonList']}]), 
                          ('find_all', [{'tag': ['li'], 'class': ['list-season-group']}])]),
         'season_num': {'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}]},
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'season_url': host, 
         'episode_url': '%sepisodio/%s-%sx%s', 
         'episodes': dict([('find', [{'tag': ['div'], 'id': ['contentChapters']}]), 
                           ('find_all', [{'tag': ['div'], 'class': ['card-general']}])]), 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'id': ['list-players', 'contentChapters', 'viewMovies']}]), 
                             ('find_all', [{'tag': ['li', 'style']}])]),
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 18, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'IDIOMAS_TMDB': {0: 'es', 1: 'es', 2: 'es'}, 'join_dup_episodes': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Últimos Episodios', url=host + 'ultimoscapitulos.php?page_no=1', action='list_all',
                         thumbnail=get_thumb('new episodes', auto=True), c_type='episodios'))

    itemlist.append(Item(channel=item.channel, title='Doramas', url=host + 'doramas.php?page_no=1', action='list_all',
                         thumbnail=get_thumb('doramas', auto=True), c_type='series')) 

    itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por Países[/COLOR]', action='section', 
                         url=host + 'searchBy.php?page_no=1', extra='Países', 
                         thumbnail=get_thumb('country', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por Años[/COLOR]', action='section', 
                         url=host + 'searchBy.php?page_no=1', extra='Años', 
                         thumbnail=get_thumb('year', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title='Peliculas', url=host + 'peliculas.php?page_no=1', action='list_all',
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    itemlist = []

    if item.extra == 'Países':
        sections = {
                    'China': '["1"]', 
                    'Japon': '["2"]', 
                    'Taiwan': '["4"]', 
                    'Korea': '["5"]', 
                    'Tailandia': '["6"]'
                   }
        for key, value in sections.items():
            post = {'countries': value, 'generos': '', 'years': '', 'emition': '', 'submit': ''}
            itemlist.append(item.clone(title=key, post=post, action='list_all'))

    elif item.extra == 'Años':
        import datetime
        year = datetime.datetime.today().year

        for value in range(year, 2006, -1):
            post = {'countries': '', 'generos': '', 'years': '["%s"]' % value, 'emition': '', 'submit': ''}
            itemlist.append(item.clone(title=str(value), post=post, infoLabels={'year': value}, action='list_all'))

    return itemlist


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    if (item.c_type == 'search' or item.extra) and AlfaChannel.last_page == 99999:
        AlfaChannel.last_page = int((float(len(matches_int)) / float(AlfaChannel.cnt_tot)) + 0.999999)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if item.c_type == 'search':
                elem_json['url'] = 'dorama/%s' % (elem.get('value', '') or elem.get('label', ''))
                elem_json['title'] = elem.get("id", '')
                elem_json['thumbnail'] = ('admin/uploads/doramas/%s' % elem.get('icon', '')) if elem.get('icon', '') else ''
                elem_json['mediatype'] = 'tvshow' if tv_path in elem_json['url'] else 'movie'

            else:
                elem_json['url'] = elem.a.get('href', '')

                if item.c_type == 'episodios':
                    try:
                        elem_json['season'] = int(scrapertools.find_single_match(elem.find('button', class_='btn-subtitle')\
                                                                                     .get_text(strip=True), '(\d+)'))
                        elem_json['episode'] = int(scrapertools.find_single_match(elem.find('button', class_='btn-sub-text')\
                                                                                     .get_text(strip=True), '(\d+)'))
                    except Exception:
                        elem_json['season'] = 1
                        elem_json['episode'] = 1
                        logger.error(traceback.format_exc())
                    elem_json['mediatype'] = 'episode'

                if item.c_type in ['series', 'episodios'] and not item.extra:
                    elem_json['title'] = elem.find("h3", class_="btn").get_text(strip=True)
                else:
                    elem_json['title'] = elem_json['url'].split('/')[-1].split('=')[-1].replace('-', ' ').title()

                if not elem_json.get('mediatype'): elem_json['mediatype'] = 'tvshow' if tv_path in elem_json['url'] else 'movie'
                elem_json['thumbnail'] = elem.img.get('src', '')

            try:
                elem_json['year'] = int(scrapertools.find_single_match(elem_json['title'], '\d{4}'))
                elem_json['title'] = re.sub('\s*\d{4}[^$]*$', '',elem_json['title'])
            except Exception:
                elem_json['year'] = '-' if not item.extra == 'Años' else item.infoLabels['year']

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json['url']: continue

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


def episodesxseason(item, **AHkwargs):
    logger.info()

    kwargs['matches_post_get_video_options'] = findvideos_matches
    soup = AHkwargs.get('soup', '')

    return AlfaChannel.episodes(item, data=soup, matches_post=episodesxseason_matches, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            try:
                elem_json['season'] = int(scrapertools.find_single_match(elem.find('button', class_='btn-subtitle')\
                                                                             .get_text(strip=True), '(\d+)'))
                elem_json['episode'] = int(scrapertools.find_single_match(elem.find('button', class_='btn-sub-text')\
                                                                             .get_text(strip=True), '(\d+)'))
            except Exception:
                elem_json['season'] = 1
                elem_json['episode'] = 1
                logger.error(traceback.format_exc())
            if elem_json['season'] != item.contentSeason: continue

            elem_json['url'] = elem.a.get("href", "")
            elem_json['title'] = elem.find("h3", class_="btn").get_text(strip=True)
            elem_json['thumbnail'] = elem.img.get('src', '')

            elem_json['mediatype'] = 'episode'

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())

        if not elem_json.get('url', ''): continue

        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()

    kwargs['matches_post_episodes'] = episodesxseason_matches

    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=findvideos_matches, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    soup = AHkwargs.get('soup', {})
    if not 'contentChapters' in str(soup):
        soup_movie = AlfaChannel.create_soup(host + 'library/functions.php', post={'action': 'getMoviesDoramas'}, 
                                             headers={'Referer': item.url}, alfa_s=True)
        finds_out = dict([('find', [{'tag': ['body']}]), 
                          ('get_text', [{'tag': '', '@STRIP': False, '@JSON': 'response|DEFAULT'}])])
        matches_int = AlfaChannel.parse_finds_dict(soup_movie, finds_out)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if item.contentType == 'movie':
                elem_json['url'] = elem.get('url_movie', '')
                if not elem.get('url_pelicula', '') in item.url: continue
            else:
                if 'botonestopplay' not in elem.get('class', []): continue
                elem_json['url'] = scrapertools.find_single_match(elem.get('onclick', ''), "\('([^']+)'")
            if 'fembed' in elem_json['url']: continue

            elem_json['server'] = ''
            elem_json['title'] = '%s'
            elem_json['language'] = language

            if not elem_json.get('url'): continue

            matches.append(elem_json.copy())

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

    return matches, langs


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    try:
        texto = texto.replace(" ", "+")
        item.url = host + 'library/functions.php'
        item.post = {'action': 'searchByTerm', 'term': texto}

        if texto:
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except Exception:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
