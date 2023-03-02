# -*- coding: utf-8 -*-

from past.utils import old_div
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from core import scrapertools
from core.item import Item
from core import servertools
from platformcode import logger
from core import httptools


host = "https://beeg.com"


url_api = "https://store.externulls.com"
# https://store.externulls.com/facts/file/0954825500144333
# https://store.externulls.com/facts/tag?id=27173&limit=48&offset=0
# https://store.externulls.com/tag/facts/tags?get_original=true&slug=index
def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(action="lista", title="Útimos videos", url= url_api + "/facts/tag?id=27173&limit=48&offset=0"))
    itemlist.append(item.clone(action="categorias", title="Canal", url= url_api + "/tag/facts/tags?get_original=true&slug=index"))
    itemlist.append(item.clone(action="categorias", title="Categorias", url= url_api + "/tag/facts/tags?get_original=true&slug=index"))
    # itemlist.append(item.clone(title="Buscar...", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url =  "%s/index/tag/0/pc?tag=%s" % (url_api, texto)
    
    try:
        return videos(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).json
    for tag in data:
        thumbnail = ""
        id = tag["id"]
        title = tag["tg_name"]
        slug = tag["tg_slug"]
        if tag.get("thumbs", ""):
            th2 = tag["thumbs"]
            thumbnail = "https://thumbs-015.externulls.com/tags/%s" %th2[0]
        url = '%s/facts/tag?slug=%s&limit=48&offset=0' % (url_api, slug)
        if "Canal" in item.title and thumbnail:
            itemlist.append(item.clone(action="lista", title=title, url=url, thumbnail=thumbnail))
        if "Categorias" in item.title and not thumbnail:
            itemlist.append(item.clone(action="lista", title=title, url=url, thumbnail=thumbnail))
            
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).json
    for Video in data:
        logger.debug(Video)
        id = Video['fc_file_id']
        th2= Video["fc_facts"][0]['fc_thumbs']
        segundos = Video["file"]["fl_duration"]
        stuff = Video["file"]["stuff"]
        if stuff.get("sf_name", ""):
            title = stuff["sf_name"]
        else:
            title = id
        plot = ""
        if stuff.get("sf_story", ""):
            plot = stuff["sf_story"]
        horas=int(old_div(segundos,3600))
        segundos-=horas*3600
        minutos=int(old_div(segundos,60))
        segundos-=minutos*60
        if segundos < 10:
            segundos = "0%s" %segundos
        if minutos < 10:
            minutos = "0%s" %minutos
        if horas == 00:
            duration = "%s:%s" % (minutos,segundos)
        else:
            duration = "%s:%s:%s" % (horas,minutos,segundos)
        thumbnail = "https://thumbs-015.externulls.com/videos/%s/%s.jpg" %(id, th2[0])
        # url = '%s/facts/file/%s' % (url_api, id)
        url = "%s/%s" % (host, id)
        title = "[COLOR yellow]%s[/COLOR] %s" %( duration, title)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=thumbnail, 
                             fanart=thumbnail, plot=plot,contentTitle=title, contentType="movie"))
    # Paginador
    page = int(scrapertools.find_single_match(item.url, '&offset=([0-9]+)'))
    if len(itemlist) >= 48:
        next_page = (page+ 48)
        next_page = re.sub(r"&offset=\d+", "&offset={0}".format(next_page), item.url)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page))
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
