# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seireshd.com/'


def do_downloadpage(url, post=None, headers=None):
    if not headers: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'category/estreno/', search_type = 'movie', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
 
    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '>Categorías<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == 'Estreno': continue

        if config.get_setting('descartar_xxx', default=False):
            if title == 'Eroticas (+18': continue

        title = title.replace('Eroticas (+18</span>', 'Eroticas (+18)')

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '</h3>(.*?)</section>')
    if not bloque: bloque = scrapertools.find_single_match(data, '</h1>(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="col-mt-5 postsh">(.*?)</div></div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        title = title.replace('&#8217;', "'").replace('&#8211;', '').replace('&#8230;', '').strip()

        year = '-'

        if ' (' in title:
            year = title.split(' (')[1]
            year = year.split(')')[0]
        elif '(' in title:
            year = title.split('(')[1]
            year = year.split(')')[0]

        if not year == '-':
            if ' (' in title: title = title.replace(' (' + year + ')', '').strip()
            elif '(' in title: title = title.replace('(' + year + ')', '').strip()

        PeliName = title

        if '+18 ' in PeliName: PeliName = PeliName.replace('+18 ', '').strip()

        if ' Latino' in PeliName: PeliName = PeliName.split(' Latino')[0]
        if ' Castellano' in PeliName: PeliName = PeliName.split(' Castellano')[0]
        if ' Ingles' in PeliName: PeliName = PeliName.split(' Ingles')[0]
        if ' Subtitulada' in PeliName: PeliName = PeliName.split(' Subtitulada')[0]
        if ' Subtitulado' in PeliName: PeliName = PeliName.split(' Subtitulado')[0]
        if ' Español' in PeliName: PeliName = PeliName.split(' Español')[0]

        if ' Dual ' in PeliName: PeliName = PeliName.split(' Dual ')[0]
        if ' 1080p' in PeliName: PeliName = PeliName.split(' 1080p')[0]
        if ' 720p' in PeliName: PeliName = PeliName.split(' 720p')[0]

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                            contentType = 'movie', contentTitle = PeliName, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<span class="current">' in data:
            next_page = scrapertools.find_single_match(data, '<span class="current">.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    info = scrapertools.find_single_match(data, '>Ficha Técnica<(.*?)>Servidores:<')

    idioma = scrapertools.find_single_match(info, '<b>Audio:</b>(.*?)<b>')

    if 'Latino' in idioma: lang = 'Lat'
    elif 'Subtitulado' in idioma: lang = 'Vose'
    elif 'Subtitulada' in idioma: lang = 'Vose'
    elif 'Ingles' in idioma: lang = 'Vo'
    elif 'Castellano' in idioma: lang = 'Esp'
    elif 'Español' in idioma : lang = 'Esp'
    else: lang  = '?'

    ses = 0

    if '<div class="tab-content">' in data:
        bloque = scrapertools.find_single_match(data, '<div class="tab-content">(.*?)</center>')

        downs = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)"')

        for down in downs:
            ses += 1

            if down.startswith('https://vip.'): continue

            data1 = httptools.downloadpage(down).data

            data1 = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data1)
            bloque1 = scrapertools.find_single_match(data1, '<div class="tab_container">(.*?)<li>')

            links = scrapertools.find_multiple_matches(bloque1, 'href="(.*?)"')

            for link in links:
                url = link

                if '/powvideo.' in url: continue
                elif '/streamplay.' in url: continue

                elif '/1fichier.' in url: continue
                elif '/www.fireload.' in url: continue
                elif '/terabox.' in url: continue
                elif '/t.me' in url: continue
                elif '/zb4vh-' in url: continue

                if url.startswith('https://mega.nz/folder/'): continue

                other = ''

                if '<a target=' in url: url = url.replace('<a target=', '').strip()

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                if servidor == 'various': other = servertools.corregir_other(url)

                if url.startswith('https://mega.nz/file/'):
                     _url1 = scrapertools.find_single_match(url, '/file/(.*?)#')

                     if _url1:
                         _url2 = scrapertools.find_single_match(url, '#(.*?)$')

                         if _url2:
                             url = 'https://mega.nz/#!' + _url1 + '!' + _url2

                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<p class="num-resultados">(.*?)</section>')

    matches = re.compile('<div class="col-xs-2">(.*?)</div></div>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        title = title.replace('&#8217;', "'").replace('&#8211;', '').replace('&#8230;', '').strip()

        year = '-'

        if ' (' in title:
            year = title.split(' (')[1]
            year = year.split(')')[0]
        elif '(' in title:
            year = title.split('(')[1]
            year = year.split(')')[0]

        if not year == '-':
            if ' (' in title: title = title.replace(' (' + year + ')', '').strip()
            elif '(' in title: title = title.replace('(' + year + ')', '').strip()

        PeliName = title

        if '+18 ' in PeliName: PeliName = PeliName.replace('+18 ', '').strip()

        if ' Latino' in PeliName: PeliName = PeliName.split(' Latino')[0]
        if ' Castellano' in PeliName: PeliName = PeliName.split(' Castellano')[0]
        if ' Ingles' in PeliName: PeliName = PeliName.split(' Ingles')[0]
        if ' Subtitulada' in PeliName: PeliName = PeliName.split(' Subtitulada')[0]
        if ' Subtitulado' in PeliName: PeliName = PeliName.split(' Subtitulado')[0]
        if ' Español' in PeliName: PeliName = PeliName.split(' Español')[0]

        if ' Dual ' in PeliName: PeliName = PeliName.split(' Dual ')[0]
        if ' 1080p' in PeliName: PeliName = PeliName.split(' 1080p')[0]
        if ' 720p' in PeliName: PeliName = PeliName.split(' 720p')[0]

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=PeliName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<span class="current">' in data:
            next_page = scrapertools.find_single_match(data, '<span class="current">.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_search', url = next_page, text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
