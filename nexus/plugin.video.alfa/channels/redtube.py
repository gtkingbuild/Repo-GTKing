# -*- coding: utf-8 -*-
# -*- Channel RedTube -*-
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
             'channel': 'redtube', 
             'host': config.get_setting("current_host", 'redtube', default=''), 
             'host_alt': ["https://es.redtube.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['li'], 'id': re.compile(r"^(?:browse_|ps_profile_video_|rel_videos|tags_videos_|in_your_language_video_)\d+")}]},
         'categories': {'find_all': [{'tag': ['li'], 'class': ['category_item']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['a'], 'class': 'tm_pag_nav_next', '@ARG': 'href'}])]), 
         'next_page_rgx': [['\/page\/\d+\/', '/page/%s/']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "newest"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=host + "mostviewed?period=monthly"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="list_all", url=host + "top?period=monthly"))
    itemlist.append(Item(channel=item.channel, title="Favoritas del mes" , action="list_all", url=host + "mostfavored?period=monthly"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "longest?period=alltime"))
    itemlist.append(Item(channel=item.channel, title="Castellano" , action="list_all", url=host + "inyourlanguage/es"))
    itemlist.append(Item(channel=item.channel, title="Trending" , action="list_all", url=host + "hot"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channel/top-rated", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "pornstar/subscribers", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/popular", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", url=host +"new", action="search"))
    
    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", orientation="transgender"))
    itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", orientation="gay"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    if "transgender" in item.orientation:
        url = "%sredtube/%s/" %(host,item.orientation)
    else:
        url = "%s%s/" %(host,item.orientation)
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=url + "?sorting=newest"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=url + "?sorting=mostviewed&period=monthly"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="list_all", url=url + "?sorting=rating&period=monthly"))
    itemlist.append(Item(channel=item.channel, title="Favoritas del mes" , action="list_all", url=url + "?sorting=mostfavored&period=monthly"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=url + "?sorting=longest&period=alltime"))
    if "gay" in item.orientation:
        itemlist.append(Item(channel=item.channel, title="Castellano" , action="list_all", url=url + "inyourlanguage/es"))
        itemlist.append(Item(channel=item.channel, title="Trending" , action="list_all", url=url + "hot"))
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=url + "pornstar/subscribers/", extra="PornStar"))
        itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channel/%s/top-rated" %item.orientation, extra="Canal"))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "%s/categories/popular"%item.orientation, extra="Categorias"))
        itemlist.append(Item(channel=item.channel, title="Buscar", url="%snew/%s/" %(host,item.orientation), action="search"))
    else:
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "pornstar/subscribers/%s" %item.orientation, extra="PornStar"))
        itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channel/%s/top-rated" %item.orientation, extra="Canal"))
    
    return itemlist

def section(item):
    logger.info()
    findS = finds.copy()
    
    if item.extra == 'PornStar':
        findS['categories'] = {'find_all': [{'tag': ['li'], 'class': ['tm_pornstar_box']}]}
    
    if item.extra == 'Canal':
        findS['categories'] = {'find_all': [{'tag': ['li'], 'class': ['channel-box']}]}
    
    return AlfaChannel.section(item, finds=findS, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    ''' Carga desde AHkwargs la clave “matches” resultado de la ejecución del “profile=default” en AH. 
    En “matches_int” sigue pasando los valores de siempre. '''
    matches_org = AHkwargs.get('matches', [])
    findS = AHkwargs.get('finds', finds)
    ''' contador para asegurar que matches_int y matches_org van sincronizados'''
    x = 0
    
    for elem in matches_int:
        '''carga el valor del json que ya viene procesado del “profile=default” en AH'''
        elem_json = matches_org[x].copy() if x+1 <= len(matches_org) else {}
        
        try:
            elem_json['title'] = elem.img.get('alt', '')
            if elem.find(string=re.compile(r"(?i)videos|movies")):
                elem_json['cantidad'] = elem.find(string=re.compile(r"(?i)videos|movies")).strip()
            if item.extra == "Categorias":
                elem_json['url'] += "?sorting=newest"
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        '''filtros que deben coincidir con los que tiene el “profile=default” en AH para que no descuadren las dos listas'''
        if not elem_json['url']: continue
        '''guarda json modificado '''
        matches.append(elem_json.copy())
        '''se suma al contador de registros procesados VÁLIDOS'''
        x += 1
    
    return matches


def list_all(item):
    logger.info()
    
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.img.get('alt', '')
            elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find(class_='duration').get_text(strip=True) if elem.find(class_='duration') else ''
            elem_json['quality'] = elem.find('span', class_=['hd-thumbnail', 'is-hd', 'video_quality']).get_text(strip=True)
            elem_json['stime'] = elem_json['stime'].replace(elem_json['quality'], '')
            elem_json['premium'] = elem.find('i', class_='premiumIcon') \
                                     or elem.find('span', class_=['ico-private', 'premium-video-icon']) or ''
            if elem.find('span', class_='video_count'):
                elem_json['views'] = elem.find('span', class_='video_count').get_text(strip=True)
            
            if elem.find('a',class_='video_channel'):
                elem_json['canal'] = elem.find('a',class_='video_channel').get_text(strip=True)
            pornstars = elem.find_all('li', class_="pstar")
            if pornstars:
                for x, value in enumerate(pornstars):
                    pornstars[x] = value.get_text(strip=True)
                elem_json['star'] = ' & '.join(pornstars)
            
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
    
    item.url = "%s?search=%s&page=1" % (item.url, texto.replace(" ", "+"))
    
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
