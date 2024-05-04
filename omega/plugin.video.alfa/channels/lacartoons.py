# -*- coding: utf-8 -*-
# -*- Channel lacartoons -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys, re
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from channelselector import get_thumb
from modules import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger


IDIOMAS = {'Latino': 'Latino'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['okru']

canonical = {
             'channel': 'lacartoons', 
             'host': config.get_setting("current_host", 'lacartoons', default=''), 
             'host_alt': ["http://www.lacartoons.com/"], 
             'host_black_list': [], 
             'status': 'SIN CANONICAL', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host
__channel__ = canonical['channel']


try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []
    itemlist.append(Item(channel = item.channel, title = "Novedades", action = "lista", url = host, page = 1, thumbnail = get_thumb("newest", auto = True)))
    itemlist.append(Item(channel = item.channel, title = "Categorias", action = "categorias", url = host, thumbnail = get_thumb("categories", auto = True) ))
    itemlist.append(Item(channel = item.channel, title = "Buscar", action = "search", url = host + "?Titulo=", thumbnail = get_thumb("search", auto = True)))
    autoplay.show_option(item.channel, itemlist)
    return itemlist
    
   
def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    bloque = scrapertools.find_single_match(data, 'botontes-categorias.*?</ul>')
    patron  = 'submit" value="([^"]+).*?'
    patron += 'value="([^"]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for title, id in matches:
        itemlist.append(Item(channel = item.channel,
                             action = "lista",
                             page = 0,
                             title = title,
                             url = host + "?Categoria_id=" + id
                        ))
    return itemlist

    
def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = 'a href="(/serie[^"]+).*?'
    patron += 'src="([^"]+).*?'
    patron += 'nombre-serie">([^<"]+).*?'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, thumbnail, title in matches:
        itemlist.append(item.clone(action = "seasons",
                             contentSerieName = title,
                             thumbnail = host + thumbnail,
                             title = title,
                             url = host + url
                        ))
    tmdb.set_infoLabels(itemlist)
    
    page = item.page + 1
    page_url = re.sub(r'page=\d+', 'page=%s' % page, item.url)
    if page == 2:
        page_url = "%s?page=%s" %(item.url, page)
    
    if not item.extra:
        thumbnail += '|verifypeer=false'
        itemlist.append(Item(channel = item.channel,
                                action = "lista",
                                contentSerieName = title,
                                page = page,
                                thumbnail = host + thumbnail,
                                title = "Pagina: %s" % page,
                                url = page_url
                    ))
    return itemlist


def seasons(item):
    logger.info()
    itemlist = []
    infoLabels = item.infoLabels
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = 'fa fa-chevron-right"></span> (.*?)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for title in matches:
        season = scrapertools.find_single_match(title, " (\w+)")
        infoLabels["season"] = season
        itemlist.append(item.clone(action = "episodesxseasons",
                                   infoLabels = infoLabels,
                                   title = title.strip()
                                   ))
    tmdb.set_infoLabels(itemlist)
    itemlist.append(Item())
    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'episodios':
        itemlist.append(
                Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                     action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)

    return itemlist


def episodesxseasons(item):
    logger.info()
    itemlist = []
    infoLabels = item.infoLabels
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = '%s.*?</ul>' %item.title
    bloque = scrapertools.find_single_match(data, patron)
    patron  = 'href="([^"]+).*?'
    patron += 'span>(.*?)</a>.*?'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for url, title in matches:
        title = title.replace("</span>","")
        episode = scrapertools.find_single_match(title, " (\w+)")
        title = title.replace("Capitulo ", str(item.infoLabels["season"])+"x")
        infoLabels["episode"] = episode
        itemlist.append(item.clone(action = "findvideos",
                                   infoLabels = infoLabels,
                                   title = title.strip(),
                                   url = host + url
                                   ))
    tmdb.set_infoLabels(itemlist)
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    item.extra = "busca"
    item.page = 0
    if texto != '':
        return lista(item)
    else:
        return []


def findvideos(item):
    logger.info()
    itemlist = []
    infoLabels = item.infoLabels
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = '<iframe src="([^"]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        itemlist.append(item.clone(action = "play",
                                   infoLabels = infoLabels,
                                   title = "Ver en %s",
                                   url = url
                                   ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    tmdb.set_infoLabels(itemlist, __modo_grafico__)
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)
    if itemlist and item.contentChannel != "videolibrary":
        itemlist.append(Item(channel = item.channel))
        # Opción "Añadir esta película a la biblioteca de KODI"
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir a la videoteca", text_color="green",
                                 action="add_pelicula_to_library", url=item.url, thumbnail = item.thumbnail,
                                 contentTitle = item.contentTitle
                                 ))
    return itemlist


def play(item):
    item.thumbnail = item.contentThumbnail
    return [item]
