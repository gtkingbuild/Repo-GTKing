# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://www.area-documental.com/'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'resultados-reciente.php?buscar=&genero=' ))

    itemlist.append(item.clone( title = 'Destacados', action = 'list_all', url = host + 'resultados.php?buscar=&genero=' ))
    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host +'resultados-visto.php?buscar=&genero=' ))

    itemlist.append(item.clone( title = 'En 3D', action = 'list_all', url = host + '3D.php' ))

    itemlist.append(item.clone( title = 'Series', action = 'list_all', url = host + 'series.php', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Por fecha', action = 'list_all', url = host + 'resultados-anio.php?buscar=&genero=' ))
    itemlist.append(item.clone( title = 'Por alfabético', action = 'list_all', url = host +'resultados-titulo.php?buscar=&genero=' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    block = scrapertools.find_single_match(data, '<ul class="nav navbar-nav">(.*?)</nav>')

    matches = scrapertools.find_multiple_matches(block, '<a href="(.*?)" class="dropdown-toggle" data-toggle="dropdown">(.*?)<b')

    for url, title in matches:
        title = title.strip()

        if title == 'Navegación': continue

        patron = 'data-toggle="dropdown">%s.*?<b(.*?)</ul>' % title

        bloque = scrapertools.find_single_match(data, patron)

        subcats = scrapertools.find_multiple_matches(bloque, '<li><a href=".*?>(.*?)</a>')

        url = host[:-1] + url

        itemlist.append(item.clone( action='subcategorias', title = title, url = host + url, subcats = subcats, plot=', '.join(subcats), text_color='cyan' ))

    return sorted(itemlist,key=lambda x: x.title)


def subcategorias(item):
    logger.info()
    itemlist = []

    if item.subcats:
        itemlist.append(item.clone( action='list_all', title='Todo ' + item.title, url=item.url ))

    for subcat in item.subcats:
        if subcat == 'TODO': continue

        itemlist.append(item.clone( action = 'list_all', title = subcat, url = host + 'resultados.php?genero=&buscar=' + subcat.replace(' ', '+') ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<a class="hvr-shutter-out-horizontal" href="([^"]+)"><img (?:data-|)src="([^"]+)" alt="([^"]+)"'
    patron += '.*?&nbsp;&nbsp;&nbsp;(\d+| ).*?<div class="comments-space">(.*?)</div>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, year, plot in matches:
        thumb = host + thumb
        plot = scrapertools.htmlclean(plot).strip()

        if not year: year = '-'

        if 'player.php' not in url:
            titulo = '%s [COLOR gray](%s)[/COLOR]' % (title, year)
            itemlist.append(item.clone( action='list_all', url = url, title = titulo, thumbnail=thumb, infoLabels={"year": year, "plot": plot} ))
        else:
            itemlist.append(item.clone( action='findvideos', url= host + url, title = title, thumbnail = thumb,
                                        infoLabels={"year": year, "plot": plot}, contentType='movie', contentTitle=title, contentExtra='documentary' ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
         next_page = scrapertools.find_single_match(data, '<li><a class="last">.*?<a href="([^"]+)')

         if next_page:
             next_page = next_page.replace('&amp;', '&')

             if '?page=' in next_page or '/pagina/' in next_page:
                 itemlist.append(item.clone( title='Siguientes ...', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'file:\s*"([^"]+)",.*?label: "([^"]*)"')

    ses = 0

    for url, lbl in matches:
        ses += 1

        php = False

        if '.mp4' not in url:
            if 'video.php' in url: pass 
            elif 'videoHD.php' in url: pass
            elif 'video3Dfull.php' in url: pass
            else: continue

            php = True

        if php:
            url = url + '|Referer=' + item.url 
            url += '&Cookie=' + httptools.get_cookies('www.area-documental.com')

        sub_url = scrapertools.find_single_match(data, 'file:\s*"/(webvtt/[^"]+)"')

        lang = 'Vose'
        if 'videoHD.php' in url:
            sub_url = sub_url.replace('spa', 'eng')
            lang = 'VO'

        sub_url = host + sub_url + '|Referer=' + item.url

        itemlist.append(Item( channel = item.channel, action = 'play', server='directo', title = '', url = url, language = lang, quality = lbl, subtitle = sub_url ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'resultados.php?genero=&buscar=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
