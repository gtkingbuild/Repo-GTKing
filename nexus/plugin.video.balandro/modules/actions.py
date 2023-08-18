# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3:
    import xbmcvfs
    translatePath = xbmcvfs.translatePath
else:
    import xbmc
    translatePath = xbmc.translatePath


import os, re, xbmcgui, xbmc

from platformcode import config, logger, platformtools
from core import filetools, jsontools

from core.item import Item


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


def open_settings(item):
    logger.info()

    config.__settings__.openSettings()

    platformtools.itemlist_refresh()


def _marcar_canales(item):
    cfg_cchannel_status = 'channel_' + item.canal + '_status'
    status = config.get_setting(cfg_cchannel_status, default='')

    if status:
        ant_tipo = 'Activo'
        if status == 1: ant_tipo = 'Preferido'
        if status == -1: ant_tipo = 'Desactivado'

    new_tipo = 'Activo'
    if item.estado == 1: new_tipo = 'Preferido'
    if item.estado == -1: new_tipo = 'Desactivado'

    if status:
        if ant_tipo == new_tipo:
            el_canal = ('Sin cambio en [B][COLOR %s] %s [COLOR %s] ' + item.canal.capitalize() + '[/COLOR][/B]') % (color_exec, new_tipo, color_infor)
            platformtools.dialog_notification(config.__addon_name, el_canal)
            return

        if not platformtools.dialog_yesno(config.__addon_name + ' - ' + item.canal.capitalize(), '[COLOR red][B]¿ Confirma cambiar la personalización del canal ?[/B][/COLOR]', 'de:  [COLOR cyan]' + ant_tipo + '[/COLOR]', 'a:    [COLOR yellow]' + new_tipo + '[/COLOR]'): 
            return

    config.set_setting('status', item.estado, item.canal)

    el_canal = ('Cambiado a [B][COLOR %s] %s [COLOR %s] ' + item.canal.capitalize() + '[/COLOR][/B]') % (color_exec, new_tipo, color_avis)
    platformtools.dialog_notification(config.__addon_name, el_canal)


def comprobar_nuevos_episodios(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'tracking_dbs')

    existe = filetools.exists(path)
    if not existe:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Preferidos[/COLOR][/B]' % color_exec)
        return

    la_notif = ('[B][COLOR %s]') % color_infor
    la_notif += ('Comprobando existencia nuevos episodios[/B][/COLOR]')
    platformtools.dialog_notification(config.__addon_name, la_notif, time=2000, sound=False)

    from core import trackingtools
    trackingtools.check_and_scrap_new_episodes()


def check_addon_updates(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando actualizaciones[/B][/COLOR]' % color_infor)

    from platformcode import updater
    updater.check_addon_updates(verbose=True)

    platformtools.itemlist_refresh()


def check_addon_updates_force(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Forzando actualizaciones[/B][/COLOR]' % color_avis)

    from platformcode import updater
    updater.check_addon_updates(verbose=True, force=True)

    platformtools.itemlist_refresh()


def manto_last_fix(item):
    logger.info()

    path = os.path.join(config.get_runtime_path(), 'last_fix.json')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero Fix[/COLOR][/B]' % color_infor)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el fichero de control FIX ?[/B][/COLOR]'):
        filetools.remove(path)
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Fichero control FIX eliminado[/B][/COLOR]' % color_infor)


def drop_db_cache(item):
    logger.info()

    if platformtools.dialog_yesno('Borrar Caché Tmdb', '[COLOR red][B]¿ Eliminar Todos los registros de la caché de Tmdb ?[/B][/COLOR]'): 
        from core import tmdb
        if tmdb.drop_bd():
            platformtools.dialog_notification(config.__addon_name, 'Caché Tmdb borrada', time=2000, sound=False)


def clean_db_cache(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Inspeccionado la Caché de Tmdb[/B][/COLOR]' % color_infor)

    import sqlite3, time

    fecha_caducidad = time.time() - (31 * 24 * 60 * 60)

    fname = filetools.join(config.get_data_path(), "tmdb.sqlite")
    conn = sqlite3.connect(fname)
    c = conn.cursor()

    c.execute('SELECT COUNT() FROM tmdb_cache')
    numregs = c.fetchone()[0]

    c.execute('SELECT COUNT() FROM tmdb_cache WHERE added < ?', (fecha_caducidad,))
    numregs_expired = c.fetchone()[0]

    txt = 'El caché de Tmdb ocupa [COLOR gold][B]%s[/B][/COLOR]' % config.format_bytes(filetools.getsize(fname))
    txt += ' y contiene [COLOR gold][B]%s[[/B]/COLOR] registros.' % numregs
    txt += ' ¿ Borrar los [COLOR blue][B]%s[/B][/COLOR] registros que tienen más de un mes de antiguedad de Tmdb ?' % numregs_expired

    if platformtools.dialog_yesno('Limpiar la caché de Tmdb', txt): 
        c.execute('DELETE FROM tmdb_cache WHERE added < ?', (fecha_caducidad,))
        conn.commit()
        conn.execute('VACUUM')
        platformtools.dialog_notification(config.__addon_name, 'Limpiada Caché Tmdb', time=2000, sound=False)

    conn.close()


def more_info(item):
    logger.info()

    # Si  menú contextual, recuperar parámetros action y channel
    if item.from_action: item.__dict__['action'] = item.__dict__.pop('from_action')
    if item.from_channel: item.__dict__['channel'] = item.__dict__.pop('from_channel')

    from core import tmdb

    tmdb.set_infoLabels_item(item)

    xlistitem = xbmcgui.ListItem()
    platformtools.set_infolabels(xlistitem, item, True)

    ret = xbmcgui.Dialog().info(xlistitem)


def search_trailers(item):
    logger.info()

    from core.tmdb import Tmdb

    tipo = 'movie' if item.contentType == 'movie' else 'tv'
    nombre = item.contentTitle if item.contentType == 'movie' else item.contentSerieName

    if item.infoLabels['tmdb_id']:
        tmdb_search = Tmdb(id_Tmdb=item.infoLabels['tmdb_id'], tipo=tipo, idioma_busqueda='es')
    else:
        anyo = item.infoLabels['year'] if item.infoLabels['year'] else '-'
        tmdb_search = Tmdb(texto_buscado=nombre, tipo=tipo, year=anyo, idioma_busqueda='es')

    opciones = []
    resultados = tmdb_search.get_videos()
    for res in resultados:
        it = xbmcgui.ListItem(res['name'], '[%sp] (%s)' % (res['size'], res['language']))
        if item.thumbnail: it.setArt({ 'thumb': item.thumbnail })
        opciones.append(it)

    if len(resultados) == 0:
        notification_d_ok = config.get_setting('notification_d_ok', default=True)
        if notification_d_ok:
            platformtools.dialog_ok(nombre, 'No se encuentra ningún tráiler en TMDB')
        else:
            platformtools.dialog_notification(nombre, '[B][COLOR %s]Sin tráiler en TMDB[/COLOR][/B]' % color_alert)
    else:
        while not xbmc.Monitor().abortRequested():
            ret = xbmcgui.Dialog().select('Tráilers para [B][COLOR yellow]%s[/B][/COLOR]' % nombre, opciones, useDetails=True)
            if ret == -1: break

            platformtools.dialog_notification(resultados[ret]['name'], 'Cargando tráiler ...', time=3000, sound=False)

            from core import servertools

            if 'youtube' in resultados[ret]['url']:
                video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing('youtube', resultados[ret]['url'])
            else:
                video_urls = []
                logger.info("check-resultados: %s" % resultados[ret])

            if len(video_urls) > 0:
                xbmc.Player().play(video_urls[0][1])
                xbmc.sleep(1000)
                while not xbmc.Monitor().abortRequested() and xbmc.Player().isPlaying():
                    xbmc.sleep(1000)
            else:
                la_notif = ('[B][COLOR %s]') % color_alert
                la_notif += ('No se pudo reproducir el tráiler[/B][/COLOR]')

                platformtools.dialog_notification(resultados[ret]['name'], la_notif, time=3000, sound=False)

            if len(resultados) == 1: break


def global_proxies(item):
    logger.info()

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR yellow][B]¿ Confirma Obtener Proxies en los canales que los necesiten ?[/B][/COLOR]'):
        from modules import proxysearch

        proxysearch.proxysearch_all(item)


def manto_domains(item):
    logger.info()

    from core import channeltools

    filtros = {}

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar los Dominios memorizados en Todos los canales que los tengan?[/B][/COLOR]'):
       for ch in ch_list:
           if not 'current' in ch['clusters']: continue

           cfg_domain_channel = 'channel_' + ch['name'] + '_dominio'

           if config.get_setting(cfg_domain_channel, default=''): config.set_setting(cfg_domain_channel, '')

       platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Dominios eliminados[/B][/COLOR]' % color_infor)


def manto_proxies(item):
    logger.info()

    from core import channeltools

    filtros = {'active': True}

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar los Proxies memorizados en Todos los canales que los tengan?[/B][/COLOR]'):
       for ch in ch_list:
           if not 'proxies' in ch['notes'].lower(): continue

           # por NAME anteriores a 2.0
           cfg_proxies_channel = 'channel_' + ch['name'] + '_proxies'

           if config.get_setting(cfg_proxies_channel, default=''):
               config.set_setting(cfg_proxies_channel, '')

               cfg_proxytools_max_channel = 'channel_' + ch['name'] + '_proxytools_max'
               if config.get_setting(cfg_proxytools_max_channel, default=''): config.set_setting(cfg_proxytools_max_channel, '')

               cfg_proxytools_provider = 'channel_' + ch['name'] + '_proxytools_provider'
               if config.get_setting(cfg_proxytools_provider, default=''): config.set_setting(cfg_proxytools_provider, '')

           # por ID
           cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
           cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'
           cfg_proxytools_provider = 'channel_' + ch['id'] + '_proxytools_provider'

           if not config.get_setting(cfg_proxies_channel, default=''):
               if not config.get_setting(cfg_proxytools_max_channel, default=''):
                   if not config.get_setting(cfg_proxytools_provider, default=''):
                       continue

           if config.get_setting(cfg_proxies_channel, default=''): config.set_setting(cfg_proxies_channel, '')
           if config.get_setting(cfg_proxytools_max_channel, default=''): config.set_setting(cfg_proxytools_max_channel, '')
           if config.get_setting(cfg_proxytools_provider, default=''): config.set_setting(cfg_proxytools_provider, '')

       config.set_setting('channels_proxies_memorized', '')

       platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Proxies eliminados[/B][/COLOR]' % color_infor)


def manto_params(item):
    logger.info()

    if platformtools.dialog_yesno(config.__addon_name, "Se quitarán: 'Logins' en canales, 'Dominios' seleccionados en los canales, 'Canales Incluidos/Excluidos' en búsquedas, 'Canales Excluidos' en buscar proxies global, y se Inicializarán otros 'Parámetros'.", '[COLOR yellow][B]¿ Confirma Restablecer a sus valores por defecto los Parámetros Internos del addon ?[/B][/COLOR]'):
        config.set_setting('adults_password', '')

        config.set_setting('dominio', '', 'test_providers')
        config.set_setting('channel_test_providers_dominio', '')

        config.set_setting('proxies', '', 'test_providers')

        config.set_setting('channel_animefenix_dominio', '')
        config.set_setting('channel_animeflv_dominio', '')
        config.set_setting('channel_animeonline_dominio', '')

        config.set_setting('channel_cinecalidad_dominio', '')
        config.set_setting('channel_cinecalidadla_dominio', '')
        config.set_setting('channel_cinecalidadlol_dominio', '')
        config.set_setting('channel_cinecalidadmx_dominio', '')
        config.set_setting('channel_cliversite_dominio', '')
        config.set_setting('channel_cuevana3video_dominio', '')

        config.set_setting('channel_divxtotal_dominio', '')
        config.set_setting('channel_dontorrents_dominio', '')

        config.set_setting('channel_elifilms_dominio', '')
        config.set_setting('channel_elitetorrent_dominio', '')
        config.set_setting('channel_ennovelas_dominio', '')
        config.set_setting('channel_entrepeliculasyseries_dominio', '')
        config.set_setting('channel_estrenosdoramas_dominio', '')

        config.set_setting('channel_gnula24_dominio', '')
        config.set_setting('channel_grantorrent_dominio', '')
        config.set_setting('channel_grantorrents_dominio', '')

        config.set_setting('channel_hdfull_dominio', '')
        config.set_setting('channel_hdfull_hdfull_login', False)
        config.set_setting('channel_hdfull_hdfull_password', '')
        config.set_setting('channel_hdfull_hdfull_username', '')

        config.set_setting('channel_hdfullse_dominio', '')
        config.set_setting('channel_henaojara_dominio', '')

        config.set_setting('channel_mejortorrentapp_dominio', '')

        config.set_setting('channel_nextdede_nextdede_login', False)
        config.set_setting('channel_nextdede_nextdede_email', '')
        config.set_setting('channel_nextdede_nextdede_password', '')
        config.set_setting('channel_nextdede_nextdede_username', '')

        config.set_setting('channel_pelishouse_dominio', '')
        config.set_setting('channel_pelismaraton_dominio', '')
        config.set_setting('channel_pelispedia_dominio', '')
        config.set_setting('channel_pelispediaws_dominio', '')
        config.set_setting('channel_pelisplus_dominio', '')
        config.set_setting('channel_pelisplushd_dominio', '')
        config.set_setting('channel_pelisplushdlat_dominio', '')
        config.set_setting('channel_pelisplushdnz_dominio', '')
        config.set_setting('channel_pelispluslat_dominio', '')

        config.set_setting('channel_playdede_dominio', '')
        config.set_setting('channel_playdede_playdede_login', False)
        config.set_setting('channel_playdede_playdede_password', '')
        config.set_setting('channel_playdede_playdede_username', '')

        config.set_setting('channel_poseidonhd2_dominio', '')

        config.set_setting('channel_series24_dominio', '')
        config.set_setting('channel_seriesantiguas_dominio', '')
        config.set_setting('channel_serieskao_dominio', '')
        config.set_setting('channel_seriesyonkis_dominio', '')
        config.set_setting('channel_srnovelas_dominio', '')
        config.set_setting('channel_subtorrents_dominio', '')

        config.set_setting('channel_torrentpelis_dominio', '')

        config.set_setting('channels_proxies_memorized', '')

        config.set_setting('search_included_all', '')

        config.set_setting('search_excludes_movies', '')
        config.set_setting('search_excludes_tvshows', '')
        config.set_setting('search_excludes_documentaries', '')
        config.set_setting('search_excludes_mixed', '')
        config.set_setting('search_excludes_all', '')

        config.set_setting('proxysearch_excludes', '')

        config.set_setting('proxysearch_process', '')
        config.set_setting('proxysearch_process_proxies', '')

        config.set_setting('search_last_all', '')
        config.set_setting('search_last_movie', '')
        config.set_setting('search_last_tvshow', '')
        config.set_setting('search_last_documentary', '')
        config.set_setting('search_last_person', '')

        download_path = filetools.join(config.get_data_path(), 'downloads')
        config.set_setting('downloadpath', download_path)

        config.set_setting('chrome_last_version', '115.0.5790.171')

        config.set_setting('debug', '0')

        config.set_setting('developer_mode', False)
        config.set_setting('developer_test_channels', '')
        config.set_setting('developer_test_servers', '')

        config.set_setting('user_test_channel', '')

        manto_proxies(item)

        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Parámetros restablecidos[/B][/COLOR]' % color_infor)


def manto_textos(item):
    logger.info()

    hay_lastest = False

    if config.get_setting('search_last_all', default=''): hay_lastest = True
    elif config.get_setting('search_last_movie', default=''): hay_lastest = True
    elif config.get_setting('search_last_tvshow', default=''): hay_lastest = True
    elif config.get_setting('search_last_documentary', default=''): hay_lastest = True
    elif config.get_setting('search_last_person', default=''): hay_lastest = True

    if not hay_lastest:
         platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay Textos Memorizados[/COLOR][/B]' % color_alert)
         return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar los Textos Memorizados ?[/B][/COLOR]'):
        config.set_setting('search_last_all', '')
        config.set_setting('search_last_movie', '')
        config.set_setting('search_last_tvshow', '')
        config.set_setting('search_last_documentary', '')
        config.set_setting('search_last_person', '')

        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Texos restablecidos[/B][/COLOR]' % color_infor)

def manto_cookies(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'cookies.dat')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero de Cookies[/COLOR][/B]' % color_alert)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el fichero de Cookies ?[/B][/COLOR]'):
        filetools.remove(path)
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Fichero Cookies eliminado[/B][/COLOR]' % color_infor)


def manto_advs(item):
    logger.info()

    path = translatePath(os.path.join('special://home/userdata', ''))

    file_advs = 'advancedsettings.xml'

    file = path + file_advs

    existe = filetools.exists(file)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero Advancedsettings[/COLOR][/B]' % color_infor)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el fichero Advancedsettings ?[/B][/COLOR]'):
        filetools.remove(file)
        platformtools.dialog_ok(config.__addon_name, '[B][COLOR pink]Fichero Advancedsettings eliminado[/B][/COLOR]', '[B][COLOR yellow]Debe Abandonar obligatoriamente su Media Center e Ingresar de nuevo en el.[/B][/COLOR]')


def manto_folder_cache(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'cache')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no hay Carpeta Caché[/COLOR][/B]' % color_exec)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar Toda la carpeta Caché ?[/B][/COLOR]'):
        filetools.rmdirtree(path)
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Carpeta Caché eliminada[/B][/COLOR]' % color_infor)


def manto_limpiezas(item):
    logger.info()

    opciones_limpiezas = []

    opciones_limpiezas.append(platformtools.listitem_to_select('[COLOR olive][B]Limpieza [/B][COLOR powderblue][B]Media Center[/B][/COLOR]'))
    opciones_limpiezas.append(platformtools.listitem_to_select('[COLOR olive][B]Limpieza [/B][COLOR powderblue][B]Add-Ons[/B][/COLOR]'))
    opciones_limpiezas.append(platformtools.listitem_to_select('[COLOR olive][B]Limpieza [/B][COLOR powderblue][B]Sistema[/B][/COLOR]'))
    opciones_limpiezas.append(platformtools.listitem_to_select('[COLOR olive][B]Limpieza [/B][COLOR powderblue][B]Logs[/B][/COLOR]'))
    opciones_limpiezas.append(platformtools.listitem_to_select('[COLOR olive][B]Limpieza [/B][COLOR powderblue][B]Temporales[/B][/COLOR]'))
    opciones_limpiezas.append(platformtools.listitem_to_select('[COLOR olive][B]Eliminar [/B][COLOR red][B]Poxies[/B][/COLOR] de Todos los Canalas'))

    ret = platformtools.dialog_select('Limpiezas', opciones_limpiezas)

    if not ret == -1:
        procesado = False

        if ret == 0:
            path_advs = translatePath(os.path.join('special://home/userdata', ''))
            file_advs = 'advancedsettings.xml'
            file = path_advs + file_advs
            existe = filetools.exists(file)

            if existe:
                manto_advs(item)
                procesado = True

            path_cache = translatePath(os.path.join('special://temp/archive_cache', ''))
            existe_cache = filetools.exists(path_cache)

            caches = []
            if existe_cache: caches = os.listdir(path_cache)

            if caches:
                manto_caches(item)
                procesado = True

            path_thumbs = translatePath(os.path.join('special://home/userdata/Thumbnails', ''))
            existe_thumbs = filetools.exists(path_thumbs)

            if existe_thumbs:
                manto_thumbs(item)
                procesado = True

            if not procesado:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Nada a limpiar de Media Center[/COLOR][/B]' % color_exec)
                return

        elif ret == 1:
            ejecutar = False

            path_packages = translatePath(os.path.join('special://home/addons/packages', ''))
            existe_packages = filetools.exists(path_packages)

            packages = []
            if existe_packages: packages = os.listdir(path_packages)

            path_temp = translatePath(os.path.join('special://home/addons/temp', ''))
            existe_temp = filetools.exists(path_temp)

            temps = []
            if existe_temp: temps = os.listdir(path_temp)

            if packages: ejecutar = True
            elif temps: ejecutar = True

            if not ejecutar:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no hay Add-Ons[/COLOR][/B]' % color_exec)
                return

            if packages: manto_addons_packages(item)
            if temps: manto_addons_temp(item)

        elif ret == 2:
            path = os.path.join(config.get_runtime_path(), 'last_fix.json')
            existe = filetools.exists(path)

            if existe:
                manto_last_fix(item)
                procesado = True

            path = os.path.join(config.get_data_path(), 'cookies.dat')
            existe = filetools.exists(path)

            if existe:
                manto_cookies(item)
                procesado = True

            path = os.path.join(config.get_data_path(), 'cache')
            existe = filetools.exists(path)

            if existe:
                manto_folder_cache(item)
                procesado = True

            downloadpath = config.get_setting('downloadpath', default='')
            if downloadpath: path = downloadpath
            else: path = filetools.join(config.get_data_path(), 'downloads')

            existe = filetools.exists(path)
            if existe:
                manto_folder_downloads(item)
                procesado = True

            path = filetools.join(config.get_data_path(), 'tracking_dbs')
            existe = filetools.exists(path)

            if existe:
                manto_tracking_dbs(item)
                procesado = True

            path = filetools.join(config.get_data_path(), 'tmdb.sqlite-journal')
            existe = filetools.exists(path)

            if existe:
                item.journal = 'journal'
                manto_tmdb_sqlite(item)
                procesado = True

            path = filetools.join(config.get_data_path(), 'tmdb.sqlite')
            existe = filetools.exists(path)

            if existe:
                manto_tmdb_sqlite(item)
                procesado = True

            path = config.get_data_path()
            existe = filetools.exists(path)

            if existe:
                manto_folder_addon(item)
                procesado = True

            if not procesado:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Nada a limpiar de Sistema[/COLOR][/B]' % color_exec)
                return

        elif ret == 3:
            ejecutar = False

            if os.path.exists(os.path.join(config.get_data_path(), 'servers_todo.log')): ejecutar = True
            elif os.path.exists(os.path.join(config.get_data_path(), 'qualities_todo.log')): ejecutar = True
            elif os.path.exists(os.path.join(config.get_data_path(), 'proxies.log')): ejecutar = True

            if not ejecutar:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no hay Logs[/COLOR][/B]' % color_exec)
                return

            if ejecutar: manto_temporales(item)

        elif ret == 4:
            ejecutar = False

            if os.path.exists(os.path.join(config.get_data_path(), 'info_channels.csv')): ejecutar = True
            elif os.path.exists(os.path.join(config.get_data_path(), 'temp.torrent')): ejecutar = True
            elif os.path.exists(os.path.join(config.get_data_path(), 'm3u8hls.m3u8')): ejecutar = True
            elif os.path.exists(os.path.join(config.get_data_path(), 'blenditall.m3u8')): ejecutar = True
            elif os.path.exists(os.path.join(config.get_data_path(), 'test_logs')): ejecutar = True
            elif os.path.exists(os.path.join(config.get_data_path(), 'temp_updates.zip')): ejecutar = True
            elif os.path.exists(os.path.join(config.get_data_path(), 'tempfile_mkdtemp')): ejecutar = True

            if not ejecutar:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no hay Temporales[/COLOR][/B]' % color_exec)
                return

            if ejecutar: manto_temporales(item)

        elif ret == 5:
            manto_proxies(item)


def manto_temporales(item):
    logger.info()

    hay_temporales = False

    if item._logs:
        path = os.path.join(config.get_data_path(), 'servers_todo.log')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'qualities_todo.log')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'proxies.log')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

    else:
        path = os.path.join(config.get_data_path(), 'info_channels.csv')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'temp.torrent')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'm3u8hls.m3u8')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'blenditall.m3u8')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'test_logs')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'temp_updates.zip')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'tempfile_mkdtemp')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

    if hay_temporales == False:
        if item._logs:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay ficheros Logs[/COLOR][/B]' % color_alert)
        else:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay ficheros Temporales[/COLOR][/B]' % color_alert)
        return

    if item._logs:
        texto = '[COLOR red][B]¿ Confirma Eliminar los ficheros Logs ?[/B][/COLOR]'
    else:
        texto = '[COLOR red][B]¿ Confirma Eliminar los ficheros Temporales ?[/B][/COLOR]'

    if platformtools.dialog_yesno(config.__addon_name, texto):
        if item._logs:
            path = os.path.join(config.get_data_path(), 'servers_todo.log')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'qualities_todo.log')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'proxies.log')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

        else:
            path = os.path.join(config.get_data_path(), 'info_channels.csv')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'temp.torrent')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'm3u8hls.m3u8')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'blenditall.m3u8')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'test_logs')
            existe = filetools.exists(path)
            if existe: filetools.rmdirtree(path)

            path = os.path.join(config.get_data_path(), 'temp_updates.zip')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'tempfile_mkdtemp')
            existe = filetools.exists(path)
            if existe: filetools.rmdirtree(path)

        if item._logs:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Ficheros Logs eliminados[/B][/COLOR]' % color_infor)
        else:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Ficheros Temporales eliminados[/B][/COLOR]' % color_infor)


def manto_addons_packages(item):
    logger.info()

    path = translatePath(os.path.join('special://home/addons/packages', ''))

    hay_temporales = False

    existe = filetools.exists(path)
    if existe: hay_temporales = True

    if existe:
        packages = []
        packages = os.listdir(path)

        if not packages: hay_temporales = False

    if hay_temporales == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay ficheros en Addons/Packages[/COLOR][/B]' % color_alert)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar los ficheros de Addons/Packages ?[/B][/COLOR]'):
        filetools.rmdirtree(path)

        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Ficheros Addons/Packages eliminados[/B][/COLOR]' % color_infor)


def manto_addons_temp(item):
    logger.info()

    path = translatePath(os.path.join('special://home/addons/temp', ''))

    hay_temporales = False

    existe = filetools.exists(path)
    if existe: hay_temporales = True

    if existe:
        temps = []
        temps = os.listdir(path)

        if not temps: hay_temporales = False

    if hay_temporales == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay ficheros en Addons/Temp[/COLOR][/B]' % color_alert)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar los ficheros de Addons/Temp ?[/B][/COLOR]'):
        filetools.rmdirtree(path)

        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Ficheros Addons/Temp eliminados[/B][/COLOR]' % color_infor)


def manto_caches(item):
    logger.info()

    path = translatePath(os.path.join('special://temp/archive_cache', ''))

    hay_caches = False

    existe = filetools.exists(path)
    if existe: hay_caches = True

    if hay_caches == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay ficheros de Caché en su Media Center[/COLOR][/B]' % color_alert)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar los ficheros de Caché de su Media Center ?[/B][/COLOR]'):
        filetools.rmdirtree(path)

        platformtools.dialog_ok(config.__addon_name, '[B][COLOR pink]Ficheros Caché de su Media Center eliminados[/B][/COLOR]', '[B][COLOR yellow]Debe Abandonar obligatoriamente su Media Center e Ingresar de nuevo en el.[/B][/COLOR]')


def manto_thumbs(item):
    logger.info()

    path = translatePath(os.path.join('special://home/userdata/Thumbnails', ''))

    hay_thumbs = False

    existe = filetools.exists(path)
    if existe: hay_thumbs = True

    if hay_thumbs == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay ficheros de Thumbnails en su Media Center[/COLOR][/B]' % color_alert)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar Todos los ficheros de Thumbnails de su Media Center ?[/B][/COLOR]', '[COLOR yellow][B]Atención: el Proceso podría durar un cierto tiempo considerable, en función del numero de archivos existentes.[/B][/COLOR]'):
        filetools.rmdirtree(path)

        platformtools.dialog_ok(config.__addon_name, '[B][COLOR pink]Ficheros Thumbnails de su Media Center eliminados[/B][/COLOR]', '[B][COLOR yellow]Debe Abandonar obligatoriamente su Media Center e Ingresar de nuevo en el.[/B][/COLOR]')


def manto_tracking_dbs(item):
    logger.info()

    path = filetools.join(config.get_data_path(), 'tracking_dbs')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Preferidos[/COLOR][/B]' % color_exec)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar Todo el contenido de sus Preferidos ?[/B][/COLOR]'):
        filetools.rmdirtree(path)
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Contenido Preferidos eliminado[/B][/COLOR]' % color_infor)


def manto_tmdb_sqlite(item):
    logger.info()

    if not item.journal:
        path = filetools.join(config.get_data_path(), 'tmdb.sqlite')

        existe = filetools.exists(path)
        if existe == False:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Tmdb Sqlite[/COLOR][/B]' % color_exec)

        if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el fichero Tmdb Sqlite ?[/B][/COLOR]'):
            filetools.remove(path)
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Fichero Tmdb Sqlite eliminado[/B][/COLOR]' % color_infor)

    else:

        path = filetools.join(config.get_data_path(), 'tmdb.sqlite-journal')

        existe = filetools.exists(path)
        if existe == False:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Tmdb Sqlite Journal[/COLOR][/B]' % color_exec)

        if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el fichero Tmdb Sqlite Journal?[/B][/COLOR]'):
            filetools.remove(path)
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Fichero Tmdb Sqlite Journal eliminado[/B][/COLOR]' % color_infor)


def manto_folder_downloads(item):
    logger.info()

    downloadpath = config.get_setting('downloadpath', default='')

    if downloadpath: path = downloadpath
    else: path = filetools.join(config.get_data_path(), 'downloads')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Descargas[/COLOR][/B]' % color_exec)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el contenido de Todas sus Descargas ?[/B][/COLOR]'):
        filetools.rmdirtree(path)

        # por si varió el path y quedaron descargas huerfanas en el path default
        if downloadpath:
           try:
              path = filetools.join(config.get_data_path(), 'downloads')
              filetools.rmdirtree(path)
           except:
              pass

        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Contenido Descargas eliminado[/B][/COLOR]' % color_infor)


def manto_folder_addon(item):
    logger.info()

    path = config.get_data_path()

    existe = filetools.exists(path)

    if not existe == False:
        if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ ATENCION: Confirma Eliminar Todos los Datos del Addon ?[/B][/COLOR]'):
            filetools.rmdirtree(path)
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Datos del Addon eliminados[/B][/COLOR]' % color_adver)

            try:
                # ~  a veces puede dejar solo settings.xml lo tiene bloqueado el sistema
                path = os.path.join(config.get_data_path(), 'settings.xml')

                existe = filetools.exists(path)
                if existe:
                    platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]settings.xml[/B][/COLOR]', '[COLOR red][B][I]Imposible Eliminar su fichero de Configuración/Ajustes. Está Bloqueado por su Sistema Media Center[/I][/B][/COLOR]', '[COLOR cyan][B]Por favor, Eliminelo manualmente en la ruta [/B][/COLOR][COLOR yellow][B].../.kodi/userdata/plugin.video.balandro[/B][/COLOR]')
            except:
                pass


def adults_password(item):
    logger.info()

    if not config.get_setting('adults_password'):
        password = platformtools.dialog_numeric(0, 'Pin (4 dígitos)')
        if not password: return

        if len(password) != 4:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin obligatorio 4 dígitos[/B][/COLOR]' % color_alert)
            return

        if str(password) == '0000':
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin NO admitido[/COLOR][/B]' % color_avis)
            return

        confirmpassword = platformtools.dialog_numeric(0, 'Confirme el Pin')
        if not confirmpassword: return

        if password == confirmpassword:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin establecido[/B][/COLOR]' % color_infor)
            config.set_setting('adults_password', password)
            return password
    else:
        password = platformtools.dialog_numeric(0, '[B][COLOR %s]Indique Pin parental[/COLOR][/B]' % color_adver)
        try:
            if int(password) == int(config.get_setting('adults_password')):
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin correcto[/COLOR][/B]' % color_avis)
                return True
            else:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin incorrecto[/COLOR][/B]' % color_exec)
                return False
        except:
            return False


def adults_password_del(item):
    logger.info()

    if not config.get_setting('adults_password'):
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Pin parental[/COLOR][/B]' % color_exec)
        return

    password = platformtools.dialog_numeric(0, '[B][COLOR %s]Indique Pin parental[/COLOR][/B]' % color_adver)

    try:
       if int(password) == int(config.get_setting('adults_password')):
           txt = 'Si es afirmativa su repuesta a la pregunta formulada, deberá salir y volver a acceder a esta configuración y si lo desea establecer un nuevo Pin parental.'
           if platformtools.dialog_yesno(config.__addon_name, txt, '[B][COLOR %s]¿ Desea eliminar el Pin parental memorizado ?[/COLOR][/B]' % color_adver):
               config.set_setting('adults_password', '')
               platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin anulado[/COLOR][/B]' % color_exec)
       else:
           platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin incorrecto[/COLOR][/B]' % color_exec)
           return
    except:
       return


def show_latest_domains(item):
    logger.info()

    path = os.path.join(config.get_runtime_path(), 'dominios.txt')

    existe = filetools.exists(path)

    if not existe:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún No hay fichero con Últimos Dominios[/COLOR][/B]' % color_alert)
        return

    txt = ''

    try:
       with open(os.path.join(config.get_runtime_path(), 'dominios.txt'), 'r') as f: txt=f.read(); f.close()
    except:
       try: txt = open(os.path.join(config.get_runtime_path(), 'dominios.txt'), encoding="utf8").read()
       except: pass

    if txt: platformtools.dialog_textviewer('Últimos Cambios de Dominios', txt)


def show_ubicacion(item):
    logger.info()

    downloadpath = config.get_setting('downloadpath', default='')

    if downloadpath:
        path = downloadpath
    else:
        path = os.path.join(config.get_data_path(), 'downloads')

    platformtools.dialog_textviewer('Ubicación de las Descargas', path)


def show_servers_alternatives(item):
    logger.info()

    from modules import filters

    item.tipo = 'alternativos'

    filters.show_servers_list(item)


def test_internet(item):
    platformtools.dialog_notification(config.__addon_name, 'Comprobando [B][COLOR %s]Internet[/COLOR][/B]' % color_avis)

    from core import httptools, scrapertools

    your_ip = ''

    try:
       data = httptools.downloadpage('http://httpbin.org/ip').data
       data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
       your_ip = scrapertools.find_single_match(str(data), '.*?"origin".*?"(.*?)"')
    except:
       pass

    if not your_ip:
        try:
           your_ip = httptools.downloadpage('http://ipinfo.io/ip').data
        except:
           pass

    if not your_ip:
        try:
           your_ip = httptools.downloadpage('http://www.icanhazip.com/').data
        except:
           pass

    if your_ip:
        your_info = ''

        try:
           your_info = httptools.downloadpage('https://ipinfo.io/json').data
        except:
           pass

        if your_info:
            your_info = your_info.replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace(',', '').replace('"', '').replace("'", '')
            platformtools.dialog_textviewer('Información de su Internet', your_info)
        else:
            if not 'ip:' in your_info: platformtools.dialog_ok(config.__addon_name, '[COLOR cyan][B]Compruebe la  conexión con internet.[/B][/COLOR]', your_ip)
            else: platformtools.dialog_ok(config.__addon_name, '[COLOR yellow][B]Hay conexión con internet.[/B][/COLOR]', your_ip)

        return

    platformtools.dialog_ok(config.__addon_name, '[COLOR red][B]Parece que NO hay conexión con internet.[/B][/COLOR]', 'Compruebelo realizando cualquier Búsqueda, desde un Navegador Web ')
    return


def opciones_animefenix(item):
    item.from_channel = 'animefenix'
    opciones_domains_common(item)

def opciones_animeflv(item):
    item.from_channel = 'animeflv'
    opciones_domains_common(item)

def opciones_animeonline(item):
    item.from_channel = 'animeonline'
    opciones_domains_common(item)

def opciones_cinecalidad(item):
    item.from_channel = 'cinecalidad'
    opciones_domains_common(item)

def opciones_cinecalidadla(item):
    item.from_channel = 'cinecalidadla'
    opciones_domains_common(item)

def opciones_cinecalidadlol(item):
    item.from_channel = 'cinecalidadlol'
    opciones_domains_common(item)

def opciones_cinecalidadmx(item):
    item.from_channel = 'cinecalidadmx'
    opciones_domains_common(item)

def opciones_cliversite(item):
    item.from_channel = 'cliversite'
    opciones_domains_common(item)

def opciones_cuevana3video(item):
    item.from_channel = 'cuevana3video'
    opciones_domains_common(item)

def opciones_divxtotal(item):
    item.from_channel = 'divxtotal'
    opciones_domains_common(item)

def opciones_dontorrents(item):
    item.from_channel = 'dontorrents'
    opciones_domains_common(item)

def opciones_elifilms(item):
    item.from_channel = 'elifilms'
    opciones_domains_common(item)

def opciones_elitetorrent(item):
    item.from_channel = 'elitetorrent'
    opciones_domains_common(item)

def opciones_ennovelas(item):
    item.from_channel = 'ennovelas'
    opciones_domains_common(item)

def opciones_entrepeliculasyseries(item):
    item.from_channel = 'entrepeliculasyseries'
    opciones_domains_common(item)

def opciones_estrenosdoramas(item):
    item.from_channel = 'estrenosdoramas'
    opciones_domains_common(item)

def opciones_gnula24(item):
    item.from_channel = 'gnula24'
    opciones_domains_common(item)

def opciones_grantorrent(item):
    item.from_channel = 'grantorrent'
    opciones_domains_common(item)

def opciones_grantorrents(item):
    item.from_channel = 'grantorrents'
    opciones_domains_common(item)

def opciones_hdfull(item):
    item.from_channel = 'hdfull'
    opciones_domains_common(item)

def opciones_hdfullse(item):
    item.from_channel = 'hdfullse'
    opciones_domains_common(item)

def opciones_henaojara(item):
    item.from_channel = 'henaojara'
    opciones_domains_common(item)

def opciones_mejortorrentapp(item):
    item.from_channel = 'mejortorrentapp'
    opciones_domains_common(item)

def opciones_pelishouse(item):
    item.from_channel = 'pelishouse'
    opciones_domains_common(item)

def opciones_pelismaraton(item):
    item.from_channel = 'pelismaraton'
    opciones_domains_common(item)

def opciones_pelispedia(item):
    item.from_channel = 'pelispedia'
    opciones_domains_common(item)

def opciones_pelispediaws(item):
    item.from_channel = 'pelispediaws'
    opciones_domains_common(item)

def opciones_pelisplus(item):
    item.from_channel = 'pelisplus'
    opciones_domains_common(item)

def opciones_pelisplushd(item):
    item.from_channel = 'pelisplushd'
    opciones_domains_common(item)

def opciones_pelisplushdlat(item):
    item.from_channel = 'pelisplushdlat'
    opciones_domains_common(item)

def opciones_pelisplushdnz(item):
    item.from_channel = 'pelisplushdnz'
    opciones_domains_common(item)

def opciones_pelispluslat(item):
    item.from_channel = 'pelispluslat'
    opciones_domains_common(item)

def opciones_playdede(item):
    item.from_channel = 'playdede'
    opciones_domains_common(item)

def opciones_poseidonhd2(item):
    item.from_channel = 'poseidonhd2'
    opciones_domains_common(item)

def opciones_series24(item):
    item.from_channel = 'series24'
    opciones_domains_common(item)

def opciones_seriesantiguas(item):
    item.from_channel = 'seriesantiguas'
    opciones_domains_common(item)

def opciones_serieskao(item):
    item.from_channel = 'serieskao'
    opciones_domains_common(item)

def opciones_seriesyonkis(item):
    item.from_channel = 'seriesyonkis'
    opciones_domains_common(item)

def opciones_srnovelas(item):
    item.from_channel = 'srnovelas'
    opciones_domains_common(item)

def opciones_subtorrents(item):
    item.from_channel = 'subtorrents'
    opciones_domains_common(item)

def opciones_torrentpelis(item):
    item.from_channel = 'torrentpelis'
    opciones_domains_common(item)


def opciones_domains_common(item):
    logger.info()

    el_canal = ('Comprobando [B][COLOR %s]' + item.from_channel.capitalize()) % color_exec
    platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')

    channel_json = item.from_channel + '.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    if not 'current' in str(params['clusters']):
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] Sin Gestión Dominios [/COLOR][/B]' % color_alert)
        return

    opciones_dominios = []

    domain = config.get_setting('dominio', id, default='')

    if domain: opciones_dominios.append(platformtools.listitem_to_select('[COLOR darkorange][B]Modificar/Eliminar el dominio memorizado[/B][/COLOR]'))
    else: opciones_dominios.append(platformtools.listitem_to_select('[COLOR darkorange][B]Informar Nuevo Dominio manualmente[/B][/COLOR]'))

    if domain: opciones_dominios.append(platformtools.listitem_to_select('[COLOR powderblue][B]Test Web [COLOR yellow][B] ' + domain + '[/B][/COLOR]'))
    else: opciones_dominios.append(platformtools.listitem_to_select('[COLOR powderblue][B]Test Web del canal/dominio [COLOR yellow][B] ' + domain + '[/B][/COLOR]'))

    if 'notice' in str(params['clusters']): opciones_dominios.append(platformtools.listitem_to_select('[COLOR green][B]Aviso Información del canal[/B][/COLOR]'))

    ret = platformtools.dialog_select('[COLOR yellowgreen][B]Gestión Dominio ' + name + '[/B][/COLOR]', opciones_dominios)

    if not ret == -1:
        from modules import domains

        if ret == 0:
            if item.from_channel == 'animefenix': domains.manto_domain_animefenix(item)

            elif item.from_channel == 'animeflv': domains.manto_domain_animeflv(item)

            elif item.from_channel == 'animeonline': domains.manto_domain_animeonline(item)

            elif item.from_channel == 'cinecalidad': domains.manto_domain_cinecalidad(item)

            elif item.from_channel == 'cinecalidadla': domains.manto_domain_cinecalidadla(item)

            elif item.from_channel == 'cinecalidadlol': domains.manto_domain_cinecalidadlol(item)

            elif item.from_channel == 'cinecalidadmx': domains.manto_domain_cinecalidadmx(item)

            elif item.from_channel == 'cliversite': domains.manto_domain_cliversite(item)

            elif item.from_channel == 'cuevana3video': domains.manto_domain_cuevana3video(item)

            elif item.from_channel == 'divxtotal': domains.manto_domain_divxtotal(item)

            elif item.from_channel == 'dontorrents': domains.manto_domain_dontorrents(item)

            elif item.from_channel == 'elifilms': domains.manto_domain_elifilms(item)

            elif item.from_channel == 'elitetorrent': domains.manto_domain_elitetorrent(item)

            elif item.from_channel == 'ennovelas': domains.manto_domain_ennovelas(item)

            elif item.from_channel == 'entrepeliculasyseries': domains.manto_domain_entrepeliculasyseries(item)

            elif item.from_channel == 'estrenosdoramas': domains.manto_domain_estrenosdoramas(item)

            elif item.from_channel == 'gnula24': domains.manto_domain_gnula24(item)

            elif item.from_channel == 'grantorrent': domains.manto_domain_grantorrent(item)

            elif item.from_channel == 'grantorrents': domains.manto_domain_grantorrents(item)

            elif item.from_channel == 'hdfull': domains.manto_domain_hdfull(item)

            elif item.from_channel == 'hdfullse': domains.manto_domain_hdfullse(item)

            elif item.from_channel == 'henaojara': domains.manto_domain_henaojara(item)

            elif item.from_channel == 'mejortorrentapp': domains.manto_domain_mejortorrentapp(item)

            elif item.from_channel == 'pelishouse': domains.manto_domain_pelishouse(item)

            elif item.from_channel == 'pelismaraton': domains.manto_domain_pelismaraton(item)

            elif item.from_channel == 'pelispedia': domains.manto_domain_pelispedia(item)

            elif item.from_channel == 'pelispediaws': domains.manto_domain_pelispediaws(item)

            elif item.from_channel == 'pelisplus': domains.manto_domain_pelisplus(item)

            elif item.from_channel == 'pelisplushd': domains.manto_domain_pelisplushd(item)

            elif item.from_channel == 'pelisplushdlat': domains.manto_domain_pelisplushdlat(item)

            elif item.from_channel == 'pelisplushdnz': domains.manto_domain_pelisplushdnz(item)

            elif item.from_channel == 'pelispluslat': domains.manto_domain_pelispluslat(item)

            elif item.from_channel == 'playdede': domains.manto_domain_playdede(item)

            elif item.from_channel == 'poseidonhd2': domains.manto_domain_poseidonhd2(item)

            elif item.from_channel == 'series24': domains.manto_domain_series24(item)

            elif item.from_channel == 'seriesantiguas': domains.manto_domain_seriesantiguas(item)

            elif item.from_channel == 'serieskao': domains.manto_domain_serieskao(item)

            elif item.from_channel == 'seriesyonkis': domains.manto_domain_seriesyonkis(item)

            elif item.from_channel == 'srnovelas': domains.manto_domain_srnovelas(item)

            elif item.from_channel == 'subtorrents': domains.manto_domain_subtorrents(item)

            elif item.from_channel == 'torrentpelis': domains.manto_domain_torrentpelis(item)

            else:
               platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Acción No Permitida[/B][/COLOR]' % color_alert)

        elif ret == 1:
            if item.from_channel == 'animefenix': domains.test_domain_animefenix(item)

            elif item.from_channel == 'animeflv': domains.test_domain_animeflv(item)

            elif item.from_channel == 'animeonline': domains.test_domain_animeonline(item)

            elif item.from_channel == 'cinecalidad': domains.test_domain_cinecalidad(item)

            elif item.from_channel == 'cinecalidadla': domains.test_domain_cinecalidadla(item)

            elif item.from_channel == 'cinecalidadlol': domains.test_domain_cinecalidadlol(item)

            elif item.from_channel == 'cinecalidadmx': domains.test_domain_cinecalidadmx(item)

            elif item.from_channel == 'cliversite': domains.test_domain_cliversite(item)

            elif item.from_channel == 'cuevana3video': domains.test_domain_cuevana3video(item)

            elif item.from_channel == 'divxtotal': domains.test_domain_divxtotal(item)

            elif item.from_channel == 'dontorrents': domains.test_domain_dontorrents(item)

            elif item.from_channel == 'elifilms': domains.test_domain_elifilms(item)

            elif item.from_channel == 'elitetorrent': domains.test_domain_elitetorrent(item)

            elif item.from_channel == 'ennovelas': domains.test_domain_ennovelas(item)

            elif item.from_channel == 'entrepeliculasyseries': domains.test_domain_entrepeliculasyseries(item)

            elif item.from_channel == 'estrenosdoramas': domains.test_domain_estrenosdoramas(item)

            elif item.from_channel == 'gnula24': domains.test_domain_gnula24(item)

            elif item.from_channel == 'grantorrent': domains.test_domain_grantorrent(item)

            elif item.from_channel == 'grantorrents': domains.test_domain_grantorrents(item)

            elif item.from_channel == 'hdfull': domains.test_domain_hdfull(item)

            elif item.from_channel == 'hdfullse': domains.test_domain_hdfullse(item)

            elif item.from_channel == 'henaojara': domains.test_domain_henaojara(item)

            elif item.from_channel == 'mejortorrentapp': domains.test_domain_mejortorrentapp(item)

            elif item.from_channel == 'pelishouse': domains.test_domain_pelishouse(item)

            elif item.from_channel == 'pelismaraton': domains.test_domain_pelismaraton(item)

            elif item.from_channel == 'pelispedia': domains.test_domain_pelispedia(item)

            elif item.from_channel == 'pelispediaws': domains.test_domain_pelispediaws(item)

            elif item.from_channel == 'pelisplus':  domains.test_domain_pelisplus(item)

            elif item.from_channel == 'pelisplushd': domains.test_domain_pelisplushd(item)

            elif item.from_channel == 'pelisplushdlat': domains.test_domain_pelisplushdlat(item)

            elif item.from_channel == 'pelisplushdnz': domains.test_domain_pelisplushdnz(item)

            elif item.from_channel == 'pelispluslat': domains.test_domain_pelispluslat(item)

            elif item.from_channel == 'playdede': domains.test_domain_playdede(item)

            elif item.from_channel == 'poseidonhd2': domains.test_domain_poseidonhd2(item)

            elif item.from_channel == 'series24': domains.test_domain_series24(item)

            elif item.from_channel == 'seriesantiguas': domains.test_domain_seriesantiguas(item)

            elif item.from_channel == 'serieskao': domains.test_domain_serieskao(item)

            elif item.from_channel == 'seriesyonkis': domains.test_domain_seriesyonkis(item)

            elif item.from_channel == 'srnovelas': domains.test_domain_srnovelas(item)

            elif item.from_channel == 'subtorrents': domains.test_domain_subtorrents(item)

            elif item.from_channel == 'torrentpelis': domains.test_domain_torrentpelis(item)

            else:
               platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Acción No Permitida[/B][/COLOR]' % color_alert)

        elif ret == 2:
            from modules import helper

            if item.from_channel == 'animefenix': helper.show_help_animefenix(item)

            elif item.from_channel == 'animeflv': helper.show_help_animeflv(item)

            elif item.from_channel == 'animeonline': helper.show_help_animeonline(item)

            elif item.from_channel == 'cinecalidadlol': helper.show_help_cinecalidadlol(item)

            elif item.from_channel == 'cinecalidadmx': helper.show_help_cinecalidadmx(item)

            elif item.from_channel == 'cuevana3video': helper.show_help_cuevana3video(item)

            elif item.from_channel == 'divxtotal': helper.show_help_divxtotal(item)

            elif item.from_channel == 'dontorrents': helper.show_help_dontorrents(item)

            elif item.from_channel == 'elifilms': helper.show_help_elifilms(item)

            elif item.from_channel == 'elitetorrent': helper.show_help_elitetorrent(item)

            elif item.from_channel == 'ennovelas': helper.show_help_ennovelas(item)

            elif item.from_channel == 'entrepeliculasyseries': helper.show_help_entrepeliculasyseries(item)

            elif item.from_channel == 'gnula24': helper.show_help_gnula24(item)

            elif item.from_channel == 'grantorrent': helper.show_help_grantorrent(item)

            elif item.from_channel == 'grantorrents': helper.show_help_grantorrents(item)

            elif item.from_channel == 'hdfull': helper.show_help_hdfull(item)

            elif item.from_channel == 'hdfullse': helper.show_help_hdfullse(item)

            elif item.from_channel == 'henaojara': helper.show_help_henaojara(item)

            elif item.from_channel == 'mejortorrentapp': helper.show_help_mejortorrentapp(item)

            elif item.from_channel == 'pelishouse': helper.show_help_pelishouse(item)

            elif item.from_channel == 'pelismaraton': helper.show_help_pelismaraton(item)

            elif item.from_channel == 'pelispedia': helper.show_help_pelispedia(item)

            elif item.from_channel == 'pelispediaws': helper.show_help_pelispediaws(item)

            elif item.from_channel == 'pelisplus': helper.show_help_pelisplus(item)

            elif item.from_channel == 'pelisplushd': helper.show_help_pelisplushd(item)

            elif item.from_channel == 'pelisplushdlat':  helper.show_help_pelisplushdlat(item)

            elif item.from_channel == 'pelisplushdnz': helper.show_help_pelisplushdnz(item)

            elif item.from_channel == 'pelispluslat': helper.show_help_pelispluslat(item)

            elif item.from_channel == 'playdede': helper.show_help_playdede(item)

            elif item.from_channel == 'series24': helper.show_help_series24(item)

            elif item.from_channel == 'seriesantiguas': helper.show_help_seriesantiguas(item)

            elif item.from_channel == 'serieskao': helper.show_help_serieskao(item)

            elif item.from_channel == 'seriesyonkis': helper.show_help_seriesyonkis(item)

            elif item.from_channel == 'srnovelas': helper.show_help_srnovelas(item)

            elif item.from_channel == 'subtorrents': helper.show_help_subtorrents(item)

            elif item.from_channel == 'torrentpelis': helper.show_help_torrentpelis(item)
