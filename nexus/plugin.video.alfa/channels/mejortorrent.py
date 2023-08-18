# -*- coding: utf-8 -*-
# -*- Channel MejorTorrent -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAllChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

IDIOMAS = AlfaChannelHelper.IDIOMAS_T
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES_T
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS_T
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'mejortorrent', 
             'host': config.get_setting("current_host", 'mejortorrent', default=''), 
             'host_alt': ["https://www3.mejortorrent.rip/"], 
             'host_black_list': ['https://mejortorrent.cc', 'https://mejortorrent.one/', 
                                 'https://mejortorrent.nz', 'https://www.mejortorrentes.org/'], 
             'pattern': '<div\s*class="header-logo[^>]*>\s*<a\s*href="([^"]+)"', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_torrent = host
channel = canonical['channel']
categoria = channel.capitalize()
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)     # Actualización sólo últ. Temporada?
min_temp = modo_ultima_temp if not modo_ultima_temp else 'continue'

timeout = config.get_setting('timeout_downloadpage', channel)
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/pelicula"
tv_path = '/serie'
documental_path = '/documental'
language = ['CAST']
url_replace = []

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['cards', 'flex flex-row mb-2']}]}, 
         'sub_menu': {}, 
         'categories': {},  
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': dict([('find', [{'tag': ['nav'], 'role': ['navigation']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], '@ARG': 'href', '@TEXT': '\/(\d+)'}])]), 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {},
         'season_num': {}, 
         'seasons_search_num_rgx': [['(?i)\s*-?\s*(\d{1,2}).?\s*-?\s*Temp\w*[^$]*$', None]], 
         'seasons_search_qty_rgx': [['(?i)(?:Temporada|Miniserie)(?:-?\[?\(?(.*?)\)?\]?(?:\.|\/|-$|$))', None]], 
         'episode_url': '', 
         'episodes': dict([('find', [{'tag': ['tbody'], 'class': ['bg-mejortorrent-green']}]), 
                           ('find_all', [{'tag': ['tr']}])]), 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'profile_labels': {}, 
         'findvideos': {'find_all': [{'tag': ['a'], 'class': 'text-sm ml-2'}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax', ''],
                         ['(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', ''], 
                         ['(?i)[-|\(]?\s*HDRip\)?|microHD|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?', ''], 
                         ['(?i)\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|[\(|\[]\S*\.*$', ''],
                         ['(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*|\[*\(*dvd\s*r\d*\w*\]*\)*|[\[|\(]*dv\S*[\)|\]]*', ''], 
                         ['(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?', ''], 
                         ['(?i)(?:\s*&#8211;)?\s*temp.*?\d+.*', ''], ['\d?\d?&#.*', ''], ['\d+[x|×]\d+.*', ''], 
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)(?:libro|volumen)?\s+\d{1,2}$', ''], 
                         ['(?i)\s*-?\s*\d{1,2}.?\s*-?\s*Temp\w*[^$]*$', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'min_temp': min_temp, 'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 15, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': True, 
                      'host_torrent': host_torrent, 'duplicates': [['(?i)\s*-?\s*\d{1,2}.?\s*-?\s*Temp\w*[^$]*$', '']], 
                      'join_dup_episodes': False},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu', url=host, 
                         thumbnail=get_thumb('channels_movie.png'), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu', url=host, 
                         thumbnail=get_thumb('channels_tvshow.png'), c_type='series'))

    itemlist.append(Item(channel=item.channel, title='Documentales',  action='sub_menu', url=host, 
                         thumbnail=get_thumb('channels_documentary.png'), c_type='documentales'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         thumbnail=get_thumb("search.png")))

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


def sub_menu(item):
    logger.info()

    itemlist = list()

    if item.c_type in ['peliculas', 'series']:
        itemlist.append(Item(channel=item.channel, title='Estrenos', url=host + 'torrents', action='list_all',
                             thumbnail=get_thumb('news.png'), c_type=item.c_type, extra='Estrenos'))

    if item.c_type == 'peliculas':
        for url_sufix in ['', '-hd', '-4k']:
            itemlist.append(Item(channel=item.channel, title='Películas %s' % url_sufix.replace('-', '').upper(), 
                                 url=item.url + 'peliculas%s' % url_sufix, action='list_all',
                                 thumbnail=get_thumb('channels_movie%s.png' % url_sufix.replace('-', '_')), c_type=item.c_type))
            if not url_sufix:
                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]por Género[/COLOR]', action='section', 
                                     url=item.url + 'peliculas%s' % url_sufix, 
                                     thumbnail=get_thumb('genres.png'), c_type=item.c_type, extra='genre'))
                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]por Año[/COLOR]', action='section', 
                                     url=item.url + 'peliculas%s' % url_sufix,
                                     thumbnail=get_thumb('years.png'), c_type=item.c_type, extra='year'))
                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]por Calidad[/COLOR]', action='section', 
                                     url=item.url + 'peliculas%s' % url_sufix,
                                     thumbnail=get_thumb('search_star.png'), c_type=item.c_type, extra='quality'))
                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]por A-Z[/COLOR]', action='section', 
                                     url=item.url + 'peliculas%s' % url_sufix,
                                     thumbnail=get_thumb('channels_movie_az.png'), c_type=item.c_type, extra='letter'))

    elif item.c_type == 'series':
        for url_sufix in ['', '-hd']:
            itemlist.append(Item(channel=item.channel, title='Series %s' % url_sufix.replace('-', '').upper(), 
                                 url=item.url + 'series%s' % url_sufix, action='list_all',
                                 thumbnail=get_thumb('channels_tvshow%s.png' % url_sufix.replace('-', '_')), c_type=item.c_type))
            if not url_sufix:
                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]por A-Z[/COLOR]', action='section', 
                                     url=item.url + 'series%s' % url_sufix,
                                     thumbnail=get_thumb('channels_tvshow_az.png'), c_type=item.c_type, extra='letter'))

    else:
        for url_sufix in ['']:
            itemlist.append(Item(channel=item.channel, title='Documentales %s' % url_sufix.replace('-', '').upper(), 
                                 url=item.url + 'documentales%s' % url_sufix, action='list_all',
                                 thumbnail=get_thumb('channels_documentary.png'), c_type=item.c_type))
            if not url_sufix:
                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]por A-Z[/COLOR]', action='section', 
                                     url=item.url + 'documentales%s' % url_sufix,
                                     thumbnail=get_thumb('channels_documentary.png'), c_type=item.c_type, extra='letter'))

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    if item.extra in ['genre', 'year', 'quality']:
        findS['categories'] = dict([('find', [{'tag': ['select'], 'id': [item.extra]}]), 
                                    ('find_all', [{'tag': ['option']}])])
        findS['url_replace'] = [[host, '%s%s/%s/' % (host, item.url.split('/')[-1], item.extra)]]

    elif item.extra == 'letter':
        itemlist = []

        for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:

            itemlist.append(item.clone(action="list_all", title=letra, url=item.url + '/%s/%s' % (item.extra, letra.lower())))

        return itemlist

    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
                
    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=True, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    thumbs_index = {}
    findS = AHkwargs.get('finds', finds)

    for elem_block in matches_int:
        
        for elem in elem_block.find_all(['a', 'b']):
            elem_json = {}
            #logger.error(elem)

            try:
                if elem.img and elem.img.get("src", ""):
                    thumbs_index[elem.get("href", "")] = elem.img.get("src", "").split('=')[-1]
                    continue
                    
                if not elem.get("href", ""):
                    if item.c_type == 'peliculas' and matches and not matches[-1].get('quality'):
                        matches[-1]['quality'] = '*%s' % elem.get_text(strip=True).replace('(', '').replace(')', '')
                    continue

                elem_json['url'] = elem.get("href", "") or elem.a.get("href", "")
                if item.c_type == 'peliculas' and movie_path not in elem_json['url']: continue
                if item.c_type == 'series' and tv_path not in elem_json['url']: continue
                if item.c_type == 'documentales' and documental_path not in elem_json['url']: continue

                info = elem.get_text('|', strip=True).replace('-', ' ').split('|')
                elem_json['title'] = info[0]
                elem_json['quality'] = '*%s' % info[1].replace('(', '').replace(')', '') if len(info) > 1 else \
                                               'HDTV-720p' if item.c_type in ['series', 'documentales'] and '720p' in elem_json['url'] else \
                                               'HDTV' if item.c_type in ['series', 'documentales'] else ''
            except:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue

            if not elem_json.get('url'): continue

            matches.append(elem_json.copy())

    for elem_json in matches:
        if elem_json['url'] in thumbs_index:
            elem_json['thumbnail'] = thumbs_index[elem_json['url']]

    return matches


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item, **kwargs)


def episodios(item):
    logger.info()

    itemlist = []

    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    kwargs['matches_post_get_video_options'] = findvideos_matches

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, generictools=True, finds=finds, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        for x, td in enumerate(elem.find_all('td')):
            #logger.error(td)

            if x == 1: 
                try:
                    season = 0
                    sxe = td.get_text(strip=True)
                    if scrapertools.find_single_match(sxe, '(?i)temp\w*\s+(\d+)\s+comp\w*'):
                        season = scrapertools.find_single_match(sxe, '(?i)temp\w*\s+(\d+)\s+comp\w*')
                        episode = 1
                    elif scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)'):
                        season, episode = scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)')
                    else:
                        sxe = elem.find_all('td')[-1].a.get('href', '')
                        season, episode = scrapertools.find_single_match(sxe, '(?i)\[Cap\.(\d{1})(\d{2})\]')
                        elem_json['quality'] = '*%s' % td.get_text(strip=True).replace('N/A', '')\
                                                       .replace('HDRip', 'HDTV').replace('720p', 'HDTV-720p').replace('Dvdrip', 'HDTV') or 'HDTV'
                    if len(season) > 2:
                        pos = len(str(item.contentSeason)) * -1
                        season = season[pos:]
                    elem_json['season'] = int(season or 1)
                    elem_json['episode'] = int(episode or 1)
                    if elem_json['season'] != item.contentSeason: break
                    if scrapertools.find_single_match(sxe, '(?i)\d+x\d+-(\d+)'):
                        elem_json['title'] = 'al %s' % scrapertools.find_single_match(sxe, '(?i)\d+x\d+-(\d+)')
                except:
                    logger.error(td)
                    logger.error(traceback.format_exc())
                    break

            if x == 3:
                if td.p:
                    elem_json['password'] = td.get_text(strip=True).replace('N/A', '').replace('Sin clave', '')
                else:
                    elem_json['torrent_info'] = td.get_text(strip=True).replace('N/A', '')

            if x == 4:
                elem_json['url'] = td.a.get('href', '')
                if not elem_json.get('quality'): elem_json['quality'] = 'HDTV-720p' if '720p' in elem_json['url'] else 'HDTV'

        if elem_json.get('season', 0) != item.contentSeason:
            continue
        if not elem_json.get('url', ''): 
            continue

        elem_json['server'] = 'torrent'
        elem_json['title'] = elem_json.get('title', '')
        elem_json['language'] = item.language
        elem_json['size'] = ''
        elem_json['torrent_info'] = elem_json.get('torrent_info', '')

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
    videolibrary = AHkwargs.get('videolibrary', False)
    soup = AHkwargs.get('soup', {})
    
    try:
        year = int(soup.find('div', class_="px-2 py-4 border-b border-gray-400").find('p').find_next('p').find('a').get_text(strip=True))
        if year and year != item.infoLabels.get('year', 0):
            AlfaChannel.verify_infoLabels_keys(item, {'year': year})
    except Exception:
        pass

    if videolibrary:
        for x, (scrapedurl) in enumerate(matches_int):
            elem_json = {}
            #logger.error(matches_int[x])

            if item.infoLabels['mediatype'] in ['episode']:
                elem_json['season'] = item.infoLabels['season']
                elem_json['episode'] = item.infoLabels['episode']

            elem_json['url'] = scrapedurl
            elem_json['server'] = 'torrent'
            elem_json['language'] = language
            elem_json['quality'] = item.quality

            matches.append(elem_json.copy())
            item.emergency_urls[1][x] = elem_json.copy()

    else:
        for elem in matches_int:
            elem_json = {}
            #logger.error(elem)
            
            try:
                elem_json['url'] = elem.get('href', '')
                elem_json['server'] = 'torrent'
                elem_json['quality'] = item.quality

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


def get_page_num(item):
    logger.info()
    # Llamamos al método que salta al nº de página seleccionado

    return AlfaChannel.get_page_num(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    texto = texto.replace(" ", "+")

    try:
        if texto:
            item.url = "%sbusqueda?q=%s" % (host, texto)
            item.texto = texto
            item.c_type = 'search'
            return list_all(item)
        else:
            return []
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []
