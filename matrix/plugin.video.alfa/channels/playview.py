# -*- coding: utf-8 -*-
# -*- Channel Playview -*-
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
from core.item import Item
from platformcode import config, logger
from channels import autoplay
from channels import filtertools
from bs4 import BeautifulSoup
import base64
import datetime


IDIOMAS = {"Latino": "LAT", "Español": "CAST", "Subtitulado": "VOSE"}
list_language = list(IDIOMAS.values())
list_quality = list()
list_servers = ['upstream', 'cloudvideo', 'mixdrop', 'mystream', 'doodstream']
date = datetime.datetime.now()

canonical = {
             'channel': 'playview', 
             'host': config.get_setting("current_host", 'playview', default=''), 
             'host_alt': ["https://playview.io/"], 
             'host_black_list': [], 
             'pattern': '<link\s*rel="[^>]*icon"[^>]+href="([^"]+)"', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Películas', action='sub_menu',
                         thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Series', action='list_all', url=host + 'series-online',
                         thumbnail=get_thumb('tvshows', auto=True), first=0))

    itemlist.append(Item(channel=item.channel, title='Anime', action='list_all', url=host + 'anime-online',
                         thumbnail=get_thumb('tvshows', auto=True), first=0))

    itemlist.append(Item(channel=item.channel, title='Buscar', action='search', url=host + 'search/',
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(
        Item(channel=item.channel, title='Ultimas', action='list_all', url=host + 'estrenos-%s' % date.year, first=0,
             thumbnail=get_thumb('last', auto=True)))

    itemlist.append(
        Item(channel=item.channel, title='Todas', action='list_all', url=host + 'peliculas-online', first=0,
             thumbnail=get_thumb('all', auto=True)))

    itemlist.append(
        Item(channel=item.channel, title='Generos', action='section', thumbnail=get_thumb('genres', auto=True)))

    return itemlist


def create_soup(url, referer=None, unescape=False, forced_proxy_opt=None):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, forced_proxy_opt=forced_proxy_opt, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, forced_proxy_opt=forced_proxy_opt, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def list_all(item):
    logger.info()

    itemlist = list()
    listed = list()
    next = False

    soup = create_soup(item.url)
    matches = soup.find_all("div", class_="spotlight_container")

    first = item.first
    last = first + 20
    if last >= len(matches):
        last = len(matches)
        next = True

    for elem in matches[first:last]:

        url = elem.find("a",  class_="overviewPlay playLink")["href"]
        title = re.sub("\s{2}.*", "", elem.find("div", class_="spotlight_title").text.strip())
        thumb = elem.find("div", class_="spotlight_image lazy")["data-original"]
        try:
            year = elem.find_all("span", class_="slqual sres")[0].text
        except:
            year = "-"
        new_item = Item(channel=item.channel, title=title, thumbnail=thumb, infoLabels={'year': year})

        if elem.find("div", class_="info-series"):
            new_item.contentSerieName = title
            season_path = re.sub("-temp-\d+", "", scrapertools.find_single_match(url, "%s(.+)" % host))
            new_item.url = "%sver-temporadas-completas-de/%s" % (host, season_path)
            new_item.action = "seasons"

        else:
            new_item.contentTitle = title
            new_item.url = url
            new_item.action = "findvideos"
        if url not in listed:
            itemlist.append(new_item)
            listed.append(url)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if not next:
        url_next_page = item.url
        first = last
    else:
        try:
            url_next_page = soup.find_all("a", class_="page-link")[-1]["href"]
            first = 0
        except:
            url_next_page = None

    if url_next_page:
        itemlist.append(item.clone(title="Siguiente >>", url=url_next_page, action='list_all', first=first))
    return itemlist


def section(item):
    logger.info()
    itemlist = list()

    soup = create_soup(host).find("li", class_="dropdown")

    if item.title == "Generos":
        matches = soup.find_all("li")

    for elem in matches:
        url = elem.a["href"]
        title = elem.a.text
        if "serie" in title.lower():
            continue
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all", first=0 ))
    itemlist = sorted(itemlist, key=lambda i: i.title)

    return itemlist


def seasons(item):
    logger.info()
    itemlist = list()

    infoLabels = item.infoLabels
    soup = create_soup(item.url)
    matches = soup.find_all("div", class_="spotlight_container")

    if len(matches) == 1:

        season_info = scrapertools.find_single_match(matches[0], "Temporada (\d+)")
        if not season_info:
            season_info = 1
        url = matches[0].a["href"]
        infoLabels["season"] = season_info
        title = "Temporada %s" % season_info
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="episodesxseason",
                             infoLabels=infoLabels))
    else:
        for elem in matches:
            full_title = elem.find("div", class_="spotlight_title").text
            title = re.sub(r"%s|/.*" % item.infoLabels["tvshowtitle"].lower(), "", full_title.lower()).strip()
            url = elem.a["href"]
            infoLabels["season"] = scrapertools.find_single_match(title, "\d+")
            itemlist.append(Item(channel=item.channel, title=title.capitalize(), url=url, action="episodesxseason",
                                 infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    itemlist = sorted(itemlist, key=lambda i: i.title)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                             url=item.url, action="add_serie_to_library", extra="episodios",
                             contentSerieName=item.contentSerieName))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = list()

    info_soup = create_soup(item.url)
    set_option = "LoadOptionsEpisode"
    info = info_soup.find("div", id="ficha")
    post = {"set": set_option, 'action': "EpisodesInfo", "id": info["data-id"], "type": info["data-type"]}

    episodesinfo = httptools.downloadpage(host + canonical['channel'], post=post, canonical=canonical).data

    matches = BeautifulSoup(episodesinfo, "html5lib").find_all("div", class_="episodeBlock")
    infoLabels = item.infoLabels

    for elem in matches:
        epi_num = elem.find("div", class_="episodeNumber").text
        title = "%sx%s" % (infoLabels["season"], epi_num)
        infoLabels["episode"] = epi_num
        post = {"set": set_option, "action": "Step1", "id": elem["data-id"], "type": "1", 'episode': epi_num}

        itemlist.append(Item(channel=item.channel, title=title,action="findvideos", post=post,
                             infoLabels=infoLabels))
    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    set_option = "LoadOptions"
    episode = ""

    if item.post:
        post = item.post
        id = post['id']
        episode = post['episode']
        dtype = post['type']
        set_option = 'LoadOptionsEpisode'
    else:
        info_soup = create_soup(item.url)
        info = info_soup.find("div", id="ficha")
        id = info["data-id"]
        dtype = info["data-type"]
        post = {"set": set_option, 'action': "Step1", "id": id, "type": dtype}

    step1 = httptools.downloadpage(host + canonical['channel'], post=post, canonical=canonical).data

    matches = BeautifulSoup(step1, "html5lib").find_all("button", class_="select-quality")

    for step2 in matches:
        post = {"set": set_option, "action": "Step2", "id": id, "type": dtype,
                "quality": step2["data-quality"], "episode": episode}

        options = httptools.downloadpage(host + canonical['channel'], post=post, canonical=canonical).data

        soup = BeautifulSoup(options, "html5lib").find_all("li", class_="tb-data-single")
        for elem in soup:
            lang = elem.find("h4").text
            srv = re.sub(r"(\..+|\s.+)", "", elem.find("img")["title"])
            video_id = elem.find("button", class_="btn-link")["data-id"]
            qlty = scrapertools.find_single_match(step2["data-quality"], r"\d+p")
            post = {"set": set_option, "action": "Step3", "id": video_id, "type": dtype}
            if not srv:
                srv = "directo"
            itemlist.append(Item(channel=item.channel, title=srv.capitalize(), server=srv, action="play", post=post,
                                 language=IDIOMAS.get(lang, "LAT"), quality=qlty, infoLabels=item.infoLabels))

    itemlist = sorted(itemlist, key=lambda i: i.language)

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


def play(item):
    logger.info()

    data = httptools.downloadpage(host + canonical['channel'], post=item.post).data

    url_data = BeautifulSoup(data, "html5lib")
    try:
        iframe = url_data.find("iframe", class_="embed-responsive-item")["src"]
        url = httptools.downloadpage(iframe).url
    except:
        url_data = url_data.find("button", class_="linkfull")["data-url"]
        url = base64.b64decode(scrapertools.find_single_match(url_data, "/go/(.+)"))

    srv = servertools.get_server_from_url(url)
    item = item.clone(url=url, server=srv)

    return [item]


def search(item, texto):
    logger.info()

    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto
        item.first = 0
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
    item.type = 'movie'
    item.first = 0
    try:
        if categoria == 'peliculas':
            item.url = host + 'peliculas-online'
        elif categoria == 'infantiles':
            item.url = host + 'peliculas-online/animacion'
        elif categoria == 'terror':
            item.url = host + 'peliculas-online/terror'

        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist




