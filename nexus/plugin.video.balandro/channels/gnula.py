# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://gnula.nu/'


url_estrenos = host + 'peliculas-de-estreno/lista-de-peliculas-online-parte-1/'

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
    ant_hosts = ['http://gnula.nu/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    timeout = None
    if host in url:
        if config.get_setting('channel_gnula_proxies', default=''): timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, timeout=timeout).data
    else:
        data = httptools.downloadpage_proxy('gnula', url, post=post, timeout=timeout).data

        if not data:
            if '/lista-' in url or '/ver-' in url or '/generos/' in url:
                platformtools.dialog_notification('Gnula', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')
                data = httptools.downloadpage_proxy('gnula', url, post=post, timeout=timeout).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='gnula', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host, group = 'estrenos' ))
    itemlist.append(item.clone( title = 'Novedades', action = 'list_last', url = host, group = 'novedades' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_last', url = host, group = 'recomendadas' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = url_estrenos ))

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
        if url in [it.url for it in itemlist]: continue # descartar repetidos

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

        itemlist.append(item.clone( title = '%s estrenos' % idio[lg][0], action = 'list_all', url = url_estrenos, filtro_lang = idio[lg][1], text_color='moccasin' ))
        itemlist.append(item.clone( title = '%s recomendadas' % idio[lg][0], action = 'list_all', url = url_recomendadas, filtro_lang = idio[lg][1], text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    patron  = '<a class="Ntooltip" href="([^"]+)">([^<]+)<span><br[^<]+'
    patron += '<img src="([^"]+)"></span></a>(.*?)<br'
    matches = re.compile(patron, re.DOTALL).findall(data)

    # ~  reducir lista según idioma
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

            if len(palabras) == 0: return [] # ~ No hay palabras a buscar

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
        quality = ''

        for span in spans:
            if span.startswith('(') and span.endswith(')'):
                lg = span[1:-1]
                langs.append(IDIOMAS.get(lg, lg))
            elif len(langs) > 0:
                quality = span
                break

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=', '.join(langs), qualities=quality,
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

    #if item.filtro_lang:
    #    matches = list(filter(lambda m: '(%s)' % item.filtro_lang in m[3], matches))

    for url, title, thumb in list(matches):
        title = title.replace('Poster pequeño de', '').replace('Poster pequeño', '').strip()

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
        patron = '<strong>Ver película online</strong> \[<span style="[^"]*">([^<]+)</span>\](.*?)<table[^>]*>(.*?)</table>'
        matches = re.compile(patron, re.DOTALL).findall(data)

    for opcion, iframes, tabla in matches:
        opcs = opcion.split(',')
        lang = opcs[1].strip().lower()
        quality = opcs[2].strip().upper()

        links = re.compile('<iframe width="[^"]+" height="[^"]+" src="([^"]+)', re.DOTALL).findall(iframes)
        if not links: links = re.compile('<iframe src="([^"]+)', re.DOTALL).findall(iframes)

        for url in links:
            if url.endswith('/soon') or url.startswith('http://soon.'): continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = IDIOMAS.get(lang, lang), quality = quality ))

        links = re.compile('<a href="([^"]+)', re.DOTALL).findall(tabla)

        for url in links:
            if url.endswith('/soon') or url.startswith('http://soon.'): continue

            servidor = servertools.get_server_from_url(url, disabled_servers=True)

            if servidor is None: continue

            servidor = servertools.corregir_servidor(servidor)

            if servertools.is_server_available(servidor):
                if not servertools.is_server_enabled(servidor): continue
            else:
                if not config.get_setting('developer_mode', default=False): continue

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor,
                                  language = IDIOMAS.get(lang, lang), quality = quality, quality_num = puntuar_calidad(quality) ))

    return itemlist


# ~ No hay buscador propio en la web, usan el buscador genérico de google en su site.
def search(item, texto):
    logger.info()
    itemlist2 = []
    itemlist3 = []
    itemlist4 = []

    try:
        item.filtro_search = texto

        item.url = url_estrenos
        itemlist = list_all(item)

        if itemlist:
            item.url = host
            item.group = 'estrenos'
            itemlist2 = list_last(item)

            for it2 in itemlist2:
                if it2.url not in [it.url for it in itemlist]:
                    itemlist.append(it2)

            if itemlist2:
                item.url = host
                item.group = 'novedades'
                itemlist3 = list_last(item)

                for it3 in itemlist3:
                    if it3.url not in [it.url for it in itemlist]:
                        itemlist.append(it3)

            if not itemlist2 and not itemlist3:
                item.url = url_recomendadas
                itemlist4 = list_all(item)

                for it4 in itemlist4:
                    if it4.url not in [it.url for it in itemlist]:
                        itemlist.append(it4)

        return itemlist

    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
