# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

from lib import decrypters


host = 'https://descargacineclasico.net/'


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tag/peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Documentales', action = 'list_all', url = host + 'tag/documentales/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = httptools.downloadpage(host).data
    bloque = scrapertools.find_single_match(data, '<h3>Géneros(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<li[^>]*><a href="([^"]+)" title="[^"]*">([^<]+)</a></li>')

    if not matches:
        patron = '<li[^>]*><a href=([^ ]+) title="[^"]*">([^<]+)</a></li>'
        matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, titulo in matches:
        if descartar_xxx and scrapertools.es_genero_xxx(titulo): continue

        itemlist.append(item.clone( title=titulo, url=url, action='list_all' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'tag/castellano/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'tag/latino/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'tag/subtitulada/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Versión original', action = 'list_all', url = host + 'tag/vo/', search_type = 'movie' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    for ano in range(2013, 1913, -1):
        itemlist.append(item.clone( action = 'list_all', title = str(ano), url = host + 'fecha/' + str(ano) + '/' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    raise_weberror = False if '/fecha/' in item.url else True

    data = httptools.downloadpage(item.url, raise_weberror=raise_weberror).data

    # descartar idiomas pq los VO y Vose no se acostrumbran a cumplir
    patron = '<div class="post-thumbnail">\s*<a href="([^"]+)" title="([^"]+)">\s*'
    patron += '<img width="[^"]*" height="[^"]*" style="[^"]*" src="([^"]+)".*?<p>(.*?)</p>'

    matches = scrapertools.find_multiple_matches(data, patron)
    if not matches:
        patron = '<div class=post-thumbnail>\s*<a href=([^ ]+) title="([^"]+)">.*?<p>(.*?)</p>.*?<p>(.*?)</p>'
        matches = scrapertools.find_multiple_matches(data, patron)

    for url, title, thumb, plot in matches:
        if 'indice-de-peliculas-clasicas' in url: continue

        title = title.replace(' Descargar y ver Online', '')

        year = scrapertools.find_single_match(title, '\((\d{4})\)')
        if year: title = title.replace('(%s)' % year, '').strip()
        else: year = '-'

        plot = scrapertools.decodeHtmlentities(plot)

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, name = title, any = year,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, ' rel=next href=([^ >]+)')
        if not next_page: next_page = scrapertools.find_single_match(data, ' rel="next" href="([^"]+)"')

        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    if '<h2>Ver online' in data: data = data.split('<h2>Ver online')[1]

    patron = '<a href="#(div_\d+_v)" class="MO">\s*'
    patron += '<span>(.*?)</span>\s*'
    patron += '<span>.*?</span>\s*'
    patron += '<span>(.*?)</span>\s*'
    patron += '<span>.*?</span>\s*'
    patron += '<span>.*?/imgdes/(.*?).jpg".*?</span>\s*'
    patron += '</a>.*?<div id="([^"]+)"[^>]*>\s*<a href=([^ ]+)'

    try:
        matches = scrapertools.find_multiple_matches(data, patron)
        if not matches:
            patron = '<a href=#(div_\d+_v) class=MO>\s*'
            patron += '<span>(.*?)</span>\s*'
            patron += '<span>.*?</span>\s*'
            patron += '<span>(.*?)</span>\s*'
            patron += '<span>.*?</span>\s*'
            patron += '<span>.*?/imgdes/(.*?).jpg".*?</span>\s**'
            patron += '</a>.*?<div id=([^ ]+) [^>]*>\s*<a href=([^ ]+)'
            matches = scrapertools.find_multiple_matches(data, patron)
    except:
        return itemlist

    ses = 0

    for div1, lg, qlty, servidor, div2, url in matches:
        ses += 1

        if div1 != div2: continue

        url = url.replace('"', '')
        if not url.startswith('http'): continue

        if '/esp.png' in lg: lang = 'Esp'
        elif '/esp-lat' in lg: lang = 'Lat'
        elif '/vose.png' in lg or '/dual-sub.png' in lg: lang = 'Vose'
        else: lang = 'VO'

        if 'adshrink.it' in url: continue
        elif 'theicongenerator' in url: continue
        elif '/rainonit.com/' in url: continue

        other = ''

        servidor = servidor.lower()
        if servidor == 'clip': servidor = 'clipwatching'

        elif '/fumacrom.com/' in url or 'tmearn.com/' in url or 'tmearn.net/' in url or '/tinyurl.com/' in url or '/ouo.io/'in url:
            other = servidor.capitalize()
            servidor = 'directo'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, referer = item.url,
                              language = lang, quality = qlty , other = other, name = item.name, any = item.any ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if 'tmearn.com/' in item.url or 'tmearn.net/' in item.url:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    elif item.url.startswith('https://adf.ly/'): 
        url = decrypters.decode_adfly(item.url)

        if url: 
            if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone(server = servidor, url = url))
    
    elif item.server == 'directo':
        if '/ouo.io/' in item.url:
            if item.any:
                item.name = item.name.replace(' ', '-')
                new_url = 'https://odysee.com/@CineClasico:a/' + str(item.name) + '-' + str(item.any) + ':b'
        else:
            new_url = httptools.downloadpage(item.url, follow_redirects=False).headers.get('location', '')

        if new_url:
            if new_url.startswith('https://odysee.com'):
                data = httptools.downloadpage(new_url).data
                url = scrapertools.find_single_match(data, '"contentUrl": "(.*?)"')

                if url:
                   itemlist.append(item.clone(server = item.server, url = url))

            else:
                data = httptools.downloadpage(new_url).data
                fbm_url = scrapertools.find_single_match(data, 'id="fbm".*?<script src="(.*?)"')

                if fbm_url:
                    url = decrypters.decrypt_dcs(data)

                    if url:
                        servidor = servertools.get_server_from_url(url)
                        servidor = servertools.corregir_servidor(servidor)

                        url = str(url)

                        if url.startswith('https://odysee.com'):
                            data = httptools.downloadpage(url).data
                            url = scrapertools.find_single_match(data, '"contentUrl": "(.*?)"')

                        if url:
                            itemlist.append(item.clone(server = servidor, url = url))

    else:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone(server = servidor, url = url))

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
