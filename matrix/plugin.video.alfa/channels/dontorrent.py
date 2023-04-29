# -*- coding: utf-8 -*-
# -*- Channel DonTorrent -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
import traceback

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
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'dontorrent', 
             'host': config.get_setting("current_host", 'dontorrent', default=''), 
             'host_alt': ['https://dontorrent.observer/', 'https://todotorrents.net/', 'https://dontorrent.in/', 
                          'https://verdetorrent.com/', 'https://tomadivx.net/', 'https://donproxies.com/'], 
             'host_black_list': ['https://dontorrent.cash/', 'https://dontorrent.care/', 'https://dontorrent.ms/', 
                                 'https://dontorrent.pictures/', 'https://dontorrent.cloud/', 'https://dontorrent.africa/', 
                                 'https://dontorrent.love/', 'https://dontorrent.ninja/', 'https://dontorrent.plus/', 
                                 'https://dontorrent.chat/', 'https://dontorrent.casa/', 'https://dontorrent.how/', 
                                 'https://dontorrent.surf/', 'https://dontorrent.beer/', 'https://dontorrent.blue/', 
                                 'https://dontorrent.army/', 'https://dontorrent.mba/', 'https://dontorrent.futbol/', 
                                 'https://dontorrent.fail/', 'https://dontorrent.click/', 'https://dontorrent.gy/',
                                 'https://dontorrent.gs/', 'https://dontorrent.me/', 'https://dontorrent.ltd/', 
                                 'https://dontorrent.fans/', 'https://dontorrent.uno/', 'https://dontorrent.ist/', 
                                 'https://dontorrent.vin/', 'https://dontorrent.tf/', 'https://dontorrent.pub/', 
                                 'https://dontorrent.moe/', 'https://dontorrent.soy/', 'https://dontorrent.pet/', 
                                 'https://dontorrent.bid/', 'https://dontorrent.dev/', 'https://dontorrent.dog/', 
                                 'https://dontorrent.vet/', 'https://dontorrent.ch/', 'https://dontorrent.vg/', 
                                 'https://dontorrent.yt/', 'https://dontorrent.tw/', 'https://dontorrent.kim/', 
                                 'https://dontorrent.ink/', 'https://dontorrent.fi/', 'https://dontorrent.wtf/', 
                                 'https://dontorrent.cab/', 'https://dontorrent.bet/', 'https://dontorrent.cx/', 
                                 'https://dontorrent.nl/', 'https://dontorrent.tel/', 'https://dontorrent.pl/', 
                                 'https://dontorrent.cat/', 'https://dontorrent.run/', 'https://dontorrent.wf/', 
                                 'https://dontorrent.pm/', 'https://dontorrent.top/', 'https://dontorrent.re/'], 
             'pattern_proxy': '<a[^>]*class="text-white[^"]+"\s*style="font-size[^"]+"\s*href="([^"]+)"[^>]*>\s*Descargar\s*<\/a>', 
             'proxy_url_test': 'pelicula/25159/The-Batman', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
domain_torrent = 'blazing.network'
host_torrent = 'https://%s' % domain_torrent if 'dontorrent' in host and not '.in/' in host else ''
host_torrent_referer = 'https://%s' % domain_torrent if 'dontorrent' in host else host
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)     # Actualización sólo últ. Temporada?
min_temp = modo_ultima_temp if not modo_ultima_temp else 'continue'

timeout = config.get_setting('timeout_downloadpage', channel)
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/pelicula"
tv_path = '/serie'
docu_path = '/documental'
tienda_path = '/tienda'
language = ['CAST']
url_replace = []

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['text-center']}]}, 
         'sub_menu': {'find': [{'tag': ['div'], 'class': ['torrents-list']}], 'find_all': [{'tag': ['a']}]}, 
         'categories': {},  
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s'], ['&pagina=\d+', '&pagina=%s']], 
         'last_page': {'find': [{'tag': ['ul'], 'class': ['pagination']}], 
                       'find_all': [{'tag': ['a'], '@POS': [-2]}], 'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}]}, 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {},
         'season_num': {'find': [{'tag': ['a']}], 'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}]}, 
         'seasons_search_num_rgx': [['(?i)-(\d+)-(?:Temporada|Miniserie)', None], ['(?i)(?:Temporada|Miniserie)-(\d+)', None]], 
         'seasons_search_qty_rgx': [['(?i)(?:Temporada|Miniserie)(?:-(.*?)(?:\.|\/|-$|$))', None]], 
         'episode_url': '', 
         'episodes': {'find': [{'tag': ['div'], 'class': ['card shadow-sm p-4']}], 'find_all': [{'tag': ['tr']}]}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['div'], 'class': ['card shadow-sm p-4']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax|documental|completo', ''],
                         ['(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', ''], 
                         ['(?i)[-|\(]?\s*HDRip\)?|microHD|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?', ''], 
                         ['(?i)\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|[\(|\[]\S*\.*$', ''],
                         ['(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*|\[*\(*dvd\s*r\d*\w*\]*\)*|[\[|\(]*dv\S*[\)|\]]*', ''], 
                         ['(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?|\s+final', ''], 
                         ['(?i)\s+\[*sub.*.*\s*int\w*\]*', ''], 
                         ['(?i)(?:\s*&#8211;)?\s*temp.*?\d+.*', ''], ['\d?\d?&#.*', ''], ['\d+[x|×]\d+.*', ''], 
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)\s*-\s*\d{1,2}.\s*temporada\s*(?:\[.*?\])?', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'min_temp': min_temp, 'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 15, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': True, 
                      'host_torrent': host_torrent, 'btdigg': True, 'duplicates': [], 'dup_list': 'title', 
                      'force_find_last_page': [5, 999, 'url'], 'btdigg_quality_control': True},
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

    itemlist.append(Item(channel=item.channel, title="Documentales", action="submenu", 
                         url=host, thumbnail=get_thumb("channels_documentary.png"), c_type="series", 
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

        for novedad, contentType, c_type in [['Películas', 'movie', 'peliculas'], 
                                             ['Series', 'tvshow', 'series'], 
                                             ['Documentales', 'documentary', 'series']]:

            itemlist.append(Item(channel=item.channel, title=novedad, action="list_all", 
                                 url=host + "ultimos", thumbnail=get_thumb("channels_%s.png" % contentType), 
                                 c_type=c_type, extra="novedades", category=categoria))

        itemlist.append(Item(channel=item.channel, title='Buscar...', action="search", 
                             url=host, thumbnail=get_thumb("search.png"), 
                             c_type="search", category=categoria))

        itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

        return itemlist

    soup = AlfaChannel.create_soup(host, **kwargs)
    matches_int = AlfaChannel.parse_finds_dict(soup, findS['sub_menu'])

    # En películas las categorías se llaman con Post
    post_alfabeto = 'campo=letra&valor3=%s&valor=&valor2=&pagina=1'
    post_anno = 'campo=anyo&valor=%s&valor2=&valor3=&valor4=&pagina=1'
    post_genero = 'campo=genero&valor3=&valor=&valor2=%s&pagina=1'
    post_calidad = 'campo=tiporip&valor3=&valor=&valor2=&valor5=%s&pagina=1'

    if not matches_int:
        return itemlist

    for elem in matches_int:
        #logger.error(elem)

        title = '[B]%s[/B]' % elem.get_text('|', strip=True).split('|')[0].title()
        url = AlfaChannel.urljoin(host, elem.get('href', '')).strip()
        contentType = 'movie' if item.c_type == "peliculas" else 'documentary' if item.title == "Documentales" else 'tvshow'
        if contentType == 'movie':
            quality = 'HD' if 'hd' in title.lower() or '4k' in title.lower() else ''
        else:
            quality = 'HDTV-720p' if 'hd' in title.lower() else 'HDTV'

        if item.title in title:
            if 'descargar-' in url: 
                url = url.replace('descargar-', '')
            itemlist.append(Item(channel=item.channel, title=title, action="list_all", 
                                 url=url+'/page/1', thumbnail=get_thumb("channels_%s%s.png" % (contentType, '_hd' if quality else '')), 
                                 c_type=item.c_type, quality=quality, category=categoria))

            if item.c_type != 'peliculas':                                      # Para todo, menos películas
                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por [A-Z][/COLOR]', action="section", 
                                     url=url + "/letra-%s/page/1", thumbnail=get_thumb('channels_movie_az.png'), c_type=item.c_type, 
                                     extra='Alfabético', category=categoria))

            elif title == '[B]Películas[/B]':                                   # Categorías sólo de películas
                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por [A-Z][/COLOR]', action="section", 
                                     url=url + "/buscar", thumbnail=get_thumb('channels_movie_az.png'), c_type=item.c_type, 
                                     extra='Alfabético', category=categoria, post=post_alfabeto))

                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por Género[/COLOR]', action="section", 
                                     url=url+'/page/1', thumbnail=get_thumb('genres.png'), c_type=item.c_type, 
                                     extra='Géneros', category=categoria, info=[url + "/buscar", post_genero, 'valor2']))

                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por Año[/COLOR]', action="section", 
                                     url=url + "/buscar", thumbnail=get_thumb('years.png'), c_type=item.c_type, 
                                     extra='Year', category=categoria, post=post_anno))

                itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por Calidad[/COLOR]', action="section", 
                                     url=url+'/page/1', thumbnail=get_thumb('search_star.png'), c_type=item.c_type, 
                                     extra='Quality', category=categoria, info=[url + "/buscar", post_calidad, 'valor5']))

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    if item.extra == "Alfabético":
        itemlist = []

        for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            
            if item.c_type != 'peliculas':
                itemlist.append(item.clone(action="list_all", title=letra, url=item.url % letra.lower()))
            else:
                itemlist.append(item.clone(action="list_all", title=letra, post=item.post % letra))

        return itemlist
    
    if item.extra == "Year":
        from platformcode.platformtools import dialog_numeric
        
        year = dialog_numeric(0, "Introduzca el Año de búsqueda", default="")
        item.post = item.post % year
        
        return list_all(item)

    findS['categories'] = {'find': [{'tag': ['select'], 'name': item.info[2]}], 'find_all': [{'tag': ['option']}]}

    return AlfaChannel.section(item, matches_post=section_matches, finds=findS, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        elem_json['url'] = item.info[0]
        elem_json['title'] = elem.get_text(strip=True)
        elem_json['post'] = item.info[1] % elem_json['title'].replace(' ', '+')
        elem_json['c_type'] = item.c_type

        matches.append(elem_json.copy())

    return matches


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    kwargs['headers'] = {'Referer': item.url}
    
    if item.extra in ['novedades']:
        findS['find'] = {'find_all': [{'tag': ['div'], 'class': ['card shadow-sm p-2']}]}
        
        findS['last_page'] = {}
        if findS['controls'].get('force_find_last_page'): del findS['controls']['force_find_last_page']
        if 'Documentales' in item.title: findS['controls']['btdigg'] = False
    
    elif item.extra in ['Alfabético', 'Géneros', 'Year', 'Quality'] and item.c_type == 'peliculas':
        findS['find'] = {'find_all': [{'tag': ['div'], 'class': ['card shadow-sm p-3 mt-3']}]}

        findS['last_page'] = {'find': [{'tag': ['select'], 'name': ['pagina']}], 
                             'find_all': [{'tag': ['option'], '@POS': [-1], '@ARG': 'value'}]}
        findS['controls'].update({'force_find_last_page': ['', '', 'post']})

    elif item.extra in ['Alfabético'] and item.c_type == 'series':
        findS['find'] = {'find_all': [{'tag': ['div'], 'class': ['card shadow-sm p-4 mt-3']}]}

    elif item.c_type == 'search':
        findS['find'] = {'find_all': [{'tag': ['div'], 'class': ['card shadow-sm p-4']}]}

        findS['last_page'] = {}
        if findS['controls'].get('force_find_last_page'): del findS['controls']['force_find_last_page']
    
    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=True, finds=findS, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        if item.extra in ['novedades']:
            for elem_a in elem.find_all('a', class_='text-primary'):
                elem_json = {}

                try:
                    elem_json['url'] = elem_a.get("href", "")
                    if not elem_json['url'].startswith('http') and not elem_json['url'].startswith('/'):
                        elem_json['url'] = '/%s' % elem_json['url']
                    if (movie_path not in elem_json['url'] and tv_path not in elem_json['url'] \
                                   and docu_path not in elem_json['url']) or tienda_path in elem_json['url']: continue
                    #logger.error(elem_a)
                    
                    elem_json['title'] = elem_a.get_text(strip=True)
                    if scrapertools.find_single_match(elem_json['title'], '(?i)\:?\s*(\d+x\d+)'):
                        elem_json['title_subs'] = ["Episodio %s" % scrapertools.find_single_match(elem_json['title'], '(?i)\:?\s*(\d+x\d+)')]
                    elem_json['title'] = re.sub('(?i)\:?\s*\d+x\d+','', elem_json['title'])

                    if movie_path in elem_json['url']:
                        elem_json['quality'] = '*%s' % re.sub('(?i)\(|\)|Ninguno', '', 
                                                elem_a.find_next_sibling('span', class_='text-muted').get_text(strip=True))
                    elif tv_path in elem_json['url']:
                        elem_json['quality'] = '*%s' % scrapertools.find_single_match(elem_json['title'], '\[([^\]]+)\]')

                except:
                    logger.error(elem_a)
                    logger.error(traceback.format_exc())
                    continue

                if not elem_json.get('url'): continue
                if item.title == 'Películas' and movie_path not in elem_json['url']: continue
                if item.title == 'Series' and tv_path not in elem_json['url']: continue
                if item.title == 'Documentales' and docu_path not in elem_json['url']: continue

                matches.append(elem_json.copy())

        elif item.extra in ['Alfabético'] and item.c_type == 'series':
            for elem_a in elem.find_all('p'):
                elem_json = {}
                #logger.error(elem_a)

                try:
                    if not elem_a.find('a'): continue
                    elem_json['url'] = elem_a.a.get("href", "")
                    elem_json['title'] = elem_a.a.get_text(strip=True)
                    elem_json['quality'] = '*%s' % (scrapertools.find_single_match(elem_json['title'], '\[([^\]]+)\]')\
                                                                .replace('Subs. integrados', '').strip() or 'HDTV')
                    elem_json['language'] = '*'

                except:
                    logger.error(elem_a)
                    logger.error(traceback.format_exc())
                    continue

                if not elem_json.get('url') or tienda_path in elem_json['url']: continue

                matches.append(elem_json.copy())
        
        elif item.extra in ['Géneros', 'Year', 'Quality'] :
            for elem_a in elem.find_all('a', class_='position-relative'):
                elem_json = {}
                #logger.error(elem_a)

                try:
                    elem_json['url'] = elem_a.get("href", "")
                    if movie_path not in elem_json['url'] and tv_path not in elem_json['url']: continue
                    info = AlfaChannel.do_soup(elem_a.get("data-content", ""))
                    elem_json['title'] = info.find('p', class_='lead text-dark mb-0').get_text(strip=True)
                    elem_json['plot'] = info.find('hr', class_='my-2').find_next('p').get_text(strip=True)
                    elem_json['thumbnail'] = elem_a.img.get("src", "")
                    elem_json['quality'] = '*%s' % re.sub('(?i)\(|\)|Ninguno', '', elem_a.get_text(strip=True))
                    elem_json['language'] = '*'

                except:
                    logger.error(elem_a)
                    logger.error(traceback.format_exc())
                    continue

                if not elem_json.get('url'): continue
                if item.c_type == 'peliculas' and tv_path in elem_json['url']: continue
                if item.c_type == 'series' and movie_path in elem_json['url']: continue

                matches.append(elem_json.copy())

        elif item.c_type in ['search']:
            for elem_a in elem.find_all('p'):
                elem_json = {}
                #logger.error(elem_a)

                try:
                    if not elem_a.find('a'): continue
                    elem_json['url'] = elem_a.find('a').get("href", "")
                    if movie_path not in elem_json['url'] and tv_path not in elem_json['url'] and docu_path not in elem_json['url']: continue
                    elem_json['title'] = re.sub('(?i)\s*\(.*?\).*?$', '', elem_a.get_text()).rstrip('.')
                    elem_json['quality'] = '*%s' % scrapertools.find_single_match(elem_a.get_text(), '\((.*?)\)').replace('Ninguno', '')
                    elem_json['language'] = '*'

                except:
                    logger.error(elem_a)
                    logger.error(traceback.format_exc())
                    continue

                if not elem_json.get('url'): continue

                matches.append(elem_json.copy())

            if not AlfaChannel.last_page:
                try:           
                    AlfaChannel.last_page = int(float(elem.find('p', class_="lead").find_next('p', class_="lead")\
                                                .get_text('|', strip=True).split('|')[1]) / float(len(matches))  + 0.500009)
                except:
                    AlfaChannel.last_page = 0

        elif item.c_type in ['peliculas', 'series']:
            for elem_a in elem.find_all('a'):
                elem_json = {}
                #logger.error(elem_a)
                
                try:
                    elem_json['url'] = elem_a.get("href", "")
                    if tienda_path in elem_json['url']: continue
                    elem_json['thumbnail'] = elem_json['title'] = elem_a.img.get("src", "")
                    elem_json['quality'] = item.quality
                    elem_json['language'] = '*CAST'
                    
                    if movie_path in elem_json['url']:
                        # Si es Película obtenermos el título a partir del Thumbnail
                        elem_json['title'] = scrapertools.remove_htmltags(elem_json['title']).strip().strip('.')
                        elem_json['title'] = re.sub('\d{3,7}[-|_|\/]+\d{3,10}[-|\/]', '', elem_json['title'].split('/')[-1])
                        elem_json['title'] = re.sub('--[^\.|$]*|.jpg|.png|$', '', elem_json['title'])
                        elem_json['title'] = re.sub('-\d{6,10}-mmed(?:.jpg|.png|$)', '', elem_json['title'])
                        elem_json['title'] = elem_json['title'].replace('-', ' ').replace('_', ' ').strip()
                    
                    else:
                        # Si es Serie o Documental obtenermos el título a partir de la url
                        if scrapertools.find_single_match(elem_json['url'], '[-|\/]\d{3,10}[-|\/]\d{3,10}[-|\/]*(.*?)(?:.htm|$)'):
                            elem_json['title'] = scrapertools.find_single_match(elem_json['url'], 
                                                 '[-|\/]\d{3,10}[-|\/]\d{3,10}[-|\/]*(.*?)(?:.htm|$)').replace('-', ' ').replace('_', ' ')
                            elem_json['title'] = re.sub('\d+\s*[t|T]emporada', '', elem_json['title'])
                        else:
                            elem_json['title'] = scrapertools.find_single_match(elem_json['url'], 
                                                 '[-|\/]\d{3,10}[-|\/](.*?)(?:.htm|$)').replace('-', ' ').replace('_', ' ')
                        elem_json['title'] = re.sub('(?i)\s*-\s*\d{1,2}.\s*temporada\s*(?:\[.*?\])?', '', elem_json['title']).rstrip('.')
                        if not elem_json['title']:
                            elem_json['title'] = elem_json['url']
                        elem_json['title'] = scrapertools.remove_htmltags(elem_json['title'])

                except:
                    logger.error(elem_a)
                    logger.error(traceback.format_exc())
                    continue
                
                if not elem_json.get('url'): continue
                if item.c_type == 'peliculas' and (tv_path in elem_json['url'] or docu_path in elem_json['url']): continue
                if item.c_type == 'series' and movie_path in elem_json['url']: continue

                matches.append(elem_json.copy())

    return matches

def seasons(item):
    logger.info()

    kwargs['headers'] = {'Referer': item.url}

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
        #logger.error(elem)

        for x, td in enumerate(elem.find_all('td')):
            #logger.error(td)

            if x == 0: 
                epi_rango = False
                error = False
                alt_epi = 0
                try:
                    sxe = td.get_text(strip=True)
                    if not sxe: break
                    if scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)\s*al\s*\d+x(\d+)'):
                        elem_json['season'], elem_json['episode'], alt_epi = \
                                scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)\s*al\s*\d+x(\d+)')
                        epi_rango = True
                    elif scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)\s*al\s*(\d+)'):
                        elem_json['season'], elem_json['episode'], alt_epi = \
                                scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)\s*al\s*(\d+)')
                        epi_rango = True
                    elif scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)\s*-\s*(\d+)'):
                        elem_json['season'], elem_json['episode'], alt_epi = \
                                scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)\s*-\s*(\d+)')
                        epi_rango = True
                    elif scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)'):
                        elem_json['season'], elem_json['episode'] = \
                                scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)')
                    elif scrapertools.find_single_match(sxe, '(\d+)'):
                        elem_json['season'] = 1
                        elem_json['episode'] = scrapertools.find_single_match(sxe, '^(\d+)')
                    elif scrapertools.find_single_match(sxe, '(?i)\[cap\.(\d)(\d{2})\]'):
                        continue
                    else:
                        break
                    elem_json['season'] = contentSeason = int(elem_json['season'])
                    elem_json['episode'] = int(elem_json['episode'])
                    alt_epi = int(alt_epi)
                except:
                    logger.error('ERROR al extraer Temporada/Episodio: %s' % sxe)
                    logger.error(td)
                    logger.error(traceback.format_exc())
                    elem_json['season'] = contentSeason = 1
                    elem_json['episode'] = 1
                    error = True
                
                if epi_rango:                                                   # Si son episodios múltiples, lo guardamos
                    elem_json['title'] = 'al %s' % str(alt_epi).zfill(2)

            if x == 1:
                elem_json['url'] = td.a.get('href', '')
                if error and docu_path not in elem_json['url']: break
                if elem_json['url'].startswith('//'):
                    elem_json['url'] = 'https:%s' % elem_json['url']
                elem_json['quality'] = '*%s' % (scrapertools.find_single_match(elem_json['url'], 
                                               '[-|_]\(?\[?((?:HDTV\d{3,4}p|720p|1080p|HDTV)(?:[-|_]\d+p)?)').replace('_', '-'))

            if x == 3:
                if 'copiar' in td.a.get('title', ''):
                    info = AlfaChannel.do_soup(td.a.get('title', ''))
                    if info and info.a: elem_json['password'] = info.a.get('data-clave', '')

        if not elem_json.get('url', ''): 
            continue
        if docu_path not in elem_json['url'] and elem_json.get('season', 0) != item.contentSeason:
            continue

        elem_json['server'] = 'torrent'
        elem_json['language'] = '*'
        elem_json['size'] = ''
        elem_json['torrent_info'] = ''
        elem_json['title'] = elem_json.get('title', '')
        elem_json['quality'] = AlfaChannel.find_quality(elem_json, item)

        matches.append(elem_json.copy())
    
    return matches


def findvideos(item):
    logger.info()

    kwargs['headers'] = {'Referer': item.url}
    kwargs['matches_post_episodes'] = episodesxseason_matches

    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    videolibrary = AHkwargs.get('videolibrary', False)

    if videolibrary:
        for x, (scrapedtitle, scrapedurl, scrapedpassword, scrapedquality) in enumerate(matches_int):
            elem_json = {}
            #logger.error(matches_int[x])

            if item.infoLabels['mediatype'] in ['episode']:
                elem_json['season'] = item.infoLabels['season']
                elem_json['episode'] = item.infoLabels['episode']

            elem_json['url'] = scrapedurl
            elem_json['title'] = scrapedtitle
            if 'magnet' in elem_json['url']:
                elem_json['torrent_info'] = scrapedpassword
            else:
                if scrapedpassword: elem_json['password'] = scrapedpassword
                elem_json['torrent_info'] = ''
            elem_json['quality'] = '*%s' % scrapedquality
            elem_json['server'] = 'torrent'
            elem_json['language'] = '*CAST'

            matches.append(elem_json.copy())
            item.emergency_urls[1][x] = elem_json.copy()

    else:
        for elem in matches_int:
            elem_json = {}
            #logger.error(elem)

            try:
                elem_json['url'] = elem.find('a', class_='bg-primary').get('href', '')

                elem_json['quality'] = elem.find('b', class_='bold', string=re.compile('Formato:'))\
                                           .find_previous('p').get_text('|', strip=True).split('|')[1]

                if  elem.find('b', class_='bold', string=re.compile('Clave:')):
                    elem_json['password'] = elem.find('b', class_='bold', string=re.compile('Clave:'))\
                                                .find_previous('p').get('data-clave', '')
            except:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue
            
            elem_json['server'] = 'torrent'
            elem_json['language'] = '*CAST'
            elem_json['torrent_info'] = ''
            
            if not elem_json.get('url', ''): continue

            matches.append(elem_json.copy())

    return matches, langs


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    global kwargs
    kwargs = AHkwargs

    texto = texto.replace(" ", "%20")

    try:
        if texto:
            item.url = item.referer = host + 'buscar/' + texto + '/page/1'
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
    global kwargs
    kwargs = AHkwargs

    itemlist = []
    item = Item()

    item.title = "newest"
    item.category_new = "newest"
    item.channel = channel

    try:
        if categoria in ['peliculas', 'series']:
            item.url = host + "ultimos"
            item.c_type = categoria
            item.extra = "novedades"
            item.action = "list_all"
            itemlist = list_all(item)

        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc())
        return []

    return itemlist
