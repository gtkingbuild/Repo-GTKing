# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

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
             'channel': 'subtorrents', 
             'host': config.get_setting("current_host", 'subtorrents', default=''), 
             'host_alt': ['https://www.subtorrents.eu/'], 
             'host_black_list': ['https://www.subtorrents.re/', 'https://www.subtorrents.do/'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'
patron_sufix = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+(\.\w+)(?:\/|\?|$)'
host_torrent = host[:-1]
sufix = scrapertools.find_single_match(host, patron_sufix)

color1, color2, color3 = ['0xFF58D3F7', '0xFF2E64FE', '0xFF0404B4']
__modo_grafico__ = config.get_setting('modo_grafico', channel)
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)        #Actualización sólo últ. Temporada?
timeout = config.get_setting('timeout_downloadpage', channel)
idioma_busqueda = 'es,en'


def mainlist(item):
    logger.info()
    itemlist = []
    
    thumb_pelis_hd = get_thumb("channels_movie_hd.png")
    thumb_series = get_thumb("channels_tvshow.png")
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, url=host, title="Películas", action="submenu", thumbnail=thumb_pelis_hd, extra="peliculas"))
    
    itemlist.append(Item(channel=item.channel, url=host, title="Series", action="submenu", thumbnail=thumb_series, extra="series"))
    
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + "?s=%s", thumbnail=thumb_buscar, extra="search"))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", folder=False, thumbnail=thumb_separador))
    
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", thumbnail=thumb_settings))
    
    autoplay.show_option(item.channel, itemlist)                    #Activamos Autoplay

    return itemlist
    
    
def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return

    
def submenu(item):
    logger.info()
    itemlist = []
    
    thumb_cartelera = get_thumb("now_playing.png")
    thumb_latino = get_thumb("channels_latino")
    thumb_pelis = get_thumb("channels_movie.png")
    thumb_pelis_AZ = get_thumb("channels_movie_az.png")
    thumb_pelis_hd = get_thumb("channels_movie_hd.png")
    thumb_series = get_thumb("channels_tvshow.png")
    thumb_series_AZ = get_thumb("channels_tvshow_az.png")
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    thumb_series = get_thumb("channels_tvshow.png")

    if item.extra == "peliculas":
    
        itemlist.append(Item(channel=item.channel, title="Novedades", action="listado", url=host + "peliculas-subtituladas/?filtro=estrenos", thumbnail=thumb_cartelera, extra="peliculas"))
        itemlist.append(Item(channel=item.channel, title="Películas", action="listado", url=host + "peliculas-subtituladas/", thumbnail=thumb_pelis, extra="peliculas"))
        itemlist.append(Item(channel=item.channel, title="    Latino", action="listado", url=host + "peliculas-subtituladas/?filtro=audio-latino", thumbnail=thumb_latino, extra="peliculas"))
        itemlist.append(Item(channel=item.channel, title="    Alfabético A-Z", action="alfabeto", url=host + "peliculas-subtituladas/?s=letra-%s", thumbnail=thumb_pelis_AZ, extra="peliculas"))
        itemlist.append(Item(channel=item.channel, title="3D", action="listado", url=host + "peliculas-3d/", thumbnail=thumb_pelis, extra="peliculas"))
        itemlist.append(Item(channel=item.channel, title="Calidad DVD", action="listado", url=host + "calidad/dvd-full/", thumbnail=thumb_pelis, extra="peliculas"))
    
    if item.extra == "series":

        itemlist.append(item.clone(title="Series", action="listado", url=item.url + "series-2/", thumbnail=thumb_series, extra="series"))
        itemlist.append(item.clone(title="    Alfabético A-Z", action="alfabeto", url=item.url + "series-2/?s=letra-%s", thumbnail=thumb_series_AZ, extra="series"))

    return itemlist
    
    
def alfabeto(item):
    logger.info()
    itemlist = []
    
    itemlist.append(item.clone(action="listado", title="0-9", url=item.url % "0"))

    for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        itemlist.append(item.clone(action="listado", title=letra, url=item.url % letra))

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
    fin = inicio + 5                                                            # Después de este tiempo pintamos (segundos)
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
    
    post = None
    forced_proxy_opt = None
    referer = None
    if item.post:                                                               # Rescatamos el Post, si lo hay
        post = item.post
        forced_proxy_opt = None
    if item.referer:
        referer = item.referer
    
    next_page_url = item.url
    #Máximo num. de líneas permitidas por TMDB. Máx de 10 segundos por Itemlist para no degradar el rendimiento
    while cnt_title < cnt_tot * 0.5 and curr_page <= last_page and fin > time.time():
    
        # Descarga la página
        data = ''
        cnt_match = 0                                                           # Contador de líneas procesadas de matches
        if not item.matches:                                                    # si no viene de una pasada anterior, descargamos
            data, response, item, itemlist = generictools.downloadpage(next_page_url, timeout=timeout_search, 
                                                                       post=post, canonical=canonical, 
                                                                       forced_proxy_opt=forced_proxy_opt, referer=referer, 
                                                                       item=item, itemlist=itemlist)        # Descargamos la página)
            # Verificamos si ha cambiado el Host
            if response.host:
                next_page_url = response.url_new
        
            curr_page += 1                                                      #Apunto ya a la página siguiente
            if not data:                                                        #Si la web está caída salimos sin dar error
                if len(itemlist) > 1:                                           # Si hay algo que pintar lo pintamos
                    last_page = 0
                    break
                return itemlist                                                 # Si no hay nada más, salimos directamente

        #Patrón para todo, menos para Series completas, incluido búsquedas en cualquier caso
        patron = '<td\s*class="vertThseccion"[^>]*>\s*<img\s*src="([^"]+)"[^>]*>'
        patron += '\s*<a\s*href="([^"]+)"\s*title="([^"]+)"\s*>[^<]+<\/a>\s*<\/td>\s*'
        patron += '(?:<td>[^<]*\d+?<\/td>)?\s*<td>([^<]+)?<\/td>\s*<td>([^<]+)?<\/td>\s*<\/tr>'
        if not scrapertools.find_single_match(data, patron):
            patron = '<div\s*class="pintinia[^>]*>\s*<div\s*class="[^>]*>\s*<h6\s*class="[^>]*>'
            patron += '\s*<a\s*href="([^"]+)"\s*title="([^"]+)".*?<img\s*style="background-image:'
            patron += "\s*url\('([^']+)'\)"
            patron += '"[^>]*>\s*<span[^>]*><\/span>\s*.*?<span\s*class="pc_games_cracker"\s*>([^<]*)<\/span>\s*<span[^<]+'
            patron += "<img src='([^']+)'"
        
        #Si son series completas, ponemos un patrón especializado
        if item.extra == 'series':
            patron = '<(td)><a href="([^"]+)"\s*title="([^"]+)"\s*><[^>]+src="[^"]+\/(\d{4})[^"]+"[^>]+>(?:(\d+))?\s*<\/a>'
            if not scrapertools.find_single_match(data, patron):
                patron = '<div\s*class="pintinia[^>]*>\s*<div\s*class="[^>]*>\s*<h6\s*class="[^>]*>'
                patron += '\s*<a\s*href="([^"]+)"\s*title="([^"]+)"\s*>[^<]*<\/a>\s*'
                patron += '<\/h6>\s*<\/div>\s*<\/div>\s*<a[^<]*>\s*<img\s*style="background-image:'
                patron += "\s*url\('([^']+)'\)"
                patron += '"[^>]*>\s*<span[^>]*>[^<]*()<\/span>\s*<span[^>]+class="last_flags"\s*>[^<]+<img src=[^<]+title='
                patron += "'([^']+)"
            
        if not item.matches:                                                    # De pasada anterior o desde Novedades?
            matches = re.compile(patron, re.DOTALL).findall(data)
        else:
            matches = item.matches
            del item.matches
        
        if not matches and not '<p>Lo sentimos, pero que esta buscando algo que no esta aqui. </p>' in data \
                       and not item.extra2 and not '<h2>Sin resultados</h2> in data':       # error
            logger.error("ERROR 02: LISTADO: Ha cambiado la estructura de la Web " + " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 02: LISTADO: Ha cambiado la estructura de la Web.  Reportar el error con el log'))
            break                                       #si no hay más datos, algo no funciona, pintamos lo que tenemos
        
        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)
        
        #Buscamos la próxima y la última página
        patron_last = "<div\s*class='pagination'[^>]*>.*?<a\s*href='([^']+\/page\/(\d+)[^']+)'\s*>(?:&raquo;)?(?:\d+)?<\/a>\s*<\/div>"
        
        if last_page == 99999:                                                          #Si es el valor inicial, buscamos last page
            try:
                next_page_url, last_page = scrapertools.find_single_match(data, patron_last)      #cargamos la url y la última página
                last_page = int(last_page)
            except:                                                                     #Si no lo encuentra, lo ponemos a 1
                last_page = 1
                #logger.error('ERROR 03: LISTADO: Al obtener la paginación: ' + patron_last + ' / ' + next_page_url + ' / ' + str(last_page))
            #logger.debug('curr_page: ' + str(curr_page) + '/ last_page: ' + str(last_page))
            
        if last_page > 1:
            next_page_url = re.sub(r'\/page\/\d+\/', '/page/%s/' % curr_page, next_page_url)
            next_page_url = next_page_url.replace('&#038;', '&')
        else:
            next_page_url = item.url
        #logger.debug('curr_page: ' + str(curr_page) + '/ last_page: ' + str(last_page) + '/ next_page_url: ' + next_page_url)
        
        #Empezamos el procesado de matches
        #for _scrapedurl, _scrapedtitle, _scrapedthumb, _scrapedquality, _scrapedlanguage in matches:
        for _scrapedthumb, _scrapedurl, _scrapedtitle, _scrapedlanguage, _scrapedquality in matches:
            if item.extra == "search_OLD":
                scrapedurl = _scrapedtitle
                scrapedtitle = _scrapedthumb
                scrapedthumb = _scrapedquality
                scrapedquality = _scrapedlanguage
                scrapedlanguage = _scrapedurl
            else:
                scrapedurl = _scrapedurl
                scrapedtitle = _scrapedtitle
                scrapedthumb = _scrapedthumb
                scrapedquality = _scrapedquality
                scrapedlanguage = _scrapedlanguage
            
            title = scrapedtitle
            url = scrapedurl.replace('&#038;', '&')
            year = ''
            scrapedcategory = ''
            
            # Slugify, pero más light
            title = title.replace("á", "a").replace("é", "e").replace("í", "i")\
                    .replace("ó", "o").replace("ú", "u").replace("ü", "u")\
                    .replace("ï¿½", "ñ").replace("Ã±", "ñ")
            title = scrapertools.decode_utf8_error(title)
            
            #cnt_title += 1
            item_local = item.clone()                                                   #Creamos copia de Item para trabajar
            if item_local.tipo:                                                         #... y limpiamos
                del item_local.tipo
            if item_local.totalItems:
                del item_local.totalItems
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
                
            title_subs = []                                             #creamos una lista para guardar info importante
            item_local.language = ['VOSE']                              #creamos lista para los idiomas
            item_local.quality = scrapedquality                         #iniciamos calidad                                     
            item_local.thumbnail = scrapedthumb
            item_local.url = url.replace('&#038;', '&').replace('.io/', sufix).replace('.com/', sufix)       #guardamos la url final
            item_local.context = "['buscar_trailer']"

            item_local.contentType = "movie"                            #por defecto, son películas
            item_local.action = "findvideos"

            #Analizamos el formato de series
            if '/series' in scrapedurl or item_local.extra == 'series' or 'series' in scrapedcategory:
                item_local.extra = 'series'
                item_local.contentType = "tvshow"
                item_local.action = "episodios"
                item_local.season_colapse = True                        #Muestra las series agrupadas por temporadas
                
            #Detectamos idiomas            
            if "1.png" in scrapedlanguage: item_local.language += ['CAST']
            if "512.png" in scrapedlanguage or 'latino' in title.lower(): item_local.language += ['LAT']
            
            if '-3d' in scrapedurl:
                title = title.replace('3D', '').replace('3d', '')
                item_local.quality += ' 3D'

            #Detectamos el año
            item_local.infoLabels['year'] = '-'
            if year:
                try:
                    year = int(year)
                    if year >= 1970 and year <= 2040:
                        item_local.infoLabels["year"] = year
                except:
                    pass
            
            #Detectamos info importante a guardar para después de TMDB
            if "extendida" in title.lower() or "extended" in title.lower() or "v.e." in title.lower()or "v e " in title.lower():
                title_subs += ["[V. Extendida]"]
                title = title.replace("Version Extendida", "").replace("(Version Extendida)", "").replace("V. Extendida", "").replace("VExtendida", "").replace("V Extendida", "").replace("V.Extendida", "").replace("V  Extendida", "").replace("V.E.", "").replace("V E ", "")
            if scrapertools.find_single_match(title, '[m|M].*?serie'):
                title = re.sub(r'[m|M]iniserie', '', title)
                title_subs += ["Miniserie"]
            if scrapertools.find_single_match(title, '[s|S]aga'):
                title = re.sub(r'[s|S]aga', '', title)
                title_subs += ["Saga"]
            if scrapertools.find_single_match(title, '[c|C]olecc'):
                title = re.sub(r'[c|C]olecc...', '', title)
                title_subs += ["Colección"]
            
            #Empezamos a limpiar el título en varias pasadas
            patron = '\s?-?\s?(line)?\s?-\s?$'
            regex = re.compile(patron, re.I)
            title = regex.sub("", title)
            title = re.sub(r'\(\d{4}\s*?\)', '', title)
            title = re.sub(r'\[\d{4}\s*?\]', '', title)
            title = re.sub(r'[s|S]erie', '', title)
            title = re.sub(r'- $', '', title)
            title = re.sub(r'\d+[M|m|G|g][B|b]', '', title)
            title = re.sub(r'\(clasicos\)', "", title.lower()).strip()

            #Limpiamos el título de la basura innecesaria
            title = re.sub(r'(?i)TV|Online|Spanish|Torrent|en Espa\xc3\xb1ol|Español|Latino|Subtitulado|Blurayrip|Bluray rip|\[.*?\]|R2 Pal|\xe3\x80\x90 Descargar Torrent \xe3\x80\x91|Completa|Temporada|Descargar|Torren|\(iso\)|\(dvd.*?\)|(?:\d+\s*)?\d{3,4}p.*?$|extended|(?:\d+\s*)?bdrip.*?$|\(.*?\).*?$|iso$|unrated|\[.*?$|\d{4}$', '', title)
            if not title:
                continue
            #Obtenemos temporada y episodio si se trata de Episodios
            if item_local.contentType == "episode":
                patron = '(\d+)[x|X](\d+)'
                try:
                    item_local.contentSeason, item_local.contentEpisodeNumber = scrapertools.find_single_match(title, patron)
                except:
                    item_local.contentSeason = 1
                    item_local.contentEpisodeNumber = 0
                
                #Si son eisodios múltiples, lo extraemos
                patron1 = '\d+[x|X]\d+.?(?:y|Y|al|Al)?.?\d+[x|X](\d+)'
                epi_rango = scrapertools.find_single_match(title, patron1)
                if epi_rango:
                    item_local.infoLabels['episodio_titulo'] = 'al %s' % epi_rango
                    title = re.sub(patron1, '', title)
                else:
                    title = re.sub(patron, '', title)
            #Terminamos de limpiar el título
            title = re.sub(r'\??\s?\d*?\&.*', '', title)
            title = re.sub(r'[\(|\[]\s+[\)|\]]', '', title)
            title = title.replace('()', '').replace('[]', '').strip().lower().title()
            item_local.from_title = title.strip().lower().title()           #Guardamos esta etiqueta para posible desambiguación de título
            #Salvamos el título según el tipo de contenido
            if item_local.contentType == "movie":
                item_local.contentTitle = title
            else:
                item_local.contentSerieName = title.strip().lower().title()
            item_local.title = title.strip().lower().title()
            item_local.quality = item_local.quality.strip()
                
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
    tmdb.set_infoLabels(itemlist, __modo_grafico__, idioma_busqueda=idioma_busqueda)
    
    #Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
    item, itemlist = generictools.post_tmdb_listado(item, itemlist)

    # Si es necesario añadir paginacion
    if curr_page <= last_page and last_page > 1:
        if last_page:
            title = '%s de %s' % (curr_page-1, last_page)
        else:
            title = '%s' % curr_page-1

        itemlist.append(Item(channel=item.channel, action="listado", title=">> Página siguiente " + title, title_lista=title_lista, url=next_page_url, extra=item.extra, extra2=item.extra2, last_page=str(last_page), curr_page=str(curr_page)))

    return itemlist

    
def findvideos(item):
    logger.info()
    itemlist = []
    itemlist_t = []                                     #Itemlist total de enlaces
    itemlist_f = []                                     #Itemlist de enlaces filtrados
    if not item.language:
        item.language = ['CAST']                        #Castellano por defecto
    matches = []
    subtitles = []
    item.category = categoria
    
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

    if item.extra != 'episodios':
        #Bajamos los datos de la página
        data = ''
        if not item.matches:
            data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                                       s2=False, item=item, itemlist=[]) # Descargamos la página)
        if (not data and not item.matches) or response.code == 999:
            logger.error("ERROR 01: FINDVIDEOS: La Web no responde o la URL es erronea: " + item.url)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 01: FINDVIDEOS:.  La Web no responde o la URL es erronea. Si la Web está activa, reportar el error con el log', folder=False))
            
            if item.emergency_urls and not item.videolibray_emergency_urls:     #Hay urls de emergencia?
                matches = item.emergency_urls[1]                                #Restauramos matches de vídeos
                subtitles = item.emergency_urls[2]                              #Restauramos matches de subtítulos
                item.armagedon = True                                           #Marcamos la situación como catastrófica 
            else:
                if item.videolibray_emergency_urls:                             #Si es llamado desde creación de Videoteca...
                    return item                                                 #Devolvemos el Item de la llamada
                else:
                    return itemlist                                     #si no hay más datos, algo no funciona, pintamos lo que tenemos

        if not item.armagedon:
            #Extraemos el thumb
            if not item.thumbnail:
                patron = '<div class="secciones"><h1>[^<]+<\/h1><br\s*\/><br\s*\/><div class="fichimagen">\s*<img class="carat" src="([^"]+)"'
                item.thumbnail = scrapertools.find_single_match(data, patron)   #guardamos thumb si no existe
            
            #Extraemos quality, audio, year, country, size, scrapedlanguage
            patron = '<\/script><\/div><ul>(?:<li><label>Fecha de estreno <\/label>'
            patron += '[^<]+<\/li>)?(?:<li><label>Genero <\/label>[^<]+<\/li>)?'
            patron += '(?:<li><label>Calidad <\/label>([^<]+)<\/li>)?'
            patron += '(?:<li><label>Audio <\/label>([^<]+)<\/li>)?(?:<li><label>Fecha <\/label>'
            patron += '.*?(\d+)<\/li>)?(?:<li><label>Pais de Origen <\/label>([^<]+)<\/li>)?'
            patron += '(?:<li><label>Tamaño <\/label>([^<]+)<\/li>)?(<li> Idioma[^<]+<img src=.*?<br \/><\/li>)?'
            try:
                quality = ''
                audio = ''
                year = ''
                country = ''
                size = ''
                scrapedlanguage = ''
                quality, audio, year, country, size, scrapedlanguage = scrapertools.find_single_match(data, patron)
            except:
                pass
            if quality: item.quality = quality
            if audio: item.quality += ' %s' % audio.strip()
            if not item.infoLabels['year'] and year: item.infoLabels['year'] = year
            size = size.replace('GB', 'G·B').replace('Gb', 'G·b').replace('MB', 'M·B')\
                        .replace('Mb', 'M·b').replace('.', ',').replace('G B', 'G·B').replace('M B', 'M·B')
            if size: item.quality += ' [%s]' % size
            if size:
                item.title = re.sub(r'\s*\[\d+,?\d*?\s\w\s*[b|B]\]', '', item.title)    #Quitamos size de título, si lo traía
            
            language = []
            matches_lang = re.compile('(\d+.png)', re.DOTALL).findall(scrapedlanguage)
            for lang in matches_lang:
                if "1.png" in lang and not 'CAST' in language: language += ['CAST']
                if "512.png" in lang and not 'LAT' in language: language += ['LAT']
                if ("1.png" not in lang and "512.png" not in lang) and not 'VOSE' in language: language += ['VOSE']
            if language: item.language = language
        
            #Extraemos los enlaces .torrent
            #Modalidad de varios archivos
            patron = '<div\s*class="fichadescargat">\s*<\/div>\s*<div\s*class="table-responsive"[^>]+>'
            patron += '.*?<\/thead>\s*<tbody>(.*?)<\/tbody>\s*<\/table>\s*<\/div>'
            if scrapertools.find_single_match(data, patron):
                data_torrents = scrapertools.find_single_match(data, patron)
                patron = '<tr><td>.*?<\/td><td><a href="([^"]+)"[^>]+><[^>]+><\/a><\/td><\/tr>'
            #Modalidad de un archivo
            else:
                data_torrents = data
                patron = '<div\s*class="fichasubtitulos">\s*<\/div>\s*<\/li>\s*<\/ul>\s*<a\s*target="[^>]+\s*href="([^"]+)"'
                if not scrapertools.find_single_match(data_torrents, patron):
                    patron = '<div class="fichasubtitulos">.*?<\/div><\/li><\/ul>.*?<a href="([^"]+)"'
            
            if not item.matches:
                matches = re.compile(patron, re.DOTALL).findall(data)
            else:
                matches = item.matches
                del item.matches
            
            if not matches:                                                             #error
                logger.error("ERROR 02: FINDVIDEOS: No hay enlaces o ha cambiado la estructura de la Web " + " / PATRON: " + patron + data)
                itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 02: FINDVIDEOS: No hay enlaces o ha cambiado la estructura de la Web.  Verificar en la Web esto último y reportar el error con el log', folder=False))
                
                if item.emergency_urls and not item.videolibray_emergency_urls:         #Hay urls de emergencia?
                    matches = item.emergency_urls[1]                                    #Restauramos matches de vídeos
                    subtitles = item.emergency_urls[2]                                  #Restauramos matches de subtítulos
                    item.armagedon = True                                               #Marcamos la situación como catastrófica 
                else:
                    if item.videolibray_emergency_urls:                                 #Si es llamado desde creación de Videoteca...
                        return item                                                     #Devolvemos el Item de la llamada
                    else:
                        return itemlist                                     #si no hay más datos, algo no funciona, pintamos lo que tenemos
    
    else:                                                                           #SERIES: ya viene con las urls
        data = item.url                                                             #inicio data por compatibilidad
        matches = [item.url]                                                        #inicio matches por compatibilidad
    
    #Extraemos las urls de los subtítulos (Platformtools usa item.subtitle como sub-titulo por defecto)
    patron = '<div class="fichasubtitulos">\s*<label class="fichsub">\s*<a href="([^"]+)">Subtitulos\s*<\/a>\s*<\/label>'
    if scrapertools.find_single_match(data, patron) or item.subtitle:
        if item.extra == 'episodios':                                               #Si viene de Series, ya tengo la primera url
            subtitle = item.subtitle
            del item.subtitle
        else:
            subtitle = scrapertools.find_single_match(data, patron).replace('&#038;', '&').replace('.io/', sufix).replace('.com/', sufix)
        
        data_subtitle, response, item, itemlist = generictools.downloadpage(subtitle, timeout=timeout, 
                                                                            item=item, itemlist=[])      # Descargamos la página)
        if not data_subtitle:
            if item.emergency_urls and not item.videolibray_emergency_urls:         #Hay urls de emergencia?
                matches = item.emergency_urls[1]                                    #Restauramos matches de vídeos
                subtitles = item.emergency_urls[2]                                  #Restauramos matches de subtítulos
                item.armagedon = True                                               #Marcamos la situación como catastrófica 
        else:
            patron = '<tbody>(<tr class="fichserietabla_b">.*?<\/tr>)<\/tbody>'         #salvamos el bloque
            data_subtitle = scrapertools.find_single_match(data_subtitle, patron)
            patron = '<tr class="fichserietabla_b">.*?<a href="([^"]+)"'
            subtitles = re.compile(patron, re.DOTALL).findall(data_subtitle)            #Creamos una lista con todos los sub-títulos
        if subtitles:
            item.subtitle = []
            for subtitle in subtitles:
                subtitle = subtitle.replace('&#038;', '&').replace('.io/', sufix).replace('.com/', sufix)
                item.subtitle.append(subtitle)

    #logger.debug("PATRON: " + patron)
    #logger.debug(matches)
    #logger.debug(subtitles)
    #logger.debug(data)
    
    #Si es un lookup para cargar las urls de emergencia en la Videoteca...
    if item.videolibray_emergency_urls:
        item.emergency_urls = []                                                #Iniciamos emergency_urls
        item.emergency_urls.append([])                              #Reservamos el espacio para los .torrents locales
        matches_list = []                                                       # Convertimos matches-tuple a matches-list
        for tupla in matches:
            if isinstance(tupla, tuple):
                matches_list.append(list(tupla))
        if matches_list:
            item.emergency_urls.append(matches_list)                            # Salvamnos matches de los vídeos...  
        else:
            item.emergency_urls.append(matches)
        item.emergency_urls.append(subtitles)                                   #Salvamnos matches de los subtítulos
    
    #Llamamos al método para crear el título general del vídeo, con toda la información obtenida de TMDB
    if not item.videolibray_emergency_urls:
        item, itemlist = generictools.post_tmdb_findvideos(item, itemlist)

    #Ahora tratamos los enlaces .torrent
    for x, _scrapedurl in enumerate(matches):                                   #leemos los torrents con la diferentes calidades
        
        scrapedurl = generictools.convert_url_base64(_scrapedurl, host_torrent)
        # Si ha habido un cambio en la url, actualizados matches para emergency_urls
        if item.videolibray_emergency_urls and scrapedurl != _scrapedurl:
            item.emergency_urls[1][x] = scrapedurl
        
        #Generamos una copia de Item para trabajar sobre ella
        item_local = item.clone()

        item_local.url = scrapedurl.replace('&#038;', '&').replace('.io/', sufix).replace('.com/', sufix)
        if item.videolibray_emergency_urls:
            item.emergency_urls[0].append(scrapedurl)                           #guardamos la url y pasamos a la siguiente
            continue
        
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
        
        #Buscamos si ya tiene tamaño, si no, los buscamos en el archivo .torrent
        size = scrapertools.find_single_match(item_local.quality, '\s*\[(\d+,?\d*?\s\w\s*[b|B])\]')
        if not size and not item.videolibray_emergency_urls:
            if not item.armagedon:
                # Buscamos el tamaño en el .torrent desde la web    
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
                        .replace('Mb', 'M·b').replace('.', ',').replace('G B', 'G·B').replace('M B', 'M·B')
            item_local.title = re.sub(r'\s*\[\d+,?\d*?\s\w\s*[b|B]\]', '', item_local.title)    #Quitamos size de título, si lo traía
            item_local.quality = re.sub(r'\s*\[\d+,?\d*?\s\w\s*[b|B]\]', '', item_local.quality)    #Quitamos size de calidad, si lo traía
            item_local.torrent_info += '%s' % size                              #Agregamos size
            if not item.unify:
                item_local.torrent_info = '[%s]' % item_local.torrent_info.strip().strip(',')
            
        if item.armagedon:                                                      #Si es catastrófico, lo marcamos
            item_local.quality = '[/COLOR][COLOR hotpink][E] [COLOR limegreen]%s' % item_local.quality
        
        #Ahora pintamos el link del Torrent
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
        item_local.quality = item_local.quality.replace("--", "").replace("[]", "").replace("()", "").replace("(/)", "").replace("[/]", "").replace(".", ",").strip()
        
        if not size or 'Magnet' in size:
            item_local.alive = "??"                                             #Calidad del link sin verificar
        elif 'ERROR' in size and 'Pincha' in size:
            item_local.alive = "ok"                                             #link en error, CF challenge, Chrome disponible
        elif 'ERROR' in size and 'Introduce' in size:
            item_local.alive = "??"                                             #link en error, CF challenge, ruta de descarga no disponible
            item_local.channel = 'setting'
            item_local.action = 'setting_torrent'
            item_local.unify = False
            item_local.folder = False
            item_local.item_org = item.tourl()
        elif 'ERROR' in size:
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

    if item.videolibray_emergency_urls:                                         #Si ya hemos guardado todas las urls...
        return item                                                             #... nos vamos
    
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
    
    
def play(item):                                                                 #Permite preparar la descarga de los subtítulos externos
    logger.info()
    itemlist = []
    headers = []
    import os
    from core import downloadtools
    from core import httptools
    
    if item.subtitle:                                                           #Si hay urls de sub-títulos, se descargan
        headers.append(["User-Agent", httptools.random_useragent()])            #Se busca un User-Agent aleatorio
        if not os.path.exists(os.path.join(config.get_videolibrary_path(), "subtitles")):   #Si no hay carpeta se Sub-títulos, se crea
            os.mkdir(os.path.join(config.get_videolibrary_path(), "subtitles"))
        subtitles = []
        subtitles.extend(item.subtitle)
        item.subtitle = subtitles[0]                                            #ponemos por defecto el primeroç
        #item.subtitle = os.path.join(config.get_videolibrary_path(), os.path.join("subtitles", scrapertools.find_single_match(subtitles[0], '\/\d{2}\/(.*?\.\w+)$')))
        for subtitle in subtitles:                                              #recorremos la lista
            subtitle_name = scrapertools.find_single_match(subtitle, '\/\d{2}\/(.*?\.\w+)$')                #se pone el nombre del Sub-título
            subtitle_folder_path = os.path.join(config.get_videolibrary_path(), "subtitles", subtitle_name)         #Path de descarga
            ret = downloadtools.downloadfile(subtitle, subtitle_folder_path, headers=headers, continuar=True, silent=True)  #Descarga

    itemlist.append(item.clone())                                               #Reproducción normal
        
    return itemlist

    
def episodios(item):
    logger.info()
    itemlist = []
    item.category = categoria
    
    #logger.debug(item)

    if item.from_title:
        item.title = item.from_title
    if item.subtitle:
        del item.subtitle
    
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
    #if not item.infoLabels['tmdb_id']:
    try:
        tmdb.set_infoLabels(item, True, idioma_busqueda=idioma_busqueda)                    #TMDB de cada Temp
    except:
        pass
        
    modo_ultima_temp_alt = modo_ultima_temp
    if item.ow_force == "1":                                                                #Si hay un traspaso de canal o url, se actualiza todo 
        modo_ultima_temp_alt = False
    
    max_temp = 1
    if item.infoLabels['number_of_seasons']:
        max_temp = item.infoLabels['number_of_seasons']
    y = []
    if modo_ultima_temp_alt and item.library_playcounts:                                    #Averiguar cuantas temporadas hay en Videoteca
        patron = 'season (\d+)'
        matches = re.compile(patron, re.DOTALL).findall(str(item.library_playcounts))
        for x in matches:
            y += [int(x)]
        max_temp = max(y)

    # Descarga la página
    data = ''                                                                               #Inserto en num de página en la url
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                               item=item, itemlist=[])      # Descargamos la página
    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if not response.sucess:                                                 # Si ERROR o lista de errores ...
        return itemlist                                                     # ... Salimos

    patron = '<td\s*class="capitulonombre">\s*<img\s*src="([^"]+)"[^>]+><a[^>]*title="[^"]+"'
    patron += '>\s*([^<]*)<\/a>\s*<\/td>\s*<td\s*class="capitulodescarga">\s*<a[^>]*href="([^"]+)"()()()'
    if not scrapertools.find_single_match(data, patron):
        patron = '<td\s*class="capitulonombre">\s*<img\s*src="([^"]+)[^>]+>(?:<a\s*href="[^>]+>)?'
        patron += '(.*?)<\/a>\s*<\/td>\s*<td\s*class="capitulodescarga">\s*<a\s*href="([^"]+)[^>]+>'
        patron += '.*?(?:<td\s*class="capitulofecha">.*?(\d{4})?.*?<\/td>)?'
        patron += '(?:<td\s*class="capitulosubtitulo">\s*<a\s*href="([^"]+)[^>]+>.*?<\/td>)?'
        if not scrapertools.find_single_match(data, patron):
            patron = '<td\s*class="capitulonombre">\s*<img\s*src="([^"]+)[^>]+><a\s*'
            patron += '(?:target="[^"]*"\s*)?href="[^>]*title="([^"]+)">[^<]*<\/a>\s*<\/td>'
            patron += '\s*<td\s*class="capitulodescarga">\s*<a\s*(?:target="[^"]*"\s*)?'
            patron += 'href="([^"]+)"[^>]+>.*?(?:<td\s*class="capitulofecha">.*?(\d{4})?.*?<\/td>)?'
            patron += '.*?(?:<td\s*class="capitulosubtitulo">\s*<a\s*href="([^"]+)[^>]+>.*?<\/td>)?'
            patron += '.*?(?:<td\s*class="capitulodescarga">\s*<a\s*(?:target="[^"]*"\s*)?href="([^"]+)")?'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
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

    # Recorremos todos los episodios generando un Item local por cada uno en Itemlist
    for scrapedlanguage, scrapedtitle, scrapedurl, year, scrapedsubtitle, scrapedurl2 in matches:
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
        item_local.url = scrapedurl.replace('&#038;', '&').replace('.io/', sufix).replace('.in/', sufix).replace('.com/', sufix)
        if scrapedurl2: item_local.url = scrapedurl2.replace('&#038;', '&').replace('.io/', sufix).replace('.in/', sufix).replace('.com/', sufix)
        if scrapedsubtitle:
            item_local.subtitle = scrapedsubtitle.replace('&#038;', '&').replace('.io/', sufix).replace('.in/', sufix).replace('.com/', sufix)
        title = scrapedtitle
        item_local.language = []
        
        if "1.png" in scrapedlanguage: item_local.language += ['CAST']
        if "512.png" in scrapedlanguage or 'latino' in title.lower(): item_local.language += ['LAT']
        if ("1.png" not in scrapedlanguage and "512.png" not in scrapedlanguage) or "eng" in title.lower() or "sub" in title.lower(): item_local.language += ['VOSE']

        try:
            item_local.contentEpisodeNumber = 0
            if 'miniserie' in title.lower():
                item_local.contentSeason = 1
                title = title.replace('miniserie', '').replace('MiniSerie', '')
            elif 'completa' in title.lower():
                patron = '[t|T].*?(\d+) [c|C]ompleta'
                if scrapertools.find_single_match(title, patron):
                    item_local.contentSeason = int(scrapertools.find_single_match(title, patron))
            if not item_local.contentSeason:
                #Extraemos los episodios
                patron = '(\d{1,2})[x|X](\d{1,2})'
                item_local.contentSeason, item_local.contentEpisodeNumber = scrapertools.find_single_match(title, patron)
                item_local.contentSeason = int(item_local.contentSeason)
                item_local.contentEpisodeNumber = int(item_local.contentEpisodeNumber)
        except:
            logger.error('ERROR al extraer Temporada/Episodio: ' + title)
            item_local.contentSeason = 1
            item_local.contentEpisodeNumber = 0
        
        #Si son eisodios múltiples, lo extraemos
        patron1 = '\d+[x|X]\d{1,2}.?(?:y|Y|al|Al)?(?:\d+[x|X]\d{1,2})?.?(?:y|Y|al|Al)?.?\d+[x|X](\d{1,2})'
        epi_rango = scrapertools.find_single_match(title, patron1)
        if epi_rango:
            item_local.infoLabels['episodio_titulo'] = 'al %s' % epi_rango
            item_local.title = '%sx%s al %s -' % (str(item_local.contentSeason), str(item_local.contentEpisodeNumber).zfill(2), str(epi_rango).zfill(2))
        else:
            item_local.title = '%sx%s -' % (str(item_local.contentSeason), str(item_local.contentEpisodeNumber).zfill(2))

        if modo_ultima_temp_alt and item.library_playcounts:                    #Si solo se actualiza la última temporada de Videoteca
            if item_local.contentSeason < max_temp:
                break                                                           #Sale del bucle actual del FOR

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
        tmdb.set_infoLabels(itemlist, True, idioma_busqueda=idioma_busqueda)

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
        item.url = item.url % texto

        if texto != '':
            return listado(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []
 
 
def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    
    try:
        if categoria == 'peliculas':
            item.url = host + "peliculas-subtituladas/?filtro=estrenos"
            item.extra = "peliculas"
            item.channel = channel
            item.category_new= 'newest'

            itemlist = listado(item)
            if len(itemlist) > 0 and (">> Página siguiente" in itemlist[-1].title or "Pagina siguiente >>" in itemlist[-1].title):
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
