# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import jsontools as json

IDIOMAS = {'vo': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = ['default']
list_servers = []

canonical = {
             'channel': 'camsoda', 
             'host': config.get_setting("current_host", 'camsoda', default=''), 
             'host_alt': ["https://camsoda.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
httptools.downloadpage(host, canonical=canonical).data


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "api/v1/browse/react/?p=1"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "api/v1/tags/index?page=1"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%sapi/v1/browse/react/search/%s?p=1" % (host, texto)
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
    data = httptools.downloadpage(item.url, canonical=canonical).json
    for elem in data['tag_list']:
        name = elem['tag_slug']
        cantidad = elem['tag_count']
        title = "%s (%s)" %(name, cantidad)
        thumbnail = ""
        url = "%sapi/v1/browse/react/tag/%s-cams?p=1" % (host,name)
        plot = "[COLOR yellow]%s[/COLOR]" %name
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot) )
    count= data['tag_count']
    current_page = scrapertools.find_single_match(item.url, ".*?page=(\d+)")
    current_page = int(current_page)
    if (current_page * 26) <= int(count) and (int(count) - (current_page*26)) > 26:
        current_page += 1
        next_page = re.sub(r"page=\d+", "page={0}".format(current_page), item.url)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).json
    for elem in data['userList']:
        title = elem['username']
        is_on = elem['status']
        thumbnail = elem['thumbUrl']
        username = "guest_22596"
        url = "%sapi/v1/video/vtoken/%s?username=%s" % (host,title,username)
        if not "online" in is_on:
            title = "[COLOR red]%s[/COLOR]" % title
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, contentTitle=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail))
    count= data['totalCount']
    current_page = scrapertools.find_single_match(item.url, ".*?p=(\d+)")
    current_page = int(current_page)
    if (current_page * 60) <= int(count) and (int(count) - (current_page*60)) > 60:
        current_page += 1
        next_page = re.sub(r"p=\d+", "p={0}".format(current_page), item.url)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).json
    server = data['edge_servers']
    token = data['token']
    dir = data['stream_name']
    if dir == "":
        return False, "El video ha sido borrado o no existe"
    if "vide" in server[0]:
        url = "https://%s/cam/mp4:%s_h264_aac_480p/chunklist_w206153776.m3u8?token=%s"  %(server[0],dir,token)
    else:
        url = "https://%s/%s_v1/tracks-v4a2/mono.m3u8?token=%s" %(server[0],dir,token)
    # url += "|verifypeer=false"
    itemlist.append(item.clone(action="play", url=url, server="Directo" ))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).json
    server = data['edge_servers']
    token = data['token']
    dir = data['stream_name']
    if dir == "":
        return False, "El video ha sido borrado o no existe"
    if "vide" in server[0]:
        url = "https://%s/cam/mp4:%s_h264_aac_480p/chunklist_w206153776.m3u8?token=%s"  %(server[0],dir,token)
    else:
        url = "https://%s/%s_v1/tracks-v4a2/mono.m3u8?token=%s" %(server[0],dir,token)
    # url += "|verifypeer=false"
    itemlist.append(item.clone(action="play", title=url, contentTitle = item.title, url=url, server="Directo" ))
    return itemlist