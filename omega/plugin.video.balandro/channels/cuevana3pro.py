# -*- coding: utf-8 -*-

import ast, re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


from lib.pyberishaes import GibberishAES


host = 'https://tv8.cuevana3.vip'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://wwa3.cuevana3.vip', 'https://wlw.cuevana3.vip', 'https://wlv.cuevana3.vip',
             'https://wli3.cuevana3.vip', 'https://wnv3.cuevana3.vip', 'https://wn3.cuevana3.vip',
             'https://wv3i.cuevana3.vip', 'https://wmi.cuevana3.vip', 'https://wi3v.cuevana3.vip',
             'https://wev3.cuevana3.vip', 'https://wl3n.cuevana3.vip', 'https://cuevana3.vip',
             'https://wiw3.cuevana3.vip', 'https://wmi3.cuevana3.vip', 'https://wn3l.cuevana3.vip', 
             'https://imu.cuevana3.vip', 'https://wni3.cuevana3.vip', 'https://mvi.cuevana3.vip',
             'https://wi3n.cuevana3.vip', 'https://wi3m.cuevana3.vip', 'https://im3.cuevana3.vip',
             'https://iv3.cuevana3.vip', 'https://lm3.cuevana3.vip', 'https://ww3v.cuevana3.vip',
             'https://ww3u.cuevana3.vip', 'https://wl3v.cuevana3.vip', 'https://wv3n.cuevana3.vip',
             'https://wl3r.cuevana3.vip', 'https://me3.cuevana3.vip', 'https://me4.cuevana3.vip',
             'https://mia.cuevana3.vip', 'https://max.cuevana3.vip', 'https://zx1.cuevana3.vip',
             'https://zz.cuevana3.vip', 'https://gx.cuevana3.vip', 'https://tv.cuevana3.vip']


domain = config.get_setting('dominio', 'cuevana3pro', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'cuevana3pro')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'cuevana3pro')
    else: host = domain


perpage = 25

def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_cuevana3pro_proxies', default=''):
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

    hay_proxies = False
    if config.get_setting('channel_cuevana3pro_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('cuevana3pro', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('Cuevana3Pro', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('cuevana3pro', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if not url.startswith(host):
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
        else:
            if hay_proxies:
                data = httptools.downloadpage_proxy('cuevana3pro', url, post=post, headers=headers, timeout=timeout).data
            else:
                data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>Just a moment...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'cuevana3pro', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_cuevana3pro', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='cuevana3pro', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_cuevana3pro', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_cuevana3pro', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('cuevana3pro') ))

    itemlist.append(Item( channel='actions', action='show_old_domains', title='[COLOR coral][B]Historial Dominios[/B][/COLOR]', channel_id = 'cuevana3pro', thumbnail=config.get_thumb('cuevana3pro') ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catalogo', action = 'list_all', url = host + '/series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + '/episodios/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    generos = [
       'accion',
       'action-adventure',
       'animacion',
       'anime',
       'aventura',
       'belica',
       'ciencia-ficcion',
       'comedia',
       'crimen',
       'dc-comics',
       'documental',
       'doramas',
       'drama',
       'familia',
       'fantasia',
       'historia',
       'misterio',
       'musica',
       'pelicula-de-tv',
       'romance',
       'sci-fi-fantasy',
       'suspense',
       'terror',
       'western'
       ]

    for genero in generos:
        url = host + '/category/' + genero + '/'

        itemlist.append(item.clone( title = genero.capitalize(), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if 'Online<' in data:
        bloque = scrapertools.find_single_match(data, 'Online<(.*?)>Unirme')
    else: bloque = data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)
    if not matches: matches = re.compile('id="post-(.*?)</div></div>', re.DOTALL).findall(bloque)

    for article in matches:
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>').strip()
        if not title: title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#039;m', "'m").replace('&#039;s', "'s").replace('&#038;', '&').replace('&#8211;', '').replace('&#8217;s', "'s").replace('&#8217;', '').replace('&#8230;', '').replace('&#039;', "'").replace('&amp;', '').strip()

        thumb = scrapertools.find_single_match(article, 'src="(.*?)"')

        if not 'http' in thumb: thumb = 'https' + thumb

        year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(article, '<span class=Year>(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(article, '<span class="Date">(.*?)</span>').strip()

        if year:
            title = title.replace('(' + year + ')', '').strip()
            c_year = scrapertools.find_single_match(title, '(\d{4})')
            if c_year: title = title.replace('(' + c_year + ')', '').strip()
        else:
            year = scrapertools.find_single_match(title, '(\d{4})')
            if year: title = title.replace('(' + year + ')', '').strip()

        if not year: year = '-'

        tipo = 'tvshow' if '/series/' in url else 'movie'

        if tipo == 'movie':
            if item.search_type == "tvshow": continue

            title = title.replace('Pelicula', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = ''

        if '<div class="pagination">' in data:
            bloque_next = scrapertools.find_single_match(data, '<div class="pagination">(.*?)</nav>')
            next_page = scrapertools.find_single_match(bloque_next, '<span class="current">.*?href="(.*?)"')

        elif '<nav class="navigation pagination">' in data:
            bloque_next = scrapertools.find_single_match(data, '<nav class="navigation pagination">(.*?)</nav>')
            next_page = scrapertools.find_single_match(bloque_next, '<a class="page-link current".*?<a class="page-link".*?</a>.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Ultimos Episodios<(.*?)>Unirme')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>').strip()
        if not title: title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#039;m', "'m").replace('&#039;s', "'s").replace('&#038;', '&').replace('&#8211;', '').replace('&#8217;s', "'s").replace('&#8217;', '').replace('&#8230;', '').replace('&amp;', '').strip()

        thumb = scrapertools.find_single_match(article, 'data-src="(.*?)"')

        if not 'http' in thumb: thumb = 'https' + thumb

        year = scrapertools.find_single_match(title, '(\d{4})').strip()
        SerieName = scrapertools.find_single_match(title, '(.*?)' + year)

        SerieName = SerieName.strip()

        s_t = ''

        if year: s_t = scrapertools.find_single_match(title, year  + '(.*?)$')

        s_t = s_t.replace('(', '').replace(')', '').strip()

        season = scrapertools.find_single_match(s_t, '(.*?)x').strip()
        if not season: season = 1

        epis = scrapertools.find_single_match(s_t, 'x(.*?)$').strip()
        if not epis: epis = 1

        if year: title = title.replace('(' + year + ')', '').strip()

        titulo = '[COLOR goldenrod]Epis. [/COLOR]' + str(season) + 'x' + str(epis) + ' ' + title.replace(str(season) + 'x' + str(epis), '').strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb, infoLabels={'year': '-'},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber=epis))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page = item.page + 1, action='last_epis', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = ''

            if '<div class="pagination">' in data:
                bloque_next = scrapertools.find_single_match(data, '<div class="pagination">(.*?)</nav>')
                next_page = scrapertools.find_single_match(bloque_next, '<span class="current">.*?href="(.*?)"')

            elif '<nav class="navigation pagination">' in data:
                bloque_next = scrapertools.find_single_match(data, '<nav class="navigation pagination">(.*?)</nav>')
                next_page = scrapertools.find_single_match(bloque_next, '<a class="page-link current".*?<a class="page-link".*?</a>.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'last_epis', page = 0, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('data-season="(.*?)"', re.DOTALL).findall(data)
    if not matches: matches = re.compile('<option value="(.*?)"', re.DOTALL).findall(data)

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
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    d_post = scrapertools.find_single_match(data, 'data-post="(.*?)"')

    if d_post:
        post = {'action': 'action_select_season', 'season': str(item.contentSeason), 'post': d_post}

        data = do_downloadpage(host + '/wp-admin/admin-ajax.php', post = post)

    if '<option value="' in data:
        bloque = scrapertools.find_single_match(data, "<ul id=season-" + str(item.contentSeason) + "(.*?)</section>")

        matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)
    else:
        matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('Cuevana3Pro', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Cuevana3Pro', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Pro', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Pro', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Pro', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3Pro', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Cuevana3Pro', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if not 'http' in thumb: thumb = 'https:' + thumb

        epis = scrapertools.find_single_match(match, '<span class="num-epi">.*?x(.*?)</span>')
        if not epis: epis = scrapertools.find_single_match(match, '<h2 class="Title">.*?Episodio(.*?)</h2>').strip()

        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')
        if not title: title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        titulo = str(item.contentSeason) + 'x' + epis + ' ' + title.replace(str(item.contentSeason) + 'x' + epis, '').strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

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

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, 'id="player-option-(.*?)</li>')
    if not matches: matches = scrapertools.find_multiple_matches(data, "id='player-option-(.*?)</li>")

    ses = 0

    for match in matches:
        # ~ dtype, dpost, dnume
        dtype = scrapertools.find_single_match(match, ' data-type="(.*?)"')
        if not dtype: dtype = scrapertools.find_single_match(match, " data-type='(.*?)'")

        dpost = scrapertools.find_single_match(match, ' data-post="(.*?)"')
        if not dpost: dpost = scrapertools.find_single_match(match, " data-post='(.*?)'")

        dnume = scrapertools.find_single_match(match, ' data-nume="(.*?)"')
        if not dnume: dnume = scrapertools.find_single_match(match, " data-nume='(.*?)'")

        if dtype and dpost and dnume:
            data1 = do_downloadpage(host + '/wp-json/dooplayer/v2/' + dpost + '/' + dtype + '/' + dnume +'/')

            embed = scrapertools.find_single_match(str(data1), '"embed_url":.*?"(.*?)"')

            if embed:
                ses += 1

                if not dnume == 'trailer':
                    embed = embed.replace('\\/', '/')

                    if embed.startswith('//'): embed = 'https:' + embed

                    if not '/pelisplay.' in embed:
                        if embed.startswith('//'):embed  = 'https:' + embed

                        servidor = servertools.get_server_from_url(embed)
                        servidor = servertools.corregir_servidor(servidor)

                        embed = servertools.normalize_url(servidor, embed)

                        lang = scrapertools.find_single_match(match, '<span class="title">(.*?)</span>')
                        if not lang: lang = scrapertools.find_single_match(match, "<span class='title'>(.*?)</span>")

                        if 'Latino' in lang: lang = 'Lat'
                        elif 'Castellano' in lang or 'Español' in lang: lang = 'Esp'
                        elif 'Subtitulado' in lang or 'VOSE' in lang or 'Vose' in lang: lang = 'Vose'
                        elif 'Inglés' in lang: lang = 'Vo'
                        else: lang = '?'

                        other = ''
                        if servidor == 'various': other = servertools.corregir_other(embed)

                        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = embed, language = lang, other = other ))
                    else:
                        data2 = do_downloadpage(embed)

                        links = scrapertools.find_multiple_matches(data2, '<li class="linkserver".*?data-video="(.*?)"')
                        if not links: links = scrapertools.find_multiple_matches(data2,"'<li class='linkserver'.*?data-video='(.*?)'")

                        if links:
                            for url in links:
                                ses += 1

                                if '/hydrax.' in url: continue
                                elif '/xupalace.' in url: continue
                                elif '/uploadfox.' in url: continue

                                if url.startswith('//'): url = 'https:' + url

                                servidor = servertools.get_server_from_url(url)
                                servidor = servertools.corregir_servidor(servidor)

                                url = servertools.normalize_url(servidor, url)

                                lang = scrapertools.find_single_match(match, '<span class="title">(.*?)</span>')
                                if not lang: lang = scrapertools.find_single_match(match, "<span class='title'>(.*?)</span>")

                                if 'Latino' in lang: lang = 'Lat'
                                elif 'Castellano' in lang or 'Español' in lang: lang = 'Esp'
                                elif 'Subtitulado' in lang or 'VOSE' in lang or 'Vose' in lang: lang = 'Vose'
                                elif 'Inglés' in lang: lang = 'Vo'
                                else: lang = '?'

                                other = ''
                                if servidor == 'various': other = servertools.corregir_other(url)

                                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

        # ~ iframes
        opt = scrapertools.find_single_match(match, '(.*?)"')

        srv = scrapertools.find_single_match(match, '<span class="server">(.*?)-').strip()
        lng = scrapertools.find_single_match(match, '<span class="server">.*?-(.*?)</span>').strip()

        srv = srv.lower().strip()

        if 'youtube' in srv: continue

        if 'Latino' in lng: lang = 'Lat'
        elif 'Castellano' in lng or 'Español' in lng: lang = 'Esp'
        elif 'Subtitulado' in lng or 'VOSE' in lng or 'Vose' in lng: lang = 'Vose'
        elif 'Inglés' in lng: lang = 'Vo'
        else: lang = '?'

        servidor = servertools.corregir_servidor(srv)

        links = scrapertools.find_multiple_matches(data, '<div id="options-' + opt + '.*?<iframe.*?src="(.*?)"')

        if not links: continue

        for url in links:
            ses += 1

            trembed = url.replace('&#038;', '&').replace('&amp;', '&').replace('#038;', '')

            data3 = do_downloadpage(trembed)

            vid = scrapertools.find_single_match(data3, '<iframe.*?src="([^"]+)')
            if not vid: vid = scrapertools.find_single_match(data3, '<IFRAME.*?SRC="([^"]+)')

            if vid:
                if vid.startswith('//'): vid = 'https:' + vid

                if '/play?' in vid or '/streamhd?' in vid:
                    vid = vid.replace('&#038;', '&').replace('&amp;', '&').replace('#038;', '')

                    data4 = do_downloadpage(vid)

                    vids = scrapertools.find_multiple_matches(data4, 'data-video="(.*?)"')

                    if vids:
                        for url in vids:
                            ses += 1

                            if url:
                                if '/hydrax.' in url: continue
                                elif '/xupalace.' in url: continue
                                elif '/uploadfox' in url: continue

                                if url.startswith('//'): url = 'https:' + url

                                servidor = servertools.get_server_from_url(url)
                                servidor = servertools.corregir_servidor(servidor)

                                url = servertools.normalize_url(servidor, url)

                                other = ''
                                if servidor == 'various': other = servertools.corregir_other(url)

                                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

                    embed = scrapertools.find_single_match(str(data), "sources:.*?'(.*?)'")

                    if embed:
                        ses += 1

                        if embed.startswith('//'): embed = 'https:' + embed

                        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = embed, language = lang ))

                else:
                    url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
                    if not url: url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="([^"]+)')

                    if url:
                        ses += 1

                        if '/hydrax.' in url: continue
                        elif '/xupalace.' in url: continue
                        elif '/uploadfox.' in url: continue

                        elif '/media.esplay.one' in url: continue

                        if url.startswith('//'): url = 'https:' + url

                        servidor = servertools.get_server_from_url(url)
                        servidor = servertools.corregir_servidor(servidor)

                        url = servertools.normalize_url(servidor, url)

                        other = ''
                        if servidor == 'various': other = servertools.corregir_other(url)

                        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

            else:
                other = srv

                if servidor == srv: other = ''
                elif not servidor == 'directo':
                   if not servidor == 'various': other = ''

                if url.startswith('//'): url = 'https:' + url

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other.capitalize() ))

    # ~ iframes 2do
    matches1 = scrapertools.find_multiple_matches(data, '<iframe src="(.*?)"')
    matches2 = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    matches = matches1 + matches1

    for url in matches:
        if not url: continue

        ses += 1

        url = url.replace('&#038;', '&').replace('&amp;', '&').replace('#038;', '')

        if 'Latino' in data: lang = 'Lat'
        elif 'Castellano' in data or 'Español' in data: lang = 'Esp'
        elif 'Subtitulado' in data or 'VOSE' in data or 'Vose' in data: lang = 'Vose'
        elif 'Inglés' in data: lang = 'Vo'
        else: lang = '?'

        data5 = do_downloadpage(url)

        matches5 = scrapertools.find_multiple_matches(data5, '<iframe.*?src="(.*?)"')

        for match in matches5:
            if match.startswith('//'): match = 'https:' + match

            data6 = do_downloadpage(match)

            links = scrapertools.find_multiple_matches(data6, '<li class="linkserver".*?data-video="(.*?)"')

            if links:
                for url in links:
                    if '/hydrax.' in url: continue
                    elif '/xupalace.' in url: continue
                    elif '/uploadfox.' in url: continue

                    if url.startswith('//'): url = 'https:' + url

                    servidor = servertools.get_server_from_url(url)
                    servidor = servertools.corregir_servidor(servidor)

                    url = servertools.normalize_url(servidor, url)

                    other = ''
                    if servidor == 'various': other = servertools.corregir_other(url)

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

                continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    # ~ iframes data-src
    matches = scrapertools.find_multiple_matches(data, '<iframe.*?data-src="(.*?)"')

    for match in matches:
        lang = '?'

        if '//embed69.' in match:
            ses += 1

            datae = do_downloadpage(match)

            dataLink = scrapertools.find_single_match(datae, 'const dataLink =(.*?);')
            if not dataLink: dataLink = scrapertools.find_single_match(datae, 'dataLink(.*?);')

            e_bytes = scrapertools.find_single_match(datae, "const bytes =.*?'(.*?)'")
            if not e_bytes: e_bytes = scrapertools.find_single_match(datae, "encrypted.*?'(.*?)'")

            e_links = dataLink.replace(']},', '"type":"file"').replace(']}]', '"type":"file"')

            langs = scrapertools.find_multiple_matches(str(e_links), '"video_language":(.*?)"type":"file"')

            for lang in langs:
                ses += 1

                lang = lang + '"type":"video"'

                links = scrapertools.find_multiple_matches(str(lang), '"servername":"(.*?)","link":"(.*?)".*?"type":"video"')

                if 'SUB' in lang: lang = 'Vose'
                elif 'LAT' in lang: lang = 'Lat'
                elif 'ESP' in lang: lang = 'Esp'
                else: lang = '?'

                for srv, link in links:
                    ses += 1

                    srv = srv.lower().strip()

                    if not srv: continue
                    elif host in link: continue

                    elif '1fichier.' in srv: continue
                    elif 'plustream' in srv: continue
                    elif 'embedsito' in srv: continue
                    elif 'disable2' in srv: continue
                    elif 'disable' in srv: continue
                    elif 'xupalace' in srv: continue
                    elif 'uploadfox' in srv: continue

                    elif srv == 'download': continue

                    servidor = servertools.corregir_servidor(srv)

                    if servertools.is_server_available(servidor):
                        if not servertools.is_server_enabled(servidor): continue
                    else:
                        if not config.get_setting('developer_mode', default=False): continue

                    other = ''

                    if servidor == 'various': other = servertools.corregir_other(srv)

                    if servidor == 'directo':
                        if not config.get_setting('developer_mode', default=False): continue
                        else:
                           other = url.split("/")[2]
                           other = other.replace('https:', '').strip()

                    itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = '', crypto=link, bytes=e_bytes,
                                          language=lang, other=other ))

        elif '/xupalace.' in match:
            ses += 1

            if 'php?id=' in match:
                datax = do_downloadpage(match)

                url = scrapertools.find_single_match(datax, '<iframe src="(.*?)"')

                if url:
                    servidor = servertools.get_server_from_url(url)
                    servidor = servertools.corregir_servidor(servidor)

                    if servertools.is_server_available(servidor):
                        if not servertools.is_server_enabled(servidor): continue
                    else:
                        if not config.get_setting('developer_mode', default=False): continue

                    url = servertools.normalize_url(servidor, url)

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url=url, language=lang, other=other ))

                continue

            elif '/video/' in match:
                datax = do_downloadpage(match)

                matchesx = scrapertools.find_multiple_matches(datax, "go_to_playerVast.*?'(.*?)'")

                for matchx in matchesx:
                    if '/embedsito.' in matchx: continue
                    elif '/player-cdn.' in matchx: continue
                    elif '/1fichier.' in matchx: continue
                    elif '/hydrax.' in matchx: continue
                    elif '/xupalace.' in matchx: continue
                    elif '/uploadfox.' in matchx: continue

                    servidor = servertools.get_server_from_url(matchx)
                    servidor = servertools.corregir_servidor(servidor)

                    if servertools.is_server_available(servidor):
                        if not servertools.is_server_enabled(servidor): continue
                    else:
                        if not config.get_setting('developer_mode', default=False): continue

                    url = servertools.normalize_url(servidor, matchx)

                    other = ''
                    if servidor == 'various': other = servertools.corregir_other(url)

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url=url, language=lang, other=other ))

                continue

            else: continue

    # ~ data servers
    match = scrapertools.find_single_match(data, 'data-server="(.*?)"')

    if match:
        ses += 1

        datam = do_downloadpage(match)

        d_links = scrapertools.find_single_match(datam, 'const dataLink =(.*?);')
        d_bytes = scrapertools.find_single_match(datam, "const bytes =.*?'(.*?)'")

        if d_links:
            ses += 1

            data = datam

            langs = scrapertools.find_multiple_matches(str(d_links), '"video_language":(.*?)"type":"file"')

            for lang in langs:
                ses += 1

                lang = lang + '"type":"video"'

                links = scrapertools.find_multiple_matches(str(lang), '"servername":"(.*?)","link":"(.*?)".*?"type":"video"')

                if 'SUB' in lang: lang = 'Vose'
                elif 'LAT' in lang: lang = 'Lat'
                elif 'ESP' in lang: lang = 'Esp'
                else: lang = '?'

                for srv, link in links:
                    ses += 1

                    srv = srv.lower().strip()

                    if not srv: continue
                    elif srv == '#': continue

                    elif host in link: continue

                    elif 'fembed' in srv: continue
                    elif 'streamsb' in srv: continue
                    elif 'playersb' in srv: continue
                    elif 'sbembed' in srv: continue

                    elif 'player-cdn' in srv: continue

                    elif '1fichier.' in srv: continue
                    elif 'short' in srv: continue
                    elif 'plustream' in srv: continue
                    elif 'disable2' in srv: continue
                    elif 'disable' in srv: continue
                    elif 'embedsito' in srv: continue
                    elif 'xupalace' in srv: continue
                    elif 'uploadfox' in srv: continue

                    servidor = servertools.corregir_servidor(srv)

                    if servertools.is_server_available(servidor):
                        if not servertools.is_server_enabled(servidor): continue
                    else:
                        if not config.get_setting('developer_mode', default=False): continue

                    other = ''

                    if servidor == 'various': other = servertools.corregir_other(srv)

                    if servidor == 'directo':
                        if not config.get_setting('developer_mode', default=False): continue
                        else:
                            other = url.split("/")[2]
                            other = other.replace('https:', '').strip()

                    itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = '', crypto=link, bytes=d_bytes,
                                          language=lang, other=other ))


    matches = scrapertools.find_multiple_matches(data, 'onclick="go_to_player.*?' + "'(.*?)'")
    if not matches: matches = scrapertools.find_multiple_matches(data, 'onclick="go_to_player.*?' + "'(.*?)'")

    langs = []
    if 'data-lang="1"' in data: langs.append('Esp')
    if 'data-lang="0"' in data: langs.append('Lat')
    if 'data-lang="2"' in data: langs = langs.append('Vose')

    if ',' in str(langs): lang = ",".join(langs)
    else: lang = str(langs).replace('[', '').replace("'", '').replace(']', '').strip()

    if not langs: lang = '?'

    for url in matches:
        ses += 1

        if not url: continue

        elif 'player-cdn' in url: continue

        elif '/1fichier.' in url: continue
        elif '/short.' in url: continue
        elif '/plustream.' in url: continue
        elif 'embedsito' in url: continue
        elif 'disable2' in url: continue
        elif 'disable' in url: continue
        elif 'xupalace' in url: continue
        elif 'uploadfox' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        elif servidor == 'filemooon':
            servidor = 'filemoon'
            url = url.replace('filemooon', 'filemoon')

        elif servidor == 'netu': servidor = 'waaw'

        itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&#038;', '&').replace('&amp;', '&').replace('#038;', '')

    if item.crypto:
        crypto = str(item.crypto)
        bytes = str(item.bytes)

        try:
            cripto = ast.literal_eval(cripto)
        except:
            crypto = str(item.crypto)

        try:
            url = GibberishAES.dec(GibberishAES(), string = crypto, pass_ = bytes)
        except:
            url = ''

        if not url:
            return '[COLOR cyan]No se pudo [COLOR red]Desencriptar[/COLOR]'

    elif item.server == 'directo':
        item.url = url

        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
        if not url: url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="([^"]+)')

        if not url:
            if '/hydrax.' in data or '/xupalace.' in data or '/uploadfox.' in data:
                return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'
            return itemlist

        if '/pelisplay.' in url: url = ''

        if url:
            if '/hydrax.' in url or '/xupalace.' in url or '/uploadfox.' in url:
                return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor == 'directo':
                new_server = servertools.corregir_other(url).lower()
                if new_server.startswith("http"): servidor = new_server

            itemlist.append(item.clone(server = servidor, url = url))

        return itemlist

    if url:
        if '/hydrax.' in url or '/xupalace.' in url or '/uploadfox.' in url:
            return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

    itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '</h1>' in data:
         bloque = scrapertools.find_single_match(data,'</h1>(.*?)<div class="copy"')
         if not bloque: bloque = scrapertools.find_single_match(data,'</h1>(.*?)<p class="copy">')

    elif 'Online<' in data:
        bloque = scrapertools.find_single_match(data, '>Búsquedas(.*?)>Unirme')

    else: bloque = data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)
    if not matches: matches = re.compile('id="post-(.*?)</div></div>', re.DOTALL).findall(bloque)

    for article in matches:
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>').strip()
        if not title: title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#039;m', "'m").replace('&#039;s', "'s").replace('&#038;', '&').replace('&#8211;', '').replace('&#8217;s', "'s").replace('&#8217;', '').replace('&amp;', '').strip()

        thumb = scrapertools.find_single_match(article, 'src="(.*?)"')

        year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(article, '<span class=Year>(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(article, '<span class="Date">(.*?)</span>').strip()

        if year:
            title = title.replace('(' + year + ')' , '').strip()
            c_year = scrapertools.find_single_match(title, '(\d{4})')
            if c_year: title = title.replace('(' + c_year + ')', '').strip()
        else: year ='-'

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            title = title.replace('Pelicula', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = ''

        if '<div class="pagination">' in data:
            bloque_next = scrapertools.find_single_match(data, '<div class="pagination">(.*?)</nav>')
            next_page = scrapertools.find_single_match(bloque_next, '<span class="current">.*?.*?href="(.*?)"')

        elif '<nav class="navigation pagination">' in data:
            bloque_next = scrapertools.find_single_match(data, '<nav class="navigation pagination">(.*?)</nav>')
            next_page = scrapertools.find_single_match(bloque_next, '<a class="page-link current".*?<a class="page-link".*?</a>.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_search', text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()

    try:
        item.url = host + '/?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
