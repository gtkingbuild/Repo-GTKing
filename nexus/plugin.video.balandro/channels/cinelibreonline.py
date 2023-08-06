# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.cinelibreonline.com/'


results = 14

perpage = 20
perpage_lis = 30


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/search?max-results=' + str(results), search_type = 'movie' ))

    itemlist.append(item.clone( title = 'La butaca', action = 'list_genre', url = host + 'p/butaca.html', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por alfabético', action = 'listas', url= host + 'p/peliculas.html', search_type='movie' ))

    itemlist.append(item.clone( title = 'Por categorias', action = 'categorias', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action = 'listas', title = 'Colecciones', url= host + 'p/colecciones.html', exec_action = 'list_genre', text_color='moccasin' ))
    itemlist.append(item.clone( action = 'listas', title = 'Cortometrajes', url= host + 'p/cortometrajes.html', text_color='moccasin' ))

    itemlist.append(item.clone( action = 'list_list', title = 'Dibujos animados', url= host + '2015/10/dibujos-animados-en-dominio-publico.html', text_color='moccasin' ))

    # ~ itemlist.append(item.clone( action = 'list_list', title = 'Disney', url = host + '2014/08/peliculas-de-disney-en-dominio-publico.html', text_color='moccasin' ))

    itemlist.append(item.clone( action = 'listas', title = 'Documentales', url= host + 'p/documentales.html', text_color='moccasin' ))

    itemlist.append(item.clone( action='list_all', title = 'Segunda guerra mundial', url= host + 'search/label/Segunda%20Guerra%20Mundial', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, """(?is)data-version='1' id='HTML6'>.*?widget-content(.*?)widget-content""")

    matches = scrapertools.find_multiple_matches(bloque, '(?is)href="([^"]+).*?src="([^"]+)')

    for url, thumb in matches:
        title = url.replace("-"," ").replace(" online","")
        title = scrapertools.find_single_match(title, '/p/(.*).h')

        title = title.replace('peliculas de', '').replace('peliculas', '').replace('clasicos', '').strip()
        title = title.capitalize()

        itemlist.append(item.clone( action='list_genre', title=title, url=url, thumbnail=thumb, text_color = 'deepskyblue' ))

    if itemlist:
        itemlist.append(item.clone( action='list_all', title='Historia', url= host + 'search/label/Historia', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( action='list_all', title='Thriller', url= host + 'search/label/Thriller', text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action = 'listas', title = 'Años 70/80', url= host + 'p/peliculas-anos-70-y-80.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( action = 'listas', title = 'Años 60', url= host + 'p/peliculas-anos-60.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( action = 'listas', title = 'Años 50', url= host + 'p/peliculas-anos-50.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( action = 'listas', title = 'Años 40', url= host + 'p/peliculas-anos-40.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( action = 'listas', title = 'Años 30', url= host + 'p/peliculas-anos-30.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( action = 'listas', title = 'Años 20', url= host + 'p/peliculas-anos-20.html', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron  = "(?is)post-title entry.*?href='([^']+)'>([^<]+)"
    patron += '.*?tulo original</i>: <b>([^<]+).*?<i>.*?Año</i>: ([^<]+).*?<a href="([^"]+)'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, title, Title, year, thumb in matches:
        if not year: year = '-'
        else:
            if year in title:
                title = title.replace('(' + year + ')', '').strip()
                if year in title: title = title.replace(year, '').strip()

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=Title, infoLabels={'year': year} ))

    if not '/search?q=' in item.url:
        tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, """blog-pager-older-link.*?href='([^']+)""")

        if next_page:
            res = scrapertools.find_single_match(next_page, '&max-results=\w+')
            if not next_page.endswith("&"): next_page += '&'

            next_page = next_page.replace(res, '') + 'max-results=' + str(results)

            itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral'))

    return itemlist


def list_list(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<span style="font-size:.*?">(.*?)<br /><br /><br /><br />')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(match, '<u><b>(.*?)</b>')

        if title == '<br />': title = scrapertools.find_single_match(match, '<span style="font-size:.*?"><u><b>(.*?)</b>')

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, '<i>Año</i>: (.*?)"<br />').strip()
        if not year: year = '-'
        else:
            if year in title:
                title = title.replace('(' + year + ')', '').strip()
                if year in title: title = title.replace(year, '').strip()

        bloque = scrapertools.find_single_match(match, '>Ver online(.*?)$')

        url = scrapertools.find_single_match(bloque, '<a href="(.*?)"')

        if '.blogspot.' in url: continue

        if url:
            if url.startswith('//'): url = 'https:' + url

            ver = scrapertools.find_single_match(bloque, '</b></a>(.*?)<br />').strip()
            titulo = title + ' ' + ver

            itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if 'Ver online' in bloque:
            url = scrapertools.find_single_match(bloque, 'Ver online.*?<a href="(.*?)"')

            if url:
                if url.startswith('//'): url = 'https:' + url

                ver = scrapertools.find_single_match(bloque, 'Ver online.*?</b></a>(.*?)$').strip()
                titulo = title + ' ' + ver

                itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

            if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage

            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_genre', text_color='coral' ))

    return itemlist


def list_genre(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, """(?is)id='post-body(.*?)clear: both;""")

    if item.exec_action:
        matches = scrapertools.find_multiple_matches(bloque, '<h3>.*?href="(.*?)".*?target="_blank">(.*?)</a>.*?src="(.*?)"')
        if not matches: matches = scrapertools.find_multiple_matches(bloque, 'href="([^"]+).*?alt="([^"]+).*?src="([^"]+)')
    else:
        matches = scrapertools.find_multiple_matches(bloque, 'href="([^"]+).*?alt="([^"]+).*?src="([^"]+)')

    num_matches = len(matches)

    for url, title, thumb in matches[item.page * perpage:]:
        if '.blogspot.' in url: continue

        if thumb.startswith('//'): thumb = 'https:' + thumb

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage

            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_genre', text_color='coral' ))

    return itemlist


def listas(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    data = do_downloadpage(item.url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, "<div class='post-body entry-content'(.*?)<div style='clear: both;'></div>")

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?">(.*?)</a>')

    num_matches = len(matches)

    for url, title in matches[item.page * perpage_lis:]:
        title = title.replace('<b>', '').replace('</b>', '')

        if '<span' in title:
            if  '</span></span>' in title: title = scrapertools.find_single_match(title, '<span.*?">(.*?)<span').strip()
            elif not '></span>' in title:  title = scrapertools.find_single_match(title, '<span.*?">(.*?)</span').strip()
            else: title = scrapertools.find_single_match(title, '(.*?)<span').strip()

        elif '.html' in title: title = scrapertools.find_single_match(title, '.html.*?">(.*?)$').strip()

        action = 'findvideos'
        contentTitle = title

        if item.exec_action:
            action = item.exec_action
            contentTitle = ''

        itemlist.append(item.clone( action = action, url = url, title = title, contentType = 'movie', contentTitle = contentTitle, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage_lis: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage_lis:
            hasta = (item.page * perpage_lis) + perpage_lis

            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='listas', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if '/youtu' in item.url or '/www.youtube' in item.url:
        servidor = servertools.get_server_from_url(item.url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = item.url ))
        return itemlist

    elif '.wikipedia.' in item.url or '.wikimedia.' in item.url:
        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = item.url ))
        return itemlist

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '(?is)>ver \w+ online:.*?href="([^"]+).*?/span>.*?\(([^\)]+)' )

    if not matches:
        matches = scrapertools.find_multiple_matches(data, '>Ver película online.*?href="([^"]+)".*?/span>.*?\(([^\)]+)' )

        if not matches:
            bloque = scrapertools.find_single_match(data, '<b><u>(.*?)<div')
            matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?</span>(.*?)<br />' )

    ses = 0

    for url, idioma in matches:
        ses += 1

        if '.blogspot.' in url: continue

        if url.startswith('//'): url = 'https:' + url

        if 'original' in idioma:
            if 'doblada' in idioma: lang = 'Vose'
            elif 'español' in idioma: lang = 'Esp'
            elif 'subtitulos' in idioma: lang = 'Vose'
            elif 'subtítulos' in idioma: lang = 'Vose'	
            else: lang = 'VO'
        elif 'español' in idioma: lang = 'Esp'
        else: lang = '?'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.server == 'directo':
        data = do_downloadpage(url)
        url = scrapertools.find_single_match(data, '<source src="(.*?)"')
        if url.startswith('//'): url = 'https:' + url

    if url:
        itemlist.append(item.clone(url = url, server = item.server))

    return itemlist


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
