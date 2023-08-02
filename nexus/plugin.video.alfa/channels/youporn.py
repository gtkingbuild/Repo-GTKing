# -*- coding: utf-8 -*-
# -*- Channel YouPorn -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

import re
import traceback
if not PY3: _dict = dict; from collections import OrderedDict as dict

from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryAdultChannel

IDIOMAS = {}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = []
list_quality_tvshow = []
list_servers = []
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'youporn', 
             'host': config.get_setting("current_host", 'youporn', default=''), 
             'host_alt': ["https://www.youporn.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []


finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['container']}]),
                       ('find_all', [{'tag': ['div'], 'class': ['video-box']}])]),
         'categories': {'find_all': [{'tag': ['div'], 'class': ['porn-star-list']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['&page=\d+', '&page=%s'], ['\?page=\d+', '?page=%s']], 
         'last_page':  dict([('find', [{'tag': ['div'], 'id': ['pagination']},
                             {'tag': ['ul'], '@ARG': 'data-max'}])]),
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         # 'profile_labels': {'section_cantidad': dict([('find', [{'tag': ['span', 'div'], 'class': ['video-count', 'videoCount']}]),
                                                      # ('get_text', [{'strip': True}])])}, 
         'controls': {'url_base64': False, 'cnt_tot': 32, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "browse/time/?page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Visto" , action="list_all", url=host + "browse/views/?page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Valorada" , action="list_all", url=host + "top_rated/?page=1"))
    itemlist.append(Item(channel=item.channel, title="Favoritas" , action="list_all", url=host + "/most_favorited/?page=1"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "pornstars/most_popular/?page=1", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channels/most_popular/?page=1", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url= host))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    
    findS['url_replace'] = [['(\/(?:category|channel|pornstar)\/[^$]+$)', r'\1time/?page=1']]
    
    if item.extra:
        findS['next_page'] = {'find': [{'tag': ['div'], 'id': ['next']}, 
                                       {'tag': ['a'], '@ARG': 'href'}]}
        findS['last_page'] = {}
    
    if not "PornStar" in item.extra:
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': ['full-row-channel', 'row grouped']}]),
                                    ('find_all', [{'tag': ['a'], 'class': ['channel-box-image', 'categoryBox']}])])
    return AlfaChannel.section(item, finds=findS, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    logger.debug(matches_int[0])
    for elem in matches_int:
        elem_json = {}
        try:
            
            elem_json['url'] = elem.get("href", '') or elem.a.get("href", '')
            elem_json['title'] = (elem.img.get('alt', '') if elem.img else '') \
                                                   or elem.a.get_text(strip=True)
            if elem.img: elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                                     or elem.img.get('data-src', '') \
                                                                                     or elem.img.get('src', '')
            if elem.find(['span', 'div'], class_=['videoCount', 'video-count', 'views']):
                elem_json['cantidad'] = elem.find(['span', 'div'], class_=['videoCount', 'video-count', 'views']).get_text(strip=True)
            elif elem.find(string=re.compile(r"(?i)videos|movies")):
                elem_json['cantidad'] = elem.find(string=re.compile(r"(?i)videos|movies")).strip()
        
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
    logger.debug(matches_int[6])
    for elem in matches_int:
        elem_json = {}
        
        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.img.get('alt', '')
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find(class_='video-duration').get_text(strip=True) if elem.find(class_='video-duration') else ''
            elem_json['quality'] = elem.find(class_='video-best-resolution').get_text(strip=True) if elem.find(class_='video-best-resolution')  else ''
            pornstars = elem.find_all('a', href=re.compile(r"/pornstar/[a-z0-9-]+/"))
            if pornstars:
                for x, value in enumerate(pornstars):
                    pornstars[x] = value.get_text(strip=True)
                elem_json['star'] = ' & '.join(pornstars)
            if elem.find('a', href=re.compile(r"/channel/[a-z0-9-]+/")):
                elem_json['canal'] = elem.find('a', href=re.compile(r"/channel/[a-z0-9-]+/")).get_text(strip=True)

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


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/time/?query=%s&page=1" % (item.url, texto.replace(" ", "+"))
    
    try:
        if texto:
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
