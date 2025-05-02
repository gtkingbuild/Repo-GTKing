# -*- coding: utf-8 -*-

import ast, re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


from lib.pyberishaes import GibberishAES


host = 'https://app.pelisgratishd.life/'


perpage = 35


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_pgratishd_proxies', default=''):
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
    ant_hosts = ['https://www.pelisgratishd.life/', 'https://www.pelisgratishd.xyz/', 'https://ver.pelisgratishd.life/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    hay_proxies = False
    if config.get_setting('channelpgratishd__proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('pgratishd', url, post=post, headers=headers).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers).data

        if not data:
            if not '/search/' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('PGratisHd', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('pgratishd', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>Just a moment...</title>' in data:
        if not '/search/' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='pgratishd', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_pgratishd', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('pgratishd') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Colecciones', action = 'colecciones', search_type = 'all', text_color = 'moccasin' ))

    if config.get_setting('mnu_doramas', default=False):
        itemlist.append(item.clone( title = 'Doramas', action = 'list_col', url = host + 'scroll/coleccion/doramas-90?filter=null&page=1', search_type = 'all', text_color = 'firebrick' ))

    if not config.get_setting('descartar_anime', default=False):
        itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host + 'peliculas?filter={"sorting":"released"}', search_type = 'movie', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'peliculas?filter={"sorting":"popular"}', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas?filter={"sorting":"imdb"}', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Colecciones', action = 'colecciones', search_type = 'all', text_color = 'moccasin' ))

    if config.get_setting('mnu_doramas', default=False):
        itemlist.append(item.clone( title = 'Doramas', action = 'list_col', url = host + 'scroll/coleccion/doramas-90?filter=null&page=1', search_type = 'movie', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'all' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host + 'series?filter={"sorting":"released"}', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'series?filter={"sorting":"popular"}', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'series?filter={"sorting":"imdb"}', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Colecciones', action = 'colecciones', search_type = 'all', text_color = 'moccasin' ))

    if config.get_setting('mnu_doramas', default=False):
        itemlist.append(item.clone( title = 'Doramas', action = 'list_col', url = host + 'scroll/coleccion/doramas-90?filter=null&page=1', search_type = 'tvshow', text_color = 'firebrick' ))

    if not config.get_setting('descartar_anime', default=False):
        itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', search_type = 'tvshow', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'all' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'tvshow' ))

    return itemlist


def mainlist_animes(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_col', url = host + 'scroll/anime?filter=null&page=1', group = 'animes', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = host + 'anime?filter={"sorting":"released"}', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'anime?filter={"sorting":"popular"}', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'anime?filter={"sorting":"imdb"}', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', group = 'animes', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', group = 'animes', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', group = 'animes', search_type = 'tvshow' ))

    return itemlist


def colecciones(item):
    logger.info()
    itemlist = []

    if item.search_type == 'all': text_color = 'moccasin'
    elif item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    itemlist.append(item.clone( action = 'list_col', title = 'Disney', url = host + 'scroll/coleccion/disney-20?filter=null&page=1', text_color = text_color ))
    itemlist.append(item.clone( action = 'list_col', title = 'Doramas', url = host + 'scroll/coleccion/doramas-90?filter=null&page=1', text_color = text_color ))
    itemlist.append(item.clone( action = 'list_col', title = 'Marvel', url = host + 'scroll/coleccion/marvel-22?filter=null&page=1', text_color = text_color ))
    itemlist.append(item.clone( action = 'list_col', title = 'National Geographic', url = host + 'scroll/coleccion/national-geographic-24?filter=null&page=1', text_color = text_color ))
    itemlist.append(item.clone( action = 'list_col', title = 'Pixar', url = host + 'scroll/coleccion/pixar-21?filter=null&page=1', text_color = text_color ))
    itemlist.append(item.clone( action = 'list_col', title = 'Star Wars', url = host + 'scroll/coleccion/star-wars-23?filter=null&page=1', text_color = text_color ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else:
       text_color = 'hotpink'
       if item.group == 'animes':  text_color = 'springgreen'

    data = do_downloadpage(host + 'categorias')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="app-section">(.*?)</div></div></div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?title="(.*?)"')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
        url_any = host + 'peliculas?'
        text_color = 'deepskyblue'
    else:
        if item.group == 'animes':
            url_any = host + 'anime?'
            text_color = 'springgreen'
        else:
            url_any = host + 'series?'
            text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    itemlist.append(item.clone( title = '2020 - ' + str(current_year), url = url_any + 'filter={%22released%22:%222020-' + str(current_year) + '%22,%22sorting%22:%22newest%22}', action = 'list_all', text_color = text_color ))

    itemlist.append(item.clone( title = '2010 - 2019', url = url_any + 'filter={%22released%22:%222010-2019%22,%22sorting%22:%22newest%22}', action = 'list_all', text_color = text_color ))

    itemlist.append(item.clone( title = '2000 - 2009', url = url_any + 'filter={%22released%22:%222000-2009%22,%22sorting%22:%22newest%22}', action = 'list_all', text_color = text_color ))

    itemlist.append(item.clone( title = '1990 - 1999', url = url_any + 'filter={%22released%22:%221990-1999%22,%22sorting%22:%22newest%22}', action = 'list_all', text_color = text_color ))

    itemlist.append(item.clone( title = '1980 - 1989', url = url_any + 'filter={%22released%22:%221980-1989%22,%22sorting%22:%22newest%22}', action = 'list_all', text_color = text_color ))

    itemlist.append(item.clone( title = '1970 - 1979', url = url_any + 'filter={%22released%22:%221970-1979%22,%22sorting%22:%22newest%22}', action = 'list_all', text_color = text_color ))

    itemlist.append(item.clone( title = '1960 - 1969', url = url_any + 'filter={%22released%22:%221960-1969%22,%22sorting%22:%22newest%22}', action = 'list_all', text_color = text_color ))

    if item.search_type == 'movie':
        itemlist.append(item.clone( title = '1950 - 1959', url = url_any + 'filter={%22released%22:%221950-1959%22,%22sorting%22:%22newest%22}', action = 'list_all', text_color = text_color ))

        itemlist.append(item.clone( title = '1940 - 1949', url = url_any + 'filter={%22released%22:%221940-1949%22,%22sorting%22:%22newest%22}', action = 'list_all', text_color = text_color ))

        itemlist.append(item.clone( title = '1930 - 1939', url = url_any + 'filter={%22released%22:%221930-1939%22,%22sorting%22:%22newest%22}', action = 'list_all', text_color = text_color ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
        url_qlty = host + 'peliculas?'
        text_color = 'deepskyblue'
    else:
        if item.group == 'animes':
            url_qlty = host + 'anime?'
            text_color = 'springgreen'
        else:
            url_qlty = host + 'series?'
            text_color = 'hotpink'

    if item.search_type == 'movie':
        itemlist.append(item.clone( title = 'Cam', url = url_qlty + 'filter={"quality":"CAM","sorting":"newest"}', action = 'list_all', text_color = text_color ))

    itemlist.append(item.clone( title = 'HD', url = url_qlty + 'filter={"quality":"HD","sorting":"newest"}', action = 'list_all', text_color = text_color ))

    itemlist.append(item.clone( title = 'SD', url = url_qlty + 'filter={"quality":"SD","sorting":"newest"}', action = 'list_all', text_color = text_color ))

    itemlist.append(item.clone( title = 'Ultra HD', url = url_qlty + 'filter={"quality":"Ultra HD","sorting":"newest"}', action = 'list_all', text_color = text_color ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    if item.search_type == 'all': text_color = 'moccasin'
    elif item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host + 'servicios')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Services<(.*?)</div></div></div>')

    matches = scrapertools.find_multiple_matches(bloque, "background-image.*?'(.*?)'" + '.*?<a href="(.*?)".*?<div style=.*?">(.*?)</div>')

    for thumb, url, title in matches:
        if not 'https:' in thumb: thumb = host[:-1] + thumb

        url = host + url + '?filter=null&page=1'

        url = url.replace('/coleccion/', '/scroll/coleccion/')

        itemlist.append(item.clone( action = 'list_col', title = title, thumbnail = thumb, url = url, text_color=text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def paises(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host + 'countries')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Los Paises<(.*?)</div></div></div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?title="">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_lst', title = title, url = url, text_color=text_color ))

    return itemlist


def list_col(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(str(data), '"id".*?"title":"(.*?)".*?"type":"(.*?)".*?"create_year":"(.*?)".*?"image":"(.*?)".*?"url":"(.*?)"')

    if item.group == 'animes':
       matches2 = scrapertools.find_multiple_matches(str(data), '"id".*?"title":"(.*?)".*?"image":"(.*?)".*?"create_year":"(.*?)".*?"type":"(.*?)".*?"url":"(.*?)"')

       matches = matches + matches2

    for title, _type, year, thumb, url in matches:
        if not url or not title: continue

        title = clean_title(title)

        title = title.replace('&#8211;', '').replace('&#039;', "'").replace('&#8230;', ' &').replace('&amp;', '&').replace('&#8217;s', "'").strip()
        title = title.replace('PelisplusHD', '').replace('Pelisplus', '').replace('Cuevana', '').replace(' Online', '').strip()

        thumb = host + thumb

        url = url.replace('\\/', '/')

        tipo = 'movie' if _type == 'movie' else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
               if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        url_pag = scrapertools.find_single_match(item.url, '(.*?)filter=null&page=')
        url_pag = url_pag.replace('?', '').strip()

        if url_pag:
            try:
               num_pag = item.url.split('&page=')[1]

               num_pag = num_pag.replace('?filter=null', '').strip()

               nro_pag = int(num_pag)
               num_pag = nro_pag + 1

               pagina = '?filter=null&page=' + str(num_pag)

               next_page = url_pag + str(pagina)

               itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_col', text_color='coral' ))
            except:
               pass

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="list-movie">(.*?)</div></div></div>')

    for match in matches:
        title = scrapertools.find_single_match(match, 'class="list-title">(.*?)</a>').strip()

        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')

        if not title or not url: continue

        if not 'http' in url: continue

        thumb = scrapertools.find_single_match(match, 'data-src="([^"]+)"')

        year = scrapertools.find_single_match(match, '<div class="list-year">(.*?)</div>')

        if not year: year = '-'

        title = title.replace('&#8211;', '').replace('&#039;', "'").replace('&#8230;', ' &').replace('&amp;', '&').replace('&#8217;s', "'").strip()
        title = title.replace('PelisplusHD', '').replace('Pelisplus', '').replace('Cuevana', '').replace(' Online', '').strip()

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
               if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination' in data:
            next_page = scrapertools.find_single_match(data, '<ul class="pagination.*?<li class="page-item active">.*?</a>' + ".*?href='(.*?)'.*?>Siguiente<")
            if not next_page: next_page = scrapertools.find_single_match(data, '<ul class="pagination.*?<li class="page-item active">.*?</a>.*?href="(.*?)".*?>Siguiente<')

            if '&page=' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def list_lst(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="list-movie">(.*?)</div></div></div>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(match, 'class="list-title">(.*?)</a>').strip()

        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')

        if not title or not url: continue

        if not 'http' in url: continue

        thumb = scrapertools.find_single_match(match, 'data-src="([^"]+)"')

        year = scrapertools.find_single_match(match, '<div class="list-year">(.*?)</div>')

        if not year: year = '-'

        title = title.replace('&#8211;', '').replace('&#039;', "'").replace('&#8230;', ' &').replace('&amp;', '&').replace('&#8217;s', "'").strip()
        title = title.replace('PelisplusHD', '').replace('Pelisplus', '').replace('Cuevana', '').replace(' Online', '').strip()

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
               if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, pagina = item.pagina, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<span itemprop="name">Temporada (.*?)</span>')

    tot_seasons = len(matches)

    for nro_season in matches:
        nro_tempo = nro_season

        if tot_seasons >= 10:
            if len(nro_season) == 1:
                nro_tempo = '0' + nro_tempo

        title = 'Temporada ' + nro_tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = nro_season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = nro_season, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.title)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="episodes tab-content">(.*?)>Contenido Silimar<')

    season = scrapertools.find_single_match(bloque, 'id="season-' + str(item.contentSeason) + '"(.*?)</a></div>')

    matches = scrapertools.find_multiple_matches(season, '<a href="(.*?)".*?<div class="episode">(.*?)</div>.*?<div class="name">(.*?)</div>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('PGratisHd', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PGratisHd', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PGratisHd', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PGratisHd', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PGratisHd', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PGratisHd', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PGratisHd', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, epis, title in matches[item.page * item.perpage:]:
        epis = epis.replace('Episodio', '').strip()

        if not epis: epis = 1

        if not title: title = item.contentSerieName

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

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
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    embed = scrapertools.find_single_match(data, 'data-embed="(.*?)"')

    if not embed: return itemlist

    data = do_downloadpage(host + 'ajax/embed/', post = {'id': embed, 'Referer': item.url} )

    new_url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')

    if not new_url: return itemlist

    if not 'http' in new_url: return itemlist

    data = do_downloadpage(new_url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    ses = 0

    if '/streamsito.' in new_url: ses += 1 

    if '//embed69.' in new_url:
        ses += 1

        datae = data

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
                elif 'streamsito' in srv: continue

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

    # ~ Otros
    options = scrapertools.find_multiple_matches(data, '<li onclick="go_to_playerVast(.*?)</li>')

    for option in options:
        ses += 1

        if 'data-lang="2"' in option: lang = 'Vose'
        elif 'data-lang="0"' in option: lang = 'Lat'
        elif 'data-lang="1"' in option: lang = 'Esp'
        else: lang = '?'

        url = scrapertools.find_single_match(str(option), "'(.*?)'")

        if '/embedsito.' in url:
           data1 = do_downloadpage(url)
           data1 = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

           url = scrapertools.find_single_match(data1, '<a href="(.*?)"')

        if not url: continue
        elif url == '#': continue

        elif 'fembed' in url: continue
        elif 'streamsb' in url: continue
        elif 'playersb' in url: continue
        elif 'sbembed' in url: continue

        elif 'player-cdn' in url: continue
        elif 'streamsito' in url: continue

        elif '/1fichier.' in url: continue
        elif '/short.' in url: continue
        elif '/plustream.' in url: continue
        elif '/disable2.' in url: continue
        elif '/disable.' in url: continue
        elif '/embedsito.' in url: continue
        elif '/xupalace.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        if servidor == 'directo':
            if not config.get_setting('developer_mode', default=False): continue
            else:
                other = url.split("/")[2]
                other = other.replace('https:', '').strip()

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    # ~ Downloads error link

    if not itemlist:
        matches = scrapertools.find_multiple_matches(data, '<iframe src="(.*?)"')
        if not matches: matches = scrapertools.find_multiple_matches(data, '<IFRAME SRC="(.*?)"')

        for url in matches:
            if '/1fichier.' in url: continue
            elif '/short.' in url: continue
            elif '/plustream.' in url: continue
            elif '/disable2.' in url: continue
            elif '/disable.' in url: continue
            elif '/embedsito.' in url: continue
            elif '/xupalace.' in url: continue
            elif 'streamsito' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            other = ''

            if servidor == 'various': other = servertools.corregir_other(url)

            if servidor == 'directo':
                if config.get_setting('developer_mode', default=False):
                    other = url.split("/")[2]
                    other = other.replace('https:', '').strip()

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = '?', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

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

    if url:
        if '/xupalace.' in url or '/uploadfox.' in url:
            return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def clean_title(title):
    logger.info()

    title = title.replace('\\u00e1', 'a').replace('\\u00c1', 'a').replace('\\u00e9', 'e').replace('\\u00ed', 'i').replace('\\u00f3', 'o').replace('\\u00fa', 'u')
    title = title.replace('\\u00f1', 'ñ').replace('\\u00bf', '¿').replace('\\u00a1', '¡').replace('\\u00ba', 'º')
    title = title.replace('\\u00eda', 'a').replace('\\u00f3n', 'o').replace('\\u00fal', 'u').replace('\\u00e0', 'a')

    title = title.replace('\\u00c9', 'E').replace('\\u00da', 'u')

    title = title.replace('\/', '').strip()

    return title


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search/' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

