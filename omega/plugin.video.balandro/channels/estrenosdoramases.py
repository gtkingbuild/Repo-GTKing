# -*- coding: utf-8 -*-

import re


from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://estrenosdoramas.es/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color='firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'temporadas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    matches = scrapertools.find_multiple_matches(data, 'id="genre-.*?value="(.*?)".*?<label.*?">(.*?)</label>')

    for id, title in matches:
        url = host + 'temporadas/?genre[]=' + id + '&status=&type=&order='

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='firebrick' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if letra == '#': letra = '0-9'

        url = host + 'a-z-dorama-list/?show=' + letra

        itemlist.append(item.clone( title = letra, action = 'list_all', url = url, text_color='firebrick' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#8217;s', "'s").replace('&#8217;t', "'t").replace('&#8211;', '').strip()
        title = title.replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').replace('&amp;', '').replace('amp;', '').replace('quot;', '').strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(title, '(\d{4})')
        if not year: year = '-'
        else: title = title.replace('(' + year + ')', '').strip()

        SerieName = title

        if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
        if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]
        if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb, infoLabels={'year': '-'},
                                    contentSerieName = SerieName, contentType = 'tvshow', contentSeason = 1 ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if 'Previous' in data:
            next_page = scrapertools.find_single_match(data,'<div class="hpage">.*?</a>.*?href="(.*?)"')
        else:
            next_page = scrapertools.find_single_match(data,'<div class="hpage">.*?href="(.*?)"')

        if next_page:
            if '?page=' in next_page:
                next_page = host + 'temporadas/' + next_page

                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'Doramasmp4<(.*?)</ul>')

    matches = re.compile('<li>(.*?)</li>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '</i>(.*?)</span>').strip()

        if not url or not title: continue

        title = title.replace('&#8217;s', "'s").replace('&#8217;t', "'t").replace('&#8211;', '').strip()
        title = title.replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').replace('&amp;', '').replace('amp;', '').replace('quot;', '').strip()

        year = scrapertools.find_single_match(title, '(\d{4})')
        if not year: year = '-'
        else: title = title.replace('(' + year + ')', '').strip()

        season = 1

        epis = scrapertools.find_single_match(match, '<span class="r">(.*?)</span>').strip()

        epis = epis.replace('Capitulo', '').strip()
        if not epis: epis = 1

        title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        titulo = str(season) + 'x' + str(epis) + ' ' + title

        if '-capitulo-' in url:
            itemlist.append(item.clone( action='findvideos', url=url, title=titulo,
                                        contentType='episode', contentSerieName=title, contentSeason=season, contentEpisodeNumber=epis, infoLabels={'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url=url, title=titulo,
                                        contentSerieName=title, contentType='tvshow', contentSeason=season, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul id="myList">(.*?)</ul>')

    epis = scrapertools.find_multiple_matches(bloque, '<li(.*?)</li>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(epis)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('EstrenosDoramasEs', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('EstrenosDoramasEs', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EstrenosDoramasEs', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EstrenosDoramasEs', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EstrenosDoramasEs', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EstrenosDoramasEs', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('EstrenosDoramasEs', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    title_ser = item.contentSerieName.replace("’s", 's').replace("'t", 't').replace(':', '').replace("'t", 't').replace(' ', '-').lower()

    title_ser = title_ser.replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').replace('&amp;', '').replace('amp;', '').replace('quot;', '').strip()

    if '-(' in title_ser: title_ser = scrapertools.find_single_match(title_ser, '(.*?)-(')
    if '.' in title_ser: title_ser = title_ser.replace('.', '-')
    if ',' in title_ser: title_ser = title_ser.replace(',', '')

    ok_title_ser = False

    for match in epis[item.page * item.perpage:]:
        if '>Muy Pronto<' in match: continue

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        epi = scrapertools.find_single_match(match, '<div class="epl-title">(.*?)</div>')

        if not url or not epi: continue

        if not title_ser in url: continue

        ok_title_ser = True

        epi = epi.replace('Capitulo', '').replace('Capítulo', '').replace('capitulo', '').replace('capítulo', '').replace('Episode', '').replace('episode', '').strip()

        titulo = '%sx%s %s' % (str(item.contentSeason), epi, item.contentSerieName)

        if len(epi) == 1: orden = '0' + epi
        else: orden = epi

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, orden = orden,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epi ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(epis) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral', orden = '10000' ))

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
        item.url =  host + "?s=" + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
