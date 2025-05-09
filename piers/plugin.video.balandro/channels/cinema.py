# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www1.verpelis.top/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'online/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genero/estreno-1/', search_type = 'movie', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'movie', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'GENEROS(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url, genre = title, text_color = 'deepskyblue' ))

    if itemlist:
        itemlist.append(item.clone( title = 'Animación', action = 'list_all', url = host + 'genero/animacion/', genre='Animación', search_type = 'movie', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Crimen', action = 'list_all', url = host + 'genero/crimen/', genre='Crimen', search_type = 'movie', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Familia', action = 'list_all', url = host + 'genero/familia/', genre='Familia', search_type = 'movie', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Fantasía', action = 'list_all', url = host + 'genero/fantasia/', genre='Fantasia', search_type = 'movie', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Historia', action = 'list_all', url = host + 'genero/historia/', genre='Historia', search_type = 'movie', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Misterio', action = 'list_all', url = host + 'genero/misterio/', genre='Misterio', search_type = 'movie', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Música', action = 'list_all', url = host + 'genero/musica/', genre='Musica', search_type = 'movie', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Romance', action = 'list_all', url = host + 'genero/romance/', genre='Romance', search_type = 'movie', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Terror', action = 'list_all', url = host + 'genero/terror/', genre='Terror', search_type = 'movie', text_color = 'deepskyblue' ))

    return sorted(itemlist,key=lambda x: x.title)


def plataformas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Amazon Prime', action = 'list_all', url = host + 'genero/amazon-prime/', genre='Amazon Prime', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Disney+', action = 'list_all', url = host + 'genero/disney/', genre='Disney+', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Hbo', action = 'list_all', url = host + 'genero/hbo/', genre='HBO', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'genero/netflix/', genre='Netflix', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Rakuten', action = 'list_all', url = host + 'genero/rakuten/', genre='Rakuten', search_type = 'movie', text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '(.*?)>Lo más reciente<')

    if item.genre:
        bloque = scrapertools.find_single_match(data, '<h1>' + item.genre + '(.*?)>Lo más reciente<')
    else:
        bloque = scrapertools.find_single_match(data, '>Películas<(.*?)>Lo más reciente<')
        if not bloque: bloque = scrapertools.find_single_match(data, '>Estreno<(.*?)>Lo más reciente<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = '-'

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<span class="current">.*?' + 'href="(.*?)"')

            if next_page:
                ant_page = scrapertools.find_single_match(item.url, '.*?/page/(.*?)/')

                if '/page/' in next_page:
                    new_page = scrapertools.find_single_match(next_page, '.*?/page/(.*?)/')

                    if not ant_page:
                        itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))
                    else:
                        if new_page > ant_page:
                            itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data =  re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, 'id="player-option-(.*?)</li>')
    if not matches: matches = scrapertools.find_multiple_matches(data, "id='player-option-(.*?)</li>")

    ses = 0

    for match in matches:
        ses += 1

        opt = scrapertools.find_single_match(match, '(.*?)"')
        if not opt: opt = scrapertools.find_single_match(match, "(.*?)'")

        if not opt: continue

        # ~ dtype, dpost, dnume
        dtype = scrapertools.find_single_match(match, ' data-type="(.*?)"')
        if not dtype: dtype = scrapertools.find_single_match(match, " data-type='(.*?)'")

        dpost = scrapertools.find_single_match(match, ' data-post="(.*?)"')
        if not dpost: dpost = scrapertools.find_single_match(match, " data-post='(.*?)'")

        dnume = scrapertools.find_single_match(match, ' data-nume="(.*?)"')
        if not dnume: dnume = scrapertools.find_single_match(match, " data-nume='(.*?)'")

        if not dtype or not dpost or not dnume: continue

        if dnume == 'trailer':
            ses = ses - 1
            continue

        headers = {'Referer': item.url}

        post = {'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype}

        data0 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)

        embed = scrapertools.find_single_match(data0, "<iframe.*?src='(.*?)'")
        if not embed: embed = scrapertools.find_single_match(data0, '<iframe.*?src="(.*?)"')

        if not embed: continue

        data1 = do_downloadpage(embed)

        links = scrapertools.find_multiple_matches(str(data1), '<li onclick="go_to_player' + ".*?'(.*?)'(.*?)</li>")

        for url, resto in links:
            if '/ul.' in url: continue
            elif '/1fichier.' in url: continue
            elif '/rapidgator' in url: continue
            elif '/katfile' in url: continue
            elif '/nitro' in url: continue
            elif '/filecrypt.' in url: continue

            elif '/viewsb.' in url: continue
            elif '/www.fembed.' in url: continue

            elif '/sb' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            if 'Latino' in resto: lang = 'Lat'
            elif 'Sub Español' in resto: lang = 'Vose'
            elif 'Castellano' in resto or 'Español' in resto: lang = 'Esp'
            elif 'Subtitulado' in resto: lang = 'Vose'
            else: lang = '?'

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

    # ~ Descargas No se tratan

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1>Resultados(.*?)>Lo más reciente<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        if not '>Película<' in match: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<span class="current">.*?' + 'href="(.*?)"')

            if next_page:
                ant_page = scrapertools.find_single_match(item.url, '.*?/page/(.*?)/')

                if '/page/' in next_page:
                    new_page = scrapertools.find_single_match(next_page, '.*?/page/(.*?)/')

                    if not ant_page:
                        itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_search', text_color = 'coral' ))
                    else:
                        if new_page > ant_page:
                            itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_search', text_color = 'coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

