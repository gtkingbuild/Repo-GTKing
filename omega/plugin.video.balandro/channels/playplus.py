# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb, jsontools


host = 'https://playdede.ws/'


elepage = 42

perpage = 21


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/?anio=' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[COLOR greenyellow][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    if not config.get_setting('descartar_anime', default=False):
        itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[COLOR greenyellow][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host, _type = 'movies', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'En cartelera', action = 'list_all', url = host + 'peliculas/?tipo=cartelera', search_type = 'movie', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'peliculas/?tipo=populares', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas/?tipo=rate', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', slug = 'peliculas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', slug = 'peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', slug = 'peliculas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', slug = 'peliculas', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[COLOR greenyellow][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'seriesa/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Nuevos episodios', action = 'list_last', url = host, _type = 'episodes', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Últimas actualizadas', action = 'list_last', url = host, _type = 'series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Cartelera', action = 'list_all', url = host + 'seriesa/?tipo=cartelera', search_type = 'tvshow', text_color = 'moccasin' ))

    if not config.get_setting('descartar_anime', default=False):
        itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'seriesa/?tipo=populares', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'seriesa/?tipo=rate', search_type = 'tvshow' ))


    itemlist.append(item.clone( title = 'Por género', action = 'generos', slug = 'series', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', slug = 'series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', slug = 'series', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', slug = 'series', search_type = 'tvshow' ))

    return itemlist


def mainlist_animes(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[COLOR greenyellow][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animacion/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Cartelera', action = 'list_all', url = host + 'animacion?tipo=cartelera', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'animacion/?tipo=populares', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'animacion/?tipo=rate', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', group = 'anime', slug = 'animes', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', group = 'anime', slug = 'animes', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', group = 'anime', slug = 'animes', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', group = 'anime', slug = 'animes', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else:
       if item.search_type == 'movie': text_color = 'deepskyblue'
       else: text_color = 'hotpink'

    if item.group == 'anime': url_generos = host + 'animacion/'
    else:
        if item.search_type == 'movie': url_generos = host + 'peliculas/'
        else: url_generos = host + 'seriesa/'

    url = url_generos

    data = do_downloadpage(url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="Ageneros">(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>').findall(bloque)

    for genre, title in matches:
        if item.group == 'anime':
            if title == 'Documental': continue

        if config.get_setting('descartar_anime', default=False):
            if title == 'Anime': continue

        title = title.replace('&amp;', '').replace('i?n', 'ion')

        url = host[:-1] + genre

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else:
       if item.search_type == 'movie': text_color = 'deepskyblue'
       else: text_color = 'hotpink'

    if item.group == 'anime': url_anios = host + 'animacion/'
    else:
        if item.search_type == 'movie': url_anios = host + 'peliculas/'
        else: url_anios = host + 'seriesa/'

    if item.search_type == 'movie': tope_year = 1939
    else: tope_year = 1969

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        url = url_anios + '/?anio=' + str(x)

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else:
       if item.search_type == 'movie': text_color = 'deepskyblue'
       else: text_color = 'hotpink'

    if item.group == 'anime': url_idiomas = host + 'animacion/'
    else:
        if item.search_type == 'movie': url_idiomas = host + 'peliculas/'
        else: url_idiomas = host + 'seriesa/'

    url = url_idiomas

    data = do_downloadpage(url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="Alenguajes Ageneros">(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>').findall(bloque)

    for idioma, title in matches:
        title = title.lower()

        url = url_idiomas + '?lenguaje=' + title

        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url, text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def paises(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else:
       if item.search_type == 'movie': text_color = 'deepskyblue'
       else: text_color = 'hotpink'

    if item.group == 'anime': url_paises = host + 'animacion/'
    else:
        if item.search_type == 'movie': url_paises = host + 'peliculas/'
        else: url_paises = host + 'seriesa/'

    url = url_paises

    data = do_downloadpage(url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>SELECCIONAR PAÍS<(.*?)</div>')

    matches = re.compile('data-type="country".*?value="(.*?)">(.*?)</option>').findall(bloque)

    for pais, title in matches:
        if not pais: continue

        title = title.replace('á', 'Á').replace('é', 'É').replace('i', 'Í').replace('ó', 'Ó').replace('ú', 'Ú').replace('ñ', 'Ñ')

        url = url_paises + '?pais=' + pais

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article(.*?)</article>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if year:
            if ',' in year: year = scrapertools.find_single_match(year, ',(.*?)$').strip()
        else: year = '-'

        if '/?anio=' in item.url: year = scrapertools.find_single_match(item.url, "/?anio=(.*?)$")

        tipo = 'movie' if '/movie/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
                buscar_next = False

        if num_matches < elepage: buscar_next = False

        if buscar_next:
            if '<div class="pagPlaydede">' in data:
                if 'Pagina anterior' in data: patron = '<div class="pagPlaydede">.*?Pagina anterior.*?<a href="([^"]+)'
                else: patron = '<div class="pagPlaydede"><a href="([^"]+)'

                next_url = scrapertools.find_single_match(data, patron)

                if '/page/' in next_url:
                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_url, page = 0, text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if item._type == 'movies': bloque = scrapertools.find_single_match(data, 'class="animation-2 items b-tab tab-movies">(.*?)class="animation-2 items b-tab tab-series">')
    elif item._type == 'series': bloque = scrapertools.find_single_match(data, 'class="animation-2 items b-tab tab-series">(.*?)</div></div></div></div>')
    else: bloque = scrapertools.find_single_match(data, 'class="items b-tab active tab-episodes">(.*?)class="animation-2 items b-tab tab-movies">')

    i = 0

    matches = re.compile('<article(.*?)</article>').findall(bloque)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if item._type == 'episodes': title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if year:
            if ',' in year: year = scrapertools.find_single_match(year, ',(.*?)$').strip()
        else: year = '-'

        if '/movie/' in url:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

        elif '/serie/' in url:
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        else:
            titulo = scrapertools.find_single_match(match, '<a href="(.*?)"')

            titulo = titulo.replace('/episodios/', '').replace('_1', '').replace('_', ' ').replace('-', ' ').strip()
            titulo = titulo.replace('//', '').strip()

            titulo = titulo.capitalize()

            thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')
            thumb = thumb.replace('http:', 'https:')

            s_e = scrapertools.get_season_and_episode(title)

            try:
               season = int(s_e.split("x")[0])
               epis = s_e.split("x")[1]
            except:
               i += 1
               season = 0
               epis = i

            title = title.replace('/', '').strip()

            titulo = titulo.replace(str(season) + 'x' + str(epis), '').strip()
            titulo = titulo.replace(title, '').strip()

            if not 'Episodio' in title: titulo = titulo +  ' ' + title

            SerieName = titulo

            del_temp_epis = ''
            del_titulo = ''
            del_num_url = ''

            if '_' in url:
                del_num_url = scrapertools.find_single_match(url, '_(.*?)-').strip()
                if not del_num_url: del_num_url = scrapertools.find_single_match(del_num_url, '_(.*?)$').strip()

                if '_' in del_num_url:
                    del_num_url = scrapertools.find_single_match(del_num_url, '_(.*?)$').strip()

                    if '_' in del_num_url:
                        while '_' in del_num_url:
                           del_num_url = scrapertools.find_single_match(del_num_url, '_(.*?)$').strip()

                try:
                   del_num_url = int(del_num_url)
                   titulo = titulo.replace(str(del_num_url), '').strip()
                except:
                   del_num_url = ''

            if ':' in title: del_temp_epis = scrapertools.find_single_match(title, ':(.*?)$').strip()

            if ':' in titulo:
                del_titulo = scrapertools.find_single_match(titulo, ':(.*?)$').strip()
                titulo = titulo.replace(del_titulo, '').strip()
                titulo = titulo.replace(':', '').strip()

            if del_temp_epis:
                SerieName = SerieName.replace(del_temp_epis, '').strip()
                SerieName = SerieName.replace(':', '').strip()

            if del_num_url:
                ini_SerieName = SerieName
                SerieName = SerieName.replace(str(del_num_url), '').strip()

                if ini_SerieName == SerieName:
                    del_num_url = str(del_num_url)[1:]

                    if del_num_url:
                        SerieName = SerieName.replace(str(del_num_url), '').strip()

                        if del_num_url in titulo: titulo = titulo.replace(str(del_num_url), '').strip()

            titulo = titulo.replace('  ', ' ')

            if not 'x' in titulo: titulo = titulo + ' ' + str(season) + 'x' + str(epis)

            if 'Https' in titulo:
                titulo = titulo.replace('Https', '').strip()
                titulo = title

            SerieName = SerieName.replace('  ', ' ')

            itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_last', text_color = 'coral' ))

    return itemlist


def list_listas(item):
    logger.info()
    itemlist = []

    if not item.url: url_listas = host + 'listas/'
    else: url_listas = item.url

    url = url_listas

    data = do_downloadpage(url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article>.*?<a href="(.*?)".*?<h2>(.*?)</h2>').findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color='moccasin' ))

    if itemlist:
        if '<div class="pagPlaydede">' in data:
            if 'Pagina anterior' in data: patron = '<div class="pagPlaydede">.*?Pagina anterior.*?<a href="([^"]+)'
            else: patron = '<div class="pagPlaydede"><a href="([^"]+)'

            next_url = scrapertools.find_single_match(data, patron)

            if next_url:
                if '/page/' in next_url:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_listas', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="clickSeason.*?data-season="(.*?)"', re.DOTALL).findall(data)
    if not matches: matches = re.compile("<div class='clickSeason.*?data-season='(.*?)'", re.DOTALL).findall(data)

    if len(matches) > 25: platformtools.dialog_notification('PlayPlus', '[COLOR blue][B]Cargando Temporadas[/B][/COLOR]')

    for tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = int(tempo)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = int(tempo), text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="se-c".*?data-season="%d"(.*?)<\/div><\/div>' % (item.contentSeason))
    if not bloque: bloque = scrapertools.find_single_match(data, "<div class='se-c'.*?data-season='%d'(.*?)<\/div><\/div>" % (item.contentSeason))

    patron = '<a href="([^"]+)"><div class="imagen">'
    patron += '.*?src="([^"]+)"><\/div>.*?<div class="epst">([^<]+)'
    patron += '<\/div>.*?<div class="numerando">([^<]+)'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PlayPlus', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PlayPlus', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PlayPlus', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PlayPlus', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PlayPlus', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PlayPlus', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, thumb, titulo, name in matches[item.page * item.perpage:]:
        s_e = scrapertools.get_season_and_episode(name)
        season = int(s_e.split("x")[0])
        episode = s_e.split("x")[1]

        title = str(season) + 'x' + str(episode) + ' ' + titulo

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    url = item.url

    data = do_downloadpage(url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    # ~ Reproductor
    matches = re.compile('<div class="playerItem(.*?)</div></div>', re.DOTALL).findall(data)

    ses = 0

    for match in matches:
        ses += 1

        sid = scrapertools.find_single_match(match, 'data-loadPlayer="(.*?)"')
        if not sid: sid = scrapertools.find_single_match(match, 'data-loadplayer="(.*?)"')

        server = scrapertools.find_single_match(match, '<h3>(.*?)</h3>').lower().strip()

        if not server or not sid: continue

        if server == 'powvideo': continue
        elif server == 'streamplay': continue

        elif 'premiun' in server: continue

        lang = ''

        if '>Latino<' in match: lang = 'Lat'
        elif '>Castellano<' in match: lang = 'Esp'
        elif '>Subtitulado<' in match: lang = 'Vose'

        if not lang: lang = scrapertools.find_single_match(match, 'data-lang="(.*?)"')

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()

        qlty = scrapertools.find_single_match(match, '">Calidad:.*?">(.*?)</span>')

        other = ''

        if server == 'links':
            data1 = do_downloadpage(sid)

            links1 = re.compile('<li onclick="go_to_player.*?' + "'(.*?)'", re.DOTALL).findall(str(data1))
            links2 = re.compile('<a href="(.*?)"', re.DOTALL).findall(str(data1))

            links = links1 + links2

            for link in links:
                if '/ul.' in link: continue
                elif '/1fichier.' in link: continue
                elif '/ddownload.' in link: continue
                elif '/clk.' in link: continue
                elif '/rapidgator' in link: continue
                elif '/katfile' in link: continue
                elif '/nitro' in link: continue

                elif '/viewsb.' in link: continue
                elif '/formatearwindows.' in link: continue

                link = link.replace('/player.cuevana.ac/f/', '/waaw.to/watch_video.php?v=').replace('/player.cuevana3.one/f/', '/waaw.to/watch_video.php?v=')

                servidor = servertools.get_server_from_url(link)
                servidor = servertools.corregir_servidor(servidor)

                link = servertools.normalize_url(servidor, link)

                if not servidor == 'various': other = ''
                else: other = servertools.corregir_other(link)

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                    if not config.get_setting('developer_mode', default=False): continue

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link,
                                      language = lang, quality = qlty, other = other ))

            continue

        if server == 'player':
            server = 'waaw'
            sid = sid.replace('/player.cuevana.ac/f/', '/waaw.to/watch_video.php?v=').replace('/player.cuevana3.one/f/', '/waaw.to/watch_video.php?v=')

        elif server == 'filelions': other = 'Filelions'
        elif server == 'filemoon': other = 'Filemoon'
        elif server == 'streamwish': other = 'Streamwish'
        elif server == 'streamhub': other = 'Streamhub'
        elif server == 'uploaddo': other = 'Uploaddo'
        elif server == 'vembed': other = 'Vidguard'
        elif server == 'hexupload': other = 'Hexupload'
        elif server == 'userload': other = 'Userload'
        elif server == 'streamruby': other = 'Streamruby'

        elif 'premiun' in server: continue

        server = servertools.corregir_servidor(server)

        if servertools.is_server_available(server):
            if not servertools.is_server_enabled(server): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = sid,
                              language = lang, quality = qlty, other = other ))

    # ~ Enlaces
    bloque = scrapertools.find_single_match(data, '<div class="linkSorter">(.*?)<div class="contEP contepID_3">')

    matches = re.compile('data-quality="(.*?)".*?data-lang="(.*?)".*?href="(.*?)".*?<span>.*?">(.*?)</b>', re.DOTALL).findall(bloque)

    for qlty, lang, url, server in matches:
        ses += 1

        if not url or not server: continue

        server = server.lower().strip()

        if server == 'powvideo': continue
        elif server == 'streamplay': continue

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()

        other = ''

        if server == 'links':
            data1 = do_downloadpage(url)

            links1 = re.compile('<li onclick="go_to_player.*?' + "'(.*?)'", re.DOTALL).findall(str(data1))
            links2 = re.compile('<a href="(.*?)"', re.DOTALL).findall(str(data1))

            links = links1 + links2

            for link in links:
                if '/ul.' in link: continue
                elif '/1fichier.' in link: continue
                elif '/ddownload.' in link: continue
                elif '/clk.' in link: continue
                elif '/rapidgator' in link: continue
                elif '/katfile' in link: continue
                elif '/nitro' in link: continue

                elif '/viewsb.' in link: continue
                elif '/formatearwindows.' in link: continue

                link = link.replace('/player.cuevana.ac/f/', '/waaw.to/watch_video.php?v=').replace('/player.cuevana3.one/f/', '/waaw.to/watch_video.php?v=')

                servidor = servertools.get_server_from_url(link)
                servidor = servertools.corregir_servidor(servidor)

                link = servertools.normalize_url(servidor, link)

                if not servidor == 'various': other = ''
                else: other = servertools.corregir_other(link)

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                    if not config.get_setting('developer_mode', default=False): continue

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link,
                                      language = lang, quality = qlty, other = other ))

            continue

        if server == 'player':
            server = 'waaw'
            url = url.replace('/player.cuevana.ac/f/', '/waaw.to/watch_video.php?v=').replace('/player.cuevana3.one/f/', '/waaw.to/watch_video.php?v=')

        if server == 'filelions': other = 'Filelions'
        elif server == 'filemoon': other = 'Filemoon'
        elif server == 'streamwish': other = 'Streamwish'
        elif server == 'streamhub': other = 'Streamhub'
        elif server == 'uploaddo': other = 'Uploaddo'
        elif server == 'vembed': other = 'Vidguard'
        elif server == 'hexupload': other = 'Hexupload'
        elif server == 'userload': other = 'Userload'

        elif 'premiun' in server: continue

        server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url,
                              language = lang, quality = qlty, other = other ))

    # ~ Descargas
    bloque = scrapertools.find_single_match(data, '<div class="contEP contepID_3">(.*?)$')

    matches = re.compile('data-quality="(.*?)".*?data-lang="(.*?)".*?href="(.*?)".*?<span>.*?">(.*?)</b>', re.DOTALL).findall(bloque)

    for qlty, lang, url, server in matches:
        ses += 1

        if not url or not server: continue

        server = server.lower().strip()

        if '/ul.' in url: continue
        elif '/1fichier.' in url: continue
        elif '/ddownload.' in url: continue
        elif '/clk.' in url: continue
        elif '/rapidgator' in url: continue
        elif '/katfile' in url: continue
        elif '/nitro' in url: continue

        elif '/short/' in url: continue

        elif '/formatearwindows.' in url: continue

        if 'https://netload.cc/st?' in url:
             url = scrapertools.find_single_match(url, '&url=(.*?)$')
             if not url: continue

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()

        server = servertools.corregir_servidor(server)

        other = 'D'

        if not server == 'directo':
            if server == 'various': other = servertools.corregir_other(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, language = lang, quality = qlty, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

