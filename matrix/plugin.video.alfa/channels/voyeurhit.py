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

from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import httptools
from core import jsontools as json

#  https://hclips.com    https://hdzog.com  https://hotmovs.com   https://txxx.com 
#  https://tubepornclassic.com  https://upornia.com    https://vjav.com   https://voyeurhit.com  
#  https://desiporn.tube/   https://manysex.com/  https://porntop.com/   https://shemalez.com/  https://thegay.com/ 
#  https://pornzog.com/   https://tporn.xxx/  https://see.xxx/ 

canonical = {
             'channel': 'voyeurhit', 
             'host': config.get_setting("current_host", 'voyeurhit', default=''), 
             'host_alt': ["https://voyeurhit.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
url_api = host + "api/json/videos/%s/%s/%s/60/%s.%s.1.all..%s.json"
httptools.downloadpage(host, canonical=canonical).data


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Ultimas" , action="lista", url=url_api % ("14400", "str", "latest-updates", "", "", "")))
    itemlist.append(Item(channel=item.channel, title="Mejor valoradas" , action="lista", url=url_api % ("14400", "str", "top-rated", "", "", "month")))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=url_api % ("14400", "str", "most-popular", "", "", "month")))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista",  url=url_api % ("14400", "str", "most-commented", "", "", "month") ))
    # itemlist.append(Item(channel=item.channel, title="Pornstar" , action="pornstar", url=host + "api/json/models/86400/%s/filt........../most-popular/48/1.json" %"str"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "api/json/channels/14400/%s/most-viewed/80/..1.json" %"str"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "api/json/categories/14400/%s.all.json" %"str"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", orientation="str"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%sapi/videos.php?params=259200/%s/relevance/60/search..1.all..&s=%s&sort=latest-updates&date=all&type=all&duration=all" % (host,item.orientation,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def pornstar(item):
    logger.info()
    itemlist = []
    if not item.orientation:
        item.orientation = "str"
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for cat in  JSONData["models"]:
        scrapedtitle = cat["title"]
        dir = cat["dir"]
        scrapedthumbnail =  cat["img"]
        num = cat["statistics"]
        n = 'videos'
        num = num.get(n,n)
        thumbnail = scrapedthumbnail.replace("\/", "/")
        scrapedplot = ""
        url = url_api % ("14400", item.orientation, "latest-updates", "model", dir, "")
        title = "%s (%s)" %(scrapedtitle,num)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, thumbnail=thumbnail , plot=scrapedplot) )
    total= int(JSONData["total_count"])
    page = int(scrapertools.find_single_match(item.url,'.*?(\d+).json'))
    url_page = scrapertools.find_single_match(item.url,'(.*?)\d+.json')
    next_page = (page+ 1)
    if (page*60) < total:
        next_page = "%s%s.json" %(url_page,next_page)
        itemlist.append(Item(channel=item.channel, action="pornstar", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist



def catalogo(item):
    logger.info()
    itemlist = []
    if not item.orientation:
        item.orientation = "str"
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for cat in  JSONData["channels"]:
        scrapedtitle = cat["title"]
        dir = cat["dir"]
        scrapedthumbnail =  cat["cf3"]
        num = cat["statistics"]
        n = 'videos'
        num = num.get(n,n)
        thumbnail = scrapedthumbnail.replace("\/", "/")
        plot = ""
        url = url_api % ("7200", item.orientation, "latest-updates", "channel", dir, "")
        title = "%s (%s)" %(scrapedtitle,num)
        itemlist.append(Item(channel=item.channel, action="lista", title=title , url=url , 
                        thumbnail=thumbnail , plot=plot) )
    total= int(JSONData["total_count"])
    page = int(scrapertools.find_single_match(item.url,'.*?.(\d+).json'))
    url_page = scrapertools.find_single_match(item.url,'(.*?).\d+.json')
    next_page = (page+ 1)
    if (page*60) < total:
        next_page = "%s.%s.json" %(url_page,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    if not item.orientation:
        item.orientation = "str"
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers, canonical=canonical).data
    JSONData = json.load(data)
    for cat in  JSONData["categories"]:
        scrapedtitle = cat["title"]
        dir = cat["dir"]
        num = cat["total_videos"]
        url = url_api % ("14400", item.orientation, "latest-updates", "categories", dir, "day")
        thumbnail = ""
        scrapedplot = ""
        title = "%s (%s)" %(scrapedtitle,num)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, thumbnail=thumbnail, plot=scrapedplot) )
    return  sorted(itemlist, key=lambda i: i.title)


def lista(item):
    logger.info()
    itemlist = []
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for Video in  JSONData["videos"]:
        video_id = Video["video_id"]
        dir = Video["dir"]
        scrapedtitle = Video["title"]
        duration = Video["duration"]
        scrapedthumbnail =  Video["scr"]
        scrapedhd =  Video["props"]
        url = "%sembed/%s" %(host,video_id)
        if scrapedhd:
            title = "[COLOR yellow]%s[/COLOR] [COLOR tomato]HD[/COLOR] %s" % (duration, scrapedtitle)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (duration, scrapedtitle)
        thumbnail = scrapedthumbnail.replace("\/", "/")
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title , url=url, thumbnail=thumbnail, 
                        fanart=thumbnail, plot=plot, contentTitle=title) )
    total= int(JSONData["total_count"])
    page = int(scrapertools.find_single_match(item.url,'(\d+).all..'))
    url_page = scrapertools.find_single_match(item.url,'(.*?).\d+.all..')
    post = scrapertools.find_single_match(item.url,'all..(.*)')
    next_page = (page+ 1)
    if (page*60) < total:
        next_page = "%s.%s.all..%s" %(url_page,next_page,post)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle= item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle= item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
