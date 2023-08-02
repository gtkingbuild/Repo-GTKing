# -*- coding: utf-8 -*-
# -*- Channel Beeg -*-
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
             'channel': 'beeg', 
             'host': config.get_setting("current_host", 'beeg', default=''), 
             'host_alt': ["https://beeg.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
url_api = "https://store.externulls.com"

timeout = 5
kwargs = {}
kwargs['soup'] = False
kwargs['json'] = True
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': {},
         'categories': {}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [], 
         'last_page': {}, 
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''], ['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'custom_pagination': True}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Útimos videos", action="list_all", url= url_api + "/facts/tag?id=27173&limit=48&offset=0"))
    itemlist.append(Item(channel=item.channel, title="Canal", action="section", url= url_api + "/tag/facts/tags?get_original=true&slug=index", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Catalogo", action="section", url= url_api + "/tag/facts/tags?get_original=true&slug=index", extra="PornStar"))
    # itemlist.append(item.clone(title="Buscar...", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    if not item.orientation:
        item.orientation = "str"
    
    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        
        try:
            elem_json['thumbnail'] = ""
            id = elem["id"]
            if elem.get("thumbs", ""):
                th2 = elem.get("thumbs", "")[0]
                elem_json['thumbnail'] = "https://thumbs.externulls.com/photos/%s/to.webp" %th2.get('id', '')
            if item.extra == 'Canal' and not elem_json['thumbnail']:
                continue
            if item.extra == 'PornStar' and elem_json['thumbnail']:
                continue
            elem_json['url'] = '%s/facts/tag?slug=%s&limit=48&offset=0' % (url_api, elem.get('tg_slug', '') )
            elem_json['title'] = elem.get('tg_name', '')
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
    
    page = int(scrapertools.find_single_match(item.url, '&offset=([0-9]+)')) + len(matches_int)
    AlfaChannel.next_page_url = re.sub(r"&offset=\d+", "&offset=%s" % page, item.url)
    
    for elem in matches_int:
        elem_json = {}
       
        try:
            id = elem['fc_file_id']
            th2= elem["fc_facts"][0]['fc_thumbs']
            stime = elem["file"]["fl_duration"]
            stuff = elem["file"]["stuff"]
            if stuff.get("sf_name", ""):
                title = stuff["sf_name"]
            else:
                title = id
            plot = ""
            if stuff.get("sf_story", ""):
                plot = stuff["sf_story"]
            
            elem_json['url'] = "%s%s" % (host, id)
            elem_json['title'] = title
            elem_json['thumbnail'] = "https://thumbs-015.externulls.com/videos/%s/%s.jpg" %(id, th2[0])
            elem_json['stime'] = stime
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


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%sapi/videos.php?params=259200/%s/latest-updates/60/search..1.all..&s=%s&sort=latest-updates&date=all&type=all&duration=all" % (host,item.orientation, texto.replace(" ", "%20")) 
    
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
