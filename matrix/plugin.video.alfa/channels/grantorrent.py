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
             'channel': 'grantorrent', 
             'host': config.get_setting("current_host", 'grantorrent', default=''), 
             'host_alt': ['https://grantorrent.fi/'], 
             'host_black_list': ['https://grantorrent.si/', 
                                 'https://grantorrent.re/', 'https://grantorrent.ac/', 'https://grantorrent.ch/'], 
             'pattern': '<div\s*class="flex[^>]*>\s*<a\s*href="([^"]+)"[^>]*>\s*.nicio\s*<', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'
domain = scrapertools.find_single_match(host, patron_domain)
host_torrent = 'https://files.' + domain
movies_sufix = 'peliculas/'
series_sufix = 'series_p/'

__modo_grafico__ = config.get_setting('modo_grafico', channel)                  # búsqueda TMDB ?
IDIOMAS_TMDB = {0: 'es', 1: 'en', 2: 'es,en'}
idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', channel)]    # Idioma base para TMDB
idioma_busqueda_VO = IDIOMAS_TMDB[2]                                                # Idioma para VO
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel) # Actualización sólo últ. Temporada?
timeout = config.get_setting('timeout_downloadpage', channel) * 2
season_colapse = config.get_setting('season_colapse', channel)                  # Season colapse?
filter_languages = config.get_setting('filter_languages', channel)              # Filtrado de idiomas?


def mainlist(item):
    logger.info()
    itemlist = []
    
    thumb_pelis = get_thumb("channels_movie.png")
    thumb_series = get_thumb("channels_tvshow.png")
    thumb_calidades = get_thumb("channels_movie_hd.png")
    thumb_generos = get_thumb("genres.png")
    #thumb_years = get_thumb("years.png")
    
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Películas", action="listado", 
                url=host + movies_sufix + 'page/1/', thumbnail=thumb_pelis, extra="peliculas", category=categoria))
    itemlist.append(Item(channel=item.channel, title="   -   por Calidad", action="calidades", 
                url=host + movies_sufix + 'page/1/', thumbnail=thumb_calidades, extra="peliculas", category=categoria))
    itemlist.append(Item(channel=item.channel, title="   -   por Genero", action="generos", 
                url=host + movies_sufix + 'page/1/', thumbnail=thumb_generos, extra="peliculas", category=categoria))
    #itemlist.append(Item(channel=item.channel, title="   -   por Año", action="annos", 
    #            url=host + movies_sufix + 'page/1/', thumbnail=thumb_years, extra="peliculas", category=categoria))
    # Buscar películas
    itemlist.append(Item(channel=item.channel, title="Buscar en Películas >>", action="search", 
                url=host + movies_sufix,  thumbnail=thumb_buscar, extra="search", extra2="peliculas", 
                category=categoria))
    
    itemlist.append(Item(channel=item.channel, title="Series", action="listado", 
                url=host + series_sufix + 'page/1/', thumbnail=thumb_series, extra="series", category=categoria))
    # Buscar series
    itemlist.append(Item(channel=item.channel, title="Buscar en Series >>", action="search", 
                url=host + series_sufix, thumbnail=thumb_buscar, extra="search", extra2="series", 
                category=categoria))

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
    
    
def calidades(item):
    logger.info()
    itemlist = []

    patron = '<select\s*id="quality"\s*name="quality"[^>]*>(.*?)<\/select><\/div>'
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, referer=host, 
                                                               patron=patron, item=item, itemlist=[])       # Descargamos la página

    data = scrapertools.find_single_match(data, patron)
    patron = '<option\s*value="([^"]+)"\s*>([^<]+)<\/option'
    matches = re.compile(patron, re.DOTALL).findall(data)

    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)

    if not matches:
        logger.error("ERROR 02: CALIDADES: Ha cambiado la estructura de la Web " + 
                        " / PATRON: " + patron + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: CALIDADES: Ha cambiado la estructura de la Web.  '
                        + 'Reportar el error con el log'))
        return itemlist                                             # si no hay más datos, algo no funciona, pintamos lo que tenemos

    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url, '?query&quality=%s&genre&year' % title)
        if '4k' in title.lower():
            url = url.replace('4k', '4k-2')
        if 'hdrip' in title.lower():
            url = url.replace('HDRip', 'HDRip-2')
        
        itemlist.append(item.clone(action="listado", title=title, url=url, 
                    extra2='calidades'))                                        # Listado de calidades
    
    return itemlist
    
    
def generos(item):
    logger.info()
    itemlist = []

    patron = '<select\s*id="genre"\s*name="genre"[^>]*>(.*?)<\/select><\/div>'
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, referer=host, 
                                                               patron=patron, item=item, itemlist=[])       # Descargamos la página

    # Obtenemos el bloque a tratar
    patron = '<select\s*id="genre"\s*name="genre"[^>]*>(.*?)<\/select><\/div>'
    data = scrapertools.find_single_match(data, patron)
    
    # Buscamos los géneros
    patron = '<option\s*value="([^"]+)"\s*>([^<]+)<\/option'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)
    
    if not matches:
        logger.error("ERROR 02: GENEROS: Ha cambiado la estructura de la Web " + 
                        " / PATRON: " + patron + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: GENEROS: Ha cambiado la estructura de la Web.  '
                        + 'Reportar el error con el log'))
        return itemlist                                             # si no hay más datos, algo no funciona, pintamos lo que tenemos

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.slugify(scrapedtitle).strip().capitalize()         # Limpiamos de tildes y demás

        itemlist.append(item.clone(action="listado", title=title, url=urlparse.urljoin(host, 'categoria/' + scrapedurl + '/page/1/'), 
                    extra2='generos', thumbnail=get_thumb('%s' % title, auto=True)))    # Listado de géneros

    return itemlist


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
    referer = host
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
                                                                       timeout=timeout_search, post=post, referer=referer, s2=False, 
                                                                       item=item, itemlist=itemlist)      # Descargamos la página)
            data = data.replace('<br>', '')
            
            # Verificamos si ha cambiado el Host
            if response.host:
                next_page_url = response.url_new

            curr_page += 1                                                      # Apunto ya a la página siguiente
            if not data or 'Error 503 Backend fetch failed' in data:            # Si la web está caída salimos sin dar error
                if len(itemlist) > 1 or item.extra2 in ['calidades', 'generos']:    # Si hay algo que pintar lo pintamos
                    last_page = 0
                    break
                logger.error("ERROR 01: LISTADO: La Web no responde o ha cambiado de URL: " + next_page_url + " / DATA: " + data)
                itemlist.append(item.clone(action='', title=item.channel.capitalize() + 
                            ': ERROR 01: LISTADO:.  La Web no responde o ha cambiado de URL.' 
                            + ' Si la Web está activa, reportar el error con el log'))
                return itemlist                                                 # Si no hay nada más, salimos directamente

        # Patrón para búsquedas, géneros, pelis y series
        patron = '<div\s*class="relative\s*my[^>]*>\s*<a\s*href="([^"]+)"[^>]*>\s*'
        patron += '(?:<div\s*x-show=[^>]*>\s*)?(?:<div\s*class="bg[^>]*>\s*<span>\s*'
        patron += '([^<]*)<\/span>\s*<\/div>\s*)?<\/div>\s*(?:<div\s*class="media[^>]*>\s*)?'
        patron += '<img\s*class="[^"]*"\s*src="([^"]+)"[^>]*>\s*<\/div>\s*(?:<div\s*x-show=[^>]*>\s*)?'
        patron += '<p\s*class=[^>]*>\s*([^<]*)<\/p>\s*(?:<p\s*class=[^>]*>\s*\d{2}\/\d{2}\/(\d{4})\s*<\/p>)?'
        if not item.matches:                                                    # De pasada anterior?
            matches = re.compile(patron, re.DOTALL).findall(data)
        else:
            matches = item.matches
            del item.matches
            
        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)

        if not matches and item.extra != 'search'and item.extra2 not in ['calidades', 'generos']:  # error o fin
            logger.error("ERROR 02: LISTADO: Ha cambiado la estructura de la Web " 
                        + " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + 
                        ': ERROR 02: LISTADO: Ha cambiado la estructura de la Web.  ' 
                        + 'Reportar el error con el log'))
            last_page = 0
            break                                       #si no hay más datos, algo no funciona, pintamos lo que tenemos
        
        if not matches and (item.extra == 'search' or item.extra2 in ['calidades', 'generos']):    # búsqueda vacía
            if len(itemlist) > 0:                                               # Si hay algo que pintar lo pintamos
                last_page = 0
                break
            return itemlist                                                     # Salimos
        
        #Buscamos la última página
        if last_page == 99999:                                                  # Si es el valor inicial, buscamos
            patron_page = '<\/svg>\s*<\/a>\s*<a\s*href="[^"]+\/(\d+)\/[^"]*"\s*rel="next"'
            if not scrapertools.find_single_match(data, patron_page):
                patron_page = '"go\s*to\s*page\s*\d+">\s*(\d+)\s*<\/a>\s*<\/span>\s*<\/div>'
            if scrapertools.find_single_match(data, patron_page):
                try:
                    last_page = int(scrapertools.find_single_match(data, patron_page))
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
        #for scrapedurl, scrapedthumbnail, scrapedquality, scrapedlang, scrapedtitle, scrapeddate in matches:
        for scrapedurl, scrapedquality, scrapedthumbnail, scrapedtitle, scrapeddate in matches:
            cnt_match += 1
            
            title = scrapertools.remove_htmltags(scrapedtitle).rstrip()         # Removemos Tags del título
            url = scrapedurl.replace(' ', '%20').replace('&amp;', '&')
            scrapedlang = ''

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
            if item_local.extra == 'search':
                if 'serie' in url:
                    item_local.extra = 'series'                                 # Serie búsqueda
                else:
                    item_local.extra = 'peliculas'                              # Película búsqueda
            
            # Guardamos los formatos para películas
            if item_local.extra == 'peliculas':
                item_local.contentType = "movie"
                item_local.action = "findvideos"
                item_local.referer = urlparse.urljoin(host, 'peliculas')

            # Guardamos los formatos para series y documentales
            elif item_local.extra == 'series':
                item_local.contentType = "tvshow"
                item_local.action = "episodios"
                item_local.referer = urlparse.urljoin(host, 'series_p')
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
            title = re.sub(r'(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d)[\]|\)]?', '', title)
            item_local.quality = re.sub(r'(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', 
                        '', item_local.quality).strip()
            
            item_local.thumbnail = urlparse.urljoin(host, scrapedthumbnail)

            item_local.url = urlparse.urljoin(host, url)                        # guardamos la url final
            item_local.context = "['buscar_trailer']"                           # ... y el contexto

            #Limpiamos el título de la basura innecesaria
            if 'saga' in title.lower():
                title_subs += 'Saga'
            title = re.sub(r'(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie', '', title).strip()
            title = re.sub(r'(?i)Dual|Subtitulada|Subt|Sub|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?', 
                        '', title).strip()
            title = re.sub(r'(?i)[-|\(]?\s*HDRip\)?|microHD|DVDRip|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?|\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|\s*ts', 
                        '', title).strip()
            title = re.sub(r'[\(|\[]\s+[\)|\]]', '', title)
            title = title.replace('()', '').replace('[]', '').replace('[4K]', '').replace('(4K)', '')

            #Salvamos el título según el tipo de contenido
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

            # El año que da el canal es el de publicación en la web, no el de release.  Si no está claro ponemos '-'
            item_local.infoLabels["year"] = '-'

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
                      'force': False, 
                      'data_torrent': True, 
                      'subtitles': True, 
                      'file_list': True
                      }
    
    post = None
    headers = None
    referer = None
    if item.referer:                                                            # Rescatamos el Referer, si lo hay
        referer = item.referer
    follow_redirects = True
    timeout_find = timeout
    if item.videolibray_emergency_urls:                                         #Si se están cacheando enlaces aumentamos el timeout
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
    
    # Bajamos los datos de las páginas
    if not item.matches:
        data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout_find, post=post, headers=headers, 
                                                                   referer=referer, s2=False, canonical=canonical, 
                                                                   follow_redirects=follow_redirects, 
                                                                   item=item, itemlist=[])              # Descargamos la página)

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

    patron = '()()<div\s*class\s*=\s*"mt-3"\s*>\s*<div\s*class\s*=\s*"flex[^>]*>\s*<a\s*href\s*=\s*"([^"]+)"'
    if not scrapertools.find_single_match(data, patron):
        patron = '()()<td class="px-6[^>]*>\s*<a\s*href\s*=\s*"([^"]+)"'

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
    for x, (scrapedlang, scrapedpassword, _scrapedurl) in enumerate(matches):
        
        scrapedurl = generictools.convert_url_base64(_scrapedurl, host_torrent)
        # Si ha habido un cambio en la url, actualizados matches para emergency_urls
        if item.videolibray_emergency_urls and scrapedurl != _scrapedurl:
            item.emergency_urls[1][x][4] = scrapedurl
        
        referer = None
        post= None
        headers = None
        
        # Puede ser necesario baja otro nivel para encontrar la página          ############  DESACTIVADO TEMPORALMENTE
        if not 'magnet:' in scrapedurl and not '.torrent' in scrapedurl and item.contentType == 'XXX':
            patron_torrent = '(?i)>\s*Pincha[^<]*<a\s*href="([^"]+)"'
            data_torrent, response, item, itemlist = generictools.downloadpage(scrapedurl, timeout=timeout, referer=referer, canonical=canonical, 
                                                                               post=post, headers=headers, s2=False, patron=patron_torrent, 
                                                                               item=item, itemlist=itemlist)        # Descargamos la página)
                                              
            #logger.debug("PATRON: " + patron_torrent)
            #logger.debug(data_torrent)
            
            # Verificamos si se ha cargado una página, y si además tiene la estructura correcta
            if not data_torrent or response.code == 999:
                if item.emergency_urls and not item.videolibray_emergency_urls: # Hay urls de emergencia?
                    if len(item.emergency_urls) > 1 and item.emergency_urls[1]:
                        matches = item.emergency_urls[1]                        # Restauramos matches de vídeos
                    elif len(item.emergency_urls) == 1 and item.emergency_urls[0]:
                        matches = item.emergency_urls[0]                        # Restauramos matches de vídeos - OLD FORMAT
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
            if "dual" in scrapedlang.lower() or "dual" in item_local.url:
                item_local.language[0:0] = ["DUAL"]
            if not item_local.language:
                item_local.language = ['CAST']                                  # [CAST] por defecto
        
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
        if item.contentType != 'movie':
            size = ''
        elif item_local.torrent_info:
            size = item_local.torrent_info
        else:
            size = ''
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
        if item_local.url.startswith('magnet:'):
            item_local.torrent_info += ' Magnet'
        if item_local.torrent_info:
            item_local.torrent_info = item_local.torrent_info.strip().strip(',')
            #item.torrent_info = item_local.torrent_info
            if not item.unify:
                item_local.torrent_info = '[%s]' % item_local.torrent_info
   
        # Si tiene contraseña, la guardamos y la pintamos
        if scrapedpassword and scrapedpassword != 'Sin clave':
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
    search_seasons = True

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
    for _url in list_temp:                                                      # Recorre todas las temporadas encontradas
        url = _url
        data, response, item, itemlist = generictools.downloadpage(url, timeout=timeout, s2=False, canonical=canonical, 
                                                                   item=item, itemlist=itemlist)        # Descargamos la página
        # Verificamos si ha cambiado el Host
        if response.host:
            for x, u in enumerate(list_temp):
                list_temp[x] = list_temp[x].replace(scrapertools.find_single_match(url, patron_host), response.host.rstrip('/'))
            url = response.url_new
        
        #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
        if not response.sucess:                                                         # Si ERROR o lista de errores ...
            if len(itemlist) > 1 or not 'timeout' in response.code:             # puede ser un enlace erroneo de una temporada.  Siguiente...
                continue
            logger.error("ERROR 01: EPISODIOS: La Web no responde o ha cambiado de URL " + 
                            " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.category + 
                            ': ERROR 01: EPISODIOS: La Web no responde o ha cambiado de URL.  '
                            + 'Reportar el error con el log'))
            return itemlist                                                     # Si no hay nada más, salimos directamente

        patron = '<img\s*src="[^"]*"\s*title="([^"]*)"[^>]*>\s*<\/td>\s*<td\s*class=[^>]*>'
        patron += '\s*([^<]*)<.*?<p\s*class="bg[^>]*>([^<]*)<\/p>\s*<\/td>\s*'
        patron += '<td\s*class="px[^>]*>\s*<a\s*href="([^"]+)"'
        
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
        for scrapedlang, temp_epi, scrapedpassword, scrapedurl_la in matches:
            
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
            
            title = temp_epi
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
                if "temporada" in title.lower() or "completa" in title.lower(): #si es una temporada, lo aceptamos como episodio 1
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
                    itemlist[-1].matches.insert(0, (scrapedlang, scrapedpassword, scrapedurl))
                else:
                    itemlist[-1].matches.append((scrapedlang, scrapedpassword, scrapedurl))
                continue                                                        #ignoramos el episodio duplicado
                
            # Salvamos los matches de cada episodio para findvideos
            item_local.matches.append((scrapedlang, scrapedpassword, scrapedurl))

            if season_display > 0:                                              # Son de la temporada estos episodios?
                if item_local.contentSeason > season_display:
                    break
                elif item_local.contentSeason < season_display:
                    continue

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
    
    if "/series" in item.url:
        item.url = "%spage/1/?s=%s&filtro=series" % (host, texto)
        item.title = "Series"
    else:
        item.url = "%spage/1/?s=%s&filtro=" % (host, texto)
        item.title = "Películas"
    item.extra = "search"
    
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

    try:
        for cat in ['peliculas', 'series', '4k']:
            if cat != categoria: continue
                
            item.extra = cat
            if cat == '4k': item.extra = 'peliculas'
            
            if cat == 'peliculas': item.url = host
            if cat == 'series': item.url = host + series_sufix
            if cat == '4k': item.url = host + 'categoria/4k-2/'

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
