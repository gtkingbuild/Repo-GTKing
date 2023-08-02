# -*- coding: utf-8 -*-
# -*- Channel PornVase -*-
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
             'channel': 'eroticmv', 
             'host': config.get_setting("current_host", 'eroticmv', default=''), 
             'host_alt': ["https://eroticmv.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['article'], 'id': re.compile(r"^post-\d+")}]},
         'categories': {},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+\/', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['wp-pagenavi']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': '/page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {},
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "category/decades/?archive_query=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=host + "category/decades/?archive_query=view"))
    itemlist.append(Item(channel=item.channel, title="Mejor Valoradas" , action="list_all", url=host + "category/decades/?archive_query=like"))
    itemlist.append(Item(channel=item.channel, title="Mas Comentadas" , action="list_all", url=host + "category/decades/?archive_query=comment"))
    itemlist.append(Item(channel=item.channel, title="Orden Alfabetico" , action="list_all", url=host + "category/decades/?archive_query=title"))
    itemlist.append(Item(channel=item.channel, title="Pais" , action="section", url=host, extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Decada" , action="section", url=host, extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host, extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.extra == 'Canal':
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': ['nav-menu-control']}]), 
                                    ('find_all', [{'tag': ['a'], 'href': re.compile(r"/country/")}])])
    if item.extra == 'Categorias':
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': ['nav-menu-control']}]), 
                                    ('find_all', [{'tag': ['a'], 'href': re.compile(r"/genre/")}])])
    if item.extra == 'PornStar':
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': ['nav-menu-control']}]), 
                                    ('find_all', [{'tag': ['a'], 'href': re.compile(r"/decades/[0-9]+")}])])
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.extra == 'Canal':
        findS['next_page'] = dict([('find', [{'tag': ['div'], 'class': ['wp-pagenavi']}]), 
                                   ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])])
        findS['last_page'] = {}
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    # url = "https://eroticmv.com/wp-admin/admin-ajax.php?action=ajaxsearchpro_search&aspp=&asid=1&asp_inst_id=1_3&options=customset[]=post&asp_gen[]=title&filters_initial=1&filters_changed=0&qtranslate_lang=0&current_page_id=18375"
    
    item.url = "%ssearch/%s/" % (host, texto.replace(" ", "%20"))
    
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
