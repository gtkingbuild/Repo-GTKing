# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# Updater (kodi)
# --------------------------------------------------------------------------------
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import os
import re
import time
import threading
import traceback
import base64
import xbmc

from platformcode import config
from platformcode import logger
from platformcode.platformtools import dialog_notification, is_playing
from platformcode import help_window
from core import httptools
from core import jsontools
from core import downloadtools
from core import scrapertools
from core import ziptools
from core.item import Item

CURRENT_VERSION = config.get_addon_version(with_fix=False, from_xml=True)
ADDON_UPDATES = 'https://extra.alfa-addon.com/addon_updates/'
ADDON_UPDATES_JSON = 'json/%s.json' % CURRENT_VERSION
ADDON_UPDATES_ZIP = 'zip/%s.zip' % CURRENT_VERSION
ADDON_UPDATES_BROADCAST = 'json/%s_broadcast.json' % CURRENT_VERSION

ALFA_DEPENDENCIES = 'alfa_dependencies.json'

ITEM = Item()
last_fix_json = os.path.join(config.get_runtime_path(), 'last_fix.json')        # información de la versión fixeada del usuario
timeout = 15
command = ''
last_id_old = 0

def check_addon_init():
    logger.info()

    # Subtarea de monitor.  Se activa cada X horas para comprobar si hay FIXES al addon
    def check_addon_monitor():
        logger.info()

        # Obtiene el íntervalo entre actualizaciones y si se quieren mensajes
        try:
            timer = int(config.get_setting('addon_update_timer',
                                           default=12))                         # Intervalo entre actualizaciones, en Ajustes de Alfa
            if timer <= 0:
                try:
                    user_type = base64.b64decode(config.get_setting('proxy_dev')).decode('utf-8')
                except Exception:
                    user_type = 'user'
                if user_type == 'user':
                    config.set_setting('addon_update_timer', 12)                # Si es usuario se fuerza a 12 horas
                    timer = 12
                else:
                    check_date_real()                                           # Obtiene la fecha real de un sistema externo
                    verify_emergency_update(proxy_only=True)
                    return                                                      # 0.  No se quieren actualizaciones
            verbose = config.get_setting('addon_update_message', default=False)
        except Exception:
            logger.error(traceback.format_exc())
            timer = 12  # Por defecto cada 12 horas
            verbose = False  # Por defecto, sin mensajes
        timer = timer * 3600  # Lo pasamos a segundos
        timer_emer = 30 * 60
        timer_blocks = int(timer / timer_emer)

        if config.get_platform(True)['num_version'] >= 14:                      # Si es Kodi, lanzamos el monitor
            monitor = xbmc.Monitor()
        else:  # Lanzamos solo una actualización y salimos

            check_addon_updates(verbose, monitor=False)                         # Lanza la actualización
            if verify_emergency_update():
                check_addon_updates(verbose)                                    # Lanza la actualización de emergencia

            return

        while not monitor.abortRequested():                                     # Loop infinito hasta cancelar Kodi
           
            check_addon_updates(verbose, monitor=monitor)                       # Lanza la actualización
            
            for x in range(timer_blocks + 1):
                if verify_emergency_update():
                    check_addon_updates(verbose)                                # Lanza la actualización de emergencia

                if monitor.waitForAbort(timer_emer):                            # Espera el tiempo programado o hasta que cancele Kodi
                    break                                                       # Cancelación de Kodi, salimos
            else:
                continue
            break

        check_update_to_others(verbose=False, app=False)                        # Actualizamos otros add-ons antes de irnos, para el siguiente inicio
        # Borra el .zip de instalación de Alfa de la carpeta Packages, por si está corrupto, y que así se pueda descargar de nuevo
        version = 'plugin.video.alfa-%s.zip' % CURRENT_VERSION
        packages_path = os.path.join(config.translatePath('special://home'), 'addons', 'packages', version)
        if os.path.exists(packages_path):
            os.remove(packages_path)
        return

    # Lanzamos en Servicio de actualización de FIXES
    try:
        from platformcode.custom_code import emergency_fixes
        emergency_fixes()                                                       # Fixes de emergencia que deben ejecutarse lo antes posible
        threading.Thread(target=check_addon_monitor).start()                    # Creamos un Thread independiente, hasta el fin de Kodi
        time.sleep(5)  # Dejamos terminar la primera verificación...
    except Exception:                                                                     # Si hay problemas de threading, se llama una sola vez
        try:
            timer = int(config.get_setting('addon_update_timer',
                                           default=12))                         # Intervalo entre actualizaciones, en Ajustes de Alfa
            if timer <= 0:
                try:
                    user_type = base64.b64decode(config.get_setting('proxy_dev')).decode('utf-8')
                except Exception:
                    user_type = 'user'
                if user_type == 'user':
                    config.set_setting('addon_update_timer', 12)                # Si es usuario se fuerza a 12 horas
                    timer = 12
                else:
                    verify_emergency_update(proxy_only=True)
                    return                                                      # 0.  No se quieren actualizaciones
            verbose = config.get_setting('addon_update_message', default=False)
        except Exception:
            verbose = False                                                     # Por defecto, sin mensajes
            pass
        check_addon_updates(verbose)                                            # Lanza la actualización, en Ajustes de Alfa
        time.sleep(5)                                                           # Dejamos terminar la primera verificación...

    return


def check_addon_updates(verbose=False, monitor=None):
    logger.info()
    from platformcode.custom_code import verify_script_alfa_update_helper

    # Forzamos la actualización de los repos para facilitar la actualización del addon Alfa
    xbmc.executebuiltin('UpdateAddonRepos')

    check_date_real()                                                           # Obtiene la fecha real de un sistema externo
    get_ua_list()

    try:
        help_window.show_info('broadcast', wait=False)                          # Muestra nuevo mensaje de broadcast, si está disponible

        # Se guarda en get_runtime_path en lugar de get_data_path para que se elimine al cambiar de versión
        try:
            localfilename = os.path.join(config.get_data_path(), 'temp_updates.zip')
            if os.path.exists(localfilename): os.remove(localfilename)
        except Exception:
            pass

        # Descargar json con las posibles actualizaciones
        # -----------------------------------------------
        data = {}
        url = ADDON_UPDATES
        resp = httptools.downloadpage(url + ADDON_UPDATES_JSON, timeout=timeout, ignore_response_code=True)

        if monitor and monitor.waitForAbort(0.1):
            return False

        if resp.sucess:
            data = resp.json
            if data:
                resp.sucess = verify_addon_version(CURRENT_VERSION, data.get('addon_version', ''))
            else:
                resp.sucess = False

        if not resp.sucess and str(resp.code) != '404':
            logger.info('ERROR en la descarga de actualizaciones: %s' % resp.code, force=True)
            if verbose:
                dialog_notification('Alfa: error en la actualización', 'Hay un error al descargar la actualización')
            if monitor is None and verify_emergency_update():
                return check_addon_updates(verbose, monitor=False)              # Lanza la actualización de emergencia
            return False

        # Comprobar que ha llegado un json válido
        # ---------------------------------------
        if not resp.data or 'Not found.' in str(resp.data) or not data or 'addon_version' not in data \
                                                           or 'fix_version' not in data or data.get('fix_version', 0) == 0:
            logger.info('No se encuentran actualizaciones de esta versión del addon', force=True)
            if verbose:
                dialog_notification('Alfa ya está actualizado', 'No hay ninguna actualización urgente')
            check_update_to_others(verbose=verbose)                             # Comprueba las actualuzaciones de otros productos
            verify_script_alfa_update_helper(emergency=False)                   # Verifica si hay una nueva versión de Alfa e instala
            return False

        # Comprobar versión que tiene instalada el usuario con versión de la actualización
        # --------------------------------------------------------------------------------
        current_version = CURRENT_VERSION
        if (not data.get('files', []) and verify_addon_version(current_version, data['addon_version'])) \
                                      or not verify_addon_version(current_version, data['addon_version']):
            logger.info('No hay actualizaciones para la versión %s del addon' % current_version, force=True)
            if verbose:
                dialog_notification('Alfa ya está actualizado', 'No hay ninguna actualización urgente')
            if monitor:
                check_update_to_others(verbose=verbose)                         # Comprueba las actualuzaciones de otros productos
                verify_script_alfa_update_helper(emergency=False)               # Verifica si hay una nueva versión de Alfa e instala
            return False

        data['addon_version'] = current_version
        lastfix = {}
        if os.path.exists(last_fix_json):
            try:
                with open(last_fix_json, "r") as lfj:
                    lastfix = jsontools.load(lfj.read())
                if verify_addon_version(lastfix['addon_version'], current_version) \
                                        and lastfix['fix_version'] >= data['fix_version']:
                    logger.info('Ya está actualizado con los últimos cambios. Versión %s.fix%d' % (
                                current_version, lastfix['fix_version'] or data['fix_version']), force=True)
                    if verbose:
                        dialog_notification('Alfa ya está actualizado', 'Versión %s.fix%d' \
                                            % (current_version, lastfix['fix_version'] or data['fix_version']))
                    if monitor:
                        check_update_to_others(verbose=verbose)                 # Comprueba las actualuzaciones de otros productos
                        verify_script_alfa_update_helper(emergency=False)       # Verifica si hay una nueva versión de Alfa e instala
                    return False
            except Exception:
                if lastfix:
                    logger.error('last_fix.json: ERROR en: ' + str(lastfix))
                else:
                    logger.error('last_fix.json: ERROR desconocido')
                lastfix = {}

        # Muestra y guarda .json de Broadcast
        # -----------------------------------
        if lastfix.get('broadcast_version'):
            data['broadcast_version'] = lastfix['broadcast_version']
            data['broadcast'] = lastfix.get('broadcast', '')

        resp_broadcast = httptools.downloadpage(url + ADDON_UPDATES_BROADCAST, timeout=timeout, ignore_response_code=True)

        if resp_broadcast.sucess and not 'login' in str(resp_broadcast.url) and not 'Not found.' in str(resp_broadcast.data):
            broadcast = resp_broadcast.json
            if broadcast and str(broadcast.get('fix_version', '')) != '0' \
                         and verify_addon_version(CURRENT_VERSION, broadcast.get('addon_version', '')):
                if broadcast.get('fix_version', '') and verify_addon_version(lastfix.get('broadcast_version', 0), broadcast.get('fix_version', '')):
                    if not lastfix.get('broadcast_version') or verify_addon_version(data['fix_version'], broadcast.get('fix_version', '')):
                        try:
                            help_window.show_info(0, wait=False, 
                                                  title="[COLOR limegreen]Alfa BROADCAST: [/COLOR][COLOR hotpink]Noticia IMPORTANTE[/COLOR]", 
                                                  text=str(broadcast.get('message', '')))
                            data['broadcast_version'] = data['fix_version']
                            data['broadcast'] = str(broadcast.get('message', ''))
                            logger.info('Mensaje de Broadcast enviado: %s ' % str(broadcast), force=True)
                        except Exception:
                            logger.error('ERROR en mensaje de Broadcast: %s ' % str(broadcast))
                    else:
                        logger.info('Broadcast existe pero no aplica: %s' % str(broadcast), force=True)
                else:
                    logger.info('Broadcast existe pero no aplica: %s' % str(broadcast), force=True)

        if monitor and monitor.waitForAbort(0.1):
            return False

        # Descargar zip con las actualizaciones
        # -------------------------------------
        if downloadtools.downloadfile(url + ADDON_UPDATES_ZIP, localfilename, silent=True) < 0:
            raise

        alfa_caching = config.cache_reset(action='OFF')                         # Reseteamos e inactivamos las caches de settings

        if monitor and monitor.waitForAbort(0.1):
            return False

        # Descomprimir zip dentro del addon
        # ---------------------------------
        try:
            unzipper = ziptools.ziptools()
            unzipper.extract(localfilename, config.get_runtime_path())
        except Exception:
            xbmc.executebuiltin('Extract("%s", "%s")' % (localfilename, config.get_runtime_path()))
            time.sleep(1)

        alfa_caching = config.cache_reset(action='ON')                          # Reseteamos y activamos las caches de settings

        # Borrar el zip descargado
        # ------------------------
        try:
            os.remove(localfilename)
        except Exception:
            pass

        if monitor and monitor.waitForAbort(0.1):
            return False

        # Si es PY3 se actualizan los módulos marshal
        # Se reinicia Proxytools
        try:
            if PY3:
                from platformcode.custom_code import marshal_check
                marshal_check()
            if not PY3:
                from core.proxytools import get_proxy_list
            else:
                from core.proxytools_py3 import get_proxy_list
            get_proxy_list(monitor_start=False)
        except Exception:
            logger.error('Error Marshalizando e iniciando Proxytools')
            logger.error(traceback.format_exc())

        # Guardar información de la versión fixeada
        # -----------------------------------------
        show_update_info(data, wait=False)
        new_fix_json = data.copy()

        last_id = 0
        if isinstance(data["files"], list):
            last_id = len(data["files"])
        elif isinstance(data["files"], dict):
            for k in data["files"].keys():
                if int(k) > last_id:
                    last_id = int(k)

        if 'files' in data: data.pop('files', None)
        data["last_id"] = last_id
        with open(last_fix_json, "w") as lfj:
            lfj.write(jsontools.dump(data))
        
        # Actualiza la versión del addon en las cabeceras
        try:
            httptools.__version = '%s.fix%d' % (data['addon_version'], data['fix_version'])
        except Exception:
            pass

        logger.info('Addon actualizado correctamente a %s.fix%d' % (data['addon_version'], data['fix_version']), force=True)

        if verbose:
            dialog_notification('Alfa actualizado a', 'Versión %s.fix%d' % (current_version, data['fix_version']))

        if monitor and monitor.waitForAbort(0.1):
            return False

        check_update_to_others(verbose=verbose)                                 # Comprueba las actualuzaciones de otros productos
        verify_script_alfa_update_helper(emergency=False)                       # Verifica si hay una nueva versión de Alfa e instala
        reset_fixed_services(new_fix_json)                                      # Si se actualizan los módulos de servicios se recargan
        return True

    except Exception:
        if monitor and monitor.waitForAbort(0.1):
            return False
        logger.error('Error al comprobar actualizaciones del addon!')
        logger.error(traceback.format_exc())
        if verbose:
            dialog_notification('Alfa actualizaciones', 'Error al comprobar actualizaciones')
        check_update_to_others(verbose=verbose)                                 # Comprueba las actualuzaciones de otros productos
        return False


def verify_addon_version(installed, fixes):
    logger.info('Installed: %s; Fixes: %s' % (str(installed), str(fixes)))
    
    resp = False
    
    try:
        if str(installed) and str(fixes):
            if str(installed) == str(fixes):
                return True
            
            installed = str(installed).split('.')
            fixes = str(fixes).split('.')
            
            for x, fix in enumerate(fixes):
                if str(fix) != '*' and not str(fix).startswith('[') and str(fix) != installed[x]:
                    break
                elif str(fix) == '*':
                    return True
                elif str(fix).startswith('['):
                    fix_list = fix.replace('[', '').replace(']', '').split(':')
                    if not fix_list[0] or fix_list[0] == '*' or int(fix_list[0]) <= int(installed[x]):
                        if not fix_list[1] or fix_list[1] == '*' or int(fix_list[1]) >= int(installed[x]):
                            return True
    except Exception:
        logger.error('Error al verificar versiones: Installed: %s; Fixes: %s' % (str(installed), str(fixes)))
        logger.error(traceback.format_exc())

    return resp


def verify_emergency_update(proxy_only=False):
    global command

    resp = False
    install = 0
    command = ''
    updates_url = ''
    github_url = ''
    proxyCF = ''
    proxySSL = ''
    
    try:
        if not PY3: from lib import alfaresolver
        else: from lib import alfaresolver_py3 as alfaresolver
        result = alfaresolver.frequency_count(ITEM, emergency=True)
        if result:
            for x, (fecha, addon_version, fix_version_, install, key) in enumerate(result):
                if verify_addon_version(CURRENT_VERSION, addon_version):

                    fix_version__ = fix_version_.split('|')
                    fix_version = fix_version__[0] or '*'
                    if len(fix_version__) >= 2:
                        updates_url = fix_version__[1]
                    if len(fix_version__) >= 3:
                        github_url = fix_version__[2]
                    if int(key) == 1:
                        if len(fix_version__) >= 4:
                            proxyCF = fix_version__[3]
                        if len(fix_version__) >= 5:
                            proxySSL = fix_version__[4]
                        parse_emergency_proxies(proxyCF, proxySSL)

                    if str(install).startswith('-') or proxy_only: break

                    if os.path.exists(last_fix_json):
                        with open(last_fix_json, "r") as lfj:
                            lastfix = jsontools.load(lfj.read())
                        if lastfix:
                            if not fix_version:
                                break
                            if verify_addon_version(lastfix.get('fix_version', '0'), fix_version):
                                resp = True
                                command = result[x]
                                github_url = parse_emergency_update(updates_url, github_url)
                                break
                        else:
                            resp = True
                    else:
                        resp = True

            if resp and install == 1:
                logger.info('REINSTALLING: %s' % str(command), force=True)
                from platformcode.custom_code import verify_script_alfa_update_helper
                verify_script_alfa_update_helper(emergency=True, github_url=github_url)
                resp = False
    except Exception:
        logger.error(traceback.format_exc())

    logger.info('%s %s' % (str('Proxy_only' if proxy_only else resp), str(command)), force=True)

    return resp


def parse_emergency_update(updates_url, github_url):
    logger.info('updates_url: %s; github_url: %s' % (updates_url, github_url))
    global ADDON_UPDATES, command

    url = ''
    
    try:
        if updates_url:
            updates_url = updates_url.split(',')
            for u_url_ in updates_url:
                u_url = u_url_.strip('[').strip(']').strip('{').strip('}').strip('"').strip("'").strip()
                resp = httptools.downloadpage(u_url, timeout=timeout, ignore_response_code=True, hide_infobox=True)
                if not resp.sucess or 'login' in str(resp.url):
                    continue
                ADDON_UPDATES = u_url
                logger.debug('ADDON_UPDATES: %s' % ADDON_UPDATES)
                break
        
        if github_url:
            github_url = github_url.split(',')
            for g_url_ in github_url:
                g_url = g_url_.strip('[').strip(']').strip('{').strip('}').strip('"').strip("'").strip()
                resp = httptools.downloadpage(g_url + 'addons.xml', timeout=timeout, ignore_response_code=True, hide_infobox=True)
                if not resp.sucess:
                    continue
                url = g_url
                logger.debug('Github_url: %s' % url)
                break
    except Exception:
        logger.error(traceback.format_exc())

    return url


def parse_emergency_proxies(proxyCF, proxySSL):

    try:
        if not PY3:
            from core.proxytools import set_proxy_lists
        else:
            from core.proxytools_py3 import set_proxy_lists
        set_proxy_lists(proxyCF, proxySSL)

    except Exception:
        logger.error(traceback.format_exc())


def check_update_to_others(verbose=False, app=True):
    logger.info()

    folder = ''
    folder_list = []

    try:
        list_folder = os.listdir(os.path.join(config.get_runtime_path(), 'tools'))
        for folder in sorted(list_folder):
            in_folder = os.path.join(config.get_runtime_path(), 'tools', folder)
            if not os.path.isdir(in_folder):
                continue
            if 'patch#' in folder:
                for folder_patch in sorted(os.listdir(in_folder)):
                    in_folder_patch = os.path.join(in_folder, folder_patch)
                    if not os.path.isdir(in_folder):
                        continue
                    folder_list += [os.path.join(folder, folder_patch)]
            else:
                folder_list += [folder]

        for folder in folder_list:
            in_folder = os.path.join(config.get_runtime_path(), 'tools', folder)
            out_folder = os.path.join(config.translatePath('special://home/addons'), os.path.split(in_folder)[1])
            if not os.path.exists(out_folder):
                continue
            if not check_dependencies(in_folder):
                continue

            logger.info('Updating: %s' % folder, force=True)
            copytree(in_folder, out_folder)
            if os.path.exists(os.path.join(out_folder, ALFA_DEPENDENCIES)):
                os.remove(os.path.join(out_folder, ALFA_DEPENDENCIES))

        config.verify_settings_integrity()
        from platformcode.custom_code import set_season_holidays
        set_season_holidays()

    except Exception:
        logger.error('Error al actualizar OTROS paquetes: %s' % folder)
        logger.error(traceback.format_exc())

    if app:
        try:
            from lib import alfa_assistant
            res, addonid = alfa_assistant.update_alfa_assistant(verbose=verbose)
        except Exception:
            logger.error("Alfa Assistant.  Error en actualización")
            logger.error(traceback.format_exc())


def check_dependencies(in_folder):
    """ Check is patch applies to current installed version
    Dependencies file is optional and named alfa_dependencies.json
    
    Optional paramenters:
    
    - patch_platforms: [list of patch-supportted platforms]
    - patch_python: python version i.e. Py2, Py3
    - patch_version_high: version number for patch to apply.  If patch_version_low param exists, it marks the highest version applicable
    - patch_version_low: marks the lowest version applicable for the patch.  It requires patch_version_high set
    
    Note:   version and sub-versions are separated by "." (slots).  Any version/sub-versions number can be a wild character "*"
            version/sub-versions slots number must be the same as the add-on to be patched
    
    """

    res = True
    dep_path = os.path.join(in_folder, ALFA_DEPENDENCIES)

    if not os.path.exists(dep_path):
        return res

    try:
        import xbmcaddon
        addon_name = os.path.split(in_folder)[1]
        __settings__ = xbmcaddon.Addon(id="{}".format(addon_name))
        addon_version = __settings__.getAddonInfo('version').split('.')
    except Exception:
        return False
    
    try:
        with open(dep_path, "r") as f:
            dep_json = jsontools.load(f.read())

        if dep_json.get('patch_platforms', []):
            # Check for PLATFORM
            if config.get_system_platform() not in dep_json['patch_platforms']:
                return False

        if dep_json.get('patch_python', '') and dep_json['patch_python'] in ['Py2', 'Py3']:
            # Check for PYTHON version
            if PY3 and dep_json['patch_python'] != 'Py3':
                return False
            if not PY3 and dep_json['patch_python'] == 'Py3':
                return False

        if dep_json.get('patch_version_high', []):
            # Check for Version or Vesion highest
            for x, ver in enumerate(addon_version):
                if dep_json['patch_version_high'].split('.')[x] == ver or dep_json['patch_version_high'].split('.')[x] == '*':
                    continue
                elif dep_json['patch_version_high'].split('.')[x] > ver and dep_json.get('patch_version_low', []):
                    break
                elif dep_json['patch_version_high'].split('.')[x] > ver and not dep_json.get('patch_version_low', []):
                    return False
                elif dep_json['patch_version_high'].split('.')[x] < ver:
                    return False
            else:
                return res

            # Check for Version lowest
            if dep_json.get('patch_version_low', []):
                for x, ver in enumerate(addon_version):
                    if dep_json['patch_version_low'].split('.')[x] == ver or dep_json['patch_version_low'].split('.')[x] == '*':
                        continue
                    elif dep_json['patch_version_low'].split('.')[x] > ver:
                        return False
                else:
                    return res

    except Exception:
        return False
        logger.error(traceback.format_exc())

    return res


def copytree(src, dst, symlinks=False, ignore=None):
    """Recursively copy a directory tree using copy2().

    *** Obtained from Kody Python 2.7 Shutil ***
    *** Ignores error if dst-dir exists ***

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    try:
        length = 16 * 1024
        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()

        if not os.path.exists(dst):
            os.makedirs(dst)

        for name in names:
            if name in ignored_names:
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)

            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                with open(srcname, 'rb') as fsrc:
                    with open(dstname, 'wb') as fdst:
                        while 1:
                            buf = fsrc.read(length)
                            if not buf:
                                break
                            fdst.write(buf)
    except Exception:
        logger.error(traceback.format_exc())


def get_ua_list():
    logger.info()
    
    try:
        url = "http://omahaproxy.appspot.com/all?csv=1"
        current_ver = config.get_setting("chrome_ua_version", default="").split(".")
        data = httptools.downloadpage(url, alfa_s=True, ignore_response_code=True).data
        
        new_ua_ver = scrapertools.find_single_match(data, "win64,stable,([^,]+),")
        if not new_ua_ver:
            return

        if not current_ver:
            config.set_setting("chrome_ua_version", new_ua_ver)
        else:
            for pos, val in enumerate(new_ua_ver.split('.')):
                if int(val) > int(current_ver[pos]):
                    config.set_setting("chrome_ua_version", new_ua_ver)
                    break
    except Exception:
        logger.error(traceback.format_exc())


def show_update_info(new_fix_json, wait=False):
    global last_id_old
    
    if not config.get_setting("show_fixes", default=True):
        return

    from core import channeltools

    try:
        fixed = list()
        old_fix = os.path.join(config.get_runtime_path(), 'last_fix.json')

        if isinstance(new_fix_json.get("files", {}), dict):
            if not os.path.exists(old_fix):
                for k, v in new_fix_json["files"].items():
                    if "channels" in v:
                        v = re.sub(r"\.py|\.json", "", v[1])
                        channel_parameters = channeltools.get_channel_parameters(v)
                        if not channel_parameters["channel"] or channel_parameters["adult"]:
                            continue
                        fixed.append("- %s\n" % v.title())
            else:
                with open(old_fix, "r") as f:
                    old_fix_json = jsontools.load(f.read())

                last_id_old = old_fix_json.get("last_id", 0)

                for k, v in new_fix_json["files"].items():
                    if int(k) > last_id_old and "channels" in v:
                        v = re.sub(r"\.py|\.json", "", v[1])
                        channel_parameters = channeltools.get_channel_parameters(v)
                        if not channel_parameters["channel"] or channel_parameters["adult"]:
                            continue
                        fixed.append("- %s\n" % v.title())
        elif isinstance(new_fix_json.get("files", []), list):
            if not os.path.exists(old_fix):
                for fix in new_fix_json["files"]:
                    if "channels" in fix:
                        fix = re.sub(r"\.py|\.json", "", fix[1])
                        channel_parameters = channeltools.get_channel_parameters(fix)
                        if not channel_parameters["channel"] or channel_parameters["adult"]:
                            continue
                        fixed.append("- %s\n" % fix.title())
            else:
                with open(old_fix, "r") as f:
                    old_fix_json = jsontools.load(f.read())

                last_id_old = old_fix_json.get("last_id", 0)
                if len(new_fix_json["files"]) > last_id_old:
                    for fix in new_fix_json["files"][last_id_old + 1:]:
                        if "channels" in fix:
                            fix = re.sub(r"\.py|\.json", "", fix[1])
                            channel_parameters = channeltools.get_channel_parameters(fix)
                            if not channel_parameters["channel"] or channel_parameters["adult"]:
                                continue
                            fixed.append("- %s\n" % fix.title())

        if fixed:
            fix_number = "%s - FIX %s" % (CURRENT_VERSION, new_fix_json["fix_version"])
            fixed_list = "".join(set(fixed))
            text = "[B]Se han aplicado correcciones a los siguientes canales:[/B] \n\n%s\n\n" % fixed_list
            text += "[I]Si no deseas ver esta ventana desactívala desde:[/I]\nConfiguración > Preferencias > General > Mostrar informe de correcciones"
            if not is_playing():
                help_window.show_info(0, wait=wait, title="Alfa - Correcciones (%s)" % fix_number, text=text)
    except Exception:
        logger.error(traceback.format_exc())


def reset_fixed_services(new_fix_json):
    global last_id_old

    services_list = ['videolibrary_service.py', 'generictools.py', 'custom_code.py', 
                     'config.py', 'httptools.py', 'filetools.py', 'updater.py']
    services_reload = []

    try:
        if isinstance(new_fix_json.get("files", {}), dict) and new_fix_json.get("files", {}):

            for k, fix in new_fix_json["files"].items():
                if int(k) > last_id_old and fix[1] in services_list:
                    fix[1] = re.sub(r"\.py|\.json", "", fix[1])
                    services_reload.append([fix[0], fix[1]])

        elif isinstance(new_fix_json.get("files", []), list) and new_fix_json.get("files", []):

            if len(new_fix_json["files"]) > last_id_old:
                for fix in new_fix_json["files"][last_id_old + 1:]:
                    if fix[1] in services_list:
                        fix[1] = re.sub(r"\.py|\.json", "", fix[1])
                        services_reload.append([fix[0], fix[1]])

        if services_reload:
            import importlib
            logger.info('Reseting Services: %s' % services_reload, force=True)

            for folder, service in services_reload:
                function = __import__('%s.%s' % (folder, service), None, None, ["%s.%s" % (folder, service)])
                importlib.reload(function)

    except Exception:
        logger.error(traceback.format_exc())


def check_date_real():
    import datetime
    
    try:
        pages = ['https://worldtimeapi.org/api/ip', 'https://timeapi.io/api/Time/current/zone?timeZone=Europe/Madrid']
        kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
                  'alfa_s': True, 'timeout': 5, 'cf_assistant': False}
        
        dia_hoy = datetime.date.today()
        fecha_int = ''
        
        for page in pages:
            try:
                resp = httptools.downloadpage(page, **kwargs)
                if resp.sucess:
                    fecha_int = resp.json.get('datetime', '')[:10] or resp.json.get('dateTime', '')[:10] \
                                                                   or resp.json.get('currentDateTime', '')[:10]
                    if not fecha_int: continue
                    config.set_setting('date_real', fecha_int)
                    break
                else:
                    logger.debug('ERROR al obtener la Fecha REAL: %s: %s' % (page, str(resp.code)))
            except Exception:
                logger.error('ERROR al obtener la Fecha REAL: %s' % page)
        else:
            fecha = "%s-%s-%s" % (dia_hoy.year, dia_hoy.month, dia_hoy.day)
            config.set_setting('date_real', fecha)
            logger.error('ERROR al obtener la Fecha REAL en: %s; Fecha del SISTEMA: %s' % (pages, fecha))

        if fecha_int and len(fecha_int) >= 10:
            fecha_int_alt = fecha_int[:10].split('-')
            if (dia_hoy.year == int(fecha_int_alt[0]) or dia_hoy.year == int(fecha_int_alt[0])-1) \
                                and (dia_hoy.month == int(fecha_int_alt[1]) or int(fecha_int_alt[1])-1 == 0) \
                                and (dia_hoy.day == int(fecha_int_alt[2])-1 or int(fecha_int_alt[2])-1 == 0):
                fecha = "%s-%s-%s" % (dia_hoy.year, dia_hoy.month, dia_hoy.day)
                config.set_setting('date_real', fecha)
                logger.info('Fecha REAL (del SISTEMA): %s' % fecha, force=True)
            else:
                logger.info('Fecha REAL (de la WEB): %s' % fecha_int, force=True)
    except Exception:
        logger.error(traceback.format_exc())