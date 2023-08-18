# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3: PY3 = True
else: PY3 = False


import os

from datetime import datetime

from platformcode import config, logger, platformtools, updater
from core.item import Item

from core import channeltools


color_list_prefe = config.get_setting('channels_list_prefe_color', default='gold')
color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')
color_list_inactive = config.get_setting('channels_list_inactive_color', default='gray')

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')

current_year = int(datetime.today().year)
current_month = int(datetime.today().month)


context_desarrollo = []

tit = '[COLOR tan][B]Parámetros Menús[/B][/COLOR]'
context_desarrollo.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR %s]Ajustes categoría Team[/COLOR]' % color_exec
context_desarrollo.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_menu = []

tit = '[COLOR tan][B]Parámetros Menús[/B][/COLOR]'
context_menu.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR fuchsia][B]Parámetros Play[/B][/COLOR]'
context_menu.append({'title': tit, 'channel': 'helper', 'action': 'show_play_parameters'})

tit = '[COLOR %s]Ajustes categorías Menú y Play[/COLOR]' % color_exec
context_menu.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_buscar = []

tit = '[COLOR powderblue][B]Parámetros Buscar[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'search', 'action': 'show_help_parameters'})

tit = '[COLOR tan][B]Parámetros Menús[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR fuchsia][B]Parámetros Play[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_play_parameters'})

tit = '[COLOR red][B]Parámetros Proxies[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_prx_parameters'})

tit = '[COLOR %s]Información Dominios[/COLOR]' % color_infor
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios dominios[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR %s][B]Quitar Dominios memorizados[/B][/COLOR]' % color_alert
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'manto_domains'})

tit = '[COLOR greenyellow][B]Buscar Solo en los canales[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_included'})

if config.get_setting('search_included_all', default=''):
    tit = '[COLOR greenyellow][B]Quitar canales de Buscar Solo[/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_included_del'})

tit = '[COLOR violet][B]Excluir canales[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded'})

if config.get_setting('search_excludes_all', default=''):
    tit = '[COLOR violet][B]Quitar canales excluidos[/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})

tit = '[COLOR powderblue][B]Global configurar proxies[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_buscar.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información proxies[/COLOR]' % color_infor
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s][B]Quitar proxies actuales[/B][/COLOR]' % color_list_proxies
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR %s][B]Información búsquedas[/B][/COLOR]' % color_infor
context_buscar.append({'title': tit, 'channel': 'search', 'action': 'show_help'})

tit = '[COLOR %s]Ajustes categorías Dominios, Proxies y Buscar[/COLOR]' % color_exec
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_generos = []

tit = '[COLOR tan][B]Parámetros Menús[/B][/COLOR]'
context_generos.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR powderblue][B]Global configurar proxies[/B][/COLOR]'
context_generos.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_generos.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información proxies[/COLOR]' % color_infor
context_generos.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s][B]Quitar proxies actuales[/B][/COLOR]' % color_list_proxies
context_generos.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR %s]Ajustes categorías Menú y Canales[/COLOR]' % color_exec
context_generos.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_proxy_channels = []

tit = '[COLOR tan][B]Parámetros Menús[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s]Ajustes categoría Menú y Proxies[/COLOR]' % color_exec
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_cfg_search = []

tit = '[COLOR tan][B]Parámetros Menús[/B][/COLOR]'
context_cfg_search.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR %s]Ajustes categoría Menú[/COLOR]' % color_exec
context_cfg_search.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_torrents = []

if config.get_setting('cliente_torrent') == 'Seleccionar' or config.get_setting('cliente_torrent') == 'Ninguno':
    tit = '[COLOR %s][B]Información Motores torrents[/B][/COLOR]' % color_infor
    context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_help_torrents'})

tit = '[COLOR %s][B]Motores torrents instalados[/B][/COLOR]' % color_avis
context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_clients_torrent'})

tit = '[COLOR tan][B]Parámetros Canales[/B][/COLOR]'
context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios dominios[/B][/COLOR]'
context_torrents.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR %s]Ajustes categorías Canales, Dominios, Torrents y Buscar[/COLOR]' % color_exec
context_torrents.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_parental = []

if config.get_setting('adults_password'):
    tit = '[COLOR %s][B]Eliminar Pin parental[/B][/COLOR]' % color_adver
    context_parental.append({'title': tit, 'channel': 'actions', 'action': 'adults_password_del'})
else:
    tit = '[COLOR %s][B]Información parental[/B][/COLOR]' % color_infor
    context_parental.append({'title': tit, 'channel': 'helper', 'action': 'show_help_adults'})

tit = '[COLOR tan][B]Parámetros Canales[/B][/COLOR]'
context_parental.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios dominios[/B][/COLOR]'
context_parental.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR %s]Ajustes categorías Canales, Parental, y Dominios[/COLOR]' % color_exec
context_parental.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_desactivados = []

tit = '[COLOR tan][B]Parámetros Menús[/B][/COLOR]'
context_desactivados.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR %s]Ajustes categoría Menú y Canales[/COLOR]' % color_exec
context_desactivados.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_preferidos = []

tit = '[COLOR %s][B]Información preferidos[/B][/COLOR]' % color_infor
context_preferidos.append({'title': tit, 'channel': 'helper', 'action': 'show_help_tracking'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios dominios[/B][/COLOR]'
context_preferidos.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR %s][B]Comprobar Nuevos Episodios[/B][/COLOR]' % color_adver
context_preferidos.append({'title': tit, 'channel': 'actions', 'action': 'comprobar_nuevos_episodios'})

tit = '[COLOR %s][B]Eliminar Todos los preferidos[/B][/COLOR]' % color_alert
context_preferidos.append({'title': tit, 'channel': 'actions', 'action': 'manto_tracking_dbs'})

tit = '[COLOR tan][B]Parámetros Menús[/B][/COLOR]'
context_preferidos.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR %s]Ajustes categoría Preferidos[/COLOR]' % color_exec
context_preferidos.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_descargas = []

tit = '[COLOR %s][B]Ubicación actual descargas[/B][/COLOR]' % color_infor
context_descargas.append({'title': tit, 'channel': 'downloads', 'action': 'show_folder_downloads'})

tit = '[COLOR %s][B]Eliminar Todas las descargas[/B][/COLOR]' % color_alert
context_descargas.append({'title': tit, 'channel': 'actions', 'action': 'manto_folder_downloads'})

tit = '[COLOR tan][B]Parámetros Menús[/B][/COLOR]'
context_descargas.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR %s]Ajustes categoría Descargas[/COLOR]' % color_exec
context_descargas.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


context_config = []

tit = '[COLOR %s][B]Quitar Proxies memorizados[/B][/COLOR]' % color_alert
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR tan][B]Parámetros Canales[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

tit = '[COLOR %s]Información Dominios[/COLOR]' % color_infor
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})

tit = '[COLOR %s][B]Últimos Cambios dominios[/B][/COLOR]' % color_exec
context_config.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR %s][B]Quitar Dominios memorizados[/B][/COLOR]' % color_alert
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_domains'})

tit = '[COLOR %s][B]Sus Ajustes personalizados[/B][/COLOR]' % color_avis
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_sets'})

tit = '[COLOR %s]Cookies actuales[/COLOR]' % color_infor
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_cook'})

tit = '[COLOR %s][B]Eliminar Cookies[/B][/COLOR]' % color_alert
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_cookies'})

tit = '[COLOR %s]Sus Advanced Settings[/COLOR]' % color_adver
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_advs'})

tit = '[COLOR %s][B]Eliminar Advanced Settings[/B][/COLOR]' % color_alert
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_advs'})

tit = '[COLOR darkorange][B]Borrar Carpeta Caché[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_folder_cache'})

tit = '[COLOR olive][B]Limpiezas[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_limpiezas'})

tit = '[COLOR mediumaquamarine][B]Restablecer parámetros Internos[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_params'})

tit = '[COLOR green][B]Informacion plataforma[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_plataforma'})


def mainlist(item):
    logger.info()
    itemlist = []

    item.category = config.__addon_name

    if config.get_setting('developer_mode', default=False):
        itemlist.append(item.clone( channel='submnuteam', action='submnu_team', title = '[B]Desarrollo[/B]', context=context_desarrollo, thumbnail=config.get_thumb('team'), text_color='darkorange' ))

    if config.get_setting('mnu_search_proxy_channels', default=False):
        itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                    only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

    if config.get_setting('sub_mnu_favoritos', default=False):
        itemlist.append(item.clone( channel='favoritos', action='mainlist', title='[B]Favoritos[/B]', context=context_cfg_search, thumbnail=config.get_thumb('star'), text_color='coral' ))

    if current_month == 4:
        itemlist.append(item.clone( channel='filmaffinitylists', action='_oscars', title='[B]Premios Oscar ' + str(current_year) + '[/B]', text_color='greenyellow', thumbnail=config.get_thumb('oscars'), plot = 'Las películas nominadas a los premios Oscars' ))

    elif current_month == 10:
        itemlist.append(item.clone( channel='filmaffinitylists', action='_emmys', title='[B]Premios Emmy ' + str(current_year) + '[/B]', text_color='greenyellow', thumbnail=config.get_thumb('emmys'), plot = 'Las Series nominadas a los premios Emmy' ))

    elif current_month == 11:
         itemlist.append(item.clone( channel='tmdblists', action='descubre', title='[B]Halloween[/B]', text_color='greenyellow',
                                     extra = 27, search_type = 'movie', thumbnail=config.get_thumb('halloween'), plot = 'Películas del género Terror' ))

    elif current_month == 12:
        itemlist.append(item.clone( channel='filmaffinitylists', action='_navidad', title='[B]Navidad[/B]', text_color='greenyellow', thumbnail=config.get_thumb('navidad'), plot = 'Películas y Series del tema Navidad' ))

    itemlist.append(item.clone( channel='submnuctext', action='submnu_news', title='[B]Novedades[/B]', thumbnail=config.get_thumb('novedades'), text_color='darksalmon' ))

    if config.get_setting('sub_mnu_special', default=True):
        itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', context=context_cfg_search, extra='all', thumbnail=config.get_thumb('heart'), text_color='pink' ))

    itemlist.append(Item( channel='search', action='mainlist', title='[B]Buscar[/B]', context=context_buscar, thumbnail=config.get_thumb('search'), text_color='yellow' ))

    context_usual = []

    tit = '[COLOR tan][B]Parámetros Canales[/B][/COLOR]'
    context_usual.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

    tit = '[COLOR mediumaquamarine][B]Últimos Cambios dominios[/B][/COLOR]'
    context_usual.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

    tit = '[COLOR %s]Ajustes categorías Canales, Dominios, y Buscar[/COLOR]' % color_exec
    context_usual.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    if not config.get_setting('mnu_simple', default=False):
        if config.get_setting('mnu_preferidos', default=True):
            if config.get_setting('ord_preferidos', default=False):
                itemlist.append(item.clone( channel='tracking', action='mainlist', title='[B]Preferidos[/B]', context=context_preferidos, thumbnail=config.get_thumb('videolibrary'), text_color='wheat' ))

        if config.get_setting('mnu_desargas', default=True):
            if config.get_setting('ord_descargas', default=False):
                itemlist.append(item.clone( channel='downloads', action='mainlist', title='[B]Descargas[/B]', context=context_descargas, thumbnail=config.get_thumb('downloads'), text_color='seagreen' ))

    itemlist.append(item.clone( action='', title='[B]Menú:[/B]', thumbnail=config.get_thumb('addon'), text_color='tan', context=context_menu ))

    if config.get_setting('mnu_sugeridos', default=True):
        itemlist.append(item.clone( action='channels', extra='suggested', title=' - Sugeridos', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='aquamarine' ))

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action='channels', extra='all', title=' - Canales', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='gold' ))

    if config.get_setting('mnu_idiomas', default=True):
        itemlist.append(item.clone( channel='groups', action='mainlist', mnu_lang='idiomas', title=' - Idiomas', context=context_menu, thumbnail=config.get_thumb('idiomas'), text_color='yellowgreen' ))

    if config.get_setting('mnu_grupos', default=True):
        itemlist.append(item.clone( channel='groups', action='mainlist', extra='groups', title=' - Grupos', context=context_cfg_search, thumbnail=config.get_thumb('bookshelf'), text_color='magenta' ))

    if not config.get_setting('mnu_simple', default=False):
        if config.get_setting('mnu_pelis', default=True):
            itemlist.append(item.clone( action='channels', extra='movies', title=' - Películas', context=context_usual, thumbnail=config.get_thumb('movie'), text_color='deepskyblue' ))

        if config.get_setting('mnu_series', default=True):
            itemlist.append(item.clone( action='channels', extra='tvshows', title=' - Series', context=context_usual, thumbnail=config.get_thumb('tvshow'), text_color='hotpink' ))

        if config.get_setting('channels_link_pyse', default=False):
           itemlist.append(item.clone( action='channels', extra='mixed', title=' - Películas y Series', context=context_usual,
                                       no_docs = True, thumbnail=config.get_thumb('booklet'), text_color='teal' ))

        if config.get_setting('mnu_generos', default=True):
           itemlist.append(item.clone( channel='submnuctext', action='submnu_genres', title= ' - Géneros', context=context_generos, thumbnail=config.get_thumb('genres'), text_color='thistle' ))

        if config.get_setting('mnu_documentales', default=True):
            itemlist.append(item.clone( action='channels', extra='documentaries', title=' - Documentales', context=context_usual, thumbnail=config.get_thumb('documentary'), text_color='cyan' ))

        if config.get_setting('mnu_infantiles', default=True):
            itemlist.append(item.clone( action='channels', extra='infantil', title=' - Infantiles', context=context_usual, thumbnail=config.get_thumb('booklet'), text_color='lightyellow' ))

        if config.get_setting('mnu_novelas', default=True):
            itemlist.append(item.clone( action='channels', extra='tales', title=' - Novelas', context=context_usual, thumbnail=config.get_thumb('booklet'), text_color='limegreen' ))

        if config.get_setting('mnu_torrents', default=True):
            itemlist.append(item.clone( action='channels', extra='torrents', title=' - Torrents', context=context_torrents, thumbnail=config.get_thumb('torrents'), text_color='blue' ))

        if config.get_setting('mnu_doramas', default=True):
            itemlist.append(item.clone( action='channels', extra='dorama', title=' - Doramas', context=context_usual, thumbnail=config.get_thumb('computer'), text_color='firebrick' ))

        if config.get_setting('mnu_animes', default=True):
            if not config.get_setting('descartar_anime', default=True):
                itemlist.append(item.clone( action='channels', extra='anime', title=' - Animes', context=context_parental, thumbnail=config.get_thumb('anime'), text_color='springgreen' ))

        if config.get_setting('mnu_adultos', default=True):
            if not config.get_setting('descartar_xxx', default=True):
                itemlist.append(item.clone( action='channels', extra='adults', title=' - Adultos', context=context_parental, thumbnail=config.get_thumb('adults'), text_color='orange' ))

        if config.get_setting('mnu_proxies', default=False):
            itemlist.append(item.clone( action='channels', extra='proxies', title=' - Proxies', context=context_proxy_channels, thumbnail=config.get_thumb('stack'), text_color='red' ))

        if config.get_setting('mnu_problematicos', default=False):
            itemlist.append(item.clone( action='channels', extra='problematics', title=' - Problemáticos', context=context_desactivados, thumbnail=config.get_thumb('stack'), text_color='darkgoldenrod' ))

        if config.get_setting('mnu_desactivados', default=False):
            itemlist.append(item.clone( action='channels', extra='disableds', title=' - Desactivados', context=context_desactivados, thumbnail=config.get_thumb('stack'), text_color='gray' ))

        if config.get_setting('mnu_preferidos', default=True):
            if not config.get_setting('ord_preferidos', default=False):
                itemlist.append(item.clone( channel='tracking', action='mainlist', title='[B]Preferidos[/B]', context=context_preferidos, thumbnail=config.get_thumb('videolibrary'), text_color='wheat' ))

        if config.get_setting('mnu_desargas', default=True):
            if not config.get_setting('ord_descargas', default=False):
                itemlist.append(item.clone( channel='downloads', action='mainlist', title='[B]Descargas[/B]', context=context_descargas, thumbnail=config.get_thumb('downloads'), text_color='seagreen' ))

    try: last_ver = updater.check_addon_version()
    except: last_ver = True

    if not last_ver: last_ver = '[I][COLOR %s](desfasada)[/COLOR][/I]' % color_adver
    else: last_ver = ''

    context_ayuda = []

    tit = '[COLOR %s][B]Información versión[/B][/COLOR]' % color_infor
    context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_version'})

    last_fix = config.get_addon_version()

    if not 'desfasada' in last_ver:
        if 'fix' in last_fix:
            tit = '[COLOR %s]Información Fix[/COLOR]' % color_infor
            context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_last_fix'})

        tit = '[COLOR %s]Comprobar actualizaciones Fix[/COLOR]' % color_avis
        context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'check_addon_updates'})

        tit = '[COLOR %s][B]Forzar actualizaciones Fix[/B][/COLOR]' % color_adver
        context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'check_addon_updates_force'})

    tit = '[COLOR goldenrod][B]Miscelánea[/B][/COLOR]'
    context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_help_miscelanea'})

    tit = '[COLOR tan][B]Parámetros Menús[/B][/COLOR]'
    context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

    tit = '[COLOR %s]Información Dominios[/COLOR]' % color_infor
    context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})

    tit = '[COLOR %s][B]Últimos Cambios dominios[/B][/COLOR]' % color_exec
    context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

    tit = '[COLOR %s][B]Log Media Center[/B][/COLOR]' % color_adver
    context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_log'})

    tit = '[COLOR blue][B]Log Balandro Media Center[/B][/COLOR]'
    context_ayuda.append({'title': tit, 'channel': 'submnuteam', 'action': 'balandro_log'})

    tit = '[COLOR %s][B]Test sistema[/B][/COLOR]' % color_avis
    context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_test'})

    tit = '[COLOR darkorange][B]Test internet[/B][/COLOR]'
    context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'test_internet'})

    tit = '[COLOR green][B]Preguntas frecuentes[/B][/COLOR]'
    context_ayuda.append({'title': tit, 'channel': 'helper', 'action': 'show_help_faq'})

    tit = '[COLOR %s]Ajustes configuración[/COLOR]' % color_exec
    context_ayuda.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    title = '[B]Ayuda[/B] (%s)  %s' % (config.get_addon_version(), last_ver)

    itemlist.append(item.clone( channel='helper', action='mainlist', title=title, context=context_ayuda, thumbnail=config.get_thumb('help'), text_color='chartreuse' ))

    if not 'desfasada' in last_ver:
        if 'fix' in last_fix:
            tit = '[COLOR %s][B]Eliminar Fichero control Fix[/B][/COLOR]' % color_alert
            context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_last_fix'})

    itemlist.append(item.clone( channel='actions', action='open_settings', title='[B]Configuración[/B]', context=context_config,
                                folder=False, thumbnail=config.get_thumb('settings'), text_color='chocolate' ))

    return itemlist


def channels(item):
    logger.info()
    itemlist = []

    thumb_filmaffinity = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'filmaffinity.jpg')
    thumb_tmdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'tmdb.jpg')

    context_search = []

    tit = '[COLOR powderblue][B]Global configurar proxies[/B][/COLOR]'
    context_search.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

    if config.get_setting('proxysearch_excludes', default=''):
        tit = '[COLOR %s]Anular canales excluidos en Proxies[/COLOR]' % color_list_proxies
        context_search.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context_search.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    tit = '[COLOR %s][B]Información búsquedas[/B][/COLOR]' % color_infor
    context_search.append({'title': tit, 'channel': 'search', 'action': 'show_help'})

    tit = '[COLOR %s]Ajustes categoría Buscar[/COLOR]' % color_exec
    context_search.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    if item.extra == 'movies':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                        only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

        if config.get_setting('sub_mnu_cfg_search', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]', context=context_cfg_search,
                                        extra = 'movies', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='movie', title='[B]Buscar Película ...[/B]', context=context_search,
                              extra = 'movies', thumbnail=config.get_thumb('search'), text_color='deepskyblue' ))

        if config.get_setting('search_extra_trailers', default=False):
            itemlist.append(item.clone( channel='trailers', action='search', title='[B]Tráilers[/B]', text_color='darkgoldenrod' ))

        if config.get_setting('search_extra_main', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_news', title='[B]Novedades[/B]', thumbnail=config.get_thumb('novedades'), text_color='darksalmon' ))

            itemlist.append(item.clone( channel='tmdblists', action='mainlist', search_type='movie', title='[B]Búsquedas y listas en TMDB[/B]', thumbnail=thumb_tmdb, text_color=color_adver ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='mainlist', search_type='movie', title='[B]Búsquedas y listas en Filmaffinity[/B]', thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', context=context_cfg_search, extra='movies', thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con Películas'
        accion = 'mainlist_pelis'
        filtros = {'categories': 'movie'}

    elif item.extra == 'tvshows':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                        only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

        if config.get_setting('sub_mnu_cfg_search', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]', context=context_cfg_search, extra = 'tvshows', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='tvshow', title='[B]Buscar Serie ...[/B]', context=context_search, extra = 'tvshows', thumbnail=config.get_thumb('search'), text_color='hotpink' ))

        if config.get_setting('search_extra_main', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_news', title='[B]Novedades[/B]', thumbnail=config.get_thumb('novedades'), extra = 'tvshows', text_color='darksalmon' ))

            itemlist.append(item.clone( channel='tmdblists', action='mainlist', search_type='tvshow', title='[B]Búsquedas y listas en TMDB[/B]', thumbnail=thumb_tmdb, text_color=color_adver ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='mainlist', search_type='tvshow', title='[B]Búsquedas y listas en Filmaffinity[/B]', thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', context=context_cfg_search, extra='tvshows', thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con Series'
        accion = 'mainlist_series'
        filtros = {'categories': 'tvshow'}

    elif item.extra == 'documentaries':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                        only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

        if config.get_setting('sub_mnu_cfg_search', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]', context=context_cfg_search, extra = 'documentaries', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='documentary', title='[B]Buscar Documental ...[/B]', context=context_search, extra = 'documentaries', thumbnail=config.get_thumb('search'), text_color='cyan' ))

        if config.get_setting('search_extra_main', default=False):
            itemlist.append(item.clone( channel='filmaffinitylists', action='mainlist', search_type='documentary', title='[B]Búsquedas y listas en Filmaffinity[/B]', thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', context=context_cfg_search, extra='documentaries', thumbnail=config.get_thumb('heart'), text_color='pink' ))

        itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales con temática Documental[/B]', group = 'docs', text_color='magenta' ))

        item.category = 'Canales con Documentales'
        accion = 'mainlist'
        filtros = {'categories': 'documentary', 'searchable': True}

    elif item.extra == 'mixed':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                        only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

        if config.get_setting('sub_mnu_cfg_search', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]', context=context_cfg_search, extra = 'mixed', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='all', title='[B]Buscar Película y/o Serie ...[/B]', context=context_search, extra = 'mixed', thumbnail=config.get_thumb('search'), text_color='yellow' ))

        if config.get_setting('search_extra_trailers', default=False):
             itemlist.append(item.clone( channel='trailers', action='search', title='[B]Tráilers[/B]', text_color='darkgoldenrod' ))

        if config.get_setting('search_extra_main', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_news', title='[B]Novedades[/B]', thumbnail=config.get_thumb('novedades'), text_color='darksalmon' ))

            itemlist.append(item.clone( channel='tmdblists', action='mainlist', search_type='all', title='[B]Búsquedas y listas en TMDB[/B]', thumbnail=thumb_tmdb, text_color=color_adver ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='mainlist', search_type='all', title='[B]Búsquedas y listas en Filmaffinity[/B]', thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', context=context_cfg_search, extra='all', no_docs = item.no_docs, thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con Películas y Series (ambos contenidos)'
        accion = 'mainlist'
        filtros = {}

    elif item.extra == 'torrents':
        cliente_torrent = config.get_setting('cliente_torrent', default='Seleccionar')

        if cliente_torrent == 'Seleccionar' or cliente_torrent == 'Ninguno':
            itemlist.append(item.clone( channel='actions', action='open_settings', title='[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR blue][B]Torrents)[/B][/COLOR]' + ' [COLOR fuchsia][B]Motor:[/B][/COLOR][COLOR goldenrod][B] ' + cliente_torrent.capitalize() + '[/B][/COLOR]',
                                        folder=False, thumbnail=config.get_thumb('settings') ))

        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                        only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

        if config.get_setting('sub_mnu_cfg_search', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]', context=context_cfg_search, extra = 'torrents', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='all', title='[B][COLOR blue]Buscar Torrent[/COLOR] película y/o Serie ...[/B]', context=context_search, extra = 'only_torrents', thumbnail=config.get_thumb('search'), text_color='yellow' ))

        if config.get_setting('search_extra_trailers', default=False):
            itemlist.append(item.clone( channel='trailers', action='search', title='[B]Tráilers[/B]', text_color='darkgoldenrod' ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', context=context_cfg_search, extra='torrents', thumbnail=config.get_thumb('heart'), text_color='pink' ))

        itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales que pueden tener enlaces Torrents[/B]', group = 'torrents', text_color='magenta' ))

        item.category = 'Canales con archivos Torrents'
        accion = 'mainlist'
        filtros = {'categories': 'torrent'}

    else:
        if item.extra == 'adults': pass
        elif item.extra == 'anime': pass
        elif item.extra == 'dorama': pass
        elif item.extra == 'infantil': pass
        elif item.extra == 'tales': pass

        elif not item.extra == 'groups':
            presentar = True

            if config.get_setting('mnu_proxies', default=False):
                if item.extra == 'proxies': presentar = False

            if config.get_setting('mnu_problematicos', default=False):
                if item.extra == 'problematics': presentar = False

            if config.get_setting('mnu_desactivados', default=False):
                if item.extra == 'disableds': presentar = False

            if presentar:
               if config.get_setting('mnu_search_proxy_channels', default=False):
                   itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                               only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

               if config.get_setting('sub_mnu_cfg_search', default=True):
                   itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]', context=context_cfg_search, extra = 'all', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

               itemlist.append(Item( channel='search', action='search', search_type='all', title='[B]Buscar Película y/o Serie ...[/B]', context=context_search, thumbnail=config.get_thumb('search'), text_color='yellow' ))

               if config.get_setting('mnu_documentales', default=True):
                   itemlist.append(Item( channel='search', action='search', search_type='documentary', title='[B]Buscar Documental ...[/B]', context=context_search, thumbnail=config.get_thumb('search'), text_color='cyan' ))

               if config.get_setting('search_extra_trailers', default=False):
                   itemlist.append(item.clone( channel='trailers', action='search', title='[B]Tráilers[/B]', text_color='darkgoldenrod' ))

               if config.get_setting('search_extra_main', default=False):
                   itemlist.append(item.clone( channel='submnuctext', action='submnu_news', title='[B]Novedades[/B]', thumbnail=config.get_thumb('novedades'), text_color='darksalmon' ))

                   itemlist.append(item.clone( channel='tmdblists', action='mainlist', search_type='all', title='[B]Búsquedas y listas en TMDB[/B]', thumbnail=thumb_tmdb, text_color=color_adver ))

                   itemlist.append(item.clone( channel='filmaffinitylists', action='mainlist', search_type='all', title='[B]Búsquedas y listas en Filmaffinity[/B]', thumbnail=thumb_filmaffinity, text_color=color_adver ))

               if config.get_setting('sub_mnu_special', default=True):
                   itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', context=context_cfg_search, extra='all', thumbnail=config.get_thumb('heart'), text_color='pink' ))

        if item.extra == 'adults': item.category = 'Solo los Canales exclusivos para Adultos'
        elif item.extra == 'anime': item.category = 'Solo los Canales exclusivos de Animes'
        elif item.extra == 'dorama': item.category = 'Solo los Canales exclusivos de Doramas'
        elif item.extra == 'infantil': item.category = 'Solo los Canales exclusivos Infantiles'
        elif item.extra == 'tales': item.category = 'Solo los Canales con temática de Novelas'
        elif item.extra == 'suggested': item.category = 'Solo los Canales Sugeridos'
        elif item.extra == 'proxies': item.category = 'Solo los Canales con Proxies Memorizados'
        elif item.extra == 'disableds': item.category = 'Solo los Canales que estén Desactivados'
        elif item.extra == 'problematics': item.category = 'Solo los Canales que sean Problemáticos (Predominan Sin enlaces Disponibles/Válidos/Soportados)'
        elif not item.extra == 'groups': item.category = 'Todos los Canales'
        else: item.category = 'Canales con Agrupaciones (novedades, estrenos, temáticas, países, años, plataformas, etc.)'

        if item.extra == 'infantil':
            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                            only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

            if config.get_setting('sub_mnu_cfg_search', default=True):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]', context=context_cfg_search, extra = 'mixed', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

            itemlist.append(Item( channel='search', action='search', search_type='all', title='[B]Buscar Película y/o Serie ...[/B]', context=context_search, extra = 'mixed', thumbnail=config.get_thumb('search'), text_color='yellow' ))

            if config.get_setting('search_extra_trailers', default=False):
                itemlist.append(item.clone( channel='trailers', action='search', title='[B]Tráilers[/B]', text_color='darkgoldenrod' ))

            if config.get_setting('search_extra_main', default=False):
                itemlist.append(item.clone( channel='tmdblists', action='mainlist', search_type='all', title='[B]Búsquedas y listas en TMDB[/B]', thumbnail=thumb_tmdb, text_color=color_adver ))

                itemlist.append(item.clone( channel='filmaffinitylists', action='mainlist', search_type='all', title='[B]Búsquedas y listas en Filmaffinity[/B]', thumbnail=thumb_filmaffinity, text_color=color_adver ))

            itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales con contenido Infantil[/B]', group = 'kids', text_color='magenta' ))

        if item.extra == 'tales':
            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                            only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

            if config.get_setting('sub_mnu_cfg_search', default=True):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]', context=context_cfg_search, extra = 'tvshows', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

            itemlist.append(Item( channel='search', action='search', search_type='tvshow', title='[B]Buscar Serie ...[/B]', context=context_search, extra = 'tvshows', thumbnail=config.get_thumb('search'), text_color='hotpink' ))

            if config.get_setting('search_extra_main', default=False):
                itemlist.append(item.clone( channel='tmdblists', action='mainlist', search_type='tvshow', title='[B]Búsquedas y listas en TMDB[/B]', thumbnail=thumb_tmdb, text_color=color_adver ))

                itemlist.append(item.clone( channel='filmaffinitylists', action='mainlist', search_type='tvshow', title='[B]Búsquedas y listas en Filmaffinity[/B]', thumbnail=thumb_filmaffinity, text_color=color_adver ))

            itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales con contenido de Novelas[/B]', group = 'tales', text_color='magenta' ))

        if item.extra == 'dorama':
            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                            only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

            itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Todos los canales con contenido Dorama[/B]', group = 'dorama', text_color='magenta' ))

            itemlist.append(Item( channel='search', action='search', search_type='all', title='Buscar Dorama ...',
                                  thumbnail=config.get_thumb('computer'), search_special = 'dorama', text_color='magenta' ))

        if item.extra == 'adults' or item.extra == 'anime':
            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                            only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

            if not config.get_setting('adults_password'):
                itemlist.append(item.clone( channel='helper', action='show_help_adults', title='[B]Información parental[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

            if item.extra == 'adults':
                itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales que pueden tener vídeos para Adultos[/B]', group = 'adults', text_color='magenta' ))

            if item.extra == 'anime':
                itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Todos los canales con contenido Anime[/B]', group = 'anime', text_color='magenta' ))

                itemlist.append(Item( channel='search', action='search', search_type='all', title='Buscar Anime ...', thumbnail=config.get_thumb('anime'), search_special = 'anime', text_color='springgreen' ))

        if item.extra == 'proxies' or item.extra == 'problematics':
            itemlist.append(item.clone( channel='actions', action='open_settings', title='[B]Configuración[/B]', context=context_config,
                                        folder=False, thumbnail=config.get_thumb('settings'), text_color='chocolate' ))

        accion = 'mainlist'
        filtros = {}

    channels_list_status = config.get_setting('channels_list_status', default=0)
    if channels_list_status > 0:
        filtros['status'] = 0 if channels_list_status == 1 else 1

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0

    for ch in ch_list:
        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

        if not item.extra == 'all':
            if config.get_setting('search_extra_trailers', default=False):
                if str(ch['clusters']) == "['trailers']": continue

        if item.extra == 'problematics':
            if not 'problematic' in ch['clusters']: continue
        else:
            if not item.extra == 'all':
                if config.get_setting('mnu_problematicos', default=False):
                    if 'problematic' in ch['clusters']: continue

        if item.extra == 'disableds':
            if not ch['status'] == -1: continue
        else:
            if not item.extra == 'all':
                if config.get_setting('mnu_desactivados', default=False):
                    if ch['status'] == -1: continue

        if item.extra == 'proxies':
            if not 'Puede requerir el uso de proxies' in ch['notes']: continue

            if not config.get_setting(cfg_proxies_channel, default=''): continue

        else:
            if not item.extra == 'all':
                if not item.extra == 'disableds':
                    if config.get_setting('mnu_proxies', default=False):
                        if 'Puede requerir el uso de proxies' in ch['notes']:
                            if config.get_setting(cfg_proxies_channel, default=''): continue

        if item.extra == 'movies':
            if ch['searchable'] == False:
                if 'adults' in ch['clusters']: continue
                elif 'anime' in ch['clusters']:
                   if config.get_setting('mnu_animes', default=True): continue
                elif 'dorama' in ch['clusters']:
                   if config.get_setting('mnu_doramas', default=True): continue
                elif 'infantil' in ch['clusters']:
                   if config.get_setting('mnu_infantiles', default=True): continue
                elif 'tales' in ch['clusters']:
                   if config.get_setting('mnu_novelas', default=True): continue

        elif item.extra == 'tvshows':
            if ch['searchable'] == False:
                if 'adults' in ch['clusters']: continue
                elif 'anime' in ch['clusters']:
                   if config.get_setting('mnu_animes', default=True): continue
                elif 'dorama' in ch['clusters']:
                   if config.get_setting('mnu_doramas', default=True): continue

                elif 'infantil' in ch['clusters']:
                   if not ch['id'] == 'seodiv':
                       if config.get_setting('mnu_infantiles', default=True): continue

                elif 'tales' in ch['clusters']:
                   if config.get_setting('mnu_novelas', default=True): continue

        elif item.extra == 'adults':
            if ch['searchable'] == True: continue
            if not 'adults' in ch['clusters']: continue

        elif item.extra == 'anime':
            if ch['searchable'] == True: continue
            if not 'anime' in ch['clusters']: continue

        elif item.extra == 'mixed':
            tipos = ch['search_types']
            if 'documentary' in tipos: continue

            if not 'movie' in tipos: continue
            if not 'tvshow' in tipos: continue

        elif item.extra == 'torrents':
            tipos = ch['search_types']
            if 'documentary' in tipos: continue

        elif item.extra == 'suggested':
            if not 'suggested' in ch['clusters']: continue

            if not config.get_setting('mnu_documentales', default=True):
                if str(ch['search_types']) == "['documentary']": continue

            if not config.get_setting('mnu_novelas', default=True):
                if 'exclusivamente en Novelas' in ch['notes']: continue

        elif item.extra == 'infantil':
            if not 'infantil' in ch['clusters']: continue

        elif item.extra == 'tales':
            if not 'tales' in ch['clusters']: continue

        elif item.extra == 'dorama':
            if ch['searchable'] == True: continue
            if not 'dorama' in ch['clusters']: continue

        else:
           if config.get_setting('mnu_simple', default=False):
               if ch['searchable'] == False:
                   if 'adults' in ch['clusters']: continue
                   elif 'anime' in ch['clusters']: continue
                   elif 'dorama' in ch['clusters']: continue
                   elif 'infantil' in ch['clusters']: continue
                   elif 'tales' in ch['clusters']: continue
               else:
                   if not config.get_setting('mnu_documentales', default=True):
                       if str(ch['search_types']) == "['documentary']": continue

                   if not config.get_setting('mnu_novelas', default=True):
                       if 'exclusivamente en Novelas' in ch['notes']: continue

           else:
              if not config.get_setting('mnu_documentales', default=True):
                  if str(ch['search_types']) == "['documentary']": continue

              if not config.get_setting('mnu_infantiles', default=True):
                  if 'infantil' in ch['clusters']: continue

              if not config.get_setting('mnu_novelas', default=True):
                  if 'exclusivamente en Novelas' in ch['notes']: continue
                  if 'tales' in ch['clusters']: continue

              if not config.get_setting('mnu_torrents', default=True):
                  if 'enlaces Torrent exclusivamente' in ch['notes']: continue

              if not config.get_setting('mnu_doramas', default=True):
                  if ch['searchable'] == False: continue
                  if 'dorama' in ch['clusters']: continue

              if not config.get_setting('mnu_animes', default=True):
                  if ch['searchable'] == False: continue
                  if 'anime' in ch['clusters']: continue

              if not config.get_setting('mnu_adultos', default=True):
                  if ch['searchable'] == False: continue
                  if 'adults' in ch['clusters']: continue

        context = []

        if 'proxies' in ch['notes'].lower():
            if config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
                context.append({'title': tit, 'channel': item.channel, 'action': '_quitar_proxies'})

        if ch['searchable']:
            if not ch['status'] == -1:
                cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'

                if config.get_setting(cfg_searchable_channel, default=False):
                    tit = '[COLOR %s][B]Quitar exclusión en búsquedas[/B][/COLOR]' % color_adver
                    context.append({'title': tit, 'channel': item.channel, 'action': '_quitar_no_searchables'})
                else:
                    tit = '[COLOR %s][B]Excluir de búsquedas[/B][/COLOR]' % color_adver
                    context.append({'title': tit, 'channel': item.channel, 'action': '_poner_no_searchables'})

        if ch['status'] != 1:
            tit = '[COLOR %s][B]Marcar canal como Preferido[/B][/COLOR]' % color_list_prefe
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 1})

        if ch['status'] != 0:
            if ch['status'] == 1:
                tit = '[COLOR %s][B]Des-Marcar canal como Preferido[/B][/COLOR]' % color_list_prefe
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            elif ch['status'] == -1:
                tit = '[COLOR %s][B]Des-Marcar canal como Desactivado[/B][/COLOR]' % color_list_inactive
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            else:
                tit = '[COLOR white][B]Marcar canal como Activo[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})

        if ch['status'] != -1:
            tit = '[COLOR %s][B]Marcar canal como Desactivado[/B][/COLOR]' % color_list_inactive
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': -1})

        cfg_domains = False

        if 'current' in ch['clusters']:
            cfg_domains = True

            tit = '[COLOR %s]Información Dominios[/COLOR]' % color_infor
            context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})

        tit = '[COLOR %s][B]Últimos Cambios dominios[/B][/COLOR]' % color_exec
        context.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

        if cfg_domains:
            tit = '[COLOR yellowgreen][B]Dominio vigente[/B][/COLOR]'
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominio_vigente'})

            if 'Dispone de varios posibles dominios' in ch['notes']:
                tit = '[COLOR powderblue][B]Configurar dominio a usar[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_dominios'})

            tit = '[COLOR orange][B]Modificar dominio Memorizado[/B][/COLOR]'
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominio_memorizado'})

        if 'register' in ch['clusters']:
            cfg_user_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_username'
            cfg_pass_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_password'

            if not config.get_setting(cfg_user_channel, default='') or not config.get_setting(cfg_pass_channel, default=''):
                tit = '[COLOR green][B]Información para Registrarse[/B][/COLOR]'
                context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_register'})

                tit = '[COLOR teal][B]Credenciales Cuenta[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_credenciales'})
            else:
                cfg_login_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_login'

                presentar = True
                if 'dominios' in ch['notes'].lower():
                    cfg_dominio_channel = 'channel_' + ch['id'] + '_dominio'
                    if not config.get_setting(cfg_dominio_channel, default=''): presentar = False

                if presentar:
                    if config.get_setting(cfg_login_channel, default=False):
                        tit = '[COLOR teal][B]Cerrar sesión[/B][/COLOR]'
                        context.append({'title': tit, 'channel': item.channel, 'action': '_credenciales'})

        if 'proxies' in ch['notes'].lower():
            if not config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s]Información proxies[/COLOR]' % color_infor
                context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

            tit = '[COLOR %s][B]Configurar proxies a usar[/B][/COLOR]' % color_list_proxies
            context.append({'title': tit, 'channel': item.channel, 'action': '_proxies'})

        if 'notice' in ch['clusters']:
            tit = '[COLOR tan][B]Aviso del canal[/B][/COLOR]'
            context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_' + ch['id']})
		
        tit = '[COLOR darkorange][B]Test Web del canal[/B][/COLOR]'
        context.append({'title': tit, 'channel': item.channel, 'action': '_tests'})

        if cfg_domains:
            tit = '[COLOR %s]Ajustes categoría Dominios[/COLOR]' % color_exec
            context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

        color = color_list_prefe if ch['status'] == 1 else 'white' if ch['status'] == 0 else color_list_inactive

        plot = ''
        if item.extra == 'all': plot += '[' + ', '.join([config.get_localized_category(ct) for ct in ch['categories']]) + '][CR]'
        plot += '[' + ', '.join([idioma_canal(lg) for lg in ch['language']]) + ']'
        if ch['notes'] != '': plot += '[CR][CR]' + ch['notes']

        titulo = ch['name']

        if ch['status'] == -1:
            titulo += '[I][COLOR %s] (desactivado)[/COLOR][/I]' % color_list_inactive
            if config.get_setting(cfg_proxies_channel, default=''): titulo += '[I][COLOR %s] (proxies)[/COLOR][/I]' % color_list_proxies
        else:
            if config.get_setting(cfg_proxies_channel, default=''):
                if ch['status'] == 1: titulo += '[I][COLOR %s] (proxies)[/COLOR][/I]' % color_list_proxies
                else: color = color_list_proxies

        if 'register' in ch['clusters']:
            cfg_user_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_username'
            cfg_pass_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_password'
            if not config.get_setting(cfg_user_channel, default='') or not config.get_setting(cfg_pass_channel, default=''):
               titulo += '[I][COLOR teal] (cuenta)[/COLOR][/I]'
            else:
               cfg_login_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_login'

               if config.get_setting(cfg_login_channel, default=False):
                   presentar = True
                   if 'dominios' in ch['notes'].lower():
                       cfg_dominio_channel = 'channel_' + ch['id'] + '_dominio'
                       if not config.get_setting(cfg_dominio_channel, default=''): presentar = False

                   if presentar: titulo += '[I][COLOR teal] (sesion)[/COLOR][/I]'
               else: titulo += '[I][COLOR teal] (login)[/COLOR][/I]'

        if not PY3:
            if 'mismatched' in ch['clusters']: titulo += '[I][COLOR coral] (Incompatible)[/COLOR][/I]'

        if 'inestable' in ch['clusters']:
            if config.get_setting('mnu_simple', default=False): continue
            elif config.get_setting('channels_list_no_inestables', default=False): continue

            titulo += '[I][COLOR plum] (inestable)[/COLOR][/I]'

        if 'problematic' in ch['clusters']:
            if config.get_setting('mnu_simple', default=False): continue
            elif config.get_setting('mnu_problematicos', default=False): continue
            elif config.get_setting('channels_list_no_problematicos', default=False): continue

            titulo += '[I][COLOR darkgoldenrod] (problemático)[/COLOR][/I]'

        if config.get_setting('mnu_simple', default=False):
            if 'movie' in ch['categories']:
                if "tvshow" in ch['categories']:
                    titulo += '[B][I][COLOR teal] películas, series[/COLOR][/I][/B]'
                    if 'tales' in ch['clusters']: titulo += '[B][I][COLOR limegreen] novelas[/COLOR][/I][/B]'
                else: titulo += '[B][I][COLOR deepskyblue] películas[/COLOR][/I][/B]'
            else:
                if "tvshow" in ch['categories']:
                    titulo += '[B][I][COLOR hotpink] series[/COLOR][/I][/B]'
                    if 'tales' in ch['clusters']: titulo += '[B][I][COLOR limegreen] novelas[/COLOR][/I][/B]'
                elif "documentary" in ch['categories']: titulo += '[B][I][COLOR cyan] documentales[/COLOR][/I][/B]'

        i =+ 1

        itemlist.append(Item( channel=ch['id'], action=accion, title=titulo, context=context, text_color=color, plot = plot, thumbnail=ch['thumbnail'], category=ch['name'] ))

    if len(ch_list) == 0 or i == 0:
        if item.extra == 'Proxies':
            itemlist.append(item.clone( channel='filters', action='with_proxies', title='[B]Opción Sin canales con Proxies Memorizados[/B]',
                                        text_color=color_list_proxies, thumbnail=config.get_thumb('stack'), folder=False ))
        elif item.extra == 'problematics':
            itemlist.append(item.clone( channel='filters', action='show_channels_list', title='[B]Opción Sin canales Problemáticos[/B]',
                                        text_color='darkgoldenrod', problematics=True, thumbnail=config.get_thumb('stack'), folder=False ))
        elif item.extra == 'disableds':
            itemlist.append(item.clone( channel='filters', action='channels_status', title='[B]Opción Sin canales Desactivados[/B]',
                                        text_color=color_list_inactive, des_rea=True, thumbnail=config.get_thumb('stack'), folder=False ))
        else:
            itemlist.append(item.clone( channel='filters', action='channels_status', title='[B]Opción Sin canales Preferidos[/B]', text_color=color_list_prefe,
                                        des_rea=False, thumbnail=config.get_thumb('stack'), folder=False ))

    return itemlist


def idioma_canal(lang):
    idiomas = { 'cast': 'Castellano', 'lat': 'Latino', 'eng': 'Inglés', 'pt': 'Portugués', 'vo': 'VO', 'vose': 'Vose', 'vos': 'Vos', 'cat': 'Català' }
    return idiomas[lang] if lang in idiomas else lang


def _marcar_canal(item):
    from modules import submnuctext
    submnuctext._marcar_canal(item)


def _poner_no_searchables(item):
    from modules import submnuctext
    submnuctext._poner_no_searchable(item)

def _quitar_no_searchables(item):
    from modules import submnuctext
    submnuctext._quitar_no_searchable(item)


def _quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)


def _dominio_vigente(item):
    from modules import submnuctext
    submnuctext._dominio_vigente(item)


def _dominio_memorizado(item):
    from modules import submnuctext
    submnuctext._dominio_memorizado(item)


def _dominios(item):
    from modules import submnuctext
    submnuctext._dominios(item)


def _credenciales(item):
    from modules import submnuctext
    submnuctext._credenciales(item)


def _proxies(item):
    from modules import submnuctext
    submnuctext._proxies(item)


def _tests(item):
    from modules import submnuctext
    submnuctext._test_webs(item)
