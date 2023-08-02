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

# xnxx
canonical = {
             'channel': 'xvideos', 
             'host': config.get_setting("current_host", 'xvideos', default=''), 
             'host_alt': ["https://www.xvideos.com/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*hreflang="?x-default"?'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="Lo mejor" , action="lista", url=host + "best/"))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="catalogo", url=host + "pornstars-index/from/worldwide/ever"))
    itemlist.append(Item(channel=item.channel, title="WebCAM" , action="catalogo", url=host + "webcam-models-index/from/worldwide/ever"))
    itemlist.append(Item(channel=item.channel, title="Modelos Eroticas" , action="catalogo", url=host + "erotic-models-index/from/worldwide/ever"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "channels-index/from/worldwide/top"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "tags"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    itemlist.append(Item(channel=item.channel, title=""))
    itemlist.append(Item(channel=item.channel, title="Gay" , action="submenu", id="gay"))
    itemlist.append(Item(channel=item.channel, title="Trans" , action="submenu", id="shemale"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []     
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url="%s%s"%(host,item.id)))
    if "gay" in item.id:
        itemlist.append(Item(channel=item.channel, title="Top rated" , action="lista", url="%sbest-of-gay/"%host))
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="catalogo", url=host + "porn-actors-index/gay/from/worldwide/ever"))
        itemlist.append(Item(channel=item.channel, title="Amateur" , action="catalogo", url=host + "amateurs-index/gay/from/worldwide/ever"))
        itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "channels-gay/from/worldwide/top"))
    else:
        itemlist.append(Item(channel=item.channel, title="Top rated" , action="lista", url="%sbest-of-shemale/"%host))
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="catalogo", url=host + "pornstars-index/trans/from/worldwide/ever"))
        itemlist.append(Item(channel=item.channel, title="Amateur" , action="catalogo", url=host + "amateurs-index/trans/from/worldwide/ever"))
        itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "channels-trans/from/worldwide/top"))
    itemlist.append(Item(channel=item.channel, title="Categoria" , action="categorias", url=host + "tags", id=item.id ))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", id=item.id))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    if item.id:
        item.url = "%s?k=%s&sort=uploaddate&typef=%s" % (host, texto, item.id)
    else:
        item.url = "%s?k=%s&sort=uploaddate" % (host, texto)

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
    soup = create_soup(item.url).find('ul', id='tags')
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.b.text.strip()
        cantidad = elem.span.text.strip()
        url = url.replace("/tags/", "/tags/s:uploaddate/")
        if item.id:
            url = url.replace("/tags/", "/tags/t:%s/" %item.id)
        url = urlparse.urljoin(item.url,url)
        title = "%s (%s)" % (title, cantidad)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             thumbnail="" ) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', id=re.compile(r"^profile_\w+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.find(class_='profile-name')
        if "Canal" in item.title:
            strong = title.strong.text
            title= title.text.replace("%s" %strong, "").strip()
        else:
            title= title.a.text.strip()
        thumbnail = elem.script.text.strip()
        thumbnail = scrapertools.find_single_match(thumbnail, 'src="([^"]+)"')
        cantidad = elem.find('span', class_='with-sub')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        if "/gay" in url or "/shemale" in url:
            url = url.replace("/gay", "/videos/new/gay/0").replace("/shemale", "/videos/new/shemale/0")
        else:
            url += "/videos/new/0"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="listados", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next-page')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    soup = create_soup(item.url)
    matches = soup.find_all('div', id=re.compile(r"^video_\d+"))
    for elem in matches:
        url = elem.a['href']
        id = elem['data-id']
        if "/search-video/" in url:
            url = "%s/video%s/a" %(host,id)
        if "/prof-video-click/" in url:
            url = scrapertools.find_single_match(str(url), '/(\d+/[A-z0-9_]+)')
            url = "/video%s" %url
        title = elem.find('p', class_='title').a['title']
        thumbnail = elem.img['data-src']
        thumbnail = thumbnail.replace("THUMBNUM.", "9.")
        time = elem.find('span', class_='duration').text.strip()
        quality = elem.find('span', class_='video-hd-mark')
        url = urlparse.urljoin(host,url)
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time,quality.text.strip(),title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next-page')
    if next_page:
        next_page = next_page['href']
        if "#" in next_page:
            next_page = scrapertools.find_single_match(str(next_page), '(\d+)')
            next_page = re.sub(r"/\d+", "/{0}".format(next_page), item.url)
        else:
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
            title = "[COLOR yellow]%s[/COLOR] [COLOR tomato]%s[/COLOR] %s" % (duration, quality, title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (duration, title)
        thumbnail = thumbnail.replace("\/", "/")
        url = scrapertools.find_single_match(url, '/(\d+/[A-z0-9_-]+)')
        url = "/video%s" %url
        url = urlparse.urljoin(item.url,url)
        plot = ""
        quality = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, quality=quality,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
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
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist