# -*- coding: utf-8 -*-
# -*- Configurator -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import os
import xbmcgui
import xbmcaddon
from platformcode import config
from platformcode import logger
from platformcode import xbmc_videolibrary
from core.item import Item

addon = xbmcaddon.Addon("plugin.video.alfa")
icon = addon.getAddonInfo("icon")

media_path = media_path = os.path.join(config.get_runtime_path(), "resources/skins/Default/media/Controls/")

ACTION_SHOW_FULLSCREEN = 36
ACTION_GESTURE_SWIPE_LEFT = 511
ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_DOWN = 4
ACTION_MOVE_UP = 3

def show_window():
    main = Main('configurator.xml', config.get_runtime_path())
    main.doModal()
    del main


class Main(xbmcgui.WindowXMLDialog):

    def onInit(self):


        self.action_exitkeys_id = [xbmcgui.ACTION_STOP, xbmcgui.ACTION_BACKSPACE, xbmcgui.ACTION_PREVIOUS_MENU,
                                   xbmcgui.ACTION_NAV_BACK]

        self.font = "font25_title"
        self.shadow = "0xFF504416"
        self.open_greeter()

    def main_window(self):

        self.buttons = list()
        self.setProperty("title", "Alfa - Configuración inicial")
        label = "Continuar"
        btn = xbmcgui.ControlButton(450, 540, 120, 40, label, font=self.font, alignment=6, shadowColor=self.shadow,
                                             noFocusTexture=media_path + 'MenuItemNOFO.png',
                                             focusTexture=media_path + "MenuItemFO.png")
        self.addControl(btn)
        self.buttons.append(btn)

        posx = 20
        posy = 50
        width = 180
        height = 60
        labels = ["videoteca", "cliente torrent", "titulos inteligentes", "set de iconos", "ajustes Avanzados"]

        for label in labels:
            btn = xbmcgui.ControlButton(posx, posy, width, height, label.title(), font=self.font, alignment=6,
                                              shadowColor=self.shadow, noFocusTexture=media_path + 'MenuItemNOFO.png',
                                              focusTexture=media_path + "MenuItemFO.png", textColor="0xFFFFFFFF")

            self.addControl(btn)
            self.buttons.append(btn)
            posy += 70

        self.hand = xbmcgui.ControlImage(0, 0, 40, 40, media_path + "click.png")

        self.addControl(self.hand)
        self.hand.setVisible(False)
        self.hand.setAnimations(
            [("isVisible", "effect=zoom delay=120 center=auto start=80 end=50  time=350 loop=true condition=true")])

        self.setFocus(self.buttons[1])
        self.focus = 1

    def open_greeter(self):

        self.getControl(3071).setPosition(100, 0)
        self.getControl(3071).setWidth(795)
        self.getControl(3071).setHeight(600)

        self.getControl(3072).setPosition(100, 0)
        self.getControl(3072).setWidth(795)
        self.getControl(3072).setHeight(40)

        self.getControl(3072).setVisible(False)
        self.getControl(3075).setVisible(False)
        self.getControl(3076).setVisible(False)
        self.getControl(3077).setPosition(120, 310)
        self.getControl(3077).setWidth(740)
        self.getControl(3077).setHeight(600)
        self.getControl(3078).setPosition(100, 0)
        self.getControl(3078).setWidth(795)
        self.getControl(3078).setHeight(220)
        self.getControl(3078).setImage("https://i.postimg.cc/GmPN7R9G/M7f-DTp-Dn-Jc-Z4dt3myngzxi.jpg")

        self.getControl(3074).setImage(icon)
        self.welcome = xbmcgui.ControlLabel(120, 240, 755, 60, "Te damos la bienvenida a Alfa!", alignment=6,
                                            font="font52_title")
        self.addControl(self.welcome)

        label = "Alfa es un proyecto open source que permite acceder a contenido de diferentes paginas web de manera " \
                "cómoda y sencilla utilizando kodi.\n\n[I]ALFA NO POSEE CONTENIDO PROPIO, SOLO LISTA CONTENIDO DE INTERNET\n" \
                "ES TOTALMENTE GRATUITO, NO DEBES PAGAR POR EL.[/I]\n\n" \
                "Problemas?, Dudas?, Sugerencias? => [COLOR gold]https://alfa-addon.com[/COLOR]\n\n" \
                "Nuestro canal de telegram => [COLOR gold]@alfa_addon[/COLOR]"


        self.setProperty("button_info", label)

        label = "Comenzar"
        self.start_btn = xbmcgui.ControlButton(430, 540, 120, 40, label, font=self.font, alignment=6, shadowColor=self.shadow,
                                          noFocusTexture=media_path + 'MenuItemNOFO.png',
                                          focusTexture=media_path + "MenuItemFO.png")
        self.addControl(self.start_btn)
        self.setFocus(self.start_btn)


    def close_greeter(self):
        self.removeControl(self.start_btn)
        self.removeControl(self.welcome)
        self.getControl(3074).setVisible(False)
        self.setProperty("button_info", "")
        self.getControl(3071).setPosition(0, 0)
        self.getControl(3071).setWidth(995)
        self.getControl(3071).setHeight(600)

        self.getControl(3072).setPosition(0, 0)
        self.getControl(3072).setWidth(995)
        self.getControl(3072).setHeight(40)

        self.getControl(3072).setVisible(True)
        self.getControl(3075).setVisible(True)
        self.getControl(3076).setVisible(True)
        self.getControl(3077).setPosition(250, 230)
        self.getControl(3077).setWidth(700)
        self.getControl(3077).setHeight(300)
        self.getControl(3078).setPosition(220, 50)
        self.getControl(3078).setWidth(760)
        self.getControl(3078).setHeight(150)
        self.getControl(3078).setImage("")
        self.main_window()

    def onFocus(self, control):
        animate = False
        control_label = self.getControl(control).getLabel()
        if control_label == "Videoteca":

            animate = True

            btn_info = "[B] - Configura la videoteca de Alfa - [/B]\n\n\nPodrás hacer seguimiento de tus series," \
                       " llevar el control de los episodios vistos, recibir actualizaciones de episodios de series" \
                       " en emisión y mas!\n\n" \
                       " - Escoge un proveedor de información para películas y configura tu idioma.\n " \
                       "- Escoge un proveedor de información para series y configura tu idioma.\n\n " \
                       "Ya puedes disfrutar de tu videoteca!"

            self.setProperty("button_info", btn_info)
            self.getControl(3078).setImage("https://i.postimg.cc/ht3BL9F1/ss6.png")

        elif control_label == "Cliente Torrent":

            animate = True

            btn_info = "[B] - Configura tu cliente para reproducir torrents - [/B]\n\n\n - Escoge tu cliente por defecto.\n "\
                       "- Configura también otras opciones relacionadas a este tipo de contenido."

            self.setProperty("button_info", btn_info)
            self.getControl(3078).setImage("https://i.postimg.cc/nLChjPFR/ss90.png")

        elif control_label == "Titulos Inteligentes":

            animate = True

            btn_info = "[B] - Activa Títulos inteligentes - [/B]\n\n\nObtendrás información mas clara sobre el contenido " \
                       "(año, puntuación, sinopsis), todo diferenciado por colores.\n\n" \
                       "- Escoge un estilo de color predefinido o personaliza de manera sencilla."

            self.setProperty("button_info", btn_info)
            self.getControl(3078).setImage("https://i.postimg.cc/QCbLH7k5/ss7.png")

        elif control_label == "Set De Iconos":

            animate = True

            btn_info = "[B] - Escoge tu set de iconos favorito - [/B]\n\n\nAlfa cuenta con varios temas de iconos entre " \
                       "los cuales puedes escoger, elige el que mas te guste y disfruta tu alfa mas bonito."

            self.setProperty("button_info", btn_info)
            self.getControl(3078).setImage("https://i.postimg.cc/T1TFMwMP/ss3.png")

        elif control_label == "Ajustes Avanzados":

            animate = True

            btn_info = "[B] - Configura Alfa al Máximo - [/B]\n\n\nPuedes utilizar la configuración avanzada para ajustar " \
                       "muchos mas aspectos y funciones del addon."

            self.setProperty("button_info", btn_info)
            self.getControl(3078).setImage("https://i.postimg.cc/3wLMQ82W/0.jpg")
        elif control_label == "Comenzar":
            pass
        else:
                self.hand.setVisible(False)

        if animate:
            self.hand.setPosition(self.getControl(control).getX() + 140, self.getControl(control).getY() + 35)
            self.hand.setVisible(True)


    def onAction(self, action):

        if action == ACTION_PREVIOUS_MENU or action == ACTION_GESTURE_SWIPE_LEFT or action == 110 or action == 92:
            config.set_setting("show_once", True)
            self.close()

        if action == ACTION_MOVE_DOWN:
            self.focus += 1
            if self.focus > len(self.buttons) - 1:
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


    def onClick(self, control):
        if control == 3075:
            config.set_setting("show_once", True)
            self.close()
        control = self.getControl(control).getLabel().lower()
        if control == "comenzar":
            self.close_greeter()
        elif control == "videoteca":
            xbmc_videolibrary.ask_set_content(1, silent=True)
            config.set_setting('show_once', True)
        elif control == "cliente torrent":
            from modules import setting
            setting.setting_torrent(Item())
        elif control == "titulos inteligentes":
            from platformcode import colors
            from platformcode import unify
            unify.init_colors()
            colors.show_window()
        elif control == "set de iconos":
            from modules import setting
            setting.icon_set_selector()
        elif control == "ajustes avanzados":
            self.close()
            config.open_settings()

        elif control == "continuar":
            config.set_setting("show_once", True)
            from platformcode import envtal
            envtal.list_env()
            self.close()
