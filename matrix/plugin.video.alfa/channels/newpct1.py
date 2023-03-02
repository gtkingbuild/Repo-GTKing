# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

from builtins import range
from past.utils import old_div

import re
import datetime
import time
import ast
import random
import traceback

from channelselector import get_thumb
from core import scrapertools
from core import servertools
from core import channeltools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from lib import generictools
from channels import filtertools
from channels import autoplay


IDIOMAS = {'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['torrent']

channel_py = 'newpct1'
item = Item()
item.channel = channel_py
categoria = channel_py.capitalize()
clone_list_random = []                                                          #Iniciamos la lista aleatoria de clones
host = ''
decode_code = ''
#page_url = 'pg/1'
page_url = ''

#category = 'pctmix1'                                                            # Clone preferido para Novedades
category = ''                                                                   # Clone preferido para Novedades
clone_num = 1                                                                   # Número de Clones "buenos"
clone_num_ext = 1                                                               # Número de Clones "válidos"
clone_num_post = 1                                                              # Número de Clones "válidos" sin proxy-post
channel_clone_post = ''

#Código para permitir usar un único canal para todas las webs clones de NewPct1
#Cargamos en .json del canal para ver las listas de valores en settings
channel_json = channeltools.get_channel_json(channel_py)

for settings in channel_json['settings']:                                       #Se recorren todos los settings
    if settings['id'] == "clonenewpct1_channels_list":                          #Encontramos el setting
        clone_list = settings['default']                                        #Carga lista de clones
        break
clone_list = ast.literal_eval(clone_list)                                       #la convierte en array
clone_list_check = clone_list[:]                                                #la salvamos para otros usos
host_index = config.get_setting('clonenewpct1_channel_default', channel_py, 0)  #Clone por defecto
if host_index > clone_num_ext:  config.set_setting('clonenewpct1_channel_default', 0, channel_py)   # Si el clone seleccionado no existe, se pone "Aleatorio"
host_index_check = host_index                                                   #lo salvamos para otros usos

if host_index == 0:                                                             #Si el clones es "Aleatorio"...
    i = 0
    j = clone_num - 1                                                           #... marcamos el último de los clones "buenos"
    for active_clone, channel_clone, host_clone, contentType_clone, info_clone in clone_list:
        if i <= j and active_clone == "1":
            clone_list_random += [clone_list[i]]                                #... añadimos el clone activo "bueno" a la lista
        if i == clone_num_post:
            channel_clone_post = channel_clone                                  #Nombre del Canal elegido para POST
        i += 1
    if clone_list_random:                                                       #Si hay clones en la lista aleatoria...
        clone_list = [random.choice(clone_list_random)]                         #Seleccionamos un clone aleatorio
        #logger.debug(clone_list)
    host_index = 1                              #mutamos el num. de clone para que se procese en el siguiente loop
      
if host_index > 0 or not clone_list_random:     #Si el Clone por defecto no es Aleatorio, o hay ya un aleatorio seleccionado...
    i = 1
    for active_clone, channel_clone, host_clone, contentType_clone, info_clone in clone_list:
        if i == host_index:
            channel_clone_name = channel_clone                                  #Nombre del Canal elegido
            host = host_clone                                                   #URL del Canal elegido
            if active_clone == "1":                                             #Comprueba que el clone esté activo
                break
            channel_clone_name = "*** DOWN ***"                                 #es un fallo masivo ???
            for active_clone, channel_clone, host_clone, contentType_clone, info_clone in clone_list:
                if active_clone == "1":                                         #Comprueba que el clone esté activo
                    channel_clone_name = channel_clone                          #Nombre del Canal elegido
                    host = host_clone                                           #URL del Canal elegido
                    break
        i += 1
clone_list_inter = []
for clone in clone_list:
    clone_list_inter += [list(clone)]
clone_list = clone_list_inter[:]

forced_proxy_opt = 'ProxyWeb:hide.me'
CF_test = False

canonical = {
             'channel': channel_py, 
             'host': host, 
             'host_alt': [], 
             'host_black_list': [], 
             'retries_cloudflare': 5, 
             'CF': False, 'CF_test': CF_test, 'alfa_s': True, 
             'forced_proxy_opt': forced_proxy_opt
            }

if not channel_clone_post: channel_clone_post = channel_clone_post
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'
patron_canal = '(?:http.*\:)?\/\/(?:ww[^\.]*)?\.?(\w+)\.\w+(?:\/|\?|$)'
patron_torrent = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+(\/.*?\/)'
domain = scrapertools.find_single_match(host, patron_domain)
sufix = scrapertools.find_single_match(host, '\.\w+\/*$')
download_sufix = 'descargar/'
download_pre_url_torr = '/t_download/'
download_post_url_torr = '/download-link/'
download_post_url_torr_tail = '/dom-t/%s'
host_torrent = 'https://atomtt.com'

#Carga de opciones del canal        
__modo_grafico__ = config.get_setting('modo_grafico', channel_py)               #TMDB?
IDIOMAS_TMDB = {0: 'es', 1: 'en', 2: 'es,en'}
idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', channel_py)] # Idioma base para TMDB
idioma_busqueda_VO = IDIOMAS_TMDB[2]                                                # Idioma para VO
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel_py)  #Actualización sólo últ. Temporada?
timeout = config.get_setting('clonenewpct1_timeout_downloadpage', channel_py)   #Timeout downloadpage
#timeout = timeout * 2.5                                                         # Incremento temporal
if timeout == 0: timeout = None
season_colapse = config.get_setting('season_colapse', channel_py)               # Season colapse?
filter_languages = config.get_setting('filter_languages', channel_py)           # Filtrado de idiomas?
find_alt_link_option = config.get_setting('find_alt_link_option', channel_py)   # Buscamos enlaces alternativos en buscador externo

fecha_rango = config.get_setting('clonenewpct1_rango_fechas_novedades', channel_py) #Rango fechas para Novedades
if fecha_rango == 0: fecha_rango = 'Hoy'
elif fecha_rango == 1: fecha_rango = 'Ayer'
elif fecha_rango == 2: fecha_rango = 'Semana'
elif fecha_rango == 3: fecha_rango = 'Mes'
elif fecha_rango == 4: fecha_rango = 'Siempre'
episodio_serie = config.get_setting('clonenewpct1_serie_episodio_novedades', channel_py)    #Episodio o serie para Novedades

headers = {'referer': None}
DUMMY = 'DUMMY'
btdigg_label = ' [COLOR limegreen]BT[/COLOR][COLOR red]Digg[/COLOR]'
find_alt_link_result_save = []

#Temporal, sólo para actualizar newpct1_data.json con otro valor por defecto
#channel_banned = config.get_setting('clonenewpct1_excluir1_enlaces_veronline', channel_py)  #1eer Canal baneado
#if channel_banned == 9:
#    config.set_setting('clonenewpct1_excluir1_enlaces_veronline', 22, channel_py)      #se pone el nuevo valor por defecto


def mainlist(item):
    logger.info()
    
    itemlist = []

    thumb_cartelera = get_thumb("now_playing.png")
    
    thumb_pelis = get_thumb("channels_movie.png")
    thumb_pelis_hd = get_thumb("channels_movie_hd.png")
    thumb_pelis_VO = get_thumb("channels_vos.png")
    
    thumb_series = get_thumb("channels_tvshow.png")
    thumb_series_hd = get_thumb("channels_tvshow_hd.png")
    thumb_series_az = get_thumb("channels_tvshow_az.png")
    thumb_series_VOD = get_thumb("videolibrary_tvshow.png")
    
    thumb_documentales = get_thumb("channels_documentary.png")
    
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    
    global host
    item, host = verify_host(item, host)                                        # Actualizamos la url del host
    if channel_clone_name == "*** DOWN ***":                                    # Ningún clones activo !!!
        itemlist.append(item.clone(action='', title="[COLOR yellow]Ningún canal NewPct1 activo[/COLOR]"))    
        return itemlist                                     # si no hay más datos, algo no funciona, pintamos lo que tenemos y salimos

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, action="submenu_novedades", title="Novedades", 
                    url=item.channel_host + "ultimas-descargas/", extra="novedades", 
                    thumbnail=thumb_cartelera, category=item.category, channel_host=item.channel_host))

    itemlist.append(Item(channel=item.channel, action="submenu", title="Películas", 
                    url=item.channel_host, extra="peliculas", thumbnail=thumb_pelis, 
                    category=item.category, channel_host=item.channel_host))

    itemlist.append(Item(channel=item.channel, action="submenu", title="Series", 
                    url=item.channel_host, extra="series", thumbnail=thumb_series, 
                    category=item.category, channel_host=item.channel_host))
    
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar", 
                    url=item.channel_host + "buscar", thumbnail=thumb_buscar, 
                    category=item.category, channel_host=item.channel_host))
    
    clone_act = 'Clone: '
    if config.get_setting('clonenewpct1_channel_default', channel_py) == 0:
        clone_act = 'Aleatorio: '
    itemlist.append(Item(channel=item.channel, url=item.channel_host, 
                    title="[COLOR yellow]Configuración:[/COLOR] (" + clone_act + 
                    item.category + ")", folder=False, thumbnail=thumb_separador, 
                    category=item.category, channel_host=item.channel_host))
    
    itemlist.append(Item(channel=item.channel, action="configuracion", 
                    title="Configurar canal", thumbnail=thumb_settings, category=item.category, 
                    channel_host=item.channel_host))
    
    autoplay.show_option(item.channel, itemlist)                                #Activamos Autoplay
       
    item.category = '%s / %s' % (channel_py.title(), item.category.title())     #Newpct1: nombre de clone en pantalla Mainlist
        
    return itemlist
    
    
def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return
    

def submenu(item):
    logger.info()
    
    itemlist = []
    item.extra2 = ''
    matches_hd = []
    
    data_menu = '<li><a href="https://%s/peliculas/" title="Descargar Peliculas"><i class="icon-double-angle-right"></i>Peliculas</a></li><li><a href="https://%s/estrenos-de-cine/" title="Descargar Estrenos de Cine"><i class="icon-double-angle-right"></i>Estrenos de Cine</a></li><li><a href="https://%s/peliculas-latino/" title="Bajar Peliculas Latino"><i class="icon-double-angle-right"></i>Peliculas Latino</a></li><li><a href="https://%s/peliculas-hd/" title="Descargar Peliculas HD gratis"><i class="icon-double-angle-right"></i>Peliculas en HD</a></li><li><a href="https://%s/peliculas-3d/" title="Gratis Peliculas 3D"><i class="icon-double-angle-right"></i>Peliculas en 3D</a></li><li><a href="https://%s/peliculas-vo/" title="Ver online Peliculas Subtituladas"><i class="icon-double-angle-right"></i>Peliculas Subtituladas</a></li><li><a href="https://%s/otras-peliculas/" title="Otras Peliculas"><i class="icon-double-angle-right"></i>Otras Peliculas</a></li><li><a href="https://%s/peliculas-x264-mkv/" title="Peliculas x264 MKV"><i class="icon-double-angle-right"></i>Peliculas x264 MKV</a></li> <li><a href="https://%s/series/" title="Descargar Series"><i class="icon-double-angle-right"></i>Series</a></li><li><a href="https://%s/series-hd/" title="Series HD ver online"><i class="icon-double-angle-right"></i>Series HD</a></li><li><a href="https://%s/series-vo/" title="Gratis Series Subtituladas"><i class="icon-double-angle-right"></i>Series Subtituladas</a></li>' \
    % (domain, domain, domain, domain, domain, domain, domain, domain, domain, domain, domain)
    
    patron = '<li><a\s*(?:style="[^"]+"\s*)?href="([^"]+)"\s*.itle="[^"]+"\s*>'
    patron += '(?:<i\s*class="[^"]+">\s*<\/i>)?([^>]+)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data_menu)

    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data_menu)

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = scrapedurl
        headers = {'Referer': url, "User-Agent": 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}
        if 'otras-peliculas' in url:
            continue

        #Preguntamos por las entradas que no corresponden al "extra"
        if item.extra in scrapedtitle.lower() or (item.extra == "peliculas" and \
                    ("cine" in scrapedurl or "anime" in scrapedurl)) or \
                    (item.extra == "varios" and ("documentales" in scrapedurl \
                    or "varios" in scrapedurl)):
            
            #Si tiene filtro de idiomas, marcamos estas páginas como no filtrables
            if "castellano" in title.lower() or "latino" in title.lower() or \
                    "subtituladas" in title.lower() or "vo" in title.lower() or \
                    "v.o" in title.lower() or "- es" in title.lower():
                item.extra2 = "categorias"
            else:
                item.extra2 = ""
            
            #Arreglo para Desacargas2020
            if url == item.url:
                url = url + item.extra + '/'
            
            itemlist.append(item.clone(action="listado", title=title, url=url+page_url, headers=headers))
            
            if matches_hd and 'HD' in title:
                for scrapedurlcat, scrapedtitlecat in matches_hd:               #Pintamos las categorías de peliculas en HD
                    if 'uhd4k' in scrapedtitlecat.lower():                      #... ignoramos uhd4k, lo dejamos para el final
                        continue
                    itemlist.append(item.clone(action="listado", title="   - Calidad: " 
                            + scrapedtitlecat, url=scrapedurlcat+page_url, headers=headers))
            
            itemlist.append(item.clone(action="alfabeto", title=title + " [A-Z]", url=url, headers=headers))
    
    if item.extra == "peliculas":
        itemlist.append(item.clone(action="listado", title="Películas 4K Full UHD", 
                    url=item.channel_host + "peliculas-hd/4kultrahd/"+page_url, headers=headers))
        itemlist.append(item.clone(action="alfabeto", title="Películas 4K Full UHD" + 
                    " [A-Z]", url=item.channel_host + "peliculas-hd/4kultrahd/"+page_url, headers=headers))

    return itemlist
    

def submenu_OLD(item):
    logger.info()
    
    itemlist = []
    item.extra2 = ''
    matches_hd = []
    headers = {'referer': item.url}
    
    global host
    item, host = verify_host(item, host)                                        # Actualizamos la url del host
    
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, s2=False, headers=headers, 
                                                               decode_code=decode_code, canonical=canonical, 
                                                               quote_rep=True, CF_test=CF_test, item=item, itemlist=[])   # Descargamos la página
    # Verificamos si ha cambiado el Host
    if response.host:
        global sufix, domain, clone_list
        sufix = scrapertools.find_single_match(response.host, '\.\w+\/*$')
        domain = scrapertools.find_single_match(response.host, patron_domain)
        clone_list[0][2] = host

    patron = '(?:Inicio|Categorias)'
    
    #logger.debug("PATRON: " + patron)
    #logger.debug(data)
    
    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    #Si no hay datos consistentes, llamamos al método de fail_over para que encuentre un canal que esté activo y pueda gestionar el submenú
    if not data or not scrapertools.find_single_match(data, patron):
        item, data = generictools.fail_over_newpct1(item, patron.replace('|', '¡'), timeout=timeout)
    
    if not data:                                                                #Si no ha logrado encontrar nada, salimos
        itemlist.append(item.clone(action='', title="[COLOR yellow]" + item.category 
                    + '[/COLOR]: Ningún canal NewPct1 activo'))    
        itemlist.append(item.clone(action='', title=item.category + 
                    ': ERROR 01: SUBMENU: La Web no responde o ha cambiado de URL. ' 
                    + 'Si la Web está activa, reportar el error con el log'))
        return itemlist                                                         #si no hay más datos, algo no funciona, pintamos lo que tenemos
    
    elif item.channel_alt:                                                      #Si ha habido fail-over, lo comento
        itemlist.append(item.clone(action='', title="[COLOR yellow]" + 
                    item.category + '[/COLOR] [ALT ] en uso'))
        itemlist.append(item.clone(action='', title="[COLOR yellow]" + 
                    item.channel_alt.capitalize() + '[/COLOR] inaccesible'))
        
        if item.url_alt: del item.url_alt
        del item.channel_alt

    # Seleccionamos el bloque que nos interesa
    patron = '<li><a\s*class="[^"]+"\s*href="[^"]+"><i\s*class="[^"]+".*?><\/i>.*?'
    patron += 'Inicio.*?<\/a><\/li>(.*?)<\/ul>\s*<\/nav>'
    if not scrapertools.find_single_match(data, patron):
        patron = '<div\s*class="links-content">\s*<div class="one_fourth">\s*<h3>'
        patron += 'Categorias<\/h3>\s*<ul class="content-links">(.*?)<\/ul>\s*<\/div>'
        if not scrapertools.find_single_match(data, patron):
            patron = '<div\s*class="[^"]+">\s*<h4>\s*Categorias\s*<\/h4>\s*<ul>(.*?)<\/ul>\s*<\/div>'
    
    data_menu = scrapertools.find_single_match(data, patron)                    #Seleccionamos el trozo que nos interesa
    if not data_menu:
        try:
            logger.error("ERROR 02: SUBMENU: Ha cambiado la estructura de la Web " 
                    + " / PATRON: " + patron + " / DATA: " + data)
        except:
            logger.error("ERROR 02: SUBMENU: Ha cambiado la estructura de la Web " 
                    + " / PATRON: " + patron + " / DATA: (probablemente bloqueada por antivirus)")
        itemlist.append(item.clone(action='', title=item.category + 
                    ': ERROR 02: SUBMENU: Ha cambiado la estructura de la Web.  ' 
                    + ' Reportar el error con el log'))
        return itemlist                                                         #si no hay más datos, algo no funciona, pintamos lo que tenemos

    # Procesamos la página
    patron = '<li><a\s*(?:style="[^"]+"\s*)?href="([^"]+)"\s*.itle="[^"]+"\s*>'
    patron += '(?:<i\s*class="[^"]+">\s*<\/i>)?([^>]+)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data_menu)
    
    if not 'series' in str(matches):
        #patron_series = '<\/ul><\/li><li\s*class="li-series">\s*<a\s*href="([^"]+)">\s*<i\s*class=[^>]+>\s*<\/i>\s*<br>\s*(\w+)\s*<\/a>'
        matches.append((host + 'series/', 'Series'))

    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data_menu)
    
    if not matches:
        logger.error("ERROR 02: SUBMENU: Ha cambiado la estructura de la Web " + 
                    " / PATRON: " + patron + " / DATA: " + data_menu)
        itemlist.append(item.clone(action='', title=item.category + 
                    ': ERROR 02: SUBMENU: Ha cambiado la estructura de la Web.  ' 
                    + 'Reportar el error con el log'))
        return itemlist                                                         #si no hay más datos, algo no funciona, pintamos lo que tenemos

    # Para películas, ahondamos en calidades
    if item.extra == "peliculas":
        patron = '<h3\s*(?:style="[^"]+")?>(?:<strong>)?Peliculas(?:<\/strong>)? en HD '
        patron += '<a href="[^"]+"\s*class="[^"]+"\s*title="[^"]+">(?:ver .*?)?<\/a>'
        patron += '<span(?:\s*style="[^"]+")?>(.*?)(?:<\/span>)?<\/h3>'
        data_hd = scrapertools.find_single_match(data, patron)                  #Seleccionamos el trozo que nos interesa
        if data_hd:
            patron = '<a\s*href="([^"]+)"\s*.itle="[^"]+"\s*>([^<]+)\s*<'
            matches_hd = re.compile(patron, re.DOTALL).findall(data_hd)
            #logger.debug(matches_hd)
    
    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = scrapedurl
        if 'otras-peliculas' in url:
            continue

        #Preguntamos por las entradas que no corresponden al "extra"
        if item.extra in scrapedtitle.lower() or (item.extra == "peliculas" and \
                    ("cine" in scrapedurl or "anime" in scrapedurl)) or \
                    (item.extra == "varios" and ("documentales" in scrapedurl \
                    or "varios" in scrapedurl)):
            
            #Si tiene filtro de idiomas, marcamos estas páginas como no filtrables
            if "castellano" in title.lower() or "latino" in title.lower() or \
                    "subtituladas" in title.lower() or "vo" in title.lower() or \
                    "v.o" in title.lower() or "- es" in title.lower():
                item.extra2 = "categorias"
            else:
                item.extra2 = ""
            
            #Arreglo para Desacargas2020
            if url == item.url:
                url = url + item.extra + '/'
            
            itemlist.append(item.clone(action="listado", title=title, url=url+page_url))
            
            if matches_hd and 'HD' in title:
                for scrapedurlcat, scrapedtitlecat in matches_hd:               #Pintamos las categorías de peliculas en HD
                    if 'uhd4k' in scrapedtitlecat.lower():                      #... ignoramos uhd4k, lo dejamos para el final
                        continue
                    itemlist.append(item.clone(action="listado", title="   - Calidad: " 
                            + scrapedtitlecat, url=scrapedurlcat+page_url))
            
            itemlist.append(item.clone(action="alfabeto", title=title + " [A-Z]", url=url))
    
    if item.extra == "peliculas":
        itemlist.append(item.clone(action="listado", title="Películas 4K Full UHD", 
                    url=item.channel_host + "peliculas-hd/4kultrahd/"+page_url))
        itemlist.append(item.clone(action="alfabeto", title="Películas 4K Full UHD" + 
                    " [A-Z]", url=item.channel_host + "peliculas-hd/4kultrahd/"+page_url))

    return itemlist


def submenu_novedades(item):
    logger.info()

    itemlist = []
    itemlist_alt = []
    item.extra2 = ''
    timeout_search=timeout * 2                                                  #Más tiempo para Novedades, que es una búsqueda

    thumb_buscar = get_thumb("search.png")
    thumb_settings = get_thumb("setting_0.png")

    global host
    item, host = verify_host(item, host, category=category)        # Actualizamos la url del host
    headers = {'referer': host}
    
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout_search, s2=False, 
                                                               headers=headers, decode_code=decode_code, canonical=canonical, 
                                                               quote_rep=True, CF_test=CF_test, item=item, itemlist=[])     # Descargamos la página
    # Verificamos si ha cambiado el Host
    if response.host:
        global sufix, domain, clone_list
        sufix = scrapertools.find_single_match(response.host, '\.\w+\/*$')
        domain = scrapertools.find_single_match(response.host, patron_domain)
        clone_list[0][2] = host

    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    #Si no hay datos consistentes, llamamos al método de fail_over para que encuentre un canal que esté activo y pueda gestionar el submenú
    #patron = '<div class="content">.*?<ul class="noticias'
    patron = '<div class="content">.*?$'
    if not data or not scrapertools.find_single_match(data, patron):
        item, data = generictools.fail_over_newpct1(item, patron, timeout=timeout_search)
    
    if not data:                                                                #Si no ha logrado encontrar nada, salimos
        itemlist.append(item.clone(action='', title="[COLOR yellow]" + item.category + 
                    '[/COLOR]: Ningún canal NewPct1 activo'))    
        itemlist.append(item.clone(action='', title=item.category + 
                    ': ERROR 01: SUBMENU: La Web no responde o ha cambiado de URL. ' 
                    + ' Si la Web está activa, reportar el error con el log'))
        return itemlist                                     #si no hay más datos, algo no funciona, pintamos lo que tenemos
    
    elif item.channel_alt:                                                      #Si ha habido fail-over, lo comento
        itemlist.append(item.clone(action='', title="[COLOR yellow]" + item.category 
                    + '[/COLOR] [ALT ] en uso'))
        itemlist.append(item.clone(action='', title="[COLOR yellow]" + item.channel_alt.capitalize() 
                    + '[/COLOR] inaccesible'))
        
        item.from_channel_alt = item.channel_alt
        #if item.url_alt: del item.url_alt
        #del item.channel_alt
        
    # Procesamos la página
    data = scrapertools.find_single_match(data, patron)                         #Seleccionamos el trozo que nos interesa
    patron = '<option value="([^"]+)".*?>(.*?)<\/option>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)
    
    # Si es el formato reducido, pasamos directamente a Listado
    if not matches:
        item.action = "listado"
        #item.url = '%spg/1' % item.url
        return listado(item)
    
    
    """ Continuamos con el formato COMPLETO (ya en deshuso, desafortunadamente...) """
    itemlist.append(item.clone(action='', title="[COLOR yellow]Ver lo Último de:[/COLOR]"))
    for value, title in matches:
        if not value.isdigit():
            if title not in "Mes": 
                item.post = "date=%s&pg=1" % value
                itemlist.append(item.clone(action="listado", title=title, 
                        url=item.url+page_url, post=item.post))
    
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar", url=item.channel_host 
                        + "buscar", thumbnail=thumb_buscar, category=item.category, 
                        channel_host=item.channel_host))
    
    itemlist.append(item.clone(action='', title="[COLOR yellow]Lo Último en la " 
                        + "Categoría de [B]%s[/B][/COLOR]" % fecha_rango))
    for value, title in matches:
        if value.isdigit():
            if title not in "Juegos, Software, Musica, Deportes":
                
                #tratamos de poner al principio las categorías más relevantes
                if value == '1027': title = "01" + title                        #Pelis HD
                elif value == '757': title = "02" + title                       #Pelis Castellano
                elif value == '1527': title = "03" + title                      #Pelis Latino
                elif value == '1469': title = "04" + title                      #Series HD
                elif value == '767': title = "05" + title                       #Series
                else: title = "99" + title                                      #Resto

                item.post = "categoryIDR=%s&date=%s&pg=1" % (value, fecha_rango)
                itemlist_alt.append(item.clone(action="listado", title=title, 
                        url=item.url+page_url, post=item.post))
    
    itemlist_alt = sorted(itemlist_alt, key=lambda it: it.title)                #clasificamos
    for item_local in itemlist_alt:
        item_local.title = re.sub(r'^\d{2}', '', item_local.title)              #Borramos la secuencia
        
        #Si tiene filtro de idiomas, marcamos estas páginas como no filtrables
        if "castellano" in item_local.title.lower() or "latino" in item_local.title.lower() \
                    or "subtituladas" in item_local.title.lower() or "vo" in \
                    item_local.title.lower() or "v.o" in item_local.title.lower() \
                    or "- es" in item_local.title.lower():
            item_local.extra2 = "categorias"
        else:
            item_local.extra2 = ""
        
        itemlist.append(item_local.clone())
        
    itemlist.append(Item(channel=item.channel, action="", title="[COLOR yellow]Configuración de " 
                    + "Novedades:[/COLOR]", url="", thumbnail=thumb_settings, 
                    category=item.category, channel_host=item.channel_host))
    itemlist.append(Item(channel=item.channel, action="configuracion", 
                    title="Periodos y formatos de series en Novedades", url="", 
                    thumbnail=thumb_settings, category=item.category, 
                    channel_host=item.channel_host))

    return itemlist
    
    
def alfabeto(item):
    logger.info()
    itemlist = []

    global host
    item, host = verify_host(item, host)                                        # Actualizamos la url del host
    headers = {'referer': host}
    
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, s2=False, headers=headers, CF_test=CF_test, 
                                                               decode_code=decode_code, quote_rep=True, 
                                                               item=item, itemlist=[])          # Descargamos la página

    #Si no hay datos consistentes, llamamos al método de fail_over para que encuentre un canal que esté activo y pueda gestionar el submenú
    patron = '<ul class="alfabeto">(.*?)</ul>'
    if not data or not scrapertools.find_single_match(data, patron):
        item, data = generictools.fail_over_newpct1(item, patron, timeout=timeout)
    
    if not data:                                                                #Si no ha logrado encontrar nada, salimos
        itemlist.append(item.clone(action='', title="[COLOR yellow]" + item.category + 
                        '[/COLOR]: Ningún canal NewPct1 activo'))    
        itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 01: ALFABETO: La Web no responde o ha cambiado de URL. ' 
                        + 'Si la Web está activa, reportar el error con el log'))
        return itemlist                                                         #si no hay más datos, algo no funciona, pintamos lo que tenemos
    
    elif item.channel_alt:                                                      #Si ha habido fail-over, lo comento
        itemlist.append(item.clone(action='', title="[COLOR yellow]" + 
                        item.category + '[/COLOR] [ALT ] en uso'))
        itemlist.append(item.clone(action='', title="[COLOR yellow]" + 
                        item.channel_alt.capitalize() + '[/COLOR] inaccesible'))
        
        if item.url_alt: del item.url_alt
        del item.channel_alt
    
    # Proecesamos la página
    data = scrapertools.find_single_match(data, patron)
    patron = '<a href="([^"]+)"[^>]*>([^>]*)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)
    
    if not matches:
        logger.error("ERROR 02: ALFABETO: Ha cambiado la estructura de la Web " + 
                        " / PATRON: " + patron + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: ALFABETO: Ha cambiado la estructura de la Web.  ' 
                        + 'Reportar el error con el log'))
        return itemlist                                                         #si no hay más datos, algo no funciona, pintamos lo que tenemos

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.upper()

        itemlist.append(item.clone(action="listado", title=title, url=scrapedurl))

    return itemlist


def listado(item, alfa_s=False):                                                              # Listado principal y de búsquedas
    logger.info()
    
    itemlist = []
    clase = "pelilist"                                                          # etiqueta para localizar zona de listado de contenidos
    if item.pattern:
        clase = item.pattern
    
    thumb_pelis = get_thumb("channels_movie.png")
    thumb_series = get_thumb("channels_tvshow.png")
    
    global host
    item, host = verify_host(item, host, post=item.post)                        # Actualizamos la url del host
    if channel_clone_name == "*** DOWN ***":                                    #Ningún clones activo !!!
        itemlist.append(item.clone(action='', title="[COLOR yellow]Ningún canal NewPct1 activo[/COLOR]"))    
        return itemlist 

    #logger.debug(item)
    
    curr_page = 1                                                               # Página inicial
    last_page = 99999                                                           # Última página inicial
    page_name = 'pg'                                                            # Nombre de pie de página (pg o page)
    last_page_print = 1                                                         # Última página inicial, para píe de página
    page_factor = 1.0                                                           # Factor de conversión de pag. web a pag. Alfa
    if item.curr_page:
        curr_page = int(item.curr_page)                                         # Si viene de una pasada anterior, lo usamos
        del item.curr_page                                                      # ... y lo borramos
    if item.last_page:
        last_page = int(item.last_page)                                         # Si viene de una pasada anterior, lo usamos
        del item.last_page                                                      # ... y lo borramos
    if item.page_factor:
        page_factor = float(item.page_factor)                                   # Si viene de una pasada anterior, lo usamos
        del item.page_factor                                                    # ... y lo borramos
    if item.last_page_print:
        last_page_print = item.last_page_print                                  # Si viene de una pasada anterior, lo usamos
        del item.last_page_print                                                # ... y lo borramos
    if item.cnt_tot_match:
        cnt_tot_match = float(item.cnt_tot_match)                               # restauramos el contador TOTAL de líneas procesadas de matches
        del item.cnt_tot_match
    else:
        cnt_tot_match = 0.0                                                     # Contador TOTAL de líneas procesadas de matches
    
    cnt_tot = 30                                                                # Poner el num. máximo de items por página
    cnt_title = 0                                                               # Contador de líneas insertadas en Itemlist
    inicio = time.time()                                    # Controlaremos que el proceso no exceda de un tiempo razonable
    fin = inicio + 5                                                            # Después de este tiempo pintamos (segundos)
    timeout_search = timeout * 2                                                # Timeout para descargas
    if item.extra == 'search' and item.extra2 == 'episodios':                   # Si viene de episodio se quitan los límites
        cnt_tot = 999
        fin = inicio + 30

    #Sistema de paginado para evitar páginas vacías o semi-vacías en casos de búsquedas con series con muchos episodios
    title_lista = []                            # Guarda la lista de series que ya están en Itemlist, para no duplicar lineas
    if item.title_lista:                                    # Si viene de una pasada anterior, la lista ya estará guardada
        title_lista.extend(item.title_lista)                                    # Se usa la lista de páginas anteriores en Item
        del item.title_lista                                                    # ... limpiamos
    matches = []
    last_match = ''
        
    if not item.extra2:                                                         # Si viene de Catálogo o de Alfabeto
        item.extra2 = ''
        
    post = None
    forced_proxy_opt_loc = forced_proxy_opt
    headers = {'referer': host}
    if item.post:
        forced_proxy_opt_loc = 'Proxydirect'
        canonical['forced_proxy_opt'] = forced_proxy_opt_loc
        canonical['retries_cloudflare'] = 0
    if item.post or item.post is None:                                          # Rescatamos el Post, si lo hay
        post = item.post
        del item.post
    if item.headers or item.headers is None:                                    # Rescatamos el Headers, si lo hay
        headers = item.headers
        del item.headers

    next_page_url = item.url
    #Máximo num. de líneas permitidas por TMDB. Máx de 5 segundos por Itemlist para no degradar el rendimiento
    while (cnt_title < cnt_tot and curr_page <= last_page and fin > time.time()) or item.matches:
    
        # Descarga la página
        data = ''
        fichas = ''
        cnt_match = 0                                                           # Contador de líneas procesadas de matches

        if not item.matches:                                                    # si no viene de una pasada anterior, descargamos
            data, response, item, itemlist = generictools.downloadpage(next_page_url, timeout=timeout_search, post=post, CF_test=CF_test, 
                                                                       s2=True, headers=headers, decode_code=decode_code, 
                                                                       quote_rep=True, no_comments=False, canonical=canonical, 
                                                                       forced_proxy_opt=forced_proxy_opt_loc, 
                                                                       item=item, itemlist=itemlist, alfa_s=alfa_s)
            curr_page += 1                                                      #Apunto ya a la página siguiente
            
            # Verificamos si ha cambiado el Host
            if response.host:
                global sufix, domain, clone_list
                sufix = scrapertools.find_single_match(response.host, '\.\w+\/*$')
                domain = scrapertools.find_single_match(response.host, patron_domain)
                clone_list[0][2] = host
                return listado(item)
            
            #seleccionamos el bloque que nos interesa
            search1 = '<h3><strong>( 0 ) Resultados encontrados </strong>'
            search2 = '"data":{"total":\d+,"all":\d+,"items":0'                 # Fin de páginas con patrón "torrentName" (json)
            search3 = '<ul class="noticias-series"></ul></form></div><!-- end .page-box -->'
            if item.extra == "novedades":
                patron = '<div class="content">.*?<ul class="noticias(.*?)<\/div><!-- end .content -->'
                patron = '<div class="content">.*?$'
                if not scrapertools.find_single_match(data, patron) and not search1 in data:
                    patron = '<div class="content">.*?<ul class="noticias(.*?)<\/li><\/ul>(?:<\/form>)?<\/div>'
                    if not scrapertools.find_single_match(data, patron) and not search1 in data:
                        patron = 'patron|'
                        patron += '<div class="content">.*?$|'
                        patron += '<div class="content">.*?<ul class="noticias(.*?)<\/li><\/ul>(?:<\/form>)?<\/div>'
            elif scrapertools.find_single_match(data, '"torrentName":'):
                patron = '"torrentName":\s*"([^"]+)",\s*'                       #título
                patron += '"calidad":\s*(?:"([^"]+)"|null),.*?'                 #calidad
                patron += '"torrentSize":\s*"([^"]+)",\s*'                      #tamaño (significativo para peliculas)
                patron += '"imagen":\s*"([^"]+)",'                              #thumb
                patron += '"guid":"([^"]+)"'                                    #url
                patron += '()'                                                  #año (dummy)
            else:
                patron = '<ul class="%s">(.*?)</ul>' % clase

            #logger.debug("PATRON: " + patron)
            #logger.debug(data)
            
            #Si no hay datos consistentes, llamamos al método de fail_over para que encuentre un canal que esté activo y pueda gestionar la lista
            if not data or (not scrapertools.find_single_match(data, patron) and 'letter/' not in item.url):

                if search1 in data or scrapertools.find_single_match(data, search2):    # Si es una búsqueda, a veces la última pag. está mal
                    last_page = 0
                    if len(itemlist) > 0:                                       # Si hay algo que pintar lo pintamos
                        break
                    return itemlist                                             #Salimos
                
                logger.error("ERROR 02: LISTADO: Ha cambiado la estructura de la Web " 
                        + " / PATRON: " + patron + " / DATA: " + data)
                if item.extra == "search":
                    item, data = generictools.fail_over_newpct1(item, '', timeout=timeout_search)
                else:
                    item, data = generictools.fail_over_newpct1(item, patron, timeout=timeout)
                cnt_tot_match += len(itemlist)
            
            if not data:                                                        #Si no ha logrado encontrar nada, salimos
                itemlist.append(item.clone(action='', title="[COLOR yellow]" + 
                            item.channel.capitalize() + '[/COLOR]: Ningún canal NewPct1 activo'))    
                itemlist.append(item.clone(action='', title=item.category + 
                            ': ERROR 01: LISTADO: La Web no responde o ha cambiado de URL. ' 
                            + 'Si la Web está activa, reportar el error con el log'))
                
                if len(itemlist) > 2:                                           # Si hay algo que pintar lo pintamos
                    last_page = 0
                    break
                return itemlist                                                 #Salimos
            
            elif item.channel_alt:                                              #Si ha habido fail-over, lo comento
                for active_clone, channel_clone, host_clone, contentType_clone, info_clone in clone_list:
                    if channel_clone == item.category.lower():
                        host = host_clone
                        break

            #Selecciona el tramo de la página con el listado de contenidos
            if item.extra == "novedades":
                patron = '<div class="content">.*?$'
                if not scrapertools.find_single_match(data, patron):
                    patron = '<div class="content">.*?<ul class="noticias(.*?)<\/div><!-- end .content -->'  
            elif scrapertools.find_single_match(data, '"torrentName":'):
                patron = '"torrentName":\s*"([^"]+)",\s*"calidad":\s*(?:"([^"]+)"|null),.*?'
                patron += '"torrentSize":\s*"([^"]+)",\s*"imagen":\s*"([^"]+)","guid":"([^"]+)"'
            else:
                patron = '<ul class="%s">(.*?)</ul>' % clase
            
            if not scrapertools.find_single_match(data, '"torrentName":'):
                fichas = scrapertools.find_single_match(data, patron)
            else:
                fichas = data
            
            if not fichas and not search1 in data and 'letter/' not in item.url:    #error
                logger.error("ERROR 02: LISTADO: Ha cambiado la estructura de la Web " 
                        + " / PATRON: " + patron + " / DATA: " + data)
                itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: LISTADO: Ha cambiado la estructura de la Web.  ' 
                        + 'Reportar el error con el log'))
                return itemlist                                                 #si no hay más datos, algo no funciona, pintamos lo que tenemos
            elif search1 in data:                                               #no hay vídeos
                return itemlist
        
        #Scrapea los datos de cada vídeo.  Título alternativo se mantiene, aunque no se usa de momento
        if item.extra == "novedades":
            patron = '<li><a\s*href="(?P<scrapedurl>[^"]+)"\s*'                 #url
            patron += '(?:style="[^"]+"\s*)?title="(?P<scrapedtitle>[^"]+)"[^>]*>\s*'   #título
            patron += '<img[^>]*src="(?P<scrapedthumbnail>[^"]+)"?.*?'          #thumb
            patron += '<\/h2>\s*<\/a>\s*<span[^>]+>(?P<calidad>.*?)?'           #calidad
            patron += '<(?P<year>[^>]*)?'                                       #año
            patron += '>Tama.*?\s(?P<size>\d+[.|\s].*?[GB|MB])?\s*<\/strong>'   #tamaño (significativo para peliculas)
        elif scrapertools.find_single_match(data, '"torrentName":'):
            patron = '"torrentName":\s*"([^"]+)",\s*'                           #título
            patron += '"calidad":\s*(?:"([^"]+)"|null),.*?'                     #calidad
            patron += '"torrentSize":\s*"([^"]+)",\s*'                          #tamaño (significativo para peliculas)
            patron += '"imagen":\s*"([^"]+)",'                                  #thumb
            patron += '"guid":"([^"]+)"'                                        #url
            patron += '()'                                                      #año (dummy)
        elif item.extra == "search":
            patron = '<li[^>]*>\s*<a href="(?P<scrapedurl>[^"]+)"\s*'           #url
            patron += 'title="(?P<scrapedtitle>[^"]+)">\s*'                     #título
            patron += '<img.*?src="(?P<scrapedthumbnail>[^"]+)?".*?'            #thumb
            patron += '<h2.*?(?P<calidad>\[.*?)?<\/h2.*?'                       #calidad
            patron += '<span.*?>\d+-\d+-(?P<year>\d{4})?<\/span>*.?'            #año
            patron += '<span.*?>(?P<size>\d+[\.|\s].*?[GB|MB])?<\/span>'        #tamaño (significativo para peliculas)
        else:
            patron = '<a href="([^"]+)"\s*'                                     # la url
            patron += 'title="([^"]+)"[^>]*>\s*'                                # el titulo
            patron += '<img.*?src="([^"]+)"[^>]*>\s*'                           # el thumbnail
            patron += '<h2.*?>[^<]*<\/h2>\s*'                                   # titulo alternativo.  Se trunca en títulos largos (dummy)
            patron += '<span>([^<].*?)?<'                                       # la calidad
            patron += '()'                                                      # Año (dummy, compatibilidad search)
            patron += '()'                                                      # Size (dummy, compatibilidad search)

        if not item.matches:                                                    # De pasada anterior o desde Novedades?
            matches = re.compile(patron, re.DOTALL).findall(fichas)
        else:
            matches = item.matches
            del item.matches
            
        #logger.debug("PATRON: " + patron)
        #logger.debug(len(matches))
        #logger.debug(matches)
        #logger.debug(fichas)
        
        if last_match == str(matches[0]):
            break                                                               # No hay más resultados.  Salimos

        if not matches and not search1 in fichas and not scrapertools.find_single_match(data, search2) \
                        and not search3 in fichas and 'letter/' not in item.url:    #error
            logger.error("ERROR 02: LISTADO: Ha cambiado la estructura de la Web " 
                        + " / PATRON: " + patron + " / DATA: " + fichas)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + 
                        ': ERROR 02: LISTADO: Ha cambiado la estructura de la Web.  ' 
                        + 'Reportar el error con el log'))
            if len(itemlist) > 1:                                               # Si hay algo que pintar lo pintamos
                last_page = 0
                break
            return itemlist                                                     #Salimos
            
        if not matches and (search1 in fichas or scrapertools.find_single_match(data, search2) \
                        or search3 in fichas):                                  # Fin de páginas
            if len(itemlist) > 1:                                               # Si hay algo que pintar lo pintamos
                last_page = 0
                break
            return itemlist                                                     #Salimos

        """
        #Buscamos la última página
        """
        if last_page == 99999:                                                  #Si es el valor inicial, buscamos
            patron_last = '"total":\d+,"all":(\d+),'
            if not scrapertools.find_single_match(data, patron_last):
                patron_last = '<a href="[^"]+\/(\d+)">Last<\/a><\/li>'
                if not scrapertools.find_single_match(data, patron_last):
                    patron_last = '<ul class="pagination">.*?'
                    patron_last += '<a\s*href="[^"]+pg[\/|=]\d+">Next<\/a>.*?<a\s*href="[^"]'
                    patron_last += '+pg[\/|=](\d+)">Last<\/a>'
                    if not scrapertools.find_single_match(data, patron_last):
                        patron_last = '<ul class="pagination">.*?<a\s*href="[^"]+"(?:\s*onClick='
                        patron_last += '".*?\(\'[^"]+\'\);">Next<\/a>.*?onClick=".*?\(\'([^"]+)\'\)'
                        patron_last += ';">Last<\/a>)'
                        if not scrapertools.find_single_match(data, patron_last):
                            patron_last = '<ul\s*class="pagination"\s*>.*?<li>\s*<a\s*href='
                            patron_last += '"[^"]+\/page\/(\d+)\/"\s*>\s*&raquo;\s*<\/a>\s*<\/li>\s*&nbsp;\s*<\/div>'
                            page_name = 'page'

            try:
                last_page = int(scrapertools.find_single_match(data, patron_last))
                page_factor = float(len(matches)) / float(cnt_tot)
            except:                                                             #Si no lo encuentra, lo ponemos a 1
                last_page = 1
                last_page_print = int((float(len(matches)) / float(cnt_tot)) + 0.999999)
            if item.extra == "search":
                last_page = 999                                                 # La gestión de última pag. en search es penosa...
                last_page_print = int((float(len(matches)) / float(cnt_tot)) + 0.999999)
            if not post:
                next_page_url += '%s/1' % page_name
                item.url = next_page_url
            #logger.debug('curr_page: ' + str(curr_page) + ' / last_page: ' + str(last_page) + ' / page_factor: ' + str(page_factor))
        
        #Buscamos la próxima página
        if post:                                                                # Search o Novedades antiguas
            post = re.sub(r'\&%s=(\d+)' % page_name, '&%s=%s' % (page_name, str(curr_page)), post)
            next_page_log = post
        else:                                                                   # Resto
            #next_page_url = re.sub(r'%s\/\d+' % page_name, '%s/%s' % (page_name, str(curr_page)), item.url)
            next_page_url = re.sub(r'\/\d+$', '/%s' % (str(curr_page)), item.url)
            next_page_log = next_page_url
        """
        logger.debug('curr_page: ' + str(curr_page) + ' / last_page: ' + str(last_page) + \
                    ' / page_factor: ' + str(page_factor) + ' / cnt_tot_match: ' +  str(cnt_tot_match) + \
                    ' / url o post: ' +  str(next_page_log))
        """

        #Empezamos el procesado de matches
        for _scrapedurl, _scrapedtitle, _scrapedthumbnail, _calidad, _year, _size in matches:
            
            scrapedurl = _scrapedurl
            scrapedtitle = _scrapedtitle
            scrapedthumbnail = _scrapedthumbnail
            calidad = _calidad.replace('creeener', 'creener')
            year = _year
            size = _size
            
            if scrapertools.find_single_match(data, '"torrentName":') or 'pictures' in _calidad or 'images' in _calidad:
                scrapedtitle = scrapertools.find_single_match(_scrapedurl, '^(.*?)\s*(?:-(?:\s*[T|t]emp)|\[|$)')
                calidad = _scrapedtitle.replace('creeener', 'creener')
                size = _scrapedthumbnail
                scrapedthumbnail = _calidad.replace('\\', '')
                scrapedthumbnail = urlparse.urljoin(host, scrapedthumbnail)
                scrapedurl = _year.replace('\\', '')
                scrapedurl = urlparse.urljoin(host, scrapedurl)
                year = _size
            
            cnt_match += 1
            
            title = scrapedtitle
            title = scrapertools.remove_htmltags(title).rstrip('.')             # Removemos Tags del título
            url = urlparse.urljoin(host, scrapedurl)
            title_subs = []                                                     # creamos una lista para guardar info importante
            
            # Slugify, pero más light
            title = title.replace("á", "a").replace("é", "e").replace("í", "i")\
                    .replace("ó", "o").replace("ú", "u").replace("ü", "u")\
                    .replace("ï¿½", "ñ").replace("Ã±", "ñ")\
                    .replace("\\u00c3\\u00b1", "ñ").replace("\\u00c3\\u00ad", "í")
            title = scrapertools.decode_utf8_error(title)

            #logger.debug(title)
            
            last_match = str(matches[-1])

            if ("juego/" in scrapedurl or "xbox" in scrapedurl.lower()) and not "/serie" \
                    in scrapedurl or "xbox" in scrapedtitle.lower() or "windows" in \
                    scrapedtitle.lower() or "windows" in calidad.lower() or "nintendo" \
                    in scrapedtitle.lower() or "xbox" in calidad.lower() or "epub" in \
                    calidad.lower() or "pdf" in calidad.lower() or "pcdvd" in calidad.lower() \
                    or "crack" in calidad.lower():                              # no mostramos lo que no sean videos
                continue
            
            # Salvo que venga la llamada desde Episodios, se filtran las entradas para evitar duplicados de Temporadas
            if scrapedurl in title_lista or scrapedthumbnail in title_lista:    # si ya se ha tratado, pasamos al siguiente item
                continue                                                        # solo guardamos la url para series y docus
            elif ".com/serie" in scrapedurl or "/serie" in scrapedurl or "-serie" \
                    in scrapedurl or "varios/" in scrapedurl:
                title_lista += [scrapedurl]
                title_lista += [scrapedthumbnail]
            
            # Tratamiento especial para Novedades, con opciones como 4K
            if item.extra == "novedades" and item.extra2:
                if not item.extra2 in url.lower() and not item.extra2 in scrapedtitle.lower() and not item.extra2 in scrapedtitle.lower():
                    continue
            
            cnt_title += 1                                                      # Incrementamos el contador de entradas válidas
            
            item_local = item.clone()                                           # Creamos copia de Item para trabajar
            if item_local.tipo:                                                 # ... y limpiamos
                del item_local.tipo
            if item_local.totalItems:
                del item_local.totalItems
            if item_local.post:
                del item_local.post
            if item_local.pattern:
                del item_local.pattern
            if item_local.category:
                del item_local.category
            if item_local.intervencion:
                del item_local.intervencion
            if item_local.viewmode:
                del item_local.viewmode
            item_local.extra2 = True
            del item_local.extra2
            item_local.text_bold = True
            del item_local.text_bold
            item_local.text_color = True
            del item_local.text_color
            item_local.matches = []
            del item_local.matches
            item_local.title_lista = []
            del item_local.title_lista
            
            item_local.title = ''
            item_local.context = "['buscar_trailer']"
            item_local.quality = calidad
            
            #Guardamos el resto de variables del vídeo
            item_local.url = url
            if not item_local.url.startswith("http"):                           #Si le falta el http.: lo ponemos
                item_local.url = scrapertools.find_single_match(item_local.channel_host, '(\w+:)//') + item_local.url
            item_local.thumbnail = urlparse.urljoin(host, scrapedthumbnail)
            if not item_local.thumbnail.startswith("http"):                     #Si le falta el http.: lo ponemos
                item_local.thumbnail = scrapertools.find_single_match(item_local.channel_host, \
                        '(\w+:)//') + item_local.thumbnail
            item_local.contentThumbnail = item_local.thumbnail

            """Si son episodios sueltos de Series que vienen de Novedades, se busca la url de la Serie"""
            pattern = '<div\s*class="content.*?">.*?<h1.*?>.*?<a\s*href="([^"]+)"'  #Patron para Serie completa
            pattern_al = '\/temp.*?-(\d+)-?\/cap.*?-(\d+(?:-al-\d+)?)-?(?:\/|$)'
            if item.extra == "novedades" and "/serie" in url and 'serie-1080p' not in url and 'serie-4k' not in url and episodio_serie == 1:
                item_local.url = url
                item_local.extra2 = 'serie_episodios'                           #Creamos acción temporal excluyente para otros clones
                headers = {'referer': item.url}

                data_serie, response, item, itemlist = generictools.downloadpage(item_local.url, timeout=timeout, post=post, CF_test=CF_test, 
                                                                                 s2=True, headers=headers, no_comments=False, 
                                                                                 decode_code=decode_code, quote_rep=True, 
                                                                                 item=item, itemlist=itemlist, alfa_s=alfa_s)

                if not data_serie or (not scrapertools.find_single_match(data_serie, pattern) \
                                and not search3 in data):
                    logger.error("ERROR 01: LISTADO_BUSQUEDA: La Web no responde o ha cambiado de URL: " 
                                + item_local.url + " / DATA: " + data_serie)
                    #Si no hay datos consistentes, llamamos al método de fail_over para que encuentre un canal que esté activo y pueda gestionar el cambio de episodio por serie
                    item_local, data_serie = generictools.fail_over_newpct1(item_local, \
                                pattern, timeout=timeout)
                
                if not data_serie:                                              #Si no ha logrado encontrar nada, salimos
                    title_subs += ["ERR"]
                    
                elif item_local.channel_alt:                                    #Si ha habido fail-over, lo comento
                    url = url.replace(item_local.channel_alt, item_local.category.lower())
                    title_subs += ["ALT"]

                try:
                    item_local.url = urlparse.urljoin(host, scrapertools.find_single_match(data_serie, pattern))
                    #Son series VO mal formadas?
                    if (item.post and '775' in item.post and 'vo/' not in item_local.url) or 'vo/' in url:      
                        item_local.url = item_local.url.replace('/series/', '/series-vo/')
                        
                    #Son series HD formada como series estándar?
                    #if (scrapertools.find_single_match(item_local.quality, '\d{3, 4}p')) and '/series/' in item_local.url:
                    if 'hd/' in url:
                        item_local.url = item_local.url.replace('/series/', '/series-hd/')
                        
                    #item_local.url = re.sub(r'\/\d+$', '/', item_local.url)        #Quitamos el ID de la serie por compatib.
                    if item_local.url:
                        title_subs += ["Episodio %sx%s" % (scrapertools.find_single_match(url, pattern_al))]
                        url = item_local.url
                except:
                    logger.error(traceback.format_exc())
                    
                #logger.debug(item_local.url)
                
            if item.extra == "novedades" and "/serie" in url:
                if not item_local.url or episodio_serie == 0 or 'serie-1080p' in url or 'serie-4k' in url:
                    item_local.url = url
                    if scrapertools.find_single_match(url, pattern_al):
                        title_subs += ["Episodio %sx%s" % (scrapertools.find_single_match(url, pattern_al))]
                    else:
                        title_subs += ["Episodio 1x01"]

            
            #Establecemos los valores básicos en función del tipo de contenido
            if (item_local.extra == "series" or ".com/serie" in url or "/serie" in url or "-serie" in url) \
                             and not "/miniseries" in url and not "/capitulo" in url \
                             and 'serie-1080p' not in url and 'serie-4k' not in url :           #Series
                item_local.action = "episodios"
                item_local.contentType = "tvshow"
                item_local.season_colapse = True
                item_local.extra = "series"
            elif item_local.extra == "varios" or "varios/" in url or "/miniseries" in url:      #Documentales y varios
                item_local.action = "findvideos"
                item_local.contentType = "movie"
                item_local.extra = "varios"
            elif "/capitulo" in url and not "/miniseries"in url and ('serie-1080p' in url or 'serie-4k' in url):    #Documentales y varios
                item_local.action = "findvideos"
                item_local.contentType = "episode"
                item_local.extra = "series"
            else:                                                                               #Películas
                item_local.action = "findvideos"
                item_local.contentType = "movie"
                item_local.extra = "peliculas"
                size = size.replace(".", ",")
                if size:
                    item_local.quality = '%s [%s]' % (item_local.quality, size)

            #Determinamos y marcamos idiomas
            item_local.language = []
            if "[vos" in title.lower() or "v.o.s" in title.lower() or "v.o" in title.lower() \
                        or "subs" in title.lower() or "-vo/" in scrapedurl or "vos" in \
                        calidad.lower() or "vose" in calidad.lower() or "v.o.s" in calidad.lower() \
                        or "sub" in calidad.lower() or "-vo/" in item.url:
                item_local.language += ["VOS"]                                  # VOS
            if "latino" in title.lower() or "argentina" in title.lower() or "-latino/" in \
                        scrapedurl or "latino" in calidad.lower() or "argentina" in calidad.lower() \
                        or "latino" in item.url:
                item_local.language += ["LAT"]                                  # LAT
            if "[dual" in title.lower() or "multileng" in title.lower() or "multileng" \
                        in item_local.quality.lower() or (("espa" in title.lower() or \
                        "spani" in title.lower()) and "VOS" in item_local.language):
                title = re.sub(r'\[[D|d]ual.*?\]', '', title)
                title = re.sub(r'\[[M|m]ultileng.*?\]', '', title)
                item_local.quality = re.sub(r'\[[M|m]ultileng.*?\]', '', item_local.quality)
                item_local.language[0:0] = ["DUAL"]                             # DUAL
            if "VOS" in item_local.language and "DUAL" not in item_local.language and \
                        ("[sp" in item_local.quality.lower() or "espa" in item_local.quality.lower() \
                        or "cast" in item_local.quality.lower() or "spani" in item_local.quality.lower()):
                item_local.language[0:0] = ["DUAL"]                             # DUAL 
            if ("[es-" in item_local.quality.lower() or (("cast" in item_local.quality.lower() \
                        or "espa" in item_local.quality.lower() or "spani" in \
                        item_local.quality.lower()) and ("eng" in item_local.quality.lower() \
                        or "ing" in item_local.quality.lower()))) and "DUAL" not in \
                        item_local.language:
                item_local.language[0:0] = ["DUAL"]                             # DUAL
            if not item_local.language:
                item_local.language = ["CAST"]                                  # Si no hay otro idioma, ponero CAST por defecto
            
            #Guardamos info de 3D en calidad y limpiamos
            if "3d" in title.lower():
                if not "3d" in item_local.quality.lower():
                    item_local.quality = item_local.quality + " 3D"
                calidad3D = scrapertools.find_single_match(title, r'(?i)3d\s*(?:h-*\s*sbs\s|sbs\s|hou\s*|aa\s*|ou\s*)?\s*').strip()
                if calidad3D:
                    item_local.quality = item_local.quality.replace("3D", calidad3D)
                title = re.sub(r'(?i)3d\s*(?:h-*\s*sbs\s|sbs\s|hou\s*|aa\s*|ou\s*)?\s*', '', title)
            if "imax" in title.lower():
                item_local.quality = item_local.quality + " IMAX"
                title = re.sub(r'(?i)(?:version)?\s*imax', '', title)
            if "2d" in title.lower():
                title = re.sub(r'(?i)\s*.2d.', '', title)
                title_subs += ["[2D]"]
            if "HDR" in title:
                title = title.replace(" HDR", "")
                if not "HDR" in item_local.quality:
                    item_local.quality += " HDR"    

            #Terminamos de preparar la calidad
            item_local.quality = re.sub(r'(?i)\[es-\w+]|[\s|-]caste\w+|[\s|-]espa\w+|[\s|-|\[]spani\w+|[\s|-].ngl\w+', '', item_local.quality)
            item_local.quality = re.sub(r'(?i)proper|unrated|directors|cut|repack|internal|real|gratis', '', item_local.quality)
            item_local.quality = re.sub(r'(?i)extended|masted|docu|super|duper|amzn|uncensored|hulu', '', item_local.quality)
            item_local.quality = re.sub(r'(?i)[\s|-]latino\s*|[\+|-]*subs|vose\s*|vos\s*', '', item_local.quality)
            item_local.quality = re.sub(r'(?i)\[\d{4}\]\s*|\[cap.*?\]\s*|\s*cap\w*\s*|\[docu.*?\]\s*|\[\s*|\]\s*', '', item_local.quality)
            item_local.quality = item_local.quality.replace("ALTA DEFINICION", "HDTV").strip()
            
            #Eliminamos Temporada de Series, solo nos interesa la serie completa
            if ("temp" in title.lower() or "cap" in title.lower()) and item_local.contentType != "movie":
                title = re.sub(r'(?i)(?:-*\s*temp\w*\.*\s*\d+\s*)?(?:cap\w*\.*\s*\d+\s*)?(?:al|Al|y)\s*\d+', '', title)
                title = re.sub(r'(?i)-*\s*temp\w*\.*\s*\d+(?:x\d+)?', '', title)
                title = re.sub(r'(?i)-*\s*cap.*?\d+(?:\s*al\s*\d+)?', '', title)
            if "audio" in title.lower():                                        #Reservamos info de audio para después de TMDB
                title_subs += ['[%s]' % scrapertools.find_single_match(title, r'(\[[a|A]udio.*?\])')]
                title = re.sub(r'\[[a|A]udio.*?\]', '', title)
            if "duolog" in title.lower() or "trilog" in title.lower() or "saga" in title.lower():
                title_subs += ["[Saga]"]
                title = re.sub(r'(?i)duolog\w*|trilog\w*|\s*saga\s*.ompleta|\s*saga', '', title)
            if scrapertools.find_single_match(title, r'(?i)version\s*ext\w*|\(version\s*ext\w*\)|v.\s*ext\w*|V\.E\.'):
                title_subs += ["[V. Extendida]"]
                title = re.sub(r'(?i)version\s*ext\w*|\(version\s*ext\w*\)|v.\s*ext\w*|V\.E\.', '', title)
            if "colecc" in title.lower() or "completa" in title.lower():
                title = re.sub(r'(?i)\s*colecci..|\s*completa', '', title)
            if scrapertools.find_single_match(title, r'(- [m|M].*?serie ?\w+)'):
                title = re.sub(r'(?i)-*\s*m.*?serie\s*\w*', '', title)
                title_subs += ["[Miniserie]"]

            #Limpiamos restos en título
            title = re.sub(r'(?i)castellano|español|ingl.s\s*|english\s*|calidad|de\s*la\s*serie|spanish|Descarga\w*\s*\w+\-\w+', '', title)
            title = re.sub(r'(?i)ver\s*online\s*(?:serie\s*)|descarga.*\s*Serie\s*(?:hd\s*)?|ver\s*en\s*linea\s*|v.o.\s*|cvcd\s*', '', title)
            title = re.sub(r'(?i)en\s*(?:Full\s*)?HD\s*|microhd\s*|hdtv\s*|\(proper\)\s*|ratdvd\s*|dvdrip\s*|dvd.*\s*|dvbrip\s*', '', title)
            title = re.sub(r'(?i)ESDLA\s*|dvb\s*|descarga\w*\s*|torrent\s*|gratis\s*|estreno\w*\s*', '', title)
            title = re.sub(r'(?i)(?:la\s*)?pelicula\w*\s*en\s*latino\s*|(?:la\s*)?pelicula\w*\s*|descarga\w*\s*todas\s*', '', title)
            title = re.sub(r'(?i)bajar\s*|hdrip\s*|rip\s*|xvid\s*|ac3\s*5\.1\s*|ac3\s*|1080p\s*|720p\s*|dvd-screener\s*', '', title)
            title = re.sub(r'(?i)ts-screener\s*|screener\s*|bdremux\s*|4k\s*uhdrip\s*|full\s*uhd4k\s*|4kultra\s*|2cd\s*', '', title)
            title = re.sub(r'(?i)fullbluray\s*|en\s*bluray\s*|bluray\s*en\s*|bluray\s*|bonus\s*disc\s*|de\s*cine\s*', '', title)
            title = re.sub(r'(?i)telecine\s*|argentina\s*|\+\+sub\w+\s*|\+-\+sub\w+\s*|directors\s*cut\s*|\s*en\s*hd', '', title)
            title = re.sub(r'(?i)subs.\s*integrados\s*|subtitulos\s*|blurayrip(?:\])?|descarga\w*\s*otras\s*|\(comple.*?\)', '', title).strip()
            title = re.sub(r'(?i)resubida|montaje\s*del\s*director|-*v.cine\s*|x264\s*|mkv\s*|sub\w*\s*|remaste\w+|sw\s*', '', title).strip()
            title = title.replace("a?o", 'año').replace("a?O", 'año').replace("A?o", 'Año')\
                    .replace("A?O", 'Año').strip()
            title = title.replace("(", "-").replace(")", "-").replace(".", " ").strip()
            if "en espa" in title: title = title[:-11]
            
            # Salvamos info de episodio
            if (item.extra == 'series' or item.extra == 'documentales') and item.extra2 == 'novedades': # Series, Docs desde Novedades
                title_subs += [scrapertools.find_single_match(title, patron)]

            #Guardamos el año que puede venir en el título, por si luego no hay resultados desde TMDB
            if scrapertools.find_single_match(title, r'\s+[\[|\(|-]*(\d{4})[\]|\)|-]*\s*'):
                year = int(scrapertools.find_single_match(title, r'\s+[\[|\(|-]*(\d{4})[\]|\)|-]*\s*'))
                if title != str(year):
                    title = re.sub(r'\s+[\[|\(|-]*(\d{4})[\]|\)|-]*\s*', '', title)
                else:
                    year = ''
            else:
                year = ''
            if year and year >= 1900 and year <= 2040:
                item_local.infoLabels['year'] = year
            else:
                item_local.infoLabels['year'] = '-'

            # Normalizamos títulos
            if item_local.contentType == "tvshow":
                title = scrapertools.find_single_match(title, '(^.*?)(?:$|\s+\(|\s+\[|\s+-)')
            if not title:
                title = "SIN TITULO"
            title = re.sub(r'(?:-\s*)?ES\s*|\(4k\)\s*|\[4k\]\s*|\(|\)|\[|\]|BR\s*|[\(|\[]\s+[\)|\]]|\(\)\s*|\[\]\s*|\+\s*', '', title)
            title = re.sub(r'\s*-\s*', ' ', title)
            item_local.from_title = title.strip().lower().title()               #Guardamos esta etiqueta para posible desambiguación de título
            item_local.title = title.strip().lower().title()

            #Salvamos el título según el tipo de contenido
            if item_local.contentType == "movie":
                item_local.contentTitle = item_local.title
            else:
                item_local.contentSerieName = item_local.title

            #Guarda la variable temporal que almacena la info adicional del título a ser restaurada después de TMDB
            item_local.title_subs = title_subs

            #Ahora se filtra por idioma, si procede, y se pinta lo que vale.  Excluye categorías en otros idiomas.
            if filter_languages > 0 and item.extra2 != 'categorias':
                itemlist = filtertools.get_link(itemlist, item_local, list_language)
            else:
                itemlist.append(item_local.clone())                             #Si no, pintar pantalla
            
            cnt_title = len(itemlist)                                           # Recalculamos los items después del filtrado
            if cnt_title >= cnt_tot and (len(matches) - cnt_match) + cnt_title > cnt_tot * 1.3:     #Contador de líneas añadidas
                break
            
            #logger.debug(item_local)
    
        matches = matches[cnt_match:]                                           # Salvamos la entradas no procesadas
        cnt_tot_match += cnt_match                                              # Calcular el num. total de items mostrados
    
    #Pasamos a TMDB la lista completa Itemlist
    tmdb.set_infoLabels(itemlist, __modo_grafico__, idioma_busqueda=idioma_busqueda)
    
    #Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
    item, itemlist = generictools.post_tmdb_listado(item, itemlist)

    # Si es necesario añadir paginacion
    if curr_page <= last_page or len(matches) > 0:
        curr_page_print = int(cnt_tot_match / float(cnt_tot))
        if curr_page_print < 1:
            curr_page_print = 1
        if last_page:
            if last_page > 1:
                last_page_print = int((last_page * page_factor) + 0.999999)
            title = '%s de %s' % (curr_page_print, last_page_print)
        else:
            title = '%s' % curr_page_print

        itemlist.append(Item(channel=item.channel, action="listado", title=">> Página siguiente " 
                        + title, title_lista=title_lista, url=next_page_url, extra=item.extra, 
                        extra2=item.extra2, last_page=str(last_page), curr_page=str(curr_page), 
                        page_factor=str(page_factor), cnt_tot_match=str(cnt_tot_match), matches=matches, 
                        last_page_print=last_page_print, post=post))

    return itemlist

    
def findvideos(item, retry=False):
    logger.info()
    
    itemlist = []
    itemlist_t = []                                                             #Itemlist total de enlaces
    itemlist_f = []                                                             #Itemlist de enlaces filtrados
    matches = []
    data = ''
    code = 0
    timeout_search = timeout * 2                                                # Timeout para descargas
    if not item.language:
        item.language = ['CAST']                                                #Castellano por defecto
    
    torrent_params = {
                      'url': item.url,
                      'torrents_path': None, 
                      'local_torr': item.torrents_path, 
                      'torrent_alt': '', 
                      'lookup': True, 
                      'force': False, 
                      'data_torrent': True, 
                      'subtitles': True, 
                      'file_list': True, 
                      'find_alt_link_option': find_alt_link_option, 
                      'find_alt_link_result': [], 
                      'size': ''
                      }
    
    #logger.debug(item)
    
    global host, sufix
    item, host = verify_host(item, host)                                        # Actualizamos la url del host
    sufix_save = sufix
    if channel_clone_name == "*** DOWN ***":                                    #Ningún clones activo !!!
        itemlist.append(item.clone(action='', title="[COLOR yellow]Ningún canal NewPct1 activo[/COLOR]"))    
        return itemlist 
    
    # Cualquiera de las tres opciones son válidas
    # item.url = item.url.replace(".com/",".com/ver-online/")
    # item.url = item.url.replace(".com/",".com/descarga-directa/")
    item.url = item.url.replace("descarga-torrent/descargar/", download_sufix)
    if not download_sufix in item.url:
        item.url = item.url.replace(sufix+"descargar/", sufix+download_sufix)
    torrent_tag = item.channel_host + download_sufix
    
    
    """ Función para limitar la verificación de enlaces de Servidores para Ver online y Descargas """
    #Inicializamos las variables por si hay un error en medio del proceso
    channel_exclude = []
    ver_enlaces = []
    ver_enlaces_veronline = -1                                                  #Ver todos los enlaces Ver Online
    verificar_enlaces_veronline = -1                                            #Verificar todos los enlaces Ver Online
    verificar_enlaces_veronline_validos = True                                  #"¿Contar sólo enlaces 'verificados' en Ver Online?"
    excluir_enlaces_veronline = []                                              #Lista vacía de servidores excluidos en Ver Online
    ver_enlaces_descargas = 0                                                   #Ver todos los enlaces Descargar
    verificar_enlaces_descargas = -1                                            #Verificar todos los enlaces Descargar
    verificar_enlaces_descargas_validos = True                                  #"¿Contar sólo enlaces 'verificados' en Descargar?"
    excluir_enlaces_descargas = []                                              #Lista vacía de servidores excluidos en Descargar
    
    if not item.videolibray_emergency_urls:                                     #Si es un proceso nomal...
        try:
            #Leemos las opciones de permitir Servidores para Ver Online y Descargas
            #Cargamos en .json del canal para ver las listas de valores en  settings
            channel_exclude = channeltools.get_channel_json(item.channel)
            for settings in channel_exclude['settings']:                        #Se recorren todos los settings
                if settings['id'] == "clonenewpct1_excluir1_enlaces_veronline": #lista de enlaces a excluir
                    max_excl = int(settings['max_excl'])                        #Máximo número de servidores excluidos
                    channel_exclude = settings['lvalues']                       #Cargamos la lista de servidores
                if settings['id'] == "clonenewpct1_ver_enlaces_descargas":      #Número de enlances a ver o verificar
                    ver_enlaces = settings['lvalues']                           #Cargamos la lista de num. de enlaces
        
            #Primer loop para enlaces de Ver Online.  
            #Carga la variable de ver
            ver_enlaces_veronline = int(config.get_setting("clonenewpct1_ver_enlaces_veronline", item.channel))
            if ver_enlaces_veronline == 1:                                      #a "Todos" le damos valor -1.  Para "No" dejamos 0
                ver_enlaces_veronline = -1
            if ver_enlaces_veronline > 1:                                       #para los demás valores, tomamos los de la lista
                ver_enlaces_veronline = int(ver_enlaces[ver_enlaces_veronline])
        
            #Carga la variable de verificar
            verificar_enlaces_veronline = int(config.get_setting("clonenewpct1_verificar_enlaces_veronline", item.channel))
            if verificar_enlaces_veronline == 1:                                #a "Todos" le damos valor -1.  Para "No" dejamos 0
                verificar_enlaces_veronline = -1
            if verificar_enlaces_veronline > 1:                                 #para los demás valores, tomamos los de la lista
                verificar_enlaces_veronline = int(ver_enlaces[verificar_enlaces_veronline])

            #Carga la variable de contar sólo los servidores verificados
            verificar_enlaces_veronline_validos = int(config.get_setting\
                    ("clonenewpct1_verificar_enlaces_veronline_validos", item.channel))

            #Carga la variable de lista de servidores excluidos
            x = 1
            for x in range(1, max_excl+1):                                      #recorremos todas las opciones de canales exluidos
                valor = str(config.get_setting("clonenewpct1_excluir%s_enlaces_veronline" % x, item.channel))
                valor = int(valor)
                if valor > 0:                                                   #Evitamos "No"
                    excluir_enlaces_veronline += [channel_exclude[valor]]       #Añadimos el nombre de servidor excluido a la lista
                x += 1

            #Segundo loop para enlaces de Descargar.  
            #Carga la variable de ver
            ver_enlaces_descargas = int(config.get_setting("clonenewpct1_ver_enlaces_descargas", item.channel))
            if ver_enlaces_descargas == 1:                                      #a "Todos" le damos valor -1.  Para "No" dejamos 0
                ver_enlaces_descargas = -1
            if ver_enlaces_descargas > 1:                                       #para los demás valores, tomamos los de la lista
                ver_enlaces_descargas = int(ver_enlaces[ver_enlaces_descargas])
        
            #Carga la variable de verificar
            verificar_enlaces_descargas = int(config.get_setting\
                    ("clonenewpct1_verificar_enlaces_descargas", item.channel))
            if verificar_enlaces_descargas == 1:                                #a "Todos" le damos valor -1.  Para "No" dejamos 0
                verificar_enlaces_descargas = -1
            if verificar_enlaces_descargas > 1:                                 #para los demás valores, tomamos los de la lista
                verificar_enlaces_descargas = int(ver_enlaces[verificar_enlaces_descargas])

            #Carga la variable de contar sólo los servidores verificados
            verificar_enlaces_descargas_validos = int(config.get_setting\
                    ("clonenewpct1_verificar_enlaces_descargas_validos", item.channel))

            #Carga la variable de lista de servidores excluidos
            x = 1
            for x in range(1, max_excl+1):                                      #recorremos todas las opciones de canales exluidos
                valor = str(config.get_setting("clonenewpct1_excluir%s_enlaces_descargas" % x, item.channel))
                valor = int(valor)
                if valor > 0:                                                   #Evitamos "No"
                    excluir_enlaces_descargas += [channel_exclude[valor]]       #Añadimos el nombre de servidor excluido a la lista
                x += 1

        except Exception as ex:                                                 #En caso de error, lo mostramos y reseteamos todas las variables
            logger.error("Error en la lectura de parámentros del .json del canal: " 
                    + item.channel + " \n%s" % ex)
            #Mostrar los errores
            logger.error(ver_enlaces_veronline)
            logger.error(verificar_enlaces_veronline)
            logger.error(verificar_enlaces_veronline_validos)
            logger.error(excluir_enlaces_veronline)
            logger.error(ver_enlaces_descargas)
            logger.error(verificar_enlaces_descargas)
            logger.error(verificar_enlaces_descargas_validos)
            logger.error(excluir_enlaces_descargas)

    
    """ Descarga la página """
    data_servidores = ''
    enlaces_ver = []
    url_servidores = item.url
    url_torr_save = item.url
    category_servidores = item.category
    data_servidores_stat = False
    size = ''
    headers = {'referer': host}
    printed_CF = False
    find_alt = False
    find_alt_id = 'Digg'
    canonical['retries_cloudflare'] = 1
    
    if not item.matches:
        data, response, item, itemlist_alt = generictools.downloadpage(item.url, timeout=timeout_search, quote_rep=True, CF_test=CF_test, 
                                                                       decode_code=decode_code, canonical=canonical, 
                                                                       headers=headers, item=item, itemlist=[])     # Descargamos la página)
        data = data.replace("$!", "#!").replace("Ã±", "ñ").replace("//pictures", "/pictures")
        data_servidores = data                                                  #salvamos data para verificar servidores, si es necesario

        # Verificamos si ha cambiado el Host
        if response.host:
            global domain, clone_list
            sufix = scrapertools.find_single_match(response.host, '\.\w+\/*$')
            domain = scrapertools.find_single_match(response.host, patron_domain)
            url_servidores = item.url
            headers = {'referer': host}
            clone_list[0][2] = host
            return findvideos(item)

    """ Procesamos los datos de las páginas """
    #Patron para .torrent
    patron = 'window.location.href = (?:parseURL\()?"(.*?)"\)?;'
    patron_mult = 'torrent:check:status|' + patron + '|<a href="([^"]+)"\s?title='
    patron_mult += '"[^"]+"\s?class="btn-torrent"'
    # Patrón para Servidores
    patron_lu = '<div class=\"box1\"[^<]+<img src=\"([^<]+)?" style[^<]+><\/div'
    patron_lu += '[^<]+<div class="box2">([^<]+)?<\/div[^<]+<div class="box3">([^<]+)?'
    patron_lu += '<\/div[^<]+<div class="box4">([^<]+)?<\/div[^<]+<div class="box5">'
    patron_lu += '<a href=(.*?)? rel.*?<\/div[^<]+<div class="box6">([^<]+)?<'
    
    if not scrapertools.find_single_match(data, patron):
        patron = '<\s*script\s*type="text\/javascript"\s*>\s*var\s*[lt\s*=\s*"[^"]*"'       #Patron .torrent
        patron += '(?:,\s*idlt\s*=\s*"[^"]*")?,\s*nalt\s*=\s*"([^"]+)"'                     #descargas2020
        if not scrapertools.find_single_match(data, patron):
            patron = '<a\s*href="javascript:;"\s*onclick="if\s*\(!window.__cfRLUnblockHandlers\)'
            patron += '\s*return\s*false;\s*post\([^\{]+{name:\s*"([^"]+).torrent"}\);"'    #Patron .torrent Pctnew
            if not scrapertools.find_single_match(data, patron):
                patron = '<a href="([^"]+)"\s?title="[^"]+"\s?class="btn-torrent"'          #Patron .torrent (planetatorrent)
    
    # Salvamos el enlace .torrent
    url_torr = scrapertools.find_single_match(data, patron).replace('javascript:;', '').strip()
    if url_torr:
        url_torr = urlparse.urljoin(torrent_tag, scrapertools.find_single_match(data, patron))
    else:
        url_torr = DUMMY
        data = DUMMY
    url_torr_save = url_torr
    torrent_params['force'] = True
    url_torr, headers = find_torrent_link(url_torr, 0, item=item, headers=headers, torrent_params=torrent_params, patron=patron)
    if url_torr_save == DUMMY and url_torr and url_torr != DUMMY: url_torr_save = url_torr
    size = torrent_params['size']
    if find_alt_id in size: find_alt = True
    if torrent_params['torrent_alt']:
        item.armagedon = True                                                   # Forzamos el uso de los torrents cacheados en la videoteca
    
    # Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if (not data and not item.matches) or 'javascript:;' in url_torr:           # Si no hay datos o url, error
        size = ''
        if 'Archivo torrent no Existe' in data:
            logger.error("ERROR 09: FINDVIDEOS: Archivo torrent no Existe ")
        else:
            logger.error("ERROR 02: FINDVIDEOS: Ha cambiado la estructura de la Web " 
                        + " / PATRON: " + patron + " / DATA: ")                 # + str(data)
        if item.emergency_urls and not item.videolibray_emergency_urls:         #Hay urls de emergencia?
            url_torr = item.emergency_urls[0][0]                                #Restauramos la url
            if len(item.emergency_urls) > 1 and item.emergency_urls[1]:
                matches = item.emergency_urls[1]                                #Restauramos matches de vídeos
            item.armagedon = True                                               #Marcamos la situación como catastrófica
            data = 'xyz123'                                                     #Para que no haga más preguntas
        else:
            #Si no hay datos consistentes, llamamos al método de fail_over para que 
            #encuentre un canal que esté activo y pueda gestionar el vídeo
            item, data = generictools.fail_over_newpct1(item, patron_mult, timeout=timeout_search)
            data = data.replace("$!", "#!").replace("'", '"').replace("Ã±", "ñ").replace("//pictures", "/pictures")
            
            #Volvemos a buscar el .torrent, repitiendo todo como al principio
            patron = 'window.location.href = (?:parseURL\()?"(.*?)"\)?;'
            if not scrapertools.find_single_match(data, patron):
                patron = '<\s*script\s*type="text\/javascript"\s*>\s*var\s*[lt\s*=\s*"[^"]*"'       #Patron .torrent
                patron += '(?:,\s*idlt\s*=\s*"[^"]*")?,\s*nalt\s*=\s*"([^"]+)"'                     #descargas2020
                if not scrapertools.find_single_match(data, patron):
                    patron = '<a\s*href="javascript:;"\s*onclick="if\s*\(!window.__cfRLUnblockHandlers\)'
                    patron += '\s*return\s*false;\s*post\([^\{]+{name:\s*"([^"]+).torrent"}\);"'    #Patron .torrent Pctnew
                    if not scrapertools.find_single_match(data, patron):
                        patron = '<a href="([^"]+)"\s?title="[^"]+"\s?class="btn-torrent"'          #Patron .torrent (planetatorrent)
            
            if 'Archivo torrent no Existe' in data:
                url_torr = ''
            else:
                url_torr = scrapertools.find_single_match(data, patron).replace('javascript:;', '').strip()
            if url_torr:
                url_torr = urlparse.urljoin(torrent_tag, scrapertools.find_single_match(data, patron))
            elif 'Archivo torrent no Existe' in data:
                logger.error("ERROR 09: FINDVIDEOS: Archivo torrent no Existe ")
            else:
                logger.error("ERROR 02: FINDVIDEOS: Ha cambiado la estructura de la Web " 
                        + " / PATRON: " + patron + " / DATA: ")                 # + str(data)
            if url_torr:
                torrent_params['force'] = False
                torrent_params['torrent_alt'] = ''
                url_torr, headers = find_torrent_link(url_torr, 0, item=item, headers=headers, torrent_params=torrent_params, patron=patron)
                size = torrent_params['size']
                if find_alt_id in size: find_alt = True
                if torrent_params['torrents_path']: item.torrents_path = torrent_params['torrents_path']

    #Si no ha logrado encontrar nada, verificamos si hay servidores
    if not data and not matches:
        cnt_servidores = 0
        item.category = category_servidores                                     #restauramos valores originales
        item.url = url_servidores
        
        # Lookup: Sistema de scrapeo de servidores creado para Torrentlocula, compatible con otros clones de Newpct1
        enlaces_ver = re.compile(patron_lu, re.DOTALL).findall(data_servidores)
        enlaces_descargar = enlaces_ver
        
        for logo, servidor, idioma, calidad, enlace, title in enlaces_ver:      #buscamos enlaces de servidores de ver-online
            if ver_enlaces_veronline == 0:                                      #Si no se quiere Ver Online, se sale del bloque
                break
            if "ver" in title.lower():
                cnt_servidores += 1

        if cnt_servidores == 0:
            item, data_servidores = generictools.fail_over_newpct1(item, patron_lu, timeout=timeout_search)    #intentamos recuperar servidores
            
            #Miramos si ha servidores
            if not data_servidores:                                             #Si no ha logrado encontrar nada nos vamos
                itemlist.append(item.clone(action='', title="[COLOR yellow]" + 
                        item.channel.capitalize() + '[/COLOR]: Ningún canal NewPct1 activo', 
                        folder=False))    
                itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 01: FINDVIDEOS:.  La Web no responde o la URL es erronea. ' 
                        + 'Si la Web está activa, reportar el error con el log', 
                        folder=False))
                if item.videolibray_emergency_urls:
                    return item
                else:
                    return itemlist                                             #si no hay más datos, algo no funciona, pintamos lo que tenemos
        
        data = data_servidores                                                  #restauramos los datos
        data = data.replace("$!", "#!").replace("'", '"').replace("Ã±", "ñ").replace("//pictures", "/pictures")
        data_servidores_stat = True                                             #Marcamos como que los hemos usado
    
    if not item.armagedon:
        if item.matches:
            matches = item.matches
            del item.matches

    #logger.debug("PATRON: " + patron)
    #logger.debug(matches)
    #logger.debug(data)

    #Si es un lookup para cargar las urls de emergencia en la Videoteca, lo iniciamos
    if item.videolibray_emergency_urls:
        if item.channel_host: del item.channel_host
        item.emergency_urls = []                                                # Iniciamos emergency_urls
        item.emergency_urls.append([])                                          # Reservamos el espacio para los .torrents locales
        item.emergency_urls.append([])                                          # Reservamos el espacio para los enlaces directos
        item.emergency_urls.append([])                                          # Reservamos para uso urls y magnets punteros a los torrents locales
        item.emergency_urls.append([])                                          # Reservamos para uso los torrent_info de los magnets
        
    item.quality = re.sub(r'(?i)\s*\d+(?:.\d+)?\s*(?:gb|mb)', '', item.quality)    # Quitamos el tamaño que viene de Search
    
    #Llamamos al método para crear el título general del vídeo, con toda la información obtenida de TMDB
    if not item.videolibray_emergency_urls:
        item, itemlist = generictools.post_tmdb_findvideos(item, itemlist, headers=headers)

    """ Tratamos los enlaces .torrent de calidades alternativas """
    matches_torrent = []
    if item.armagedon:
        for x, url in enumerate(item.emergency_urls[0]):
            sz = ''
            qt = item.quality
            if x > 0 and len(item.emergency_urls) > 3 and len(item.emergency_urls[3]) >= x+1:
                info = item.emergency_urls[3][x]
                qt = scrapertools.find_single_match(info, '^#([^#]+)#')
                if not qt: qt = item.quality
                sz = re.sub('^#[^#]+#', '', info)
            matches_torrent.append((url, url, url, [], qt, sz, ''))
                
    elif url_torr:
        matches_torrent.append((url_torr, url_torr_save, torrent_params['torrents_path'], 
                        torrent_params['find_alt_link_result'], item.quality, size, data))

    if not item.armagedon and item.url_quality_alt:
        for x, (url, quality) in enumerate(item.url_quality_alt):
            url_torr = url
            size = ''

            if not url_torr.startswith('magnet'):
                if not download_sufix in url_torr:
                    url_torr = url_torr.replace(sufix+"descargar/", sufix+download_sufix)
                if url_torr.startswith('http') or url_torr.startswith('//'):
                    url_torr = urlparse.urljoin(torrent_tag, url_torr)
                
                data_alt, response, item, itemlist_alt = generictools.downloadpage(url_torr, timeout=timeout_search, quote_rep=True, 
                                                                                   decode_code=decode_code, headers=headers, 
                                                                                   item=item, itemlist=[], CF_test=CF_test)
                data_alt = data_alt.replace("$!", "#!").replace("Ã±", "ñ").replace("//pictures", "/pictures")
                
                #Volvemos a buscar el .torrent, repitiendo todo como al principio
                patron = 'window.location.href = (?:parseURL\()?"(.*?)"\)?;'
                if not scrapertools.find_single_match(data_alt, patron):
                    patron = '<\s*script\s*type="text\/javascript"\s*>\s*var\s*[lt\s*=\s*"[^"]*"'       #Patron .torrent
                    patron += '(?:,\s*idlt\s*=\s*"[^"]*")?,\s*nalt\s*=\s*"([^"]+)"'                     #descargas2020
                    if not scrapertools.find_single_match(data_alt, patron):
                        patron = '<a\s*href="javascript:;"\s*onclick="if\s*\(!window.__cfRLUnblockHandlers\)'
                        patron += '\s*return\s*false;\s*post\([^\{]+{name:\s*"([^"]+).torrent"}\);"'    #Patron .torrent Pctnew
                        if not scrapertools.find_single_match(data_alt, patron):
                            patron = '<a href="([^"]+)"\s?title="[^"]+"\s?class="btn-torrent"'          #Patron .torrent (planetatorrent)
                
                if 'Archivo torrent no Existe' in data_alt:
                    url_torr = ''
                else:
                    url_torr = scrapertools.find_single_match(data_alt, patron).replace('javascript:;', '').strip()
                if not url_torr:
                    url_torr = DUMMY
                else:
                    url_torr = urlparse.urljoin(torrent_tag, url_torr)

                url_torr_save = url_torr
                torrent_params['force'] = False
                torrent_params['quality_alt'] = quality if item.contentType != 'movie' else 'rip 720p 1080p 4kwebrip 4k'
                url_torr, headers = find_torrent_link(url_torr, x+1, item=item, headers=headers, torrent_params=torrent_params, patron=patron)
                size = torrent_params['size']
                if find_alt_id in size: find_alt = True
            
            matches_torrent.append((url_torr, url_torr_save, torrent_params['torrents_path'], 
                        torrent_params['find_alt_link_result'], quality, size, data_alt))
    
    if matches_torrent:
        item.matches_torrent = []
        for url, url_save, torrents_path, find_alt_link_result, quality, _size, _data in matches_torrent:
            item.matches_torrent += [url_save]
        from servers.torrent import videolibray_populate_cached_torrents
        cached_torrents = videolibray_populate_cached_torrents(item.matches_torrent[0], find=True, item=item)
        if cached_torrents['updated']:
            del item.matches_torrent
            if item.armagedon and not retry:
                return findvideos(item, retry=True)
    
    """ Ahora tratamos los enlaces .torrent """
    for x, (url, url_save, torrents_path, find_alt_link_result, quality, _size, _data) in enumerate(matches_torrent):
        url_torr = url
        size = _size
        data = _data
        
        if (url_torr.startswith('http') or url_torr.startswith('//')) and torrent_params['torrents_path'] != 'CF_BLOCKED':
            url_torr = generictools.convert_url_base64(url_torr, host)
        else:
            url_torr = generictools.convert_url_base64(url_torr)
        
        #Generamos una copia de Item para trabajar sobre ella
        item_local = item.clone()

        item_local.url = url_torr
        if torrents_path: 
            item_local.torrents_path = torrents_path
        else:
            item_local.torrents_path = ''
        if item.armagedon and x > 0:
            item_local.torrent_alt = ''
            torrent_params['torrent_alt'] = ''

        # Restauramos urls de emergencia si es necesario
        local_torr = 'NewPct1_torrent_file'
        if item.emergency_urls and len(item.emergency_urls[0]) > x and not item.videolibray_emergency_urls:
            try:                                                                # Guardamos la url ALTERNATIVA
                if item.emergency_urls[0][x].startswith('http') or item.emergency_urls[0][x].startswith('//'):
                    item_local.torrent_alt = generictools.convert_url_base64(item.emergency_urls[0][x], host_torrent)
                else:
                    item_local.torrent_alt = generictools.convert_url_base64(item.emergency_urls[0][x])
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
                if not item_local.torrent_alt.startswith('http') and not item_local.torrent_alt.startswith('magnet'):
                    local_torr = filetools.join(config.get_videolibrary_path(), FOLDER, item_local.url)
        
        #Buscamos tamaño en el archivo .torrent
        if not size:
            size = scrapertools.find_single_match(data, '<div class="entry-left".*?><a href=' + \
                        '".*?span class=.*?>Size:<\/strong>?\s(\d+?\.?\d*?\s\w[b|B])<\/span>')
        if not size:                                                                #Para planetatorrent
            size = scrapertools.find_single_match(data, '<div class="fichas-box"><div class=' + \
                        '"entry-right"><div style="[^"]+"><span class="[^"]+"><strong>' + \
                        'Size:<\/strong>?\s(\d+?\.?\d*?\s\w[b|B])<\/span>')
        if not size:
            size = scrapertools.find_single_match(quality, '\s?\[(\d+.?\d*?\s?\w\s?[b|B])\]')
        if not size and item.armagedon and not item.videolibray_emergency_urls:
            torrent_params['url'] = item_local.url
            torrent_params['torrents_path'] = None
            torrent_params['local_torr'] = local_torr
            torrent_params['force'] = False
            torrent_params['torrent_f'] = ''
            torrent_params = generictools.get_torrent_size(item_local.url, torrent_params=torrent_params, 
                                                           timeout=timeout, headers=headers, item=item_local)   # Tamaño en el .torrent
            size = torrent_params['size']
            if torrent_params['torrents_path'] and not item_local.torrents_path: item_local.torrents_path = torrent_params['torrents_path']

            if 'ERROR' in size and item.emergency_urls and not item.videolibray_emergency_urls:
                local_torr = 'NewPct1_torrent_file'
                item_local.armagedon = True
                try:                                                        # Restauramos la url
                    if item.emergency_urls[0][x].startswith('http') or item.emergency_urls[0][x].startswith('//'):
                        item_local.url = generictools.convert_url_base64(item.emergency_urls[0][x], host_torrent)
                    else:
                        item_local.url = generictools.convert_url_base64(item.emergency_urls[0][x])
                        if not item.url.startswith('http'):
                            local_torr = filetools.join(config.get_videolibrary_path(), FOLDER, item_local.url)
                except:
                    item_local.torrent_alt = ''
                    item.emergency_urls[0] = []
                torrent_params['url'] = item_local.url
                torrent_params['torrents_path'] = None
                torrent_params['local_torr'] = local_torr
                torrent_params['force'] = False
                torrent_params['torrent_f'] = ''
                torrent_params = generictools.get_torrent_size(item_local.url, torrent_params=torrent_params, 
                                                               timeout=timeout, headers=headers, item=item_local)   # Tamaño en el .torrent
                size = torrent_params['size']
                if torrent_params['torrents_path'] and not item_local.torrents_path: item_local.torrents_path = torrent_params['torrents_path']

        if size:
            size = size.replace('GB', 'G·B').replace('Gb', 'G·b').replace('MB', 'M·B')\
                        .replace('Mb', 'M·b').replace('.', ',')
            item_local.torrent_info = '%s, ' % size                             #Agregamos size
        if item_local.url.startswith('magnet:'):
            item_local.torrent_info += ' Magnet'
        if item_local.torrent_info:
            item_local.torrent_info = item_local.torrent_info.strip().strip(',')
            #item.torrent_info = item_local.torrent_info
            if not item.unify:
                item_local.torrent_info = '[%s]' % item_local.torrent_info
   
        # Guadamos la password del RAR
        patron_pass = '<input\s*type="text"\s*id="txt_password"\s*name="[^"]+"\s*onClick="[^"]+"\s*value="([^"]+)"'
        if scrapertools.find_single_match(data, patron_pass):
            password = scrapertools.find_single_match(data, patron_pass)
            if password or item.password:
                if not item.password:
                    item.password = password
                    itemlist.append(item.clone(action="", title="[COLOR magenta][B] Contraseña: [/B][/COLOR]'" 
                            + item.password + "'", folder=False))
                item_local.password = item.password

        #Si es un lookup para cargar las urls de emergencia en la Videoteca, guardarmos los enlaces
        if item.videolibray_emergency_urls:
            item.emergency_urls[0].append(url_torr)                             # Guardamos el enlace del .torrent
            item.emergency_urls[2].append(url_torr)                             # Guardamos el enlace del .torrent
            item.emergency_urls[3].append(item_local.torrent_info)              # Guardamos el torrent_info del .torrent
            for scrapedurl, scrapedtitle, scrapedsize, scrapedquality, scrapedmagnet in find_alt_link_result:
                item.emergency_urls[0].append(scrapedmagnet)                    # Guardamos el enlace del .magnet
                item.emergency_urls[2].append(scrapedmagnet)                    # Guardamos el enlace del .magnet
                item.emergency_urls[3].append('#%s#%s' % (scrapedquality, scrapedsize))     # Guardamos el torrent_info del .magnet
            item.headers = headers
        
        #... ejecutamos el proceso normal
        else:
            item_local.headers = headers
            item_local.quality = quality
            if item.armagedon:
                item_local.quality = '[COLOR hotpink][E][/COLOR] [COLOR limegreen]%s[/COLOR]' % item_local.quality
            
            if not printed_CF and ("CF_BLOCKED" in item_local.torrents_path or "[B]BLOQUEO[/B]" in item_local.torrent_info):
                browser, res = generictools.call_browser('', lookup=True)
                if browser:
                    printed_CF = True
                    itemlist.append(item.clone(action="", title="[COLOR blue] Saldrán anuncios desde la web %s[/COLOR]" \
                                    % item_local.category, unify=False))
                    itemlist.append(item.clone(action="call_browser", channel="setting", 
                                    title="[COLOR blue][B]**- Pinche [COLOR yellow]aquí[/COLOR] para instrucciones de uso -**[/B][/COLOR]", 
                                    url="https://alfa-addon.com/threads/bloqueos-en-la-descarga-de-torrents.3646/", unify=False))
            
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
            
            if not size or 'Magnet' in size:
                item_local.alive = "??"                                         #Calidad del link sin verificar
            elif 'ERROR' in size and 'Pincha' in size:
                item_local.alive = "ok"                                         #link en error, CF challenge, Chrome disponible
            elif 'ERROR' in size and 'Introduce' in size:
                item_local.alive = "??"                                         #link en error, CF challenge, ruta de descarga no disponible
                item_local.channel = 'setting'
                item_local.action = 'setting_torrent'
                item_local.unify = False
                item_local.folder = False
                item_local.item_org = item.tourl()
            elif 'ERROR' in size:
                item_local.alive = "no"                                         #Calidad del link en error, CF challenge?
            else:
                item_local.alive = "ok"                                         #Calidad del link verificada
            if item_local.channel != 'setting':
                item_local.action = "play"                                      #Visualizar vídeo
                item_local.server = "torrent"                                   #Seridor Torrent
            
            itemlist_t.append(item_local.clone())                               #Pintar pantalla, si no se filtran idiomas
            quality = item_local.quality
            for scrapedurl, scrapedtitle, scrapedsize, scrapedquality, scrapedmagnet in find_alt_link_result:
                item_btdigg = item_local.clone()
                item_btdigg.url = scrapedmagnet
                item_btdigg.torrent_info = scrapedsize
                item_btdigg.title = '[[COLOR yellow]?[/COLOR]] [COLOR yellow][Torrent][/COLOR] ' \
                                     + '[COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR] %s' % \
                                     (scrapedquality, str(item_btdigg.language), \
                                     item_btdigg.torrent_info)
                if item_btdigg.contentType == 'movie': 
                    item_btdigg.quality = scrapedquality
                else:
                    item_btdigg.quality = quality
                item_btdigg.torrents_path = ''
                if not item.videolibray_emergency_urls: item_btdigg.btdigg = True
                itemlist_t.append(item_btdigg)
                find_alt = True
            
            # Requerido para FilterTools
            if config.get_setting('filter_languages', channel_py) > 0:          #Si hay idioma seleccionado, se filtra
                itemlist_f = filtertools.get_link(itemlist_f, item_local, list_language)  #Pintar pantalla, si no está vacío

            #logger.debug("TORRENT: " + scrapedurl + " / title gen/torr: " + item.title + " / " + item_local.title + " / calidad: " + item_local.quality + " / content: " + item_local.contentTitle + " / " + item_local.contentSerieName)
            #logger.debug(item_local)
        
    if not item.videolibray_emergency_urls:
        if find_alt:
            itemlist.append(item.clone(action="", title="[COLOR blue] Enlaces (imprecisos) buscados en%s" % btdigg_label))
        if len(itemlist_f) > 0:                                                 #Si hay entradas filtradas...
            itemlist.extend(itemlist_f)                                         #Pintamos pantalla filtrada
        else:                                                                       
            if config.get_setting('filter_languages', channel_py) > 0 and len(itemlist_t) > 0:  #Si no hay entradas filtradas ...
                thumb_separador = get_thumb("next.png")                         #... pintamos todo con aviso
                itemlist.append(Item(channel=item.channel, url=host, 
                            title="[COLOR red][B]NO hay elementos con el idioma seleccionado[/B][/COLOR]", 
                            thumbnail=thumb_separador, folder=False))
            itemlist.extend(itemlist_t)                                         #Pintar pantalla con todo si no hay filtrado
    
    
    """ VER y DESCARGAR vídeos, descargar vídeos un link,  o múltiples links"""
    itemlist_t = []                                                             #Itemlist total de enlaces
    itemlist_f = []                                                             #Itemlist de enlaces filtrados
    
    #Seleccionar el bloque para evitar duplicados
    patron = '<div id="tab1" class="tab_content"(.*?<\/ul>(?:<div.*?>)?<\/div><\/div><\/div>)'
    data = scrapertools.find_single_match(data_servidores, patron)
    
    host_dom = scrapertools.find_single_match(item.channel_host, '(?:http.*\:)?\/\/(?:www\.)?([^\?|\/]+)(?:\?|\/)')
    data = data.replace("http://tumejorserie.com/descargar/url_encript.php?link=", "(")
    data = re.sub(r'javascript:;" onClick="popup\("(?:http:)?\/\/(?:www.)?' + host_dom + 
                    '\w{1,9}\/library\/include\/ajax\/get_modallinks.php\?links=', "", data)

    # Nuevo sistema de scrapeo de servidores creado para Torrentlocula, compatible con otros clones de Newpct1
    patron = patron_lu
    if not item.armagedon:                                                      #Si es un proceso normal, seguimos
        enlaces_ver = re.compile(patron, re.DOTALL).findall(data)
    else:
        enlaces_ver = matches

    #logger.debug(enlaces_ver)
    
    #Si es un lookup para cargar las urls de emergencia en la Videoteca, lo hacemos y nos vamos sin más
    if item.videolibray_emergency_urls:
        emergency_urls_directos = []
        i = 0
        for logo, servidor, idioma, calidad, enlace, title in enlaces_ver:
            if "ver" in title.lower():
                emergency_urls_directos.append(enlaces_ver[i])
            i += 1
        item.emergency_urls[1] = emergency_urls_directos
        return item

    if not enlaces_ver:
        # Requerido para AutoPlay
        autoplay.start(itemlist, item)                                          #Lanzamos Autoplay
        return itemlist

    """ Recorre todos los links de VER y DESCARGAR, si está permitido """
    for accion in ['ver', 'descarga']:
        if accion == 'ver' and ver_enlaces_veronline == 0:
            continue
        elif accion == 'ver':
            ver_enlaces = ver_enlaces_veronline
            verificar_enlaces_validos = verificar_enlaces_veronline_validos
            excluir_enlaces = excluir_enlaces_veronline
        elif accion == 'descarga' and ver_enlaces_descargas == 0:
            continue
        elif accion == 'descarga':
            ver_enlaces = ver_enlaces_descargas
            verificar_enlaces_validos = verificar_enlaces_descargas_validos
            excluir_enlaces = excluir_enlaces_descargas
        cnt_enl_ver = 1
        cnt_enl_verif = 1
        
        for logo, servidor, idioma, calidad, enlace, title in enlaces_ver:
            if accion in title.lower():
                item_local = item.clone()
                servidor = servidor.replace("streamin", "streaminto").replace("uploaded", "uploadedto")
                partes = enlace.split(" ")                                      #Partimos el enlace en cada link de las partes
                if accion == 'descarga':
                    title = "Descarga"                      #Usamos la palabra reservada de Unify para que no formatee el título

                if servidor.capitalize() in excluir_enlaces:                    #Servidor excluido, pasamos al siguiente
                    continue
                
                #Recorremos cada una de las partes.  Vemos si el primer link está activo.  Si no lo está ignoramos todo el enlace
                p = 1
                for enlace in partes:
                    if accion == 'descarga':
                        if not item.unify:                                      #Si titles Inteligentes NO seleccionados:
                            title = "[COLOR yellow][%s][/COLOR] %s (%s/%s) [COLOR limegreen]" % \
                                    (servidor.capitalize(), "Descarga", p, len(partes)) + \
                                    "[%s][/COLOR] [COLOR red]%s[/COLOR]" % (item_local.quality, \
                                    str(item_local.language))
                        else:
                            title = title.replace('Descarga', 'Descarg.')
                            item_local.quality = '[/COLOR][COLOR white] %s (%s/%s) [/COLOR][COLOR limegreen][%s] ' \
                                    % ('Descarg.', p, len(partes), item.quality)
                            title = "[COLOR yellow][%s]%s[/COLOR] [COLOR red][%s][/COLOR]" % \
                                    (servidor.capitalize(), item_local.quality, str(item_local.language))
                
                    p += 1
                    mostrar_server = True
                    if config.get_setting("hidepremium"):                       #Si no se aceptan servidore premium, se ignoran
                        mostrar_server = servertools.is_server_enabled(servidor)
                        
                    #logger.debug("VER: url: " + enlace + " / title: " + title + 
                    #        " / servidor: " + servidor + " / idioma: " + idioma)
                    
                    #Si el servidor es válido, se comprueban si los links están activos
                    if mostrar_server:
                        try:
                            if cnt_enl_ver <= ver_enlaces or ver_enlaces == -1:
                                devuelve = servertools.findvideosbyserver(enlace, servidor)         #existe el link ?
                                if ver_enlaces == 0:
                                    cnt_enl_ver += 1
                            else:
                                ver_enlaces = 0                                 #FORZAR SALIR del loop
                                break                                           #Si se ha agotado el contador de verificación, se sale
                            
                            if devuelve:                                        #Hay link
                                enlace = devuelve[0][1]                         #Se guarda el link
                                
                                #Verifica si está activo el primer link.  Si no lo está se ignora el enlace-servidor entero
                                if p <= 2:
                                    item_local.alive = "??"                     #Se asume por defecto que es link es dudoso
                                    if ver_enlaces != 0:                        #Se quiere verificar si el link está activo?
                                        if cnt_enl_verif <= ver_enlaces or  ver_enlaces == -1:      #contador?
                                            #Llama a la subfunción de check_list_links(itemlist) para cada link de servidor
                                            item_local.alive = servertools.check_video_link(enlace, servidor, timeout=timeout)  #activo el link ?
                                            if verificar_enlaces_validos:       #Los links tienen que ser válidos para contarlos?
                                                if item_local.alive == "Ok":    #Sí
                                                    cnt_enl_verif += 1          #Movemos los contadores
                                                    cnt_enl_ver += 1            #Movemos los contadores
                                            else:                               #Si no es necesario que sean links válidos, sumamos
                                                cnt_enl_verif += 1              #Movemos los contadores
                                                cnt_enl_ver += 1                #Movemos los contadores
                                        else:
                                            ver_enlaces = 0                     #FORZAR SALIR del loop
                                            break                               #Si se ha agotado el contador de verificación, se sale

                                #Si el link no está activo se ignora
                                if accion == 'ver':
                                    if "??" in item_local.alive:                #dudoso
                                        item_local.title = '[COLOR yellow][?][/COLOR] [COLOR yellow]' + \
                                                '[%s][/COLOR] [COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR]' \
                                                % (servidor.capitalize(), item_local.quality, \
                                                str(item_local.language))
                                    elif "no" in item_local.alive.lower():      #No está activo.  Lo preparo, pero no lo pinto
                                        item_local.title = '[COLOR red][%s][/COLOR] [COLOR yellow]' % item_local.alive + \
                                                '[%s][/COLOR] [COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR]' \
                                                % (servidor.capitalize(), item_local.quality, str(item_local.language))
                                        logger.debug(item_local.alive + ": ALIVE / " + title + 
                                                " / " + servidor + " / " + enlace)
                                        raise
                                    else:                                       #Sí está activo
                                        item_local.title = '[COLOR yellow][%s][/COLOR] [COLOR limegreen]' % \
                                                servidor.capitalize() + '[%s][/COLOR] [COLOR red]%s[/COLOR]' % \
                                                (item_local.quality, str(item_local.language))
                                else:
                                    if "??" in item_local.alive:                #dudoso
                                        if not item.unify:                      #Si titles Inteligentes NO seleccionados:
                                            item_local.title = '[COLOR yellow][?][/COLOR] %s' % \
                                                    (title)
                                        else:
                                            item_local.title = '[COLOR yellow]%s[/COLOR]-%s' % \
                                                    (item_local.alive, title)
                                    elif "no" in item_local.alive.lower():      #No está activo.  Lo preparo, pero no lo pinto
                                        if not item.unify:                      #Si titles Inteligentes NO seleccionados:
                                            item_local.title = '[COLOR red][%s][/COLOR] %s' % \
                                                (item_local.alive, title)
                                        else:
                                            item_local.title = '[COLOR red]%s[/COLOR]-%s' % \
                                                (item_local.alive, title)
                                        logger.debug(item_local.alive + ": ALIVE / " 
                                                + title + " / " + servidor + " / " + enlace)
                                        raise
                                    else:                                           #Sí está activo
                                        item_local.title = title

                                #Preparamos el resto de variables de Item para ver los vídeos en directo    
                                item_local.action = "play"
                                item_local.server = servidor
                                item_local.url = enlace
                                
                                #Preparamos título y calidad, quitamos etiquetas vacías
                                item_local.title = re.sub(r'\s?\[COLOR \w+\]\[\[?\s?\]?\]\[\/COLOR\]', \
                                        '', item_local.title)    
                                item_local.title = re.sub(r'\s?\[COLOR \w+\]\s?\[\/COLOR\]', \
                                        '', item_local.title)
                                item_local.title = item_local.title.replace("--", "")\
                                        .replace("[]", "").replace("()", "").replace("(/)", "")\
                                        .replace("[/]", "").strip()
                                item_local.quality = re.sub(r'\s?\[COLOR \w+\]\[\[?\s?\]?\]\[\/COLOR\]'\
                                        , '', item_local.quality)
                                item_local.quality = re.sub(r'\s?\[COLOR \w+\]\s?\[\/COLOR\]', \
                                        '', item_local.quality)
                                item_local.quality = item_local.quality.replace("--", "")\
                                        .replace("[]", "").replace("()", "").replace("(/)", "")\
                                        .replace("[/]", "").strip()
                                
                                itemlist_t.append(item_local.clone())           #Pintar pantalla, si no se filtran idiomas
                                
                                # Requerido para FilterTools
                                if config.get_setting('filter_languages', channel_py) > 0: #Si hay idioma seleccionado, se filtra
                                    itemlist_f = filtertools.get_link(itemlist_f, item_local, \
                                        list_language)                          #Pintar pantalla, si no está vacío

                        except:
                            logger.error('ERROR al procesar enlaces VER/DESCARGAS DIRECTOS: ' + 
                                        servidor + ' / ' + enlace)
                            break

    if len(itemlist_f) > 0:                                                     #Si hay entradas filtradas...
        itemlist.extend(itemlist_f)                                             #Pintamos pantalla filtrada
    else:                                                                       
        if config.get_setting('filter_languages', channel_py) > 0 and len(itemlist_t) > 0: #Si no hay entradas filtradas ...
            thumb_separador = get_thumb("next.png")                             #... pintamos todo con aviso
            itemlist.append(Item(channel=item.channel, url=item.channel_host, title=\
                        "[COLOR red][B]NO hay elementos con el idioma seleccionado[/B][/COLOR]", 
                        thumbnail=thumb_separador, folder=False))
        
        if len(itemlist_t) == 0:
            if len(itemlist) == 0 or (len(itemlist) > 0 and itemlist[-1].server != 'torrent'):
                return []
        itemlist.extend(itemlist_t)                                             #Pintar pantalla con todo si no hay filtrado

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)                                              #Lanzamos Autoplay
    
    return itemlist
    

def episodios(item):
    logger.info()
    
    itemlist = []
    matches_old = []
    
    global host
    item, host = verify_host(item, host)                                        # Actualizamos la url del host
    if channel_clone_name == "*** DOWN ***":                                    # Ningún clones activo !!!
        itemlist.append(item.clone(action='', title="[COLOR yellow]Ningún canal NewPct1 activo[/COLOR]"))    
        return itemlist 
    json_category = item.channel_redir.lower() or item.category.lower()         # Salvamos la categoría que viene de la videoteca
    
    #logger.debug(item)

    if item.from_title:
        item.title = item.from_title
    
    #Limpiamos num. Temporada y Episodio que ha podido quedar por Novedades
    season_display = 0
    if item.contentSeason:
        if item.season_colapse:                                                 #Si viene del menú de Temporadas...
            season_display = item.contentSeason                                 #... salvamos el num de sesión a pintar
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
    idioma = idioma_busqueda
    if 'VO' in str(item.language):
        idioma = idioma_busqueda_VO
    try:
        tmdb.set_infoLabels(item, True, idioma_busqueda=idioma)
    except:
        pass
        
    modo_ultima_temp_alt = modo_ultima_temp
    if item.ow_force == "1":                                                    #Si hay una migración de canal o url, se actualiza todo 
        modo_ultima_temp_alt = False
    
    # Vemos la última temporada de TMDB y del .nfo
    max_temp = 1
    max_temp_seen = 0
    num_temporadas_flag = False
    if item.infoLabels['number_of_seasons']:
        max_temp = item.infoLabels['number_of_seasons']                         # Salvamos el num. máximo de temporadas
        num_temporadas_flag = True
    y = []
    if modo_ultima_temp_alt and item.library_playcounts:                        # Salvamos el num. de última temporada que hay en Videoteca
        patron = 'season (\d+)'
        matches = re.compile(patron, re.DOTALL).findall(str(item.library_playcounts))
        for x in matches:
            y += [int(x)]
        max_temp = max(y)
        num_temporadas_flag = True
    season = max_temp                                                           # Salvamos el num. última temporada
    
    # Si es actualización de la videoteca, no viene en el .nfo el "language" de la serie.  Hay que obtenerlo desde un episodio.json
    if item.library_playcounts:
        item = find_language(item, json_category)

    max_page = 100                                                              # Límite de páginas a visitar, la web da valores malos
    if item.library_playcounts: 
        max_page = old_div(max_page, 5)                                         # Si es una actualización, recortamos
    page = 1
    if scrapertools.find_single_match(item.url, '\/(\d{4,20})\/*$'):            # Tiene número de serie?
        list_pages = ['%s/pg/%s' % (item.url, page)]
    else:
        list_pages = ['%s//pg/%s' % (item.url, page)]                           # ... si no hay que poner 2 //
    
    data = ''
    list_episodes = []
    url_quality_alt = {}
    first = True                                                                # Primera pasada
    headers = {'referer': host}
    
    patron = '<li[^>]*>\s*<a href="(?P<url>[^"]+)"\s*title="[^>]+>\s*<img.*?'
    patron += 'src="(?P<thumb>[^"]+)?".*?<h2[^>]+>(?P<info>.*?)?<\/h2>'
    patron_noepis = 'Visitas:\s*[^>]*>\s*0<\/span>\s*<span[^>]*>[^>]*>\s*Genero:\s*[^>]*>\s*[^<]*<\/span>'
    patron_noepis += '<span[^>]*>[^>]*>\s*Estreno:[^>]*>\s*\d*<\/span>\s*<\/br>\s*<\/div>\s*<\/div>\s*<\/div>'
    patron_noepis += '<\/div>\s*<aside\s*class="sidebar"'

    """ Descarga las páginas """
    while list_pages and page < max_page:                                       # Recorre la lista de páginas, con límite

        if not data:
            data, response, item, itemlist = generictools.downloadpage(list_pages[0], timeout=timeout, headers=headers, 
                                                                       decode_code=decode_code, canonical=canonical, 
                                                                       quote_rep=True, no_comments=False, CF_test=CF_test, 
                                                                       item=item, itemlist=itemlist)        # Descargamos la página
            # Verificamos si ha cambiado el Host
            if response.host:
                global sufix, domain
                sufix = scrapertools.find_single_match(response.host, '\.\w+\/*$')
                domain = scrapertools.find_single_match(response.host, patron_domain)
                clone_list[0][2] = host
                return episodios(item)

        #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
        if not response.sucess or not data or not scrapertools.find_single_match(data, patron) \
                        or not ' ) Capitulos encontrados <' in data or '>( 0 ) Capitulos encontrados <' in data \
                        or scrapertools.find_single_match(data, patron_noepis):
            if (len(itemlist) > 0 and not ') Capitulos encontrados <' in data) or '>( 0 ) Capitulos encontrados <' in data\
                        or scrapertools.find_single_match(data, patron_noepis):
                break
                
            #Si a la url de la serie que se ha quitado el código final por fail-over, en algunos canales puede dar error
            if not scrapertools.find_single_match(item.url, '\/(\d{4,20})\/*$'):
                patron_series = "var\s*parametros\s*=\s*\{(?:'rating'\s*\:[^']+)?(?:'ratingc'\s*\:[^']+)?"
                patron_series += "(?:'n_votos'\s*\:[^']+)?(?:'id'\s*\:[^,]+,)?'cate'\s*\:\s*'([^']+)'"
                url_serie_nocode = scrapertools.find_single_match(data, patron_series)
                if url_serie_nocode:
                    url_serie_nocode = '%s/%s/pg/1' % (item.url, url_serie_nocode)
                    data, response, item, itemlist = generictools.downloadpage(url_serie_nocode, timeout=timeout, CF_test=CF_test, 
                                                                               decode_code=decode_code, quote_rep=True, 
                                                                               no_comments=False, headers=headers, 
                                                                               item=item, itemlist=itemlist)        # Descargamos la página
                else:
                    data = ''

            if not data or not scrapertools.find_single_match(data, patron):
                #Si no hay datos consistentes, llamamos al método de fail_over para que encuentre un canal que esté activo y pueda gestionar el vídeo
                item, data = generictools.fail_over_newpct1(item, patron, timeout=timeout)

        if not data and not item.library_playcounts:                            #No se ha encontrado ningún canal activo para este vídeo
            itemlist.append(item.clone(action='', title="[COLOR yellow]" + item.channel.capitalize() 
                        + '[/COLOR]: Ningún canal NewPct1 activo'))    
            itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 01: EPISODIOS:.  La Web no responde o la URL es erronea. ' 
                        + 'Si la Web está activa, reportar el error con el log'))
            return itemlist
        elif not data and item.library_playcounts:                              # Si es una actualización de la videoteca salimos sin meter basura
            return []
        
        matches = re.compile(patron, re.DOTALL).findall(data)
        if matches_old == matches:
            break
        matches_old = matches[:]
        
        if not matches or '>( 0 ) Capitulos encontrados <' in data:             #error
            if len(itemlist) == 0:                                              # Si ya hay datos, puede ser la última página
                logger.error("ERROR 02: EPISODIOS: Ha cambiado la estructura de la Web " 
                        + " / PATRON: " + patron + " / DATA: " + data)
                itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: EPISODIOS: Ha cambiado la estructura de la Web.  ' 
                        + 'Reportar el error con el log', contentSeason=0, contentEpisodeNumber=1))
            return itemlist                                                     #si no hay más datos, algo no funciona, pintamos lo que tenemos
        
        page += 1                                                               # Apuntamos a la página siguiente
        if scrapertools.find_single_match(item.url, '\/(\d{4,20})\/*$'):        # Tiene número de serie?
            list_pages = ['%s/pg/%s' % (item.url, page)]
        else:
            list_pages = ['%s//pg/%s' % (item.url, page)]                       # ... si no hay que poner 2 //

        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(list_pages)
        #logger.debug(data)
        
        serie_quality_url_patron = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+\/(serie[^\/]*)\/'
        serie_quality_url = scrapertools.find_single_match(item.url, serie_quality_url_patron)
        if serie_quality_url == 'series': serie_quality_url = 'serie'
        elif serie_quality_url == 'series-hd': serie_quality_url = 'serie-en-hd'
        elif serie_quality_url == 'series-vo': serie_quality_url = 'serie-vo'
        elif serie_quality_url == 'series-1080p': serie_quality_url = 'serie-1080p'
        elif serie_quality_url == 'series-4k': serie_quality_url = 'serie-4k'

        """ Recorremos todos los episodios generando un Item local por cada uno en Itemlist """
        x = 0
        for scrapedurl, scrapedthumb, info in matches:
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

            item_local.url = urlparse.urljoin(host, scrapedurl)
            episode_quality_url_patron = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+\/descargar\/(serie[^\/]*)\/'
            episode_quality_url = scrapertools.find_single_match(item_local.url, episode_quality_url_patron)
            if not episode_quality_url: episode_quality_url = 'serie'
            
            if scrapedthumb:
                item_local.thumbnail = urlparse.urljoin(host, scrapedthumb)
                item_local.contentThumbnail = item_local.thumbnail
            estado = True                                                       #Buena calidad de datos por defecto
            item_local.category = json_category.capitalize()                    #Restauramos la Categoría del .NFO
            x += 1
            item_local.context = "['buscar_trailer']"

            
            """ Localizamos el patrón correcto, teniendo en cuenta formatos antiguos """
            # NEW style
            if "<span" in info:
                pattern = "[^>]+>.*?(?:Temp\.|Temp\w*)\s*(?:<span[^>]+>\[\s?)?(?P<season>\d+)?.*?"
                pattern += "(?:Cap\.|Cap\w*)\s*(?:<span[^>]+>\[\s?)?(?P<episode>\d+)?(?:.*?(?P"
                pattern += "<episode2>\d+)?)<.*?<span[^>]+>(?P<lang>.*?)?<\/span>\s*Calidad"
                pattern += "\s*<span[^>]+>[\[]\s*(?P<quality>.*?)?\s*[\]]<\/span>"
                
                if not scrapertools.find_single_match(info, pattern):
                    if "especial" in info.lower():                              # Capitulos Especiales
                        pattern = ".*?[^>]+>.*?(?:Temp\.|Temp\w*).*?\[.*?(?P<season>\d+).*?\].*?"
                        pattern += "(?:Cap\.|Cap\w*).*?\[\s*(?P<episode>\d+).*?\]?(?:.*?"
                        pattern += "(?P<episode2>\d+)?)<.+?<span[^>]+>(?P<lang>.*?)?"
                        pattern += "<\/span>\s*Calidad\s*<span[^>]+>[\[]\s*(?P<quality>.*?)"
                        pattern += "?\s*[\]]<\/span>"
                    elif "miniserie" in info.lower() or "completa" in info.lower():     # Series o miniseries completa
                        pattern = ''
                        logger.debug("patron episodio NEW - MINISERIE: " + info)
                        info = '><strong>%sTemporada %s Capitulo 01_99</strong> - ' % \
                                (item_local.contentSerieName, season) + \
                                '<span >Español Castellano</span> Calidad <span >[%s]</span>' \
                                % item_local.quality
                
                if pattern and not scrapertools.find_single_match(info, pattern):   #en caso de error de formato, creo uno básico
                    logger.debug("patron episodio NEW: " + pattern)
                    logger.debug(info)
                    logger.debug(item_local.url)
                    info = '><strong>%sTemporada %s Capitulo 0</strong> - <span >' % \
                                (item_local.contentSerieName, season) + \
                                'Español Castellano</span> Calidad <span >[%s]</span>' \
                                % item_local.quality

            # OLD style.  Se intenta buscar un patrón que encaje con los diversos formatos antiguos.  Si no, se crea
            else:
                pattern = '\[(?P<quality>.*?)\]\[Cap.(?P<season>\d).*?(?P<episode>\d{2})'
                pattern += '(?:_(?P<season2>\d+)(?P<episode2>\d{2}))?\].*?(?P<lang>.*)?'    #Patrón básico por defecto

                if scrapertools.find_single_match(info, '\[\d{3}\]'):
                    info = re.sub(r'\[(\d{3}\])', r'[Cap.\1', info)
                elif scrapertools.find_single_match(info, 'Temp.*?(?P<season>\d+).*?[c|C]ap.*?\.' + \
                            '(?P<episode>\d+)?.*?(?:(?P<episode2>\d+))\]?\[(?P<lang>\w+)?(?P<quality>\w+)\]?'):
                    pattern = 'Temp.*?(?P<season>\d+).*?[c|C]ap.*?\.' + \
                            '(?P<episode>\d+)?.*?(?:(?P<episode2>\d+))\]?\[(?P<lang>\w+)?(?P<quality>\w+)\]?'
                elif scrapertools.find_single_match(info, 'Temp.*?(?P<season>\d+).*?\[(?P<quality>.*?)\].*?(?P<episode>\d{2})?' + \
                            '(?:.*?(?P<episode2>\d{2}))?.*?(?P<lang>\[\w+.*)\[.*?\]?'):
                    pattern = 'Temp.*?(?P<season>\d+).*?\[(?P<quality>.*?)\].*?(?P<episode>\d{2})?' + \
                            '(?:.*?(?P<episode2>\d{2}))?.*?(?P<lang>\[\w+.*)\[.*?\]?'
                elif scrapertools.find_single_match(info, 'Temp.*?(?P<season>\d+).*?\[(?P<quality>.*?)\].*?Cap\w?\.\s\d?' + \
                            '(?P<episode>\d{2})(?:.*?(?P<episode2>\d{2}))?.*?\[(?P<lang>\w+)\]?'):
                    pattern = 'Temp.*?(?P<season>\d+).*?\[(?P<quality>.*?)\].*?Cap\w?\.\s\d?' + \
                            '(?P<episode>\d{2})(?:.*?(?P<episode2>\d{2}))?.*?\[(?P<lang>\w+)\]?'
                elif scrapertools.find_single_match(info, '\[Cap.\d{2}_\d{2}\]'):
                    info = re.sub(r'\[Cap.(\d{2})_(\d{2})\]', r'[Cap.1\1_1\2]', info)
                elif scrapertools.find_single_match(info, '\[Cap.([A-Za-z]+)\]'):
                    info = re.sub(r'\[Cap.([A-Za-z]+)\]', '[Cap.100]', info)
                elif "completa" in info.lower():
                    info = info.replace("COMPLETA", "Caps. 01_99")
                    pattern = 'Temp.*?(?P<season>\d+).*?Cap\w?\.\s\d?(?P<episode>\d{2})' + \
                            '(?:.*?(?P<episode2>\d{2}))?.*?\[(?P<quality>.*?)\].*?\[(?P<lang>\w+)\]?'
                    if not scrapertools.find_single_match(info, pattern):       #en caso de error de formato, creo uno básico
                        logger.debug(info)
                        info = '%s - Temp.%s [Caps. 01_99][%s][Spanish]' % \
                                (item_local.contentSerieName, season, item_local.quality)
                
                if scrapertools.find_single_match(info, '\[Cap.\d{2,3}'):
                    pattern = "\[(?P<quality>.*?)\].*?\[Cap.(?P<season>\d).*?(?P<episode>\d{2})' + \
                            '(?:_(?P<season2>\d+)(?P<episode2>\d{2}))?.*?\].*?(?:\[(?P<lang>.*?)\])?"
                elif scrapertools.find_single_match(info, 'Cap.\d{2,3}'):
                    pattern = ".*?Temp.*?\s(?P<quality>.*?)\s.*?Cap.(?P<season>\d).*?(?P<episode>\d{2})' + \
                            '(?:_(?P<season2>\d+)(?P<episode2>\d{2}))?.*?\s(?P<lang>.*)?"
                elif scrapertools.find_single_match(info, '(?P<quality>.*?)?(?P<season>\d)[x|X|\.](?P<episode>\d{2})\s?' + \
                            '(?:_(?P<season2>\d+)(?P<episode2>\d{2}))?.*?(?P<lang>.*)?'):
                    pattern = "(?P<quality>.*?)?(?P<season>\d)[x|X|\.](?P<episode>\d{2})\s?' + \
                            '(?:_(?P<season2>\d+)(?P<episode2>\d{2}))?.*?(?P<lang>.*)?"
                    estado = False                                              #Mala calidad de datos
                
                if not scrapertools.find_single_match(info, pattern):           #en caso de error de formato, creo uno básico
                    logger.debug("patron episodio OLD: " + pattern)
                    logger.debug(info)
                    logger.debug(item_local.url)
                    info = '%s - Temp.%s [%s][Cap.%s00][Spanish]' % (item_local.contentSerieName, \
                            season, item_local.quality, season)
                    estado = False                                              #Mala calidad de datos
            
            """ Procesamos en PATRON encontrado/creado del episodio """
            try:
                r = re.compile(pattern)
                match = [m.groupdict() for m in r.finditer(info)][0]
            except:
                match = []
            if not match:                                                       #error
                logger.error("ERROR 02: EPISODIOS: Ha cambiado la estructura de la Web " 
                            + " / PATRON: " + pattern + " / DATA: " + info)
                itemlist.append(item.clone(action='', title=item.category + 
                            ': ERROR 02: EPISODIOS: Ha cambiado la estructura de la Web.  ' 
                            + 'Reportar el error con el log'))
                continue                                                        #pasamos al siguiente episodio

            #Si no se encuentran valores, se pone lo básico
            try:
                if match['season'] is None or match['season'] == "0" or \
                                not match['season']: match['season'] = season
                if match['episode'] is None: match['episode'] = "0"
                match['season'] = int(match['season'])
                match['episode'] = int(match['episode'])
            except:
                match['season'] = 1
                match['episode'] = 0
                logger.error(traceback.format_exc())
            season_alt = match['season']
            
            if match['season'] > max_temp or match['episode'] == 0:
                logger.error("ERROR 07: EPISODIOS: Error en número de Temporada o Episodio: " 
                        + " / TEMPORADA/EPISODIO: " + str(match['season']) + " / " + 
                        str(match['episode']) + " / NUM_TEMPORADA: " + str(max_temp) 
                        + " / " + str(season) + " / MATCHES: " + str(matches))
                match['season'] = scrapertools.find_single_match(item_local.url, '\/[t|T]emp\w+-*(\d+)\/')
                num_temporadas_flag = False
                if not match['season']:
                    match['season'] = season_alt
                else:
                    match['season'] = int(match['season'])

            if num_temporadas_flag and match['season'] != season and match['season'] > max_temp + 1:
                #Si el num de temporada está fuera de control, se trata pone en num. de temporada actual
                logger.error("ERROR 07: EPISODIOS: Num. de Temporada fuera de rango " + 
                            " / TEMPORADA: " + str(match['season']) + " / " + str(match['episode']) 
                            + " / NUM_TEMPORADA: " + str(max_temp) + " / " + str(season) + 
                            " / PATRON: " + pattern + " / MATCHES: " + str(matches))
                match['season'] = season
                item_local.contentSeason = season
            else:
                item_local.contentSeason = match['season']
                season = match['season']
                if match['episode'] > 0:
                    num_temporadas_flag = True
                if season > max_temp:
                    max_temp = season
                    
            if match['quality'] and estado == True:
                item_local.quality = match['quality']                           #Si hay quality se coge, si no, la de la serie
                item_local.quality = item_local.quality.replace("ALTA DEFINICION", "HDTV")
            
            if match['lang'] and (estado == False or "especia" in str(match['lang']).lower()):
                match['lang'] = match['lang'].replace("- ", "").replace("[", "").replace("]", "")
                item_local.infoLabels['episodio_titulo'] = match['lang']
                item_local.infoLabels['title'] = item_local.infoLabels['episodio_titulo']
            elif match['lang']:
                if 'espa' in match['lang'].lower(): item_local.language = ['CAST']
                if 'lati' in match['lang'].lower(): item_local.language = ['LAT']
                if 'dual' in match['lang'].lower(): item_local.language = ['DUAL']
                if 'vers' in match['lang'].lower() or 'orig' in match['lang'].lower() \
                        or 'subt' in match['lang'].lower() or 'ingl' in match['lang'].lower() \
                        or 'engl' in match['lang'].lower(): item_local.language = ['VOS']

            if match['episode'] == 0: match['episode'] = 1                      #Evitar errores en Videoteca
            item_local.contentEpisodeNumber = match['episode']

            if match["episode2"]:                                               #Hay episodio dos? es una entrada múltiple?
                item_local.title = "%sx%s al %s -" % (str(match["season"]), \
                        str(match["episode"]).zfill(2), str(match["episode2"])\
                        .zfill(2))                                              #Creamos un título con el rango de episodios
            else:                                                               #Si es un solo episodio, se formatea ya
                item_local.title = "%sx%s -" % (match["season"], str(match["episode"]).zfill(2))

            if first:                                                           #Si es el primer episodio, comprobamos que ...
                first = False
                if item_local.contentSeason < max_temp:                         #... la temporada sea la última ...
                    modo_ultima_temp_alt = False                                #... si no, por seguridad leeremos toda la serie
            
            if modo_ultima_temp_alt and item.library_playcounts:                #Si solo se actualiza la última temporada de Videoteca
                if item_local.contentSeason < max_temp and modo_ultima_temp_alt and max_temp_seen > 1:
                    list_pages = []                                             #Sale del bucle de leer páginas
                    break                                                       #Sale del bucle actual del FOR de episodios por página
                elif item_local.contentSeason < max_temp:                       #Si está desordenada ...
                    modo_ultima_temp_alt = False                                #... por seguridad leeremos toda la serie
              
            if season_display > 0:
                if item_local.contentSeason > season_display or (not modo_ultima_temp_alt \
                            and item_local.contentSeason != season_display):
                    continue
                elif item_local.contentSeason < season_display and max_temp_seen > 1:
                    list_pages = []                                             #Sale del bucle de leer páginas
                    break
                elif item_local.contentSeason < season_display:                 #Si no ha encontrado epis de la temp, sigue
                    continue

            max_temp_seen += 1

            # Si mezcla episodios de diferentes calidades e idiomas, intentamos filtrarlos para igualar a los de de la Serie
            if not item_local.quality: item_local.quality = item.quality
            if not item_local.language: item_local.language = item.language
            for lang in item_local.language:
                if lang in str(item.language):
                    break
            else:
                lang = ''
            if lang and item_local.title not in str(list_episodes):
                #if (item.quality == 'HDTV' and item_local.quality == item.quality) \
                #                or (item.quality != 'HDTV' and item_local.quality != 'HDTV'):
                if (item_local.quality == item.quality) \
                                or (serie_quality_url == episode_quality_url):
                    list_episodes += [item_local.title]
                    
                    item_local.quality = item.quality
                    itemlist.append(item_local.clone())
            if lang and item.quality != 'HDTV' and item_local.quality != 'HDTV':    # Salvamos las urls de calidades alternativas
                if len(itemlist) > 0 and itemlist[-1].url == item_local.url:
                    pass
                else:
                    if not url_quality_alt.get(item_local.title, ''):
                        url_quality_alt[item_local.title] = [(item_local.url, item_local.quality)]
                    else:
                        url_quality_alt[item_local.title].append((item_local.url, item_local.quality))

            #logger.debug(item_local)
            
        data = '' 

    try:
        if len(itemlist) > 1:
            itemlist = sorted(itemlist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))       #clasificamos
    except:
        logger.error(traceback.format_exc(1))

    for item_local in itemlist:                                                 # Salvamos las urls de calidades alternativas
        if url_quality_alt.get(item_local.title, ''):
            item_local.url_quality_alt = url_quality_alt[item_local.title]
    
    if item.season_colapse and not item.add_videolibrary:                       #Si viene de listado, mostramos solo Temporadas
        item, itemlist = generictools.post_tmdb_seasons(item, itemlist)

    if not item.season_colapse:                                                 #Si no es pantalla de Temporadas, pintamos todo
        # Pasada por TMDB y clasificación de lista por temporada y episodio
        tmdb.set_infoLabels(itemlist, True, idioma_busqueda=idioma)

        #Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
        item, itemlist = generictools.post_tmdb_episodios(item, itemlist)
    
    #logger.debug(item)

    return itemlist


def find_language(item, json_category=''):
    logger.info()

    if item.library_playcounts:
        try:
            from core import filetools, jsontools
            
            epi_json_path = ''
            epi_json_file = ''
            if not json_category:
                json_category = item.channel_redir.lower() or item.category.lower()

            # Localizamos un número de episodio válido
            for key, value in list(item.library_playcounts.items()):
                if scrapertools.find_single_match(key, '\d+x\d+'):
                    break
            
            # Creamos el path al episodio y verificamos que existe
            if config.get_setting("original_title_folder", "videolibrary") == 1 and item.infoLabels['originaltitle']:
                base_name = item.infoLabels['originaltitle']
            elif item.infoLabels['tvshowtitle']:
                base_name = item.infoLabels['tvshowtitle']
            elif item.infoLabels['title']:
                base_name = item.infoLabels['title']
            else:
                base_name = item.contentSerieName
            base_name = filetools.validate_path(base_name.replace('/', '-'))
            if config.get_setting("lowerize_title", "videolibrary") == 0:
                base_name = base_name.lower()
            epi_json_path = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_tvshows"))
            epi_json_path = filetools.join(epi_json_path, '%s [%s]' % (base_name, item.infoLabels['IMDBNumber']))
            epi_json_file = filetools.join(epi_json_path, '%s [%s].json' % (key, json_category))
            if not filetools.exists(epi_json_file):
                logger.info('MISSING epi_json_file %s' % epi_json_file)
                epi_json_file = filetools.join(epi_json_path, '1x01 [%s].json' % (json_category))
                if not filetools.exists(epi_json_file):
                    logger.info('MISSING epi_json_file %s' % epi_json_file)
                    item.language = ['CAST']
                    return item
            
            # Cargamos el episodio.json y obtenemos el language
            epi_json = jsontools.load(filetools.read(epi_json_file))
            if not epi_json:
                logger.error('ERROR READING epi_json_file %s' % epi_json_file)
            if 'language' in epi_json:
                item.language = epi_json['language']
            else:
                item.language = ['CAST']                                        # Si no hay language, tomamos CAST por defecto

        except:
            item.language = ['CAST']
            if epi_json_file:
                logger.error('ERROR in epi_json_file %s' % epi_json_file)
            else:
                logger.error('ERROR in epi_json_path %s' % epi_json_path)
            logger.error(traceback.format_exc(1))
            
    return item


def verify_host(item, host_call, force=False, category='', post=None):
    clone_list_alt = []
    host_call_save = host_call
    
    item.url = urlparse.urljoin(host_call, item.url)
    
    if channel_clone_name == "*** DOWN ***":                                    #Ningún clone activo !!!
        return (item, host_call_save)
    
    if item.channel_alt:
        category = item.category.lower()
        item.from_channel_alt = item.channel_alt
    elif item.from_channel_alt:
        category = item.category.lower()

    if force or host_index_check > 0 or post:                                   # Si se quiere usar un clone, en lo posible ...
        if not category:
            category = scrapertools.find_single_match(item.url, 'http.*\:\/\/(?:www.)?(\w+)\.\w+\/')
        if host_index_check > 0 and not category:
            category = channel_clone_name
        if post:
            category = channel_clone_post
        x = 0
        for active_clone, channel_clone, host_clone, contentType_clone, info_clone in clone_list_check:
            if category == channel_clone and active_clone == '1':               # Se comprueba que el clone esté activo
                clone_list_alt.append(clone_list_check[x])                      # y se salva como referencia
                break
            x += 1
        else:
            clone_list_alt = clone_list                                         # Si no se encuentra el clone, se usa el actual
    else:
        clone_list_alt = clone_list                                             # Se usa el clone actual
    
    # Renombramos el canal al nombre de clone elegido.  Actualizamos URL
    for active_clone, channel_clone, host_clone, contentType_clone, info_clone in clone_list_alt:
        host_call = host_clone                                                  # URL del clone actual
        item.channel_host = host_call
        dom_sufix_org = scrapertools.find_single_match(item.url, ':\/\/(.*?)[\/|?]').replace('.', '-')
        dom_sufix_clone = scrapertools.find_single_match(host_call, ':\/\/(.*?)\/*$').replace('.', '-')
        if not dom_sufix_org or not dom_sufix_clone: continue
        #if 'pctreload' in dom_sufix_clone:
        #    dom_sufix_clone = 'pctnew-org'
        if 'descargas2020' not in dom_sufix_clone and 'descargas2020' not in dom_sufix_clone \
                        and 'pctreload' not in dom_sufix_clone and 'pctmix' not in dom_sufix_clone: dom_sufix_clone = ''
        item.url = re.sub(scrapertools.find_single_match(item.url, '(http.*\:\/\/(?:www.)?\w+\.\w+\/)'), host_call, item.url)
        dom_sufix_clone = dom_sufix_clone.replace('pctmix-com', 'pctreload-com')
        item.url = item.url.replace(dom_sufix_org, dom_sufix_clone)
        item.category = channel_clone.capitalize()
        break                                                                   # Terminado
    else:
        return (item, host_call_save)
        
    item = generictools.verify_channel_regex(item, clone_list_alt)              # Procesamos los regex de url que tenga el clone
        
    global host, sufix, domain
    host = host_call
    sufix = scrapertools.find_single_match(host, '\.\w+\/*$')
    domain = scrapertools.find_single_match(host, patron_domain)
    
    return (item, host)


def find_torrent_link(url_torr, emergency_urls_pos, headers={}, item={}, itemlist=[], torrent_params={}, patron=''):
    global find_alt_link_result_save
    from core import filetools
    
    patron_torrent = '(https:\/\/[^"]+\.php(?:#|\?\w=)[^"]+)"'
    patron_quality = '(?i)(?:\d{0,4}p|HDTV$|\dKWebrip)'
    torrent_prefix = ''
    sufix = ''
    torrent_params['torrents_path'] = ''
    torrent_params['local_torr'] = 'NewPct1_torrent_file'
    torrent_params['torrent_f'] = ''
    torrent_params['find_alt_link_result_save'] = find_alt_link_result_save or []
    if not item: item = Item()
    item.torrents_path = ''
    headers_save = headers
    url_torr_save = url_torr
    cached = False
    short_link = ''
    retry_CF_own = 1 if not DUMMY in url_torr else -1

    torrent_cached_list = config.get_setting('torrent_cached_list', server='torrent', default=[])
    for link, path_torrent in torrent_cached_list:                              # Si ya estaba cacheado lo usamos
        if filetools.encode(url_torr.split('?')[0]) != link:
            continue
        url_torr = path_torrent
        torrent_params['local_torr'] = url_torr
        cached = True
        break
    else:
        torrent_params['local_torr'] = 'NewPct1_torrent_file'
    
    if item.emergency_urls and len(item.emergency_urls[0]) >= emergency_urls_pos and \
                           not item.emergency_urls[0][emergency_urls_pos].startswith('http') and \
                           not item.emergency_urls[0][emergency_urls_pos].startswith('magnet'):
            if item.contentType == 'movie':
                folder = config.get_setting("folder_movies")                    # películas
            else:
                folder = config.get_setting("folder_tvshows")                   # o series
            PATH_videos = filetools.join(config.get_videolibrary_path(), folder)
            torrent_params['torrent_alt'] = filetools.join(PATH_videos, item.emergency_urls[0][emergency_urls_pos])
            cached = True

    if url_torr:
        
        host_torrent_loc = scrapertools.find_single_match(url_torr_save, patron_host)
        host_torrent_loc = host_torrent_loc if host_torrent_loc.endswith('/') else host_torrent_loc + '/'
        headers['referer'] = host_torrent_loc
        if not cached and not DUMMY in url_torr:
            url_torr = url_torr.replace(" ", "%20")                             # Sustituimos espacios por %20, por si acaso
            if not url_torr.startswith("http"):                                 # Si le falta el http.: lo ponemos
                url_torr = scrapertools.find_single_match(host, '(\w+:)//') + url_torr
            set_tls = False if host_torrent in url_torr else True
            data, response, item, itemlist_alt = generictools.downloadpage(url_torr, timeout=timeout, referer=host, 
                                                                           set_tls=set_tls, retries_cloudflare=retry_CF_own, 
                                                                           decode_code=decode_code, quote_rep=True, alfa_s=False, 
                                                                           item=item, itemlist=[], CF_test=CF_test)     # Descargamos el enlace
            if not host_torrent in url_torr and scrapertools.find_single_match(data, patron):
                url_torr = scrapertools.find_single_match(data, patron)
                url_torr = url_torr.replace(" ", "%20")                         # Sustituimos espacios por %20, por si acaso
                if not url_torr.startswith("http"):                             # Si le falta el http.: lo ponemos
                    url_torr = scrapertools.find_single_match(host, '(\w+:)//') + url_torr
                set_tls = False if host_torrent in url_torr else True
                data, response, item, itemlist_alt = generictools.downloadpage(url_torr, timeout=timeout, referer=host, 
                                                                               set_tls=set_tls, retries_cloudflare=retry_CF_own, 
                                                                               decode_code=decode_code, quote_rep=True, alfa_s=False, 
                                                                               item=item, itemlist=[], CF_test=CF_test)     # Descargamos el enlace
                if scrapertools.find_single_match(data, patron):
                    url_torr = scrapertools.find_single_match(data, patron)
                    url_torr = url_torr.replace(" ", "%20")                     # Sustituimos espacios por %20, por si acaso
                    if not url_torr.startswith("http"):                         # Si le falta el http.: lo ponemos
                        url_torr = scrapertools.find_single_match(host, '(\w+:)//') + url_torr

            short_link = scrapertools.find_single_match(data, patron_torrent)
            if not short_link:
                logger.debug('NO short_link: %s' % data)
                retry_CF_own = -1
            elif not short_link.startswith("http"):                                     # Si le falta el http.: lo ponemos
                short_link = scrapertools.find_single_match(host, '(\w+:)//') + short_link
            if short_link:
                url_torr = generictools.convert_url_base64(short_link, referer=host_torrent_loc)
                if not url_torr.startswith('http') and not url_torr.startswith('magnet'):
                    url_torr = url_torr_save
                    retry_CF_own = -1
                else:
                    torrent_params['local_torr'] = filetools.basename(data.split('?')[0])

        torrent_params['url'] = url_torr
        torrent_params['url_index'] = url_torr_save
        torrent_params['torrents_path'] = None
        torrent_params['force'] = True
        quality = scrapertools.find_single_match(torrent_params.get('quality_alt', '') or item.quality, patron_quality).lower()
        if not torrent_params.get('quality_alt', ''):
            torrent_params['quality_alt'] = 'rip 720p 1080p 4kwebrip 4k' if '720' in item.quality or item.contentType == 'movie' else '[HDTV]'
            if 'screener' in item.quality.lower(): torrent_params['quality_alt'] += ' screener'
        set_tls = False if host_torrent in url_torr else True
        torrent_params = generictools.get_torrent_size(url_torr, torrent_params=torrent_params, 
                                                       timeout=timeout, headers=headers, 
                                                       set_tls=set_tls, retries_cloudflare=retry_CF_own, item=item)

        if torrent_params['torrents_path'] and not item.torrents_path: item.torrents_path = torrent_params['torrents_path']
        if item.contentType != 'movie':
            if torrent_params['find_alt_link_result'] and not find_alt_link_result_save:
                find_alt_link_result_save = torrent_params['find_alt_link_result'][:]
            torrent_params['find_alt_link_result'] = []
        
            for scrapedurl, scrapedtitle, scrapedsize, scrapedquality, scrapedmagnet in find_alt_link_result_save:
                if quality not in scrapedquality.lower(): continue
                torrent_params['find_alt_link_result'].append([scrapedurl, scrapedtitle, scrapedsize, scrapedquality, scrapedmagnet])
        
        if DUMMY in url_torr and torrent_params['find_alt_link_result']:
            torrent_params['size'] = torrent_params['find_alt_link_result'][0][2]
            url_torr = torrent_params['find_alt_link_result'][0][4]
            torrent_params['url'] = url_torr
            torrent_params['torrents_path'] = None
            item.quality = torrent_params['find_alt_link_result'][0][3]
            del torrent_params['find_alt_link_result'][0]
            
    return url_torr, headers_save


def find_torrent_link_OLD(url_torr, headers={}, item={}, itemlist=[], torrent_params={}):
    from core import filetools
    
    patron_torrent_inter = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+\/.*?\/(.*?)\/'
    torrent_token = scrapertools.find_single_match(url_torr, patron_torrent_inter)
    patron_torrent_prefix = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+\/(.*?)\/.*?\/'
    #torrent_prefix = scrapertools.find_single_match(url_torr, patron_torrent_prefix)
    torrent_prefix = ''
    #sufix = '.torrent'
    sufix = ''
    torrent_params['torrents_path'] = ''
    torrent_params['local_torr'] = 'NewPct1_torrent_file'
    torrent_params['torrent_f'] = ''
    if not item: item = Item()
    item.torrents_path = ''
    
    if item.emergency_urls:
        if item.contentType == 'movie':
            folder = config.get_setting("folder_movies")  # películas
        else:
            folder = config.get_setting("folder_tvshows")  # o series
        PATH_videos = filetools.join(config.get_videolibrary_path(), folder)
        try:
            torrent_params['torrent_alt'] = filetools.join(PATH_videos, item.emergency_urls[0][0])
        except:
            pass

    if url_torr:
        url_torr = url_torr.replace(" ", "%20")                                 # Sustituimos espacios por %20, por si acaso
        if not url_torr.startswith("http"):                                     # Si le falta el http.: lo ponemos
            url_torr = scrapertools.find_single_match(host, '(\w+:)//') + url_torr
        host_torrent = scrapertools.find_single_match(url_torr, patron_host)
        headers['referer'] = host_torrent if host_torrent.endswith('/') else host_torrent + '/'
        torrent_link = urlparse.urljoin(host_torrent, 'to.php')
        torrent_post = 't=%s' % torrent_token
        headers_link = {'Content-Type': 'application/x-www-form-urlencoded', 'Referer': url_torr, 'X-Requested-With': 'XMLHttpRequest'}
        retry_CF = canonical.get('retries_cloudflare', 0)
        
        for x in range(retry_CF+2):
            data, response, item, itemlist = generictools.downloadpage(torrent_link, timeout=timeout, headers=headers_link, 
                                                                       retries_cloudflare=retry_CF, 
                                                                       decode_code=decode_code, quote_rep=True, alfa_s=True, CF_test=CF_test, 
                                                                       post=torrent_post, item=item, itemlist=[])       # Descargamos el enlace
            
            if response.sucess and data and len(data) > 20 and len(data) < 250:
                url_torr = '%s%s' % (urlparse.urljoin(host+torrent_prefix, data), sufix)
                torrent_params['local_torr'] = filetools.basename(data.split('?')[0])
            
            if torrent_params:
                torrent_params['url'] = url_torr
                torrent_params['torrents_path'] = None
                torrent_params['force'] = True
                torrent_params = generictools.get_torrent_size(url_torr, torrent_params=torrent_params, 
                                                               timeout=timeout, headers=headers, 
                                                               retries_cloudflare=retry_CF, item=item)
                if torrent_params.get('code', 200) != 404:
                    break
            time.sleep(2)
        if torrent_params['torrents_path'] and not item.torrents_path: item.torrents_path = torrent_params['torrents_path']
            
    return url_torr, headers


def actualizar_titulos(item):
    logger.info()
    
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels
    item = generictools.update_title(item)
    
    #Volvemos a la siguiente acción en el canal
    return item

    
def search(item, texto, alfa_s=False):
    logger.info("search:" + texto)
    # texto = texto.replace(" ", "+")

    try:
        item.url = host + "get/result/"
        item.post = "categoryIDR=&categoryID=&idioma=&calidad=&ordenar=Fecha&inon=Descendente&s=%s&pg=1" % texto
        item.pattern = "buscar-list"
        item.extra = "search"
        item.headers = {'Referer': host}
        itemlist = listado(item, alfa_s=alfa_s)
        
        return itemlist

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        logger.error(traceback.format_exc())
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
 
 
def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    
    item.title = "newest"
    item.category_new = 'newest'
    item.channel = channel_py
    
    try:
        if categoria == 'peliculas':
            item.url = host + 'ultimas-descargas/'
            value = 757
            #item.post = "categoryIDR=%s&date=%s&pg=1" % (value, fecha_rango)
            item.extra = "novedades"
            item.extra2 = "pelicula"
            item.action = "listado"
            itemlist = listado(item)

        elif categoria == '4k':
            item.url = host + 'ultimas-descargas/'
            value = 1027
            #item.post = "categoryIDR=%s&date=%s&pg=1" % (value, fecha_rango)
            item.extra = "novedades"
            item.extra2 = "4k"
            item.action = "listado"
            itemlist = listado(item)
                
        elif categoria == 'latino':
            item.url = host + 'peliculas-latino/'
            value = 1527
            #item.post = "categoryIDR=%s&date=%s&pg=1" % (value, fecha_rango)
            item.extra = "peliculas"
            item.action = "listado"
            itemlist = listado(item)
            
        elif categoria == 'torrent':
            item.url = host + 'ultimas-descargas/'
            value = 757
            item.post = "categoryIDR=%s&date=%s&pg=1" % (value, fecha_rango)
            item.extra = "novedades"
            item.action = "listado"
            itemlist.extend(listado(item))
            
        if len(itemlist) > 0 and (">> Página siguiente" in itemlist[-1].title or "Pagina siguiente >>" in itemlist[-1].title):
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        logger.error(traceback.format_exc())
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist