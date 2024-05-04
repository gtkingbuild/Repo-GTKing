# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# Server management
# --------------------------------------------------------------------------------

from __future__ import division
from __future__ import absolute_import
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    #from future import standard_library
    #standard_library.install_aliases()
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

from builtins import range
from past.utils import old_div

import datetime
import re
import time
import codecs
import traceback

from core import filetools
from core import httptools
from core import jsontools
from core.item import Item
from platformcode import config, logger

IGNORE_NULL_LABELS = []
dict_servers_parameters = {}
proxy_channel_bloqued = {}
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?([\w|\-\d]+\.(?:[\w|\-\d]+\.?)?(?:[\w|\-\d]+\.?)?(?:[\w|\-\d]+))(?:\/|\?|$)'

""" CACHING SERVERS PARAMETERS """
alfa_caching = False
alfa_servers = {}
alfa_servers_jsons = {}
kodi = True
try:
    import xbmcgui
    import json
    window = xbmcgui.Window(10000)                                              # Home
except:
    kodi = False
DEBUG = config.DEBUG_JSON


def find_video_items(item=None, data=None):
    """
    Función genérica para buscar vídeos en una página, devolviendo un itemlist con los items listos para usar.
     - Si se pasa un Item como argumento, a los items resultantes mantienen los parametros del item pasado
     - Si no se pasa un Item, se crea uno nuevo, pero no contendra ningun parametro mas que los propios del servidor.

    @param item: Item al cual se quieren buscar vídeos, este debe contener la url válida
    @type item: Item
    @param data: Cadena con el contendio de la página ya descargado (si no se pasa item)
    @type data: str

    @return: devuelve el itemlist con los resultados
    @rtype: list
    """
    logger.info()
    from core import httptools
    
    itemlist = []

    # Descarga la página
    if data is None:
        data = httptools.downloadpage(item.url).data

    # Crea un item si no hay item
    if item is None:
        item = Item()
    # Pasa los campos thumbnail y title a contentThumbnail y contentTitle
    else:
        if not item.contentThumbnail:
            item.contentThumbnail = item.thumbnail
        if not item.contentTitle:
            item.contentTitle = item.title

    # Busca los enlaces a los videos
    for label, url, server, thumbnail in findvideos(data):
        title = config.get_localized_string(70206) % label
        itemlist.append(
            item.clone(title=title, action="play", url=url, thumbnail=thumbnail, server=server, folder=False))

    return itemlist


def get_servers_itemlist(itemlist, fnc=None, sort=False):
    """
    Obtiene el servidor para cada uno de los items, en funcion de su url.
     - Asigna el servidor, la url modificada, el thumbnail (si el item no contiene contentThumbnail se asigna el del thumbnail)
     - Si se pasa una funcion por el argumento fnc, esta se ejecuta pasando el item como argumento,
       el resultado de esa funcion se asigna al titulo del item
       - En esta funcion podemos modificar cualquier cosa del item
       - Esta funcion siempre tiene que devolver el item.title como resultado
     - Si no se encuentra servidor para una url, se asigna "directo"
     
    @param itemlist: listado de items
    @type itemlist: list
    @param fnc: función para ejecutar con cada item (para asignar el titulo)
    @type fnc: function
    @param sort: indica si el listado resultante se ha de ordenar en funcion de la lista de servidores favoritos
    @type sort: bool
    """
    # Recorre los servidores
    for serverid in list(get_servers_list().keys()):
        server_parameters = get_server_parameters(serverid)

        # Recorre los patrones
        for pattern in server_parameters.get("find_videos", {}).get("patterns", []):
            # logger.info(pattern["pattern"])
            # Recorre los resultados
            for match in re.compile(pattern["pattern"], re.DOTALL).finditer(
                    "\n".join([item.url.split('|')[0] for item in itemlist if not item.server])):
                url = pattern["url"]
                for x in range(len(match.groups())):
                    url = url.replace("\\%s" % (x + 1), match.groups()[x])

                for item in itemlist:
                    if match.group() in item.url:
                        if not item.contentThumbnail:
                            item.contentThumbnail = item.thumbnail
                        item.thumbnail = server_parameters.get("thumbnail", "")
                        item.server = serverid
                        if '|' in item.url:
                            item.url = url + '|' + item.url.split('|')[1]
                        else:
                            item.url = url

    # Eliminamos los servidores desactivados
    #itemlist = filter(lambda i: not i.server or is_server_enabled(i.server), itemlist)
    # Filtrar si es necesario
    itemlist = filter_servers(itemlist)

    for item in itemlist:
        # Asignamos "directo" en caso de que el server no se encuentre en Alfa y agregado el thumbnail
        if not item.server and item.url:
            item.server = "directo"
            item.contentThumbnail = item.thumbnail
        if fnc:
            item.title = fnc(item)


    # Ordenar segun favoriteslist si es necesario
    if sort:
        itemlist = sort_servers(itemlist)

    return itemlist


def findvideos(data, skip=False):
    """
    Recorre la lista de servidores disponibles y ejecuta la funcion findvideosbyserver para cada uno de ellos
    :param data: Texto donde buscar los enlaces
    :param skip: Indica un limite para dejar de recorrer la lista de servidores. Puede ser un booleano en cuyo caso
    seria False para recorrer toda la lista (valor por defecto) o True para detenerse tras el primer servidor que
    retorne algun enlace. Tambien puede ser un entero mayor de 1, que representaria el numero maximo de enlaces a buscar.
    :return:
    """
    logger.info()
    devuelve = []
    skip = int(skip)
    servers_list = list(get_servers_list().keys())


    # Ordenar segun favoriteslist si es necesario
    servers_list = sort_servers(servers_list)
    is_filter_servers = False

    # Ejecuta el findvideos en cada servidor activo
    for serverid in servers_list:
        '''if not is_server_enabled(serverid):
            continue'''
        if config.get_setting("filter_servers") == True and config.get_setting("black_list", server=serverid):
            is_filter_servers = True
            continue
        devuelve.extend(findvideosbyserver(data, serverid))
        if skip and len(devuelve) >= skip:
            devuelve = devuelve[:skip]
            break
    if config.get_setting("filter_servers") == False:  is_filter_servers = False
    if not devuelve and is_filter_servers:
        from platformcode.platformtools import dialog_ok
        dialog_ok(config.get_localized_string(60000), config.get_localized_string(60001))

    return devuelve


def findvideosbyserver(data, serverid):
    serverid = get_server_name(serverid)
    if not serverid:
        return []

    server_parameters = get_server_parameters(serverid)
    if not server_parameters.get("active", ""):
        return []
    devuelve = []
    if "find_videos" in server_parameters:
        # Recorre los patrones
        for pattern in server_parameters["find_videos"].get("patterns", []):
            msg = "%s\npattern: %s" % (serverid, pattern["pattern"])
            # Recorre los resultados
            for match in re.compile(pattern["pattern"], re.DOTALL).finditer(data):
                url = pattern["url"]
                # Crea la url con los datos
                for x in range(len(match.groups())):
                    url = url.replace("\\%s" % (x + 1), match.groups()[x])
                msg += "\nurl encontrada: %s" % url
                value = server_parameters["name"], url, serverid, server_parameters.get("thumbnail", "")
                if value not in devuelve and url not in server_parameters["find_videos"].get("ignore_urls", []):
                    devuelve.append(value)
                logger.info(msg)

    return devuelve


def get_server_from_url(url):
    encontrado = findvideos(url, True)
    if len(encontrado) > 0:
        devuelve = encontrado[0][2]
    else:
        devuelve = "directo"

    return devuelve

def parse_hls(video_urls, server):
    logger.info()
    from core import scrapertools
    from core import httptools

    hs = ''
    new_video_urls = list()
    headers = dict()
    
    if (len(video_urls)) == 1 and config.get_setting("default_action") < 2:
        url = video_urls[0][1]
        if '|' in url:
            part = url.split('|')
            url = part[0]
            if not 'm3u8' in url:
                return video_urls
            
            khs = part[1]
            hs = '|' + khs
            matches = scrapertools.find_multiple_matches(khs, r'(\w+)=([^&]+)')
            
            for key, val in matches:
                headers[key] = val

        if not 'm3u8' in url:
                return video_urls
        
        data = httptools.downloadpage(url, headers=headers).data
        patron = r'#EXT-X-STREAM-INF.*?RESOLUTION=(\d+x\d+).*?\s(http.*?)\s'
        if not isinstance(data, str): data = codecs.decode(data, "utf-8")
        matches = scrapertools.find_multiple_matches(data, patron)

        if len(matches) > 1:
            for res, video_url in matches:
                video_url += hs
                new_video_urls.append(['m3u8 (%s) [%s]' % (res, server), video_url])

            return new_video_urls

    return video_urls


def resolve_video_urls_for_playing(server, url, video_password="", muestra_dialogo=False):
    """
    Función para obtener la url real del vídeo
    @param server: Servidor donde está alojado el vídeo
    @type server: str
    @param url: url del vídeo
    @type url: str
    @param video_password: Password para el vídeo
    @type video_password: str
    @param muestra_dialogo: Muestra el diálogo de progreso
    @type muestra_dialogo: bool

    @return: devuelve la url del video
    @rtype: list
    """
    logger.info("Server: %s, Url: %s" % (server, url))
    from core import httptools

    server = server.lower()

    video_urls = []
    video_exists = True
    error_messages = []
    opciones = []
    proxy_data = dict()
    url_proxy = url

    if httptools.channel_proxy_list(url):
        opt = {'forced_proxy': None, 'force_proxy_get': True}
        url_proxy, proxy_data, opt = httptools.check_proxy(url, **opt)
        if not proxy_data['web_name']:
            url_proxy = url

    # ACTUALIZACIÓN: Ahora se validan las url de directo en directo.py
    # Si el vídeo es "directo" o "local", si hay contraseña no hay que buscar más
    # Hay que verificar que haya url y que sea video, verlo en el server directo.py
    if (server == "directo" or server == "local") and url:
        if isinstance(video_password, list):
            return video_password, len(video_password) > 0, "<br/>".join(error_messages)
        # logger.info("Server: %s, la url es la buena" % server)
        # video_urls.append(["%s [%s]" % (urlparse.urlparse(url)[2][-4:], server), url_proxy])

    # else:
    # Averigua la URL del vídeo
    if server:
        server_parameters = get_server_parameters(server)
    else:
        server_parameters = {}

    if server_parameters and server_parameters.get("name"):
        # Muestra un diágo de progreso
        if muestra_dialogo:
            from platformcode.platformtools import dialog_progress
            progreso = dialog_progress(config.get_localized_string(20000),
                                       config.get_localized_string(70180) % server_parameters["name"])

        # Cuenta las opciones disponibles, para calcular el porcentaje

        orden = [
            ["free"] + [server] + [premium for premium in server_parameters["premium"] if not premium == server],
            [server] + [premium for premium in server_parameters["premium"] if not premium == server] + ["free"],
            [premium for premium in server_parameters["premium"] if not premium == server] + [server] + ["free"]
        ]

        if server_parameters["free"] == True:
            opciones.append("free")
        opciones.extend(
            [premium for premium in server_parameters["premium"] if config.get_setting("premium", server=premium)])

        priority = int(config.get_setting("resolve_priority"))
        opciones = sorted(opciones, key=lambda x: orden[priority].index(x))

        logger.info("Opciones disponibles: %s | %s" % (len(opciones), opciones))
    else:
        logger.error("No existe conector para el servidor %s" % server)
        error_messages.append(config.get_localized_string(60004) % server)
        muestra_dialogo = False

    # Importa el server
    try:
        server_module = __import__('servers.%s' % server, None, None, ["servers.%s" % server])
        logger.info("Servidor importado: %s" % server_module)
    except:
        server_module = None
        logger.error("No se ha podido importar el servidor: %s" % server)
        logger.error(traceback.format_exc())

    # Si tiene una función para ver si el vídeo existe, lo comprueba ahora
    if hasattr(server_module, 'test_video_exists'):
        logger.info("Invocando a %s.test_video_exists" % server)
        try:
            video_exists, message = server_module.test_video_exists(page_url=url)

            if not video_exists:
                error_messages.append(message)
                logger.info("test_video_exists dice que el video no existe")
            else:
                logger.info("test_video_exists dice que el video SI existe")
        except:
            logger.error("No se ha podido comprobar si el video existe")
            logger.error(traceback.format_exc())

    # Si el video existe y el modo free está disponible, obtenemos la url
    if video_exists:
        for opcion in opciones:
            # Opcion free y premium propio usa el mismo server
            if opcion == "free" or opcion == server:
                serverid = server_module
                server_name = server_parameters["name"]

            # Resto de opciones premium usa un debrider
            else:
                serverid = __import__('servers.debriders.%s' % opcion, None, None,
                                        ["servers.debriders.%s" % opcion])
                server_name = get_server_parameters(opcion)["name"]

            # Muestra el progreso
            if muestra_dialogo:
                progreso.update((old_div(100, len(opciones))) * opciones.index(opcion), config.get_localized_string(70180) % server_name)
            
            
            # Modo free
            if opcion == "free":
                try:
                    logger.info("Invocando a %s.get_video_url" % server)
                    response = serverid.get_video_url(page_url=url, video_password=video_password)
                    video_urls.extend(response)
                except:
                    logger.error("Error al obtener la url en modo free")
                    error_messages.append("Se ha producido un error en %s" % server_name)
                    logger.error(traceback.format_exc())

            # Modo premium
            else:
                try:
                    logger.info("Invocando a %s.get_video_url" % opcion)
                    response = serverid.get_video_url(page_url=url, premium=True,
                                                        user=config.get_setting("user", server=opcion),
                                                        password=config.get_setting("password", server=opcion),
                                                        video_password=video_password)
                    if response and response[0][1]:
                        video_urls.extend(response)
                    elif response and response[0][0]:
                        error_messages.append(response[0][0])
                    else:
                        error_messages.append(config.get_localized_string(60006) % server_name)
                except:
                    logger.error("Error en el servidor: %s" % opcion)
                    error_messages.append(config.get_localized_string(60006) % server_name)
                    logger.error(traceback.format_exc())

            # Si ya tenemos URLS, dejamos de buscar
            if video_urls and config.get_setting("resolve_stop") == True:
                break

        # Cerramos el progreso
        if muestra_dialogo:
            progreso.update(100, config.get_localized_string(60008))
            progreso.close()

        # Si no hay opciones disponibles mostramos el aviso de las cuentas premium
        if video_exists and not opciones and server_parameters.get("premium"):
            listapremium = [get_server_parameters(premium)["name"] for premium in server_parameters["premium"]]
            error_messages.append(
                config.get_localized_string(60009) % (server, " o ".join(listapremium)))

        # Si no tenemos urls ni mensaje de error, ponemos uno generico
        elif not video_urls and not error_messages:
            error_messages.append(config.get_localized_string(60006) % get_server_parameters(server)["name"])

    video_urls = parse_hls(video_urls, server)
    return video_urls, len(video_urls) > 0, "<br/>".join(error_messages)


def get_server_name(serverid):
    """
    Función obtener el nombre del servidor real a partir de una cadena.
    @param serverid: Cadena donde mirar
    @type serverid: str

    @return: Nombre del servidor
    @rtype: str
    """
    serverid = serverid.lower().split(".")[0]

    # Obtenemos el listado de servers
    server_list = list(get_servers_list().keys())

    # Si el nombre está en la lista
    if serverid in server_list:
        return serverid

    # Recorre todos los servers buscando el nombre
    for server in server_list:
        params = get_server_parameters(server)
        # Si la nombre esta en el listado de ids
        if serverid in str(params["id"]):
            return server
        # Si el nombre es mas de una palabra, comprueba si algun id esta dentro del nombre:
        elif len(serverid.split()) > 1:
            for id in params["id"]:
                if id in serverid:
                    return server

    # Si no se encuentra nada se devuelve una cadena vacia
    return ""


def is_server_enabled(server, domain=''):
    """
    Función comprobar si un servidor está segun la configuración establecida
    @param server: Nombre del servidor
    @type server: str

    @return: resultado de la comprobación
    @rtype: bool
    """

    server = get_server_name(server)
    if server in ['torrent']:
        return True
    server_parameters = get_server_parameters(server)
    
    if domain:
        if not proxy_channel_bloqued: get_proxy_list()
        if domain in proxy_channel_bloqued:
            logger.info('Server en PROXY: %s, Dominio: %s' % (server, domain), force=True)
            return False
            
    if server_parameters.get("active", False) == True:
        if not config.get_setting("hidepremium"):
            return True
        elif server_parameters.get("free", False) == True:
            return True
        elif [premium for premium in server_parameters["premium"] if config.get_setting("premium", server=premium)]:
            return True
    
    if not server:
        return False
    
    return False


def get_server_parameters(server):
    """
    Obtiene los datos del servidor
    @param server: Nombre del servidor
    @type server: str

    @return: datos del servidor
    @rtype: dict
    """
    # logger.info("server %s" % server)
    global dict_servers_parameters
    
    server = server.split('.')[0]
    if not server:
        return {}

    if server not in dict_servers_parameters:
        try:
            dict_server = get_server_json(server)

            # Imagenes: se admiten url y archivos locales dentro de "resources/images"
            if dict_server.get("thumbnail") and "://" not in dict_server["thumbnail"]:
                dict_server["thumbnail"] = filetools.join(config.get_runtime_path(), "resources", "media",
                                                        "servers", dict_server["thumbnail"])
            for k in ['premium', 'id']:
                dict_server[k] = dict_server.get(k, list())

                if isinstance(dict_server[k], str):
                    dict_server[k] = [dict_server[k]]

            if "find_videos" in dict_server:
                dict_server['find_videos']["patterns"] = dict_server['find_videos'].get("patterns", list())
                dict_server['find_videos']["ignore_urls"] = dict_server['find_videos'].get("ignore_urls", list())

            if "settings" in dict_server:
                dict_server['has_settings'] = True
            else:
                dict_server['has_settings'] = False

            dict_servers_parameters[server] = dict_server

        except:
            mensaje = config.get_localized_string(59986) % server
            logger.error(mensaje + traceback.format_exc())
            return {}

    return dict_servers_parameters[server]


def get_server_json(server_name, debug=DEBUG):
    # logger.info("server_name=" + server_name)
    global alfa_caching, alfa_servers_jsons
    
    server_json = {}
    
    try:
        if kodi:
            alfa_caching = bool(window.getProperty("alfa_caching"))
            if alfa_caching:
                try:
                    if not alfa_servers_jsons: alfa_servers_jsons = json.loads(window.getProperty("alfa_servers_jsons"))
                    server_json = alfa_servers_jsons.get(server_name, {}).copy()
                    if debug and server_json: logger.error('READ Cached SERVER_JSON: %s %s' % (server_name.upper(), server_json))
                except:
                    server_json = {}
                    logger.error(traceback.format_exc())
        
        if not server_json:
            server_path = filetools.join(config.get_runtime_path(), "servers", server_name + ".json")
            if not filetools.exists(server_path):
                server_path = filetools.join(config.get_runtime_path(), "servers", "debriders", server_name + ".json")

            # logger.info("server_path=" + server_path)
            server_json = jsontools.load(filetools.read(server_path))
            if debug or not server_json: logger.error('READ File (Cache: %s) SERVER_JSON: %s: %s' \
                                                       % (str(alfa_caching).upper(), server_name.upper(),  server_json))
            # logger.info("server_json= %s" % server_json)
            if kodi and alfa_caching:
                alfa_servers_jsons.update({server_name: server_json.copy()})
                window.setProperty("alfa_servers_jsons", json.dumps(alfa_servers_jsons))
                if debug: logger.error('SAVE Cached SERVER_JSON: %s: %s' % (server_name.upper(), server_json))

    except Exception as ex:
        template = "An exception of type %s occured. Arguments:\n%r"
        message = template % (type(ex).__name__, ex.args)
        logger.error(" %s" % message)
        server_json = {}

    return server_json


def get_server_controls_settings(server_name):
    dict_settings = {}

    list_controls = get_server_json(server_name).get('settings', [])
    import copy
    list_controls = copy.deepcopy(list_controls)

    # Conversion de str a bool, etc...
    for c in list_controls:
        if 'id' not in c or 'type' not in c or 'default' not in c:
            # Si algun control de la lista  no tiene id, type o default lo ignoramos
            continue

        # new dict with key(id) and value(default) from settings
        dict_settings[c['id']] = c['default']

    return list_controls, dict_settings


def get_server_setting(name, server, default=None, caching_var=True, debug=DEBUG):
    global alfa_caching, alfa_servers
    """
        Retorna el valor de configuracion del parametro solicitado.

        Devuelve el valor del parametro 'name' en la configuracion propia del servidor 'server'.

        Busca en la ruta \addon_data\plugin.video.addon\settings_servers el archivo server_data.json y lee
        el valor del parametro 'name'. Si el archivo server_data.json no existe busca en la carpeta servers el archivo 
        server.json y crea un archivo server_data.json antes de retornar el valor solicitado. Si el parametro 'name'
        tampoco existe en el el archivo server.json se devuelve el parametro default.


        @param name: nombre del parametro
        @type name: str
        @param server: nombre del servidor
        @type server: str
        @param default: valor devuelto en caso de que no exista el parametro name
        @type default: any

        @return: El valor del parametro 'name'
        @rtype: any

    """
    module = ''
    if debug:
        import inspect
        module = inspect.getmodule(inspect.currentframe().f_back.f_back)
        if module == None:
            module = "None"
        else:
            module = module.__name__
        function = inspect.currentframe().f_back.f_back.f_code.co_name
        if '<module>' in function: function = 'mainlist'
        module = ' [%s.%s]' % (module, function)
    
    # Creamos la carpeta si no existe
    if not filetools.exists(filetools.join(config.get_data_path(), "settings_servers")):
        filetools.mkdir(filetools.join(config.get_data_path(), "settings_servers"))

    file_settings = filetools.join(config.get_data_path(), "settings_servers", server + "_data.json")
    dict_settings = {}
    dict_file = {}

    if isinstance(caching_var, str):
        # Borrado de cache de un servidor y borrado de .json
        if caching_var in ['reset', 'delete']:
            if kodi:
                alfa_servers = json.loads(window.getProperty("alfa_servers"))
                if server in alfa_servers.keys():
                    if debug: logger.error('RESET Cached SERVER: %s%s: %s:' % (server.upper(), module, alfa_servers[server]))
                    del alfa_servers[server]
                    window.setProperty("alfa_servers", json.dumps(alfa_servers))
            if caching_var in ['delete']:
                if debug: logger.error('DELETE Server JSON: %s%s' % (server.upper(), module))
                filetools.remove(file_settings, silent=True)
            caching_var = False

    if kodi and caching_var:
        alfa_caching = bool(window.getProperty("alfa_caching"))
        if not alfa_servers: alfa_servers = json.loads(window.getProperty("alfa_servers"))
        dict_file = alfa_servers.get(server, {}).copy()
        if debug and dict_file: logger.error('READ Cached SERVER: %s%s, NAME: %s: %s:' % (server.upper(), module, str(name).upper(), dict_file))
    if alfa_caching and caching_var and dict_file:
        dict_settings = alfa_servers[server].get('settings', {}).copy()
        if dict_settings.get(name, ''):
            dict_settings[name] = config.decode_var(dict_settings[name])
            #logger.error('%s, %s: A: %s - D: %s' % (name, server, [alfa_servers[server][name]], [config.decode_var(dict_settings[name])]))
    
    if not dict_file and filetools.exists(file_settings):
        # Obtenemos configuracion guardada de ../settings/server_data.json
        try:
            dict_file = jsontools.load(filetools.read(file_settings))
            if debug or not dict_file: logger.error('READ File (Cache: %s) SERVER: %s%s, NAME: %s: %s:' \
                                                     % (str(caching_var and alfa_caching).upper(), server.upper(), 
                                                        module, str(name).upper(), dict_file))
            if isinstance(dict_file, dict) and 'settings' in dict_file:
                dict_settings = dict_file['settings']
                if alfa_caching:
                    alfa_servers.update({server: dict_file.copy()})
                    if debug: logger.error('SAVE Cached SERVER: %s%s: %s:' % (server.upper(), module, alfa_servers[server]))
                    window.setProperty("alfa_servers", json.dumps(alfa_servers))
        except EnvironmentError:
            logger.error("ERROR al leer el archivo: %s, parámetro: %s" % (file_settings, name))
            logger.error(filetools.file_info(file_settings))

    if not dict_settings or name not in dict_settings:
        # Obtenemos controles del archivo ../servers/server.json
        try:
            list_controls, default_settings = get_server_controls_settings(server)
        except:
            default_settings = {}
        #if name in default_settings:  # Si el parametro existe en el server.json creamos el server_data.json
        default_settings.update(dict_settings)
        dict_settings = default_settings.copy()
        if name not in dict_settings:
            dict_settings[name] = default
        dict_file['settings'] = dict_settings.copy()
        
        if alfa_caching:
            alfa_servers.update({server: dict_file.copy()})
            if debug: logger.error('SAVE Cached from Default SERVER: %s%s: %s:' % (server.upper(), module, alfa_servers[server]))
            window.setProperty("alfa_servers", json.dumps(alfa_servers))
        dict_file['settings'] = dict_settings
        
        # Creamos el archivo ../settings/cserver_data.json
        if name not in IGNORE_NULL_LABELS or (name in IGNORE_NULL_LABELS and dict_settings[name] != None):
            for label in IGNORE_NULL_LABELS:
                if label in dict_file['settings'] and dict_file['settings'][label] == None: del dict_file['settings'][label]
            json_data = jsontools.dump(dict_file)
            if debug: logger.error('WRITE File SERVER: %s%s: %s:' % (server.upper(), module, json_data))
            if not filetools.write(file_settings, json_data, silent=True):
                logger.error("ERROR al salvar el parámetro: %s en el archivo: %s" % (name, file_settings))
                logger.error(filetools.file_info(file_settings))

    # Devolvemos el valor del parametro local 'name' si existe, si no se devuelve default
    return dict_settings.get(name, default)


def set_server_setting(name, value, server, retry=False, debug=DEBUG):
    global alfa_caching, alfa_servers
    
    module = ''
    if debug:
        import inspect
        module = inspect.getmodule(inspect.currentframe().f_back.f_back)
        if module == None:
            module = "None"
        else:
            module = module.__name__
        function = inspect.currentframe().f_back.f_back.f_code.co_name
        module = ' [%s.%s]' % (module, function)
    
    # Creamos la carpeta si no existe
    if not filetools.exists(filetools.join(config.get_data_path(), "settings_servers")):
        filetools.mkdir(filetools.join(config.get_data_path(), "settings_servers"))

    file_settings = filetools.join(config.get_data_path(), "settings_servers", server + "_data.json")
    dict_settings = {}
    dict_file = {}

    if kodi:
        alfa_caching = bool(window.getProperty("alfa_caching"))
    if alfa_caching:
        if not alfa_servers: alfa_servers = json.loads(window.getProperty("alfa_servers"))
        dict_file = alfa_servers.get(server, {}).copy()
        if dict_file:
            dict_settings = alfa_servers[server].get('settings', {}).copy()
            if debug: logger.error('READ Cached SERVER: %s%s, NAME: %s: %s:' % (server.upper(), module, str(name).upper(), dict_file))

    if not dict_file and filetools.exists(file_settings):
        # Obtenemos configuracion guardada de ../settings/server_data.json
        try:
            dict_file = jsontools.load(filetools.read(file_settings))
            if debug or not dict_file: logger.error('READ File (Cache: %s) SERVER: %s%s, NAME: %s: %s:' \
                                                     % (str(alfa_caching).upper(), server.upper(), module, str(name).upper(), dict_file))
            if dict_file: dict_settings = dict_file.get('settings', {})
        except EnvironmentError:
            logger.error("ERROR al leer el archivo: %s, parámetro: %s" % (file_settings, name))
            logger.error(filetools.file_info(file_settings))

    if 'settings' in dict_file and isinstance(dict_file, dict):
        for label in IGNORE_NULL_LABELS:
            if label in dict_settings and dict_settings[label] == None: del dict_settings[label]
        dict_settings[name] = value
        dict_file['settings'] = dict_settings.copy()
    else:
        get_server_setting(name, server, caching_var=False, debug=debug)
        if not retry: return set_server_setting(name, value, server, retry=True, debug=debug)

    if alfa_caching:
        alfa_caching = bool(window.getProperty("alfa_caching"))
        if alfa_caching:
            alfa_servers.update({server: dict_file.copy()})
            if debug: logger.error('SAVE Cached SERVER: %s%s: %s:' % (server.upper(), module, alfa_servers[server]))
            window.setProperty("alfa_servers", json.dumps(alfa_servers))
        else:
            alfa_servers = {}
            if debug: logger.error('DROP Cached SERVER: %s%s: %s:' % (server.upper(), module, alfa_servers))
            window.setProperty("alfa_servers", json.dumps(alfa_servers))

    # comprobamos si existe dict_file y es un diccionario, sino lo creamos
    if not dict_file:
        dict_file = {}

    # Creamos el archivo ../settings/server_data.json
    json_data = jsontools.dump(dict_file)
    if debug: logger.error('WRITE File SERVER: %s%s: %s:' % (server.upper(), module, json_data))
    if not filetools.write(file_settings, json_data, silent=True):
        logger.error("ERROR al salvar el parámetro: %s en el archivo: %s" % (name, file_settings))
        logger.error(filetools.file_info(file_settings))
        alfa_servers = {}
        if debug: logger.error('DROP Cached SERVER: %s%s: %s:' % (server.upper(), module, alfa_servers))
        window.setProperty("alfa_servers", json.dumps(alfa_servers))
        return None

    return value


def get_servers_list():
    """
    Obtiene un diccionario con todos los servidores disponibles

    @return: Diccionario cuyas claves son los nombre de los servidores (nombre del json)
    y como valor un diccionario con los parametros del servidor.
    @rtype: dict
    """
    server_list = {}
    get_proxy_list()
    for server in filetools.listdir(filetools.join(config.get_runtime_path(), "servers")):
        if server.endswith(".json") and not server == "version.json":
            server_parameters = get_server_parameters(server)
            server_list[server.split(".")[0]] = server_parameters

    return server_list


def get_debriders_list():
    """
    Obtiene un diccionario con todos los debriders disponibles

    @return: Diccionario cuyas claves son los nombre de los debriders (nombre del json)
    y como valor un diccionario con los parametros del servidor.
    @rtype: dict
    """
    server_list = {}
    get_proxy_list()
    for server in filetools.listdir(filetools.join(config.get_runtime_path(), "servers", "debriders")):
        if server.endswith(".json"):
            server_parameters = get_server_parameters(server)
            if server_parameters["active"] == True:
                logger.info(server_parameters)
                server_list[server.split(".")[0]] = server_parameters
    return server_list


def sort_servers(servers_list):
    """
    Si esta activada la opcion "Ordenar servidores" en la configuracion de servidores y existe un listado de servidores 
    favoritos en la configuracion lo utiliza para ordenar la lista servers_list
    :param servers_list: Listado de servidores para ordenar. Los elementos de la lista servers_list pueden ser strings
    u objetos Item. En cuyo caso es necesario q tengan un atributo item.server del tipo str.
    :return: Lista del mismo tipo de objetos que servers_list ordenada en funcion de los servidores favoritos.
    """
    if servers_list and config.get_setting('favorites_servers'):
        if isinstance(servers_list[0], Item):
            servers_list = sorted(servers_list,
                                  key=lambda x: config.get_setting("favorites_servers_list", server=x.server) or 100)
        else:
            servers_list = sorted(servers_list,
                                  key=lambda x: config.get_setting("favorites_servers_list", server=x) or 100)

    return servers_list


def filter_servers(servers_list):
    """
    Si esta activada la opcion "Filtrar por servidores" en la configuracion de servidores, elimina de la lista 
    de entrada los servidores incluidos en la Lista Negra.
    :param servers_list: Listado de servidores para filtrar. Los elementos de la lista servers_list pueden ser strings
    u objetos Item. En cuyo caso es necesario q tengan un atributo item.server del tipo str.
    :return: Lista del mismo tipo de objetos que servers_list filtrada en funcion de la Lista Negra.
    """
    from platformcode.platformtools import dialog_yesno
    from core.scrapertools import find_single_match

    #Eliminamos los inactivos
    if servers_list:
        #servers_list = [i for i in servers_list if not i.server or is_server_enabled(i.server, url=domain)]
        
        servers_list_alt = []
        for i in servers_list:
            if i.server:
                channel = i.contentChannel if i.contentChannel and i.contentChannel not in ['list', 'videolibrary'] else i.channel
                domain = find_single_match(i.url, patron_domain)
                if domain and domain in config.get_setting('current_host', channel=channel, default=''): domain = ''
                if not is_server_enabled(i.server, domain=domain): continue
            servers_list_alt.append(i)
        servers_list = servers_list_alt[:]

    if servers_list and config.get_setting('filter_servers'):
        if isinstance(servers_list[0], Item):
            servers_list_filter = [x for x in servers_list if not config.get_setting("black_list", server=x.server)]
        else:
            servers_list_filter = [x for x in servers_list if not config.get_setting("black_list", server=x)]

        # Si no hay enlaces despues de filtrarlos
        if servers_list_filter or not dialog_yesno(config.get_localized_string(60000),
                                                   config.get_localized_string(60010),
                                                   config.get_localized_string(70281)):
            servers_list = servers_list_filter
    
    if config.get_setting("favorites_servers") == True:
        servers_list = sort_servers(servers_list)
    
    return servers_list

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Comprobación de enlaces
# -----------------------

def check_list_links(itemlist, numero='', timeout=3):
    """
    Comprueba una lista de enlaces a videos y la devuelve modificando el titulo con la verificacion.
    El parámetro numero indica cuantos enlaces hay que verificar (0:5, 1:10, 2:15, 3:20)
    El parámetro timeout indica un tope de espera para descargar la página
    """
    numero = ((int(numero) + 1) * 5) if numero != '' else 10
    for it in itemlist:
        if numero > 0 and it.server != '' and it.url != '':
            verificacion = check_video_link(it.url, it.server, timeout)
            it.title = verificacion + ', ' + it.title.strip()
            it.alive = verificacion
            numero -= 1
    return itemlist

def check_video_link(url, server, timeout=3):
    """
    Comprueba si el enlace a un video es valido y devuelve un string de 2 posiciones con la verificacion.
    :param url, server: Link y servidor
    :return: str(2) '??':No se ha podido comprobar. 'Ok':Parece que el link funciona. 'NO':Parece que no funciona.
    """
    from core import httptools
    
    try:
        server_module = __import__('servers.%s' % server, None, None, ["servers.%s" % server])
    except:
        server_module = None
        logger.info("[check_video_link] No se puede importar el servidor! %s" % server)
        return "??"
        
    if hasattr(server_module, 'test_video_exists'):
        ant_timeout = httptools.HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT
        httptools.HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = timeout  # Limitar tiempo de descarga
        try:
            video_exists, message = server_module.test_video_exists(page_url=url)
            if not video_exists:
                logger.info("[check_video_link] No existe! %s %s %s" % (message, server, url))
                resultado = "[COLOR red][B]NO[/B][/COLOR]"
            else:
                logger.info("[check_video_link] comprobacion OK %s %s" % (server, url))
                resultado = "[COLOR green][B]OK[/B][/COLOR]"
        except:
            logger.info("[check_video_link] No se puede comprobar ahora! %s %s" % (server, url))
            resultado = "??"
            logger.error(traceback.format_exc())

        finally:
            httptools.HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = ant_timeout  # Restaurar tiempo de descarga
            return resultado

    logger.info("[check_video_link] No hay test_video_exists para servidor: %s" % server)
    return "??"


def get_proxy_list():
    global proxy_channel_bloqued
    
    import base64
    import ast
    
    if proxy_channel_bloqued:
        return
    
    try:
        proxy_channel_bloqued_str = base64.b64decode(config.get_setting('proxy_channel_bloqued')).decode('utf-8')
        proxy_channel_bloqued = ast.literal_eval(proxy_channel_bloqued_str)
    except Exception:
        return
