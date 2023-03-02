# -*- coding: utf-8 -*-
# -*- Channel Ennovelas -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int

import re

from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import tmdb
from channels import autoplay
from platformcode import config, logger
from channelselector import get_thumb

IDIOMAS = {'la': 'LAT', 'sub': 'VOSE'}
list_idiomas = list(IDIOMAS.values())
list_servers = ['fembed', 'mega', 'yourupload', 'streamsb', 'mp4upload', 'mixdrop', 'uqload']
list_quality = []

canonical = {
             'channel': 'ennovelas', 
             'host': config.get_setting("current_host", 'ennovelas', default=''), 
             'host_alt': ["https://www.ennovelas.com/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host + "?op=categories_all&per_page=60&page=1",
                         thumbnail=get_thumb("all", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Nuevos Episodios" , action="new_episodes", url= host + "just_added.html",
                          thumbnail=get_thumb('new_episodes', auto=True), infoLabels={"year": "-"}))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host + "?op=categories_all&name=",
                         thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    if texto != '':
        return list_all(item)
    return []


def list_all(item):
    logger.info()
    
    itemlist = list()
    infoLabels = {"year": "-"}
    
    data = httptools.downloadpage(item.url, canonical=canonical).data
    
    patron  = 'video-post clearfix.*?href="([^"]+).*?'
    patron += 'url\((.*?)\).*?'
    patron += '<p>([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapedtitle
        try:
            infoLabels['season'] = int(scrapertools.find_single_match(title, '\s*(\d{1,3})'))
            title = re.sub('\s*\d{1,3}', '', title)
        except:
            infoLabels['season'] = 1
        itemlist.append(Item(channel=item.channel, title='%s - Temporada %s' % (title, infoLabels['season']), 
                             url=scrapedurl, thumbnail=scrapedthumbnail, action="episodesxseason",
                             contentSerieName=title, infoLabels=infoLabels, contentType='season'))
    #tmdb
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    next_page = scrapertools.find_single_match(data, "<b>\d+</b><a href='([^']+)'")
    if next_page:
        itemlist.append( Item(channel=item.channel, action="list_all", title="Siguiente>>", url=next_page) )
    
    return itemlist


def new_episodes(item):
    logger.info()
    
    itemlist = list()
    infoLabels = item.infoLabels
    
    data = httptools.downloadpage(item.url, canonical=canonical).data
    
    patron  = "videobox.*?url\('(.*?)'\).*?"
    patron += 'href="([^"]+).*?'
    patron += 'center">([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    
    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        title = scrapedtitle
        if scrapertools.find_single_match(title, '(?i)\s+(\d{1,3})\s+temporada'):
            infoLabels["season"] = int(scrapertools.find_single_match(title, '(?i)\s+(\d{1,3})\s+temporada'))
            title =  re.sub('(?i)\s+(\d{1,3})\s+temporada', '', title)
        else:
            infoLabels["season"] = 1
        contentSerieName = title.split("-")[0]
        try:
            infoLabels["episode"] = int(scrapertools.find_single_match(title, 'Capitulo\s*(\d+)'))
        except:
            infoLabels["episode"] = 1
        
        itemlist.append(Item(channel=item.channel, title=title, url=scrapedurl, thumbnail=scrapedthumbnail, action="findvideos",
                        contentSerieName=contentSerieName, infoLabels=infoLabels, contentType="episode"))
    # tmdb
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    
    return itemlist



def episodios(item):
    logger.info()
    
    itemlst = list()
    itemlist = episodesxseason(item)
    
    return itemlist


def episodesxseason(item):
    logger.info()
    
    itemlist = list()
    infoLabels = item.infoLabels
    
    for pagina in range(1,15):
        data = httptools.downloadpage(item.url + "&page=%s" % pagina, canonical=canonical).data
        patron  = "videobox.*?url\('(.*?)'\).*?"
        patron += 'href="([^"]+).*?'
        patron += 'center">([^<]+)'
        matches = scrapertools.find_multiple_matches(data, patron)
        if not matches: break
        
        for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
            try:
                infoLabels["episode"] = int(scrapertools.find_single_match(scrapedtitle, 'Capitulo\s*(\d+)'))
            except:
                infoLabels["episode"] = 1
            infoLabels["season"] = infoLabels["season"] or 1
            
            itemlist.append(Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, action="findvideos",
                            contentSerieName=item.contentSerieName, infoLabels=infoLabels, contentType="episode"))
    
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    
    return itemlist


def findvideos(item):
    logger.info()
    
    itemlist = list()
    infoLabels = item.infoLabels
    
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = 'src: "([^"]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    
    for scrapedurl in matches:
        itemlist.append(Item(channel=item.channel, title="%s", url=scrapedurl, action="play",
                        contentSerieName=item.contentSerieName, infoLabels=infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())
    autoplay.start(itemlist, item)
    
    return itemlist


def play(item):
    logger.info()
    
    item.title = item.contentSerieName
    
    return [item]
