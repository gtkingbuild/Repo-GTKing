# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


# ~ 27/10/2022 por los controles que tiene la web necesitara proxies siempre incluso para hacer Play?

host = 'https://www1.inkapelis.li/'


embeds = 'inkapelis.li'

# ~ _player = 'https://gcs.megaplay.cc/'
_player = 'https://players.oceanplay.me/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://inkapelis.me/', 'https://inkapelis.in/', 'https://ww1.inkapelis.de/']


domain = config.get_setting('dominio', 'inkapelis', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'inkapelis')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'inkapelis')
    else: host = domain


# ~ players 'https://players.inkapelis.??'
points = host.count('.')

if points == 1:
    players = host.replace('https://', '').replace('/', '')
else:
    tmp_host = host.split('.')[0]
    tmp_host = tmp_host + '.'
    players = host.replace(tmp_host, '').replace('/', '')

players = 'https://player.' + players


descartar_anime = config.get_setting('descartar_anime', default=False)


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_inkapelis_proxies', default=''):
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

    raise_weberror = False if '/fecha/' in url else True

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('inkapelis', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                data = httptools.downloadpage_proxy('inkapelis', url, post=post, headers=headers, raise_weberror=raise_weberror).data
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

    domain_memo = config.get_setting('dominio', 'inkapelis', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_inkapelis', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='inkapelis', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_inkapelis', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_inkapelis', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos en HD', action = 'list_all', url = host + 'estado/estrenos-hd/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = host + 'estado/destacadas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'calidad/hd/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Superheroes', action = 'list_all', url = host + 'seccion/superheroes/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Infantiles', action = 'list_all', url = host + 'seccion/infantil/', search_type = 'movie' ))

    if not descartar_anime:
        itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'seccion/animes/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos capítulos', action = 'last_epis', url = host + 'episodio/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Últimas temporadas', action = 'last_temps', url = host + 'temporada/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Superheroes', action = 'list_all', url = host + 'seccion/superheroes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Infantiles', action = 'list_all', url = host + 'seccion/infantil/', search_type = 'tvshow' ))

    if not descartar_anime:
        itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'seccion/animes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/castellano/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/latino/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/subtituladas/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': url_gen = host + 'pelicula/'
    else: url_gen = host + 'serie/'

    data = do_downloadpage(url_gen)

    bloque = scrapertools.find_single_match(data, '<ul class="genres scrolling">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>.*?<i>(.*?)</i>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<a href=(.*?)>(.*?)</a>.*?<i>(.*?)</i>')

    for url, title, num in matches:
        if num == '0': continue

        if '/cine/' in url or '/destacadas/' in url or '/estrenos-hd/' in url: continue

        title = title.replace('&amp;', '&')

        if item.search_type == 'tvshow': titulo = title
        else: titulo = '%s (%s)' % (title, num)

        itemlist.append(item.clone( action='list_all', title=titulo, url=url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'fecha/' + str(x) + '/', action='list_all' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    productoras = [
        ['abc', 'ABC'],
        ['adult-swim', 'Adult Swim'],
        ['amazon', 'Amazon'],
        ['amc', 'AMC'],
        ['apple-tv', 'Apple TV+'],
        ['bbc-one', 'BBC One'],
        ['bbc-two', 'BBC Two'],
        ['bs11', 'BS11'],
        ['cbc', 'CBC'],
        ['cbs', 'CBS'],
        ['comedy-central', 'Comedy Central'],
        ['dc-universe', 'DC Universe'],
        ['disney', 'Disney+'],
        ['disney-xd', 'Disney XD'],
        ['espn', 'ESPN'],
        ['fox', 'FOX'],
        ['fx', 'FX'],
        ['hbc', 'HBC'],
        ['hbo', 'HBO'],
        ['hbo-espana', 'HBO España'],
        ['hbo-max', 'HBO Max'],
        ['hulu', 'Hulu'],
        ['kbs-kyoto', 'KBS Kyoto'],
        ['mbs', 'MBS'],
        ['nbc', 'NBC'],
        ['netflix', 'Netflix'],
        ['nickelodeon', 'Nickelodeon'],
        ['paramount', 'Paramount+'],
        ['showtime', 'Showtime'],
        ['sky-atlantic', 'Sky Atlantic'],
        ['stan', 'Stan'],
        ['starz', 'Starz'],
        ['syfy', 'Syfy'],
        ['tbs', 'TBS'],
        ['telemundo', 'Telemundo'],
        ['the-cw', 'The CW'],
        ['tnt', 'TNT'],
        ['tokyo-mx', 'Tokyo MX'],
        ['tv-tokyo', 'TV Tokyo'],
        ['usa-network', 'USA Network'],
        ['youtube-premium', 'YouTube Premium'],
        ['zdf', 'ZDF']
        ]

    url = host + 'network/'

    for x in productoras:
        itemlist.append(item.clone( title = x[1], url = url + str(x[0]) + '/', action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '<h2>Añadido recientemente' in data: patron = '<h2>Añadido recientemente(.*?)<div class=copy>'
    else:
        if '/page/' in item.url: patron = '</h1>(.*?)<div class=copy>'
        else: patron = '<h1>(.*?)>Géneros<'

    bloque = scrapertools.find_single_match(data, patron)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')
        if not url: url = scrapertools.find_single_match(article, ' href=(.*?)>').strip()

        title = scrapertools.find_single_match(article, '<div class=title><h4>(.*?)</h4>')
        if not title:
            title = scrapertools.find_single_match(article, 'alt="(.*?)"')
            if not title:title = scrapertools.find_single_match(article, 'alt=(.*?)>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src=(.*?)>').strip()
        if thumb.startswith('//'): thumb = 'https:' + thumb

        title_alt = title.split('(')[0].strip() if ' (' in title else ''

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>'))

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            qlty = scrapertools.find_single_match(article, '<span class="quality">([^<]+)')

            langs = []
            if '<div class="castellano">' in article: langs.append('Esp')
            if '<div class="español">' in article: langs.append('Esp')
            if '<div class="latino">' in article: langs.append('Lat')
            if '<div class="subtitulado">' in article: langs.append('Vose')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        languages = ', '.join(langs), fmt_sufijo = sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo = sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="pagination".*?<span class="current">.*?href=(.*?) ')
        if not next_page: next_page = scrapertools.find_single_match(data, '<a class=arrow_pag href=([^>]+)><i id=nextpagination')
        if not next_page: next_page = scrapertools.find_single_match(data, '<span class=current>.*?<a href=(.*?) class=inactive').strip()

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile("<span class=.*?se-t.*?>(.*?)</span>", re.DOTALL).findall(data)

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
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    season = item.contentSeason

    data = do_downloadpage(item.url)

    if item.no_block: bloque = data
    else: bloque = scrapertools.find_single_match(data, "<span class=.*?se-t.*?>" + str(season) + "</span>(.*?)</ul></div></div>")

    matches = re.compile("<li class=mark-(.*?)</div></li>").findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('InkaPelis', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('InkaPelis', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('InkaPelis', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('InkaPelis', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('InkaPelis', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for datos in matches[item.page * item.perpage:]:
        thumb = scrapertools.find_single_match(datos, "src=(.*?)>").strip()
        if thumb.startswith('//'): thumd = 'https:' + thumb

        url = scrapertools.find_single_match(datos, " href=(.*?)>").strip()
        title = scrapertools.find_single_match(datos, " href=.*?>(.*?)</a>").strip()

        if not url or not title: continue

        epis = scrapertools.find_single_match(datos, "<div class=numerando>(.*?)</div>")

        if not epis: continue

        epis = epis.split('-')[1].strip()

        titulo = season + 'x' + epis + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentSerieName = item.contentSerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')
        if not url: url = scrapertools.find_single_match(article, ' href=(.*?)>').strip()

        title = scrapertools.find_single_match(article, '<div class=title><h4>(.*?)</h4>')
        if not title:
            title = scrapertools.find_single_match(article, 'alt="(.*?)"')
            if not title: title = scrapertools.find_single_match(article, 'alt=(.*?)>').strip()

        if not url or not title: continue

        season = scrapertools.find_single_match(article, '<span>T(.*?)E').strip()
        episode = scrapertools.find_single_match(article, '<span>T.*?E(.*?)/').strip()
        if not season or not episode: continue

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src=(.*?)alt=').strip()
        if thumb.startswith('//'): thumb = 'https:' + thumb

        title = title.replace('&#215;', ' ')
        if ":" in title: title = title.split(":")[0]

        titulo = season + 'x' + episode + ' ' + title.strip()

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail = thumb, url = url,
                                    contentType = 'episode', contentSerieName = title, contentSeason = season, contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="pagination".*?<span class="current".*?href=(.*?) ')
        if not next_page: next_page = scrapertools.find_single_match(data, '<a class=arrow_pag href=([^>]+)><i id=nextpagination')
        if not next_page: next_page = scrapertools.find_single_match(data, '<span class=current>.*?<a href=(.*?) class=inactive').strip()

        if next_page:
            if '/page/' in next_page:
                mext_page = next_page.strip()

                itemlist.append(item.clone( title="Siguientes ...", action="last_epis", url = next_page, text_color='coral' ))

    return itemlist


def last_temps(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(item.url)

    matches = re.compile(' class="item se seasons"(.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')
        if not url: url = scrapertools.find_single_match(article, ' href=(.*?)>').strip()

        title = scrapertools.find_single_match(article, '<div class=title><h4>(.*?)</h4>')
        if not title:
            title = scrapertools.find_single_match(article, 'alt="(.*?)"')
            if not title: title = scrapertools.find_single_match(article, 'alt=(.*?)>').strip()

        numtempo = scrapertools.find_single_match(article, '<span class=b>(.*?)</span>')

        if not url or not title or not numtempo: continue

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src=(.*?)alt=').strip()
        if thumb.startswith('//'): thumb = 'https:' + thumb

        serie_name = title.replace('&#215;', ' ')
        if ":" in serie_name: serie_name = serie_name.split(":")[0]

        itemlist.append(item.clone( action='episodios', title=title, thumbnail=thumb, url = url, no_block = True,
                                    contentSerieName=serie_name, contentType='season', contentSeason=numtempo ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="pagination".*?<span class="current">.*?href=(.*?) ')
        if not next_page: next_page = scrapertools.find_single_match(data, '<a class=arrow_pag href=([^>]+)><i id=nextpagination')
        if not next_page: next_page = scrapertools.find_single_match(data, '<span class=current>.*?<a href=(.*?) class=inactive').strip()

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='last_temps', text_color='coral' ))

    return itemlist


def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)

    if servidor == 'drive': return 'gvideo'
    elif servidor == 'drive [vip]': return 'gvideo'
    elif servidor == 'playstp': return 'streamtape'
    elif servidor == 'stp': return 'streamtape'
    elif servidor == 'playsl': return 'streamlare'
    elif servidor == 'playsb': return 'streamsb'
    elif servidor == 'str': return 'doodstream'
    elif servidor == 'vip': return 'directo'
    elif servidor == 'premium': return 'digiload'
    elif servidor == 'goplay': return 'gounlimited'
    elif servidor in ['meplay', 'megaplay']: return 'netutv'
    elif servidor == 'playerv': return 'directo' # storage.googleapis
    elif servidor == 'stream': return 'mystream'
    elif servidor in ['evoplay', 'evo']: return 'evoload'
    elif servidor == 'zplay': return 'zplayer'
    elif servidor == 'descargar': return 'mega' # 1fichier, Uptobox
    else: return servidor


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'castellano': 'Esp', 'español': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)
    data = re.sub('\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<li id=player-option-(.*?)</span>')

    ses = 0

    for enlace in matches:
        ses += 1

        dtype = scrapertools.find_single_match(data, "data-type=(.*?)data-post=").strip()
        dpost = scrapertools.find_single_match(data, "data-post=(.*?)data-nume=").strip()
        dnume = scrapertools.find_single_match(data, "data-nume=(.*?)>").strip()

        if dnume == 'trailer': continue
        elif not dtype or not dpost or not dnume: continue

        if dtype == 'tv': link_final = '/tv/meplayembed'
        else: link_final = '/movie/meplayembed'

        enbed_url = do_downloadpage(host + 'wp-json/dooplayer/v2/' + dpost + link_final, headers={'Referer': item.url})
        if not enbed_url: continue

        new_embed_url = scrapertools.find_single_match(enbed_url, '"embed_url":"(.*?)"')
        if not new_embed_url: continue

        new_embed_url = new_embed_url.replace('\\/', '/')

        data2 = do_downloadpage(new_embed_url, headers={'Referer': item.url})

        # ~  "Server1" tienen ReCaptcha Invisible, resto de "Servers" son raros y no se tratan
        url = scrapertools.find_single_match(data2, '"Server0":"(.*?)"')
        if not url: continue

        lang = scrapertools.find_single_match(enlace, "/img/flags/(.*?).svg").lower()

        if 'play.php?v=' in url:
            vurl = url.split('play.php?v=')[1]
            if vurl.startswith('//'): vurl = 'https:' + vurl
            servidor = servertools.get_server_from_url(vurl)

            if servidor and servidor != 'directo':
                vurl = servertools.normalize_url(servidor, vurl)
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = vurl, language = IDIOMAS.get(lang, lang) ))

        else:
            data3 = do_downloadpage(url, headers={'Referer': host})
            dom = '/'.join(url.split('/')[:3])

            links = scrapertools.find_multiple_matches(data3, '<li(?: id="servers"|) onclick(.*?)</li>')

            i_lang = 0

            for lnk in links:
                i_lang += 1

                vurl = scrapertools.find_single_match(lnk, "go_to_player\('([^']+)")
                if not vurl: continue

                lang2 = scrapertools.find_single_match(str(links), ".*?'" + str(i_lang) + ".*?/assets/player/lang/(.*?).png").lower()

                if lang2: lang = lang2

                vurl = vurl.replace('https://go.megaplay.cc/index.php?h=', '/playerdir/')
                if '/playerdir/' in vurl: vurl = '/playdir/' + scrapertools.find_single_match(vurl, "/playerdir/([^&]+)")
                if vurl.startswith('/'): vurl = dom + vurl

                servidor = scrapertools.find_single_match(lnk, 'player/server/([^."]+)').lower()
                if not servidor: servidor = scrapertools.find_single_match(lnk, '<span class="serverx">([^<]+)').lower()

                if servidor == 'meplay': continue
                elif servidor == 'stream': continue
                elif servidor == 'descargar':
                     if '&uptobox=' in vurl: servidor = 'uptobox'
                     elif '&mega=' in vurl: servidor = 'mega'
                     else: continue

                if not lang2:
                    lang3 = scrapertools.find_single_match(lnk, "<p>([A-z]+)").lower()
                    if lang3: lang = lang3
                    else:
                       if str(item.languages): lang = str(item.languages)
                       else:
                          if not lang: lang = '?'

                servidor = corregir_servidor(servidor)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = vurl, language = IDIOMAS.get(lang, lang) ))

            if not links:
                links = scrapertools.find_multiple_matches(data3, '<a id="servers"(.*?)</a>')
                for lnk in links:
                    lembed = scrapertools.find_single_match(lnk, 'data-embed="([^"]+)')
                    ltype = scrapertools.find_single_match(lnk, 'data-type="([^"]+)')

                    servidor = scrapertools.find_single_match(lnk, 'title="([^".]+)').lower()
                    if not servidor: servidor = scrapertools.find_single_match(lnk, '<span class="serverx">([^<]+)').lower()

                    if servidor == 'meplay': continue
                    elif servidor == 'stream': continue

                    servidor = corregir_servidor(servidor)

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', referer = url,
                                          lembed = lembed, ltype = ltype, lurl = '/'.join(url.split('/')[:3]), language = IDIOMAS.get(lang, lang) ))

            if not links:
                dom = '/'.join(url.split('/')[:3])
                links = get_sources(data3)
                for lnk in links:
                    if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]

                    itemlist.append(Item( channel = item.channel, action = 'play', server = '', title = '', url = lnk[0], referer = url,
                                          language = IDIOMAS.get(lang, lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

        if not config.get_setting('channel_inkapelis_proxies', default=''):
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Quizás necesite Proxies[/B][/COLOR]')

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    vurl = ''

    if '/go.megaplay.cc/' in item.url or '/gcs.megaplay.cc/' in item.url or '/plays.megaplay.cc' in item.url or '/players.oceanplay.me/' in item.url:
        data = do_downloadpage(item.url)

        try:
            key, value = scrapertools.find_single_match(data, 'name="([^"]+)" value="([^"]+)"')

            if '/go.megaplay.cc/' in item.url: url_post = 'https://go.megaplay.cc/r.php'
            elif '/gcs.megaplay.cc/' in item.url: url_post = 'https://gcs.megaplay.cc/r.php'
            elif '/plays.megaplay.cc' in item.url: url_post = 'https://plays.megaplay.cc/r.php'
            else: url_post = 'https://players.oceanplay.me/r.php'

            # ~ vurl = httptools.downloadpage(url_post, post={key: value}, follow_redirects=False).headers['location']
            vurl = httptools.downloadpage_proxy('repelishd', url_post, post={key: value}, follow_redirects=False).headers['location']

        except:
            vurl = scrapertools.find_single_match(data, 'location.href = "(.*?)"')

    if item.lembed and item.ltype and item.lurl:
        post = {'type': item.ltype, 'streaming': item.lembed}
        data = do_downloadpage(item.lurl + '/edge-data/', post=post, headers={'Referer': item.referer})

        item.url = scrapertools.find_single_match(data, '"url": "([^"]+)')
        if not item.url:
            if data.startswith('http'): item.url = data
            elif data.startswith('/'): item.url = item.lurl + data

        if not item.url:
            return itemlist

        item.url = item.url.replace(embeds + '/fplayer?url=', embeds + '/redirector.php?url=')

    if 'playerd.xyz/' in item.url or embeds in item.url:
        # ~ resp = httptools.downloadpage(item.url, headers={'Referer': item.referer if item.referer else item.url}, follow_redirects=False)
        resp = httptools.downloadpage_proxy('inkapelis', item.url, headers={'Referer': item.referer if item.referer else item.url}, follow_redirects=False)

        if 'refresh' in resp.headers: vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
        elif 'location' in resp.headers: vurl = resp.headers['location']
        else:
            url = scrapertools.find_single_match(resp.data, '<iframe src="([^"]+)')
            if not url: url = scrapertools.find_single_match(resp.data, "window\.open\('([^']+)")
            if not url: url = scrapertools.find_single_match(resp.data, 'location\.href = "([^"]+)')
            if url and url.startswith('/'): url = '/'.join(item.url.split('/')[:3]) + url

            if 'playerd.xyz/' in url or embeds in url:
                url = url.replace('iframe?url=', 'redirect?url=')
                # ~ resp = httptools.downloadpage(url, headers={'Referer': item.url}, follow_redirects=False)
                resp = httptools.downloadpage_proxy('inkapelis', url, headers={'Referer': item.url}, follow_redirects=False)

                if 'refresh' in resp.headers: vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
                elif 'location' in resp.headers: vurl = resp.headers['location']
                else:
                    vurl = scrapertools.find_single_match(resp.data, 'downloadurl = "([^"]+)')
                    if not vurl and 'player.php?id=' in url: vurl = url
            else:
                if url: vurl = url
                else:
                    gk_link = scrapertools.find_single_match(resp.data, 'config_player\.link = "([^"]+)')
                    if gk_link:
                        post = 'link=' + gk_link
                        data = do_downloadpage(players + '/player/plugins/gkpluginsphp.php', post=post)
                        vurl = scrapertools.find_single_match(data, '"link":"([^"]+)').replace('\\/', '/')
                    else:
                        if '/direct/' in item.url:
                            item.url = item.url.replace('/direct/', '/linkd/')
                            url_play = item.url
                        else:
                            if '/v2/' in item.url: url_play = item.url
                            else: url_play = players + '/playdir/' + item.url

                        url_play = url_play.split('&')[0]

                        data = do_downloadpage(url_play, headers={'Referer': url_play})

                        url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
                        if not url: url = scrapertools.find_single_match(data, 'action="(.*?)"')

                        if not url:
                            if 'action="r.php"' in data:
                                hash = scrapertools.find_single_match(data, 'value="(.*?)"')
                                post = {'h': hash}

                                try:
                                    # ~ url = httptools.downloadpage(_player + 'r.php', post = post, headers={'Referer': item.url}, follow_redirects = False, only_headers = True, raise_weberror=False).headers.get('location', '')
                                    url = httptools.downloadpage_proxy('inkapelis', _player + 'r.php', post = post, headers={'Referer': item.url}, follow_redirects = False, only_headers = True, raise_weberror=False).headers.get('location', '')
                                except:
                                    url = ''
                        if not url:
                            try:
                               # ~ url = httptools.downloadpage(url_play, headers={'Referer': url_play}, follow_redirects=False).headers['location']
                               url = httptools.downloadpage_proxy('inkapelis', url_play, headers={'Referer': url_play}, follow_redirects=False).headers['location']
                            except:
                               url = ''

                        if url == 'https://URL/NONE/':
                            url = ''
                            if item.server == 'uqload':
                                code = scrapertools.find_single_match(data, 'file_code=(.*?)&hash')
                                if code: url = 'https://uqload.com/embed-' + code + '.html'

                        if url: vurl = url
                        else:
                            vurl = None
                            dom = '/'.join(item.url.split('/')[:3])
                            links = get_sources(resp.data)

                            for lnk in links:
                                if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]
                                if lnk[1] == 'hls': itemlist.append(item.clone(url = lnk[0], server = 'm3u8hls'))
                                else: itemlist.append([lnk[2], lnk[0]])

        if vurl and vurl.startswith('/'): vurl = '/'.join(item.url.split('/')[:3]) + vurl

    elif item.url.startswith('http'):
        vurl = item.url

    if vurl and '/playdir' in vurl:
        # ~ resp = httptools.downloadpage(vurl, headers={'Referer': item.url}, follow_redirects=False)
        resp = httptools.downloadpage_proxy('inkapelis', vurl, headers={'Referer': item.url}, follow_redirects=False)

        if 'refresh' in resp.headers: vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
        elif 'location' in resp.headers: vurl = resp.headers['location']
        else: vurl = None

    if vurl:
        if 'player.php?id=' in vurl:
            # ~ resp = httptools.downloadpage(vurl, headers={'Referer': item.url}, follow_redirects=False)
            resp = httptools.downloadpage_proxy('inkapelis', vurl, headers={'Referer': item.url}, follow_redirects=False)

            dom = '/'.join(vurl.split('/')[:3])
            links = get_sources(resp.data)

            for lnk in links:
                if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]
                if lnk[1] == 'hls': itemlist.append(item.clone(url = lnk[0], server = 'm3u8hls'))
                else: itemlist.append([lnk[2], lnk[0]])

            vurl = None

        elif 'index.php?h=' in vurl:
            hash = scrapertools.find_single_match(vurl, 'h=(.*?)&')
            post = {'h': hash}

            try:
                # ~ vurl = httptools.downloadpage(_player + 'r.php', post = post, headers={'Referer': item.url}, follow_redirects = False, only_headers = True, raise_weberror=False).headers.get('location', '')
                vurl = httptools.downloadpage_proxy('inkapelis', _player + 'r.php', post = post, headers={'Referer': item.url}, follow_redirects = False, only_headers = True, raise_weberror=False).headers.get('location', '')
            except:
                vurl = ''

    if vurl:
        if '/hqq.' in vurl or '/waaw.' in vurl or '/netu.' in vurl:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(vurl)
        servidor = servertools.corregir_servidor(servidor)

        if item.server == 'uptobox':
            if not servidor == 'uptobox':
                return 'Servidor erróneo [COLOR plum]No es Uptobox[/COLOR]'

        if servidor == 'zplayer':
            player = 'https://player.' + embeds + '/'
            vurl = vurl + '|' + player

        if servidor and (servidor != 'directo' or 'googleapis.com' in vurl):
            url = servertools.normalize_url(servidor, vurl)
            itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def get_sources(data):
    srcs = []

    bloque = scrapertools.find_single_match(data, '(?:"|)sources(?:"|):\s*\[(.*?)\]')

    for enlace in scrapertools.find_multiple_matches(bloque, "\{(.*?)\}"):
        v_url = scrapertools.find_single_match(enlace, '(?:"|)file(?:"|):\s*"([^"]+)')
        if not v_url: continue

        v_type = scrapertools.find_single_match(enlace, '(?:"|)type(?:"|):\s*"([^"]+)')
        v_lbl = scrapertools.find_single_match(enlace, '(?:"|)label(?:"|):\s*"([^"]+)')
        if not v_lbl: v_lbl = 'mp4'
        srcs.append([v_url, v_type, v_lbl])

    return srcs


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
