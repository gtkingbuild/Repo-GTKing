# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Localiza las variables de entorno más habituales (kodi)
# ------------------------------------------------------------

from __future__ import division
#from builtins import str
from past.utils import old_div
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import xbmc
import xbmcgui
import xbmcaddon

import os
import subprocess
import re
import platform
try:
    import ctypes
except:
    pass
import traceback

from core import filetools, scrapertools
from platformcode import logger, config, platformtools, xbmc_videolibrary
from servers.torrent import torrent_dirs

if PY3:
    FF = b'\n'
else:
    FF = '\n'


def get_environment():
    """
    Devuelve las variables de entorno del OS, de Kodi y de Alfa más habituales,
    necesarias para el diagnóstico de fallos 
    """

    try:
        import base64
        import ast
        
        PLATFORM = config.get_system_platform()
        
        environment = config.get_platform(full_version=True)
        environment['num_version'] = str(environment['num_version'])
        environment['python_version'] = '%s (%s, %s)' % (str(platform.python_version()), \
                    str(sys.api_version), str(platform.python_implementation()))
        environment['os_release'] = str(platform.release())
        environment['prod_model'] = ''
        try:
            import multiprocessing
            environment['proc_num'] = ' (%sx)' % str(multiprocessing.cpu_count())
        except:
            environment['proc_num'] = ''
        
        if PLATFORM in ['windows', 'xbox']:
            environment['os_name'] = PLATFORM.capitalize()
            try:
                if platform.platform():
                    environment['os_release'] = str(platform.platform()).replace('Windows-', '')
                elif platform._syscmd_ver()[2]:
                    environment['os_release'] = str(platform._syscmd_ver()[2])
                
                command = ["wmic", "cpu", "get", "name"]
                p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000)
                output_cmd, error_cmd = p.communicate()
                if PY3 and isinstance(output_cmd, bytes):
                    output_cmd = output_cmd.decode()
                output_cmd = re.sub(r'\n|\r|\s{2}', '', output_cmd)
                environment['prod_model'] = str(scrapertools.find_single_match(output_cmd, \
                                '\w+.*?(?i)(?:Intel\(R\))?(?:\s*Core\(TM\))\s*(.*?CPU.*?)\s*(?:\@|$)'))
            except:
                pass
        
        elif PLATFORM in ['android', 'atv2']:
            environment['os_name'] = PLATFORM.capitalize()
            try:
                for label_a in subprocess.check_output('getprop').split(FF):
                    if PY3 and isinstance(label_a, bytes):
                        label_a = label_a.decode()
                    if 'build.version.release' in label_a:
                        environment['os_release'] = str(scrapertools.find_single_match(label_a, ':\s*\[(.*?)\]$'))
                    if 'product.model' in label_a:
                        environment['prod_model'] = str(scrapertools.find_single_match(label_a, ':\s*\[(.*?)\]$'))
            except:
                try:
                    for label_a in filetools.read(os.environ['ANDROID_ROOT'] + '/build.prop').split():
                        if PY3 and isinstance(label_a, bytes):
                            label_a = label_a.decode()
                        if 'build.version.release' in label_a:
                            environment['os_release'] = str(scrapertools.find_single_match(label_a, '=(.*?)$'))
                        if 'product.model' in label_a:
                            environment['prod_model'] = str(scrapertools.find_single_match(label_a, '=(.*?)$'))
                except:
                    pass
            environment['prod_model'] += ' (%s)' % config.is_rooted(silent=True)
        
        elif PLATFORM in ['linux', 'raspberry']:
            environment['os_name'] = PLATFORM.capitalize() if 'linux' in PLATFORM else 'RaspberryPi'
            try:
                for label_a in subprocess.check_output('hostnamectl').split(FF):
                    if PY3 and isinstance(label_a, bytes):
                        label_a = label_a.decode()
                    if 'Operating' in label_a:
                        environment['os_release'] = str(scrapertools.find_single_match(label_a, 'Operating\s*S\w+:\s*(.*?)\s*$'))
                        break
                        
                for label_a in subprocess.check_output(['cat', '/proc/cpuinfo']).split(FF):
                    if PY3 and isinstance(label_a, bytes):
                        label_a = label_a.decode()
                    if 'model name' in label_a:
                        environment['prod_model'] = str(scrapertools.find_single_match(label_a, \
                                'model.*?:\s*(?i)(?:Intel\(R\))?(?:\s*Core\(TM\))\s*(.*?CPU.*?)\s*(?:\@|$)'))
                        break
            except:
                pass
            
            if 'libreelec' in environment['os_release'].lower() and PLATFORM != 'raspberry':
                environment['os_name'] = 'RaspberryPi'
                if config.get_setting("caching", default=True):
                    try:
                        PLATFORM = 'raspberry'
                        window = xbmcgui.Window(10000)
                        window.setProperty("alfa_system_platform", PLATFORM)
                    except:
                        pass
        
        else:
            environment['os_name'] = str(PLATFORM.capitalize())

        if not environment['os_release']: environment['os_release'] = str(platform.release())
        if environment['proc_num'] and environment['prod_model']: environment['prod_model'] += environment['proc_num']
        environment['machine'] = str(platform.machine())
        environment['architecture'] = str(sys.maxsize > 2 ** 32 and "64-bit" or "32-bit")
        environment['language'] = str(xbmc.getInfoLabel('System.Language'))

        environment['cpu_usage'] = str(xbmc.getInfoLabel('System.CpuUsage'))
        
        environment['mem_total'] = str(xbmc.getInfoLabel('System.Memory(total)')).replace('MB', '').replace('KB', '')
        environment['mem_free'] = str(xbmc.getInfoLabel('System.Memory(free)')).replace('MB', '').replace('KB', '')
        if not environment['mem_total'] or not environment['mem_free']:
            try:
                if environment['os_name'].lower() in ['windows', 'xbox']:
                    kernel32 = ctypes.windll.kernel32
                    c_ulong = ctypes.c_ulong
                    c_ulonglong = ctypes.c_ulonglong
                    class MEMORYSTATUS(ctypes.Structure):
                        _fields_ = [
                            ('dwLength', c_ulong),
                            ('dwMemoryLoad', c_ulong),
                            ('dwTotalPhys', c_ulonglong),
                            ('dwAvailPhys', c_ulonglong),
                            ('dwTotalPageFile', c_ulonglong),
                            ('dwAvailPageFile', c_ulonglong),
                            ('dwTotalVirtual', c_ulonglong),
                            ('dwAvailVirtual', c_ulonglong),
                            ('availExtendedVirtual', c_ulonglong)
                        ]
                 
                    memoryStatus = MEMORYSTATUS()
                    memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUS)
                    kernel32.GlobalMemoryStatus(ctypes.byref(memoryStatus))
                    environment['mem_total'] = str(old_div(int(memoryStatus.dwTotalPhys), (1024**2)))
                    environment['mem_free'] = str(old_div(int(memoryStatus.dwAvailPhys), (1024**2)))

                else:
                    with open('/proc/meminfo') as f:
                        meminfo = f.read()
                    environment['mem_total'] = str(old_div(int(re.search(r'MemTotal:\s+(\d+)', meminfo).groups()[0]), 1024))
                    environment['mem_free'] = str(old_div(int(re.search(r'MemAvailable:\s+(\d+)', meminfo).groups()[0]), 1024))
            except:
                environment['mem_total'] = ''
                environment['mem_free'] = ''
            
        try:
            environment['kodi_buffer'] = '20'
            environment['kodi_bmode'] = '0'
            environment['kodi_rfactor'] = '4.0'
            if filetools.exists(filetools.join("special://userdata", "advancedsettings.xml")):
                advancedsettings = filetools.read(filetools.join("special://userdata", 
                                "advancedsettings.xml")).split('\n')
                for label_a in advancedsettings:
                    if 'memorysize' in label_a:
                        environment['kodi_buffer'] = str(old_div(int(scrapertools.find_single_match
                                (label_a, '>(\d+)<\/')), 1024**2))
                    if 'buffermode' in label_a:
                        environment['kodi_bmode'] = str(scrapertools.find_single_match
                                (label_a, '>(\d+)<\/'))
                    if 'readfactor' in label_a:
                        environment['kodi_rfactor'] = str(scrapertools.find_single_match
                                (label_a, '>(.*?)<\/'))
        except:
            pass
        
        environment['userdata_path'] = str(config.get_data_path())
        environment['userdata_path_perm'] = filetools.file_info(environment['userdata_path'])
        if not environment['userdata_path_perm']: del environment['userdata_path_perm']
        try:
            if environment['os_name'].lower() in ['windows', 'xbox']:
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(environment['userdata_path']), 
                                None, None, ctypes.pointer(free_bytes))
                environment['userdata_free'] = str(round(float(free_bytes.value) / (1024**3), 3))
            else:
                disk_space = os.statvfs(environment['userdata_path'])
                if not disk_space.f_frsize: disk_space.f_frsize = disk_space.f_frsize.f_bsize
                environment['userdata_free'] = str(round((float(disk_space.f_bavail) / \
                                (1024**3)) * float(disk_space.f_frsize), 3))
        except:
            environment['userdata_free'] = '?'
        
        if environment.get('userdata_path_perm', ''):
            environment['userdata_path'] = environment['userdata_path_perm']
            del environment['userdata_path_perm']
        environment['torrent_lang'] = '%s/%s' % (config.get_setting("channel_language", default="").upper(), \
                                config.get_setting("second_language", default="").upper())

        try:
            try:
                environment['videolab_pelis_scraper'] = 'TMDB' 
                environment['videolab_series_scraper'] = 'TMDB' if config.get_setting('scraper_tvshows', 'videolibrary', default=0) == 0 else 'TVDB'
                folder_movies = config.get_setting("folder_movies")
                folder_tvshows = config.get_setting("folder_tvshows")
                folders = [folder_movies, folder_tvshows]
                vlab_path = config.get_videolibrary_config_path()
                for i, folder in enumerate(folders):
                    if vlab_path.startswith("special://"): 
                        path = '%s/%s/' % (vlab_path, folder)
                    else:
                        path = filetools.join(vlab_path, folder, ' ').rstrip()
                    sql = 'SELECT strScraper FROM path where strPath LIKE "%s"' % path
                    nun_records, records = xbmc_videolibrary.execute_sql_kodi(sql, silent=True)
                    if nun_records > 0:
                        if i == 0:
                            if 'themoviedb' in records[0][0]: environment['videolab_pelis_scraper'] = 'TMDB,OK'
                            elif 'universal' in records[0][0]: environment['videolab_pelis_scraper'] = 'UNIV,OK'
                            else: environment['videolab_pelis_scraper'] = str(records[0][0]).upper()
                        else:
                            if 'themoviedb' in records[0][0]: environment['videolab_series_scraper'] = 'TMDB,OK'
                            elif 'tvdb' in records[0][0]: environment['videolab_series_scraper'] = 'TVDB,OK'
                            else: environment['videolab_series_scraper'] = str(records[0][0]).upper()
                    else:
                        if i == 0: environment['videolab_pelis_scraper'] += ',NOP'
                        else: environment['videolab_series_scraper'] += ',NOP'
            except:
                pass

            environment['videolab_series'] = '?'
            environment['videolab_episodios'] = '?'
            environment['videolab_pelis'] = '?'
            environment['videolab_path'] = str(config.get_videolibrary_path())
            environment['videolab_path_perm'] = filetools.file_info(environment['videolab_path'])
            if not environment['videolab_path_perm']:
                environment['videolab_path_perm'] = environment['videolab_path']
            if filetools.exists(filetools.join(environment['videolab_path'], \
                                config.get_setting("folder_tvshows"))):
                environment['videolab_series'] = str(len(filetools.listdir(filetools.join(environment['videolab_path'], \
                                config.get_setting("folder_tvshows")))))
                counter = 0
                if environment['videolab_path'].startswith("ftp://") or environment['videolab_path'].startswith("smb://"):
                    counter = '?'
                else:
                    for root, folders, files in filetools.walk(filetools.join(environment['videolab_path'], \
                                        config.get_setting("folder_tvshows"))):
                        for file in files:
                            if file.endswith('.strm'): counter += 1
                environment['videolab_episodios'] = str(counter)
            if filetools.exists(filetools.join(environment['videolab_path'], \
                                config.get_setting("folder_movies"))):
                environment['videolab_pelis'] = str(len(filetools.listdir(filetools.join(environment['videolab_path'], \
                                config.get_setting("folder_movies")))))
        except:
            pass
        try:
            video_updates = ['No', 'Inicio', 'Una vez', 'Inicio+Una vez', 'Dos veces al día']
            environment['videolab_update'] = str(video_updates[config.get_setting("update", "videolibrary")])
            if config.get_setting("videolibrary_backup_scan", "videolibrary", default=False):
                environment['videolab_update'] += ' (Solo SCAN)'
        except:
            environment['videolab_update'] = '?'
        try:
            if environment['os_name'].lower() in ['windows', 'xbox']:
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(environment['videolab_path']), 
                                None, None, ctypes.pointer(free_bytes))
                environment['videolab_free'] = str(round(float(free_bytes.value) / (1024**3), 3))
            else:
                disk_space = os.statvfs(environment['videolab_path'])
                if not disk_space.f_frsize: disk_space.f_frsize = disk_space.f_frsize.f_bsize
                environment['videolab_free'] = str(round((float(disk_space.f_bavail) / \
                                (1024**3)) * float(disk_space.f_frsize), 3))
        except:
            environment['videolab_free'] = '?'

        torrent_paths = torrent_dirs()
        environment['torrent_list'] = []
        environment['torrentcli_option'] = ''
        environment['torrent_error'] = ''
        environment['torrentcli_rar'] = config.get_setting("mct_rar_unpack", server="torrent", default=True)
        environment['torrentcli_backgr'] = config.get_setting("mct_background_download", server="torrent", default=True)
        environment['torrentcli_lib_path'] = config.get_setting("libtorrent_path", server="torrent", default="")
        
        if environment['torrentcli_lib_path']:
            lib_path = 'Activo'
        else:
            lib_path = 'Inactivo'
        if config.get_setting("libtorrent_version", server="torrent", default=""):
            lib_path += '-%s' % config.get_setting("libtorrent_version", server="torrent", default="")
        environment['torrentcli_unrar'] = config.get_setting("unrar_path", server="torrent", default="")
        if environment['torrentcli_unrar']:
            unrar = config.get_setting("unrar_device", server="torrent", default="").capitalize()
        else:
            unrar = 'Inactivo'
        torrent_id = config.get_setting("torrent_client", server="torrent", default=0)
        environment['torrentcli_option'] = str(torrent_id)
        torrent_options = platformtools.torrent_client_installed()
        if lib_path != 'Inactivo':
            torrent_options = [': MCT'] + torrent_options
            torrent_options = [': BT'] + torrent_options
        environment['torrent_list'].append({'Torrent_opt': str(torrent_id), 'Libtorrent': lib_path, \
                                            'RAR_Auto': str(environment['torrentcli_rar']), \
                                            'RAR_backgr': str(environment['torrentcli_backgr']), \
                                            'UnRAR': unrar})
        environment['torrent_error'] = config.get_setting("libtorrent_error", server="torrent", default="")
        if environment['torrent_error']:
            environment['torrent_list'].append({'Libtorrent_error': environment['torrent_error']})

        for torrent_option in torrent_options:
            cliente = dict()
            cliente['D_load_Path'] = ''
            cliente['Libre'] = '?'
            cliente['Plug_in'] = scrapertools.find_single_match(torrent_option, ':\s*(\w+)')
            if cliente['Plug_in'] not in ['BT', 'MCT']: cliente['Plug_in'] = cliente['Plug_in'].capitalize()
            
            cliente['D_load_Path'] = torrent_paths[cliente['Plug_in'].upper()]
            cliente['D_load_Path_perm'] = filetools.file_info(cliente['D_load_Path'])
            cliente['Buffer'] = str(torrent_paths[cliente['Plug_in'].upper()+'_buffer'])
            cliente['Version'] = str(torrent_paths[cliente['Plug_in'].upper()+'_version'])
            if cliente['Plug_in'].upper() == 'TORREST':
                cliente['Buffer'] = str(int(int(torrent_paths[cliente['Plug_in'].upper()+'_buffer']) /(1024*1024)))
                bin_path = filetools.join('special://home', 'addons', 'plugin.video.torrest', 'resources', 'bin')
                if filetools.exists(bin_path):
                    cliente['Platform'] = str(filetools.listdir(bin_path)[0])
                else:
                    cliente['Platform'] = 'None'
                try:
                    __settings__ = xbmcaddon.Addon(id="plugin.video.torrest")
                    cliente['Platform'] += ': %s: %s:%s' % (str(__settings__.getSetting("service_enabled")), \
                                    str(__settings__.getSetting("service_ip")), str(__settings__.getSetting("port")))
                except:
                    pass
                #cliente['Options'] = str(filetools.read(filetools.join('special://masterprofile', \
                #                    'addon_data', 'plugin.video.torrest', 'settings.xml')))
            if torrent_paths.get(cliente['Plug_in'].upper()+'_memory_size', ''):
                cliente['Memoria'] = str(torrent_paths[cliente['Plug_in'].upper()+'_memory_size'])
            
            if cliente.get('D_load_Path', ''):
                try:
                    if environment['os_name'].lower() in ['windows', 'xbox']:
                        free_bytes = ctypes.c_ulonglong(0)
                        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(cliente['D_load_Path']), 
                                    None, None, ctypes.pointer(free_bytes))
                        cliente['Libre'] = str(round(float(free_bytes.value) / \
                                    (1024**3), 3)).replace('.', ',')
                    else:
                        disk_space = os.statvfs(cliente['D_load_Path'])
                        if not disk_space.f_frsize: disk_space.f_frsize = disk_space.f_frsize.f_bsize
                        cliente['Libre'] = str(round((float(disk_space.f_bavail) / \
                                    (1024**3)) * float(disk_space.f_frsize), 3)).replace('.', ',')
                except:
                    pass
                if cliente.get('D_load_Path_perm', ''):
                    cliente['D_load_Path'] = cliente['D_load_Path_perm']
                    del cliente['D_load_Path_perm']
            environment['torrent_list'].append(cliente)

        environment['proxy_active'] = ''
        try:
            proxy_channel_bloqued_str = base64.b64decode(config.get_setting('proxy_channel_bloqued')).decode('utf-8')
            proxy_channel_bloqued = dict()
            proxy_channel_bloqued = ast.literal_eval(proxy_channel_bloqued_str)
            for channel_bloqued, proxy_active in list(proxy_channel_bloqued.items()):
                if proxy_active != 'OFF':
                    environment['proxy_active'] += channel_bloqued + ', '
        except:
            pass
        if not environment['proxy_active']: environment['proxy_active'] = 'OFF'
        environment['proxy_active'] = environment['proxy_active'].rstrip(', ')

        for root, folders, files in filetools.walk("special://logpath/"):
            for file in files:
                if file.lower() in ['kodi.log', 'jarvis.log', 'spmc.log', 'cemc.log', \
                                    'mygica.log', 'wonderbox.log', 'leiapp,log', \
                                    'leianmc.log', 'kodiapp.log', 'anmc.log', \
                                    'latin-anmc.log']:
                    environment['log_path'] = str(filetools.join(root, file))
                    break
            else:
                environment['log_path'] = ''
            break
        
        if environment.get('log_path', ''):
            environment['log_size_bytes'] = str(filetools.getsize(environment['log_path']))
            environment['log_size'] = str(round(float(environment['log_size_bytes']) / \
                                (1024*1024), 3))
        else:
            environment['log_size_bytes'] = ''
            environment['log_size'] = ''
        
        environment['debug'] = str(config.get_setting('debug'))
        environment['addon_version'] = '%s (Upd: %s h.)' % (str(config.get_addon_version(from_xml=True)), \
                                str(config.get_setting("addon_update_timer", default=12)).replace('0', 'No'))

        environment['assistant_version'] = str(None)
        if filetools.exists(filetools.join(config.get_data_path(), 'alfa-desktop-assistant.version')) \
                            and config.get_setting("assistant_mode") == "este":
            environment['assistant_version'] = filetools.read(filetools.join(config.get_data_path(), 'alfa-desktop-assistant.version'))
            config.set_setting('assistant_version', environment['assistant_version'])
            environment['assistant_version'] = '%s, %s' % (environment['assistant_version'], str(config.get_setting("assistant_mode")))
            environment['assistant_path'] = str(filetools.file_info(filetools.join(config.get_data_path(), 'assistant')))
        elif filetools.exists(filetools.join(config.get_data_path(), 'alfa-mobile-assistant.version')):
            environment['assistant_version'] = filetools.read(filetools.join(config.get_data_path(), 'alfa-mobile-assistant.version'))
            config.set_setting('assistant_version', environment['assistant_version'])
            environment['assistant_version'] = '%s, %s, %s' % (environment['assistant_version'], str(config.get_setting("assistant_mode")), 
                                                               str(config.get_setting("assistant_custom_address")))
        environment['assistant_version'] += ', Req: %s' % str(config.get_setting('assistant_binary', default=False))
        environment['assistant_cf_ua'] = str(config.get_setting('cf_assistant_ua', default=None))
        assistant_path = filetools.join(os.getenv('ANDROID_STORAGE'), 'emulated', '0', 'Android', 'data', 'com.alfa.alfamobileassistant')
        if PLATFORM in ['android', 'atv2'] and filetools.exists(assistant_path):
            environment['assistant_path'] = str(filetools.file_info(assistant_path))
    
        try:
            import ssl
            environment['ssl_version'] = str(ssl.OPENSSL_VERSION)
        except:
            environment['ssl_version'] = ''

    except:
        logger.error(traceback.format_exc())
        environment = {}
        environment['log_size'] = ''
        environment['cpu_usage'] = ''
        environment['python_version'] = ''
        environment['log_path'] = ''
        environment['userdata_free'] = ''
        environment['mem_total'] = ''
        environment['machine'] = ''
        environment['platform'] = ''
        environment['videolab_path'] = ''
        environment['num_version'] = ''
        environment['os_name'] = ''
        environment['video_db'] = ''
        environment['userdata_path'] = ''
        environment['log_size_bytes'] = ''
        environment['name_version'] = ''
        environment['language'] = ''
        environment['mem_free'] = ''
        environment['prod_model'] = ''
        environment['proxy_active'] = ''
        environment['architecture'] = ''
        environment['os_release'] = ''
        environment['videolab_free'] = ''
        environment['kodi_buffer'] = ''
        environment['kodi_bmode'] = ''
        environment['kodi_rfactor'] = ''
        environment['videolab_pelis_scraper'] = ''
        environment['videolab_series_scraper'] = ''
        environment['videolab_series'] = ''
        environment['videolab_episodios'] = ''
        environment['videolab_pelis'] = ''
        environment['videolab_update'] = ''
        environment['videolab_path_perm'] = ''
        environment['debug'] = ''
        environment['addon_version'] = ''
        environment['torrent_list'] = []
        environment['torrent_lang'] = ''
        environment['torrentcli_option'] = ''
        environment['torrentcli_rar'] = ''
        environment['torrentcli_lib_path'] = ''
        environment['torrentcli_unrar'] = ''
        environment['torrent_error'] = ''
        environment['assistant_version'] = ''
        environment['assistant_cf_ua'] = ''
        environment['ssl_version'] = ''
        
    return environment


def list_env(environment={}):
    if not environment:
        environment = get_environment()

    logger.info('----------------------------------------------', force=True)
    logger.info('Variables de entorno Alfa: ' + environment['addon_version'] + 
                ' Debug: ' + environment['debug'], force=True)
    logger.info("----------------------------------------------", force=True)
    logger.info('** OS Environ: %s' % os.environ, force=True)
    logger.info("----------------------------------------------", force=True)

    logger.info(environment['os_name'] + ' ' + environment['os_release'] + ' ' + 
                environment['prod_model'] + ' ' + environment['machine'] + ' ' + 
                environment['architecture'] + ' ' + environment['language'], force=True)
    
    logger.info('Kodi ' + environment['num_version'] + ', Vídeo: ' + 
                environment['video_db'] + ', Python ' + environment['python_version'], force=True)
    
    if environment['cpu_usage']:
        logger.info('CPU: ' + environment['cpu_usage'], force=True)
    
    if environment['mem_total'] or environment['mem_free']: 
        logger.info('Memoria: Total: ' + environment['mem_total'] + ' MB / Disp.: ' + 
                    environment['mem_free'] + ' MB / Buffers: ' + 
                    str(int(environment['kodi_buffer']) * 3) + ' MB / Buffermode: ' + 
                    environment['kodi_bmode']  + ' / Readfactor: ' + 
                    environment['kodi_rfactor'], force=True)

    logger.info('Userdata: ' + environment['userdata_path'] + ' - Libre: ' + 
                environment['userdata_free'].replace('.', ',') +  ' GB' + 
                ' - Idioma: ' + environment['torrent_lang'], force=True)
    
    logger.info('Videoteca: Series/Epis (%s): ' % environment['videolab_series_scraper'] + 
                    environment['videolab_series'] + '/' + 
                    environment['videolab_episodios'] + ' - Pelis (%s): ' % environment['videolab_pelis_scraper'] + 
                    environment['videolab_pelis'] + ' - Upd: ' + 
                    environment['videolab_update'] + ' - Path: ' + 
                    environment['videolab_path_perm'] + ' - Libre: ' + 
                    environment['videolab_free'].replace('.', ',') +  ' GB', force=True)
    
    if environment['torrent_list']:
        for x, cliente in enumerate(environment['torrent_list']):
            if x == 0:
                cliente_alt = cliente.copy()
                del cliente_alt['Torrent_opt']
                logger.info('Torrent: Opt: %s, %s' % (str(cliente['Torrent_opt']), \
                            str(cliente_alt).replace('{', '').replace('}', '')\
                            .replace("'", '').replace('_', ' ')), force=True)
            elif x == 1 and environment['torrent_error']:
                logger.info('- ' + str(cliente).replace('{', '').replace('}', '')\
                            .replace("'", '').replace('_', ' '), force=True)
            else:
                cliente_alt = cliente.copy()
                del cliente_alt['Plug_in']
                del cliente_alt['Version']
                cliente_alt['Libre'] = cliente_alt['Libre'].replace('.', ',') + ' GB'
                logger.info('- %s v.%s: %s' % (str(cliente['Plug_in']), str(cliente['Version']), \
                            str(cliente_alt).replace('{', '').replace('}', '').replace("'", '')\
                            .replace('\\\\', '\\')), force=True)
    
    logger.info('Proxy: ' + environment['proxy_active'], force=True)
    
    logger.info('SSL version: ' + environment['ssl_version'], force=True)
    
    logger.info('Assistant ver.: ' + environment['assistant_version'] + \
                            ' - Assistant UA: ' + environment['assistant_cf_ua'] + \
                            ' - Assistant path: ' + environment.get('assistant_path', ''), force=True)
    
    logger.info('TAMAÑO del LOG: ' + environment['log_size'].replace('.', ',') + ' MB', force=True)
    logger.info("----------------------------------------------", force=True)
    
    return environment
    
    
def paint_env(item, environment={}):
    from core.item import Item
    from channelselector import get_thumb
    
    if not environment:
        environment = get_environment()
    environment = list_env(environment)
    
    itemlist = []
    
    thumb = get_thumb("setting_0.png")
    
    cabecera = """\
    Muestra las [COLOR yellow]variables[/COLOR] del ecosistema de Kodi que puden ser relevantes para el diagnóstico de problema en Alfa:
        - Versión de Alfa con Fix
        - (Upd): Intervalo de actualización en horas, o NO actualización
        - Debug Alfa: True/False
    """
    plataform = """\
    Muestra los datos especificos de la [COLOR yellow]plataforma[/COLOR] en la que está alojado Kodi:
        - Sistema Operativo
        - Modelo (opt)
        - Versión SO
        - Procesador
        - Aquitectura
        - Idioma de Kodi
    """
    kodi = """\
    Muestra los datos especificos de la instalación de [COLOR yellow]Kodi[/COLOR]:
        - Versión de Kodi
        - Base de Datos de Vídeo
        - Versión de Python (API, Fuente)
    """
    cpu = """\
    Muestra los datos consumo actual de [COLOR yellow]CPU(s)[/COLOR]
    """
    memoria = """\
    Muestra los datos del uso de [COLOR yellow]Memoria[/COLOR] del sistema:
        - Memoria total
        - Memoria disponible
        - en [COLOR yellow]Advancedsettings.xml[/COLOR]
             - Buffer de memoria 
                 configurado: 
                 para Kodi: 3 x valor de 
                 <memorysize>
             - Buffermode: cachea: 
                 * Internet (0, 2)
                 * También local (1)
                 * No Buffer (3)
             - Readfactor: readfactor * 
                 avg bitrate vídeo
    """
    userdata = """\
    Muestra los datos del "path" de [COLOR yellow]Userdata[/COLOR]:
        - Path
        - Espacio disponible
        - Idioma primario/secudario de Alfa
    """
    videoteca = """\
    Muestra los datos de la [COLOR yellow]Videoteca[/COLOR]:
        - Nº de Series y Episodios (Scraper)
        - Nº de Películas (Scraper)
        - Tipo de actulización
        - Path
        - Espacio disponible
    """
    torrent = """\
    Muestra los datos generales del estado de [COLOR yellow]Torrent[/COLOR]:
        - ID del cliente seleccionado
        - Descompresión automática de archivos RAR?
        - Está activo Libtorrent?
        - Se descomprimen los RARs en background?
        - Está operativo el módulo UnRAR? Qué plataforma?
    """
    torrent_error = """\
    Muestra los datos del error de importación de [COLOR yellow]Libtorrent[/COLOR]
    """
    torrent_cliente = """\
    Muestra los datos de los [COLOR yellow]Clientes Torrent[/COLOR]:
        - Nombre del Cliente
        - Tamaño de buffer inicial
        - Path de descargas
        - Tamaño de buffer en Memoria 
                (opt, si no disco)
        - Espacio disponible
    """
    proxy = """\
    Muestra las direcciones de canales o servidores que necesitan [COLOR yellow]Proxy[/COLOR]
    """
    SSL = """\
    Muestra la versión instalada de SSL [COLOR yellow]Proxy[/COLOR]
    """
    assistant = """\
    Muestra la versión del [COLOR yellow]Assistant[/COLOR] instalado y el [COLOR yellow]User Agent[/COLOR] usado
    """
    log = """\
    Muestra el tamaño actual del [COLOR yellow]Log[/COLOR]
    """
    reporte = """\
    Enlaza con la utilidad que permite el [COLOR yellow]envío del Log[/COLOR] de Kodi a través de un servicio Pastebin
    """

    itemlist.append(Item(channel=item.channel, title="[COLOR orange][B]Variables " +
                    "de entorno Alfa: %s Debug: %s[/B][/COLOR]" % 
                     (environment['addon_version'], environment['debug']), 
                    action="", plot=cabecera, thumbnail=thumb, folder=False)) 

    itemlist.append(Item(channel=item.channel, title='[COLOR yellow]%s[/COLOR]' % 
                    environment['os_name'] + ' ' + environment['os_release'] + ' ' + 
                    environment['prod_model'] + ' '  + environment['machine'] + ' ' + 
                    environment['architecture'] + ' ' + environment['language'], 
                    action="", plot=plataform, thumbnail=thumb, folder=False))
    
    itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Kodi [/COLOR]' + 
                    environment['num_version'] + ', Vídeo: ' + environment['video_db'] + 
                    ', Python ' + environment['python_version'], action="", 
                    plot=kodi, thumbnail=thumb, folder=False))
    
    if environment['cpu_usage']:
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]CPU: [/COLOR]' + 
                    environment['cpu_usage'], action="", plot=cpu, thumbnail=thumb, 
                    folder=False))
    
    if environment['mem_total'] or  environment['mem_free']: 
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Memoria: [/COLOR]Total: ' + 
                    environment['mem_total'] + ' MB / Disp.: ' + 
                    environment['mem_free'] + ' MB / Buffers: ' + 
                    str(int(environment['kodi_buffer']) * 3) + ' MB / Buffermode: ' + 
                    environment['kodi_bmode']  + ' / Readfactor: ' + 
                    environment['kodi_rfactor'], 
                    action="", plot=memoria, thumbnail=thumb, folder=False))

    itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Userdata: [/COLOR]' + 
                    environment['userdata_path'] + ' - Free: ' + environment['userdata_free'].replace('.', ',') + 
                    ' GB' + ' - Idioma: ' + environment['torrent_lang'], action="", plot=userdata, thumbnail=thumb, folder=False))
    
    itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Videoteca: [/COLOR]Series/Epis (%s): ' 
                    % environment['videolab_series_scraper'] + 
                    environment['videolab_series'] + '/' + environment['videolab_episodios'] + 
                    ' - Pelis (%s): ' % environment['videolab_pelis_scraper'] + 
                    environment['videolab_pelis'] + ' - Upd: ' + 
                    environment['videolab_update'] + ' - Path: ' + 
                    environment['videolab_path'] + ' - Free: ' + environment['videolab_free'].replace('.', ',') +  
                    ' GB', action="", plot=videoteca, thumbnail=thumb, folder=False))

    if environment['torrent_list']:
        for x, cliente in enumerate(environment['torrent_list']):
            if x == 0:
                cliente_alt = cliente.copy()
                del cliente_alt['Torrent_opt']
                itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Torrent: [/COLOR]Opt: %s, %s' \
                            % (str(cliente['Torrent_opt']), str(cliente_alt).replace('{', '').replace('}', '')\
                            .replace("'", '').replace('_', ' ')), action="", plot=torrent, thumbnail=thumb, 
                            folder=False))
            elif x == 1 and environment['torrent_error']:
                itemlist.append(Item(channel=item.channel, title='[COLOR magenta]- %s[/COLOR]' % str(cliente).replace('{', '').replace('}', '')\
                            .replace("'", '').replace('_', ' '), action="", plot=torrent_error, thumbnail=thumb, 
                            folder=False))
            else:
                cliente_alt = cliente.copy()
                del cliente_alt['Plug_in']
                del cliente_alt['Version']
                cliente_alt['Libre'] = cliente_alt['Libre'].replace('.', ',') + ' GB'
                itemlist.append(Item(channel=item.channel, title='[COLOR yellow]- %s v%s: [/COLOR]%s' % 
                            (str(cliente['Plug_in']), str(cliente['Version']), str(cliente_alt).replace('{', '')\
                            .replace('}', '').replace("'", '').replace('\\\\', '\\')), action="", plot=torrent_cliente, 
                            thumbnail=thumb, folder=False))
    
    itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Proxy: [/COLOR]' + 
                    environment['proxy_active'], action="", plot=proxy, thumbnail=thumb, 
                    folder=False))
                    
    itemlist.append(Item(channel=item.channel, title='[COLOR yellow]SSL: [/COLOR]' + 
                    environment['ssl_version'], action="", plot=SSL, thumbnail=thumb, 
                    folder=False))
    
    itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Assistant ver.: [/COLOR]' + 
                    environment['assistant_version'] + ' - [COLOR yellow]Assistant UA: [/COLOR]' + 
                    environment['assistant_cf_ua'] + ' - [COLOR yellow]Assistant path: [/COLOR]' + 
                    environment.get('assistant_path', ''), action="", plot=assistant, thumbnail=thumb, 
                    folder=False))
    
    itemlist.append(Item(channel=item.channel, title='[COLOR yellow]TAMAÑO del LOG: [/COLOR]' + 
                    environment['log_size'].replace('.', ',') + ' MB', action="", plot=log, thumbnail=thumb, 
                    folder=False))
                    
    itemlist.append(Item(title="[COLOR hotpink][B]==> Reportar un fallo[/B][/COLOR]", 
                    channel="report", action="mainlist", category='Configuración', 
                    unify=False, plot=reporte, thumbnail=get_thumb("error.png")))
    
    return (itemlist, environment)