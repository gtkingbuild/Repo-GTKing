# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                 # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                 # Usamos el nativo de PY2 que es más rápido

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


IDIOMAS = {'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['torrent']

canonical = {
             'channel': 'elitetorrent', 
             'host': config.get_setting("current_host", 'elitetorrent', default=''), 
             'host_alt': ['https://www.elitetorrent.com/'], 
             'host_black_list': ['https://www.elitetorrent.dev/', 'https://www.elitetorrent.wtf/', 'https://elitetorrent.la/'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'

__modo_grafico__ = config.get_setting('modo_grafico', channel)
IDIOMAS_TMDB = {0: 'es', 1: 'en', 2: 'es,en'}
idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', channel)]    # Idioma base para TMDB
idioma_busqueda_VO = IDIOMAS_TMDB[2]                                                # Idioma para VO
#modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel) #Actualización sólo últ. Temporada?
#season_colapse = config.get_setting('season_colapse', channel)                  # Season colapse?
timeout = config.get_setting('timeout_downloadpage', channel)
filter_languages = config.get_setting('filter_languages', channel)              # Filtrado de idiomas?


def mainlist(item):
    logger.info()
    itemlist = []
    
    thumb_pelis = get_thumb("channels_movie.png")
    thumb_pelis_hd = get_thumb("channels_movie_hd.png")
    thumb_series = get_thumb("channels_tvshow.png")
    thumb_series_hd = get_thumb("channels_tvshow_hd.png")
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    home = ''
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, action="submenu", title="Novedades", 
                    url=host + home, extra="novedades", thumbnail=thumb_pelis))

    itemlist.append(Item(channel=item.channel, action="submenu", title="Películas", 
                    url=host + home, extra="peliculas", thumbnail=thumb_pelis))
    
    itemlist.append(Item(channel=item.channel, action="submenu", title="Series", 
                    url=host + home, extra="series", thumbnail=thumb_series))
    
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar", 
                    url=host + home, thumbnail=thumb_buscar, filter_lang=True))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                    folder=False, thumbnail=thumb_separador))
    
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                    thumbnail=thumb_settings))
    
    autoplay.show_option(item.channel, itemlist)            #Activamos Autoplay

    return itemlist
    
    
def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return
    
    
def submenu(item):
    logger.info()
    
    from datetime import date
    todays_date = date.today()
    
    itemlist = []
    item.filter_lang = True
    
    patron = '<div class="cab_menu"\s*>.*?<\/div>'                              #Menú principal
    data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, s2=False, canonical=canonical, 
                                                               patron=patron, item=item, itemlist=[])       # Descargamos la página
        
    # Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if not response.sucess or itemlist:                                         # Si ERROR o lista de errores ...
        return itemlist                                                         # ... Salimos

    data1 = scrapertools.find_single_match(data, patron)
    patron = '<div id="menu_langen"\s*>.*?<\/div>'                              #Menú de idiomas
    data1 += scrapertools.find_single_match(data, patron)
    
    patron = '<a href="(.*?)".*?title="(.*?)"'                                  #Encontrar todos los apartados
    matches = re.compile(patron, re.DOTALL).findall(data1)
    
    #logger.debug(patron)
    #logger.debug(matches)
    #logger.debug(data)
    
    if not matches:
        logger.error("ERROR 02: SUBMENU: Ha cambiado la estructura de la Web " + 
                        " / PATRON: " + patron + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.category + 
                        ': ERROR 02: SUBMENU: Ha cambiado la estructura de la Web.  '
                        + 'Reportar el error con el log'))
        return itemlist                                                         # Si no hay más datos, algo no funciona, pintamos lo que tenemos
    
    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.replace(" torrent", "").replace(" Torrent", "").replace("Series y ", "").title()
        if item.extra in ['novedades'] and 'estreno' in scrapedurl:
            if str(todays_date.year) in scrapedurl:
                title = 'Estrenos %s' % todays_date.year
            elif str(todays_date.year-1) in scrapedurl:
                title = 'Estrenos %s' % str(todays_date.year - 1)
            else:
                continue
            item.url = scrapedurl
            item.title = title
            return listado(item)
        
        elif item.extra not in ['novedades']:
            if 'estreno' in scrapedurl:
                continue
        
            if "castellano" in scrapedtitle.lower():                            # Evita la entrada de peliculas castellano del menú de idiomas
                continue
            
            if item.extra == "series":                                          # Tratamos Series
                if not "/serie" in scrapedurl:
                    continue
            else:                                                               # Tratamos Películas
                if "/serie" in scrapedurl:
                    continue
            
            if 'subtitulado' in scrapedtitle.lower() or 'latino' in scrapedtitle.lower() or 'original' in scrapedtitle.lower():
                item.filter_lang = False
        
            itemlist.append(item.clone(action="listado", title=title, url=scrapedurl))
            
    if item.extra == "series":                                                  # Añadimos Series VOSE que está fuera del menú principal
        itemlist.append(item.clone(action="listado", title="Series VOSE", url=host + "series-vose/", filter_lang=False))
    
    # Generos
    if item.extra == 'peliculas':
        patron = '<li\s*id="mas_categorias">\s*<i[^>]*>\s*<\/i>\s*categorias<\/li>(.*?)\/ul>'
        data1 = scrapertools.find_single_match(data, patron)
        
        patron = '<li>\s*<a\s*rel="nofollow"\s*href="([^"]+)"\s*title="[^"]+">\s*([^<]+)<\/a>\s*<\/li>'
        matches = re.compile(patron, re.DOTALL).findall(data1)
    
        #logger.debug(patron)
        #logger.debug(matches)
        #logger.debug(data1)
        
        if not matches:
            return itemlist
        
        itemlist.append(item.clone(action='', title='Géneros', url=''))
        for scrapedurl, scrapedtitle in sorted(matches):
            title = scrapertools.decode_utf8_error(scrapedtitle)
            itemlist.append(item.clone(action="listado", title='  - '+title, url=scrapedurl))
    
    return itemlist
    

def listado(item):
    logger.info()
    
    itemlist = []
    title_subs = []
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

    #Sistema de paginado para evitar páginas vacías o semi-vacías en casos de búsquedas con series con muchos episodios
    title_lista = []                            # Guarda la lista de series que ya están en Itemlist, para no duplicar lineas
    if item.title_lista:                                    # Si viene de una pasada anterior, la lista ya estará guardada
        title_lista.extend(item.title_lista)                                    # Se usa la lista de páginas anteriores en Item
        del item.title_lista                                                    # ... limpiamos
    matches = []

    post = None
    forced_proxy_opt = None
    referer = item.url
    if item.post:                                                               # Rescatamos el Post, si lo hay
        post = item.post
        forced_proxy_opt = None
    if item.referer:
        referer = item.referer
    
    patron_canonical = 'rel="?canonical"?\s*href="?([^"|>]+)["|>|\s*]'
    
    next_page_url = item.url
    #Máximo num. de líneas permitidas por TMDB. Máx de 5 segundos por Itemlist para no degradar el rendimiento
    while (cnt_title < cnt_tot and curr_page <= last_page and fin > time.time()) or item.matches:
    
        # Descarga la página
        data = ''
        cnt_match = 0                                                           # Contador de líneas procesadas de matches
        if not item.matches:                                                    # si no viene de una pasada anterior, descargamos
            data, response, item, itemlist = generictools.downloadpage(next_page_url, timeout=timeout_search, 
                                                                       post=post, s2=False, canonical=canonical, 
                                                                       forced_proxy_opt=forced_proxy_opt, referer=referer, 
                                                                       item=item, itemlist=itemlist)        # Descargamos la página)
            # Verificamos si ha cambiado el Host
            if response.host:
                next_page_url = response.url_new
            if scrapertools.find_single_match(data, patron_canonical):
                next_page_url = scrapertools.find_single_match(data, patron_canonical)
                if not 'page/' in next_page_url: 
                    if curr_page == 1:
                        next_page_url += 'page/1/'
                    else:
                        next_page_url += 'page/%s/' % curr_page
            referer = next_page_url
            
            curr_page += 1                                                      #Apunto ya a la página siguiente
            if not data:                                                        #Si la web está caída salimos sin dar error
                if len(itemlist) > 1:                                           # Si hay algo que pintar lo pintamos
                    last_page = 0
                    break
                return itemlist                                                 # Si no hay nada más, salimos directamente

        patron = '<div id="principal">.*?<\/nav><\/div><\/div>'
        data = scrapertools.find_single_match(data, patron)
        
        patron = '<li>\s*<div\s*class="[^"]+"\s*>\s*<a\s*href="([^"]+)"\s*'
        patron += 'title="([^"]+)"\s*(?:alt="[^"]+")?\s*>\s*<img\s*(?:class="[^"]+")?'
        patron += '\s*src="([^"]+)".*?border="[^"]+"\s*title="([^"]+)".*?<span\s*class="[^"]+"'
        patron += '\s*id="[^"]+"\s*>\s*<i>\s*<img\s*src="[^"]+"\s*data-src="[^"]+\/(\w+).png"'
        patron += '.*?<span\s*class="[^"]+"\s*style="[^"]+"\s*>\s*<i>(.*?)?<\/i>'
        patron += '(?:<\/span.*?="dig1"\s*>(.*?)?)?(?:<.*?="dig2">(.*?)?)?<\/span>\s*<\/div>'

        if not item.matches:                                                    # De pasada anterior o desde Novedades?
            matches = re.compile(patron, re.DOTALL).findall(data)
        else:
            matches = item.matches
            del item.matches
        
        if not matches and len(itemlist) > 0:                                   # Página vacía pero hay algo que pintar
            last_page = 0
            break
        
        if not matches and not '<title>503 Backend fetch failed</title>' in data and not 'No se han encontrado resultados' in data:
            logger.error("ERROR 02: LISTADO: Ha cambiado la estructura de la Web " 
                        + " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + 
                        ': ERROR 02: LISTADO: Ha cambiado la estructura de la Web.  ' 
                        + 'Reportar el error con el log'))
            break                                       #si no hay más datos, algo no funciona, pintamos lo que tenemos

        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)

        #Buscamos la próxima página
        next_page_url = re.sub(r'page\/(\d+)', 'page/%s' % str(curr_page), next_page_url)
        #logger.debug('curr_page: ' + str(curr_page) + ' / last_page: ' + str(last_page) + ' / page_factor: ' + str(page_factor))
        
        #Buscamos la última página
        if last_page == 99999:                                                  # Si es el valor inicial, buscamos
            patron_last = '(?i)siguiente[^<]*<\/a>\s*<a\s*href="[^"]+\/(\d+)\/[^"]*"'
            if not scrapertools.find_single_match(data, patron_last):
                patron_last = 'class="pagina">(\d+)<\/a>\s*<\/div>'
            try:
                last_page = int(scrapertools.find_single_match(data, patron_last))
                page_factor = float(len(matches)) / float(cnt_tot)
            except:                                                             # Si no lo encuentra, lo ponemos a 999
                last_page = 999
            #logger.debug('curr_page: ' + str(curr_page) + ' / last_page: ' + str(last_page) + ' / page_factor: ' + str(page_factor))

        for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedcategory, scrapedlang, \
                                scrapedcalidad, scrapedsize, scrapedsizet in matches:
            cnt_match += 1
            item_local = item.clone()                                           # Creamos copia de Item para trabajar

            title = scrapedtitle.replace(" torrent", "").replace(" Torrent", "").replace("Series y ", "")
            item_local.url = urlparse.urljoin(host, scrapedurl)
            item_local.thumbnail = urlparse.urljoin(host, scrapedthumbnail)
            
            if "---" in scrapedcalidad:                                         # limpiamos calidades
                scrapedcalidad = ''
            if "microhd" in title.lower():
                item_local.quality = "microHD"
            if not "/series-vose/" in item.url and not item_local.quality:
                item_local.quality = scrapedcalidad
            if scrapertools.find_single_match(item_local.quality, r'\d+\.\d+'):
                item_local.quality = ''
            if not item_local.quality and ("DVDRip" in title or "HDRip" in title \
                                      or "BR-LINE" in title or "HDTS-SCREENER" in title \
                                      or "BDRip" in title or "BR-Screener" in title \
                                      or "DVDScreener" in title or "TS-Screener" in title):
                item_local.quality = scrapertools.find_single_match(title, r'\((.*?)\)')
                item_local.quality = item_local.quality.replace("Latino", "")
            if not scrapedsizet or "---" in scrapedsizet:
                scrapedsize = ''
            else:
                item_local.quality += ' [%s %s]' % (scrapedsize.replace(".", ","), scrapedsizet)
            
            item_local.language = []                                            # Verificamos el idioma por si encontramos algo
            if "latino" in scrapedlang.lower() or "latino" in item.url or "latino" in title.lower():
                item_local.language += ["LAT"]
            if scrapedlang.lower() in ['vos', 'vose'] or "vose" in item.url or "vos" in item.url \
                            or "vose" in scrapedurl or "vos" in scrapedurl or "subt" in title.lower():
                    item_local.language += ["VOSE"]
            elif scrapedlang.lower() in ['ingles', 'inglés', 'english', 'original', 'vo'] or "ingles" in item.url \
                            or "vo" in item.url or "ingles" in scrapedurl or "vo" in scrapedurl:
                    item_local.language += ["VO"]
            if item_local.language == []:
                    item_local.language = ['CAST']                              # Por defecto
            
            if "dual" in scrapedlang.lower() or "dual" in title.lower():
                item_local.language[0:0] = ["DUAL"]

            #Limpiamos el título de la basura innecesaria
            title = title.replace("Dual", "").replace("dual", "").replace("Subtitulada", "").replace("subtitulada", "").replace("Subt", "").replace("subt", "").replace("Sub", "").replace("sub", "").replace("(Proper)", "").replace("(proper)", "").replace("Proper", "").replace("proper", "").replace("#", "").replace("(Latino)", "").replace("Latino", "")
            title = title.replace("- HDRip", "").replace("(HDRip)", "").replace("- Hdrip", "").replace("(microHD)", "").replace("(DVDRip)", "").replace("(HDRip)", "").replace("(BR-LINE)", "").replace("(HDTS-SCREENER)", "").replace("(BDRip)", "").replace("(BR-Screener)", "").replace("(DVDScreener)", "").replace("TS-Screener", "").replace(" TS", "").replace(" Ts", "").replace("temporada", "").replace("Temporada", "").replace("capitulo", "").replace("Capitulo", "")
            
            title = re.sub(r'(?i)\s*S\d+E\d+', '', title)
            title = re.sub(r'(?:\d+)?x.?\s?\d+', '', title)
            title = re.sub(r'\??\s?\d*?\&.*', '', title).title().strip()
            
            item_local.from_title = title                                       # Guardamos esta etiqueta para posible desambiguación de título
            
            title_subs = []                                                     # Creamos una lista para guardar info importante
            
            if item_local.extra == "peliculas":                                 # preparamos Item para películas
                if "/serie" in scrapedurl or "/serie" in item.url:
                    continue
            if not "/serie" in scrapedurl and not "/serie" in item.url:
                item_local.contentType = "movie"
                item_local.contentTitle = title
                item_local.extra = "peliculas"
            
            if item_local.extra == "series":                                    # preparamos Item para series
                if not "/serie" in scrapedurl and not "/serie" in item.url:
                    continue
            if "/serie" in scrapedurl or "/serie" in item.url:
                item_local.contentType = "episode"
                item_local.extra = "series"
                epi_mult = scrapertools.find_single_match(item_local.url, r'cap.*?-\d+-al-(\d+)')
                if scrapertools.find_single_match(scrapedtitle, r'(?i)\s*S(\d+)E(\d+)'):
                    item_local.contentSeason, item_local.contentEpisodeNumber = scrapertools.find_single_match(scrapedtitle, r'(?i)\s*S(\d+)E(\d+)')
                else:
                    item_local.contentSeason = scrapertools.find_single_match(item_local.url, r'temporada-(\d+)')
                    item_local.contentEpisodeNumber = scrapertools.find_single_match(item_local.url, r'cap.*?-(\d+)')
                if not item_local.contentSeason:
                    item_local.contentSeason = scrapertools.find_single_match(item_local.url, r'-(\d+)[x|X]\d+')
                if not item_local.contentEpisodeNumber:
                    item_local.contentEpisodeNumber = scrapertools.find_single_match(item_local.url, r'-\d+[x|X](\d+)')
                try:
                    if not item_local.contentSeason: item_local.contentSeason = 0
                    if not item_local.contentEpisodeNumber: item_local.contentEpisodeNumber = 1
                    item_local.contentSeason = int(item_local.contentSeason)
                    item_local.contentEpisodeNumber = int(item_local.contentEpisodeNumber)
                except:
                    pass
                if not item_local.contentSeason or item_local.contentSeason < 1:
                    item_local.contentSeason = 0
                if item_local.contentEpisodeNumber < 1:
                    item_local.contentEpisodeNumber = 1
                #title_subs += ['Episodio %sx%s' % (item_local.contentSeason, str(item_local.contentEpisodeNumber).zfill(2))]
                title_subs += [' (MAX_EPISODIOS)']
                
                item_local.contentSerieName = title
                if epi_mult:
                    title = "%sx%s al %s" % (item_local.contentSeason, str(item_local.contentEpisodeNumber).zfill(2), str(epi_mult).zfill(2))                         #Creamos un título con el rango de episodios
                else:
                    title = '%sx%s - ' % (str(item_local.contentSeason), str(item_local.contentEpisodeNumber).zfill(2))
            
            item_local.action = "findvideos"
            item_local.title = title.strip()
            item_local.infoLabels['year'] = "-"
            
            #Guarda la variable temporal que almacena la info adicional del título a ser restaurada después de TMDB
            item_local.title_subs = title_subs
            
            #Ahora se filtra por idioma, si procede, y se pinta lo que vale
            if config.get_setting('filter_languages', channel) > 0 and item.filter_lang:     #Si hay idioma seleccionado, se filtra
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
                        last_page_print=last_page_print, post=post, referer=referer))

    return itemlist

    
def findvideos(item):
    logger.info()
    itemlist = []
    itemlist_t = []                                                             #Itemlist total de enlaces
    itemlist_f = []                                                             #Itemlist de enlaces filtrados
    if not item.language:
        item.language = ['CAST']                                                #Castellano por defecto
        
    post = None
    forced_proxy_opt = None
    referer = None
    if item.post:                                                               # Rescatamos el Post, si lo hay
        post = item.post
    if item.referer:
        referer = item.referer
    
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

    #Bajamos los datos de la página
    if not item.matches:
        data, response, item, itemlist = generictools.downloadpage(item.url, timeout=timeout, canonical=canonical, 
                                                                   post=post, referer=referer, forced_proxy_opt=forced_proxy_opt, 
                                                                   s2=False, item=item, itemlist=[])        # Descargamos la página)

    if not data and not item.matches:
        logger.error("ERROR 01: FINDVIDEOS: La Web no responde o la URL es erronea: " + item.url + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.channel.capitalize() + \
                    ': ERROR 01: FINDVIDEOS:.  La Web no responde o la URL es erronea. Si la Web está activa, reportar el error con el log', 
                    folder=False))
        if item.emergency_urls and not item.videolibray_emergency_urls:         # Hay urls de emergencia?
            link_torrent = item.emergency_urls[0][0]                            # Guardamos la url del .Torrent
            link_magnet = item.emergency_urls[1][0]                             # Guardamos la url del .Magnet
            item.armagedon = True                                               # Marcamos la situación como catastrófica 
        else:
            if item.videolibray_emergency_urls:                                 # Si es llamado desde creación de Videoteca...
                return item                                                     # Devolvemos el Item de la llamada
            else:
                return itemlist                                                 # si no hay más datos, algo no funciona, pintamos lo que tenemos

    patron_t = '<a\s*href="([^"]+)"[^>]*>.escargar\s*el\s*\.torrent'
    patron_m = '<a\s*href="([^"]+)"[^>]*>.escargar\s*por\s*magnet'
    if not item.armagedon:                                                      # Si es un proceso normal, seguimos
        data_links = data
        for x in range(2):
            link_torrent = scrapertools.find_single_match(data_links, patron_t)
            if link_torrent:
                link_torrent = generictools.convert_url_base64(link_torrent, host)
                #link_torrent = urlparse.urljoin(host, link_torrent)
                link_torrent = link_torrent.replace(" ", "%20")                 # sustituimos espacios por %20, por si acaso
            #logger.info("link Torrent: " + link_torrent)
            
            link_magnet = scrapertools.find_single_match(data_links, patron_m)
            if 'magnet' not in link_magnet:
                link_magnet = generictools.convert_url_base64(link_magnet)
            #logger.info("link Magnet: " + link_magnet)
        
            if not (link_torrent and link_magnet) and x == 0:
                data_links = generictools.identifying_links(data_links)
            if '.torrent' in link_torrent and 'magnet' in link_magnet:
                break

    #Si es un lookup para cargar las urls de emergencia en la Videoteca...
    if (link_torrent or link_magnet) and item.videolibray_emergency_urls:
        item.emergency_urls = []
        item.emergency_urls.append([link_torrent])                              #Salvamos el enlace de .torrent
        item.emergency_urls.append([link_magnet])                               #Salvamos el enlace de .magnet
        return item                                                             #... y nos vamos
    
    #Añadimos el tamaño para todos
    size = scrapertools.find_single_match(item.quality, '\s\[(\d+,?\d*?\s\w\s*[b|B]s*)\]')
    if size:
        item.title = re.sub('\s\[\d+,?\d*?\s\w\s*[b|B]s*\]', '', item.title)    #Quitamos size de título, si lo traía
        item.quality = re.sub('\s\[\d+,?\d*?\s\w\s*[b|B]s*\]', '', item.quality)    #Quitamos size de calidad, si lo traía
    
    if not link_torrent and not link_magnet:                                    #error
        item = generictools.web_intervenida(item, data)                         #Verificamos que no haya sido clausurada
        if item.intervencion:                                                   #Sí ha sido clausurada judicialmente
            item, itemlist = generictools.post_tmdb_findvideos(item, itemlist)  #Llamamos al método para el pintado del error
        else:
            logger.error("ERROR 02: FINDVIDEOS: El archivo Torrent no existe o ha cambiado la estructura de la Web " + " / PATRON: " + patron_t + " / " + patron_m + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 02: FINDVIDEOS: El archivo Torrent no existe o ha cambiado la estructura de la Web.  Verificar en la Web y reportar el error con el log', folder=False))
        if item.emergency_urls and not item.videolibray_emergency_urls:         #Hay urls de emergencia?
            link_torrent = item.emergency_urls[0][0]                            #Guardamos la url del .Torrent
            link_magnet = item.emergency_urls[1][0]                             #Guardamos la url del .Magnet
            item.armagedon = True                                               #Marcamos la situación como catastrófica 
        else:
            if item.videolibray_emergency_urls:                                 #Si es llamado desde creación de Videoteca...
                return item                                                     #Devolvemos el Item de la llamada
            else:
                return itemlist                         #si no hay más datos, algo no funciona, pintamos lo que tenemos

    #Llamamos al método para crear el título general del vídeo, con toda la información obtenida de TMDB
    item, itemlist = generictools.post_tmdb_findvideos(item, itemlist)
    
    if not size and not item.armagedon:
        torrent_params['url'] = link_torrent
        torrent_params = generictools.get_torrent_size(link_torrent, torrent_params=torrent_params, 
                                                       referer=host, item=item) # Tamaño en el .torrent
        size = torrent_params['size']
        if torrent_params['torrents_path']: item.torrents_path = torrent_params['torrents_path']
    if size:
        size = size.replace('GB', 'G·B').replace('Gb', 'G·b').replace('MB', 'M·B')\
                        .replace('Mb', 'M·b').replace('.', ',')

    #Ahora pintamos el link del Torrent, si lo hay
    if link_torrent:		                                                    # Hay Torrent ?
        #Generamos una copia de Item para trabajar sobre ella
        item_local = item.clone()

        item_local.torrent_info = "[Torrent] "
        item_local.torrent_info += '%s' % size                                   #Agregamos size
        if not item.unify:
            item_local.torrent_info = '[%s]' % item_local.torrent_info.strip().strip(',')
        if item.armagedon:                                                      #Si es catastrófico, lo marcamos
            item_local.quality = '[/COLOR][COLOR hotpink][E] [COLOR limegreen]%s' % item_local.quality
        item_local.url = link_torrent
        if item_local.url and item.emergency_urls and not item.armagedon:
            item_local.torrent_alt = item.emergency_urls[0][0]                  #Guardamos la url del .Torrent ALTERNATIVA
        
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
            itemlist_f = filtertools.get_link(itemlist_f, item_local, list_language)  #Pintar pantalla, si no está vacío
            
        if len(itemlist_f) > 0:                                                 #Si hay entradas filtradas...
            itemlist.extend(itemlist_f)                                         #Pintamos pantalla filtrada
        else:                                                                       
            if config.get_setting('filter_languages', channel) > 0 and len(itemlist_t) > 0: #Si no hay entradas filtradas ...
                thumb_separador = get_thumb("next.png")                             #... pintamos todo con aviso
                itemlist.append(Item(channel=item.channel, url=host, title="[COLOR red][B]NO hay elementos con el idioma seleccionado[/B][/COLOR]", thumbnail=thumb_separador, folder=False))
            itemlist.extend(itemlist_t)                                         #Pintar pantalla con todo si no hay filtrado
    
    #Ahora pintamos el link del Magnet, si lo hay
    itemlist_t = []                                                             #Itemlist total de enlaces
    itemlist_f = []                                                             #Itemlist de enlaces filtrados
    if link_magnet:		                                                        # Hay Magnet ?
        #Generamos una copia de Item para trabajar sobre ella
        item_local = item.clone()
        
        item_local.torrent_info = "[Magnet] "
        item_local.torrent_info += '%s' % size                                  #Agregamos size
        if not item.unify:
            item_local.torrent_info = '[%s]' % item_local.torrent_info.strip().strip(',')
        if item.armagedon:                                                      #Si es catastrófico, lo marcamos
            item_local.quality = '[/COLOR][COLOR hotpink][E] [COLOR limegreen]%s' % item_local.quality
        item_local.url = link_magnet
        
        item_local.title = '[[COLOR yellow]?[/COLOR]] [COLOR yellow][Torrent][/COLOR] ' \
                        + '[COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR] %s' % \
                        (item_local.quality, str(item_local.language),  \
                        item_local.torrent_info)                                #Preparamos título de Magnet
                        
        item_local.title = re.sub(r'\s\[COLOR \w+\]\[\[?\]?\]\[\/COLOR\]', '', item_local.title)    #Quitamos etiquetas vacías
        item_local.title = re.sub(r'\s\[COLOR \w+\]\[\/COLOR\]', '', item_local.title)          #Quitamos colores vacíos
        item_local.alive = "??"                                                 #Calidad del link sin verificar
        item_local.action = "play"                                              #Visualizar vídeo
        item_local.server = "torrent"                                           #Seridor Torrent
        
        itemlist_t.append(item_local.clone())                                   #Pintar pantalla, si no se filtran idiomas
        
        # Requerido para FilterTools
        if config.get_setting('filter_languages', channel) > 0:                 #Si hay idioma seleccionado, se filtra
            itemlist_f = filtertools.get_link(itemlist_f, item_local, list_language)  #Pintar pantalla, si no está vacío
            
        if len(itemlist_f) > 0:                                                 #Si hay entradas filtradas...
            itemlist.extend(itemlist_f)                                         #Pintamos pantalla filtrada
        else:                                                                       
            if config.get_setting('filter_languages', channel) > 0 and len(itemlist_t) > 0: #Si no hay entradas filtradas ...
                thumb_separador = get_thumb("next.png")                             #... pintamos todo con aviso
                itemlist.append(Item(channel=item.channel, url=host, title="[COLOR red][B]NO hay elementos con el idioma seleccionado[/B][/COLOR]", thumbnail=thumb_separador, folder=False))
            itemlist.extend(itemlist_t)                                         #Pintar pantalla con todo si no hay filtrado
    
    #logger.debug("TORRENT: " + link_torrent + "MAGNET: " + link_magnet + " / title gen/torr: " + item.title + " / " + item_local.title + " / calidad: " + item_local.quality + " / tamaño: " + size + " / content: " + item_local.contentTitle + " / " + item_local.contentSerieName)
    #logger.debug(item_local)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)                                              #Lanzamos Autoplay
    
    return itemlist


def actualizar_titulos(item):
    logger.info()
    
    item = generictools.update_title(item) #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    #Volvemos a la siguiente acción en el canal
    return item
    

def search(item, texto):
    logger.info("search:" + texto)
    # texto = texto.replace(" ", "+")

    try:
        item.url = host + "page/1/?s=%s&x=0&y=0" % texto
        itemlist = listado(item)
        
        return itemlist

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
 
 
def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host + '/estrenos-/'
            item.extra = "peliculas"
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
