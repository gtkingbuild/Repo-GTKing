# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.1gnula.top/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_gnulatop_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar ...[/B]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/release/' in url: raise_weberror = False

    if not headers: headers = {'Referer': host}

    hay_proxies = False
    if config.get_setting('channel_gnulatop_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('gnulatop', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

        if not data:
            if not '/?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('GnulaTop', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('gnulatop', url, post=post, headers=headers, raise_weberror=raise_weberror).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='gnulatop', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genero/estrenos/', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ratings/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'gennero/estrenos/', search_type = 'tvshow', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ratings/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>GÉNEROS<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?>(.*?)</a>')

    for url, title in matches:
        if config.get_setting('descartar_anime', default=False):
            if title == 'Anime': continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = text_color ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1969, -1):
        url = host + 'release/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', text_color = 'deepskyblue' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    productoras = [
        ('abc', 'ABC'),
        ('adult-swim', 'Adult Swim'),
        ('amazon', 'Amazon'),
        ('apple-tv', 'Apple TV+'),
        ('broadcast-syndication', 'Broadcast Syndication'),
        ('bs11', 'BS11'),
        ('cbs', 'Cbs'),
        ('cartoon-network', 'Cartoon Network'),
        ('comedy-central', 'Comedy Central'),
        ('dc-universe', 'DC Universe'),
        ('disney-channel', 'Disney Channel'),
        ('disney-xd', 'Disney XD'),
        ('fbs', 'FBS'),
        ('fox', 'FOX'),
        ('fuji-tv', 'Fuji TV'),
        ('fx', 'FX'),
        ('fxx', 'FXX'),
        ('htb', 'HTB'),
        ('hulu', 'Hulu'),
        ('itv', 'ITV'),
        ('mbs', 'MBS'),
        ('nbc', 'NBC'),
        ('netflix', 'Netflix'),
        ('nhk', 'NHK'),
        ('nickelodeon', 'Nickelodeon'),
        ('syndication', 'Syndication'),
        ('telefe', 'Telefe'),
        ('tf1', 'TF1'),
        ('the-cw', 'The CW'),
        ('the-wb', 'The WB'),
        ('tokyo-mx', 'Tokyo MX'),
        ('tv-asahi', 'Tv Asahi'),
        ('upn', 'UPN')
        ]

    for opc, tit in productoras:
        url = host + 'network/' + opc + '/'

        itemlist.append(item.clone( title = tit, action = 'list_all', url = url, text_color = 'hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if 'Añadido recientemente' in data:
        bloque = scrapertools.find_single_match(data, 'Añadido recientemente(.*?)<div class="copy">')
    else:
        bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        if ('|') in title:
            title = title.split("|")[0]
            title = title.strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="imdb".*?</span>.*?<span>(.*?)</span>')
        if not year:
            year = scrapertools.find_single_match(match, 'class="local-link".*?</h3>.*?<span>(.*?)</span>')
            if year: year = scrapertools.find_single_match(year, ',(.*?)$').strip()

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        title = title.replace('&#8230;', '').replace('&#8211;', '')

        langs = []
        if '/flags/es.png' in match: langs.append('Esp')
        if '/flags/mx.png' in match: langs.append('Lat')
        if '/flags/en.png' in match: langs.append('Vose')

        if 'ver-pelicula/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = ', '.join(langs),
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<span class="current">' in data:
            patron = '<span class="current">.*?'
            patron += "href='(.*?)'"

            next_page = scrapertools.find_single_match(data, patron)

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    seasons = scrapertools.find_multiple_matches(data, "<span class='title'>(.*?)<i>")

    for title in seasons:
        title = title.strip()
        tempo = title.replace('Temporada ', '').strip()

        if len(seasons) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = item.url, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    bloque = scrapertools.find_single_match(data, "<div class='se-q'>.*?<span class='title'>" + str(item.title) + "(.*?)</div></div>")
    if not bloque: bloque = scrapertools.find_single_match(data, "<div class='se-q'>.*?<span class='title'>Temporada(.*?)</div></div>")

    patron = "<div class='imagen'.*?data-id='(.*?)'.*?src='(.*?)'.*?<div class='numerando'(.*?)</div>.*?<a href='(.*?)'.*?>(.*?)</a>.*?</span>(.*?)</div></li>"

    episodes = scrapertools.find_multiple_matches(bloque, patron)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(episodes)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('GnulaTop', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('GnulaTop', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('GnulaTop', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('GnulaTop', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('GnulaTop', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('GnulaTop', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for data_id, thumb, temp_epis, url, title, idiomas in episodes[item.page * item.perpage:]:
        langs = []
        if 'title="Español"' in idiomas: langs.append('Esp')
        if 'title="Latino"' in idiomas: langs.append('Lat')
        if 'title="Subtitulado"' in idiomas: langs.append('Vose')
        if 'title="Ingles"' in idiomas: langs.append('VO')

        epis = scrapertools.find_single_match(temp_epis, ".*?-(.*?)$").strip()

        titulo = str(item.contentSeason) + 'x' + epis + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, languages = ', '.join(langs),
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

    logger.info()
    itemlist = []

    IDIOMAS = {'mx': 'Lat', 'es': 'Esp', 'en': 'Vose', 'jp': 'Vose'}

    data = do_downloadpage(item.url)

    # embeds
    matches = scrapertools.find_multiple_matches(data, "<li id='player-option-(.*?)</li>")

    ses = 0

    for match in matches:
        ses += 1

        servidor = scrapertools.find_single_match(match, "<span class='title'>(.*?)</span>").lower()

        if not servidor: continue

        if 'trailer' in servidor: continue

        if 'hqq.' in servidor: servidor = 'waaw'

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        lang = scrapertools.find_single_match(match, " src='.*?/flags/(.*?).png'")

        dpost = scrapertools.find_single_match(match, " data-post='(.*?)'")
        dnume = scrapertools.find_single_match(match, " data-nume='(.*?)'")

        if not dpost or not dnume: continue

        other = servertools.corregir_other(servidor)

        servidor = servertools.corregir_servidor(servidor)

        if not servidor == 'directo':
            if not servidor == 'various': other = ''

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, dpost = dpost, dnume = dnume, language = IDIOMAS.get(lang, lang), other = other ))

    # enlaces
    matches = scrapertools.find_multiple_matches(data, "<tr id='link-'(.*?)</tr>")

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, "<a href='(.*?)'")
        if not url: url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if '/hqq.' in url: servidor = 'waaw'

        if servidor == 'directo': continue

        url = servertools.normalize_url(servidor, url)

        qlty = scrapertools.find_single_match(match, "<strong class='quality'>(.*?)</strong>")

        lang = scrapertools.find_single_match(match, " src='.*?/flags/(.*?).png'")

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = IDIOMAS.get(lang, lang), quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if not url:
        post = {'action': 'doo_player_ajax', 'post': item.dpost, 'nume': item.dnume, 'type': 'movie'}
        headers = {"Referer": item.url}

        data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)

        url = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        url = url.replace('\\/', '/')

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1>Resultados encontrados(.*?)<div class="copy">')

    matches = scrapertools.find_multiple_matches(bloque, '<article>(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')

        title = scrapertools.find_single_match(article, ' alt="(.*?)"')

        if ('|') in title:
            title = title.split("|")[0]
            title = title.strip()

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')

        year = scrapertools.find_single_match(article, '<span class="year">(\d{4})</span>')
        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        title = title.replace('&#8230;', '').replace('&#8211;', '')

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="contenido"><p>(.*?)</p>'))

        langs = []
        if '/flags/es.png' in article: langs.append('Esp')
        if '/flags/mx.png' in article: langs.append('Lat')
        if '/flags/en.png' in article: langs.append('Vose')

        tipo = 'movie' if '/ver-pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = ', '.join(langs), fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

