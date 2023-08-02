# -*- coding: utf-8 -*-
# -*- Channel PornHub -*-
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
             'channel': 'pornhub', 
             'host': config.get_setting("current_host", 'pornhub', default=''), 
             'host_alt': ["https://es.pornhub.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
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


finds = {'find': dict([ ('find', [{'tag': ['ul'], 'class': ['nf-videos', 'search-video-thumbs', 'row-5-thumbs']}]), 
                         ('find_all', [{'tag': ['li'], 'data-video-id': re.compile(r"^\d+")}]) ]),
         'categories': {'find_all': [{'tag': ['li'], 'class': ['pornstarLi', 'modelLi', 'wrap', 'catPic']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div'], 'class': ['paginationGated']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': {}, 
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''], ['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 30, 'reverse': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = []
    plot = ''
    
    itemlist.append(Item(channel=item.channel, action="list_all", title="Novedades", url="%svideo?o=cm" % host, 
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot))
    itemlist.append(Item(channel=item.channel, action="list_all", title="Recientes", url="%svideo" % host, 
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot))
    itemlist.append(Item(channel=item.channel, action="list_all", title="Mas visto", url="%svideo?o=mv" % host, 
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot))
    itemlist.append(Item(channel=item.channel, action="list_all", title="Mejor valorado", url="%svideo?o=tr" % host,
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot))
    itemlist.append(Item(channel=item.channel, action="list_all", title="Recomendado", url="%srecommended" % host,
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot))
    itemlist.append(Item(channel=item.channel, action="list_all", title="Caliente", url="%svideo?o=ht" % host,
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot))
    itemlist.append(Item(channel=item.channel, action="list_all", title="Mas largo", url="%svideo?o=lg" % host,
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot))
    itemlist.append(Item(channel=item.channel, action="list_all", title="Castellano", url="%slanguage/spanish" % host,
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot))
    itemlist.append(Item(channel=item.channel, action="section", title="Canal", url="%schannels?o=tr" % host,
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot, extra="Canal"))
    itemlist.append(Item(channel=item.channel, action="section", title="PornStar", url="%spornstars?o=t" % host,
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot, extra="PornStar"))
    itemlist.append(Item(channel=item.channel, action="section", title="Categorias", url="%scategories" % host,
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot, extra="Categorias"))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar", url=host, 
                         fanart=item.fanart, thumbnail=item.thumbnail, contentPlot=plot))

    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, matches_post=section_matches, **kwargs)
    # return AlfaChannel.section(item, **kwargs)   Coge todo pero falta url+ de pornstar
    



def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.img.get('alt', '')
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['cantidad'] = elem.find('span', class_=['videosNumber', 'videoCount']).get_text(strip=True) if elem.find('span', class_=['videosNumber', 'videoCount']) else ''
            if not elem_json['cantidad'] and elem.find(string=re.compile(r"(?i)videos|movies")):
                elem_json['cantidad'] = elem.find(string=re.compile(r"(?i)videos|movies"))
                if not "\d+" in elem_json['cantidad']:
                    elem_json['cantidad'] = elem_json['cantidad'].parent.text.strip()
            if item.extra == 'PornStar':
               elem_json['url'] += "/videos"
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        
        matches.append(elem_json.copy())
       

    return matches


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    if item.extra == 'PornStar':
        findS['find'] = dict([ ('find', [{'tag': ['ul'], 'id': ['mostRecentVideosSection']}]), 
                                        ('find_all', [{'tag': ['li'], 'data-video-id': re.compile(r"^\d+")}]) ])
    
    return AlfaChannel.list_all(item, finds=findS, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:    
            if elem.find('div', class_='thumbTextPlaceholder'): continue   
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.a.get('title', '')
            elem_json['thumbnail'] = elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find('var', class_='duration').get_text(strip=True) if elem.find('var', class_='duration') else ''
            if elem.find('span', class_='views'):
                elem_json['views'] = elem.find('span', class_='views').get_text(strip=True)

            
            data = elem.find('div', class_='videoUploaderBlock')
            if data and 'channels' in data.a['href']:
                elem_json['canal'] = data.a.get_text(strip=True)
                elem_json['extra'] = 'casa'
            elif data:
                elem_json['star'] = data.a.get_text(strip=True)

        
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
    if soup.find_all('a', class_="pstar-list-btn"): 
        pornstars = soup.find_all('a', class_="pstar-list-btn")
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
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    item.url = "%svideo/search?search=%s&o=mr" % (host, texto.replace(" ", "+"))

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


