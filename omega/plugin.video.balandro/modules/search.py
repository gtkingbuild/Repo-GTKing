# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3: PY3 = True
else: PY3 = False


import os, time

from threading import Thread

from platformcode import config, logger, platformtools
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


no_results_proxies = config.get_setting('search_no_results_proxies', default=True)
no_results = config.get_setting('search_no_results', default=False)


context_cfg_search = []

tit = '[COLOR tan][B]Preferencias Menús[/B][/COLOR]'
context_cfg_search.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR %s]Ajustes categoría Menú y Buscar[/COLOR]' % color_exec
context_cfg_search.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


def mainlist(item):
    logger.info()
    itemlist = []

    thumb_filmaffinity = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'filmaffinity.jpg')
    thumb_tmdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'tmdb.jpg')

    item.category = 'Buscar'

    itemlist.append(item.clone( action='', title='[B]BUSCAR:[/B]', folder=False, text_color='yellow' ))

    itemlist.append(item.clone( action='show_help', title='[COLOR green][B]Información [COLOR yellow]Búsquedas[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( channel='helper', action='show_help_audios', title= '[COLOR green][B]Información[/B][/COLOR] [COLOR cyan][B]Idiomas[/B][/COLOR] en los Audios de los Vídeos', thumbnail=config.get_thumb('news') ))

    if config.get_setting('search_extra_main', default=False):
        itemlist.append(item.clone( action='', title= '[B]Búsquedas por Título en TMDB:[/B]', folder=False, text_color='violet', thumbnail=thumb_tmdb ))

        itemlist.append(item.clone( channel='tmdblists', action='search', search_type='movie', title= ' - Buscar [COLOR deepskyblue]Película[/COLOR] ...', thumbnail=config.get_thumb('movie'), plot = 'Indicar el título de una película para buscarla en The Movie Database' ))

        itemlist.append(item.clone( channel='tmdblists', action='search', search_type='tvshow', title= ' - Buscar [COLOR hotpink]Serie[/COLOR] ...', thumbnail=config.get_thumb('tvshow'), plot = 'Indicar el título de una serie para buscarla en The Movie Database' ))

        itemlist.append(item.clone( action='', title= '[B]Búsquedas por Título en Filmaffinity:[/B]', folder=False, text_color='violet', thumbnail=thumb_filmaffinity ))

        itemlist.append(item.clone( channel='filmaffinitylists', action='listas', search_type='all', stype='title', title=' - Buscar [COLOR yellow]Película y/ó Serie[/COLOR] ...', thumbnail=config.get_thumb('search'), plot = 'Indicar el título de una película ó serie para buscarla en Filmaffinity' ))

        if not config.get_setting('mnu_simple', default=False):
            if config.get_setting('mnu_documentales', default=True):
                itemlist.append(item.clone( channel='filmaffinitylists', action='listas', search_type='documentary', stype='documentary', title=' - Buscar [COLOR cyan]Documental[/COLOR] ...', thumbnail=config.get_thumb('documentary'), plot = 'Indicar el título de un documental para buscarlo en Filmaffinity' ))

    titulo = '[B]Búsquedas por Titulo:[/B]'
    if config.get_setting('search_extra_main', default=False): titulo = '[B]Búsquedas por Título en los Canales:[/B]'

    itemlist.append(item.clone( action='', title= titulo, folder=False, text_color='chartreuse', thumbnail=config.get_thumb('stack') ))

    if config.get_setting('search_extra_trailers', default=False):
         itemlist.append(item.clone( channel='trailers', action='search', title= ' - Buscar [COLOR darkgoldenrod]Tráiler[/COLOR]', thumbnail=config.get_thumb('trailers'), plot = 'Indicar el título de una película para buscar su tráiler' ))

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action='search', search_type='all', title= ' - Buscar [COLOR yellow]Película y/ó Serie[/COLOR] ...', plot = 'Indicar el título para Buscarlo indistintamente en películas y/ó series en todos los canales' ))

    if not config.get_setting('mnu_simple', default=False):
        if config.get_setting('mnu_pelis', default=True):
            itemlist.append(item.clone( action='search', search_type='movie', title= ' - Buscar [COLOR deepskyblue]Película[/COLOR] ...', thumbnail=config.get_thumb('movie'), plot = 'Indicar el título de una película para buscarla en los canales de películas' ))

        if config.get_setting('mnu_series', default=True):
            itemlist.append(item.clone( action='search', search_type='tvshow', title= ' - Buscar [COLOR hotpink]Serie[/COLOR] ...', thumbnail=config.get_thumb('tvshow'), plot = 'Indicar el título de una serie para buscarla en los canales de series' ))

        if config.get_setting('mnu_documentales', default=True):
            itemlist.append(item.clone( action='search', search_type='documentary', title= ' - Buscar [COLOR cyan]Documental[/COLOR] ...', thumbnail=config.get_thumb('documentary'), plot = 'Indicar el título de un documental para buscarlo en los canales de documentales' ))

        if config.get_setting('mnu_doramas', default=True):
            itemlist.append(item.clone( action='search', search_type='all', title= ' - Buscar [COLOR firebrick]Dorama[/COLOR] ...',  thumbnail=config.get_thumb('computer'), search_special = 'dorama', plot = 'Indicar el título de un dorama para buscarlo Solo en los canales exlusivos de Doramas' ))

        if config.get_setting('mnu_animes', default=True):
            if not config.get_setting('descartar_anime', default=True):
               itemlist.append(item.clone( action='search', search_type='all', title= ' - Buscar [COLOR springgreen]Anime[/COLOR] ...', thumbnail=config.get_thumb('anime'), search_special = 'anime', plot = 'Indicar el título de un anime para buscarlo Solo en los canales exlusivos de Animes' ))

    if config.get_setting('search_extra_main', default=False):
        itemlist.append(item.clone( action='', title= '[B]Búsquedas Especiales:[/B]', folder=False, text_color='yellowgreen' ))

        itemlist.append(item.clone( channel='tmdblists', action='mainlist', title= ' - Búsquedas y listas en [COLOR violet]TMDB[/COLOR]', thumbnail=thumb_tmdb, plot = 'Buscar personas y ver listas de películas y series de la base de datos de The Movie Database' ))

        itemlist.append(item.clone( channel='filmaffinitylists', action='mainlist', title= ' - Búsquedas y listas en [COLOR violet]Filmaffinity[/COLOR]', thumbnail=thumb_filmaffinity, plot = 'Buscar personas y ver listas de películas, series ó documentales de Filmaffinity' ))

    if config.get_setting('search_extra_proxies', default=True):
        itemlist.append(item.clone( action='', title= '[B]Búsquedas en canales con Proxies:[/B]', folder=False, thumbnail=config.get_thumb('stack'), text_color='red' ))

        itemlist.append(item.clone( channel='helper', action='show_help_proxies', title= ' - [COLOR green][B]Información[/B][/COLOR] Uso de proxies', thumbnail=config.get_thumb('news') ))
        itemlist.append(item.clone( channel='helper', action='show_help_providers', title= ' - [COLOR green][B]Información[/B][/COLOR] Proveedores de proxies', thumbnail=config.get_thumb('news') ))
        itemlist.append(item.clone( channel='helper', action='show_help_providers2', title= ' - [COLOR green][B]Información[/B][/COLOR] Lista [COLOR aqua][B]Ampliada[/B][/COLOR] Proveedores de proxies', thumbnail=config.get_thumb('news') ))
        itemlist.append(item.clone( channel='helper', action='show_help_recommended', title= ' - Qué [COLOR green][B]Proveedores[/B][/COLOR] de proxies están [COLOR lime][B]Recomendados[/B][/COLOR]', thumbnail=config.get_thumb('news') ))

        itemlist.append(item.clone( channel='filters', action='with_proxies', title=  ' - Qué canales pueden usar [COLOR red][B]Proxies[/B][/COLOR]', thumbnail=config.get_thumb('stack'), new_proxies=True ))

        if config.get_setting('memorize_channels_proxies', default=True):
            itemlist.append(item.clone( channel='filters', action='with_proxies', title=  ' - Qué [COLOR red][B]Canales[/B][/COLOR] tiene con proxies Memorizados', thumbnail=config.get_thumb('stack'), new_proxies=True, memo_proxies=True, test_proxies=True ))

        itemlist.append(item.clone( channel='actions', title= ' - Quitar los proxies en los canales [COLOR red][B](que los Tengan)[/B][/COLOR]', action = 'manto_proxies', thumbnail=config.get_thumb('flame') ))

        itemlist.append(item.clone( channel='proxysearch', title =  ' - Configurar proxies a usar [COLOR plum][B](en los canales que los Necesiten)[/B][/COLOR]', action = 'proxysearch_all', thumbnail=config.get_thumb('flame') ))

        if config.get_setting('proxysearch_excludes', default=''):
            itemlist.append(item.clone( channel='proxysearch', title =  ' - Anular los canales excluidos de Configurar proxies a usar', action = 'channels_proxysearch_del', thumbnail=config.get_thumb('flame'), text_color='coral' ))

    if config.get_setting('sub_mnu_cfg_search', default=True):
        itemlist.append(item.clone( action='', title= '[B]Personalización búsquedas:[/B]', folder=False, thumbnail=config.get_thumb('help'), text_color='moccasin' ))

        itemlist.append(item.clone( action='show_help_parameters', title=' - Qué [COLOR chocolate]Ajustes[/COLOR] tiene en preferencias para las búsquedas', thumbnail=config.get_thumb('news') ))

        itemlist.append(item.clone( channel='filters', action='no_actives', title= ' - Qué canales [COLOR goldenrod][B]Nunca[/B][/COLOR] intervendrán en las búsquedas', no_searchables = True, thumbnail=config.get_thumb('stack') ))

        itemlist.append(item.clone( channel='filters', action='no_actives', title= ' - Qué canales no intervienen en las búsquedas están [COLOR gray][B]Desactivados[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

        itemlist.append(item.clone( channel='filters', action='channels_status', title= ' - Personalizar [COLOR gold]Canales[/COLOR] (Desactivar ó Re-activar)', des_rea = True, thumbnail=config.get_thumb('stack') ))

        itemlist.append(item.clone( channel='filters', action='only_prefered', title= ' - Qué canales tiene marcados como [COLOR gold]Preferidos[/COLOR]', thumbnail=config.get_thumb('stack') ))

        itemlist.append(item.clone( channel='filters', action='channels_status', title= ' - Personalizar canales [COLOR gold]Preferidos[/COLOR] (Marcar ó Des-marcar)', des_rea = False, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='', title= '[B]Personalizaciones especiales:[/B]', folder=False, thumbnail=config.get_thumb('help'), text_color='yellow' ))

    if config.get_setting('search_show_last', default=True):
        itemlist.append(item.clone( channel='actions', action = 'manto_textos', title= ' - Quitar los [COLOR coral][B]Textos[/B][/COLOR] Memorizados de las búsquedas', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(item.clone( channel='filters', action = 'mainlist2', title = ' - [COLOR greenyellow][B]Efectuar búsquedas [COLOR gold](solo en determinados canales)[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='filters', action = 'mainlist', title = ' - [COLOR cyan][B]Excluir canales de las búsquedas[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='', title= '[B]Ajustes:[/B]', thumbnail=config.get_thumb('help'), folder=False, text_color='goldenrod' ))

    itemlist.append(item.clone( channel='actions', title= ' - [COLOR chocolate]Ajustes[/COLOR] categorías ([COLOR red][B]Proxies[/B][/COLOR] y [COLOR yellow][B]Buscar[/B][/COLOR])', action = 'open_settings', thumbnail=config.get_thumb('settings') ))

    return itemlist


def show_help_parameters(item):
    if config.get_setting('mnu_simple', default=False):
        txt = '[CR] - Opera con el Menú [B][COLOR crimson]SIMPLIFICADO[/COLOR][/B][CR]'
        txt += '    - No Se Buscará en los canales [B][I][COLOR plum]Inestables[/COLOR][/I][/B][CR]'
        txt += '    - No Se Buscará en los canales [B][I][COLOR darkgoldenrod]Problemáticos[/COLOR][/I][/B][CR][CR]'

    else: txt = 'Los canales que tenga marcados como [B][COLOR cyan]Desactivados[/COLOR][/B] nunca intervendrán en las búsquedas[CR][CR]'

    txt += ' - [B][COLOR gold]Canales[/COLOR][/B] que nunca intervienen en las busquedas:'
    txt += '[CR][COLOR darkorange][B]    CineDeAntes,  CineLibreOnline,  CineMatteFlix,  Frozenlayer,'
    txt += '[CR]    SeoDiv,  SeriesBiblicas,  SigloXX,  Trailers,  TvSeries,  YouTubeDocs[/B][/COLOR]'

    if not config.get_setting('mnu_documentales', default=True): txt += '[CR][CR] - Los canales de [B][COLOR cyan]Documentales[/COLOR][/B] jamás intervendrán en las busquedas'

    txt += '[CR][CR] - Qué canales Nunca intervendrán en las busquedas de [COLOR gold][B]Peliculas, Series y/ó Documentales[/B][/COLOR]:'

    if config.get_setting('mnu_doramas', default=True): txt += '[CR]   - Los canales de [B][COLOR firebrick]Doramas[/COLOR][/B]'

    if config.get_setting('mnu_animes', default=True): txt += '[CR]   - Los canales de [B][COLOR springgreen]Animes[/COLOR][/B]'

    if config.get_setting('mnu_adultos', default=True): txt += '[CR]   - Los canales de [B][COLOR orange]Adultos[/COLOR][/B]'

    txt += '[CR][CR] - [COLOR goldenrod][B]Procesos[/COLOR][/B]:'

    txt += '[CR]   - Cuantos Resultados se previsualizarán por canal: [COLOR coral][B]' + str(config.get_setting('search_limit_by_channel', default=2)) + '[/COLOR][/B]'

    if config.get_setting('search_only_prefered', default=False): txt += '[CR]   - Tiene Activado efectuar búsquedas solo en los canales [B][COLOR gold]Preferidos[/COLOR][/B]'

    if config.get_setting('search_only_suggesteds', default=False): txt += '[CR]   - Tiene Activado efectuar búsquedas solo en los canales [B][COLOR moccasin]Sugeridos[/COLOR][/B]'

    if config.get_setting('search_no_proxies', default=False): txt += '[CR]   - Tiene Activado descartar búsquedas en los canales con [B][COLOR red]Proxies informados[/COLOR][/B]'

    if config.get_setting('search_con_torrents', default=False): txt += '[CR]   - Tiene Activado efectuar las búsquedas solo en los canales que pueden contener archivos [B][COLOR blue]Torrent[/COLOR][/B]'

    if config.get_setting('search_no_torrents', default=False): txt += '[CR]   - Tiene Activado descartar en las búsquedas los canales que pueden contener archivos [B][COLOR blue]Torrent[/COLOR][/B]'

    if config.get_setting('search_no_exclusively_torrents', default=False): txt += '[CR]   - Tiene Activado descartar en las búsquedas los canales con enlaces exclusivamente [B][COLOR blue]Torrent[/COLOR][/B]'

    if config.get_setting('search_no_notices', default=False): txt += '[CR]   - Tiene Activado descartar búsquedas en los canales con [COLOR green][B]Aviso[/COLOR][COLOR red] CloudFlare [COLOR orangered]Protection[/B][/COLOR]'

    if config.get_setting('search_no_inestables', default=False): txt += '[CR]   - Tiene Activado descartar búsquedas en los canales con [B][COLOR plum]Inestables[/COLOR][/B]'

    if config.get_setting('search_no_problematicos', default=False): txt += '[CR]   - Tiene Ativado descartar búsquedas en los canales que sean [B][COLOR darkgoldenrod]Problemáticos[/COLOR][/B]'

    txt += '[CR]   - Añadir acceso al detalle de Personalizar Próximas Búsquedas:'

    if config.get_setting('sub_mnu_cfg_prox_search', default=True): txt += ' [COLOR coral][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR coral][B] Des-Activado[/B][/COLOR]'

    txt += '[CR]   - Menú contextual para Buscar Exacto ó Parecido en los resultados de las Búsquedas:'

    if config.get_setting('search_dialog', default=True): txt += ' [COLOR coral][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR coral][B] Des-Activado[/B][/COLOR]'

    txt += '[CR]   - Notificar en qué canales No han funcionado los Proxies:'

    if config.get_setting('search_no_work_proxies', default=False): txt += ' [COLOR coral][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR coral][B] Des-Activado[/B][/COLOR]'

    txt += '[CR]   - Presentar en qué canales deberá configurar Nuevamente Proxies:'

    if config.get_setting('search_no_results_proxies', default=True): txt += ' [COLOR coral][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR coral][B] Des-Activado[/B][/COLOR]'

    txt += '[CR]   - Presentar los canales Sin Resultados:'

    if config.get_setting('search_no_results', default=False): txt += ' [COLOR coral][B] Activado[/B][/COLOR]'
    else: txt += ' [COLOR coral][B] Des-Activado[/B][/COLOR]'

    if config.get_setting('search_no_channels', default=False): txt += '[CR]    - Tiene Activado notificar en las búsquedas los canales [B][COLOR yellowgreen]Ignorados[/COLOR][/B]'

    if not config.get_setting('search_multithread', default=True): txt += '[CR]    - Tiene Des-Activada la opción [B][COLOR yellowgreen]Multithread[/COLOR][/B]'

    if config.get_setting('search_included_all', default=''):
        incluidos = config.get_setting('search_included_all', default='')
        if incluidos:
            txt += '[CR]   - [COLOR yellow][B]Búsquedas [COLOR greenyellow][B]Solo Determinados canales[/B][/COLOR] incluidos en [B][COLOR green]Todos[/COLOR][/B]:'
            incluidos = scrapertools.find_multiple_matches(incluidos, "'(.*?)'")

            for incluido in incluidos:
                incluido = incluido.capitalize().strip()
                txt += '[CR]     [COLOR violet][B] ' + incluido + '[/B][/COLOR]'

    filtros = {'searchable': True}

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if ch_list:
        txt_ch = ''

        for ch in ch_list:
            if not ch['status'] == -1: continue

            txt_ch += '[CR]   [COLOR gray]%s[/COLOR]' % ch['name']

        if txt_ch: txt += '[CR][CR] - [COLOR gold]Desactivados:[/COLOR]  %s' % str(txt_ch) 

    filtros = {'searchable': True}
    opciones = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if ch_list:
       txt_ch = ''

       for ch in ch_list:
           cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'

           if not config.get_setting(cfg_searchable_channel, default=False): continue

           txt_ch += '[CR]   [COLOR gold]%s[/COLOR]' % ch['name']

       if txt_ch: txt += '[CR][CR] - [COLOR goldenrod][B]Canales excluidos[B][/COLOR]:  %s' % str(txt_ch)

    if config.get_setting('search_excludes_movies', default=''):
        excluidos = config.get_setting('search_excludes_movies', default='')
        if excluidos:
            txt += '[CR][CR] - [COLOR goldenrod][B]Canales excluidos en las búsquedas de [COLOR deepskyblue]Películas[/COLOR][/B]:'
            excluidos = scrapertools.find_multiple_matches(excluidos, "'(.*?)'")

            for excluido in excluidos:
                excluido = excluido.capitalize().strip()
                txt += '[CR]   [COLOR gold][B] ' + excluido + '[/B][/COLOR]'

    if config.get_setting('search_excludes_tvshows', default=''):
        excluidos = config.get_setting('search_excludes_tvshows', default='')
        if excluidos:
            txt += '[CR][CR] - [COLOR goldenrod][B]Canales excluidos en las búsquedas de [COLOR hotpink]Series[/COLOR][/B]:'
            excluidos = scrapertools.find_multiple_matches(excluidos, "'(.*?)'")

            for excluido in excluidos:
                excluido = excluido.capitalize().strip()
                txt += '[CR]   [COLOR gold][B] ' + excluido + '[/B][/COLOR]'

    if config.get_setting('search_excludes_documentaries', default=''):
        excluidos = config.get_setting('search_excludes_documentaries', default='')
        if excluidos:
            txt += '[CR][CR] - [COLOR goldenrod][B]Canales excluidos en las búsquedas de [COLOR cyan]Documentales[/COLOR][/B]:'
            excluidos = scrapertools.find_multiple_matches(excluidos, "'(.*?)'")

            for excluido in excluidos:
                excluido = excluido.capitalize().strip()
                txt += '[CR]   [COLOR gold][B] ' + excluido + '[/B][/COLOR]'

    if config.get_setting('search_excludes_torrents', default=''):
        excluidos = config.get_setting('search_excludes_torrents', default='')
        if excluidos:
            txt += '[CR][CR] - [COLOR goldenrod][B]Canales excluidos en las búsquedas de [COLOR blue]Torrents[/COLOR][/B]:'
            excluidos = scrapertools.find_multiple_matches(excluidos, "'(.*?)'")

            for excluido in excluidos:
                excluido = excluido.capitalize().strip()
                txt += '[CR]   [COLOR gold][B] ' + excluido + '[/B][/COLOR]'

    if config.get_setting('search_excludes_mixed', default=''):
        excluidos = config.get_setting('search_excludes_mixed', default='')
        if excluidos:
            txt += '[CR][CR] - [COLOR goldenrod][B]Canales excluidos en las búsquedas de [COLOR yellow]Películas y/ó Series[/COLOR][/B]:'
            excluidos = scrapertools.find_multiple_matches(excluidos, "'(.*?)'")

            for excluido in excluidos:
                excluido = excluido.capitalize().strip()
                txt += '[CR]   [COLOR gold][B] ' + excluido + '[/B][/COLOR]'

    if config.get_setting('search_excludes_all', default=''):
        excluidos = config.get_setting('search_excludes_all', default='')
        if excluidos:
            txt += '[CR][CR] - [COLOR goldenrod][B]Canales excluidos en las búsquedas de [COLOR green]Todos[/COLOR][/B]:'
            excluidos = scrapertools.find_multiple_matches(excluidos, "'(.*?)'")

            for excluido in excluidos:
                excluido = excluido.capitalize().strip()
                txt += '[CR]   [COLOR gold][B] ' + excluido + '[/B][/COLOR]'

    if config.get_setting('search_show_last', default=True):
        txt += '[CR][CR] - Textos para búsquedas [B][COLOR goldenrod]Memorizados[/COLOR][/B]:'

        hay_lastest = False

        if config.get_setting('search_last_all', default=''):
            hay_lastest = True

            txt += '[CR]   [COLOR yellow][B]General:[/B][/COLOR]  ' + config.get_setting('search_last_all')

        if config.get_setting('search_last_movie', default=''):
            hay_lastest = True

            txt += '[CR]   [COLOR deepskyblue][B]Películas:[/B][/COLOR]  ' + config.get_setting('search_last_movie')

        if config.get_setting('search_last_tvshow', default=''):
            hay_lastest = True

            txt += '[CR]   [COLOR hotpink][B]Series:[/B][/COLOR]  ' + config.get_setting('search_last_tvshow')

        if config.get_setting('search_last_documentary', default=''):
            hay_lastest = True

            txt += '[CR]   [COLOR cyan][B]Documentales:[/B][/COLOR]  ' + config.get_setting('search_last_documentary')

        if config.get_setting('search_last_person', default=''):
            hay_lastest = True

            txt += '[CR]   [COLOR plum][B]Personas:[/B][/COLOR]  ' + config.get_setting('search_last_person')

        if not hay_lastest: txt += '[CR]   [COLOR cyan][B]Sin textos memorizados[/B][/COLOR]'

    platformtools.dialog_textviewer('Información sobre sus parámetros de búsquedas', txt)

    return True


def show_help(item):
    txt = ''

    if not config.get_setting('search_extra_main', default=False):
        txt += '[COLOR gold][B]Por Defecto[/B][/COLOR]:[CR]'
        txt += ' Está [COLOR coral][B]Des-Habilitada[/B][/COLOR] la opción del Menú principal y Sub-Menús [B][COLOR violet]Búsquedas Especiales (Listas TMDB, etc.)[/COLOR][/B][CR][CR]'

        txt += '[COLOR gold][B]Explicaciones[/B][/COLOR]:[CR]'

    txt += 'Desde los Ajustes [COLOR yellow][B]categoría Buscar[/B][/COLOR] se puede definir [COLOR chartreuse][B] los Resultados que se Previsualizan para cada canal[/B][/COLOR].'
    txt += ' Si por ejemplo el canal devuelve 15 resultados y se previsualizan 2, entrar en el enlace del [COLOR gold][B]Nombre del canal[/B][/COLOR] de la búsqueda para verlos todos.'

    txt += '[CR][CR]En cada web/canal el [COLOR cyan][B]Tiempo de Respuesta[/B][/COLOR] puede ser elevado y más aún si tiene Proxies Configurados.'

    txt += '[CR][CR]Según cada web/canal su buscador puede permitir diferenciar por [COLOR teal][B]Películas y/ó Series ó No[/B][/COLOR].'

    txt += '[CR][CR][COLOR yellowgreen][B]También es variable la sensibilidad de la búsqueda (si busca sólo en el Título ó también en la Sinopsis, el tratamiento si hay varias palabras, si devuelve muchos ó pocos resultados, etc.)[/B][/COLOR]'

    txt += '[CR][CR]Desde cualquier [COLOR teal][B]Película ó Serie[/B][/COLOR], se puede acceder al [COLOR yellow][B]Menú contextual[/B][/COLOR] para buscar esa misma referencia en los demás canales.'

    txt += '[CR][CR]Desde cualquier [COLOR teal][B]Película ó Serie[/B][/COLOR] guardada en [COLOR tan][B]Preferidos[/B][/COLOR], si al acceder se produce un error en la web, se ofrece un diálogo para volver a buscar esa referencia ([COLOR gold][B]Misma/Parecida/Similar[/B][/COLOR]) en los demás canales ó en el mismo canal (por si los enlaces ya no funcionan).'

    platformtools.dialog_textviewer('Información sobre búsquedas', txt)

    return True


def search(item, tecleado):
    logger.info()

    item.category = 'Buscar ' + tecleado
    if item.search_type == '': item.search_type = 'all'

    itemlist = do_search(item, tecleado)

    return itemlist


def do_search_channel(item, tecleado, ch):
    canal = __import__('channels.' + item.channel, fromlist=[''])

    if hasattr(canal, 'search'):
        ch['itemlist_search'] = canal.search(item, tecleado)
    else:
        logger.error('Search not found in channel %s. Implementar search o quitar searchable!' % item.channel)


def do_search(item, tecleado):
    itemlist = []

    channels_new_proxies = []

    if config.get_setting('search_no_work_proxies', default=False):
        config.set_setting('sin_resp', '')
        sin_results = False
    else:
        config.set_setting('sin_resp', 'no')
        no_results_proxies = True
        sin_results = True

    multithread = config.get_setting('search_multithread', default=True)
    threads = []

    search_limit_by_channel = config.get_setting('search_limit_by_channel', default=2)

    progreso = platformtools.dialog_progress('Buscando ' + '[B][COLOR yellow]' + tecleado + '[/B][/COLOR]', '...')

    # ~ status para descartar desactivados por el usuario
    if item.search_special == 'anime' or item.search_special == 'dorama':
        filtros = { 'searchable': False, 'status': 0 }
    else:
        if item.only_channels_group:
            if item.group == 'dorama': filtros = { 'status': 0 }
            elif item.group == 'anime': filtros = { 'status': 0 }
            else: filtros = { 'searchable': True, 'status': 0 }
        else: filtros = { 'searchable': True, 'status': 0 }

    if item.search_type != 'all':
        if item.only_channels_group:
            if not item.group == 'docs': filtros['search_types'] = item.search_type
        else: filtros['search_types'] = item.search_type
    else:
        if item.only_channels_group:
            if not item.group == 'tales':
                if not item.group == 'torrents':
                    if not item.group == 'dorama':
                        if not item.group == 'anime':
                            filtros['search_types'] = item.search_type

    ch_list = channeltools.get_channels_list(filtros=filtros)

    # ~ descartar from_channel (búsqueda en otros canales)
    if item.from_channel != '':
        ch_list = [ch for ch in ch_list if ch['id'] != item.from_channel]

    if item.search_type == 'all':
        if item.only_channels_group and (item.group == 'docs' or item.group == '3d'): pass
        else: ch_list = [ch for ch in ch_list if 'documentary' not in ch['categories']]

    num_canales = float(len(ch_list))

    only_torrents = ''
    if item.extra == 'only_torrents': only_torrents = item.extra

    only_prefered = config.get_setting('search_only_prefered', default=False)
    only_suggesteds = config.get_setting('search_only_suggesteds', default=False)

    con_torrents = config.get_setting('search_con_torrents', default=False)
    no_torrents = config.get_setting('search_no_torrents', default=False)
    no_exclusively_torrents = config.get_setting('search_no_exclusively_torrents', default=False)

    no_inestables = config.get_setting('search_no_inestables', default=False)
    no_proxies = config.get_setting('search_no_proxies', default=False)

    no_problematicos = config.get_setting('search_no_problematicos', default=False)

    no_channels = config.get_setting('search_no_channels', default=False)

    only_includes = config.get_setting('search_included_all', default='')

    no_notices = config.get_setting('search_no_notices', default='')

    if item.search_type == 'movie':
        channels_search_excluded = config.get_setting('search_excludes_movies', default='')

    elif item.search_type == 'tvshow':
        channels_search_excluded = config.get_setting('search_excludes_tvshows', default='')

    elif item.search_type == 'documentary':
        channels_search_excluded = config.get_setting('search_excludes_documentaries', default='')

    elif item.extra == 'only_torrents':
        channels_search_excluded = config.get_setting('search_excludes_torrents', default='')
    else:
        channels_search_excluded = config.get_setting('search_excludes_mixed', default='')
        channels_search_excluded = channels_search_excluded + config.get_setting('search_excludes_all', default='')

    for i, ch in enumerate(ch_list):
        perc = int(i / num_canales * 100)

        progreso.update(perc, 'Analizar %s en el canal %s ' % (tecleado, ch['name']))

        c_item = Item( channel=ch['id'], action='search', search_type=item.search_type, title='Buscar en ' + ch['name'], thumbnail=ch['thumbnail'] )

        if item.search_special == 'anime':
            if 'anime' in ch['clusters']:
                if not 'Web dedicada exclusivamente al anime' in ch['notes']:
                    num_canales = num_canales - 1
                    continue
            else: continue

        if item.search_special == 'dorama':
            if 'dorama' in ch['clusters']:
                if not 'Web dedicada exclusivamente al dorama' in ch['notes']:
                    num_canales = num_canales - 1
                    continue
            else: continue

        if not PY3:
            if 'mismatched' in ch['clusters']:
                num_canales = num_canales - 1
                continue

        if con_torrents:
            if not 'torrents' in ch['clusters']:
                 num_canales = num_canales - 1
                 continue

        if no_torrents:
            if 'torrents' in ch['clusters']:
                num_canales = num_canales - 1
                continue

        if no_exclusively_torrents:
            if 'enlaces torrent exclusivamente' in ch['notes'].lower():
                 num_canales = num_canales - 1
                 continue

        if 'register' in ch['clusters']:
            sesion_login = config.get_setting('channel_%s_%s_login' % (ch['id'], ch['id']), default=False)
            if sesion_login == False:
                num_canales = num_canales - 1
                continue

        if no_inestables or config.get_setting('mnu_simple', default=False):
            if 'inestable' in ch['clusters']:
                num_canales = num_canales - 1
                continue

        if no_problematicos or config.get_setting('mnu_simple', default=False):
            if 'problematic' in ch['clusters']:
                num_canales = num_canales - 1
                continue

        if no_proxies:
            if 'proxies' in ch['notes'].lower():
                cfg_proxies_channel = 'channel_' + ch['name'].lower() + '_proxies'
                if config.get_setting(cfg_proxies_channel, default=''):
                    if no_channels: platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado por proxies[/COLOR][/B]' % color_adver)

                    num_canales = num_canales - 1
                    continue

        if only_includes:
            channels_preselct = str(only_includes).replace('[', '').replace(']', ',')
            if not ("'" + ch['id'] + "'") in str(channels_preselct):
                if no_channels: platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado no está en Incluidos[/COLOR][/B]' % color_exec)

                num_canales = num_canales - 1
                continue

        if no_notices:
            if 'notice' in ch['clusters']:
                if only_includes:
                    channels_preselct = str(only_includes).replace('[', '').replace(']', ',')
                    if not ("'" + ch['id'] + "'") in str(channels_preselct):
                        if no_channels: platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado no está en Incluidos[/COLOR][/B]' % color_exec)

                        num_canales = num_canales - 1
                        continue
                else:
                    platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado por CloudFlare Protection[/COLOR][/B]' % color_exec)
                    num_canales = num_canales - 1
                    continue

        if channels_search_excluded:
            channels_preselct = str(channels_search_excluded).replace('[', '').replace(']', ',')
            if ("'" + ch['id'] + "'") in str(channels_preselct):
                if no_channels: platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado por Excluido[/COLOR][/B]' % color_exec)

                num_canales = num_canales - 1
                continue

        cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'
        if config.get_setting(cfg_searchable_channel, default=False):
            if no_channels: platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado por Excluido[/COLOR][/B]' % color_adver)
            num_canales = num_canales - 1
            continue

        if item.only_channels_group:
            if not ("'" + ch['id'] + "'") in str(item.only_channels_group):
                num_canales = num_canales - 1
                continue
        else:
            if only_prefered:
                cfg_status_channel = 'channel_' + ch['name'].lower() + '_status'
                if not config.get_setting(cfg_status_channel, default=''):
                    num_canales = num_canales - 1
                    continue
            elif only_suggesteds:
                if not 'suggested' in ch['clusters']:
                   num_canales = num_canales - 1
                   continue
            elif only_torrents:
                if not 'torrents' in ch['clusters']:
                   num_canales = num_canales - 1
                   continue

        if multithread:
            t = Thread(target=do_search_channel, args=[c_item, tecleado, ch], name=ch['name'])
            t.setDaemon(True)
            t.start()
            threads.append(t)
        else:
            do_search_channel(c_item, tecleado, ch)

        if progreso.iscanceled(): break

    if multithread:
        if PY3:
            pendent = [a for a in threads if a.is_alive()]
        else:
            pendent = [a for a in threads if a.isAlive()]

        while len(pendent) > 0:
            hechos = num_canales - len(pendent)
            perc = int(hechos / num_canales * 100)
            mensaje = ', '.join([a.getName() for a in pendent])

            progreso.update(perc, '[COLOR gold]Buscando[/COLOR] en el %d de %d canales. [COLOR chartreuse]Quedan[/COLOR] %d : %s' % (hechos, num_canales, len(pendent), mensaje))

            if progreso.iscanceled(): break

            time.sleep(0.5)

            if PY3:
                pendent = [a for a in threads if a.is_alive()]
            else:
                pendent = [a for a in threads if a.isAlive()]

    config.set_setting('sin_resp', 'si')

    if item.from_channel != '': 
        # ~ Buscar exacto o parecido en otros/todos canales de una peli/serie
        tecleado_lower = tecleado.lower()

        for ch in ch_list:
            if 'itemlist_search' in ch and len(ch['itemlist_search']) > 0:
                for it in ch['itemlist_search']:
                    if it.contentType not in ['movie','tvshow','season']: continue
                    if it.infoLabels['tmdb_id'] and item.infoLabels['tmdb_id']:
                        if it.infoLabels['tmdb_id'] != item.infoLabels['tmdb_id']: continue
                    else:
                        if it.contentType == 'movie' and it.contentTitle.lower() != tecleado_lower: continue
                        if it.contentType in ['tvshow','season'] and it.contentSerieName.lower() != tecleado_lower: continue

                    if no_inestables or config.get_setting('mnu_simple', default=False):
                        if 'inestable' in ch['clusters']: continue

                    if no_problematicos or config.get_setting('mnu_simple', default=False):
                        if 'problematic' in ch['clusters']: continue

                    color = 'chartreuse'

                    name = ch['name']

                    if ch['status'] == 1: color = color_list_prefe

                    if 'proxies' in ch['notes'].lower():
                        cfg_proxies_channel = 'channel_' + ch['name'].lower() + '_proxies'
                        if config.get_setting(cfg_proxies_channel, default=''): color = color_list_proxies

                    if 'inestable' in ch['clusters']: name += '[I][COLOR plum] (inestable) [/COLOR][/I]'

                    if 'problematic' in ch['clusters']: name += '[I][COLOR darkgoldenrod] (problemático) [/COLOR][/I]'

                    it.title = '[B][COLOR ' + color + ']' + name + '[/B][/COLOR] ' + it.title

                    itemlist.append(it)

    else:
        # ~ Búsqueda parecida en todos los canales : link para acceder a todas las coincidencias y previsualización de n enlaces por canal
        nro = 0
        sin = 0

        titulo = ''

        for ch in sorted(ch_list, key=lambda ch: True if 'itemlist_search' not in ch or len(ch['itemlist_search']) == 0 else False):
            action = ''

            cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

            if 'itemlist_search' in ch:
                if not PY3:
                    if 'mismatched' in ch['clusters']:
                        platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado por incompatible[/COLOR][/B]' % color_exec)
                        continue

                if len(ch['itemlist_search']) == 0:
                    action = 'mainlist'

                    if not config.get_setting('search_no_results_proxies', default=True): continue

                    sin += 1

                    if sin == 1:
                        itemlist.append(item.clone( action='', title='[B][I]- CANALES:  Sin Resultados[/I][/B]', thumbnail=config.get_thumb('search'), text_color='yellow' ))

                    if no_results or sin_results:
                        titulo = ch['name']

                        if config.get_setting(cfg_proxies_channel, default=''):
                            if 'notice' in ch['clusters']: titulo = titulo + ' [COLOR goldenrod]Posible cloudflare[/COLOR]'
                            channels_new_proxies.append(ch['id'])
                            titulo = titulo + ' [COLOR red]quizás requiera [I]Nuevos Proxies[/I]'
                        else:
                            if 'proxies' in ch['notes'].lower():
                                if 'notice' in ch['clusters']: titulo = titulo + ' [COLOR goldenrod]Posible cloudflare[/COLOR]'
                                channels_new_proxies.append(ch['id'])
                                titulo = titulo + ' [COLOR darkorange]quizás necesite [I]Configurar Proxies[/I]'

                        if no_results == False:
                            if sin_results:
                                if not 'quizás' in titulo: continue
                    else:
                        if config.get_setting(cfg_proxies_channel, default=''):
                            if no_results_proxies:
                                titulo = ch['name']

                                channels_new_proxies.append(ch['id'])
                                if 'notice' in ch['clusters']: titulo = titulo + ' [COLOR goldenrod]Posible cloudflare[/COLOR]'
                                titulo = titulo + ' [COLOR red]quizás requiera [I]Nuevos Proxies[/I]'
                            else:
                                continue
                        else:
                            if no_channels: platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado sin resultados[/COLOR][/B]' % color_avis)
                            continue
                else:
                    action = 'search'
                    texto = 'resultados'

                    if len(ch['itemlist_search']) == 1: texto = 'resultado'

                    name = ch['name']

                    color = 'chartreuse'

                    if ch['status'] == 1: color = color_list_prefe

                    if 'proxies' in ch['notes'].lower():
                        cfg_proxies_channel = 'channel_' + ch['name'].lower() + '_proxies'
                        if config.get_setting(cfg_proxies_channel, default=''): color = color_list_proxies

                    if 'inestable' in ch['clusters']: texto += '[I][COLOR plum] (inestable)[/COLOR][/I]'

                    if 'problematic' in ch['clusters']: texto += '[I][COLOR darkgoldenrod] (problemático)[/COLOR][/I]'

                    titulo = '%s [COLOR %s]- %d %s' % (name, color, len(ch['itemlist_search']), texto)
            else:
                if progreso.iscanceled(): titulo = '%s [COLOR darkcyan]búsqueda cancelada' % ch['name']
                else:
                    if item.only_channels_group:
                        if not ("'" + ch['id'] + "'") in str(item.only_channels_group): continue

                    titulo = '%s [COLOR plum]No se ha buscado' % ch['name']

                    if item.search_special == 'anime':
                        if 'anime' in ch['clusters']:
                            if not 'Web dedicada exclusivamente al anime' in ch['notes']: continue
                        else: continue

                    if item.search_special == 'dorama':
                        if 'dorama' in ch['clusters']:
                            if not 'Web dedicada exclusivamente al dorama' in ch['notes']: continue
                        else: continue

                    if not PY3:
                        if 'mismatched' in ch['clusters']:
                            platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado por incompatible[/COLOR][/B]' % color_exec)
                            continue

                    if con_torrents:
                        if not 'torrents' in ch['clusters']: continue

                    if no_torrents:
                        if 'torrents' in ch['clusters']: continue

                    if no_exclusively_torrents:
                       if 'enlaces torrent exclusivamente' in ch['notes'].lower(): continue

                    if no_inestables or config.get_setting('mnu_simple', default=False):
                        if 'inestable' in ch['clusters']: continue

                    if no_problematicos or config.get_setting('mnu_simple', default=False):
                        if 'problematic' in ch['clusters']: continue

                    if no_proxies:
                        if 'proxies' in ch['notes'].lower():
                            if config.get_setting(cfg_proxies_channel, default=''):
                                if no_channels: titulo = titulo + ' [COLOR yellow]Ignorado por proxies'
                                continue

                    if only_includes:
                        channels_preselct = str(only_includes).replace('[', '').replace(']', ',')
                        if not ("'" + ch['id'] + "'") in str(channels_preselct):
                            if no_channels: titulo = titulo + ' [COLOR yellow]Ignorado no está en Incluidos'
                            continue

                    if no_notices:
                        if 'notice' in ch['clusters']:
                            if only_includes:
                                channels_preselct = str(only_includes).replace('[', '').replace(']', ',')
                                if not ("'" + ch['id'] + "'") in str(channels_preselct):
                                    if no_channels: titulo = titulo + ' [COLOR yellow]Ignorado no está en Incluidos'
                                    continue

                            else:
                                if no_channels: titulo = titulo + ' [COLOR yellow]Ignorado por CloudFlare Protection'
                                continue

                    if channels_search_excluded:
                        channels_preselct = str(channels_search_excluded).replace('[', '').replace(']', ',')
                        if ("'" + ch['id'] + "'") in str(channels_preselct):
                            if no_channels: titulo = titulo + ' [COLOR cyan]Ignorado por Excluido'
                            continue

                    cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'
                    if config.get_setting(cfg_searchable_channel, default=False):
                        if no_channels: titulo = titulo + ' [COLOR cyan]Ignorado por Excluido'
                        continue
                    else:
                       if only_prefered: continue
                       elif only_suggesteds: continue
                       elif only_torrents: continue

                       elif 'register' in ch['clusters']:
                           username = config.get_setting(ch['id'] + '_username', ch['id'], default='')
                           if not username: titulo = titulo + ' [COLOR teal]faltan [I]Credenciales Cuenta[/I]'
                           else:
                               sesion_login = config.get_setting('channel_%s_%s_login' % (ch['id'], ch['id']), default=False)
                               if sesion_login == False: titulo = titulo + ' [COLOR teal]falta [I]Iniciar Sesion[/I]'
                       elif only_includes:
                           if no_channels: titulo = titulo + ' [COLOR yellow]Ignorado no está en Incluidos'
                       elif no_notices:
                           if no_channels: titulo = titulo + ' [COLOR yellow]Ignorado por CloudFlare Protection'
                       elif 'proxies' in ch['notes'].lower(): titulo = titulo + ' [COLOR red]comprobar si [I]Necesita Proxies[/I]'
                       else:
                           if channels_search_excluded:
                               channels_preselct = str(channels_search_excluded).replace('[', '').replace(']', ',')
                               if ("'" + ch['id'] + "'") in str(channels_preselct):
                                   if no_channels: titulo = titulo + ' [COLOR cyan]Ignorado por Excluido'

                           else:
                              cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'
                              if config.get_setting(cfg_searchable_channel, default=False):
                                  if no_channels: titulo = titulo + ' [COLOR cyan]Ignorado por Excluido'
                              else: titulo = titulo + ' [COLOR yellow]comprobar el canal'

            nro += 1

            if nro == 1:
                itemlist.append(item.clone( action='', title='[B][I]- BUSCADO:  ' + tecleado + '[/I][/B]', thumbnail=config.get_thumb('search'), text_color='yellow' ))

                if config.get_setting('sub_mnu_cfg_prox_search', default=True):
                    itemlist.append(Item( channel='submnuctext', action='submnu_search', title='[B]Personalizar Próximas búsquedas[/B]', context=context_cfg_search, extra = item.search_type, thumbnail=config.get_thumb('help'), text_color='moccasin' ))

                itemlist.append(item.clone( channel='helper', action='show_help_audios', title= '[COLOR green][B]Información[/B][/COLOR] [COLOR cyan][B]Idiomas[/B][/COLOR] en los Audios de los Vídeos', thumbnail=config.get_thumb('news') ))

            if not titulo:
                itemlist.append(Item( action = '', title = tecleado + '[COLOR coral]sin resultados en ningún canal[/COLOR]' ))
                break

            context = []

            tit = '[COLOR cyan][B]Cambios Próximas Búsquedas[/B][/COLOR]'
            context.append({'title': tit, 'channel': '', 'action': ''})

            if ' Proxies' in titulo:
                tit = '[COLOR darkorange][B]Test Web del canal[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_tests'})

                if 'proxies' in ch['notes'].lower():
                    cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

                    if not config.get_setting(cfg_proxies_channel, default=''):
                        tit = '[COLOR %s]Información Proxies[/COLOR]' % color_infor
                        context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

                    tit = '[COLOR %s][B]Configurar proxies a usar[/B][/COLOR]' % color_list_proxies
                    context.append({'title': tit, 'channel': item.channel, 'action': '_proxies'})
            else:
                if 'proxies' in ch['notes'].lower():
                    cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

                    if config.get_setting(cfg_proxies_channel, default=''):
                        tit = '[COLOR darkorange][B]Test Web del canal[/B][/COLOR]'
                        context.append({'title': tit, 'channel': item.channel, 'action': '_tests'})

                        tit = '[COLOR %s]Información Proxies[/COLOR]' % color_infor
                        context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

                        tit = '[COLOR %s][B]Configurar proxies a usar[/B][/COLOR]' % color_list_proxies
                        context.append({'title': tit, 'channel': item.channel, 'action': '_proxies'})

            cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'

            if config.get_setting(cfg_searchable_channel, default=False):
                tit = '[COLOR %s][B]Quitar exclusión en búsquedas[/B][/COLOR]' % color_adver
                context.append({'title': tit, 'channel': item.channel, 'action': '_quitar_no_searchables'})
            else:
                tit = '[COLOR %s][B]Excluir de búsquedas[/B][/COLOR]' % color_adver
                context.append({'title': tit, 'channel': item.channel, 'action': '_poner_no_searchables'})

            if ch['status'] != 1:
                tit = '[COLOR %s][B]Marcar canal como Preferido[/B][/COLOR]' % color_list_prefe
                context.append({'title': tit, 'channel': 'actions', 'action': '_marcar_canales', 'estado': 1, 'canal': ch['id']})

            if ch['status'] != 0:
                if ch['status'] == 1:
                    tit = '[COLOR %s][B]Des-Marcar canal como Preferido[/B][/COLOR]' % color_list_prefe
                    context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})

            if ch['status'] != -1:
                tit = '[COLOR %s][B]Marcar canal como Desactivado[/B][/COLOR]' % color_list_inactive
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': -1})

            color = 'chartreuse'

            titulo = '[B][COLOR %s]%s[/COLOR][/B]' % (color, titulo)

            itemlist.append(Item( channel=ch['id'], action=action, buscando=tecleado, title=titulo, module_search= True, context=context, thumbnail=ch['thumbnail'], search_type=item.search_type ))

            if 'itemlist_search' in ch:
                for j, it in enumerate(ch['itemlist_search']):
                    if it.contentType not in ['movie', 'tvshow', 'season']: continue
                    if j < search_limit_by_channel: itemlist.append(it)
                    else: break

            if 'búsqueda cancelada' in titulo: break

    if config.get_setting('sub_mnu_cfg_prox_search', default=True):
        if channels_new_proxies:
            itemlist.append(Item( channel='submnuctext', action='_search_new_proxies', title='[B][COLOR goldenrod]BUSCAR [COLOR red]Proxies[/COLOR] en [/COLOR][COLOR chartreuse]TODOS los Canales [/COLOR][COLOR coral]SIN RESULTADOS[/COLOR][/B]', channels_new_proxies = channels_new_proxies, extra = item.search_type, thumbnail=config.get_thumb('flame') ))

    progreso.close()

    if len(itemlist) == 0:
        if only_prefered: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Búsqueda solo en preferidos[/COLOR][/B]' % color_infor)
        elif only_suggesteds: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Búsqueda solo en sugeridos[/COLOR][/B]' % color_infor)
        elif only_torrents: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Búsqueda solo en torrents[/COLOR][/B]' % color_infor)
        elif only_includes: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Búsqueda solo en Incluidos[/COLOR][/B]' % color_infor)
        else: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Búsqueda sin resultados[/COLOR][/B]' % color_infor)

    return itemlist


def _tests(item):
    from modules import submnuctext
    submnuctext._test_webs(item)


def _proxies(item):
    if platformtools.dialog_yesno(item.from_channel.capitalize(), '[COLOR yellow][B]Solo se tendrán en cuenta para las próximas búsquedas[/B][/COLOR]','[COLOR red][B]¿ Efectuar una nueva búsqueda de proxies en el canal ?[/B][/COLOR]'):
        from modules import submnuctext

        item.module_search = True
        submnuctext._proxies(item)


def _poner_no_searchables(item):
    from modules import submnuctext

    item.module_search = True
    submnuctext._poner_no_searchable(item)

def _quitar_no_searchables(item):
    from modules import submnuctext

    item.module_search = True
    submnuctext._quitar_no_searchable(item)
