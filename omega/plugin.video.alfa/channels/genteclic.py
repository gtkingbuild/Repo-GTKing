# -*- coding: utf-8 -*-

import sys, base64
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
list_servers = ['fembed', 'streamtape', 'fastplay', 'gvideo', 'netutv', 'Jawcloud']

canonical = {
             'channel': 'genteclic', 
             'host': config.get_setting("current_host", 'genteclic', default=''), 
             'host_alt': ["https://www.genteclic.com"], 
             'host_black_list': [], 
             'pattern': '<div\s*class=.?"jeg_thumb.?">[^<]+<a\s*href=.?"([^"]+)"', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
__channel__= canonical['channel']
forced_proxy_opt = 'ProxyDirect'
encoding = None

try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist = []
    itemlist.append(Item(channel = item.channel, title = "Novedades", action = "peliculas", tipo_action="jnews_module_ajax_jnews_video_block4_view", url = host + "/latest", thumbnail = get_thumb("newest", auto = True)))
    #itemlist.append(Item(channel = item.channel, title = "Por género", action = "generos_years", url = host, extra = "Genero", thumbnail = get_thumb("genres", auto = True) ))
    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel = item.channel, title = "Buscar", action = "search", url = host, thumbnail = get_thumb("search", auto = True)))
    autoplay.show_option(item.channel, itemlist)
    return itemlist

def favorites(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, encoding=encoding, canonical=canonical).data
    patron  = '(?s)short_overlay.*?<a href="([^"]+)'
    patron += '.*?img.*?src="([^"]+)'
    patron += '.*?title="([^"]+).*?'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, thumbnail, titulo in matches:
        idioma = "Latino"
        mtitulo = scrapertools.htmlclean(titulo + " (" + idioma + ")")
        itemlist.append(item.clone(channel = item.channel,
                                   action = "findvideos",
                                   title = mtitulo,
                                   contentTitle = titulo,
                                   thumbnail = thumbnail,
                                   url = url,
                                   contentType="movie",
                                   language = idioma
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    url_pagina = scrapertools.find_single_match(data, 'next" href="([^"]+)')
    if url_pagina != "":
        pagina = "Pagina: " + scrapertools.find_single_match(url_pagina, "page/([0-9]+)")
        itemlist.append(Item(channel = item.channel, action = "peliculas", title = pagina, url = url_pagina))
    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria in ['peliculas','latino']:
            item.url = host + "/latest"
        elif categoria == 'infantiles':
            item.url = host + '/category/animacion/'
        elif categoria == 'terror':
            item.url = host + '/category/torror/'
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
    item.texto = texto.replace(" ", "+")
    item.extra = "busca"
    item.tipo_action = "jnews_ajax_live_search"
    if item.texto != '':
        return peliculas(item)
    else:
        return []


def generos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, encoding=encoding, canonical=canonical).data
    patron = '(?s)%s(.*?)<\/ul>\s*<\/div>' %item.extra
    bloque = scrapertools.find_single_match(data, patron)
    patron  = 'href="([^"]+)'
    patron += '">([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for url, titulo in matches:
        if not url.startswith("http"): url = host + url
        itemlist.append(Item(channel = item.channel,
                             action = "peliculas",
                             title = titulo,
                             url = url
                             ))
    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    if not item.pagina:  item.pagina = 1
    post = {"action":item.tipo_action,
            "module":"true",
            "s":item.texto,
            "data[filter]":"0",
            "data[filter_type]":"all",
            "data[current_page]":item.pagina,
            "data[attribute][data_type]":"custom",
            "data[attribute][video_only]":"yes",
            "data[attribute][number_post]":"12",
            "data[attribute][pagination_number_post]":"12"
            }
            #jnews_module_ajax_jnews_video_block4_view
            #jnews_ajax_live_search
    uuu = "%s?ajax-request=jnews" % host
    headers = {"accept": "text/html, */*; q=0.01",
                "accept-language": "es-ES,es;q=0.9",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "x-requested-with": "XMLHttpRequest"
               }

    if item.tipo_action == "jnews_module_ajax_jnews_video_block4_view":
        data = httptools.downloadpage(uuu, post=post, headers = headers, canonical=canonical).json
        data = data["content"]
    else:
        data = httptools.downloadpage(uuu, post=post, headers = headers, canonical=canonical).data

    patron  = '(?is)jeg_thumb.*?href="([^"]+)"'
    patron += '.*?data-src="([^"]+)"'
    patron += '.*?"jeg_post_title">.*?">([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        quitar = scrapertools.find_single_match(scrapedtitle, '\&\#.*')
        scrapedtitle = scrapedtitle.replace(quitar, "")
        item.infoLabels['year'] = "-"
        itemlist.append(item.clone(channel = item.channel,
                                   action = "findvideos",
                                   title = scrapedtitle,
                                   contentTitle = scrapedtitle,
                                   thumbnail = scrapedthumbnail,
                                   url = scrapedurl,
                                   contentType="movie"
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    if itemlist:
        tpagina = "Pagina: %s" %(item.pagina + 1)
        itemlist.append(Item(channel = item.channel, action = "peliculas", title = tpagina, pagina = item.pagina + 1, tipo_action = item.tipo_action))
    return itemlist


def findvideos(item):
    itemlist = []
    data = httptools.downloadpage(item.url, encoding=encoding, canonical=canonical).data
    matches = scrapertools.find_multiple_matches(data, 'jeg_video_container.*?src="([^"]+)' )
    for url in matches:
        itemlist.append(Item(
                        channel=item.channel,
                        contentTitle=item.contentTitle,
                        contentThumbnail=item.thumbnail,
                        infoLabels=item.infoLabels,
                        language="Latino",
                        title='%s', action="play",
                        url=url
                       ))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
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
    item.thumbnail = item.contentThumbnail
    return [item]
