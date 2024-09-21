# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3: PY3 = True
else: PY3 = False


import os

from platformcode import config, logger
from core.item import Item

from core import channeltools, scrapertools


color_list_prefe = config.get_setting('channels_list_prefe_color', default='gold')
color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')
color_list_inactive = config.get_setting('channels_list_inactive_color', default='gray')

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


thumb_filmaffinity = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'filmaffinity.jpg')
thumb_tmdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'tmdb.jpg')


con_incidencias = ''
no_accesibles = ''

try:
    with open(os.path.join(config.get_runtime_path(), 'dominios.txt'), 'r') as f: txt_status=f.read(); f.close()
except:
    try: txt_status = open(os.path.join(config.get_runtime_path(), 'dominios.txt'), encoding="utf8").read()
    except: txt_status = ''

if txt_status:
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


context_buscar = []

tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR fuchsia][B]Preferencias Play[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_play_parameters'})

tit = '[COLOR powderblue][B]Preferencias Buscar[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'search', 'action': 'show_help_parameters'})

tit = '[COLOR darkcyan][B]Preferencias Proxies[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_prx_parameters'})

tit = '[COLOR %s]Información Dominios[/COLOR]' % color_infor
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR %s][B]Quitar Dominios Memorizados[/B][/COLOR]' % color_alert
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'manto_domains'})

tit = '[COLOR gold][B]Qué Canales No Intervienen[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'channels_no_searchables'})

tit = '[COLOR gray][B]Qué Canales están Desactivados[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'filters', 'action': 'no_actives'})

tit = '[COLOR yellow][B]Búsquedas Solo en ...[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_included'})

if config.get_setting('search_included_all', default=''):
    tit = '[COLOR indianred][B]Quitar Búsquedas Solo en ...[/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_included_del'})

tit = '[COLOR greenyellow][B]Excluir Canales[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded'})

if config.get_setting('search_excludes_all', default=''):
    tit = '[COLOR violet][B]Quitar Canales Excluidos[/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})

if config.get_setting('search_excludes_movies', default=''):
    tit = '[B][COLOR deepskyblue]Películas [COLOR violet]Quitar Canales Excluidos [/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del_movies'})

if config.get_setting('search_excludes_tvshows', default=''):
    tit = '[B][COLOR hotpink]Series [COLOR violet]Quitar Canales Excluidos [/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del_tvshows'})

if config.get_setting('search_excludes_documentaries', default=''):
    tit = '[B][COLOR cyan]Documentales [COLOR violet]Quitar Canales Excluidos [/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del_documentaries'})

if config.get_setting('search_excludes_torrents', default=''):
    tit = '[B][COLOR blue]Torrents [COLOR violet]Quitar Canales Excluidos [/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del_torrents'})

if config.get_setting('search_excludes_mixed', default=''):
    tit = '[B][COLOR teal]Películas y/ó Series [COLOR violet]Quitar Canales Excluidos [/B][/COLOR]'
    context_buscar.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del_mixed'})

tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_buscar.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_buscar.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_infor
context_buscar.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s][B]Quitar Proxies Actuales[/B][/COLOR]' % color_list_proxies
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR %s][B]Información Búsquedas[/B][/COLOR]' % color_infor
context_buscar.append({'title': tit, 'channel': 'search', 'action': 'show_help'})

tit = '[COLOR %s]Ajustes categorías Canales, Dominios, Play, Proxies y Buscar[/COLOR]' % color_exec
context_buscar.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_proxy_channels = []

tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_proxy_channels.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_proxy_channels.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_avis
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s][B]Quitar Proxies Actuales[/B][/COLOR]' % color_list_proxies
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR %s]Ajustes categorías Menú, Canales, Dominios y Proxies[/COLOR]' % color_exec
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_generos = []

tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_generos.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_generos.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_generos.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_generos.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_infor
context_generos.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s][B]Quitar Proxies Actuales[/B][/COLOR]' % color_list_proxies
context_generos.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR %s]Ajustes categorías Menú, Canales, Dominios y Proxies[/COLOR]' % color_exec
context_generos.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_cfg_search = []

tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_cfg_search.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR %s]Ajustes categoría Menú[/COLOR]' % color_exec
context_cfg_search.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_torrents = []

tit = '[COLOR tan][B]Preferencias Canales[/B][/COLOR]'
context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_torrents.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

if config.get_setting('cliente_torrent') == 'Seleccionar' or config.get_setting('cliente_torrent') == 'Ninguno':
    tit = '[COLOR %s][B]Información Motores Torrent[/B][/COLOR]' % color_infor
    context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_help_torrents'})

tit = '[COLOR %s][B]Motores torrents instalados[/B][/COLOR]' % color_avis
context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_clients_torrent'})

tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_torrents.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_torrents.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_avis
context_torrents.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s][B]Quitar Proxies Actuales[/B][/COLOR]' % color_list_proxies
context_torrents.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR %s]Ajustes categorías Canales, Dominios, Proxies y Torrents[/COLOR]' % color_exec
context_torrents.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_parental = []

tit = '[COLOR tan][B]Preferencias Canales[/B][/COLOR]'
context_parental.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_parental.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

if config.get_setting('adults_password'):
    tit = '[COLOR %s][B]Eliminar Pin Parental[/B][/COLOR]' % color_adver
    context_parental.append({'title': tit, 'channel': 'actions', 'action': 'adults_password_del'})
else:
    tit = '[COLOR %s][B]Información Parental[/B][/COLOR]' % color_infor
    context_parental.append({'title': tit, 'channel': 'helper', 'action': 'show_help_adults'})

    tit = '[COLOR %s][B]Establecer Pin Parental[/B][/COLOR]' % color_avis
    context_parental.append({'title': tit, 'channel': 'actions', 'action': 'adults_password'})

tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_parental.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_parental.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_avis
context_parental.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s][B]Quitar Proxies Actuales[/B][/COLOR]' % color_list_proxies
context_parental.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR %s]Ajustes categorías Canales, Parental, Dominios y Proxies[/COLOR]' % color_exec
context_parental.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

context_config = []

tit = '[COLOR tan][B]Preferencias Canales[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

tit = '[COLOR %s]Información Dominios[/COLOR]' % color_infor
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})

tit = '[COLOR %s][B]Últimos Cambios Dominios[/B][/COLOR]' % color_exec
context_config.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR %s][B]Quitar Dominios Memorizados[/B][/COLOR]' % color_alert
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_domains'})

tit = '[COLOR green][B]Información Plataforma[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_plataforma'})

tit = '[COLOR %s][B]Quitar Proxies Memorizados[/B][/COLOR]' % color_alert
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR olive][B]Limpiezas[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_limpiezas'})

tit = '[COLOR darkorange][B]Borrar Carpeta Caché[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_folder_cache'})

tit = '[COLOR %s][B]Sus Ajustes Personalizados[/B][/COLOR]' % color_avis
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_sets'})

tit = '[COLOR %s][B]Cookies Actuales[/B][/COLOR]' % color_infor
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_cook'})

tit = '[COLOR %s][B]Eliminar Cookies[/B][/COLOR]' % color_alert
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_cookies'})

tit = '[COLOR %s]Sus Advanced Settings[/COLOR]' % color_adver
context_config.append({'title': tit, 'channel': 'helper', 'action': 'show_advs'})

tit = '[COLOR %s][B]Eliminar Advanced Settings[/B][/COLOR]' % color_alert
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_advs'})

tit = '[COLOR mediumaquamarine][B]Restablecer Parámetros Internos[/B][/COLOR]'
context_config.append({'title': tit, 'channel': 'actions', 'action': 'manto_params'})

context_usual = []

tit = '[COLOR tan][B]Preferencias Canales[/B][/COLOR]'
context_usual.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

tit = '[COLOR mediumaquamarine][B]Últimos Cambios Dominios[/B][/COLOR]'
context_usual.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

tit = '[COLOR yellow][B]Preferencias Buscar[/B][/COLOR]'
context_usual.append({'title': tit, 'channel': 'search', 'action': 'show_help_parameters'})

tit = '[COLOR powderblue][B]Global Configurar Proxies[/B][/COLOR]'
context_usual.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

if config.get_setting('proxysearch_excludes', default=''):
    tit = '[COLOR %s]Anular canales excluidos de Proxies[/COLOR]' % color_adver
    context_usual.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

tit = '[COLOR %s]Información Proxies[/COLOR]' % color_avis
context_usual.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s][B]Quitar Proxies Actuales[/B][/COLOR]' % color_list_proxies
context_usual.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

tit = '[COLOR %s]Ajustes categorías Canales, Dominios y Proxies[/COLOR]' % color_exec
context_usual.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


def mainlist(item):
    logger.info()
    itemlist = []

    item.category = 'Agrupaciones de Canales'

    if config.get_setting('mnu_search_proxy_channels', default=False):
        itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels, only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

    if config.get_setting('sub_mnu_cfg_search', default=True):
        itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title= '[B]Personalizar búsquedas[/B]', context=context_cfg_search, thumbnail=config.get_thumb('help'), text_color='moccasin', extra = 'all' ))

    if not item.mnu_lang:
        if config.get_setting('sub_mnu_favoritos', default=False):
            itemlist.append(item.clone( channel='favoritos', action='mainlist', title='[B]Favoritos[/B]', context=context_cfg_search, thumbnail=config.get_thumb('star'), text_color='plum' ))

        if config.get_setting('sub_mnu_news', default=True):
            presentar = False
            if config.get_setting('mnu_simple', default=False): presentar = True
            elif config.get_setting('mnu_pelis', default=True): presentar = True
            elif config.get_setting('mnu_series', default=True): presentar = True
            elif config.get_setting('channels_link_pyse', default=False): presentar = True

        if presentar:
            itemlist.append(item.clone( channel='submnuctext', action='submnu_news', title='[B]Novedades[/B]', context=context_cfg_search, thumbnail=config.get_thumb('novedades'), text_color='darksalmon' ))

        if not config.get_setting('mnu_simple', default=False):
            if config.get_setting('mnu_generos', default=True):
               itemlist.append(item.clone( channel='submnuctext', action='submnu_genres', title= 'Géneros', context=context_generos, thumbnail=config.get_thumb('genres'), text_color='thistle' ))

        itemlist.append(Item( channel='search', action='mainlist', title='[B]Buscar[/B]', context=context_buscar, thumbnail=config.get_thumb('search'), text_color='yellow' ))

        if not config.get_setting('mnu_simple', default=False): tit_mnu = '[B][I]Menú Grupos:[/I][/B]'
        else: tit_mnu = '[B][I]Menú Grupos Simplificado:[/I][/B]'

        itemlist.append(item.clone( action='', title=tit_mnu, context=context_cfg_search, text_color='tan', folder=False ))

        if presentar:
            itemlist.append(item.clone( title = ' - [B]Novedades[/B]', action = 'submnu_news', context=context_usual, thumbnail=config.get_thumb('novedades'), text_color='darkcyan' ))

        itemlist.append(item.clone( title = ' - [B]Películas y/ó Series[/B]', action = 'submnu_alls', context=context_usual, thumbnail=config.get_thumb('booklet'), text_color='goldenrod' ))

        if config.get_setting('channels_link_pyse', default=False) or config.get_setting('mnu_pelis', default=True):
            itemlist.append(item.clone( title = ' - [B]Películas[/B]', action = 'submnu_pelis', context=context_usual, thumbnail=config.get_thumb('movie'), text_color='deepskyblue' ))

        if config.get_setting('channels_link_pyse', default=False) or config.get_setting('mnu_series', default=True):
            itemlist.append(item.clone( title = ' - [B]Series[/B]', action = 'submnu_series', context=context_usual, thumbnail=config.get_thumb('tvshow'), text_color='hotpink' ))

        if not config.get_setting('mnu_simple', default=False):
            if config.get_setting('mnu_documentales', default=True):
                itemlist.append(item.clone( title = ' - [B]Documentales[/B]', action = 'submnu_docs', context=context_usual, thumbnail=config.get_thumb('documentary'), text_color='cyan' ))

        presentar = True
        if config.get_setting('mnu_simple', default=False): presentar = False

        if presentar:
            if config.get_setting('mnu_doramas', default=True):
                itemlist.append(item.clone( title = ' - [B]Doramas[/B]', action = 'submnu_doramas', context=context_usual, thumbnail=config.get_thumb('computer'), text_color='firebrick' ))

        presentar = True
        descartar_xxx = config.get_setting('descartar_xxx', default=False)

        if config.get_setting('mnu_simple', default=False): presentar = False
        else:
           if descartar_xxx:
               if descartar_anime: presentar = False

        if presentar:
            if not config.get_setting('descartar_anime', default=True):
                itemlist.append(item.clone( title = ' - [B]Animes[/B]', action = 'submnu_animes', context=context_parental, thumbnail=config.get_thumb('anime'), text_color='springgreen' ))

            if not descartar_xxx:
                itemlist.append(item.clone( title = ' - [B]Adultos (+18)[/B]', action = 'submnu_adults', context=context_parental, thumbnail=config.get_thumb('adults'), text_color='orange' ))

        itemlist.append(item.clone( title = ' - [B]Diversos[/B]', action = 'submnu_diversos', context=context_usual, thumbnail=config.get_thumb('crossroads'), text_color='teal' ))

    presentar = False
    if item.mnu_lang: presentar = True
    else:
       if config.get_setting('mnu_idiomas', default=True): presentar = False

    if presentar:
        itemlist.append(item.clone( title = '[B]Idiomas (Audios en los canales):[/B]', action = '', thumbnail=config.get_thumb('idiomas'), text_color='yellowgreen' ))

        itemlist.append(item.clone( channel='helper', action='show_help_audios', title= ' - [COLOR green][B]Información[/B][/COLOR] [COLOR cyan][B]Idiomas[/B][/COLOR] en los Audios de los Vídeos', thumbnail=config.get_thumb('news') ))

        itemlist.append(item.clone( channel='helper', action='show_play_parameters', title=' - Qué [COLOR chocolate][B]Ajustes[/B][/COLOR] tiene en preferencias [COLOR fuchsia][B]Play[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

        itemlist.append(item.clone( title = ' - Audio [COLOR goldenrod][B]Múltiple[/B][/COLOR]', action = 'ch_groups', group = 'all', extra = 'mixed', thumbnail=config.get_thumb('stack'), langs = True ))
        itemlist.append(item.clone( title = ' - Audio solo en [COLOR chartreuse][B]Castellano[/B][/COLOR]', action = 'ch_groups', group = 'cast', extra = 'mixed', thumbnail=config.get_thumb('stack'), langs = True ))
        itemlist.append(item.clone( title = ' - Audio solo en [COLOR limegreen][B]Latino[/B][/COLOR]', action = 'ch_groups', group = 'lat', extra = 'mixed', thumbnail=config.get_thumb('stack'), langs = True ))
        itemlist.append(item.clone( title = ' - Audio solo en [COLOR red][B]Vose[/B][/COLOR]', action = 'ch_groups', group = 'vose', extra = 'mixed', thumbnail=config.get_thumb('stack'), langs = True ))
        itemlist.append(item.clone( title = ' - Audio solo en [COLOR indianred][B]Vo ó Vos[/B][/COLOR]', action = 'ch_groups', group = 'vo', extra = 'mixed', thumbnail=config.get_thumb('stack'), langs = True ))

        if item.mnu_lang:
            itemlist.append(item.clone( channel='actions', action = 'open_settings', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] preferencias (categoría [COLOR fuchsia][B]Play[/B][/COLOR])', context=context_config, folder=False, thumbnail=config.get_thumb('settings') ))

    else:
        if config.get_setting('mnu_idiomas', default=True):
            itemlist.append(item.clone( title = ' - [B]Audios[/B]', action = 'submnu_audios', thumbnail=config.get_thumb('idiomas'), text_color='violet' ))

    if not presentar:
        itemlist.append(item.clone( channel='actions', action='open_settings', title='[COLOR chocolate][B]Ajustes[/B][/COLOR] preferencias (categoría [COLOR tan][B]Menú)[/B][/COLOR]', context=context_config, folder=False, thumbnail=config.get_thumb('settings') ))

    return itemlist


def submnu_news(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action = '', title = '[B]NOVEDADES[/B]', thumbnail=config.get_thumb('novedades'), text_color='darkcyan' ))

    presentar = False

    if config.get_setting('search_extra_main', default=False): presentar = True
    elif config.get_setting('mnu_pelis', default=True): presentar = True
    elif config.get_setting('mnu_series', default=True): presentar = True
    elif config.get_setting('channels_link_pyse', default=False): presentar = True

    if presentar:
        itemlist.append(item.clone( title = '[B][I]Canales:[/I][/B]', action = '', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='tan' ))

        if config.get_setting('mnu_pelis', default=True):
            itemlist.append(item.clone( title = ' - De [COLOR deepskyblue][B]Películas[/B][/COLOR] con Estrenos y/ó Novedades', thumbnail=config.get_thumb('movie'), action = 'ch_groups', group = 'news', extra = 'movies', ))

        if config.get_setting('mnu_series', default=True):
            itemlist.append(item.clone( title = ' - De [COLOR hotpink][B]Series[/B][/COLOR] con Episodios Nuevos y/ó Últimos', thumbnail=config.get_thumb('tvshow'), action = 'ch_groups', group = 'lasts', extra = 'tvshows' ))

        if config.get_setting('search_extra_main', default=False):
            itemlist.append(item.clone( title = '[B]Búsquedas a través de Listas en TMDB:[/B]', action = '', thumbnail=thumb_tmdb, text_color='violet' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - Películas en Cartelera', extra='now_playing', thumbnail=config.get_thumb('novedades'), search_type = 'movie' ))

            itemlist.append(item.clone( title = '[B]Búsquedas a través de Listas en Filmaffinity:[/B]', action = '', thumbnail=thumb_filmaffinity, text_color='violet' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='list_all', title= ' - Películas en Cartelera', url = 'https://www.filmaffinity.com/es/cat_new_th_es.html', thumbnail=config.get_thumb('novedades'), search_type = 'movie' ))

            itemlist.append(item.clone( title = ' - Películas y Series Novedades a la venta', channel='filmaffinitylists', action = 'list_all', url = 'https://www.filmaffinity.com/es/cat_new_sa_es.html', search_type = 'all', thumbnail=thumb_filmaffinity ))

            itemlist.append(item.clone( title = ' - Películas y Series Novedades en alquiler', channel='filmaffinitylists', action = 'list_all', url = 'https://www.filmaffinity.com/es/cat_new_re_es.html', search_type = 'all', thumbnail=thumb_filmaffinity ))

    return itemlist


def submnu_alls(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[B]PELÍCULAS Y/Ó SERIES[/B]', action = '', thumbnail=config.get_thumb('booklet'), text_color='goldenrod' ))

    cliente_torrent = config.get_setting('cliente_torrent', default='Seleccionar')

    if cliente_torrent == 'Seleccionar' or cliente_torrent == 'Ninguno':
        itemlist.append(item.clone( channel='actions', action='open_settings', title='[COLOR chocolate][B]Ajustes[/B][/COLOR] preferencias (categoría [COLOR blue][B]Torrents)[/B][/COLOR]' + ' [COLOR fuchsia][B]Motor:[/B][/COLOR][COLOR goldenrod][B] ' + cliente_torrent.capitalize() + '[/B][/COLOR]', folder=False, thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( title = '[B][I]Canales:[/I][/B]', action = '', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='tan' ))

    itemlist.append(item.clone( title = '   - Con temática Clásica', action = 'ch_groups', group = 'classic', extra = 'all' ))

    if config.get_setting('mnu_infantiles', default=True):
        itemlist.append(item.clone( title = '   - Con temática Infantil', action = 'ch_groups', group = 'kids', extra = 'all' ))

    itemlist.append(item.clone( title = '   - Con Rankings (Más vistas, Más valoradas, etc.)', action = 'ch_groups', group = 'rankings', extra = 'all' ))

    if config.get_setting('mnu_torrents', default=True):
        itemlist.append(item.clone( title = '   - Que pueden tener enlaces Torrents', context=context_torrents, thumbnail=config.get_thumb('torrents'), action = 'ch_groups', group = 'torrents', extra = 'torrents' ))

    if config.get_setting('mnu_idiomas', default=True):
        itemlist.append(item.clone( title = '   - Con Vídeos en Versión Original y/ó Subtitulada', action = 'ch_groups', group = 'vos', extra = 'all' ))

    itemlist.append(item.clone( title = '   - Con Vídeos en 4K', action = 'ch_groups', group = '4k', extra = 'all' ))

    itemlist.append(item.clone( title = '   - Con Vídeos en 3D', action = 'ch_groups', group = '3d', extra = 'all' ))

    if config.get_setting('search_extra_main', default=False):
        itemlist.append(item.clone( title = '[B]Búsquedas a través de Listas en TMDB:[/B]', action = '', thumbnail=thumb_tmdb, text_color='violet' ))

        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - Películas en Cartelera', extra='now_playing', thumbnail=config.get_thumb('novedades'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - Películas Más populares', extra='popular', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - Películas Más valoradas', extra='top_rated',thumbnail=config.get_thumb('bestmovies') , search_type = 'movie' ))
        itemlist.append(item.clone( channel='tmdblists', action='networks', title='   - Películas por productora', thumbnail=config.get_thumb('booklet'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='tmdblists', action='networks', title='   - Series por productora', thumbnail=config.get_thumb('booklet'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - Series Más populares', extra='popular', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - Series Más valoradas', extra='top_rated',thumbnail=config.get_thumb('besttvshows') , search_type = 'tvshow' ))

        itemlist.append(item.clone( title = '[B]Búsquedas a través de Listas en Filmaffinity:[/B]', action = '', thumbnail=thumb_filmaffinity, text_color='violet' ))

        itemlist.append(item.clone( channel='filmaffinitylists', action='list_all', title= ' - Películas en Cartelera', url = 'https://www.filmaffinity.com/es/cat_new_th_es.html', thumbnail=config.get_thumb('novedades'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_bestmovies', title='   - Películas Recomendadas', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='plataformas', title='   - Películas y Series por plataforma', thumbnail=config.get_thumb('booklet'), search_type = 'all' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_themes', title='   - Películas y Series por tema', thumbnail=config.get_thumb('listthemes'), search_type = 'all' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_oscars', title='   - Películas Premios Oscar', thumbnail=config.get_thumb('oscars'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_sagas', title='   - Películas Sagas y colecciones', thumbnail=config.get_thumb('bestsagas'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_besttvshows', title='   - Series Recomendadas', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_emmys', title='   - Series Premios Emmy', thumbnail=config.get_thumb('emmys'), origen='mnu_esp', search_type = 'tvshow' ))

    return itemlist


def submnu_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[B]PELÍCULAS[/B]', action = '', thumbnail=config.get_thumb('movie'), text_color='deepskyblue' ))

    itemlist.append(item.clone( title = '[B][I]Canales:[/I][/B]', action = '', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='tan' ))

    itemlist.append(item.clone( title = '   - Con temática Clásica', action = 'ch_groups', group = 'classic', extra = 'movies' ))

    if config.get_setting('mnu_infantiles', default=True):
        itemlist.append(item.clone( title = '   - Con temática Infantil', action = 'ch_groups', group = 'kids', extra = 'movies' ))

    if config.get_setting('mnu_idiomas', default=True):
        itemlist.append(item.clone( title = '   - Con Vídeos en Versión Original y/ó Subtitulada', action = 'ch_groups', group = 'vos', extra = 'movies' ))

    itemlist.append(item.clone( title = '   - Con Vídeos en 4K', action = 'ch_groups', group = '4k', extra = 'movies' ))

    itemlist.append(item.clone( title = '   - Con Vídeos en 3D', action = 'ch_groups', group = '3d', extra = 'movies' ))

    if config.get_setting('mnu_generos', default=True):
        itemlist.append(item.clone( title = '   - Con Géneros', action = 'ch_groups', group = 'genres', extra = 'movies' ))

    if config.get_setting('mnu_idiomas', default=True):
        itemlist.append(item.clone( title = '   - Con Idiomas', action = 'ch_groups', group = 'languages', extra = 'movies' ))

    itemlist.append(item.clone( title = '   - Con Años', action = 'ch_groups', group = 'years', extra = 'movies' ))
    itemlist.append(item.clone( title = '   - Con Épocas', action = 'ch_groups', group = 'epochs', extra = 'movies' ))
    itemlist.append(item.clone( title = '   - Con Calidades', action = 'ch_groups', group = 'qualityes', extra = 'movies' ))

    presentar = False
    if config.get_setting('channels_link_pyse', default=False): presentar = True
    elif config.get_setting('mnu_pelis', default=True): presentar = True

    if presentar:
        itemlist.append(item.clone( title = '   - Con Países', action = 'ch_groups', group = 'countries', extra = 'movies' ))

    if config.get_setting('search_extra_main', default=False):
        itemlist.append(item.clone( title = '[B]Búsquedas a través de Listas en TMDB:[/B]', action = '', thumbnail=thumb_tmdb, text_color='violet' ))

        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - En Cartelera', extra='now_playing', thumbnail=config.get_thumb('novedades'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - Más populares', extra='popular', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - Más valoradas', extra='top_rated', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='tmdblists', action='networks', title='   - Por productora', thumbnail=config.get_thumb('booklet'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='tmdblists', action='generos', title='   - Por género', thumbnail=config.get_thumb('listgenres'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='tmdblists', action='anios', title='   - Por año', thumbnail=config.get_thumb('listyears'), search_type = 'movie' ))

        itemlist.append(item.clone( title = '[B]Búsquedas a través de Listas en Filmaffinity:[/B]', action = '', thumbnail=thumb_filmaffinity, text_color='violet' ))

        itemlist.append(item.clone( channel='filmaffinitylists', action='list_all', title= ' - En Cartelera', url = 'https://www.filmaffinity.com/es/cat_new_th_es.html', thumbnail=config.get_thumb('novedades'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_bestmovies', title='   - Recomendadas', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='plataformas', title='   - Por plataforma', thumbnail=config.get_thumb('booklet'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_themes', title=' - Por tema', thumbnail = config.get_thumb('listthemes'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_oscars', title='   - Premios Oscar', thumbnail=config.get_thumb('oscars'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_sagas', title='   - Sagas y colecciones', thumbnail=config.get_thumb('bestsagas'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='generos', title='   - Por género', thumbnail=config.get_thumb('listgenres'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='paises', title='   - Por país', thumbnail=config.get_thumb('idiomas'), search_type = 'movie' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_years', title='   - Por año', thumbnail=config.get_thumb('listyears'), search_type = 'movie' ))

    return itemlist


def submnu_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[B]SERIES[/B]', action = '', thumbnail=config.get_thumb('tvshow'), text_color='hotpink' ))

    itemlist.append(item.clone( title = '[B][I]Canales:[/I][/B]', action = '', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='tan' ))

    itemlist.append(item.clone( title = '   - Con temática Clásica', action = 'ch_groups', group = 'classic', extra = 'tvshows' ))

    if config.get_setting('mnu_infantiles', default=True):
        itemlist.append(item.clone( title = '   - Con temática Infantil', action = 'ch_groups', group = 'kids', extra = 'tvshows' ))

    if config.get_setting('mnu_idiomas', default=True):
        itemlist.append(item.clone( title = '   - Con Vídeos en Versión Original y/ó Subtitulada', action = 'ch_groups', group = 'vos', extra = 'tvshows' ))

    if config.get_setting('mnu_generos', default=True):
        itemlist.append(item.clone( title = '   - Con Géneros', action = 'ch_groups', group = 'genres', extra = 'tvshows' ))

    if config.get_setting('mnu_novelas', default=True):
        itemlist.append(item.clone( title = '   - Con Novelas', action = 'ch_groups', group = 'tales', extra = 'tvshows' ))

    itemlist.append(item.clone( title = '   - Con Temas Bíblicos', action = 'ch_groups', group = 'bibles', extra = 'tvshows' ))

    itemlist.append(item.clone( title = '   - Con Años', action = 'ch_groups', group = 'years', extra = 'tvshows' ))

    presentar = False
    if config.get_setting('channels_link_pyse', default=False): presentar = True
    elif not config.get_setting('mnu_series', default=True): presentar = True

    if presentar:
        itemlist.append(item.clone( title = '   - Con Países', action = 'ch_groups', group = 'countries', extra = 'tvshows' ))

    if config.get_setting('search_extra_main', default=False):
        itemlist.append(item.clone( title = '[B]Búsquedas a través de Listas en TMDB:[/B]', action = '', thumbnail=thumb_tmdb, text_color='violet' ))

        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - En emisión', extra='on_the_air', thumbnail=thumb_tmdb, search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - Más populares', extra='popular', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='tmdblists', action='listado', title= '   - Más valoradas', extra='top_rated', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='tmdblists', action='networks', title='   - Por productora', thumbnail=config.get_thumb('booklet'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='tmdblists', action='generos', title='   - Por género', thumbnail = config.get_thumb('listgenres'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='tmdblists', action='anios', title='   - Por año', thumbnail = config.get_thumb('listyears'), search_type = 'tvshow' ))

        itemlist.append(item.clone( title = '[B]Búsquedas a través de Listas en Filmaffinity:[/B]', action = '', thumbnail=thumb_filmaffinity, text_color='violet' ))

        itemlist.append(item.clone( channel='filmaffinitylists', action='_besttvshows', title='   - Recomendadas', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_emmys', title='   - Premios Emmy', thumbnail=config.get_thumb('emmys'), origen='mnu_esp', search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='plataformas', title='   - Por plataforma', thumbnail=config.get_thumb('booklet'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_themes', title='   - Por tema', thumbnail = config.get_thumb('listthemes'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_genres', title='   - Por género', thumbnail = config.get_thumb('listgenres'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='paises', title='   - Por país', thumbnail=config.get_thumb('idiomas'), search_type = 'tvshow' ))
        itemlist.append(item.clone( channel='filmaffinitylists', action='_years', title='   - Por año', thumbnail = config.get_thumb('listyears'), search_type = 'tvshow' ))

    return itemlist


def submnu_docs(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[B]DOCUMENTALES[/B]', action = '', thumbnail=config.get_thumb('documentary'), text_color='cyan' ))

    itemlist.append(item.clone( title = '[B][I]Canales:[/I][/B]', action = '', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='tan' ))

    itemlist.append(item.clone( title = ' - [COLOR magenta][B]Todos los canales con temática [/COLOR][COLOR cyan]Documental[/B][/COLOR]', action = 'ch_groups', group = 'docs', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( title = ' - Solo los canales con contenido Exclusivo de [COLOR cyan][B]Documentales[/B][/COLOR]', action = 'ch_groups', group = 'documentaries', only = 'documentales', extra = 'documentaries' ))

    if config.get_setting('search_extra_main', default=False):
        itemlist.append(item.clone( title = '[B]Búsquedas a través de Listas en Filmaffinity:[/B]', action = '', thumbnail=config.get_thumb('booklet'), text_color='violet' ))

        itemlist.append(item.clone( channel='filmaffinitylists', action='_bestdocumentaries', title=' - Los Mejores', thumbnail=thumb_filmaffinity, search_type = 'all' ))

    return itemlist


def submnu_doramas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[B]DORAMAS[/B]', action = '', thumbnail=config.get_thumb('computer'), text_color='firebrick' ))

    itemlist.append(item.clone( title = '[B][I]Canales:[/I][/B]', action = '', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='tan' ))

    itemlist.append(item.clone( title = ' - [COLOR magenta][B]Todos los canales con contenido de [/COLOR][COLOR firebrick]Doramas[/B][/COLOR]', action = 'ch_groups', group = 'dorama', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( title = ' - Solo los canales con contenido Exclusivo de [COLOR firebrick][B]Doramas[/B][/COLOR]', action = 'ch_groups', group = 'dorama', only = 'doramas', search_special = 'dorama' ))

    return itemlist


def submnu_animes(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[B]ANIMES[/B]', action = '', thumbnail=config.get_thumb('anime'), text_color='springgreen' ))

    itemlist.append(item.clone( title = '[B][I]Canales:[/I][/B]', action = '', context=context_parental, thumbnail=config.get_thumb('stack'), text_color='tan' ))

    itemlist.append(item.clone( title = ' - [COLOR magenta][B]Todos los canales con contenido de [/COLOR][COLOR springgreen]Animes[/B][/COLOR]', action = 'ch_groups', group = 'anime', context=context_parental, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( title = ' - Solo los canales con contenido Exclusivo de [COLOR springgreen][B]Animes[/B][/COLOR]', action = 'ch_groups', group = 'anime', only = 'animes', search_special = 'anime', context=context_parental ))

    return itemlist


def submnu_adults(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[B]ADULTOS (+18)[/B]', action = '', thumbnail=config.get_thumb('adults'), text_color='orange' ))

    itemlist.append(item.clone( title = '[B][I]Canales:[/I][/B]', action = '', context=context_parental, thumbnail=config.get_thumb('stack'), text_color='tan' ))

    itemlist.append(item.clone( title = ' - [COLOR magenta][B]Todos los canales que pueden contener vídeos para [/COLOR][COLOR orange]Adultos[/B][/COLOR]', action = 'ch_groups', group = 'adults', context=context_parental, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( title = ' - Solo los canales con contenido Exclusivo de [COLOR orange][B]Adultos[/B][/COLOR]', action = 'ch_groups', group = 'adults', only = 'adults', context=context_parental ))

    return itemlist


def submnu_diversos(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[B]DIVERSOS[/B]', action = '', thumbnail=config.get_thumb('crossroads'), text_color='teal' ))

    itemlist.append(item.clone( title = '[B][I]Canales:[/I][/B]', action = '', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='tan' ))

    itemlist.append(item.clone( title = '   - Con Categorías', action = 'ch_groups', group = 'categories', extra = 'mixed', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( title = '   - Con Intérpretes', action = 'ch_groups', group = 'stars', extra = 'mixed', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( title = '   - Con Directores/as', action = 'ch_groups', group = 'directors', extra = 'mixed', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( title = '   - Con Productoras, Plataformas, y/ó Estudios', action = 'ch_groups', group = 'producers', extra = 'mixed', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( title = '   - Con Listas, Sagas, Colecciones, y/ó Otros', action = 'ch_groups', group = 'lists', extra = 'mixed', thumbnail=config.get_thumb('stack') ))

    if not config.get_setting('mnu_simple', default=False):
        if config.get_setting('search_extra_main', default=False):
            itemlist.append(item.clone( action='', title= '[B]Búsquedas por Título en TMDB:[/B]', folder=False, text_color='pink', thumbnail=thumb_tmdb ))

            itemlist.append(item.clone( channel='tmdblists', action='search', search_type='movie', title= ' - Buscar [COLOR deepskyblue]Película[/COLOR] ...', thumbnail = config.get_thumb('movie') ))

            itemlist.append(item.clone( channel='tmdblists', action='search', search_type='tvshow', title= ' - Buscar [COLOR hotpink]Serie[/COLOR] ...', thumbnail = config.get_thumb('tvshow') ))

            itemlist.append(item.clone( action='', title= '[B]Búsquedas por Título en Filmaffinity:[/B]', folder=False, text_color='pink', thumbnail=thumb_filmaffinity ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='listas', search_type='all', stype='title', title=' - Buscar [COLOR yellow]Película y/ó Serie[/COLOR] ...', thumbnail=config.get_thumb('search') ))

            itemlist.append(item.clone( action = '', title = '[B]Búsqueda a través de Personas en [COLOR violet]TMDB[/COLOR]:[/B]', thumbnail=thumb_tmdb, text_color='violet' ))

            itemlist.append(item.clone( channel='tmdblists', action='personas', search_type='cast', title='   - Buscar [COLOR aquamarine]intérprete[/COLOR] ...', thumbnail=config.get_thumb('search'), plot = 'Escribir el nombre de un actor o una actriz para listar todas las películas y series en las que ha intervenido.' ))

            itemlist.append(item.clone( channel='tmdblists', action='personas', search_type='crew', title='   - Buscar [COLOR springgreen]dirección[/COLOR] ...', thumbnail=config.get_thumb('search'), plot = 'Escribir el nombre de una persona para listar todas las películas y series que ha dirigido.' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado_personas', search_type='person', extra = 'popular', title=' - [COLOR limegreen]Más populares[/COLOR]', thumbnail=config.get_thumb('search') ))

            itemlist.append(item.clone( action = '', title = '[B]Búsquedas a través de Listas en TMDB:[/B]', thumbnail=thumb_tmdb, text_color='violet' ))

            itemlist.append(item.clone( channel='tmdblists', action='networks', title='   - Por productora', search_type = 'movie', thumbnail=config.get_thumb('booklet') ))

            itemlist.append(item.clone( title = '[B]Búsquedas a través de Listas en Filmaffinity:[/B]', action = '', thumbnail=thumb_filmaffinity, text_color='violet' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='plataformas', title='   - Por plataforma', search_type = 'all', thumbnail=config.get_thumb('booklet') ))
            itemlist.append(item.clone( channel='filmaffinitylists', action='_themes', title='   - Por tema', thumbnail=config.get_thumb('listthemes'), search_type = 'all' ))
            itemlist.append(item.clone( channel='filmaffinitylists', action='_sagas', title='   - Sagas y colecciones', thumbnail=config.get_thumb('bestsagas'), search_type = 'movie' ))

    return itemlist


def submnu_audios(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[B]AUDIOS EN LOS CANALES:[/B]', action = '', thumbnail=config.get_thumb('idiomas'), text_color='violet' ))

    itemlist.append(item.clone( channel='helper', action='show_play_parameters', title=' - Qué [COLOR chocolate][B]Ajustes[/B][/COLOR] tiene en preferencias [COLOR fuchsia][B]Play[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( title = ' - Audio [COLOR goldenrod][B]Múltiple[/B][/COLOR]', action = 'ch_groups', group = 'all', extra = 'mixed', thumbnail=config.get_thumb('stack'), langs = True ))
    itemlist.append(item.clone( title = ' - Audio solo en [COLOR chartreuse][B]Castellano[/B][/COLOR]', action = 'ch_groups', group = 'cast', extra = 'mixed', thumbnail=config.get_thumb('stack'), langs = True ))
    itemlist.append(item.clone( title = ' - Audio solo en [COLOR limegreen][B]Latino[/B][/COLOR]', action = 'ch_groups', group = 'lat', extra = 'mixed', thumbnail=config.get_thumb('stack'), langs = True ))
    itemlist.append(item.clone( title = ' - Audio solo en [COLOR red][B]Vose[/B][/COLOR]', action = 'ch_groups', group = 'vose', extra = 'mixed', thumbnail=config.get_thumb('stack'), langs = True ))
    itemlist.append(item.clone( title = ' - Audio solo en [COLOR indianred][B]Vo ó Vos[/B][/COLOR]', action = 'ch_groups', group = 'vo', extra = 'mixed', thumbnail=config.get_thumb('stack'), langs = True ))

    return itemlist


def ch_groups(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)
    descartar_anime = config.get_setting('descartar_anime', default=False)

    accion = 'mainlist'

    search_type = ''
    if item.group == 'news': accion = 'mainlist_pelis'
    elif item.group == 'lasts': accion = 'mainlist_series'

    elif item.group == 'classic':
         if item.extra == 'movies': search_type = 'movie'
         elif item.extra == 'tvshows': search_type = 'tvshow'

    elif item.group == 'kids':
         if item.extra == 'movies': search_type = 'movie'
         elif item.extra == 'tvshows': search_type = 'tvshow'

    elif item.group == 'genres' or item.group == 'generos':
         if item.extra == 'movies': search_type = 'movie'
         else: search_type = 'tvshow'

    elif item.group == 'languages':
         accion = 'idiomas'
         search_type = 'movie'

    elif item.group == 'years':
         if item.extra == 'movies':
            accion = 'anios'
            search_type = 'movie'
         else:
            accion = 'anios'
            search_type = 'tvshow'

    elif item.group == 'epochs':
         search_type = 'movie'

    elif item.group == 'countries':
         if item.extra == 'movies':
             accion = 'paises'
             search_type = 'movie'
         else:
             accion = 'mainlist_series'
             search_type = 'tvshow'

    elif item.group == 'qualityes':
         accion = 'calidades'
         search_type = 'movie'

    elif item.group == 'categories': accion = 'categorias'

    canales = []
    filtros = {}

    channels_list_status = config.get_setting('channels_list_status', default=0)
    if channels_list_status > 0:
        filtros['status'] = 0 if channels_list_status == 1 else 1

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0

    for ch in ch_list:
        if ch['status'] == -1: continue

        try: agrupaciones = ch['clusters']
        except: continue

        if config.get_setting('mnu_problematicos', default=False):
            if 'problematic' in ch['clusters']: continue

        if 'trailers' in ch['clusters']: continue

        if item.group == 'classic':
            if item.extra == 'movies':
                if not 'movie' in ch['categories']: continue

            elif item.extra == 'tvshows':
                if not 'tvshow' in ch['categories']: continue

            if not 'classic' in ch['clusters']: continue

        elif item.group == 'kids':
            if item.extra == 'movies':
                if not 'movie' in ch['categories']: continue

            elif item.extra == 'tvshows':
                if not 'tvshow' in ch['categories']: continue

            if not 'kids' in ch['clusters']: continue

        elif item.group == 'genres' or item.group == 'generos':
            if item.extra == 'movies':
                if not 'movie' in ch['categories']: continue
                if not 'géneros' in ch['notes']: continue

            elif item.extra == 'tvshows':
                if not 'tvshow' in ch['categories']: continue
                if not 'Géneros' in ch['notes']: continue

            search_types = ch['search_types']

            accion = 'generos'

            if item.group == 'generos': accion = 'mainlist'
            elif 'all' in search_types:
               if search_type == 'tvshow':
                   if not 'Géneros' in ch['notes']: continue
               elif not 'géneros' in ch['notes']: accion = 'mainlist'

        elif item.group == 'countries':
            if not 'countries' in ch['clusters']: continue

            search_types = ch['search_types']

            if item.extra == 'movies':
                if not 'movie' in search_types: continue
            else:
                if not 'tvshow' in search_types: continue

        elif item.group == 'cast':
            audios = ch['language']
            if not item.group in audios: continue

            if 'lat' in audios: continue
            elif 'vose' in audios: continue
            elif 'vo' in audios: continue
        elif item.group == 'lat':
            audios = ch['language']
            if not item.group in audios: continue

            if 'cast' in audios: continue
            elif 'vose' in audios: continue
            elif 'vo' in audios: continue
        elif item.group == 'vose':
            audios = ch['language']
            if not item.group in audios: continue

            if 'cast' in audios: continue
            elif 'lat' in audios: continue
            elif 'vo' in audios: continue
        elif item.group == 'vo':
            audios = ch['language']
            if not item.group in audios: continue

            if 'cast' in audios: continue
            elif 'lat' in audios: continue
            elif 'vose' in audios: continue

            if ch['searchable'] == False: # adultos
               if descartar_xxx: continue

        elif item.group == 'all':
            audios = ch['language']
            if len(audios) == 1: continue

        else:
           if not item.group in agrupaciones:
               if not item.group == 'documentaries': continue

           if item.extra == 'movies':
               if not 'movie' in ch['categories']: continue
           elif item.extra == 'tvshows':
               if not 'tvshow' in ch['categories']: continue

        if ch['searchable'] == False:
            if descartar_xxx:
                if 'adults' in agrupaciones:
                    if item.group == 'news': continue
                    elif item.group == 'rankings': continue
                    elif item.group == 'categories': continue
                    elif item.group == 'stars': continue
                    elif item.group == 'vose': continue
                    elif item.group == 'vo': continue
            else:
               if config.get_setting('mnu_simple', default=False):
                   if 'adults' in agrupaciones: continue

            if descartar_anime:
                if 'anime' in agrupaciones:
                   if item.group == 'anime': continue
                   elif item.group == 'vose': continue
                   elif item.group == 'vo': continue
            else:
               if config.get_setting('mnu_simple', default=False):
                   if 'anime' in agrupaciones: continue

            if not config.get_setting('mnu_doramas', default=True):
                if 'dorama' in ch['clusters']: continue

            if not config.get_setting('mnu_animes', default=True):
                if 'anime' in agrupaciones: continue

            if not config.get_setting('mnu_adultos', default=True):
                if 'adults' in agrupaciones: continue

        if config.get_setting('mnu_simple', default=False):
            if str(ch['search_types']) == "['documentary']": continue
            elif 'enlaces torrent exclusivamente' in ch['notes'].lower(): continue
            elif 'dedicada exclusivamente al dorama' in ch['notes'].lower(): continue

            elif 'anime' in agrupaciones: continue
            elif 'adults' in agrupaciones: continue

        if not config.get_setting('mnu_torrents', default=True):
            if 'enlaces torrent exclusivamente' in ch['notes'].lower(): continue

        action = accion

        if item.group == 'documentaries':
            if item.only == 'documentales':
                if not str(ch['categories']) == "['documentary']": continue

        elif item.group == 'dorama':
            if item.only == 'doramas':
                if 'dorama' in ch['clusters']:
                    if not 'dedicada exclusivamente al dorama' in ch['notes'].lower(): continue

        elif item.group == 'anime':
            if item.only == 'animes':
                if 'anime' in ch['clusters']:
                    if not 'dedicada exclusivamente al anime' in ch['notes'].lower(): continue

            if 'anime' in ch['notes'].lower(): action = 'mainlist_anime'
            else:
                 if ch['name'].startswith('Series'): action = 'mainlist_series'
                 else: action = 'mainlist_pelis'

        elif item.group == 'adults':
            if item.only == 'adults':
                if 'adults' in ch['clusters']:
                    if not '+18' in ch['notes']: continue

        context = []

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

        if 'proxies' in ch['notes'].lower():
            if config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s][B]Quitar Proxies del Canal[/B][/COLOR]' % color_list_proxies
                context.append({'title': tit, 'channel': item.channel, 'action': '_quitar_proxies'})

        if ch['searchable']:
            if not ch['status'] == -1:
                cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'

                if config.get_setting(cfg_searchable_channel, default=False):
                    tit = '[COLOR %s][B]Quitar Excluido Búsquedas[/B][/COLOR]' % color_adver
                    context.append({'title': tit, 'channel': item.channel, 'action': '_quitar_no_searchables'})
                else:
                    if config.get_setting('search_included_all', default=''):
                        search_included_all = config.get_setting('search_included_all')

                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_included_all):
                            tit = '[COLOR indianred][B]Quitar Búsquedas Solo en[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_included_del_one'})

                    if config.get_setting('search_excludes_all', default=''):
                        search_excludes_all = config.get_setting('search_excludes_all')

                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_all):
                            tit = '[COLOR indianred][B]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})


                    elif config.get_setting('search_excludes_movies', default=''):
                        search_excludes_movies = config.get_setting('search_excludes_movies')

                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_movies):
                            tit = '[B][COLOR deepskyblue]Películas [COLOR indianred]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})

                    elif config.get_setting('search_excludes_tvshows', default=''):
                        search_excludes_tvshows = config.get_setting('search_excludes_tvshows')

                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_tvshows):
                            tit = '[B][COLOR hotpink]Series [COLOR indianred]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})

                    elif config.get_setting('search_excludes_documentaries', default=''):
                        search_excludes_documentaries = config.get_setting('search_excludes_documentaries')

                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_documentaries):
                            tit = '[B][COLOR cyan]Documentales [COLOR indianred]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})

                    elif config.get_setting('search_excludes_torrents', default=''):
                        search_excludes_torrents = config.get_setting('search_excludes_torrents')

                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_torrents):
                            tit = '[B][COLOR blue]Torrents [COLOR indianred]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})

                    elif config.get_setting('search_excludes_mixed', default=''):
                        search_excludes_mixed = config.get_setting('search_excludes_mixed')

                        el_memorizado = "'" + ch['id'] + "'"
                        if el_memorizado in str(search_excludes_mixed):
                            tit = '[B][COLOR teal]Películas y/ó Series [COLOR indianred]Quitar Exclusión Búsquedas[/B][/COLOR]'
                            context.append({'title': tit, 'channel': 'submnuctext', 'action': '_channels_excluded_del'})

                    else:
                        tit = '[COLOR %s][B]Excluir en Búsquedas[/B][/COLOR]' % color_adver
                        context.append({'title': tit, 'channel': item.channel, 'action': '_poner_no_searchables'})

        if ch['status'] != 1:
            tit = '[COLOR %s][B]Marcar Canal como Preferido[/B][/COLOR]' % color_list_prefe
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 1})

        if ch['status'] != 0:
            if ch['status'] == 1:
                tit = '[COLOR %s][B]Des-Marcar Canal Preferido[/B][/COLOR]' % color_list_prefe
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            elif ch['status'] == -1:
                tit = '[COLOR %s][B]Des-Marcar Canal Desactivado[/B][/COLOR]' % color_list_inactive
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            else:
                tit = '[COLOR white][B]Marcar Canal como Activo[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})

        if ch['status'] != -1:
            tit = '[COLOR %s][B]Marcar Canal como Desactivado[/B][/COLOR]' % color_list_inactive
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': -1})

        cfg_domains = False

        if 'current' in ch['clusters']:
            cfg_domains = True

            tit = '[COLOR %s]Información Dominios[/COLOR]' % color_infor
            context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_domains'})

        tit = '[COLOR %s][B]Últimos Cambios Dominios[/B][/COLOR]' % color_exec
        context.append({'title': tit, 'channel': 'actions', 'action': 'show_latest_domains'})

        if cfg_domains:
            tit = '[COLOR yellowgreen][B]Dominio Vigente[/B][/COLOR]'
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominio_vigente'})

            if 'Dispone de varios posibles dominios' in ch['notes']:
                tit = '[COLOR powderblue][B]Configurar Dominio a usar[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_dominios'})

            tit = '[COLOR orange][B]Modificar dominio Memorizado[/B][/COLOR]'
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominio_memorizado'})

        if 'register' in ch['clusters']:
            cfg_user_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_username'
            cfg_pass_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_password'

            if not config.get_setting(cfg_user_channel, default='') or not config.get_setting(cfg_pass_channel, default=''):
                tit = '[COLOR green][B]Información Registrarse[/B][/COLOR]'
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
                       tit = '[COLOR teal][B]Cerrar Sesión[/B][/COLOR]'
                       context.append({'title': tit, 'channel': item.channel, 'action': '_credenciales'})

        if 'proxies' in ch['notes'].lower():
            if not config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s][B]Información Proxies[/B][/COLOR]' % color_infor
                context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

            tit = '[COLOR %s][B]Configurar Proxies a usar[/B][/COLOR]' % color_list_proxies
            context.append({'title': tit, 'channel': item.channel, 'action': '_proxies'})

        if 'notice' in ch['clusters']:
            tit = '[COLOR tan][B]Aviso Canal[/B][/COLOR]'
            context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_' + ch['id']})

        tit = '[COLOR darkorange][B]Test Web Canal[/B][/COLOR]'
        context.append({'title': tit, 'channel': item.channel, 'action': '_tests'})

        if cfg_domains:
            tit = '[COLOR %s]Ajustes categoría Dominios[/COLOR]' % color_exec
            context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

        color = color_list_prefe if ch['status'] == 1 else 'white' if ch['status'] == 0 else color_list_inactive

        plot = ''
        plot += '[' + ', '.join([config.get_localized_category(ct) for ct in ch['categories']]) + '][CR]'
        plot += '[' + ', '.join([idioma_canal(lg) for lg in ch['language']]) + ']'
        if ch['notes'] != '': plot += '[CR][CR]' + ch['notes']

        titulo = ch['name']

        if ch['status'] == -1:
            titulo += '[I][B][COLOR %s] (desactivado)[/COLOR][/I][/B]' % color_list_inactive
            if config.get_setting(cfg_proxies_channel, default=''): titulo += '[I][B][COLOR %s] (proxies)[/COLOR][/I][/B]' % color_list_proxies
        else:
            if ch['status'] == 1: titulo += '[I][B][COLOR indianred] (preferido)[/COLOR][/I][/B]'
            elif 'suggested' in ch['clusters']: titulo += '[I][B][COLOR olivedrab] (sugerido)[/COLOR][/I][/B]'

            if config.get_setting(cfg_proxies_channel, default=''):
                if ch['status'] == 1: titulo += '[I][B][COLOR %s] (proxies)[/COLOR][/I][/B]' % color_list_proxies
                else: color = color_list_proxies

        if 'register' in ch['clusters']:
            cfg_user_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_username'
            cfg_pass_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_password'
            if not config.get_setting(cfg_user_channel, default='') or not config.get_setting(cfg_pass_channel, default=''):
               titulo += '[I][B][COLOR teal] (cuenta)[/COLOR][/I][/B]'
            else:
               cfg_login_channel = 'channel_' + ch['id'] + '_' + ch['id'] + '_login'

               if config.get_setting(cfg_login_channel, default=False):
                   presentar = True
                   if 'dominios' in ch['notes'].lower():
                       cfg_dominio_channel = 'channel_' + ch['id'] + '_dominio'
                       if not config.get_setting(cfg_dominio_channel, default=''): presentar = False

                   if presentar: titulo += '[I][B][COLOR teal] (sesion)[/COLOR][/I][/B]'
               else: titulo += '[I][COLOR teal] (login)[/COLOR][/I]'

        if 'current' in ch['clusters']:
            cfg_current_channel = 'channel_' + ch['id'] + '_dominio'

            if config.get_setting(cfg_current_channel, default=False): titulo += '[I][B][COLOR green] (dominio)[/COLOR][/I][/B]'

        if not PY3:
            if 'mismatched' in ch['clusters']: titulo += '[I][B][COLOR coral] (Incompatible)[/COLOR][/I][/B]'

        if 'inestable' in ch['clusters']:
            if config.get_setting('mnu_simple', default=False): continue
            elif config.get_setting('channels_list_no_inestables', default=False): continue

            titulo += '[I][B][COLOR plum] (inestable)[/COLOR][/I][/B]'

        if 'problematic' in ch['clusters']:
            if config.get_setting('mnu_simple', default=False): continue
            elif config.get_setting('mnu_problematicos', default=False): continue
            elif config.get_setting('channels_list_no_problematicos', default=False): continue

            titulo += '[I][B][COLOR darkgoldenrod] (problemático)[/COLOR][/I][/B]'

        if con_incidencias:
           if ch['name'] in str(con_incidencias): titulo += '[I][B][COLOR tan] (incidencia)[/COLOR][/I][/B]'

        if no_accesibles:
           if ch['name'] in str(no_accesibles): titulo += '[I][B][COLOR tan] (no accesible)[/COLOR][/I][/B]'

        if ch['searchable']:
            if not ch['status'] == -1:
                cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'

                if config.get_setting(cfg_searchable_channel, default=False): titulo += '[I][B][COLOR yellowgreen] (no búsquedas)[/COLOR][/I][/B]'

        if not item.langs:
            if not config.get_setting('mnu_adultos', default=True):
                if '+18' in ch['notes']: continue

            if '+18' in ch['notes']: titulo += '[B][I][COLOR orange] (+18)[/COLOR][/I][/B]'

        else:
            if not config.get_setting('mnu_adultos', default=True):
                if '+18' in ch['notes']: continue

            if 'movie' in ch['categories']:
                if "tvshow" in ch['categories']:
                    titulo += '[B][I][COLOR deepskyblue] películas[/COLOR] [COLOR hotpink]series[/COLOR][/I][/B]'
                    if 'tales' in ch['clusters']: titulo += '[B][I][COLOR limegreen] novelas[/COLOR][/I][/B]'
                else:
                    if '+18' in ch['notes']: titulo += '[B][I][COLOR orange] +18[/COLOR][/I][/B]'
                    else: titulo += '[B][I][COLOR deepskyblue] películas[/COLOR][/I][/B]'
            else:
                if "tvshow" in ch['categories']:
                    titulo += '[B][I][COLOR hotpink] series[/COLOR][/I][/B]'
                    if 'tales' in ch['clusters']: titulo += '[B][I][COLOR limegreen] novelas[/COLOR][/I][/B]'
                elif "documentary" in ch['categories']: titulo += '[B][I][COLOR cyan] documentales[/COLOR][/I][/B]'

            langs = str(ch['language'])
            langs = langs.replace('[', '').replace(']', '').replace('cast', 'esp').replace("'", '').strip()
            langs = langs.replace('esp', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'Vo').replace('vos', 'Vos')

            titulo += ' [COLOR coral][B][I]' + str(langs) + '[/I][/B][/COLOR]'

        i =+ 1

        itemlist.append(Item( channel=ch['id'], action=accion, title=titulo, context=context, text_color=color, plot=plot, extra=item.extra, sort='D', thumbnail=ch['thumbnail'], category=ch['name'], search_type=search_type ))

        canales.append(ch['id'])

    if len(itemlist) == 0 or i == 0:
        itemlist.append(item.clone( channel='filters', action='channels_status', title='[B]Opción Sin canales[/B]', sort = 'D', text_color=color_list_prefe, folder=False, des_rea=False, thumbnail=config.get_thumb('stack') ))

    if itemlist:
        buscar_only_group = True

        if item.group == 'adults':
            buscar_only_group = False
	
            itemlist.append(item.clone( action='', title = '[COLOR goldenrod][B]ADULTOS[/B][/COLOR]', sort = 'A' ))

            if not config.get_setting('adults_password'):
                itemlist.append(item.clone( channel='helper', action='show_help_adults', title='[COLOR green][B]Información [COLOR yellow]Parental[/B][/COLOR]', sort = 'A', thumbnail=config.get_thumb('news') ))
                itemlist.append(item.clone( channel='actions', action='adults_password', title= '[COLOR yellow][B]Establecer[/B][/COLOR] un PIN Parental', sort = 'A', thumbnail=config.get_thumb('pencil') ))
            else:
                itemlist.append(item.clone( channel='helper', action='show_pin_parental', title= '[COLOR springgreen][B]Ver[/B][/COLOR] el PIN Parental', sort = 'A', thumbnail=config.get_thumb('pencil') ))
                itemlist.append(item.clone( channel='actions', action='adults_password_del', title= '[COLOR red][B]Eliminar[/B][/COLOR] PIN parental', sort = 'A', erase = True, folder=False, thumbnail=config.get_thumb('pencil') ))

        if buscar_only_group:
            if len(itemlist) > 0:
                search_type = 'all'
                if item.extra == 'documentaries': search_type = 'documentary'

                tipo = '[COLOR chartreuse]Título[/COLOR]'
                if item.group == 'docs': tipo = '[COLOR cyan]Documental[/COLOR]'
                elif item.group == 'kids': tipo = '[COLOR lightyellow]Infantil[/COLOR]'
                elif item.group == 'tales': tipo = '[COLOR limegreen]Novela[/COLOR]'
                elif item.group == 'torrents': tipo = '[COLOR blue]Torrent[/COLOR]'
                elif item.group == 'dorama': tipo = '[COLOR firebrick]Dorama[/COLOR]'
                elif item.group == 'anime': tipo = '[COLOR springgreen]Anime[/COLOR]'
                elif item.group == 'adults': tipo = '[COLOR orange]+18[/COLOR]'

                grupo = ''
                if item.group == 'all': grupo = 'Audio Múltiple'
                elif item.group == 'cast': grupo = 'Castellano'
                elif item.group == 'lat': grupo = 'Latino'
                elif item.group == 'vose': grupo = 'Vose'
                elif item.group == 'vo': grupo = 'Vo'
                elif item.group == 'vos': grupo = 'Vos'
                elif item.group == 'news': grupo = 'Novedades Películas'
                elif item.group == 'lasts': grupo = 'Novedades Series'
                elif item.group == 'classic': grupo = 'Clásicos'
                elif item.group == 'rankings': grupo = 'Rankings'
                elif item.group == '4k': grupo = '4K'
                elif item.group == '3d': grupo = '3D'
                elif item.group == 'genres': grupo = 'Géneros'
                elif item.group == 'languages': grupo = 'Idiomas'
                elif item.group == 'years': grupo = 'Años'
                elif item.group == 'epochs': grupo = 'Épocas'
                elif item.group == 'qualityes': grupo = 'Calidades'
                elif item.group == 'countries': grupo = 'Países'
                elif item.group == 'categories': grupo = 'Categorías'
                elif item.group == 'stars': grupo = 'Intérpretes'
                elif item.group == 'directors': grupo = 'Directores/as'
                elif item.group == 'producers': grupo = 'Productoras'
                elif item.group == 'lists': grupo = 'Diversos'

                if grupo:
                    itemlist.append(item.clone( action='', title = '[COLOR goldenrod][B]' + grupo.upper() + '[/B][/COLOR]', sort = 'A' ))

                    grupo = ''
                else:
                    if not tipo == '[COLOR chartreuse]Título[/COLOR]':
                        cab = ''
                        if item.group == 'docs': cab = 'Documentales'
                        elif item.group == 'kids': cab = 'Infantiles'
                        elif item.group == 'tales': cab = 'Novelas'
                        elif item.group == 'torrents': cab = 'Torrents'
                        elif item.group == 'dorama': cab = 'Doramas'
                        elif item.group == 'anime': cab = 'Animes'
                        elif item.group == 'adults': cab = 'Adultos (+18)'

                        if cab:
                            itemlist.append(item.clone( action='', title = '[COLOR goldenrod][B]' + cab.upper() + '[/B][/COLOR]', sort = 'A' ))

                            if cab == 'Animes':
                                if not config.get_setting('adults_password'):
                                    itemlist.append(item.clone( channel='helper', action='show_help_adults', title='[COLOR green][B]Información [COLOR yellow]Parental[/B][/COLOR]', sort = 'A', thumbnail=config.get_thumb('news') ))
                                    itemlist.append(item.clone( channel='actions', action='adults_password', title= '[COLOR yellow][B]Establecer[/B][/COLOR] un PIN Parental', sort = 'A', thumbnail=config.get_thumb('pencil') ))
                                else:
                                    itemlist.append(item.clone( channel='helper', action='show_pin_parental', title= '[COLOR springgreen][B]Ver[/B][/COLOR] el PIN Parental', sort = 'A', thumbnail=config.get_thumb('pencil') ))
                                    itemlist.append(item.clone( channel='actions', action='adults_password_del', title= '[COLOR red][B]Eliminar[/B][/COLOR] PIN parental', sort = 'A', erase = True, folder=False, thumbnail=config.get_thumb('pencil') ))

                if config.get_setting('mnu_search_proxy_channels', default=False):
                    itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels, only_options_proxies = True, sort = 'A', thumbnail=config.get_thumb('flame'), text_color='red' ))

                if config.get_setting('sub_mnu_cfg_search', default=True):
                    itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title= '[B]Personalizar búsquedas[/B]', context=context_cfg_search, extra = item.extra, sort = 'A', thumbnail=config.get_thumb('help'), text_color='moccasin' ))

                itemlist.append(Item( channel='search', action='search', search_type=search_type, title='[B]Buscar ' + tipo + ' ... [COLOR gold](solo en los canales de esta Lista ' + grupo + '[/B][COLOR gold])',
	                                  context=context_buscar, only_channels_group = canales, group = item.group, only = item.only, search_special = item.search_special, sort = 'B', thumbnail=config.get_thumb('search'), text_color='yellow' ))

                itemlist.append(item.clone( title = '[B][I]- Canales:[/I][/B]', action = '', sort = 'C', context=context_usual, thumbnail=config.get_thumb('stack'), text_color='tan' ))

    return sorted(itemlist, key=lambda it: it.sort)


def ch_generos(item):
    return ch_groups(item)


def idioma_canal(lang):
    idiomas = { 'cast': 'Castellano', 'lat': 'Latino', 'eng': 'Inglés', 'pt': 'Portugués', 'vo': 'Vo', 'vose': 'Vose', 'vos': 'Vos', 'cat': 'Català' }
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
