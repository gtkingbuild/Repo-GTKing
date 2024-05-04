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


host = 'https://www.henaojara.com/'


_players = ['.henaojara.']


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

    if not headers: headers = {'Referer': host}

    hay_proxies = False
    if config.get_setting('channel_henaojara_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url or _players[0] in url:
        if hay_proxies:
            # ~ timeout = config.get_setting('channels_repeat', default=30)
            timeout = 40

    if not url.startswith(host) and not _players[0] in url:
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('henaojara', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                # ~ timeout = config.get_setting('channels_repeat', default=30)
                timeout = 40

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

                if not url.startswith(host) and not _players[0] in url:
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

    if config.get_setting('descartar_anime', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'all', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver/category/categorias/?tr_post_type=2', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_last', url = host, search_type = 'all', text_color = 'olivedrab' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'ver/category/emision/', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'ver/category/estrenos/', search_type = 'all', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'ver/category/categorias/espanol-castellano/', search_type = 'all' ))

    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'ver/category/categorias/latino/', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'ver/category/categorias/subtitulos/', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'ver/category/pelicula/?tr_post_type=1', search_type = 'all', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'all' ))

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

        SerieName = title

        if 'Temporada' in title: SerieName = title.split("Temporada")[0]
        if 'Movie' in title: SerieName = title.split("Movie")[0]

        SerieName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", SerieName).strip()
        SerieName = SerieName.replace('Español Latino HD', '').replace('Español Castellano HD', '').replace('Sub Español HD', '').strip()
        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        tipo = 'movie' if '>PELICULA<' in match else 'tvshow'
        sufijo = '' if item.search_type == 'movie' else tipo

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            titulo = title + nro_season

            itemlist.append(item.clone( action = 'temporadas', url= url, title=titulo, thumbnail=thumb,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))
        else:
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            PeliName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", title).strip()

            PeliName = PeliName.strip()

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

        SerieName = title

        if 'Temporada' in title: SerieName = title.split("Temporada")[0]
        if 'Movie' in title: SerieName = title.split("Movie")[0]

        SerieName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", SerieName).strip()
        SerieName = SerieName.replace('Español Latino HD', '').replace('Español Castellano HD', '').replace('Sub Español HD', '').strip()
        SerieName = SerieName.strip()

        PeliName = SerieName

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        epis = scrapertools.find_single_match(match, '<span class="ClB">(.*?)</span>')

        tipo = 'movie' if epis == '0' or epis == '1' else 'tvshow'
        sufijo = '' if item.search_type == 'movie' else tipo

        if tipo == 'tvshow':
            temp = scrapertools.find_single_match(url, '/season/.*?hd-(.*?)/')
            if not temp: temp = 1

            title = 'Temporada ' + str(temp) + ' ' + title

            title = title.replace('Temporada', '[COLOR goldenrod]Temporada[/COLOR]')

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
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

    if '>PELICULA<' in data:
        peli = scrapertools.find_single_match(data, '<span class="Num">.*?<a href="(.*?)"')

        itemlist.append(item.clone( action='findvideos', url = peli, title = '[COLOR yellow]Servidores[/COLOR] ' + item.title,
                                    thumbnail = item.thumbnail, contentType='movie', contentTitle=item.title, text_color='tan' ))

        return itemlist

    elif '<div class="TPlayer">' in data:
        itemlist.append(item.clone( action='findvideos', url = item.url, title = '[COLOR yellow]Servidores[/COLOR] ' + item.title,
                                    thumbnail = item.thumbnail, contentType='movie', contentTitle=item.title, text_color='tan' ))

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

    if 'data-tab="' in data:
        bloque = scrapertools.find_single_match(data, 'data-tab="' + str(item.contentSeason) + '.*?</table>')
    else:
        bloque = data

    matches = re.compile('<span class="Num">(.*?)</span>.*?><a href="(.*?)".*?<img src="(.*?)".*?<td class="MvTbTtl">.*?">(.*?)</a>', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
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
        titulo = '%sx%s - %s' % (str(item.contentSeason), epis, title)

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

    if '>PELICULA<' in data:
        peli = scrapertools.find_single_match(data, '<span class="Num">.*?<a href="(.*?)"')

        data = do_downloadpage(peli)

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

        url = url.replace('.henaojara2.', '.henaojara.')

        other = scrapertools.find_single_match(data, 'data-tplayernv="Opt' + str(option) + '"><span>(.*?)</span>')
        other = other.replace('<strong>', '').replace('</strong>', '')

        other = other.strip().lower()

        if other == 'multiplayer':
            url2 = url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

            data2 = do_downloadpage(url2)

            players = scrapertools.find_single_match(data2, 'src="(.*?)"')

            if players:
                players = players.replace('.henaojara2.', '.henaojara.')

                players = players.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

                data3 = do_downloadpage(players)

                matches3 = scrapertools.find_multiple_matches(data3, "loadVideo.*?'(.*?)'" + '.*?alt="(.*?)"')

                for player, srv in matches3:
                    srv = srv.strip().lower()

                    player = player.replace('.henaojara2.', '.henaojara.')

                    if srv == 'fembed': continue
                    elif srv == 'streamsb': continue

                    if srv == 'netuplayer': servidor = 'waaw'

                    elif srv == 'streamwish': servidor = 'various'
                    elif srv == 'filelions': servidor = 'various'
                    elif srv == 'filemoon': servidor = 'various'
                    elif srv == 'streamvid': servidor = 'various'

                    elif srv == 'ok': servidor = 'okru'

                    else:
                       if servertools.is_server_available(srv):
                           if not servertools.is_server_enabled(srv): continue
                           servidor = srv
                       else:
                           if not config.get_setting('developer_mode', default=False): continue
                           servidor = 'directo'

                    other = ''
                    if servidor == 'various': other = servertools.corregir_other(srv)
                    elif not servidor == 'directo': other = ''

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = player, language = lang, other = other ))

        else:
            if other == 'fembed': continue
            elif other == 'streamsb': continue

            if other == 'netuplayer': servidor = 'waaw'

            elif other == 'streamwish': servidor = 'various'
            elif other == 'filelions': servidor = 'various'
            elif other == 'filemoon': servidor = 'various'
            elif other == 'streamvid': servidor = 'various'

            elif other == 'ok': servidor = 'okru'

            else:
               if servertools.is_server_available(other):
                    if not servertools.is_server_enabled(other): continue
                    servidor = other
               else:
                    if not config.get_setting('developer_mode', default=False): continue
                    servidor = 'directo'

            if servidor == 'various': other = servertools.corregir_other(other)
            elif not servidor == 'directo': other = ''

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

    # Descargas
    matches = re.compile('<td><span class="Num">(.*?)</span>.*?href="(.*?)".*?alt="Descargar (.*?)"', re.DOTALL).findall(data)

    for nro, url, srv in matches:
        ses += 1

        srv = srv.strip().lower()

        other = ''

        if srv == 'fembed': continue
        elif srv == 'streamsb': continue

        if srv == 'netuplayer': other = 'waaw'

        elif srv == 'streamwish': other = 'various'
        elif srv == 'filelions': other = 'various'
        elif srv == 'filemoon': other = 'various'
        elif srv == 'streamvid': other = 'various'

        elif srv == 'ok': other = 'okru'

        else:
            if servertools.is_server_available(srv):
                if not servertools.is_server_enabled(srv): continue
                other = srv
            else:
                if not config.get_setting('developer_mode', default=False): continue
                other = 'D' + str(nro)

        if other == 'various': other = servertools.corregir_other(srv)
        else:
           if not other: other = other + ' D' + str(nro)

        url = url.replace('.henaojara2.', '.henaojara.')

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = lang, other = other ))

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

    url = item.url

    if '/?trdownload=' in url:
        try:
           timeout = None
           if host_player in url or _players[0] in url:
               if config.get_setting('channel_henaojara_proxies', default=''):
                   # ~ timeout = config.get_setting('channels_repeat', default=30)
                   timeout = 40

           if not url.startswith(host_player) and not _players[0] in url:
               url = httptools.downloadpage(url, follow_redirects=False, timeout=timeout).headers['location']
           else:
               if config.get_setting('channel_henaojara_proxies', default=''):
                   url = httptools.downloadpage_proxy('henaojara', url, follow_redirects=False, timeout=timeout).headers['location']
               else:
                   url = httptools.downloadpage(url, follow_redirects=False, timeout=timeout).headers['location']

           if '/multiplayer/' in url: url = ''
        except:
           url = ''

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
    elif '/pelistop.' in url: url = ''
    elif '/descargas/' in url: url = ''

    if url:
        if '/vidhidepro.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        elif '.mystream.' in url:
            return 'Servidor [COLOR tan]Cerrado[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = servertools.corregir_other(url)
        if other == 'Streamwish': servidor = 'various'
        elif other == 'Filelions': servidor = 'various'
        elif other == 'Filemoon': servidor = 'various'
        elif other == 'Streamvid': servidor = 'various'

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
