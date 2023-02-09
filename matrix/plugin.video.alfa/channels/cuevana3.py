# -*- coding: utf-8 -*-
# -*- Channel Cuevana 3 -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int

if PY3:
    import urllib.parse as urllib                                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                                               # Usamos el nativo de PY2 que es más rápido

import re

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


IDIOMAS = {"optl": "LAT", "opte": "CAST", "opts": "VOSE"}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['fastplay', 'directo', 'streamplay', 'flashx', 'streamito', 'streamango', 'vidoza']

canonical = {
             'channel': 'cuevana3', 
             'host': config.get_setting("current_host", 'cuevana3', default=''), 
             'host_alt': ["https://www3.cuevana3.ai/"], 
             'host_api': 'api.cuevana3.me', 
             'host_black_list': ["https://cuevana3.be/", "https://www4.cuevana3.ai/", 
                                 "https://www1.cuevana3.ai/", "https://ww1.cuevana3.ai/", "https://cuevana3.ai/", 
                                 "https://h3.cuevana3.me/", "https://v1.cuevana3.me/", "https://v3.cuevana3.me/", 
                                 "https://s2.cuevana3.me/", "https://z2.cuevana3.me/", "https://a2.cuevana3.me/", 
                                 "https://ww1.cuevana3.me/", "https://s3.cuevana3.me/", "https://ww4.cuevana3.me/", 
                                 "https://ww3.cuevana3.me/", "https://cuevana3.me/", "https://cuevana3.io/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
domain = scrapertools.find_single_match(host, patron_domain)
domain_fix = domain
domain_api =  canonical['host_api']

forced_proxy_opt = 'ProxyDirect'


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host+'peliculas',
                         thumbnail=get_thumb('all', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Estrenos", action="list_all", url=host+'estrenos',
                         thumbnail=get_thumb('premieres', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Mas vistas", action="list_all", url=host+'peliculas-mas-vistas',
                         thumbnail=get_thumb('more watched', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Mas votadas", action="list_all", url=host+'peliculas-mas-valoradas',
                         thumbnail=get_thumb('more voted', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="genres", section='genre',
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Castellano", action="list_all", url= host+'peliculas-espanol',
                         thumbnail=get_thumb('audio', auto=True)))
    
    itemlist.append(Item(channel=item.channel, title="Latino", action="list_all", url=host + 'peliculas-latino',
                         thumbnail=get_thumb('audio', auto=True)))
    
    itemlist.append(Item(channel=item.channel, title="VOSE", action="list_all", url=host + 'peliculas-subtituladas',
                         thumbnail=get_thumb('audio', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host,
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def create_soup(url, referer=None, unescape=False, forced_proxy_opt=None):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, forced_proxy_opt=forced_proxy_opt, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, forced_proxy_opt=forced_proxy_opt, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    matches = soup.find("ul", class_="MovieList").find_all("li", class_="xxx")

    for elem in matches:
        thumb = elem.find("figure").img["src"]
        title = elem.find("h2", class_="Title").text
        url = elem.a["href"]
        year = elem.find("span", class_="Year").text

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             thumbnail=thumb, contentTitle=title, infoLabels={'year': year}))

    tmdb.set_infoLabels_itemlist(itemlist, True)
    try:
        url_next_page = soup.find("a", class_="next")["href"]
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all',
                             section=item.section))
    except:
        pass

    return itemlist


def genres(item):
    logger.info()
    itemlist = list()

    soup = create_soup(host)

    action = 'list_all'

    matches = soup.find("li", class_="menu-item menu-item-has-children cols3").find_all("li")

    for elem in matches:
        url = elem.a["href"]
        title = elem.a.text
        if title != 'Ver más':
            new_item = Item(channel=item.channel, title= title, url=url, action=action, section=item.section)
            itemlist.append(new_item)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list ()
    servers_list = {"1": "directo", "2": "streamtape", "3": "fembed", "4": "netu"}
    soup = create_soup(item.url, forced_proxy_opt=forced_proxy_opt).find("div", class_="TPlayer embed_div")

    matches = soup.find_all("div", class_="TPlayerTb")
    for elem in matches[:-1]:
        srv = servers_list.get(elem["id"][-1], "directo")
        lang = IDIOMAS.get(elem["id"][:-1].lower(), "VOSE")
        elem = elem.find("iframe")
        url = elem["data-src"]
        v_id = scrapertools.find_single_match(url, '\?h=(.*)')

        if url:
            itemlist.append(Item(channel=item.channel, title="%s", url=url, action="play", server=srv.capitalize(),
                                 language=lang, v_id=v_id, infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % '%s [%s]' % (i.server.capitalize(),
                                                                                           i.language))

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                 action="add_pelicula_to_library", extra="findvideos", contentTitle=item.contentTitle))

    return itemlist


def search(item, texto):
    logger.info()

    try:
        texto = texto.replace(" ", "+")
        item.url = '%ssearch/%s' % (host, texto)

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
        if categoria == 'peliculas':
            item.url = host+'estrenos'
        elif categoria == 'infantiles':
            item.url = host+'category/animacion'
        elif categoria == 'terror':
            item.url = host+'category/terror'
        elif categoria == 'documentales':
            item.url = host+'category/documental'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def play(item):
    logger.info()

    item.server = ""

    if domain_fix in item.url or domain_api in item.url or "tomatomatel" in item.url:
        item.url = get_urls(item.url, item.v_id)
    
    if "damedamehoy" in item.url:
        item.url, id = item.url.split("#")
        new_url = "https://damedamehoy.xyz/details.php?v=%s" % id
        item.url = httptools.downloadpage(new_url, forced_proxy_opt=forced_proxy_opt).json["file"]
    elif "embed.html#" in item.url:
        new_url = item.url.replace("=", "").replace("embed.html#", "details.php?v=") + "&r"
        item.url = httptools.downloadpage(new_url, forced_proxy_opt=forced_proxy_opt).json["file"]

    if "netu" in item.url:
        return []

    itemlist = servertools.get_servers_itemlist([item])

    return itemlist


def get_urls(url, v_id, domain=domain):

    base_url = "https://api.%s/ir/rd.php" % domain
    param = 'url'
    
    if 'tomatomatel' in url:
        if not url.startswith('http'): url = "https:%s" % url
        base_url = '%s/ir/rd.php' % scrapertools.find_single_match(url, patron_host)

    if '/sc/' in url:
        base_url = "https://api.%s/sc/r.php" % domain
        param = 'h'

    elif 'goto_ddh.php' in url:
        base_url = "https://api.%s/ir/redirect_ddh.php" % domain

    elif 'goto.php' in url:
        base_url = "https://api.%s/ir/goto.php" % domain
    
    elif domain_api in url:
        if not url.startswith('http'): url = "https:%s" % url
        base_url = re.sub('\?h=.*?$', 'api.php', url)
        param = 'h'

    url = httptools.downloadpage(base_url, post={param: v_id}, timeout=5, forced_proxy_opt=forced_proxy_opt,
                                 follow_redirects=False, ignore_response_code=True)
    if url.sucess or url.code == 302:
        if url.headers.get('location', ''):
            url = url.headers.get('location', '')
        elif url.json:
            url = url.json.get('url', '') or url.json.get('file', '')
        if '//api.cuevana3.me' in url:
            if not url.startswith('http'): url = "https:%s" % url
            domain = scrapertools.find_single_match(url, patron_domain)
            v_id = scrapertools.find_single_match(url, '\?h=(.*)')
            return get_urls(url, v_id, domain)

    if domain_fix in url:
        v_id = scrapertools.find_single_match(url, '\?h=(.*)')
        url = get_urls(url, v_id)

    return url