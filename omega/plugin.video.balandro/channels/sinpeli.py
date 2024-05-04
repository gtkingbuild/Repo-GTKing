# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


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


host = 'https://www.sinpeli.com/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_sinpeli_proxies', default=''):
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
    hay_proxies = False
    if config.get_setting('channel_sinpeli_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('sinpeli', url, post=post, headers=headers).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('sinpeli', url, post=post, headers=headers).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not '?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='sinpeli', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_sinpeli', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/castellano/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Castellano AC3 5.1', action = 'list_all', url = host + 'idioma/castellano51/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/latino/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Latino AC3 5.1', action = 'list_all', url = host + 'idioma/latino51/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/subtituladas/', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Genero</a>(.*?)>Idiomas<')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'deepskyblue' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Cam', action = 'list_all', url = host + 'calidad/cam/', text_color='moccasin' ))
    itemlist.append(item.clone( title = '720p', action = 'list_all', url = host + 'calidad/720p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = '1080p', action = 'list_all', url = host + 'calidad/1080p/', text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)class="Copy">')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<div class="Title">(.*?)</div>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        qlty = scrapertools.find_single_match(match, '<span class="Qlty">(.*?)</span>')

        year = '-'

        if title.endswith(')') == True:
           part_title = title.split('(')[0].strip()
           year = title.split('(')[1].strip()

           if part_title: title = part_title

           year = year.replace(')', '').strip()

           if not year: year = '-'

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#038;', '&')

        langs = []
        lngs = scrapertools.find_multiple_matches(match, 'bold;"><img src="(.*?)"')

        if 'castellano' in str(lngs): langs.append('Esp')
        if 'latino' in str(lngs): langs.append('Lat')
        if 'subtitulado' in str(lngs): langs.append('Vose')

        plot = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=', '.join(langs), qualities=qlty,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, "<span aria-current='page' class='current'>.*?" + 'href="(.*?)"')

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'data-tplayernv="Opt(.*?)</li>')

    ses = 0

    for match in matches:
        ses += 1

        servidor = scrapertools.find_single_match(match, "<span>(.*?)</span>").lower()

        if 'trailer' in servidor: continue

        if servidor == 'ok': servidor = 'okru'

        lang = scrapertools.find_single_match(match, "</span><span>(.*?)</span>").strip()

        if 'Latino' in lang: lang = 'Lat'
        elif 'Castellano' in lang or 'Español' in lang: lang = 'Esp'
        elif 'Subtitulado' in lang or 'VOSE' in lang: lang = 'Vose'
        else: lang = '?'

        qlty = scrapertools.find_single_match(match, "</span><span>.*?-(.*?)</span>").strip()
        if 'Subtitulado -' in qlty: qlty = qlty.replace('Subtitulado -', '').strip()

        url = scrapertools.find_single_match(match, 'data-player="(.*?)"')

        if not servidor == 'cuevana3'and not servidor == 'ver online':
            itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = lang, quality=qlty ))

        else:
            new_url = base64.b64decode(url)

            if 'b"' in str(new_url): new_url = str(new_url).replace('b"', '').replace('"', '')

            new_url = scrapertools.find_single_match(str(new_url), "src='(.*?)'")

            if new_url:
                data2 = do_downloadpage(new_url)

                links = scrapertools.find_multiple_matches(data2, "go_to_player.*?'(.*?)'")

                for link in links:
                    servidor = servertools.get_server_from_url(link)
                    servidor = servertools.corregir_servidor(servidor)

                    url = servertools.normalize_url(servidor, link)

                    other = ''

                    if servidor == 'directo': other = 'cuevana3'

                    itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = lang, quality = qlty, other = other ))

    # Descargas recaptcha y comprimidos por partes
    # patron = 'class="Button STPb  toggle_links">Download.*?">(.*?)</span>.*?href="(.*?)".*?alt=.*?">(.*?)</span>.*?class=.*?">(.*?)</span>'

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.other == 'cuevana3':
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

        return itemlist

    try:
        url = base64.b64decode(url)
        if url: url = scrapertools.find_single_match(str(url), "<iframe src='(.*?)'")
    except:
        url = item.url

    if not url: url = item.url

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

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

