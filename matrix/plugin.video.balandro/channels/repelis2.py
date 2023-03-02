# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.repelis2.co/'



def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'estrenos/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Categorías<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article(.*?)</article>').findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2>(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        langs = []
        if '<div class="es">' in match: langs.append('Esp')
        if '<div class="lat">' in match: langs.append('Lat')
        if '<div class="vose">' in match: langs.append('Vose')

        year = scrapertools.find_single_match(match, '<div class="year">(.*?)</div>').strip()
        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title = title, thumbnail = thumb, languages = ', '.join(langs),
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="counter">.*?href="(.*?)"')

        if '/pagina' in next_page:
            itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', page=0, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    logger.info("check-1-data: %s" % data)

    matches = scrapertools.find_multiple_matches(data, '<div class="opt">(.*?)</div></div></div>')

    logger.info("check-1-matches: %s" % matches)

    ses = 0

    for match in matches:
        match = match + '</div></div></div>'

        logger.info("check-1-match: %s" % match)

        servers = scrapertools.find_multiple_matches(match, '<div class="server(.*?)</div></div></div>')

        logger.info("check-1-servers: %s" % servers)

        for srvs in servers:
            ses += 1

            srv = scrapertools.find_single_match(srvs, '<div class="s-name">(.*?)</div>')
            srv = srv.lower()

            if 'hqq' in srv or 'waaw' in srv or 'netu' in srv: continue

            qlty = scrapertools.find_single_match(srvs, '<div class="s-quality">(.*?)$')

            lang = scrapertools.find_single_match(srvs, '<div class="lang-name">(.*?)</div>')

            if lang == 'Latino': lang = 'Lat'
            elif lang == 'Español': lang = 'Esp'
            elif lang == 'Subtitulado': lang = 'Vose'

            hash = scrapertools.find_single_match(srvs, 'data-hash="(.*?)"')

            if hash:
               itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', hash = hash,
                                     quality = qlty, language = lang, other = srv.capitalize() ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = ''

    data = do_downloadpage(host + 'player.php?file=' + item.hash + '&play=1')

    url = scrapertools.find_single_match(data, '<iframe src="(.*?)"')
    if not url: url = scrapertools.find_single_match(data, '<IFRAME SRC="(.*?)"')

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor and not servidor == 'directo':
            url = servertools.normalize_url(servidor, url)

            if '.zplayer.' in url: url = url + "|https://player.cuevana2.io/"

            itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'buscar/' + texto.replace(" ", "+") + '/'
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
