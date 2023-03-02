# -*- coding: utf-8 -*-
# -*- Colors -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import os
import re
import xbmcgui

from platformcode import config
from platformcode import logger
from platformcode import platformtools
from platformcode import unify
from core import jsontools
from core import filetools

ACTION_SHOW_FULLSCREEN = 36
ACTION_GESTURE_SWIPE_LEFT = 511
ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_DOWN = 4
ACTION_MOVE_UP = 3

media_path = os.path.join(config.get_runtime_path(), "resources/skins/Default/media/Controls/")
styles_path = os.path.join(config.get_runtime_path(), 'resources', 'color_styles.json')


def color_selector():
    logger.info()

    list_colors = list()
    data = filetools.read("special://xbmc/system/colors.xml")
    colors = re.compile('name="([^"]+)"', re.DOTALL).findall(data)

    for color in colors:
        list_colors.append("[COLOR %s]%s[/COLOR]" % (color, color.title()))

    selected = platformtools.dialog_select("Seleccione un color", list_colors)

    if not selected:
        return
    else:
        return re.sub("\[COLOR \w+]|\[/COLOR]", "", list_colors[selected]).lower()


def show_window(item=None):
    main = Main('colors.xml', config.get_runtime_path())
    main.doModal()
    del main


class Main(xbmcgui.WindowXMLDialog):

    def onInit(self):
        self.action_exitkeys_id = [xbmcgui.ACTION_STOP, xbmcgui.ACTION_BACKSPACE, xbmcgui.ACTION_NAV_BACK]
        self.buttons = list()
        self.color = "white"
        self.preset = config.get_setting("preset_style", default="Inicial")
        self.color_schemes = unify.colors_file
        self.color_setting = self.color_schemes[self.preset]
        self.preset_mode = config.get_setting("preset_style_switch")
        self.window_title = "Titulos Inteligentes"
        if self.preset_mode:
            self.setProperty("title", "%s [%s]" % (self.window_title, self.preset.capitalize()))
        else:
            self.setProperty("title", "%s [%s]" % (self.window_title, "Personalizado"))

        posx = 20
        posy = 60
        width = 175
        height = 30
        font = "font12"

        self.label_list = ["Película", "Serie", "Año", "Servidores", "Calidad", "Valoración Alta", "Valoración Media",
                           "Valoración Baja", "Castellano", "Latino", "VOSE", "VOS", "VO", "Agregar a Videoteca",
                           "Actualizar Videoteca", "No Actualizar Videoteca"]

        self.show_sample()
        self.colorize_sample()

        label = "Inicial"
        self.style0 = xbmcgui.ControlButton(posx, posy, width, height, label, font=font, alignment=6,
                                            noFocusTexture=media_path + 'MenuItemNOFO.png',
                                            focusTexture=media_path + "MenuItemFO.png")
        self.addControl(self.style0)
        self.buttons.append(self.style0)

        posy += 32
        label = "Estilo 1"
        self.style1 = xbmcgui.ControlButton(posx, posy, width, height, label, font=font, alignment=6,
                                            noFocusTexture=media_path + 'MenuItemNOFO.png',
                                            focusTexture=media_path + "MenuItemFO.png")
        self.addControl(self.style1)
        self.buttons.append(self.style1)

        posy += 32
        label = "Estilo 2"
        self.style2 = xbmcgui.ControlButton(posx, posy, width, height, label, font=font, alignment=6,
                                            noFocusTexture=media_path + 'MenuItemNOFO.png',
                                            focusTexture=media_path + "MenuItemFO.png")
        self.addControl(self.style2)
        self.buttons.append(self.style2)

        posy += 32
        label = "All White"
        self.style3 = xbmcgui.ControlButton(posx, posy, width, height, label, font=font, alignment=6,
                                            noFocusTexture=media_path + 'MenuItemNOFO.png',
                                            focusTexture=media_path + "MenuItemFO.png")
        self.addControl(self.style3)
        self.buttons.append(self.style3)

        posy += 32
        label = "Personalizar"
        self.custom = xbmcgui.ControlButton(posx, posy, width, height, label, font=font, alignment=6,
                                            noFocusTexture=media_path + 'MenuItemNOFO.png',
                                            focusTexture=media_path + "MenuItemFO.png")
        self.addControl(self.custom)
        self.buttons.append(self.custom)

        label = "Aceptar"
        self.confirm = xbmcgui.ControlButton(400, 540, 120, 40, label, font=font, alignment=6,
                                             noFocusTexture=media_path + 'MenuItemNOFO.png',
                                             focusTexture=media_path + "MenuItemFO.png")
        self.addControl(self.confirm)
        self.buttons.append(self.confirm)

        posy = 60
        for label in self.label_list:
            self.btns = xbmcgui.ControlButton(posx, posy, width, height, label, font=font, alignment=6,
                                              noFocusTexture=media_path + 'MenuItemNOFO.png',
                                              focusTexture=media_path + "MenuItemFO.png")
            posy += 32

            self.buttons.append(self.btns)
        self.focus = 0
        self.setFocusId(self.buttons[self.focus].getId())
        posy += 50

    def show_sample(self):

        m_label = "Joker [2019] [7.5]"
        t_label = "Arrow [2012] [5.5]"
        s_label = "[Fembed] [HD] [CAST] [LAT]"
        r_label = "[2.5] [5.5] [9.0]"
        l_label = "[CAST] [LAT] [VOSE] [VOS] [VO]"
        v_label = "Agregar esta Pelicula/serie a la videoteca"
        va_label = "The Big Bang Theory"
        vna_label = "The Big Bang Theory"

        label_x = 460
        label_y = 215

        self.movie_label = xbmcgui.ControlLabel(label_x, label_y, 320, 65, m_label)
        self.addControl(self.movie_label)
        label_y += 40

        self.tv_label = xbmcgui.ControlLabel(label_x, label_y, 320, 65, t_label)
        self.addControl(self.tv_label)
        label_y += 40

        self.srv_label = xbmcgui.ControlLabel(label_x, label_y, 320, 65, s_label)
        self.addControl(self.srv_label)
        label_y += 40

        self.rate_label = xbmcgui.ControlLabel(label_x, label_y, 320, 65, r_label)
        self.addControl(self.rate_label)
        label_y += 40

        self.lang_label = xbmcgui.ControlLabel(label_x, label_y, 380, 65, l_label)
        self.addControl(self.lang_label)
        label_y += 40

        self.vlib_label = xbmcgui.ControlLabel(label_x, label_y, 380, 65, v_label)
        self.addControl(self.vlib_label)
        label_y += 40

        self.avlib_label = xbmcgui.ControlLabel(label_x, label_y, 380, 65, va_label)
        self.addControl(self.avlib_label)
        label_y += 40

        self.navlib_label = xbmcgui.ControlLabel(label_x, label_y, 380, 65, vna_label)
        self.addControl(self.navlib_label)

    def onAction(self, action):

        if action == ACTION_PREVIOUS_MENU or action == ACTION_GESTURE_SWIPE_LEFT or action == 110 or action == 92:
            if not self.custom.isVisible():
                self.removeControls(self.buttons[6:])
                self.custom.setVisible(True)
                self.style0.setVisible(True)
                self.style1.setVisible(True)
                self.style2.setVisible(True)
                self.style3.setVisible(True)
            else:
                self.close()

        if action == ACTION_MOVE_DOWN:
            self.focus += 1
            if self.focus > len(self.buttons) - 1 or not self.buttons[self.focus].isVisible():
                self.focus = 0

            while True:
                if self.buttons[self.focus].isVisible():
                    self.setFocus(self.buttons[self.focus])
                    break
                self.focus += 1

        if action == ACTION_MOVE_UP:
            self.focus -= 1
            if self.focus < 0:
                self.focus = len(self.buttons) - 1
            while True:
                if self.buttons[self.focus].isVisible():
                    self.setFocus(self.buttons[self.focus])
                    break
                self.focus -= 1

        if action == ACTION_MOVE_RIGHT:
            self.last_focus = self.focus
            self.focus = 3
            self.setFocusId(self.buttons[3].getId())

        if action == ACTION_MOVE_LEFT:
            if self.getFocus().getLabel() == "Aceptar":
                if self.buttons[self.last_focus].isVisible():
                    self.setFocusId(self.buttons[self.last_focus].getId())
                    self.focus = self.last_focus
                else:
                    self.setFocusId(self.buttons[0].getId())
                    self.focus = 0

    def colorize_sample(self):

        dict_set = {u"Valoración Alta": ["rating_3", 2],
                    u"Valoración Media": ["rating_2", 1],
                    u"Valoración Baja": ["rating_1", 0],
                    "Castellano": ["cast", 0],
                    "Latino": ["lat", 1],
                    "VOSE": ["vose", 2],
                    "VOS": ["vos", 3],
                    "VO": ["vo", 4]}

        if config.get_setting("preset_style_switch", False):
            for k, v in self.color_setting.items():
                config.set_setting("%s_color" % k, "[COLOR %s]%s[/COLOR]" % (v, v))

        self.change(self.movie_label, 0, "movie_color", mode="get")
        self.change(self.tv_label, 0, "tvshow_color", mode="get")
        self.change(self.movie_label, 1, "year_color", mode="get")
        self.change(self.tv_label, 1, "year_color", mode="get")
        self.change(self.srv_label, 0, "server_color", mode="get")
        self.change(self.srv_label, 1, "quality_color", mode="get")

        for k, v in dict_set.items():

            if "Valoración" not in k:
                self.change(self.lang_label, dict_set[k][1], "%s_color" % dict_set[k][0], mode="get")
                if k == "Castellano":
                    self.change(self.srv_label, 2, "%s_color" % dict_set[k][0], mode="get")
                elif k == "Latino":
                    self.change(self.srv_label, 3, "%s_color" % dict_set[k][0], mode="get")
            else:
                self.change(self.rate_label, dict_set[k][1], "%s_color" % dict_set[k][0], mode="get")
                if "Alta" in k:
                    self.change(self.movie_label, 2, "%s_color" % dict_set[k][0], mode="get")
                elif "Media" in k:
                    self.change(self.tv_label, 2, "%s_color" % dict_set[k][0], mode="get")

        self.change(self.vlib_label, "full", "library_color", mode="get")
        self.change(self.avlib_label, "full", "update_color", mode="get")
        self.change(self.navlib_label, "full", "no_update_color", mode="get")

    def change(self, label, pos, id, mode="set"):

        self.color_setting = self.color_schemes[self.preset]
        logger.debug(id)
        if mode == "get":
            if self.preset_mode:
                self.color = re.sub(r"\[COLOR \w+]|\[/COLOR]", "", self.color_setting[id.replace("_color", "")])
            else:
                if config.get_setting(id):
                    self.color = re.sub(r"\[COLOR \w+]|\[/COLOR]", "", config.get_setting(id))
                else:
                    config.set_setting(id, "white")
                    self.color = re.sub(r"\[COLOR \w+]|\[/COLOR]", "", config.get_setting(id))

        config.set_setting(id, "[COLOR %s]%s[/COLOR]" % (self.color, self.color))
        if pos != "full":
            mod_label = label.getLabel().replace("COLOR ", "COLOR|")
            parts = mod_label.split(" ")
            parts[pos] = re.sub("\[COLOR\|\w+]|\[/COLOR]", "", parts[pos])
            parts[pos] = "[COLOR %s]%s[/COLOR]" % (self.color, parts[pos])
            new_label = "".join(map(lambda w: w + " ", parts)).strip()
            label.setLabel(new_label.replace("|", " "))

        else:
            mod_label = label.getLabel()
            mod_label = re.sub("\[COLOR \w+]|\[/COLOR]", "", mod_label)
            new_label = "[COLOR %s]%s[/COLOR]" % (self.color, mod_label)
            label.setLabel(new_label)

    def onClick(self, control):

        if control == 3070 or self.getControl(control).getLabel() == "Aceptar":
            config.set_setting("unify", True)
            return self.close()

        dict_set = {u"Valoración Alta": ["rating_3", 2],
                    u"Valoración Media": ["rating_2", 1],
                    u"Valoración Baja": ["rating_1", 0],
                    "Castellano": ["cast", 0],
                    "Latino": ["lat", 1],
                    "VOSE": ["vose", 2],
                    "VOS": ["vos", 3],
                    "VO": ["vo", 4]}

        control = self.getControl(control).getLabel()

        if control in ["Personalizar", "Inicial", "Estilo 1", "Estilo 2", "All White"]:
            config.set_setting("title_color", "true")

            if control == "Personalizar":
                config.set_setting("preset_style_switch", False)
                self.setProperty("title", "%s [%s]" % (self.window_title, "Personalizado"))
                self.preset_mode = False
                self.custom.setVisible(False)
                self.style0.setVisible(False)
                self.style1.setVisible(False)
                self.style2.setVisible(False)
                self.style3.setVisible(False)
                self.addControls(self.buttons[6:])
                self.setFocusId(self.buttons[self.focus].getId() + 2)
                self.focus = self.focus + 2

            if "Estilo" in control or 'Inicial' in control or 'White' in control:
                config.set_setting("preset_style_switch", True)
                self.preset_mode = True
                if control == "Inicial":
                    config.set_setting("preset_style", "Inicial")
                    self.preset = "Inicial"

                elif control == "Estilo 1":
                    config.set_setting("preset_style", "Estilo 1")
                    self.preset = "Estilo 1"

                elif control == "Estilo 2":
                    config.set_setting("preset_style", "Estilo 2")
                    self.preset = "Estilo 2"
                
                elif control == "All White":
                    config.set_setting("preset_style", "All White")
                    self.preset = "All White"
                
                self.setProperty("title", "%s [%s]" % (self.window_title, self.preset))
                self.colorize_sample()
                return

        else:
            self.color = color_selector()

        if control == "Película":
            self.change(self.movie_label, 0, "movie_color")

        elif control == "Serie":
            self.change(self.tv_label, 0, "tvshow_color")

        elif control == "Año":
            self.change(self.movie_label, 1, "year_color")
            self.change(self.tv_label, 1, "year_color")

        elif control == "Servidores":
            self.change(self.srv_label, 0, "server_color")

        elif control == "Calidad":
            self.change(self.srv_label, 1, "quality_color")

        elif control in dict_set:
            if "Valoración" not in control:
                self.change(self.lang_label, dict_set[control][1], "%s_color" % dict_set[control][0])
                if control == "Castellano":
                    self.change(self.srv_label, 2, "%s_color" % dict_set[control][0])
                elif control == "Latino":
                    self.change(self.srv_label, 3, "%s_color" % dict_set[control][0])
            else:
                self.change(self.rate_label, dict_set[control][1], "%s_color" % dict_set[control][0])
                if "Alta" in control:
                    self.change(self.movie_label, 2, "%s_color" % dict_set[control][0])
                elif "Media" in control:
                    self.change(self.tv_label, 2, "%s_color" % dict_set[control][0])

        elif "Agregar" in control:
            self.change(self.vlib_label, "full", "library_color")

        elif control == "Actualizar Videoteca":
            self.change(self.avlib_label, "full", "update_color")

        elif control == "No Actualizar Videoteca":
            self.change(self.navlib_label, "full", "no_update_color")
