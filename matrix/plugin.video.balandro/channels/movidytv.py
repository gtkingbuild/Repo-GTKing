# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://movidy.tv/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_movidytv_proxies', default=''):
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


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if not headers: headers = {'Referer': host}

    if '&estreno[]=' in url: raise_weberror = False
    elif '/?s=' in url:
        headers = {'Referer': url}
        raise_weberror = False

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('movidytv', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                data = httptools.downloadpage_proxy('movidytv', url, post=post, headers=headers, raise_weberror=raise_weberror).data
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

    itemlist.append(item.clone( title = 'Búsqueda de personas:', action = '', folder=False, text_color='goldenrod' ))

    itemlist.append(item.clone( title = ' - Buscar intérprete ...', action = 'search', group = 'actor', search_type = 'person',
                                plot = 'Debe indicarse el nombre y apellido/s del intérprete. Separando estos por un guión'))
    itemlist.append(item.clone( title = ' - Buscar dirección ...', action = 'search', group = 'director', search_type = 'person',
                                plot = 'Debe indicarse el nombre y apellido/s del director. Separando estos por un guión'))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-2/', search_type = 'movie' ))

    # ~ itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas-2/?estrenos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas-2/?mejor-valoradas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host + 'series/?novedades', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'series/?estreno', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'series/?mejor-valoradas', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    genres = [
       'Acción',
       'Animación',
       'Aventura',
       'Bélica',
       'Ciencia ficción',
       'Comedia',
       'Crimen',
       'Documental',
       'Drama',
       'Familia',
       'Fantasia',
       'Historia',
       'Kids',
       'Misterio',
       'Música',
       'Reality',
       'Romance',
       'Soap',
       'Suspense',
       'Terror',
       'Western'
       ]

    if item.search_type == 'movie':
        url_gen = host + 'peliculas-2/?genero[]='
    else:
        url_gen = host + 'series/?genero[]='

    for genre in genres:
        if item.search_type == 'movie':
            if genre == 'Reality': continue
            elif genre == 'Soap': continue

        url = url_gen + genre + '&estreno[]='

        itemlist.append(item.clone( action = "list_all", title = genre, url = url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    limit_year = 1965 if item.search_type == 'movie' else 1984
    if item.search_type == 'movie':
        url_any = host + 'peliculas-2/?genero[]='
    else:
        url_any = host + 'series/?genero[]='

    for x in range(current_year, limit_year, -1):
        url = url_any + '&estreno[]=' + str(x)

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    es_busqueda = '?s=' in item.url or '/actor/' in item.url or '/director/' in item.url
    tipo_url = 'tvshow' if '/serie' in item.url else 'movie'

    data = do_downloadpage(item.url)

    # ~ 14/1/2022
    if '/?s=' in item.url:
        if not data or '<title>Please Wait... | Cloudflare</title>' in data or not host in data:
            platformtools.dialog_notification('MovidyTv', '[COLOR yellow]Requiere verificación [COLOR red]reCAPTCHA[/COLOR]')
            return itemlist

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, ' title="([^"]+)"').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-echo="([^"]+)"')

        year = scrapertools.find_single_match(article, '<div class="CInfo noHidetho"><p>(.*?)</p>')
        if not year: year = '-'

        if es_busqueda:
            tipo = 'tvshow' if '/serie' in url else 'movie'
            if item.search_type not in ['all', tipo]: continue
        else:
            tipo = tipo_url

        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            if '/episodio-' in url:

               season_episode = scrapertools.find_single_match(article, '<h2><b>(.*?)</b>')
               if not season_episode: continue

               season = scrapertools.find_single_match(season_episode, '(.*?)-').strip()
               episode = scrapertools.find_single_match(season_episode, '-(.*?)$').strip()

               titulo = '%sx%s %s' % (season, episode, title)

               itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, fmt_sufijo = sufijo,
                                           contentSerieName = title, contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode,
                                           infoLabels = {'year': year} ))

            else:
                itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                            contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*>Pagina siguiente')
        if next_page:
            next_page = next_page.replace('#038;', '')
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('onclick="activeSeason.*?temporada-.*?">T(.*?)</div>', re.DOTALL).findall(data)

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
    itemlist=[]

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    if '<footer>' in data: final = '<footer>'
    else: final = '</body>'

    cuantas = scrapertools.find_multiple_matches(data, '<div class="season temporada-(.*?)">')

    if len(cuantas) == 1:
         bloque = scrapertools.find_single_match(data, '<div class="season temporada-' + str(item.contentSeason) + '(.*?)' + final)
    else:
         bloque = scrapertools.find_single_match(data, '<div class="season temporada-' + str(item.contentSeason) + '(.*?)<div class="season temporada-')
         if not bloque:
             bloque = scrapertools.find_single_match(data, '<div class="season temporada-' + str(item.contentSeason) + '(.*?)' + final)

    patron = '<a href="(.*?)".*?data-echo="(.*?)".*?<h2>(.*?)</h2>.*?<span>(.*?)</span>.*?<span>(.*?)</span>'

    matches = scrapertools.find_multiple_matches(bloque, patron)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('MovidyTv', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MovidyTv', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MovidyTv', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MovidyTv', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('MovidyTv', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for url, thumb, title, season_episode, fecha in matches[item.page * item.perpage:]:
        season = scrapertools.find_single_match(season_episode, '(.*?)-').strip()
        episode = scrapertools.find_single_match(season_episode, '-(.*?)$').strip()

        if item.contentSeason:
            if not str(item.contentSeason) == season: continue

        if not title: title = item.contentSerieName

        titulo = '%sx%s %s' % (season, episode, title)

        if fecha: titulo = titulo + '  (' + fecha + ')'

        itemlist.append(item.clone( action = 'findvideos', title = titulo, thumbnail = thumb, url = url,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['screener', 'TS', '360p', '480p', 'rip', 'hdrip', 'hdrvrip', '720p', 'HDTV', '1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def corregir_servidor(servidor):
    servidor = servidor.replace('www.', '').replace('.com', '').replace('.net', '').replace('.org', '').replace('.co', '').replace('.cc', '')
    servidor = servidor.replace('.to', '').replace('.tv', '').replace('.ru', '').replace('.io', '').replace('.eu', '').replace('.ws', '')
    servidor = servidor.replace('.', '')

    servidor = servertools.corregir_servidor(servidor)

    if servidor == 'pro': return 'fembed'
    if servidor in ['beta', 'bot', 'soap']: return 'directo'
    return servidor


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'castellano': 'Esp', 'español castellano': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose', 'ingles subtitulado': 'Vose', 'ingles': 'VO'}

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    ses = 0

    # Ver Online
    id = scrapertools.find_single_match(data, 'src="/video/(.*?).mp4"')
    url = host + 'video/' + id + '.mp4'

    headers = {'Referer': item.url}

    data_id = do_downloadpage(url, headers = headers, raise_weberror=False)
    data_id = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data_id)

    matches = scrapertools.find_multiple_matches(data_id, '<li id="(.*?)".*?<span>(.*?)</span><p>(.*?)</p>')

    for opt, servidor, qlty in matches:
        ses += 1

        url = scrapertools.find_single_match(data, "getElementById\('%s'\).setAttribute\('onclick', 'go_to_player\(.'([^']+)" % opt)[:-1]
        url = host[:-1] + url

        lang = ''
        if 'castellano' in opt: lang = 'Esp'
        elif 'latino' in opt: lang = 'Lat'
        elif 'subtitulado' in opt: lang = 'Vose'
        elif 'ingles' in opt: lang = 'VO'

        servidor = servidor.lower()
        servidor = corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, referer = item.url,
                              language = lang, quality = qlty, quality_num = puntuar_calidad(qlty) ))

    # Enlaces Externos
    bloque = scrapertools.find_single_match(data, '<div class="contEP contepID_2">(.*?)<div class="contEP contepID_3">')

    patron = r'<a href="(.*?)".*?<img src=.*?>(.*?)<b>(.*?)</b>.*?src=.*?/images/(.*?).png'

    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, servidor, qlty, lang in matches:
        ses += 1

        url = host[:-1] + url

        servidor = servidor.split('.', 1)[0]
        servidor = corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, referer = item.url,
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) ))

    # Enlaces Descargas
    bloque = scrapertools.find_single_match(data, '<div class="contEP contepID_3">(.*?)<footer>')

    patron = r'<a href="(.*?)".*?<img src=.*?>(.*?)<b>(.*?)</b>.*?src=.*?/images/(.*?).png'

    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, servidor, qlty, lang in matches:
        ses += 1

        url = host[:-1] + url

        if '/dl1.' in url: continue
        elif '/mixloads.' in url: continue

        servidor = servidor.split('.', 1)[0]
        servidor = corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, referer = item.url,
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url:
       if '/hqq.' in item.url or '/waaw.' in item.url or '/netu.' in item.url:
           return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

       servidor = servertools.get_server_from_url(item.url)
       servidor = servertools.corregir_servidor(servidor)

       if servidor != 'directo':
           url = servertools.normalize_url(servidor, item.url)
           itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.group:
            item.url = host + item.group + '/' + texto.replace(" ", "-") + '/'
            item.search_type = ''
        else:
            item.url = host + '?s=' + texto.replace(" ", "+")

        if item.search_type == '': item.search_type = 'all'
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

