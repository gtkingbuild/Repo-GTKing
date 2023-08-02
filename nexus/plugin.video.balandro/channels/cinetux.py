# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://cinetux.nu/'


# ~ por si viene de enlaces guardados
ant_hosts = ['http://cinetux.nu/', 'https://www.cinetux.to/', 'https://cinetux.to/',
             'https://www.cinetux.nu/',]


domain = config.get_setting('dominio', 'cinetux', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'cinetux')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'cinetux')
    else: host = domain


IDIOMAS = {'Latino': 'Lat', 'Subtitulado': 'Vose', 'Español': 'Esp', 'Espa%C3%B1ol': 'Esp', 'SUB': 'VO' }


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_cinetux_proxies', default=''):
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
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('cinetux', url, post=post, headers=headers).data
    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'cinetux', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_cinetux', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='cinetux', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_cinetux', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

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

    itemlist.append(item.clone( title='Catálogo', action='peliculas', url=host + 'pelicula/' ))

    itemlist.append(item.clone( title='Estrenos', action='peliculas', url=host + 'genero/estrenos/' ))
    itemlist.append(item.clone( title='Destacadas', action='peliculas', url=host + 'mas-vistos/?get=movies' ))

    itemlist.append(item.clone( title='Por idioma', action='idiomas' ))
    itemlist.append(item.clone( title='Por género', action='generos' ))
    itemlist.append(item.clone( title='Por año', action = 'anios' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='peliculas', title='Español', url= host + 'idioma/espanol/' ))
    itemlist.append(item.clone( action='peliculas', title='Latino', url= host + 'idioma/latino/' ))
    itemlist.append(item.clone( action='peliculas', title='Subtitulado', url= host + 'idioma/subtitulado/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = do_downloadpage(host)
    bloque = scrapertools.find_single_match(data, '(?s)dos_columnas">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, ' href="/([^"]+)">([^<]+)')

    for scrapedurl, scrapedtitle in matches:
        if '/estrenos/' in scrapedurl: continue

        if descartar_xxx and scrapertools.es_genero_xxx(scrapedtitle): continue

        itemlist.append(item.clone( action='peliculas', title=scrapedtitle.strip(), url=host + scrapedurl ))

    if itemlist:
        if 'genero/belica/' not in bloque:
            itemlist.append(item.clone( action='peliculas', title='Bélica', url=host + 'genero/belica/' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for ano in range(current_year, 1938, -1):
        itemlist.append(item.clone( action = 'peliculas', title = str(ano), url = host + 'ano/' + str(ano) + '/' ))

    return itemlist


def extraer_show_showalt(title):
    if ' / ' in title: # pueden ser varios títulos traducidos ej: Lat / Cast, Cast / Lat / Eng, ...
        aux = title.split(' / ')
        show = aux[0].strip()
        showalt = aux[-1].strip()
    else:
        show = title.strip()
        showalt = scrapertools.find_single_match(show, '\((.*)\)$') # si acaba en (...) puede ser el título traducido ej: Lat (Cast)
        if showalt != '':
            show = show.replace('(%s)' % showalt, '').strip()
            if showalt.isdigit(): showalt = '' # si sólo hay dígitos no es un título alternativo

    return show, showalt


def peliculas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article id="[^"]*" class="item movies">(.*?)</article>')

    for article in matches:
        thumb, title = scrapertools.find_single_match(article, ' src="([^"]+)" alt="([^"]+)')
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        year = scrapertools.find_single_match(article, '/ano/(\d{4})/')
        plot = scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>')

        langs = []
        if 'class="espanol"' in article: langs.append('Esp')
        if 'class="latino"' in article: langs.append('Lat')
        if 'class="subtitulado"' in article: langs.append('Vose')

        quality = scrapertools.find_single_match(article, '/beta/([^\.]+)\.png')
        if 'calidad' in quality: quality = quality.replace('-', ' ').replace('calidad', '').strip().capitalize()
        else: quality = ''

        show, showalt = extraer_show_showalt(title)

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=', '.join(langs), qualities=quality,
                                    contentType='movie', contentTitle=show, contentTitleAlt=showalt, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)')
        if not next_page: next_page = scrapertools.find_single_match(data, '<div class=\'resppages\'><a href="([^"]+)')

        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', action='peliculas', url=next_page, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['CAM', 'WEB-SCR', 'TS-SCR', 'BLURAY-SCR', 'HD', 'HD-RIP', 'DVD-RIP', 'BLURAY-RIP', 'HD 720p', 'HD 1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)

    if servidor == 'fcom': return 'fembed'
    elif servidor in ['mp4', 'api', 'drive']: return 'gvideo'
    else: return servidor


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<tr id='link-[^']+'>(.*?)</tr>")

    ses = 0

    for enlace in matches:
        ses += 1

        if 'Obtener</a>' in enlace: continue

        url = scrapertools.find_single_match(enlace, " href='([^']+)")
        servidor = scrapertools.find_single_match(enlace, " alt='([^'.]+)")
        if not servidor: servidor = scrapertools.find_single_match(enlace, "domain=([^'.]+)")

        servidor = corregir_servidor(servidor.strip().lower())

        if not servidor: continue

        if 'Descargar</a>' in enlace and servidor not in ['mega', 'gvideo', 'uptobox']: continue

        uploader = scrapertools.find_single_match(enlace, "author/[^/]+/'>([^<]+)</a>")

        enlace = enlace.replace('https://static.cinetux.to/', '/').replace('https://cdn.cinetux.nu/', '/')
        tds = scrapertools.find_multiple_matches(enlace, 'data-lazy-src="/assets/img/([^\.]*)')

        try:
            if tds:
                quality = tds[1]
                lang = tds[2]
            else:
                quality = scrapertools.find_single_match(enlace, "<strong class='quality'>([^<]+)")
                lang = scrapertools.find_single_match(enlace, "<td>([^<]+)")
        except:
            quality = ''
            lang = ''

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                              language = IDIOMAS.get(lang,lang), quality = quality, quality_num = puntuar_calidad(quality), other = uploader ))


    matches = scrapertools.find_multiple_matches(data, '<li id="player-option-\d+"(.*?)</li>')
    if matches:
        entrecomillado = '"([^"]+)'
    else:
        matches = scrapertools.find_multiple_matches(data, "<li id='player-option-\d+'(.*?)</li>")
        entrecomillado = "'([^']+)"

    for enlace in matches:
        ses += 1

        dtype = scrapertools.find_single_match(enlace, 'data-type=%s' % entrecomillado)
        dpost = scrapertools.find_single_match(enlace, 'data-post=%s' % entrecomillado)
        dnume = scrapertools.find_single_match(enlace, 'data-nume=%s' % entrecomillado)

        tds = scrapertools.find_multiple_matches(enlace, 'data-lazy-src=".*?/assets/img/([^\.]+)')
        if not tds: tds = scrapertools.find_multiple_matches(enlace, " src='.*?/assets/img/([^\.]+)")
        if len(tds) != 2 or not dtype or not dpost or not dnume: continue

        lang = tds[0].replace('3', '')

        servidor = tds[1].lower()

        if servidor == 'cinetuxm': continue
        elif servidor == 'desconocido': continue
        elif servidor == 'videozerr': servidor = 'directo'

        servidor = corregir_servidor(servidor.strip().lower())

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                              title = '', dtype = dtype, dpost = dpost, dnume = dnume, referer = item.url, language = IDIOMAS.get(lang, lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def extraer_video(item, data):
    itemlist = []

    idvideo = scrapertools.find_single_match(data, 'src="([^"]+)').split('#')
    if len(idvideo) == 2:
        if 'ok.ru/videoembed/' in data:
            itemlist.append(item.clone( url='https://ok.ru/videoembed/' + idvideo[1], server='okru' ))
        elif 'drive.google.com' in data:
            itemlist.append(item.clone( url='https://docs.google.com/get_video_info?docid=' + idvideo[1], server='gvideo' ))
        else:
            itemlist.append(item.clone( url='https://' + idvideo[1], server='gvideo' ))
    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url:
        data = do_downloadpage(item.url)
        new_url = scrapertools.find_single_match(data, '<a id="link"[^>]* href="([^"]+)')
        if new_url:
            if '&url=' in new_url: new_url = new_url.split('&url=')[1]
            if 'cinetux.me' in new_url:
                data = do_downloadpage(new_url)
                new_url = scrapertools.find_single_match(data, "<a class='cta' href='([^']+)")
                if new_url: 
                    itemlist.append(item.clone( server='', url=new_url ))
                    itemlist = servertools.get_servers_itemlist(itemlist)
                else:
                    itemlist = extraer_video(item, data)
            else:
                new_url = servertools.normalize_url(item.server, new_url)
                itemlist.append(item.clone( url=new_url ))

    else:
        post = {'action': 'doo_player_ajax', 'post': item.dpost, 'nume': item.dnume, 'type': item.dtype}
        data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post, headers={'Referer':item.referer})

        new_url = scrapertools.find_single_match(data, "src='([^']+)'")
        if not new_url: new_url = scrapertools.find_single_match(data, 'src="([^"]+)"')
        if new_url:
            new_url = new_url.replace('videozerr.', '')
            if 'cinetux.me' in new_url:
                data = do_downloadpage(new_url)

                if data:
                   url = scrapertools.find_single_match(str(data), '<script>window.*?"(.*?)"')
                   if url:
                       servidor = servertools.get_server_from_url(url)
                       servidor = servertools.corregir_servidor(servidor)

                       itemlist.append(item.clone( url = url, server = servidor ))
                   else:
                       itemlist = extraer_video(item, data)
            else:
                servidor = servertools.get_server_from_url(new_url)
                servidor = servertools.corregir_servidor(servidor)

                itemlist.append(item.clone( url = new_url, server = servidor ))

    return itemlist


def busqueda(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article>(.*?)</article>')

    for article in matches:
        thumb, title = scrapertools.find_single_match(article, ' src="([^"]+)" alt="([^"]+)')
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        year = scrapertools.find_single_match(article, '<span class="year">(\d{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="contenido">(.*?)</div>'))

        show, showalt = extraer_show_showalt(title)

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=show, contentTitleAlt=showalt, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)')
        if next_page:
            itemlist.append(item.clone( action='busqueda', title='Siguientes ...', url=next_page, text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    item.url = host + "?s=" + texto.replace(" ", "+")
    try:
        return busqueda(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
