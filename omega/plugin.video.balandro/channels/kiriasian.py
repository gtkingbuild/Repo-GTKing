# -*- coding: utf-8 -*-

import re, base64


from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://kissasian.com.mx/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://kiriasian.com/', 'https://kissasians.bar/', 'https://kissasians.vin/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not headers: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color='firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos doramas', action = 'list_all', url = host + 'series/?status=&type=&order=update', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por alfabético (A - Z)', action = 'list_all', url = host + 'series/?status=&type=&order=title', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<ul class="genre">(.*?)</ul>')
    if not bloque: bloque = scrapertools.find_single_match(data, '<!-- genres -->(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'value="(.*?)".*?<label.*?">(.*?)</label>')

    for id, title in matches:
        url = host + 'series/?genre[]=' + id

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='firebrick' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<div class="card">(.*?)</div></div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').replace('&amp;', '').replace('amp;', '').replace('quot;', '').strip()

        SerieName = title

        if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
        if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]
        if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]

        SerieName = SerieName.strip()

        if ' 2nd ' in match: season = 2
        elif ' 3rd ' in match: season = 3
        elif ' 4th ' in match: season = 4
        elif ' 5th ' in match: season = 5
        elif ' 6th ' in match: season = 6
        elif ' 7th ' in match: season = 7
        elif ' 8th ' in match: season = 8
        elif ' 9th ' in match: season = 9
        else: season = 1

        title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb, infoLabels={'year': '-'},
                                    contentSerieName = SerieName, contentType = 'tvshow', contentSeason = season  ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if 'Previous' in data:
            next_page = scrapertools.find_single_match(data,'<div class="hpage">.*?</a>.*?href="(.*?)"')
        else:
            next_page = scrapertools.find_single_match(data,'<div class="hpage">.*?href="(.*?)"')

        if next_page:
            if '?page=' in next_page:
                next_page = host + 'series/' + next_page

                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    epis = scrapertools.find_multiple_matches(data, '<li data-index=".*?<a href="(.*?)".*?<div class="epl-num">(.*?)</div>.*?<div class="epl-title">(.*?)</div>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(epis)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('KiriAsian', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('KiriAsian', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('KiriAsian', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('KiriAsian', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('KiriAsian', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('KiriAsian', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('KiriAsian', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, epi, title in epis[item.page * item.perpage:]:
        c_year = scrapertools.find_single_match(title, '(\d{4})')
        if c_year: title = title.replace('(' + c_year + ')', '').strip()

        title = title.replace('Episode', '[COLOR goldenrod]Epis.[/COLOR]').replace('episode', '[COLOR goldenrod]Epis.[/COLOR]')

        titulo = '%sx%s - %s' % (str(item.contentSeason), epi, title)

        if len(epi) == 1: orden = '0' + epi
        else: orden = epi

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, orden = orden,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epi ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(epis) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral', orden = '10000' ))

    return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    ses = 0

    # ~ Enlaces
    bloque = scrapertools.find_single_match(data,'>Select Video Server<(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque, '<option value="(.*?)".*?data-index="(.*?)".*?>(.*?)</option>')

    for d_value, d_index, srv in matches:
        ses += 1

        srv = srv.lower().strip()

        video = base64.b64decode(d_value).decode("utf-8")

        if not video: continue

        url = scrapertools.find_single_match(video,'<iframe.*?src="(.*?)"')
        if not url: url = scrapertools.find_single_match(video,'<IFRAME.*?SRC="(.*?)"')

        if url:
            if '/streaming.php' in url:
                if not 'http' in url: url = 'https:' + url

                data1 = do_downloadpage(url)

                url = scrapertools.find_single_match(data1,'file: "(.*?)"')

                if not url: continue

            elif '/play.php?' in url:
                if not 'http' in url: url = 'https:' + url

                data2 = do_downloadpage(url)

                matches2 = scrapertools.find_multiple_matches(data2, '<li class="linkserver".*?data-video="(.*?)"')

                for vid in matches2:
                    servidor = servertools.get_server_from_url(vid)
                    servidor = servertools.corregir_servidor(servidor)

                    other = ''
                    if servidor == 'various': other = servertools.corregir_other(vid)

                    if '/asianload.' in vid:
                        data3 = do_downloadpage(vid)

                        vid = scrapertools.find_single_match(data3, 'file:"(.*?)"')
                        if not vid: vid = scrapertools.find_single_match(data3, 'file: "(.*?)"')

                        if not vid: continue

                    if servidor == 'directo':
                        if vid.endswith('.m3u8'): other = 'Asianload'
                        else:
                            if not config.get_setting('developer_mode', default=False): continue
                            other = vid.split("/")[2]
                            other = other.replace('https:', '').strip()

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = vid, language = 'Vose', other = other ))

                continue

            if url.startswith("//"): url = 'https:' + url

            if not 'http' in url: ses = ses - 1
            else:
                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                other = ''
                if servidor == 'various': other = servertools.corregir_other(url)

                if '/asianload.' in url:
                   data4 = do_downloadpage(url)

                   url = scrapertools.find_single_match(data4, 'file:"(.*?)"')
                   if not url: url = scrapertools.find_single_match(data4, 'file: "(.*?)"')

                   if not url: continue

                if servidor == 'directo':
                    if url.endswith('.m3u8'): other = 'Asianload'
                    else:
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
