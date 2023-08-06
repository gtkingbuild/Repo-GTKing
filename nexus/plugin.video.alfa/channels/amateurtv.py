# -*- coding: utf-8 -*-
# -*- Channel AmateurTV -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAdultChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

IDIOMAS = AlfaChannelHelper.IDIOMAS_A
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES_A
list_quality_tvshow = []
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS_A
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'amateurtv', 
             'host': config.get_setting("current_host", 'amateurtv', default=''), 
             'host_alt': ["https://www.amateur.tv/"], 
             'host_black_list': [], 
             'pattern': ['property="og:url" content="?([^"|\s*]+)["|\s*]"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
# url_api = "%sv3/readmodel/cache/cams/%s/0/50/es"      ##  https://es.amateur.tv/v3/readmodel/cache/onlinecamlist
# https://es.amateur.tv/v3/readmodel/cache/menu   ##  https://es.amateur.tv/v3/readmodel/cache/sectioncamlist?section=viewers  couples
url_api = '%sv3/readmodel/cache/sectioncamlist?%s'



timeout = 10
kwargs = {}
kwargs['soup'] = False
kwargs['json'] = True
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []


finds = {'find': {},
         'categories': {}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [], 
         'last_page': {}, 
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''], ['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 25, 'reverse': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    # soup = AlfaChannel.create_soup(host, alfa_s=True) #Para coger canonical
    AlfaChannel.httptools.downloadpage(host, canonical=canonical).data
    
    itemlist.append(Item(channel = item.channel,title="Mujer" , action="list_all", url=url_api %(host, 'genre=["w"]')))
    itemlist.append(Item(channel = item.channel,title="Parejas" , action="list_all", url=url_api %(host, 'genre=["c"]')))
    itemlist.append(Item(channel = item.channel,title="Hombres" , action="list_all", url=url_api %(host, 'genre=["m"]')))
    itemlist.append(Item(channel = item.channel,title="Trans" , action="list_all", url=url_api %(host, 'genre=["t"]')))
    itemlist.append(Item(channel = item.channel,title="Categorias" , action="section", url=host + "/v3/tag/list"))
    
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    matches_int = matches_int.get('body', {}).get('tags', {}).copy()
    if not matches_int: return matches
    
    for elem in matches_int:
        elem_json = {}
        try:
            elem_json['title'] = elem.get('tag', '')
            elem_json['url'] = '%sv3/readmodel/cache/sectioncamlist?genre=["w","m","c","t"]&tag=%s' % (host, elem_json['title'])
            elem_json['thumbnail'] = ''
            elem_json['cantidad'] = elem.get('count', '')
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
    
    return matches


def list_all(item):
    logger.info()
    
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    matches_int = matches_int.get('body', {}).get('cams', {}).copy()
    
    # AlfaChannel.last_page = int(len(matches_int) / finds['controls'].get('cnt_tot', 25))
    # AlfaChannel.last_page = int((float(len(matches_int)) / float(finds['controls'].get('cnt_tot', 25)))  + 0.999999)
    
    for elem in matches_int:
        elem_json = {}
        try:
            name =  elem.get('username', '')
            age = elem.get('ages', '')[0]
            country  = elem.get('countryName', '')
            
            elem_json['url'] = "%sv3/readmodel/show/%s/es" %(host, name)
            elem_json['title'] = "%s [%s] %s" %(name, age, country)
            elem_json['thumbnail'] = elem.get('capture', '') if elem.get('capture', []) else ''
            elem_json['quality'] = 'HD' if elem.get('hd') else ''
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        
        matches.append(elem_json.copy())
    
    return matches


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)

def play(item):
    logger.info()
    itemlist = []
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    qualities = soup.get('qualities', [])
    vid = soup.get('videoTechnologies', {}).get('fmp4', {})
    for elem in qualities:
        quality = scrapertools.find_single_match(elem, "\d+x(\d+)") 
        url = "%s&variant=%s" % (vid, quality)
        itemlist.append(["[amateurtv] %sp" %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist

