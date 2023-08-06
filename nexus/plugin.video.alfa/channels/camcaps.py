# -*- coding: utf-8 -*-
# -*- Channel Camcaps -*-
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

# https://camcaps.to https://www.nsfwcrave.com/  https://reallifecam.to 
 # https://voyeur-house.to  https://www.voyeur-house.life/   https://www.voyeur-house.fun/
#   https://www.3dsexanime.xyz/   https://www.chaturbate-video.xyz/
#  
# https://fanstube.net/  https://leakedbay.com/   clones de camcaps con <article 'thumb'

#      https://www.sexvr.com/  https://celebsnudeworld.com/      https://www.hentaikif.com/

canonical = {
             'channel': 'camcaps', 
             'host': config.get_setting("current_host", 'camcaps', default=''), 
             'host_alt': ["https://camcaps.to/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 10
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []


finds = {'find': {'find_all': [{'tag': ['div'],  'class': ['col-sm-6']}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['col-md-3', 'col-md-4']}]}, 
         # 'find':  dict([('find', [{'tag': ['div'], 'class': ['v-cards']}]),
                        # ('find_all', [{'tag': ['a'], 'href': re.compile("/video/[0-9]+/")}])]),
         # 'categories': dict([('find', [{'tag': ['div'], 'class': ['v-cards']}]),
                             # ('find_all', [{'tag': ['div'], 'class': ['item']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['&page=\d+', '&page=%s']], 
         # 'last_page': dict([('find', [{'tag': ['div'], 'class': ['load-more']}]), 
                            # ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           # '@ARG': 'data-max-queries', '@TEXT': '(\d+)'}])]), 
         'last_page': dict([('find', [{'tag': ['div', 'nav', 'ul'], 'class': ['n-pagination', 'pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'href', '@TEXT': 'page=(\d+)'}])]), 
         # 'last_page': {}, 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_stime': {'find': [{'tag': ['span'], 'class': ['is-hd'], '@TEXT': '(\d+:\d+)' }]},
                            # 'list_all_url': {'find': [{'tag': ['a'], 'class': ['link'], '@ARG': 'href'}]},
                            # 'list_all_title': dict([('find', [{'tag': ['h3']}]),
                                                    # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_stime': dict([('find', [{'tag': ['div', 'span'], 'class': ['thumb-duration', 'time']}]),
                                                    # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_quality': {'find': [{'tag': ['span', 'div'], 'class': ['hd'], '@ARG': 'class',  '@TEXT': '(hd)' }]},
                            # 'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['is-hd']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_premium': dict([('find', [{'tag': ['span'], 'class': ['ico-private']}]),
                                                       # ('get_text', [{'tag': '', 'strip': True}])]),
                            'section_cantidad': dict([('find', [{'tag': ['div'], 'class':['float-right', 'pull-right']}]),
                                                      ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
                            },
         'controls': {'url_base64': False, 'cnt_tot': 20, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="3dsexanime" , action="submenu", url= "https://www.3dsexanime.xyz/", chanel="3dsexanime", thumbnail= "https://www.3dsexanime.xyz/images/logo/logo.png"))
    itemlist.append(Item(channel=item.channel, title="CamCaps" , action="submenu", url= "https://camcaps.to/", chanel="camcaps", thumbnail= "https://camcaps.to/images/logo/logo.png", cat="yes"))
    # itemlist.append(Item(channel=item.channel, title="FansTube" , action="submenu", url= "https://fanstube.net/", chanel="fanstube", thumbnail = "https://i.postimg.cc/gJH23yWB/fanstube.png"))
    # itemlist.append(Item(channel=item.channel, title="LeakedBay" , action="submenu", url= "https://leakedbay.com/", chanel="leakedbay", thumbnail = "https://i.postimg.cc/qvwwDSGk/leakedbay.png"))
    itemlist.append(Item(channel=item.channel, title="NSFWcrave" , action="submenu", url= "https://www.nsfwcrave.com/", chanel="nsfwcrave", thumbnail = "https://www.nsfwcrave.com/images/logo/logo.png", cat="yes"))
    itemlist.append(Item(channel=item.channel, title="RealLifeCam" , action="submenu", url= "https://reallifecam.to/", chanel="reallifecam", thumbnail = "https://reallifecam.to/images/logo/logo.png", cat="yes"))
    itemlist.append(Item(channel=item.channel, title="VoyeurHouse" , action="submenu", url= "https://voyeur-house.to/", chanel="voyeur-house", thumbnail = "https://voyeur-house.to/images/logo/logo.png"))
    itemlist.append(Item(channel=item.channel, title="VoyeurFunHouse" , action="submenu", url= "https://www.voyeur-house.fun/", chanel="voyeur-house", thumbnail = "https://www.voyeur-house.fun/images/logo/logo.png"))
    itemlist.append(Item(channel=item.channel, title="VoyeurLifeHouse" , action="submenu", url= "https://www.voyeur-house.life/", chanel="voyeur-house", thumbnail = "https://www.voyeur-house.life/images/logo/logo.png"))
    itemlist.append(Item(channel=item.channel, title="ChaturbateVideo" , action="submenu", url= "https://www.chaturbate-video.xyz/", chanel="chaturbate-video", thumbnail = "https://www.chaturbate-video.xyz/images/logo/logo.png", cat="yes"))

    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    itemlist.append(Item(channel=item.channel, title="Nuevo" , action="list_all", url=item.url + "videos?o=mr&page=1", thumbnail = item.thumbnail, chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Visto" , action="list_all", url=item.url + "videos?o=mv&t=m&page=1", thumbnail = item.thumbnail, chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorado" , action="list_all", url=item.url + "videos?o=tr&t=m&page=1", thumbnail = item.thumbnail, chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Favorito" , action="list_all", url=item.url + "videos?o=tf&t=m&page=1", thumbnail = item.thumbnail, chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Comentado" , action="list_all", url=item.url + "videos?o=md&t=m&page=1", thumbnail = item.thumbnail, chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "videos?o=lg&t=m&page=1", thumbnail = item.thumbnail, chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Trending" , action="list_all", url=item.url + "videos?o=bw&page=1", thumbnail = item.thumbnail, chanel=item.chanel))
    if item.cat:
        itemlist.append(Item(channel=item.channel, title="Canal" , action="mycanal", url=item.url , extra="Canal", thumbnail = item.thumbnail, chanel=item.chanel))
    # itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=item.url + "pornstar", extra="PornStar", thumbnail = item.thumbnail, chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories", extra="Categorias", thumbnail = item.thumbnail, chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, thumbnail = item.thumbnail, chanel=item.chanel))
    return itemlist

def mycanal(item):
    logger.info()
    
    AlfaChannel.host = config.get_setting("current_host", item.chanel, default=host)
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})

    itemlist = []
    if "camcaps" in item.url or "chaturbate-video" in item.url or "nsfwcrave" in item.url:
        itemlist.append(Item(channel=item.channel, title="Onlyfans" , action="list_all", url=item.url + "search/videos/onlyfans?o=mr&page=1", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Snapchat" , action="list_all", url=item.url + "search/videos/snapchat?o=mr&page=1", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Manyvids" , action="list_all", url=item.url + "search/videos/manyvids?o=mr&page=1", chanel=item.chanel))
        if "camcaps" in item.url:
            itemlist.append(Item(channel=item.channel, title="Fansly" , action="list_all", url=item.url + "search/videos/fansly?o=mr&page=1", chanel=item.chanel))
            itemlist.append(Item(channel=item.channel, title="Loyalfans" , action="list_all", url=item.url + "search/videos/loyalfans?o=mr&page=1", chanel=item.chanel))
            itemlist.append(Item(channel=item.channel, title="Pornhub" , action="list_all", url=item.url + "search/videos/pornhub?o=mr&page=1", chanel=item.chanel))
            itemlist.append(Item(channel=item.channel, title="Clips4sale" , action="list_all", url=item.url + "search/videos/clips4sale?o=mr&page=1", chanel=item.chanel))
            itemlist.append(Item(channel=item.channel, title="Youtube" , action="list_all", url=item.url + "search/videos/youtube?o=mr&page=1", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="MFC" , action="list_all", url=item.url + "search/videos/mfc?o=mr&page=1", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Chaturbate" , action="list_all", url=item.url + "search/videos/chaturbate?o=mr&page=1", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Sextape" , action="list_all", url=item.url + "search/videos/sextape?o=mr&page=1", chanel=item.chanel))
    else:
        itemlist.append(Item(channel=item.channel, title="Onlyfans" , action="list_all", url=item.url + "search/videos/onlyfans?o=mr&page=1", chanel=item.chanel))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/videos\/[^$]+$)', r'\1?o=mr&page=1']]
    
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
    
    AlfaChannel.host = config.get_setting("current_host", item.chanel, default=host)
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    url = soup.find('div', class_='video-embedded').find(['iframe', 'source']).get('src', '')
    if url:
        itemlist.append(Item(channel = item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
        itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    if "reallifecam" in item.url:
        item.url = "%ssearch/videos?search_query=%s&o=mr&page=1" % (item.url, texto.replace(" ", "+"))
    else:
        item.url = "%ssearch/videos/%s?o=mr&page=1" % (item.url, texto.replace(" ", "-"))
    
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
