# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://detodopeliculas.nu/'


perpage = 28


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'novedades/' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas-de-estreno/', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Recomendadas', action = 'list_all', url = host + 'peliculas-recomendadas/' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Generos<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    matches = re.compile('<article(.*?)</article', re.DOTALL).findall(data)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, '</div>.*?<a href="(.*?)"')
        title = scrapertools.find_single_match(article, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, '<img src="(.*?)"')

        year = scrapertools.find_single_match(title, '(\d{4})')
        if not year: year = '-'
        else: title = title.replace('(' + year + ')', '').strip()

        title = title.replace('&#038;', '').replace('&#215;', 'x')

        langs = []
        if '/cas.png' in article: langs.append('Esp')
        if '/lat.png' in article: langs.append('Lat')
        if '/sub.png' in article: langs.append('Vose')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=', '.join(langs),
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, pagina = item.pagina, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "<a href='(.*?)'")

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', url = next_page, page = 0, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    ses = 0

    headers = {'Referer': item.url}

    matches = scrapertools.find_multiple_matches(data, 'id="player-option-(.*?)</li>')
    if not matches: matches = scrapertools.find_multiple_matches(data, "id='player-option-(.*?)</li>")

    for match in matches:
        ses += 1

        # ~ dtype, dpost, dnume
        dtype = scrapertools.find_single_match(match, ' data-type="(.*?)"')
        if not dtype: dtype = scrapertools.find_single_match(match, " data-type='(.*?)'")

        dpost = scrapertools.find_single_match(match, ' data-post="(.*?)"')
        if not dpost: dpost = scrapertools.find_single_match(match, " data-post='(.*?)'")

        dnume = scrapertools.find_single_match(match, ' data-nume="(.*?)"')
        if not dnume: dnume = scrapertools.find_single_match(match, " data-nume='(.*?)'")

        lang = scrapertools.find_single_match(match, '/img/flags/(.*?).png')

        if 'lat' in lang: lang = 'Lat'
        elif 'cas' in lang: lang = 'Esp'
        elif 'sub' in lang: lang = 'Vose'
        elif 'ing' in lang: lang = 'Vo'
        else: lang = '?'

        if dtype and dpost and dnume:
            post = {'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype}

            data1 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)

            embed = scrapertools.find_single_match(str(data1), '"embed_url":.*?"(.*?)"')

            if embed:
                ses += 1

                if not dnume == 'trailer':
                    embed = embed.replace('\\/', '/')

                    if embed.startswith('//'): embed = 'https:' + embed

                    servidor = servertools.get_server_from_url(embed)
                    servidor = servertools.corregir_servidor(servidor)

                    embed = servertools.normalize_url(servidor, embed)

                    other = ''
                    if servidor == 'various': other = servertools.corregir_other(embed)

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = embed,
                                          language = lang, other = other ))

    # ~ downloads
    post_id = scrapertools.find_single_match(data, ' name="comment_post_ID" value="(.*?)"')
    if not post_id: post_id = scrapertools.find_single_match(data, " name='comment_post_ID' value='(.*?)'")

    nonce = scrapertools.find_single_match(data, 'admin-ajax.php","nonce":"(.*?)"')

    if post_id and nonce:
        # ~ Castellano
        if '>Enlaces Castellano<' in data:
            post = {'action': 'event-list', 'post_id': post_id, 'idioma': 'Castellano', 'nonce': nonce}

            data2 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)

            links = scrapertools.find_multiple_matches(data2, "<tr id='link-(.*?)</tr>")

            for link in links:
                ses += 1

                if 'powvideo' in link: continue
                elif '1fichier' in link: continue

                enlace = scrapertools.find_single_match(link, "<a href='(.*?)'")

                if enlace:
                    data3 = do_downloadpage(enlace, headers = headers)

                    new_url = scrapertools.find_single_match(data3, 'href="(.*?)"')

                    if not new_url: continue

                    try:
                        url = httptools.downloadpage(new_url, follow_redirects=False).headers['location']
                    except:
                        url = ''

                    if url:
                        servidor = servertools.get_server_from_url(url)
                        servidor = servertools.corregir_servidor(servidor)

                        url = servertools.normalize_url(servidor, url)

                        other = ''
                        if servidor == 'various': other = servertools.corregir_other(url)

                        itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                             language = 'Esp', other = other ))

        # ~ Latino
        if '>Enlaces Latino<' in data:
            post = {'action': 'event-list', 'post_id': post_id, 'idioma': 'Latino', 'nonce': nonce}

            data2 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)

            links = scrapertools.find_multiple_matches(data2, "<tr id='link-(.*?)</tr>")

            for link in links:
                ses += 1

                if 'powvideo' in link: continue
                elif '1fichier' in link: continue

                enlace = scrapertools.find_single_match(link, "<a href='(.*?)'")

                if enlace:
                    data3 = do_downloadpage(enlace, headers = headers)

                    new_url = scrapertools.find_single_match(data3, 'href="(.*?)"')

                    if not new_url: continue

                    try:
                        url = httptools.downloadpage(new_url, follow_redirects=False).headers['location']
                    except:
                        url = ''

                    if url:
                        servidor = servertools.get_server_from_url(url)
                        servidor = servertools.corregir_servidor(servidor)

                        url = servertools.normalize_url(servidor, url)

                        other = ''
                        if servidor == 'various': other = servertools.corregir_other(url)

                        itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                            language = 'Lat', other = other ))

        # ~ Subtitulado
        if '>Enlaces Subtitulado<' in data:
            post = {'action': 'event-list', 'post_id': post_id, 'idioma': 'Subtitulado', 'nonce': nonce}

            data2 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = headers)

            links = scrapertools.find_multiple_matches(data2, "<tr id='link-(.*?)</tr>")

            for link in links:
                ses += 1

                if 'powvideo' in link: continue
                elif '1fichier' in link: continue

                enlace = scrapertools.find_single_match(link, "<a href='(.*?)'")

                if enlace:
                    data3 = do_downloadpage(enlace, headers = headers)

                    new_url = scrapertools.find_single_match(data3, 'href="(.*?)"')

                    if not new_url: continue

                    try:
                        url = httptools.downloadpage(new_url, follow_redirects=False).headers['location']
                    except:
                        url = ''

                    if url:
                        servidor = servertools.get_server_from_url(url)
                        servidor = servertools.corregir_servidor(servidor)

                        url = servertools.normalize_url(servidor, url)

                        other = ''
                        if servidor == 'various': other = servertools.corregir_other(url)

                        itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                             language = 'vose', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = data

    if '>Lo + Nuevo<' in data: bloque = scrapertools.find_single_match(data, '(.*?)Nuevo<')
    elif '>Top Mas Vistas<' in data: bloque = scrapertools.find_single_match(data, '(.*?)>Top Mas Vistas<')

    matches = re.compile('<article(.*?)</article', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src=(.*?)"')

        year = scrapertools.find_single_match(title, '(\d{4})')
        if not year: year = '-'
        else: title = title.replace('(' + year + ')', '').strip()

        title = title.replace('&#038;', '').replace('&#215;', 'x')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

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
