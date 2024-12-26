# -*- coding: utf-8 -*-

import re

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.frozen-layer.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data

def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_anime', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    titulo = 'dorama, anime, ova, manga ...'
    text_color = 'hotpink'

    if item.extra == 'anime':
        titulo = 'anime, ova, manga ...'
        text_color = 'springgreen'
    elif item.extra == 'dorama':
        titulo = 'dorama ...'
        text_color = 'firebrick'

    itemlist.append(item.clone( title = '[B][COLOR yellow]Buscar [/B][/COLOR]' + titulo, action = 'search', search_type = 'tvshow', text_color = text_color ))

    itemlist.append(item.clone( title = 'Catálogo general', action = 'list_all', url = host + '/descargas/detallada/bittorrent', search_type = 'tvshow' ))

    if item.extra == 'all' or item.extra == 'torrents' or item.extra == 'dorama' or item.extra == 'groups':
        itemlist.append(item.clone( title = '[B]Doramas:[/B]', folder=False, text_color='moccasin' ))
        itemlist.append(item.clone( title = ' - Episodios', action = 'list_all', url = host + '/descargas/detallada/bittorrent/dorama', search_type = 'tvshow' ))

    if not config.get_setting('descartar_anime', default=False):
        if item.extra == 'all' or item.extra == 'torrents' or item.extra == 'anime' or item.extra == 'groups':
            itemlist.append(item.clone( title = '[B]Animes:[/B]', folder=False, text_color='moccasin' ))

            itemlist.append(item.clone( title = ' - Catálogo', action = 'list_lst', url = host + '/buscar/anime/tv?&categoria=tv&detallada=true', search_type = 'tvshow' ))

            itemlist.append(item.clone( title = ' - [COLOR cyan]Estrenos[/COLOR]', action = 'list_lst', url = host + '/animes/lista?sort=anio&direction=desc&detallada=true', search_type = 'tvshow' ))

            itemlist.append(item.clone( title = ' - Más valorados', action = 'list_lst', url = host + '/animes/lista?sort=rating&direction=desc&detallada=true', search_type = 'tvshow' ))

            itemlist.append(item.clone( title = ' - [COLOR deepskyblue]Películas[/COLOR]', action = 'list_lst', url = host + '/buscar/anime/pelicula?&categoria=pelicula&detallada=true', search_type = 'movie' ))

            itemlist.append(item.clone( title = ' - [COLOR greenyellow]Episodios[/COLOR]', action = 'list_all', url = host + '/descargas/detallada/bittorrent/anime', search_type = 'tvshow' ))

            itemlist.append(item.clone( title = ' - Por género', action = 'generos', search_type = 'tvshow' ))

            itemlist.append(item.clone( title = ' - Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

            itemlist.append(item.clone( title = '[B]Ovas:[/B]', folder=False, text_color='moccasin' ))
            itemlist.append(item.clone( title = ' - Catálogo', action = 'list_lst', url = host + '/buscar/anime/ova?&categoria=ova&detallada=true', search_type = 'tvshow' ))
            itemlist.append(item.clone( title = ' - Episodios', action = 'list_all', url = host + '/descargas/detallada/bittorrent/anime-OVA', search_type = 'tvshow' ))

            itemlist.append(item.clone( title = '[B]Mangas:[/B]', folder=False, text_color='moccasin' ))
            itemlist.append(item.clone( title = ' - [COLOR deepskyblue]Películas[/COLOR]', action = 'list_all', url = host + '/descargas/detallada/bittorrent/manga', _group = 'mangas', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + '/animes')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h2>Categorias(.*?)</div>')

    matches = re.compile('<a href="(.*?)".*?">(.*?)</a>').findall(bloque)

    for url, title in matches:
        if config.get_setting('descartar_xxx', default=False):
            if title == 'Adulto': continue
            elif title == 'Erótico': continue
            elif title == 'Incesto': continue

        url = host + url + '?&detallada=true'

        itemlist.append(item.clone( title = title.capitalize(), action = 'list_lst', url = url, text_color = 'springgreen' ))

    return sorted(itemlist, key=lambda x: x.title)


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0':
        url = host + '/animes/lista/letra/' + letra + '?&detallada=true'

        itemlist.append(item.clone( title = letra, action = 'list_lst', url = url, text_color = 'springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, "<h1 class='descarga_titulo'>(.*?)</div></div>")

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<a href=".*?">(.*?)</a>').strip()

        if title.startswith("["):
           if '] -' in title: title = scrapertools.find_single_match(title, ' -(.*?)$').strip()

        thumb = scrapertools.find_single_match(match, "<div class='twocol'>.*?" + '<a href="(.*?)"')

        year = scrapertools.find_single_match(title, '(\d{4})')
        if year: title = title.replace('(' + year + ')', '')
        else: year = '-'

        title_ser = title.strip()

        if ' Season Episodio' in title_ser: title_ser = scrapertools.find_single_match(title, '(.*?) Season Episodio')
        elif ' Episodio' in title_ser: title_ser = scrapertools.find_single_match(title, '(.*?) Episodio')
        elif ' Capitulo' in title_ser: title_ser = scrapertools.find_single_match(title, '(.*?) Capitulo')
        elif ' Cap' in title_ser: title_ser = scrapertools.find_single_match(title, '(.*?) Cap')
        elif ' Tomo' in title_ser: title_ser = scrapertools.find_single_match(title, '(.*?) Tomo')
        elif ' OVA' in title_ser: title_ser = scrapertools.find_single_match(title, '(.*?) OVA')
        elif ' COMPLETA' in title_ser: title_ser = scrapertools.find_single_match(title, '(.*?) COMPLETA')

        SerieName = corregir_SerieName(title_ser)

        if not SerieName: SerieName = title.strip()

        url_tor = scrapertools.find_single_match(match, "<div id='descargar_torrent'>.*?href='(.*?)'")

        title = title.replace('Episodio', '[COLOR goldenrod]Epis.[/COLOR]').replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace(' Cap', '[COLOR goldenrod] Epis.[/COLOR]')

        if item._group == 'mangas' or '(Pelicula)' in title or '(pelicula)' in title or 'Pelicula' in title or 'Película' in title:
            PeliName = title.replace('(Pelicula)', '').replace('(pelicula)', '').replace('Pelicula', '').replace('Película', '').strip()

            title = title.replace('(Pelicula)', '[COLOR deepskyblue]Film[/COLOR]').replace('(pelicula)', '[COLOR deepskyblue]Film[/COLOR]').replace('Pelicula', '[COLOR deepskyblue]Film[/COLOR]').replace('Película', '[COLOR deepskyblue]Film[/COLOR]')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType = 'movie', contentTitle = PeliName, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, url_tor = url_tor,
                                        contentExtra='3',
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<span class='next'>" in data:
            next_page = scrapertools.find_single_match(data, "<span class='next'>" + '.*?href="(.*?)"')

            if next_page:
                if 'page=' in next_page:
                    next_page = host + next_page

                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def list_lst(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, "id='descarga_anime_row'>(.*?)</span></div>")

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if url:
            if url == '/buscar/descargas/tv': continue
            elif url == '/buscar/descargas/pelicula': continue

            url = url + '/descargas'

            title = scrapertools.find_single_match(match, 'src=".*?<a href=".*?">(.*?)</a>').strip()

            title = title.replace('&#x27;s', "'s")

            thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

            year = scrapertools.find_single_match(title, '(\d{4})')
            if year: title = title.replace('(' + year + ')', '')
            else: year = '-'

            SerieName = corregir_SerieName(title)

            if not SerieName: SerieName = title.strip()

            if item._group == 'mangas' or '(Pelicula)' in title or '(pelicula)' in title or 'Pelicula' in title or 'Película' in title:
                PeliName = title.replace('(Pelicula)', '').replace('(pelicula)', '').replace('Pelicula', '').replace('Película', '').strip()

                title = title.replace('(Pelicula)', '[COLOR deepskyblue]Film[/COLOR]').replace('(pelicula)', '[COLOR deepskyblue]Film[/COLOR]').replace('Pelicula', '[COLOR deepskyblue]Film[/COLOR]').replace('Película', '[COLOR deepskyblue]Film[/COLOR]')

                itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                            contentType = 'movie', contentTitle = PeliName, infoLabels={'year': year} ))
            else:
                itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                            contentExtra='3',
                                            contentType = 'tvshow', contentSerieName = SerieName, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<span class='next'>" in data:
            next_page = scrapertools.find_single_match(data, "<span class='next'>" + '.*?href="(.*?)"')

            if next_page:
                if 'page=' in next_page:
                    next_page = host + next_page

                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_lst', url = next_page, text_color='coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, "<td class='tit'>(.*?)<td class='detalles'>")

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'class="detalles_link">(.*?)</a>').strip()

        try:
            episode = scrapertools.find_single_match(title, 'Episodio.*?(\d+)$').strip()
            if not episode: episode = scrapertools.find_single_match(title, '- OVA(.*?)$').strip()
        except:
            episode = 0

        if ' al ' in episode: episode = scrapertools.find_single_match(title, "(.*?) al").strip()
        elif 'OVA' in episode:
            episode = scrapertools.find_single_match(title, ".*?-OVA(.*?)$").strip()
            if 'OVA' in episode: episode = scrapertools.find_single_match(title, "OVA(.*?)$").strip()

        if not episode: episode = 0

        titulo = title

        if 'Episodio' in title: titulo = '[COLOR goldenrod]Epis.[/COLOR] ' + str(episode) + ' ' + title.replace('Episodio', '').strip()
        elif '- OVA' in title: titulo = '[COLOR goldenrod]Epis.[/COLOR] ' + str(episode) + ' ' + title.replace('- OVA ', '').strip()
        else: titulo = titulo.replace('Pelicula', '[COLOR deepskyblue]Film[/COLOR]').replace('Película', '[COLOR deepskyblue]Film[/COLOR]')

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<span class='next'>" in data:
            next_page = scrapertools.find_single_match(data, "<span class='next'>" + '.*?href="(.*?)"')

            if next_page:
                if 'page=' in next_page:
                    next_page = host + next_page

                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'episodios', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'Seeds:.*?"stats.*?">(\d+)<.*?Peers:.*?"stats.*?">(\d+)<.*?descargar_torrent.*?href=\'(.*?)\'')

    if not matches:
        if item.url_tor:
            if item.url_tor.endswith('.torrent'): servidor = 'torrent'
            elif item.url_tor.startswith('magnet:?'): servidor = 'torrent'
            else: servidor = ''

            if servidor:
                url = item.url_tor

                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = 'Vose' ))

                return itemlist

    ses = 0

    for seeds, peers, url in matches:
        ses += 1

        if url.endswith('.torrent'): servidor = 'torrent'
        elif url.startswith('magnet:?'): servidor = 'torrent'
        else:
           servidor = servertools.get_server_from_url(url)
           servidor = servertools.corregir_servidor(servidor)

           url = servertools.normalize_url(servidor, url)

           if servidor == 'directo': continue

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = 'Vose' ))

    match = scrapertools.find_single_match(data, 'Magnet Link:.*?<a href="(.*?)"')

    if match:
        if match.endswith('.torrent'): servidor = 'torrent'
        elif match.startswith('magnet:?'): servidor = 'torrent'
        else: servidor = ''

        match = match.replace('&amp;', '&')

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = match, server = servidor, language = 'Vose' ))

    if not itemlist:
        matches = scrapertools.find_multiple_matches(data, 'FlashVars.*?text=https.*?https(.*?)">')
        if not matches:
            matches = scrapertools.find_multiple_matches(data, 'tr class="enlaces">.*?">(.*?)</td>')

            if not matches:
               if 'FlashVars="text=' in data or 'tr class="enlaces">' in data: ses += 1

        if matches:
           for match in matches:
               ses += 1

               if not 'http' in match: url = 'https' + match
               else: url = match

               if url.endswith('.torrent'): servidor = 'torrent'
               elif url.startswith('magnet:?'): servidor = 'torrent'
               else:
                  servidor = servertools.get_server_from_url(url)
                  servidor = servertools.corregir_servidor(servidor)

                  url = servertools.normalize_url(servidor, url)

                  if servidor == 'directo': continue

               itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = 'Vose' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def corregir_SerieName(SerieName):
    logger.info()

    if 'Película' in SerieName: SerieName = SerieName.split("Película")[0]

    if 'Episodio' in SerieName: SerieName = SerieName.split("Episodio")[0]
    if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
    if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]

    if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
    if 'season' in SerieName: SerieName = SerieName.split("season")[0]

    if 'Pack' in SerieName: SerieName = SerieName.split("Pack")[0]

    if '(OVA)' in SerieName: SerieName = SerieName.split("(OVA)")[0]
    if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]
    if 'TV' in SerieName: SerieName = SerieName.split("TV")[0]
    if '(serie de' in SerieName: SerieName = SerieName.split("(serie de")[0]

    if '2nd' in SerieName: SerieName = SerieName.split("2nd")[0]
    if '3rd' in SerieName: SerieName = SerieName.split("3rd")[0]
    if '4th' in SerieName: SerieName = SerieName.split("4th")[0]
    if '5th' in SerieName: SerieName = SerieName.split("5th")[0]
    if '6th' in SerieName: SerieName = SerieName.split("6th")[0]
    if '7th' in SerieName: SerieName = SerieName.split("7th")[0]
    if '8th' in SerieName: SerieName = SerieName.split("8th")[0]
    if '9th' in SerieName: SerieName = SerieName.split("9th")[0]

    SerieName = SerieName.strip()

    return SerieName


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/buscar/' + texto.replace(" ", "+") + '?&detallada=true'
        return list_lst(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
