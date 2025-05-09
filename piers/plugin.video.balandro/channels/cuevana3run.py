# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.cuevana3.run/'


perpage = 23


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_cuevana3run_proxies', default=''):
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
    hay_proxies = False
    if config.get_setting('channel_cuevana3run_proxies', default=''): hay_proxies = True

    if '/release/' in url: raise_weberror = False

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('cuevana3run', url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

        if not data:
            if not '/?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('Cuevana3Run', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('cuevana3run', url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if not url.startswith(host):
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
        else:
            if hay_proxies:
                data = httptools.downloadpage_proxy('cuevana3run', url, post=post, headers=headers, timeout=timeout).data
            else:
                data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if not '/?s=' in url:
        if '<title>Just a moment...</title>' in data:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
            return ''

        elif '<title>One moment, please...</title>' in data:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection [COLOR plum]Level 2[/B][/COLOR]')

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='cuevana3run', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_cuevana3run', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('cuevana3run') ))

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

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=movies', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Lista general', action = 'listado', url = host + 'catalogo-peliculas/', search_type = 'movie', text_color='moccasin' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catalogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + 'episodio/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=tv', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'tag/espanol/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'tag/latino/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'tag/sub-espanol/', text_color='moccasin' ))

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
       ('familia', 'Familia'),
       ('fantasia', 'Fantasía'),
       ('historia', 'Historia'),
       ('kids', 'Kids'),
       ('misterio', 'Misterio'),
       ('musica', 'Música'),
       ('Película de TV', 'Pelicula de tv'),
       ('reality', 'Reality'),
       ('romance', 'Romance'),
       ('sci-fi-fantasy', 'Sci-Fi & Fantasy'),
       ('suspense', 'Suspense'),
       ('terror', 'Terror'),
       ('western', 'Western')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'genero/' + opc + '/', action = 'list_all', text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
        text_color = 'deepskyblue'
        limit_year = 1939
    else:
        text_color = 'hotpink'
        limit_year = 1999

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, limit_year, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'release/' + str(x) + '/', action = 'list_all', text_color=text_color ))

    return itemlist


def listado(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')

    matches = re.compile('<td(.*?)</td>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<a href=".*?>(.*?)</a>').strip()

        if not url or not title: continue

        title = title.replace('&#039;s', "'s").replace('&#038;', '').replace('&#8211;', '').replace('&amp;', '&').strip()

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        c_year = scrapertools.find_single_match(title, '(\d{4})')
        if c_year: title = title.replace('(' + c_year + ')', '').strip()

        PeliName = title

        if '(TMDB' in PeliName: PeliName = PeliName.split("(TMDB")[0]
        if '(Es' in PeliName: PeliName = PeliName.split("(Es")[0]
        if '(Cam' in PeliName: PeliName = PeliName.split("(Cam")[0]
        if '(Sub' in PeliName: PeliName = PeliName.split("(Sub")[0]

        PeliName = PeliName.strip()

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=PeliName, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'listado', text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)>FILTRAR POR IDIOMA<')
    if not bloque: bloque = scrapertools.find_single_match(data, '</h1>(.*?)>FILTRAR POR IDIOMA<')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        title = scrapertools.find_single_match(article, 'alt="(.*?)"').strip()

        if not url or not title: continue

        title = title.replace('&#039;s', "'s").replace('&#038;', '').replace('&#8211;', '').replace('&amp;', '&').strip()

        thumb = scrapertools.find_single_match(article, '<img src="(.*?)"')

        c_year = scrapertools.find_single_match(title, '(\d{4})')
        if c_year: title = title.replace('(' + c_year + ')', '').strip()

        year = scrapertools.find_single_match(article, '</h3><span>(.*?)</span>')
        if not year: year = '-'

        tipo = 'tvshow' if '/series/' in url else 'movie'

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            if '<link rel="next"' in data:
                next_page = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)"')

                if next_page:
                    if '/page/' in next_page:
                        itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, page = 0, action = 'list_all', text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)>FILTRAR POR IDIOMA<')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()

        if not url or not title: continue

        title = title.replace('&#039;s', "'s").replace('&#038;', '').replace('&#8211;', '').replace('&#215;', 'x').replace('&amp;', '').strip()

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        season, episode = scrapertools.get_season_and_episode(url).split("x")

        contentSerieName = scrapertools.find_single_match(title, '(.*?) \d')

        titulo = str(season) + 'x' + str(episode) + ' ' + title.replace(str(season) + 'x' + str(episode), '')

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSerieName=contentSerieName, contentSeason = season, contentEpisodeNumber = episode,
                                    infoLabels={'year': '-'}))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<link rel="next"' in data:
            next_page = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'last_epis', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile("<span class='se-t.*?'>(.*?)</span>", re.DOTALL).findall(data)

    for tempo in matches:
        tempo = tempo.strip()

        title = 'Temporada ' + tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action='episodios', title=title, page = 0, contentType='season', contentSeason=tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + "</span>(.*?)</ul>")

    matches = re.compile("<li class='mark-.*?<img src='(.*?)'.*?</div><div class='numerando'>(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>", re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('Cuevana3Run', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Cuevana3Run', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Run', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Run', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Run', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Run', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Cuevana3Run', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, season_epis, url, title in matches[item.page * item.perpage:]:
        season = scrapertools.find_single_match(season_epis, '(.*?)-').strip()
        epis = scrapertools.find_single_match(season_epis, '-(.*?)$').strip()

        titulo = str(season) + 'x' + str(epis) + ' ' + title.strip()

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Latino': 'Lat', 'LAT': 'Lat', 'LA': 'Lat', 'Castellano': 'Esp', 'ESP': 'Esp', 'ES': 'Esp', 'Subtitulado': 'Vose', 'SUB': 'Vose'}

    data = do_downloadpage(item.url)

    ses = 0

    matches = re.compile("<li id='player-option-(.*?)</li>", re.DOTALL).findall(data)

    for option in matches:
        ses += 1

        dpost = scrapertools.find_single_match(option, " data-post='(.*?)'")
        dtype = scrapertools.find_single_match(option, " data-type='(.*?)'")
        dnume = scrapertools.find_single_match(option, " data-nume='(.*?)'")

        if not dpost or not dtype or not dnume: continue

        if dnume == 'trailer': continue

        post = {'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype}

        data1 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post, headers= {'Referer': item.url} )

        embed = scrapertools.find_single_match(data1, '"embed_url":"(.*?)"')

        if not embed: return itemlist

        embed = embed.replace('\\/', '/')

        datae = do_downloadpage(embed)

        bloque = scrapertools.find_single_match(datae, '<div class="SelectLangDisp">(.*?)<div class="FirstLoad"')

        lang = scrapertools.find_single_match(bloque,'/lang/(.*?).png')

        links = scrapertools.find_multiple_matches(bloque, '<li onclick="(.*?)</p>')

        for url in links:
            ses += 1

            if '//sb' in url: continue

            elif 'lvturbo' in url: continue
            elif 'vanfem' in url: continue
            elif 'fembed' in url: continue
            elif 'fcom' in url: continue

            if url:
                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                link_other = ''

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                      language = IDIOMAS.get(lang, lang), other = link_other ))

    if '/embed.php?' in item.url:
        ses += 1

        datae = do_downloadpage(item.url)

        bloque = scrapertools.find_single_match(datae, '<div class="SelectLangDisp">(.*?)<div class="FirstLoad"')

        lang = scrapertools.find_single_match(bloque,'/lang/(.*?).png')

        links = scrapertools.find_multiple_matches(bloque, '<li onclick="go_to_player.*?' + "'(.*?)'")

        for url in links:
            ses += 1

            if '//sb' in url: continue

            elif 'lvturbo' in url: continue
            elif 'vanfem' in url: continue
            elif 'fembed' in url: continue
            elif 'fcom' in url: continue

            if url:
                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                link_other = ''

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                      language = IDIOMAS.get(lang, lang), other = link_other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)</div></div></div>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()

        if not url or not title: continue

        title = title.replace('&#039;s', "'s").replace('&#038;', '').replace('&#8211;', '').replace('&amp;', '&').strip()

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        c_year = scrapertools.find_single_match(title, '(\d{4})')
        if c_year: title = title.replace('(' + c_year + ')', '').strip()

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        tipo = 'tvshow' if '>TV<' in match else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

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
