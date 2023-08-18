# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://www.mundodesconocido.es/'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'category/blog/videoprogramas/' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    cats = []

    data = httptools.downloadpage(host).data

    matches = scrapertools.find_multiple_matches(data, '/category/blog/(.*?)/')

    for url in matches:
        if '/page/' in url: continue

        title = url.capitalize()
        title = title.replace('-blog', '').replace('-', '')

        if title == 'Altosecreto': title = 'Alto secreto'
        elif title == 'Amosenlasombra': title = 'Amos en la sombra'
        elif title == 'Elsecreto': title = 'El secreto'
        elif title == 'Grandesincertidumbres': title = 'Grandes incertidumbres'
        elif title == 'Humanosbajocontrol': title = 'Humanos bajo control'
        elif title == 'Lagranjahumana': title = 'La granja humana'
        elif title == 'Laluna': title = 'La luna'
        elif title == 'Lamatriz': title = 'La matriz'
        elif title == 'Mensajesocultosenlogos': title = 'Mensajes ocultos en logos'
        elif title == 'Nadaesloqueparece': title = 'Nada es lo que parece'
        elif title == 'Ordenimpuesto': title = 'Orden impuesto'
        elif title == 'Reptileseneleden': title = 'Reptiles en el eden'
        elif title == 'Rutasmagicas': title = 'Rutas magicas'
        elif title == 'Saludhumana': title = 'Salud humana'
        elif title == 'Videoprogramas': title = 'Video programas'

        if title in str(cats): continue

        url = host + '/category/blog/' + url + '/'

        cats.append(title)

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'cyan' ))

    return sorted(itemlist, key=lambda i: i.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'by: <a href=.*?data-a2a-url="(.*?)".*?data-a2a-title="(.*?)".*?src="(.*?)"')

    for url, title, thumb in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType='movie', contentTitle=title, contentExtra='documentary' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'class="page-numbers current">.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, '<iframe  id=".*?src="(.*?)"')

    if url:
        servidor = servertools.get_server_from_url(url)

        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = '', url = url, language = 'Esp' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
