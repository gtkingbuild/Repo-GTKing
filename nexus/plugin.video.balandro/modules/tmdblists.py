# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools

from core.item import Item
from core import tmdb


thumbs = 'https://image.tmdb.org/'


def mainlist(item):
    logger.info()
    itemlist = []

    item.category = 'TMDB'

    itemlist.append(item.clone( action='show_help', title='[COLOR green][B]Información[/B][/COLOR] TMDB', folder=False, thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( action='', title= '[B]Búsquedas a través de [COLOR pink]Personas[/COLOR]:[/B]', text_color='yellowgreen' ))

    itemlist.append(item.clone( action='personas', search_type='cast', title=' - Buscar [COLOR aquamarine]intérprete[/COLOR] ...', thumbnail=config.get_thumb('search'),
                                plot = 'Escribir el nombre de un actor o una actriz para listar todas las películas y series en las que ha intervenido.' ))

    itemlist.append(item.clone( action='personas', search_type='crew', title=' - Buscar [COLOR springgreen]dirección[/COLOR] ...', thumbnail=config.get_thumb('search'),
                                plot = 'Escribir el nombre de una persona para listar todas las películas y series que ha dirigido.' ))

    itemlist.append(item.clone( action='', title= '[B]Búsquedas a través de [COLOR pink]Listas[/COLOR]:[/B]', text_color='yellowgreen' ))

    itemlist.append(item.clone( action='listado_personas', search_type='person', extra = 'popular', title=' - [COLOR limegreen]Personas[/COLOR] más populares' ))

    presentar = True
    if item.search_type == 'tvshow': presentar = False
    elif item.search_type == 'documentary': presentar = False
    elif item.extra == 'mixed':
       if item.search_type == 'movie': presentar = False

    if presentar:
        itemlist.append(item.clone( title = '[B]Películas:[/B]', thumbnail=config.get_thumb('movie'), action = '', text_color='deepskyblue' ))

        if config.get_setting('search_extra_trailers', default=False):
            itemlist.append(item.clone( channel='trailers', action='search', title=' - Buscar en [COLOR darkgoldenrod]Tráilers[/COLOR] ...', thumbnail=config.get_thumb('search') ))

        itemlist.append(item.clone( action='search', title=' - Buscar [COLOR deepskyblue]título[/COLOR] ...', search_type='movie', thumbnail=config.get_thumb('search') ))

        itemlist.append(item.clone( action='listado', search_type='movie', extra = 'now_playing', title='   - En cartelera', thumbnail=config.get_thumb('novedades') ))
        itemlist.append(item.clone( action='listado', search_type='movie', extra = 'popular', title='   - Más populares', thumbnail=config.get_thumb('besttvshows') ))
        itemlist.append(item.clone( action='listado', search_type='movie', extra = 'top_rated', title='   - Mejor valoradas', thumbnail=config.get_thumb('besttvshows') ))

        # ~ itemlist.append(item.clone( action='listado', search_type='movie', url = 'movie/upcoming', title='   - Próximas' ))

        itemlist.append(item.clone( action='networks', search_type='movie', title='   - Por productora', thumbnail=config.get_thumb('booklet') ))
        itemlist.append(item.clone( action='generos', search_type='movie', title='   - Por género', thumbnail=config.get_thumb('listgenres') ))
        itemlist.append(item.clone( action='anios', search_type='movie', title='   - Por año', thumbnail=config.get_thumb('listyears') ))

    presentar = True
    if item.search_type == 'movie': presentar = False
    elif item.search_type == 'documentary': presentar = False
    elif item.extra == 'mixed':
       if item.search_type == 'tvshow': presentar = False

    if presentar:
        itemlist.append(item.clone( title = '[B]Series:[/B]', thumbnail=config.get_thumb('tvshow'), action = '', text_color='hotpink' ))

        itemlist.append(item.clone( action='search', title=' - Buscar [COLOR hotpink]título[/COLOR] ...', search_type='tvshow', thumbnail=config.get_thumb('search') ))

        itemlist.append(item.clone( action='listado', search_type='tvshow', extra = 'on_the_air', title='   - En emisión' ))
        itemlist.append(item.clone( action='listado', search_type='tvshow', extra = 'popular', title='   - Más populares', thumbnail=config.get_thumb('besttvshows') ))
        itemlist.append(item.clone( action='listado', search_type='tvshow', extra = 'top_rated', title='   - Mejor valoradas', thumbnail=config.get_thumb('besttvshows') ))

        # ~ itemlist.append(item.clone( action='listado', search_type='tvshow', url = 'tv/airing_today', title='   - Que se emiten Hoy' ))

        itemlist.append(item.clone( action='networks', search_type='tvshow', title='   - Por productora', thumbnail=config.get_thumb('booklet') ))
        itemlist.append(item.clone( action='generos', search_type='tvshow', title='   - Por género', thumbnail=config.get_thumb('listgenres') ))
        itemlist.append(item.clone( action='anios', search_type='tvshow', title='   - Por año', thumbnail=config.get_thumb('listyears') ))

    return itemlist


def show_help(item):
    txt = 'En este apartado se pueden hacer consultas a la web [COLOR gold][B]The Movie Database[/B][/COLOR] (TMDB), un proyecto comunitario que ofrece información de películas, series y personas.'

    txt += '[CR]'
    txt += '[CR]Se puede buscar la [COLOR moccasin][B]filmografía[/B][/COLOR] de una persona y ver las películas/series dónde ha participado.'

    txt += '[CR]'
    txt += '[CR]También se pueden ver distintas [COLOR yellow][B]Listas[/B][/COLOR] de películas y/ó series según varios conceptos (más populares, más valoradas, por géneros, etc.)'

    txt += '[CR]'
    txt += '[CR]Al seleccionar una película/serie [COLOR chartreuse][B]se iniciará su búsqueda en los canales[/B][/COLOR] y se mostrarán los resultados encontrados.'
    txt += ' Hay que tener en cuenta que habrá películas/series que no tendrán enlaces en ninguno de los canales.'

    txt += '[CR]'
    txt += '[CR]Si al buscar por persona [COLOR violet][B]se obtiene una sola coincidencia[/B][/COLOR] de películas, se listan directamente sus películas y series (Ej: Stanley Kubrick).'
    txt += ' Si hubierna varios resultados se muestra una [COLOR yellowgreen][B]Lista de Personas[/B][/COLOR] para seleccionar la que corresponda (Ej: Kubrick).'

    platformtools.dialog_textviewer('Información búsquedas y listas en TMDB', txt)
    return True


def texto_busqueda(txt):
    if ':' in txt: return txt.split(':')[1].strip()
    return txt


def lista(item, elementos):
    itemlist = []

    if not item.page: item.page = 1

    for elemento in elementos:
        titulo = elemento['title'] if 'title' in elemento else elemento['name']

        if 'title' in elemento:
            itemlist.append(item.clone( channel='search', action = 'search', buscando = texto_busqueda(titulo), from_channel = item.channel, title = titulo, search_type = 'movie', 
                                        contentType = 'movie', contentTitle = titulo, infoLabels = {'tmdb_id': elemento['id']} ))
        else:
            itemlist.append(item.clone( channel='search', action = 'search', buscando = texto_busqueda(titulo), from_channel = item.channel, title = titulo, search_type = 'tvshow', 
                                        contentType = 'tvshow', contentSerieName = titulo, infoLabels = {'tmdb_id': elemento['id']} ))

    tmdb.set_infoLabels(itemlist)

    if len(itemlist) > 0:
        itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, text_color='coral' ))

    return itemlist


def listado(item):
    logger.info()

    if not item.page: item.page = 1

    tipo = 'movie' if item.search_type == 'movie' else 'tv'
    elementos = tmdb.get_list(tipo, item.extra, item.page)

    return lista(item, elementos)


def descubre(item):
    logger.info()

    if not item.page: item.page = 1

    tipo = 'movie' if item.search_type == 'movie' else 'tv'
    elementos = tmdb.get_discover(tipo, item.extra, item.page)

    return lista(item, elementos)


def descubre_networks(item):
    logger.info()

    if not item.page: item.page = 1

    tipo = 'movie' if item.search_type == 'movie' else 'tv'
    elementos = tmdb.get_discover_networks(tipo, item.extra, item.page)

    return lista(item, elementos)


def generos(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    tipo = 'movie' if item.search_type == 'movie' else 'tv'
    elementos = tmdb.get_genres(tipo)

    for codigo, titulo in elementos[tipo].items():
        itemlist.append(item.clone( title=titulo, action='descubre', extra = codigo, text_color = text_color ))

    return sorted(itemlist, key=lambda it: it.title)


def networks(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    networks_list = {'8': ['Netflix', 'https://www.themoviedb.org//t/p/original/9A1JSVmSxsyaBK4SUFsYVqbAYfW.jpg'],
	'119': ['Amazon Prime Video', 'https://www.themoviedb.org//t/p/original/68MNrwlkpF7WnmNPXLah69CR5cb.jpg'],
	'337': ['Disney Plus', 'https://www.themoviedb.org//t/p/original/dgPueyEdOwpQ10fjuhL2WYFQwQs.jpg'],
	'2': ['Apple iTunes', 'https://www.themoviedb.org//t/p/original/q6tl6Ib6X5FT80RMlcDbexIo4St.jpg'],
	'3': ['Google Play Movies', 'https://www.themoviedb.org//t/p/original/p3Z12gKq2qvJaUOMeKNU2mzKVI9.jpg'],
	'118': ['HBO', 'https://www.themoviedb.org//t/p/original/vAtH6Z6Oq7zCmEGS3Sdu08dxvYZ.jpg'],
	'257': ['FuboTV', 'https://www.themoviedb.org//t/p/original/2wPRZit7b8u79GsqTdygmGL6kBW.jpg'],
	'11': ['Mubi', 'https://www.themoviedb.org//t/p/original/kXQQbZ6ZvTwojzMPivQF9sX0V4y.jpg'],
	'100': ['GuideDoc', 'https://www.themoviedb.org//t/p/original/nNQnRz0jQ7UOJVtifg64VFc4vDk.jpg'],
	'63': ['Filmin', 'https://www.themoviedb.org//t/p/original/j3SNvXPH2hRvH7MEvc2fGRLt9q2.jpg'],
	'64': ['Filmin Plus', 'https://www.themoviedb.org//t/p/original/rEylX9XTOCSmUD0kHz1af8ZMqLe.jpg'],
	'149': ['Movistar Plus', 'https://www.themoviedb.org//t/p/original/3kZQY7nIwC5sIJmURyF6W91pAkg.jpg'],
	'457': ['VIX ', 'https://www.themoviedb.org//t/p/original/p5RDRIibqNyPq40YU4L7raTaYCb.jpg'],
	'350': ['Apple TV Plus', 'https://www.themoviedb.org//t/p/original/A3WLxoSkmuxwaQkpfwL6H8WwWwM.jpg'],
	'62': ['Atres Player', 'https://www.themoviedb.org//t/p/original/ibnxKce4MBay3jTqfIKaBTySp0L.jpg'],
	'188': ['YouTube Premium', 'https://www.themoviedb.org//t/p/original/hvVCDCBcmj8ouq5T18P5g2qfaNc.jpg'],
	'190': ['Curiosity Stream', 'https://www.themoviedb.org//t/p/original/aWGqR6ERNT6cAlgmtQUMfGFeaFv.jpg'],
	'521': ['Spamflix', 'https://www.themoviedb.org//t/p/original/qc4Aze8HWuVdjUyA1qcOsMZZc6I.jpg'],
	'495': ['CGood TV', 'https://www.themoviedb.org//t/p/original/46veKqyFzqexqq9ZuOxdBiIdkMo.jpg'],
	'393': ['FlixOlé', 'https://www.themoviedb.org//t/p/original/5VpgBWB3AQzS87sn06cA082qmRG.jpg'],
	'475': ['DOCSVILLE', 'https://www.themoviedb.org//t/p/original/rre9YaMnTG9xKG8GiCp2NVgg5Rw.jpg'],
	'35': ['Rakuten TV', 'https://www.themoviedb.org//t/p/original/wuViyDkbFp4r7VqI0efPW5hFfQj.jpg'],
	'534': ['Argo', 'https://www.themoviedb.org//t/p/original/bpn7c7kNnbeNjgx41ruqPsI3iB.jpg'],
	'546': ['WOW Presents Plus', 'https://www.themoviedb.org//t/p/original/5avC3AeBNARK5J0bV4qZeHtscHk.jpg'],
	'456': ['Mitele ', 'https://www.themoviedb.org//t/p/original/7YSulLY6w0fRL86m2NcmP7Hh7CG.jpg'],
	'551': ['Magellan TV', 'https://www.themoviedb.org//t/p/original/1LMwnJAWz045Txz17IUILT5uDDw.jpg'],
	'554': ['BroadwayHD', 'https://www.themoviedb.org//t/p/original/sZh3q3C0aVh6TAfuzB0cnKikX7u.jpg'],
	'559': ['Filmzie', 'https://www.themoviedb.org//t/p/original/nM4igKRYuYRwm9HqWyrKkJgCC7j.jpg'],
	'68': ['Microsoft Store', 'https://www.themoviedb.org//t/p/original/paq2o2dIfQnxcERsVoq7Ys8KYz8.jpg'],
	'194': ['Starz Play Amazon Channel', 'https://www.themoviedb.org//t/p/original/zznIwoeBvIUHJUfCaXzzmvJz2WH.jpg'],
	'538': ['Plex', 'https://www.themoviedb.org//t/p/original/5JMX2rehfh2lMpATccCO8aVN7WL.jpg']}

    for network in networks_list:
        itemlist.append(item.clone( title=networks_list.get(network)[0], thumbnail = networks_list.get(network)[1], action='descubre_networks', extra = network, text_color = text_color ))

    return sorted(itemlist, key=lambda it: it.title)


def descubre_anios(item):
    logger.info()

    if not item.page: item.page = 1

    tipo = 'movie' if item.search_type == 'movie' else 'tv'
    elementos = tmdb.get_discover_anios(tipo, item.extra, item.page)

    return lista(item, elementos)


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    to_year = 1950 if item.search_type == 'tvshow' else 1919

    for x in range(current_year, to_year, -1):
        itemlist.append(item.clone( title=str(x), action='descubre_anios', extra = str(x), text_color = text_color ))

    return itemlist


def personas(item):
    logger.info()
    itemlist = []

    if not item.person_id:
        last_search = config.get_setting('search_last_person', default='')
        tecleado = platformtools.dialog_input(last_search, 'Nombre de la persona a buscar')

        if tecleado is None or tecleado == '': return

        config.set_setting('search_last_person', tecleado)

        elementos = tmdb.get_person(tecleado)

        if len(elementos) == 0:
            platformtools.dialog_notification(tecleado, '[COLOR coral]Sin resultados[/COLOR]')
            return

        elif len(elementos) == 1:
            item.person_id = elementos[0]['id']
            item.category = elementos[0]['name']

        else:
            opciones = []; opciones_ids = [];
            for elemento in elementos:
                info = ''

                for detalle in elemento['known_for']:
                    if info != '': info += ', '
                    if 'title' in detalle:
                        info += detalle['title']
                        if 'release_date' in detalle: info += ' (%s)' % detalle['release_date'][:4]
                    else:
                        info += detalle['name']
                        if 'first_air_date' in detalle:info += ' (TV %s)' % detalle['first_air_date'][:4]

                thumb = ''
                if elemento['profile_path']: thumb = thumbs + 't/p/w235_and_h235_face%s' % elemento['profile_path']

                opciones.append(platformtools.listitem_to_select(elemento['name'], info, thumb))
                opciones_ids.append(elemento['id'])

            ret = platformtools.dialog_select('Selecciona la persona que buscas', opciones, useDetails=True)
            if ret == -1: 
                return

            item.person_id = opciones_ids[ret]
            item.category = opciones[ret].getLabel()

    # ~ Listar pelis y series de la persona
    if not item.page: item.page = 1

    elementos = tmdb.get_person_credits(item.person_id, item.search_type)

    if item.search_type == 'crew':
        elementos = list(filter(lambda it: 'job' in it and it['job'] == 'Director', elementos))

    perpage = 20
    num_elementos = len(elementos)
    desde = (item.page - 1) * perpage

    for elemento in elementos[desde:]:
        titulo = elemento['title'] if 'title' in elemento else elemento['name']
        sufijo = ''

        if 'name' in elemento: sufijo += '[COLOR hotpink](TV)[/COLOR] '

        if 'character' in elemento: sufijo += '[LIGHT][COLOR gray][I]%s[/I][/COLOR][/LIGHT]' % elemento['character']

        if 'title' in elemento:
            itemlist.append(item.clone( channel='search', action = 'search', buscando = texto_busqueda(titulo), from_channel = item.channel, title = titulo, fmt_sufijo=sufijo, search_type = 'movie',
                                        contentType = 'movie', contentTitle = titulo, infoLabels = {'tmdb_id': elemento['id']} ))
        else:
            itemlist.append(item.clone( channel='search', action = 'search', buscando = texto_busqueda(titulo), from_channel = item.channel, title = titulo, fmt_sufijo=sufijo, search_type = 'tvshow',
                                        contentType = 'tvshow', contentSerieName = titulo, infoLabels = {'tmdb_id': elemento['id']} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if desde + perpage < num_elementos:
        itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, text_color='coral' ))

    return itemlist


def listado_personas(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    elementos = tmdb.get_list('person', item.extra, item.page)

    for elemento in elementos:
        info = ''

        for detalle in elemento['known_for']:
            if info != '': info += ', '
            if 'title' in detalle: info += '%s (%s)' % (detalle['title'], detalle['release_date'][:4])
            else: info += '%s (TV %s)' % (detalle['name'], detalle['first_air_date'][:4])

        thumb = ''
        if elemento['profile_path']: thumb = thumbs + 't/p/w235_and_h235_face%s' % elemento['profile_path']

        itemlist.append(item.clone( action = 'personas', person_id = elemento['id'], search_type = 'cast', page = 1, 
                                    title = elemento['name'], thumbnail = thumb, plot = info, category = elemento['name'], text_color='moccasin' ))

    if len(itemlist) > 0:
        itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []

    if texto:
        tmdb_info = tmdb.Tmdb(texto_buscado=texto, tipo=item.search_type.replace('show', ''))

        results = tmdb_info.results

        for result in results:
            result = tmdb_info.get_infoLabels(result, origen=result)

            if item.search_type == 'movie':
                search_type = 'movie'

                title = result['title']
                contentTitle = title
                contentSerieName = ''
            else:
                search_type = 'tvshow'

                title = result['name']

                contentSerieName = title
                contentTitle = ''

            thumb = ''
            if result['poster_path']: thumb = thumbs + 't/p/original%s' % result['poster_path']

            tmdb_id = result['id']

            new_item = Item( channel='search', action='search', title=title, buscando=title, thumbnail=thumb,
                                               search_type=search_type, contentTitle=contentTitle, contentSerieName=contentSerieName, from_channel=item.channel, infoLabels = {'tmdb_id': tmdb_id} )

            itemlist.append(new_item)

    if itemlist:
        tmdb.set_infoLabels(itemlist)

    return itemlist

