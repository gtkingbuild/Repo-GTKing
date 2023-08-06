# -*- coding: utf-8 -*-
# -*- Channel SubTorrent -*-
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
             'channel': 'subtorrents', 
             'host': config.get_setting("current_host", 'subtorrents', default=''), 
             'host_alt': ['https://www.subtorrents.eu/'], 
             'host_black_list': ['https://www.subtorrents.re/', 'https://www.subtorrents.do/'], 
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
movie_path = "/peliculas"
tv_path = '/series'
language = []
url_replace = []
languagues = {'1': 'español', '512': 'latino', '2': 'subtitulada'}

finds = {'find': dict([('find', [{'tag': ['tbody']}]), 
                       ('find_all', [{'tag': ['tr'], 'class': ['fichserietabla_b']}])]), 
         'sub_menu': {}, 
         'categories': {},  
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/|images\/idioma\/)(\d+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href', '@TEXT': '\/(\d+)\/'}])]), 
         'year': {}, 
         'season_episode': {}, 
         'seasons': dict([('find', [{'tag': ['div'], 'class': ['fichseriecapitulos']}]), 
                          ('find_all', [{'tag': [], 'string': re.compile('(?i)temporada\s*\d{1,2}')}])]), 
         'season_num': {}, 
         'seasons_search_num_rgx': '(?i)temp\w*\s+(\d+)', 
         'seasons_search_qty_rgx': [], 
         'episode_url': '', 
         'episodes': dict([('find', [{'tag': ['div'], 'id': ['tabla%s']}]), 
                           ('find_all', [{'tag': ['tr']}])]), 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['div'], 'class': ['secciones']}]}, 
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
         'controls': {'min_temp': min_temp, 'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 15, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'host_torrent': host_torrent, 'duplicates': []},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, url=host, title="Películas", action="submenu", 
                         thumbnail=get_thumb("channels_movie_hd.png"), c_type="peliculas"))

    itemlist.append(Item(channel=item.channel, url=host, title="Series", action="submenu", 
                         thumbnail=get_thumb("channels_tvshow.png"), c_type="series"))

    itemlist.append(Item(channel=item.channel, url=host, title="Buscar...", action="search", 
                         thumbnail=get_thumb("search.png"), c_type="search"))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                         folder=False, thumbnail=get_thumb("next.png")))

    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                         thumbnail=get_thumb("setting_0.png")))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)                                # Activamos Autoplay

    return itemlist


def configuracion(item):
    from platformcode import platformtools

    ret = platformtools.show_channel_settings()

    return platformtools.itemlist_refresh()

    
def submenu(item):
    logger.info()

    itemlist = []

    if item.c_type == "peliculas":

        itemlist.append(item.clone(title="Novedades", action="list_all", url=host + "peliculas-subtituladas/?filtro=estrenos", 
                                   thumbnail=get_thumb("now_playing.png")))
        itemlist.append(item.clone(title="Películas", action="list_all", url=host + "peliculas-subtituladas/", 
                                   thumbnail=get_thumb("channels_movie.png")))
        itemlist.append(item.clone(title=" - [COLOR paleturquoise]Latino[/COLOR]", action="list_all", 
                                   url=host + "peliculas-subtituladas/?filtro=audio-latino", 
                                   thumbnail=get_thumb("channels_latino"), extra='latino'))
        itemlist.append(item.clone(title=" - [COLOR paleturquoise]3D[/COLOR]", action="list_all", 
                                   url=host + "peliculas-3d/", 
                                   thumbnail=get_thumb("channels_movie.png")))
        itemlist.append(item.clone(title=" - [COLOR paleturquoise]Calidad DVD[/COLOR]", action="list_all", 
                                   url=host + "calidad/dvd-full/", 
                                   thumbnail=get_thumb("channels_movie.png")))
        itemlist.append(item.clone(title=" - [COLOR paleturquoise]Por [A-Z][/COLOR]", action="section", 
                                   url=host + "peliculas-subtituladas/?s=letra-%s", 
                                   thumbnail=get_thumb("channels_movie_az.png")))

    if item.c_type == "series":

        itemlist.append(item.clone(title="Series", action="list_all", url=host + "series-2/", 
                                   thumbnail=get_thumb("channels_tvshow.png")))
        itemlist.append(item.clone(title=" - [COLOR paleturquoise]Por [A-Z][/COLOR]", action="section", 
                                   url=host + "series-2/?s=letra-%s", 
                                   thumbnail=get_thumb("channels_tvshow_az.png")))

    return itemlist


def section(item):
    logger.info()

    itemlist = []

    for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:

        itemlist.append(item.clone(action="list_all", title=letra, url=item.url % letra))

    return itemlist


def list_all(item):
    logger.info()

    findS = finds.copy()

    if item.c_type == 'series':
        findS['find'] = dict([('find', [{'tag': ['table'], 'class': ['tablaseries2']}]), 
                              ('find_all', [{'tag': ['td']}])])

    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=True, finds=findS, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        if item.c_type in ['peliculas', 'search']:
            for x, td in enumerate(elem.find_all('td')):

                try:
                    if x == 0: 
                        if 'latino' in item.extra:
                            elem_json['language'] = '*latino'
                        else:
                            elem_json['language'] = '*%s' % languagues.get(scrapertools.find_single_match(td.img.get('src', ''), 
                                                                           findS['get_language_rgx']) or '1', 'VOSE')
                        elem_json['url'] = td.a.get('href', '')
                        elem_json['title'] = td.a.get_text(strip=True)

                    if x == 2: elem_json['quality'] = '*%s' % td.get_text(strip=True)
                    if x == 3: elem_json['quality'] = '*%s' % td.get_text(strip=True)

                except:
                    logger.error(td)
                    logger.error(elem)
                    logger.error(traceback.format_exc())
                    continue
        else:
            try:
                elem_json['url'] = elem.a.get('href', '')
                elem_json['title'] = elem.a.get('title', '')
                elem_json['thumbnail'] = elem.a.img.get('src', '')
                if len(elem.get_text('|', strip=True).split('|')) > 1:
                    elem_json['title_subs'] = [elem.get_text('|', strip=True).split('|')[1]\
                                               .replace('SUBTITULADO', '').replace('subtitulado', '')]
                elem_json['quality'] = '*'
                elem_json['language'] = '*'

            except:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue

        if not elem_json.get('url'): continue
        if tv_path in elem_json['url'] and elem_json['quality'] == '*': elem_json['quality'] = '*HDTV'

        matches.append(elem_json.copy())

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

    findS = finds.copy()

    findS['episodes'] = dict([('find', [{'tag': ['div'], 'id': ['tabla%s' % item.contentSeason]}]), 
                              ('find_all', [{'tag': ['tr']}])])

    kwargs['matches_post_get_video_options'] = findvideos_matches
    kwargs['headers'] = {'Referer': item.url}

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, generictools=True, finds=findS, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            try:
                season = 0
                sxe = elem.get_text(strip=True)
                if scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)'):
                    season, episode = scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)')
                elif scrapertools.find_single_match(sxe, '(?i)\[Cap\.(\d{1})(\d{2})\]'):
                    season, episode = scrapertools.find_single_match(sxe, '(?i)\[Cap\.(\d{1})(\d{2})\]')
                else:
                    logger.error(elem)
                    continue

                if len(season) > 2:
                    pos = len(str(item.contentSeason)) * -1
                    season = season[pos:]
                elem_json['season'] = int(season or 1)
                elem_json['episode'] = int(episode or 1)
                if elem_json['season'] != item.contentSeason: continue
                if scrapertools.find_single_match(sxe, '(?i)\d+x\d+-(\d+)'):
                    elem_json['title'] = 'al %s' % scrapertools.find_single_match(sxe, '(?i)\d+x\d+-(\d+)')
            except:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue
            
            elem_json['url'] = AlfaChannel.convert_url_base64(elem.td.a.get('href', ''), host, force_host=True)
            elem_json['quality'] = '*%s' % item.quality
            elem_json['language'] = '*%s' % languagues.get(scrapertools.find_single_match(elem.td.img.get('src', ''), 
                                                           findS['get_language_rgx']) or '1', item.language)
            elem_json['server'] = 'torrent'
            elem_json['torrent_info'] = ''
            
            if elem.find('td', class_='capitulosubtitulo').a:
                    elem_json['subtitle'] = []
                    for sub in elem.find('td', class_='capitulosubtitulo').find_all('a'):
                        subtitle = AlfaChannel.create_soup(sub.get('href', ''), hide_infobox=True)\
                                                           .find('tr', class_='fichserietabla_b').a.get('href', '')
                        elem_json['subtitle'] += [subtitle.replace(AlfaChannel.obtain_domain(subtitle, scheme=True), host.rstrip('/'))]
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url', ''): 
            continue

        elem_json['server'] = 'torrent'

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

    if videolibrary:
        for x, (scrapedurl) in enumerate(matches_int):
            elem_json = {}
            #logger.error(matches_int[x])

            if item.infoLabels['mediatype'] in ['episode']:
                elem_json['season'] = item.infoLabels['season']
                elem_json['episode'] = item.infoLabels['episode']

            elem_json['url'] = scrapedurl
            elem_json['server'] = 'torrent'
            elem_json['language'] = '*'
            elem_json['quality'] = '*'
            elem_json['torrent_info'] = ''

            matches.append(elem_json.copy())
            item.emergency_urls[1][x] = elem_json.copy()

    else:
        for elem in matches_int[0].find_all('a', target='_blank'):
            elem_json = {}
            #logger.error(elem)
            
            try:
                elem_json['url'] = AlfaChannel.convert_url_base64(elem.get('href', ''), host, force_host=True)
                elem_json['quality'] = '*%s' % item.quality
                elem_json['language'] = '*%s' % item.language
                elem_json['server'] = 'torrent'
                elem_json['torrent_info'] = ''
                if matches_int[0].find('div', class_='fichasubtitulos').a:
                    elem_json['subtitle'] = []
                    for sub in matches_int[0].find('div', class_='fichasubtitulos').label.find_all('a'):
                        subtitle = AlfaChannel.create_soup(sub.get('href', ''), hide_infobox=True)\
                                                  .find('tr', class_='fichserietabla_b').a.get('href', '')
                        elem_json['subtitle'] += [subtitle.replace(AlfaChannel.obtain_domain(subtitle, scheme=True), host.rstrip('/'))]

            except:
                logger.error(elem)
                logger.error(traceback.format_exc())

            if not elem_json.get('url', '') or elem_json['url'] in str(matches): 
                continue

            matches.append(elem_json.copy())

    return matches, langs


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    texto = texto.replace(" ", "+")

    try:
        item.url = item.url + "?s=%s" % texto

        if texto:
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

 
def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    itemlist = []
    item = Item()

    try:
        if categoria == 'peliculas':
            item.url = host + "peliculas-subtituladas/?filtro=estrenos"
            item.c_type = "peliculas"
            item.channel = channel
            item.category_new= 'newest'
            item.action= 'list_all'

            itemlist = list_all(item)

        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
