# -*- coding: utf-8 -*-
# -*- Channel Cuevana2Español -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryChannel

IDIOMAS = {"latino": "LAT", "spanish": "CAST", "english": "VOSE", "Subtitulado": "VOSE", 
           'mx': 'LAT', 'dk': 'LAT', 'es': 'CAST', 'en': 'VOSE', 'gb': 'VOSE', 'de': 'OTHER',
           "mexico": "LAT", "Español": "CAST", "España": "CAST"}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_servers = ['fembed', 'streamtape', 'streamlare', 'zplayer']

canonical = {
             'channel': 'cuevana2espanol', 
             'host': config.get_setting("current_host", 'cuevana2espanol', default=''), 
             'host_alt': ["https://cuevana2espanol.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
forced_proxy_opt = 'ProxyCF|FORCE'

finds = {'find': {'find': [{'tag': ['div'], 'class': ['row row-cols-xl-5 row-cols-lg-4 row-cols-3']}], 'find_all': ['article']},
         'next_page': {'find': [{'tag': ['span'], 'string': re.compile('Next')}], 'find_parent': [{'tag': ['a'], '@ARG': 'href'}]}, 
         'year': {'find': [{'tag': ['div'], 'class': ['MovieItem_data__BdOz3', 'SerieItem_data__LFJR_'], '@TEXT': '\d{4}'}]}, 
         'season_episode': {'find': [{'tag': ['div'], 'class': ['EpisodeItem_data__jsvqZ']}, ['span']]}, 
         'season': {'find': [{'tag': ['div'], 'class': ['serieBlockListEpisodes_selector__RwIbM']}], 'find_all': ['option']}, 
         'episode_url': '%sseries/%s/seasons/%s/episodes/%s', 
         'episodes': {'find': [{'tag': ['script'], 'id': ['__NEXT_DATA__']}], 'get_text': [{'tag': '', '@STRIP': False}]}, 
         'episode_num': [], 
         'episode_clean': [], 
         'findvideos': {'find': [{'tag': ['script'], 'id': ['__NEXT_DATA__']}], 'get_text': [{'tag': '', '@STRIP': False}]}, 
         'title_clean': []}
AlfaChannel = DictionaryChannel(host, movie_path="/movies", tv_path='/series', canonical=canonical, finds=finds, debug=False)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu', url=host+'archives/movies', 
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu', url=host+'archives/series', 
                         thumbnail=get_thumb('tvshows', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + 'search?q=',
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Últimas', url=item.url, action='list_all',
                         thumbnail=get_thumb('all', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, title='Estrenos', url=item.url+'/releases', action='list_all',
                         thumbnail=get_thumb('all', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, title='Tendencias Semana', url=item.url+'/top/week', action='list_all',
                         thumbnail=get_thumb('all', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, title='Tendencias Día', url=item.url+'/top/day', action='list_all',
                         thumbnail=get_thumb('all', auto=True), c_type=item.c_type))
    
    if item.c_type == 'peliculas':
        itemlist.append(Item(channel=item.channel, title='Generos', action='section', url=host,
                             thumbnail=get_thumb('genres', auto=True), c_type=item.c_type))
    else:
        itemlist.append(Item(channel=item.channel, title='Episodios', action='list_all', url=host+'archives/episodes',
                             thumbnail=get_thumb('episodes', auto=True), c_type='episodios'))

    return itemlist


def list_all(item):
    logger.info()
    global finds
    
    if item.c_type == 'episodios':
        finds['find'] = {'find': [{'tag': ['div'], 'class': ['row row-cols-xl-4 row-cols-lg-3 row-cols-2']}]}

    return AlfaChannel.list_all(item, finds=finds)


def section(item):
    logger.info()

    genres = {'Acción': 'genres/accion', 
              'Animación': 'genres/animacion', 
              'Crimen': 'genres/crimen', 
              'Familia': 'genres/familia', 
              'Misterio': 'genres/misterio', 
              'Suspense': 'genres/suspenso', 
              'Aventura': 'genres/aventura', 
              'Ciencia Ficción': 'genres/ciencia-ficcion', 
              'Drama': 'genres/drama', 
              'Fantasía': 'genres/fantasia', 
              'Romance': 'genres/romance', 
              'Terror': 'genres/terror'
              }

    return AlfaChannel.section(item, section_list=genres)


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item)


def episodesxseason(item):
    logger.info()

    return AlfaChannel.episodes(item)


def episodios(item):
    logger.info()
    
    itemlist = []
    
    templist = seasons(item)
    
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    if not finds.get('findvideos', {}):
        return itemlist

    servers = {'drive': 'gvideo', 'fembed': 'fembed', "player": "oprem", "openplay": "oprem", "embed": "mystream"}
    action = item.contentType if item.contentType == 'episode' else 'post'

    soup = AlfaChannel.create_soup(item.url)

    json = jsontools.load(AlfaChannel.parse_finds_dict(soup, finds['findvideos']))
    matches = json.get('props', {}).get('pageProps', {}).get(action, {}).get('players', {})
    
    if not matches: 
        logger.error(soup)
        logger.error(json)
        return itemlist

    for lang, elem in list(matches.items()):

        for link in elem:
            srv = link.get('cyberlocker', '')
            url = link.get('result', '')
            quality = link.get('quality', '')
            if not url:
                continue

            if srv.lower() in ["waaw", "jetload"]:
               continue
            if srv.lower() in servers:
               srv = servers[srv.lower()]

            itemlist.append(Item(channel=item.channel, title=srv, url=url, action="play", infoLabels=item.infoLabels,
                                 language=IDIOMAS.get(lang, lang), server=srv, quality=quality, referer=item.url))

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.contentType == 'movie':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    autoplay.start(itemlist, item)

    return itemlist


def play(item):
    logger.info()
    
    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
              'timeout': 5, 'cf_assistant': False, 'follow_redirects': False, 'referer': item.referer, 'canonical': {}, 
              'CF': False, 'forced_proxy_opt': forced_proxy_opt}
    item.setMimeType = 'application/vnd.apple.mpegurl'

    soup = AlfaChannel.create_soup(item.url, **kwargs)
    if not soup:
        return []
    soup = soup.find("script").text

    item.url = scrapertools.find_single_match(str(soup), "url\s*=\s*'([^']+)'")
    if item.url:
        itemlist = servertools.get_servers_itemlist([item])
    else:
        itemlist = []

    if item.server.lower() == "zplayer":
        item.url += "|referer=%s" % host
        
        itemlist = [item]
    
    return itemlist


def search(item, texto):
    logger.info()
    
    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto
        
        if texto != '':
            return list_all(item)
        else:
            return []
    
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()

    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host + 'archives/movies'

        itemlist = list_all(item)
        
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist