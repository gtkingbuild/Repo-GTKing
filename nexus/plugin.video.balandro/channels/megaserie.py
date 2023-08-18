# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

from lib import decrypters


host = 'https://megaxserie.me/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_megaserie_proxies', default=''):
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
    if url.startswith(host):
        if not headers: headers = {'Referer': host}

    if '/release/' in url: raise_weberror = False

    timeout = None
    if host in url:
        if config.get_setting('channel_megaserie_proxies', default=''): timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
    else:
        data = httptools.downloadpage_proxy('megaserie', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

        if not data:
            if not '?s=' in url:
                platformtools.dialog_notification('MegaSerie', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')
                data = httptools.downloadpage_proxy('megaserie', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                else:
                    data = httptools.downloadpage_proxy('megaserie', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
        except:
            pass

    if '<title>Just a moment...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    elif '<title>Bot Verification</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] reCAPTCHA[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='megaserie', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_megaserie', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone ( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone ( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

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
        ('familia', 'Familiar'), 
        ('fantasia', 'Fantasía'),
        ('historia', 'Historia'), 
        ('kids', 'Infantil'),
        ('misterio', 'Misterio'),
        ('musica', 'Música'),
        ('pelicula-de-tv' ,'Película de TV'),
        ('reality', 'Reality'),
        ('romance', 'Romance'),
        ('sci-fi-fantasy' ,'Sci-Fi & Fantasy'),
        ('suspense', 'Suspense'),
        ('terror', 'Terror'),
        ('western', 'Western')
        ]

    if item.search_type == 'movie': 
        opciones.remove(('action-adventure','Action & Adventure'))
        opciones.remove(('kids','Infantil'))
        opciones.remove(('reality','Reality'))
        opciones.remove(('sci-fi-fantasy','Sci-Fi & Fantasy'))

    elif item.search_type == 'tvshow': 
        opciones.remove(('suspense','Suspense'))

    for opc, tit in opciones:
        url = host + opc
        if item.search_type == 'movie': url += '/?type=movies'
        else: url += '/?type=series'

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie': top_year = 1955
    else: top_year = 1998

    for x in range(current_year, top_year, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'release/' + str(x) + '/', action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '(.*?)<p>MegaxSerie')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>')

        if not url or not title: continue

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(article, '<span class="Qlty">([^<]+)</span>')

        langs = []
        if '/Spain.png' in article: langs.append('Esp')
        if '/Mexico.png' in article: langs.append('Lat')
        if '/United-States-Minor-Outlying.png' in article: langs.append('Vose')

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, languages=', '.join(langs), fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '>SIGUIENTE' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="([^"]+)')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('data-season="(.*?)"', re.DOTALL).findall(data)

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
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

    data_post = scrapertools.find_single_match(data, 'data-post="(.*?)"')

    if not data_post: return itemlist

    post = {'action': 'action_select_season', 'season': str(item.contentSeason), 'post': data_post}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

    patron = '<article.*?src="(.*?)".*?<span class="num-epi">(.*?)</span>.*?<h2 class="entry-title">(.*?)</h2>.*?<a href="(.*?)"'

    matches = scrapertools.find_multiple_matches(data, patron)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('MegaSerie', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MegaSerie', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MegaSerie', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MegaSerie', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MegaSerie', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('MegaSerie', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, temp_epis, title, url in matches[item.page * item.perpage:]:
        if not 'http' in thumb: thumb = 'https:' + thumb

        title = title.replace(temp_epis, '').strip()

        titulo = temp_epis + ' ' + title

        epis = scrapertools.find_single_match(temp_epis, '.*?x(.*?)$').strip()

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

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, 'href="#options-(.*?)".*?<span class="server">(.*?)</span>')

    ses = 0

    for opt, srv_lang in matches:
        ses += 1

        srv = scrapertools.find_single_match(srv_lang, '(.*?)-').lower().strip()

        if srv == 'hqq' or srv == 'waaw' or srv == 'netu': continue

        if not srv == 'descargaonline':
            if servertools.is_server_available(srv):
                if not servertools.is_server_enabled(srv): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

        lang = scrapertools.find_single_match(srv_lang, '.*?-(.*?)$').strip()

        url = scrapertools.find_single_match(data, '<div id="options-' + opt + '.*?src="(.*?)"')

        if srv == 'descargaonline':
            if '/acortar24.xyz/' in url:
                host_torrent = host[:-1]
                url_base64 = decrypters.decode_url_base64(url, host_torrent)

                if not url_base64.startswith(host):
                    new_url = httptools.downloadpage(url_base64, follow_redirects=False).headers.get('location', '')
                else:
                    new_url = httptools.downloadpage_proxy('megaserie', url_base64, follow_redirects=False).headers.get('location', '')

                if new_url:
                    data1 = do_downloadpage(new_url)

                    matches1 = scrapertools.find_multiple_matches(data1, '<a target=".*?href="(.*?)"')

                    for link in matches1:
                        if '/hqq' in link or '/waaw' in link or '/netu' in link: continue

                        servidor = servertools.get_server_from_url(link)
                        servidor = servertools.corregir_servidor(servidor)

                        if servidor != 'directo':
                            link = servertools.normalize_url(servidor, link)

                            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link, language = IDIOMAS.get(lang, lang)))

                    continue

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, language = IDIOMAS.get(lang, lang), other = srv ))

    # ~ Descargar
    matches = scrapertools.find_multiple_matches(data, '<td><span class="num">.*?</span>(.*?)</td>.*?<td>(.*?)</td>.*?<td><span>(.*?)</span>.*?href="(.*?)"')
    if not matches:
        matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">.*?</span>(.*?)</td>.*?<td>(.*?)</td>.*?<td><span>(.*?)<span>.*?href="(.*?)"')

    for srv, lang, qlty, url in matches:
        ses += 1

        srv = srv.replace(' &amp; ', '').lower().strip()

        if srv == 'hqq' or srv == 'waaw' or srv == 'netu': continue

        if not srv == 'descargaonline':
            if servertools.is_server_available(srv):
                if not servertools.is_server_enabled(srv): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

        if srv == 'descargaonline':
            if '/acortar24.xyz/' in url:
                host_torrent = host[:-1]
                url_base64 = decrypters.decode_url_base64(url, host_torrent)

                if not url_base64.startswith(host):
                    new_url = httptools.downloadpage(url_base64, follow_redirects=False).headers.get('location', '')
                else:
                    new_url = httptools.downloadpage_proxy('megaserie', url_base64, follow_redirects=False).headers.get('location', '')

                if new_url:
                    data2 = do_downloadpage(new_url)

                    matches2 = scrapertools.find_multiple_matches(data2, '<a target=".*?href="(.*?)"')

                    for link in matches2:
                        if '/hqq' in link or '/waaw' in link or '/netu' in link: continue

                        servidor = servertools.get_server_from_url(link)
                        servidor = servertools.corregir_servidor(servidor)

                        if servidor != 'directo':
                            link = servertools.normalize_url(servidor, link)

                            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link,
                                                  language = IDIOMAS.get(lang, lang), quality = qlty ))

                    continue

        if url:
            lang = lang.strip()

            other = 'D ' + srv

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, language = IDIOMAS.get(lang, lang), other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    if item.server != 'directo':
        itemlist.append(item.clone( url = url, server = item.server ))

        return itemlist

    if url.startswith(host):
        data = do_downloadpage(url)

        url = scrapertools.find_single_match(data, 'src="(.*?)"')

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor != 'directo':
                itemlist.append(item.clone( url = url, server = servidor ))

            return itemlist

    else:
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(url, host_torrent)

        if not url_base64.startswith(host):
            url = httptools.downloadpage(url_base64, follow_redirects=False).headers.get('location', '')
        else:
            url = httptools.downloadpage_proxy('megaserie', url_base64, follow_redirects=False).headers.get('location', '')

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor != 'directo':
                itemlist.append(item.clone( url = url, server = servidor ))

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
