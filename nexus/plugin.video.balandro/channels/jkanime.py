# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools, tmdb


host = 'https://jkanime.net/'


perpage = 25


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_last', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos capítulos', action = 'last_epis', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'genero/latino/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'tipo/ova/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'tipo/pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    matches = re.compile(r'<li><a href="([^"]+)".*?">([^<]+)').findall(data)

    for url, title in matches:
        if title == "Latino": continue
        elif title == "Ovas": continue
        elif title == "Peliculas": continue

        itemlist.append(item.clone( action = "list_all", title = title, url = host[:-1] + url))

    return sorted(itemlist, key=lambda x: x.title)


def alfabetico(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    matches = re.compile('li><a class="letra-link" href="([^"]+)".*?">([^<]+)').findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action = "list_all", title = title, url = host[:-1] + url))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<h5.*?href="([^"]+)">([^<]+)<\/a></h5></div>.*?div class="[^"]+"><.*?set[^"]+"[^"]+"([^"]+)"'

    matches = re.compile(patron).findall(data)

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

                itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                            contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year':'-'} ))
            else:
                url = url + 'pelicula/'

                itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                            contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

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
            next_url = scrapertools.find_single_match(data, '<a class="text nav-next".*?href="(.*?)".*?">Resultados')
            if next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(data, '(?is)Últimos Animes agregados</h4>.*?<div class="col-lg-4 col-md-6 col-sm-8 trending_div">')

    matches = scrapertools.find_multiple_matches(data, '(?is)data-setbg="(.+?)".*?<a  href="([^"]+)".*?>(.+?)<')

    num_matches = len(matches)

    for thumb, url, title in matches[item.page * perpage:]:
        SerieName = title

        if 'OVA' in title: SerieName = title.split("OVA")[0]
        if 'Season' in title: SerieName = title.split("Season")[0]
        if 'Movie' in title: SerieName = title.split("Movie")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year':'-'} ))

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

    data = httptools.downloadpage(item.url).data

    patron = '<a href="([^"]+)" class="bloqq">.+?\n.+?\n.+?<img src="([^"]+)".+?title="([^"]+)".+?\n.+?\n.+?\n.+?\n.+?h6>.+?\n.+?(\d+).+?</'

    matches = scrapertools.find_multiple_matches(data, patron)

    num_matches = len(matches)

    for url, thumb, title, episode in matches[item.page * perpage:]:
        SerieName = title

        SerieName = SerieName.strip()

        title = 'cap.{} - {}'.format(episode, title)

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=episode ))

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

    data = httptools.downloadpage(item.url).data

    id_serie = scrapertools.find_single_match(data, 'ajax/pagination_episodes\/(\d+)\/')
    if not id_serie: id_serie = scrapertools.find_single_match(str(data), host + 'ajax/pagination_episodes\(.*?)/')

    if not id_serie:
        title = scrapertools.find_single_match(data, '<h1>(.*?)</h1>')
        itemlist.append(item.clone( action='findvideos', title = title, url = item.url ))
        return itemlist

    try:
       paginas, capitulos = pages_episodes(data)

       if paginas > 1:
           platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR tan]Cargando ' + str(paginas) + ' Páginas[/COLOR]')

       for pag in range(1, paginas + 1):
           pag_nro = str(pag)

           headers = {"Referer": item.url}
           data = httptools.downloadpage(host + 'ajax/pagination_episodes/%s/%s/' % (id_serie, pag_nro), headers=headers).data

           matches = scrapertools.find_multiple_matches(data, '"number"\:"(\d+)","title"\:"([^"]+)"')

           for nro, title in matches:
               title = title.strip()

               title = '1x' + str(nro) + ' ' + title

               url = item.url + nro

               itemlist.append(item.clone( action='findvideos', url = url, title = title,
                                           contentType = 'episode', contentSeason = 1, contentEpisodeNumber=nro ))
    except:
       url = host + 'ajax/pagination_episodes/%s/%s/' %(id_serie, str(item.page))
       data = httptools.downloadpage(url).data
       jdata = jsontools.load(data)

       for match in jdata:
           itemlist.append(item.clone( action='findvideos', url = item.url + str(match['number']), title = match['title'],
                                       contentType = 'episode', contentSeason = 1, contentEpisodeNumber=match['number'] ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile(r'video\[\d+\] = \'<iframe.*?src="(.*?)".*?</iframe>', re.DOTALL).findall(data)

    for url in matches:
        if 'jkanime.net/um2.php' in url: url = url.replace('jkanime.net/um2.php', 'jkanime.net/um.php')
        elif '/um2.php' in url: url = url.replace('/um2.php', '/um.php')

        other = ''
        if "/um.php" in url: other = 'um'
        elif "/jk.php" in url: other = 'jk'
        elif "okru" in url: other = 'okru'
        elif "fembed" in url: other = 'fembed'
        elif "mixdrop" in url: other = 'mixdrop'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []


    servidor = item.server

    if servidor == 'directo':
        if not item.url.startswith(host): item.url = host[:-1] + item.url

    url_play = item.url

    if "/um.php" in item.url or "/um2.php" in item.url:
        item.url = item.url.replace('/um2.php', '/um.php')

        data = httptools.downloadpage(item.url).data
        url_play = scrapertools.find_single_match(data, "swarmId: \'([^\']+)\'")

    elif "/jk.php" in item.url:
        data = httptools.downloadpage(item.url).data

        url_play = scrapertools.find_single_match(data, '<source src="(.*?)"')
        if not url_play: url_play = scrapertools.find_single_match(data, "video: {.*?url:.*?'(.*?)'")

        if host in url_play:
            url_play = httptools.downloadpage(url_play, follow_redirects=False, only_headers=True).headers.get("location", "")

    elif "okru" in item.url or "fembed" in item.url or "mixdrop" in item.url:
        data = httptools.downloadpage(item.url).data
        url_play = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)"')

        if url_play:
           if not url_play.startswith("http"): url_play = "https:" + url_play

           url_play = url_play.replace("\\/", "/")

           servidor = servertools.get_server_from_url(url_play)
           servidor = servertools.corregir_servidor(servidor)

           url_play = servertools.normalize_url(servidor, url_play)

    if url_play:
        if not url_play.startswith("http"): url_play = "https:" + url_play

        url_play = url_play.replace("\\/", "/")

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

