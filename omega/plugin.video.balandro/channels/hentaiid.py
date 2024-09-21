# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://hentai-id.tv/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_xxx', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color='orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'archivos/h2/', group = 'find' ))

    itemlist.append(item.clone( title = 'Sin censura', action = 'list_all', url = host + 'archivos/sin-censura/' ))
    itemlist.append(item.clone( title = 'Alta definición', action = 'list_all', url = host + 'archivos/high-definition/' ))
    itemlist.append(item.clone( title = 'Los mejores', action = 'list_all', url = host + 'archivos/ranking-hentai/' ))

    itemlist.append(item.clone( title = 'Mangas H', action = 'list_all', url = host + 'archivos/m2/', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = scrapertools.find_single_match(data, 'id="hentai2"><div[^>]+>(.*?)</div></div>')

    matches = re.compile('href="([^"]+)"[^>]+>(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', url = url, title = title, text_color='orange' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    bloque = scrapertools.find_single_match(data, '<div class="col-xs-12 col-md-12 col-lg-9.*?<ul>(.*?)</ul><div class="clearfix">')
    if not bloque: bloque = scrapertools.find_single_match(data, '<h4>Busqueda en Hentais:</h4>(.*?)<div class="col-lg-3 col-md-12" >')

    matches = re.compile('<a href="([^"]+)".*?<img src="([^"]+)" title="([^"]+)"', re.DOTALL).findall(bloque)

    for url, thumb, title, in matches:
        title = title.replace('][', ' ').replace('[', ' ').replace(']', ' ')

        title = title.replace('&#8211;', '').replace('&#8230;', '').replace('&#039;', "'")

        if item.group == 'find':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))
        else:
            itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        bloque = scrapertools.find_single_match(data, "<div class='wp-pagenavi'(.*?)</div>")

        next_page = scrapertools.find_single_match(bloque, "<span aria-current='page'.*?" + 'href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    bloque = scrapertools.find_single_match(data, '<div class="box-entry-title text-center">Lista de Capítulos</div>(.*?)</div></div>')

    matches = re.compile('<a href="([^"]+)"[^>]+>([^<]+)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        title = title.replace('][', ' ').replace('[', ' ').replace(']', ' ')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if not itemlist:
        if '<iframe src="' in data or '<IFRAME SRC="':
            title = item.title

            itemlist.append(item.clone( action = 'findvideos', url = item.url, title = title, contentType = 'movie', contentTitle = title, contentExtra='adults' ))
            
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    videos = []
    downloads = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}', "", data)

    matches = re.compile('<(?:iframe)?(?:IFRAME)?\s*(?:src)?(?:SRC)?="([^"]+)"', re.DOTALL).findall(data)

    ses = 0

    for url in matches:
        ses += 1

        if 'goo.gl' in url or 'tinyurl' in url:
            video = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers["location"]
            videos.append(video)
        else: videos.append(url)

    paste = scrapertools.find_single_match(data, 'https://gpaste.us/([a-zA-Z0-9]+)')

    if paste:
        try:
           data = do_downloadpage('https://gpaste.us/' + paste)

           block = scrapertools.find_single_match(data, 'id="input_text">(.*?)</div>')

           matches = block.split('<br>')

           for url in matches:
               ses += 1

               downloads.append(url)
        except:
           pass

    videos.extend(downloads)


    for url in videos:
        if not url.startswith('http'): continue

        if '/streamango.' in url: continue
        elif '/verystream.' in url: continue
        elif '/openload.' in url: continue
        elif '/1fichier.' in url: continue

        elif '/vapley.' in url: continue
        elif '/megadl.' in url: continue
        elif '/tiny.' in url: continue
        elif '/bit.' in url: continue
        elif '/ouo.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Vo', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
