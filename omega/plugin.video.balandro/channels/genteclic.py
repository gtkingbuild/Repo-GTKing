# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools, config
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.genteclic.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'trending/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    matches = scrapertools.find_multiple_matches(data, '<li class="cat-item cat-item-(.*?)">.*?<a href="(.*?)".*?>(.*?)</a>')

    for cat, url, tit in matches:
        if 'Academia de Sabiduría' in tit: continue

        elif tit == 'Conciertos': continue
        elif tit == 'Conspiraciones': continue
        elif tit == 'Curiosidades': continue
        elif tit == 'Educacion': continue
        elif tit == 'Metaciencia': continue
        elif tit == 'Peliculas': continue

        elif 'Cosmos' in tit: continue
        elif 'Playlist' in tit: continue

        elif tit == 'Series': continue
        elif tit == 'Salud': continue

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', cat = cat, text_color = 'deepskyblue' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Academia de sabiduría', action = 'list_all', url = host + 'category/academia-de-sabiduria-universal/', cat = '372', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Conciertos', action = 'list_all', url = host + 'category/conciertos/', cat = '293', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Conspiraciones', action = 'list_all', url = host + 'category/conspiraciones/', cat = '36', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Cosmos', action = 'list_all', url = host + 'category/documentales/cosmos-mundos-posibles/', cat = '191', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Curiosidades', action = 'list_all', url = host + 'category/curiosidades/', cat = '192', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Educación', action = 'list_all', url = host + 'category/educacion/', cat = '201', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Metaciencia', action = 'list_all', url = host + 'category/peliculas/metaciencia/', cat = '238', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'category/peliculas/', cat = '1', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Salud', action = 'list_all', url = host + 'category/salud/', cat = '193', text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if item.page == 1:
        bloque = scrapertools.find_single_match(data, '>Recientes<(.*?)<div class="jeg_block_navigation">')
        if not bloque: bloque = data

        matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

        for article in matches:
            url = scrapertools.find_single_match(article, ' href="(.*?)"')

            if not url: continue

            title = scrapertools.find_single_match(article, '<h3 class="jeg_post_title">.*?<a href=".*?">(.*?)</a>')
            if not title:  title = scrapertools.find_single_match(article, 'alt="(.*?)"')

            lang = ''
            if 'latino' in title.lower(): lang = 'Lat'
            elif 'español' in title.lower(): lang = 'Esp'

            if not '-' in title: title = title.replace('&#8211;', '-')
            else: title = title.replace('&#8211;', '')

            if not '/documentales/' in item.url:
                if '-' in title: title = scrapertools.find_single_match(title, '(.*?)-')

            if 'pelicula' in title: title = scrapertools.find_single_match(title.lower(), '(.*?)pelicula')
            elif 'película' in title: title = scrapertools.find_single_match(title.lower(), '(.*?)película')

            title = title.replace('Pelicula', '').replace('Película', '').replace('Online', '').replace('online', '').replace('-sinopsis', '')
            title = title.replace('Latino', '').replace('latino', '').replace('Español', '').replace('español', '').replace('completa en', '')
            title = title.replace(' - Ver', '').replace(' - pelicula', '').replace(' idioma', '').replace('pelicula', '').replace(' -', '')
            title = title.replace(' HD', '').replace(' ver', '').replace('( )', '')

            title = title.replace('&#8211;', '').replace('&#8217;s', "'").strip()

            title = title.capitalize()

            if not title: continue

            thumb = scrapertools.find_single_match(article, ' data-src="([^"]+)')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang,
                                        contentType='movie', infoLabels = {'year': '-'}, contentTitle=title ))

        if not itemlist: return itemlist

        tmdb.set_infoLabels(itemlist)

        if '/?s=' in item.url: return itemlist

    if itemlist or item.page:
        item.page += 1

        post = {"action": "jnews_module_ajax_jnews_video_block4_view",
                "module": "true",
                "s": "",
                "data[filter]": "0",
                "data[filter_type]": "all",
                "data[current_page]": item.page,
                "data[attribute][data_type]": "custom",
                "data[attribute][video_only]": "yes",
                "data[attribute][number_post]": "20",
                "data[attribute][pagination_number_post]": "20",
                "data[attribute][first_title]": "Latest+Videos",
                "data[attribute][sort_by]": "latest",
                "data[attribute][include_category]": item.cat
                }

        url = host + '?ajax-request=jnews'

        headers = {"accept": "text/html, */*; q=0.01",
                   "accept-language": "es-ES,es;q=0.9",
                   "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "x-requested-with": "XMLHttpRequest",
                   "Connection": "keep-alive",
                   "Referer": item.url
                   }

        data2 = do_downloadpage(url, post=post, headers=headers)
        data2 = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data2)

        data2 = str(data2).replace('\\/', '/')

        matches2 = scrapertools.find_multiple_matches(str(data2), '<article(.*?)</article>')

        for match in matches2:
            match = str(match).replace('\\/', '/')

            match = str(match).replace('=\\', '=').replace('\\"', '/"').replace('//"', '"').replace('/"', '"')

            url = scrapertools.find_single_match(match, '<a href="(.*?)"')

            title = scrapertools.find_single_match(match, 'alt="(.*?)"')

            if not url or not title: continue

            title = clean_title(title)

            title = title.replace('Pelicula', '').replace('Película', '').replace('Online', '').replace('online', '').replace('-sinopsis', '')
            title = title.replace('Latino', '').replace('latino', '').replace('Español', '').replace('español', '').replace('completa en', '')
            title = title.replace(' - Ver', '').replace(' - pelicula', '').replace(' idioma', '').replace('pelicula', '').replace(' -', '')
            title = title.replace(' HD', '').replace(' ver', '').replace('( )', '')

            title = title.replace('&#8211;', '').replace('&#8217;s', "'").strip()

            title = title.capitalize()

            thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', infoLabels = {'year': '-'}, contentTitle=title ))

        tmdb.set_infoLabels(itemlist)

        if matches2:
            itemlist.append(item.clone( title='Siguientes ...', url = item.url, page = item.page, action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, '<source type="video/mp4".*?src="(.*?)"')

    if not links:
        if 'data-type="youtube"' in data:
            patron = '<div class="jeg_featured_big">.*?'
            patron += 'data-src="([^"]+)"'

            links = scrapertools.find_multiple_matches(data, patron)

    if not links:
         bloque = scrapertools.find_single_match(data, '<div class="jeg_video_container">(.*?)/div></div></div>')

         links = scrapertools.find_multiple_matches(bloque, 'src="(.*?)"')
         if not links: links = scrapertools.find_multiple_matches(bloque, "src='(.*?)'")

    ses = 0

    for url in links:
        ses += 1

        if 'data:text' in url: continue

        if not url.startswith('http'): url = 'https' + url

        if '.bitchute.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        lang = item.languages
        if not lang: lang = 'Lat'

        itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def clean_title(title):
    logger.info()

    title = title.replace('\\u00e1', 'a').replace('\\u00c1', 'a').replace('\\u00e9', 'e').replace('\\u00ed', 'i').replace('\\u00f3', 'o').replace('\\u00fa', 'u')
    title = title.replace('\\u00f1', 'ñ').replace('\\u00bf', '¿').replace('\\u00a1', '¡').replace('\\u00ba', 'º')
    title = title.replace('\\u00eda', 'a').replace('\\u00f3n', 'o').replace('\\u00fal', 'u').replace('\\u00e0', 'a').replace('\\u00fc', 'u').replace('\\u00d3', 'o').replace('\\u00c9', 'e')

    return title


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
