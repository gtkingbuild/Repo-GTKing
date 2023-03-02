# -*- coding: utf-8 -*-

import re, string

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://areliux.com/'


perpage = 30


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in string.ascii_uppercase:
        itemlist.append(item.clone (action = "list_alfa", title = letra, url = host, filtro = letra))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = re.compile('<div class="shortstory-in">(.*?)</div></div>', re.DOTALL).findall(data)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for match in matches[desde:hasta]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not url: continue
        elif url == '#': continue

        title = scrapertools.find_single_match(match, 'title="(.*?)"').strip()

        if title.lower() == 'promo': continue
        elif title.lower() == 'proximamente': continue
        elif title == '#': continue

        elif 'class="radius-3"' in match: continue

        if not host in url: url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if '-capitulo-' in url or '/main/' in url:
            season = scrapertools.find_single_match(url, '-temporada-(.*?)-')
            if not season: season = '1'

            epis =  scrapertools.find_single_match(url, '-capitulo-(.*?).')
            if not epis: epis = '1'

            SerieName = title

            if "Capitulo" in title: SerieName = title.split("Capitulo")[0]
            if "Temporada" in title: SerieName = title.split("Temporada")[0]

            SerieName = SerieName.strip()

            if '/main/' in url:
                itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))
            else:
                itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb,
                                            contentSerieName=SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        else:
            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))

    return itemlist


def list_alfa(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = re.compile('<div class="shortstory-in">(.*?)</div></div>', re.DOTALL).findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, 'title="(.*?)"').strip()

        if title.lower() == 'promo': continue
        elif title.lower() == 'proximamente': continue
        elif title == '#': continue

        letra = item.filtro.lower().strip()
        titulo = title.lower().strip()

        try:
            letra_titulo = titulo[0]
            if not letra_titulo == letra: continue
        except:
            continue

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not url: continue
        elif url == '#': continue

        if not host in url: url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if '-capitulo-' in url or '/main/' in url:
            season = scrapertools.find_single_match(url, '-temporada-(.*?)-')
            if not season: season = '1'

            epis =  scrapertools.find_single_match(url, '-capitulo-(.*?).')
            if not epis: epis = '1'

            SerieName = title

            if "Capitulo" in title: SerieName = title.split("Capitulo")[0]
            if "Temporada" in title: SerieName = title.split("Temporada")[0]

            SerieName = SerieName.strip()

            if '/main/' in url:
                itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))
            else:
                itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb,
                                            contentSerieName=SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        else:
            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin Temporadas')
    item.page = 0
    item.dialog = False
    item.contentType = 'season'
    item.contentSeason = 1
    itemlist = episodios(item)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    if not item.url: data = ''
    elif item.url == '#': data = ''
    else:
        data = httptools.downloadpage(item.url).data
        data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, '<div class="shortstoddry-news radius-3">(.*?)</div><div class="clearfix"></div>')

    if bloque:
        matches = scrapertools.find_multiple_matches(bloque, '<div class="col-sm-4 col-xs-12">(.*?)</div></div>')
    else:
        matches = scrapertools.find_multiple_matches(data, '<div class="col-sm-4 col-xs-12">(.*?)</div></div>')

    cargar_todas = False

    tot_pages = 0

    if item.page == 0 and not item.dialog:
        if '<div class="pages-numbers">' in data:
            tot_pages = scrapertools.find_single_match(data, '<div class="pages-numbers">.*?<span class="nav_ext">.*?">(.*?)</a>')
            if not tot_pages:
                blok = scrapertools.find_single_match(data, '<div class="pages-numbers">(.*?)</div></div>')
                lnks = scrapertools.find_multiple_matches(blok, '<a href="(.*?)"')
                tot_pages = (len(lnks) + 1)

        if str(tot_pages) > '1':
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(tot_pages) + '[/B][/COLOR] páginas disponibles, desea cargar Todas las páginas de una sola vez ?'):
                item.perpage = 1000
                cargar_todas = True
                matches_page = []

                i = 1

                sgte_page = scrapertools.find_single_match(data, '<div class="col-lg-1 col-sm-2 col-xs-2 pages-next">.*?<a href="(.*?)"')

                while sgte_page:
                   platformtools.dialog_notification('SeoDiv', '[COLOR cyan]Cargando página ' + str(i) + '[/COLOR]')

                   if not sgte_page: pass
                   elif sgte_page == '#': pass
                   else:
                       data = httptools.downloadpage(sgte_page).data
                       data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

                       bloque_page = scrapertools.find_single_match(data, '<div class="shortstoddry-news radius-3">(.*?)</div><div class="clearfix"></div>')

                       if bloque_page:
                           matches_page = matches_page + scrapertools.find_multiple_matches(bloque_page, '<div class="col-sm-4 col-xs-12">(.*?)</div></div>')
                       else:
                           matches_page = matches_page + scrapertools.find_multiple_matches(data, '<div class="col-sm-4 col-xs-12">(.*?)</div></div>')

                       sgte_page = scrapertools.find_single_match(data, '<div class="col-lg-1 col-sm-2 col-xs-2 pages-next">.*?<a href="(.*?)"')

                   i += 1

                   if i > int(tot_pages):
                       break

                matches = matches + matches_page

    i = 0

    for match in matches[item.page * item.perpage:]:
        title = scrapertools.find_single_match(match, 'title="(.*?)"')
        if 'onyx equinox' in title: title = title.replace('onyx equinox' ,'').strip()

        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        if not '-capitulo-' in url:
            if not '-temporada-' in url: continue

        i += 1

        titulo = title.lower().replace(item.contentSerieName.lower(), '')

        if not 'capitulo' in titulo: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        if thumb.startswith("/"): thumb = host[:-1] + thumb

        episode = str(item.contentSeason) + str(i)

        itemlist.append(item.clone( action='findvideos', url= url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if not cargar_todas:
            if len(matches) > ((item.page + 1) * item.perpage):
                itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))
            else:
                next_page = scrapertools.find_single_match(data, '<div class="col-lg-1 col-sm-2 col-xs-2 pages-next">.*?<a href="(.*?)"')

                if next_page:
                    if not next_page == '#':
                        itemlist.append(item.clone( title="Siguientes ...", action="episodios", url = next_page,
                                                    dialog = True, page = 0, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.findall('<iframe src="(.*?)"', data, flags=re.DOTALL)

    for url in matches:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, language = 'Lat', title = '', url = url )) 

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = re.compile('<div class="shortstory-in">(.*?)</div></div>', re.DOTALL).findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, 'title="(.*?)"').strip()

        if title.lower() == 'promo': continue
        elif title.lower() == 'proximamente': continue
        elif title == '#': continue

        busqueda = item.title_search.lower().strip()
        titulo = title.lower().strip()

        if not busqueda in titulo: continue

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not url: continue
        elif url == '#': continue

        if not host in url: url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if '-capitulo-' in url or '/main/' in url:
            season = scrapertools.find_single_match(url, '-temporada-(.*?)-')
            if not season: season = '1'

            epis =  scrapertools.find_single_match(url, '-capitulo-(.*?).')
            if not epis: epis = '1'

            SerieName = title

            if "Capitulo" in title: SerieName = title.split("Capitulo")[0]
            if "Temporada" in title: SerieName = title.split("Temporada")[0]

            SerieName = SerieName.strip()

            if '/main/' in url:
                itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))
            else:
                itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb,
                                            contentSerieName=SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        else:
            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb,
                                        contentType='tvshow', contentSerieName=title,  infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []

    try:
        item.title_search = texto
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    return itemlist
