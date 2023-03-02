# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

import re
import time
import traceback
import base64

from channelselector import get_thumb
from core import scrapertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from lib import generictools
from channels import filtertools
from channels import autoplay
from lib.AlfaChannelHelper import DictionaryAllChannel


IDIOMAS = {'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['torrent']

canonical = {
             'channel': 'torrentpelis', 
             'host': config.get_setting("current_host", 'torrentpelis', default=''), 
             'host_alt': ['https://torrentpelis.org/'], 
             'host_black_list': ['https://www2.torrentpelis.com/', 'https://www1.torrentpelis.com/', 'https://torrentpelis.com/'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant_if_proxy': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'
domain = scrapertools.find_single_match(host, patron_domain)
host_torrent = host[:-1]

__modo_grafico__ = config.get_setting('modo_grafico', channel)                  # TMDB?
IDIOMAS_TMDB = {0: 'es', 1: 'en', 2: 'es,en'}
idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', channel)]    # Idioma base para TMDB
idioma_busqueda_VO = IDIOMAS_TMDB[2]                                                # Idioma para VO
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel) #Actualización sólo últ. Temporada?
timeout = config.get_setting('timeout_downloadpage', channel) * 2
season_colapse = config.get_setting('season_colapse', channel)                  # Season colapse?
filter_languages = config.get_setting('filter_languages', channel)              # Filtrado de idiomas?

finds = {'find': {'find': [{'tag': ['div'], 'id': ['archive-content']}], 
                  'find_all': [{'tag': ['article'], 'class': ['item']}]}, 
         'categories': {'find': [{'tag': ['div'], 'class': ['items normal']}], 
                        'find_all': [{'tag': ['article'], 'class': ['item']}]}, 
         'search': {'find_all': [{'tag': ['div'], 'class': ['result-item']}]}, 
         'next_page': [], 
         'last_page': {'find': [{'tag': ['div'], 'class': ['pagination']}, {'tag': ['span']}], 
                       'get_text': [{'@TEXT': '..gina \d+ de (\d+)'}]}, 
         'season_episode': [], 
         'season': [], 
         'episode_url': '', 
         'episodes': [], 
         'episode_num': [], 
         'episode_clean': [], 
         'findvideos': {'find': [{'tag': ['tbody']}], 'find_all': [{'tag': ['tr']}]}, 
         'title_clean': [],
         'quality_clean': [],
         'language_clean': []}
AlfaChannel = DictionaryAllChannel(host, movie_path="/peliculas", canonical=canonical, finds=finds, 
                                   list_language=list_language, list_servers=list_servers)


def mainlist(item):
    logger.info()
    itemlist = []
    
    thumb_pelis = get_thumb("channels_movie.png")

    thumb_genero = get_thumb("genres.png")
    thumb_calidad = get_thumb("top_rated.png")
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all", c_type='peliculas', 
                url=host + 'peliculas/page/1/', thumbnail=thumb_pelis, extra="peliculas", extra2="PELICULA"))
    itemlist.append(Item(channel=item.channel, title="    - por Género", action="genero", c_type='peliculas', 
                url=host, thumbnail=thumb_genero, extra="peliculas", extra2="GENERO"))
    #itemlist.append(Item(channel=item.channel, title="    - por Netflix", action="submenu", c_type='peliculas', 
    #            url=host, thumbnail=thumb_pelis, extra="peliculas", extra2="NETFLIX"))
    itemlist.append(Item(channel=item.channel, title="    - por Tendencias", action="submenu", c_type='peliculas', 
                url=host, thumbnail=thumb_calidad, extra="peliculas", extra2="TENDENCIAS"))
    
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search",
                url=host, thumbnail=thumb_buscar, extra="search"))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                folder=False, thumbnail=thumb_separador))
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                thumbnail=thumb_settings))
    
    autoplay.show_option(item.channel, itemlist)                                #Activamos Autoplay

    return itemlist
    
    
def configuracion(item):
    from platformcode import platformtools
    
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    
    return


def submenu(item):

    patron = '<li\s*id="menu-item-[^"]+"\s*class="menu-item[^"]+">\s*<a\s*href="([^"]+)">'
    patron += '\s*<icona\s*class="fa[^"]+">\s*<\/icona>\s*(\w+)\s*(?:<\/a>\s*)?<\/a>.*?<\/li>'

    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               s2=False, patron=patron, item=item, itemlist=[])     # Descargamos la página

    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if not response.sucess or itemlist:                                         # Si ERROR o lista de errores ..
        return itemlist                                                         # ... Salimos

    matches = re.compile(patron, re.DOTALL).findall(data)

    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)

    if not matches:
        logger.error("ERROR 02: SUBMENU: Ha cambiado la estructura de la Web " + 
                        " / PATRON: " + patron + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: SUBMENU: Ha cambiado la estructura de la Web.  '
                        + 'Reportar el error con el log'))
        return itemlist                                         #si no hay más datos, algo no funciona, pintamos lo que tenemos
        
    for scrapedurl, scrapedtitle in matches:
        if scrapedtitle in item.extra2:
            item.url = scrapedurl
            if not item.url.endswith('/'): item.url += '/'
            item.url += 'page/1/'
            return list_all(item)
            
    return itemlist

    
def genero(item):
    logger.info()
    itemlist = []

    patron = '<li\s*id="menu-item-[^"]+"\s*class="menu-item[^"]+genres[^"]+">\s*'
    patron += '<a\s*href="([^"]+)">\s*([^<]+)<\/a>\s*<\/li>'

    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               s2=False, patron=patron, item=item, itemlist=[])     # Descargamos la página

    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if not response.sucess or itemlist:                                         # Si ERROR o lista de errores ...
        return itemlist                                                         # ... Salimos

    matches = re.compile(patron, re.DOTALL).findall(data)

    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)

    if not matches:
        logger.error("ERROR 02: SUBMENU: Ha cambiado la estructura de la Web " + 
                        " / PATRON: " + patron + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: SUBMENU: Ha cambiado la estructura de la Web.  '
                        + 'Reportar el error con el log'))
        return itemlist                                         #si no hay más datos, algo no funciona, pintamos lo que tenemos

    for scrapedurl, gen in matches:
        itemlist.append(item.clone(action="list_all", title=gen.capitalize(), url=scrapedurl + 'page/1/'))
        
    if len(itemlist) > 1:
        itemlist = sorted(itemlist, key=lambda it: it.title)                    #clasificamos

    return itemlist


def list_all(item):                                                             # Listado principal y de búsquedas
    logger.info()
    
    finds['controls'] = {
                         'timeout': timeout
                        }
    finds['title_clean'] = [
                            ['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie', ''],
                            ['[\(|\[]\s*[\)|\]]', '']
                           ]
    finds['quality_clean'] = [
                              ['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']
                             ]

    if item.extra2 in ["GENERO", "TENDENCIAS"]: 
        finds['find'] = finds.get('categories', {})
    elif item.extra == "search":
        finds['find'] = finds.get('search', {})
                       
    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=True, finds=finds)
                        

def list_all_matches(item, matches_int):                                        # Listado principal: procesado de matches
    logger.info()
    
    matches = []

    for elem in matches_int:
        elem_json = {}
        
        elem_json['url'] = elem.a.get('href', '')
        elem_json['title'] = elem.img.get('alt', '')
        elem_json['thumbnail'] = elem.img.get('src', '')
        if item.extra == "search":
            elem_json['year'] = elem.find('span', class_="year").text
        else:
            elem_json['year'] = elem.find('div', class_='data').find('span').text
        elem_json['year'] = scrapertools.find_single_match(elem_json['year'], '\d{4}')
        
        matches.append(elem_json.copy())
    
    return matches


def findvideos(item):
    logger.info()
    
    itemlist = []
    itemlist_t = []                                                             #Itemlist total de enlaces
    itemlist_f = []                                                             #Itemlist de enlaces filtrados
    matches = []
    data = ''
    response = {
                'data': data, 
                'sucess': False, 
                'code': 0
               }
    response = type('HTTPResponse', (), response)
    
    torrent_params = {
                      'url': item.url,
                      'torrents_path': None, 
                      'local_torr': item.torrents_path, 
                      'lookup': False, 
                      'force': True, 
                      'data_torrent': True, 
                      'subtitles': True, 
                      'file_list': True
                      }
    
    #logger.debug(item)
    
    item.matches = []
    soup = AlfaChannel.create_soup(item.url)
    matches = AlfaChannel.parse_finds_dict(soup, finds['findvideos'])
    for elem in matches:
        for x, td in enumerate(elem.find_all('td')):
            if x == 0: scrapedurl = td.a['href']
            if x == 1: scrapedquality = td.get_text()
            if x == 2: scrapedlanguage = td.img['src']
            if x == 3: scrapedsize = td.get_text()
        item.matches.append((scrapedurl, scrapedquality, scrapedlanguage, scrapedsize))

    #Bajamos los datos de la página
    #patron = '<div\s*id="torrent".*?class="quality">\s*([^<]*)<\/strong>\s*<\/td>'
    #patron += '\s*<td>\s*([^<]*)<\/td>\s*<td>\s*([^<]*)<\/td>.*?<a\s*href="([^"]+)"'
    patron = '(?i)<a\s*href="([^"]+)"\s*target="_blank">descargar\s*torrent<\/a>' \
             '\s*<\/td>\s*<td>\s*<strong\s*class="quality">([^<]*)<\/strong>\s*<\/td>' \
             '\s*<td>([^<]*)<\/td>\s*<td>([^<]*)<\/td>'
    
    if not item.matches:
        data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                                   s2=False, patron=patron, item=item, itemlist=itemlist)   # Descargamos la página

    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if (not data and not item.matches) or response.code == 999:
        if item.emergency_urls and not item.videolibray_emergency_urls:         #Hay urls de emergencia?
            if len(item.emergency_urls) > 1:
                matches = item.emergency_urls[1]                                #Restauramos matches de vídeos
            elif len(item.emergency_urls) == 1 and item.emergency_urls[0]:
                matches = item.emergency_urls[0]                                #Restauramos matches de vídeos - OLD FORMAT
            item.armagedon = True                                               #Marcamos la situación como catastrófica 
        else:
            if item.videolibray_emergency_urls:                                 #Si es llamado desde creación de Videoteca...
                return item                                                     #Devolvemos el Item de la llamada
            else:
                return itemlist                                                 #si no hay más datos, algo no funciona, pintamos lo que tenemos

    if not item.armagedon:
        if not item.matches:
            matches = re.compile(patron, re.DOTALL).findall(data)
        else:
            matches = item.matches
    
    #logger.debug("PATRON: " + patron)
    #logger.debug(matches)
    #logger.debug(data)
    
    if not matches:                                                             #error
        return itemlist

    #Si es un lookup para cargar las urls de emergencia en la Videoteca...
    if item.videolibray_emergency_urls:
        item.emergency_urls = []                                                #Iniciamos emergency_urls
        item.emergency_urls.append([])                                          #Reservamos el espacio para los .torrents locales
        matches_list = []                                                       # Convertimos matches-tuple a matches-list
        for tupla in matches:
            if isinstance(tupla, tuple):
                matches_list.append(list(tupla))
        if matches_list:
            item.emergency_urls.append(matches_list)                            # Salvamnos matches de los vídeos...  
        else:
            item.emergency_urls.append(matches)

    #Llamamos al método para crear el título general del vídeo, con toda la información obtenida de TMDB
    if not item.videolibray_emergency_urls:
        item, itemlist = generictools.post_tmdb_findvideos(item, itemlist)

    #Ahora tratamos los enlaces .torrent con las diferentes calidades
    for x, (scrapedurl, scrapedquality, scrapedlanguage, scrapedsize) in enumerate(matches):
        scrapedpassword = ''

        #Generamos una copia de Item para trabajar sobre ella
        item_local = item.clone()

        item_local.url = generictools.convert_url_base64(scrapedurl, host_torrent)
        if item.videolibray_emergency_urls and item_local.url != scrapedurl:
            item.emergency_urls[1][x][0] = item_local.url
        
        # Buscamos el enlace definitivo, si es necesario
        if not item_local.url.startswith('magnet'):
            patron = '<a\s*id="link"[^>]*href="([^"]+)"'
            data, response, item, itemlist = generictools.downloadpage(item_local.url, timeout=timeout, canonical=canonical, 
                                                                       s2=False, follow_redirects=False, item=item, itemlist=itemlist)
            if response.headers.get('location', '') and response.headers['location'].startswith('magnet'):
                item_local.url = response.headers['location']
            else:
                item_local.url = scrapertools.find_single_match(data, patron)
            if not item_local.url: continue
        
        # Restauramos urls de emergencia si es necesario
        local_torr = ''
        if item.emergency_urls and not item.videolibray_emergency_urls:
            try:                                                                # Guardamos la url ALTERNATIVA
                if item.emergency_urls[0][0].startswith('http') or item.emergency_urls[0][0].startswith('//'):
                    item_local.torrent_alt = generictools.convert_url_base64(item.emergency_urls[0][0], host_torrent)
                else:
                    item_local.torrent_alt = generictools.convert_url_base64(item.emergency_urls[0][0])
            except:
                item_local.torrent_alt = ''
                item.emergency_urls[0] = []
            from core import filetools
            if item.contentType == 'movie':
                FOLDER = config.get_setting("folder_movies")
            else:
                FOLDER = config.get_setting("folder_tvshows")
            if item.armagedon and item_local.torrent_alt:
                item_local.url = item_local.torrent_alt                         # Restauramos la url
                if not item.torrent_alt.startswith('http'):
                    local_torr = filetools.join(config.get_videolibrary_path(), FOLDER, item_local.url)
            if len(item.emergency_urls[0]) > 1:
                del item.emergency_urls[0][0]
        
        # Procesamos idiomas
        item_local.language = []                                                #creamos lista para los idiomas
        item_local.quality = scrapedquality                                     # Copiamos la calidad
        if '[Subs. integrados]' in scrapedlanguage or '(Sub Forzados)' in scrapedlanguage \
                    or 'Subs integrados' in scrapedlanguage:
            item_local.language = ['VOS']                                       # añadimos VOS
        if 'castellano' in scrapedlanguage.lower() or ('espa' in scrapedlanguage.lower() and not 'latino' in scrapedlanguage.lower()):
            item_local.language += ['CAST']                                     # añadimos CAST
        if 'dual' in item_local.quality.lower():
            item_local.quality = re.sub(r'(?i)dual.*?', '', item_local.quality).strip()
            item_local.language += ['DUAL']                                     # añadimos DUAL
        if not item_local.language:
            item_local.language = ['LAT']                                       # [LAT] por defecto
        
        #Buscamos tamaño en el archivo .torrent
        size = ''
        if item_local.torrent_info:
            size = item_local.torrent_info
        elif scrapedsize:
            size = scrapedsize
            if '--' in size:
                size = ''
        if not size and not item.videolibray_emergency_urls and not item_local.url.startswith('magnet:'):
            if not item.armagedon:
                torrent_params['url'] = item_local.url
                torrent_params['local_torr'] = local_torr
                torrent_params = generictools.get_torrent_size(item_local.url, torrent_params=torrent_params, item=item_local) # Tamaño en el .torrent
                size = torrent_params['size']
                if torrent_params['torrents_path']: item_local.torrents_path = torrent_params['torrents_path']
                
                if 'ERROR' in size and item.emergency_urls and not item.videolibray_emergency_urls:
                    item_local.armagedon = True
                    try:                                                        # Restauramos la url
                        if item.emergency_urls[0][0].startswith('http') or item.emergency_urls[0][0].startswith('//'):
                            item_local.url = generictools.convert_url_base64(item.emergency_urls[0][0], host_torrent)
                        else:
                            item_local.url = generictools.convert_url_base64(item.emergency_urls[0][0])
                            if not item.url.startswith('http'):
                                local_torr = filetools.join(config.get_videolibrary_path(), FOLDER, item_local.url)
                    except:
                        item_local.torrent_alt = ''
                        item.emergency_urls[0] = []
                    torrent_params['url'] = item_local.url
                    torrent_params['local_torr'] = local_torr
                    torrent_params = generictools.get_torrent_size(item_local.url, torrent_params=torrent_params, item=item_local)
                    size = torrent_params['size']
                    if torrent_params['torrents_path']: item_local.torrents_path = torrent_params['torrents_path']
        if size:
            size = size.replace('GB', 'G·B').replace('Gb', 'G·b').replace('MB', 'M·B')\
                        .replace('Mb', 'M·b').replace('.', ',')
            item_local.torrent_info = '%s, ' % size                             #Agregamos size
        if item_local.url.startswith('magnet:') and not 'Magnet' in item_local.torrent_info:
            item_local.torrent_info += ' Magnet'
        if item_local.torrent_info:
            item_local.torrent_info = item_local.torrent_info.strip().strip(',')
            if item.videolibray_emergency_urls:
                item.torrent_info = item_local.torrent_info
            if not item.unify:
                item_local.torrent_info = '[%s]' % item_local.torrent_info
   
        # Guadamos la password del RAR
        password = scrapedpassword
        # Si tiene contraseña, la guardamos y la pintamos
        if password or item.password:
            if not item.password: item.password = password
            item_local.password = item.password
            itemlist.append(item.clone(action="", title="[COLOR magenta][B] Contraseña: [/B][/COLOR]'" 
                        + item_local.password + "'", folder=False))
        
        # Guardamos urls de emergencia si se viene desde un Lookup de creación de Videoteca
        if item.videolibray_emergency_urls:
            item.emergency_urls[0].append(item_local.url)                       #guardamos la url y nos vamos
            continue

        if item_local.armagedon:
            item_local.quality = '[COLOR hotpink][E][/COLOR] [COLOR limegreen]%s[/COLOR]' % item_local.quality
        
        #Ahora pintamos el link del Torrent
        item_local.title = '[[COLOR yellow]?[/COLOR]] [COLOR yellow][Torrent][/COLOR] ' \
                        + '[COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR] %s' % \
                        (item_local.quality, str(item_local.language), \
                        item_local.torrent_info)
        
        #Preparamos título y calidad, quitando etiquetas vacías
        item_local.title = re.sub(r'\s?\[COLOR \w+\]\[\[?\s?\]?\]\[\/COLOR\]', '', item_local.title)    
        item_local.title = re.sub(r'\s?\[COLOR \w+\]\s?\[\/COLOR\]', '', item_local.title)
        item_local.title = item_local.title.replace("--", "").replace("[]", "")\
                        .replace("()", "").replace("(/)", "").replace("[/]", "")\
                        .replace("|", "").strip()
        item_local.quality = re.sub(r'\s?\[COLOR \w+\]\[\[?\s?\]?\]\[\/COLOR\]', '', item_local.quality)
        item_local.quality = re.sub(r'\s?\[COLOR \w+\]\s?\[\/COLOR\]', '', item_local.quality)
        item_local.quality = item_local.quality.replace("--", "").replace("[]", "")\
                        .replace("()", "").replace("(/)", "").replace("[/]", "")\
                        .replace("|", "").strip()
        
        if not item_local.torrent_info or 'Magnet' in item_local.torrent_info:
            item_local.alive = "??"                                             #Calidad del link sin verificar
        elif 'ERROR' in item_local.torrent_info and 'Pincha' in item_local.torrent_info:
            item_local.alive = "ok"                                             #link en error, CF challenge, Chrome disponible
        elif 'ERROR' in item_local.torrent_info and 'Introduce' in item_local.torrent_info:
            item_local.alive = "??"                                             #link en error, CF challenge, ruta de descarga no disponible
            item_local.channel = 'setting'
            item_local.action = 'setting_torrent'
            item_local.unify = False
            item_local.folder = False
            item_local.item_org = item.tourl()
        elif 'ERROR' in item_local.torrent_info:
            item_local.alive = "no"                                             #Calidad del link en error, CF challenge?
        else:
            item_local.alive = "ok"                                             #Calidad del link verificada
        if item_local.channel != 'setting':
            item_local.action = "play"                                          #Visualizar vídeo
            item_local.server = "torrent"                                       #Seridor Torrent
        
        itemlist_t.append(item_local.clone())                                   #Pintar pantalla, si no se filtran idiomas
        
        # Requerido para FilterTools
        if config.get_setting('filter_languages', channel) > 0:                 #Si hay idioma seleccionado, se filtra
            itemlist_f = filtertools.get_link(itemlist_f, item_local, list_language)  #Pintar pantalla, si no está vacío

        #logger.debug("TORRENT: " + scrapedurl + " / title gen/torr: " + item.title + " / " + item_local.title + " / calidad: " + item_local.quality + " / content: " + item_local.contentTitle + " / " + item_local.contentSerieName)
        #logger.debug(item_local)

    #Si es un lookup para cargar las urls de emergencia en la Videoteca...
    if item.videolibray_emergency_urls:
        return item                                                             #... nos vamos
    
    if len(itemlist_f) > 0:                                                     #Si hay entradas filtradas...
        itemlist.extend(itemlist_f)                                             #Pintamos pantalla filtrada
    else:                                                                       
        if config.get_setting('filter_languages', channel) > 0 and len(itemlist_t) > 0: #Si no hay entradas filtradas ...
            thumb_separador = get_thumb("next.png")                             #... pintamos todo con aviso
            itemlist.append(Item(channel=item.channel, url=host, 
                        title="[COLOR red][B]NO hay elementos con el idioma seleccionado[/B][/COLOR]", 
                        thumbnail=thumb_separador, folder=False))
        
        if len(itemlist_t) == 0:
            if len(itemlist) == 0 or (len(itemlist) > 0 and itemlist[-1].server != 'torrent'):
                return []
        itemlist.extend(itemlist_t)                                             #Pintar pantalla con todo si no hay filtrado
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)                                              #Lanzamos Autoplay
    
    return itemlist


def actualizar_titulos(item):
    logger.info()
    
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels
    item = generictools.update_title(item)
    
    #Volvemos a la siguiente acción en el canal
    return item


def search(item, texto):
    logger.info()
    
    texto = texto.replace(" ", "+")
    
    try:
        item.url = host + 'page/1/?s=' + texto
        item.extra = 'search'

        if texto:
            return list_all(item)
        else:
            return []
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc(1))
        return []
 
 
def newest(categoria):
    logger.info()
    
    itemlist = []
    item = Item()

    item.title = "newest"
    item.category_new = "newest"
    item.channel = channel
    
    try:
        if categoria in ['peliculas', 'latino', 'torrent']:
            item.url = host + "peliculas/page/1/"
            item.extra = "peliculas"
            item.extra2 = "novedades"
            item.action = "list_all"
            itemlist.extend(list_all(item))
                
        if len(itemlist) > 0 and (">> Página siguiente" in itemlist[-1].title or "Pagina siguiente >>" in itemlist[-1].title):
            itemlist[-1].pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc(1))
        return []

    return itemlist
