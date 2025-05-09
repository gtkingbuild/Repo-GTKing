# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ennovelas.pro/'


IDIOMAS = {'Latino': 'Lat', 'mx': 'Lat', 'Español': 'Esp', 'es': 'Esp', 'Spanish': 'Esp', 'en': 'Esp', 'English': 'Vose'}


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_masnovelas_proxies', default=''):
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
    raise_weberror = True
    if '/?years=' in url: raise_weberror = False

    hay_proxies = False
    if config.get_setting('channel_masnovelas_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('masnovelas', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if not data or '<title>Checking your browser before accessing. Just a moment...</title>' in data or '<title>405 Not Allowed</title>' in data:
        if not '/?s=' in url:
            if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('MasNovelas', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

            timeout = config.get_setting('channels_repeat', default=30)

            if hay_proxies:
                data = httptools.downloadpage_proxy('masnovelas', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
            else:
                data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

            if not data or '<title>Checking your browser before accessing. Just a moment...</title>' in data or '<title>405 Not Allowed</title>' in data:
                if not '/?years=' in url:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('masnovelas', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data or 'Just a moment...</title>' in data:
        if not url.startswith(host):
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
        else:
            if hay_proxies:
                data = httptools.downloadpage_proxy('masnovelas', url, post=post, headers=headers, raise_weberror=raise_weberror).data
            else:
                data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>Just a moment...</title>' in data or 'Just a moment...</title>' in data:
        if not '/?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='masnovelas', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    itemlist.append(Item( channel='helper', action='show_help_masnovelas', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('masnovelas') ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movie/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tv_shows/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por país', action='paises', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?<span class="elementor-icon-list-text">(.*?)</span>')

    for url, tit in matches:
        if '?orderby=' in url: continue

        if url == '#': continue

        tit = tit.strip()

        if tit == 'Actions': tit = 'Action'
        elif tit == 'Hisroty': tit = 'History'

        if item.search_type == 'tvshow': url = url.replace('/movies_cat/', '/tv_shows_cat/')

        itemlist.append(item.clone( title=tit, url= url, action = 'list_all', text_color = text_color ))

    if itemlist:
        if item.search_type == 'movie':
             itemlist.append(item.clone( title='Acción', url= host + 'movies_cat/accion/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Animación', url= host + 'movies_cat/animacion/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Aventura', url= host + 'movies_cat/aventura/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Bélica', url= host + 'movies_cat/belica/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Ciencia Ficción', url= host + 'movies_cat/ciencia-ficcion/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Comedia', url= host + 'movies_cat/comedia/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Crime', url= host + 'movies_cat/crime/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Crimen', url= host + 'movies_cat/crimen/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Documental', url= host + 'movies_cat/documental/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Documentary', url= host + 'movies_cat/documentary/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Familia', url= host + 'movies_cat/familia/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Fantasía', url= host + 'movies_cat/fantasia/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Historia', url= host + 'movies_cat/historia/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Misterio', url= host + 'movies_cat/misterio/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Música', url= host + 'movies_cat/musica/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Película de TV', url= host + 'movies_cat/pelicula-de-tv/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Suspense', url= host + 'movies_cat/suspense/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Terror', url= host + 'movies_cat/terror/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='War', url= host + 'movies_cat/war/', action = 'list_all', text_color = text_color ))
        else:
             itemlist.append(item.clone( title='Acción', url= host + 'tv_shows_cat/accion/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Animación', url= host + 'tv_shows_cat/animacion/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Aventura', url= host + 'tv_shows_cat/aventura/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Bélica', url= host + 'tv_shows_cat/belica/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Ciencia Ficción', url= host + 'tv_shows_cat/ciencia-ficcion/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Comedia', url= host + 'tv_shows_cat/comedia/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Crime', url= host + 'tv_shows_cat/crime/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Crimen', url= host + 'tv_shows_cat/crimen/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Documental', url= host + 'tv_shows_cat/documental/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Documentary', url= host + 'tv_shows_cat/documentary/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Familia', url= host + 'tv_shows_cat/familia/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Fantasía', url= host + 'tv_shows_cat/fantasia/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Historia', url= host + 'tv_shows_cat/historia/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Misterio', url= host + 'tv_shows_cat/misterio/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Música', url= host + 'tv_shows_cat/musica/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Película de TV', url= host + 'tv_shows_cat/pelicula-de-tv/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Suspense', url= host + 'tv_shows_cat/suspense/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='Terror', url= host + 'tv_shows_cat/terror/', action = 'list_all', text_color = text_color ))
             itemlist.append(item.clone( title='War', url= host + 'tv_shows_cat/war/', action = 'list_all', text_color = text_color ))

    return sorted(itemlist, key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        if item.search_type == 'movie': url = host + 'movie/?years='
        else: url = url = host + 'tv_shows/?years='

        url = url + str(x)

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    text_color = 'hotpink'

    itemlist.append(item.clone( title = 'Argentina', action = 'list_all', url = host + 'tv_shows_cat/novelas-argentinas/', text_color=text_color ))
    itemlist.append(item.clone( title = 'Colombia', action = 'list_all', url = host + 'tv_shows_cat/novelas-colombianas/', text_color=text_color ))
    itemlist.append(item.clone( title = 'México', action = 'list_all', url = host + 'tv_shows_cat/novelas-mexicanas', text_color=text_color ))
    itemlist.append(item.clone( title = 'Tuquía', action = 'list_all', url = host + 'tv_shows_cat/series-turcas/', text_color=text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<span>Filters</span>(.*?)>Copyright')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="post-media">(.*?)</div></div></div>')

    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<a class="video-detail"(.*?)</div><div><label>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<a class="videos-play (.*?)</h6>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<a href=.*?">(.*?)</a>').strip()
        if not title: title = scrapertools.find_single_match(match, "alt='(.*?)'").strip()

        if '<img class=' in title: title = scrapertools.find_single_match(match, '<h5 class="video_title">.*?<a href=.*?">(.*?)</a>').strip()

        if not url or not title: continue

        title = title.replace('&#8211;', "").replace('&#8220;', "").replace('&#8221;', "").strip()
        title = title.replace('&#8216;', "").replace('&#8217;', "").replace('&#8230;', "").strip()
        title = title.replace('&#038;', '&').replace('&amp;', '&')

        thumb = scrapertools.find_single_match(match, ' src=(.*?)>').strip()

        year = scrapertools.find_single_match(match, '<div class="video-years">(.*?)</div>')
        if year: title = title.replace('(' + year +')', '').strip()
        else: year = ''

        if '/?years=' in item.url: year = scrapertools.find_single_match(item.url, "/?years=(.*?)$")

        lang = scrapertools.find_single_match(match, '<label>Language:</label>(.*?)$')

        if '</div>' in lang: lang = scrapertools.find_single_match(lang, '(.*?)</div>').strip()

        lang = IDIOMAS.get(lang, lang)

        SerieName = title

        if "(En Español)" in SerieName: SerieName = SerieName.split("(En Español)")[0]

        SerieName = SerieName.strip()

        tipo = 'movie' if '/movie/' in url else 'tvshow'

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang,
                                        contentType = 'movie', contentTitle = SerieName, infoLabels={'year': year} ))

        if tipo == 'tvshow':			
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, languages=lang,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="jws-pagination-number">.*?class="page-numbers current">.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    post_id = scrapertools.find_single_match(data, 'data-post-id="(.*?)"')

    if not post_id: return itemlist

    matches = re.compile('data-index="(.*?)".*?data-value="Season(.*?)"', re.DOTALL).findall(data)

    for d_index, tempo in matches:
        tempo = tempo.strip()

        title = 'Temporada ' + tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.post_id = post_id
            item.d_index = d_index
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, post_id = post_id, d_index = d_index, page = 0,
                                    contentType = 'season', contentSeason = tempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    if not item.post_id or not item.d_index: return itemlist

    post = {'action': 'jws_load_season', 'id': item.post_id, 'season': item.d_index}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = data.replace('=\\', '=').replace('\\"', '/"')

    data = data.replace('\\r\\n \\r\\n \\r\\n', '</fin>')

    matches = re.compile('<div class="post-media(.*?)</fin>', re.DOTALL).findall(data)

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
                platformtools.dialog_notification('MasNovelas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('MasNovelas', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MasNovelas', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MasNovelas', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MasNovelas', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MasNovelas', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('MasNovelas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h6.*?<a href=.*?">(.*?)h6>').strip()

        if '<\/a><\/' in title: title = title.replace('<\/a><\/', '').strip()

        if not url or not title: continue

        url = url.replace('\\/', '/').replace('\/', '/')

        if not 'http' in url: url = 'https:' + url

        title = clean_title(title)

        title = title.replace('&#8211;', "").replace('&#8220;', "").replace('&#8221;', "").strip()
        title = title.replace('&#8216;', "").replace('&#8217;', "").replace('&#8230;', "").strip()
        title = title.replace('&#038;', '&').replace('&amp;', '&')

        season = item.contentSeason
        c_season = scrapertools.find_single_match(url, '-temporada-(.*?)-')
        if c_season:
            if not c_season == season: season = c_season
	
        epis = scrapertools.find_single_match(url, '-capitulo-(.*?)-')
        if not epis: epis = scrapertools.find_single_match(url, '-capitulo-(.*?)/')

        if not epis: epis = scrapertools.find_single_match(match, '<span class="episodes-number.*?E(.*?)<')

        if not epis or epis == 'completo': epis = 1

        thumb = scrapertools.find_single_match(match, ' src=(.*?)>').strip()
        thumb = thumb.replace('\\/', '/')

        title = title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]')

        title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Epis.[/COLOR]')

        titulo = str(season) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    player_id = scrapertools.find_single_match(data, 'data-playerid="(.*?)"')

    if not player_id: return itemlist

    lang = item.languages

    if not lang: lang = '?'

    headers = {'Referer': item.url}

    enlaces = scrapertools.find_multiple_matches(data, 'data-index="(.*?)"')

    ses = 0

    for d_index in enlaces:
        ses += 1

        post = {'action': 'jws_ajax_sources', 'id': player_id, 'index': d_index}

        data1 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)

        if '<IFRAME' in data1 or '<iframe' in data1:
            data1 = data1.replace('=\\', '=').replace('\\"', '/"')

        url = scrapertools.find_single_match(str(data1), ' src="(.*?)"')

        if url:
            url = url.replace('\\/', '/')

            if not 'http' in url: url = 'https:' + url

            if '.disney.' in url: continue
            elif '/short.' in url: continue

            if 'api.mycdn.moe/uqlink.php?id=' in url: url = url.replace('api.mycdn.moe/uqlink.php?id=', 'uqload.com/embed-')

            elif 'api.mycdn.moe/dourl.php?id=' in url: url = url.replace('api.mycdn.moe/dourl.php?id=', 'dood.to/e/')

            elif 'api.mycdn.moe/dl/?uptobox=' in url: url = url.replace('api.mycdn.moe/dl/?uptobox=', 'uptobox.com/')

            elif url.startswith('http://vidmoly/'): url = url.replace('http://vidmoly/w/', 'https://vidmoly/embed-').replace('http://vidmoly/', 'https://vidmoly/')

            elif url.startswith('https://sr.ennovelas.net/'): url = url.replace('/sr.ennovelas.net/', '/waaw.to/')
            elif url.startswith('https://video.ennovelas.net/'): url = url.replace('/video.ennovelas.net/', '/waaw.to/')
            elif url.startswith('https://reproductor.telenovelas-turcas.com.es/'): url = url.replace('/reproductor.telenovelas-turcas.com.es/', '/waaw.to/')
            elif url.startswith('https://novelas360.cyou/player/'): url = url.replace('/novelas360.cyou/player/', '/waaw.to/')
            elif url.startswith('https://novelas360.cyou/'): url = url.replace('/novelas360.cyou/', '/waaw.to/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other))

    # ~ iframes
    matches = scrapertools.find_multiple_matches(data, '<iframe src="(.*?)"')

    for url in matches:
        ses += 1

        if url:
            url = url.replace('\\/', '/')

            if not 'http' in url: url = 'https:' + url

            if '.disney.' in url: continue
            elif '/short.' in url: continue

            if 'api.mycdn.moe/uqlink.php?id=' in url: url = url.replace('api.mycdn.moe/uqlink.php?id=', 'uqload.com/embed-')

            elif 'api.mycdn.moe/dourl.php?id=' in url: url = url.replace('api.mycdn.moe/dourl.php?id=', 'dood.to/e/')

            elif 'api.mycdn.moe/dl/?uptobox=' in url: url = url.replace('api.mycdn.moe/dl/?uptobox=', 'uptobox.com/')

            elif url.startswith('http://vidmoly/'): url = url.replace('http://vidmoly/w/', 'https://vidmoly/embed-').replace('http://vidmoly/', 'https://vidmoly/')

            elif url.startswith('https://sr.ennovelas.net/'): url = url.replace('/sr.ennovelas.net/', '/waaw.to/')
            elif url.startswith('https://video.ennovelas.net/'): url = url.replace('/video.ennovelas.net/', '/waaw.to/')
            elif url.startswith('https://reproductor.telenovelas-turcas.com.es/'): url = url.replace('/reproductor.telenovelas-turcas.com.es/', '/waaw.to/')
            elif url.startswith('https://novelas360.cyou/player/'): url = url.replace('/novelas360.cyou/player/', '/waaw.to/')
            elif url.startswith('https://novelas360.cyou/'): url = url.replace('/novelas360.cyou/', '/waaw.to/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def clean_title(title):
    logger.info()

    title = title.replace('\\u00e1', 'a').replace('\\u00c1', 'a').replace('\\u00e9', 'e').replace('\\u00ed', 'i').replace('\\u00f3', 'o').replace('\\u00fa', 'u')
    title = title.replace('\\u00f1', 'ñ').replace('\\u00bf', '¿').replace('\\u00a1', '¡').replace('\\u00ba', 'º')
    title = title.replace('\\u00eda', 'a').replace('\\u00f3n', 'o').replace('\\u00fal', 'u').replace('\\u00e0', 'a')
    title = title.replace('\\u014d', 'o')

    title = title.replace('\\u00a0', ' ')

    return title


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url, post = item.post)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Search results for:(.*?)>Copyright')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="post-media">(.*?)</div></div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if '/must-watch-' in url: continue
        elif '/best-movies-' in url: continue

        title = scrapertools.find_single_match(match, '<h4 class="entry-title">.*?<a href=.*?">(.*?)</a>').strip()
        if not title: title = scrapertools.find_single_match(match, "alt='(.*?)'").strip()

        if '<img class=' in title: title = scrapertools.find_single_match(match, '<h5 class="video_title">.*?<a href=.*?">(.*?)</a>').strip()

        if not url or not title: continue

        title = title.replace('&#8211;', "").replace('&#8220;', "").replace('&#8221;', "").strip()
        title = title.replace('&#8216;', "").replace('&#8217;', "").replace('&#8230;', "").strip()
        title = title.replace('&#038;', '&').replace('&amp;', '&')

        thumb = scrapertools.find_single_match(match, ' src=(.*?)>').strip()

        SerieName = title

        if "(En Español)" in SerieName: SerieName = SerieName.split("(En Español)")[0]

        SerieName = SerieName.strip()

        tipo = 'movie' if '/movie/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = SerieName, infoLabels={'year': '-'} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="jws-pagination-number">.*?class="page-numbers current">.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_search', text_color = 'coral' ))

    return itemlist


def search(item, texto):
    logger.info()

    itemlist1 = []
    itemlist2 = []

    try:
       if item.search_type == "movie":
           item.url = host + '?s=' + texto.replace(" ", "+")
           item.post = {'action': 'jws_ajax_search', 'post_type': 'movies'}
           return list_search(item)

       elif item.search_type == "tvshow":
           item.url = host + '?s=' + texto.replace(" ", "+")
           item.post = {'action': 'jws_ajax_search', 'post_type': 'tv_shows'}
           return list_search(item)
	
       else:
           item.url = host + '?s=' + texto.replace(" ", "+")
           item.post = {'action': 'jws_ajax_search', 'post_type': 'movies'}
           itemlist1 = list_search(item)

           item.url = host + '?s=' + texto.replace(" ", "+")
           item.post = {'action': 'jws_ajax_search', 'post_type': 'tv_shows'}
           itemlist2 = list_search(item)

           return itemlist1 + itemlist2
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

