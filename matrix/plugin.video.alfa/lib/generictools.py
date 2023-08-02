# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# GenericTools
# ------------------------------------------------------------
# Código reusable de diferentes partes de los canales que pueden
# ser llamadados desde otros canales, y así carificar el formato
# y resultado de cada canal y reducir el costo su mantenimiento
# ------------------------------------------------------------

from __future__ import division
from builtins import zip
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urllib
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido
    import urllib 

from builtins import range
from past.utils import old_div

import re
import os
import datetime
import time
import traceback
import inspect
import json
import base64
import random

from channelselector import get_thumb
from core import scrapertools
from core import servertools
from core import channeltools
from core import filetools
from core import tmdb
from core.item import Item
from platformcode import config, logger, unify

import xbmcgui
alfa_caching = False
window = None
video_list_str = ''

try:
    window = xbmcgui.Window(10000)
    alfa_caching = bool(window.getProperty("alfa_caching"))
    if not alfa_caching:
        window.setProperty("alfa_videolab_movies_list", '')
        window.setProperty("alfa_videolab_series_list", '')
except Exception:
    alfa_caching = False
    window = None
    video_list_str = ''
    logger.error(traceback.format_exc())

channel_py = "wolfmax4k"
channel_py_episode_list = {}
idioma_busqueda = 'es'
idioma_busqueda_VO = 'es,en'
movies_videolibrary_path = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_movies"))
series_videolibrary_path = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_tvshows"))
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'
patron_canal = '(?:http.*\:)?\/\/(?:ww[^\.]*)?\.?(\w+)\.\w+(?:\/|\?|$)'
patron_local_torrent = '(?i)(?:(?:\\\|\/)[^\[]+\[\w+\](?:\\\|\/)[^\[]+\[\w+\]_\d+\.torrent|magnet\:)'
find_alt_domains = 'atomohd'   # Solo poner uno.  Alternativas: pctmix, pctmix1, pctreload, pctreload1, maxitorrent, descargas2020, pctnew
btdigg_url = config.BTDIGG_URL
btdigg_label = config.BTDIGG_LABEL
btdigg_label_B = config.BTDIGG_LABEL_B
DEBUG = config.get_setting('debug_report', default=False)


def convert_url_base64(url, host='', referer=None, rep_blanks=True, force_host=False, item=Item()):
    logger.info('URL: ' + url + ', HOST: ' + host)
    
    host_whitelist = ['mediafire.com']
    host_whitelist_skip = ['adfly.mobi']
    domain = scrapertools.find_single_match(url, patron_domain)

    url_base64 = url
    url_sufix = ''

    if scrapertools.find_single_match(url, patron_local_torrent):
        return url_base64 + url_sufix

    if ('&dn=' in url_base64 or '&tr=' in url_base64) and not 'magnet:' in url_base64:
        url_base64_list = url_base64.split('&')
        url_base64 = url_base64_list[0]
        for param in url_base64_list[1:]:
            url_sufix += '&%s' % param
    if '=http' in url_base64 and not 'magnet:' in url_base64:
        url_base64 = scrapertools.find_single_match(url_base64, '=(http.*?$)')

    if len(url_base64) > 1 and not 'magnet:' in url_base64 and not '.torrent' in url_base64:
        patron_php = 'php(?:#|\?\w=)(.*?)(?:\&|$)'
        if not scrapertools.find_single_match(url_base64, patron_php):
            patron_php = '\?(?:\w+=.*&)?(?:urlb64|anonym)?=(.*?)(?:\&|$)'

        url_base64 = scrapertools.find_single_match(url_base64, patron_php)
        if not url_base64:
            logger.info('Url base64 vacía: Patron incorrecto: %s' % patron_php)
            url_base64 = url
        else:
            try:
                # Da hasta 20 pasadas o hasta que de error
                for x in range(20):
                    url_base64 = base64.b64decode(url_base64).decode('utf-8')
                logger.info('Url base64 después de 20 pasadas (incompleta): %s' % url_base64)
                url_base64 = url
            except Exception:
                if url_base64 and url_base64 != url:
                    logger.info('Url base64 convertida: %s' % url_base64)
                    if rep_blanks: url_base64 = url_base64.replace(' ', '%20')
                #logger.error(traceback.format_exc())
                if not url_base64:
                    url_base64 = url
                if url_base64.startswith('magnet') or url_base64.endswith('.torrent') or (domain and domain in host_whitelist_skip):
                    return url_base64 + url_sufix
                
                from lib.unshortenit import sortened_urls
                if domain and domain in host_whitelist:
                    url_base64_bis = sortened_urls(url_base64, url_base64, host, referer=referer, alfa_s=True, item=item)
                else:
                    url_base64_bis = sortened_urls(url, url_base64, host, referer=referer, alfa_s=True, item=item)
                host_name = scrapertools.find_single_match(url_base64_bis, patron_host)
                if host_name:
                    url_base64_bis = host_name + url_base64_bis.replace(host_name, '').replace('//', '/')
                else:
                    url_base64_bis = url_base64_bis.replace('//', '/')
                domain_bis = scrapertools.find_single_match(url_base64_bis, patron_domain)
                if domain_bis: domain = domain_bis
                if url_base64_bis != url_base64:
                    url_base64 = url_base64_bis
                    logger.info('Url base64 RE-convertida: %s' % url_base64)
                
    if not domain: domain = 'default'
    if host and host not in url_base64 and not url_base64.startswith('magnet') \
                    and (not url_base64.startswith('http') or force_host) and domain not in str(host_whitelist):
        url_base64 = urlparse.urljoin(host, url_base64)
        if force_host:
            url_base64 = url_base64.replace('%s://%s' % (urlparse.urlparse(url_base64).scheme, 
                                                         urlparse.urlparse(url_base64).netloc), host.rstrip('/'))
        if url_base64 != url or host not in url_base64:
            host_name = scrapertools.find_single_match(url_base64, patron_host) + '/'
            url_base64 = re.sub(host_name, host, url_base64)
            logger.info('Url base64 urlparsed: %s' % url_base64)

    return url_base64 + url_sufix


def js2py_conversion(data, url, domain_name='', channel='', size=10000, resp={}, **kwargs):

    if PY3 and isinstance(data, bytes):
        if not b'Javascript is required' in data[:size]:
            return data if not resp else resp
    elif not 'Javascript is required' in data[:size]:
        return data if not resp else resp
    
    from lib import js2py
    from core import httptools
    
    if DEBUG: logger.debug('url: %s; domain_name: %s, channel: %s, size: %s; kwargs: %s, DATA: %s' \
                            % (url, domain_name, channel, size, kwargs, data[:1000]))
    json = kwargs.pop('json', False)
    soup = kwargs.get('soup', False)
    
    # Obtiene nombre del dominio para la cookie
    if not domain_name:
        domain_name = httptools.obtain_domain(url)

    # Obtiene nombre del canal que hace la llamada para marcarlo en su settings.xml
    if not channel and channel is not None:
        channel = inspect.getmodule(inspect.currentframe().f_back.f_back)
        try:
            channel = channel.__name__.split('.')[1]
        except Exception:
            channel = ""
    
    # Obtiene el código JS
    if PY3 and isinstance(data, bytes):
        data = "".join(chr(x) for x in bytes(data))
    patron = ',\s*S="([^"]+)"'
    data_new = scrapertools.find_single_match(data, patron)
    if not data_new:
        patron = ",\s*S='([^']+)'"
        data_new = scrapertools.find_single_match(data, patron)
    if not data_new:
        logger.error('js2py_conversion: NO data_new')
        return data if not resp else resp
        
    # Descompone el código Base64
    try:
        # Da hasta 10 pasadas o hasta que de error
        for x in range(10):
            data_end = base64.b64decode(data_new).decode('utf-8')
            data_new = data_end
    except Exception:
        js2py_code = data_new
    else:
        logger.error('js2py_conversion: base64 data_new NO Funciona: ' + str(data_new))
        return data if not resp else resp
    if not js2py_code:
        logger.error('js2py_conversion: NO js2py_code BASE64')
        return data if not resp else resp

    def atob(s):
        import base64
        return base64.b64decode('{}'.format(s)).decode('utf-8')
     
    # Hace las llamadas a js2py para obtener la cookie
    js2py_code = js2py_code.replace('document', 'window').replace(" location.reload();", "")
    js2py.disable_pyimport()
    context = js2py.EvalJs({'atob': atob})
    new_cookie = context.eval(js2py_code)
    
    logger.info('new_cookie: ' + new_cookie)

    # Construye y salva la la cookie
    dict_cookie = {'domain': domain_name,}

    if ';' in new_cookie:
        new_cookie = new_cookie.split(';')[0].strip()
        namec, valuec = new_cookie.split('=')
        dict_cookie['name'] = namec.strip()
        dict_cookie['value'] = valuec.strip()
    res = httptools.set_cookies(dict_cookie)
    
    # Si existe channel se marca en settings como cookie regenerada
    if channel:
        try:
            config.set_setting("cookie_ren", True, channel=channel)
        except Exception:
            pass

    # Se ejecuta de nuevo la descarga de la página, ya con la nueva cookie
    data_new = ''
    response = httptools.downloadpage(url, **kwargs)

    if resp:
        return response
    if response.code not in httptools.SUCCESS_CODES + httptools.REDIRECTION_CODES:
        return data

    if json and response.json:
        data_new = response.json
    elif soup and response.soup:
        data_new = response.soup
    else:
        data_new = re.sub(r"\n|\r|\t", "", response.data)
    if data_new:
        data = data_new
    
    return data


def check_blocked_IP(data, itemlist, url, canonical={}, verbose=True):
    logger.info()
    thumb_separador = get_thumb("next.png")
    channel = canonical.get('channel', '')
    
    host = scrapertools.find_single_match(url, patron_host)
    
    if 'Please wait while we try to verify your browser...' in data:
        logger.error('ERROR 99: La IP ha sido bloqueada por la Web "%s" / DATA: %s' % (host, data[:2500]))
        
        itemlist.append(Item(channel=channel, url=host, 
                        title="[COLOR %s]La IP ha sido bloqueada por la Web.[/COLOR]" \
                        % get_color_from_settings('library_color', default='yellow'), 
                        folder=False, thumbnail=thumb_separador))
        itemlist.append(Item(channel=channel, url=host, 
                        title="[COLOR %s]Fuerce la renovación de la IP en el Router[/COLOR]" \
                        % get_color_from_settings('library_color', default='yellow'), 
                        folder=False, thumbnail=thumb_separador))
        if verbose:
            from platformcode.platformtools import dialog_notification
            dialog_notification("IP bloqueada", "%s: Reiniciar ROUTER" % channel.upper())
        return (True, itemlist)                                                 # Web bloqueada
    
    return (False, itemlist)                                                    # No hay bloqueo


def get_color_from_settings(label, default='white'):
    
    color = config.get_setting(label)
    if not color:
        return default
    
    color = scrapertools.find_single_match(color, '\](\w+)\[')
    
    return color or default


def update_title(item):
    logger.info()
    from core import scraper

    """
    Utilidad para desambiguar Títulos antes de añadirlos a la Videoteca.  Puede ser llamado desde Videolibrarytools
    o desde Episodios en un Canal.  Si se llama desde un canal, la llamada sería así (incluida en post_tmdb_episodios(item, itemlist)):
    
        #Permitimos la actualización de los títulos, bien para uso inmediato, o para añadir a la videoteca
        item.from_action = item.action      #Salvamos la acción...
        item.from_title = item.title        #... y el título
        itemlist.append(item.clone(title="** [COLOR limegreen]Actualizar Títulos - vista previa videoteca[/COLOR] **", action="actualizar_titulos", extra="episodios", tmdb_stat=False))
    
    El canal deberá añadir un método para poder recibir la llamada desde Kodi/Alfa, y poder llamar a este método:
    
    def actualizar_titulos(item):
        logger.info()
        itemlist = []
        from lib import generictools
        from platformcode import launcher
        
        item = generictools.update_title(item) #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels
        
        #Volvemos a la siguiente acción en el canal
        return launcher.run(item)
    
    Para desambiguar títulos, se provoca que TMDB pregunte por el título realmente deseado, borrando los IDs existentes
    El usuario puede seleccionar el título entre los ofrecidos en la primera pantalla
    o puede cancelar e introducir un nuevo título en la segunda pantalla
    Si lo hace en "Introducir otro nombre", TMDB buscará automáticamente el nuevo título
    Si lo hace en "Completar Información", cambia al nuevo título, pero no busca en TMDB.  Hay que hacerlo de nuevo
    Si se cancela la segunda pantalla, la variable "scraper_return" estará en False.  El usuario no quiere seguir
    """
    #logger.debug(item)
    
    #Restauramos y borramos las etiquetas intermedias (si se ha llamado desde el canal)
    if item.from_action:
        item.action = item.from_action
        del item.from_action
    if item.from_update:
        if item.from_title_tmdb:                                    # Si se salvó el título del contenido devuelto por TMDB, se restaura.
            item.title = item.from_title_tmdb
    else:
        item.add_videolibrary = True                                # Estamos Añadiendo a la Videoteca.  Indicador para control de uso de los Canales
    if item.add_videolibrary:
        if item.season_colapse: del item.season_colapse
        if item.from_num_season_colapse: del item.from_num_season_colapse
        if item.from_title_season_colapse: del item.from_title_season_colapse
        if item.contentType == "movie":
            if item.from_title_tmdb:                                # Si se salvó el título del contenido devuelto por TMDB, se restaura.
                item.title = item.from_title_tmdb
            del item.add_videolibrary
        if item.channel_host:                                       # Borramos ya el indicador para que no se guarde en la Videoteca
            del item.channel_host
        if item.contentTitle:
            item.contentTitle = re.sub(r' -%s-' % item.category, '', item.contentTitle)
            item.title = re.sub(r' -%s-' % item.category, '', item.title)
    if item.contentType == 'movie':
        from_title_tmdb = item.contentTitle
    else:
        from_title_tmdb = item.contentSerieName
    
    # Sólo ejecutamos este código si no se ha hecho antes en el Canal.  Por ejemplo, si se ha llamado desde Episodios o Findvideos,
    # ya no se ejecutará al Añadia a Videoteca, aunque desde el canal se podrá llamar tantas veces como se quiera, 
    # o hasta que encuentre un título no ambiguo
    if item.tmdb_stat:
        if item.from_title_tmdb: del item.from_title_tmdb
        if item.from_title: del item.from_title
        item.from_update = True
        del item.from_update
    else:
        new_item = item.clone()                                                 # Salvamos el Item inicial para restaurarlo si el usuario cancela
        #Borramos los IDs y el año para forzar a TMDB que nos pregunte
        if 'tmdb_id' in item.infoLabels: item.infoLabels['tmdb_id'] = ''
        if 'tvdb_id' in item.infoLabels: item.infoLabels['tvdb_id'] = ''
        if 'imdb_id' in item.infoLabels: item.infoLabels['imdb_id'] = ''
        if 'IMDBNumber' in item.infoLabels: item.infoLabels['IMDBNumber'] = ''
        if item.infoLabels['season']: del item.infoLabels['season']             # Funciona mal con num. de Temporada.  Luego lo restauramos
        item.infoLabels['year'] = '-'
        
        if item.from_title:
            if item.from_title_tmdb:
                if scrapertools.find_single_match(item.from_title_tmdb, '^(?:\[COLOR \w+\])?(.*?)(?:\[)'):
                    from_title_tmdb = scrapertools.find_single_match(item.from_title_tmdb, '^(?:\[COLOR \w+\])?(.*?)(?:\[)').strip()
            item.title = item.title.replace(from_title_tmdb, item.from_title)
            item.infoLabels['title'] = item.from_title
            
            if item.from_title_tmdb: del item.from_title_tmdb
        if not item.from_update and item.from_title: del item.from_title

        if item.contentSerieName:                           # Copiamos el título para que sirva de referencia en menú "Completar Información"
            item.infoLabels['originaltitle'] = item.contentSerieName
            item.contentTitle = item.contentSerieName
        else:
            item.infoLabels['originaltitle'] = item.contentTitle
            
        scraper_return = scraper.find_and_set_infoLabels(item)

        if not scraper_return:  #Si el usuario ha cancelado, restituimos los datos a la situación inicial y nos vamos
            item = new_item.clone()
        else:
            #Si el usuario ha cambiado los datos en "Completar Información" hay que ver el título definitivo en TMDB
            if not item.infoLabels['tmdb_id']:
                if item.contentSerieName:
                    item.contentSerieName = item.contentTitle                   # Se pone título nuevo
                item.infoLabels['noscrap_id'] = ''                              # Se resetea, por si acaso
                item.infoLabels['year'] = '-'                                   # Se resetea, por si acaso
                scraper_return = scraper.find_and_set_infoLabels(item)          # Se intenta de nuevo

                #Parece que el usuario ha cancelado de nuevo.  Restituimos los datos a la situación inicial
                if not scraper_return or not item.infoLabels['tmdb_id']:
                    item = new_item.clone()
                else:
                    item.tmdb_stat = True                                       # Marcamos Item como procesado correctamente por TMDB (pasada 2)
            else:
                item.tmdb_stat = True                                           # Marcamos Item como procesado correctamente por TMDB (pasada 1)

            #Si el usuario ha seleccionado una opción distinta o cambiado algo, ajustamos los títulos
            if item.contentType != 'movie' or item.from_update:
                item.channel = new_item.channel                                 # Restuaramos el nombre del canal, por si lo habíamos cambiado
            if item.tmdb_stat == True:
                if new_item.contentSerieName:                                   # Si es serie...
                    filter_languages = config.get_setting("filter_languages", item.channel, default=-1)
                    if isinstance(filter_languages, int) and filter_languages >= 0:
                        item.title_from_channel = new_item.contentSerieName     # Guardo el título incial para Filtertools
                        item.contentSerieName = new_item.contentSerieName       # Guardo el título incial para Filtertools
                    else:
                        item.title = item.title.replace(new_item.contentSerieName, item.contentTitle).replace(from_title_tmdb, item.contentTitle)
                        item.contentSerieName = item.contentTitle
                    if new_item.contentSeason: item.contentSeason = new_item.contentSeason      #Restauramos Temporada
                    if item.infoLabels['title']: del item.infoLabels['title']   # Borramos título de peli (es serie)
                else:                                                           # Si es película...
                    item.title = item.title.replace(new_item.contentTitle, item.contentTitle).replace(from_title_tmdb, item.contentTitle)
                if new_item.infoLabels['year']:                                 # Actualizamos el Año en el título
                    item.title = item.title.replace(str(new_item.infoLabels['year']), str(item.infoLabels['year']))
                if new_item.infoLabels['rating']:                               # Actualizamos en Rating en el título
                    try:
                        rating_old = ''
                        if new_item.infoLabels['rating'] and new_item.infoLabels['rating'] != 0.0:
                            rating_old = float(new_item.infoLabels['rating'])
                            rating_old = round(rating_old, 1)
                        rating_new = ''
                        if item.infoLabels['rating'] and item.infoLabels['rating'] != 0.0:
                            rating_new = float(item.infoLabels['rating'])
                            rating_new = round(rating_new, 1)
                        item.title = item.title.replace("[" + str(rating_old) + "]", "[" + str(rating_new) + "]")
                    except Exception:
                        logger.error(traceback.format_exc())
                if item.wanted:                                                 # Actualizamos Wanted, si existe
                    item.wanted = item.contentTitle
                if new_item.contentSeason:                                      # Restauramos el núm. de Temporada después de TMDB
                    item.contentSeason = new_item.contentSeason
                    
                if item.from_update:                                            # Si la llamda es desde el menú del canal...
                    item.from_update = True 
                    del item.from_update
                    if item.AHkwargs:
                        try:
                            item = AH_find_videolab_status(item, [item], **item.AHkwargs)[0]
                            del item.AHkwargs
                        except Exception:
                            logger.error(traceback.format_exc())
                    xlistitem = refresh_screen(item)                            # Refrescamos la pantallas con el nuevo Item
                    
        #Para evitar el "efecto memoria" de TMDB, se le llama con un título ficticio para que resetee los buffers
        if item.contentSerieName:
            new_item.infoLabels['tmdb_id'] = '289'                              # Una serie no ambigua
        else:
            new_item.infoLabels['tmdb_id'] = '111'                              # Una peli no ambigua
        new_item.infoLabels['year'] = '-'
        if new_item.contentSeason:
            del new_item.infoLabels['season']                                   # Funciona mal con num. de Temporada
        scraper_return = scraper.find_and_set_infoLabels(new_item)
        
    #logger.debug(item)
    
    return item
    

def refresh_screen(item):
    logger.info()
    
    """
    #### Compatibilidad con Kodi 18 ####
    
    Refresca la pantalla con el nuevo Item después que haber establecido un dialogo que ha causado el cambio de Item
    Crea un xlistitem para engañar a Kodi con la función xbmcplugin.setResolvedUrl FALSE
    
    Entrada: item:          El Item actualizado
    Salida: xlistitem       El xlistitem creado, por si resulta de alguna utilidad posterior
    """

    try:
        import xbmcplugin
        import xbmcgui
        from platformcode.platformtools import itemlist_update
        
        xlistitem = xbmcgui.ListItem(path=item.url)                             # Creamos xlistitem por compatibilidad con Kodi 18
        if config.get_platform(True)['num_version'] >= 16.0:
            xlistitem.setArt({"thumb": item.contentThumbnail})                  # Cargamos el thumb
        else:
            xlistitem.setThumbnailImage(item.contentThumbnail)
        xlistitem.setInfo("video", item.infoLabels)                             # Copiamos infoLabel

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xlistitem)           # Preparamos el entorno para evitar error Kod1 18
        time.sleep(1)                                                           # Dejamos tiempo para que se ejecute
    except Exception:
        logger.error(traceback.format_exc())
    
    itemlist_update(item)                                                       # Refrescamos la pantalla con el nuevo Item
    
    return xlistitem


def format_tmdb_id(entity):
    if not entity: return

    def format_entity(item):
        try:
            if item.infoLabels:
                id_tmdb = '' if (not item.infoLabels['imdb_id'] or item.infoLabels['imdb_id'] == 'None') else item.infoLabels['imdb_id']
                if 'tmdb_id' in item.infoLabels:
                    item.infoLabels['tmdb_id'] = '' if (not item.infoLabels['tmdb_id'] \
                                                        or item.infoLabels['tmdb_id'] == 'None') \
                                                        else item.infoLabels['tmdb_id']
                if 'tvdb_id' in item.infoLabels:
                    item.infoLabels['tvdb_id'] = '' if (not item.infoLabels['tvdb_id'] \
                                                        or item.infoLabels['tvdb_id'] == 'None') \
                                                        else item.infoLabels['tvdb_id']
                if 'imdb_id' in item.infoLabels:
                    item.infoLabels['imdb_id'] = '' if (not item.infoLabels['imdb_id'] \
                                                        or item.infoLabels['imdb_id'] == 'None') \
                                                        else item.infoLabels['imdb_id']
                if 'IMDBNumber' in item.infoLabels:
                    item.infoLabels['IMDBNumber'] = '' if (not item.infoLabels['IMDBNumber'] \
                                                           or item.infoLabels['IMDBNumber'] == 'None') \
                                                           else item.infoLabels['IMDBNumber']
        except Exception:
            logger.error(traceback.format_exc())

    if not isinstance(entity, list):                                            # Es Item
        format_entity(entity)
    else:                                                                       # Es Itemlist
        for item_local in entity:
            format_entity(item_local)


def create_videolab_list(update=None):
    logger.info('update: %s' % True if update else None)
    from core import jsontools
    
    patron = "\[([^\]]+)\]"

    def build_videolab_json(videolab_list, list_movies, list_series, json_path):
        from core import videolibrarytools
        
        res = False
        hit = False

        try:
            for movie in list_movies:
                imdb_id = scrapertools.find_single_match(movie, patron)
                if imdb_id:
                    path_nfo = filetools.join(movies_videolibrary_path, movie, movie+'.nfo')
                    head_nfo, it = videolibrarytools.read_nfo(path_nfo)
                    if it and it.infoLabels.get('imdb_id') and it.infoLabels.get('tmdb_id'):
                        videolab_list['movie'][imdb_id] = it.infoLabels
                        hit = True
            
            for tvshow in list_series:
                imdb_id = scrapertools.find_single_match(tvshow, patron)
                if imdb_id:
                    path_nfo = filetools.join(series_videolibrary_path, tvshow, 'tvshow.nfo')
                    head_nfo, it = videolibrarytools.read_nfo(path_nfo)
                    if it and it.infoLabels.get('imdb_id') and it.infoLabels.get('tmdb_id'):
                        videolab_list['tvshow'][imdb_id] = it.infoLabels
                        hit = True

            res = filetools.write(json_path, jsontools.dump(videolab_list))
        except Exception:
            logger.error(traceback.format_exc())
            
        if not res:
            logger.error('ERROR en la ESCRITURA del videolab_list.json: %s' % videolab_list)
            filetools.remove(json_path)
        if not hit:
            logger.info('Videolibrary VACÍA para videolab_list.json', force=True)
        return res and hit

    try:
        video_list_movies = ''
        video_list_series = ''
        json_path = filetools.join(config.get_runtime_path(), 'resources', 'videolab_list.json')

        list_movies = filetools.listdir(movies_videolibrary_path)
        list_series = filetools.listdir(series_videolibrary_path)

        if not filetools.exists(json_path):
            videolab_list = {
                             'movie': {}, 
                             'tvshow': {}
                            }
            res = filetools.write(json_path, jsontools.dump(videolab_list))
            if not res:
                logger.error('ERROR en la CREACIÓN del videolab_list.json')
                return video_list_movies, video_list_series
            
            res = build_videolab_json(videolab_list, list_movies, list_series, json_path)
            if res: logger.info('CREACIÓN del videolab_list.json con ÉXITO', force=True)

        if filetools.exists(json_path) and not update:
            videolab_list = jsontools.load(filetools.read(json_path))
            if videolab_list:
                for movie in list_movies:
                    imdb_id = scrapertools.find_single_match(movie, patron)
                    if imdb_id:
                        video_list_movies += "'%s'|%s|%s|, " % (movie, videolab_list.get('movie', {}).get(imdb_id, {}).get('tmdb_id', ''),
                                                                videolab_list.get('movie', {}).get(imdb_id, {}).get('tvdb_id', ''))
                
                for tvshow in list_series:
                    imdb_id = scrapertools.find_single_match(tvshow, patron)
                    if imdb_id:
                        video_list_series += "'%s'|%s|%s|, " % (tvshow, videolab_list.get('tvshow', {}).get(imdb_id, {}).get('tmdb_id', ''),
                                                                videolab_list.get('tvshow', {}).get(imdb_id, {}).get('tvdb_id', ''))
            if DEBUG: logger.debug('videolab_list.json LEÍDO')

        elif filetools.exists(json_path) and update:
            res = False
            if update.get('mediatype') and update.get('imdb_id') and update.get('tmdb_id'):
                videolab_list = jsontools.load(filetools.read(json_path))
                videolab_list[update['mediatype']][update['imdb_id']] = update
                res = filetools.write(json_path, jsontools.dump(videolab_list))
                if not res:
                    logger.error('ERROR en la ACTUALIZACIÓN del videolab_list.json: %s' % update)
                    return
                config.cache_reset(label='alfa_videolab_series_list')
            if DEBUG: logger.debug('videolab_list.json UPDATE %s: %s' % (res, update))
            return

    except Exception:
        logger.error(traceback.format_exc())

    if DEBUG: logger.debug('video_list_movies (%s): %s' % (len(video_list_movies), video_list_movies))
    if DEBUG: logger.debug('video_list_series (%s): %s' % (len(video_list_series), video_list_series))

    return video_list_movies, video_list_series


def check_marks_in_videolibray(item, strm='', video_list_init=False):
    logger.info()
    
    """
    Comprueba si el item listado está visto/no visto en la videoteca Kodi.  Si lo está devuelve True
    """
    
    from platformcode import xbmc_videolibrary
    ret = False
    
    season_episode = strm
    if not season_episode and item.contentSeason and item.contentEpisodeNumber:
        season_episode = '%sx%s.strm' % (str(item.contentSeason), str(item.contentEpisodeNumber).zfill(2))
    
    episode_list = xbmc_videolibrary.get_videos_watched_on_kodi(item, list_videos=True)

    if video_list_init:
        if episode_list: ret = True
        return ret, episode_list

    if not episode_list and item.video_path:
        del item.video_path
        return False
    
    if season_episode and episode_list.get(season_episode, 0) >= 1:
        return True
    else:
        return False


def context_for_videolibray(item):
    logger.info()
    
    context = []

    if item.video_path:

        if item.contentType == 'tvshow':
            poner_marca = config.get_localized_string(60021)
            quitar_marca = config.get_localized_string(60020)
        elif item.contentType == 'season':
            poner_marca = config.get_localized_string(60029)
            quitar_marca = config.get_localized_string(60028)
        else:
            poner_marca = config.get_localized_string(60033)
            quitar_marca = config.get_localized_string(60032)

        context.extend(({"title": quitar_marca,
                        "action": "mark_video_as_watched",
                        "channel": "videolibrary",
                        "playcount": 0},
                       {"title": poner_marca,
                        "action": "mark_video_as_watched",
                        "channel": "videolibrary",
                        "playcount": 1}))
    
    if (item.video_path and item.contentType in ['tvshow']) or (item.contentType in ['episode'] and item.nfo):
        context.append(({"title": config.get_localized_string(70269),
                        "action": "update_tvshow",
                        "channel": "videolibrary"}))
    
        if not item.context: item.context = []
        if not isinstance(item.context, list):
            item.context = item.context.replace('["', '').replace('"]', '').replace("['", "").replace("']", "").split("|")
        for cont in context:
            if cont['title'] in str(item.context): continue
            item.context += [cont]

    return item


def AH_find_videolab_status(item, itemlist, **AHkwargs):
    logger.info()
    if DEBUG: logger.debug('video_list_str: %s; function: %s' % (video_list_str, AHkwargs.get('function', '')))

    res = False
    season_episode = ''

    try:
        format_tmdb_id(item)
        format_tmdb_id(itemlist)
        
        if AHkwargs.get('function', '') == 'list_all':
            #tmdb.set_infoLabels_itemlist(itemlist, True)
            for item_local in itemlist:
                item_local.video_path = AH_check_title_in_videolibray(item_local)
                if item_local.video_path:
                    item_local.title  = '(V)-%s' % item_local.title
                    item_local.contentTitle = '(V)-%s' % (item_local.contentSerieName or item_local.contentTitle)
                    item_local = context_for_videolibray(item_local)
                    item_local.unify_extended = True

                    if item_local.contentType in ['season', 'episode']:
                        season_episode = '%sx%s.strm' % (str(item_local.contentSeason), str(item_local.contentEpisodeNumber).zfill(2))
                        if check_marks_in_videolibray(item_local, strm=season_episode):
                            item_local.infoLabels["playcount"] = 1
                    elif item_local.contentType in ['movie']:
                        season_episode = '%s.strm' % item_local.contentTitle.replace('(V)-' , '').lower()
                        if check_marks_in_videolibray(item_local, strm=season_episode):
                            item_local.infoLabels["playcount"] = 1
                    elif item_local.contentType in ['tvshow']:
                        res, season_list = check_marks_in_videolibray(item_local, video_list_init=True)
                        if res:
                            for season, values in list(season_list.items()):
                                if values[0] < values[1]:
                                    break
                            else:
                                item_local.infoLabels["playcount"] = 1

        elif AHkwargs.get('function', '') in ['seasons']:
            if item.video_path:
                res, season_list = check_marks_in_videolibray(item, video_list_init=True)
                if res:
                    for item_local in itemlist:
                        if season_list.get(item_local.contentSeason):
                            if season_list.get(item_local.contentSeason, 0)[0] >= season_list.get(item_local.contentSeason, 0)[1]:
                                item_local.infoLabels["playcount"] = 1

        elif AHkwargs.get('function', '') in ['episodes']:
            if item.video_path:
                res, episode_list = check_marks_in_videolibray(item, video_list_init=True)
                if res:
                    for item_local in itemlist:
                        season_episode = '%sx%s.strm' % (str(item_local.contentSeason), str(item_local.contentEpisodeNumber).zfill(2))
                        if episode_list.get(season_episode, 0) >= 1:
                            item_local.infoLabels["playcount"] = 1

        elif AHkwargs.get('function', '') in ['get_video_options']:
            if item.video_path:
                if item.contentType in ['movie']:
                    season_episode = '%s.strm' % item.contentTitle.replace('(V)-' , '').lower()
                else:
                    season_episode = '%sx%s.strm' % (str(item.contentSeason), str(item.contentEpisodeNumber).zfill(2))
                playcount = 1 if check_marks_in_videolibray(item, strm=season_episode) else 0
                item.infoLabels["playcount"] = playcount
                for item_local in itemlist:
                    if playcount == 0:
                        item_local.infoLabels["playcount"] = playcount
                    elif item_local.action == 'play':
                        item_local.infoLabels["playcount"] = playcount
    except Exception:
        logger.error(traceback.format_exc())

    return itemlist


def AH_check_title_in_videolibray(item):
    """
    Comprueba si el item listado está en la videoteca Alfa.  Si lo está devuelve True
    """
    global video_list_str
    res = False
    
    if not item.infoLabels['imdb_id'] and not item.infoLabels['tmdb_id'] and not item.infoLabels['tvdb_id']:
        return res
    
    if not video_list_str:
        if alfa_caching and window.getProperty("alfa_videolab_movies_list") \
                        and window.getProperty("alfa_videolab_series_list"):
            video_list_str = window.getProperty("alfa_videolab_movies_list")
            video_list_str += window.getProperty("alfa_videolab_series_list")
            logger.info(True)
        else:
            video_list_movies, video_list_series = create_videolab_list()
            video_list_str = video_list_movies + video_list_series
            logger.info(False)
            
            if alfa_caching:
                window.setProperty("alfa_videolab_movies_list", video_list_movies)
                window.setProperty("alfa_videolab_series_list", video_list_series)

    if (item.infoLabels['imdb_id'] and '[%s]' % item.infoLabels['imdb_id'] in video_list_str) \
        or (item.infoLabels['tmdb_id'] and '|%s|' % item.infoLabels['tmdb_id'] in video_list_str) \
        or (item.infoLabels['tvdb_id'] and '|%s|' % item.infoLabels['tvdb_id'] in video_list_str):

        for video in video_list_str.split(','):
            if (item.infoLabels['imdb_id'] and '[%s]' % item.infoLabels['imdb_id'] in video) \
                or (item.infoLabels['tmdb_id'] and '|%s|' % item.infoLabels['tmdb_id'] in video) \
                or (item.infoLabels['tvdb_id'] and '|%s|' % item.infoLabels['tvdb_id'] in video):
                res = video.split('|')[0].strip().strip("'").strip()
                if res: break

    if DEBUG: logger.debug('video "%s %s" %s en videolab: "%s"' % (item.infoLabels['title'], 
                            item.infoLabels['imdb_id'] or item.infoLabels['tmdb_id'] or item.infoLabels['tvdb_id'], 
                            'ENCONTRADO' if res else 'NO Encontrado', video_list_str))

    return res


def AH_post_tmdb_listado(item, itemlist, **AHkwargs):
    logger.info()

    """
        
    Pasada para maquillaje de los títulos obtenidos desde TMDB en Listado y Listado_Búsqueda.
    
    Toma de infoLabel todos los datos de interés y los va situando en diferentes variables, principalmente título
    para que sea compatible con Unify, y si no se tienen Títulos Inteligentes, para que el formato sea lo más
    parecido al de Unify.
    
    También restaura varios datos salvados desde el título antes de pasarlo por TMDB, ya que mantenerlos no habría encontrado el título (title_subs)
    
    """
    #logger.debug(item)

    # Ajustamos el nombre de la categoría
    if item.category_new == "newest":                                           # Viene de Novedades.  Lo marcamos para Unify
        item.from_channel = 'news'
        del item.category_new

    format_tmdb_id(item)
    format_tmdb_id(itemlist)

    for item_local in itemlist:                                                 # Recorremos el Itemlist generado por el canal
        item_local.title = re.sub(r'(?i)online|descarga|downloads|trailer|videoteca|gb|autoplay', '', item_local.title).strip()
        title = item_local.title
        season = 0
        episode = 0
        idioma = idioma_busqueda
        if 'VO' in str(item_local.language):
            idioma = idioma_busqueda_VO
        #logger.debug(item_local)

        if item_local.contentSeason_save:                                       # Restauramos el num. de Temporada
            item_local.contentSeason = item_local.contentSeason_save

        #Restauramos la info adicional guarda en la lista title_subs, y la borramos de Item
        title_add = ''
        if item_local.title_subs:
            for title_subs in item_local.title_subs:
                if not title_subs: continue
                if scrapertools.find_single_match(title_subs, r'Episodio\s*(\d+)x(\d+)'):
                    title_subs += ' (MAX_EPISODIOS)'
                title_add = '%s -%s-' % (title_add, title_subs)                 # Se agregan el resto de etiquetas salvadas
        if len(title_add) > 1: item_local.unify_extended = True
        if 'title_subs' in item_local: del item_local.title_subs  

        # Para Episodios, tomo el año de exposición y no el de inicio de la serie
        if item_local.infoLabels['aired']:
            item_local.infoLabels['year'] = scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})')

        if item_local.from_title:
            if item_local.contentType == 'movie':
                item_local.contentTitle = item_local.from_title
                item_local.title = item_local.from_title
            elif item_local.contentType == 'season':
                item_local.title = item_local.from_title
            else:
                item_local.contentSerieName = item_local.from_title
            
            item_local.title = re.sub(r'(?i)online|descarga|downloads|trailer|videoteca|gb|autoplay', '', item_local.title).strip()
            title = item_local.title

        #Limpiamos calidad de títulos originales que se hayan podido colar
        if item_local.infoLabels['originaltitle'].lower() in item_local.quality.lower():
            item_local.quality = re.sub(item_local.infoLabels['originaltitle'], '', item_local.quality)

        # Preparamos el título para series, con los núm. de temporadas, si las hay
        if item_local.contentType in ['season', 'tvshow', 'episode']:
            item_local.contentSerieName = filetools.validate_path(item_local.contentSerieName.replace('/', '-').replace('  ', ' '))
            item_local.contentTitle = filetools.validate_path(item_local.contentTitle.replace('/', '-').replace('  ', ' '))
            item_local.title = filetools.validate_path(item_local.title.replace('/', '-').replace('  ', ' '))
            if item_local.from_title: item_local.from_title = filetools.validate_path(item_local.from_title.replace('/', '-').replace('  ', ' '))

            # Pasada por TMDB a Serie, para datos adicionales, y mejorar la experiencia en Novedades
            if scrapertools.find_single_match(title_add, r'Episodio\s*(\d+)x(\d+)') or ' (MAX_EPISODIOS)' in title_add:
                # Salva los datos de la Serie y lo transforma temporalmente en Season o Episode
                contentPlot = item_local.contentPlot
                contentType = item_local.contentType
                if scrapertools.find_single_match(title_add, r'Episodio\s*(\d+)x(\d+)'):
                    season, episode = scrapertools.find_single_match(title_add, r'Episodio\s*(\d+)x(\d+)')
                else:
                    season = item_local.infoLabels['season']
                    episode = item_local.infoLabels['episode']
                episode_max = int(episode)
                try:
                    item_local.infoLabels['season'] = int(season)
                    item_local.infoLabels['episode'] = int(episode)
                except Exception:
                    season = 0
                    episode = 0

                if not season:
                    title_add = re.sub(r'Episodio\s*(\d+)x(\d+)', '', title_add)
                elif '-al-' not in title_add and episode:
                    item_local.infoLabels['episode'] = episode
                    item_local.contentType = "episode"
                else:
                    item_local.contentType = "season"
                    episode_max = int(scrapertools.find_single_match(title_add, r'Episodio\s*\d+x\d+-al-(\d+)'))

                if (not item_local.infoLabels['temporada_nombre'] or not item_local.infoLabels['number_of_seasons']) \
                                                                  and item_local.infoLabels['tmdb_id'] \
                                                                  and item_local.infoLabels['season']:
                    tmdb.set_infoLabels_item(item_local, seekTmdb=True, idioma_busqueda=idioma)     # TMDB de la serie
                    format_tmdb_id(item_local)
 
                # Restaura los datos de infoLabels a su estado original, menos plot y año
                item_local.infoLabels['year'] = scrapertools.find_single_match(item_local.infoLabels['aired'], r'\d{4}')

                if item_local.infoLabels.get('temporada_num_episodios', 0) >= episode_max:
                    tot_epis = ''
                    if item_local.infoLabels.get('temporada_num_episodios', 0):
                        tot_epis = ' (de %s' % str(item_local.infoLabels['temporada_num_episodios'])
                    if (item_local.infoLabels.get('number_of_seasons', 0) > 1 \
                            and item_local.infoLabels.get('number_of_episodes', 0) > 0) \
                            or (item_local.infoLabels.get('number_of_seasons', 0) \
                            and not item_local.infoLabels.get('temporada_num_episodios', 0)):
                        tot_epis += ' (' if not tot_epis else ', '
                        tot_epis += 'de %sx%s' % (str(item_local.infoLabels['number_of_seasons']), \
                                                  str(item_local.infoLabels['number_of_episodes']))
                    if tot_epis: tot_epis += ')'
                    title_add = title_add.replace(' (MAX_EPISODIOS)', tot_epis)
                else:
                    title_add = title_add.replace(' (MAX_EPISODIOS)', '')

                if contentPlot[10:] != item_local.contentPlot[10:]:
                    item_local.contentPlot += '\n\n%s' % contentPlot

                item_local.contentType = contentType
                if item_local.contentType in ['tvshow'] and item_local.infoLabels['season']: del item_local.infoLabels['season']
                if item_local.contentType in ['season', 'tvshow'] and item_local.contentEpisodeNumber: del item_local.infoLabels['episode']

            # Exploramos los diferentes formatos
            if item_local.contentType == "episode":
                # Si no está el título del episodio, pero sí está en "title", lo rescatamos
                if not item_local.infoLabels['episodio_titulo'] and item_local.infoLabels['title'].lower() \
                                                                != item_local.infoLabels['tvshowtitle'].lower():
                    item_local.infoLabels['episodio_titulo'] = item_local.infoLabels['title']

                if "Temporada" in title:                                        # Compatibilizamos "Temporada" con Unify
                    title = '%sx%s al 99 -' % (str(item_local.contentSeason), str(item_local.contentEpisodeNumber))
                if " al " in title:                                             # Si son episodios múltiples, ponemos nombre de serie
                    if " al 99" in title.lower():                               # Temporada completa.  Buscamos num total de episodios
                        title = title.replace("99", str(item_local.infoLabels['temporada_num_episodios']))
                    title = '%s %s' % (title, item_local.contentSerieName)
                    item_local.infoLabels['episodio_titulo'] = '%s - %s %s %s' % (scrapertools.find_single_match(title, r'(al \d+)'), 
                                                               item_local.contentSerieName, unify.set_color(item_local.infoLabels['year'], 'year'), 
                                                               unify.format_rating(item_local.infoLabels['rating']))

                elif item_local.infoLabels['episodio_titulo']:
                    title = '%s %s, %s' % (title, item_local.infoLabels['episodio_titulo'], item_local.contentSerieName)
                    item_local.infoLabels['episodio_titulo'] = '%s, %s %s %s' % (item_local.infoLabels['episodio_titulo'], 
                                                               item_local.contentSerieName,  unify.set_color(item_local.infoLabels['year'], 'year'), 
                                                               unify.format_rating(item_local.infoLabels['rating']))

                else:                                                           # Si no hay título de episodio, ponermos el nombre de la serie
                    if item_local.contentSerieName not in title:
                        title = '%s %s' % (title, item_local.contentSerieName)
                    item_local.infoLabels['episodio_titulo'] = '%s %s %s' % (item_local.contentSerieName, 
                                                                                 unify.set_color(item_local.infoLabels['year'], 'year'), 
                                                                                 unify.format_rating(item_local.infoLabels['rating']))

                if not item_local.contentSeason or not item_local.contentEpisodeNumber:
                    if "Episodio" in title_add:
                        item_local.contentSeason, item_local.contentEpisodeNumber = scrapertools.find_single_match(title_add, 
                                                                                    'Episodio (\d+)x(\d+)')
                        title = '%s %s %s' % (title, unify.set_color(item_local.infoLabels['year'], 'year'), 
                                                         unify.format_rating(item_local.infoLabels['rating']))

            elif item_local.contentType == "season":
                if not item_local.contentSeason:
                    item_local.contentSeason = scrapertools.find_single_match(item_local.url, '-(\d+)x')
                if not item_local.contentSeason:
                    item_local.contentSeason = scrapertools.find_single_match(item_local.url, '-temporadas?-(\d+)')
                if item_local.contentSeason:
                    title = '%s -Temporada %s' % (title, str(item_local.contentSeason))
                    if not item_local.contentSeason_save:                           # Restauramos el num. de Temporada
                        item_local.contentSeason_save = item_local.contentSeason    # Y lo volvemos a salvar
                    del item_local.infoLabels['season']                             # Funciona mal con num. de Temporada.  Luego lo restauramos
                else:
                    title = '%s -Temporada !!!' % (title)

        # Se añaden etiquetas adicionales, si las hay
        title += title_add.replace(' (MAX_EPISODIOS)', '').replace('BTDIGG_INFO', '(de %sx%s)' \
                                                           % (str(item_local.infoLabels['number_of_seasons']), \
                                                              str(item_local.infoLabels['number_of_episodes'])))
        if title_add and item_local.contentType == 'movie':
            item_local.contentTitle += title_add.replace(' (MAX_EPISODIOS)', '')

        # Viene de Novedades.  Lo preparamos para Unify
        if item_local.from_channel == "news":

            if item_local.contentType in ['season', 'tvshow']:
                title = '%s %s' % (item_local.contentSerieName, title_add)
            elif "Episodio " in title:
                if not item_local.contentSeason or not item_local.contentEpisodeNumber:
                    try:
                        item_local.contentSeason, item_local.contentEpisodeNumber = \
                                scrapertools.find_single_match(title_add, 'Episodio (\d+)x(\d+)')
                    except Exception:
                        item_local.contentSeason = item_local.contentEpisodeNumber = 1
            item_local.unify_extended = True

        # Ponemos el estado de las Series
        if item_local.infoLabels['status'] and (item_local.infoLabels['status'].lower() == "ended" \
                        or item_local.infoLabels['status'].lower() == "canceled"):
            title += ' [TERM]'
            item_local.unify_extended = True

        item_local.title = title

        #logger.debug(item_local)

    if 'from_channel' in item.from_channel:
        del item.from_channel

    return item, itemlist


def AH_find_seasons(self, item, matches, **AHkwargs):
    logger.info()

    # Si hay varias temporadas, buscamos todas las ocurrencias y las filtrados por TMDB, calidad e idioma
    findS = AHkwargs.get('finds', {})
    title_search = findS.get('controls', {}).get('title_search', '')
    modo_ultima_temp = AHkwargs.get('modo_ultima_temp', config.get_setting('seleccionar_ult_temporadda_activa', item.channel, default=True))
    language_def = AHkwargs.get('language', [])
    function = AHkwargs.get('function', 'find_seasons')
    kwargs = {'function': function, 'kwargs': AHkwargs.get('kwargs', {})}
    if not item.language: item.language = language_def
    if not item.library_playcounts: modo_ultima_temp = False
    item.quality = item.quality.replace(config.BTDIGG_LABEL, '')
    patron_seasons = findS.get('seasons_search_num_rgx', [['(?i)-(\d+)-(?:Temporada|Miniserie)', None], 
                                                         ['(?i)(?:Temporada|Miniserie)-(\d+)', None]])
    patron_qualities = findS.get('seasons_search_qty_rgx', [['(?i)(?:Temporada|Miniserie)(?:-(.*?)(?:\.|\/|-$|$))', None]])
    list_temps = []
    list_temp_int = []
    list_temp = []
    seasons = []
    itemlist = []
    title_list = []
    seasons_found = 0
    for match in matches:
        list_temps.append(match['url'])
    if not list_temps:
        list_temps.append(item.url)

    format_tmdb_id(item)

    try:
        # Vemos la última temporada de TMDB y del .nfo
        if item.ow_force == "1":                                                    # Si hay una migración de canal o url, se actualiza todo 
            modo_ultima_temp = False
        max_temp = int(item.infoLabels['number_of_seasons'] or 0)
        max_nfo = 0
        y = []
        if modo_ultima_temp and item.library_playcounts:                            # Averiguar cuantas temporadas hay en Videoteca
            patron = 'season (\d+)'
            matches_x = re.compile(patron, re.DOTALL).findall(str(item.library_playcounts))
            for x in matches_x:
                y += [int(x)]
            max_nfo = max(y)
        if max_nfo > 0 and max_nfo != max_temp:
            max_temp = max_nfo
        if max_temp == 0 or max_nfo:
            modo_ultima_temp = min_temp = False

        if item.infoLabels['number_of_seasons'] and item.infoLabels['number_of_seasons'] == 1 and not item.btdig_in_use:
            itemlist.append(item)
        else:
            # Creamos un nuevo Item para la búsqueda de las temporadas
            item_search = item.clone()
            item_search.extra = function
            item_search.c_type = item_search.c_type or 'series'

            title = title_search or scrapertools.find_single_match(item_search.season_search or item_search.contentSerieName \
                                                 or item_search.contentTitle, '(^.*?)\s*(?:$|\(|\[)').lower()                       # Limpiamos
            title = scrapertools.quote(title, plus=True)
            title_list += [title]
            title_org = scrapertools.find_single_match(item_search.infoLabels['originaltitle'], '(^.*?)\s*(?:$|\(|\[)').lower()     # Limpiamos
            title_org = scrapertools.quote(title_org, plus=True)
            if title_org != title: title_list += [title_org]

            channel = __import__('channels.%s' % item_search.channel, None, None, ["channels.%s" % item_search.channel])
            item_search.url = channel.host

            if DEBUG: logger.debug('list_temps INICAL: %s; title_list: %s' % (list_temps, title_list))
            for title_search in title_list:
                item_search.title = title_search
                item_search.infoLabels = {}

                # Llamamos a 'Listado' para que procese la búsqueda
                itemlist = getattr(channel, "search")(item_search, title_search.lower(), **kwargs)

                if not itemlist:
                    continue

                format_tmdb_id(itemlist)

                # Analizamos si las temporadas encontradas corresponden a las serie
                for item_found in itemlist:                                     # Procesamos el Itemlist de respuesta
                    item_found.quality = item_found.quality.replace(config.BTDIGG_LABEL, '')
                    if DEBUG: logger.debug('===============================================')
                    if DEBUG: logger.debug('tmdb_id: item_found: %s / item: %s' % (item_found.infoLabels['tmdb_id'], item.infoLabels['tmdb_id']))
                    if DEBUG: logger.debug('language: item_found: %s / item: %s' % (item_found.language, item.language))
                    if DEBUG: logger.debug('quality: item_found: %s / item: %s' % (item_found.quality, item.quality))
                    if DEBUG: logger.debug('url: item_found: %s / item: %s' % (item_found.url, item.url))
                    if DEBUG: logger.debug('title: item_found: %s / item: %s' % (item_found.title, item.title))

                    if item_found.url in str(list_temps):                       # Si ya está la url, pasamos a la siguiente
                        continue
                    if not item_found.infoLabels['tmdb_id']:                    # tiene TMDB?
                        continue
                    if item_found.infoLabels['tmdb_id'] != item.infoLabels['tmdb_id']:  # Es el mismo TMDB?
                        continue
                    if item.language and item_found.language:                   # Es el mismo Idioma?
                        if item.language != item_found.language:
                            continue
                    if item.quality and item_found.quality:                     # Es la misma Calidad?, si la hay...
                        if item.quality != item_found.quality and item.quality.replace(' AC3 5.1', '')\
                                           .replace(' ', '-').replace(btdigg_label, '') != item_found.quality:
                            continue
                    elif patron_qualities:
                        for patron_quality in patron_qualities:
                            if scrapertools.find_single_match(item.url, patron_quality) == \
                                    scrapertools.find_single_match(item_found.url, patron_quality):     # Coincide la calidad? (alternativo)
                                break
                        else:
                            continue
                    list_temps.append(item_found.url)                           # Si hay ocurrencia, guardamos la url
                    seasons_found += 1
                    if DEBUG: logger.debug('item_found: ### TRUE ###')

                if seasons_found > 0: 
                    break
        
        if DEBUG: logger.debug('list_temps: %s' % list_temps)
        # Organizamos las temporadas válidas encontradas

        for x, url in enumerate(list_temps):
            elem_json = {}
            for y, (patron_season, none) in enumerate(patron_seasons):
                if scrapertools.find_single_match(url, patron_season):          # Está la Temporada en la url en este formato?
                    season = scrapertools.find_single_match(url, patron_season)
                    try:                                                        # Miramos si la Temporada está procesada
                        if not modo_ultima_temp or (modo_ultima_temp and max_temp >= max_nfo \
                                                    and int(season) >= max_nfo):
                            elem_json['url'] = url                              # No está procesada, la añadimos
                            elem_json['season'] = int(season)
                            elem_json['priority'] = y
                        else:
                            break
                    except Exception:
                        logger.error('ERROR Temporada sin num: %s' % url)
                        elem_json['url'] = url                                  # ERROR, la añadimos
                        elem_json['season'] = x + 1
                        elem_json['priority'] = y
                        logger.error(traceback.format_exc())

                    list_temp_int.append(elem_json.copy())
                    break
            else:
                logger.error('Temporada sin patrón: %s' % url)
                elem_json['url'] = url                                          # No está procesada, la añadimos
                elem_json['season'] = x + 1
                elem_json['priority'] = 98
                if elem_json['season'] == 1:
                    list_temp_int.append(elem_json.copy())
        
        list_temp_int = sorted(list_temp_int, key=lambda el: (int(el['priority']), int(el['season'])))
        for x, elem_json in enumerate(list_temp_int):
            if elem_json['season'] in seasons:
                continue
            seasons += [elem_json['season']]
            list_temp.append(list_temp_int[x])
        list_temp = sorted(list_temp, key=lambda el: int(el['season']))
        
        url_changed = False
        if list_temp:
            if item.url != list_temp[-1]['url'] or (item.library_urls and item.library_urls.get(item.channel) \
                                                and item.library_urls[item.channel] != list_temp[-1]['url']):
                url_changed = True
            item.url = list_temp[-1]['url']                                     # Guardamos la url de la última Temporada en .NFO
            if item.library_urls and item.library_urls.get(item.channel):
                item.library_urls[item.channel] = item.url                      # Guardamos la url en el .nfo
        
        # Si la ha cambiado la última temporada, actualizamos el .nfo para la Videoteca
        if url_changed and (item.nfo or item.path or item.video_path):
            from core import videolibrarytools
            path = item.nfo
            if not path:
                path = filetools.join(series_videolibrary_path, item.path or item.video_path, 'tvshow.nfo')
            head_nfo, it = videolibrarytools.read_nfo(path)
            if it:
                it.library_urls[item.channel] = item.url
                res = videolibrarytools.write_nfo(path, head_nfo=head_nfo, item=it)     # Refresca el .nfo para recoger actualizaciones

    except Exception:
        logger.error('ERROR al procesar las temporadas: %s' % list_temps)
        elem_json = {}
        elem_json['url'] = item.url                                             # No está procesada, la añadimos
        elem_json['season'] = 1
        elem_json['priority'] = 99
        list_temp.append(elem_json)
        logger.error(traceback.format_exc())

    if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(list_temp), len(str(list_temp)), str(list_temp)))

    return list_temp


def AH_post_tmdb_seasons(item, itemlist, **AHkwargs):
    logger.info()
    
    """

    Pasada para gestión del menú de Temporadas de una Serie
    
    La clave de activación de este método es la variable item.season_colapse que pone el canal en el Item de Listado.
    Esta variable tendrá que desaparecer cuando se añada a la Videoteca para que se analicen los episodios de la forma tradicional

    """
    #logger.debug(item)
    #logger.debug(config.get_setting("no_pile_on_seasons", 'videolibrary'))
    
    # Si no se quiere mostrar por temporadas, nos vamos...
    if item.season_colapse == False or config.get_setting("no_pile_on_seasons", 'videolibrary') == 2 or len(itemlist) <= 1:
        item.season_colapse = False                                             # Quitamos el indicador de listado por Temporadas
        return item, itemlist
    
    # Si no se quiere mostrar el título de TODAS las temporadas, nos vamos...
    if not config.get_setting("show_all_seasons", 'videolibrary'):
        return item, itemlist
    
    format_tmdb_id(item)
    format_tmdb_id(itemlist)
    
    matches = AHkwargs.get('matches', [])
    
    # Se muestra una entrada para listar todas los episodios
    if itemlist and config.get_setting("show_all_seasons", 'videolibrary'):
        item_season = item.clone()
                                 
        item_season.season_colapse = False                                      # Quitamos el indicador de listado por Temporadas
        if matches:
            item_season.matches = matches
        item_season.title = '** Todas las Temporadas'                           # Agregamos título de TODAS las Temporadas (modo tradicional)
        if item_season.infoLabels['number_of_episodes']:                        # Ponemos el núm de episodios de la Serie
            item_season.title += ' (%sx%s epis)' % (str(item_season.infoLabels['number_of_seasons']), \
                                                    str(item_season.infoLabels['number_of_episodes']))
    
        itemlist.insert(0, item_season.clone(from_title_season_colapse=item.title, unify_extended=True))

    return item, itemlist
    

def AH_post_tmdb_episodios(item, itemlist, **AHkwargs):
    logger.info()

    itemlist_fo = []
        
    """
        
    Pasada para maquillaje de los títulos obtenidos desde TMDB en Episodios.
    
    Toma de infoLabel todos los datos de interés y los va situando en diferentes variables, principalmente título
    para que sea compatible con Unify, y si no se tienen Títulos Inteligentes, para que el formato sea lo más
    parecido al de Unify.

    Lleva un control del num. de episodios por temporada, tratando de arreglar los errores de la Web y de TMDB
    
    """
    #logger.debug(item)
    
    format_tmdb_id(item)
    format_tmdb_id(itemlist)
    
    matches = AHkwargs.get('matches', [])

    # Recorremos el Itemlist generado por el canal    
    for item_local in itemlist:
        #logger.debug(item_local.title)

        # Preparamos el título para que sea compatible con Añadir Serie a Videoteca
        if "Temporada" in item_local.title:                                     # Compatibilizamos "Temporada" con Unify
            item_local.title = '%sx%s al 99 -' % (str(item_local.contentSeason), str(item_local.contentEpisodeNumber))

        if " al " in item_local.title:                                          # Si son episodios múltiples, ponemos nombre de serie
            if " al 99" in item_local.title.lower():                            # Temporada completa.  Buscamos num de episodios de la temporada
                item_local.title = item_local.title.replace("99", 
                                   str(item_local.infoLabels['temporada_num_episodios']) or str(item_local.infoLabels['number_of_episodes']))
            item_local.title = '%s %s' % (item_local.title, item_local.contentSerieName)
            item_local.infoLabels['episodio_titulo'] = '%s - %s' \
                                  % (scrapertools.find_single_match(item_local.title, r'(al \d+)'), 
                                  item_local.contentSerieName)

    return item, itemlist


def AH_post_tmdb_findvideos(item, itemlist, **AHkwargs):
    logger.info()
    
    """
        
    Llamada para crear un pseudo título con todos los datos relevantes del vídeo.
    
    Toma de infoLabel todos los datos de interés y los va situando en diferentes variables, principalmente título. Lleva un control del num. de episodios por temporada
        
    En Itemlist devuelve un Item con el pseudotítulo.  Ahí el canal irá agregando el resto.
    
    """
    #logger.debug(item)
    
    headers = AHkwargs.get('headers', {})
 
    # Saber si estamos en una ventana emergente lanzada desde una viñeta del menú principal,
    # con la función "play_from_library"
    item.unify = False
    Window_IsMedia = False
    try:
        import xbmc
        if xbmc.getCondVisibility('Window.IsMedia') == 1:
            Window_IsMedia = True
            item.unify = config.get_setting("unify")
    except Exception:
        item.unify = config.get_setting("unify")
        logger.error(traceback.format_exc())
    
    if item.contentSeason_save:                                                 # Restauramos el num. de Temporada
        item.contentSeason = item.contentSeason_save
        del item.contentSeason_save
    
    if item.library_filter_show:
        del item.library_filter_show
    
    if item.unify_extended:
        del item.unify_extended

    if item.contentType != 'movie' and item.nfo: 
        item = context_for_videolibray(item)
        if item.nfo and not item.video_path:
            item.video_path = filetools.basename(filetools.dirname(item.nfo))

    # Si no existe "clean_plot" se crea a partir de "plot"
    if not item.clean_plot and item.infoLabels['plot']:
        item.clean_plot = item.infoLabels['plot']

    # Guardamos la url del episodio/película para favorecer la recuperación en caso de errores
    item.url_save_rec = ([item.url, headers])
    
    if (not config.get_setting("pseudo_titulos", item.channel, default=False) and item.channel != 'url') or item.downloadFilename:
        return (item, itemlist)
    
    if item.armagedon:                                                          # Es una situación catastrófica?
        itemlist.append(item.clone(action='', title=item.category + ': [COLOR hotpink]Usando enlaces de emergencia[/COLOR]', 
                                   quality='', server='', folder=False))
    
    # Quitamos el la categoría o nombre del título, si lo tiene
    if item.contentTitle:
        item.contentTitle = re.sub(r' -%s-' % item.category, '', item.contentTitle)
        item.title = re.sub(r' -%s-' % item.category, '', item.title)
    
    # Limpiamos de año y rating de episodios
    if item.infoLabels['episodio_titulo']:
        item.infoLabels['episodio_titulo'] = re.sub(r'\s?\[.*?\]', '', item.infoLabels['episodio_titulo'])
        item.infoLabels['episodio_titulo'] = re.sub(r'\s?\(.*?\)', '', item.infoLabels['episodio_titulo'])
        item.infoLabels['episodio_titulo'] = item.infoLabels['episodio_titulo'].replace(item.contentSerieName, '')
    if item.infoLabels['aired'] and item.contentType == "episode":
        item.infoLabels['year'] = scrapertools.find_single_match(str(item.infoLabels['aired']), r'\/(\d{4})')

    if item.action == 'show_result':                                            # Viene de una búsqueda global
        channel = item.channel.capitalize()
        if item.from_channel:
            channel = item.from_channel.capitalize()
        item.quality = '[COLOR yellow][%s][/COLOR] %s' % (channel, item.quality)

    # Si tiene contraseña, la pintamos
    if 'RAR-' in item.torrent_info and not item.password:
        item = find_rar_password(item)
    if item.password:
        itemlist.append(item.clone(action="", title="[COLOR magenta][B] Contraseña: [/B][/COLOR]'" 
                                                     + item.password + "'", quality='', server='', folder=False))
    
    #Si es ventana damos la opción de descarga, ya que no hay menú contextual
    if not Window_IsMedia:
        if item.contentType == 'movie': contentType = 'Película'
        if item.contentType == 'episode': contentType = 'Episodio'
        itemlist.append(item.clone(title="-Descargar %s-" % contentType, channel="downloads", server='torrent', 
                                   folder=False, quality='', action="save_download", from_channel=item.channel, from_action='play'))
        if item.contentType == 'episode' and not item.channel_recovery:
            itemlist.append(item.clone(title="-Descargar Epis NO Vistos-", channel="downloads", contentType="tvshow", 
                                       action="save_download", from_channel=item.channel, from_action='episodios', 
                                       folder=False, quality='', sub_action="unseen"))
            item.quality = scrapertools.find_single_match(item.quality, '(.*?)\s\[')
            itemlist.append(item.clone(title="-Descargar Temporada-", channel="downloads", contentType="season", 
                                       action="save_download", from_channel=item.channel, from_action='episodios', 
                                       folder=False, quality='', sub_action="season"))
            itemlist.append(item.clone(title="-Descargar Serie-", channel="downloads", contentType="tvshow", 
                                       action="save_download", from_channel=item.channel, from_action='episodios', 
                                       folder=False, quality='', sub_action="tvshow"))

    #logger.debug(item)
    
    return (item, itemlist)


def post_btdigg(itemlist, channel, channel_obj=None, **AHkwargs):

    try:
        if not channel_obj:
            channel_obj = __import__('channels.%s' % channel, None, None, ["channels.%s" % channel])

        if not config.get_setting('find_alt_link_option', channel, default=False):
            return itemlist
        if not channel_obj.finds.get('controls', {}).get('btdigg', False):
            return itemlist

        for it in itemlist:
            if it.action and it.action not in ['configuracion', 'autoplay_config']:
                it.contentPlot = config.BTDIGG_POST + it.contentPlot
    except Exception:
        logger.error(traceback.format_exc())
    
    return itemlist


def AH_find_btdigg_matches(item, matches, **AHkwargs):
    logger.info()

    itemlist = []
    matches_out = []
    matches_index = {}
    matches_post = AHkwargs.get('matches_post_get_video_options', None)

    try:
        for match in matches:
            if item.contentType == 'movie':
                match_key = '%s [%s]' % (item.contentTitle, item.contentChannel or item.channel)
            else:
                match_key = '%sx%s [%s].json' % (match.get('season', 0), str(match.get('episode', 0)).zfill(2), item.channel)
            matches_index[match_key] = match.copy()
            if item.action == 'findvideos':
                match_key = match.get('url', '').replace(' ', '%20')
            matches_index[match_key] = match.copy()

        if not item.matches or item.nfo:
            if not item.video_path and not item.nfo: 
                return matches
            
            if item.nfo:
                path = filetools.dirname(item.nfo)
            else:
                path = filetools.join(movies_videolibrary_path if item.contentType == 'movie' else series_videolibrary_path, item.video_path)
            for epi in filetools.listdir(path):
                if not epi.endswith('.json'): continue
                if epi not in matches_index: continue

                json_path = filetools.join(path, epi)
                itemlist.append(Item().fromjson(filetools.read(json_path)))
        elif AHkwargs.get('matches'):
            itemlist.append(item.clone(matches=AHkwargs['matches']))
        else:
            itemlist.append(item)
        if DEBUG: logger.debug('Matches_index (%s/%s): %s - Matches_post: %s' \
                                % (len(matches), len(itemlist), matches_index.keys(), matches_post))

        for x, it in enumerate(itemlist):
            if not it.matches: continue
            if not isinstance(it.matches[0], dict):
                if not matches_post: continue
                AHkwargs['videolibrary'] = True
                matches_it, langs = matches_post(it, it.matches, [], {}, **AHkwargs)
                AHkwargs['videolibrary'] = False
            else:
                matches_it = it.matches.copy()

            if it.contentType == 'movie':
                match_key = '%s [%s]' % (it.contentTitle, it.channel)
            else:
                match_key = '%sx%s [%s].json' % (it.contentSeason, str(it.contentEpisodeNumber).zfill(2), it.channel)
            if not matches_index.get(match_key): continue

            for match_it in matches_it:
                if item.action == 'findvideos':
                    match_key = match_it.get('url', '').replace(' ', '%20')
                    match_it['url'] = match_it['url'].replace(' ', '%20')
                    if match_key.startswith('//'): 
                        match_key = 'https:%s' % match_key
                        match_it['url'] = 'https:%s' % match_it['url']
                if match_it.get('url', '') and match_it['url'] not in matches_index.get(match_key, {}).get('url', ''):
                    if match_it.get('quality', '').replace('*', '') and matches_index.get(match_key, {}).get('quality', '') \
                                                   and matches_index[match_key]['quality'] in match_it['quality'].replace('*', ''): continue
                    if 'Digg' in match_it.get('torrent_info', '') and not btdigg_label in match_it.get('quality', '').replace('*', ''):
                        match_it['quality'] += btdigg_label
                    matches_out.append(match_it)
    except Exception:
        logger.error(traceback.format_exc())

    if DEBUG: logger.debug('Matches AÑADIDAS: %s / %s' % (len(matches_out), matches_out))
    return matches + matches_out


def AH_find_btdigg_list_all_from_channel_py(self, item, matches=[], matches_index={}, channel_alt=channel_py, 
                                            channel_entries=20, btdigg_entries=80, **AHkwargs):
    logger.info('"%s"' % len(matches))

    matches_inter = []
    matches_btdigg = matches[:]
    controls = self.finds.get('controls', {})
    quality_control = AHkwargs.get('btdigg_quality_control', controls.get('btdigg_quality_control', False))

    try:
        channel = __import__('channels.%s' % channel_alt, None,
                             None, ["channels.%s" % channel_alt])
        host_alt = channel.host
        finds_alt = channel.finds
        finds_alt_controls = channel.finds.get('controls', {})
        btdigg_cfg = channel.finds.get('btdigg_cfg', {})
        headers = {'Referer': channel.host}
        if not finds_alt or not btdigg_cfg or not finds_alt_controls.get('btdigg_service', True):
            if DEBUG: logger.debug('matches_PY: %s / %s' % (len(matches_btdigg), matches_btdigg))
            return matches_btdigg, matches_index

        try:
            if canonical.get('global_search_active', False):
                channel.canonical['global_search_active'] = True
            canonical_alt = channel.canonical
        except Exception:
            canonical_alt = {}
            
        y = btdigg_entries
        token = ''
        for elem_cfg in btdigg_cfg:
            if item.c_type not in elem_cfg['c_type']: continue
            finds_find_alt = elem_cfg.get('find', {}) or finds_alt.get('find', {})
            if not finds_find_alt:
                if DEBUG: logger.debug('matches_PY: %s / %s' % (len(matches_btdigg), matches_btdigg))
                return matches_btdigg, matches_index

            if elem_cfg['c_type'] == 'search_token':
                soup = self.create_soup(elem_cfg['url'], post=elem_cfg.get('post', None), timeout=channel.timeout, 
                                        headers=headers, canonical=canonical_alt, alfa_s=True)
                token = self.parse_finds_dict(soup, finds_find_alt, c_type='search')
                continue
            
            if elem_cfg['c_type'] == 'search':
                if elem_cfg.get('post', None): 
                    elem_cfg['post'] = elem_cfg['post'] % (token, item.texto)
                else:
                    elem_cfg['url'] = elem_cfg['url'] % item.texto

            soup = self.create_soup(elem_cfg['url'] + str(item.page), post=elem_cfg.get('post', None), timeout=channel.timeout*2, 
                                    headers=headers, canonical=canonical_alt, alfa_s=True)

            if not self.response.sucess:
                if DEBUG: logger.debug('ERROR matches_PY: %s / %s / %s' % (self.response.code, len(matches_btdigg), matches_btdigg))
                return matches_btdigg, matches_index
            if self.response.host:
                elem_cfg['url'] = elem_cfg['url'].replace(host_alt, self.response.host)
                host_alt = self.response.host

            item.btdig_in_use= True
            matches_inter = self.parse_finds_dict(soup, finds_find_alt, c_type=elem_cfg['c_type'])
            if isinstance(matches_inter, dict):
                matches_inter = matches_inter['data']['torrents']['0']
            if not matches_inter or isinstance(matches_inter, str):
                if DEBUG: logger.debug('matches_PY: %s / %s' % (len(matches_btdigg), matches_btdigg))
                return matches_btdigg, matches_index

            x = 0
            for elem in matches_inter if isinstance(matches_inter, list) else list(matches_inter.items()):
                elem_json = {}
                #logger.error(elem)

                if isinstance(matches_inter, list):
                    if not elem.find('div', class_='card-body'): continue
                    elem_json['url'] = elem.a.get("href", "")
                    elem_json['title'] = elem.find('div', class_='card-body').find('h3', class_='title').get_text(strip=True)
                    elem_json['year'] = scrapertools.find_single_match(elem_json['title'], '\((\d{4})\)') or '-'
                    elem_json['thumbnail'] = elem.find('img').get("src", "")
                    if elem_json['thumbnail'].startswith('//'): elem_json['thumbnail'] = 'https:%s' % elem_json['thumbnail']
                    elem_json['quality'] = elem.find('div', class_='quality').get_text(strip=True)
                    elem_json['quality'] = elem_json['quality'].replace('creeener', 'creener')\
                                                               .replace('AC3 5.1', '').replace('HDTV 720p', 'HDTV-720p').strip()
                    elem_json['torrent_info'] = ''
                    elem_json['size'] = ''
                    elem_json['language'] = ['CAST']
                    
                    elem_json['mediatype'] = 'movie' if (elem_cfg.get('movie_path') and elem_cfg['movie_path'] in elem_json['url']) else 'tvshow'
                    if elem_cfg['c_type'] == 'peliculas' and elem_json['mediatype'] != 'movie': continue
                    if elem_cfg['c_type'] == 'episodios' and elem_json['mediatype'] != 'episode': continue

                    if elem_json['mediatype'] == 'episode':
                        try:
                            elem_json['season'] = int(scrapertools.find_single_match(elem.find('div', class_='card-body')\
                                                                  .find('span', class_='fdi-item').get_text(strip=True), '(\d+)'))
                            if len(str(elem_json['season'])) > 2:
                                elem_json['season'] = int(scrapertools.find_single_match(elem_json['url'], '/temporada-(\d+)'))

                            elem_json['episode'] = int(scrapertools.find_single_match(elem.find('div', class_='card-body')\
                                                                   .find('span', class_='fdi-type').get_text(strip=True), '(\d+)'))
                            if len(str(elem_json['episode'])) > 3:
                                elem_json['episode'] = int(scrapertools.find_single_match(elem_json['url'], '/capitulo-(\d+)'))
                        except:
                            logger.error(elem)
                            elem_json['season'] =  1
                            elem_json['episode'] =  1

                else:
                    elem = elem[1]
                    elem_json['url'] = self.urljoin(host_alt, elem.get('guid', ''))
                    elem_json['title'] = scrapertools.find_single_match(elem.get('torrentName', ''), '(.*?)\[').strip()
                    elem_json['year'] = scrapertools.find_single_match(elem_json['title'], '\((\d{4})\)') or '-'
                    elem_json['thumbnail'] = self.urljoin(host_alt, elem.get('imagen', ''))
                    elem_json['quality'] = elem.get('calidad', '')
                    elem_json['quality'] = elem_json['quality'].replace('creeener', 'creener')\
                                                               .replace('AC3 5.1', '').replace('HDTV 720p', 'HDTV-720p').strip()
                    elem_json['language'] = ['CAST']

                elem_json['media_path'] = self.movie_path.strip('/') if elem_json['mediatype'] == 'movie' else self.tv_path.strip('/')

                for clean_org, clean_des in finds_alt.get('title_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(elem_json['title'], clean_org):
                            elem_json['title'] = scrapertools.find_single_match(elem_json['title'], clean_org).strip()
                            break
                    else:
                        elem_json['title'] = re.sub(clean_org, clean_des, elem_json['title']).strip()
                title = elem_json['title'].lower().replace(' ', '_')
                if elem_json['mediatype'] != 'movie' and quality_control: title = '%s_%s' % (title, elem_json['quality'].replace('*', ''))
                if elem_json['mediatype'] == 'movie': elem_json['quality'] = elem_json['quality'].capitalize()

                language = elem_json.get('language', '')
                if not language or '*' in str(language): language = ['CAST']
                if matches_index.get('%s_%s_%s' % (title, language, elem_json['mediatype'])):
                    if elem_json['quality'] not in matches_index['%s_%s_%s' % (title, language, elem_json['mediatype'])]:
                        matches_index['%s_%s_%s' % (title, language, elem_json['mediatype'])] += [elem_json['quality']]
                    if DEBUG: logger.debug('DROP title dup: %s / %s' % ('%s_%s_%s' % (title, language, 
                                                                                      elem_json['mediatype']), elem_json['quality']))
                    continue

                matches_btdigg.append(elem_json.copy())
                matches_index['%s_%s_%s' % (title, language, elem_json['mediatype'])] = [elem_json['quality']]
                x += 1

                if x >= elem_cfg['cnt_tot'] * channel_entries: 
                    break

            y -= x
            if y <= 0: 
                break
        
    except Exception:
        logger.error(traceback.format_exc())

    if DEBUG: logger.debug('matches_PY: %s / %s \n%s' % (len(matches_btdigg), matches_btdigg, matches_index))
    return matches_btdigg, matches_index


def AH_find_btdigg_list_all_from_BTDIGG(self, item, matches=[], matches_index={}, channel_alt=channel_py, 
                                        channel_entries=15, btdigg_entries=45, **AHkwargs):
    logger.info('"%s"' % len(matches))

    matches_inter = []
    matches_btdigg = matches[:]
    matches_len = len(matches_btdigg)
    titles_search = [{'urls': ['%sHDTV 720p'], 'checks': ['Cap.']} if item.c_type == 'series' else \
                     {'urls': ['%sBluray Castellano'], 'checks': ['Cast', 'Esp', 'Spanish', '%s' % channel_alt.replace('4k', '')]} \
                                                                   if item.c_type == 'peliculas' else {}]
    if item.c_type == 'search':
        titles_search = [{'urls': ['%s ' + channel_alt], 'checks': ['Cast', 'Esp', 'Spanish', '%s' % channel_alt.replace('4k', '')]}, 
                         {'urls': ['%s Bluray Castellano'], 'checks': ['Cast', 'Esp', 'Spanish', '%s' % channel_alt.replace('4k', '')]},
                         {'urls': ['%s HDTV 720p'], 'checks': ['Cap.']}]
    controls = self.finds.get('controls', {})
    disable_cache = True
    quality_control = AHkwargs.get('btdigg_quality_control', controls.get('btdigg_quality_control', False))
    canonical = AHkwargs.get('canonical', self.canonical)

    title_clean = AHkwargs.get('finds', {}).get('title_clean', [])
    title_clean.append(['(?i)\s*UNCUT', ''])
    patron_title = '(?i)(.*?)\s*(?:-*\s*temp|\(|\[)'
    patron_title_b = '(?i)(.*?)\s*(?:-*\s*temp|\(|\[|\s+-)'
    patron_year = '\(?(\d{4})\)?'

    language_alt = []

    try:
        if canonical.get('global_search_cancelled', False) or (config.GLOBAL_SEARCH_CANCELLED \
                                                           and canonical.get('global_search_active', False)):
            logger.info('## Búsqueda global cancelada: %s: %s' % (item.channel, item.title), force=True)
            return matches_btdigg, matches_index

        format_tmdb_id(item)

        if not PY3: from lib.alfaresolver import find_alternative_link, get_cached_files
        else: from lib.alfaresolver_py3 import find_alternative_link, get_cached_files

        for title_search in titles_search:

            quality_alt = '720p 1080p 2160p 4kwebrip 4k'
            if item.c_type in ['peliculas', 'search'] and 'HDTV' not in str(title_search['urls']):
                quality_alt += ' bluray rip screener'
                language_alt = ['DUAL', 'CAST', 'LAT']
                if item.c_type in ['search'] and channel_alt in str(title_search['urls']):
                    quality_alt += ' HDTV'
            else:
                if not quality_control:
                    quality_alt += ' HDTV'
                elif item.quality and '720' not in item.quality and '1080' not in item.quality and '4k' not in item.quality:
                    quality_alt = 'HDTV'

            torrent_params = {
                              'find_alt_news': [title_search] if item.c_type != 'search' else [], 
                              'title_prefix': [title_search] if item.c_type == 'search' else [], 
                              'quality_alt': quality_alt, 
                              'language_alt': language_alt, 
                              'find_alt_link_next': 0, 
                              'domain_alt': None, #find_alt_domains,
                              'extensive_search': False if item.c_type != 'search' else True,
                              'search_order': 2 if item.c_type != 'search' else 0,
                              'link_found_limit': 20000 if item.c_type != 'search' else 100000, 
                              'find_catched': True if item.c_type != 'search' else False
                              }

            limit_pages = int((btdigg_entries * (0.5 if item.c_type in ['peliculas', 'search'] else 1.4)) / 10)
            limit_pages_min = 2 if (channel_alt in str(title_search['urls']) or 'HDTV' in str(title_search['urls'])) else 1
            interface = str(config.get_setting('btdigg_status', server='torrent'))
            limit_items_found = 5 * 10 if interface != '200' else 10 * 10

            x = 0
            while x < limit_pages:
                torrent_params = find_alternative_link(item, torrent_params=torrent_params, cache=disable_cache)

                if not torrent_params.get('find_alt_link_result') and not torrent_params.get('find_alt_link_next'): x = 999999
                if not torrent_params.get('find_alt_link_result') and torrent_params.get('find_alt_link_next', 0) >= limit_pages_min: x = 999999
                if not torrent_params.get('find_alt_link_next'): x = 999999
                if torrent_params.get('find_alt_link_found') and int(torrent_params['find_alt_link_found']) < limit_items_found: 
                    limit_pages = int(int(torrent_params['find_alt_link_found']) / 10) + 1
                x += 1

                for y, elem in enumerate(torrent_params['find_alt_link_result']):
                    elem_json = {}
                    #logger.error(torrent_params['find_alt_link_result'][y])

                    try:
                        elem_json['url'] = elem.get('url', '')
                        elem_json['language'] = elem.get('language', [])
                        elem_json['quality'] = elem.get('quality', '').replace('HDTV 720p', 'HDTV-720p').replace(btdigg_label, '').strip()
                        elem_json['mediatype'] = 'tvshow' if 'Cap.' in elem_json['url'] else 'movie'
                        if elem_json['mediatype'] == 'movie': elem_json['quality'] = elem_json['quality'].capitalize()

                        elem_json['title'] = elem.get('title', '').replace(btdigg_label_B, '')
                        if scrapertools.find_single_match(elem_json['title'], patron_title).strip():
                            elem_json['title'] = scrapertools.find_single_match(elem_json['title'], patron_title).strip()
                        elif scrapertools.find_single_match(elem_json['title'], patron_title_b).strip():
                            elem_json['title'] = scrapertools.find_single_match(elem_json['title'], patron_title_b).strip()
                        else:
                            if DEBUG: logger.debug('Error en PATRON: %s / %s' % (elem_json['title'], patron_title))
                            continue
                        for clean_org, clean_des in title_clean:
                            if clean_des is None:
                                if scrapertools.find_single_match(elem_json['title'], clean_org):
                                    elem_json['title'] = scrapertools.find_single_match(elem_json['title'], clean_org).strip()
                                    break
                            else:
                                elem_json['title'] = re.sub(clean_org, clean_des, elem_json['title']).strip()
                        elem_json['title'] = elem_json['title'].replace('- ', '')
                        if scrapertools.find_single_match(elem_json['title'], patron_year):
                            elem_json['year'] = scrapertools.find_single_match(elem_json['title'], patron_year) or '-'
                            elem_json['title'] = re.sub(patron_year, '', elem_json['title']).strip()
                        title = elem_json['title'].lower().replace(' ', '_')
                        if elem_json['mediatype'] != 'movie' and quality_control: title = '%s_%s' % (title, elem_json['quality'])

                        if matches_index.get('%s_%s_%s' % (title, elem_json['language'], elem_json['mediatype'])):
                            if elem_json['quality'] not in matches_index['%s_%s_%s' % (title, elem_json['language'], elem_json['mediatype'])]:
                                matches_index['%s_%s_%s' % (title, elem_json['language'], elem_json['mediatype'])] += [elem_json['quality']]
                            if DEBUG: logger.debug('DROP title dup: %s / %s' % ('%s_%s_%s' % (title, elem_json['language'], 
                                                                                elem_json['mediatype']), elem_json['quality']))
                            continue

                        elem_json['media_path'] = self.movie_path.strip('/') if elem_json['mediatype'] == 'movie' else self.tv_path.strip('/')
                        elem_json['torrent_info'] = elem.get('size', '').replace(btdigg_label_B, '').replace('GB', 'G·B').replace('Gb', 'G·b')\
                                                                        .replace('MB', 'M·B').replace('Mb', 'M·b').replace('.', ',')
                        elem_json['size'] = elem.get('size', '').replace(btdigg_label_B, '')\
                                                                .replace('[COLOR magenta][B]RAR-[/B][/COLOR]', '')
                        if elem_json['mediatype'] == 'movie': elem_json['size'] = self.convert_size(elem_json['size'])

                        item.btdig_in_use =  True
                        matches_btdigg.append(elem_json.copy())
                        matches_index['%s_%s_%s' % (title, elem_json['language'], elem_json['mediatype'])] = [elem_json['quality']]

                    except Exception:
                        logger.error(traceback.format_exc())
                        continue
                    
        #if item.c_type == 'peliculas' and matches_btdigg: matches_btdigg = sorted(matches_btdigg, key=lambda it: int(-it['size']))

    except Exception:
        logger.error(traceback.format_exc())

    if DEBUG: logger.debug('matches_BTDIGG: %s / %s \r\n%s' % (len(matches_btdigg), matches_btdigg, matches_index))
    return matches_btdigg, matches_index


def AH_find_btdigg_list_all(self, item, matches=[], channel_alt=channel_py, **AHkwargs):
    logger.info('"%s"' % len(matches))

    canonical = self.canonical
    controls = self.finds.get('controls', {})
    quality_control = AHkwargs.get('btdigg_quality_control', controls.get('btdigg_quality_control', False))
    if not controls:
        return matches

    news_allowed = {
                    'dontorrent': ['peliculas', 'series', 'search'],
                    'ANY': ['peliculas', 'series', 'search']
                   }
    if not item or (item.c_type not in news_allowed.get(item.channel, []) and item.c_type not in news_allowed.get('ANY', [])):
        return matches

    format_tmdb_id(item)
    
    try:
        if canonical.get('global_search_cancelled', False) or (config.GLOBAL_SEARCH_CANCELLED \
                                                           and canonical.get('global_search_active', False)):
            logger.info('## Búsqueda global cancelada: %s: %s' % (item.channel, item.title), force=True)
            return matches

        channel_entries = controls.get('cnt_tot', 20)
        btdigg_entries = channel_entries * 4 if (item.c_type == 'peliculas' or quality_control) else channel_entries * 3
        matches_inter = []
        matches_btdigg = []
        matches_index = {}
        convert = ['.=', '-= ', ':=', '&= ', '  = ']
        matches_len = len(matches)

        for elem_json in matches[:channel_entries]:
            language = elem_json.get('language', '')
            if not language or '*' in str(language): language = elem_json['language'] = ['CAST']
            mediatype = elem_json['mediatype'] = elem_json.get('mediatype', '') or ('movie' if self.movie_path in elem_json['url'] else 'tvshow')

            if 'pelicula' in item.c_type or self.movie_path in elem_json.get('url', '') or mediatype == 'movie':
                title = scrapertools.slugify(re.sub('\s*\[.*?\]', '', elem_json.get('title', '')), 
                                             strict=False, convert=convert).strip().lower().replace(' ', '_')
                elem_json['quality'] = quality = elem_json.get('quality', '').replace('*', '').replace('-', ' ').capitalize()

            else:
                title = scrapertools.slugify(re.sub('\s+-\s+\d+.+?$', '', elem_json.get('title', '')), 
                                             strict=False, convert=convert).strip().lower().replace(' ', '_')
                quality = elem_json.get('quality', '').replace('*', '') or 'HDTV'
                if '[' in quality: quality = scrapertools.find_single_match(quality, '\[(.*?)\]').strip() or 'HDTV'
                if quality_control: title = '%s_%s' % (title, quality)
            
            if matches_index.get('%s_%s_%s' % (title, language, mediatype)):
                if quality not in matches_index['%s_%s_%s' % (title, language, mediatype)]:
                    matches_index['%s_%s_%s' % (title, language, mediatype)] += [quality]
                continue
            matches_index['%s_%s_%s' % (title, language, mediatype)] = [quality]

            matches_inter.append(elem_json.copy())

        matches_btdigg = matches_inter[:]
        matches = []

        if channeltools.is_enabled(channel_alt):
            matches_btdigg, matches_index = AH_find_btdigg_list_all_from_channel_py(self, item, matches=matches_btdigg, 
                                                                                    matches_index=matches_index, channel_alt=channel_alt, 
                                                                                    channel_entries=channel_entries, btdigg_entries=btdigg_entries, 
                                                                                    **AHkwargs)
        matches_btdigg, matches_index = AH_find_btdigg_list_all_from_BTDIGG(self, item, matches=matches_btdigg, matches_index=matches_index, 
                                                                            channel_alt=channel_alt, channel_entries=channel_entries, 
                                                                            btdigg_entries=btdigg_entries, **AHkwargs)

        x = 0
        for elem_json in matches_btdigg:
            #logger.error(elem_json)
            if 'magnet' in elem_json['url'] or channel_alt in elem_json.get('thumbnail', ''):

                # Slugify, pero más light
                elem_json['title'] = scrapertools.htmlclean(elem_json['title']).strip()
                elem_json['title'] = elem_json['title'].replace("á", "a").replace("é", "e").replace("í", "i")\
                                                       .replace("ó", "o").replace("ú", "u").replace("ü", "u")\
                                                       .replace("ï¿½", "ñ").replace("Ã±", "ñ").replace(' - ', ' ')
                elem_json['title'] = scrapertools.decode_utf8_error(elem_json['title']).strip()
                if "en espa" in elem_json['title']: elem_json['title'] = elem_json['title'][:-11]

                language = 'latino' if 'latino/' in elem_json['url'] else ''
                elem_json['language'] = '*latino' if 'latino/' in elem_json['url'] else elem_json.get('language', '*')
                media_path = elem_json.pop('media_path', '')
                url_final = '%s%s_btdig/%s%s' % (btdigg_url, media_path, language, elem_json['title'].replace(' ', '-').lower().strip())
                quality = elem_json['quality'].capitalize().replace(btdigg_label, '').split(', ')
                elem_json['quality'] = '%s%s' % (elem_json['quality'].capitalize(), btdigg_label)
                elem_json['btdig_in_use'] = True
                url_save = scrapertools.slugify(re.sub('(?:\s+\(+\d{4}\)+$|\s*-\s*Temp.*?$|\s+-\s+\d+.*?$)', '', elem_json['title']), 
                                                strict=False, convert=convert)

                if elem_json['mediatype'] == 'movie':
                    elem_json['url'] = url_final
                    x += 1
                    matches.append(elem_json.copy())

                elif elem_json['mediatype'] in ['tvshow', 'episode'] or 'documental' in elem_json['url']:
                    elem_json['title'] = re.sub('(?i)\s*-*\s*temp\w*\s*\d*\s*', '', elem_json['title'])
                    if not quality_control:
                        quality = "HDTV, HDTV-720p"
                        elem_json['quality'] = "HDTV, HDTV-720p%s" % btdigg_label
                        elem_json['url'] = url_final
                        if item.extra in ['novedades']: elem_json['title_subs'] = ['BTDIGG_INFO']
                        x += 1
                        matches.append(elem_json.copy())

                    else:
                        for q in ['HDTV', 'HDTV-720p']:
                            title_temp = '%s [%s]' % (url_save, q)
                            quality = q
                            elem_json['quality'] = '%s%s' % (q, btdigg_label)
                            elem_json['url'] = '%s%s' % (url_final, '-%s' % q if '720p' in q else '')
                            if item.extra in ['novedades']: 
                                elem_json['title_subs'] = ['BTDIGG_INFO', unify.set_color('720p', 'quality') if '720p' in q else '']
                            x += 1
                            matches.append(elem_json.copy())

            else:
                matches.append(elem_json.copy())

            if x >= btdigg_entries + matches_len: 
                break

    except Exception:
        logger.error(traceback.format_exc())

    for elem_json in matches:
        language = elem_json.get('language', '')
        if not language or '*' in str(language): language = ['CAST']
        mediatype = elem_json['mediatype'] = elem_json.get('mediatype', '') or ('movie' if self.movie_path in elem_json['url'] else 'tvshow')
        title = elem_json['title'].lower().replace(' ', '_')
        if mediatype != 'movie' and quality_control: title = '%s_%s' % (title, elem_json['quality'].replace('*', '').replace(btdigg_label, ''))
        if mediatype == 'movie': elem_json['quality'].capitalize()
        
        if matches_index.get('%s_%s_%s' % (title, language, mediatype)):
            quality = elem_json['quality'].replace('*', '').replace(btdigg_label, '').split(', ')
            for q in quality:
                if not q in matches_index['%s_%s_%s' % (title, language, mediatype)]:
                    matches_index['%s_%s_%s' % (title, language, mediatype)] += [q]

            elem_json['quality'] = ', '.join(q for q in matches_index['%s_%s_%s' % (title, language, mediatype)]).rstrip(', ')

        if btdigg_url in elem_json['url'] or ',' in elem_json['quality']:
            elem_json['quality'] = elem_json['quality'].replace(btdigg_label, '') + btdigg_label

    return matches


def CACHING_find_btdigg_list_all_NEWS_from_BTDIGG_(options=None):
    logger.info()

    import xbmc
    monitor = xbmc.Monitor()
    if not PY3: from lib.alfaresolver import find_alternative_link
    else: from lib.alfaresolver_py3 import find_alternative_link
    from lib.AlfaChannelHelper import DictionaryAllChannel

    item = Item()

    titles_search = [[{'urls': ['%sBluray ' + channel_py], 'checks': ['Cast', 'Esp', 'Spanish', '%s' % channel_py.replace('4k', '')]}, 'movie'], 
                     [{'urls': ['%sBluray Castellano'], 'checks': ['Cast', 'Esp', 'Spanish', '%s' % channel_py.replace('4k', '')]}, 'movie'], 
                     [{'urls': ['%sHDTV 720p ' + channel_py], 'checks': ['Cap.']}, 'tvshow'], 
                     [{'urls': ['%sHDTV 720p'], 'checks': ['Cap.']}, 'tvshow']]

    btdigg_entries = 50
    disable_cache = True
    torrent_params = {}
    cached = {'movie': [], 'tvshow': [], 'episode': {}}
    language_alt = []
    matches = []
    matches_index = {}
    patron_sea = 'Cap.(\d+)\d{2}'
    patron_cap = 'Cap.\d+(\d{2})'
    patron_title = '(?i)(.*?)\s*(?:-*\s*temp|\(|\[)'

    try:
        channel = __import__('channels.%s' % channel_py, None,
                             None, ["channels.%s" % channel_py])
        self = DictionaryAllChannel(channel.host, channel=channel_py, finds=channel.finds, debug=DEBUG)
        item.contentType = contentType = 'episode'
        item.c_type = 'series'

        for item.page in range(1, 6):
            matches, matches_index = (AH_find_btdigg_list_all_from_channel_py(self, item, matches=matches, matches_index=matches_index))
            if not matches: break
            if monitor.waitForAbort(10):
                return

        for elem in matches:
            try:
                elem['season'], elem['episode'] = scrapertools.find_single_match(elem['url'], '(?i)\/temp\w*-?(\d+)\/cap\w*-?(\d+)')
                elem['season'] = int(elem['season'])
                elem['episode'] = int(elem['episode'])
                elem['mediatype'] = 'episode'
            except Exception:
                logger.error('Error en EPISODIO: %s' % elem['url'])

            cached[contentType][elem['title'].lower()] = elem

        if not cached[contentType]:
            titles_search.extend([[{'urls': ['%sHDTV 720p ' + channel_py], 'checks': ['Cap.']}, 'episode']])
        
        for title_search, contentType in titles_search:

            quality_alt = '720p 1080p 2160p 4kwebrip 4k'
            if 'bluray' in str(title_search).lower():
                quality_alt += ' bluray rip screener'
                language_alt = ['DUAL', 'CAST', 'LAT']
            elif contentType == 'episode':
                quality_alt = '720p'
            else:
                quality_alt += ' HDTV'

            limit_pages = int((btdigg_entries * (1 if contentType == 'movie' else 1.4 if contentType == 'tvshow' else 3)) / 10)
            limit_items_found = int(btdigg_entries * (1 if contentType == 'movie' else 1.4 if contentType == 'tvshow' else 2))
            item.contentType = contentType
            item.c_type = 'peliculas' if contentType == 'movie' else 'series'
            cached_str = str(cached[contentType])

            torrent_params = {
                              'find_alt_news': [title_search], 
                              'quality_alt': quality_alt, 
                              'language_alt': language_alt, 
                              'find_alt_link_next': 0, 
                              'link_found_limit': limit_items_found, 
                              'domain_alt': None,
                              'extensive_search': False,
                              'search_order': 2,
                              'link_found_limit': 20000
                              }

            x = 0
            while x < limit_pages:
                torrent_params = find_alternative_link(item, torrent_params=torrent_params, cache=disable_cache)

                if torrent_params.get('find_alt_link_code', '') in ['200']:
                    if not torrent_params.get('find_alt_link_result') and not torrent_params.get('find_alt_link_next'): x = 999999
                    if not torrent_params.get('find_alt_link_next'): x = 999999
                    if torrent_params.get('find_alt_link_found') and int(torrent_params['find_alt_link_found']) < limit_items_found: 
                        limit_pages = int(int(torrent_params['find_alt_link_found']) / 10) + 1
                x += 1

                for elem in torrent_params.get('find_alt_link_result', []):
                    #logger.error(elem)
                    if elem.get('url', '') in cached_str: continue

                    if contentType == 'episode':
                        try:
                            elem['title'] = elem.get('title', '').replace(btdigg_label_B, '')
                            elem['season'] = int(scrapertools.find_single_match(elem['title'], patron_sea))
                            elem['episode'] = int(scrapertools.find_single_match(elem['title'], patron_cap))
                            elem['title'] = scrapertools.find_single_match(elem['title'], patron_title)
                            if not elem['title']: continue
                            if elem['title'] in cached[contentType].get(elem['title'].lower(), ''): continue
                        except Exception:
                            logger.error('Error en EPISODIO: %s' % elem['url'])
                            continue
                        cached[contentType][elem['title'].lower()] = elem

                    else:
                        cached[contentType].append(elem.copy())

                    if len(cached[contentType])> limit_items_found: 
                        x = 999999
                        break

                if monitor.waitForAbort(5):
                    return

            window.setProperty("alfa_cached_btdigg_%s" % contentType, str(cached[contentType]))
            if monitor.waitForAbort(1 * 60):
                return

        if not window.getProperty("alfa_cached_btdigg_episode"):
            window.setProperty("alfa_cached_btdigg_episode", str(cached['episode']))

    except Exception:
        logger.error(traceback.format_exc())


def AH_find_btdigg_seasons(self, item, matches=[], domain_alt=channel_py, **AHkwargs):
    logger.info()
    global channel_py_episode_list

    controls = self.finds.get('controls', {})
    url = AHkwargs.pop('url', item.url)
    contentSeason = AHkwargs.pop('btdigg_contentSeason', controls.get('btdigg_contentSeason', 0))
    disable_cache = not AHkwargs.pop('btdigg_cache', controls.get('btdigg_cache', True))
    quality_control = AHkwargs.pop('btdigg_quality_control', controls.get('btdigg_quality_control', False))
    canonical = AHkwargs.pop('canonical', self.canonical)
    matches = sorted(matches, key=lambda it: int(it.get('season', 0))) if matches else []
    season_high = [elem_json['season'] for elem_json in matches] if matches else [0]
    channel_py_strict = False

    if (item.infoLabels['number_of_seasons'] in season_high and contentSeason == 0) \
                         or (contentSeason > 0 and contentSeason in season_high \
                         and season_high[-1] >= item.infoLabels['number_of_seasons']):
        return matches

    try:
        if canonical.get('global_search_cancelled', False) or (config.GLOBAL_SEARCH_CANCELLED \
                                                           and canonical.get('global_search_active', False)):
            logger.info('## Búsqueda global cancelada: %s: %s' % (item.channel, item.title), force=True)
            return itemlist

        format_tmdb_id(item)

        if not PY3: from lib.alfaresolver import find_alternative_link, get_cached_files
        else: from lib.alfaresolver_py3 import find_alternative_link, get_cached_files

        if item.library_urls and item.from_action not in ['update_tvshow'] and not item.sub_action:
            if not channel_py_episode_list: channel_py_episode_list = get_cached_files('episode')
            if item.contentSerieName.lower() in channel_py_episode_list:
                channel_py_strict = True

        season = item.infoLabels['number_of_seasons'] or 1
        seasons = season
        season_low = contentSeason or season_high[-1] + 1 or season
        if season != season_low:
            seasons = '%s-%s' % (season_low, season)
        elif btdigg_url in item.url:
            seasons = '1-%s' % season
            season_low = 1
        patron_sea = 'Cap.(\d+)\d{2}'

        quality_alt = '720p 1080p 2160p 4kwebrip 4k'
        if not quality_control:
            quality_alt +=  ' HDTV'
        elif '720' not in item.quality:
            quality_alt =  'HDTV'

        language_alt = ['DUAL', 'CAST'] if 'CAST' in item.language else ['DUAL', 'LAT'] if 'LAT' in item.language else ['DUAL', 'CAST', 'LAT']

        titles_search = []
        if season and season == season_low:
            titles_search.extend([{'urls': ['%s HDTV ' + domain_alt], 'checks': ['Cap.']}])
            if not channel_py_strict:
                titles_search.extend([{'urls': ['%s HDTV'], 'checks': ['Cap.']},
                                      {'urls': ['%s Temporada ' + str(season)], 'checks': ['Cap.']}])
        if season and season != season_low:
            titles_search.extend([{'urls': ['%s HDTV'], 'checks': ['Cap.']}])

        x = 0
        for title_search in titles_search:

            limit_pages = 7 if domain_alt in str(title_search['urls']) else 4
            limit_pages_min = 4 if domain_alt in str(title_search['urls']) else 1
            limit_items_found = 10 * 10

            torrent_params = {
                              'title_prefix': [title_search], 
                              'quality_alt': quality_alt, 
                              'language_alt': language_alt, 
                              'find_alt_link_season': seasons, 
                              'find_alt_link_next': 0, 
                              'link_found_limit': limit_items_found, 
                              'domain_alt': None,
                              'extensive_search': False if contentSeason > 0 else False
                              }

            x = 0
            while x < limit_pages:
                torrent_params = find_alternative_link(item, torrent_params=torrent_params, cache=disable_cache)

                if not torrent_params.get('find_alt_link_result') and not torrent_params.get('find_alt_link_next'): x = 999999
                if not torrent_params.get('find_alt_link_result') and torrent_params.get('find_alt_link_next', 0) >= limit_pages_min: x = 999999
                if not torrent_params.get('find_alt_link_next'): x = 999999
                if torrent_params.get('find_alt_link_found') and int(torrent_params['find_alt_link_found']) < limit_items_found: 
                    limit_pages = int(int(torrent_params['find_alt_link_found']) / 10) + 1
                x += 1

                for y, elem in enumerate(torrent_params['find_alt_link_result']):
                    elem_json = {}
                    #logger.error(torrent_params['find_alt_link_result'][y])

                    try:
                        if not scrapertools.find_single_match(elem.get('title', ''), patron_sea): continue
                        elem_json['season'] = int(scrapertools.find_single_match(elem.get('title', ''), patron_sea))
                        if elem_json['season'] in season_high: continue
                        if item.infoLabels['number_of_seasons'] \
                                            and elem_json['season'] > int(item.infoLabels['number_of_seasons']): continue
                        season_high += [elem_json['season']]

                        elem_json['url'] = '%sseries_btdig/%s%s' % (config.BTDIGG_URL, elem.get('language', []) or item.language \
                                            if item.language else '', item.contentSerieName.lower().replace(' ', '-'))
                        elem_json['magnet'] = elem.get('url', '')
                        elem_json['quality'] = '%s%s' % (elem.get('quality', '').upper().replace('P', 'p')\
                                                        .replace('HDTV 720p', 'HDTV-720p'), btdigg_label)
                        if item.quality:
                            if elem_json['quality'].replace(btdigg_label, '') not in item.quality:
                                elem_json['quality'] = '%s, %s' % (item.quality.replace(btdigg_label, ''), elem_json['quality'])
                            else:
                                elem_json['quality'] = '%s%s' % (item.quality.replace(btdigg_label, ''), btdigg_label)
                        elem_json['language'] = elem.get('language', []) or item.language
                        elem_json['size'] = elem.get('size', '')
                        
                        elem_json['title'] = ''

                        matches.append(elem_json.copy())
                        if elem_json['season'] == season_low and elem_json['season'] == season:
                            x = 888888
                            break

                    except Exception:
                        logger.error(traceback.format_exc())
                        continue

                if isinstance(seasons, int) and seasons in season_high:
                    x = 888888
                    break
            
            if x == 888888: break

        matches = sorted(matches, key=lambda it: int(it.get('season', 0)))

    except Exception:
        logger.error(traceback.format_exc())

    return matches


def AH_find_btdigg_episodes(self, item, matches=[], domain_alt=channel_py, **AHkwargs):
    global channel_py_episode_list

    controls = self.finds.get('controls', {})
    contentSeason = AHkwargs.pop('btdigg_contentSeason', controls.get('btdigg_contentSeason', 0))
    disable_cache = not AHkwargs.pop('btdigg_cache', controls.get('btdigg_cache', True))
    quality_control = AHkwargs.pop('btdigg_quality_control', controls.get('btdigg_quality_control', False))
    canonical = AHkwargs.pop('canonical', self.canonical)
    channel_py_strict = False

    season = seasons = item.infoLabels['season'] or 1
    episode_max = item.infoLabels['temporada_num_episodios'] or item.infoLabels['number_of_episodes'] or 1
    last_episode_to_air = item.infoLabels['last_episode_to_air'] or episode_max

    matches = sorted(matches, key=lambda it: int(it.get('episode', 0))) if matches else []
    matches_len = len(matches)
    epis_index = {}
    l_p_missing = []

    for x, epi in enumerate(matches):
        json_inter = {}
        if not epi.get('episode'): continue
        if epi['episode'] > last_episode_to_air: last_episode_to_air = epi['episode']
        epi['quality'] = epi.get('quality', 'HDTV').replace('*', '') or 'HDTV'
        if not epis_index.get(epi['episode']):
            epis_index[epi['episode']] = [[epi['episode'], x, epi['quality'].lower()]]
        else:
            epis_index[epi['episode']] += [[epi['episode'], x, epi['quality'].lower()]]

    for epi_avl in range(1, last_episode_to_air + 1):
        sxe = '%sx%s' % (item.infoLabels['number_of_seasons'], str(epi_avl).zfill(2))
        if sxe not in item.library_playcounts and epi_avl not in epis_index:
            l_p_missing += [sxe]

    logger.info('[LE: %s / EPI: %s / MAX: %s / MISSING: %s / MATCHES: %s]' % (item.infoLabels['last_episode_to_air'], 
                                                                              last_episode_to_air, episode_max, 
                                                                              l_p_missing, epis_index))

    if item.infoLabels['last_air_date'] and matches and (item.library_playcounts or item.video_path) \
                                        and item.from_action not in ['update_tvshow'] and not l_p_missing:
        if not item.sub_action or (item.sub_action and item.sub_action in ['auto']):
            try:
                res, episode_list = check_marks_in_videolibray(item, video_list_init=True)
                if res:
                    for x, epi in enumerate(matches):
                        season_episode = '%sx%s.strm' % (str(epi.get('season', 0)), str(epi.get('episode', 0)).zfill(2))
                        if not season_episode in str(episode_list):
                            if DEBUG: logger.debug('NUEVO EPI: %s' % season_episode)
                            break
                    else:
                        if DEBUG: logger.debug('NO NUEVOS EPIs')

                        try:
                            last_air_date = datetime.datetime.strptime(item.infoLabels['last_air_date'], "%Y-%m-%d")
                        except TypeError:
                            last_air_date = datetime.datetime(*(time.strptime(item.infoLabels['last_air_date'], "%Y-%m-%d")[0:6]))

                        now = datetime.datetime.now()
                        period = datetime.datetime.now() - last_air_date
                        days = period.days
                        seconds = period.seconds
                        if days < 0: days = 0; seconds = 0
                        if seconds < 0: seconds = 0
                        elapsed = (days*60*60*24) + seconds
                        expiration = 10*60*60*24
                        if elapsed > expiration:
                            if DEBUG: logger.debug('EPIs ANTIGUOs: %s' % item.infoLabels['last_air_date'])
                            
                            matches = AH_find_btdigg_matches(item, matches, **AHkwargs)
                            matches = sorted(matches, key=lambda it: (it.get('episode', 0), self.convert_size(it.get('size', 0)))) \
                                                                      if matches else []
                            return matches
                
                        if DEBUG: logger.debug('EPIs MODERNOS: %s' % item.infoLabels['last_air_date'])

            except Exception:
                logger.error(traceback.format_exc())

    try:
        if canonical.get('global_search_cancelled', False) or (config.GLOBAL_SEARCH_CANCELLED \
                                                           and canonical.get('global_search_active', False)):
            logger.info('## Búsqueda global cancelada: %s: %s' % (item.channel, item.title), force=True)
            return itemlist

        format_tmdb_id(item)

        if not PY3: from lib.alfaresolver import find_alternative_link, get_cached_files
        else: from lib.alfaresolver_py3 import find_alternative_link, get_cached_files

        if item.library_urls and item.from_action not in ['update_tvshow'] and not item.sub_action:
            if not channel_py_episode_list: channel_py_episode_list = get_cached_files('episode')
            if item.contentSerieName.lower() in channel_py_episode_list:
                channel_py_strict = True

        if not channel_py_strict and not l_p_missing:
            sxe_max = '%sx%s' % (item.infoLabels['number_of_seasons'], str(episode_max).zfill(2))
            if sxe_max in item.library_playcounts:
                return matches

        quality_alt = '720p 1080p 2160p 4kwebrip 4k'
        if not quality_control:
            quality_alt +=  ' HDTV'
        elif '720' not in item.quality:
            quality_alt =  'HDTV'

        language_alt = ['DUAL', 'CAST'] if 'CAST' in item.language else ['DUAL', 'LAT'] if 'LAT' in item.language else ['DUAL', 'CAST', 'LAT']

        titles_search = []
        if quality_alt ==  'HDTV':
            titles_search.extend([{'urls': ['%s HDTV ' + domain_alt], 'checks': ['Cap.']}])
        else:
            titles_search.extend([{'urls': ['%s HDTV ' + domain_alt, '%s 4K ' + domain_alt], 'checks': ['Cap.']}])
        if not channel_py_strict:
            titles_search.extend([{'urls': ['%s HDTV'], 'checks': ['Cap.']},
                                  {'urls': ['%s Temporada ' + str(season)], 'checks': ['Cap.']}])

        for title_search in titles_search:

            limit_pages = 7 if domain_alt in str(title_search['urls']) else 4
            limit_pages_min = 4 if domain_alt in str(title_search['urls']) else 1
            limit_items_found = 10 * 10
            patron_sea = 'Cap.(\d+)\d{2}'
            patron_cap = 'Cap.\d+(\d{2})'
            patron_title = '(?i)(.*?(?:\(\d{4}\))?)\s*(?:-*\s*temp|\[)'

            torrent_params = {
                              'title_prefix': [title_search], 
                              'quality_alt': quality_alt, 
                              'language_alt': language_alt, 
                              'find_alt_link_season': seasons, 
                              'find_alt_link_next': 0, 
                              'link_found_limit': limit_items_found, 
                              'domain_alt': None,
                              'extensive_search': False if contentSeason > 0 else False
                              }

            x = 0
            while x < limit_pages:
                torrent_params = find_alternative_link(item, torrent_params=torrent_params, cache=disable_cache)

                if not torrent_params.get('find_alt_link_result') and not torrent_params.get('find_alt_link_next'): x = 999999
                if not torrent_params.get('find_alt_link_result') and torrent_params.get('find_alt_link_next', 0) >= limit_pages_min: x = 999999
                if not torrent_params.get('find_alt_link_next'): x = 999999
                if torrent_params.get('find_alt_link_found') and int(torrent_params['find_alt_link_found']) < limit_items_found: 
                    limit_pages = int(int(torrent_params['find_alt_link_found']) / 10) + 1
                x += 1

                for y, elem in enumerate(torrent_params['find_alt_link_result']):
                    elem_json = {}
                    #logger.error(torrent_params['find_alt_link_result'][y])

                    try:
                        if not scrapertools.find_single_match(elem.get('title', ''), patron_sea): continue
                        elem_json['season'] = int(scrapertools.find_single_match(elem.get('title', ''), patron_sea))
                        if elem_json['season'] != item.infoLabels['season']: continue
                        if not scrapertools.find_single_match(elem.get('title', ''), patron_cap): continue
                        elem_json['episode'] = int(scrapertools.find_single_match(elem.get('title', ''), patron_cap))
                        if elem_json['episode'] > episode_max: continue
                        if elem_json['episode'] > last_episode_to_air: last_episode_to_air = episode_max

                        elem_json['url'] = elem.get('url', '')
                        elem_json['quality'] = elem.get('quality', '').upper().replace('P', 'p').replace('HDTV 720p', 'HDTV-720p')
                        ignore = False
                        for episode, index, quality in epis_index.get(elem_json['episode'], []):
                            if elem_json['quality'].lower() == quality:
                                ignore = True
                                break
                        if ignore:
                            if DEBUG: logger.debug('DROP Cap. dup: %s / %sx%s / %s' \
                                                    % (item.contentSerieName, elem_json['season'], elem_json['episode'], elem_json['quality']))
                            continue
                        elem_json['quality'] = '%s%s' % (elem_json['quality'], btdigg_label)
                        elem_json['torrent_info'] = elem.get('size', '')
                        elem_json['torrent_info'] += ' (%s)' % scrapertools.find_single_match(elem.get('title', '')\
                                                               .replace(btdigg_label_B, ''), patron_title)
                        elem_json['language'] = elem.get('language', []) or item.language
                        elem_json['size'] = elem_json['torrent_info'].replace(btdigg_label_B, '')\
                                                                     .replace('[COLOR magenta][B]RAR-[/B][/COLOR]', '')
                        elem_json['title'] = ''
                        elem_json['server'] = 'torrent'
                        elem_json['btdig_in_use'] = True

                        if elem_json['episode'] in epis_index:
                            matches.append(elem_json.copy())
                            epis_index[elem_json['episode']] += [[elem_json['episode'], len(matches) - 1, 
                                                                  elem_json['quality'].replace(btdigg_label, '').lower()]]
                        else:
                            matches.append(elem_json.copy())
                            epis_index[elem_json['episode']] = [[elem_json['episode'], len(matches) - 1, 
                                                                 elem_json['quality'].replace(btdigg_label, '').lower()]]
                    except Exception:
                        logger.error(traceback.format_exc())

            if len(epis_index) >= last_episode_to_air: break

        if matches_len == len(matches): matches = AH_find_btdigg_matches(item, matches, **AHkwargs)
        matches = sorted(matches, key=lambda it: (it.get('episode', 0), self.convert_size(it.get('size', 0)))) if matches else []
    
    except Exception:
        logger.error(traceback.format_exc())

    return matches


def AH_find_btdigg_findvideos(self, item, matches=[], domain_alt=channel_py, **AHkwargs):
    logger.info()

    if item.matches and item.channel != 'videolibrary' and item.contentChannel != 'videolibrary' and item.from_channel != 'videolibrary':
        return matches

    if matches and isinstance(matches[0], list):
        matches_in = matches[:]
        matches = []
        for scrapedtitle, scrapedmagnet, scrapedsize, scrapedquality in matches_in:
            matches.append({'bt_url': '', 'title': scrapedtitle, 'url': scrapedmagnet, 'size': scrapedsize, 'quality': scrapedquality})
    
    controls = self.finds.get('controls', {})
    contentSeason = AHkwargs.pop('btdigg_contentSeason', controls.get('btdigg_contentSeason', 0))
    disable_cache = False if (item.contentChannel == 'videolibrary' or item.from_channel == 'videolibrary' or not item.matches) else True
    quality_control = AHkwargs.pop('btdigg_quality_control', controls.get('btdigg_quality_control', False))
    canonical = AHkwargs.pop('canonical', self.canonical)
    matches_len = len(matches)
    language_alt = []

    try:
        if canonical.get('global_search_cancelled', False) or (config.GLOBAL_SEARCH_CANCELLED \
                                                           and canonical.get('global_search_active', False)):
            logger.info('## Búsqueda global cancelada: %s: %s' % (item.channel, item.title), force=True)
            return itemlist

        format_tmdb_id(item)

        if not PY3: from lib.alfaresolver import find_alternative_link
        else: from lib.alfaresolver_py3 import find_alternative_link

        quality_alt = '720p 1080p 2160p 4kwebrip 4k'
        if item.contentType == 'movie':
            titles_search = [{'urls': ['%s ' + domain_alt], 'checks': ['Cast', 'Esp', 'Spanish', '%s' % domain_alt.replace('4k', '')]}, 
                             {'urls': ['%s Bluray Castellano'], 'checks': ['Cast', 'Esp', 'Spanish', '%s' % domain_alt.replace('4k', '')]}]
            quality_alt +=  ' bluray rip screener'
            language_alt = ['DUAL', 'CAST'] if 'CAST' in item.language else ['DUAL', 'LAT'] if 'LAT' in item.language else ['DUAL', 'CAST', 'LAT']
        else:
            titles_search = [{'urls': ['%s Cap.' + '%s%s' % (item.contentSeason, str(item.contentEpisodeNumber).zfill(2))], 'checks': ['Cap.']}]
            if not quality_control:
                quality_alt +=  ' HDTV'
            elif '720' not in item.quality and '1080' not in item.quality and '4k' not in item.quality:
                quality_alt =  'HDTV'
            language_alt = ['DUAL', 'CAST'] if 'CAST' in item.language else ['DUAL', 'LAT'] if 'LAT' in item.language else ['DUAL', 'CAST', 'LAT']

        for title_search in titles_search:

            limit_pages = 3 if domain_alt in str(title_search['urls']) else 2
            limit_pages_min = 2 if domain_alt in str(title_search['urls']) else 1
            limit_items_found = 10 * 10
            patron_sea = 'Cap.(\d+)\d{2}'
            patron_cap = 'Cap.\d+(\d{2})'
            patron_title = '(?i)(.*?(?:\(\d{4}\))?)\s*(?:-*\s*temp|\[)'

            torrent_params = {
                              'title_prefix': [title_search], 
                              'quality_alt': quality_alt, 
                              'language_alt': language_alt, 
                              'find_alt_link_next': 0, 
                              'link_found_limit': limit_items_found, 
                              'domain_alt': None
                              }

            x = 0
            while x < limit_pages:
                torrent_params = find_alternative_link(item, torrent_params=torrent_params, cache=disable_cache)

                if not torrent_params.get('find_alt_link_result') and not torrent_params.get('find_alt_link_next'): x = 999999
                if not torrent_params.get('find_alt_link_result') and torrent_params.get('find_alt_link_next', 0) >= limit_pages_min: x = 999999
                if not torrent_params.get('find_alt_link_next'): x = 999999
                if torrent_params.get('find_alt_link_found') and int(torrent_params['find_alt_link_found']) < limit_items_found: 
                    limit_pages = int(int(torrent_params['find_alt_link_found']) / 10) + 1
                x += 1

                for y, elem in enumerate(torrent_params['find_alt_link_result']):
                    elem_json = {}
                    #logger.error(torrent_params['find_alt_link_result'][y])

                    try:
                        if item.contentType == 'episode':
                            if not scrapertools.find_single_match(elem.get('title', ''), patron_sea): continue
                            elem_json['season'] = int(scrapertools.find_single_match(elem.get('title', ''), patron_sea))
                            if elem_json['season'] != item.infoLabels['season']: continue
                            if not scrapertools.find_single_match(elem.get('title', ''), patron_cap): continue
                            elem_json['episode'] = int(scrapertools.find_single_match(elem.get('title', ''), patron_cap))
                            if elem_json['episode'] != item.contentEpisodeNumber: continue

                        elem_json['url'] = elem.get('url', '')
                        if elem_json['url'] in str(matches): 
                            if DEBUG: logger.debug('DROP: %s' % elem_json['url'])
                            continue

                        elem_json['language'] = elem.get('language', []) or item.language
                        elem_json['quality'] = elem.get('quality', '').replace('HDTV 720p', 'HDTV-720p').replace(btdigg_label, '')
                        q_match = False
                        for mate in matches:
                            if elem_json['quality'] in mate.get('quality', '').replace(btdigg_label, '').replace('*', ''):
                                for lang in elem_json['language']:
                                    if lang in mate.get('language', []) or mate.get('language', []) == '*':
                                        if DEBUG: logger.debug('DROP quality: %s' % elem_json['quality'])
                                        q_match = True
                        if q_match: continue
                        elem_json['quality'] = '%s%s' % (elem_json['quality'], btdigg_label)
                        elem_json['torrent_info'] = elem.get('size', '').replace('GB', 'G·B').replace('Gb', 'G·b')\
                                                                        .replace('MB', 'M·B').replace('Mb', 'M·b').replace('.', ',')
                        title = elem.get('title', '').replace(btdigg_label_B, '').replace('- ', '').replace(elem.get('quality', ''), '')
                        title = re.sub('(?i)BTDigg\s*|-\s+|\[.*?\]|Esp\w*\s*|Cast\w*\s*|Lat\w*\s*|span\w*' , '', title)
                        elem_json['torrent_info'] += ' (%s)' % title
                        elem_json['size'] = elem.get('size', '').replace(btdigg_label_B, '')\
                                                                .replace('[COLOR magenta][B]RAR-[/B][/COLOR]', '')
                        elem_json['server'] = 'torrent'
                        elem_json['btdig_in_use'] = True

                        matches.append(elem_json.copy())

                    except Exception:
                        logger.error(traceback.format_exc())
                        continue

        if matches_len == len(matches): matches = AH_find_btdigg_matches(item, matches, **AHkwargs)
        matches = sorted(matches, key=lambda it: (self.convert_size(it.get('size', 0)))) if matches else []
    
    except Exception:
        logger.error(traceback.format_exc())

    return matches


def find_rar_password(item):
    logger.info()
    from core import httptools
    
    try:
        channel_names = ['dontorrent', 'grantorrent', 'divxtotal']
        host_alt = []
        for channel_name in channel_names:
            channel = __import__('channels.%s' % channel_name, None,
                                     None, ["channels.%s" % channel_name])
            host_alt += [channel.host]
    except Exception:
        return item
    
    # Si no hay, buscamos en páginas alternativas
    rar_search = [
                 ['1', host_alt[0], [['<input\s*type="text"\s*id="txt_password"\s*' + \
                                'name="[^"]+"\s*onClick="[^"]+"\s*value="([^"]+)"']], [['capitulo-[^0][^\d]', 'None'], \
                                ['capitulo-', 'capitulo-0'], ['capitulos-', 'capitulos-0']]], 
                 ['2', host_alt[1], [[]], [['series(?:-\d+)?\/', 'descargar/serie-en-hd/'], \
                                ['-temporada', '/temporada'], ['^((?!serie).)*$', 'None'], \
                                ['.net\/', '.net/descargar/peliculas-castellano/'], ['\/$', '/blurayrip-ac3-5-1/']]], 
                 ['2', host_alt[2], [[]], [['^((?!temporada).)*$', 'None'], \
                                ['.net\/', '.net/descargar/peliculas-castellano/'], ['-microhd-1080p\/$', '']]]
    ]
    
    url_host = scrapertools.find_single_match(item.url, patron_host)
    dom_sufix_org = scrapertools.find_single_match(item.url, ':\/\/(.*?)[\/|?]').replace('.', '-')
    url_host_act = url_host
    url_password = item.url
    if item.referer:
        url_password = item.referer
    
    for y in ['2', '1']:
        for active, clone_id, regex_list, regex_url_list in rar_search:
            x = str(y)
            if item.password: break
            if active != x: continue
            if x == '2' and clone_id not in url_host: continue
            if x == '1' and clone_id in item.url: continue
            url_password = url_password.replace(url_host_act, clone_id)
            url_host_act = scrapertools.find_single_match(url_password, patron_host)

            dom_sufix_clone = scrapertools.find_single_match(url_host_act, ':\/\/(.*?)\/*$').replace('.', '-')
            if 'descargas2020' not in dom_sufix_clone and 'descargas2020' not in \
                        dom_sufix_clone and 'pctreload' not in dom_sufix_clone and \
                        'pctmix' not in dom_sufix_clone: dom_sufix_clone = ''
            dom_sufix_clone = dom_sufix_clone.replace('pctmix1-com', 'pctreload1-com')
            if dom_sufix_org and url_password.endswith(dom_sufix_org):
                url_password = url_password.replace(dom_sufix_org, dom_sufix_clone)
            else:
                url_password += dom_sufix_clone
            dom_sufix_org = dom_sufix_clone

            for regex, regex_rep in regex_url_list:
                if regex_rep == 'None':
                    if scrapertools.find_single_match(url_password, regex):
                        continue
                    else:
                        break
                if regex:
                    url_password = re.sub(regex, regex_rep, url_password)
            if 'grantorrent' in url_password:
                if item.contentType == 'episode':
                    url_password = '%scapitulo-%s/' % (url_password, item.contentEpisodeNumber)
            
            if x != '1': continue
            if url_host == clone_id: continue
            try:
                data_password = ''
                data_password = re.sub(r"\n|\r|\t|(<!--.*?-->)", "", httptools.downloadpage(url_password).data)
                data_password = data_password.replace("$!", "#!").replace("'", "\"").replace("Ã±", "ñ").replace("//pictures", "/pictures")
            except Exception:
                logger.error(traceback.format_exc(1))
            
            for regex_alt in regex_list:
                for regex in regex_alt:
                    if scrapertools.find_single_match(data_password, regex):
                        item.password = scrapertools.find_single_match(data_password, regex)
                        break
    
    logger.info('Contraseña vídeo: %s' % item.password)
    return item


def get_torrent_size(url, **kwargs):
    logger.info()
    from servers.torrent import caching_torrents
    
    """
    Módulo extraido del antiguo canal ZenTorrent
    
    Calcula el tamaño de los archivos que contienen un .torrent.  Descarga el archivo .torrent en una carpeta,
    lo lee y descodifica.  Si contiene múltiples archivos, suma el tamaño de todos ellos
    
    Llamada:            generictools.get_torrent_size(url, data_torrent=False)
    Entrada: url:       url del archivo .torrent
    Entrada: referer:   url de referer en caso de llamada con post
    Entrada: post:      contenido del post en caso de llamada con post
    torrent_params = {
                      'url': url,               url del archivo .torrent
                      'torrents_path': None,    Retorna el path the .torrent cacheado
                      'local_torr' = None,      Informa de la carpeta y archivo donde cachear el .torrent
                      'lookup', True,           en torrent.capture_thru_browser indica si solo da el aviso (False) o descarga (True)
                      'force': False,           Forzar cacheo del .torrent
                      'data_torrent': True,     Flag por si se quiere el contenido del .torretn de vuelta
                      'subtitles': True,        Se quieren subtitles_list de vuelta
                      'file_list': True,        Se quieren files de vuelta
                      'size': '',               str con el tamaño y tipo de medida ( MB, GB, etc)
                      'torrent_f': {},          dict() con el contenido del .torrent
                      'files': {},              dict() con los nombres de los archivos del torrent y su tamaño
                      'subtitles_list': [],     lista con archivos .str de subtítulos que acompañaban al .torrent
                      'cached': False,          True si el tarrent ha sido cacheado
                      'size_lista': [],         Lista de (.torrent, path)
                      'size_amount': [],        Lista de sizes si hay varios .torrents
                      'torrent_cached_list': [] Lista de torrents cacheados durante la sesión de Kodi
                      'time_elapsed':           Tiempo utilizado en la descarga del torrent.  0 si estaba cacheado
                      }
    """
    
    def convert_size(size):
        import math
        if (size == 0):
            return '0B'
        size_name = ("B", "KB", "M·B", "G·B", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size, 1024)))
        p = math.pow(1024, i)
        #s = round(size / p, 2)
        s = round(old_div(size, p), 2)
        return '%s %s' % (s, size_name[i])
    
    def decode(text):
        try:
            src = tokenize(text)
            if not PY3:
                data = decode_item(src.next, src.next())                        # Py2
            else:
                data = decode_item(src.__next__, next(src))                     # Py3
            for token in src:                                                   # look for more tokens
                raise SyntaxError("trailing junk")
        except (AttributeError, ValueError, StopIteration):
            try:
                data = data
            except Exception:
                data = src

        return data
        
    def tokenize(text, match=re.compile("([idel])|(\d+):|(-?\d+)").match):
        i = 0
        while i < len(text):
            m = match(text, i)
            s = m.group(m.lastindex)
            i = m.end()
            if m.lastindex == 2:
                yield "s"
                yield text[i:i + int(s)]
                i = i + int(s)
            else:
                yield s

    def decode_item(next, token):
        if token == "i":
            # integer: "i" value "e"
            data = int(next())
            if next() != "e":
                raise ValueError
        elif token == "s":
            # string: "s" value (virtual tokens)
            data = next()
        elif token == "l" or token == "d":
            # container: "l" (or "d") values "e"
            data = []
            tok = next()
            while tok != "e":
                data.append(decode_item(next, tok))
                tok = next()
            if token == "d":
                #data = dict(zip(data[0::2], data[1::2]))
                data = dict(list(zip(data[0::2], data[1::2])))
        else:
            raise ValueError
        return data

    # Móludo principal: iniciamos diccionario de variables
    torrent_params = kwargs.pop('torrent_params', {})
    torrent_params['url'] = url or torrent_params.get('url', '')
    torrent_params['torrents_path'] = torrent_params.get('torrents_path', '')
    torrent_params['local_torr'] = torrent_params.get('local_torr', '')
    torrent_params['lookup'] = torrent_params.get('lookup', True)
    torrent_params['force'] = torrent_params.get('force', False)
    torrent_params['data_torrent'] = torrent_params.get('data_torrent', False)
    torrent_params['subtitles'] = torrent_params.get('subtitles', False)
    torrent_params['file_list'] = torrent_params.get('file_list', False)
    torrent_params['channel'] = torrent_params.get('channel', '')
    torrent_params['torrent_alt'] = torrent_params.get('torrent_alt', '')
    torrent_params['find_alt_link_option'] = torrent_params.get('find_alt_link_option', False)
    torrent_params['find_alt_link_result_save'] = torrent_params.get('find_alt_link_result_save', [])
    torrent_params['domain_alt'] = torrent_params.get('domain_alt', '') or find_alt_domains
    torrent_params['size'] = ''
    torrent_params['torrent_f'] = {}
    torrent_params['files'] = {}
    torrent_params['subtitles_list'] = []
    torrent_params['cached'] = False
    torrent_params['size_lista'] = []
    torrent_params['size_amount'] = []
    torrent_params['torrent_cached_list'] = []
    torrent_params['time_elapsed'] = 0
    torrent_params['find_alt_link_result'] = []
    torrent_params['find_alt_link_found'] = 0
    torrent_params['find_alt_link_next'] = 0
    if not url:
        torrent_params['size'] = 'ERROR'
        return torrent_params
    
    retry_CF = kwargs.get('retries_cloudflare', 2)
    if retry_CF < 0: torrent_params['torrents_path'] = 'CF_BLOCKED'
    torrent_file =  torrent_params.pop('torrent_file', '')
    if torrent_file: torrent_params['torrents_path'] = 'torrent_file'
    DOWNLOAD_PATH = config.get_setting('downloadpath', default='')
    
    if PY3 and isinstance(url, bytes):
        torrent_params['url'] = "".join(chr(x) for x in bytes(torrent_params['url']))
    if PY3 and isinstance(torrent_params['torrents_path'], bytes):
        torrent_params['torrents_path'] = "".join(chr(x) for x in bytes(torrent_params['torrents_path']))
    if PY3 and isinstance(torrent_params['local_torr'], bytes):
        torrent_params['local_torr'] = "".join(chr(x) for x in bytes(torrent_params['local_torr']))

    # Si queremos cachear el torrent se debe especificar el nombre del archivo de salida, con o sin path absoluto
    # Si se había cacheado previamente, se usa el archivo especificado
    if torrent_params['local_torr'] and not torrent_params['local_torr'].startswith('http') \
                       and not torrent_params['local_torr'].startswith('magnet'):
        torrent_params['cached'] = True
        if not filetools.isfile(torrent_params['local_torr']):
            if DOWNLOAD_PATH and filetools.dirname(DOWNLOAD_PATH.rstrip('/').rstrip('\\')) not in torrent_params['local_torr'] \
                             and not scrapertools.find_single_match(torrent_params['local_torr'], 
                            '(?:\d+x\d+)?\s+\[.*?\]_\d+'):
                torrent_params['local_torr'] = filetools.join(DOWNLOAD_PATH, 
                          'cached_torrents_Alfa', torrent_params['local_torr'])
            if not filetools.isfile(torrent_params['local_torr']):
                torrent_params['cached'] = False

    try:        
        # Si es lookup, verifica si el canal tiene activado el Autoplay.  Si es así, retorna sin hacer el lookup
        if torrent_params['lookup'] and not torrent_params['force'] and not torrent_params['cached']:
            is_channel = inspect.getmodule(inspect.currentframe().f_back)
            is_channel = scrapertools.find_single_match(str(is_channel), "<module\s*'channels\.(.*?)'")
            if is_channel:
                from channels import autoplay
                res = autoplay.is_active(is_channel)
                if res:
                    torrent_params['url'] = 'autoplay'
                    return torrent_params
        
        if not torrent_params['lookup']: kwargs['timeout'] = kwargs.get('timeout', 5) * 3
        if (torrent_params['url'] and not torrent_params['cached'] and retry_CF > 0 \
                                  and 'DUMMY' not in torrent_params['url'] and not torrent_file) \
                                  or torrent_params['url'].startswith("magnet"):
            
            torrent_file, torrent_params = caching_torrents(torrent_params['url'], torrent_params, **kwargs)
        
        elif torrent_params['cached']:
            torrent_file = filetools.read(torrent_params['local_torr'], mode='rb')
            torrent_params['torrents_path'] = torrent_params['local_torr']
        
        if torrent_params['url'].startswith("magnet"):
            torrent_params['size'] = ''
            logger.info('Torrent SIZE: %s-%s - %s' % ('MAGNET', torrent_params['torrents_path'], 
                         torrent_params['time_elapsed'] or torrent_params['cached']), force=True)
            return torrent_params
        
        if isinstance(torrent_params['torrents_path'], list):
            torrents_path_list = torrent_params['torrents_path'][:]
            torrent_lista = True
        else:
            torrents_path_list = [(torrent_params['torrents_path'], torrent_file)]
            torrent_lista = False
        
        for torrent_params['torrents_path'], torrent_file in torrents_path_list:
            torrent_params['size'] = ''
            if not torrent_params['torrents_path'] or 'CF_BLOCKED' in torrent_params['torrents_path'] \
                        or (PY3 and isinstance(torrent_file, bytes) and torrent_file.startswith(b"magnet")) \
                        or (isinstance(torrent_file, str) and torrent_file.startswith("magnet")):
                torrent_params['size'] = 'ERROR'
                
                # si el archivo .torrent está bloqueado con CF, se intentará descargarlo a través de un browser externo
                if torrent_params['torrents_path'] == 'CF_BLOCKED':
                    torrent_params['size'] += ' [COLOR hotpink][B]BLOQUEO[/B][/COLOR]'
                    browser, res = call_browser('', lookup=True, strict=True)
                    if not browser:
                        browser, res = call_browser('', lookup=True)
                    if not browser:
                        torrent_params['size'] += ': [COLOR magenta][B]Instala un browser externo para usar este enlace[/B][/COLOR] (Chrome, Firefox, Opera)'
                    elif res is None and not config.get_setting("capture_thru_browser_path", server="torrent", default=""):
                        torrent_params['size'] += ': [COLOR gold][B]Introduce la ruta para usar con [I]%s[/I][/B][/COLOR]' % browser
                    elif res is None and config.get_setting("capture_thru_browser_path", server="torrent", default=""):
                        torrent_params['size'] += ': [COLOR limegreen][B]Pincha para usar con [I]%s[/I][/B][/COLOR]' % browser
                    elif res or config.get_setting("capture_thru_browser_path", server="torrent", default=""):
                        if res and res is not True:
                            config.set_setting("capture_thru_browser_path", res, server="torrent")
                            torrent_params['size'] += ': [COLOR limegreen][B]Pincha para usar con [I]%s[/I][/B][/COLOR]' % browser
                        elif res and not config.get_setting("capture_thru_browser_path", server="torrent", default=""):
                            torrent_params['size'] += ': [COLOR gold][B]Introduce la ruta para usar con [I]%s[/I][/B][/COLOR]' % browser
                        else:
                            torrent_params['size'] += ': [COLOR limegreen][B]Pincha para usar con [I]%s[/I][/B][/COLOR]' % browser
                    else:
                        torrent_params['size'] += ': [COLOR gold][B]Introduce la ruta para usar con [I]%s[/I][/B][/COLOR]' % browser
                    
                    if torrent_params['find_alt_link_option'] and torrent_params['find_alt_link_result_save']:
                        torrent_params['find_alt_link_result'] = torrent_params['find_alt_link_result_save'][:]
                        torrent_params['find_alt_link_result_save'] = []
                    elif torrent_params['find_alt_link_option'] and kwargs.get('item', {}):
                        if not PY3: from lib.alfaresolver import find_alternative_link
                        else: from lib.alfaresolver_py3 import find_alternative_link
                        torrent_params = find_alternative_link(kwargs['item'], torrent_params=torrent_params, cache=True)
                
                logger.info('Torrent SIZE: %s-%s - %s' % (str(torrent_params['size']), torrent_params['torrents_path'], 
                             torrent_params['time_elapsed'] or torrent_params['cached']), force=True)
                return torrent_params

            if PY3 and isinstance(torrent_file, bytes):                         # Convertimos a String para poder hacer el decode
                torrent_file = "".join(chr(x) for x in torrent_file)
            torrent_params['torrent_f'] = decode(torrent_file)                  # Decodificamos el .torrent

            #si sólo tiene un archivo, tomamos la longitud y la convertimos a una unidad legible, si no dará error
            try:
                sizet = torrent_params['torrent_f']["info"]['length']
                torrent_params['size'] = convert_size(sizet)
                
                torrent_params['files'] = torrent_params['torrent_f']["info"].copy()
                if 'path' not in torrent_params['files']: torrent_params['files'].update({'path': ['']})
                if 'piece length' in torrent_params['files']: del torrent_params['files']['piece length']
                if 'pieces' in torrent_params['files']: del torrent_params['files']['pieces']
                if 'name' in torrent_params['files']: del torrent_params['files']['name']
                torrent_params['files'] = [torrent_params['files']]
                torrent_params['files'].append({"__name": torrent_params['torrent_f']["info"]["name"], 'length': 0})
                torrent_params['size_lista'] += [(torrent_params['size'], torrent_params['torrents_path'], 
                            torrent_params['torrent_f'], torrent_params['files'])]
            except Exception:
                pass
                
            #si tiene múltiples archivos sumamos la longitud de todos
            if not torrent_params['size']:
                try:
                    check_video = scrapertools.find_multiple_matches(str(torrent_params['torrent_f']["info"]["files"]), "'length': (\d+).*?}")
                    sizet = sum([int(i) for i in check_video])
                    torrent_params['size'] = convert_size(sizet)
                    
                    torrent_params['files'] = torrent_params['torrent_f']["info"]["files"][:]
                    torrent_params['files'].append({"__name": torrent_params['torrent_f']["info"]["name"], 'length': 0})
                    
                except Exception:
                    torrent_params['size'] = 'ERROR'
                    logger.error(traceback.format_exc())
            
            # Marcamos si es hay archivos RAR
            if '.rar' in str(torrent_params['files']):
                torrent_params['size'] = '[COLOR magenta][B]RAR-[/B][/COLOR]%s' % torrent_params['size']
                
            # Puede haber errores de decode en los paths.  Se intentan arreglar
            try:
                for entry in torrent_params['files']:
                    for file, path in list(entry.items()):
                        if file == 'path':
                            for x, file_r in enumerate(path):
                                entry[file][x] = scrapertools.decode_utf8_error(file_r)
                        elif file == '__name':
                            entry[file] = scrapertools.decode_utf8_error(path)
            except Exception:
                logger.error(traceback.format_exc())
            
            torrent_params['files'] = sorted(torrent_params['files'], reverse=True, key=lambda k: k['length'])
            torrent_params['size_lista'] += [(torrent_params['size'], torrent_params['torrents_path'], 
                            torrent_params['torrent_f'], torrent_params['files'])]
            torrent_params['size_amount'] += [torrent_params['size']]
        
        if len(torrent_params['size_amount']) > 1:
            torrent_params['size'] = str(torrent_params['size_amount'])

    except Exception:
        torrent_params['size'] = 'ERROR'
        torrent_params['torrent_f'] = {}
        torrent_params['files'] = {}
        torrent_params['torrents_path'] = ''
        torrent_params['subtitles_list'] = []
        torrent_lista = False
        logger.error('ERROR al buscar el tamaño de un .Torrent: ' + str(torrent_params['url']))
        logger.error(traceback.format_exc())

    logger.info('Torrent SIZE: %s - %s' % (str(torrent_params['size']), 
                 torrent_params['time_elapsed'] or torrent_params['cached']), force=True)

    return torrent_params


def verify_channel(channel, clones_list=False):
    
    # Lista con los datos de los canales alternativos
    # Cargamos en .json del canal para ver las listas de valores en settings
    
    clones = []

    """
    if channel_py:
        clones = channeltools.get_channel_json(channel_py)
        for settings in clones['settings']:                                     # Se recorren todos los settings
            if settings['id'] == "clonenewpct1_channels_list":                  # Encontramos en setting
                clones = settings['default']                                    # Carga lista de clones
                channel_alt = "'%s'" % channel
                break
    """

    if clones_list:
        if clones:
            import ast
            clones = ast.literal_eval(clones)
        return channel, (clones or [channel])
        
    return channel
 
                            
def call_browser(url, download_path='', lookup=False, strict=False, wait=False, intent='', dataType=''):
    logger.info()
    # Basado en el código de "Chrome Launcher 1.2.0" de Jani (@rasjani) Mikkonen
    # Llama a un browser disponible y le pasa una url
    import xbmc
    import subprocess
    
    exePath = {}
    PATHS = []
    PLATAFORMA = config.get_system_platform()
    PM_LIST = ''
    creationFlags = 0
    prefs_file = ''
    res = None
    browsers = []
    SAVED_D_PATH = config.get_setting("capture_thru_browser_path", server="torrent", default="")

    try:
        # Establecemos las variables relativas a cada browser
        browser_params = {
                          "chrome": ['<html><body style="background:black"><script>window.location.href = "%s";</script></body></html>' % url, 
                                     ['--start-maximized', '--disable-translate', '--disable-new-tab-first-run', 
                                     '--no-default-browser-check', '--no-first-run '], 
                                     '', '"savefile"\s*:\s*{.*?"default_directory"\s*:\s*"([^"]+)"'], 
                          "chromium": ['<html><body style="background:black"><script>window.location.href = "%s";</script></body></html>' % url, 
                                       ['--noerordialogs', '--disable-session-crashed-bubble', '--disable-infobars', '--start-maximized'], 
                                       '', '"savefile"\s*:\s*{.*?"default_directory"\s*:\s*"([^"]+)"'], 
                          "firefox": ['<html><body style="background:black"><script>window.location.href = "%s";</script></body></html>' % url, 
                                      [], 
                                      'Default=(.*?)[\r|\n]', 'user_pref\s*\("browser.download.dir",\s*"([^"]+)"\)'], 
                          "opera": ['<html><body style="background:black"><script>window.location.href = "%s";</script></body></html>' % url, 
                                    [], 
                                    '', '"savefile"\s*:\s*{.*?"default_directory"\s*:\s*"([^"]+)"']
                         }

        # Establecemos las variables relativas a cada plataforma
        if PLATAFORMA in ['android', 'atv2']:
            try:
                ANDROID_STORAGE = os.getenv('ANDROID_STORAGE')
            except Exception:
                ANDROID_STORAGE = ''
            if not ANDROID_STORAGE:
                if "'HOME'" in os.environ:
                    ANDROID_STORAGE = scrapertools.find_single_match(os.getenv('HOME'), '^(\/.*?)\/')
                    if not ANDROID_STORAGE:
                        ANDROID_STORAGE = '/storage'
                else:
                    ANDROID_STORAGE = '/storage'
            
            exePath = {
                       "chrome": [[ANDROID_STORAGE + '/emulated/0/Android/data/com.android.chrome',
                                   ANDROID_STORAGE + '/emulated/0/Android/data/com.chrome.canary'], 
                                  0, 'ANDROID_DATA', [], ['/user/0/com.android.chrome/app_chrome/Default/Preferences', 
                                  '/user/0/com.chrome.canary/app_chrome/Default/Preferences']], 
                       "chromium": [[ANDROID_STORAGE + '/emulated/0/Android/data/org.bromite.chromium', 
                                     ANDROID_STORAGE + '/emulated/0/Android/data/org.chromium.webview_shell'], 
                                    0, 'ANDROID_DATA', [], ['/user/0/org.bromite.chromium/app_chrome/Default/Preferences', 
                                    '/user/0/org.chromium.webview_shell/app_chrome/Default/Preferences']], 
                       "firefox": [[ANDROID_STORAGE + '/emulated/0/Android/data/org.mozilla.firefox'], 
                                   0, 'ANDROID_DATA', ['/user/0/org.mozilla.firefox/files/mozilla/installs.ini', 
                                   '/user/0/org.mozilla.firefox/files/mozilla/profiles.ini'], ['prefs.js']],
                       "opera": [[ANDROID_STORAGE + '/emulated/0/Android/data/com.opera.browser', 
                                  ANDROID_STORAGE + '/emulated/0/Android/data/com.vewd.core.integration.dia', 
                                  os.getenv('ANDROID_DATA') + '/user/0/com.vewd.core.integration.dia', 
                                  ANDROID_STORAGE + '/emulated/0/Android/data/com.opera.sdk.example', 
                                  os.getenv('ANDROID_DATA') + '/user/0/com.opera.sdk.example'], 
                                 0, 'ANDROID_DATA', [], ['/user/0/com.opera.browser/Preferences', 
                                 'user/0/com.vewd.core.integration.dia/Preferences', 'user/0/com.opera.sdk.example/Preferences']]
                      }
        
            PATHS = [ANDROID_STORAGE + '/emulated/0/Android/data', os.getenv('ANDROID_DATA') + '/user/0']
            DOWNLOADS_PATH = [filetools.join(ANDROID_STORAGE, 'emulated/0/Download')]
            
            commands = [['pm', 'list', 'packages'], ['pm', 'list packages']]
            try:
                for command in commands:
                    try:
                        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        PM_LIST, error_cmd = p.communicate()
                        if not error_cmd:
                            break
                    except Exception:
                        continue
                if not PM_LIST: raise
                
                if PY3 and isinstance(PM_LIST, bytes):
                    PM_LIST = PM_LIST.decode()
                PM_LIST = PM_LIST.replace('\n', ', ')
            except Exception:
                logger.error(command)
                if config.is_rooted(silent=True) == 'rooted':
                    commands = [['su', '-c', 'pm list packages'], ['su', '-c', 'pm',  'list', 'packages'], \
                                ['su', '-0', 'pm list packages'], ['su', '-0', 'pm',  'list', 'packages']]
                    for command in commands:
                        try:
                            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            PM_LIST, error_cmd = p.communicate()
                            if not error_cmd:
                                break
                        except Exception as e:
                            if not PY3:
                                e = unicode(str(e), "utf8", errors="replace").encode("utf8")
                            elif PY3 and isinstance(e, bytes):
                                e = e.decode("utf8")
                            logger.info('Command ERROR: %s, %s' % (str(command), str(e)), force=True)
                            continue
                    
                    if PY3 and isinstance(PM_LIST, bytes):
                        PM_LIST = PM_LIST.decode()
                    PM_LIST = PM_LIST.replace('\n', ', ')
                
            #logger.info('PACKAGE LIST: %s' % PM_LIST, force=True)

            PREF_PATHS = [ANDROID_STORAGE + '/emulated/0/Android/data']
            PREF_PATHS += [os.getenv('ANDROID_DATA') + '/user/0']
        
        elif PLATAFORMA in ['windows', 'xbox']:
            exePath = {
                       "chrome": [['%PATH%\\Google\\Chrome\\Application\\chrome.exe'], 
                                  0x00000008, 'LOCALAPPDATA', [], ['\\Google\\Chrome\\User Data\\Default\\Preferences']], 
                       "chromium": [[os.getenv('LOCALAPPDATA') + '\\Chromium\\Application\\chrome.exe'], 
                                    0x00000008, 'LOCALAPPDATA', [], ['\\Chromium\\User Data\\Default\\Preferences']], 
                       "firefox": [['%PATH%\\Mozilla Firefox\\firefox.exe'], 
                                   0x00000008, 'APPDATA', ['\\Mozilla\\Firefox\\installs.ini'], ['prefs.js']],
                       "opera": [[os.getenv('LOCALAPPDATA') + '\\Programs\\Opera\\launcher.exe'], 
                                 0x00000008, 'APPDATA', [], ['\\Opera Software\\Opera Stable\\Preferences']]
                      }
                      
            PATHS = [os.getenv('PROGRAMFILES')]
            PATHS += [os.getenv('PROGRAMFILES(X86)')]
            if not PATHS:
                PATHS = ['C:\\Program Files', 'C:\\Program Files (x86)']
            DOWNLOADS_PATH = [filetools.join(os.getenv('SYSTEMDRIVE'), os.getenv('HOMEPATH'), 'Downloads'), \
                                'D:\\Downloads', 'D:\\Mis documentos\\Downloads']
                
            PREF_PATHS = [os.getenv('LOCALAPPDATA')]
            PREF_PATHS += [os.getenv('APPDATA')]

        elif PLATAFORMA in ['osx', 'ios', 'tvos', 'darwin']:
            exePath = {
                       "chrome": [['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 
                                   '/Applications/Google Chrome.app/AppData/AppHome'], 
                                  0, 'HOME', [], ['Library/Application Support/Google/Chrome/Default/Preferences']], 
                       "chromium": [['/Applications/Chromium.app/Contents/MacOS/Chromium', 
                                     '/Applications/Chromium.app/AppData/AppHome'], 
                                    0, 'HOME', [], ['Library/Application Support/Chromium/Default/Preferences']], 
                       "firefox": [['/Applications/Firefox.app/Contents/MacOS/firefox', 
                                    '/Applications/Firefox.app/AppData/AppHome'], 
                                   0, 'HOME', ['Library/Application Support/Firefox/installs.ini'], ['prefs.js']],
                       "opera": [['/Applications/Opera.app/Contents/MacOS/opera', 
                                  '/Applications/Opera.app/AppData/AppHome'], 
                                 0, 'HOME', [], ['/Library/Application Support/com.operasoftware.Opera/Preferences']]
                      }
            
            PATHS = ['/Applications']
            DOWNLOADS_PATH = [filetools.join(os.getenv('HOME'), 'Descargas'), filetools.join(os.getenv('HOME'), 'Downloads')]
            
            PREF_PATHS = [filetools.join(os.getenv('HOME'), '/Library/Application Support')]
            
        elif PLATAFORMA in ['raspberry']:
            exePath = {
                       "chrome": [['%PATH%/google-chrome', '%PATH%/google-chrome-stable'], 
                                  0, 'HOME', [], ['.config/google-chrome/Default/Preferences', 
                                  '.config/google-chrome-stable/Default/Preferences', 
                                  'snap/google-chrome/current/.config/google-chrome/Default/Preferences']],
                       "opera": [['%PATH%/opera'], 
                                 0, 'HOME', [], ['.config/opera/Preferences', 
                                 'snap/opera/current/.config/opera/Preferences']], 
                       "firefox": [['%PATH%/firefox'], 
                                   0, 'HOME', ['.mozilla/firefox/installs.ini', 
                                   'snap/mozilla/current/.mozilla/firefox/installs.ini'], ['prefs.js']], 
                       "chromium": [['%PATH%/chromium', '%PATH%/chromium-browser'], 
                                    0, 'HOME', [], ['.config/chromium/Default/Preferences', 
                                    'snap/chromium/current/.config/chromium/Default/Preferences']]
                      }
            
            PATHS = ['/usr/bin', '/usr/local/bin', '/usr/sbin', '/usr/local/sbin']
            xpaths = os.getenv('PATH').split(':')
            if xpaths:
                for xpath in xpaths:
                    if xpath not in PATHS:
                        PATHS += [xpath]
            DOWNLOADS_PATH = [filetools.join(os.getenv('HOME'), 'Descargas'), 
                              filetools.join(os.getenv('HOME'), 'descargas'), 
                              filetools.join(os.getenv('HOME'), 'Downloads'), 
                              filetools.join(os.getenv('HOME'), 'downloads')]
            
            PREF_PATHS = [os.getenv('HOME')]
            PREF_PATHS += [filetools.join(os.getenv('HOME'), '.config')]
            PREF_PATHS += [filetools.join(os.getenv('HOME'), 'snap')]
        
        elif PLATAFORMA in ['linux']:
            exePath = {
                       "chrome": [['%PATH%/google-chrome', '%PATH%/google-chrome-stable'], 
                                  0, 'HOME', [], ['.config/google-chrome/Default/Preferences', 
                                  '.config/google-chrome-stable/Default/Preferences', 
                                  'snap/google-chrome/current/.config/google-chrome/Default/Preferences']], 
                       "chromium": [['%PATH%/chromium', '%PATH%/chromium-browser'], 
                                    0, 'HOME', [], ['.config/chromium/Default/Preferences', 
                                    'snap/chromium/current/.config/chromium/Default/Preferences']],
                       "opera": [['%PATH%/opera'], 
                                 0, 'HOME', [], ['.config/opera/Preferences', 
                                 'snap/opera/current/.config/opera/Preferences']], 
                       "firefox": [['%PATH%/firefox'], 
                                   0, 'HOME', ['.mozilla/firefox/installs.ini', 
                                   'snap/mozilla/current/.mozilla/firefox/installs.ini'], ['prefs.js']]
                      }
            
            PATHS = ['/usr/bin', '/usr/local/bin', '/usr/sbin', '/usr/local/sbin']
            xpaths = os.getenv('PATH').split(':')
            if xpaths:
                for xpath in xpaths:
                    if xpath not in PATHS:
                        PATHS += [xpath]
            DOWNLOADS_PATH = [filetools.join(os.getenv('HOME'), 'Descargas'), 
                            filetools.join(os.getenv('HOME'), 'descargas'), 
                            filetools.join(os.getenv('HOME'), 'Downloads'), 
                            filetools.join(os.getenv('HOME'), 'downloads')]
            
            PREF_PATHS = [os.getenv('HOME')]
            PREF_PATHS += [filetools.join(os.getenv('HOME'), '.config')]
            PREF_PATHS += [filetools.join(os.getenv('HOME'), 'snap')]

        else:
            return (False, False)
            
        # Añadimos PATHS adicionales para listar carpetas de Preferencias
        for browser, paths in list(exePath.items()):
            for path in paths[4]:
                if filetools.dirname(path):
                    PREF_PATHS += [filetools.join(os.getenv(paths[2]), filetools.dirname(path))]
            for path in paths[3]:
                if filetools.dirname(path):
                    PREF_PATHS += [filetools.join(os.getenv(paths[2]), filetools.dirname(path))]

        
        # Buscamos si está instalado un browser soportado
        for browser, paths in list(exePath.items()):
            for path in paths[0]:
                #if browser != 'chromium': continue
                if path.startswith('%PATH%'):
                    for PATH in PATHS:
                        if PATH:
                            xpath = path.replace('%PATH%', PATH)
                            if filetools.exists(xpath):
                                path = xpath
                                break
                    else:
                        if PM_LIST and filetools.basename(xpath) in PM_LIST:
                            path = xpath
                            break
                        continue

                # Se comprueba que los paths de ejecución existen.  En el caso de Android se comprueban los paths de configuración en sdcard
                if filetools.basename(path) in PM_LIST or filetools.exists(path):
                    creationFlags = paths[1]
                    try:
                        prefs_file = os.getenv(paths[2])
                        if not prefs_file and PLATAFORMA in ['android', 'atv2']:
                            prefs_file = '/data'
                    except Exception:
                        if PLATAFORMA in ['android', 'atv2']:
                            prefs_file = '/data'
                    break
            else:
                continue
            
            browsers.append((browser, path))
            logger.info('BROWSER: %s, PATH: %s, PREFS_FILE: %s, LOOKUP: %s, STRICIT: %s, DOWNLOAD_PATH: %s, SAVED_D_PATH: %s' % \
                                (browser, path, prefs_file, lookup, strict, download_path, SAVED_D_PATH), force=True)
            # Cuando se necesita conocer el path de Downloads
            if lookup or download_path:
                res = True
                if not prefs_file:
                    return (browser.capitalize(), res)
                
                # Buscamos el path correcto para obtener el archivo de preferencias
                if paths[3]:
                    for prefs_path in paths[3]:
                        if filetools.exists(filetools.join(prefs_file, prefs_path)):
                            break
                else:
                    for prefs_path in paths[4]:
                        if filetools.exists(filetools.join(prefs_file, prefs_path)):
                            break
                
                # Opción especial para Firefox
                if browser_params[browser][2]:
                    installs = filetools.join(prefs_file, prefs_path)
                    scraper = browser_params[browser][2]
                    if PLATAFORMA in ['android', 'atv2']:
                        scraper = scraper.replace('Default', 'Path')
                    profile = scrapertools.find_single_match(filetools.read(installs, silent=True), scraper)
                    prefs_file = filetools.join(prefs_file, filetools.dirname(prefs_path), profile)
                    prefs_path = paths[4][0]
                
                # Accedemos al archivo de las preferencias del browser.  
                prefs_file = filetools.join(prefs_file, prefs_path)
                browser_prefs = filetools.read(prefs_file, silent=True)
                res = scrapertools.find_single_match(browser_prefs, browser_params[browser][3]).replace('\\\\', '\\')
                if not res and browser_prefs:
                    logger.debug('Archivo de Preferencias sin PARÁMETRO %s: %s' % (prefs_file, str(browser_params[browser][3])))
                elif not res:
                    logger.error('Archivo de preferencias no encontrado/accesible: %s' % (prefs_file))
                    for prefs_dir in PREF_PATHS:
                        logger.debug('Listado de %s - %s' % (prefs_dir, sorted(filetools.listdir(prefs_dir))))

                # En Android puede haber problemas de permisos.  Si no se encuentra el path, se asume un path por defecto
                if SAVED_D_PATH and not filetools.exists(SAVED_D_PATH):
                    logger.debug('Path de DESCARGAS almacenado NO EXISTE.  Reseteado: %s' % SAVED_D_PATH)
                    SAVED_D_PATH = ''
                    config.set_setting("capture_thru_browser_path", SAVED_D_PATH, server="torrent")
                if not res and not download_path and not SAVED_D_PATH:
                    for folder in DOWNLOADS_PATH:
                        if filetools.exists(folder):
                            res = folder
                            logger.debug('Path de DESCARGAS por defecto: %s' % (folder))
                            break

                # Si se ha pasado la opción de download_path y difiere del path obtenido, se pasa a otro browser
                if download_path and download_path.lower() != res.lower():
                    logger.info('Paths de DESCARGA DIFERENTES: download_PATH: %s - RES: %s' % (download_path, res), force=True)
                    continue
                # Si no se ha obtenido el path y se ha pedido la opción strict, se pasa a otro browser
                if not res and strict:
                    continue
                # Si no se ha obtenido el path y no hay ninguno guardado, se notifica
                if not res and not SAVED_D_PATH:
                    res = None
                # Si no se ha obtenido el path pero hay uno guardado, se notifica
                elif not res and SAVED_D_PATH:
                    res = True
                else:
                    break
            
            else:
                # Se ha encontrado un browser aceptable.  Se llama al browser
                break
                
        else:
            if browsers:
                browser = browsers[0][0]
                path = browsers[0][1]
                # Si hay browser(s) pero no hay res pero se ha suministrado un download path, y existe, se usa éste último con el primer browser
                if not strict and not res and (download_path or SAVED_D_PATH):
                    if download_path and filetools.exists(download_path):
                        res = download_path
                        logger.info('No RES. Se toma Path de entrada: download_path: %s' % download_path, force=True)
                    elif SAVED_D_PATH and filetools.exists(SAVED_D_PATH):
                        res = SAVED_D_PATH
                        logger.info('No RES. Se toma Path Almacenado: SAVED_D_PATH: %s' % SAVED_D_PATH, force=True)
                elif strict and not res and (download_path or SAVED_D_PATH):
                    logger.info('Browser no encontrado en mod STRICT.  Disponible: %s' % browser.capitalize(), force=True)
                    return (False, False)

            else:
                # Si no se ha encontrado ningún browser que cumpla las condiciones, se vuelve con error
                logger.error('No se ha encontrado ningún BROWSER: %s' % str(exePath))
                if PM_LIST: logger.debug('PACKAGE LIST: %s' % PM_LIST)
                logger.debug('Listado de APPS INSTALADAS en %s: %s' % (PATHS[0], sorted(filetools.listdir(PATHS[0]))))
                if len(PATHS) > 1:
                    logger.debug('Listado de APPS INSTALADAS en %s: %s' % (PATHS[1], sorted(filetools.listdir(PATHS[1]))))
                for prefs_dir in PREF_PATHS:
                    logger.debug('Listado de %s - %s' % (prefs_dir, sorted(filetools.listdir(prefs_dir))))
                return (False, False)
        
        if lookup:
            logger.info('LOOKUP: Selección BROWSER: %s, RES: %s' % (browser, res), force=True)
            return (browser.capitalize(), res)
        
        
        # Ahora hacemos la Call al Browser detectado
        # Si la plataforma es Android, se llama de una forma diferente.
        if PLATAFORMA in ['android', 'atv2']:
            cmd = "StartAndroidActivity(%s,%s,%s,%s)" % (filetools.basename(path), intent, dataType, url)
            logger.info('Android Browser call: %s' % cmd, force=True)
            xbmc.executebuiltin(cmd)
        
        else:
            # Se crea una página .html intermedia con los parámetros necesarios para que funcione la llamada al browser
            if browser == 'chromium':
                browser_call = url
            else:
                browser_call = filetools.join(config.get_data_path(), 'browser_call.html')
                filetools.write(browser_call, browser_params[browser][0])

            params = [path]
            # Se añaden las opciones de llamada del browser seleccionado
            for option in browser_params[browser][1]:
                params += [option]
            params += [browser_call]
            
            try:
                # Se crea un subproceso con la llama al browser
                if PLATAFORMA in ['windows', 'xbox']:
                    s = subprocess.Popen(params, shell=False, creationflags=creationFlags, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    s = subprocess.Popen(params, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                res = s
                
                # Si se ha pedido esperar hasta que termine el browser...
                if wait:
                    output_cmd, error_cmd = s.communicate()
                    if error_cmd: res = False
                    logger.error('Error "%s" en Browser %s, Comando %s' % (str(error_cmd), browser, str(params)))
            except Exception:
                res = False
                logger.error('Error "%s" en Browser %s, Comando %s' % (str(error_cmd), browser, str(params)))

    except Exception:
        logger.error(traceback.format_exc())
        return (False, False)
    
    return (browser.capitalize(), res)


def rec(site_key, co, sa, loc):
    from core import httptools
    
    api_url = "https://www.google.com/recaptcha/api.js"
    headers = {
               "User-Agent": httptools.get_user_agent(),
               "Referer": loc,
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Language": "ro-RO,ro;q=0.8,en-US;q=0.6,en-GB;q=0.4,en;q=0.2"
               }

    r_data = httptools.downloadpage(api_url, headers=headers, follow_redirects=False, alfa_s=True).data
    v = scrapertools.find_single_match(r_data, "releases/([^/]+)")
    cb = "123456789"
    base_url = "https://www.google.com/recaptcha/api2/anchor?ar=1&k=%s&co=%s&hl=ro&v=%s&size=invisible&cb%s" % (site_key, co, v, cb)

    r_data = httptools.downloadpage(base_url, headers=headers, follow_redirects=False, alfa_s=True).data
    c = scrapertools.find_single_match(r_data, 'id="recaptcha-token" value="([^"]+)"')

    t_url = "https://www.google.com/recaptcha/api2/reload?k=%s" % site_key

    post = {"v": v, "reason": "q", "k": site_key, "c": c, "sa": sa, "co": co}
    p = "v=%s&reason=q&k=%s&c=%s&sa=%s&co=%s" % (v, site_key, c, sa, co)
    head = {
            "Accept": "*/*'",
            "Accept-Language": "ro-RO,ro;q=0.8,en-US;q=0.6,en-GB;q=0.4,en;q=0.2",
            "Accept-Encoding": "deflate",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Content-Length": "%s" % len(p),
            "Connection": "keep-alive",
            "referer": base_url
            }

    r_data = httptools.downloadpage(t_url, headers=head, follow_redirects=False, post=post, alfa_s=True).data
    response = scrapertools.find_single_match(r_data, '"rresp","([^"]+)"')
    return response
