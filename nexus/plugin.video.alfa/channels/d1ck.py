# -*- coding: utf-8 -*-
# -*- Channel D1ck -*-
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

# https://d1ck.co/   https://faphard.co/   https://f1ix.com/ https://pornrz.com/  https://pornn.co/
# https://18yos.co/   https://boombj.com/  https://roleplayers.co/   https://teenanal.co/  https://wanktank.co/

canonical = {
             'channel': 'd1ck', 
             'host': config.get_setting("current_host", 'd1ck', default=''), 
             'host_alt': ["https://d1ck.co/"], 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['preview']}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['preview']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['ul'], 'class': ['pages']}]),
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         # 'next_page': dict([('find', [{'tag': ['ul'], 'class': ['pages']}]),
                            # ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'data-parameters', '@TEXT': ':(\d+)'}])]), 
         'next_page_rgx': [['&from_videos=\d+', '&from_videos=%s'], ['&from=\d+', '&from=%s'], 
                           ['/\d+', '/%s/'], ['&page=\d+', '&page=%s'], ['\?page=\d+', '?page=%s'], ['\/page\/\d+\/', '/page/%s/']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {'list_all_stime': dict([('find', [{'tag': ['div'], 'class': ['dur']}]),
                                                    ('get_text', [{'strip': True}])]),
                            # 'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['hd']}]),
                                                      # ('get_text', [{'strip': True}])]),
                            'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['dur']}]),
                                                      ('get_text', [{'strip': True}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 40, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)



def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="18yos" , action="submenu", url="https://18yos.co/", chanel="18yos", thumbnail="https://i.postimg.cc/13RpPMBr/18yos.png"))
    itemlist.append(Item(channel=item.channel, title="Boombj" , action="submenu", url="https://boombj.com/", chanel="boombj", thumbnail="https://i.postimg.cc/NMxsg8pR/boombj.png"))
    itemlist.append(Item(channel=item.channel, title="D1ck" , action="submenu", url="https://d1ck.co/", chanel="d1ck", thumbnail="https://i.postimg.cc/59DzCVYv/d1ck.png"))
    itemlist.append(Item(channel=item.channel, title="Faphard" , action="submenu", url="https://faphard.co/", chanel="faphard", thumbnail="https://i.postimg.cc/13jTxgSM/Faphard.png"))
    itemlist.append(Item(channel=item.channel, title="F1ix" , action="submenu", url="https://f1ix.com/", chanel="f1ix", thumbnail="https://i.postimg.cc/dtrsWYKh/f1ix.png"))
    itemlist.append(Item(channel=item.channel, title="Pornrz" , action="submenu", url="https://pornrz.com/", chanel="pornrz", thumbnail="https://i.postimg.cc/LX19cG4m/pornrz.png"))
    itemlist.append(Item(channel=item.channel, title="Pornn" , action="submenu", url="https://pornn.com/", chanel="pornn", thumbnail="https://i.postimg.cc/9FRRCKH2/pornn.png"))
    itemlist.append(Item(channel=item.channel, title="RolePlayers" , action="submenu", url="https://roleplayers.co/", chanel="roleplayers", thumbnail="https://i.postimg.cc/t4GM50XC/roleplayers.png"))
    itemlist.append(Item(channel=item.channel, title="TeenAnal" , action="submenu", url="https://teenanal.co/", chanel="teenanal", thumbnail="https://i.postimg.cc/pLZM5VDt/teenanal.png"))
    itemlist.append(Item(channel=item.channel, title="WankTank" , action="submenu", url="https://wanktank.co/", chanel="wanktank", thumbnail="https://i.postimg.cc/GtQxJfz9/wanktank.png"))

    AlfaChannel.host = item.url
    AlfaChannel.canonical = canonical.update({'channel': item.chanel, 'host': config.get_setting("current_host", item.chanel, default=''), 'host_alt': AlfaChannel.host})    
    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    config.set_setting("current_host", item.url, item.chanel)
    # itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "latest-updates/?sort_by=post_date&from=01"))
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=item.url + "latest-updates/1/"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=item.url + "most-popular/1/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="list_all", url=item.url + "top-rated/1/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url))
    
    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    if item.extra == "Categorias":
        findS['url_replace'] = [[host, '%scategories/' % host], ['($)', '1/']]

    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.c_type == "search" or item.extra == "Categorias":
        findS['next_page'] = {}
        item.last_page = 9999
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def play(item):
    logger.info()
    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    url = soup.find('div', class_='player-holder').iframe['src']
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/?q=%s&sort_by=post_date&from_videos=01" % (item.url, texto.replace(" ", "+"))
    # item.url = "%ssearch/?q=%s" % (host, texto.replace(" ", "+"))
    
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
