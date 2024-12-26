# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ennovelas.org.pl/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://ennovelas.net.pl/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    raise_weberror = True
    if '/years/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + 'ultimos-capitulos/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por país', action='paises', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('action', 'Acción'),
       ('aventura', 'Aventura'),
       ('comedy', 'Comedia'),
       ('crime', 'Crimen'),
       ('drama', 'Drama'),
       ('mistery', 'Misterio'),
       ('music', 'Música'),
       ('romance', 'Romance'),
       ('thriller', 'Thriller'),
       ('terror', 'Terror'),
       ('western', 'Western')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url = host + 'genre/' + opc + '/', action = 'list_all', text_color = 'hotpink' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1989, -1):
        url = host + 'years/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'América', action = 'list_all', url = host + 'country/united-states/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Chile', action = 'list_all', url = host + 'country/chile/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Colombia', action = 'list_all', url = host + 'country/colombia/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'México', action = 'list_all', url = host + 'country/mexico/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Perú', action = 'list_all', url = host + 'country/peru/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Turquía', action = 'list_all', url = host + 'country/turkey/', text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, ' title="(.*?)"')

        if not url or not title: continue

        if '/movies/' in url: continue

        year = '-'
        if '/years/' in item.url: year = scrapertools.find_single_match(item.url, "/years/(.*?)/")

        SerieName = title

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        elif 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]

        SerieName = SerieName.strip()

        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]
        elif 'capitulo' in SerieName: SerieName = SerieName.split("capitulo")[0]

        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        temp = scrapertools.find_single_match(match, '<span>Season</span>.*?<span>(.*?)<span>').strip()
        if not temp: temp = 1

        title = title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                    contentType = 'tvshow', contentSerieName = SerieName, contentSeason = temp, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data or "<div class='pagination'>" in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?.*?href="(.*?)"')
            if not next_page: next_page = scrapertools.find_single_match(data, "<div class='pagination'>.*?<span class='current'>.*?href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, ' title="(.*?)"')

        if not url or not title: continue

        SerieName = title

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        elif 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]

        SerieName = SerieName.strip()

        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]
        elif 'capitulo' in SerieName: SerieName = SerieName.split("capitulo")[0]

        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        temp = 1

        epis = scrapertools.find_single_match(match, '<div class="episodeNum">.*?</span>.*?<span>(.*?)</span>')
        if not epis: epis = 1

        title = title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')

        title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Epis.[/COLOR]')

        titulo = str(temp) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSerieName = SerieName, contentSeason = temp, contentEpisodeNumber = epis, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data or "<div class='pagination'>" in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?.*?href="(.*?)"')
            if not next_page: next_page = scrapertools.find_single_match(data, "<div class='pagination'>.*?<span class='current'>.*?href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'last_epis', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if config.get_setting('channels_seasons', default=True):
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]Temporadas[/COLOR]')

    item.page = 0
    item.contentType = 'season'
    item.contentSeason = 1
    itemlist = episodios(item)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Temporada & Capitulos<(.*?)</ul></div></div></div>')

    episodes = scrapertools.find_multiple_matches(bloque, 'href="(.*?)".*?title="(.*?)".*?</em>.*?<span>(.*?)</span>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(episodes)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('EnNovelasPl', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('EnNovelasPl', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EnNovelasPl', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EnNovelasPl', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EnNovelasPl', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EnNovelasPl', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('EnNovelasPl', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, title, epis in episodes[item.page * item.perpage:]:
        if not epis: epis = 1

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(episodes) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


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

        itemlist.append(Item( channel=item.channel, action = 'play', server = servidor, url = url, language = lang, other = other.capitalize() ))

    # ~ links
    data = do_downloadpage(item.url + '?do=watch')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    # ~ links iframes
    iframes = scrapertools.find_multiple_matches(data, '<iframe src="(.*?)"')
    if not iframes: iframes = scrapertools.find_multiple_matches(data, '<IFRAME.*?SRC="(.*?)"')

    for iframe in iframes:
        if iframe.startswith('//'): iframe = 'https:' + iframe

        servidor = servertools.get_server_from_url(iframe)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor,iframe )

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other ))

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

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')

        title = scrapertools.find_single_match(article, ' title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')

        name = scrapertools.find_single_match(article, ' alt="(.*?)"')

        SerieName = name

        if 'capitulos' in name: SerieName = name.split("capitulos")[0]
        if 'temporada' in name: SerieName = name.split("temporada")[0]

        SerieName = SerieName.strip()

        title = title.capitalize()

        if '-capitulo-' in url:
            epis = scrapertools.find_single_match(url, '-capitulo-(.*?)$')

            epis = epis.replace('/', '')

            if not epis: epis = 1

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, infoLabels={'year': '-'},
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epis ))

        else:
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, infoLabels={'year': '-'}, 
                                        contentSerieName = SerieName, contentType = 'tvshow' ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'class="page-numbers current".*?href="(.*?)"')

        if next_page:
            if '?s=' in next_page:
                itemlist.append(item.clone( title = "Siguientes ...", action = "list_search", url = next_page, text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search/' + texto.replace(" ", "+") + '/'
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
