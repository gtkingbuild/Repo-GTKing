# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://tv.ennovelas.net/'


_ajax = 'https://ennovelas.com.de/wp-content/themes/vo2022/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://ennovelas1.com/', 'https://ennovelas.cloud/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    raise_weberror = True
    if '/years/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Nuevos episodios', action = 'last_epis', url = host + 'episodes/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por país', action='paises', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    opciones = [
       ('action', 'Acción'),
       ('aventura', 'Aventura'),
       ('comedia', 'Comedia'),
       ('crimen', 'Crimen'),
       ('drama', 'Drama'),
       ('misterio', 'Misterio'),
       ('musica', 'Música'),
       ('romance', 'Romance'),
       ('srnovelas', 'SrNovelas'),
       ('thriller', 'Thriller'),
       ('terror', 'Terror'),
       ('western', 'Western')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'genre/' + opc + '/', action = 'list_all', text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie': limit_year = 2010
    else: limit_year = 1989

    for x in range(current_year, limit_year, -1):
        url = host + 'years/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En 480', action = 'list_all', url = host + 'quality/480p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 720', action = 'list_all', url = host + 'quality/720p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 1080', action = 'list_all', url = host + 'quality/1080p/', text_color='moccasin' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'América', action = 'list_all', url = host + 'country/united-states/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Argentina', action = 'list_all', url = host + 'country/argentina/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Brasil', action = 'list_all', url = host + 'country/brasil/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Chile', action = 'list_all', url = host + 'country/chile/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Colombia', action = 'list_all', url = host + 'country/colombia/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'España', action = 'list_all', url = host + 'country/espanol/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Filipinas', action = 'list_all', url = host + 'country/filipinas/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'México', action = 'list_all', url = host + 'country/mexico/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Perú', action = 'list_all', url = host + 'country/peru/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Reino unido', action = 'list_all', url = host + 'country/reino-unido/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Turquía', action = 'list_all', url = host + 'country/turkey-a/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Venezuela', action = 'list_all', url = host + 'country/venezuela/', text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        tipo = 'movie' if '/movies/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, 'data-img="(.*?)"')

        title = title.replace('&#8211;', '').replace('&#038;', '')

        year = scrapertools.find_single_match(match, '(\d{4})')
        if not year: year = '-'
        else:
           title = title.replace(year, '').strip()

        if '/years/' in item.url: year = scrapertools.find_single_match(item.url, "/years/(.*?)/")

        SerieName = title

        if " - " in SerieName: SerieName = SerieName.split(" - ")[0]
        if "(en Español)" in SerieName: SerieName = SerieName.split("(en Español)")[0]
        if "(en Espanol)" in SerieName: SerieName = SerieName.split("(en Espanol)")[0]
        if "en español" in SerieName: SerieName = SerieName.split("en español")[0]
        if "En Espanol" in SerieName: SerieName = SerieName.split("En Espanol")[0]
        if "en Espanol" in SerieName: SerieName = SerieName.split("en Espanol")[0]

        SerieName = SerieName.strip()

        if "Temporada" in SerieName: SerieName = SerieName.split("Temporada")[0]
        if "Capitulos" in SerieName: SerieName = SerieName.split("Capitulos")[0]

        SerieName = SerieName.strip()

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = SerieName, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            if '/search/' in item.url:
                cap = False
                if 'Capitulos' in title or 'Capítulos' in title: pass
                elif 'Capitulo' in title or 'Capítulo' in title: cap = True

                if cap:
                    season = scrapertools.find_single_match(title, 'Temporada(.*?)*').strip()
                    if not season: season = 1

                    epis = scrapertools.find_single_match(title, '- Capitulo(.*?)$').strip()
                    if not epis: epis = 1

                    title = title.replace('Capitulo', '[COLOR goldenrod]Capitulo[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Capítulo[/COLOR]')

                    itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                                contentSerieName = SerieName, contentType = 'episode',
                                                contentSeason = season, contentEpisodeNumber = epis, infoLabels={'year': year} ))
                    continue

            title = title.replace('Temporada', '[COLOR tan]Temporada[/COLOR]')

            title = title.replace('Capitulo', '[COLOR goldenrod]Capitulo[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Capítulo[/COLOR]').replace('capitulo', '[COLOR goldenrod]Capítulo[/COLOR]')

            lang = ''
            if '/espanol/' in item.url: lang = 'Esp'

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, lang=lang, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<div class='pagination'>.*?<span class='current'>.*?<a href='(.*?)'")
        if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-img="(.*?)"')

        title = title.replace('&#8211;', '').replace('&#038;', '')

        season = 1

        if "Temporada" in title:
            season = scrapertools.find_single_match(title, 'Temporada(.*?)Capitulo').strip()
            if not season: season = scrapertools.find_single_match(title, 'Temporada(.*?)Capítulo').strip()

            if not season: season = 1

        epis = scrapertools.find_single_match(match, '<div class="episodeNum">.*?</span>.*?<span>(.*?)</span>').strip()
        if not epis: epis = 1

        SerieName = title

        if " - " in SerieName: SerieName = SerieName.split(" - ")[0]
        if "(en Español)" in SerieName: SerieName = SerieName.split("(en Español)")[0]
        if "(en Espanol)" in SerieName: SerieName = SerieName.split("(en Espanol)")[0]
        if "en español" in SerieName: SerieName = SerieName.split("en español")[0]
        if "En Espanol" in SerieName: SerieName = SerieName.split("En Espanol")[0]
        if "en Espanol" in SerieName: SerieName = SerieName.split("en Espanol")[0]

        SerieName = SerieName.strip()

        if "Temporada" in SerieName: SerieName = SerieName.split("Temporada")[0]
        if "Capitulos" in SerieName: SerieName = SerieName.split("Capitulos")[0]
        if "Completo" in SerieName: SerieName = SerieName.split("Completo")[0]

        SerieName = SerieName.strip()

        title = title.replace('capitulo', '[COLOR goldenrod]capitulo[/COLOR]').replace('Capitulo', '[COLOR goldenrod]Capitulo[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Capítulo[/COLOR]')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, infoLabels={'year': '-'},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<div class='pagination'>.*?<span class='current'>.*?<a href='(.*?)'")
        if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'last_epis', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('data-season="(.*?)".*?>Temporada(.*?)</li>', re.DOTALL).findall(data)

    if not matches:
        bloque = scrapertools.find_single_match(data, '>Temporadas y episodios<(.*?)<footer>')

        d_season = scrapertools.find_single_match(data, 'data-season="(.*?)"')

        if bloque:
            epis = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

            if epis:
                if config.get_setting('channels_seasons', default=True):
                    platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR tan]Sin temporadas[/COLOR]')

                item.d_season = d_season
                item.page = 0
                item.contentType = 'season'

                season = scrapertools.find_single_match(item.url, '-temporada-(.*?)-')
                if not season: item.contentSeason = 1
                else: item.contentSeason = season

                itemlist = episodios(item)
                return itemlist

        return itemlist

    for d_season, numtempo in matches:
        numtempo = numtempo.strip()

        if not numtempo: numtempo = '1'

        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.d_season = d_season
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, d_season = d_season, page = 0, contentType = 'season', contentSeason = numtempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda x: x.title)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    if item.d_season:
        if _ajax in data:
            data = do_downloadpage(_ajax + 'temp/ajax/seasons.php?seriesID=' + item.d_season, headers = {'Referer': item.url, 'X-Requested-With': 'XMLHttpRequest'})
        else:
            data = do_downloadpage(host + 'wp-content/themes/vo2024/temp/ajax/seasons.php?seriesID=' + item.d_season, headers = {'Referer': item.url, 'X-Requested-With': 'XMLHttpRequest'})

        if not data: return itemlist

        epis = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
        if not epis: data = do_downloadpage(item.url)
    else:
        data = do_downloadpage(item.url)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('EnNovelas', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ENovelasUno', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ENovelasUno', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ENovelasUno', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ENovelasUno', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('ENovelasUno', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#8211;', "").strip()

        epis = scrapertools.find_single_match(match, '<span>Cap.*?<span>(.*?)</span>')
        if not epis: epis = 1

        thumb = scrapertools.find_single_match(match, 'data-img=".*?url(.*?)"')
        thumb = thumb.replace('(', '').replace(');', '').strip()

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    _php = scrapertools.find_single_match(data, '<form method="post" action="(.*?)"')

    if not _php: return itemlist

    _value = scrapertools.find_single_match(data, 'name="watch" value="(.*?)"')

    if not _value: return itemlist

    data = do_downloadpage(_php, post={'watch': _value, 'submit': ''})

    if item.lang == 'Esp': lang = 'Esp'
    elif 'película en español' in data or 'pelicula en español' in data: lang = 'Esp'
    elif 'en Espanol' in item.title: lang = 'Esp'
    else: lang = 'Lat'

    ses = 0

    # ~ embeds
    matches1 = scrapertools.find_multiple_matches(data, "<iframe.*?src='(.*?)'")
    matches2 = scrapertools.find_multiple_matches(data, "<div class='video-bibplayer-video'>.*?href='(.*?)'")

    matches = matches1 + matches2

    for url in matches:
        ses += 1

        url = url.strip()

        if '/likessb.' in url: continue

        if url.startswith('//'): url = 'https:' + url

        if 'api.mycdn.moe/uqlink.php?id=' in url: url = url.replace('api.mycdn.moe/uqlink.php?id=', 'uqload.com/embed-')

        elif 'api.mycdn.moe/dourl.php?id=' in url: url = url.replace('api.mycdn.moe/dourl.php?id=', 'dood.to/e/')

        elif 'api.mycdn.moe/dl/?uptobox=' in url: url = url.replace('api.mycdn.moe/dl/?uptobox=', 'uptobox.com/')

        elif url.startswith('http://vidmoly/'): url = url.replace('http://vidmoly/w/', 'https://vidmoly/embed-').replace('http://vidmoly/', 'https://vidmoly/')

        elif url.startswith('https://sr.ennovelas.net/'): url = url.replace('/sr.ennovelas.net/', '/waaw.to/')
        elif url.startswith('https://video.ennovelas.net/'): url = url.replace('/video.ennovelas.net/', '/waaw.to/')
        elif url.startswith('https://reproductor.telenovelas-turcas.com.es/'): url = url.replace('/reproductor.telenovelas-turcas.com.es/', '/waaw.to/')
        elif url.startswith('https://novelas360.cyou/player/'): url = url.replace('/novelas360.cyou/player/', '/waaw.to/')
        elif url.startswith('https://novelas360.cyou/'): url = url.replace('/novelas360.cyou/', '/waaw.to/')

        url = url.replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        if not servidor == 'directo':
            itemlist.append(Item( channel=item.channel, action = 'play', server = servidor, url = url, language = lang, other = other.capitalize() ))

    # ~ links onclick
    t_link = scrapertools.find_single_match(data, 'var vo_theme_dir = "(.*?)"')
    id_link = scrapertools.find_single_match(data, 'vo_postID = "(.*?)"')

    if t_link and id_link:
        clicks = scrapertools.find_multiple_matches(str(data), 'onclick="getServer.*?this.id,(.*?),(.*?);')

        for opt, srv in clicks:
            srv = srv.replace(')', '')

            data0 = do_downloadpage(t_link + '/temp/ajax/iframe2.php?id=' + id_link + '&video=' + opt + '&serverId=' + srv, headers = {'Referer': item.url, 'x-requested-with': 'XMLHttpRequest'} )

            data0 = data0.strip()

            if not data0: continue

            u_link = scrapertools.find_single_match(data0, '<iframe.*?src="(.*?)"')
            if not u_link: u_link = scrapertools.find_single_match(data0, '<IFRAME.*?SRC="(.*?)"')

            if u_link:
                if u_link.startswith('//'): u_link = 'https:' + u_link

                u_link = u_link.replace('&amp;', '&')

                servidor = servertools.get_server_from_url(u_link)
                servidor = servertools.corregir_servidor(servidor)

                u_link = servertools.normalize_url(servidor, u_link)

                other = ''
                if servidor == 'various': other = servertools.corregir_other(u_link)

                if not servidor == 'directo':
                    itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = u_link, server = servidor, language = lang, other = other ))

    # ~ links values
    values = scrapertools.find_multiple_matches(data, '<form method="post".*?action="(.*?)".*?<input type="hidden".*?name="(.*?)".*?value="(.*?)"')

    for link, type, value in values:
        ses += 1

        if not link: continue

        if type == 'watch': post = {'watch': str(value), 'submit': ''}
        else: post = {'download': str(value), 'submit': ''}

        data1 = do_downloadpage(link, post = post, headers = {'Referer': item.url} )

        matches = scrapertools.find_multiple_matches(data1, "<iframe.*?src='(.*?)'")
        if not matches: matches = scrapertools.find_multiple_matches(data1, '<iframe.*?src="(.*?)"')

        if not matches: matches = scrapertools.find_multiple_matches(data1, "<IFRAME.*?SRC='(.*?)'")
        if not matches: matches = scrapertools.find_multiple_matches(data1, '<IFRAME.*?SRC="(.*?)"')

        if not matches: matches = scrapertools.find_multiple_matches(data1, '<td>Server.*?href="(.*?)"')

        for url in matches:
            if '/wp-admin/' in url: continue

            if url.startswith('//'): url = 'https:' + url

            if 'api.mycdn.moe/uqlink.php?id=' in url: url = url.replace('api.mycdn.moe/uqlink.php?id=', 'uqload.com/embed-')

            elif 'api.mycdn.moe/dourl.php?id=' in url: url = url.replace('api.mycdn.moe/dourl.php?id=', 'dood.to/e/')

            elif 'api.mycdn.moe/dl/?uptobox=' in url: url = url.replace('api.mycdn.moe/dl/?uptobox=', 'uptobox.com/')

            elif url.startswith('http://vidmoly/'): url = url.replace('http://vidmoly/w/', 'https://vidmoly/embed-').replace('http://vidmoly/', 'https://vidmoly/')

            elif url.startswith('https://sr.ennovelas.net/'): url = url.replace('/sr.ennovelas.net/', '/waaw.to/')
            elif url.startswith('https://video.ennovelas.net/'): url = url.replace('/video.ennovelas.net/', '/waaw.to/')
            elif url.startswith('https://reproductor.telenovelas-turcas.com.es/'): url = url.replace('/reproductor.telenovelas-turcas.com.es/', '/waaw.to/')
            elif url.startswith('https://novelas360.cyou/player/'): url = url.replace('/novelas360.cyou/player/', '/waaw.to/')
            elif url.startswith('https://novelas360.cyou/'): url = url.replace('/novelas360.cyou/', '/waaw.to/')

            url = url.replace('&amp;', '&')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            if type == 'download':
                if other: other = other + ' D'
                else: other = 'D'

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other ))

    # ~ links post
    t_link = scrapertools.find_single_match(data, 'var vo_theme_dir = "(.*?)"')
    id_link = scrapertools.find_single_match(data, 'vo_postID = "(.*?)"')

    if t_link and id_link:
        i = 0

        while i <= 5:
           data2 = do_downloadpage(t_link + '/temp/ajax/iframe.php?id=' + id_link + '&video=' + str(i), headers = {'Referer': item.url, 'x-requested-with': 'XMLHttpRequest'} )

           data2 = data2.strip()

           if not data2: break

           ses += 1

           u_link = scrapertools.find_single_match(data2, '<iframe.*?src="(.*?)"')
           if not u_link: u_link = scrapertools.find_single_match(data2, '<IFRAME.*?SRC="(.*?)"')

           if u_link.startswith('//'): u_link = 'https:' + u_link

           if '/wp-admin/' in u_link: u_link = ''

           if u_link:
               if u_link.startswith('https://sr.ennovelas.net/'): u_link = u_link.replace('/sr.ennovelas.net/', '/waaw.to/')
               elif u_link.startswith('https://video.ennovelas.net/'): u_link = u_link.replace('/video.ennovelas.net/', '/waaw.to/')
               elif u_link.startswith('https://reproductor.telenovelas-turcas.com.es/'): u_link = u_link.replace('/reproductor.telenovelas-turcas.com.es/', '/waaw.to/')
               elif u_link.startswith('https://novelas360.cyou/player/'): u_link = u_link.replace('/novelas360.cyou/player/', '/waaw.to/')
               elif u_link.startswith('https://novelas360.cyou/'):  u_link =  u_link.replace('/novelas360.cyou/', '/waaw.to/')

               elif u_link.startswith('https://vk.com/'): u_link = u_link.replace('&amp;', '&')

               u_link = u_link.replace('&amp;', '&')

               servidor = servertools.get_server_from_url(u_link)
               servidor = servertools.corregir_servidor(servidor)

               u_link = servertools.normalize_url(servidor, u_link)

               other = ''
               if servidor == 'various': other = servertools.corregir_other(u_link)

               if not servidor == 'directo':
                   itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = u_link, server = servidor, language = lang, other = other ))

           i += 1

    # ~ Downloads
    data = do_downloadpage(item.url + '?do=downloads', headers = {'Referer': item.url, 'x-requested-with': 'XMLHttpRequest'})

    matches = scrapertools.find_multiple_matches(data, '<td>Server.*?href="(.*?)"')

    for url in matches:
        ses += 1

        if '/wp-admin/' in url: continue

        if url.startswith('//'): url = 'https:' + url

        if url.startswith('https://sr.ennovelas.net/'): url = url.replace('/sr.ennovelas.net/', '/waaw.to/')
        elif url.startswith('https://video.ennovelas.net/'): url = url.replace('/video.ennovelas.net/', '/waaw.to/')
        elif url.startswith('https://reproductor.telenovelas-turcas.com.es/'): url = url.replace('/reproductor.telenovelas-turcas.com.es/', '/waaw.to/')
        elif url.startswith('https://novelas360.cyou/player/'): url = url.replace('/novelas360.cyou/player/', '/waaw.to/')
        elif url.startswith('https://novelas360.cyou/'): url = url.replace('/novelas360.cyou/', '/waaw.to/')

        url = url.replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        if other: other = other + ' d'
        else: other = 'd'

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'search/' + texto.replace(" ", "+") + '/'
       return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

