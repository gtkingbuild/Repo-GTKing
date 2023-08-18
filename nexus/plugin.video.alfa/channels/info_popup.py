# -*- coding: utf-8 -*-
# -*- Channel infoPopup -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from core.item import Item
from core import tmdb
from core import jsontools
from core import filetools
from platformcode import logger
from platformcode import config
from platformcode import platformtools
from channelselector import get_thumb
import os
import sys
import sqlite3
import datetime
import xbmc
import xbmcgui
from channels import news
from lib import strptime_fix
from concurrent import futures
from threading import Thread
from platformcode import help_window

db_path = os.path.join(config.get_data_path(), "available.sqlite")

class notifyWindow(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        self.no_image = filetools.join(config.get_runtime_path(), "resources", "noimage.png")
        self.results = kwargs["data"]
        self.current = kwargs["current"]
        self.title = ""
        self.selected = list()
        self.infolabels = dict()

    def onInit(self):
        self.setFocusId(40002)
        self.show_next()
        self.infolabels = jsontools.load(self.results[self.current][1])
        self.title = self.infolabels["title"]
        rating = self.infolabels.get("rating", "N/D")
        thumb = self.infolabels.get("thumbnail", self.no_image)
        self.getControl(2).setText(self.infolabels.get("plot", "No disponible"))
        self.setProperty("title", "[B]%s  (%s)  %s[/B]" % (self.infolabels["title"], self.infolabels["year"], rating))

        self.wish = self.results[self.current][4]
        if not self.wish:
            self.getControl(40002).setLabel("Guardar")
        else:
            self.selected.append(self.infolabels["tmdb_id"])
            self.getControl(40002).setLabel("Quitar")

        self.getControl(40000).setImage(thumb)
        if self.current == 0:
            self.getControl(40001).setVisible(False)
        if len(self.results) <= 1:
            self.getControl(40003).setVisible(False)


    def onAction(self, action):
        if action in [xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_NAV_BACK]:
            self.close()

        if self.current <= 0:
            self.getControl(40001).setVisible(False)
        else:
            self.getControl(40001).setVisible(True)

        if self.current >= len(self.results) - 1:
            self.getControl(40003).setVisible(False)
        else:
            self.getControl(40003).setVisible(True)

        if self.infolabels["tmdb_id"] not in self.selected:
            self.getControl(40002).setLabel("Guardar")
        else:
            self.getControl(40002).setLabel("Quitar")

    def onClick(self, controlID):

        if controlID == 39999:
            self.close()

        if controlID == 40001:
            if self.current > 0:
                self.current -= 1
                self.show_previous()
                self.refresh()
            if self.current <= 0:
                self.setFocus(self.getControl(40002))

        if controlID == 40002:
            item = (Item(infoLabels=self.infolabels))
            if self.getControl(controlID).getLabel() == "Guardar":
                item.value = 1
                set_checked(item)
                self.selected.append(self.infolabels["tmdb_id"])
            else:
                item.value = 0
                self.getControl(controlID).setLabel("Guardar")
                self.selected.remove(self.infolabels["tmdb_id"])
                set_checked(item)

        if controlID == 40003:
            if self.current < len(self.results) - 1:
                self.current += 1
                self.show_next()
                self.refresh()
                self.getControl(40001).setVisible(True)
            if self.current >= len(self.results) - 1:
                self.setFocus(self.getControl(40002))

        if controlID == 40004:
            self.close()
            item = Item(channel="trailertools", title="buscar", infoLabels=self.infolabels,
                                            action="buscartrailer", contextual=True, current=self.current)

            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.alfa/?%s)" % item.tourl())

    def show_next(self):
        self.infolabels = self.results[self.current][1]

    def show_previous(self):
        self.infolabels = self.results[self.current][1]

    def refresh(self):
        self.infolabels = jsontools.load(self.results[self.current][1])
        self.wish = self.results[self.current][4]
        if not self.wish:
            self.getControl(40002).setLabel("Guardar")
        else:
            self.getControl(40002).setLabel("Quitar")
        self.title = self.infolabels["title"]
        rating = self.infolabels.get("rating", "N/D")
        self.getControl(2).setText(self.infolabels.get("plot", "No disponible"))
        thumb = self.infolabels.get("thumbnail", self.no_image)
        self.setProperty("title", "[B]%s  (%s)  %s[/B]" % (self.infolabels["title"], self.infolabels["year"], rating))
        self.getControl(40000).setImage(thumb)


def show_popup(item, ignore_new_wish=False, first_pass=False):
    logger.info()
    if not platformtools.is_playing():
        results = get_info(ignore_new_wish)
        if results:
            if first_pass and len(results) > 5:
                results = results[:5]
            window = notifyWindow('notify.xml', config.get_runtime_path(), data=results, current=int(item.current))
            window.doModal()
            del window


def get_info(ignore_new_wish=False):

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if not ignore_new_wish:
        c.execute('SELECT * FROM availables WHERE new=1 AND wish=0 order by "release" DESC')
    else:
        c.execute('SELECT * FROM availables WHERE new=1 order by "release" DESC')
    results = c.fetchall()
    c.close()
    return results


def autoscan():
    if not config.get_setting("autoscan", "info_popup"):
        return
    else:
        help_window.show_info("infopopup", wait=False)

    monitor = xbmc.Monitor()
    hours = [8, 12, 24]
    timer = config.get_setting("autoscan_timer", "info_popup")

    timer = hours[timer] * 3600
    while not monitor.abortRequested():

        t = Thread(target=now_available())
        t.start()

        if monitor.waitForAbort(timer):
            break


def now_available():

    itemlist = list()
    channel_list = list()
    if not platformtools.is_playing():
        channel_list.extend(news.get_channels("peliculas"))
        first_pass = check_db()
        #platformtools.dialog_notification("Alfa", "Buscando estrenos...")
        with futures.ThreadPoolExecutor() as executor:
            c_results = [executor.submit(news.get_channel_news, ch, "peliculas") for ch in channel_list]

            for index, res in enumerate(futures.as_completed(c_results)):
                try:
                    itemlist.extend(res.result()[1])
                except:
                    continue

        tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

        conn = sqlite3.connect(db_path)
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM availables")


        #if first_pass:
        #    set_new = 0
        #else:
        #    set_new = 1

        now = datetime.datetime.today()

        for elem in itemlist:
            if not elem.infoLabels["tmdb_id"] or not elem.infoLabels["release_date"]:
                continue
            release = datetime.datetime.strptime(elem.infoLabels["release_date"], "%d/%m/%Y")
            status = elem.infoLabels["status"]
            if status != "Released" or release < (now - datetime.timedelta(weeks=26.0715)):
                continue
            cursor.execute("SELECT * FROM availables WHERE tmdb_id=?", (elem.infoLabels["tmdb_id"],))
            results = cursor.fetchone()
            id = elem.infoLabels["tmdb_id"]
            release = datetime.datetime.strftime(release, "%Y/%m/%d")

            #if set_new:
            info = jsontools.dump(elem.infoLabels)
            #else:
            #    info = ""
            if results:
                continue
            else:
                cursor.execute("INSERT INTO availables (tmdb_id, info, new, release, wish)VALUES (?, ?, ?, ?, ?)",
                               (id, info, 1, release, 0))
                conn.commit()

        item = Item(channel="info_popup", current=0)
        show_popup(item, first_pass=first_pass)


def check_db():

    if filetools.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('UPDATE availables SET info="", new=0, release="" WHERE new=1 AND wish=0')
        conn.commit()
        conn.execute("VACUUM")
        conn.close()
        return False
    else:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS availables (tmdb_id, info, new, release, wish)')
        conn.commit()
        conn.close()
        return True


def mainlist(item):

    itemlist = list()
    status = config.get_setting("autoscan", item.channel)

    if not status:
        from platformcode import platformtools
        opt = platformtools.dialog_yesno("Alfa - Lista de deseos",
                                   "Para agregar elementos a esta sección necesitas activar la busqueda de estrenos y sugerencias."
                                   " Deseas activarla ahora?")
        if opt:
            config.set_setting("autoscan", True, item.channel)
            Thread(target=autoscan).start()
    if not filetools.exists(db_path):
        return itemlist
    itemlist.append(Item(channel=item.channel, title="Configuración", thumbnail=get_thumb("setting_0.png"),
                         action="show_settings"))
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM availables WHERE wish=1")
    results = c.fetchall()
    c.close()

    for x in results:
        infolabels = jsontools.load(x[1])
        infolabels["quality"] = ""
        infolabels["language"] = ""
        context = [{"title": "Quitar de la lista",
                    "action": "set_checked",
                    "channel": item.channel,
                    "contextual": True,
                    "value": 0}
                   ]
        itemlist.append(Item(channel="search",
                             action='from_context',
                             title="",
                             text=infolabels["title"],
                             contentType="movie",
                             context=context,
                             infoLabels=infolabels))

    tmdb.set_infoLabels_itemlist(itemlist[1:], seekTmdb=True)


    return itemlist


def set_checked(item):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE availables SET wish=%s WHERE tmdb_id='%s'" % (item.value, item.infoLabels["tmdb_id"]))
    conn.commit()
    c.close()
    if item.contextual:
        platformtools.itemlist_refresh()


def show_settings(item):
    platformtools.show_channel_settings()
    return
