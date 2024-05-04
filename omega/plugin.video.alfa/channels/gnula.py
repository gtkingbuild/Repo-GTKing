# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channelselector import get_thumb

canonical = {
             'channel': 'gnula', 
             'host': config.get_setting("current_host", 'gnula', default=''), 
             'host_alt': ["https://gnula.nu/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'CF_stat': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_search = "https://cse.google.com/cse/element/v1?rsz=filtered_cse&num=20&hl=es&source=gcsc&gss=.es&sig=c891f6315aacc94dc79953d1f142739e&cx=014793692610101313036:vwtjajbclpq&q=%s&safe=off&cse_tok=%s&googlehost=www.google.com&callback=google.search.Search.csqr6098&nocache=1540313852177&start=0"
item_per_page = 20


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Estrenos", action="peliculas",
                         url= host +"peliculas-de-estreno/lista-de-peliculas-online-parte-1/", viewmode="movie",
                         thumbnail=get_thumb('premieres', auto=True), first=0))
    itemlist.append(
        Item(channel=item.channel, title="Generos", action="generos", url= host + "generos/lista-de-generos/",
             thumbnail=get_thumb('genres', auto=True),))
    itemlist.append(Item(channel=item.channel, title="Recomendadas", action="peliculas",
                         url= host + "peliculas/lista-de-peliculas-recomendadas/", viewmode="movie",
                         thumbnail=get_thumb('recomended', auto=True), first=0))
    itemlist.append(Item(channel = item.channel, action = ""))
    itemlist.append(
        Item(channel=item.channel, title="Buscar", action="search", url = host_search,
             thumbnail=get_thumb('search', auto=True),))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    data = httptools.downloadpage(host, canonical=canonical).data
    cxv = scrapertools.find_single_match(data, 'cx" value="([^"]+)"')
    data = httptools.downloadpage("https://cse.google.es/cse.js?hpg=1&cx=%s" %cxv).data
    if PY3 and isinstance(data, bytes):
        data = "".join(chr(x) for x in bytes(data))
    cse_token = scrapertools.find_single_match(data, 'cse_token": "([^"]+)"')
    if cse_token:                                       #Evita un loop si error
        item.url = host_search %(texto, cse_token)
        try:
            return sub_search(item)
        # Se captura la excepción, para no interrumpir al buscador global si un canal falla
        except:
            import sys
            for line in sys.exc_info():
                logger.error("%s" % line)
    return []


def sub_search(item):
    logger.info()
    itemlist = []
    while True:
        response = httptools.downloadpage(item.url)
        data = response.data
        if PY3 and isinstance(data, bytes):
            data = "".join(chr(x) for x in bytes(data))
        if len(data) < 500 or not response.sucess:      #Evita un loop si error
            break

        page = int(scrapertools.find_single_match(item.url, ".*?start=(\d+)")) + item_per_page
        item.url = scrapertools.find_single_match(item.url, "(.*?start=)") + str(page)
        patron =  '(?s)clicktrackUrl":\s*".*?q=(.*?)".*?'
        patron += 'titleNoFormatting":\s*"([^"]+)".*?'
        patron += 'cseThumbnail.*?"src":\s*"([^"]+)"' # se usa el thumb de google
        matches = scrapertools.find_multiple_matches(data, patron)
        for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
            scrapedurl = scrapertools.find_single_match(scrapedurl, ".*?online/")
            scrapedtitle = scrapedtitle.replace(" online", "").replace("<b>", "").replace("</b>", "")
            if "ver-" not in scrapedurl:
                continue
            year = scrapertools.find_single_match(scrapedtitle, "\d{4}")
            contentTitle = scrapedtitle.replace(scrapertools.find_single_match('\[.+', scrapedtitle),"")
            contentTitle = scrapedtitle.replace("(%s)" %year,"").replace("Ver","").strip()
            itemlist.append(Item(action = "findvideos",
                                 channel = item.channel,
                                 contentTitle = contentTitle,
                                 infoLabels = {"year":year},
                                 title = scrapedtitle,
                                 thumbnail = scrapedthumbnail,
                                 url = scrapedurl,
                                 ))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = scrapertools.find_single_match(data, '<spa[^>]+>Lista de g(.*?)/table')
    patron = '<strong>([^<]+)</strong> .<a href="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for genero, scrapedurl in matches:
        title = scrapertools.htmlclean(genero)
        if not item.url.startswith("http"): scrapedurl = item.url + scrapedurl
        itemlist.append(Item(channel = item.channel,
                             action = 'peliculas',
                             title = title,
                             url = scrapedurl,
                             viewmode = "movie",
                             first=0))
    itemlist = sorted(itemlist, key=lambda item: item.title)
    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    next = True
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = '<a class="Ntooltip" href="([^"]+)">([^<]+)<span><br[^<]+'
    patron += '<img src="([^"]+)"></span></a>(.*?)<br'
    matches = scrapertools.find_multiple_matches(data, patron)
    first = item.first
    last = first + 19
    if last > len(matches):
        last = len(matches)
        next = False

    for scrapedurl, scrapedtitle, scrapedthumbnail, resto in matches[first:last]:
        language = []
        plot = scrapertools.htmlclean(resto).strip()
        languages = scrapertools.find_multiple_matches(plot, r'\((V.)\)')
        quality = scrapertools.find_single_match(plot, r'(?:\[.*?\].*?)\[(.*?)\]')
        for lang in languages:
            language.append(lang)
        title = scrapedtitle + " " + plot
        if not scrapedurl.startswith("http"):
            scrapedurl = item.url + scrapedurl
        year = scrapertools.find_single_match(scrapedurl, "\-(\d{4})\-")
        contentTitle = scrapedtitle.replace(scrapertools.find_single_match('\[.+', scrapedtitle),"")
        itemlist.append(Item(action = 'findvideos',
                             channel = item.channel,
                             contentTitle = scrapedtitle,
                             infoLabels = {"year":year},
                             language=language,
                             plot = plot,
                             quality=quality,
                             title = title,
                             thumbnail = scrapedthumbnail,
                             url = scrapedurl
                             ))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    #paginacion
    url_next_page = item.url
    first = last
    if next:
        itemlist.append(item.clone(title="Siguiente >>", url=url_next_page, action='peliculas', first=first))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, ignore_response_code=True, canonical=canonical).data
    #item.plot = scrapertools.find_single_match(data, '<div class="entry">(.*?)<div class="iframes">')
    #item.plot = scrapertools.htmlclean(item.plot).strip()
    #item.contentPlot = item.plot
    patron = '<strong>Ver película online.*?>.*?>([^<]+)'
    scrapedopcion = scrapertools.find_single_match(data, patron)
    titulo_opcional = scrapertools.find_single_match(scrapedopcion, ".*?, (.*)").upper()
    bloque  = scrapertools.find_multiple_matches(data, 'contenedor_tab.*?/table')
    cuenta = 0
    for datos in bloque:
        cuenta = cuenta + 1
        patron = '<em>((?:opciÃ³n|opción) %s.*?)</em>' %cuenta
        scrapedopcion = scrapertools.find_single_match(data, patron)
        titulo_opcion = "(" + scrapertools.find_single_match(scrapedopcion, "op.*?, (.*)").upper() + ")"
        if "TRAILER" in titulo_opcion or titulo_opcion == "()":
            titulo_opcion = "(" + titulo_opcional + ")"
        urls = scrapertools.find_multiple_matches(datos, '(?:src|href)="([^"]+)')
        titulo = "Ver en %s " + titulo_opcion
        for url in urls:
            if "soon" in url:  continue
            itemlist.append(item.clone(action = "play",
                                 title = titulo,
                                 url = url
                                 ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    #tmdb.set_infoLabels_itemlist(itemlist, True)
    if itemlist:
        if config.get_videolibrary_support():
                itemlist.append(Item(channel = item.channel, action = ""))
                itemlist.append(Item(channel=item.channel, title="Añadir a la videoteca", text_color="green",
                                     action="add_pelicula_to_library", url=item.url, thumbnail = item.thumbnail,
                                     contentTitle = item.contentTitle
                                     ))
    return itemlist


def play(item):
    item.thumbnail = item.contentThumbnail
    return [item]
