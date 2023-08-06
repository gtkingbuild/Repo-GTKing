# -*- coding: utf-8 -*-
# -*- Channel RetroTV -*-
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
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'retrotv', 
             'host': config.get_setting("current_host", 'retrotv', default=''), 
             'host_alt': ["https://retrotv.org/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/pelicula"
tv_path = '/tv'
language = ['LAT']
url_replace = []

finds = {'find': dict([('find', [{'tag': ['ul'], 'class': ['MovieList']}]), 
                       ('find_all', [{'tag': ['article',], 'class': re.compile("TPost C")}])]),
         'categories': dict([('find', [{'tag': ['li'], 'id': ['menu-item-2460']}]), 
                             ('find_all', [{'tag': ['li']}])]), 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/||d{4}\/\d{2}\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['a'], 'string': re.compile('(?i)siguiente')}]), 
                            ('find_previous', [{'tag': ['a'], 'class': ['page-numbers']}]), 
                            ('get_text', [{'tag': '', '@STRIP': True}])]), 
         'year': dict([('find', [{'tag': ['span'], 'class': ['Year']}]), 
                       ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]), 
         'season_episode': {}, 
         'seasons': {'find_all': [{'tag': ['div'], 'class': ['AA-Season']}]}, 
         'season_num': dict([('find', [{'tag': ['span']}]), 
                             ('get_text', [{'tag': '', '@STRIP': True}])]), 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {'find_all': [{'tag': ['div'], 'class': ['Wdgt AABox']}]}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['div'], 'class': ['TPlayer']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real-*|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 20, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Todas las Series", action="list_all", c_type='series', 
                         url=host + "lista-series/", thumbnail=get_thumb("all", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Animación", action="list_all", c_type='series', 
                         url=host + "category/animacion/", thumbnail=get_thumb("animacion", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Live Action", action="list_all", c_type='series', 
                         url=host + "category/liveaction/", thumbnail=get_thumb("tvshows", auto=True)))
    
    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all", c_type='peliculas', 
                         url=host + "peliculas/", thumbnail=get_thumb("movies", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Géneros", action="section", url=host, c_type='series', 
                         thumbnail=get_thumb("genres", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Alfabético", action="alfabetico", url=host, c_type='series', 
                         thumbnail=get_thumb("alphabet", auto=True), extra='alpha'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url= host, c_type='search', 
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    return AlfaChannel.section(item, **kwargs)


def alfabetico(item):
    logger.info()

    itemlist = []

    for letra in ['0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:

        itemlist.append(item.clone(action="list_all", title=letra, url=host + 'letter/%s/' % letra.lower()))

    return itemlist


def list_all(item):
    logger.info()
    
    findS = finds.copy()

    if item.extra == 'alpha':
        findS['find'] = {'find_all': [{'tag': ['tr']}]}
        findS['year'] = dict([('find', [{'tag': ['td'], 'class': ['MvTbTtl']}]), 
                              ('find_next', [{'tag': ['td']}]), 
                              ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])])

    return AlfaChannel.list_all(item, matches_post=list_all_matches, finds=findS, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if item.extra == 'alpha':
                if not elem.find("a", class_="MvTbImg"): continue
                elem_json['url'] = elem.find("a", class_="MvTbImg").get("href", "")
                elem_json['title'] = elem.find("td", class_="MvTbTtl").get_text(strip=True)
            else:
                elem_json['url'] = elem.a.get("href", "")
                elem_json['title'] = elem.a.h3.get_text(strip=True)
            elem_json['thumbnail'] = elem.find("img")
            elem_json['thumbnail'] = elem_json['thumbnail']["data-src"] if elem_json['thumbnail']\
                                               .has_attr("data-src") else elem_json['thumbnail']["src"]
            if elem.find('span', class_="Qlty"): elem_json['quality'] = '*%s' \
                                                 % elem.find('span', class_="Qlty").get_text(strip=True).replace('Desconocido', '')
            elem_json['year'] = elem_json.get('year', AlfaChannel.parse_finds_dict(elem, findS.get('year', {}), year=True, c_type=item.c_type))
        except:
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


def episodesxseason(item):
    logger.info()

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    kwargs['matches_post_get_video_options'] = findvideos_matches
    findS = AHkwargs.get('finds', finds)

    for elem_season in matches_int:

        if elem_season.find("div", class_="AA-Season").get("data-tab", '0') == str(item.contentSeason):
            for elem in elem_season.find_all("tr"):
                elem_json = {}
                logger.error(elem)

                try:
                    if 'href' not in str(elem): continue
                    elem_json['url'] = elem.a.get('href', '')
                    elem_json['title'] = elem.find("td", class_="MvTbTtl").get_text('|', strip=True).split('|')[0]
                    elem_json['season'] = item.contentSeason
                    try:
                        elem_json['episode'] = int(elem.find("span", class_="Num").get_text(strip=True) or 1)
                    except:
                        elem_json['episode'] = 1
                    elem_json['thumbnail'] = elem.find("img").get('src', '') if 'img' in elem \
                                             else scrapertools.find_single_match(str(elem), 'src="([^"]+)"')
                except:
                    logger.error(elem)
                    logger.error(traceback.format_exc())
                    continue

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

    servers = {"femax20": "fembed", "embed": "mystream", "dood": "doodstream"}

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['server'] = elem.div.get('id', '')

            elem_json['url'] = elem.iframe.get('src', '')
            if host in elem_json['url']:
                trtype = 1 if item.contentType == 'movie' else '2'
                if 'trid' not in elem_json['url']:
                    trid = scrapertools.find_single_match(elem_json['url'], '\?p=(\d+)')
                    elem_json['url'] = '%s?trembed=0&trid=%s&trtype=%s' % (host, trid, trtype)
                else:
                    elem_json['url'] = re.sub("amp;|#038;", "", elem_json['url'])

                elem_json['url'] = AlfaChannel.create_soup( elem_json['url'], referer=item.url).find("div", class_="Video").iframe.get("src", '')
                
                elem_json['server'] = 'directo' if 'blenditall' in elem_json['url'] else ''
                if 'mega.' in elem_json['url']:
                    elem_json['url'] = elem_json['url'].replace("/embed/", "/file/")

            elem_json['url'] = re.sub("amp;|#038;", "", elem_json['url'])
            if elem_json['server'].lower() in servers: elem_json['server'] = servers[elem_json['server'].lower()]
            if elem_json['server'].lower() in ["waaw", "jetload", "player"]: continue
            elem_json['title'] = '%s'
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json['url']: continue

        matches.append(elem_json.copy())

    return matches, langs


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def play(item):
    logger.info()

    itemlist = list()
    json = {}
    url = item.url
    server = item.server

    if item.server == 'directo':

        soup = AlfaChannel.create_soup(item.url).find("body", class_="videoplayer")

        base = scrapertools.find_single_match(str(soup), 'sources\:\[([^\]]+\})\]')
        if base: json = jsontools.load(base)
        if not json and str(soup).startswith('{'): 
            json = jsontools.load(str(soup))
            if 'sources' in json.keys():
                json = json.get('sources', [])[0]

        url = json.get('file', '')
        if not url:
            url = scrapertools.find_single_match(str(soup), 'ajax\(\{url\:"([^"]+)"')
            if not url:
                return itemlist
        if url and not url.startswith('http'):
            url = 'https:%s' % url

        resp = AlfaChannel.create_soup(url, referer=item.url, soup=False)
        if PY3 and isinstance(resp.data, bytes):
            resp.data = "".join(chr(x) for x in bytes(resp.data))

        if resp.json:
            json = resp.json
            if 'sources' in json.keys():
                json = json.get('sources', [])[0]
            url = json.get('file', '')
            if url and not url.startswith('http'):
                url = 'https:%s' % url
            
            resp = AlfaChannel.create_soup(url, referer=item.url, soup=False)
            if PY3 and isinstance(resp.data, bytes):
                resp.data = "".join(chr(x) for x in bytes(resp.data))

        matches = re.compile('QUALITY=(\w+),[^\/]+(\/\/[^\n]+)', re.DOTALL).findall(resp.data)
        matches.reverse()
        for quality, _url in matches:
            if len(matches) > 1 and quality == 'mobile': continue
            url = _url
            break
        if not url:
            return itemlist
        if not url.startswith('http'):
            url = 'https:%s' % url
        server = "oprem"

    itemlist.append(item.clone(url=url, server=server, title=item.title.capitalize()))
    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    try:
        texto = texto.replace(" ", "+")

        if texto:
            item.url += "?s=" + texto
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

