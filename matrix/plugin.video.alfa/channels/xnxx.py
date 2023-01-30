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

# xvideos
canonical = {
             'channel': 'xnxx', 
             'host': config.get_setting("current_host", 'xnxx', default=''), 
             'host_alt': ["https://www.xnxx.com/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*hreflang="?x-default"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Today Selection" , action="lista", url=host + "todays-selection/"))
    itemlist.append(Item(channel=item.channel, title="Top rated" , action="lista", url=host + "best/"))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="lista", url=host + "hits/month/0"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="catalogo", url=host + "pornstars"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host))
    itemlist.append(Item(channel=item.channel, title=""))
    itemlist.append(Item(channel=item.channel, title="Gay" , action="submenu", id="gay"))
    itemlist.append(Item(channel=item.channel, title="Trans" , action="submenu", id="shemale"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Today Selection" , action="lista", url="%s%s/todays-selection/"%(host,item.id)))
    itemlist.append(Item(channel=item.channel, title="Top rated" , action="lista", url="%s%s/best/"%(host,item.id)))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="lista", url="%s%s/hits/month/0"%(host,item.id)))
    if "gay" in item.url:
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="catalogo", url=host + "pornstars-gay"))
    else:
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="catalogo", url=host + "pornstars-trans"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url="%s%s/" %(host,item.id) ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", id=item.id))
    return itemlist



def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    if item.id:
        item.url = "%ssearch/%s/month/%s" % (host,item.id,texto)
    else:
        item.url = "%ssearch/month/%s" % (host,texto)
    item.ref = item.ref
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|\\", "", data)
    patron = '"i":"([^"]+)".*?'
    patron += '"u":"([^"]+)\\?.*?'
    patron += '"tf":"([^"]+)".*?'
    patron += '"n":"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedurl,title,cantidad in matches:
        title = "%s (%s)" %(title, cantidad)
        url = scrapedurl.replace("\/" , "/")
        url= url.replace("/search/","/search/month/")
        url = urlparse.urljoin(host,url)
        thumbnail = scrapedthumbnail.replace("\/" , "/")
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    itemlist.sort(key=lambda x: x.title)
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>|amp;", "", data)
    patron = '<div class="thumb-inside">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'src="([^"]+)".*?'
    patron += '>([^<]+)</a></p>.*?'
    patron += '>([^<]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,thumbnail,scrapedtitle,cantidad in matches:
        if "/shemale" in url:
            url = url.replace("/shemale", "/videos/new/shemale/0")
        elif "/gay" in url:
            url = url.replace("/gay", "/videos/new/gay/0")
        else:
            url += "/videos/new/0"
        url = urlparse.urljoin(host,url)
        title = "%s (%s)" % (scrapedtitle, cantidad)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="listados", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)" class="no-page next-page">Siguiente')
    if next_page=="":
        next_page = scrapertools.find_single_match(data, '<li><a class="active".*?<a href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = ' id="video_(\d+)".*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?'
    patron += 'title="([^"]+)".*?'
    patron += '>([^<]+)<span class="video-hd">.*?'
    patron += '</span>([^<]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for id,url,scrapedthumbnail,scrapedtitle,scrapedtime,quality in matches:
        url = urlparse.urljoin(item.url,url)
        if "/search-video/" in url:
            url = "%s/embedframe/%s" %(host, id)
        title = '[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s' % (scrapedtime,quality,scrapedtitle)
        thumbnail = scrapedthumbnail.replace("THUMBNUM" , "10")
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, quality=quality, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)" class="no-page next">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def listados(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).json
    for Video in  data["videos"]:
        url = Video["u"]
        title = Video["tf"]
        duration = Video["d"]
        thumbnail =  Video["i"]
        hp = Video["hp"]
        hm = Video["hm"]
        quality = ""
        if hp == 1 : quality = "1080p"
        if hp == 0 and hm == 1: quality= "720p"
        if hp == 0 and hm == 0: quality = "360p"
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (duration, quality, title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (duration, title)
        thumbnail = thumbnail.replace("\/", "/")
        url = url.replace("\/", "/")
        url = urlparse.urljoin(host,url)
        plot = ""
        quality = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, quality=quality, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    nb_videos = data['nb_videos']
    nb_per_page = data['nb_per_page']
    current_page = data['current_page']
    current_page += 1
    if nb_videos > (nb_per_page * current_page):
        next_page = current_page
        next_page = re.sub(r"/new/\d+", "/new/{0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="listados", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist



def findvideos(item):
    logger.info()
    itemlist = []
    if "/prof-video-click/" in item.url:
        item.url = httptools.downloadpage(item.url, canonical=canonical).url
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = '<a class="is-pornstar" href="[^"]+">([^<]+)<'
    pornstars = re.compile(patron,re.DOTALL).findall(data)
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.title.split()
    if "[COLOR red]" in item.title:
        lista.insert (4, pornstar)
    else:
        lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)

    if "/prof-video-click/" in item.url:
        item.url = httptools.downloadpage(item.url, canonical=canonical).url
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist