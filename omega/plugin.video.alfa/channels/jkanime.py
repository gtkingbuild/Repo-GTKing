# -*- coding: utf-8 -*-

from __future__ import division
from builtins import range
from past.utils import old_div
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import logger, config

canonical = {
             'channel': 'jkanime', 
             'host': config.get_setting("current_host", 'jkanime', default=''), 
             'host_alt': ["https://jkanime.net/"], 
             'host_black_list': [], 
             'pattern': '<meta\s*property="og:url"\s*content="([^"]+)"', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host


def mainlist(item):
    logger.info()
    itemlist = list()
    itemlist.append(Item(channel=item.channel, thumbnail=get_thumb("tvshows", auto=True), action="ultimas_series", title="Últimas Series", url=host))
    itemlist.append(Item(channel=item.channel, thumbnail=get_thumb("new episodes", auto=True),action="ultimos_episodios", title="Últimos Episodios", url=host))
    itemlist.append(Item(channel=item.channel, thumbnail=get_thumb("alphabet", auto=True),action="p_tipo", title="Listado Alfabetico", url=host, list_type="letras"))
    itemlist.append(Item(channel=item.channel, thumbnail=get_thumb("genres", auto=True),action="p_tipo", title="Listado por Genero", url=host, list_type="generos"))
    itemlist.append(Item(channel=item.channel, thumbnail=get_thumb("search", auto=True),action="search", title="Buscar"))
    return itemlist


def ultimas_series(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = scrapertools.find_single_match(data, '(?is)Últimos Animes agregados</h4>.*?<div class="col-lg-4 col-md-6 col-sm-8 trending_div">')
    patron  = '(?is)data-setbg="(.+?)".*?'
    patron += '<a  href="([^"]+)".*?'
    patron += '>(.+?)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=item.channel, action="episodios", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                 show=scrapedtitle))
    tmdb.set_infoLabels(itemlist)
    return itemlist


def search(item, texto):
    logger.info()
    if item.url == "":
        item.url = host + "buscar/%s/"
    texto = texto.replace(" ", "+")
    item.url = item.url % texto
    try:
        return series(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def ultimos_episodios(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = '<a href="([^"]+)" class="bloqq">.+?\n.+?\n.+?<img src="([^"]+)".+?title="([^"]+)"'
    patron += '.+?\n.+?\n.+?\n.+?\n.+?h6>.+?\n.+?(\d+).+?</'            # url
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedepisode in matches:
        title = "{} - Episodio {}".format(scrapedtitle, scrapedepisode)
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=scrapedurl, thumbnail=scrapedthumbnail,
                 show=scrapedtitle))
    tmdb.set_infoLabels(itemlist)
    return itemlist


def p_tipo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    if item.list_type == "letras":
        data = scrapertools.find_single_match(data, '<div class="letras-box addmenu">(.*?)</ul>')
        patron  = 'class="letra-link" href="([^"]+)".*?'
        patron += '>([^<]+)</a>'
    elif item.list_type == "generos":
        data = scrapertools.find_single_match(data, 'Animes por Genero(.*?)</ul>')
        patron  = 'href="([^"]+)".*?'
        patron += '>([^<]+)</a>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=item.channel, action="series", title=scrapedtitle, url="{}{}".format(host, scrapedurl),
                 viewmode="movie_with_plot"))
    return itemlist


def series(item):
    logger.info()
    # Descarga la pagina
    data = httptools.downloadpage(item.url, canonical=canonical).data
    # Extrae las entradas
    # patron  = '<a title="([^"]+)" href="([^"]+)" rel="nofollow">.*?'
    # patron += 'src="([^"]+)".*?'
    # patron += 'eps-num">([^<]+)</span>.*?'
    # patron += '<p>([^\<]+)</p>'
    patron = 'class="anime__item">\s+?<a  href="(.+?)".+?'  # url
    patron += 'data-setbg="(.+?)".+?'                       # thumb
    patron += 'class="ep".*?>(\d+).+?'                      # epnum
    patron += 'class="title".*?>(.+?)</.+?'                 # title
    patron += 'p>(.+?)</'                                   # plot
    matches = scrapertools.find_multiple_matches(data, patron)
    itemlist = []
    for scrapedurl, scrapedthumbnail, scrapedepisode, scrapedtitle, scrapedplot in matches:
        title = "{} ({})".format(scrapedtitle, scrapedepisode)
        # scrapedthumbnail = scrapedthumbnail.replace("thumbnail", "image")
        plot = scrapertools.htmlclean(scrapedplot)
        itemlist.append(Item(channel=item.channel, action="episodios", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail,
                 plot=scrapedplot, show=scrapedtitle))
    tmdb.set_infoLabels(itemlist)
    try:
        siguiente = scrapertools.find_single_match(data, '<a class="text nav-next" href="([^"]+)"')
        scrapedurl = siguiente
        scrapedtitle = ">> Pagina Siguiente"
        scrapedthumbnail = ""
        scrapedplot = ""
        if len(itemlist)>0:
            itemlist.append(
                Item(channel=item.channel, action="series", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                     plot=scrapedplot, viewmode="movie_with_plot"))
    except:
        pass
    return itemlist


def get_pages_and_episodes(data):
    results = scrapertools.find_multiple_matches(data, 'href="#pag([0-9]+)".*?>[0-9]+ - ([0-9]+)')
    if results:
        return int(results[-1][0]), int(results[-1][1])
    return 1, 0


def episodios(item):
    logger.info()
    itemlist = []
    # Descarga la pagina
    data = httptools.downloadpage(item.url, canonical=canonical).data
    scrapedplot = scrapertools.find_single_match(data, '<meta name="description" content="([^"]+)"/>')
    scrapedthumbnail = scrapertools.find_single_match(data, '<div class="separedescrip">.*?src="([^"]+)"')
    idserie = scrapertools.find_single_match(data, "ajax/pagination_episodes/(\d+)/")
    logger.info("idserie=" + idserie)
    if " Eps" in item.extra and "Desc" not in item.extra:
        caps_x = item.extra
        caps_x = caps_x.replace(" Eps", "")
        capitulos = int(caps_x)
        paginas = old_div(capitulos, 10) + (capitulos % 10 > 0)
    else:
        paginas, capitulos = get_pages_and_episodes(data)
    for num_pag in range(1, paginas + 1):
        numero_pagina = str(num_pag)
        headers = {"Referer": item.url}
        data2 = httptools.downloadpage(host + "ajax/pagination_episodes/%s/%s/" % (idserie, numero_pagina),
                                        headers=headers, canonical=canonical).data
        patron = '"number"\:"(\d+)","title"\:"([^"]+)"'
        matches = scrapertools.find_multiple_matches(data2, patron)
        for numero, scrapedtitle in matches:
            try: int(numero.strip())
            except: pass
            infoLabels = item.infoLabels
            infoLabels["season"] = 1
            infoLabels["episode"] = numero
            title = scrapedtitle.strip()
            url = item.url + numero
            plot = scrapedplot
            itemlist.append(item.clone(action="findvideos", infoLabels=infoLabels, title=title, url=url, plot=plot))
    if len(itemlist) == 0:
        try:
            itemlist.append(Item(channel=item.channel, action="findvideos", title="Serie por estrenar", url="",
                                 thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot,
                                 server="directo", folder=False))
        except:
            pass
    tmdb.set_infoLabels(itemlist, True)
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    aux_url = []
    serv_dict = {'jkfembed': 'https://feurl.com/v/',
                'jk': '%s' % host,
                'jkvmixdrop': 'https://mixdrop.co/e/',
                'jkokru': 'https://ok.ru/videoembed/'
                }
    data = httptools.downloadpage(item.url, canonical=canonical).data
    list_videos = scrapertools.find_multiple_matches(data, '\'<iframe.*? src="([^"]+)"')
    list_down = scrapertools.find_multiple_matches(data, "blank\" href='(.*?)'>Descargar")
    index = 1
    for e in list_videos:
        if e.startswith(host + "jk") or "um.php" in e:
            if "um.php?" in e or "jk.php" in e or "jkokru.php" in e or "jkfembed.php" in e:
                headers = {"Referer": item.url}
                data = httptools.downloadpage(e, headers=headers).data
                url = scrapertools.find_single_match(data, "url: '([^']+)',")
                if not url:
                    url = scrapertools.find_single_match(data, 'src="([^"]+)')
            else:
                serv, hash_ = scrapertools.find_single_match(e, r'%s/(\w+).php\?u=(.*)' % host)
                serv = serv_dict.get(serv, serv)
                url = serv + hash_

            if host in url:
                url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get("location", "")

            if url:
                itemlist.append(item.clone(title="Enlace encontrado en server #" + str(index) + " (%s)", url=url, action="play"))
                index += 1
        else:
            aux_url.append(item.clone(title="Enlace encontrado (%s)", url=e, action="play"))
    
    for d in list_down:
        aux_url.append(item.clone(title="Enlace encontrado (%s)", url=d, action="play"))
    itemlist.extend(aux_url)
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    for videoitem in itemlist:
        videoitem.contentTitle = item.contentTitle
        videoitem.channel = item.channel
        videoitem.thumbnail = item.thumbnail
    return itemlist

# def btoa(s):
#     import base64
#     return base64.b64encode(s.to_string().value)
    
# def decode_url(data):
#     from lib import js2py
#     import re
#     data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
#     js = scrapertools.find_single_match(data, '<script>(l.*?)</script>')
    
#     part = js.split("+ll")
#     part0 = part[1].split("String['fromCharCode'")[0]
#     part1 = part[1].replace(part0, "")
#     part1 = re.sub(r'(l.*?)\(\(\[', 'window.btoa(([', part1)
#     context = js2py.EvalJs({ "btoa": btoa });
#     url = "htt%s" % context.eval(part1)
#     logger.info(url)
#     return url
