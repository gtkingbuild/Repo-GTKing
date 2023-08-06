# -*- coding: utf-8 -*-
# -*- Channel YTS -*-
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
             'channel': 'yts', 
             'host': config.get_setting("current_host", 'yts', default=''), 
             'host_alt': ["https://ytstv.me/", "https://ytstvmovies.co/"], 
             'host_black_list': ["https://yts.mx/"], 
             'pattern': '<ul\s*class="nav-links">\s*<li>\s*<a\s*href="([^"]+)"', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_torrent = 'https://ytsmx.xyz'
host_language = canonical['host_alt'][1]
host_year = canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/movies"
tv_path = '/series'
episode_path = '/episode'
language = ['VOS']
url_replace = []

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['ml-item']}]}, 
         'sub_menu': {}, 
         'categories': dict([('find', [{'tag': ['li'], 'class': ['menu-item-29403', 'menu-item-29161']}]), 
                            ('find_all', [{'tag': ['li'], 'class': ['menu-item-object-category']}])]), 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href', '@TEXT': '\/page\/(\d+)'}])]), 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {'find_all': [{'tag': ['div'], 'class': ['les-title']}]}, 
         'season_num': dict([('find', [{'tag': ['div'], 'class': ['les-title']}]), 
                             ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]),  
         'seasons_search_num_rgx': [], 
         'seasons_search_qty_rgx': [], 
         'episode_url': '', 
         'episodes': {'find_all': [{'tag': ['div'], 'class': ['tvseason']}]}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['a'], 'class': ['lnk-lnk']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax|\s*Series?\s*\d{4}?|\s*Shows?\s*\d{4}?', ''],
                         ['(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', ''], 
                         ['(?i)[-|\(]?\s*HDRip\)?|microHD|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?', ''], 
                         ['(?i)\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|[\(|\[]\S*\.*$', ''],
                         ['(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*|\[*\(*dvd\s*r\d*\w*\]*\)*|[\[|\(]*dv\S*[\)|\]]*', ''], 
                         ['(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?', ''], 
                         ['(?i)(?:\s*&#8211;)?\s*temp.*?\d+.*', ''], ['\d?\d?&#.*', ''], ['\d+[x|×]\d+.*', ''], 
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)(?:libro|volumen)?\s+\d{1,2}$', ''], ['(?i)season\s*\d+\s*comp\w*\s*', ''], 
                         ['(?i)season\s*\d+\s*full\w*\s*epi\w*\s*', ''], ['(?i)\s*season\s*\d{1,2}\s*epi\w*\s*\d*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 20, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 
                      'host_torrent': host_torrent, 'duplicates': []},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = []
    plot = ''

    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Películas", action="sub_menu", 
                         url=host + "movies/page/1", 
                         thumbnail=get_thumb("channels_movie.png"), c_type="peliculas", 
                         contentPlot=plot))

    itemlist.append(Item(channel=item.channel, title="Series", action="sub_menu", 
                         url=host + "series/page/1", 
                         thumbnail=get_thumb("channels_tvshow_hd.png"), c_type="series", 
                         contentPlot=plot))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", 
                         url=host, thumbnail=get_thumb("search.png"), c_type="search", 
                         category=categoria, contentPlot=plot))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                         folder=False, thumbnail=get_thumb("next.png")))
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                         thumbnail=get_thumb("setting_0.png")))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def configuracion(item):
    from platformcode import platformtools

    ret = platformtools.show_channel_settings()

    return platformtools.itemlist_refresh()


def sub_menu(item):
    logger.info()

    itemlist = []

    if item.c_type == 'peliculas':
        itemlist.append(Item(channel=item.channel, title="Explorar Películas", 
                             action="list_all", url=item.url, 
                             thumbnail=get_thumb('movies', auto=True), c_type=item.c_type, contentPlot=item.plot))

    if item.c_type == 'series':
        itemlist.append(Item(channel=item.channel, title="Explorar Series", 
                             action="list_all", url=item.url, 
                             thumbnail=get_thumb('tvshows', auto=True), c_type=item.c_type, contentPlot=item.plot))

    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]%s por Género[/COLOR]" % item.c_type.title(), 
                         action="section", url=item.url, extra='Géneros', 
                         thumbnail=get_thumb('genres', auto=True), c_type=item.c_type, contentPlot=item.plot))

    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]%s por Año[/COLOR]" % item.c_type.title(), 
                         action="section", url=host_year, extra='Año', 
                         thumbnail=get_thumb('year', auto=True), c_type=item.c_type, contentPlot=item.plot))

    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]%s por Idiomas[/COLOR]" % item.c_type.title(), 
                         action="section", url=host_language, extra='Idiomas', 
                         thumbnail=get_thumb('language', auto=True), c_type=item.c_type, contentPlot=item.plot))

    if item.c_type == 'peliculas':
        itemlist.append(Item(channel=item.channel, title="Top Películas IMDB", 
                             action="list_all", url=host + 'top-imdb/page/1', 
                             thumbnail=get_thumb('rating', auto=True), c_type=item.c_type, contentPlot=item.plot))
        
        itemlist.append(Item(channel=item.channel, title="Calidad 4K", 
                             action="list_all", url=host + 'quality/4k/page/1', 
                             thumbnail=get_thumb('quality', auto=True), c_type=item.c_type, contentPlot=item.plot))

    if item.c_type == 'series':
        itemlist.append(Item(channel=item.channel, title="Temporadas Completas", 
                             action="list_all", url=host + 'tag/tv-series-full-episode/page/1', 
                             thumbnail=get_thumb('tvshows', auto=True), c_type='temporadas', contentPlot=item.plot))

        itemlist.append(Item(channel=item.channel, title="Últimos Episodios", 
                             action="list_all", url=host + 'episode/page/1', 
                             thumbnail=get_thumb('episodes', auto=True), c_type='episodios', contentPlot=item.plot))

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    if item.extra == 'Año':
        findS['categories'] =  dict([('find', [{'tag': ['li'], 'class': ['menu-item-44346']}]), 
                                     ('find_all', [{'tag': ['li'], 'class': ['menu-item-type-custom']}])])
        findS['controls']['reverse'] = True
        if host == host_language:
            findS['url_replace'] = [[host_year, host_language]]
            kwargs['canonical_check'] = False

    if item.extra == 'Idiomas':
        findS['categories'] =  dict([('find', [{'tag': ['li'], 'class': ['menu-item-41282']}]), 
                                     ('find_all', [{'tag': ['li'], 'class': ['menu-item-type-custom']}])])
        if host == host_year: 
            findS['url_replace'] = [[host_language, host_year]]
            kwargs['canonical_check'] = False

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
        #logger.error(elem)

        try: 
            elem_json['url'] = elem.a.get("href", "")
            if item.c_type == 'peliculas' and tv_path in elem_json['url']: continue
            if item.c_type == 'series' and tv_path not in elem_json['url']: continue
            if item.c_type in ['temporadas', 'episodios'] and episode_path not in elem_json['url']: continue
            if item.c_type == 'search' and episode_path in elem_json['url']: continue
            elem_json['title'] = elem.a.get("title", "") or elem.a.get("oldtitle", "")
            if tv_path not in elem_json['url'] and episode_path not in elem_json['url']: elem_json['quality'] = elem.span.get_text(strip=True)
            elem_json['language'] = language
            elem_json['thumbnail'] = elem.img.get("data-original", "").strip()
            if scrapertools.find_single_match(elem_json['title'], '[\(|\s+](\d{4})\)'):
                elem_json['year'] = int(scrapertools.find_single_match(elem_json['title'], '[\(|\s+](\d{4})\)'))
            elem_json['plot'] = elem.find('p', class_='f-desc').find_next('p').get_text(strip=True) if elem.find('p', class_='f-desc') else ''
            elem_json['mediatype'] = 'movie' if (not tv_path in elem_json['url'] and not episode_path in elem_json['url']) else 'tvshow'
            if episode_path in elem_json['url'] and not item.c_type in ['episodios']:
                elem_json['action'] = 'findvideos'
                elem_json['extra'] = 'seasons'
                elem_json['plot_extend'] = '[COLOR darkgrey](Season %s)[/COLOR]' \
                                           % scrapertools.find_single_match(elem_json['title'], '(?i)season\s*(\d+)')
                item.c_type = 'tvshow'
            elif episode_path in elem_json['url'] and item.c_type in ['episodios']:
                elem_json['action'] = 'findvideos'
                elem_json['mediatype'] = 'episode'
                if scrapertools.find_single_match(elem_json['title'], '(?i)season\s*(\d{1,2})\s*epi\w*\s*(\d+)'):
                    elem_json['season'], elem_json['episode'] = scrapertools.find_single_match(elem_json['title'], 
                                                                '(?i)season\s*(\d{1,2})\s*epi\w*\s*(\d+)')
                    elem_json['season'] = int(elem_json['season'])
                    elem_json['episode'] = int(elem_json['episode'])
                    if scrapertools.find_single_match(elem_json['title'], '(?i)epi\w*\s*\d+\s*-\s*(\d+)'):
                        elem_json['title'] = 'al %s' % scrapertools.find_single_match(elem_json['title'], '(?i)epi\w*\s*\d+\s*-\s*(\d+)').zfill(2)
                        elem_json['extra'] = 'seasons'

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url'): continue

        matches.append(elem_json.copy())

    return matches


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item, **kwargs)


def episodios(item):
    logger.info()

    itemlist = []

    templist = seasons(item)
    data = AlfaChannel.response.soup

    for tempitem in templist:
        itemlist += episodesxseason(tempitem, data=data)

    return itemlist


def episodesxseason(item, data=[]):
    logger.info()

    return AlfaChannel.episodes(item, data=data, matches_post=episodesxseason_matches, generictools=True, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    elem_json_list = {}
    findS = finds.copy()

    for season in matches_int:
        if int(AlfaChannel.parse_finds_dict(season, findS['season_num'])) != item.contentSeason: continue
        
        for elem in season.find_all('a'):
            elem_json = {}
            #logger.error(elem)

            try:
                try:
                    elem_json['title'] = elem.get_text(strip=True)
                    elem_json['season'] = item.contentSeason
                    elem_json['episode'] = int(scrapertools.find_single_match(elem_json['title'], '(?i)epi\w*\s*(\d+)'))
                    if scrapertools.find_single_match(elem_json['title'], '(?i)epi\w*\s*\d+\s*-\s*(\d+)'):
                        elem_json['title'] = 'al %s' % scrapertools.find_single_match(elem_json['title'], '(?i)epi\w*\s*\d+\s*-\s*(\d+)').zfill(2)
                        elem_json['extra'] = 'seasons'
                except Exception:
                    logger.error(elem)
                    elem_json['episode'] = 0

                elem_json['url'] = elem.get('href', '')
                elem_json['language'] = item.language

            except Exception:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue

            matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()

    findS = finds.copy()

    if episode_path in item.url:
        findS['controls']['sort_findvideos'] = False

    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, finds=findS, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        
        try:
            elem_json['url'] = elem.get('href', '').replace(' ', '%20')
            if 'subtitles' in elem_json['url']:
                if not item.subtitle: item.subtitle = []
                item.subtitle += [elem_json['url']]
                continue
            elem_json['quality'] = '*%s' % elem.find_all("span", class_="lnk lnk-dl")[-2].get_text(strip=True)
            elem_json['language'] = item.language
            elem_json['torrent_info'] = elem_json['size'] = ''

            if episode_path in item.url:
                info = elem.find("span", class_="lnk lnk-dl").get_text(strip=True)
                elem_json['season'] = int(scrapertools.find_single_match(info, '(?i)s(\d{2})e\d{2}') or 1)
                elem_json['episode'] = int(scrapertools.find_single_match(info, '(?i)s\d{2}e(\d{2})') or 0)
                if item.extra == 'seasons':
                    if elem_json['episode']:
                        elem_json['torrent_info'] = 'Epi %sx%s - ' % (elem_json['season'], str(elem_json['episode']).zfill(2))
                    else:
                        elem_json['torrent_info'] = 'Season %s - ' % elem_json['season']
                elem_json['mediatype'] = 'episode'

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())

        if not elem_json.get('url', ''): 
            continue
        elem_json['server'] = 'torrent'

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
            item.url = host + '?s=' + texto
            item.c_type = 'search'
            item.texto = texto
            itemlist = list_all(item)

            return itemlist
        else:
            return []

    except Exception:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []