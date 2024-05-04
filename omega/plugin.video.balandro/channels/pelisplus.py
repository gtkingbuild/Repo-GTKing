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


host = 'https://pelisplusgo.vip/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://pelisplus.so/', 'https://www1.pelisplus.so/', 'https://www2.pelisplus.so/',
             'https://pelisplus.sh/', 'https://pelisplus.ac/', 'https://pelisplus.pe/',
             'https://www1.pelisplus.pe/', 'https://pelisplus.cx/', 'https://www1.pelisplus.cx/',
             'https://www2.pelisplus.cx/', 'https://www3.pelisplus.cx/', 'https://pelisplus.ph/',
             'https://www1.pelisplus.ph/', 'https://www2.pelisplus.ph/', 'https://www3.pelisplus.ph/',
             'https://www4.pelisplus.ph/', 'https://pelisplus.ws/', 'https://www3.pelisplus.ws/',
             'https://www4.pelisplus.ws/', 'https://pelisplushd.video/', 'https://www1.pelisplushd.video/',
             'https://pelisplushd.so/']


domain = config.get_setting('dominio', 'pelisplus', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'pelisplus')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'pelisplus')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_pelisplus_proxies', default=''):
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

    if '/peliculas-' in url: raise_weberror = False

    hay_proxies = False
    if config.get_setting('channel_pelisplus_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('pelisplus', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('pelisplus', url, post=post, headers=headers, raise_weberror=raise_weberror).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
            except:
                pass

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'pelisplus', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_pelisplus', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='pelisplus', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_pelisplus', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '?page=', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos?page=', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series?page=', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<h2>GÉNEROS(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)" title="(.*?)">.*?</a>')

    for url, tit in matches:
        url = host[:-1] + url + '?page='

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1930, -1):
        url = host + 'peliculas-' + str(x) + '?page='

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    data = do_downloadpage(item.url + str(item.page))

    data = data.replace('\n','')

    bloque = scrapertools.find_single_match(data, '<div class="main-peliculas movie-refresh">(.*?)<div class="butmore"')
    if not bloque: bloque = scrapertools.find_single_match(data, '<h2 class="pull-left">(.*?)<div class="footer">')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="item-pelicula(.*?)</figure>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()

        if not url or not title: continue

        if url.startswith('/'): url = host[:-1] + url

        title = re.sub(r" \(.*?\)| \| .*", "", title)

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year text-center">(.*?)</span>')
        if year: title = title.replace('(' + year + ')', '').strip()

        if not year: year = '-'

        if '/serie/' in url:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))
        else:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(itemlist) == 20:
            itemlist.append(item.clone (url = item.url, page = item.page + 1, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    temporadas = re.compile('div class="item-season-title">.*?</i>(.*?)</div>', re.DOTALL).findall(data)

    tot_tempo = len(temporadas)

    for tempo in temporadas:
        tempo = tempo.replace('Temporada', '').strip()

        if tot_tempo >= 10:
            if int(tempo) < 10: tempo = '0' + tempo

        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.title)


def episodios(item):
    logger.info()
    itemlist = []

    tab_epis = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'div class="item-season-title">.*?</i>Temporada ' + str(item.contentSeason) + ".*?</div>(.*?)</div>")

    matches = re.compile('<a href="(.*?)".*?</i>(.*?)</a>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PelisPlus', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlus', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlus', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlus', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPlus', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PelisPlus', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, title in matches:
        if url.startswith('/'): url = host[:-1] + url

        title = title.strip()
        episode = scrapertools.find_single_match(title, ".*?Capítulo(.*?)$")

        episode = episode.strip()

        ord_epis = str(episode)

        if len(str(ord_epis)) == 1: ord_epis = '0000' + ord_epis
        elif len(str(ord_epis)) == 2: ord_epis = '000' + ord_epis
        elif len(str(ord_epis)) == 3: ord_epis = '00' + ord_epis
        else:
            if num_matches > 50: ord_epis = '0' + ord_epis

        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        if num_matches > 50:
            tab_epis.append([ord_epis, url, titulo, episode])
        else:
            itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                        contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode, orden = ord_epis ))

    if num_matches > 50:
        tab_epis = sorted(tab_epis, key=lambda x: x[0])

        for orden, url, tit, epi in tab_epis[item.page * item.perpage:]:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = tit,
                                        orden = orden, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epi ))

            if len(itemlist) >= item.perpage:
                break

        if itemlist:
            if num_matches > ((item.page + 1) * item.perpage):
                itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", data_epi = item.data_epi, orden = '10000',
                                            page = item.page + 1, perpage = item.perpage, text_color = 'coral' ))

        return itemlist

    else:
        return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'latino': 'Lat', 'castell': 'Esp', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    data = data.replace('\n','')

    matches = scrapertools.find_multiple_matches(data, '<ul id=".*?_(.*?)"(.*?)</ul>')

    ses = 0

    for match in matches:
        idioma = match[0]

        urls = scrapertools.find_multiple_matches(match[1], '<li role="presentation" data-video="(.*?)" ')

        for url in urls:
            ses += 1

            if '/clonamesta.' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            link_other = ''
            if servidor == 'directo': link_other = normalize_other(url)
            elif servidor == 'various': link_other = servertools.corregir_other(url)

            lang = idioma

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = IDIOMAS.get(lang, lang), other = link_other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def normalize_other(url):
    if '/clonamesta' in url: link_other = ''

    elif 'pelisplus' in url: link_other = 'plus'
    elif 'pelisplay' in url: link_other = 'play'
    elif 'damedamehoy' in url: link_other = 'dame'
    elif 'apialfa' in url: link_other = 'apialfa'
    elif 'tomatomatela' in url: link_other = 'dame'
    else:
       if config.get_setting('developer_mode', default=False): link_other = url
       else: link_other = ''

    return link_other


def resuelve_dame_toma(dame_url):
    data = do_downloadpage(dame_url)

    url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
    if not url:
        checkUrl = dame_url.replace('embed.html#', 'details.php?v=')
        data = do_downloadpage(checkUrl, headers={'Referer': dame_url})
        url = scrapertools.find_single_match(data, '"file":\s*"([^"]+)').replace('\\/', '/')

    return url


def play(item):
    logger.info()
    itemlist = []

    servidor = item.server

    url = item.url

    if url.startswith('//'): url = 'https:' + url

    if item.other == 'dame':
        url = resuelve_dame_toma(item.url)

        if url:
            itemlist.append(item.clone(url=url , server='directo'))
            return itemlist

    elif item.other == 'apialfa':
        fid = scrapertools.find_single_match(item.url, "h=([^&]+)")

        if fid:
            if '/sc/' in item.url:
                post = {'h': fid}

                vid = item.url.replace('https://apialfa.tomatomatela.club/sc/index.php', 'https://apialfa.tomatomatela.club/sc/r.php')

                if not vid.startswith(host):
                    data = do_downloadpage(vid, post=post)
                else:
                    if config.get_setting('channel_pelisplus_proxies', default=''):
                        data = do_downloadpage_proxy('pelisplus', vid, post=post)
                    else:
                        data = do_downloadpage(vid, post=post)

                url = scrapertools.find_single_match(data, '<meta name="og:url" content="(.*?)"')

                if url:
                    servidor = servertools.get_server_from_url(url)
                    servidor = servertools.corregir_servidor(servidor)

                    url = servertools.normalize_url(servidor, url)

                    itemlist.append(item.clone(url=url, server=servidor))

                return itemlist

            vid = item.url.replace('https://apialfa.tomatomatela.club/ir/player.php', 'https://apialfa.tomatomatela.club/ir/rd.php')

            post = {'url': fid}

            try:
                if not vid.startswith(host):
                    new_url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                else:
                    if config.get_setting('channel_pelisplus_proxies', default=''):
                        new_url = httptools.downloadpage_proxy('pelisplus', vid, post=post, follow_redirects=False).headers['location']
                    else:
                        new_url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
            except:
                new_url = ''

            if new_url:
                if new_url.startswith('//'): new_url = 'https:' + new_url

                data = do_downloadpage(new_url)
                vid = scrapertools.find_single_match(data, 'value="(.*?)"')

                if vid:
                    try:
                        if not vid.startswith(host):
                            new_url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                        else:
                            if config.get_setting('channel_pelisplus_proxies', default=''):
                                new_url = httptools.downloadpage_proxy('pelisplus', vid, post=post, follow_redirects=False).headers['location']
                            else:
                                new_url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                    except:
                        new_url = ''

                if new_url:
                    servidor = servertools.get_server_from_url(new_url)
                    servidor = servertools.corregir_servidor(servidor)

                    if servidor and servidor != 'directo':
                        url = servertools.normalize_url(servidor, new_url)

                        itemlist.append(item.clone(url=url, server=servidor))

                    return itemlist

            else:
                vid = 'https://apialfa.tomatomatela.club/ir/redirect_ddh.php'

                try:
                    if not vid.startswith(host):
                        url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                    else:
                        if config.get_setting('channel_pelisplus_proxies', default=''):
                            url = httptools.downloadpage_proxy('pelisplus', vid, post=post, follow_redirects=False).headers['location']
                        else:
                            url = httptools.downloadpage(vid, post=post, follow_redirects=False).headers['location']
                except:
                    url = ''

                if url:
                    if '//damedamehoy.' in url or '//tomatomatela.' in url :
                        url = resuelve_dame_toma(url)

                        if url: itemlist.append(item.clone(url=url, server='directo'))
                        return itemlist

                    servidor = servertools.get_server_from_url(url)
                    servidor = servertools.corregir_servidor(servidor)

                    url = servertools.normalize_url(servidor, url)

                    itemlist.append(item.clone(url=url, server=servidor))
                    return itemlist


    elif item.server == 'directo':
        data = do_downloadpage(url)

        if item.other == 'play':
            url = scrapertools.find_single_match(data, '<div id="load-iframe">.*?</iframe>.*?<iframe id="embedvideo" src="(.*?)"')

            if url:
                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                itemlist.append(item.clone( url = url, server = servidor ))

                return itemlist

        data = data.replace('\n','')

        urls = scrapertools.find_multiple_matches(data, "sources:\[{file:.*?\'(.*?)\',label")

        for url in urls:
            if not 'error' in url:
                if '/pelisloadtop.com/' in url: continue

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                itemlist.append(item.clone( url = url, server = servidor ))
    else:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'pelisplus', default='')

    if domain_memo: host_player = domain_memo
    else: host_player = host

    h = {}

    h['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
    h['X-Requested-With'] = 'XMLHttpRequest'
    h['Referer'] = host_player
    h['Cookie'] = 'gogoanime=an0jqv9rr6aoe18irs9bo7qvc7'

    if not item.url.startswith(host_player):
        data = httptools.downloadpage(url = item.url, headers=h, raise_weberror=False).data
    else:
        if config.get_setting('channel_pelisplus_proxies', default=''):
            data = httptools.downloadpage_proxy('pelisplus', url = item.url, headers=h, raise_weberror=False).data
        else:
            data = httptools.downloadpage(url = item.url, headers=h, raise_weberror=False).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="title-results">(.*?)</div></div></div>')

    patron = '<div class="item-pelicula.*?<a href="(.*?)".*?<img alt="(.*?)".*?<span class="year text-center">(.*?)</span>.*?<p>(.*?)</p>'

    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, thumb, year, title in matches:
        if url.startswith('/'): url = host_player + url

        if not year: year = '-'

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'search.html?keyword=' + texto.replace(" ", "+")
       return list_search(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
