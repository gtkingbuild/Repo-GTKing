# -*- coding: utf-8 -*-


from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ultrapelishd.net/'



def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genre/estrenos-hd/', search_type = 'movie', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + 'genre/marvel/', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'genre/netflix/', search_type = 'movie', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'genre/destacados/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En [COLOR moccasin][B]4K[/B][/COLOR]', action = 'list_all', url = host + 'genre/peliculas-4k/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>CATEGORÍAS(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if '/genre/estrenos-hd/' in url: continue
        elif '/genre/marvel/' in url: continue
        elif '/genre/netflix/' in url: continue
        elif '/genre/destacados/' in url: continue
        elif '/genre/peliculas-4k/' in url: continue

        if title == 'PRÓXIMAMENTE': continue

        title = title.lower().capitalize()

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)<div class="copy">')
    if not bloque: bloque = scrapertools.find_single_match(data, '>Resultados(.*?)<div class="copy">')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<h3 class="title">(.*?)</h3>')

        if not url or not title: continue

        title = title.replace('[4K]', '').replace('[4k]', '').replace(' 4K', '').replace(' 4k', '').replace('&#8211;', '').replace('&#8217;', "'").strip()

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, '</h3></pan>(.*?)</span>')

        if year: title = title.replace('(', year + ')').strip()
        else: year = '-'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?</a>.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<li id='player-option-(.*?)</span>")

    ses = 0

    for match in matches:
        ses += 1

        d_type = scrapertools.find_single_match(match, "data-type='(.*?)'")
        d_post = scrapertools.find_single_match(match, "data-post='(.*?)'")
        d_nume = scrapertools.find_single_match(match, "data-nume='(.*?)'")

        if not d_type or not d_post or not d_nume: continue

        if d_nume == 'trailer': continue

        post = {'action': 'doo_player_ajax', 'post': d_post, 'nume': d_nume, 'type': d_type}

        data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

        url = scrapertools.find_single_match(data, '"embed_url":.*?"(.*?)"')

        url = url.replace('\\/', '/')

        if not url: continue

        if '/openload.' in url: continue
        elif '.fembed.' in url: continue
        elif '/vidlox.' in url: continue
        elif '/gounlimited.' in url: continue
        elif '/ultrapelishd.' in url: continue

        if 'http:' in url: url = url.replace('http:', 'https:')

        if 'castellano' in match.lower(): lang = 'Esp'
        elif 'latino' in match.lower(): lang = 'Lat'
        elif 'subtitulado' in match.lower(): lang = 'Vose'
        else: lang = '?'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
            else:
               if not config.get_setting('developer_mode', default=False): continue

        other = servidor

        if servidor == 'various': other = servertools.corregir_other(url)

        if servidor == other: other = ''

        elif not servidor == 'directo':
           if not servidor == 'various': other = ''

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

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

