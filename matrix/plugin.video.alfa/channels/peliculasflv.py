# -*- coding: utf-8 -*-

import sys, base64
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from channelselector import get_thumb
from channels import autoplay
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
list_servers = ['upstream', 'mixdrop']

canonical = {
             'channel': 'peliculasflv', 
             'host': config.get_setting("current_host", 'peliculasflv', default=''), 
             'host_alt': ["https://www.peliculasflv.io/"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host
__channel__ = canonical['channel']
#__channel__='allcalidad'

encoding = None

try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []
    itemlist.append(Item(channel = item.channel, title = "Novedades", action = "peliculas", url = host + "estrenos", thumbnail = get_thumb("newest", auto = True)))
    itemlist.append(Item(channel = item.channel, title = "Por género", action = "generos", url = host, thumbnail = get_thumb("genres", auto = True) ))
    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel = item.channel, title = "Buscar", action = "search", url = host + "buscar/", thumbnail = get_thumb("search", auto = True)))
    autoplay.show_option(item.channel, itemlist)
    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, encoding=encoding, canonical=canonical).data
    patron  = '(?is)<article>.*?href="([^"]+).*?'
    patron += 'img src="([^"]+).*?'
    patron += '"langs">(.*?)'
    patron += '<div class="year">([^<]+)<.*?'
    patron += '<h2>([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    #, scrapedtitle
    for scrapedurl, scrapedthumbnail, scrapedlanguage, scrapedyear, scrapedtitle in matches:
        item.infoLabels['year'] = scrapertools.find_single_match(scrapedyear, '\d{4}')
        title = scrapedtitle
        itemlist.append(item.clone(channel = item.channel,
                                   action = "findvideos",
                                   contentTitle = scrapedtitle,
                                   thumbnail = scrapedthumbnail,
                                   title = title,
                                   url = scrapedurl
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    url_pagina = scrapertools.find_single_match(data, 'paginator.*?<div><a href="([^"]+)')
    if url_pagina != "":
        pagina = "Pagina: " + scrapertools.find_single_match(url_pagina, "pagina([0-9]+)")
        itemlist.append(Item(channel = item.channel, action = "peliculas", title = pagina, url = url_pagina))
    return itemlist


def findvideos(item):
    itemlist = []
    data = httptools.downloadpage(item.url, encoding=encoding, canonical=canonical).data
    bloques = scrapertools.find_multiple_matches(data, '(?is)<div class="opt">.*?</div>\s*</div>\s*</div>\s*</div>\s*</div>' )
    for scrapedblock in bloques:
        lang = scrapertools.find_single_match(scrapedblock, '"lang-name">([^<]+)')
        matches = scrapertools.find_multiple_matches(scrapedblock, 'data-hash="([^"]+).*?s-name">([^<]+)')
        for scrapedhash, scrapedserver in matches:
            itemlist.append(item.clone(
                            action = "play",
                            language = lang,
                            server = "",
                            title = scrapedserver + " (%s)" %lang,
                            hash = scrapedhash,
                            url = scrapedhash
                        ))

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if itemlist and item.contentChannel != "videolibrary":
        itemlist.append(Item(channel=item.channel))
        itemlist.append(item.clone(channel="trailertools", title="Buscar Tráiler", action="buscartrailer", context="",
                                   text_color="magenta"))

        # Opción "Añadir esta película a la videoteca de KODI"
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir a la videoteca", text_color="green",
                                 action="add_pelicula_to_library", url=item.url, thumbnail = item.thumbnail,
                                 contentTitle = item.contentTitle
                                 ))
    return itemlist
    
    
def play(item):
    logger.info()
    data = httptools.downloadpage(host + "player.php?file=%s" %item.hash).data
    item.url = scrapertools.find_single_match(data, 'iframe src="([^"]+)')
    item.thumbnail = item.contentThumbnail
    itemlist = servertools.get_servers_itemlist([item])
    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria in ['peliculas','latino']:
            item.url = host
        elif categoria == 'infantiles':
            item.url = host + 'category/animacion/'
        elif categoria == 'terror':
            item.url = host + 'category/torror/'
        itemlist = peliculas(item)
        if "Pagina" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    item.extra = "busca"
    if texto != '':
        return peliculas(item)
    else:
        return []


def generos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, encoding=encoding, canonical=canonical).data
    patron  = '(?is)<li>\s*<a href="([^"]+)"'
    patron += '>([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, titulo in matches:
        if not url.startswith("http"): url = host + url
        itemlist.append(Item(channel = item.channel,
                             action = "peliculas",
                             title = titulo,
                             url = url
                             ))
    return itemlist



def clear_url(url):
    if PY3 and isinstance(url, bytes):
        url = "".join(chr(x) for x in bytes(url))
    url = url.replace("fembed.com/v","fembed.com/f").replace("mega.nz/embed/","mega.nz/file/").replace("streamtape.com/e/","streamtape.com/v/").replace("v2.zplayer.live/download","v2.zplayer.live/embed")
    if "streamtape" in url:
        url = scrapertools.find_single_match(url, '(https://streamtape.com/v/\w+)')
    return url


