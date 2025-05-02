# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, os

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://en.rarbg-official.to/'


url_browser = host + "browse-movies"


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_rarbg_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar ...[/B]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None):
    hay_proxies = False
    if config.get_setting('channel_rarbg_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('rarbg', url, post=post, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, timeout=timeout).data

        if not data:
            if not '?keyword=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('RarBg', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('rarbg', url, post=post, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if not url.startswith(host):
            data = httptools.downloadpage(url, post=post, timeout=timeout).data
        else:
            if hay_proxies:
                data = httptools.downloadpage_proxy('rarbg', url, post=post, timeout=timeout).data
            else:
                data = httptools.downloadpage(url, post=post, timeout=timeout).data

    if '<title>Just a moment...</title>' in data:
        if not '?keyword=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='rarbg', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_rarbg', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('animejl') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = url_browser, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = url_browser + '?keyword=&rating=5', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En [COLOR moccasin]4K[/COLOR]', action = 'list_all', url = url_browser + '?keyword=&quality=2160p', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(url_browser)

    bloque = scrapertools.find_single_match(data,'>Quality:<(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque,'<option value="(.*?)".*?>(.*?)</option>')

    for qltys, tit in matches:
        if qltys == 'all': continue

        url = url_browser + '?keyword=&quality=' + qltys

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = 'moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(url_browser)

    bloque = scrapertools.find_single_match(data,'>Genre:<(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque,'<option value="(.*?)".*?>(.*?)</option>')

    for genre, tit in matches:
        if tit == 'All': continue

        url = url_browser + '?keyword=&genre=' + genre

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(url_browser)

    bloque = scrapertools.find_single_match(data,'<div id="main-search".*?>Year:<(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque,'<option value="(.*?)"')

    for anyos in matches:
        if anyos == '0': continue

        url = url_browser + '?keyword&year=' + anyos

        itemlist.append(item.clone( title = anyos, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = data.replace('</div></div> </div>', '</div></div></div>')

    matches = re.compile('<div class="browse-movie-wrap col-xs-10 col-sm-4 col-md-5 col-lg-4">(.*?)</div></div></div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'class="browse-movie-title">(.*?)</a>')

        if not url or not title: continue

        url = host[:-1] + url

        if '</span>' in title: 
            title = scrapertools.find_single_match(title, '</span>(.*?)$').strip()

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        thumb = host[:-1] + thumb

        year = scrapertools.find_single_match(match, '<div class="browse-movie-year">(.*?)$')
        if not year: tear = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'class="current">.*?href="(.*?)"')

        if next_page:
            if '?page=' in next_page:
                next_page = host[:-1] + next_page

                itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="modal-torrent">(.*?)</a></div>', re.DOTALL).findall(data)

    ses = 0

    for match in matches:
        ses += 1

        url1 = scrapertools.find_single_match(match, ' href="(.*?)"')

        if url1:
            url1 = host[:-1] + url1

            qlty = scrapertools.find_single_match(match, 'id="modal-quality-.*?<span>(.*?)</span>')

            lang = 'Vo'

            if item.lang: lang = item.lang

            peso = scrapertools.find_single_match(match, '<p>File size</p>.*?<p class="quality-size">(.*?)</p>')

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url1, server = 'torrent',
                                  language = lang, quality = qlty, other = peso ))

        url2 = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if url2:
            if not 'magnet:?' in url2: url2 = host[:-1] + url2

            qlty = scrapertools.find_single_match(match, 'id="modal-quality-.*?<span>(.*?)</span>')

            lang = 'Vo'

            if item.lang: lang = item.lang

            peso = scrapertools.find_single_match(match, '<p>File size</p>.*?<p class="quality-size">(.*?)</p>')

            age = ''

            if 'magnet:?' in url2: age = 'Magnet'

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url2, server = 'torrent',
                                  language = lang, quality = qlty, other = peso, age = age ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url.endswith('.torrent'):
        if config.get_setting('proxies', item.channel, default=''):
            if PY3:
                from core import requeststools
                data = requeststools.read(item.url, 'rarbg')
            else:
                data = do_downloadpage(item.url)

            if data:
                if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
                    return 'Archivo [COLOR red]Inexistente[/COLOR]'

                file_local = os.path.join(config.get_data_path(), "temp.torrent")
                with open(file_local, 'wb') as f: f.write(data); f.close()

                itemlist.append(item.clone( url = file_local, server = 'torrent' ))
                return itemlist
        else:
            itemlist.append(item.clone( url = item.url, server = 'torrent' ))

            return itemlist

    itemlist.append(item.clone( url = item.url, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = url_browser + '?keyword=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
