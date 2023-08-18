# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

if PY3:
    from urllib.parse import unquote
else:
    from urlparse import unquote


import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://meganovelas.online/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://www.srnovelas.cc/', 'https://srnovelas.com/']

domain = config.get_setting('dominio', 'srnovelas', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'srnovelas')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'srnovelas')
    else: host = domain


perpage = 20


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_srnovelas_proxies', default=''):
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


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not headers: headers = {'Referer': host}

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers).data
    else:
        data = httptools.downloadpage_proxy('srnovelas', url, post=post, headers=headers).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers).data
                else:
                    data = httptools.downloadpage_proxy('srnovelas', url, post=post, headers=headers).data
        except:
            pass

    if '<title>Just a moment...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'srnovelas', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_srnovelas', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='srnovelas', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_srnovelas', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_srnovelas', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'novelas-completas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'olive' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host, group = 'onair', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'tvshow' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'América', action = 'list_all', url = host + 'novelas-americanas/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Brasil', action = 'list_all', url = host + 'novelas-brasilenas/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Chile', action = 'list_all', url = host + 'novelas-chilenas/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Colombia', action = 'list_all', url = host + 'novelas-colombianas/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'México', action = 'list_all', url = host + 'novelas-mexicanas/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Turquía', action = 'list_all', url = host + 'novelas-turcas/', text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    if item.group == 'onair': bloque = scrapertools.find_single_match(data, '>Novelas en Emisión<(.*?)<footer>')
    else:
       if '>Novelas Completas Gratis<' in data: bloque = scrapertools.find_single_match(data, '>Novelas Completas Gratis<(.*?)</h2>')
       else: bloque = scrapertools.find_single_match(data, '<h1>(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, ' title="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        ref_serie = url

        year = '-'

        try:
           name = title.split(" (")[0]
           year = title.split(" (")[1]
           if ')' in year: year = year.split(")")[0]
           elif '-' in year: year = year.split("-")[0]

           if year: title = name
        except:
            name = title

        SerieName = name

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        elif 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]

        SerieName = SerieName.strip()

        if 'Capitulos' in SerieName: SerieName = SerieName.split("Capitulos")[0]
        elif 'capitulos' in SerieName: SerieName = SerieName.split("capitulos")[0]

        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        title = title.capitalize()

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, ref_serie = ref_serie, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage

            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page = item.page + 1, action='list_all', text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Últimos Episodios<(.*?)>Novelas en Emisión<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, ' title="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        ref_serie = url

        year = '-'

        try:
           name = title.split(" (")[0]
           year = title.split(" (")[1]
           if ')' in year: year = year.split(")")[0]
           elif '-' in year: year = year.split("-")[0]

           if year: title = name
        except:
            name = title

        SerieName = name

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        elif 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]

        SerieName = SerieName.strip()

        if 'Capitulos' in SerieName: SerieName = SerieName.split("Capitulos")[0]
        elif 'capitulos' in SerieName: SerieName = SerieName.split("capitulos")[0]

        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]
        elif 'capitulo' in SerieName: SerieName = SerieName.split("capitulo")[0]

        SerieName = SerieName.strip()

        ref_serie = url

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        epis = scrapertools.find_single_match(url, '-capitulo-(.*?)$')

        epis = epis.replace('/', '')

        if not epis: epis = 1

        title = title.capitalize()

        title = title.replace('capitulo', '[COLOR goldenrod]Capitulo[/COLOR]').replace('capítulo', '[COLOR goldenrod]Capítulo[/COLOR]')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, ref_serie = ref_serie, infoLabels={'year': year},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    seasons = scrapertools.find_multiple_matches(data, '<span class="su-spoiler-icon">.*?Temporada(.*?)</div>')

    if not seasons:
        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]Temporadas[/COLOR]')
        item.page = 0
        item.contentType = 'season'
        item.contentSeason = 1
        itemlist = episodios(item)
        return itemlist

    for title in seasons:
        tempo = title.strip()

        title = 'Temporada ' + title.strip()

        if len(seasons) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    if '<span class="su-spoiler-icon">' in data:
        bloque = scrapertools.find_single_match(data, '<span class="su-spoiler-icon">.*?Temporada ' + str(item.contentSeason) + '(.*?)</div></div>')
        if not bloque: bloque = scrapertools.find_single_match(data, '<ul class="su-posts su-posts-list-loop(.*?)</ul>')
    else:
        bloque = scrapertools.find_single_match(data, '<ul class="su-posts su-posts-list-loop(.*?)</ul>')

    episodes = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?>(.*?)</a>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(episodes)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SrNovelas', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SrNovelas', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SrNovelas', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SrNovelas', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SrNovelas', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SrNovelas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, title, in episodes[item.page * item.perpage:]:
        epis = scrapertools.find_single_match(title, '.*?Capitulo (.*?) ').strip()
        if not epis: epis = scrapertools.find_single_match(title, '.*?Capitulo (.*?)$').strip()

        epis = epis.replace('|', '').strip()

        if not epis: epis = '1'

        titulo = str(item.contentSeason) + 'x' + epis + ' ' + item.contentSerieName

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

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

    data = do_downloadpage(item.url)

    # ~ embeds
    matches = scrapertools.find_multiple_matches(data, 'data-title="Opción.*?src="(.*?)"')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    for url in matches:
        url = url.strip()
        ref = item.url

        lang = 'Lat'

        itemlist.append(Item( channel=item.channel, action = 'play', server = 'directo', url = url, ref = ref, ref_serie = item.ref_serie, language = lang ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    servidor = servertools.get_server_from_url(url)
    servidor = servertools.corregir_servidor(servidor)

    if not servidor == 'direct':
        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

        httptools.save_cookie('w3tc_referrer', host, 'srnovelas.com')

        return itemlist

    CUSTOM_HEADERS = {}
    CUSTOM_HEADERS['Cookie'] = 'w3tc_referrer=' + item.ref_serie
    CUSTOM_HEADERS['Referer'] = item.ref

    httptools.save_cookie('w3tc_referrer', item.ref_serie, 'srnovelas.com')

    data = httptools.downloadpage(item.url, headers=CUSTOM_HEADERS).data

    olid = scrapertools.find_single_match(data, "var OLID = '(.*?)'")

    if olid:
       new_url = scrapertools.find_single_match(data, 'src="(.*?)"')

       if new_url:
           new_url = new_url.replace("'+OLID+'", '')
           new_url = new_url + olid

           referer = item.url.replace('/?or=', '/?od=')

           resp = httptools.downloadpage(new_url, headers={'Referer': referer}, follow_redirects=False, only_headers=True)

           httptools.save_cookie('w3tc_referrer', host, 'srnovelas.com')

           if 'location' in resp.headers:
              url = resp.headers['location']
              url = unquote(str(url))
           else:
              return 'Archivo [COLOR plum]inexistente[/COLOR]'

           if "b'" in str(url): url = scrapertools.find_single_match(str(url), "'(.*?)'")

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

    httptools.save_cookie('w3tc_referrer', host, 'srnovelas.com')

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

        ref_serie = url

        title = title.capitalize()

        if '-capitulo-' in url:
            epis = scrapertools.find_single_match(url, '-capitulo-(.*?)$')

            epis = epis.replace('/', '')

            if not epis: epis = 1

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, ref_serie = ref_serie, infoLabels={'year': '-'},
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epis ))

        else:
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, ref_serie = ref_serie, infoLabels={'year': '-'}, 
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
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


