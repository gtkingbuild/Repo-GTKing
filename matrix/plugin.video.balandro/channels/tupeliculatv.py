# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.tupelicula.tv/'


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '>Películas por género</div>(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?</span>(.*?)</a>')

    for url, title in matches:
        title = title.strip()

        if title == 'PROXIMOS ESTRENOS': continue

        if descartar_xxx:
            if title == 'Adultos': continue
            elif title == 'Erotico': continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'filter?language=1' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'filter?language=2' ))
    itemlist.append(item.clone( title = 'Inglés (VO)', action = 'list_all', url = host + 'filter?language=3' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'filter?language=4' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1935, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'filter?year=' + str(x), action = 'list_all' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '</i> Formato</label>(.*?)</i> Idioma</label>')

    matches = scrapertools.find_multiple_matches(bloque, '<option value="(.*?)"')

    for title in matches:
        if title:
            itemlist.append(item.clone( title = 'En ' + title, url = host + 'filter?quality=' + title, action = 'list_all' ))

    return sorted(itemlist, key = lambda it: it.title)


def list_all(item): 
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    list_movies = scrapertools.find_single_match(data, '<div id="movie-list"(.*?)</ul>')

    patron = '<a href="([^"]+)".*?data-original="([^"]+)" alt="([^"]+)".*?'
    patron += '<div class="_audio">(.*?)"label_year">(\d{4}) &bull;([^<]+)<'

    matches = re.compile(patron, re.DOTALL).findall(list_movies)

    for url, thumb, title, list_idiomas, year, genre in matches:
        if descartar_xxx:
            if genre == 'Adultos': continue
            elif genre == 'Erotico': continue

        if thumb.startswith('//') == True: thumb = 'https:' + thumb

        title = scrapertools.find_single_match(title, '([^\(]+)')
        langs = get_languages(list_idiomas)

        if not year: year = '-'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = ','.join(langs),
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)"><i class="fa fa-angle-right">')

        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = httptools.downloadpage(item.url).data

    if descartar_xxx:
       genres = scrapertools.find_single_match(data, '&bull;(.*?)</span>')

       if 'Adultos' in genres or 'Erotico' in genres:
           platformtools.dialog_notification('TupeliculaTv', '[COLOR red]Descartada Género Adultos/Erótico[/COLOR]')
           return

    go_url = scrapertools.find_single_match(data, '<iframe id="playerframe" data-src="([^"]+)"')
    data = httptools.downloadpage(go_url).data

    matches = re.compile('title="(.*?)" data-id="(\d+)">.*?img src="([^"]+)".*?>([^<]+)<', re.DOTALL).findall(data)

    ses = 0

    for title, id, list_idiomas, qlty in matches:
        ses += 1

        servidor = servertools.corregir_servidor(title)
        if servidor == '': continue

        link_other = servidor.lower()
        link_other = link_other.replace('descargar pelicula', 'd').replace('descargar capitulo', 'd').replace('descargar parte', 'd').replace('completo', 'c').replace('ver online', 'v').strip()

        link_other = normalize_other(link_other)
        if link_other == '': continue

        server = ''

        if link_other == 'd': pass
        elif link_other == 'c': pass
        elif link_other == 'v': pass
        else:
             server = link_other

             link_other = ''
             if server == 'tunepk':
                 link_other = server
                 server = 'directo'

        langs = get_languages(list_idiomas)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', id = id, referer = go_url,
                              language = ','.join(langs), quality = qlty.strip(), other = link_other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    id_url =  host + 'player/rep/' + item.id
    data = httptools.downloadpage(id_url, headers={'Referer': item.referer}).data

    url = scrapertools.find_single_match(data.lower(), 'iframe src=.*?"([^"]+)"')

    if not url:
        if '<center>' in data:
            url = scrapertools.find_single_match(data, '<center>.*?href=.*?"(.*?)"')
            if not url: url = scrapertools.find_single_match(data, '<center>.*?src=.*?"(.*?)"')
        elif 'var video_html' in data:
            url = scrapertools.find_single_match(data, 'var video_html.*?src=.*?"(.*?)"')
            if not url: url = scrapertools.find_single_match(data, 'var video_html.*?href=.*?"(.*?)"')

    if url:
       url = url.replace('\\/', '/')
       url = url.replace('https://uqload.com/embed-https://', 'https://')

       if url.startswith('//') == True: url = 'https://' + url

       servidor = servertools.get_server_from_url(url)
       servidor = servertools.corregir_servidor(servidor)

       if servidor == 'directo':
           if item.server == 'vk':
               if 'vk.com/' in url: servidor = 'vk'

       url = servertools.normalize_url(servidor, url)
       url = url.replace('&amp;', '&')
       url = normalize_other(url)

       if url:
           if '.blogspot.com' in url: url = ''
           elif url.endswith('/embed-https.html') == True: url = ''
           elif url.startswith('https://es.xhamster.com/') == True: url = ''

       if not url:
           platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Enlace NO Soportado[/B][/COLOR]')

       if url:
           url = url.replace('\\', '/').replace('\\/', '/')
		   
           if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
               return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'
           elif 'openload' in url or 'powvideo' in url or 'streamplay' in url or 'rapidvideo' in url or 'streamango' in url or 'verystream' in url or 'vidtodo' in url:
               return 'Servidor [COLOR yellow]NO soportado[/COLOR]'

           servidor = servertools.get_server_from_url(url)
           servidor = servertools.corregir_servidor(servidor)

           url = servertools.normalize_url(servidor, url)

           itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def get_languages(list_idiomas):
    logger.info()

    IDIOMAS = {'la_la': 'Lat', 'es_es': 'Esp', 'en_es': 'Vose', 'en_en': 'Vo', 'em-portugues': 'Pt'}

    languages = []

    list_langs = scrapertools.find_multiple_matches(list_idiomas, '/flags/(.*?).png"?')
    other_langs = scrapertools.find_multiple_matches(list_idiomas, '/img/(.*?).png"?')

    list_langs = list_langs + other_langs

    for lang in list_langs:
        lang = IDIOMAS[lang]

        if lang not in languages: 
            if not languages: languages.append(lang)
            else: languages.append(' ' + lang)

    return languages


def normalize_other(server):
    if server.startswith('http') == False:
        server = server.replace('www.', '').replace('.com', '').replace('.net', '').replace('.org', '').replace('.co', '').replace('.cc', '')
        server = server.replace('.to', '').replace('.tv', '').replace('.ru', '').replace('.io', '').replace('.eu', '').replace('.ws', '')
        server = server.replace('.', '')

        if server:
            server = servertools.corregir_servidor(server)

            if server == 'gamohd': return 'gamovideo'
            elif server == 'goo': return 'gounlimited'

            elif server == 'netutv': server = ''
            elif server == 'powvideo': server = ''
            elif server == 'streamplay': server = ''
            elif server == 'uploadedto': server = ''

            elif server == 'tunepk': server = ''
            elif server == 'byter': server = ''
            elif server == 'powhd': server = ''
            elif server == 'stream': server = ''
            elif server == 'hqqnew': server = ''
            elif server == 'rapidvideohd': server = ''
            elif server == 'openloadhd': server = ''
            elif server == 'streamangohq': server = ''
            elif server == 'streaminghd': server = ''
            elif server == 'streamcherry': server = ''
            elif server == 'nowvideo': server = ''
    else:
        server = servertools.corregir_servidor(server)

        if server == 'netutv': server = ''
        elif server == 'powvideo': server = ''
        elif server == 'streamplay': server = ''
        elif server == 'uploadedto': server = ''

        elif '/byter.' in server: server = ''
        elif '/biter.' in server: server = ''
        elif '/jetload.' in server: server = ''
        elif '/vidcloud.' in server: server = ''
        elif '/openload.' in server: server = ''
        elif '/oload.' in server: server = ''
        elif '/clicknupload.' in server: server = ''
        elif '/onlystream.' in server: server = ''
        elif '/www.rapidvideo.' in server: server = ''
        elif '/www.rapidvid.' in server: server = ''
        elif '/streamango.' in server: server = ''
        elif '/streamcherry.' in server: server = ''
        elif '/streamcloud.' in server: server = ''
        elif '/streamix.' in server: server = ''
        elif '/thevid.' in server: server = ''
        elif '/thevideo.' in server: server = ''
        elif '/www.uploadmp4.' in server: server = ''
        elif '/verystream.' in server: server = ''

        elif '/mangovideo.club' in server: server = ''
        elif '/daxab.com' in server: server = ''

    return server


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
