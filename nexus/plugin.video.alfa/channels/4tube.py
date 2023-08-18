# -*- coding: utf-8 -*-
# -*- Channel PornVase -*-
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

#  https://www.porntube.com    https://www.pornerbros.com   https://www.4tube.com  https://www.fux.com
canonical = {
             'channel': '4tube', 
             'host': config.get_setting("current_host", '4tube', default=''), 
             'host_alt': ["https://www.4tube.com/"], 
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


finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['grid-col2', 'grid-col4']}]),
                       ('find_all', [{'tag': ['div'], 'class': ['thumb_video']}])]),
         'categories': {'find_all': [{'tag': ['a'], 'class': ['thumb-link']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]),
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         'next_page_rgx': [['?p=d+', '?p=%s']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 28, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "videos?sort=date&p=1"))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="list_all", url=host + "videos?time=month&p=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Visto" , action="list_all", url=host + "videos?sort=views&time=month&p=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Valorada" , action="list_all", url=host + "videos?sort=rating&time=month&p=1"))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="list_all", url=host + "videos?sort=duration&time=month&p=1"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "pornstars?p=1", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channels?p=1", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "tags", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url= host))
    
    itemlist.append(Item(channel=item.channel, title = ""))
    itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", orientation="shemale/"))
    itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", orientation="gay/"))
    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    url = host + item.orientation
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=url + "videos?sort=date&p=1"))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="list_all", url=url + "videos?time=month&p=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Visto" , action="list_all", url=url + "videos?sort=views&time=month&p=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Valorada" , action="list_all", url=url + "videos?sort=rating&time=month&p=1"))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="list_all", url=url + "videos?sort=duration&time=month&p=1"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=url + "pornstars?p=1", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=url + "channels?p=1", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=url + "tags", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=url))
    
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            elem_json['url'] = elem.get("href", '')
            elem_json['title'] = elem.get('title', '')
            elem_json['thumbnail'] =elem.img.get('data-original', '')
            if elem.find('div', class_=['thumb-info']).li:
                elem_json['cantidad'] = elem.find('div', class_=['thumb-info']).li.get_text(strip=True)
        
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
        
        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '')
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find('li', class_='duration-top').get_text(strip=True)
            if elem.find('li', class_='topHD'): elem_json['quality'] = elem.find('li', class_='topHD').get_text(strip=True)
            
            pornstars = elem.find_all('li', class_="master-pornstar")
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


def play(item):
    logger.info()
    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    if soup.find('ul', class_='pornlist'):
        pornstars = soup.find('ul', class_='pornlist').find_all('h3')
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        color = AlfaChannel.color_setting.get('rating_3', '')
        txt = scrapertools.find_single_match(item.contentTitle, "%s\]([^\[]+)"  % color)
        if not txt.lower() in pornstar.lower():
            pornstar = "%s & %s" %(txt,pornstar)
        item.contentTitle = re.sub(r"%s][^\[]+"  % color, "%s]{0}".format(pornstar) % color, item.contentTitle)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch?sort=date&q=%s" % (item.url, texto.replace(" ", "-"))
    
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
