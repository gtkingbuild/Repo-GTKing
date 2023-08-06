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

canonical = {
             'channel': 'analdin', 
             'host': config.get_setting("current_host", 'analdin', default=''), 
             'host_alt': ["https://www.analdin.com/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s* id="item1"?'], 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['item']}]},
         'categories': {'find_all': [{'tag': ['div', 'a'], 'class': ['item']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['&from_videos=\d+', '&from_videos=%s'], ['&from=\d+', '&from=%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], 'string': re.compile('(?i)(?:ltima|last)'), '@POS': [-1], 
                                           '@ARG': 'data-parameters', '@TEXT': 'from\w*:\s*(\d+)'}])]), 
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
    
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "más-reciente/?sort_by=post_date&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=host + "más-visto/?sort_by=video_viewed_month&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="list_all", url=host + "mejor-valorado/?sort_by=rating_month&from=1"))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="section", url=host + "models/?sort_by=total_videos&from=1", extra="Pornstar"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host, extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categorías/?sort_by=title&from=1", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
    if item.extra == 'Pornstar':
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': 'list-models'}]), 
                                    ('find_all', [{'tag': ['a'], 'class': 'item'}])])
    
    if item.extra == 'Canal':
        findS['categories'] = dict([('find', [{'tag': ['div'], 'id': 'popup-sponsors'}]), 
                                    ('find_all', [{'tag': ['li']}])])
        findS['last_page'] = {}
    
    if item.extra == 'Categorias':
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': 'list-categories'}]), 
                                    ('find_all', [{'tag': ['a']}])])
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    return AlfaChannel.list_all(item, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def play(item):
    logger.info()
    
    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    pornstars = soup.find_all('a', href=re.compile("/model(?:o|)s/[A-z0-9-]+/"))
    
    for x, value in enumerate(pornstars):
        pornstars[x] = value.get_text(strip=True)
    
    pornstar = ' & '.join(pornstars)
    pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
    
    lista = item.contentTitle.split()
    if "HD" in item.title:
        lista.insert (4, pornstar)
    else:
        lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%sbuscar/?q=%s&sort_by=video_viewed&from_videos=1" % (host, texto.replace(" ", "+"))
    
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
