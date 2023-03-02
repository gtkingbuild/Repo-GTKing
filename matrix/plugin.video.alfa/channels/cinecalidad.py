# -*- coding: utf-8 -*-
# -*- Channel CineCalidad -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from builtins import map
from builtins import range

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    #from future import standard_library
    #standard_library.install_aliases()
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido

import re
import base64
from core import tmdb
from core import httptools
from core.item import Item
from core import servertools
from core import scrapertools
from bs4 import BeautifulSoup
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay

IDIOMAS = {'latino': 'Latino', 'castellano': 'Castellano', 'portugues': 'Portugues'}
list_language = list(IDIOMAS.values())
list_quality = ['1080p']
list_servers = ['gounlimited',
                'mega',
                'vidcloud',
                'torrent'
                ]

canonical = {
             'channel': 'cinecalidad', 
             'host': config.get_setting("current_host", 'cinecalidad', default=''), 
             'host_alt': ["https://cinecalidad.ms/"], 
             'host_black_list': ["https://cinecalidad.dev/", "https://www.cinecalidad.lat/", 
                                 "https://v3.cine-calidad.com/", "https://www5.cine-calidad.com/", "https://cinecalidad3.com/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

thumbmx = 'http://flags.fmcdn.net/data/flags/normal/mx.png'
thumbes = 'http://flags.fmcdn.net/data/flags/normal/es.png'
thumbbr = 'http://flags.fmcdn.net/data/flags/normal/br.png'

current_lang = ''

site_list = ['', '%s' % host, '%sespana/' % host, 'https://www.cinemaqualidade.im']
site = config.get_setting('filter_site', channel=canonical['channel'])
site_lang = '%s' % site_list[site]
sufix = ['', '', '?castellano=sp', '']


def mainlist(item):
    logger.info()

    itemlist = list()
    idioma2 = "destacadas"

    if site > 0:
        item.action = 'submenu'
        item.host = site_lang
        return submenu(item)

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(Item(channel=item.channel,
                         title="CineCalidad Latino",
                         action="submenu",
                         host=host,
                         site=1, 
                         thumbnail=thumbmx))

    itemlist.append(Item(channel=item.channel,
                         title="CineCalidad Castellano",
                         action="submenu",
                         host=host+'espana/',
                         site=2, 
                         thumbnail=thumbes))

    # itemlist.append(Item(channel=item.channel,
    #                      title="CineCalidad Portugues",
    #                      action="submenu",
    #                      host="https://www.cinemaqualidade.im",
    #                      thumbnail=thumbbr))

    itemlist.append(Item(channel=item.channel,
                         title="Configurar Canal...",
                         text_color="turquoise",
                         action="settingCanal",
                         thumbnail=get_thumb('setting_0.png'),
                         url='',
                         fanart=get_thumb('setting_0.png')
                         ))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def submenu(item):
    logger.info()
    global site, host
    
    idioma = 'peliculas'
    idioma2 = "destacada"
    host = item.host
    if item.site: site = item.site
    # if item.host == "https://www.cinemaqualidade.im":
    #     idioma = "filmes"
    #     idioma2 = "destacado"
    
    itemlist = []

    itemlist.append(Item(channel=item.channel,
                         title=idioma.capitalize(),
                         action="list_all",
                         url=host,
                         site=site, 
                         thumbnail=get_thumb('movies', auto=True),
                         ))
    if "/espana/" not in item.host:
        itemlist.append(Item(channel=item.channel,
                             title="Destacadas",
                             # action="featured",
                             action="list_all",
                             url=host + "peliculas-populares/",
                             site=site, 
                             thumbnail=get_thumb('hot', auto=True),
                             ))
        itemlist.append(Item(channel=item.channel,
                             title="Generos",
                             action="genres",
                             url=host,
                             site=site, 
                             thumbnail=get_thumb('genres', auto=True),

                             ))
        # itemlist.append(Item(channel=item.channel,
        #                      title="Por Año",
        #                      action="by_year",
        #                      url=host + idioma + "-por-ano",
        #                      thumbnail=get_thumb('year', auto=True),
        #                      ))
    itemlist.append(Item(channel=item.channel,
                         title="Buscar...",
                         action="search",
                         thumbnail=get_thumb('search', auto=True),
                         url=host + '?s=',
                         site=site, 
                         host=item.host,
                         ))
    if site > 0:
        autoplay.init(item.channel, list_servers, list_quality)

        itemlist.append(Item(channel=item.channel,
                             title="Configurar Canal...",
                             text_color="turquoise",
                             action="settingCanal",
                             thumbnail=get_thumb('setting_0.png'),
                             url='',
                             fanart=get_thumb('setting_0.png')
                             ))

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


# def featured(item):
    # logger.info()
    # itemlist = list()
    # soup = create_soup(item.url).find("div", class_="widget_movies")
    # matches = soup.find_all("a")

    # for elem in matches:
        # url = elem["href"]
        # if scrapertools.find_single_match(url, "\d+x\d+") or "episode" in url:
            # continue
        # title = elem["title"]
        # year = "-"
        # contentTitle = title.replace("(%s)" % year, "").strip()
        
        # itemlist.append(Item(channel=item.channel, title=contentTitle, contentTitle=contentTitle, url=url,
                             # action="findvideos", infoLabels={"year": year}))
        # tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url, unescape=True)
    #matches = soup.find_all("div", class_="home_post_cont")
    matches = soup.find_all("article")#, class_="relative group")
    #logger.debug(matches)
    
    for elem in matches:
        #url = scrapertools.find_single_match(elem.img.get("extract", ""), "href='([^']+)'")
        url = elem.a.get("href", "")
        if '/serie' in url: continue
        if sufix[item.site or 0] and sufix[item.site or 0] not in url:
            url += sufix[item.site or 0]
        
        if not url:
            continue
        try:
            title, year = elem.find('img', class_='w-full')["title"].split(' (')
            year = re.sub(r"\)","", year)
        except:
            title = elem.find('img', class_='w-full')["alt"]
            year = "-"

        thumb = re.sub(r'(-\d+x\d+.jpg)', '.jpg', elem.img["src"])
        if elem.p: 
            plot = elem.p.text
        else:
            plot = ''
        
        if scrapertools.find_single_match(url, "\d+x\d+") or "episode" in url:
            continue
        itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=thumb, action="findvideos",
                             plot=plot, contentTitle=title, infoLabels={'year': year}))
    tmdb.set_infoLabels_itemlist(itemlist, True)

    ## Pagination ##

    try:
        next_page = soup.find("span", {"aria-current": True}).find_next_sibling()["href"]
        #logger.debug(next_page)
        itemlist.append(Item(channel=item.channel,  action="list_all",  title="Página siguiente >>",
                             url=next_page, language=item.language ))
    except:
        pass

    return itemlist


def by_year(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url, unescape=True).find("div", class_="yearlist")
    for elem in soup.find_all('a'):
        url = elem["href"]
        title = elem.text
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all", search=True))

    return itemlist


def genres(item):
    logger.info()

    itemlist = list()

    #soup = create_soup(item.url, unescape=True).find("ul", id="menu-menu")
    soup = create_soup(item.url, unescape=True).find("ul", id="close-menu")
    matches = soup.find_all("a")
    for elem in matches:

        url = elem["href"]
        title = elem.text

        if "series" in title.lower() or "peliculas" in title.lower():
            continue

        if not url.startswith('http'):
            url = item.url +url
        
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all"))

    return itemlist


def settingCanal(item):
    from platformcode import platformtools
    platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return


def findvideos(item):
    logger.info()
    itemlist = list()

    srv_ids = {"Dood": "Doodstream",
               "Watchsb": "Streamsb",
               "Maxplay": "voe",
               "1fichier": "Onefichier",
               "Latmax": "Fembed"}

    soup = create_soup(item.url)
    try:
        strm_links = soup.find("ul", class_="options").find_all("a")

        for lnk in strm_links:
            try:
                url = base64.b64decode(lnk["data-src"]).decode('utf-8')
                srv = lnk.text.strip().capitalize()
                if srv in ["Cineplay", "Netu", "Trailer"]:
                    continue
                if srv in srv_ids:
                    srv = srv_ids[srv]
                itemlist.append(Item(channel=item.channel, url=url, title=srv, action="play", infoLabels=item.infoLabels))
            except:
                pass

        dl_links = soup.find("ul", class_="links").find_all("a")
        for lnk in dl_links:
            try:
                url = base64.b64decode(lnk["data-url"]).decode('utf-8')
                srv = lnk.text.strip().capitalize()
                if srv in ["Cineplay", "Netu"]:
                    continue
                if srv in srv_ids:
                    srv = srv_ids[srv]
                itemlist.append(Item(channel=item.channel, url=url, title=srv, action="play", infoLabels=item.infoLabels,
                                     is_dl=True))
            except:
                pass
    except:
        pass

    return itemlist


def play(item):
    logger.info()

    if item.is_dl:
        item.url = create_soup(item.url).find("div", id="btn_enlace").a["href"]
    else:
        item.url = create_soup(item.url).find("iframe")["src"]

    itemlist = servertools.get_servers_itemlist([item])

    return itemlist


def get_urls(item, link):
    logger.info()
    url = '%s/ccstream/ccstream.php' % host
    headers = dict()
    headers["Referer"] = item.url
    post = 'link=%s' % link

    dict_data = httptools.downloadpage(url, post=post, headers=headers, canonical=canonical).json
    return dict_data['link']


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria in ['peliculas', 'latino']:
            item.url = host
        elif categoria == 'infantiles':
            item.url = '%sinfantil/' % host
        elif categoria == 'terror':
            item.url = '%sterror/' % host
        elif categoria == 'castellano':
            item.url = '%sespana/' % host
        itemlist = list_all(item)
        if itemlist[-1].title == 'Página siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []
    texto = texto.replace(" ", "-")

    item.url = host + '?s=' + texto
    if texto != '':
        itemlist.extend(list_all(item))

    return itemlist