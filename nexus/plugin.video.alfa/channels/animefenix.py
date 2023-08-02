# -*- coding: utf-8 -*-
# -*- Channel AnimeFenix -*-
# -*- Created for Alfa Addon -*-
# -*- By the Alfa Development Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido

import re

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from channels import filtertools, autoplay
from modules import renumbertools
from core import tmdb


IDIOMAS = {'vose': 'VOSE'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['directo', 'verystream', 'openload',  'streamango', 'uploadmp4', 'fembed']
forced_proxy_opt = 'ProxyCF'

canonical = {
             'channel': 'animefenix', 
             'host': config.get_setting("current_host", 'animefenix', default=''), 
             'host_alt': ["https://animefenix.tv/"], 
             'host_black_list': ["https://www.animefenix.tv/", "https://www.animefenix.com/"], 
             'pattern': '<div\s*class="navbar-start">\s*<a\s*class="navbar-item"\s*href="([^"]+)"', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF_stat': False, 'session_verify': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(
        Item(
            action = "new_episodes",
            channel = item.channel,
            thumbnail = get_thumb("channels_anime.png"),
            title = "Nuevos Capítulos",
            url = host + 'nino'
        )
    )

    itemlist.append(
        Item(
            action = "list_all",
            channel = item.channel,
            thumbnail = get_thumb("now_playing.png"),
            title = "Emision",
            url = host + 'animes?type%5B%5D=tv&estado%5B%5D=1',
        )
    )

    itemlist.append(
        Item(
            action = "list_all",
            channel = item.channel,
            thumbnail = get_thumb("channels_anime.png"),
            title = "Recientes",
            url = host
        )
    )

    itemlist.append(
        Item(
            action = "list_all",
            channel = item.channel,
            thumbnail = get_thumb("channels_anime.png"),
            title = "Todas",
            url = '%sanimes?order=title' % host
        )
    )

    itemlist.append(
        Item(
            action = "search",
            channel = item.channel,
            thumbnail = get_thumb('search.png'),
            title = "Buscar",
            url = host + 'animes?q='
        )
    )

    autoplay.show_option(item.channel, itemlist)

    itemlist = renumbertools.show_option(item.channel, itemlist)

    return itemlist


def get_source(url, json=False, unescape=False, **opt):
    logger.info()

    opt['canonical'] = canonical
    opt['ignore_response_code'] = True
    opt['timeout'] = 10
    data = httptools.downloadpage(url, **opt)
    data.data = scrapertools.unescape(data.data) if unescape else data.data

    if json:
        data = data.json
    elif opt.get('soup', False):
        data = data.soup
    else:
        data = data.data

    return data


def list_all(item):
    logger.info()

    itemlist = list()

    soup = get_source(item.url, soup=True)
    try:
        matches = soup.find("div", class_="list-series").find_all("article", class_="serie-card")
    except:
        matches = []

    for elem in matches:
        url = elem.a["href"]
        title = elem.a["title"]
        title = re.sub('(?i)\s*season\s*|\s*part\s*|\s*\d+(?:st|nd|rd|th)\s*|\s*\d{1,3}$', '', title)
        thumb = elem.img["src"]
        context = renumbertools.context(item)
        context2 = autoplay.context
        context.extend(context2)
        itemlist.append(
            Item(
                action = 'episodios',
                channel = item.channel,
                contentSerieName = title,
                context = context,
                thumbnail = thumb,
                title = title,
                url = url,
                contentType='tvshow'
            )
        )

    tmdb.set_infoLabels_itemlist(itemlist, True)

    next_page = soup.find('div', class_='pagination')

    if next_page and len(next_page.find_all('li')) > 0:
        try:
            next_page = next_page.find_all('li')[-1]
            next_url = next_page.find('a')['href'] if next_page.find('a') and next_page.find('a').get('href') else ''
            base_url = scrapertools.find_single_match(item.url, '(.+?)\?')

            if next_url:
                itemlist.append(
                    Item(
                        action = item.action,
                        channel = item.channel,
                        thumbnail = thumb,
                        title = 'Siguiente página >',
                        url = "%s%s" % (base_url, next_url) if not base_url in next_url else next_url
                    )
                )
        except:
            import traceback
            logger.error(traceback.format_exc())

    return itemlist


def new_episodes(item):
    logger.info()

    itemlist = list()

    soup = get_source(item.url, soup=True).find("div", class_="capitulos-grid")

    try:
        for elem in soup.find_all("div", "overarchingdiv"):

            title = elem.img["alt"]
            thumb = elem.img["src"]
            url = elem.a["href"]

            season = 1
            episode = 1
            if scrapertools.find_single_match(title, '(?i)\s*\d{1,2}(?:st|nd|rd|th)\s*season\s+\d{1,3}\s*$'):
                season, episode = scrapertools.find_single_match(title, '(?i)\s*(\d{1,2})(?:st|nd|rd|th)\s*season\s+(\d{1,3})\s*$')
                name = re.sub('(?i)\s*\d{1,2}(?:st|nd|rd|th)\s*season\s+\d{1,3}\s*$', '', title)
                title = '%s %sx%s' % (name, season, str(episode).zfill(2))
            elif scrapertools.find_single_match(title, '(?i)season\s+\d{1,2}\s*$'):
                season = scrapertools.find_single_match(title, '(?i)season\s+(\d{1,2})\s*$')
                name = re.sub('(?i)season\s+\d{1,2}\s*$', '', title)
                title = '%s %sx%s' % (name, season, str(episode).zfill(2))
            elif scrapertools.find_single_match(title, '\s+\d{1,2}\s+\d+\s*$'):
                season, episode = scrapertools.find_single_match(title, '\s+(\d{1,2})\s+(\d+)\s*$')
                name = re.sub('\s+\d{1,2}\s+\d+\s*$', '', title)
                title = '%s %sx%s' % (name, season, str(episode).zfill(2))
            elif scrapertools.find_single_match(title, '\s+\d{1,3}\s*$'):
                episode = scrapertools.find_single_match(title, '\s+(\d{1,3})\s*$')
                name = re.sub('\s+\d{1,3}\s*$', '', title)
                title = '%s %sx%s' % (name, season, str(episode).zfill(2))
            else:
                # name = elem.find("div", class_="overtitle").text
                name = title
            try:
                season = int(season)
                episode = int(episode)
            except:
                season = 1
                episode = 1
            
            if scrapertools.find_single_match(name, '\s*\(?\[?\d{4}\]?\)?\s*'):
                name = re.sub('\s*\(?\[?\d{4}\]?\)?\s*', '', name)
                title = re.sub('\s*\(?\[?\d{4}\]?\)?\s*', '', title)
            name = re.sub('(?i)\s*season\s*|\s*part\s*|\s*\d+(?:st|nd|rd|th)\s*', '', name)
            title = re.sub('(?i)\s*season\s*|\s*part\s*|\s*\d+(?:st|nd|rd|th)\s*', '', name)

            itemlist.append(Item(channel=item.channel, title=title, thumbnail=thumb, url=url, action="findvideos",
                                 contentSerieName=name, contentType='episode', contentSeason=season, contentEpisodeNumber=episode))
    except:
        pass
    
    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist


def episodios(item):
    logger.info()

    item.videolibrary = True if item.extra else False
    itemlist = episodesxseason(item)
    
    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = list()

    soup = get_source(item.url, soup=True).find("div", class_="column is-12")

    infoLabels = item.infoLabels

    try:
        for elem in soup.find_all("li"):
            url = elem.a["href"]
            try:
                if scrapertools.find_single_match(elem.a.text, "(?i)\s*(?:Part|Season)\s*(\d+)"):
                    sea_num = int(scrapertools.find_single_match(elem.a.text, "(?i)\s*(?:Part|Season)\s*(\d+)"))
                elif scrapertools.find_single_match(elem.a.text, "(?i)\s*\d{1,2}(?:st|nd|rd|th)\s*season"):
                    sea_num = int(scrapertools.find_single_match(elem.a.text, "(?i)\s*(\d{1,2})(?:st|nd|rd|th)\s*season"))
                elif scrapertools.find_single_match(elem.a.text, "(?i)\s*(\d{1,3})\s+Episodio\s+\d{1,3}"):
                    sea_num = int(scrapertools.find_single_match(elem.a.text, "(?i)\s*(\d{1,3})\s+Episodio\s+\d{1,3}"))
                else:
                    sea_num = 1
            except:
                sea_num = 1
            try:
                epi_num = int(scrapertools.find_single_match(elem.span.text, "(\d+)"))
            except:
                epi_num = 1
            infoLabels['season'] = sea_num or 1
            infoLabels['episode'] = epi_num
            title = '%sx%s - Episodio %s' % (sea_num, epi_num, epi_num)
            
            itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos', 
                                 infoLabels=infoLabels, contentType='episode'))
    except:
        pass

    tmdb.set_infoLabels_itemlist(itemlist, True)

    itemlist = itemlist[::-1]

    if config.get_videolibrary_support() and len(itemlist) > 0 and not item.videolibrary:
        itemlist.append(
            Item(
                action = "add_serie_to_library",
                channel = item.channel,
                contentSerieName = item.contentSerieName,
                extra = 'episodios',
                text_color = "yellow",
                title = 'Añadir esta serie a la videoteca',
                url = item.url
            )
        )

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    servers = {"6": "https://www.yourupload.com/embed/%s", "15": "https://mega.nz/embed/%s",
               "21": "https://www.burstcloud.co/embed/%s", "12": "https://ok.ru/videoembed/%s",
               "17": "https://videobin.co/embed-%s.html", "9": host + "stream/amz.php?v=%s",
               "11": host +"stream/amz.php?v=%s", "2": "https://www.fembed.com/v/%s",
               "3": "https://www.mp4upload.com/embed-%s.html", "4": "https://sendvid.com/embed/%s",
               "19": "https://videa.hu/player?v=%s", "23": "https://sbthe.com/e/%s"}

    try:
        soup = get_source(item.url, soup=True, unescape=True)

        pl = soup.find("div", class_="player-container")

        script = pl.find("script").text
        urls = scrapertools.find_multiple_matches(script, "src='([^']+)'")

        for url in urls:

            srv_id, v_id = scrapertools.find_single_match(url, "player=(\d+)&amp;code=([^&]+)")

            if urllib.unquote(v_id).startswith("/"):
                v_id = v_id[1:]

            if 'fireload' in v_id:
                url = v_id
                if not url.startswith('http'):
                    url = 'https://' + url
            elif srv_id not in servers:
                srv_data = get_source(url, referer=item.url)
                url = host.rstrip('/') + scrapertools.find_single_match(srv_data, 'playerContainer.innerHTML .*?src="([^"]+)"')
            else:
                srv = servers.get(srv_id, "directo")
                if srv != "directo":
                    url = srv % v_id

            if "/stream/" in url:
                data = get_source(url, referer=item.url)
                url = scrapertools.find_single_match(data, '"file":"([^"]+)"').replace('\\/', '/').replace('/stream/fl.php?v=', '')

            if not url or url == 'https://':
                continue
            url = urllib.unquote(url)
            
            itemlist.append(
                Item(
                    action = 'play',
                    channel = item.channel,
                    infoLabels = item.infoLabels,
                    language = IDIOMAS['vose'],
                    title = '%s',
                    url = url
                )
            )

        itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

        # Requerido para FilterTools
        itemlist = filtertools.get_links(itemlist, item, list_language)

        # Requerido para AutoPlay
        autoplay.start(itemlist, item)

        return itemlist
    except:
        import traceback
        logger.info(traceback.format_exc())
        return [Item(title='Cambio de estructura. Reportar en el foro')]


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    if texto != '':
        try:
            return list_all(item)
        except:
            import traceback
            logger.error(traceback.format_exc())
            return []


def newest(categoria):
    itemlist = []
    item = Item()
    if categoria == 'anime':
        item.url=host
        itemlist = new_episodes(item)
    return itemlist
