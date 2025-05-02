# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3:
    import xbmcvfs
    translatePath = xbmcvfs.translatePath
else:
    import xbmc
    translatePath = xbmc.translatePath


import os, re, glob, xbmcgui, xbmc

from platformcode import config, logger, platformtools
from core import filetools, jsontools, scrapertools

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


def manto_yourlist(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'Lista-proxies.txt')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B].../addon_data.../plugin.video.balandro[/B][/COLOR]', 'Aún No hay fichero Lista de Proxies', '[B][COLOR %s]Lista-proxies.txt[/COLOR][/B]' % color_alert)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el fichero Lista-proxies.txt ?[/B][/COLOR]'):
        filetools.remove(path)
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Fichero Lista-proxies.txt eliminado[/B][/COLOR]' % color_infor)


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

            platformtools.dialog_notification(resultados[ret]['name'], '[COLOR cyan]Cargando Tráiler[/COLOR] ...', time=3000, sound=False)

            from core import servertools

            if 'youtube' in resultados[ret]['url']:
                video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing('youtube', resultados[ret]['url'])
            else:
                video_urls = []
                logger.info("check-resultados: %s" % resultados[ret])

            if len(video_urls) > 0:
                xbmc.Player().play(video_urls[0][1])
                xbmc.sleep(1000)

                # ~ 5/4/24
                # ~ while not xbmc.Monitor().abortRequested() and xbmc.Player().isPlaying():
                # ~       xbmc.sleep(1000)

                while not xbmc.Monitor().abortRequested():
                      xbmc.sleep(1000)
                      if xbmc.Player().isPlaying():
                         if len(video_urls) == 1: break
                         else: xbmc.sleep(1000)
                      else: xbmc.sleep(1000)
            else:
                la_notif = ('[B][COLOR %s]') % color_alert
                la_notif += ('No se pudo reproducir el tráiler[/B][/COLOR]')

                platformtools.dialog_notification(resultados[ret]['name'], la_notif, time=3000, sound=False)

            if len(resultados) == 1: break

def global_proxies(item):
    logger.info()

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR yellow][B]¿ Desea Obtener [COLOR red]Proxies[COLOR yellow] en los canales que los necesiten ?[/B][/COLOR]'):
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


def show_old_domains(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name + ' ' + item.channel_id, '[B][COLOR %s]Accediendo Historial Canal[/B][/COLOR]' % color_infor)

    channel_py = item.channel_id + '.py'
    filename_py = os.path.join(config.get_runtime_path(), 'channels', channel_py)

    try:
        data = filetools.read(filename_py)
    except:
        el_canal = ('Falta [B][COLOR %s]' + channel_py) % color_alert
        platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
        return

    part_py = 'def mainlist'

    if 'ver_stable_chrome' in data: part_py = 'ver_stable_chrome'

    elif 'CLONES =' in data or 'clones =' in data: part_py = 'clones  ='
    elif 'CLASS login_' in data or 'class login_' in data: part_py = 'class login_'

    elif 'def do_make_login_logout' in data: part_py = 'def do_make_login_logout'
    elif 'def login' in data: part_py = 'def login'
    elif 'def logout' in data: part_py = 'def logout'

    elif 'def configurar_proxies' in data: part_py = 'def configurar_proxies'
    elif 'def do_downloadpage' in data: part_py = 'def do_downloadpage'

    bloc = scrapertools.find_single_match(data.lower(), '(.*?)' + part_py)
    bloc = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', bloc)

    ant_hosts = scrapertools.find_single_match(str(bloc), 'ant_hosts.*?=.*?(.*?)]')
    if not ant_hosts: ant_hosts = scrapertools.find_single_match(str(bloc), "ant_hosts.*?=.*?(.*?)]")

    if not ant_hosts:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin Historial de Dominios[/B][/COLOR]' % color_exec)
        return

    tab_hosts = scrapertools.find_multiple_matches(ant_hosts, "'(.*?)'")
    if not tab_hosts: tab_hosts = scrapertools.find_multiple_matches(ant_hosts, '"(.*?)"')

    if not tab_hosts:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin Historial de Dominios[/B][/COLOR]' % color_exec)
        return

    txt = ''

    sort_hosts = []

    i = 0

    for ant_host in tab_hosts:
        i +=1

        sort_hosts.append((i, ant_host))

    tab_hosts = sorted(sort_hosts, key=lambda i: i[0], reverse=True)

    ant_hosts = tab_hosts

    txt = '[COLOR moccasin][B]Dominios Anteriores [COLOR yellowgreen]' + item.channel_id + '[/COLOR]:[/B][CR]'

    for ant_host in ant_hosts:
        txt += '[COLOR mediumaquamarine][B]' + ant_host[1] + '[/B][/COLOR][CR]'

    platformtools.dialog_textviewer('Historial Dominios ' + item.channel_id.capitalize(), txt)


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

        config.set_setting('channel_animeflv_dominio', '')
        config.set_setting('channel_animeid_dominio', '')
        config.set_setting('channel_animeonline_dominio', '')

        config.set_setting('channel_cinecalidad_dominio', '')
        config.set_setting('channel_cinecalidadla_dominio', '')
        config.set_setting('channel_cinecalidadlol_dominio', '')
        config.set_setting('channel_cliversite_dominio', '')
        config.set_setting('channel_cuevana2_dominio', '')
        config.set_setting('channel_cuevana2esp_dominio', '')
        config.set_setting('channel_cuevana3pro_dominio', '')
        config.set_setting('channel_cuevana3video_dominio', '')

        config.set_setting('channel_divxtotal_dominio', '')
        config.set_setting('channel_dontorrents_dominio', '')
        config.set_setting('channel_dontorrentsin_dominio', '')

        config.set_setting('channel_elifilms_dominio', '')
        config.set_setting('channel_elitetorrent_dominio', '')
        config.set_setting('channel_elitetorrentnz_dominio', '')
        config.set_setting('channel_ennovelastv_dominio', '')
        config.set_setting('channel_entrepeliculasyseries_dominio', '')

        config.set_setting('channel_gnula_dominio', '')
        config.set_setting('channel_gnula24_dominio', '')
        config.set_setting('channel_gnula24h_dominio', '')
        config.set_setting('channel_grantorrent_dominio', '')

        config.set_setting('channel_hdfull_dominio', '')
        config.set_setting('channel_hdfull_hdfull_login', False)
        config.set_setting('channel_hdfull_hdfull_password', '')
        config.set_setting('channel_hdfull_hdfull_username', '')

        config.set_setting('channel_hdfullse_dominio', '')
        config.set_setting('channel_henaojara_dominio', '')
        config.set_setting('channel_homecine_dominio', '')

        config.set_setting('channel_mejortorrentapp_dominio', '')
        config.set_setting('channel_mejortorrentnz_dominio', '')
        config.set_setting('channel_mitorrent_dominio', '')

        config.set_setting('channel_novelastop_dominio', '')

        config.set_setting('channel_peliculaspro_dominio', '')
        config.set_setting('channel_pelisforte_dominio', '')
        config.set_setting('channel_pelismart_dominio', '')
        config.set_setting('channel_pelispanda_dominio', '')
        config.set_setting('channel_pelispediaws_dominio', '')
        config.set_setting('channel_pelisplus_dominio', '')
        config.set_setting('channel_pelisplushd_dominio', '')
        config.set_setting('channel_pelisplushdlat_dominio', '')
        config.set_setting('channel_pelisplushdnz_dominio', '')

        config.set_setting('channel_playdede_dominio', '')
        config.set_setting('channel_playdede_playdede_login', False)
        config.set_setting('channel_playdede_playdede_password', '')
        config.set_setting('channel_playdede_playdede_username', '')

        config.set_setting('channel_poseidonhd2_dominio', '')

        config.set_setting('channel_series24_dominio', '')
        config.set_setting('channel_serieskao_dominio', '')
        config.set_setting('channel_seriespapayato_dominio', '')
        config.set_setting('channel_seriesplus_dominio', '')
        config.set_setting('channel_srnovelas_dominio', '')
        config.set_setting('channel_subtorrents_dominio', '')

        config.set_setting('channel_todotorrents_dominio', '')

        config.set_setting('channel_veronline_dominio', '')

        config.set_setting('autoplay_max_links', '10')

        config.set_setting('proxies_totales_limit', '500')
        config.set_setting('proxies_memory', '5')

        config.set_setting('channels_proxies_memorized', '')

        config.set_setting('search_limit_by_channel', '2')

        config.set_setting('addon_tracking_interval', '12')
        config.set_setting('tracking_perpage_movies', '10')
        config.set_setting('tracking_perpage_tvshows', '10')
        config.set_setting('tracking_perpage_episodes', '10')

        config.set_setting('tmdb_threads', '20')

        config.set_setting('search_included_all', '')

        config.set_setting('search_excludes_movies', '')
        config.set_setting('search_excludes_tvshows', '')
        config.set_setting('search_excludes_documentaries', '')
        config.set_setting('search_excludes_torrents', '')
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
        config.set_setting('search_last_list', '')
        config.set_setting('search_last_video', '')

        config.set_setting('search_no_work_proxies', False)
        config.set_setting('search_no_results_proxies', True)
        config.set_setting('search_no_results', False)
        config.set_setting('search_no_channels', False)
        config.set_setting('search_multithread', True)

        config.set_setting('proxies_erase', True)
        config.set_setting('proxies_help', True)

        config.set_setting('proxies_vias', False)
        config.set_setting('proxies_tplus', '32')

        config.set_setting('proxies_list', False)

        config.set_setting('proxies_proces', True)

        download_path = filetools.join(config.get_data_path(), 'downloads')
        config.set_setting('downloadpath', download_path)

        config.set_setting('check_repo', True)
        config.set_setting('erase_cookies', False)
        config.set_setting('ver_stable_chrome', True)
        config.set_setting('httptools_timeout', '15')
        config.set_setting('notification_d_ok', False)
        config.set_setting('notification_beep', False)
        config.set_setting('channels_repeat', '30')
        config.set_setting('servers_waiting', '6')

        config.set_setting('chrome_last_version', '134.0.6998.166')  # ~ 22/3/25

        config.set_setting('debug', '0')

        config.set_setting('developer_mode', False)
        config.set_setting('developer_test_channels', '')
        config.set_setting('developer_test_servers', '')

        config.set_setting('user_test_channel', '')

        config.set_setting('sin_resp', '')

        config.set_setting('proxies_tplus_proces', '')

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
    elif config.get_setting('search_last_list', default=''): hay_lastest = True
    elif config.get_setting('search_last_video', default=''): hay_lastest = True

    if not hay_lastest:
         platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay Textos Memorizados[/COLOR][/B]' % color_alert)
         return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar los Textos Memorizados ?[/B][/COLOR]'):
        config.set_setting('search_last_all', '')
        config.set_setting('search_last_movie', '')
        config.set_setting('search_last_tvshow', '')
        config.set_setting('search_last_documentary', '')
        config.set_setting('search_last_person', '')
        config.set_setting('search_last_list', '')
        config.set_setting('search_last_video', '')

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
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero Advanced Settings[/COLOR][/B]' % color_infor)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el fichero Advanced Settings ?[/B][/COLOR]'):
        filetools.remove(file)
        platformtools.dialog_ok(config.__addon_name, '[B][COLOR pink]Fichero Advance dSettings eliminado[/B][/COLOR]', '[B][COLOR yellow]Debe Abandonar obligatoriamente su Media Center e Ingresar de nuevo en el.[/B][/COLOR]')


def manto_favs(item):
    logger.info()

    path = translatePath(os.path.join('special://home/userdata', ''))

    file_favs = 'favourites.xml'
    file = path + file_favs
    existe = filetools.exists(file)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero Favourites Settings[/COLOR][/B]' % color_infor)
        return

    if existe:
        txt_favs = ''

        try:
           with open(os.path.join(path, file_favs), 'r') as f: txt_favs=f.read(); f.close()
        except:
           try: txt_favs = open(os.path.join(path, file_favs), encoding="utf8").read()
           except: pass

        bloque = scrapertools.find_single_match(txt_favs, '<favourites>(.*?)</favourites>')

        matches = bloque.count('<favourite')

        if matches == 0: existe = False

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Favourites Settings Sin Datos[/COLOR][/B]' % color_exec)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el fichero Favourites Settings ?[/B][/COLOR]'):
        filetools.remove(file)
        platformtools.dialog_ok(config.__addon_name, '[B][COLOR pink]Fichero Favourites Settings eliminado[/B][/COLOR]')


def manto_pcfs(item):
    logger.info()

    path = translatePath(os.path.join('special://home/userdata', ''))

    file_pcfs = 'playercorefactory.xml'

    file = path + file_pcfs

    existe = filetools.exists(file)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero PlayerCoreFactory Settings[/COLOR][/B]' % color_infor)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Eliminar el fichero PlayerCoreFactory Settings ?[/B][/COLOR]'):
        filetools.remove(file)
        platformtools.dialog_ok(config.__addon_name, '[B][COLOR pink]Fichero PlayerCoreFactory Settings eliminado[/B][/COLOR]', '[B][COLOR yellow]Debe Abandonar obligatoriamente su Media Center e Ingresar de nuevo en el.[/B][/COLOR]')


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

            path_favs = translatePath(os.path.join('special://home/userdata', ''))
            file_favs = 'favourites.xml'
            file = path_favs + file_favs
            existe = filetools.exists(file)

            if existe:
                txt_favs = ''

                try:
                   with open(os.path.join(path, file_favs), 'r') as f: txt_favs=f.read(); f.close()
                except:
                   try: txt_favs = open(os.path.join(path, file_favs), encoding="utf8").read()
                   except: pass

                bloque = scrapertools.find_single_match(txt_favs, '<favourites>(.*?)</favourites>')

                matches = bloque.count('<favourite')

                if matches == 0: existe = False

            if existe:
                manto_favs(item)
                procesado = True

            path_pcfs = translatePath(os.path.join('special://home/userdata', ''))
            file_pcfs = 'playercorefactory.xml'
            file = path_pcfs + file_pcfs
            existe = filetools.exists(file)

            if existe:
                manto_pcfs(item)
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
            path = os.path.join(config.get_runtime_path(), 'Lista-proxies.txt')
            existe = filetools.exists(path)

            if existe:
                manto_yourlist(item)
                procesado = True

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


def manto_logs(item):
    logger.info()

    hay_logs = False

    path = os.path.join(config.get_data_path(), 'servers_todo.log')
    existe = filetools.exists(path)
    if existe: hay_logs = True

    path = os.path.join(config.get_data_path(), 'qualities_todo.log')
    existe = filetools.exists(path)
    if existe: hay_logs = True

    path = os.path.join(config.get_data_path(), 'proxies.log')
    existe = filetools.exists(path)
    if existe: hay_logs = True

    if hay_logs == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay ficheros Logs[/COLOR][/B]' % color_alert)
        return

    texto = '[COLOR red][B]¿ Confirma Eliminar los ficheros Logs ?[/B][/COLOR]'

    if platformtools.dialog_yesno(config.__addon_name, texto):
        path = os.path.join(config.get_data_path(), 'servers_todo.log')
        existe = filetools.exists(path)
        if existe: filetools.remove(path)

        path = os.path.join(config.get_data_path(), 'qualities_todo.log')
        existe = filetools.exists(path)
        if existe: filetools.remove(path)

        path = os.path.join(config.get_data_path(), 'proxies.log')
        existe = filetools.exists(path)
        if existe: filetools.remove(path)

        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Ficheros Logs eliminados[/B][/COLOR]' % color_infor)


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
              platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Contenido Descargas NO Localizado[/COLOR][/B]' % color_alert)
              return

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
                    platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]settings.xml[/B][/COLOR]', '[COLOR red][B][I]Imposible Eliminar su fichero de Ajustes/Preferencias. Está Bloqueado por su Sistema Media Center[/I][/B][/COLOR]', '[COLOR cyan][B]Por favor, Eliminelo manualmente en la ruta [/B][/COLOR][COLOR yellow][B].../.kodi/userdata/plugin.video.balandro[/B][/COLOR]')
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
           txt = '[COLOR yellow][B]Si es afirmativa su repuesta a la pregunta formulada, deberá salir y volver a acceder a los Ajustes y si lo desea establecer un nuevo Pin parental.[/B][/COLOR]'
           if item.erase: txt = ''

           if platformtools.dialog_yesno(config.__addon_name + ' Eliminar PIN Parental', txt, '[B][COLOR %s]¿ Desea eliminar el Pin parental memorizado ?[/COLOR][/B]' % color_alert):
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

    if path.startswith('smb://'):
        fichs = sorted(filetools.listdir(path))
        ficheros = [filetools.join(path, fit) for fit in fichs if fit.endswith('.json')]
    else:
        path = filetools.join(path, '*.json')
        ficheros = glob.glob(path)
        ficheros.sort(key=os.path.getmtime, reverse=False)

    txt = '[COLOR goldenrod][B]UBICACIÓN DESCARGAS:[/B][/COLOR][CR]'

    txt += 'Carpeta de descargas (por defecto [COLOR chocolate][B].../addon_data.../downloads[/B][/COLOR])'

    if not ficheros: txt += '[CR][CR][COLOR yellow][B]Aún no tiene[/B][/COLOR][CR]'
    else: txt += '[CR][CR][COLOR cyan][B]Hay descargas[/B][/COLOR][CR]'

    txt += '[CR]' + path.replace('*.json', '').replace('.json', '')

    txt += '[CR][CR][COLOR goldenrod][B]AJUSTES DESCARGAS:[/B][/COLOR][CR]'

    down_block = config.get_setting('block_size', default=1)

    if down_block == 0: block = '128 KB'
    elif down_block == 1: block = '256 KB'
    elif down_block == 2: block = '512 KB'
    elif down_block == 3: block = '1024 KB'
    else: cache = '2048 KB'

    txt += ' - [COLOR cyan]Tamaño por Bloque (por defecto 256 KB): [/COLOR][COLOR red][B]' + block + '[/B][/COLOR][CR]'

    down_part = config.get_setting('part_size', default=1)

    if down_part == 0: part = '1 MB'
    elif down_part == 1: part = '2 MB'
    elif down_part == 2: part = '4 MB'
    elif down_part == 3: part = '8 MB'
    elif down_part == 4: part = '16 MB'
    else: part  = '32 MB'

    txt += ' - [COLOR cyan]Tamaño por Parte (por defecto 2 MB): [/COLOR][COLOR red][B]' + part + '[/B][/COLOR][CR]'

    down_connections = config.get_setting('max_connections', default=4)

    if down_connections == 0: connections = '1'
    elif down_connections == 1: connections = '2'
    elif down_connections == 2: connections = '3'
    elif down_connections == 3: connections = '4'
    elif down_connections == 4: connections = '5'
    elif down_connections == 5: connections = '6'
    elif down_connections == 6: connections = '7'
    elif down_connections == 7: connections = '8'
    elif down_connections == 8: connections = '9'
    else: connections  = '10'

    txt += ' - [COLOR cyan]Número máximo de Conexiones Simultáneas (por defecto 5): [/COLOR][COLOR red][B]' + connections + '[/B][/COLOR][CR]'

    down_buffer = config.get_setting('max_buffer', default=4)

    if down_buffer == 0: buffer = '0'
    elif down_buffer == 1: buffer = '2'
    elif down_buffer == 2: buffer = '4'
    elif down_buffer == 3: buffer = '6'
    elif down_buffer == 4: buffer = '8'
    elif down_buffer == 5: buffer = '10'
    elif down_buffer == 6: buffer = '12'
    elif down_buffer == 7: buffer = '14'
    elif down_buffer == 8: buffer = '16'
    elif down_buffer == 9: buffer = '18'
    else: buffer = '20'

    txt += ' - [COLOR cyan]Número máximo de Partes en Memoria (por defecto 10): [/COLOR][COLOR red][B]' + buffer + '[/B][/COLOR][CR]'

    platformtools.dialog_textviewer('Ajustes de las Descargas', txt)


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


def opciones_animeflv(item):
    item.from_channel = 'animeflv'
    opciones_domains_common(item)

def opciones_animeid(item):
    item.from_channel = 'animeid'
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

def opciones_cliversite(item):
    item.from_channel = 'cliversite'
    opciones_domains_common(item)

def opciones_cuevana2(item):
    item.from_channel = 'cuevana2'
    opciones_domains_common(item)

def opciones_cuevana2esp(item):
    item.from_channel = 'cuevana2esp'
    opciones_domains_common(item)

def opciones_cuevana3pro(item):
    item.from_channel = 'cuevana3pro'
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

def opciones_dontorrentsin(item):
    item.from_channel = 'dontorrentsin'
    opciones_domains_common(item)

def opciones_elifilms(item):
    item.from_channel = 'elifilms'
    opciones_domains_common(item)

def opciones_elitetorrent(item):
    item.from_channel = 'elitetorrent'
    opciones_domains_common(item)

def opciones_elitetorrentnz(item):
    item.from_channel = 'elitetorrentnz'
    opciones_domains_common(item)

def opciones_ennovelastv(item):
    item.from_channel = 'ennovelastv'
    opciones_domains_common(item)

def opciones_entrepeliculasyseries(item):
    item.from_channel = 'entrepeliculasyseries'
    opciones_domains_common(item)

def opciones_gnula(item):
    item.from_channel = 'gnula'
    opciones_domains_common(item)

def opciones_gnula24(item):
    item.from_channel = 'gnula24'
    opciones_domains_common(item)

def opciones_gnula24h(item):
    item.from_channel = 'gnula24h'
    opciones_domains_common(item)

def opciones_grantorrent(item):
    item.from_channel = 'grantorrent'
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

def opciones_homecine(item):
    item.from_channel = 'homecine'
    opciones_domains_common(item)

def opciones_mejortorrentapp(item):
    item.from_channel = 'mejortorrentapp'
    opciones_domains_common(item)

def opciones_mejortorrentnz(item):
    item.from_channel = 'mejortorrentnz'
    opciones_domains_common(item)

def opciones_mitorrent(item):
    item.from_channel = 'mitorrent'
    opciones_domains_common(item)

def opciones_novelastop(item):
    item.from_channel = 'novelastop'
    opciones_domains_common(item)

def opciones_peliculaspro(item):
    item.from_channel = 'peliculaspro'
    opciones_domains_common(item)

def opciones_pelisforte(item):
    item.from_channel = 'pelisforte'
    opciones_domains_common(item)

def opciones_pelismart(item):
    item.from_channel = 'pelismart'
    opciones_domains_common(item)

def opciones_pelispanda(item):
    item.from_channel = 'pelispanda'
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

def opciones_playdede(item):
    item.from_channel = 'playdede'
    opciones_domains_common(item)

def opciones_poseidonhd2(item):
    item.from_channel = 'poseidonhd2'
    opciones_domains_common(item)

def opciones_series24(item):
    item.from_channel = 'series24'
    opciones_domains_common(item)

def opciones_serieskao(item):
    item.from_channel = 'serieskao'
    opciones_domains_common(item)

def opciones_seriespapayato(item):
    item.from_channel = 'seriespapayato'
    opciones_domains_common(item)

def opciones_seriesplus(item):
    item.from_channel = 'seriesplus'
    opciones_domains_common(item)

def opciones_srnovelas(item):
    item.from_channel = 'srnovelas'
    opciones_domains_common(item)

def opciones_subtorrents(item):
    item.from_channel = 'subtorrents'
    opciones_domains_common(item)

def opciones_todotorrents(item):
    item.from_channel = 'todotorrents'
    opciones_domains_common(item)

def opciones_veronline(item):
    item.from_channel = 'veronline'
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

    if domain: opciones_dominios.append(platformtools.listitem_to_select('[COLOR darkorange][B]Modificar/Eliminar el Dominio memorizado[/B][/COLOR]'))
    else: opciones_dominios.append(platformtools.listitem_to_select('[COLOR darkorange][B]Informar Nuevo Dominio manualmente[/B][/COLOR]'))

    if domain: opciones_dominios.append(platformtools.listitem_to_select('[COLOR powderblue][B]Test Web [COLOR yellow][B] ' + domain + '[/B][/COLOR]'))
    else: opciones_dominios.append(platformtools.listitem_to_select('[COLOR powderblue][B]Test Web del canal/dominio [COLOR yellow][B] ' + domain + '[/B][/COLOR]'))

    if 'notice' in str(params['clusters']): opciones_dominios.append(platformtools.listitem_to_select('[COLOR green][B]Aviso Información del canal[/B][/COLOR]'))

    ret = platformtools.dialog_select('[COLOR yellowgreen][B]Gestión Dominio ' + name + '[/B][/COLOR]', opciones_dominios)

    if not ret == -1:
        from modules import domains

        if ret == 0:
            if item.from_channel == 'animeflv': domains.manto_domain_animeflv(item)

            elif item.from_channel == 'animeid': domains.manto_domain_animeid(item)

            elif item.from_channel == 'animeonline': domains.manto_domain_animeonline(item)

            elif item.from_channel == 'cinecalidad': domains.manto_domain_cinecalidad(item)

            elif item.from_channel == 'cinecalidadla': domains.manto_domain_cinecalidadla(item)

            elif item.from_channel == 'cinecalidadlol': domains.manto_domain_cinecalidadlol(item)

            elif item.from_channel == 'cliversite': domains.manto_domain_cliversite(item)

            elif item.from_channel == 'cuevana2': domains.manto_domain_cuevana2(item)

            elif item.from_channel == 'cuevana2esp': domains.manto_domain_cuevana2esp(item)

            elif item.from_channel == 'cuevana3pro': domains.manto_domain_cuevana3pro(item)

            elif item.from_channel == 'cuevana3video': domains.manto_domain_cuevana3video(item)

            elif item.from_channel == 'divxtotal': domains.manto_domain_divxtotal(item)

            elif item.from_channel == 'dontorrents': domains.manto_domain_dontorrents(item)

            elif item.from_channel == 'dontorrentsin': domains.manto_domain_dontorrentsin(item)

            elif item.from_channel == 'elifilms': domains.manto_domain_elifilms(item)

            elif item.from_channel == 'elitetorrent': domains.manto_domain_elitetorrent(item)

            elif item.from_channel == 'elitetorrentnz': domains.manto_domain_elitetorrentnz(item)

            elif item.from_channel == 'ennovelastv': domains.manto_domain_ennovelastv(item)

            elif item.from_channel == 'entrepeliculasyseries': domains.manto_domain_entrepeliculasyseries(item)

            elif item.from_channel == 'gnula': domains.manto_domain_gnula(item)

            elif item.from_channel == 'gnula24': domains.manto_domain_gnula24(item)

            elif item.from_channel == 'gnula24h': domains.manto_domain_gnula24h(item)

            elif item.from_channel == 'grantorrent': domains.manto_domain_grantorrent(item)

            elif item.from_channel == 'hdfull': domains.manto_domain_hdfull(item)

            elif item.from_channel == 'hdfullse': domains.manto_domain_hdfullse(item)

            elif item.from_channel == 'henaojara': domains.manto_domain_henaojara(item)

            elif item.from_channel == 'homecine': domains.manto_domain_homecine(item)

            elif item.from_channel == 'mejortorrentapp': domains.manto_domain_mejortorrentapp(item)

            elif item.from_channel == 'mejortorrentnz': domains.manto_domain_mejortorrentnz(item)

            elif item.from_channel == 'mitorrent': domains.manto_domain_mitorrent(item)

            elif item.from_channel == 'novelastop': domains.manto_domain_novelastop(item)

            elif item.from_channel == 'peliculaspro': domains.manto_domain_peliculaspro(item)

            elif item.from_channel == 'pelisforte': domains.manto_domain_pelisforte(item)

            elif item.from_channel == 'pelismart': domains.manto_domain_pelismart(item)

            elif item.from_channel == 'pelispanda': domains.manto_domain_pelispanda(item)

            elif item.from_channel == 'pelispediaws': domains.manto_domain_pelispediaws(item)

            elif item.from_channel == 'pelisplus': domains.manto_domain_pelisplus(item)

            elif item.from_channel == 'pelisplushd': domains.manto_domain_pelisplushd(item)

            elif item.from_channel == 'pelisplushdlat': domains.manto_domain_pelisplushdlat(item)

            elif item.from_channel == 'pelisplushdnz': domains.manto_domain_pelisplushdnz(item)

            elif item.from_channel == 'playdede': domains.manto_domain_playdede(item)

            elif item.from_channel == 'poseidonhd2': domains.manto_domain_poseidonhd2(item)

            elif item.from_channel == 'series24': domains.manto_domain_series24(item)

            elif item.from_channel == 'serieskao': domains.manto_domain_serieskao(item)

            elif item.from_channel == 'seriespapayato': domains.manto_domain_seriespapayato(item)

            elif item.from_channel == 'seriesplus': domains.manto_domain_seriesplus(item)

            elif item.from_channel == 'srnovelas': domains.manto_domain_srnovelas(item)

            elif item.from_channel == 'subtorrents': domains.manto_domain_subtorrents(item)

            elif item.from_channel == 'todotorrents': domains.manto_domain_todotorrents(item)

            elif item.from_channel == 'veronline': domains.manto_domain_veronline(item)

            else:
               platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Acción No Permitida[/B][/COLOR]' % color_alert)

        elif ret == 1:
            if item.from_channel == 'animeflv': domains.test_domain_animeflv(item)

            elif item.from_channel == 'animeid': domains.test_domain_animeid(item)

            elif item.from_channel == 'animeonline': domains.test_domain_animeonline(item)

            elif item.from_channel == 'cinecalidad': domains.test_domain_cinecalidad(item)

            elif item.from_channel == 'cinecalidadla': domains.test_domain_cinecalidadla(item)

            elif item.from_channel == 'cinecalidadlol': domains.test_domain_cinecalidadlol(item)

            elif item.from_channel == 'cliversite': domains.test_domain_cliversite(item)

            elif item.from_channel == 'cuevana2': domains.test_domain_cuevana2(item)

            elif item.from_channel == 'cuevana2esp': domains.test_domain_cuevana2esp(item)

            elif item.from_channel == 'cuevana3pro': domains.test_domain_cuevana3pro(item)

            elif item.from_channel == 'cuevana3video': domains.test_domain_cuevana3video(item)

            elif item.from_channel == 'divxtotal': domains.test_domain_divxtotal(item)

            elif item.from_channel == 'dontorrents': domains.test_domain_dontorrents(item)

            elif item.from_channel == 'dontorrentsin': domains.test_domain_dontorrentsin(item)

            elif item.from_channel == 'elifilms': domains.test_domain_elifilms(item)

            elif item.from_channel == 'elitetorrent': domains.test_domain_elitetorrent(item)

            elif item.from_channel == 'elitetorrentnz': domains.test_domain_elitetorrentnz(item)

            elif item.from_channel == 'ennovelastv': domains.test_domain_ennovelastv(item)

            elif item.from_channel == 'entrepeliculasyseries': domains.test_domain_entrepeliculasyseries(item)

            elif item.from_channel == 'gnula': domains.test_domain_gnula(item)

            elif item.from_channel == 'gnula24': domains.test_domain_gnula24(item)

            elif item.from_channel == 'gnula24h': domains.test_domain_gnula24h(item)

            elif item.from_channel == 'grantorrent': domains.test_domain_grantorrent(item)

            elif item.from_channel == 'hdfull': domains.test_domain_hdfull(item)

            elif item.from_channel == 'hdfullse': domains.test_domain_hdfullse(item)

            elif item.from_channel == 'henaojara': domains.test_domain_henaojara(item)

            elif item.from_channel == 'homecine': domains.test_domain_homecine(item)

            elif item.from_channel == 'mejortorrentapp': domains.test_domain_mejortorrentapp(item)

            elif item.from_channel == 'mejortorrentnz': domains.test_domain_mejortorrentnz(item)

            elif item.from_channel == 'mitorrent': domains.test_domain_mitorrent(item)

            elif item.from_channel == 'novelastop': domains.test_domain_novelastop(item)

            elif item.from_channel == 'peliculaspro': domains.test_domain_peliculaspro(item)

            elif item.from_channel == 'pelisforte': domains.test_domain_pelisforte(item)

            elif item.from_channel == 'pelismart': domains.manto_domain_pelismart(item)

            elif item.from_channel == 'pelispanda': domains.manto_domain_pelispanda(item)

            elif item.from_channel == 'pelispediaws': domains.test_domain_pelispediaws(item)

            elif item.from_channel == 'pelisplus':  domains.test_domain_pelisplus(item)

            elif item.from_channel == 'pelisplushd': domains.test_domain_pelisplushd(item)

            elif item.from_channel == 'pelisplushdlat': domains.test_domain_pelisplushdlat(item)

            elif item.from_channel == 'pelisplushdnz': domains.test_domain_pelisplushdnz(item)

            elif item.from_channel == 'playdede': domains.test_domain_playdede(item)

            elif item.from_channel == 'poseidonhd2': domains.test_domain_poseidonhd2(item)

            elif item.from_channel == 'series24': domains.test_domain_series24(item)

            elif item.from_channel == 'serieskao': domains.test_domain_serieskao(item)

            elif item.from_channel == 'seriespapayato': domains.test_domain_seriespapayato(item)

            elif item.from_channel == 'seriesplus': domains.test_domain_seriesplus(item)

            elif item.from_channel == 'srnovelas': domains.test_domain_srnovelas(item)

            elif item.from_channel == 'subtorrents': domains.test_domain_subtorrents(item)

            elif item.from_channel == 'todotorrents': domains.test_domain_todotorrents(item)

            elif item.from_channel == 'veronline': domains.test_domain_veronline(item)

            else:
               platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Acción No Permitida[/B][/COLOR]' % color_alert)

        elif ret == 2:
            from modules import helper

            if item.from_channel == 'animeonline': helper.show_help_animeonline(item)

            elif item.from_channel == 'cinecalidadlol': helper.show_help_cinecalidadlol(item)

            elif item.from_channel == 'cuevana3pro': helper.show_help_cuevana3pro(item)

            elif item.from_channel == 'cuevana3video': helper.show_help_cuevana3video(item)

            elif item.from_channel == 'entrepeliculasyseries': helper.show_help_entrepeliculasyseries(item)

            elif item.from_channel == 'gnula': helper.show_help_gnula(item)

            elif item.from_channel == 'gnula24h': helper.show_help_gnula24h(item)

            elif item.from_channel == 'hdfull': helper.show_help_hdfull(item)

            elif item.from_channel == 'henaojara': helper.show_help_henaojara(item)

            elif item.from_channel == 'homecine': helper.show_help_homecine(item)

            elif item.from_channel == 'peliculaspro': helper.show_help_peliculaspro(item)

            elif item.from_channel == 'pelisforte': helper.show_help_pelisforte(item)

            elif item.from_channel == 'playdede': helper.show_help_playdede(item)

            elif item.from_channel == 'seriespapayato': helper.show_help_seriespapayato(item)

            elif item.from_channel == 'seriesplus': helper.show_help_seriesplus(item)

            elif item.from_channel == 'srnovelas': helper.show_help_srnovelas(item)

            elif item.from_channel == 'subtorrents': helper.show_help_subtorrents(item)

def quitar_autoplay(item):
    logger.info()

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Quitar el Auto Play ?[/B][/COLOR]'):
        config.set_setting('autoplay', False)

def quitar_autoplay_one_link(item):
    logger.info()

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma Quitar el Auto Play [/B][/COLOR]Si solo hay [COLOR gold][B]Un enlace[/B][/COLOR] para reproducir ?'):
        config.set_setting('autoplay_one_link', False)
