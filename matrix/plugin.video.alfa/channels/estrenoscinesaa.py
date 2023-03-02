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
from core import servertools
from channels import filtertools
from bs4 import BeautifulSoup
from channelselector import get_thumb

list_language = []
list_servers = ['Fembed', 'Uqload', 'Youtube']
list_quality = []

canonical = {
             'channel': 'estrenoscinesaa', 
             'host': config.get_setting("current_host", 'estrenoscinesaa', default=''), 
             'host_alt': ["https://www.estrenoscinesaa.com/"], 
             'host_black_list': [], 
             'pattern': '<link\s*rel="shortcut\s*icon"\s*href="([^"]+)"', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

__channel__= canonical['channel']
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
    
    itemlist.append(item.clone(title="Peliculas" , action="lista", url= host + "movies/", thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(item.clone(title="Series", action="lista", url= host + "tvshows/", thumbnail=get_thumb("tvshows", auto=True)))
    itemlist.append(item.clone(title="Genero" , action="categorias", url= host, thumbnail=get_thumb('genres', auto=True)))
    itemlist.append(item.clone(title="Buscar", action="search", thumbnail=get_thumb("search", auto=True)))
    
    itemlist.append(item.clone(title="Configurar canal...", text_color="gold", action="configuracion", thumbnail=get_thumb('setting_0.png')))
    autoplay.show_option(item.channel, itemlist)
    return itemlist


def configuracion(item):
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        item.url = "%s/?s=%s" % (host, texto)
        item.first = 0
        if texto != "":
            return search_results(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def search_results(item):
    logger.info()
    itemlist = list()
    soup = create_soup(item.url)
    for elem in soup.find_all("div", class_="result-item"):
        url = elem.a["href"]
        thumbnail = elem.img["src"]
        title = elem.img["alt"]
        year = elem.find("span", class_="year").text
        new_item = item.clone(url=url, title=title, thumbnail=thumbnail, infoLabels={"year": year})
        if "tvshows" in url:
            new_item.action = "seasons"
            new_item.contentSerieName = title
        else:
            new_item.action = "findvideos"
            new_item.contentTitle = title
        itemlist.append(new_item)
    tmdb.set_infoLabels_itemlist(itemlist, True)
    next_page = soup.find('span', class_='current')
    if next_page:
        next_page = next_page.find_next('a')['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="search_results", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('li', class_='cat-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text
        cantidad = elem.i.text
        plot = ""
        thumbnail = ""
        title = "%s (%s)" %(title, cantidad) 
        itemlist.append(item.clone(action="lista", title=title , url=url, thumbnail=thumbnail, plot=plot) )
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
    if "genre" in item.url:
        matches = soup.find('div', class_='content')
    else:
        matches = soup.find('div', id='archive-content')
    for elem in matches.find_all("article", id=re.compile(r"^post-\d+")):
        id = elem['id'].replace("post-", "")
        url = elem.a['href']
        title = elem.find('h3').text
        if elem.find(src=True):
            thumbnail = elem.img['src']
        else:
            thumbnail = elem.img['data-src']
        year = elem.find('div', class_='data').find_all_next(string=True)[1]
        if year == '':
            year = '-'
        new_item = item.clone(url=url, title=title, thumbnail=thumbnail, infoLabels={"year": year})
        if "tvshows" in url:
            new_item.action = "seasons"
            new_item.contentSerieName = title
        else:
            new_item.action = "findvideos"
            new_item.contentTitle = title
        itemlist.append(new_item)
    tmdb.set_infoLabels(itemlist, True)
    next_page = soup.find('span', class_='current')
    if next_page:   #los generos con menos de 30 pelis no tienen paginacion
        next_page = next_page.find_next_siblings("a")
    if next_page:
        next_page = next_page[0]['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def seasons(item):
    logger.info()
    itemlist = list()
    soup = create_soup(item.url).find("div", id="seasons")
    matches = soup.find_all("div", class_="se-c")
    infoLabels = item.infoLabels
    for elem in matches:
        season = elem.find("span", class_="se-t").text
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(item.clone(title=title, url=item.url, action="episodesxseasons", infoLabels=infoLabels))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(item.clone(title="[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]", url=item.url,
                        action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))
    return itemlist


def episodesxseasons(item):
    logger.info()
    itemlist = list()
    soup = create_soup(item.url).find("div", id="seasons")
    matches = soup.find_all("div", class_="se-c")
    infoLabels = item.infoLabels
    season = infoLabels["season"]
    for elem in matches:
        if elem.find("span", class_="se-t").text != str(season):
            continue
        epi_list = elem.find("ul", class_="episodios")
        for epi in epi_list.find_all("li"):
            info = epi.find("div", class_="episodiotitle")
            url = info.a["href"]
            epi_name = info.a.text
            epi_num = epi.find("div", class_="numerando").text.split(" - ")[1]
            infoLabels["episode"] = epi_num
            title = "%sx%s - %s" % (season, epi_num, epi_name)
            itemlist.append(item.clone(title=title, url=url, action="findvideos", infoLabels=infoLabels))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all("div", id=re.compile(r"^source-player-\d+"))
    for elem in matches:
        try:
            url = elem.iframe['src']
        except:
            url = elem.text
        lang = "CAST"
        if not config.get_setting('unify'):
            title = ' (%s)' % (lang)
        else:
            title = ''
        if url != '' and not "mirrorace" in url: #mirrorrace son descargas con recaptcha
            itemlist.append(item.clone(action="play", title='%s'+title, url=url, language=lang ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para Filtrar enlaces
    if __comprueba_enlaces__:
        itemlist = servertools.check_list_links(itemlist, __comprueba_enlaces_num__)
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra !='findvideos' and not "/episodios/" in item.url :
        itemlist.append(item.clone(action="add_pelicula_to_library", 
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                             extra="findvideos", contentTitle=item.contentTitle)) 
    return itemlist

