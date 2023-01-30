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
from core import servertools
from core import scrapertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from lib import generictools
from channels import filtertools
from channels import autoplay

# Canal común con Cinetorrent(muerto), Magnetpelis, Pelispanda, Yestorrent


IDIOMAS = {'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['torrent']

canonical = {
             'channel': 'magnetpelis', 
             'host': config.get_setting("current_host", 'magnetpelis', default=''), 
             'host_alt': ['https://magnetpelis.re/'], 
             'host_black_list': ['https://magnetpelis.org/', 'https://magnetpelis.com/'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
host_torrent = host[:-1]
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
domain = scrapertools.find_single_match(host, patron_domain)

__modo_grafico__ = config.get_setting('modo_grafico', channel)                  # TMDB?
IDIOMAS_TMDB = {0: 'es', 1: 'en', 2: 'es,en'}
idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', channel)]    # Idioma base para TMDB
idioma_busqueda_VO = IDIOMAS_TMDB[2]                                                # Idioma para VO
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel) #Actualización sólo últ. Temporada?
timeout = config.get_setting('timeout_downloadpage', channel)
season_colapse = config.get_setting('season_colapse', channel)                  # Season colapse?
filter_languages = config.get_setting('filter_languages', channel)              # Filtrado de idiomas?
#page = 'page/1/'
page = ''


def mainlist(item):
    logger.info()
    itemlist = []
    
    thumb_pelis = get_thumb("channels_movie.png")

    thumb_series = get_thumb("channels_tvshow.png")

    thumb_genero = get_thumb("genres.png")
    thumb_anno = get_thumb("years.png")
    thumb_calidad = get_thumb("top_rated.png")
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Películas", action="submenu", 
                url=host, thumbnail=thumb_pelis, extra="peliculas"))
    itemlist.append(Item(channel=item.channel, title="    - por Género", action="genero", 
                url=host, thumbnail=thumb_genero, extra="peliculas"))
    itemlist.append(Item(channel=item.channel, title="    - por Año", action="anno", 
                url=host, thumbnail=thumb_anno, extra="peliculas"))
    if channel not in ['magnetpelis']:
        itemlist.append(Item(channel=item.channel, title="    - por Calidad", action="calidad", 
                url=host, thumbnail=thumb_calidad, extra="peliculas"))
    
    itemlist.append(Item(channel=item.channel, title="Series", action="submenu", 
                url=host, thumbnail=thumb_series, extra="series"))
    itemlist.append(Item(channel=item.channel, title="    - por Año", action="anno", 
                url=host, thumbnail=thumb_anno, extra="series"))
    
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

    patron = '<li\s*class="header__nav-item">\s*<a\s*href="([^"]+)"\s*class="header__nav-link">([^<]+)<\/a>'

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
        if scrapertools.slugify(scrapedtitle) in item.extra:
            item.url = urlparse.urljoin(host, scrapedurl.replace(scrapertools.find_single_match(scrapedurl, patron_host), ''))
            if not item.url.endswith('/'): item.url += '/'
            item.url += page
            return listado(item)
            
    return itemlist


def anno(item):
    logger.info()
    from platformcode import platformtools
    
    itemlist = []
    
    patron = '(?i)<a\s*class="dropdown-toggle\s*header__nav-link"\s*href="#"\s*'
    patron += 'role="button"\s*data-toggle="dropdown">[^<]*A.O\s*<\/a>\s*'
    patron += '<ul\s*class="dropdown-menu\s*header__dropdown-menu">\s*(.*?)\s*<\/ul>\s*<\/li>'

    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               s2=False, patron=patron, item=item, itemlist=[])     # Descargamos la página

    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if not response.sucess or itemlist:                                         # Si ERROR o lista de errores ...
        return itemlist                                                         # ... Salimos

    data = scrapertools.find_single_match(data, patron)
    patron = '<li><a\s*href="([^"]+)"\s*target="[^"]*">([^<]+)\s*<\/a>\s*<\/li>'
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

    year = platformtools.dialog_numeric(0, "Introduzca el Año de búsqueda", default="")
    item.url = re.sub(r'years/\d+', 'years/%s' % year, matches[0][0])
    if not item.url.endswith('/'): item.url += '/'
    item.url += page
    item.extra2 = 'anno' + str(year)

    return listado(item)

    
def genero(item):
    logger.info()
    itemlist = []

    patron = '(?i)<a\s*class="dropdown-toggle\s*header__nav-link"\s*href="#"\s*'
    patron += 'role="button"\s*data-toggle="dropdown">[^<]*G.nero\s*<\/a>\s*'
    patron += '<ul\s*class="dropdown-menu\s*header__dropdown-menu">\s*(.*?)\s*<\/ul>\s*<\/li>'

    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               s2=False, patron=patron, item=item, itemlist=[])     # Descargamos la página

    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if not response.sucess or itemlist:                                         # Si ERROR o lista de errores ...
        return itemlist                                                         # ... Salimos

    data = scrapertools.find_single_match(data, patron)
    patron = '<li><a\s*href="([^"]+)"\s*target="[^"]*">([^<]+)\s*<\/a>\s*<\/li>'
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
        itemlist.append(item.clone(action="listado", title=gen.capitalize(), url=scrapedurl + page, 
                        extra2='genero'))

    return itemlist


def calidad(item):
    
    logger.info()
    itemlist = []

    patron = '(?i)<a\s*class="dropdown-toggle\s*header__nav-link"\s*href="#"\s*'
    patron += 'role="button"\s*data-toggle="dropdown">[^<]*calidad\s*<\/a>\s*'
    patron += '<ul\s*class="dropdown-menu\s*header__dropdown-menu">\s*(.*?)\s*<\/ul>\s*<\/li>'

    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               s2=False, patron=patron, item=item, itemlist=[])     # Descargamos la página

    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if not response.sucess or itemlist:                                         # Si ERROR o lista de errores ...
        return itemlist                                                         # ... Salimos

    data = scrapertools.find_single_match(data, patron)
    patron = '<li><a\s*href="([^"]+)"\s*target="[^"]*">([^<]+)\s*<\/a>\s*<\/li>'
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

    for scrapedurl, cal in matches:
        if cal not in ['HD', '720p']:
            itemlist.append(item.clone(action="listado", title=cal.capitalize(), url=scrapedurl + page, 
                        extra2='calidad'))

    return itemlist


def listado(item):                                                              # Listado principal y de búsquedas
    logger.info()
    
    itemlist = []
    item.category = categoria
    thumb_pelis = get_thumb("channels_movie.png")
    thumb_series = get_thumb("channels_tvshow.png")

    #logger.debug(item)
    
    curr_page = 1                                                               # Página inicial
    last_page = 99999                                                           # Última página inicial
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
    
    cnt_tot = 30                                                                # Poner el num. máximo de items por página
    cnt_title = 0                                                               # Contador de líneas insertadas en Itemlist
    if item.cnt_tot_match:
        cnt_tot_match = float(item.cnt_tot_match)                               # restauramos el contador TOTAL de líneas procesadas de matches
        del item.cnt_tot_match
    else:
        cnt_tot_match = 0.0                                                     # Contador TOTAL de líneas procesadas de matches
    inicio = time.time()                                    # Controlaremos que el proceso no exceda de un tiempo razonable
    fin = inicio + 5                                                            # Después de este tiempo pintamos (segundos)
    timeout_search = timeout * 2                                                # Timeout para descargas
    if item.extra == 'search' and item.extra2 == 'episodios':                   # Si viene de episodio que quitan los límites
        cnt_tot = 999
        fin = inicio + 30

    #Sistema de paginado para evitar páginas vacías o semi-vacías en casos de búsquedas con series con muchos episodios
    title_lista = []                                        # Guarda la lista de series que ya están en Itemlist, para no duplicar lineas
    if item.title_lista:                                    # Si viene de una pasada anterior, la lista ya estará guardada
        title_lista.extend(item.title_lista)                                    # Se usa la lista de páginas anteriores en Item
        del item.title_lista                                                    # ... limpiamos
    matches = []
        
    if not item.extra2:                                                         # Si viene de Catálogo o de Alfabeto
        item.extra2 = ''
        
    post = None
    if item.post:                                                               # Rescatamos el Post, si lo hay
        post = item.post
    
    next_page_url = item.url
    # Máximo num. de líneas permitidas por TMDB. Máx de 5 segundos por Itemlist para no degradar el rendimiento
    while (cnt_title < cnt_tot and curr_page <= last_page and fin > time.time()) or item.matches:
    
        # Descarga la página
        data = ''
        cnt_match = 0                                                           # Contador de líneas procesadas de matches
        if not item.matches:                                                    # si no viene de una pasada anterior, descargamos
            data, response, item, itemlist = generictools.downloadpage(next_page_url, canonical=canonical, 
                                                                       timeout=timeout_search, post=post, s2=False, 
                                                                       item=item, itemlist=itemlist)        # Descargamos la página)
            # Verificamos si ha cambiado el Host
            if response.host:
                next_page_url = response.url_new
            elif response.url and response.url != next_page_url:
                next_page_url = item.url = '%s%s' % (response.url, scrapertools.find_single_match(next_page_url, '(page\/\d+\/?)'))
            
            # Verificamos si se ha cargado una página correcta
            curr_page += 1                                                      # Apunto ya a la página siguiente
            if not data or not response.sucess:                                 # Si la web está caída salimos sin dar error
                if len(itemlist) > 1:                                           # Si hay algo que pintar lo pintamos 
                    last_page = 0
                    break
                return itemlist                                                 # Si no hay nada más, salimos directamente
        
        #Patrón para búsquedas, pelis y series
        patron = '<div\s*class="[^"]+">\s*<div\s*class="card">\s*<a\s*href="([^"]+)"'
        patron += '\s*class="card__cover">\s*<img[^>]+src="([^"]*)"\s*alt="[^"]*"\s*\/*>\s*'
        patron += '<div\s*class="card__play">.*?<\/div>\s*<ul\s*class="card__list">\s*'
        patron += '<li>([^<]+)<\/li>\s*<\/ul>\s*(?:<ul\s*class="card__list\s*right">\s*'
        patron += '<li>(\w*)<\/li>[^"]*<\/ul>\s*)?<\/a>\s*<div\s*class="card__content">\s*'
        patron += '<h3\s*class="card__title"><a\s*href="[^"]+">([^<]+)<\/a><\/h3>'
        patron += '.*?<\/div>\s*<\/div>\s*<\/div>'

        if not item.matches:                                                    # De pasada anterior?
            matches = re.compile(patron, re.DOTALL).findall(data)
        else:
            matches = item.matches
            del item.matches
            
        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)

        if not matches and item.extra != 'search' and not item.extra2:          #error
            logger.error("ERROR 02: LISTADO: Ha cambiado la estructura de la Web " 
                        + " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + 
                        ': ERROR 02: LISTADO: Ha cambiado la estructura de la Web.  ' 
                        + 'Reportar el error con el log'))
            break                                                               #si no hay más datos, algo no funciona, pintamos lo que tenemos
        
        if not matches and item.extra == 'search':                              #búsqueda vacía
            if len(itemlist) > 0:                                               # Si hay algo que pintar lo pintamos
                last_page = 0
                break
            return itemlist                                                     #Salimos
        
        # Buscamos la próxima página
        if not '/page/' in item.url:
            next_page_url = ''
        else:
            next_page_url = re.sub(r'page\/(\d+)', 'page/%s' % str(curr_page), item.url)
        #logger.debug('curr_page: ' + str(curr_page) + ' / last_page: ' + str(last_page))
        
        # Buscamos la última página
        if last_page == 99999:                                                  #Si es el valor inicial, buscamos
            patron_last = '<ul\s*class="pagination[^"]+">.*?<li>\s*<a\s*class="page-numbers"\s*href="[^"]+">'
            patron_last += '(\d+)<\/a><\/li>\s*<li>\s*<a\s*class="next page-numbers"\s*href="[^"]+">»<\/a><\/li>\s*<\/ul>'
            try:
                last_page = int(scrapertools.find_single_match(data, patron_last))
                page_factor = float(len(matches)) / float(cnt_tot)
            except:                                                             #Si no lo encuentra, lo ponemos a 999
                last_page = 1
                last_page_print = int((float(len(matches)) / float(cnt_tot)) + 0.999999)

            #logger.debug('curr_page: ' + str(curr_page) + ' / last_page: ' + str(last_page))
        
        #Empezamos el procesado de matches
        for scrapedurl, scrapedthumb, scrapedquality, scrapedlanguage, scrapedtitle in matches:
            cnt_match += 1
            
            title = scrapedtitle

            title = scrapertools.remove_htmltags(title).rstrip('.')             # Removemos Tags del título
            url = scrapedurl
            
            title_subs = []                                                     #creamos una lista para guardar info importante
            
            # Slugify, pero más light
            title = title.replace("á", "a").replace("é", "e").replace("í", "i")\
                    .replace("ó", "o").replace("ú", "u").replace("ü", "u")\
                    .replace("ï¿½", "ñ").replace("Ã±", "ñ")
            title = scrapertools.decode_utf8_error(title)

            # Se filtran las entradas para evitar duplicados de Temporadas
            url_list = url
            if url_list in title_lista:                                         #Si ya hemos procesado el título, lo ignoramos
                continue
            else:
                title_lista += [url_list]                                       #la añadimos a la lista de títulos

            # Si es una búsqueda por años, filtramos por tipo de contenido
            if item.extra == 'series' and '/serie' not in url:
                continue
            elif item.extra == 'peliculas' and '/serie' in url:
                continue
            
            cnt_title += 1                                                      # Incrementamos el contador de entradas válidas
            
            item_local = item.clone()                                           #Creamos copia de Item para trabajar
            if item_local.tipo:                                                 #... y limpiamos
                del item_local.tipo
            if item_local.totalItems:
                del item_local.totalItems
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
            
            # Después de un Search se restablecen las categorías
            if item_local.extra == 'search':
                if '/serie' in url:
                    item_local.extra = 'series'                                 # Serie búsqueda
                else:
                    item_local.extra = 'peliculas'                              # Película búsqueda

            # Procesamos idiomas
            item_local.language = []                                            #creamos lista para los idiomas
            if '[Subs. integrados]' in scrapedquality or '(Sub Forzados)' in scrapedquality \
                        or 'Sub' in scrapedquality or 'ing' in scrapedlanguage.lower():
                item_local.language = ['VOS']                                   # añadimos VOS
            if 'lat' in scrapedlanguage.lower():
                item_local.language += ['LAT']                                  # añadimos LAT
            if 'castellano' in scrapedquality.lower() or ('español' in scrapedquality.lower() \
                        and not 'latino' in scrapedquality.lower()) or 'cas' in scrapedlanguage.lower(): 
                item_local.language += ['CAST']                                 # añadimos CAST
            if '[Dual' in title or 'dual' in scrapedquality.lower() or 'dual' in scrapedlanguage.lower():
                title = re.sub(r'(?i)\[dual.*?\]', '', title)
                item_local.language += ['DUAL']                                 # añadimos DUAL
            if not item_local.language:
                item_local.language = ['LAT']                                   # [LAT] por defecto
                
            # Procesamos Calidad
            if scrapedquality:
                item_local.quality = scrapertools.remove_htmltags(scrapedquality)   # iniciamos calidad
                if '[720p]' in scrapedquality.lower() or '720p' in scrapedquality.lower():
                    item_local.quality = '720p'
                if '[1080p]' in scrapedquality.lower() or '1080p' in scrapedquality.lower():
                    item_local.quality = '1080p'
                if '4k' in scrapedquality.lower():
                    item_local.quality = '4K'
                if '3d' in scrapedquality.lower() and not '3d' in item_local.quality.lower():
                    item_local.quality += ', 3D'
            if not item_local.quality or item_local.extra == 'series':
                item_local.quality = '720p'
                
            item_local.thumbnail = ''                                           #iniciamos thumbnail

            item_local.url = urlparse.urljoin(host, url)                        #guardamos la url final
            item_local.context = "['buscar_trailer']"                           #... y el contexto

            # Guardamos los formatos para series
            if item_local.extra == 'series' or '/serie' in item_local.url:
                item_local.contentType = "tvshow"
                item_local.action = "episodios"
                item_local.season_colapse = season_colapse                      #Muestra las series agrupadas por temporadas?
            else:
                # Guardamos los formatos para películas
                item_local.contentType = "movie"
                item_local.action = "findvideos"

            #Limpiamos el título de la basura innecesaria
            if item_local.contentType == "tvshow":
                title = scrapertools.find_single_match(title, '(^.*?)\s*(?:$|\(|\[|-)')

            title = re.sub(r'(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie', '', title).strip()
            item_local.quality = re.sub(r'(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', 
                        '', item_local.quality).strip()

            #Analizamos el año.  Si no está claro ponemos '-'
            item_local.infoLabels["year"] = '-'
            try:
                if 'anno' in item.extra2:
                    item_local.infoLabels["year"] = int(item.extra2.replace('anno', ''))
            except:
                pass
            
            #Terminamos de limpiar el título
            title = re.sub(r'[\(|\[]\s+[\)|\]]', '', title)
            title = title.replace('()', '').replace('[]', '').replace('[4K]', '').replace('(4K)', '').strip().lower().title()
            item_local.from_title = title.strip().lower().title()           #Guardamos esta etiqueta para posible desambiguación de título

            #Salvamos el título según el tipo de contenido
            if item_local.contentType == "movie":
                item_local.contentTitle = title
            else:
                item_local.contentSerieName = title.strip().lower().title()

            item_local.title = title.strip().lower().title()
            
            #Guarda la variable temporal que almacena la info adicional del título a ser restaurada después de TMDB
            item_local.title_subs = title_subs
                
            #Salvamos y borramos el número de temporadas porque TMDB a veces hace tonterias.  Lo pasamos como serie completa
            if item_local.contentSeason and (item_local.contentType == "season" \
                        or item_local.contentType == "tvshow"):
                item_local.contentSeason_save = item_local.contentSeason
                del item_local.infoLabels['season']

            #Ahora se filtra por idioma, si procede, y se pinta lo que vale
            if filter_languages > 0:                                            #Si hay idioma seleccionado, se filtra
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

    #Bajamos los datos de la página y seleccionamos el bloque
    patron = '\s*<th\s*class="hide-on-mobile">Total\s*Descargas<\/th>\s*<th>'
    patron += 'Descargar<\/th>\s*<\/thead>\s*<tbody>\s*(.*?<\/tr>)\s*<\/tbody>'
    patron += '\s*<\/table>\s*<\/div>'
    
    if not item.matches:
        data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                                   s2=False, patron=patron, item=item, itemlist=[])     # Descargamos la página)

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
    elif data:
        # Seleccionamos el bloque y buscamos los apartados
        data = scrapertools.find_single_match(data, patron)

    patron = '<tr>(?:\s*<td[^>]*>(\d+)<\/td>)?(?:\s*<td[^>]*>([^<]*)<\/td>)?\s*'
    patron += '<td[^>]*>([^<]+)<\/td>\s*<td[^>]*>([^<]*)<\/td>\s*<td\s*class=[^<]+<\/td>'
    patron += '(?:\s*<td[^>]*>([^<]+)<\/td>)?(?:\s*<td\s*class=[^<]+<\/td>)?\s*'
    patron += '<td\s*class=[^<]+<\/td>\s*<td[^>]*>\s*<a\s*class="[^>]+href="([^"]+)"'

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
    for x, (episode_num, _scrapedserver, _scrapedquality, _scrapedlanguage, scrapedsize, scrapedurl) in enumerate(matches):
        scrapedpassword = ''
        if _scrapedserver not in ['torrent', 'Torrent', 'array', 'Array']:
            scrapedserver = 'torrent'
            scrapedquality = _scrapedserver
            scrapedlanguage = _scrapedquality
        else:
            scrapedserver = _scrapedserver
            scrapedquality = _scrapedquality
            scrapedlanguage = _scrapedlanguage

        #Generamos una copia de Item para trabajar sobre ella
        item_local = item.clone()

        item_local.url = generictools.convert_url_base64(scrapedurl, host_torrent)
        if item.videolibray_emergency_urls and item_local.url != scrapedurl:
            item.emergency_urls[1][x][4] = item_local.url
        
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
        if 'castellano' in scrapedlanguage.lower() or ('español' in scrapedlanguage.lower() and not 'latino' in scrapedlanguage.lower()):
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
        
        item_local.server = scrapedserver.lower()                               #Servidor
        if item_local.url.startswith('magnet:') or not item_local.server:
            item_local.server = 'torrent'
        if item_local.server != 'torrent':
            if config.get_setting("hidepremium"):                               #Si no se aceptan servidore premium, se ignoran
                if not servertools.is_server_enabled(item_local.server):
                    continue
            devuelve = servertools.findvideosbyserver(item_local.url, item_local.server)    #existe el link ?
            if not devuelve:
                continue
            item_local.url = devuelve[0][1]
            item_local.alive = servertools.check_video_link(item_local.url, item_local.server, timeout=timeout)     #activo el link ?
            if 'NO' in item_local.alive:
                continue
        
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
    

def episodios(item):
    logger.info()
    
    itemlist = []
    item.category = categoria
    
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
    if item.infoLabels['number_of_seasons']:
        max_temp = item.infoLabels['number_of_seasons']
    y = []
    if modo_ultima_temp_alt and item.library_playcounts:                        #Averiguar cuantas temporadas hay en Videoteca
        patron = 'season (\d+)'
        matches = re.compile(patron, re.DOTALL).findall(str(item.library_playcounts))
        for x in matches:
            y += [int(x)]
        max_temp = max(y)

    # Si la series tiene solo una temporada, o se lista solo una temporada, guardamos la url y seguimos normalmente
    list_temp = []
    list_temp.append(item.url)
    #logger.debug(list_temp)

    # Descarga las páginas
    for _url in list_temp:                                                       # Recorre todas las temporadas encontradas
        url = _url
        data, response, item, itemlist = generictools.downloadpage(url, timeout=timeout, canonical=canonical, 
                                                                   s2=False, item=item, itemlist=itemlist)      # Descargamos la página
        # Verificamos si ha cambiado el Host
        if response.host:
            for x, u in enumerate(list_temp):
                list_temp[x] = list_temp[x].replace(scrapertools.find_single_match(url, patron_host), response.host.rstrip('/'))
            url = response.url_new

        #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
        if not response.sucess:                                                 # Si ERROR o lista de errores ...
            return itemlist                                                     # ... Salimos

        patron_temp = '<div\s*class="card-header"[^>]*>\s*<button\s*type="button"\s*'
        patron_temp += 'data-toggle="collapse"\s*data-target="#collapse-\d+">\s*'
        patron_temp += '<span>Temporada\s*(\d+)[^<]*<\/span>(.*?)<\/table>\s*<\/div>\s*<\/div>\s*<\/div>'
        
        matches_temp = re.compile(patron_temp, re.DOTALL).findall(data)
        
        #logger.debug("PATRON_temp: " + patron_temp)
        #logger.debug(matches_temp)
        #logger.debug(data)
        
        if 'class="accordion__list"' not in str(matches_temp):
            matches_temp = []
            patron_acorta = '<a\s*class="btn\s*btn-primary"[^>]*href="([^"]+)"\s*>'
            matches_temp_acorta = re.compile(patron_acorta, re.DOTALL).findall(data)

            for acorta in matches_temp_acorta:
                url = generictools.convert_url_base64(acorta, host_torrent)
                data_alt, response, item, itemlist = generictools.downloadpage(url, timeout=timeout, canonical=canonical, 
                                                                           s2=False, item=item, itemlist=itemlist)      # Descargamos la página
                matches_temp_temp = re.compile(patron_temp, re.DOTALL).findall(data_alt)
                if not matches_temp_temp: logger.debug(data_alt)
                matches_temp.extend(matches_temp_temp)
            
            #logger.debug("PATRON_temp: " + patron_temp)
            #logger.debug(matches_temp)
            #logger.debug(data_alt)

        patron = '<tr>(?:\s*<td[^>]*>(\d+)<\/td>)?(?:\s*<td[^>]*>([^<]*)<\/td>)?\s*'
        patron += '<td[^>]*>([^<]+)<\/td>\s*<td[^>]*>([^<]*)<\/td>\s*<td\s*class=[^<]+<\/td>'
        patron += '(?:\s*<td[^>]*>([^<]+)<\/td>)?(?:\s*<td\s*class=[^<]+<\/td>)?\s*'
        patron += '<td\s*class=[^<]+<\/td>\s*<td[^>]*>\s*<a\s*class="[^>]+href="([^"]+)"'
        
        for season_num, episodes in matches_temp:

            matches = re.compile(patron, re.DOTALL).findall(episodes)

            #logger.debug("PATRON: " + patron)
            #logger.debug(matches)
            #logger.debug(episodes)

            # Recorremos todos los episodios generando un Item local por cada uno en Itemlist
            for episode_num, scrapedserver, scrapedquality, scrapedlanguage, scrapedsize, scrapedurl in matches:
                server = scrapedserver
                if not server: server = 'torrent'
                item_local = item.clone()
                item_local.action = "findvideos"
                item_local.contentType = "episode"
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

                item_local.url = url                                            # Usamos las url de la temporada, no hay de episodio
                url_base64 = generictools.convert_url_base64(scrapedurl, host_torrent)
                item_local.matches = []
                item_local.matches.append((episode_num, server, scrapedquality, scrapedlanguage, scrapedsize, url_base64))  # Salvado Matches de cada episodio
                item_local.context = "['buscar_trailer']"
                if not item_local.infoLabels['poster_path']:
                    item_local.thumbnail = item_local.infoLabels['thumbnail']
                
                # Extraemos números de temporada y episodio
                try:
                    item_local.contentSeason = int(season_num)
                except:
                    item_local.contentSeason = 1
                try:
                    item_local.contentEpisodeNumber = int(episode_num)
                except:
                    item_local.contentEpisodeNumber = 0

                item_local.title = '%sx%s - ' % (str(item_local.contentSeason), 
                            str(item_local.contentEpisodeNumber).zfill(2))

                # Procesamos Calidad
                if scrapedquality:
                    item_local.quality = scrapertools.remove_htmltags(scrapedquality)       # iniciamos calidad
                    if '[720p]' in scrapedquality.lower() or '720p' in scrapedquality.lower():
                        item_local.quality = '720p'
                    if '[1080p]' in scrapedquality.lower() or '1080p' in scrapedquality.lower():
                        item_local.quality = '1080p'
                    if '4k' in scrapedquality.lower():
                        item_local.quality = '4K'
                    if '3d' in scrapedquality.lower() and not '3d' in item_local.quality.lower():
                        item_local.quality += ', 3D'
                if not item_local.quality:
                    item_local.quality = '720p'
                
                # Comprobamos si hay más de un enlace por episodio, entonces los agrupamos
                if len(itemlist) > 0 and item_local.contentSeason == itemlist[-1].contentSeason \
                            and item_local.contentEpisodeNumber == itemlist[-1].contentEpisodeNumber \
                            and itemlist[-1].contentEpisodeNumber != 0:         # solo guardamos un episodio ...
                    if itemlist[-1].quality:
                        if item_local.quality not in itemlist[-1].quality:
                            itemlist[-1].quality += ", " + item_local.quality   # ... pero acumulamos las calidades
                    else:
                        itemlist[-1].quality = item_local.quality
                    itemlist[-1].matches.append(item_local.matches[0])          # Salvado Matches en el episodio anterior
                    continue                                                    # ignoramos el episodio duplicado
                
                if season_display > 0:                                          # Son de la temporada estos episodios?
                    if item_local.contentSeason > season_display:
                        break
                    elif item_local.contentSeason < season_display:
                        continue
                        
                if modo_ultima_temp_alt and item.library_playcounts:            # Si solo se actualiza la última temporada de Videoteca
                    if item_local.contentSeason < max_temp:
                        continue                                                # Sale del bucle actual del FOR

                itemlist.append(item_local.clone())

                #logger.debug(item_local)
            
    if len(itemlist) > 1:
        itemlist = sorted(itemlist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))       #clasificamos
        
    if item.season_colapse and not item.add_videolibrary:                       #Si viene de listado, mostramos solo Temporadas
        item, itemlist = generictools.post_tmdb_seasons(item, itemlist)

    if not item.season_colapse:                                                 #Si no es pantalla de Temporadas, pintamos todo
        # Pasada por TMDB y clasificación de lista por temporada y episodio
        tmdb.set_infoLabels(itemlist, True, idioma_busqueda=idioma)

        #Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
        item, itemlist = generictools.post_tmdb_episodios(item, itemlist)
    
    #logger.debug(item)

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
        item.url = host + 'buscar/%s?buscar=' % page + texto
        item.extra = 'search'

        if texto:
            return listado(item)
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
            if channel == 'yestorrent':
                item.url = host + "Descargar-peliculas-completas/page/1/"
            item.extra = "peliculas"
            item.extra2 = "novedades"
            item.action = "listado"
            itemlist.extend(listado(item))
                
        if len(itemlist) > 0 and (">> Página siguiente" in itemlist[-1].title or "Pagina siguiente >>" in itemlist[-1].title):
            itemlist.pop()
        
        if categoria in ['series', 'latino', 'torrent']:
            item.category_new= 'newest'
            item.url = host + "series/page/1/"
            item.extra = "series"
            item.extra2 = "novedades"
            item.action = "listado"
            itemlist.extend(listado(item))

        if len(itemlist) > 0 and (">> Página siguiente" in itemlist[-1].title or "Pagina siguiente >>" in itemlist[-1].title):
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc(1))
        return []

    return itemlist
