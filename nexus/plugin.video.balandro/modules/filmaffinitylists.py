# -*- coding: utf-8 -*-

import re

from datetime import datetime

from platformcode import config, logger, platformtools

from core.item import Item
from core import httptools, scrapertools, tmdb

from modules import search


host = 'https://www.filmaffinity.com/es/'


ruta_sel = 'topgen.php?country=%s&genre=%s&fromyear=%s&toyear=%s'

current_year = int(datetime.today().year)

perpage = 30


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='show_help', title='[B]Información Filmaffinity[/B]', folder=False, thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( action='', title= '[B]Búsquedas a través de [COLOR pink]Personas[/COLOR]:[/B]', text_color='yellowgreen' ))

    itemlist.append(item.clone( action='listas', search_type='person', stype='cast', title=' - Buscar [COLOR aquamarine]intérprete[/COLOR] ...', thumbnail=config.get_thumb('search'),
                                plot = 'Escribir el nombre de un actor o una actriz para listar todas las películas y series en las que ha intervenido.' ))

    itemlist.append(item.clone( action='listas', search_type='person', stype='director', title=' - Buscar [COLOR springgreen]dirección[/COLOR] ...', thumbnail=config.get_thumb('search'),
                                plot = 'Escribir el nombre de una persona para listar todas las películas y series que ha dirigido.' ))

    itemlist.append(item.clone( action='', title= '[B]Búsquedas a través de [COLOR pink]Listas[/COLOR]:[/B]', text_color='yellowgreen' ))

    itemlist.append(item.clone( action='listas', search_type='all', stype='title', title=' - Buscar [COLOR yellow]película y/ó serie[/COLOR] ...', thumbnail=config.get_thumb('search') ))
    itemlist.append(item.clone( action='listas', search_type='documentary', stype='documentary', title=' - Buscar [COLOR cyan]documental[/COLOR] ...', thumbnail=config.get_thumb('search') ))

    por_plataforma = False
    por_tema = False

    presentar = True
    if item.search_type == 'tvshow': presentar = False
    elif item.search_type == 'documentary': presentar = False
    elif item.extra == 'mixed':
       if item.search_type == 'movie': presentar = False

    if presentar:
        por_plataforma = True
        por_tema = True

        itemlist.append(item.clone( title = '[B]Películas:[/B]', thumbnail=config.get_thumb('movie'), action = '', text_color='deepskyblue' ))

        if config.get_setting('search_extra_trailers', default=False):
            itemlist.append(item.clone( channel='trailers', action='search', title=' - Buscar en [COLOR darkgoldenrod]Tráilers[/COLOR] ...', thumbnail=config.get_thumb('search') ))

        itemlist.append(item.clone( title = ' - En cartelera', action = 'list_all', url = host + 'cat_new_th_es.html', thumbnail=config.get_thumb('novedades'), search_type = 'movie' ))

        itemlist.append(item.clone( title = ' - Por plataforma', action = 'plataformas', thumbnail=config.get_thumb('booklet'), search_type = 'movie' ))
        itemlist.append(item.clone( title = ' - Por género', action = 'generos', thumbnail=config.get_thumb('listgenres'), search_type = 'movie' ))
        itemlist.append(item.clone( title = ' - Por país', action = 'paises', thumbnail=config.get_thumb('idiomas'), search_type = 'movie' ))
        itemlist.append(item.clone( title = ' - Por año', action = 'anios', thumbnail=config.get_thumb('listyears'), search_type = 'movie' ))
        itemlist.append(item.clone( title = ' - Por tema', action = 'temas', url = host + 'topics.php', thumbnail=config.get_thumb('listthemes'), search_type = 'movie' ))

        itemlist.append(item.clone( title = ' - Premios Oscar', action = 'oscars', url = host + 'oscar_data.php', thumbnail=config.get_thumb('oscars'), search_type = 'movie' ))
        itemlist.append(item.clone( title = ' - Sagas y colecciones', action = 'sagas', url = host + 'movie-groups-all.php', page = 1, thumbnail=config.get_thumb('bestsagas'), search_type = 'movie' ))

        itemlist.append(item.clone( title = ' - Las mejores', action = 'list_sel', url = host + ruta_sel + '&notvse=1&nodoc=1', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

    presentar = True
    if item.search_type == 'movie': presentar = False
    elif item.search_type == 'documentary': presentar = False
    elif item.extra == 'mixed':
       if item.search_type == 'tvshow': presentar = False

    if presentar:
        if not por_plataforma:
            por_plataforma = True
            itemlist.append(item.clone( title = ' - Por plataforma', action = 'plataformas', thumbnail=config.get_thumb('booklet') ))

        if not por_tema:
            por_tema = True
            itemlist.append(item.clone( title = ' - Por tema', action = 'temas', url = host + 'topics.php' ))

        itemlist.append(item.clone( title = '[B]Series:[/B]', thumbnail=config.get_thumb('tvshow'), action = '', text_color='hotpink' ))

        itemlist.append(item.clone( title = ' - Premios Emmy', action = 'emmy_ediciones', url = host + 'award_data.php?award_id=emmy&year=', thumbnail=config.get_thumb('emmys'), search_type = 'tvshow' ))

        itemlist.append(item.clone( title = ' - Las mejores', action = 'list_sel', url = host + ruta_sel + '&nodoc=1', cod_genre = 'TV_SE', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

    presentar = True
    if item.search_type == 'movie': presentar = False
    elif item.search_type == 'tvshow': presentar = False
    elif item.extra == 'mixed': presentar = False

    if presentar:
        if not por_tema:
            itemlist.append(item.clone( title = ' - Por tema', action = 'temas', url = host + 'topics.php' ))

        if config.get_setting('mnu_documentales', default=True):
            itemlist.append(item.clone( title = '[B]Documentales:[/B]', thumbnail=config.get_thumb('documentary'), action = '', text_color='cyan' ))

            itemlist.append(item.clone( title = ' - Los mejores', action = 'list_sel', url = host + ruta_sel + '&notvse=1', cod_genre = 'DO', thumbnail=config.get_thumb('bestdocumentaries'), search_type = 'all' ))

    if not item.search_type:
        if config.get_setting('channels_link_main', default=True):
            itemlist.append(item.clone( title = '[B]Películas y Series:[/B]', thumbnail=config.get_thumb('bookshelf'), action = '', text_color='yellow' ))

            itemlist.append(item.clone( title = ' - Novedades a la venta', action = 'list_all', url = host + 'cat_new_sa_es.html', thumbnail=config.get_thumb('novedades'), search_type = 'all' ))
            itemlist.append(item.clone( title = ' - Novedades en alquiler', action = 'list_all', url = host + 'cat_new_re_es.html', thumbnail=config.get_thumb('novedades'), search_type = 'all' ))

    return itemlist
 

def show_help(item):
    txt = 'En este apartado se pueden hacer consultas a la web [COLOR gold][B]Filmaffinity[/B][/COLOR], que ofrece información de películas, series y personas.'

    txt += '[CR]'
    txt += '[CR]Se puede buscar la [COLOR moccasin][B]Filmografía[/B][/COLOR] de una persona y ver las películas/series dónde ha participado.'

    txt += '[CR]'
    txt += '[CR]También se pueden ver distintas [COLOR yellow][B]Listas[/B][/COLOR] de películas y/ó series según varios conceptos (más populares, más valoradas, por géneros, etc.)'

    txt += '[CR]'
    txt += '[CR]Al seleccionar una película/serie [COLOR chartreuse][B]se iniciará su búsqueda en los canales[/B][/COLOR] y se mostrarán los resultados encontrados.'
    txt += ' Hay que tener en cuenta que habrá películas/series que no tendrán enlaces en ninguno de los canales.'

    platformtools.dialog_textviewer('Información búsquedas y listas en Filmaffinity', txt)
    return True


def plataformas(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    if item.search_type == 'movie': text_color = 'deepskyblue'
    elif item.search_type == 'tvshow': text_color = 'hotpink'

    itemlist.append(item.clone( title = 'Amazon prime', action = 'list_all', url = host + 'cat_new_amazon_es.html', text_color = text_color ))
    itemlist.append(item.clone( title = 'Apple TV+', action = 'list_all', url = host + 'cat_apple_tv_plus.html', text_color = text_color ))
    itemlist.append(item.clone( title = 'Disney+', action = 'list_all', url = host + 'cat_disneyplus.html', text_color = text_color ))
    itemlist.append(item.clone( title = 'Filmin', action = 'list_all', url = host + 'cat_new_filmin.html', text_color = text_color ))
    itemlist.append(item.clone( title = 'HBO', action = 'list_all', url = host + 'cat_new_hbo_es.html', text_color = text_color ))
    itemlist.append(item.clone( title = 'Movistar+', action = 'list_all', url = host + 'cat_new_movistar_f.html', text_color = text_color ))
    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'cat_new_netflix.html', text_color = text_color ))
    itemlist.append(item.clone( title = 'Rakuten TV', action = 'list_all', url = host + 'cat_new_rakuten.html', text_color = text_color ))

    return itemlist


def oscars(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    if item.search_type == 'movie': text_color = 'deepskyblue'
    elif item.search_type == 'tvshow': text_color = 'hotpink'

    itemlist.append(item.clone( title = 'Películas con Más Oscars', action = 'list_oscars', url = item.url, grupo = 'Películas con más Oscars', text_color = text_color ))
    itemlist.append(item.clone( title = 'Películas con Más Nominaciones (sin Oscar a la mejor película)', action = 'list_oscars', url = item.url, grupo = 'Películas con más nominaciones', text_color = text_color ))
    itemlist.append(item.clone( title = 'Películas con Más Nominaciones y Ningún Oscar', action = 'list_oscars', url = item.url, grupo = 'Películas con más nominaciones y ningún Oscar', text_color = text_color ))
    itemlist.append(item.clone( title = 'Películas Ganadoras de los 5 Oscars principales', action = 'list_oscars', url = item.url, grupo = 'Películas ganadoras de los 5 Oscars principales', text_color = text_color ))
    itemlist.append(item.clone( title = 'Últimas Películas Ganadoras del Oscar principal', action = 'list_oscars', url = item.url, grupo = 'Últimas películas ganadoras del Oscar principal', text_color = text_color ))
    itemlist.append(item.clone( title = 'Ediciones Premios Oscar', action = 'oscars_ediciones', url = host + 'award_data.php?award_id=academy_awards', text_color = text_color ))

    return itemlist


def listas(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.page == 0:
        if not '&p=' in item.url:
            last_search = config.get_setting('search_last_' + item.search_type, default='')

            if item.search_type == 'person': texto = 'Nombre de la persona a buscar'
            else: texto = 'Texto a buscar'

            tecleado = platformtools.dialog_input(last_search, texto)

            if tecleado is None or tecleado == '': return

            config.set_setting('search_last_' + item.search_type, tecleado)

            if ':' in tecleado: tecleado.split(':')[1].strip()

            item.tecleado = tecleado

    if not '&p=' in item.url:
        url = host + 'search.php?stype=' + item.stype + '&stext=' + item.tecleado

        data = httptools.downloadpage(url).data
    else:
        data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'data-movie-id="(.*?)<div class="lists-box">')

    if not matches:
        if item.stype == 'cast':
            url = scrapertools.find_single_match(data, '<ul class="main-role">.*?<a href="(.*?)"')

            data = httptools.downloadpage(url).data

            matches = scrapertools.find_multiple_matches(data, 'data-movie-id="(.*?)<div class="lists-box">')

        elif item.stype == 'director':
            url = scrapertools.find_single_match(data, '<ul class="main-role">.*?<a href="(.*?)"')

            url = url.replace('&role-cat=cas', '&role-cat=dir')

            data = httptools.downloadpage(url).data

            matches = scrapertools.find_multiple_matches(data, 'data-movie-id="(.*?)<div class="lists-box">')

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for match in matches[desde:hasta]:
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        thumb = thumb.replace('-mtiny', '-large') + '|User-Agent=Mozilla/5.0'

        name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '').replace('(C)', '')

        title = title.replace('(Serie de TV)', '(TV)').replace('(Miniserie de TV)', '(TV)')

        if '(Serie de TV)' in title or '(Miniserie de TV)' in title:
            _search_type = 'tvshow'

            if item.search_type == 'documentary': _search_type = 'all'

            if '(TV)' in title: title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = _search_type, name = name, contentSerieName = name, infoLabels = {'year': '-'} ))
        else:
            _search_type = 'movie'

            if '(C)' in title: title = title.replace('(C)', '[COLOR moccasin](C)[/COLOR]')

            elif '(TV)' in title:
                title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')
                _search_type = 'tvshow'

            if item.search_type == 'documentary': _search_type = 'all'

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = _search_type, name = name, contentTitle = name, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, tecleado = item.tecleado, stype = item.stype, action = 'listas', text_color='coral' ))
        else:
            if '<div class="pager-bar-content">' in data:
               next_page = scrapertools.find_single_match(data, '<span class="current">.*?</span> <a href="(.*?)"')

               if next_page:
                   itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'listas', page = 0, text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div class="movie-poster" data-movie-id=.*?src="(.*?)".*?title="(.*?)"')

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for thumb, title in matches[desde:hasta]:
        title = title.strip()

        thumb = thumb.replace('-mtiny', '-large') + '|User-Agent=Mozilla/5.0'

        name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '').replace('(C)', '')

        title = title.replace('(Serie de TV)', '(TV)').replace('(Miniserie de TV)', '(TV)')

        if '(Serie de TV)' in title or '(Miniserie de TV)' in title:
            if '(TV)' in title: title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'tvshow', name = name, contentSerieName = name ))
        else:
            _search_type = 'movie'

            if '(C)' in title: title = title.replace('(C)', '[COLOR moccasin](C)[/COLOR]')

            elif '(TV)' in title:
                title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')
                _search_type = 'tvshow'

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = _search_type, name = name, contentTitle = name, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color='coral' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    if item.search_type == 'movie': text_color = 'deepskyblue'
    elif item.search_type == 'tvshow': text_color = 'hotpink'

    labels_generos = [
          ('Accion', 'AC'),
          ('Animación', 'AN'),
          ('Aventuras', 'AV'),
          ('Bélico', 'BE'),
          ('Ciencia ficción', 'C-F'),
          ('Cine negro', 'F-N'),
          ('Comedia', 'CO'),
          ('Documental', 'DO'),
          ('Drama', 'DR'),
          ('Fantástico', 'FAN'),
          ('Infantil', 'INF'),
          ('Intriga', 'INT'),
          ('Musical', 'MU'),
          ('Romance', 'RO'),
          ('Serie de TV', 'TV_SE'),
          ('Terror', 'TE'),
          ('Thriller', 'TH'),
          ('Western', 'WE')
          ]

    ruta_gen = 'topgen.php?country=%s&genres=%s&fromyear=%s&toyear=%s'

    for genero in labels_generos:
        url = host + ruta_gen

        if not genero[0] == 'Serie de TV': url = url + '&notvse=1'
        elif not genero[0] == 'Documental': url = url + '&nodoc=1'

        itemlist.append(item.clone ( title = genero[0], action = 'list_sel', url = url, cod_genre = genero[1], text_color = text_color ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    if item.search_type == 'movie': text_color = 'deepskyblue'
    elif item.search_type == 'tvshow': text_color = 'hotpink'

    labels_paises = [
          ('Alemania', 'DE'),
          ('Argentina', 'AR'),
          ('Australia', 'AU'),
          ('Austria', 'AT'),
          ('Bélgica', 'BE'),
          ('Bolivia', 'BO'),
          ('Brasil', 'BR'),
          ('Canadá', 'CA'),
          ('Chile', 'CL'),
          ('China', 'CN'),
          ('Colombia', 'CO'),
          ('Costa Rica', 'CR'),
          ('Ecuador', 'EC'),
          ('España', 'ES'),
          ('Estados Unidos', 'US'),
          ('Francia', 'FR'),
          ('Guatemala', 'GT'),
          ('Holanda', 'NL'),
          ('Honduras', 'HN'),
          ('India', 'IN'),
          ('Irlanda', 'IE'),
          ('Israel', 'IL'),
          ('Italia', 'IT'),
          ('Japón', 'JP'),
          ('México', 'MX'),
          ('Nicaragua', 'NI'),
          ('Noruega', 'NO'),
          ('Panamá', 'PA'),
          ('Paraguay', 'PY'),
          ('Perú', 'PE'),
          ('Polonia', 'PL'),
          ('Portugal', 'PT'),
          ('Reino Unido', 'GB'),
          ('Rep. Dominicana', 'DO'),
          ('Rusia', 'RU'),
          ('Sudafrica', 'ZA'),
          ('Suecia', 'SE'),
          ('Suiza', 'CH'),
          ('Tailandia', 'TH'),
          ('Taiwán', 'TW'),
          ('Turquía', 'TR'),
          ('Unión Soviética', 'ZY'),
          ('Uruguay', 'UY'),
          ('Venezuela', 'VE'),
          ('Yugoeslavia', 'YU')
          ]

    for pais in labels_paises:
        itemlist.append(item.clone ( title = pais[0], action = 'list_sel', url = host + ruta_sel + '&notvse=1&nodoc=1', cod_country = pais[1], text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    if item.search_type == 'movie': text_color = 'deepskyblue'
    elif item.search_type == 'tvshow': text_color = 'hotpink'

    for x in range(current_year, 1909, -1):
        anyo = str(x)

        itemlist.append(item.clone( title = anyo, action='list_sel', url = host + ruta_sel + '&notvse=1&nodoc=1', fromyear = anyo, toyear = anyo, text_color = text_color ))

    return itemlist


def temas(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    if item.search_type == 'movie': text_color = 'deepskyblue'
    elif item.search_type == 'tvshow': text_color = 'hotpink'

    if not item.page: item.page = 0

    perpage = 150

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<li><a class="topic" href="(.*?)">(.*?)<em>')

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for url, title in matches[desde:hasta]:
        title = title.strip()

        url = url + '&attr=all&order=BY_YEAR'

        search_type = 'movie'

        if title.startswith('Documental ') == True:
            url = url.replace('&nodoc', '')
            search_type = 'documentary'
        elif title == 'Serie [Alfred Hitchcock presenta]': search_type = 'tvshow'
        elif title == 'Serie [Colombo]': search_type = 'tvshow'
        elif title == 'Serie [Pesadillas y alucinaciones]': search_type = 'tvshow'
        elif title == 'Serie [What a Cartoon!]': search_type = 'tvshow'

        itemlist.append(item.clone( action = 'list_temas', title = title, url = url, page = 1, search_type = search_type, text_color = text_color ))

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'temas', text_color='coral' ))

    return itemlist


def list_temas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches1 = scrapertools.find_multiple_matches(data, '<div class="subline-pg">(.*?)</a></li>')

    matches2 = scrapertools.find_multiple_matches(data, '<div class="blank-content">(.*?)</a></li>')

    matches = matches1 + matches2

    for match in matches:
        year = scrapertools.find_single_match(match, '<div class="header-pg-text">(.*?)</div>').strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()
        if not title: title = scrapertools.find_single_match(match, '<div class="title-no-image">(.*?)</div>').strip()

        if year:
            if year > str(current_year): continue
        else: year = '-'

        if thumb.startswith('/imgs/') == True: thumb = 'https://www.filmaffinity.com' + thumb

        thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '').replace('(C)', '')

        title = title.replace('(Serie de TV)', '(TV)').replace('(Miniserie de TV)', '(TV)')

        if item.search_type == 'tvshow':
            if '(TV)' in title: title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = item.search_type, name = name, contentSerieName = name, infoLabels={'year': year} ))

        elif item.search_type == 'documentary':
            if '(TV)' in title: title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')

            elif '(C)' in title: title = title.replace('(C)', '[COLOR moccasin](C)[/COLOR]')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = item.search_type, name = name, contentSerieName = name, infoLabels={'year': year} ))

        elif '(Serie de TV)' in title or '(Miniserie de TV)' in title:
            if '(TV)' in title: title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'tvshow', name = name, contentSerieName = name, infoLabels={'year': year} ))

        else:
            _search_type = 'movie'

            if '(C)' in title: title = title.replace('(C)', '[COLOR moccasin](C)[/COLOR]')

            elif '(TV)' in title:
                title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')
                _search_type = 'tvshow'

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = _search_type, name = name, contentTitle = name, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pager">' in data:
           next_page = scrapertools.find_single_match(data, '<div class="pager">.*?<span class="current">.*?</span> <a href="(.*?)"')
           if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pager">.*?<a href="(.*?)"')

           if next_page:
               itemlist.append(item.clone( title = 'Siguientes ...', url = host + next_page, action = 'list_temas', page = 0, text_color='coral' ))

    return itemlist


def list_oscars(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    grupo = scrapertools.find_single_match(data, item.grupo + '(.*?)</table>')

    if item.grupo == 'Películas con más Oscars' or item.grupo == 'Últimas películas ganadoras del Oscar principal': 
        matches = scrapertools.find_multiple_matches(grupo, '">(.*?)</a>.*?title="(.*?)".*?<td>.*?<td>(.*?)</td>')
    else: matches = scrapertools.find_multiple_matches(grupo, '">(.*?)</a>.*?title="(.*?)".*?<td>(.*?)</td>')

    for year, title, premios in matches:
        title = title.strip()
        premios = premios.replace('Oscar', '').strip()

        if len(premios) == 2: titulo = '[COLOR tan][B]' + premios + '[/B][/COLOR]  ' + title
        else: titulo = '[COLOR tan][B]  ' + premios + '[/B][/COLOR]  ' + title

        itemlist.append(item.clone( action = 'find_search', title = titulo, search_type = 'movie', name = title, contentType='movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def oscars_ediciones(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    if item.search_type == 'movie': text_color = 'deepskyblue'
    elif item.search_type == 'tvshow': text_color = 'hotpink'

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<td><a href="(.*?)" title="(.*?)">(.*?)</a>')

    for url, title, anyo in matches:
        title = title.strip()
        if not title: title = 'Premios Oscars ' + anyo

        itemlist.append(item.clone( action = 'list_premios_anyo', title = title, url = url, anyo = anyo, text_color = text_color ))

    return sorted(itemlist, key = lambda it: it.anyo, reverse = True)


def list_premios_anyo(item):
    logger.info()
    itemlist = []

    premiadas = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)</div></li></ul></div></div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?title="(.*?)".*?src="(.*?)"')

    for url, title, thumb in matches:
        title = title.strip()

        if 'Edición de los Oscar' in title: continue

        thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '').replace('(C)', '')

        title = title.replace('(Serie de TV)', '(TV)').replace('(Miniserie de TV)', '(TV)')

        if not title in str(premiadas):
            premiadas.append(title)

            if '(Serie de TV)' in title or '(Miniserie de TV)' in title:
                if '(TV)' in title: title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')

                itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'tvshow', name = name, contentSerieName = name, infoLabels = {'year': item.anyo} ))
            else:
                _search_type = 'movie'

                if '(C)' in title: title = title.replace('(C)', '[COLOR moccasin](C)[/COLOR]')

                elif '(TV)' in title:
                    title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')
                    _search_type = 'tvshow'

                itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = _search_type, name = name, contentTitle = name, infoLabels = {'year': item.anyo} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def emmy_ediciones(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    if item.search_type == 'movie': text_color = 'deepskyblue'
    elif item.search_type == 'tvshow': text_color = 'hotpink'

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<td><a href="(.*?)".*?title="">(.*?)</a>')
    matches = scrapertools.find_multiple_matches(data, '<td><a href="(.*?)" title="(.*?)">(.*?)</a>')

    for url, title, anyo in matches:
        title = title.strip()
        if not title: title = 'Premios Emmy ' + anyo

        itemlist.append(item.clone( action = 'list_premios_anyo', title = title, url = url, anyo = anyo, text_color = text_color ))

    return sorted(itemlist, key = lambda it: it.anyo, reverse = True)


def sagas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<li class="fa-shadow">.*?href="(.*?)".*?<div class="group-name">(.*?)</div>.*?src="(.*?)".*?<div class="count-movies">(.*?)</div>')

    for url, title, thumb, count in matches:
        thumb = thumb.replace('-med', '-large') + '|User-Agent=Mozilla/5.0'

        title = '[COLOR moccasin]' + title + '[/COLOR]'

        count = count.replace('películas', '').strip()
        if count: count = '  (' + count + ')'

        itemlist.append(item.clone( action = 'list_sagas', title = title + count, url = url, thumbnail = thumb, page = 0 ))

    if '<div class="pager">' in data:
        not_last_page = scrapertools.find_single_match(data, '<span class="current">.*?</span> <a href="(.*?)"')

        if not_last_page:
            url = item.url

            prev_page = '?p=' + str(item.page)
            url = url.replace(prev_page, '')

            next_page = item.page + 1
            itemlist.append(item.clone( title = 'Siguientes ...', url = url + '?p=' + str(next_page), action = 'sagas', page = next_page, text_color='coral' ))

    return itemlist


def list_sagas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<div class="movie-card.*?movie-card-.*?data-movie-id=".*?src="(.*?)".*?title="(.*?)">.*?</a>[^\d+]+(\d+)[^<]+'

    matches = scrapertools.find_multiple_matches(data, patron)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for thumb, title, year in matches[desde:hasta]:
        if year:
            if year > str(current_year):
                num_matches = num_matches - 1
                continue
        else: year = '-'

        title = title.strip()

        thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '').replace('(C)', '')

        title = title.replace('(Serie de TV)', '(TV)').replace('(Miniserie de TV)', '(TV)')

        if '(Serie de TV)' in title or '(Miniserie de TV)' in title:
            if '(TV)' in title: title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'tvshow', name = name, contentSerieName = name, infoLabels={'year': year} ))
        else:
            _search_type = 'movie'

            if '(C)' in title: title = title.replace('(C)', '[COLOR moccasin](C)[/COLOR]')

            elif '(TV)' in title:
                title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')
                _search_type = 'tvshow'

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = _search_type, name = name, contentTitle = name, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_sagas', text_color='coral' ))

    return itemlist


def list_sel(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    url = item.url

    cod_country = ''
    cod_genre = ''

    if item.cod_country: cod_country = item.cod_country

    if item.cod_genre:
        if not item.cod_genre == 'TV_SE': 
           if not item.cod_genre == 'DO':
               cod_genre = '%2B' + item.cod_genre

    if item.fromyear: fromyear = item.fromyear
    else: fromyear = '1874'

    if item.toyear: toyear = item.toyear
    else: toyear = str(current_year)

    url = url % (cod_country, cod_genre, fromyear, toyear)

    if item.cod_genre == 'TV_SE': url = url + '&chv=1&orderby=avg&movietype=serie%7C&ratingcount=3&runtimemin=0&runtimemax=4'
    elif item.cod_genre == 'DO': url = url + '&chv=1&orderby=avg&movietype=documentary%7C&ratingcount=3&runtimemin=0&runtimemax=8'
    else: url = url + '&chv=1&orderby=avg&movietype=movie%7C&ratingcount=3&runtimemin=0&runtimemax=4'

    post = {'from': item.page}
    data = httptools.downloadpage(url, post = post).data

    matches = scrapertools.find_multiple_matches(data, '<li class="position">(.*?)</ul>')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<li>(.*?)</li>')

    for match in matches:
        title = scrapertools.find_single_match(match, ' title="(.*?)"').strip()

        year = scrapertools.find_single_match(match, ' title=.*?</a>(.*?)<img').strip()
        year = year.replace('(', '').replace(')', '').strip()

        if not year:
            if item.toyear: year = item.toyear
            else: year = '-'

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')
        thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '').replace('(C)', '')

        title = title.replace('(Serie de TV)', '(TV)').replace('(Miniserie de TV)', '(TV)')

        if '(Serie de TV)' in title or '(Miniserie de TV)' in title or cod_genre == 'TV_SE':
            if '(TV)' in title: title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'tvshow', name = name, contentSerieName = name, infoLabels={'year': year} ))

        elif '&genre=DO&' in url:
            if '(C)' in title: title = title.replace('(C)', '[COLOR moccasin](C)[/COLOR]')

            elif '(TV)' in title: title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'documentary', name = name, contentTitle = name, infoLabels={'year': year} ))

        else:
            _search_type = 'movie'

            if '(C)' in title: title = title.replace('(C)', '[COLOR moccasin](C)[/COLOR]')

            elif '(TV)' in title:
                title = title.replace('(TV)', '[COLOR hotpink](TV)[/COLOR]')
                _search_type = 'tvshow'

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = _search_type, name = title, contentTitle = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if matches:
        num_matches = len(matches)

        if num_matches >= 30:
            next_page = item.page + 30
            itemlist.append(item.clone( title = 'Siguientes ...', url = item.url, page = next_page, action = 'list_sel', text_color='coral' ))

    return itemlist


def _oscars(item):
    logger.info()
    itemlist = []

    url = host + 'awards.php?award_id=academy_awards&year=' + str(current_year)

    data = httptools.downloadpage(url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="full-content"><div class="header" id="([^"]+)">([^<]+)').findall(data)

    for oscars_id, title in matches:
        itemlist.append(item.clone( action = '_oscars_categories', title = title, oscars_id = oscars_id))

    return itemlist


def _oscars_categories(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '(<div class="full-content"><div class="header" id="%s">.*?</div></div></li></ul></div></div>)' % (item.oscars_id)

    bloque = scrapertools.find_single_match(data, patron)

    matches = scrapertools.find_multiple_matches(bloque, '<li class="(fa-shadow.*?)">(.*?)</li>')

    for info, match in matches:
        titulo = ''

        title = scrapertools.find_single_match(match, '<a class="movie-title-link" href="[^"]+" title="([^"]+)\W+"')
        titulo += title

        nominated = scrapertools.find_single_match(match, '<div class="nom-text">([^<]+)</div>')
        if nominated: titulo += ' - ' + nominated

        nominations = scrapertools.find_single_match(match, '<b>(.*?)</a>')
        if nominations:
            nominations = re.sub('<.*?>', '', nominations) if scrapertools.find_single_match(nominations, '(<.*?>)') else nominations
            titulo += ' - ' + nominations
        else: nominations = '1 nominación'

        if 'win' in info: titulo = ''.join(("[COLOR pink]", titulo, "[/COLOR]"))

        itemlist.append(item.clone( action = 'find_search', title = titulo, search_type = 'movie', name = title, contentTitle = title, infoLabels={'year': '-'} ))
        
    tmdb.set_infoLabels(itemlist)

    return itemlist


def _emmys(item):
    logger.info()

    item.url = host + 'award_data.php?award_id=emmy&year='

    if item.origen == 'mnu_esp':
        return emmy_ediciones(item)

    item.url = item.url + str(current_year)

    return list_premios_anyo(item)


def _oscars(item):
    logger.info()

    item.url = host + 'oscar_data.php'
    item.page = 1

    return oscars(item)

def _sagas(item):
    logger.info()

    item.url = host + 'movie-groups-all.php'
    item.page = 1

    return sagas(item)


def _bestmovies(item):
    logger.info()

    item.url = host + ruta_sel + '&notvse=1&nodoc=1'

    return list_sel(item)


def _besttvshows(item):
    logger.info()

    item.url = host + ruta_sel + '&nodoc=1'
    item.cod_genre = 'TV_SE'

    return list_sel(item)


def _bestdocumentaries(item):
    logger.info()

    item.url = host + ruta_sel + '&notvse=1'
    item.cod_genre = 'DO'

    return list_sel(item)


def _genres(item):
    logger.info()

    return generos(item)


def _years(item):
    logger.info()

    return anios(item)


def _themes(item):
    logger.info()

    item.url = host + 'topics.php'

    return temas(item)


def _navidad(item):
    logger.info()

    item.page = 1
    item.search_type = 'all'

    item.url = host + 'movietopic.php?topic=308785&nodoc&attr=all&order=BY_YEAR'

    return list_temas(item)


def find_search(item):
    logger.info()
    itemlist = []

    itemlist = search.search(item, item.name)

    return itemlist

