# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://latanime.org/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_latanime_proxies', default=''):
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
    hay_proxies = False
    if config.get_setting('channel_latanime_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('latanime', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not 'buscar?p=1&q=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('LatAnime', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('latanime', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>Just a moment...</title>' in data:
        if not 'buscar?p=1&q=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='latanime', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_latanime', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('latanime') ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes?p=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'emision?p=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En blu-ray', action = 'list_all', url = host + 'animes?genero=blu-ray', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'pelis', group = 'cats', search_type = 'movie', text_color='deepskyblue' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', group = 'cats', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En 1080p', action = 'list_all', url = host + 'animes?fecha=false&genero=false&letra=false&categoria=pelicula-1080p', text_color='deepskyblue' ))
    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'animes?fecha=false&genero=false&letra=false&categoria=Película+Castellano', text_color='deepskyblue' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'animes?fecha=false&genero=false&letra=false&categoria=Película+Latino', text_color='deepskyblue' ))
    itemlist.append(item.clone( title = 'Otras', action = 'list_all', url = host + 'animes?fecha=false&genero=false&letra=false&categoria=Película', text_color='deepskyblue' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'animes?fecha=false&genero=false&letra=false&categoria=castellano', search_type = 'tvshow', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En catalán', action = 'list_all', url = host + 'animes?fecha=false&genero=false&letra=false&categoria=catalan', search_type = 'tvshow', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'animes?fecha=false&genero=false&letra=false&categoria=latino', search_type = 'tvshow', text_color='moccasin' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = host + 'animes'

    data = do_downloadpage(url_cat)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'name="categoria"(.*?)>Categoria<')

    matches = re.compile('<optionvalue="(.*?)">(.*?)</option>').findall(bloque)

    for categoria, title in matches:
        if title == "Seleccionar": continue
        elif title == "PREESTRENO": continue

        elif title == 'Castellano': continue
        elif title == 'Latino': continue
        elif title == 'Catalán': continue

        elif 'Pelicula' in title or 'Película' in title: continue

        url = url_cat + '?fecha=false&genero=false&letra=false&categoria=' + categoria

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='moccasin' ))

    return sorted(itemlist,key=lambda x: x.title)


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + 'animes'

    data = do_downloadpage(url_genre)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'name="genero"(.*?)</select>')

    matches = re.compile('<optionvalue="(.*?)">(.*?)</option>').findall(bloque)

    for genre, title in matches:
        title = title.strip()

        if title == 'Seleccionar': continue
        elif title == 'Castellano': continue
        elif title == 'Latino': continue

        elif title == 'Blu-ray': continue

        url = url_genre + '?fecha=false&genero=' + genre + '&letra=false&categoria=false'

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1979, -1):
        url = host + 'animes' + '?fecha=' + str(x) + '&genero=false&letra=false&categoria=false'

        itemlist.append(item.clone( title = str(x), action = 'list_all', url = url, text_color='springgreen' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if letra == '#': letter = '09'
        else: letter = letra.lower()

        url = host + 'animes' + '?fecha=false&genero=false&letra=' + letter + '&categoria=false'

        itemlist.append(item.clone( title = letra, action = 'list_all', url = url, letra = letter, text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="row">(.*?)<nav>')

    if not bloque:
        if item.group == 'cats':
            hay_cat = scrapertools.find_single_match(item.url, '&categoria=(.*?)$')

            if hay_cat:
                bloque = scrapertools.find_single_match(data, '>Categoria<.*?<div class="row">(.*?)<nav>')
                if not bloque: bloque = scrapertools.find_single_match(data, '>Categoria<.*?<div class="row">(.*?)</footer>')
            else: bloque = scrapertools.find_single_match(data, '<div class="row">(.*?)</footer>')

        else: bloque = scrapertools.find_single_match(data, '<div class="row">(.*?)</footer>')

    matches = re.compile('<div class="col-md-4 col-lg-3 col-xl-2 col-6 my-3">(.*?)</div></a></div>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'class="my-1">(.*?)</h3')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '</svg>(.*?)</span>').strip()

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        title = title.replace('&#039;s', "'s").replace('&#039;', '').replace('&quot;', '').replace('&amp;', '').strip()

        SerieName = corregir_SerieName(title)

        tipo = 'movie' if '-pelicula' in url or '-movie' in url or '>Película<' in match or '>Pelicula' in match else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        title = title.replace('Audio', '[COLOR red]Audio[/COLOR]').replace('Catalán', '[COLOR yellowgreen]Catalán[/COLOR]')

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = SerieName, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            title = title.replace(' S1 ', '[COLOR tan] S1 [/COLOR]').replace(' S2 ', '[COLOR tan] S2 [/COLOR]').replace(' S3 ', '[COLOR tan] S3 [/COLOR]').replace(' S4 ', '[COLOR tan] S4 [/COLOR]')

            title = title.replace(' S5 ', '[COLOR tan] S5 [/COLOR]').replace(' S6 ', '[COLOR tan] S6 [/COLOR]').replace(' S7 ', '[COLOR tan] S7 [/COLOR]').replace(' S8 ', '[COLOR tan] S8 [/COLOR]')

            title = title.replace(' S9 ', '[COLOR tan] S9 [/COLOR]')

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<ul class="pagination">.*?<li class="page-item active".*?</li>.*?href="(.*?)"')

            if next_page:
                if '?p=' in next_page or 'p=' in next_page:
                    next_page = next_page.replace('&amp;', '&')

                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'Añadidos recientemente<(.*?)>Series recientes<')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="col-6 col-md-6 col-lg-3 mb-3">.*?<a href="(.*?)".*?data-src="(.*?)".*?alt="(.*?)"')

    for url, thumb, title in matches:
        title = title.replace('&#039;s', "'s").replace('&#039;', '').replace('&quot;', '').replace('&amp;', '').strip()

        SerieName = corregir_SerieName(title)

        epis = scrapertools.find_single_match(title, 'capitulo(.*?)$').strip()

        if not epis: epis = 1

        titulo = '[COLOR goldenrod]Epis. [/COLOR]' + str(epis) + ' ' + title.replace('capitulo '+ str(epis), '').strip()

        titulo = titulo.replace(' S1 ', '[COLOR tan] S1 [/COLOR]').replace(' S2 ', '[COLOR tan] S2 [/COLOR]').replace(' S3 ', '[COLOR tan] S3 [/COLOR]').replace(' S4 ', '[COLOR tan] S4 [/COLOR]')

        titulo = titulo.replace(' S5 ', '[COLOR tan] S5 [/COLOR]').replace(' S6 ', '[COLOR tan] S6 [/COLOR]').replace(' S7 ', '[COLOR tan] S7 [/COLOR]').replace(' S8 ', '[COLOR tan] S8 [/COLOR]')

        titulo = titulo.replace(' S9 ', '[COLOR tan] S9 [/COLOR]')

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb,
                                    contentSerieName=SerieName, contentType='episode',
                                    contentSeason=1, contentEpisodeNumber=epis, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Capítulos<(.*?)</script>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?alt="(.*?)"')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?</svg>(.*?)</div>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('LatAnime', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, title in matches[item.page * item.perpage:]:
        if not url or not title: continue

        title = title.replace('&#039;s', "'s").replace('&quot;', '').replace('&amp;', '').strip()

        epis = scrapertools.find_single_match(title, 'Capitulo(.*?)$').strip()
        if not epis: epis = scrapertools.find_single_match(title, 'capitulo(.*?)$').strip()

        if not epis: epis = 1

        titulo = '1x' + str(epis) + ' ' + title.replace('Capitulo ' + str(epis), '').replace('capitulo ' + str(epis), '' ).strip()

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

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

    if not item.search_type == 'tvshow':
        if not '-episodio-' in item.url: item.url = item.url.replace('/anime/', '/ver/') + '-episodio-1'

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    links = scrapertools.find_multiple_matches(data, 'data-player="(.*?)"')

    if not links: return itemlist

    ses = 0

    for url in links:
        ses += 1

        url = base64.b64decode(url).decode('utf-8')

        if url.startswith("https://sb"): continue

        elif '/lvturbo.' in url: continue
        elif 'fembed' in url: continue
        elif 'streamsb' in url: continue
        elif 'playersb' in url: continue

        elif '.monoschinos2.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'directo':
            other = url
            if '/lulu' in url: servidor = 'various'

        if servidor == 'various': other = servertools.corregir_other(url)

        if '-castellano-' in item.url: lang = 'Esp'
        elif '-latino-' in item.url: lang = 'Lat'
        elif '-catalan-' in item.url: lang = 'Cat'
        else: lang = 'Vose'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def corregir_SerieName(SerieName):
    logger.info()

    if 'Película' in SerieName: SerieName = SerieName.split("Película")[0]

    if 'Castellano' in SerieName: SerieName = SerieName.split("Castellano")[0]
    elif 'Latino' in SerieName: SerieName = SerieName.split("Latino")[0]
    elif 'Catalán' in SerieName: SerieName = SerieName.split("Catalán")[0]

    if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
    if 'season' in SerieName: SerieName = SerieName.split("season")[0]

    if ' Live Action' in SerieName: SerieName = SerieName.split(" Live Action")[0]

    if ' Especiales' in SerieName: SerieName = SerieName.split(" Especiales")[0]
    elif ' Especial' in SerieName: SerieName = SerieName.split(" Especial")[0]
    elif ' Specials' in SerieName: SerieName = SerieName.split(" Specials")[0]
    elif ' Special' in SerieName: SerieName = SerieName.split(" Special")[0]

    if ' OVA ' in SerieName: SerieName = SerieName.split(" OVA ")[0]
    elif ' Ova ' in SerieName: SerieName = SerieName.split(" Ova ")[0]
    elif " OVA's " in SerieName: SerieName = SerieName.split(" OVA's ")[0]
    elif " Ova's " in SerieName: SerieName = SerieName.split(" Ova's ")[0]

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
        item.url = host + 'buscar?p=1&q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

