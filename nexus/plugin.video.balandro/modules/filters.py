# -*- coding: utf-8 -*-

import os, xbmc, xbmcgui

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


cfg_search_included = 'search_included_all'

channels_search_included = config.get_setting(cfg_search_included, default='')


def mainlist(item):
    logger.info()
    itemlist = []

    tot_opt_anular = 0

    if config.get_setting('channels_link_main', default=True):
        if channels_search_excluded_mixed: tot_opt_anular += 1

    if channels_search_excluded_movies: tot_opt_anular += 1

    if channels_search_excluded_tvshows: tot_opt_anular += 1

    if channels_search_excluded_documentaries: tot_opt_anular += 1

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de [COLOR yellow][B]Películas y/o Series[/B][/COLOR]',
                                    extra = 'mixed', folder = False ))

    itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de [COLOR deepskyblue][B]Películas[/B][/COLOR]',
                                extra = 'movies', folder = False ))
    itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de [COLOR hotpink][B]Series[/B][/COLOR]',
                                extra = 'tvshows', folder = False ))
    itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de [COLOR cyan][B]Documentales[/B][/COLOR]',
                                extra = 'documentaries', folder = False ))
    itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de [COLOR blue][B]Torrents[/B][/COLOR]',
                                extra = 'torrents', folder = False ))

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action = 'channels_excluded', title='Excluir canales en las búsquedas de [COLOR green][B]Todos[/B][/COLOR]',
                                    extra = 'all', folder = False ))

    if config.get_setting('channels_link_main', default=True):
        if channels_search_excluded_mixed:
            itemlist.append(item.clone( title = '[B]Anular las exclusiones para [COLOR yellow]Películas y/o Series[/COLOR][/B]', action = 'channels_excluded_del',
                                        extra = 'mixed', folder = False, text_color='coral' ))

    if channels_search_excluded_movies:
        itemlist.append(item.clone( title = '[B]Anular las exclusiones para [COLOR deepskyblue]Películas[/COLOR][/B]', action = 'channels_excluded_del',
                                    extra = 'movies', folder = False, text_color='coral' ))

    if channels_search_excluded_tvshows:
        itemlist.append(item.clone( title = '[B]Anular las exclusiones para [COLOR hotpink]Series[/COLOR][/B]', action = 'channels_excluded_del',
                                    extra = 'tvshows', folder = False, text_color='coral' ))

    if channels_search_excluded_documentaries:
        itemlist.append(item.clone( title = '[B]Anular las exclusiones para [COLOR cyan]Documentales[/COLOR][/B]', action = 'channels_excluded_del',
                                    extra = 'documentaries', folder = False, text_color='coral' ))

    if channels_search_excluded_torrents:
        itemlist.append(item.clone( title = '[B]Anular las exclusiones para [COLOR blue]Torrents[/COLOR][/B]', action = 'channels_excluded_del',
                                    extra = 'torrents', folder = False, text_color='coral' ))

    if config.get_setting('channels_link_main', default=True):
        if channels_search_excluded_all or tot_opt_anular > 1:
            itemlist.append(item.clone( title = '[B]Anular [COLOR green]Todas[/COLOR][/B] las exclusiones', action = 'channels_excluded_del',
                                        extra= 'all', folder = False, text_color='yellow' ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist2(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action = 'channels_excluded', title='[COLOR greenyellow][B]Efectuar las búsquedas Solo en determinados canales[/B][/COLOR]',
                                extra = 'included', folder = False ))

    if channels_search_included:
        itemlist.append(item.clone( title = '[COLOR coral][B]Anular Todos los canales[/COLOR][/B] En las búsquedas de Solo determinados canales',
                                    action = 'channels_excluded_del', extra = 'included', folder = False, text_color='yellow' ))

    platformtools.itemlist_refresh()

    return itemlist


def only_animes(item):
    logger.info()

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return

    cabecera = 'Canales con contenido de Animes'
    if item.exclusively_animes: cabecera = 'Canales con contenido Exclusivamente de Animes'

    filtros = {'clusters': 'anime'}

    opciones_channels = []
    canales_animes = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        info = ''

        if item.exclusively_animes:
            if not 'exclusivamente al anime' in ch['notes'].lower(): continue

        if ch['status'] == 1: info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1: info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')

        if ch['searchable'] == False:
            tipos = str(tipos).replace('movie', 'Vídeos')
            tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('all,', '').strip()
        else:
            tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '').strip()

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'VO')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_animes.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_animes[ret]
        tests_channels(canal[0], canal[1], canal[2])


def only_adults(item):
    logger.info()

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return

    cabecera = 'Canales con contenido para Adultos'
    if item.exclusively_adults: cabecera = 'Canales con contenido Exclusivamente para Adultos'

    filtros = {'clusters': 'adults'}

    opciones_channels = []
    canales_adults = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        info = ''

        if item.exclusively_adults:
            if not '+18' in ch['notes']: continue

        if ch['status'] == 1: info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1: info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        if '+18' in ch['notes']: info = info + '[B][COLOR pink] %s [/B][/COLOR]' % '+18'

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')

        if ch['searchable'] == False: tipos = str(tipos).replace('movie', 'Vídeos')
        else: tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '').strip()

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'VO')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_adults.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_adults[ret]
        tests_channels(canal[0], canal[1], canal[2])


def with_proxies(item):
    logger.info()

    channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')

    no_proxies = config.get_setting('search_no_proxies', default=False)

    if item.memo_proxies: cabecera = 'Canales con Proxies Memorizados'
    else: cabecera = 'Canales que pueden necesitar Proxies'

    filtros = {}

    opciones_channels = []
    canales_proxies = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0

    for ch in ch_list:
        if not 'proxies' in ch['notes'].lower(): continue

        i =+ 1

    if i == 0:
        if item.memo_proxies:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales con proxies memorizados[/B][/COLOR]' % color_adver)
        else:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales con proxies a Configurar[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        if not 'proxies' in ch['notes'].lower(): continue

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'
        cfg_proxytools_provider = 'channel_' + ch['id'] + '_proxytools_provider'

        if item.memo_proxies:
            if channels_proxies_memorized:
                el_memorizado = "'" + ch['id'] + "'"
                if not el_memorizado in str(channels_proxies_memorized):
                    if not config.get_setting(cfg_proxies_channel, default=''): continue
                else:
                   if item.memo_proxies:
                        if not config.get_setting(cfg_proxies_channel, default=''): continue
            else:
                if not config.get_setting(cfg_proxies_channel, default=''): continue

        info = ''

        if ch['status'] == 1: info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1: info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies
        elif config.get_setting(cfg_proxytools_max_channel, default=''): info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'
        elif config.get_setting(cfg_proxytools_provider, default=''): info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'
        else: info = info + '[COLOR firebrick][B] Quizás use proxies [/B][/COLOR]'

        if no_proxies: info = info + '[COLOR white][B] EXCLUIDO Buscar [/B][/COLOR]'

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '').strip()

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'VO')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_proxies.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_proxies[ret]
        retorno = False

        if item.new_proxies:
            retorno = search_new_proxies(canal[0], canal[1], canal[2])

            if not item.test_proxies: return

        if not retorno:
            tests_channels(canal[0], canal[1], canal[2])


def no_actives(item):
    logger.info()

    if item.no_searchables:
        cabecera = 'Canales que Nunca intervendrán en las búsquedas'
        filtros = {'searchable': False}
    else:
        cabecera = 'Canales Desactivados'
        filtros = {'searchable': True}

    opciones_channels = []
    canales_no_actives = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not item.no_searchables:
        i = 0
        for ch in ch_list:
            if not ch['status'] == -1: continue

            i =+ 1

        if i == 0:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales desactivados[/B][/COLOR]' % color_adver)
            return

    for ch in ch_list:
        if not item.no_searchables:
            if not ch['status'] == -1: continue

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'
        cfg_proxytools_provider = 'channel_' + ch['id'] + '_proxytools_provider'

        info = ''

        if not item.no_searchables: info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive
        else:
            if 'adults' in ch['clusters']: info = info + '[COLOR red][B] Adultos [/B][/COLOR]'
            elif 'anime' in ch['clusters']: info = info + '[COLOR fuchsia][B] Anime [/B][/COLOR]'
            elif 'dorama' in ch['clusters']: info = info + '[COLOR firebrick][B] Doramas [/B][/COLOR]'

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies
        elif config.get_setting(cfg_proxytools_max_channel, default=''): info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'
        elif config.get_setting(cfg_proxytools_provider, default=''): info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '').strip()

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'VO')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_no_actives.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_no_actives[ret]
        tests_channels(canal[0], canal[1], canal[2])


def only_prefered(item):
    logger.info()

    cabecera = 'Canales Preferidos'
    filtros = {'searchable': True}

    opciones_channels = []
    canales_only_prefered = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0
    for ch in ch_list:
        if not ch['status'] == 1: continue

        i =+ 1

    if i == 0:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales preferidos[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        if not ch['status'] == 1: continue

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'
        cfg_proxytools_provider = 'channel_' + ch['id'] + '_proxytools_provider'

        info = ''

        info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies
        elif config.get_setting(cfg_proxytools_provider, default=''): info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'
        elif config.get_setting(cfg_proxytools_max_channel, default=''): info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '').strip()

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'VO')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_only_prefered.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_only_prefered[ret]
        tests_channels(canal[0], canal[1], canal[2])


def only_torrents(item):
    logger.info()

    cabecera = 'Canales que pueden contener archivos Torrents'
    if item.exclusively_torrents: cabecera = 'Canales con enlaces Torrent exclusivamente'

    filtros = {'categories': 'torrent'}

    opciones_channels = []
    canales_torrents = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        if item.exclusively_torrents:
            if not 'enlaces torrent exclusivamente' in ch['notes'].lower(): continue

        info = ''

        if ch['status'] == 1: info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1: info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '').strip()

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'VO')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales_torrents.append((ch['name'], info, ch['notes']))

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales_torrents[ret]
        tests_channels(canal[0], canal[1], canal[2])


def channels_status(item):
    logger.info()

    if item.des_rea: cabecera = 'Desactivar o Re-activar'
    else: cabecera = 'Marcar o Des-marcar Preferidos'

    filtros = {}

    preselect = []
    channels_ids = []
    opciones = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    for ch in ch_list:
        info = ''

        if ch['status'] == 1: info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1: info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        if '+18' in ch['notes']: info = info + '[COLOR pink][B] Adultos [/B][/COLOR]'
        elif 'anime' in ch['clusters']: info = info + '[COLOR fuchsia][B] Anime [/B][/COLOR]'
        elif 'torrents' in ch['clusters']: info = info + '[COLOR violet][B] Torrents [/B][/COLOR]'
        elif 'dorama' in ch['clusters']: info = info + '[COLOR firebrick][B] Doramas [/B][/COLOR]'

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '').strip()

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'VO')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        it = xbmcgui.ListItem(ch['name'], info)
        it.setArt({'thumb': ch['thumbnail']})
        opciones.append(it)

        channels_ids.append(ch['id'])

    ret = xbmcgui.Dialog().multiselect('Personalizar canales [COLOR yellow]' + cabecera + '[/COLOR]', opciones, preselect=preselect, useDetails=True)

    if ret is None: return

    if item.des_rea:
        seleccionados = channels_des_rea_make(ret, channels_ids)
    else:
        seleccionados = channels_preferidos_make(ret, channels_ids)

    if not str(seleccionados) == '[]':
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Canales Re-ajustados[/B][/COLOR]' % color_exec)

        platformtools.itemlist_refresh()


def channels_des_rea_make(ret, channels_ids):
    logger.info()

    seleccionados = []

    for ord_channel in ret:
        channel_id = channels_ids[ord_channel]
        seleccionados.append(channel_id)

        status = config.get_setting('status', channel_id)

        if status is None: config.set_setting('status', -1, channel_id)
        else:
            if status == -1: config.set_setting('status', 0, channel_id)
            elif str(status) == '0': config.set_setting('status', -1, channel_id)
            else: config.set_setting('status', -1, channel_id)

    return seleccionados


def channels_preferidos_make(ret, channels_ids):
    logger.info()

    seleccionados = []

    for ord_channel in ret:
        channel_id = channels_ids[ord_channel]
        seleccionados.append(channel_id)

        status = config.get_setting('status', channel_id)

        if status is None: config.set_setting('status', 1, channel_id)
        else:
            if status == -1: config.set_setting('status', 1, channel_id)
            elif str(status) == '0': config.set_setting('status', 1, channel_id)
            else: config.set_setting('status', 0, channel_id)

    return seleccionados


def channels_excluded(item):
    logger.info()

    if item.extra == 'included':
        cabecera = 'Todos (Solo determinados canales)'
        filtros = {'searchable': True}

    elif item.extra == 'movies':
        cabecera = 'Películas'
        filtros = {'categories': 'movie', 'searchable': True}
    elif item.extra == 'tvshows':
        cabecera = 'Series'
        filtros = {'categories': 'tvshow', 'searchable': True}
    elif item.extra == 'documentaries':
        cabecera = 'Documentales'
        filtros = {'categories': 'documentary', 'searchable': True}
    elif item.extra == 'torrents':
        cabecera = 'Torrents'
        filtros = {'categories': 'torrent', 'searchable': True}
    elif item.extra == 'mixed':
        cabecera = 'Películas y/o Series'
        filtros = {'searchable': True}
    else:
        cabecera = 'Todos'
        filtros = {'searchable': True}

    preselect = []
    channels_ids = []
    opciones = []

    if item.extra == 'included':
        cfg_excludes = 'search_included_all'
    else:
        cfg_excludes = 'search_excludes_' + item.extra

    channels_search = config.get_setting(cfg_excludes, default='')

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if channels_search:
        channels_orden = []

        exclusiones = False

        for ch in ch_list:
            if ch['searchable'] == False: continue

            if item.extra == 'mixed':
                tipos = ch['search_types']
                if 'documentary' in tipos: continue

            channels_orden.append(ch['id'])

        channels_preselct = str(channels_search).replace('[', '').replace(']', ',')

        matches = scrapertools.find_multiple_matches(channels_preselct, "(.*?), '(.*?)',")

        if matches:
            for ch_nro, ch_name in matches:
                ord_nro = 0

                for ch in channels_orden:
                    if ch_name == ch:
                        if ch_name in str(preselect): break

                        exclusiones = True
                        preselect.append(ord_nro)
                        break

                    ord_nro += 1

            if not exclusiones:
                tex1 = '[COLOR plum]El orden de la lista de canales ha variado respecto a su lista anterior (Preferidos, Desactivados, Inactivos ó Anulados).[/COLOR]'
                tex2 = '[COLOR cyan][B]Deberá seleccionar de nuevo los canales a excluir deseados.[/B][/COLOR]'
                tex3 = '[COLOR red]Porque se eliminarán los canales memorizados para excluirlos en las búsquedas[/COLOR]'
                platformtools.dialog_ok(config.__addon_name, tex1, tex2, tex3)
                config.set_setting(cfg_excludes, '')
                preselect = []

    i = 0

    for ch in ch_list:
        if ch['searchable'] == False: continue

        if item.extra == 'mixed':
            tipos = ch['search_types']
            if 'documentary' in tipos: continue

        if not channels_search: preselect.append(i)
        channels_ids.append(ch['id'])
        i += 1

    for ch in ch_list:
        if ch['searchable'] == False: continue

        if item.extra == 'mixed':
            tipos = ch['search_types']
            if 'documentary' in tipos: continue

        info = ''

        if channels_search:
            channels_preselct = str(channels_search).replace('[', '').replace(']', ',')
            if ("'" + ch['id'] + "'") in str(channels_preselct): info = info + '[COLOR violet][B]EXCLUIDO [/B][/COLOR]'

        if ch['status'] == 1: info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1: info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
        if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '').strip()

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'VO')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        it = xbmcgui.ListItem(ch['name'], info)
        it.setArt({'thumb': ch['thumbnail']})
        opciones.append(it)

    if item.extra == 'included': cab = 'Incluir canales en las búsquedas de [COLOR yellow]'
    else: cab = 'Excluir canales en las búsquedas de  [COLOR yellow]'

    ret = xbmcgui.Dialog().multiselect(cab + cabecera + '[/COLOR]', opciones, preselect=preselect, useDetails=True)

    if ret is None: return

    seleccionados = channels_excluded_list(ret, channels_ids, channels_search)

    if str(seleccionados) == '[]': seleccionados = ''
    config.set_setting(cfg_excludes, str(seleccionados))

    platformtools.itemlist_refresh()


def channels_excluded_del(item):
    logger.info()

    if item.extra == 'included':
        canales_excluidos = channels_search_included
        txt = 'Todos'

    elif item.extra == 'movies':
        canales_excluidos = channels_search_excluded_movies
        txt = 'Películas'
    elif item.extra == 'tvshows':
        canales_excluidos = channels_search_excluded_tvshows
        txt = 'Series'
    elif item.extra == 'documentaries':
        canales_excluidos = channels_search_excluded_documentaries
        txt = 'Documentales'
    elif item.extra == 'torrents':
        canales_excluidos = channels_search_excluded_torrents
        txt = 'Torrents'
    elif item.extra == 'mixed':
        canales_excluidos = channels_search_excluded_mixed
        txt = 'Películas y/o Series'
    else:
        canales_excluidos = channels_search_excluded_all
        txt = 'Películas, Series y Documentales'

    canales_excluidos = scrapertools.find_multiple_matches(str(canales_excluidos), "(.*?), '(.*?)'")

    txt_excluidos = ''

    for orden_nro, id_canal in canales_excluidos:
        if not txt_excluidos: txt_excluidos = id_canal.capitalize()
        else: txt_excluidos += (', ' + id_canal.capitalize())

    if item.extra == 'included':
        if not platformtools.dialog_yesno(config.__addon_name + ' [COLOR greenyellow][B]Inclusiones[/B][/COLOR]', '[COLOR plum]' + str(txt_excluidos) + '[/COLOR]', '[COLOR red]¿ Desea anular los canales memorizados para Incluirlos de Nuevo en las búsquedas de ? [COLOR yellow] ' + txt + '[/COLOR]'):
            return

    else:
        if not platformtools.dialog_yesno(config.__addon_name + ' [COLOR cyan][B]Exclusiones[/B][/COLOR]', '[COLOR plum]' + str(txt_excluidos) + '[/COLOR]', '[COLOR red]¿ Desea anular los canales memorizados para excluirlos en las búsquedas de ? [COLOR yellow] ' + txt + '[/COLOR]'):
            return

    if item.extra == 'included': config.set_setting(cfg_search_included, '')

    elif item.extra == 'movies': config.set_setting(cfg_search_excluded_movies, '')
    elif item.extra == 'tvshows': config.set_setting(cfg_search_excluded_tvshows, '')
    elif item.extra == 'documentaries': config.set_setting(cfg_search_excluded_documentaries, '')
    elif item.extra == 'torrents': config.set_setting(cfg_search_excluded_torrents, '')
    elif item.extra == 'mixed': config.set_setting(cfg_search_excluded_mixed, '')
    else:
        if channels_search_excluded_movies: config.set_setting(cfg_search_excluded_movies, '')
        if channels_search_excluded_tvshows: config.set_setting(cfg_search_excluded_tvshows, '')
        if channels_search_excluded_documentaries: config.set_setting(cfg_search_excluded_documentaries, '')
        if channels_search_excluded_torrents: config.set_setting(cfg_search_excluded_torrents, '')
        if channels_search_excluded_mixed: config.set_setting(cfg_search_excluded_mixed, '')
        if channels_search_excluded_all: config.set_setting(cfg_search_excluded_all, '')

    platformtools.itemlist_refresh()


def channels_excluded_list(ret, channels_ids, channels_search):
    logger.info()

    channel_sel = []
    seleccionados = []

    if channels_search:
        for ch in ret:
            channel_sel.append(ch)
    else:
        nro_sel = 0
        for ch in ret:
            if not ch == nro_sel:
                channel_sel.append(nro_sel)
                nro_sel += 1

                while not (nro_sel == ch):
                    channel_sel.append(nro_sel)
                    nro_sel += 1

            nro_sel += 1

    for ch_sel in channel_sel:
        seleccionados.append(ch_sel)
        i_id = 0

        for channel_id in channels_ids:
            if ch_sel == i_id: seleccionados.append(channel_id)
            i_id += 1

    if not seleccionados:
        if len(channels_ids) > len(ret):
            i_id = 0
            len_ret = len(ret)

            for channel_id in channels_ids:
                if i_id < len_ret:
                    i_id += 1
                    continue

                ord_nro = str(i_id).replace('[', '').replace(']', '').strip()

                seleccionados.append(ord_nro)
                seleccionados.append(channel_id + ',')

                i_id += 1

    return seleccionados


def show_servers_list(item):
    logger.info()

    servers_preferred = config.get_setting('servers_preferred', default='')
    if servers_preferred: servers_preferred_list = servers_preferred.lower().replace(' ', '').split(',')

    servers_unfavored = config.get_setting('servers_unfavored', default='')
    if servers_unfavored: servers_unfavored_list = servers_unfavored.lower().replace(' ', '').split(',')

    servers_discarded = config.get_setting('servers_discarded', default='')
    if servers_discarded: servers_discarded_list = servers_discarded.lower().replace(' ', '').split(',')

    from core import filetools, jsontools

    if item.tipo == 'activos':
        cabecera = 'Servidores Disponibles'
        filtro = True
    elif item.tipo == 'alternativos':
        cabecera = 'Servidores Vías Alternativas'
        filtro = True
    elif item.tipo == 'inactivos':
        cabecera = 'Servidores Inactivos'
        filtro = False
    elif item.tipo == 'sinsoporte':
        cabecera = 'Servidores No Soportados'
        filtro = False
    else:
        cabecera = 'Todos los Servidores'
        filtro = None

    channels_ids = []
    opciones_servers = []
    servers = []

    path = os.path.join(config.get_runtime_path(), 'servers')

    servidores = os.listdir(path)
    servidores = sorted(servidores)

    if not servidores:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin servidores de este tipo[/B][/COLOR]' % color_adver)
        return

    thumb = config.get_thumb('bolt')

    for server in servidores:
        if not server.endswith('.json'): continue

        path_server = os.path.join(config.get_runtime_path(), 'servers', server)

        if not os.path.isfile(path_server): continue

        data = filetools.read(path_server)
        dict_server = jsontools.load(data)

        if not filtro is None:
            if filtro == False:
                if dict_server['active'] == True: continue
            else:
                if dict_server['active'] == False: continue

        info = ''

        try:
           notes = dict_server['notes']
        except: 
           notes = ''

        if item.tipo == 'sinsoporte':
            if not "Requiere" in notes: continue
        elif item.tipo == 'alternativos':
            if not "Alternative" in notes: continue

            add_on = scrapertools.find_single_match(notes, 'vía:(.*?)$').strip().lower()
            if ' (' in add_on: add_on = scrapertools.find_single_match(add_on, '(.*?) ').strip().lower()

            if xbmc.getCondVisibility('System.HasAddon("%s")' % add_on): exists_addon = ' [COLOR tan][B] Instalada [/B]'
            else: exists_addon = ' [COLOR red][B] No instalada [/B]'

            info = info + exists_addon

        if dict_server['active'] == False:
            if item.tipo == 'activos': continue

            info = info + '[COLOR red][B] Inactivo [/B][/COLOR]'

        if servers_preferred:
            if dict_server['id'] in servers_preferred_list:
                if info: info = info + '  '
                info = info + '[COLOR cyan][B] Preferido [/B][/COLOR]'

        if servers_unfavored:
            if dict_server['id'] in servers_unfavored:
                if info: info = info + '  '
                info = info + '[COLOR chartreuse][B] como Última opción [/B][/COLOR]'

        if servers_discarded:
            if dict_server['id'] in servers_discarded_list:
                if info: info = info + '  '
                info = info + '[COLOR indianred][B] Descartado [/B][/COLOR]'

        if notes:
            if info: info = info + '  '
            info = info + '[COLOR mediumaquamarine]' + notes + '[/COLOR]'

        server_name = dict_server['name']
        server_thumb = thumb

        opciones_servers.append(platformtools.listitem_to_select('[COLOR yellow]' + server_name + '[/COLOR]', info, server_thumb))

        servers.append((server_name, info))

    if not opciones_servers:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin servidores de este tipo[/B][/COLOR]' % color_adver)
        return


    ret = platformtools.dialog_select(cabecera, opciones_servers, useDetails=True)

    if not ret == -1:
        servidor = servers[ret]
        tests_servers(servidor[0], servidor[1])


def show_channels_list(item):
    logger.info()

    channels_search_movies = config.get_setting(cfg_search_excluded_movies, default='')
    channels_search_tvshows = config.get_setting(cfg_search_excluded_tvshows, default='')
    channels_search_documentaries = config.get_setting(cfg_search_excluded_documentaries, default='')
    channels_search_mixed = config.get_setting(cfg_search_excluded_mixed, default='')
    channels_search_all = config.get_setting(cfg_search_excluded_all, default='')

    channels_search = channels_search_movies + channels_search_tvshows + channels_search_documentaries + channels_search_mixed + channels_search_all

    no_proxies = config.get_setting('search_no_proxies', default=False)
    no_channels = config.get_setting('search_no_channels', default=False)

    opciones_channels = []
    canales = []

    if item.tipo == 'all':
        filtros = {'active': False}
        ch_list_f = channeltools.get_channels_list(filtros=filtros)
        filtros = {'active': True}
        ch_list_t = channeltools.get_channels_list(filtros=filtros)
        ch_list = ch_list_f + ch_list_t

        ch_list.sort(key=lambda ch: ch['id'])

    else:
        if item.no_active == True or item.temp_no_active == True: filtros = {'active': False}
        elif item.no_stable == True: filtros = {'clusters': 'inestable'}
        elif item.cta_register == True: filtros = {'clusters': 'register'}
        elif item.suggesteds == True: filtros = {'clusters': 'suggested'}
        elif item.last_domain == True: filtros = {'clusters': 'current'}
        elif item.mismatched == True: filtros = {'clusters': 'mismatched'}
        elif item.problematics == True: filtros = {'clusters': 'problematic'}
        elif item.notices == True: filtros = {'clusters': 'notice'}
        else: filtros = {}

        ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    for ch in ch_list:
        info = ''

        if item.temp_no_active:
            if not 'temporary' in ch['clusters']: continue
        elif item.no_active:
            if 'temporary' in ch['clusters']: continue
        elif item.var_domains:
            if not 'dominios' in ch['notes'].lower(): continue
        elif item.last_domain:
            if not 'current' in ch['clusters']: continue
        elif item.suggesteds:
            if not 'suggested' in ch['clusters']: continue
        elif item.privates:
            if not 'privates' in ch['clusters']: continue
        elif item.mismatched:
            if not 'mismatched' in ch['clusters']: continue
        elif item.problematics:
            if not 'problematic' in ch['clusters']: continue
        elif item.notices:
            if not 'notice' in ch['clusters']: continue

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

        if 'register' in ch['clusters']: info = info + '[COLOR fuchsia][B] Cuenta [/B][/COLOR]'

        if ch['active'] == False:
            if 'temporary' in ch['clusters']: info = info + '[COLOR pink][B] Temporalmente Inactivo [/B][/COLOR]'
            else: info = info + '[COLOR red][B] Inactivo [/B][/COLOR]'
        elif ch['searchable'] == False: info = info + '[COLOR coral][B] No búsquedas [/B][/COLOR]'
        elif channels_search:
            if no_proxies:
                if 'proxies' in ch['notes'].lower():
                    if config.get_setting(cfg_proxies_channel, default=''):
                        if no_channels: info = info + '[COLOR moccasin][B] Descartado Proxies [/B][/COLOR]'

            if ch['id'] in channels_search: info = info + '[COLOR coral][B] No búsquedas [/B][/COLOR]'

        cfg_searchable_channel = 'channel_' + ch['id'] + '_no_searchable'

        if config.get_setting(cfg_searchable_channel, default=False): info = info + '[COLOR violet][B] Descartado búsquedas [/B][/COLOR]'

        if ch['status'] == 1: info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
        elif ch['status'] == -1: info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

        if 'dominios' in ch['notes'].lower():
            dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
            if dominio:
                dominio = dominio.replace('https://', '').replace('/', '')
                info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio
        else:
            if 'current' in ch['clusters']:
                vigente = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
                if item.only_last_domain:
                    if not vigente: continue

                if vigente:
                    vigente = vigente.replace('https://', '').replace('/', '')
                    info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % vigente

        if 'problematic' in ch['clusters']: info = info + '[B][I][COLOR darkgoldenrod] Problemático [/I][/B][/COLOR]'
        if 'notice' in ch['clusters']: info = info + '[B][COLOR orange] Aviso [/B][/COLOR]'

        if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

        tipos = ch['search_types']
        tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
        tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '').strip()

        if info: info = info + '  '
        info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

        idiomas = ch['language']
        idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
        idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'VO')

        if info: info = info + '  '
        info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

        channel_name = ch['name']
        channel_thumb = ch['thumbnail']

        opciones_channels.append(platformtools.listitem_to_select('[COLOR yellow]' + channel_name + '[/COLOR]', info, channel_thumb))

        canales.append((ch['name'], info, ch['notes']))

    if not canales:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    if item.tipo == 'all':
        cabecera = 'Canales [COLOR yellow]Todos[/COLOR]'
        if item.privates == True: cabecera = 'Canales [COLOR yellow]Privados[/COLOR]'
    else:
        if item.no_active == True: cabecera = 'Canales [COLOR yellow]Inactivos[/COLOR]'
        elif item.temp_no_active == True: cabecera = 'Canales [COLOR yellow]Temporalmente Inactivos[/COLOR]'
        elif item.no_stable == True: cabecera = 'Canales [COLOR yellow]Inestables[/COLOR]'
        elif item.cta_register == True: cabecera = 'Canales [COLOR yellow]con Cuenta[/COLOR]'
        elif item.var_domains == True: cabecera = 'Canales [COLOR yellow]con varios Dominios[/COLOR]'
        elif item.last_domain == True:
              cabecera = 'Canales [COLOR yellow]que puede comprobarse el Último Dominio Vigente[/COLOR]'
              if item.only_last_domain: cabecera = 'Canales con el [COLOR yellow]Último Dominio Vigente[/COLOR] informado'
        elif item.suggesteds == True: cabecera = 'Canales [COLOR yellow]Sugeridos[/COLOR]'
        elif item.privates == True: cabecera = 'Canales [COLOR yellow]Privados[/COLOR]'
        elif item.mismatched == True: cabecera = 'Canales [COLOR yellow]Incompatibles con su Media Center[/COLOR]'
        elif item.problematics == True: cabecera = 'Canales [COLOR yellow]Problemáticos[/COLOR]'
        elif item.notices == True: cabecera = 'Canales con [COLOR yellow]Aviso CloudFlare Protection[/COLOR]'
        else: cabecera = 'Canales [COLOR yellow]Disponibles[/COLOR]'

    ret = platformtools.dialog_select(cabecera, opciones_channels, useDetails=True)

    if not ret == -1:
        canal = canales[ret]
        tests_channels(canal[0], canal[1], canal[2])

def show_clients_torrent(item):
    logger.info()

    cliente_torrent = config.get_setting('cliente_torrent', default='Seleccionar')

    from core import jsontools

    torrent_clients = jsontools.get_node_from_file('torrent.json', 'clients', os.path.join(config.get_runtime_path(), 'servers'))

    torrent_clients = sorted(torrent_clients, key=lambda x:x['name'])

    opciones_torrent = []
    torrents = []

    thumb = config.get_thumb('cloud')

    for client in torrent_clients:
        client_name = str(client['name']).capitalize()
        client_id = str(client['id'])

        if xbmc.getCondVisibility('System.HasAddon("%s")' % client['id']):
            if cliente_torrent.lower() in client['id']: exists_torrent = ' [COLOR yellow][B] Instalado[COLOR greenyellow] Asignado[/B]'
            else: exists_torrent = ' [COLOR yellow][B] Instalado [/B]'
        else: exists_torrent = ' [COLOR red][B] No instalado [/B]'

        if client_name == 'Elementum': client_recommended = '[COLOR limegreen][B]  Recomendado[/B][/COLOR]'
        else: client_recommended = ''

        opciones_torrent.append(platformtools.listitem_to_select('[COLOR cyan]' + client_name + '[/COLOR]', '[COLOR moccasin]' + client_id + exists_torrent + '[/COLOR]' + client_recommended, thumb))

        torrents.append((client_name, client_id + exists_torrent))

    ret = platformtools.dialog_select('Clientes/Motores externos para [COLOR yellow]Torrents[/COLOR]', opciones_torrent, useDetails=True)

    if ret == -1: return ret
	
    torrent = torrents[ret]

    name = torrent[0]

    sel_ret = [name, 'plugin.video.' + name.lower()]

    if 'soportados' in item.title:
        if 'Instalado' in str(torrent[1]):
            if not cliente_torrent == name:
                platformtools.dialog_ok(torrent[0], torrent[1] + '[/COLOR]', 'Por favor, asignelo como [COLOR coral]Cliente/Motor Torrent Habitual[/COLOR]')
        else:
            platformtools.dialog_ok(torrent[0], torrent[1] + '[/COLOR]', '[COLOR yellowgreen][B]No lo puede Asignar, falta instalarlo[/B][/COLOR]')
            return -1

    return sel_ret


def search_new_proxies(canal_0, canal_1, canal_2):
    if platformtools.dialog_yesno(canal_0, canal_1, '[COLOR red][B]¿ Desea efectuar una nueva búsqueda de proxies en el canal ?[/B][/COLOR]'):
        channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')
        iniciales_channels_proxies_memorized = channels_proxies_memorized

        from modules import proxysearch
        proxysearch.proxysearch_channel('', canal_0.lower(), canal_0, iniciales_channels_proxies_memorized)
        return True

    return False

def tests_channels(canal_0, canal_1, canal_2):
    if platformtools.dialog_yesno(canal_0, '[COLOR darkorange][B]¿ Efectuar Test Web del Canal ?[/B][/COLOR]', canal_1, canal_2):
        from modules import tester

        config.set_setting('developer_test_channels', '')

        try:
            tester.test_channel(canal_0)
        except:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)

def tests_servers(servidor_0, servidor_1):
    if platformtools.dialog_yesno(servidor_0,'[COLOR darkorange][B]¿ Efectuar Test Web del Servidor ?[/B][/COLOR]', servidor_1):
        from modules import tester

        config.set_setting('developer_test_servers', '')

        try:
            tester.test_server(servidor_0)
        except:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)

