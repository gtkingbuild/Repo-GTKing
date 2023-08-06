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


import os, re, time, xbmcaddon

import xbmc, xbmcgui, platform

from platformcode import config, logger, platformtools, updater
from core.item import Item
from core import channeltools, filetools, servertools, httptools, scrapertools

from modules import filters


ADDON_REPO_ADDONS = 'https://balandro-tk.github.io/balandro/'
ADDON_UPDATES_JSON = 'https://raw.githubusercontent.com/balandro-tk/addon_updates/main/updates.json'

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')

descartar_xxx = config.get_setting('descartar_xxx', default=False)
descartar_anime = config.get_setting('descartar_anime', default=False)

_foro = "[COLOR plum][B][I] www.mimediacenter.info/foro/ [/I][/B][/COLOR]"
_source = "[COLOR coral][B][I] https://balandro-tk.github.io/balandro/ [/I][/B][/COLOR]"
_scripts = "[COLOR mediumaquamarine][B][I] https://balandro-tk.github.io/balandro/scripts/ [/I][/B][/COLOR]"
_telegram = "[COLOR lightblue][B][I] t.me/balandro_asesor [/I][/B][/COLOR]"

_team = "[COLOR hotpink][B][I] t.me/Balandro_team [/I][/B][/COLOR]"


context_temas = []

tit = '[COLOR red][B]Temas NO Contemplados[/B][/COLOR]'
context_temas.append({'title': tit, 'channel': 'helper', 'action': 'show_not_contemplated'})

tit = '[COLOR yellowgreen][B]Preguntas Frecuentes[/B][/COLOR]'
context_temas.append({'title': tit, 'channel': 'helper', 'action': 'show_help_faq'})

tit = '[COLOR seagreen][B]Trucos y Consejos[/B][/COLOR]'
context_temas.append({'title': tit, 'channel': 'helper', 'action': 'show_help_tips'})

tit = '[COLOR limegreen][B]Ejemplos de Uso[/B][/COLOR]'
context_temas.append({'title': tit, 'channel': 'helper', 'action': 'show_help_use'})

tit = '[COLOR green][B]Apuntes sobre Parámetros[/B][/COLOR]'
context_temas.append({'title': tit, 'channel': 'helper', 'action': 'show_help_settings'})

tit = '[COLOR %s]Ajustes Configuración[/COLOR]' % color_exec
context_temas.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='submnu_contacto', title= '[B]CONTACTO[/B]', text_color='limegreen', thumbnail=config.get_thumb('pencil') ))
    itemlist.append(item.clone( action='submnu_fuente', title= '[B]FUENTE[/B]', text_color='tomato', thumbnail=config.get_thumb('pencil') ))
    itemlist.append(item.clone( action='show_help_miscelanea', title= '[B]MISCELÁNEA[/B]', text_color='goldenrod', thumbnail=config.get_thumb('booklet') ))

    itemlist.append(item.clone( action='', title= '[B]AYUDA TEMAS:[/B]', context=context_temas, text_color='lightyellow', folder=False ))

    itemlist.append(item.clone( action='submnu_uso', title= ' - [B]USO[/B]', text_color='darkorange', thumbnail=config.get_thumb('addon') ))
    itemlist.append(item.clone( action='submnu_menus', title= ' - [B]MENÚS[/B]', text_color='chartreuse', thumbnail=config.get_thumb('dev') ))
    itemlist.append(item.clone( action='submnu_canales', title= ' - [B]CANALES[/B]', text_color='gold', thumbnail=config.get_thumb('stack') ))

    if not config.get_setting('mnu_simple', default=False):
        itemlist.append(item.clone( action='submnu_parental', title= ' - [B]PARENTAL[/B]', text_color='orange', thumbnail=config.get_thumb('roadblock') ))

    itemlist.append(item.clone( action='submnu_domains', title= ' - [B]DOMINIOS[/B]', text_color='bisque', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='submnu_audios', title=' - [B]AUDIOS[/B]', text_color='limegreen', thumbnail=config.get_thumb('idiomas') ))
    itemlist.append(item.clone( action='submnu_play', title=' - [B]PLAY [COLOR powderblue]Servidores[/B]', text_color='fuchsia', thumbnail=config.get_thumb('bolt') ))
    itemlist.append(item.clone( action='submnu_proxies', title= ' - [B]PROXIES[/B]', text_color='red', thumbnail=config.get_thumb('flame') ))
    itemlist.append(item.clone( action='submnu_torrents', title= ' - [B]TORRENTS[/B]', text_color='blue', thumbnail=config.get_thumb('torrents') ))
    itemlist.append(item.clone( action='submnu_buscar', title=' - [B]BUSCAR[/B]', text_color='yellow', thumbnail=config.get_thumb('magnifyingglass') ))

    presentar = True
    if config.get_setting('mnu_simple', default=False): presentar = False
    else:
       if not config.get_setting('mnu_preferidos', default=True): presentar = False

    if presentar:
        itemlist.append(item.clone( action='submnu_preferidos', title=' - [B]PREFERIDOS[/B]', text_color='wheat', thumbnail=config.get_thumb('videolibrary') ))

    presentar = True
    if config.get_setting('mnu_simple', default=False): presentar = False
    else:
       if not config.get_setting('mnu_desargas', default=True): presentar = False

    if presentar:
        itemlist.append(item.clone( action='submnu_descargas', title=' - [B]DESCARGAS[/B]', text_color='seagreen', thumbnail=config.get_thumb('download') ))

    itemlist.append(item.clone( action='submnu_config', title=' - [B]CONFIGURACIÓN[/B]', text_color='chocolate', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='submnu_actualizar', title=' - [B]ACTUALIZAR [COLOR powderblue]Fixes[/B]', text_color='cyan', thumbnail=config.get_thumb('addon') ))
    itemlist.append(item.clone( action='submnu_mediacenter', title= ' - [B]MEDIA CENTER[/B]', text_color='pink', thumbnail=config.get_thumb('computer') ))
    itemlist.append(item.clone( action='submnu_sistema', title= ' - [B]SISTEMA[/B]', text_color='teal', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( action='submnu_clean', title= ' - [B]LIMPIEZAS[/B]', text_color='olive', thumbnail=config.get_thumb('quote') ))
    itemlist.append(item.clone( action='submnu_version', title=' - [B]VERSIONES[/B]', text_color='violet', thumbnail=config.get_thumb('addon') ))
    itemlist.append(item.clone( action='submnu_desarrollo', title=' - [B]DESARROLLO [COLOR powderblue]Team[/B]', text_color='firebrick', thumbnail=config.get_thumb('team') ))
    itemlist.append(item.clone( action='submnu_legalidad', title=' - [B]LEGALIDAD[/B]', text_color='crimson', thumbnail=config.get_thumb('roadblock') ))

    return itemlist

def submnu_contacto(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]CONTACTO:[/B]', text_color='limegreen', folder=False, thumbnail=config.get_thumb('pencil') ))

    itemlist.append(item.clone( action='', title= ' - Foro ' + _foro + ' Instalaciones, Novedades, Sugerencias, etc.', thumbnail=config.get_thumb('foro'), folder=False ))
    itemlist.append(item.clone( action='', title= ' - Telegram ' + _telegram + ' Asesoramiento, Dudas, Consultas, etc.', thumbnail=config.get_thumb('telegram'), folder=False ))

    itemlist.append(item.clone( action='', title= ' - Team ' + _team + ' Equipo de Desarrollo', thumbnail=config.get_thumb('team'), folder=False ))

    return itemlist


def submnu_fuente(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]FUENTE:[/B]', text_color='tomato', folder=False, thumbnail=config.get_thumb('pencil') ))

    itemlist.append(item.clone( action='', title= ' - Fuente ' + _source + ' Repositorio, Add-On, Scripts', thumbnail=config.get_thumb('repo'), folder=False ))

    itemlist.append(item.clone( action='', title= '[B]SCRIPTS:[/B]', text_color='tomato', folder=False, thumbnail=config.get_thumb('pencil') ))

    itemlist.append(item.clone( action='', title= ' - Fuente ' + _scripts, thumbnail=config.get_thumb('repo'), folder=False ))

    itemlist.append(item.clone( action='', title= '   - Carpeta Kodi18: Repo ResolveUrl y Plugin Youtube hasta 18.x', thumbnail=config.get_thumb('repo'), folder=False ))

    itemlist.append(item.clone( action='', title= '   - Carpeta Kodi19: Repo ResolveUrl y Plugin Youtube desde 19.x', thumbnail=config.get_thumb('repo'), folder=False ))

    return itemlist


def submnu_uso(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]USO:[/B]', text_color='darkorange', folder=False, thumbnail=config.get_thumb('addon') ))

    itemlist.append(item.clone( action='show_not_contemplated', title= ' - ¿ Qué [COLOR goldenrod][B]NO[/B][/COLOR] está contemplado en Balandro ?', thumbnail=config.get_thumb('roadblock') ))
    itemlist.append(item.clone( action='show_help_faq', title= ' - Preguntas Frecuentes' ))
    itemlist.append(item.clone( action='show_help_tips', title= ' - Trucos y Consejos' ))
    itemlist.append(item.clone( action='show_help_use', title= ' - Ejemplos de Uso' ))
    itemlist.append(item.clone( action='show_help_settings', title= ' - Apuntes sobre ciertos Parámetros de la configuración', thumbnail=config.get_thumb('pencil') ))
    itemlist.append(item.clone( action='show_server_report', title= ' - Como [COLOR cyan][B]Reportar[/B][/COLOR] posible Fallo en la Reproducción de Servidores', thumbnail=config.get_thumb('telegram') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] Configuración', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_menus(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]MENÚS:[/B]', text_color='chartreuse', folder=False, thumbnail=config.get_thumb('dev') ))

    itemlist.append(item.clone( action='show_menu_parameters', title= ' - [COLOR green][B]Información[/B][/COLOR] sobre sus [COLOR chocolate][B]Parámetros[/B][/COLOR] Actuales', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR chartreuse][B]Menú[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_canales(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]CANALES:[/B]', text_color='gold', folder=False, thumbnail=config.get_thumb('stack') ))

    if config.get_setting('developer_mode', default=False):
        itemlist.append(item.clone( action='show_channels_list', title= ' - [COLOR gold][B]Todos[/B][/COLOR] los Canales', tipo = 'all', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='show_channels_parameters', title=' - Qué [COLOR chocolate][B]Ajustes[/B][/COLOR] tiene configurados para Mostrar los Canales', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='show_channels_list', title= ' - Qué canales están [COLOR gold][B]Disponibles[/B][/COLOR] (Activos)', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= ' - Qué canales están [COLOR aquamarine][B]Sugeridos[/B][/COLOR]', suggesteds = True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='', title= '[B]CANALES [COLOR powderblue]Personalización[/COLOR]:[/B]', text_color='goldenrod', folder=False, thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='channels_prefered', title= '    - Qué canales tiene marcados como [COLOR gold][B]Preferidos[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_status', title= '    - Personalizar canales Preferidos [COLOR gold][B](Marcar ó Des-marcar)[/B][/COLOR]', des_rea = False, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_no_actives', title= '    - Qué canales tiene marcados como [COLOR gray][B]Desactivados[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_status', title= '    - Personalizar canales [COLOR gray][B](Desactivar ó Re-activar)[/B][/COLOR]', des_rea = True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='', title= '[B]CANALES [COLOR powderblue]Cuentas[/COLOR]:[/B]', text_color='goldenrod', folder=False, thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_help_register', title= '    - [COLOR green][B]Información[/B][/COLOR] webs que requieren [COLOR gold][B]Registrarse[/B][/COLOR] (Cuenta)', thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales requieren [COLOR teal][B]Cuenta[/B][/COLOR]', cta_register = True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='', title= '[B]CANALES [COLOR powderblue]Situación[/COLOR]:[/B]', text_color='goldenrod', folder=False, thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='submnu_avisinfo_channels', title= '    - [COLOR aquamarine][B]Avisos[/COLOR] [COLOR green]Información[/B][/COLOR] canales', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='channels_with_notice', title= '    - Qué canales tienen [COLOR green][B]Aviso[/COLOR][COLOR red] CloudFlare [COLOR orangered]Protection[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_with_proxies', title= '    - Qué canales pueden necesitar [COLOR red][B]Proxies[/B][/COLOR]', new_proxies=True, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales están [COLOR plum][B]Inestables[/B][/COLOR]', no_stable = True, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales son [COLOR darkgoldenrod][B]Problemátios[/B][/COLOR] (Predominan Sin enlaces Disponibles/Válidos/Soportados)', problematics = True, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales están [COLOR cyan][B]Temporalmente[/B][/COLOR] inactivos', temp_no_active = True, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales son [COLOR grey][B]Privados[/B][/COLOR]', tipo = 'all', privates = True, thumbnail=config.get_thumb('stack') ))

    if not PY3:
        itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales son [COLOR violet][B]Incompatibiles[/B][/COLOR] con su Media Center', mismatched = True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales están [COLOR coral][B]Inactivos[/B][/COLOR]', no_active = True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categorías [COLOR gold][B]Canales, Dominios y Cuentas[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist

def submnu_avisinfo_channels(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]AVISOS INFORMACIÓN CANALES:[/B]', text_color='gold', folder=False, thumbnail=config.get_thumb('stack') ))

    datos = channeltools.get_channel_parameters('hdfull')
    if datos['active']:
        itemlist.append(item.clone( action='show_help_hdfull', title= ' - [COLOR aquamarine][B]Aviso[/COLOR] [COLOR green][B]Información[/B][/COLOR] canal [COLOR yellow][B]HdFull[/B][/COLOR]', thumbnail=config.get_thumb('hdfull', 'thumb', 'channels') ))

    datos = channeltools.get_channel_parameters('playdede')
    if datos['active']:
        itemlist.append(item.clone( action='show_help_playdede', title= ' - [COLOR aquamarine][B]Aviso[/COLOR] [COLOR green][B]Información[/B][/COLOR] canal [COLOR yellow][B]PlayDede[/B][/COLOR]', thumbnail=config.get_thumb('playdede', 'thumb', 'channels') ))

    itemlist.append(item.clone( action='show_help_resto', title= ' - Posible [COLOR aquamarine][B]Aviso[/COLOR] [COLOR green][B]Información[/B][/COLOR] en el resto de los [COLOR gold][B]Canales[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

    return itemlist


def submnu_parental(item):
    logger.info()
    itemlist = []

    presentar = True
    if descartar_xxx:
        if descartar_anime: presentar = False

    itemlist.append(item.clone( action='', title= '[B]PARENTAL:[/B]', text_color='orange', folder=False, thumbnail=config.get_thumb('roadblock') ))

    itemlist.append(item.clone( action='show_menu_parameters', title= '[COLOR green][B]Información[/B][/COLOR] sobre sus [COLOR chocolate][B]Parámetros[/B][/COLOR] Actuales', thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( action='show_help_adults', title= '[COLOR green][B]Información[/B][/COLOR] Control parental (+18)', thumbnail=config.get_thumb('news') ))

    if presentar:
        if config.get_setting('mnu_animes', default=True):
            if not descartar_anime:
                itemlist.append(item.clone( action='', title= '[B]CANALES [COLOR powderblue]con Animes[/COLOR]:[/B]', text_color='orange', folder=False, thumbnail=config.get_thumb('anime') ))

                itemlist.append(item.clone( action='channels_only_animes', title= '   - Qué canales pueden tener contenido de Animes', thumbnail=config.get_thumb('anime') ))
                itemlist.append(item.clone( action='channels_exclusively_animes', title= '   - Qué canales tienen contenido Exclusivamente de [COLOR springgreen][B]Animes[/B][/COLOR]', thumbnail=config.get_thumb('anime') ))

        if config.get_setting('mnu_adultos', default=True):
            if not descartar_xxx:
                itemlist.append(item.clone( action='', title= '[B]CANALES [COLOR powderblue]con vídeos para Adultos[/COLOR]:[/B]', text_color='orange', folder=False, thumbnail=config.get_thumb('adults') ))

                itemlist.append(item.clone( action='channels_only_adults', title= '   - Qué canales pueden tener contenido para Adultos', thumbnail=config.get_thumb('adults') ))
                itemlist.append(item.clone( action='channels_exclusively_adults', title= '   - Qué canales tienen contenido Exclusivamente para [COLOR orange][B]Adultos[/B][/COLOR]', thumbnail=config.get_thumb('adults') ))

    if config.get_setting('adults_password', default=''):
        itemlist.append(item.clone( action='', title= '[COLOR red][B]Tiene informado PIN control parental[/B][/COLOR]', folder=False, thumbnail=config.get_thumb('roadblock') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR orange][B]Parental[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_domains(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]DOMINIOS:[/B]', text_color='bisque', folder=False, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='actions', action='show_latest_domains', title= ' - [COLOR cyan][B]Últimos Cambios[/B][/COLOR] de Dominios', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( action='show_help_domains', title= ' - [COLOR green][B]Información[/B][/COLOR] Dominios', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales tienen varios [COLOR gold][B]Dominios[/B][/COLOR]', var_domains = True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='show_channels_list', title= '    - En qué canales se puede gestionar el [COLOR gold][B]Último dominio Vigente[/B][/COLOR]', last_domain = True, thumbnail=config.get_thumb('roadblock') ))

    itemlist.append(item.clone( action='channels_only_last_domain', title= '    - En qué canales tiene informado el [COLOR yellow][B]Último dominio Vigente[/B][/COLOR]', thumbnail=config.get_thumb('roadblock') ))

    itemlist.append(item.clone( channel='actions', action='manto_domains', title= '    - Quitar los Dominios en los canales [COLOR darkorange][B](que los tengan Memorizados)[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR gold][B]Dominios[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_audios(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]AUDIOS:[/B]', folder=False, text_color='limegreen', thumbnail=config.get_thumb('idiomas') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR fuchsia][B]Play[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_play(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]PLAY [COLOR powderblue]SERVIDORES[/COLOR]:[/B]', folder=False, text_color='fuchsia', thumbnail=config.get_thumb('bolt') ))

    if config.get_setting('developer_mode', default=False):
        itemlist.append(item.clone( action='show_servers_list', title= ' - [COLOR darkorange][B]Todos[/B][/COLOR] los Servidores', tipo = 'all', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( action='show_server_report', title= ' - Como [COLOR deepskyblue][B]Reportar[/B][/COLOR] posible Fallo en la Reproducción de Servidores', thumbnail=config.get_thumb('telegram') ))

    itemlist.append(item.clone( action='show_play_parameters', title=' - Qué [COLOR chocolate][B]Ajustes[/B][/COLOR] tiene configurados en [COLOR fuchsia][B]Play[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='show_help_recaptcha', title= ' - ¿ Qué significa Requiere verificación [COLOR red][B]reCAPTCHA[/B][/COLOR] ?', thumbnail=config.get_thumb('roadblock') ))
    itemlist.append(item.clone( action='show_help_acortador', title= ' - ¿ Qué significa Tiene [COLOR plum][B]Acortador[/B][/COLOR] del enlace ?', thumbnail=config.get_thumb('roadblock') ))

    itemlist.append(item.clone( action='show_servers_list', title= ' - Qué servidores están [COLOR darkorange][B]Disponibles[/B][/COLOR] (Activos)', tipo = 'activos', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( action='', title= '[B]PLAY [COLOR powderblue]Servidores Vías Alternativas[/COLOR]:[/B]', folder=False, text_color='orchid', thumbnail=config.get_thumb('settings') ))

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        cod_version = xbmcaddon.Addon("script.module.resolveurl").getAddonInfo("version").strip()
        tex_yt = '  ' + cod_version
    else: tex_yt = '  [COLOR red]No instalado[/COLOR]'

    itemlist.append(item.clone( action = '', title= ' [COLOR goldenrod][B]ResolveUrl[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_yt + '[/B][/COLOR]', thumbnail=config.get_thumb('resolveurl') ))

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
        cod_version = xbmcaddon.Addon("plugin.video.youtube").getAddonInfo("version").strip()
        tex_yt = '  ' + cod_version
    else: tex_yt = '  [COLOR red]No instalado[/COLOR]'

    itemlist.append(item.clone( action = '', title= ' [COLOR goldenrod][B]Youtube[/B][/COLOR]' + '[COLOR yellowgreen][B] ' + tex_yt + '[/B][/COLOR]', thumbnail=config.get_thumb('youtube') ))


    itemlist.append(item.clone( action='show_help_vias', title= ' - ¿ Dónde obtener Add-Ons para Vías Alternativas ?', thumbnail=config.get_thumb('telegram') ))

    itemlist.append(item.clone( action='show_help_vias', title= ' - [COLOR green][B]Información[/B][/COLOR] vía alternativa [COLOR goldenrod][B]ResolveUrl[/B][/COLOR]', thumbnail=config.get_thumb('resolveurl') ))
    itemlist.append(item.clone( action='show_help_vias', title= ' - [COLOR green][B]Información[/B][/COLOR] vía alternativa [COLOR goldenrod][B]Youtube[/B][/COLOR]', thumbnail=config.get_thumb('youtube') ))

    itemlist.append(item.clone( action='show_servers_list', title= '    - Qué servidores tienen [COLOR yellow][B]Vías Alternativas[/B][/COLOR]', tipo = 'alternativos', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( action='', title= '[B]PLAY [COLOR powderblue]Servidores Situación[/COLOR]:[/B]', folder=False, text_color='orchid', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='submnu_avisinfo_servers', title= '    - [COLOR aquamarine][B]Avisos[/COLOR] [COLOR green]Información[/B][/COLOR] servidores', thumbnail=config.get_thumb('bolt') ))
    itemlist.append(item.clone( action='show_servers_list', title= '    - Qué servidores se detectan pero [COLOR fuchsia][B]No están Soportados[/B][/COLOR]', tipo = 'sinsoporte', thumbnail=config.get_thumb('roadblock') ))
    itemlist.append(item.clone( action='show_servers_list', title= '    - Qué servidores están [COLOR coral][B]Inactivos[/B][/COLOR]', tipo = 'inactivos', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR fuchsia][B]Play[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_avisinfo_servers(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]AVISOS INFORMACIÓN SERVIDORES:[/B]', text_color='gold', folder=False, thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( action='show_help_gamovideo', title= ' - [COLOR green][B]Información[/B][/COLOR] servidor [COLOR darkorange][B]Gamovideo[/B][/COLOR]', thumbnail=config.get_thumb('gamovideo') ))

    itemlist.append(item.clone( action='show_help_mega', title= ' - [COLOR green][B]Información[/B][/COLOR] servidor [COLOR darkorange][B]Mega[/B][/COLOR]', thumbnail=config.get_thumb('mega') ))

    itemlist.append(item.clone( action='show_help_uptobox', title= ' - [COLOR green][B]Información[/B][/COLOR] servidor [COLOR darkorange][B]Uptobox[/B][/COLOR]', thumbnail=config.get_thumb('uptobox') ))

    return itemlist


def submnu_proxies(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]PROXIES:[/B]', folder=False, text_color='red', thumbnail=config.get_thumb('flame') ))

    itemlist.append(item.clone( action='show_prx_parameters', title= ' - [COLOR green][B]Información[/B][/COLOR] sobre sus [COLOR chocolate][B]Parámetros[/B][/COLOR] Actuales', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( action='show_help_proxies', title= ' - [COLOR green][B]Información[/B][/COLOR] Uso de proxies', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_help_providers', title= ' - [COLOR green][B]Información[/B][/COLOR] Proveedores de proxies', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_help_providers2', title= ' - [COLOR green][B]Información[/B][/COLOR] Lista [COLOR aqua][B]Ampliada[/B][/COLOR] de Proveedores de proxies', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_help_recommended', title= ' - Qué Proveedores de proxies están [COLOR lime][B]Recomendados[/B][/COLOR]', thumbnail=config.get_thumb('flame') ))

    path = os.path.join(config.get_data_path(), 'Lista-proxies.txt')

    existe = filetools.exists(path)

    if existe:
        itemlist.append(item.clone( action='show_yourlist', title= ' - [COLOR green][B]Información[/B][/COLOR] de su Fichero Lista de proxies [COLOR gold][B](Lista-proxies.txt)[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='channels_with_proxies', title= ' - Qué canales pueden usar Proxies', new_proxies=True, test_proxies=True, thumbnail=config.get_thumb('stack') ))

    if config.get_setting('memorize_channels_proxies', default=True):
        itemlist.append(item.clone( action='channels_with_proxies_memorized', title= ' - Qué [COLOR red]canales[/COLOR] tiene con proxies [COLOR red][B]Memorizados[/B][/COLOR]',
                                    new_proxies=True, memo_proxies=True, test_proxies=True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='actions', action = 'manto_proxies', title= ' - Quitar los proxies en los canales [COLOR red][B](que los tengan Memorizados)[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='actions', action = 'global_proxies', title = ' - Configurar proxies a usar [COLOR plum][B](en los canales que los necesiten)[/B][/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR red][B]Proxies[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_torrents(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]TORRENTS:[/B]', folder=False, text_color='blue', thumbnail=config.get_thumb('torrents') ))

    cliente_torrent = config.get_setting('cliente_torrent', default='Seleccionar')

    if cliente_torrent == 'Seleccionar' or cliente_torrent == 'Ninguno': tex_tor = cliente_torrent
    else:
      tex_tor = cliente_torrent
      cliente_torrent = 'plugin.video.' + cliente_torrent.lower()
      if xbmc.getCondVisibility('System.HasAddon("%s")' % cliente_torrent):
          cod_version = xbmcaddon.Addon(cliente_torrent).getAddonInfo("version").strip()
          tex_tor += '  [COLOR yellowgreen]' + cod_version + '[/COLOR]'

    itemlist.append(item.clone( action = '', title= 'Cliente/Motor Habitual asignado ' + '[COLOR fuchsia][B] ' + tex_tor + '[/B][/COLOR]', thumbnail=config.get_thumb('torrents') ))

    itemlist.append(item.clone( action='show_help_torrents', title= ' - ¿ Dónde obtener los Clientes/Motores para torrents (Add-Ons) ?', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( action='show_clients_torrent', title= ' - Clientes/Motores externos torrent [COLOR gold][B]Soportados[/B][/COLOR]', thumbnail=config.get_thumb('cloud') ))

    if PY3:
        itemlist.append(item.clone( action='show_help_elementum', title= ' - [COLOR green][B]Información[/B][/COLOR] Motor Torrent [COLOR goldenrod][B]Elementum[/B][/COLOR]', thumbnail=config.get_thumb('elementum') ))

    itemlist.append(item.clone( action='channels_only_torrents', title= ' - Qué canales pueden contener archivos Torrent', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_exclusively_torrents', title= ' - Qué canales tienen enlaces Torrent [COLOR goldenrod][B]Exclusivamente[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_help_semillas', title= ' - [COLOR green][B]Información[/B][/COLOR] archivos Torrent [COLOR gold][B]Semillas[/B][/COLOR]' ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR blue][B]Torrents[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_buscar(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]BUSCAR:[/B]', folder=False, text_color='yellow', thumbnail=config.get_thumb('magnifyingglass') ))

    itemlist.append(item.clone( channel='search', action='show_help', title = ' - [COLOR green][B]Información[/B][/COLOR] sobre Búsquedas' ))
    itemlist.append(item.clone( channel='tmdblists', action='show_help', title= ' - [COLOR green][B]Información[/B][/COLOR] Búsquedas y Listas en TMDB' ))
    itemlist.append(item.clone( channel='search', action='show_help_parameters', title=' - Qué [COLOR chocolate][B]Ajustes[/B][/COLOR] tiene configurados para las búsquedas', thumbnail=config.get_thumb('settings') ))

    if config.get_setting('search_show_last', default=True):
        itemlist.append(item.clone( channel='actions', action = 'manto_textos', title= ' - Quitar los [COLOR red]Textos Memorizados[/COLOR] de las búsquedas', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='channels_no_searchables', title= ' - Qué canales [COLOR goldenrod][B]Nunca[/B][/COLOR] intervendrán en las búsquedas', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_no_actives', title= ' - Qué canales no intervienen en las búsquedas [COLOR gray][B]Desactivados[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( channel='actions', action = 'global_proxies', title = ' - Configurar Proxies a usar [COLOR plum](en los canales que los necesiten)[/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='filters', title = ' - [COLOR greenyellow][B]Efectuar las búsquedas Solo en determinados canales[/B][/COLOR]', action = 'mainlist2', thumbnail=config.get_thumb('settings') ))

    txt_exc = ''

    if config.get_setting('search_excludes_movies', default=''): txt_exc += '[COLOR deepskyblue][B]Películas[/B][/COLOR] '
    if config.get_setting('search_excludes_tvshows', default=''): txt_exc += '[COLOR hotpink][B]Series[/B][/COLOR] '
    if config.get_setting('search_excludes_documentaries', default=''): txt_exc += '[COLOR cyan][B]Documentales[/B][/COLOR] '
    if config.get_setting('search_excludes_torrents', default=''): txt_exc += '[COLOR blue][B]Torrents[/B][/COLOR] '
    if config.get_setting('search_excludes_mixed', default=''): txt_exc += '[COLOR yellow][B]Películas y/ó Series[/B][/COLOR] '
    if config.get_setting('search_excludes_all', default=''): txt_exc += '[COLOR green][B]Todos[/B][/COLOR] '

    if txt_exc:
        txt_exc.strip()
        txt_exc = '[COLOR chocolate][B] hay en [/B][/COLOR]' + txt_exc

    itemlist.append(item.clone( channel='filters', title = ' - [COLOR mediumaquamarine][B]Excluir canales en las búsquedas[/B][/COLOR]' + txt_exc, action = 'mainlist', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR yellow][B]Buscar[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_preferidos(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]PREFERIDOS:[/B]', folder=False, text_color='wheat', thumbnail=config.get_thumb('videolibrary') ))

    itemlist.append(item.clone( action='show_help_tracking', title= ' - [COLOR green][B]Información[/B][/COLOR] ¿ Cómo funciona ?', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( action='show_help_tracking_update', title= ' - [COLOR green][B]Información[/B][/COLOR] Búsqueda automática de [COLOR cyan][B]Nuevos Episodios[/B][/COLOR]', thumbnail=config.get_thumb('tools') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR wheat][B]Preferidos[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_descargas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]DESCARGAS:[/B]', folder=False, text_color='seagreen', thumbnail=config.get_thumb('download') ))

    itemlist.append(item.clone( action='show_help_descargas', title= ' - [COLOR green][B]Información[/B][/COLOR] ¿ Cómo funcionan ?', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( channel='actions', action='show_ubicacion', title= ' - ¿ Donde se ubican las [COLOR seagreen][B]Descargas[/B][/COLOR] ?', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( action='show_help_usb', title= ' - ¿ Se puede Descargar directamente en una [COLOR goldenrod][B]Unidad USB[/B][/COLOR] ?', thumbnail=config.get_thumb('usb') ))
    itemlist.append(item.clone( action='show_not_download', title= ' - ¿ Qué [COLOR goldenrod][B]NO[/B][/COLOR] está contemplado en las [COLOR seagreen][B]Descargas[/B][/COLOR] ?', thumbnail=config.get_thumb('roadblock') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR seagreen][B]Descargas[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_config(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]CONFIGURACIÓN [COLOR powderblue]CATEGORÍAS[/COLOR]:[/B]', folder=False, text_color='chocolate', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Menú[/B]', text_color='tan', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Canales[/B]', text_color='gold', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Parental[/B]',  text_color='orange', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Dominios[/B]',  text_color='bisque', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Cuentas[/B]',  text_color='goldenrod', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Play[/B]',  text_color='fuchsia', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Proxies[/B]',  text_color='red', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Torrents[/B]',  text_color='blue', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Buscar[/B]',  text_color='yellow', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Preferidos[/B]',  text_color='wheat', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Descargas[/B]',  text_color='seagreen', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Actualizar[/B]',  text_color='cyan', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Visual[/B]',  text_color='coral', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - TMDB[/B]',  text_color='darkorange', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Sistema[/B]',  text_color='pink', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Ayuda[/B]',  text_color='chartreuse', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Versión[/B]',  text_color='violet', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Contacto[/B]',  text_color='teal', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Team[/B]',  text_color='firebrick', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title='[B] - Legal[/B]',  text_color='crimson', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_actualizar(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]ACTUALIZAR [COLOR powderblue]FIXES[/COLOR]:[/B]', folder=False, text_color='cyan', thumbnail=config.get_thumb('addon') ))

    itemlist.append(item.clone( action='show_help_fixes', title= ' - ¿ Qué son los Fix ?' ))
    itemlist.append(item.clone( action='show_last_fix', title= ' - [COLOR green][B]Información[/B][/COLOR] último Fix instalado', thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( channel='actions', action='show_latest_domains', title= ' - [COLOR cyan][B]Últimos Cambios[/B][/COLOR] de Dominios', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( channel='actions', action = 'check_addon_updates', title= ' - Comprobar últimas actualizaciones tipo Fix', thumbnail=config.get_thumb('download') ))
    itemlist.append(item.clone( channel='actions', action = 'check_addon_updates_force', title= ' - Forzar Todas las actualizaciones tipo Fix', thumbnail=config.get_thumb('download') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR cyan][B]Actualizar[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_mediacenter(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]MEDIA CENTER:[/B]', folder=False, text_color='pink', thumbnail=config.get_thumb('computer') ))

    itemlist.append(item.clone( action='show_plataforma', title= ' - [COLOR green][B]Información[/B][/COLOR] Plataforma', thumbnail=config.get_thumb('computer') ))
    itemlist.append(item.clone( action='show_help_centers', title= ' - ¿ Dónde obtener soporte para su Media Center ?', thumbnail=config.get_thumb('telegram') ))
    itemlist.append(item.clone( action='show_log', title= ' - Visualizar el fichero LOG de su Media Center', thumbnail=config.get_thumb('computer') ))
    itemlist.append(item.clone( action='copy_log', title= ' - Obtener una Copia del fichero LOG de su Media Center', thumbnail=config.get_thumb('folder') ))
    itemlist.append(item.clone( channel='submnuteam', action='balandro_log', title= ' - Visualizar el fichero LOG ([COLOR pink][B]solo ejecución Balandro[/B][/COLOR]) de su Media Center', thumbnail=config.get_thumb('computer') ))
    itemlist.append(item.clone( action='show_advs', title= ' - Visualizar su fichero Advanced Settings de su Media Center', thumbnail=config.get_thumb('quote') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR pink][B]Sistema[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_sistema(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= '[B]SISTEMA:[/B]', folder=False, text_color='teal', thumbnail=config.get_thumb('tools') ))

    itemlist.append(item.clone( action='show_test', title= ' - Test [COLOR yellow][B]Status[/B][/COLOR] del sistema', thumbnail=config.get_thumb('addon') ))
    itemlist.append(item.clone( channel='actions', title= ' - Comprobar el estado de su [COLOR gold][B]Internet[/B][/COLOR]', action = 'test_internet', thumbnail=config.get_thumb('crossroads') ))

    itemlist.append(item.clone( channel='submnuteam', action='submnu_canales', title= ' - Test [COLOR gold][B]Canales[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( channel='submnuteam', action='submnu_servidores', title= ' - Test [COLOR fuchsia][B]Servidores[/B][/COLOR]', thumbnail=config.get_thumb('flame') ))
    itemlist.append(item.clone( channel='submnuteam', action='submnu_proxies', title= ' - Test [COLOR red][B]Proxies[/B][/COLOR]', thumbnail=config.get_thumb('flame') ))

    itemlist.append(item.clone( action='show_sets', title= ' - Visualizar sus [COLOR chocolate][B]Ajustes[/B][/COLOR] Personalizados de la configuración', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_cook', title= ' - Visualizar su fichero de cookies', thumbnail=config.get_thumb('folder') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] Configuración (categoría [COLOR teal][B]Sistema[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_clean(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]LIMPIEZAS:[/B]', folder=False, text_color='olive', thumbnail=config.get_thumb('quote') ))

    itemlist.append(item.clone( channel='submnuteam', action='submnu_center', title=' - [B]Limpieza [COLOR powderblue]Media Center[/COLOR][/B]', helper = True, thumbnail=config.get_thumb('computer'), text_color='olive' ))
    itemlist.append(item.clone( channel='submnuteam', action='submnu_addons', title=' - [B]Limpieza [COLOR powderblue]Add-Ons[/COLOR][/B]', helper = True, thumbnail=config.get_thumb('tools'), text_color='olive' ))
    itemlist.append(item.clone( channel='submnuteam', action='submnu_sistema', title=' - [B]Limpieza [COLOR powderblue]Sistema[/COLOR][/B]', helper = True, thumbnail=config.get_thumb('tools'), text_color='olive' ))
    itemlist.append(item.clone( channel='submnuteam', action='submnu_logs', title=' - [B]Limpieza [COLOR powderblue]Logs[/COLOR][/B]', helper = True, thumbnail=config.get_thumb('tools'), text_color='olive' ))
    itemlist.append(item.clone( channel='submnuteam', action='submnu_temporales', title=' - [B]Limpieza [COLOR powderblue]Temporales[/COLOR][/B]', helper = True, thumbnail=config.get_thumb('tools'), text_color='olive' ))

    itemlist.append(item.clone( channel='actions', action='manto_proxies', title=' - [B]Limpieza [COLOR red]Proxies[/COLOR][/B]', thumbnail=config.get_thumb('flame'), text_color='olive' ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] Configuración (categoría [COLOR olive][B]Sistema[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_version(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]VERSIONES:[/B]', folder=False, text_color='violet', thumbnail=config.get_thumb('addon') ))

    itemlist.append(item.clone( action='show_version', title= ' - [COLOR green][B]Información[/B][/COLOR] Versión', thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( action='show_changelog', title= ' - [COLOR gold][B]Historial[/B][/COLOR] de Versiones', thumbnail=config.get_thumb('news') ))

    return itemlist


def submnu_desarrollo(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]DESARROLLO [COLOR powderblue]TEAM[/COLOR]:[/B]', folder=False, text_color='firebrick', thumbnail=config.get_thumb('team') ))

    itemlist.append(item.clone( action='show_help_notice', title= '[COLOR aqua][B]Comunicado[/B][/COLOR] Oficial de Balandro', thumbnail=config.get_thumb('megaphone') ))

    itemlist.append(item.clone( action='', title= '[COLOR firebrick][B]Desarrollo [COLOR powderblue]Modo Developers[/COLOR]:[/B]', folder=False, thumbnail=config.get_thumb('team') ))

    itemlist.append(item.clone( action='show_dev_notes', title= ' - Notas para Developers (desarrolladores)', thumbnail=config.get_thumb('tools') ))

    if config.get_setting('developer_mode', default=False):
        itemlist.append(item.clone( channel='submnuteam', action='submnu_team', title = ' - Acceso a la opción de [COLOR darkorange][B]Desarrollo[/B][/COLOR] Team', thumbnail=config.get_thumb('team') ))

    itemlist.append(item.clone( action='', title= '[COLOR firebrick][B]Desarrollo [COLOR powderblue]Fuentes[/COLOR]:[/B]', folder=False, thumbnail=config.get_thumb('team') ))

    itemlist.append(item.clone( action='', title= ' - Fuentes [COLOR darkorange][B]github.com/balandro-tk/balandro-addon[/B][/COLOR]', thumbnail=config.get_thumb('telegram'), folder=False ))

    itemlist.append(item.clone( action='', title= '[COLOR firebrick][B]Desarrollo [COLOR powderblue]Unirse al Equipo[/COLOR]:[/B]', folder=False, thumbnail=config.get_thumb('team') ))

    itemlist.append(item.clone( action='', title= ' - Team ' + _team + ' Equipo de Desarrollo', folder=False, thumbnail=config.get_thumb('foro') ))

    itemlist.append(item.clone( action='', title='[COLOR yellow][B] - Incorporaciones: con Enlace de Invitación, solicitarlo en Foro ó Telegrams[/B][/COLOR]', folder=False, thumbnail=config.get_thumb('pencil') ))

    itemlist.append(item.clone( action='', title= '   - Foro ' + _foro + ' Instalaciones, Novedades, Sugerencias, etc.', thumbnail=config.get_thumb('foro'), folder=False ))
    itemlist.append(item.clone( action='', title= '   - Telegram ' + _telegram + ' Asesoramiento, Dudas, Consultas, etc.', thumbnail=config.get_thumb('telegram'), folder=False ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR pink][B]Team[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_legalidad(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]LEGALIDAD:[/B]', folder=False, text_color='crimson', thumbnail=config.get_thumb('roadblock') ))

    itemlist.append(item.clone( action='show_license', title= ' - Licencia (Gnu Gpl v3)', thumbnail=config.get_thumb('megaphone') ))
    itemlist.append(item.clone( action='show_legalidad', title= ' - Cuestiones Legales', thumbnail=config.get_thumb('megaphone') ))

    return itemlist


def channels_only_animes(item):
    logger.info()

    filters.only_animes(item)

def channels_exclusively_animes(item):
    logger.info()

    item.exclusively_animes = True

    filters.only_animes(item)

def channels_only_adults(item):
    logger.info()

    filters.only_adults(item)

def channels_exclusively_adults(item):
    logger.info()

    item.exclusively_adults = True

    filters.only_adults(item)

def show_channels_list(item):
    logger.info()

    filters.show_channels_list(item)

def channels_only_last_domain(item):
    logger.info()

    item.last_domain = True
    item.only_last_domain = True

    filters.show_channels_list(item)

def channels_status(item):
    logger.info()

    filters.channels_status(item)

def channels_des_rea(item):
    logger.info()

    item.des_rea = True

    filters.channels_status(item)

def channels_with_proxies(item):
    logger.info()

    filters.with_proxies(item)

def channels_with_proxies_memorized(item):
    logger.info()

    # por si venimos de config
    if config.get_setting('memorize_channels_proxies', default=True):
        item.memo_proxies = True

        filters.with_proxies(item)

def channels_no_actives(item):
    logger.info()

    filters.no_actives(item)

def channels_no_searchables(item):
    logger.info()

    item.no_searchables = True

    filters.no_actives(item)

def channels_prefered(item):
    logger.info()

    filters.only_prefered(item)

def channels_suggesteds(item):
    logger.info()

    item.suggesteds = True

    filters.show_channels_list(item)

def channels_inestables(item):
    logger.info()

    item.no_stable = True

    filters.show_channels_list(item)

def channels_problematicos(item):
    logger.info()

    item.problematics = True

    filters.show_channels_list(item)

def channels_with_notice(item):
    logger.info()

    item.notices = True

    filters.show_channels_list(item)

def channels_only_torrents(item):
    logger.info()

    filters.only_torrents(item)

def channels_exclusively_torrents(item):
    logger.info()

    item.exclusively_torrents = True

    filters.only_torrents(item)

def show_clients_torrent(item):
    logger.info()

    if not item.title: item.title = 'soportados'

    filters.show_clients_torrent(item)

def show_servers_list(item):
    logger.info()

    # por si venimos de config
    if not item.tipo: item.tipo = 'activos'

    filters.show_servers_list(item)


def show_help_miscelanea(item):
    logger.info()

    txt = '[COLOR gold][B]KODI Media Center:[/B][/COLOR][CR]'
    txt += '  Versiones soportadas en Balandro:  [COLOR darkorange][B]20.x,  19.x,  18.x  y  17.x[/B][/COLOR][CR][CR]'

    txt += '  Kodi [COLOR yellow]Oficial[/COLOR]:  [COLOR plum][B]kodi.tv/download/[/B][/COLOR][CR]'
    txt += '  para obtener la [COLOR yellowgreen]Última versión[/COLOR] de este Media Center[CR][CR]'

    txt += '  Kodi [COLOR yellow]Oficial[/COLOR]:  [COLOR plum][B]mirrors.kodi.tv/releases/[/B][/COLOR][CR]'
    txt += '  para obtener [COLOR yellowgreen]versiones Anteriores[/COLOR] a la última de este Media Center[CR][CR]'

    txt += '  Kodi [COLOR chartreuse]Soporte:  [/COLOR][COLOR lightblue][B]kodi.wiki/view/[/B][/COLOR][CR]'
    txt += '  para [COLOR yellowgreen]Consultas[/COLOR] sobre este Media Center[CR][CR]'

    txt += '[COLOR gold][B]KELEBEK (Add-Ons y Otros Media Centers):[/B][/COLOR][CR]'

    txt += '  Fuente [COLOR yellow]Kelebek[/COLOR]:  [COLOR plum][B]https://newkelebek.gitgub.io/Newkelebek[/B][/COLOR][CR]'
    txt += '  para obtener otros [COLOR yellowgreen]Add-Ons, Scripts, etc.[/COLOR][CR][CR]'

    txt += '  [COLOR chartreuse]Telegram[/COLOR] Soporte:  [COLOR lightblue][B]t.me/AprendiendoKodi[/B][/COLOR][CR]'
    txt += '  para Consultas [COLOR yellowgreen]Media Center, Motores Torrent, Servidores Alternativos, etc.[/COLOR][CR][CR]'

    txt += '[COLOR gold][B]BALANDRO:[/B][/COLOR][CR]'

    txt += '  Fuente [COLOR yellow]Balandro[/COLOR]:  [COLOR plum][B]https://balandro-tk.github.io/balandro/[/B][/COLOR][CR]'
    txt += '  para obtener [COLOR yellowgreen]Repositorio, Add-On, Scripts, etc.[/COLOR][CR][CR]'

    txt += '  Foro:  [COLOR coral][B]www.mimediacenter.info/foro/[/B][/COLOR][CR]'
    txt += '  para [COLOR yellowgreen]Instalaciones, Novedades, Sugerencias, etc.[/COLOR][CR][CR]'

    txt += '  [COLOR chartreuse]Telegram[/COLOR]:  [COLOR lightblue][B]t.me/balandro_asesor[/B][/COLOR][CR]'
    txt += '  para [COLOR yellowgreen]Asesoramiento, Dudas, Consultas, etc.[/COLOR][CR][CR]'

    txt += '[COLOR gold][B]DESARROLLO:[/B][/COLOR][CR]'

    txt += '  [COLOR firebrick]Fuentes Desarrollo[/COLOR] [COLOR yellow]Balandro[/COLOR]:  [COLOR darkorange][B]github.com/balandro-tk/balandro-addon[/B][/COLOR][CR]'
    txt += '  para [COLOR orange]Mantenimiento del Add-On, Scripts, etc.[/COLOR][CR][CR]'

    txt += '  [COLOR chartreuse]Telegram[/COLOR]:  [COLOR lightblue][B]t.me/Balandro_team[/B][/COLOR][CR]'
    txt += '  para unirse al [COLOR yellowgreen]Equipo de desarrollo[/COLOR][CR][CR]'


    platformtools.dialog_textviewer('Información Miscelánea', txt)


def show_help_register(item):
    logger.info()

    txt = '*) Determinadas webs obligan a registrarse para permitir su acceso.'

    txt += '[CR][CR]  Es importante usar [B][COLOR gold]cuentas secundarias[/COLOR][/B] para registrarse, nunca useis las vuestras personales.'

    txt += '[CR][CR]*) Para ello desde otro equipo debeis accecder a la web en cuestión y registraros (darse de alta)'

    txt += '[CR][CR]  Si desconoceis el dominio actual de esa web, mediante un navegador localizar su [B][COLOR gold]twitter[/COLOR][/B]'

    txt += '[CR][CR]  Por ejemplo [B][COLOR yellow]HdFull[/COLOR][/B] twitter oficial ó [B][COLOR yellow]PlayDede[/COLOR][/B] twitter oficial'

    txt += '[CR][CR]  ó bien acceder para [COLOR yellow]HdFull[/COLOR] a [B][COLOR cyan]dominioshdfull.com[/COLOR][/B] y para [COLOR yellow]PlayDede[/COLOR] [B][COLOR cyan]dominiosplaydede.com[/COLOR][/B]'

    txt += '[CR][CR]*) Imprescindible tomar buena nota de vuestro [B][COLOR gold]Usuario y Contraseña[/COLOR][/B] para cada web.'

    txt += '[CR][CR]*) Una vez tengáis vuestros datos, podéis informarlos en la configuración, ó bien se os solicitará al acceder a ese canal determinado.'

    txt += '[CR][CR]*) Mientras mantengáis las sesiones abiertas via navegador en estos dominios, no tendreis que volver a informar vuestras credenciales.'

    txt += '[CR][CR]*) [B][COLOR gold]Atención[/COLOR][/B]: las [COLOR chartreuse]Sesiones Abiertas[/COLOR] en vuestro Media Center [B][COLOR greenyellow]No son In Eternum[/COLOR][/B], por ello es conveniente, que procedaís a [COLOR chartreuse]Cerrar vuestra Sesión[/COLOR] cada cierto tiempo, porque podría provocar que no se presentaran resultados.'

    platformtools.dialog_textviewer('Información dominios que requieren Registrarse', txt)


def show_help_animefenix(item):
    item.notice = 'animefenix'
    show_help_canales(item)

def show_help_animeonline(item):
    item.notice = 'animeonline'
    show_help_canales(item)

def show_help_cuevana3video(item):
    item.notice = 'cuevana3video'
    show_help_canales(item)

def show_help_cinecalidadlol(item):
    item.notice = 'cinecalidadlol'
    show_help_canales(item)

def show_help_cinecalidadmx(item):
    item.notice = 'cinecalidadmx'
    show_help_canales(item)

def show_help_dilo(item):
    item.notice = 'dilo'
    show_help_canales(item)

def show_help_ennovelas(item):
    item.notice = 'ennovelas'
    show_help_canales(item)

def show_help_entrepeliculasyseries(item):
    item.notice = 'entrepeliculasyseries'
    show_help_canales(item)

def show_help_gnula24h(item):
    item.notice = 'gnula24h'
    show_help_canales(item)

def show_help_hdfull(item):
    item.notice = 'hdfull'
    show_help_canales(item)

def show_help_henaojara(item):
    item.notice = 'henaojara'
    show_help_canales(item)

def show_help_historiadeamortv(item):
    item.notice = 'historiadeamortv'
    show_help_canales(item)

def show_help_homecine(item):
    item.notice = 'homecine'
    show_help_canales(item)

def show_help_jkanime(item):
    item.notice = 'jkanime'
    show_help_canales(item)

def show_help_megaserie(item):
    item.notice = 'megaserie'
    show_help_canales(item)

def show_help_mirapeliculas(item):
    item.notice = 'mirapeliculas'
    show_help_canales(item)

def show_help_peliculaspro(item):
    item.notice = 'peliculaspro'
    show_help_canales(item)

def show_help_pelisforte(item):
    item.notice = 'pelisforte'
    show_help_canales(item)

def show_help_pelismaraton(item):
    item.notice = 'pelismaraton'
    show_help_canales(item)

def show_help_pelisxd(item):
    item.notice = 'pelisxd'
    show_help_canales(item)

def show_help_pelisyseries(item):
    item.notice = 'pelisyseries'
    show_help_canales(item)

def show_help_pepecinetop(item):
    item.notice = 'pepecinetop'
    show_help_canales(item)

def show_help_playdede(item):
    item.notice = 'playdede'
    show_help_canales(item)

def show_help_rojotorrent(item):
    item.notice = 'rojotorrent'
    show_help_canales(item)

def show_help_seriespapayato(item):
    item.notice = 'seriespapayato'
    show_help_canales(item)

def show_help_srnovelas(item):
    item.notice = 'srnovelas'
    show_help_canales(item)

def show_help_subtorrents(item):
    item.notice = 'subtorrents'
    show_help_canales(item)

def show_help_torrentpelis(item):
    item.notice = 'torrentpelis'
    show_help_canales(item)

def show_help_resto(item):
    item.notice = ''
    show_help_canales(item)


def show_help_canales(item):
    logger.info()

    if item.notice:
        datos = channeltools.get_channel_parameters(item.notice)
        if not datos['active']:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
            return

    if item.notice:
         txt = '[B][COLOR cyan]El webmaster de [COLOR yellow]' + item.notice.capitalize() + '[/COLOR] ha activado un nivel más de protección con [COLOR orangered]CloudFlare[/COLOR][/B][CR]'
    else:
         txt = '[B][COLOR cyan]El webmaster del [COLOR yellow]Canal[/COLOR] ha activado un nivel más de protección con [COLOR orangered]CloudFlare[/COLOR][/B][CR]'

    if item.notice == 'hdfull' or item.notice == 'playdede':
       txt += '[COLOR gold][B][CR]También ha añadido un control contra robots [COLOR red]reCAPTCHA[/COLOR] oculto.[/COLOR][/B][CR]'

       if item.notice == 'hdfull':
           txt += '[CR][COLOR yellow]  Para conocer el dominio actual acceder a través de un navegador web a[/COLOR] [B][COLOR greenyellow]dominioshdfull.com[/COLOR][/B][CR]'
       else:
           txt += '[CR][COLOR yellow]  Para conocer el dominio actual acceder a través de un navegador web a[/COLOR] [B][COLOR greenyellow]dominiosplaydede.com[/COLOR][CR]'

    txt += '[CR][COLOR goldenrod][B]  Desconocemos si será Temporal ó Definitivo.[/B][/COLOR][CR]'

    txt += '[CR][COLOR plum][B]  Ya ocurrió alguna vez en el pasado y al cabo de un cierto tiempo lo retiró.[/B][/COLOR][CR]'

    txt += '[CR][COLOR aquamarine][B]  Por ello, si no os funciona correctamente, pues hay que tener paciencia,'
    txt += '[CR]  e ir probando uno a uno, los Proveedores de proxies, en [COLOR red]Configurar proxies a usar ...[/B][/COLOR][CR]'

    txt += '[CR][COLOR yellowgreen][B]Ó bien prescindir/desactivar el canal hasta que se estabilize posiblemente en un futuro.[/B][/COLOR]'

    platformtools.dialog_textviewer('Información canal ' + item.notice.capitalize(), txt)


def show_help_gamovideo(item):
    logger.info()

    if not servertools.is_server_available('gamovideo'):
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El servidor está Inactivo[/B][/COLOR]' % color_avis)
        return

    txt = '*) Consideraciones si [COLOR gold][B]Jamás[/COLOR][/B] reproduce este servidor en ningún Canal.[CR]'

    txt = '*) Si su Media Center opera bajo alguna de las siguientes opciones:[CR]'

    txt += '  - Ejecución de Balandro bajo [COLOR gold]Builds, Wizards ó Widgets[/COLOR] puede fallar la Reproducción de este servidor[CR]'
    txt += '  - Intervención del fichero [COLOR gold]AdvancedSettings[/COLOR] con sentencias relativas a la memoria de su Media Center[CR][CR]'

    platformtools.dialog_textviewer('Información servidor Gamovideo', txt)


def show_help_mega(item):
    logger.info()

    if not servertools.is_server_available('mega'):
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El servidor está Inactivo[/B][/COLOR]' % color_avis)
        return

    txt = '*) Si su Media Center es una versión anterior a [COLOR gold][B]19.x[/COLOR][/B] y opera bajo el sistema operativo [COLOR gold][B]Windows[/COLOR][/B], en determinadas ocasiones, puede fallar la Reproducción.[CR][CR]'

    txt += '*) Para cualquier plataforma de ejecución [COLOR gold][B](Windows, Android, Rasperri, etc.)[/COLOR][/B] deben existir Obligatoriamente los modulos necesarios de [COLOR yellow][B]Cryptografía[/COLOR][/B] ya integrados en su Equipo, si no existieran, puede fallar la Reproducción.'

    platformtools.dialog_textviewer('Información servidor Mega', txt)


def show_help_uptobox(item):
    logger.info()

    if not servertools.is_server_available('uptobox'):
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El servidor está Inactivo[/B][/COLOR]' % color_avis)
        return

    txt = '*) Determinados servidores obligan a registrarse para permitir su acceso.'

    txt += '[CR][CR] Es importante usar [B][COLOR gold]cuentas secundarias[/COLOR][/B] para registrarse, nunca useis las vuestras personales.'

    txt += '[CR][CR]*) Para ello desde otro equipo debeis accecder a la web en cuestión y registraros (darse de alta)'

    txt += '[CR][CR] Si desconoceis el dominio actual de ese servidor, mediante un navegador localizar su [B][COLOR gold]twitter[/COLOR][/B]'

    txt += '[CR][CR] Por ejemplo [B][COLOR gold]Uptobox[/COLOR][/B] twitter oficial'

    txt += '[CR][CR]*) Imprescindible tomar buena nota de vuestro [B][COLOR gold]Usuario y Contraseña[/COLOR][/B] para ese servidor.'

    txt += '[CR][CR]*) Una vez tengáis vuestros datos, se os solicitará al acceder a ese servidor determinado.'

    txt += '[CR][CR]*) Acceder desde otro equipo via navegador a [B][COLOR gold]uptobox.com/pin[/COLOR][/B], solo se gestionan las cuentas [B][COLOR yellow]Free[/COLOR][/B]'

    txt += '[CR][CR]*) En el caso de no estar registrados proceder a ello (darse de alta)'

    txt += '[CR][CR] Iniciar la sesión con vuestras credenciales'
    txt += ' e introducir el [B][COLOR gold]PIN[/COLOR][/B] que se os mostró en la ventana al intentar reproducir, para tener vinculada vuestra cuenta.'

    txt += '[CR][CR]*) Mientras mantengáis las sesiones abiertas via navegador en ese servidor, no tendreis que volver a informar vuestras credenciales.'

    txt += '[CR][CR]*) Hay servidores que limitan el [B][COLOR gold]tiempo máximo de visionado diario[/COLOR][/B] (aprox. 150 minutos).'

    platformtools.dialog_textviewer('Información servidor Uptobox', txt)


def show_server_report(item):
    logger.info()

    txt = '*) Estos Reportes debereís informarlos en nuestro [COLOR chartreuse]Grupo de Telegram[/COLOR]' + _telegram

    txt += '[CR][CR]*) [B][COLOR gold]Antes de reportarlo como un posible error, rogamos accedaís a través de un navegador web, a ese canal en concreto y procedaís a comprobar si esa pelicula/serie/episodio reproduce a través del servidor en cuestión[/COLOR][/B]'

    txt += '[CR][CR]*) [B][COLOR yellow]Si el resultado de esta operativa ha resultado satisfactoria, indicarnos toda esa información para proceder a su verficación/subsanación[/COLOR][/B]'

    txt += '[CR][CR]*) Debeís comprender que este trabajo ha de ser compartido entre vosotros y nosotros, porqué si la carga solo recayera sobre nosotros sería imposible abordarlo por saturación/falta de tiempo'

    txt += '[CR][CR]*) Muchas gracias, por vuestro tiempo y comprensión al respecto'

    platformtools.dialog_textviewer('Como Reportar posible Fallo en la Reproducción de servidores', txt)


def show_help_settings(item):
    logger.info()

    txt = '*) Las opciones para los [COLOR gold]listados de canales[/COLOR] se usan si marcas canales como [COLOR gold][B]Preferidos[/B][/COLOR] ó [COLOR gray][B]Desactivados[/B][/COLOR].'
    txt += ' Esto lo puedes hacer desde el [COLOR yellow][B]Menú Contextual[/B][/COLOR] en los listados de canales.'

    txt += '[CR][CR]*) En [COLOR gold]Búsquedas[/COLOR] el parámetro [COLOR gold][B]Resultados por canal[/B][/COLOR] sirve para limitar el número de coincidencias que se muestran en la pantalla de búsqueda global.'
    txt += ' Es para que no salga un listado demasiado largo ya que algunos canales son más sensibles que otros y pueden devolver bastantes resultados.'
    txt += ' Pero de todas maneras se puede acceder al listado de todos los resultados de cada canal concreto.'
    txt += ' Dispones de más parámetros personalizables en la configuración categoría [COLOR yellow][B]Buscar[/B][/COLOR].'

    txt += '[CR][CR]*) En [COLOR gold]Reproducción[/COLOR] se puede activar [COLOR yellow][B]Auto Play[/B][/COLOR] para no tener que seleccionar un servidor para reproducir.'
    txt += ' Si hay algún canal para el que quieras desactivar el autoplay puedes indicarlo en la configuración categoría [COLOR fuchsia][B]Play[/B][/COLOR].'

    txt += '[CR][CR]*) En [COLOR gold]Reproducción[/COLOR] los parámetros para ordenar/filtrar los enlaces [COLOR gold][B]por idioma[/B][/COLOR] permiten indicar nuestras preferencias de idiomas.'
    txt += ' Entre Español, Latino y Versión Original elije el orden que prefieres, ó descarta alguno de ellos si no te interesa.'
    txt += ' Todo ello puedes personalizarlo en la configuración categoría [COLOR fuchsia][B]Play[/B][/COLOR].'

    txt += '[CR][CR]*) En [COLOR gold]Reproducción[/COLOR] los parámetros para ordenar los enlaces [COLOR gold][B]por calidad[/B][/COLOR] permiten mostrar antes los de más calidad en lugar de mostrarlos según el orden que tienen en la web.'
    txt += ' Algunos canales tienen valores fiables de calidad pero otros no, depende de cada web.'
    txt += ' Todo ello puedes personalizarlo en la configuración categoría [COLOR fuchsia][B]Play[/B][/COLOR].'

    txt += '[CR][CR]*) En [COLOR gold]Reproducción[/COLOR] los parámetros para ordenar/filtrar los enlaces [COLOR gold][B]por servidores[/B][/COLOR] permiten hacer algunos ajustes en función de los servidores.'
    txt += ' Si no quieres que te salgan enlaces de ciertos servidores, escríbelos en [COLOR cyan][B]Descartados[/B][/COLOR] (ej: torrent, mega).'
    txt += ' Y si quieres priorizar algunos servidores escríbelos en [COLOR darkorange][B]Preferidos[/B][/COLOR] (ej: torrent, mega), ó al revés en [COLOR gold][B]última opción[/B][/COLOR] (ej: torrent, mega).'
    txt += ' Para modificar estas opciones necesitas saber qué servidores te funcionan mejor y peor, en caso de duda no hace falta que lo modifiques.'
    txt += ' Todo ello puedes personalizarlo en la configuración categoría [COLOR fuchsia][B]Play[/B][/COLOR].'

    txt += '[CR][CR]*) Una opción que puede provocar una demora en los tiempos de respuesta es en configuración categoría [COLOR gold][B]TMDB[/B][/COLOR] si se activa [COLOR gold][B]buscar información extendida[/B][/COLOR].'
    txt += ' Esto provoca que los listados de películas y series de todos los canales tarden más en mostrarse ya que se hace una segunda llamada a TMDB para intentar recuperar más datos.'

    txt += '[CR][CR]*) En [COLOR gold][B]TMDB[/B][/COLOR] se pueden desactivar las [COLOR gold][B]llamadas a TMDB[/COLOR][/B] en los listados.'
    txt += ' Esto provoca que los listados de películas y series de todos los canales tarden menos en mostrarse pero en la mayoría de casos no tendrán información como la sinopsis y las carátulas serán de baja calidad.'
    txt += ' Puede ser útil desactivarlo temporalmente en casos donde alguna película/serie no se identifica correctamente en tmdb y se quieran ver los datos originales de la web.'

    txt += '[CR][CR]*) Exiten más parámetros en la [COLOR gold]Configuracion[/COLOR] de Balandro,  para tener personalizada su ejecución.'
    txt += ' Divididos por categorías [COLOR gold]Menú, Canales, Parental, Dominios, Cuentas, Play, Proxies, Torrents, Buscar, etc.[/COLOR].'

    platformtools.dialog_textviewer('Apuntes sobre ciertos Parámetros de la configuración', txt)


def show_help_tips(item):
    logger.info()

    txt = '*) Es importante usar el [B][COLOR yellow]Menú Contextual[/COLOR][/B] para acceder a acciones que se pueden realizar sobre los elementos de los listados.'
    txt += ' Si dispones de un teclado puedes acceder a él pulsando la tecla C, en dispositivos táctiles manteniendo pulsado un elemento, y en mandos de tv-box manteniendo pulsado el botón de selección.'
    txt += ' Si usas un mando de TV es recomendable configurar una de sus teclas con [COLOR gold][B]ContextMenu[/B][/COLOR] (Menú Contextual).'

    txt += '[CR][CR]*) En los listados de los canales puedes usar el [COLOR yellow][B]Menú Contextual[/B][/COLOR] para marcar los canales como [COLOR gold]Desactivado/Activo/Preferido[/COLOR].'
    txt += ' De esta manera podrás tener tus [COLOR gold]canales preferidos[/COLOR] al inicio y mover al final los que no te interesen.'
    txt += ' Los canales desactivados son accesibles pero no forman parte de las búsquedas.'

    txt += '[CR][CR]*) Si en algún canal encuentras una película/serie que te interesa pero fallan sus enlaces, accede al [COLOR yellow][B]Menú Contextual[/B][/COLOR] y selecciona'
    txt += ' [COLOR gold]buscar en otros canales[/COLOR] para ver si está disponible en algún otro canal.'

    txt += '[CR][CR]*) Desde cualquier pantalla desplázate hacia el lateral izquierdo para desplegar algunas [COLOR gold]opciones standard de su Media Center[/COLOR].'
    txt += ' Allí tienes siempre un acceso directo a la Configuración del addon y también puedes cambiar el [COLOR yellow][B]Tipo de Vista[/B][/COLOR] que se aplica a los listados.'
    txt += ' Entre Lista, Cartel, Muro de información, Lista amplia, Muro, Fanart, etc. escoge como prefieres ver la información.'

    txt += '[CR][CR]*) Algunos canales de series tienen un listado de [COLOR gold]últimos episodios[/COLOR]. En función de las características de las webs, los enlaces llevan'
    txt += ' a ver el capítulo ó a listar las temporadas de la serie. Cuando es posible, desde el enlace se ve el episodio y desde el [COLOR yellow][B]Menú Contextual[/B][/COLOR]'
    txt += ' se puede acceder a la temporada concreta ó la lista de temporadas.'

    txt += '[CR][CR]*) Para seguir series es recomendable usar la opción [COLOR wheat][B]Preferidos[/B][/COLOR]. Busca la serie que te interese en cualquiera de los canales y desde el [COLOR yellow][B]Menú Contextual[/B][/COLOR] guárdala.'
    txt += ' Luego ves a [COLOR wheat][B]Preferidos[/B][/COLOR] donde podrás gestionar lo necesario para la serie. Además puedes usar [COLOR gold]Buscar en otros canales[/COLOR] y desde el listado de resultados con el'
    txt += ' [COLOR yellow][B]Menú Contextual[/B][/COLOR] también los puedes guardar y se añadirán a los enlaces que ya tenías. De esta manera tendrás alternativas en diferentes enlaces por si algún día falla alguno ó desaparece.'

    platformtools.dialog_textviewer('Trucos y consejos varios', txt)


def show_help_use(item):
    logger.info()

    txt = '[COLOR gold][B]Modo CASUAL:[/B][/COLOR][CR]'
    txt += 'Accede por ejemplo a Películas ó Series desde el menú principal, entra en alguno de los canales y navega por sus diferentes opciones hasta encontrar una película que te interese.'
    txt += ' Al entrar en la película se mostrará un diálogo con diferentes opciones de vídeos encontrados.'
    txt += ' Prueba con el primero y si el enlace es válido empezará a reproducirse. Sino, prueba con alguno de los otros enlaces disponibles.'
    txt += ' Si ninguno funcionara, desde el enlace de la película accede al [COLOR yellow][B]Menú Contextual[/B][/COLOR] y selecciona [COLOR gold]Buscar en otros canales[/COLOR].'

    txt += '[CR][CR][COLOR gold][B]Modo DIRECTO:[/B][/COLOR][CR]'
    txt += 'Si quieres ver una película/serie concreta, accede a [COLOR yellow][B]Buscar[/B][/COLOR] desde el menú principal y escribe el título en el buscador.'
    txt += ' Te saldrá una lista con las coincidencias en todos los canales disponibles.'

    txt += '[CR][CR][COLOR gold][B]Modo PLANIFICADOR (Guardar en Preferidos):[/B][/COLOR][CR]'
    txt += 'Navega por los diferentes canales y ves apuntando las películas/series que te puedan interesar.'
    txt += ' Para ello accede al [COLOR yellow][B]Menú Contextual[/B][/COLOR] desde cualquier Película/Serie/Episodio y selecciona [COLOR gold][B]Guardar enlace[/B][/COLOR].'
    txt += ' Cuando quieras ver una película/serie, accede a [COLOR wheat][B]Preferidos[/B][/COLOR] desde el menú principal donde estará todo lo guardado.'

    txt += '[CR][CR][COLOR gold][B]Modo ASEGURADOR (Descargas):[/B][/COLOR][CR]'
    txt += 'Descarga algunos [COLOR gold]Vídeos[/COLOR] para tener listas para ver sin depender de la saturación de la red/servidores en momentos puntuales.'
    txt += ' Desde cualquier película/episodio, tanto en los [COLOR gold][B]Canales[/B][/COLOR] como en [COLOR wheat][B]Preferidos[/B][/COLOR], accede al [COLOR yellow][B]Menú Contextual[/B][/COLOR] y selecciona [COLOR gold][B]Descargar vídeo[/B][/COLOR].'
    txt += ' Selecciona alguno de los enlaces igual que cuando se quiere reproducir y empezará la descarga.'
    txt += ' Para ver lo descargado, accede a [COLOR seagreen][B]Descargas[/B][/COLOR] desde el menú principal.'

    txt += '[CR][CR][COLOR gold][B]Modo COLECCIONISTA (Menú Preferidos):[/B][/COLOR][CR]'
    txt += 'Desde [COLOR wheat][B]Preferidos[/B][/COLOR] accede a [COLOR gold][B]Gestionar listas[/B][/COLOR], donde puedes crear diferentes listas para organizarte las películas y series que te interesen.'
    txt += ' Por ejemplo puedes tener listas para distintos usuarios de Balandro (Padres, Esposa, Hijos, etc.) ó de diferentes temáticas, ó para guardar lo que ya hayas visto, ó para pasar tus recomendaciones a algún amigo, etc.'

    platformtools.dialog_textviewer('Ejemplos de uso de Balandro', txt)


def show_help_faq(item):
    logger.info()

    txt = '[COLOR gold][B]¿ De dónde viene Balandro ?[/B][/COLOR][CR]'
    txt += 'Balandro es desde el año [COLOR cyan][B]2018[/B][/COLOR] un addon derivado de [COLOR gold]Pelisalacarta y Alfa[/COLOR], optimizado a nivel interno de código y a nivel funcional para el usuario.'
    txt += ' Puede ser útil en dispositivos poco potentes como las [COLOR yellow][B]Raspberry Pi[/B][/COLOR] u otros [COLOR yellow][B]TvBox[/B][/COLOR] y para usuarios que no quieran complicaciones.'
    txt += ' Al ser un addon de tipo navegador, tiene el nombre de un velero ya que Balandro era una embarcación ligera y maniobrable, muy apreciada por los piratas.'

    txt += '[CR][CR][COLOR gold][B]¿ Qué características tiene Balandro ?[/B][/COLOR][CR]'
    txt += 'Principalmente permite acceder a los contenidos de webs con vídeos de películas y series para reproducirlos y/ó guardarlos, y'
    txt += ' dispone de unos [COLOR wheat][B]Preferidos[/B][/COLOR] propios donde poder apuntar todas las Películas y Series que interesen al usuario.'
    txt += ' Se pueden configurar múltiples opciones, por ejemplo la preferencia de idioma, la reproducción automática, los colores para los listados, los servidores preferidos, excluir canales en las búsquedas, etc.'

    txt += '[CR][CR][COLOR gold][B]¿ Almacena Balandro algún tipo de contenido?[/B][/COLOR][CR]'
    txt += 'NO, este Add-On es tan solo un mero Ejercicio de Aprendizaje del Lenguaje de Programación Python y se distribuye sin Ningún Contenido Multimedia adjunto al mismo.'
    txt += '[COLOR red][B][I] En consecuencia solo Las Webs son plenamente Responsables de los Contenidos que Publiquen [/I][/B][/COLOR].'

    txt += '[CR][CR][COLOR gold][B]¿ Qué particularidades tienen los Canales [/COLOR][COLOR darkgoldenrod]Problemáticos[/COLOR][COLOR gold] ?[/B][/COLOR][CR]'
    txt += 'Son aquellos canales en los que Predominan Referencias/Elementos Sin enlaces Disponibles, enlaces Inválidos y/ó enlaces a servidores No Soportados.'

    txt += '[CR][CR][COLOR gold][B]¿ Cómo funciona el [/COLOR][COLOR fuchsia]Autoplay[/COLOR][COLOR gold] ?[/B][/COLOR][CR]'
    txt += 'Se puede activar la función de reproducción automática desde la configuración del addon.'
    txt += ' Si se activa, al ver una película ó episodio se intenta reproducir el primero de los enlaces que funcione, sin mostrarse el diálogo de selección de servidor.'
    txt += ' Los enlaces se intentan secuencialmente en el mismo orden que se vería en el diálogo, por lo que es importante haber establecido las preferencias de idioma, servidores y calidades.'

    txt += '[CR][CR][COLOR gold][B]¿ En qué orden se muestran los enlaces de servidores ?[/B][/COLOR][CR]'
    txt += 'El orden inicial es por la fecha de los enlaces, para tener al principio los últimos actualizados ya que es más probable que sigan vigentes, aunque en los canales que no lo informan es según el orden que devuelve la web.'
    txt += ' Desde la configuración se puede activar el ordenar por calidades, pero su utilidad va a depender de lo que muestre cada canal y la fiabilidad que tenga.'
    txt += ' A partir de aquí, si hay preferencias de servidores en la configuración, se cambia el orden para mostrar al principio los servidores preferentes y al final los de última opción.'
    txt += ' Y finalmente se agrupan en función de las preferencias de idiomas del usuario.'

    txt += '[CR][CR][COLOR gold][B]¿ Funcionan los enlaces [/COLOR][COLOR blue]Torrent[/COLOR][COLOR gold] ?[/B][/COLOR][CR]'
    txt += 'El addon está preparado para tratarlos usando un Motor/Cliente de torrents externo, tipo [COLOR gold]Elementum, etc.[/COLOR]'
    txt += ' Estos Motores/Clientes externos (addons) torrents no están incluidos en Balandro y deben Instalarse por separado.'
    txt += ' Además, debe indicarse Obligatoriamente en la configuración de Balandro cual va a ser su Motor/Cliente habitual de torrents.'

    txt += '[CR][CR]Si algún otro addon tiene activado [COLOR gold]Borrar caché de kodi en el inicio[/COLOR], se elimina una carpeta temporal que [COLOR gold]Elementum[/COLOR] necesita'
    txt += ' [COLOR gold].../.kodi/temp/elementum/[/COLOR], en consecuencia puede fallar la descarga/reproducción del torrent.'
    txt += ' Cuando a [COLOR gold]Elementum[/COLOR] se le pasa un enlace .torrent lo intenta descargar en esa carpeta, pero no podrá hacerlo si esta carpeta se ha eliminado.'
    txt += ' Si esto sucede, en el Log de su Media Center se observa el mensaje [COLOR gold]Error adding torrent: &os.PathError[/COLOR].'
    txt += ' Este error no se produce si el enlace es de tipo [COLOR gold]magnet:?[/COLOR], por lo tanto, pueden haber enlaces en Balandro que funcionen y otros que No.'

    txt += '[CR][CR][COLOR blue][B]Este problema se resuelve:[/B][/COLOR] si se accede a la Configuración de [COLOR gold]Elementum[/COLOR] y se guarda nuevamente, se regenera su carpeta de caché y funcionará correctamente la descarga/reproducción del torrent.'
    txt += ' Pero si se mantiene activado el borrado por ejemplo en Indigo, al reiniciar su Media Center Kodi dejará de funcionar de nuevo.'

    txt += '[CR][CR][COLOR gold][B]¿ Porqué la opción [/COLOR][COLOR yellow]Buscar[/COLOR][COLOR gold] entra em modo bucle (vuelve a solicitar el texto a localizar) ?[/B][/COLOR][CR]'
    txt += 'Addons de limpieza que pueden afectar al funcionamiento de Balandro, [COLOR gold]LimpiaTuKodi, Indigo y similares.[/COLOR]'

    txt += '[CR][CR]Cuando desde estos addons se ejecuta la función [COLOR gold]Limpiar Cache y Rom[/COLOR],'
    txt += ' se elimina la carpeta interna de la caché de su Media Center Kodi [COLOR gold].../.kodi/temp/archive_cache/[/COLOR]'
    txt += ' y ello provoca que este no pueda cachear. Al no poder usar esta caché, puede influir en el rendimiento en general de todos los addons,'
    txt += ' pero donde resulta una molestia dentro de Balandro (y demás addons) es al buscar, ya que después de hacer una búsqueda y entrar en alguno de los resultados,'
    txt += ' al volver atrás, vuelve a solicitar de nuevo la introducción de texto, cuando debería volver a mostrar la lista de resultados previa.'

    txt += '[CR][CR][COLOR yellow][B]Este problema se resuelve:[/B][/COLOR] Re-iniciando su Media center Kodi, ya que Kodi vuelve a generar la carpeta de caché al iniciarse.'
    txt += ' Cualquier addon que en lugar de eliminar el contenido del caché para limpiar, elimine la propia carpeta provocará este mismo efecto.'

    txt += '[CR][CR][COLOR gold][B]¿ Como evitar la Ventana [/COLOR][COLOR chartreuse]Lista de Reproduccion Abortada[/COLOR][COLOR gold] aunque el enlace NO reproduzca ?[/B][/COLOR][CR]'
    txt += 'Es necesario incorporar en su Media Center, las instrucciones que a continuación se detallan en el archivo [COLOR gold]advancedsettings.xml[/COLOR], si no existiera dicho fichero deberá crear uno Nuevo con ese Contenido.'
    txt += ' la ruta donde debe estar ubicado este arhivo es [COLOR gold].../.kodi/userdata/[/COLOR]'

    txt += '[CR][CR][COLOR chartreuse][B]Este problema se resuelve:[/B][/COLOR] Con las siguientes Instrucciones[CR]'

    if PY3: txt += ' - [COLOR darkorange][B]Pueden NO funcionar correctamente en su Media Center[/B][/COLOR][CR]'

    txt += '[CR]<!-- Balandro -->[CR]'
    txt += '[COLOR darkorange][B]<advancedsettings  version="1.0">[/B][/COLOR][CR]'
    txt += '[COLOR darkorange][B]   <playlistretries>-1</playlistretries>[/B][/COLOR][CR]'
    txt += '[COLOR darkorange][B]   <playlisttimeout>-1</playlisttimeout>[/B][/COLOR][CR]'
    txt += '[COLOR darkorange][B]</advancedsettings>[/B][/COLOR]'

    platformtools.dialog_textviewer('Preguntas Frecuentes', txt)


def show_help_notice(item):
    logger.info()

    txt = '[COLOR gold][B]COMUNICADO BALANDRO 9/5/2022 20:00[/B][/COLOR]'

    txt += '[CR][CR][COLOR yellow][B][I]Son ya más de 4 años desde la aparición pública de nuestro Addon[/COLOR][COLOR cyan] (2018)[/I][/B][/COLOR]'

    txt += '[CR][CR]Desde [COLOR gold]Enero/2021[/COLOR] hemos solicitado incorporaciones al desarrollo del Addon [COLOR gold](equipo Balandro Team)[/COLOR] por distintas vías, y todos nuestros intentos han sido infructuosos hasta el momento[CR]'

    txt += '[CR][COLOR darkorange]Motivos:[/COLOR][CR]'
    txt += ' - Desconocen la Programación[CR]'
    txt += ' - Desconocen el lenguaje Python[CR]'
    txt += ' - No disponen de Tiempo para ello[CR]'
    txt += ' - No están Interesados[CR]'
    txt += ' - Solo se comprometen a intervenciones Puntuales[CR]'

    txt += '[CR][COLOR darkorange]Situación:[/COLOR][CR]'
    txt += '  [COLOR chartreuse][B]El Addon se seguirá manteniendo[/B][/COLOR], pero nos va a ser del todo imposible, acomenter el mantenimiento del mismo como ha sido hasta ahora, a no ser que realmente vengan [COLOR gold]Nuevas Incorporaciones a Balandro Team[/COLOR] con un compromiso y complicidad total[CR]'

    txt += '[CR]  El principal miembro de [COLOR gold]Balandro Team[/COLOR] y responsable del mantenimiento, ya ha superado una edad sexagenaria, y se agotó de este cometido[CR]'

    txt += '[CR]  Tan solo vamos a efectuar los [COLOR chartreuse][B]Mínimos cambios en Canales y Servidores[/B][/COLOR], que no sufran una alteración radical de estructura, y no abordaremos [COLOR gold]Jamás[/COLOR], ni [COLOR chartreuse][B]Nuevos Canales/Servidores[/B][/COLOR], ni [COLOR chartreuse][B]Mejoras[/B][/COLOR], reservandonos el derecho incluso de [COLOR chartreuse][B]Desactivar[/B][/COLOR] lo que nos de un quebradero de cabeza[CR]'

    txt += '[CR][COLOR darkorange]Conclusión:[/COLOR][CR]'
    txt += '  Somos conscientes, que con el paso del tiempo, el Addon sufra una degradación y deje de cumplir vuestras expectativas sobre el, pero también debeís tener presente, que nosotros así mismo tenemos nuestras vidas y existe más vida fuera del Media Center Kodi[CR]'

    txt += '[CR]Saludos, Balandro Team[CR]'

    platformtools.dialog_textviewer('Comunicado Oficial de Balandro', txt)


def show_not_contemplated(item):
    logger.info()

    txt ='[COLOR red][B]¿ Qué temas no están Implementados dentro de Balandro ?[/B][/COLOR][CR][CR]'

    txt += '[COLOR yellow][B] - No se pueden Garantizar resultados satisfactorios:[/B][/COLOR][CR]'
    txt += '    - Con Versiones anteriores a [COLOR darkorange][B]17.x[/B][/COLOR] en su Media Center.[CR]'
    txt += '    - Ejecución en Media Centers que vengan Pre-instalados en su equipo tipos [COLOR gold]KdPlayer, KkPlayer ó similares[/COLOR][CR]'
    txt += '    - Ejecución de Balandro bajo [COLOR gold]Builds, Wizards ó Widgets[/COLOR] en su Media Center.[CR]'
    txt += '    - Intervención del fichero [COLOR gold]AdvancedSettings[/COLOR] con sentencias relativas a la memoria de su Media Center[CR][CR]'

    txt += '[COLOR yellowgreen][B] - No Contemplado:[/B][/COLOR][CR]'
    txt += '    - Integración con la [COLOR gold]Videoteca[/COLOR] de su Media Center[CR]'
    txt += '    - Motor Torrent [COLOR gold]Horus / AceStream[/COLOR][CR]'
    txt += '    - Integración con cuentas [COLOR gold]Alldebrid, Realdebrid, ó similares[/COLOR][CR]'
    txt += '    - Integración con [COLOR gold]Trak.Tv[/COLOR] seguimiento de Películas y/ó Series[CR][CR]'

    txt += '[COLOR seagreen][B] - Descargas:[/B][/COLOR][CR]'
    txt += '   - Descargar [COLOR gold]Todos[/COLOR] los Capítulos de una Temporada alunísono[CR]'
    txt += '   - NO se admiten las descargas de ficheros en formatos [COLOR gold]m3u8,  mpd,  rtmp,  torrent[/COLOR][CR]'
    txt += '   - NO están permitidas las descargas de ficheros en formato Comprimido [COLOR gold]zip,  rar,  etc.[/COLOR][CR][CR]'

    txt += '[COLOR gold][B] - Servidores:[/B][/COLOR][CR]'
    txt += '    - Cuentas Premium en el servidor [COLOR darkorange][B]Uptobox[/B][/COLOR][CR]'
    txt += '    - Algunos Servidores que dada su complejidad para efectuar [COLOR orchid][B]Play[/B][/COLOR] [COLOR gold]No están Soportados[/COLOR][CR][CR]'

    txt += '[COLOR cyan][B] - Listas:[/B][/COLOR][CR]'
    txt += '   - Acceder a [COLOR gold]Una Página Concreta[/COLOR] en los listados de las opciones de los canales[CR]'
    txt += '   - Incluir el [COLOR gold]Rating[/COLOR] en los listados de las opciones de los canales[CR]'

    platformtools.dialog_textviewer('¿ Qué NO está contemplado en Balandro ?', txt)


def show_not_download(item):
    logger.info()

    txt ='[COLOR red][B]¿ Qué temas no están Implementados en las Descargas ?[/B][/COLOR][CR][CR]'

    txt += ' - Descargar [COLOR gold]Todos[/COLOR] los Capítulos de una Temporada alunísono[CR]'
    txt += ' - NO se admiten las descargas de ficheros en formatos [COLOR gold]m3u8,  mpd,  rtmp,  torrent[/COLOR][CR]'
    txt += ' - NO están permitidas las descargas de ficheros en formato Comprimido [COLOR gold]zip,  rar,  etc.[/COLOR][CR]'

    platformtools.dialog_textviewer('¿ Qué NO está contemplado en las Descargas ?', txt)


def show_help_tracking(item):
    logger.info()

    txt = '[COLOR gold]¿ Cómo se guardan las películas ó series ?[/COLOR][CR]'
    txt += 'Desde cualquiera de los canales donde se listen películas ó series, accede al [COLOR yellow][B]Menú Contextual[/B][/COLOR] y selecciona [COLOR gold]Guardar película/serie[/COLOR].'
    txt += ' En el caso de películas es casi instantáneo, y para series puede demorarse unos segundos si tiene muchas temporadas/episodios.'
    txt += ' Para ver y gestionar todo lo que tengas, accede a [COLOR gold]Preferidos[/COLOR] desde el menú principal del addon.'
    txt += ' También puedes guardar una temporada ó episodios concretos.'

    txt += '[CR][CR][COLOR gold]¿ Qué pasa si una película/serie no está correctamente identificada ?[/COLOR][CR]'
    txt += 'Esto puede suceder cuando la película/serie no está bien escrita en la web de la que procede ó si hay varias películas con el mismo título.'
    txt += ' Si no se detecta te saldrá un diálogo para seleccionar entre varias opciones ó para cambiar el texto de búsqueda.'
    txt += ' Desde las opciones de configuración puedes activar que se muestre siempre el diálogo de confirmación, para evitar que se detecte incorrectamente.'

    txt += '[CR][CR][COLOR gold]¿ Y si no se puede identificar la película/serie ?[/COLOR][CR]'
    txt += 'Es necesario poder identificar cualquier película/serie en TMDB, sino no se puede guardar.'
    txt += ' Si no existe en [COLOR gold]themoviedb.org[/COLOR] ó tiene datos incompletos puedes completar allí la información ya que es un proyecto comunitario y agradecerán tu aportación.'

    txt += '[CR][CR][COLOR gold]¿ Se puede guardar la misma película/serie desde canales diferentes ?[/COLOR][CR]'
    txt += 'Sí, al guardar se apuntan en la base de datos interna los datos propios de la película, serie, temporada ó episodio, y también el enlace al canal de donde se ha guardado.'
    txt += ' De esta manera puedes tener diferentes alternativas por si algún canal fallara ó no tuviera enlaces válidos.'
    txt += ' Si tienes enlaces de varios canales, al reproducir podrás escoger en cual intentarlo.'

    txt += '[CR][CR][COLOR gold]¿ Se guardan las marcas de películas/episodios ya vistos ?[/COLOR][CR]'
    txt += 'Sí, su Media Center gestiona automáticamente las marcas de visto/no visto.'
    txt += ' Estas marcas están en la base de datos de su Media Center pero no en las propias de Balandro.'

    txt += '[CR][CR][COLOR gold]¿ Qué pasa si un enlace guardado deja de funcionar ?[/COLOR][CR]'
    txt += 'A veces las webs desaparecen ó cambian de estructura y/ó de enlaces, y eso provoca que en Preferidos dejen de ser válidos.'
    txt += ' Al acceder a un enlace que da error, se muestra un diálogo para escoger si se quiere [COLOR gold]Buscar en otros canales[/COLOR] ó [COLOR gold]Volver a buscar en el mismo canal[/COLOR].'
    txt += ' Si la web ha dejado de funcionar deberás buscar en otros canales, pero si ha sufrido cambios puedes volver a buscar en ella.'

    txt += '[CR][CR][COLOR gold]¿ Se puede compartir una lista de Preferidos ?[/COLOR][CR]'
    txt += 'De momento puedes hacerlo manualmente. En la carpeta userdata del addon, dentro de [COLOR gold]tracking_dbs[/COLOR] están los ficheros [COLOR gold].sqlite[/COLOR] de cada lista que tengas creada.'
    txt += ' Puedes copiar estos ficheros y llevarlos a otros dispositivos.'

    txt += '[CR][CR][COLOR gold]¿ Cómo invertir el orden de los episodios ?[/COLOR][CR]'
    txt += 'Por defecto los episodios dentro de una temporada se muestran en orden ascendente, del primero al último.'
    txt += ' Si prefieres que sea al revés, desde el [COLOR yellow][B]Menú Contextual[/B][/COLOR] de una temporada selecciona [COLOR gold]Invertir el orden de los episodios[/COLOR] y'
    txt += ' tu preferencia quedará guardada para esa temporada.'

    txt += '[CR][CR][COLOR gold]¿ Hay alguna límitación en los episodios a guardar por cada temporada ?[/COLOR][CR]'
    txt += 'Si, no se almacenarán más de [COLOR red]50 episodios por temporada [/COLOR], si fuera necesario, debe gestionar esa serie y/ó temporada'
    txt += ' a través de los [COLOR gold]favoritos/videoteca genérica[/COLOR] de su Media Center.'

    txt += '[CR][CR][COLOR gold]¿ Cómo integrar los Preferidos en la Videoteca de su Media Center? ?[/COLOR][CR]'
    txt += 'Una alternativa es añadir los Preferidos de Balandro a los [COLOR gold]favoritos/videoteca genérica[/COLOR] de su Media center.'
    txt += ' ó bien, añadir el contenido de Preferidos de Balandro a la [COLOR gold]Videoteca genérica[/COLOR] de su Media center, con el addon externo [COLOR gold]ADD TO LIB[/COLOR]'

    platformtools.dialog_textviewer('Preferidos y su Funcionamiento', txt)


def show_help_tracking_update(item):
    logger.info()

    txt = '[COLOR gold]¿ Qué es el servicio de búsqueda de nuevos episodios ?[/COLOR][CR]'
    txt += 'El servicio es un proceso de Balandro que se ejecuta al iniciarse su Media Center, y se encarga de comprobar cuando hay que buscar actualizaciones.'
    txt += ' En la configuración dentro de [COLOR gold]Actualizar[/COLOR] puedes indicar cada cuanto tiempo deben hacerse las comprobaciones.'
    txt += ' Por defecto es dos veces al día, cada 12 horas, pero puedes cambiarlo.'
    txt += ' Si lo tienes desactivado, puedes ejecutar manualmente la misma búsqueda desde el [COLOR yellow][B]Menú Contextual[/B][/COLOR] de [COLOR gold]Series[/COLOR] dentro de [COLOR gold]Preferidos[/COLOR].'

    txt += '[CR][CR][COLOR gold]¿ Cómo se activa la búsqueda de nuevos episodios para series ?[/COLOR][CR]'
    txt += 'Desde el listado de series dentro de [COLOR gold]Preferidos[/COLOR] accede a [COLOR gold]Gestionar serie[/COLOR] desde el [COLOR yellow][B]Menú Contextual[/B][/COLOR].'
    txt += ' Al seleccionar [COLOR gold]Programar búsqueda automática de nuevos episodios[/COLOR] podrás definir el seguimiento que quieres darle a la serie'
    txt += ' e indicar cada cuanto tiempo hay que hacer la comprobación de si hay nuevos episodios.'

    txt += '[CR][CR][COLOR gold]¿ Cómo se combina el servicio con las series ?[/COLOR][CR]'
    txt += 'Cada vez que se ejecuta el servicio (1, 2, 3 ó 4 veces por día) se buscan las series que tienen activada la búsqueda automática.'
    txt += ' Por cada serie según su propia periodicidad se ejecuta ó no la búsqueda.'
    txt += ' Esto permite por ejemplo tener series que sólo requieren una actualización por semana, y otras donde conviene comprobar cada día.'

    txt += '[CR][CR][COLOR gold]¿ Porqué la búsqueda de nuevos episodios está desactivada por defecto ?[/COLOR][CR]'
    txt += 'Es preferible ser prudente con las actualizaciones para no saturar más las webs de donde se obtiene la información.'
    txt += ' Por esta razón al guardar series por defecto no tienen activada la comprobación de nuevos episodios y hay que indicarlo explícitamente si se quiere.'
    txt += ' Si por ejemplo sigues una serie ya terminada seguramente no necesitarás buscar nuevos episodios, en cambio si sigues una serie de un show diario sí te interesará.'

    txt += '[CR][CR][COLOR gold]¿ Dónde se ven los nuevos episodios encontrados ?[/COLOR][CR]'
    txt += 'En [COLOR gold]Preferidos[/COLOR] estarán dentro de sus series respectivas, pero también se puede ver un listado de los últimos episodios añadidos'
    txt += ' por fecha de emisión ó de actualización en los canales.'

    platformtools.dialog_textviewer('Búsqueda automática de nuevos episodios', txt)

def show_help_descargas(item):
    logger.info()

    txt = '[CR][CR][COLOR cyan][B]Uso[/B][/COLOR] [COLOR seagreen][B]Descargas:[/B][/COLOR][CR][CR]'
    txt += 'Descarga algunas películas para tener listas para ver sin depender de la saturación de la red/servidores en momentos puntuales.'
    txt += ' Desde cualquier película/episodio, tanto en los [COLOR gold][B]Canales[/B][/COLOR] como en [COLOR wheat][B]Preferidos[/B][/COLOR], accede al [COLOR yellow][B]Menú Contextual[/B][/COLOR] y [COLOR gold]Descargar vídeo[/COLOR].'
    txt += ' Selecciona alguno de los enlaces igual que cuando se quiere reproducir y empezará la descarga.'
    txt += ' Para ver lo descargado, accede a [COLOR seagreen][B]Descargas[/B][/COLOR] desde el menú principal.'

    txt += '[CR][CR][COLOR cyan][B]Restricciones[/B][/COLOR] en las [COLOR seagreen][B]Descargas:[/B][/COLOR][CR][CR]'
    txt += ' - Descargar [COLOR gold]Todos[/COLOR] los Capítulos de una Temporada alunísono[CR]'
    txt += ' - NO se admiten las descargas de ficheros en formatos [COLOR gold]m3u8,  mpd,  rtmp,  torrent[/COLOR][CR]'
    txt += ' - NO están permitidas las descargas de ficheros en formato Comprimido [COLOR gold]zip,  rar,  etc.[/COLOR][CR]'

    platformtools.dialog_textviewer('Descargas y su Funcionamiento', txt)

def show_help_usb(item):
    logger.info()

    txt = '[COLOR cyan][B]SI[/B][/COLOR] se puede descargar directamente a una [COLOR goldenrod][B]Unidad USB[/B][/COLOR][CR]'
    txt += 'Para ello deberá indicarlo en la Configuración, categoría [COLOR seagreen][B]Descargas[/B][/COLOR] apartado Ubicación'

    txt += '[CR][CR][B][COLOR chartreuse]Si observase lentitud, parones, ó cualquier otra anomalía durante la [COLOR seagreen][B]Descarga[/B][/COLOR][COLOR chartreuse][B]:[/COLOR][/B][/COLOR][CR]'
    txt += '  Le [COLOR yellow]sugerimos[/COLOR] que efectue la [COLOR seagreen][B]descarga[/B][/COLOR] en la [COLOR gold][B]carpeta por defecto de la configuración[B][/COLOR][CR]'
    txt += '  y una vez finalizada, [COLOR cyan][B]Obtenga una Copia[/B][/COLOR] de esa [COLOR seagreen][B]descarga[/B][/COLOR] hacia la [COLOR goldenrod][B]Unidad USB[/B][/COLOR][CR]'
    txt += '  desde la opción del menú [COLOR seagreen][B]Descargas[/B][/COLOR] al seleccionar cualquier fichero existente en [COLOR seagreen][B]Descargas[/B][/COLOR].[CR]'

    txt += '[CR]También puede [COLOR cyan][B]Obtener una Copia[/B][/COLOR] de su [COLOR seagreen][B]descarga[/B][/COLOR] hacia una [COLOR goldenrod][B]Unidad USB[/B][/COLOR][CR]'
    txt += 'seleccionando cualquier fichero existente en sus [COLOR seagreen][B]Descargas[/B][/COLOR].[CR]'


    platformtools.dialog_textviewer('¿ Se puede Descargar directamente en una Unidad USB ?', txt)


def show_help_proxies(item):
    logger.info()

    txt = '[COLOR gold][B]¿ Porqué en algunos canales hay una opción para configurar proxies ?[/B][/COLOR][CR]'
    txt += 'Ciertos canales sufren bloqueos por parte de algunos países/operadoras que no permiten acceder a su contenido.'
    txt += ' Mediante el uso de proxies se puede evitar esa restricción.'

    txt += '[CR][CR][COLOR gold][B]¿ En qué canales hay que usar los proxies ?[/B][/COLOR][CR]'
    txt += 'Depende de la conexión de cada usuario (el país dónde se conecta, con qué operadora, qué dns tiene configurados, si usa ó no vpn, ...).'
    txt += ' Lo más aconsejable es probar primero si funcionan sin necesidad de proxies ya que es lo más cómodo y rápido.'
    txt += ' Aunque un canal tenga la opción de proxies no es obligatorio usarlos, hacerlo solamente si es necesario.'

    txt += '[CR][CR][COLOR gold][B]¿ Se pueden descartar los canales que requieren proxies ?[/B][/COLOR][CR]'
    txt += 'Sí, desde la opción dentro de buscar [COLOR goldenrod][B]Excluir canales en las búsquedas[/B][/COLOR].'
    txt += 'También, desde el listado de canales de películas y/ó series, en el [COLOR yellow][B]Menú Contextual[/B][/COLOR] se pueden desactivar los canales deseados.'
    txt += ' De esta manera quedarán descartados para las búsquedas globales, se evitarán sus mensajes relacionados con los proxies'
    txt += ' y se acelerará la búsqueda.'

    txt += '[CR][CR][COLOR gold][B]¿ Cómo se usa la configuración de proxies ?[/B][/COLOR][CR]'
    txt += 'Por defecto en la configuración de Balandro esta activada la opción [COLOR goldenrod][B]Buscar proxies automáticamente[/B][/COLOR] ello efectua un barrido de búsqueda de acuerdo con el proveedor informado.'

    txt += '[CR][CR]En la configuración de [COLOR goldenrod][B]Proxies[/B][/COLOR] se pueden personalizar (Dejar de buscar si se hallaron suficientes válidos, Proveedor de proxies habitual, Limitar la cantidad de válidos a memorizar,'
    txt += ' las solicitudes de Anonimidad, País, etc.)'

    txt += '[CR][CR]En el caso de No obtener suficientes proxies, se puede [COLOR goldenrod][B]Aumentar/No Limitar[/B][/COLOR] el número de proxies válidos a buscar en los [COLOR yellow][B]Apartados Proceso/Especiales[/B][/COLOR] de la [COLOR yellow][B]Categoría Proxies[/B][/COLOR] dentro de la [COLOR goldenrod][B]Configuración[/COLOR] de Balandro'

    txt += '[CR][CR][COLOR gold][B]¿ Cómo funciona el proceso de Búsqueda ?[/B][/COLOR][CR]'
    txt += 'Una vez finalizado el Proceso de Búsqueda se presentará la consola de resultados con varias [COLOR goldenrod][B]Opciones:[/B][/COLOR]'

    txt += '[CR][CR] - La primera opción [COLOR goldenrod][B]Informar proxies manualmente[/B][/COLOR] es para indicar manualmente los proxies a usar.'
    txt += '[CR] - La segunda opción [COLOR goldenrod][B]Buscar nuevos proxies[/B][/COLOR] es para realizar una búsqueda de proxies para el canal.'
    txt += '[CR] - La tercera opción [COLOR goldenrod][B]Parámetros búsquedas[/B][/COLOR] sirve para configurar ciertas opciones para la búsqueda de proxies.'

    txt += '[CR][CR] - Las opciones por defecto son suficientes, pero si no se obtubieran resultados, pueden cambiar algúno de los parámetros para el proceso (el proveedor de dónde se obtienen, el tipo de proxy, ...).'

    txt += '[CR][CR] - Por defecto, los tres proxies más rápidos entre los válidos se guardarán en la configuración del canal.'

    txt += '[CR][CR][COLOR gold][B]¿ Como quitar los proxies en un canal determinado ?[/B][/COLOR][CR]'
    txt += 'Pulsación sostenida sobre el texto [COLOR goldenrod][B]Configurar proxies a usar ... [/B][/COLOR]dentro del canal y ahí aparecerá un [COLOR yellow][B]Menú Contextual[/B][/COLOR] con esa opción,'
    txt += ' ó bien dentro del proceso de buscar proxies, en la consola de resultados la opción [COLOR goldenrod][B]Quitar proxies[/B][/COLOR].'

    txt += '[CR][CR][COLOR gold][B]¿ Se ralentizan los canales si se utilizan proxies ?[/B][/COLOR][CR]'
    txt += 'Sí, acceder a las webs de los canales a través de proxies ralentiza considerablemente lo que tardan en responder.'
    txt += ' Aún así, [COLOR yellowgreen][B]hay proxies más rápidos que otros, ó más estables, ó menos saturados, ó más duraderos, gratuítos ó de pago, etc.[/B][/COLOR]'

    txt += '[CR][CR][COLOR gold][B]¿ Porqué muchos proxies dejan de funcionar ?[/B][/COLOR][CR]'
    txt += 'Los proxies que se pueden encontrar en la búsqueda [COLOR yellowgreen][B]son todos gratuítos pero tienen ciertas limitaciones y no siempre están activos.[/B][/COLOR]'
    txt += ' Para cada canal se guardan los proxies a utilizar, pero es posible que algunos días cuando entres tengas que volver a hacer una búsqueda de proxies porque han dejado de funcionar.'

    platformtools.dialog_textviewer('Uso de Proxies', txt)


def show_channels_parameters(item):
    txt = ''

    txt += '[COLOR yellow][B]CANALES:[/B][/COLOR]'

    todos = True

    if config.get_setting('mnu_simple', default=False):
        todos = False

        txt += '[CR] - Opera con el Menú [B][COLOR crimson]SIMPLIFICADO[/COLOR][/B][CR]'
        txt += '    - No Se Muestran los canales [B][I][COLOR plum]Inestables[/COLOR][/I][/B][CR]'
        txt += '    - No Se Muestran los canales [B][I][COLOR darkgoldenrod]Problemáticos[/COLOR][/I][/B][CR]'
    else:
        if config.get_setting('channels_list_no_inestables', default=False): todos = False
        if config.get_setting('channels_list_no_problematicos', default=False): todos = False

    channels_list_status = config.get_setting('channels_list_status', default=0)

    if channels_list_status == 0: 
       if todos: txt += '[CR] - Se Muestran [B][COLOR goldenrod]TODOS LOS CANALES[/COLOR][/B][CR]'
       else: txt += '[CR] - Se Muestran Solo [B][COLOR goldenrod]DETERMINADOS CANALES[/COLOR][/B][CR]'

    elif channels_list_status == 1: txt += '[CR] - Solo se Muestran los canales [B][COLOR goldenrod]PREFERIDOS Y ACTIVOS[/COLOR][/B][CR]'
    else: txt += '[CR] - Solo se Muestran los canales [B][COLOR goldenrod]PREFERIDOS[/COLOR][/B][CR]'
 
    if config.get_setting('channels_list_order', default=True):
        txt +='[CR] - Se Presentan los canales [B][COLOR gold]Preferidos[/COLOR][/B] al principio de las Listas[CR]'

    if config.get_setting('channels_list_no_inestables', default=False):
        txt += '[CR] - No se presentan los canales [COLOR plum][B]Inestables[/B][/COLOR][CR]'

    if config.get_setting('channels_list_no_problematicos', default=False):
        txt += '[CR] - No se presentan los canales [COLOR darkgoldenrod][B]Problemáticos[/B][/COLOR][CR]'

    txt += '[CR]'

    txt_disableds = _menu_parameters()

    if txt_disableds:
        txt += '[COLOR yellow][B]MENÚS:[/B][/COLOR][CR]'
        txt += txt_disableds

    txt_specials = _menu_specials()

    if txt_specials:
        txt += '[COLOR yellow][B]MENÚS Y SUB-MENÚS:[/B][/COLOR][CR]'
        txt += txt_specials

    if descartar_anime or descartar_xxx:
        txt += '[COLOR yellow][B]PARENTAL:[/B][/COLOR][CR]'

        if descartar_anime: txt += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción para Descartar los Canales Exclusivos de [B][COLOR springgreen]Animes[/COLOR][/B][CR]'
        if descartar_xxx: txt += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción para Descartar los Canales Exclusivos de [B][COLOR orange]Adultos[/COLOR][/B][CR]'

    if config.get_setting('developer_mode', default=False):
        txt += '[COLOR yellow][B]DESARROLLO:[/B][/COLOR]'

        txt += '[CR] - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú [B][COLOR darkorange]Desarrollo[/COLOR][/B] en los ajustes categoría [B][COLOR goldenrod]Team[/COLOR][/B]'

    platformtools.dialog_textviewer('Información Parámetros Actuales para Mostrar los Canales en las Listas', txt)


def show_play_parameters(item):
    txt = ''

    txt += '[COLOR yellow][B]PLAY:[/B][/COLOR]'

    txt += '[CR][CR][COLOR orchid][B] - ADDONS EXTERNOS y VIAS ALTERNATIVAS:[/B][/COLOR]'

    cliente_torrent = config.get_setting('cliente_torrent', default='Seleccionar')

    if cliente_torrent == 'Seleccionar' or cliente_torrent == 'Ninguno': tex_tor = cliente_torrent
    else:
       tex_tor = cliente_torrent
       cliente_torrent = 'plugin.video.' + cliente_torrent.lower()
       if xbmc.getCondVisibility('System.HasAddon("%s")' % cliente_torrent):
           cod_version = xbmcaddon.Addon(cliente_torrent).getAddonInfo("version").strip()
           tex_tor += '  [COLOR goldenrod]' + cod_version + '[/COLOR]'

    txt +='[CR]    - Cliente/Motor Torrent Habitual asignado ' + '[COLOR orchid][B] ' + tex_tor + '[/B][/COLOR]'

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        cod_version = xbmcaddon.Addon("script.module.resolveurl").getAddonInfo("version").strip()
        tex_yt = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_yt = '  [COLOR red]No instalado[/COLOR]'

    txt +='[CR]    - [COLOR orchid][B]ResolveUrl[/B][/COLOR] ' + '[COLOR yellowgreen][B] ' + tex_yt + '[/B][/COLOR]'

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
        cod_version = xbmcaddon.Addon("plugin.video.youtube").getAddonInfo("version").strip()
        tex_yt = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
    else: tex_yt = '  [COLOR red]No instalado[/COLOR]'

    txt +='[CR]    - [COLOR orchid][B]Youtube[/B][/COLOR] ' + '[COLOR yellowgreen][B] ' + tex_yt + '[/B][/COLOR]'

    txt += '[CR][CR][COLOR fuchsia][B] - AUTO PLAY:[/B][/COLOR]'

    if config.get_setting('autoplay', default=False): txt +='[CR]    - [COLOR yellowgreen][B] Activado[/B][/COLOR]'
    else: txt +='[CR]    - [COLOR yellowgreen][B] Des-Activado[/B][/COLOR]'

    if config.get_setting('autoplay_one_link', default=False): txt +='[CR]    -  Si solo hay [COLOR gold][B]Un enlace[/B][/COLOR] para reproducir[COLOR yellowgreen][B] Activado[/B][/COLOR]'
    else: txt +='[CR]    -  Si solo hay [COLOR gold][B]Un enlace[/B][/COLOR] para reproducir[COLOR yellowgreen][B] Des-Activado[/B][/COLOR]'

    if config.get_setting('autoplay_channels_discarded', default=''):
        txt +='[CR]    -  Servidores descartados [COLOR gray][B] ' + str(config.get_setting('autoplay_channels_discarded')) + '[/B][/COLOR]'

    txt += '[CR][CR][COLOR fuchsia][B] - ORDENAR Y/Ó FILTRAR POR IDIOMA:[/B][/COLOR]'

    tex_idio = 'Descartar'
    if config.get_setting('preferencia_idioma_esp') == 1: tex_idio = 'Primero'
    elif config.get_setting('preferencia_idioma_esp') == 2: tex_idio = 'Segundo'
    elif config.get_setting('preferencia_idioma_esp') == 3: tex_idio = 'Tercero'

    txt +='[CR]    -  Idioma [COLOR red][B]Esp[/B][/COLOR] (castellano de España) ' +  '[COLOR yellowgreen][B] ' + tex_idio + '[/B][/COLOR]'

    tex_idio = 'Descartar'
    if config.get_setting('preferencia_idioma_lat') == 1: tex_idio = 'Primero'
    elif config.get_setting('preferencia_idioma_lat') == 2: tex_idio = 'Segundo'
    elif config.get_setting('preferencia_idioma_lat') == 3: tex_idio = 'Tercero'

    txt +='[CR]    -  Idioma [COLOR red][B]Lat[/B][/COLOR] (castellano de América) ' +  '[COLOR yellowgreen][B] ' + tex_idio + '[/B][/COLOR]'

    tex_idio = 'Descartar'
    if config.get_setting('preferencia_idioma_vos') == 1: tex_idio = 'Primero'
    elif config.get_setting('preferencia_idioma_vos') == 2: tex_idio = 'Segundo'
    elif config.get_setting('preferencia_idioma_vos') == 3: tex_idio = 'Tercero'

    txt +='[CR]    -  Idioma [COLOR red][B]Vose, VO[/B][/COLOR] (versión Subtitulada y/ó Original) ' +  '[COLOR yellowgreen][B] ' + tex_idio + '[/B][/COLOR]'

    txt += '[CR][CR][COLOR fuchsia][B] - ORDENAR POR CALIDAD:[/B][/COLOR]'

    tex_qlty = 'Orden de la Web'

    if config.get_setting('servers_sort_quality') == 1: tex_qlty = 'Calidad Descendente'
    elif config.get_setting('servers_sort_quality') == 2: tex_qlty = 'Calidad Ascendente'

    txt +='[CR]    -  En cada idioma ordenar los enlaces según ' +  '[COLOR yellowgreen][B] ' + tex_qlty + '[/B][/COLOR]'

    if config.get_setting('servers_preferred', default='') or config.get_setting('servers_unfavored', default='') or config.get_setting('servers_discarded', default=''):
        txt += '[CR][CR][COLOR fuchsia][B] - FILTRAR SERVIDORES:[/B][/COLOR]'

        if config.get_setting('servers_preferred', default=''):
            txt +='[CR]    -  Servidores [COLOR darkorange][B]Preferidos [COLOR gold] ' + str(config.get_setting('servers_preferred')) + '[/B][/COLOR]'

        if config.get_setting('servers_unfavored', default=''):
            txt +='[CR]    -  Servidores como [COLOR gold][B]Última opción [COLOR blue][B]' + str(config.get_setting('servers_unfavored')) + '[/B][/COLOR]'

        if config.get_setting('servers_discarded', default=''):
            txt +='[CR]    -  Servidores [COLOR cyan][B]Descartados [COLOR gray][B]' + str(config.get_setting('servers_discarded')) + '[/B][/COLOR]'

    platformtools.dialog_textviewer('Información Parámetros Actuales en Play', txt)


def show_prx_parameters(item):
    default_provider = 'proxyscrape.com'
    all_providers = 'All-providers'
    private_list = 'Lista-proxies.txt'

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

    txt = ''

    txt += '[COLOR yellow][B]PROVEEDORES:[/B][/COLOR]'

    provider = config.get_setting('proxies_provider')
    provider = opciones_provider[provider]

    txt += '[CR][COLOR red][B] - Proveedor Habitual:[/B][/COLOR]' + ' [COLOR yellowgreen][B]' + provider + '[/B][/COLOR][CR]'

    txt += '[CR][COLOR red][B] - Ampliar Lista de Proveedores:[/B][/COLOR]'

    if config.get_setting('proxies_extended', default=False): txt += ' [COLOR yellowgreen][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR yellowgreen][B] Des-Activado[/B][/COLOR]'

    txt += '[CR][COLOR red][B] - Solo tener en cuenta al procesar los Proveedores Recomendados:[/B][/COLOR]'

    if config.get_setting('proxies_recommended', default=False): txt += '[COLOR yellowgreen][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR yellowgreen][B] Des-Activado[/B][/COLOR]'

    txt += '[CR][COLOR red][B] - Tratar Primero en las búsquedas los Proveedores de la Lista Ampliada:[/B][/COLOR]'

    if config.get_setting('proxies_search_extended', default=False): txt += ' [COLOR yellowgreen][B] Activado[/B][/COLOR][CR]'
    else: txt += ' [COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    if config.get_setting('providers_preferred', default=''):
        txt += '[CR][COLOR red][B] - Tratar Solo los Proveedores Preferidos:[/B][/COLOR]'
        txt +='[CR]    - [COLOR yellowgreen][B]' + str(config.get_setting('providers_preferred')) + '[/B][/COLOR][CR]'

    txt += '[CR][COLOR yellow][B]PROCESOS:[/B][/COLOR]'

    txt += '[CR][COLOR red][B] - Buscar Automáticamente (solo si Proveedor Habitual Todos/All-Providers):[/B][/COLOR]'

    if config.get_setting('proxies_auto', default=True): txt +='[CR]    - [COLOR yellowgreen][B] Activado[/B][/COLOR][CR]'
    else: txt +='[CR]    - [COLOR yellowgreen][B] Des-Activado[/B][/COLOR][CR]'

    txt += '[CR][COLOR red][B] - Límite Máximo Total de proxies para Analizar:[/B][/COLOR]' + ' [COLOR yellowgreen][B]' + str(config.get_setting('proxies_totales_limit')) + '[/B][/COLOR]'

    txt += '[CR][COLOR red][B] - Si se encontraron Suficientes proxies válidos dejar de buscar más:[/B][/COLOR]'

    if config.get_setting('proxies_limit', default=False): txt += ' [COLOR yellowgreen][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR yellowgreen][B] Des-Activado[/B][/COLOR]'

    txt += '[CR][COLOR red][B] - Limitar la Cantidad de proxies válidos:[/B][/COLOR]'

    if config.get_setting('proxies_validos', default=True): txt += ' [COLOR yellowgreen][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR yellowgreen][B] Des-Activado[/B][/COLOR]'

    txt += '[CR][COLOR red][B] - Cantidad Máxima de proxies válidos:[/B][/COLOR]' + ' [COLOR yellowgreen][B]' + str(config.get_setting('proxies_memory')) + '[/B][/COLOR][CR]'

    txt += '[CR][COLOR yellow][B]SOLICITUDES:[/B][/COLOR]'

    txt += '[CR][COLOR red][B] - Solicitar el tipo de Anonimidad:[/B][/COLOR]'

    if config.get_setting('proxies_tipos', default=False): txt += ' [COLOR yellowgreen][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR yellowgreen][B] Des-Activado[/B][/COLOR]'

    txt += '[CR][COLOR red][B] - Solicitar el País:[/B][/COLOR]'

    if config.get_setting('proxies_paises', default=False): txt += ' [COLOR yellowgreen][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR yellowgreen][B] Des-Activado[/B][/COLOR]'

    txt += '[CR][COLOR red][B] - No solicitar y forzar el Valor máximo de los proxies a analizar:[/B][/COLOR]'

    if config.get_setting('proxies_maximo', default=True): txt += ' [COLOR yellowgreen][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR yellowgreen][B] Des-Activado[/B][/COLOR]'

    if config.get_setting('proxies_list', default=False):
        txt += '[CR][COLOR red][B] - Habilitar la selección de su Lista Personalizada:[/B][/COLOR]' + ' [COLOR yellowgreen][B] Activado[/B][/COLOR][CR]'

    platformtools.dialog_textviewer('Información Parámetros Actuales en Proxies', txt)


def _menu_parameters():
    txt_disableds = ''

    if not config.get_setting('mnu_sugeridos', default=True):
        txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR aquamarine]Sugeridos[/COLOR][/B][CR][CR]'

    if not config.get_setting('channels_link_main', default=True):
        txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR gold]Canales[/COLOR][/B][CR][CR]'

    if not config.get_setting('mnu_idiomas', default=True):
        txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR limegreen]Idiomas[/COLOR][/B][CR][CR]'
    else:
        if config.get_setting('mnu_problematicos', default=False):
            txt_disableds += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal [B][COLOR limegreen]Idiomas[/COLOR][/B][CR]'

            txt_disableds += '   Además NO se mostrarán los canales que sean [COLOR darkgoldenrod]Problemáticos[/COLOR][CR][CR]'

    if not config.get_setting('mnu_grupos', default=True):
        txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR magenta]Grupos[/COLOR][/B][CR][CR]'
    else:
        if config.get_setting('mnu_problematicos', default=False):
            txt_disableds += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal [B][COLOR magenta]Grupos[/COLOR][/B][CR]'

            txt_disableds += '   Además NO se mostrarán los canales que sean [COLOR darkgoldenrod]Problemáticos[/COLOR][CR][CR]'

    if config.get_setting('mnu_simple', default=False):
        txt_disableds += ' - [B][COLOR crimson]Menú Simplificado:[/B][/COLOR][CR]'

        txt_disableds += '   - No se presentará [COLOR gold]Jamás[/COLOR] la opción del Menú principal [B][COLOR wheat]Preferidos[/COLOR][/B][CR]'
        txt_disableds += '     Además no se mostrará en los [COLOR yellow][B]Menús Contextuales[/B][/COLOR] la opción [COLOR darkorange][B]Guardar en Preferidos[/B][/COLOR][CR][CR]'

        txt_disableds += '   - No se presentará [COLOR gold]Jamás[/COLOR] la opción del Menú principal [B][COLOR seagreen]Descargas[/COLOR][/B][CR]'
        txt_disableds += '     Además no se mostrará en los [COLOR yellow][B]Menús Contextuales[/B][/COLOR] la opción [COLOR darkorange][B]Descargar Vídeo[/B][/COLOR][CR][CR]'

        txt_disableds += '   - No se presentarán [COLOR gold][B]Nunca[/B][/COLOR] las opciónes de:[CR]'
        txt_disableds += '      - [B][COLOR deepskyblue]Películas[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR hotpink]Series[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR teal]Películas y Series[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR thistle]Géneros[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR cyan]Documentales[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR lightyellow]Infantiles[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR limegreen]Novelas[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR blue]Torrents[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR firebrick]Doramas[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR springgreen]Animes[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR orange]Adultos[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR red]Proxies[/COLOR][/B][CR]'
        txt_disableds += '      - [B][COLOR darkgoldenrod]Problemáticos[/B][/COLOR][CR]'
        txt_disableds += '      - [B][COLOR gray]Desactivados[/COLOR][/B][CR][CR]'

    else:
        if not config.get_setting('mnu_pelis', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR deepskyblue]Películas[/COLOR][/B][CR][CR]'

        if not config.get_setting('mnu_series', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR hotpink]Series[/COLOR][/B][CR][CR]'

        if config.get_setting('channels_link_pyse', default=False):
            txt_disableds += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal [B][COLOR teal]Películas y Series[/COLOR][/B][CR][CR]'
        else:
            txt_disableds += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR coral]Des-Habilitada[/COLOR] la opción del Menú principal [B][COLOR teal]Películas y Series[/COLOR][/B][CR][CR]'

        if not config.get_setting('mnu_generos', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR thistle]Géneros[/COLOR][/B][CR][CR]'
        else:
            if config.get_setting('mnu_problematicos', default=False):
                txt_disableds += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal [B][COLOR thistle]Géneros[/COLOR][/B][CR]'

                txt_disableds += '   Además NO se mostrarán los canales que sean [COLOR darkgoldenrod]Problemáticos[/COLOR][CR][CR]'

        if not config.get_setting('mnu_documentales', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR cyan]Documentales[/COLOR][/B][CR]'

            txt_disableds += '   Además NO se mostrarán en el resto de las opciones del Menú principal los canales que sean [COLOR cyan]Exclusivos de Documentales[/COLOR][CR][CR]'

        if not config.get_setting('mnu_infantiles', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR lightyellow]Infantiles[/COLOR][/B][CR]'

            txt_disableds += '   Además NO se mostrarán en el resto de las opciones del Menú principal los canales que sean [COLOR lightyellow]Exclusivos de Infantiles[/COLOR][CR][CR]'

        if not config.get_setting('mnu_novelas', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR limegreen]Novelas[/COLOR][/B][CR]'

            txt_disableds += '   Además NO se mostrarán en el resto de las opciones del Menú principal los canales que sean [COLOR limegreen]Exclusivos de Novelas[/COLOR][CR][CR]'

        if not config.get_setting('mnu_torrents', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR blue]Torrents[/COLOR][/B][CR]'

            txt_disableds += '   Además NO se mostrarán en el resto de las opciones del Menú principal los canales que sean [COLOR blue]Exclusivos de Torrents[/COLOR][CR][CR]'

        if not config.get_setting('mnu_doramas', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR firebrick]Doramas[/COLOR][/B][CR]'

            txt_disableds += '   Además NO se mostrarán en el resto de las opciones del Menú principal los canales que sean [COLOR firebrick]Exclusivos de Doramas[/COLOR][CR][CR]'

        if not config.get_setting('mnu_animes', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR springgreen]Animes[/COLOR][/B][CR]'

            txt_disableds += '   Además NO se mostrarán en el resto de las opciones del Menú principal los canales que sean [COLOR springgreen]Exclusivos de Animes[/COLOR][CR][CR]'

        if not config.get_setting('mnu_adultos', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR orange]Adultos[/COLOR][/B][CR]'

            txt_disableds += '   Además NO se mostrarán en el resto de las opciones del Menú principal los canales que sean [COLOR orange]Exclusivos para Adultos[/COLOR][CR][CR]'

        if config.get_setting('mnu_proxies', default=False):
            txt_disableds += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal [B][COLOR red]Proxies[/COLOR][/B][CR]'

            txt_disableds += '   Siempre se mostrarán en la Opción del Menú principal [COLOR gold][B]Canales[/B][/COLOR][CR]'

            if config.get_setting('mnu_idiomas', default=True):
                txt_disableds += '   También se mostrarán en la Opción del Menú principal [COLOR limegreen][B]Idiomas[/B][/COLOR][CR]'

            if config.get_setting('mnu_grupos', default=True):
                txt_disableds += '   También se mostrarán en la Opción del Menú principal [COLOR magenta][B]Grupos[/B][/COLOR][CR]'

            txt_disableds += '   Además NO se mostrarán en el [COLOR gold]Resto de las opciones del Menú principal[/COLOR] los canales con [COLOR red]Proxies[/COLOR] Memorizados[CR][CR]'
        else:
            txt_disableds += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR coral]Des-Habilitada[/COLOR] la opción del Menú principal [B][COLOR red]Proxies[/COLOR][/B][CR][CR]'

        if config.get_setting('mnu_problematicos', default=False):
            txt_disableds += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal [B][COLOR darkgoldenrod]Problemáticos[/COLOR][/B][CR]'

            txt_disableds += '   Siempre se mostrarán en la Opción del Menú principal [COLOR gold][B]Canales[/B][/COLOR][CR]'
            txt_disableds += '   Además NO se mostrarán en el resto de las opciones del Menú principal los canales que sean [COLOR darkgoldenrod]Problemáticos[/COLOR][CR][CR]'
        else:
            txt_disableds += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR coral]Des-Habilitada[/COLOR] la opción del Menú principal [B][COLOR darkgoldenrod]Problemáticos[/COLOR][/B][CR][CR]'

        if config.get_setting('mnu_desactivados', default=False):
            txt_disableds += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal [B][COLOR gray]Desactivados[/COLOR][/B][CR]'

            txt_disableds += '   Siempre se mostrarán en la Opción del Menú principal [COLOR gold][B]Canales[/B][/COLOR][CR]'
            txt_disableds += '   Además NO se mostrarán en el resto de las opciones del Menú principal los canales que esten [COLOR gray]Desactivados[/COLOR][CR][CR]'
        else:
            txt_disableds += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR coral]Des-Habilitada[/COLOR] la opción del Menú principal [B][COLOR gray]Desactivados[/COLOR][/B][CR][CR]'

        if not config.get_setting('mnu_preferidos', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR wheat]Preferidos[/COLOR][/B][CR][CR]'

            txt_disableds += '   Además NO se mostrará en los [COLOR yellow][B]Menús Contextuales[/B][/COLOR] la opción [COLOR darkorange][B]Guardar en Preferidos[/B][/COLOR][CR][CR]'

        if not config.get_setting('mnu_desargas', default=True):
            txt_disableds += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal [B][COLOR seagreen]Descargas[/COLOR][/B][CR][CR]'

            txt_disableds += '   Además NO se mostrará en los [COLOR yellow][B]Menús Contextuales[/B][/COLOR] la opción [COLOR darkorange][B]Descargar Vídeo[/B][/COLOR][CR][CR]'

    return txt_disableds


def _menu_specials():
    txt_specials = ''

    if config.get_setting('mnu_search_proxy_channels', default=False):
        txt_specials += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR red]Buscar Nuevos Proxies[/COLOR][/B][CR][CR]'
    else:
        txt_specials += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR coral]Des-Habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR red]Buscar Nuevos Proxies[/COLOR][/B][CR][CR]'

    if config.get_setting('search_extra_proxies', default=True):
        txt_specials += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR red]Búsquedas en Canales con Proxies[/COLOR][/B][CR][CR]'
    else:
        txt_specials += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR plum]Habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR red]Búsquedas en Canales con Proxies[/COLOR][/B][CR][CR]'

    if config.get_setting('sub_mnu_favoritos', default=False):
        txt_specials += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal [B][COLOR plum]Favoritos[/COLOR][/B][CR][CR]'
    else:
        txt_specials += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR coral]Des-Habilitada[/COLOR] la opción del Menú principal [B][COLOR plum]Favoritos[/COLOR][/B][CR][CR]'

    if config.get_setting('search_extra_trailers', default=False):
        txt_specials += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR darkgoldenrod]Tráilers[/COLOR][/B][CR][CR]'
    else:
        txt_specials += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR coral]Des-Habilitada[/COLOR] la opción en los Sub-Menús [B][COLOR darkgoldenrod]Tráilers[/COLOR][/B][CR][CR]'

    if not config.get_setting('sub_mnu_special', default=True):
        txt_specials += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR pink]Especiales[/COLOR][/B][CR][CR]'
    else:
        txt_specials += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR plum]Habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR pink]Especiales[/COLOR][/B][CR][CR]'

    if config.get_setting('search_extra_main', default=False):
        txt_specials += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR violet]Búsquedas Especiales (Listas TMDB, etc.)[/COLOR][/B][CR][CR]'
    else:
        txt_specials += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR coral]Des-Habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR violet]Búsquedas Especiales (Listas TMDB, etc.)[/COLOR][/B][CR][CR]'

    if not config.get_setting('sub_mnu_cfg_search', default=True):
        txt_specials += ' - Tiene [COLOR coral]Des-habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR moccasin]Personalizar Búsquedas[/COLOR][/B][CR][CR]'
    else:
        txt_specials += ' - [COLOR gold]Por Defecto[/COLOR] está [COLOR plum]Habilitada[/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR moccasin]Personalizar Búsquedas[/COLOR][/B][CR][CR]'

    return txt_specials


def show_menu_parameters(item):
    txt = ''

    if config.get_setting('mnu_simple', default=True): txt += 'Opera con el Menú [B][COLOR crimson]SIMPLIFICADO[/COLOR][/B][CR][CR]'

    txt_disableds = _menu_parameters()

    if txt_disableds:
        txt += 'MENÚS:[CR]'
        txt += txt_disableds

    txt_specials = _menu_specials()

    if txt_specials:
        txt += 'MENÚS Y SUB-MENÚS:[CR]'
        txt += txt_specials

    if descartar_anime or descartar_xxx:
        txt += 'PARENTAL:[CR]'

        if descartar_anime: txt += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción para Descartar los Canales Exclusivos de [B][COLOR springgreen]Animes[/COLOR][/B][CR][CR]'
        if descartar_xxx: txt += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción para Descartar los Canales Exclusivos de [B][COLOR orange]Adultos[/COLOR][/B][CR][CR]'

    if config.get_setting('developer_mode', default=False):
        txt += 'DESARROLLO:[CR]'

        txt += ' - Tiene [COLOR plum]Habilitada[/COLOR] la opción del Menú principal [B][COLOR darkorange]Desarrollo[/COLOR][/B] en los ajustes [B][COLOR goldenrod]Team[/COLOR][/B][CR][CR]'

    platformtools.dialog_textviewer('Información Parámetros Actuales para los Menús', txt)


def show_help_providers(item):
    logger.info()

    txt = ''

    if not item.ampliada:
        providers_preferred = config.get_setting('providers_preferred', default='')
        if providers_preferred:
            txt = '[COLOR wheat][B]Proveedores preferidos:[/B][/COLOR][CR]'

            txt += '    [COLOR violet][B]' + str(providers_preferred) + '[/B][/COLOR][CR][CR]'

        txt += '[COLOR goldenrod][B]Proveedores habituales:[/B][/COLOR][CR]'

        txt += '  [COLOR yellow]all-providers[/COLOR][CR]'
        txt += '  [COLOR yellow]almroot[/COLOR][CR]'
        txt += '  [COLOR yellow]clarketm[/COLOR][CR]'
        txt += '  [COLOR yellow]dailyproxylists.com[/COLOR][CR]'
        txt += '  [COLOR yellow]free-proxy-list[/COLOR][CR]'
        txt += '  [COLOR yellow]geonode.com[/COLOR][CR]'
        txt += '  [COLOR yellow]google-proxy.net[/COLOR][CR]'
        txt += '  [COLOR yellow]hidemy.name[/COLOR][CR]'
        txt += '  [COLOR yellow]httptunnel.ge[/COLOR][CR]'
        txt += '  [COLOR yellow]hidester.com[/COLOR][CR]'
        txt += '  [COLOR yellow]ip-adress.com[/COLOR][CR]'
        txt += '  [COLOR yellow]mertguvencli[/COLOR][CR]'
        txt += '  [COLOR red][B]mmpx12[COLOR lime]  recomendado[/B][/COLOR][CR]'
        txt += '  [COLOR yellow]proxy-list.download[/COLOR][CR]'
        txt += '  [COLOR yellow]proxydb.net[/COLOR][CR]'
        txt += '  [COLOR yellow]proxynova.com[/COLOR][CR]'
        txt += '  [COLOR red][B]proxyscrape.com[COLOR lime]  recomendado[/B][/COLOR][CR]'
        txt += '  [COLOR yellow]proxyservers.pro[/COLOR][CR]'
        txt += '  [COLOR yellow]proxysource.org[/COLOR][CR]'
        txt += '  [COLOR yellow]roosterkid[/COLOR][CR]'
        txt += '  [COLOR yellow]shiftytR[/COLOR][CR]'
        txt += '  [COLOR yellow]silverproxy.xyz[/COLOR][CR]'
        txt += '  [COLOR yellow]spys.me[/COLOR][CR]'
        txt += '  [COLOR yellow]spys.one[/COLOR][CR]'
        txt += '  [COLOR yellow]sslproxies.org[/COLOR][CR]'
        txt += '  [COLOR red][B]us-proxy.org[COLOR lime]  recomendado[/B][/COLOR][CR]'

    if config.get_setting('proxies_extended', default=False):
        txt += '[CR][COLOR aqua][B]Lista ampliada de proveedores:[/B][/COLOR][CR]'

        txt += '  [COLOR gold]coderduck[/COLOR][CR]'
        txt += '  [COLOR gold]echolink[/COLOR][CR]'
        txt += '  [COLOR red][B]free-proxy-list.anon[COLOR lime]  recomendado[/B][/COLOR][CR]'
        txt += '  [COLOR gold]free-proxy-list.com[/COLOR][CR]'
        txt += '  [COLOR gold]free-proxy-list.uk[/COLOR][CR]'
        txt += '  [COLOR gold]free-proxy-list.uk[/COLOR][CR]'
        txt += '  [COLOR gold]github[/COLOR][CR]'
        txt += '  [COLOR gold]proxy-daily[/COLOR][CR]'
        txt += '  [COLOR gold]proxy-list.org[/COLOR][CR]'
        txt += '  [COLOR gold]proxyhub[/COLOR][CR]'
        txt += '  [COLOR gold]proxyranker[/COLOR][CR]'
        txt += '  [COLOR gold]xroxy[/COLOR][CR]'
        txt += '  [COLOR gold]socks[/COLOR][CR]'
        txt += '  [COLOR gold]squidproxyserver[/COLOR][CR]'

    platformtools.dialog_textviewer('Proveedores de proxies', txt)


def show_help_recommended(item):
    logger.info()

    txt = ''

    txt += '[COLOR goldenrod][B]Proveedores habituales:[/B][/COLOR][CR]'

    txt += '  [COLOR yellow][B]mmpx12[/B][/COLOR][CR]'
    txt += '  [COLOR yellow][B]proxyscrape.com[/B][/COLOR][CR]'
    txt += '  [COLOR yellow][B]us-proxy.org[/B][/COLOR][CR]'

    if config.get_setting('proxies_extended', default=False):
        txt += '[CR][COLOR aqua][B]Lista ampliada de proveedores:[/B][/COLOR][CR]'

        txt += '  [COLOR gold][B]free-proxy-list.anon[/B][/COLOR][CR]'

    platformtools.dialog_textviewer('Proveedores Recomendados de proxies', txt)

def show_help_providers2(item):
    logger.info()

    item.ampliada = True
    show_help_providers(item)


def show_help_fixes(item):
    logger.info()

    txt = '[CR] Son correcciones del Addon:[CR]'

    txt += ' - [COLOR yellow]Por bugs (errores)[/COLOR][CR]'

    txt += ' - [COLOR yellow]Por cambios menores (nuevos dominios, estructuras, etc.)[/COLOR][CR]'

    txt += '[CR] Y que no tienen la embergadura suficiente como para confeccionar y publicar una nueva versión.[CR]'

    txt += '[CR][COLOR gold] Los Fixes siempre se actualizan automáticamente al iniciar sesión en su Media Center.[/COLOR]'

    platformtools.dialog_textviewer('Información ¿ Qué son los fixes ?', txt)


def show_help_recaptcha(item):
    logger.info()

    txt = 'Son avisos de porqué no se puede reproducir ese enlace en cuestion.[CR]'

    txt += '[CR] Para reproducir ese enlace el servidor exige resolver que no eres un [COLOR gold]Boot[/COLOR], para ello'

    txt += '[CR] presenta un proceso para [COLOR yellow]seleccionar imágenes[/COLOR] (bicicletas, barcos, semáforos, etc.)'

    txt += '[CR][CR]Dada su dificultad [COLOR gold]NO[/COLOR] está contemplado en el Addon esta situación.'

    platformtools.dialog_textviewer('Información ¿ Qué significa Requiere verificación [COLOR red]reCAPTCHA[/COLOR] ?', txt)


def show_help_acortador(item):
    logger.info()

    txt = 'Son avisos de porqué no se puede reproducir ese enlace en cuestion.[CR]'

    txt += '[CR] Son redireccionamientos, que hacen que un Link concreto, efectue accesos a otros enlaces diferentes.'

    txt += '[CR] Para reproducir ese enlace el servidor exige resolver y esperar Todos esas [COLOR gold]Redirecciones[/COLOR], para ello'

    txt += '[CR] presenta un proceso para [COLOR yellow]seleccionar diferentes Webs[/COLOR] (publicidad, esperas, etc.)'

    txt += '[CR][CR]Dada su dificultad [COLOR gold]NO[/COLOR] está contemplado en el Addon esta situación.'

    platformtools.dialog_textviewer('Información ¿ Qué significa Tiene [COLOR plum]Acortador[/COLOR] del enlace ?', txt)


def show_version(item):
    logger.info()

    txt = ''

    try:
       with open(os.path.join(config.get_runtime_path(), 'version.txt'), 'r') as f: txt=f.read(); f.close()
    except:
       try: txt = open(os.path.join(config.get_runtime_path(), 'version.txt'), encoding="utf8").read()
       except: pass

    if txt: platformtools.dialog_textviewer('Información versión', txt)


def show_changelog(item):
    logger.info()

    txt = ''

    try:
       with open(os.path.join(config.get_runtime_path(), 'changelog.txt'), 'r') as f: txt=f.read(); f.close()
    except:
       try: txt = open(os.path.join(config.get_runtime_path(), 'changelog.txt'), encoding="utf8").read()
       except: pass

    if txt: platformtools.dialog_textviewer('Historial de versiones', txt)


def show_dev_notes(item):
    logger.info()

    txt = ''

    try:
       with open(os.path.join(config.get_runtime_path(), 'dev-notes.txt'), 'r') as f: txt=f.read(); f.close()
    except:
       try: txt = open(os.path.join(config.get_runtime_path(), 'dev-notes.txt'), encoding="utf8").read()
       except: pass

    if txt: platformtools.dialog_textviewer('Notas para developers', txt)


def show_todo_log(item):
    logger.info()

    path = os.path.join(config.get_data_path(), item.todo)

    existe = filetools.exists(path)

    if not existe:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún No hay el fichero Log[/COLOR][/B]' % color_alert)
        return

    txt = ''

    try:
        with open(path, 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(path, encoding="utf8").read()
        except: pass

    if txt:
        platformtools.dialog_textviewer('Fichero Log ' + item.todo, txt)
    else:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin Información[/COLOR][/B]' % color_alert)


def show_log(item):
    logger.info()

    loglevel = config.get_setting('debug', 0)
    if not loglevel >= 2:
        if not platformtools.dialog_yesno(config.__addon_name, 'El nivel actual de información del fichero LOG de su Media Center NO esta configurado al máximo. ¿ Desea no obstante visualizarlo ?'): 
            return

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
        with open(os.path.join(path, file_log), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(path, file_log), encoding="utf8").read()
        except: pass

    if config.get_setting('developer_mode', default=False):
        txt = txt.replace('Balandro.', '[COLOR yellow][B]Balandro[/B][/COLOR].')
        txt = txt.replace('Balandro ', '[COLOR yellow][B]Balandro[/B][/COLOR] ')
        txt = txt.replace('balandro.', '[COLOR yellow][B]Balandro[/B][/COLOR].')
        txt = txt.replace('balandro ', '[COLOR yellow][B]Balandro[/B][/COLOR] ')

    if txt: platformtools.dialog_textviewer('Fichero LOG de su Media Center', txt)


def copy_log(item):
    logger.info()

    loglevel = config.get_setting('debug', 0)
    if not loglevel >= 2:
        if not platformtools.dialog_yesno(config.__addon_name, 'El nivel actual de información del fichero LOG de su Media Center NO esta configurado al máximo. [B][COLOR %s]¿ Desea no obstante obtener una Copia ?[/B][/COLOR]' % color_infor):
            return

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

    destino_path = xbmcgui.Dialog().browseSingle(3, 'Seleccionar carpeta dónde copiar', 'files', '', False, False, '')
    if not destino_path: return

    origen = os.path.join(path, file_log)
    destino = filetools.join(destino_path, file_log)
    if not filetools.copy(origen, destino, silent=False):
        platformtools.dialog_ok(config.__addon_name, 'Error, no se ha podido copiar el fichero Log!', origen, destino)
        return

    platformtools.dialog_notification('Fichero Log copiado', file_log)

    time.sleep(0.5)

    loglevel = config.get_setting('debug', 0)
    if not loglevel == 0:
        if not platformtools.dialog_yesno(config.__addon_name, 'La configuración actual del nivel de información del fichero LOG de su Media Center REDUCE el rendimiento de su equipo. [B][COLOR %s]¿ Desea mantener ese Nivel de información ?[/B][/COLOR]' % color_avis):
            config.set_setting('debug', '0')


def test_log(item):
    logger.info()

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

    if existe: return file_log

    return '[COLOR red][B]Fichero Log NO localizado[/B][/COLOR]'


def show_advs(item):
    logger.info()

    path = translatePath(os.path.join('special://home/userdata', ''))

    file_advs = 'advancedsettings.xml'

    file = path + file_advs

    existe = filetools.exists(file)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero Advancedsettings[/COLOR][/B]' % color_infor)
        return

    txt = ''

    try:
       with open(os.path.join(path, file_advs), 'r') as f: txt=f.read(); f.close()
    except:
       try: txt = open(os.path.join(path, file_advs), encoding="utf8").read()
       except: pass

    if txt: platformtools.dialog_textviewer('Su fichero Advancedsettings de su Media Center', txt)


def show_yourlist(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'Lista-proxies.txt')

    existe = filetools.exists(path)

    if not existe:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún No hay fichero Lista de Proxies[/COLOR][/B]' % color_alert)
        return

    txt = ''

    try:
        with open(path, 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(path, encoding="utf8").read()
        except: pass

    if txt:
        platformtools.dialog_textviewer('Fichero Lista de Proxies', txt)
    else:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin Información[/COLOR][/B]' % color_alert)


def show_help_adults(item):
    logger.info()

    txt = '*) Las webs podrian, en algún caso, publicar Vídeos con contenido [COLOR gold]No Apto[/COLOR] para menores.'
    txt += ' Balandro cuenta con un apartado en su configuración exclusivo para el [COLOR gold]Control Parental[/COLOR].'
    txt += ' (por defecto este apartado está [COLOR gold]Habilitado[/COLOR]).'

    txt += '[CR][CR]*) Pero no se puede garantizar que todo el material de este tipo se filtre correctamente en determinadas ocasiones.'

    platformtools.dialog_textviewer('Control Parental', txt)


def show_help_domains(item):
    logger.info()

    txt = '*) Determinadas webs Cambian constantemente de Dominio y es necesario modificarlo para permitir su acceso.'

    txt += '[CR][CR]*) Para ello desde otro equipo debeis accecder a la web en cuestión y obtener ese nuevo dominio.'
    txt += '[CR]    Si desconoceís el dominio actual de esa web, mediante un navegador web deberéis localizarlo.'

    txt += '[CR][CR]*) También lo podreis obtener durante un corto espacio de tiempo efectuando el [B][COLOR gold]Test Web del Canal[/COLOR][/B].'
    txt += '[CR]    ver los datos [B][COLOR yellow]Host/Nuevo[/COLOR][/B] en la información del Test.'

    txt += '[CR][CR]    Así mismo, bajo ciertas circunstancias ese [B][COLOR gold]Test Web del Canal[/COLOR][/B].'
    txt += '[CR]    podría obtener automáticamente el [B][COLOR yellow]Nuevo Dominio Permanente ó Temporal[/COLOR][/B] como propuesta.'

    txt += '[CR][CR]*) Imprescindible en caso de ser necesario, tomar buena nota de ese [B][COLOR gold]Nuevo Dominio[/COLOR][/B] para esa web.'

    txt += '[CR][CR]*) Una vez tengáis ese Dominio, podéis informarlo en la configuración [B][COLOR gold]categoría Dominios[/COLOR][/B],'
    txt += '[CR]    ó bien al acceder a ese canal determinado a través de su opción [B][COLOR yellow]Acciones[/COLOR][/B].'

    platformtools.dialog_textviewer('Gestión Dominios', txt)


def show_help_torrents(item):
    logger.info()

    txt = '*) A través de un [COLOR gold]Navegador Web[/COLOR] localize e instale al menos uno de los add-ons de la lista que más se adapte a'
    txt += '  sus necesidades y que sea a su vez compatible con su Media Center.'

    txt += '[CR][CR]*) Add-Ons:[CR]'
    txt += '    - [COLOR yellow][B]plugin.video.elementum[/COLOR]  [COLOR limegreen]Recomendado[/B][/COLOR][CR]'
    txt += '    - [COLOR yellow][B]plugin.video.pulsar[/B][/COLOR][CR]'
    txt += '    - [COLOR yellow][B]plugin.video.quasar[/B][/COLOR][CR]'
    txt += '    - [COLOR yellow][B]plugin.video.stream[/B][/COLOR][CR]'
    txt += '    - [COLOR yellow][B]plugin.video.torrest[/B][/COLOR][CR]'
    txt += '    - [COLOR yellow][B]plugin.video.torrenter[/B][/COLOR][CR]'
    txt += '    - [COLOR yellow][B]plugin.video.torrentin[/B][/COLOR][CR]'
    txt += '    - [COLOR yellow][B]plugin.video.xbmctorrent[/B][/COLOR]'

    txt += '[CR][CR]*) A modo de ejemplo para [COLOR gold]Elementum[/COLOR] puede acceder a su web oficial en [COLOR goldenrod][B]elementum.surge.sh[/B][/COLOR]'

    txt += '[CR][CR]*) Existen múltiples sitios webs en donde puede localizar estos add-ons, entre estos sitios le recomendamos,'
    txt += '   que instale [COLOR cyan][B]Kelebek[/B][/COLOR] desde esta fuente [COLOR gold][B]https://newkelebek.gitgub.io/Newkelebek[B][/COLOR]'

    txt += '[CR][CR]*) También le sugerimos contactar con este [COLOR chartreuse]Grupo de Telegram[/COLOR], para recibir Soporte al respecto.[CR]'
    txt += '   [COLOR cyan][B]t.me/AprendiendoKodi[/B][/COLOR]'

    platformtools.dialog_textviewer('¿ Dónde obtener los add-ons para torrents ?', txt)


def show_help_semillas(item):
    logger.info()

    txt = '*) Los archivos Torrent se proveen de [COLOR gold]Semillas[/COLOR] usuarios que están Online con las partes de ese archivo.'

    txt += '[CR][CR] Por ejemplo, en la pantalla de seguimiento de [COLOR gold]Elememtum[/COLOR], comprobar el dato [COLOR gold][B]S:[/B][/COLOR]'
    txt += '  si ese dato contiene [COLOR yellow][B]0[/B][/COLOR], significará que no hay [COLOR gold]Semillas[/COLOR].'

    txt += '[CR][CR]  Si NO apareciera la pantalla de seguimiento de [COLOR gold]Elememtum[/COLOR] [COLOR red][B]No hay ningún usuario Online[/B][/COLOR]'

    txt += '[CR][CR]*) Por lo tanto, tocará esperar, a que estén Onlime [COLOR gold]Todos los Usuarios[/COLOR] con las partes de ese archivo para efectuar el Play.'

    platformtools.dialog_textviewer('Información archivos Torrent (Semillas)', txt)


def show_help_centers(item):
    logger.info()

    txt = '*) Le sugerimos contactar con este [COLOR chartreuse]Grupo de Telegram[/COLOR], para recibir Soporte al respecto.[CR]'
    txt += '   [COLOR cyan][B]t.me/AprendiendoKodi[/B][/COLOR]'

    platformtools.dialog_textviewer('¿ Dónde obtener soporte para su Media Center ?', txt)


def show_help_vias(item):
    logger.info()

    txt = '*) A través de un [COLOR cyan]Navegador[/COLOR] Web localize e instale al menos uno de los add-ons de la lista que más se adapte a'
    txt += '  sus necesidades y que sea a su vez compatible con su Media Center.'

    txt += '[CR][CR]*) Add-Ons:[CR]'
    txt += '    - [COLOR yellow][B]plugin.video.youtube[/B][/COLOR][CR]'
    txt += '    - [COLOR yellow][B]script.module.resolveurl[/B][/COLOR]'

    txt += '[CR][CR]*) Puede obtenerlos desde [COLOR chartreuse][B]Nuestra Fuente[/B][/COLOR], carpeta [COLOR gold][B]Scripts[/B][/COLOR].[CR]'
    txt += '    [COLOR darkorange][B]https://balandro-tk.github.io/balandro/[/B][/COLOR][CR]'

    txt += '    [COLOR mediumaquamarine][B]https://balandro-tk.github.io/balandro/scripts/[/B][/COLOR][CR]'
    txt += '     - [COLOR lightblue][B]Carpeta Kodi18: Repo ResolveUrl y Plugin Youtube hasta 18.x[/B][/COLOR][CR]'
    txt += '     - [COLOR lightblue][B]Carpeta Kodi19: Repo ResolveUrl y Plugin Youtube desde 19.x[/B][/COLOR]'

    txt += '[CR][CR]*) Ó bien, le sugerimos contactar con este [COLOR chartreuse]Grupo de Telegram[/COLOR], para recibir Soporte al respecto.[CR]'
    txt += '    [COLOR cyan][B]t.me/AprendiendoKodi[/B][/COLOR]'

    platformtools.dialog_textviewer('¿ Dónde obtener los add-ons para Vías Alternativas ?', txt)


def show_help_elementum(item):
    logger.info()

    txt = '*) Si su Media Center es una versión posterior a [COLOR gold][B]18.x[/COLOR][/B] y [COLOR yellow][B]NO[/B][/COLOR] opera bajo el sistema operativo [COLOR gold][B]Windows[/COLOR][/B], en determinadas ocasiones, puede fallar la Reproducción, a través de este Motor Torrent.'

    txt += '[CR][CR]*) Ejemplo: si esta operando bajo [COLOR yellow][B]Android[/B][/COLOR] y su versión de [COLOR gold]Android es superior a 9.x[/COLOR][CR]'
    txt += '    Necesitará un [COLOR darkorange][B]Media Center Especial Modificado para ello.[/B][/COLOR]'

    txt += '[CR][CR]*) Puede obtenerlo desde el [COLOR chartreuse]Grupo de Telegram[/COLOR], para recibir Soporte al respecto.[CR]'
    txt += '    [COLOR cyan][B]t.me/AprendiendoKodi[/B][/COLOR]'

    platformtools.dialog_textviewer('Información Motor Torrent Elementum', txt)


def show_legalidad(item):
    logger.info()

    txt = '[COLOR yellow]*)[B] Balandro [COLOR moccasin][B] es Totalmente [I] GRATUITO [/I], si Pagó por este Add-On le [I] ENGAÑARON, [/I][/B][/COLOR]'
    txt += '[COLOR lightblue][B] y tiene como objeto, permitir visualizar Películas, Series, Documentales, etc... [/B][/COLOR]'
    txt += '[COLOR lightblue][B] Todo a través de Internet y directamente desde su Sistema Media Center.[/B][/COLOR]'

    txt += '[CR][CR][COLOR orchid][B] Este Add-On es tan solo un mero Ejercicio de Aprendizaje del Lenguaje de Programación Python y se distribuye sin Ningún Contenido Multimedia adjunto al mismo.[/B][/COLOR]'
    txt += '[COLOR lightgrey][B][I] En consecuencia solo Las Webs son plenamente Responsables de los Contenidos que Publiquen [/I][/B][/COLOR]'

    txt += '[CR][CR][COLOR tan][B] Úselo de acuerdo con su Criterio y bajo su Responsabilidad,[/B][/COLOR]'
    txt += '[COLOR tan][B] sus Creadores quedarán Totalmente Eximidos de toda Repercusión Legal, si se Re-Distribuye solo ó con acceso a Contenidos Protegidos por los Derechos de Autor, sin el Permiso Explícito de estos mismos.[/B][/COLOR]'

    txt += '[CR][CR]*)[COLOR chocolate][B][I] Si este tipo de contenido está Prohibido en su País, solamente Usted será el Responsable de su uso.[/I][/B][/COLOR]'

    txt += '[CR][CR]*)[COLOR mediumaquamarine][B] Este Add-On es un proyecto sin ánimo de Lucro y con Fines Educativos, por lo tanto está Prohibida su Venta en solitario ó como parte de Software Integrado en cualquier dispositivo, es exclusivamente para un uso Docente y Personal.[/B][/COLOR]'

    txt += '[CR][CR]*)[COLOR chartreuse][B] Vesiones de este Add-On desde el año 2018.[/B][/COLOR]'

    txt += '[CR][CR]*)[COLOR red][B][I] Queda totalmente Prohibida su Re-Distribución, sin la Autorización Fehaciente de sus Creadores.[/I][/B][/COLOR]'

    platformtools.dialog_textviewer('Cuestiones Legales', txt)


def show_license(item):
    logger.info()

    txt = ''
    try:
       with open(os.path.join(config.get_runtime_path(), 'LICENSE'), 'r') as f: txt=f.read(); f.close()
    except:
       try: txt = open(os.path.join(config.get_runtime_path(), 'LICENSE'), encoding="utf8").read()
       except: pass

    if txt: platformtools.dialog_textviewer('Licencia (Gnu Gpl v3)', txt)


def show_test(item):
    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Cargando información sistema[/B][/COLOR]' % color_infor)

    your_ip = ''

    try:
       data = httptools.downloadpage('http://httpbin.org/ip').data
       data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
       your_ip = scrapertools.find_single_match(str(data), '.*?"origin".*?"(.*?)"')
    except:
       pass

    if not your_ip:
        try: your_ip = httptools.downloadpage('http://ipinfo.io/ip').data
        except: pass

    if not your_ip:
        try: your_ip = httptools.downloadpage('http://www.icanhazip.com/').data
        except: pass

    if not your_ip:
	    platformtools.dialog_ok(config.__addon_name, '[COLOR red]Parece que NO hay conexión con internet.[/COLOR]', 'Compruebelo realizando cualquier Búsqueda, desde un Navegador Web ')

    hay_repo = False
    if xbmc.getCondVisibility('System.HasAddon("%s")' % 'repository.balandro'): hay_repo = True

    access_repo = False
    tex_access_repo = ''
    if hay_repo:
        try:
           data = httptools.downloadpage(ADDON_REPO_ADDONS).data
           if data: access_repo = True
        except: tex_access_repo = '[COLOR lightblue][B]No se pudo comprobar[/B][/COLOR]'

    ult_ver = ''

    access_last_ver = False

    if hay_repo:
        if access_repo:
            try: ult_ver = updater.check_addon_version()
            except: pass

            if ult_ver: access_last_ver = True

    access_fixes = False
    tex_access_fixes = ''
    if hay_repo:
        if access_repo:
            try:
               data = httptools.downloadpage(ADDON_UPDATES_JSON).data
               if data:
                   access_fixes = True
                   if 'addon_version' not in data or 'fix_version' not in data: access_fixes = None
            except: tex_access_fixes = '[COLOR lightblue][B]No se pudo comprobar[/B][/COLOR]'

    txt = '[CR][COLOR fuchsia]BALANDRO[/COLOR][CR]'

    if not your_ip: your_ip = '[COLOR red][B] Sin Conexión [/B][/COLOR]'

    txt += ' - [COLOR gold]Conexión internet:[/COLOR]  %s [CR][CR]' % your_ip

    tex_repo = ' Instalado'
    if hay_repo == False: tex_repo = '[I][B][COLOR %s] No instalado, No recibirá más versiones [/COLOR][/B][/I]' % color_adver

    txt += ' - [COLOR gold]Repositorio:[/COLOR]  %s [CR][CR]' % tex_repo
    tex_access_repo = ' Accesible'
    if access_repo == False:
        if tex_access_repo == '': tex_access_repo = '[COLOR red][B] Sin conexión, No accesible [/B][/COLOR]'

    txt += ' - [COLOR gold]Conexión con repositorio:[/COLOR]  %s [CR][CR]' % tex_access_repo

    if access_last_ver: tex_access_last_ver = ' Versión correcta '
    else:
        if not ult_ver:
            if not access_repo: tex_access_last_ver = '[I][B][COLOR %s] No accesible [/COLOR][/B][/I]' % color_adver
            else: tex_access_last_ver = '[I][B][COLOR %s] Accesible desde Repositorio [/COLOR][/B][/I]' % color_adver
        else: tex_access_last_ver = '[I][B][COLOR %s] (desfasada)[/COLOR][/B][/I]' % color_adver

    txt += ' - [COLOR gold]Última versión:[/COLOR]  %s [CR][CR]' % tex_access_last_ver

    if not tex_access_fixes:
        tex_access_fixes = ' Accesibles'
        if access_fixes == None: tex_access_fixes = '[COLOR yellow] Sin actualizaciones tipo Fix pendientes [/COLOR]'
        elif access_fixes == False: tex_access_fixes = '[I][B][COLOR %s] Fixes sobre última versión, No accesibles [/COLOR][/B][/I]' % color_adver

    txt += ' - [COLOR gold]Fixes sobre última versión:[/COLOR]  %s [CR][CR]' % tex_access_fixes

    txt += ' - [COLOR gold]Versión instalada:[/COLOR]  [COLOR yellow][B]%s[/B][/COLOR]' % config.get_addon_version()
    if not ult_ver:
        if not access_repo: txt = txt + '[I][COLOR %s] (Sin repositorio)[/COLOR][/I]' % color_adver
        else: txt = txt + '[I][COLOR %s] (desfasada)[/COLOR][/I]' % color_adver

    txt += '[CR][CR]'

    folder_down = config.get_setting('downloadpath', default='')
    if not folder_down == '':
        txt += ' - [COLOR gold]Carpeta descargas:[/COLOR]  [COLOR moccasin]%s[/COLOR][CR][CR]' % folder_down

    tex_dom = ''

    datos = channeltools.get_channel_parameters('animefenix')
    if datos['active']:
        animefenix_dominio = config.get_setting('channel_animefenix_dominio', default='')
        if animefenix_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + animefenix_dominio
           else: tex_dom = animefenix_dominio

    datos = channeltools.get_channel_parameters('animeflv')
    if datos['active']:
        animeflv_dominio = config.get_setting('channel_animeflv_dominio', default='')
        if animeflv_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + animeflv_dominio
           else: tex_dom = animeflv_dominio

    datos = channeltools.get_channel_parameters('animeonline')
    if datos['active']:
        animeonline_dominio = config.get_setting('channel_animeonline_dominio', default='')
        if animeonline_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + animeonline_dominio
           else: tex_dom = animeonline_dominio

    datos = channeltools.get_channel_parameters('cinecalidad')
    if datos['active']:
        cinecalidad_dominio = config.get_setting('channel_cinecalidad_dominio', default='')
        if cinecalidad_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + cinecalidad_dominio
           else: tex_dom = cinecalidad_dominio

    datos = channeltools.get_channel_parameters('cinecalidadla')
    if datos['active']:
        cinecalidadla_dominio = config.get_setting('channel_cinecalidadla_dominio', default='')
        if cinecalidadla_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + cinecalidadla_dominio
           else: tex_dom = cinecalidadla_dominio

    datos = channeltools.get_channel_parameters('cinecalidadlol')
    if datos['active']:
        cinecalidadlol_dominio = config.get_setting('channel_cinecalidadlol_dominio', default='')
        if cinecalidadlol_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + cinecalidadlol_dominio
           else: tex_dom = cinecalidadlol_dominio

    datos = channeltools.get_channel_parameters('cinecalidadmx')
    if datos['active']:
        cinecalidadmx_dominio = config.get_setting('channel_cinecalidadmx_dominio', default='')
        if cinecalidadmx_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + cinecalidadmx_dominio
           else: tex_dom = cinecalidadmx_dominio

    datos = channeltools.get_channel_parameters('cliversite')
    if datos['active']:
        cliversite_dominio = config.get_setting('channel_cliversite_dominio', default='')
        if cliversite_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + cliversite_dominio
           else: tex_dom = cliversite_dominio

    datos = channeltools.get_channel_parameters('cuevana3video')
    if datos['active']:
        cuevana3video_dominio = config.get_setting('channel_cuevana3video_dominio', default='')
        if cuevana3video_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + cuevana3video_dominio
           else: tex_dom = cuevana3video_dominio

    datos = channeltools.get_channel_parameters('divxtotal')
    if datos['active']:
        divxtotal_dominio = config.get_setting('channel_divxtotal_dominio', default='')
        if divxtotal_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + divxtotal_dominio
           else: tex_dom = divxtotal_dominio

    datos = channeltools.get_channel_parameters('dontorrents')
    if datos['active']:
        dontorrents_dominio = config.get_setting('channel_dontorrents_dominio', default='')
        if dontorrents_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + dontorrents_dominio
           else: tex_dom = dontorrents_dominio

    datos = channeltools.get_channel_parameters('elifilms')
    if datos['active']:
        elifilms_dominio = config.get_setting('channel_elifilms_dominio', default='')
        if elifilms_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + elifilms_dominio
           else: tex_dom = elifilms_dominio

    datos = channeltools.get_channel_parameters('elitetorrent')
    if datos['active']:
        elitetorrent_dominio = config.get_setting('channel_elitetorrent_dominio', default='')
        if elitetorrent_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + elitetorrent_dominio
           else: tex_dom = elitetorrent_dominio

    datos = channeltools.get_channel_parameters('ennovelas')
    if datos['active']:
        ennovelas_dominio = config.get_setting('channel_ennovelas_dominio', default='')
        if ennovelas_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + ennovelas_dominio
           else: tex_dom = ennovelas_dominio

    datos = channeltools.get_channel_parameters('entrepeliculasyseries')
    if datos['active']:
        entrepeliculasyseries_dominio = config.get_setting('channel_entrepeliculasyseries_dominio', default='')
        if entrepeliculasyseries_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + entrepeliculasyseries_dominio
           else: tex_dom = entrepeliculasyseries_dominio

    datos = channeltools.get_channel_parameters('estrenosdoramas')
    if datos['active']:
        estrenosdoramas_dominio = config.get_setting('channel_estrenosdoramas_dominio', default='')
        if estrenosdoramas_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + estrenosdoramas_dominio
           else: tex_dom = estrenosdoramas_dominio

    datos = channeltools.get_channel_parameters('gnula24')
    if datos['active']:
        gnula24_dominio = config.get_setting('channel_gnula24_dominio', default='')
        if gnula24_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + gnula24_dominio
           else: tex_dom = gnula24_dominio

    datos = channeltools.get_channel_parameters('grantorrent')
    if datos['active']:
        grantorrent_dominio = config.get_setting('channel_grantorrent_dominio', default='')
        if grantorrent_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + grantorrent_dominio
           else: tex_dom = grantorrent_dominio

    datos = channeltools.get_channel_parameters('grantorrents')
    if datos['active']:
        grantorrents_dominio = config.get_setting('channel_grantorrents_dominio', default='')
        if grantorrents_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + grantorrents_dominio
           else: tex_dom = grantorrents_dominio

    datos = channeltools.get_channel_parameters('hdfull')
    if datos['active']:
        hdfull_dominio = config.get_setting('channel_hdfull_dominio', default='')
        if hdfull_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + hdfull_dominio
           else: tex_dom = hdfull_dominio

    datos = channeltools.get_channel_parameters('hdfullse')
    if datos['active']:
        hdfullse_dominio = config.get_setting('channel_hdfullse_dominio', default='')
        if hdfullse_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + hdfullse_dominio
           else: tex_dom = hdfullse_dominio

    datos = channeltools.get_channel_parameters('henaojara')
    if datos['active']:
        henaojara_dominio = config.get_setting('channel_henaojara_dominio', default='')
        if henaojara_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + henaojara_dominio
           else: tex_dom = henaojara_dominio

    datos = channeltools.get_channel_parameters('mejortorrentapp')
    if datos['active']:
        mejortorrentapp_dominio = config.get_setting('channel_mejortorrentapp_dominio', default='')
        if mejortorrentapp_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + mejortorrentapp_dominio
           else: tex_dom = mejortorrentapp_dominio

    datos = channeltools.get_channel_parameters('pelishouse')
    if datos['active']:
        pelishouse_dominio = config.get_setting('channel_pelishouse_dominio', default='')
        if pelishouse_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + pelishouse_dominio
           else: tex_dom = pelishouse_dominio

    datos = channeltools.get_channel_parameters('pelismaraton')
    if datos['active']:
        pelismaraton_dominio = config.get_setting('channel_pelismaraton_dominio', default='')
        if pelismaraton_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + pelismaraton_dominio
           else: tex_dom = pelismaraton_dominio

    datos = channeltools.get_channel_parameters('pelispedia')
    if datos['active']:
        pelispedia_dominio = config.get_setting('channel_pelispedia_dominio', default='')
        if pelispedia_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + pelispedia_dominio
           else: tex_dom = pelispedia_dominio

    datos = channeltools.get_channel_parameters('pelispediaws')
    if datos['active']:
        pelispediaws_dominio = config.get_setting('channel_pelispediaws_dominio', default='')
        if pelispediaws_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + pelispediaws_dominio
           else: tex_dom = pelispediaws_dominio

    datos = channeltools.get_channel_parameters('pelisplus')
    if datos['active']:
        pelisplus_dominio = config.get_setting('channel_pelisplus_dominio', default='')
        if pelisplus_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + pelisplus_dominio
           else: tex_dom = pelisplus_dominio

    datos = channeltools.get_channel_parameters('pelisplushd')
    if datos['active']:
        pelisplushd_dominio = config.get_setting('channel_pelisplushd_dominio', default='')
        if pelisplushd_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + pelisplushd_dominio
           else: tex_dom = pelisplushd_dominio

    datos = channeltools.get_channel_parameters('pelisplushdlat')
    if datos['active']:
        pelisplushdlat_dominio = config.get_setting('channel_pelisplushdlat_dominio', default='')
        if pelisplushdlat_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + pelisplushdlat_dominio
           else: tex_dom = pelisplushdlat_dominio

    datos = channeltools.get_channel_parameters('pelisplushdnz')
    if datos['active']:
        pelisplushdnz_dominio = config.get_setting('channel_pelisplushdnz_dominio', default='')
        if pelisplushdnz_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + pelisplushdnz_dominio
           else: tex_dom = pelisplushdnz_dominio

    datos = channeltools.get_channel_parameters('pelispluslat')
    if datos['active']:
        pelispluslat_dominio = config.get_setting('channel_pelispluslat_dominio', default='')
        if pelispluslat_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + pelispluslat_dominio
           else: tex_dom = pelispluslat_dominio

    datos = channeltools.get_channel_parameters('playdede')
    if datos['active']:
        playdede_dominio = config.get_setting('channel_playdede_dominio', default='')
        if playdede_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + playdede_dominio
           else: tex_dom = playdede_dominio

    datos = channeltools.get_channel_parameters('poseidonhd2')
    if datos['active']:
        poseidonhd2_dominio = config.get_setting('channel_poseidonhd2_dominio', default='')
        if poseidonhd2_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + poseidonhd2_dominio
           else: tex_dom = poseidonhd2_dominio

    datos = channeltools.get_channel_parameters('series24')
    if datos['active']:
        series24_dominio = config.get_setting('channel_series24_dominio', default='')
        if series24_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + series24_dominio
           else: tex_dom = series24_dominio

    datos = channeltools.get_channel_parameters('seriesantiguas')
    if datos['active']:
        seriesantiguas_dominio = config.get_setting('channel_seriesantiguas_dominio', default='')
        if seriesantiguas_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + seriesantiguas_dominio
           else: tex_dom = seriesantiguas_dominio

    datos = channeltools.get_channel_parameters('serieskao')
    if datos['active']:
        serieskao_dominio = config.get_setting('channel_serieskao_dominio', default='')
        if serieskao_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + serieskao_dominio
           else: tex_dom = serieskao_dominio

    datos = channeltools.get_channel_parameters('seriesyonkis')
    if datos['active']:
        seriesyonkis_dominio = config.get_setting('channel_seriesyonkis_dominio', default='')
        if seriesyonkis_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + seriesyonkis_dominio
           else: tex_dom = seriesyonkis_dominio

    datos = channeltools.get_channel_parameters('srnovelas')
    if datos['active']:
        srnovelas_dominio = config.get_setting('channel_srnovelas_dominio', default='')
        if srnovelas_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + srnovelas_dominio
           else: tex_dom = srnovelas_dominio

    datos = channeltools.get_channel_parameters('subtorrents')
    if datos['active']:
        subtorrents_dominio = config.get_setting('channel_subtorrents_dominio', default='')
        if subtorrents_dominio:
           if tex_dom: tex_dom = tex_dom + '  '  + subtorrents_dominio
           else: tex_dom = subtorrents_dominio

    datos = channeltools.get_channel_parameters('torrentpelis')
    if datos['active']:
        torrentpelis_dominio = config.get_setting('channel_torrentpelis_dominio', default='')
        if torrentpelis_dominio:
           if tex_dom: tex_dom = tex_dom + '  ' + torrentpelis_dominio
           else: tex_dom = torrentpelis_dominio

    if tex_dom:
        txt += ' - [COLOR gold]Dominios:[/COLOR]  [COLOR springgreen]%s[/COLOR][CR][CR]' % str(tex_dom).replace('https://', '').replace('/', '')


    filtros = {'clusters': 'register'}
    opciones = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if ch_list:
        txt_ch = ''

        for ch in ch_list:
            username = config.get_setting(ch['id'] + '_username', ch['id'], default='')

            if not txt_ch: txt_ch = '[CR]'

            if not username: txt_ch  += '   ' + ch['name'] + ' [COLOR green][B]falta registrarse[/B][/COLOR][CR]'
            else: txt_ch  += '   ' + ch['name'] +  '[COLOR green][B] informadas[/B][/COLOR][CR]'

        if not txt_ch: txt_ch = 'No hay canales que requieran registrarse' 
        txt += ' - [COLOR gold]Credenciales:[/COLOR]  %s' % str(txt_ch)
        txt += '[CR]'

    filtros = {'searchable': True}
    opciones = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if ch_list:
       txt_ch = ''

       for ch in ch_list:
           cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

           if not config.get_setting(cfg_proxies_channel, default=''): continue

           txt_ch += '[COLOR red]%s[/COLOR]  ' % ch['name']

       if not txt_ch: txt_ch = 'No hay canales con proxies' 
       txt += ' - [COLOR gold]Proxies:[/COLOR]  %s' % str(txt_ch)

    if config.get_setting('search_included_all', default=''):
        txt += '[CR][CR] - [COLOR greenyellow][B]Solo Buscar: en Determinados canales[/B][/COLOR] Incluidos en las búsquedas de [B][COLOR green]Todos[/COLOR][/B]'
        txt += ' ' + config.get_setting('search_included_all') + '[CR]'

    txt_exc = ''

    if config.get_setting('search_excludes_movies', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR deepskyblue][B]Películas[/B][/COLOR] ' + config.get_setting('search_excludes_movies') + '[CR]'
    if config.get_setting('search_excludes_tvshows', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR hotpink][B]Series[/B][/COLOR] ' + config.get_setting('search_excludes_tvshows') + '[CR]'
    if config.get_setting('search_excludes_documentaries', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR cyan][B]Documentales[/B][/COLOR] ' + config.get_setting('search_excludes_documentaries') + '[CR]'
    if config.get_setting('search_excludes_torrents', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR blue][B]Torrents[/B][/COLOR] ' + config.get_setting('search_excludes_torrents') + '[CR]'
    if config.get_setting('search_excludes_mixed', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR yellow][B]Películas y/ó Series[/B][/COLOR] ' + config.get_setting('search_excludes_mixed') + '[CR]'
    if config.get_setting('search_excludes_all', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR green][B]Todos[/B][/COLOR] ' + config.get_setting('search_excludes_all') + '[CR]'

    if txt_exc: txt += '[CR][CR]' + txt_exc

    filtros = {'searchable': True}
    opciones = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if ch_list:
       txt_ch = ''

       for ch in ch_list:
           cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'

           if not config.get_setting(cfg_searchable_channel, default=False): continue

           txt_ch += '[COLOR violet]%s[/COLOR]  ' % ch['name']

       if txt_ch: txt += '[CR][CR] - [COLOR gold]Excluidos en Búsquedas:[/COLOR]  %s' % str(txt_ch)

    cliente_torrent = config.get_setting('cliente_torrent', default='Ninguno')
    if cliente_torrent == 'Ninguno': tex_tor = '[COLOR moccasin]Ninguno[/COLOR]'
    elif cliente_torrent == 'Seleccionar':  tex_tor = 'Seleccionar'
    else:
      tex_tor = ' ' + cliente_torrent
      cliente_torrent = 'plugin.video.' + cliente_torrent.lower()
      if xbmc.getCondVisibility('System.HasAddon("%s")' % cliente_torrent):
          cod_version = xbmcaddon.Addon(cliente_torrent).getAddonInfo("version").strip()
          tex_tor += '  ' + cod_version
      else: tex_tor += '  [COLOR red][B]No instalado[/B][/COLOR]'

    if not txt_exc: txt += '[CR]'

    txt += '[CR] - [COLOR gold]Cliente/Motor torrent:[/COLOR]  %s' % tex_tor

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
        cod_version = xbmcaddon.Addon("plugin.video.youtube").getAddonInfo("version").strip()
        tex_yt = '  ' + cod_version
    else: tex_yt = '  [COLOR red][B]No instalado[/B][/COLOR]'

    txt += '[CR][CR] - [COLOR gold]YouTube Add-on:[/COLOR]  %s' % tex_yt

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        cod_version = xbmcaddon.Addon("script.module.resolveurl").getAddonInfo("version").strip()
        tex_yt = '  ' + cod_version
    else: tex_yt = '  [COLOR red][B]No instalado[/B][/COLOR]'

    txt += '[CR][CR] - [COLOR gold]ResolveUrl Script:[/COLOR]  %s' % tex_yt

    loglevel = config.get_setting('debug', 0)
    if loglevel == 0: tex_niv = 'Solo Errores'
    elif loglevel == 1: tex_niv = 'Errores e Información'
    else: tex_niv = 'Máxima Información'

    txt += '[CR][CR] - [COLOR gold]Log:[/COLOR]  %s' % tex_niv

    tex_log = test_log(item)

    txt += '  ' + tex_log

    plataforma = get_plataforma('')

    txt += plataforma

    if not ult_ver:
        if not access_repo:
            platformtools.dialog_ok(config.__addon_name, 'Versión instalada sin repositorio[COLOR coral][B] ' + config.get_addon_version() + '[/B][/COLOR]', '[COLOR yellow][B] Instale la última Versión del Repositorio [/COLOR][/B]')
        else:
            platformtools.dialog_ok(config.__addon_name, 'Versión instalada desfasada[COLOR coral][B] ' + config.get_addon_version() + '[/B][/COLOR]', '[COLOR yellow][B] Instale la última Versión disponible del Add-On[/COLOR][/B]')

    platformtools.dialog_textviewer('Test status sistema', txt)


def show_plataforma(item):
    logger.info()

    plataforma = get_plataforma('')

    txt = plataforma

    platformtools.dialog_textviewer('Información sobre su Plataforma', txt)


def get_plataforma(txt):
    logger.info()

    txt += '[CR][CR][COLOR fuchsia]PLATAFORMA[/COLOR][CR]'

    txt += ' - [COLOR gold]Media center:[/COLOR]  [COLOR coral]%s[/COLOR][CR][CR]' % str(xbmc.getInfoLabel('System.BuildVersion'))

    if '14.' in txt: ver = '14 - Helix  NO soportado'
    elif '15.' in txt: ver = '15 - Isengard  NO soportado'
    elif '16.' in txt: ver = '16 - Jarvis  NO soportado'
    elif '17.' in txt: ver = '17 - Krypton'
    elif '18.' in txt: ver = '18 - Leia'
    elif '19.' in txt: ver = '19 - Matrix'
    elif '20.' in txt: ver = '20 - Nexus'
    elif '21.' in txt: ver = '21 - Omega'
    else: ver = 'Desconocido'

    txt += ' - [COLOR gold]Versión:[/COLOR]  ' + ver + '[CR][CR]'

    try:
       if xbmc.getCondVisibility("System.Platform.Android"): plat = 'Android'
       elif xbmc.getCondVisibility("System.Platform.Windows"): plat = 'Windows'
       elif xbmc.getCondVisibility("System.Platform.UWP"): plat = 'Windows'
       elif xbmc.getCondVisibility("System.Platform.Linux"): plat = 'Linux'
       elif xbmc.getCondVisibility("system.platform.Linux.RaspberryPi"): plat = 'Raspberry'
       elif xbmc.getCondVisibility("System.Platform.OSX"): plat = 'Osx'
       elif xbmc.getCondVisibility("System.Platform.IOS"): plat = 'Ios'
       elif xbmc.getCondVisibility("System.Platform.Darwin"): plat = 'Darwin'
       elif xbmc.getCondVisibility("System.Platform.Xbox"): plat = 'Xbox'
       elif xbmc.getCondVisibility("System.Platform.Tvos"): plat = 'Tvos'
       elif xbmc.getCondVisibility("System.Platform.Atv2"): plat = 'Atv2'
       else: plat = 'Desconocida'
    except:
        plat = '?'

    txt += ' - [COLOR gold]Plataforma:[/COLOR]  ' + plat + '[CR][CR]'

    txt += ' - [COLOR gold]Release:[/COLOR]  ' + str(platform.release()) + '[CR][CR]'

    txt += ' - [COLOR gold]Procesador:[/COLOR]  ' + str(platform.machine()) + '[CR][CR]'

    txt += ' - [COLOR gold]Language:[/COLOR]  ' + str(xbmc.getInfoLabel('System.Language')) + '[CR][CR]'

    txt += ' - [COLOR gold]Uso CPU:[/COLOR]  ' + str(xbmc.getInfoLabel('System.CpuUsage')) + '[CR][CR]'

    plataforma = platform.uname()

    txt += ' - [COLOR gold]Sistema:[/COLOR]  %s-%s-%s[CR][CR]' % (str(plataforma[0]), str(plataforma[2]), str(plataforma[3]))

    txt += ' - [COLOR gold]Python:[/COLOR]  %s.%s.%s[CR][CR]' % (str(sys.version_info[0]), str(sys.version_info[1]), str(sys.version_info[2]))

    return txt


def show_last_fix(item):
    logger.info()

    path = os.path.join(config.get_runtime_path(), 'last_fix.json')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero Fix[/COLOR][/B]' % color_infor)
        return

    txt = ''

    try:
       with open(path, 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(path, encoding="utf8").read()
        except: pass

    if txt:
       txt = txt.replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace(',', '').replace('"', '').replace("'", '').strip()

       txt = txt.replace('addon_version:', '[COLOR cyan][B]Version:[/B][/COLOR]')
       txt = txt.replace('files:', '[COLOR yellowgreen][B]Ficheros:[/B][/COLOR]')

       txt = txt.replace('channels:', '[COLOR yellow][B]Canales:[/B][/COLOR]')
       txt = txt.replace('core:', '[COLOR yellow][B]Core:[/B][/COLOR]')
       txt = txt.replace('lib:', '[COLOR yellow][B]Lib:[/B][/COLOR]')
       txt = txt.replace('modules:', '[COLOR yellow][B]Modules:[/B][/COLOR]')
       txt = txt.replace('platformcode:', '[COLOR yellow][B]Platformcode:[/B][/COLOR]')
       txt = txt.replace('resources:', '[COLOR yellow][B]Resources:[/B][/COLOR]')
       txt = txt.replace('root dir:', '[COLOR yellow][B]Root:[/B][/COLOR]')
       txt = txt.replace('servers:', '[COLOR yellow][B]Servidores:[/B][/COLOR]')

       txt = txt.replace('fix_version:', '[COLOR cyan][B]Numero de Fix:[/B][/COLOR]')
       txt = txt.replace('hash:', '[COLOR slateblue][B]Control Hash:[/B][/COLOR]')

       platformtools.dialog_textviewer('Información del último Fix instalado', txt)


def show_sets(item):
    logger.info()

    file_sets = os.path.join(config.get_data_path(), "settings.xml")

    existe = filetools.exists(file_sets)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No existe settings.xml[/COLOR][/B]' % color_alert)
        return

    txt = ''
    try:
       with open(os.path.join(file_sets), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(file_sets), encoding="utf8").read()
        except: pass

    if txt: platformtools.dialog_textviewer('Su fichero de Ajustes personalizados', txt)


def show_cook(item):
    logger.info()

    file_cook = os.path.join(config.get_data_path(), "cookies.dat")

    existe = filetools.exists(file_cook)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No existe cookies.dat[/COLOR][/B]' % color_adver)
        return

    txt = ''

    try:
       with open(os.path.join(file_cook), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(file_cook), encoding="utf8").read()
        except: pass

    if txt: platformtools.dialog_textviewer('Su fichero de Cookies', txt)
