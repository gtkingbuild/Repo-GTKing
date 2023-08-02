# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ievenn.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'seccion/cine/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action = 'list_all', title = 'Abejas', url = host + 'tema/abejas/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Cine alemán', url = host + 'tema/cine-alemania/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Cine Usa', url = host + 'tema/cine-usa/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Contaminación', url = host + 'tema/contaminacion/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Coronavirus', url = host + 'tema/coronavirus/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Documental', url = host + 'tema/documental/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Kids en castellano', url = host + 'seccion/kids/kids-espanol/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Kids en VO', url = host + 'seccion/kids/kids-english/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Rugby', url = host + 'tema/rugby/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Segunda guerra mundial', url = host + 'tema/segunda-guerra-mundial/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Toc', url = host + 'tema/toc/' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Árabe', action = 'list_all', url = host + 'seccion/cine/arabic/' ))
    itemlist.append(item.clone( title = 'Alemán', action = 'list_all', url = host + 'seccion/cine/deutsche/' ))
    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'seccion/cine/cine-espanol/' ))
    itemlist.append(item.clone( title = 'Chino', action = 'list_all', url = host + 'seccion/cine/chinese/' ))
    itemlist.append(item.clone( title = 'Francés', action = 'list_all', url = host + 'seccion/cine/cine-francais/' ))
    itemlist.append(item.clone( title = 'Hindú', action = 'list_all', url = host + 'seccion/cine/hindi/' ))
    itemlist.append(item.clone( title = 'Inglés', action = 'list_all', url = host + 'seccion/cine/cine-english/' ))
    itemlist.append(item.clone( title = 'Italiano', action = 'list_all', url = host + 'seccion/cine/cine-italiano/' ))
    itemlist.append(item.clone( title = 'Japonés', action = 'list_all', url = host + 'seccion/cine/japanese/' ))
    itemlist.append(item.clone( title = 'Portugués', action = 'list_all', url = host + 'seccion/cine/portugues/' ))

    itemlist.append(item.clone( title = 'Subtitulado Vose', action = 'list_all', url = host + 'tema/subtitulos/' ))
    itemlist.append(item.clone( title = 'Subtitulado VO', action = 'list_all', url = host + 'tema/subtitles/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data,'>English<(.*?)>Inter<')

    matches = scrapertools.find_multiple_matches(bloque,'<a href="(.*?)".*?>(.*?)</a>')

    for url, tit in matches:
        if '/tv-series/' in url or '/seccion/' in url: continue

        elif tit == 'Subtitles': continue
        elif tit == 'Subtítulos': continue

        if 'eng' in url: tit = tit + ' (Eng)'

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article(.*?)</article>').findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        title = scrapertools.find_single_match(match, 'rel="bookmark">(.*?)</a>')
        if not url or not title: continue

        title = title.replace('&#8211;', '-')

        lang = scrapertools.find_single_match(match, '<span class="penci-cat-links">.*?>(.*?)</a>')
        if lang == 'Español': lang = 'Esp'
        elif lang == 'English': lang = 'Ing'
        elif lang == 'Deutsche': lang = 'Ale'
        elif lang == 'Chinese': lang = 'Chi'
        elif lang == 'Français': lang = 'Fra'
        elif lang == 'Hindi': lang = 'Hin'
        elif lang == 'Italiano': lang = 'Ita'
        elif lang == 'Arabic': lang = 'Arb'
        elif lang == 'Japanese': lang = 'Jap'

        elif 'Portug' in lang: lang = 'Por'

        year = scrapertools.find_single_match(title, '-(.*?)-').strip()
        if not year: year = '-'

        if '-' in title: title = scrapertools.find_single_match(title, '(.*?)-').strip()

        thumb = scrapertools.find_single_match(match, 'style="background-image: url(.*?);')
        thumb = thumb.replace('(', '').replace(')', '')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb, languages = lang,
                                            contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<nav class="navigation pagination"' in data:
            next_url = scrapertools.find_single_match(data, '<nav class="navigation pagination".*?class="page-numbers current">.*?href="(.*?)"')
            if next_url:
                if '/page/' in next_url:
                    itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    url = scrapertools.find_single_match(data,'div class="post-format-meta.*?<iframe.*?src="(.*?)"')

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            platformtools.dialog_notification(config.__addon_name, 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]')
            return

        elif '/ronemo.com/' in url:
            platformtools.dialog_notification(config.__addon_name, 'Servidor [COLOR tan]No Soportado[/COLOR]')
            return

        if not url.startswith("http"): url = "https:" + url

        lng = item.languages

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, language = lng ))

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

