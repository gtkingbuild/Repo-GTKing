# -*- coding: utf-8 -*-#
# -*- Based on source code from Kodi On Demand (KOD) addon -*-#

import xbmc, xbmcgui, os, sys
import re
from platformcode import config, platformtools, logger
from time import time, sleep
from core import jsontools, filetools
from concurrent import futures
from core.item import Item
from platformcode.launcher import play_from_library
from threading import Thread

ND = 'NextDialogCompact.xml' if config.get_setting('next_ep_type') else 'NextDialog.xml'


def check(item):
    return True if config.get_setting('next_ep') > 0 and item.contentType != 'movie' else False


def return_item(item):
    logger.info()
    with futures.ThreadPoolExecutor() as executor:
        future = executor.submit(next_ep, item)
        item = future.result()
    return item


def run(item):
    logger.info()
    with futures.ThreadPoolExecutor() as executor:
        future = executor.submit(next_ep, item)
        item = future.result()
    if item.next_ep:
        return play_from_library(item)


def videolibrary(item):
    item.videolibrary = True
    Thread(target=next_ep, args=[item]).start()


def next_ep(item):
    logger.info()

    item.next_ep = False
    item.show_server = True

    VL = True if item.videolibrary else False

    time_over = False
    time_limit = time() + 30
    TimeFromEnd = config.get_setting('next_ep_seconds')

    # wait until the video plays
    while not platformtools.is_playing() and time() < time_limit:
        sleep(1)

    while platformtools.is_playing() and not time_over:
        try:
            Total = xbmc.Player().getTotalTime()
            Actual = xbmc.Player().getTime()
            Difference = Total - Actual
            if Total > TimeFromEnd >= Difference:
                time_over = True
        except:
            break

    if time_over:

        # check i next file exist
        current_filename = os.path.basename(item.strm_path)
        base_path = os.path.basename(os.path.normpath(os.path.dirname(item.strm_path)))
        path = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_tvshows"),base_path)
        fileList = []
        strmList = []
        for file in os.listdir(path):
            if file.endswith('.strm'):
                fileList.append(file)

        for strm in fileList:
            se = re.search(r"(\d+)x(\d+)", strm)
            se = se.group(0).split("x")
            strmList.append([int(se[0]), int(se[1]), strm])
        strmList = sorted(strmList, key=lambda s: (s[0], s[1]))

        for index, value in enumerate(strmList):
            if current_filename == value[2]:
                nextIndex = index + 1
                break

        if nextIndex == 0 or nextIndex == len(strmList):
            next_file = None
        else:
            next_file = strmList[nextIndex][2]

        # start next episode window after x time
        if next_file:
            season = strmList[nextIndex][0]
            episode = strmList[nextIndex][1]
            next_ep = '%sx%s' % (season, str(episode).zfill(2))
            info_file = next_file.replace("strm", "nfo")
            item = Item(
                action='play_from_library',
                module='videolibrary',
                contentEpisodeNumber=episode,
                contentSeason=season,
                contentTitle=next_ep,
                contentType='episode',
                infoLabels={'episode': episode, 'mediatype': 'episode', 'season': season, 'title': next_ep},
                strm_path=filetools.join(base_path, next_file))

            global INFO
            INFO = filetools.join(path, info_file)

            nextDialog = NextDialog(ND, config.get_runtime_path())
            nextDialog.show()
            while platformtools.is_playing() and not nextDialog.is_still_watching():
                xbmc.sleep(100)
                pass

            nextDialog.close()
            logger.info('Next Episode: ' +str(nextDialog.stillwatching))

            if nextDialog.stillwatching or nextDialog.continuewatching:
                item.next_ep = True
                xbmc.Player().stop()
                if VL:
                    sleep(1)
                    xbmc.executebuiltin('Action(Back)')
                    sleep(0.5)

                    return play_from_library(item)
            else:
                item.show_server = False
                if VL:
                    sleep(1)
                    xbmc.executebuiltin('Action(Back)')
                    sleep(0.5)
                    return None

    return item


class NextDialog(xbmcgui.WindowXMLDialog):

    cancel = False
    stillwatching = False
    continuewatching = True

    def __init__(self, *args, **kwargs):
        logger.info()
        self.action_exitkeys_id = [xbmcgui.ACTION_STOP, xbmcgui.ACTION_BACKSPACE, xbmcgui.ACTION_PREVIOUS_MENU,
                                   xbmcgui.ACTION_NAV_BACK]
        self.progress_control = None
        self.set_info()

    def set_info(self):

        with open(INFO, 'r') as f:
            full_info = f.readlines()
            full_info = full_info[1:]
        full_info = "".join(full_info)
        info = jsontools.load(full_info)
        info = info["infoLabels"]
        next_title = "%s - (%sx%s)" % (info["tvshowtitle"], info["season"], str(info["episode"]).zfill(2))
        self.setProperty("next_title", next_title)
        self.setProperty("epi_title", info["title"])
        if "episodio_imagen" in info:
            img = info["episodio_imagen"]
        else:
            img = filetools.join(config.get_runtime_path(), "resources", "noimage.png")
        self.setProperty("next_img", img)

    def set_still_watching(self, stillwatching):
        self.stillwatching = stillwatching

    def set_continue_watching(self, continuewatching):
        self.continuewatching = continuewatching

    def is_still_watching(self):
        return self.stillwatching

    def onFocus(self, controlId):
        pass

    def doAction(self):
        pass

    def closeDialog(self):
        self.close()

    def onClick(self, controlId):
        if controlId == 3012:  # Still watching
            self.set_still_watching(True)
            self.set_continue_watching(False)
            self.close()
        elif controlId == 3013:  # Cancel
            self.set_continue_watching(False)
            self.close()

    def onAction(self, action):
        logger.info()
        if action in self.action_exitkeys_id:
            self.set_continue_watching(False)
            self.close()
