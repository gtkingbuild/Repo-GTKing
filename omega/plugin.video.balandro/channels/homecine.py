# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


LINUX = False
BR = False
BR2 = False

if PY3:
    try:
       import xbmc
       if xbmc.getCondVisibility("system.platform.Linux.RaspberryPi") or xbmc.getCondVisibility("System.Platform.Linux"): LINUX = True
    except: pass

try:
   if LINUX:
       try:
          from lib import balandroresolver2 as balandroresolver
          BR2 = True
       except: pass
   else:
       if PY3:
           from lib import balandroresolver
           BR = true
       else:
          try:
             from lib import balandroresolver2 as balandroresolver
             BR2 = True
          except: pass
except:
   try:
      from lib import balandroresolver2 as balandroresolver
      BR2 = True
   except: pass


host = 'https://homecine.cc/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://homecine.tv/', 'https://www3.homecine.tv/']


domain = config.get_setting('dominio', 'homecine', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'homecine')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'homecine')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_homecine_proxies', default=''):
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
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    hay_proxies = False
    if config.get_setting('channel_homecine_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('homecine', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

        if not data:
            if not '/?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('HomeCine', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('homecine', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('homecine', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not '/?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'homecine', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_homecine', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='homecine', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_homecine', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_homecine', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('homecine') ))

    itemlist.append(Item( channel='actions', action='show_old_domains', title='[COLOR coral][B]Historial Dominios[/B][/COLOR]', channel_id = 'homecine', thumbnail=config.get_thumb('') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Búsqueda de personas:', action = '', folder=False, text_color='tan' ))

    itemlist.append(item.clone( title = ' - Buscar intérprete ...', action = 'search', search_type = 'person',
                                plot = 'Indicar el nombre y/ó apellido/s del intérprete.'))
    itemlist.append(item.clone( title = ' - Buscar dirección ...', action = 'search', search_type = 'person',
                                plot = 'Indicars el nombre y/ó apellido/s del director.'))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'cartelera-peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'last_epis', url = host, group ='plast', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'cartelera-series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'last_epis', url = host, group ='slast', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, group ='elast', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<ul class="sub-menu">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?>(.*?)</a>')

    for url, title in matches:
        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if thumb.startswith('//'): thumb = 'https:' + thumb
        elif thumb.startswith('/'): thumb = host + thumb

        title = title.replace('&amp;', '&').replace('&#8211;', '').replace('&#8217;', "'")

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(match, '<span class="Qlty">(.*?)</span>')

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<nav class="navigation pagination".*?<a class="page-link current".*?</a>.*?href="([^"]+)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if item.group == 'plast':
        bloque = scrapertools.find_single_match(data, '>Últimas Peliculas Agregadas(.*?)>Últimas Series Agregadas')
    elif item.group == 'slast':
        bloque = scrapertools.find_single_match(data, '>Últimas Series Agregadas(.*?)>Últimos Capítulos Agregados')
    else:
        bloque = scrapertools.find_single_match(data, '>Últimos Capítulos Agregados(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, '<article (.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')

        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(article, 'src="(.*?)"')

        if thumb.startswith('//'): thumb = 'https:' + thumb

        if '/capitulo/' in url:
            season = scrapertools.find_single_match(article, '<span class="num-epi">(.*?)x')
            if not season: season = 1

            episode = scrapertools.find_single_match(article, '<span class="num-epi">.*?x(.*?)</span>')
            if not episode: episode = 1

            if len(season) == 2:
                if season.startswith('0'):
                    season = season.replace('0', '')

            if len(episode) == 2:
                if episode.startswith('0'):
                    episode = episode.replace('0', '')

            SerieName = title

            if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]

            if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
            if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]

            SerieName = SerieName.strip()

            title = title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')
            title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

            title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('capitulo', '[COLOR goldenrod]Epis.[/COLOR]')
            title = title.replace('Episode', '[COLOR goldenrod]Epis.[/COLOR]').replace('episode', '[COLOR goldenrod]Epis.[/COLOR]')
            title = title.replace('Episodio', '[COLOR goldenrod]Epis.[/COLOR]').replace('episodio', '[COLOR goldenrod]Epis.[/COLOR]')

            titulo = '%sx%s %s' % (season, episode, title)

            itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail = thumb,
                                        contentType='episode', contentSerieName=SerieName,
                                        contentSeason=season, contentEpisodeNumber=episode, infoLabels={'year': '-'} ))

            continue

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'

        if tipo == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))
        if tipo == 'tvshow':
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<a data-post="(.*?)" data-season="(.*?)"')

    tot_seasons = len(matches)

    for dpost, tempo in matches:
        nro_tempo = tempo

        if tot_seasons >= 10:
            if len(nro_tempo) == 1:
                nro_tempo = '0' + nro_tempo

        title = 'Temporada ' + nro_tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.dpost = dpost
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, dpost = dpost,
                                    contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda x: x.title)


def episodios(item): 
    logger.info()
    itemlist = []

    tab_epis = []

    if not item.dpost: return itemlist

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    post = {'action': 'action_select_season', 'post': item.dpost, 'season': item.contentSeason}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post)

    tot_pages = scrapertools.find_single_match(data, '<a class="page-numbers" href=".*?>(.*?)</a>')

    if not tot_pages:
        matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

        if item.page == 0 and item.perpage == 50:
            sum_parts = len(matches)

            try:
                tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
                if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
            except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
            elif tvdb_id:
                if sum_parts > 50:
                    platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
            else:
                item.perpage = sum_parts

                if sum_parts >= 1000:
                    if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                        platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                        item.perpage = 500

                elif sum_parts >= 500:
                    if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                        platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                        item.perpage = 250

                elif sum_parts >= 250:
                    if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                        platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                        item.perpage = 125

                elif sum_parts >= 125:
                    if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                        platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                        item.perpage = 75

                elif sum_parts > 50:
                    if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                        platformtools.dialog_notification('HomeCine', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                        item.perpage = sum_parts
                    else: item.perpage = 50

        for match in matches[item.page * item.perpage:]:
            title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

            url = scrapertools.find_single_match(match, '<a href="(.*?)"')

            if not url or not title: continue

            thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

            if thumb: thumb = 'https:' + thumb

            season = scrapertools.find_single_match(match, '<span class="num-epi">(.*?)x')
            if not season: season = 1

            episode = scrapertools.find_single_match(match, '<span class="num-epi">.*?x(.*?)</span>')
            if not episode: episode = 1

            ord_epis = str(episode)

            if len(str(ord_epis)) == 1: ord_epis = '0000' + ord_epis
            elif len(str(ord_epis)) == 2: ord_epis = '000' + ord_epis
            elif len(str(ord_epis)) == 3: ord_epis = '00' + ord_epis

            title = title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')
            title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

            title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('capitulo', '[COLOR goldenrod]Epis.[/COLOR]')
            title = title.replace('Episode', '[COLOR goldenrod]Epis.[/COLOR]').replace('episode', '[COLOR goldenrod]Epis.[/COLOR]')
            title = title.replace('Episodio', '[COLOR goldenrod]Epis.[/COLOR]').replace('episodio', '[COLOR goldenrod]Epis.[/COLOR]')

            tab_epis.append([ord_epis, url, title, thumb, season, episode])

        if tab_epis:
            tab_epis = sorted(tab_epis, key=lambda x: x[0])

            for orden, url, tit, thu, ses, epi in tab_epis:

                 tit = str(ses) + 'x' + str(epi) + ' ' + tit

                 itemlist.append(item.clone( action = 'findvideos', url = url, title = tit, thumbnail = thu,
                                             contentType='episode', ontentSeason=item.contentSeason, contentEpisodeNumber=epi ))

        tmdb.set_infoLabels(itemlist)

        return itemlist

    try:
       pages = int(tot_pages)
       if pages > 2: platformtools.dialog_notification('HomeCine', '[COLOR blue]Cargando episodios[/COLOR]')
    except:
       pages = 12

    for i in range(pages):
        matches = scrapertools.find_multiple_matches(data, '<li><a href="([^"]+)"[^>]*>([^<]+)')

        for url, title in matches:
            s_e = scrapertools.find_single_match(title, '(\d+)(?:x|X)(\d+)')

            if not s_e: continue

            season = int(s_e[0])
            episode = int(s_e[1])

            ord_epis = str(episode)

            if len(str(ord_epis)) == 1: ord_epis = '0000' + ord_epis
            elif len(str(ord_epis)) == 2: ord_epis = '000' + ord_epis
            elif len(str(ord_epis)) == 3: ord_epis = '00' + ord_epis

            tab_epis.append([ord_epis, url, title, season, episode])

        if pages > 0:
            next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="[^"]*page/(\d+)/')

            if next_page:
                post = {'action': 'action_pagination_ep', 'object': item.dobject, 'season': item.contentSeason, 'page': next_page}
                data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post)
            else:
                break

    if tab_epis:
        tab_epis = sorted(tab_epis, key=lambda x: x[0])

        for orden, url, tit, ses, epi in tab_epis:
            tit = tit.replace('"', '').strip()

            tit = tit.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('capitulo', '[COLOR goldenrod]Epis.[/COLOR]')
            tit = tit.replace('Episode', '[COLOR goldenrod]Epis.[/COLOR]').replace('episode', '[COLOR goldenrod]Epis.[/COLOR]')
            tit = tit.replace('Episodio', '[COLOR goldenrod]Epis.[/COLOR]').replace('episodio', '[COLOR goldenrod]Epis.[/COLOR]')

            itemlist.append(item.clone( action = 'findvideos', url = url, title = tit, contentType='episode', contentSeason=ses, contentEpisodeNumber=epi ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {
      'Español Latino': 'Lat',
      'Latino': 'Lat',
      'Español Castellano': 'Esp',
      'Castellano': 'Esp',
      'Español': 'Esp',
      'Sub Latino': 'Vose',
      'Sub Español': 'Vose',
      'Sub': 'Vose',
      'VOSE': 'Vose',
      'Ingles':'VO'
      }

    data = do_downloadpage(item.url)

    ses = 0

    options = scrapertools.find_multiple_matches(data, 'href="#options-(.*?)">.*?<span class="server">(.*?)</span>')

    for opt, lng in options:
        ses += 1

        srv = scrapertools.find_single_match(lng, '(.*?)-').strip()

        servidor = 'directo'

        if not srv: servidor = 'fastream'
        else: servidor = srv

        lng = scrapertools.find_single_match(lng, '.*?-(.*?)$').strip()

        matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)".*?</iframe>')

        for url in matches:
            ses += 1

            lang = lng

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, ref = item.url,
                                  language = IDIOMAS.get(lang, lang) ))

    # ~ Descargas No se tratan

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist



def play(item):
    logger.info()
    itemlist = []

    url = item.url

    url = url.replace('&#038;', '&')

    logger.info("check-00-play: %s" % url)

    data = do_downloadpage(url, headers={'Referer': item.ref}, raise_weberror=False)

    url = scrapertools.find_single_match(data, '(?i)<iframe.*?src="(.*?)"')

    if not url: return itemlist

    if '/cinemaupload.com/' in url:
        url = url.replace('/cinemaupload.com/', '/embed.cload.video/')

    if 'embed.cload' in url:
        data = do_downloadpage(url, headers={'Referer': host}, raise_weberror=False)

        if '<div class="g-recaptcha"' in data or 'Solo los humanos pueden ver' in data:
            headers = {'Referer': host, 'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)'}
            data = do_downloadpage(url, headers=headers, raise_weberror=False)

            new_url = scrapertools.find_single_match(data, '<div id="option-players".*?src="([^"]+)"')
            if new_url:
                new_url = new_url.replace('/cinemaupload.com/', '/embed.cload.video/')
                data = do_downloadpage(new_url, raise_weberror=False)

        url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')

        if url:
            if '/download/' in url:
                url = url.replace('//download/', '/files/').replace('/download/', '/files/')
                itemlist.append(item.clone( url = url, server = 'directo' ))
                return itemlist

            elif '/manifest.mpd' in url:
                if platformtools.is_mpd_enabled():
                    itemlist.append(['mpd', url, 0, '', True])
                    return itemlist

                itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
                return itemlist

            else:
                itemlist.append(['m3u8', url])
                return itemlist

    if url:
        if 'dailymotion' in url: url = 'https://www.dailymotion.com/' + url.split('/')[-1]

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

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

