# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://doramasqueen.in/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'temporadas/?status=&type=&order=update', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Últimos episodios', action = 'list_all', url = host , group = 'last', search_type = 'tvshow', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por estudio', action = 'estudios', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'temporadas/')

    bloque = scrapertools.find_single_match(data, '> Genre <(.*?)</ul>')

    matches = re.compile('value="(.*?)".*?<label for="genre-.*?">(.*?)</label>').findall(bloque)

    for value, title in matches:
        url = host + 'temporadas/?genre[]=' + value + '&status=&type=&order='

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = 'firebrick' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'temporadas/')

    bloque = scrapertools.find_single_match(data, '> Country <(.*?)</ul>')

    matches = re.compile('value="(.*?)".*?<label for="country-.*?">(.*?)</label>').findall(bloque)

    for value, title in matches:
        url = host + 'temporadas/?country[]=' + value + '&status=&type=&order='

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = 'moccasin' ))

    return itemlist


def estudios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'temporadas/')

    bloque = scrapertools.find_single_match(data, '> Studio <(.*?)</ul>')

    matches = re.compile('value="(.*?)".*?<label for="studio-.*?">(.*?)</label>').findall(bloque)

    for value, title in matches:
        url = host + 'temporadas/?studio[]=' + value + '&status=&type=&order='

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = 'tan' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'temporadas/')

    bloque = scrapertools.find_single_match(data, '> Network <(.*?)</ul>')

    matches = re.compile('value="(.*?)".*?<label for="network-.*?">(.*?)</label>').findall(bloque)

    for value, title in matches:
        url = host + 'temporadas/?network[]=' + value + '&status=&type=&order='

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = 'moccasin' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if letra == '#': letra = '0-9'

        url = host + 'a-z-dorama-list/?show=' + letra.lower()

        itemlist.append(item.clone( title = letra, action = 'list_all', url = url, text_color='firebrick' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    if item.group == 'last':
        bloque = scrapertools.find_single_match(data, '>Actualmente(.*?)</ul>')

        matches = scrapertools.find_multiple_matches(data, '<li>(.*?)</li>')
    else:
        matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"').strip()

        if not url or not title: continue

        title = title.replace('&#8217;s', "'s").replace('&#8217;t', "'t").replace('&#038;', '&').replace('&#8211;', '').strip()
        title = title.replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').replace('&amp;', '').replace('amp;', '').replace('quot;', '').strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(title, '(\d{4})')
        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        SerieName = title.strip()

        if item.group == 'last':
            if "Capitulo" in SerieName: SerieName = SerieName.split("Capitulo")[0]

            season = scrapertools.find_single_match(url, '-temporada-(.*?)$')
            if not season: season = 1

            episode = scrapertools.find_single_match(url, '-capitulo-(.*?)/')
            if not episode: episode = 1

            title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

            title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]')

            if '-capitulo-' in url:
                itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentSerieName=SerieName,
                                            contentType = 'episode', contentSeason = season, contentEpisodeNumber=episode, infoLabels={'year': year} ))
            else:
                itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                            contentSerieName=SerieName, contentType='tvshow', infoLabels={'year': year} ))

        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentSerieName=SerieName, contentType='tvshow', infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="hpage">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="hpage">.*?<a href="(.*?)"')

            if next_page:
                if '?page=' in next_page:
                    next_page = host + 'temporadas/' + next_page

                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

        elif '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?class="page-numbers current">.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

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

    bloque = scrapertools.find_single_match(data, '<div class="eplister">(.*?)</ul>')

    matches = re.compile('<li(.*?)</li>', re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('DoramasQueenIn', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramasQueenIn', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasQueenIn', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasQueenIn', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasQueenIn', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramasQueenIn', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    title_ser = item.contentSerieName.replace("’s", 's').replace("'t", 't').replace(':', '').replace("'t", 't').replace(' ', '-').lower()

    title_ser = title_ser.replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').replace('&amp;', '').replace('amp;', '').replace('quot;', '').strip()

    if '-(' in title_ser: title_ser = scrapertools.find_single_match(title_ser, '(.*?)-(')
    if '.' in title_ser: title_ser = title_ser.replace('.', '-')
    if ',' in title_ser: title_ser = title_ser.replace(',', '')

    ok_title_ser = False

    for match in matches[item.page * item.perpage:]:
        if '>Muy Pronto<' in match: continue

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not title_ser in url: continue

        ok_title_ser = True

        title = scrapertools.find_single_match(match, 'div class="epl-title">(.*?)"')

        title = title.strip()

        episode = scrapertools.find_single_match(url, '-capitulo-(.*?)/')
        if not episode: episode = 1

        title = str(item.contentSeason) + 'x' + str(episode) + ' ' + item.contentSerieName

        if '-' in episode: episode = episode.replace('-', '').strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = title, orden = 1,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios",
                                        page=item.page + 1, perpage = item.perpage, text_color='coral', orden = '10000' ))

    if not itemlist:
        if not ok_title_ser:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin Ningún Episodio[/B][/COLOR]')
            return

    return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    ses = 0

    # ~ Embeds
    matches = scrapertools.find_multiple_matches(data, 'data-embed="(.*?)"')

    for url in matches:
        url = url.strip()

        if url:
            ses += 1

            if url.startswith("//"): url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            # ~ intentar Voe
            if servidor == 'directo':
                new_url = scrapertools.find_single_match(url, '.com/(.*?)$')

                if new_url:
                    url = 'https://voe.sx/' + new_url
                    servidor = 'voe'

            if servidor == 'directo':
                if not 'http' in url: continue

                if not config.get_setting('developer_mode', default=False): continue
                other = url.split("/")[2]
                other = other.replace('https:', '').strip()

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Vose', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
