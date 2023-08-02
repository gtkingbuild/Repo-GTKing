# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools, tmdb


host = 'https://clasico.tv/'


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
    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tvshows/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host + 'episodes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', url = host, search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    productoras = [
        ('amazon', 'Amazon'),
        ('cartoon-network', 'Cartoon Network'),
        ('disney', 'Disney+'),
        ('fox', 'FOX'),
        ('hbo', 'HBO'),
        ('mtv', 'MTV'),
        ('netflix', 'Netflix')
        ]

    for opc, tit in productoras:
        url = host + 'network/' + opc + '/'

        itemlist.append(item.clone( title = tit, action = 'list_all', url = url ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('accion', 'Acción'),
       ('action-adventure', 'Action & Adventure'),
       ('animacion', 'Animación'),
       ('aventura', 'Aventura'),
       ('belica', 'Bélica'),
       ('ciencia-ficcion', 'Ciencia ficción'),
       ('comedia', 'Comedia'),
       ('crimen', 'Crimen'),
       ('documental', 'Documental'),
       ('drama', 'Drama'),
       ('familia', 'Familia'),
       ('fantasia', 'Fantasía'),
       ('kids', 'Kids'),
       ('misterio', 'Misterio'),
       ('musica', 'Música'),
       ('reality', 'Reality'),
       ('sci-fi-fantasy', 'Sci-Fi & Fantasy'),
       ('suspense', 'Suspense'),
       ('soap', 'Soap'),
       ('terror', 'Terror'),
       ('war-politics', 'War & Politics'),
       ('western', 'Western')
       ]

    for opc, tit in opciones:
        if item.search_type == 'tvshow':
            if opc == 'ciencia-ficcion': continue
            elif opc == 'musica': continue
            elif opc == 'terror': continue
        else:
            if opc == 'action-adventure': continue
            elif opc == 'kids': continue
            elif opc == 'reality': continue
            elif opc == 'sci-fi-fantasy': continue
            elif opc == 'soap': continue
            elif opc == 'war-politics': continue

        itemlist.append(item.clone( title = tit, url= host + 'genre/' + opc + '/', action = 'list_all' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#':
        itemlist.append(item.clone( title = letra, action = 'list_letra', letra = letra.lower() ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article id="post-(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, '<a href="([^"]+)')
        title = scrapertools.find_single_match(article, ' alt="(.*?)"').strip()

        if not url or not title: continue

        tipo = 'movie' if '/movies/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)')

        year = scrapertools.find_single_match(article, '</h3> <span>.*?,(.*?)</span>').strip()
        if not year: year = '-'

        plot = scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>')
        plot = scrapertools.htmlclean(plot)

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if '/genre/' in item.url:
        if not itemlist: return itemlist

    if itemlist:
        if '<div class="pagination">' in data:
           next_url = ''

           if item.search_type == 'movie':
               next_url = scrapertools.find_single_match(data, '<span class="current">.*?<a href=(.*?)class="inactive">')
               if next_url:
                   next_url = next_url.replace("'", '').strip()
                   next_page = ''
           else:
              if "id='nextpagination'" in data:
                  next_url = item.url

                  if not item.page == 1: next_url = next_url.split('page/')[0]

                  next_url = next_url + 'page/'
                  next_page = item.page + 1
              else:
                  next_url = scrapertools.find_single_match(data, '<span class="current">.*?<a href=(.*?)class="inactive">')
                  if next_url:
                      next_url = next_url.replace("'", '').strip()
                      next_page = ''

           if next_url:
               if next_page: next_url = next_url  + str(next_page) + '/'

               itemlist.append(item.clone (url = next_url, title = 'Siguientes ...', action = 'list_all', page = next_page, text_color='coral' ))

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<article (.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        temp_epi = scrapertools.find_single_match(url, '-(\d+)x(\d+)/$')

        if not temp_epi: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h3><a[^>]+>([^<]+)</a></h3>')
        name = scrapertools.find_single_match(article, '<span class="serie">([^<]+)</span>')

        titulo = temp_epi[0] + 'x' + temp_epi[1] + ' ' + name + ': ' + title

        itemlist.append(item.clone( action = 'findvideos', title = titulo, url = url, thumbnail = thumb,
                                    contentType = 'episode', contentSerieName = name, contentSeason = temp_epi[0], contentEpisodeNumber = temp_epi[1] ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_url = ''

            if "id='nextpagination'" in data:
                next_url = item.url

                if not item.page == 1: next_url = next_url.split('page/')[0]

                next_url = next_url + 'page/'
                next_page = item.page + 1
            else:
                next_url = scrapertools.find_single_match(data, '<span class="current">.*?<a href=(.*?)class="inactive">')
                if next_url:
                   next_url = next_url.replace("'", '').strip()
                   next_page = ''

            if next_url:
                if next_page: next_url = next_url  + str(next_page) + '/'

                itemlist.append(item.clone (url = next_url, title = 'Siguientes ...', action = 'list_epis', page = next_page, text_color='coral' ))

    return itemlist


def list_letra(item):
    logger.info()
    itemlist = []

    url = host + 'wp-json/dooplay/glossary/?term=' + item.letra + '&nonce=262b33c1c6&type='

    if item.search_type == 'movie': url = url + 'movies'
    else: url = url + 'tvshows'

    data = httptools.downloadpage(url).data

    try:
        data_js = jsontools.load(data)

        if not 'error' in data_js:
            for match in data_js:
                elem = data_js[match]

                url = elem['url']
                url = url.replace('\\/', '/')

                if not url: continue

                title = elem['title']
                thumb = re.sub(r'-\d+x\d+.jpg', '.jpg', elem['img'])

                try:
                    year = elem['year']
                except:
                    year = '-'

                if '/movies/' in url:
                    if item.search_type == 'tvshow': continue

                    itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                            contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))
                else:
                    if item.search_type == 'movie': continue

                    itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                                contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))
    except:
        pass

    if itemlist: 
        tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, "<div class='se-c'>.*?<span.*?'>(.*?)<.*?class='title'>(.*?)<i>")

    for numtempo, title in matches:
        title = title.strip()

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + "(.*?)</ul></div>")

    matches = scrapertools.find_multiple_matches(bloque, "<li class='mark-(.*?)</li>")

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('ClasicoTv', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ClasicoTv', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ClasicoTv', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('ClasicoTv', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('ClasicoTv', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for data_epi in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(data_epi, "<a href='(.*?)'")

        if url:
            thumb = scrapertools.find_single_match(data_epi, "src='(.*?)'")

            title = scrapertools.find_single_match(data_epi, "<a href=.*?'>(.*?)</a>")
            title = title.strip()

            episode = title.lower()
            episode = episode.replace('episodio', '').strip()

            numer = scrapertools.find_single_match(data_epi, "<div class='numerando'>(.*?)</div>")
            numer = numer.strip()
            if numer:
                episode = numer.split(' - ')[1]
                numer = numer.replace(' - ', 'x')
                title = numer + '  ' + title

            fecha = scrapertools.find_single_match(data_epi, "<span class='date'>(.*?)</span>").strip()
            if fecha: title = title + '  (' + fecha + ')'

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    lang = 'Lat'

    data = httptools.downloadpage(item.url).data

    if 'subtitulado' in item.title.lower() or 'subtitulada' in item.title.lower(): lang = 'Vose'

    bloque = scrapertools.find_single_match(data, "<ul id='playeroptionsul'(.*?)</ul>")

    matches = scrapertools.find_multiple_matches(bloque, "<li id='player-option-(.*?)</li>")

    ses = 0

    for match in matches:
        ses += 1

        if 'youtube' in match: continue

        data_post = scrapertools.find_single_match(match, "data-post='(.*?)'")
        data_nume = scrapertools.find_single_match(match, "data-nume='(.*?)'")
        data_type = scrapertools.find_single_match(match, "data-type='(.*?)'")

        if not data_post or not data_nume or not data_type: continue

        post = {'action': 'doo_player_ajax', 'post': data_post, 'nume': data_nume, 'type': data_type}
        headers = {'Referer': item.url}

        data = httptools.downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers).data

        url = scrapertools.find_single_match(str(data), 'src=.*?"(.*?)"')
        if not url: url = scrapertools.find_single_match(str(data), '"embed_url":"(.*?)"')

        if url:
           url = url.replace('\\/', '/')

           if 'data:text/javascript;base64,' in url:
               url_b64 = url.replace('data:text/javascript;base64,', '')
               src_b64 = base64.b64decode(url_b64)
               url = scrapertools.find_single_match(src_b64, "src = '(.*?)'")

               url = url.replace('\\/', '/')

        if url:
           if url.endswith('.js') == True: continue

           if url.startswith('//') == True: url = 'https:' + url

           servidor = servertools.get_server_from_url(url)
           servidor = servertools.corregir_servidor(servidor)

           if servidor and servidor != 'directo':
               url = servertools.normalize_url(servidor, url)

               itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search_results(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article>(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' alt="(.*?)"').strip()

        if not url or not title: continue

        tipo = 'tvshow' if 'class="tvshows"' in article else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)')

        year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        plot = scrapertools.find_single_match(article, '<div class="contenido"><p>(.*?)</p>')
        plot = scrapertools.htmlclean(plot)

        if '/movies/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return search_results(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
