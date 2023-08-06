# -*- coding: utf-8 -*-

import base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://pelispedia.one/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://pelispedia.co/', 'https://www.pelispedia.de/', 'https://pelispedia.de/']


domain = config.get_setting('dominio', 'pelispedia', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'pelispedia')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'pelispedia')
    else: host = domain


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_pelispedia_proxies', default=''):
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

    if '/release/' in url: raise_weberror = False

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    else:
        data = httptools.downloadpage_proxy('pelispedia', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'pelispedia', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_pelispedia', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='pelispedia', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_pelispedia', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone ( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone ( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    opciones = [
        ('Acción', 'accion'),
        ('Action & Adventure', 'action-adventure'),
        ('Animación', 'animacion'),
        ('Aventura', 'aventura'),
        ('Bélica', 'belica'),
        ('Ciencia ficción', 'ciencia-ficcion'),
        ('Comedia', 'comedia'),
        ('Crimen', 'crimen'),
        ('Documental', 'documental'),
        ('Drama', 'drama'),
        ('Familia', 'familia'),
        ('Fantasía', 'fantasia'),
        ('Halloween', 'halloween'),
        ('Historia', 'historia'),
        ('Kids', 'kids'),
        ('Misterio', 'misterio'),
        ('Música', 'musica'),
        ('Película de TV', 'pelicula-de-tv'),
        ('Reality', 'reality'),
        ('Romance', 'romance'),
        ('Sci-Fi & Fantasy', 'sci-fi-fantasy'),
        ('Suspense', 'suspense'),
        ('Terror', 'terror'),
        ('War & Politics', 'war-politics'),
        ('Western', 'western')
        ]

    for tit, opc in opciones:
        if item.search_type == 'movie':
           if tit == 'Kids': continue
           elif tit == 'Reality': continue
           elif tit == 'Sci-Fi & Fantasy': continue
           elif tit == 'War & Politics': continue
        else:
           if tit == 'Aventura': continue
           elif tit == 'Bélica': continue
           elif tit == 'Ciencia ficción': continue
           elif tit == 'Familia': continue
           elif tit == 'Fantasía': continue
           elif tit == 'Halloween': continue
           elif tit == 'Historia': continue
           elif tit == 'Música': continue
           elif tit == 'Película de TV': continue
           elif tit == 'Romance': continue
           elif tit == 'Suspense': continue
           elif tit == 'Terror': continue
           elif tit == 'Western': continue

        itemlist.append(item.clone( title = tit, url = host + opc + '/', action='list_all', text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1949, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'release/' + str(x) + '/', action='list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        if not url: url = scrapertools.find_single_match(article, ' href=([^ >]+)')

        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>')
        if not title: title = scrapertools.find_single_match(article, '<h4>(.*?)</h4>')
        if not title: title = scrapertools.find_single_match(article, ' alt="([^"]+)"')

        if not url or not title: continue

        if '|' in title:
            title = title.split('|')[0]
            title = title.strip()

        title = title.replace('&#8217;', '')

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src=([^ >]+)')

        year = scrapertools.find_single_match(article, '<span class="year">(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, ' (\d{4})</span>')
        if not year and '/release/' in item.url: year = scrapertools.find_single_match(item.url, '/release/(\d{4})')
        if not year: year = '-'

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            qlty = scrapertools.find_single_match(article, '<span class="Qlty">([^<]+)')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<nav class="pagination mat2 tac">' in data:
            bloque = scrapertools.find_single_match(data, '<nav class="pagination mat2 tac">(.*?)</nav>')

            prev_page = ''
            if 'Anterior' in bloque: prev_page = 'Anterior.*?'

            next_page = scrapertools.find_single_match(bloque, prev_page + '<a href="(.*?)"')

            if '/page/' in next_page:
                itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'click="tab = ' + "'season-(.*?)'" + '">T(.*?)</button>')
    for nro_temp, tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.url = item.url
            item.nrotemp = nro_temp
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = item.url, page = 0, nrotemp = nro_temp, contentType = 'season', contentSeason = tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    tempo = scrapertools.find_single_match(data, 'x-show="tab === ' + "'season-" + str(item.nrotemp) + '(.*?)</div>')

    matches = scrapertools.find_multiple_matches(tempo, '<article(.*?)</article>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PelisPedia', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPedia', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPedia', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPedia', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PelisPedia', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PelisPedia', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, ' href="([^"]+)')

        season = scrapertools.find_single_match(match, 'class="pdx brd1 dib vat black-bg mar yellow-co">(.*?) -').strip()
        episode = scrapertools.find_single_match(match, 'class="pdx brd1 dib vat black-bg mar yellow-co">.*? - (.*?)</span>').strip()

        if not url or not season or not episode: continue

        thumb = scrapertools.find_single_match(match, ' data-src="([^"]+)')

        title = scrapertools.find_single_match(match, '<h2 class="ttl tvw fz4 mab">(.*?)</h2>')

        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, contentType='episode', contentSeason=item.contentSeason, contentEpisodeNumber=episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['cam', 'tsscreener', 'brscreener', 'sd240p', 'sd480p', 'dvdrip', 'hd', 'hdrip', 'hd720p', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'fcom': return 'fembed'
    elif servidor in ['mp4', 'api', 'drive']: return 'gvideo'
    elif servidor in ['stream', 'stream-mx', 'stream mx', 'streammx', 'mx server']: return 'directo'
    else: return servidor


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es': 'Esp',
       'mx': 'Lat',
       'en': 'Vose',
       'spanish': 'Esp',
       'español': 'Esp',
       'castellano': 'Esp',
       'latino': 'Lat',
       'subtitulado': 'Vose',
       'inglés sub': 'Vose',
       'ingles sub': 'Vose',
       'inglés': 'VO',
       'ingles': 'VO'
       }

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<div class="op-srv brd1"(.*?)</div>')

    ses = 0

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, ' data-url="(.*?)"')
        if not url: url = scrapertools.find_single_match(match, ' data-src="(.*?)"')
        if not url: continue

        server = scrapertools.find_single_match(match, '<span class="ttu db tvw white-co">(.*?)</span>').lower()
        if not server: continue

        server = corregir_servidor(server)

        modif = scrapertools.find_single_match(match, '<span class="ttu db tvw fz2">(.*?)</span>')
        modif = modif.replace(' | ', ' - ')

        lang = scrapertools.find_single_match(modif, '(.*?) -').lower().strip()
        qlty = scrapertools.find_single_match(modif, '- (.*?)$').strip()

        if not '//' in url: server = 'directo'

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, referer = item.url, title = '', url = url, language = IDIOMAS.get(lang, lang), quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if not '//' in url:
        url_b64 = base64.b64decode(url)

        if "b'" in str(url_b64): url_b64 = scrapertools.find_single_match(str(url_b64), "b'(.*?)'$")

        url_b64 = url_b64.replace('&#038;', '&').replace('&amp;', '&')

        if not url_b64.startswith(host):
            data = httptools.downloadpage(url_b64, raise_weberror = False).data
        else:
            data = httptools.downloadpage_proxy('pelispedia', url_b64, raise_weberror = False).data

        if '/privatelink.de/' in data or '/www.privatelink.de/' in data: return itemlist

        if '.bayfiles.' in data or '.anonfiles.' in data:
            new_url = scrapertools.find_single_match(data, '<a type="button" id="download-url".*?href="(.*?)"')
            if new_url:
                itemlist.append(item.clone(server = 'directo', url = new_url))
                return itemlist

        new_url = scrapertools.find_single_match(data, '<h1 class.*?<a href="(.*?)"')
        if not new_url: new_url = scrapertools.find_single_match(data, ' src="(.*?)"')
        if not new_url: new_url = scrapertools.find_single_match(data, ' SRC="(.*?)"')

        if new_url:
            new_url = new_url.replace('&#038;', '&').replace('&amp;', '&')

            if 'stream-mx.com/' in new_url:
                fid = scrapertools.find_single_match(new_url, "id=([^&]+)")
                if not fid: return itemlist

                url = 'https://stream-mx.com/player.php?id=%s&v=2&ver=si' % fid

                data = httptools.downloadpage(url, headers={'Referer': new_url}).data

                bloque = scrapertools.find_single_match(data, '"sources":\s*\[(.*?)\]')
                for enlace in scrapertools.find_multiple_matches(bloque, "\{(.*?)\}"):
                    v_url = scrapertools.find_single_match(enlace, '"file":\s*"([^"]+)')
                    if not v_url: continue

                    v_type = scrapertools.find_single_match(enlace, '"type":\s*"([^"]+)')
                    if v_type == 'hls':
                       itemlist.append(item.clone(url = v_url, server = 'm3u8hls'))
                    else:
                       v_lbl = scrapertools.find_single_match(enlace, '"label":\s*"([^"]+)')
                       itemlist.append([v_lbl, v_url])

                return itemlist

            if '/hqq.' in new_url or '/waaw.' in new_url or '/netu.' in new_url:
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

            elif '/pelisplayer.xyz/' in new_url:
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

            servidor = servertools.get_server_from_url(new_url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor: itemlist.append(item.clone(server = servidor, url = new_url))
            else: itemlist.append(item.clone(server = 'directo', url = new_url))

        return itemlist

    if '/o.php?l=' in item.url:
        url = scrapertools.find_single_match(item.url, "/o\.php\?l=(.*)")

        for i in range(9): # range(5)
            url = base64.b64decode(url)
            if url.startswith('http'): break

        if not url.startswith('http'): url = ''

    elif url.startswith('https://streamcrypt.net/'):
        url = httptools.downloadpage(url, follow_redirects=False).headers.get('location', '')

        if url:
            url = url.replace('?id=', '?p=2&id=')
            url = httptools.downloadpage(url, follow_redirects=False).headers.get('location', '')
        else:
            data = do_downloadpage(url)
            url = scrapertools.find_single_match(data, "window.open.*?'(.*?)'")

    else:
        item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')

        if not item.url.startswith(host):
            resp = httptools.downloadpage(item.url, headers={'Referer': item.referer}, follow_redirects=False)
        else:
            resp = httptools.downloadpage_proxy('pelispedia', item.url, headers={'Referer': item.referer}, follow_redirects=False)

        if 'location' in resp.headers: 
            url = resp.headers['location']
        else:
            url = scrapertools.find_single_match(resp.data, "src='([^']+)")
            if not url: url = scrapertools.find_single_match(resp.data, 'src="([^"]+)')
            if not url: url = scrapertools.find_single_match(resp.data, 'src=([^ >]+)')
            if not url: url = scrapertools.find_single_match(resp.data, '"embed_url":"([^"]+)')

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        elif '/pelisplayer.xyz/' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor:
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone(url=url, server=servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
