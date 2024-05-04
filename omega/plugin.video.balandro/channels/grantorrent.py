# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


LINUX = False
BR = False
BR2 = False

if PY3:
    try:
       import xbmc
       if xbmc.getCondVisibility("system.platform.Linux.RaspberryPi") or xbmc.getCondVisibility("System.Platform.Linux"): LINUX = True
    except: pass
 
try:
   if LINUX:
       try:
          from lib import balandroresolver2 as balandroresolver
          BR2 = True
       except: pass
   else:
       if PY3:
           from lib import balandroresolver
           BR = true
       else:
          try:
             from lib import balandroresolver2 as balandroresolver
             BR2 = True
          except: pass
except:
   try:
      from lib import balandroresolver2 as balandroresolver
      BR2 = True
   except: pass


host = 'https://www1.grantorrent.wf/'


# ~ por si viene de enlaces guardados
ant_hosts = ['http://grantorrent.net/', 'https://grantorrent1.com/', 'https://grantorrent.one/',
             'https://grantorrent.tv/', 'https://grantorrent.la/', 'https://grantorrent.io/',
             'https://grantorrent.eu/', 'https://grantorrent.cc/', 'https://grantorrent.li/',
             'https://grantorrent.online/', 'https://grantorrentt.com/', 'https://grantorrent.nl/',
             'https://grantorrent.ch/', 'https://grantorrent.ac/', 'https://grantorrent.re/',
             'https://grantorrent.se/', 'https://grantorrent.si/', 'https://grantorrent.fi/',
             'https://grantorrent.bz/', 'https://grantorrent.zip/', 'https://www1.grantorrent.pm/']


domain = config.get_setting('dominio', 'grantorrent', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'grantorrent')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'grantorrent')
    else: host = domain


# ~ b64_host 'grantorrent.fi'
points = host.count('.')

if points == 1:
    b64_host = host.replace('https://', '').replace('/', '')
else:
    tmp_host = host.split('.')[0]
    tmp_host = tmp_host + '.'
    b64_host = host.replace(tmp_host, '').replace('/', '')


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_grantorrent_proxies', default=''):
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


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    headers = {'Referer': host}

    hay_proxies = False
    if config.get_setting('channel_grantorrent_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('grantorrent', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('GranTorrent', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('grantorrent', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('grantorrent', url, post=post, headers=headers, timeout=timeout).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
            except:
                pass

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'grantorrent', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_grantorrent', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='grantorrent', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_grantorrent', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = {
        'accion': 'Acción',
        'animacion': 'Animación',
        'aventura': 'Aventura',
        'biografia': 'Biografía',
        'ciencia-ficcion': 'Ciencia ficción',
        'comedia': 'Comedia',
        'crimen': 'Crimen',
        'deporte': 'Deporte',
        'documental': 'Documental',
        'drama': 'Drama',
        'familia': 'Familia',
        'fantasia': 'Fantasía',
        'guerra': 'Guerra',
        'historia': 'Historia',
        'misterio': 'Misterio',
        'musica': 'Música',
        'romance': 'Romance',
        'suspense': 'Suspense',
        'terror': 'Terror',
        'western': 'Western'
        }

    for opc in sorted(opciones):
        itemlist.append(item.clone( title = opciones[opc], url = host + 'categoria/' + opc + '/', action ='list_all', text_color = 'deepskyblue' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'peliculas/')

    bloque = scrapertools.find_single_match(data, '<label for="quality"(.*?)</select>')

    matches = re.compile('<option value="(.*?)".*?>(.*?)</option>', re.DOTALL).findall(bloque)

    for value, title in matches:
        if not value: continue

        value = value.strip()
        title = title.strip()

        url = host + 'tag/' + value.replace(' ', '-').lower() + '/'

        itemlist.append(item.clone( title=title, url=url, action='list_all', text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="relative my-5 md:my-4">(.*?)</p></div></div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(http[^"]+)')

        lang = 'Esp'

        qlty = scrapertools.find_single_match(match, ' text-center">.*?<span>(.*?)</span>')

        title = title.replace('&#038;', '').strip()

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang, qualities=qlty,
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<span aria-current='page'>.*?<a href='(.*?)'")

        if next_page:
            if '/page/' in next_page:
                next_page = next_page.replace('&#038;', '&')

                itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    txt = txt.lower().replace(' ', '').replace('-', '')

    orden = ['3d',
             'screener',
             'screener720p',
             'hdscreener',
             'brscreener',
             'avi',
             'mkv',
             'dvdrip',
             'hdrip',
             '720p',
             'bluray720p',
             'microhd',
             'microhd1080p',
             '1080p',
             'blurayrip',
             'bluray1080p',
             'fullbluray1080p',
             'bdremux1080p',
             '4k',
             'full4k',
             '4kuhdrip',
             '4kfulluhd',
             '4kuhdremux',
             '4kuhdremux1080p',
             '4khdr']

    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium ml-auto">.*?href="(.*?)"', re.DOTALL).findall(data)

    for url in matches:
        if not url.endswith('.torrent'):
            if not '/s.php' in url: continue

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent',
                              language = item.languages, quality = item.qualities, quality_num = puntuar_calidad(item.qualities) ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if not item.url.endswith('.torrent'):
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(item.url, host_torrent)

        if url_base64.endswith('.torrent'):
           url_base64 = url_base64.replace(host, 'https://dl.' + b64_host + '/' )
           item.url = url_base64

    if item.url.endswith('.torrent'):
        if config.get_setting('proxies', item.channel, default=''):
            if PY3:
                from core import requeststools
                data = requeststools.read(item.url, 'grantorrent')
            else:
                data = do_downloadpage(item.url)

            if data:
                if '<h1>404 Not Found</h1>' in str(data) or '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data) or '<!doctype' in str(data):
                    return 'Archivo [COLOR red]Inexistente[/COLOR]'

                elif 'Página no encontrada</title>' in str(data) or 'no encontrada</title>' in str(data) or '<h1>403 Forbidden</h1>' in str(data):
                    return 'Archivo [COLOR red]No encontrado[/COLOR]'

                import os

                file_local = os.path.join(config.get_data_path(), "temp.torrent")
                with open(file_local, 'wb') as f: f.write(data); f.close()

                itemlist.append(item.clone( url = file_local, server = 'torrent' ))
        else:
            itemlist.append(item.clone( url = item.url, server = 'torrent' ))

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
