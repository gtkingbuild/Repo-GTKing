# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

import re
import base64

from core import httptools
from core import jsontools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from modules import autoplay
from platformcode import config, logger


IDIOMAS = {'default': 'VO'}
title2 = {'Action': 'Action2','Xmas':'Christmas', 'Kungfu':'Martial%20Arts','Psychological':'Genres','TV Show':'TV', 'Sitcom':'Genres', 'Costume':'Genres', 'Mythological':'Genres'}
list_language = list(IDIOMAS.values())
list_servers = ['directo', 'xstreamcdn']
list_quality = ['default']

canonical = {
             'channel': 'watchseries', 
             'host': config.get_setting("current_host", 'watchseries', default=''), 
             'host_alt': ["http://watchmovie.ac/"], 
             'host_black_list': ["https://watchmovie.cc/"], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = []

    itemlist.append(item.clone(title="Películas", action='menu_movies', text_color="0xFFD4AF37", text_bold=True, thumbnail= "https://github.com/master-1970/resources/raw/master/images/genres/0/Directors%20Chair.png"))
    itemlist.append(item.clone(title='Series', action='menu_series', thumbnail= "https://github.com/master-1970/resources/raw/master/images/genres/0/TV%20Series.png",  text_color="0xFFD4AF37", text_bold=True))
    itemlist.append(
        item.clone(title="Buscar...", action="search", text_color="0xFF5AC0E0", text_bold=True, url=host + 'search.html?keyword=', thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Search.png"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist

def menu_movies(item):
    logger.info()

    itemlist=[]

    itemlist.append(Item(channel=item.channel, text_color="0xFF5AC0E0", text_bold=True, title="Estrenos", fanart="http://i.imgur.com/c3HS8kj.png", action="novedades_cine", url=host, thumbnail="https://github.com/master-1970/resources/raw/master/images/genres/0/New%20Releases.png"))
    itemlist.append(
        Item(channel=item.channel, text_color="0xFF5AC0E0", text_bold=True, title="Más Vistas", action="popular", url=host + "popular", extra="popular", thumbnail="https://github.com/master-1970/resources/raw/master/images/genres/0/All%20Movies%20by%20Watched.png"))
    itemlist.append(Item(channel=item.channel, text_color="0xFFD4AF37", text_bold=True,  title="Géneros", action="section", url=host + "popular", thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Genres.png"))
    itemlist.append(Item(channel=item.channel, text_color="0xFFD4AF37", text_bold=True,  title="Año", action="section", url=host + "popular", thumbnail="https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Year.png"))

    return itemlist

def menu_series(item):
    logger.info()

    itemlist=[]
    itemlist.append(Item(channel=item.channel, text_color="0xFF399437", text_bold=True, action="novedades_episodios", title="Últimos Episodios de:", folder=False, thumbnail=item.thumbnail))
    itemlist.append(Item(channel=item.channel, text_color="0xFF5AC0E0", text_bold=True, action="novedades_episodios", title="   Series Tv", url=host + "watch-series", extra= "watch-series", thumbnail='https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/New%20TV%20Episodes.png', type='tvshows'))
    itemlist.append(Item(channel=item.channel, text_color="0xFF5AC0E0", text_bold=True, action="novedades_episodios", title="   Doramas", url=host + "drama", extra= "drama", thumbnail='https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Asian%20Movies.png', type='tvshows'))
    itemlist.append(Item(channel=item.channel, text_color="0xFF5AC0E0", text_bold=True, action="novedades_episodios", title="   Animes", url=host + "anime", extra= "anime", thumbnail='https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Anime.png', type='anime'))

    return itemlist

def search(item, texto):
    logger.info()
    itemlist = []
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    if texto != '':
        try:
            return popular(item)
        except:
            itemlist.append(item.clone(url='', title='No match found...', action=''))
            return itemlist

def section(item):
    logger.info()
    data = httptools.downloadpage(item.url, canonical=canonical).data
    itemlist = []
    if 'Géneros' in item.title:
        patron = '<a href="([^"]+)" class="wpb_button  wpb_btn-primary wpb_btn-small ">(.*?)</a>'
        action = 'popular'
        icono = ''
    elif 'Año' in item.title:
        patron = '<a href="([^"]+)" class="wpb_button  wpb_btn-info wpb_btn-small ">(.*?)</a>'
        action = 'popular'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:

        url = host + scrapedurl
        title = scrapedtitle
        if 'Géneros' in item.title:
            if title in title2:
                title1 = title2[title]
            else:
                title1 = title
            icono = 'https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/'+ title1 +'.png'
        else:
            icono = 'https://raw.githubusercontent.com/master-1970/resources/master/images/genres/0/Year.png'
        itemlist.append(Item(channel=item.channel,
                             action=action,
                             title=title,
                             url=url,
                             text_color="0xFF5AC0E0",
                             extra="popular",
                             thumbnail = icono
                             ))
    return itemlist

def novedades_episodios(item):
    logger.info()
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url_pagination = scrapertools.find_single_match(data, "<li class='next next page-numbers'><a href='(.*?)'")
    matches = re.compile('<div class="video_likes icon-tag"> (.*?)</div>[\s\S]+?<a href="(.*?)" class="view_more"></a>[\s\S]+?<img src="([^"]+)" alt="" class="imgHome" title="" alt="([^"]+)"[\s\S]+?</li>', re.DOTALL).findall(data)
    itemlist = []
    for episode, url, thumbnail,season in matches:

        if item.extra == "watch-series":
            scrapedinfo = season.split(' - ')
            scrapedtitle = scrapedinfo[0]
            season = scrapertools.find_single_match(scrapedinfo[1], 'Season (\d+)')
            episode = scrapertools.find_single_match(episode, 'Episode (\d+)')
            title = scrapedtitle + " %sx%s" % (season, episode)
        else:
            scrapedtitle = season
            title = scrapedtitle + ' - ' + episode
        url = urlparse.urljoin(host, url)

        new_item = Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                        contentSerieName=scrapedtitle,)
        itemlist.append(new_item)
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True, idioma_busqueda='en')
    if url_pagination:
        url = urlparse.urljoin(host +  item.extra, url_pagination)
        title = ">> Pagina Siguiente"
        itemlist.append(Item(channel=item.channel, action="novedades_episodios", title=title, url=url, extra=item.extra))
    return itemlist


def novedades_cine(item):
    logger.info()
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url_pagination = scrapertools.find_single_match(data, "<li class='next next page-numbers'><a href='(.*?)'")
    matches = re.compile('<div class="video_likes icon-tag"> (.*?)</div>[\s\S]+?<a href="(.*?)" class="view_more"></a>[\s\S]+?<img src="([^"]+)" alt="" class="imgHome" title="" alt="([^"]+)"[\s\S]+?</li>', re.DOTALL).findall(data)
    itemlist = []
    for episode, url, thumbnail,season in matches:
        scrapedyear = '-'
        title = "%s [%s]" % (season, episode)
        url = urlparse.urljoin(host, url)
        new_item = Item(channel=item.channel, action="findvideos",title=title, url=url, contentTitle=season, thumbnail=thumbnail,infoLabels={'year':scrapedyear})
        itemlist.append(new_item)
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True, idioma_busqueda='en')
    if url_pagination:
        url = urlparse.urljoin(host + item.extra, url_pagination)
        title = ">> Pagina Siguiente"
        itemlist.append(Item(channel=item.channel, action="novedades_cine", title=title, url=url))
    return itemlist

def popular(item):
    logger.info()
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url_pagination = scrapertools.find_single_match(data, "<li class='next next page-numbers'><a href='(.*?)'")
    matches = re.compile('<div class="video_image_container sdimg">[\s\S]+?<a href="(.*?)" class="view_more" title="([^"]+)"></a>[\s\S]+?<img src="([^"]+)" alt=""', re.DOTALL).findall(data)
    itemlist = []
    for url, title, thumbnail in matches:
        scrapedyear = '-'
        if "- Season " in title:
            scrapedinfo = title.split(' - Season ')
            title2 = scrapedinfo[0]
            season = scrapedinfo[1]
            url = urlparse.urljoin(host, url)+ "/season"
            new_item = Item(channel=item.channel, action="episodios",title=title, contentSerieName=title2, url=url, thumbnail=thumbnail,infoLabels={'season':season})
        elif "-info/" in url:
            url = urlparse.urljoin(host, url)
            url = url.replace("-info/", "/")+ "/all"
            new_item = Item(channel=item.channel, action="episodios",title=title, contentSerieName=title, url=url, thumbnail=thumbnail)
        else:
            url = urlparse.urljoin(host, url)+"-episode-0"
            extra = "film"
            new_item = Item(channel=item.channel, action="findvideos",title=title, url=url, extra=extra, contentTitle=title, thumbnail=thumbnail,infoLabels={'year':scrapedyear})
        itemlist.append(new_item)
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True, idioma_busqueda='en')
    if url_pagination:
        url = urlparse.urljoin(host + item.extra, url_pagination)
        title = ">> Pagina Siguiente"
        itemlist.append(Item(channel=item.channel, action="popular", title=title, url=url))
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    infoLabels = item.infoLabels
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", data)
    matches = re.compile('<div class="vid_info"><span><a href="(.*?)" title="(.*?)" class="videoHname"><b>Episode (\d+)', re.DOTALL).findall(data)
    for url, title, episode in matches:
        url = urlparse.urljoin(host, url)
        thumbnail = item.thumbnail
        title = title + " - Ep. " + episode
        if " Season " in title:
            scrapedinfo = title.split(' Season ')
            title = scrapedinfo[0] + " " + infoLabels['season'] + "x" + episode
        infoLabels['episode'] = episode
        itemlist.append(Item(channel=item.channel,
                             action="findvideos",
                             title=title,
                             url=url,
                             thumbnail=thumbnail,
                             infoLabels=infoLabels
                             ))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True, idioma_busqueda='en')
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    if "-episode-0" in item.url:
        data1 = httptools.downloadpage(item.url, canonical=canonical).data
        if "Page not found</h1>" in data1:
            item.url = item.url.replace("-episode-0", "-episode-1")
    
    data = re.sub(r"\n|\r|\t|\s{2}|-\s", "", httptools.downloadpage(item.url).data)
    matches = scrapertools.find_multiple_matches(data, 'data-video="(.*?)"')
    url = ''
    urlsub = ''
    urlsub = scrapertools.find_single_match(data, "&sub=(.*?)&cover")
    if urlsub != '':
        urlsub =  base64.b64decode(urlsub).decode('utf-8')
        urlsub = 'https://sub.movie-series.net' + urlsub   
    for source in matches:
        if '/streaming.php' in source:
            new_data = httptools.downloadpage("https:" + source).data
            url = scrapertools.find_single_match(new_data, "file: '(https://redirector.*?)'")
            thumbnail= "https://martechforum.com/wp-content/uploads/2015/07/drive-300x300.png"
            if url == "":
                source = source.replace("streaming.php", "load.php")
        elif '/load.php' in source:
            new_data = httptools.downloadpage("https:" + source).data
            url = scrapertools.find_single_match(new_data, "file: '(https://[A-z0-9]+.cdnfile.info/.*?)'")
            thumbnail= "https://vidnode.net/img/logo_vid.png"
        else:
            url = source
            thumbnail= ""
        if "https://redirector."  in url or "cdnfile.info" in url:
            url += "|referer=https://vidnode.net/"  
        
        if url != "":
            itemlist.append(Item(channel=item.channel, url=url, title='%s', action='play',plot=item.plot,  thumbnail=thumbnail, subtitle=urlsub))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra == 'film':
        itemlist.append(Item(channel=item.channel, title="Añadir a la Videoteca", text_color="yellow",
                             action="add_pelicula_to_library", url=item.url, thumbnail = item.thumbnail,
                             contentTitle = item.contentTitle
                             ))
    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist
