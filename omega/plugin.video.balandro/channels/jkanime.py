# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools, tmdb


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


host = 'https://jkanime.net/'


perpage = 25


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_jkanime_proxies', default=''):
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
    if config.get_setting('channel_jkanime_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('jkanime', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '/buscar/' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('JKAnime', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('jkanime', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('jkanime', url, post=post, headers=headers, timeout=timeout).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not 'buscar/' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='jkanime', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_jkanime', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_anime', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos capítulos', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_last', url = host, search_type = 'tvshow', text_color = 'olivedrab' ))

    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'tipo/ova/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'tipo/pelicula/', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    matches = re.compile(r'<li><a href="([^"]+)".*?">([^<]+)').findall(data)

    for url, title in matches:
        if title == "Ovas": continue
        elif title == "Peliculas": continue

        itemlist.append(item.clone( action = "list_all", title = title, url = host[:-1] + url, text_color='springgreen' ))

    return sorted(itemlist, key=lambda x: x.title)


def alfabetico(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    matches = re.compile('li><a class="letra-link" href="([^"]+)".*?">([^<]+)').findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action = "list_all", title = title, url = host[:-1] + url, text_color='springgreen' ))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<h5.*?href="([^"]+)">([^<]+)<\/a></h5></div>.*?div class="[^"]+"><.*?set[^"]+"[^"]+"([^"]+)"').findall(data)

    num_matches = len(matches)

    for url, title, thumb in matches[item.page * perpage:]:
        if not title: continue

        if url:
            if item.search_type == "tvshow":
                SerieName = title

                if 'OVA' in title: SerieName = title.split("OVA")[0]
                if 'Season' in title: SerieName = title.split("Season")[0]
                if 'Movie' in title: SerieName = title.split("Movie")[0]

                SerieName = SerieName.strip()

                itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, contentType='tvshow', contentSerieName=SerieName, infoLabels={'year':'-'} ))
            else:
                url = url + 'pelicula/'

                itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

            if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<a class="text nav-next".*?href="(.*?)".*?">Resultados')

            if next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'Últimos Animes agregados</h4>.*?<div class="col-lg-4 col-md-6 col-sm-8 trending_div">')

    matches = scrapertools.find_multiple_matches(bloque, 'data-setbg="(.*?)".*?<a  href="(.*?)">(.*?)</a>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, 'data-setbg="(.*?)".*?<a href="(.*?)">(.*?)</a>')

    num_matches = len(matches)

    for thumb, url, title in matches[item.page * perpage:]:
        SerieName = title

        if 'OVA' in title: SerieName = title.split("OVA")[0]
        if 'Season' in title: SerieName = title.split("Season")[0]
        if 'Movie' in title: SerieName = title.split("Movie")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, contentType='tvshow', contentSerieName=SerieName, infoLabels={'year':'-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_last', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<a href="([^"]+)" class="bloqq">.*?<img src="([^"]+)".*?title="([^"]+)".*?\n.*?\n.*?\n.*?\n.*?h6>.*?\n.*?(\d+).*?</')

    num_matches = len(matches)

    for url, thumb, title, episode in matches[item.page * perpage:]:
        SerieName = title

        SerieName = SerieName.strip()

        title = 'Cap.{} - {}'.format(episode, title)

        title = title.replace('Cap.', '[COLOR goldenrod]Cap.[/COLOR]')

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
                                    contentSerieName=SerieName, contentType='episode', contentSeason=1, contentEpisodeNumber=episode ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'last_epis', text_color = 'coral' ))

    return itemlist


def pages_episodes(data):
    results = scrapertools.find_multiple_matches(data, 'href="#pag([0-9]+)".*?>[0-9]+ - ([0-9]+)')
    if results:
        return int(results[-1][0]), int(results[-1][1])

    return 1, 0


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    id_serie = scrapertools.find_single_match(data, 'ajax/pagination_episodes\/(\d+)\/')
    if not id_serie: id_serie = scrapertools.find_single_match(str(data), host + 'ajax/pagination_episodes\(.*?)/')

    if not id_serie:
        title = scrapertools.find_single_match(data, '<h1>(.*?)</h1>')
        itemlist.append(item.clone( action='findvideos', title = title, url = item.url ))
        return itemlist

    try:
       paginas, capitulos = pages_episodes(data)

       if not config.get_setting('channels_charges', default=True):
           if paginas > 1:
               platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR cyan]Cargando ' + str(paginas) + ' Páginas[/COLOR]')

       for pag in range(1, paginas + 1):
           pag_nro = str(pag)

           headers = {"Referer": item.url}
           data = do_downloadpage(host + 'ajax/pagination_episodes/%s/%s/' % (id_serie, pag_nro), headers=headers)

           matches = scrapertools.find_multiple_matches(data, '"number"\:"(\d+)","title"\:"([^"]+)"')

           for nro, title in matches:
               title = title.strip()

               title = '1x' + str(nro) + ' ' + title

               url = item.url + nro

               itemlist.append(item.clone( action='findvideos', url = url, title = title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=nro ))
    except:
       url = host + 'ajax/pagination_episodes/%s/%s/' %(id_serie, str(item.page))

       data = do_downloadpage(url)

       jdata = jsontools.load(data)

       for match in jdata:
           itemlist.append(item.clone( action='findvideos', url = item.url + str(match['number']), title = match['title'],
                                       contentType = 'episode', contentSeason = 1, contentEpisodeNumber=match['number'] ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile(r'video\[\d+\] = \'<iframe.*?src="(.*?)".*?</iframe>', re.DOTALL).findall(data)

    for url in matches:
        if 'jkanime.net/um2.php' in url: url = url.replace('jkanime.net/um2.php', 'jkanime.net/um.php')
        elif '/um2.php' in url: url = url.replace('/um2.php', '/um.php')

        other = ''
        if "/um.php" in url: other = 'um'
        elif "/jk.php" in url: other = 'jk'
        elif '/jksw.php' in url: other =  'jk'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
           if not url.startswith(host): url = host[:-1] + url

           if "okru" in url: servidor = 'okru'
           if "mixdrop" in url: servidor = 'mixdrop'

        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vose', other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url_play = item.url

    if "/um.php" in item.url or "/um2.php" in item.url:
        item.url = item.url.replace('/um2.php', '/um.php')

        headers = {"Referer": item.url}
        data = do_downloadpage(item.url, headers = headers)

        url_play = scrapertools.find_single_match(data, "swarmId: \'([^\']+)\'")

    elif "/jk.php" in item.url or '/jksw.php' in item.url:
        data = do_downloadpage(item.url)

        url_play = scrapertools.find_single_match(data, '<source src="(.*?)"')
        if not url_play: url_play = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')
        if not url_play: url_play = scrapertools.find_single_match(data, "video: {.*?url:.*?'(.*?)'")

        if host in url_play:
            if not url_play.startswith(host):
                url = httptools.downloadpage(url_play, follow_redirects=False, only_headers=True).headers.get("location", "")
            else:
                if config.get_setting('channel_jkanime_proxies', default=''):
                    url = httptools.downloadpage_proxy('jkanime', url_play, follow_redirects=False, only_headers=True).headers.get("location", "")
                else:
                    url = httptools.downloadpage(url_play, follow_redirects=False, only_headers=True).headers.get("location", "")

            url_play = url

    elif "okru" in item.url or "mixdrop" in item.url:
        data = do_downloadpage(item.url)

        url_play = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)"')

    if url_play:
        if not url_play.startswith("http"): url_play = "https:" + url_play

        url_play = url_play.replace("\\/", "/")

        servidor = servertools.get_server_from_url(url_play)
        servidor = servertools.corregir_servidor(servidor)

        url_play = servertools.normalize_url(servidor, url_play)

        itemlist.append(item.clone(url = url_play, server = servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'buscar/' + texto.replace(" ", "_")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

