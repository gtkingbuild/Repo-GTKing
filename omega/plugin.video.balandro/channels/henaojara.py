# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, base64

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


host = 'https://henaojara.com/'


_players = ['.henaojara.', '.henaojara2.']


# ~ por si viene de enlaces guardados
ant_hosts = ['https://henaojara2.com/', 'https://www1.henaojara.com/', 'https://wvw.henaojara.com/',
             'https://www.henaojara.com/']


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
    if not url: return ''

    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    hay_proxies = False
    if config.get_setting('channel_henaojara_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url or str(_players) in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host) and not str(_players) in url:
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('henaojara', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('henaojara', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host) and not str(_players) in url:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('henaojara', url, post=post, headers=headers, timeout=timeout).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    if '>Sorry, you have been blocked<' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]Access[COLOR orangered] Blocked[/B][/COLOR]')
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

    itemlist.append(Item( channel='helper', action='show_help_henaojara', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('henaojara') ))

    itemlist.append(Item( channel='actions', action='show_old_domains', title='[COLOR coral][B]Historial Dominios[/B][/COLOR]', channel_id = 'henaojara', thumbnail=config.get_thumb('henaojara') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_anime', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'all', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animeonline/category/categorias/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'animeonline/category/estrenos/', search_type = 'tvshow', text_color = 'greenyellow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_last', url = host, search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'animeonline/category/emision/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'animeonline/category/pelicula/', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'animeonline/category/categorias/espanol-castellano/', text_color = 'moccasin' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'animeonline/category/categorias/latino/', text_color = 'moccasin' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'animeonline/category/categorias/subtitulos/', text_color = 'moccasin' ))

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
        elif title == 'ESTRENOS': continue
        elif title == 'PELICULAS': continue

        elif 'ESPAÑOL CASTELLANO' in title: continue
        elif 'ESPAÑOL LATINO' in title: continue
        elif 'ESPAÑOL SUBTITULADO' in title: continue

        title = title.replace('&amp;', '&')

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

        title = title.replace('#8217;', "'")

        nro_season = ''
        if 'Temporada' in title:
            nro_season = scrapertools.find_single_match(title, 'Temporada (.*?) ').strip()
            if nro_season: nro_season = ' T' + nro_season

        title = title.replace('#8217;', "'")

        year = scrapertools.find_single_match(title, '(\d{4})')
        if year: title = title.replace('(' + year + ')', '').strip()

        SerieName = corregir_SerieName(title)

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        tipo = 'movie' if '>PELICULA<' in match or '>Pelicula' in match or '-movie-' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            titulo = title + nro_season

            itemlist.append(item.clone( action = 'temporadas', url= url, title=titulo, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            PeliName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", title).strip()

            if 'Movie' in PeliName: PeliName = PeliName.split("Movie")[0]

            PeliName = PeliName.replace('Peliculas', '').replace('Pelicula', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=PeliName, infoLabels={'year': '-'} ))

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

        title = title.replace('#8217;', "'")

        year = scrapertools.find_single_match(match, '<span class="Year">.*?-(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(title, '(\d{4})')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        SerieName = corregir_SerieName(title)

        PeliName = SerieName

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        epis = scrapertools.find_single_match(match, '<span class="ClB">(.*?)</span>')

        tipo = 'movie' if epis == '0' else 'tvshow'

        if tipo == 'tvshow':
            temp = scrapertools.find_single_match(url, '/season/.*?hd-(.*?)/')
            if not temp: temp = 1

            title = 'Temporada ' + str(temp) + ' ' + title

            title = title.replace('Temporada', '[COLOR goldenrod]Temp.[/COLOR]')

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

        if tipo == 'movie':
            PeliName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", title).strip()

            if 'Movie' in PeliName: PeliName = PeliName.split("Movie")[0]

            PeliName = PeliName.replace('Peliculas', '').replace('Pelicula', '').strip()

            title = '[COLOR deepskyblue]Film [/COLOR]' + title

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=PeliName, infoLabels={'year': year} ))

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

        title = title.replace('#8217;', "'")

        SerieName = title

        if 'Temporada' in title: SerieName = title.split("Temporada")[0]
        if 'Movie' in title: SerieName = title.split("Movie")[0]

        SerieName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", SerieName).strip()
        SerieName = SerieName.replace('Español Latino HD', '').replace('Español Castellano HD', '').replace('Sub Español HD', '').strip()
        SerieName = SerieName.strip()

        temp = scrapertools.find_single_match(match, '<span class="ClB">(.*?)x')
        if not temp: temp = 1

        epis = scrapertools.find_single_match(match, '<span class="ClB">.*?x(.*?)</span>')
        if not epis: epis = 1

        if not str(temp) == '1': title = 'Episodio ' + str(temp) + 'x' + epis + ' ' + title
        else: title = 'Episodio ' + epis + ' ' + title

        title = title.replace('Episodio', '[COLOR goldenrod]Epis.[/COLOR]')

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

    hay_estreno = False
    if '>ESTRENO:' in data or '>Estreno:' in data: hay_estreno = True

    if hay_estreno:
        fec_estreno = scrapertools.find_single_match(data, '>ESTRENO:(.*?)<').strip()
        if not fec_estreno: fec_estreno = scrapertools.find_single_match(data, '>Estreno:(.*?)<').strip()

        if fec_estreno:
            platformtools.dialog_notification(config.__addon_name, '[COLOR cyan][B]Proximamente[/B][/COLOR]')

            fec_estreno = 'Estreno: ' + fec_estreno
            itemlist.append(item.clone( action='', title = fec_estreno, thumbnail = item.thumbnail, text_color='cyan', infoLabels={'year': ''} ))

            return itemlist

    if '>PELICULA<' in data or '>Pelicula' in data or '-movie-' in item.url:
        peli = scrapertools.find_single_match(data, '<span class="Num">.*?<a href="(.*?)"')

        itemlist.append(item.clone( action='findvideos', url = peli, title = '[COLOR yellow]Servidores[/COLOR] ' + item.title,
                                    thumbnail = item.thumbnail, contentType='movie', contentTitle=item.title, text_color='tan' ))

        return itemlist

    elif '<div class="TPlayer">' in data:
        itemlist.append(item.clone( action='findvideos', url = item.url, title = '[COLOR yellow]Servidores[/COLOR] ' + item.title,
                                    thumbnail = item.thumbnail, contentType='tvshow', contentTitle=item.title, text_color='tan' ))

        return itemlist

    if '<div class="snslst">' in data:
        bloque = scrapertools.find_single_match(data, '<div class="snslst">(.*?)</tbody>')

        matches = re.compile('<a href="(.*?)".*?class="Button STPb.*?>Temporada <span>(.*?)</span>', re.DOTALL).findall(bloque)


        for url, season in matches:
            title = 'Temporada ' + season

            if len(matches) == 1:
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]Una Temporada[/COLOR]')
                item.url = url
                item.page = 0
                item.contentType = 'season'
                item.contentSeason = season
                itemlist = episodios(item)
                return itemlist

            itemlist.append(item.clone( action = 'episodios', title = title, url = url, page = 0, contentType = 'season', contentSeason = season, text_color='tan' ))

    elif 'data-tab="' in data:
        matches = re.compile('data-tab="(.*?)"', re.DOTALL).findall(data)

        for season in matches:
            title = 'Temporada ' + season

            if len(matches) == 1:
                if config.get_setting('channels_seasons', default=True):
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

    hay_estreno = False
    if '>ESTRENO:' in data or '>Estreno:' in data: hay_estreno = True

    if 'data-tab="' in data:
        bloque = scrapertools.find_single_match(data, 'data-tab="' + str(item.contentSeason) + '"(.*?)</table>')
    else:
        bloque = data

    bloque = bloque.replace('&quot;', '"')

    matches = re.compile('<span class="Num">(.*?)</span>.*?><a href="(.*?)".*?src="(.*?)".*?<td class="MvTbTtl">.*?">(.*?)</a>', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
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

    for epis, url, thumb, title in matches[item.page * item.perpage:]:
        next_cap = ''
        if '">Proximo Capitulo' in title:
            next_cap = scrapertools.find_single_match(str(title), '.*?">(.*?)</b>')
            title = scrapertools.find_single_match(title, "(.*?)- <b").strip()

        if '</b>' in title: title = scrapertools.find_single_match(title, "</b>(.*?)$").strip()

        if item.contentSerieName: titulo = '%sx%s - %s' % (str(item.contentSeason), epis, str(item.contentSerieName))
        else: titulo = item.title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            if next_cap:
                next_cap = next_cap.replace('Proximo Capitulo', 'Próx. Epis.')
                itemlist.append(item.clone( action='', title = next_cap, thumbnail = item.thumbnail, text_color='cyan'))
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage, text_color='coral' ))

    tmdb.set_infoLabels(itemlist)

    if not itemlist:
        if hay_estreno:
            fec_estreno = scrapertools.find_single_match(data, '>ESTRENO:(.*?)<').strip()
            if not fec_estreno: fec_estreno = scrapertools.find_single_match(data, '>Estreno:(.*?)<').strip()

            if fec_estreno:
                platformtools.dialog_notification(config.__addon_name, '[COLOR cyan][B]Proximamente[/B][/COLOR]')

                fec_estreno = 'Estreno: ' + fec_estreno
                itemlist.append(item.clone( action='', title = fec_estreno, thumbnail = item.thumbnail, text_color='cyan', infoLabels={'year': ''} ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    if '>PELICULA<' in data or '>Pelicula' in data or '-movie-' in item.url:
        peli = scrapertools.find_single_match(data, '<span class="Num">.*?<a href="(.*?)"')

        peli = peli.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

        if not '/disqus.' in peli: data = do_downloadpage(peli)

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

        other = other.strip().lower()

        if other == 'multiplayer':
            url2 = url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

            data2 = do_downloadpage(url2)

            players = scrapertools.find_single_match(data2, 'src="(.*?)"')

            if players:
                players = players.replace('embed.php', 'player.php')

                if '?' in players:
                    path, queryString = players.split('?', 1)

                    if '&' in queryString:
                        queries_out = []
                        queries_in = queryString.split('&')

                        for query in queries_in:
                            if '=' in query:
                                key, val = query.split('=')
                                val = val+'ionA#as9ng849fg'
                                val = base64.b64encode(val.encode("utf-8")).decode('utf8')
                                queries_out.append('{}={}'.format(key, val))
                                queryString = '&'.join(queries_out)

                    players = '{}?{}'.format(path, queryString)

                    if players:
                        players = players.replace('', '')

                players = players.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&').strip()

                headers = {'Referer': host}

                data3 = do_downloadpage(players, headers=headers)

                matches3 = scrapertools.find_multiple_matches(data3, "loadVideo.*?'(.*?)'" + '.*?alt="(.*?)"')

                for player, srv in matches3:
                    srv = srv.strip().lower()

                    servidor = srv

                    if srv == 'fembed': continue
                    elif srv == 'streamsb': continue
                    elif srv == 'nyuu': continue
                    elif srv == '4sync': continue

                    if srv == 'netuplayer' or srv == 'netu' or srv == 'hqq': servidor = 'waaw'

                    elif srv == 'streamwish': servidor = 'various'
                    elif srv == 'streamhg': servidor = 'various'
                    elif srv == 'filelions': servidor = 'various'
                    elif srv == 'filemoon': servidor = 'various'
                    elif srv == 'streamvid': servidor = 'various'
                    elif srv == 'vidhide': servidor = 'various'
                    elif srv == 'lulustream': servidor = 'various'

                    elif srv == 'ok': servidor = 'okru'
                    elif srv == 'dood': servidor = 'doodstream'

                    else:
                       if servertools.is_server_available(servidor):
                           if not servertools.is_server_enabled(servidor): continue
                       else:
                           if not config.get_setting('developer_mode', default=False): continue
                           servidor = 'directo'

                    other = ''
                    if servidor == 'various': other = servertools.corregir_other(srv).capitalize()
                    elif not servidor == 'directo': other = ''

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = player, language = lang, other = other ))

        else:
            servidor = other

            if other == 'fembed': continue
            elif other == 'streamsb': continue
            elif other == '4sync': continue

            if other == 'netuplayer' or other == 'netu' or other == 'hqq': servidor = 'waaw'

            elif other == 'streamwish': servidor = 'various'
            elif other == 'filelions': servidor = 'various'
            elif other == 'filemoon': servidor = 'various'
            elif other == 'streamvid': servidor = 'various'
            elif other == 'vidhide': servidor = 'various'
            elif other == 'lulustream': servidor = 'various'

            elif other == 'ok': servidor = 'okru'
            elif other == 'dood': servidor = 'doodstream'

            else:
               if servertools.is_server_available(servidor):
                   if not servertools.is_server_enabled(servidor): continue
               else:
                   if not config.get_setting('developer_mode', default=False): continue
                   servidor = 'directo'

            if servidor == 'various': other = servertools.corregir_other(other)
            elif not servidor == 'directo': other = ''

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

    # Descargas
    matches = re.compile('<td><span class="Num">(.*?)</span>.*?href="(.*?)".*?alt="Descargar(.*?)"', re.DOTALL).findall(data)

    for nro, url, srv in matches:
        ses += 1

        srv = srv.strip().lower()

        servidor = srv

        other = ''

        if srv == 'fembed': continue
        elif srv == 'streamsb': continue
        elif srv == '4sync': continue

        if srv == 'netuplayer' or srv == 'netu' or srv == 'hqq': servidor = 'waaw'

        elif srv == 'streamwish': servidor = 'various'
        elif srv == 'filelions': servidor = 'various'
        elif srv == 'filemoon': servidor = 'various'
        elif srv == 'streamvid': servidor = 'various'
        elif srv == 'vidhide': servidor = 'various'
        elif srv == 'lulustream': servidor = 'various'

        elif srv == 'ok': servidor = 'okru'
        elif srv == 'dood': servidor = 'doodstream'

        else:
           if servertools.is_server_available(servidor):
               if not servertools.is_server_enabled(servidor): continue
           else:
               if not config.get_setting('developer_mode', default=False): continue

               if srv == 'streamwish': servidor = 'various'
               elif srv == 'filelions': servidor = 'various'
               elif srv == 'filemoon': servidor = 'various'
               elif srv == 'streamvid': servidor = 'various'
               elif srv == 'vidhide': servidor = 'various'
               elif srv == 'lulustream': servidor = 'various'

               else:
                  servidor = 'directo'
                  other = 'D' + str(nro)

        if servidor == 'various': other = servertools.corregir_other(srv)
        else:
           if servidor == 'directo':
               if not other: other = other + ' D' + str(nro)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'henaojara', default='')

    if domain_memo: host_player = domain_memo
    else: host_player = host

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    url = item.url.strip()

    if '/?trdownload=' in url:
        try:
           timeout = None
           if host_player in url or str(_players) in url:
               if config.get_setting('channel_henaojara_proxies', default=''): timeout = config.get_setting('channels_repeat', default=30)

           if not url.startswith(host_player) and not str(_players) in url:
               url = httptools.downloadpage(url, follow_redirects=False, timeout=timeout).headers['location']
           else:
               if config.get_setting('channel_henaojara_proxies', default=''):
                   url = httptools.downloadpage_proxy('henaojara', url, follow_redirects=False, timeout=timeout).headers['location']
               else:
                   url = httptools.downloadpage(url, follow_redirects=False, timeout=timeout).headers['location']
        except:
           url = ''

        if url:
           url = url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

           if '/multiplayer/' in url:
               headers = {'Referer': host}

               data = do_downloadpage(url, headers=headers)

               srv = scrapertools.find_single_match(data, "value = '(.*?)'")

               if srv:
                   data = do_downloadpage(url, post={'servidor': srv}, headers=headers)

                   url = scrapertools.find_single_match(data, '<a href="(.*?)"')
               else: url = ''

               if not url:
                   return 'Tiene [COLOR plum]Acortador[/COLOR] del enlace'

    elif '/go.php?v=' in url:
          url = scrapertools.find_single_match(url, 'v=(.*?)$')

    else:
        data = do_downloadpage(url)

        new_url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"').strip()

        if new_url:
            if new_url.startswith('//'): new_url = 'https:' + new_url

            url = new_url

            if '/nyuu.' in new_url:
                new_url = new_url.replace('&amp;', '&').strip()

                data = do_downloadpage(new_url)

                url = scrapertools.find_single_match(data, 'url: "(.*?)"')

                url = url.replace('&amp;', '&').strip()

                if url:
                    itemlist.append(item.clone( url=url, server='directo'))
                    return itemlist

            elif '/player/go.php?v=' in new_url:
                new_url = new_url.replace('/player/go.php?v=', '/player/go-player.php?v=')

                data = do_downloadpage(new_url)

                url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')

                if url.startswith('//'): url = 'https:' + url

    if '/streamium.xyz/' in url: url = ''
    elif '/pelispng.' in url: url = ''
    elif '/pelistop.' in url: url = ''
    elif '/descargas/' in url: url = ''

    if url:
        if '.mystream.' in url:
            return 'Servidor [COLOR tan]Cerrado[/COLOR]'
        elif '.fembed.' in url:
            return 'Servidor [COLOR tan]Cerrado[/COLOR]'

        url = url.replace('&amp;', '&').strip()

        if '/player.streamhj.top/' in url: url = url.replace('/player.streamhj.top/', '/netu.to/')
        elif '/netuplayer.top/' in url: url = url.replace('/netuplayer.top/', '/netu.to/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone( url=url, server=servidor))

    return itemlist


def corregir_SerieName(SerieName):
    logger.info()

    if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
    if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]

    if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]

    if '(Sin Relleno)' in SerieName: SerieName = SerieName.split("(Sin Relleno)")[0]

    if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]

    SerieName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", SerieName).strip()
    SerieName = SerieName.replace('Español Latino HD', '').replace('Español Castellano HD', '').replace('Sub Español HD', '').strip()

    if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]

    if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
    if 'season' in SerieName: SerieName = SerieName.split("season")[0]

    if ' S1 ' in SerieName: SerieName = SerieName.split(" S1 ")[0]
    elif ' S2 ' in SerieName: SerieName = SerieName.split(" S2 ")[0]
    elif ' S3 ' in SerieName: SerieName = SerieName.split(" S3 ")[0]
    elif ' S4 ' in SerieName: SerieName = SerieName.split(" S4 ")[0]
    elif ' S5 ' in SerieName: SerieName = SerieName.split(" S5 ")[0]
    elif ' S6 ' in SerieName: SerieName = SerieName.split(" S6 ")[0]
    elif ' S7 ' in SerieName: SerieName = SerieName.split(" S7 ")[0]
    elif ' S8 ' in SerieName: SerieName = SerieName.split(" S8 ")[0]
    elif ' S9 ' in SerieName: SerieName = SerieName.split(" S9 ")[0]

    if ' T1 ' in SerieName: SerieName = SerieName.split(" T1 ")[0]
    elif ' T2 ' in SerieName: SerieName = SerieName.split(" T2 ")[0]
    elif ' T3 ' in SerieName: SerieName = SerieName.split(" T3 ")[0]
    elif ' T4 ' in SerieName: SerieName = SerieName.split(" T4 ")[0]
    elif ' T5 ' in SerieName: SerieName = SerieName.split(" T5 ")[0]
    elif ' T6 ' in SerieName: SerieName = SerieName.split(" T6 ")[0]
    elif ' T7 ' in SerieName: SerieName = SerieName.split(" T7 ")[0]
    elif ' T8 ' in SerieName: SerieName = SerieName.split(" T8 ")[0]
    elif ' T9 ' in SerieName: SerieName = SerieName.split(" T9 ")[0]

    if '2nd' in SerieName: SerieName = SerieName.split("2nd")[0]
    if '3rd' in SerieName: SerieName = SerieName.split("3rd")[0]
    if '4th' in SerieName: SerieName = SerieName.split("4th")[0]
    if '5th' in SerieName: SerieName = SerieName.split("5th")[0]
    if '6th' in SerieName: SerieName = SerieName.split("6th")[0]
    if '7th' in SerieName: SerieName = SerieName.split("7th")[0]
    if '8th' in SerieName: SerieName = SerieName.split("8th")[0]
    if '9th' in SerieName: SerieName = SerieName.split("9th")[0]

    SerieName = SerieName.strip()

    return SerieName


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
