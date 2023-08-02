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
from bs4 import BeautifulSoup

canonical = {
             'channel': 'bongacams', 
             'host': config.get_setting("current_host", 'bongacams', default=''), 
             'host_alt': ["https://bongacams.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
hosta = "%stools/listing_v3.php?livetab=%s&online_only=true&offset=0&can_pin_models=true&limit=40"  

def mainlist(item):
    logger.info()
    itemlist = []
    # httptools.downloadpage(host, canonical=canonical).data ### Esta en categorias
    itemlist.append(Item(channel = item.channel, title="Female" , action="lista", url=hosta %(host, "female")))
    itemlist.append(Item(channel = item.channel, title="Couples" , action="lista", url=hosta % (host, "couples")))
    itemlist.append(Item(channel = item.channel, title="Male" , action="lista", url=hosta % (host, "male")))
    itemlist.append(Item(channel = item.channel, title="Transexual" , action="lista", url=hosta % (host, "/transsexual")))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="categorias", url=host))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/" % (host,texto)
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
    soup = create_soup(item.url)
    matches = soup.find_all('li', class_='hbd_item')
    for elem in matches:
        cat = elem.a['href'].replace("/", "")
        cantidad = elem.find('span', class_='hbd_s_live')
        if cantidad:
            title = "%s %s" % (cat,cantidad.text.strip())
        url = "%stools/listing_v3.php?livetab=%s&online_only=true&offset=0&can_pin_models=true&category=%s&limit=40" %(host,"female", cat)
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel = item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    headers={'X-Requested-With' : 'XMLHttpRequest'}
    data = httptools.downloadpage(item.url, headers=headers, canonical=canonical).json
    for elem in data['models']:
        plot= ""
        thumbnail = elem['thumb_image'].replace("{ext}", "webp")
        title = elem['username']
        name = elem['display_name']
        name = title
        thumbnail = "https:%s" % thumbnail
        quality = elem['vq']
        quality = quality.split("x")[-1]
        if "960" in quality: quality = "720"
        title += " [COLOR red]%sp[/COLOR]" %quality
        if elem.get("about_me", ""):
            plot = elem['about_me']
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel, action=action, title=title, thumbnail=thumbnail, name=name,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
                               
    count= data['online_count']
    current_page = scrapertools.find_single_match(item.url, ".*?&offset=(\d+)")
    current_page = int(current_page)
    if current_page <= int(count) and (int(count) - current_page) > 40:
        current_page += 40
        next_page = re.sub(r"&offset=\d+", "&offset={0}".format(current_page), item.url)
        itemlist.append(Item(channel = item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    url="http://bongacams.com/tools/amf.php"
    post = {'method' : 'getRoomData', 'args[]' : 'false', 'args[]' : item.name}
    headers={'X-Requested-With' : 'XMLHttpRequest'}
    data = httptools.downloadpage(url, post=post, headers=headers).json
    url = data['localData']['videoServerUrl']
    if url.startswith("//mobile"):
       videourl = 'https:' + url + '/hls/stream_' + item.name + '.m3u8'
    else:
       videourl = 'https:' + url + '/hls/stream_' + item.name + '/playlist.m3u8'
    itemlist.append(Item(channel = item.channel, action="play", title=videourl, contentTitle = item.title, url=videourl, server="Directo" ))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    url="http://bongacams.com/tools/amf.php"
    post = {'method' : 'getRoomData', 'args[]' : item.name}
    headers={'X-Requested-With' : 'XMLHttpRequest'}
    data = httptools.downloadpage(url, post=post, headers=headers).json
    url = data['localData']['videoServerUrl']
    if url.startswith("//mobile"):
       videourl = 'https:' + url + '/hls/stream_' + item.name + '.m3u8'
    else:
       videourl = 'https:' + url + '/hls/stream_' + item.name + '/playlist.m3u8'
    itemlist.append(Item(channel = item.channel, action="play", title=videourl, contentTitle = item.title, url=videourl, server="Directo" ))
    return itemlist