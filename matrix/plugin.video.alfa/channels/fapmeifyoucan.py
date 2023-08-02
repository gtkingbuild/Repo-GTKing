# -*- coding: utf-8 -*-
# -*- Channel FapMEifYouCan -*-
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
             'channel': 'fapmeifyoucan', 
             'host': config.get_setting("current_host", 'fapmeifyoucan', default=''), 
             'host_alt': ["https://fapmeifyoucan.net/"], 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['block-video-preview']}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['col-md-3', 'col-md-2', 'col-tag']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page':{}, 
         'next_page_rgx': [['page=\d+', 'page=%s']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'href', '@TEXT': 'page=(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {}, 
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
    
    itemlist.append(Item(channel=item.channel, title="Nuevos", action="list_all", url=host + "video?page=1"))
    itemlist.append(Item(channel=item.channel, title="Más visto", action="list_all", url=host + "video?t=m&page=1"))
    itemlist.append(Item(channel=item.channel, title="Canal", action="section", url=host + "studio/", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars", action="section", url=host + "actor/?sort=actor.name&direction=asc&page=1", extra="Pornstar"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="section", url=host + "category", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    matches_org = AHkwargs.get('matches', [])
    findS = AHkwargs.get('finds', finds)
    ''' contador para asegurar que matches_int y matches_org van sincronizados'''
    x = 0
    for elem in matches_int:
        '''carga el valor del json que ya viene procesado del “profile=default” en AH'''
        elem_json = matches_org[x].copy() if x+1 <= len(matches_org) else {}

        try:
            '''filtros que deben coincidir con los que tiene el “profile=default” en AH para que no descuadren las dos listas  '''
            if "Canal" in item.extra:
                videos = elem.a.span.get_text(strip=True)
                elem_json['cantidad'] = videos.replace(" ", "")
                elem_json['title'] = elem_json['title'].replace(videos , "")

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        if not elem.a.get('href', ''): continue 
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
            elem_json['title'] = elem.h3.get_text(strip=True)
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find(string=re.compile('\d{2}:\d{2}:\d{2}')).replace("duration: ", "")
            
            pornstars = elem.find_all('a', class_='ml-3')
            for x, value in enumerate(pornstars):
                pornstars[x] = value.get_text(strip=True)
            elem_json['star']  = ' & '.join(pornstars)
        
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
    if soup.find_all('li', class_="starw"):
        pornstars = soup.find_all('li', class_="starw")
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        lista.insert (2, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%svideo/search/result?search=%s" % (host, texto.replace(" ", "+"))
    
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
