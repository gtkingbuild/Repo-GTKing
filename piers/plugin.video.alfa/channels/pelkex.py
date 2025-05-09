# -*- coding: utf-8 -*-
# -*- Channel Pelkex -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core import tmdb
from core.item import Item
from platformcode import config, logger
from modules import autoplay
from channels import filtertools
from bs4 import BeautifulSoup

list_language = ["LAT"]
list_quality = list()
list_servers = ['zplayer', 'streamtape', 'mega', 'torrent']

canonical = {
             'channel': 'pelkex', 
             'host': config.get_setting("current_host", 'pelkex', default=''), 
             'host_alt': ["https://newpelis.re/"], 
             'host_black_list': ["https://newpelis.org/", "https://newpelis.nl/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Peliculas", action="list_all", url=host,
                         thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Series", action="list_all", url=host + "/series",
                         thumbnail=get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section",
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Años", action="section", thumbnail=get_thumb('year', auto=True)))


    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host + '?s=',
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

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
    soup = create_soup(item.url)
    matches = soup.find("div", class_="cf")
    for elem in matches.find_all("article", class_=re.compile("shortstory cf")):
        url = elem.a["href"]
        if elem.find('div', class_='short_header'):
            title = elem.find('div', class_='short_header').text.strip()
        else:
            title = elem.a.text.strip()
        thumb = elem.find("img")["src"]
        try:
            year = extra_info[1].text
        except:
            year = "-"
        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, infoLabels={"year": year})
        if "/peliculas/" in url:
            new_item.contentTitle = title
            new_item.action = "findvideos"
        else:
            new_item.contentSerieName = title
            new_item.action = "seasons"
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find_all("a", class_="page-numbers")[-1]["href"]

        if url_next_page:
            itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all',
                                 section=item.section))
    except:
        pass

    return itemlist


def section(item):
    logger.info()
    itemlist = list()
    soup = create_soup(host)
    action = 'list_all'
    menu = soup.find_all("ul", id="menu-home")
    if item.title == "Generos":
        matches = menu[0].find_all("li", class_="menu-item")
    else:
        matches = menu[1].find_all("li", class_="menu-item")
    for elem in matches:
        url = elem.a["href"]
        if not url.startswith("http"):
            url = host + url
        title = elem.a.text
        itemlist.append(Item(channel=item.channel, title=title, url=url, action=action, section=item.section))
    if item.title == "Generos":
        return itemlist
    else:
        return itemlist[::-1]


def seasons(item):
    logger.info()
    itemlist = list()
    infoLabels = item.infoLabels
    soup = create_soup(item.url)
    matches = soup.find_all('span', class_='season-title')
    for elem in matches:
        season= elem.text.strip().replace("Temporada", "")
        if int(season) < 10:
            season = "0%s" %season
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(item.clone(title=title, url=item.url, action="episodesxseasons",
                             infoLabels=infoLabels))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(item.clone(title="[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]", url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))
    return itemlist


def episodesxseasons(item):
    logger.info()
    itemlist = list()
    infoLabels = item.infoLabels
    season = infoLabels["season"]
    num_season = int(season) -1
    soup = create_soup(item.url)
    matches = soup.find_all('ul', class_='seasons-list')[num_season]
    for elem in matches.find_all('li'):
        cap= elem.text
        cap = scrapertools.find_single_match(cap, "tulo (\d+)")
        if int(cap) < 10:
            cap = "0%s" % cap
        title = "%sx%s" % (season, cap)
        infoLabels["episode"] = cap
        # url= elem.cla['href']
        itemlist.append(item.clone(title=title, action="findvideos",
                                 infoLabels=infoLabels))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = list()
    if "/series/" in item.url:
        infoLabels = item.infoLabels
        num_season = int(infoLabels["season"]) -1
        num_cap = int(infoLabels["episode"]) -1
        soup = create_soup(item.url)
        online = soup.find_all('ul', class_='seasons-list')[num_season].find_all('li')[num_cap]
        url = online['data-url']
        itemlist.append(Item(channel=item.channel, title="%s", url=url, action="play",
                             language="LAT", infoLabels=item.infoLabels))
        itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
        download = soup.find_all('div', class_='panel')[num_season].find_all('a')[num_cap]
        url = download['href']
        itemlist.append(Item(channel=item.channel, title="Torrent", url=url, server="torrent", action="play",
                             language="LAT", infoLabels=item.infoLabels))
    else:
        url = "%s?play" %item.url
        soup = create_soup(url)
        matches = soup.find('ul', class_='server-list').find_all('li')
        for elem in matches:
            import base64
            enc_url = elem.a['data-id']
            url = base64.b64decode(enc_url).decode('utf-8')
            if "Trailer" in elem.a.text:
                url = "https://www.youtube.com/watch?v=%s" %enc_url
            itemlist.append(Item(channel=item.channel, title="%s", url=url, action="play",
                                 language="LAT", infoLabels=item.infoLabels))
        itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
        url = "%s?download" %item.url
        soup = create_soup(url)
        url = soup.tbody.find('td').a['href']
        itemlist.append(Item(channel=item.channel, title="Torrent", url=url, server="torrent", action="play",
                             language="LAT", infoLabels=item.infoLabels))
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    if item.contentType == 'movie':
        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
            itemlist.append(
                Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
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
        import sys

        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()

    item = Item()
    try:
        if categoria in ['peliculas', 'latino', 'torrent']:
            item.url = host
        elif categoria == 'infantiles':
            item.url = host + 'category/infantil'
        elif categoria == 'terror':
            item.url = host + 'category/terror'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist




