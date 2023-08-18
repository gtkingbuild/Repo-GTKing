# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://asianhdplay.pro/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color='firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Recientes', action = 'list_all', url = host + 'recently-added-raw', search_type = 'tvshow', text_color = 'olive' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'ongoing-series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'popular', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'kshow', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'movies', search_type = 'movie', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h3(.*?)<div class="clr"></div>')

    matches = re.compile('<li class="video-block ">(.*?)</li>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        new_title = scrapertools.find_single_match(match, '<div class="name">(.*?)</div>').strip()
        if new_title: title = new_title

        year = '-'

        if " (" in title:
           year = scrapertools.find_single_match(title, '(\d{4})')
           if year: title = title.replace('(' + year + ')', '').strip()

        url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        if item.search_type == 'movie':
            if "Episode" in title: PeliName = title.split("Episode")[0]
            elif 'Movie' in title: PeliName = title.split("Movie")[0]
            else: PeliName = title

            PeliName = PeliName.strip()

            title = title.replace('Episode', '[COLOR goldenrod]Episode[/COLOR]')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=PeliName, infoLabels={'year': year} ))
        else:
            SerieName = title.replace('(Dub)' , '')

            if "Episode" in SerieName: SerieName = SerieName.split("Episode")[0]
            elif "Season" in SerieName: SerieName = SerieName.split("Season")[0]
            elif " S1 " in SerieName: SerieName = SerieName.split(" S1 ")[0]
            elif " S2 " in SerieName: SerieName = SerieName.split(" S2 ")[0]
            elif " S3 " in SerieName: SerieName = SerieName.split(" S3 ")[0]

            SerieName = SerieName.strip()

            if "-s1-" in url: season = 1
            elif "-s2-" in url: season = 2
            elif "-s3-" in url: season = 3
            else:
               season = scrapertools.find_single_match(url, '-season-(.*?)-episode-')
               if not season: season = 1

            epis = scrapertools.find_single_match(url, '-episode-(.*?)$')
            if not epis: epis = 1

            title = title.replace('Episode', '[COLOR goldenrod]Episode[/COLOR]')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                        contentType = 'episode', contentSerieName = SerieName, contentSeason = season, contentEpisodeNumber = epis, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<ul class='pagination'" in data:
            next_url = scrapertools.find_single_match(data, "<ul class='pagination'.*?class=active>.*?</li>.*?href='(.*?)'")

            if next_url:
                next_url = host[:-1] + next_url

                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    link = scrapertools.find_single_match(data, '<iframe src="(.*?)"')

    if not link: return itemlist

    if not link.startswith("http"): link = "https:" + link

    data = do_downloadpage(link)

    ses = 0

    matches = re.compile('<li class="linkserver".*?data-video="(.*?)">(.*?)</li>', re.DOTALL).findall(data)

    for url, srv in matches:
        ses += 1

        srv = srv.lower()

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue

        elif 'jetload.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'directo': other = srv

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vose', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search.html?keyword=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

