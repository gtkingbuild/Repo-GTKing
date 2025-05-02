# -*- coding: utf-8 -*-

import re

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.torrenflix.com/'


IDIOMAS = {'Español': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose', 'V.O.S.E': 'Vose', 'Inglés': 'Ing'}


def do_downloadpage(url, post=None, headers=None):
    raise_weberror = True
    if '/peliculas/estrenos-' in url: raise_weberror = False
    elif '/release/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if not data:
        if not '?s=' in url:
            if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('TorrenFlix', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

            timeout = config.get_setting('channels_repeat', default=30)

            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone ( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'torrents-peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'estrenos', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Cine clásico', action = 'list_all', url = host + 'peliculas/cine-clasico/', search_type = 'movie', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_mvi', url = host + 'wp-admin/admin-ajax.php', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'torrents-series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'estrenos', search_type = 'tvshow', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_mvi', url = host + 'wp-admin/admin-ajax.php', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    return itemlist


def estrenos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 2017, -1):
        itemlist.append(item.clone( title = 'Estrenos ' + str(x), action = 'list_all', url = host + 'peliculas/estrenos-' + str(x) +'/', text_color = text_color ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En 4K UHD Micro', action = 'list_all', url = host + 'peliculas/4k-uhdmicro/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 4K UHD Remux', action = 'list_all', url = host + 'peliculas/4k-uhdremux/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 4K UHD Rip', action = 'list_all', url = host + 'peliculas/4k-uhdrip/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 4K WEB Rip', action = 'list_all', url = host + 'peliculas/4kwebrip/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En BDremux', action = 'list_all', url = host + 'peliculas/bdremux/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En Bluray 1080p', action = 'list_all', url = host + 'peliculas/blurayrip-1080p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En Bluray MicroHD', action = 'list_all', url = host + 'peliculas/bluray-microhd/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En Web DL', action = 'list_all', url = host + 'peliculas/web-dl/', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'Generos</span></a>\s*<ul class="sub-menu">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"><i[^>]*></i><span>([^<]+)')
    for url, title in matches:
        title = title.replace('&amp;', '&')

        if '/estrenos/' in url: continue

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
        text_color = 'deepskyblue'
        top_year = 1938
    else:
        text_color = 'hotpink'
        top_year = 1999

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, top_year, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'release/' + str(x) + '/', action='list_all', text_color = text_color ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        letras = letra.lower()
        if letras == '#': letras = '0-9'

        url = host + 'letters/' + letras + '/'

        itemlist.append(item.clone( action = 'list_all', title = letra, url = url, text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)</section>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')

        title = scrapertools.find_single_match(article, '<div class="Title">(.*?)</div>')
        if not title: title = scrapertools.find_single_match(article, '<h2 class=.*?>(.*?)</h2>')

        if not url or not title: continue

        title = title.replace('&#038;', '&')

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = '-'

        if '/release/' in item.url: year = scrapertools.find_single_match(item.url, "/release/(.*?)/")

        qlty_lang = scrapertools.find_single_match(article, '<span class="calidad">(.*?)</span')
        if '|' in qlty_lang:
            qlty = qlty_lang.split('|')[0].strip()
            lang = qlty_lang.split('|')[1].strip()
        else:
            qlty = qlty_lang
            lang = ''

        if tipo == 'movie':
            if not item.search_type == 'all':
               if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        qualities=qlty, languages=IDIOMAS.get(lang, lang),
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
               if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '>SIGUIENTE<' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?<a class="page-link".*?href="(.*?)"')

            if next_page:
               itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def list_mvi(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.search_type == 'movie':
        post = {'action': 'action_tr_movie_category', 'limit': '48', 'post': 'movies', 'cate': 'all', 'mode': '2'}
    else:
        post = {'action': 'action_tr_movie_category', 'limit': '48', 'post': 'series', 'cate': 'all', 'mode': '2'}

    data = do_downloadpage(item.url, post = post)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')

        title = scrapertools.find_single_match(article, '<div class="Title">(.*?)</div>')
        if not title: title = scrapertools.find_single_match(article, '<h2 class=.*?>(.*?)</h2>')

        if not url or not title: continue

        title = title.replace('&#038;', '&')

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = '-'

        qlty_lang = scrapertools.find_single_match(article, '<span class="calidad">(.*?)</span')
        if '|' in qlty_lang:
            qlty = qlty_lang.split('|')[0].strip()
            lang = qlty_lang.split('|')[1].strip()
        else:
            qlty = qlty_lang
            lang = ''

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        qualities=qlty, languages=IDIOMAS.get(lang, lang),
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_mvi', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('data-season="(.*?)"', re.DOTALL).findall(data)

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = numtempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    post_id = scrapertools.find_single_match(data, '"post_id":"(.*?)"')

    if not post_id: return itemlist

    post = {'action': 'action_select_season' , 'season': str(item.contentSeason), 'post': post_id}
    data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

    matches = re.compile('<article.*?src="(.*?)".*?<span class="num-epi">(.*?)</span>.*?<h2 class="entry-title">(.*?)</h2>.*?<a href="(.*?)"', re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('TorrenFlix', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('TorrenFlix', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TorrenFlix', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TorrenFlix', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TorrenFlix', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TorrenFlix', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('TorrenFlix', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, epis, title, url in matches[item.page * item.perpage:]:
        if thumb.startswith('//'): thumb = 'https:' + thumb
        thumb = thumb.replace('&quot;', '').strip()

        epis = scrapertools.find_single_match(epis, '.*?x(.*?)$')

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title.replace(str(item.contentSeason) + 'x' + str(epis),'')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail=thumb, contentType = 'episode', contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color= 'coral' ))

    return itemlist


def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()

    orden = [
          'cam',
          'camrip',
          'hdcam',
          'webscreener',
          'tsscreener',
          'hdtcscreener',
          'brscreener',
          'brscreener720p',
          'hdtv',
          'hdtv720p',
          'hdtv1080p',
          'microhd',
          'dvdrip',
          'blurayrip1080p',
          'blurayrip720p',
          'bluraymicrohd',
          'blurayrip',
          'bdremux',
          'hdrip',
          'hdrip720p',
          'hd720',
          'hd1080',
          '4kwebrip',
          '4kuhdmicro',
          '4kuhdrip',
          '4kuhdremux',
          'webdl'
          ]

    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def normalize_server(server):
    server = servertools.corregir_servidor(server)

    server = server.replace('.com', '').replace('.net', '').replace('.to', '')

    if server == 'uploaded': return 'uploadedto'

    return server


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<section class="section player(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, ' href="#options-(.*?)".*?class="server">(.*?)</span>')

    ses = 0

    # enlaces
    for opt, server_idioma in matches:
        ses += 1

        s_i = scrapertools.find_single_match(server_idioma, '(.*?)-(.*?)$')
        if not s_i: continue

        servidor = s_i[0].strip().lower()
        if not servidor: continue
        elif servidor == 'youtube': continue

        lang = s_i[1].strip()

        url = scrapertools.find_single_match(bloque, '<div id="options-' + opt + '.*?<iframe src="(.*?)"')
        if not url: url = scrapertools.find_single_match(bloque, '<div id="options-' + opt + '.*?<iframe data-src="(.*?)"')

        if not url: continue

        servidor = normalize_server(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = 'e', language = IDIOMAS.get(lang, lang) ))

    # ~ descargas
    if '>Descargar Torrent<' in data:
        bloque = scrapertools.find_single_match(data, '<table>(.*?)</table>')

        matches = re.compile('<td><span class="num">(.*?)</tr>', re.DOTALL).findall(bloque)

        for match in matches:
            ses += 1

            url = scrapertools.find_single_match(match, ' href="([^"]+)"')
            if url.startswith('//'): url = 'https:' + url

            if not url: continue

            servidor = scrapertools.find_single_match(match, 'class=".*?">(.*?)</a>').strip()

            if not servidor: continue

            lang = scrapertools.find_single_match(match, '</td>.*?<td>(.*?)</td>').strip()
            qlty = scrapertools.find_single_match(match, '<td><span>(.*?)</span>').strip()

            other = ''

            if servidor.lower() != 'torrent': other = 't'

            if servidor:
                servidor = normalize_server(servidor)

                if servertools.is_server_available(servidor):
                   if not servertools.is_server_enabled(servidor): continue
                else:
                   if not config.get_setting('developer_mode', default=False): continue

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = other,
                                  language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&').replace(' class=', '')

    url = ''

    if '/?trdownload=' in item.url:
        url = httptools.downloadpage(item.url, only_headers = True, follow_redirects = False).headers.get('location')

        if url:
            if url.endswith('.torrent') or '/torrent/' in url:
               if not 'http' in url:
                   if not host in url: url = host[:-1] + url
			   
               itemlist.append(item.clone( url = url, server = 'torrent' ))
               return itemlist

    elif item.server == 'torrent':
          if not 'http' in url:
              if not host in url: url = host[:-1] + url

          itemlist.append(item.clone( url = item.url, server = 'torrent' ))
          return itemlist

    elif item.other == 't':
        url = httptools.downloadpage(item.url, only_headers = True, follow_redirects = False).headers.get('location')

        if url:
            if url.endswith('.torrent') or '/torrent/' in url:
               if not 'http' in url:
                   if not host in url: url = host[:-1] + url

               itemlist.append(item.clone( url = url, server = 'torrent' ))
               return itemlist

    else:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')

    if url:
        if '.filekas.'in url:
            data = do_downloadpage(url)

            url = scrapertools.find_single_match(data, '<li id="download">.*?<a href="(.*?)"')

        elif url.startswith('https://drive.google.com/'): url = ''

    if url:
       if item.server == 'torrent':
           if url.endswith('.torrent'):
               if not 'http' in url:
                   if not host in url: url = host[:-1] + url

               itemlist.append(item.clone(url = url, server = item.server))
       else:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor == 'directo':
                new_server = servertools.corregir_other(url).lower()
                if new_server.startswith("http"): servidor = new_server

            url = servertools.normalize_url(servidor, url)

            itemlist.append(item.clone( url = url, server = servidor ))

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
