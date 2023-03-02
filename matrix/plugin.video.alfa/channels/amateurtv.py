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
from core import jsontools as json
canonical = {
             'channel': 'amateurtv', 
             'host': config.get_setting("current_host", 'amateurtv', default=''), 
             'host_alt': ["https://www.amateur.tv/"], 
             'host_black_list': [], 
             'pattern': ['property="og:url" content="?([^"|\s*]+)["|\s*]"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
hosta = "%sv3/readmodel/cache/cams/%s/0/50/es"

httptools.downloadpage(host, canonical=canonical).data

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel,title="Destacados" , action="lista", url=hosta % (host,"a")))
    itemlist.append(Item(channel = item.channel,title="Mujer" , action="lista", url=hosta %(host, "w")))
    itemlist.append(Item(channel = item.channel,title="Parejas" , action="lista", url=hosta %(host, "c")))
    itemlist.append(Item(channel = item.channel,title="Hombres" , action="lista", url=hosta %(host, "m")))
    itemlist.append(Item(channel = item.channel,title="Trans" , action="lista", url=hosta %(host, "t")))
    itemlist.append(Item(channel = item.channel,title="Privado" , action="lista", url=hosta %(host, "p")))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).json
    data = data['cams']
    for elem in data['nodes']:
        id = elem['id']
        is_on = elem['online']
        thumbnail = elem['imageURL']
        country  = elem['country']
        name = elem['user']['username']
        age = elem['user']['age']
        quality = elem['hd']
        title = "%s %s %s" %(name, age, country)
        if not is_on:
            title= "[COLOR red] %s[/COLOR]" % title
        url = "%sv3/readmodel/show/%s/es" %(host, name)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel,action=action, title=title, url=url, thumbnail=thumbnail,
                                   plot=plot, fanart=thumbnail, contentTitle=title ))
    count= data['totalCount']
    current_page = scrapertools.find_single_match(item.url, ".*?/(\d+)/50/")
    current_page = int(current_page)
    if current_page <= int(count) and (int(count) - current_page) > 50:
        current_page += 50
        next_page = re.sub(r"\d+/50/", "{0}/50/".format(current_page), item.url)
        itemlist.append(Item(channel = item.channel,action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).json
    url = data['videoTechnologies']['fmp4']
    url += "|ignore_response_code=True"
    itemlist.append(Item(channel = item.channel,action="play", contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).json
    url = data['videoTechnologies']['fmp4']
    # url = httptools.downloadpage(url, follow_redirects=False).headers["location"]
    url += "|ignore_response_code=True"
    itemlist.append(Item(channel = item.channel,action="play", title= "Directo", contentTitle = item.title, url=url))
    return itemlist

