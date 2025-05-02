# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://mega1link.com/'


def do_downloadpage(url, post=None, headers=None):
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

    itemlist.append(item.clone( title = 'Catálogo', action='list_all', url = host + 'peliculas/' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', _avis = True, search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', _avis = True, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Castellano', action='list_all', url = host + 'tag/espanol-castellano/', text_color='moccasin' ))
    itemlist.append(item.clone( title='Latino', action='list_all', url = host + 'tag/espanol-latino/', text_color='moccasin' ))
    itemlist.append(item.clone( title='Subtitulado', action='list_all', url = host + 'tag/subtitulada/', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Genero</a>(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<a href=(.*?)>(.*?)</a>')

    for url, title in matches:
        if not '/genero/' in url: continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = text_color ))

    if itemlist:
        itemlist.append(item.clone( action = 'list_all', title = 'Bélica', url = host + 'genero/belica/', text_color = text_color ))
        itemlist.append(item.clone( action = 'list_all', title = 'Western', url = host + 'genero/western/',text_color = text_color  ))

    return sorted(itemlist, key=lambda it: it.title)


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'Calidad</a>(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<a href=(.*?)>(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title='En ' + title, url = url, text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)<strong>Mega1Link</strong>')
    if not bloque: bloque = scrapertools.find_single_match(data, '<h1(.*?)<strong>Mega1Link</strong>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        article = scrapertools.decodeHtmlentities(article)

        url = scrapertools.find_single_match(article, ' href="(.*?)"')
        if not url: url = scrapertools.find_single_match(article, " href='(.*?)'")
        if not url: url = scrapertools.find_single_match(article, ' href=(.*?)>')

        title = scrapertools.find_single_match(article, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(article, ' data-src=(.*?) ')

        year = scrapertools.find_single_match(article, '<span class=year>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>.*?,(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(article, '<span>(.*?)</span>').strip()

        if year: title = title = title.replace(' ' + year, '').replace(' (' + year + ')', '').strip()
        else: year = '-'

        if '/release/' in item.url: year = scrapertools.find_single_match(item.url, "/release/(.*?)/")

        qlty = scrapertools.find_single_match(article, '<span class=quality>(.*?)</span>')
        qlty = re.sub(' -$', '', qlty)

        plot = scrapertools.find_single_match(article, '<div class=texto>(.*?)</div>')

        PeliTitle = title

        if "Latino" in PeliTitle: PeliTitle = PeliTitle.split("Latino")[0]

        if "DVDrip" in PeliTitle: PeliTitle = PeliTitle.split("DVDrip")[0]
        if " HD " in PeliTitle: PeliTitle = PeliTitle.split(" HD ")[0]
        if " hd " in PeliTitle: PeliTitle = PeliTitle.split(" hd ")[0]
        if " HD" in PeliTitle: PeliTitle = PeliTitle.split(" HD")[0]
        if " hd" in PeliTitle: PeliTitle = PeliTitle.split(" hd")[0]

        tipo = 'tvshow' if '/series/' in url else 'movie'

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='movie', contentTitle=PeliTitle, infoLabels={'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='tvshow', contentSerieName=PeliTitle, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span class="current">.*?' + "<a href='(.*?)'")
        if not next_page: next_page = scrapertools.find_single_match(data, '<span class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (url = next_page, page = 0, title = 'Siguientes ...', action = 'list_all', text_color='coral'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile("<span class='title'>Season(.*?)<i>", re.DOTALL).findall(data)

    for numtempo in matches:
        if not numtempo: continue

        numtempo = numtempo.strip()

        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = numtempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<span class='se-t se-o'>" + str(item.contentSeason) + '(.*?)</div></div></div></div>')

    patron = "<li class='mark-.*?" + '<img src="(.*?)".*?' + "<div class='numerando'>(.*?)</div>.*?a href='(.*?)'.*?>(.*?)</a>"

    matches = scrapertools.find_multiple_matches(bloque, patron)

    if not matches:
        patron = "<li class='mark-.*?<img src='(.*?)'.*?<div class='numerando'>(.*?)</div>.*?a href='(.*?)'.*?>(.*?)</a>"

        matches = scrapertools.find_multiple_matches(bloque, patron)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('Mega1Link', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Mega1Link', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Mega1Link', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Mega1Link', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Mega1Link', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Mega1Link', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Mega1Link', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, temp_epis, url, title in matches[item.page * item.perpage:]:
        if not 'http' in thumb: thumb = 'https:' + thumb

        epis = scrapertools.find_single_match(temp_epis, '.*?-(.*?)$').strip()

        titulo = "%sx%s - %s" % (str(item.contentSeason), epis, title)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, contentType = 'episode', contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color= 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Español Castellano': 'Esp', 'Castellano': 'Esp', 'Español': 'Esp', 'Spanish': 'Esp', 'Español Latino': 'Lat', 'Latino': 'Lat','Subtitulada': 'Vose', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    ses = 0

    # Video Soources
    matches: matches = scrapertools.find_multiple_matches(data, 'id="player-option-(.*?)</li>')
    if not matches: matches = scrapertools.find_multiple_matches(data, "id='player-option-(.*?)</li>")

    for match in matches:
        # ~ dtype, dpost, dnume
        dtype = scrapertools.find_single_match(match, ' data-type="(.*?)"')
        if not dtype: dtype = scrapertools.find_single_match(match, " data-type='(.*?)'")

        dpost = scrapertools.find_single_match(match, ' data-post="(.*?)"')
        if not dpost: dpost = scrapertools.find_single_match(match, " data-post='(.*?)'")

        dnume = scrapertools.find_single_match(match, ' data-nume="(.*?)"')
        if not dnume: dnume = scrapertools.find_single_match(match, " data-nume='(.*?)'")

        if dtype and dpost and dnume:
            data1 = do_downloadpage(host + '/wp-json/dooplayer/v2/' + dpost + '/' + dtype + '/' + dnume +'/')

            embed = scrapertools.find_single_match(str(data1), '"embed_url":.*?"(.*?)"')

            if embed:
                ses += 1

                if not dnume == 'trailer':
                    embed = embed.replace('\\/', '/')

                    if embed.startswith('//'): embed = 'https:' + embed

                    if not '/pelisplay.' in embed:
                        if embed.startswith('//'):embed  = 'https:' + embed

                        servidor = servertools.get_server_from_url(embed)
                        servidor = servertools.corregir_servidor(servidor)

                        embed = servertools.normalize_url(servidor, embed)

                        lang = scrapertools.find_single_match(match, '<span class="title">(.*?)</span>')
                        if not lang: lang = scrapertools.find_single_match(match, "<span class='title'>(.*?)</span>")

                        if 'Latino' in lang: lang = 'Lat'
                        elif 'Castellano' in lang or 'Español' in lang or 'Spanish' in lang: lang = 'Esp'
                        elif 'Subtitulado' in lang or 'VOSE' in lang or 'Vose' in lang: lang = 'Vose'
                        elif 'Inglés' in lang: lang = 'Vo'
                        else: lang = '?'

                        other = ''
                        if servidor == 'various': other = servertools.corregir_other(embed)

                        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = embed, language = lang, other = other ))
                    else:
                        data2 = do_downloadpage(embed)

                        links = scrapertools.find_multiple_matches(data2, '<li class="linkserver".*?data-video="(.*?)"')
                        if not links: links = scrapertools.find_multiple_matches(data2,"'<li class='linkserver'.*?data-video='(.*?)'")

                        if links:
                            for url in links:
                                ses += 1

                                if '/hydrax.' in url: continue
                                elif '/xupalace.' in url: continue
                                elif '/uploadfox.' in url: continue

                                if url.startswith('//'): url = 'https:' + url

                                servidor = servertools.get_server_from_url(url)
                                servidor = servertools.corregir_servidor(servidor)

                                url = servertools.normalize_url(servidor, url)

                                lang = scrapertools.find_single_match(match, '<span class="title">(.*?)</span>')
                                if not lang: lang = scrapertools.find_single_match(match, "<span class='title'>(.*?)</span>")

                                if 'Latino' in lang: lang = 'Lat'
                                elif 'Castellano' in lang or 'Español' in lang or 'Spanish' in lang: lang = 'Esp'
                                elif 'Subtitulado' in lang or 'VOSE' in lang or 'Vose' in lang: lang = 'Vose'
                                elif 'Inglés' in lang: lang = 'Vo'
                                else: lang = '?'

                                other = ''
                                if servidor == 'various': other = servertools.corregir_other(url)

                                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    # Descargas
    i = 0

    matches = re.compile('<tr id=(.*?)</tr>', re.DOTALL).findall(data)

    for lin in matches:
        ses += 1

        if '<th' in lin: continue

        url = scrapertools.find_single_match(lin, '<a href="(.*?)"')
        if not url: url = scrapertools.find_single_match(lin, "<a href='(.*?)'")

        servidor = scrapertools.find_single_match(lin, "domain=([^.']+)").strip()

        if not url or not servidor: continue

        if servidor == 'soon': continue
        elif servidor == 'uii': continue
        elif servidor == 'rinku': continue
        elif servidor == 'koramaup': continue

        if servidor == 'pastedvdrip':
            if '/links/' in url:
               i += 1

               if i > 1: continue

               if config.get_setting('channels_charges', default=True):
                   platformtools.dialog_notification('Mega1Link', '[COLOR blue]Cargando enlaces[/COLOR]')

               data1 = do_downloadpage(url)

               matches1 = scrapertools.find_multiple_matches(data1, 'href="(.*?)"')

               for match in matches1:
                   data2 = httptools.downloadpage(match).data

                   links = scrapertools.find_multiple_matches(data2, '<a target=.*?href="(.*?)"')

                   for link in links:
                       if not '/pastedvdrip.' in link: continue

                       try:
                           new_url = httptools.downloadpage(link, follow_redirects=False).headers['location']
                       except: continue

                       if new_url:
                           if '/1fichier.' in new_url: continue
                           elif '/koramaup.' in new_url: continue
                           elif '/akirabox.' in new_url: continue

                           url = new_url

                           servidor = servertools.get_server_from_url(url)
                           servidor = servertools.corregir_servidor(servidor)

                           url = servertools.normalize_url(servidor, url)

                           if servertools.is_server_available(servidor):
                               if not servertools.is_server_enabled(servidor): continue
                           else:
                               if not config.get_setting('developer_mode', default=False): continue

                           if url.startswith('//'): url = 'https:' + url

                           qlty = scrapertools.find_single_match(lin, "<strong class='quality'>(.*?)</strong>").replace('mp4', '').strip()

                           lang = scrapertools.find_single_match(lin, "<td>([^<]+)")

                           other = ''
                           if servidor == 'various': other = servertools.corregir_other(url)
                           elif servidor == 'directo':
                              if '/mega.' in url: other = 'Mega'
                              elif '/cybervynx.' in url: other = 'Cybervynx'

                           url = url.replace('/Smoothpre.', '/smoothpre.')

                           itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = '', url=url, 
                                                 language=IDIOMAS.get(lang, lang), quality=qlty, quality_num=puntuar_calidad(qlty), other=other ))


               continue  

        elif 'drive' in servidor: servidor = 'gvideo'

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        if url.startswith('//'): url = 'https:' + url

        qlty = scrapertools.find_single_match(lin, "<strong class='quality'>(.*?)</strong>").replace('mp4', '').strip()

        lang = scrapertools.find_single_match(lin, "<td>([^<]+)")

        other = ''
        if servidor == 'various': other = servertools.corregir_other(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = '', url=url, 
                              language=IDIOMAS.get(lang, lang), quality=qlty, quality_num=puntuar_calidad(qlty), other=other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['tscam', 'hdts', 'brscreener', 'dvdrip', 'hd720p', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.server == 'uptobox':
        return 'Servidor [COLOR goldenrod]Fuera de Servicio[/COLOR]'

    if item.url.startswith(host):
        if '/links/' in item.url:
            new_url = ''
            try:
                new_url = httptools.downloadpage(item.url, follow_redirects=False).headers['location']
            except: pass

        if new_url: url = new_url
        else:
            data = do_downloadpage(item.url)

            url = scrapertools.find_single_match(data, '<a id=.*?href="(.*?)"')

            if url:
                if 'url=' in url: url = scrapertools.find_single_match(url, 'url=(.*?)$')

                url = url.replace('&amp;', '&')

    if url:
        if '/uii.' in url:
            return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

        url = url.replace('/Smoothpre.', '/smoothpre.')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        if '/mega.' in url: servidor = 'mega'
        elif '/cybervynx.' in url: servidor = 'various'

        url = servertools.normalize_url(servidor, url)

        if servidor != 'directo':
            itemlist.append(item.clone(url=url, server=servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)<strong>Mega1Link</strong>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        article = scrapertools.decodeHtmlentities(article)

        url = scrapertools.find_single_match(article, ' href="(.*?)"')
        if not url: url = scrapertools.find_single_match(article, " href='(.*?)'")
        if not url: url = scrapertools.find_single_match(article, ' href=(.*?)>')

        title = scrapertools.find_single_match(article, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(article, ' data-src=(.*?) ')

        year = scrapertools.find_single_match(article, '<span class=year>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>.*?,(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(article, '<span>(.*?)</span>').strip()

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))

        if year: title = title = title.replace(' ' + year, '').replace(' (' + year + ')', '').strip()
        else: year = '-'

        PeliTitle = title

        if "Latino" in PeliTitle: PeliTitle = PeliTitle.split("Latino")[0]

        if "DVDrip" in PeliTitle: PeliTitle = PeliTitle.split("DVDrip")[0]
        if " HD " in PeliTitle: PeliTitle = PeliTitle.split(" HD ")[0]
        if " hd " in PeliTitle: PeliTitle = PeliTitle.split(" hd ")[0]

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=PeliTitle, infoLabels={'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=PeliTitle, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span class="current">.*?' + "<a href='(.*?)'")
        if not next_page: next_page = scrapertools.find_single_match(data, '<span class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_search', text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
