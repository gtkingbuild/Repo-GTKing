# -*- coding: utf-8 -*-

import os, re, time

from datetime import datetime

from core.item import Item

from platformcode import config, logger, platformtools

from core import trackingtools, filetools


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


# Infos
def valor_infolabel(valor, infoLabels):
    if valor in infoLabels: return infoLabels[valor]
    return ''

def valor_infolabel_informado(valores, infoLabels):
    for valor in valores:
        if valor in infoLabels: return infoLabels[valor]
    return ''


# Guardar desde menú contextual
def addFavourite(item):
    logger.info()

    # Si se llega aquí mediante el menú contextual, hay que recuperar los parámetros action y channel
    if item.from_action: item.__dict__['action'] = item.__dict__.pop('from_action')
    if item.from_channel: item.__dict__['channel'] = item.__dict__.pop('from_channel')

    if item.contentType not in ['movie', 'tvshow', 'season', 'episode']:
        notification_d_ok = config.get_setting('notification_d_ok', default=True)
        if notification_d_ok:
            platformtools.dialog_ok(config.__addon_name, 'Sólo películas, series, temporadas ó capítulos')
        else:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sólo películas, series, temporadas ó capítulos[/COLOR][/B]' % color_avis)
        return False

    # Si no está definido tmdb_id seleccionar
    if item.contentType in ['movie', 'tvshow'] and not item.infoLabels['tmdb_id']:
        tipo = 'película' if item.contentType == 'movie' else 'serie'
        platformtools.dialog_ok(config.__addon_name, '[COLOR red][B]La %s no está identificada en TMDB.[/B][/COLOR]' % tipo, '[COLOR yellow][B]Si hay varias opciones posibles. Seleccionar una de ellas y sino cambiar el texto de búsqueda.[/B][/COLOR]')

        from core import tmdb

        ret = tmdb.dialog_find_and_set_infoLabels(item)
        if not ret:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Proceso cancelado[/COLOR][/B]' % color_adver)
            return False

    # Si está activada la confirmación de tmdb_id
    elif config.get_setting('tracking_confirm_tmdbid', default=False):
        if item.contentType in ['movie', 'tvshow']:
            from core import tmdb

            ret = tmdb.dialog_find_and_set_infoLabels(item)
            if not ret:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Proceso cancelado[/COLOR][/B]' % color_adver)
                return False
        else:
            # para temporadas/episodios no perder season/episode
            it_ant = item.clone()

            from core import tmdb

            ret = tmdb.dialog_find_and_set_infoLabels(item)
            if not ret:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Proceso cancelado[/COLOR][/B]' % color_adver)
                return False

            item.contentType = it_ant.contentType
            item.contentSeason = it_ant.contentSeason
            if it_ant.contentEpisodeNumber: item.contentEpisodeNumber = it_ant.contentEpisodeNumber

    # Si es una película/serie, completar información de tmdb si no se tiene activado tmdb_plus_info (para season/episodio no hace falta pq ya se habrá hecho la "segunda pasada")
    if item.contentType in ['movie', 'tvshow'] and not config.get_setting('tmdb_plus_info', default=False):
        from core import tmdb

        # obtener más datos en "segunda pasada" (actores, duración, ...)
        tmdb.set_infoLabels_item(item)

    # Guardar datos de serie/temporadas/episodios para el canal pedido
    if item.contentType == 'movie': tit = 'Guardando película'; sub = '[B][COLOR %s]Obteniendo datos[/COLOR][/B]' % color_infor
    elif item.contentType == 'tvshow': tit = 'Guardando serie'; sub = '[B][COLOR %s]Obteniendo temporadas y episodios[/COLOR][/B]' % color_infor
    elif item.contentType == 'season': tit = 'Guardando temporada'; sub = '[B][COLOR %s]Obteniendo episodios[/COLOR][/B]' % color_infor
    else:tit = 'Guardando episodio'; sub = '[B][COLOR %s]Obteniendo datos[/COLOR][/B]' % color_infor

    platformtools.dialog_notification(tit, sub)

    done = ''

    try:
        if item.contentType == 'movie': done, msg = trackingtools.scrap_and_save_movie(item.clone())
        else: done, msg = trackingtools.scrap_and_save_tvshow(item.clone())
    except:
        msg = '[B][COLOR yellow]Comprobar modulos (.scrap_and_save_....)[/COLOR][/B]'

    if not done:
        platformtools.dialog_ok(config.__addon_name, '[B][COLOR red]No se pudieron añadir los enlaces[/COLOR][/B]', msg)
        return False

    tit = item.contentTitle if item.contentType == 'movie' else item.contentSerieName
    el_canal = ('Añadidos enlaces de [B][COLOR %s]' + item.channel) % color_avis
    platformtools.dialog_notification(tit, el_canal + '[/COLOR][/B]')
    return True


# Navegacion Menús
def mainlist(item):
    logger.info()
    itemlist = []

    item.category = trackingtools.get_current_dbname()

    db = trackingtools.TrackingData()
    count_movies = db.get_movies_count()
    count_shows = db.get_shows_count()
    count_episodes = db.get_episodes_count()
    db.close()

    if (count_movies + count_shows + count_episodes) == 0:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Preferidos[/COLOR][/B]' % color_exec)

        try:
           preferidos_path = filetools.join(config.get_data_path(), 'tracking_dbs')
           filetools.rmdirtree(preferidos_path)
        except:
           pass

    else:
        itemlist.append(item.clone( title = 'Películas (%d)' % count_movies, action = 'mainlist_pelis', thumbnail=config.get_thumb('movie') ))

        context = [ {'title': 'Info tracking new episodes', 'channel': item.channel, 'action': 'info_tracking_shows'} ]
        context.append( {'title': 'Buscar ahora nuevos episodios', 'channel': item.channel, 'action': 'doit_tracking_shows'} )
        itemlist.append(item.clone( title = 'Series (%d)' % count_shows, action = 'mainlist_series', thumbnail=config.get_thumb('tvshow'), context=context ))

        itemlist.append(item.clone( title = 'Episodios (%d) recientes' % count_episodes, action = 'mainlist_episodios', thumbnail=config.get_thumb('hot') ))

        itemlist.append(item.clone( title='Gestionar listas', action='mainlist_listas' )) 

    itemlist.append(item.clone( channel='actions', title= '[COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR wheat][B]Preferidos[/B][/COLOR])', action = 'open_settings', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='helper', title = '[COLOR green][B]Información[/B][/COLOR] ¿ Cómo funciona ?', action = 'show_help_tracking', thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( channel='helper', title = '[COLOR green][B]Información[/B][/COLOR] Búsqueda automática de [COLOR cyan][B]Nuevos Episodios[/B][/COLOR]', action = 'show_help_tracking_update', thumbnail=config.get_thumb('help') ))

    return itemlist

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    db = trackingtools.TrackingData()

    count_movies = db.get_movies_count()

    if not item.desde: item.desde = 0
    if item.desde > count_movies: item.desde = 0

    tracking_perpage = config.get_setting('tracking_perpage_movies', default=10)

    tracking_order = config.get_setting('tracking_order_movies', default=0)
    orden = ['updated DESC', 'title ASC', 'aired DESC']

    rows = db.get_movies(orden=orden[tracking_order], desde=item.desde, numero=tracking_perpage)

    for tmdb_id, infolabels in rows:
        title = valor_infolabel('title', infolabels)
        if tracking_order == 1: title += '  [COLOR gray](%s)[/COLOR]' % valor_infolabel_informado(['release_date', 'year'], infolabels)
        else: title += '  [COLOR gray](%s)[/COLOR]' % valor_infolabel_informado(['year'], infolabels)

        context = [ {'title': 'Gestionar película', 'channel': item.channel, 'action': 'acciones_peli'} ]

        itemlist.append(Item( channel=item.channel, action='findvideos', title = title,
                              thumbnail = valor_infolabel('thumbnail', infolabels), fanart = valor_infolabel('fanart', infolabels),
                              infoLabels = infolabels, context=context ))

    if item.desde + tracking_perpage < count_movies:
        itemlist.append(item.clone( title = 'Siguientes ...', desde = item.desde + tracking_perpage, text_color = 'coral' ))

    db.close()

    return itemlist

def mainlist_series(item):
    logger.info()
    itemlist = []

    db = trackingtools.TrackingData()

    count_shows = db.get_shows_count()

    if not item.desde: item.desde = 0
    if item.desde > count_shows: item.desde = 0

    tracking_perpage = config.get_setting('tracking_perpage_tvshows', default=10)

    tracking_order = config.get_setting('tracking_order_tvshows', default=0)
    orden = ['updated DESC', 'title ASC', 'aired DESC']

    rows = db.get_shows(orden=orden[tracking_order], desde=item.desde, numero=tracking_perpage)

    for tmdb_id, infolabels in rows:
        title = valor_infolabel('tvshowtitle', infolabels)
        if tracking_order == 1: title += '  [COLOR gray](%s)[/COLOR]' % valor_infolabel_informado(['aired', 'year'], infolabels)
        else:
           anyo = valor_infolabel_informado(['year'], infolabels)
           if not anyo == '-': title += '  [COLOR gray](%s)[/COLOR]' % anyo

        # ~ if db.tracking_show_exists(tmdb_id): title += ' [COLOR gold](*)[/COLOR]'

        context = [ {'title': 'Gestionar serie', 'channel': item.channel, 'action': 'acciones_serie'} ]

        itemlist.append(Item( channel=item.channel, action='serie_temporadas', title = title,
                              thumbnail = valor_infolabel('thumbnail', infolabels), fanart = valor_infolabel('fanart', infolabels),
                              infoLabels = infolabels, context=context ))

    if item.desde + tracking_perpage < count_shows:
        itemlist.append(item.clone( title = 'Siguientes ...', desde = item.desde + tracking_perpage, text_color = 'coral' ))

    db.close()

    return itemlist


def mainlist_episodios(item):
    logger.info()
    itemlist = []

    db = trackingtools.TrackingData()

    count_episodes = db.get_episodes_count()

    if not item.desde: item.desde = 0
    if item.desde > count_episodes: item.desde = 0

    tracking_perpage = config.get_setting('tracking_perpage_episodes', default=10)

    tracking_order = config.get_setting('tracking_order_episodes', default=1)
    orden = ['updated DESC', 'aired DESC']

    rows = db.get_all_episodes(orden=orden[tracking_order], desde=item.desde, numero=tracking_perpage)

    for tmdb_id, season, episode, infolabels in rows:
        titulo = '%s %dx%02d' % (infolabels['tvshowtitle'], infolabels['season'], infolabels['episode'])
        subtitulo = valor_infolabel('episodio_titulo', infolabels)
        if subtitulo != '': titulo += ' ' + subtitulo

        if tracking_order == 1: titulo += '  [COLOR gray]%s[/COLOR]' % valor_infolabel('aired', infolabels)

        thumbnail = valor_infolabel_informado(['episodio_imagen','thumbnail'], infolabels)

        fanart = valor_infolabel('fanart', infolabels)

        context = [ {'title': 'Temporadas de la serie', 'channel': item.channel, 'action': 'serie_temporadas', 'link_mode': 'update'} ]

        itemlist.append(item.clone( action='findvideos', title=titulo, thumbnail = thumbnail, fanart = fanart, infoLabels = infolabels, context=context ))

    if item.desde + tracking_perpage < count_episodes:
        itemlist.append(item.clone( title = 'Siguientes ...', desde = item.desde + tracking_perpage, text_color = 'coral' ))

    db.close()

    return itemlist


# Listar Temporadas de una serie
def serie_temporadas(item):
    logger.info()
    itemlist = []

    item.category = item.contentSerieName

    db = trackingtools.TrackingData()

    rows = db.get_seasons(item.infoLabels['tmdb_id'])

    for season, infolabels in rows:
        titulo = 'Temporada %d' % season
        nombre = valor_infolabel('temporada_nombre', infolabels)

        if nombre != '' and nombre != titulo and nombre != 'Season %d' % season: titulo += ' ' + nombre

        thumbnail = valor_infolabel_informado(['temporada_poster','thumbnail'], infolabels)
        if thumbnail == '': thumbnail = item.thumbnail

        fanart = valor_infolabel('fanart', infolabels)
        if fanart == '': fanart = item.fanart

        context = [ {'title': 'Gestionar temporada', 'channel': item.channel, 'action': 'acciones_temporada'} ]

        itemlist.append(Item( channel=item.channel, action='serie_episodios', title=titulo, thumbnail = thumbnail, fanart = fanart,
                                                    infoLabels = infolabels, context=context ))

    db.close()

    return itemlist


# Listar Episodios de una temporada
def serie_episodios(item):
    logger.info()
    itemlist = []

    db = trackingtools.TrackingData()

    db.cur.execute('SELECT reverseorder FROM seasons WHERE tmdb_id=? AND season=?', (item.infoLabels['tmdb_id'], item.infoLabels['season']))
    inverso = True if db.cur.fetchone()[0] else False

    rows = db.get_episodes(item.infoLabels['tmdb_id'], item.infoLabels['season'], inverso)

    for season, episode, infolabels in rows:
        subtitulo = valor_infolabel('episodio_titulo', infolabels)
        if subtitulo == '': subtitulo = 'Capítulo ' + str(infolabels['episode'])

        titulo = str(infolabels['season']) + 'x' + str(infolabels['episode']) + ' ' + str(subtitulo)

        thumbnail = valor_infolabel_informado(['episodio_imagen','thumbnail'], infolabels)
        if thumbnail == '': thumbnail = item.thumbnail

        fanart = valor_infolabel('fanart', infolabels)
        if fanart == '': fanart = item.fanart

        context = [ {'title': 'Gestionar episodio', 'channel': item.channel, 'action': 'acciones_episodio'} ]

        itemlist.append(item.clone( action='findvideos', title=titulo, thumbnail = thumbnail, fanart = fanart, infoLabels = infolabels, context=context ))

    db.close()

    return itemlist


# Seleccionar canal dónde reproducir y devolver itemlist llamando a su findvideos.
# El item recibido tendrá los datos mínimos para mantener las marcas de visto/no visto de Kodi (ver en platformtools render_items)
# Datos mínimos: contentType, infoLabels['tmdb_id'] y en caso de episodio también infoLabels['season'], infoLabels['episode'].
def findvideos(item):
    logger.info()

    color_list_prefe = config.get_setting('channels_list_prefe_color', default='gold')
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')
    color_list_inactive = config.get_setting('channels_list_inactive_color', default='gray')

    db = trackingtools.TrackingData()

    opciones = []; opciones_row = []
    if item.contentType == 'movie':
        rows = db.get_movie_channels(item.infoLabels['tmdb_id'])
        infolabels = db.get_movie(item.infoLabels['tmdb_id'])
    else:
        try:
            rows = db.get_episode_channels(item.infoLabels['tmdb_id'], item.infoLabels['season'], item.infoLabels['episode'])
            infolabels = db.get_episode(item.infoLabels['tmdb_id'], item.infoLabels['season'], item.infoLabels['episode'])
        except:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No se localizaron Enlaces[/COLOR][/B]' % color_exec)
            return None

    from core import channeltools

    for channel, url in rows:
        ch_parms = channeltools.get_channel_parameters(channel)

        # no tener en cuenta canales que ya no existan o estén desactivados
        if ch_parms['active']:
            info = ''

            if ch_parms['status'] == 1: info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
            elif ch_parms['status'] == -1: info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

            cfg_proxies_channel = 'channel_' + ch_parms['id'] + '_proxies'
            if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies

            tipos = ch_parms['search_types']
            tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')

            if ch_parms['searchable'] == False:
                tipos = str(tipos).replace('movie', 'Vídeos')
                tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series')
            else:
                tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '')

            if info: info = info + '  '
            info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

            idiomas = ch_parms['language']
            idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
            idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose')

            if info: info = info + '  '
            info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

            opciones.append(platformtools.listitem_to_select(ch_parms['name'], info, ch_parms['thumbnail']))
            opciones_row.append([channel, url])

    db.close()

    if len(opciones) == 0:
        platformtools.dialog_ok(config.__addon_name, '[B][COLOR %s]No hay enlaces guardados con ningún canal, ó, No hay guardado ningún canal activo con enlaces.[/B][/COLOR]' % color_adver)
        return None

    # Sólo hay un canal, ir a él directamente
    elif len(opciones) == 1: ret = 0

    else:
        # canal preferente preseleccionado u ordenar por updated o último usado ?
        ret = platformtools.dialog_select('¿ De qué canal quieres los enlaces ?', opciones, useDetails=True)
        if ret == -1: return None

    it_sel = Item().fromurl(opciones_row[ret][1])

    # Añadir infoLabels pq las urls se guardan sin ellos
    it_sel.infoLabels = infolabels

    canal = __import__('channels.' + opciones_row[ret][0], fromlist=[''])
    if hasattr(canal, 'findvideos'): itemlist = canal.findvideos(it_sel)
    else: itemlist = servertools.find_video_items(it_sel)

    # Para algunos servers (ej: gamovideo) se necesita guardar la url para usar como referer
    if itemlist:
        if len(itemlist) > 0: itemlist[0].parent_item_url = it_sel.url

    return itemlist


# Acciones desde menú contextual
def info_tracking_shows(item):
    logger.info()

    db = trackingtools.TrackingData()
    db.cur.execute('SELECT a.tmdb_id, a.periodicity, a.tvdbinfo, a.lastscrap, b.title FROM tracking_shows a LEFT JOIN shows b ON a.tmdb_id = b.tmdb_id')
    series = db.cur.fetchall()
    db.close()

    txt = '%d Series con búsqueda de nuevos episodios.' % len(series)

    if config.get_setting('addon_tracking_atstart', default=True):
        interval = config.get_setting('addon_tracking_interval', default='12')
        lastscrap = config.get_setting('addon_tracking_lastscrap', default='')
        dt_scrap = datetime.fromtimestamp(float(lastscrap))
        txt += ' El servicio de búsqueda se ejecuta cada %d horas. Última ejecución: %s.' % (int(interval), dt_scrap.strftime('%d/%m/%Y a las %H:%M'))
    else:
        txt += ' Servicio de búsqueda desactivado en la configuración del addon.'

    for tmdb_id, periodicity, tvdbinfo, lastscrap, title in series:
        txt += '[CR][CR][B][COLOR gold]%s[/COLOR][/B], con tmdb_id %s : ' % (title.encode('utf-8'), tmdb_id.encode('utf-8'))
        periodicity = int(periodicity)
        if periodicity == 0: txt += ' cada vez que se ejecute el servicio'
        elif periodicity == 24: txt += ' una vez al día'
        elif periodicity == 48: txt += ' cada dos días'
        elif periodicity == 72: txt += ' cada tres días'
        elif periodicity == 24*7: txt += ' una vez por semana'
        else: txt += ' cada %d horas' % periodicity

        txt += ', con datos de TVDB.' if tvdbinfo == 1 else '.'

        if lastscrap: 
            dt_scrap = datetime.fromtimestamp(float(lastscrap))
            txt += ' Última comprobación: %s.' % dt_scrap.strftime('%A %d/%m/%Y a las %H:%M')

    platformtools.dialog_textviewer('Info tracking new episodes', txt)
    return True


def doit_tracking_shows(item):
    logger.info()

    trackingtools.check_and_scrap_new_episodes(notification=True)
    return True


def acciones_peli(item):
    logger.info()
    tmdb_id = item.infoLabels['tmdb_id']

    db = trackingtools.TrackingData()

    acciones = []
    acciones.append('Información de enlaces guardados')
    acciones.append('Actualizar datos desde TMDB (themoviedb.org)')

    rows = db.get_movie_channels(tmdb_id)

    for channel, url in rows:
        el_canal = str(channel.encode('utf-8'))
        el_canal = el_canal.replace("b'", '').replace("'", '').strip()

        acciones.append('Eliminar enlaces del canal [COLOR blue]%s[/COLOR]' % el_canal)

    if len(rows) == 0: acciones.append('Eliminar película')
    elif len(rows) >= 1: acciones.append('Eliminar película')

    listas = []
    itemlist_listas = mainlist_listas(item)
    for it in itemlist_listas:
        # descarta item crear y lista activa
        if it.lista != '' and '[lista activa]' not in it.title: listas.append(it.title)

    if not len(listas) == 0:
        acciones.append('Mover película a otra lista')
        acciones.append('Copiar película a otra lista')

    # Si está ordenado por Updated opción para subirla a la primera de la lista modificando su updated.
    if config.get_setting('tracking_order_movies', default=0) == 0:
        acciones.append('Mostrar película al principio de la lista')

    # Tratamiento de la acción escogida
    ret = platformtools.dialog_select(item.contentTitle, acciones)
    if ret == -1:
        db.close()
        return False

    elif acciones[ret].startswith('Actualizar datos desde TMDB'):
        res, msg = trackingtools.update_infolabels_movie(tmdb_id)
        platformtools.dialog_notification('Actualizar de TMDB', msg)

    elif acciones[ret] == 'Mostrar película al principio de la lista':
        db.cur.execute('UPDATE movies SET updated=? WHERE tmdb_id=?', (datetime.now(), tmdb_id))

    elif acciones[ret] == 'Eliminar película':
        if not platformtools.dialog_yesno('Eliminar película', '¿Confirma Eliminar la película [COLOR gold][B]%s[/B][/COLOR] con tmdb_id: %s ?' % (item.contentTitle, tmdb_id)): return False
        db.delete_movie(tmdb_id)

    elif acciones[ret].startswith('Eliminar enlaces del canal '):
        channel = config.quitar_colores(acciones[ret].replace('Eliminar enlaces del canal ', ''))
        if not platformtools.dialog_yesno('Eliminar enlaces Película', '¿Confirma Elimiar los enlaces del canal [COLOR blue][B]%s[/B][/COLOR] ?' % channel): return False

        el_canal = str(channel)
        el_canal = el_canal.replace("b'", '').replace("'", '').strip()
        db.delete_movie_channel(tmdb_id, el_canal)

    elif acciones[ret] == 'Información de enlaces guardados':
        txt = 'Película [B][COLOR gold]%s[/COLOR][/B] con tmdb_id: %s' % (item.contentTitle, tmdb_id)

        if len(rows) > 0:
            links_channels = ''

            for channel, url in rows:
                el_canal = str(channel.encode('utf-8'))
                el_canal = el_canal.replace("b'", '').replace("'", '').strip()
                links_channels += '[CR][CR]Con enlace al canal: [COLOR blue]%s[/COLOR]' % el_canal.capitalize()

            txt += links_channels 
        else:
            txt += '[CR][CR]No hay enlaces guardados con ningún canal.'

        db.close()
        platformtools.dialog_textviewer('Información de enlaces guardados', txt)
        return True

    elif acciones[ret] == 'Copiar película a otra lista' or acciones[ret] == 'Mover película a otra lista':
        operacion = 'copiada' if acciones[ret] == 'Copiar película a otra lista' else 'movida'

        # Diálogo para escoger lista
        opciones = []
        itemlist_listas = mainlist_listas(item)
        for it in itemlist_listas:
            # descarta item crear y lista activa
            if it.lista != '' and '[lista activa]' not in it.title: opciones.append(it.title)

        if len(opciones) == 0:
            db.close()
            platformtools.dialog_ok(config.__addon_name, 'No hay otras listas dónde mover el enlace.', '[COLOR yellow]Puedes crearlas desde la opción Gestionar listas.[/COLOR]')
            return False

        ret2 = platformtools.dialog_select('Seleccionar lista destino', opciones)
        if ret2 == -1: 
            db.close()
            return False

        dbname_destino = opciones[ret2]
        filename_destino = filetools.join(trackingtools.get_tracking_path(), dbname_destino + '.sqlite')

        db.cur.execute('ATTACH DATABASE ? AS db_destino', (filename_destino,))

        db.cur.execute('DELETE FROM db_destino.movies WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('DELETE FROM db_destino.channels_movies WHERE tmdb_id=?', (tmdb_id,))

        db.cur.execute('INSERT INTO db_destino.movies SELECT * FROM movies WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('INSERT INTO db_destino.channels_movies SELECT * FROM channels_movies WHERE tmdb_id=?', (tmdb_id,))

        if operacion == 'movida':
            db.cur.execute('DELETE FROM movies WHERE tmdb_id=?', (tmdb_id,))
            db.cur.execute('DELETE FROM channels_movies WHERE tmdb_id=?', (tmdb_id,))

        try:
            db.cur.execute('DETACH DATABASE db_destino')
        except:
            platformtools.dialog_notification(config.__addon_name, '[COLOR cyan][B]Database destino Locked[/B][/COLOR]')

        platformtools.dialog_notification(acciones[ret], '[COLOR gold]%s[/COLOR] %s a lista [COLOR blue][B]%s[/B][/COLOR]' % (item.contentTitle, operacion, dbname_destino) )
        if operacion == 'copiada':
            # No necesita itemlist_refresh posterior
            db.close(commit=True)
            return True

    db.close(commit=True)

    platformtools.itemlist_refresh()
    return True


def acciones_serie(item):
    logger.info()
    tmdb_id = item.infoLabels['tmdb_id']

    db = trackingtools.TrackingData()

    acciones = []
    acciones.append('Información de enlaces guardados')
    acciones.append('Programar búsqueda automática de nuevos episodios')
    acciones.append('Buscar ahora nuevos episodios')
    acciones.append('Actualizar datos desde TMDB (themoviedb.org)')
    acciones.append('Actualizar datos desde TVDB (thetvdb.com)')

    # 'Vista/No vista' => bucle para todas las temporadas/episodios y marcarlos en bd_kodi_files !? De momento por temporada.

    # Diferentes canales con enlaces ya sea en serie, temporadas o episodios
    sql = 'SELECT DISTINCT channel FROM ('
    sql += ' SELECT DISTINCT channel FROM channels_shows WHERE tmdb_id=?'
    sql += ' UNION'
    sql += ' SELECT DISTINCT channel FROM channels_seasons WHERE tmdb_id=?'
    sql += ' UNION'
    sql += ' SELECT DISTINCT channel FROM channels_episodes WHERE tmdb_id=?'
    sql += ')'
    db.cur.execute(sql, (tmdb_id,tmdb_id,tmdb_id))

    # Ej: [(u'seriesblanco',), (u'seriespapaya',)]
    canales = db.cur.fetchall()

    for (channel,) in canales:
        el_canal = str(channel.encode('utf-8'))
        el_canal = el_canal.replace("b'", '').replace("'", '').strip()

        acciones.append('Eliminar enlaces del canal [COLOR blue]%s[/COLOR]' % el_canal)

    if len(canales) == 0: acciones.append('Eliminar serie')
    elif len(canales) >= 1: acciones.append('Eliminar serie')

    listas = []
    itemlist_listas = mainlist_listas(item)

    for it in itemlist_listas:
        # descarta item crear y lista activa
        if it.lista != '' and '[lista activa]' not in it.title: listas.append(it.title)

    if not len(listas) == 0:
        acciones.append('Mover serie a otra lista')
        acciones.append('Copiar serie a otra lista')

    # Si está ordenado por Updated opción para subirla a la primera de la lista modificando su updated.
    if config.get_setting('tracking_order_tvshows', default=0) == 0:
        acciones.append('Mostrar serie al principio de la lista')

    # Tratamiento de la acción escogida
    ret = platformtools.dialog_select(item.contentSerieName, acciones)

    if ret == -1:
        db.close()
        return False

    elif acciones[ret] == 'Mostrar serie al principio de la lista':
        db.cur.execute('UPDATE shows SET updated=? WHERE tmdb_id=?', (datetime.now(), tmdb_id))

    elif acciones[ret] == 'Eliminar serie':
        if not platformtools.dialog_yesno('Eliminar serie', '¿Confirma Eliminar la serie [COLOR gold][B]%s[/B][/COLOR] con tmdb_id: %s ?' % (item.contentSerieName, tmdb_id)): return False
        db.delete_show(tmdb_id)

    elif acciones[ret].startswith('Eliminar enlaces del canal '):
        channel = config.quitar_colores(acciones[ret].replace('Eliminar enlaces del canal ', ''))
        if not platformtools.dialog_yesno('Eliminar enlaces Serie', '¿Confirma Eliminar los enlaces del canal [COLOR blue][B]%s[/B][/COLOR] ?' % channel): return False

        el_canal = str(channel)
        el_canal = el_canal.replace("b'", '').replace("'", '').strip()

        db.delete_show_channel(tmdb_id, el_canal)

    elif acciones[ret].startswith('Actualizar datos desde TMDB'):
        res, msg = trackingtools.update_infolabels_show(tmdb_id)
        platformtools.dialog_notification('Actualizar de TMDB', msg)

    elif acciones[ret].startswith('Actualizar datos desde TVDB'):
        res, msg = trackingtools.update_infolabels_show(tmdb_id, with_tvdb=True)
        platformtools.dialog_notification('Actualizar de TVDB', msg)

    elif acciones[ret] == 'Información de enlaces guardados':
        txt = 'Serie [B][COLOR gold]%s[/COLOR][/B] con tmdb_id: %s' % (item.contentSerieName, tmdb_id)

        # Mostrar info de tracking
        db.cur.execute('SELECT periodicity, tvdbinfo, lastscrap FROM tracking_shows WHERE tmdb_id=?', (tmdb_id,))
        row = db.cur.fetchone()
        if row is not None:
            periodicity = int(row[0])
            # ~ txt += ', tiene activada la búsqueda automática de nuevos episodios cada %d horas' % int(row[0])

            txt += ', tiene activada la búsqueda automática de nuevos episodios'
            if row[1] == 1: txt += ' con datos de TVDB'
            if periodicity == 0: txt += ' cada vez que se ejecute el servicio.'
            elif periodicity == 24: txt += ' una vez al día.'
            elif periodicity == 48: txt += ' cada dos días.'
            elif periodicity == 72: txt += ' cada tres días.'
            elif periodicity == 24*7: txt += ' una vez por semana.'
            else: txt += ' cada %d horas.' % periodicity

            if row[2]:
                dt_scrap = datetime.fromtimestamp(float(row[2]))
                txt += ' Última comprobación: %s.' % dt_scrap.strftime('%A %d/%m/%Y a las %H:%M')

        # Mostrar info de infolabels
        db.cur.execute('SELECT COUNT(*) FROM episodes WHERE tmdb_id=?', (tmdb_id,))
        num_epi = db.cur.fetchone()[0]
        db.cur.execute('SELECT season FROM seasons WHERE tmdb_id=? ORDER BY season ASC', (tmdb_id,))
        seasons = db.cur.fetchall()
        txt += '[CR][CR]%d episodios en %d temporadas. ' % (num_epi, len(seasons))
        for (season,) in seasons:
            db.cur.execute('SELECT COUNT(*) FROM episodes WHERE tmdb_id=? AND season=?', (tmdb_id, season))
            num_epi = db.cur.fetchone()[0]
            txt += ' [B]T%d[/B] (%d)' % (season, num_epi)

        # Mostrar info de enlaces
        txt += '[CR][CR]Enlaces a nivel de serie y temporadas:'
        for (channel,) in canales:
            guardados = []
            links_channels = ''

            db.cur.execute('SELECT channel FROM channels_shows WHERE tmdb_id=? AND channel=?', (tmdb_id, channel.encode('utf-8')))
            if db.cur.fetchone() is not None: guardados.append('Serie')

            db.cur.execute('SELECT season FROM channels_seasons WHERE tmdb_id=? AND channel=? ORDER BY season ASC', (tmdb_id, channel.encode('utf-8')))
            enlaces = db.cur.fetchall()
            for (season,) in enlaces:
                guardados.append('T%d' % season)

            if len(guardados) > 0:
                if 'Serie' in guardados and len(guardados) == 1: guardados = ['Temporadas y episodios en un mismo enlace']

                #for channel in guardados:
                el_canal = str(channel.encode('utf-8'))
                el_canal = el_canal.replace("b'", '').replace("'", '').strip()
                lo_guardado = str(guardados)
                lo_guardado = lo_guardado.replace("['", '').replace("']", '').strip()
                links_channels += ('[CR][CR] - Con enlace al canal [COLOR blue]%s[/COLOR] ' + lo_guardado + '.') % el_canal.capitalize()

                txt += links_channels 
            else:
                el_canal = str(channel.encode('utf-8'))
                el_canal = el_canal.replace("b'", '').replace("'", '').strip()
                links_channels += ('[CR][CR]Con enlace al canal: [COLOR blue]%s[/COLOR] ' 'episodios sueltos.') % el_canal.capitalize()

                txt += links_channels 

        txt += '[CR][CR]Episodios por canal:'
        for (channel,) in canales:
            # ~ db.cur.execute('SELECT season, episode FROM channels_episodes WHERE tmdb_id=? AND channel=? ORDER BY season ASC, episode ASC', (tmdb_id, channel.encode('utf-8')))
            # ~ enlaces = db.cur.fetchall()
            # ~ if len(enlaces) > 0:
                # ~ txt += '[CR][COLOR blue]%s[/COLOR]:' % channel.encode('utf-8')
                # ~ for season, episode in enlaces:
                    # ~ txt += ' %dx%d' % (season, episode)

            db.cur.execute('SELECT season, COUNT() FROM channels_episodes WHERE tmdb_id=? AND channel=? GROUP BY season ORDER BY season ASC', (tmdb_id, channel.encode('utf-8')))
            enlaces = db.cur.fetchall()
            if len(enlaces) > 0:
                links_channels = ''

                for season, count in enlaces:
                    el_canal = str(channel.encode('utf-8'))
                    el_canal = el_canal.replace("b'", '').replace("'", '').strip()
                    links_channels += '[CR][CR] - Con enlace al canal [COLOR blue]%s[/COLOR] T%d (%d)' % (el_canal.capitalize(), season, count)

                txt += links_channels 

        db.close()
        platformtools.dialog_textviewer('Información de enlaces guardados', txt)
        return True

    elif acciones[ret] == 'Programar búsqueda automática de nuevos episodios':
        db.cur.execute('SELECT periodicity, tvdbinfo FROM tracking_shows WHERE tmdb_id=?', (tmdb_id,))
        row = db.cur.fetchone()
        if row is not None:
            if platformtools.dialog_yesno('Tracking', '¿ Desactivar la búsqueda automática de nuevos episodios para la serie [COLOR gold][B]%s[/B][/COLOR] con tmdb_id: %s ?' % (item.contentSerieName, tmdb_id)):
                db.cur.execute('DELETE FROM tracking_shows WHERE tmdb_id=?', (tmdb_id,))
                platformtools.dialog_notification(item.contentSerieName, '[B][COLOR %s]Desactivada búsqueda automática de nuevos episodios[/B][/COLOR]' % color_adver)
                cambiar_opciones = False
            else:
                cambiar_opciones = True
        else:
            if not platformtools.dialog_yesno('Tracking', '¿ Activar la búsqueda automática de nuevos episodios para la serie [COLOR gold][B]%s[/B][/COLOR] con tmdb_id: %s ?' % (item.contentSerieName, tmdb_id)):
                db.close()
                return False

            cambiar_opciones = True

        if cambiar_opciones:
            opciones = ['Cada vez que se ejecute el servicio', 'Una vez al día', 'Cada dos días', 'Cada tres días', 'Cada semana']
            ret = platformtools.dialog_select('¿ Cada cuanto comprobar si hay nuevos episodios ?', opciones)
            if ret == -1:
                db.close()
                return False

            periodicity = 0 if ret == 0 else 24 if ret == 1 else 48 if ret == 2 else 72 if ret == 3 else 24*7
            tvdbinfo = platformtools.dialog_yesno('Tracking', '¿ Desea que se acceda a TVDB para recuperar datos de los nuevos episodios ? (bastante más lento pero en algunos casos se obtiene más información)')

            db.cur.execute('INSERT OR REPLACE INTO tracking_shows (tmdb_id, updated, periodicity, tvdbinfo) VALUES (?, ?, ?, ?)', (tmdb_id, datetime.now(), periodicity, tvdbinfo))
            platformtools.dialog_notification(item.contentSerieName, '[B][COLOR %s]Activada búsqueda automática de nuevos episodios[/B][/COLOR]' % color_infor)

    elif acciones[ret] == 'Buscar ahora nuevos episodios':
        db.cur.execute('SELECT tvdbinfo FROM tracking_shows WHERE tmdb_id=?', (tmdb_id,))
        row = db.cur.fetchone()
        tvdbinfo = False if row is None else True if row[0] == 1 else False
        db.close()

        done, msg = trackingtools.search_new_episodes(tmdb_id, show_progress=True, tvdbinfo=tvdbinfo)
        return True

    elif acciones[ret] == 'Copiar serie a otra lista' or acciones[ret] == 'Mover serie a otra lista':
        operacion = 'copiada' if acciones[ret] == 'Copiar serie a otra lista' else 'movida'

        # Diálogo para escoger lista
        opciones = []
        itemlist_listas = mainlist_listas(item)
        for it in itemlist_listas:
            # descarta item crear y lista activa
            if it.lista != '' and '[lista activa]' not in it.title: opciones.append(it.title)

        if len(opciones) == 0:
            db.close()
            platformtools.dialog_ok(config.__addon_name, 'No hay otras listas dónde mover el enlace.', '[COLOR yellow]Puedes crearlas desde la opción Gestionar listas.[/COLOR]')
            return False

        ret2 = platformtools.dialog_select('Seleccionar lista destino', opciones)
        if ret2 == -1:
            db.close()
            return False

        dbname_destino = opciones[ret2]
        filename_destino = filetools.join(trackingtools.get_tracking_path(), dbname_destino + '.sqlite')

        db.cur.execute('ATTACH DATABASE ? AS db_destino', (filename_destino,))

        db.cur.execute('DELETE FROM db_destino.shows WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('DELETE FROM db_destino.channels_shows WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('DELETE FROM db_destino.seasons WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('DELETE FROM db_destino.channels_seasons WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('DELETE FROM db_destino.episodes WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('DELETE FROM db_destino.channels_episodes WHERE tmdb_id=?', (tmdb_id,))

        db.cur.execute('INSERT INTO db_destino.shows SELECT * FROM shows WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('INSERT INTO db_destino.channels_shows SELECT * FROM channels_shows WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('INSERT INTO db_destino.seasons SELECT * FROM seasons WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('INSERT INTO db_destino.channels_seasons SELECT * FROM channels_seasons WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('INSERT INTO db_destino.episodes SELECT * FROM episodes WHERE tmdb_id=?', (tmdb_id,))
        db.cur.execute('INSERT INTO db_destino.channels_episodes SELECT * FROM channels_episodes WHERE tmdb_id=?', (tmdb_id,))

        if operacion == 'movida':
            db.cur.execute('DELETE FROM shows WHERE tmdb_id=?', (tmdb_id,))
            db.cur.execute('DELETE FROM channels_shows WHERE tmdb_id=?', (tmdb_id,))
            db.cur.execute('DELETE FROM seasons WHERE tmdb_id=?', (tmdb_id,))
            db.cur.execute('DELETE FROM channels_seasons WHERE tmdb_id=?', (tmdb_id,))
            db.cur.execute('DELETE FROM episodes WHERE tmdb_id=?', (tmdb_id,))
            db.cur.execute('DELETE FROM channels_episodes WHERE tmdb_id=?', (tmdb_id,))

        try:
            db.cur.execute('DETACH DATABASE db_destino')
        except:
            platformtools.dialog_notification(config.__addon_name, '[COLOR cyan][B]Database destino Locked[/B][/COLOR]')

        platformtools.dialog_notification(acciones[ret], '[COLOR gold]%s[/COLOR] %s a lista [COLOR blue][B]%s[/B][/COLOR]' % (item.contentSerieName, operacion, dbname_destino) )
        if operacion == 'copiada':
            # No necesita itemlist_refresh posterior
            db.close(commit=True)
            return True

    db.close(commit=True)

    platformtools.itemlist_refresh()
    return True


def acciones_temporada(item):
    logger.info()
    tmdb_id = item.infoLabels['tmdb_id']
    season = item.infoLabels['season']

    acciones = []
    acciones.append('Invertir el orden en que se muestran los episodios')
    acciones.append('Actualizar desde TMDB los episodios de la Temporada %d' % season)
    acciones.append('Actualizar desde TVDB los episodios de la Temporada %d' % season)
    acciones.append('Marcar como vistos todos los episodios de la Temporada %d' % season)
    acciones.append('Marcar como no vistos todos los episodios de la Temporada %d' % season)
    acciones.append('Eliminar la Temporada %d' % season)

    # Tratamiento de la acción escogida
    ret = platformtools.dialog_select('Acción a ejecutar', acciones)
    if ret == -1: return False

    elif acciones[ret].startswith('Invertir el orden'):
        db = trackingtools.TrackingData()
        db.cur.execute('SELECT reverseorder FROM seasons WHERE tmdb_id=? AND season=?', (tmdb_id, season))
        inverso = 0 if db.cur.fetchone()[0] else 1
        db.cur.execute('UPDATE seasons SET reverseorder=? WHERE tmdb_id=? AND season=?', (inverso, tmdb_id, season))
        db.close(commit=True)
        return True

    elif acciones[ret].startswith('Actualizar desde TMDB'):
        res, msg = trackingtools.update_infolabels_episodes(tmdb_id, season)
        platformtools.dialog_notification('Actualizar de TMDB', msg)

    elif acciones[ret].startswith('Actualizar desde TVDB'):
        res, msg = trackingtools.update_infolabels_episodes(tmdb_id, season, with_tvdb=True)
        platformtools.dialog_notification('Actualizar de TVDB', msg)

    elif acciones[ret].startswith('Marcar como vistos'):
        res = trackingtools.update_season_watched(tmdb_id, season, True)
        msg = 'Ok, todos los episodios marcados como vistos.' if res else 'No se han podido marcar los episodios.'
        platformtools.dialog_notification('Temporada %d' % season, msg)

    elif acciones[ret].startswith('Marcar como no vistos'):
        res = trackingtools.update_season_watched(tmdb_id, season, False)
        msg = 'Ok, todos los episodios marcados como NO vistos.' if res else 'No se han podido marcar los episodios.'
        platformtools.dialog_notification('Temporada %d' % season, msg)

    elif acciones[ret].startswith('Eliminar'):
        if not platformtools.dialog_yesno('Eliminar temporada', '¿ Confirma Eliminar la [COLOR gold][B]Temporada %d[/B][/COLOR] de la serie [COLOR gold][B]%s[/B][/COLOR] y todos sus episodios ?' % (season, item.contentSerieName)): return False
        db = trackingtools.TrackingData()
        db.delete_season(tmdb_id, season)
        db.close(commit=True)

    platformtools.itemlist_refresh()
    return True


def acciones_episodio(item):
    logger.info()
    tmdb_id = item.infoLabels['tmdb_id']
    season = item.infoLabels['season']
    episode = item.infoLabels['episode']

    acciones = []
    acciones.append('Actualizar desde TMDB el episodio %d x %d' % (season, episode))
    acciones.append('Actualizar desde TVDB el episodio %d x %d' % (season, episode))
    acciones.append('Eliminar el episodio %d x %d' % (season, episode))

    # Tratamiento de la acción escogida
    ret = platformtools.dialog_select('Acción a ejecutar', acciones)
    if ret == -1: return False

    elif acciones[ret].startswith('Actualizar desde TMDB'):
        res, msg = trackingtools.update_infolabels_episodes(tmdb_id, season, episode)
        platformtools.dialog_notification('Actualizar de TMDB', msg)

    elif acciones[ret].startswith('Actualizar desde TVDB'):
        res, msg = trackingtools.update_infolabels_episodes(tmdb_id, season, episode, with_tvdb=True)
        platformtools.dialog_notification('Actualizar de TVDB', msg)

    elif acciones[ret].startswith('Eliminar'):
        if not platformtools.dialog_yesno('Eliminar episodio', '¿ Confirma Eliminar el episodio [COLOR gold][B]%dx%d[/B][/COLOR] de la serie [COLOR gold][B]%s[/B][/COLOR] ?' % (season, episode, item.contentSerieName)): return False
        db = trackingtools.TrackingData()
        db.delete_episode(tmdb_id, season, episode)
        db.close(commit=True)

    platformtools.itemlist_refresh()
    return True


# Para poder gestionar varias bases de datos de tracking
def mainlist_listas(item):
    logger.info()
    itemlist = []

    item.category = 'Listas'

    current_dbname = trackingtools.get_current_dbname()
    tracking_path = trackingtools.get_tracking_path()

    import glob

    path = filetools.join(tracking_path, '*.sqlite')

    for fichero in glob.glob(path):
        lista = filetools.basename(fichero)
        nombre = lista.replace('.sqlite', '')
        titulo = nombre if nombre != current_dbname else '[COLOR gold]%s[/COLOR] [lista activa]' % nombre

        # ídem que intro pero por si se accede al menú contextual
        context = [ {'title': 'Gestionar lista', 'channel': item.channel, 'action': 'acciones_lista', 'lista': lista} ]

        itemlist.append(item.clone(action='acciones_lista', lista=lista, title=titulo, folder=False, context=context))

    plot = 'Puedes crear varias listas para guardar películas y series. Por ejemplo una infantil, otras temáticas, otras para cada usuario, etc.'
    plot += ' Desde el menú contextual de cada película o serie tienes la opción de mover o copiar a otras listas.'

    itemlist.append(item.clone(action='crear_lista', title='Crear nueva lista ...', folder=False, plot=plot, thumbnail=config.get_thumb('booklet'))) 

    plot = 'Si tienes alguna lista en otros dispositivos de tu red puedes copiarla a este.'
    plot += ' Para poder hacerlo necesitas haber añadido tu dispositivo remoto como fuente desde Kodi y tener acceso a la carpeta dónde tengas las listas.'

    itemlist.append(item.clone(action='copiar_lista', title='Copiar de otro dispositivo ...', folder=False, plot=plot, thumbnail=config.get_thumb('computer'))) 

    return itemlist


def copiar_lista(item):
    logger.info()

    import xbmcgui

    # 1:ShowAndGetFile
    origen = xbmcgui.Dialog().browseSingle(1, 'Selecciona el fichero .sqlite a copiar', 'files', '.sqlite', False, False, '')
    if origen is None or origen == '': return False

    lista_origen = filetools.basename(origen)
    destino = filetools.join(trackingtools.get_tracking_path(), lista_origen)

    if filetools.exists(destino):
        lista_origen = lista_origen.replace('.sqlite', '') + '-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.sqlite'
        destino = filetools.join(trackingtools.get_tracking_path(), lista_origen)
        platformtools.dialog_ok(config.__addon_name, 'Ya existe una lista con este nombre, se le añade un sufijo para diferenciarla.', lista_origen)

    if not filetools.copy(origen, destino, silent=False):
        platformtools.dialog_ok(config.__addon_name, 'Error, no se ha podido copiar la lista', origen, destino)
        return False

    platformtools.itemlist_refresh()
    return True


def crear_lista(item):
    logger.info()

    titulo = platformtools.dialog_input(default='', heading='Nombre de la lista')
    if titulo is None or titulo == '': return False

    titulo = config.text_clean(titulo, blank_char='_')

    filename = titulo.replace('.sqlite', '') + '.sqlite'
    fullfilename = filetools.join(trackingtools.get_tracking_path(), filename)

    # Comprobar que el fichero no exista ya
    if filetools.exists(fullfilename):
        platformtools.dialog_ok(config.__addon_name, 'Error, ya existe una lista con este nombre', filename)
        return False

    # Provocar que se guarde
    db = trackingtools.TrackingData(filename)
    db.close(commit=True)

    platformtools.itemlist_refresh()
    return True


def acciones_lista(item):
    logger.info()

    acciones = ['Establecer como lista activa', 'Cambiar nombre de la lista', 'Eliminar lista', 'Información de la lista'] 

    ret = platformtools.dialog_select(item.lista, acciones)

    if ret == -1: return False
    elif ret == 0: return activar_lista(item)
    elif ret == 1: return renombrar_lista(item)
    elif ret == 2: return eliminar_lista(item)
    elif ret == 3: return informacion_lista(item)


def activar_lista(item):
    logger.info()

    fullfilename = filetools.join(trackingtools.get_tracking_path(), item.lista)
    if not filetools.exists(fullfilename):
        platformtools.dialog_ok(config.__addon_name, 'Error, no se encuentra la lista', item.lista)
        return False

    trackingtools.set_current_dbname(item.lista)

    # ~ platformtools.itemlist_refresh() # mejor con replace=True para que no haya problemas si se vuelve atrás

    item_inicio = Item( channel='tracking', action='mainlist', title='Seguimiento', thumbnail=config.get_thumb('videolibrary') )
    platformtools.itemlist_update(item_inicio, replace=True)
    return True


def renombrar_lista(item):
    logger.info()

    fullfilename_current = filetools.join(trackingtools.get_tracking_path(), item.lista)
    if not filetools.exists(fullfilename_current):
        platformtools.dialog_ok(config.__addon_name, 'Error, no se encuentra la lista', item.lista)
        return False

    nombre = item.lista.replace('.sqlite', '')
    titulo = platformtools.dialog_input(default=nombre, heading='Nombre de la lista')
    if titulo is None or titulo == '' or titulo == nombre: return False

    filename = titulo + '.sqlite'
    fullfilename = filetools.join(trackingtools.get_tracking_path(), filename)

    # Comprobar que el nuevo nombre no exista
    if filetools.exists(fullfilename):
        platformtools.dialog_ok(config.__addon_name, 'Error, ya existe una lista con este nombre!', filename)
        return False

    # Rename del fichero
    if not filetools.rename(fullfilename_current, filename):
        platformtools.dialog_ok(config.__addon_name, 'Error, no se pudo renombrar la lista!', filename)
        return False

    # Update settings si es la lista activa
    if item.lista.replace('.sqlite', '') == trackingtools.get_current_dbname():
        trackingtools.set_current_dbname(filename)

    platformtools.itemlist_refresh()
    return True


def eliminar_lista(item):
    logger.info()

    fullfilename = filetools.join(trackingtools.get_tracking_path(), item.lista)
    if not filetools.exists(fullfilename):
        platformtools.dialog_ok(config.__addon_name, 'Error, no se encuentra la lista', item.lista)
        return False

    if item.lista.replace('.sqlite', '') == trackingtools.get_current_dbname():
        platformtools.dialog_ok(config.__addon_name, 'La lista activa no se puede eliminar', item.lista)
        return False

    if not platformtools.dialog_yesno('Eliminar lista', '[COLOR red][B]¿ Confirma Eliminar la lista %s ?[/B][/COLOR]' % item.lista):
        return False

    filetools.remove(fullfilename)

    platformtools.itemlist_refresh()
    return True


def informacion_lista(item):
    logger.info()

    fullfilename = filetools.join(trackingtools.get_tracking_path(), item.lista)
    if not filetools.exists(fullfilename):
        platformtools.dialog_ok(config.__addon_name, 'Error, no se encuentra la lista', item.lista)
        return False

    db = trackingtools.TrackingData(item.lista)
    count_movies = db.get_movies_count()
    count_shows = db.get_shows_count()
    count_episodes = db.get_episodes_count()
    db.close()

    txt = 'Nombre: [COLOR gold]%s[/COLOR]' % item.lista

    txt += '[CR][CR]Número de películas: [B]%d[/B]' % count_movies
    txt += '[CR][CR]Número de series: [B]%d[/B]' % count_shows
    txt += '[CR][CR]Número de episodios: [B]%d[/B]' % count_episodes

    txt += '[CR][CR]Tamaño de la base de datos: [B]%s[/B]' % config.format_bytes(filetools.getsize(fullfilename))

    platformtools.dialog_textviewer('Información de la lista', txt)
    return True
