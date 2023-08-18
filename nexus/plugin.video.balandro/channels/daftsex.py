# -*- coding: utf-8 -*-

import re, base64, time

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools


host = 'https://daft.sex/'


_player = 'https://dxb.to/'


espera = config.get_setting('servers_waiting', default=6)


def do_downloadpage(url, post=None, headers=None, timeout=None, raise_weberror=True):
    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

    if timeout is None: timeout = config.get_setting('channels_repeat', default=30)

    if not data:
        platformtools.dialog_notification('DaftSex', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(resp.data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
        except:
            pass

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color='orange' ))

    itemlist.append(item.clone( title = 'Últimos vídeos', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Más calientes', action = 'list_all', url = host + 'hottest'))

    itemlist.append(item.clone( title = 'Listas', action = 'listas', url = host + 'browse' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars' ))

    return itemlist


def listas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="video-title"[^>]+>([^<]+)<.*?a href="([^"]+).*?data-thumb="([^"]+)"').findall(data)

    for title, url, thumb in matches:
        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url,
                                    thumbnail = thumb if thumb.startswith('http') else host[:-1] + thumb, title = title, text_color='orange' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li><a href="([^"]+)" title="Next page"')

        if next_url:
            next_url = next_url.replace('&amp;', '&')

            next_url = host + next_url if not url.startswith('http') else host[:-1] + next_url

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'listas', text_color = 'coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'categories')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="video-item"><a href="([^"]+)".*?data-thumb="([^"]+)".*?<div class="video-title">([^<]+)').findall(data)

    for url, thumb, title in matches:
        url = host + url if not url.startswith('/') else host[:-1] + url

        thumb = host + thumb if not url.startswith('/') else host[:-1] + thumb

        itemlist.append(item.clone( action = 'list_all', url = url, title = title, thumbnail = thumb, text_color='orange' ))

    return sorted(itemlist, key=lambda i: i.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="pornstar"><a href="([^"]+)"><div class="[^"]+"><div class="lazy thumb".*?data-thumb="([^"]+)"></div></div><span>([^<]+)'

    matches = re.compile(patron).findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url,
                                    thumbnail = thumb if thumb.startswith('http') else host[:-1] + thumb, title = title, text_color='orange' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li><a href="([^"]+)" title="Next page"')

        if next_url:
            next_url = next_url.replace('&amp;', '&')

            next_url = host + next_url if not url.startswith('http') else host[:-1] + next_url

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'pornstars', text_color = 'coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="video-item video(.*?)</a></div>').findall(data)

    for match in matches:
        video_id = scrapertools.find_single_match(match, '(.*?)"')

        title = scrapertools.find_single_match(match, '<div class="video-title".*?>(.*?)</div>')
        if not title: title = 'Not Titled'

        title = title.replace('&quot;', '').replace('[', '').replace(']', '').strip()

        thumb = scrapertools.find_single_match(match, 'data-thumb="(.*?)"')

        time = scrapertools.find_single_match(match, '<span class="video-time">(.*?)</span>')

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        url = host + 'watch/%s' % (video_id)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li><a href="([^"]+)" title="Next page"')

        if next_url:
            next_url = next_url.replace('&amp;', '&')

            next_url = host + next_url if not url.startswith('http') else host[:-1] + next_url

            itemlist.append(item.clone( title = 'Siguientes ...', url= next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    hash = scrapertools.find_single_match(data, 'hash: "(.*?)"')
    color = scrapertools.find_single_match(data, 'hash:.*?color: "(.*?)"')

    if not hash or not color: return itemlist

    url = _player + 'player/%s?color=%s' % (hash, color)

    data = do_downloadpage(url, headers = {'Referer': host})

    ids = scrapertools.find_single_match(data, 'id: "(.*?)"')
    if not ids: return itemlist

    id1, id2 = ids.split('_')

    srv = scrapertools.find_single_match(data, 'server: "(.*?)"')[::-1]
    srv = base64.b64decode(srv).decode('utf-8')
    if not srv: return itemlist

    srv = "https://%s" % srv

    token = scrapertools.find_single_match(data, 'access_token: "(.*?)"')
    idv = scrapertools.find_single_match(data, 'id: "(.*?)"')
    c_key = scrapertools.find_single_match(data, 'c_key: "(.*?)"')
    credentials = scrapertools.find_single_match(data, 'credentials: "(.*?)"')

    e_key = scrapertools.find_single_match(data, 'extra_key: "(.*?)"')
    partial = scrapertools.find_single_match(data, 'partial: (.*?)}}')

    if credentials:
        url = srv + '/method/video.get/%s?token=%s&videos=%s&ckey=%s&credentials=%s&extra_key=%s' % (ids, token, idv, c_key, credentials, e_key)

        platformtools.dialog_notification('Cargando ' + '[COLOR cyan][B]Vídeos[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
        time.sleep(int(espera))

        data = do_downloadpage(url, headers = {'Referer': _player}, timeout = 40, raise_weberror=False)

        matches = re.compile('"mp4_(.*?)":"(.*?)"', re.DOTALL).findall(str(data))

        for qlty, url in matches:
            url = url.replace('\\u0026', '&')

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = qlty, url = url, language = 'VO' ))

    elif partial:
        bloque = scrapertools.find_single_match(str(data), '"quality":(.*?)$')

        if bloque:
            matches = re.compile('"(.*?)":"(.*?)"', re.DOTALL).findall(str(bloque))

            for qlty, url in matches:
                url = '%s/videos/%s/%s/%s.mp4?extra_key=%s' % (srv, id1, id2, qlty, e_key)

                itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = qlty, url = url, language = 'VO', other = 'Partial' ))

    else:
        matches = re.compile('"mp4_\d+":"(\d+).([^"]+)"', re.DOTALL).findall(str(data))

        for qlty, url in matches:
            url = '%s/videos/%s/%s/%s.mp4?extra=%s' % (srv, id1, id2, qlty, url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = qlty, url = url, language = 'VO' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "video/%s" % (texto.replace(" ", "%20"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
