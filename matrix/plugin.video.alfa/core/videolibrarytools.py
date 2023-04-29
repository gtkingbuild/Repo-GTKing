# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Common Library Tools
# ------------------------------------------------------------

#from builtins import str
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import errno
import math
import traceback
import re
import time

from core import filetools, scraper, scrapertools
from core.item import Item
from platformcode import config, logger, platformtools
from lib import generictools

FOLDER_MOVIES = config.get_setting("folder_movies")
FOLDER_TVSHOWS = config.get_setting("folder_tvshows")
VIDEOLIBRARY_PATH = config.get_videolibrary_path()
MOVIES_PATH = filetools.join(VIDEOLIBRARY_PATH, FOLDER_MOVIES)
TVSHOWS_PATH = filetools.join(VIDEOLIBRARY_PATH, FOLDER_TVSHOWS)
NFO_FORMAT = 'url_scraper'      # 'url_scraper' o 'xml'
DEBUG = config.get_setting('debug_report', default=False)
magnet_caching = config.get_setting("magnet2torrent", server='torrent', default=False)

if not FOLDER_MOVIES or not FOLDER_TVSHOWS or not VIDEOLIBRARY_PATH \
        or not filetools.exists(MOVIES_PATH) or not filetools.exists(TVSHOWS_PATH):
    config.verify_directories_created()

addon_name = "plugin://plugin.video.%s/" % config.PLUGIN_NAME


def get_content_channels(item):
    """
    Obtiene los canales de videolibrary asociados a un item y sus urls
    Las funciones findvideos devuelven una lista con ['nombre_canal', 'http://url.de/contenido/en-canal']
    Las demás funciones solo devuelven una lista con ['nombre_canal']
    @param item: item de videoteca (item.channel == 'videolibrary')
    @type item: item

    @return: lista con canales disponibles para el item en videoteca
    @rtype: list
    """
    if item.library_urls:
        library_urls = []
        for channel, url in item.library_urls.items():
            if not 'downloads' in channel:
                library_urls.append([channel, url])
        return library_urls
    else:
        canales = []
        list_canales = []
        content_title = "".join(c for c in item.contentTitle.strip().lower() if c not in ":*?<>|\\/")

        if item.contentType == 'movie':
            item.strm_path = filetools.join(MOVIES_PATH, item.strm_path)
            path_dir = filetools.dirname(item.strm_path)
            item.nfo = filetools.join(path_dir, filetools.basename(path_dir) + ".nfo")
        else:
            item.strm_path = filetools.join(TVSHOWS_PATH, item.strm_path)
            path_dir = filetools.dirname(item.strm_path)
            item.nfo = filetools.join(path_dir, 'tvshow.nfo')

        from core import jsontools
        for fd in filetools.listdir(path_dir):
            if fd.endswith('.json'):
                contenido, channel_name = fd[:-6].split('[')
                if (contenido.startswith(content_title) or item.contentType == 'movie') and \
                        channel_name not in canales and channel_name != 'downloads':
                    jsonpath = filetools.join(path_dir, fd)
                    jsonitem = Item().fromjson(filetools.read(jsonpath))
                    canales.append(channel_name)
                    list_canales.append([channel_name, '{}'.format(jsonitem.url)])
                    logger.info(jsonpath)
                    logger.info(channel_name)
                    logger.info(jsonitem)
        
        return list_canales


def read_nfo(path_nfo, item=None):
    """
    Metodo para leer archivos nfo.
        Los arcivos nfo tienen la siguiente extructura: url_scraper | xml + item_json
        [url_scraper] y [xml] son opcionales, pero solo uno de ellos ha de existir siempre.
    @param path_nfo: ruta absoluta al archivo nfo
    @type path_nfo: str
    @param item: Si se pasa este parametro el item devuelto sera una copia de este con
        los valores de 'infoLabels', 'library_playcounts' y 'path' leidos del nfo
    @type: Item
    @return: Una tupla formada por la cabecera (head_nfo ='url_scraper'|'xml') y el objeto 'item_json'
    @rtype: tuple (str, Item)
    """
    head_nfo = ""
    it = Item()

    data = filetools.read(path_nfo)
    if data and data.endswith('-->'): data = data[:-4]      # Si el json forma parte de un comentario de una xml, se quita la cola

    if data:
        head_nfo = data.splitlines()[0] + "\n"
        data = "\n".join(data.splitlines()[1:])

        it_nfo = Item().fromjson(data)

        if item:
            it = item.clone()
            it.infoLabels = it_nfo.infoLabels
            if 'library_playcounts' in it_nfo:
                it.library_playcounts = it_nfo.library_playcounts
            if it_nfo.path:
                it.path = it_nfo.path
        else:
            it = it_nfo

        if 'fanart' in it.infoLabels:
            it.fanart = it.infoLabels['fanart']
            
        # Si hay cambio de formato del .nfo se realiza una conversión silenciosa al nuevo formato
        if NFO_FORMAT == 'xml' and not head_nfo.startswith('<?xml'):
            res = write_nfo(path_nfo, head_nfo, it)
        elif NFO_FORMAT == 'url_scraper' and head_nfo.startswith('<?xml'):
            logger.info(head_nfo, force=True)
            head_nfo = scraper.get_nfo(it, nfo_format=NFO_FORMAT)
            res = write_nfo(path_nfo, head_nfo, it)

    return head_nfo, it


def write_nfo(path_nfo, head_nfo=None, item=None, nfo_format=NFO_FORMAT):
    """
    Metodo para escribir archivos nfo.
        Los arcivos nfo tienen la siguiente extructura: url_scraper | xml + item_json
        [url_scraper] y [xml] son opcionales, pero solo uno de ellos ha de existir siempre.
    @param path_nfo: ruta absoluta al archivo nfo
    @type path_nfo: str
    @param head_nfo:'url_scraper'|'xml'
    @type: str
    @param item: json a guardar
    @type: Item
    @return: resultado de la operación: True|False
    @rtype: Bool
    """
    res = False
    tail_nfo = ''
    
    if not path_nfo or not head_nfo or not item:
        logger.error('Algún campo está vacío: path_nfo=%s; head_nfo=%s; item=%s' % (path_nfo, head_nfo, item))
        return res
        
    if nfo_format == 'xml':
        if not head_nfo.startswith('<?xml'):
            logger.info(head_nfo, force=True)
            head_nfo = scraper.get_nfo(item, nfo_format=nfo_format)
        if not head_nfo.endswith('<!--\n'):
            head_nfo = head_nfo[:-1] + '<!--\n'
        tail_nfo = '\n-->'
    
    res = filetools.write(path_nfo, head_nfo + item.tojson() + tail_nfo)
    if not res:
        logger.error('Error de escritura en %s; head_nfo: %s; tail_nfo=%s; item=%s' % (path_nfo, head_nfo, tail_nfo, item))

    return res


def save_movie(item, silent=False):
    """
    guarda en la libreria de peliculas el elemento item, con los valores que contiene.
    @type item: item
    @param item: elemento que se va a guardar.
    @rtype insertados: int
    @return:  el número de elementos insertados
    @rtype sobreescritos: int
    @return:  el número de elementos sobreescritos
    @rtype fallidos: int
    @return:  el número de elementos fallidos o -1 si ha fallado todo
    """
    logger.info()
    # logger.debug(item.tostring('\n'))
    insertados = 0
    sobreescritos = 0
    fallidos = 0
    path = ""
    # Quitamos la etiqueta de Filtertools
    if 'filtertools' in item: del item.filtertools

    # Itentamos obtener el titulo correcto:
    # 1. contentTitle: Este deberia ser el sitio correcto, ya que title suele contener "Añadir a la videoteca..."
    # 2. title
    if not item.contentTitle:
        # Colocamos el titulo correcto en su sitio para que scraper lo localize
        item.contentTitle = item.title

    # Si llegados a este punto no tenemos titulo, salimos
    if not item.contentTitle or not item.channel:
        logger.debug("NO ENCONTRADO contentTitle")
        return 0, 0, -1  # Salimos sin guardar

    scraper_return = scraper.find_and_set_infoLabels(item)

    # Llegados a este punto podemos tener:
    #  scraper_return = True: Un item con infoLabels con la información actualizada de la peli
    #  scraper_return = False: Un item sin información de la peli (se ha dado a cancelar en la ventana)
    #  item.infoLabels['code'] == "" : No se ha encontrado el identificador de IMDB necesario para continuar, salimos
    if not scraper_return or not item.infoLabels['code']:
        # TODO de momento si no hay resultado no añadimos nada,
        # aunq podriamos abrir un cuadro para introducir el identificador/nombre a mano
        logger.debug("NO ENCONTRADO EN SCRAPER O NO TIENE code")
        return 0, 0, -1

    _id = item.infoLabels['code'][0]

    # progress dialog
    if not silent: p_dialog = platformtools.dialog_progress(config.get_localized_string(20000), config.get_localized_string(60062))

    if config.get_setting("original_title_folder", "videolibrary") == 1 and item.infoLabels['originaltitle']:
        base_name = item.infoLabels['originaltitle']
    else:
        base_name = item.contentTitle

    if not PY3:
        base_name = unicode(filetools.validate_path(base_name.replace('/', '-')), "utf8").encode("utf8")
    else:
        base_name = filetools.validate_path(base_name.replace('/', '-'))

    if config.get_setting("lowerize_title", "videolibrary") == 0:
        base_name = base_name.lower()

    for raiz, subcarpetas, ficheros in filetools.walk(MOVIES_PATH):
        for c in subcarpetas:
            code = scrapertools.find_single_match(c, '\[(.*?)\]')
            if code and code in item.infoLabels['code']:
                path = filetools.join(raiz, c)
                _id = code
                break

    if not path:
        # Crear carpeta
        path = filetools.join(MOVIES_PATH, ("%s [%s]" % (base_name, _id)).strip())
        logger.info("Creando directorio pelicula:" + path)
        if not filetools.mkdir(path):
            logger.debug("No se ha podido crear el directorio")
            return 0, 0, -1

    nfo_path = filetools.join(path, "%s [%s].nfo" % (base_name, _id))
    strm_path = filetools.join(path, "%s.strm" % base_name)
    json_path = filetools.join(path, ("%s [%s].json" % (base_name, item.channel.lower())))

    nfo_exists = filetools.exists(nfo_path)
    strm_exists = filetools.exists(strm_path)
    json_exists = filetools.exists(json_path)

    if nfo_exists:
        # Si existe .nfo, pero estamos añadiendo un nuevo canal lo abrimos
        head_nfo, item_nfo = read_nfo(nfo_path)
        if not item_nfo.channel:
            logger.error('.nfo corrupto. Regenerando %s' % nfo_path)
            if not filetools.remove(nfo_path):              # .nfo corrupto.  Lo borramos para regenerarlo
                return 0, 0, -1, path                       # Problema con el filesystem?
            nfo_exists = False

    if not nfo_exists:
        # Creamos .nfo si no existe
        logger.info("Creando .nfo: " + nfo_path)
        head_nfo = scraper.get_nfo(item, nfo_format=NFO_FORMAT)

        item_nfo = Item(title=item.contentTitle, channel="videolibrary", action='findvideos',
                        library_playcounts={"%s [%s]" % (base_name, _id): 0}, infoLabels=item.infoLabels,
                        library_urls={})

    if not strm_exists:
        # Crear base_name.strm si no existe
        item_strm = Item(channel='videolibrary', action='play_from_library',
                         strm_path=strm_path.replace(MOVIES_PATH, ""), contentType='movie',
                         contentTitle=item.contentTitle)
        strm_exists = filetools.write(strm_path, '%s?%s' % (addon_name, item_strm.tourl()))
        item_nfo.strm_path = strm_path.replace(MOVIES_PATH, "")

    # Solo si existen item_nfo y .strm continuamos
    if item_nfo and strm_exists:

        if json_exists:
            logger.info("El fichero existe. Se sobreescribe")
            sobreescritos += 1
        else:
            insertados += 1

        # Si se ha marcado la opción de url de emergencia, se añade ésta a la película después de haber ejecutado Findvideos del canal
        try:
            headers = {}
            if item.headers:
                headers = item.headers
            channel = generictools.verify_channel(item.channel)
            if config.get_setting("emergency_urls", channel) in [1, 3]:
                item = emergency_urls(item, None, json_path, headers=headers)
                if item_nfo.emergency_urls and not isinstance(item_nfo.emergency_urls, dict):
                    del item_nfo.emergency_urls
                if not item_nfo.emergency_urls:
                    item_nfo.emergency_urls = dict()
                item_nfo.emergency_urls.update({item.channel: True})
        except:
            logger.error("No se ha podido guardar las urls de emergencia de %s en la videoteca" % item.contentTitle)
            logger.error(traceback.format_exc())
        
        if item.from_channel_alt: del item.from_channel_alt
        if item_nfo.from_channel_alt: del item_nfo.from_channel_alt
        if filetools.write(json_path, item.tojson()):
            if not silent: p_dialog.update(100, 'Añadiendo película...' + '\n' + item.contentTitle + '\n' + ' ')
            item_nfo.library_urls[item.channel] = item.url

            if write_nfo(nfo_path, head_nfo, item_nfo):
                # actualizamos la videoteca de Kodi con la pelicula
                if config.is_xbmc() and not silent:
                    from platformcode import xbmc_videolibrary
                    xbmc_videolibrary.update(FOLDER_MOVIES, '_scan_series')
                # Si el usuario quiere un backup de la película (local o remoto), se toma la dirección/direcciones de destino y se copia
                videolibrary_backup =  config.get_setting('videolibrary_backup', channel='videolibrary')
                if videolibrary_backup:
                    try:
                        import threading
                        threading.Thread(target=videolibrary_backup_exec, args=(item_nfo, videolibrary_backup)).start()
                    except:
                        logger.error('Error en el backup de la película %s' % item_nfo.strm_path)
                        logger.error(traceback.format_exc(1))

                if not silent: p_dialog.close()
                return insertados, sobreescritos, fallidos

    # Si llegamos a este punto es por q algo ha fallado
    logger.error("No se ha podido guardar %s en la videoteca" % item.contentTitle)
    if not silent: p_dialog.update(100, config.get_localized_string(60063) + '\n' + item.contentTitle + '\n' + ' ')
    if not silent: p_dialog.close()
    return 0, 0, -1


def save_tvshow(item, episodelist, silent=False, overwrite=True, monitor=None):
    """
    guarda en la libreria de series la serie con todos los capitulos incluidos en la lista episodelist
    @type item: item
    @param item: item que representa la serie a guardar
    @type episodelist: list
    @param episodelist: listado de items que representan los episodios que se van a guardar.
    @rtype insertados: int
    @return:  el número de episodios insertados
    @rtype sobreescritos: int
    @return:  el número de episodios sobreescritos
    @rtype fallidos: int
    @return:  el número de episodios fallidos o -1 si ha fallado toda la serie
    @rtype path: str
    @return:  directorio serie
    """
    logger.info()
    # logger.debug(item.tostring('\n'))
    path = ""
    # Quitamos la etiqueta de Filtertools
    if 'filtertools' in item: del item.filtertools
    
    if not monitor and config.is_xbmc():
        import xbmc
        if config.get_platform(True)['num_version'] >= 14:
            monitor = xbmc.Monitor()  # For Kodi >= 14

    # Si llegados a este punto no tenemos titulo o code, salimos
    if not (item.contentSerieName or item.infoLabels['code']) or not item.channel:
        logger.error("NO ENCONTRADO contentSerieName NI code: " + item.url)
        return 0, 0, -1, path  # Salimos sin guardar

    scraper_return = scraper.find_and_set_infoLabels(item)
    # Llegados a este punto podemos tener:
    #  scraper_return = True: Un item con infoLabels con la información actualizada de la serie
    #  scraper_return = False: Un item sin información de la peli (se ha dado a cancelar en la ventana)
    #  item.infoLabels['code'] == "" : No se ha encontrado el identificador de IMDB necesario para continuar, salimos
    if not scraper_return or not item.infoLabels['code']:
        # TODO de momento si no hay resultado no añadimos nada,
        # aunq podriamos abrir un cuadro para introducir el identificador/nombre a mano
        logger.error("NO ENCONTRADO EN SCRAPER O NO TIENE code: " + item.url)
        return 0, 0, -1, path

    _id = item.infoLabels['code'][0]
    if not item.infoLabels['code'][0] or item.infoLabels['code'][0] == 'None': 
        if item.infoLabels['code'][1] and item.infoLabels['code'][1] != 'None':
            _id = item.infoLabels['code'][1]
        elif item.infoLabels['code'][2] and item.infoLabels['code'][2] != 'None':
            _id = item.infoLabels['code'][2]
        else:
            logger.error("NO ENCONTRADO EN SCRAPER O NO TIENE code: " + item.url 
                        + ' / ' + item.infoLabels['code'])
            return 0, 0, -1, path

    if config.get_setting("original_title_folder", "videolibrary") == 1 and item.infoLabels['originaltitle']:
        base_name = item.infoLabels['originaltitle']
    elif item.infoLabels['tvshowtitle']:
        base_name = item.infoLabels['tvshowtitle']
    elif item.infoLabels['title']:
        base_name = item.infoLabels['title']
    else:
        base_name = item.contentSerieName

    if not PY3:
        base_name = unicode(filetools.validate_path(base_name.replace('/', '-')), "utf8").encode("utf8")
    else:
        base_name = filetools.validate_path(base_name.replace('/', '-'))

    if config.get_setting("lowerize_title", "videolibrary") == 0:
        base_name = base_name.lower()

    for raiz, subcarpetas, ficheros in filetools.walk(TVSHOWS_PATH):
        for c in subcarpetas:
            code = scrapertools.find_single_match(c, '\[(.*?)\]')
            if code and code != 'None' and code in item.infoLabels['code']:
                path = filetools.join(raiz, c)
                _id = code
                break

    if not path:
        path = filetools.join(TVSHOWS_PATH, ("%s [%s]" % (base_name, _id)).strip())
        logger.info("Creando directorio serie: " + path)
        try:
            filetools.mkdir(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    tvshow_path = filetools.join(path, "tvshow.nfo")
    if filetools.exists(tvshow_path):
        # Si existe tvshow.nfo, pero estamos añadiendo un nuevo canal actualizamos el listado de urls
        head_nfo, item_tvshow = read_nfo(tvshow_path)
        if item_tvshow.channel:
            item_tvshow.channel = "videolibrary"
            item_tvshow.action = "get_seasons"
            item_tvshow.library_urls[item.channel] = item.url
        else:
            logger.error('.nfo corrupto. Regenerando %s' % item_tvshow)
            if not filetools.remove(tvshow_path):           # .nfo corrupto.  Lo borramos para regenerarlo
                return 0, 0, -1, path                       # Problema con el filesystem?

    if not filetools.exists(tvshow_path):
        # Creamos tvshow.nfo, si no existe, con la head_nfo, info de la serie y marcas de episodios vistos
        logger.info("Creando tvshow.nfo: " + tvshow_path)
        head_nfo = scraper.get_nfo(item, nfo_format=NFO_FORMAT)
        item.infoLabels['mediatype'] = "tvshow"
        item.infoLabels['title'] = item.contentSerieName
        item_tvshow = Item(title=item.contentSerieName, channel="videolibrary", action="get_seasons",
                           fanart=item.infoLabels['fanart'], thumbnail=item.infoLabels['thumbnail'],
                           infoLabels=item.infoLabels, path=path.replace(TVSHOWS_PATH, ""))
        item_tvshow.library_playcounts = {}
        item_tvshow.library_urls = {item.channel: item.url}
        if item.serie_info: item_tvshow.serie_info = item.serie_info
        if item.season_search: item_tvshow.season_search = item.season_search

    # FILTERTOOLS
    # si el canal tiene filtro de idiomas, añadimos el canal y el show
    if episodelist and "list_language" in episodelist[0]:
        # si ya hemos añadido un canal previamente con filtro, añadimos o actualizamos el canal y show
        if "library_filter_show" in item_tvshow:
            if item.title_from_channel:
                item_tvshow.library_filter_show[item.channel] = item.title_from_channel
            else:
                item_tvshow.library_filter_show[item.channel] = item.show
        # no habia ningún canal con filtro y lo generamos por primera vez
        else:
            if item.title_from_channel:
                item_tvshow.library_filter_show = {item.channel: item.title_from_channel}
            else:
                item_tvshow.library_filter_show = {item.channel: item.show}

    if int(overwrite) == 3 and item_tvshow.active == 0 and (item_tvshow.infoLabels["status"] == "Ended" 
                            or item_tvshow.infoLabels["status"] == "Canceled"):
        item_tvshow.active = 0  # lo dejamos inactivo
    elif item.channel != "downloads":
        item_tvshow.active = 1  # para que se actualice a diario cuando se llame a videolibrary_service

    if not write_nfo(tvshow_path, head_nfo, item_tvshow):
        # Error de escritura del .nfo
        return 0, 0, 0, path

    if not episodelist:
        # La lista de episodios esta vacia
        return 0, 0, 0, path

    # Guardar los episodios
    '''import time
    start_time = time.time()'''
    insertados, sobreescritos, fallidos = save_episodes(path, episodelist, item, silent=silent, overwrite=overwrite, monitor=monitor)
    '''msg = "Insertados: %d | Sobreescritos: %d | Fallidos: %d | Tiempo: %2.2f segundos" % \
          (insertados, sobreescritos, fallidos, time.time() - start_time)
    logger.debug(msg)'''

    return insertados, sobreescritos, fallidos, path


def save_episodes(path, episodelist, serie, silent=False, overwrite=True, monitor=None):
    """
    guarda en la ruta indicada todos los capitulos incluidos en la lista episodelist
    @type path: str
    @param path: ruta donde guardar los episodios
    @type episodelist: list
    @param episodelist: listado de items que representan los episodios que se van a guardar.
    @type serie: item
    @param serie: serie de la que se van a guardar los episodios
    @type silent: bool
    @param silent: establece si se muestra la notificación
    @param overwrite: permite sobreescribir los ficheros existentes
    @type overwrite: bool
    @rtype insertados: int
    @return:  el número de episodios insertados
    @rtype sobreescritos: int
    @return:  el número de episodios sobreescritos
    @rtype fallidos: int
    @return:  el número de episodios fallidos
    """
    logger.info()

    # No hay lista de episodios, no hay nada que guardar
    if not len(episodelist):
        logger.info("No hay lista de episodios, salimos sin crear strm")
        return 0, 0, 0

    insertados = 0
    sobreescritos = 0
    fallidos = 0
    news_in_playcounts = {}
    overwrite_back = overwrite
    if int(overwrite) == 3:
        overwrite = True

    # Listamos todos los ficheros de la serie, asi evitamos tener que comprobar si existe uno por uno
    raiz, carpetas_series, ficheros = next(filetools.walk(path))
    ficheros = [filetools.join(path, f) for f in ficheros]

    nostrm_episodelist = []
    for root, folders, files in filetools.walk(path):
        for file in files:
            season_episode = scrapertools.get_season_and_episode(file)
            if season_episode == "" or filetools.exists(filetools.join(path, "%s.strm" % season_episode)):
                continue
            nostrm_episodelist.append(season_episode)
    nostrm_episodelist = sorted(set(nostrm_episodelist))
    
    # Si solo se quiere al última temporada, averiguamos cuál es y la salvamos
    if config.get_setting('last_season_only', 'videolibrary', default=False) or serie.infoLabels.get('last_season_only', False):
        try:
            #episodelist = sorted(episodelist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))         #clasificamos
            season_last = 0
            episodelist_alt = []
            for e in reversed(episodelist):
                if e.infoLabels.get('season', 0) and e.infoLabels.get('season', 0) >= season_last:
                    season_last = e.infoLabels.get('season', 0)
                    serie.infoLabels['last_season_only'] = True
                    if 'last_season_only' in e.infoLabels:
                        del e.infoLabels['last_season_only']
                    episodelist_alt.append(e)
                elif not e.infoLabels.get('season', 0):
                    continue
                else:
                    break
            if episodelist_alt:
                episodelist = episodelist_alt.copy()
                episodelist = sorted(episodelist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))     #clasificamos
        except:
            logger.error("Error al seleccionar la última temporada %s" % e.contentTitle)
            logger.error(traceback.format_exc())

    # Silent es para no mostrar progreso (para videolibrary_service)
    if not silent:
        # progress dialog
        p_dialog = platformtools.dialog_progress(config.get_localized_string(20000), config.get_localized_string(60064))
        p_dialog.update(0, config.get_localized_string(60065))

    channel_alt = generictools.verify_channel(serie.channel)                    #Preparamos para añadir las urls de emergencia
    emergency_urls_stat = config.get_setting("emergency_urls", channel_alt)     #El canal quiere urls de emergencia?
    emergency_urls_succ = False
    channel = __import__('channels.%s' % channel_alt, fromlist=["channels.%s" % channel_alt])
    if serie.torrent_caching_fail:                                              #Si el proceso de conversión ha fallado, no se cachean
        emergency_urls_stat = 0
        del serie.torrent_caching_fail
    
    new_episodelist = []
    # Obtenemos el numero de temporada y episodio y descartamos los q no lo sean
    tags = []
    if config.get_setting("enable_filter", "videolibrary"):
        tags = [x.strip() for x in config.get_setting("filters", "videolibrary").lower().split(",")]

    for e in episodelist:
        if monitor and monitor.waitForAbort(0.1):
            return 0, 0, -1
        
        headers = {}
        if e.headers:
            headers = e.headers
        if tags != [] and tags != None and any(tag in e.title.lower() for tag in tags):
            continue
        # Quitamos la etiqueta de Filtertools
        if 'filtertools' in e: del e.filtertools

        try:
            # Valor por defecto por si no se provee temporada = 1
            # No podemos darle valor de episodio por defecto
            if e.contentEpisodeNumber and isinstance(e.contentSeason, int):
                season_episode = scrapertools.get_season_and_episode('{}x{}'.format(e.contentSeason, e.contentEpisodeNumber))
            elif scrapertools.find_single_match(e.title.lower(), '(?i)\d+x(\d+)'):
                season_episode = scrapertools.get_season_and_episode(e.title.lower())
            elif e.contentEpisodeNumber:
                season_episode = scrapertools.get_season_and_episode('{}x{}'.format(1, e.contentEpisodeNumber))
            elif scrapertools.find_single_match(e.title.lower(), '(?i)x(\d+)'):
                episode_number = scrapertools.find_single_match(e.title.lower(), '(?i)x(\d+)')
                season_episode = scrapertools.get_season_and_episode('{}x{}'.format(1, episode_number))
            if not season_episode:
                season_episode = scrapertools.get_season_and_episode(e.title.lower())

            if not season_episode or 'temp. a videoteca' in e.title.lower() \
                            or 'serie a videoteca' in e.title.lower() \
                            or 'vista previa videoteca' in e.title.lower():
                continue
        
            # Si se ha marcado la opción de url de emergencia, se añade ésta a cada episodio después de haber ejecutado Findvideos del canal
            if e.emergency_urls and isinstance(e.emergency_urls, dict): del e.emergency_urls    #Borramos trazas anteriores
            json_path = filetools.join(path, ("%s [%s].json" % (season_episode, e.channel)).lower())    #Path del .json del episodio
            if emergency_urls_stat == 1 and not e.emergency_urls and e.contentType == 'episode':     #Guardamos urls de emergencia?
                if not silent:
                    p_dialog.update(0, 'Cacheando enlaces y archivos .torrent...' + '\n' + e.title + '\n' + ' ' + '\n' + ' ')     #progress dialog
                    if p_dialog.iscanceled(): p_dialog.close(); return 0, 0, 0
                if json_path in ficheros:                                   #Si existe el .json sacamos de ahí las urls
                    if overwrite:                                           #pero solo si se se sobrescriben los .json
                        json_epi = Item().fromjson(filetools.read(json_path))                   #Leemos el .json
                        if json_epi.emergency_urls:                         #si existen las urls de emergencia...
                            e.emergency_urls = json_epi.emergency_urls      #... las copiamos
                        else:                                               #y si no...
                            e = emergency_urls(e, channel, json_path, headers=headers)  #... las generamos
                else:
                    e = emergency_urls(e, channel, json_path, headers=headers)  #Si el episodio no existe, generamos las urls
                if e.emergency_urls:                                        #Si ya tenemos urls...
                    emergency_urls_succ = True                              #... es un éxito y vamos a marcar el .nfo
            elif emergency_urls_stat == 2 and e.contentType == 'episode':   #Borramos urls de emergencia?
                if e.emergency_urls: del e.emergency_urls
                emergency_urls_succ = True                                  #... es un éxito y vamos a marcar el .nfo
            elif emergency_urls_stat == 3 and e.contentType == 'episode':   #Actualizamos urls de emergencia?
                if not silent:
                    p_dialog.update(0, 'Cacheando enlaces y archivos .torrent...' + '\n' + e.title + '\n' + ' ' + '\n' + ' ')     #progress dialog
                    if p_dialog.iscanceled(): p_dialog.close(); return 0, 0, 0
                e = emergency_urls(e, channel, json_path, headers=headers)  #generamos las urls
                if e.emergency_urls:                                        #Si ya tenemos urls...
                    emergency_urls_succ = True                              #... es un éxito y vamos a marcar el .nfo
            
            if not e.infoLabels["tmdb_id"] or (serie.infoLabels["tmdb_id"] and e.infoLabels["tmdb_id"] != serie.infoLabels["tmdb_id"]):                                                    #en series multicanal, prevalece el infolabels...
                e.infoLabels = serie.infoLabels                             #... del canal actual y no el del original
            if not (isinstance(e.contentSeason, int) and isinstance(e.contentSeason, int)):
                e.contentSeason, e.contentEpisodeNumber = season_episode.split("x")
            try:
                e.contentSeason = int(e.contentSeason)
                e.contentEpisodeNumber = int(e.contentEpisodeNumber)
            except:
                logger.error('### No se ha podido guardar el episodio "%sx%s" de %s:%s' % 
                             (str(e.contentSeason), str(e.contentEpisodeNumber), e.channel, str(e.contentSerieName)))
                continue
            if e.videolibray_emergency_urls:
                del e.videolibray_emergency_urls
            e.library_playcounts = {}
            del e.library_playcounts
            if e.ow_force:
                del e.ow_force
            if e.video_path:
                del e.video_path
            if e.channel_redir:
                del e.channel_redir                                         #... y se borran las marcas de redirecciones
            new_episodelist.append(e)
        except:
            if e.contentType == 'episode':
                logger.error("No se ha podido guardar las urls de emergencia de %s en la videoteca" % e.contentTitle)
                logger.error(traceback.format_exc())
            continue
            
        if e.from_channel_alt: del e.from_channel_alt
    if serie.from_channel_alt: del serie.from_channel_alt

    # No hay lista de episodios, no hay nada que guardar
    if not len(new_episodelist):
        logger.info("No hay lista de episodios, salimos sin crear strm")
        return 0, 0, 0

    # fix float porque la division se hace mal en python 2.x
    try:
        t = float(100) / len(new_episodelist)
    except:
        t = 0

    last_season_episode = ''
    for i, e in enumerate(scraper.sort_episode_list(new_episodelist)):
        if not silent:
            p_dialog.update(int(math.ceil((i + 1) * t)), config.get_localized_string(60064) + '\n' + e.title + '\n' + ' ' + '\n' + ' ')

        high_sea = e.contentSeason
        high_epi = e.contentEpisodeNumber
        if scrapertools.find_single_match(e.title, '[a|A][l|L]\s*(\d+)'):
            high_epi = int(scrapertools.find_single_match(e.title, 'al\s*(\d+)'))
        max_sea = e.infoLabels["number_of_seasons"]
        max_epi = 0
        if e.infoLabels["number_of_seasons"] and (e.infoLabels["temporada_num_episodios"] or e.infoLabels["number_of_seasons"] == 1):
            if e.infoLabels["number_of_seasons"] == 1 and e.infoLabels["number_of_episodes"]:
                max_epi = e.infoLabels["number_of_episodes"]
            else:
                max_epi = e.infoLabels["temporada_num_episodios"]

        season_episode = "%sx%s" % (e.contentSeason, str(e.contentEpisodeNumber).zfill(2))
        strm_path = filetools.join(path, "%s.strm" % season_episode)
        nfo_path = filetools.join(path, "%s.nfo" % season_episode)
        json_path = filetools.join(path, ("%s [%s].json" % (season_episode, e.channel_redir.lower() or e.channel)).lower())

        if season_episode in nostrm_episodelist:
            logger.error('Error en la estructura de la Videoteca: Serie ' + serie.contentSerieName + ' ' + season_episode)
            continue
        strm_exists = strm_path in ficheros
        nfo_exists = nfo_path in ficheros
        json_exists = json_path in ficheros

        if not strm_exists:
            # Si no existe season_episode.strm añadirlo
            item_strm = Item(action='play_from_library', channel='videolibrary',
                             strm_path=strm_path.replace(TVSHOWS_PATH, ""), infoLabels={})
            item_strm.contentSeason = e.contentSeason
            item_strm.contentEpisodeNumber = e.contentEpisodeNumber
            item_strm.contentType = e.contentType
            item_strm.contentTitle = season_episode

            # FILTERTOOLS
            if item_strm.list_language:
                # si tvshow.nfo tiene filtro se le pasa al item_strm que se va a generar
                if "library_filter_show" in serie:
                    item_strm.library_filter_show = serie.library_filter_show

                if item_strm.library_filter_show == "":
                    logger.error("Se ha producido un error al obtener el nombre de la serie a filtrar")

            # logger.debug("item_strm" + item_strm.tostring('\n'))
            # logger.debug("serie " + serie.tostring('\n'))
            strm_exists = filetools.write(strm_path, '%s?%s' % (addon_name, item_strm.tourl()))

        item_nfo = None
        if not nfo_exists and e.infoLabels["code"]:
            # Si no existe season_episode.nfo añadirlo
            scraper.find_and_set_infoLabels(e)
            head_nfo = scraper.get_nfo(e, nfo_format=NFO_FORMAT)

            item_nfo = e.clone(channel="videolibrary", url="", action='findvideos',
                               strm_path=strm_path.replace(TVSHOWS_PATH, ""))
            if item_nfo.emergency_urls:
                del item_nfo.emergency_urls                     #Solo se mantiene en el .json del episodio

            nfo_exists = write_nfo(nfo_path, head_nfo, item_nfo)

        # Solo si existen season_episode.nfo y season_episode.strm continuamos
        if nfo_exists and strm_exists:
            if not json_exists or overwrite:
                # Obtenemos infoLabel del episodio
                if not item_nfo:
                    head_nfo, item_nfo = read_nfo(nfo_path)
                    if not item_nfo.channel:
                        logger.info("Fallido .nfo: %s" % nfo_path)
                        fallidos += 1
                        continue

                # En series multicanal, prevalece el infolabels del canal actual y no el del original
                if not e.infoLabels["tmdb_id"] or (item_nfo.infoLabels["tmdb_id"] \
                            and e.infoLabels["tmdb_id"] != item_nfo.infoLabels["tmdb_id"]): 
                    e.infoLabels = item_nfo.infoLabels

                if filetools.write(json_path, e.tojson()):
                    if not json_exists:
                        logger.info("Insertado: %s" % json_path)
                        insertados += 1
                        # Marcamos episodio como no visto
                        news_in_playcounts[season_episode] = 0
                        # Marcamos la temporada como no vista
                        news_in_playcounts["season %s" % e.contentSeason] = 0
                        # Marcamos la serie como no vista
                        # logger.debug("serie " + serie.tostring('\n'))
                        news_in_playcounts[serie.contentSerieName] = 0

                    else:
                        logger.info("Sobreescrito: %s" % json_path)
                        sobreescritos += 1
                else:
                    logger.info("Fallido: %s" % json_path)
                    fallidos += 1

        else:
            logger.info("Fallido: %s" % json_path)
            fallidos += 1

        if not silent and p_dialog.iscanceled():
            break

    #logger.debug('high_sea x high_epi: %sx%s' % (str(high_sea), str(high_epi)))
    #logger.debug('max_sea x max_epi: %sx%s' % (str(max_sea), str(max_epi)))
    if not silent:
        p_dialog.close()

    if news_in_playcounts or emergency_urls_succ or serie.infoLabels["status"] == "Ended" or serie.infoLabels["status"] == "Canceled":
        # Si hay nuevos episodios los marcamos como no vistos en tvshow.nfo ...
        tvshow_path = filetools.join(path, "tvshow.nfo")
        try:
            import datetime
            head_nfo, tvshow_item = read_nfo(tvshow_path)
            tvshow_item.library_playcounts.update(news_in_playcounts)
            
            #Si la operación de insertar/borrar urls de emergencia en los .jsons de los episodios ha tenido éxito, se marca el .nfo
            if emergency_urls_succ:
                if tvshow_item.emergency_urls and not isinstance(tvshow_item.emergency_urls, dict):
                    del tvshow_item.emergency_urls
                if emergency_urls_stat in [1, 3]:                               #Operación de guardar/actualizar enlaces
                    if not tvshow_item.emergency_urls:
                        tvshow_item.emergency_urls = dict()
                    if tvshow_item.library_urls.get(serie.channel, False):
                        tvshow_item.emergency_urls.update({serie.channel: True})
                elif emergency_urls_stat == 2:                                  #Operación de Borrar enlaces
                    if tvshow_item.emergency_urls and tvshow_item.emergency_urls.get(serie.channel, False):
                        tvshow_item.emergency_urls.pop(serie.channel, None)     #borramos la entrada del .nfo
                        
            if tvshow_item.active == 30:
                tvshow_item.active = 1
            if tvshow_item.infoLabels["tmdb_id"] == serie.infoLabels["tmdb_id"]:
                tvshow_item.infoLabels = serie.infoLabels
                if tvshow_item.infoLabels["tvshowtitle"]: tvshow_item.infoLabels["title"] = tvshow_item.infoLabels["tvshowtitle"]
                elif tvshow_item.infoLabels["title"]: tvshow_item.infoLabels["tvshowtitle"] = tvshow_item.infoLabels["title"]
                tvshow_item.infoLabels["thumbnail"] = tvshow_item.infoLabels["thumbnail"].replace('http:', 'https:')
                if tvshow_item.infoLabels["thumbnail"]: tvshow_item.thumbnail = tvshow_item.infoLabels["thumbnail"]
                tvshow_item.infoLabels["fanart"] = tvshow_item.infoLabels["fanart"].replace('http:', 'https:')
                if tvshow_item.infoLabels["fanart"]: tvshow_item.fanart = tvshow_item.infoLabels["fanart"]

            if max_sea == high_sea and max_epi == high_epi and (tvshow_item.infoLabels["status"] == "Ended" 
                            or tvshow_item.infoLabels["status"] == "Canceled") and insertados == 0 and fallidos == 0:
                tvshow_item.active = 0                                          # ... no la actualizaremos más
                logger.debug("%s [%s]: serie 'Terminada' o 'Cancelada'.  Se desactiva la actualización periódica" % \
                            (serie.contentSerieName, serie.channel))
            
            
            
            # Actualiza la fecha de la próxima actualización
            update_last = datetime.date.today()
            tvshow_item.update_last = update_last.strftime('%Y-%m-%d')
            update_next = datetime.date.today() + datetime.timedelta(days=int(tvshow_item.active))
            tvshow_item.update_next = update_next.strftime('%Y-%m-%d')

            res = write_nfo(tvshow_path, head_nfo, tvshow_item)
        except:
            logger.error("Error al actualizar tvshow.nfo")
            logger.error("No se ha podido guardar las urls de emergencia de %s en la videoteca" % tvshow_item.contentSerieName)
            logger.error(traceback.format_exc())
            fallidos = -1
        else:
            # ... si ha sido correcto actualizamos la videoteca de Kodi
            if config.is_xbmc() and not silent:
                from platformcode import xbmc_videolibrary
                xbmc_videolibrary.update(FOLDER_TVSHOWS, '_scan_series')
            # Si el usuario quiere un backup de la serie (local o remoto), se toma la dirección/direcciones de destino y se copia lo nuevo
            videolibrary_backup =  config.get_setting('videolibrary_backup', channel='videolibrary')
            if videolibrary_backup:
                try:
                    import threading
                    threading.Thread(target=videolibrary_backup_exec, args=(tvshow_item, videolibrary_backup)).start()
                except:
                    logger.error('Error en el backup de la serie %s' % tvshow_item.path)
                    logger.error(traceback.format_exc(1))

    if fallidos == len(episodelist):
        fallidos = -1

    logger.debug("%s [%s]: insertados= %s, sobreescritos= %s, fallidos= %s" %
                 (serie.contentSerieName, serie.channel, insertados, sobreescritos, fallidos))
    return insertados, sobreescritos, fallidos


def reset_movie(movie_file, p_dialog=None, i=100, t=1):
    logger.info(movie_file)
    import math
    from core import jsontools
    
    movie_json_list = []
    heading = config.get_localized_string(60586)
    head_nfo = ''
    movie_path = filetools.basename(filetools.dirname(movie_file))

    try:
        active = False
        if not p_dialog:
            active = True
            p_dialog = platformtools.dialog_progress_bg(config.get_localized_string(60585), heading)
            p_dialog.update(0, '')

        path = filetools.dirname(movie_file)
        if movie_file.endswith('.json'):
            movie = Item().fromjson(filetools.read(movie_file))
            movie, it, overwrite = generictools.redirect_clone_newpct1(movie, overwrite=3)
            movie = redirect_url(movie)
            library_urls = {movie.channel: movie.url}
            movie_clone = movie.clone()
            movie_clone.clave = '%s|%s' % (movie.channel, movie.url)
            movie_json_list.append(movie_clone)
        else:
            head_nfo, movie = read_nfo(movie_file)
            movie, it, overwrite = generictools.redirect_clone_newpct1(movie, overwrite=3)
            movie = redirect_url(movie)
            library_urls = movie.library_urls.copy()
            del movie.library_urls
            movie_clone = movie.clone()
            for channel, url in list(library_urls.items()):
                movie_clone.channel = channel
                movie_clone.url = url
                library_urls_clone = {movie_clone.channel: movie_clone.url}
            library_urls = library_urls_clone.copy()
            for channel, url in list(library_urls.items()):
                json_path = filetools.join(path, ("%s [%s].json" % (movie.title.lower(), channel)))
                if filetools.exists(json_path):
                    try:
                        movie_clone = Item().fromjson(filetools.read(json_path))
                        movie_clone.clave = '%s|%s' % (channel, url)
                        movie_json_list.append(movie_clone)
                    except:
                        pass
        
        # Verificamos que las webs de los canales estén activas
        from core import httptools
        for channel, url in list(library_urls.items()):
            if not url.startswith('magnet'):
                response = httptools.downloadpage(url, timeout=10, ignore_response_code=True, hide_infobox=True)
                if not response.sucess:
                    raise Exception(response.code)
        
        if movie.emergency_urls: del movie.emergency_urls
        if movie.library_playcounts: del movie.library_playcounts
        if movie.strm_path: del movie.strm_path
        if movie.path: del movie.path
        if movie.nfo: del movie.nfo
        if not movie.fanart and movie.infoLabels.get('fanart', ''):
            movie.fanart = movie.infoLabels['fanart']

        # Eliminamos la carpeta con la pelicula ...
        filetools.rmdirtree(path)

        # ... y la volvemos a añadir
        for channel, url in list(library_urls.items()):
            clave = '%s|%s' % (channel, url)
            movie_clone = movie.clone()
            movie_clone.channel = channel
            movie_clone.category = channel.capitalize()
            movie_clone.url = url
            movie_clone, it, overwrite = generictools.redirect_clone_newpct1(movie_clone, overwrite=3)
            p_dialog.update(int(math.ceil((i + 1) * t)), heading, "%s: %s" % (movie_clone.contentTitle,
                                                                              movie_clone.channel.capitalize()))
            for movie_clone_json in movie_json_list:
                if not movie_clone_json.channel:
                    logger.error("Error al crear de nuevo la película: %s" % json_path)
                    continue
                if movie_clone_json.clave != clave:
                    continue
                if not movie_clone.clean_plot and movie_clone_json.clean_plot:
                    movie_clone.clean_plot = movie_clone_json.clean_plot
                if not movie_clone.context and movie_clone_json.context:
                    movie_clone.context = movie_clone_json.context
                if not movie_clone.extra and movie_clone_json.extra:
                    movie_clone.extra = movie_clone_json.extra
                if not movie_clone.extra2 and movie_clone_json.extra2:
                    movie_clone.extra2 = movie_clone_json.extra2
                if not movie_clone.language and movie_clone_json.language:
                    movie_clone.language = movie_clone_json.language
                if movie_clone_json.thumbnail:
                    movie_clone.thumbnail = movie_clone_json.thumbnail
                if movie_clone_json.list_language:
                    movie_clone.list_language = movie_clone_json.list_language
                if movie_clone_json.list_quality:
                    movie_clone.list_quality = movie_clone_json.list_quality
                if movie_clone_json.text_bold:
                    movie_clone.text_bold = movie_clone_json.text_bold
                if movie_clone_json.password:
                    movie_clone.password = movie_clone_json.password
                if movie_clone_json.post:
                    movie_clone.post = movie_clone_json.post
                if movie_clone_json.sid:
                    movie_clone.sid = movie_clone_json.sid
                if movie_clone_json.referer:
                    movie_clone.referer = movie_clone_json.referer
                if movie_clone_json.headers:
                    movie_clone.headers = movie_clone_json.headers
                if movie_clone_json.torrent_info:
                    movie_clone.torrent_info = movie_clone_json.torrent_info
                if movie_clone_json.wanted:
                    movie_clone.wanted = movie_clone_json.wanted
                movie_clone.title = movie_clone_json.title
                save_movie(movie_clone, silent=True)
                break
            else:
                save_movie(movie_clone, silent=True)
    except Exception as ex:
        heading = "Error al crear de nuevo la película"
        logger.error(heading)
        logger.error(traceback.format_exc())
        p_dialog.update(int(math.ceil((i + 1) * t)), heading, "%s: %s" % (movie.contentTitle,
                                                                          movie.channel.capitalize()))
        time.sleep(3)
        logger.error(traceback.format_exc())
    
    if active:
        p_dialog.close()
        if config.is_xbmc():
            import xbmc
            from platformcode import xbmc_videolibrary
            xbmc_videolibrary.update(FOLDER_MOVIES, '_scan_series')             # Se escanea el directorio de cine para catalogar en Kodi
            while xbmc.getCondVisibility('Library.IsScanningVideo()'):          # Se espera a que acabe el scanning
                time.sleep(1)
            if movie_file.endswith('.nfo'):
                xbmc_videolibrary.mark_content_as_watched_on_alfa(movie_file)


def reset_serie(tvshow_file, p_dialog=None, i=100, t=1, inactive=False):
    logger.info(tvshow_file)
    res = False
    tvshow_path = filetools.basename(filetools.dirname(tvshow_file))
    
    try:
        active = False
        if not p_dialog:
            active = True
            heading = config.get_localized_string(60584)
            p_dialog = platformtools.dialog_progress_bg(config.get_localized_string(60585), heading)
            p_dialog.update(0, '')
        
        head_nfo, serie = read_nfo(tvshow_file)
        path = filetools.dirname(tvshow_file)

        if not serie.active and not active and not inactive:
            # si la serie no esta activa descartar
            if active:
                p_dialog.close()
            return

        # Limpiamos el .nfo y forzamos recarga de todos los episodios
        if serie.emergency_urls: del serie.emergency_urls
        if serie.nfo: del serie.nfo
        if serie.strm_path: del serie.strm_path
        if not serie.fanart and serie.infoLabels.get('fanart', ''):
            serie.fanart = serie.infoLabels['fanart']
        if not serie.thumbnail and serie.infoLabels.get('thumbnail', ''):
            serie.thumbnail = serie.infoLabels['thumbnail']
        serie.library_playcounts = {serie.contentSerieName: 0}
        serie.ow_force = '1'
        
        # Verificamos que las webs de los canales estén activas
        from core import httptools
        serie, it, overwrite = generictools.redirect_clone_newpct1(serie, overwrite=3)
        serie = redirect_url(serie)
        for channel, url in list(serie.library_urls.items()):
            if not url.startswith('magnet'):
                response = httptools.downloadpage(url, timeout=10, ignore_response_code=True, hide_infobox=True)
                if not response.sucess:
                    raise Exception(response.code)
        
        # Eliminamos la carpeta con la serie ...
        filetools.rmdirtree(path)
        time.sleep(1)

        # ... y la volvemos a añadir con el .nfo
        filetools.mkdir(path)
        res = write_nfo(tvshow_file, head_nfo, serie)
        if res:
            from videolibrary_service import update
            update(path, p_dialog, i, t, serie, 3, redir=False)
        else:
            logger.error("Error al crear de nuevo la serie: %s" % tvshow_path)
    except Exception as ex:
        heading = "Error al crear de nuevo la serie: %s" % tvshow_path
        logger.error(heading)
        logger.error(traceback.format_exc())
        import math
        p_dialog.update(int(math.ceil((i + 1) * t)), heading, "%s: %s" % (serie.contentSerieName,
                                                                          serie.channel.capitalize()))
        time.sleep(3)
    
    if active:
        p_dialog.close()
        if config.is_xbmc() and res:
            import xbmc
            from platformcode import xbmc_videolibrary
            xbmc_videolibrary.update(FOLDER_TVSHOWS, '_scan_series')            # Se escanea el directorio de series para catalogar en Kodi
            while xbmc.getCondVisibility('Library.IsScanningVideo()'):          # Se espera a que acabe el scanning
                time.sleep(1)
            xbmc_videolibrary.mark_content_as_watched_on_alfa(tvshow_file)


def redirect_url(video, channel=''):

    try:
        if isinstance(video, (dict, Item)):
            if video.url:
                video.url = redirect_url(video.url, channel=video.channel)
            if video.library_urls:
                for channel, url in list(video.library_urls.items()):
                    if not url.startswith('magnet'):
                        video.library_urls[channel] = redirect_url(url, channel)
            if video.library_filter_show and video.channel and video.channel != 'videolibrary':
                title = video.contentTitle if video.contentType == 'movie' else video.contentSerieName
                video.show = video.library_filter_show.get(video.channel, title)
            if video.url_tvshow:
                video.url_tvshow = redirect_url(video.url_tvshow, video.channel)
            if video.referer:
                video.referer = redirect_url(video.referer, video.channel)
        
        elif channel and generictools.verify_channel(channel) != 'newpct1' and not video.startswith('magnet'):
            try:
                channel_host = ''
                obj = __import__('channels.%s' % channel, fromlist=["channels.%s" % channel])
                if obj.host and isinstance(obj.host, str):
                    channel_host = obj.host
                    if obj.canonical and isinstance(obj.canonical, dict):
                        if channel_host in canonical.get('host_black_list', []) and canonical.get('host_alt', []):
                            channel_host = canonical['host_alt'][0]
            except:
                pass
            
            if channel_host and not video.startswith(channel_host):
                logger.debug("vl channel: %s" % channel)
                logger.debug("vl url: %s" % video)
                logger.debug("cambiando dominio....")

                video = re.sub("(https?:\/\/.+?\/)", channel_host, video)
                logger.debug("Nueva URL: %s" % video)
    except:
        logger.error(traceback.format_exc())
    
    return video


def add_movie(item):
    """
        guarda una pelicula en la libreria de cine. La pelicula puede ser un enlace dentro de un canal o un video
        descargado previamente.

        Para añadir episodios descargados en local, el item debe tener exclusivamente:
            - contentTitle: titulo de la pelicula
            - title: titulo a mostrar junto al listado de enlaces -findvideos- ("Reproducir video local HD")
            - infoLabels["tmdb_id"] o infoLabels["imdb_id"]
            - contentType == "movie"
            - channel = "downloads"
            - url : ruta local al video

        @type item: item
        @param item: elemento que se va a guardar.
    """
    logger.info()

    #Para desambiguar títulos, se provoca que TMDB pregunte por el título realmente deseado
    #El usuario puede seleccionar el título entre los ofrecidos en la primera pantalla
    #o puede cancelar e introducir un nuevo título en la segunda pantalla
    #Si lo hace en "Introducir otro nombre", TMDB buscará automáticamente el nuevo título
    #Si lo hace en "Completar Información", cambia parcialmente al nuevo título, pero no busca en TMDB.  Hay que hacerlo
    #Si se cancela la segunda pantalla, la variable "scraper_return" estará en False.  El usuario no quiere seguir
    
    item = generictools.update_title(item) #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels
    #if item.tmdb_stat:
    #    del item.tmdb_stat          #Limpiamos el status para que no se grabe en la Videoteca
    
    new_item = item.clone(action="findvideos", contentType='movie')
    new_item.contentTitle = re.sub('^(V)-', '', new_item.title)
    new_item.title = re.sub('^(V)-', '', new_item.title)
    if '-Película-' in new_item.infoLabels.get('tagline', ''): del new_item.infoLabels['tagline']
    generictools.format_tmdb_id(new_item)                                       # Normaliza el formato de los IDs

    insertados, sobreescritos, fallidos = save_movie(new_item)

    if fallidos == 0:
        generictools.create_videolab_list(update=new_item.infoLabels)
        config.cache_reset(label='alfa_videolab_series_list')
        platformtools.dialog_ok(config.get_localized_string(30131), new_item.contentTitle,
                                config.get_localized_string(30135))             # 'se ha añadido a la videoteca'
    else:
        platformtools.dialog_ok(config.get_localized_string(30131),
                                config.get_localized_string(60066))             # "ERROR, la pelicula NO se ha añadido a la videoteca")


def add_tvshow(item, channel=None):
    """
        Guarda contenido en la libreria de series. Este contenido puede ser uno de estos dos:
            - La serie con todos los capitulos incluidos en la lista episodelist.
            - Un solo capitulo descargado previamente en local.

        Para añadir episodios descargados en local, el item debe tener exclusivamente:
            - contentSerieName (o show): Titulo de la serie
            - contentTitle: titulo del episodio para extraer season_and_episode ("1x01 Piloto")
            - title: titulo a mostrar junto al listado de enlaces -findvideos- ("Reproducir video local")
            - infoLabels["tmdb_id"] o infoLabels["imdb_id"]
            - contentType != "movie"
            - channel = "downloads"
            - url : ruta local al video

        @type item: item
        @param item: item que representa la serie a guardar
        @type channel: modulo
        @param channel: canal desde el que se guardara la serie.
            Por defecto se importara item.from_channel o item.channel

    """
    import xbmc
    
    logger.info("show=#" + item.show + "#")
    #logger.debug("item en videolibrary add tvshow: %s" % item)
    item.title = re.sub('^(V)-', '', item.title)
    if '-Serie-' in item.infoLabels.get('tagline', ''): del item.infoLabels['tagline']
    if item.channel == "downloads":
        itemlist = [item.clone()]

    else:
        # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
        item.action = item.extra
        if isinstance(item.extra, str) and "###" in item.extra:
            item.action = item.extra.split("###")[0]
            item.extra = item.extra.split("###")[1]

        if item.from_action:
            item.__dict__["action"] = item.__dict__.pop("from_action")
            item.__dict__["extra"] = item.__dict__["action"]

        if item.from_channel:
            item.__dict__["channel"] = item.__dict__.pop("from_channel")

        if not channel:
            try:
                channel = __import__('channels.%s' % item.channel, fromlist=["channels.%s" % item.channel])
            except ImportError:
                platformtools.dialog_ok(config.get_localized_string(30131), config.get_localized_string(60068))
                logger.error("La serie %s no se ha podido añadir a la videoteca, Canal: %s" % (item.show, item.channel))
                return

        #Para desambiguar títulos, se provoca que TMDB pregunte por el título realmente deseado
        #El usuario puede seleccionar el título entre los ofrecidos en la primera pantalla
        #o puede cancelar e introducir un nuevo título en la segunda pantalla
        #Si lo hace en "Introducir otro nombre", TMDB buscará automáticamente el nuevo título
        #Si lo hace en "Completar Información", cambia parcialmente al nuevo título, pero no busca en TMDB.  Hay que hacerlo
        #Si se cancela la segunda pantalla, la variable "scraper_return" estará en False.  El usuario no quiere seguir
        
        item = generictools.update_title(item)      # Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels
        #if item.tmdb_stat:
        #    del item.tmdb_stat          #Limpiamos el status para que no se grabe en la Videoteca
        
        # Quitamos la etiqueta de Filtertools
        if 'filtertools' in item: del item.filtertools
        
        # Obtiene el listado de episodios
        generictools.format_tmdb_id(item)                                       # Normaliza el formato de los IDs
        itemlist = getattr(channel, item.action)(item)
        generictools.format_tmdb_id(itemlist)                                   # Normaliza el formato de los IDs

    global magnet_caching
    magnet_caching = False
    insertados, sobreescritos, fallidos, path = save_tvshow(item, itemlist)

    if not insertados and not sobreescritos and not fallidos:
        platformtools.dialog_ok(config.get_localized_string(30131), config.get_localized_string(60067))
        logger.error("La serie %s no se ha podido añadir a la videoteca. No se ha podido obtener ningun episodio"
                     % item.show)

    elif fallidos == -1:
        platformtools.dialog_ok(config.get_localized_string(30131), config.get_localized_string(60068))
        logger.error("La serie %s no se ha podido añadir a la videoteca" % item.show)

    elif fallidos > 0:
        platformtools.dialog_ok(config.get_localized_string(30131), config.get_localized_string(60069))
        logger.error("No se han podido añadir %s episodios de la serie %s a la videoteca" % (fallidos, item.show))

    else:
        generictools.create_videolab_list(update=item.infoLabels)
        config.cache_reset(label='alfa_videolab_series_list')
        platformtools.dialog_ok(config.get_localized_string(30131), config.get_localized_string(60070))
        logger.info("Se han añadido %s episodios de la serie %s a la videoteca" %
                    (insertados, item.show))
        if config.is_xbmc():
            if config.get_setting("sync_trakt_new_tvshow", "videolibrary"):
                from platformcode import xbmc_videolibrary
                if config.get_setting("sync_trakt_new_tvshow_wait", "videolibrary"):
                    # Comprobar que no se esta buscando contenido en la videoteca de Kodi
                    while xbmc.getCondVisibility('Library.IsScanningVideo()'):
                        xbmc.sleep(1000)
                # Se lanza la sincronizacion para la videoteca de Kodi
                xbmc_videolibrary.sync_trakt_kodi()
                # Se lanza la sincronización para la videoteca del addon
                xbmc_videolibrary.sync_trakt_addon(path)
        
        #Si el canal lo permite, se comienza el proceso de descarga de los nuevos episodios descargados
        if insertados:
            serie = item.clone()
            serie.channel = generictools.verify_channel(serie.channel)
            if config.get_setting('auto_download_new', serie.channel, default=False):
                serie.sub_action = 'auto'
                serie.add_videolibrary = True
                serie.category = itemlist[0].category
                from channels import downloads
                downloads.save_download(serie, silent=True)
                if serie.sub_action: del serie.sub_action
                while xbmc.getCondVisibility('Library.IsScanningVideo()'):
                    xbmc.sleep(1000)
                downloads.download_auto(serie)


def emergency_urls(item, channel=None, path=None, headers={}):
    logger.info()
    from servers.torrent import caching_torrents
    
    """ 
    Llamamos a Findvideos del canal con la variable "item.videolibray_emergency_urls = True" para obtener la variable
    "item.emergency_urls" con la lista de listas de tuplas de los enlaces torrent y de servidores directos para ese episodio o película
    En la lista [0] siempre deben ir los enlaces torrents, si los hay.  Si se desea cachear los .torrents, la búsqueda va contra esa lista.
    En la lista dos irán los enlaces de servidores directos, pero también pueden ir enlaces magnet (que no son cacheables)
    """
    # Lanzamos un "lookup" en el "findvideos" del canal para obtener los enlaces de emergencia
    try:
        if channel == None:                             #Si el llamador no ha aportado la estructura de channel, se crea
            channel = generictools.verify_channel(item.channel)             #Se verifica si es un clon, que devuelva "newpct1"
            channel = __import__('channels.%s' % channel, fromlist=["channels.%s" % channel])
        if hasattr(channel, 'findvideos'):                                  #Si el canal tiene "findvideos"...
            item.videolibray_emergency_urls = True                          #... se marca como "lookup"
            channel_save = item.channel                 #... guarda el canal original por si hay fail-over en Newpct1
            category_save = item.category               #... guarda la categoría original por si hay fail-over o redirección en Newpct1
            post_save = item.post                       #... guarda el post original
            referer_save = item.referer                 #... guarda el referer original
            headers_save = item.headers                 #... guarda el headers original
            if item.channel_redir:                      #... si hay un redir, se restaura temporamente el canal alternativo
                item.channel = scrapertools.find_single_match(item.url, 'http.?\:\/\/(?:www.)?(\w+)\.\w+\/').lower()
                item.category = scrapertools.find_single_match(item.url, 'http.?\:\/\/(?:www.)?(\w+)\.\w+\/').capitalize()
            item_res = item.clone()
            item_res = getattr(channel, 'findvideos')(item_res)             #... se procesa Findvideos
            item_res.channel = channel_save             #... restaura el canal original por si hay fail-over en Newpct1
            item.channel = channel_save                 #... restaura el canal original por si hay fail-over en Newpct1
            item_res.category = category_save           #... restaura la categoría original por si hay fail-over o redirección en Newpct1
            item.category = category_save               #... restaura la categoría original por si hay fail-over o redirección en Newpct1
            del item_res.videolibray_emergency_urls                         #... y se borra la marca de lookup
            if item.videolibray_emergency_urls:
                del item.videolibray_emergency_urls                         #... y se borra la marca de lookup original
    except:
        logger.error('ERROR al procesar el título en Findvideos del Canal: ' + item.channel + ' / ' + item.title)
        logger.error(traceback.format_exc())
        item.channel = channel_save                     #... restaura el canal original por si hay fail-over o redirección en Newpct1
        item.category = category_save                   #... restaura la categoría original por si hay fail-over o redirección en Newpct1
        item_res = item.clone()                         #Si ha habido un error, se devuelve el Item original
        if item_res.videolibray_emergency_urls:
            del item_res.videolibray_emergency_urls                         #... y se borra la marca de lookup
        if item.videolibray_emergency_urls:
            del item.videolibray_emergency_urls                             #... y se borra la marca de lookup original
        item_res.referer = referer_save
        item_res.headers = headers_save
        item_res.post = post_save
    
    # Si el usuario ha activado la opción "emergency_urls_torrents", se descargarán los archivos .torrent de cada título
    else:                                                                   #Si se han cacheado con éxito los enlaces...
        try:
            referer = None
            post = None
            subtitles_list = []
            channel_bis = generictools.verify_channel(item.channel)
            if config.get_setting("emergency_urls_torrents", channel_bis) and item_res.emergency_urls and path != None:
                videolibrary_path = config.get_videolibrary_path()              #detectamos el path absoluto del título
                movies = FOLDER_MOVIES
                series = FOLDER_TVSHOWS
                if movies in path: 
                    folder = movies
                else:
                    folder = series
                videolibrary_path = filetools.join(videolibrary_path, folder)
                i = 1
                if item_res.referer: referer = item_res.referer
                if item_res.post: post = item_res.post
                emergency_urls = item_res.emergency_urls[0]
                for x, url in enumerate(emergency_urls):                        #Recorremos las urls de emergencia...
                    torrents_path = re.sub(r'(?:\.\w+$)', '_%s.torrent' % str(i).zfill(2), path)
                    path_real = ''
                    if not url.startswith('http') and (filetools.isfile(url) or filetools.isdir(url)) and filetools.exists(url):
                        filetools.copy(url, torrents_path, silent=True)
                        path_real = torrents_path
                    elif magnet_caching or not url.startswith('magnet'):
                        torrent_params = {
                                          'url': url,
                                          'torrents_path': torrents_path,
                                          'local_torr': item_res.torrents_path,
                                          'lookup': True
                                         }
                        kwargs = {}
                        if item_res.kwargs: kwargs = item_res.kwargs
                        torrent_file, torrent_params = caching_torrents(url, torrent_params=torrent_params, referer=referer, 
                                                                        post=post, headers=headers or item_res.headers, item=item_res, 
                                                                        **kwargs)
                        if torrents_path == 'CF_BLOCKED' or url == 'CF_BLOCKED' or torrent_params['torrents_path'] == 'CF_BLOCKED':
                            torrents_path = ''
                            torrent_params['torrents_path'] = ''
                        path_real = torrent_params.get('torrents_path', '')
                        url = torrent_params.get('url', url)
                        if url.startswith('magnet'): path_real = url
                        subtitles_list = torrent_params.get('subtitles_list', [])
                    elif url.startswith('magnet'):
                        path_real = url

                    if path_real:                                               #Si ha tenido éxito...
                        item_res.emergency_urls[0][i-1] = path_real.replace(videolibrary_path, '')  #se guarda el "path" relativo
                        if not url.startswith('http') and (filetools.isfile(url) or filetools.isdir(url)) and filetools.exists(url):
                            item_res.url = item_res.emergency_urls[0][i-1]
                        if 'ERROR' in item.torrent_info: item.torrent_info = ''
                    if subtitles_list and not item_res.subtitle:
                        item_res.subtitle = subtitles_list[0].replace(videolibrary_path, '')  #se guarda el "path" relativo
                    i += 1
                    
            # Restauramos variables originales
            if referer_save and not item_res.referer:
                item_res.referer = referer_save
            if headers_save and not item_res.headers:
                item_res.headers = headers_save
            elif not headers_save and item_res.headers:
                del item_res.headers
            if post_save and not item_res.post:
                item_res.post = post_save
            item_res.url = item.url
            if item.torrents_path:
                del item.torrents_path
            if item_res.torrents_path:
                del item_res.torrents_path
            if item_res.kwargs:
                del item_res.kwargs
            if item.kwargs:
                del item.kwargs

        except:
            logger.error('ERROR al cachear el .torrent de: ' + item.channel + ' / ' + item.title)
            logger.error(traceback.format_exc())
            item_res = item.clone()                                             #Si ha habido un error, se devuelve el Item original
            item_res.channel = channel_save                     #... restaura el canal original por si hay fail-over o redirección en Newpct1
            item_res.category = category_save                   #... restaura la categoría original por si hay fail-over o redirección en Newpct1
            if item_res.videolibray_emergency_urls:
                del item_res.videolibray_emergency_urls                         #... y se borra la marca de lookup
            if item.videolibray_emergency_urls:
                del item.videolibray_emergency_urls                             #... y se borra la marca de lookup original
            item_res.referer = referer_save
            item_res.headers = headers_save
            item_res.post = post_save

    #logger.debug(item_res.emergency_urls)
    return item_res                                                             #Devolvemos el Item actualizado con los enlaces de emergencia


def videolibrary_backup_exec(item, videolibrary_backup):
    from datetime import datetime
    try: 
        if item.strm_path:
            contentType = FOLDER_MOVIES
            video_path = filetools.join(config.get_videolibrary_path(), contentType, filetools.dirname(item.strm_path))
        else:
            contentType = FOLDER_TVSHOWS
            video_path = filetools.join(config.get_videolibrary_path(), contentType, item.path)
        logger.info(filetools.basename(video_path))

        if not item or not videolibrary_backup:
            logger.error('Peli/Serie o Ruta incorrectos')
            raise
        if not filetools.exists(video_path):
            logger.error('Ruta a Videolibrary incorrecta: %s' % video_path)
            raise

        backup_addr_list = videolibrary_backup.split(',')
        backup_addr_list_alt = backup_addr_list[:]
        # Verificamos que las direcciones están accesibles
        for addr in backup_addr_list_alt:
            addr_alt = addr
            if scrapertools.find_single_match(addr_alt, '^\w+:\/\/') and '@' in addr_alt:
                addr_alt = re.sub(':\/\/.*?\:.*?\@', '://USERNAME:PASSWORD@', addr_alt)
            if not filetools.exists(addr):
                logger.error('Dirección no accesible: %s' % addr_alt)
                backup_addr_list.remove(addr)
            else:
                path = filetools.join(addr, contentType)
                if not filetools.exists(path):
                    filetools.mkdir(path)
                if not filetools.exists(path) and path.startswith('ftp'):
                    path = path.replace('ftp://', 'smb://')
                    filetools.mkdir(path)
                if filetools.exists(path):
                    res = filetools.write(filetools.join(path, 'back_up_test'), contentType, silent=True)
                    if res:
                        res = filetools.remove(filetools.join(path, 'back_up_test'), silent=True)
                        if not res and path.startswith('ftp'):
                            path = path.replace('ftp://', 'smb://')
                            res = filetools.remove(filetools.join(path, 'back_up_test'), silent=True)
                        continue
                logger.error('Dirección no accesible para escritura: %s' % filetools.join(addr_alt, contentType))
                backup_addr_list.remove(addr)
                    
        if not backup_addr_list:
            logger.error('No hay direcciones accesibles para el backup.  Operación terminada')
            return False
            
        # Una vez validadas la(s) ruta(s) se procede a la copia de los archivos que no están en el destino, más el tvshow.nfo de Series
        for addr in backup_addr_list:
            backup_path = filetools.join(addr, contentType, filetools.basename(video_path))
            if not filetools.exists(backup_path):
                filetools.mkdir(backup_path)
            if not filetools.exists(backup_path) and backup_path.startswith('ftp'):
                backup_path_alt = backup_path.replace('ftp://', 'smb://')
                filetools.mkdir(backup_path_alt)
            
            if filetools.exists(backup_path):
                list_video_alt = []
                list_backup_alt = []
                patron_ls = '[^\s]+\s+[^\s]+\s+[^\s]+\s+[^\s]+\s+[^\s]+\s+(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})\s+([^$]+)'
                list_video = filetools.listdir(video_path, file_inf=True)
                for file in list_video:
                    list_video_alt.append(scrapertools.find_single_match(file, patron_ls))
                list_backup = filetools.listdir(backup_path, file_inf=True)
                for file in list_backup:
                    list_backup_alt.append(scrapertools.find_single_match(file, patron_ls))
                addr_alt = backup_path
                if scrapertools.find_single_match(addr_alt, '^\w+:\/\/') and '@' in addr_alt:
                    addr_alt = re.sub(':\/\/.*?\:.*?\@', '://USERNAME:PASSWORD@', addr_alt)
                    logger.info('Haciendo backup en %s' % addr_alt)
                
                for date_time_a, file in list_video_alt:
                    copy_stat = False
                    if file not in str(list_backup_alt):
                        copy_stat = True
                    if file in str(list_backup_alt):
                        for date_time_b, file_b in list_backup_alt:
                            if file == file_b:
                                if date_time_a != date_time_b:
                                    try:
                                        video_time = datetime.strptime(date_time_a, '%Y-%m-%d %H:%M')
                                    except TypeError:
                                        video_time = datetime(*(time.strptime(date_time_a, '%Y-%m-%d %H:%M')[0:6]))
                                    try:
                                        backup_time = datetime.strptime(date_time_b, '%Y-%m-%d %H:%M')
                                    except TypeError:
                                        backup_time = datetime(*(time.strptime(date_time_b, '%Y-%m-%d %H:%M')[0:6]))
                                    if video_time > backup_time:
                                        copy_stat = True
                                break
                            
                    if copy_stat:
                        res = filetools.copy(filetools.join(video_path, file), filetools.join(backup_path, file), silent=True)
                        if not res and backup_path.startswith('ftp'):
                            backup_path = backup_path.replace('ftp://', 'smb://')
                            addr_alt = addr_alt.replace('ftp://', 'smb://')
                            logger.error('Dirección no accesible para escritura.  Cambiado a SMB: %s' % filetools.join(addr_alt, contentType))
                            res = filetools.copy(filetools.join(video_path, file), filetools.join(backup_path, file), silent=True)
                        logger.info('%s %s, Status: %s' % (backup_path[:4], file, str(res)))
            else:
                logger.error('Dirección no accesible para escritura: %s' % backup_path)
                
    except:
        logger.error(traceback.format_exc())
        return False
    
    return True