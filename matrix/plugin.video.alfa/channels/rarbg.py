# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                               # Usamos el nativo de PY2 que es más rápido

import re
import time

from channelselector import get_thumb
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import tmdb
from lib import generictools
from channels import filtertools
from channels import autoplay


#IDIOMAS = {'CAST': 'Castellano', 'LAT': 'Latino', 'VO': 'Version Original'}
IDIOMAS = {'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['torrent']

canonical = {
             'channel': 'rarbg', 
             'host': config.get_setting("current_host", 'rarbg', default=''), 
             'host_alt': ["https://rarbgaccessed.org/", "https://rarbgget.org/", "https://proxyrarbg.org/"], 
             'host_black_list': ["https://rarbgmirror.org/"], 
             'host_black_list': [], 
             'status': 'SIN CANONICAL NI DOMINIO', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'

__modo_grafico__ = config.get_setting('modo_grafico', channel)
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)        #Actualización sólo últ. Temporada?
timeout = config.get_setting('timeout_downloadpage', channel)


def mainlist(item):
    logger.info()
    itemlist = []
    
    thumb_cartelera = get_thumb("now_playing.png")
    thumb_pelis = get_thumb("channels_movie.png")
    thumb_pelis_hd = get_thumb("channels_movie_hd.png")
    thumb_pelis_VO = get_thumb("channels_vos.png")
    thumb_series = get_thumb("channels_tvshow.png")
    thumb_series_hd = get_thumb("channels_tvshow_hd.png")
    thumb_series_VOD = get_thumb("videolibrary_tvshow.png")
    thumb_generos = get_thumb("genres.png")
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]NOTA: Esta web puede considerar una intrusión[/COLOR]", folder=False, thumbnail=thumb_separador))
    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]más de 1 usuario o 10 accesos por IP/Router.[/COLOR]", folder=False, thumbnail=thumb_separador))
    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Si es bloqueado, se reintentará automáticamente[/COLOR]", folder=False, thumbnail=thumb_separador))
    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Si sigue bloqueado, renueve la IP en el Router[/COLOR]", folder=False, thumbnail=thumb_separador))
    
    itemlist.append(Item(channel=item.channel, title="Películas", action="listado", url=host + "torrents.php?category=movies&search=&order=data&by=DESC", thumbnail=thumb_pelis_VO, extra="peliculas"))
    itemlist.append(Item(channel=item.channel, title="    - Calidades", action="calidades", url=host + "torrents.php?category=movies&search=&order=data&by=DESC", thumbnail=thumb_pelis_hd, extra="peliculas"))
    #itemlist.append(Item(channel=item.channel, title="    - Géneros", action="generos", url=host + "catalog/movies/", thumbnail=thumb_generos, extra="peliculas"))

    itemlist.append(Item(channel=item.channel, title="Series", action="listado", url=host + "torrents.php?category=2;18;41;49&search=&order=data&by=DESC", thumbnail=thumb_series_VOD, extra="series"))
    itemlist.append(Item(channel=item.channel, title="    - Calidades", action="calidades", url=host + "torrents.php?category=2;18;41;49&search=&order=data&by=DESC", thumbnail=thumb_series_hd, extra="series"))
    #itemlist.append(Item(channel=item.channel, title="    - Géneros", action="generos", url=host + "catalog/tv/", thumbnail=thumb_generos, extra="series"))
    
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + "?s=%s", thumbnail=thumb_buscar, extra="search"))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", folder=False, thumbnail=thumb_separador))
    
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", thumbnail=thumb_settings))
    
    autoplay.show_option(item.channel, itemlist)            #Activamos Autoplay

    return itemlist
    
    
def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return


def calidades(item):
    logger.info()
    itemlist = []

    data = ''
    patron = '<div align="[^"]+"><div style="[^"]+" id="divadvsearch">(.*?)<\/a><\/div><\/div><\/form><\/div>'
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               patron=patron, item=item, itemlist=[], 
                                                               quote_rep=False, check_blocked_IP=True)      # Descargamos la página
    if not response.sucess or itemlist:                                         # Si ERROR o lista de errores lo reintentamos con otro Host
        return itemlist                                                         # ... Salimos

    data = scrapertools.find_single_match(data, patron)                         #Seleccionamos el bloque
    patron = '<div class="divadvscat"><input class="inputadvscat" type="checkbox" '
    patron += 'name="category\[.*?\]" value="[^"]+"\s*(?:.*?)?\/> <a href="([^"]+)">(.*?)<\/a>\s*<\/div>\s*'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if not matches:
        logger.error("ERROR 02: SUBMENU: Ha cambiado la estructura de la Web " + " / PATRON: " + patron + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.category + ': ERROR 02: SUBMENU: Ha cambiado la estructura de la Web.  Reportar el error con el log'))
        return itemlist                                 #si no hay más datos, algo no funciona, pintamos lo que tenemos

    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)
    
    itemlist.append(item.clone(action="listado", title="ALL", extra2="calidades"))
    
    for scrapedurl, scrapedtitle in matches:
        if not "Mov" in scrapedtitle and item.extra == 'peliculas':
            continue
        if not "TV" in scrapedtitle and item.extra == 'series':
            continue
        
        title = scrapedtitle.strip().replace('Movs/', '').replace('Movies/', '')
        url = urlparse.urljoin(host, scrapedurl + "&search=&order=data&by=DESC")

        itemlist.append(item.clone(action="listado", title=title, url=url, extra2="calidades"))

    return itemlist

    
def listado(item):
    logger.info()
    itemlist = []
    item.category = categoria

    #logger.debug(item)
    
    curr_page = 1                                                               # Página inicial
    last_page = 99999                                                           # Última página inicial
    if item.curr_page:
        curr_page = int(item.curr_page)                                         # Si viene de una pasada anterior, lo usamos
        del item.curr_page                                                      # ... y lo borramos
    if item.last_page:
        last_page = int(item.last_page)                                         # Si viene de una pasada anterior, lo usamos
        del item.last_page                                                      # ... y lo borramos
    
    cnt_tot = 40                                                                # Poner el num. máximo de items por página
    cnt_title = 0                                                               # Contador de líneas insertadas en Itemlist
    inicio = time.time()                                    # Controlaremos que el proceso no exceda de un tiempo razonable
    fin = inicio + 3                                                            # Después de este tiempo pintamos (segundos)
    timeout_search = timeout                                                    # Timeout para descargas
    if item.extra == 'search':
        timeout_search = timeout * 2                                            # Timeout un poco más largo para las búsquedas
        if timeout_search < 5:
            timeout_search = 5                                                  # Timeout un poco más largo para las búsquedas

    #Sistema de paginado para evitar páginas vacías o semi-vacías en casos de búsquedas con series con muchos episodios
    title_lista = []                            # Guarda la lista de series que ya están en Itemlist, para no duplicar lineas
    if item.title_lista:                                    # Si viene de una pasada anterior, la lista ya estará guardada
        title_lista.extend(item.title_lista)                                    # Se usa la lista de páginas anteriores en Item
        del item.title_lista                                                    # ... limpiamos
        
    if not item.extra2:                                                         # Si viene de Catálogo o de Alfabeto
        item.extra2 = ''
    
    next_page_url = item.url
    #Máximo num. de líneas permitidas por TMDB. Máx de 3 segundos por Itemlist para no degradar el rendimiento
    while cnt_title <= cnt_tot * 0.50 and curr_page <= last_page and fin > time.time():
    
        # Descarga la página
        data = ''
        data, response, item, itemlist = generictools.downloadpage(next_page_url, timeout=timeout_search, canonical=canonical, 
                                                                   item=item, itemlist=itemlist, 
                                                                   quote_rep=False, check_blocked_IP=True)      # Descargamos la página
        data = re.sub(r"&nbsp;", "", data)
        # Verificamos si ha cambiado el Host
        if response.host:
            next_page_url = response.url_new
        
        curr_page += 1                                                          # Apunto ya a la página siguiente
        if not data and not item.extra2:                                        #Si la web está caída salimos sin dar error
            if len(itemlist) > 1:                                               # Si hay algo que pintar lo pintamos
                last_page = 0
                break
            logger.error("ERROR 01: LISTADO: La Web no responde o ha cambiado de URL: " + next_page_url + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + 
                        ': ERROR 01: LISTADO:.  La Web no responde o ha cambiado de URL.' 
                        + ' Si la Web está activa, reportar el error con el log'))
            return itemlist                                                     # Si no hay nada más, salimos directamente

        #Patrón para todo, incluido búsquedas en cualquier caso
        patron = '<tr class="lista2"><td align="(?:[^"]+)?"\s*class="(?:[^"]+)?"'
        patron += '\s*width="(?:[^"]+)?"\s*style="(?:[^"]+)?"><a href="[^"]+">'
        patron += '<img src="([^"]+)?"\s*border="(?:[^"]+)?"\s*alt="(?:[^"]+)?"\s*\/>'
        patron += '<\/a><\/td><td\s*align="(?:[^"]+)?"\s*class="(?:[^"]+)?"><a onmouseover="'
        patron += '(?:[^"]+)?"\s*onmouseout="(?:[^"]+)?"\s*href="[^"]+" title="[^"]+"'
        patron += '>([^<]+)<\/a>\s*<a href="([^"]+)"><img src="[^"]+"\s*border="'
        patron += '(?:[^"]+)?"\s*alt="(?:[^"]+)?"\s*><\/a>\s*(?:<a href="([^"]+)">'
        patron += '<img src="[^"]+"\s*border="(?:[^"]+)?"\s*alt="(?:[^"]+)?"\s*><\/a>)?'
        patron += '\s*<br><span.*?<\/span>\s*<\/td><td align="(?:[^"]+)?"\s*width="'
        patron += '(?:[^"]+)?"\s*class="(?:[^"]+)?">.*?<\/td><td align="(?:[^"]+)?"\s*'
        patron += 'width="(?:[^"]+)?"\s*class="(?:[^"]+)?">([^<]+)?<\/td><td align="'
        patron += '(?:[^"]+)?"\s*width="(?:[^"]+)?"\s*class="(?:[^"]+)?">\s*'
        patron += '<font color="(?:[^"]+)?">(\d+)?<\/font>'
        patron = '<tr class="lista2"><td align="(?:[^"]+)?"\s*class="(?:[^"]+)?"\s*width="(?:[^"]+)?"\s*style="(?:[^"]+)?"><a href="[^"]+"><img src="([^"]+)?"\s*border="(?:[^"]+)?"\s*alt="(?:[^"]+)?"\s*\/><\/a><\/td><td\s*align="(?:[^"]+)?"\s*class="(?:[^"]+)?"><a onmouseover="(?:[^"]+)?"\s*onmouseout="(?:[^"]+)?"\s*href="[^"]+" title="[^"]+">([^<]+)<\/a>\s*<a href="([^"]+)"><img src="[^"]+"\s*border="(?:[^"]+)?"\s*alt="(?:[^"]+)?"\s*><\/a>\s*(?:<a href="([^"]+)"><img src="[^"]+"\s*border="(?:[^"]+)?"\s*alt="(?:[^"]+)?"\s*><\/a>)?\s*<br><span.*?<\/span>\s*<\/td><td align="(?:[^"]+)?"\s*width="(?:[^"]+)?"\s*class="(?:[^"]+)?">.*?<\/td><td align="(?:[^"]+)?"\s*width="(?:[^"]+)?"\s*class="(?:[^"]+)?">([^<]+)?<\/td><td align="(?:[^"]+)?"\s*width="(?:[^"]+)?"\s*class="(?:[^"]+)?">\s*<font color="(?:[^"]+)?">(\d+)?<\/font>'
            
        matches = re.compile(patron, re.DOTALL).findall(data)
        if not matches and item.extra != 'search':                                  #error
            logger.error("ERROR 02: LISTADO: Ha cambiado la estructura de la Web " + " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 02: LISTADO: Ha cambiado la estructura de la Web.  Reportar el error con el log'))
            break                                       #si no hay más datos, algo no funciona, pintamos lo que tenemos
        if not matches and item.extra == 'search':                                  #búsqueda vacía
            return itemlist                                                         #Salimos
        
        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)
        
        #Buscamos la próxima y la última página
        patron_next = '<a href="([^"]+page=(\d+))" title="next page">'
        if item.extra == 'search':
            patron_last = '<a href="[^"]+"\s*title="page\s*\d+">\d+<\/a>\s*<b>(\d+)<\/b><\/div><\/div><\/td>'
        else:
            patron_last = 'title="previous page"[^<]+<\/a>\s*<a href="[^>]+>(\d+)<\/a>'

        try:
            next_page_url, next_page = scrapertools.find_single_match(data, patron_next)
            next_page = int(next_page)
            next_page_url = item.url + '&page=' + str(next_page)
        except:                                                                         #Si no lo encuentra, lo ponemos a 1
            #logger.error('ERROR 03: LISTADO: Al obtener la paginación: ' + patron_next + ' / ' + patron_last + ' / ' + scrapertools.find_single_match(data, "<ul class=\"pagination\">.*?<\/span><\/a><\/li><\/ul><\/nav><\/div><\/div><\/div>"))
            next_page = 1
        #logger.debug('curr_page: ' + str(curr_page) + ' / next_page: ' + str(next_page) + ' / last_page: ' + str(last_page))
        
        if last_page == 99999:                                                          #Si es el valor inicial, buscamos
            if item.extra == 'search':
                last_page = 99
            try:
                data_last = ''
                data_last, response, item, itemlist = generictools.downloadpage(item.url + '&page=%s' % last_page, timeout=timeout_search, 
                                                                                quote_rep=False, item=item, itemlist=itemlist)
                data_last = re.sub(r"&nbsp;", "", data_last)
                last_page = int(scrapertools.find_single_match(data_last, patron_last)) #lo cargamos como entero
            except:                                                                     #Si no lo encuentra, lo ponemos a 1
                #logger.error('ERROR 03: LISTADO: Al obtener la paginación: ' + patron_next + ' / ' + patron_last + ' / ' + scrapertools.find_single_match(data, "<ul class=\"pagination\">.*?<\/span><\/a><\/li><\/ul><\/nav><\/div><\/div><\/div>"))
                last_page = next_page
            #logger.debug('curr_page: ' + str(curr_page) + ' / next_page: ' + str(next_page) + ' / last_page: ' + str(last_page))
        
        #Empezamos el procesado de matches
        for scrapedthumbnail, scrapedtitle, scrapedurl, scrapedepisodes, scrapedsize, scrapedseeds in matches:
            
            title = scrapedtitle
            if scrapedepisodes:
                url = scrapedepisodes
            else:
                url = scrapedurl
            size = scrapedsize
            
            # Slugify, pero más light
            title = title.replace("á", "a").replace("é", "e").replace("í", "i")\
                    .replace("ó", "o").replace("ú", "u").replace("ü", "u")\
                    .replace("ï¿½", "ñ").replace("Ã±", "ñ")
            title = scrapertools.decode_utf8_error(title)

            if scrapedurl in title_lista:                                   #Si ya hemos procesado el título, lo ignoramos
                continue
            else:
                title_lista += [scrapedurl]                                 #la añadimos a la lista de títulos
            
            #cnt_title += 1
            item_local = item.clone()                                       #Creamos copia de Item para trabajar
            if item_local.tipo:                                             #... y limpiamos
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
                
            title_subs = []                                                 #creamos una lista para guardar info importante
            item_local.language = ['VO']                                            #creamos lista para los idiomas
            item_local.quality = ''                                                 #iniciamos calidad
            item_local.thumbnail = scrapedthumbnail                                 #iniciamos thumbnail

            if item.extra == 'search':
                if scrapedepisodes:
                    item_local.extra = 'series'
                else:
                    item_local.extra = 'peliculas'
                
            item_local.url = urlparse.urljoin(host, url)                            #guardamos la url final
            if item_local.extra != 'series':
                item_local.url += '&order=size&by=ASC'                              #guardamos la url final
            item_local.context = "['buscar_trailer']"
            
            item_local.contentType = "movie"                                        #por defecto, son películas
            item_local.action = "findvideos"
            
            #Analizamos los formatos de la películas
            if item_local.extra == 'peliculas':
                patron_title = '(.*?)\.([1|2][9|0]\d{2})?\.(.*?)(?:-.*?)?$'
                if not scrapertools.find_single_match(title, patron_title):
                    logger.error('ERROR tratando título PELI: ' + title)
                    continue
                try:
                    title, year, item_local.quality = scrapertools.find_single_match(title, patron_title)
                except:
                    title = scrapedtitle
                    year = ''
                    item_local.quality = ''
                title = title.replace('.', ' ')
                item_local.quality = item_local.quality.replace('.', ' ')

            #Analizamos los formatos de series, temporadas y episodios
            elif item_local.extra == 'series':
                patron_title = '(.*?)(\.[1|2][9|0]\d{2})?\.S\d{2}.*?\.([\d|A-Z]{2}.*?)(?:-.*?)?$'
                if not scrapertools.find_single_match(title, patron_title):
                    patron_title = '(.*?)\.*([1|2][9|0]\d{2})?(?:\.\d{2}\.\d{2}).*?\.([\d|A-Z]{2}.*?)(?:-.*?)?$'
                    if not scrapertools.find_single_match(title, patron_title):
                        logger.error('ERROR tratando título SERIE: ' + title)
                        continue
                try:
                    title, year, item_local.quality = scrapertools.find_single_match(title, patron_title)
                except:
                    title = scrapedtitle
                    year = ''
                    item_local.quality = ''
                title = title.replace('.', ' ')
                item_local.quality = item_local.quality.replace('.', ' ')
                year = '-'
                
                item_local.contentType = "tvshow"
                item_local.action = "episodios"
                item_local.season_colapse = True                            #Muestra las series agrupadas por temporadas

            #Limpiamos el título de la basura innecesaria
            title = re.sub(r'(?i)TV|Online', '', title).strip()
            item_local.quality = re.sub(r'(?i)proper|unrated|directors|cut|german|repack|internal|real|korean|extended|masted|docu|oar|super|duper|amzn|uncensored|hulu', '', item_local.quality).strip()

            #Analizamos el año.  Si no está claro ponemos '-'
            try:
                year_int = int(year)
                if year_int >= 1940 and year_int <= 2050:
                    item_local.infoLabels["year"] = year_int
                else:
                    item_local.infoLabels["year"] = '-'
            except:
                item_local.infoLabels["year"] = '-'
            
            #Terminamos de limpiar el título
            title = re.sub(r'[\(|\[]\s+[\)|\]]', '', title)
            title = title.replace('()', '').replace('[]', '').strip().lower().title()
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
            if item_local.contentSeason and (item_local.contentType == "season" or item_local.contentType == "tvshow"):
                item_local.contentSeason_save = item_local.contentSeason
                del item_local.infoLabels['season']

            #Ahora se filtra por idioma, si procede, y se pinta lo que vale
            if config.get_setting('filter_languages', channel) > 0:     #Si hay idioma seleccionado, se filtra
                itemlist = filtertools.get_link(itemlist, item_local, list_language)
            else:
                itemlist.append(item_local.clone())                     #Si no, pintar pantalla
            
            cnt_title = len(itemlist)                                   #Contador de líneas añadidas
            
            #logger.debug(item_local)

    #Pasamos a TMDB la lista completa Itemlist
    tmdb.set_infoLabels(itemlist, __modo_grafico__, idioma_busqueda='es,en')
    
    #Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
    item, itemlist = generictools.post_tmdb_listado(item, itemlist)

    # Si es necesario añadir paginacion
    if curr_page <= last_page:
        if last_page:
            title = '%s de %s' % (curr_page-1, last_page)
        else:
            title = '%s' % curr_page-1

        itemlist.append(Item(channel=item.channel, action="listado", title=">> Página siguiente " + title, title_lista=title_lista, url=next_page_url, extra=item.extra, extra2=item.extra2, last_page=str(last_page), curr_page=str(curr_page)))

    return itemlist

    
def findvideos(item):
    logger.info()
    itemlist = []
    itemlist_t = []                                                                 #Itemlist total de enlaces
    itemlist_f = []                                                                 #Itemlist de enlaces filtrados
    if not item.language:
        item.language = ['VO']                                                      #VO por defecto
    matches = []
    item.category = categoria

    #logger.debug(item)

    #Bajamos los datos de la página
    data = ''
    patron = '<tr class="lista2">\s*<td align="(?:[^"]+)?"\s*class="(?:[^"]+)?'
    patron += '"\s*width="(?:[^"]+)?"\s*style="(?:[^"]+)?">\s*<a href="[^"]+">\s*'
    patron += '<img src="([^"]+)?"\s*border="(?:[^"]+)?"\s*alt="(?:[^"]+)?"\s*\/><\/a><\/td>\s*'
    patron += '<td\s*align="(?:[^"]+)?"(?:\s*width="[^"]+")?\s*class="(?:[^"]+)?">\s*'
    patron += '<a onmouseover="(?:[^"]+)?"\s*onmouseout="(?:[^"]+)?"\s*href="([^"]+)"'
    patron += ' title="[^"]+">(.*?)<\/a>\s*<a href="[^"]+">\s*<img src="[^"]+"\s*'
    patron += 'border="(?:[^"]+)?"\s*alt="(?:[^"]+)?"\s*><\/a>(?:\s*<a.*?<\/a>)?'
    patron += '\s*<br><span.*?<\/span>\s*<\/td>\s*<td align="(?:[^"]+)?"\s*width="'
    patron += '(?:[^"]+)?"\s*class="(?:[^"]+)?">.*?<\/td>\s*<td align="(?:[^"]+)?'
    patron += '"\s*width="(?:[^"]+)?"\s*class="(?:[^"]+)?">(.*?)?<\/td>\s*<td align="(?:[^"]+)?'
    patron += '"\s*width="(?:[^"]+)?"\s*class="(?:[^"]+)?">\s*<font color="(?:[^"]+)?">(\d+)?<\/font>'
        
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               patron=patron, item=item, itemlist=itemlist, 
                                                               quote_rep=False, check_blocked_IP=True)
    if not data or response.code in [999, 99]:                                  # Si ERROR o lista de errores lo reintentamos con otro Host
        return itemlist                                                         # ... Salimos

    matches = re.compile(patron, re.DOTALL).findall(data)
    if not matches:                                                             #error
        logger.error("ERROR 02: FINDVIDEOS: No hay enlaces o ha cambiado la estructura de la Web " + " / PATRON: " + patron + data)
        itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 02: FINDVIDEOS: No hay enlaces o ha cambiado la estructura de la Web.  Verificar en la Web esto último y reportar el error con el log', folder=False))
        return itemlist                         #si no hay más datos, algo no funciona, pintamos lo que tenemos

    #logger.debug("PATRON: " + patron)
    #logger.debug(matches)
    #logger.debug(data)

    #Llamamos al método para crear el título general del vídeo, con toda la información obtenida de TMDB
    item, itemlist = generictools.post_tmdb_findvideos(item, itemlist)

    #Ahora tratamos los enlaces .torrent con las diferentes calidades
    for scrapedthumbnail, scrapedurl, scrapedtitle, scrapedsize, scrapedseeds in matches:
        #Generamos una copia de Item para trabajar sobre ella
        item_local = item.clone()
        title = scrapedtitle

        #Analizamos los formatos de la películas y series
        if item_local.contentType == 'movie':
            patron_title = '(.*?)\.([1|2][9|0]\d{2})?\.(.*?)(?:-.*?)?$'
            if not scrapertools.find_single_match(title, patron_title):
                continue
        else:
            patron_title = '(.*?)(\.[1|2][9|0]\d{2})?\.S\d{2}.*?\.([\d|A-Z]{2}.*?)(?:-.*?)?$'
            if not scrapertools.find_single_match(title, patron_title):
                patron_title = '(.*?)\.*([1|2][9|0]\d{2})?(?:\.\d{2}\.\d{2}).*?\.([\d|A-Z]{2}.*?)(?:-.*?)?$'
                if not scrapertools.find_single_match(title, patron_title):
                    continue
        
        try:
            title, year, item_local.quality = scrapertools.find_single_match(title, patron_title)
        except:
            title = scrapedtitle
            year = ''
            item_local.quality = ''
        title = title.replace('.', ' ')
        item_local.quality = item_local.quality.replace('.', ' ')
        item_local.quality = re.sub(r'(?i)proper|unrated|directors|cut|german|repack|internal|real|korean|extended|masted|docu|oar|super|duper|amzn|uncensored|hulu', '', item_local.quality).strip()
        
        #Buscamos si ya tiene tamaño, si no, los buscamos en el archivo .torrent
        size = scrapedsize
        if size:
            item_local.title = '%s [%s]' % (item_local.title, size)             #Agregamos size al final del título
            size = size.replace('GB', 'G·B').replace('Gb', 'G·b').replace('MB', 'M·B')\
                        .replace('Mb', 'M·b').replace('.', ',')
            item_local.torrent_info = '%s, ' % size                             #Agregamos size

        #Añadimos los seeds en calidad, como información adicional
        if scrapedseeds:
            item_local.torrent_info += 'Seeds: %s' % scrapedseeds               #Agregamos seeds
        if not item.unify:
                item_local.torrent_info = '[%s]' % item_local.torrent_info.strip().strip(',')

        #Ahora pintamos el link del Torrent
        item_local.url = urlparse.urljoin(host, scrapedurl)
        item_local.title = '[[COLOR yellow]?[/COLOR]] [COLOR yellow][Torrent][/COLOR] ' \
                        + '[COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR] %s' % \
                        (item_local.quality, str(item_local.language),  \
                        item_local.torrent_info)                                #Preparamos título de Torrent
        
        #Preparamos título y calidad, quitamos etiquetas vacías
        item_local.title = re.sub(r'\s?\[COLOR \w+\]\[\[?\s?\]?\]\[\/COLOR\]', '', item_local.title)    
        item_local.title = re.sub(r'\s?\[COLOR \w+\]\s?\[\/COLOR\]', '', item_local.title)
        item_local.title = item_local.title.replace("--", "").replace("[]", "").replace("()", "").replace("(/)", "").replace("[/]", "").strip()
        item_local.quality = re.sub(r'\s?\[COLOR \w+\]\[\[?\s?\]?\]\[\/COLOR\]', '', item_local.quality)
        item_local.quality = re.sub(r'\s?\[COLOR \w+\]\s?\[\/COLOR\]', '', item_local.quality)
        item_local.quality = item_local.quality.replace("--", "").replace("[]", "").replace("()", "").replace("(/)", "").replace("[/]", "").strip()
        
        item_local.alive = "??"                                                     #Calidad del link sin verificar
        item_local.action = "play"                                                  #Visualizar vídeo
        item_local.server = "torrent"                                               #Seridor Torrent
        
        itemlist_t.append(item_local.clone())                                       #Pintar pantalla, si no se filtran idiomas
        
        # Requerido para FilterTools
        if config.get_setting('filter_languages', channel) > 0:                     #Si hay idioma seleccionado, se filtra
            itemlist_f = filtertools.get_link(itemlist_f, item_local, list_language)  #Pintar pantalla, si no está vacío

        #logger.debug("TORRENT: " + scrapedurl + " / title gen/torr: " + item.title + " / " + item_local.title + " / calidad: " + item_local.quality + " / content: " + item_local.contentTitle + " / " + item_local.contentSerieName)
        #logger.debug(item_local)

    if len(itemlist_f) > 0:                                                     #Si hay entradas filtradas...
        itemlist.extend(itemlist_f)                                             #Pintamos pantalla filtrada
    else:                                                                       
        if config.get_setting('filter_languages', channel) > 0 and len(itemlist_t) > 0: #Si no hay entradas filtradas ...
            thumb_separador = get_thumb("next.png")                             #... pintamos todo con aviso
            itemlist.append(Item(channel=item.channel, url=host, title="[COLOR red][B]NO hay elementos con el idioma seleccionado[/B][/COLOR]", thumbnail=thumb_separador, folder=False))
        itemlist.extend(itemlist_t)                                             #Pintar pantalla con todo si no hay filtrado
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)                                              #Lanzamos Autoplay
    
    return itemlist
    
    
def play(item):                                 #Permite preparar la descarga de los .torrents y subtítulos externos
    logger.info()
    itemlist = []
    headers = []
    from core import downloadtools
    from core import ziptools
    from core import filetools
    
    #buscamos la url del .torrent
    patron = '<tr><td align="(?:[^"]+)?"\s*class="(?:[^"]+)?"\s*width="(?:[^"]+)?">'
    patron += '\s*Torrent:<\/td><td class="(?:[^"]+)?">\s*<img src="(?:[^"]+)?"\s*'
    patron += 'alt="(?:[^"]+)?"\s*border="(?:[^"]+)?"\s*\/>\s*<a onmouseover="'
    patron += '(?:[^"]+)?"\s*onmouseout="(?:[^"]+)?" href="([^"]+)".*?<\/a>'
    
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, 
                                                               patron=patron, item=item, itemlist=[], 
                                                               quote_rep=False, check_blocked_IP=True)
    if not data or response.code in [999, 99]:                                  # Si ERROR o lista de errores lo reintentamos con otro Host
        return itemlist                                                         # ... Salimos

    item.url = urlparse.urljoin(host, scrapertools.find_single_match(data, patron))
    
    #buscamos subtítulos en español
    patron = '<tr><td align="(?:[^"]+)?"\s*class="(?:[^"]+)?"\s*>\s*Subs.*?<\/td><td class="(?:[^"]+)?"\s*>(.*?)(?:<br\/>)?<\/td><\/tr>'
    data_subt = scrapertools.find_single_match(data, patron)
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
            filetools.rmtree(videolibrary_path)
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
    
    item = generictools.update_title(item) #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels
    
    #Volvemos a la siguiente acción en el canal
    return item

    
def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    
    try:
        item.url = host + 'torrents.php?category=2;18;41;49;14;48;17;44;45;47;50;51;52;42;46&search=%s' % texto
        item.extra = 'search'

        if texto != '':
            return listado(item)
    except:
        import sys
        import traceback
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc())
        return []
 