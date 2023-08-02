# -*- coding: utf-8 -*-
# -*- Channel DivXtotal -*-
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
           'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VOSE'}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['torrent']
forced_proxy_opt = 'ProxyWeb'

canonical = {
             'channel': 'divxtotal', 
             'host': config.get_setting("current_host", 'divxtotal', default=''), 
             'host_alt': ["https://www.divxtotal.win/"], 
             'host_black_list': ["https://www.divxtotal.wf/", "https://www.divxtotal.pl/", "https://www.divxtotal.cat/", 
                                 "https://www.divxtotal.fi/", "https://www.divxtotal.dev/", "https://www.divxtotal.ac/", 
                                 "https://www.divxtotal.re/", "https://www.divxtotal.pm/", "https://www.divxtotal.nl/"], 
             'pattern': '<li>\s*<a\s*href="([^"]+)"\s*>\S*\/a><\/li>', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)     # Actualización sólo últ. Temporada?
min_temp = modo_ultima_temp if not modo_ultima_temp else 'continue'
movies_sufix = 'peliculas-hd/'
series_sufix = 'series/'

timeout = config.get_setting('timeout_downloadpage', channel) * 3
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas"
tv_path = '/series'
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['table'], 'class': ['table']}]), 
                       ('find_all', [{'tag': ['tr']}])]), 
         'sub_menu': dict([('find', [{'tag': ['ul'], 'class': ['nav navbar-nav']}]), 
                           ('find_all', [{'tag': ['li']}])]), 
         'categories': dict([('find', [{'tag': ['div'], 'id': 'bloque_cat'}]), 
                             ('find_all', [{'tag': ['a']}])]),  
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/|\/images\/)([^\.]+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': dict([('find', [{'tag': ['ul'], 'class': True}]), 
                              ('get_text', [{'tag': '', '@STRIP': True}])]), 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href', '@TEXT': '\/(\d+)\/'}])]), 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {'find_all': [{'tag': ['h3'], 'string': re.compile('(?i)temporada')}]},
         'season_num': dict([('find', [{'tag': ['a']}]), 
                             ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]), 
         'seasons_search_num_rgx': [['(?i)-(\d+)-(?:Temporada|Miniserie)', None], ['(?i)(?:Temporada|Miniserie)-(\d+)', None]], 
         'seasons_search_qty_rgx': [['(?i)(?:Temporada|Miniserie)(?:-(.*?)(?:\.|\/|-$|$))', None]], 
         'episode_url': '', 
         'episodes': dict([('find', [{'tag': ['div'], 'class': ['row fichseriecapitulos']}]), 
                           ('find_all', [{'tag': ['tbody']}])]), 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['h3'], 'class': ['orange text-center']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax', ''],
                         ['(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', ''], 
                         ['(?i)[-|\(]?\s*HDRip\)?|microHD|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?', ''], 
                         ['(?i)\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|[\(|\[]\S*\.*$', ''],
                         ['(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*|\[*\(*dvd\s*r\d*\w*\]*\)*|[\[|\(]*dv\S*[\)|\]]*', ''], 
                         ['(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?|\s+final', ''], 
                         ['(?i)(?:\s*&#8211;)?\s*temp.*?\d+.*', ''], ['\d?\d?&#.*', ''], ['\d+[x|×]\d+.*', ''], 
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': min_temp, 'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 15, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'host_torrent': host, 'btdigg': True},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Novedades", action="submenu", 
                         url=host, thumbnail=get_thumb("now_playing.png"), c_type="novedades", 
                         category=categoria))
    
    itemlist.append(Item(channel=item.channel, title="Películas", action="submenu", 
                         url=host, thumbnail=get_thumb("channels_movie.png"), c_type="peliculas", 
                         category=categoria))

    itemlist.append(Item(channel=item.channel, title="Series", action="submenu", 
                         url=host, thumbnail=get_thumb("channels_tvshow.png"), c_type="series", 
                         category=categoria))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", 
                         url=host, thumbnail=get_thumb("search.png"), c_type="search", 
                         category=categoria))

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


def submenu(item):
    logger.info()

    itemlist = []
    findS = finds.copy()
    
    if item.c_type == "novedades":
        itemlist.append(Item(channel=item.channel, title='Películas', action="list_all", 
                             url=host, thumbnail=get_thumb("channels_movie_hd.png"), 
                             c_type="peliculas", extra="novedades", category=categoria))

        itemlist.append(Item(channel=item.channel, title='Series', action="list_all", 
                             url=host, thumbnail=get_thumb("channels_tvshow_hd.png"), 
                             c_type="series", extra="novedades", category=categoria))

        itemlist.append(Item(channel=item.channel, title='Buscar...', action="search", 
                             url=host, thumbnail=get_thumb("search.png"), 
                             c_type="search", category=categoria))

        itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

        return itemlist

    soup = AlfaChannel.create_soup(host, **kwargs)
    matches_int = AlfaChannel.parse_finds_dict(soup, findS['sub_menu'])

    if not matches_int:
        return itemlist

    for elem in matches_int:
        #logger.error(elem)

        title = '[B]%s[/B]' % elem.a.get_text(strip=True).title()
        url = AlfaChannel.urljoin(host, elem.a.get('href', ''))
        contentType = 'movie' if item.c_type == "peliculas" else 'tvshow'

        if item.title in title:
            itemlist.append(Item(channel=item.channel, title=title, action="list_all", 
                                 url=url, thumbnail=get_thumb("channels_%s_hd.png" % contentType), 
                                 c_type=item.c_type, category=categoria))
            
            if item.c_type == "peliculas":
                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Géneros[/COLOR]', action="section", 
                                     url=url, thumbnail=get_thumb('genres.png'), 
                                     c_type=item.c_type, extra='Géneros', category=categoria))

            itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Alfabético[/COLOR]', action="section", 
                                 url=url, thumbnail=get_thumb('channels_%s_az.png' % contentType), 
                                 c_type=item.c_type, extra='Alfabético', category=categoria))

    return itemlist


def section(item):
    logger.info()

    if item.extra == "Alfabético":
        itemlist = []

        for letra in ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:

            itemlist.append(item.clone(action="list_all", title=letra, url=item.url + '?s=letra-%s' % letra.lower()))

        return itemlist

    return AlfaChannel.section(item, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.extra == "novedades":
        findS['find'] = {'find_all': [{'tag': ['div'], 'class': ['col-lg-8 title']}]}
    
    elif item.c_type == "series":
        findS['find'] = {'find_all': [{'tag': ['div'], 'class': ['col-lg-3 col-md-3 col-md-4 col-xs-6']}]}
                       
    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=True, finds=findS, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if item.extra == 'novedades':
                elem_json['url'] = elem.a.get("href", "")
                if host not in elem_json['url'] or (movie_path not in elem_json['url'] and tv_path not in elem_json['url']): continue
                
                elem_json['title'] = elem.a.get_text(strip=True)
                if scrapertools.find_single_match(elem_json['title'], '(?i)\s*(\d+x\d+)'):
                    elem_json['title_subs'] = ["Episodio %s" % scrapertools.find_single_match(elem_json['title'], '(?i)\s*(\d+x\d+)')]
                elem_json['title'] = re.sub('(?i)\s*\d+x\d+','', elem_json['title'])

                elem_json['thumbnail'] = scrapertools.find_single_match(elem.a.get("onmouseover", ""), "javascript:cambia_[^\(]+\('([^']+)'")
                
                if movie_path+'-' in elem_json['url']:
                    elem_json['quality'] = '*%s' % scrapertools.find_single_match(elem_json['url'], 
                                                                                  '%s-([^\/]+)\/' % movie_path).upper().replace('-', '')
            elif item.c_type in ['peliculas', 'search']:
                for x, td in enumerate(elem.find_all('td')):
                    if x == 0:
                        elem_json['url'] = td.a.get('href', '')
                        elem_json['title'] = td.get_text(strip=True)
                    #if x == 2 and item.c_type in ['peliculas']: elem_json['year'] = scrapertools.find_single_match(td.get_text(strip=True), '\d{4}')

            else:
                elem_json['url'] = elem.find('p', class_="secconimagen").a.get("href", "")
                elem_json['title'] = elem.find('p', class_="seccontnom").a.get('title', '')
                elem_json['thumbnail'] = elem.find('p', class_="secconimagen").img.get("src", "")
                #elem_json['year'] = scrapertools.find_single_match(elem.find('p', class_="seccontfetam").get_text(strip=True), '\d{4}')

            elem_json['quality'] = elem_json.get('quality', '') or 'HDTV' if tv_path in elem_json['url'] else ''

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url'): continue
        if item.c_type == 'peliculas' and tv_path in elem_json['url']: continue
        if item.c_type == 'series' and movie_path in elem_json['url']: continue
        if tv_path not in elem_json['url'] and movie_path not in elem_json['url']: continue

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

    kwargs['headers'] = {'Referer': item.url}
    kwargs['matches_post_get_video_options'] = findvideos_matches

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, generictools=True, finds=finds, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}

        for y, tr in enumerate(elem.find_all('tr')):
            #logger.error(tr)
            for x, td in enumerate(tr.find_all('td')):

                if x == 0: 
                    try:
                        sxe = td.a.get_text(strip=True)
                        if not sxe: break
                        if scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)'):
                            season = scrapertools.find_single_match(sxe, '(?i)(\d+)x\d+')
                            if len(season) > 2:
                                pos = len(str(item.contentSeason)) * -1
                                season = season[pos:]
                            episode = scrapertools.find_single_match(sxe, '(?i)\d+x(\d+)')
                        elem_json['season'] = int(season or 1)
                        elem_json['episode'] = int(episode or 1)
                        if elem_json['season'] != item.contentSeason: break
                    except:
                        logger.error(td)
                        logger.error(traceback.format_exc())
                        break
                
                    elem_json['language'] = td.img.get('src', '')
                    AlfaChannel.get_language_and_set_filter(elem_json['language'], elem_json)

                    elem_json['url'] = td.a.get('href', '')
                
                if x == 2:
                    if host not in elem_json['url'] and td.a.get('href', ''):
                        elem_json['url'] = td.a.get('href', '')

            if elem_json.get('season', 0) != item.contentSeason:
                break
            if not elem_json.get('url', ''): 
                continue

            elem_json['server'] = 'torrent'
            elem_json['quality'] = 'HDTV'
            elem_json['size'] = ''
            elem_json['torrent_info'] = ''

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
            elem_json['language'] = '*CAST'
            elem_json['quality'] = '*'
            elem_json['torrent_info'] = ''

            matches.append(elem_json.copy())
            item.emergency_urls[1][x] = elem_json.copy()

    else:
        for elem in matches_int:
            #logger.error(elem)
            
            if '<td' not in str(elem): continue
            for tr in elem.find_all('tr'):
                elem_json = {}
                #logger.error(tr)

                try:
                    for x, td in enumerate(tr.find_all('td')):
                        if td.has_attr('data-th'):
                            if x == 0: 
                                AlfaChannel.get_language_and_set_filter(td, elem_json)
                                if not elem_json['language']: elem_json['language'] = '*%s' % td.img.get('src', '').replace('N/A', '')
                            if x == 2: elem_json['quality'] = '*%s' % td.get_text().replace('-', '').replace('N/A', '')
                            if x == 3: elem_json['torrent_info'] =  td.get_text().replace('-', '').replace('N/A', '')
                            if x == 4:
                                elem_json['url'] = td.a.get('href', '')
                                if host not in elem_json['url'] and elem.find('a', class_="opcion_2").get('href', ''):
                                    elem_json['url'] = elem.find('a', class_="opcion_2").get('href', '')

                        elif '<a class=' in str(tr):
                            if x == 1: elem_json['url'] = td.a.get('href', '')
                            if x == 2: 
                                if host not in elem_json['url'] and elem.find('a', class_="opcion_2").get('href', ''):
                                    elem_json['url'] = elem.find('a', class_="opcion_2").get('href', '')
                                AlfaChannel.get_language_and_set_filter(td, elem_json)
                                if not elem_json['language']: elem_json['language'] = '*'
                                elem_json['quality'] = '*3D'
                                elem_json['torrent_info'] = ''

                        else:
                            break

                    elem_json['server'] = 'torrent'

                    if elem_json.get('url', ''):
                        elem_json['url'] = elem_json['url'].replace("download/torrent.php', {u: ", "download_tt.php?u=")
                    if '.php?u=http' in elem_json.get('url', ''):
                        elem_json['url'] = elem_json['url'].replace(host[:-1], '')

                except:
                    logger.error(tr)
                    logger.error(traceback.format_exc())

                if not elem_json.get('url', ''): 
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

    item.url = host + '?s=%s' % texto

    try:
        if texto:
            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        logger.error(traceback.format_exc())
        return []
 
 
def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    itemlist = []
    item = Item()

    item.title = "newest"
    item.category_new = "newest"
    item.channel = channel

    try:
        for cat in ['peliculas', 'series']:
            if cat != categoria: continue
                
            item.c_type = cat
            if cat == 'peliculas': item.url = host + movies_sufix
            if cat == 'series': item.url = host + series_sufix

            item.extra = "novedades"
            item.action = "list_all"
            itemlist = list_all(item)

        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()

    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc())
        return []

    return itemlist
