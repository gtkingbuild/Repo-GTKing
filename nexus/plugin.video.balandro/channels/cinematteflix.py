# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools, jsontools


host = 'https://www.cinematte.com.es/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www.cinematteflix.com/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'category/videoclub/' ))

    itemlist.append(item.clone( title = 'Magazine', action = 'list_all', url = host, group = 'magazine', page = 1))

    itemlist.append(item.clone( title = 'Videoclub', action = 'list_all', url = host + 'tag/cinematte-videoclub/' ))

    itemlist.append(item.clone( title = 'Obras maestras', action = 'list_all', url = host + 'tag/cinematte-obras-maestras/' ))

    itemlist.append(item.clone( title = 'Cine de culto', action = 'list_all', url = host + 'tag/cinematte-culto/' ))

    itemlist.append(item.clone( title = 'Los 80', action = 'list_all', url = host + 'tag/cinematte-80/' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Análisis y estudios', url = host + 'category/analisis-y-estudios/', action = 'list_all', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Artículos de cine', url = host + 'category/articulos-de-cine/', action = 'list_all', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Cinematte', url = host + 'category/cinematte-flix/', action = 'list_all', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Críticas', url = host + 'category/critica/', action = 'list_all', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Contemporaneo', url = host + 'category/actualidad/', action = 'list_all', text_color = 'deepskyblue' ))

    if not config.get_setting('descartar_xxx', default=False):
        itemlist.append(item.clone( title = 'Erotismo', url = host + 'category/erotismo/', action = 'list_all', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Imprescindibles', url = host + 'category/imprescindibles/', action = 'list_all', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Lecciones de cine', url = host + 'category/lecciones-de-cine/', action = 'list_all', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Operas primas', url = host + 'category/obras-maestras/', action = 'list_all', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Uncategorized', url = host + 'category/uncategorized/', action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, "<article(.*?)</article>")

    for match in matches:
        match = match.replace('&#8216;', '').replace('&#8217;', '').replace('&#8220;', '').replace('', '')

        if item.group == 'magazine':
            if '/sin-categoria/' in match: continue

        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        if not url: continue

        if '/passionatte.com/' in url: continue
        elif '/entra-al-videoclub-online-gratuito/' in url: continue

        info = scrapertools.find_single_match(match, '<header class="post-header">(.*?)</header>')

        year = scrapertools.find_single_match(info, "\d{4}")
        if not year: year = '-'

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(match, ' style="background-image.*?' + "'(.*?)'")
		
        thumb = thumb.replace('&#038;', '&').replace('&amp;', '&')

        capitulos = False
        if '-serie-' in url: capitulos = True
        elif '-temporada-' in url: capitulos = True
        elif ' temporada' in info.lower(): capitulos = True
        elif ' temporadas' in info.lower(): capitulos = True

        if 'subtitulada' in info.lower() or 'subtitulado' in info.lower(): langs = 'Vose'
        elif 'V.O.S.E.' in info: langs = 'Vose'
        elif 'V.O.' in info: langs = 'Vo'
        elif 'Versión ' in info: langs = 'Vo'
        else: langs = 'Esp'

        title = scrapertools.find_single_match(match, 'rel="bookmark">(.*?)</a>')
        if not title: title = scrapertools.find_single_match(match, ' alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<a href=".*?">(.*?)</a>')

        if not title: continue

        title = title.lower()

        title = title.replace('Ver Serie completa ', '').replace('ver ', '').replace('videoclub gratuito online ', '').replace('videoclub gratuito ', '').replace('videoclub gratis: ', '').replace('videoclub gratis ', '').replace('videoclub online gratis: ', '').replace('videoclub online gratis ', '').replace('videoclub online: ', '').replace('videoclub online ', '').replace('videoclub: ', '').replace('videoclub ', '').replace('y descargar ', '').strip()

        if title.startswith('|'):
            title = title.split("|")[1]
            title = title.strip()
        elif ('gratis') in title:
            title = title.replace(' | ', '')
            title = title.replace('gratis', '').strip()

        title = title.capitalize()

        title = title.replace('Á', 'á').replace('É', 'é').replace('Í', 'í').replace('Ó', 'ó').replace('Ú', 'ú').replace('Ñ', 'ñ')

        if not year == '-': title = title.replace('(' + year + ')', '').strip()

        title = title.replace('&#8211;', '').replace('&#8221;', '').replace('&#215;', '').replace('&#039;', '')

        if capitulos:
            datos_cap = do_downloadpage(url)

            hay_capitulos = scrapertools.find_multiple_matches(datos_cap, '<div class="wp-block-embed__wrapper">.*?src="(.*?)"')
            if len(hay_capitulos) <= 1: capitulos = False

        if not capitulos:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = langs,
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action = 'list_col', url = url, title = title, thumbnail = thumb, languages = langs, grupo = 'colec',
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

    if not '/?s=' in item.url: tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def list_col(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<div class="wp-block-embed__wrapper">.*?title="(.*?)".*?src="(.*?)"')

    if matches: platformtools.dialog_notification('CinematteFlix', '[COLOR blue]Cargando vídeos [/COLOR]')

    for title, url in matches:
        if not 'youtube' in url: continue

        try:
            info_url = 'https://www.youtube.com/oembed?url=%s&format=json' % url.replace('/embed/', '/watch?v=')

            data = do_downloadpage(info_url)
            info = jsontools.load(data)

            thumb = info["thumbnail_url"]
        except:
            thumb = item.thumbnail

        year = scrapertools.find_single_match(title, "\d{4}")

        if not year: year = '-'

        if 'subtitulada' in title.lower() or 'subtitulado' in title.lower(): langs = 'Vose'
        elif 'V.O.S.E.' in title: langs = 'Vose'
        elif 'V.O.' in title: langs = 'Vo'
        elif 'Versión ' in title: langs = 'Vo'
        else: langs = 'Esp'

        title = title.lower().strip()

        title = title.capitalize()

        title = title.replace('Á', 'á').replace('É', 'é').replace('Í', 'í').replace('Ó', 'ó').replace('Ú', 'ú').replace('Ñ', 'ñ').replace('Ü', 'ú')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = langs, grupo = item.grupo,
                                    contentType = 'movie', contentTitle = item.title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.grupo == 'colec':
        url = item.url.replace('?feature=oembed', '')

        servidor = servertools.get_server_from_url(url)

        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, title = '', language = item.languages)) 

        return itemlist

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, '<div class="jetpack-video-wrapper">.*?src="(.*?)"')
    if not links: links = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    ses = 0

    for url in links:
        ses += 1

        url = url.replace('?feature=oembed', '')

        if url.startswith("//"): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)

        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, title = '', language = item.languages)) 

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
