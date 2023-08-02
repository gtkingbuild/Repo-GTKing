# -*- coding: utf-8 -*-

import threading
from platformcode import config


# Comprobar actualizaciones solamente una vez al iniciar Kodi, no es necesario dejar el servicio corriendo (o sí para dispositivos siempre encendidos !?)
def comprobar_actualizaciones():
    if config.get_setting('addon_update_atstart', default=False):
        from platformcode import updater
        updater.check_addon_updates(verbose=config.get_setting('addon_update_verbose', default=False))

threading.Thread(target=comprobar_actualizaciones).start()


# Lanzar servicio para comprobar nuevos capítulos
def comprobar_nuevos_episodios():
    if config.get_setting('addon_tracking_atstart', default=True):
        interval = int(config.get_setting('addon_tracking_interval', default='12')) * 3600 # horas convertidas a segundos

        import xbmc, time
        from core import trackingtools

        monitor = xbmc.Monitor()
        while not monitor.abortRequested():
            if config.get_setting('addon_tracking_atstart', default=True): # por si se desactiva con el servicio ejecutándose
                lastscrap = config.get_setting('addon_tracking_lastscrap', default='')
                if lastscrap == '' or float(lastscrap) + interval <= time.time():
                    trackingtools.check_and_scrap_new_episodes(notification=config.get_setting('addon_tracking_verbose', default=False))

            if monitor.waitForAbort(3600):
                break

threading.Thread(target=comprobar_nuevos_episodios).start()

