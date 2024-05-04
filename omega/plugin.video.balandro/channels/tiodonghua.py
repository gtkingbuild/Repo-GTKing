# -*- coding: utf-8 -*-

import re, base64


from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://anime.tiodonghua.com/'


def do_downloadpage(url, post=None, headers=None):
    if not headers: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_anime', default=False): return

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'anime/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host, group = 'last_epis', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Generos<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?title=.*?" >(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if letra == '#': url = host + '/a-z/?show=0-9'
        else: url = host + '/a-z/?show=' + letra

        itemlist.append(item.clone( action = 'list_all', title = letra, url = url, text_color = 'springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if item.group == 'last_epis':
        if '>Hot Series Update<' in data: bloque = scrapertools.find_single_match(data, '>Hot Series Update<(.*?)>Recommendation<')
        else: bloque = scrapertools.find_single_match(data, '(.*?)>Recommendation<')
    else: bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        title = title.replace('&#8211;', '').replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').strip()

        SerieName = title

        if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
        if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]
        if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]

        SerieName = SerieName.strip()

        if ' 2nd ' in match: season = 2
        elif ' 3rd ' in match: season = 3
        elif ' 4th ' in match: season = 4
        elif ' 5th ' in match: season = 5
        elif ' 6th ' in match: season = 5
        else: season = 1

        if item.group == 'last_epis':
            episode = scrapertools.find_single_match(match, '<span class="epx">(.*?)</span>')

            episode = episode.replace('Ep', '').strip()

            epis = episode
            if not epis: epis = 1

            try:
                if len(str(epis)) > 1:
                    nseason = epis[0]
                    nepis = epis[1:len(str(epis))]

                    season = nseason
                    epis = nepis
            except:
                pass

            titulo = str(season) + 'x' + str(epis) + ' ' + title

            SerieName = SerieName.replace(episode, '').strip()

            itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, infoLabels={'year': '-'},
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis))

        else:
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
                next_page = host + 'anime/' + next_page

                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    epis = scrapertools.find_multiple_matches(data, '<li data-index=".*?<a href="(.*?)".*?<div class="epl-num">(.*?)</div>.*?<div class="epl-title">(.*?)</div>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(epis)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, epi, title in epis[item.page * item.perpage:]:
        titulo = '%sx%s - %s' % (str(item.contentSeason), epi, title)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epi ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(epis) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


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

        url = scrapertools.find_single_match(video,'<iframe src="(.*?)"')

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Vose', other = other ))

    # ~ Download
    matches = scrapertools.find_multiple_matches(data, '<iframe src="(.*?)"')

    for url in matches:
        ses += 1

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = 'D'
        if servidor == 'various': other = servertools.corregir_other(url) + ' D'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Vose', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    servidor = item.server

    url = item.url

    if 'https://v.tioanime.com/' in url: return itemlist

    servidor = servertools.get_server_from_url(url)
    servidor = servertools.corregir_servidor(servidor)

    url = servertools.normalize_url(servidor, url)

    itemlist.append(item.clone(url = url, server = servidor))

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
