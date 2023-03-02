# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://pelisflix2.fun/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://pelisflix.li/', 'https://pelisflix2.one/', 'https://ww1.pelisflix2.one/',
             'https://ww2.pelisflix2.one/', 'https://ww3.pelisflix.biz/', 'https://pelisflix.biz/',
             'https://pelisflix.pw/', 'https://pelisflix.run/']


domain = config.get_setting('dominio', 'pelisflix', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'pelisflix')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'pelisflix')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_pelisflix_proxies', default=''):
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

    # ~ data = httptools.downloadpage(url, post=post, headers=headers.data
    data = httptools.downloadpage_proxy('pelisflix', url, post=post, headers=headers).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
                data = httptools.downloadpage_proxy('pelisflix', url, post=post, headers=headers).data
        except:
            pass

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'pelisflix', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_pelisflix', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='pelisflix', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_pelisflix', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'productoras', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url = host + 'peliculas/'

    data = do_downloadpage(url)

    bloque = scrapertools.find_single_match(data, '>GÉNEROS<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url ))

    if itemlist:
        itemlist.append(item.clone( title = 'DC Comics', action = 'list_all', url = host + 'categoria/dc-comics-hd-1a2b3a5/' ))
        itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + 'categoria/marvel-2-hd-b2e4s5b/' ))
        itemlist.append(item.clone( title = 'Western', action = 'list_all', url = host + 'categoria/western/' ))

    return sorted(itemlist, key=lambda it: it.title)


def productoras(item):
    logger.info()
    itemlist = []

    url = host + 'series/'

    data = do_downloadpage(url)

    bloque =  scrapertools.find_single_match(data, '>PRODUCTORAS<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)".*?title">(.*?)</span>').findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="Qlty Yr">(.*?)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(match, '<span class="Qlty">(.*?)</span>')

        tipo = 'movie' if '/peliculas/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="(.*?)"')

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', group = item.group, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('<section class="SeasonBx.*?<a href="(.*?)".*?<span>(.*?)</span>', re.DOTALL).findall(data)

    for url, tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.url = url
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, page = 0, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    patron = '<tr class="Viewed">.*?<span class="Num">(.*?)</span>.*?<a href="(.*?)".*?src="(.*?)".*?<a href=.*?>(.*?)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PelisFlix', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisFlix', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisFlix', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisFlix', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PelisFlix', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for episode, url, thumb, title in matches[item.page * item.perpage:]:
        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode ))

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

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<button(.*?)</button>')

    ses = 0

    for match in matches:
        ses += 1

        dkey = scrapertools.find_single_match(match, 'data-key="(.*?)"')
        dide = scrapertools.find_single_match(match, 'data-id="(.*?)"')

        if not dkey or not dide: continue

        lang = scrapertools.find_single_match(match, "</span>.*?<span>(.*?)</span>").lower().strip()

        if 'latino' in lang: lang = 'Lat'
        elif 'castellano' in lang or 'español' in lang: lang = 'Esp'
        elif 'subtitulado' in lang or 'vose' in lang: lang = 'Vose'
        else: lang = '?'

        qlty = scrapertools.find_single_match(match, "</span>.*?<span>.*?<span>(.*?)•").strip()

        servidor = scrapertools.find_single_match(match, "</span>.*?<span>.*?<span>.*?•(.*?)</span>").strip().lower()

        servidor = servertools.corregir_servidor(servidor)

        if 'gounlimited' in servidor: continue
        elif 'video' in servidor: continue
        elif 'app' in servidor: continue

        if servidor == 'dood': servidor = 'doodstream'

        if 'data-typ="movie"' in match: dtype = "1"
        else: dtype = "2"

        url = host + '?trembed=%s&trid=%s&trtype=%s' % (dkey , dide, dtype)

        if 'vip' in servidor:
            data = do_downloadpage(url)

            url = scrapertools.find_single_match(data, 'src="(.*?)"')

            data = do_downloadpage(url)

            matches2 = re.compile("go_to_player\('([^']+)'\)", re.DOTALL).findall(data)

            for url in matches2:
                itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url,
                                      language = lang, quality = qlty, other = servidor.capitalize() ))

            continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, quality = qlty ))

    # ~ Download

    matches = scrapertools.find_multiple_matches(data, '<div class="OptionBx on">(.*?)</li>')

    for match in matches:
        ses += 1

        lang = scrapertools.find_single_match(match, '<p class="AAIco-language">(.*?)</p>').lower().strip()

        if 'latino' in lang: lang = 'Lat'
        elif 'castellano' in lang or 'español' in lang: lang = 'Esp'
        elif 'subtitulado' in lang or 'vose' in lang: lang = 'Vose'
        else: lang = '?'

        qlty = scrapertools.find_single_match(match, '<p class="AAIco-equalizer">(.*?)</p>').strip()

        servidor = scrapertools.find_single_match(match, '<p class="AAIco-dns">(.*?)</p>').strip().lower()

        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(match, 'href="(.*?)"').strip()

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')
    item.url = item.url.replace('amp;#038;', '&').replace('#038;', '&').replace('amp;', '&')

    url = item.url

    if 'pelisflix' in url:
        data = do_downloadpage(url)

        if "<a class='fake-player-container'" in data: url = scrapertools.find_single_match(data, "<a class='fake-player-container'" + '.*?href="(.*?)"')
        else:
            new_url = scrapertools.find_single_match(data, 'src="(.*?)"')

            if new_url:
                if new_url.startswith('/stream/index.php'):
                    data = do_downloadpage(host + new_url)

                    id = scrapertools.find_single_match(data, '<input type="hidden".*?name="h".*?value="(.*?)"')

                    if id:
                        post = {'h': id}
                        url_post = host + 'stream/r.php'

                        # ~ url = httptools.downloadpage(url_post, post = post, follow_redirects=False).headers['location']
                        url = httptools.downloadpage_proxy('pelisflix', url_post, post = post, follow_redirects=False).headers['location']

                else:
                    id = scrapertools.find_single_match(new_url, '/?h=([A-z0-9]+)')

                    if id:
                        post = {'h': id}
                        url_post = host + 'stream/r.php'

                        # ~ url = httptools.downloadpage(url_post, post = post, follow_redirects=False).headers['location']
                        url = httptools.downloadpage_proxy('pelisflix', url_post, post = post, follow_redirects=False).headers['location']

    elif 'byegoto' in url:
        id = scrapertools.find_single_match(url, '=([^"]+)')

        if id:
           post = {'url': id}
           url_post =  host + 'byegoto/rd.php'

           url = do_downloadpage(url_post, post = post)

    elif 'mega1080p' in url:
        from lib import jsunpack

        new_url = do_downloadpage(url)

        pack = scrapertools.find_single_match(new_url, 'p,a,c,k,e,d.*?</script>')
        unpack = jsunpack.unpack(pack).replace('\\', '')

        url_final = scrapertools.find_single_match(unpack, "'file':'([^']+)'")

        if url_final:
            url = url_final.replace("/master", "/720/720p")
            url = 'https://pro.mega1080p.club/' + url_final
            url += '|Referer=' + url_final

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        elif '/1fichier.' in url:
              return 'Servidor NO soportado [COLOR tan]1fichier[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if not servidor == 'directo':
            itemlist.append(item.clone(server = servidor, url = url))

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

