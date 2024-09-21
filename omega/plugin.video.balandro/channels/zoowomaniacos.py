# -*- coding: utf-8 -*-

import re, string

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools, tmdb


host = 'https://zoowomaniacos.org/'

host_opts = host + 'alternativo3/server.php'


perpage = 22


epochs = [
   ('Años 10'),
   ('Años 1900'),
   ('Años 20'),
   ('Años 30'),
   ('Años 40'),
   ('Años 50'),
   ('Años 60'),
   ('Años 70'),
   ('Años 80'),
   ('Años 90'),
   ('Antigua Grecia'),
   ('Antigua Roma'),
   ('Antiguo Egipto'),
   ('Crisis económica 2008'),
   ('Guerra Chino-Japonesa (II)'),
   ('Guerra Civil Española'),
   ('Guerra de Corea'),
   ('Guerra de independencia americana'),
   ('Guerra de Iraq'),
   ('Guerra de la Indepencia Española'),
   ('Guerra de Secesión'),
   ('Guerra de Vietnam'),
   ('Guerra del Golfo'),
   ('Guerra Fría'),
   ('Historia de España'),
   ('I Guerra Mundial'),
   ('II Guerra Mundial'),
   ('Revolución Cubana'),
   ('Revolución cultural china'),
   ('Revolución Francesa'),
   ('Revolución Mexicana'),
   ('Revolución Rusa'),
   ('Siglo XII'),
   ('Siglo XIII'),
   ('Siglo XIV'),
   ('Siglo XV'),
   ('Siglo XVI'),
   ('Siglo XVII'),
   ('Siglo XVIII'),
   ('Siglo XIX')
   ]


writers = [
   ('Alberto Moravia'),
   ('Alejandro Dumas'),
   ('Benito Pérez Galdós'),
   ('Charles Dickens'),
   ('Clásicos literarios'),
   ('David H. Lawrence'),
   ('Dostoievski'),
   ('Émile Zola'),
   ('George Orwell'),
   ('Graham Greene'),
   ('Pio Baroja'),
   ('Ray Bradbury'),
   ('Shakespeare'),
   ('Tennessee Williams'),
   ('Thomas Mann')
   ]


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Búsquedas:', action = '', folder=False, text_color='plum' ))
    itemlist.append(item.clone ( title = ' - Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = ' - Buscar por dirección, intérprete ...', action = 'search', grupo = 'agrupa', search_type = 'movie', text_color='salmon' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host_opts ))

    itemlist.append(item.clone( title = 'Las 1001 que hay que ver', action= 'list_all', url = host_opts, text_color = 'cyan',
                                pane = 'Las 1001',
                                post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': 'Las 1001', 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': '', 'searchPanes[a6][0]': ''},
                                ))

    itemlist.append(item.clone( title = 'Películas de culto', action= 'list_all', url = host_opts, text_color = 'moccasin',
                                pane = 'Película de Culto',
                                post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': 'Película de Culto', 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': '', 'searchPanes[a6][0]': ''},
                                ))

    itemlist.append(item.clone( title = 'Versión original', action= 'list_all', url = host_opts,
                                pane = 'VO',
                                post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': 'VO', 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': '', 'searchPanes[a6][0]': ''},
                                ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por época', action = 'epocas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por escritor', action = 'escritores' ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por dirección, interpretación ...', action = 'alfabetico', text_color='salmon' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    genres = []

    post = {'start': '', 'length': 20, 'metodo': 'ObtenerListaTotal'}
    headers = {'Referer': host + 'home/buscador.php'}

    data = do_downloadpage(host_opts, post = post, headers = headers)

    jdata = jsontools.load(data)

    bloque = scrapertools.find_single_match(str(jdata), "'options':.*?'a5':(.*?)'a4':")
    if not bloque: bloque = scrapertools.find_single_match(str(jdata), "'options':.*?'a5':(.*?)'a3':") # PY3

    matches = scrapertools.find_multiple_matches(str(bloque), "'label': '(.*?)'.*?'value': '(.*?)'")

    _epochs = str(list(epochs))
    _writers = str(list(writers))

    for value, label in matches:
        if '\\' in label:
           title = label.decode("unicode_escape")
           title = title.encode('latin1').decode('utf8')
        else:
           title = label

        if title:
            if value in str(_epochs): continue
            elif value in str(_writers): continue

            genres.append([value, title])

    for x in genres:
        title = x[1]
        # ~ genre = x[0] PY3
        genre = title

        if config.get_setting('descartar_xxx', default=False):
            if title == 'Animación para Adultos': continue
            elif title == 'Erótico': continue
            elif title == 'Pornografía': continue

        if title == 'Las 1001': continue
        elif title == 'Película de Culto': continue
        elif title == 'VO': continue

        if title == 'Animación para Adultos': title = title + ' (+18)'
        elif title == 'Erótico': title = title + ' (+18)'
        elif title == 'Pornografía': title = title + ' (+18)'

        title = title.replace('&amp;', '&')

        post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': genre, 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': '', 'searchPanes[a6][0]': ''}

        itemlist.append(item.clone( title = title, action = 'list_all', url = host_opts, pane = genre, post = post, text_color = 'deepskyblue' ))

    return itemlist


def epocas(item):
    logger.info()
    itemlist = []

    for x in epochs:
        title = x
        epoca = title

        post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': epoca, 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': '', 'searchPanes[a6][0]': ''}

        itemlist.append(item.clone( title = title, action = 'list_all', url = host_opts, pane = epoca, post = post, text_color = 'deepskyblue' ))

    return itemlist


def escritores(item):
    logger.info()
    itemlist = []

    for x in writers:
        title = x
        writer = title

        post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': writer, 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': '', 'searchPanes[a6][0]': ''}

        itemlist.append(item.clone( title = title, action = 'list_all', url = host_opts, pane = writer, post = post, text_color='tan' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1894, -1):
        any = str(x)

        post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': '', 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': any, 'searchPanes[a6][0]': ''}

        itemlist.append(item.clone( title = any, action = 'list_all', url = host_opts, any = any, post = post, text_color = 'deepskyblue' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    countries = []

    post = {'start': '', 'length': 20, 'metodo': 'ObtenerListaTotal'}
    headers = {'Referer': host + 'home/buscador.php'}

    data = do_downloadpage(host_opts, post = post, headers = headers)

    jdata = jsontools.load(data)

    bloque = scrapertools.find_single_match(str(jdata), "'options':.*?'a6':(.*?)'data'")
    if not bloque: bloque = scrapertools.find_single_match(str(jdata), "'options':.*?'a6':(.*?)'a5':") # PY3

    matches = scrapertools.find_multiple_matches(str(bloque), "'label': '(.*?)'.*?'value': '(.*?)'")

    for value, label in matches:
        if '\\' in label:
           title = label.decode("unicode_escape")
           title = title.encode('latin1').decode('utf8')
        else:
           title = label

        if title:
            countries.append([value, title])

    for x in countries:
        title = x[1]
        # ~ country = x[0] PY3
        country = title

        post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': '', 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': '', 'searchPanes[a6][0]': country}

        itemlist.append(item.clone( title = title, action = 'list_all', url = host_opts, country = country, post = post, text_color='moccasin' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in string.ascii_uppercase:
        itemlist.append(item.clone (action = "directores", title = letra, letra = letra))

    itemlist.append(item.clone (action = "directores", title = 'Todos', letra = 'Todos'))

    return itemlist


def directores(item):
    logger.info()
    itemlist = []

    directors = []

    if not item.paginacion: item.paginacion = 0

    post = {'start': '', 'length': 20, 'metodo': 'ObtenerListaTotal'}
    headers = {'Referer': host + 'home/buscador.php'}

    data = do_downloadpage(host_opts, post = post, headers = headers)

    jdata = jsontools.load(data)

    bloque = scrapertools.find_single_match(str(jdata), "'options':.*?'a3':(.*?)'a5':")
    if not bloque: bloque = scrapertools.find_single_match(str(jdata), "'options':.*?'a3':(.*?)}}}") # PY3

    matches = scrapertools.find_multiple_matches(str(bloque), "'label': '(.*?)'.*?'value': '(.*?)'")

    for value, label in matches:
        if '\\' in label:
           title = label.decode("unicode_escape")
           title = title.encode('latin1').decode('utf8')
        else:
           title = label

        if title:
            if item.filtro_search:
               if not item.filtro_search.lower() in title.lower(): continue
            else:
               if not item.letra == 'Todos':
                   if not title[:1] == item.letra: continue

            directors.append([value, title])

    paginacion = 100000
    if item.letra == 'Todos': paginacion = 999

    num_matches = len(directors)

    for x in directors[item.paginacion * paginacion:]:
        title = x[1]
        # ~ director = x[0] PY3
        director = title

        post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a3][0]': director, 'search[value]': '', 'searchPanes[a4][0]': '', 'searchPanes[a5][0]': '', 'searchPanes[a6][0]': ''}

        itemlist.append(item.clone( title = title, action = 'list_all', url = host_opts, director = director, post = post, text_color='moccasin' ))

        if len(itemlist) >= paginacion: break

    if itemlist:
        if num_matches > paginacion:
            hasta = ((item.paginacion * paginacion) + paginacion)
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', paginacion = item.paginacion + 1, action='directores', text_color='coral' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.start: item.start = 0
    if not item.tex_search: item.tex_search = ''
    if not item.director: item.director = ''
    if not item.pane: item.pane = ''
    if not item.any: item.any = ''
    if not item.country: item.country = ''

    start = str(item.start)
    pane = str(item.pane)
    search = str(item.tex_search)
    director = str(item.director)
    any = str(item.any)
    country = str(item.country)

    if not item.post:
       post = {'start': start, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'search[value]': search, 'searchPanes[a3][0]': director, 'searchPanes[a4][0]': any, 'searchPanes[a5][0]': pane, 'searchPanes[a6][0]': country}
    else:
       post = item.post

    # ~ Menu Principal addon opcion Generos
    if item.zoo_genre:
        pane = item.zoo_genre
        post = {'start': start, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': pane, 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': '', 'searchPanes[a6][0]': ''}

    data = do_downloadpage(item.url, post = post)

    jdata = jsontools.load(data)

    try:
        for elem in jdata['data']:
            title_alt = elem.get('a2', '')

            try:
                title = title_alt.split('-')[0].strip()
                title_alt = title_alt.split('-')[1].strip()
            except:
                title = title_alt

            direccion = elem.get('a3', '0')

            titulo = title + ' - ' + direccion

            _id = elem.get('a1', '0')

            year = elem.get('a4', '0')
            if not year: year = '-'

            thumb = '%swp/wp-content/uploads/%s' % (host[:-1], elem.get('a8', ''))

            plot = elem.get('a100', '')

            itemlist.append(item.clone( action='findvideos', _id=_id, title=titulo, thumbnail=thumb, contentType='movie', contentTitle=title, contentTitleAlt = title_alt, infoLabels={'year': year, 'plot': plot} ))
    except:
        return itemlist

    tmdb.set_infoLabels(itemlist)

    if itemlist:
       if len(itemlist) == perpage:
           start = int(start) + perpage

           zoo_genre = item.zoo_genre

           post = {'start': start, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'search[value]': search, 'searchPanes[a3][0]': director, 'searchPanes[a4][0]': any, 'searchPanes[a5][0]': pane, 'searchPanes[a6][0]': country}
	
           itemlist.append(item.clone (url = item.url, post = post, start = start, pane = pane, search = search, director = director, any = any, country = country, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {
            'es': 'Esp',
            'ar': 'Lat',
            'co': 'Lat',
            'cl': 'Lat',
            'pe': 'Lat',
            'mx': 'Lat',
            'en': 'Ing',
            'gb': 'Ing',
            'vose': 'Vose',
            'vo': 'VO',
            'it': 'IT',
            'de': 'DE',
            'fr': 'FR',
            'jp': 'JP',
            'td': 'RO',
            'se': 'SE',
            'br': 'BR',
            'ru': 'RU',
            'kr': 'KR',
            'pt': 'PT',
            'cn': 'HK',
            'pl': 'PL',
            'in': 'IN',
            'tr': 'TR',
            'nl': 'NL'
            }

    # ~ https://proyectox.yoyatengoabuela.com/playerex.php?id=
    det_url = host + 'testplayer.php?id=' + item._id

    data = do_downloadpage(det_url)

    matches = scrapertools.find_multiple_matches(data, '<div id="option-(.*?)".*?src="(.*?)"')

    ses = 0

    for opt, lnk in matches:
        # ~ the puppet masters  y  masters del universo
        if not item._id == '19997':
            if lnk == 'https://ok.ru/videoembed/1683045747235': continue
            elif lnk == 'https://ok.ru/videoembed/332656282246': continue

        ses += 1

        servidor = servertools.get_server_from_url(lnk)
        servidor = servertools.corregir_servidor(servidor)

        lnk = servertools.normalize_url(servidor, lnk)

        patron = '<a class="options" href="#option-' + str(opt) + '">.*?/flags/(.*?).png'

        lngs = scrapertools.find_multiple_matches(data, patron)

        other = ''

        try:
            if len(lngs) > 1:
                other = str(lngs[i])
                other = IDIOMAS.get(other, other)
        except:
            pass

        lang = scrapertools.find_single_match(data, patron)

        lang = IDIOMAS.get(lang, lang)

        if lang == other: other = ''
        else:
           if other:
               lang = other
               other = ''

        if lang == '': lang = '?'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = lnk, language = lang, other = other ))

        if 'ZXLQ3000' in item.title:
            if lnk.endswith('.mp4') == True: servidor = 'directo'

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = lnk, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def _las1001(item):
    logger.info()

    item.url = host_opts
    item.pane = 'Las 1001'

    item.post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': 'Las 1001', 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': '', 'searchPanes[a6][0]': ''}

    return list_all(item)


def _culto(item):
    logger.info()

    item.url = host_opts
    item.pane = 'Película de Culto'

    item.post = {'start': 0, 'length': perpage, 'metodo': 'ObtenerListaTotal', 'searchPanes[a5][0]': 'Película de Culto', 'search[value]': '', 'searchPanes[a3][0]': '', 'searchPanes[a4][0]': '', 'searchPanes[a6][0]': ''}

    return list_all(item)


def search(item, texto):
    logger.info()
    try:
        item.tex_search = texto.replace(" ", "+")
        item.url = host_opts

        if item.grupo == 'agrupa':
            item.filtro_search = texto
            return directores(item)

        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

