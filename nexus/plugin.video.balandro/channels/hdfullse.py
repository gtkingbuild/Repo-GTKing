# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, servertools, tmdb


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


# ~ web para comprobar dominio vigente en actions pero pueden requerir proxies
# ~ web 0)-'https://hdfull.pm'


host = 'https://www.hdfull.it'

refer = 'https://hdfull.pm/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://hdfull.se', 'https://hdfull.so', 'https://hdfull.fm',
             'https://hdfull.cm', 'https://hdfull.gg', 'https://hdfull.be',
             'https://www.hdfull.app', 'https://www.hdfull.tw', 'https://hdfull.bz']

domain = config.get_setting('dominio', 'hdfullse', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'hdfullse')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'hdfullse')
    else: host = domain


perpage = 20


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_hdfullse_proxies', default=''):
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


def do_downloadpage(url, post = None, referer = None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    hay_proxies = False
    if config.get_setting('channel_hdfullse_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not referer: referer = refer
    headers = {'Referer': referer}

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('hdfullse', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '/search' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('HdFullSe', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('hdfullse', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'hdfullse', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_hdfullse', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='hdfullse', folder=False, text_color='chartreuse' ))

    itemlist.append(Item( channel='domains', action='operative_domains_hdfullse', title='Comprobar [B]Dominio Operativo Vigentes[/B]',
                          desde_el_canal = True, thumbnail=config.get_thumb('settings'), text_color='mediumaquamarine' ))

    itemlist.append(Item( channel='domains', action='last_domain_hdfullse', title='[B]Comprobar último dominio vigente[/B]',
                          desde_el_canal = True, host_canal = url, thumbnail=config.get_thumb('settings'), text_color='chocolate' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_hdfullse', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_hdfullse', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    itemlist.append(item.clone( title='Novelas', action = 'mainlist_series', text_color = 'limegreen' ))
    itemlist.append(item.clone( title='Doramas', action = 'mainlist_series', text_color = 'firebrick' ))

    if not config.get_setting('descartar_anime', default=False):
        itemlist.append(item.clone( title='Animes', action = 'mainlist_series', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Búsqueda de personas:', action = '', folder=False, text_color='tan' ))

    itemlist.append(item.clone( title = ' - Buscar intérprete ...', action = 'search', group = 'star', search_type = 'person', 
                                plot = 'Debe indicarse el nombre y apellido/s del intérprete.'))

    itemlist.append(item.clone( title = ' - Buscar dirección ...', action = 'search', group = 'director', search_type = 'person',
                                plot = 'Debe indicarse el nombre y apellido/s del director.'))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Catálogo', url= host + '/movies', search_type = 'movie' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Estrenos', url = host + '/new-movies', search_type = 'movie', text_color='cyan' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Actualizadas', url = host + '/updated-movies', search_type = 'movie' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Más valoradas', url = host + '/movies/imdb_rating', search_type = 'movie' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Por alfabético', url = host + '/movies/abc', search_type = 'movie' ))
    itemlist.append(item.clone( action = 'generos', title = 'Por género', search_type = 'movie' ))
    itemlist.append(item.clone( action = 'anios', title = 'Por año', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Catálogo', url= host + '/tv-shows', search_type = 'tvshow' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Más valoradas', url= host + '/tv-shows/imdb_rating', search_type = 'tvshow' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Novelas', url = host + '/tv-tags/soap', search_type = 'tvshow', text_color='limegreen' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Doramas', url = host + '/tv-tags/dorama', search_type = 'tvshow', text_color='firebrick' ))

    if not config.get_setting('descartar_anime', default=False):
        itemlist.append(item.clone( action = 'list_all', title = 'Animes', url = host + '/tv-tags/anime', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Por alfabético', url = host + '/tv-shows/abc', search_type = 'tvshow' ))

    itemlist.append(item.clone( action = 'generos', title = 'Por género', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host + '/movies')

    tipo = 'TV' if item.search_type == 'tvshow' else 'Películas'
    bloque = scrapertools.find_single_match(data, '<b class="caret"></b>&nbsp;&nbsp;%s</a>\s*<ul class="dropdown-menu">(.*?)</ul>' % tipo)

    matches = re.compile('<li><a href="([^"]+)">([^<]+)', re.DOTALL).findall(bloque)

    for url, title in matches:
        if title == 'All': continue

        if config.get_setting('descartar_anime', default=False):
            if title == 'Anime': continue

        itemlist.append(item.clone( title = title, url = host + url, action = 'list_all', text_color = text_color ))

    return sorted(itemlist, key = lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1919, -1):
        itemlist.append(item.clone( title = str(x), url = host + '/search/year/' + str(x) + '/', action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.search_post: data = do_downloadpage(item.url, post=item.search_post)
    else: data = do_downloadpage(item.url)

    patron = '<div class="item"[^>]*">'
    patron += '\s*<a href="([^"]+)"[^>]*>\s*<img class="[^"]*"\s+src="([^"]+)"[^>]*>'
    patron += '\s*</a>\s*</div>\s*<div class="rating-pod">\s*<div class="left">(.*?)</div>'
    patron += '.*?title="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    if item.search_post != '' and item.search_type != 'all':
        matches = list(filter(lambda x: ('/movie/' in x[0] and item.search_type == 'movie') or ('/show/' in x[0] and item.search_type == 'tvshow'), matches))

    num_matches = len(matches)

    for url, thumb, langs, title in matches[item.page * perpage:]:
        title = title.strip()
        languages = detectar_idiomas(langs)

        thumb = host + thumb

        url = host + url

        tipo = 'movie' if '/movie/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = ', '.join(languages), fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, languages = ', '.join(languages), fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))

        if len(itemlist) >= perpage: break

    # ~ al no tener year puede no corresponer caratula con el titulo
    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page_link = scrapertools.find_single_match(data, '<a class="current">.*?href="(.*?)">')

            if next_page_link:
                url = host + next_page_link
                itemlist.append(item.clone( title = 'Siguientes ...', url = url, page = 0, action = 'list_all', text_color='coral' ))

    return itemlist


def detectar_idiomas(txt):
    languages = []
    if '/spa.png' in txt: languages.append('Esp')
    if '/lat.png' in txt: languages.append('Lat')
    if '/sub.png' in txt: languages.append('Vose')
    if '/eng.png' in txt: languages.append('Eng')
    return languages


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    # ~ Reintentar a veces tarda en responder
    if not data: data = do_downloadpage(item.url)

    patron = 'itemprop="season".*?'
    patron += "<a href='(.*?)'.*?"
    patron += '<img class=.*?original-title="(.*?)".*?'
    patron += 'src="(.*?)".*?'
    patron += '<h5.*?>(.*?)</h5>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, thumb, retitle in matches:
        numtempo = scrapertools.find_single_match(title, 'Temporadas (\d+)')
        if not numtempo: numtempo = scrapertools.find_single_match(url, '-(\d+)$')

        if not numtempo: continue

        titulo = title
        if retitle != title: 
           if not 'Temporadas' in retitle: titulo += ' - ' + retitle

        titulo = titulo.replace('Season', 'Temporada').replace('Temporadas', 'Temporada')

        url = host + url

        if '/episode-' in url: url = scrapertools.find_single_match(url, '(.*?)/episode-')

        thumb = host + thumb

        if len(matches) == 1:
            blk_temp = scrapertools.find_single_match(data, '>Todas las temporadas<(.*?)</div>')
            num_temp = scrapertools.find_single_match(blk_temp, "'.*?/season-(.*?)'")

            if num_temp: numtempo = num_temp

            title = title.replace('Season', 'Temporada').replace('Temporadas', 'Temporada')

            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.referer = item.url
            item.url = url
            item.thumbnail = thumb
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', url = url, title = titulo, thumbnail = thumb, referer = item.url, page = 0,
                                    contentType = 'season', contentSeason = numtempo, text_color = 'tan' ))

    if len(itemlist) == 0:
        itemlist.append(item.clone( action = 'episodios', url = item.url + '/season-1', title = 'Temporada 1', referer = item.url, page = 0,
                                    contentType = 'season', contentSeason = 1, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    color_lang = config.get_setting('list_languages_color', default='red')

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'id="season-episodes">(.*?)</div></div></div>')

    patron = 'itemprop="season".*?'
    patron += "<a href='(.*?)'.*?"
    patron += 'src="(.*?)".*?'
    patron += '"name">(.*?)<.*?'
    patron += '</b>(.*?)</h5>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('HdFullSe', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HdFullSe', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HdFullSe', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HdFullSe', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HdFullSe', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('HdFullSe', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, thumb, title, epis in matches[item.page * item.perpage:]:
        titulo = str(item.contentSeason) + 'x' + epis + ' ' + item.contentSerieName

        thumb = host + thumb
        url = host + url

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['CAM', 'TS', 'DVDSCR', 'DVDRIP', 'HDTV', 'RHDTV', 'HD720', 'HD1080']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    data_js = do_downloadpage(host + '/static/style/js/jquery.hdfull.view.min.js')

    keys = scrapertools.find_multiple_matches(data_js, 'JSON.parse\(atob.*?substrings\((.*?)\)')
    if not keys: 
        keys = scrapertools.find_multiple_matches(data_js, 'JSON.*?\]\((0x[0-9a-f]+)\)\);')
        if keys: 
            for i, key in enumerate(keys): keys[i] = int(key, 16)

        else: keys = scrapertools.find_multiple_matches(data_js, 'JSON.*?\]\(([0-9]+)\)\);')

    data_js = do_downloadpage(host + '/static/js/providers.js')

    try:
        provs = balandroresolver.hdfull_providers(data_js)
        if not provs: return itemlist
    except:
        return itemlist

    data = do_downloadpage(item.url)

    data_obf = scrapertools.find_single_match(data, "var ad\s*=\s*'(.*?)'")

    data_decrypt = ''

    for key in keys:
        try:
           data_decrypt = jsontools.load(balandroresolver.obfs(base64.b64decode(data_obf), 126 - int(key)))
           if data_decrypt: break
        except:
           return itemlist

    matches = []

    for match in data_decrypt:
        if match['provider'] in provs:
            try:
                embed = provs[match['provider']][0]
                url = eval(provs[match['provider']][1].replace('_code_', "match['code']"))
                matches.append([match['lang'], match['quality'], url, embed])
            except:
                pass

    ses = 0

    for idioma, calidad, url, embed in matches:
        ses += 1

        if embed == 'd':
            if not 'uptobox' in url: continue

        elif '/powvideo.' in url: continue
        elif '/streamplay.' in url: continue

        elif 'onlystream.tv' in url: url = url.replace('onlystream.tv', 'upstream.to')
        elif 'vev.io' in url: url = url.replace('vev.io', 'streamtape.com/e')

        try:
            calidad = unicode(calidad, 'utf8').upper().encode('utf8')
        except: 
            try: calidad = str(calidad, 'utf8').upper()
            except: calidad  = calidad.upper()

        idioma = idioma.capitalize() if idioma != 'ESPSUB' else 'Vose'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, 
                              language = idioma, quality = calidad, quality_num = puntuar_calidad(calidad) ))

    itemlist = servertools.get_servers_itemlist(itemlist)

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.group:
            item.url = host + '/search' + '/' + item.group + '/' + texto
        else:
            texto = texto.replace(' ', '+')
            item.search_post = {'menu': 'search', 'query': texto}
            item.url = host + '/search'
			
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
