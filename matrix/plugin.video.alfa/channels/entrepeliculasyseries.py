# -*- coding: utf-8 -*-
# -*- Channel EntrePeliculasySeries -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
import traceback

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb, jsontools
from core.item import Item
from platformcode import config, logger
from channels import autoplay
from channels import filtertools
from bs4 import BeautifulSoup

IDIOMAS = {"latino": "LAT", "castellano": "CAST", "subtitulado": "VOSE"}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_servers = ['mega', 'fembed', 'vidtodo', 'gvideo']

canonical = {
             'channel': 'entrepeliculasyseries', 
             'host': config.get_setting("current_host", 'entrepeliculasyseries', default=''), 
             'host_alt': ['https://entrepeliculasyseries.nz/'], 
             'host_black_list': ['https://entrepeliculasyseries.nu/'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

forced_proxy_opt = 'ProxyDirect'
under_proxy = False


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Peliculas",  action="sub_menu",
                         thumbnail=get_thumb('channels_movie.png')))

    itemlist.append(Item(channel=item.channel, title="Series", action="sub_menu",
                         thumbnail=get_thumb('channels_tvshow.png')))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", 
                         thumbnail=get_thumb('search.png')))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    if item.title == "Peliculas":
        mode = "movie"
        itemlist.append(Item(channel=item.channel, title="[B]Todas[/B]", action="list_all", url=host + 'peliculas/',
                             section='movies', thumbnail=get_thumb('channels_movie.png'), mode=mode))
    else:
        mode = "tv"
        itemlist.append(Item(channel=item.channel, title="Últimos Episodios", action="list_all", url=host + 'episodios/',
                             section='episodes', thumbnail=get_thumb('on_the_air.png'), mode=mode))

        itemlist.append(Item(channel=item.channel, title="Últimas Series", action="list_all", url=host + 'series-recientes/',
                             section='last', thumbnail=get_thumb('popular.png'), mode=mode))

        itemlist.append(Item(channel=item.channel, title="[B]Todas[/B]", action="list_all", url=host + 'series/',
                             section='series', thumbnail=get_thumb('channels_tvshow.png'), mode=mode))

        itemlist.append(Item(channel=item.channel, title="Productoras", action="producers", url=host + 'episodios/',
                         section='producer', thumbnail=get_thumb('channels_anime.png'), mode=mode))
    
    itemlist.append(Item(channel=item.channel, title="Géneros", action="genres", section='genre', 
                         thumbnail=get_thumb('genres.png'), mode=mode))

    return itemlist


def create_soup(url, referer=None, unescape=False, forced_proxy_opt=None, ignore_response_code=True):
    logger.info()
    global under_proxy

    if referer:
        response = httptools.downloadpage(url, forced_proxy_opt=forced_proxy_opt, ignore_response_code=ignore_response_code, 
                                          headers={'Referer': referer}, canonical=canonical, CF=False)
    else:
        response = httptools.downloadpage(url, forced_proxy_opt=forced_proxy_opt, ignore_response_code=ignore_response_code, 
                                          canonical=canonical, CF=False)
    
    data = response.data or ''
    if response.proxy__: under_proxy = True

    if unescape:
        data = scrapertools.unescape(data)
    
    if data:
        soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    else:
        soup = ''

    return soup


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    
    try:
        if item.section in ['search']:
            matches = soup.find_all("li", class_="xxx TPostMv")
        elif item.section in ['episodes']:
            matches = soup.find("ul", class_="MovieList").find_all("article", class_="TPost C")
        else:
            matches = soup.find("ul", class_="list-movie").find_all("li", class_="item")
    except:
        logger.error(traceback.format_exc(1))
        logger.debug(soup)
        return itemlist

    for elem in matches:
        try:
            url = elem.a["href"] or elem.find("a", class_="link-title")["href"]
            title = scrapertools.decode_utf8_error(elem.h2.text)
            year = scrapertools.find_single_match(elem.h4.text, "(\d{4})") if item.section not in ['episodes', 'search'] else '-'
            thumb = elem.a.img["src"] or elem.a.img["data-src"]

            new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, infoLabels={'year': year})

            if "/episodio" in url or item.section in ['episodes']:
                new_item.contentSerieName = scrapertools.find_single_match(title, '(.*?)\s+\d{1,2}[x|X]\d{1,3}')
                if scrapertools.find_single_match(title, '.*?\s+(\d{1,2})[x|X](\d{1,3})'):
                    new_item.contentSeason, new_item.contentEpisodeNumber = scrapertools.find_single_match(title, '.*?\s+(\d{1,2})[x|X](\d{1,3})')
                new_item.action = "findvideos"
                new_item.contentType = 'episode'
                new_item.context = filtertools.context(item, list_language, list_quality)
            elif "/serie" in url or 'tv' in item.mode:
                new_item.contentSerieName = title
                new_item.action = "seasons"
                new_item.contentType = 'tvshow'
                if item.section in ['search']:
                    new_item.infoLabels['tagline'] = '[COLOR coral]-Serie-[/COLOR]'
                new_item.context = filtertools.context(item, list_language, list_quality)
            else:
                new_item.contentTitle = title
                new_item.action = "findvideos"
                new_item.contentType = 'movie'
                if item.section in ['search']:
                    new_item.infoLabels['tagline'] = '[COLOR white]-Película-[/COLOR]'

            itemlist.append(new_item)
        except:
            logger.error(traceback.format_exc(1))
            logger.debug(elem)
            continue

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find("a", class_="nextpostslink")["href"]
        if soup.find("a", class_="last"):
            url_last_page = soup.find("a", class_="last")["href"]
        elif soup.find("a", class_="page larger"):
            url_last_page = soup.find("a", class_="page larger")["href"]
        else:
            url_last_page = url_next_page
        
        url_next_page_num = 1
        url_last_page_num = 1
        if url_next_page: url_next_page_num = scrapertools.find_single_match(url_next_page, '\/(\d+)\/?')
        if url_last_page: url_last_page_num = scrapertools.find_single_match(url_last_page, '\/(\d+)\/?')

        if url_next_page:
            itemlist.append(Item(channel=item.channel, title="Siguiente >> %s de %s" % (url_next_page_num, url_last_page_num), 
                                 url=url_next_page, action='list_all', section=item.section))
    except:
        pass

    return itemlist


def producers(item):
    logger.info()
    itemlist = list()

    action = 'list_all'
    soup = create_soup(item.url).find("ul", class_="category-carrusel-inner")
    matches = soup.find_all("li", class_="item")

    for elem in matches:
        url = elem.a["href"]
        title = elem.a.text.strip().replace('\n', ':').split(':')
        plot = title[1] if len(title) > 1 else ''
        title = title[0]
        if not under_proxy:
            thumb = elem.img["src"]
        else:
            thumb = get_thumb('channels_anime.png')
        
        itemlist.append(Item(channel=item.channel, title=title, url=url, action=action, 
                             section=item.section, mode=item.mode, thumbnail=thumb, contentPlot=plot))

    return itemlist


def genres(item):
    logger.info()
    itemlist = list()

    action = 'list_all'
    soup = create_soup(host).find("nav", class_="Menu").find("li", class_=re.compile("AAIco-%s menu-category" % item.mode))

    matches = soup.find("ul", class_="sub-menu").find_all("li")
    for elem in matches:
        url = elem.a["href"]
        title = elem.a.text
        
        itemlist.append(Item(channel=item.channel, title=title, url=url, action=action, 
                             section=item.section, mode=item.mode))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("div", class_="select-season").find_all("option")
    infoLabels = item.infoLabels
    if '-Serie-' in infoLabels.get('tagline', ''): del infoLabels['tagline']

    for elem in matches:
        season = elem["value"]
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseason',
                             infoLabels=infoLabels, contentType='season'))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0 and not item.extra:
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_serie_to_library",
                             extra="episodios",
                             contentType='season', 
                             contentSerieName=item.contentSerieName
                             ))
    
    tmdb.set_infoLabels_itemlist(itemlist, True)
    
    return itemlist


def episodios(item):
    logger.info()

    itemlist = list()
    templist = seasons(item)
    
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = list()
    season = item.infoLabels["season"]
    soup = create_soup(item.url).find("ul", id="season-%s" % season)
    if not soup: return itemlist
    matches = soup.find_all("article")
    infoLabels = item.infoLabels

    for elem in matches:
        if elem.find("i", class_="fa fa-calendar"):
            continue
        url = elem.a["href"]
        episode = scrapertools.find_single_match(elem.h2.text, "\d+x(\d+)")
        title = "%sx%s" % (infoLabels["season"], episode)
        infoLabels["episode"] = episode

        itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                             infoLabels=infoLabels, contentType='episode'))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    if '-Película-' in item.infoLabels.get('tagline', ''): del item.infoLabels['tagline']

    try:
        matches = soup.find_all("div", class_=re.compile(r"option-lang"))
    except:
        matches = []

    for elem in matches:
        lang = elem.h3.text.lower().strip()
        try:
            lang, quality = scrapertools.find_single_match(lang, '(^\w+)[^$]*\s+(\w+$)')
        except:
            lang = scrapertools.find_single_match(lang, '(^\w+)')
            quality = ''

        if lang == "descargar":
            continue

        for opt in elem.find_all("li", class_="option"):
            server = opt.text.lower().strip()
            url = opt["data-link"]
            if host not in url:
                url = host.rstrip('/') + url

            itemlist.append(Item(channel=item.channel, title=server.capitalize(), url=url, server=server, action="play",
                                 language=IDIOMAS.get(lang, 'LAT'), quality=quality.capitalize(), infoLabels=item.infoLabels))

    if itemlist: itemlist = sorted(itemlist, key=lambda it: it.language)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if item.contentType == 'movie':
        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
            itemlist.append(
                Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                     url=item.url, action="add_pelicula_to_library", extra="findvideos",
                     contentTitle=item.contentTitle, contentType='movie'))

    return itemlist


def search(item, texto):
    logger.info()

    try:
        texto = texto.replace(" ", "+")
        item.url = host + '?s=' + texto
        item.section = 'search'

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
        if categoria == 'peliculas':
            item.url = host + 'peliculas/'
        elif categoria == 'infantiles':
            item.url = host + 'peliculas-de-animacion/'
        elif categoria == 'terror':
            item.url = host + 'peliculas-de-terror/'
        itemlist = list_all(item)
        if 'Siguiente >>' in itemlist[-1].title:
            itemlist[-1].pop()
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def play(item):
    
    itemlist = list()
    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 'timeout': 5}
    
    id = scrapertools.find_single_match(item.url, "h=([^$]+)")
    headers = {"referer": item.url}
    post = {"h": id}
    base_url = "%sr.php" % host
    url = ''
    
    for x in range(2):
        resp = httptools.downloadpage(base_url, post=post, headers=headers, follow_redirects=False, 
                                     forced_proxy_opt=forced_proxy_opt, CF=False, **kwargs)
        if resp.code in httptools.REDIRECTION_CODES:
            url = resp.headers.get("location", "")
            break
    
    if url and not url.startswith("http"):
        url = "https:" + url
    item.server = ""
    itemlist.append(item.clone(url=url))

    itemlist = servertools.get_servers_itemlist(itemlist)
    
    return itemlist
