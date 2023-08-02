# -*- coding: utf-8 -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re
from platformcode import config, logger
from core import scrapertools, httptools
from core.item import Item
from core import servertools
from bs4 import BeautifulSoup

canonical = {
             'channel': 'xhamster', 
             'host': config.get_setting("current_host", 'xhamster', default=''), 
             'host_alt': ["https://xhamster.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="lista", title="Útimos videos", url=host + "newest"))
    itemlist.append(Item(channel=item.channel, action="votados", title="Lo mejor"))
    itemlist.append(Item(channel=item.channel, action="vistos", title="Los mas vistos"))
    itemlist.append(Item(channel=item.channel, action="lista", title="Recomendados", url=host + "videos/recommended"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "pornstars"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "channels"))
    itemlist.append(Item(channel=item.channel, action="categorias", title="Categorías", url=host))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/%s?sort=newest" % (host, texto)
    item.extra = "buscar"
    try:
        return lista(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='all-categories')
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.text.strip()
        url += "/newest"
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url))
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    if "pornstars" in item.url:
        matches = soup.find_all('div', class_='pornstar-thumb-container')
    else:
        matches = soup.find_all('div', class_='channel-thumb-container')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if elem.find('div', class_='videos'):   
            cantidad = elem.find('div', class_='videos').text.strip()
        else:
            cantidad = elem.find('div', class_='channel-thumb-container__info-videos').text.strip()
        if cantidad:
            title = "%s (%s)" % (title,cantidad)
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
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
    matches = soup.find_all('div', class_='thumb-list__item')
    for elem in matches:
        if "thumb-plug" in elem['class']:
            continue
        url = elem.a['href']
        title = elem.img['alt']
        # title = elem.find('a', class_='video-thumb-info__name role-pop').text.strip() 
        thumbnail = elem.img['src']
        time = elem.find('div', class_='thumb-image-container__duration').text.strip()
        quality = ""
        if elem.find('i', class_='thumb-image-container__icon--hd'): quality = "HD"
        if elem.find('i', class_='thumb-image-container__icon--uhd'): quality = "4K"
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time,quality,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    if soup.find('a', attrs={'data-page':'next'}):
        next_page = soup.find('a', attrs={'data-page':'next'})
    else:
        next_page = soup.find('a', class_='prev-next-list-link--next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def votados(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, action="lista", title="Día", url=urlparse.urljoin(host, "/best/daily"),
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="lista", title="Semana", url=urlparse.urljoin(host, "/best/weekly"),
             viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="lista", title="Mes", url=urlparse.urljoin(host, "/best/monthly"),
             viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="lista", title="De siempre", url=urlparse.urljoin(host, "/best/"),
             viewmode="movie"))
    return itemlist


def vistos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="lista", title="Día", url=urlparse.urljoin(host, "/most-viewed/daily"),
             viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="lista", title="Semana", url=urlparse.urljoin(host, "/most-viewed/weekly"),
             viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="lista", title="Mes", url=urlparse.urljoin(host, "/most-viewed/monthly"),
             viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="lista", title="De siempre", url=urlparse.urljoin(host, "/most-viewed/"),
             viewmode="movie"))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '"embedUrl":"([^"]+)"')
    url = url.replace("\\", "")
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = 'class="video-tag" href=".*?/pornstars/[^"]+".*?>([^<]+)</a>'
    pornstars = re.compile(patron,re.DOTALL).findall(data)
    for x , value in enumerate(pornstars):
        pornstars[x] = value.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.title.split()
    if "HD" in item.title or "4K" in item.title:
        lista.insert (4, pornstar)
    else:
        lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)
    
    url = scrapertools.find_single_match(data, '"embedUrl":"([^"]+)"')
    url = url.replace("\\", "")
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
