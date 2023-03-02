# -*- coding: utf-8 -*-
# -*- Channel SeriesFlix -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from channels import autoplay
from platformcode import logger, config
from channelselector import get_thumb
from lib.AlfaChannelHelper import ToroFlix


IDIOMAS = {"Latino": "LAT", "Castellano": "CAST", "Subtitulado": "VOSE"}
list_language = list(IDIOMAS.values())

list_servers = ['uqload', 'fembed', 'mixdrop', 'supervideo', 'mystream']

list_quality = []

canonical = {
             'channel': 'seriesflix', 
             'host': config.get_setting("current_host", 'seriesflix', default=''), 
             'host_alt': ["https://seriesflix.video/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
AlfaChannel = ToroFlix(host, tv_path="/series/", canonical=canonical)

domain = scrapertools.find_single_match(host, 'https*:\/\/(.*?)[\/|$]')


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Ultimas", action="list_all", url=host + "ver-series-online/",
                         thumbnail=get_thumb("last", auto=True), first=0))

    itemlist.append(Item(channel=item.channel, title="Productoras", action="section", url=host))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section", url=host,
                         thumbnail=get_thumb("genres", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Alfabetico", action="section", url=host,
                         thumbnail=get_thumb("alphabet", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + "?s=",
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item, postprocess=set_filter)


def section(item):
    logger.info()

    if item.title == "Generos":
        return AlfaChannel.section(item, section="genres")

    elif item.title == "Alfabetico":
        return AlfaChannel.section(item, section="alpha", action="list_alpha")

    else:
        return AlfaChannel.section(item, menu_id="1888")[:-1]


def list_alpha(item):
    logger.info()

    return AlfaChannel.list_alpha(item, postprocess=set_filter)


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

    soup, matches = AlfaChannel.get_video_options(item.url)

    for elem in matches:

        url = "%s?trembed=%s&trid=%s&trtype=2" % (host, elem["data-key"], elem["data-id"])
        server = elem.find("p", class_="AAIco-dns").text

        if server.lower() == "embed":
            server = "Mystream"
        lang = elem.find("p", class_="AAIco-language").text.split(' ')[1]
        qlty = elem.find("p", class_="AAIco-equalizer").text
        title = "%s [%s]" % (server, lang)

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='play',
                             language=IDIOMAS.get(lang, lang), quality=qlty, infoLabels=item.infoLabels,
                             server=server))

    #Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    #Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def play(item):
    logger.info()

    itemlist = list()

    url = AlfaChannel.create_soup(item.url).find("div", class_="Video").iframe["src"]

    if "streamcheck" in url or "//sc." in url:
        api_url = "%sstreamcheck/r.php" % host
        v_id = scrapertools.find_single_match(url, r"\?h=([A-z0-9]+)")
        post = {"h": v_id}
        url = httptools.downloadpage(api_url, post=post, ignore_response_code=True, proxy_retries=-0, 
                                     count_retries_tot=0, canonical=canonical).url

    itemlist.append(item.clone(url=url, server=""))
    itemlist = servertools.get_servers_itemlist(itemlist)
    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        if texto != '':
            item.url += texto
            item.first = 0
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def set_filter(*args):
    logger.info()

    args[2].context = filtertools.context(args[3], list_language, list_quality)

    return args[2]
