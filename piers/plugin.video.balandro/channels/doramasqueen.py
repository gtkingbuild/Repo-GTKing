# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://doramasqueen.com/'


perpage = 24


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'doramas.php', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Últimos episodios', action = 'list_all', url = host + 'ultimoscapitulos.php', group = 'last', search_type = 'tvshow', text_color='cyan' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, '<div class="col-xl-2(.*?)</div></div>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h5 class="card-title">(.*?)</h5>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        title_serie = re.sub(r'(\d{4})$', '', title).strip()

        if "Capitulo" in title_serie: SerieName = title_serie.split("Capitulo")[0]
        else: SerieName = title_serie

        SerieName = SerieName.strip()

        if item.group == 'last':
            season = scrapertools.find_single_match(url, '-temporada-(.*?)$')

            if not season: season = 1

            episode = scrapertools.find_single_match(url, '-capitulo-(.*?)-temporada-')

            if not episode: episode = 1

            SerieName = re.sub(r'(\d{4})$', '', SerieName)

            SerieName = SerieName.strip()

            title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

            title = title + ' [COLOR goldenrod]Epis.[/COLOR] ' + episode

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentSerieName=SerieName,
                                        contentType = 'episode', contentSeason = season, contentEpisodeNumber=episode, infoLabels={'year': '-'} ))
        else:
            title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentSerieName=SerieName, contentType='tvshow', infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, pagina = item.pagina, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            if '<nav aria-label="Page navigation">' in data:
               next_page = scrapertools.find_single_match(data, '<nav aria-label="Page navigation">.*?<li class="page-item active">.*?</a>.*?href="(.*?)"')

               if next_page:
                   if '?pagina=' in next_page:
                       if item.group == 'last': next_page = host + 'ultimoscapitulos.php' + next_page
                       else: next_page = host + 'doramas.php' + next_page

                       itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', page=0, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if config.get_setting('channels_seasons', default=True):
        title = 'Temporadas'

        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]' + title + '[/COLOR]')

    item.page = 0
    item.contentType = 'season'
    item.contentSeason = 1
    itemlist = episodios(item)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, '<div class="list-group">(.*?)</div></div>')

    matches = re.compile('<a href="(.*?)".*?">(.*?)</a>', re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramasQueen', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, title in matches[item.page * item.perpage:]:
        season = scrapertools.find_single_match(url, '-temporada-(.*?)$')

        episode = scrapertools.find_single_match(url, '-capitulo-(.*?)-temporada-')

        title = str(season) + 'x' + str(episode) + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = title, orden = 1,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber=episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage, text_color='coral', orden = '10000' ))

    return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, '"iframevideo".*?src = "(.*?)"')

    ses = 0

    for url in matches:
        if not url: continue

        ses +=1

        if '/youtu.' in url:
            ses = ses - 1
            continue

        lang = 'Vose'
        if '-dub-' in item.url: lang = 'Lat'

        url = url.replace('\\/', '/')

        if url.startswith('//'): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        elif servidor == 'directo': other = '?'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def list_search(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url, post = {'query': item.texto})

    matches = scrapertools.find_multiple_matches(data, "href='(.*?)'.*?src='(.*?)'.*? /> (.*?)</p>")

    for url, thumb, title in matches:
        if not url or not title: continue

        title_serie = re.sub(r'(\d{4})$', '', title).strip()

        SerieName = title_serie

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                    contentSerieName=SerieName, contentType='tvshow', infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'app/buscar.php'
        item.texto = texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
