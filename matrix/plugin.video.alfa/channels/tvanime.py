# -*- coding: utf-8 -*-
# -*- Channel TVAnime -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int

import re
import base64

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from channels import filtertools, autoplay
from core import tmdb
from modules import renumbertools
from platformcode import platformtools

canonical = {
             'channel': 'tvanime', 
             'host': config.get_setting("current_host", 'tvanime', default=''), 
             'host_alt': ["https://monoschinos2.com/"], 
             'host_black_list': [], 
             'pattern': '<meta\s*property="og:url"\s*content="([^"]+)"', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

IDIOMAS = {'VOSE': 'VOSE', 'Latino': 'LAT', 'Castellano': 'CAST'}

epsxfolder = config.get_setting('epsxfolder', canonical['channel'])
list_epsxf = {0: None, 1: 25, 2: 50, 3: 100}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['directo', 'fembed', 'streamtape', 'uqload', 'okru', 'streamsb']


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    
    itemlist.append(Item(channel=item.channel, title="Nuevos Episodios",
                         action="new_episodes",
                         thumbnail=get_thumb('new_episodes', auto=True),
                         url=host))

    itemlist.append(Item(channel=item.channel, title="Ultimas",
                               action="list_all",
                               thumbnail=get_thumb('last', auto=True),
                               url=host + 'emision'))

    itemlist.append(Item(channel=item.channel, title="Todas",
                               action="list_all",
                               thumbnail=get_thumb('all', auto=True),
                               url=host + 'animes'))

    itemlist.append(Item(channel=item.channel, title="Anime",
                              action="list_all",
                              thumbnail=get_thumb('anime', auto=True),
                              url=host + 'animes?categoria=anime'))

    itemlist.append(Item(channel=item.channel, title="Donghua",
                         action="list_all",
                         thumbnail='',
                         url=host + 'animes?categoria=donghua'))

    itemlist.append(Item(channel=item.channel, title="Películas",
                         action="list_all",
                         thumbnail=get_thumb('movies', auto=True),
                         url=host + 'animes?categoria=pelicula'))

    itemlist.append(Item(channel=item.channel, title="OVAs",
                              action="list_all",
                              thumbnail='',
                              url=host + 'animes?categoria=ova'))

    itemlist.append(Item(channel=item.channel, title="ONAs",
                              action="list_all",
                              thumbnail='',
                              url=host + 'animes?categoria=ona'))

    itemlist.append(Item(channel=item.channel, title="Especiales",
                              action="list_all",
                              thumbnail='',
                              url=host + 'animes?categoria=especial'))

    itemlist.append(Item(channel=item.channel, title="A - Z",
                         action="section",
                         thumbnail=get_thumb('alphabet', auto=True),
                         url=host + 'animes',
                         section="letra"))

    itemlist.append(Item(channel=item.channel, title="Generos",
                         action="section",
                         thumbnail=get_thumb('genres', auto=True),
                         url=host + 'animes',
                         section="genero"))

    itemlist.append(Item(channel=item.channel, title="Buscar",
                               action="search",
                               url=host + 'buscar?q=',
                               thumbnail=get_thumb('search', auto=True),
                               fanart='https://s30.postimg.cc/pei7txpa9/buscar.png'
                               ))

    itemlist.append(Item(channel=item.channel,
                             title="Configurar Canal...",
                             text_color="turquoise",
                             action="settingCanal",
                             thumbnail=get_thumb('setting_0.png'),
                             url='',
                             fanart=get_thumb('setting_0.png')
                             ))

    autoplay.show_option(item.channel, itemlist)
    itemlist = renumbertools.show_option(item.channel, itemlist)

    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    from bs4 import BeautifulSoup

    if referer:
        data = httptools.downloadpage(url, headers={'Referer':referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def new_episodes(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find_all("div", class_="col col-md-6 col-lg-2 col-6")

    for elem in matches:
        url = elem.a["href"]
        lang, c_title = clear_title(elem.a["title"])
        c_title = re.sub('(?i)1080p|720p|movie', '', c_title).strip()
        try:
            season = int(scrapertools.find_single_match(c_title, '(?i)\s*(\d+)\s*(?:st|nd|rd|th)\s+season'))
            c_title = re.sub('(?i)\s*\d+\s*(?:st|nd|rd|th)\s+season', '', c_title)
        except:
            season = 1
        try:
            epi = int(elem.p.text)
        except:
            epi = 1
        title = "%sx%s - %s" % (season, epi, c_title)
        thumb = elem.img["src"]

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             thumbnail=thumb, contentSerieName=c_title, language=lang,
                             contentSeason=season, contentEpisodeNumber=epi, contentType='episode'))

    tmdb.set_infoLabels_itemlist(itemlist, True)
    
    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find_all("div", class_="col-md-4 col-lg-2 col-6")

    for elem in matches:
        url = elem.a["href"]
        lang, title = clear_title(elem.a.get("title", '') or elem.find("h3", class_="seristitles").text)
        title = re.sub('(?i)1080p|720p|movie|ovas|ova|onas|ona|especiales|especial|specials|special', '', title).strip()
        thumb = elem.img["src"]

        context = renumbertools.context(item)

        if 'pelicula' in item.url:
            itemlist.append(Item(channel=item.channel, title=title, url=url, action='folders', context=context,
                                 language=lang, thumbnail=thumb, contentTitle=title, contentType='movie',
                                 infoLabels={'year': '-'}))
        else:
            itemlist.append(Item(channel=item.channel, title=title, url=url, action='folders', context=context,
                                 language=lang, thumbnail=thumb, contentSerieName=title, contentType='tvshow'))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find("a", rel="next")["href"]
        if url_next_page and len(itemlist) > 8:
            itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all'))
    except:
        pass

    return itemlist


def section(item):

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("select", {"name": "%s" % item.section}).find_all("option")

    for elem in matches[1:]:

        url = host + "animes?categoris=anime&%s=%s" % (item.section, elem["value"])
        title = elem["value"].capitalize()
        
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all"))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = list()

    templist = folders(item)

    for tempitem in templist:
        if tempitem.infoLabels["episode"]:
            itemlist = templist
            break
        itemlist += episodesxfolder(tempitem)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find_all("p", class_="play-video")

    for elem in matches:
        url = base64.b64decode(elem["data-player"]).decode("utf-8")

        itemlist.append(Item(channel=item.channel, title='%s', url=url, action='play',
                             language=item.language, infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def search(item, texto):
    logger.info()
    
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    
    try:
        if texto != '':
            return list_all(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    
    itemlist = []
    item = Item()
    
    if categoria == 'anime':
        item.url = host
        itemlist = new_episodes(item)
    
    return itemlist


def settingCanal(item):

    platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return


def clear_title(title):
    
    if 'latino' in title.lower():
        lang = 'Latino'
    elif 'castellano' in title.lower():
        lang = 'Castellano'
    else:
        lang = 'VOSE'

    title = re.sub(r'Audio|Latino|Castellano|\((.*?)\)', '', title)
    title = re.sub(r'\s:', ':', title)

    return lang, title


def folders(item):
    logger.info()

    itemlist = list()

    exf = list_epsxf.get(epsxfolder, None)
    if not epsxfolder:
        return episodesxfolder(item)

    soup = create_soup(item.url)
    matches = soup.find_all("div", {"data-episode": True})

    l_matches = len(matches)

    if l_matches <= exf:
        return episodesxfolder(item)
    div = l_matches // exf
    res = l_matches % exf
    tot_div = div

    count = 1
    for folder in list(range(0, tot_div)):
        final = (count * exf)
        inicial = (final - exf) + 1
        if count == tot_div:
            final = (count * exf) + res

        title = "Eps %s - %s" % (inicial, final)
        init = inicial - 1
        itemlist.append(Item(channel=item.channel, title=title, url=item.url,
                             action='episodesxfolder', init=init, fin=final, type=item.type,
                             thumbnail=item.thumbnail, foldereps=True))
        count += 1

    if item.contentSerieName != '' and config.get_videolibrary_support() and len(
            itemlist) > 0 and not item.extra == "episodios":
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName,
                 extra1='library'))

    return itemlist


def episodesxfolder(item):
    logger.info()

    itemlist = list()

    if not item.init:
        item.init = None
    if not item.fin:
        item.fin = None

    soup = create_soup(item.url)
    matches = soup.find_all("div", {"data-episode": True})

    infoLabels = item.infoLabels

    for elem in matches[item.init:item.fin]:
        scrapedurl = elem.a["href"]
        episode = scrapertools.find_single_match(scrapedurl, '.*?episodio-(\d+)')
        lang = item.language
        try:
            season, episode = renumbertools.numbered_for_tratk(item.channel, item.contentSerieName, 1, int(episode))
            season = int(season)
            episode = int(episode)
        except:
            season = 1
            episode = 1
        title = "%sx%s - %s" % (season, str(episode).zfill(2), item.contentSerieName)
        url = scrapedurl
        infoLabels['season'] = season
        infoLabels['episode'] = episode

        itemlist.append(Item(channel=item.channel, title=title, contentSerieName=item.contentSerieName, url=url,
                             action='findvideos', language=lang, infoLabels=infoLabels, contentType='episode'))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    if not item.extra:
        if item.contentSerieName != '' and config.get_videolibrary_support() and len(itemlist) > 0 and not item.foldereps:
            itemlist.append(
                Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                     action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName,
                     extra1='library'))

    return itemlist
