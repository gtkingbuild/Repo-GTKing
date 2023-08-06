# -*- coding: utf-8 -*-
# -*- Channel Estreno Doramas -*-
# -*- Created for Alfa-addon -*-
# -*- By the BDamian (Based on channels from Alfa Develop Group) -*-

from builtins import map
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from modules import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core import jsontools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channelselector import get_thumb
import ast

import time
import base64

import requests
import re
import struct

IDIOMAS = {'Latino': 'LAT', 'Vo':'VO', 'Vose': 'VOSE'}
IDIOMA = "no filtrar"
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['openload', 'streamango', 'netutv', 'okru', 'mp4upload']

canonical = {
             'channel': 'estrenosdoramas', 
             'host': config.get_setting("current_host", 'estrenosdoramas', default=''), 
             'host_alt': ["https://www25.estrenosdoramas.net/"], 
             'host_black_list': [ "https://www24.estrenosdoramas.net/", "https://www23.estrenosdoramas.net/"], 
             'pattern': '<link\s*rel="shortcut\s*icon"\s*href="([^"]+)"', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

source_headers = dict()
source_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
source_headers["X-Requested-With"] = "XMLHttpRequest"
source_headers["Origin"] = "https://repro3.estrenosdoramas.us"

PATRON_REGEX = "\('([^']+)','([^\']?(?:\\.|[^\'])*)','([^\']?(?:\\.|[^\'])*)','([^\']?(?:\\.|[^\'])*)'"
PLAYER_SRC = 'test'


def set_player_src(player_src):
    # logger.info(player_src)
    global PLAYER_SRC
    PLAYER_SRC = player_src


def decrypt(data, index=0):
    
    index += 1

    matches = re.compile(PATRON_REGEX, re.DOTALL) .findall(str(data))

    log = 'Matches (%s): (%s)'%(index, len(matches))
    logger.info(log)
    # logger.info(data)
    if len(matches) > 0:
        for w,i,s,e in matches:
            if not i and not s and not e:
                secret = decodeone(w)
            else:
                # logger.info(str(data))
                secret = decode(w,i,s,e)
                if "jwplayer" in secret:
                    logger.info('player found')
                    secret = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", secret)
                    set_player_src(secret)
                    # logger.info(data1)
            decrypt(secret, index)
    # else:
    #     logger.info(str(data))
    
    return


def utf16_decimals(char):
    # encode the character as big-endian utf-16
    encoded_char = char.encode('utf-16-be')

    # convert every 2 bytes to an integer
    decimals = []
    for i in range(0, len(encoded_char), 2):
        chunk = encoded_char[i:i+2]
        decimals.append(struct.unpack('>H', chunk)[0])

    return decimals


def decode(w, i, s, e):
    lIll = 0
    ll1I = 0
    Il1l = 0
    ll1l = []
    l1lI = []

    while len(w) + len(i) + len(s) + len(e) != len(ll1l) + len(l1lI) + len(e):
        if lIll < 5: 
            l1lI.append(w[lIll])
        elif lIll < len(w):
            ll1l.append(w[lIll])
        lIll += 1

        if ll1I < 5:
            l1lI.append(i[ll1I])
        elif ll1I < len(i):
            ll1l.append(i[ll1I])
        ll1I += 1

        if Il1l < 5:
            l1lI.append(s[Il1l])
        elif Il1l < len(s):
            ll1l.append(s[Il1l])
        Il1l += 1

    lI1l = ''.join(ll1l)
    I1lI = ''.join(l1lI)
    ll1I = 0
    l1ll = []

    for i in range(0,len(ll1l),2):
        lIll = i
        ll11 = -1
        nchar = utf16_decimals(I1lI[ll1I])[0]
        if nchar % 2:
            ll11 = 1
        l1ll.append( str(chr(int(lI1l[lIll:lIll+2], 36) - ll11)) )
        ll1I += 1
        if ll1I == len(l1lI): 
            ll1I = 0
        
    return ''.join(l1ll)


def decodeone(w):
    i = ''
    for s in range(0,len(w),2):
        i +=  str(chr(int(w[s:s+2], 36))) 
    return i


def get_source(url, referer=None):
    logger.info()
    if referer is None:
        data = httptools.downloadpage(url, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, headers={'Referer':referer}, canonical=canonical).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    return data


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(Item(channel= item.channel, title="Doramas", action="list_all",
                         url=host + 'category/doramas-online',
                         thumbnail=get_thumb('doramas', auto=True), type='dorama'))

    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all",
                         url=host + 'category/peliculas',
                         thumbnail=get_thumb('movies', auto=True), type='movie'))
    
    itemlist.append(Item(channel=item.channel, title="Últimos capítulos", action="list_all",
                         url=host + 'category/ultimos-capitulos-online',
                         thumbnail=get_thumb('doramas', auto=True), type='movie'))

    itemlist.append(Item(channel=item.channel, title="Por Genero", action="menu_generos",
                         url=host,
                         thumbnail=get_thumb('doramas', auto=True), type='dorama'))

    itemlist.append(Item(channel=item.channel, title="Doblado Latino", action="list_all",
                         url=host + 'category/latino',
                         thumbnail=get_thumb('doramas', auto=True), type='dorama'))

    itemlist.append(Item(channel=item.channel, title = 'Buscar', action="search", url= host+'search/',
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def menu_generos(item):
    logger.info()

    data = get_source(item.url)
    data = scrapertools.find_single_match(data, '<div id="genuno">(.*?)</div>')
    
    itemlist = []

    patron = '<li><a.*?href="(.*?)">(.*?)</a>.*?</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    media_type = item.type
    for scrapedurl, scrapedtitle in matches:
        new_item = Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, 
                        thumbnail=item.thumbnail, type=item.type, action="list_all")
        itemlist.append(new_item)

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = get_source(item.url)
    data = scrapertools.find_single_match(data, '<h3 class="widgetitulo">Resultados</h3>.*?<div id="(?:sidebar|footer)-wrapper">')
    
    patron = '<div.*?<a href="(.*?)"><img src="(.*?)" alt="(.*?)".*?</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = re.sub('^Pelicula ', '', scrapedtitle)
        new_item = Item(channel=item.channel, title=title, url=scrapedurl,
                        thumbnail=scrapedthumbnail)
        if scrapedtitle.startswith("Pelicula") or item.type == "movie":
            new_item.action = 'findvideos'
            new_item.contentTitle = title
        elif 'capitulo' in scrapedurl:
            new_item.contentSerieName=scrapedtitle
            new_item.action = 'findvideos'
        else:
            new_item.contentSerieName=scrapedtitle
            new_item.action = 'episodios'
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    # Paginacion
    patron = '<a class="nextpostslink" rel="next" aria-label="Next Page" href="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if matches:
        itemlist.append(Item(channel=item.channel, action="list_all", title='Siguiente >>>',
                             url=matches[0], type=item.type))
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    data = get_source(item.url)

    plot_regex = '(<span class="clms"><b>Nombre.*?)<\/div>'
    plot_match = re.compile(plot_regex, re.DOTALL).findall(data)
    if plot_match:
        plot = scrapertools.htmlclean(plot_match[0].replace('<br />', '\n'))
    
    data = scrapertools.find_single_match(data, '<ul class="lcp_catlist".*?</ul>')
    patron = '<a href="([^"]+)">([^<]+)</a>'
    
    matches = re.compile(patron, re.DOTALL).findall(data)
    infoLabels = item.infoLabels

    for scrapedurl, scrapedtitle in matches:
        scrapedep = scrapertools.find_single_match(scrapedtitle.lower(), "capitulo (\d+)")
        if item.url == scrapedurl:
            continue
        url = scrapedurl        
        contentEpisodeNumber = scrapedep
        if contentEpisodeNumber == "":
            title = '1xEE - ' + scrapedtitle
        else:
            title = '1x' + ("0" + contentEpisodeNumber)[-2:] + " - " + scrapedtitle
            # title = ("0" + contentEpisodeNumber)[-2:]

        infoLabels['season'] = 1
        infoLabels['episode'] = contentEpisodeNumber
        infoLabels = item.infoLabels

        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, plot=plot,
                             contentEpisodeNumber=contentEpisodeNumber, type='episode', infoLabels=infoLabels))

    itemlist.sort(key=lambda x: x.title)
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            item.clone(title="Añadir esta serie a la videoteca", action="add_serie_to_library", extra="episodios", text_color='yellow'))
    return itemlist

def findvideos(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)
    data = scrapertools.find_single_match(data, '<div id="marco-post">.*?<div id="sidebar">')
    data = scrapertools.unescape(data)
    data = scrapertools.decodeHtmlentities(data)
    
    options_regex = '<a href="#tab.*?">.*?<b>(.*?)</b>'
    option_matches = re.compile(options_regex, re.DOTALL).findall(data)

    video_regex = '<iframe.*?src="(.*?)".*?</iframe>'
    video_matches = re.compile(video_regex, re.DOTALL).findall(data)

    # for option, scrapedurl in matches:
    # for option, scrapedurl in map(None, option_matches, video_matches):
    for option, scrapedurl in zip(option_matches, video_matches):
        if scrapedurl is None:
            continue
        
        scrapedurl = scrapedurl.replace('"','').replace('&#038;','&')

        try:
            data_video = get_source(scrapedurl)
        except Exception as e:
            logger.info('Error en url: ' + scrapedurl)
            continue
        
        # logger.info(data_video)

        # Este sitio pone multiples páginas intermedias, cada una con sus reglas.
        source_headers = dict()
        source_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        source_headers["X-Requested-With"] = "XMLHttpRequest"
        # logger.info("{0}: {1}".format(option, scrapedurl))
        if scrapedurl.find("https://repro") != 0:
            logger.info("Caso 0: url externa")
            url = scrapedurl
            itemlist.append(Item(channel=item.channel, title=option, url=url, action='play', language=IDIOMA))
        elif scrapedurl.find("pi76823.php") > 0:
            logger.info("Caso 1")
            source_data = get_source(scrapedurl)
            source_regex = 'post\( "(.*?)", { key: \'(.*?)\''
            source_matches = re.compile(source_regex, re.DOTALL).findall(source_data)
            for source_page, source_key in source_matches:
                base_url = scrapedurl.rsplit('/', 1)[0] + '/'
                source_headers["Origin"] = base_url
                source_url = base_url + source_page
                # logger.info(source_key)
                token_get = str(int(round(time.time())))
                token = base64.b64encode(token_get.encode("utf-8"))
                source_result = httptools.downloadpage(source_url, post='key=' + source_key 
                                                    + '&token=' + str(token), headers=source_headers)
                source_json = source_result.json
                if source_json.get("link", ''):
                    video_url = base64.b64decode(source_json["link"])
                    # logger.info(video_url)
                    itemlist.append(Item(channel=item.channel, title=option, url=video_url, 
                                         action='play', language=IDIOMA))
        elif scrapedurl.find("pi7.php") > 0:
            logger.info("Caso 2")
            source_data = get_source(scrapedurl)
            logger.info(scrapedurl)

            global PLAYER_SRC
            PLAYER_SRC = ''
            decrypt(source_data)
            if PLAYER_SRC:
                # logger.info(PLAYER_SRC)
                source_regex = 'post\(\s?"(.*?)",\s?{\s?key: \'(.*?)\''
                source_matches = re.compile(source_regex, re.DOTALL).findall(PLAYER_SRC)
                # logger.info(source_data)
                for source_page, source_key in source_matches:
                    base_url = scrapedurl.rsplit('/', 1)[0] + '/'
                    source_headers["Origin"] = base_url
                    source_url = base_url + source_page
                    # logger.info(source_key)
                    token_get = str(int(round(time.time())))
                    token = base64.b64encode(token_get.encode("utf-8"))
                    source_result = httptools.downloadpage(source_url, post='key=' + source_key 
                                                        + '&token=' + str(token), headers=source_headers)
                    source_json = source_result.json
                    if source_json.get("link", ''):
                        video_url = base64.b64decode(source_json["link"])
                        # logger.info(video_url)
                        itemlist.append(Item(channel=item.channel, title=option, url=video_url, 
                                            action='play', language=IDIOMA))
        elif scrapedurl.find("reproducir120.php") > 0:
            logger.info("Caso 3")
            source_data = get_source(scrapedurl)

            videoidn = scrapertools.find_single_match(source_data, 'var videoidn = \'(.*?)\';')
            tokensn = scrapertools.find_single_match(source_data, 'var tokensn = \'(.*?)\';')
            
            source_regex = 'post\( "(.*?)", { acc: "(.*?)"'
            source_matches = re.compile(source_regex, re.DOTALL).findall(source_data)
            for source_page, source_acc in source_matches:
                source_url = scrapedurl[0:scrapedurl.find("reproducir120.php")] + source_page
                source_result = httptools.downloadpage(source_url, post='acc=' + source_acc + '&id=' + 
                                                       videoidn + '&tk=' + tokensn, headers=source_headers)
                if source_result.code == 200:
                    source_json = jsontools.load(source_result.data)
                    urlremoto_regex = "file:'(.*?)'"
                    urlremoto_matches = re.compile(urlremoto_regex, re.DOTALL).findall(source_json['urlremoto'])
                    if len(urlremoto_matches) == 1:
                        itemlist.append(Item(channel=item.channel, title=option, url=urlremoto_matches[0], action='play', language=IDIOMA))
        elif scrapedurl.find("reproducir14.php") > 0:
            logger.info("Caso 4")
            source_data = get_source(scrapedurl)
            
            source_regex = '<div id="player-contenido" vid="(.*?)" name="(.*?)"'
            source_matches = re.compile(source_regex, re.DOTALL).findall(source_data)
            videoidn = source_matches[0][0]
            tokensn = source_matches[0][1]
            
            source_regex = 'post\( "(.*?)", { acc: "(.*?)"'
            source_matches = re.compile(source_regex, re.DOTALL).findall(source_data)
            for source_page, source_acc in source_matches:
                source_url = scrapedurl[0:scrapedurl.find("reproducir14.php")] + source_page
                source_result = httptools.downloadpage(source_url, post='acc=' + source_acc + '&id=' + 
                                                       videoidn + '&tk=' + tokensn, headers=source_headers)
                if source_result.code == 200:
                    source_json = jsontools.load(source_result.data)
                    if source_json.get('urlremoto', ''): 
                        itemlist.append(Item(channel=item.channel, title=option, url=source_json['urlremoto'], action='play', language=IDIOMA))
        else:
            logger.info("Caso nuevo")      

    itemlist = servertools.get_servers_itemlist(itemlist)

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
    itemlist = []
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    item.type = 'search'
    if texto != '':
        try:
            return list_all(item)
        except:
            itemlist.append(item.clone(url='', title='No hay elementos...', action=''))
            return itemlist