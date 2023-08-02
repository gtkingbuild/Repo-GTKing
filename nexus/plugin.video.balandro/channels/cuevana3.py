# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://cuevana3.be/'


# ~ por si viene de enlaces guardados
ant_hosts = ['http://www.cuevana3.co/', 'https://cuevana3.co/', 'https://cuevana3.io/',
             'https://cuevana3.me/', 'https://ww1.cuevana3.me/', 'https://ww2.cuevana3.me/',
             'https://ww3.cuevana3.me/', 'https://ww4.cuevana3.me/,' 'https://ww5.cuevana3.me/',
             'https://c3.cuevana3.me/', 'https://s3.cuevana3.me/', 'https://es.cuevana3.me/',
             'https://a2.cuevana3.me/', 'https://b2.cuevana3.me/', 'https://d2.cuevana3.me/',
             'https://e2.cuevana3.me/', 'https://g2.cuevana3.me/', 'https://z2.cuevana3.me/',
             'https://s2.cuevana3.me/', 'https://m2.cuevana3.me/', 'https://n2.cuevana3.me/',
             'https://ver.cuevana3.me/', 'https://u2.cuevana3.me/', 'https://u3.cuevana3.me/',
             'https://n3.cuevana3.me/', 'https://v3.cuevana3.me/', 'https://m3.cuevana3.me/',
             'https://z3.cuevana3.me/', 'https://t3.cuevana3.me/', 'https://v3.cuevana3.me/',
             'https://d3.cuevana3.me/', 'https://r3.cuevana3.me/', 'https://k3.cuevana3.me/',
             'https://p3.cuevana3.me/', 'https://c1.cuevana3.me/', 'https://e1.cuevana3.me/',
             'https://a1.cuevana3.me/', 'https://z1.cuevana3.me/', 'https://b1.cuevana3.me/',
             'https://q1.cuevana3.me/', 'https://o1.cuevana3.me/', 'https://l2.cuevana3.me/',
             'https://j2.cuevana3.me/', 'https://k2.cuevana3.me/', 'https://o2.cuevana3.me/',
             'https://y2.cuevana3.me/', 'https://f3.cuevana3.me/', 'https://h3.cuevana3.me/',
             'https://j3.cuevana3.me/', 'https://l3.cuevana3.me/', 'https://y4.cuevana3.me/',
             'https://b4.cuevana3.me/', 'https://u4.cuevana3.me/', 'https://r4.cuevana3.me/',
             'https://cuevana3.ai/', 'https://ww1.cuevana3.ai/', 'https://ww2.cuevana3.ai/',
             'https://www1.cuevana3.ai/', 'https://www2.cuevana3.ai/', 'https://www4.cuevana3.ai/']


domain = config.get_setting('dominio', 'cuevana3', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'cuevana3')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'cuevana3')
    else: host = domain


IDIOMAS = {'Latino': 'Lat', 'Español': 'Esp', 'Subtitulado': 'Vose'}


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_cuevana3_proxies', default=''):
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


def do_downloadpage(url, post=None, headers=None, follow_redirects=True, only_headers=False):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ resp = httptools.downloadpage(url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers)
    resp = httptools.downloadpage_proxy('cuevana3', url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers)

    if only_headers: return resp.headers
    return resp.data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'cuevana3', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_cuevana3', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='cuevana3', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_cuevana3', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas-mas-valoradas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'peliculas-mas-vistas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catalogo', action = 'list_all', url = host + 'serie', filtro = 'tabserie-1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'serie', filtro = 'tabserie-2', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'serie', filtro = 'tabserie-3', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'serie', filtro = 'tabserie-4', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'peliculas-espanol', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'peliculas-latino', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'peliculas-subtituladas', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    matches = re.compile('/(category/[^ >]+)>([^<]+)</a></li>', re.DOTALL).findall(data)

    for url, title in matches:
        itemlist.append(item.clone( title=title, url=host + url, action='list_all', search_type = item.search_type ))

    if itemlist:
        itemlist.append(item.clone( title='Suspense', url=host + 'category/suspense', action='list_all', search_type = item.search_type ))
        itemlist.append(item.clone( title='Western', url=host + 'category/western', action='list_all', search_type = item.search_type ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if item.page:
        post = {'page': item.page}
        if item.filtro == 'tabserie-1': post['action'] = 'cuevana_ajax_pagination'
        elif item.filtro == 'tabserie-2': post['action'] = 'cuevana_ajax_pagination_estreno'
        elif item.filtro == 'tabserie-3': post['action'] = 'cuevana_ajax_pagination_rating'
        elif item.filtro == 'tabserie-4': post['action'] = 'cuevana_ajax_pagination_view'

        data = do_downloadpage(host+'wp-admin/admin-ajax.php', post=post)
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    else:
        data = do_downloadpage(item.url)
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

        if item.filtro:
            data = scrapertools.find_single_match(data, '<div id="%s(.*?)</div></nav>' % item.filtro)

    matches = re.compile('<li\s*class="[^"]*TPostMv">(.*?)</li>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, '\s*href=(?:"|)([^ >"]+)')

        title = scrapertools.find_single_match(article, '<h2 class="Title">([^<]+)</h2>')

        if not url or not title: continue

        if '/pagina-ejemplo' in url: continue

        thumb = scrapertools.find_single_match(article, 'data-src=([^ >]+)')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src=(?:"|)([^ >"]+)')

        year = scrapertools.find_single_match(article, '<span\s*class=(?:"|)Year(?:"|)>(\d+)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(article, '<span\s*class=(?:"|)Qlty(?:"|)>([^<]+)</span>')

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page or '?paged=' in next_page:
                if not item.filtro:
                    itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_all', text_color='coral' ))
                else:
                    pagina = 2 if not item.page else item.page + 1

                    itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_all', page=pagina, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<option value=".*?>Temporada(.*?)</option>', re.DOTALL).findall(data)

    for tempo in matches:
        tempo = tempo.strip()

        title = 'Temporada ' + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    if item.contentSeason:
        data = scrapertools.find_single_match(data, '<ul id="season-' + str(item.contentSeason) + '(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</li>', re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Cuevana3', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Cuevana3', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Cuevana3', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for url, datos in matches[item.page * item.perpage:]:
        try:
            season, epis = scrapertools.find_single_match(url, '-(\d+)x(\d+)$')
        except:
            season = scrapertools.find_single_match(url, '-(\d+)x')
            epis = scrapertools.find_single_match(url, '-.*?x(\d+)$')

        if item.contentSeason:
            if not str(item.contentSeason) == str(season): continue

        title = scrapertools.find_single_match(datos, '<h2[^>]*>(.*?)</h2>')
        thumb = scrapertools.find_single_match(datos, 'data-src=([^ >]+)"')

        itemlist.append(item.clone( action='findvideos', title = title, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['Cam', 'WEB-S', 'DVD-S', 'TS-HQ', 'DVD', 'DvdRip', 'HD', 'FullHD1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<li data-TPlayerNv="Opt(\w\d+).*?<span class="cdtr"><span>\d+ - (.*?) - ([^<]+)<', re.DOTALL).findall(data)

    ses = 0

    for option, lang, qlty in matches:
        ses += 1

        if ' - ' in lang: lang = scrapertools.find_single_match(qlty, '(.*?)-').strip()

        if ' - ' in qlty: qlty = scrapertools.find_single_match(qlty, ' - (.*?)$').strip()

        url = scrapertools.find_single_match(data, '<div class="TPlayerTb".*?id="Opt%s".*?data-src="(.*?)"' % option)

        if url.startswith('//'): url = 'https:' + url

        if url and 'youtube' not in url:
            url = url.replace('#Synchronization+Service', '')

            itemlist.append(Item( channel = item.channel, action = 'play', other = option, title = '', url = url, referer = item.url,
                                  language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) ))

    # Enlaces descarga
    patron = 'Uptobox</td><td>([^<]*)</td><td><span>([^<]*)</span></td><td><a\s*rel=nofollow target=_blank href="([^"]+)" class="Button STPb">Descargar</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for lang, qlty, url in matches:
        ses += 1

        if ' - ' in lang: lang = scrapertools.find_single_match(qlty, '(.*?)-').strip()

        if ' - ' in qlty: qlty = scrapertools.find_single_match(qlty, ' - (.*?)$').strip()

        if url.startswith('/'): url = 'https:' + url

        itemlist.append(Item( channel = item.channel, action = 'play', other = 'D', server = 'uptobox', title = '', url = url, referer = item.url,
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) ))

    itemlist = servertools.get_servers_itemlist(itemlist)

    # Dejar desconocidos como directos
    for it in itemlist:
        if it.server == 'desconocido' and ('//api.cuevana3' in it.url or '//apialfa' in it.url or '//damedamehoy.' in it.url or '//tomatomatela.' in it.url or '//apialfa.' in it.url):
            it.server = 'fembed' if '/fembed/?' in it.url else 'directo' if '//damedamehoy.' in it.url or '//tomatomatela.' or '//apialfa.' in it.url else ''
        elif it.server == 'desconocido' and 'openloadpremium.com/' in it.url:
            it.server = 'm3u8hls'

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


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

    if '//damedamehoy.' in item.url or '//tomatomatela.' in item.url:
        url = resuelve_dame_toma(item.url)
        if url: itemlist.append(['mp4', url])
        return itemlist

    if '//api.cuevana3' in item.url or '//apialfa' in item.url:
        if 'file=' in item.url:
            fid = scrapertools.find_single_match(item.url, "file=([^&]+)").replace('\\/', '/')
            url = 'https://api.cuevana3.me/stream/plugins/gkpluginsphp.php'
            data = do_downloadpage(url, post={'link': fid})

            enlaces = scrapertools.find_multiple_matches(data, '"link":"([^"]+)"([^}]*)')
            for url, resto in enlaces:
                if 'player.php?id=' in url:
                    url = url.replace('player.php?id=', 'index/').replace('&hlsfe=yes', '.m3u8')
                    data = do_downloadpage(url)
                    matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+)\s*(.*?\.m3u8)')
                    if matches:
                        for res, url in sorted(matches, key=lambda x: int(x[0]), reverse=True):
                            itemlist.append(item.clone(url = url, server = 'm3u8hls'))
                            break
                        return itemlist

                elif 'openloadpremium.com/embed/' in url:
                    url = '' # no encontrado ningún ejemplo válido

                else:
                    lbl = scrapertools.find_single_match(resto, '"label":"([^"]+)')
                    if not lbl: lbl = scrapertools.find_single_match(resto, '"type":"([^"]+)')
                    if not lbl: lbl = 'mp4'
                    itemlist.append([lbl, url])

            itemlist.sort(key=lambda it: int(it[0].replace('p','')) if it[0].endswith('p') else it[0])

        elif 'h=' in item.url:
            fid = scrapertools.find_single_match(item.url, "h=([^&]+)")
            if 'https://api.cuevana3.me/sc/index.php?h=' in item.url:
                api_url = 'https://api.cuevana3.me/sc/r.php'
                api_post = 'h=' + fid
            elif 'https://api.cuevana3.me/ir/goto_ddh.php' in item.url:
                api_url = 'https://api.cuevana3.me/ir/redirect_ddh.php'
                api_post = 'url=' + fid
            else:
                api_url = 'https://api.cuevana3.me/ir/rd.php'
                api_post = 'url=' + fid

            url = do_downloadpage(api_url, post=api_post, headers={'Referer': item.url}, follow_redirects=False, only_headers=True).get('location', '')

            if url.startswith('//'): url = 'https:' + url
 
            if 'h=' in url:
                fid = scrapertools.find_single_match(url, "h=([^&]+)")
                if 'https://api.cuevana3.me/sc/index.php?h=' in url:
                    api_url = 'https://api.cuevana3.me/sc/r.php'
                    api_post = 'h=' + fid
                elif 'https://api.cuevana3.me/ir/goto_ddh.php' in url:
                    api_url = 'https://api.cuevana3.me/ir/redirect_ddh.php'
                    api_post = 'url=' + fid
                else:
                    api_url = 'https://api.cuevana3.me/ir/rd.php'
                    api_post = 'url=' + fid

                url = do_downloadpage(api_url, post=api_post, headers={'Referer': item.url}, follow_redirects=False, only_headers=True).get('location', '')

                if url.startswith('//'): url = 'https:' + url

            if '/hqq.' in url or '/waaw.' in url or '/netu.' in url or 'gounlimited' in url:
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

            if '//damedamehoy.' in url or '//tomatomatela.' in url:
                url = resuelve_dame_toma(url)
                if url:
                    itemlist.append(['mp4', url])
            else:
                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                if servidor != 'directo':
                    url = servertools.normalize_url(servidor, url)
                    itemlist.append(item.clone( url = url, server = servidor ))
                else:
                    fid = scrapertools.find_single_match(url, "id=([^&]+)")
                    if fid:
                        url = url.replace('public/dist/index.html?id=', 'hls/') + '/' + fid + '.playlist.m3u8'
                        itemlist.append(['m3u8', url])

    elif 'openloadpremium.com/' in item.url and '/player.php?' in item.url:
        data = do_downloadpage(item.url, headers={'Referer': item.referer})
        url = scrapertools.find_single_match(data, '"file": "([^"]+)')
        if url:
            if 'openloadpremium.com/mp4/' in url and 'hash=' in url: 
                itemlist.append(item.clone(url = url+'|Referer='+item.url, server='directo'))
            else:
                itemlist.append(item.clone(url = url))

    else:
        itemlist.append(item.clone())

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search/' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

