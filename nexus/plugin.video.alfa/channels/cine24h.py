# -*- coding: utf-8 -*-
# -*- Channel Cine24H -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from bs4 import BeautifulSoup
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import tmdb
from modules import autoplay
from platformcode import config, logger
from channelselector import get_thumb

canonical = {
             'channel': 'cine24h', 
             'host': config.get_setting("current_host", 'cine24h', default=''), 
             'host_alt': ["https://cine24h.online/"], 
             'host_black_list': ["https://cine24h.net/"], 
             'pattern': '<link\s*rel="icon"\s*href="([^"]+)"', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

host_lang = config.get_setting('host_lang', channel='cine24h')

if host_lang > 0:
    dom_dict = {1: 'esp.', 2: 'sub.'}
    dom = dom_dict.get(host_lang, '')
    host = re.sub(r'(\w+.\w{2,4}/)', '%s\\1' % dom, host)


IDIOMAS = {'LAT': 'LAT', 'ESP': 'CAST', 'SUB': 'VOSE'}
list_language = list(IDIOMAS.values())
list_servers = ['fembed', 'mystream', 'uptobox', 'gounlimited']
list_quality = ['720HD']



def settingCanal(item):
    from platformcode import platformtools
    platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ''

def create_soup(url, referer=None, unescape=False):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={'Referer':referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html.parser", from_encoding="utf-8")

    return soup

#Las series están principalmente en Netu, se elimina la opcion

def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()


    itemlist.append(Item(channel=item.channel, title="Novedades", action="list_all", 
                         url=host + 'peliculas/',
                         thumbnail=get_thumb("newest", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Más Vistas", action="list_all", 
                         url=host + 'peliculas-mas-vistas/',
                         thumbnail=get_thumb("more watched", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Mejor Valoradas", action="list_all", 
                         url=host + 'peliculas-mas-valoradas/',
                         thumbnail=get_thumb("more voted", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section", url=host,
                         thumbnail=get_thumb("genres", auto=True), type=1))

    itemlist.append(Item(channel=item.channel, title="Por Año", action="section", url=host,
                         thumbnail=get_thumb("year", auto=True), type=1))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + '?s=',
                         thumbnail=get_thumb("search", auto=True)))

    
    itemlist.append(Item(channel=item.channel,
                         title="Configurar Canal...",
                         text_color="turquoise",
                         action="settingCanal",
                         thumbnail=get_thumb('setting_0.png'),
                         url=''
                         ))

    autoplay.show_option(item.channel, itemlist)


    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()
    # year = ''
    # quality = '720HD'
    # language = "LAT"
    
    if item.type:
        item.url += '?tr_post_type=%s' % item.type
    
    soup = create_soup(item.url)
    matches = soup.find("ul", class_="MovieList NoLmtxt Rows AX A06 B04 C03 E20")

    if not matches:
        return itemlist

    for elem in soup.find_all("article"):

        url = elem.a["href"]
        if '/serie/' in url:
            continue
        
        title = fix_title(elem.a.h3.text)
        thumb = re.sub(r'/w\d+/', '/original/', elem.find("img")["src"])
        
        if thumb.startswith('//'):
            thumb = 'https:%s' % thumb
        
        try:
            info = elem.find_all("span")[:3]
            year = info[0].text
            quality = info[1]["class"][1].replace("sprite-", '')

            lang = info[2].div["class"][1].replace("sprite-", '')
            language = IDIOMAS.get(lang, lang)
        
        #pelicula sin enlances
        except:
            continue

        itemlist.append(Item(channel=item.channel, title=title, url=url,
                            contentTitle = title, action = "findvideos",
                            quality = quality, language = language,
                            thumbnail=thumb, infoLabels={"year": year}))

        

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        next_page = soup.find("a", class_="next page-numbers")["href"]
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action='list_all'))
    except:
        pass

    return itemlist


def section(item):
    logger.info()
    import string

    itemlist = list()
    soup = create_soup(item.url).find_all("ul", class_="sub-menu")
    if item.title == "Generos":
        soup = soup[1]
        for elem in soup.find_all("li"):
            url = elem.a["href"]
            title = elem.a.text
            itemlist.append(Item(channel=item.channel, title=title, action="list_all",
                                 url=url, type=item.type))

    elif item.title == "Por Año":
        soup = soup[0]
        for elem in soup.find_all("li"):
            url = elem.a["href"]
            title = elem.a.text
            itemlist.append(Item(channel=item.channel, title=title, action="list_all",
                                 url=url, type=item.type))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    infoLabels = item.infoLabels
    servers = {'upto': 'uptobox', 'gou': 'gounlimited', 'fmd': 'fembed', 'msm': 'mystream'}
    
    data = create_soup(item.url)
    soup = data.find("ul", class_="TPlayerNv")
    
    if not soup:
        return itemlist

    for btn in soup.find_all("li"):
        opt = btn["data-tplayernv"]
        
        srv = btn.span.text.lower()[:-1]
        server = servers.get(srv, srv)
        
        info = btn.span.findNext('span').text.split(' - ')
        lang = IDIOMAS.get(info[0], info[0])
        quality = info[1]

        itemlist.append(Item(channel=item.channel, title=srv, url=item.url, action='play', server=server, opt=opt,
                            infoLabels=infoLabels, language=lang, quality=quality))
    
    itemlist = sorted(itemlist, key=lambda i: (i.language, i.server))

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos' and not item.contentSerieName:
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist


def play(item):
    logger.info()
    itemlist = list()

    soup = create_soup(item.url).find("div", class_="TPlayerTb", id=item.opt)
    surl = scrapertools.find_single_match(str(soup), 'src="([^"]+)"')
    url = get_url(surl)
    
    itemlist.append(item.clone(url=url, server=""))
    
    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        if texto != '':
            item.url += texto
            return list_all(item)
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def fix_title(title):
    title = re.sub(r'\((.*)', '', title)
    title = re.sub(r'\[(.*?)\]', '', title)
    return title

def get_url(url):
    url = re.sub("amp;|#038;", "", url)
    url = re.sub("trembed=", "trdownload=", url)
    url = httptools.downloadpage(url, only_headers=True).url
    return url

