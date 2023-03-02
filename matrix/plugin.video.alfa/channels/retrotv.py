# -*- coding: utf-8 -*-
# -*- Channel RetroTV -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from channels import filtertools
from core import scrapertools
from core import servertools
from core import jsontools
from core.item import Item
from channels import autoplay
from lib.AlfaChannelHelper import ToroPlay
from platformcode import logger, config
from channelselector import get_thumb

list_idiomas = ['LAT']
list_servers = ['okru', 'yourupload', 'mega', 'direct']
list_quality = []

canonical = {
             'channel': 'retrotv', 
             'host': config.get_setting("current_host", 'retrotv', default=''), 
             'host_alt': ["https://retrotv.org/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
AlfaChannel = ToroPlay(host, tv_path="/tv", canonical=canonical)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Todas las Series", action="list_all",
                         url=host + "lista-series/", thumbnail=get_thumb("all", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Animación", action="list_all",
                         url=host + "category/animacion/", thumbnail=get_thumb("animacion", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Live Action", action="list_all",
                         url=host + "category/liveaction/", thumbnail=get_thumb("tvshows", auto=True)))
    
    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all",
                         url=host + "peliculas/", thumbnail=get_thumb("movies", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section", url=host,
                         thumbnail=get_thumb("genres", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Alfabetico", action="section", url=host,
                         thumbnail=get_thumb("alphabet", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url= host + "?s=",
                         thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item)


def section(item):
    logger.info()

    if item.title == "Generos":
        return AlfaChannel.section(item, menu_id="2460")
    elif item.title == "Alfabetico":
        return AlfaChannel.section(item, section="alpha", action="list_alpha")


def list_alpha(item):
    logger.info()

    return AlfaChannel.list_alpha(item)


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item)


def episodesxseason(item):
    logger.info()

    return AlfaChannel.episodes(item)


def episodios(item):
    logger.info()

    itemlist = list()
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    opt = ''
    srv = ''
    
    # soup = create_soup(item.url).find("ul", class_="TPlayerNv").find_all("li")
    soup, matches = AlfaChannel.get_video_options(item.url)

    infoLabels = item.infoLabels

    for btn in matches:
        opt = btn["data-tplayernv"]
        srv = btn.span.text.lower()
        if "opci" in srv.lower() or not srv:
            # srv = "okru"
            continue
        itemlist.append(Item(channel=item.channel, title=srv, url=item.url, action='play', server=srv, opt=opt,
                             language='LAT', infoLabels=infoLabels))

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_idiomas, list_quality)

    if not itemlist:
        trtype = 1 if item.contentType == 'movie' else '2'
        patron = '<link\s*href="([^"]+)"\s*rel="shortlink"\s*\/>'
        matches = re.compile(patron, re.DOTALL).findall(str(soup))
        if not matches:
            patron = '<div\s*class="TPlayerTb\s*Current"[^>]*>\s*<iframe[^>]*src="([^"]+)"'
            matches = re.compile(patron, re.DOTALL).findall(str(soup))

        for btn in matches:
            if not 'trid' in btn:
                trid = scrapertools.find_single_match(btn, '\?p=(\d+)')
                url = '%s?trembed=0&trid=%s&trtype=%s' % (host, trid, trtype)
            else:
                url = btn.replace('amp;', '')
            
            link = AlfaChannel.create_soup(url, referer=item.url).find("div", class_="Video").iframe["src"]
            srv = 'directo'
            
            itemlist.append(Item(channel=item.channel, title=srv, url=link, action='play', server=srv, opt=opt,
                                 language='LAT', infoLabels=infoLabels))

    itemlist = sorted(itemlist, key=lambda i: i.server)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    return itemlist


def play(item):
    logger.info()
    
    itemlist = list()
    url = item.url
    server = item.server
    
    if item.server != 'directo':

        soup = AlfaChannel.create_soup(item.url).find("div", class_="TPlayerTb", id=item.opt)
        
        url = scrapertools.find_single_match(str(soup), 'src="([^"]+)"')
        url = re.sub("amp;|#038;", "", url)
        
        url = AlfaChannel.create_soup(url).find("div", class_="Video").iframe["src"]
        if 'mega.' in url:
            url = url.replace("/embed/", "/file/")
            server = ''
    else:
        soup = AlfaChannel.create_soup(item.url).find("body", class_="videoplayer")
        
        json = {}
        base = scrapertools.find_single_match(str(soup), 'sources\:\[([^\]]+\})\]')
        if base: json = jsontools.load(base)
        if not json and str(soup).startswith('{'): 
            json = jsontools.load(str(soup))
            if 'sources' in json.keys():
                json = json.get('sources', [])[0]
        
        url = json.get('file', '')
        if not url:
            url = scrapertools.find_single_match(str(soup), 'ajax\(\{url\:"([^"]+)"')
            if not url:
                return itemlist
        if url and not url.startswith('http'):
            url = 'https:%s' % url
            
        resp = AlfaChannel.create_soup(url, referer=item.url, soup=False)
        if PY3 and isinstance(resp.data, bytes):
            resp.data = "".join(chr(x) for x in bytes(resp.data))
        if resp.json:
            json = resp.json
            if 'sources' in json.keys():
                json = json.get('sources', [])[0]
            url = json.get('file', '')
            if url and not url.startswith('http'):
                url = 'https:%s' % url
            
            resp = AlfaChannel.create_soup(url, referer=item.url, soup=False)
            if PY3 and isinstance(resp.data, bytes):
                resp.data = "".join(chr(x) for x in bytes(resp.data))
        
        matches = re.compile('QUALITY=(\w+),[^\/]+(\/\/[^\n]+)', re.DOTALL).findall(resp.data)
        matches.reverse()
        for quality, _url in matches:
            if len(matches) > 1 and quality == 'mobile': continue
            url = _url
            break
        if not url:
            return itemlist
        if not url.startswith('http'):
            url = 'https:%s' % url
        server = "oprem"
        
    itemlist.append(item.clone(url=url, server=server, title=item.title.capitalize()))
    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    
    try:
        texto = texto.replace(" ", "+")
        if texto != '':

            item.url += texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

