# -*- coding: utf-8 -*-
# -*- Channel Eztv -*-
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

IDIOMAS = {'es': 'CAST', 'la': 'LAT', 'us': 'VOSE', 'ES': 'CAST', 'LA': 'LAT', 'US': 'VOSE', 
           'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VOSE', 'SPANISH': 'CAST', }
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['torrent']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'eztv', 
             'host': config.get_setting("current_host", 'eztv', default=''), 
             'host_alt': ["https://eztv.re/"], 
             'host_black_list': [], 
             'pattern': '<div\s*id="header_logo">\s*<a\s*href="([^"]+)"', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_torrent = 'https://zoink.ch/'
channel = canonical['channel']
categoria = channel.capitalize()
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)     # Actualización sólo últ. Temporada?
min_temp = modo_ultima_temp if not modo_ultima_temp else 'continue'

timeout = config.get_setting('timeout_downloadpage', channel)
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas/"
tv_path = '/shows'
language = ['VO']
url_replace = []

finds = {'find': {'find_all': [{'tag': ['tr'], 'name': ['hover'], '@LIM': 500}]}, 
         'sub_menu': {}, 
         'categories': {}, 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {'find': [{'tag': ['a'], 'string': re.compile('next page'), '@ARG': 'href'}]}, 
         'next_page_rgx': [['\/page_\d+', '/page_%s']], 
         'last_page': {}, 
         'year': {}, 
         'season_episode': {}, 
         'seasons': dict([('find', [{'tag': ['table'], 'class': ['show_info_description']}]), 
                          ('find_all', [{'tag': ['h3'], 'string': re.compile('(?i)season')}])]), 
         'season_num': {'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(?i)season\s+(\d{1,2})\s+'}]}, 
         'seasons_search_num_rgx': [], 
         'seasons_search_qty_rgx': [], 
         'episode_url': '', 
         'episodes': dict([('find', [{'tag': ['table'], 'class': ['show_info_description']}]), 
                           ('find_all', [{'string': re.compile('[^-]+\s+--\s+[^\-]+(?:\s+--\s+[^$]*)?$')}])]), 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['tr'], 'name': ['hover']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax|documental|completo|\s*torrent', ''],
                         ['[\(|\[]\s+[\)|\]]', '']],
         'quality_clean': [['(?i)proper\s*|unrated\s*|directors\s*|cut\s*|german\s*|repack\s*|internal\s*|real\s*|korean\s*', ''],
                           ['(?i)extended\s*|masted\s*|docu\s*|oar\s*|super\s*|duper\s*|amzn\s*|uncensored\s*|hulu\s*', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'min_temp': min_temp, 'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 20,
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'host_torrent': host_torrent, 'btdigg': False, 'duplicates': [], 'dup_list': 'title', 'dup_movies': True, 
                      'join_dup_episodes': False, 'manage_torrents': True},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = []
    plot =  ''
    
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Series", action="list_all", 
                         url=host + "showlist/rating/", post="showlist_thumbs=on&status=airing", 
                         thumbnail=get_thumb("channels_tvshow_hd.png"), c_type="series", 
                         contentPlot=plot))
    
    itemlist.append(Item(channel=item.channel, title="Temporadas completas", action="list_all", 
                         url=host + "cat/tv-packs-1/", extra = 'Temporadas', 
                         thumbnail=get_thumb("downloads.png"), c_type="series", 
                         contentPlot=plot))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", 
                         url=host, thumbnail=get_thumb("search.png"), c_type="search", 
                         category=categoria, contentPlot=plot))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                         folder=False, thumbnail=get_thumb("next.png")))
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                         thumbnail=get_thumb("setting_0.png")))
    
    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)
    
    autoplay.show_option(item.channel, itemlist)

    return itemlist


def configuracion(item):
    from platformcode import platformtools

    ret = platformtools.show_channel_settings()

    return platformtools.itemlist_refresh()


def list_all(item):
    logger.info()
    
    findS = finds
    
    if item.c_type == 'search':
        findS['controls'].update({'duplicates': None})
    
    return AlfaChannel.list_all(item, matches_post=list_all_matches, finds=findS, generictools=True, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    search_list = []
    patron_sxe = '(?i)S(\d+)E(\d+)'
    findS = AHkwargs.get('finds', finds)

    for y, elem_tr in enumerate(matches_int):
        elem_json = {'mediatype': 'tvshow'}
        #if y == 0: logger.error(elem_tr)
        
        if item.extra == 'Temporadas':
            
            elem_json = findvideos_links(item, elem_tr, elem_json)

        elif item.c_type == 'search':
            for x, elem in enumerate(elem_tr.find_all('td')):
                #if y == 0: logger.error(elem)

                try:
                    if x == 0:
                        if 'other tv shows' in elem.a.get("title", "").lower(): break
                        if elem.a.get("href", "") in search_list: continue
                        elem_json['url'] = elem.a.get("href", "")
                        search_list += [elem_json['url']]
                        
                        elem_json['title'] = elem.a.get("title", "")
                    
                    if x == 1:
                        if not scrapertools.find_single_match(elem.a.get("title", ""), patron_sxe):
                            matches.append(elem_json.copy())
                            elem_json = findvideos_links(item, elem_tr, {'mediatype': 'tvshow'})
                        break
                        
                except Exception:
                    logger.error(elem)
                    logger.error(traceback.format_exc())
                    break

        else:
            for x, elem in enumerate(elem_tr.find_all('td')):
                #if y == 0: logger.error(elem)

                try:
                    if elem.img:
                        elem_json['thumbnail'] = elem.img.get("src", "")
                        continue
                    if elem.a:
                        elem_json['url'] = elem.a.get("href", "")
                        elem_json['title'] = elem.a.get_text(strip=True)
                        continue
                    if elem.span:
                        if ' 0 votes' in elem.span.get_text(strip=True):
                            elem_json = {}
                            break
                        continue

                except Exception:
                    logger.error(elem)
                    logger.error(traceback.format_exc())
                    continue

        if not elem_json.get('url'): continue

        matches.append(elem_json.copy())

    return matches


def seasons(item):
    logger.info()
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    
    imdb_id = soup.find('table', class_='show_info_description').find('a', string=re.compile('(?i)imdb'))
    if imdb_id:
        imdb_id = scrapertools.find_single_match(str(imdb_id), 'imdb.com\/title\/(tt\d+)\/')
        if imdb_id and imdb_id not in item.infoLabels['imdb_id']:
            AlfaChannel.verify_infoLabels_keys(item, {'imdb_id': imdb_id})

    return AlfaChannel.seasons(item, data=soup, **kwargs)


def episodios(item):
    logger.info()

    itemlist = []

    templist = seasons(item)
    data = AlfaChannel.response.soup

    for tempitem in templist:
        itemlist += episodesxseason(tempitem, data=data)

    return itemlist


def episodesxseason(item, data=[]):
    logger.info()

    kwargs['headers'] = {'Referer': item.url}
    #kwargs['matches_post_get_video_options'] = findvideos_matches

    return AlfaChannel.episodes(item, data=data, matches_post=episodesxseason_matches, generictools=True, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    elem_json_list = {}
    findS = finds.copy()

    soup = AHkwargs.get('soup', {})
    findS['episodes'] = {'find_all': [{'tag': ['tr'], 'name': ['hover']}]}
    matches_links = AlfaChannel.parse_finds_dict(soup, findS['episodes'])

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            info = elem.split(' -- ')

            try:
                elem_json['season'], elem_json['episode'] = scrapertools.find_single_match(info[0], '(?i)(\d{1,2})x(\d{1,3})')
                elem_json['season'] = int(elem_json['season'])
                elem_json['episode'] = int(elem_json['episode'])
            except Exception:
                logger.error(info)
                elem_json['season'] = item.contentSeason
                elem_json['episode'] = 0
            if elem_json['season'] != item.contentSeason: continue

            sxe = 's%se%s' % (str(elem_json['season']).zfill(2), str(elem_json['episode']).zfill(2))
            elem_json['url'] = elem_json['url_episode'] = '%ssearch/%s-%s' % (host, item.contentSerieName.replace(' ', '-').lower(), sxe)
            elem_json['title'] = '%sx%s %s' % (str(elem_json['season']), str(elem_json['episode']).zfill(2), (info[2] if len(info) > 2 else ''))

            elem_json['language'] = item.language
            elem_json['quality'] = ''
            elem_json['matches'] = []

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        elem_json_list[sxe] = elem_json.copy()

    for elem_links in matches_links:
        elem_json = {}
        #logger.error(elem_links)

        elem_json = findvideos_links(item, elem_links, elem_json)
        if not elem_json.get('url'): continue

        sxe = 's%se%s' % (str(elem_json['season']).zfill(2), str(elem_json['episode']).zfill(2))
        if elem_json_list.get(sxe):
            elem_json_list[sxe]['matches'] += [elem_json.copy()]
            if elem_json['quality'] not in elem_json_list[sxe]['quality']:
                elem_json_list[sxe]['quality'] += '%s, ' % elem_json['quality']

    for key, elem_json in elem_json_list.items():
        if item.infoLabels['number_of_seasons'] and item.infoLabels['number_of_seasons'] == elem_json['season']:
            if not elem_json['matches']: continue
        elem_json['quality'] = elem_json['quality'].rstrip(', ')

        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()

    kwargs['matches_post_episodes'] = episodesxseason_matches

    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        
        elem_json = findvideos_links(item, elem, elem_json)
        
        if elem_json:
            matches.append(elem_json.copy())

    return matches, langs


def findvideos_links(item, elem_in, elem_json):
    logger.info()

    patron_title = '(?i)(.*?)\s*s(\d{1,2})'
    patron_title_epi = '(?i)(.*?)\s*(\d{4}(?:\s*\d+\s*\d+)?)'
    patron_quality = '(?i)((?:\d{3,4}p|xvid|web)[^-]*)'
    patron_sxe = '(?i)S(\d+)E(\d+)'

    for x, elem in enumerate(elem_in.find_all('td')):
        #logger.error(elem)

        try:
            if x == 1:
                info = elem.a.get('title', '')
                if not info: break

                if item.extra == 'Temporadas' or item.c_type == 'search':
                    if scrapertools.find_single_match(info, patron_title):
                        elem_json['title'], season = scrapertools.find_single_match(info, patron_title)
                        elem_json['title_subs'] = ['Temporada %s' % int(season)]
                    else:
                        elem_json['title'], season = scrapertools.find_single_match(info, patron_title_epi)
                        elem_json['title_subs'] = ['Episodio %s' % season]
                    elem_json['action'] = 'findvideos'
                else:
                    if not scrapertools.find_single_match(info, patron_sxe):
                        elem_json['season'] = item.contentSeason
                        elem_json['episode'] = 1
                    else:
                        season, elem_json['episode'] = scrapertools.find_single_match(info, patron_sxe)
                        if item.contentSeason != int(season): break
                        elem_json['season'] = item.contentSeason
                        elem_json['episode'] = int(elem_json['episode'])
                    elem_json['url_episode'] = '%ssearch/%s-s%se%s' % (host, item.contentSerieName.replace(' ', '-').lower(), 
                                                                       str(elem_json['season']).zfill(2), str(elem_json['episode']).zfill(2))
                    elem_json['title'] = '%sx%s - ' % (str(elem_json['season']), str(elem_json['episode']).zfill(2))
                    
                elem_json['language'] = item.language
                elem_json['server'] = 'torrent'
                elem_json['url'] = ''
                elem_json['quality'] = '*%s' % scrapertools.find_single_match(info, patron_quality)
                elem_json['quality'] = AlfaChannel.find_quality(elem_json, item)

            if x == 2:
                for url in elem.find_all('a'):
                    elem_json['url'] = url.get('href', '')
                    if elem_json['url'].endswith('.torrent'): break

            if x == 3:
                elem_json['torrent_info'] = elem_json['size'] = elem.get_text(strip=True)

            if x == 5:
                try:
                    elem_json['seeds'] = int(elem.get_text(strip=True) or elem.font.get_text(strip=True))
                except Exception:
                    elem_json['seeds'] = 0
                elem_json['torrent_info'] += ', Seeds: %s' % elem_json['seeds']

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            break

    if not elem_json.get('url') or item.contentSerieName.lower().replace(' ', '.') not in elem_json.get('url', '').lower(): 
        elem_json = {}

    return elem_json


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    texto = texto.replace(" ", "-")
    
    try:
        if texto:
            item.url = host + 'search/%s' % texto
            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []
    except Exception:
        for line in sys.exc_info():
            logger.error("%s" % line)
        logger.error(traceback.format_exc())
        return []

 