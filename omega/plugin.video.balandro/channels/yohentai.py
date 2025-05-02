# -*- coding: utf-8 -*-

import base64, re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://yohentai.net/'


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_xxx', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', search_video = 'adult', text_color='orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'search?categoria=hentai' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'hentai/' ))

    itemlist.append(item.clone( title = 'Sin censura', action = 'list_all', url = host + 'search?genero=3d%2Csin-censura', text_color = 'tan' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'search?genero=1080p' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'search').data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    bloque = scrapertools.find_single_match(data, '>Buscar Género<(.*?)</div></div>')

    matches = re.compile('value="(.*?)".*?<label data-multi="true.*?>(.*?)</label>', re.DOTALL).findall(bloque)

    for genre, title in matches:
        if title == '1080p': continue
        elif title == 'Sin Censura': continue

        url = host + 'search?genero=' + genre

        itemlist.append(item.clone( action = 'list_all', url = url, title = title, text_color='moccasin' ))

    return sorted(itemlist, key=lambda i: i.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    matches = re.compile('<li class="col mb-5">(.*?)</div></a></li>', re.DOTALL).findall(data)
    if not matches: matches = re.compile('<li class="col mb-3">(.*?)</div></a></li>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="fs-6 my-2 text-light">(.*?)</h2>')
        if not title: title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        title = title.replace('Episode', '[COLOR goldenrod]Epis.[/COLOR]')

        itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        if '<ul class="pagination' in data:
            next_page = scrapertools.find_single_match(data, '<li class="page-item active".*?</li>.*?href="(.*?)"')

            next_page = next_page.replace('&amp;', '&')

            if next_page:
                if '?p=' in next_page or '&p=' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)

    _token = scrapertools.find_single_match(data, '<meta name="csrf-token" content="(.*?)"')

    if not _token: return itemlist

    data_ajax = scrapertools.find_single_match(data, 'data-ajax="(.*?)"')

    if not data_ajax: return itemlist

    post = {'_token': _token, 'order': '1'}
    headers = {'Referer': item.url}

    data = httptools.downloadpage(data_ajax, post=post, headers=headers).data

    data = str(data).replace('},', '"').replace('}]', '"')

    matches = re.compile('"num":(.*?)"', re.DOTALL).findall(str(data))

    for match in matches:
        url = item.url.replace('/hentai/', '/ver/').replace('sub-espanol', '')

        url = url + 'capitulo-' + str(match)

        titulo = 'Episodio ' + str(match)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, contentType = 'movie',
                                    contentTitle = item.title, contentExtra='adults' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}', "", data)

    lang = 'Vose'

    matches = re.compile('data-player="(.*?)".*?>(.*?)</button>', re.DOTALL).findall(data)

    ses = 0

    for url, srv in matches:
        ses += 1

        if not srv: continue

        srv = srv.lower()

        if 'com/' in srv: continue

        elif srv == 'senvid2': continue
        elif srv == 'embed': continue

        if srv == 'ok': srv = 'okru'

        servidor = servertools.corregir_servidor(srv)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(srv)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

    # ~ Descargas
    matches = re.compile('<a class="btn btn-secondary" target="_blank" href="(.*?)"', re.DOTALL).findall(data)

    ses = 0

    for url in matches:
        ses += 1

        if 'fireload' in url: continue
        elif '1fichier' in url: continue
        elif '1cloudfile' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if not 'http' in item.url: url = base64.b64decode(item.url).decode("utf-8")

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        config.set_setting('search_last_video', texto)

        item.url =  host + 'buscar?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
