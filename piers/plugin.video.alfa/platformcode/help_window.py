# -*- coding: utf-8 -*-#

from platformcode import config, logger
from core import filetools
from core import jsontools
import xbmc, xbmcgui
import threading
import traceback

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

info_file_path = filetools.join(config.get_runtime_path(), "resources", "help_info.json")
data_path = filetools.join(config.get_data_path(), "help_window.json")


class HelpWindow(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):

        self.title = kwargs.get('title')
        self.text = kwargs.get('text')

    def onInit(self):

        self.setFocusId(3)
        self.setProperty("title", "[B]%s[/B]" % self.title)
        self.getControl(2).setText(self.text)

    def onAction(self, action):
        if action in [xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_NAV_BACK, xbmcgui.ACTION_SELECT_ITEM]:
            self.close()

    def onClick(self, controlID):
        if controlID == 40000:
            self.close()


def show_info(id, wait=True, title="", text=""):
    
    def show_window(title, text):
        window = HelpWindow('help_window.xml', config.get_runtime_path(), title=title, text=text)
        window.doModal()
        del window
    if not title and not text:
        watched = False
        info_file = dict()
        watched_file = dict()
        ids = []

        if filetools.exists(info_file_path):
            info_file = jsontools.load(filetools.read(info_file_path))
            if filetools.exists(data_path):
                watched_file = jsontools.load(filetools.read(data_path))

        if id == 'broadcast' and info_file:
            ids = [x for x in list(info_file.keys()) if x.startswith(id)]
        ids = ids or [id]
        for id in ids:
            if watched_file.get(id, ''):
                watched = True

            if info_file.get(id, '') and not watched:
                title = info_file[id]["title"]
                text = info_file[id]["text"]
                t = threading.Thread(target=show_window, args=(title, text))
                t.start()
                if wait:
                    t.join()
                set_watched(id)
    else:
        t = threading.Thread(target=show_window, args=(title, text))
        t.start()
        if wait:
            t.join()


def set_watched(id):

    watched_file = dict()
    
    if filetools.exists(data_path) and filetools.getsize(data_path) > 0:
        watched_file = jsontools.load(filetools.read(data_path))

    watched_file[id] = "true"
    filetools.write(data_path, jsontools.dump(watched_file))
    
    
def clean_watched_new_version():
    
    try:
        info_file = dict()
        watched_file = dict()

        if filetools.exists(info_file_path):
            info_file = jsontools.load(filetools.read(info_file_path))
            if filetools.exists(data_path):
                watched_file = jsontools.load(filetools.read(data_path))
        
        for msg, values in list(info_file.items()):
            if values.get('version', False) and watched_file.get(msg):
                del watched_file[msg]
                
        watched_file_atl = watched_file.copy()
        for msg in watched_file_atl:
            if not info_file.get(msg):
                del watched_file[msg]
        
        filetools.write(data_path, jsontools.dump(watched_file))
    except:
        logger.error(traceback.format_exc())
