# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from channels import autoplay
from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, tmdb
from core import servertools, channeltools
from channels import filtertools
from bs4 import BeautifulSoup
from channelselector import get_thumb
forced_proxy_opt = 'ProxyCF'

canonical = {
             'channel': 'animeonlineninja', 
             'host': config.get_setting("current_host", 'animeonlineninja', default=''), 
             'host_alt': ["https://www1.animeonline.ninja/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

IDIOMAS = {"esp": "CAST", "lat": "LAT", "sub": "VOSE"}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = []

__comprueba_enlaces__ = config.get_setting('comprueba_enlaces', canonical['channel'])
__comprueba_enlaces_num__ = config.get_setting('comprueba_enlaces_num', canonical['channel'])
try:
    __modo_grafico__ = config.get_setting('modo_grafico', canonical['channel'])
except:
    __modo_grafico__ = True

parameters = channeltools.get_channel_parameters(canonical['channel'])
unif = parameters['force_unify']


def mainlist(item):
    logger.info()
    
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(item.clone(title="Por idioma", action="idioma", url= host + "Series.html?page=1", thumbnail=get_thumb('language', auto=True)))
    itemlist.append(item.clone(title="Nuevos Episodios" , action="new_episodes", url= host + "episodio/", thumbnail=get_thumb('new_episodes', auto=True)))
    itemlist.append(item.clone(title="Ultimas" , action="lista", url= host + "online/", thumbnail=get_thumb('last', auto=True)))
    itemlist.append(item.clone(title="       Mas Popular" , action="lista", url= host + "tendencias/?get=tv", thumbnail=get_thumb("anime", auto=True)))
    itemlist.append(item.clone(title="       Mejor Valorado" , action="lista", url= host + "ratings/?get=tv", thumbnail=get_thumb("anime", auto=True)))
    itemlist.append(item.clone(title="Pelicula", action="lista", url= host + "pelicula/", thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(item.clone(title="       Mas Popular" , action="lista", url= host + "tendencias/?get=movies", thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(item.clone(title="       Mejor Valorado" , action="lista", url= host + "ratings/?get=movies", thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(item.clone(title="Live Action" , action="lista", url= host + "genero/live-action/", thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(item.clone(title="Dragon Ball" , action="categorias", url= host, id="menu-item-11164", thumbnail="" ))
    itemlist.append(item.clone(title="Genero" , action="categorias", url= host, thumbnail=get_thumb('genres', auto=True)))
    itemlist.append(item.clone(title="Buscar...", action="search", thumbnail=get_thumb("search", auto=True)))
    itemlist.append(item.clone(title="Configurar canal...", action="configuracion", text_color="gold", folder=False, thumbnail=get_thumb("setting_0.png")))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def configuracion(item):
    from platformcode import platformtools
    
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    
    return ret


def search(item, texto):
    logger.info()
    
    try:
        texto = texto.replace(" ", "+")
        item.url = "%s?s=%s" % (host, texto)
        if texto != "":
            return lista(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def idioma(item):
    logger.info()
    
    itemlist = []
    
    itemlist.append(item.clone(action="lista", title="Castellano", url= host + "genero/anime-castellano/"))
    itemlist.append(item.clone(action="lista", title="Latino", url= host + "genero/audio-latino/"))
    # itemlist.append(item.clone(action="peliculas", title="VOSE", url= host + "idioma/subtitulado/"))
    
    return itemlist


def categorias(item):
    logger.info()
    
    itemlist = []
    
    if item.id:
        soup = create_soup(item.url).find('li', id=item.id).ul
    else:
        soup = create_soup(item.url).find('li', id='menu-item-11872').ul
    matches = soup.find_all('a')
    
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        if "/online/" in url:
            action = "seasons"
        else:
            action = "lista"
        itemlist.append(item.clone(channel=item.channel, action=action, title=title , url=url, 
                              section=item.section) )
    return itemlist


def create_soup(url, referer=None, post=None, unescape=False):
    logger.info()
    
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    if post:
        data = httptools.downloadpage(url, post=post, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    
    return soup


def new_episodes(item):
    logger.info()
    
    itemlist = []
    
    soup = create_soup(item.url, referer=host)
    matches = soup.find_all("article", class_="item")

    for elem in matches:
        id = elem['id'].replace("post-", "")
        url = elem.a['href']
        url = "%swp-json/dooplayer/v1/post/%s?type=tv&source=1" % (host,id)
        title = elem.h3.text.strip()
        thumbnail= elem.img['data-src']
        try:
            epi = int(elem.h4.text.replace('Episodio ', '').strip())
        except:
            epi = 1
        title = '%s - %s' % (title, epi)
        itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=thumbnail,
                             action='findvideos', contentSerieName=elem.h3.text.strip(), contentType='episode', 
                             contentSeason=1, contentEpisodeNumber=epi))
    
    tmdb.set_infoLabels(itemlist, True)
    
    next_page = soup.find(id='nextpagination')
    if next_page:
        next_page = next_page.parent['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="new_episodes", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    
    return itemlist


def lista(item):
    logger.info()
    
    itemlist = []
    
    soup = create_soup(item.url, referer=host)
    if "/?s=" in item.url:
        matches = soup.find('div', class_='search-page').find_all("article")
    else:
        matches = soup.find('div', class_='content').find_all("article", id=re.compile(r"^post-\d+"))
    
    for elem in matches:
        tipo = ""
        title = ""
        year = ""
        if not "/?s=" in item.url:
            title = elem.h3.text.strip()
        if not title:
            title = elem.img['alt']
        url1 = elem.a['href']
        thumbnail= elem.img['data-src']
        if "/pelicula/" in url1:
            tipo = "movie"
            # url = "%swp-json/dooplayer/v1/post/%s?type=%s&source=1" % (host,id,tipo)
            quality = elem.find('span', class_='quality')
            if quality:
                quality = quality.text.strip()
                if "Próximamente" in quality:
                    title = "[COLOR red]%s[/COLOR]: %s" %(quality.capitalize(),title)
            data = elem.find('div', class_='data')
            if data:
                data = data.span.text.strip()
                year = scrapertools.find_single_match(data, '(\d{4})')
        contentTitle = title
        if elem.find('span', class_='year'):
            year = elem.find('span', class_='year').text.strip()
        if year == '':
            year = '-'
        new_item = Item(channel=item.channel, title=title, thumbnail=thumbnail, infoLabels={"year": year})
        if tipo:
            new_item.action = "findvideos"
            new_item.url = url1
            new_item.contentTitle = contentTitle
            new_item.contentType = 'movie'
        else:
            new_item.action = "seasons"
            new_item.url = url1
            new_item.contentSerieName = contentTitle
            new_item.contentType = 'tvshow'
        
        itemlist.append(new_item)
    
    tmdb.set_infoLabels(itemlist, True)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    next_page = soup.find('span', class_='current')
    if next_page and next_page.find_next_sibling("a"):
        next_page = next_page.find_next_sibling("a")['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    
    return itemlist


def seasons(item):
    logger.info()
    
    itemlist = list()
    infoLabels = item.infoLabels
    
    soup = create_soup(item.url)
    matches = soup.find_all('span', class_='se-t')
    
    for elem in matches:
        season= elem.text.strip()
        if int(season) < 10:
            season = "0%s" %season
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(item.clone(title=title, url=item.url, action="episodesxseasons",
                             infoLabels=infoLabels))
    
    tmdb.set_infoLabels_itemlist(itemlist, True)
    
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(item.clone(title="[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]", url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))
    
    return itemlist


def episodesxseasons(item):
    logger.info()
    
    itemlist = list()
    infoLabels = item.infoLabels
    season = infoLabels["season"]
    
    soup = create_soup(item.url)
    matches = soup.find_all('li', class_=re.compile(r"^mark-\d+"))
    
    for elem in matches:
        cap= elem['class'][0].replace("mark-", "")
        if int(cap) < 10:
            cap = "0%s" % cap
        title = "%sx%s" % (season, cap)
        infoLabels["episode"] = cap
        url= elem.a['href']
        itemlist.append(item.clone(title=title, url=url, action="findvideos",
                                 infoLabels=infoLabels))
    
    tmdb.set_infoLabels_itemlist(itemlist, True)
    
    a = len(itemlist)-1
    for i in itemlist:
        if a >= 0:
            title= itemlist[a].title
            titulo = itemlist[a].infoLabels['episodio_titulo']
            title = "%s %s" %(title, titulo)
            itemlist[a].title = title
            a -= 1
    
    return itemlist


def episodios(item):
    logger.info()
    
    itemlist = []
    
    templist = seasons(item)
    
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)
    
    return itemlist


def findvideos(item):
    logger.info()
    
    itemlist = []
    
    if not "/wp-json/dooplayer/" in item.url:
        soup = create_soup(item.url)
        id = soup.find('link', rel='shortlink')['href']
        id = scrapertools.find_single_match(id, '=(\d+)')
        cap = "%swp-json/dooplayer/v1/post/%s?type=tv&source=1" % (host,id)
        data = httptools.downloadpage(cap, canonical=canonical).json
    else:
        data = httptools.downloadpage(item.url, canonical=canonical).json
    url = data['embed_url']
    if not url:
        return
    
    if "/embed.php?id=" in url:
        soup = create_soup(url)
        matches = soup.find('div', class_='OptionsLangDisp').find_all('li')
        for elem in matches:
            url = elem['onclick'].replace("go_to_player('", "").replace("')", "")
            lang = elem.p.text.strip()
            if "castellano" in lang.lower(): lang = "esp"
            if "latino" in lang.lower(): lang = "lat" 
            if "sub" in lang.lower(): lang = "sub" 
            lang = IDIOMAS.get(lang, lang)
            itemlist.append(item.clone(action="play", title="%s", url=url, language=lang ))
    else:
        matches = soup.find('div', id='playeroptions').find_all('li')
        for elem in matches:
            lang = ""
            title = elem.find('span', class_='title')
            server = elem.find('span', class_='server')
            id = elem['data-post']
            type = elem['data-type']
            source = elem['id'].replace("player-option-", "")
            cap = "%swp-json/dooplayer/v1/post/%s?type=%s&source=%s" % (host,id,type,source)
            data = httptools.downloadpage(cap, canonical=canonical).json
            url = data['embed_url']
            if title:
                title = title.text.strip()
            if "castellano" in title.lower(): lang = "esp"
            if "latino" in title.lower(): lang = "lat" 
            if "sub" in title.lower(): lang = "sub" 
            if not lang:
                lang = "sub"
            lang = IDIOMAS.get(lang, lang)
            if url:
                itemlist.append(item.clone(action="play", title="%s", url=url, language=lang ))
    
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())
    itemlist.sort(key=lambda it: (it.language))

    # Requerido para Filtrar enlaces
    if __comprueba_enlaces__:
        itemlist = servertools.check_list_links(itemlist, __comprueba_enlaces_num__)
    
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra !='findvideos' and not "/episodios/" in item.url :
        itemlist.append(item.clone(action="add_pelicula_to_library", 
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                             extra="findvideos", contentTitle=item.contentTitle)) 
    
    return itemlist

