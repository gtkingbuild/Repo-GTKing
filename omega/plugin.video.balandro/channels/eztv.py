# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, os

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://eztvx.to/'


perpage = 25


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_eztv_proxies', default=''):
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
    if config.get_setting('channel_eztv_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('eztv', url, post=post, headers=headers).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='eztv', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'showlist/rating/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Temporadas completas', action='list_all', url = host + 'cat/tv-packs-1/', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    matches = re.compile('<tr name="hover"(.*?)</tr>', re.DOTALL).findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, 'class="thread_link">(.*?)</a>')

        if not url or not title: continue

        title = title.replace('Torrent', '').strip()

        url = host[:-1] + url

        itemlist.append(item.clone( action='temporadas', url=url, title=title, contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<td align="right">.*?<a href="(.*?)"')

            if '/page_' in next_page:
                next_page = host[:-1] + next_page

                itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if not '- Season' in data:
        item.page = 0
        item.contentType = 'season'
        item.contentSeason = 1
        itemlist = episodios(item)
        return itemlist

    matches = scrapertools.find_multiple_matches(data, "- Season(.*?)--")

    for tempo in matches:
        tempo = tempo.strip()

        title = 'Temporada ' + tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = item.url, page = 0, contentType = 'season', contentSeason = int(tempo), text_color = 'tan' ))

    return itemlist    


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    links = re.compile('<td class="forum_thread_post">.*?<a href="(.*?)"', re.DOTALL).findall(data)

    if not '- Season' in data:
        bloque = re.compile('Episodes</h3>(.*?)<h3>', re.DOTALL).findall(data)
    else:
        bloque = re.compile('- Season ' + str(item.contentSeason) + '.*?Episodes</h3>(.*?)<h3>', re.DOTALL).findall(data)

    matches = re.compile('<br/>(.*?)--', re.DOTALL).findall(str(bloque))

    for match in matches:
        match = match.strip()

        season = scrapertools.find_single_match(match, '(.*?)x').strip()

        epis = scrapertools.find_single_match(match, '.*?x(.*?)$').strip()

        if not season or not epis: continue

        titulo = str(season) + 'x' + str(epis) + ' ' + item.contentSerieName

        if len(str(season)) > 1:
           if not len(str(season)) > 2: _s = '-s' + str(season)
           else: _s = '-s00' + str(season)
        else: _s = '-s0' + str(season)

        if len(str(epis)) > 1:
            if not len(str(epis)) > 2: _e = 'e' + str(epis)
            else: _e = 'e00' + str(epis)
        else: _e = 'e0' + str(epis)

        season_episode = _s + _e + '-'

        url = ''

        for link in links:
            if not season_episode in link: continue

            url = host[:-1] + link
            break

        if url:
            itemlist.append(item.clone( action='findvideos', url=url, title=titulo,
                                        contentSerieName = item.contentSerieName, contentType = 'episode',
                                        contentSeason = season, contentEpisodeNumber = epis, infoLabels={'year': ''} ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Download Links<(.*?)</div></div>')

    matches = re.compile('<a href="(.*?)"', re.DOTALL).findall(bloque)

    for match in matches:
        url = match

        if url.endswith('.torrent'): pass
        elif 'magnet' in url: pass
        else: continue

        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='torrent', language='Vo'))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if config.get_setting('proxies', item.channel, default=''):
        if PY3:
            from core import requeststools
            data = requeststools.read(item.url, 'eztv')
        else:
            data = do_downloadpage(item.url)

        if data:
            try:
               if 'Página no encontrada</title>' in str(data):
                   platformtools.dialog_ok('eztv', '[COLOR yellow]Archivo no encontrado[/COLOR]')
                   return itemlist
            except:
               pass

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))
    else:
        itemlist.append(item.clone( url = item.url, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'search/' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []