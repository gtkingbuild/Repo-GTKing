# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.henaojara.com/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://henaojara.com/', 'https://henaojara2.com/', 'https://www1.henaojara.com/']


domain = config.get_setting('dominio', 'henaojara', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'henaojara')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'henaojara')
    else: host = domain


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

    if not headers: 
        if url == host: headers = {'Referer': 'https://duckduckgo.com/'}
        else: headers = {'Referer': host}

    timeout = None
    if host in url:
        if config.get_setting('channel_henaojara_proxies', default=''): timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        data = httptools.downloadpage_proxy('henaojara', url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '?s=' in url:
                platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')
                data = httptools.downloadpage_proxy('henaojara', url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers).data
                else:
                    data = httptools.downloadpage_proxy('henaojara', url, post=post, headers=headers, timeout=timeout).data
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

    domain_memo = config.get_setting('dominio', 'henaojara', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_henaojara', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='henaojara', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_henaojara', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_henaojara', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


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

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver/category/categorias/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'olive' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_last', url = host, search_type = 'tvshow', text_color = 'olive' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'ver/category/emision/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'ver/category/estrenos/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'ver/category/categorias/espanol-castellano/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'ver/category/categorias/latino/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'ver/category/pelicula/?tr_post_type=1', search_type = 'movie', text_color = 'deepskyblue' ))

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

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

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

        title = title.replace('#8217;', "'")

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

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=PeliName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<link rel="next" href="(.*?)"')

        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Últimos Animes<(.*?)>Últimos Episodios<')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3 class="Title">(.*?)</h3>')

        if not url or not title: continue

        title = title.replace('Español Latino HD', '').strip()

        title = title.replace('#8217;', "'")

        SerieName = title

        SerieName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", title).strip()

        SerieName = SerieName.strip()

        temp = scrapertools.find_single_match(match, '<span class="Year">Temporada (.*?)-')
        temp = temp.replace('Español Latino HD', '').strip()

        if not temp: temp = 1

        title = 'Temporada ' + str(temp) + ' ' + title

        title = title.replace('Temporada', '[COLOR goldenrod]Temporada[/COLOR]')

        if 'Pelicula' in title: title = title.replace('Pelicula', '[COLOR deepskyblue]Pelicula[/COLOR]')

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="Year">.*?-(.*?)</span>').strip()

        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, infoLabels={'year': year},
                                    contentType = 'tvshow', contentSerieName = SerieName, contentSeason = temp, list_last = True ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Últimos Episodios<(.*?)</section>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3 class="Title">(.*?)</h3>')

        if not url or not title: continue

        title = title.replace('Español Latino HD', '').strip()

        title = title.replace('#8217;', "'")

        SerieName = title

        SerieName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", title).strip()

        SerieName = SerieName.strip()

        temp = scrapertools.find_single_match(match, '<span class="ClB">(.*?)x')
        epis = scrapertools.find_single_match(match, '<span class="ClB">.*?x(.*?)</span>')

        title = 'Episodio ' + epis + ' ' + title

        title = title.replace('Episodio', '[COLOR goldenrod]Episodio[/COLOR]')

        if 'Pelicula' in title: title = title.replace('Pelicula', '[COLOR deepskyblue]Pelicula[/COLOR]')

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, '<span class="Year">.*?,(.*?)</span>').strip()

        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb, infoLabels={'year': year},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason=temp, contentEpisodeNumber=epis))

    tmdb.set_infoLabels(itemlist)

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
                                        thumbnail = item.thumbnail, contentType='movie', contentTitle=item.title, text_color='tan' ))

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

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = season, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

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

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        epis = scrapertools.find_single_match(match,'<td><span class="Num">(.*?)</span>')

        url = scrapertools.find_single_match(match,'<a href="(.*?)"')

        thumb = scrapertools.find_single_match(match,'<img src="(.*?)"')

        titulo = '%sx%s - Episodio %s' % (item.contentSeason, epis, epis)

        titulo = titulo + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage, text_color='coral' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if item.list_last:
        new_url = scrapertools.find_single_match(data, '<td class="MvTbTtl"><a href="(.*?)"')

        if new_url: data = do_downloadpage(new.url)

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

        if other.lower() == 'hqq' or other.lower() == 'waaw'  or other.lower() == 'netu' or other.lower() == 'netuplayer': continue

        if other.lower() == 'streamwish': servidor = 'various'
        else: servidor = 'directo'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

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
           timeout = None
           if host in url:
               if config.get_setting('channel_henaojara_proxies', default=''): timeout = 40

           if not url.startswith(host):
               url = httptools.downloadpage(url, follow_redirects=False, timeout=timeout).headers['location']
           else:
               url = httptools.downloadpage_proxy('henaojara', url, follow_redirects=False, timeout=timeout).headers['location']
        except:
           url = ''

    else:
        data = do_downloadpage(url)

        new_url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')

        if new_url:
            if new_url.startswith('//'): new_url = 'https:' + new_url

            url = new_url

            if '/nyuu.hjstream.xyz' in new_url:
                data = do_downloadpage(new_url)

                url = scrapertools.find_single_match(data, 'url: "(.*?)"')

                if url:
                    itemlist.append(item.clone( url=url, server='directo'))
                    return itemlist

            elif '/player/go.php?v=' in new_url:
                new_url = new_url.replace('/player/go.php?v=', '/player/go-player.php?v=')

                data = do_downloadpage(new_url)

                url = scrapertools.find_single_match(data, 'src="(.*?)"')
                if url.startswith('//'): url = 'https:' + url

    if '/hqq.' in url or '/waaw.' in url or '/netu' in url:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    elif '.mystream.' in url:
        return 'Servidor [COLOR tan]Cerrado[/COLOR]'

    elif '/streamium.xyz/' in url: url = ''
    elif '/descargas/' in url: url = ''

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
