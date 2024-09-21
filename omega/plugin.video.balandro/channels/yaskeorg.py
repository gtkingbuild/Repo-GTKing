# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.yaske.org/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<div class="categorias">(.*?)</div>')

    matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)".*?<strong>(.*?)</strong>')

    for url, title in matches:
        title = title.replace('B�lico', 'Bélico').strip()

        if config.get_setting('descartar_xxx', default=False):
            if title == 'Eroticas +18': continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="box-peli">(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('Ver Película', '').replace('Ver Pel�cula', '').replace('Ver Pelcula', '').replace('Ver ', '').replace(' Online', '').strip()

        title = clean_title(title)

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        qlty = scrapertools.find_single_match(match, '<img src=.*?<div class="(.*?)"')

        year = scrapertools.find_single_match(title, '.*?\((\d+)\)$')
        if year: title = title.replace(' (' + year + ')', '').strip()
        else: year = '-'

        titulo = title

        if ' Descarga' in titulo: titulo = titulo.split(" Descarga")[0]
        if ' 4k' in titulo: titulo = titulo.split(" 4k")[0]

        titulo = titulo.replace('�', '').strip()

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, qualities=qlty,
                                    contentType = 'movie', contentTitle = titulo, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="paginacion">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="paginacion">.*?<a href=.*?<span><b>.*?<a href="(.*?)"')

            if next_page:
                if '?page=' in next_page:
                    next_page = host + next_page

                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def clean_title(title):
    logger.info()

    title = title.replace('n�a', 'nua').replace('i�n ', 'ion ').replace('M�t', 'Mat').replace('Tr�', 'Tra').replace('el�', 'eli').replace('i�o', 'iño').strip()
    title = title.replace('P�n', 'Pan').replace('a�a', 'aña').replace('g� ', 'go ').replace('r�n', 'ron').replace('f�r', 'for').replace('am� ', 'ama ').strip()
    title = title.replace(' �l', ' ul').replace('M�s', 'Mas').replace('e�o', 'eño').replace('v�s', 'ves').replace('h�r', 'her').replace(' �c', ' ac').strip()
    title = title.replace('e�o', 'eño').replace('z�n', 'zon').replace('h�s', 'hos').replace('P�l', 'Pal').replace('g�n', 'gon').replace('a�s', 'ais').strip()
    title = title.replace('N�m', 'Nom').replace('m�s', 'mas').replace('�lt', 'Ult').replace('d�a', 'dia').replace('c�p', 'cap').replace('Hu�', 'Hue').strip()
    title = title.replace('�e�a', 'ueña').replace('Qu�', 'Que').replace('e�n', 'eon').replace('f�t', 'fut').replace('c�a', 'cia').replace('m�', 'ma').strip()
    title = title.replace('u�a', 'uña').replace(' �r', ' ar').replace('t�n', 'ton').replace('ll�', 'lla').replace('S�p', 'Sup').replace('i�a', 'iña').strip()
    title = title.replace(' �n', ' un').replace('r�m', 'rim').replace('t�n', 'ton').replace('ll�', 'lla').replace('S�p', 'Sup').replace('i�a', 'iña').strip()
    title = title.replace('t�s', 'tas').replace('ah�', 'ahi').replace('a�o', 'año').replace('o�o', 'oño').replace('i�s', 'ios').replace('as�', 'aso').strip()
    title = title.replace('�as', 'ias').replace('M�g', 'Mag').replace('C�d', 'Cod').replace('p�r', 'pir').replace('H�r', 'Her').replace('k�m', 'kem').strip()
    title = title.replace('u�o', 'uño').replace('c�n', 'con').replace('t�r', 'ter').replace('b�l', 'bel').replace('n�n', 'non').replace('d�n', 'don').strip()
    title = title.replace('d�l', 'dol').replace('l�n', 'lon').replace('a�d', 'aid').replace('p� ', 'po ').replace('o�a', 'oña').replace('s� ', 'si ').strip()
    title = title.replace('m� ', 'mi ').replace('i�n', 'ion').replace('�ra', 'Era').replace('r�s', 'ras').replace('r�a', 'ria').replace('s�n', 'san').strip()
    title = title.replace('i� ', 'io ').replace('s�s', 'sus').replace('t� ', 'ta ').replace('r� ', 're ').replace('�ma', 'Ama').replace('f�n', 'fon').strip()
    title = title.replace('r�c', 'rac').replace('p�a', 'pia').replace('n�g', 'nig')

    title = title.replace(' � ', ' ').replace(' �', ' ').strip()

    return title


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div id="tab_container"(.*?)</div></div>')

    matches = scrapertools.find_multiple_matches(bloque, '<iframe src="(.*?)"')

    ses = 0

    for url in matches:
        ses += 1

        if '.mystream.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        other = servidor

        if servidor == 'various': other = servertools.corregir_other(url)

        if servidor == other: other = ''

        elif not servidor == 'directo':
           if not servidor == 'various': other = ''

        if servidor == 'directo':
            if not config.get_setting('developer_mode', default=False): continue
            other = url.split("/")[2]
            other = other.replace('https:', '').strip()

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Lat', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'buscar/?q=' + texto.replace(" ", "+")
       return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

