# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://metroseries.net/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://seriesmetro.com/', 'https://seriesmetro.net/']

domain = config.get_setting('dominio', 'seriesmetro', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'seriesmetro')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'seriesmetro')
    else: host = domain


perpage = 30


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'seriesmetro', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_seriesmetro', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='seriesmetro', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_seriesmetro', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    platformtools.itemlist_refresh()

    return itemlist


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action ='list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + 'ultimos-capitulos/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
        ('accion', 'Acción'),
        ('action-adventure', 'Action & Adventure'),
        ('aventura', 'Aventura'),
        ('animacion', 'Animación'),
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
        ('romance', 'Romance'),
        ('sci-fi-fantasy', 'Sci-Fi & Fantasy'),
        ('talk', 'Talk'),
        ('terror', 'Terror'),
        ('war-politics', 'War & Politics'),
        ('western', 'Western')
        ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url=host + 'ver/' + opc + '/', action='list_all', text_color = 'hotpink' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        itemlist.append(item.clone ( title = letra, url = host + 'letter/%s/' % (letra.replace('#', '0-9')), action = 'list_all', text_color = 'hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '</main>' in data: data = data.split('</main>')[0]
    elif '<aside class="sidebar"' in data: data = data.split('<aside class="sidebar"')[0]

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)" class="lnk-blk"')
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(article, '<span class="date">(\d+)</span>')
        if not year: year = '-'

        plot = scrapertools.find_single_match(article, '<p><p>(.*?)</p>')
        plot = scrapertools.htmlclean(plot)

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                    contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><i class="fa-arrow-right">')

        if next_page:
            itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Últimos Capítulos<(.*?)>Series Recomendadas<')

    matches = scrapertools.find_multiple_matches(bloque, '<article (.*?)</article>')

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')
        title = scrapertools.find_single_match(article, '<span class="tvshow">(.*?)</span>').strip()

        season, episode = scrapertools.find_single_match(article, '<span class="tv-num">T(.*?)E(.*?)</span>')

        season = season.strip()
        episode = episode.strip()

        if not title or not url or not season or not episode: continue

        if len(season) == 2:
            if season.startswith('0'):
                season = season.replace('0', '')

        if len(episode) == 2:
            if episode.startswith('0'):
                episode = episode.replace('0', '')

        title = title.replace(season + 'x' + episode, '').strip()

        thumb = scrapertools.find_single_match(article, '<noscript>.*?<img src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(article, 'data-lazy-src="(.*?)"')

        if thumb.startswith('//'): thumb = 'https:' + thumb

        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail = thumb,
                                    contentType='episode', contentSerieName=title, contentSeason=season, contentEpisodeNumber=episode, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page = item.page + 1, action='last_epis', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<nav class="navigation pagination".*?class="page-numbers current">.*?href="([^"]+)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone (url = next_page, page = 0, title = 'Siguientes ...', action = 'last_epis', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    dobject = scrapertools.find_single_match(data, 'data-object ="(.*?)"')

    if not dobject: return itemlist

    matches = scrapertools.find_multiple_matches(data, '<li class="sel-temp"><a data-post="([^"]+)" data-season="([^"]+)')

    for dpost, tempo in matches:
        title = 'Temporada ' + '0' + tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.dobject = dobject
            item.dpost = dpost
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, dobject = dobject, dpost = dpost,
                                    contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda x: x.title)


# limitar episodios a mostrar y no hacer paginación automàtica (excepto para preferidos)
def episodios(item): 
    logger.info()
    itemlist = []

    tab_epis = []

    if not item.dobject or not item.dpost: return itemlist

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    post = {'action': 'action_select_season', 'post': item.dpost, 'object': item.dobject, 'season': item.contentSeason}
    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post)

    tot_pages = scrapertools.find_single_match(data, '<a class="page-numbers" href=".*?>(.*?)</a>')

    if not tot_pages:
        matches = scrapertools.find_multiple_matches(data, '<li><a href="([^"]+)"[^>]*>([^<]+)')

        if item.page == 0 and item.perpage == 50:
            sum_parts = len(matches)

            try:
                tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
                if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
            except: tvdb_id = ''

            if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
            elif tvdb_id:
                if sum_parts > 50:
                    platformtools.dialog_notification('SeriesMetro', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
            else:
                item.perpage = sum_parts

                if sum_parts >= 1000:
                    if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                        platformtools.dialog_notification('SeriesMetro', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                        item.perpage = 500

                elif sum_parts >= 500:
                    if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                        platformtools.dialog_notification('SeriesMetro', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                        item.perpage = 250

                elif sum_parts >= 250:
                    if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                        platformtools.dialog_notification('SeriesMetro', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                        item.perpage = 125

                elif sum_parts >= 125:
                    if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                        platformtools.dialog_notification('SeriesMetro', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                        item.perpage = 75

                elif sum_parts > 50:
                    if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                        platformtools.dialog_notification('SeriesMetro', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                        item.perpage = sum_parts
                    else: item.perpage = 50

        for url, title in matches[item.page * item.perpage:]:
            s_e = scrapertools.find_single_match(title, '(\d+)(?:x|X)(\d+)')

            if not s_e: continue

            season = int(s_e[0])
            episode = int(s_e[1])

            ord_epis = str(episode)

            if len(str(ord_epis)) == 1: ord_epis = '0000' + ord_epis
            elif len(str(ord_epis)) == 2: ord_epis = '000' + ord_epis
            elif len(str(ord_epis)) == 3: ord_epis = '00' + ord_epis

            tab_epis.append([ord_epis, url, title, season, episode])

        if tab_epis:
            tab_epis = sorted(tab_epis, key=lambda x: x[0])

            for orden, url, tit, ses, epi in tab_epis:
                 tit = tit + ' ' + item.contentSerieName

                 itemlist.append(item.clone( action = 'findvideos', url = url, title = tit, contentType = 'episode',
                                             contentSeason = item.contentSeason, contentEpisodeNumber = epi ))

        tmdb.set_infoLabels(itemlist)

        return itemlist

    try:
       pages = int(tot_pages)
       if pages > 2: platformtools.dialog_notification('SeriesMetro', '[COLOR blue]Cargando episodios[/COLOR]')
    except:
       pages = 12

    for i in range(pages):
        matches = scrapertools.find_multiple_matches(data, '<li><a href="([^"]+)"[^>]*>([^<]+)')

        for url, title in matches:
            s_e = scrapertools.find_single_match(title, '(\d+)(?:x|X)(\d+)')

            if not s_e: continue

            season = int(s_e[0])
            episode = int(s_e[1])

            ord_epis = str(episode)

            if len(str(ord_epis)) == 1: ord_epis = '0000' + ord_epis
            elif len(str(ord_epis)) == 2: ord_epis = '000' + ord_epis
            elif len(str(ord_epis)) == 3: ord_epis = '00' + ord_epis

            tab_epis.append([ord_epis, url, title, season, episode])

        if pages > 0:
            next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="[^"]*page/(\d+)/')

            if next_page:
                post = {'action': 'action_pagination_ep', 'object': item.dobject, 'season': item.contentSeason, 'page': next_page}
                data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post)
            else:
                break

    if tab_epis:
        tab_epis = sorted(tab_epis, key=lambda x: x[0])

        for orden, url, tit, ses, epi in tab_epis:
            tit = tit.replace('"', '').strip()

            itemlist.append(item.clone( action = 'findvideos', url = url, title = tit, contentType = 'episode', contentSeason = ses, contentEpisodeNumber = epi ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {
      'Español Latino': 'Lat',
      'Latino': 'Lat',
      'Español Castellano': 'Esp',
      'Español': 'Esp',
      'Sub Latino': 'Vose',
      'Sub Español': 'Vose',
      'Sub': 'Vose',
      'Ingles':'VO'
      }

    data = do_downloadpage(item.url)

    dterm = scrapertools.find_single_match(data, ' data-term="([^"]+)')
    if not dterm: return itemlist

    matches = scrapertools.find_multiple_matches(data, '<a data-opt="([^"]+)".*?<span class="option">(?:Cload|CinemaUpload) - ([^<]*)')

    for dopt, lang in matches:
        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', dterm = dterm, dopt = dopt, url = item.url, language = IDIOMAS.get(lang, lang) ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    post = {'action': 'action_player_series', 'term_id': item.dterm, 'ide': item.dopt}
    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post, raise_weberror=False)

    url = scrapertools.find_single_match(data, '(?i)<iframe[^>]* src="([^"]+)')
    if not url: return itemlist

    url = url.replace('&#038;', '&')

    data = do_downloadpage(url, headers={'Referer': item.url}, raise_weberror=False)

    url = scrapertools.find_single_match(data, '(?i)<iframe[^>]* src="([^"]+)')
    if not url: return itemlist

    if '/cinemaupload.com/' in url:
        url = url.replace('/cinemaupload.com/', '/embed.cload.video/')

    if 'embed.cload' in url:
        data = do_downloadpage(url, headers={'Referer': host}, raise_weberror=False)

        if '<div class="g-recaptcha"' in data or 'Solo los humanos pueden ver' in data:
            headers = {'Referer': host, 'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)'}
            data = do_downloadpage(item.url, headers=headers, raise_weberror=False)

            new_url = scrapertools.find_single_match(data, '<div id="option-players".*?src="([^"]+)"')
            if new_url:
                new_url = new_url.replace('/cinemaupload.com/', '/embed.cload.video/')
                data = do_downloadpage(new_url, raise_weberror=False)

        url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')

        if url:
            if '/download/' in url:
                url = url.replace('//download/', '/files/').replace('/download/', '/files/')
                itemlist.append(item.clone( url = url, server = 'directo' ))
                return itemlist

            elif '/manifest.mpd' in url:
                if platformtools.is_mpd_enabled():
                    itemlist.append(['mpd', url, 0, '', True])
                itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
            else:
                itemlist.append(['m3u8', url])

    else:
        if 'dailymotion' in url: url = 'https://www.dailymotion.com/' + url.split('/')[-1]

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)

            itemlist.append(item.clone( url=url, server=servidor ))

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
