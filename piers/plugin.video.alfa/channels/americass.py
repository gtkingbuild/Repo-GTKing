# -*- coding: utf-8 -*-
# -*- Channel AmericAss -*-
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
             'channel': 'americass', 
             'host': config.get_setting("current_host", 'americass', default=''), 
             'host_alt': ["https://americass.net/"], 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['video-preview']}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['col-lg-3', 'col-lg-2', 'col-tag']}]}, 
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
    itemlist.append(Item(channel=item.channel, title="Categorias", action="section", url=host + "tag/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

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
            
            elem_json['url'] = elem.a.get("href", '')
            if elem.img: elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                                     or elem.img.get('data-src', '') \
                                                                                     or elem.img.get('src', '')
            if elem.find(class_=['text-muted', 'd-block']):
                elem_json['cantidad'] = elem.find(class_=['text-muted', 'd-block']).get_text(strip=True)
            if elem.find('p'):
                elem_json['title'] = elem.p.get_text(strip=True) 
            if "/tag/" in elem_json['url']:
                elem_json['title'] =  elem.a.get_text(strip=True)
                elem_json['title'] = elem_json['title'].replace(elem_json['cantidad'], "")
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
            elem_json['url'] = elem.a.get("href", '')
            elem_json['title'] = elem.h3.get_text(strip=True)
            if elem.img: elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                                     or elem.img.get('data-src', '') \
                                                                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find(class_='video-duration-overlay').get_text(strip=True) if elem.find(class_='video-duration-overlay') else ''
            img = ""
            img = elem.find('img', class_='img-fluid')
            if img:
                if '/studio/' in img['src']:
                    elem_json['canal'] = img['alt']
                    elem_json['extra'] = 'casa'
                else:
                    elem_json['star'] = img['alt']
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        if not elem.a.get('href', ''): continue 
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
    if soup.find_all('a', href = re.compile("/actor/[A-z0-9-]+")):
        pornstars = soup.find_all('a', href = re.compile("/actor/[A-z0-9-]+"))
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        
        pornstar = ' & '.join(pornstars)
        if item.extra:
            lista = item.contentTitle.split('[/COLOR]')
            pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
            pornstar = pornstar.replace('[/COLOR]', '')
            pornstar = ' %s' %pornstar
            lista.insert (2, pornstar)
            item.contentTitle = '[/COLOR]'.join(lista)
        else:
            color = AlfaChannel.color_setting.get('rating_3', '')
            txt = scrapertools.find_single_match(item.contentTitle, "%s\]([^\[]+)"  % color)
            if not txt.lower() in pornstar.lower():
                pornstar = "%s & %s" %(txt,pornstar)
            item.contentTitle = re.sub(r"%s][^\[]+"  % color, "%s]{0}".format(pornstar) % color, item.contentTitle)
    
    url = "%s/resolve"  %item.url
    kwargs['soup'] = False
    kwargs['json'] = True
    data = AlfaChannel.create_soup(url, **kwargs)['template']
    url = scrapertools.find_single_match(data, '<source src="([^"]+)"')
    itemlist.append(Item(channel=item.channel, action="play", server= "directo", contentTitle = item.contentTitle, url=url))
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%svideo/search/%s?page=1" % (host, texto.replace(" ", "+"))
    
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
