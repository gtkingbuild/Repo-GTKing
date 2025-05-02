# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.doramasyt.com/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_doramasyt_proxies', default=''):
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


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    hay_proxies = False
    if config.get_setting('channel_doramasyt_proxies', default=''): hay_proxies = True

    if '&fecha=': raise_weberror = False

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('doramasyt', url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

        if not data:
            if not 'buscar?q=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('doramasyt', url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

    if '<title>Just a moment...</title>' in data:
        if not 'buscar?q=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='doramasyt', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_doramasyt', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('doramasyt') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Doramas', action = 'mainlist_series', text_color = 'firebrick' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'doramas?categoria=pelicula', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'doramas?categoria=dorama', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Live action', action = 'list_all', url = host + 'doramas?categoria=live-action', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'emision', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'firebrick'

    genres = [
       ['policial', 'Policial'],
       ['romance', 'Romance'],
       ['comedia', 'Comedia'],
       ['escolar', 'Escolar'],
       ['accion', 'Acción'],
       ['thriller', 'Thriller'],
       ['drama', 'Drama'],
       ['misterio', 'Misterio'],
       ['fantasia', 'Fantasía'],
       ['historico', 'Histórico'],
       ['belico', 'Bélico'],
       ['militar', 'Militar'],
       ['medico', 'Médico'],
       ['ciencia-ficcion', 'Ciencia Ficción'],
       ['sobrenatural', 'Sobrenatural'],
       ['horror', 'Horror'],
       ['politica', 'Política'],
       ['familiar', 'Familiar'],
       ['melodrama', 'Melodrama'],
       ['deporte', 'Deporte'],
       ['comida', 'Comida'],
       ['supervivencia', 'Supervivencia'],
       ['aventuras', 'Aventuras'],
       ['artes-marciales', 'Artes marciales'],
       ['recuentos-de-la-vida', 'Recuentos de la vida'],
       ['amistad', 'Amistad'],
       ['psicologico', 'Psicológico'],
       ['yuri', 'Yuri'],
       ['k-drama', 'K-Drama'],
       ['j-drama', 'J-Drama'],
       ['c-drama', 'C-Drama'],
       ['hk-drama', 'HK-Drama'],
       ['tw-drama', 'TW-Drama'],
       ['thai-drama', 'Thai-Drama'],
       ['idols', 'Idolos'],
       ['suspenso', 'Suspenso'],
       ['negocios', 'Negocios'],
       ['time-travel', 'Time Travel'],
       ['crimen', 'Crimen '],
       ['yaoi', 'Yaoi'],
       ['legal', 'Legal'],
       ['juvenil', 'Juvenil'],
       ['musical', 'Musical'],
       ['reality-show', 'Reality Show'],
       ['documental', 'Documental']
       ]

    if item.search_type == 'movie':
        url_gen = host + 'doramas?categoria=pelicula&genero='
    else:
        url_gen = host + 'doramas?categoria=dorama&genero='

    for genero in genres:
        url = url_gen + genero[0]

        itemlist.append(item.clone( title = genero[1], action = 'list_all', url = url, text_color = text_color ))

    return sorted(itemlist, key=lambda i: i.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie': url_any = host + 'doramas?categoria=pelicula&fecha='
    else: url_any = host + 'doramas?categoria=dorama&fecha='

    for x in range(current_year, 1999, -1):
        url = url_any + str(x)

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '</h2>(.*?)>DoramasYT')

    matches = re.compile('ficha_efecto">(.*?)</li>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        if 'latino' in title.lower(): lang = 'Lat'
        elif 'castellano' in title.lower(): lang = 'Esp'
        else: lang = 'Vose'

        title = re.sub(r'Audio|Latino|Castellano|\((.*?)\)', '', title)
        title = re.sub(r'\s:', ':', title)

        title = title.replace('&#039;', '')

        if '>Pelicula' in match: tipo = 'movie'
        elif '>Dorama<' in match: tipo = 'tvshow'
        else: tipo = item.search_type

        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = lang, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, languages = lang, fmt_sufijo=sufijo, 
                                        contentSerieName = title, contentType = 'tvshow', contentSeason = 1, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination' in data:
            bloque = scrapertools.find_single_match(data, '<ul class="pagination(.*?)</nav>')

            next_page = scrapertools.find_single_match(bloque, '<li class="page-item active".*?href="(.*?)"')

            if next_page:
                next_page = next_page.replace('&amp;', '&')

                if 'p=' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>últimos capítulos<(.*?)>Series recientes<')

    matches = re.compile('<article>(.*?)</article>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        title = title.replace('&#039;', '')

        title = title.strip()

        if "capitulo" in title: SerieName = title.split("capitulo")[0]
        else: titulo = SerieName

        SerieName = SerieName.strip()

        season = 1

        epis = scrapertools.find_single_match(url, '-episodio-(.*?)$')

        if not epis: epis = 1

        titulo = title.replace('capitulo', '[COLOR goldenrod]Epis.[/COLOR]')

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail = thumb, url = url,
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if config.get_setting('channels_seasons', default=True):
        title = 'Sin temporadas'

        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#039;', "'").replace('&#8217;', "'"), '[COLOR tan]' + title + '[/COLOR]')

    item.page = 0
    item.contentType = 'season'
    item.contentSeason = 1
    itemlist = episodios(item)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data_ajax = scrapertools.find_single_match(data, 'data-ajax="(.*?)"')
    _token = scrapertools.find_single_match(data, '<meta name="csrf-token" content="(.*?)"')
    _url = scrapertools.find_single_match(data, '<div class="d-flex gap-3 mt-3">.*?<a href="(.*?)"')

    if not data_ajax or not _token or not _url: return itemlist

    data = do_downloadpage(data_ajax, post = {'_token': _token})

    matches = re.compile('{"num":(.*?)}', re.DOTALL).findall(str(data))

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramasYt', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    _url = scrapertools.find_single_match(_url, '(.*?)-episodio-')

    for match in matches[item.page * item.perpage:]:
        url = _url + '-episodio-' + match

        title = 'Epis. ' + match

        if item.search_type == 'movie': titulo = item.contentTitle + ' ' + title
        else: titulo = '1x'+ str(match) + ' ' + title + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = 1, contentEpisodeNumber=match ))

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

    if item.search_type == 'movie':
        item.url = item.url.replace('/dorama/', '/ver/').replace('-sub-espanol', '-episodio-1')

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '<title>Página no encontrada</title>' in data:
        new_url = item.url.replace('-sub-espanol-', '-')

        data = do_downloadpage(new_url)
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li id="play-video".*?data-player="(.*?)">(.*?)</button>', re.DOTALL).findall(data)

    ses = 0

    for d_play, srv in matches:
        ses += 1

        srv = srv.lower()

        other = ''

        if srv == 'puj': continue
        elif srv == '1cloud' or srv == 'cloud': continue

        elif srv == 'ok': srv = 'okru'
        elif srv == 'zeus': srv = 'directo'
        elif srv == 'anonfile': srv = 'anonfiles'
        elif srv == 'zippy': srv = 'zippyshare'
        elif srv == 'drive': srv = 'gvideo'
        elif srv == 'pixel': srv = 'pixeldrain'
        elif srv == 'senvid2': srv = 'sendvid'
        elif srv == 'mixdropco' or srv == 'mxdrop': srv = 'mixdrop'
        elif srv == 'mdy48tn97com': srv = 'mixdrop'

        elif srv == 'cybervynx':
             srv = 'various'

             other = 'Cybervynx'

        else:
             if srv == 'vgembedcom': srv = 'vembed'

             other = servertools.corregir_other(srv)

        servidor = servertools.corregir_servidor(srv)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        if not servidor == 'directo':
            if not servidor == 'various': other = ''
            
        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', d_play = d_play, language = 'Vose', other = other ))

    # download
    bloque = scrapertools.find_single_match(data, '>Descargas<(.*?)</div>')

    matches = re.compile('href="(.*?)".*?</svg>(.*?)</a>', re.DOTALL).findall(bloque)

    for url, srv in matches:
        ses += 1

        srv = srv.lower().strip()

        if srv == '1fichier' or srv == '1ficher': continue
        elif srv == '1cloud' or srv == 'cloud': continue

        elif srv == 'anonfile': srv = 'anonfiles'
        elif srv == 'bay': srv = 'bayfiles'
        elif srv == 'zippy': srv = 'zippyshare'
        elif srv == 'pixel': srv = 'pixeldrain'

        elif srv == 'ok':
          if '.fireload.com/' in url: continue

          elif '/1cloudfile.' in url: srv = ''

          elif '/mega.nz/' in url: srv = 'mega'

        if not srv: srv = servertools.get_server_from_url(url)

        if servertools.is_server_available(srv):
            if not servertools.is_server_enabled(srv): continue
        else:
           if not config.get_setting('developer_mode', default=False): continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = srv, title = '', url = url, language = 'Vose', other = 'D' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if not item.d_play:
        itemlist.append(item.clone( url = item.url, server = item.server ))
        return itemlist

    player = host + 'reproductor?video=' + item.d_play

    data = do_downloadpage(player)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    url = scrapertools.find_single_match(data, 'var redir = "(.*?)"')

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'buscar?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
