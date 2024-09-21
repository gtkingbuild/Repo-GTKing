# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://ww2.dipelis.com/'


perpage = 20


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://dipelis.com/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone ( title = 'Más valoradas', action = 'list_all', url = host + 'ver/top-peliculas/' ))

    itemlist.append(item.clone ( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'ver/castellano/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'ver/latino/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'ver/subtituladas/', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Categorías<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?title=".*?">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return sorted(itemlist, key = lambda it: it.title)


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Películas Recién Agregadas<(.*?)</section>')

    if not bloque: bloque = scrapertools.find_single_match(data, '<h1>Películas(.*?)</section>')
    if not bloque: bloque = scrapertools.find_single_match(data, '<h1>Peliculas(.*?)</section>')

    matches = re.compile('<div class="col-mt-5 postsh">(.*?)</div></div>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        title = title.replace('Ver Película', '').replace('Completa', '').strip()

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<div class="ano"> <p>(.*?)</p>')
        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<div class="pagenavi">.*?<span class="current".*?<a href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone (url = next_page, page = 0, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    blk = scrapertools.find_single_match(str(data), "var (.*?)click")

    if not blk: return itemlist

    blk = str(blk).replace('e[', 'e="').replace(']=', '"=')

    hay_https = False
    if 'https://' in str(blk): hay_https = True

    ses = 0

    matches = scrapertools.find_multiple_matches(data, '<li data-id="(.*?)">(.*?)</li>')
    if not matches: matches = scrapertools.find_multiple_matches(data, "<li data-id='(.*?)'>(.*?)</li>")

    for opt, idio in matches:
        ses += 1

        if idio == 'Latino': idio = 'Lat'
        elif idio == 'Castellano' or idio == 'Español': idio = 'Esp'
        elif idio == 'Subtitulado': idio = 'Vose'
        else: idio = '?'

        url = scrapertools.find_single_match(str(blk),  'e="' + str(opt) + '"=' +".*?'(.*?)'")
        if not url: url = scrapertools.find_single_match(str(blk), 'e="' + str(opt) + '"=' + '.*?"(.*?)"')

        avisar = True

        if url:
            if not 'https://' in url:
                srv = ''

                if "|" in url: srv = url.split("|")[1]
                if "|" in url: url = url.split("|")[0]

                if srv:
                    # ~    hay_https  0=filemoon    1=streamwish  2=filemoon  3=streamwish  4=mixdrop     |= ???
                    # ~ NO hay_https  0=streamwish  1=streamwish  2=filemoon  3=streamwish  4=streamwish  |= ???

                    if hay_https:
                        if srv == '0': url = 'https://filemoon.sx/e/' + url
                        elif srv == '1': url = 'https://swdyu.com/e/' + url
                        elif srv == '2': url = 'https://filemoon.sx/e/' + url
                        elif srv == '3': url = 'https://swdyu.com/e/' + url
                        elif srv == '4': url = 'https://mixdrop.ag/e/' + url
                        else: avisar = True
                    else:
                        if srv == '0': url = 'https://swdyu.com/e/' + url
                        elif srv == '1': url = 'https://swdyu.com/e/' + url
                        elif srv == '2': url = 'https://filemoon.sx/e/' + url
                        elif srv == '3': url = 'https://swdyu.com/e/' + url
                        elif srv == '4': url = 'https://swdyu.com/e/' + url
                        else: avisar = True

            if 'https://' in url: avisar = False

            if avisar:
                if config.get_setting('developer_mode', default=False):
                    logger.info("check-1-cplus-opt: %s" % opt)
                    logger.info("check-1-cplus-url: %s" % url)
                    platformtools.dialog_notification(config.__addon_name, '[B][COLOR cyan]Revisar Servers Canal[/COLOR][/B]')
                return

        if url:
            if url.startswith('https://player.ojearanime.com/'): url = url.replace('/player.ojearanime.com/', '/waaw.to/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            link_other = ''
            if servidor == 'various': link_other = servertools.corregir_other(url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, 
                                      language = idio, other = link_other ))

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
