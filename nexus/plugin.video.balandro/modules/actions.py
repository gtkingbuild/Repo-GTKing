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
from core import filetools

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
            ret = xbmcgui.Dialog().select('Tráilers para %s' % nombre, opciones, useDetails=True)
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

    filtros = {'searchable': True}

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

        config.set_setting('channel_animefenix_dominio', '')
        config.set_setting('channel_animeflv_dominio', '')
        config.set_setting('channel_caricaturashd_dominio', '')
        config.set_setting('channel_cinecalidad_dominio', '')
        config.set_setting('channel_cinecalidadla_dominio', '')
        config.set_setting('channel_cinecalidadlol_dominio', '')
        config.set_setting('channel_cinetux_dominio', '')
        config.set_setting('channel_cuevana3_dominio', '')
        config.set_setting('channel_cuevana3video_dominio', '')
        config.set_setting('channel_divxtotal_dominio', '')
        config.set_setting('channel_dontorrents_dominio', '')
        config.set_setting('channel_elifilms_dominio', '')
        config.set_setting('channel_elitetorrent_dominio', '')
        config.set_setting('channel_entrepeliculasyseries_dominio', '')

        config.set_setting('channel_gnula24_dominio', '')
        config.set_setting('channel_grantorrent_dominio', '')
        config.set_setting('channel_grantorrents_dominio', '')

        config.set_setting('channel_hdfull_dominio', '')
        config.set_setting('channel_hdfull_hdfull_login', False)
        config.set_setting('channel_hdfull_hdfull_password', '')
        config.set_setting('channel_hdfull_hdfull_username', '')

        config.set_setting('channel_hdfullse_dominio', '')
        config.set_setting('channel_inkapelis_dominio', '')
        config.set_setting('channel_kindor_dominio', '')
        config.set_setting('channel_pelis28_dominio', '')
        config.set_setting('channel_pelisflix_dominio', '')
        config.set_setting('channel_pelishouse_dominio', '')
        config.set_setting('channel_pelismaraton_dominio', '')
        config.set_setting('channel_pelispedia_dominio', '')
        config.set_setting('channel_pelispediaws_dominio', '')
        config.set_setting('channel_pelisplus_dominio', '')
        config.set_setting('channel_pelisplushd_dominio', '')
        config.set_setting('channel_pelisplushdlat_dominio', '')

        config.set_setting('channel_playdede_dominio', '')
        config.set_setting('channel_playdede_playdede_login', False)
        config.set_setting('channel_playdede_playdede_password', '')
        config.set_setting('channel_playdede_playdede_username', '')

        config.set_setting('channel_repelis24_dominio', '')
        config.set_setting('channel_repelishd_dominio', '')
        config.set_setting('channel_series24_dominio', '')
        config.set_setting('channel_seriesanimadas_dominio', '')
        config.set_setting('channel_seriesyonkis_dominio', '')
        config.set_setting('channel_subtorrents_dominio', '')
        config.set_setting('channel_torrentdivx_dominio', '')
        config.set_setting('channel_torrentpelis_dominio', '')

        config.set_setting('channels_proxies_memorized', '')

        config.set_setting('search_included_all', '')

        config.set_setting('search_excludes_movies', '')
        config.set_setting('search_excludes_tvshows', '')
        config.set_setting('search_excludes_documentaries', '')
        config.set_setting('search_excludes_mixed', '')
        config.set_setting('search_excludes_all', '')

        config.set_setting('proxysearch_excludes', '')

        config.set_setting('search_last_all', '')
        config.set_setting('search_last_movie', '')
        config.set_setting('search_last_tvshow', '')
        config.set_setting('search_last_documentary', '')
        config.set_setting('search_last_person', '')

        config.set_setting('downloadpath', '')

        config.set_setting('chrome_last_version', '108.0.5359.99')

        config.set_setting('debug', '0')

        config.set_setting('developer_mode', False)
        config.set_setting('developer_test_channels', '')
        config.set_setting('developer_test_servers', '')

        config.set_setting('user_test_channel', '')

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
        path = os.path.join(config.get_data_path(), 'servers_todo.log')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'qualities_todo.log')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'proxies.log')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'info_channels.csv')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'temp.torrent')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'm3u8hls.m3u8')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'test_logs')
        existe = filetools.exists(path)
        if existe: hay_temporales = True

        path = os.path.join(config.get_data_path(), 'temp_updates.zip')
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
            path = os.path.join(config.get_data_path(), 'servers_todo.log')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'qualities_todo.log')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'proxies.log')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'info_channels.csv')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'temp.torrent')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'm3u8hls.m3u8')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

            path = os.path.join(config.get_data_path(), 'test_logs')
            existe = filetools.exists(path)
            if existe: filetools.rmdirtree(path)

            path = os.path.join(config.get_data_path(), 'temp_updates.zip')
            existe = filetools.exists(path)
            if existe: filetools.remove(path)

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


def manto_tracking_dbs(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'tracking_dbs')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Preferidos[/COLOR][/B]' % color_exec)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar Todo el contenido de sus Preferidos ?[/B][/COLOR]'):
        filetools.rmdirtree(path)
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Contenido Preferidos eliminado[/B][/COLOR]' % color_infor)


def manto_folder_downloads(item):
    logger.info()

    downloadpath = config.get_setting('downloadpath', default='')

    if downloadpath:
        path = downloadpath
    else:
        path = os.path.join(config.get_data_path(), 'downloads')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Descargas[/COLOR][/B]' % color_exec)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el contenido de Todas sus Descargas ?[/B][/COLOR]'):
        filetools.rmdirtree(path)

        # por si varió el path y quedaron descargas huerfanas en el path default
        if downloadpath:
           try:
              path = os.path.join(config.get_data_path(), 'downloads')
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
            platformtools.dialog_ok(config.__addon_name, '[COLOR yellow][B]Hay conexión con internet.[/B][/COLOR]', your_ip)
        return

    platformtools.dialog_ok(config.__addon_name, '[COLOR red][B]Parece que NO hay conexión con internet.[/B][/COLOR]', 'Compruebelo realizando cualquier Búsqueda, desde un Navegador Web ')
    return
