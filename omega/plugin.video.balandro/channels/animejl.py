# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.anime-jl.net/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_animejl_proxies', default=''):
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
    if config.get_setting('channel_animejl_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('animejl', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '/animes?q=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('animejl', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
         if not url.startswith(host):
             data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
         else:
             if hay_proxies:
                 data = httptools.downloadpage_proxy('animejl', url, post=post, headers=headers, timeout=timeout).data
             else:
                 data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>Just a moment...</title>' in data:
        if not '/animes?q=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='animejl', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_animejl', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('animejl') ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes?page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'animes?estado%5B%5D=2&order=created&page=1', search_type = 'tvshow', text_color = 'greenyellow' ))
    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'animes?estado%5B%5D=0&order=created&page=1', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Finalizados', action = 'list_all', url = host + 'animes?estado%5B%5D=1&order=created&page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Donghuas', action = 'list_all', url = host + 'animes?tipo[]=7&order=created&page=1', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'animes?tipo[]=2&order=created&page=1&page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En Castellano/Latino', action = 'list_all', url = host + 'animes?genre[]=46&order=created&page=1', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'animes?tipo[]=3&order=created&page=1', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'animes')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<select name="genre(.*?)</select>')

    matches = re.compile("<option value='(.*?)'.*?>(.*?)</option>").findall(bloque)

    for value, title in matches:
        if title == 'Latino/Español': continue

        url = host + 'animes?genre%5B%5D=' + value + '&order=created&page=1'

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1984, -1):
        url = host + 'animes?year%5B%5D=' + str(x) + '&order=created&page=1'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article(.*?)</article>').findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, "<a href='(.*?)'")
        title = scrapertools.find_single_match(match, "<h3 class='Title'>(.*?)</h3>")

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        plot = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        thumb = host + thumb

        title = title.replace('&#039;', "'").replace('&quot;', '').strip()

        titulo = title

        titulo = titulo.replace('Español Latino', '').replace('Español latino', '').replace('español Latino', '').replace('español latino', '').replace('Español', '').replace('español', '').replace('Castellano', '').replace('castellano', '').strip()

        tipo = 'movie' if '>Pelicula<' in match else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        lang = ''

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            PeliName = corregir_SerieName(title)

            if 'Español Latino' in title or 'Español Latino' in title or 'español Latino' in title or 'español latino' in title: lang = 'Lat'
            elif 'Español' in title or 'español' in title or 'Castellano' in title or 'castellano' in title: lang = 'Esp'

            title = title.replace('Audio', '[COLOR red]Audio[/COLOR]')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, lang=lang, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = PeliName, infoLabels={'year': '-', 'plot': plot} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            SerieName = corregir_SerieName(title)

            if 'Español Latino' in title or 'Español Latino' in title or 'español Latino' in title or 'español latino' in title: lang = 'Lat'
            elif 'Español' in title or 'español' in title or 'Castellano' in title or 'castellano' in title: lang = 'Esp'

            title = title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')

            title = title.replace('Audio', '[COLOR red]Audio[/COLOR]')

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, lang=lang, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-', 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link" href="([^"]+)" rel="next">')

            if next_page:
                next_page = next_page.replace('&amp;', '&')

                itemlist.append(item.clone( title = 'Siguientes ...', url = '%s%s' % (host, next_page) if not host in next_page else next_page,
                                            action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, "<h2>Últimos episodios agregados(.*?)</ul>")

    patron = "<li><a href='(.*?)' class.*?<img src='(.*?)' alt='(.*?)'></span><span class='Capi'>(.*?)</span>"

    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, thumb, title, epis in matches:
        title = title.replace('ver ', '')

        thumb = host + thumb

        SerieName = corregir_SerieName(title)

        season = scrapertools.find_single_match(title, 'Temporada (.*?) ')
        if not season: season = 1

        if not epis.lower() in title: titulo = '%s - %s' % (title, epis)
        else: titulo = title

        epis = epis.replace('Episodio', '').replace('Capítulo', '').strip()

        if '/' in epis: epis = scrapertools.find_single_match(epis, '(.*?)/').strip()

        if not epis: epis = 1

        titulo = titulo.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').replace('temporada', '[COLOR tan]Temp.[/COLOR]')

        titulo = '[COLOR goldenrod]Epis. [/COLOR]' + str(epis) + ' ' + titulo.replace('episodio', '').strip()

        titulo = titulo.replace('Audio', '[COLOR red]Audio[/COLOR]')

        lang = ''

        if 'Español Latino' in title or 'Español Latino' in title or 'español Latino' in title or 'español latino' in title: lang = 'Lat'
        elif 'Español' in title or 'español' in title or 'Castellano' in title or 'castellano' in title: lang = 'Esp'

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, lang=lang,
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber=epis))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    hay_proximo = False
    if 'var anime_info = ' in data: hay_proximo = True

    matches = scrapertools.find_multiple_matches(data, '\[(\d+),"([^"]+)","([^"]+)",[^\]]+\]')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimeJl', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for epis, url, thumb in matches[item.page * item.perpage:]:
        url = "%s/%s" % (item.url, url)

        title = 'Episodio %s' % epis

        if item.contentSerieName: titulo = '1x' + str(epis) + ' ' + title.replace('Episodio ' + str(epis), '').strip() + ' ' + item.contentSerieName
        else: titulo = item.title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

        if len(itemlist) >= item.perpage:
            if hay_proximo:
                blk_cap = scrapertools.find_single_match(str(data), 'var anime_info = (.*?);')

                next_cap = scrapertools.find_single_match(blk_cap, '.*?",".*?",".*?","(.*?)"')

                if next_cap:
                    next_cap = 'Próx. Epis.: ' + next_cap
                    itemlist.append(item.clone( action='', title = next_cap, thumbnail = item.thumbnail, text_color='cyan' ))
            break

    tmdb.set_infoLabels(itemlist)

    if not itemlist:
        if hay_proximo:
            blk_cap = scrapertools.find_single_match(str(data), 'var anime_info = (.*?);')

            next_cap = scrapertools.find_single_match(blk_cap, '.*?",".*?",".*?","(.*?)"')

            if next_cap:
                platformtools.dialog_notification(config.__addon_name, '[COLOR cyan][B]Proximamente[/B][/COLOR]')

                next_cap = 'Próx. Epis.: ' + next_cap
                itemlist.append(item.clone( action='', title = next_cap, thumbnail = item.thumbnail, text_color='cyan', infoLabels={'year': ''} ))

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if not item.search_type == 'tvshow':
        if not '/episodio' in item.url: item.url = item.url + '/episodio-1'

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    lang = item.lang
    if not lang: lang = 'Vose'

    ses = 0

    matches = scrapertools.find_multiple_matches(data, 'video\[\d+\]\s*=\s*\'<iframe.*?src="([^"]+)"')

    for url in matches:
        ses += 1

        if url:
            if url.startswith('//'): url = 'https:' + url

            if url.startswith('https://animejl.top/v/'): url = url.replace('https://animejl.top/v/', 'https://vanfem.com/v/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor == 'zplayer': url = url + '|' + host

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    # ~ descargas  no se tratan por anomizador

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def corregir_SerieName(SerieName):
    logger.info()

    if 'Audio' in SerieName: SerieName = SerieName.split("Audio")[0]

    if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
    if 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]

    if 'Español Latino' in SerieName: SerieName = SerieName.split("Español Latino")[0]
    elif 'Español Latino' in SerieName: SerieName = SerieName.split("español Latino")[0]
    elif 'español Latino' in SerieName: SerieName = SerieName.split("español Latino")[0]
    elif 'español latino' in SerieName: SerieName = SerieName.split("español latino")[0]

    if 'Español' in SerieName: SerieName = SerieName.split("Español")[0]
    elif 'español' in SerieName: SerieName = SerieName.split("español")[0]
    elif 'Castellano' in SerieName: SerieName = SerieName.split("Castellano")[0]
    elif 'castellano' in SerieName: SerieName = SerieName.split("castellano")[0]

    if '(Sin Censura)' in SerieName: SerieName = SerieName.split("(Sin Censura)")[0]

    if 'Películas' in SerieName: SerieName = SerieName.split("Películas")[0]

    if 'Ovas' in SerieName: SerieName = SerieName.split("Ovas")[0]
    if 'Ova' in SerieName: SerieName = SerieName.split("Ova")[0]

    if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]

    if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
    if 'season' in SerieName: SerieName = SerieName.split("season")[0]

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
        item.url = host + 'animes?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

