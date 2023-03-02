# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.pelisplanet.to/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_pelisplanet_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www.pelisplanet.com/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('pelisplanet', url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))
    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genero/estrenos/' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('accion', 'Acción'),
       ('adolecentes', 'Adolecentes'),
       ('animacion-e-infantil', 'Animación e Infantil'),
       ('anime', 'Anime'),
       ('artes-marciales', 'Artes Marciales'),
       ('aventura', 'Aventura'),
       ('biografico', 'Biográfico'),
       ('ciencia-ficcion', 'Ciencia Ficcion'),
       ('comedia', 'Comedia'),
       ('crimen', 'Crimen'),
       ('deporte', 'Deporte'),
       ('documental', 'Documental'),
       ('drama', 'Drama'),
       ('familiar', 'Familiar'),
       ('fantasia', 'Fantasia'),
       ('fantastico', 'Fantastico'),
       ('guerra', 'Guerra'),
       ('historica', 'Historica'),
       ('homosexualidad', 'Homosexualidad'),
       ('intriga', 'Intriga'),
       ('misterio', 'Misterio'),
       ('musical', 'Musical'),
       ('navideñas', 'Navideñas'),
       ('religion', 'Religión'),
       ('romance', 'Romance'),
       ('secuela', 'Secuela'),
       ('superheroes', 'Superheroes'),
       ('suspenso', 'Suspenso'),
       ('terror', 'Terror'),
       ('triller', 'Triller'),
       ('uncategorized', 'Uncategorized'),
       ('videojuegos', 'Videojuegos'),
       ('westerns', 'Westerns')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'genero/' + opc + '/', action = 'list_all' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/castellano/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/latino/' ))
    itemlist.append(item.clone( title = 'Subtitulada', action = 'list_all', url = host + 'idioma/subtitulada/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/subtitulado/' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1920, -1):
        itemlist.append(item.clone( title = str(x), url= host + 'fecha-estreno/' + str(x) + '/', action = 'list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\(.*?\)|\s{2}|&nbsp;", "", data)

    data = scrapertools.find_single_match(data, '<div class="home-movies">(.*?)<footer>')

    patron = 'col-sm-5".*?href="([^"]+)".+?'
    patron += 'browse-movie-link-qd.*?>([^<]+)</.+?'
    patron += '<p>([^<]+)</p>.+?'
    patron += 'title one-line">([^<]+)</h2>.+?'
    patron += 'img-responsive" src="([^"]+)".*?'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, qlty, year, title, thumb in matches:
        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)">')
        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Español Latino': 'Lat', 'Subtitulada': 'Vose'}

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\(.*?\)|\s{2}|&nbsp;", "", data)

    patron = '<a id="[^"]+" style="cursor:pointer; cursor: hand" rel="([^"]+)".*?'
    patron += '<span class="optxt"><span>(.*?)</span>.*?'
    patron += '<span class="q">([^<]+)</span>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    ses = 0

    for url, lang, servidor in matches:
        ses += 1

        servidor = servidor.lower().strip()

        if servidor == 'streamvips': continue
        elif servidor == 'ultrastream': continue

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue
        elif '.mystream' in url: continue
        elif '.rapidvideo' in url: continue
        elif 'streamango.' in url: continue
        elif 'openload.' in url: continue

        if url.startswith('ttps://') == True: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor:
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang, lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def sub_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<li class="itemlist searchResult".*?<a href="(.*?)".*?title="(.*?)".*?src="(.*?)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, thumb in matches:
        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        item.url = host + 'search/' + texto +'/'

        return sub_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
