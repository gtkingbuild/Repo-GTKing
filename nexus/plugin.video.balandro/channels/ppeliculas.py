# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.pepeliculas.org/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_ppeliculas_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('ppeliculas', url, post=post, headers=headers).data

    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
                data = httptools.downloadpage_proxy('ppeliculas', url, post=post, headers=headers).data
        except:
            pass

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genre/estreno/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = host + 'pelicula/', group = 'destacadas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_top', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + 'episodios/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = host + 'series/', group = 'destacadas', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_top', url = host, search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('accion', 'Acción'),
       ('action-adventure', 'Action & Adventure'),
       ('animacion', 'Animación'),
       ('aventura', 'Aventura'),
       ('ciencia-ficcion', 'Ciencia ficción'),
       ('comedia', 'Comedia'),
       ('comedy', 'Comedy'),
       ('crimen', 'Crimen'),
       ('documental', 'Documental'),
       ('drama', 'Drama'),
       ('familia', 'Familia'),
       ('fantasia', 'Fantasía'),
       ('guerra', 'Guerra'),
       ('historia', 'Historia'),
       ('history', 'History'),
       ('misterio', 'Misterio'),
       ('mystery', 'Mystery'),
       ('musica', 'Música'),
       ('romance', 'Romance'),
       ('sci-fi-fantasy', 'Sci-Fi & Fantasy'),
       ('suspense', 'Suspense'),
       ('terror', 'Terror'),
       ('thriller', 'Thriller'),
       ('war', 'War'),
       ('western', 'Western')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'genre/' + opc + '/', action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if item.group == 'destacadas':
        blk = 'destacadas</h2(.*?)recientemente</h2'
    else:
        blk = 'recientemente</h2(.*?)<div class="pagination">'

    bloque = scrapertools.find_single_match(data, blk)

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        qlty = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>')

        year = scrapertools.find_single_match(match, '</h3>.*?<span>(.*?)</span>')
        if year:
            if not len(year) == 4:
                try:
                   year = year.split(',')[1]
                   year = year.strip()
                except:
                   year = ''

        if not year: year = '-'

        if '/pelicula/' in url:
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if not item.group == 'destacadas':
            next_page = scrapertools.find_single_match(data, "<div class='resppages'>" + '.*?</a><a href="(.*?)".*?><span')
            if not next_page: next_page = scrapertools.find_single_match(data, "<div class='resppages'>" + '<a href="(.*?)".*?><span')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone(title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral'))

    return itemlist


def list_top(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if item.search_type == 'movie':
        blk = '<h3>TOP Movies(.*?)<h3>TOP Series'
    else:
        blk = '<h3>TOP Series(.*?)</div></div></div>'

    bloque = scrapertools.find_single_match(data, blk)

    matches = scrapertools.find_multiple_matches(bloque, "<div class='top-imdb-item'(.*?)<div class='puesto'>")

    for match in matches:
        url = scrapertools.find_single_match(match, "<a href='(.*?)'")

        title = scrapertools.find_single_match(match, "alt='(.*?)'")

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, "src='(.*?)'")

        if '/pelicula/' in url:
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'recientemente</h2(.*?)</a></div></div>')

    i = 0

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        s_e = scrapertools.get_season_and_episode(url)

        try:
           season = int(s_e.split("x")[0])
           epis = s_e.split("x")[1]
        except:
           i += 1
           season = 0
           epis = i

        title = title.replace('Online', '').replace('Sub Español', 'Vose').strip()

        if ':' in title: SerieName = scrapertools.find_single_match(title, '(.*?):').strip()
        elif ' (' in title: SerieName = title.split(" (")[0]
        else: SerieName = title

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentSerieName = SerieName, contentType='episode', contentSeason=season, contentEpisodeNumber=epis ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<div class='resppages'>" + '.*?</a><a href="(.*?)".*?><span')
        if not next_page: next_page = scrapertools.find_single_match(data, "<div class='resppages'>" + '<a href="(.*?)".*?><span')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone(title = 'Siguientes ...', url = next_page, action = 'last_epis', text_color = 'coral'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<span class='se-t.*?'>(.*?)</span>")

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = numtempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + "</span>(.*?)</div></li></ul></div></div>")

    patron = "<li class='mark-(.*?)'>.*?<img src='(.*?)'.*?<a href='(.*?)'>(.*?)</a>"

    matches = scrapertools.find_multiple_matches(bloque, patron)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Ppeliculas', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Ppeliculas', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Ppeliculas', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Ppeliculas', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Ppeliculas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for episode, thumb, url, title in matches[item.page * item.perpage:]:
        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason , contentEpisodeNumber = episode ))

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

    # ~ torrents No se tratan dan error  https://www.pepeliculas.org/link/361535-zypzvbie5v/   13/10/2022

    data = do_downloadpage(item.url)

    patron = "<li id='player-option-.*?"
    patron += "data-post='(.*?)'.*?data-type='(.*?)'.*?data-nume='(.*?)'.*?<span class='title'>(.*?)</span>.*?<span class='server'>(.*?)</span>"

    matches = scrapertools.find_multiple_matches(data, patron)

    ses = 0

    # ~ orden post

    for _post, _type, _nume, qlty_lang, _server in matches:
        ses += 1

        url = host + 'wp-json/dooplayer/v2/%s/%s/%s'  %  (_post, _type, _nume)

        if 'Latino' in qlty_lang:
            qlty = qlty_lang.replace('Latino', '').strip()
            lang = 'Lat'
        elif 'Castellano' in qlty_lang or 'Español' in qlty_lang:
            qlty = qlty_lang.replace('Castellano', '').strip()
            lang = 'Esp'
        elif 'Subtitulado' in qlty_lang or 'VOSE' in qlty_lang:
            qlty = qlty_lang.replace('Subtitulado', '').strip()
            lang = 'Vose'
        else:
            qlty = qlty_lang
            lang = '?'

        other = _server.lower()
        other = other.replace('.com', '').replace('.org', '').replace('.co', '').replace('.cc', '').replace('.net', '').replace('.to', '')
        other = other.replace('.ru', '').replace('.tv', '').replace('my.', '').replace('.info', '').replace('.re', '').replace('.xx', '')
        other = other.replace('v2.', '').replace('.veoh', '').replace('.sh', '').replace('.nz', '').replace('.site', '').strip()

        if 'youtube' in other: continue

        elif 'waaw' in other or 'hqq' in other or 'netu' in other: continue

        elif 'powvideo' in other or 'pomvideo' in other: continue

        elif 'openload' in other: continue
        elif 'streamplay' in other: continue
        elif 'rapidvideo' in other: continue
        elif 'streamango' in other: continue
        elif 'verystream' in other: continue
        elif 'vidtodo' in other: continue
        elif 'stormo' in other: continue
        elif 'streamcherry' in other: continue
        elif 'biter' in other: continue

        elif 'pepeliculas' in other: continue

        elif 'uploaded' in other: continue
        elif 'earn4files' in other: continue
        elif 'uploadrive' in other: continue
        elif 'uploadbuzz' in other: continue
        elif 'mediafire' in other: continue
        elif 'drive.google' in other: continue
        elif 'fileflares' in other: continue

        if other == qlty: qlty = ''

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', url = url, ref = item.url,
                                                      other = other.capitalize(), language = lang, quality = qlty ))

    # ~ orden type

    patron = "<li id='player-option-.*?"
    patron += "data-type='(.*?)'.*?data-post='(.*?)'.*?data-nume='(.*?)'.*?<span class='title'>(.*?)</span>.*?<span class='server'>(.*?)</span>"

    matches = scrapertools.find_multiple_matches(data, patron)

    for _type, _post, _nume, qlty_lang, _server in matches:
        ses += 1

        url = host + 'wp-json/dooplayer/v2/%s/%s/%s'  %  (_post, _type, _nume)

        if 'Latino' in qlty_lang:
            qlty = qlty_lang.replace('Latino', '').strip()
            lang = 'Lat'
        elif 'Castellano' in qlty_lang or 'Español' in qlty_lang:
            qlty = qlty_lang.replace('Castellano', '').strip()
            lang = 'Esp'
        elif 'Subtitulado' in qlty_lang or 'VOSE' in qlty_lang:
            qlty = qlty_lang.replace('Subtitulado', '').strip()
            lang = 'Vose'
        else:
            qlty = qlty_lang
            lang = '?'

        other = _server.lower()
        other = other.replace('.com', '').replace('.org', '').replace('.co', '').replace('.cc', '').replace('.net', '').replace('.to', '')
        other = other.replace('.ru', '').replace('.tv', '').replace('my.', '').replace('.info', '').replace('.re', '').replace('.sx', '')
        other = other.replace('v2.', '').replace('.veoh', '').replace('.sh', '').replace('.nz', '').replace('.site', '').strip()

        if 'youtube' in other: continue

        elif 'waaw' in other or 'hqq' in other or 'netu' in other: continue

        elif 'powvideo' in other or 'pomvideo' in other: continue

        elif 'openload' in other: continue
        elif 'streamplay' in other: continue
        elif 'rapidvideo' in other: continue
        elif 'streamango' in other: continue
        elif 'verystream' in other: continue
        elif 'vidtodo' in other: continue
        elif 'stormo' in other: continue
        elif 'streamcherry' in other: continue
        elif 'biter' in other: continue

        elif 'pepeliculas' in other: continue

        elif 'uploaded' in other: continue
        elif 'earn4files' in other: continue
        elif 'uploadrive' in other: continue
        elif 'uploadbuzz' in other: continue
        elif 'mediafire' in other: continue
        elif 'drive.google' in other: continue
        elif 'fileflares' in other: continue

        if other == qlty: qlty = ''

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', url = url, ref = item.url,
                                                      other = other.capitalize(), language = lang, quality = qlty ))

    # ~ Ver

    if 'Ver en línea' in data: 
        patron = "<tr id='link-.*?<img src=.*?"
        patron += "domain=(.*?)'>.*?<a href='(.*?)'.*?target='_blank'>(.*?)</a>.*?<strong class='quality'>(.*?)</strong>.*?</td><td>(.*?)</td>"

        matches = scrapertools.find_multiple_matches(data, patron)

        for domain, url, tipo, qlty, lang in matches:
            ses += 1

            if not tipo == 'Ver en línea': continue

            servidor = domain.lower()
            servidor = servidor.replace('.com', '').replace('.co', '').replace('.cc', '').replace('.net', '').replace('.to', '')
            servidor = servidor.replace('.ru', '').replace('.tv', '').replace('my.', '').replace('.info', '').replace('.re', '').replace('.sx', '')
            servidor = servidor.replace('v2.', '').replace('.veoh', '').replace('.sh', '').replace('.nz', '').replace('.site', '').strip()

            servidor = servertools.corregir_servidor(servidor)

            if 'waaw' in servidor or  'hqq' in servidor or 'netu' in servidor: continue

            elif 'powvideo' in servidor or 'pomvideo' in servidor: continue

            elif 'openload' in servidor: continue
            elif 'streamplay' in servidor: continue
            elif 'rapidvideo' in servidor: continue
            elif 'streamango' in servidor: continue
            elif 'verystream' in servidor: continue
            elif 'vidtodo' in servidor: continue
            elif 'stormo' in servidor: continue
            elif 'streamcherry' in servidor: continue
            elif 'biter' in servidor: continue

            elif 'pepeliculas' in servidor: continue

            elif 'uploaded' in servidor: continue
            elif 'earn4files' in servidor: continue
            elif 'uploadrive' in servidor: continue
            elif 'uploadbuzz' in servidor: continue
            elif 'mediafire' in servidor: continue
            elif 'drive.google' in servidor: continue

            if lang == 'Latino': lang = 'Lat'
            elif lang == 'Castellano' or lang == 'Español': lang = 'Esp'
            elif lang == 'Subtitulado' or lang == 'VOSE': lang = 'Vose'
            else: lang = '?'

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, ref = item.url,
                                                          other = 'v', language = lang, quality = qlty ))

    # ~ Descargas

    if 'Descarga' in data:
        patron = "<tr id='link-.*?<img src=.*?"
        patron += "domain=(.*?)'>.*?<a href='(.*?)'.*?target='_blank'>(.*?)</a>.*?<strong class='quality'>(.*?)</strong>.*?</td><td>(.*?)</td>"

        matches = scrapertools.find_multiple_matches(data, patron)

        for domain, url, tipo, qlty, lang in matches:
            ses += 1

            if not tipo == 'Descarga': continue

            servidor = domain.lower()
            servidor = servidor.replace('.com', '').replace('.org', '').replace('.co', '').replace('.cc', '').replace('.net', '').replace('.to', '')
            servidor = servidor.replace('.ru', '').replace('.tv', '').replace('my.', '').replace('.info', '').replace('.re', '').replace('.sx', '')
            servidor = servidor.replace('v2.', '').replace('.veoh', '').replace('.sh', '').replace('.nz', '').replace('.site', '').strip()

            servidor = servertools.corregir_servidor(servidor)

            if 'waaw' in servidor or 'hqq' in servidor or 'netu' in servidor: continue

            elif 'powvideo' in servidor or 'pomvideo' in servidor: continue

            elif 'openload' in servidor: continue
            elif 'streamplay' in servidor: continue
            elif 'rapidvideo' in servidor: continue
            elif 'streamango' in servidor: continue
            elif 'verystream' in servidor: continue
            elif 'vidtodo' in servidor: continue
            elif 'stormo' in servidor: continue
            elif 'streamcherry' in servidor: continue
            elif 'biter' in servidor: continue

            elif 'pepeliculas' in servidor: continue

            elif 'uploaded' in servidor: continue
            elif 'earn4files' in servidor: continue
            elif 'uploadrive' in servidor: continue
            elif 'uploadbuzz' in servidor: continue
            elif 'mediafire' in servidor: continue
            elif 'drive.google' in servidor: continue

            elif '1fichier' in servidor: continue
            elif 'ddownload' in servidor: continue
            elif 'fastclick' in servidor: continue
            elif 'nitro.download' in servidor: continue
            elif 'multiup' in servidor: continue
            elif 'fileflares' in servidor: continue

            if servidor == 'filemoon': servidor = 'various'

            if lang == 'Latino': lang = 'Lat'
            elif lang == 'Castellano' or lang == 'Español': lang = 'Esp'
            elif lang == 'Subtitulado' or lang == 'VOSE': lang = 'Vose'
            else: lang = '?'

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, ref = item.url,
                                                          other = 'd', language = lang, quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.other == 'v' or item.other == 'd':
        resp = httptools.downloadpage_proxy('ppeliculas', item.url, follow_redirects=False)
        if 'location' in resp.headers: url = resp.headers['location']

    else:
        data = do_downloadpage(item.url, headers = {'Referer': item.ref})

        url = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        url = url.replace('\\/', '/')

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        if url.startswith('//'): url = 'https:' + url

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'zplayer': url = url + '|' + host

        itemlist.append(item.clone( url=url, server=servidor))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article>(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(match, '<p>(.*?)</p>'))

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
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
