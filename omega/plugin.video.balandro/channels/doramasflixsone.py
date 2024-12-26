# -*- coding: utf-8 -*-

import os, re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://doramastv.cam/'


perpage = 30


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://doramaflixs.one/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    resp = httptools.downloadpage(url, post=post, headers=headers)

    if resp.sucess: data = resp.data
    else: data = ''

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_lst', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Episodios', action = 'list_all', url = host, search_type = 'tvshow' ))

    return itemlist


def list_lst(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<option class="level-0".*?value="(.*?)">(.*?)</option>').findall(data)

    num_matches = len(matches)

    for value, title in matches[item.page * perpage:]:
        title = title.replace('&#8211;', '').replace('&amp;', ' & ').replace('&#8217;', "'").strip()

        url = host + '?cat=' + value

        SerieName = title

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        if 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]

        if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
        if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='list_all', url = url, title = title, cat = True,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_lst', text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    title_ser = item.contentSerieName.replace("’s", 's').replace("'t", 't').replace(':', '').replace('.', '-').replace("'t", 't').replace('ñ', 'n').replace(' ', '-').lower()

    title_ser = title_ser.replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').replace('&amp;', '').replace('amp;', '').replace('quot;', '').strip()

    matches = re.compile('<div class="recent-item tie_video">(.*?)</p>').findall(data)

    if not matches:
        bloque = scrapertools.find_single_match(data, 'Search Results for:(.*?)<div id="categories-2"')

        matches = re.compile('<article(.*?)</article>').findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3 class="post-box-title">.*?rel="bookmark">(.*?)</a>').strip()
        if not title: title = scrapertools.find_single_match(match, '<h2 class="post-box-title">.*?">(.*?)</a>').strip()

        if not url or not title: continue

        if not title_ser in url: continue

        title = title.replace('&#8211;', '').replace('&amp;', ' & ').replace('&#8217;', "'").replace('&#038;', '&').strip()

        SerieName = title

        if 'Sub Español' in SerieName: SerieName = SerieName.split("Sub Español")[0]

        if "Episode" in SerieName: SerieName = SerieName.split("Episode")[0]
        if "Episodio" in SerieName: SerieName = SerieName.split("Episodio")[0]

        if "Season" in SerieName: SerieName = SerieName.split("Season")[0]
        if "season" in SerieName: SerieName = SerieName.split("season")[0]
        if " S1 " in SerieName: SerieName = SerieName.split(" S1 ")[0]
        if " S2 " in SerieName: SerieName = SerieName.split(" S2 ")[0]
        if " S3 " in SerieName: SerieName = SerieName.split(" S3 ")[0]

        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]
        if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
        if 'capitulo' in SerieName: SerieName = SerieName.split("capitulo")[0]
        if 'capítulo' in SerieName: SerieName = SerieName.split("capítulo")[0]

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        if 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]

        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('Episodio', '[COLOR goldenrod]Epis.[/COLOR]')

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                thumb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'doramasflixsone.jpg')

                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all',
                                            thumbnail=thumb, infoLabels={'year': '-'}, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if not item.cat:
        if config.get_setting('channels_seasons', default=True):
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR tan]Sin temporadas[/COLOR]')

    item.contentType = 'season'

    season = 1
    if '-temporada-' in item.url:
        season = scrapertools.find_single_match(item.url, '-temporada-(.*?)-')
        if not season: season = scrapertools.find_single_match(item.url, '-temporada-(.*?)/')
        if not season: season = 1

    elif '-season-' in item.url:
        season = scrapertools.find_single_match(item.url, '-season-(.*?)-')
        if not season: season = scrapertools.find_single_match(item.url, '-season-(.*?)/')
        if not season: season = 1

    item.contentSeason = season
    item.page = 0

    title_ser = item.contentSerieName.replace("’s", 's').replace("'t", 't').replace(':', '').replace("'t", 't').replace('ñ', 'n').replace(' ', '-').lower()

    title_ser = title_ser.replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').replace('&amp;', '').replace('amp;', '').replace('quot;', '').strip()

    if '-temporada-' in item.url: 
        temporada = scrapertools.find_single_match(item.url, '-temporada-(.*?)-')
        if temporada:
            title_ser = title_ser + '-temporada-' + temporada

    url = host + 'category/' + title_ser + '/'

    SerieName = title_ser.replace('-', ' ').capitalize()

    itemlist.append(item.clone( action='episodios', url=url, title='[COLOR hotpink]Serie[/COLOR] ' + title_ser.replace('-', ' ').capitalize(),
                                        serie = True, cat = False, page = 0,
                                        contentType = 'tvshow', contentSerieName = SerieName, contentSeason = season ))

    itemlist2 = episodios(item)

    itemlist = itemlist + itemlist2

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    matches = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    if not data: return itemlist

    hay_match = False

    match = scrapertools.find_single_match(data, '<link rel="canonical" href="(.*?)"')

    if item.serie:
        match = ''

        matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    if match:
        hay_match = True

        url = item.url

        epis = scrapertools.find_single_match(url, '-capitulo-(.*?)-')
        if not epis: epis = 1

        itemlist.append(item.clone( action='findvideos', url = match, title = item.title,
                                    contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

    if item.cat:
        matches = []

        if not hay_match:
            epis = scrapertools.find_single_match(item.url, '-capitulo-(.*?)-')
            if not epis: epis = 1

            itemlist.append(item.clone( action='findvideos', url = item.url, title = item.title,
                                        contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))
    else:
        if not matches: matches = re.compile('<div class="related-item tie_video">(.*?)</p>', re.DOTALL).findall(data)

        if not matches:
            season = item.contentSeason
            if '-temporada-' in item.url: season = scrapertools.find_single_match(item.url, '-temporada-(.*?)/')

            epis = scrapertools.find_single_match(item.url, '-capitulo-(.*?)/')
            if not epis: epis = scrapertools.find_single_match(item.url, '-capitulo-(.*?)-')

            if not epis: epis = 1

            itemlist.append(item.clone( action='findvideos', url=item.url, title=item.title,
                                        contentType = 'episode', contentSeason = season, contentEpisodeNumber=epis ))

            tmdb.set_infoLabels(itemlist)

            return itemlist

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts > 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                    platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    title_ser = item.contentSerieName.replace("’s", 's').replace("'t", 't').replace(':', '').replace('.', '-').replace("'t", 't').replace('ñ', 'n').replace(' ', '-').lower()

    title_ser = title_ser.replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').replace('&amp;', '').replace('amp;', '').replace('quot;', '').strip()

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        if not title_ser in url: continue

        title = scrapertools.find_single_match(match, '<h3 class="post-box-title">.*?rel="bookmark">(.*?)</a>').strip()
        if not title: title = scrapertools.find_single_match(match, '<h3><a href=".*?">(.*?)</a>').strip()

        if not title: title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not title: title = item.contentSerieName.replace('-', ' ').capitalize()

        title = title.replace('&#8211;', '').replace('&amp;', ' & ').replace('&#8217;', "'").replace('&#038;', '&').strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        epis = scrapertools.find_single_match(url, '-capitulo-(.*?)-')
        if not epis: epis = scrapertools.find_single_match(url, '-capitulo-(.*?)/')

        if not epis: epis = 1

        title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('Episodio', '[COLOR goldenrod]Epis.[/COLOR]')

        titulo = title

        if not 'capitulo' in titulo.lower():
            titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + titulo

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

        if not hay_match:
            if len(itemlist) >= item.perpage:
                break
        else:
            if len(itemlist) >= (item.perpage + 1):
                break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        thumb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'doramasflixsone.jpg')

        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page= item.page + 1, perpage = item.perpage,
                                        thumbnail=thumb, infoLabels={'year': '-'}, text_color = 'coral' ))
        else:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

            if next_page:
                if '/page/'in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'episodios', page = 0,
                                                thumbnail=thumb, infoLabels={'year': '-'}, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    ses = 0

    matches1 = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')
    matches2 = scrapertools.find_multiple_matches(data, '<IFRAME.*?SRC="(.*?)"')
    matches3 = scrapertools.find_multiple_matches(data, 'videoIframe.src = "(.*?)"')

    matches = matches1 + matches2 + matches3

    for url in matches:
        if not url: continue

        ses += 1

        if url.startswith("//"): url = 'https:' + url

        url = url.replace('/7/', '/e/').replace('&#038;', '&')

        if '/boosterx.' in url: continue
        elif '.mundodrama.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vose', other = other ))

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
