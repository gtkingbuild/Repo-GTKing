# -*- coding: utf-8 -*-
# -*- Channel Mundo Donghua -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys, re
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from bs4 import BeautifulSoup
from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from platformcode import platformtools
from channels import filtertools, autoplay
from channels import renumbertools
from core import tmdb


IDIOMAS = {'vose': 'VOSE'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['directo', 'dailymotion']

canonical = {
             'channel': 'mundodonghua', 
             'host': config.get_setting("current_host", 'mundodonghua', default=''), 
             'host_alt': ["https://www.mundodonghua.com/"], 
             'host_black_list': [], 
             'pattern': '<meta\s*property="og:image"\s*content="([^"]+)"', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host
sort_views = True


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos Capítulos", url=host+ 'lista-episodios', 
                        action="list_all", thumbnail=get_thumb('new episodes', auto=True), neweps=True))

    itemlist.append(Item(channel=item.channel, title="Emision", url=host + 'lista-donghuas-emision',
                         action="list_all", thumbnail=get_thumb('on air', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Finalizadas", url=host+ 'lista-donghuas-finalizados',
                         action="list_all", thumbnail=get_thumb('anime', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Todas", url=host+'lista-donghuas',
                        action="list_all", thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", url=host, action="genres",
                        thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", url=host + 'busquedas/', action="search",
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    itemlist = renumbertools.show_option(item.channel, itemlist)

    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()

    data = httptools.downloadpage(url, headers={'Referer':referer}, canonical=canonical).data
    
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup

def genres(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    for elem in soup.find_all("div", class_="col-xs-6 p-0"):
        url = host+elem.a["href"]
        title = elem.a.text.strip()
        itemlist.append(Item(channel=item.channel, title=title, url=url,
                             action='list_all'))

    return itemlist

def list_all(item):
    logger.info()

    itemlist = list()
    
    action = "episodios"
    if item.neweps:
        action = "findvideos"

    soup = create_soup(item.url)


    for elem in soup.find_all("div", class_=re.compile("item col-lg-\d col-md-\d col-xs")):
        
        url = host+elem.a["href"]
        title = elem.h5.text.strip()
        thumb = host+elem.img["src"]
        typo = elem.a.find('div', class_="img fit-1").text.strip()
        views = elem.label.text.strip()
        
        context = renumbertools.context(item)
        context2 = autoplay.context
        context.extend(context2)
        

        filtro_tmdb = list({"original_language": 'zh'}.items())
        
        if typo.lower() == 'película':
            url = url.replace('/donghua/', 'ver/') + '/1'
            itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                                thumbnail=thumb, contentTitle=title, plot=typo, typo=typo,
                                views=views, infoLabels={'filtro':filtro_tmdb}))
        else:
            
            context3 = [{"title": "Config Saltar Intro en Serie",
                        "action": "set_skip_time",
                        "channel": item.channel}]

            context.extend(context3)
            
            itemlist.append(Item(channel=item.channel, title=title, url=url, action=action,
                                thumbnail=thumb, contentSerieName=title, context=context,
                                plot=typo, views=views, infoLabels={'filtro':filtro_tmdb}))
    if sort_views and not 'Capítulos'in item.title:
        itemlist.sort(key=lambda it: int(it.views), reverse=True)
    tmdb.set_infoLabels_itemlist(itemlist, True)
    try:
        url_next_page = soup.find("ul", class_="pagination").find_all("a")[-1]
        if url_next_page.text:
            url_next_page = ''
        else:
            url_next_page = url_next_page["href"]
    except:
        return itemlist

    url_next_page = host + url_next_page

    if url_next_page:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>",
                             url=url_next_page, action='list_all'))
    return itemlist

def episodios(item):
    logger.info()

    itemlist = list()
    first_url = ""

    infoLabels = item.infoLabels
    item.contex = [{"title": "Config Saltar Intro en Serie",
                        "action": "set_skip_time",
                        "channel": item.channel}]
    soup = create_soup(item.url)
    ep_list = soup.find("ul", class_="donghua-list")
    try:
        plot = soup.find("p", class_="text-justify fc-dark").text
    except:
        plot = ""
    try:
        state = soup.find("span", class_="badge bg-success")
    except:
        state = ''


    for elem in ep_list.find_all("a"):
        
        url = host+elem["href"]

        if not first_url and state:
            first_url = url
        epi_num = scrapertools.find_single_match(elem.text.strip(), "(\d+)$")
        season, episode = renumbertools.numbered_for_tratk(item.channel, item.contentSerieName, 1, int(epi_num))
        infoLabels['season'] =  season
        infoLabels['episode'] = episode
        title = '%sx%s - Episodio %s' % (season, episode, episode)
        itemlist.append(Item(channel=item.channel, title=title, url=url,
                            plot=plot, thumbnail=item.thumbnail,
                            action='findvideos', infoLabels=infoLabels, 
                            context=item.contex))

    itemlist = itemlist[::-1]
    
    if first_url and state:
        epi_num = int(scrapertools.find_single_match(first_url, "(\d+)$"))+1
        url = re.sub("(\d+)$", str(epi_num), first_url)
        season, episode = renumbertools.numbered_for_tratk(item.channel, item.contentSerieName, 1, int(epi_num))
        infoLabels['season'] =  season
        infoLabels['episode'] = episode
        title = '%sx%s - Episodio %s' % (season, episode, episode)
        try:
            data = httptools.downloadpage(url).data
            #logger.error(data)
            matches = scrapertools.find_multiple_matches(data, "(eval.*?)\n")
            if matches:
                itemlist.append(Item(channel=item.channel, title=title, url=url, 
                             plot=plot, thumbnail=item.thumbnail,
                            action='findvideos', infoLabels=infoLabels,
                            context=item.contex))
        except:
            pass

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName,
                 extra1='library'))

    return itemlist

def findvideos(item):
    logger.info()
    from lib import jsunpack
    import base64, time

    itemlist = list()

    data = httptools.downloadpage(item.url, canonical=canonical).data
    #logger.error(data)
    matches = scrapertools.find_multiple_matches(data, "(eval.*?)\n")
    if len(matches) > 1:
        for pack in matches:
            unpack = jsunpack.unpack(pack)
            #logger.error(unpack)
            url = scrapertools.find_single_match(unpack, 'file(?:"|):"([^"]+)')
            if not url.startswith('http'):
                url = 'http:'+url

            itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url, language=IDIOMAS['vose'],
                             infoLabels=item.infoLabels))

    else:
        unpack = jsunpack.unpack(matches[0])
        #logger.error(unpack)
        slugs = scrapertools.find_multiple_matches(unpack, '"slug":"([^"]+)')
        if slugs:
            for slug in slugs:
                url = '%sapi_donghua.php?slug=%s' %(host, slug)
                try:
                    data = httptools.downloadpage(url, headers={'Referer': item.url}).json[0]
                except:
                    
                    time.sleep(1)
                    data = httptools.downloadpage(url, headers={'Referer': item.url}).json[0]

                #logger.error(data)
                if data.get('url',''):
                    url = 'https://www.dailymotion.com/video/'+base64.b64decode(data['url']).decode('utf-8')
                elif data.get('source', ''):
                    url = data['source'][0].get('file','')
                    if not url.startswith('http'):
                        url = 'http:'+url

                itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url, language=IDIOMAS['vose'],
                                 infoLabels=item.infoLabels))
        else:
            url = scrapertools.find_single_match(unpack, 'file(?:"|):"([^"]+)')
            if not url.startswith('http'):
                url = 'http:'+url
            item.url = url
            item.action = "play"
            item.skip = get_skip_time(item.contentSerieName, item)
            time.sleep(0.5)
            if not isinstance(logger.info(), bool):
                platformtools.play_video(item)
                time.sleep(2)
                if not platformtools.is_playing():
                    platformtools.play_video(item)
            return ""
            itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url, language=IDIOMAS['vose'],
                                 infoLabels=item.infoLabels))
    
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)


    if config.get_videolibrary_support() and itemlist and item.typo:
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist

def play(item):
    if item.contentSerieName:
        item.skip = get_skip_time(item.contentSerieName, item)
    logger.error(item.channel)
    return [item]

def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    if texto != '':
        return list_all(item)
    else:
        return []

def get_skip_time(title, item):
    channel = item.channel
    if channel == 'videolibrary':
        channel = item.contentChannel
    saved_skips_list = config.get_setting("saved_skips_list", channel)
    if not saved_skips_list:
        return None
    
    skips_list = list(saved_skips_list)
    for s in skips_list:
        time_skip = list(s.values())[0]
        title_saved = list(s.keys())[0]
        if title == title_saved:
            return time_skip


    return None

def set_skip_time(item):

    heading = "Introduzca en segundos la duración de la Intro"
    seconds = int(platformtools.dialog_numeric(0, heading, default=""))
    return save_skip_time(seconds, item)



def save_skip_time(time, item):
    saved_skips_list = []
    
    title =item.contentSerieName
    channel = item.channel
    
    heading = "Config Saltar Intro para %s" % title
    edit = "Guardado"
    tm = ""
    
    saved_skips_list = config.get_setting("saved_skips_list", channel)
    skips_list = list(saved_skips_list)

    for n, sv in enumerate(skips_list):
        if isinstance(sv, dict) and sv.get(title, ''):
            edit = "Editado"
            if not time:
                edit = "Eliminado"
            del skips_list[n]

    if time:
        skips_list.insert(0, {title: time})
        tm = "[COLOR gold][%ss][/COLOR] " % str(time)
    
    config.set_setting("saved_skips_list", skips_list, channel)

    
    mes = "Registro %s con Exito" % edit
    message = tm+mes

    platformtools.dialog_notification(heading, message, sound=True)



