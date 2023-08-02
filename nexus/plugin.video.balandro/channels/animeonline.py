# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www1.animeonline.ninja/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_animeonline_proxies', default=''):
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
    if not config.get_setting('channel_animeonline_proxies', default=''): raise_weberror=False

    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://animeonline1.ninja/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('animeonline', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                data = httptools.downloadpage_proxy('animeonline', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        except:
            pass

    if '<title>Just a moment...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return itemlist

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_animeonline', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'online/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host + 'episodio/', group = 'last_epis', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all',  url = host + 'genero/en-emision/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'tendencias/?get=tv', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'ratings/?get=tv', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Sin censura', action = 'list_all', url = host + 'genero/sin-censura/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Live action', action = 'list_all', url = host + 'genero/live-action/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En blu-ray / dvd', action = 'list_all', url = host + 'genero/blu-ray/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Amazon prime video', action = 'list_all', url = host + 'genero/amazon-prime-video/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Dragon ball', action = 'dragons', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'pelis', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def dragons(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'genero/anime-castellano/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'genero/audio-latino/', search_type = 'tvshow' ))

    return itemlist


def pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo (Películas)', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=movies', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ratings/?get=movies', search_type = 'movie' ))

    return itemlist

def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'genero/anime-castellano/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'genero/audio-latino/', search_type = 'tvshow' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    url_anio = url = host + 'release/'

    tope_year = 1985

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        url = url_anio + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '<header><h1>' in data: parte = '<header><h1>'
    else: parte = '<h1>'

    bloque = scrapertools.find_single_match(data, parte + '(.*?)</h2>')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        lang = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>')
        lang = lang.replace('Audio', '').lower().strip()

        if lang == 'latino' or lang == 'laninofinal': lang = 'Lat'
        elif lang == 'castellano' or lang == 'español': lang = 'Esp'
        elif lang == 'multi': lang = 'Multi-Audio'
        elif lang == 'triple': lang = 'Triple-Audio'
        else: lang = ''

        qlty = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>').lower()
        if 'audio' in qlty: qlty = ''
        elif 'castellano' in qlty: qlty = ''
        elif 'español' in qlty: qlty = ''

        if qlty == 'final' or qlty == 'corto' or qlty == 'sin censura': qlty = ''

        year = scrapertools.find_single_match(match, '</h3><span>(.*?)</span>')
        if not year: year = '-'

        if item.group == 'last_epis' or item.search_type == 'movie':
            if item.search_type == 'movie':
                PeliName = title

                if 'Movie' in title: PeliName = title.split("Movie")[0]

                PeliName = PeliName.strip()

                itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, languages=lang,
                                            contentType='movie', contentTitle=PeliName, infoLabels={'year': year} ))
            else:
                SerieName = title

                if 'Cap' in title: SerieName = title.split("Cap")[0]

                SerieName = SerieName.strip()

                epis = scrapertools.find_single_match(title, 'Cap(.*?)$').strip()
                if not epis: epis = 1

                itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, qualities=qlty, languages=lang,
                                            contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis,
                                            infoLabels={'year': year} ))

        else:
            SerieName = title

            if 'Movie' in title: SerieName = title.split("Movie")[0]

            SerieName = SerieName.strip()

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, qualities=qlty, languages=lang,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<span class="current">.*?' + "<a href='(.*?)'")

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile("<span class='se-t.*?'>(.*?)</span>", re.DOTALL).findall(data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = tempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist



def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>%s</span>(.*?)</div></div>" % (item.contentSeason))

    epis = re.compile("<li class='mark-(.*?)</li>", re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(epis)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimeOnline', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeOnline', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeOnline', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeOnline', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimeOnline', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for epi in epis[item.page * item.perpage:]:
        epi_num = scrapertools.find_single_match(epi, "(.*?)'>")

        thumb = scrapertools.find_single_match(epi, "data-src='(.*?)'")
        url = scrapertools.find_single_match(epi, "<a href='(.*?)'")

        title = scrapertools.find_single_match(epi, "<div class='episodiotitle'>.*?<a href=.*?'>(.*?)</a>")

        titulo = '%sx%s - %s' % (str(item.contentSeason), epi_num, title)

        Season = item.contentSeason
        Episode = epi_num

        if '.' in epi_num: Episode = epi_num.split(".")[0]

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb, 
                                    contentType = 'episode', contentSeason = Season, contentEpisodeNumber = Episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(epis) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    players = scrapertools.find_multiple_matches(data, "<li id='player-option-(.*?)</ul>")

    ses = 0

    for datos in players:
        ses += 1

        _server = scrapertools.find_single_match(datos, "<span class='server'>(.*?)</span>")

        if not 'saidochesto' in _server: continue

        data_type = scrapertools.find_single_match(datos, "data-type='(.*?)'")
        data_post = scrapertools.find_single_match(datos, "data-post='(.*?)'")
        data_nume = scrapertools.find_single_match(datos, "data-nume='(.*?)'")

        if not data_type or not data_post or not data_nume: continue

        url = host + '/wp-json/dooplayer/v1/post/' + data_post + '?type=' + data_type + '&source=' + data_nume

        data = do_downloadpage(url)

        link = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        if not link: continue

        link = link.replace('\\/', '/')

        servers = do_downloadpage(link)

        _servers = scrapertools.find_multiple_matches(servers, '<li onclick="go_(.*?)</li>')

        for dat_server in _servers:
            ses += 1

            url = scrapertools.find_single_match(dat_server, "to_player.*?'(.*?)'")

            if '/netu.' in url or '/hqq.' in url or '/waaw.' in url: continue
            elif '/saikoudane.' in url: continue

            if url:
                if url == 'undefined': continue

                if 'Sub Español' in dat_server: lang = 'Vose'
                elif 'Sub Latino' in dat_server: lang = 'Vose'
                elif 'Latino' in dat_server: lang = 'Lat'
                elif 'Castellano' in dat_server or 'español' in dat_server: lang = 'Esp'
                else: lang = '?'

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                link_other = ''

                if config.get_setting('developer_mode', default=False):
                    try:
                       link_other = url.split('//')[1]
                       link_other = link_other.split('/')[0]
                    except:
                        link_other = url

                    link_other = link_other.replace('www.', '').replace('.com', '').replace('.net', '').replace('.org', '').replace('.co', '').replace('.cc', '').replace('.sh', '')
                    link_other = link_other.replace('.to', '').replace('.tv', '').replace('.ru', '').replace('.io', '').replace('.eu', '').replace('.ws', '').replace('.sx', '').replace('.top', '')

                    link_other = servertools.corregir_servidor(link_other)

                    if link_other == servidor: link_other = ''
                    link_other = link_other.capitalize()

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = link_other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    servidor = item.server

    if url.startswith('https://krakenfiles.com/'): url = ''

    if url:
        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
