# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3: PY3 = False
else: PY3 = True


import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seriespapaya.club/'


# ~ 23/5/2022 Solo funciona TODO en k19 el resto hay enlaces que si y otros que no

notification_d_ok = config.get_setting('notification_d_ok', default=True)

color_adver = config.get_setting('notification_adver_color', default='violet')


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_seriespapayaxyz_proxies', default=''):
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
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://seriespapaya.xyz/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not headers: headers = {'Referer': host, 'Connection': 'keep-alive'}

    if '&years%5B%5D=' in url: raise_weberror=False

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        data = httptools.downloadpage_proxy('seriespapayaxyz', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                else:
                    data = httptools.downloadpage_proxy('seriespapayaxyz', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        except:
            pass

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='seriespapayaxyz', folder=False, text_color='chartreuse' ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series-2/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    opciones = [
        ('Acción', 'accion'),
        ('Aventura', 'aventura'),
        ('Animación', 'animacion'),
        ('Bélica', 'belica'),
        ('Comedia', 'comedia'),
        ('Crimen', 'crimen'),
        ('Documental', 'documental'),
        ('Drama', 'drama'),
        ('Familia', 'familia'),
        ('Fantasía', 'fantasia'),
        ('Historia', 'historia'),
        ('Kids', 'kids'),
        ('Música', 'musica'),
        ('Misterio', 'misterio'),
        ('Reality', 'reality'),
        ('Romance', 'romance'),
        ('Suspense', 'suspense'),
        ('Western', 'western')
        ]


    for tit, opc in opciones:
        url = host + 'category/' + opc + '/'

        itemlist.append(item.clone( title = tit, action = 'list_all', url = url, text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'tvshow': tope = 1999
    else: tope = 1999

    for x in range(current_year, tope, -1):
        url = host + '?s=trfilter&trfilter=1&years%5B%5D=' + str(x)

        if item.search_type == 'tvshow': url = url + '&tr_post_type=2'
        else: url = url + '&tr_post_type=1'

        itemlist.append(item.clone( title = str(x), action = 'list_all', url = url, text_color = text_color ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    for letra in '0ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        title = '0-9' if letra == '0' else letra

        url = host + 'letter/' + title  + '/'

        itemlist.append(item.clone( action='por_letra', title = title, url = url, text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = 'class="TPost C">.*?<a href="([^"]+)".*?src="([^"]+)".*?class="Title">([^<]+)</h3>.*?<span class="Year">([^<]+)</span>(.*?)</article>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, year, info in matches:
        if not title or not url: continue

        tipo = 'movie' if item.search_type == 'movie' else 'tvshow'

        if item.search_type == 'all':
            if '<span class="TpTv BgA">TV</span>' in info: tipo = 'tvshow'
            else: tipo = 'movie'

        sufijo = '' if item.search_type != 'all' else tipo

        thumb if thumb.startswith('http') else "https:" + thumb

        title = title.replace("&#8217;", "'").replace('&#8211;', '').replace('&#038;', '')

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title,  infoLabels = {'year': year} ))

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
         next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')

         if itemlist and next_page:
             itemlist.append(item.clone( title = 'Siguientes ...', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def por_letra(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</tr>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<strong>(.*?)</strong>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')
        thumb if thumb.startswith('http') else "https:" + thumb

        year = scrapertools.find_single_match(match, '</strong>.*?<td>(.*?)</td>')

        if item.search_type == 'movie':
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url= url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title,  infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')

        if itemlist and next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'por_letra', url = next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')

    data = do_downloadpage(item.url)

    if not PY3:
        if not data:
            if notification_d_ok:
                platformtools.dialog_ok(config.__addon_name, '[COLOR yellow]Probable incompatibilidad con la versión de su Media Center.[/COLOR]', 'El canal no da respuesta a las temporadas en esta serie.')
            else:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Posible MediaCenter Incompatibile[/COLOR][/B]' % color_adver)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="Title AA-Season.*?data-tab="(.*?)">(.*?)<i class(.*?)</tbody>')

    for season, title, episodes in matches:
        sin_epis = ''
        if '<td>Episodios no disponibles</td>' in episodes:
            sin_epis = 's'

        title = re.sub('<.?span>','',title)
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.sin_epis = sin_epis
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = season, sin_epis = sin_epis, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if item.sin_epis == 's':
        color_avis  = config.get_setting('notification_avis_color', default='yellow')
        platformtools.dialog_notification(item.title, '[B][COLOR %s]Aún sin episodios[/COLOR][/B]' % color_avis)
        return itemlist

    item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    headers = {'Referer': item.url, 'Connection': 'keep-alive'}

    data = do_downloadpage(item.url, headers = headers)

    if not PY3:
        if not data:
            if notification_d_ok:
                platformtools.dialog_ok(config.__addon_name, '[COLOR yellow]Probable incompatibilidad con la versión de su Media Center.[/COLOR]', 'El canal no da respuesta a los episodios de la temporada dn esta serie.')
            else:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Posible MediaCenter Incompatibile[/COLOR][/B]' % color_adver)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="Title AA-Season.*?data-tab="%s">.*?<tbody>(.*?)</tbody>' % str(item.contentSeason))

    if 'src=&quot;' in bloque: bloque = bloque.replace('src=&quot;', 'src="').replace('&quot;', '"')

    matches = scrapertools.find_multiple_matches(bloque, '<td><span class="Num">(\d+)</span></td>.*?src="([^"]+).*?href="([^"]+)">([^<]*)')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesPapayaXyz', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesPapayaXyz', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesPapayaXyz', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesPapayaXyz', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesPapayaXyz', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesPapayaXyz', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for epis, thumb, url, title in matches[item.page * item.perpage:]:
        thumb if thumb.startswith('http') else "https:" + thumb

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb, 
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['ts-scr', '240-p', '360-p', '480-p', 'w-rip', 'hd-rip', '720-p', '1080-p', 'DVD-RIP']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es': 'Esp', 'lat': 'Lat', 'sub': 'Vose', 'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose'}

    item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')

    data = do_downloadpage(item.url)

    if not PY3:
        if not data:
            if notification_d_ok:
                platformtools.dialog_ok(config.__addon_name, '[COLOR yellow]Probable incompatibilidad con la versión de su Media Center.[/COLOR]', 'El canal no da respuesta a los enlaces de reproducción.')
            else:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Posible MediaCenter Incompatibile[/COLOR][/B]' % color_adver)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<td><span class="Num">.*?href="([^"]+)".*?class="Button STPb">([^<]+)</a></td><td><span><.*?>\s*([^<]+)' \
             '</span></td><td><span><img.*?>([^<]+)</span></td><td><span>([^<]+)'

    matches = scrapertools.find_multiple_matches(data, patron)

    ses = 0

    for url, type, servidor, lang, qlty in matches:
        ses += 1

        if url.startswith('https://acortar24.xyz/'): continue

        if '</span><span>' in lang: lang = scrapertools.find_single_match(lang, '</span><span>(.*?)$')

        qlty = qlty.lower()
        if qlty == 'desconocido': qlty = ''

        servidor = servidor.strip().lower()

        if servidor == 'ok': servidor = 'okru'

        if servidor == 'descarga &amp; online':
             url = url.replace('&#038;', '&').replace('&amp;', '&')

             data2 = do_downloadpage(url)

             matches2 = scrapertools.find_multiple_matches(data2, '<a target="_blank" href="(.*?)"')

             for link in matches2:
                 servidor = servertools.get_server_from_url(link)
                 servidor = servertools.corregir_servidor(servidor)

                 if servidor == 'directo': continue

                 url = servertools.normalize_url(servidor, link)

                 lang = IDIOMAS.get(lang, lang)

                 itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = 'Paste', language = lang, quality = qlty.upper(), quality_num = puntuar_calidad(qlty) ))

             continue

        servidor = servertools.corregir_servidor(servidor)

        lang = IDIOMAS.get(lang, lang)

        other = servidor
        if servidor == 'player': servidor = 'directo'

        itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = other, language = lang, quality = qlty.upper(), quality_num = puntuar_calidad(qlty) ))

    # ~ Descargas
    if 'data-tplayernv="Opt' in data:
        options = scrapertools.find_multiple_matches(data, 'data-tplayernv="Opt(.*?)"><span>(.*?)</span><span>(.*?) - (.*?)</span>.*?src="(.*?)"')

        for opt, servidor, lang, qlty, url in options:
            ses += 1

            if '</span><span>' in lang: lang = scrapertools.find_single_match(lang, '</span><span>(.*?)$')

            qlty = qlty.lower()
            if qlty == 'desconocido': qlty = ''

            servidor = servidor.strip().lower()

            if servidor == 'ok': servidor = 'okru'

            if servidor == 'descarga &amp; online':
                url = url.replace('&#038;', '&').replace('&amp;', '&')

                data2 = do_downloadpage(url)

                matches = scrapertools.find_multiple_matches(data2, '<a target="_blank" href="(.*?)"')

                for link in matches:
                    servidor = servertools.get_server_from_url(link)
                    servidor = servertools.corregir_servidor(servidor)

                    if servidor == 'directo': continue

                    url = servertools.normalize_url(servidor, link)

                    lang = IDIOMAS.get(lang, lang)

                    itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = 'Paste', language = lang, quality = qlty.upper(), quality_num = puntuar_calidad(qlty) ))

                continue

            servidor = servertools.corregir_servidor(servidor)

            if 'src=&quot;' in data: data = data.replace('src=&quot;', 'src="').replace('&quot;', '"')

            url = scrapertools.find_single_match(data, 'id="Opt' + opt + '".*?src="(.*?)"')

            if url.startswith('https://acortar24.xyz/'): continue

            if url:
                url= url.replace('&amp;#038;', '&').replace('&amp;', '&')

                lang = IDIOMAS.get(lang, lang)

                itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, quality = qlty.upper(), quality_num = puntuar_calidad(qlty) ))

    # ~ Descargas Megapaste
    if '<td><span class="Num">' in data:
        opts = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)<span>(.*?)</tr>')

        for opt in opts:
            ses += 1

            url = scrapertools.find_single_match(str(opt), '</td>--><td><a rel="nofollow" target="_blank" href="(.*?)"')

            lang = scrapertools.find_single_match(str(opt), '</span></td><td><span>.*?alt=".*?">(.*?)</span>')

            qlty = scrapertools.find_single_match(str(opt), '<span><img src=.*?</span></td><td><span>(.*?)</span>')

            if '</span><span>' in lang: lang = scrapertools.find_single_match(lang, '</span><span>(.*?)$')

            qlty = qlty.lower()
            if qlty == 'desconocido': qlty = ''

            if url:
                data2 = do_downloadpage(url)

                matches = scrapertools.find_multiple_matches(data2, '<a target="_blank" href="(.*?)"')

                for link in matches:
                    servidor = servertools.get_server_from_url(link)
                    servidor = servertools.corregir_servidor(servidor)

                    if servidor == 'directo': continue

                    url = servertools.normalize_url(servidor, link)

                    lang = IDIOMAS.get(lang, lang)

                    itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = 'megaPaste', language = lang, quality = qlty.upper(), quality_num = puntuar_calidad(qlty) ))

                continue

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')

    if item.url.startswith(host):
        headers = {'Referer': host, 'Connection': 'keep-alive'}

        url = ''

        if not item.url.startswith(host):
            resp = httptools.downloadpage(item.url, follow_redirects=False, headers=headers)
        else:
            resp = httptools.downloadpage_proxy('seriespapayaxyz', item.url, follow_redirects=False, headers=headers)

        if 'location' in resp.headers: url = resp.headers['location']

        if not url:
            headers = {}

            if not item.url.startswith(host):
                data = httptools.downloadpage(item.url, headers=headers).data
            else:
                headers = {'Referer': host, 'Connection': 'keep-alive'}

                data = httptools.downloadpage_proxy('seriespapayaxyz', item.url, headers=headers).data

            url = scrapertools.find_single_match(data, 'src="(.*?)"')
            if not url: url = scrapertools.find_single_match(data, 'SRC="(.*?)"')

        if url:
            if '.megaxserie.me/' in url:
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

            itemlist.append(item.clone(server = item.server, url = url))

    elif item.url.startswith('https://ouo.io/'):
        if not '/go/' in item.url:
            item.url = item.url.replace('https://ouo.io/', 'https://ouo.io/go/')

        ouo_code = item.url.replace('https://ouo.io/go/', '')
        headers = {'Referer': item.url.replace('/go/', '/')}

        _action, _id, _token = scrapertools.find_single_match(data, '<form method="POST" action="(.*?)".*?id="(.*?)".*?name="_token" type="hidden" value="(.*?)"')
        post = {'action': _action, 'id': _id, '_token': _token }

        datos_post = do_downloadpage(item.url, post = post, headers = headers)

        try:
           _action2, _id2, _token2 = scrapertools.find_single_match(datos_post, '<form method="POST" action="(.*?)".*?id="(.*?)".*?name="_token" type="hidden" value="(.*?)"')
           if _action2:
               if not _action2 == _action:
                   headers = {'Referer': item.url}
                   if ouo_code in _action2: item.url = _action2
                   _action = _action2
                   _id = _id2
                   _token = _token2
        except:
           pass
 
        post = {'action': _action, 'id': _id, '_token': _token }

        if not item.url.startswith(host):
            url = httptools.downloadpage(item.url, post = post, headers = headers, follow_redirects=False, only_headers=True).headers.get('location', '')
        else:
            url = httptools.downloadpage_proxy('seriespapayaxyz', item.url, post = post, headers = headers, follow_redirects=False, only_headers=True).headers.get('location', '')

        if url:
            if url.startswith('//') == True: url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor:
                if '.megaxserie.me/' in url:
                    return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

                url = servertools.normalize_url(servidor, url)

                itemlist.append(item.clone(url = url, server = servidor))

    elif item.other == 'Paste' or item.other == 'megaPaste':
        servidor = servertools.get_server_from_url(item.url)
        servidor = servertools.corregir_servidor(servidor)

        if '.megaxserie.me/' in item.url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        itemlist.append(item.clone(url = item.url, server = servidor))

    else:
        if not item.url.startswith(host):
            data = httptools.downloadpage(item.url).data
        else:
            data = httptools.downloadpage_proxy('seriespapayaxyz', item.url).data


        new_url = scrapertools.find_single_match(data, "location.href='([^']+)")

        if new_url:
            if '.megaxserie.me/' in new_url:
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

            servidor = servertools.get_server_from_url(new_url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone(url = new_url, server = servidor))

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

