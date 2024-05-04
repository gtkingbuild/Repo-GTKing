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
from builtins import object
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import time
import xbmc, xbmcgui, xbmcaddon

from .net import HTTP
from core import filetools                                                      ### Alfa
from core import ziptools
from platformcode import config                                                 ### Alfa

#__libbaseurl__ = "https://github.com/DiMartinoXBMC/script.module.libtorrent/raw/master/python_libtorrent"
__libbaseurl__ = ["https://github.com/DiMartinoXBMC/script.module.libtorrent/raw/master/python_libtorrent"]
#__settings__ = xbmcaddon.Addon(id='script.module.libtorrent')
#__version__ = __settings__.getAddonInfo('version')
#__plugin__ = __settings__.getAddonInfo('name') + " v." + __version__
#__icon__= filetools.join(filetools.translatePath('special://home'), 'addons',
#                                   'script.module.libtorrent', 'icon.png')
#__settings__ = xbmcaddon.Addon(id='plugin.video.alfa')                         ### Alfa
__version__ = '2.0.2'                                                           ### Alfa
__plugin__ = "python-libtorrent v.2.0.2"                                        ### Alfa
__icon__= filetools.join(filetools.translatePath('special://home'), 'addons',
                                   'plugin.video.alfa', 'icon.png')             ### Alfa
#__language__ = __settings__.getLocalizedString                                 ### Alfa

#from python_libtorrent.platform_pulsar import get_platform, get_libname        ### Alfa
from lib.python_libtorrent.python_libtorrent.platform_pulsar import get_platform, get_libname   ### Alfa

def log(msg):
    if PY3:
        try:
            xbmc.log("### [%s]: %s" % (__plugin__,msg,), level=xbmc.LOGINFO )
        except UnicodeEncodeError:
            xbmc.log("### [%s]: %s" % (__plugin__,msg.encode("utf-8", "ignore"),), level=xbmc.LOGINFO )
        except:
            xbmc.log("### [%s]: %s" % (__plugin__,'ERROR LOG',), level=xbmc.LOGINFO )
    else:
        try:
            xbmc.log("### [%s]: %s" % (__plugin__,msg,), level=xbmc.LOGNOTICE )
        except UnicodeEncodeError:
            xbmc.log("### [%s]: %s" % (__plugin__,msg.encode("utf-8", "ignore"),), level=xbmc.LOGNOTICE )
        except:
            xbmc.log("### [%s]: %s" % (__plugin__,'ERROR LOG',), level=xbmc.LOGNOTICE )

def getSettingAsBool(setting):
    __settings__ = xbmcaddon.Addon(id='plugin.video.alfa')                      ### Alfa
    return __settings__.getSetting(setting).lower() == "true"

class LibraryManager(object):
    def __init__(self, dest_path, platform):
        self.dest_path = dest_path
        self.platform = platform
        self.root=filetools.dirname(filetools.dirname(__file__))
        ver1, ver2, ver3 = platform['version'].split('.')                       ### Alfa: resto método
        try:
            ver1 = int(ver1)
            ver2 = int(ver2)
        except:
            ver1 = 2
            ver2 = 0
        if ver1 > 1 or (ver1 == 1 and ver2 >= 2):
            global __libbaseurl__
            __libbaseurl__ = ['https://raw.githubusercontent.com/alfa-addon/alfa-repo/master/downloads/libtorrent', \
                              'https://gitlab.com/addon-alfa/alfa-repo/-/raw/master/downloads/libtorrent']
        else:
            __libbaseurl__ = ["https://github.com/DiMartinoXBMC/script.module.libtorrent/raw/master/python_libtorrent"]

    def check_exist(self, dest_path='', platform=''):
        if dest_path: self.dest_path = dest_path
        if platform: self.platform = platform
        for libname in get_libname(self.platform):
            if not filetools.exists(filetools.join(self.dest_path, libname)):
                return False
        return True

    def check_update(self):
        need_update=False
        for libname in get_libname(self.platform):
            if libname!='liblibtorrent.so':
                self.libpath = filetools.join(self.dest_path, libname)
                self.sizepath=filetools.join(self.root, self.platform['system'], self.platform['version'], libname+'.size.txt')
                size=str(filetools.getsize(self.libpath))
                size_old=open( self.sizepath, "r" ).read()
                if size_old!=size:
                    need_update=True
        return need_update

    def update(self, dest_path='', platform=''):
        if dest_path: self.dest_path = dest_path
        if platform: self.platform = platform
        if self.check_update():
            for libname in get_libname(self.platform):
                self.libpath = filetools.join(self.dest_path, libname)
                filetools.remove(self.libpath)
            self.download()

    def download(self, dest_path='', platform=''):
        if dest_path: self.dest_path = dest_path
        if platform: self.platform = platform
        ver1, ver2, ver3 = platform['version'].split('.')                       ### Alfa: resto método
        try:
            ver1 = int(ver1)
            ver2 = int(ver2)
        except:
            ver1 = 2
            ver2 = 0
        if ver1 > 1 or (ver1 == 1 and ver2 >= 2):
            global __libbaseurl__
            __libbaseurl__ = ['https://raw.githubusercontent.com/alfa-addon/alfa-repo/master/downloads/libtorrent', \
                              'https://gitlab.com/addon-alfa/alfa-repo/-/raw/master/downloads/libtorrent']
        else:
            __libbaseurl__ = ["https://github.com/DiMartinoXBMC/script.module.libtorrent/raw/master/python_libtorrent"]
            
        __settings__ = xbmcaddon.Addon(id='plugin.video.alfa')                  ### Alfa
        filetools.mkdir(self.dest_path)
        for libname in get_libname(self.platform):
            p_version = self.platform['version']
            if PY3: p_version += '_PY3'
            dest = filetools.join(self.dest_path, libname)
            log("try to fetch %s/%s/%s" % (self.platform['system'], p_version, libname))
            
            for url_lib in __libbaseurl__:                                      ### Alfa
                url = "%s/%s/%s/%s.zip" % (url_lib, self.platform['system'], p_version, libname)
                url_size = "%s/%s/%s/%s.size.txt" % (url_lib, self.platform['system'], p_version, libname)
                if libname!='liblibtorrent.so':
                    try:
                        self.http = HTTP()
                        response = self.http.fetch(url, download=dest + ".zip", progress=False)                ### Alfa
                        log("%s -> %s" % (url, dest))
                        if response.code != 200: continue                                      ### Alfa
                        response = self.http.fetch(url_size, download=dest + '.size.txt', progress=False)      ### Alfa
                        log("%s -> %s" % (url_size, dest + '.size.txt'))
                        if response.code != 200: continue                                      ### Alfa
                        
                        try:
                            unzipper = ziptools.ziptools()
                            unzipper.extract("%s.zip" % dest, self.dest_path)
                        except:
                            xbmc.executebuiltin('Extract("%s.zip","%s")' % (dest, self.dest_path))
                            time.sleep(1)
                        if filetools.exists(dest):
                            filetools.remove(dest + ".zip")
                    except:
                        import traceback
                        text = 'Failed download %s!' % libname
                        log(text)
                        log(traceback.format_exc(1))
                        #xbmc.executebuiltin("Notification(%s,%s,%s,%s)" % (__plugin__,text,750,__icon__))
                        continue
                else:
                    filetools.copy(filetools.join(self.dest_path, 'libtorrent.so'), dest, silent=True)    ### Alfa
                
                #dest_alfa = filetools.join(filetools.translatePath(__settings__.getAddonInfo('Path')), \
                #                'lib', libname)                                 ### Alfa
                #filetools.copy(dest, dest_alfa, silent=True)                    ### Alfa
                dest_alfa = filetools.join(filetools.translatePath(__settings__.getAddonInfo('Profile')), \
                                'bin', libname)                                 ### Alfa
                filetools.remove(dest_alfa, silent=True)
                filetools.copy(dest, dest_alfa, silent=True)                    ### Alfa
                break
            else:
                return False

        return True

    def android_workaround(self, new_dest_path):                                ### Alfa (entera)

        for libname in get_libname(self.platform):
            libpath = filetools.join(self.dest_path, libname)
            size = str(filetools.getsize(libpath))
            new_libpath = filetools.join(new_dest_path, libname)

            if filetools.exists(new_libpath):
                new_size = str(filetools.getsize(new_libpath))
                if size != new_size:
                    res = filetools.remove(new_libpath, su=True)
                    if res:
                        log('Deleted: (%s) %s -> (%s) %s' %(size, libpath, new_size, new_libpath))
                    
            if not filetools.exists(new_libpath):
                res = filetools.copy(libpath, new_libpath, ch_mod='777', su=True)   ### ALFA

            else:
                log('Module exists.  Not copied... %s' % new_libpath)           ### ALFA

        return new_dest_path
