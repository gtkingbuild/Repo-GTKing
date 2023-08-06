# -*- coding: utf-8 -*-
# -*- Channel Legalmente Gratis -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from modules import autoplay
from channels import filtertools

IDIOMAS = {'español':'CAST', 'VOSE': 'VOSE'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['youtube']

canonical = {
             'channel': 'legalmentegratis', 
             'host': config.get_setting("current_host", 'legalmentegratis', default=''), 
             'host_alt': ["http://legalmentegratis.com/"], 
             'host_black_list': [], 
             'pattern': '<h1\s*class="site-title">\s*<a\s*href="([^"]+)"', 
             'set_tls': False, 'set_tls_min': True, 'retries_cloudflare': 0, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host,
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section", section='genre',
                         thumbnail=get_thumb('genres', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def get_source(url, referer=None, timeout=5):
    logger.info()
    
    if referer is None:
        data = httptools.downloadpage(url, timeout=timeout, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, timeout=timeout, headers={'Referer':referer}, canonical=canonical).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    
    return data


def list_all(item):
    logger.info()
    
    itemlist = []

    data = get_source(item.url)
    patron = '<article id="post-\d+".*?href="([^"]+)".*?src="([^"]+)".*?<p>(.*?) (\(?\d{4}\)?)([^<]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, _year, scrapedplot in matches:

        url = scrapedurl
        contentTitle = scrapedtitle
        year = re.sub(r'\(|\)','', _year) or '-'
        title = '%s [%s]' % (contentTitle, year)
        thumbnail = 'http:' + scrapedthumbnail
        
        itemlist.append(Item(channel=item.channel, action='findvideos',
                             title=title,
                             url=url,
                             thumbnail=thumbnail,
                             contentTitle=contentTitle,
                             contentType='movie', 
                             infoLabels={'year': year}
                             ))
    
    tmdb.set_infoLabels_itemlist(itemlist, True)

    itemlist = sorted(itemlist, key=lambda it: it.contentTitle)
    
    #  Paginación
    url_next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)">')
    if url_next_page:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all',
                             section=item.section))
    return itemlist


def section(item):
    logger.info()
    
    itemlist = []

    data = get_source(host+'generos/')
    action = 'list_all'

    if item.section == 'genre':
        data = scrapertools.find_single_match(data, '<h1\s*class="entry-title"\s*>Géneros</h1>(.*?)<\/article>')

    patron = 'href="([^"]+)".*?>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title in matches:
        new_item = Item(channel=item.channel, title=title, url=url, action=action, section=item.section)
        
        itemlist.append(new_item)

    return itemlist


def findvideos(item):
    logger.info()
    
    itemlist = []
    
    data = get_source(item.url)
    
    lang_data = scrapertools.find_single_match(data, '<p><strong(.*?)</strong></p>')
    if 'español' in lang_data:
        language = 'español'
    else:
        language = 'VOSE'
    
    url = scrapertools.find_single_match (data, '<iframe.*?src="([^"]+)"')
    if 'gloria.tv' in url:
        new_data = get_source(url)
        url = 'https://gloria.tv'+ scrapertools.find_single_match(new_data, '<source type=".*?" src="([^"]+)">')

    itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url,
                         language=IDIOMAS[language], infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % '%s' % i.server.capitalize())

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    
    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))
    return itemlist
