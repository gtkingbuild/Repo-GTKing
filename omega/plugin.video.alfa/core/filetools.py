# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# filetools
# Gestion de archivos con discriminación xbmcvfs/samba/local
# ------------------------------------------------------------

from __future__ import division
#from builtins import str
from builtins import range
from past.utils import old_div
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; basestring = str

import os
import re
import traceback

from core.scrapertools import find_single_match
from core.item import Item
from platformcode import logger, config

platform = config.get_system_platform()

if config.is_xbmc():
    KODI = True
    import xbmc
else:
    KODI = False

xbmc_vfs = True                                                 # False para desactivar XbmcVFS, True para activar
if xbmc_vfs:
    try:
        import xbmcvfs
        if not PY3:
            reload(sys)                                         ### Workoround Python 2
            sys.setdefaultencoding('utf-8')                     # xbmcvfs degrada el valor de defaultencoding.  Se reestablece
        xbmc_vfs = True
    except:
        xbmc_vfs = False

samba = None
if not xbmc_vfs:
    if PY3:
        from lib.sambatools_py3 import libsmb as samba
    else:
        from lib.sambatools_py2 import libsmb as samba
        reload(sys)                                             ### Workoround Python 2
        sys.setdefaultencoding('utf-8')                         # Samba degrada el valor de defaultencoding.  Se reestablece

# Windows es "mbcs" linux, osx, android es "utf8"
if not PY3 and platform in ['windows', 'xbox']:
    fs_encoding = ""
else:
    fs_encoding = "utf-8"


def validate_path(path, replacement='', trans_none=''):
    """
    Reemplaza o elimina cáracteres no permitidos
    @param path: cadena a validar
    @type path: str
    @rtype: str
    @return: devuelve la cadena sin los caracteres no permitidos
    """
    if not path or not isinstance(path, (unicode, basestring, bytes)):
        if path is None: path = trans_none

    pattern = "[:\*\?<>\|\\/]"
    pattern_url = "[:\*\?<>\|]"
    if find_single_match(path, '(^\w+:\/\/)'):
        protocolo = find_single_match(path, '(^\w+:\/\/)')
        parts = re.split(r'^\w+:\/\/(.+?)/(.+)', path)[1:3]
        parts[1] = parts[1].replace("\\", "/")
        return '{}{}/{}'.format(protocolo, parts[0], re.sub(pattern_url, replacement, parts[1]))

    else:
        if path.find(":\\") == 1:
            unidad = path[0:3]
            path = path[2:]
        else:
            unidad = ""

        return '{}{}'.format(unidad, re.sub(pattern, replacement, path))


def translatePath(path, trans_none=''):
    """
    Kodi 19: xbmc.translatePath is deprecated and might be removed in future kodi versions. Please use xbmcvfs.translatePath instead.
    @param path: cadena con path special://
    @type path: str
    @rtype: str
    @return: devuelve la cadena con el path real
    """
    if not path or not isinstance(path, (unicode, basestring, bytes)):
        if path is None: path = trans_none
        return path

    if PY3 and xbmc_vfs:
        if PY3 and isinstance(path, bytes):
            path = path.decode(fs_encoding)
        path = xbmcvfs.translatePath(path)
        if isinstance(path, bytes):
            path = path.decode(fs_encoding)

    elif KODI:
        path = xbmc.translatePath(path)

    return path


def makeLegalFilename(path, trans_none=''):
    """
    Kodi 19: xbmc.makeLegalFilename is deprecated and might be removed in future kodi versions. Please use xbmcvfs.makeLegalFilename instead.
    @param path: cadena a convertir platform specific
    @type path: str
    @rtype: str
    @return: devuelve la cadena con el path ajustado
    """
    if not path or not isinstance(path, (unicode, basestring, bytes)):
        if path is None: path = trans_none
        return path

    if PY3 and xbmc_vfs:
        if PY3 and isinstance(path, bytes):
            path = path.decode(fs_encoding)
        path = xbmcvfs.makeLegalFilename(path)
        if isinstance(path, bytes):
            path = path.decode(fs_encoding)

    elif KODI and not PY3:
        path = xbmc.makeLegalFilename(path)
        
    return path


def validatePath(path, trans_none=''):
    """
    Kodi 19: xbmc.validatePath is deprecated and might be removed in future kodi versions. Please use xbmcvfs.validatePath instead.
    @param path: cadena a convertir platform specific
    @type path: str
    @rtype: str
    @return: devuelve la cadena con el path ajustado
    """
    if not path or not isinstance(path, (unicode, basestring, bytes)):
        if path is None: path = trans_none
        return path

    if PY3 and xbmc_vfs:
        if PY3 and isinstance(path, bytes):
            path = path.decode(fs_encoding)
        path = xbmcvfs.validatePath(path)
        if isinstance(path, bytes):
            path = path.decode(fs_encoding)
    
    elif KODI:
        path = xbmc.validatePath(path)
        
    return path


def encode(path, _samba=False, trans_none=''):
    """
    Codifica una ruta según el sistema operativo que estemos utilizando.
    El argumento path tiene que estar codificado en utf-8
    @type path unicode o str con codificación utf-8
    @param path parámetro a codificar
    @type _samba bool
    @para _samba si la ruta es samba o no
    @rtype: str
    @return ruta codificada en juego de caracteres del sistema o utf-8 si samba
    """
    if not path or isinstance(path, (list, dict)):
        if path is None: path = trans_none
        return path

    if isinstance(path, (unicode, basestring, bytes)) and "special://" in path:
        path = translatePath(path)
    
    if not isinstance(path, unicode):
        path = unicode(path, "utf-8", "ignore")

    if find_single_match(path, '(^\w+:\/\/)') or _samba:
        path = path.encode("utf-8", "ignore")
    else:
        if fs_encoding:
            path = path.encode(fs_encoding, "ignore")
            
    if PY3 and isinstance(path, bytes):
        path = path.decode(fs_encoding)

    return path


def decode(path, trans_none=''):
    """
    Convierte una cadena de texto, lista o dict al juego de caracteres utf-8
    eliminando los caracteres que no estén permitidos en utf-8
    @type: str, unicode, list de str o unicode, dict list de str o unicode o list
    @param path: puede ser una ruta o un list() o un dict{} con varias rutas
    @rtype: str
    @return: ruta codificado en UTF-8
    """
    if not path:
        if path is None: path = trans_none
        elif PY3 and path == b'': path = ''
        elif str(path) == '': path = ''
        return path
        
    if PY3 and isinstance(path, bytes) and b"special://" in path:
        path = translatePath(path)
    elif not PY3 and isinstance(path, (unicode, basestring, bytes)) and "special://" in path:
        path = translatePath(path)
    
    if isinstance(path, list):
        for x in range(len(path)):
            path[x] = decode(path[x], trans_none=trans_none)
    elif isinstance(path, tuple):
        path = tuple(decode(list(path), trans_none=trans_none))
    elif isinstance(path, dict):
        newdct = {}
        for key in path:
            value_unc = decode(path[key], trans_none=trans_none)
            key_unc = decode(key, trans_none=trans_none)
            newdct[key_unc] = value_unc
        return newdct
    elif isinstance(path, unicode):
        path = path.encode("utf8")
    elif not PY3 and isinstance(path, basestring):
        path = unicode(path, "utf8", "ignore").encode("utf8")
    
    if PY3 and isinstance(path, bytes):
        path = path.decode(fs_encoding)

    return path


def read(path, linea_inicio=0, total_lineas=None, whence=0, mode='r', silent=False, vfs=True):
    """
    Lee el contenido de un archivo y devuelve los datos
    @param path: ruta del fichero
    @type path: str
    @param linea_inicio: primera linea a leer del fichero
    @type linea_inicio: int positivo
    @param total_lineas: numero maximo de lineas a leer. Si es None o superior al total de lineas se leera el
        fichero hasta el final.
    @type total_lineas: int positivo
    @rtype: str, bytes, bytesarray
    @return: datos que contiene el fichero
    """
    path = encode(path)
    try:
        mode_open = mode.replace('s', '')
        if not isinstance(linea_inicio, int):
            try:
                linea_inicio = int(linea_inicio)
            except:
                logger.error('Read: ERROR de linea_inicio: %s' % str(linea_inicio))
                linea_inicio = 0
        if total_lineas != None and not isinstance(total_lineas, int):
            try:
                total_lineas = int(total_lineas)
            except:
                logger.error('Read: ERROR de total_lineas: %s' % str(total_lineas))
                total_lineas = None
        
        if xbmc_vfs and vfs:
            if 'r' in mode and '+' in mode:
                mode = mode.replace('r', 'w').replace('+', '')
                mode_open = mode.replace('r', 'w').replace('+', '')
                logger.debug('Open MODE cambiado a: %s' % mode)
            if 'a' in mode:
                mode = mode.replace('a', 'w').replace('+', '')
                mode_open = mode.replace('a', 'w').replace('+', '')
                logger.debug('Open MODE cambiado a: %s' % mode)
                
            if not exists(path): 
                if not silent: logger.info('Path missing: ' + str(path), force=True)
                return False
            f = xbmcvfs.File(path, "rb")
            if linea_inicio > 0:
                if not isinstance(whence, int):
                    try:
                        whence = int(whence)
                    except:
                        if not silent: logger.info('Whence error: ' + str(whence) + ' in: ' + str(path), force=True)
                        f.close()
                        return False
                f.seek(linea_inicio, whence)
                logger.debug('POSICIÓN de comienzo de lectura, tell(): %s' % f.seek(0, 1))
            if total_lineas == None:
                total_lineas = 0
            if mode in ['r', 'ra']:
                try:
                    data = f.read(total_lineas)
                except Exception as e:
                    if "codec can't decode" in str(e):
                        mode = 'rbs'
                        f.seek(linea_inicio, whence)
                        logger.error(str(e) + '.  Intentaremos leerlo en "mode=rbs", bytes a string, el archivo: ' + str(path))
                    else:
                        raise Exception(e)
            if mode not in ['r', 'ra']:
                data = f.readBytes(total_lineas)
            f.close()
            if mode in ['r', 'ra']:
                return "".join(data)
            elif mode in ['rbs', 'rabs'] and isinstance(data, (bytes, bytearray)):
                return "".join(chr(x) for x in data)
            elif mode in ['rb', 'rab'] and isinstance(data, bytearray):
                return bytes(data)
            else:
                return data

        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            f = samba.smb_open(path, "rb")
            mode = 'rbs'
        
        elif PY3 and mode in ['r', 'ra']:
            f = open(path, mode_open, encoding=fs_encoding)
        else:
            f = open(path, mode_open)

        data = []
        for x, line in enumerate(f):
            if x < linea_inicio: continue
            if len(data) == total_lineas: break
            data.append(line)
        f.close()
    except:
        logger.error("ERROR al leer el archivo: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
        try:
            f.close()
        except:
            pass
        return False

    else:
        if not PY3 or mode in ['r', 'ra']:
            return "".join(data)
        elif mode in ['rbs', 'rabs'] and isinstance(data, (bytes, bytearray)):
            return "".join(chr(x) for x in data)
        elif mode in ['rbs', 'rabs'] and isinstance(data, (list)):
            return "".join(decode(data))
        else:
            return b"".join(data)


def write(path, data, mode="wb", silent=False, vfs=True, ch_mod=''):
    """
    Guarda los datos en un archivo
    @param path: ruta del archivo a guardar
    @type path: str
    @param data: datos a guardar
    @type data: str, bytes, bytesarray
    @rtype: bool
    @return: devuelve True si se ha escrito correctamente o False si ha dado un error
    """
    path = encode(path)
    try:
        mode_open = mode.replace('s', '')
        if xbmc_vfs and vfs:
            if 'r' in mode and '+' in mode:
                mode = mode.replace('r', 'w').replace('+', '')
                mode_open = mode.replace('r', 'w').replace('+', '')
                logger.debug('Open MODE cambiado a: %s' % mode)
            if 'a' in mode:
                mode = mode.replace('a', 'w').replace('+', '')
                mode_open = mode.replace('a', 'w').replace('+', '')
                logger.debug('Open MODE cambiado a: %s' % mode)
                
            if mode not in ['w', 'a'] and PY3 and isinstance(data, str):
                data = bytearray(list(ord(x) for x in data))
            elif isinstance(data, bytes):
                data = bytearray(data)
            f = xbmcvfs.File(path, mode_open)
            result = bool(f.write(data))
            f.close()
            if result and ch_mod:
                result = chmod(path, ch_mod, silent=silent)
            return result
        
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            f = samba.smb_open(path, "wb")
        
        elif PY3 and mode in ['w', 'a']:
            f = open(path, mode_open, encoding=fs_encoding)
        else:
            f = open(path, mode_open)
        
        if mode not in ['w', 'a'] and PY3 and isinstance(data, str):
            data = bytes(list(ord(x) for x in data))

        f.write(data)
        f.close()
    except:
        logger.error("ERROR al guardar el archivo: %s" % path)
        logger.error(traceback.format_exc())
        try:
            f.close()
        except:
            pass
        return False
    else:
        return True


def file_open(path, mode="r", silent=False, vfs=True):
    """
    Abre un archivo
    @param path: ruta
    @type path: str
    @rtype: str
    @return: objeto file
    """
    path = encode(path)
    try:
        mode = mode.replace('s', '')
        if xbmc_vfs and vfs:
            if 'r' in mode and '+' in mode:
                mode = mode.replace('r', 'w').replace('+', '')
                logger.debug('Open MODE cambiado a: %s' % mode)
            if 'a' in mode:
                mode = mode.replace('a', 'w').replace('+', '')
                logger.debug('Open MODE cambiado a: %s' % mode)
            return xbmcvfs.File(path, mode)
        
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            return samba.smb_open(path, mode)
        
        elif PY3 and 'b' not in mode:
            return open(path, mode, encoding=fs_encoding)
        else:
            return open(path, mode)
    
    except:
        logger.error("ERROR al abrir el archivo: %s, %s" % (path, mode))
        if not silent:
            logger.error(traceback.format_exc())
            from platformcode.platformtools import dialog_notification
            dialog_notification("Error al abrir", path)
        return False


def file_stat(path, silent=False, vfs=True):
    """
    Stat de un archivo
    @param path: ruta
    @type path: str
    @rtype: str
    @return: objeto file
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            if not exists(path): return False
            return xbmcvfs.Stat(path)
        raise
    except:
        logger.error("File_Stat no soportado: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
        return False
        

def file_info(path, silent=False, vfs=True):
    """
    Info de un archivo o carpeta
    @param path: ruta
    @type path: str
    @rtype: str
    @return: Info de un archivo o carpeta
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            if not exists(path): return False
            import datetime
            
            stat = xbmcvfs.Stat(path)

            # Diccionario de permisos y tipos de archivos
            dic_perm = {'7':'rwx', '6':'rw-', '5':'r-x', '4':'r--', '3':'-wx', '2':'-w-', '1':'--x', '0':'---'}
            dic_type = {'01':'-', '02':'l', '03':'m', '04':'d'}
            perm = str(oct(stat.st_mode()))                                     # Convertimos desde Octal los permisos y tipos de archivos
            if perm.startswith('0o'): perm = perm.replace('o', '')
            if perm.endswith('L'): perm = perm[:-1]
            file_type = dic_type.get(perm[:2], '')                              # Lo pasamos por diccionario de tipos de archivo
            perm = perm[-3:]
            perm = ''.join(dic_perm.get(x,x) for x in perm)                     # Lo pasamos por diccionario de permisos
            
            try:                                                                # Esta función NO está soportada en todas las plataformas
                import pwd
                uid = find_single_match(str(pwd.getpwuid(stat.st_uid())), "pw_name='([^']+)'")
                if not uid: uid = stat.st_uid()
                gid = find_single_match(str(pwd.getpwuid(stat.st_gid())), "pw_name='([^']+)'")
                if not gid: gid = stat.st_gid()
            except:
                uid = stat.st_uid()
                gid = stat.st_gid()
            
            try:                                                                # Puede haber errores en la fecha
                mod_time = stat.st_mtime()
                mod_time = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M')
            except:
                mod_time = '0000-00-00 00:00'                                   # Fecha en caso de error
            
            # Construimos la respuesta
            res = '%s%s  %s  %s  %s  %s  %s  %s' % (file_type, perm, stat.st_nlink(), uid, gid, stat.st_size(), mod_time, path)
            
            # Y la pasamos por encode, está en unicode en Py2.  En el caso de Windows con Py2 hay que hacer una verificación adicional
            res = encode(res)
            if not PY3 and isinstance(res, unicode):
                res = res.encode("utf-8", "ignore")
            return res
        raise
    except:
        logger.error("File_Stat no soportado: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
        return False


def chmod(path, ch_mod, su=False, silent=False):
    """
    Cambia los permisos de un archivo o carpeta en sistemas Linux y derivados
    @param path: ruta
    @type path: str
    @param ch_mod: permisos
    @type ch_mod: str
    @param su: super-user, con diferentes variantes según plataforma
    @type su: bool
    @rtype: str
    @return: File-Info de un archivo o carpeta
    """
    path = encode(path)
    res = False
    error_cmd = True
    
    if KODI and platform in ['windows', 'xbox']:
        if not silent:
            logger.info('Command ERROR: CHMOD no soportado en esta plataforma', force=True)
    else:
        try:
            import subprocess
            if not su:
                command = ['chmod', ch_mod, path]
                if not silent:
                    logger.info('Command: %s' % str(command), force=True)
                p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output_cmd, error_cmd = p.communicate()
            elif su and config.is_rooted(silent=True) == 'rooted':
                for subcmd in ['-c', '-0']:
                    for cmdtype in [['chmod', ch_mod, path], ['chmod %s %s' % (ch_mod, path)]]:
                        command = ['su', subcmd] + cmdtype
                        output_cmd, error_cmd = config.su_command(command, silent=silent)
                        if not error_cmd:
                            break
                    if not error_cmd:
                        break
                else:
                    raise
            
            if not silent and error_cmd:
                logger.error('Command ERROR: %s, %s' % (str(command), str(error_cmd)))
        except:
            if not silent:
                logger.error(traceback.format_exc())
            
    # Pedir file_info del archivo o carpeta
    res = file_info(path, silent=silent)
    if not silent:
        logger.info('File-stat: %s' % str(res), force=True)
    
    return res


def rename(path, new_name, silent=False, strict=False, vfs=True, ch_mod=''):
    """
    Renombra un archivo o carpeta
    @param path: ruta del fichero o carpeta a renombrar
    @type path: str
    @param new_name: nuevo nombre
    @type new_name: str
    @rtype: bool
    @return: devuelve False en caso de error
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            path_end = path
            if path_end.endswith('/') or path_end.endswith('\\'):
                path_end = path_end[:-1]
            dest = encode(join(dirname(path_end), new_name))
            result = bool(xbmcvfs.rename(path, dest))
            if not result and not strict:
                if not silent:
                    logger.error("ERROR al RENOMBRAR el archivo: %s.  Copiando y borrando" % path)
                result = bool(copy(path, dest, su=True))
                if not result:
                    return False
                xbmcvfs.delete(path)
            if result and ch_mod:
                result = chmod(dest, ch_mod, silent=silent)
            return result
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            new_name = encode(new_name, True)
            samba.rename(path, join(dirname(path), new_name))
        else:
            new_name = encode(new_name, False)
            os.rename(path, os.path.join(os.path.dirname(path), new_name))
    except:
        logger.error("ERROR al renombrar el archivo: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
            from platformcode.platformtools import dialog_notification
            dialog_notification("Error al renombrar", path)
        return False
    else:
        return True


def move(path, dest, silent=False, strict=False, vfs=True, ch_mod=''):
    """
    Mueve un archivo
    @param path: ruta del fichero a mover
    @type path: str
    @param dest: ruta donde mover
    @type dest: str
    @rtype: bool
    @return: devuelve False en caso de error
    """
    try:
        if xbmc_vfs and vfs:
            if not exists(path): return False
            path = encode(path)
            dest = encode(dest)
            result = bool(xbmcvfs.rename(path, dest))
            if not result and not strict:
                if not silent:
                    logger.error("ERROR al MOVER el archivo: %s.  Copiando y borrando" % path)
                result = bool(copy(path, dest, su=True))
                if not result:
                    return False
                xbmcvfs.delete(path)
            if result and ch_mod:
                result = chmod(dest, ch_mod, silent=silent)
            return result
        
        # samba/samba
        elif path.lower().startswith("smb://") or dest.lower().startswith("smb://"):
            if not samba: import_samba()
            dest = encode(dest, True)
            path = encode(path, True)
            samba.rename(path, dest)

        # local/local
        elif not path.lower().startswith("smb://") and not dest.lower().startswith("smb://"):
            dest = encode(dest)
            path = encode(path)
            os.rename(path, dest)
        # mixto En este caso se copia el archivo y luego se elimina el de origen
        else:
            if not silent:
                from platformcode.platformtools import dialog_progress
                dialogo = dialog_progress("Copiando archivo", "")
            return copy(path, dest) == True and remove(path) == True
    except:
        logger.error("ERROR al mover el archivo: %s a %s" % (path, dest))
        if not silent:
            logger.error(traceback.format_exc())
        return False
    else:
        return True


def copy(path, dest, silent=False, vfs=True, ch_mod='', su=False):
    """
    Copia un archivo o carpeta o arbol de carpetas
    @param path: ruta del fichero/carpeta a copiar
    @type path: str
    @param dest: ruta donde copiar
    @type dest: str
    @param silent: se muestra o no el cuadro de dialogo
    @type silent: bool
    @rtype: bool
    @return: devuelve False en caso de error
    """
    try:
        result = False
        if xbmc_vfs and vfs:
            path = encode(path)
            dest = encode(dest)
            if isdir(path):
                if not silent:
                    logger.info("Copiando carpetas %s a %s" % (path, dest), force=True)
                try:
                    import shutil
                    shutil.copytree(path, dest)
                    result = True
                except:
                    logger.error(traceback.format_exc())
                    logger.info("Copiando carpeta por archivo %s a %s" % (path, dest), force=True)
                    for file in listdir(path):
                        if not bool(xbmcvfs.copy(join(path, file), join(dest, file))):
                            break
                    else:
                        result = True
            if not result:
                if not silent:
                    logger.info("Copiando archivo %s a %s" % (path, dest), force=True)
                result = bool(xbmcvfs.copy(path, dest))
            
            # Si la copia no ha funcionado y se ha especificado su=True, se intenta el comando CP vía SU del sistema
            if not result and su and config.is_rooted(silent=True) == 'rooted':
                error_cmd = True
                for subcmd in ['-c', '-0']:
                    for cmdtype in [['cp', path, dest], ['cp %s %s' % (path, dest)]]:
                        command = ['su', subcmd] + cmdtype
                        output_cmd, error_cmd = config.su_command(command, silent=silent)
                        if not error_cmd:
                            break
                    if not error_cmd:
                        result = True
                        break
                else:
                    logger.error('Sin PERMISOS ROOT: %s' % str(command))
                    result = False
            elif result:
                su = ''
                
            if result and ch_mod:
                result = chmod(dest, ch_mod, silent=silent, su=su)
            return result
        
        fo = file_open(path, "rb")
        fd = file_open(dest, "wb")
        if fo and fd:
            if not silent:
                from platformcode.platformtools import dialog_progress
                dialogo = dialog_progress("Copiando archivo", "")
            size = getsize(path)
            copiado = 0
            while True:
                if not silent:
                    dialogo.update(old_div(copiado * 100, size), basename(path))
                buf = fo.read(1024 * 1024)
                if not buf:
                    break
                if not silent and dialogo.iscanceled():
                    dialogo.close()
                    return False
                fd.write(buf)
                copiado += len(buf)
            if not silent:
                dialogo.close()
    except:
        logger.error("ERROR al copiar el archivo: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
        return False
    else:
        return True


def exists(path, silent=False, vfs=True):
    """
    Comprueba si existe una carpeta o fichero
    @param path: ruta
    @type path: str
    @rtype: bool
    @return: Retorna True si la ruta existe, tanto si es una carpeta como un archivo
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            result = bool(xbmcvfs.exists(path))
            if not result and not path.endswith('/') and not path.endswith('\\'):
                result = bool(xbmcvfs.exists(join(path, ' ').rstrip()))
            return result    
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            return samba.exists(path)
        else:
            return os.path.exists(path)
    except:
        logger.error("ERROR al comprobar la ruta: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
        return False


def isfile(path, silent=False, vfs=True):
    """
    Comprueba si la ruta es un fichero
    @param path: ruta
    @type path: str
    @rtype: bool
    @return: Retorna True si la ruta existe y es un archivo
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            if not find_single_match(path, '(^\w+:\/\/)') and not (platform in ['windows', 'xbox'] and len(path) > 260):
                return os.path.isfile(path)
            if path.endswith('/') or path.endswith('\\'):
                path = path[:-1]
            dirs, files = xbmcvfs.listdir(dirname(path))
            base_name = basename(path)
            for file in files:
                if base_name == file:
                    return True
            return False
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            return samba.isfile(path)
        else:
            return os.path.isfile(path)
    except:
        logger.error("ERROR al comprobar el archivo: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
        return False


def isdir(path, silent=False, vfs=True):
    """
    Comprueba si la ruta es un directorio
    @param path: ruta
    @type path: str
    @rtype: bool
    @return: Retorna True si la ruta existe y es un directorio
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            if not find_single_match(path, '(^\w+:\/\/)'):
                return os.path.isdir(path)
            if path.endswith('/') or path.endswith('\\'):
                path = path[:-1]
            dirs, files = xbmcvfs.listdir(dirname(path))
            base_name = basename(path)
            for dir in dirs:
                if base_name == dir:
                    return True
            return False
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            return samba.isdir(path)
        else:
            return os.path.isdir(path)
    except:
        logger.error("ERROR al comprobar el directorio: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
        return False


def getsize(path, silent=False, vfs=True):
    """
    Obtiene el tamaño de un archivo
    @param path: ruta del fichero
    @type path: str
    @rtype: str
    @return: tamaño del fichero
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            if not exists(path): return long(0)
            f = xbmcvfs.File(path)
            s = f.size()
            f.close()
            return s
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            return long(samba.get_attributes(path).file_size)
        else:
            return os.path.getsize(path)
    except:
        logger.error("ERROR al obtener el tamaño: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
        return long(0)


def remove(path, silent=False, vfs=True, su=False):
    """
    Elimina un archivo, con alternativa de usar SU
    @param path: ruta del fichero a eliminar
    @type path: str
    @rtype: bool
    @return: devuelve False en caso de error
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            result = bool(xbmcvfs.delete(path))
        
            # Si el borrado no ha funcionado y se especificado su=True, se intenta el comando RM vía SU del sistema
            if not result and su and config.is_rooted(silent=True) == 'rooted':
                error_cmd = True
                for subcmd in ['-c', '-0']:
                    for cmdtype in [['rm', path], ['rm %s' % path]]:
                        command = ['su', subcmd] + cmdtype
                        output_cmd, error_cmd = config.su_command(command, silent=silent)
                        if not error_cmd:
                            break
                    if not error_cmd:
                        result = True
                        break
                else:
                    logger.error('Sin PERMISOS ROOT: %s' % str(command))
                    result = False
            return result
        
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            samba.remove(path)
        else:
            os.remove(path)
    except:
        logger.error("ERROR al eliminar el archivo: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
        return False
    else:
        return True


def rmdirtree(path, silent=False, vfs=True):
    """
    Elimina un directorio y su contenido
    @param path: ruta a eliminar
    @type path: str
    @rtype: bool
    @return: devuelve False en caso de error
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            if not exists(path): return True
            if not path.endswith('/') and not path.endswith('\\'):
                path = join(path, ' ').rstrip()
            for raiz, subcarpetas, ficheros in walk(path, topdown=False):
                for f in ficheros:
                    xbmcvfs.delete(join(raiz, f))
                for s in subcarpetas:
                    xbmcvfs.rmdir(join(raiz, s))
            xbmcvfs.rmdir(path)
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            for raiz, subcarpetas, ficheros in samba.walk(path, topdown=False):
                for f in ficheros:
                    samba.remove(join(decode(raiz), decode(f)))
                for s in subcarpetas:
                    samba.rmdir(join(decode(raiz), decode(s)))
            samba.rmdir(path)
        else:
            import shutil
            shutil.rmtree(path, ignore_errors=True)
    except:
        logger.error("ERROR al eliminar el directorio: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
            from platformcode.platformtools import dialog_notification
            dialog_notification("Error al eliminar el directorio", path)
        return False
    else:
        return not exists(path)


def rmdir(path, silent=False, vfs=True):
    """
    Elimina un directorio
    @param path: ruta a eliminar
    @type path: str
    @rtype: bool
    @return: devuelve False en caso de error
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            if not path.endswith('/') and not path.endswith('\\'):
                path = join(path, ' ').rstrip()
            return bool(xbmcvfs.rmdir(path))
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            samba.rmdir(path)
        else:
            os.rmdir(path)
    except:
        logger.error("ERROR al eliminar el directorio: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
            from platformcode.platformtools import dialog_notification
            dialog_notification("Error al eliminar el directorio", path)
        return False
    else:
        return True


def mkdir(path, silent=False, vfs=True, ch_mod=''):
    """
    Crea un directorio
    @param path: ruta a crear
    @type path: str
    @rtype: bool
    @return: devuelve False en caso de error
    """
    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            if not path.endswith('/') and not path.endswith('\\'):
                path = join(path, ' ').rstrip()
            result = bool(xbmcvfs.mkdirs(path))
            if not result or not exists(path):
                result = False
                try:
                    os.makedirs(path)
                    result = True
                except:
                    try:
                        os.mkdir(path)
                        result = True
                    except:
                        pass
            if not result:
                import time
                time.sleep(0.1)
                result = exists(path)
            if result and ch_mod:
                result = chmod(path, ch_mod, silent=silent)
            return result
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            samba.mkdir(path)
        else:
            try:
                os.makedirs(path)
            except:
                os.mkdir(path)
    except:
        logger.error("ERROR al crear el directorio: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
            from platformcode.platformtools import dialog_notification
            dialog_notification("Error al crear el directorio", path)
        return False
    else:
        return True


def walk(top, topdown=True, onerror=None, vfs=True):
    """
    Lista un directorio de manera recursiva
    @param top: Directorio a listar, debe ser un str "UTF-8"
    @type top: str
    @param topdown: se escanea de arriba a abajo
    @type topdown: bool
    @param onerror: muestra error para continuar con el listado si tiene algo seteado sino levanta una excepción
    @type onerror: bool
    ***El parametro followlinks que por defecto es True, no se usa aqui, ya que en samba no discrimina los links
    """
    top = encode(top)
    if top.lower().startswith("ftp://"):
        top_alt = ftp_to_smb_credential(top, remove=False)
        if exists(top_alt):
            top = top_alt
    
    if xbmc_vfs and vfs:
        for a, b, c in walk_vfs(top, topdown, onerror):
            # list(b) es para que haga una copia del listado de directorios
            # si no da error cuando tiene que entrar recursivamente en directorios con caracteres especiales
            yield a, list(b), c
    elif top.lower().startswith("smb://"):
        if not samba: import_samba()
        for a, b, c in samba.walk(top, topdown, onerror):
            # list(b) es para que haga una copia del listado de directorios
            # si no da error cuando tiene que entrar recursivamente en directorios con caracteres especiales
            yield decode(a), decode(list(b)), decode(c)
    else:
        for a, b, c in os.walk(top, topdown, onerror):
            # list(b) es para que haga una copia del listado de directorios
            # si no da error cuando tiene que entrar recursivamente en directorios con caracteres especiales
            yield decode(a), decode(list(b)), decode(c)


def walk_vfs(top, topdown=True, onerror=None):
    """
    Lista un directorio de manera recursiva
    Como xbmcvfs no tiene esta función, se copia la lógica de libsmb(samba) para realizar la previa al Walk
    """
    top = encode(top)
    dirs, nondirs = xbmcvfs.listdir(top)

    if topdown:
        yield top, dirs, nondirs

    for name in dirs:
        if isinstance(name, unicode):
            name = name.encode("utf8")
            if PY3: name = name.decode("utf8")
        elif PY3 and isinstance(name, bytes):
            name = name.decode("utf8")
        elif not PY3:
            name = unicode(name, "utf8")
        new_path = "/".join(top.split("/") + [name])
        for x in walk_vfs(new_path, topdown, onerror):
            yield x
    if not topdown:
        yield top, dirs, nondirs


def listdir(path, silent=False, vfs=True, file_inf=False):
    """
    Lista un directorio
    @param path: Directorio a listar, debe ser un str "UTF-8"
    @type path: str
    @rtype: str
    @return: contenido de un directorio
    """

    path = encode(path)
    try:
        if xbmc_vfs and vfs:
            dirs, files = xbmcvfs.listdir(path)
            res = sorted(dirs) + sorted(files)
            if file_inf:
                path = join(path, ' ').rstrip()
                ls_la = []
                for file in res:
                    file_ext = file_info(join(path, file))
                    if not isinstance(file_ext, bool):
                        file_ext = file_ext.replace(path, '')
                    else:
                        return file_ext
                    if file_ext:
                        ls_la += [file_ext]
                    else:
                        ls_la += ['%s%s  %s  %s  %s  %s  %s  %s' % ('#', '#', '#', '#', '#', '#', '#', file)]
                res = ls_la
            return decode(res)
        
        elif path.lower().startswith("smb://"):
            if not samba: import_samba()
            return decode(samba.listdir(path))
        
        else:
            return decode(os.listdir(path))
    except:
        logger.error("ERROR al leer el directorio: %s" % path)
        if not silent:
            logger.error(traceback.format_exc())
        return False


def join(*paths):
    """
    Junta varios directorios
    Corrige las barras "/" o "\" segun el sistema operativo y si es o no smaba
    @rytpe: str
    @return: la ruta concatenada
    """
    list_path = []
    if encode(paths[0]).startswith("/"):
        list_path.append("")

    for path in paths:
        if path:
            if xbmc_vfs:
                path = encode(path)
            list_path += path.replace("\\", "/").strip("/").split("/")

    if find_single_match(encode(paths[0]), '(^\w+:\/\/)'):
        return str("/".join(list_path))
    else:
        return str(os.sep.join(list_path))


def split(path, vfs=True):
    """
    Devuelve una tupla formada por el directorio y el nombre del fichero de una ruta
    @param path: ruta
    @type path: str
    @return: (dirname, basename)
    @rtype: tuple
    """
    path = encode(path)
    if find_single_match(path, '(^\w+:\/\/)'):
        protocol = find_single_match(path, '(^\w+:\/\/)')
        if '/' not in path[6:]:
            path = path.replace(protocol, protocol + "/", 1)
        return path.rsplit('/', 1)
    else:
        try:
            return decode(os.path.split(path))
        except:
            return os.path.split(path)


def basename(path, vfs=True):
    """
    Devuelve el nombre del fichero de una ruta
    @param path: ruta
    @type path: str
    @return: fichero de la ruta
    @rtype: str
    """
    path = encode(path)
    try:
        return decode(split(path)[1])
    except:
        return split(path)[1]


def dirname(path, vfs=True):
    """
    Devuelve el directorio de una ruta
    @param path: ruta
    @type path: str
    @return: directorio de la ruta
    @rtype: str
    """
    path = encode(path)
    try:
        return decode(split(path)[0])
    except:
        return split(path)[0]


def is_relative(path):
    return "://" not in path and not path.startswith("/") and ":\\" not in path


def remove_tags(title):
    """
    devuelve el titulo sin tags como color
    @type title: str
    @param title: title
    @rtype: str
    @return: cadena sin tags
    """
    logger.info()

    title_without_tags = find_single_match(title, '\[color .+?\](.+)\[\/color\]')

    if title_without_tags:
        return title_without_tags
    else:
        return title
        
    
def remove_smb_credential(path):
    """
    devuelve el path sin contraseña/usuario para paths de SMB
    @param path: ruta
    @type path: str
    @return: cadena sin credenciales
    @rtype: str
    """
    logger.info()
    
    if not find_single_match(path, '(^\w+:\/\/)'):
        return path
    
    protocol = find_single_match(path, '(^\w+:\/\/)')
    path_without_credentials = find_single_match(path, '^\w+:\/\/(?:[^;\n]+;)?(?:[^:@\n]+[:|@])?(?:[^@\n]+@)?(.*?$)')

    if path_without_credentials:
        return (protocol + path_without_credentials)
    else:
        return path


def ftp_to_smb_credential(path, remove=False):
    """
    devuelve el path ftp convertido a SMB, sin puerto
    @param path: ruta
    @type path: str
    @return: cadena formato SMB
    @rtype: str
    """
    logger.info()
    
    if not find_single_match(path, '(^\w+:\/\/)'):
        return path
    
    if path.lower().startswith("ftp://"):
        path = path.replace("ftp://", "smb://")
        path = re.sub("\:\d+(?:\/|$)", "/", path)
        if remove:
            path = remove_smb_credential(path)

    return path


def import_samba():
    global samba
    
    if not samba:
        if PY3:
            from lib.sambatools_py3 import libsmb as samba
        else:
            from lib.sambatools_py2 import libsmb as samba
            reload(sys)                                             ### Workoround Python 2
            sys.setdefaultencoding('utf-8')                         # Samba degrada el valor de defaultencoding.  Se reestablece
