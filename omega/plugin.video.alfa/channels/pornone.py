# -*- coding: utf-8 -*-
# -*- Channel PornOne -*-
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
             'channel': 'pornone', 
             'host': config.get_setting("current_host", 'pornone', default=''), 
             'host_alt': ["https://pornone.com/"], 
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


finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['md:container']}]),
                       #('find_all', [{'tag': ['a'], 'href': re.compile(r"^https://pornone.com/[A-z0-9-]+/[A-z0-9-]+/[0-9]+/?")}])]),
                       ('find_all', [{'tag': ['a'], 'class': ['tracking-normal']}])]), ## COGE LiveCAM

         'categories': dict([('find', [{'tag': ['main']}]),
                       ('find_all', [{'tag': ['a'], 'class': ['tracking-tighter', 'overflow-hidden']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['nav'], 'aria-label': ['Pagination']}]),
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         'next_page_rgx': [['\/\d+\/', '/%s/']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 32, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Hetero" , action="submenu", url=host, pornstars = True))
    itemlist.append(Item(channel=item.channel, title="Female" , action="submenu", url=host + "female/"))
    itemlist.append(Item(channel=item.channel, title="Shemale" , action="submenu", url=host + "shemale/"))
    itemlist.append(Item(channel=item.channel, title="Gay" , action="submenu", url=host + "gay/"))
    return itemlist

def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "newest/"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "views/month/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "rating/month/"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="list_all", url=item.url + "comments/month/"))
    itemlist.append(Item(channel=item.channel, title="Mas metraje" , action="list_all", url=item.url + "longest/month/"))
    if item.pornstars: 
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=host + "pornstars/", extra="PornStar"))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/", extra="Categorias"))
        itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    
    return AlfaChannel.section(item, finds=findS, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        
        elem_json = {}
        
        try:
            
            elem_json['url'] = elem.get("href", '')
            elem_json['title'] = elem.find('div', class_='font-semibold').get_text(strip=True)
            elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                   or elem.img.get('data-src', '') \
                                                                   or elem.img.get('src', '')
                                                                   
            if elem.find(string=re.compile(r"(?i)videos|movies")):
                data = elem.find(string=re.compile(r"(?i)videos|movies")).strip()
                elem_json['cantidad'] = scrapertools.find_single_match(data, "(\d+) Videos")
        
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
    
    for elem in matches_int:
        elem_json = {}
        
        if 'livecam' in elem.get("class", []): continue
        
        try:
            elem_json['url'] = elem.get("href", '')
            img = elem.find('img', class_='imgvideo')
            elem_json['title'] = img.get('alt', '')
            elem_json['thumbnail'] = img.get('data-original', '') \
                                       or img.get('data-src', '') \
                                       or img.get('src', '')
            data = elem.find('span', class_='text-f13')
            elem_json['stime'] = data.get_text(strip=True) if data else ''
            elem_json['quality'] = data.img.get('alt', '') if data.img else ''
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
    if soup.find('a', id='star1'):
        pornstars = soup.find_all('a', id=re.compile(r"^star\d+"))
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True).replace(",", "")
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        if "HD" in item.contentTitle:
            lista.insert (2, pornstar)
        else:
            lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/?query=%s" % (item.url, texto.replace(" ", "+"))
    
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
