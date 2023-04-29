# -*- coding: utf-8 -*-
# -*- Channel Rarbg -*-
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
from lib.generictools import check_blocked_IP
from lib.AlfaChannelHelper import DictionaryAllChannel

IDIOMAS = {'es': 'CAST', 'la': 'LAT', 'us': 'VOSE', 'ES': 'CAST', 'LA': 'LAT', 'US': 'VOSE', 
           'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VOSE', 'SPANISH': 'CAST', }
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['torrent']
forced_proxy_opt = None

canonical = {
             'channel': 'rarbg', 
             'host': config.get_setting("current_host", 'rarbg', default=''), 
             'host_alt': ["https://rarbgaccessed.org/", "https://rarbgget.org/", "https://proxyrarbg.org/"], 
             'host_black_list': ["https://rarbgmirror.org/"], 
             'host_black_list': [], 
             'status': 'SIN CANONICAL NI DOMINIO', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True, 'check_blocked_IP': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)     # Actualización sólo últ. Temporada?
min_temp = modo_ultima_temp if not modo_ultima_temp else 'continue'

timeout = config.get_setting('timeout_downloadpage', channel)
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/torrent"
tv_path = '/tv'
language = ['VO']
url_replace = []

finds = {'find': {'find_all': [{'tag': ['tr'], 'class': ['lista2']}]}, 
         'sub_menu': {}, 
         'categories': {}, 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {'find': [{'tag': ['div'], 'id': ['pager_links']}], 
                       'find_all': [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}]}, 
         'next_page_rgx': [['\?page=\d+', '?page=%s']], 
         'last_page': {}, 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {'find_all': [{'tag': ['h1'], 'class': ['black']}]}, 
         'season_num': {'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}]}, 
         'seasons_search_num_rgx': [], 
         'seasons_search_qty_rgx': [], 
         'episode_url': '', 
         'episodes': {'find_all': [{'tag': ['div'], 'class': ['tvcontent']}]}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['tr'], 'class': ['lista2', 'lista_related']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax|documental|completo', ''],
                         ['[\(|\[]\s+[\)|\]]', '']],
         'quality_clean': [['(?i)proper\s*|unrated\s*|directors\s*|cut\s*|german\s*|repack\s*|internal\s*|real\s*|korean\s*', ''],
                           ['(?i)extended\s*|masted\s*|docu\s*|oar\s*|super\s*|duper\s*|amzn\s*|uncensored\s*|hulu\s*', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'min_temp': min_temp, 'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 15, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'host_torrent': host, 'btdigg': False, 'duplicates': [], 'dup_list': 'title', 'dup_movies': True, 
                      'join_dup_episodes': False, 'manage_torrents': False},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = []
    plot =  '[COLOR hotpink][B]NOTA: [/COLOR][COLOR yellow]Esta web puede considerar una intrusión más de '
    plot += '1 usuario o 10 accesos por IP/Router.[/B][/COLOR]\n\n'
    plot += '[COLOR yellow]Si es bloqueado, [/COLOR][COLOR limegreen][B]renueve la IP en el Router[/B][/COLOR]'
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all", 
                         url=host + "torrents.php?category=movies&search=&order=data&by=DESC", 
                         thumbnail=get_thumb("channels_vos.png"), c_type="peliculas", 
                         contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Calidades[/COLOR]", action="section", 
                         url=host + "torrents.php?category=movies&search=&order=data&by=DESC", 
                         thumbnail=get_thumb("channels_movie_hd.png"), c_type="peliculas", 
                         contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Géneros[/COLOR]", action="section", 
                         url=host + "catalog/movies/", 
                         thumbnail=get_thumb("genres.png"), c_type="peliculas", 
                         contentPlot=plot))
    
    itemlist.append(Item(channel=item.channel, title="Series", action="list_all", 
                         url=host + "torrents.php?category=2;18;41;49&search=&order=data&by=DESC", 
                         thumbnail=get_thumb("videolibrary_tvshow.png"), c_type="series", 
                         contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Calidades[/COLOR]", action="section", 
                         url=host + "torrents.php?category=2;18;41;49&search=&order=data&by=DESC", 
                         thumbnail=get_thumb("channels_tvshow_hd.png"), c_type="series", 
                         contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Géneros[/COLOR]", action="section", 
                         url=host + "catalog/tv/", 
                         thumbnail=get_thumb("genres.png"), c_type="series", 
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


def section(item):
    logger.info()

    findS = finds.copy()
    
    if 'Calidades' in item.title:
        findS['categories'] = {'find_all': [{'tag': ['div'], 'class': ['divadvscat']}]}
    
    elif 'Géneros' in item.title:
        findS['categories'] = {'find': [{'tag': ['div'], 'align': ['center']}], 
                               'find_next': [{'tag': ['div'], 'align': ['center']}], 
                               'find_all': [{'tag': ['span'], 'class': ['catalog-genre']}]}
        findS['next_page_rgx'] = [['\d+', '%s']]

    return AlfaChannel.section(item, matches_post=section_matches, finds=findS, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        
        if 'Calidades' in item.title:
            elem_json['url'] = AlfaChannel.urljoin(host, elem.a.get('href') + "&search=&order=data&by=DESC")
            elem_json['title'] = elem.a.get_text(strip=True).strip()

            if item.c_type == 'peliculas' and "Mov" not in elem_json['title']: continue
            if item.c_type == 'series' and "TV" not in elem_json['title']: continue
            elem_json['c_type'] = item.c_type
            elem_json['title'] = elem_json['title'].replace('Movs/', '').replace('Movies/', '')
        
        elif 'Géneros' in item.title:
            elem_json['url'] = AlfaChannel.urljoin(host, elem.a.get('href'))
            elem_json['title'] = elem.a.get_text(strip=True).strip()

        matches.append(elem_json.copy())

    return matches


def list_all(item):
    logger.info()
                       
    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=True, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    patron_thumb = "return\s*overlib\('[^i]*img\s*src='([^']+)'"
    patron_title = '(.*?)(\.[1|2][9|0]\d{2})?\.S\d{2}.*?\.([\d|A-Z]{2}.*?)(?:-.*?)?$'

    for elem_tr in matches_int:
        elem_json = {}
        #logger.error(elem_tr)

        for x, elem in enumerate(elem_tr.find_all('td')):
            #logger.error(elem)

            try:
                if x == 1:
                    elem_json['url'] = elem.a.get("href", "")
                    elem_json['thumbnail'] = scrapertools.find_single_match(elem.a.get("onmouseover", "").replace('\\', ''), patron_thumb)
                    if elem.a.find_next('a') and 'imdb' in elem.a.find_next('a').get("href", ""):
                        elem_json['imdb_id'] = elem.a.find_next('a').get("href", "").split('=')[1]
                    elem_json['title'] = elem.a.get_text(strip=True)

            except:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue

        # Analizamos los formatos de series, temporadas y episodios
        if item.c_type in ['series', 'search']:
            patron_title = '(.*?)(\.[1|2][9|0]\d{2})?\.S\d{2}.*?\.([\d|A-Z]{2}.*?)(?:-.*?)?$'
            if scrapertools.find_single_match(elem_json['title'], patron_title):
                elem_json['mediatype'] = 'tvshow'
                if elem_json.get('imdb_id'): elem_json['url'] = 'tv/%s/' % elem_json['imdb_id']
            else:
                patron_title = '(.*?)\.*([1|2][9|0]\d{2})?(?:\.\d{2}\.\d{2}).*?\.([\d|A-Z]{2}.*?)(?:-.*?)?$'
                if scrapertools.find_single_match(elem_json['title'], patron_title):
                    elem_json['mediatype'] = 'tvshow'
                    if elem_json.get('imdb_id'): elem_json['url'] = 'tv/%s/' % elem_json['imdb_id']
                elif item.c_type in ['series']:
                    logger.error('ERROR tratando título SERIE: ' + elem_json['title'])
                    continue

        # Analizamos los formatos si es película
        title_save = elem_json['title']
        if item.c_type in ['peliculas', 'search'] and not elem_json.get('mediatype'):
            patron_title = '(.*?)\.([1|2][9|0]\d{2})?\.(.*?)(?:-.*?)?$'
            if scrapertools.find_single_match(elem_json['title'], patron_title):
                elem_json['mediatype'] = 'movie'
                if elem_json.get('imdb_id'): elem_json['url'] = 'torrents.php?imdb=%s&order=size&by=ASC' % elem_json['imdb_id']
            else:
                logger.error('ERROR tratando título PELI: ' + elem_json['title'])
                continue

        try:
            elem_json['title'], elem_json['year'], elem_json['quality'] = scrapertools.find_single_match(elem_json['title'], patron_title)
        except:
            logger.error(traceback.format_exc())
            elem_json['title'] = title_save
            elem_json['year'] = ''
            elem_json['quality'] = ''

        elem_json['title'] = elem_json['title'].replace('.', ' ')
        elem_json['quality'] = '*%s' % elem_json.get('quality', '').replace('.', ' ')
        elem_json['language'] = '*%s' % scrapertools.find_single_match(elem_json['quality'], '\*([A-Z]+)\s*')
        elem_json['quality'] = re.sub('\*[A-Z]+\s*', '*', elem_json['quality'])

        # Analizamos el año.  Si no está claro ponemos '-'
        try:
            elem_json['year'] = int(elem_json['year'])
            if elem_json['year'] <= 1940 or elem_json['year'] >= 2050:
                elem_json['year'] = '-'
        except:
            elem_json['year'] = '-'

        if not elem_json.get('url'): continue

        matches.append(elem_json.copy())

    return matches


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item, **kwargs)


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
    kwargs['matches_post_get_video_options'] = findvideos_matches

    return AlfaChannel.episodes(item, data=data, matches_post=episodesxseason_matches, generictools=True, finds=finds, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem_in in matches_int:
        if elem_in.div.get('id', '').startswith('season_') and scrapertools.find_single_match(elem_in.div.get('id', ''), 
                                                                            '\d+') != str(item.contentSeason): continue

        for x, elem in enumerate(elem_in.find_all('div', class_='tvdivhidden')):
            elem_json = {}
            epi_rango = False
            #logger.error(elem)
            
            try:
                elem_json['url'] = 'tv.php?ajax=1&tvepisode=%s' % re.sub('populate_tv\(|\)|;', '', elem.a.get('onclick', ''))
                info = elem.get_text('|', strip=True).split('|')
                elem_json['title'] = info[1].strip()
                
                elem_json['season'] = item.contentSeason
                elem_json['episode'] = int(scrapertools.find_single_match(info[0], '(?i)Epi\w*\s*(\d+)') or 1)

                #Si son episodios múltiples, lo extraemos
                if 'season pack' in elem_json['title'].lower():
                    elem_json['episode'] = 1
                    epi_rango = True
                if epi_rango: elem_json['title'] = 'al 99'

            except:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue

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
    patron_thumb = "return\s*overlib\('[^i]*img\s*src='([^']+)'"
    patron_title = '(.*?)(\.[1|2][9|0]\d{2})?\.S\d{2}.*?\.([\d|A-Z]{2}.*?)(?:-.*?)?$'
    seeds = 0

    for elem_tr in matches_int:
        elem_json = {}
        #logger.error(elem_tr)
        tr_class = elem_tr.get('class', '')

        for x, elem in enumerate(elem_tr.find_all('td')):
            #logger.error(elem)

            try:
                if 'lista2' in tr_class:
                    if x == 1:
                        elem_json['url'] = elem.a.get("href", "")
                        elem_json['thumbnail'] = scrapertools.find_single_match(elem.a.get("onmouseover", "").replace('\\', ''), patron_thumb)
                        elem_json['title'] = elem.a.get_text(strip=True)

                    if x == 3:
                        elem_json['torrent_info'] = elem_json['size'] = elem.get_text(strip=True)

                    if x == 4:
                        try:
                            elem_json['seeds'] = int(elem.get_text(strip=True))
                            seeds += elem_json['seeds']
                        except:
                            elem_json['seeds'] = 0
                        elem_json['torrent_info'] += ', Seeds: %s' % elem_json['seeds']

                else:
                    if x == 4:
                        elem_json['url'] = elem.a.get("href", "")
                        elem_json['title'] = elem.a.get_text(strip=True)

                    if x == 5:
                        try:
                            elem_json['seeds'] = int(elem.get_text(strip=True))
                            seeds += elem_json['seeds']
                        except:
                            elem_json['seeds'] = 0

                    if x == 7:
                        elem_json['torrent_info'] = elem_json['size'] = elem.get_text(strip=True)
                        elem_json['torrent_info'] += ', Seeds: %s' % elem_json['seeds']

            except:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue

        # Analizamos los formatos de series, temporadas y episodios
        if item.contentType in ['tvshow']:
            patron_title = '(.*?)(\.[1|2][9|0]\d{2})?\.S\d{2}.*?\.([\d|A-Z]{2}.*?)(?:-.*?)?$'
            if not scrapertools.find_single_match(elem_json['title'], patron_title):
                patron_title = '(.*?)\.*([1|2][9|0]\d{2})?(?:\.\d{2}\.\d{2}).*?\.([\d|A-Z]{2}.*?)(?:-.*?)?$'
                if not scrapertools.find_single_match(elem_json['title'], patron_title):
                    logger.error('ERROR tratando título SERIE: ' + elem_json['title'])

        # Analizamos los formatos si es película
        if item.contentType in ['movie']:
            patron_title = '(.*?)\.([1|2][9|0]\d{2})?\.(.*?)(?:-.*?)?$'
            if not scrapertools.find_single_match(elem_json['title'], patron_title):
                logger.error('ERROR tratando título PELI: ' + elem_json['title'])

        try:
            elem_json['title'], year, elem_json['quality'] = scrapertools.find_single_match(elem_json['title'], patron_title)
        except:
            logger.error(traceback.format_exc())
            elem_json['title'] = item.contentTitle
            elem_json['quality'] = ''

        elem_json['title'] = elem_json['title'].replace('.', ' ')
        elem_json['quality'] = '*%s' % elem_json.get('quality', '').replace('.', ' ')
        elem_json['language'] = '*%s' % scrapertools.find_single_match(elem_json['quality'], '\*([A-Z]+)\s*')
        elem_json['quality'] = re.sub('\*[A-Z]+\s*', '*', elem_json['quality'])
        
        elem_json['server'] = 'torrent'

        matches.append(elem_json.copy())

    if seeds > 0:
        matches = sorted(matches, key=lambda match: int(-match.get('seeds', 0)))
        for x, match in enumerate(matches.copy()):
            if not match.get('seeds'):
                del matches[x]

    return matches, langs


def play(item):                                                                 # Permite preparar la descarga de los .torrents y subtítulos externos
    logger.info()

    itemlist = []
    headers = []

    soup = AlfaChannel.create_soup(item.url, **kwargs)
    itemlist = AlfaChannel.itemlist
    AlfaChannel.itemlist = []
    if itemlist:                                                                # Bloqueo de IP
        return []
    
    matches = soup.find('td', class_="header2", string=re.compile('Torrent:')).find_next('td', class_="lista").find_all('a')
    item.url = ''

    for elem in matches:
        #logger.error(elem)

        if elem.get('href', ''):
            if '.torrent' in elem.get('href', '') and not '.torrent' in item.url:
                item.url = AlfaChannel.urljoin(host, elem.get('href', ''))
            elif 'magnet' in elem.get('href', '') and not 'magnet' in item.torrent_alt:
                item.torrent_alt = elem.get('href', '')

    return [item]

    try:
        matches = soup.find('div', id='files').find_all('td', class_='lista')
        logger.error(matches)
        for elem in matches:
            logger.error(elem)

            if elem.get_text(strip=True) and '.srt' in elem.get_text(strip=True):
                item.subtitle += elem.get_text(strip=True).split('/')[-1]
                logger.error(item.subtitle)
                break
    except:
        logger.error(matches)
        logger.error(traceback.format_exc())

    from core import downloadtools
    from core import ziptools
    from core import filetools
    import time

    #buscamos subtítulos en español
    patron = '<tr><td align="(?:[^"]+)?"\s*class="(?:[^"]+)?"\s*>\s*Subs.*?<\/td><td class="(?:[^"]+)?"\s*>(.*?)(?:<br\/>)?<\/td><\/tr>'
    data_subt = scrapertools.find_single_match(AlfaChannel.response.data, patron)
    if data_subt:
        patron = '<a href="([^"]+)"\s*onmouseover="return overlib\('
        patron += "'Download Spanish subtitles'"
        patron += '\)"\s*onmouseout="(?:[^"]+)?"\s*><img src="(?:[^"]+)?"\s*><\/a>'
        subt = scrapertools.find_single_match(data_subt, patron)
        if subt:
            item.subtitle = urlparse.urljoin(host, subt)
    
    if item.subtitle:                                                   #Si hay urls de sub-títulos, se descargan
        from core import httptools
        headers.append(["User-Agent", httptools.get_user_agent()])      #Se busca el User-Agent por defecto
        videolibrary_path = config.get_videolibrary_path()              #Calculamos el path absoluto a partir de la Videoteca
        if videolibrary_path.lower().startswith("smb://"):              #Si es una conexión SMB, usamos userdata local
            videolibrary_path = config.get_data_path()                  #Calculamos el path absoluto a partir de Userdata
        videolibrary_path = filetools.join(videolibrary_path, "subtitles")
        #Primero se borra la carpeta de subtitulos para limpiar y luego se crea
        if filetools.exists(videolibrary_path):   
            filetools.rmdirtree(videolibrary_path)
            time.sleep(1)
        if not filetools.exists(videolibrary_path):   
            filetools.mkdir(videolibrary_path)
        subtitle_name = 'Rarbg-ES_SUBT.zip'                                     #Nombre del archivo de sub-títulos
        subtitle_folder_path = filetools.join(videolibrary_path, subtitle_name)   #Path de descarga
        ret = downloadtools.downloadfile(item.subtitle, subtitle_folder_path, headers=headers, continuar=True, silent=True)

        if filetools.exists(subtitle_folder_path):
            # Descomprimir zip dentro del addon
            # ---------------------------------
            try:
                unzipper = ziptools.ziptools()
                unzipper.extract(subtitle_folder_path, videolibrary_path)
            except:
                import xbmc
                xbmc.executebuiltin('Extract("%s", "%s")' % (subtitle_folder_path, videolibrary_path))
                time.sleep(1)
            
            # Borrar el zip descargado
            # ------------------------
            filetools.remove(subtitle_folder_path)
            
            #Tomo el primer archivo de subtítulos como valor por defecto
            for raiz, subcarpetas, ficheros in filetools.walk(videolibrary_path):
                for f in ficheros:
                    if f.endswith(".srt"):
                        #f_es = 'rarbg_subtitle.spa.srt'
                        f_es = scrapertools.find_single_match(item.url, '&f=(.*?).torrent$').replace('.', ' ').replace('-', ' ').lower() + '.spa.srt'
                        if not f_es:
                            f_es = item.infoLabels['originaltitle'] + '.spa.srt'
                            f_es = f_es.replace(':', '').lower()
                        filetools.rename(filetools.join(videolibrary_path, f), filetools.join(videolibrary_path, f_es))
                        item.subtitle = filetools.join(videolibrary_path, f_es)   #Archivo de subtitulos
                        break
                break
        
    itemlist.append(item.clone())                                               #Reproducción normal
        
    return itemlist

    
def episodios_OLD(item):
    logger.info()
    itemlist = []
    item.category = categoria
    
    #logger.debug(item)

    if item.from_title:
        item.title = item.from_title
    
    #Limpiamos num. Temporada y Episodio que ha podido quedar por Novedades
    season_display = 0
    if item.contentSeason:
        if item.season_colapse:                                                             #Si viene del menú de Temporadas...
            season_display = item.contentSeason                                             #... salvamos el num de sesión a pintar
            item.from_num_season_colapse = season_display
            del item.season_colapse
            item.contentType = "tvshow"
            if item.from_title_season_colapse:
                item.title = item.from_title_season_colapse
                del item.from_title_season_colapse
                if item.infoLabels['title']:
                    del item.infoLabels['title']
        del item.infoLabels['season']
    if item.contentEpisodeNumber:
        del item.infoLabels['episode']
    if season_display == 0 and item.from_num_season_colapse:
        season_display = item.from_num_season_colapse

    # Obtener la información actualizada de la Serie.  TMDB es imprescindible para Videoteca
    try:
        tmdb.set_infoLabels(item, True, idioma_busqueda='es,en')
    except:
        pass
        
    modo_ultima_temp_alt = modo_ultima_temp
    if item.ow_force == "1":                                    #Si hay un traspaso de canal o url, se actualiza todo 
        modo_ultima_temp_alt = False
    
    max_temp = 1
    if item.infoLabels['number_of_seasons']:
        max_temp = item.infoLabels['number_of_seasons']
    y = []
    if modo_ultima_temp_alt and item.library_playcounts:        #Averiguar cuantas temporadas hay en Videoteca
        patron = 'season (\d+)'
        matches = re.compile(patron, re.DOTALL).findall(str(item.library_playcounts))
        for x in matches:
            y += [int(x)]
        max_temp = max(y)

    # Descarga la página
    patron_temp = '<h1\s*class="[^"]+">Season\s*(\d+)<\/h1><div class="tvcontent">'
    patron_temp += '<div id="[^"]+"><\/div>(.*?<\/div><\/div>)(?:<script>.*?<\/script>)?<\/div>'
    data = ''                                                                   #Inserto en num de página en la url
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               patron=patron_temp, item=item, itemlist=[], 
                                                               quote_rep=False, check_blocked_IP=True)
    data = re.sub(r"&nbsp;", "", data)
    if not data or response.code in [999, 99]:                                  # Si ERROR o lista de errores lo reintentamos con otro Host
        return itemlist                                                         # ... Salimos

    #Capturamos las temporadas de episodios dentro de la serie
    
    temp_serie = re.compile(patron_temp, re.DOTALL).findall(data)
    
    for season_num, temporada in temp_serie:
        
        patron = '<div id="episode_(\d+)"><div class="[^"]+">\s*<a onclick="[^"]+"'
        patron += '\s*class="[^"]+"><div class="[^"]+">.*?\s*(\d+)<\/div>\s*(.*?)\s*<'
        matches = re.compile(patron, re.DOTALL).findall(temporada)
        if not matches:                                                             #error
            logger.error("ERROR 02: EPISODIOS: Ha cambiado la estructura de la Web " + " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 02: EPISODIOS: Ha cambiado la estructura de la Web.  Reportar el error con el log'))
            return itemlist                         #si no hay más datos, algo no funciona, pintamos lo que tenemos

        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)
        
        season = max_temp
        #Comprobamos si realmente sabemos el num. máximo de temporadas
        if item.library_playcounts or (item.infoLabels['number_of_seasons'] and item.tmdb_stat):
            num_temporadas_flag = True
        else:
            num_temporadas_flag = False

        if modo_ultima_temp_alt and item.library_playcounts:    #Si solo se actualiza la última temporada de Videoteca
            if int(season_num) < max_temp:
                break                                           #Sale del bucle actual del FOR
        
        # Recorremos todos los episodios generando un Item local por cada uno en Itemlist
        for epi_id, episode_num, scrapedtitle in matches:
            item_local = item.clone()
            item_local.action = "findvideos"
            item_local.contentType = "episode"
            item_local.extra = "episodios"
            if item_local.library_playcounts:
                del item_local.library_playcounts
            if item_local.library_urls:
                del item_local.library_urls
            if item_local.path:
                del item_local.path
            if item_local.update_last:
                del item_local.update_last
            if item_local.update_next:
                del item_local.update_next
            if item_local.channel_host:
                del item_local.channel_host
            if item_local.active:
                del item_local.active
            if item_local.contentTitle:
                del item_local.infoLabels['title']
            if item_local.season_colapse:
                del item_local.season_colapse

            item_local.title = ''
            item_local.context = "['buscar_trailer']"
            item_local.url = urlparse.urljoin(host, 'tv.php?ajax=1&tvepisode=%s' % epi_id)
            title = scrapedtitle
            item_local.language = ['VO']
            if not item_local.infoLabels['poster_path']:
                item_local.thumbnail = item_local.infoLabels['thumbnail']
            epi_rango = False

            try:
                item_local.contentSeason = int(season_num)
                if 'season pack' in title.lower():
                    item_local.contentEpisodeNumber = 1
                    epi_rango = True
                else:
                    item_local.contentEpisodeNumber = int(episode_num)
            except:
                logger.error('ERROR al extraer Temporada/Episodio: ' + title)
                item_local.contentSeason = 1
                item_local.contentEpisodeNumber = 0
            
            #Si son episodios múltiples, lo extraemos
            if epi_rango:
                item_local.infoLabels['episodio_titulo'] = 'al 99'
                item_local.title = '%sx%s al 99 - Season Pack' % (str(item_local.contentSeason), str(item_local.contentEpisodeNumber).zfill(2))
            else:
                item_local.title = '%sx%s - ' % (str(item_local.contentSeason), str(item_local.contentEpisodeNumber).zfill(2))

            if season_display > 0:
                if item_local.contentSeason > season_display:
                    continue
                elif item_local.contentSeason < season_display:
                    break
            
            itemlist.append(item_local.clone())

            #logger.debug(item_local)
            
    if len(itemlist) > 1:
        itemlist = sorted(itemlist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))       #clasificamos
        
    if item.season_colapse and not item.add_videolibrary:                       #Si viene de listado, mostramos solo Temporadas
        item, itemlist = generictools.post_tmdb_seasons(item, itemlist)

    if not item.season_colapse:                                                 #Si no es pantalla de Temporadas, pintamos todo
        # Pasada por TMDB y clasificación de lista por temporada y episodio
        tmdb.set_infoLabels(itemlist, True, idioma_busqueda='es,en')

        #Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
        item, itemlist = generictools.post_tmdb_episodios(item, itemlist)
    
    #logger.debug(item)

    return itemlist
    
    
def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    global kwargs
    kwargs = AHkwargs

    texto = texto.replace(" ", "+")
    
    try:
        if texto:
            item.url = host + 'torrents.php?category=2;18;41;49;14;48;17;44;45;47;50;51;52;42;46&search=%s' % texto
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

 