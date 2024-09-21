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


host = 'https://ww3u.cuevana3.vip'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://wwa3.cuevana3.vip', 'https://wlw.cuevana3.vip', 'https://wlv.cuevana3.vip',
             'https://wli3.cuevana3.vip', 'https://wnv3.cuevana3.vip', 'https://wn3.cuevana3.vip',
             'https://wv3i.cuevana3.vip', 'https://wmi.cuevana3.vip', 'https://wi3v.cuevana3.vip',
             'https://wev3.cuevana3.vip', 'https://wv3n.cuevana3.vip', 'https://wl3n.cuevana3.vip',
             'https://cuevana3.vip', 'https://wiw3.cuevana3.vip', 'https://wmi3.cuevana3.vip',
             'https://wn3l.cuevana3.vip', 'https://imu.cuevana3.vip', 'https://wni3.cuevana3.vip',
             'https://mvi.cuevana3.vip', 'https://wi3n.cuevana3.vip', 'https://wi3m.cuevana3.vip',
             'https://im3.cuevana3.vip', 'https://ww23.cuevana3.vip', 'https://iv3.cuevana3.vip',
             'https://lm3.cuevana3.vip', 'https://ww3v.cuevana3.vip']


domain = config.get_setting('dominio', 'cuevana3pro', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'cuevana3pro')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'cuevana3pro')
    else: host = domain


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


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    hay_proxies = False
    if config.get_setting('channel_cuevana3pro_proxies', default=''): hay_proxies = True

    if '/release/' in url: raise_weberror = False

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('cuevana3pro', url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

        if not data:
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('Cuevana3Pro', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('cuevana3pro', url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('cuevana3pro', url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    elif '<title>Bot Verification</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] reCAPTCHA[/B][/COLOR]')
        return ''

    elif '>Site Blocked</h2>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]Web Site[COLOR orangered] Blocked[/B][/COLOR]')
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

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + '/category/page-peliculas-de-estrenos/', search_type = 'movie', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Sagas', action = 'list_all', url = host + '/genre/sagas/', search_type = 'movie', text_color = 'greenyellow' ))

    itemlist.append(item.clone( title = 'DC Comics', action = 'list_all', url = host + '/genre/dc-comics/', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + '/genre/marvel/', search_type = 'movie', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catalogo', action = 'list_all', url = host + '/series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host + '/movies/')

    bloque = scrapertools.find_single_match(data,'>Genres<(.*?)</ul>')
    if not bloque: bloque = scrapertools.find_single_match(data,'>Categorias<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque,'<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == 'Estrenos': continue
        elif title == 'SAGAS': continue
        elif title == 'News': continue

        if item.search_type == 'movie':
            if title == 'Reality': continue
            elif title == 'Soap': continue
            elif title == 'Talk': continue

        if item.search_type == 'tvshow':
            if title == 'Película de TV': continue

        title = title.replace('&amp;', '&')

        itemlist.append(item.clone( title = title, url = url, action = 'list_all', text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
        text_color = 'deepskyblue'
        top_year = 1949
    else:
        text_color = 'hotpink'
        top_year = 1969

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, top_year, -1):
        url = host + '/release/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>').strip()
        if not title: title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#038;', '&').replace('&#8211;', '').strip()

        thumb = scrapertools.find_single_match(article, 'src="(.*?)"')

        if not 'http' in thumb: thumb = 'https' + thumb

        year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>')

        if year: title = title.replace('(' + year + ')' , '').strip()
        else: year ='-'

        if '/release/' in item.url: year = scrapertools.find_single_match(item.url, "/release/(.*?)/")

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
            next_page = scrapertools.find_single_match(bloque_next, '<span class="current">.*?.*?href="(.*?)"')

        elif '<nav class="navigation pagination">' in data:
            bloque_next = scrapertools.find_single_match(data, '<nav class="navigation pagination">(.*?)</nav>')
            next_page = scrapertools.find_single_match(bloque_next, '<a class="page-link current".*?</a>.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('data-season="(.*?)"', re.DOTALL).findall(data)

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

    if not d_post: return itemlist

    post = {'action': 'action_select_season', 'season': str(item.contentSeason), 'post': d_post}

    data = do_downloadpage(host + '/wp-admin/admin-ajax.php', post = post)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
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
        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        if thumb: thumb = 'https:' + thumb

        epis = scrapertools.find_single_match(match, '<span class="num-epi">.*?x(.*?)</span>')

        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

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
        ses += 1

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
                                if '/hydrax.' in url: continue
                                elif '/terabox.' in url: continue

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
                                elif '/terabox.' in url: continue

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
                        if '/hydrax.' in url: continue
                        elif '/terabox.' in url: continue
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
                    elif '/terabox.' in url: continue

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

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&#038;', '&').replace('&amp;', '&').replace('#038;', '')

    if item.server == 'directo':
        item.url = url

        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
        if not url: url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="([^"]+)')

        if not url:
            if '/terabox.' in data or '.terabox.' in data or '/hydrax.' in data:
                return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'
            return itemlist

        if '/pelisplay.' in url: url = ''

        if url:
            if '/terabox.' in url or '.terabox.' in url or '/hydrax.' in url:
                return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor == 'directo':
                new_server = servertools.corregir_other(url).lower()
                if not new_server.startswith("http"): servidor = new_server

            itemlist.append(item.clone(server = servidor, url = url))

        return itemlist

    itemlist.append(item.clone(server = item.server, url = url))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = data

    if '</h1>' in data:
         bloque = scrapertools.find_single_match(data,'</h1>(.*?)<div class="copy"')
         if not bloque: bloque = scrapertools.find_single_match(data,'</h1>(.*?)<p class="copy">')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>').strip()
        if not title: title = scrapertools.find_single_match(article, 'alt="(.*?)"')

        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#038;', '&').replace('&#8211;', '').strip()

        thumb = scrapertools.find_single_match(article, 'src="(.*?)"')

        year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>')

        if year: title = title.replace('(' + year + ')' , '').strip()
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
            next_page = scrapertools.find_single_match(bloque_next, '<a class="page-link current".*?</a>.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_search', text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    itemlist1 = []
    itemlist2 = []

    try:
        if item.search_type == 'movie':
            item.url = host + '/movies?s=' + texto.replace(" ", "+")
            return list_search(item)
        elif item.search_type == 'tvshow':
            item.url = host + '/series?s=' + texto.replace(" ", "+")
            return list_search(item)
        else:
            item.url = host + '/movies?s=' + texto.replace(" ", "+")
            itemlist1 = list_search(item)

            item.url = host + '/series?s=' + texto.replace(" ", "+")
            itemlist2 = list_search(item)

            itemlist = itemlist1 + itemlist2
            return itemlist
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
