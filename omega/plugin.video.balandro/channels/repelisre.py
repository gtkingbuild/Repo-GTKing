# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


# ~ 14/12/24  Los Episodios de las Series SIEMPRE dan Error Pagina NO Encomtrada

host = 'https://wow.repelis.re/'


api = 'wp-json/cuevana/v1/'


useragent = httptools.get_user_agent()


perpage = 25


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_repelisre_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar[/B] ...', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, ref, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://repelis.re/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not host in url:
        if ref.startswith('/'): ref = host[:-1] + ref
        else: 
           if not host in ref: ref = host + ref

        url = host + api + url

        if '/page/' in ref: page = scrapertools.find_single_match(ref, '/page/(.*?)$')
        else: page = '1'

        headers = dict()
        headers["User-Agent"] = useragent

        headers["paged"] = str(page)
        headers["limit"] = "25" 

        headers["Referer"] = ref

    else:
        if '/series-online/' in url:
            headers = dict()
            headers["User-Agent"] = useragent

            headers["Referer"] = ref

    hay_proxies = False
    if config.get_setting('channel_repelisre_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('repelisre', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '/search?' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('RePelisRe', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('repelisre', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if not url.startswith(host):
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
        else:
            if hay_proxies:
                data = httptools.downloadpage_proxy('repelisre', url, post=post, headers=headers, timeout=timeout).data
            else:
                data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>Just a moment...</title>' in data:
        if not '/search?' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='repelisre', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))
    itemlist.append(Item( channel='helper', action='show_help_repelisre', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('repelisre') ))


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', ref = '/peliculas-online/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', ref = '/series-online/', search_type = 'tvshow') )

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage('menu', item.ref)

    bloque = scrapertools.find_single_match(str(data), '"Generos"(.*?)$')

    matches = scrapertools.find_multiple_matches(str(bloque), '"name":"(.*?)".*?"link":"(.*?)"')

    for title, ref in matches:
        title = clean_title(title)

        ref = ref.replace('\\/', '/')

        genre = scrapertools.find_single_match(ref, '/genero-de-la-pelicula/(.*?)/')

        url = 'taxonomy?tax-data={"name":"genre","term":"' + genre + '"}'

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, ref = ref, group = 'genres', text_color='deepskyblue' ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    if item.group == 'genres': item.url = item.url + 'chrome?paged=' + str(item.page) + '&ptype=movies,series&limit=25&lang=any'

    if not item.url:
        item.url = 'chrome?type=movies&paged=' + str(item.page) + '&limit=25&lang=any'

        if item.search_type == 'tvshow': item.url = 'chrome?type=series&paged=' + str(item.page) + '&limit=25&lang=any'

    data = do_downloadpage(item.url, item.ref)

    data = data.replace('"_id":', '"_id":"')

    matches = scrapertools.find_multiple_matches(str(data), '"link":(.*?)"genres"')

    for match in matches:
        ref = scrapertools.find_single_match(str(match), '.*?"(.*?)"')
        _id = scrapertools.find_single_match(str(match), '_id":"(.*?)"')

        _id = _id.replace(',', '').strip()

        if not ref or not _id: continue

        ref = ref.replace('\\/', '/')

        if not '/pelicula' in ref and not '/serie' in ref: continue

        title = scrapertools.find_single_match(str(match), '"title":"(.*?)"')

        title = clean_title(title)

        title = title.replace('&#8217;', "'").replace('&amp;', '&').replace('&#8211;', '')

        thumb = scrapertools.find_single_match(str(match), '"cover":"(.*?)"')

        thumb = thumb.replace('\\/', '/')

        thumb = host[:-1] + thumb

        plot = scrapertools.find_single_match(str(match), '"desc":"(.*?)"')

        plot = clean_title(plot)

        year = scrapertools.find_single_match(str(match), '"release":"(.*?)"')
        year = scrapertools.find_single_match(year, '(.*?)-')
        if not year: year = '-'

        if not host in ref: ref = host[:-1] + ref

        tipo = 'movie' if '/pelicula' in ref else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url = 'player/', id = _id, ref = ref, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType='movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url = ref, id = _id, ref = ref, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if 'search?' in item.url:  return itemlist

    if itemlist:
        tot_pages = scrapertools.find_single_match(str(data), '"total_pages":(.*?)$')

        tot_pages = tot_pages.replace('}', '').strip()

        if tot_pages:
            tot_pages = int(tot_pages)
            next_page = item.page + 1

            if next_page <= tot_pages:
                if 'moviespage' in item.url or 'seriesspage' in item.url: url = ''
                else: url = item.url

                if not '/page/' in item.ref:
                    if not item.ref.endswith('/'): ref = item.ref + '/page/' + str(next_page) + '/'
                    else: ref = item.ref + 'page/' + str(next_page) + '/'
                else:
                    ref = scrapertools.find_single_match(item.ref, '(.*?)/page/')
                    if not ref.endswith('/'): ref = ref + '/page/' + str(next_page) + '/'
                    else: ref = ref + 'page/' + str(next_page) + '/'

                itemlist.append(item.clone( title='Siguientes ...', url = url, ref = ref, page = next_page, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url, item.ref)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    temporadas = re.compile('>Temporada(.*?)</button>', re.DOTALL).findall(data)

    for tempo in temporadas:
        tempo = tempo.replace('Temporada', '').replace('TEMPORADA', '').strip()

        nro_tempo = tempo

        title = 'Temporada ' + nro_tempo

        if len(temporadas) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url, item.ref)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div x-show="tab === ' + "'season" + str(item.contentSeason) + "'" + '"(.*?)</ul>')

    patron = '<img src="(.*?)".*?overflow-ellipsis">(.*?)</div>.*?<p class="text-xs">(.*?)</p>.*?<a class="lka".*?href="(.*?)"'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('RePelisRe', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('RePelisRe', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('RePelisRe', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('RePelisRe', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('RePelisRe', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('RePelisRe', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('RePelisRe', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, epis, title, url in matches:
        epis = epis.replace('Proximo', '').replace('Episodio', '').strip()

        if not epis: epis = 1

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url + item.id, item.ref)

    matches = scrapertools.find_multiple_matches(str(data), '"audio":"(.*?)"server"')

    ses = 0

    for option in matches:
        ses += 1

        lang = scrapertools.find_single_match(str(option), '(.*?)"')

        if lang == 'CASTELLANO': lang = 'Esp'
        elif lang == 'LATINO': lang = 'Lat'
        elif lang == 'SUBTITULADO': lang = 'Vose'
        elif lang == 'INGLES': lang = 'Vose'

        qlty = scrapertools.find_single_match(str(option), '"quality":"(.*?)"')

        url = scrapertools.find_single_match(str(option), '"url":"(.*?)"')

        url = url.replace('\\/', '/')

        if '/cinestart.' in url: continue
        elif '/1fichier.' in url: continue

        if host in url: continue
        elif url.endswith('.srt'): continue

        url = url.replace('/netu.repelis.run/', '/waaw.to/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if 'okru.' in url: servidor = 'okru' 

        if not servidor == 'torrent':
            if not 'http' in url: continue

        other = ''

        if config.get_setting('developer_mode', default=False):
            if servidor == 'directo':
                try:
                   if '//' in url: other = url.split('//')[1]
                   else: other = url.split('/')[1]

                   other = other.split('/')[0]
                except:
                   other = url

        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = lang, quality = qlty, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def clean_title(title):
    logger.info()

    title = title.replace('\\u00e1', 'a').replace('\\u00c1', 'a').replace('\\u00e9', 'e').replace('\\u00ed', 'i').replace('\\u00f3', 'o').replace('\\u00fa', 'u')
    title = title.replace('\\u00f1', 'ñ').replace('\\u00bf', '¿').replace('\\u00a1', '¡').replace('\\u00ba', 'º').replace('\\u2013', '-')
    title = title.replace('\\u00eda', 'a').replace('\\u00f3n', 'o').replace('\\u00fal', 'u').replace('\\u00e0', 'a')
    title = title.replace('\\u00c9', 'E').replace('\\u00da', 'U')
    title = title.replace("\\u00f3", "o").replace("\\u00ed", "i").replace("\\u00f1", "ñ").replace("&#8217;", "").replace("\\u00e1", "a").replace("\\u00e9", "e").replace("\\", "")

    title = title.replace('\\', '').replace('\\/', '').strip()

    return title


def search(item, texto):
    logger.info()
    try:
        item.url = 'search-title?q=' + texto.replace(" ", "+")
        item.ref = 'search-title?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
