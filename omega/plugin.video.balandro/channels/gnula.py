# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://gnulahd.nu/'


# ~ por si viene de enlaces guardados
ant_hosts = ['http://gnula.nu/', 'https://gnula.nu/']

domain = config.get_setting('dominio', 'gnula', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'gnula')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'gnula')
    else: host = domain

_player = '.gnulahd.'

url_recientes = host + 'peliculas-de-estreno/lista-de-peliculas-online-parte-1/'

url_recomendadas = host + 'peliculas/lista-de-peliculas-recomendadas/'

IDIOMAS = {'VC': 'Esp', 'VL': 'Lat', 'VS': 'Vose', 'castellano': 'Esp', 'latino': 'Lat', 'vose': 'Vose'}

perpage = 30


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_gnula_proxies', default=''):
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


def do_downloadpage(url, post=None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    url = url.replace('http://', 'https://')

    hay_proxies = False
    if config.get_setting('channel_gnula_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url or _player in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host) and not _player in url:
        data = httptools.downloadpage(url, post=post, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('gnula', url, post=post, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, timeout=timeout).data

        if data:
            if not host in data and not _player in data:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('Gnula', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('gnula', url, post=post, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, timeout=timeout).data

            if not host in data and not _player in data: data = ''

        if not data:
            if '/lista-' in url or '/ver-' in url or '/generos/' in url or '/peliculas-de-estreno/' in url or '/lista-de-peliculas-recomendadas/' in url or _player in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('Gnula', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('gnula', url, post=post, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data or '<title>Just a moment please...</title>' in data:
        if not url.startswith(host) and not _player in url:
            data = httptools.downloadpage(url, post=post, timeout=timeout).data
        else:
            if hay_proxies:
                data = httptools.downloadpage_proxy('gnula', url, post=post, timeout=timeout).data
            else:
                data = httptools.downloadpage(url, post=post, timeout=timeout).data

    if '<title>Just a moment...</title>' in data or '<title>Just a moment please...</title>' in data:
        platformtools.dialog_notification(config.__addon_name, '[COLOR cyan][B]Gnula [COLOR red]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'gnula', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_gnula', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='gnula', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_gnula', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_gnula', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('gnula') ))

    itemlist.append(Item( channel='actions', action='show_old_domains', title='[COLOR coral][B]Historial Dominios[/B][/COLOR]', channel_id = 'gnula', thumbnail=config.get_thumb('gnula') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_last', url = host, group = 'estrenos', text_color = 'cyan' ))
    itemlist.append(item.clone( title = 'Novedades', action = 'list_last', url = host, group = 'novedades' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_last', url = host, group = 'recomendadas' ))

    itemlist.append(item.clone( title = 'Recientes', action = 'list_all', url = url_recientes ))
    itemlist.append(item.clone( title = 'Recomendadas', action = 'list_all', url = url_recomendadas ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'generos/lista-de-generos/')

    matches = re.compile('<td>\s*<strong>([^<]+)</strong>\s*\[<a href="([^"]+)" title="([^"]+)"', re.DOTALL).findall(data)

    for title, url, plot in matches:
        itemlist.append(item.clone( title=title, url=url, action='list_all', plot=plot, text_color = 'deepskyblue' ))


    matches = re.compile('<td>\s*<strong>([^<]+)</strong>\s*\[<a href="([^"]+)"', re.DOTALL).findall(data)

    for title, url in matches:
        # ~ descartar repetidos
        if url in [it.url for it in itemlist]: continue

        itemlist.append(item.clone( title=title, url=url, action='list_all', text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)


def idiomas(item):
    logger.info()
    itemlist = []

    # ~ Enlaces por idioma según las preferencias del usuario en servidores
    idio = {'Esp': ['Castellano', 'VC'], 'Lat': ['Latino', 'VL'], 'VO': ['Subtitulado', 'VS']}

    prefs = config.get_lang_preferences()
    prefs = sorted(prefs.items(), key=lambda p: p[1])

    for lg, num in prefs:
        if num == 0: continue

        itemlist.append(item.clone( title = '%s recientes' % idio[lg][0], action = 'list_all', url = url_recientes, filtro_lang = idio[lg][1], text_color='moccasin' ))
        itemlist.append(item.clone( title = '%s recomendadas' % idio[lg][0], action = 'list_all', url = url_recomendadas, filtro_lang = idio[lg][1], text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    patron  = '<a class="Ntooltip" href="([^"]+)">([^<]+)<span><br[^<]+'
    patron += '<img.*?src="([^"]+)"></span></a>(.*?)<br'

    matches = re.compile(patron, re.DOTALL).findall(data)

    # ~ reducir lista según idioma
    if item.filtro_lang:
        matches = list(filter(lambda m: '(%s)' % item.filtro_lang in m[3], matches))

    # ~ reducir lista según texto buscado
    if item.filtro_search:
        buscado = item.filtro_search.lower().strip()
        if ' ' not in buscado:
            matches = list(filter(lambda m: buscado in m[1].lower(), matches))
        else:
            # ~ descartar palabras demasiado cortas (la, de, los, etc)
            palabras = list(filter(lambda p: len(p) > 3, buscado.split(' ')))

             # ~ No hay palabras a buscar
            if len(palabras) == 0: return []

            def contiene(texto, palabras):
                found = False
                for palabra in palabras:
                    if palabra in texto:
                       found = True
                       break
                return found

            matches = list(filter(lambda m: contiene(m[1].lower(), palabras), matches))

    for url, title, thumb, resto in list(matches)[item.page * perpage:]:
        year = scrapertools.find_single_match(url, '-(\d+)-online/$')

        spans = scrapertools.find_multiple_matches(resto, '<span style="[^"]+">([^<]+)</span>')

        langs = []
        qltys = ''

        for span in spans:
            if span.startswith('(') and span.endswith(')'):
                lg = span[1:-1]
                langs.append(IDIOMAS.get(lg, lg))
            elif len(langs) > 0:
                qltys = span
                break

        title = title.replace('&#8217;', "'")

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=', '.join(langs), qualities=qltys,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if not item.filtro_search and len(list(matches)) > (item.page + 1) * perpage:
            itemlist.append(item.clone( title="Siguientes ...", page=item.page + 1, action='list_all', text_color='coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if item.group == 'estrenos':
        bloque = scrapertools.find_single_match(data, '<strong>ESTRENOS DE CINE</strong>(.*?)</table>')
    elif item.group == 'novedades':
        bloque = scrapertools.find_single_match(data, '<strong>NOVEDADES DE PELÍCULAS</strong>(.*?)</table>')
    else:
        bloque = scrapertools.find_single_match(data, '<strong>PELÍCULAS RECOMENDADAS</strong>(.*?)</table>')

    matches = re.compile('<a href="(.*?)".*?alt="(.*?)".*?src="(.*?)"', re.DOTALL).findall(bloque)

    for url, title, thumb in list(matches):
        title = title.replace('Poster pequeño de', '').replace('Poster pequeño', '').strip()

        title = title.replace('&#8217;', "'")

        titulo = title

        if " (" in titulo: titulo = titulo.split(" (")[0]

        if item.filtro_search:
             buscado = titulo.lower().strip()

             if not item.filtro_search.lower() in buscado: continue

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=titulo, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def puntuar_calidad(txt):
    orden = ['CAM', 'TS', 'TS-HQ', 'WEB-S', 'HC-CAM', 'HD-S', 'DVD-S', 'BR-S', 'HD-TC', 'HD-TV', 'DVD-R', 'HD-R', 'BR-R']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<em>([^<]+)</em></p>(.*?)<table[^>]*>(.*?)</table>', re.DOTALL).findall(data)

    if len(matches) == 0:
        matches = re.compile('<strong>Ver película online</strong> \[<span style="[^"]*">([^<]+)</span>\](.*?)<table[^>]*>(.*?)</table>', re.DOTALL).findall(data)

    ses = 0

    # ~ players
    for opcion, iframes, tabla in matches:
        ses += 1

        opcs = opcion.split(',')

        lang = opcs[1].strip().lower()
        qlty = opcs[2].strip().upper()

        links = re.compile('<iframe width="[^"]+" height="[^"]+" src="([^"]+)', re.DOTALL).findall(iframes)
        if not links: links = re.compile('<iframe src="([^"]+)', re.DOTALL).findall(iframes)

        for url in links:
            if url.endswith('/soon') or url.startswith('//soon.'): continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            other = servidor

            if other == 'powvideo': continue
            elif other == 'streamplay': continue
            elif other == 'streamango': continue
            elif other == 'streamcloud': continue
            elif other == 'openload': continue
            elif other == 'rapidvideo': continue

            if servidor == 'various': other = servertools.corregir_other(url)

            if servidor == other: other = ''

            lng = IDIOMAS.get(lang, lang)

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor,
                                  language = lng, quality = qlty, quality_num = puntuar_calidad(qlty), other = other ))

        links = re.compile('<a href="(.*?)".*?<span class="(.*?)"', re.DOTALL).findall(tabla)

        for url, srv in links:
            if url.endswith('/soon') or url.startswith('//soon.'): continue

            srv = srv.strip().lower()

            if srv == 'powvideo': continue
            elif srv == 'streamplay': continue
            elif srv == 'streamango': continue
            elif srv == 'streamcloud': continue
            elif srv == 'openload': continue
            elif srv == 'rapidvideo': continue

            elif srv == 'uploaded': continue
            elif srv == 'tele': continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            other = servidor

            if srv: other = srv

            if servidor == 'various': other = servertools.corregir_other(url)

            if servidor == other: other = ''

            lng = IDIOMAS.get(lang, lang)

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor,
                                  language = lng, quality = qlty, quality_num = puntuar_calidad(qlty), other = other ))

    # ~ downloads
        bloque = scrapertools.find_single_match(data, '>Online/Descarga<(.*?)</table>')

        links = re.compile('<a href="(.*?)"', re.DOTALL).findall(bloque)

        for url in links:
            if url.endswith('/soon') or url.startswith('//soon.'): continue

            elif '/powvideo.' in url: continue
            elif '/streamplay' in url: continue
            elif '/streamango.' in url: continue
            elif '/streamcloud.' in url: continue
            elif '/openload.'in url: continue
            elif '/rapidvideo.' in url: continue

            elif '/1fichier.' in url: continue
            elif '/ul.' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            other = servidor

            if servidor == 'various': other = servertools.corregir_other(url)

            if servidor == other: other = ''

            if servidor == 'directo':
                if not '/enlace.php?u=' in url: continue

                urls = re.compile('<a href="(.*?)"', re.DOTALL).findall(bloque)
                others = re.compile('<span class="(.*?)"', re.DOTALL).findall(bloque)

                if not others: continue

                other = ''

                i = 0

                for enlace in urls:
                    if not url in enlace:
                        i += 1
                        continue

                    try: other = others[i]
                    except: pass
                    break

                if not other: continue

                elif other == 'powvideo': continue
                elif other == 'streamplay': continue
                elif other == 'streamango': continue
                elif other == 'streamcloud': continue
                elif other == 'openload': continue
                elif other == 'rapidvideo': continue

                elif other == 'uploaded': continue

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, other = other ))

    # ~ others
        bloque = scrapertools.find_single_match(data, '>Online/Descarga<(.*?)</table>')

        links = re.compile('src="(.*?)"', re.DOTALL).findall(bloque)

        for url in links:
            if not '/player/?id=' in url: continue

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = '' ))

    # ~ embeds
    if not matches:
        bloque = scrapertools.find_single_match(data, '<strong>Ver película online</strong>(.*?)<strong>Reportar<')

        matches = re.compile('<iframe.*?src="(.*?)"', re.DOTALL).findall(bloque)

        for embed in matches:
            ses += 1

            data = do_downloadpage(embed)

            lang = ''
            if 'vose' in data: lang = 'Vose'
            elif 'latino' in data: lang = 'Lat'
            elif 'castellano' in data: lang = 'Esp'

            block = scrapertools.find_single_match(data, 'var videos =(.*?)</script>')

            matches = scrapertools.find_multiple_matches(str(block), '".*?","(.*?)"')

            for url in matches:
                url = url.replace('\\/', '/')

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                    if not config.get_setting('developer_mode', default=False): continue

                other = servidor

                if servidor == 'various': other = servertools.corregir_other(url)

                if servidor == other: other = ''

                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other ))

            matches = scrapertools.find_multiple_matches(data, '<a rel="nofollow".*?href="(.*?)"')

            for url in matches:
                if '/powvideo.' in url: continue
                elif '/streamplay' in url: continue
                elif '/streamango.' in url: continue
                elif '/streamcloud.' in url: continue
                elif '/openload.'in url: continue
                elif '/rapidvideo.' in url: continue

                elif '/1fichier.' in url: continue
                elif '/ul.' in url: continue

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                    if not config.get_setting('developer_mode', default=False): continue

                other = servidor

                if servidor == 'various': other = servertools.corregir_other(url)

                if servidor == other: other = ''

                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    url = url.replace('http://', 'https://')

    if '/soon' in url: url = ''
    elif '/powvideo.' in url: url = ''
    elif '/1fichier.' in url: url = ''
    elif '/ul.' in url: url = ''
    elif '/bembed.' in url: url = ''

    if item.server == 'directo':
        if url:
            try:
                if config.get_setting('channel_gnula_proxies', default=''):
                    url = httptools.downloadpage_proxy('gnula', url, follow_redirects=False).headers['location']
                else:
                    url = httptools.downloadpage(url, follow_redirects=False).headers['location']
            except:
                url = ''

    elif not item.server:
        data = do_downloadpage(url)

        url = scrapertools.find_single_match(data, "var url = '(.*?)'")

    if url:
        if '/soon' in url: url = ''
        elif '/powvideo.' in url: url = ''
        elif '/1fichier.' in url: url = ''
        elif '/ul.' in url: url = ''
        elif '/bembed.' in url: url = ''

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    # ~ No hay buscador propio en la web, usan el buscador genérico de google.

    logger.info()
    itemlist2 = []
    itemlist3 = []
    itemlist4 = []
    itemlist5 = []

    try:
        item.filtro_search = texto

        item.url = host
        item.group = 'estrenos'
        itemlist = list_last(item)

        if not itemlist:
            if not config.get_setting('channel_gnula_proxies', default=''):
                item.url = host
                item.group = 'novedades'
                itemlist2 = list_last(item)

                for it2 in itemlist2:
                    if it2.url not in [it.url for it in itemlist]:
                        itemlist.append(it2)

                if not itemlist2:
                    item.url = host
                    item.group = 'recomendadas'
                    itemlist3 = list_last(item)

                    for it3 in itemlist3:
                        if it3.url not in [it.url for it in itemlist]:
                            itemlist.append(it3)

                    if not itemlist3:
                        item.url = url_recomendadas
                        itemlist4 = list_all(item)

                        for it4 in itemlist4:
                            if it4.url not in [it.url for it in itemlist]:
                                itemlist.append(it4)

                        if not itemlist4:
                            item.url = url_recientes
                            itemlist5 = list_all(item)

                            for it5 in itemlist5:
                                if it5.url not in [it.url for it in itemlist]:
                                    itemlist.append(it5)

        return itemlist

    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
