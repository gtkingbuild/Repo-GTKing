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
             'channel': 'analdin', 
             'host': config.get_setting("current_host", 'analdin', default=''), 
             'host_alt': ["https://www.analdin.com/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s* id="item1"?'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevas" , action="lista", url=host + "más-reciente/?mode=async&function=get_block&block_id=list_videos_latest_videos_list&sort_by=post_date&from=1"))
    itemlist.append(item.clone(title="Mas Vistas" , action="lista", url=host + "más-visto/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=video_viewed_month&from=1"))
    itemlist.append(item.clone(title="Mejor valorada" , action="lista", url=host + "mejor-valorado/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=rating_month&from=1"))
    itemlist.append(item.clone(title="Canal" , action="catalogo", url=host))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "categorías/"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%sbuscar/%s/?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&q=%s&category_ids=&sort_by=post_date&from_videos=1" % (host, texto, texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = scrapertools.find_single_match(data,'<strong class="popup-title">Sponsors</strong>(.*?)</div>')
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<li><a class="item" href="([^"]+)" title="([^"]+)">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedurl = "%s?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1" % scrapedurl
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<li class="arrow"><a rel="next" href="([^"]+)">&raquo;</a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<a class="item" href="([^"]+)" title="([^"]+)">.*?'
    patron += 'src="([^"]+)".*?'
    patron += '<div class="videos">([^"]+)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,cantidad in matches:
        scrapedplot = ""
        scrapedtitle = "%s (%s)" % (scrapedtitle, cantidad)
        # scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        scrapedurl = "%s?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1" %scrapedurl
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail,  thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return sorted(itemlist, key=lambda i: i.title)


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<a class="popup-video-link" href="([^"]+)".*?'
    patron += 'thumb="([^"]+)".*?'
    patron += '<div class="duration">(.*?)</div>.*?'
    patron += '<strong class="title">\s*([^"]+)</strong>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtime,scrapedtitle  in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = "[COLOR yellow]%s[/COLOR] %s" % (scrapedtime, scrapedtitle)
        thumbnail = scrapedthumbnail
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=thumbnail, plot=plot,
                              fanart=thumbnail, contentTitle = title))
    last_page= scrapertools.find_single_match(data,'<li class="last-page">.*?:(\d+)">Última<')
    page = scrapertools.find_single_match(item.url, "(.*?)\d+")
    current_page = scrapertools.find_single_match(item.url, ".*?(\d+)")
    if last_page:
        last_page = int(last_page)
    if current_page:
        current_page = int(current_page)
    if current_page < last_page:
        current_page += 1
        next_page = "%s%s" %(page,current_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(action="play", title= "%s", contentTitle= item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    if "kt_player" in data:
        url = item.url
    itemlist.append(item.clone(action="play", title= "%s", contentTitle= item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
