# -*- coding: utf-8 -*-

from inspect import trace
import sys, base64
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import time
if PY3:
    import urllib.parse as urlparse
else:
    import urlparse
from channelselector import get_thumb
from channels import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger


IDIOMAS = {'Latino': 'Latino'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['fembed', 'streamtape', 'fastplay', 'gvideo', 'Jawcloud']

__channel__='allcalidad'

canonical = {
             'channel': 'cuevana3video', 
             'host': config.get_setting("current_host", 'cuevana3video', default=''), 
             'host_alt': ["https://www8.cuevana3.ch/"], 
             'host_black_list': ["https://www10.cuevana3.ch/", 
                                 "https://www7.cuevana3.ch/", "https://www6.cuevana3.ch/", "https://www5.cuevana3.ch/", 
                                 "https://www4.cuevana3.ch/", "https://www3.cuevana3.ch/", "https://www2.cuevana3.ch/", 
                                 "https://www1.cuevana3.ch/", "https://cuevana3.ch/", "https://www1.cuevana3.fm/", 
                                 "https://cuevana3.fm/", "https://www1.cuevana3.vc/", "https://cuevana3.vc/", 
                                 "https://www2.cuevana3.pe/", "https://www1.cuevana3.pe/", "https://cuevana3.pe/", 
                                 "https://www2.cuevana3.cx/", "https://www1.cuevana3.cx/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

encoding = "utf-8"
__modo_grafico__ = config.get_setting('modo_grafico', __channel__, default=True)


def mainlist(item):
    logger.info()

    itemlist = []
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(
        Item(
            channel = item.channel,
            title = "Películas:"
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            action = "list_all",
            title = "     Estrenos",
            url = host + "estrenos",
            thumbnail = get_thumb('newest', auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            action = "list_all",
            title = "     Ultimas",
            url = host + "peliculas-mas-vistas",
            thumbnail = get_thumb('newest', auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            action="list_all",
            title = "     Películas",
            url = host + "peliculas",
            thumbnail = get_thumb('movie', auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            action = "generos",
            title = "     Por género",
            url = host,
            thumbnail = get_thumb('genere', auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            title = "Series:"
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            action = "last_episodes",
            title = "     Ultimos episodios",
            url = host + "serie",
            thumbnail = get_thumb('tvshow', auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            action = "last_tvshows",
            title = "     Ultimas series",
            url = host + "serie",
            type_tvshow = "tabserie-1",
            thumbnail = get_thumb('tvshow', auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            action = "last_tvshows",
            title = "     Mas vistas",
            url = host + "serie",
            type_tvshow = "tabserie-4",
            thumbnail = get_thumb('tvshow', auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            title = "Buscar",
            action = "search",
            url = host,
            thumbnail = get_thumb("search", auto = True)
        )
    )

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def last_episodes(item):
    logger.info()

    itemlist = []
    infoLabels = {}
    
    data = httptools.downloadpage(item.url, canonical=canonical).data
    bloque = scrapertools.find_single_match(data, 'Ultimos Episodios.*?</ul>')
    patron  = '(?is)<a href="([^"]+)'
    patron += '.*?src="([^"]+)'
    patron += '.*?"Title">([^<]+)'
    patron += '.*?<p>([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapeddate in matches:
        season, episode = scrapertools.get_season_and_episode(scrapedtitle).split("x")
        infoLabels = {"mediatype": "episode", "tvshowtitle": scrapertools.find_single_match(scrapedtitle, '(.*?) \d')}
        try:
            infoLabels["episode"] = int(episode)
            infoLabels["season"] = int(season)
        except:
            infoLabels["episode"] = 1
            infoLabels["season"] = 1

        itemlist.append(
            item.clone(
                action = "findvideos",
                channel = item.channel,
                infoLabels = infoLabels,
                thumbnail = "https://" + scrapedthumbnail,
                title = scrapedtitle.strip() + " %s" %scrapeddate,
                url = urlparse.urljoin(host, scrapedurl),
            )
        )

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    return itemlist


def last_tvshows(item):
    logger.info()

    itemlist = []
    url = item.url
    if not item.page: item.page = 1
    if not item.extra: url += "?page=%s" %item.page

    data = httptools.downloadpage(url, canonical=canonical).data
    bloque = scrapertools.find_single_match(data, 'id="%s".*?</ul>' %item.type_tvshow)
    patron  = '(?is)TPost C.*?<a href="([^"]+)'
    patron += '.*?src="([^"]+)'
    patron += '.*?"Title">([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        itemlist.append(
            item.clone(
                action = "seasons",
                channel = item.channel,
                contentSerieName = scrapedtitle.strip(),
                contentType = 'tvshow', 
                thumbnail = "https://" + scrapedthumbnail,
                title = scrapedtitle,
                url = urlparse.urljoin(host, scrapedurl)
            )
        )

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    item.page += 1
    url_pagina = scrapertools.find_single_match(data, 'page=%s' %item.page)

    if url_pagina != "":
        pagina = "Pagina: %s" %item.page

        itemlist.append(
            Item(
                channel = item.channel,
                action = "last_tvshows",
                page = item.page,
                title = pagina,
                type_tvshow = item.type_tvshow,
                url = item.url
            )
        )

    return itemlist


def seasons(item):
    logger.info()
    
    itemlist = []
    
    data = httptools.downloadpage(item.url, canonical=canonical).data
    
    patron  = '(?is)<option value="(\d+).*?>([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for _scrapedid, scrapedtitle in matches:
        try:
            scrapedid = int(_scrapedid)
        except:
            scrapedid = 1
        itemlist.append(
            item.clone(
                action = "episodesxseasons",
                contentType = 'season', 
                id = str(scrapedid),
                contentSeason = scrapedid, 
                title = scrapedtitle.strip()
            )
        )

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    itemlist = sorted(itemlist, key=lambda i: i.season)

    if config.get_videolibrary_support() and len(itemlist) > 0 and "serie" in item.url:
        itemlist.append(
            Item(
                action = "add_serie_to_library",
                channel = item.channel,
                contentSerieName = item.contentSerieName,
                extra = "episodios",
                text_color = 'yellow',
                title = 'Añadir esta serie a la videoteca',
                url = item.url
            )
        )

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

    itemlist = []
    infoLabels = item.infoLabels
    
    data = httptools.downloadpage(item.url, canonical=canonical).data
    
    bloque = scrapertools.find_single_match(data, 'season-%s.*?</ul>' %item.id)
    patron  = '(?is)<a href="([^"]+)'
    patron += '.*?src="([^"]+)'
    patron += '.*?"Title">([^<]+)'
    patron += '.*?<p>([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapeddate in matches:
        season, episode  = scrapertools.get_season_and_episode(scrapedtitle).split("x")
        infoLabels["mediatype"] = "episode"
        try:
            infoLabels["episode"] = int(episode)
            infoLabels["season"] = int(season)
        except:
            infoLabels["episode"] = 1
            infoLabels["season"] = 1

        itemlist.append(
            item.clone(
                channel = item.channel,
                action = "findvideos",
                episode = episode,
                infoLabels = infoLabels,
                title = scrapedtitle.strip(),
                thumbnail = scrapedthumbnail,
                url = urlparse.urljoin(host, scrapedurl)
            )
        )

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    itemlist = sorted(itemlist, key=lambda i: i.episode)

    return itemlist


def search(item, texto):
    logger.info()

    texto = texto.replace(" ", "+")
    item.url = host + "search.html?keyword=" + texto
    item.extra = "busca"

    if texto != '':
        try:
            return list_all(item)

        except Exception:
            import traceback
            logger.error(traceback.format_exc())

    else:
        return []


def list_all(item):
    logger.info()

    itemlist = []
    url = item.url
    if not item.page: item.page = 1
    if not item.extra: url += "?page=%s" %item.page

    data = httptools.downloadpage(url, encoding=encoding, canonical=canonical).data
    patron  = '(?is)TPost C.*?<a href="([^"]+)'
    patron += '.*?data-src="([^"]+)'
    patron += '.*?"Title">([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.entityunescape(scrapedtitle)
        item.infoLabels['year'] = "-"

        if "serie" in scrapedurl:
            itemlist.append(
                item.clone(
                    action = "seasons",
                    channel = item.channel,
                    contentSerieName = scrapedtitle.strip(),
                    contentType = 'tvshow', 
                    thumbnail = "https://" + scrapedthumbnail,
                    title = scrapedtitle,
                    url = urlparse.urljoin(host, scrapedurl),
                )
            )

        else:
            itemlist.append(
                item.clone(
                    action = "findvideos",
                    channel = item.channel,
                    contentType = "movie",
                    contentTitle = scrapedtitle.strip(),
                    thumbnail = "https://" + scrapedthumbnail,
                    title = scrapedtitle,
                    url = urlparse.urljoin(host, scrapedurl),
                )
            )

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    item.page += 1
    url_pagina = scrapertools.find_single_match(data, 'page=%s' %item.page)

    if url_pagina != "":
        pagina = "Pagina: %s" %item.page

        itemlist.append(
            Item(
                action = "list_all",
                channel = item.channel,
                page = item.page,
                title = pagina,
                url = item.url
            )
        )

    return itemlist


def findvideos(item):
    
    itemlist = []
    
    data = httptools.downloadpage(item.url, encoding=encoding, forced_proxy_opt='ProxyCF', canonical=canonical).data
    bloques = scrapertools.find_multiple_matches(data, '(?is)open_submenu .*?</ul>' )

    for scrapedblock in bloques:
        lang = scrapertools.find_single_match(scrapedblock, 'span>([^<]+)')
        matches = scrapertools.find_multiple_matches(scrapedblock, 'data-video="([^"]+).*?cdtr.*?span>([^<]+)')

        for scrapedurl, scrapedtitle in matches:
            #if  "peliscloud" in scrapedtitle.lower(): continue
            if not scrapedurl.startswith("http"): scrapedurl = "https:" + scrapedurl

            itemlist.append(
                item.clone(
                    action = "play",
                    language = lang,
                    server = "",
                    title = scrapedtitle,
                    url = scrapedurl
                )
            )

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if itemlist and item.contentChannel != "videolibrary":
        itemlist.append(
            item.clone(
                action = "buscartrailer",
                channel = "trailertools",
                text_color = "magenta",
                title = "Buscar Tráiler",
            )
        )

        # Opción "Añadir esta película a la videoteca"
        if config.get_videolibrary_support():
            itemlist.append(
                Item(
                    action = "add_pelicula_to_library",
                    channel = item.channel,
                    contentTitle = item.contentTitle,
                    text_color = "green",
                    thumbnail = item.thumbnail,
                    title = "Añadir a la videoteca",
                    url = item.url
                )
            )

    return itemlist


def play(item):
    logger.info()
    
    itemlist = []
    item.thumbnail = item.contentThumbnail
    item.url = item.url.replace("embedsito.com","fembed.com").replace("pelispng.online","fembed.com")

    if "pelisplay.cc" in item.url:
        data = httptools.downloadpage(item.url, headers={"Referer" : item.url}).data
        item.url = scrapertools.find_single_match(data, "file: '([^']+)")
        
    if "hydrax.net" in item.url:
        data = httptools.downloadpage(item.url, headers={"Referer" : item.url}).data
        v = scrapertools.find_single_match(item.url, 'v=(\w+)')
        post = "slug=%s&dataType=mp4"  %v
        data = httptools.downloadpage("https://ping.iamcdn.net/", post = post).data
        data = httptools.downloadpage("https://geoip.redirect-ads.com/?v=%s" %v, headers={"Referer" : item.url}).data
        
    if "damedamehoy" in item.url:
        item.url, id = item.url.split("#")
        new_url = "https://damedamehoy.xyz/details.php?v=%s" % id
        v_data = httptools.downloadpage(new_url).json
        item.url = v_data["file"]
        item.server = "directo"

    if "pelisplus.icu" in item.url:
        data = httptools.downloadpage(item.url).data
        item.url = scrapertools.find_single_match(data, "file: '([^']+)")

        if not item.url:
            item.url = scrapertools.find_single_match(data, '(?is)<iframe id="embedvideo" src="(https://[^"]+)')

    if "peliscloud.net" in item.url:
        dominio = urlparse.urlparse(item.url)[1]
        id = scrapertools.find_single_match(item.url, 'id=(\w+)')
        tiempo = int(time.time())
        item.url = "https://" + dominio + "/playlist/" + id + "/%s.m3u8" %tiempo
        data = httptools.downloadpage(item.url).data
        url = scrapertools.find_single_match(data, '/hls/\w+/\w+') + "?v=%s" %tiempo
        item.url = "https://" + dominio + url
        data = httptools.downloadpage(url).data
        item.server = "oprem"
        return ([item])

    if item.url:
        itemlist = servertools.get_servers_itemlist([item])

    return itemlist


def newest(categoria):
    logger.info()

    itemlist = []
    item = Item()

    try:
        if categoria in ['peliculas','latino']:
            item.url = host + "estrenos"

        elif categoria == 'infantiles':
            item.url = host + 'category/animacion/'

        elif categoria == 'terror':
            item.url = host + 'category/torror/'

        itemlist = list_all(item)

        if "Pagina" in itemlist[-1].title:
            itemlist.pop()

    except Exception:
        import traceback
        logger.error(traceback.format_exc())
        return []

    return itemlist


def generos(item):
    logger.info()

    itemlist = []
    
    data = httptools.downloadpage(item.url, encoding=encoding).data
    
    patron = '(?is)menu-item-object-category.*?<a href="([^"]+)'
    patron += '.*?">([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)

    for url, titulo in matches:
        if not url.startswith("http"): url = urlparse.urljoin(host, url)

        itemlist.append(
            Item(
                action = "list_all",
                channel = item.channel,
                extra = "generos",
                title = titulo,
                url = url
            )
        )

    return itemlist
