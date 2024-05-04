# -*- coding: utf-8 -*-

import re

from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channelselector import get_thumb

canonical = {
             'channel': 'cineasiaenlinea', 
             'host': config.get_setting("current_host", 'cineasiaenlinea', default=''), 
             'host_alt': ["https://cineasiaenlinea.com/"], 
             'host_black_list': [], 
             'pattern': '<link\s*rel="stylesheet"\s*type="[^"]+"\s*media="[^"]+"\s*href="([^"]+)"', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
__channel__=canonical['channel']

try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True

# Configuracion del canal
__perfil__ = int(config.get_setting('perfil', 'cineasiaenlinea'))

# Fijar perfil de color            
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]

if __perfil__ - 1 >= 0:
    color1, color2, color3 = perfil[__perfil__ - 1]
else:
    color1 = color2 = color3 = ""


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(action="peliculas", title="Novedades", url=host + "archivos/peliculas",
                               thumbnail=get_thumb('newest', auto=True), text_color=color1,))
    itemlist.append(item.clone(action="peliculas", title="Estrenos", url=host + "archivos/estrenos",
                               thumbnail=get_thumb('premieres', auto=True), text_color=color1))
    itemlist.append(item.clone(action="indices", title="Por Géneros", url=host,
                               thumbnail=get_thumb('genres', auto=True), text_color=color1))
    itemlist.append(item.clone(action="indices", title="Por País", url=host, text_color=color1,
                               thumbnail=get_thumb('country', auto=True)))
    itemlist.append(item.clone(action="indices", title="Por Año", url=host, text_color=color1,
                               thumbnail=get_thumb('year', auto=True)))

    itemlist.append(item.clone(title="", action="", folder=False))
    itemlist.append(item.clone(action="search", title="Buscar...", text_color=color3,
                               thumbnail=get_thumb('search', auto=True)))
    itemlist.append(item.clone(action="configuracion", title="Configurar canal...", text_color="gold", folder=False))

    return itemlist

def get_source(url, patron=None):

    data = httptools.downloadpage(url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|\s{2}|<br />", "", data)
    
    if patron:
        data = scrapertools.find_single_match(data, patron)

    return data

def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()

    item.url = "%s?s=%s" % (host, texto.replace(" ", "+"))

    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host + "archivos/peliculas"
        elif categoria == 'terror':
            item.url = host + "genero/terror"
        item.action = "peliculas"
        itemlist = peliculas(item)

        if itemlist[-1].action == "peliculas":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    item.text_color = color2

    # Descarga la página
    data = get_source(item.url)

    patron = '<h3><a href="([^"]+)">([^<]+)<.*?src="([^"]+)".*?<a rel="tag">(.*?)<' \
             '.*?<a rel="tag">(.*?)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle, scrapedthumbnail, year, calidad in matches:
        title = re.sub(r' \((\d{4})\)$', '', scrapedtitle)
        if calidad:
            scrapedtitle += "  [%s]" % calidad

        infolab = {'year': year or '-'}
        itemlist.append(item.clone(action="findvideos", title=scrapedtitle, url=scrapedurl,
                                   thumbnail=scrapedthumbnail, infoLabels=infolab,
                                   contentTitle=title, contentType="movie", quality=calidad))

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)"')
    if next_page:
        itemlist.append(item.clone(title=">> Página Siguiente", url=next_page))

    return itemlist


def indices(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = get_source(item.url)

    if "géneros" in item.title:
        bloque = scrapertools.find_single_match(data, '(?i)<h4>Peliculas por genero</h4>(.*?)</ul>')
        matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?>([^<]+)<')
    elif "año" in item.title:
        bloque = scrapertools.find_single_match(data, '(?i)<h4>Peliculas por Año</h4>(.*?)</select>')
        matches = scrapertools.find_multiple_matches(bloque, '<option value="([^"]+)">([^<]+)<')
    else:
        bloque = scrapertools.find_single_match(data, '(?i)<h4>Peliculas por Pais</h4>(.*?)</ul>')
        matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?>([^<]+)<')

    for scrapedurl, scrapedtitle in matches:
        if "año" in item.title:
            scrapedurl = "%sfecha-estreno/%s" % (host, scrapedurl)
        itemlist.append(Item(channel=item.channel, action="peliculas", title=scrapedtitle, url=scrapedurl,
                             thumbnail=item.thumbnail, text_color=color3))

    return itemlist


def findvideos(item):
    logger.info()
    data = get_source(item.url)
    if not item.infoLabels["plot"]:
        plot = scrapertools.find_single_match(data, '(?i)<h2>SINOPSIS.*?<p>(.*?)</p>')
        item.infoLabels["plot"] = scrapertools.decodeHtmlentities(plot)
    #item.infoLabels["trailer"] = scrapertools.find_single_match(data, 'src="(http://www.youtube.com/embed/[^"]+)"')

    itemlist = servertools.find_video_items(item=item, data=data)
    for it in itemlist:

        it.title = it.server.capitalize()
        if item.quality:
            it.title += ' [%s]' % item.quality
        if it.server == 'youtube':
            it.title = 'Ver Trailer'
        it.thumbnail = item.thumbnail
        it.text_color = color2
    
    '''if item.infoLabels["trailer"]:
        folder = True
        if config.is_xbmc():
            folder = False
        itemlist.append(item.clone(channel="trailertools", action="buscartrailer", title="Ver Trailer", folder=folder,
                                   contextual=not folder))'''

    if len(itemlist) and config.get_videolibrary_support():
        itemlist.append(item.clone(action="add_pelicula_to_library", title="Añadir película a la videoteca"))

    return itemlist
