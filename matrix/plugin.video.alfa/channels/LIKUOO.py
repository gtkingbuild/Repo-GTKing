# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re


from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

canonical = {
             'channel': 'LIKUOO', 
             'host': config.get_setting("current_host", 'LIKUOO', default=''), 
             'host_alt': ["https://www.likuoo.video/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# JETLOAD

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Ultimos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="categorias", url=host + "pornstars/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "all-channels/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/?s=%s" % (host, texto)
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
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<div class="item_p">.*?<a href="([^"]+)" title="([^"]+)"><img src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedplot = ""
        if not scrapedthumbnail.startswith("https"):
            thumbnail = "https:%s" % scrapedthumbnail
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=thumbnail, thumbnail=thumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'...<a href="([^"]+)" class="next">&#187;</a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<div class="item">.*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'src="(.*?)".*?'
    patron += '<div class="runtime">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,thumbnail,scrapedtime in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        scrapedtime = scrapedtime.replace("m", ":").replace("s", "")
        title = "[COLOR yellow]%s[/COLOR] %s" %(scrapedtime,scrapedtitle)
        contentTitle = title
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page = scrapertools.find_single_match(data,'...<a href="([^"]+)" class="next">&#187;</a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|amp;|\s{2}|&nbsp;", "", data)
    patron = 'url:\'([^\']+)\'.*?'
    patron += 'data:\'([^\']+)\''
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl,post in matches:
        post = post.replace("%3D", "=")
        scrapedurl = host + scrapedurl
        datas = httptools.downloadpage(scrapedurl, post=post, headers={'Referer':item.url}).data
        datas = datas.replace("\\", "")
        url = scrapertools.find_single_match(datas, 'src="([^"]+)"')
        if not url.startswith("https"):
            url = "https:%s" % url
        itemlist.append(Item(channel=item.channel, action="play", title="%s",contentTitle = item.title, url=url ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|amp;|\s{2}|&nbsp;", "", data)
    patron = 'url:\'([^\']+)\'.*?'
    patron += 'data:\'([^\']+)\''
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl,post in matches:
        post = post.replace("%3D", "=")
        scrapedurl = host + scrapedurl
        datas = httptools.downloadpage(scrapedurl, post=post, headers={'Referer':item.url}).data
        datas = datas.replace("\\", "")
        url = scrapertools.find_single_match(datas, 'src="([^"]+)"')
        if not url.startswith("https"):
            url = "https:%s" % url
        itemlist.append(Item(channel=item.channel, action="play", title="%s",contentTitle = item.title, url=url ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
