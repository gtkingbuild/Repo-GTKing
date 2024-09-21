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


host = 'https://monoschinos2.com'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_monoschinos_proxies', default=''):
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
    if config.get_setting('channel_monoschinos_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('monoschinos', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '/buscar?q=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('monoschinos', url, post=post, headers=headers, timeout=timeout).data
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
                        data = httptools.downloadpage_proxy('monoschinos', url, post=post, headers=headers, timeout=timeout).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not '/buscar?q=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='monoschinos', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_monoschinos', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('latanime') ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/animes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + '/animes?genero=emision', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En blu-ray', action = 'list_all', url = host + '/animes?categoria=false&genero=blu-ray', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + '/animes?categoria=pelicula', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + '/animes?categoria=false&genero=castellano', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + '/animes?categoria=false&genero=latino', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + '/animes'

    data = do_downloadpage(url_genre)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div id="genero"(.*?)</div></div>')

    matches = re.compile('<input id=".*?value="(.*?)".*?">(.*?)</label>').findall(bloque)

    for gen, title in matches:
        title = title.strip()

        if title == 'Genero': continue
        elif title == 'Blu-ray': continue
        elif title == 'Castellano': continue
        elif title == 'Emisión': continue
        elif title == 'Latino': continue

        url = host + '/animes?categoria=false&genero=%s&fecha=false&letra=false' % gen

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1967, -1):
        url = host + '/animes?categoria=false&genero=false&fecha=%s&letra=false' % str(x)

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('ficha_efecto">(.*?)</li>').findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, 'title="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<h.*?>(.*?)</h')

        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        if not url or not title: continue

        title = title.replace('&quot;', '').replace('&#039;', "'")

        SerieName = title

        if 'OVA' in title: SerieName = title.split("OVA")[0]
        if 'Doblaje' in title: SerieName = title.split("Doblaje")[0]
        if 'La película' in title: SerieName = title.split("La película")[0]
        if 'Season' in title: SerieName = title.split("Season")[0]
        if 'Castellano' in title: SerieName = title.split("Castellano")[0]
        if 'Latino' in title: SerieName = title.split("Latino")[0]

        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        tipo = 'movie' if '-movie-' in url or 'Pelicula' in match else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '"page-item active".*?</li>.*?<a class="page-link.*?href="([^"]+)">')

        if next_page:
            next_page = next_page.replace('&amp;', '&')

            if '?p=' in next_page or '&p=' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>últimos capítulos<(.*?)>Series recientes<')

    matches = re.compile('<article>(.*?)</article>', re.DOTALL).findall(bloque)

    for match in matches:
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, 'title="(.*?)"')

        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        epis = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        if not epis: epis = 1

        title = title.replace('&quot;', '').replace('&#039;', "'")

        SerieName = title

        if 'OVA' in title: SerieName = title.split("OVA")[0]
        if 'Doblaje' in title: SerieName = title.split("Doblaje")[0]
        if 'capitulo' in title: SerieName = title.split("capitulo")[0]
        if 'Season' in title: SerieName = title.split("Season")[0]
        if 'Castellano' in title: SerieName = title.split("Castellano")[0]
        if 'Latino' in title: SerieName = title.split("Latino")[0]

        SerieName = SerieName.strip()

        title = title.replace('capitulo', '[COLOR goldenrod]capitulo[/COLOR]')

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    data_ajax = scrapertools.find_single_match(data, 'data-ajax="(.*?)"')
    _token = scrapertools.find_single_match(data, '<meta name="csrf-token" content="(.*?)"')
    _url = scrapertools.find_single_match(data, '<div class="d-flex gap-3 mt-3">.*?<a href="(.*?)"')

    if not data_ajax or not _token or not _url: return itemlist

    data = do_downloadpage(data_ajax, post = {'_token': _token})

    matches = re.compile('{"num":(.*?)}', re.DOTALL).findall(str(data))

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    _url = scrapertools.find_single_match(_url, '(.*?)-episodio-')

    for match in matches[item.page * item.perpage:]:
        url = _url + '-episodio-' + match

        title = 'Capítulo ' + match

        titulo = title + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = 1, contentEpisodeNumber=match ))

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

    matches = re.compile('<li id="play-video".*?data-player="(.*?)">(.*?)</button>', re.DOTALL).findall(data)

    ses = 0

    for d_play, srv in matches:
        ses += 1

        srv = srv.lower()

        other = ''

        if srv == 'puj': continue

        elif srv == 'ok': srv = 'okru'
        elif srv == 'zeus': srv = 'directo'
        elif srv == 'anonfile': srv = 'anonfiles'
        elif srv == 'zippy': srv = 'zippyshare'
        elif srv == 'drive': srv = 'gvideo'
        elif srv == 'pixel': srv = 'pixeldrain'
        elif srv == 'senvid2': srv = 'sendvid'
        else:
             if srv == 'vgembedcom': srv = 'vembed'

             other = servertools.corregir_other(srv)

        servidor = servertools.corregir_servidor(srv)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        if not servidor == 'directo':
            if not servidor == 'various': other = ''

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', d_play = d_play, language = 'Vose', other = other ))

    # download
    bloque = scrapertools.find_single_match(data, '<div class="downbtns">(.*?)</div>')

    matches = re.compile('href="(.*?)".*?<button>(.*?)<', re.DOTALL).findall(bloque)

    for url, srv in matches:
        ses += 1

        srv = srv.lower().strip()

        if srv == '1fichier' or srv == '1ficher': continue

        if srv == 'anonfile': srv = 'anonfiles'
        elif srv == 'bay': srv = 'bayfiles'
        elif srv == 'zippy': srv = 'zippyshare'
        elif srv == 'pixel': srv = 'pixeldrain'

        elif srv == 'ok':
          if '.fireload.com/' in url: continue

          elif '/mega.nz/' in url: srv = 'mega'

        if not srv: srv = servertools.get_server_from_url(url)

        if servertools.is_server_available(srv):
            if not servertools.is_server_enabled(srv): continue
        else:
           if not config.get_setting('developer_mode', default=False): continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = srv, title = '', url = url, language = 'Vose', other = 'D' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if not item.d_play:
        itemlist.append(item.clone( url = item.url, server = item.server ))
        return itemlist

    url = base64.b64decode(item.d_play).decode("utf-8")

    if host in url: url = scrapertools.find_single_match(url, 'url=(.*?)$')
    else:
       if '?url=' in url: url = scrapertools.find_single_match(url, 'url=(.*?)$')

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if not new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/buscar?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

