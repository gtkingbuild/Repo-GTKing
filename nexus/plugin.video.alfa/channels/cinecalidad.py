# -*- coding: utf-8 -*-
# -*- Channel CineCalidad -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

import re
import traceback
if not PY3: _dict = dict; from collections import OrderedDict as dict

from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryAllChannel

IDIOMAS = {'latino': 'LAT', 'castellano': 'CAST', 'portugues': 'VOSE'}
list_language = list(IDIOMAS.values())
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay']
list_quality_tvshow = []
list_servers = ['gounlimited', 'mega', 'vidcloud', 'torrent']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'cinecalidad', 
             'host': config.get_setting("current_host", 'cinecalidad', default=''), 
             'host_alt': ["https://www.cinecalidad.tf/"], 
             'host_black_list': ["https://www3.cinecalidad.ms/", "https://startgaming.net/", 
                                 "https://cinecalidad.ms/", "https://cinecalidad.dev/", "https://www.cinecalidad.lat/", 
                                 "https://v3.cine-calidad.com/", "https://www5.cine-calidad.com/", "https://cinecalidad3.com/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_torrent = host
channel = canonical['channel']
categoria = channel.capitalize()

thumbmx = 'http://flags.fmcdn.net/data/flags/normal/mx.png'
thumbes = 'http://flags.fmcdn.net/data/flags/normal/es.png'
thumbbr = 'http://flags.fmcdn.net/data/flags/normal/br.png'

current_lang = ''

site_list = ['', '%s' % host, '%sespana/' % host, 'https://www.cinemaqualidade.im']
site = config.get_setting('filter_site', channel=canonical['channel'])
site_lang = '%s' % site_list[site]
sufix = ['', '', '?castellano=sp', '']

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas"
tv_path = '/series'
language = []
url_replace = []

finds = {'find': {'find_all': [{'tag': ['article']}]}, 
         'sub_menu': {}, 
         'categories': {},
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['nav'], 'class': ['pagination']}]), 
                            ('find_all',[{'tag': ['a'], '@POS': [-2]}]), 
                            ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]), 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {},
         'season_num': {}, 
         'seasons_search_num_rgx': [], 
         'seasons_search_qty_rgx': [], 
         'episode_url': '', 
         'episodes': {}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['a'], 'class': ['inline-block']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax', ''],
                         ['(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', ''], 
                         ['(?i)[-|\(]?\s*HDRip\)?|microHD|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?', ''], 
                         ['(?i)\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|[\(|\[]\S*\.*$', ''],
                         ['(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*|\[*\(*dvd\s*r\d*\w*\]*\)*|[\[|\(]*dv\S*[\)|\]]*', ''], 
                         ['(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?', ''], 
                         ['(?i)(?:\s*&#8211;)?\s*temp.*?\d+.*', ''], ['\d?\d?&#.*', ''], ['\d+[x|×]\d+.*', ''], 
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)(?:libro|volumen)?\s+\d{1,2}$', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 11, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 
                      'host_torrent': host_torrent, 'duplicates': []},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = list()
    idioma2 = "destacadas"

    if site > 0:
        item.action = 'submenu'
        item.site_lang = site_lang
        item.url = host if site == 1 else host+'espana/'
        return submenu(item)

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel,
                         title="CineCalidad Latino",
                         action="submenu",
                         url=host,
                         site=1, 
                         thumbnail=thumbmx))

    itemlist.append(Item(channel=item.channel,
                         title="CineCalidad Castellano",
                         action="submenu",
                         url=host+'espana/',
                         site=2, 
                         c_type = 'peliculas', 
                         thumbnail=thumbes))

    # itemlist.append(Item(channel=item.channel,
    #                      title="CineCalidad Portugues",
    #                      action="submenu",
    #                      url="https://www.cinemaqualidade.im",
    #                      c_type = 'peliculas', 
    #                      thumbnail=thumbbr))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                         folder=False, thumbnail=get_thumb("next.png")))
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                         thumbnail=get_thumb("setting_0.png")))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def submenu(item):
    logger.info()
    
    global site, host
    
    idioma = 'peliculas'
    idioma2 = "destacada"
    if item.site_lang: host = item.site_lang
    if item.site: site = item.site
    # if item.site_lang == "https://www.cinemaqualidade.im":
    #     idioma = "filmes"
    #     idioma2 = "destacado"
    
    itemlist = []

    itemlist.append(Item(channel=item.channel,
                         title=idioma.capitalize(),
                         action="list_all",
                         url=item.url, 
                         site=site, 
                         c_type = 'peliculas', 
                         thumbnail=get_thumb('movies', auto=True),
                         ))

    if "/espana/" not in item.url:
        itemlist.append(Item(channel=item.channel,
                             title="Estrenos",
                             action="list_all",
                             url=item.url + "estrenos/",
                             site=site, 
                             c_type = 'peliculas', 
                             thumbnail=get_thumb('last', auto=True),
                             ))
        itemlist.append(Item(channel=item.channel,
                             title="Destacadas",
                             action="list_all",
                             url=item.url + "peliculas-populares/",
                             site=site, 
                             c_type = 'peliculas', 
                             thumbnail=get_thumb('hot', auto=True),
                             ))
        itemlist.append(Item(channel=item.channel,
                             title="Géneros",
                             action="section",
                             url=item.url,
                             site=site, 
                             c_type = 'peliculas', 
                             thumbnail=get_thumb('genres', auto=True),
                             ))
        itemlist.append(Item(channel=item.channel,
                             title="Año",
                             action="section",
                             url=item.url,
                             site=site, 
                             c_type = 'peliculas', 
                             thumbnail=get_thumb('year', auto=True),
                             ))
        # itemlist.append(Item(channel=item.channel,
        #                      title="Por Año",
        #                      action="by_year",
        #                      url=host + idioma + "-por-ano",
        #                      c_type = 'peliculas', 
        #                      thumbnail=get_thumb('year', auto=True),
        #                      ))

    itemlist.append(Item(channel=item.channel,
                         title="Buscar...",
                         action="search",
                         url=item.url,
                         site=site, 
                         c_type = 'peliculas',
                         thumbnail=get_thumb('search', auto=True)
                         ))

    if site > 0:
        autoplay.init(item.channel, list_servers, list_quality)

        itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                             folder=False, thumbnail=get_thumb("next.png")))
        itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                             thumbnail=get_thumb("setting_0.png")))

        autoplay.show_option(item.channel, itemlist)

    return itemlist


def configuracion(item):
    from platformcode import platformtools

    ret = platformtools.show_channel_settings()

    return platformtools.itemlist_refresh()


def section(item):
    logger.info()

    findS = finds.copy()
    kwargs['unescape'] = True

    if item.title == 'Géneros':
        findS['categories'] = dict([('find', [{'tag': ['nav'], 'id': ['menu']}]), 
                                    ('find_all', [{'tag': ['li']}])])
    elif item.title == 'Año':
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': ['year_tcine']}]), 
                                    ('find_all', [{'tag': ['a']}])])
        findS['controls'].update({'reverse': True}) 

    return AlfaChannel.section(item, matches_post=section_matches, finds=findS, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        elem_json['url'] = elem.a.get('href', '') if elem.a else elem.get('href', '')
        if item.title == 'Géneros' and 'categoria' not in elem_json['url']: continue

        elem_json['title'] = elem.get_text(strip=True)

        matches.append(elem_json.copy())

    return matches


def list_all(item):
    logger.info()

    kwargs['unescape'] = True

    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.a.get("href", "")
            if '/serie' in elem_json['url']: continue
            if scrapertools.find_single_match(elem_json['url'], "\d+x\d+") or "episode" in elem_json['url']: continue
            if sufix[item.site or 0] and sufix[item.site or 0] not in elem_json['url']:
                elem_json['url'] += sufix[item.site or 0]

            if "title" in elem.find('img', class_='w-full'):
                elem_json['title'], elem_json['year'] = elem.find('img', class_='w-full').get("title", "").split(' (')
            else:
                elem_json['title'] = elem.find('img', class_='w-full').get("alt", "")

            if not elem_json.get('year'):
                elem_json['year'] = '-'
                if elem.find('div'): elem_json['year'] = scrapertools.find_single_match(elem.find('div').get_text(strip=True), '\d{4}') or '-'

            elem_json['thumbnail'] = re.sub(r'(-\d+x\d+.jpg)', '.jpg', elem.find('img', class_="w-full").get("src", ""))

            elem_json['plot'] = elem.p.get_text(strip=True) if elem.p else ''
            
            elem_json['language'] = '*CAST' if item.site == 2 else '*LAT'

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url'): continue

        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()
    import base64

    matches = []
    findS = AHkwargs.get('finds', finds)
    srv_ids = {"Dood": "Doodstream",
               "Watchsb": "Streamsb",
               "Maxplay": "voe",
               "1fichier": "Onefichier",
               "Latmax": "Fembed", 
               "Ok": "Okru"}

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = base64.b64decode(elem.get("data-url", "") or elem.get("data-src", "")).decode('utf-8')
            if elem.get("data-url", ""):
                if elem.get_text(strip=True).capitalize() != 'Torrent': continue
                elem_json['url'] = AlfaChannel.create_soup(elem_json['url']).find("div", id="btn_enlace").a.get("href", "")

                elem_json['quality'] = '*'

                elem_json['language'] = '*LAT'

            elem_json['server'] = elem.get_text(strip=True).capitalize()
            if elem_json['server'] in ["Cineplay", "Netu", "trailer"]: continue
            if elem_json['server'] in srv_ids:
                elem_json['server'] = srv_ids[elem_json['server']]
            
            if not elem_json.get('language'): elem_json['language'] = item.language

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())

        if not elem_json.get('url', ''): 
            continue

        matches.append(elem_json.copy())

    return matches, langs


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def play(item):
    logger.info()

    if not 'magnet' in item.url and not 'torrent' in item.url:
        item.url = AlfaChannel.create_soup(item.url).find("iframe").get("src", "")

        itemlist = servertools.get_servers_itemlist([item])
    else:
        itemlist = [item]

    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    global kwargs
    kwargs = AHkwargs

    itemlist = []
    texto = texto.replace(" ", "-")

    item.url = host + '?s=' + texto

    try:
        if texto != '':
            item.c_type = 'peliculas'
            item.texto = texto
            itemlist.extend(list_all(item))
            return itemlist
        else:
            return []

    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    itemlist = []
    item = Item()
    item.c_type = 'peliculas'

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

        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
