# -*- coding: utf-8 -*-

import os

from platformcode import logger, config, platformtools
from core import filetools

from datetime import datetime


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')

cfg_search_excluded_movies = 'search_excludes_movies'
cfg_search_excluded_tvshows = 'search_excludes_tvshows'
cfg_search_excluded_documentaries = 'search_excludes_documentaries'
cfg_search_excluded_torrents = 'search_excludes_torrents'
cfg_search_excluded_mixed = 'search_excludes_mixed'
cfg_search_excluded_all = 'search_excludes_all'

channels_search_excluded_movies = config.get_setting(cfg_search_excluded_movies, default='')
channels_search_excluded_tvshows = config.get_setting(cfg_search_excluded_tvshows, default='')
channels_search_excluded_documentaries = config.get_setting(cfg_search_excluded_documentaries, default='')
channels_search_excluded_torrents = config.get_setting(cfg_search_excluded_torrents, default='')
channels_search_excluded_mixed = config.get_setting(cfg_search_excluded_mixed, default='')
channels_search_excluded_all = config.get_setting(cfg_search_excluded_all, default='')

current_year = int(datetime.today().year)
current_month = int(datetime.today().month)


thumb_filmaffinity = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'filmaffinity.jpg')
thumb_tmdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'tmdb.jpg')


context_proxy_channels = []

tit = '[COLOR %s]Información menús[/COLOR]' % color_infor
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_menu_parameters'})

tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
context_proxy_channels.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

tit = '[COLOR %s]Ajustes categorías menú y proxies[/COLOR]' % color_exec
context_proxy_channels.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


def submnu_news(item):
    logger.info()
    itemlist = []

    if not item.extra == 'tvshows':
        itemlist.append(item.clone( action='', title='[B]Novedades en Películas:[/B]', thumbnail=config.get_thumb('novedades'), text_color='deepskyblue' ))

        itemlist.append(item.clone( channel='filmaffinitylists', action='list_all', title=' - Cartelera en [COLOR violet]Filmaffinity[/COLOR]',
                                    url = 'https://www.filmaffinity.com/es/cat_new_th_es.html', search_type = 'movie', thumbnail=thumb_filmaffinity ))

        itemlist.append(item.clone( channel='tmdblists', action='listado', title=' - Cartelera en [COLOR violet]TMDB[/COLOR]',
                                    extra = 'now_playing', search_type = 'movie', thumbnail=thumb_tmdb ))

    itemlist.append(item.clone( action='', title='[B]Novedades en Películas y Series:[/B]', thumbnail=config.get_thumb('novedades'), text_color='yellow' ))

    itemlist.append(item.clone( title = ' - Novedades a la venta', channel='filmaffinitylists', action = 'list_all', 
                                url = 'https://www.filmaffinity.com/es/cat_new_sa_es.html', search_type = 'all', thumbnail=thumb_filmaffinity ))

    itemlist.append(item.clone( title = ' - Novedades en alquiler', channel='filmaffinitylists', action = 'list_all',
                                url = 'https://www.filmaffinity.com/es/cat_new_re_es.html', search_type = 'all', thumbnail=thumb_filmaffinity ))

    return itemlist


def submnu_genres(item):
    logger.info()
    itemlist = []

    if config.get_setting('mnu_search_proxy_channels', default=False):
        itemlist.append(item.clone( action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                    only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

    itemlist.append(item.clone( channel='generos', action='mainlist', title='[B]Géneros[/B]', thumbnail=config.get_thumb('genres'), text_color='moccasin' ))

    itemlist.append(item.clone( action='', title= '[B]Canales que podrían necesitar Nuevamente [COLOR red]Proxies[/COLOR]:[/B]', text_color='magenta' ))

    itemlist.append(item.clone( channel='groups', action='ch_generos', title=' - Canales con Películas', group = 'generos', extra = 'movies', thumbnail = config.get_thumb('movie'), text_color='deepskyblue' ))

    itemlist.append(item.clone( channel='groups', action='ch_generos', title=' - Canales con Series', group = 'generos', extra = 'tvshows', thumbnail = config.get_thumb('tvshow'), text_color='hotpink' ))

    return itemlist


def submnu_special(item):
    logger.info()
    itemlist = []

    if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'movies':
        itemlist.append(item.clone( action='', title = '[COLOR deepskyblue][B]Películas[COLOR goldenrod] Recomendadas:[/B][/COLOR]', thumbnail=config.get_thumb('movie'), folder=False ))

        itemlist.append(item.clone( channel='cinedeantes', action='list_all', title=' - Las joyas del cine clásico',
                                    url = 'https://cinedeantes2.weebly.com/joyas-del-cine.html',
                                    thumbnail=config.get_thumb('bestmovies'),search_type = 'movie' ))

        itemlist.append(item.clone( channel='adnstream', action='_ayer_y_siempre', title=' - Las mejores del cine de ayer y siempre', thumbnail = config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(item.clone( channel='zoowomaniacos', action='_culto', title=' - Las mejores del cine de culto', thumbnail = config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(item.clone( channel='zoowomaniacos', action='_las1001', title=' - Las 1001 que hay que ver', thumbnail = config.get_thumb('bestmovies'), search_type = 'movie' ))

    if config.get_setting('search_extra_main', default=False):
        if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'movies' or item.extra == 'tvshows':
            itemlist.append(item.clone( action='', title= '[B]Búsquedas por Título en TMDB:[/B]', folder=False, text_color='pink', thumbnail=thumb_tmdb ))

            itemlist.append(item.clone( channel='tmdblists', action='search', search_type='movie', title= ' - Buscar [COLOR deepskyblue]Película[/COLOR] ...', thumbnail = config.get_thumb('movie') ))

            itemlist.append(item.clone( channel='tmdblists', action='search', search_type='tvshow', title= ' - Buscar [COLOR hotpink]Serie[/COLOR] ...', thumbnail = config.get_thumb('tvshow') ))

            itemlist.append(item.clone( action='', title= '[B]Búsquedas por Título en Filmaffinity:[/B]', folder=False, text_color='pink', thumbnail=thumb_filmaffinity ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='listas', search_type='all', stype='title', title=' - Buscar [COLOR yellow]Película y/ó Serie[/COLOR] ...', thumbnail=config.get_thumb('search') ))

        if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'movies' or item.extra == 'tvshows':
            itemlist.append(item.clone( action='', title = '[B]Búsquedas de Personas en TMDB:[/B]', thumbnail=thumb_tmdb, folder=False, text_color='violet' ))

            itemlist.append(item.clone( channel='tmdblists', action='personas', title= ' - Buscar [COLOR aquamarine]intérprete[/COLOR] ...', search_type='cast', thumbnail = config.get_thumb('search') ))

            itemlist.append(item.clone( channel='tmdblists', action='personas', title= ' - Buscar [COLOR springgreen]dirección[/COLOR] ...', search_type='crew', thumbnail = config.get_thumb('search') ))

            itemlist.append(item.clone( action='', title = '[B]Búsquedas de Personas en Filmaffinity:[/B]', thumbnail=thumb_filmaffinity, folder=False, text_color='violet' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='listas', search_type='person', stype='cast', title=' - Buscar [COLOR aquamarine]intérprete[/COLOR] ...', thumbnail = config.get_thumb('search')))

            itemlist.append(item.clone( channel='filmaffinitylists', action='listas', search_type='person', stype='director', title=' - Buscar [COLOR springgreen]dirección[/COLOR] ...', thumbnail = config.get_thumb('search')))

        if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'movies' or item.extra == 'torrents':
            itemlist.append(item.clone( action='', title='[COLOR deepskyblue][B]Películas[/COLOR] a través de Listas en TMDB ó Filmaffinity:[/B]', thumbnail=config.get_thumb('movie'), folder=False, text_color='pink' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - En Cartelera', extra='now_playing', thumbnail=thumb_tmdb, search_type = 'movie' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='list_all', title= ' - En Cartelera', 
                                        url = 'https://www.filmaffinity.com/es/cat_new_th_es.html', thumbnail=thumb_filmaffinity, search_type = 'movie' ))

            if not current_month == 4:
                itemlist.append(item.clone( channel='filmaffinitylists', action='_oscars', title=' - Premios Oscar', thumbnail=config.get_thumb('oscars'), search_type = 'movie' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_sagas', title=' - Sagas y colecciones', thumbnail=config.get_thumb('bestsagas'), search_type = 'movie' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - Más populares', extra='popular', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - Más valoradas', extra='top_rated', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_bestmovies', title=' - Recomendadas', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

            itemlist.append(item.clone( channel='tmdblists', action='networks', title=' - Por productora', thumbnail=thumb_tmdb, search_type = 'movie' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='plataformas', title='   - Por plataforma', thumbnail=thumb_filmaffinity, search_type = 'movie' ))

            itemlist.append(item.clone( channel='tmdblists', action='generos', title=' - Por género', thumbnail=thumb_tmdb, search_type = 'movie' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_genres', title=' - Por género', thumbnail=thumb_filmaffinity, search_type = 'movie' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='paises', title='   - Por país', thumbnail=config.get_thumb('idiomas'), search_type = 'movie' ))

            itemlist.append(item.clone( channel='tmdblists', action='anios', title=' - Por año', thumbnail=thumb_tmdb, search_type = 'movie' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_years', title='   - Por año', thumbnail=thumb_filmaffinity, search_type = 'movie' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_themes', title=' - Por tema', thumbnail=config.get_thumb('listthemes'), search_type = 'movie' ))

        if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'tvshows' or item.extra == 'torrents':
            itemlist.append(item.clone( action='', title = '[COLOR hotpink][B]Series[/COLOR] a través de Listas en TMDB ó Filmaffinity:[/B]', thumbnail=config.get_thumb('tvshow'), folder=False, text_color='pink' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - En emisión', extra='on_the_air', thumbnail=thumb_filmaffinity, search_type = 'tvshow' ))

            if not current_month == 10:
                itemlist.append(item.clone( channel='filmaffinitylists', action='_emmys', title=' - Premios Emmy', thumbnail=config.get_thumb('emmys'), origen='mnu_esp', search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - Más populares', extra='popular', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - Más valoradas', extra='top_rated', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_besttvshows', title=' - Recomendadas', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='tmdblists', action='networks', title='   - Por productora', thumbnail=thumb_tmdb, search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='plataformas', title='   - Por plataforma', thumbnail=thumb_filmaffinity, search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='tmdblists', action='generos', title=' - Por género', thumbnail=thumb_tmdb, search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_genres', title=' - Por género', thumbnail=thumb_filmaffinity, search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='tmdblists', action='anios', title=' - Por año', thumbnail=thumb_tmdb, search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_years', title='   - Por año', thumbnail=thumb_filmaffinity, search_type = 'tvshow' ))

        if not item.extra == 'documentaries':
            itemlist.append(item.clone( action='', title = '[COLOR yellow][B]Películas y Series[/COLOR] a través de Listas en Filmaffinity:[/B]', thumbnail=thumb_filmaffinity, folder=False, text_color='pink' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='plataformas', title=' - Por plataforma', thumbnail=config.get_thumb('booklet'), search_type = 'all' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_genres', title=' - Por género', thumbnail=config.get_thumb('listgenres'), search_type = 'all' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='paises', title=' - Por país', thumbnail=config.get_thumb('idiomas'), search_type = 'all' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_years', title=' - Por año', thumbnail=config.get_thumb('listyears'), search_type = 'all' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_themes', title=' - Por tema', thumbnail=config.get_thumb('listthemes'), search_type = 'all' ))

        if not item.no_docs:
            if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'documentaries' or item.extra == 'torrents':
                itemlist.append(item.clone( action='', title = '[COLOR cyan][B]Documentales[/COLOR] a través de Listas en Filmaffinity:[/B]', thumbnail=thumb_filmaffinity, folder=False, text_color='pink' ))

                if config.get_setting('mnu_documentales', default=True):
                    itemlist.append(item.clone( channel='filmaffinitylists', action='_bestdocumentaries', title=' - Los Mejores', thumbnail = config.get_thumb('bestdocumentaries'), search_type = 'all' ))

                    itemlist.append(item.clone( channel='filmaffinitylists', action='listas', search_type='documentary', stype='documentary', title=' - Buscar [COLOR cyan]Documental[/COLOR] ...', thumbnail=config.get_thumb('search') ))

    return itemlist


def submnu_search(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='search', action='show_help', title='[COLOR green][B]Información búsquedas[/B][/COLOR]', thumbnail = config.get_thumb('help') ))

    if config.get_setting('search_extra_proxies', default=True):
        itemlist.append(item.clone( action='', title='[B]Búsquedas en canales con Proxies:[/B]', folder=False, text_color='red' ))

        itemlist.append(item.clone( channel='helper', action='show_help_proxies', title= ' - [COLOR green][B]Información Uso de proxies[/B][/COLOR]' ))
        itemlist.append(item.clone( channel='helper', action='show_help_providers', title= ' - [COLOR green][B]Información Proveedores de proxies[/B][/COLOR]' ))
        itemlist.append(item.clone( channel='helper', action='show_help_providers2', title= ' - [COLOR green][B]Información Lista[/B][/COLOR] [COLOR aqua][B]Ampliada[/B][/COLOR][COLOR green][B] Proveedores de proxies[/B][/COLOR]' ))
        itemlist.append(item.clone( channel='helper', action='show_help_recommended', title= ' - Qué [COLOR green][B]Proveedores de proxies[/B][/COLOR] están [COLOR lime][B]Recomendados[/B][/COLOR]' ))

        itemlist.append(item.clone( channel='filters', title=' - Qué canales pueden usar proxies', action='with_proxies', thumbnail=config.get_thumb('stack'), new_proxies=True ))

        if config.get_setting('memorize_channels_proxies', default=True):
            itemlist.append(item.clone( channel='filters', title=  ' - Qué [COLOR red]canales[/COLOR] tiene con proxies memorizados', action='with_proxies',
                                        thumbnail=config.get_thumb('stack'), new_proxies=True, memo_proxies=True, test_proxies=True ))

        itemlist.append(item.clone( channel='actions', title= ' - Quitar los proxies en los canales [COLOR red](que los tengan memorizados)[/COLOR]',
                                    action = 'manto_proxies', thumbnail=config.get_thumb('flame') ))

        itemlist.append(item.clone( channel='proxysearch', title=' - Configurar proxies a usar [COLOR plum](en los canales que los necesiten)[/COLOR]',
                                    action='proxysearch_all', thumbnail=config.get_thumb('flame') ))

        if config.get_setting('proxysearch_excludes', default=''):
            itemlist.append(item.clone( channel='proxysearch', title=' - Anular los canales excluidos de Configurar proxies a usar',
                                        action='channels_proxysearch_del', thumbnail=config.get_thumb('flame'), text_color='coral' ))


    if item.only_options_proxies:
        itemlist.append(item.clone( action='', title= '[B]Configuración:[/B]', folder=False, text_color='goldenrod' ))

        itemlist.append(item.clone( channel='actions', title=' - [COLOR chocolate]Ajustes[/COLOR] categorías ([COLOR tan][B]Menú[/B][/COLOR], [COLOR red][B]Proxies[/B][/COLOR] y [COLOR yellow][B]Buscar[/B][/COLOR])', action = 'open_settings', thumbnail=config.get_thumb('settings') ))

        return itemlist


    if config.get_setting('sub_mnu_cfg_search', default=True):
        itemlist.append(item.clone( action='', title= '[B]Personalización búsquedas:[/B]', folder=False, text_color='moccasin' ))

        itemlist.append(item.clone( channel='search', action='show_help_parameters', title='[COLOR chocolate][B] - Qué ajustes tiene configurados para las búsquedas[/B][/COLOR]', thumbnail=config.get_thumb('help') ))

        itemlist.append(item.clone( channel='filters', action='no_actives', title=' - Qué canales no intervienen en las búsquedas (están desactivados)', thumbnail=config.get_thumb('stack') ))

        itemlist.append(item.clone( channel='filters', action='channels_status', title=' - Personalizar canales (Desactivar o Re-activar)',
                                    des_rea=True, thumbnail=config.get_thumb('stack') ))

        itemlist.append(item.clone( channel='filters', action='only_prefered', title=' - Qué canales tiene marcados como [COLOR gold]Preferidos[/COLOR]', thumbnail=config.get_thumb('stack') ))

        itemlist.append(item.clone( channel='filters', action='channels_status', title=' - Personalizar canales [COLOR gold]Preferidos[/COLOR] (Marcar o Des-marcar)',
                                    des_rea=False, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='', title= '[B]Personalizaciones especiales:[/B]', folder=False, text_color='teal' ))

    if config.get_setting('search_show_last', default=True):
        itemlist.append(item.clone( channel='actions', action = 'manto_textos', title= ' - Quitar los [COLOR red]Textos Memorizados[/COLOR] de las búsquedas',
                                    thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='filters', action = 'mainlist2', title = ' - [COLOR greenyellow][B]Efectuar las búsquedas Solo en determinados canales[/B][/COLOR]', thumbnail=config.get_thumb('stack') ))

    if item.extra == 'movies':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR deepskyblue]Películas[/B][/COLOR]',
                                    extra='movies', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_movies:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR deepskyblue]Películas[/B][/COLOR]',
                                        extra='movies', thumbnail=config.get_thumb('stack') ))

    elif item.extra == 'tvshows':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR hotpink]Series[/B][/COLOR]',
                                    extra='tvshows', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_tvshows:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR hotpink]Series[/B][/COLOR]',
                                        extra='tvshows', thumbnail=config.get_thumb('stack') ))

    elif item.extra == 'documentaries':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR cyan]Documentales[/B][/COLOR]',
                                    extra='documentaries', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_documentaries:
            itemlist.append(item.clone( channel='filters', action = 'channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR cyan]Documentales[/B][/COLOR]',
                                        extra='documentaries', thumbnail=config.get_thumb('stack') ))

    elif item.extra == 'torrents':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales [COLOR blue]Torrent[/COLOR][COLOR tomato]en las búsquedas para [COLOR yellow]Películas y/o Series[/B][/COLOR]',
                                    extra='torrents', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_mixed:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales [COLOR blue]Torrent[/COLOR][COLOR coral]excluidos en las búsquedas para Películas y/o Series[/B][/COLOR]',
                                        extra='torrents', thumbnail=config.get_thumb('stack') ))

    else:
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR green]Todos[/B][/COLOR]',
                                    extra='all', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_all:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR green]Todos[/B][/COLOR]',
                                        extra='all', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='', title= '[B]Configuración:[/B]', folder=False, text_color='goldenrod' ))

    itemlist.append(item.clone( channel='actions', title=' - [COLOR chocolate]Ajustes[/COLOR] categorías ([COLOR tan][B]Menú[/B][/COLOR], [COLOR red][B]Proxies[/B][/COLOR] y [COLOR yellow][B]Buscar[/B][/COLOR])', action = 'open_settings', thumbnail=config.get_thumb('settings') ))

    return itemlist


def _refresh_menu(item):
    platformtools.dialog_notification(config.__addon_name, 'Refrescando [B][COLOR %s]caché Menú[/COLOR][/B]' % color_exec)
    platformtools.itemlist_refresh()


def _marcar_canal(item):
    config.set_setting('status', item.estado, item.from_channel)

    if not item.module_search: _refresh_menu(item)


def _poner_no_searchable(item):
    platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR violet]Excluyendo de búsquedas[/COLOR][/B]')

    config.set_setting('no_searchable', True, item.from_channel)

    if not item.module_search: _refresh_menu(item)


def _quitar_no_searchable(item):
    platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR violet]Incluyendo en búsquedas[/COLOR][/B]')

    config.set_setting('no_searchable', False, item.from_channel)

    if not item.module_search: _refresh_menu(item)


def _channels_included(item):
    logger.info()

    from modules import filters

    item.extra = 'included'

    filters.channels_excluded(item)

def _channels_included_del(item):
    logger.info()

    from modules import filters

    item.extra = 'included'

    filters.channels_excluded_del(item)


def _channels_excluded(item):
    logger.info()

    from modules import filters

    item.extra = 'all'

    filters.channels_excluded(item)

def _channels_excluded_del(item):
    logger.info()

    from modules import filters

    item.extra = 'all'

    filters.channels_excluded_del(item)


def _dominios(item):
    logger.info()

    from modules import domains

    if item.from_channel == 'hdfull':
        from channels import hdfull

        item.channel = 'hdfull'
        hdfull.configurar_dominio(item)
    else:
        _dominio_memorizado(item)


def _dominio_vigente(item):
    from modules import domains

    item.desde_el_canal = True

    if item.from_channel == 'dontorrents': domains.last_domain_dontorrents(item)

    elif item.from_channel == 'hdfull': domains.last_domain_hdfull(item)

    elif item.from_channel == 'hdfullse': domains.last_domain_hdfullse(item)

    elif item.from_channel == 'playdede': domains.last_domain_playdede(item)

    else:
        domains.manto_domain_common(item, item.from_channel, item.from_channel.capitalize())


def _dominio_memorizado(item):
    from modules import domains

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
        platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Configuración No Permitida[/B][/COLOR]' % color_alert)


def _credenciales(item):
    if item.from_channel == 'hdfull': _credenciales_hdfull(item)

    elif item.from_channel == 'nextdede': _credenciales_nextdede(item)

    elif item.from_channel == 'playdede': _credenciales_playdede(item)

    else:
        platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Falta _Credenciales[/B][/COLOR]' % color_alert)


def _credenciales_hdfull(item):
    logger.info()

    from core import jsontools

    channel_json = 'hdfull.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name + ' - HdFull', el_canal + '[/COLOR][/B]')
       return

    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    from channels import hdfull

    item.channel = 'hdfull'

    if config.get_setting('hdfull_login', 'hdfull', default=False): hdfull.logout(item)

    hdfull.login('')

    _refresh_menu(item)


def _credenciales_nextdede(item):
    logger.info()

    from core import jsontools

    channel_json = 'nextdede.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name + ' - NextDede', el_canal + '[/COLOR][/B]')
       return

    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    from channels import nextdede

    item.channel = 'nextdede'

    if config.get_setting('nextdede_login', 'nextdede', default=False): nextdede.logout(item)

    nextdede.login('')

    _refresh_menu(item)


def _credenciales_playdede(item):
    logger.info()

    from core import jsontools

    channel_json = 'playdede.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name + ' - PlayDede', el_canal + '[/COLOR][/B]')
       return

    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    from channels import playdede

    item.channel = 'playdede'

    if config.get_setting('playdede_login', 'playdede', default=False): playdede.logout(item)

    playdede.login('')

    _refresh_menu(item)


def _proxies(item):
    logger.info()

    refrescar = True

    if item.from_channel == 'animefenix':
        from channels import animefenix
        item.channel = 'animefenix'
        animefenix.configurar_proxies(item)

        if config.get_setting('channel_animefenix_proxies') is None: refrescar = False

    elif item.from_channel == 'animeonline':
        from channels import animeonline
        item.channel = 'animeonline'
        animeonline.configurar_proxies(item)

        if config.get_setting('channel_animeonline_proxies') is None: refrescar = False

    elif item.from_channel == 'cinecalidad':
        from channels import cinecalidad
        item.channel = 'cinecalidad'
        cinecalidad.configurar_proxies(item)

        if config.get_setting('channel_cinecalidad_proxies') is None: refrescar = False

    elif item.from_channel == 'cinecalidadlol':
        from channels import cinecalidadlol
        item.channel = 'cinecalidadlol'
        cinecalidadlol.configurar_proxies(item)

        if config.get_setting('channel_cinecalidadlol_proxies') is None: refrescar = False

    elif item.from_channel == 'cinecalidadmx':
        from channels import cinecalidadmx
        item.channel = 'cinecalidadmx'
        cinecalidadmx.configurar_proxies(item)

        if config.get_setting('channel_cinecalidadmx_proxies') is None: refrescar = False

    elif item.from_channel == 'cliversite':
        from channels import cliversite
        item.channel = 'cliversite'
        cliversite.configurar_proxies(item)

        if config.get_setting('channel_cliversite_proxies') is None: refrescar = False

    elif item.from_channel == 'cuevana2':
        from channels import cuevana2
        item.channel = 'cuevana2'
        cuevana2.configurar_proxies(item)

        if config.get_setting('channel_cuevana2_proxies') is None: refrescar = False

    elif item.from_channel == 'cuevana2esp':
        from channels import cuevana2esp
        item.channel = 'cuevana2esp'
        cuevana2esp.configurar_proxies(item)

        if config.get_setting('channel_cuevana2esp_proxies') is None: refrescar = False

    elif item.from_channel == 'cuevana3video':
        from channels import cuevana3video
        item.channel = 'cuevana3video'
        cuevana3video.configurar_proxies(item)

        if config.get_setting('channel_cuevana3video_proxies') is None: refrescar = False

    elif item.from_channel == 'dilo':
        from channels import dilo
        item.channel = 'dilo'
        dilo.configurar_proxies(item)

        if config.get_setting('channel_dilo_proxies') is None: refrescar = False

    elif item.from_channel == 'divxtotal':
        from channels import divxtotal
        item.channel = 'divxtotal'
        divxtotal.configurar_proxies(item)

        if config.get_setting('channel_divxtotal_proxies') is None: refrescar = False

    elif item.from_channel == 'divxtotalcc':
        from channels import divxtotalcc
        item.channel = 'divxtotalcc'
        divxtotalcc.configurar_proxies(item)

        if config.get_setting('channel_divxtotalcc_proxies') is None: refrescar = False

    elif item.from_channel == 'dontorrents':
        from channels import dontorrents
        item.channel = 'dontorrents'
        dontorrents.configurar_proxies(item)

        if config.get_setting('channel_dontorrents_proxies') is None: refrescar = False

    elif item.from_channel == 'dontorrentsin':
        from channels import dontorrentsin
        item.channel = 'dontorrentsin'
        dontorrentsin.configurar_proxies(item)

        if config.get_setting('channel_dontorrentsin_proxies') is None: refrescar = False

    elif item.from_channel == 'elifilms':
        from channels import elifilms
        item.channel = 'elifilms'
        elifilms.configurar_proxies(item)

        if config.get_setting('channel_elifilms_proxies') is None: refrescar = False

    elif item.from_channel == 'ennovelas':
        from channels import ennovelas
        item.channel = 'ennovelas'
        ennovelas.configurar_proxies(item)

        if config.get_setting('channel_ennovelas_proxies') is None: refrescar = False

    elif item.from_channel == 'entrepeliculasyseries':
        from channels import entrepeliculasyseries
        item.channel = 'entrepeliculasyseries'
        entrepeliculasyseries.configurar_proxies(item)

        if config.get_setting('channel_entrepeliculasyseries_proxies') is None: refrescar = False

    elif item.from_channel == 'estrenoscinesaa':
        from channels import estrenoscinesaa
        item.channel = 'estrenoscinesaa'
        estrenoscinesaa.configurar_proxies(item)

        if config.get_setting('channel_estrenoscinesaa_proxies') is None: refrescar = False

    elif item.from_channel == 'gnula':
        from channels import gnula
        item.channel = 'gnula'
        gnula.configurar_proxies(item)

        if config.get_setting('channel_gnula_proxies') is None: refrescar = False

    elif item.from_channel == 'gnula24':
        from channels import gnula24
        item.channel = 'gnula24'
        gnula24.configurar_proxies(item)

        if config.get_setting('channel_gnula24_proxies') is None: refrescar = False

    elif item.from_channel == 'gnula24h':
        from channels import gnula24h
        item.channel = 'gnula24h'
        gnula24h.configurar_proxies(item)

        if config.get_setting('channel_gnula24h_proxies') is None: refrescar = False

    elif item.from_channel == 'grantorrent':
        from channels import grantorrent
        item.channel = 'grantorrent'
        grantorrent.configurar_proxies(item)

        if config.get_setting('channel_grantorrent_proxies') is None: refrescar = False

    elif item.from_channel == 'grantorrents':
        from channels import grantorrents
        item.channel = 'grantorrents'
        grantorrents.configurar_proxies(item)

        if config.get_setting('channel_grantorrents_proxies') is None: refrescar = False

    elif item.from_channel == 'hdfull':
        from channels import hdfull
        item.channel = 'hdfull'
        hdfull.configurar_proxies(item)

        if config.get_setting('channel_hdfull_proxies') is None: refrescar = False

    elif item.from_channel == 'hdfullse':
        from channels import hdfullse
        item.channel = 'hdfullse'
        hdfullse.configurar_proxies(item)

        if config.get_setting('channel_hdfullse_proxies') is None: refrescar = False

    elif item.from_channel == 'henaojara':
        from channels import henaojara
        item.channel = 'henaojara'
        henaojara.configurar_proxies(item)

        if config.get_setting('channel_henaojara_proxies') is None: refrescar = False

    elif item.from_channel == 'homecine':
        from channels import homecine
        item.channel = 'homecine'
        homecine.configurar_proxies(item)

        if config.get_setting('channel_homecine_proxies') is None: refrescar = False

    elif item.from_channel == 'jkanime':
        from channels import jkanime
        item.channel = 'jkanime'
        jkanime.configurar_proxies(item)

        if config.get_setting('channel_jkanime_proxies') is None: refrescar = False

    elif item.from_channel == 'lilatorrent':
        from channels import lilatorrent
        item.channel = 'lilatorrent'
        lilatorrent.configurar_proxies(item)

        if config.get_setting('channel_lilatorrent_proxies') is None: refrescar = False

    elif item.from_channel == 'megaserie':
        from channels import megaserie
        item.channel = 'megaserie'
        megaserie.configurar_proxies(item)

        if config.get_setting('channel_megaserie_proxies') is None: refrescar = False

    elif item.from_channel == 'mejortorrentapp':
        from channels import mejortorrentapp
        item.channel = 'mejortorrentapp'
        mejortorrentapp.configurar_proxies(item)

        if config.get_setting('channel_mejortorrentapp_proxies') is None: refrescar = False

    elif item.from_channel == 'mejortorrentnz':
        from channels import mejortorrentnz
        item.channel = 'mejortorrentnz'
        mejortorrentnz.configurar_proxies(item)

        if config.get_setting('channel_mejortorrentnz_proxies') is None: refrescar = False

    elif item.from_channel == 'mirapeliculas':
        from channels import mirapeliculas
        item.channel = 'mirapeliculas'
        mirapeliculas.configurar_proxies(item)

        if config.get_setting('channel_mirapeliculas_proxies') is None: refrescar = False

    elif item.from_channel == 'naranjatorrent':
        from channels import naranjatorrent
        item.channel = 'naranjatorrent'
        naranjatorrent.configurar_proxies(item)

        if config.get_setting('channel_naranjatorrent_proxies') is None: refrescar = False

    elif item.from_channel == 'peliculaspro':
        from channels import peliculaspro
        item.channel = 'peliculaspro'
        peliculaspro.configurar_proxies(item)

        if config.get_setting('channel_peliculaspro_proxies') is None: refrescar = False

    elif item.from_channel == 'pelisforte':
        from channels import pelisforte
        item.channel = 'pelisforte'
        pelisforte.configurar_proxies(item)

        if config.get_setting('channel_pelisforte_proxies') is None: refrescar = False

    elif item.from_channel == 'pelishouse':
        from channels import pelishouse
        item.channel = 'pelishouse'
        pelishouse.configurar_proxies(item)

        if config.get_setting('channel_pelishouse_proxies') is None: refrescar = False

    elif item.from_channel == 'pelismaraton':
        from channels import pelismaraton
        item.channel = 'pelismaraton'
        pelismaraton.configurar_proxies(item)

        if config.get_setting('channel_pelismaraton_proxies') is None: refrescar = False

    elif item.from_channel == 'pelispanda':
        from channels import pelispanda
        item.channel = 'pelispanda'
        pelispanda.configurar_proxies(item)

        if config.get_setting('channel_pelispanda_proxies') is None: refrescar = False

    elif item.from_channel == 'pelispedia':
        from channels import pelispedia
        item.channel = 'pelispedia'
        pelispedia.configurar_proxies(item)

        if config.get_setting('channel_pelispedia_proxies') is None: refrescar = False

    elif item.from_channel == 'pelisplus':
        from channels import pelisplus
        item.channel = 'pelisplus'
        pelisplus.configurar_proxies(item)

        if config.get_setting('channel_pelisplus_proxies') is None: refrescar = False

    elif item.from_channel == 'pelisplushd':
        from channels import pelisplushd
        item.channel = 'pelisplushd'
        pelisplushd.configurar_proxies(item)

        if config.get_setting('channel_pelisplushd_proxies') is None: refrescar = False

    elif item.from_channel == 'pelisplushdnz':
        from channels import pelisplushdnz
        item.channel = 'pelisplushdnz'
        pelisplushdnz.configurar_proxies(item)

        if config.get_setting('channel_pelisplushdnz_proxies') is None: refrescar = False

    elif item.from_channel == 'pelispluslat':
        from channels import pelispluslat
        item.channel = 'pelispluslat'
        pelispluslat.configurar_proxies(item)

        if config.get_setting('channel_pelispluslat_proxies') is None: refrescar = False

    elif item.from_channel == 'pelisxd':
        from channels import pelisxd
        item.channel = 'pelisxd'
        pelisxd.configurar_proxies(item)

        if config.get_setting('channel_pelisxd_proxies') is None: refrescar = False

    elif item.from_channel == 'pelisyseries':
        from channels import pelisyseries
        item.channel = 'pelisyseries'
        pelisyseries.configurar_proxies(item)

        if config.get_setting('channel_pelisyseries_proxies') is None: refrescar = False

    elif item.from_channel == 'pepecinetop':
        from channels import pepecinetop
        item.channel = 'pepecinetop'
        pepecinetop.configurar_proxies(item)

        if config.get_setting('channel_pepecinetop_proxies') is None: refrescar = False

    elif item.from_channel == 'playdede':
        from channels import playdede
        item.channel = 'playdede'
        playdede.configurar_proxies(item)

        if config.get_setting('channel_playdede_proxies') is None: refrescar = False

    elif item.from_channel == 'playview':
        from channels import playview
        item.channel = 'playview'
        playview.configurar_proxies(item)

        if config.get_setting('channel_playview_proxies') is None: refrescar = False

    elif item.from_channel == 'reinventorrent':
        from channels import reinventorrent
        item.channel = 'reinventorrent'
        reinventorrent.configurar_proxies(item)

        if config.get_setting('channel_reinventorrent_proxies') is None: refrescar = False

    elif item.from_channel == 'rojotorrent':
        from channels import rojotorrent
        item.channel = 'rojotorrent'
        rojotorrent.configurar_proxies(item)

        if config.get_setting('channel_rojotorrent_proxies') is None: refrescar = False

    elif item.from_channel == 'series24':
        from channels import series24
        item.channel = 'series24'
        series24.configurar_proxies(item)

        if config.get_setting('channel_series24_proxies') is None: refrescar = False

    elif item.from_channel == 'seriesmovil':
        from channels import seriesmovil
        item.channel = 'seriesmovil'
        seriesmovil.configurar_proxies(item)

        if config.get_setting('channel_seriesmovil_proxies') is None: refrescar = False

    elif item.from_channel == 'seriespapayato':
        from channels import seriespapayato
        item.channel = 'seriespapayato'
        seriespapayato.configurar_proxies(item)

        if config.get_setting('channel_seriespapayato_proxies') is None: refrescar = False

    elif item.from_channel == 'seriespapayaxyz':
        from channels import seriespapayaxyz
        item.channel = 'seriespapayaxyz'
        seriespapayaxyz.configurar_proxies(item)

        if config.get_setting('channel_seriespapayaxyz_proxies') is None: refrescar = False

    elif item.from_channel == 'seriesyonkis':
        from channels import seriesyonkis
        item.channel = 'seriesyonkis'
        seriesyonkis.configurar_proxies(item)

        if config.get_setting('channel_seriesyonkis_proxies') is None: refrescar = False

    elif item.from_channel == 'srnovelas':
        from channels import srnovelas
        item.channel = 'srnovelas'
        srnovelas.configurar_proxies(item)

        if config.get_setting('channel_srnovelas_proxies') is None: refrescar = False

    elif item.from_channel == 'subtorrents':
        from channels import subtorrents
        item.channel = 'subtorrents'
        subtorrents.configurar_proxies(item)

        if config.get_setting('channel_subtorrents_proxies') is None: refrescar = False

    elif item.from_channel == 'todotorrents':
        from channels import todotorrents
        item.channel = 'todotorrents'
        todotorrents.configurar_proxies(item)

        if config.get_setting('channel_todotorrents_proxies') is None: refrescar = False

    elif item.from_channel == 'tomadivx':
        from channels import tomadivx
        item.channel = 'tomadivx'
        tomadivx.configurar_proxies(item)

        if config.get_setting('channel_tomadivx_proxies') is None: refrescar = False

    elif item.from_channel == 'torrentpelis':
        from channels import torrentpelis
        item.channel = 'torrentpelis'
        torrentpelis.configurar_proxies(item)

        if config.get_setting('channel_torrentpelis_proxies') is None: refrescar = False

    elif item.from_channel == 'tupelihd':
        from channels import tupelihd
        item.channel = 'tupelihd'
        tupelihd.configurar_proxies(item)

        if config.get_setting('channel_tupelihd_proxies') is None: refrescar = False

    elif item.from_channel == 'verdetorrent':
        from channels import verdetorrent
        item.channel = 'verdetorrent'
        verdetorrent.configurar_proxies(item)

        if config.get_setting('channel_verdetorrent_proxies') is None: refrescar = False

    elif item.from_channel == 'yestorrent':
        from channels import yestorrent
        item.channel = 'yestorrent'
        yestorrent.configurar_proxies(item)

        if config.get_setting('channel_yestorrent_proxies') is None: refrescar = False

    else:
        platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Falta _Proxies[/B][/COLOR]' % color_alert)
        refrescar = False

    channels_unsatisfactory = config.get_setting('developer_test_channels', default='')
    if channels_unsatisfactory == 'unsatisfactory': refrescar = False

    if item.module_search: refrescar = False

    if refrescar: _refresh_menu(item)


def _search_new_proxies(item):
    if item.channels_new_proxies:
        if platformtools.dialog_yesno(config.__addon_name, '[COLOR yellow][B]Solo se tendrán en cuenta para las próximas búsquedas[/B][/COLOR]','[COLOR red][B]¿ Desea efectuar una nueva búsqueda de proxies en Todos esos canales ?[/B][/COLOR]'):
            for channel in item.channels_new_proxies:
                item.from_channel = channel
                item.module_search = True
                _proxies(item)


def _quitar_proxies(item):
    platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR red]Quitando los proxies[/COLOR][/B]')

    config.set_setting('proxies', '', item.from_channel)
    _refresh_menu(item)


def _test_webs(item):
    platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR violet]Test web canal[/COLOR][/B]')

    config.set_setting('developer_test_channels', '')
    config.set_setting('developer_test_servers', '')

    config.set_setting('user_test_channel', '')

    from modules import tester

    try:
        tester.test_channel(item.from_channel)
    except:
        platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)
