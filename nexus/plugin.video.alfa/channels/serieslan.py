# -*- coding: utf-8 -*-
# -*- Channel Ennovelas -*-
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

import string
from modules import renumbertools
from rJs import runJavascript

IDIOMAS = AlfaChannelHelper.IDIOMAS_T
list_language = list(set(IDIOMAS.values()))
list_quality_movies = []
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'serieslan', 
             'host': config.get_setting("current_host", 'serieslan', default=''), 
             'host_alt': ["https://serieslan.com/"], 
             'host_black_list': [], 
             'status': 'SIN CANONICAL NI DOMINIO', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/movies"
tv_path = '/series'
language = ['LAT']
url_replace = []

finds = {'find': {'find_all': [{'tag': ['a', 'div'], 'class': ['link', 'min-la', 'el']}]},
         'categories': {}, 
         'search': {'find': [{'tag': ['body'], '@JSON': 'DEFAULT'}]},
         'search': dict([('find', [{'tag': ['body']}]), 
                         ('get_text', [{'tag': '', '@STRIP': False, '@JSON': 'dt|DEFAULT'}])]), 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/||d{4}\/\d{2}\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div'], 'class': ['pag']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         'next_page_rgx': [['\/pag-\d+', '/pag-%s']], 
         'last_page': {}, 
         'year': {}, 
         'season_episode': {},
         'seasons': dict([('find', [{'tag': ['div'], 'class': ['box lista']}]), 
                          ('find_all', [{'tag': ['h3'], 'class': ['colapse']}])]), 
         'season_num': {}, 
         'seasons_search_num_rgx': [['(?i)-(?:t\w*-*)?(\d{1,2})(?:-a)?\/*$', None], ['(?i)-(\d{1,2})(?:-temp\w*|-cap[^$]*)?\/*$', None]], 
         'seasons_search_qty_rgx': None, 
         'episode_url': '', 
         'episodes': dict([('find', [{'tag': ['body'], 'id': ['box lista']}]), 
                           ('find_all', [{'tag': ['h3'], 'class': ['colapse']}])]), 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['body']}]},
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)\s*(?:\s*–|-)?\s+(\d+)\s+(?:temp\w*\s+-*\s+)?cap.\w+\s+(\d+)', ''], 
                         ['(?i)(?:\s*–|-)?\s+cap.\w+\s+(\d+)', ''], ['(?i)(?:\s+\d+)?\s+temp\w*(?:\s+\d+)?', ''], 
                         ['\s+\d{1,2}$', ''], ['(?i)\s+“*final”*$', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real-*|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 25, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'duplicates': [['(?i)-(?:t\w*-*)?(\d{1,2})(?:-a)?\/*$', ''], ['(?i)-(\d{1,2})(?:-temp\w*|-cap[^$]*)?\/*$', '']]},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = list()
    plot = "Tus series animadas de la infancia"

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(
        Item(channel=item.channel, action="list_all", title="Novedades",
            url=host, thumbnail=get_thumb("tvshow", auto=True), c_type="series",
            plot=plot))

    itemlist.append(
        Item(channel=item.channel, action="section", title=" - [COLOR paleturquoise]Listado [A-Z][/COLOR]",
            url=host+"lista.php?or=abc", thumbnail=get_thumb("alphabet", auto=True), c_type="series",
            plot=plot, extra='Alfabético'))

    itemlist.append(
        Item(channel=item.channel, action="list_all", title="Series más Recientes",
            url=host+"lista.php?or=rel", thumbnail=get_thumb("news", auto=True), c_type="series",
            plot=plot))

    itemlist.append(
        Item(channel=item.channel, action="list_all", title="Series más Populares",
            url=host+"lista.php?or=mas", thumbnail=get_thumb("popular", auto=True), c_type="series",
            plot=plot))

    itemlist.append(
        Item(channel=item.channel, action="list_all", title="Series Live Action",
            url=host+"liveaction", thumbnail=get_thumb("tvshow", auto=True), c_type="series",
            plot="Series LiveAction de los 90s y 2000", extra='LiveAction'))
    
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar...",
            thumbnail=get_thumb("search", auto=True)))

    itemlist = renumbertools.show_option(item.channel, itemlist)

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(action="list_all", title="0-9", character=[str(d) for d in range(10)] + ['¡'] + ['¿']))

    for letter in list(string.ascii_lowercase):
        itemlist.append(item.clone(action="list_all", title=letter.upper(), character=letter))

    return itemlist


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
            if item.c_type == 'search':
                elem_json['thumbnail'] = '/tb/%s.jpg' % elem[0]
                elem_json['title'] = elem[1]
                elem_json['url'] = elem[2]
                elem_json['year'] = scrapertools.find_single_match(elem_json['title'], '(\d{4})') or elem[3]
                elem_json['title'] = re.sub('\s*\d{4}', '', elem_json['title']).strip()
            
            else:
                elem_json['title'] = elem.find(["h3", "h2"]).get_text(strip=True) \
                                     if elem.find(["h3", "h2"]) else elem.find("div").get_text(strip=True)
                if item.extra == 'Alfabético':
                    if isinstance(item.character, list):
                        if elem_json['title'][0].lower() not in item.character: continue
                    else:
                        if elem_json['title'][0].lower() < item.character: continue
                        if elem_json['title'][0].lower() > item.character: break

                elem_json['url'] = elem.get("href", "") or elem.a.get("href", "")
                elem_json['year'] = scrapertools.find_single_match(elem_json['title'], '(\d{4})') \
                                                 or elem.find("span").get_text(strip=True) if elem.find("span") else '-'
                elem_json['title'] = elem_json['title'].replace(" y "," & ")
                elem_json['title'] = re.sub('\s*\d{4}', '', elem_json['title']).strip()
                elem_json['thumbnail'] = elem.find("img").get("src", "") or elem.find("img").get("data-original", "")

            elem_json['mediatype'] = 'tvshow'

            elem_json['context'] = renumbertools.context(item)
            elem_json['context'].extend(autoplay.context)

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json['url']: continue

        matches.append(elem_json.copy())

    return matches


def seasons(item):
    logger.info()

    findS = finds.copy()

    findS['controls'].update({'title_search': '%s temporada' % item.season_search or item.contentSerieName})

    return AlfaChannel.seasons(item, matches_post=seasons_matches, finds=findS, **kwargs)


def seasons_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for x, elem in enumerate(matches_int):
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['info'] = elem.get('dt', '')
            elem_json['title'] = elem.get_text(strip=True)
            elem_json['season'] = 1 if "unica" in elem_json['title'].lower() else \
                                    elem_json['title'].split(" ")[1] if "temporada" in elem_json['title'].lower() else 0
            if not "temporada" in elem_json['title'].lower() and not "extra" in elem_json['title'].lower():
                elem_json['season'] = x + 1 if not [int(s) for s in elem_json['title'] if s.isdigit()] else \
                                            [int(s) for s in elem_json['title'] if s.isdigit()][0]
            elem_json['season'] = int(elem_json['season'])

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        matches.append(elem_json.copy())

    return matches


def episodios(item):
    logger.info()

    itemlist = []

    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    findS = finds.copy()
    kwargs['matches_post_get_video_options'] = findvideos_matches
    
    findS['episodes'] = dict([('find', [{'tag': ['div'], 'id': [item.info]}]), 
                              ('find_all', [{'tag': ['a']}])])

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, finds=findS, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.get("href", "")
            title = elem.find("li").get_text('|', strip=True).split('|')
            title[1] = scrapertools.find_single_match(title[1], '(\d+)')
            elem_json['season'] = item.contentSeason
            elem_json['episode'] = int(title[1])
            elem_json['title'] = ''

            pat = "/" if not "KND" in item.title else "-"
            name = title[2]
            total_episode = 0

            if len(name.split(pat)) > 1:
                for j, pos in enumerate(name.split(pat)):
                    total_episode += 1
                    season, episode = renumbertools.numbered_for_tratk(item.channel, 
                                      item.contentSerieName, elem_json['season'], total_episode)
                    if len(name.split(pat)) == j+1:
                        elem_json['title'] += "{}x{:02d}".format(season, episode)
                    else:
                        elem_json['title'] += "{}x{:02d}_".format(season, episode)
            else:
                total_episode += 1
                season, episode = renumbertools.numbered_for_tratk(item.channel, 
                                  item.contentSerieName, elem_json['season'], total_episode)
                elem_json['title'] += "{}x{:02d}".format(season, episode)

            elem_json['title'] = "{} {}".format(elem_json['title'], name)

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

    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    data = AlfaChannel.response.data
    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
              'timeout': 5, 'cf_assistant': False, 'canonical': {}}

    _sa = scrapertools.find_single_match(data, 'var _sa = (true|false);')
    _sl = scrapertools.find_single_match(data, 'var _sl = ([^;]+);')
    sl = eval(_sl)

    buttons = scrapertools.find_multiple_matches(data, '<button.*?class="selop" sl="([^"]+)">')
    if not buttons:
        buttons = [0, 1, 2]

    for id in buttons:
        elem_json = {}
        #logger.error(id)

        elem_json['title'] = '%s'
        elem_json['server'] = ''
        elem_json['language'] = item.language or language
        url = golink(int(id), _sa, sl)

        data_new = AlfaChannel.create_soup(url, soup=False, **kwargs).data

        matches_alt = scrapertools.find_multiple_matches(data_new, 'javascript">(.*?)</script>')
        js = ""
        for part in matches_alt:
            js += part

        try: 
            matches_alt = scrapertools.find_multiple_matches(data_new, '<input[^>]*\s*id="(.*?)"\s*val="([^"]+)"')
            for zanga, val in matches_alt:
                js = js.replace('var %s = document.getElementById("%s");' % (zanga, zanga), "")
                js = js.replace('%s.getAttribute("val")' % zanga, '"%s"' % val)
        except:
            pass

        js = re.sub('(document\[.*?)=', 'prem=', js)

        video = scrapertools.find_single_match(js, "sources: \[\{src:(.*?), type")
        js = re.sub(' videojs\((.*?)\);', video+";", js)

        try:
            result = runJavascript.runJs().runJsString(js, True)
        except:
            logger.error('MATCHES vacías: %s' % matches_alt)
            result = ''

        elem_json['url'] = scrapertools.find_single_match(result, 'src="(.*?)"')
        if not elem_json['url']:
            elem_json['url'] = result.strip() if '//' in result else ''
        if elem_json['url']:
            matches.append(elem_json.copy())

    return matches, langs


def golink (num, sa, sl):

    SVR = "https://viteca.stream/" if sa == 'true' else host
    TT = "/" + AlfaChannel.do_quote(sl[3].replace("/", "><")) if num == 0 else ""
    url_end = link(num, sl)

    return SVR + "el/" + sl[0] + "/" + sl[1] + "/" + str(num) + "/" + sl[2] + url_end + TT


def link(ida, sl):

    a = ida
    b = [3, 10, 5, 22, 31]
    c = 1
    d = ""
    e = sl[2]

    for i in range(len(b)):
      d = d + substr(e, b[i] + a ,c)

    return d


def substr(st, a, b):
    return st[a:a + b]
'''
def x92(data1, data2):
    data3 = []
    data4 = 0
    data5 = ""
    data6 = ""
    for i in range(len(256)):
      data3[i] = i
    for i in range(len(256)):
      data4 = (data4 + data3[i] + ord(data1[i])) % 256
      data5 = data3[i]
      data3[i] = data3[data4]
      data3[data4] = data5
    i = 0
    data4 = 0
    for j in range(len(data2)):
        i = (i + 1) % 256
        data4 = (data4 + data3[i]) % 256
        data5 = data3[i]
        data3[i] = data3[data4]
        data3[data4] = data5
        data6 =1#+= str(unichr(data2[ord(str(j)) ^ data3[(data3[i] + data3[data4]) % 256]))
    return data6

def _ieshlgagkP(umZFJ):
    return umZFJ
def _RyHChsfwdd(ZBKux):
    return ZBKux
def _eladjkKtjf(czuwk):
    return czuwk
def _slSekoKrHb():
    return ''
def _VySdeBApGO():
    return 'Z'

def _nEgqhkiRub():
    return 28

def _lTjZxWGNnE():
    return 57
'''


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def get_page_num(item):
    logger.info()
    # Llamamos al método que salta al nº de página seleccionado

    return AlfaChannel.get_page_num(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    try:
        if texto:
            texto = texto.replace(" ", "+")
            item.url = '%sb.php/' %  (host)
            item.post = "k=" + texto

            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
