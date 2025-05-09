# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ennovelas.com.se/'


def do_downloadpage(url, post=None, headers=None):
    if not headers: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'novelas-completas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host + 'episodes/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'tvshow' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        url = host + 'years/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    opciones = [
       ('action', 'Acción'),
       ('aventura', 'Aventura'),
       ('comedy', 'Comedia'),
       ('crime', 'Crimen'),
       ('documentary', 'Documental'),
       ('drama', 'Drama'),
       ('family', 'Familia'),
       ('history', 'Historia'),
       ('mistery', 'Misterio'),
       ('music', 'Música'),
       ('musical', 'Músical'),
       ('romance', 'Romance'),
       ('thriller', 'Thriller'),
       ('terror', 'Terror'),
       ('western', 'Western')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url = host + 'genre/' + opc + '/', action = 'list_all', text_color=text_color ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'América', action = 'list_all', url = host + 'country/united-states/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Brasil', action = 'list_all', url = host + 'country/brasil/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Chile', action = 'list_all', url = host + 'country/chile/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Colombia', action = 'list_all', url = host + 'country/colombia/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'México', action = 'list_all', url = host + 'country/mexico/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Perú', action = 'list_all', url = host + 'country/peru/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Turquía', action = 'list_all', url = host + 'country/turkey-a/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Venezuela', action = 'list_all', url = host + 'country/venezuela/', text_color='hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, ' title="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#8211;', "").replace('&#8220;', "").replace('&#8221;', "").strip()
        title = title.replace('&#8216;', "").replace('&#8217;', "").replace('&#8230;', "").strip()
        title = title.replace('&#038;', '&').replace('&amp;', '&')

        title = title.capitalize()

        SerieName = title

        if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]

        if 'capítulo' in SerieName: SerieName = SerieName.split("capítulo")[0]
        if 'capitulo' in SerieName: SerieName = SerieName.split("capitulo")[0]

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        if 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]

        if "En Español" in SerieName: SerieName = SerieName.split("En Español")[0]
        if "en español" in SerieName: SerieName = SerieName.split("en español")[0]

        if "(En Español)" in SerieName: SerieName = SerieName.split("(En Español)")[0]
        if "(en español)" in SerieName: SerieName = SerieName.split("(en español)")[0]

        if "En Espanol" in SerieName: SerieName = SerieName.split("En Espanol")[0]
        if "en espanol" in SerieName: SerieName = SerieName.split("en espanol")[0]

        if "(En Espanol)" in SerieName: SerieName = SerieName.split("(En Espanol)")[0]
        if "(en espanol)" in SerieName: SerieName = SerieName.split("(en espanol)")[0]

        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, 'data-img="(.*?)"')

        tipo = 'movie' if '/movies/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = SerieName, infoLabels={'year': '-'} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            title = title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')

            title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Epis.[/COLOR]')
            title = title.replace('capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('capítulo', '[COLOR goldenrod]Epis.[/COLOR]')

            if '-capitulo-' in url:
                itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                            contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))
            else:
                itemlist.append(item.clone( action = 'temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                           contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<div class='pagination'>" in data:
            next_page = scrapertools.find_single_match(data, "<div class='pagination'>.*?<span class='current'>.*?<a href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    tempo = scrapertools.find_single_match(item.url, '-temporada-(.*?)-')
    if not tempo: tempo = scrapertools.find_single_match(item.url, '-temporada-(.*?)$')

    tempo = tempo.replace('/', '')

    if not tempo: tempo = 1

    if config.get_setting('channels_seasons', default=True):
        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]Temporadas[/COLOR]')

    item.page = 0
    item.contentType = 'season'
    item.contentSeason = tempo
    itemlist = episodios(item)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    tempo = scrapertools.find_single_match(item.url, '-temporada-(.*?)-')
    if not tempo: tempo = scrapertools.find_single_match(item.url, '-temporada-(.*?)$')

    tempo = tempo.replace('/', '')

    if not tempo: tempo = 1

    bloque = scrapertools.find_single_match(data, '>Temporadas y episodios<(.*?)</div></div></div></div>')

    episodes = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(episodes)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('NovelasPlus', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('NovelasPlus', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('NovelasPlus', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('NovelasPlus', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('NovelasPlus', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('NovelasPlus', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('NovelasPlus', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in episodes[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#8211;', "").replace('&#8220;', "").replace('&#8221;', "").strip()
        title = title.replace('&#8216;', "").replace('&#8217;', "").replace('&#8230;', "").strip()
        title = title.replace('&#038;', '&').replace('&amp;', '&')

        epis = scrapertools.find_single_match(url, '-capitulo-(.*?)$')

        if '-' in epis:
            epis = epis.split("-")[0]
            epis = epis.strip()

        epis = epis.replace('/', '')

        if not epis:
            epis = scrapertools.find_single_match(match, '<span>Cap</span>.*?<span>(.*?</span>')

            if not epis:
                epis = 1

        if len(episodes) >= 10:
            if len(str(epis)) == 1: epis = '0' + str(epis)

        season = scrapertools.find_single_match(url, '-temporada-(.*?)-')
        if season == 'capitulo' or season == 'capituloo' or season == 'completo': season = ''

        if not season:
            season = tempo
            if not season:
                season = 1

        titulo = str(season) + 'x' + str(epis) + ' ' + title

        titulo = titulo.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')

        titulo = titulo.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Epis.[/COLOR]')
        titulo = titulo.replace('capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('capítulo', '[COLOR goldenrod]Epis.[/COLOR]')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis, epis = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(episodes) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral', epis = '1000' ))

    return sorted(itemlist,key=lambda x: x.epis)


def findvideos(item):
    logger.info()
    itemlist = []

    if item.lang == 'Esp': lang = 'Esp'
    elif item.lang == 'Vose': lang = 'Vose'
    else: lang = 'Lat'

    data = do_downloadpage(item.url)

    ses = 0

    # ~ embeds
    matches = scrapertools.find_multiple_matches(data, 'data-title="Opción.*?data-src="(.*?)"')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<iframe.*?data-src="(.*?)"')

    if not matches: matches = scrapertools.find_multiple_matches(data, 'data-title="Opción.*?src="(.*?)"')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    for url in matches:
        ses += 1

        url = url.strip()

        if '/likessb.' in url: continue
        elif '/scripts/' in url: continue
        elif 'data:image' in url: continue

        if host[:-1] in url: continue

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
        elif url.startswith('https://w.ennovelas.io/'): url = url.replace('/w.ennovelas.io/', '/waaw.to/')
        elif url.startswith('https://sr.ennovelas.io/'): url = url.replace('/sr.ennovelas.io/', '/waaw.to/')

        url = url.replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel=item.channel, action = 'play', server = servidor, url = url, language = lang, other = other.capitalize() ))

    # ~ links

    data = do_downloadpage(item.url + '?do=watch')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    values = scrapertools.find_multiple_matches(data, '<form method="post".*?action="(.*?)".*?<input type="hidden".*?name="(.*?)".*?value="(.*?)"')

    for link, type, value in values:
        ses += 1

        if not link: continue

        if type == 'watch': post = {'watch': str(value)}
        else: post = {'download': str(value)}

        data1 = do_downloadpage(link, post = post, headers = {'Referer': item.url} )

        matches = scrapertools.find_multiple_matches(data1, "<iframe.*?src='(.*?)'")
        if not matches: matches = scrapertools.find_multiple_matches(data1, '<iframe.*?src="(.*?)"')

        if not matches: matches = scrapertools.find_multiple_matches(data1, "<IFRAME.*?SRC='(.*?)'")
        if not matches: matches = scrapertools.find_multiple_matches(data1, '<IFRAME.*?SRC="(.*?)"')

        if not matches: matches = scrapertools.find_multiple_matches(data1, '<td>Server.*?href="(.*?)"')

        for url in matches:
            if '/wp-admin/' in url: continue
            elif '/scripts/' in url: continue
            elif 'data:image' in url: continue

            if host[:-1] in url: continue

            if url.startswith('//'): url = 'https:' + url

            elif 'api.mycdn.moe/uqlink.php?id=' in url: url = url.replace('api.mycdn.moe/uqlink.php?id=', 'uqload.com/embed-')

            elif 'api.mycdn.moe/dourl.php?id=' in url: url = url.replace('api.mycdn.moe/dourl.php?id=', 'dood.to/e/')

            elif 'api.mycdn.moe/dl/?uptobox=' in url: url = url.replace('api.mycdn.moe/dl/?uptobox=', 'uptobox.com/')

            elif url.startswith('http://vidmoly/'): url = url.replace('http://vidmoly/w/', 'https://vidmoly/embed-').replace('http://vidmoly/', 'https://vidmoly/')

            elif url.startswith('https://sr.ennovelas.net/'): url = url.replace('/sr.ennovelas.net/', '/waaw.to/')
            elif url.startswith('https://video.ennovelas.net/'): url = url.replace('/video.ennovelas.net/', '/waaw.to/')
            elif url.startswith('https://reproductor.telenovelas-turcas.com.es/'): url = url.replace('/reproductor.telenovelas-turcas.com.es/', '/waaw.to/')
            elif url.startswith('https://novelas360.cyou/player/'): url = url.replace('/novelas360.cyou/player/', '/waaw.to/')
            elif url.startswith('https://novelas360.cyou/'): url = url.replace('/novelas360.cyou/', '/waaw.to/')
            elif url.startswith('https://w.ennovelas.io/'): url = url.replace('/w.ennovelas.io/', '/waaw.to/')
            elif url.startswith('https://sr.ennovelas.io/'): url = url.replace('/sr.ennovelas.io/', '/waaw.to/')

            url = url.replace('&amp;', '&')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            if type == 'download':
                if other: other = other + ' D'
                else: other = 'D'

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other ))

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
           elif '/scripts/' in u_link: u_link = ''
           elif 'data:image' in u_link: u_link = ''

           if u_link:
               if u_link.startswith('https://sr.ennovelas.net/'): u_link = u_link.replace('/sr.ennovelas.net/', '/waaw.to/')
               elif u_link.startswith('https://video.ennovelas.net/'): u_link = u_link.replace('/video.ennovelas.net/', '/waaw.to/')
               elif u_link.startswith('https://reproductor.telenovelas-turcas.com.es/'): u_link = u_link.replace('/reproductor.telenovelas-turcas.com.es/', '/waaw.to/')
               elif u_link.startswith('https://novelas360.cyou/player/'): u_link = u_link.replace('/novelas360.cyou/player/', '/waaw.to/')
               elif u_link.startswith('https://novelas360.cyou/'): u_link = u_link.replace('/novelas360.cyou/', '/waaw.to/')
               elif u_link.startswith('https://w.ennovelas.io/'): u_link = u_link.replace('/w.ennovelas.io/', '/waaw.to/')
               elif u_link.startswith('https://sr.ennovelas.io/'): u_link = u_link.replace('/sr.ennovelas.io/', '/waaw.to/')

               elif u_link.startswith('https://vk.com/'): u_link = u_link.replace('&amp;', '&')

               u_link = u_link.replace('&amp;', '&')

               servidor = servertools.get_server_from_url(u_link)
               servidor = servertools.corregir_servidor(servidor)

               u_link = servertools.normalize_url(servidor, u_link)

               other = ''
               if servidor == 'various': other = servertools.corregir_other(u_link)

               itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = u_link, server = servidor, language = lang, other = other ))

           i += 1

    # ~ Downloads
    data = do_downloadpage(item.url + '?do=downloads', headers = {'Referer': item.url, 'x-requested-with': 'XMLHttpRequest'})

    matches = scrapertools.find_multiple_matches(data, '<td>Server.*?href="(.*?)"')

    for url in matches:
        ses += 1

        if '/wp-admin/' in url: continue
        elif '/scripts/' in url: continue
        elif 'data:image' in url: continue

        if url.startswith('//'): url = 'https:' + url

        if url.startswith('https://sr.ennovelas.net/'): url = url.replace('/sr.ennovelas.net/', '/waaw.to/')
        elif url.startswith('https://video.ennovelas.net/'): url = url.replace('/video.ennovelas.net/', '/waaw.to/')
        elif url.startswith('https://reproductor.telenovelas-turcas.com.es/'): url = url.replace('/reproductor.telenovelas-turcas.com.es/', '/waaw.to/')
        elif url.startswith('https://novelas360.cyou/player/'): url = url.replace('/novelas360.cyou/player/', '/waaw.to/')
        elif url.startswith('https://novelas360.cyou/'): url = url.replace('/novelas360.cyou/', '/waaw.to/')
        elif url.startswith('https://w.ennovelas.io/'): url = url.replace('/w.ennovelas.io/', '/waaw.to/')
        elif url.startswith('https://sr.ennovelas.io/'): url = url.replace('/sr.ennovelas.io/', '/waaw.to/')

        url = url.replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        if other: other = other + ' d'
        else: other = 'd'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if '.strp2p.' in url: url = ''

    elif url == 'https://ennovelas.net/': url = ''

    if url:
        if url.startswith("https://sb"):
            return 'Servidor [COLOR goldenrod]Obsoleto[/COLOR]'

        elif 'streamsb' in url or 'playersb' in url or 'pelisplay' in url or 'tomatomatela' in url:
            return 'Servidor [COLOR goldenrod]Obsoleto[/COLOR]'

        elif '.fembed.' in url or 'fembed' in url:
            return 'Servidor [COLOR red]Fuera de Servicio[/COLOR]'

        elif '/xvideosharing.' in url:
            return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

        elif '/clonamesta.' in url:
            return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

        if not 'https' in url: url = url.replace('http', 'https')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        url = servertools.normalize_url(servidor, url)

        if 'streamwish' in url or 'strwish' in url or 'embedwish' in url or 'wishembed' in url or 'awish' in url or 'dwish' in url or 'mwish' in url or 'wishfast' in url or 'sfastwish' in url or 'doodporn' in url or 'flaswish' in url or 'obeywish' in url or 'cdnwish' in url or 'asnwish' in url or 'flastwish' in url or 'jodwish' in url or 'swhoi' in url or 'fsdcmo' in url or 'swdyu' in url or 'wishonly' in url or 'playerwish' in url or 'hlswish' in url or 'wish' in url or 'iplayerhls' in url or 'hlsflast' in url or 'ghbrisk' in url:
            url += "|Referer=" + host

        elif 'vudeo' in url:
            url += "|Referer=" + host

        itemlist.append(item.clone( url=url, server=servidor ))

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


