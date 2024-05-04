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


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


_foro = "[COLOR plum][B][I] www.mimediacenter.info/foro/ [/I][/B][/COLOR]"
_source = "[COLOR coral][B][I] https://repobal.github.io/base/ [/I][/B][/COLOR]"
_telegram = "[COLOR lightblue][B][I] t.me/balandro_asesor [/I][/B][/COLOR]"

_team = "[COLOR hotpink][B][I] t.me/balandro_team [/I][/B][/COLOR]"


context_desarrollo = []

tit = '[COLOR goldenrod][B]Miscelánea[/B][/COLOR]'
context_desarrollo.append({'title': tit, 'channel': 'helper', 'action': 'show_help_miscelanea'})

tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_desarrollo.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR %s]Ajustes categoría Team[/COLOR]' % color_exec
context_desarrollo.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


def submnu_team(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]DESARROLLO:[/B]', thumbnail=config.get_thumb('team'), text_color='darkorange' ))

    itemlist.append(item.clone( action='submnu_team_info', title='[COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news'), context=context_desarrollo ))

    itemlist.append(item.clone( action='', title='[B]Menú:[/B]', thumbnail=config.get_thumb('addon'), text_color='tan' ))

    itemlist.append(item.clone( action='submnu_center', title=' - [B]Media Center[/B]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

    itemlist.append(item.clone( action='submnu_addons', title=' - [B]Add-Ons[/B]', thumbnail=config.get_thumb('tools'), text_color='yellowgreen' ))

    itemlist.append(item.clone( action='submnu_sistema', title=' - [B]Sistema[/B]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

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

    itemlist.append(item.clone( action='submnu_proxies', title=' - [B]Tests Proxies[/B]', thumbnail=config.get_thumb('tools'), text_color='red' ))

    itemlist.append(item.clone( action='submnu_canales', title=' - [B]Tests Canales[/B]', thumbnail=config.get_thumb('tools'), text_color='gold' ))

    itemlist.append(item.clone( action='submnu_servidores', title=' - [B]Tests Servidores[/B]', thumbnail=config.get_thumb('tools'), text_color='fuchsia' ))

    itemlist.append(item.clone( action='submnu_developers', title=' - [B]Developers[/B]', thumbnail=config.get_thumb('team'), text_color='firebrick' ))

    try: last_ver = updater.check_addon_version()
    except: last_ver = None

    if last_ver is None: last_ver = '[B][I][COLOR %s](sin acceso)[/COLOR][/I][/B]' % color_alert
    elif not last_ver: last_ver = '[B][I][COLOR %s](desfasada)[/COLOR][/I][/B]' % color_adver
    else: last_ver = ''

    title = '[COLOR chocolate][B]Ajustes [COLOR powderblue]Preferencias[/B][/COLOR] (%s)  %s' % (config.get_addon_version(), last_ver)

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title=title, thumbnail=config.get_thumb('settings'), text_color='chocolate' ))

    return itemlist


def submnu_team_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR darkorange]DESARROLLO[/COLOR][/B]:' ))

    path = os.path.join(config.get_runtime_path(), 'dominios.txt')

    existe = filetools.exists(path)

    if existe:
        txt_status = ''

        try:
           with open(os.path.join(config.get_runtime_path(), 'dominios.txt'), 'r') as f: txt_status=f.read(); f.close()
        except:
           try: txt_status = open(os.path.join(config.get_runtime_path(), 'dominios.txt'), encoding="utf8").read()
           except: pass

        if txt_status:
            bloque = scrapertools.find_single_match(txt_status, 'SITUACION CANALES(.*?)CANALES TEMPORALMENTE DES-ACTIVADOS')

            matches = bloque.count('[COLOR lime]')

            if matches:
                itemlist.append(item.clone( channel='actions', action='show_latest_domains', title='[COLOR aqua][B]Últimos Cambios Dominios[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='resumen_canales', title='[COLOR gold][B]Canales[/B][/COLOR] Resúmenes y Distribución', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='resumen_servidores', title='[COLOR fuchsia][B]Servidores[/B][/COLOR] Resúmenes y Distribución', thumbnail=config.get_thumb('bolt') ))

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
       itemlist.append(item.clone( action='show_help_alternativas', title='Qué servidores tienen [COLOR yellow][B]Vías Alternativas[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))
       itemlist.append(item.clone( action='show_help_adicionales', title='Servidores [COLOR goldenrod][B]Vías Adicionales[/B][/COLOR] a través de [COLOR yellowgreen][B]ResolveUrl[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

    return itemlist


def submnu_center(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]MEDIA CENTER:[/B]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

    if not item.helper:
        itemlist.append(item.clone( action='submnu_center_info', title='[COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    path = translatePath(os.path.join('special://home/userdata', ''))

    file_advs = 'advancedsettings.xml'
    file = path + file_advs
    existe = filetools.exists(file)

    if existe:
        itemlist.append(item.clone( action='', title='[I]Archivo ADVANCED SETTINGS:[/I]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

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
        itemlist.append(item.clone( action='', title='[I]Archivo FAVOURITES SETTINGS:[/I]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

        itemlist.append(item.clone( channel='helper', action='show_favs', title=' - Ver', thumbnail=config.get_thumb('quote'), text_color='yellow' ))
        itemlist.append(item.clone( channel='actions', action='manto_favs', title=' - Eliminar', thumbnail=config.get_thumb('quote'), text_color='red' ))

    file_pcfs = 'playercorefactory.xml'
    file = path + file_pcfs
    existe = filetools.exists(file)

    if existe:
        itemlist.append(item.clone( action='', title='[I]Archivo PLAYERCOREFACTORY SETTINGS:[/I]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

        itemlist.append(item.clone( channel='helper', action='show_pcfs', title=' - Ver', thumbnail=config.get_thumb('quote'), text_color='yellow' ))
        itemlist.append(item.clone( channel='actions', action='manto_pcfs', title=' - Eliminar [B][COLOR violet](Si ejecuta es Recomendable Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('quote'), text_color='red' ))

    presentar = False

    path_cache = translatePath(os.path.join('special://temp/archive_cache', ''))
    existe_cache = filetools.exists(path_cache)

    caches = []
    if existe_cache: caches = os.listdir(path_cache)

    if caches: presentar = True

    if presentar:
        itemlist.append(item.clone( action='', title='[I]Archivos en la CACHÉ:[/I]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

        itemlist.append(item.clone( action='show_addons', title=' - Ver', addons = caches, tipo = 'Caché', thumbnail=config.get_thumb('keyboard'), text_color='yellow' ))

        itemlist.append(item.clone( channel='actions', action='manto_caches', title=' - Eliminar [B][COLOR cyan](Si ejecuta es Obligatorio Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('keyboard'), text_color='red' ))

    path_thumbs = translatePath(os.path.join('special://home/userdata/Thumbnails', ''))
    existe_thumbs = filetools.exists(path_thumbs)

    if existe_thumbs:
        itemlist.append(item.clone( action='', title='[I]Archivos en THUMBNAILS:[/I]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

        itemlist.append(item.clone( channel='actions', action='manto_thumbs', title=' - Eliminar [B][COLOR cyan](Si ejecuta es Obligatorio Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('keyboard'), text_color='red' ))

    if item.helper: platformtools.itemlist_refresh()

    return itemlist


def submnu_center_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR pink]MEDIA CENTER[/COLOR][/B]:' ))

    itemlist.append(item.clone( channel='helper', action='show_plataforma', title='[COLOR gold][B]Plataforma[/B][/COLOR]', thumbnail=config.get_thumb('computer') ))

    itemlist.append(item.clone( channel='actions', action = 'test_internet', title= 'Comprobar [COLOR goldenrod][B]Internet[/B][/COLOR]', thumbnail=config.get_thumb('crossroads') ))

    itemlist.append(item.clone( action='', title='[I]Archivo LOG BALANDRO:[/I]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

    itemlist.append(item.clone( action='balandro_log', title=' -  Ver Log ejecución Balandro', thumbnail=config.get_thumb('search'), text_color='coral' ))

    itemlist.append(item.clone( action='', title='[I]Archivo LOG GENERAL:[/I]', thumbnail=config.get_thumb('computer'), text_color='pink' ))

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
            itemlist.append(item.clone( action='', title='[I]Archivos en PACKAGES:[/I]', thumbnail=config.get_thumb('computer'), text_color='yellowgreen' ))

            itemlist.append(item.clone( action='show_addons', title=' - Ver', addons = packages, tipo = 'Packages', thumbnail=config.get_thumb('keyboard'), text_color='yellow' ))

            itemlist.append(item.clone( channel='actions', action='manto_addons_packages', title=' - Eliminar [B][COLOR violet](Si ejecuta es Recomendable Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('keyboard'), text_color='red' ))

        if temps:
            itemlist.append(item.clone( action='', title='[I]Archivos en TEMP:[/I]', thumbnail=config.get_thumb('computer'), text_color='yellowgreen' ))

            itemlist.append(item.clone( action='show_addons', title=' - Ver', addons = temps, tipo = 'Temp', thumbnail=config.get_thumb('keyboard'), text_color='yellow' ))

            itemlist.append(item.clone( channel='actions', action='manto_addons_temp', title=' - Eliminar [B][COLOR violet](Si ejecuta es Recomendable Re-iniciar Media Center)[/B][/COLOR]', thumbnail=config.get_thumb('keyboard'), text_color='red' ))

    if item.helper: platformtools.itemlist_refresh()

    if item.helper:
        if not presentar: return []

    return itemlist


def submnu_addons_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR yellowgreen]ADD-ONS[/COLOR][/B]:' ))

    itemlist.append(item.clone( channel='helper', action='show_help_vias', title= 'Vía alternativa [COLOR goldenrod][B]ResolveUrl[/B][/COLOR]', thumbnail=config.get_thumb('resolveurl') ))
    itemlist.append(item.clone( channel='helper', action='show_help_vias', title= 'Vía alternativa [COLOR goldenrod][B]Youtube[/B][/COLOR]', thumbnail=config.get_thumb('youtube') ))

    itemlist.append(item.clone( channel='helper', action='show_help_torrents', title= '¿ Dónde obtener los Add-Ons para [COLOR gold][B]Clientes/Motores[/B][/COLOR] torrents ?', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( channel='helper', action='show_clients_torrent', title= 'Clientes/Motores externos torrent [COLOR gold][B]Soportados[/B][/COLOR]', thumbnail=config.get_thumb('cloud') ))

    itemlist.append(item.clone( action='', title='[I]Add-ons EXTERNOS y VIAS ALTERNATIVAS:[/I]', thumbnail=config.get_thumb('tools'), text_color='yellowgreen' ))

    if config.get_setting('mnu_torrents', default=True):
        cliente_torrent = config.get_setting('cliente_torrent', default='Seleccionar')

        if cliente_torrent == 'Seleccionar' or cliente_torrent == 'Ninguno': tex_tor = cliente_torrent
        else:
           tex_tor = cliente_torrent
           cliente_torrent = 'plugin.video.' + cliente_torrent.lower()
           if xbmc.getCondVisibility('System.HasAddon("%s")' % cliente_torrent):
               cod_version = xbmcaddon.Addon(cliente_torrent).getAddonInfo("version").strip()
               tex_tor += '  [COLOR goldenrod]' + cod_version + '[/COLOR]'

        itemlist.append(item.clone( action = '', title= ' - Cliente/Motor Torrent Habitual asignado ' + '[COLOR fuchsia][B] ' + tex_tor + '[/B][/COLOR]', thumbnail=config.get_thumb('torrents') ))

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

    itemlist.append(item.clone( action='', title='[I]Add-ons EXTERNOS REPOSITORIOS:[/I]', thumbnail=config.get_thumb('tools'), text_color='yellowgreen' ))

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

    return itemlist


def submnu_sistema(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]SISTEMA:[/B]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

    if not item.helper:
        itemlist.append(item.clone( action='submnu_sistema_info', title='[COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    path = os.path.join(config.get_data_path(), 'Lista-proxies.txt')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]Archivo LISTA-PROXIES.TXT:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        itemlist.append(item.clone( channel='helper', action='show_yourlist', title=' - Ver', thumbnail=config.get_thumb('keyboard'), text_color='yellow' ))

        itemlist.append(item.clone( channel='actions', action='manto_yourlist', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    path = os.path.join(config.get_data_path(), 'cookies.dat')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]Archivo COOKIES:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        itemlist.append(item.clone( channel='actions', action='manto_cookies', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    path = os.path.join(config.get_data_path(), 'cache')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]Carpeta CACHÉ:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        itemlist.append(item.clone( channel='actions', action='manto_folder_cache', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    if not item.helper:
        downloadpath = config.get_setting('downloadpath', default='')

        if downloadpath: path = downloadpath
        else: path = filetools.join(config.get_data_path(), 'downloads')

        existe = filetools.exists(path)

        if existe:
            itemlist.append(item.clone( action='', title='[I]Contenido DESCARGAS:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

            itemlist.append(item.clone( channel='actions', action='manto_folder_downloads', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

        path = filetools.join(config.get_data_path(), 'tracking_dbs')

        existe = filetools.exists(path)

        if existe:
            itemlist.append(item.clone( action='', title='[I]Contenido PREFERIDOS:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

            itemlist.append(item.clone( channel='actions', action='manto_tracking_dbs', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    path = filetools.join(config.get_data_path(), 'tmdb.sqlite-journal')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]Archivo TMDB SQLITE JOURNAL:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        itemlist.append(item.clone( channel='actions', action='manto_tmdb_sqlite', title= " - Eliminar", journal = 'journal', thumbnail=config.get_thumb('computer'), text_color='red' ))

    path = filetools.join(config.get_data_path(), 'tmdb.sqlite')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]Archivo TMDB SQLITE:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

        itemlist.append(item.clone( channel='actions', action='manto_tmdb_sqlite', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    if not item.helper:
        path = config.get_data_path()

        existe = filetools.exists(path)

        if existe:
            itemlist.append(item.clone( action='', title='[I]Ajustes PREFERENCIAS:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

            itemlist.append(item.clone( channel='actions', action='manto_folder_addon', title= " - Eliminar", thumbnail=config.get_thumb('computer'), text_color='red' ))

    if item.helper: platformtools.itemlist_refresh()

    return itemlist


def submnu_sistema_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR violet]SISTEMA[/COLOR][/B]:' ))

    itemlist.append(item.clone( channel='actions', action='show_latest_domains', title='[COLOR aqua][B]Últimos Cambios Dominios[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( channel='helper', action='show_version', title= '[COLOR lime][B]Versión[/B][/COLOR]', thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( channel='actions', action = 'test_internet', title= 'Comprobar [COLOR goldenrod][B]Internet[/B][/COLOR]', thumbnail=config.get_thumb('crossroads') ))
    itemlist.append(item.clone( channel='helper', action='show_test', title= 'Test [COLOR gold][B]Status[/B][/COLOR] del sistema', thumbnail=config.get_thumb('addon') ))

    path = os.path.join(config.get_runtime_path(), 'last_fix.json')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='', title='[I]Archivo FIX:[/I]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

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
            itemlist.append(item.clone( action='', title='[I]Log de SERVIDORES:[/I]', thumbnail=config.get_thumb('tools'), text_color='limegreen' ))

            itemlist.append(item.clone( channel='helper', action='show_todo_log', title=' - Ver', todo = 'servers_todo.log', thumbnail=config.get_thumb('crossroads'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'qualities_todo.log')):
            itemlist.append(item.clone( action='', title='[I]Log de CALIDADES:[/I]', thumbnail=config.get_thumb('tools'), text_color='limegreen' ))

            itemlist.append(item.clone( channel='helper', action='show_todo_log', title=' - Ver', todo = 'qualities_todo.log', thumbnail=config.get_thumb('quote'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'proxies.log')):
            itemlist.append(item.clone( action='', title='[I]Log de PROXIES:[/I]', thumbnail=config.get_thumb('tools'), text_color='limegreen' ))

            itemlist.append(item.clone( channel='helper', action='show_todo_log', title=' - Ver', todo = 'proxies.log', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        itemlist.append(item.clone( channel='actions', action='manto_temporales', title='Eliminar', _logs = True, thumbnail=config.get_thumb('keyboard'), text_color='red' ))

    if item.helper: platformtools.itemlist_refresh()

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
            itemlist.append(item.clone( action='', title='[I]Ficheros INFO CHANNELS:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay Info channels', thumbnail=config.get_thumb('dev'), text_color='goldenrod' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'temp.torrent')):
            itemlist.append(item.clone( action='', title='[I]Fichero TORRENT:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay Torrent', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'm3u8hls.m3u8')):
            itemlist.append(item.clone( action='', title='[I]Fichero M3U8HLS:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay M3u8hls', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'blenditall.m3u8')):
            itemlist.append(item.clone( action='', title='[I]Fichero BLENDITALL:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay M3u8', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'test_logs')):
            itemlist.append(item.clone( action='', title='[I]Ficheros Test LOGS:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay Test logs', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'temp_updates.zip')):
            itemlist.append(item.clone( action='', title='[I]Fichero UPDATES:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay Updates', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        if os.path.exists(os.path.join(config.get_data_path(), 'tempfile_mkdtemp')):
            itemlist.append(item.clone( action='', title='[I]Ficheros MKDTEMP:[/I]', thumbnail=config.get_thumb('tools'), text_color='cyan' ))

            itemlist.append(item.clone( action='', title=' - Hay Mkdtemp', thumbnail=config.get_thumb('dev'), text_color='yellow' ))

        itemlist.append(item.clone( channel='actions', action='manto_temporales', title='Eliminar', thumbnail=config.get_thumb('keyboard'), text_color='red' ))

    if item.helper: platformtools.itemlist_refresh()

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

    itemlist.append(item.clone( action='', title='[B]TESTS PROXIES:[/B]', thumbnail=config.get_thumb('tools'), text_color='red' ))

    itemlist.append(item.clone( action='submnu_proxies_info', title='[COLOR green][B]Información[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( action='', title='[I]OPCIONES PROXIES:[/I]', thumbnail=config.get_thumb('tools'), text_color='red' ))

    itemlist.append(item.clone( action='test_providers', title= ' - [COLOR yellowgreen][B]Tests[/B][/COLOR] Proveedores', thumbnail=config.get_thumb('flame') ))

    itemlist.append(item.clone( action='test_tplus', title= ' - Asignar proveedor [COLOR goldenrod][B]TPlus[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='helper', action='channels_with_proxies', title= ' - Qué canales pueden usar Proxies', new_proxies=True, test_proxies=True, thumbnail=config.get_thumb('stack') ))

    if config.get_setting('memorize_channels_proxies', default=True):
        itemlist.append(item.clone( channel='helper', action='channels_with_proxies_memorized', title= ' - Qué [COLOR red]canales[/COLOR] tiene con proxies [COLOR red][B]Memorizados[/B][/COLOR]',
                                    new_proxies=True, memo_proxies=True, test_proxies=True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='actions', action = 'manto_proxies', title= ' - Quitar los proxies en los canales [COLOR red][B](que los tengan Memorizados)[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='actions', action = 'global_proxies', title = ' - Configurar proxies a usar [COLOR plum][B](en los canales que los necesiten)[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    presentar = False

    path = os.path.join(config.get_data_path(), 'Lista-proxies.txt')

    existe = filetools.exists(path)

    if existe: presentar = True

    if presentar:
        itemlist.append(item.clone( action='', title='[I]Fichero LISTA-PROXIES.TXT:[/I]', thumbnail=config.get_thumb('tools'), text_color='red' ))

        itemlist.append(item.clone( channel='helper', action='show_help_yourlist', title= ' - [COLOR goldenrod][B]Gestión[/B][/COLOR] Fichero Personalizado', thumbnail=config.get_thumb('pencil') ))

        itemlist.append(item.clone( channel='helper', action='show_yourlist', title= ' - [COLOR green][B]Contenido[/B][/COLOR] de su Fichero [COLOR gold][B]Personalizado[/B][/COLOR] de proxies', thumbnail=config.get_thumb('settings') ))

        itemlist.append(item.clone( channel='actions', action='manto_yourlist', title= ' - [COLOR red][B]Eliminar[/B][/COLOR] su Fichero [COLOR yellow][B]Personalizado[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_proxies_info(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[COLOR green][B]INFORMACIÓN[/COLOR] [COLOR red]TEST PROXIES[/COLOR][/B]:' ))

    itemlist.append(item.clone( channel='helper', action='show_help_proxies', title= 'Uso de proxies', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='helper', action='show_help_providers', title= 'Proveedores de proxies', thumbnail=config.get_thumb('settings') ))

    if config.get_setting('proxies_extended', default=False): 
        itemlist.append(item.clone( channel='helper', action='show_help_providers2', title= 'Lista [COLOR aqua][B]Ampliada[/B][/COLOR] de Proveedores de proxies', thumbnail=config.get_thumb('settings') ))

    if config.get_setting('proxies_vias', default=False): 
        itemlist.append(item.clone( channel='helper', action='proxies_show_vias', title= 'Lista [COLOR aqua][B]Vías Alternativas[/B][/COLOR] de Proveedores de proxies', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_canales(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]TESTS CANALES:[/B]', thumbnail=config.get_thumb('tools'), text_color='gold' ))

    itemlist.append(item.clone( action='test_all_webs', title=' - Posibles [B][COLOR gold]Insatisfactorios[/B][/COLOR]', thumbnail=config.get_thumb('stack'), unsatisfactory = True ))
    itemlist.append(item.clone( action='test_alfabetico', title=' - Insatisfactorios desde un canal [B][COLOR powderblue]letra inicial[/B][/COLOR]', thumbnail=config.get_thumb('stack'), unsatisfactory = True ))

    itemlist.append(item.clone( action='test_all_webs', title=' - Todos', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='test_one_channel', title=' - Un canal concreto', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='test_one_channel', title= ' - Temporalmente [B][COLOR mediumaquamarine]Inactivos[/B][/COLOR]', temp_no_active = True, thumbnail=config.get_thumb('stack') ))

    return itemlist


def submnu_servidores(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]TESTS SERVIDORES:[/B]', thumbnail=config.get_thumb('tools'), text_color='fuchsia' ))

    itemlist.append(item.clone( action='test_all_srvs', title=' - Posibles [B][COLOR fuchsia]Insatisfactorios[/B][/COLOR]', thumbnail=config.get_thumb('bolt'), unsatisfactory = True ))
    itemlist.append(item.clone( action='test_alfabetico', title=' - Insatisfactorios desde un servidor [B][COLOR powderblue]letra inicial[/B][/COLOR]', thumbnail=config.get_thumb('bolt'), unsatisfactory = True ))

    itemlist.append(item.clone( action='test_all_srvs', title=' - Todos', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( action='test_one_server', title=' - Un servidor concreto', thumbnail=config.get_thumb('bolt') ))

    return itemlist


def submnu_developers(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]DEVELOPERS:[/B]', thumbnail=config.get_thumb('team'), text_color='firebrick' ))

    itemlist.append(item.clone( channel='helper', action='show_help_notice', title= '[COLOR aqua][B]Comunicado[/B][/COLOR] Oficial de Balandro', thumbnail=config.get_thumb('megaphone') ))

    itemlist.append(item.clone( channel='helper', action='show_dev_notes', title= 'Notas para Developers (desarrolladores)', thumbnail=config.get_thumb('tools') ))

    itemlist.append(item.clone( action='copy_dev', title= 'Obtener una Copia del fichero dev-notes.txt', thumbnail=config.get_thumb('folder'), text_color='yellowgreen' ))

    itemlist.append(item.clone( channel='helper', action='', title= '[COLOR firebrick][B][I]Desarrollo [COLOR powderblue]Fuentes[/COLOR]:[/I][/B][/COLOR]', folder=False, thumbnail=config.get_thumb('team') ))

    itemlist.append(item.clone( channel='helper', action='', title= ' - Fuentes [COLOR darkorange][B]github.com/repobal[/B][/COLOR]', thumbnail=config.get_thumb('telegram'), folder=False ))

    itemlist.append(item.clone( channel='helper', action='', title= '[COLOR firebrick][B][I]Desarrollo [COLOR powderblue]Telegram[/COLOR]:[/I][/B][/COLOR]', folder=False, thumbnail=config.get_thumb('team') ))

    itemlist.append(item.clone( channel='helper', action='', title= ' - Team ' + _team + ' Equipo de Desarrollo', folder=False, thumbnail=config.get_thumb('foro') ))

    itemlist.append(item.clone( action='', title= '[COLOR firebrick][B]Desarrollo[/COLOR][COLOR powderblue] Incorporaciones[/COLOR]:[/B]', folder=False, thumbnail=config.get_thumb('team') ))

    itemlist.append(item.clone( channel='helper', action='', title='[COLOR yellow][B][I]  Solicitudes solo con Enlace de Invitación[/I][/B][/COLOR]', folder=False, thumbnail=config.get_thumb('pencil') ))

    itemlist.append(item.clone( channel='helper', action='', title= '  Foro ' + _foro, thumbnail=config.get_thumb('foro'), folder=False ))
    itemlist.append(item.clone( channel='helper', action='', title= '  Telegram ' + _telegram, thumbnail=config.get_thumb('telegram'), folder=False ))

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

    opciones_tplus = [
            'openproxy.space http',
            'openproxy.space socks4',
            'openproxy.space socks5',
            'vpnoverview.com',
            'proxydb.net http',
            'proxydb.net https',
            'proxydb.net socks4',
            'proxydb.net socks5',
            'netzwelt.de',
            'proxy-list.download http',
            'proxy-list.download https',
            'proxy-list.download socks4',
            'proxy-list.download socks5',
            'freeproxy.world',
            'freeproxy.world anonymity',
            'hidemyna.me.en',
            'list.proxylistplus.com',
            'proxyservers.pro',
            'TheSpeedX',
            'proxyscan.io http',
            'proxyscan.io https',
            'openproxylist.xyz http',
            'openproxylist.xyz socks4',
            'openproxylist.xyz socks5',
            'proxy-list.download v1 socks4',
            'proxy-list.download v1 socks5',
            'monosans',
            'jetkai',
            'sunny9577',
            'proxy4parsing',
            'hendrikbgr',
            'rdavydov http',
            'aslisk',
            'rdavydov socks4',
            'hookzof',
            'manuGMG',
            'rdavydov socks5',
            'lamt3012'
            ]

    preselect = tplus_actual
    ret = platformtools.dialog_select('Proveedores Tplus', opciones_tplus, preselect=preselect)
    if ret == -1: return

    if opciones_tplus[ret] == 'openproxy.space http': proxies_tplus = '0'
    elif opciones_tplus[ret] == 'openproxy.space socks4': proxies_tplus = '1'
    elif opciones_tplus[ret] == 'openproxy.space socks5': proxies_tplus = '2'
    elif opciones_tplus[ret] == 'vpnoverview.com': proxies_tplus = '3'
    elif opciones_tplus[ret] == 'proxydb.net http': proxies_tplus = '4'
    elif opciones_tplus[ret] == 'proxydb.net https': proxies_tplus = '5'
    elif opciones_tplus[ret] == 'proxydb.net socks4': proxies_tplus = '6'
    elif opciones_tplus[ret] == 'proxydb.net socks5': proxies_tplus = '7'
    elif opciones_tplus[ret] == 'netzwelt.de': proxies_tplus = '8'
    elif opciones_tplus[ret] == 'proxy-list.download http': proxies_tplus = '9'
    elif opciones_tplus[ret] == 'proxy-list.download https': proxies_tplus = '10'
    elif opciones_tplus[ret] == 'proxy-list.download socks4': proxies_tplus = '11'
    elif opciones_tplus[ret] == 'proxy-list.download socks5': proxies_tplus = '12'
    elif opciones_tplus[ret] == 'freeproxy.world': proxies_tplus = '13'
    elif opciones_tplus[ret] == 'freeproxy.world nonymity': proxies_tplus = '14'
    elif opciones_tplus[ret] == 'hidemyna.me.en': proxies_tplus = '15'
    elif opciones_tplus[ret] == 'lis.proxylistplus.com': proxies_tplus = '16'
    elif opciones_tplus[ret] == 'proxyservers.pro': proxies_tplus = '17'
    elif opciones_tplus[ret] == 'TheSpeedX': proxies_tplus = '18'
    elif opciones_tplus[ret] == 'proxyscan.io http': proxies_tplus = '19'
    elif opciones_tplus[ret] == 'proxyscan.io https': proxies_tplus = '20'
    elif opciones_tplus[ret] == 'openproxylist.xyz http': proxies_tplus = '21'
    elif opciones_tplus[ret] == 'openproxylist.xyz socks4': proxies_tplus = '22'
    elif opciones_tplus[ret] == 'openproxylist.xyz socks5': proxies_tplus = '23'
    elif opciones_tplus[ret] == 'proxy-list.download v1 socks4': proxies_tplus = '24'
    elif opciones_tplus[ret] == 'proxy-list.download v1 socks5': proxies_tplus = '25'
    elif opciones_tplus[ret] == 'monosans': proxies_tplus = '26'
    elif opciones_tplus[ret] == 'jetkai': proxies_tplus = '27'
    elif opciones_tplus[ret] == 'sunny9577': proxies_tplus = '28'
    elif opciones_tplus[ret] == 'proxy4parsing': proxies_tplus = '29'
    elif opciones_tplus[ret] == 'hendrikbgr': proxies_tplus = '30'
    elif opciones_tplus[ret] == 'rdavydov http': proxies_tplus = '31'
    elif opciones_tplus[ret] == 'aslisk': proxies_tplus = '32'
    elif opciones_tplus[ret] == 'rdavydov socks4': proxies_tplus = '33'
    elif opciones_tplus[ret] == 'hookzof': proxies_tplus = '34'
    elif opciones_tplus[ret] == 'manuGMG': proxies_tplus = '35'
    elif opciones_tplus[ret] == 'rdavydov socks5': proxies_tplus = '36'
    elif opciones_tplus[ret] == 'lamt3012': proxies_tplus = '37'

    else: proxies_tplus = '32'

    config.set_setting('proxies_tplus', proxies_tplus)


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
        if item.unsatisfactory: text = '¿ Iniciar Test Web de los Posibles Canales Insatisfactorios ?'
        else: text = '¿ Iniciar Test Web de Todos los Canales ?'

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
                     continue
            else: continue

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
                             continue
	
                        if not 'code: [COLOR springgreen][B]200' in str(txt):
                            if ' con proxies ' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                        else:
                            rememorize = True

                elif 'Sin proxies' in str(txt):
                    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR chartreuse][B]Quizás necesite Proxies.[/B][/COLOR] ¿ Desea Iniciar la Búsqueda de Proxies en el Canal ?'):
                        _proxies(item, ch['id'])

                        try: txt = tester.test_channel(ch['name'])
                        except:
                             platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                             continue

                        if not 'code: [COLOR springgreen][B]200' in str(txt):
                            if 'Sin proxies' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                        else:
                            rememorize = True

                if 'invalid:' in str(txt):
                    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '¿ Desea comprobar el Canal de nuevo, [COLOR red][B]por Acceso sin Host Válido en los datos. [/B][/COLOR]?'):
                        try: txt = tester.test_channel(ch['name'])
                        except:
                             platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                             continue

                        if 'code: [COLOR springgreen][B]200' in str(txt):
                            if 'invalid:' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado el Acceso sin Host Válido en los datos.[/B][/COLOR]')

            elif 'Falso Positivo.' in str(txt):
                platformtools.dialog_textviewer(ch['name'], txt)

                if ' con proxies ' in str(txt):
                    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]¿ Desea Iniciar una nueva Búsqueda de Proxies en el Canal ?[/B][/COLOR]'):
                        _proxies(item, ch['id'])

                        try: txt = tester.test_channel(ch['name'])
                        except:
                              platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                              continue
	
                        if not 'code: [COLOR springgreen][B]200' in str(txt):
                            if ' con proxies ' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                        else:
                            rememorize = True

                elif 'Sin proxies' in str(txt):
                    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR chartreuse][B]Quizás necesite Proxies.[/B][/COLOR] ¿ Desea Iniciar la Búsqueda de Proxies en el Canal ?'):
                        _proxies(item, ch['id'])

                        try: txt = tester.test_channel(ch['name'])
                        except:
                             platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                             continue

                        if not 'code: [COLOR springgreen][B]200' in str(txt):
                            if 'Sin proxies' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                        else:
                            rememorize = True

                if 'Falso Positivo.' in str(txt):
                    if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '¿ Desea comprobar el Canal de nuevo, [COLOR red][B]por Falso Positivo. [/B][/COLOR]?'):
                        try: txt = tester.test_channel(ch['name'])
                        except:
                             platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                             continue

                        if 'code: [COLOR springgreen][B]200' in str(txt):
                            if 'Falso Positivo.' in str(txt):
                                platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado el Falso Positivo.[/B][/COLOR]')

            if ' al parecer No se necesitan' in str(txt):
                if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]¿ Desea Quitar los Proxies del Canal ?[/B][/COLOR], porqué parece que NO se necesitan.'):
                    _quitar_proxies(item, ch['id'])

                    try: txt = tester.test_channel(ch['name'])
                    except:
                         platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
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
           if 'code: [COLOR [COLOR orangered][B]301' in str(txt) or 'code: [COLOR [COLOR orangered][B]308' in str(txt): continue

           if 'code: [COLOR [COLOR orangered][B]302' in str(txt) or 'code: [COLOR [COLOR orangered][B]307' in str(txt): continue

           if 'Podría estar Correcto' in str(txt): continue

           if ' con proxies ' in str(txt):
               if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]¿ Desea Iniciar una nueva Búsqueda de Proxies en el Canal ?[/B][/COLOR]'):
                   _proxies(item, ch['id'])

                   try: txt = tester.test_channel(ch['name'])
                   except:
                        platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                        continue
	
                   if not 'code: [COLOR springgreen][B]200' in str(txt):
                       if ' con proxies ' in str(txt):
                           platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                   else:
                       rememorize = True

           elif 'Sin proxies' in str(txt):
               if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR chartreuse][B]Quizás necesite Proxies.[/B][/COLOR] ¿ Desea Iniciar la Búsqueda de Proxies en el Canal ?'):
                   _proxies(item, ch['id'])

                   try: txt = tester.test_channel(ch['name'])
                   except:
                        platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B] ' + ch['name'] + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Canal Ignorado[/B][/COLOR]' % color_alert)
                        continue

                   if not 'code: [COLOR springgreen][B]200' in str(txt):
                       if 'Sin proxies' in str(txt):
                           platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + ch['name'] + '[/B][/COLOR]', '[COLOR red][B]No se ha solucionado Buscando Nuevos Proxies.[/B][/COLOR]')
                   else:
                       rememorize = True

        if rememorize:
            proxies = config.get_setting('proxies', ch['id'], default='').strip()

            if proxies:
                if config.get_setting('memorize_channels_proxies', default=True):
                    channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')

                    el_memorizado = "'" + ch['id'] + "'"

                    if not el_memorizado in str(channels_proxies_memorized):
                        channels_proxies_memorized = channels_proxies_memorized + ', ' + el_memorizado
                        config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

    if i > 0: platformtools.dialog_ok(config.__addon_name, 'Canales Testeados ' + str(i))

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
        if item.unsatisfactory: text = '¿ Iniciar Test Web de los Posibles Servidores Insatisfactorios ?'
        else: text = '¿ Iniciar Test Web de Todos los Servidores ?'

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
                     continue
            else: continue

        if not txt: continue

    if i > 0: platformtools.dialog_ok(config.__addon_name, 'Servidores Testeados ' + str(i))

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
    temporarys = 0
    mismatcheds = 0
    inestables = 0
    problematics = 0
    notices = 0
    proxies = 0
    registers = 0
    dominios = 0
    currents = 0
    onlyones = 0
    searchables = 0
    status = 0

    bus_pelisyseries = 0
    bus_pelis = 0
    bus_series = 0
    bus_documentales = 0
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
            bus_documentales += 1
        else:
           if 'docs' in ch['clusters']:
               if ch['searchable']: bus_documentales += 1

        if 'infantil' in ch['clusters']: infantiles += 1

        if 'tales' in ch['clusters']: tales += 1

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
    txt += '       ' + str(temporarys) + ' [COLOR cyan]Temporalmente Inactivos[/COLOR][CR]'

    if not PY3: txt += '       ' + str(mismatcheds) + ' [COLOR violet]Posible Incompatibilidad[/COLOR][CR]'

    txt += '       ' + str(inestables) + ' [COLOR plum]Inestables[/COLOR][CR]'
    txt += '       ' + str(problematics) + ' [COLOR darkgoldenrod]Problemáticos[/COLOR][CR]'
    txt += '     ' + str(notices) + ' [COLOR olivedrab]CloudFlare Protection[/COLOR][CR]'
    txt += '     ' + str(proxies) + ' [COLOR red]Pueden Usar Proxies[/COLOR][CR]'
    txt += '       ' + str(registers) + ' [COLOR teal]Requieren Cuenta[/COLOR][CR]'
    txt += '       ' + str(dominios) + ' [COLOR green]Varios Dominios[/COLOR][CR]'
    txt += '     ' + str(currents) + ' [COLOR goldenrod]Gestión Dominio Vigente[/COLOR][CR]'
    txt += '     ' + str(onlyones) + ' [COLOR fuchsia]Con un Único Servidor[/COLOR][CR]'
    txt += '     ' + str(searchables) + ' [COLOR aquamarine]No Actuan en Búsquedas[/COLOR][CR]'

    path = os.path.join(config.get_runtime_path(), 'dominios.txt')

    existe = filetools.exists(path)

    if existe:
        txt_status = ''

        try:
           with open(os.path.join(config.get_runtime_path(), 'dominios.txt'), 'r') as f: txt_status=f.read(); f.close()
        except:
           try: txt_status = open(os.path.join(config.get_runtime_path(), 'dominios.txt'), encoding="utf8").read()
           except: pass

        if txt_status:
            bloque = scrapertools.find_single_match(txt_status, 'SITUACION CANALES(.*?)CANALES TEMPORALMENTE DES-ACTIVADOS')

            matches = bloque.count('[COLOR lime]')

            if matches:
                status = matches

                txt += '       ' + str(status) + ' [COLOR tan]Problemas Acceso Dominio[/COLOR][CR]'

    txt += '[CR]  ' + str(disponibles) + ' [COLOR gold][B]Disponibles[/B][/COLOR][CR]'

    if not status == 0:
        accesibles = (disponibles - status)
        txt += '  ' + str(accesibles) + ' [COLOR powderblue][B]Accesibles[/B][/COLOR][CR]'

    if not no_actives == 0: txt += '  ' + str(no_actives) + ' [COLOR gray][B]Desactivados[/B][/COLOR][CR]'

    txt += '[CR][COLOR dodgerblue][B]DISTRIBUCIÓN CANALES DISPONIBLES:[/B][/COLOR][CR]'

    txt += '  ' + str(suggesteds) + ' [COLOR moccasin]Sugeridos[/COLOR][CR]'

    txt += '[CR]  ' + str(peliculas) + ' [COLOR deepskyblue]Películas[/COLOR][CR]'

    txt += '  ' + str(series) + ' [COLOR hotpink]Series[/COLOR][CR]'

    txt += '  ' + str(pelisyseries) + ' [COLOR teal]Películas y Series[/COLOR][CR]'

    txt += '[CR]  ' + str(generos) + '  [COLOR thistle]Géneros[/COLOR][CR]'
    txt += '    ' + str(documentarys) + '  [COLOR cyan]Documentales[/COLOR][CR]'
    txt += '    ' + str(infantiles) + '  [COLOR lightyellow]Infantiles[/COLOR][CR]'
    txt += '  ' + str(tales) + '  [COLOR limegreen]Novelas[/COLOR][CR]'
    txt += '  ' + str(torrents) + ' [COLOR blue]Torrents[/COLOR][CR]'
    txt += '  ' + str(doramas) + '  [COLOR firebrick]Doramas[/COLOR][CR]'
    txt += '  ' + str(animes) + '  [COLOR springgreen]Animes[/COLOR][CR]'
    txt += '  ' + str(adults) + '  [COLOR orange]Adultos[/COLOR][CR]'

    txt += '[CR][COLOR powderblue][B]DISTRIBUCIÓN CANALES DISPONIBLES PARA BÚSQUEDAS:[/B][/COLOR][CR]'

    txt += '  ' + str(bus_pelis) + ' [COLOR deepskyblue]Películas[/COLOR][CR]'
    txt += '  ' + str(bus_series) + ' [COLOR hotpink]Series[/COLOR][CR]'
    txt += '  ' + str(bus_pelisyseries) + ' [COLOR teal]Películas y Series[/COLOR][CR]'
    txt += '  ' + str(bus_documentales) + ' [COLOR cyan]Temática Documental[/COLOR][CR]'
    txt += '  ' + str(bus_torrents) + ' [COLOR blue]Torrents[/COLOR][CR]'
    txt += '  ' + str(bus_doramas) + ' [COLOR firebrick]Temática Dorama[/COLOR][CR]'
    txt += '  ' + str(bus_animes) + ' [COLOR springgreen]Temática Anime[/COLOR][CR]'

    platformtools.dialog_textviewer('Resúmenes de Canales y su Distribución', txt)


def resumen_servidores(item):
    logger.info()

    from core import jsontools

    total = 0
    inactives = 0
    notsuported = 0
    alternatives = 0
    aditionals = 35
    disponibles = 0

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

        if not dict_server['name'] == 'various':
            if "alternative" in notes.lower(): alternatives += 1

    txt = '[COLOR yellow][B]RESÚMENES SERVIDORES:[/B][/COLOR][CR]'

    txt += '  ' + str(total) + ' [COLOR darkorange][B]Servidores[/B][/COLOR][CR][CR]'

    txt += '    ' + str(inactives) + '  [COLOR coral]Inactivos[/COLOR][CR]'
    txt += '    ' + str(notsuported) + '  [COLOR fuchsia]Sin Soporte[/COLOR][CR]'

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        txt += '[CR][COLOR gold][B]RESOLVEURL:[/B][/COLOR][CR]'

        txt += '    ' + str(alternatives) + '  [COLOR green]Vías alternativas[/COLOR][CR]'
        txt += '    ' + str(aditionals) + '  [COLOR powderblue]Vías Adicionales[/COLOR][CR]'

    txt += '[CR]  ' + str(disponibles) + '  [COLOR gold][B]Disponibles[/B][/COLOR]'

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        accesibles = (disponibles + aditionals)
        txt += '[CR]  ' + str(accesibles) + '  [COLOR powderblue][B]Accesibles[/B][/COLOR]'

    platformtools.dialog_textviewer('Resúmenes Servidores y su Distribución', txt)


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
    txt += '   [COLOR yellow]Doodstream[/COLOR][CR]'
    txt += '   [COLOR yellow]Gofile[/COLOR][CR]'
    txt += '   [COLOR yellow]MegaUp[/COLOR][CR]'
    txt += '   [COLOR yellow]Playtube[/COLOR][CR]'
    txt += '   [COLOR yellow]Racaty[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamlare[/COLOR][CR]'
    txt += '   [COLOR yellow]Uptobox[/COLOR][CR]'
    txt += '   [COLOR yellow]Various[/COLOR][CR]'
    txt += '   [COLOR yellow]Vk[/COLOR][CR]'
    txt += '   [COLOR yellow]Waaw[/COLOR][CR]'

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
    txt += '   [COLOR yellow]Fastupload[/COLOR][CR]'
    txt += '   [COLOR yellow]Filelions[/COLOR][CR]'
    txt += '   [COLOR yellow]Filemoon[/COLOR][CR]'
    txt += '   [COLOR yellow]Fileupload[/COLOR][CR]'
    txt += '   [COLOR yellow]Hxfile[/COLOR][CR]'
    txt += '   [COLOR yellow]Hexupload[/COLOR][CR]'
    txt += '   [COLOR yellow]Krakenfiles[/COLOR][CR]'
    txt += '   [COLOR yellow]Lulustream[/COLOR][CR]'
    txt += '   [COLOR yellow]Moonmov[/COLOR][CR]'
    txt += '   [COLOR yellow]Moonplayer[/COLOR][CR]'
    txt += '   [COLOR yellow]Mvidoo[/COLOR][CR]'
    txt += '   [COLOR yellow]Rutube[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamhub[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamvid[/COLOR][CR]'
    txt += '   [COLOR yellow]Streamwish[/COLOR][CR]'
    txt += '   [COLOR yellow]Tubeload[/COLOR][CR]'
    txt += '   [COLOR yellow]Twitch[/COLOR][CR]'
    txt += '   [COLOR yellow]Uploaddo[/COLOR][CR]'
    txt += '   [COLOR yellow]Uploadever[/COLOR][CR]'
    txt += '   [COLOR yellow]Uploadraja[/COLOR][CR]'
    txt += '   [COLOR yellow]Userload[/COLOR][CR]'
    txt += '   [COLOR yellow]Vidello[/COLOR][CR]'
    txt += '   [COLOR yellow]Videowood[/COLOR][CR]'
    txt += '   [COLOR yellow]Vidguard[/COLOR][CR]'
    txt += '   [COLOR yellow]Vidspeed[/COLOR][CR]'
    txt += '   [COLOR yellow]Vidhidepro[/COLOR][CR]'
    txt += '   [COLOR yellow]Vkspeed[/COLOR][CR]'
    txt += '   [COLOR yellow]Vudeo[/COLOR][CR]'
    txt += '   [COLOR yellow]Yandex[/COLOR][CR]'
    txt += '   [COLOR yellow]Youdbox[/COLOR]'

    platformtools.dialog_textviewer('Servidores Vías Adicionales', txt)
