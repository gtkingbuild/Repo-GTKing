# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3: PY3 = False
else: PY3 = True

import os, re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

# ~ Dominio 8/10/2022

host = 'https://atomohd.vg/'


clon_name = 'Atomix'

perpage = 20

color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')


CLONES = [
   ['atomix', host, 'movie, tvshow', 'atomixhq.png'],
   ['descargas2020', 'https://descargas2020.net/', 'movie', 'descargas2020.jpg']
   ]

# ~ 'descargas2020'  prescindimos de series y buscar, sin proxies,  WEB CERRADA 25/9/2022

# ~ Para una misma peli/serie no siempre hay uno sólo enlace, pueden ser múltiples. La videoteca de momento no está preparada para acumular
# ~ múltiples enlaces de un mismo canal, así que solamente se guardará el enlace del último agregado.

# ~ Las entradas en la web parecen manuales y pueden ser un poco dispares, lo cual dificulta interpretar título, idioma, calidades, etc.


def item_configurar_proxies(item, clon_host):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_newpct1_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder "utilizar/reproducir" este canal en alguno de sus clones necesites configurar algún proxy,'
    plot += ' ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + clon_host + ' necesitarás un proxy.'
    title = 'Configurar proxies a usar ...  [COLOR plum](si no hay resultados)[COLOR moccasin] comunes en todos los clones[/COLOR]'
    return item.clone( title = title, action = 'configurar_proxies', host = clon_host, folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, item.host)


def do_downloadpage(item, url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://pctmix.com/', 'https://pctmix1.com/',
                 'https://pctreload.com/', 'https://pctreload1.com/',
                 'https://maxitorrent.com/',
                 'https://atomixhq.com/', 'https://atomixhq.one/', 'https://atomixhq.net/', 'https://atomixhq.top/', 'https://atomixhq.art/', 'https://atomixhq.link/', 'https://atomixhq.club/',
                 'https://nucleohd.com/', 'https://atomixhq.tel/', 'https://atomixhq.xyz/',
                 'https://atomohd.com/', 'https://atomohd.net/', 'https://atomohd.org/', 'https://atomohd.xyz/', 'https://atomohd.life/', 'https://atomohd.art/', 'https://atomohd.top/',
                 'https://atomohd.one/', 'https://atomohd.tel/', 'https://atomohd.pl/', 'https://atomohd.link/', 'https://atomohd.in/', 'https://atomohd.re/', 'https://atomohd.cc/',
                 'https://atomohd.click/', 'https://atomohd.wf/', 'https://atomohd.pm/', 'https://atomohd.app/', 'https://atomohd.live/', 'https://atomohd.vip/', 'https://atomohd.yt/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ intento sin proxies
    data = ''

    if not headers: headers = {'Referer': url}

    # ~ 2022/03/19 atomix en k17 y k18 (HTTP Error 403: Forbidden, salta >Attention Required! | Cloudflare)
    try: data = httptools.downloadpage(url, post=post, headers=headers).data
    except: pass

    if not data:
        if config.get_setting('proxies', item.channel, default=''): data = httptools.downloadpage_proxy('newpct1', url, post=post, headers=headers).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item, host))

    itemlist.append(item.clone( title = '[COLOR yellow]Buscar ...[/COLOR] (búsquedas solo en ' + clon_name + ')', action = 'search', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item, host))

    itemlist.append(item.clone( title = '[COLOR deepskyblue]Buscar película ...[/COLOR] (búsquedas solo en ' + clon_name + ')', action = 'search', search_type = 'movie' ))

    for clone in CLONES:
        if 'movie' in clone[2]:
            thumb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', clone[3])
            url = clone[1]

            color = 'white'

            if config.get_setting('proxies', item.channel, default=''): color = color_list_proxies

            itemlist.append(item.clone( title = clone[0].capitalize(), action = 'mainlist_pelis_clon', url = url, thumbnail = thumb, text_color=color ))

    return itemlist


def mainlist_pelis_clon(item):
    logger.info()
    itemlist = []

    item.category += '~' + item.title

    clon_host = item.url

    itemlist.append(item_configurar_proxies(item, clon_host))

    if not 'descargas2020' in clon_host:
        itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', url = item.url, search_type = 'movie', text_color='deepskyblue' ))

    enlaces = [
        ['Estrenos', 'estrenos-de-cine/'],
        ['En castellano', 'peliculas/'],
        ['En latino', 'peliculas-latino/'],
        # - ['Películas en Subtitulado', 'peliculas-vo/'],
        ['En HD', 'peliculas-hd/'],
        ['En HD FullBluRay', 'peliculas-hd/fullbluray-1080p/'],
        ['En HD BluRay', 'peliculas-hd/bluray-1080p/'],
        ['En HD MicroHD', 'peliculas-hd/microhd-1080p/'],
        ['En X264', 'peliculas-x264-mkv/'],
        ['En 4K UltraHD', 'peliculas-hd/4kultrahd/'],
        ['En 4K UHDremux', 'peliculas-hd/4k-uhdremux/'],
        ['En 4K UHDmicro', 'peliculas-hd/4k-uhdmicro/'],
        ['En 4K UHDrip', 'peliculas-hd/4k-uhdrip/'],
        ['En 4K Full UHD4K', 'peliculas-hd/full-uhd4k/'],
        ['En 4K Webrip', 'peliculas-hd/4k-webrip/'],
        ['En 3D', 'peliculas-3d/']
        ]

    if 'descargas2020' in item.url: 
        item.url += 'categoria/'
        enlaces = [
            ['Estrenos', 'estrenos-de-cine/'],
            ['En castellano', 'peliculas-castellano/'],
            ['En latino', 'peliculas-latino/'],
            ['En HD', 'peliculas-hd/'],
            ['En X264', 'peliculas-x264-mkv/'],
            ['En Rip', 'peliculas-rip/'],
            ['En 3D', 'peliculas-3d/']
            ]

    for enlace in enlaces:
        itemlist.append(item.clone( title = enlace[0], action = 'list_all', url = item.url + enlace[1], search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item, host))

    itemlist.append(item.clone( title = '[COLOR hotpink]Buscar serie ...[/COLOR] (búsquedas solo en ' + clon_name + ')', action = 'search', search_type = 'tvshow' ))

    for clone in CLONES:
        if 'tvshow' in clone[2]:
            thumb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', clone[3])
            url = clone[1]

            color = 'white'

            if config.get_setting('proxies', item.channel, default=''): color = color_list_proxies

            itemlist.append(item.clone( title = clone[0].capitalize(), action = 'mainlist_series_clon', url = url, thumbnail = thumb, text_color=color ))

    return itemlist


def mainlist_series_clon(item):
    logger.info()
    itemlist = []

    item.category += '~' + item.title

    clon_host = item.url

    itemlist.append(item_configurar_proxies(item, clon_host))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', url = item.url, search_type = 'tvshow', text_color='hotpink' ))

    enlaces = [
        ['Catálogo', 'series/'],
        ['En HD', 'series-hd/'],
        ['Subtituladas', 'series-vo/']
        ]

    if 'descargas2020' in item.url: del enlaces[1:]

    for enlace in enlaces:
        itemlist.append(item.clone( title = enlace[0], action = 'list_all', url = item.url + enlace[1], search_type = 'tvshow' ))

    return itemlist


def limpiar_titulo(title, quitar_sufijo=''):
    prefijos = ['Ver en linea ', 'Ver online ', 'Descarga Gratis ', 'Descarga Serie HD ',
                'Descargar Estreno ', 'Descargar Pelicula ', 'Descargar torrent ']

    for prefijo in prefijos:
        if title.startswith(prefijo): title = title[len(prefijo):]

    if title.endswith(' en HD'): title = title.replace(' en HD', '')

    m = re.match(r"^Descargar (.*?) torrent gratis$", title)
    if m: title = m.group(1)

    m = re.match(r"^Descargar (.*?)gratis$", title)
    if m: title = m.group(1)

    m = re.match(r"^Descargar (.*?) torrent$", title)
    if m: title = m.group(1)

    m = re.match(r"^Pelicula en latino (.*?) gratis$", title)
    if m: title = m.group(1)

    if quitar_sufijo != '': title = re.sub(quitar_sufijo+'[A-Za-z .]*$', '', title)

    return title.strip()


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    quitar_sufijo = ''
    if '-3d/' in item.url: quitar_sufijo = ' 3D'

    data = do_downloadpage(item, item.url)

    patron = '<li>\s*<a href="([^"]+)" title="([^"]+)">\s*<img src="([^"]+)"[^>]+>'
    patron += '\s*<h2[^>]*>[^<]+</h2>\s*<span>([^<]+)</span>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    num_matches = len(matches)

    for url, title, thumb, quality in matches[item.page * perpage:]:
        # descartar descargas de pc, revistas pdf
        if '/varios/' in item.url and quality in ['ISO','DVD-Screener']: continue

        year = scrapertools.find_single_match(title, '\((\d{4})\)')
        if year: title = title.replace('(%s)' % year, '').strip()
        else: year = '-'

        title = limpiar_titulo(title, quitar_sufijo)
        titulo = title

        if item.search_type == 'tvshow':
            m = re.match(r"^(.*?) - (Temporada \d+) Capitulo \d*", title)

            if not m:  m = re.match(r"^(.*?) - (Temporada \d+)", title)
            if m:
                title = m.group(1)
                titulo = '%s [%s]' % (title, m.group(2))

        if thumb.startswith('//'): thumb = 'https:' + thumb

        if item.search_type == 'tvshow':
            itemlist.append(item.clone( action='episodios', url=url, title=titulo, thumbnail=thumb, qualities=quality, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, qualities=quality, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break


    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)">Next</a>')
            if next_page:
                itemlist.append(item.clone( title='Siguientes ...', url=next_page, page=0, text_color='coral' ))

    return itemlist


def tracking_all_episodes(item):
    itemlist = episodios(item)
    while itemlist[-1].title == 'Siguientes ...':
        itemlist = itemlist[:-1] + episodios(itemlist[-1])
    return itemlist


def extraer_show(title):
    show = ''
    season = ''
    episode = ''

    datos = scrapertools.find_single_match(title, '(.*?) (?:Temporada|Temp\.) (\d+) (?:Capitulos|Cap\.) (\d+)')
    if not datos: datos = scrapertools.find_single_match(title, '(.*?) (?:Temporada|Temp\.) (\d+) (?:Capitulo|Cap\.) (\d+)')

    if datos: show, season, episode = datos
    else:
        datos = scrapertools.find_single_match(title, '(.*?) - (?:Temporada|Temp\.) (\d+).*?\[Cap\.(\d+)\]')
        if datos:
            show, season, episode = datos
            if episode.startswith(season): episode = episode[len(season):]
        else:
            datos = scrapertools.find_single_match(title, '(.*?) Temporada[^0-9]*(\d+)[^C]*Capitulos[^0-9]*(\d+)')
            if not datos: datos = scrapertools.find_single_match(title, '(.*?) Temporada[^0-9]*(\d+)[^C]*Capitulo[^0-9]*(\d+)')
            if datos: show, season, episode = datos

    if show.startswith('Serie '): show = show.replace('Serie ', '')

    return show.strip(), season, episode


def episodios(item):
    logger.info()
    itemlist = []

    episodes = []

    data = do_downloadpage(item, item.url)

    ul = scrapertools.find_single_match(data, '<ul class="buscar-list">(.*?)</ul>')

    matches = re.compile('<li[^>]*>(.*?)</li>', re.DOTALL).findall(ul)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="([^"]+)"')

        if url in str(episodes): continue

        episodes.append(url)

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)"')

        if thumb.startswith('//'): thumb = 'https:' + thumb

        title = scrapertools.find_single_match(match, 'title="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<h2[^>]*>(.*?)</h2>')
        if not title: title = scrapertools.find_single_match(match, '<strong[^>]*>(.*?)</strong>')

        title = scrapertools.htmlclean(title)

        show, season, episode = extraer_show(title)

        if show == '' or season == '' or episode == '': 
            if title != '': logger.debug('Serie/Temporada/Episodio no detectados! %s' % title)
            continue

        if '/serie-en-hd/' in url: show = show + ' HD'

        if '-al-' in url:
            more = scrapertools.find_single_match(match, '<strong style=".*?">.*?-(.*?)</strong>').strip()
            show = show + ' ' + more

        titulo = '%sx%s %s' % (season, episode, show)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, 
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)">Next</a>')
        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', url=next_page, text_color='coral', contentSeason=1000, contentEpisodeNumber=10000 ))

    return sorted(itemlist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))


def extrae_idioma(txt):
    txt = txt.lower()
    if 'latino' in txt: return 'Lat'
    elif 'castellano' in txt: return 'Esp'
    elif 'español' in txt: return 'Esp'
    elif 'subtitulado espa' in txt: return 'Vose'
    elif 'subtitulado' in txt: return 'Vose'
    else: return 'VO'


def findvideos(item):
    logger.info()
    itemlist = []

    headers = {}

    if not 'descargas2020' in item.url:
        item.url = item.url.replace('/descargar/', '/descargar/torrent/')
        headers = {'Referer': item.url}

    data = do_downloadpage(item, item.url, headers = headers)

    ses = 0

    # torrent
    calidad = ''
    idioma = ''

    h1 = scrapertools.find_single_match(data, '<h1[^>]*>(.*?)</h1>')
    h1 = scrapertools.htmlclean(h1.replace('\n', ''))

    datos = scrapertools.find_multiple_matches(h1, '\[([^\]]+)\]')

    if datos:
        calidad = datos[0]

        if len(datos) > 1: idioma = datos[1]

        if idioma: idioma = extrae_idioma(idioma)

        # a veces no es el segundo o tercero []
        if idioma == 'VO' and len(datos) > 2: idioma = extrae_idioma(datos[2])
        if idioma == 'VO' and len(datos) > 3: idioma = extrae_idioma(datos[3])

    if not idioma:
        if '/peliculas-castellano/' in item.url: idioma = extrae_idioma('Castellano')
        elif '/peliculas-latino/' in item.url: idioma = extrae_idioma('Latino')
        elif '/peliculas-subtitulado/' in item.url: idioma = extrae_idioma('Subtitulado')

    tamano = scrapertools.find_single_match(data, '<strong>Size:</strong>([^<]+)</span>').strip()

    url = scrapertools.find_single_match(data, 'window.location.href.*?"(.*?)"')

    if not 'descargas2020' in item.url:
        if url:
            if url.startswith('//'): url = 'https:' + url

        uri = 'https://atomtt.com/to.php'
        tid = scrapertools.find_single_match(url, 'atomtt.com/t_download/([^/]+)/.*?')
        # ~ logger.info("check-NewPct1-Tid: %s" % tid)

        if tid:
            ses += 1

            # ~ HTTP Error 403: Forbidden
            dat2 = do_downloadpage(item, uri, post={'t': tid}, headers={'Referer': item.url})

            if len(dat2) > 1000: dat2 = ''
            # ~ logger.info("check-NewPct1-Dat2: %s" % dat2)

            if not dat2: url = ''
            else:
                url = 'https://atomtt.com%s' % dat2
                # ~ logger.info("check-NewPct1-Url: %s" % url)

                if '/temp/' in url:
                    change1 = scrapertools.find_single_match(url, '.*?/temp/(.*?)/')
                    change2 = scrapertools.find_single_match(url, '.*?/temp/.*?/(.*?)/')
                    changes = '/temp/' + change1 + '/' + change2 + '/'
                    url = url.replace(changes, '/' + change2 + '_-' + change1 + '-')

    if url:
        ses += 1

        if url.startswith('//'): url = 'https:' + url

        if url.startswith('/'): url = ''

        if url:
            if not '.torrent' in url:
                if not url.endswith('/'):
                    if not url.endswith('.torrent'): url = url + '.torrent'

            itemlist.append(Item(channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', ref = item.url,
                                                      language = idioma, quality = calidad, other = tamano ))

    # Ver online
    patron = '<div class="box2">(.*?)</div>.*?<div class="box3">(.*?)</div>.*?<div class="box4">(.*?)</div>.*?<div class="box5">.*?'

    if "data-u='" in data:
        if '<div class="box1">' in data:
          patron = '<div class="box1">(.*?)</div>.*?<div class="box2">(.*?)</div>.*?<div class="box4">(.*?)</div>.*?<div class="box5">(.*?)</div>'
        else:
           patron += "data-u='(.*?)'"
    else:
       if 'onClick="popup' in data:
          data = data.replace(',950,550)"', '##')
          if '##' in data: patron += 'onClick="popup.*?links=(.*?)##'
       elif '<div class="box5">' in data:
          patron = '<div class="box2">(.*?)</div>.*?<div class="box3">(.*?)</div>.*?<div class="box4">(.*?)</div>.*?<div class="box5">(.*?)</div>'
       else:
          return itemlist

    try: matches = re.compile(patron, re.DOTALL).findall(data)
    except: return itemlist

    for servidor, idioma, calidad, url in matches:
        ses += 1

        if not 'descargas2020' in item.url:
            servidor = idioma
            idioma = ''

        if url.startswith("<a href='"):
           url = scrapertools.find_single_match(url, "<a href='(.*?)'")
           if not url: continue

        if url.startswith("<a href='javascript:"): continue
        elif url.startswith("javascript:"): continue

        url = url.replace("'", '').strip()

        servidor = servidor.replace('.com', '').replace('.net', '').replace('.org', '').replace('.co', '').replace('.cc', '').strip()
        servidor = servidor.replace('.to', '').replace('.tv', '').replace('.ru', '').replace('.io', '').replace('.eu', '').replace('.ws', '').strip()
        servidor = servertools.corregir_servidor(servidor)

        if not idioma:
            if '/peliculas-castellano/' in item.url: idioma = 'Castellano'
            elif '/peliculas-latino/' in item.url: idioma = 'Latino'
            elif '/peliculas-subtitulado/' in item.url: idioma = 'Subtitulado'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if not servidor == 'directo':
            itemlist.append(Item(channel = item.channel, action = 'play', title = '', url = url, server = servidor,
                                                         language = extrae_idioma(idioma), quality = calidad ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.server == 'torrent':
        if config.get_setting('proxies', item.channel, default=''):
            if PY3:
                from core import requeststools
                data = requeststools.read(item.url, 'newpct1')
            else:
                data = do_downloadpage(item, item.url)

        else:
            if PY3:
                from core import requeststools
                data = requeststools.read(item.url, '')
            else:
                data = do_downloadpage(item, item.url)

        if data:
            try:
               if '<div class="g-recaptcha my-recaptcha-placeholder"' in str(data):
                   return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'
            except:
               pass

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))

    else:
        url = item.url

        if '[]' in item.url:
            return 'Archivo con varias [COLOR cyan]Partes[/COLOR]'

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    post = 'categoryIDR=&categoryID=&idioma=&calidad=&ordenar=Fecha&inon=Descendente&s=%s&pg=%d' % (item.busca_texto, item.busca_pagina)
    data = do_downloadpage(item, item.url, post=post)

    data = data.replace('\\/', '/')

    dominio = item.url.replace('get/result/', '')

    patron = '"torrentID":"([^"]+)","torrentName":"([^"]+)","calidad":"([^"]+)","torrentDateAdded":"([^"]+)","torrentSize":"([^"]+)"'
    patron += ',"imagen":"([^"]+)","guid":"([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    for tid, tname, tcali, tdate, tsize, timg, tguid in matches:
        url = dominio + tguid
        thumb = dominio + timg[1:]

        is_tvshow = '/serie' in url or '/descargar-serie' in url
        if (item.search_type == 'tvshow' and not is_tvshow) or (item.search_type == 'movie' and is_tvshow): continue
        if url in [it.url for it in itemlist]: continue

        title = tname

        idioma = ''
        if 'Castellano]' in title: idioma = 'Esp'

        year = scrapertools.find_single_match(title, '\((\d{4})\)')
        if year: title = title.replace('(%s)' % year, '').strip()
        else: year = '-'

        title = re.sub('(\[[^\]]*\])', '', title).strip()

        # descartar enlaces a temporadas completas
        if re.match('.*?temporada \d+ completa', title, flags=re.IGNORECASE): continue

        titulo = title
        if item.search_type == 'tvshow':
            m = re.match(r"^(.*?) - (Temporada \d+) Capitulo \d*", title)

            if not m: m = re.match(r"^(.*?) - (Temporada \d+)", title)
            if m:
                title = m.group(1)
                titulo = '%s [%s]' % (title, m.group(2))

        if is_tvshow:
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            sufijo = '' if item.search_type != 'all' else 'tvshow'

            itemlist.append(item.clone( action='episodios', url=url, title=titulo, thumbnail=thumb, languages=idioma, qualities=tcali, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))
        else:
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            sufijo = '' if item.search_type != 'all' else 'movie'

            itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, languages=idioma, qualities=tcali, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '"items":30,' in data:
            itemlist.append(item.clone( title='Siguientes ...', action='busqueda', busca_pagina = item.busca_pagina + 1, text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.url == '': item.url = host
        item.url += 'get/result/'

        item.busca_texto = texto.replace(" ", "+")
        item.busca_pagina = 1
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
