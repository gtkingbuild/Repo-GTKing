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
list_servers = ['fembed', 'streamtape', 'gvideo', 'Jawcloud']

canonical = {
             'channel': 'allcalidad', 
             'host': config.get_setting("current_host", 'allcalidad', default=''), 
             'host_alt': ["https://allcalidad.ms"], 
             'host_black_list': ["https://allcalidad.si", 
                                 "https://ww3.allcalidad.is", "https://allcalidad.is", "https://allcalidad.ac"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
__channel__ = canonical['channel']

forced_proxy_opt = 'ProxyDirect'
encoding = "utf-8"

try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


def mainlist(item):
    logger.info()
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist = []
    
    itemlist.append(Item(channel = item.channel, title = "Novedades", action = "peliculas", url = host, thumbnail = get_thumb("newest", auto = True)))
    itemlist.append(Item(channel = item.channel, title = "Por género", action = "generos_years", url = host, extra = "Genero", thumbnail = get_thumb("genres", auto = True) ))
    itemlist.append(Item(channel = item.channel, title = "Por año", action = "generos_years", url = host, extra = ">Año<", thumbnail = get_thumb("year", auto = True)))
    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel = item.channel, title = "Buscar", action = "search", url = host, thumbnail = get_thumb("search", auto = True)))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def newest(categoria):
    logger.info()
    
    itemlist = []
    item = Item()
    
    try:
        if categoria in ['peliculas','latino']:
            item.url = host
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
    
    texto = texto.replace(" ", "+")
    item.url = host + "/?s=" + texto
    item.extra = "busca"
    if texto != '':
        return peliculas(item)
    else:
        return []


def generos_years(item):
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
    return itemlist[::-1]


def peliculas(item):
    logger.info()
    
    itemlist = []
    
    data = httptools.downloadpage(item.url, encoding=encoding, canonical=canonical).data
    matches = scrapertools.find_multiple_matches(data, '(?s)shortstory cf(.*?)(?:rate_post|ratebox)')
    
    for datos in matches:
        url = scrapertools.find_single_match(datos, 'href="([^"]+)')
        titulo = scrapertools.htmlclean(scrapertools.find_single_match(datos, 'short_header">([^<]+)').strip())
        if "Premium" in titulo or "Suscripci" in titulo:
            continue
        datapostid = scrapertools.find_single_match(datos, 'data-postid="([^"]+)')
        thumbnail = scrapertools.find_single_match(datos, 'data-src="([^"]+)')
        post = 'action=get_movie_details&postID=%s' %datapostid
        idioma = "Latino"
        mtitulo = titulo + " (" + idioma + ")"
        item.infoLabels['year'] = "-"
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
    
    url_pagina = scrapertools.find_single_match(data, 'next page-numbers" href="([^"]+)')
    if url_pagina != "":
        pagina = "Pagina: " + scrapertools.find_single_match(url_pagina, "page/([0-9]+)")
        itemlist.append(Item(channel = item.channel, action = "peliculas", title = pagina, url = url_pagina))
    
    return itemlist


def findvideos(item):
    logger.info()
    
    itemlist = []
    encontrado = []
    
    data = httptools.downloadpage(item.url, encoding=encoding, forced_proxy_opt=forced_proxy_opt, canonical=canonical).data
    matches = scrapertools.find_multiple_matches(data, 'data-id="([^"]+)"')
    
    for url in matches:
        url1 = base64.b64decode(url)
        url1 = clear_url(url1)
        if url1 in encontrado or "youtube.com" in url1 or "search" in url1 or 'salaload.com' in url1 or not "//" in url1:
            continue
        if not url1.startswith("http"): url1 = "http://" + url1
        if "hackplayer.org" in url1:
            id = scrapertools.find_single_match(url1, "id=(\w+)")
            token = scrapertools.find_single_match(url1, "token=(\w+)")
            post = {"id" : id, "token" : token}
            dd = httptools.downloadpage("https://hackplayer.org/r.php", post = post, allow_redirect=False).url
            v = scrapertools.find_single_match(dd, "t=(\w+)")
            dd = httptools.downloadpage("https://cinestart.net/vr.php?v=%s" %v).json
            url1 = dd["file"]
        encontrado.append(url1)
        itemlist.append(Item(
                        channel=item.channel,
                        contentTitle=item.contentTitle,
                        contentThumbnail=item.thumbnail,
                        infoLabels=item.infoLabels,
                        language="Latino",
                        title='%s', action="play",
                        url=url1
                       ))

    
    patron = '<a href="([^"]+)" class="bits-download btn btn-xs.*?<span>([^<]+)</span>'
    matches = scrapertools.find_multiple_matches(data, patron)
    
    for url, srv in matches:
        if '#aHR0' in url:
            b_url = scrapertools.find_single_match(url, '(aHR0.*)')
            try:
                url = base64.b64decode(b_url)
            except:
                continue
        url = clear_url(url)
        if url in encontrado or ".srt" in url or "search" in url or "acortalink" in url:
            continue
        if url:
            encontrado.append(url)
            new_item= Item(channel=item.channel, url=url, title='%s', action="play", contentTitle=item.contentTitle,
                           contentThumbnail=item.thumbnail, infoLabels=item.infoLabels, language="Latino")
            if "torrent" in srv.lower():
                new_item.server = "Torrent"
            itemlist.append(new_item)
    
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


def clear_url(url):
    
    if PY3 and isinstance(url, bytes):
        url = "".join(chr(x) for x in bytes(url))
    url = url.replace("fembed.com/v","fembed.com/f").replace("mega.nz/embed/","mega.nz/file/").replace("streamtape.com/e/","streamtape.com/v/").replace("v2.zplayer.live/download","v2.zplayer.live/embed")
    if "streamtape" in url:
        url = scrapertools.find_single_match(url, '(https://streamtape.com/v/\w+)')
    
    return url


def play(item):
    
    item.thumbnail = item.contentThumbnail
    
    return [item]
