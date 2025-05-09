# -*- coding: utf-8 -*-
# -*- Channel AbsoluPorn -*-
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
             'channel': 'absoluporn', 
             'host': config.get_setting("current_host", 'absoluporn', default=''), 
             'host_alt': ["http://www.absoluporn.com/"], 
             'host_black_list': [], 
             'set_tls': False, 'set_tls_min': False, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False,
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


finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['bloc-thumb']}]),
                       ('find_all', [{'tag': ['div'], 'class': ['thumb-main']}])]),

         'categories': dict([('find', [{'tag': ['div'], 'class': ['bloc-menu-gauche']}]),
                       ('find_all', [{'tag': ['li']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         # 'next_page': dict([('find', [{'tag': ['div'], 'class': ['pagination-page']}, {'tag': ['span']}]),
                            # ('find_next_sibling', [{'tag': ['a'], '@ARG': 'href'}])]), 
         'next_page': {},
         'next_page_rgx': [['-\d+.html', '-%s.html']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {'section_cantidad': dict([('find', [{'tag': ['span']}]),
                                                      ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])}, 
         'controls': {'url_base64': False, 'cnt_tot': 30, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    plot = '[COLOR yellow]Video no corresponde al seleccionado, es aleatorio.[/COLOR]'
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "en/wall-date-1.html", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Mas Visto" , action="list_all", url=host + "en/wall-main-1.html", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Mas Valorada" , action="list_all", url=host + "en/wall-note-1.html", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Mas Largo" , action="list_all", url=host + "en/wall-time-1.html", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "en", extra="Categorias", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url= host, contentPlot=plot))
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, **kwargs)


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
            elem_json['url'] = elem.a.get("href", '')
            elem_json['title'] = elem.a.get('title', '')
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                       or elem.img.get('data-src', '') \
                                       or elem.img.get('src', '')
            elem_json['stime'] = elem.find('div', class_='time').get_text(strip=True) if elem.find('div', class_='time') else ''
            elem_json['quality'] = elem.find('div', class_=re.compile(r"hd")).get_text(strip=True) if elem.find('div', class_=re.compile(r"hd")) else  ''
            plot = '[COLOR yellow]Video no corresponde al seleccionado, es aleatorio.[/COLOR]'
            elem_json['plot']=plot
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
       
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
    
    soup = AHkwargs.get('soup', {})
    if AlfaChannel.last_page in [9999, 99999] and soup and soup.find('div', class_='pagination-nbpage'): 
        total = soup.find('div', class_='pagination-nbpage').find('span', class_='text1').get_text(strip=True)
        total = scrapertools.unescape(total).split(' ')[-2]
        AlfaChannel.last_page = int(int(total) / finds['controls'].get('cnt_tot', 30))
        logger.error(AlfaChannel.last_page)
   
    return matches


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%sen/search-%s-1.html" % (item.url, texto.replace(" ", "-"))
    
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
