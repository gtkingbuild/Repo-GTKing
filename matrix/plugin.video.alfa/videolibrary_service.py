# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Service for updating new episodes on library series
# ------------------------------------------------------------

import datetime, math, threading, traceback
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


try:
    from platformcode import logger
except:
    pass

try:
    import os, time
    from platformcode import config
    librerias = os.path.join(config.get_runtime_path(), 'lib')
    sys.path.append(librerias)
    for module in ['script.module.futures']:
        if PY3: continue
        config.importer(module)
    import xbmc
except:
    xbmc = None
    logger.error(traceback.format_exc())
    
# Se activa el monitor
if xbmc:
    if config.get_platform(True)['num_version'] >= 14:
        monitor = xbmc.Monitor()  # For Kodi >= 14
    else:
        monitor = None  # For Kodi < 14


def update(path, p_dialog, i, t, serie, overwrite, redir=True):
    logger.info("Actualizando " + path)
    
    from core import filetools
    from core import channeltools, videolibrarytools
    from platformcode import platformtools
    from channels import videolibrary
    from lib import generictools
    if config.is_xbmc():
        from platformcode import xbmc_videolibrary

    insertados_total = 0
    insertados = 0
    sobreescritos = 0
    fallidos = 0
    overwrite_back = overwrite
      
    head_nfo, it = videolibrarytools.read_nfo(path + '/tvshow.nfo')
    category = serie.category

    # logger.debug("%s: %s" %(serie.contentSerieName,str(list_canales) ))
    for channel, url in list(serie.library_urls.items()):
        serie.channel = channel
        serie.url = url
        
        ###### Redirección al canal NewPct1.py si es un clone, o a otro canal y url si ha intervención judicial
        if redir:
            try:
                head_nfo, it = videolibrarytools.read_nfo(path + '/tvshow.nfo')         #Refresca el .nfo para recoger actualizaciones
                if not it:
                    logger.error('.nfo erroneo en ' + str(path))
                    continue
                if it.emergency_urls:
                    serie.emergency_urls = it.emergency_urls
                serie.category = category
                serie, it, overwrite = generictools.redirect_clone_newpct1(serie, head_nfo, it, path, overwrite)
            except:
                logger.error(traceback.format_exc())

        channel_enabled = channeltools.is_enabled(serie.channel)

        if channel_enabled:

            heading = config.get_localized_string(60389)
            p_dialog.update(int(math.ceil((i + 1) * t)), heading, "%s: %s" % (serie.contentSerieName,
                                                                              serie.channel.capitalize()))
            try:
                pathchannels = filetools.join(config.get_runtime_path(), "channels", serie.channel + '.py')
                logger.info("Cargando canal: " + pathchannels + " " +
                            serie.channel)

                if serie.library_filter_show:
                    serie.show = serie.library_filter_show.get(channel, serie.contentSerieName)
                
                if redir: serie = videolibrarytools.redirect_url(serie)

                obj = __import__('channels.%s' % serie.channel, fromlist=["channels.%s" % serie.channel])
                itemlist = getattr(obj, 'episodios')(serie)                     #... se procesa Episodios para ese canal
                
                try:
                    if monitor and monitor.waitForAbort(0.1):
                        return False
                    if int(overwrite_back) == 3:
                        # Sobrescribir todos los archivos (tvshow.nfo, 1x01.nfo, 1x01 [canal].json, 1x01.strm, etc...)
                        insertados, sobreescritos, fallidos, notusedpath = videolibrarytools.save_tvshow(serie, itemlist, 
                                                                                              silent=True, monitor=monitor, 
                                                                                              overwrite=overwrite_back)
                        #serie= videolibrary.check_season_playcount(serie, serie.contentSeason)
                        #if videolibrarytools.write_nfo(path + '/tvshow.nfo', head_nfo, it):
                        #    serie.infoLabels['playcount'] = serie.playcount
                    else:
                        insertados, sobreescritos, fallidos = videolibrarytools.save_episodes(path, itemlist, serie,
                                                                                              silent=True, monitor=monitor, 
                                                                                              overwrite=overwrite)
                        #it = videolibrary.check_season_playcount(it, it.contentSeason)
                        #if videolibrarytools.write_nfo(path + '/tvshow.nfo', head_nfo, it):
                        #    serie.infoLabels['playcount'] = serie.playcount
                    insertados_total += insertados

                except Exception as ex:
                    logger.error("Error al guardar los capitulos de la serie")
                    template = "An exception of type %s occured. Arguments:\n%r"
                    message = template % (type(ex).__name__, ex.args)
                    logger.error(message)
                    logger.error(traceback.format_exc())
                    continue

            except Exception as ex:
                logger.error("Error al obtener los episodios de: %s" % serie.show)
                template = "An exception of type %s occured. Arguments:\n%r"
                message = template % (type(ex).__name__, ex.args)
                logger.error(message)
                logger.error(traceback.format_exc())
                continue
                
            # Si el canal lo permite, se comienza el proceso de descarga de los nuevos episodios descargados
            serie_d = serie.clone()
            serie_d.channel = generictools.verify_channel(serie_d.channel)
            if insertados > 0 and config.get_setting('auto_download_new', serie_d.channel, default=False) and int(overwrite_back) != 3:
                config.set_setting("search_new_content", 1, "videolibrary")     # Escaneamos a final todas la series
                serie_d.sub_action = 'auto'
                serie_d.category = itemlist[0].category
                from channels import downloads
                downloads.save_download(serie_d, silent=True)
            
            # Limpiamos restos del canal anterior
            if serie.category_alt: del serie.category_alt
            if serie.channel_host: del serie.channel_host
            if serie.channel_redir: del serie.channel_redir

        else:
            logger.debug("Canal %s no activo no se actualiza" % serie.channel)

    #Sincronizamos los episodios vistos desde la videoteca de Kodi con la de Alfa
    try:
        if config.is_xbmc() and not config.get_setting('cleanlibrary', 'videolibrary', default=False) \
                    and int(overwrite_back) != 3:                               #Si es Kodi, lo hacemos
            xbmc_videolibrary.mark_content_as_watched_on_alfa(path + '/tvshow.nfo')
    except:
        logger.error(traceback.format_exc())
    
    return insertados_total > 0


def check_for_update(overwrite=True):
    logger.info("Actualizando series...")
    
    from core import filetools, httptools
    from core import channeltools, videolibrarytools
    from platformcode import platformtools
    from channels import videolibrary
    from lib import generictools
    if config.is_xbmc():
        from platformcode import xbmc_videolibrary
    
    p_dialog = None
    serie_actualizada = False
    update_when_finished = False
    hoy = datetime.date.today()
    estado_verify_playcount_series = False
    httptools.VIDEOLIBRARY_UPDATE = True

    try:
        if config.get_setting("update", "videolibrary") != 0 or overwrite:
            config.set_setting("updatelibrary_last_check", hoy.strftime('%Y-%m-%d'), "videolibrary")

            heading = config.get_localized_string(60389)
            p_dialog = platformtools.dialog_progress_bg(config.get_localized_string(20000), heading)
            p_dialog.update(0, '')
            show_list = []

            for path, folders, files in filetools.walk(videolibrarytools.TVSHOWS_PATH):
                show_list.extend([filetools.join(path, f) for f in files if f == "tvshow.nfo"])

            if show_list:
                t = float(100) / len(show_list)

            for i, tvshow_file in enumerate(show_list):
                try:
                    if monitor and monitor.waitForAbort(0.1):
                        return
                    
                    head_nfo, serie = videolibrarytools.read_nfo(tvshow_file)
                    if not serie:
                        logger.error('.nfo erroneo en ' + str(tvshow_file))
                        continue
                    path = filetools.dirname(tvshow_file)
                    
                    ###### Redirección al canal NewPct1.py si es un clone, o a otro canal y url si ha intervención judicial
                    overwrite_forced = False
                    try:
                        serie, serie, overwrite_forced = generictools.redirect_clone_newpct1(serie, head_nfo, serie, path, overwrite, lookup=True)
                    except:
                        logger.error(traceback.format_exc())
                    if overwrite_forced == True:
                        overwrite = True
                        serie.update_next = ''
                    
                    info_status = ''
                    if serie.infoLabels['status']:
                        info_status = serie.infoLabels['status']

                    logger.info("Serie=%s, Activa=%s, Fecha=%s, Status=%s" % (serie.contentSerieName, \
                                str(serie.active), str(serie.update_last), str(info_status)))
                    p_dialog.update(int(math.ceil((i + 1) * t)), heading, serie.contentSerieName)
                    
                    #Verificamos el estado del serie.library_playcounts de la Serie por si está incompleto
                    try:
                        estado = False
                        #Si no hemos hecho la verificación o no tiene playcount, entramos
                        estado = config.get_setting("verify_playcount", "videolibrary")
                        if not estado or estado == False or not serie.library_playcounts:       #Si no se ha pasado antes, lo hacemos ahora
                            serie, estado = videolibrary.verify_playcount_series(serie, path)   #También se pasa si falta un PlayCount por completo
                    except:
                        logger.error(traceback.format_exc())
                    else:
                        if estado:                                              #Si ha tenido éxito la actualización...
                            estado_verify_playcount_series = True               #... se marca para cambiar la opción de la Videoteca

                    if serie.active:
                        try:
                            interval = int(serie.active)                        # Podria ser del tipo bool
                        except:
                            interval = 1
                    else:
                        interval = 0

                    if not serie.active:
                        # si la serie no esta activa descartar
                        if overwrite_forced == False:
                            #Sincronizamos los episodios vistos desde la videoteca de Kodi con la de Alfa, aunque la serie esté desactivada
                            try:
                                if config.is_xbmc():                #Si es Kodi, lo hacemos
                                    xbmc_videolibrary.mark_content_as_watched_on_alfa(path + '/tvshow.nfo')
                            except:
                                logger.error(traceback.format_exc())
                        
                            continue

                    # obtenemos las fecha de actualizacion y de la proxima programada para esta serie
                    update_next = serie.update_next
                    if update_next:
                        y, m, d = update_next.split('-')
                        update_next = datetime.date(int(y), int(m), int(d))
                    else:
                        update_next = hoy

                    update_last = serie.update_last
                    if update_last:
                        y, m, d = update_last.split('-')
                        update_last = datetime.date(int(y), int(m), int(d))
                    else:
                        update_last = hoy

                    # si la serie esta activa ...
                    if overwrite or config.get_setting("updatetvshows_interval", "videolibrary") == 0:
                        # ... forzar actualizacion independientemente del intervalo
                        serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)
                        if not serie_actualizada:
                            update_next = hoy + datetime.timedelta(days=interval)

                    elif interval == 1 and update_next <= hoy:
                        # ...actualizacion diaria
                        serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)
                        if not serie_actualizada and update_last <= hoy - datetime.timedelta(days=7):
                            # si hace una semana q no se actualiza, pasar el intervalo a semanal
                            interval = 7
                            update_next = hoy + datetime.timedelta(days=interval)

                    elif interval == 7 and update_next <= hoy:
                        # ...actualizacion semanal
                        serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)
                        if not serie_actualizada:
                            if update_last <= hoy - datetime.timedelta(days=14):
                                # si hace 2 semanas q no se actualiza, pasar el intervalo a mensual
                                interval = 30

                            update_next += datetime.timedelta(days=interval)

                    elif interval == 30 and update_next <= hoy:
                        # ...actualizacion mensual
                        serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)
                        if not serie_actualizada:
                            update_next += datetime.timedelta(days=interval)
                            
                    if serie_actualizada:
                        update_last = hoy
                        update_next = hoy + datetime.timedelta(days=interval)

                    if monitor and monitor.waitForAbort(0.1):
                        return
                    
                    head_nfo, serie = videolibrarytools.read_nfo(tvshow_file)   #Vuelve a leer el.nfo, que ha sido modificado
                    if interval != int(serie.active) or update_next.strftime('%Y-%m-%d') != serie.update_next or update_last.strftime('%Y-%m-%d') != serie.update_last:
                        serie.update_last = update_last.strftime('%Y-%m-%d')
                        if update_next > hoy:
                            serie.update_next = update_next.strftime('%Y-%m-%d')
                        if serie.infoLabels["status"] != "Ended" and serie.infoLabels["status"] != "Canceled":
                            serie.active = interval
                        serie.channel = "videolibrary"
                        serie.action = "get_seasons"
                        res = videolibrarytools.write_nfo(tvshow_file, head_nfo, serie)

                    if serie_actualizada and not config.get_setting('cleanlibrary', 'videolibrary', default=False):
                        if config.get_setting("search_new_content", "videolibrary") == 0:
                            # Actualizamos la videoteca de Kodi: Buscar contenido en la carpeta de la serie
                            if config.is_xbmc():
                                xbmc_videolibrary.update(folder=filetools.basename(path))
                                update_when_finished = True
                        else:
                            update_when_finished = True
                except Exception as ex:
                    logger.error("Se ha producido un error al actualizar la serie %s" % tvshow_file)
                    template = "An exception of type %s occured. Arguments:\n%r"
                    message = template % (type(ex).__name__, ex.args)
                    logger.error(message)
                    logger.error(traceback.format_exc())
                    

            if estado_verify_playcount_series:                                  #Si se ha cambiado algún playcount, ...
                estado = config.set_setting("verify_playcount", True, "videolibrary")   #... actualizamos la opción de Videolibrary

            #if config.get_setting("search_new_content", "videolibrary") == 1 and update_when_finished:
            if config.is_xbmc() and config.get_setting('cleanlibrary', 'videolibrary', default=False):
                while xbmc.getCondVisibility('Library.IsScanningVideo()'):      # Se espera a que acabe
                    if monitor:
                        if monitor.waitForAbort(1):
                            break
                    else:
                        if xbmc.abortRequested:
                            break
                        xbmc.sleep(1000)
                xbmc.executebuiltin('CleanLibrary(video)')
                while xbmc.getCondVisibility('Library.IsScanningVideo()'):      # Se espera a que acabe
                    if monitor:
                        if monitor.waitForAbort(1):
                            break
                    else:
                        if xbmc.abortRequested:
                            break
                        xbmc.sleep(1000)
                update_when_finished = True
                config.set_setting('cleanlibrary', False, 'videolibrary')
            if update_when_finished:
                # Actualizamos la videoteca de Kodi: Buscar contenido en todas las series
                if config.is_xbmc():
                    xbmc_videolibrary.update()

            p_dialog.close()

        else:
            logger.info("No actualiza la videoteca, está desactivado en la configuración de alfa")

    except Exception as ex:
        logger.error("Se ha producido un error al actualizar las series")
        template = "An exception of type %s occured. Arguments:\n%r"
        message = template % (type(ex).__name__, ex.args)
        logger.error(message)

        if p_dialog:
            p_dialog.close()
    
    httptools.VIDEOLIBRARY_UPDATE = False
    
    # Sincroniza los "vistos" de la Videoteca de Películas    
    from core.item import Item
    item_dummy = Item()
    videolibrary.list_movies(item_dummy, silent=True)
    
    # Descarga los últimos episodios disponibles, si el canal lo permite
    if config.get_setting("update", "videolibrary") != 0 or overwrite:
        from channels import downloads
        downloads.download_auto(item_dummy)


def start(thread=True):
    if thread:
        t = threading.Thread(target=start, args=[False,])
        t.setDaemon(True)
        t.start()
    else:

        update_wait = [0, 10000, 20000, 30000, 60000, 120000, 300000, 600000, 900000]
        wait = update_wait[int(config.get_setting("update_wait", "videolibrary"))]
        if wait > 0:
            if monitor:
                if monitor.waitForAbort(wait/1000):
                    return
            else:
                if xbmc.abortRequested:
                    return
                xbmc.sleep(wait)

        if config.get_setting("update", "videolibrary") not in [2, 4]:
            if config.get_setting("videolibrary_backup_scan", "videolibrary", default=False):
                try:
                    threading.Thread(target=scan_after_remote_update, args=('start',)).start()
                except:
                    scan_after_remote_update('start')
            else:
                check_for_update(overwrite=False)

        # Se ejecuta ciclicamente
        if monitor:
            while not monitor.abortRequested():
                monitor_update()
                if monitor.waitForAbort(3600):  # cada hora
                    break
        else:
            while not xbmc.abortRequested:
                monitor_update()
                xbmc.sleep(3600*1000)


def scan_after_remote_update(mode):
    if config.is_xbmc():
        
        minute = datetime.datetime.now().minute
        sleep = (60 - minute) * 60                                  # Esperamos hasta la siguiente hora + 15'
        delay = 60 * 15                                             # Esperamos 15'

        if mode != 'start':
            delay += sleep
            
        if monitor:
            if monitor.waitForAbort(delay):
                return
        else:
            if xbmc.abortRequested:
                return
            xbmc.sleep(delay*1000)
        
        from platformcode import xbmc_videolibrary
        xbmc_videolibrary.update()


def monitor_update():
    update_setting = config.get_setting("update", "videolibrary")

    # "Actualizar "Una sola vez al dia" o "al inicar Kodi y al menos una vez al dia" o "Dos veces al día"

    if update_setting in [2, 3, 4]:
        hoy = datetime.date.today()
        last_check = config.get_setting("updatelibrary_last_check", "videolibrary")
        if last_check:
            y, m, d = last_check.split('-')
            last_check = datetime.date(int(y), int(m), int(d))
        else:
            last_check = hoy - datetime.timedelta(days=1)

        update_start = config.get_setting("everyday_delay", "videolibrary") * 4
        update_start_2 = config.get_setting("everyday_delay_2", "videolibrary") * 4

        # logger.info("Ultima comprobacion: %s || Fecha de hoy:%s || Hora actual: %s" %
        #             (last_check, hoy, datetime.datetime.now().hour))
        # logger.info("Atraso del inicio del dia: %i:00" % update_start)

        if last_check <= hoy and (datetime.datetime.now().hour == int(update_start) \
                        or (datetime.datetime.now().hour == int(update_start_2) \
                        and update_setting == 4)):
            try:
                logger.info("Inicio actualizacion programada para las %s h.: %s" % (update_start, datetime.datetime.now()))
            except:
                pass
            if config.get_setting("videolibrary_backup_scan", "videolibrary", default=False):
                scan_after_remote_update('clock')
            else:
                check_for_update(overwrite=False)


if __name__ == "__main__":
    # Se ejecuta en cada inicio

    # modo adulto:
    # sistema actual 0: Nunca, 1:Siempre, 2:Solo hasta que se reinicie Kodi
    # si es == 2 lo desactivamos.

    # Reseteamos caches por si se acaba de actualizar la versión de Alfa
    alfa_caching = config.cache_reset()
    
    # Detecta la versión correcta de marshal
    if PY3:
        from platformcode import custom_code
        custom_code.marshal_check()
    if config.get_platform(True)['num_version'] >= 17.0:
        if not PY3:
            from lib.alfaresolver import updated, update_now
        else:
            from lib.alfaresolver_py3 import updated, update_now
        if not updated():
            update_now()
    if config.get_setting("adult_mode") == 2:
        config.set_setting("adult_mode", 0)

    # Verificar quick-fixes al abrirse Kodi, y dejarlo corriendo como Thread
    from platformcode import updater
    updater.check_addon_init()

    # Copia Custom code a las carpetas de Alfa desde la zona de Userdata
    from platformcode import custom_code
    custom_code.init()

    # Identifica la dirección Proxy y la lista de alternativas
    #if PY3: from core import proxytool_py3 as proxytool else from core import proxytool_py2 as proxytool
    if not PY3: from core.proxytools import get_proxy_list
    else: from core.proxytools_py3 import get_proxy_list
    get_proxy_list()
    
    # Incializamos caching de variables
    config.cache_init()

    # Actualiza la videoteca de Alfa, con una espera inicial si se ha configurado
    if config.get_setting("update", "videolibrary") not in [0, 2, 4]:
        update_wait = [0, 10000, 20000, 30000, 60000, 120000, 300000, 600000, 900000]
        wait = update_wait[int(config.get_setting("update_wait", "videolibrary"))]
        if wait > 0:
            if monitor:
                if monitor.waitForAbort(wait/1000):
                    sys.exit()
            else:
                if xbmc.abortRequested:
                    sys.exit()
                xbmc.sleep(wait)

        if config.get_setting("update", "videolibrary") not in [0, 2, 4]:
            if config.get_setting("videolibrary_backup_scan", "videolibrary", default=False):
                try:
                    threading.Thread(target=scan_after_remote_update, args=('start',)).start()
                except:
                    scan_after_remote_update('start')
            else:
                check_for_update(overwrite=False)
    
    if monitor and monitor.waitForAbort(0.1):
        sys.exit()
    
    # Añade al LOG las variables de entorno necesarias para diagnóstico
    from platformcode import envtal
    envtal.list_env()

    # Busqueda de estrenos
    from channels import info_popup
    info_popup.autoscan()

    # Se ejecuta ciclicamente
    if monitor:
        while not monitor.abortRequested():
            monitor_update()
            if monitor.waitForAbort(3600):  # cada hora
                break
    else:
        while not xbmc.abortRequested:
            monitor_update()
            xbmc.sleep(3600*1000)
