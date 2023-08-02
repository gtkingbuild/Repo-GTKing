# -*- coding: utf-8 -*-
# -*- Channel JoysPorn -*-
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

# https://tubxporn.xxx  https://pornky.com  https://pornktube.tv  https://joysporn.com

canonical = {
             'channel': 'joysporn', 
             'host': config.get_setting("current_host", 'joysporn', default=''), 
             'host_alt': ["https://wwv.joysporn.sex/"], 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['video_c']}]},
         'categories':  dict([('find', [{'tag': ['div'], 'class': ['porncategories']}]), 
                              ('find_all', [{'tag': ['a']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['/page/\d+', '/page/%s/'],['&search_start=\d+', '&search_start=%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['navigation']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['article']}]), 
                             ('find_all', [{'tagOR': ['a'], 'href': True, 'rel': 'noreferrer'},
                                           {'tag': ['iframe'], 'src': True}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_title':  dict([('find', [{'tag': ['h2']}]),
                                                     ('get_text', [{'tag': '', 'strip': True}])]),
                            'section_title': dict([('find', [{'tag': ['h2']}]),
                                                   ('get_text', [{'tag': '', 'strip': True}])]),
                            },
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "latest/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=host + "apapu/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="list_all", url=host + "viewsing/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "list.html", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:cat)\/[^$]+$)', r'\1/page/1/']]
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    findS = finds.copy()
    if item.c_type == "search":
        findS['last_page']= dict([('find', [{'tag': ['div'], 'class': ['navigation']}]), 
                                  ('find_all', [{'tag': ['a'], '@POS': [-1]}]),
                                  ('get_text', [{'tag': '', 'strip': True}])
                                  ]) 
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%sindex.php?do=search&subaction=search&story=%s&search_start=1" % (host, texto.replace(" ", "+"))
    
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
