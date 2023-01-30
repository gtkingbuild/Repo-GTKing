# -*- coding: utf-8 -*-


from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.ennovelas.com/'


perpage = 22


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '?op=categories_all', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Nuevos episodios', action = 'last_epis', url = host + 'just_added.html', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'video-post clearfix.*?href="([^"]+).*?url\((.*?)\).*?<p>([^<]+)')

    num_matches = len(matches)

    for url, thumb, title in matches[item.page * perpage:]:
        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                    page = 0,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year': '-'} ))

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
            next_url = scrapertools.find_single_match(data, '<div class="paging">.*?</b>' + "<a href='(.*?)'")

            if next_url:
                next_url = next_url.replace('&amp;', '&')

                if 'page=' in next_url:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    patron = "videobox.*?"
    patron += 'href="(.*?)".*?'
    patron += "url.*?'(.*?)'.*?"
    patron += 'center">(.*?)</a>'

    matches = scrapertools.find_multiple_matches(data, patron)

    num_matches = len(matches)

    for url, thumb, title in matches[item.page * perpage:]:
        season = scrapertools.find_single_match(title, ' (\d+) Temporada')
        if not season: season = 1

        epis = scrapertools.find_single_match(title, 'Capitulo (\d+)$')
        if not epis: epis = 1

        SerieName = title

        if " - " in title: SerieName = title.split(" - ")[0]
        if " Temporada" in title: SerieName = title.split(" Temporada")[0]
        if " Capitulo" in title: SerieName = title.split(" Capitulo")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, infoLabels={'year': '-'},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'last_epis', text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    for pagina in range(1, 15):
        data = do_downloadpage(item.url + '&page=' + str(pagina))

        patron = "videobox.*?url\('(.*?)'\).*?"
        patron += 'href="([^"]+).*?center">([^<]+)'

        matches = scrapertools.find_multiple_matches(data, patron)

        if matches:
            platformtools.dialog_notification('EnrNovelas', '[COLOR cyan]Cargando página ' + str(pagina) + '[/COLOR]')

            for thumb, url, title in matches:
                epis = scrapertools.find_single_match(title, 'Capitulo (\d+)')
                if not epis: epis = 1

                season = scrapertools.find_single_match(title, ' (\d+) Temporada')
                if not season: season = 1

                itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                            contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'src: "(.*?)"')

    for url in matches:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?op=categories_all&name=' + texto.replace(" ", "+")
       return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

