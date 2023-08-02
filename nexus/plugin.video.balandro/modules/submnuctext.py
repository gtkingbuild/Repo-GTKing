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


def submnu_genres(item):
    logger.info()
    itemlist = []

    if config.get_setting('mnu_search_proxy_channels', default=False):
        itemlist.append(item.clone( action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]', context=context_proxy_channels,
                                    only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

    itemlist.append(item.clone( channel='generos', action='mainlist', title='[B]Géneros[/B]', thumbnail=config.get_thumb('genres'), text_color='moccasin' ))

    itemlist.append(item.clone( action='', title= '[B]Canales que podrían necesitar Nuevamente [COLOR red]Proxies[/COLOR]:[/B]', text_color='magenta' ))

    itemlist.append(item.clone( channel='groups', action='ch_generos', title=' - Canales con Películas', group = 'generos', extra = 'movies',
                                thumbnail=config.get_thumb('movie'), text_color='deepskyblue' ))

    itemlist.append(item.clone( channel='groups', action='ch_generos', title=' - Canales con Series', group = 'generos', extra = 'tvshows',
                                thumbnail=config.get_thumb('tvshow'), text_color='hotpink' ))

    return itemlist


def submnu_special(item):
    logger.info()
    itemlist = []

    if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'movies':
        itemlist.append(item.clone( action='', title = '[COLOR deepskyblue][B]Películas[COLOR goldenrod] Recomendadas:[/B][/COLOR]',
                                    thumbnail=config.get_thumb('movie'), folder=False ))

        itemlist.append(item.clone( channel='cinedeantes', action='list_all', title=' - Las joyas del cine clásico',
                                    url = 'https://cinedeantes2.weebly.com/joyas-del-cine.html',
                                    thumbnail=config.get_thumb('bestmovies'),search_type = 'movie' ))

        itemlist.append(item.clone( channel='adnstream', action='_ayer_y_siempre', title=' - Las mejores del cine de ayer y siempre',
                                    thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(item.clone( channel='zoowomaniacos', action='_culto', title=' - Las mejores del cine de culto',
                                    thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(item.clone( channel='cinequinqui', action='list_all', title=' - Las mejores del cine quinqui',
                                    url = 'https://cinekinkihd.freesite.host/movies/',
                                    group = 'best', thumbnail=config.get_thumb('bestmovies'),search_type = 'movie' ))

        itemlist.append(item.clone( channel='zoowomaniacos', action='_las1001', title=' - Las 1001 que hay que ver',
                                    thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

    if config.get_setting('search_extra_main', default=False):
        if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'movies' or item.extra == 'tvshows':
            itemlist.append(item.clone( action='', title = '[COLOR yellow][B]Películas y Series[/COLOR] búsquedas de Personas en TMDB:[/B]',
                                         thumbnail=thumb_tmdb, folder=False, text_color='pink' ))

            itemlist.append(item.clone( channel='tmdblists', action='personas', title= ' - Buscar [COLOR aquamarine]intérprete[/COLOR] ...',
                                        search_type='cast', thumbnail=config.get_thumb('search') ))

            itemlist.append(item.clone( channel='tmdblists', action='personas', title= ' - Buscar [COLOR springgreen]dirección[/COLOR] ...',
                                        search_type='crew', thumbnail=config.get_thumb('search') ))

            itemlist.append(item.clone( action='', title = '[COLOR yellow][B]Películas y Series[/COLOR] búsquedas de Personas en Filmaffinity:[/B]',
                                        thumbnail=thumb_filmaffinity, folder=False, text_color='pink' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='listas', search_type='person', stype='cast', title=' - Buscar [COLOR aquamarine]intérprete[/COLOR] ...',
                                        thumbnail=config.get_thumb('search')))

            itemlist.append(item.clone( channel='filmaffinitylists', action='listas', search_type='person', stype='director', title=' - Buscar [COLOR springgreen]dirección[/COLOR] ...',
                                        thumbnail=config.get_thumb('search')))

        if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'movies' or item.extra == 'torrents':
            itemlist.append(item.clone( action='', title='[COLOR deepskyblue][B]Películas[/COLOR] búsquedas en TMDB ó Filmaffinity:[/B]',
                                        thumbnail=config.get_thumb('movie'), folder=False, text_color='pink' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - En cartelera',
                                        extra='now_playing', thumbnail=config.get_thumb('movie'), search_type = 'movie' ))

            if not current_month == 4:
                itemlist.append(item.clone( channel='filmaffinitylists', action='_oscars', title=' - Premios Oscar', thumbnail=config.get_thumb('oscars'), search_type = 'movie' ))

                itemlist.append(item.clone( channel='filmaffinitylists', action='_sagas', title=' - Sagas y colecciones', thumbnail=config.get_thumb('bestsagas'), search_type = 'movie' ))

                itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - Más populares', extra='popular', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

                itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - Más valoradas', extra='top_rated', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

                itemlist.append(item.clone( channel='filmaffinitylists', action='_bestmovies', title=' - Recomendadas', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

                itemlist.append(item.clone( channel='tmdblists', action='networks', title=' - Por productora', thumbnail=config.get_thumb('movie'), search_type = 'movie' ))

                itemlist.append(item.clone( channel='tmdblists', action='generos', title=' - Por género', thumbnail=config.get_thumb('listgenres'), search_type = 'movie' ))

                itemlist.append(item.clone( channel='tmdblists', action='anios', title=' - Por año', thumbnail=config.get_thumb('listyears'), search_type = 'movie' ))

        if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'tvshows' or item.extra == 'torrents':
            itemlist.append(item.clone( action='', title = '[COLOR hotpink][B]Series[/COLOR] búsquedas en TMDB ó Filmaffinity:[/B]',
                                        thumbnail=config.get_thumb('tvshow'), folder=False, text_color='pink' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - En emisión', extra='on_the_air', thumbnail=config.get_thumb('tvshow'), search_type = 'tvshow' ))

            if not current_month == 10:
                itemlist.append(item.clone( channel='filmaffinitylists', action='_emmys', title=' - Premios Emmy', thumbnail=config.get_thumb('emmys'),
                                            origen='mnu_esp', search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - Más populares', extra='popular', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='tmdblists', action='listado', title= ' - Más valoradas', extra='top_rated', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_besttvshows', title=' - Recomendadas', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='tmdblists', action='generos', title=' - Por género', thumbnail=config.get_thumb('listgenres'), search_type = 'tvshow' ))

            itemlist.append(item.clone( channel='tmdblists', action='anios', title=' - Por año', thumbnail=config.get_thumb('listyears'), search_type = 'tvshow' ))

        if not item.extra == 'documentaries':
            itemlist.append(item.clone( action='', title = '[COLOR teal][B]Películas y Series[/COLOR] búsquedas en Filmaffinity:[/B]',
                                        thumbnail=thumb_filmaffinity, folder=False, text_color='pink' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='plataformas', title=' - Por plataforma', thumbnail=config.get_thumb('booklet'), search_type = 'all' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_genres', title=' - Por género', thumbnail=config.get_thumb('listgenres'), search_type = 'all' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='paises', title=' - Por país', thumbnail=thumb_filmaffinity, search_type = 'all' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_years', title=' - Por año', thumbnail=config.get_thumb('listyears'), search_type = 'all' ))

            itemlist.append(item.clone( channel='filmaffinitylists', action='_themes', title=' - Por tema', thumbnail=config.get_thumb('listthemes'), search_type = 'all' ))

        if not item.no_docs:
            if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'documentaries' or item.extra == 'torrents':
                itemlist.append(item.clone( action='', title = '[COLOR cyan][B]Documentales[/COLOR] búsquedas en Filmaffinity:[/B]',
                                            thumbnail=thumb_filmaffinity, folder=False, text_color='pink' ))

            if config.get_setting('mnu_documentales', default=True):
                itemlist.append(item.clone( channel='filmaffinitylists', action='_bestdocumentaries', title=' - Los Mejores',
                                            thumbnail=config.get_thumb('bestdocumentaries'), search_type = 'all' ))

    return itemlist


def submnu_search(item):
    logger.info()
    itemlist = []

    if config.get_setting('search_extra_proxies', default=True):
        itemlist.append(item.clone( action='', title='[B]Búsquedas en canales con Proxies:[/B]', folder=False, text_color='red' ))

        itemlist.append(item.clone( channel='filters', title=' - Qué canales pueden usar proxies', action='with_proxies',
                                    thumbnail=config.get_thumb('stack'), new_proxies=True ))

        if config.get_setting('memorize_channels_proxies', default=True):
            itemlist.append(item.clone( channel='filters', title=  ' - Qué [COLOR red]canales[/COLOR] tiene con proxies memorizados', action='with_proxies',
                                        thumbnail=config.get_thumb('stack'), new_proxies=True, memo_proxies=True, test_proxies=True ))

        itemlist.append(item.clone( channel='actions', title= ' - Quitar los proxies en los canales [COLOR red](que los tengan memorizados)[/COLOR]',
                                    action = 'manto_proxies', thumbnail=config.get_thumb('flame') ))

        itemlist.append(item.clone( channel='proxysearch', title=' - Configurar proxies a usar [COLOR plum](en los canales que los necesiten)[/COLOR]',
                                    action='proxysearch_all', thumbnail=config.get_thumb('flame') ))

        itemlist.append(item.clone( channel='helper', action='show_help_proxies', title= ' - [COLOR green][B]Información Uso de proxies[/B][/COLOR]' ))

        if config.get_setting('proxysearch_excludes', default=''):
            itemlist.append(item.clone( channel='proxysearch', title=' - Anular los canales excluidos de Configurar proxies a usar',
                                        action='channels_proxysearch_del', thumbnail=config.get_thumb('flame'), text_color='coral' ))

    if item.only_options_proxies: return itemlist

    itemlist.append(item.clone( action='', title= '[B]Personalización búsquedas:[/B]', folder=False, text_color='moccasin' ))

    itemlist.append(item.clone( channel='search', action='show_help_parameters', title='[COLOR chocolate][B] - Qué ajustes tiene configurados para las búsquedas[/B][/COLOR]',
                                thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( channel='filters', action='no_actives', title=' - Qué canales no intervienen en las búsquedas (están desactivados)',
                                thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='filters', action='channels_status', title=' - Personalizar canales (Desactivar o Re-activar)',
                                des_rea=True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='filters', action='only_prefered', title=' - Qué canales tiene marcados como preferidos',
                                thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='filters', action='channels_status', title=' - Personalizar canales Preferidos (Marcar o Des-marcar)',
                                des_rea=False, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='filters', title = ' - [COLOR greenyellow][B]Efectuar las búsquedas Solo en determinados canales[/B][/COLOR]',
                                action = 'mainlist2', thumbnail=config.get_thumb('stack') ))

    if item.extra == 'movies':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR deepskyblue]Películas[/B][/COLOR]',
                                    extra='movies', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_movies:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR deepskyblue]Películas[/B][/COLOR]',
                                        extra='movies' ))

    elif item.extra == 'tvshows':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR hotpink]Series[/B][/COLOR]',
                                    extra='tvshows', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_tvshows:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR hotpink]Series[/B][/COLOR]',
                                        extra='tvshows' ))

    elif item.extra == 'documentaries':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR cyan]Documentales[/B][/COLOR]',
                                    extra='documentaries', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_documentaries:
            itemlist.append(item.clone( channel='filters', action = 'channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR cyan]Documentales[/B][/COLOR]',
                                        extra='documentaries' ))

    elif item.extra == 'torrents':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales [COLOR blue]Torrent[/COLOR][COLOR tomato]en las búsquedas para [COLOR yellow]Películas y/o Series[/B][/COLOR]',
                                    extra='torrents', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_mixed:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales [COLOR blue]Torrent[/COLOR][COLOR coral]excluidos en las búsquedas para Películas y/o Series[/B][/COLOR]',
                                        extra='torrents' ))

    else:
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR green]Todos[/B][/COLOR]',
                                    extra='all', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_all:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR green]Todos[/B][/COLOR]',
                                        extra='all' ))

    itemlist.append(item.clone( action='', title= '[B]Configuración:[/B]', folder=False, text_color='goldenrod' ))

    itemlist.append(item.clone( channel='actions', title=' - [COLOR chocolate]Ajustes[/COLOR] categorías ([COLOR red][B]Proxies[/B][/COLOR] y [COLOR yellow][B]Buscar[/B][/COLOR])', action = 'open_settings',
                                thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='search', action='show_help', title='[COLOR green][B]Información búsquedas[/B][/COLOR]',
                                thumbnail=config.get_thumb('help') ))

    return itemlist


def _refresh_menu(item):
    platformtools.dialog_notification(config.__addon_name, 'Refrescando [B][COLOR %s]caché Menú[/COLOR][/B]' % color_exec)
    platformtools.itemlist_refresh()


def _marcar_canal(item):
    config.set_setting('status', item.estado, item.from_channel)
    _refresh_menu(item)

def _poner_no_searchable(item):
    platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR violet]Excluyendo de búsquedas[/COLOR][/B]')

    config.set_setting('no_searchable', True, item.from_channel)
    _refresh_menu(item)

def _quitar_no_searchable(item):
    platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR violet]Incluyendo en búsquedas[/COLOR][/B]')

    config.set_setting('no_searchable', False, item.from_channel)
    _refresh_menu(item)


def _channels_included(item):
    logger.info()

    from modules import filters

    item.extra = 'included'

    filters.channels_excluded(item)
    _refresh_menu(item)

def _channels_included_del(item):
    logger.info()

    from modules import filters

    item.extra = 'included'

    filters.channels_excluded_del(item)
    _refresh_menu(item)


def _channels_excluded(item):
    logger.info()

    from modules import filters

    item.extra = 'all'

    filters.channels_excluded(item)
    _refresh_menu(item)

def _channels_excluded_del(item):
    logger.info()

    from modules import filters

    item.extra = 'all'

    filters.channels_excluded_del(item)
    _refresh_menu(item)


def _dominios(item):
    logger.info()

    from modules import domains

    if item.from_channel == 'hdfull':
        from channels import hdfull
        item.channel = 'hdfull'
        hdfull.configurar_dominio(item)

    elif item.from_channel == 'animefenix':
        domains.manto_domain_animefenix(item)

    elif item.from_channel == 'animeflv':
        domains.manto_domain_animeflv(item)

    elif item.from_channel == 'caricaturashd':
        domains.manto_domain_caricaturashd(item)

    elif item.from_channel == 'cinecalidad':
        domains.manto_domain_cinecalidad(item)

    elif item.from_channel == 'cinecalidadla':
        domains.manto_domain_cinecalidadla(item)

    elif item.from_channel == 'cinecalidadlol':
        domains.manto_domain_cinecalidadlol(item)

    elif item.from_channel == 'cinetux':
        domains.manto_domain_cinetux(item)

    elif item.from_channel == 'cuevana3':
        domains.manto_domain_cuevana3(item)

    elif item.from_channel == 'cuevana3video':
        domains.manto_domain_cuevana3video(item)

    elif item.from_channel == 'divxtotal':
        domains.manto_domain_divxtotal(item)

    elif item.from_channel == 'dontorrents':
        domains.manto_domain_dontorrents(item)

    elif item.from_channel == 'elifilms':
        domains.manto_domain_elifilms(item)

    elif item.from_channel == 'elitetorrent':
        domains.manto_domain_elitetorrent(item)

    elif item.from_channel == 'entrepeliculasyseries':
        domains.manto_domain_entrepeliculasyseries(item)

    elif item.from_channel == 'gnula24':
        domains.manto_domain_gnula24(item)

    elif item.from_channel == 'grantorrent':
        domains.manto_domain_grantorrent(item)

    elif item.from_channel == 'grantorrents':
        domains.manto_domain_grantorrents(item)

    elif item.from_channel == 'hdfull':
        domains.manto_domain_hdfull(item)

    elif item.from_channel == 'hdfullse':
        domains.manto_domain_hdfullse(item)

    elif item.from_channel == 'inkapelis':
        domains.manto_domain_inkapelis(item)

    elif item.from_channel == 'kindor':
        domains.manto_domain_kindor(item)

    elif item.from_channel == 'pelis28':
        domains.manto_domain_pelis28(item)

    elif item.from_channel == 'pelisflix':
        domains.manto_domain_pelisflix(item)

    elif item.from_channel == 'pelishouse':
        domains.manto_domain_pelishouse(item)

    elif item.from_channel == 'pelismaraton':
        domains.manto_domain_pelismaraton(item)

    elif item.from_channel == 'pelispedia':
        domains.manto_domain_pelispedia(item)

    elif item.from_channel == 'pelispediaws':
        domains.manto_domain_pelispediaws(item)

    elif item.from_channel == 'pelisplus':
        domains.manto_domain_pelisplus(item)

    elif item.from_channel == 'pelisplushd':
        domains.manto_domain_pelisplushd(item)

    elif item.from_channel == 'pelisplushdlat':
        domains.manto_domain_pelisplushdlat(item)

    elif item.from_channel == 'playdede':
        domains.manto_domain_playdede(item)

    elif item.from_channel == 'repelis24':
        domains.manto_domain_repelis24(item)

    elif item.from_channel == 'repelishd':
        domains.manto_domain_repelishd(item)

    elif item.from_channel == 'series24':
        domains.manto_domain_series24(item)

    elif item.from_channel == 'seriesanimadas':
        domains.manto_domain_seriesanimadas(item)

    elif item.from_channel == 'seriesyonkis':
        domains.manto_domain_seriesyonkis(item)

    elif item.from_channel == 'subtorrents':
        domains.manto_domain_subtorrents(item)

    elif item.from_channel == 'torrentdivx':
        domains.manto_domain_torrentdivx(item)

    elif item.from_channel == 'torrentpelis':
        domains.manto_domain_torrentpelis(item)

    else:
        platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Configuración No Permitida[/B][/COLOR]' % color_alert)


def _dominio_vigente(item):
    from modules import domains

    if item.from_channel == 'hdfull':
        item.desde_el_canal = True
        domains.last_domain_hdfull(item)

    elif item.from_channel == 'hdfullse':
        item.desde_el_canal = True
        domains.last_domain_hdfullse(item)

    elif item.from_channel == 'dontorrents':
        item.desde_el_canal = True
        domains.last_domain_dontorrents(item)

    else:
        platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Efectue Test Web, la comprobación No está permitida[/B][/COLOR]' % color_alert)


def _dominio_memorizado(item):
    from modules import domains

    if item.from_channel == 'animefenix':
        domains.manto_domain_animefenix(item)

    elif item.from_channel == 'animeflv':
        domains.manto_domain_animeflv(item)

    elif item.from_channel == 'caricaturashd':
        domains.manto_domain_caricaturashd(item)

    elif item.from_channel == 'cinecalidad':
        domains.manto_domain_cinecalidad(item)

    elif item.from_channel == 'cinecalidadla':
        domains.manto_domain_cinecalidadla(item)

    elif item.from_channel == 'cinecalidadlol':
        domains.manto_domain_cinecalidadlol(item)

    elif item.from_channel == 'cinetux':
        domains.manto_domain_cinetux(item)

    elif item.from_channel == 'cuevana3':
        domains.manto_domain_cuevana3(item)

    elif item.from_channel == 'cuevana3video':
        domains.manto_domain_cuevana3video(item)

    elif item.from_channel == 'divxtotal':
        domains.manto_domain_divxtotal(item)

    elif item.from_channel == 'dontorrents':
        domains.manto_domain_dontorrents(item)

    elif item.from_channel == 'elifilms':
        domains.manto_domain_elifilms(item)

    elif item.from_channel == 'elitetorrent':
        domains.manto_domain_elitetorrent(item)

    elif item.from_channel == 'entrepeliculasyseries':
        domains.manto_domain_entrepeliculasyseries(item)

    elif item.from_channel == 'gnula24':
        domains.manto_domain_gnula24(item)

    elif item.from_channel == 'grantorrent':
        domains.manto_domain_grantorrent(item)

    elif item.from_channel == 'grantorrents':
        domains.manto_domain_grantorrents(item)

    elif item.from_channel == 'hdfull':
        domains.manto_domain_hdfull(item)

    elif item.from_channel == 'hdfullse':
        domains.manto_domain_hdfullse(item)

    elif item.from_channel == 'inkapelis':
        domains.manto_domain_inkapelis(item)

    elif item.from_channel == 'kindor':
        domains.manto_domain_kindor(item)

    elif item.from_channel == 'pelis28':
        domains.manto_domain_pelis28(item)

    elif item.from_channel == 'pelisflix':
        domains.manto_domain_pelisflix(item)

    elif item.from_channel == 'pelishouse':
        domains.manto_domain_pelishouse(item)

    elif item.from_channel == 'pelismaraton':
        domains.manto_domain_pelismaraton(item)

    elif item.from_channel == 'pelispediaws':
        domains.manto_domain_pelispediaws(item)

    elif item.from_channel == 'pelispedia':
        domains.manto_domain_pelispedia(item)

    elif item.from_channel == 'pelisplus':
        domains.manto_domain_pelisplus(item)

    elif item.from_channel == 'pelisplushd':
        domains.manto_domain_pelisplushd(item)

    elif item.from_channel == 'pelisplushdlat':
        domains.manto_domain_pelisplushdlat(item)

    elif item.from_channel == 'playdede':
        domains.manto_domain_playdede(item)

    elif item.from_channel == 'repelis24':
        domains.manto_domain_repelis24(item)

    elif item.from_channel == 'repelishd':
        domains.manto_domain_repelishd(item)

    elif item.from_channel == 'series24':
        domains.manto_domain_series24(item)

    elif item.from_channel == 'seriesanimadas':
        domains.manto_domain_seriesanimadas(item)

    elif item.from_channel == 'seriesyonkis':
        domains.manto_domain_seriesyonkis(item)

    elif item.from_channel == 'subtorrents':
        domains.manto_domain_subtorrents(item)

    elif item.from_channel == 'torrentdivx':
        domains.manto_domain_torrentdivx(item)

    elif item.from_channel == 'torrentpelis':
        domains.manto_domain_torrentpelis(item)

    else:
        platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Falta _DomainMemorizado[/B][/COLOR]' % color_alert)


def _credenciales(item):
    if item.from_channel == 'hdfull':
        _credenciales_hdfull(item)

    elif item.from_channel == 'playdede':
        _credenciales_playdede(item)

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

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] HdFull') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    from channels import hdfull

    item.channel = 'hdfull'

    if config.get_setting('hdfull_login', 'hdfull', default=False): hdfull.logout(item)

    hdfull.login('')

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

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] PlayDede') % color_avis
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

    elif item.from_channel == 'animeonline':
        from channels import animeonline
        item.channel = 'animeonline'
        animeonline.configurar_proxies(item)

    elif item.from_channel == 'cinecalidad':
        from channels import cinecalidad
        item.channel = 'cinecalidad'
        cinecalidad.configurar_proxies(item)

    elif item.from_channel == 'cinetux':
        from channels import cinetux
        item.channel = 'cinetux'
        cinetux.configurar_proxies(item)

    elif item.from_channel == 'cliversite':
        from channels import cliversite
        item.channel = 'cliversite'
        cliversite.configurar_proxies(item)

    elif item.from_channel == 'cuevana2esp':
        from channels import cuevana2esp
        item.channel = 'cuevana2esp'
        cuevana2esp.configurar_proxies(item)

    elif item.from_channel == 'cuevana3':
        from channels import cuevana3
        item.channel = 'cuevana3'
        cuevana3.configurar_proxies(item)

    elif item.from_channel == 'cuevana3video':
        from channels import cuevana3video
        item.channel = 'cuevana3video'
        cuevana3video.configurar_proxies(item)

    elif item.from_channel == 'dilo':
        from channels import dilo
        item.channel = 'dilo'
        dilo.configurar_proxies(item)

    elif item.from_channel == 'divxtotal':
        from channels import divxtotal
        item.channel = 'divxtotal'
        divxtotal.configurar_proxies(item)

    elif item.from_channel == 'divxtotalcc':
        from channels import divxtotalcc
        item.channel = 'divxtotalcc'
        divxtotalcc.configurar_proxies(item)

    elif item.from_channel == 'dontorrents':
        from channels import dontorrents
        item.channel = 'dontorrents'
        dontorrents.configurar_proxies(item)

    elif item.from_channel == 'dontorrentsin':
        from channels import dontorrentsin
        item.channel = 'dontorrentsin'
        dontorrentsin.configurar_proxies(item)

    elif item.from_channel == 'elifilms':
        from channels import elifilms
        item.channel = 'elifilms'
        elifilms.configurar_proxies(item)

    elif item.from_channel == 'entrepeliculasyseries':
        from channels import entrepeliculasyseries
        item.channel = 'entrepeliculasyseries'
        entrepeliculasyseries.configurar_proxies(item)

    elif item.from_channel == 'estrenoscinesaa':
        from channels import estrenoscinesaa
        item.channel = 'estrenoscinesaa'
        estrenoscinesaa.configurar_proxies(item)

    elif item.from_channel == 'gnula':
        from channels import gnula
        item.channel = 'gnula'
        gnula.configurar_proxies(item)

    elif item.from_channel == 'gnula24':
        from channels import gnula24
        item.channel = 'gnula24'
        gnula24.configurar_proxies(item)

    elif item.from_channel == 'gnula24h':
        from channels import gnula24h
        item.channel = 'gnula24h'
        gnula24h.configurar_proxies(item)

    elif item.from_channel == 'grantorrent':
        from channels import grantorrent
        item.channel = 'grantorrent'
        grantorrent.configurar_proxies(item)

    elif item.from_channel == 'hdfull':
        from channels import hdfull
        item.channel = 'hdfull'
        hdfull.configurar_proxies(item)
        refrescar = True

    elif item.from_channel == 'hdfullse':
        from channels import hdfullse
        item.channel = 'hdfullse'
        hdfullse.configurar_proxies(item)

    elif item.from_channel == 'henaojara':
        from channels import henaojara
        item.channel = 'henaojara'
        henaojara.configurar_proxies(item)

    elif item.from_channel == 'homecine':
        from channels import homecine
        item.channel = 'homecine'
        homecine.configurar_proxies(item)

    elif item.from_channel == 'inkapelis':
        from channels import inkapelis
        item.channel = 'inkapelis'
        inkapelis.configurar_proxies(item)

    elif item.from_channel == 'lilatorrent':
        from channels import lilatorrent
        item.channel = 'lilatorrent'
        lilatorrent.configurar_proxies(item)

    elif item.from_channel == 'megaserie':
        from channels import megaserie
        item.channel = 'megaserie'
        megaserie.configurar_proxies(item)

    elif item.from_channel == 'mejortorrentnz':
        from channels import mejortorrentnz
        item.channel = 'mejortorrentnz'
        mejortorrentnz.configurar_proxies(item)

    elif item.from_channel == 'movidytv':
        from channels import movidytv
        item.channel = 'movidytv'
        movidytv.configurar_proxies(item)

    elif item.from_channel == 'newpct1':
        platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Configurar proxies desde el canal[/COLOR][/B]' % color_adver)
        refrescar = False

    elif item.from_channel == 'peliculaspro':
        from channels import peliculaspro
        item.channel = 'peliculaspro'
        peliculaspro.configurar_proxies(item)

    elif item.from_channel == 'pelis28':
        from channels import pelis28
        item.channel = 'pelis28'
        pelis28.configurar_proxies(item)

    elif item.from_channel == 'pelisflix':
        from channels import pelisflix
        item.channel = 'pelisflix'
        pelisflix.configurar_proxies(item)

    elif item.from_channel == 'pelisforte':
        from channels import pelisforte
        item.channel = 'pelisforte'
        pelisforte.configurar_proxies(item)

    elif item.from_channel == 'pelishouse':
        from channels import pelishouse
        item.channel = 'pelishouse'
        pelishouse.configurar_proxies(item)

    elif item.from_channel == 'pelishouseonline':
        from channels import pelishouseonline
        item.channel = 'pelishouseonline'
        pelishouseonline.configurar_proxies(item)

    elif item.from_channel == 'pelismaraton':
        from channels import pelismaraton
        item.channel = 'pelismaraton'
        pelismaraton.configurar_proxies(item)

    elif item.from_channel == 'pelispedia':
        from channels import pelispedia
        item.channel = 'pelispedia'
        pelispedia.configurar_proxies(item)

    elif item.from_channel == 'pelisplanet':
        from channels import pelisplanet
        item.channel = 'pelisplanet'
        pelisplanet.configurar_proxies(item)

    elif item.from_channel == 'pelisplay':
        from channels import pelisplay
        item.channel = 'pelisplay'
        pelisplay.configurar_proxies(item)

    elif item.from_channel == 'pelisxd':
        from channels import pelisxd
        item.channel = 'pelisxd'
        pelisxd.configurar_proxies(item)

    elif item.from_channel == 'pelisyseries':
        from channels import pelisyseries
        item.channel = 'pelisyseries'
        pelisyseries.configurar_proxies(item)

    elif item.from_channel == 'playdede':
        from channels import playdede
        item.channel = 'playdede'
        playdede.configurar_proxies(item)

    elif item.from_channel == 'playview':
        from channels import playview
        item.channel = 'playview'
        playview.configurar_proxies(item)

    elif item.from_channel == 'ppeliculas':
        from channels import ppeliculas
        item.channel = 'ppeliculas'
        ppeliculas.configurar_proxies(item)

    elif item.from_channel == 'reinventorrent':
        from channels import reinventorrent
        item.channel = 'reinventorrent'
        reinventorrent.configurar_proxies(item)

    elif item.from_channel == 'repelis24':
        from channels import repelis24
        item.channel = 'repelis24'
        repelis24.configurar_proxies(item)

    elif item.from_channel == 'repelishd':
        from channels import repelishd
        item.channel = 'repelishd'
        repelishd.configurar_proxies(item)

    elif item.from_channel == 'rojotorrent':
        from channels import rojotorrent
        item.channel = 'rojotorrent'
        rojotorrent.configurar_proxies(item)

    elif item.from_channel == 'seriesflixvideo':
        from channels import seriesflixvideo
        item.channel = 'seriesflixvideo'
        seriesflixvideo.configurar_proxies(item)

    elif item.from_channel == 'seriesmovil':
        from channels import seriesmovil
        item.channel = 'seriesmovil'
        seriesmovil.configurar_proxies(item)

    elif item.from_channel == 'seriespapayaxyz':
        from channels import seriespapayaxyz
        item.channel = 'seriespapayaxyz'
        seriespapayaxyz.configurar_proxies(item)

    elif item.from_channel == 'seriesyonkis':
        from channels import seriesyonkis
        item.channel = 'seriesyonkis'
        seriesyonkis.configurar_proxies(item)

    elif item.from_channel == 'subtorrents':
        from channels import subtorrents
        item.channel = 'subtorrents'
        subtorrents.configurar_proxies(item)

    elif item.from_channel == 'todotorrents':
        from channels import todotorrents
        item.channel = 'todotorrents'
        todotorrents.configurar_proxies(item)

    elif item.from_channel == 'tomadivx':
        from channels import tomadivx
        item.channel = 'tomadivx'
        tomadivx.configurar_proxies(item)

    elif item.from_channel == 'torrentdivx':
        from channels import torrentdivx
        item.channel = 'torrentdivx'
        torrentdivx.configurar_proxies(item)

    elif item.from_channel == 'tupelihd':
        from channels import tupelihd
        item.channel = 'tupelihd'
        tupelihd.configurar_proxies(item)

    elif item.from_channel == 'verdetorrent':
        from channels import verdetorrent
        item.channel = 'verdetorrent'
        verdetorrent.configurar_proxies(item)

    elif item.from_channel == 'yespornplease':
        from channels import yespornplease
        item.channel = 'yespornplease'
        yespornplease.configurar_proxies(item)

    else:
        platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + item.from_channel.capitalize() + '[/COLOR][/B]', '[B][COLOR %s]Falta _Proxies[/B][/COLOR]' % color_alert)
        refrescar = False

    if refrescar: _refresh_menu(item)


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
