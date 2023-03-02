# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.sinpeli.com/'


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

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/castellano/' ))
    itemlist.append(item.clone( title = 'Castellano AC3 5.1', action = 'list_all', url = host + 'idioma/castellano51/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/latino/' ))
    itemlist.append(item.clone( title = 'Latino AC3 5.1', action = 'list_all', url = host + 'idioma/latino51/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/subtituladas/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Genero</a>(.*?)>Idiomas<')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Cam', action = 'list_all', url = host + 'calidad/cam/' ))
    itemlist.append(item.clone( title = '720p', action = 'list_all', url = host + 'calidad/720p/' ))
    itemlist.append(item.clone( title = '1080p', action = 'list_all', url = host + 'calidad/1080p/' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)class="Copy">')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<div class="Title">(.*?)</div>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        qlty = scrapertools.find_single_match(match, '<span class="Qlty">(.*?)</span>')

        year = '-'

        if title.endswith(')') == True:
           part_title = title.split('(')[0].strip()
           year = title.split('(')[1].strip()

           if part_title: title = part_title

           year = year.replace(')', '').strip()

           if not year: year = '-'

        langs = []
        lngs = scrapertools.find_multiple_matches(match, 'bold;"><img src="(.*?)"')

        if 'castellano' in str(lngs): langs.append('Esp')
        if 'latino' in str(lngs): langs.append('Lat')
        if 'subtitulado' in str(lngs): langs.append('Vose')

        plot = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=', '.join(langs), qualities=qlty,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, "<span aria-current='page' class='current'>.*?" + 'href="(.*?)"')
        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'data-tplayernv="Opt(.*?)</li>')

    ses = 0

    for match in matches:
        ses += 1

        servidor = scrapertools.find_single_match(match, "<span>(.*?)</span>").lower()

        if 'trailer' in servidor: continue
        elif 'waaw' in servidor: continue
        elif 'hqq' in servidor: continue
        elif 'netu' in servidor: continue

        if servidor == 'ok': servidor = 'okru'

        lang = scrapertools.find_single_match(match, "</span><span>(.*?)</span>").strip()

        if 'Latino' in lang: lang = 'Lat'
        elif 'Castellano' in lang or 'Español' in lang: lang = 'Esp'
        elif 'Subtitulado' in lang or 'VOSE' in lang: lang = 'Vose'
        else: lang = '?'

        qlty = scrapertools.find_single_match(match, "</span><span>.*?-(.*?)</span>").strip()
        if 'Subtitulado -' in qlty: qlty = qlty.replace('Subtitulado -', '').strip()

        url = scrapertools.find_single_match(match, 'data-player="(.*?)"')

        if not servidor == 'cuevana3'and not servidor == 'ver online':
            itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = lang, quality=qlty ))

        else:
            new_url = base64.b64decode(url)

            if 'b"' in str(new_url): new_url = str(new_url).replace('b"', '').replace('"', '')

            new_url = scrapertools.find_single_match(str(new_url), "src='(.*?)'")

            if new_url:
                data2 = do_downloadpage(new_url)

                links = scrapertools.find_multiple_matches(data2, "go_to_player.*?'(.*?)'")

                for link in links:
                    if '/hqq.' in link or '/waaw.' in link or '/netu.' in link: continue

                    servidor = servertools.get_server_from_url(link)
                    servidor = servertools.corregir_servidor(servidor)

                    url = servertools.normalize_url(servidor, link)

                    other = ''

                    if servidor == 'directo': other = 'cuevana3'

                    itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '',
                                                                  language = lang, quality = qlty, other = other ))

    # Descargas recaptcha y comprimidos por partes
    # patron = 'class="Button STPb  toggle_links">Download.*?">(.*?)</span>.*?href="(.*?)".*?alt=.*?">(.*?)</span>.*?class=.*?">(.*?)</span>'

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.other == 'cuevana3':
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

        return itemlist

    try:
        url = base64.b64decode(url)
        if url: url = scrapertools.find_single_match(str(url), "<iframe src='(.*?)'")
    except:
        url = item.url

    if not url: url = item.url

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

