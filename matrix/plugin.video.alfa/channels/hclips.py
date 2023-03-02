# -*- coding: utf-8 -*-
#------------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from core import jsontools as json
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

#  https://hclips.com    https://hdzog.com  https://hotmovs.com   https://txxx.com 
#  https://tubepornclassic.com  https://upornia.com    https://vjav.com   https://voyeurhit.com  
#  https://desiporn.tube/   https://manysex.com/  https://porntop.com/   https://shemalez.com/  https://thegay.com/ 
#  https://pornzog.com/   https://tporn.xxx/  https://see.xxx/ 

canonical = {
             'channel': 'hclips', 
             'host': config.get_setting("current_host", 'hclips', default=''), 
             'host_alt': ["https://hclips.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
url_api = "%sapi/json/videos/86400/%s/%s/60/%s.%s.1.all..day.json"
httptools.downloadpage(host, canonical=canonical).data


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=url_api % (host, "str", "latest-updates", "", "")))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="lista", url=url_api %  (host, "str", "most-popular", "", "")))
    itemlist.append(Item(channel=item.channel, title="Comentado" , action="lista", url=url_api %  (host, "str", "most-commented", "", "")))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="lista", url=url_api %  (host, "str", "longest", "", "")))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="canal", url=host + "api/json/channels/14400/%s/most-viewed/80/..1.json" %"str"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "api/json/categories/14400/%s.all.json" %"str"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", orientation="str"))

    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel=item.channel, title="Trans", action="submenu", orientation="she"))
    itemlist.append(Item(channel=item.channel, title="Gay", action="submenu", orientation="gay"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=url_api % (host, item.orientation, "latest-updates", "", "")))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="lista", url=url_api % (host, item.orientation, "most-popular", "", "")))
    itemlist.append(Item(channel=item.channel, title="Comentado" , action="lista", url=url_api %  (host, item.orientation, "most-commented", "", "")))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="lista", url=url_api % (host, item.orientation, "longest", "", "")))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="canal", url=host + "api/json/channels/14400/%s/most-viewed/80/..1.json" % item.orientation, orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "api/json/categories/14400/%s.all.json" % item.orientation, orientation=item.orientation))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", orientation=item.orientation))
    
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%sapi/videos.php?params=259200/%s/%s/60/search..1.all..day&s=%s" % (host,item.orientation,"latest-updates",texto)
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
    if not item.orientation:
        item.orientation = "str"
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for Video in  JSONData["categories"]:
        scrapedtitle = Video["title"]
        dir = Video["dir"]
        vidnum = Video["total_videos"]
        url = url_api %(host, item.orientation, "latest-updates", "categories", dir)
        scrapedplot = ""
        title = "%s (%s)" % (scrapedtitle, vidnum)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=url,
                               thumbnail="", plot=scrapedplot) )
    return itemlist


def canal(item):
    logger.info()
    itemlist = []
    if not item.orientation:
        item.orientation = "str"
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for Video in  JSONData["channels"]:
        scrapedtitle = Video["title"]
        dir = Video["dir"]
        thumbnail= Video["cf4"]
        vidnum = Video["statistics"]
        url = "%sapi/json/videos/86400/%s/latest-updates/20/channel.%s.1.all...json" % (host, item.orientation,dir)
        vidnum = scrapertools.find_single_match(vidnum, '"videos":"(\d+)"')
        thumbnail = thumbnail.replace("\/", "/")
        scrapedplot = ""
        title = "%s (%s)" % (scrapedtitle, vidnum)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=url,
                             fanart=thumbnail, thumbnail=thumbnail))
    total= int(JSONData["total_count"])
    page = int(scrapertools.find_single_match(item.url,'(\d+).json'))
    url_page = scrapertools.find_single_match(item.url,'(.*?).\d+.json')
    next_page = (page+ 1)
    if (page*80) < total:
        next_page = "%s.%s.json" %(url_page,next_page)
        itemlist.append(Item(channel=item.channel, action="canal", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers, canonical=canonical).data
    JSONData = json.load(data)
    for Video in  JSONData["videos"]:
        tit = Video["title"]
        id = Video["video_id"]
        veo = Video["dir"]
        time= Video["duration"]
        thumbnail = Video["scr"]
        quality = Video["props"]
        # url = "%sembed/%s/" % (host,id)
        url = "%svideos/%s/%s/" %(host,id,dir)
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,tit)
        if "hd" in quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,tit)
        contentTitle = title
        thumbnail = thumbnail.replace("\/", "/")
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle = contentTitle, url=url,
                             fanart=thumbnail, thumbnail=thumbnail, plot=plot))
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
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.contentTitle, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.contentTitle, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist