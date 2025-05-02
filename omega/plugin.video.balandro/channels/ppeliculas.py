# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import os

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.pepeliculas.org/'


_player = '/player.pepeliculas.org/'


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


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_ppeliculas_proxies', default=''):
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
    hay_proxies = False
    if config.get_setting('channel_ppeliculas_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host) and not _player in url:
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('ppeliculas', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('PPeliculas', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('ppeliculas', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                    if not url.startswith(host) and not _player in url:
                        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
                    else:
                        if hay_proxies:
                           data = httptools.downloadpage_proxy('ppeliculas', url, post=post, headers=headers, timeout=timeout).data
                        else:
                            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
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

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='ppeliculas', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_ppeliculas', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('ppeliculas') ))

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

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genre/estreno/', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'pelicula/', group = 'destacadas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'tendencias/', group = 'tendencias', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + 'episodios/', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'series/', group = 'destacadas', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'tendencias/', group = 'tendencias', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('accion', 'Acción'),
       ('action-adventure', 'Action & Adventure'),
       ('animacion', 'Animación'),
       ('aventura', 'Aventura'),
       ('ciencia-ficcion', 'Ciencia ficción'),
       ('comedia', 'Comedia'),
       ('comedy', 'Comedy'),
       ('crimen', 'Crimen'),
       ('documental', 'Documental'),
       ('drama', 'Drama'),
       ('familia', 'Familia'),
       ('fantasia', 'Fantasía'),
       ('guerra', 'Guerra'),
       ('historia', 'Historia'),
       ('history', 'History'),
       ('misterio', 'Misterio'),
       ('mystery', 'Mystery'),
       ('musica', 'Música'),
       ('romance', 'Romance'),
       ('sci-fi-fantasy', 'Sci-Fi & Fantasy'),
       ('suspense', 'Suspense'),
       ('terror', 'Terror'),
       ('thriller', 'Thriller'),
       ('war', 'War'),
       ('western', 'Western')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'genre/' + opc + '/', action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if item.group == 'destacadas':
        blk = 'destacadas</h2(.*?)recientemente</h2'
    elif item.group == 'tendencias':
        blk = '>Tendencias<(.*?)<div class="pagination">'
    else:
        blk = 'recientemente</h2(.*?)<div class="pagination">'

    bloque = scrapertools.find_single_match(data, blk)

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#038;', '&').replace("&#8217;", "'").replace("&#8211;", "")

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        qlty = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>')
        if 'Promo' in qlty or 'Proximamente' in qlty: qlty = ''

        year = scrapertools.find_single_match(match, '</h3>.*?<span>(.*?)</span>')
        if year:
            if not len(year) == 4:
                try:
                   year = year.split(',')[1]
                   year = year.strip()
                except:
                   year = ''

        if not year: year = '-'

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'

        if tipo == 'movie':
            if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if item.group == 'destacadas': return itemlist

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)".*?<i id="nextpagination"')
            if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "<a href='(.*?)'.*?<i id='nextpagination'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone(title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral'))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'recientemente</h2(.*?)<div class="pagination">')

    i = 0

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        s_e = scrapertools.get_season_and_episode(url)

        try:
           season = int(s_e.split("x")[0])
           epis = s_e.split("x")[1]
        except:
           i += 1
           season = 1
           epis = i

        if season >= 99:
            try:
               season = scrapertools.find_single_match(title, ' (' + '(.*?)X').strip()
               epis = scrapertools.find_single_match(title, ' (' + '.*?X(.*?)$').strip()
            except:
               season = ''
               epis = ''

            if not season:
                season = scrapertools.find_single_match(match, '<span>T(.*?)E').strip()
                season = 1

            if not epis: epis = 1

        title = title.replace('Online', '').replace('Sub Español', 'Vose').strip()

        title = title.replace('&#038;', '&').replace("&#8217;", "'").replace("&#8211;", "")

        if ':' in title: SerieName = scrapertools.find_single_match(title, '(.*?):').strip()
        elif ' (' in title: SerieName = title.split(" (")[0]
        else: SerieName = title

        title = title.replace('Vose', '[COLOR red][B]Vose[/B][/COLOR]').replace('Subtitulado', '[COLOR red][B]Vos[/B][/COLOR]')

        titulo = str(season) + 'x' + str(epis) + ' ' + title.replace('(' + str(season) + 'X' + str(epis) + ')', '')

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb,
                                    contentSerieName = SerieName, contentType='episode', contentSeason=season, contentEpisodeNumber=epis ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')
            if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "<a href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone(title = 'Siguientes ...', url = next_page, action = 'last_epis', text_color = 'coral'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<span class="se-t.*?">(.*?)</span>')
    if not matches: matches = scrapertools.find_multiple_matches(data, "<span class='se-t.*?'>(.*?)</span>")

    tot_tempo = len(matches)

    for numtempo in matches:
        nro_tempo = numtempo

        if tot_tempo >= 10:
            if int(numtempo) < 10: nro_tempo = '0' + numtempo

        title = 'Temporada ' + nro_tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = numtempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist,key=lambda x: x.title)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<span class="se-t.*?">' + str(item.contentSeason) + "</span>(.*?)</div></li></ul></div></div>")
    if not bloque: bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + "</span>(.*?)</div></li></ul></div></div>")

    patron = '<li class="mark-(.*?)">.*?<img src="(.*?)".*?<a href="(.*?)">(.*?)</a>'

    matches = scrapertools.find_multiple_matches(bloque, '<li class="mark-(.*?)">.*?<img src="(.*?)".*?<a href="(.*?)">(.*?)</a>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, "<li class='mark-(.*?)'>.*?<img src='(.*?)'.*?<a href='(.*?)'>(.*?)</a>")

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('PPeliculas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PPeliculas', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PPeliculas', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PPeliculas', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PPeliculas', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PPeliculas', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PPeliculas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for episode, thumb, url, title in matches[item.page * item.perpage:]:
        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason , contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color = 'coral' ))

    return itemlist


def corregir_servidor(servidor):
    logger.info()

    servidor = servidor.lower()

    servidor = servidor.replace('.com', '').replace('.org', '').replace('.co', '').replace('.cc', '').replace('.net', '').replace('.to', '').replace('.sx', '')
    servidor = servidor.replace('.ru', '').replace('.tv', '').replace('my.', '').replace('.info', '').replace('.re', '').replace('.xx', '').replace('.click', '')
    servidor = servidor.replace('v2.', '').replace('.veoh', '').replace('.sh', '').replace('.nz', '').replace('.site', '').replace('.uno', '').replace('.io', '').replace('.pl', '')
    servidor = servidor.replace('.link', '').replace('.club', '').replace('.red', '').replace('.download', '').replace('.vip', '').replace('.space', '').replace('.name', '')
    servidor = servidor.replace('.xyz', '').replace('.gl', '').replace('.me', '').replace('.eu', '').replace('.li', '').replace('.la', '').replace('.pm', '').replace('.ws', '').replace('.wf', '').replace('.one', '').replace('.hu', '').replace('.fun', '').replace('.work', '').replace('.cloud', '').replace('.google', '').strip()

    return servidor


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    ses = 0

    # ~ orden post
    if 'class="dooplay_player_option" data-post="' in data or "class='dooplay_player_option' data-post='" in data:
        matches1 = []
        matches2 = []

        if "class='dooplay_player_option' data-post='" in data:
            bloque = scrapertools.find_single_match(data, "<li id='player-option-trailer'.*?</span></li>(.*?)</li></ul></div></div>")
            if not bloque: bloque = data

            patron = "<li id='player-option-.*?"
            patron += "data-post='(.*?)'.*?data-type='(.*?)'.*?data-nume='(.*?)'.*?<span class='title'>(.*?)</span>.*?<span class='server'>(.*?)</span>"

            matches1 = scrapertools.find_multiple_matches(bloque, patron)

        if 'class="dooplay_player_option" data-post="' in data:
            bloque = scrapertools.find_single_match(data, '<li id="player-option-trailer".*?</span></li>(.*?)</li></ul></div></div>')
            if not bloque: bloque = data

            patron = '<li id="player-option-.*?'
            patron += 'data-post="(.*?)".*?data-type="(.*?)".*?data-nume="(.*?)".*?<span class="title">(.*?)</span>.*?<span class="server">(.*?)</span>'

            matches2 = scrapertools.find_multiple_matches(bloque, patron)

        matches = matches1 + matches2

        for _post, _type, _nume, qlty_lang, _server in matches:
            ses += 1

            if 'youtube' in _server: continue

            elif 'sbcom' in _server: continue
            elif 'lvturbo' in _server: continue
            elif 'vanfem' in _server: continue
            elif 'fembed' in _server: continue
            elif 'fcom' in _server: continue

            elif 'powvideo' in _server: continue
            elif 'streamplay' in _server: continue

            elif 'earn4files' in _server: continue
            elif 'uploadbuzz' in _server: continue
            elif 'powvibeo' in _server: continue
            elif 'slreamplay' in _server: continue
            elif 'fastclick' in _server: continue
            elif 'streamix' in _server: continue
            elif 'streamcloud' in _server: continue
            elif 'kingvid' in _server: continue
            elif 'stormo' in _server: continue
            elif 'uploadz' in _server: continue
            elif 'rockfile' in _server: continue
            elif 'openload' in _server: continue
            elif 'uploading' in _server: continue
            elif 'datafile' in _server: continue
            elif 'raptu' in _server: continue
            elif 'buzzheavier' in _server: continue
            elif 'guccihide' in _server: continue
            elif 'rapidgator' in _server: continue
            elif 'earn4files' in _server: continue
            elif 'uploadrive' in _server: continue
            elif 'uploadbuzz' in _server: continue
            elif 'filescdn' in _server: continue
            elif 'uploaded' in _server: continue

            url = host + 'wp-json/dooplayer/v2/%s/%s/%s'  %  (_post, _type, _nume)

            if 'Latino' in qlty_lang:
                qlty = qlty_lang.replace('Latino', '').strip()
                lang = 'Lat'
            elif 'Castellano' in qlty_lang or 'Español' in qlty_lang:
                qlty = qlty_lang.replace('Castellano', '').strip()
                lang = 'Esp'
            elif 'Subtitulado' in qlty_lang or 'Subtitulada' in qlty_lang or 'VOSE' in qlty_lang:
                qlty = qlty_lang.replace('Subtitulado', '').replace('Subtitulada', '').strip()
                lang = 'Vose'
            else:
                qlty = qlty_lang
                lang = '?'

            if 'hqq' in _server or 'netu' in _server or 'waaw' in _server: _server = 'waaw'
            elif 'dood' in _server: _server = 'doodstream'
            elif 'gofile' in _server: _server = 'gofile'
            elif 'google' in _server or 'Google' in _server: _server = 'gvideo'
            elif 'rutube' in _server: _server = 'various'
            elif 'gamovideo' in _server: _server = 'gamovideo'
            elif 'vidmoly' in _server: _server = 'vidmoly'

            other = corregir_servidor(_server)

            if other == qlty: qlty = ''

            if url.startswith('https://player.pepeliculas.org/'):
                url = url.replace('/player.pepeliculas.org/', '/waaw.to/')
                other == 'waaw'

            servidor = servertools.corregir_servidor(other)

            if servertools.is_server_available(other):
                if not servertools.is_server_enabled(other): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            other = servertools.corregir_other(other)

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', url = url, ref = item.url,
                                  other = other.capitalize(), language = lang, quality = qlty ))

    # ~ orden type
    if 'class="dooplay_player_option" data-type="' in data or "class='dooplay_player_option' data-type='" in data:
        matches1 = []
        matches2 = []

        if "class='dooplay_player_option' data-type='" in data:
            bloque = scrapertools.find_single_match(data, "<li id='player-option-trailer'.*?</span></li>(.*?)</li></ul></div></div>")
            if not bloque: bloque = data

            patron = "<li id='player-option-.*?"
            patron += "data-type='(.*?)'.*?data-post='(.*?)'.*?data-nume='(.*?)'.*?<span class='title'>(.*?)</span>.*?<span class='server'>(.*?)</span>"

            matches1 = scrapertools.find_multiple_matches(bloque, patron)

        if 'class="dooplay_player_option" data-type="' in data:
            bloque = scrapertools.find_single_match(data, '<li id="player-option-trailer".*?</span></li>(.*?)</li></ul></div></div>')
            if not bloque: bloque = data

            patron = '<li id="player-option-.*?'
            patron += 'data-type="(.*?)".*?data-post="(.*?)".*?data-nume="(.*?)".*?<span class="title">(.*?)</span>.*?<span class="server">(.*?)</span>'

            matches2 = scrapertools.find_multiple_matches(bloque, patron)

        matches = matches1 + matches2

        for _type, _post, _nume, qlty_lang, _server in matches:
            ses += 1

            if 'youtube' in _server: continue

            elif 'sbcom' in _server: continue
            elif 'lvturbo' in _server: continue
            elif 'vanfem' in _server: continue
            elif 'fembed' in _server: continue
            elif 'fcom' in _server: continue

            elif 'powvideo' in _server: continue
            elif 'streamplay' in _server: continue

            elif 'earn4files' in _server: continue
            elif 'uploadbuzz' in _server: continue
            elif 'powvibeo' in _server: continue
            elif 'slreamplay' in _server: continue
            elif 'fastclick' in _server: continue
            elif 'streamix' in _server: continue
            elif 'streamcloud' in _server: continue
            elif 'kingvid' in _server: continue
            elif 'stormo' in _server: continue
            elif 'uploadz' in _server: continue
            elif 'rockfile' in _server: continue
            elif 'openload' in _server: continue
            elif 'uploading' in _server: continue
            elif 'datafile' in _server: continue
            elif 'raptu' in _server: continue
            elif 'buzzheavier' in _server: continue
            elif 'guccihide' in _server: continue
            elif 'rapidgator' in _server: continue
            elif 'earn4files' in _server: continue
            elif 'uploadrive' in _server: continue
            elif 'uploadbuzz' in _server: continue
            elif 'filescdn' in _server: continue
            elif 'uploaded' in _server: continue

            url = host + 'wp-json/dooplayer/v2/%s/%s/%s'  %  (_post, _type, _nume)

            if 'Latino' in qlty_lang:
                qlty = qlty_lang.replace('Latino', '').strip()
                lang = 'Lat'
            elif 'Castellano' in qlty_lang or 'Español' in qlty_lang:
                qlty = qlty_lang.replace('Castellano', '').strip()
                lang = 'Esp'
            elif 'Subtitulado' in qlty_lang or 'Subtitulada' in qlty_lang or 'VOSE' in qlty_lang:
                qlty = qlty_lang.replace('Subtitulado', '').replace('Subtitulada', '').strip()
                lang = 'Vose'
            else:
                qlty = qlty_lang
                lang = '?'

            if 'hqq' in _server or 'netu' in _server or 'waaw' in _server: _server = 'waaw'
            elif 'dood' in _server: _server = 'doodstream'
            elif 'gofile' in _server: _server = 'gofile'
            elif 'google' in _server or 'Google' in _server: _server = 'gvideo'
            elif 'rutube' in _server: _server = 'various'
            elif 'gamovideo' in _server: _server = 'gamovideo'
            elif 'vidmoly' in _server: _server = 'vidmoly'

            other = corregir_servidor(_server)

            if other == qlty: qlty = ''

            if url.startswith('https://player.pepeliculas.org/'):
                url = url.replace('/player.pepeliculas.org/', '/waaw.to/')
                other == 'waaw'

            servidor = servertools.corregir_servidor(other)

            if servertools.is_server_available(other):
                if not servertools.is_server_enabled(other): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            other = servertools.corregir_other(other)

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', url = url, ref = item.url,
                                  other = other.capitalize(), language = lang, quality = qlty ))

    # ~ Ver
    if 'Ver en línea' in data:
        patron = '<tr id="link-.*?<img src=.*?'
        patron += 'domain=(.*?)">.*?<a href="(.*?)".*?target="_blank">(.*?)</a>.*?<strong class="quality">(.*?)</strong>.*?</td><td>(.*?)</td>'

        matches = scrapertools.find_multiple_matches(data, patron)

        for domain, url, tipo, qlty, lang in matches:
            ses += 1

            if not tipo == 'Ver en línea': continue

            servidor = corregir_servidor(domain)

            if 'sbcom' in servidor: continue
            elif 'lvturbo' in servidor: continue
            elif 'vanfem' in servidor: continue
            elif 'fembed' in servidor: continue
            elif 'fcom' in servidor: continue

            elif 'powvideo' in servidor: continue
            elif 'streamplay' in servidor: continue

            elif 'earn4files' in servidor: continue
            elif 'uploadbuzz' in servidor: continue
            elif 'powvibeo' in servidor: continue
            elif 'slreamplay' in servidor: continue
            elif 'fastclick' in servidor: continue
            elif 'streamix' in servidor: continue
            elif 'streamcloud' in servidor: continue
            elif 'kingvid' in servidor: continue
            elif 'stormo' in servidor: continue
            elif 'uploadz' in servidor: continue
            elif 'rockfile' in servidor: continue
            elif 'openload' in servidor: continue
            elif 'uploading' in servidor: continue
            elif 'datafile' in servidor: continue
            elif 'raptu' in servidor: continue
            elif 'buzzheavier' in servidor: continue
            elif 'guccihide' in servidor: continue
            elif 'rapidgator' in servidor: continue
            elif 'earn4files' in servidor: continue
            elif 'uploadrive' in servidor: continue
            elif 'uploadbuzz' in servidor: continue
            elif 'filescdn' in servidor: continue
            elif 'uploaded' in servidor: continue

            if 'hqq' in servidor or 'netu' in servidor or 'waaw' in servidor: servidor = 'waaw'
            elif 'dood' in servidor: servidor = 'doodstream'
            elif 'gofile' in servidor: servidor = 'gofile'
            elif 'google' in servidor or 'Google' in servidor: servidor = 'gvideo'
            elif 'rutube' in servidor: servidor = 'various'
            elif 'gamovideo' in servidor: servidor = 'gamovideo'
            elif 'vidmoly' in servidor: servidor = 'vidmoly'

            if url.startswith('https://player.pepeliculas.org/'):
                url = url.replace('/player.pepeliculas.org/', '/waaw.to/')
                servidor == 'waaw'

            if lang == 'Latino': lang = 'Lat'
            elif lang == 'Castellano' or lang == 'Español': lang = 'Esp'
            elif lang == 'Subtitulado' or lang == 'Subtitulada' or lang == 'VOSE': lang = 'Vose'
            else: lang = '?'

            servidor = servertools.get_server_from_url(url, disabled_servers=True)

            if servidor is None: continue

            servidor = servertools.corregir_servidor(servidor)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url,
                                  ref = item.url, other = 'v', language = lang, quality = qlty ))

    # ~ Descargas
    if 'Descarga' in data:
        patron = '<tr id="link-.*?<img src=.*?'
        patron += 'domain=(.*?)">.*?<a href="(.*?)".*?target="_blank">(.*?)</a>.*?<strong class="quality">(.*?)</strong>.*?</td><td>(.*?)</td>'

        matches = scrapertools.find_multiple_matches(data, patron)

        for domain, url, tipo, qlty, lang in matches:
            ses += 1

            if not tipo: continue

            servidor = corregir_servidor(domain)

            if 'sbcom' in servidor: continue
            elif 'lvturbo' in servidor: continue
            elif 'vanfem' in servidor: continue
            elif 'fembed' in servidor: continue
            elif 'fcom' in servidor: continue

            elif 'powvideo' in servidor: continue
            elif 'streamplay' in servidor: continue

            elif 'earn4files' in servidor: continue
            elif 'uploadbuzz' in servidor: continue
            elif 'multiup' in servidor: continue
            elif 'ddownload' in servidor: continue
            elif 'fikper' in servidor: continue
            elif 'powvibeo' in servidor: continue
            elif 'slreamplay' in servidor: continue
            elif 'buzzheavier' in servidor: continue
            elif 'fastclick' in servidor: continue
            elif 'streamix' in servidor: continue
            elif 'streamcloud' in servidor: continue
            elif 'kingvid' in servidor: continue
            elif 'stormo' in servidor: continue
            elif 'uploadz' in servidor: continue
            elif 'rockfile' in servidor: continue
            elif 'openload' in servidor: continue
            elif 'uploading' in servidor: continue
            elif 'datafile' in servidor: continue
            elif 'raptu' in servidor: continue
            elif 'buzzheavier' in servidor: continue
            elif 'guccihide' in servidor: continue

            elif 'rapidgator' in servidor: continue
            elif 'nitro' in servidor: continue
            elif '1fichier' in servidor: continue
            elif 'turbobit' in servidor: continue
            elif 'katfile' in servidor: continue
            elif 'earn4files' in servidor: continue
            elif 'uploadrive' in servidor: continue
            elif 'uploadbuzz' in servidor: continue
            elif 'filescdn' in servidor: continue
            elif 'uploaded' in servidor: continue

            if 'hqq' in servidor or 'netu' in servidor or 'waaw' in servidor: servidor = 'waaw'
            elif 'dood' in servidor: servidor = 'doodstream'
            elif 'gofile' in servidor: servidor = 'gofile'
            elif 'google' in servidor or 'Google' in servidor: servidor = 'gvideo'
            elif 'rutube' in servidor: servidor = 'various'
            elif 'gamovideo' in servidor: servidor = 'gamovideo'
            elif 'vidmoly' in servidor: servidor = 'vidmoly'

            elif servidor == 'filemoon': servidor = 'various'
            elif servidor == 'utorrent': servidor = 'torrent'

            if url.startswith('https://player.pepeliculas.org/'):
                url = url.replace('/player.pepeliculas.org/', '/waaw.to/')
                servidor == 'waaw'

            if lang == 'Latino': lang = 'Lat'
            elif lang == 'Castellano' or lang == 'Español': lang = 'Esp'
            elif lang == 'Subtitulado' or lang == 'Subtitulada' or lang == 'VOSE': lang = 'Vose'
            else: lang = '?'

            servidor = servertools.corregir_servidor(servidor)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url,
                                  ref = item.url, other = 'd', language = lang, quality = qlty ))

    # ~ Torrents
    blk_tor = ''

    if '>Torrent<' in data:
        blk_tor = scrapertools.find_single_match(data, ">Torrent<(.*?)</table>")

        matches = scrapertools.find_multiple_matches(blk_tor, "<tr id='link-.*?<a href='(.*?)'.*?target='_blank'>(.*?)</a>.*?<img src='.*?>(.*?)</td>")

        for url, srv, lang in matches:
            ses += 1

            if not url: continue

            if 'buzzheavier' in srv: continue
            elif 'guccihide' in srv: continue

            elif 'powvideo' in srv: continue
            elif 'streamplay' in srv: continue

            elif 'rapidgator' in srv: continue
            elif 'nitro' in srv: continue
            elif '1fichier' in srv: continue
            elif 'turbobit' in srv: continue
            elif 'katfile' in srv: continue
            elif 'earn4files' in srv: continue
            elif 'uploadrive' in srv: continue
            elif 'uploadbuzz' in srv: continue
            elif 'filescdn' in srv: continue
            elif 'uploaded' in srv: continue

            if lang == 'Latino': lang = 'Lat'
            elif lang == 'Castellano' or lang == 'Español': lang = 'Esp'
            elif lang == 'Subtitulado' or lang == 'Subtitulada' or lang == 'VOSE': lang = 'Vose'
            else: lang = '?'

            if 'utorrent' in srv: srv = 'torrent'
            elif 'mega' in srv: srv = 'mega'
            elif 'mediafire' in srv: srv = 'mediafire'

            other = corregir_servidor(srv)

            other = servertools.corregir_other(other)

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', url = url, ref = item.url,
                                  other = other.capitalize(), language = lang ))

    # ~ Torrents Data
    matches = scrapertools.find_multiple_matches(data, "<tr id='link-.*?<a href='(.*?)'.*?target='_blank'>(.*?)</a>.*?<img src='.*?>(.*?)</td>")

    for url, srv, lang in matches:
        ses += 1

        if not url: continue

        if url in blk_tor: continue

        if 'sbcom' in srv: continue
        elif 'lvturbo' in srv: continue
        elif 'vanfem' in srv: continue
        elif 'fembed' in srv: continue
        elif 'fcom' in srv: continue

        elif 'powvideo' in srv: continue
        elif 'streamplay' in srv: continue
        elif 'streanplay' in srv: continue

        elif 'buzzheavier' in srv: continue
        elif 'guccihide' in srv: continue

        elif 'rapidgator' in srv: continue
        elif 'nitro' in srv: continue
        elif '1fichier' in srv: continue
        elif 'turbobit' in srv: continue
        elif 'katfile' in srv: continue
        elif 'earn4files' in srv: continue
        elif 'uploadrive' in srv: continue
        elif 'uploadbuzz' in srv: continue
        elif 'filescdn' in srv: continue
        elif 'uploaded' in srv: continue

        if lang == 'Latino': lang = 'Lat'
        elif lang == 'Castellano' or lang == 'Español': lang = 'Esp'
        elif lang == 'Subtitulado' or lang == 'Subtitulada' or lang == 'VOSE': lang = 'Vose'
        else: lang = '?'

        if 'utorrent' in srv: srv = 'torrent'
        elif 'mega' in srv: srv = 'mega'
        elif 'mediafire' in srv: srv = 'mediafire'
        elif 'gofile' in srv: srv = 'gofile'
        elif 'google' in srv or 'Google' in srv: srv = 'gvideo'
        elif 'gamovideo' in srv: srv = 'gamovideo'
        elif 'vidmoly' in srv: srv = 'vidmoly'
        elif 'sandratableother'in srv: srv = 'voe'

        other = corregir_servidor(srv)

        if srv == 'gamovideo' or srv == 'vidmoly': pass
        else: other = servertools.corregir_other(other)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', url = url, ref = item.url,
                              other = other.capitalize(), language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.other == 'v' or item.other == 'd':
        if not item.url.startswith(host) and not _player in url:
            resp = httptools.downloadpage(item.url, follow_redirects=False)
        else:
            if config.get_setting('channel_ppeliculas_proxies', default=''):
                resp = httptools.downloadpage_proxy('ppeliculas', item.url, follow_redirects=False)
            else:
                resp = httptools.downloadpage(item.url, follow_redirects=False)

        if 'location' in resp.headers: url = resp.headers['location']

    elif item.other == 'Torrent' or item.other == 'Mega' or item.other == 'Mediafire':
        if not item.url.startswith(host) and not _player in url:
            resp = httptools.downloadpage(item.url, follow_redirects=False)
        else:
            if config.get_setting('channel_ppeliculas_proxies', default=''):
                resp = httptools.downloadpage_proxy('ppeliculas', item.url, follow_redirects=False)
            else:
                resp = httptools.downloadpage(item.url, follow_redirects=False)

        if 'location' in resp.headers: url = resp.headers['location']
        else:
           new_url = scrapertools.find_single_match(resp.data, 'href="(.*?)"')
           if new_url: url = new_url

    elif item.other == 'Clickndownload' or item.other == 'Gofile' or item.other == 'Gvideo' or item.other == 'Uptobox' or item.other == 'Dood' or item.other == 'Gamovideo' or item.other == 'Vidmoly' or item.other == 'Voe' or item.other == 'Zures' or item.other != '':
        if not item.url.startswith(host) and not _player in url:
            resp = httptools.downloadpage(item.url, follow_redirects=False)
        else:
            if config.get_setting('channel_ppeliculas_proxies', default=''):
                resp = httptools.downloadpage_proxy('ppeliculas', item.url, follow_redirects=False)
            else:
                resp = httptools.downloadpage(item.url, follow_redirects=False)

        if 'location' in resp.headers: url = resp.headers['location']
        else:
           url = scrapertools.find_single_match(resp.data, '<a id="link".*?href="(.*?)"')
           if not url: url = scrapertools.find_single_match(resp.data, '"embed_url":"(.*?)"')

        url = url.replace('\\/', '/')

        if url.startswith('//'): url = 'https:' + url

        if url.startswith('https://player.pepeliculas.org/'): url = url.replace('/player.pepeliculas.org/', '/waaw.to/')
        elif url.startswith('https://hqq.tv/player/embed_player.php?'): url = url.replace('https://hqq.tv/player/embed_player.php?', 'https://waaw.to/watch_video.php?v=')

    else:
        data = do_downloadpage(item.url, headers = {'Referer': item.ref})

        url = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        url = url.replace('\\/', '/')

        if url.startswith('//'): url = 'https:' + url

        if '/?source=' in url:
            data = do_downloadpage(url)

            url = scrapertools.find_single_match(data, 'id="player".*?<source src="(.*?)"')

        if url.startswith('https://player.pepeliculas.org/'): url = url.replace('/player.pepeliculas.org/', '/waaw.to/')
        elif url.startswith('https://hqq.tv/player/embed_player.php?'): url = url.replace('https://hqq.tv/player/embed_player.php?', 'https://waaw.to/watch_video.php?v=')

    if url.endswith('.torrent'):
        if config.get_setting('proxies', item.channel, default=''):
            if PY3:
                from core import requeststools
                data = requeststools.read(url, 'ppeliculas')
            else:
                data = do_downloadpage(url)

            if data:
                if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
                    return 'Archivo [COLOR red]Inexistente[/COLOR]'

                file_local = os.path.join(config.get_data_path(), "temp.torrent")
                with open(file_local, 'wb') as f: f.write(data); f.close()

                itemlist.append(item.clone( url = file_local, server = 'torrent' ))
        else:
            itemlist.append(item.clone( url = url, server = 'torrent' ))

        return itemlist

    if url:
        if item.other.startswith("Sb"):
            return 'Servidor [COLOR goldenrod]Obsoleto[/COLOR]'

        elif 'streamsb' in url or 'playersb' in url:
            return 'Servidor [COLOR goldenrod]Obsoleto[/COLOR]'

        elif 'openload' in url or 'streamango' in url or 'vidlox' in url or 'jetload' in url or 'verystream' in url or 'streamcherry' in url or 'gounlimited' in url or 'streamix' in url or 'viewsb' in url or 'flix555' in url or '.stormo.' in url or '.spruto.' in url or '/biter.' in url or '/streamin.' in url or '/filebebo.' in url or '/streamcloud.' in url or '/videofiles.' in url or '/kingvid.' in url or '/allvid.' in url or '/goo.' in url:
            return 'Servidor [COLOR goldenrod]Obsoleto[/COLOR]'

        elif 'uptobox' in url:
            return 'Servidor [COLOR goldenrod]Fuera de Servicio[/COLOR]'

        elif '.fembed.' in url:
            return 'Servidor [COLOR red]Fuera de Servicio[/COLOR]'

        elif '/powv1deo.' in url or '/powvibeo.' in url or '/pouvideo.' in url or '/povw1deo.' in url or '/powvldeo.' in url or '/pomvideo.' in url or '/streamp1ay.' in url or '/slreamplay.' in url or '/stemplay.' in url or '/steamplay.' in url:
            return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

        elif '.rapidvideo.' in url or '.filefactory.' in url or '.owndrives.' in url or '/rapidcloud.' in url or '/ul.' in url or '/fileflares.' in url or '/rockfile.' in url or '/estream.' in url or '/uploadrocket.' in url or '/uploading.' in url or '/ddownload.' in url or '/uploadz.' in url or '/fikper.' in url or '/www.datafile.' in url or '/filerice.' in url or '/thevideo.' in url:
            return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

        elif '/chomikuj.' in url: url = ''

        elif '.pepeliculas.' in url or '-pepeliculas.' in url: url = ''
        elif '.googleapis.' in url or '.google.' in url: url = ''
        elif '/gateway.zsprotect.' in url: url = ''

    if url:
        if '.fembed.' in url or '/feurl.' in url:
            return 'Servidor [COLOR red]Fuera de Servicio[/COLOR]'

        elif '/powv1deo.' in url or '/streamp1ay.' in url:
            return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

        if '/noblocktape.com/' in url: url = url.replace('/noblocktape.com/', '/streamtape.com/').replace('/3/', '/v/')

        url = url.replace('http://', 'https://')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'zplayer': url = url + '|' + host

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone( url=url, server=servidor))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article>(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#038;', '&').replace("&#8217;", "'").replace("&#8211;", "")

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(match, '<p>(.*?)</p>'))

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')
            if not next_page: next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "<a href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone(title = 'Siguientes ...', url = next_page, action = 'list_search', text_color = 'coral'))

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
