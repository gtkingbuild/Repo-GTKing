# -*- coding: utf-8 -*-
# -*- Channel TuPelicula -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from channels import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channelselector import get_thumb

IDIOMAS = {'la_la': 'LAT', 'es_es':'CAST', 'en_es':'VOSE', 'en_en':'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['xdrive', 'bitertv', 'okru']

canonical = {
             'channel': 'tupelicula', 
             'host': config.get_setting("current_host", 'tupelicula', default=''), 
             'host_alt': ["http://www.tupelicula.tv/"], 
             'host_black_list': [], 
             'pattern': '<div\s*id="logo">\s*<a\s*href="([^"]+)"', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def get_source(url, referer=None):
    logger.info()
    if referer is None:
        data = httptools.downloadpage(url, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, headers={'Referer':referer}, canonical=canonical).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    return data

def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host,
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Castellano", action="list_all", url=host+'filter?language=1',
                         thumbnail=get_thumb('cast', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Latino", action="list_all", url=host + 'filter?language=2',
                         thumbnail=get_thumb('lat', auto=True)))

    itemlist.append(Item(channel=item.channel, title="VOSE", action="list_all", url=host + 'filter?language=4',
                         thumbnail=get_thumb('vose', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section",
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title = 'Buscar', action="search", url=host + 'search?q=',
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    itemlist = []

    full_data = get_source(item.url)
    data = scrapertools.find_single_match(full_data, '<div id="movie-list"(.*?)</ul>')
    patron = '<a href="([^"]+)".*?data-original="([^"]+)" alt="([^"]+)".*?'
    patron += '<div class="_audio">(.*?)"label_year">(\d{4}) &bull;([^<]+)<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, lang_data, year, genre in matches:
        url = scrapedurl
        scrapedtitle = scrapertools.find_single_match(scrapedtitle, '([^\(]+)')
        lang = get_language(lang_data)
        thumbnail = 'https:'+scrapedthumbnail
        if genre.lower() not in ['adultos', 'erotico'] or config.get_setting('adult_mode') > 0:
            itemlist.append(Item(channel=item.channel, title=scrapedtitle, url=url, action='findvideos',
                            thumbnail=thumbnail, contentTitle=scrapedtitle, language = lang,
                            infoLabels={'year':year}))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    # Paginacion

    if itemlist != []:

        next_page = scrapertools.find_single_match(full_data, '<li><a href="([^"]+)"><i class="fa fa-angle-right">')
        if next_page != '':
            itemlist.append(Item(channel=item.channel, action="list_all", title='Siguiente >>>', url=next_page))

    return itemlist



def section(item):
    logger.info()

    itemlist = []
    data=get_source(host)
    if item.title == 'Generos':
        data = scrapertools.find_single_match(data, '>Películas por género</div>(.*?)</ul>')
        patron = '<a href="([^"]+)"><span class="icon"></span>.?([^<]+)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title in matches:
        if title.lower() not in ['adultos', 'erotico'] or config.get_setting('adult_mode') > 0:
            itemlist.append(Item(channel=item.channel, title=title, url=url, action='list_all'))

    return itemlist

def get_language(lang_data):
    logger.info()
    language = []

    lang_list = scrapertools.find_multiple_matches(lang_data, '/flags/(.*?).png"?')
    for lang in lang_list:
        lang = IDIOMAS[lang]
        if lang not in language:
            language.append(lang)
    return language

def findvideos(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)
    player = scrapertools.find_single_match(data, '<iframe id="playerframe" data-src="([^"]+)"')
    data = get_source(player)
    patron = 'data-id="(\d+)">.*?img src="([^"]+)".*?>([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scraped_id, lang_data, quality in matches:
        hidden_url = get_source('%splayer/rep/%s' % (host, scraped_id), player)
        url = scrapertools.find_single_match(hidden_url.lower(), 'iframe src=.?"([^"]+)"').replace('\\','')
        lang = get_language(lang_data)

        if not config.get_setting('unify'):
            title = ' %s' % lang
        else:
            title = ''

        if url != '':
            itemlist.append(Item(channel=item.channel, title='%s'+title, url=url, action='play', language=lang,
                                 infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto

        if texto != '':
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host
        elif categoria == 'latino':
            item.url = host + 'filter?language=2'

        elif categoria == 'castellano':
            item.url = host + 'filter?language=1'

        elif categoria == 'infantiles':
            item.url = host + 'genre/25/infantil'
        elif categoria == 'terror':
            item.url = host + 'genre/15/terror'
        item.pages=3
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

