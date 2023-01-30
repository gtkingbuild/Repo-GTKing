# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://descargasnsn.to/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'productora', search_type = 'movie' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'tag/castellano/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'tag/latino/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'tag/subtitulado/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    genres = [
       'accion',
       'animacion',
       'aventura',
       'belica',
       'ciencia-ficcion',
       'comedia',
       'crimen',
       'familia',
       'fantasia',
       'historia',
       'kids',
       'misterio',
       'musica',
       'romance',
       'suspense',
       'terror'
       ]

    for genero in genres:
        url = host + 'peliculas/' + genero + '/'

        itemlist.append(item.clone( action = 'list_all', title = genero.capitalize(), url = url ))

    return itemlist


def productora(item):
    logger.info()
    itemlist = []

    producers = [
        ['abc', 'ABC'],
        ['amazon-studios', 'Amazon Studios'],
        ['apple-tv', 'Apple TV+'],
        ['cbs', 'CBS'],
        ['disney', 'Disney+'],
        ['fox', 'FOX'],
        ['midnight-radio', 'Midnight Radio'],
        ['netflix', 'Netflix'],
        ['new-republic-pictures', 'New Republic Pictures'],
        ['outlier-society-productions', 'Otlier Society Productions'],
        ['paramount', 'Paramount'],
        ['skydance-media', 'Sky Dance Media'],
        ['weed-road-pictures', 'Weed Road Pictures']
        ]

    url = host + 'canal/'

    for x in producers:
        itemlist.append(item.clone( title = x[1], url = url + str(x[0]) + '/', action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        tipo = scrapertools.find_single_match(match, '<span class="rounded p-1">(.*?)</span>').strip()
        if not 'Peliculas' in tipo: continue

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        title = title.replace('Temporada', '[COLOR hotpink](Serie)[/COLOR] Temporada').strip()

        title = title.replace('Castellano-Latino', '').replace('Castellano-Latino', '').replace('Castellano-Inglés', '').replace('Latino-Inglés', '')
        title = title.replace('Castellano', '').replace('castellano', '').replace('Español', '').replace('español', '')
        title = title.replace('Latino', '').replace('latino', '')
        title = title.replace('Subtitulado', '').replace('subtitulado', '').replace('Subtitulos', '').replace('subtitulos', '')
        title = title.replace('Inglés', '').replace('inglés', '')

        title = title.replace('Descargar', '').replace('descargar', '').strip()

        thumb = scrapertools.find_single_match(match, 'style="background-image: url(.*?)"')
        thumb = thumb.replace('(', '').replace(')', '').strip()

        qltys = []

        if '2160p 4k uhd' in title.lower(): 
            title = title.replace('2160p 4K UHD', '').replace('2160p 4k uhd', '').strip()
            qltys.append('2160p 4K UHD')

        if 'bd25' in title.lower(): 
            title = title.replace('BD25', '').replace('bd25', '').strip()
            qltys.append('BD25')

        if 'bdremux' in title.lower(): 
            title = title.replace('BDRemux', '').replace('BDremux', '').replace('bdremux', '').strip()
            qltys.append('BDRemux')

        if 'bdrip 1080p' in title.lower(): 
            title = title.replace('BDRip 1080p', '').replace('bdrip 1080p', '').strip()
            qltys.append('BDRip 1080p')

        if 'bdrip' in title.lower(): 
            title = title.replace('BDRip', '').replace('bdrip', '').strip()
            qltys.append('BDRip')

        if 'dvdrip' in title.lower(): 
            title = title.replace('DVDRip', '').replace('dvdrip', '').strip()
            qltys.append('DVDRip')

        if 'hddrip' in title.lower(): 
            title = title.replace('HDRip', '').replace('hddrip', '').strip()
            qltys.append('HDRip')

        if '1080p' in title.lower(): 
            title = title.replace('1080P', '').replace('1080p', '').strip()
            qltys.append('1080p')

        if '720p' in title.lower(): 
            title = title.replace('720P', '').replace('720p', '').strip()
            qltys.append('1080p')

        if '2d+3d' in title.lower() or '2d-3d' in title.lower(): 
            title = title.replace('2D+3D', '').replace('2d+3d', '').replace('2D-3D', '').replace('2d-3d', '').strip()
            qltys.append('2D+3D')

        if '3d+2d' in title.lower() or '3d-2d' in title.lower(): 
            title = title.replace('3D+2D', '').replace('3d+2d', '').replace('3D-2D', '').replace('3d-2d', '').strip()
            qltys.append('3D+2D')

        title = title.replace(', ,', '').replace(' ,', '').replace('- - -', '').replace(' -', '').replace(' / ', '').replace(' /', '').replace('&#8211;', '').strip()

        title_alt = title
        if ' (' in title_alt:
            title_alt = title_alt.replace('(', 'DEL')
            title_alt = scrapertools.find_single_match(title_alt, '(.*?)DEL').strip()

            if title_alt: title = title_alt

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=', '.join(qltys),
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'}, contentTitleAlt = title_alt ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, 'class="page-numbers current">.*?href="(.*?)"')
        if next_url:
            if '/page/' in next_url:
               itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<li class="opcion(.*?)</span> </li>')

    ses = 0

    for match in matches:
        ses += 1

        dvid = scrapertools.find_single_match(match, 'data-vid="(.*?)"')
        if not dvid: continue

        lang = scrapertools.find_single_match(match, '<div class="idioma">(.*?)<').strip()

        if 'latino' in lang.lower(): lang = 'Lat'
        elif 'castellano' in lang.lower() or 'español' in lang.lower(): lang = 'Esp'
        elif 'subtitulado' in lang.lower() or 'vose' in lang.lower(): lang = 'Vose'
        else: '?'

        servidor = scrapertools.find_single_match(match, '<p class="sevidor">(.*?)</p>').lower()

        if servidor == 'dood': servidor = 'doodstream'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', dvid = dvid, language = lang ))

    # Descarga y Torrents
    if '<a target="_blank" href="' in data:
        matches = scrapertools.find_multiple_matches(data, '<a target="_blank" href="(.*?)"')

        for url in matches:
            ses += 1

            if '/userscloud.' in url: pass
            elif '/uptobox.' in url: pass
            elif '/to.descargasnsn.to' in url: pass
            else: continue

            if '/to.descargasnsn.to' in url:
               other = ''
               servidor = 'torrent'
            else:
               other = 'D'
               servidor = servertools.get_server_from_url(url)
               servidor = servertools.corregir_servidor(servidor)

               url = servertools.normalize_url(servidor, url)

            itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    servidor = item.server

    if servidor == 'torrent':
        if PY3:
            from core import requeststools
            data = requeststools.read(item.url, '')
        else:
            data = do_downloadpage(item.url)

        if data:
           import os

           file_local = os.path.join(config.get_data_path(), "temp.torrent")
           with open(file_local, 'wb') as f: f.write(data); f.close()

           itemlist.append(item.clone( url = file_local, server = 'torrent' ))

        return itemlist

    elif item.other == 'D':
        itemlist.append(item.clone(server = servidor, url = item.url))

        return itemlist

    data = do_downloadpage(host + 'player/?vid=' + item.dvid)

    url = scrapertools.find_single_match(data, 'window.location.href="(.*?)"')

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

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

