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

from channels import autoplay
from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, tmdb
from core import servertools, channeltools
from bs4 import BeautifulSoup
from channelselector import get_thumb


IDIOMAS = {"esp": "CAST", "lat": "LAT", "sub": "VOSE"}

list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['fembed']

canonical = {
             'channel': 'pelisencastellano', 
             'host': config.get_setting("current_host", 'pelisencastellano', default=''), 
             'host_alt': ["https://pelisencastellano.net/"], 
             'host_black_list': ["https://pelisencastellano.com/"], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host
__channel__ = canonical['channel']

__comprueba_enlaces__ = config.get_setting('comprueba_enlaces', __channel__)
__comprueba_enlaces_num__ = config.get_setting('comprueba_enlaces_num', __channel__)
try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


def mainlist(item):
    logger.info()
    itemlist = []
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(item.clone(title="Peliculas" , action="lista", url= host, thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(item.clone(title="Genero" , action="categorias", url= host, thumbnail=get_thumb('genres', auto=True)))
    itemlist.append(item.clone(title="Buscar...", action="search", thumbnail=get_thumb("search", auto=True)))
    itemlist.append(item.clone(title="Configurar canal...", action="configuracion", text_color="gold", folder=False, thumbnail=get_thumb("setting_0.png")))
    
    autoplay.show_option(item.channel, itemlist)
    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        item.url = "%s?s=%s" % (host, texto)
        if texto != "":
            return lista(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('a', class_='nav-link')
    for elem in matches:
        url = elem['href']
        title = elem.text
        # url = urlparse.urljoin(item.url,url)
        if not "peticiones" in url:
            itemlist.append(item.clone(channel=item.channel, action="lista", title=title , url=url, 
                              section=item.section) )
    return itemlist


def create_soup(url, referer=None, post=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    elif post:
        data = httptools.downloadpage(url, post=post, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url, referer=host)
    matches = soup.find_all("div", class_='card')
    for elem in matches:
        url = elem.a['href']
        thumbnail = elem.img['src']
        title = elem.find('div', class_='card-title').text.replace("en Castellano", "").strip()
        title = title.split()
        year = title[-2]
        title = " ".join(title[1:-2])
        lang = "esp"
        language = []
        language.append(IDIOMAS.get(lang, lang))
        contentTitle = title
        if year == '':
            year = '-'
            
        if not config.get_setting('unify') and not channeltools.get_channel_parameters(__channel__)['force_unify']:
            if year != "-":
                title = "%s [COLOR cyan](%s)[/COLOR] [COLOR darkgrey]%s[/COLOR]" % (title,year, language)
            else:
                title = "%s [COLOR darkgrey]%s[/COLOR]" % (title, language)
        else:
            title = title
        itemlist.append(Item(channel=item.channel, action = "findvideos", url=url, title=title, contentTitle = contentTitle,
                        thumbnail=thumbnail, language=language, infoLabels={"year": year}) )
    tmdb.set_infoLabels(itemlist, True)

    next_page = soup.find('span', class_='is-inactive')
    if next_page and next_page.find_next_sibling("a"):
        next_page = next_page.find_next_sibling("a")['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    serv=[]
    data = httptools.downloadpage(item.url, canonical=canonical).data
    output = scrapertools.find_single_match(data, 'var output = "(.*?)output ').replace("\\", "")
    output = output.split(";")
    quality = scrapertools.find_single_match(data, "<strong>Calidad: </strong> (\d+)p<")
    online = scrapertools.find_single_match(data, '<div class="centradito"><script>[A-z0-9]+ \(([^\)]+)')
    online = online.replace('"', '').split(",")
    for elem in output:
        if "href" in elem :
            ref = scrapertools.find_single_match(elem, 'href="([^"]+)"')
            id = scrapertools.find_single_match(elem, 'codigo(\d+)')
            if id:
                id = (int(id)-1)
            if "codigo" in ref:
                url = online[id]
            if not "no.html" in ref:
                url = "%s%s" %(ref, online[id])
            itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=url))
    descarga = scrapertools.find_single_match(data, "var abc = '([^']+)'")
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=descarga))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())

    # Requerido para Filtrar enlaces
    if __comprueba_enlaces__:
        itemlist = servertools.check_list_links(itemlist, __comprueba_enlaces_num__)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra !='findvideos' and not "/episodios/" in item.url :
        itemlist.append(item.clone(action="add_pelicula_to_library", 
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                             extra="findvideos", contentTitle=item.contentTitle)) 
    return itemlist

