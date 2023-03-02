# -*- coding: utf-8 -*-
# -*- Channel Series Antiguas -*-
# -*- Created for Alfa Addon -*-
# -*- By the Alfa Development Group -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from core.item import Item
from core import servertools
from core import scrapertools
from channelselector import get_thumb
from platformcode import config, logger
from channels import autoplay
from lib.AlfaChannelHelper import DictionaryChannel

IDIOMAS = {"Latino": "LAT"}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = []

canonical = {
             'channel': 'seriesantiguas', 
             'host': config.get_setting("current_host", 'seriesantiguas', default=''), 
             'host_alt': ["https://seriesantiguas.com/"], 
             'host_black_list': ["https://www.seriesantiguas.com/"], 
             'pattern': ['<a\s*href="([^"]+)"[^>]*>\s*(?:Principal|M.s\s*vistas)\s*<\/a>'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

finds = {'find': {'find': [{'tag': ['div'], 'class': ['progression-masonry-margins']}], 
                  'find_all': [{'tag': ['div'], 'class': ['progression-masonry-item']}]}, 
         'next_page': {'find': [{'tag': ['div'], 'class': ['nav-previous']}, {'tag': ['a'], '@ARG': 'href'}]}, 
         'year': [], 
         'season_episode': [], 
         'season': {'find': [{'tag': ['ul'], 'class': ['video-tabs-nav-aztec nav']}], 'find_all': [['li']]}, 
         'episode_url': '', 
         'episodes': {'find': [{'tag': ['div'], 'id': ['aztec-tab-%s']}], 
                      'find_all': [{'tag': ['div'], 'class': ['progression-studios-season-item']}]}, 
         'episode_num': ['(?i)(\d+)\.\s*[^$]+$', '(?i)[a-z_0-9 ]+\s*\((?:temp|epis)\w*\s*(?:\d+\s*x\s*)?(\d+)\)'], 
         'episode_clean': ['(?i)\d+\.\s*([^$]+)$', '(?i)([a-z_0-9 ]+)\s*\((?:temp|epis)\w*\s*(?:\d+\s*x\s*)?\d+\)'], 
         'findvideos': {'find_all': [{'tag': ['div'], 'class': ['embed-code-remove-styles-aztec']}]}, 
         'title_clean': []}
AlfaChannel = DictionaryChannel(host, movie_path="/pelicula", tv_path='/ver', canonical=canonical, finds=finds)


def mainlist(item):
    logger.info()
    
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(
        Item(
            channel = item.channel,
            title = "Series de los 80s",
            action = "list_all",
            url = host + 'media-category/80s/', 
            fanart = item.fanart,
            c_type='series', 
            thumbnail = get_thumb("year", auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            title = "Series de los 90s",
            action = "list_all",
            url = host + 'media-category/90s/', 
            fanart = item.fanart,
            c_type='series', 
            thumbnail = get_thumb("year", auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            title = "Series del 2000",
            action = "list_all",
            url = host + 'media-category/00s/', 
            fanart = item.fanart,
            c_type='series', 
            thumbnail = get_thumb("year", auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            title = "Todas las series",
            action = "list_all",
            url = host + 'series/', 
            fanart = item.fanart,
            c_type='series', 
            thumbnail = get_thumb("all", auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            title = "Buscar...",
            action = "search",
            url = host + '?post_type=video_skrn&search_keyword=',
            fanart = item.fanart,
            c_type='series', 
            thumbnail = get_thumb("search", auto=True)
        )
    )

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item, finds=finds)


def seasons(item, get_episodes = False):
    logger.info()
    global finds

    itemlist = []
    item.url = item.url.rstrip('/') + '/'

    soup = AlfaChannel.create_soup(item.url)

    url =  soup.find('a', class_='video-play-button-single-aztec', string=re.compile("antigua"))
    url = url['href'] if url else ''
    if url: 
        item.url = url.rstrip('/') + '/'
        soup = {}
        finds['season'] = {'find': [{'tag': ['li'], 'class': ['megalist']}], 'find_all': [['li']]}

    return AlfaChannel.seasons(item, data=soup, finds=finds)


def episodios(item):
    logger.info()

    itemlist = []
    
    templist = seasons(item)
    
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()
    global finds

    if '/search' in item.url:
        finds['episodes'] = {'find': [{'tag': ['div'], 'class': ['blog-posts hfeed clearfix']}], 
                             'find_all': [{'tag': ['div'], 'class': ['post hentry']}]}
    else:
        finds['episodes']['find'][0]['id'][0] = finds['episodes']['find'][0]['id'][0] % str(item.contentSeason)

    return AlfaChannel.episodes(item, json=False, finds=finds)


def findvideos(item):
    logger.info()
    global finds

    item.url = item.url.rstrip('/') + '/' if not item.url.endswith('.html') else item.url
    if not '/episodio' in item.url:
        finds['findvideos'] = {'find_all': [{'tag': ['div'], 'class': ['post-body entry-content']}]}

    return AlfaChannel.get_video_options(item.url, langs=list_language, findvideos=item, finds=finds)


def search(item, texto):
    logger.info()

    itemlist = []

    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto
        
        if texto != '':
            return list_all(item)
        else:
            return []
    
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
