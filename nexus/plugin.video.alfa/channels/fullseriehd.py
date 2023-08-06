# -*- coding: utf-8 -*-
# -*- Channel FullSerieHD -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
import traceback

from channels import filtertools
from bs4 import BeautifulSoup
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import tmdb
from modules import autoplay
from platformcode import config, logger
from channelselector import get_thumb
from lib import generictools


IDIOMAS = {'Subtitulado': 'VOSE', 'Latino':'LAT', 'Castellano':'CAST'}
list_language = list(IDIOMAS.values())
list_servers = ['okru', 'fembed', 'gvideo', 'mega']
list_quality = ['HD-1080p', 'HD-720p', 'Cam']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'fullseriehd', 
             'host': config.get_setting("current_host", 'fullseriehd', default=''), 
             'host_alt': ["https://megaxserie.me/"], 
             'host_black_list': ["https://megaserie.me/", "https://megaserie.net/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'CF_stat': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def create_soup(url, referer=None, post=None, unescape=False):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={'Referer':referer}, canonical=canonical).data
    if post:
        data = httptools.downloadpage(url, post=post, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data

    data = generictools.js2py_conversion(data, url, domain_name='', canonical=canonical)

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html.parser", from_encoding="utf-8")

    return soup

def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu',
                         thumbnail=get_thumb('movies', auto=True), type='movies'))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu',
                         thumbnail=get_thumb('tvshows', auto=True), type='series'))
                         
    itemlist.append(Item(channel=item.channel, title="Por Año", action="year",
                             thumbnail=get_thumb("year", auto=True) ))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + '?s=',
                         thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Novedades", action="list_all", 
                         url=host + item.title.lower() + '/',
                         thumbnail=get_thumb("newest", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section", url=host,
                         thumbnail=get_thumb("genres", auto=True), type=item.type))

    # itemlist.append(Item(channel=item.channel, title="Alfabetico", action="section", url=host,
                         # thumbnail=get_thumb("alphabet", auto=True), type=item.type))
    return itemlist


def list_all(item):
    logger.info()
    itemlist = list()

    if item.type:
        item.url += '?type=%s' % item.type
    soup = create_soup(item.url)
    matches = soup.find("div", id="movies-a")

    if not matches:
        return itemlist

    for elem in matches.find_all("article"):
        language = []
        year = ''
        url = elem.a["href"]
        title = fix_title(elem.h2.text)
        year = elem.find('span', class_='year')
        try:
            thumb = re.sub(r'-\d+x\d+.jpg', '.jpg', elem.find("img")["data-src"])
        except:
            thumb = elem.find("img")["src"]
        if not thumb.startswith("https"):
            thumb = "https:%s" % thumb
        if year:
            year = year.text.strip()
        if not "/series/" in url:
            lang = elem.find("span", class_="lang")
            if lang:
                lang = lang.find_all('img')
                for leng in lang:
                    lang = leng['src']
                    if "United-States" in lang: lang= "VOSE"
                    if "Mexico" in lang: lang= "LAT"
                    if "Spain" in lang: lang= "CAST"
                    language.append(lang)
            try:
                quality = ''
                quality = elem.find("span", class_="Qlty").text
            except:
                pass

        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, infoLabels={"year": year})

        if "/series/" in url:
            new_item.contentSerieName = title
            new_item.action = "seasons"
            new_item.contentType = 'tvshow'
        else:
            new_item.contentTitle = title
            new_item.action = "findvideos"
            new_item.contentType = 'movie'
            new_item.quality = quality
            if language:
                new_item.language = language

        itemlist.append(new_item)
        
    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        next_page = soup.find_all("a", string="SIGUIENTE")[0]['href']
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action='list_all'))
    except:
        pass

    return itemlist


def year(item):
    import datetime
    logger.info()

    itemlist = list()
    
    now = datetime.datetime.now()
    c_year = now.year + 1
        
    l_year = c_year - 21
    year_list = list(range(l_year, c_year))

    for year in year_list:
        year = str(year)
        url = '%srelease/%s/' % (host, year)
            
        itemlist.append(Item(channel=item.channel, title=year, url=url,
                                 action="list_all"))
    itemlist.reverse()
    return itemlist


def section(item):
    logger.info()
    import string

    itemlist = list()

    if item.title == "Generos":
        soup = create_soup(item.url).find("li", id="menu-item-89")
        try:
            for elem in soup.find_all("li"):
                url = elem.a["href"]
                title = elem.a.text
                itemlist.append(Item(channel=item.channel, title=title, action="list_all",
                                     url=url, type=item.type))
        except:
            logger.error(traceback.format_exc())
            logger.error(soup)

    elif item.title == "Alfabetico":
        url = '%sletter/0-9/?tr_post_type=%s' % (host, item.type)
        itemlist.append(Item(channel=item.channel, title='#', action="alpha_list",
                                 url=url, type=item.type))

        for l in string.ascii_uppercase:
            url = '%sletter/%s/?tr_post_type=%s' % (host, l.lower(), item.type)
            title = l
            itemlist.append(Item(channel=item.channel, title=title, action="alpha_list",
                                 url=url, type=item.type))

    return itemlist


def alpha_list(item):
    logger.info()

    itemlist = list()
    
    data = create_soup(item.url)
    soup = data.find("tbody")
    
    if not soup:
        return itemlist
    for elem in soup.find_all("tr"):
        info = elem.find("td", class_="MvTbTtl")
        thumb = elem.find("td", class_="MvTbImg").a.img["src"]
        url = info.a["href"]
        title = info.a.text.strip()
        
        year = ''
        quality = ''
        if '/pelicula/' in url:
            quality = elem.find("span", class_="Qlty").text
            try:
                year = elem.find("td", text=re.compile(r"\d{4}")).text
            except:
                pass            

        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, infoLabels={"year": year})

        if '/pelicula/' in url:
            new_item.contentTitle = title
            new_item.action = "findvideos"
            new_item.quality = quality
            new_item.contentType = 'movie'
        else:
            new_item.contentSerieName = title
            new_item.action = "seasons"
            new_item.contentType = 'tvshow'

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        next_page = data.find("a", class_="next page-numbers")["href"]
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action='list_all'))
    except:
        pass

    return itemlist


def seasons(item):
    logger.info()
    
    itemlist = list()
    infoLabels = item.infoLabels
    
    soup = create_soup(item.url).find_all("li", class_="sel-temp")
    
    for elem in soup:
        season = elem.a["data-season"]
        id = elem.a["data-post"]
        title = "Temporada %s" % season
        try:
            infoLabels["season"] = int(season)
        except:
            infoLabels["season"] = 1
        
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseason', id=id, 
                             infoLabels=infoLabels, contentType='season'))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0 and not item.extra:
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_serie_to_library",
                             extra="episodios",
                             contentSerieName=item.contentSerieName
                             ))
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
    infoLabels = item.infoLabels
    season = infoLabels["season"]
    url= "%swp-admin/admin-ajax.php" % host
    post = {'action': 'action_select_season', 'season': season, 'post': item.id}
    
    soup = create_soup(url, post=post).find_all('article')
    
    for elem in soup:
        url = elem.a["href"]
        try:
            cap = int(elem.find("span", class_="num-epi").text.split('x')[1])
        except:
            cap = 1
        if cap < 10:
            cap = "0%s" % cap
        title = "%sx%s" % (season, cap)
        title = "%sx%s" % (season, cap)
        infoLabels["episode"] = cap
        
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                             infoLabels=infoLabels, contentType='episode'))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0 and not item.extra and season == 1:
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_serie_to_library",
                             extra="episodios",
                             contentSerieName=item.contentSerieName
                             ))
    return itemlist


def findvideos(item):
    logger.info()
    
    itemlist = list()
    
    data = create_soup(item.url)
    try:
        video_urls = data.find("aside", class_="video-player").find_all('iframe')
        info = data.find("aside", class_="video-options").find_all('li')
    except:
        try:
            video_urls = data.find("tbody").find_all('a', class_="btn sm rnd blk")
            for video_url in video_urls:
                item.url = video_url['href']
                break
            else:
                logger.error(video_urls)
                return itemlist
            return findvideos_acorta(item)
        except:
            logger.error(traceback.format_exc())
            logger.error(item.url)
            logger.error(data)
            return itemlist
    
    for url, info in zip(video_urls, info):
        try:
            url = url['data-src']
            info = info.find('span', class_='server').text.split('-')
            srv = info[0].strip()
            lang = info[1].strip()
            infoLabels = item.infoLabels
            lang = IDIOMAS.get(lang, lang)
            # quality = info[1]
            quality = ""
            itemlist.append(Item(channel=item.channel, title=srv, url=url, action='play', server=srv, opt="1",
                                infoLabels=infoLabels, language=lang, quality=quality))
        except:
            logger.error(traceback.format_exc())
            logger.error(url)
            logger.error(info)
    
    # downlist = get_downlist(item, data)  #DESCARGAS ACORTADOR
    # itemlist.extend(downlist)
    
    itemlist = sorted(itemlist, key=lambda i: (i.language, i.server))

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos' and not item.contentSerieName:
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))
    return itemlist


def findvideos_acorta(item):
    logger.info()
    from lib.generictools import convert_url_base64
    
    itemlist = list()
    infoLabels = item.infoLabels
    
    try:
        url = convert_url_base64(item.url)
        data = create_soup(url)
        info = data.find("ul", class_="tabs").find_all('li')
        video_urls = data.find_all("div", class_="tab_content")
    except:
        logger.error(traceback.format_exc())
        logger.error(item.url)
        logger.error(data)
        return itemlist

    for info_block, url_block in zip(info, video_urls):
        info = info_block.div.text.replace('Espanol', 'Castellano')
        lang = info.split(' ')[0]
        quality = info.replace(lang, '').strip()
        lang = IDIOMAS.get(lang, lang)

        for url_acorta in url_block.find_all('a'):
            try:
                url = url_acorta.text

                itemlist.append(Item(channel=item.channel, title='%s', url=url, action='play', 
                                    infoLabels=infoLabels, language=lang, quality=quality))
            except:
                logger.error(traceback.format_exc())
                logger.error(info_block)
                logger.error(url_block)
        
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())
    
    return itemlist


def play(item):
    logger.info()
    
    itemlist = list()
    
    if not item.opt:
        if host in item.url:
            item.url = httptools.downloadpage(item.url, ignore_response_code=True).url
        
        itemlist.append(item.clone(url=item.url, server=item.server or ''))
        if not item.server: itemlist = servertools.get_servers_itemlist(itemlist)
        
        return itemlist
    
    url = create_soup(item.url).find("div", class_="Video").iframe["src"]
    if 'Gdri.php' in url:
        url = scrapertools.find_single_match(url, 'v=([A-z0-9-_=]+)')
        url = 'https://drive.google.com/file/d/%s/preview' % url
    
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


def get_downlist(item, data):
    import base64
    logger.info()
    
    downlist = list()
    servers = {'drive': 'gvideo', '1fichier': 'onefichier'}
    
    soup = data.find("tbody")
    
    if soup:
        soup = soup.find_all("tr")
        infoLabels = item.infoLabels
        for tr in soup:
            burl = tr.a["href"].split('#')[1]
            try:
                for x in range(7):
                    durl = base64.b64decode(burl).decode('utf-8')
                    burl = durl
            except:
                url = burl
            info = tr.find_all('td')
            srv = info[0].text.split()[1]
            srv = servers.get(srv, srv)
            lang = info[1].text
            lang = IDIOMAS.get(lang, lang)
            quality = info[2].text
            
            downlist.append(Item(channel=item.channel, title=srv, url=url, action='play', server=srv,
                                infoLabels=infoLabels, language=lang, quality=quality))
    return downlist

