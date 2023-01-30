# -*- coding: utf-8 -*-

from __future__ import division
from past.utils import old_div
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urllib
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido
    import urllib

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


IDIOMAS = {'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['torrent']

canonical = {
             'channel': 'divxtotal', 
             'host': config.get_setting("current_host", 'divxtotal', default=''), 
             'host_alt': ["https://www.divxtotal.pl/"], 
             'host_black_list': ["https://www.divxtotal.cat/", 
                                 "https://www.divxtotal.fi/", "https://www.divxtotal.dev/", "https://www.divxtotal.ac/", 
                                 "https://www.divxtotal.re/", "https://www.divxtotal.pm/", "https://www.divxtotal.nl/"], 
             'pattern': '<li>\s*<a\s*href="([^"]+)"\s*>\S*\/a><\/li>', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'
host_torrent = host[:-1]
movies_sufix = 'peliculas-hd/'
series_sufix = 'series/'

__modo_grafico__ = config.get_setting('modo_grafico', channel)                  # búsqueda TMDB ?
IDIOMAS_TMDB = {0: 'es', 1: 'en', 2: 'es,en'}
idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', channel)]    # Idioma base para TMDB
idioma_busqueda_VO = IDIOMAS_TMDB[2]                                                # Idioma para VO
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel) # Actualización sólo últ. Temporada?
timeout = config.get_setting('timeout_downloadpage', channel)
season_colapse = config.get_setting('season_colapse', channel)                  # Season colapse?
filter_languages = config.get_setting('filter_languages', channel)              # Filtrado de idiomas?
forced_proxy_opt = 'ProxyCF'


def mainlist(item):
    logger.info()
    itemlist = []
    
    thumb_cartelera = get_thumb("now_playing.png")
    thumb_pelis = get_thumb("channels_movie.png")
    thumb_pelis_hd = get_thumb("channels_movie_hd.png")
    thumb_series = get_thumb("channels_tvshow.png")
    
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Novedades", action="novedades", 
                url=host, thumbnail=thumb_cartelera, extra2="novedades", category=categoria,))
    
    itemlist.append(Item(channel=item.channel, title="Películas @todas", action="submenu", 
                url=host, thumbnail=thumb_pelis, extra="peliculas", category=categoria, 
                extra2=">Pel\xc3\xadculas<"))
    itemlist.append(Item(channel=item.channel, title="    - Películas HD", action="submenu", 
                url=host, thumbnail=thumb_pelis_hd, extra="peliculas", category=categoria, 
                extra2=">Pel\xc3\xadculas&nbsp;HD<"))
    itemlist.append(Item(channel=item.channel, title="    - Películas DVDR", action="submenu", 
                url=host, thumbnail=thumb_pelis_hd, extra="peliculas", category=categoria, 
                extra2=">Pel\xc3\xadculas&nbsp;DVDR<"))
    itemlist.append(Item(channel=item.channel, title="    - Películas 3D", action="submenu", 
                url=host, thumbnail=thumb_pelis_hd, extra="peliculas", category=categoria, 
                extra2=">Pel\xc3\xadculas&nbsp;3D<"))

    itemlist.append(Item(channel=item.channel, title="Series", action="submenu", 
                url=host, thumbnail=thumb_series, extra="series", category=categoria, 
                extra2=">Series<"))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", 
                url=host, thumbnail=thumb_buscar, extra="search", category=categoria))

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
    logger.info()
    itemlist = []

    thumb_alfabeto = get_thumb("channels_movie_az.png")
    thumb_generos = get_thumb("genres.png")
    
    patron = '<ul\s*class="nav\s*navbar-nav"\s*>(.*?)<\/ul>'
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               patron=patron, item=item, itemlist=[])       # Descargamos la página
    
    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if not response.sucess or itemlist:                                         # Si ERROR o lista de errores lo reintentamos con otro Host
        return itemlist                                                         # ... Salimos

    # Seleccionamos bloque
    data_pal = scrapertools.find_single_match(data, patron)
    patron = '<li>\s*<a\s*href="([^"]+)"\s*(>\S*)\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data_pal)
    
    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)

    if not matches:
        logger.error("ERROR 02: SUBMENU: Ha cambiado la estructura de la Web " + 
                        " / PATRON: " + patron + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: SUBMENU: Ha cambiado la estructura de la Web.  '
                        + 'Reportar el error con el log'))
        return itemlist                                             # si no hay más datos, algo no funciona, pintamos lo que tenemos

    url = 'None'
    for scrapedurl, scrapedtitle in matches:
        thumb = item.thumbnail
        url = urlparse.urljoin(host, scrapedurl)
        if scrapedtitle.strip() == item.extra2 or scrapedtitle.strip() == item.extra2.replace('Ã­', 'í'):
            title = scrapedtitle.replace("&nbsp;", " ")
            title = scrapertools.slugify(title).title() + ' @todas'
            item.url = url
            del item.extra2

            itemlist.append(item.clone(title=title, action="listado", thumbnail=thumb, 
                             url=urlparse.urljoin(url, 'page/1/')))
            break

    if url != 'None':
        itemlist.append(item.clone(action="alfabeto", title="Alfabeto [A-Z]", thumbnail=thumb_alfabeto))    #Lista de Géneros
    
    if url != 'None' and item.extra == 'peliculas':
        itemlist.append(item.clone(action="", title="Géneros", thumbnail=thumb_generos))                    #Lista de Géneros
        itemlist = generos(item, itemlist, url)
    
    return itemlist
    
    
def generos(item, itemlist=[], url=''):
    logger.info()
    
    # Obtenemos el bloque a tratar
    patron = '<div\s*id="bloque_cat"(.*?)<\/div>\s*<\/div>\s*<\/div>'
    data, response, item, itemlist = generictools.downloadpage(url, timeout=timeout, canonical=canonical, 
                                                               patron=patron, item=item, itemlist=itemlist)     # Descargamos la página
    data = scrapertools.find_single_match(data, patron)
    
    # Buscamos los géneros
    patron = '<a\s*class="href_peliculas"\s*href="([^"]+)">\s*<button\s*class="categorias_peliculas">([^<]+)<\/button>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)
    if not matches:                                                             # Si no hay matches...
        logger.error("ERROR 02: GENEROS: Ha cambiado la estructura de la Web " + 
                        " / PATRON: " + patron + " / DATA: " + data)
        return itemlist                                                         # Salimos

    for scrapedurl, scrapedtitle in matches:
        url = urlparse.urljoin(host, scrapedurl)
        url = re.sub(r'\/+\?', '/page/1/?', url)
        #title = '     - %s' % scrapertools.slugify(scrapedtitle).strip().capitalize()   # Limpiamos de tildes y demás
        title = '     - %s' % scrapedtitle.strip().capitalize()

        itemlist.append(item.clone(action="listado", title=title, url=url, 
                    extra2='generos', thumbnail=get_thumb('%s' % title, auto=True)))    # Listado de géneros

    return itemlist


def alfabeto(item):
    logger.info()
    itemlist = []
    
    itemlist.append(item.clone(action="listado", title="0-9", url=item.url + 'page/1/?s=letra-0'))

    for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        itemlist.append(item.clone(action="listado", title=letra, url=item.url + 'page/1/?s=letra-%s' % letra.lower()))

    return itemlist


def novedades(item):
    logger.info()
    itemlist = []
    matches_def = []
    
    patron = '<div\s*class="row"\s*>\s*<div\s*class=[^>]*>([^<]*)<\/div>'
    patron += '(?:\s*<div[^>]*>)?\s*<a\s*onmouseover="[^"]*javascript:cambia_'
    patron += '(?:movies|series)\S*\("([^"]+)"\);"\s*href="([^"]+)"[^>]+>([^"]+)<\/a>'
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               patron=patron, item=item, itemlist=[])       # Descargamos la página
    
    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if not response.sucess or itemlist:                                         # Si ERROR o lista de errores lo reintentamos con otro Host
        return itemlist                                                         # ... Salimos

    matches = re.compile(patron, re.DOTALL).findall(data)
    
    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)

    if not matches:
        logger.error("ERROR 02: NOVEDADES: Ha cambiado la estructura de la Web " + 
                        " / PATRON: " + patron + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: NOVEDADES: Ha cambiado la estructura de la Web.  '
                        + 'Reportar el error con el log'))
        return itemlist                                             # si no hay más datos, algo no funciona, pintamos lo que tenemos

    for fecha, scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        fecha_date = fecha.split('-')
        if len(fecha_date) == 3:
            fecha_date = str(fecha_date[2]) + str(fecha_date[1]) + str(fecha_date[0])
        else:
            fecha_date = fecha

        matches_def.append((fecha_date, scrapedthumbnail, scrapedurl, scrapedtitle))
        
    if matches_def:
        item.matches = []
        size = ''
        cnt_tot = 30                                                            # Poner el num. máximo de items por página
        item.curr_page = 2
        item.last_page = 1
        item.last_page_print = int((item.last_page * (float(len(matches_def)) / float(cnt_tot))) + 0.999999999)
        item.page_factor = float(item.last_page_print) / float(item.last_page)
        for fecha, scrapedthumbnail, scrapedurl, scrapedtitle in sorted(matches_def, reverse=True):
            item.matches.append((scrapedurl, scrapedtitle, scrapedthumbnail, size))

    return listado(item)


def listado(item):                                                              # Listado principal y de búsquedas
    logger.info()
    
    itemlist = []

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
    if item.extra == 'search' and item.extra2 == 'episodios':                   # Si viene de episodio se quitan los límites
        cnt_tot = 999
        fin = inicio + 30

    #Sistema de paginado para evitar páginas vacías o semi-vacías en casos de búsquedas con series con muchos episodios
    title_lista = []                            # Guarda la lista de series que ya están en Itemlist, para no duplicar lineas
    if item.title_lista:                                    # Si viene de una pasada anterior, la lista ya estará guardada
        title_lista.extend(item.title_lista)                                    # Se usa la lista de páginas anteriores en Item
        del item.title_lista                                                    # ... limpiamos
    matches = []
        
    if not item.extra2:                                                         # Si viene de Catálogo o de Alfabeto
        item.extra2 = ''
        
    post = None
    if item.post:                                                               # Rescatamos el Post, si lo hay
        post = item.post
    referer = None
    if item.referer:                                                            # Rescatamos el Referer, si lo hay
        referer = item.referer
    headers = None
    if item.headers:                                                            # Rescatamos el Headers, si lo hay
        headers = item.headers
    
    next_page_url = item.url
    #Máximo num. de líneas permitidas por TMDB. Máx de 5 segundos por Itemlist para no degradar el rendimiento
    while (cnt_title < cnt_tot and curr_page <= last_page and fin > time.time()) or item.matches:
    
        # Descarga la página
        data = ''
        cnt_match = 0                                                           # Contador de líneas procesadas de matches
        if not item.matches:                                                    # si no viene de una pasada anterior, descargamos
            data, response, item, itemlist = generictools.downloadpage(next_page_url, headers=headers, canonical=canonical, 
                                                                       timeout=timeout_search, post=post, referer=referer, 
                                                                       item=item, itemlist=itemlist)        # Descargamos la página)
            # Verificamos si ha cambiado el Host
            if response.host:
                next_page_url = response.url_new
            
            curr_page += 1                                                      # Apunto ya a la página siguiente
            if not data:                                                        # Si la web está caída salimos sin dar error
                if len(itemlist) > 1:                                           # Si hay algo que pintar lo pintamos
                    last_page = 0
                    break
                logger.error("ERROR 01: LISTADO: La Web no responde o ha cambiado de URL: " + next_page_url + " / DATA: " + data)
                itemlist.append(item.clone(action='', title=item.channel.capitalize() + 
                            ': ERROR 01: LISTADO:.  La Web no responde o ha cambiado de URL.' 
                            + ' Si la Web está activa, reportar el error con el log'))
                return itemlist                                                 # Si no hay nada más, salimos directamente

        # Si es el valor inicial, salvamos data para el pié de página
        data_foot = ''
        if last_page == 99999:
            data_foot = data
        
        if item.extra == 'series':
            #Si son series completas, ponemos un patrón especializado
            patron = '<div\s*class=[^>]*>\s*<p\s*class=[^>]*>\s*<a\s*href="([^"]+)"'
            patron += '\s*title="([^"]+)"\s*>\s*<img\s*src="([^"]+)"[^>]*>\s*<\/a>'
            patron += '\s*<\/p>\s*<p\s*class=[^>]*>\s*<a\s*href="[^"]+"\s*title="([^"]+)"'
        else:
            #Patrón para todo, menos para Series completas, incluido búsquedas en cualquier caso
            patron = '<tr>\s*<td(?:\s*class="[^"]+")?>\s*<a\s*href="([^"]+)"\s*'
            patron += 'title="([^"]+)"[^<]*<\/a>\s*<\/td>\s*<td(?:\s*class="[^"]+")?'
            patron += '\s*>\s*(?:<a\s*href="[^"]+">)?\s*([^<]*)(?:<\/a>)?\s*<\/td>\s*'
            patron += '<td(?:\s*class="[^"]+")?>[^<]*<\/td>\s*<td(?:\s*class="[^"]+")?>'
            patron += '\s*([^<]*)<\/td>\s*<\/tr>'
        
        if not item.matches:                                                    # De pasada anterior o novedades?
            matches = re.compile(patron, re.DOTALL).findall(data)
        else:
            matches = item.matches
            del item.matches
            
        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)

        if not matches and not '<p>Lo sentimos, pero que esta buscando algo que no esta aqui. </p>' in data \
                        and not '<h2>Sin resultados</h2>' in data:              # error o fin
            logger.error("ERROR 02: LISTADO: Ha cambiado la estructura de la Web " 
                        + " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + 
                        ': ERROR 02: LISTADO: Ha cambiado la estructura de la Web.  ' 
                        + 'Reportar el error con el log'))
            last_page = 0
            break                                       #si no hay más datos, algo no funciona, pintamos lo que tenemos
        
        if not matches and item.extra == 'search':                              # búsqueda vacía
            if len(itemlist) > 0:                                               # Si hay algo que pintar lo pintamos
                last_page = 0
                break
            return itemlist                                                     # Salimos
        
        #Buscamos la última página
        if last_page == 99999:                                                  # Si es el valor inicial, buscamos
            patron_page = '<ul\s*class=\"pagination\">.*?href="[^"]+\/page\/(\d+)\/'
            patron_page += '(?:\?[^"]+)?"\s*>(?:\d+)?\s*(?:<span\s*aria-hidden="[^"]+">'
            patron_page += '&\w+;<\/span>)?<\/a>\s*<\/li>\s*<\/ul>\s*<\/nav>\s*'
            patron_page += '<\/div>\s*<\/div>\s*<\/div>'
            if scrapertools.find_single_match(data_foot, patron_page):
                try:
                    last_page = int(scrapertools.find_single_match(data_foot, patron_page))
                except:
                    last_page = 1
                last_page_print = int((last_page * (float(len(matches)) / float(cnt_tot))) + 0.999999999)
                page_factor = float(last_page_print) / float(last_page)
            else:
                last_page = 1
                last_page_print = last_page
                page_factor = float(last_page_print) / float(last_page)
            #logger.debug('curr_page: ' + str(curr_page) + ' / last_page: ' + str(last_page) + ' / page_factor: ' + str(page_factor))
        
        #Marcamos la próxima página
        if '&p=' in  next_page_url:
            next_page_url = re.sub(r'&p=\d+', '&p=%s' % str(curr_page), next_page_url)
        elif '/page/' in  next_page_url:
            next_page_url = re.sub(r'\/page\/\d+\/', '/page/%s/' % str(curr_page), next_page_url)
        #logger.debug('curr_page: ' + str(curr_page) + ' / last_page: ' + str(last_page) + ' / last_page_print: ' + str(last_page_print))        
        
        #Empezamos el procesado de matches
        for scrapedurl, scrapedtitle, scrapedthumbnail, size in matches:
            cnt_match += 1
            if "/programas" in scrapedurl or "/otros" in scrapedurl:
                continue
            
            scrapedquality = ''
            scrapedlang = ''
            title = scrapertools.remove_htmltags(scrapedtitle).rstrip()         # Removemos Tags del título
            if item.extra == 'series':
                title = scrapertools.remove_htmltags(size).rstrip()             # Removemos Tags del título
            url = scrapedurl.replace(' ', '%20').replace('&amp;', '&')

            title_subs = []                                                     # creamos una lista para guardar info importante
            
            # Slugify, pero más light
            title = title.replace("á", "a").replace("é", "e").replace("í", "i")\
                    .replace("ó", "o").replace("ú", "u").replace("ü", "u")\
                    .replace("ï¿½", "ñ").replace("Ã±", "ñ")
            title = scrapertools.decode_utf8_error(title)

            # Salvo que venga la llamada desde Episodios, se filtran las entradas para evitar duplicados de Temporadas
            url_list = url
            if not (item.extra == 'search' and item.extra2 == 'episodios'):
                if scrapertools.find_single_match(url_list, '-torrents-\d+-\d+-'):
                    url_list = re.sub('-torrents-\d+-\d+-', '-torrents-', url)
                else:
                    url_list = re.sub('\/\d+\/\d+\/', '/', url)
                url_list = re.sub('(?i)-(\d+)-Temporada(?:-\D|-\.|\.)?', '-X-Temporada', url_list)
                url_list_alt = re.sub('(?i)-temporada-\d+', '', url_list)
                if url_list_alt in str(title_lista):                            # Si ya hemos procesado el título, lo ignoramos
                    continue
                else:
                    title_lista += [url_list_alt]                               # la añadimos a la lista de títulos
            
            cnt_title += 1                                                      # Incrementamos el contador de entradas válidas
            item_local = item.clone()                                           # Creamos copia de Item para trabajar
            if item_local.tipo:                                                 #... y limpiamos
                del item_local.tipo
            if item_local.totalItems:
                del item_local.totalItems
            if item_local.intervencion:
                del item_local.intervencion
            if item_local.viewmode:
                del item_local.viewmode
            if item_local.matches:
                del item_local.matches
            if item_local.post or item_local.post is None:
                del item_local.post
            if item_local.headers or item_local.headers is None:
                del item_local.headers
            if item_local.referer or item_local.referer is None:
                del item_local.referer
            item_local.extra2 = True
            del item_local.extra2
            item_local.text_bold = True
            del item_local.text_bold
            item_local.text_color = True
            del item_local.text_color

            # Después de un Search se restablecen las categorías
            if item_local.extra == 'search' or item.extra2 == 'novedades':
                if 'serie' in url:
                    item_local.extra = 'series'                                 # Serie búsqueda
                else:
                    item_local.extra = 'peliculas'                              # Película búsqueda

            # Guardamos los formatos para películas
            if item_local.extra == 'peliculas':
                item_local.contentType = "movie"
                item_local.action = "findvideos"

            # Guardamos los formatos para series y documentales
            elif item_local.extra == 'series':
                item_local.contentType = "tvshow"
                item_local.action = "episodios"
                item_local.season_colapse = season_colapse                      # Muestra las series agrupadas por temporadas?
            
            # Procesamos idiomas
            item_local.language = []                                            # creamos lista para los idiomas
            if "latino" in scrapedlang.lower() or "latino" in url or "latino" in title.lower():
                item_local.language += ["LAT"]
            if "ingles" in scrapedlang.lower() or "ingles" in url or "vose" in url:
                if "VOSE" in scrapedlang.lower() or "sub" in title.lower() or "vose" in url:
                    item_local.language += ["VOS"]
                else:
                    item_local.language += ["VO"]
            elif 'subtituladas' in scrapedthumbnail or 'vose' in title.lower():
                item_local.language += ['VOSE']
            elif 'Version Original' in scrapedthumbnail or 'vo' in title.lower():
                item_local.language += ['VO']
            if "dual" in scrapedlang.lower() or "dual" in title.lower():
                item_local.language[0:0] = ["DUAL"]
            if not item_local.language:
                item_local.language = ['CAST']                                  # [CAST] por defecto
                
            # Procesamos Calidad
            patron_quality = '(?i)[\[|\(](.*?)[\)|\]]'
            if scrapedquality:
                item_local.quality = scrapertools.remove_htmltags(scrapedquality).rstrip()      # iniciamos calidad
            if item_local.contentType == "tvshow":
                if '720p' in title or '720p' in scrapedquality:
                    item_local.quality = 'HDTV-720p'
                elif '1080p' in title or '1080p' in scrapedquality:
                    item_local.quality = '1080p'
                else:
                    item_local.quality = 'HDTV'
            elif not scrapedquality:
                if '/peliculas-hd' in scrapedurl or item_local.extra == 'Películas HD':
                    item_local.quality = 'HD'
                elif '/peliculas-dvdr' in scrapedurl or item_local.extra == 'Películas DVDR':
                    item_local.quality = 'DVDR'
                elif '/peliculas-3-d' in scrapedurl or item_local.extra == 'Películas 3D':
                    item_local.quality = '3D'
                if not item_local.quality:
                    item_local.quality = 'HDRip'
                if "categoria" in item.url:
                    item_local.quality = scrapertools.find_single_match(item.url, r'\/categoria\/(.*?)(?:\-\d)?\/').replace('-', ' ')
                elif scrapertools.find_single_match(title, patron_quality):
                    item_local.quality = scrapertools.find_single_match(title, patron_quality)
            if '4k' in title.lower() and not '4k' in item_local.quality.lower():
                item_local.quality += ', 4K'
            if '3d' in title.lower() and not '3d' in item_local.quality.lower():
                item_local.quality += ', 3D'
            if item_local.contentType == 'movie' and scrapertools.find_single_match(title, patron_quality):
                title = re.sub(patron_quality, '', title)
            title = re.sub(r'(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', '', title)
            item_local.quality = re.sub(r'(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', 
                        '', item_local.quality).strip()
            
            if item_local.extra == 'series' or item.extra2 == 'novedades':                                            
                item_local.thumbnail = urlparse.urljoin(host, scrapedthumbnail) # si son series, contiene el thumb
            else:
                item_local.thumbnail = ''

            item_local.url = urlparse.urljoin(host, url)                        # guardamos la url final
            item_local.context = "['buscar_trailer']"                           # ... y el contexto
            
            #Analizamos el año.  Si no está claro ponemos '-'
            item_local.infoLabels["year"] = '-'
            if item_local.contentType == 'movie':
                patron_year = '(\d{4})\s*?(?:\)|\])?$'
                year = scrapertools.find_single_match(title, patron_year)
                if year:
                    try:
                        year = int(year)
                        if year >= 1950 and year <= 2040:
                            item_local.infoLabels["year"] = year
                    except:
                        pass

            # Detectamos info importante a guardar para después de TMDB
            if 'miniserie' in title.lower():
                title_subs += ["Miniserie"]
            if 'colecc' in title.lower():
                title_subs += ["Colección"]
            if 'saga' in title.lower():
                title_subs += ['Saga']
            
            # Limpiamos el título de la basura innecesaria
            title = re.sub(r'(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|hd|torrent', '', title).strip()
            title = re.sub(r'(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?', 
                        '', title).strip()
            title = re.sub(r'(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*', '', title).strip()
            title = re.sub(r'(?i)[-|\(]?\s*HDRip\)?|microHD|DVD\s*R\w*|[\[|\(]*dv\S*[\)|\]]*|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?|\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|\s*ts|[\(|\[]\S*\.*$', 
                        '', title).strip()
            title = re.sub(r'[\(|\[]\s+[\)|\]]', '', title)
            title = title.replace('()', '').replace('[]', '').replace('[4K]', '').replace('(4K)', '')

            # Salvamos el título según el tipo de contenido
            # Si vienen de Novedades, se prepara el título para las series
            if item.extra2 == "novedades" and item_local.extra == 'series':
                title_subs += ["Episodio %s" % scrapertools.find_single_match(title, '\d+[x|×]\d+')]
            if item_local.contentType == "movie":
                item_local.contentTitle = title.strip().lower().title()
            else:
                title = re.sub(r'(?i)(?:\s*&#8211;)?\s*temp.*?\d+.*', '', title)    #Limpiamos temporadas completas, solo queremos la serie entera
                title = re.sub(r'\d?\d?&#.*', '', title)                        #Limpiamos temporada y episodio
                title = re.sub(r'\d+[x|×]\d+.*', '', title)                     #Limpiamos temporada y episodio
                title = scrapertools.htmlclean(title)                           #Quitamos html restante
                item_local.contentSerieName = title.strip().lower().title()

            item_local.title = title.strip().lower().title()
            item_local.from_title = item_local.title
            if not item_local.title: continue

            #Guarda la variable temporal que almacena la info adicional del título a ser restaurada después de TMDB
            item_local.title_subs = title_subs
                
            #Salvamos y borramos el número de temporadas porque TMDB a veces hace tonterias.  Lo pasamos como serie completa
            if item_local.contentSeason and (item_local.contentType == "season" \
                        or item_local.contentType == "tvshow"):
                item_local.contentSeason_save = item_local.contentSeason
                del item_local.infoLabels['season']

            #Ahora se filtra por idioma, si procede, y se pinta lo que vale
            if filter_languages > 0:                                            # Si hay idioma seleccionado, se filtra
                itemlist = filtertools.get_link(itemlist, item_local, list_language)
            else:
                itemlist.append(item_local.clone())                             # Si no, pintar pantalla
            
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
                        last_page_print=last_page_print, post=post, referer=referer, headers=headers))

    return itemlist

    
def findvideos(item):
    logger.info()

    itemlist = []
    itemlist_t = []                                                             # Itemlist total de enlaces
    itemlist_f = []                                                             # Itemlist de enlaces filtrados
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
    
    post = None
    headers = None
    referer = None
    follow_redirects = True
    timeout_find = timeout
    if item.videolibray_emergency_urls:                                         # Si se están cacheando enlaces aumentamos el timeout
        timeout_find = timeout * 2
    elif item.emergency_urls:                                                   # Si se llama desde la Videoteca con enlaces cacheados... 
        timeout_find = old_div(timeout, 2)                                      # reducimos el timeout antes de saltar a los enlaces cacheados
    
    #logger.debug(item)
    
    if item.post or item.post is None:
        post = item.post
        del item.post
    if item.headers or item.headers is None:
        headers = item.headers
        del item.headers
    if item.referer or item.referer is None:
        referer = item.referer
        del item.referer

    # Compatibilidad con la versión antigua en Videoteca
    if item.contentType == 'episode' and not item.matches:
        item.matches = []
        item.matches.append((item.url))
        if item.url_tvshow: item.url = item.url_tvshow
    
    # Bajamos los datos de las páginas
    if not item.matches:
        data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout_find, post=post, 
                                                                   headers=headers, referer=referer, canonical=canonical, 
                                                                   s2=False, follow_redirects=follow_redirects, 
                                                                   item=item, itemlist=[])               # Descargamos la página)
    
    # Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if (not data and not item.matches) or response.code == 999:
        if item.emergency_urls and not item.videolibray_emergency_urls:         # Hay urls de emergencia?
            if len(item.emergency_urls) > 1 and item.emergency_urls[1]:
                matches = item.emergency_urls[1]                                # Restauramos matches de vídeos
            elif len(item.emergency_urls) == 1 and item.emergency_urls[0]:
                matches = item.emergency_urls[0]                                # Restauramos matches de vídeos - OLD FORMAT
            item.armagedon = True                                               # Marcamos la situación como catastrófica 
        else:
            if item.videolibray_emergency_urls:                                 # Si es llamado desde creación de Videoteca...
                return item                                                     # Devolvemos el Item de la llamada
            else:
                return itemlist                                     # si no hay más datos, algo no funciona, pintamos lo que tenemos

    # Seleccionamos las matches
    patron = '<a\s*class="linktorrent".*?<(?:div\s*id|td\s*class)="opcion2_\w+".*?href="([^"]+)"'
    if not scrapertools.find_single_match(data, patron):                        # Buscar con patrón alternativo
        patron = '<a\s*class="linktorrent[^"]*"\s*(?:target="[^"]*"\s*)?href="([^"]+)"'
        if not scrapertools.find_single_match(data, patron):                    # Buscar con patrón alternativo
            patron = '<td\s*class="opcion2[^>]*>\s*<a\s*[^>]*href="([^"]+)"'
            if not scrapertools.find_single_match(data, patron):                # Buscar con patrón alternativo
                patron = 'onclick="post\("(?P<url>[^"]+",\s*{u:\s*"[^"]+)"}\);'

    if not item.armagedon:
        if not item.matches:
            matches = re.compile(patron, re.DOTALL).findall(data)
        else:
            matches = item.matches
            #del item.matches
    
    #logger.debug("PATRON: " + patron)
    #logger.debug(matches)
    #logger.debug(data)
    
    if not matches:                                                             # error
        if item.videolibray_emergency_urls:                                     # Si es llamado desde creación de Videoteca...
            logger.error("ERROR 02: FINDVIDEOS: Ha cambiado la estructura de la Web " + 
                            " / PATRON: " + patron)
            return item                                                         # Devolvemos el Item de la llamada
        else:
            logger.error("ERROR 02: FINDVIDEOS: Ha cambiado la estructura de la Web " + 
                            " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: FINDVIDEOS: Ha cambiado la estructura de la Web.  '
                        + 'Reportar el error con el log'))
            return itemlist                                     # si no hay más datos, algo no funciona, pintamos lo que tenemos
    
    # Si es un lookup para cargar las urls de emergencia en la Videoteca...
    if item.videolibray_emergency_urls:
        item.emergency_urls = []                                                # Iniciamos emergency_urls
        item.emergency_urls.append([])                                          # Reservamos el espacio para los .torrents locales
        matches_list = []                                                       # Convertimos matches-tuple a matches-list
        for tupla in matches:
            if isinstance(tupla, tuple):
                matches_list.append(list(tupla))
        if matches_list:
            item.emergency_urls.append(matches_list)                            # Salvamnos matches de los vídeos...  
        else:
            item.emergency_urls.append(matches)

    # Llamamos al método para crear el título general del vídeo, con toda la información obtenida de TMDB
    if not item.videolibray_emergency_urls:
        item, itemlist = generictools.post_tmdb_findvideos(item, itemlist)

    # Ahora tratamos los enlaces .torrent con las diferentes calidades
    for x, scrapedurl_la in enumerate(matches):                                 # Leemos los torrents con la diferentes calidades
        scrapedurl_base = urlparse.urljoin(host_torrent, 'download_tt.php?u=')
        if '/' not in scrapedurl_la:
            scrapedurl = urlparse.urljoin(scrapedurl_base, generictools.convert_url_base64(scrapedurl_la))
        elif '.php?' in scrapedurl_la:
            scrapedurl = generictools.convert_url_base64(scrapedurl_la, host_torrent)
        elif not 'download' in scrapedurl_la and not ('.torrent' in scrapedurl_la or 'magnet:' in scrapedurl_la):
            scrapedurl = generictools.convert_url_base64(scrapedurl_la.split('/')[-1], host_torrent)
        else:
            scrapedurl = urlparse.urljoin(host_torrent, scrapedurl_la).replace("download/torrent.php', {u: ", "download_tt.php?u=")
        if '.php?u=http' in scrapedurl:
            scrapedurl = scrapedurl.replace(scrapedurl_base, '')
        
        # Si ha habido un cambio en la url, actualizados matches para emergency_urls
        if item.videolibray_emergency_urls and scrapedurl != scrapedurl_la:
            item.emergency_urls[1][x] = scrapedurl

        referer = None
        post= None
        headers = None
        scrapedlang = ''
        scrapedquality = ''
        scrapedpassword = ''
        scrapedsize = ''
        
        # Puede ser necesario baja otro nivel para encontrar la página
        if not 'magnet:' in scrapedurl and not '.torrent' in scrapedurl:
            patron_torrent = '(?i)>\s*Pincha[^<]*<a\s*href="([^"]+)"'           # VERIFICAR !!!
            data_torrent, response, item, itemlist = generictools.downloadpage(scrapedurl, timeout=timeout, canonical=canonical, 
                                                                               referer=referer, post=post, headers=headers, 
                                                                               s2=False, patron=patron_torrent, 
                                                                               item=item, itemlist=itemlist)        # Descargamos la página)
            #logger.debug("PATRON: " + patron_torrent)
            #logger.debug(data_torrent)
            
            # Verificamos si se ha cargado una página, y si además tiene la estructura correcta
            if not data_torrent or response.code == 999:
                if item.emergency_urls and not item.videolibray_emergency_urls: # Hay urls de emergencia?
                    if len(item.emergency_urls) > 1 and item.emergency_urls[1]:
                        matches = item.emergency_urls[1]                        # Restauramos matches de vídeos
                    elif len(item.emergency_urls) == 1 and item.emergency_urls[0]:
                        matches = item.emergency_urls[0]                        # Restauramos matches de vídeos
                    item.armagedon = True                                       # Marcamos la situación como catastrófica 
                else:
                    if item.videolibray_emergency_urls:                         # Si es llamado desde creación de Videoteca...
                        return item                                             # Devolvemos el Item de la llamada
                    else:
                        return itemlist                                 # si no hay más datos, algo no funciona, pintamos lo que tenemos
            
            # Obtenemos el enlace final
            scrapedurl = generictools.convert_url_base64(scrapertools.find_single_match(data_torrent, patron_torrent), host_torrent)

        #Generamos una copia de Item para trabajar sobre ella
        item_local = item.clone()
        if item_local.post or item_local.post is None:
            del item_local.post
        if item_local.headers or item_local.headers is None:
            del item_local.headers
        if item_local.referer or item_local.referer is None:
            del item_local.referer

        item_local.url = scrapedurl
        
        # Procesamos idiomas
        if scrapedlang:
            item_local.language = []                                            # creamos lista para los idiomas
            if "latino" in scrapedlang.lower() or "latino" in item_local.url:
                item_local.language += ["LAT"]
            if "ingles" in scrapedlang.lower() or "ingles" in item_local.url or "vose" in item_local.url:
                if "VOSE" in scrapedlang.lower() or "sub" in item_local.url or "vose" in item_local.url:
                    item_local.language += ["VOS"]
                else:
                    item_local.language += ["VO"]
            elif 'subtituladas' in scrapedthumbnail or 'vose' in title.lower():
                item_local.language += ['VOSE']
            elif 'Version Original' in scrapedthumbnail or 'vo' in title.lower():
                item_local.language += ['VO']
            if "dual" in scrapedlang.lower() or "dual" in item_local.url:
                item_local.language[0:0] = ["DUAL"]
            if not item_local.language:
                item_local.language = ['CAST']                                  # [CAST] por defecto

        # Procesamos Calidad
        if scrapedquality:
            item_local.quality = scrapertools.remove_htmltags(scrapedquality).rstrip()
            if item_local.contentType == "tvshow":
                if '720p' in scrapedquality:
                    item_local.quality = 'HDTV-720p'
                elif '1080p' in scrapedquality:
                    item_local.quality = '1080p'
                else:
                    item_local.quality = 'HDTV'
            else:
                if 'avi' in scrapedquality.lower():
                    item_local.quality = 'BlueRayRip'
        
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
        
        # Buscamos tamaño en el archivo .torrent
        if scrapedsize:
            size = scrapedsize
        elif item_local.torrent_info:
            size = item_local.torrent_info
        else:
            size = ''
        if size and scrapedpassword:
            size = '[COLOR magenta][B]RAR-[/B][/COLOR]%s' % size
        if not size and not item.videolibray_emergency_urls:
            if not item.armagedon:
                # Buscamos el tamaño en el .torrent desde la web
                torrent_params['url'] = item_local.url
                torrent_params['local_torr'] = local_torr
                torrent_params = generictools.get_torrent_size(item_local.url, post=post, headers=headers, 
                                                               referer=referer, torrent_params=torrent_params, item=item_local) # Tamaño en el .torrent
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
                    torrent_params = generictools.get_torrent_size(item_local.url, post=post, headers=headers, 
                                                                   referer=referer, torrent_params=torrent_params, item=item_local)
                    size = torrent_params['size']
                    if torrent_params['torrents_path']: item_local.torrents_path = torrent_params['torrents_path']
        if size:
            size = size.replace('GB', 'G·B').replace('Gb', 'G·B').replace('MB', 'M·B')\
                        .replace('Mb', 'M·B').replace('.', ',')
            item_local.torrent_info = '%s, ' % size                             # Agregamos size
        if scrapedsize:
            size = ''                                                           # No hemos verificado el .torrent
        if item_local.url.startswith('magnet:'):
            item_local.torrent_info += ' Magnet'
        if item_local.torrent_info:
            item_local.torrent_info = item_local.torrent_info.strip().strip(',')
            #item.torrent_info = item_local.torrent_info
            if not item.unify:
                item_local.torrent_info = '[%s]' % item_local.torrent_info
   
        # Si tiene contraseña, la guardamos y la pintamos
        if scrapedpassword:
            item_local.password = scrapedpassword
            item_local.quality += ' [COLOR magenta][B] Contraseña: [/B][/COLOR]%s' % item_local.password
            #itemlist.append(item.clone(action="", title="[COLOR magenta][B] Contraseña: [/B][/COLOR]'" 
            #            + item_local.password + "'", folder=False))
        
        # Guardamos urls de emergencia si se viene desde un Lookup de creación de Videoteca
        if item.videolibray_emergency_urls:
            item.emergency_urls[0].append(item_local.url)                       # guardamos la url y nos vamos
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
        
        if not size or 'Magnet' in size:
            item_local.alive = "??"                                             # Calidad del link sin verificar
        elif 'ERROR' in size and 'Pincha' in size:
            item_local.alive = "ok"                                             # link en error, CF challenge, Chrome disponible
        elif 'ERROR' in size and 'Introduce' in size:
            item_local.alive = "??"                                             # link en error, CF challenge, ruta de descarga no disponible
            item_local.channel = 'setting'
            item_local.action = 'setting_torrent'
            item_local.unify = False
            item_local.folder = False
            item_local.item_org = item.tourl()
        elif 'ERROR' in size:
            item_local.alive = "no"                                             # Calidad del link en error, CF challenge?
        else:
            item_local.alive = "ok"                                             # Calidad del link verificada
        if item_local.channel != 'setting':
            item_local.action = "play"                                          # Visualizar vídeo
            item_local.server = "torrent"                                       # Seridor Torrent
        
        itemlist_t.append(item_local.clone())                                   # Pintar pantalla, si no se filtran idiomas
        
        # Requerido para FilterTools
        if config.get_setting('filter_languages', channel) > 0:                 # Si hay idioma seleccionado, se filtra
            itemlist_f = filtertools.get_link(itemlist_f, item_local, list_language)  # Pintar pantalla, si no está vacío

        #logger.debug("TORRENT: " + scrapedurl + " / title gen/torr: " + item.title + " / " + item_local.title + " / calidad: " + item_local.quality + " / content: " + item_local.contentTitle + " / " + item_local.contentSerieName)
        #logger.debug(item_local)

    #Si es un lookup para cargar las urls de emergencia en la Videoteca...
    if item.videolibray_emergency_urls:
        return item                                                             # ... nos vamos
    
    if len(itemlist_f) > 0:                                                     # Si hay entradas filtradas...
        itemlist.extend(itemlist_f)                                             # Pintamos pantalla filtrada
    else:                                                                       
        if config.get_setting('filter_languages', channel) > 0 and len(itemlist_t) > 0: #Si no hay entradas filtradas ...
            thumb_separador = get_thumb("next.png")                             # ... pintamos todo con aviso
            itemlist.append(Item(channel=item.channel, url=host, 
                        title="[COLOR red][B]NO hay elementos con el idioma seleccionado[/B][/COLOR]", 
                        thumbnail=thumb_separador, folder=False))
        
        if len(itemlist_t) == 0:
            if len(itemlist) == 0 or (len(itemlist) > 0 and itemlist[-1].server != 'torrent'):
                return []
        itemlist.extend(itemlist_t)                                             # Pintar pantalla con todo si no hay filtrado
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)                                              # Lanzamos Autoplay
    
    return itemlist
    

def episodios(item):
    logger.info()
    
    itemlist = []
    search_seasons = False
    #logger.debug(item)

    if item.from_title:
        item.title = item.from_title
    
    #Limpiamos num. Temporada y Episodio que ha podido quedar por Novedades
    season_display = 0
    if item.contentSeason:
        if item.season_colapse:                                                 # Si viene del menú de Temporadas...
            season_display = item.contentSeason                                 # ... salvamos el num de sesión a pintar
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
    max_nfo = 0
    if item.infoLabels['number_of_seasons']:
        max_temp = item.infoLabels['number_of_seasons']
    y = []
    if modo_ultima_temp_alt and item.library_playcounts:                        #Averiguar cuantas temporadas hay en Videoteca
        patron = 'season (\d+)'
        matches = re.compile(patron, re.DOTALL).findall(str(item.library_playcounts))
        for x in matches:
            y += [int(x)]
        max_nfo = max(y)

    # Si la series tiene solo una temporada, o se lista solo una temporada, guardamos la url y seguimos normalmente
    list_temps = []
    list_temp = []
    if season_display > 0 or max_temp == 1 or not item.infoLabels['tmdb_id']:
        list_temps.append(item.url)
        
    # Obtenemos todas las Temporada de la Serie desde Search
    # Si no hay TMDB o es sólo una temporada, listamos lo que tenemos
    if search_seasons and season_display == 0 and item.infoLabels['tmdb_id'] and max_temp > 1:
        # Si hay varias temporadas, buscamos todas las ocurrencias y las filtraos por TMDB y calidad
        list_temp = generictools.find_seasons(item, modo_ultima_temp_alt, max_temp, max_nfo)
    elif item.url not in str(list_temps):
        list_temps.append(item.url)

    if not list_temp:
        list_temp = list_temps[:]                                               # Lista final de Temporadas a procesar

    # Descarga las páginas
    for _url in list_temp:                                                       # Recorre todas las temporadas encontradas
        url = _url
        data, response, item, itemlist = generictools.downloadpage(url, timeout=timeout, canonical=canonical, 
                                                                   s2=False, item=item, itemlist=itemlist, 
                                                                   forced_proxy_opt=forced_proxy_opt)       # Descargamos la página
        # Verificamos si ha cambiado el Host
        if response.host:
            for x, u in enumerate(list_temp):
                list_temp[x] = list_temp[x].replace(scrapertools.find_single_match(url, patron_host), response.host.rstrip('/'))
            url = response.url_new
        
        #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
        if not response.sucess:                                                 # Si ERROR o lista de errores ...
            if len(itemlist) > 1 or not 'timeout' in response.code:             # puede ser un enlace erroneo de una temporada.  Siguiente...
                continue
            logger.error("ERROR 01: EPISODIOS: La Web no responde o ha cambiado de URL " + 
                            " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.category + 
                            ': ERROR 01: EPISODIOS: La Web no responde o ha cambiado de URL.  '
                            + 'Reportar el error con el log'))
            return itemlist                                                     # Si no hay nada más, salimos directamente

        patron = '(?i)<tr>\s*<td>\s*<img\s*src="[^>]+title="Idioma\s*Capitulo"\s*\/>'
        patron += '\s*([^<]*)<a\s*class=[^>]+>\s*([^<]+)<\/a>\s*<\/td>\s*<td>'
        patron += '\s*<[^>]+>\s*<[^>]+>\s*<\/a>\s*<\/td>\s*<td\s*class="opcion2_td"'
        patron += '[^>]+>\s*<a\s*href="([^"]+)"'
        if not scrapertools.find_single_match(data, patron):
            patron = '(?i)<tr>\s*<td>\s*<img\s*src="[^>]+title="Idioma\s*Capitulo"\s*\/>'
            patron += '\s*([^<]*)<a\s*class[^>]+>\s*([^<]+)<\/a>\s*<\/td>\s*<td>'
            patron += '<a[^>]+\s*class="linktorrent"\s*[^>]+\s*href="([^"]*")[^>]*>'
        
        patron_epi = '(?i)(\d{1,2})(?:x|&#215;)(\d{1,2})(?:[-|\s*](?:al|-)?[-|\s*]?'
        patron_epi += '(?:\d{1,2}(?:x|&#215;))?(\d{1,2}))?'
        
        patron_temp = '(?i)Temporada[\s*|-](\d+)'

        matches = re.compile(patron, re.DOTALL).findall(data)
       
        if not matches:
            logger.error("ERROR 02: EPISODIOS: Ha cambiado la estructura de la Web " + 
                            " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.category + 
                            ': ERROR 02: EPISODIOS: Ha cambiado la estructura de la Web.  '
                            + 'Reportar el error con el log'))
            return itemlist                                             # si no hay más datos, algo no funciona, pintamos lo que tenemos

        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)

        # Recorremos todos los episodios generando un Item local por cada uno en Itemlist
        for scrapedlang, scrapedtitle, scrapedurl_la in matches:
            scrapedquality = ''
            scrapedpassword = ''
            scrapedurl = generictools.convert_url_base64(scrapedurl_la, host_torrent)

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

            item_local.url = url
            item_local.url_tvshow = url
            
            title = re.sub('(?i)FINAL TEMPORADA', '', scrapedtitle)
            title = re.sub(item.contentSerieName, '', title)
            item_local.title = ''
            item_local.matches = []
            item_local.context = "['buscar_trailer']"
            
            # Extraemos números de temporada y episodio
            alt_epi = ''
            try:
                item_local.contentSeason, item_local.contentEpisodeNumber, alt_epi = \
                            scrapertools.find_single_match(title, patron_epi)
                
                item_local.contentSeason = int(item_local.contentSeason)
                item_local.contentEpisodeNumber = int(item_local.contentEpisodeNumber)
            except:
                if 'miniserie' in title.lower():
                    item_local.contentSeason = 1
                elif "temporada" in title.lower() or "completa" in title.lower(): #si es una temporada, lo aceptamos como episodio 1
                    try:
                        item_local.contentSeason = int(scrapertools.find_single_match(title, patron_temp))
                    except:
                        item_local.contentSeason = 1
                else:
                    logger.error('ERROR al extraer Temporada/Episodio: ' + str(title))
                    item_local.contentSeason = 1
                item_local.contentEpisodeNumber = 1

            if "temporada" in title.lower() or "completa" in title.lower():     #Temporada completa
                alt_epi = 99
            if alt_epi:                                                         # Si son episodios múltiples, lo guardamos
                item_local.infoLabels['episodio_titulo'] = 'al %s' % str(alt_epi).zfill(2)
                item_local.title = '%sx%s al %s' % (str(item_local.contentSeason), 
                        str(item_local.contentEpisodeNumber).zfill(2), str(alt_epi).zfill(2))
            else:
                item_local.title = '%sx%s - ' % (str(item_local.contentSeason), 
                        str(item_local.contentEpisodeNumber).zfill(2))
            
            # Procesamos la Idiomas
            lang = scrapedlang.strip()
            if 'vo' in lang.lower() or 'v.o' in lang.lower() or 'vo' in title.lower() or 'v.o' in title.lower():
                item_local.language += ['VO']
            elif 'vose' in lang.lower() or 'v.o.s.e' in lang.lower() or 'vose' in title.lower() or 'v.o.s.e' in title.lower():
                item_local.language += ['VOSE']
            elif 'latino' in lang.lower() or 'latino' in title.lower():
                item_local.language += ['LAT']
            if not item_local.language:
                item_local.language = ['CAST']
            
            # Procesamos la Calidad
            if '720p' in scrapedquality:
                item_local.quality = 'HDTV-720p'
            elif '1080p' in scrapedquality:
                item_local.quality = '1080p'
            else:
                item_local.quality = 'HDTV'

            # Si es el mismo episodio, pero con diferente calidad, se acumula a item anterior
            if len(itemlist) > 0 and item_local.contentSeason == itemlist[-1].contentSeason \
                            and item_local.contentEpisodeNumber == itemlist[-1].contentEpisodeNumber \
                            and item_local.title == itemlist[-1].title \
                            and itemlist[-1].contentEpisodeNumber != 0:         #solo guardamos un episodio ...
                if itemlist[-1].quality:
                    itemlist[-1].quality += ", " + item_local.quality           #... pero acumulamos las calidades
                else:
                    itemlist[-1].quality = item_local.quality
                
                if '720' in item_local.quality or '1080' in item_local.quality: # La calidad más alta primero, para Download Auto
                    itemlist[-1].matches.insert(0, (scrapedlang, item_local.quality, scrapedpassword, item_local.title, scrapedurl))
                else:
                    itemlist[-1].matches.append((scrapedurl))
                continue      
            
            # Salvamos los matches de cada episodio para findvideos
            item_local.matches.append((scrapedurl))

            if modo_ultima_temp_alt and item.library_playcounts:                #Si solo se actualiza la última temporada de Videoteca
                if item_local.contentSeason < max_temp:
                    break
            
            if season_display > 0:                                              # Son de la temporada estos episodios?
                if item_local.contentSeason > season_display:
                    continue
                elif item_local.contentSeason < season_display:
                    break

            itemlist.append(item_local.clone())

            #logger.debug(item_local)
            
    if len(itemlist) > 1:
        itemlist = sorted(itemlist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))       #clasificamos
        
    if item.season_colapse and not item.add_videolibrary:                       # Si viene de listado, mostramos solo Temporadas
        item, itemlist = generictools.post_tmdb_seasons(item, itemlist, url='season')

    if not item.season_colapse:                                                 # Si no es pantalla de Temporadas, pintamos todo
        # Pasada por TMDB y clasificación de lista por temporada y episodio
        tmdb.set_infoLabels(itemlist, True, idioma_busqueda=idioma)

        # Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
        item, itemlist = generictools.post_tmdb_episodios(item, itemlist)
    
    #logger.debug(item)

    return itemlist


def actualizar_titulos(item):
    logger.info()
    
    # Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels
    item = generictools.update_title(item)
    
    # Volvemos a la siguiente acción en el canal
    return item


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    
    item.url = host + 'page/1/?s=%s' % texto
    item.extra = "search"
    
    # Mientras sea necesario el proxy, entorpece las Novedades
    #if channel in base64.b64decode(config.get_setting('proxy_channel_bloqued')).decode('utf-8'):
    #    return []
    
    try:
        if texto:
            return listado(item)
        else:
            return []
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc())
        return []
 
 
def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()

    item.title = "newest"
    item.category_new = "newest"
    item.channel = channel
    
    # Mientras sea necesario el proxy, entorpece las Novedades
    if channel in base64.b64decode(config.get_setting('proxy_channel_bloqued')).decode('utf-8'):
        return itemlist

    try:
        for cat in ['peliculas', 'series']:
            if cat != categoria: continue
                
            item.extra = cat
            if cat == 'peliculas': item.url = host + movies_sufix
            if cat == 'series': item.url = host + series_sufix

            item.extra2 = "novedades"
            item.action = "listado"
            itemlist = listado(item)

        if len(itemlist) > 0 and (">> Página siguiente" in itemlist[-1].title or "Pagina siguiente >>" in itemlist[-1].title):
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc(1))
        return []

    return itemlist
