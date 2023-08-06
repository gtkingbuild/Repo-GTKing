# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse
import re

from platformcode import config, logger
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from channels import filtertools
from modules import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['verystream']

host = 'http://www.pornhive.tv/en'

# link caidos

def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append( Item(channel=item.channel, title="Peliculas" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search?keyword=%s" % texto
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if item.title == "Categorias" :
        data = scrapertools.find_single_match(data,'Categories(.*?)Channels')
    else:
        data = scrapertools.find_single_match(data,'Channels(.*?)</ul>')
    patron  = '<li><a href="([^"]+)" title="[^"]+">(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<div class="col-lg-3 col-md-3 col-sm-4 col-xs-6 col-thumb panel-video-\d+">.*?'
    patron  += '<a href="([^"]+)".*?'
    patron  += 'data-src="([^"]+)".*?'
    patron  += 'alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="findvideos" , title=title, url=scrapedurl, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle=title))
    next_page = scrapertools.find_single_match(data,'<li><a href="([^"]+)" data-ci-pagination-page="\d+" rel="next">Next &rsaquo;')
    if next_page != "" :
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def findvideos(item):
    import base64
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = ';extra_urls\[\d+\]=\'([^\']+)\''
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl in matches:
        url = base64.b64decode(scrapedurl).decode('utf-8')
        if "strdef" in url: 
            url = decode_url(url)
            if "strdef" in url:
                url = httptools.downloadpage(url).url
        elif "vcdn." in url:
            server = "fembed"

###################################### ES FEMBED

        # elif "vcdn" in url:
            # url = url.replace("https://vcdn.pw/v/", "https://vcdn.pw/api/source/")
            # post = "r=&d=vcdn.pw"
            # data1 = httptools.downloadpage(url, post=post).data
            # scrapedurl = scrapertools.find_single_match(data1,'"file":"([^"]+)"')
            # url = scrapedurl.replace("\/", "/")
            # url = httptools.downloadpage(url).url
##########################################
            itemlist.append(item.clone(action="play", server= server, url=url))
        # itemlist.append(item.clone(action="play", title="%s", url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 


    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist


def decode_url(txt):
    import base64
    logger.info()
    itemlist = []
    data = httptools.downloadpage(txt).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    rep = True
    while rep == True:
        b64_data = scrapertools.find_single_match(data, '\(dhYas638H\("([^"]+)"\)')
        if b64_data:
            b64_url = base64.b64decode(b64_data + "=").decode("utf8")
            b64_url = base64.b64decode(b64_url + "==").decode("utf8")
            data = b64_url
        else:
            rep = False
    url = scrapertools.find_single_match(b64_url, '<iframe src="([^"]+)"')
    return url
