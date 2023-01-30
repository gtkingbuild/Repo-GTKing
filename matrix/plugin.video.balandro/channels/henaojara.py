# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://henaojara2.com/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_henaojara_proxies', default=''):
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
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://henaojara.com/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    timeout = None
    if host in url: timeout = 50

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    data = httptools.downloadpage_proxy('henaojara', url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
                data = httptools.downloadpage_proxy('henaojara', url, post=post, headers=headers, timeout=timeout).data
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
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_henaojara', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver/category/categorias/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'ver/category/emision/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'ver/category/estrenos/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'ver/category/categorias/espanol-castellano/?tr_post_type=2',
                                search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'ver/category/categorias/latino/?tr_post_type=2',
                                search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'ver/category/pelicula/?tr_post_type=1', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, '<div id="categories-3"(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?>(.*?)</a>')

    for url, title in matches:
        if title == 'EMISION': continue
        elif title == 'ESPAÑOL CASTELLANO': continue
        elif title == 'ESPAÑOL LATINO': continue
        elif title == 'ESTRENOS': continue
        elif title == 'PELICULAS': continue

        title = title.lower()
        title = title.capitalize()

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3 class="Title">(.*?)</h3>')

        if not url or not title: continue

        nro_season = ''
        if 'Temporada' in title:
            nro_season = scrapertools.find_single_match(title, 'Temporada (.*?) ').strip()
            if nro_season: nro_season = ' T' + nro_season

        SerieName = title

        if 'Temporada' in title: SerieName = title.split("Temporada")[0]
        if 'Movie' in title: SerieName = title.split("Movie")[0]

        SerieName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", title).strip()

        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        if item.search_type == 'tvshow':
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title + nro_season, thumbnail = thumb, titulo = title,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))
        else:
            PeliName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", title).strip()

            PeliName = PeliName.strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=PeliName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<link rel="next" href="(.*?)"')
        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = re.compile('data-tab="(.*?)"', re.DOTALL).findall(data)

    if not matches:
        if '<div class="TPlayer">' in data:
            if not item.search_type == 'movie':
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]Temporadas[/COLOR]')

            itemlist.append(item.clone( action='findvideos', url = item.url, title = '[COLOR yellow]Servidores[/COLOR] ' + item.titulo,
                                        thumbnail = item.thumbnail, contentType='movie', contentTitle=item.title ))

            return itemlist

    for season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]Una Temporada[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = season ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, 'data-tab="' + str(item.contentSeason) + '".*?<tbody>(.*?)</tbody>')

    matches = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for match in matches[item.page * item.perpage:]:
        epis = scrapertools.find_single_match(match,'<td><span class="Num">(.*?)</span>')

        url = scrapertools.find_single_match(match,'<a href="(.*?)"')

        thumb = scrapertools.find_single_match(match,'<img src="(.*?)"')

        titulo = '%sx%s - Episodio %s' % (item.contentSeason, epis, epis)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    lang = scrapertools.find_single_match(data, '<h1 class="Title">(.*?)<span>')

    if 'castellano' in lang.lower(): lang = 'Esp'
    elif 'latino' in lang.lower(): lang = 'Lat'
    elif 'subtitulado' in lang.lower(): lang = 'Vose'
    elif 'sub español' in lang.lower(): lang = 'Vose'
    else: lang = 'VO'

    matches = re.compile('id="Opt(.*?)">(.*?)</div>', re.DOTALL).findall(data)

    ses = 0

    for option, datos in matches:
        ses += 1

        url = scrapertools.find_single_match(datos, 'src="(.*?)"')
        if not url: url = scrapertools.find_single_match(datos, 'src=&quot;(.*?)&quot;')

        if not url: continue

        other = scrapertools.find_single_match(data, 'data-tplayernv="Opt' + str(option) + '"><span>(.*?)</span>')
        other = other.replace('<strong>', '').replace('</strong>', '')

        if other.lower() == 'hqq' or other.lower() == 'waaw'  or other.lower() == 'netu': continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = lang, other = other ))

    # Descargas
    matches = re.compile('<td><span class="Num">(.*?)</span>.*?href="(.*?)"', re.DOTALL).findall(data)

    for nro, url in matches:
        ses += 1

        other = 'D' + str(nro)

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    url = item.url

    if '/?trdownload=' in url:
        try:
           # ~ url = httptools.downloadpage(url, follow_redirects=False).headers['location']
           url = httptools.downloadpage_proxy('henaojara', url, follow_redirects=False).headers['location']
        except:
           url = ''

    else:
        data = do_downloadpage(url)

        new_url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')

        if new_url:
            if new_url.startswith('//'): new_url = 'https:' + new_url

            url = new_url

            if '/player/go.php?v=' in new_url:
                new_url = new_url.replace('/player/go.php?v=', '/player/go_player.php?v=')

                data = do_downloadpage(new_url)

                url = scrapertools.find_single_match(data, 'src="(.*?)"')
                if url.startswith('//'): url = 'https:' + url

    if '/hqq.' in url or '/waaw.' in url or '/netu' in url:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    elif '.mystream.' in url:
        return 'Servidor [COLOR tan]Cerrado[/COLOR]'

    elif '/streamium.xyz/' in url: url = ''

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone( url=url, server=servidor))

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
