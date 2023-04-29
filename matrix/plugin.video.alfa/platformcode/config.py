# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Parámetros de configuración (kodi)
# ------------------------------------------------------------

# from builtins import str
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import os
import re
import time
import json
import threading
import traceback

import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui

PLUGIN_NAME = "alfa"
DEBUG = False
DEBUG_JSON = DEBUG or False
GLOBAL_SEARCH_CANCELLED = False
BTDIGG_URL = 'https://btdig.com/'
BTDIGG_LABEL = ' [COLOR limegreen]BT[/COLOR][COLOR red]Digg[/COLOR]'
BTDIGG_LABEL_B = '[B][COLOR limegreen]BT[/COLOR][COLOR red]Digg[/COLOR][/B] '
BTDIGG_POST = '[B]Canal potenciado con [COLOR limegreen]BT[/COLOR][COLOR red]Digg[/COLOR][/B]\n\n'

__settings__ = xbmcaddon.Addon(id="plugin.video.{}".format(PLUGIN_NAME))
__language__ = __settings__.getLocalizedString

""" CACHING ALFA PARAMETERS """
alfa_caching = False
alfa_system_platform = ''
alfa_kodi_platform = {}
alfa_settings = {}
alfa_channels = {}
alfa_servers = {}
alfa_servers_jsons = {}
alfa_no_caching_vars = []
window = None

try:
    window = xbmcgui.Window(10000)  # Home
    alfa_caching = bool(window.getProperty("alfa_caching"))
    if not alfa_caching:
        window.setProperty("alfa_system_platform", alfa_system_platform)
        window.setProperty("alfa_settings", json.dumps(alfa_settings))
        window.setProperty("alfa_channels", json.dumps(alfa_channels))
        window.setProperty("alfa_servers", json.dumps(alfa_servers))
        window.setProperty("alfa_servers_jsons", json.dumps(alfa_servers_jsons))
        window.setProperty("alfa_cookies", '')
        window.setProperty("alfa_CF_list", '')
        window.setProperty("alfa_videolab_movies_list", '')
        window.setProperty("alfa_videolab_series_list", '')
        window.setProperty("alfa_colors_file", json.dumps({}))
except:
    alfa_caching = False
    alfa_system_platform = ''
    alfa_kodi_platform = {}
    alfa_settings = {}
    alfa_channels = {}
    alfa_servers = {}
    alfa_servers_jsons = {}
    window = None
    from platformcode import logger
    logger.error(traceback.format_exc())


class CacheInit(xbmc.Monitor, threading.Thread):
    def __init__(self, *args, **kwargs):
        global window, __settings__, alfa_caching, alfa_system_platform, alfa_kodi_platform, \
                                     alfa_settings, alfa_channels, alfa_servers, alfa_servers_jsons
        xbmc.Monitor.__init__(self)
        threading.Thread.__init__(self)

        alfa_caching = __settings__.getSetting('caching')
        # Si no existe el archivo settings.xml, llama a Kodi .setSetting para forzar la creación de un archivo con valores por defecto
        if alfa_caching == 'true' or alfa_caching == None:
            alfa_caching = True
            __settings__.setSetting('caching', 'true')
            window.setProperty("alfa_caching", str(alfa_caching))
        else:
            alfa_caching = False
            __settings__.setSetting('caching', 'false')
            window.setProperty("alfa_caching", '')
        if alfa_caching:
            alfa_system_platform = get_system_platform()
            alfa_kodi_platform = get_platform(full_version=True)
            alfa_settings = get_all_settings_addon()
            alfa_channels = {}
            alfa_servers = {}
            alfa_servers_jsons = {}
            window.setProperty("alfa_system_platform", alfa_system_platform)
            window.setProperty("alfa_settings", json.dumps(alfa_settings))
            window.setProperty("alfa_channels", json.dumps(alfa_channels))
            window.setProperty("alfa_servers", json.dumps(alfa_servers))
            window.setProperty("alfa_servers_jsons", json.dumps(alfa_servers_jsons))
            window.setProperty("alfa_cookies", '')
            window.setProperty("alfa_CF_list", '')
            window.setProperty("alfa_videolab_movies_list", '')
            window.setProperty("alfa_videolab_series_list", '')
            window.setProperty("alfa_domain_web_list", '')
            styles_path = os.path.join(get_runtime_path(), 'resources', 'color_styles.json')
            with open(styles_path, "r") as cf:
                window.setProperty("alfa_colors_file", cf.read())
        window.setProperty("CAPTURE_THRU_BROWSER_in_use", '')


    def run(self):
        timer = 3600

        while not self.abortRequested():                                        # Loop infinito hasta cancelar Kodi
            window.setProperty("alfa_channels", json.dumps({}))                 # Limpiamos esta variable por si ha crecido mucho
            window.setProperty("alfa_servers", json.dumps({}))                  # Limpiamos esta variable por si ha crecido mucho
            if self.waitForAbort(timer):                                        # Espera el tiempo programado o hasta que cancele Kodi
                break                                                           # Cancelación de Kodi, salimos

    def onSettingsChanged(self):                                                # Si se modifican los ajuste de Alfa, se activa esta función
        global window, __settings__, alfa_settings, alfa_caching
        settings_pre = alfa_settings.copy() or None
        alfa_caching = __settings__.getSetting('caching')
        if alfa_caching == 'true' or alfa_caching == None:
            alfa_caching = True
            window.setProperty("alfa_caching", str(alfa_caching))
        else:
            alfa_caching = False
            window.setProperty("alfa_caching", "")

        return open_settings(settings_pre=settings_pre)


def cache_init():
    global alfa_caching, alfa_settings

    # Lanzamos en Servicio de actualización de FIXES
    try:
        monitor = CacheInit()                                                   # Creamos una clase con un Thread independiente, hasta el fin de Kodi
        monitor.start()
        time.sleep(2)                                                           # Dejamos terminar inicialización...
    except:                                                                     # Si hay problemas de threading, nos vamos
        alfa_caching = False
        alfa_settings = {}
        from platformcode import logger
        logger.error(traceback.format_exc())
        try:
            window.setProperty("alfa_caching", '')
            window.setProperty("alfa_settings", json.dumps(alfa_settings))
        except:
            pass


def cache_reset(action='OFF', label=''):
    try:
        global window, __settings__, alfa_caching, alfa_system_platform, alfa_kodi_platform, \
                                     alfa_settings, alfa_channels, alfa_servers, alfa_servers_jsons
        from platformcode import logger
        logger.info("action='%s', label='%s'" % (action, label), force=True)

        if not window: 
            return alfa_caching

        alfa_caching = bool(window.getProperty("alfa_caching"))

        if label:
            window.setProperty(label, '')

        else:
            if action == 'OFF':
                alfa_caching = False
                window.setProperty("alfa_caching", '')
            alfa_system_platform = ''
            alfa_settings = {}
            alfa_channels = {}
            alfa_servers = {}
            alfa_servers_jsons = {}
            window.setProperty("alfa_system_platform", alfa_system_platform)
            window.setProperty("alfa_settings", json.dumps(alfa_settings))
            window.setProperty("alfa_channels", json.dumps(alfa_channels))
            window.setProperty("alfa_servers", json.dumps(alfa_servers))
            window.setProperty("alfa_servers_jsons", json.dumps(alfa_servers_jsons))
            window.setProperty("alfa_cookies", '')
            window.setProperty("alfa_CF_list", '')
            window.setProperty("alfa_videolab_movies_list", '')
            window.setProperty("alfa_videolab_series_list", '')
            window.setProperty("alfa_colors_file", json.dumps({}))
            window.setProperty("CAPTURE_THRU_BROWSER_in_use", '')
            if action == 'ON': 
                alfa_caching = __settings__.getSetting('caching')
                if alfa_caching == 'true' or alfa_caching == None:
                    alfa_caching = True
                    window.setProperty("alfa_caching", str(alfa_caching))
                else:
                    alfa_caching = False
                    window.setProperty("alfa_caching", "")
    except:
        from platformcode import logger
        logger.error(traceback.format_exc())
    
    return alfa_caching


def translatePath(path):
    """
    Kodi 19: xbmc.translatePath is deprecated and might be removed in future kodi versions. Please use xbmcvfs.translatePath instead.
    @param path: cadena con path special://
    @type path: str
    @rtype: str
    @return: devuelve la cadena con el path real
    """
    if not path:
        return ''

    if PY3:
        if isinstance(path, bytes):
            path = path.decode('utf-8')
        path = xbmcvfs.translatePath(path)
        if isinstance(path, bytes):
            path = path.decode('utf-8')
    else:
        path = xbmc.translatePath(path)

    return path


def decode_var(value, trans_none='', decode_var_=True):
    """
    Convierte una cadena de texto, lista o dict al juego de caracteres utf-8
    eliminando los caracteres que no estén permitidos en utf-8
    @type: str, unicode, list de str o unicode, dict list de str o unicode o list
    @param value: puede ser una string o un list() o un dict{} con varios valores
    @rtype: str
    @return: valor codificado en UTF-8
    """
    if not decode_var_:
        return value
    
    if not value:
        if value is None: value = trans_none
        elif PY3 and value == b'': value = ''
        elif str(value) == '': value = ''
        return value
        
    if isinstance(value, (bool, int, float)):
        return value
    
    if isinstance(value, list):
        for x in range(len(value)):
            value[x] = decode_var(value[x], trans_none=trans_none)
    elif isinstance(value, tuple):
        value = tuple(decode_var(list(value), trans_none=trans_none))
    elif isinstance(value, dict):
        newdct = {}
        for key in value:
            value_unc = decode_var(value[key], trans_none=trans_none)
            key_unc = decode_var(key, trans_none=trans_none)
            newdct[key_unc] = value_unc
        return newdct
    elif isinstance(value, unicode):
        value = value.encode("utf8")
    elif not PY3 and isinstance(value, basestring):
        value = unicode(value, "utf8", "ignore").encode("utf8")
    
    if PY3 and isinstance(value, bytes):
        value = value.decode("utf8")

    return value


def get_addon_version(with_fix=True, from_xml=False):
    '''
    Devuelve el número de versión del addon, y opcionalmente número de fix si lo hay
    Con la opción from_xml se captura la versión desde addon.xml para obviar información erronea de la BD de addons de Kodi
    '''
    version = ''
    if from_xml:
        xml_file = os.path.join(get_runtime_path(), 'addon.xml')
        if os.path.exists(xml_file):
            xml = get_xml_content(xml_file)
            if xml:
                version = xml["addon"]["@version"]
                if version:
                    if with_fix:
                        return version + get_addon_version_fix()
                    else:
                        return version

    if not version:
        if with_fix:
            return __settings__.getAddonInfo('version') + get_addon_version_fix()
        else:
            return __settings__.getAddonInfo('version')


def get_addon_version_fix():
    try:
        last_fix_json = os.path.join(get_runtime_path(),
                                     'last_fix.json')  # información de la versión fixeada del usuario
        if os.path.exists(last_fix_json):
            with open(last_fix_json, 'rb') as f:
                data = f.read()
                if not PY3:
                    data = data.encode("utf-8", "ignore")
                elif PY3 and isinstance(data, (bytes, bytearray)):
                    data = "".join(chr(x) for x in data)
                f.close()
            fix = re.findall('"fix_version"\s*:\s*(\d+)', data)
            if fix:
                return '.fix%s' % fix[0]
    except:
        pass
    return ''


def get_versions_from_repo(urls=[], xml_repo='addons.xml'):
    '''
    Devuelve los números de versiones de los addons y repos incluidos en el Alfa Repo, así como la url desde donde se ha descargado
    '''
    from core import httptools
    from core import filetools

    versiones = {}
    if not urls:
        url_base = ['https://raw.githubusercontent.com/alfa-addon/alfa-repo/master/',
                    'https://gitlab.com/addon-alfa/alfa-repo/-/raw/master/']
    elif isinstance(urls, (list, tuple)):
        url_base = urls
    else:
        url_base = [urls]

    for url in url_base:
        response = httptools.downloadpage(url + xml_repo, timeout=5, ignore_response_code=True, alfa_s=True)
        if response.code != 200: continue
        try:
            import xmltodict
            xml = xmltodict.parse(response.data)
            for addon in xml["addons"]["addon"]:
                versiones[addon["@id"]] = addon["@version"]
            versiones['url'] = url
            response = httptools.downloadpage(url + xml_repo + '.md5', timeout=5, ignore_response_code=True,
                                              alfa_s=True)

            if response.code == 200 and response.data:
                versiones['repository.alfa-addon.md5'] = response.data

            for f in sorted(filetools.listdir("special://userdata/Database"), reverse=True):
                path_f = filetools.join("special://userdata/Database", f)
                if filetools.isfile(path_f) and f.lower().startswith('addons') and f.lower().endswith('.db'):
                    versiones['addons_db'] = path_f
                    break

            versiones = filetools.decode(versiones)
            break
        except:
            from platformcode import logger
            logger.error("Unable to download repo xml: %s" % versiones)
            versiones = {}
            logger.error(traceback.format_exc())
    else:
        from platformcode import logger
        logger.error("Unable to download repo xml: %s, %s" % (xml_repo, url_base))

    return versiones


def get_platform(full_version=False):
    global alfa_kodi_platform
    """
        Devuelve la información la version de xbmc o kodi sobre el que se ejecuta el plugin

        @param full_version: indica si queremos toda la informacion o no
        @type full_version: bool
        @rtype: str o dict
        @return: Si el paramentro full_version es True se retorna un diccionario con las siguientes claves:
            'num_version': (float) numero de version en formato XX.X
            'name_version': (str) nombre clave de cada version
            'video_db': (str) nombre del archivo que contiene la base de datos de videos
            'plaform': (str) esta compuesto por "kodi-" o "xbmc-" mas el nombre de la version segun corresponda.
        Si el parametro full_version es False (por defecto) se retorna el valor de la clave 'plaform' del diccionario anterior.
    """
    ret = {}
    codename = {"10": "dharma", "11": "eden", "12": "frodo",
                "13": "gotham", "14": "helix", "15": "isengard",
                "16": "jarvis", "17": "krypton", "18": "leia",
                "19": "matrix", "20": "nexus"}
    code_db = {'10': 'MyVideos37.db', '11': 'MyVideos60.db', '12': 'MyVideos75.db',
               '13': 'MyVideos78.db', '14': 'MyVideos90.db', '15': 'MyVideos93.db',
               '16': 'MyVideos99.db', '17': 'MyVideos107.db', '18': 'MyVideos116.db',
               '19': 'MyVideos119.db', '20': 'MyVideos121.db'}

    ret = alfa_kodi_platform.copy()
    if not ret:
        num_version = xbmc.getInfoLabel('System.BuildVersion')
        num_version = re.match("\d+\.\d+", num_version).group(0)
        ret['name_version'] = codename.get(num_version.split('.')[0], num_version)
        ret['video_db'] = code_db.get(num_version.split('.')[0], "")
        ret['num_version'] = float(num_version)
        if ret['num_version'] < 14:
            ret['platform'] = "xbmc-" + ret['name_version']
        else:
            ret['platform'] = "kodi-" + ret['name_version']

        alfa_kodi_platform = ret.copy()

    if full_version:
        return ret
    else:
        return ret['platform']


def is_xbmc():
    return True


def is_rooted(silent=False):
    res = get_setting('is_rooted_device', default='check')

    if res in ['rooted', 'no_rooted']:
        return res

    res = 'no_rooted'
    from platformcode import logger

    if xbmc.getCondVisibility("system.platform.windows"):
        res = 'no_rooted'

    elif xbmc.getCondVisibility("system.platform.android"):
        LIBTORRENT_MSG = get_setting("libtorrent_msg", server="torrent", default='')
        if not LIBTORRENT_MSG:
            import xbmcgui
            dialog = xbmcgui.Dialog()
            dialog.notification('ALFA: Verificando privilegios de Super-usuario', \
                                'Puede solicitarle permisos de Super usuario', time=10000)
            logger.info('### ALFA: Notificación enviada: privilegios de Super-usuario verificados', force=True)
            set_setting("libtorrent_msg", 'OK', server="torrent")

        for subcmd in ['-c', '-0']:
            command = ['su', subcmd, 'ls']
            output_cmd, error_cmd = su_command(command, silent=silent)
            if not error_cmd:
                res = 'rooted'
                break

    elif xbmc.getCondVisibility("system.platform.linux"):
        res = 'rooted'

    if not silent:
        if res == 'rooted':
            logger.info('Dispositivo Rooteado', force=True)
        else:
            logger.info('Dispositivo NO Rooteado', force=True)

    set_setting('is_rooted_device', res)
    return res


def su_command(command, silent=False):
    import subprocess

    try:
        if not silent:
            from platformcode import logger
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_cmd, error_cmd = p.communicate()
        if not error_cmd and not silent:
            logger.info('Command: %s' % str(command))
        if error_cmd and not silent:
            logger.info('Command ERROR: %s, %s' % (str(command), str(error_cmd)))

    except Exception as e:
        if not PY3:
            e = unicode(str(e), "utf8", errors="replace").encode("utf8")
        elif PY3 and isinstance(e, bytes):
            e = e.decode("utf8")
        error_cmd = e
        output_cmd = ''
        if not silent:
            logger.info('Command ERROR: %s, %s' % (str(command), str(error_cmd)))

    return output_cmd, error_cmd


def get_videolibrary_support():
    return True


def get_system_platform():
    global alfa_system_platform
    """
    Function: To recover the platform on which xbmc runs
    Credits to the original author (unknown)

    NOTE: Expensive operation, if reused, keep it in a temp var
    """
    if alfa_caching and not alfa_system_platform:
        alfa_system_platform = str(window.getProperty("alfa_system_platform"))
    if alfa_system_platform == "":

        if xbmc.getCondVisibility("System.Platform.Android"):
            platform = 'android'
        elif xbmc.getCondVisibility("System.Platform.Windows"):
            platform = 'windows'
        elif xbmc.getCondVisibility("System.Platform.UWP"):
            platform = 'windows'
        elif xbmc.getCondVisibility("System.Platform.Linux"):
            platform = 'linux'
        elif xbmc.getCondVisibility("system.platform.Linux.RaspberryPi"):
            platform = 'raspberry'
        elif xbmc.getCondVisibility("System.Platform.OSX"):
            platform = 'osx'
        elif xbmc.getCondVisibility("System.Platform.IOS"):
            platform = 'ios'
        elif xbmc.getCondVisibility("System.Platform.Darwin"):
            platform = 'darwin'
        elif xbmc.getCondVisibility("System.Platform.Xbox"):
            platform = 'xbox'
        elif xbmc.getCondVisibility("System.Platform.Tvos"):
            platform = 'tvos'
        elif xbmc.getCondVisibility("System.Platform.Atv2"):
            platform = 'atv2'
        else:
            platform = 'unknown'

        alfa_system_platform = platform
        if alfa_caching:
            window.setProperty("alfa_system_platform", alfa_system_platform)
            if DEBUG: from platformcode import logger; logger.error('SAVE Cache "alfa_system_platform": %s:' % (alfa_system_platform))

    return alfa_system_platform


def get_all_settings_addon(caching_var=True):
    global alfa_caching, alfa_settings
    # Si los settings ya están cacheados, se usan.  Si no, se cargan por el método tradicional
    if DEBUG: from platformcode import logger
    if alfa_caching and caching_var and json.loads(window.getProperty("alfa_settings")):
        if DEBUG: logger.error('READ ALL Cached Alfa SETTINGS')
        return json.loads(window.getProperty("alfa_settings")).copy()

    # Lee el archivo settings.xml y retorna un diccionario con {id: value}
    inpath = os.path.join(get_data_path(), "settings.xml")
    if not os.path.exists(inpath):
        # Si no existe el archivo settings.xml, llama a Kodi .setSetting para forzar la creación de un archivo con valores por defecto
        __settings__.setSetting('caching', 'true')
        time.sleep(1)
        if not os.path.exists(inpath):
            # Comprobamos si Kodi ha generado un archivo settings.xml accesible.  Si no es así, se cancela el cacheo y el menú de bienvenida (Apple TV)
            __settings__.setSetting('show_once', 'true')

    xml = get_xml_content(inpath)
    ret = {}

    if xml:
        tag = '#text' if "'@version': '2'" in str(xml) or "u'@version', u'2'" in str(xml) else '@value'
        for setting_ in xml['settings']['setting']:
            setting = decode_var(setting_)
            ret[setting['@id']] = get_setting_values(setting['@id'], setting.get(tag, ''), decode_var_=False)

        if DEBUG: logger.error('READ File ALL Alfa SETTINGS: alfa_caching: %s; caching_var: %s' % (alfa_caching, caching_var))
        alfa_settings = ret.copy()
        alfa_caching = False
        if alfa_settings: alfa_caching = alfa_settings.get('caching', True)
        if alfa_caching:
            window.setProperty("alfa_caching", str(alfa_caching))
        else:
            window.setProperty("alfa_caching", '')
        
    else:
        alfa_caching = False
        from platformcode import logger
        logger.error(traceback.format_exc())
        # Verificar si hay problemas de permisos de acceso a userdata/alfa
        from core.filetools import file_info, listdir, dirname
        logger.error("Error al leer settings.xml: %s, ### Folder-info: %s, ### File-info: %s" % \
                    (inpath, file_info(dirname(inpath)), listdir(dirname(inpath), file_inf=True)))
    
    if not alfa_caching:
        alfa_settings = {}
        alfa_kodi_platform = {}
        alfa_channels = {}
        alfa_servers = {}
        alfa_servers_jsons = {}
        window.setProperty("alfa_system_platform", "")
        window.setProperty("alfa_channels", json.dumps(alfa_channels))
        window.setProperty("alfa_servers", json.dumps(alfa_servers))
        window.setProperty("alfa_servers_jsons", json.dumps(alfa_servers_jsons))
        window.setProperty("alfa_cookies", '')
        window.setProperty("alfa_CF_list", '')
        window.setProperty("alfa_videolab_movies_list", '')
        window.setProperty("alfa_videolab_series_list", '')
        window.setProperty("alfa_colors_file", json.dumps({}))
        if DEBUG: logger.error('DROPING ALL Cached SETTINGS')
    
    window.setProperty("alfa_settings", json.dumps(alfa_settings))
    if DEBUG: logger.error('SAVE ALL Cached Alfa SETTINGS')

    return ret


def open_settings(settings_pre={}):
    global alfa_settings
    if isinstance(settings_pre, dict) and not settings_pre:
        settings_pre = get_all_settings_addon()
        __settings__.openSettings()
        time.sleep(1)
    alfa_settings = {}
    window.setProperty("alfa_settings", json.dumps(alfa_settings))
    settings_post = get_all_settings_addon(caching_var=False)
    if not settings_pre:
        settings_pre = settings_post.copy()

    # cb_validate_config (util para validar cambios realizados en el cuadro de dialogo)
    if settings_post:

        if settings_post.get('adult_aux_intro_password', None):
            # Hemos accedido a la seccion de Canales para adultos
            from platformcode import platformtools
            if 'adult_password' not in settings_pre:
                adult_password = set_setting('adult_password', '0000')
            else:
                adult_password = settings_pre['adult_password']

            if settings_post['adult_aux_intro_password'] == adult_password:
                # La contraseña de acceso es correcta
                set_setting("adult_mode", settings_post.get("adult_mode", 1))
                set_setting("adult_request_password", settings_post.get("adult_request_password", True))

                # Cambio de contraseña
                if settings_post.get('adult_aux_new_password1', ''):
                    if settings_post['adult_aux_new_password1'] == settings_post.get('adult_aux_new_password2', ''):
                        set_setting('adult_password', settings_post['adult_aux_new_password1'])

                    else:
                        platformtools.dialog_ok(get_localized_string(60305),
                                                get_localized_string(60306),
                                                get_localized_string(60307))

            else:
                platformtools.dialog_ok(get_localized_string(60305), get_localized_string(60309),
                                        get_localized_string(60310))

                # Deshacer cambios
                set_setting("adult_mode", settings_pre.get("adult_mode", 0))
                set_setting("adult_request_password", settings_pre.get("adult_request_password", True))

            # Borramos settings auxiliares
            set_setting('adult_aux_intro_password', '')
            set_setting('adult_aux_new_password1', '')
            set_setting('adult_aux_new_password2', '')

        # si se ha cambiado la ruta de la videoteca llamamos a comprobar directorios para que lo cree y pregunte
        # automaticamente si configurar la videoteca
        if settings_pre.get("videolibrarypath", None) != settings_post.get("videolibrarypath", None) or \
                settings_pre.get("folder_movies", None) != settings_post.get("folder_movies", None) or \
                settings_pre.get("folder_tvshows", None) != settings_post.get("folder_tvshows", None):
            verify_directories_created()

        else:
            # si se ha puesto que se quiere autoconfigurar y se había creado el directorio de la videoteca
            if not settings_pre.get("videolibrary_kodi", None) and settings_post.get("videolibrary_kodi", None) \
                    and settings_post.get("videolibrary_kodi_flag", None) == 1:
                from platformcode import xbmc_videolibrary
                xbmc_videolibrary.ask_set_content(2, silent=True)


def get_setting(name, channel="", server="", default=None, caching_var=True, debug=DEBUG):
    global alfa_settings
    """
    Retorna el valor de configuracion del parametro solicitado.

    Devuelve el valor del parametro 'name' en la configuracion global, en la configuracion propia del canal 'channel'
    o en la del servidor 'server'.

    Los parametros channel y server no deben usarse simultaneamente. Si se especifica el nombre del canal se devolvera
    el resultado de llamar a channeltools.get_channel_setting(name, channel, default). Si se especifica el nombre del
    servidor se devolvera el resultado de llamar a servertools.get_channel_setting(name, server, default). Si no se
    especifica ninguno de los anteriores se devolvera el valor del parametro en la configuracion global si existe o
    el valor default en caso contrario.

    @param name: nombre del parametro
    @type name: str
    @param channel: nombre del canal
    @type channel: str
    @param server: nombre del servidor
    @type server: str
    @param default: valor devuelto en caso de que no exista el parametro name
    @type default: any

    @return: El valor del parametro 'name'
    @rtype: any

    """

    # Specific channel setting
    if channel:
        # logger.info("get_setting reading channel setting '"+name+"' from channel json")
        from core import channeltools
        debug = False if debug == None else DEBUG_JSON if debug == DEBUG else debug
        value = channeltools.get_channel_setting(name, channel, default, caching_var=caching_var, debug=debug)
        # logger.info("get_setting -> '"+repr(value)+"'")
        return value

    # Specific server setting
    elif server:
        # logger.info("get_setting reading server setting '"+name+"' from server json")
        from core import servertools
        debug = False if debug == None else DEBUG_JSON if debug == DEBUG else debug
        value = servertools.get_server_setting(name, server, default, caching_var=caching_var, debug=debug)
        # logger.info("get_setting -> '"+repr(value)+"'")
        return value

    # Global setting
    else:
        debug = False if debug == None else DEBUG if not debug and DEBUG else debug
        if debug: from platformcode import logger

        if isinstance(caching_var, str):
            # Borrado de la cache y verificado/borrado de settings.xml
            if caching_var in ['reset', 'delete']:
                if window:
                    alfa_settings = json.loads(window.getProperty("alfa_settings"))
                    alfa_settings = {}
                    window.setProperty("alfa_settings", json.dumps(alfa_settings))
                    if debug: logger.error('DROPING Cached SETTINGS')
                if caching_var in ['delete']:
                    if debug: logger.error('DELETE Settings XML')
                    verify_settings_integrity()
                caching_var = False

        alfa_caching = bool(window.getProperty("alfa_caching"))
        if alfa_caching and caching_var:
            if not alfa_settings: alfa_settings = json.loads(window.getProperty("alfa_settings"))
            if debug: logger.error('READ Cached SETTING NAME: %s: %s:' \
                                                                    % (str(name).upper(), alfa_settings.get(name, default)))
            # Si el alfa_caching está activo, se usa la variable cargada.  Si no, se cargan por el método tradicional
            if not alfa_settings:
                get_all_settings_addon()
        if alfa_caching and caching_var and name not in str(alfa_no_caching_vars) \
                        and alfa_settings.get(name, None) != None:
            # Si el alfa_caching está activo y la variable cargada.  Si no, se cargan por el método tradicional
            return get_setting_values(name, alfa_settings.get(name, default))
        else:
            # logger.info("get_setting reading main setting '"+name+"'")
            value = __settings__.getSetting(name)
            if debug: logger.error('READ File (Cache: %s) SETTING NAME: %s: %s:' \
                                                                    % (str(alfa_caching and caching_var), str(name).upper(), value))
            if not value:
                return default
            return get_setting_values(name, value, decode_var_=False)


def get_setting_values(name, value, decode_var_=True):
    # Translate Path if start with "special://"
    if str(value).startswith("special://") and "videolibrarypath" not in name:
        value = translatePath(value)

    # hack para devolver el tipo correspondiente
    if value == "true" or value == True:
        return True
    elif value == "false" or value == False:
        return False
    else:
        # special case return as str
        if name in ["adult_password", "adult_aux_intro_password", "adult_aux_new_password1",
                    "adult_aux_new_password2"]:
            return decode_var(value, decode_var_)
        else:
            try:
                value = int(value)
                return value
            except ValueError:
                pass
            return decode_var(value, decode_var_)


def set_setting(name, value, channel="", server="", debug=DEBUG):
    global alfa_settings
    """
    Fija el valor de configuracion del parametro indicado.

    Establece 'value' como el valor del parametro 'name' en la configuracion global o en la configuracion propia del
    canal 'channel'.
    Devuelve el valor cambiado o None si la asignacion no se ha podido completar.

    Si se especifica el nombre del canal busca en la ruta \addon_data\plugin.video.alfa\settings_channels el
    archivo channel_data.json y establece el parametro 'name' al valor indicado por 'value'. Si el archivo
    channel_data.json no existe busca en la carpeta channels el archivo channel.json y crea un archivo channel_data.json
    antes de modificar el parametro 'name'.
    Si el parametro 'name' no existe lo añade, con su valor, al archivo correspondiente.


    Parametros:
    name -- nombre del parametro
    value -- valor del parametro
    channel [opcional] -- nombre del canal

    Retorna:
    'value' en caso de que se haya podido fijar el valor y None en caso contrario

    """
    value_init = value
    if channel:
        from core import channeltools
        debug = False if debug == None else DEBUG_JSON if not debug and DEBUG_JSON else debug
        return channeltools.set_channel_setting(name, value, channel, debug=debug)
    elif server:
        from core import servertools
        debug = False if debug == None else DEBUG_JSON if not debug and DEBUG_JSON else debug
        return servertools.set_server_setting(name, value, server, debug=debug)
    else:
        try:
            debug = False if debug == None else DEBUG if not debug and DEBUG else debug
            if debug: from platformcode import logger
            alfa_caching = bool(window.getProperty("alfa_caching"))
            if alfa_caching:
                if not alfa_settings: alfa_settings = json.loads(window.getProperty("alfa_settings"))
                if debug: logger.error('READ Cached SETTING NAME: %s: %s:' % (str(name).upper(), alfa_settings.get(name, None)))
                # Si el alfa_caching está activo, se usa la variable cargada.  Si no, se cargan por el método tradicional
                if not alfa_settings:
                    get_all_settings_addon()

            if isinstance(value, bool):
                if value:
                    value = "true"
                else:
                    value = "false"

            elif isinstance(value, (int, long)):
                value = str(value)

            __settings__.setSetting(name, value)
            if debug: logger.error('WRITE File (Cache; %s) SETTING NAME: %s: %s:' % (str(alfa_caching), str(name).upper(), value))

            if name == 'caching':
                if value_init:
                    window.setProperty("alfa_caching", str(True))
                    alfa_caching = True
                else:
                    window.setProperty("alfa_caching", '')
                    alfa_caching = False
                if not alfa_caching:
                    alfa_settings = {}
                    window.setProperty("alfa_settings", json.dumps(alfa_settings))
                    if debug: logger.error('DROPING Cached SETTINGS: %s' % (str(name).upper(), value_init))
            if alfa_caching and alfa_settings and alfa_settings.get(name, '') != value_init:
                alfa_settings[name] = value_init
                window.setProperty("alfa_settings", json.dumps(alfa_settings))
                if debug: logger.error('SAVE Cached SETTING NAME: %s: %s:' % (str(name).upper(), alfa_settings[name]))

        except Exception as ex:
            alfa_settings = {}
            window.setProperty("alfa_settings", json.dumps(alfa_settings))
            if debug: logger.error('DROPING Cached SETTINGS: %s' % str(name).upper())
            from platformcode import logger
            logger.error("Error al convertir '%s' no se guarda el valor \n%s" % (name, ex))
            return None

        return value


def get_kodi_setting(name, total=False):
    """
    Retorna el valor de configuracion del parametro solicitado.

    Devuelve el valor del parametro 'name' en la configuracion global de Kodi

    @param default: valor devuelto en caso de que no exista el parametro name
    @type default: any

    @return: El valor del parametro 'name'
    @rtype: any

    """

    # Global Kodi setting
    inpath = os.path.join(translatePath('special://masterprofile/'), "guisettings.xml")
    ret = {}

    xml = get_xml_content(inpath)
    
    if not xml:
        try:
            from platformcode import logger
            logger.error(traceback.format_exc())
            # Verificar si hay problemas de permisos de acceso a userdata
            from core.filetools import file_info, listdir, dirname
            logger.error("Error al leer guisettings.xml: %s, ### Folder-info: %s, ### File-info: %s" % \
                         (inpath, file_info(dirname(inpath)), listdir(dirname(inpath), file_inf=True)))
        except:
            pass

    else:
        try:
            if "'@version': '2'" in str(xml) or "u'@version', u'2'" in str(xml):
                for setting in xml['settings']['setting']:
                    ret[setting['@id']] = get_setting_values(setting['@id'], setting.get('#text', ''), decode_var_=False)
                    if setting['@id'] == name and not total:
                        return ret[setting['@id']]
            else:
                # Kodi <= 17
                sub_setting = name.split('.')[0]
                name_setting = name.split('.')[1]
                for setting in xml['settings'][sub_setting].items():
                    value = decode_var(setting)
                    key = '%s.%s' % (sub_setting, value[0])
                    if isinstance(value[1], dict):
                        ret[key] = get_setting_values(name_setting, value[1].get('#text', ''), decode_var_=False)
                    else:
                        ret[key] = get_setting_values(name_setting, value[1], decode_var_=False)
                    if value[0] == name_setting and not total:
                        return ret[key]

        except:
            from platformcode import logger
            logger.error(traceback.format_exc())
            # Verificar si hay problemas de permisos de acceso a userdata
            logger.error("Error al leer Guisettings.xml: %s; XML: %s" % (inpath, str(xml)))

    if not total:
        return None
    else:
        return ret


def get_localized_string(code):
    dev = __language__(code)

    try:
        # Unicode to utf8
        if isinstance(dev, unicode):
            dev = dev.encode("utf8")
            if PY3: dev = dev.decode("utf8")

        # All encodings to utf8
        elif not PY3 and isinstance(dev, str):
            dev = unicode(dev, "utf8", errors="replace").encode("utf8")

        # Bytes encodings to utf8
        elif PY3 and isinstance(dev, bytes):
            dev = dev.decode("utf8")
    except:
        pass

    return dev


def get_localized_category(categ):
    categories = {'movie': get_localized_string(30122), 'tvshow': get_localized_string(30123),
                  'anime': get_localized_string(30124), 'documentary': get_localized_string(30125),
                  'vos': get_localized_string(30136), 'adult': get_localized_string(30126),
                  'direct': get_localized_string(30137), 'torrent': get_localized_string(70015),
                  'sport': 'Deportes'}
    return categories[categ] if categ in categories else categ


def get_videolibrary_config_path():
    value = get_setting("videolibrarypath")
    return value


def get_videolibrary_path():
    return translatePath(get_videolibrary_config_path())


def get_temp_file(filename):
    temp = translatePath(os.path.join("special://temp/", filename))
    if (temp.endswith('/') or temp.endswith('\\')) and not os.path.exists(temp):
        os.makedirs(temp)
    return temp


def get_runtime_path():
    return translatePath(__settings__.getAddonInfo('Path'))


def get_data_path():
    dev = translatePath(__settings__.getAddonInfo('Profile'))

    # Crea el directorio si no existe
    if not os.path.exists(dev):
        os.makedirs(dev)

    return dev


def get_icon():
    return translatePath(__settings__.getAddonInfo('icon'))


def get_fanart():
    return translatePath(__settings__.getAddonInfo('fanart'))


def get_cookie_data():
    import os
    ficherocookies = os.path.join(get_data_path(), 'cookies.dat')

    with open(ficherocookies, 'r') as cookiedatafile:
        cookiedata = cookiedatafile.read()

    return cookiedata


def verify_directories_created():
    """
    Test if all the required directories are created
    """
    from platformcode import logger
    from core import filetools
    from platformcode import xbmc_videolibrary

    logger.info()
    time.sleep(1)

    config_paths = [["videolibrarypath", "videolibrary"],
                    ["downloadpath", "downloads"],
                    ["downloadlistpath", "downloads/list"],
                    ["settings_path", "settings_channels"]]

    for path, default in config_paths:
        saved_path = get_setting(path)

        # videoteca
        if path == "videolibrarypath":
            if not saved_path:
                saved_path = xbmc_videolibrary.search_library_path()
                if saved_path:
                    set_setting(path, saved_path)

        if not saved_path:
            saved_path = "special://profile/addon_data/plugin.video." + PLUGIN_NAME + "/" + default
            set_setting(path, saved_path)

        saved_path = translatePath(saved_path)
        if not filetools.exists(saved_path):
            logger.debug("Creating %s: %s" % (path, saved_path))
            filetools.mkdir(saved_path)

    config_paths = [["folder_movies", "CINE"],
                    ["folder_tvshows", "SERIES"]]

    for path, default in config_paths:
        saved_path = get_setting(path)

        if not saved_path:
            saved_path = default
            set_setting(path, saved_path)

        content_path = filetools.join(get_videolibrary_path(), saved_path)
        if not filetools.exists(content_path):
            logger.debug("Creating %s: %s" % (path, content_path))

            # si se crea el directorio
            filetools.mkdir(content_path)

    try:
        # from core import scrapertools
        # Buscamos el archivo addon.xml del skin activo
        skindir = filetools.join("special://home", 'addons', xbmc.getSkinDir(), 'addon.xml')
        if not os.path.isdir(skindir): return  # No hace falta mostrar error en el log si no existe la carpeta
        # Extraemos el nombre de la carpeta de resolución por defecto
        folder = ""
        data = filetools.read(skindir)
        # res = scrapertools.find_multiple_matches(data, '(<res .*?>)')
        res = re.compile('(<res .*?>)', re.DOTALL).findall(data)
        for r in res:
            if 'default="true"' in r:
                # folder = scrapertools.find_single_match(r, 'folder="([^"]+)"')
                folder = re.search('folder="([^"]+)"', r).group(1)
                break

        # Comprobamos si existe en el addon y sino es así, la creamos
        default = filetools.join(get_runtime_path(), 'resources', 'skins', 'Default')
        if folder and not filetools.exists(filetools.join(default, folder)):
            filetools.mkdir(filetools.join(default, folder))

        # Copiamos el archivo a dicha carpeta desde la de 720p si éste no existe o si el tamaño es diferente
        if folder and folder != '720p':
            for root, folders, files in filetools.walk(filetools.join(default, '720p')):
                for f in files:
                    if not filetools.exists(filetools.join(default, folder, f)) or \
                            (filetools.getsize(filetools.join(default, folder, f)) !=
                             filetools.getsize(filetools.join(default, '720p', f))):
                        filetools.copy(filetools.join(default, '720p', f),
                                       filetools.join(default, folder, f),
                                       True)
    except:
        logger.error("Al comprobar o crear la carpeta de resolución")
        logger.error(traceback.format_exc())


def verify_settings_integrity():
    # Comprobando la integridad de la estructura de Settings.xml
    global alfa_caching, alfa_settings
    
    try:
        from platformcode import logger, platformtools
        
        inpath = os.path.join(get_data_path(), "settings.xml")
        outpath = os.path.join(get_data_path(), "settings_bak.json")

        # Leemos el settings.xml
        try:
            with open(inpath, "rb") as infile:
                data = infile.read()
                if not PY3:
                    data = data.encode("utf-8", "ignore")
                elif PY3 and isinstance(data, (bytes, bytearray)):
                    data = "".join(chr(x) for x in data)
        except:
            data = ''
        
        if data:
            try:
                import xmltodict
                if xmltodict.parse(data):
                    # Si ya existe el settings_bak.json de una pasada anterior, lo restauramos
                    if os.path.exists(outpath):
                        return verify_settings_integrity_json(outpath)
                    logger.info('ALFA Settings.xml CORRECTO', force=True)
                    return True
                raise
            except:
                pass

        # Si ya existe el settings_bak.json de una pasada anterior, lo restauramos
        if not data and os.path.exists(outpath):
            return verify_settings_integrity_json(outpath)
        
        # Corrupción en Settings.xml: limpiamos y cancelamos la caché
        logger.error('CORRUPCIÓN en ALFA Settings.xml, regenerando: %s' % str(data))
        
        # Limpiamos la caché
        try:
            alfa_caching = False
            alfa_settings = {}
            window.setProperty("alfa_caching", '')
            window.setProperty("alfa_settings", json.dumps(alfa_settings))
        except:
            pass
        
        # Borramos el archivo Settings.xml de Alfa
        try:
            if os.path.exists(inpath):
                os.remove(inpath)
            if os.path.exists(outpath):
                os.remove(outpath)
        except:
            logger.error(traceback.format_exc())
            # Pedimos al usuario que reinstale Alfa
            
            platformtools.dialog_notification('Corrupción del archivo de Ajustes de Alfa', 
                                              'No podemos repararlo.  Desinstale Alfa por completo y reintálelo de nuevo', time=10000)
            return False
        
        # Salvamos para el nuevo settings.xml todas la estiquetas accesibles del anterior settings.xml corrupto
        try:
            matches = re.compile('<setting\s*id="([^"]*)"\s*value="([^"]*)"', re.DOTALL).findall(data)
            if not matches:
                matches = re.compile('<setting\s*id="([^"]+)"[^>]*>([^<]*)<\/', re.DOTALL).findall(data)
        except:
            matches = []
            logger.error(traceback.format_exc())
        ret = {}
        for _id, value in matches:
            ret[_id] = decode_var(value)
        try:
            ret['xml_repaired'] = str(int(ret['xml_repaired']) + 1)
        except:
            ret['xml_repaired'] = '1'
        try:
            data = json.dumps(ret)
            with open(outpath, "wb") as outfile:
                if PY3 and isinstance(data, str):
                    data = bytes(list(ord(x) for x in data))
                outfile.write(data)
        except:
            logger.error(traceback.format_exc())
            try:
                if os.path.exists(outpath):
                    os.remove(outpath)
            except:
                pass
            
            # Pedimos al usuario que revise los settings actuales
            platformtools.dialog_notification('Corrupción del archivo de Ajustes de Alfa', 
                                              'Introduzca de nuevo los ajustes de Alfa y reinicie Kodi', time=10000)
            time.sleep(1)
            __settings__.openSettings()
    except:
        logger.error(traceback.format_exc())
    
    return False


def verify_settings_integrity_json(outpath=None):
    # Migramos al nuevo settings.xml todas la estiquetas accesibles del anterior settings.xml corrupto
    global alfa_caching, alfa_settings
    
    try:
        from platformcode import logger, platformtools

        inpath = os.path.join(get_data_path(), "settings.xml")
        if not outpath:
            outpath = os.path.join(get_data_path(), "settings_bak.json")
        logger.info(outpath, force=True)
        if not os.path.exists(inpath):
            # Provocamos que Kodi genere el default settings.xml
            __settings__.setSetting('show_once', 'false')
            time.sleep(1)
            if not os.path.exists(inpath):
                logger.error('Falta settings.xml')
                return False
        if not os.path.exists(outpath):
            logger.error('Falta settings_bak.json')
            return False
        
        # Leemos el settings_bak.json
        try:
            with open(outpath, "rb") as outfile:
                data = outfile.read()
                if not PY3:
                    data = data.encode("utf-8", "ignore")
                elif PY3 and isinstance(data, (bytes, bytearray)):
                    data = "".join(chr(x) for x in data)
            ret = json.loads(data)
        except:
            ret = {}
            logger.error(traceback.format_exc())
        try:
            os.remove(outpath)
        except:
            logger.error(traceback.format_exc())

        # Actualizamos el settings.xml por defecto con los parámetros anteriores accesibles
        for _id, value in list(ret.items()):
            try:
                __settings__.setSetting(_id, str(value))
                logger.info('Recuperando "%s": "%s"' % (_id, str(value)), force=True)
            except:
                logger.error('Parámetro no rescatado "%s": "%s"' % (_id, str(value)))
        
        # Limpiamos la caché
        try:
            alfa_caching = False
            alfa_settings = {}
            window.setProperty("alfa_caching", '')
            window.setProperty("alfa_settings", json.dumps(alfa_settings))
        except:
            pass
        
        # Pedimos al usuario que revise los settings actuales
        platformtools.dialog_notification('Corrupción del archivo de Ajustes de Alfa', 
                                          'Verifique los ajustes de Alfa y reinicie Kodi', time=10000)
        time.sleep(1)
        __settings__.openSettings()
    except:
        logger.error(traceback.format_exc())
    
    return True


def get_xml_content(xml_file, content='', retry=False):
    '''
    Devuelve en formato DICT el contenido de la xml especificada en el path
    Crea o actualiza un xml desde formato DICT
    '''
    import xmltodict
    
    data = ''
    if not content:
        try:
            if os.path.exists(xml_file):
                with open(xml_file, 'rb') as f:
                    data = data_save = f.read()
                if not PY3:
                    data = data.encode("utf-8", "ignore")
                elif PY3 and isinstance(data, (bytes, bytearray)):
                    data = "".join(chr(x) for x in data)
                if not data and not retry:
                    from platformcode import logger
                    logger.debug('READ Lock error on %s?... Retrying' % xml_file)
                    time.sleep(1)
                    return get_xml_content(xml_file, retry=True)
                
                content = xmltodict.parse(data)
        except:
            content = {}
            from platformcode import logger
            logger.error('ERROR Parseando XML: %s; CONTENIDO: %s' % (xml_file, str(data) or str(data_save)))
            logger.error(traceback.format_exc())
    else:
        try:
            data = xmltodict.unparse(content, pretty=True)
            if PY3: data = bytes(list(ord(x) for x in data))
            with open(xml_file, 'wb') as f:
                f.write(data)
            content = data
        except:
            content = ''
            from platformcode import logger
            logger.error('ERROR UNparseando XML: %s; CONTENIDO: %s' % (xml_file, str(data)))
            logger.error(traceback.format_exc())

    return content


def importer(module):
    try:
        # from core import scrapertools, filetools
        from core import filetools
        path = os.path.join(xbmcaddon.Addon(module).getAddonInfo("path"))
        ad = filetools.read(filetools.join(path, "addon.xml"), silent=True)
        if ad:
            # lib_path = scrapertools.find_single_match(ad, 'library="([^"]+)"')
            lib_path = re.search('library="([^"]+)"', ad).group(1)
            sys.path.append(os.path.join(path, lib_path))
    except:
        pass
