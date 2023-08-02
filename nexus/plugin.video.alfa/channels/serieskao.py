# -*- coding: utf-8 -*-
# -*- Channel SeriesKao -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re
import base64

from core import tmdb
from core import httptools
from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from lib import jsunpack
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from bs4 import BeautifulSoup


IDIOMAS = {'2': 'VOSE', "0": "LAT", "1": "CAST"}

list_language = list(IDIOMAS.values())

list_quality = []

list_servers = [
    'gvideo',
    'fembed',
    'directo'
    ]

canonical = {
             'channel': 'serieskao', 
             'host': config.get_setting("current_host", 'serieskao', default=''), 
             'host_alt': ["https://serieskao.top/"], 
             'host_black_list': ["https://serieskao.org/", "https://serieskao.net/"], 
             'pattern': ['<link\s*rel="shortcut\s*icon"\s*href="(\w+\:\/\/[^\/]+\/)'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Todas', action='list_all', url=host + "peliculas",
                         thumbnail=get_thumb('movies', auto=True), type="peliculas"))
    itemlist.append(Item(channel=item.channel, title='Por Género', action='genres', url=host,
                         thumbnail=get_thumb('movies', auto=True), type="peliculas"))
    itemlist.append(Item(channel=item.channel, title='Año', action='genres', url=host,
                         thumbnail=get_thumb('movies', auto=True), type="peliculas"))
    itemlist.append(Item(channel=item.channel, title='Series', url=host + 'series', action='list_all',
                         thumbnail=get_thumb('tvshows', auto=True), type="series"))
    itemlist.append(Item(channel=item.channel, title='Por Género', action='genres', url=host,
                         thumbnail=get_thumb('tvshows', auto=True), type="series"))
    itemlist.append(Item(channel=item.channel, title='Año', action='genres', url=host,
                         thumbnail=get_thumb('tvshows', auto=True), type="series"))
    itemlist.append(Item(channel=item.channel, title='Anime', url=host + 'animes', action='list_all',
                         thumbnail=get_thumb('channels_anime.png', auto=True), type="animes"))
    itemlist.append(Item(channel=item.channel, title='Por Género', action='genres', url=host,
                         thumbnail=get_thumb('channels_anime.png', auto=True), type="animes"))
    itemlist.append(Item(channel=item.channel, title='Año', action='genres', url=host,
                         thumbnail=get_thumb('channels_anime.png', auto=True), type="animes"))
    itemlist.append(Item(channel=item.channel, title='Dorama', url=host + 'generos/dorama', action='list_all',
                         thumbnail=get_thumb('channels_anime.png', auto=True), type="animes"))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search",
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def genres(item):
    logger.info()
    itemlist = list()
    existe = []
    data = httptools.downloadpage(item.url).data
    if 'Por Género' in item.title:
        matches = scrapertools.find_multiple_matches(data, '(?is)href="/(genero[^"]+)">([^<]+)')
    else:
        matches = scrapertools.find_multiple_matches(data, '(?is)href="/(year[^"]+)">(\d+)<')
    for url, title in matches:
        url += "/%s" %item.type
        if title in existe: continue
        existe.append(title)
        itemlist.append(Item(channel=item.channel, title=title, url=host + url,
                 action="list_all"))
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def list_all(item):
    logger.info()
    itemlist = list()
    year = ""
    soup = create_soup(item.url)
    matches = soup.find_all("a", class_="Posters-link")
    for elem in matches:
        url = elem['href']
        title = elem['data-title']
        title = elem.p.text
        thumbnail = elem.img['src']
        year = scrapertools.find_single_match(title, ' \((\d+)\)')
        title = scrapertools.find_single_match(title, '(.*?) \(\d+\)')
        if year == '':
            year = '-'
        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumbnail, infoLabels={"year": year})
        if "/serie/" in url:
            new_item.contentSerieName = title
            new_item.action = "seasons"
            new_item.context = filtertools.context(item, list_language, list_quality)
        else:
            new_item.contentTitle = title
            new_item.action = "findvideos"
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    next_page = soup.find('a', rel='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="list_all", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def seasons(item):
    logger.info()
    itemlist = list()
    soup = create_soup(item.url)
    matches = soup.find('ul', role='tablist').find_all('li')
    infoLabels = item.infoLabels
    for elem in matches:
        season = scrapertools.find_single_match(elem.text, '\d+')
        infoLabels["season"] = season

        itemlist.append(Item(channel=item.channel, title="Temporada %s" %season, url=item.url, action='episodesxseasons',
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)

    return itemlist


def episodesxseasons(item):
    logger.info()
    itemlist = list()
    season = item.infoLabels["season"]
    id = "pills-vertical-%s" %season
    soup = create_soup(item.url)
    matches = soup.find('div', id=id).find_all('a')
    infoLabels = item.infoLabels
    for elem in matches:
        url = elem['href']
        epi_num = scrapertools.find_single_match(url, "/capitulo/(\d+)")
        infoLabels["episode"] = epi_num
        title = "%sx%s" % (season, epi_num)
        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = list()
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, "video\[1\] = '([^']+)")
    soup = create_soup(url)
    matches = soup.find('div', class_='OptionsLangDisp').find_all('li')
    for elem in matches:
        url = elem['onclick']
        lang = elem['data-lang']
        url = scrapertools.find_single_match(url, "go_to_player\('([^']+)")
        url = "https://api.mycdn.moe/player/?id=%s" %url
        soup = create_soup(url)
        video_url = soup.iframe['src']
        if "uptobox=" in video_url:
            url = scrapertools.find_single_match(video_url, 'uptobox=([A-z0-9]+)')
            video_url = "https://uptobox.com/%s" %url
        if "1fichier=" in video_url:
            url = scrapertools.find_single_match(video_url, '1fichier=\?([A-z0-9]+)')
            video_url = "https://1fichier.com/?%s" %url
        if "/embedsito.net/" in video_url:
            data = httptools.downloadpage(video_url).data
            url = scrapertools.find_single_match(data, 'var shareId = "([^"]+)"')
            video_url = "https://www.amazon.com/clouddrive/share/%s" %url
        language = IDIOMAS.get(lang, lang)
        if not "plusvip" in video_url:
            itemlist.append(Item(channel=item.channel, title='%s', action='play', url=video_url,
                                       language=language, infoLabels=item.infoLabels))
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
        item.url = "%ssearch?s=%s" % (host, texto)

        # item.url = item.url + texto
        item.extra = "buscar"

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

    item = Item()
    try:
        if categoria in ['peliculas']:
            item.url = host + 'pelicula'
        elif categoria == 'infantiles':
            item.url = host + 'pelicula/filtro/?genre=animacion-2'
        elif categoria == 'terror':
            item.url = host + 'pelicula/filtro/?genre=terror-2/'
        item.first = 0
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
