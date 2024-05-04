#-*- coding: utf-8 -*-
'''
    python-libtorrent for Kodi (script.module.libtorrent)
    Copyright (C) 2015-2016 DiMartino, srg70, RussakHH, aisman

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from __future__ import absolute_import
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from .functions import *
import xbmc, xbmcaddon
import os
import traceback                                                                ### Alfa

#__settings__ = xbmcaddon.Addon(id='script.module.libtorrent')                  ### Alfa
#__version__ = __settings__.getAddonInfo('version')                             ### Alfa
#__plugin__ = __settings__.getAddonInfo('name') + " v." + __version__           ### Alfa
#__settings__ = xbmcaddon.Addon(id='plugin.video.alfa')                         ### Alfa
__version__ = '2.0.2'                                                           ### Alfa
__plugin__ = "python-libtorrent v.2.0.2"                                        ### Alfa
#__language__ = __settings__.getLocalizedString                                 ### Alfa
__root__ = filetools.dirname(filetools.dirname(__file__))

from platformcode import config
from core import filetools
LIBTORRENT_SAFE = False

libtorrent=None
platform = get_platform()
#set_dirname=__settings__.getSetting('dirname')                                 ### Alfa
#set_dirname=filetools.join(__settings__.getAddonInfo('Path'),'lib', 'python_libtorrent')  ### Alfa
set_dirname=__root__                                                            ### Alfa
if getSettingAsBool('custom_dirname') and set_dirname:
    log('set_dirname:' +str(set_dirname))
    dirname=set_dirname
else:
    #dirname = filetools.join(filetools.translatePath('special://temp'), 'xbmcup', 'script.module.libtorrent',
    #                       'python_libtorrent')
    dirname=set_dirname                                                         ### Alfa

log('dirname: ' +str(dirname))

VERSIONS = ['0.16.19', '1.0.6', '1.0.7', '1.0.8', '1.0.9', '1.0.11', '1.1.0', '1.1.1', '1.1.6', '1.1.7', '1.2.12', '2.0.2']  ### Alfa
if platform['system'] in ['linux_armv7', 'linux_aarch64_ucs4']:                 ### Alfa: Removing ARM from v2 list
    VERSIONS.remove('2.0.2')
    VERSIONS.remove('1.2.12')

while VERSIONS:
    log('VERSIONS: %s' % str(VERSIONS))

    default_path = VERSIONS[-1]

    #set_version = int(__settings__.getSetting('set_version'))                  ### Alfa
    set_version = 0                                                             ### Alfa
    if getSettingAsBool('custom_version'):
        log('set_version:' +str(set_version)+' '+VERSIONS[set_version])
        platform['version'] = VERSIONS[set_version]
    else:
        platform['version'] = default_path

    sizefile_path = filetools.join(__root__, platform['system'], platform['version'])
    if not filetools.exists(sizefile_path):
        log('set_version: no sizefile at %s back to default %s' % (sizefile_path, default_path))
        platform['version'] = default_path
        sizefile_path = filetools.join(__root__, platform['system'], platform['version'])
        if not filetools.exists(sizefile_path):
            log('set_version: no default at %s searching for any version' % sizefile_path)
            try:
                versions = sorted(filetools.listdir(filetools.join(__root__, platform['system'])))
            except:
                versions = []
            
            versions_for = versions[:]
            for ver in versions_for:
                if ver not in VERSIONS:
                    versions.remove(ver)
                    continue
                if not filetools.isdir(filetools.join(__root__, platform['system'], ver)):
                    versions.remove(ver)
                    
            VERSIONS_for = VERSIONS[:]
            for ver in VERSIONS_for:
                if ver not in versions:
                    VERSIONS.remove(ver)

            if len(versions)>0:
                platform['version'] = versions[-1]
                log('set_version: chose %s out of %s' % (platform['version'], str(versions)))
            else:
                e = 'die because the folder is empty'
                log(e)
                raise Exception(e)
    
    dest_path = filetools.join(dirname, platform['system'], platform['version'])
    dest_path_bin = filetools.join(config.get_data_path(), 'bin')
    sys.path.insert(0, dest_path_bin)

    lm=LibraryManager(dest_path, platform)
    if not lm.check_exist(dest_path, platform) or (not 'libtorrent' in str(filetools.listdir(dest_path_bin)) \
                and not xbmc.getCondVisibility("system.platform.android")):     ### Alfa
        ok=lm.download(dest_path, platform)
        xbmc.sleep(2000)


    #if __settings__.getSetting('plugin_name')!=__plugin__:                     ### Alfa
    #    __settings__.setSetting('plugin_name', __plugin__)                     ### Alfa
    #    lm.update(dest_path, platform)                                         ### Alfa

    log('platform: ' + str(platform))
    if platform['system'] not in ['windows', 'windows_x64']:                    ### Alfa
        log('os: '+str(os.uname()))
        log_text = 'ucs4' if sys.maxunicode > 65536 else 'ucs2'
        log_text += ' x64' if sys.maxsize > 2147483647 else ' x86'
        log(log_text)

    try:
        fp = ''
        pathname = ''
        description = ''
        libtorrent = ''

        if platform['system'] in ['linux_x86', 'windows', 'windows_x64', 'linux_armv6', 'linux_armv7',
                                  'linux_x86_64', 'linux_mipsel_ucs2', 'linux_mipsel_ucs4',
                                  'linux_aarch64_ucs2', 'linux_aarch64_ucs4']:  ### Alfa
            import libtorrent

        elif platform['system'] in ['darwin', 'ios_arm']:
            import imp
            
            path_list = [dest_path_bin]
            log('path_list = ' + str(path_list))
            fp, pathname, description = imp.find_module('libtorrent', path_list)
            log('fp = ' + str(fp))
            log('pathname = ' + str(pathname))
            log('description = ' + str(description))
            try:
                libtorrent = imp.load_module('libtorrent', fp, pathname, description)
            finally:
                if fp: fp.close()
        
        elif xbmc.getCondVisibility("system.platform.android"):
            try:
                import imp
                from ctypes import CDLL
                
                dest_path = ''
                envirom = os.environ.get('KODI_ANDROID_APK', '')
                if not envirom: envirom = os.environ.get('XBMC_ANDROID_APK', '')
                if envirom:
                    log(envirom)
                    dest_path = filetools.join(filetools.dirname(envirom), 'lib')
                    dest_path_dir = filetools.listdir(dest_path)
                    log(filetools.listdir(dest_path, file_inf=True))
                    if dest_path_dir:
                        for folder in dest_path_dir:
                            if 'arm' in folder or 'aarch' in folder:
                                dest_path = filetools.join(dest_path, folder)
                                break
                        else:
                            dest_path = ''
                    if dest_path and filetools.exists(dest_path):
                        dest_path = lm.android_workaround(dest_path)
                        if not filetools.exists(filetools.join(dest_path, 'liblibtorrent.so')):
                            dest_path = ''
                    else:
                        dest_path = ''
                
                if not dest_path:
                    dest_path_ini = filetools.translatePath('special://xbmc/').replace('/cache/apk/assets', '')
                    dest_path_dir = filetools.listdir(dest_path_ini, file_inf=True)
                    log(dest_path_ini)
                    log(dest_path_dir)
                    if dest_path_dir:
                        if filetools.exists(filetools.join(dest_path_ini, 'lib')):
                            dest_path = lm.android_workaround(filetools.join(dest_path_ini, 'lib'))
                        if not filetools.exists(filetools.join(dest_path, 'liblibtorrent.so')):
                            if filetools.exists(os.environ['KODI_BINADDON_PATH']):
                                dest_path = lm.android_workaround(os.environ['KODI_BINADDON_PATH'])
                            if not filetools.exists(filetools.join(dest_path, 'liblibtorrent.so')):
                                if dest_path != filetools.join(dest_path_ini, 'cache', 'lib'):
                                    if filetools.exists(filetools.join(dest_path_ini, 'cache', 'lib')):
                                        dest_path = lm.android_workaround(filetools.join(dest_path_ini, 'cache', 'lib'))
                                if not filetools.exists(filetools.join(dest_path, 'liblibtorrent.so')):
                                    dest_path = filetools.join(dest_path_ini, 'files')
                                    if not filetools.exists(dest_path):
                                        filetools.mkdir(dest_path)
                                        dest_path = lm.android_workaround(dest_path)
                                        if not filetools.exists(filetools.join(dest_path, 'liblibtorrent.so')):
                                            raise

                sys.path.insert(0, dest_path)
                
                if PY3:                                                         ### Alfa
                    try:
                        import libtorrent                                       # Intentamos importar de forma estñandar, por si lo han arreglado
                    except:
                        log(traceback.format_exc(1))
                
                if not libtorrent:
                    dll_path = filetools.join(dest_path, 'liblibtorrent.so')
                    log('CDLL path = ' + str(filetools.file_info(dll_path)))
                    liblibtorrent = CDLL(dll_path)
                    log('CDLL = ' + str(liblibtorrent))
                    path_list = [dest_path]
                    log('path_list = ' + str(path_list))
                    
                    fp, pathname, description = imp.find_module('libtorrent', path_list)
                    log('fp = ' + str(fp))
                    log('pathname = ' + str(pathname))
                    log('description = ' + str(description))
                    try:
                        libtorrent = imp.load_module('libtorrent', fp, pathname, description)
                    finally:
                        if fp: fp.close()
            
            except Exception as e:
                if not PY3:
                    e = unicode(str(e), "utf8", errors="replace").encode("utf8")
                config.set_setting("libtorrent_path", "", server="torrent")         ### Alfa
                config.set_setting("libtorrent_error", str(e), server="torrent")    ### Alfa
                log(traceback.format_exc(1))
                if fp: log('fp = ' + str(fp))
                if pathname: log('pathname = ' + str(pathname))
                if description: log('description = ' + str(description))
                log('Error importing libtorrent from "' + str(dest_path) + '". Exception: ' + str(e))
                if fp: fp.close()

        if libtorrent:
            if xbmc.getCondVisibility("system.platform.android"): dest_path_bin = dest_path
            config.set_setting("libtorrent_path", str(dest_path_bin), server="torrent") ### Alfa
            config.set_setting("libtorrent_error", "", server="torrent")            ### Alfa
            log('Imported libtorrent v' + libtorrent.version + ' from "' + str(dest_path_bin) + '"')
            break
        elif platform['system'] in ['android_armv7', 'android_x86']:
            break
        elif platform['version'].startswith('2'):
            del VERSIONS[-1]
        elif not LIBTORRENT_SAFE:
            LIBTORRENT_SAFE = True
            del VERSIONS[-1]
        else:
            break

    except Exception as e:
        if not PY3:
            e = unicode(str(e), "utf8", errors="replace").encode("utf8")
        config.set_setting("libtorrent_path", "", server="torrent")             ### Alfa
        config.set_setting("libtorrent_error", str(e), server="torrent")        ### Alfa
        log('Error importing libtorrent from "' + str(dest_path_bin) + '". Exception: ' + str(e))
        if fp: fp.close()
        if platform['version'].startswith('2'):
            del VERSIONS[-1]
        elif not LIBTORRENT_SAFE and platform['system'] not in ['android_armv7', 'android_x86']:
            LIBTORRENT_SAFE = True
            del VERSIONS[-1]
            log('PASO platform["version"] ' + str(platform['version']))
        else:
            break
            
try:
    config.set_setting("libtorrent_version", "%s/%s" % (platform['system'], platform['version']), server="torrent")     ### Alfa
except:
    pass


def get_libtorrent():
    return libtorrent
