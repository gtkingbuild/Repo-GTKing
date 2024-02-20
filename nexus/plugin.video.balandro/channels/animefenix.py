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


host = 'https://animefenix.tv/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://www.animefenix.com/', 'https://www.animefenix.tv/']


domain = config.get_setting('dominio', 'animefenix', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'animefenix')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'animefenix')
    else: host = domain


perpage = 30


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_animefenix_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar[/B] ...', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

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
    if config.get_setting('channel_animefenix_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('animefenix', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not 'animes?q=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('AnimeFenix', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('animefenix', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('animefenix', url, post=post, headers=headers, timeout=timeout).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not 'animes?q=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'animefenix', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_animefenix', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='animefenix', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_animefenix', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_animefenix', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

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

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes?page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_last', url = host, search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'animes?estado[]=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'animes?type%5B%5D=ova&order=default', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'animes?type%5B%5D=movie&order=default', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + 'animes?type%5B%5D=special&order=default',  search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por categorías', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = host + 'animes'

    data = do_downloadpage(url_cat)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, r'<select name="[^"]+" id="order_select"(.*?)<\/select>')

    matches = re.compile(r'<option value="([^"]+)"\s*>([^<]+)').findall(data)

    for categoria, title in matches:
        if title == "Calificación": continue

        url = "%s?order=%s&page=1" % (url_cat, categoria)

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return sorted(itemlist,key=lambda x: x.title)


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + 'animes'

    data = do_downloadpage(url_genre)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, r'<select name="[^"]+" id="genre_select" multiple="multiple">(.*?)<\/select>')

    matches = re.compile(r'<option value="([^"]+)"\s*>([^<]+)').findall(data)

    for genre_id, title in matches:
        if title == "Ángeles": title = 'Angeles'

        url = "%s?genero[]=%s&order=default&page=1" % (url_genre, genre_id)

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    url_anio = host + 'animes'

    data = do_downloadpage(url_anio)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, r'<select name="[^"]+" id="year_select" multiple="multiple">(.*?)<\/select>')

    matches = re.compile(r'<option value="([^"]+)"\s*>([^<]+)').findall(data)

    for anio, title in matches:
        url = "%s?year[]=%s&order=default&page=1" % (url_anio, anio)

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<article class="serie-card"><div class="serie-card__information"><p>([^<]+)<\/p>'
    patron += '<\/div><figure class="image"><a href="([^"]+)" title="([^"]+)">'
    patron += '<img src="([^"]+)".*?<span class="tag year is-dark">(\d+)'

    matches = re.compile(patron).findall(data)

    for info, url, title, thumb, year in matches[item.page * perpage:]:
        if not url or not title: continue

        SerieName = title

        if 'Peliculas' in SerieName: SerieName = SerieName.split("Peliculas")[0]
        if 'Latino' in SerieName: SerieName = SerieName.split("Latino")[0]
        if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]
        if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]

        SerieName = SerieName.strip()

        if item.search_type == 'tvshow':
            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, 
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year, 'plot': info} ))
        else:
            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': info} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<a class="pagination-link" href="' in data:
            next_page = scrapertools.find_single_match(data, '<a class="pagination-link" href="([^"]+)">Siguiente')

            if next_page:
                next_page = item.url.split("?")[0] + next_page

                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'Últimas series agregadas(.*?)Comentarios')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?<img src="(.*?)".*?alt="(.*?)"')

    for url, thumb, title in matches:
        SerieName = title

        if 'Peliculas' in SerieName: SerieName = SerieName.split("Peliculas")[0]
        if 'Latino' in SerieName: SerieName = SerieName.split("Latino")[0]
        if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]
        if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'Episodios recientes(.*?)Últimas series agregadas')

    matches = re.compile('<a href="(.*?)".*?<img src="(.*?)".*?alt="(.*?)".*?<div class="overepisode.*?">(.*?)</div>', re.DOTALL).findall(bloque)

    for url, thumb, title, episode in matches:
        SerieName = title

        if 'Peliculas' in SerieName: SerieName = SerieName.split("Peliculas")[0]
        if 'Latino' in SerieName: SerieName = SerieName.split("Latino")[0]
        if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]
        if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]

        SerieName = SerieName.strip()

        try:
            epis = scrapertools.find_single_match(episode, "Episodio.*?(\d+)")
        except:
            epis = 0

        SerieName = SerieName.replace(str(epis), '').strip()

        title = episode + ' ' + title.replace(str(epis), '').strip()

        title = title.replace('Episodio', '[COLOR goldenrod]Episodio[/COLOR]')

        if url:
            itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb, infoLabels={'year': '-'},
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    matches = re.compile('<a class="fa-play-circle d-inline-flex align-items-center is-rounded " href="([^"]+)".*?<span>([^<]+)', re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimeFenix', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeFenix', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeFenix', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeFenix', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeFenix', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimeFenix', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, title in matches[item.page * item.perpage:]:
        try:
            episode = scrapertools.find_single_match(title, "Episodio.*?(\d+)")
        except:
            episode = 0

        titulo = title + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=episode ))

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

    ses = 0

    srvs = scrapertools.find_multiple_matches(data, '<a title="(.*?)" href="(.*?)"')

    matches = re.compile(r"tabsArray\['\d+'\] = \".*?src='(?:\.\.|)([^']+)", re.DOTALL).findall(data)

    for url in matches:
        ses += 1

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        serv = ''

        for srv, vid in srvs:
            vid = vid.replace('#vid', '')

            if not vid == str(ses): continue

            serv = srv.lower()
            break

        if serv == 'gamo': servidor = 'gamovideo'
        elif serv == 'ru': servidor = 'okru'
        elif serv == 'burst': servidor = 'burstcloud'
        elif serv == 'yourupload': servidor = 'yourupload'
        elif serv == 'mp4upload': servidor = 'mp4upload'

        if serv == 'stream2':
            servidor = 'various'
            serv = 'streamwish'
        elif serv == 'lion':
            servidor = 'various'
            serv = 'filelions'

        if serv == servidor: serv = ''

        if not serv == 'fireload':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language='Vose', other = serv ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith('//'): item.url = 'https:' + item.url

    item.url = item.url.replace('&amp;', '&')

    servidor = item.server

    url = item.url

    if '/videa.hu/' in url:
        if url.startswith('//'): url = 'https:' + url

        data = do_downloadpage(url)

        if '/recaptcha/api.js?render=explicit&hl=hu' in data:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    elif '/stream/amz.php' in url:
        if not url.startswith("http"): url = host + url[1:]

        data = do_downloadpage(url)

        url = scrapertools.find_single_match(data, '"file":"([^"]+)"')

    elif '/redirect.php?' in url:
        data = do_downloadpage(url)

        url = scrapertools.find_single_match(data, 'playerContainer.*?src="([^"]+)"')

        if '/videa.hu/' in url:
            if url.startswith('//'): url = 'https:' + url

            data = do_downloadpage(url)

            if '/recaptcha/api.js?render=explicit&hl=hu' in data:
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        elif '/stream/amz.php' in url:
            if not url.startswith("http"): url = host + url[1:]

            data = do_downloadpage(url)

            url = scrapertools.find_single_match(data, '"file":"([^"]+)"')

        elif 'terabox.' in url: url = ''

        elif '.fireload.' in url: url = scrapertools.find_single_match(url, 'v=(.*?)$')

    if url:
        if not url.startswith("http"): url = "https:" + url

        url = url.replace('&amp;', '&').replace("\\/", "/")

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'animes?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

