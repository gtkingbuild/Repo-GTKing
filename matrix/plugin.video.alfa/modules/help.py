# -*- coding: utf-8 -*-

import os

from core.item import Item
from platformcode import config, logger, platformtools
from channelselector import get_thumb

if config.is_xbmc():

    import xbmcgui

    class TextBox(xbmcgui.WindowXMLDialog):
        """ Create a skinned textbox window """
        def __init__(self, *args, **kwargs):
            self.title = kwargs.get('title')
            self.text = kwargs.get('text')
            self.doModal()

        def onInit(self):
            try:
                self.getControl(5).setText(self.text)
                self.getControl(1).setLabel(self.title)
            except:
                pass

        def onClick(self, control_id):
            pass

        def onFocus(self, control_id):
            pass

        def onAction(self, action):
            # self.close()
            if action in [xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_NAV_BACK]:
                self.close()


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(module=item.module, action="", title="FAQ:",
                         thumbnail=get_thumb("help.png"),
                         folder=False))
    if config.is_xbmc():
        itemlist.append(Item(module=item.module, action="faq",
                             title="    - ¿Cómo reportar un error?",
                             thumbnail=get_thumb("help.png"),
                             folder=False, extra="report_error"))
    itemlist.append(Item(module=item.module, action="faq",
                         title="    - ¿Se pueden activar/desactivar los canales?",
                         thumbnail=get_thumb("help.png"),
                         folder=False, extra="onoff_canales"))
    itemlist.append(Item(module=item.module, action="faq",
                         title="    - ¿Es posible la sincronización automática con Trakt?",
                         thumbnail=get_thumb("help.png"),
                         folder=False, extra="trakt_sync"))
    itemlist.append(Item(module=item.module, action="faq",
                         title="    - ¿Es posible mostrar todos los resultados juntos en el buscador global?",
                         thumbnail=get_thumb("help.png"),
                         folder=False, extra="buscador_juntos"))
    itemlist.append(Item(module=item.module, action="faq",
                         title="    - Los enlaces tardan en aparecer.",
                         thumbnail=get_thumb("help.png"),
                         folder=False, extra="tiempo_enlaces"))
    itemlist.append(Item(module=item.module, action="faq",
                         title="    - La búsqueda de contenido no se hace correctamente.",
                         thumbnail=get_thumb("help.png"),
                         folder=False, extra="prob_busquedacont"))
    itemlist.append(Item(module=item.module, action="faq",
                         title="    - Algún canal no funciona correctamente.",
                         thumbnail=get_thumb("help.png"),
                         folder=False, extra="canal_fallo"))
    itemlist.append(Item(module=item.module, action="faq",
                         title="    - Los enlaces Torrent no funcionan.",
                         thumbnail=get_thumb("help.png"),
                         folder=False, extra="prob_torrent"))
    itemlist.append(Item(module=item.module, action="faq",
                         title="    - No se actualiza correctamente la videoteca.",
                         thumbnail=get_thumb("help.png"),
                         folder=True, extra="prob_bib"))
    itemlist.append(Item(module=item.module, action="faq",
                         title="    - Enlaces de interés",
                         thumbnail=get_thumb("help.png"),
                         folder=False, extra=""))

    return itemlist


def faq(item):

    if item.extra == "onoff_canales":
        respuesta = platformtools.dialog_yesno("Alfa",
                                               "Esto se puede hacer en 'Configuración'>'Activar/Desactivar canales'. "
                                               "Puedes activar/desactivar los canales uno por uno o todos a la vez. ",
                                               "¿Deseas gestionar ahora los canales?")
        if respuesta == 1:
            from modules import setting
            setting.conf_tools(Item(extra='channels_onoff'))

    elif item.extra == "trakt_sync":
        respuesta = platformtools.dialog_yesno("Alfa",
                                               "Actualmente se puede activar la sincronización (silenciosa) "
                                               "tras marcar como visto un episodio (esto se hace automáticamente). "
                                               "Esta opción se puede activar en 'Configuración'>'Ajustes "
                                               "de la videoteca'.",
                                               "¿Deseas acceder a dichos ajustes?")
        if respuesta == 1:
            from channels import videolibrary
            videolibrary.channel_config(Item(module='videolibrary'))

    elif item.extra == "tiempo_enlaces":
        respuesta = platformtools.dialog_yesno("Alfa",
                                               "Esto puede mejorarse limitando el número máximo de "
                                               "enlaces o mostrandolos en una ventana emergente. "
                                               "Estas opciones se encuentran en 'Configuración'>'Ajustes "
                                               "de la videoteca'.",
                                               "¿Deseas acceder a dichos ajustes?")
        if respuesta == 1:
            from channels import videolibrary
            videolibrary.channel_config(Item(module='videolibrary'))

    elif item.extra == "prob_busquedacont":
        title = "Alfa - FAQ - %s" % item.title[6:]
        text = ("Puede que no hayas escrito la ruta de la librería correctamente en "
                "'Configuración'>'Preferencias'.\n"
                "La ruta específicada debe ser exactamente la misma de la 'fuente' "
                "introducida en 'Archivos' de la videoteca de Kodi.\n"
                "AVANZADO: Esta ruta también se encuentra en 'sources.xml'.\n"
                "También puedes estar experimentando problemas por estar "
                "usando algun fork de Kodi y rutas con 'special://'. "
                "SPMC, por ejemplo, tiene problemas con esto, y no parece tener solución, "
                "ya que es un problema ajeno a Alfa que existe desde hace mucho.\n"
                "Puedes intentar subsanar estos problemas en 'Configuración'>'Ajustes de "
                "la videoteca', cambiando el ajuste 'Realizar búsqueda de contenido en' "
                "de 'La carpeta de cada serie' a 'Toda la videoteca'."
                "También puedes acudir a 'http://alfa-addon.com' en busca de ayuda.")

        return TextBox("DialogTextViewer.xml", os.getcwd(), "Default", title=title, text=text)

    elif item.extra == "canal_fallo":
        title = "Alfa - FAQ - %s" % item.title[6:]
        text = ("Puede ser que la página web del canal no funcione. "
                "En caso de que funcione la página web puede que no seas el primero"
                " en haberlo visto y que el canal este arreglado. "
                "Puedes mirar en 'alfa-addon.com' o en el "
                "repositorio de GitHub (github.com/alfa-addon/addon). "
                "Si no encuentras el canal arreglado puedes reportar un "
                "problema en el foro.")

        return TextBox("DialogTextViewer.xml", os.getcwd(), "Default", title=title, text=text)

    elif item.extra == "prob_bib":
        platformtools.dialog_ok("Alfa",
                                "Puede ser que hayas actualizado el plugin recientemente "
                                "y que las actualizaciones no se hayan aplicado del todo "
                                "bien. Puedes probar en 'Configuración'>'Otras herramientas', "
                                "comprobando los archivos *_data.json o "
                                "volviendo a añadir toda la videoteca.")

        respuesta = platformtools.dialog_yesno("Alfa",
                                               "¿Deseas acceder ahora a esa seccion?")
        if respuesta == 1:
            itemlist = []
            from modules import setting
            new_item = Item(module="setting", action="submenu_tools", folder=True)
            itemlist.extend(setting.submenu_tools(new_item))
            return itemlist

    elif item.extra == "prob_torrent":
        title = "Alfa - FAQ - %s" % item.title[6:]
        text = ("Puedes probar descargando el modulo 'libtorrent' de Kodi o "
                "instalando algun addon como 'Quasar' o 'Torrenter', "
                "los cuales apareceran entre las opciones de la ventana emergente "
                "que aparece al pulsar sobre un enlace torrent. "
                "'Torrenter' es más complejo pero también más completo "
                "y siempre funciona.")

        return TextBox("DialogTextViewer.xml", os.getcwd(), "Default", title=title, text=text)

    elif item.extra == "buscador_juntos":
        respuesta = platformtools.dialog_yesno("Alfa",
                                               "Si. La opcion de mostrar los resultados juntos "
                                               "o divididos por canales se encuentra en "
                                               "'setting'>'Ajustes del buscador global'>"
                                               "'Otros ajustes'.",
                                               "¿Deseas acceder a ahora dichos ajustes?")
        if respuesta == 1:
            from channels import search
            search.settings("")

    elif item.extra == "report_error":
        from core import filetools
        if config.get_platform(True)['num_version'] < 14:
            log_name = "xbmc.log"
        else:
            log_name = "kodi.log"
        ruta = filetools.translatePath("special://logpath") + log_name
        title = "Alfa - FAQ - %s" % item.title[6:]
        text = ("Para reportar un problema en 'http://alfa-addon.com' es necesario:\n"
                "  - Versión que usas de Alfa.\n"
                "  - Versión que usas de kodi, mediaserver, etc.\n"
                "  - Versión y nombre del sistema operativo que usas.\n"
                "  - Nombre del skin (en el caso que uses Kodi) y si se "
                "te ha resuelto el problema al usar el skin por defecto.\n"
                "  - Descripción del problema y algún caso de prueba.\n"
                "  - Agregar el log en modo detallado, una vez hecho esto, "
                "zipea el log y lo puedes adjuntar en un post.\n\n"
                "Para activar el log en modo detallado, ingresar a:\n"
                "  - Configuración.\n"
                "  - Preferencias.\n"
                "  - En la pestaña General - Marcar la opción: Generar log detallado.\n\n"
                "El archivo de log detallado se encuentra en la siguiente ruta: \n\n"
                "%s" % ruta)

        return TextBox("DialogTextViewer.xml", os.getcwd(), "Default", title=title, text=text)

    else:
        platformtools.dialog_ok("Alfa",
                                "Entérate de novedades, consejos u opciones que desconoces en Telegram: @alfa_addon.\n"
                                "Si tienes problemas o dudas, puedes acudir al Foro: http://alfa-addon.com")


