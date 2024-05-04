# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urlparse
else:
    import urllib.parse as urlparse


import re, time

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://wvv1.cuevana3.vip'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://cuevana3.law', 'https://pro.cuevana8.vip', 'https://cuevana8.vip',
             'https://cuevana8.online', 'https://cuevana.la', 'https://www.cuevana.la',
             'https://ww2.cuevana3.law']

domain = config.get_setting('dominio', 'cuevana3lw', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'cuevana3lw')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'cuevana3lw')
    else: host = domain


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'cuevana3lw', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_cuevana3lw', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='cuevana3lw', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_cuevana3lw', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + '/category/estrenos/', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catalogo', action = 'list_all', url = host + '/series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + '/category/series-de-estreno/', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data,'<ul class="wp-block-categories-list wp-block-categories">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque,'<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == 'Estrenos': continue
        elif title == 'Series de Estrenos': continue
        elif title == 'News': continue

        if item.search_type == 'movie':
            if title == 'Reality': continue
            elif title == 'Soap': continue
            elif title == 'Talk': continue

        if item.search_type == 'tvshow':
            if title == 'Película de TV': continue

        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( title = title, url = url, action = 'list_all', search_type = item.search_type, text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data,'(.*?)</main>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>').strip()

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#038;', '&')

        thumb = scrapertools.find_single_match(article, 'src="(.*?)"')

        thumb = 'https:' + thumb

        year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>')

        if year: title = title.replace('(' + year + ')' , '').strip()
        else: year ='-'

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            title = title.replace('Pelicula', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<nav class="navigation pagination">' in data:
            bloque_next = scrapertools.find_single_match(data, '<nav class="navigation pagination">(.*?)</nav>')
            next_page = scrapertools.find_single_match(bloque_next, '<a class="page-link current".*?</a>.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>episodios</h3>(.*?)</section>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>').strip()

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        thumb = scrapertools.find_single_match(article, 'src="(.*?)"')

        thumb = 'https:' + thumb

        season = scrapertools.find_single_match(article, '<span class="num-epi">(.*?)x').strip()
        if not season: season = 1

        episode = scrapertools.find_single_match(article, '<span class="num-epi">.*?x(.*?)</span>').strip()
        if not episode: episode = 1

        contentSerieName = scrapertools.find_single_match(title, '(.*?) \d')

        titulo = str(season) + 'x' + str(episode) + ' ' + title.replace(str(season) + 'x' + str(episode), '').strip()

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSerieName=contentSerieName, contentSeason = season, contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('data-season="(.*?)"', re.DOTALL).findall(data)

    for tempo in matches:
        tempo = tempo.strip()

        title = 'Temporada ' + tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action='episodios', title=title, page = 0, contentType='season', contentSeason=tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    d_post = scrapertools.find_single_match(data, 'data-post="(.*?)"')

    if not d_post: return itemlist

    post = {'action': 'action_select_season', 'season': str(item.contentSeason), 'post': d_post}

    data = do_downloadpage(host + '/wp-admin/admin-ajax.php', post = post)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Cuevana3Lw', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Lw', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Lw', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Lw', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Lw', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Cuevana3Lw', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        if thumb: thumb = 'https:' + thumb

        epis = scrapertools.find_single_match(match, '<span class="num-epi">.*?x(.*?)</span>')

        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        titulo = str(item.contentSeason) + 'x' + epis + ' ' + title.replace(str(item.contentSeason) + 'x' + epis, '').strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

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

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, 'href="#options-(.*?)</li>')

    ses = 0

    for match in matches:
        ses += 1

        opt = scrapertools.find_single_match(match, '(.*?)">')

        srv = scrapertools.find_single_match(match, '<span class="server">(.*?)-').strip()
        lng = scrapertools.find_single_match(match, '<span class="server">.*?-(.*?)</span>').strip()

        srv = srv.lower().strip()

        if 'youtube' in srv: continue

        if 'Latino' in lng: lang = 'Lat'
        elif 'Castellano' in lng or 'Español' in lng: lang = 'Esp'
        elif 'Subtitulado' in lng or 'VOSE' in lng: lang = 'Vose'
        elif 'Inglés' in lng: lang = 'Vo'
        else: lang = '?'

        servidor = servertools.corregir_servidor(srv)

        links = scrapertools.find_multiple_matches(data, '<div id="options-' + opt + '.*?<iframe.*?src="(.*?)"')

        if not links: continue

        for url in links:
            trembed = url.replace('&#038;', '&')

            data = do_downloadpage(trembed)

            vid = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
            if not vid: vid = scrapertools.find_single_match(data, '<IFRAME.*?SRC="([^"]+)')

            if vid:
                if vid.startswith('//'): vid = 'https:' + vid

                if '/play?' in vid or '/streamhd?' in vid:
                    vid = vid.replace('&amp;', '&')

                    data = do_downloadpage(vid)

                    vids = scrapertools.find_multiple_matches(data, 'data-video="(.*?)"')

                    if vids:
                        for url in vids:
                            ses += 1

                            if not url: continue

                            if '/hydrax.' in url: continue

                            servidor = servertools.get_server_from_url(url)
                            servidor = servertools.corregir_servidor(servidor)

                            url = servertools.normalize_url(servidor, url)

                            other = ''
                            if servidor == 'various': other = servertools.corregir_other(url)

                            if url.startswith('//'): url = 'https:' + url

                            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

                    embed = scrapertools.find_single_match(str(data), "sources:.*?'(.*?)'")

                    if embed:
                        ses += 1

                        if embed.startswith('//'): embed = 'https:' + embed

                        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = embed, language = lang ))

                else:
                    url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
                    if not url: url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="([^"]+)')

                    if url:
                        if '/hydrax.' in url: continue
                        elif '/media.esplay.one' in url: continue

                        servidor = servertools.get_server_from_url(url)
                        servidor = servertools.corregir_servidor(servidor)

                        url = servertools.normalize_url(servidor, url)

                        other = ''
                        if servidor == 'various': other = servertools.corregir_other(url)

                        if url.startswith('//'): url = 'https:' + url

                        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

            else:
                other = srv

                if servidor == srv: other = ''
                elif not servidor == 'directo':
                   if not servidor == 'various': other = ''

                if url.startswith('//'): url = 'https:' + url

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other.capitalize() ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&#038;', '&').replace('&amp;', '&')

    if not item.server:
        item.url = url

        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
        if not url: url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="([^"]+)')

        if not url: return itemlist

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

        return itemlist

    itemlist.append(item.clone(server = item.server, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
