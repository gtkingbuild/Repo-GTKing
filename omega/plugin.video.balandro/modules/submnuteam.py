# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3:
    PY3 = True

    import xbmcvfs
    translatePath = xbmcvfs.translatePath
else:
    PY3 = False

    import xbmc
    translatePath = xbmc.translatePath


import os, xbmc, xbmcgui, xbmcaddon

from platformcode import logger, config, platformtools, updater
from core import filetools, scrapertools
from core.item import Item

from modules import filters


color_list_prefe = config.get_setting('channels_list_prefe_color', default='gold')
color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')
color_list_inactive = config.get_setting('channels_list_inactive_color', default='gray')

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


_foro = "[COLOR plum][B][I] www.mimediacenter.info/foro/ [/I][/B][/COLOR]"
_source = "[COLOR coral][B][I] https://repobal.github.io/base/ [/I][/B][/COLOR]"
_telegram = "[COLOR lightblue][B][I] t.me/balandro_asesor [/I][/B][/COLOR]"

_team = "[COLOR hotpink][B][I] t.me/balandro_team [/I][/B][/COLOR]"

tests_all_webs = []
tests_all_srvs = []

srv_pending = ''
con_incidencias = ''
no_accesibles = ''

try:
    with open(os.path.join(config.get_runtime_path(), 'dominios.txt'), 'r') as f: txt_status=f.read(); f.close()
except:
    try: txt_status = open(os.path.join(config.get_runtime_path(), 'dominios.txt'), encoding="utf8").read()
    except: txt_status = ''

if txt_status:
    bloque = scrapertools.find_single_match(txt_status, 'SITUACION SERVIDORES(.*?)SITUACION CANALES')

    matches = scrapertools.find_multiple_matches(bloque, "[B](.*?)[/B]")

    for match in matches:
        match = match.strip()

        if '[COLOR orchid]' in match: srv_pending += '[B' + match + '/I][/B][/COLOR][CR]'

    bloque = scrapertools.find_single_match(txt_status, 'SITUACION CANALES(.*?)CANALES TEMPORALMENTE DES-ACTIVADOS')

    matches = scrapertools.find_multiple_matches(bloque, "[B](.*?)[/B]")

    for match in matches:
        match = match.strip()

        if '[COLOR moccasin]' in match: con_incidencias += '[B' + match + '/I][/B][/COLOR][CR]'

    bloque = scrapertools.find_single_match(txt_status, 'CANALES PROBABLEMENTE NO ACCESIBLES(.*?)ULTIMOS CAMBIOS DE DOMINIOS')

    matches = scrapertools.find_multiple_matches(bloque, "[B](.*?)[/B]")

    for match in matches:
        match = match.strip()

        if '[COLOR moccasin]' in match: no_accesibles += '[B' + match + '/I][/B][/COLOR][CR]'

context_desarrollo = []

tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_desarrollo.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR goldenrod][B]Miscelánea[/B][/COLOR]'
context_desarrollo.append({'title': tit, 'channel': 'helper', 'action': 'show_help_miscelanea'})

tit = '[COLOR %s]Ajustes categoría Team[/COLOR]' % color_exec
context_desarrollo.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_config = []

tit = '[COLOR tan][B]Preferencias Canales[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

tit = '[COLOR darkorange]Información Dominios[/COLOR]'
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})

tit = '[COLOR %s][B]Últimos Cambios Dominios[/B][/COLOR]' % color_exec
context_config.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR darkorange][B]Quitar Dominios Memorizados[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_domains'})

tit = '[COLOR green][B]Información Plataforma[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_plataforma'})

tit = '[COLOR %s][B]Quitar Todos los Proxies[/B][/COLOR]' % color_alert
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR olive][B]Limpiezas[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_limpiezas'})

tit = '[COLOR orange][B]Borrar Carpeta Caché[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_folder_cache'})

tit = '[COLOR %s][B]Sus Ajustes Personalizados[/B][/COLOR]' % color_avis
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_sets'})

tit = '[COLOR %s][B]Cookies Actuales[/B][/COLOR]' % color_infor
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_cook'})

tit = '[COLOR %s][B]Eliminar Cookies[/B][/COLOR]' % color_infor
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_cookies'})

tit = '[COLOR %s]Sus Advanced Settings[/COLOR]' % color_adver
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_advs'})

tit = '[COLOR fuchsia][B]Eliminar Advanced Settings[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_advs'})

tit = '[COLOR mediumaquamarine][B]Restablecer Parámetros Internos[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_params'})

context_proxy_channels = []

tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR darkcyan][B]Preferencias Proxies[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_prx_parameters'})

tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_proxy_channels.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_avis
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s][B]Quitar los Proxies Actuales[/B][/COLOR]' % color_list_proxies
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR %s]Ajustes categorías Menú, Canales, Dominios y Proxies[/COLOR]' % color_exec
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_usual = []

tit = '[COLOR tan][B]Preferencias Canales[/B][/COLOR]'
context_usual.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_usual.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_usual.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_usual.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_avis
context_usual.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s][B]Quitar los Proxies Actuales[/B][/COLOR]' % color_list_proxies
context_usual.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR %s]Ajustes categorías Canales, Dominios y Proxies[/COLOR]' % color_exec
context_usual.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_ayuda = []

tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR darkorange]Información Dominios[/COLOR]'
context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})

tit = '[COLOR %s][B]Últimos Cambios Dominios[/B][/COLOR]' % color_exec
context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR %s][B]Información Versión[/B][/COLOR]' % color_infor
context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_version'})

last_fix = config.get_addon_version()

if 'fix' in last_fix:
    tit = '[COLOR %s]Información Fix[/COLOR]' % color_infor
    context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_last_fix'})

tit = '[COLOR %s]Comprobar Actualizaciones Fix[/COLOR]' % color_avis
context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'check_addon_updates'})

tit = '[COLOR %s][B]Forzar Actualizaciones Fix[/B][/COLOR]' % color_adver
context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'check_addon_updates_force'})

tit = '[COLOR green][B]Preguntas Frecuentes[/B][/COLOR]'
context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_help_faq'})

tit = '[COLOR fuchsia][B]Temas No Contemplados[/B][/COLOR]'
context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_not_contemplated'})

tit = '[COLOR goldenrod][B]Miscelánea[/B][/COLOR]'
context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_help_miscelanea'})

tit = '[COLOR darkorange][B]Test Internet[/B][/COLOR]'
context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'test_internet'})

tit = '[COLOR %s][B]Test Sistema[/B][/COLOR]' % color_avis
context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_test'})

tit = '[COLOR olive][B]Limpiezas[/B][/COLOR]'
context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'manto_limpiezas'})

tit = '[COLOR %s][B]Log Media Center[/B][/COLOR]' % color_adver
context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_log'})

tit = '[COLOR blue][B]Log Balandro Media Center[/B][/COLOR]'
context_ayuda.append({'title': tit, 'channel': 'submnuteam', 'action': 'balandro_log'})

tit = '[COLOR %s]Ajustes preferencias[/COLOR]' % color_exec
context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


def submnu_team(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]DESARROLLO:[/B]', thumbnail=config.get_thumb('team'), text_color='darkorange' ))

    itemlist.append(item.clone( action='submnu_team_info', title='[COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    if not config.get_setting('mnu_simple', default=False): tit_mnu = '[B][I]Menú Desarrollo:[/I][/B]'
    else: tit_mnu = '[B][I]Menú Desarrollo Simplificado:[/I][/B]'

    itemlist.append(item.clone( action='', title=tit_mnu, context=context_desarrollo, text_color='tan' ))

    itemlist.append(item.clone( action='submnu_center', title=' - [B]Media Center[/B]', context=context_config, thumbnail=config.get_thumb('mediacenter'), text_color='pink' ))

    itemlist.append(item.clone( action='submnu_addons', title=' - [B]Add-Ons[/B]', thumbnail=config.get_thumb('kodiaddons'), text_color='yellowgreen' ))

    itemlist.append(item.clone( action='submnu_sistema', title=' - [B]Sistema[/B]', context=context_ayuda, thumbnail=config.get_thumb('computer'), text_color='violet' ))

    presentar = False

    if os.path.exists(os.path.join(config.get_data_path(), 'servers_todo.log')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'qualities_todo.log')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'proxies.log')): presentar = True

    if presentar:
        itemlist.append(item.clone( action='submnu_logs', title=' - [B]Logs[/B]', thumbnail=config.get_thumb('tools'), text_color='limegreen' ))

    presentar = False

    if os.path.exists(os.path.join(config.get_data_path(), 'info_channels.csv')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'temp.torrent')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'm3u8hls.m3u8')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'blenditall.m3u8')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'test_logs')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'temp_updates.zip')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'tempfile_mkdtemp')): presentar = True

    if presentar:
        itemlist.append(item.clone( action='submnu_temporales', title=' - [B]Temporales[/B]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

    presentar = False

    if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developergenres.py')): presentar = True
    elif os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developertest.py')): presentar = True
    elif os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developertools.py')): presentar = True

    if presentar:
        itemlist.append(item.clone( action='submnu_gestionar', title=' - [B]Gestionar[/B]', thumbnail=config.get_thumb('tools'), text_color='teal' ))

    if not config.get_setting('mnu_simple', default=False):
        itemlist.append(item.clone( action='submnu_proxies', title=' - [B]Tests Proxies[/B]', context=context_proxy_channels, thumbnail=config.get_thumb('flame'), text_color='red' ))

    itemlist.append(item.clone( action='submnu_canales', title=' - [B]Tests Canales[/B]', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='gold' ))
    itemlist.append(item.clone( action='submnu_servidores', title=' - [B]Tests Servidores[/B]', thumbnail=config.get_thumb('bolt'), text_color='fuchsia' ))

    itemlist.append(item.clone( action='submnu_developers', title=' - [B]Developers[/B]', context=context_desarrollo, thumbnail=config.get_thumb('team'), text_color='firebrick' ))

    try: last_ver = updater.check_addon_version()
    except: last_ver = None

    if last_ver is None: last_ver = '[B][I][COLOR gray](fixes off)[/COLOR][/I][/B]'
    elif not last_ver:
          text_dev = ''
          if config.get_setting('developer_mode', default=False): text_dev = '[COLOR darkorange][B]Desarrollo[/B][/COLOR] '
          last_ver = '[B][I][COLOR %s](desfasada)[/COLOR][/I][/B]' % color_adver
          last_ver = last_ver + '  '  + text_dev
    else: last_ver = ''

    title = '[COLOR chocolate][B]Ajustes [COLOR powderblue]Preferencias[/B][/COLOR] (%s)  %s' % (config.get_addon_version().replace('.fix', '-Fix'), last_ver)

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title=title, context=context_config, thumbnail=config.get_thumb('settings'), text_color='chocolate' ))

    return itemlist


def submnu_team_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR darkorange]DESARROLLO:[/COLOR][/B]' ))

    if txt_status:
        itemlist.append(item.clone( channel='actions', action='show_latest_domains', title='[COLOR aqua][B]Últimos Cambios Dominios[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

        if con_incidencias:
            itemlist.append(item.clone( action='resumen_incidencias', title='[COLOR gold][B]Canales[/COLOR][COLOR tan] Con Incidencias[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

        if no_accesibles:
            itemlist.append(item.clone( action='resumen_no_accesibles', title='[COLOR gold][B]Canales[/COLOR][COLOR indianred] No Accesibles[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

    if config.get_setting('memorize_channels_proxies', default=True):
        itemlist.append(item.clone( channel='helper',  action='channels_with_proxies_memorized', title= '[COLOR gold][B]Canales[/COLOR][COLOR red][B] Con Proxies[/B][/COLOR]', new_proxies=True, memo_proxies=True, test_proxies=True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='resumen_canales', title='[COLOR gold][B]Canales[/B][/COLOR] Resúmenes y Distribución', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='resumen_servidores', title='[COLOR fuchsia][B]Servidores[/B][/COLOR] Resúmenes y Distribución', thumbnail=config.get_thumb('bolt') ))

    if txt_status:
        if srv_pending:
            itemlist.append(item.clone( action='resumen_pending', title='[COLOR fuchsia][B]Servidores[/COLOR][COLOR tan] Con Incidencias[/B][/COLOR]', thumbnail=config.get_thumb('bolt') ))

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        itemlist.append(item.clone( action='show_help_alternativas', title='Qué servidores tienen [COLOR yellow][B]Vías Alternativas[/B][/COLOR]', thumbnail=config.get_thumb('bolt') ))
        itemlist.append(item.clone( action='show_help_adicionales', title='Servidores [COLOR goldenrod][B]Vías Adicionales[/B][/COLOR] a través de [COLOR yellowgreen][B]ResolveUrl[/B][/COLOR]', thumbnail=config.get_thumb('resolveurl') ))

    return itemlist


def submnu_center(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]MEDIA CENTER:[/B]', thumbnail=config.get_thumb('mediacenter'), text_color='pink' ))

    if not item.helper:
        itemlist.append(item.clone( action='submnu_center_info', title='[COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    path = translatePath(os.path.join('special://home/userdata', ''))

    file_advs = 'advancedsettings.xml'
    file = path + file_advs
    existe = filetools.exists(file)

    if existe:
        itemlist.append(item.clone( action='', title='[I]ARCHIVO ADVANCED SETTINGS:[/I]', text_color='pink' ))

        itemlist.append(item.clone( channel='helper', action='show_advs', title=' - Ver', thumbnail=config.get_thumb('quote'), text_color='yellow' ))
        itemlist.append(item.clone( channel='actions', action='manto_advs', title=' - Eliminar [B][COLOR violet](Si ejecuta es Recomendable Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('quote'), text_color='red' ))

    file_favs = 'favourites.xml'
    file = path + file_favs
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
        itemlist.append(item.clone( action='', title='[I]ARCHIVO FAVOURITES SETTINGS:[/I]', text_color='pink' ))

        itemlist.append(item.clone( channel='helper', action='show_favs', title=' - Ver', thumbnail=config.get_thumb('quote'), text_color='yellow' ))
        itemlist.append(item.clone( channel='actions', action='manto_favs', title=' - Eliminar', thumbnail=config.get_thumb('quote'), text_color='red' ))

    file_pcfs = 'playercorefactory.xml'
    file = path + file_pcfs
    existe = filetools.exists(file)

    if existe:
        itemlist.append(item.clone( action='', title='[I]ARCHIVO PLAYERCOREFACTORY SETTINGS:[/I]', text_color='pink' ))

        itemlist.append(item.clone( channel='helper', action='show_pcfs', title=' - Ver', thumbnail=config.get_thumb('quote'), text_color='yellow' ))
        itemlist.append(item.clone( channel='actions', action='manto_pcfs', title=' - Eliminar [B][COLOR violet](Si ejecuta es Recomendable Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('quote'), text_color='red' ))

    presentar = False

    path_cache = translatePath(os.path.join('special://temp/archive_cache', ''))
    existe_cache = filetools.exists(path_cache)

    caches = []
    if existe_cache: caches = os.listdir(path_cache)

    if caches: presentar = True

    if presentar:
        itemlist.append(item.clone( action='', title='[I]ARCHIVOS EN LA CACHÉ:[/I]', text_color='pink' ))

        itemlist.append(item.clone( action='show_addons', title=' - Ver', addons = caches, tipo = 'Caché', thumbnail=config.get_thumb('keyboard'), text_color='yellow' ))

        itemlist.append(item.clone( channel='actions', action='manto_caches', title=' - Eliminar [B][COLOR cyan](Si ejecuta es Obligatorio Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('keyboard'), text_color='red' ))

    path_thumbs = translatePath(os.path.join('special://home/userdata/Thumbnails', ''))
    existe_thumbs = filetools.exists(path_thumbs)

    if existe_thumbs:
        itemlist.append(item.clone( action='', title='[I]ARCHIVOS EN THUMBNAILS:[/I]', text_color='pink' ))

        itemlist.append(item.clone( channel='actions', action='manto_thumbs', title=' - Eliminar [B][COLOR cyan](Si ejecuta es Obligatorio Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('keyboard'), text_color='red' ))

    if item.helper: platformtools.itemlist_refresh()

    if not itemlist:
        if item.helper:
            platformtools.dialog_notification(config.__addon_name + ' [COLOR olive][B]Media Center[/B][/COLOR]', '[B][COLOR cyan]Nada que Limpiar[/B][/COLOR]')
            return

    return itemlist


def submnu_center_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR pink]MEDIA CENTER:[/COLOR][/B]' ))

    itemlist.append(item.clone( channel='helper', action='show_plataforma', title='[COLOR gold][B]Plataforma[/B][/COLOR]', thumbnail=config.get_thumb('mediacenter') ))

    itemlist.append(item.clone( channel='actions', action = 'test_internet', title= 'Comprobar [COLOR goldenrod][B]Internet[/B][/COLOR]', thumbnail=config.get_thumb('crossroads') ))

    itemlist.append(item.clone( action='', title='[I]ARCHIVO LOG BALANDRO:[/I]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

    itemlist.append(item.clone( action='balandro_log', title=' -  Ver Log ejecución Balandro', thumbnail=config.get_thumb('search'), text_color='coral' ))

    itemlist.append(item.clone( action='', title='[I]ARCHIVO LOG GENERAL:[/I]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

    itemlist.append(item.clone( channel='helper', action='show_log', title=' - Ver Log', thumbnail=config.get_thumb('computer'), text_color='yellow' ))
    itemlist.append(item.clone( channel='helper', action='copy_log', title=' - Obtener una Copia', thumbnail=config.get_thumb('folder'), text_color='yellowgreen' ))

    return itemlist


def submnu_addons(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]ADD-ONS:[/B]', thumbnail=config.get_thumb('tools'), text_color='yellowgreen' ))

    if not item.helper:
        itemlist.append(item.clone( action='submnu_addons_info', title='[COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    presentar = False

    path_packages = translatePath(os.path.join('special://home/addons/packages', ''))
    existe_packages = filetools.exists(path_packages)

    packages = []
    if existe_packages: packages = os.listdir(path_packages)

    path_temp = translatePath(os.path.join('special://home/addons/temp', ''))
    existe_temp = filetools.exists(path_temp)

    temps = []
    if existe_temp: temps = os.listdir(path_temp)

    if packages: presentar = True
    elif temps: presentar = True

    if presentar:
        if packages:
            itemlist.append(item.clone( action='', title='[I]ARCHIVOS EN PACKAGES:[/I]', thumbnail=config.get_thumb('kodiaddons'), text_color='yellowgreen' ))

            itemlist.append(item.clone( action='show_addons', title=' - Ver', addons = packages, tipo = 'Packages', thumbnail=config.get_thumb('keyboard'), text_color='yellow' ))

            itemlist.append(item.clone( channel='actions', action='manto_addons_packages', title=' - Eliminar [B][COLOR violet](Si ejecuta es Recomendable Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('keyboard'), text_color='red' ))

        if temps:
            itemlist.append(item.clone( action='', title='[I]ARCHIVOS EN TEMP:[/I]', thumbnail=config.get_thumb('kodiaddons'), text_color='yellowgreen' ))

            itemlist.append(item.clone( action='show_addons', title=' - Ver', addons = temps, tipo = 'Temp', thumbnail=config.get_thumb('keyboard'), text_color='yellow' ))

            itemlist.append(item.clone( channel='actions', action='manto_addons_temp', title=' - Eliminar [B][COLOR violet](Si ejecuta es Recomendable Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('keyboard'), text_color='red' ))

    if item.helper: platformtools.itemlist_refresh()

    if not presentar:
        if item.helper:
            platformtools.dialog_notification(config.__addon_name + ' [COLOR olive][B]Add-Ons[/B][/COLOR]', '[B][COLOR cyan]Nada que Limpiar[/B][/COLOR]')
            return

    return itemlist


def submnu_addons_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR yellowgreen]ADD-ONS:[/COLOR][/B]' ))

    itemlist.append(item.clone( channel='helper', action='show_help_vias', title= 'Vía alternativa [COLOR goldenrod][B]ResolveUrl[/B][/COLOR]', thumbnail=config.get_thumb('resolveurl') ))
    itemlist.append(item.clone( channel='helper', action='show_help_vias', title= 'Vía alternativa [COLOR goldenrod][B]Youtube[/B][/COLOR]', thumbnail=config.get_thumb('youtube') ))

    itemlist.append(item.clone( channel='helper', action='show_help_torrents', title= '¿ Dónde obtener los Add-Ons para [COLOR gold][B]Clientes/Motores[/B][/COLOR] torrents ?', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( channel='helper', action='show_clients_torrent', title= 'Clientes/Motores externos torrent [COLOR gold][B]Soportados[/B][/COLOR]', thumbnail=config.get_thumb('cloud') ))

    itemlist.append(item.clone( action='', title='[B]Balandro[/B] [I]ADD-ONS EXTERNOS y VIAS ALTERNATIVAS:[/I]', thumbnail=config.get_thumb('kodiaddons'), text_color='yellowgreen' ))

    if config.get_setting('mnu_torrents', default=True):
        cliente_torrent = config.get_setting('cliente_torrent', default='Seleccionar')

        if cliente_torrent == 'Seleccionar' or cliente_torrent == 'Ninguno': tex_tor = cliente_torrent
        else:
           tex_tor = cliente_torrent
           cliente_torrent = 'plugin.video.' + cliente_torrent.lower()
           if xbmc.getCondVisibility('System.HasAddon("%s")' % cliente_torrent):
               cod_version = xbmcaddon.Addon(cliente_torrent).getAddonInfo("version").strip()
               tex_tor += '  [COLOR goldenrod]' + cod_version + '[/COLOR]'

        itemlist.append(item.clone( action = '', title= ' - Cliente/Motor Torrent asignado ' + '[COLOR fuchsia][B] ' + tex_tor + '[/B][/COLOR]', thumbnail=config.get_thumb('torrents') ))

        if xbmc.getCondVisibility('System.HasAddon("script.elementum.burst")'):
            cod_version = xbmcaddon.Addon("script.elementum.burst").getAddonInfo("version").strip()
            tex_tor = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
        else: tex_tor = '  [COLOR red]No instalado[/COLOR]'

        itemlist.append(item.clone( action = '', title= ' - [COLOR fuchsia][B]Elementum Burst[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_tor + '[/B][/COLOR]', thumbnail=config.get_thumb('elementum') ))

    if xbmc.getCondVisibility('System.HasAddon("inputstream.adaptive")'):
        cod_version = xbmcaddon.Addon("inputstream.adaptive").getAddonInfo("version").strip()
        tex_ia = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_ia = '  [COLOR red]No instalado[/COLOR]'

    itemlist.append(item.clone( action = '', title= ' - [COLOR fuchsia][B]InputStream Adaptive[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_ia + '[/B][/COLOR]', thumbnail=config.get_thumb('Inputstreamadaptive') ))

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
        cod_version = xbmcaddon.Addon("plugin.video.youtube").getAddonInfo("version").strip()
        tex_yt = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_yt = '  [COLOR red]No instalado[/COLOR]'

    itemlist.append(item.clone( action = '', title= ' - [COLOR fuchsia][B]Youtube[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_yt + '[/B][/COLOR]', thumbnail=config.get_thumb('youtube') ))

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        cod_version = xbmcaddon.Addon("script.module.resolveurl").getAddonInfo("version").strip()
        tex_mr = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_mr = '  [COLOR red]No instalado[/COLOR]'

    itemlist.append(item.clone( action = '', title= ' - [COLOR fuchsia][B]ResolveUrl[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_mr + '[/B][/COLOR]', thumbnail=config.get_thumb('resolveurl') ))

    itemlist.append(item.clone( action='', title='[B]Balandro[/B] [I]ADD-ONS EXTERNOS REPOSITORIOS:[/I]', thumbnail=config.get_thumb('kodiaddons'), text_color='yellowgreen' ))

    if xbmc.getCondVisibility('System.HasAddon("repository.resolveurl")'):
        cod_version = xbmcaddon.Addon("repository.resolveurl").getAddonInfo("version").strip()
        tex_rp = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_rp = '  [COLOR red]No instalado[/COLOR]'

    itemlist.append(item.clone( action = '', title= ' - [COLOR gold][B]Repository ResolveUrl[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_rp + '[/B][/COLOR]', thumbnail=config.get_thumb('resolveurl') ))

    if config.get_setting('mnu_torrents', default=True):
        if xbmc.getCondVisibility('System.HasAddon("repository.elementum")'):
            cod_version = xbmcaddon.Addon("repository.elementum").getAddonInfo("version").strip()
            tex_rp = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
        else: tex_rp = '  [COLOR red]No instalado[/COLOR]'

        itemlist.append(item.clone( action = '', title= ' - [COLOR gold][B]Repository Elementum[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_rp + '[/B][/COLOR]', thumbnail=config.get_thumb('elementum') ))

        if xbmc.getCondVisibility('System.HasAddon("repository.elementumorg")'):
            cod_version = xbmcaddon.Addon("repository.elementumorg").getAddonInfo("version").strip()
            tex_rp = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
        else: tex_rp = '  [COLOR red]No instalado[/COLOR]'

        itemlist.append(item.clone( action = '', title= ' - [COLOR gold][B]Repository ElementumOrg[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_rp + '[/B][/COLOR]', thumbnail=config.get_thumb('elementum') ))

    itemlist.append(item.clone( action='submnu_resto_addons', title='[I]ADD-ONS y SCRIPTS CON DATOS[/I]', thumbnail=config.get_thumb('kodiaddons'), text_color='yellowgreen' ))

    return itemlist


def submnu_resto_addons(item):
    logger.info()
    itemlist = []

    path = translatePath(os.path.join('special://home/userdata/addon_data', ''))

    addons = filetools.listdir(path)

    txt = ''

    for addon in addons:
        txt += '  ' + str(addon) + '[CR][CR]'

    platformtools.dialog_textviewer('Add-Ons con Datos', txt)


def submnu_sistema(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]SISTEMA:[/B]', text_color='violet' ))

    if not item.helper:
        itemlist.append(item.clone( action='submnu_sistema_info', title='[COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    path = os.path.join(config.get_data_path(), 'Lista-proxies.txt')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]ARCHIVO LISTA-PROXIES.TXT:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        itemlist.append(item.clone( channel='helper', action='show_yourlist', title=' - Ver', thumbnail=config.get_thumb('keyboard'), text_color='yellow' ))

        itemlist.append(item.clone( channel='actions', action='manto_yourlist', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    path = os.path.join(config.get_data_path(), 'cookies.dat')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]ARCHIVO COOKIES:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        itemlist.append(item.clone( channel='actions', action='manto_cookies', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    path = os.path.join(config.get_data_path(), 'cache')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]CARPETA CACHÉ:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        itemlist.append(item.clone( channel='actions', action='manto_folder_cache', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    if not item.helper:
        path = filetools.join(config.get_data_path(), 'tracking_dbs')

        existe = filetools.exists(path)

        if existe:
            itemlist.append(item.clone( action='', title='[I]CONTENIDO PREFERIDOS:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

            itemlist.append(item.clone( channel='actions', action='manto_tracking_dbs', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

        downloadpath = config.get_setting('downloadpath', default='')

        if downloadpath: path = downloadpath
        else: path = filetools.join(config.get_data_path(), 'downloads')

        existe = filetools.exists(path)

        if existe:
            itemlist.append(item.clone( action='', title='[I]CONTENIDO DESCARGAS:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

            itemlist.append(item.clone( channel='actions', action='manto_folder_downloads', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    path = filetools.join(config.get_data_path(), 'tmdb.sqlite-journal')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]ARCHIVO TMDB SQLITE JOURNAL:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        itemlist.append(item.clone( channel='actions', action='manto_tmdb_sqlite', title= " - Eliminar", journal = 'journal', thumbnail=config.get_thumb('computer'), text_color='red' ))

    path = filetools.join(config.get_data_path(), 'tmdb.sqlite')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]ARCHIVO TMDB SQLITE:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        itemlist.append(item.clone( channel='actions', action='manto_tmdb_sqlite', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    if not item.helper:
        path = config.get_data_path()

        existe = filetools.exists(path)

        if existe:
            itemlist.append(item.clone( action='', title='[I]AJUSTES PREFERENCIAS:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

            itemlist.append(item.clone( channel='actions', action='manto_folder_addon', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    if item.helper: platformtools.itemlist_refresh()

    if not itemlist:
        if item.helper:
            platformtools.dialog_notification(config.__addon_name + ' [COLOR olive][B]Sistema[/B][/COLOR]', '[B][COLOR cyan]Nada que Limpiar[/B][/COLOR]')
            return

    return itemlist


def submnu_sistema_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR violet]SISTEMA:[/COLOR][/B]' ))

    itemlist.append(item.clone( action='show_sistema', title= 'Información [COLOR teal][B]Ajustes del Sistema[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( channel='actions', action='show_latest_domains', title='[COLOR aqua][B]Últimos Cambios Dominios[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( channel='helper', action='show_version', title= '[COLOR lime][B]Versión[/B][/COLOR]', thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( channel='actions', action = 'test_internet', title= 'Comprobar [COLOR goldenrod][B]Internet[/B][/COLOR]', thumbnail=config.get_thumb('crossroads') ))
    itemlist.append(item.clone( channel='helper', action='show_test', title= 'Test [COLOR gold][B]Status[/B][/COLOR] del sistema', thumbnail=config.get_thumb('addon') ))

    txt_python = '  %s.%s.%s[CR][CR]' % (str(sys.version_info[0]), str(sys.version_info[1]), str(sys.version_info[2]))
    itemlist.append(item.clone( action='', title='[COLOR green][B]Versión Python[/COLOR][COLOR violet]' + txt_python + '[/COLOR][/B]', thumbnail=config.get_thumb('python') ))

    path = os.path.join(config.get_runtime_path(), 'last_fix.json')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]ARCHIVO FIX:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        if config.get_setting('addon_update_atstart', default=True):
            itemlist.append(item.clone( action='', title= ' - Comprobar Fixes al [COLOR goldenrod][B]Iniciar[/B][/COLOR] su Media Center [COLOR yellow][B]Activado[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))
        else:
            itemlist.append(item.clone( action='', title= ' - Comprobar Fixes al [COLOR goldenrod][B]Iniciar[/B][/COLOR] su Media Center [COLOR red][B]Des-Activado[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

        itemlist.append(item.clone( channel='helper', action='show_last_fix', title= ' - [COLOR green][B]Información[/B][/COLOR] Fix instalado', thumbnail=config.get_thumb('news') ))
        itemlist.append(item.clone( channel='actions', action='manto_last_fix', title= " - Eliminar fichero control 'Fix'", thumbnail=config.get_thumb('news'), text_color='red' ))

    return itemlist


def submnu_logs(item):
    logger.info()
    itemlist = []

    presentar = False

    if os.path.exists(os.path.join(config.get_data_path(), 'servers_todo.log')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'qualities_todo.log')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'proxies.log')): presentar = True

    if presentar:
        itemlist.append(item.clone( action='', title='[B]LOGS:[/B]', thumbnail=config.get_thumb('tools'), text_color='limegreen' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'servers_todo.log')):
            itemlist.append(item.clone( action='', title='[I]LOG SERVIDORES:[/I]', thumbnail=config.get_thumb('tools'), text_color='limegreen' ))

            itemlist.append(item.clone( channel='helper', action='show_todo_log', title=' - Ver', todo = 'servers_todo.log', thumbnail=config.get_thumb('crossroads'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'qualities_todo.log')):
            itemlist.append(item.clone( action='', title='[I]LOG CALIDADES:[/I]', thumbnail=config.get_thumb('tools'), text_color='limegreen' ))

            itemlist.append(item.clone( channel='helper', action='show_todo_log', title=' - Ver', todo = 'qualities_todo.log', thumbnail=config.get_thumb('quote'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'proxies.log')):
            itemlist.append(item.clone( action='', title='[I]LOG PROXIES:[/I]', thumbnail=config.get_thumb('tools'), text_color='limegreen' ))

            itemlist.append(item.clone( channel='helper', action='show_todo_log', title=' - Ver', todo = 'proxies.log', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        itemlist.append(item.clone( channel='actions', action='manto_temporales', title='Eliminar Todos los LOGS', _logs = True, thumbnail=config.get_thumb('keyboard'), text_color='red' ))

    if item.helper: platformtools.itemlist_refresh()

    if not itemlist:
        if item.helper:
            platformtools.dialog_notification(config.__addon_name + ' [COLOR olive][B]Logs[/B][/COLOR]', '[B][COLOR cyan]Nada que Limpiar[/B][/COLOR]')
            return

    return itemlist


def submnu_temporales(item):
    logger.info()
    itemlist = []

    presentar = False

    if os.path.exists(os.path.join(config.get_data_path(), 'info_channels.csv')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'temp.torrent')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'm3u8hls.m3u8')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'blenditall.m3u8')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'test_logs')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'temp_updates.zip')): presentar = True
    elif os.path.exists(os.path.join(config.get_data_path(), 'tempfile_mkdtemp')): presentar = True

    if presentar:
        itemlist.append(item.clone( action='', title='[B]TEMPORALES:[/B]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'info_channels.csv')):
            itemlist.append(item.clone( action='', title='[I]FICHEROS INFO CHANNELS:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay Info channels', thumbnail=config.get_thumb('dev'), text_color='goldenrod' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'temp.torrent')):
            itemlist.append(item.clone( action='', title='[I]FICHERO TORRENT:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay Torrent', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'm3u8hls.m3u8')):
            itemlist.append(item.clone( action='', title='[I]FICHERO M3U8HLS:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay M3u8hls', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'blenditall.m3u8')):
            itemlist.append(item.clone( action='', title='[I]FICHERO BLENDITALL:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay M3u8', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'test_logs')):
            itemlist.append(item.clone( action='', title='[I]FICHEROS TEST LOGS:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay Test logs', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'temp_updates.zip')):
            itemlist.append(item.clone( action='', title='[I]FICHERO UPDATES:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay Updates', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'tempfile_mkdtemp')):
            itemlist.append(item.clone( action='', title='[I]FICHEROS MKDTEMP:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay Mkdtemp', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        itemlist.append(item.clone( channel='actions', action='manto_temporales', title='Eliminar', thumbnail=config.get_thumb('keyboard'), text_color='red' ))

    if item.helper: platformtools.itemlist_refresh()

    if not itemlist:
        if item.helper:
            platformtools.dialog_notification(config.__addon_name + ' [COLOR olive][B]Temporales[/B][/COLOR]', '[B][COLOR cyan]Nada que Limpiar[/B][/COLOR]')
            return

    return itemlist


def submnu_gestionar(item):
    logger.info()
    itemlist = []

    presentar = False

    if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developergenres.py')): presentar = True
    elif os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developertest.py')): presentar = True
    elif os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developertools.py')): presentar = True

    if presentar:
        itemlist.append(item.clone( action='', title='[B]GESTIONAR:[/B]', thumbnail=config.get_thumb('tools'), text_color='teal' ))

        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developergenres.py')):
            itemlist.append(item.clone( channel='developergenres', action='mainlist', title=' - [COLOR thistle][B]Géneros[/B][/COLOR]', thumbnail=config.get_thumb('genres') ))

        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developertest.py')):
            itemlist.append(item.clone( channel='developertest', action='mainlist', title=' - [COLOR gold][B]Canales y Servidores[/B][/COLOR]', thumbnail=config.get_thumb('tools') ))

        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developertools.py')):
            if os.path.exists(os.path.join(config.get_data_path(), 'developer.sqlite')):
                itemlist.append(item.clone( channel='developertools', action='mainlist', title=' - [COLOR olive][B]Queries[/B][/COLOR] Canales y Servidores', thumbnail=config.get_thumb('tools') ))

    return itemlist


def submnu_proxies(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]TESTS PROXIES:[/B]', text_color='red' ))

    itemlist.append(item.clone( action='submnu_proxies_info', title=' - [COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( action='test_providers', title= ' - [COLOR yellowgreen][B]Tests[/B][/COLOR] Proveedores', thumbnail=config.get_thumb('flame') ))

    itemlist.append(item.clone( action='test_tplus', title= ' - Asignar proveedor [COLOR goldenrod][B]TPlus[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title='[I]OPCIONES PROXIES:[/I]', thumbnail=config.get_thumb('tools'), text_color='red' ))

    itemlist.append(item.clone( channel='helper', action='channels_with_proxies', title= ' - Qué canales pueden usar Proxies', new_proxies=True, test_proxies=True, thumbnail=config.get_thumb('stack') ))

    if config.get_setting('memorize_channels_proxies', default=True):
        itemlist.append(item.clone( channel='helper', action='channels_with_proxies_memorized', title= ' - Qué [COLOR red]canales[/COLOR] tiene con proxies [COLOR red][B]Memorizados[/B][/COLOR]', new_proxies=True, memo_proxies=True, test_proxies=True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='actions', action = 'manto_proxies', title= ' - Quitar los proxies en los canales [COLOR red][B](que los tengan Memorizados)[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='actions', action = 'global_proxies', title = ' - Configurar proxies a usar [COLOR plum][B](en los canales que los necesiten)[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    presentar = False

    path = os.path.join(config.get_data_path(), 'Lista-proxies.txt')

    existe = filetools.exists(path)

    if existe: presentar = True

    if presentar:
        itemlist.append(item.clone( action='', title='[I]FICHERO LISTA-PROXIES.TXT:[/I]', thumbnail=config.get_thumb('tools'), text_color='red' ))

        itemlist.append(item.clone( channel='helper', action='show_help_yourlist', title= ' - [COLOR goldenrod][B]Gestión[/B][/COLOR] Fichero Personalizado', thumbnail=config.get_thumb('pencil') ))

        itemlist.append(item.clone( channel='helper', action='show_yourlist', title= ' - [COLOR green][B]Contenido[/B][/COLOR] de su Fichero [COLOR gold][B]Personalizado[/B][/COLOR] de proxies', thumbnail=config.get_thumb('news') ))

        itemlist.append(item.clone( channel='actions', action='manto_yourlist', title= ' - [COLOR red][B]Eliminar[/B][/COLOR] su Fichero [COLOR yellow][B]Personalizado[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_proxies_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR red]TEST PROXIES:[/COLOR][/B]' ))

    itemlist.append(item.clone( channel='helper', action='show_help_proxies', title= 'Uso de proxies' ))
    itemlist.append(item.clone( channel='helper', action='show_help_providers', title= 'Proveedores de proxies' ))

    if config.get_setting('proxies_extended', default=False):
        itemlist.append(item.clone( channel='helper', action='show_help_providers2', title= 'Lista [COLOR aqua][B]Ampliada[/B][/COLOR] de Proveedores de proxies' ))

    if config.get_setting('proxies_vias', default=False): 
        itemlist.append(item.clone( channel='helper', action='proxies_show_vias', title= 'Lista [COLOR aqua][B]Vías Alternativas[/B][/COLOR] de Proveedores de proxies' ))

    return itemlist


def submnu_canales(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]TESTS CANALES:[/B]', text_color='gold' ))

    itemlist.append(item.clone( action='submnu_canales_info', title=' - [COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( action='test_all_webs', title=' - Posibles [B][COLOR gold]Insatisfactorios[/B][/COLOR]', unsatisfactory = True ))
    itemlist.append(item.clone( action='test_alfabetico', title=' - [COLOR gold]Insatisfactorios[/COLOR] desde un canal [B][COLOR powderblue]letra inicial[/B][/COLOR]', unsatisfactory = True ))

    itemlist.append(item.clone( action='test_all_webs', title=' - Todos' ))

    itemlist.append(item.clone( action='test_one_channel', title=' - Un canal concreto' ))

    itemlist.append(item.clone( action='test_one_channel', title= ' - Temporalmente [B][COLOR mediumaquamarine]Inactivos[/B][/COLOR]', temp_no_active = True ))

    return itemlist


def submnu_canales_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR gold]CANALES:[/COLOR][/B]' ))

    itemlist.append(item.clone( channel='helper', action='show_channels_list', title= ' - [COLOR gold][B]Todos[/B][/COLOR] los Canales', tipo = 'all' ))

    itemlist.append(item.clone( channel='helper', action='show_channels_list', title= ' - Qué canales están [COLOR gold][B]Disponibles[/B][/COLOR] (Activos)' ))
    itemlist.append(item.clone( channel='helper', action='show_channels_list', title= ' - Qué canales están [COLOR aquamarine][B]Sugeridos[/B][/COLOR]', suggesteds = True, thumbnail=config.get_thumb('suggested') ))

    itemlist.append(item.clone( channel='helper', action='channels_prefered', title= ' - Qué canales tiene marcados como [COLOR gold][B]Preferidos[/B][/COLOR]' ))
    itemlist.append(item.clone( channel='helper', action='channels_no_actives', title= '    - Qué canales tiene marcados como [COLOR gray][B]Desactivados[/B][/COLOR]' ))

    itemlist.append(item.clone( channel='helper', action='channels_with_notice', title= ' - Qué canales tienen [COLOR green][B]Aviso[/COLOR][COLOR red] CloudFlare [COLOR orangered]Protection[/B][/COLOR]' ))

    itemlist.append(item.clone( channel='helper', action='channels_with_proxies', title= '    - Qué canales pueden necesitar [COLOR red][B]Proxies[/B][/COLOR]', new_proxies=True ))
    if config.get_setting('memorize_channels_proxies', default=True):
        itemlist.append(item.clone( channel='helper', action='channels_with_proxies_memorized', title= ' - Qué [COLOR red]canales[/COLOR] tiene con proxies [COLOR red][B]Memorizados[/B][/COLOR]', new_proxies=True, memo_proxies=True, test_proxies=True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='helper', action='show_channels_list', title= '    - Qué canales están [COLOR plum][B]Inestables[/B][/COLOR]', no_stable = True ))
    itemlist.append(item.clone( channel='helper', action='show_channels_list', title= '    - Qué canales son [COLOR darkgoldenrod][B]Problemátios[/B][/COLOR] (Predominan Sin enlaces Disponibles/Válidos/Soportados)', problematics = True ))
    itemlist.append(item.clone( channel='helper', action='show_channels_list', title= '    - Qué canales son [COLOR turquoise][B]Clones[/B][/COLOR] (Clon del Canal Principal)', clones = True ))
    itemlist.append(item.clone( channel='helper', action='show_channels_list_temporaries', title= '    - Qué canales están [COLOR cyan][B]Temporalmente[/B][/COLOR] inactivos' ))
    itemlist.append(item.clone( channel='helper', action='show_channels_list', title= '    - Qué canales son [COLOR grey][B]Privados[/B][/COLOR]', tipo = 'all', privates = True ))

    if not PY3:
        itemlist.append(item.clone( channel='helper', action='show_channels_list', title= '    - Qué canales son [COLOR violet][B]Incompatibiles[/B][/COLOR] con su Media Center', mismatched = True ))

    itemlist.append(item.clone( channel='helper', action='show_channels_list_inactives', title= '    - Qué canales están [COLOR coral][B]Inactivos[/B][/COLOR]' ))

    return itemlist


def submnu_servidores(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]TESTS SERVIDORES:[/B]', text_color='fuchsia' ))

    itemlist.append(item.clone( action='submnu_servidores_info', title=' - [COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( action='test_all_srvs', title=' - Posibles [B][COLOR fuchsia]Insatisfactorios[/B][/COLOR]', unsatisfactory = True ))
    itemlist.append(item.clone( action='test_alfabetico', title=' - [COLOR fuchsia]Insatisfactorios[/COLOR] desde un servidor [B][COLOR powderblue]letra inicial[/B][/COLOR]', unsatisfactory = True ))

    itemlist.append(item.clone( action='test_all_srvs', title=' - Todos' ))

    itemlist.append(item.clone( action='test_one_server', title=' - Un servidor concreto' ))

    return itemlist


def submnu_servidores_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR fuchsia]SERVIDORES:[/COLOR][/B]' ))

    itemlist.append(item.clone( channel='helper', action='show_servers_list', title= ' - [COLOR darkorange][B]Todos[/B][/COLOR] los Servidores', tipo = 'all', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( channel='helper', action='show_servers_list', title= ' - Qué servidores están [COLOR darkorange][B]Disponibles[/B][/COLOR] (Activos)', tipo = 'activos', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( channel='helper', action='show_servers_list_out_service', title= '    - Qué servidores están [COLOR goldenrod][B]Sin Servicio[/B][/COLOR]', thumbnail=config.get_thumb('bolt') ))
    itemlist.append(item.clone( channel='helper', action='show_servers_list_inactives', title= '    - Qué servidores están [COLOR coral][B]Inactivos[/B][/COLOR]', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( channel='helper', action='show_channels_list', title= '    - Qué canales tienen [COLOR orchid][B]Solo un servidor[/B][/COLOR]', onlyone = True, thumbnail=config.get_thumb('stack') ))

    return itemlist


def submnu_developers(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]DEVELOPERS:[/B]', text_color='firebrick' ))

    itemlist.append(item.clone( channel='helper', action='show_help_notice', title= '[COLOR aqua][B]Comunicado[/B][/COLOR] Oficial de Balandro', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( channel='helper', action='show_dev_notes', title= 'Notas para Developers (desarrolladores)', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( action='copy_dev', title= 'Obtener una Copia del fichero dev-notes.txt', thumbnail=config.get_thumb('folder'), text_color='yellowgreen' ))

    itemlist.append(item.clone( action='', title= '[COLOR firebrick][B][I]DEVELOPERS FUENTES:[/I][/B][/COLOR]', folder=False ))

    itemlist.append(item.clone( action='', title= ' - Fuentes [COLOR darkorange][B]https://github.com/repobal[/B][/COLOR]', thumbnail=config.get_thumb('addon'), folder=False ))

    itemlist.append(item.clone( action='', title= '[COLOR firebrick][B][I]Developers Telegram:[/I][/B][/COLOR]', folder=False ))

    itemlist.append(item.clone( action='', title= ' - Team ' + _team + ' Equipo de Desarrollo', folder=False, thumbnail=config.get_thumb('telegram') ))

    itemlist.append(item.clone( action='', title= '[COLOR firebrick][B][I]DEVELOPERS INCORPORACIONES:[/B][/I][/COLOR]', folder=False ))

    itemlist.append(item.clone( action='', title='[COLOR yellow][B][I]  Solicitudes solo con Enlace de Invitación[/I][/B][/COLOR]', folder=False, thumbnail=config.get_thumb('pencil') ))

    itemlist.append(item.clone( action='', title= '  Foro ' + _foro, thumbnail=config.get_thumb('foro'), folder=False ))
    itemlist.append(item.clone( action='', title= '  Telegram ' + _telegram, thumbnail=config.get_thumb('telegram'), folder=False ))

    return itemlist


def copy_dev(item):
    logger.info()

    file = os.path.join(config.get_runtime_path(), 'dev-notes.txt')

    existe = filetools.exists(file)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No se localiza el fichero dev-notes.txt[/COLOR][/B]' % color_alert)
        return

    destino_path = xbmcgui.Dialog().browseSingle(3, 'Seleccionar carpeta dónde copiar', 'files', '', False, False, '')
    if not destino_path: return

    origen = os.path.join(file)
    destino = filetools.join(destino_path, 'dev-notes.txt')

    if not filetools.copy(origen, destino, silent=False):
        platformtools.dialog_ok(config.__addon_name, 'Error, no se ha podido copiar el fichero dev-notes.txt!', origen, destino)
        return

    platformtools.dialog_notification('Fichero copiado', 'dev-notes.txt')


def test_providers(item):
    logger.info()

    proxies_actuales = config.get_setting('proxies', 'test_providers', default='').strip()

    config.set_setting('channel_test_providers_dominio', '')
    config.set_setting('proxies', '', 'test_providers')

    default_provider = 'proxyscrape.com'
    all_providers = 'All-providers'
    private_list = 'Lista-proxies.txt'

    proxies_extended = config.get_setting('proxies_extended', default=False)
    proxies_list = config.get_setting('proxies_list', default=False)

    opciones_provider = [
            'spys.one',
            'hidemy.name',
            'httptunnel.ge',
            'proxynova.com',
            'free-proxy-list',
            'spys.me',
            default_provider,
            'proxyservers.pro',
            'us-proxy.org',
            'proxy-list.download',
            all_providers,
            'proxysource.org',
            'silverproxy.xyz',
            'dailyproxylists.com',
            'sslproxies.org',
            'clarketm',
            'google-proxy.net',
            'ip-adress.com',
            'proxydb.net',
            'hidester.com',
            'geonode.com',
            'mmpx12',
            'roosterkid',
            'almroot',
            'shiftytr',
            'mertguvencli',
            private_list
            ]

    if proxies_extended:
        opciones_provider.append('z-coderduck')
        opciones_provider.append('z-echolink')
        opciones_provider.append('z-free-proxy-list.anon')
        opciones_provider.append('z-free-proxy-list.com')
        opciones_provider.append('z-free-proxy-list.uk')
        opciones_provider.append('z-github')
        opciones_provider.append('z-opsxcq')
        opciones_provider.append('z-proxy-daily')
        opciones_provider.append('z-proxy-list.org')
        opciones_provider.append('z-proxyhub')
        opciones_provider.append('z-proxyranker')
        opciones_provider.append('z-xroxy')
        opciones_provider.append('z-socks')
        opciones_provider.append('z-squidproxyserver')

    if not proxies_list: opciones_provider.remove(private_list)

    preselect = 0
    opciones_provider = sorted(opciones_provider, key=lambda x: x[0])
    ret = platformtools.dialog_select('Proveedores de proxies', opciones_provider, preselect=preselect)
    if ret == -1: return

    provider = opciones_provider[ret]

    domain = 'https://'

    domain = platformtools.dialog_input(default=domain, heading='Indicar Dominio a Testear  -->  [COLOR %s]https://??????[/COLOR]' % color_avis)

    if domain is None: domain = ''
    elif domain == 'https://': domain = ''

    if domain:
       if domain.startswith('//'): domain = 'https:' + domain
       elif not domain.startswith('https://'): domain = 'https:' + domain
    else: domain = 'https://www.youtube.com/'

    from core import proxytools

    procesar = False
    if provider == all_providers: procesar = True

    proxies = proxytools._buscar_proxies('test_providers', domain, provider, procesar)

    proxies_encontrados = config.get_setting('proxies', 'test_providers', default='').strip()

    config.set_setting('proxies', '', 'test_providers')

    if proxies:
        if proxies_encontrados: return
        else:
           platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin Proxies localizados[/COLOR][/B]' % color_exec)
           return

    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B] Test_Providers[/B][/COLOR]', '[COLOR yellowgreen][B]¿ Desea efectuar el Test del Resultado ?[/B][/COLOR]'):
        from modules import tester

        config.set_setting('channel_test_providers_dominio', domain)

        try: tester.test_channel('test_providers')
        except: platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] Test_Providers[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Test Ignorado[/B][/COLOR]' % color_alert)

    else: platformtools.dialog_notification(config.__addon_name + ' ' + provider, '[B][COLOR %s]Comprobar Proveedor[/COLOR][/B]' % color_alert)

    config.set_setting('dominio', '', 'test_providers')
    config.set_setting('proxies', '', 'test_providers')


def test_tplus(item):
    logger.info()

    tplus_actual = config.get_setting('proxies_tplus', default='32')

    if config.get_setting('proxies_tplus_proces'): tplus_actual = config.get_setting('proxies_tplus_proces', default='32')

    opciones_tplus = [
            'Openproxy.space http',
            'Openproxy.space socks4',
            'Openproxy.space socks5',
            'Vpnoverview.com',
            'Proxydb.net http',
            'Proxydb.net https',
            'Proxydb.net socks4',
            'Proxydb.net socks5',
            'Netzwelt.de',
            'Proxy-list.download http',
            'Proxy-list.download https',
            'Proxy-list.download socks4',
            'Proxy-list.download socks5',
            'Freeproxy.world',
            'Freeproxy.world anonymity',
            'Hidemyna.me.en',
            'List.proxylistplus.com',
            'Proxyservers.pro',
            'TheSpeedX',
            'Proxyscan.io http',
            'Proxyscan.io all',
            'Proxyscan.io socks4',
            'Proxyscan.io socks5',
            'Openproxylist.xyz http',
            'Openproxylist.xyz socks4',
            'Openproxylist.xyz socks5',
            'Proxy-list.download v1 socks4',
            'Proxy-list.download v1 socks5',
            'Monosans',
            'Jetkai',
            'Sunny9577',
            'Proxy4parsing',
            'Hendrikbgr',
            'Rdavydov http',
            'Aslisk',
            'Rdavydov socks4',
            'Hookzof',
            'ManuGMG',
            'Rdavydov socks5',
            'Lamt3012',
            'Proxifly http',
            'Proxifly https',
            'Proxifly socks4',
            'Proxifly socks5',
            'ErcinDedeoglu http',
            'ErcinDedeoglu https',
            'ErcinDedeoglu socks4',
            'ErcinDedeoglu socks5',
            'Proxycompass',
            'Proxybros',
            'Proxyscrape all',
            'Proxyscrape anonymous',
            'Proxyscrape elite',
            'Proxyscrape transparent',
            'Proxyscrape https',
            'Markavale'
            ]

    preselect = tplus_actual

    opciones_tplus = sorted(opciones_tplus, key=lambda x: x[0])

    ret = platformtools.dialog_select('[COLOR cyan][B]Proveedores Proxies Tplus[/B][/COLOR]', opciones_tplus, preselect=preselect)
    if ret == -1: return -1

    if opciones_tplus[ret] == 'Openproxy.space http': proxies_tplus = '0'
    elif opciones_tplus[ret] == 'Openproxy.space socks4': proxies_tplus = '1'
    elif opciones_tplus[ret] == 'Openproxy.space socks5': proxies_tplus = '2'
    elif opciones_tplus[ret] == 'Vpnoverview.com': proxies_tplus = '3'
    elif opciones_tplus[ret] == 'Proxydb.net http': proxies_tplus = '4'
    elif opciones_tplus[ret] == 'Proxydb.net https': proxies_tplus = '5'
    elif opciones_tplus[ret] == 'Proxydb.net socks4': proxies_tplus = '6'
    elif opciones_tplus[ret] == 'Proxydb.net socks5': proxies_tplus = '7'
    elif opciones_tplus[ret] == 'Netzwelt.de': proxies_tplus = '8'
    elif opciones_tplus[ret] == 'Proxy-list.download http': proxies_tplus = '9'
    elif opciones_tplus[ret] == 'Proxy-list.download https': proxies_tplus = '10'
    elif opciones_tplus[ret] == 'Proxy-list.download socks4': proxies_tplus = '11'
    elif opciones_tplus[ret] == 'Proxy-list.download socks5': proxies_tplus = '12'
    elif opciones_tplus[ret] == 'Freeproxy.world': proxies_tplus = '13'
    elif opciones_tplus[ret] == 'Freeproxy.world anonymity': proxies_tplus = '14'
    elif opciones_tplus[ret] == 'Hidemyna.me.en': proxies_tplus = '15'
    elif opciones_tplus[ret] == 'List.proxylistplus.com': proxies_tplus = '16'
    elif opciones_tplus[ret] == 'Proxyservers.pro': proxies_tplus = '17'
    elif opciones_tplus[ret] == 'TheSpeedX': proxies_tplus = '18'
    elif opciones_tplus[ret] == 'Proxyscan.io http': proxies_tplus = '19'
    elif opciones_tplus[ret] == 'Proxyscan.io all': proxies_tplus = '20'
    elif opciones_tplus[ret] == 'Openproxylist.xyz http': proxies_tplus = '21'
    elif opciones_tplus[ret] == 'Openproxylist.xyz socks4': proxies_tplus = '22'
    elif opciones_tplus[ret] == 'Openproxylist.xyz socks5': proxies_tplus = '23'
    elif opciones_tplus[ret] == 'Proxy-list.download v1 socks4': proxies_tplus = '24'
    elif opciones_tplus[ret] == 'Proxy-list.download v1 socks5': proxies_tplus = '25'
    elif opciones_tplus[ret] == 'Monosans': proxies_tplus = '26'
    elif opciones_tplus[ret] == 'Jetkai': proxies_tplus = '27'
    elif opciones_tplus[ret] == 'Sunny9577': proxies_tplus = '28'
    elif opciones_tplus[ret] == 'Proxy4parsing': proxies_tplus = '29'
    elif opciones_tplus[ret] == 'Hendrikbgr': proxies_tplus = '30'
    elif opciones_tplus[ret] == 'Rdavydov http': proxies_tplus = '31'
    elif opciones_tplus[ret] == 'Aslisk': proxies_tplus = '32'
    elif opciones_tplus[ret] == 'Rdavydov socks4': proxies_tplus = '33'
    elif opciones_tplus[ret] == 'Hookzof': proxies_tplus = '34'
    elif opciones_tplus[ret] == 'ManuGMG': proxies_tplus = '35'
    elif opciones_tplus[ret] == 'Rdavydov socks5': proxies_tplus = '36'
    elif opciones_tplus[ret] == 'Lamt3012': proxies_tplus = '37'
    elif opciones_tplus[ret] == 'Proxifly http': proxies_tplus = '38'
    elif opciones_tplus[ret] == 'Proxifly https': proxies_tplus = '45'
    elif opciones_tplus[ret] == 'Proxifly socks4': proxies_tplus = '39'
    elif opciones_tplus[ret] == 'Proxifly socks5': proxies_tplus = '40'
    elif opciones_tplus[ret] == 'ErcinDedeoglu http': proxies_tplus = '41'
    elif opciones_tplus[ret] == 'ErcinDedeoglu https': proxies_tplus = '42'
    elif opciones_tplus[ret] == 'ErcinDedeoglu socks4': proxies_tplus = '43'
    elif opciones_tplus[ret] == 'ErcinDedeoglu socks5': proxies_tplus = '44'
    elif opciones_tplus[ret] == 'Proxycompass': proxies_tplus = '46'
    elif opciones_tplus[ret] == 'Proxybros': proxies_tplus = '47'
    elif opciones_tplus[ret] == 'Proxyscrape all': proxies_tplus = '48'
    elif opciones_tplus[ret] == 'Proxyscrape anonymous': proxies_tplus = '49'
    elif opciones_tplus[ret] == 'Proxyscrape elite': proxies_tplus = '50'
    elif opciones_tplus[ret] == 'Proxyscrape transparent': proxies_tplus = '51'
    elif opciones_tplus[ret] == 'Proxyscrape https': proxies_tplus = '52'
    elif opciones_tplus[ret] == 'Markavale': proxies_tplus = '53'
    elif opciones_tplus[ret] == 'Proxyscan.io socks4': proxies_tplus = '54'
    elif opciones_tplus[ret] == 'Proxyscan.io socks5': proxies_tplus = '55'

    else: proxies_tplus = '32'

    config.set_setting('proxies_tplus', proxies_tplus)
    config.set_setting('proxies_tplus_proces', '')

    return proxies_tplus


def test_alfabetico(item):
    logger.info()
    itemlist = []

    if 'canal' in item.title:
        text_color = 'gold'
        accion = 'test_all_webs'
    else:
        text_color = 'fuchsia'
        accion = 'test_all_srvs'

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        itemlist.append(item.clone( title = letra, action = accion, letra = letra.lower(), text_color = text_color  ))

    return itemlist


def test_all_webs(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    config.set_setting('user_test_channel', '')

    if not item.letra:
        if item.unsatisfactory: text = '¿ Iniciar Test Web de los Posibles Canales [B][COLOR gold]Insatisfactorios[/B][/COLOR] ?'
        else: text = '¿ Iniciar Test Web de [B][COLOR gold]TODOS[/B][/COLOR] los Canales ?'

        if not platformtools.dialog_yesno(config.__addon_name, text): return

    if item.unsatisfactory: config.set_setting('developer_test_channels', 'unsatisfactory')

    from core import channeltools

    from modules import tester

    filtros = {}

    channels_list_status = config.get_setting('channels_list_status', default=0)
    if channels_list_status > 0:
        filtros['status'] = 0 if channels_list_status == 1 else 1

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0

    for ch in ch_list:
        if config.get_setting('mnu_simple', default=False):
            if 'enlaces torrent exclusivamente' in ch['notes'].lower(): continue
            elif 'exclusivamente al dorama' in ch['notes'].lower(): continue
            elif 'exclusivamente al anime' in ch['notes'].lower(): continue
            elif '+18' in ch['notes']: continue
        else:
            if not config.get_setting('mnu_torrents', default=False) or config.get_setting('search_no_exclusively_torrents', default=False):
                if 'enlaces torrent exclusivamente' in ch['notes'].lower(): continue

            if not config.get_setting('mnu_doramas', default=True):
                if 'exclusivamente al dorama' in ch['notes'].lower(): continue

            if not config.get_setting('mnu_animes', default=True):
                if 'exclusivamente al anime' in ch['notes'].lower(): continue

            if not config.get_setting('mnu_adultos', default=True):
                if '+18' in ch['notes']: continue

        i += 1

        try:
            if item.letra:
                el_canal = ch['id']

                if el_canal[0] < item.letra:
                    i = i - 1
                    continue

            txt = tester.test_channel(ch['name'])
        except:
            if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[B][COLOR red]Error en la comprobación.[/B][/COLOR]', '[COLOR yellowgreen][B]¿ Desea comprobar el Canal de nuevo ?[/B][/COLOR]'):
                try: txt = tester.test_channel(ch['name'])
                except:
                     platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                     tests_all_webs.append(ch['name'])
                     continue
            else:
                tests_all_webs.append(ch['name'])
                continue

        rememorize = False

        if not txt: continue

        if 'code: [COLOR springgreen][B]200' in str(txt):
            if 'invalid:' in str(txt):
                platformtools.dialog_textviewer(ch['name'], txt)

                if ' con proxies ' in str(txt):
                    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]¿ Desea Iniciar una nueva Búsqueda de Proxies en el Canal ?[/B][/COLOR]'):
                        _proxies(item, ch['id'])

                        try: txt = tester.test_channel(ch['name'])
                        except:
                             platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                             tests_all_webs.append(ch['name'])
                             continue

                        if not 'code: [COLOR springgreen][B]200' in str(txt):
                            if ' con proxies ' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                                tests_all_webs.append(ch['name'])
                        else:
                            rememorize = True

                elif 'Sin proxies' in str(txt):
                    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR chartreuse][B]Quizás necesite Proxies.[/B][/COLOR] ¿ Desea Iniciar la Búsqueda de Proxies en el Canal ?'):
                        _proxies(item, ch['id'])

                        try: txt = tester.test_channel(ch['name'])
                        except:
                             platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                             tests_all_webs.append(ch['name'])
                             continue

                        if not 'code: [COLOR springgreen][B]200' in str(txt):
                            if 'Sin proxies' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                                tests_all_webs.append(ch['name'])
                        else:
                            rememorize = True

                if 'invalid:' in str(txt):
                    if not 'Suspendida' in str(txt):
                        if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '¿ Desea comprobar el Canal de nuevo, [COLOR red][B]por Acceso sin Host Válido en los datos. [/B][/COLOR]?'):
                            try: txt = tester.test_channel(ch['name'])
                            except:
                                 platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                                 tests_all_webs.append(ch['name'])
                                 continue

                            if 'code: [COLOR springgreen][B]200' in str(txt):
                                if 'invalid:' in str(txt):
                                    platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado el Acceso sin Host Válido en los datos.[/B][/COLOR]')
                                    tests_all_webs.append(ch['name'])

            elif 'Falso Positivo.' in str(txt):
                platformtools.dialog_textviewer(ch['name'], txt)

                if ' con proxies ' in str(txt):
                    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]¿ Desea Iniciar una nueva Búsqueda de Proxies en el Canal ?[/B][/COLOR]'):
                        _proxies(item, ch['id'])

                        try: txt = tester.test_channel(ch['name'])
                        except:
                              platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                              tests_all_webs.append(ch['name'])
                              continue

                        if not 'code: [COLOR springgreen][B]200' in str(txt):
                            if ' con proxies ' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                                tests_all_webs.append(ch['name'])
                        else:
                            rememorize = True

                elif 'Sin proxies' in str(txt):
                    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR chartreuse][B]Quizás necesite Proxies.[/B][/COLOR] ¿ Desea Iniciar la Búsqueda de Proxies en el Canal ?'):
                        _proxies(item, ch['id'])

                        try: txt = tester.test_channel(ch['name'])
                        except:
                             platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                             tests_all_webs.append(ch['name'])
                             continue

                        if not 'code: [COLOR springgreen][B]200' in str(txt):
                            if 'Sin proxies' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                                tests_all_webs.append(ch['name'])
                        else:
                            rememorize = True

                if 'Falso Positivo.' in str(txt):
                    if txt_status:
                        if con_incidencias:
                            host_incid = ch['name']

                            if host_incid in str(con_incidencias):
                                incidencia = ''

                                incids = scrapertools.find_multiple_matches(str(con_incidencias), '[COLOR moccasin](.*?)[/B][/COLOR]')

                                for incid in incids:
                                    if not ' ' + host_incid + ' ' in str(incid): continue

                                    incidencia = incid
                                    break

                                if incidencia:
                                    tests_all_webs.append(ch['name'])
                                    continue

                        if no_accesibles:
                            host_incid = ch['name']

                            if host_incid in str(no_accesibles):
                                incidencia = ''

                                incids = scrapertools.find_multiple_matches(str(no_accesibles), '[COLOR moccasin](.*?)[/B][/COLOR]')

                                for incid in incids:
                                    if not ' ' + host_incid + ' ' in str(incid): continue

                                    incidencia = incid
                                    break

                                if incidencia:
                                    tests_all_webs.append(ch['name'])
                                    continue

                    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '¿ Desea comprobar el Canal de nuevo, [COLOR red][B]por Falso Positivo. [/B][/COLOR]?'):
                        try: txt = tester.test_channel(ch['name'])
                        except:
                             platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                             tests_all_webs.append(ch['name'])
                             continue

                        if 'code: [COLOR springgreen][B]200' in str(txt):
                            if 'Falso Positivo.' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado el Falso Positivo.[/B][/COLOR]')
                                tests_all_webs.append(ch['name'])

            if ' al parecer No se necesitan' in str(txt):
                if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]¿ Desea Quitar los Proxies del Canal ?[/B][/COLOR], porqué parece que NO se necesitan.'):
                    _quitar_proxies(item, ch['id'])

                    try: txt = tester.test_channel(ch['name'])
                    except:
                         platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                         tests_all_webs.append(ch['name'])
                         continue

                    proxies = config.get_setting('proxies', ch['id'], default='').strip()

                    if not proxies:
                        if config.get_setting('memorize_channels_proxies', default=True):
                            channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')

                            el_memorizado = "'" + ch['id'] + "'"

                            if el_memorizado in str(channels_proxies_memorized):
                                channels_proxies_memorized = str(channels_proxies_memorized).replace(el_memorizado + ',', '').replace(el_memorizado, '').strip()
                                config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

        else:
           if 'code: [COLOR [COLOR orangered][B]301' in str(txt) or 'code: [COLOR [COLOR orangered][B]308' in str(txt):
               tests_all_webs.append(ch['name'])
               continue

           if 'code: [COLOR [COLOR orangered][B]302' in str(txt) or 'code: [COLOR [COLOR orangered][B]307' in str(txt):
               tests_all_webs.append(ch['name'])
               continue

           if 'Podría estar Correcto' in str(txt):
               tests_all_webs.append(ch['name'])
               continue

           if txt_status:
               if con_incidencias:
                   host_incid = ch['name']

                   if host_incid in str(con_incidencias):
                       incidencia = ''

                       incids = scrapertools.find_multiple_matches(str(con_incidencias), '[COLOR moccasin](.*?)[/B][/COLOR]')

                       for incid in incids:
                           if not ' ' + host_incid + ' ' in str(incid): continue

                           incidencia = incid
                           break

                       if incidencia:
                           tests_all_webs.append(ch['name'])
                           continue

               if no_accesibles:
                   host_incid = ch['name']

                   if host_incid in str(no_accesibles):
                       incidencia = ''

                       incids = scrapertools.find_multiple_matches(str(no_accesibles), '[COLOR moccasin](.*?)[/B][/COLOR]')

                       for incid in incids:
                            if not ' ' + host_incid + ' ' in str(incid): continue

                            incidencia = incid
                            break

                       if incidencia:
                           tests_all_webs.append(ch['name'])
                           continue

           if not 'nuevo:' in txt:
               if ' con proxies ' in str(txt):
                   if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]¿ Desea Iniciar una nueva Búsqueda de Proxies en el Canal ?[/B][/COLOR]'):
                       _proxies(item, ch['id'])

                       try: txt = tester.test_channel(ch['name'])
                       except:
                            platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                            tests_all_webs.append(ch['name'])
                            continue

                       if not 'code: [COLOR springgreen][B]200' in str(txt):
                           if ' con proxies ' in str(txt):
                               platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                               tests_all_webs.append(ch['name'])
                       else:
                           rememorize = True

               elif 'Sin proxies' in str(txt):
                   if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR chartreuse][B]Quizás necesite Proxies.[/B][/COLOR] ¿ Desea Iniciar la Búsqueda de Proxies en el Canal ?'):
                       _proxies(item, ch['id'])

                       try: txt = tester.test_channel(ch['name'])
                       except:
                            platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                            tests_all_webs.append(ch['name'])
                            continue

                       if not 'code: [COLOR springgreen][B]200' in str(txt):
                           if 'Sin proxies' in str(txt):
                               platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                               tests_all_webs.append(ch['name'])
                       else:
                           rememorize = True

               else:
                   tests_all_webs.append(ch['name'])

        if rememorize:
            proxies = config.get_setting('proxies', ch['id'], default='').strip()

            if proxies:
                if config.get_setting('memorize_channels_proxies', default=True):
                    channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')

                    el_memorizado = "'" + ch['id'] + "'"

                    if not el_memorizado in str(channels_proxies_memorized):
                        channels_proxies_memorized = channels_proxies_memorized + ', ' + el_memorizado
                        config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

    if i > 0:
        if not tests_all_webs:
            platformtools.dialog_ok(config.__addon_name, 'Canales Testeados ' + str(i))
        else:
            if not config.get_setting('developer_mode', default=False):
                platformtools.dialog_ok(config.__addon_name, 'Canales Testeados ' + str(i))
            else:
                if platformtools.dialog_yesno(config.__addon_name, 'Canales Testeados ' + str(i), '[B][COLOR red]Hay Conflictos. [COLOR yellow]Desea Verlos ?[/B][/COLOR]'):
                    txt_conflict = ''

                    for conflict in tests_all_webs:
                        txt_conflict += conflict + '[CR]'

                    platformtools.dialog_textviewer('Canales con Conflictos', txt_conflict)

    config.set_setting('developer_test_channels', '')

    config.set_setting('user_test_channel', '')


def test_one_channel(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    config.set_setting('user_test_channel', '')

    try:
        filters.show_channels_list(item)
    except:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR red]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]')


def _proxies(item, channel):
    item.from_channel = channel

    from modules import submnuctext
    submnuctext._proxies(item)
    return True


def _quitar_proxies(item, channel):
    item.from_channel = channel

    config.set_setting('proxies', '', item.from_channel)


def test_all_srvs(item):
    logger.info()

    config.set_setting('developer_test_servers', '')

    if not item.letra:
        if item.unsatisfactory: text = '¿ Iniciar Test Web de los Posibles Servidores [B][COLOR fuchsia]Insatisfactorios[/B][/COLOR] ?'
        else: text = '¿ Iniciar Test Web de [B][COLOR fuchsia]TODOS[/B][/COLOR] los Servidores ?'

        if not platformtools.dialog_yesno(config.__addon_name, text): return

    if item.unsatisfactory: config.set_setting('developer_test_servers', 'unsatisfactory')

    from core import jsontools

    from modules import tester

    path = os.path.join(config.get_runtime_path(), 'servers')

    servidores = os.listdir(path)
    servidores = sorted(servidores)

    i = 0

    for server in servidores:
        if not server.endswith('.json'): continue

        path_server = os.path.join(config.get_runtime_path(), 'servers', server)

        if not os.path.isfile(path_server): continue

        data = filetools.read(path_server)
        dict_server = jsontools.load(data)

        if dict_server['active'] == False: continue

        try:
           notes = dict_server['notes']
        except: 
           notes = ''

        if "out of service" in notes.lower():
            if item.unsatisfactory: continue

        el_servidor = dict_server['name']
        el_servidor = el_servidor.lower()

        if el_servidor == 'various' or el_servidor == 'waaw' or el_servidor == 'zures':
            if item.unsatisfactory: continue

        i += 1

        txt = ''

        try:
            if item.letra:
                el_servidor = dict_server['name']
                el_servidor = el_servidor.lower()

                if el_servidor[0] < item.letra:
                    i = i - 1
                    continue

            txt = tester.test_server(dict_server['name'])
        except:
            if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + dict_server['name'] + '[/B][/COLOR]', '[B][COLOR red]Error en la comprobación.[/B][/COLOR]', '[COLOR yellowgreen][B]¿ Desea comprobar el Servidor de nuevo ?[/B][/COLOR]'):
                try: txt = tester.test_server(dict_server['name'])
                except:
                     platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B]' + dict_server['name'] + '[/B][/COLOR]', '[B][COLOR %s]Error comprobación, Servidor ignorado[/B][/COLOR]' % color_alert)
                     tests_all_srvs.append(dict_server['name'])
                     continue
            else:
                tests_all_srvs.append(dict_server['name'])
                continue

        if txt_status:
            if srv_pending:
                srv_incid = dict_server['name']

                if srv_incid in str(srv_pending):
                    incidencia = ''

                    incids = scrapertools.find_multiple_matches(str(srv_pending), '[COLOR orchid](.*?)[/B][/COLOR]')

                    for incid in incids:
                         if not ' ' + srv_incid + ' ' in str(incid): continue

                         incidencia = incid
                         break

                    if incidencia:
                        tests_all_srvs.append(dict_server['name'])
                        continue

        if not txt: continue

        if not 'code: [COLOR springgreen][B]200' in str(txt):
            tests_all_srvs.append(dict_server['name'])

    if i > 0:
        if not tests_all_srvs:
            platformtools.dialog_ok(config.__addon_name, 'Servidores Testeados ' + str(i))
        else:
            if not config.get_setting('developer_mode', default=False):
                platformtools.dialog_ok(config.__addon_name, 'Servidores Testeados ' + str(i))
            else:
                if platformtools.dialog_yesno(config.__addon_name, 'Servidores Testeados ' + str(i), '[B][COLOR red]Hay Conflictos. [COLOR yellow]Desea Verlos ?[/B][/COLOR]'):
                    txt_conflict = ''

                    for conflict in tests_all_srvs:
                        txt_conflict += conflict + '[CR]'

                    platformtools.dialog_textviewer('Servidores con Conflictos', txt_conflict)

    config.set_setting('developer_test_servers', '')


def test_one_server(item):
    logger.info()

    config.set_setting('developer_test_servers', '')

    if not item.tipo: item.tipo = 'activos'

    try:
        filters.show_servers_list(item)
    except:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR red]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]')


def show_addons(item):
    logger.info()

    txt = '[COLOR gold][B]' + item.tipo + ':[/B][/COLOR][CR]'

    for addons in item.addons:
        txt += '  ' + str(addons) + '[CR][CR]'

    titulo = 'Información Add-ons '
    if item.tipo == 'Caché': titulo = 'Información Archivos '

    platformtools.dialog_textviewer(titulo + item.tipo , txt)


def show_help_addons(item):
    logger.info()

    txt = ''

    cliente_torrent = config.get_setting('cliente_torrent', default='Seleccionar')

    if cliente_torrent == 'Seleccionar' or cliente_torrent == 'Ninguno': tex_tor = cliente_torrent
    else:
       tex_tor = cliente_torrent
       cliente_torrent = 'plugin.video.' + cliente_torrent.lower()
       if xbmc.getCondVisibility('System.HasAddon("%s")' % cliente_torrent):
           cod_version = xbmcaddon.Addon(cliente_torrent).getAddonInfo("version").strip()
           tex_tor += '  [COLOR goldenrod]' + cod_version + '[/COLOR]'

    txt += ' - Cliente/Motor Torrent ' + '[COLOR fuchsia][B] ' + tex_tor + '[/B][/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("script.elementum.burst")'):
        cod_version = xbmcaddon.Addon("script.elementum.burst").getAddonInfo("version").strip()
        tex_tor = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_tor = '  [COLOR red]No instalado[/COLOR]'

    txt += ' - [COLOR fuchsia][B]Elementum Burst[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_tor + '[/B][/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("inputstream.adaptive")'):
        cod_version = xbmcaddon.Addon("inputstream.adaptive").getAddonInfo("version").strip()
        tex_ia = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_ia = '  [COLOR red]No instalado[/COLOR]'

    txt += ' - [COLOR fuchsia][B]InputStream Adaptive[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_ia + '[/B][/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
        cod_version = xbmcaddon.Addon("plugin.video.youtube").getAddonInfo("version").strip()
        tex_yt = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_yt = '  [COLOR red]No instalado[/COLOR]'

    txt += ' - [COLOR fuchsia][B]Youtube[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_yt + '[/B][/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        cod_version = xbmcaddon.Addon("script.module.resolveurl").getAddonInfo("version").strip()
        tex_mr = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_mr = '  [COLOR red]No instalado[/COLOR]'

    txt += ' - [COLOR fuchsia][B]ResolveUrl[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_mr + '[/B][/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("repository.resolveurl")'):
        cod_version = xbmcaddon.Addon("repository.resolveurl").getAddonInfo("version").strip()
        tex_rp = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_rp = '  [COLOR red]No instalado[/COLOR]'

    txt += ' - [COLOR gold][B]Repository ResolveUrl[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_rp + '[/B][/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("repository.elementum")'):
        cod_version = xbmcaddon.Addon("repository.elementum").getAddonInfo("version").strip()
        tex_rp = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_rp = '  [COLOR red]No instalado[/COLOR]'

    txt += ' - [COLOR gold][B]Repository Elementum[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_rp + '[/B][/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("repository.elementumorg")'):
        cod_version = xbmcaddon.Addon("repository.elementumorg").getAddonInfo("version").strip()
        tex_rp = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_rp = '  [COLOR red]No instalado[/COLOR]'

    txt += ' - [COLOR gold][B]Repository ElementumOrg[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_rp + '[/B][/COLOR][CR]'

    platformtools.dialog_textviewer('Información Add-Ons Extternos', txt)


def show_sistema(item):
    logger.info()

    txt = '[COLOR goldenrod][B]PREFERENCIAS SISTEMA:[/B][/COLOR][CR]'

    txt += ' - Comprobar existencia Balandro Repo: '

    if config.get_setting('check_repo', default=True): txt += '[COLOR yellow][B] Activado[/B][/COLOR][CR]'
    else: txt += '[COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    txt += ' - Comprobar Fixes al Iniciar su Media Center: '

    if config.get_setting('addon_update_atstart', default=True): txt += '[COLOR yellow][B]Activado[/B][/COLOR][CR]'
    else: txt += '[COLOR red][B]Des-Activado[/B][/COLOR][CR]'

    txt += ' - Eliminar su fichero de Cookies al Iniciar su Media Center: '

    if config.get_setting('erase_cookies', default=False): txt += '[COLOR yellow][B] Activado[/B][/COLOR][CR]'
    else: txt += '[COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    txt += ' - Obtener y Usar la versión más Reciente/Estable de Chrome/Chromium: '

    if config.get_setting('ver_stable_chrome', default=True): txt += '[COLOR yellow][B] Activado[/B][/COLOR][CR]'
    else: txt += '[COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    if config.get_setting('chrome_last_version', default=''): txt += '[CR][COLOR yellow][B] - Versión Chrome/Chromium: [/COLOR][COLOR cyan]' + config.get_setting('chrome_last_version') + ' [/B][/COLOR][CR]'

    if config.get_setting('httptools_timeout', default='15'): txt += '[CR][COLOR yellow][B] - Timeout [/B](tiempo máximo de espera en los Accesos, por defecto 15)[B]: [/COLOR][COLOR cyan]' + str(config.get_setting('httptools_timeout')) + ' [/B][/COLOR][CR]'

    txt += '[CR] - Confirmar con el Botón pulsar [OK] en ciertas Notificaciones: '

    if config.get_setting('notification_d_ok', default=False): txt += '[COLOR yellow][B] Activado[/B][/COLOR][CR]'
    else: txt += '[COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    txt += ' - Emitir un Sonido al mostrar Avisos/Notificaciones: '

    if config.get_setting('notification_beep', default=False): txt += '[COLOR yellow][B] Activado[/B][/COLOR][CR]'
    else: txt += '[COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    if config.get_setting('channels_repeat', default='30'): txt += '[CR][COLOR yellow][B] - Tiempo de espera en los Reintentos [/B](en el acceso a ciertos Canales, por defecto 30)[B]: [/COLOR][COLOR cyan]' + str(config.get_setting('channels_repeat')) + ' [/B][/COLOR][CR]'

    if config.get_setting('servers_waiting', default='6'): txt += '[CR][COLOR yellow][B] - Tiempo de espera [/B](en el acceso a ciertos Servidores, por defecto 6)[B]: [/COLOR][COLOR cyan]' + str(config.get_setting('servers_waiting')) + ' [/B][/COLOR][CR]'

    txt += '[CR][COLOR goldenrod][B]PREFERENCIAS NOTIFICACIONES CANALES:[/B][/COLOR][CR]'

    txt += ' - Notificar los Re-Intentos de acceso en los Canales: '

    if config.get_setting('channels_re_charges', default=True): txt += '[COLOR yellow][B] Activado[/B][/COLOR][CR]'
    else: txt += '[COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    txt += ' - Presentar Sin Notificar Todas las Películas en las Listas Especiales: '

    if config.get_setting('channels_charges_movies', default=True): txt += '[COLOR yellow][B] Activado[/B][/COLOR][CR]'
    else: txt += '[COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    txt += ' - Notificar cuando No existan Temporadas ó tan solo haya Una: '

    if config.get_setting('channels_seasons', default=True): txt += '[COLOR yellow][B] Activado[/B][/COLOR][CR]'
    else: txt += '[COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    txt += ' - Presentar Sin Notificar Todos los Episodios en cada Temporada: '

    if config.get_setting('channels_charges', default=True): txt += '[COLOR yellow][B] Activado[/B][/COLOR][CR]'
    else: txt += '[COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    txt += '[CR][COLOR goldenrod][B]DEPURACIÓN:[/B][/COLOR][CR]'

    loglevel = config.get_setting('debug', 0)
    if loglevel == 0: tex_niv = 'Solo Errores'
    elif loglevel == 1: tex_niv = 'Errores e Información'
    else: tex_niv = 'Máxima Información'

    txt += '[COLOR yellow][B] - Nivel de información del fichero [COLOR aqua][B]LOG[/B][/COLOR] (por defecto Error): [COLOR cyan][B]' + tex_niv + ' [/B][/COLOR][CR]'

    platformtools.dialog_textviewer('Información Ajustes del Sistema', txt)


def balandro_log(item):
    logger.info()

    txt_errors = ''
    errors = False
    hay_errors = False

    loglevel = config.get_setting('debug', 0)
    if not loglevel >= 2:
        if not platformtools.dialog_yesno(config.__addon_name, 'El nivel actual de información del fichero LOG de su Media Center NO esta Ajustado al máximo. ¿ Desea no obstante visualizarlo ?'): 
            return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR cyan][B]¿ Desea localizar los [COLOR red]Errores[COLOR cyan] de ejecución ?[/B][/COLOR]'): 
        errors = True

    path = translatePath(os.path.join('special://logpath/', ''))

    file_log = 'kodi.log'

    file = path + file_log

    existe = filetools.exists(file)

    if existe == False:
        files = filetools.listdir(path)
        for file_log in files:
            if file_log.endswith('.log') == True or file_log.endswith('.LOG') == True:
                file = path + file_log
                existe = filetools.exists(file)
                break

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No se localiza su fichero Log[/COLOR][/B]' % color_alert)
        platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]Media Center NO Oficial[/B][/COLOR]', '[COLOR red][B]No se ha localizado su fichero Log[/B][/COLOR]', '[COLOR yellowgreen][B]Localize su fichero Log, mediante un navegador de archivos en su Media Center.[/B][/COLOR]')
        return

    size = filetools.getsize(file)
    if size > 999999: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Cargando fichero log[/COLOR][/B]' % color_infor)

    txt = ''

    try:
        for line in open(os.path.join(path, file_log), encoding="utf8").readlines():
            if errors:
                if '[Balandro] Traceback' in line: hay_errors = True

                if hay_errors:
                    if line.startswith(' '): txt_errors += '[B][COLOR yellow]' + line.strip() + '[/COLOR][/B][CR]'
                    else:
                       if not 'Balandro' in line: continue
                       txt_errors += '[B][COLOR cyan]' + line + '[/COLOR][/B][CR]'
            else:
                if 'Balandro' in line: txt += line
    except:
        for line in open(os.path.join(path, file_log)).readlines():
            if errors:
                if '[Balandro] Traceback' in line: hay_errors = True

                if hay_errors:
                    if line.startswith(' '): txt_errors += '[B][COLOR yellow]' + line.strip() + '[/COLOR][/B][CR]'
                    else:
                       if not 'Balandro' in line: continue
                       txt_errors += '[B][COLOR cyan]' + line + '[/COLOR][/B][CR]'
            else:
                if 'Balandro' in line: txt += line

    if errors:
       if not txt_errors:
           platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Fichero Log Sin Errores[/COLOR][/B]' % color_exec)
           return

       txt = txt_errors

    if txt: platformtools.dialog_textviewer('Fichero LOG (ejecución Balandro) de su Media Center', txt)


def resumen_canales(item):
    logger.info()

    from core import channeltools

    total = 0

    inactives = 0
    cerrados = 0
    anulados = 0
    temporarys = 0
    mismatcheds = 0
    inestables = 0
    problematics = 0
    clones = 0
    notices = 0
    proxies = 0
    registers = 0
    dominios = 0
    currents = 0
    onlyones = 0
    searchables = 0
    status_access = 0
    con_proxies = 0

    bus_pelisyseries = 0
    bus_pelis = 0
    bus_series = 0
    bus_documentaryes = 0
    bus_documentales = 0
    bus_infantiles = 0
    bus_kids = 0
    bus_torrents = 0
    bus_doramas = 0
    bus_animes = 0

    disponibles = 0
    suggesteds = 0
    peliculas = 0
    series = 0
    pelisyseries = 0
    generos = 40
    documentarys = 0
    infantiles = 0
    tales = 0
    bibles = 0
    torrents = 0
    doramas = 0
    animes = 0
    adults = 0
    privates = 0
    no_actives = 0

    filtros = {'active': False}
    ch_list = channeltools.get_channels_list(filtros=filtros)

    for ch in ch_list:
        total += 1

        if ch['active'] == False:
            if not 'temporary' in ch['clusters']: inactives += 1

            if 'Web CERRADA' in ch['notes']: cerrados += 1
            elif 'Web ANULADA' in ch['notes']: anulados += 1

        if 'temporary' in ch['clusters']: temporarys += 1

        if 'privates' in ch['clusters']:
            el_canal = ch['id']
            if os.path.exists(os.path.join(config.get_runtime_path(), 'channels', el_canal)): privates += 1

    filtros = {}
    ch_list = channeltools.get_channels_list(filtros=filtros)

    if ch_list:
        txt_ch = ''

        for ch in ch_list:
            if not ch['status'] == -1: continue
            no_actives += 1

    filtros = {'active': True}
    ch_list = channeltools.get_channels_list(filtros=filtros)

    for ch in ch_list:
        total += 1
        disponibles += 1

        if 'mismatched' in ch['clusters']: mismatcheds += 1
        if 'inestable' in ch['clusters']: inestables += 1
        if 'problematic' in ch['clusters']: problematics += 1
        if 'clone' in ch['clusters']: clones += 1
        if 'notice' in ch['clusters']: notices += 1
        if 'proxies' in ch['notes'].lower(): proxies += 1
        if 'register' in ch['clusters']: registers += 1
        if 'dominios' in ch['notes'].lower(): dominios += 1
        if 'current' in ch['clusters']: currents += 1
        if 'onlyone' in ch['clusters']: onlyones += 1
        if 'suggested' in ch['clusters']: suggesteds += 1

        if ch['searchable'] == False: searchables += 1

        tipos = ch['categories']

        if not 'tráilers' in ch['notes'].lower():
            if not '+18' in ch['notes']:

                if not 'exclusivamente al dorama' in ch['notes'].lower():
                    if not 'exclusivamente al anime' in ch['notes'].lower():
                        if 'movie' in tipos:
                            peliculas += 1
                            if ch['searchable']: bus_pelis += 1

                        if 'tvshow' in tipos:
                            if not 'animes, ovas, doramas y mangas' in ch['notes'].lower():
                               series += 1
                               if ch['searchable']: bus_series += 1

            if 'movie' in tipos:
                if 'tvshow' in tipos:
                    pelisyseries += 1
                    if ch['searchable']: bus_pelisyseries += 1

        if 'documentary' in tipos:
            documentarys += 1
            bus_documentaryes += 1
        else:
           if 'docs' in ch['clusters']:
               if ch['searchable']: bus_documentales += 1

        if 'infantil' in ch['clusters']: infantiles += 1
        else:
            if 'kids' in ch['clusters']:
               if ch['searchable']: bus_kids += 1

        if 'tales' in ch['clusters']: tales += 1

        if 'bibles' in ch['clusters']: bibles += 1

        if 'torrent' in tipos:
            torrents += 1
            bus_torrents += 1
        else:
           if 'torrents' in ch['clusters']:
               if ch['searchable']: bus_torrents += 1

        if 'exclusivamente al dorama' in ch['notes'].lower():
            doramas += 1
            bus_doramas += 1
        elif 'exclusivamente' in ch['notes'].lower():
            if 'doramas' in ch['notes'].lower():
                doramas += 1
                bus_doramas += 1
        else:
           if 'dorama' in ch['clusters']: bus_doramas += 1

        if 'exclusivamente al anime' in ch['notes'].lower():
            animes += 1
            bus_animes += 1
        elif 'exclusivamente' in ch['notes'].lower():
            if 'animes' in ch['notes'].lower():
                animes += 1
                bus_animes += 1
        else:
           if 'anime' in ch['clusters']: bus_animes += 1

        if '+18' in ch['notes']: adults += 1

        if 'privates' in ch['clusters']:
            el_canal = ch['id']
            if os.path.exists(os.path.join(config.get_runtime_path(), 'channels', el_canal)): privates += 1

    txt = '[COLOR yellow][B]RESÚMENES CANALES:[/B][/COLOR][CR]'

    txt += '  ' + str(total) + ' [COLOR darkorange][B]Canales[/B][/COLOR][CR][CR]'

    txt += '     ' + str(inactives) + ' [COLOR coral]Inactivos[/COLOR][CR]'
    txt += '           ' + str(cerrados) + ' [COLOR coral]Cerrados[/COLOR][CR]'
    txt += '           ' + str(anulados) + ' [COLOR coral]Anulados[/COLOR][CR]'

    if not temporarys == 0: txt += '       ' + str(temporarys) + ' [COLOR cyan]Temporalmente Inactivos[/COLOR][CR]'

    if not PY3:
        if not mismatcheds == 0: txt += '       ' + str(mismatcheds) + ' [COLOR violet]Posible Incompatibilidad[/COLOR][CR]'

    if not inestables == 0: txt += '       ' + str(inestables) + ' [COLOR plum]Inestables[/COLOR][CR]'

    if not problematics == 0: txt += '       ' + str(problematics) + ' [COLOR darkgoldenrod]Problemáticos[/COLOR][CR]'

    txt += '     ' + str(clones) + ' [COLOR turquoise]Clones[/COLOR][CR]'
    txt += '     ' + str(notices) + ' [COLOR olivedrab]Con Probable CloudFlare Protection[/COLOR][CR]'
    txt += '     ' + str(proxies) + ' [COLOR red]Pueden Usar Proxies[/COLOR][CR]'

    if not registers == 0: txt += '       ' + str(registers) + ' [COLOR teal]Requieren Cuenta[/COLOR][CR]'

    if not dominios == 0: txt += '       ' + str(dominios) + ' [COLOR green]Varios Dominios[/COLOR][CR]'

    txt += '     ' + str(currents) + ' [COLOR goldenrod]Gestión Dominio Vigente[/COLOR][CR]'

    if not onlyones == 0: txt += '     ' + str(onlyones) + ' [COLOR fuchsia]Con un Único Servidor[/COLOR][CR]'

    if not searchables == 0: txt += '     ' + str(searchables) + ' [COLOR aquamarine]No Actuan en Búsquedas[/COLOR][CR]'

    if txt_status:
        if no_accesibles:
            matches = no_accesibles.count('[COLOR lime]')

            if matches:
                status_access = matches

    txt += '[CR]  ' + str(disponibles) + ' [COLOR gold][B]Disponibles[/B][/COLOR][CR]'

    if not status_access == 0: txt += '          [COLOR indianred]No Accesibles[/COLOR][B] '  + str(status_access) + '[/B][CR]'

    accesibles = (disponibles - status_access)
    txt += '  ' + str(accesibles) + ' [COLOR powderblue][B]Accesibles[/B][/COLOR][CR]'

    if txt_status:
        if con_incidencias:
            matches = con_incidencias.count('[COLOR lime]')

            if matches:
                status_incid = matches

                txt += '          [COLOR tan]Con Incidencias[/COLOR][B] ' + str(status_incid) + '[/B][CR]'

    if not no_actives == 0: txt += '          [COLOR gray][B]Desactivados[/B][/COLOR][B] ' + str(no_actives) + '[/B][CR]'

    filtros = {}

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if ch_list:
        for ch in ch_list:
            cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

            if not config.get_setting(cfg_proxies_channel, default=''): continue

            con_proxies += 1

        if con_proxies > 0: txt += '          [COLOR red]Con Proxies Informados[/COLOR][B] ' +  str(con_proxies) + '[/B][CR]'

    txt += '[CR][COLOR dodgerblue][B]DISTRIBUCIÓN CANALES DISPONIBLES:[/B][/COLOR][CR]'

    txt += '    ' + str(suggesteds) + ' [COLOR moccasin]Sugeridos[/COLOR][CR]'

    txt += '[CR]  ' + str(peliculas) + ' [COLOR deepskyblue]Películas[/COLOR][CR]'

    txt += '  ' + str(series) + ' [COLOR hotpink]Series[/COLOR][CR]'

    txt += '    ' + str(pelisyseries) + ' [COLOR teal]Películas y Series[/COLOR][CR]'

    txt += '[CR]    ' + str(generos) + '  [COLOR thistle]Géneros[/COLOR][CR]'
    txt += '    ' + str(documentarys) + '  [COLOR cyan]Documentales[/COLOR][CR]'

    if not infantiles == 0: txt += '      ' + str(infantiles) + '  [COLOR lightyellow]Infantiles[/COLOR][CR]'

    txt += '    ' + str(tales) + '  [COLOR limegreen]Novelas[/COLOR][CR]'

    if not bibles == 0: txt += '      ' + str(bibles) + '  [COLOR tan]Bíblicos[/COLOR][CR]'

    txt += '    ' + str(torrents) + ' [COLOR blue]Torrents[/COLOR][CR]'
    txt += '    ' + str(doramas) + '  [COLOR firebrick]Doramas[/COLOR][CR]'
    txt += '    ' + str(animes) + '  [COLOR springgreen]Animes[/COLOR][CR]'
    txt += '    ' + str(adults) + '  [COLOR orange]Adultos[/COLOR][CR]'

    txt += '[CR][COLOR powderblue][B]DISTRIBUCIÓN CANALES DISPONIBLES PARA BÚSQUEDAS:[/B][/COLOR][CR]'

    txt += '   ' + str(bus_pelis) + ' [COLOR deepskyblue]Películas[/COLOR][CR]'
    txt += '   ' + str(bus_series) + ' [COLOR hotpink]Series[/COLOR][CR]'
    txt += '     ' + str(bus_pelisyseries) + ' [COLOR teal]Películas y Series[/COLOR][CR]'

    txt += '[CR]'
    txt += '     ' + str(bus_documentaryes) + ' [COLOR cyan]Documentales[/COLOR][CR]'

    bus_tematica_documentales = bus_documentales + bus_documentaryes
    txt += '   ' + str(bus_tematica_documentales) + ' [COLOR darkcyan]Temática Documental[/COLOR][CR]'

    txt += '[CR]'
    bus_tematica_infantil = bus_kids + bus_infantiles
    txt += '     ' + str(bus_tematica_infantil) + ' [COLOR lightyellow]Temática Infantil[/COLOR][CR]'

    txt += '[CR]'
    txt += '     ' + str(bus_torrents) + ' [COLOR blue]Torrents[/COLOR][CR]'
    txt += '[CR]'

    txt += '     ' + str(bus_doramas) + ' [COLOR firebrick]Temática Dorama[/COLOR][CR]'
    txt += '     ' + str(bus_animes) + ' [COLOR springgreen]Temática Anime[/COLOR][CR]'

    platformtools.dialog_textviewer('Resúmenes de Canales y su Distribución', txt)


def resumen_incidencias(item):
    logger.info()

    txt = ''

    if txt_status:
        if con_incidencias:
            matches = scrapertools.find_multiple_matches(con_incidencias, "[B](.*?)[/B]")

            for match in matches:
               match = match.strip()

               if '[COLOR moccasin]' in match: txt += '[B' + match + '/I][/B][/COLOR][CR]'

    if not txt:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No Hay Incidencias[/COLOR][/B]' % color_exec)
        return

    platformtools.dialog_textviewer('Canales Con Incidencias', txt)


def resumen_no_accesibles(item):
    logger.info()

    txt = ''

    if txt_status:
        if no_accesibles:
            matches = scrapertools.find_multiple_matches(no_accesibles, "[B](.*?)[/B]")

            for match in matches:
                match = match.strip()

                if '[COLOR moccasin]' in match: txt += '[B' + match + '/I][/B][/COLOR][CR]'

    if not txt:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No Hay No Accesibles[/COLOR][/B]' % color_exec)
        return

    platformtools.dialog_textviewer('Canales No Accesibles', txt)


def resumen_servidores(item):
    logger.info()

    from core import jsontools

    total = 0
    inactives = 0
    notsuported = 0
    outservice = 0
    alternatives = 0
    aditionals = 41
    disponibles = 0
    pending = 0

    path = os.path.join(config.get_runtime_path(), 'servers')

    servidores = os.listdir(path)

    for server in servidores:
        if not server.endswith('.json'): continue

        path_server = os.path.join(config.get_runtime_path(), 'servers', server)

        if not os.path.isfile(path_server): continue

        data = filetools.read(path_server)
        dict_server = jsontools.load(data)

        total += 1

        if dict_server['active'] == False: inactives += 1
        else: disponibles += 1

        try:
           notes = dict_server['notes']
        except: 
           notes = ''

        if "requiere" in notes.lower(): notsuported += 1
        elif "out of service" in notes.lower(): outservice += 1

        if not dict_server['name'] == 'Youtube':
            if "alternative" in notes.lower(): alternatives += 1

    txt = '[COLOR yellow][B]RESÚMENES SERVIDORES:[/B][/COLOR][CR]'

    txt += '  ' + str(total) + ' [COLOR darkorange][B]Servidores[/B][/COLOR][CR][CR]'

    txt += '    ' + str(inactives) + '  [COLOR coral]Inactivos[/COLOR][CR]'
    txt += '    ' + str(notsuported) + '  [COLOR fuchsia]Sin Soporte[/COLOR][CR]'

    if outservice > 0: txt += '    ' + str(outservice) + '  [COLOR red]Sin Servicio[/COLOR][CR]'

    txt += '[CR]  ' + str(disponibles) + '  [COLOR gold][B]Disponibles[/B][/COLOR][CR]'

    operativos = disponibles

    if outservice > 0:
        operativos = disponibles - outservice
        txt += '    ' + str(operativos) + '  [COLOR goldenrod][B]Operativos[/B][/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        txt += '[CR][COLOR goldenrod][B]RESOLVEURL:[/B][/COLOR][CR]'

        txt += '    ' + str(alternatives) + '  [COLOR green]Vías alternativas[/COLOR][CR]'
        txt += '    ' + str(aditionals) + '  [COLOR powderblue]Vías Adicionales[/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
        txt += '[CR][COLOR goldenrod][B]YOUTUBE:[/B][/COLOR][CR]'

        txt += '      1' + '   [COLOR green]Vía alternativa[/COLOR][CR]'

    txt += '[CR][COLOR dodgerblue][B]DISTRIBUCIÓN SERVIDORES DISPONIBLES:[/B][/COLOR]'

    accesibles = (operativos + aditionals)
    txt += '[CR]  ' + str(accesibles) + '  [COLOR powderblue][B]Accesibles[/B][/COLOR][CR]'

    if txt_status:
        if srv_pending:
            matches = srv_pending.count('[COLOR orchid]')

            if matches:
                status = matches

                txt += '           [COLOR tan]Con Incidencias[/COLOR][B] ' + str(status) + '[/B][CR]'

    platformtools.dialog_textviewer('Resúmenes Servidores y su Distribución', txt)


def resumen_pending(item):
    logger.info()

    txt = ''

    if txt_status:
        if srv_pending:
            matches = scrapertools.find_multiple_matches(srv_pending, "[B](.*?)[/B]")

            for match in matches:
                match = match.strip()

                if '[COLOR orchid]' in match: txt += '[B' + match + '/I][/B][/COLOR][CR]'

    if not txt:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No Hay con Incidencias[/COLOR][/B]' % color_exec)
        return

    platformtools.dialog_textviewer('Servidores con Incidencias', txt)


def show_help_alternativas(item):
    logger.info()

    txt = ''

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        cod_version = xbmcaddon.Addon("script.module.resolveurl").getAddonInfo("version").strip()
        tex_mr = '  ' + cod_version
    else: tex_mr = '[COLOR red][B]No instalado[/B][/COLOR]'

    txt += '[CR][COLOR gold]ResolveUrl Script:[/COLOR]  %s' % tex_mr

    txt += '[CR][CR] - Qué servidores tienen [COLOR goldenrod][B]Vías Alternativas[/B][/COLOR] a través de [COLOR fuchsia][B]ResolveUrl[/B][/COLOR]:[CR]'

    txt += '   [COLOR yellow]Clicknupload[/COLOR][CR]'
    txt += '   [COLOR yellow]Cloudvideo[/COLOR][CR]'
    txt += '   [COLOR yellow]Dailymotion[/COLOR][CR]'
    txt += '   [COLOR yellow]Doodstream[/COLOR][CR]'
    txt += '   [COLOR yellow]Flashx[/COLOR][CR]'
    txt += '   [COLOR yellow]Gofile[/COLOR][CR]'
    txt += '   [COLOR yellow]MegaUp[/COLOR][CR]'
    txt += '   [COLOR yellow]Mixdrop[/COLOR][CR]'
    txt += '   [COLOR yellow]Playtube[/COLOR][CR]'
    txt += '   [COLOR yellow]Racaty[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamlare[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamvid[/COLOR][CR]'
    txt += '   [COLOR yellow]Uptobox[/COLOR][CR]'
    txt += '   [COLOR yellow]Userscloud[/COLOR][CR]'
    txt += '   [COLOR yellow]Various[/COLOR][CR]'
    txt += '   [COLOR yellow]Vimeo[/COLOR][CR]'
    txt += '   [COLOR yellow]Vidmoly[/COLOR][CR]'
    txt += '   [COLOR yellow]Vk[/COLOR][CR]'
    txt += '   [COLOR yellow]Voe[/COLOR][CR]'
    txt += '   [COLOR yellow]Waaw[/COLOR][CR]'
    txt += '   [COLOR yellow]Zures[/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
        cod_version = xbmcaddon.Addon("plugin.video.youtube").getAddonInfo("version").strip()
        tex_yt = '  ' + cod_version
    else: tex_yt = '  [COLOR red]No instalado[/COLOR]'

    txt += '[CR][CR][COLOR gold]Youtube Plugin:[/COLOR]  %s' % tex_yt

    txt += '[CR][CR] - Qué servidor tiene [COLOR goldenrod][B]Vía Alternativa[/B][/COLOR] a través de [COLOR fuchsia][B]YouTube[/B][/COLOR]:[CR]'

    txt += '    [COLOR yellow]Youtube[/COLOR][CR]'

    platformtools.dialog_textviewer('Servidores Vías Alternativas', txt)


def show_help_adicionales(item):
    logger.info()

    txt = ''

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        cod_version = xbmcaddon.Addon("script.module.resolveurl").getAddonInfo("version").strip()
        tex_mr = '  ' + cod_version
    else: tex_mr = '[COLOR red][B]No instalado[/B][/COLOR]'

    txt += '[CR][COLOR gold]ResolveUrl Script:[/COLOR]  %s' % tex_mr

    txt += '[CR][CR] - Servidores [COLOR goldenrod][B]Vías Adicionales[/B][/COLOR] a través de [COLOR fuchsia][B]ResolveUrl[/B][/COLOR]:[CR]'

    txt += '   [COLOR yellow]Desiupload[/COLOR][CR]'
    txt += '   [COLOR yellow]Drop[/COLOR][CR]'
    txt += '   [COLOR yellow]Dropload[/COLOR][CR]'
    txt += '   [COLOR yellow]Embedgram[/COLOR][CR]'
    txt += '   [COLOR yellow]Embedrise[/COLOR][CR]'
    txt += '   [COLOR yellow]Emturbovid[/COLOR][CR]'
    txt += '   [COLOR yellow]Fastupload[/COLOR][CR]'
    txt += '   [COLOR yellow]Filelions[/COLOR][CR]'
    txt += '   [COLOR yellow]Filemoon[/COLOR][CR]'
    txt += '   [COLOR yellow]Fileupload[/COLOR][CR]'
    txt += '   [COLOR yellow]Goodstream[/COLOR][CR]'
    txt += '   [COLOR yellow]Hxfile[/COLOR][CR]'
    txt += '   [COLOR yellow]Hexupload[/COLOR][CR]'
    txt += '   [COLOR yellow]Krakenfiles[/COLOR][CR]'
    txt += '   [COLOR yellow]Lulustream[/COLOR][CR]'
    txt += '   [COLOR yellow]Mvidoo[/COLOR][CR]'
    txt += '   [COLOR yellow]Qiwi[/COLOR][CR]'
    txt += '   [COLOR yellow]Rumble[/COLOR][CR]'
    txt += '   [COLOR yellow]Rutube[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamhub[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamruby[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamsilk[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamvid[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamwish[/COLOR][CR]'
    txt += '   [COLOR yellow]Terabox[/COLOR][CR]'
    txt += '   [COLOR yellow]Tubeload[/COLOR][CR]'
    txt += '   [COLOR yellow]Turboviplay[/COLOR][CR]'
    txt += '   [COLOR yellow]Twitch[/COLOR][CR]'
    txt += '   [COLOR yellow]Uploaddo[/COLOR][CR]'
    txt += '   [COLOR yellow]Uploadever[/COLOR][CR]'
    txt += '   [COLOR yellow]Uploadraja[/COLOR][CR]'
    txt += '   [COLOR yellow]Userload[/COLOR][CR]'
    txt += '   [COLOR yellow]Vidello[/COLOR][CR]'
    txt += '   [COLOR yellow]Videowood[/COLOR][CR]'
    txt += '   [COLOR yellow]Vidguard[/COLOR][CR]'
    txt += '   [COLOR yellow]Vidhide[/COLOR][CR]'
    txt += '   [COLOR yellow]Vidspeed[/COLOR][CR]'
    txt += '   [COLOR yellow]Vkspeed[/COLOR][CR]'
    txt += '   [COLOR yellow]Vudeo[/COLOR][CR]'
    txt += '   [COLOR yellow]Yandex[/COLOR][CR]'
    txt += '   [COLOR yellow]Youdbox[/COLOR]'

    platformtools.dialog_textviewer('Servidores Vías Adicionales', txt)
