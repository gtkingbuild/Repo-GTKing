# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seriesflix.video/'

perpage = 24


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_seriesflixvideo_proxies', default=''):
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


def do_downloadpage(url, post=None, headers=None, follow_redirects=False):
    # ~ data = httptools.downloadpage(url, post=post, headers=headers, follow_redirects=follow_redirects).data
    data = httptools.downloadpage_proxy('seriesflixvideo', url, post=post, headers=headers, follow_redirects=follow_redirects).data

    return data


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-series-online/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'generos', search_type = 'tvshow', grupo = 'productoras' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    if item.grupo == 'productoras':
        bloque = scrapertools.find_single_match(data, '>PRODUCTORAS<(.*?)</ul>')
    else:
        bloque = scrapertools.find_single_match(data, '>GÉNEROS<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">(.*?)</a>(.*?)</li>')

    for url, tit, tot in matches:
        if item.grupo == 'productoras':
            if 'series-de-' not in url: continue
        else:
            if 'series-de-' in url: continue

            if tit == 'Argentinas': continue
            elif tit == 'Colombianas': continue
            elif tit == 'Españolas': continue
            elif tit == 'Mexicanas': continue
            elif tit == 'Rusas': continue
            elif tit == 'Turcas': continue

        title = tit.replace('Series de', '').strip()
        if tot: title = title + ' %s' % tot.strip()

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    if item.grupo == 'productoras':
        return sorted(itemlist, key=lambda i: i.title)
    else:
        return itemlist


def paises(item):
    logger.info()
    itemlist = []

    labels_paises = [
          ('argentinas'),
          ('colombianas'),
          ('espanolas'),
          ('mexicanas'),
          ('rusas'),
          ('turcas')
      ]

    for x in labels_paises:
        if x == 'turcas':
            url = host + 'genero/' + x + '/'
        else:
            url = host + 'genero/series-' + x + '/'

        title = x.capitalize()
        if title == 'Espanolas': title = 'Españolas'

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h2 class="Title">(.*?)<nav class="wp-pagenavi">')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, '<h2 class="Title">(.*?)</h2>').strip()
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-src="([^"]+)')

        year = scrapertools.find_single_match(article, ' <span class="Qlty Yr">(\d{4})</span>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            if '<nav class="wp-pagenavi">' in data:
                next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?<a class="page-link" href="(.*?)">')
                if next_page:
                  itemlist.append(item.clone (url = next_page, page = 0, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<section class="SeasonBx AACrdn">.*?<a href="(.*?)".*?<span>(.*?)</span>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, numtempo in matches:
        numtempo = int(numtempo)

        title = 'Temporada ' + str(numtempo)

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.url = url
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        titulo = title
        if len(matches) >= 10:
            if len(str(numtempo)) == 1:
                titulo = title = 'Temporada 0' + str(numtempo)

        itemlist.append(item.clone( action = 'episodios', title = titulo, url = url, page = 0, contentType = 'season', contentSeason = numtempo ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key = lambda it: it.title)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<tr class="Viewed">(.*?)</tr>')

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesFlixVideo', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesFlixVideo', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesFlixVideo', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesFlixVideo', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesFlixVideo', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for data_epi in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(data_epi, '<a href="([^"]+)"')
        episode = scrapertools.find_single_match(data_epi, 'td><span class="Num">(.*?)</span>')
        if not url or not episode: continue

        title = scrapertools.find_single_match(data_epi, '<td class="MvTbTtl">.*?>(.*?)</a>')

        if not item.contentSerieName in title: title = item.contentSerieName + ' ' + str(item.contentSeason) + 'x' + episode + ' ' + title

        fecha = scrapertools.find_single_match(data_epi, '<span>(.*?)</span>')
        if fecha: title = title + ' [COLOR gray](' + fecha + ')[/COLOR]'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'castellano': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<li data-typ="episode"(.*?)</li>')

    ses = 0

    for match in matches:
        ses += 1

        ref = scrapertools.find_single_match(match, '<div class="Optntl">Opción <span>(.*?)</span></div>').strip()

        servidor = scrapertools.find_single_match(match, '<p class="AAIco-dns">(.*?)</p>').strip().lower()

        lang = scrapertools.find_single_match(match, '<p class="AAIco-language">(.*?)</p>')
        lang = lang.replace('🟢', '').replace('⚪️', '').strip().lower()

        if 'castellano' in lang.lower(): lang = 'castellano'
        elif 'latino' in lang.lower(): lang = 'latino'
        elif 'subtitulado' in lang.lower(): lang = 'subtitulado'

        qlty = scrapertools.find_single_match(match, '<p class="AAIco-equalizer">(.*?)</p>')

        d_key = scrapertools.find_single_match(match, ' data-key="(.*?)"')
        d_id = scrapertools.find_single_match(match, ' data-id="(.*?)"')

        if not d_key or not d_id: continue

        url = host + '?trembed=' + d_key + '&trid=' + d_id + '&trtype=2'

        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'server':
            servidor = 'directo'
            ref = ref + ' server'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, quality = qlty,
                              language = IDIOMAS.get(lang, lang), other = ref ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    data = do_downloadpage(item.url)

    url = scrapertools.find_single_match(data, 'src="([^"]+)"')
    if url.startswith('/'): url = host + url[1:]

    if '/flixplayer.' in url:
        data = httptools.downloadpage(url).data
        url = scrapertools.find_single_match(data, 'link":"([^"]+)"')

    elif host in url or '.seriesflix.video' in url and '?h=' in url:
        fid = scrapertools.find_single_match(url, "h=([^&]+)")
        url2 = url.replace('index.php', '').split('?h=')[0] + 'r.php'

        resp = httptools.downloadpage(url2, post= 'h=' + fid, headers = {'Referer': url}, follow_redirects=False)
        if 'location' in resp.headers: url = resp.headers['location']
        else: url = None

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)
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
