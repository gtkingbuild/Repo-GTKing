# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ytstv.me/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/release-year/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'top-imdb', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En [COLOR moccasin]4K[/COLOR]', action = 'list_all', url = host + 'quality/4k', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host + 'episode', group = 'episodes', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Temporadas completas', action = 'list_all', url = host + 'tag/tv-series-full-episode', group = 'episodes', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Alemania', action='list_all', url=host + 'country/germany', text_color='moccasin' ))
    itemlist.append(item.clone( title='Alemania (west)', action='list_all', url=host + 'country/west-germany', text_color='moccasin' ))
    itemlist.append(item.clone( title='Argentina', action='list_all', url=host + 'country/argentina', text_color='moccasin' ))
    itemlist.append(item.clone( title='Australia', action='list_all', url=host + 'country/australia', text_color='moccasin' ))
    itemlist.append(item.clone( title='Bélgica', action='list_all', url=host + 'country/belgium', text_color='moccasin' ))
    itemlist.append(item.clone( title='Bulgaria', action='list_all', url=host + 'country/bulgaria', text_color='moccasin' ))
    itemlist.append(item.clone( title='Canada', action='list_all', url=host + 'country/canada', text_color='moccasin' ))
    itemlist.append(item.clone( title='Chile', action='list_all', url=host + 'country/chile', text_color='moccasin' ))
    itemlist.append(item.clone( title='China', action='list_all', url=host + 'country/china', text_color='moccasin' ))
    itemlist.append(item.clone( title='Chipre', action='list_all', url=host + 'country/cyprus', text_color='moccasin' ))
    itemlist.append(item.clone( title='Colombia', action='list_all', url=host + 'country/colombia', text_color='moccasin' ))
    itemlist.append(item.clone( title='Corea', action='list_all', url=host + 'country/korea', text_color='moccasin' ))
    itemlist.append(item.clone( title='Corea del Sur', action='list_all', url=host + 'country/south-korea', text_color='moccasin' ))
    itemlist.append(item.clone( title='España', action='list_all', url=host + 'country/spain', text_color='moccasin' ))
    itemlist.append(item.clone( title='Estados Unidos', action='list_all', url=host + 'country/united-states', text_color='moccasin' ))
    itemlist.append(item.clone( title='Filipinas', action='list_all', url=host + 'country/philippines', text_color='moccasin' ))
    itemlist.append(item.clone( title='Finlandia', action='list_all', url=host + 'country/finland', text_color='moccasin' ))
    itemlist.append(item.clone( title='Francia', action='list_all', url=host + 'country/france', text_color='moccasin' ))
    itemlist.append(item.clone( title='Grecia', action='list_all', url=host + 'country/greece', text_color='moccasin' ))
    itemlist.append(item.clone( title='Holanda', action='list_all', url=host + 'country/netherlands', text_color='moccasin' ))
    itemlist.append(item.clone( title='Hong Kong', action='list_all', url=host + 'country/hong-kong', text_color='moccasin' ))
    itemlist.append(item.clone( title='Hungria', action='list_all', url=host + 'country/hungary', text_color='moccasin' ))
    itemlist.append(item.clone( title='India', action='list_all', url=host + 'country/india', text_color='moccasin' ))
    itemlist.append(item.clone( title='Indonesia', action='list_all', url=host + 'country/indonesia', text_color='moccasin' ))
    itemlist.append(item.clone( title='Irlanda', action='list_all', url=host + 'country/ireland', text_color='moccasin' ))
    itemlist.append(item.clone( title='Islandia', action='list_all', url=host + 'country/iceland', text_color='moccasin' ))
    itemlist.append(item.clone( title='Italia', action='list_all', url=host + 'country/italy', text_color='moccasin' ))
    itemlist.append(item.clone( title='Japón', action='list_all', url=host + 'country/japan', text_color='moccasin' ))
    itemlist.append(item.clone( title='Líbano', action='list_all', url=host + 'country/lebanon', text_color='moccasin' ))
    itemlist.append(item.clone( title='Mexico', action='list_all', url=host + 'country/mexico', text_color='moccasin' ))
    itemlist.append(item.clone( title='Nigeria', action='list_all', url=host + 'country/nigeria', text_color='moccasin' ))
    itemlist.append(item.clone( title='Noruega', action='list_all', url=host + 'country/norway', text_color='moccasin' ))
    itemlist.append(item.clone( title='Nueva Zelanda', action='list_all', url=host + 'country/new-zealand', text_color='moccasin' ))
    itemlist.append(item.clone( title='Perú', action='list_all', url=host + 'country/peru', text_color='moccasin' ))
    itemlist.append(item.clone( title='Polonia', action='list_all', url=host + 'country/poland', text_color='moccasin' ))
    itemlist.append(item.clone( title='Qatar', action='list_all', url=host + 'country/qatar', text_color='moccasin' ))
    itemlist.append(item.clone( title='Reino Unido', action='list_all', url=host + 'country/united-kingdom', text_color='moccasin' ))
    itemlist.append(item.clone( title='República Checa', action='list_all', url=host + 'country/czech-republic', text_color='moccasin' ))
    itemlist.append(item.clone( title='República Dominicana', action='list_all', url=host + 'country/dominican-republic', text_color='moccasin' ))
    itemlist.append(item.clone( title='Rusia', action='list_all', url=host + 'country/russia', text_color='moccasin' ))
    itemlist.append(item.clone( title='Serbia', action='list_all', url=host + 'country/serbia', text_color='moccasin' ))
    itemlist.append(item.clone( title='Sudafríca', action='list_all', url=host + 'country/south-africa', text_color='moccasin' ))
    itemlist.append(item.clone( title='Suiza', action='list_all', url=host + 'country/sweden', text_color='moccasin' ))
    itemlist.append(item.clone( title='Thailandia', action='list_all', url=host + 'country/thailand', text_color='moccasin' ))
    itemlist.append(item.clone( title='Turquía', action='list_all', url=host + 'country/turkey', text_color='moccasin' ))
    itemlist.append(item.clone( title='Ucrania', action='list_all', url=host + 'country/ukraine', text_color='moccasin' ))
    itemlist.append(item.clone( title='UK', action='list_all', url=host + 'country/uk', text_color='moccasin' ))
    itemlist.append(item.clone( title='USA', action='list_all', url=host + 'country/usa', text_color='moccasin' ))
    itemlist.append(item.clone( title='Venezuela', action='list_all', url=host + 'country/venezuela', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data,'>Genre<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque,'<a href="(.*?)".*?>(.*?)</a>')

    for url, tit in matches:
        if not url or not tit: continue

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie': top_year = 1959
    else: top_year = 1999

    for x in range(current_year, top_year, -1):
        url = host + 'release-year/' + str(x)

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div data-movie-id="(.*?)</div></div></div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img data-original="(.*?)"')
        qlty = scrapertools.find_single_match(match, '<span class="mli-quality">(.*?)</span>').strip()

        year = scrapertools.find_single_match(match, 'rel="tag">(.*?)</a>').strip()
        if not year: year = '-'
        else:
           title = title.replace('TV Shows ', '').replace('TV-Shows ', '').replace('TV-Series ', '').replace('TV Series ', '').strip()
           title = title.replace('(' + year + ')', '').strip()

        title = title.replace('&#8217;', '').replace('&#038;', '&').strip()

        tipo = 'tvshow' if '/series/' in url or '/episode/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            SerieName = title

            if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]

            SerieName = SerieName.strip()

            if item.group == 'episodes':
                if not '-full-episodes' in url: title = title.replace('Episode', '[COLOR goldenrod]Episode[/COLOR]')

                season = scrapertools.find_single_match(url, '-season-(.*?)-')

                epis = scrapertools.find_single_match(url, '-episode-(.*?)$')
                if not epis: epis = 0

                itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                            contentSerieName=SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis, infoLabels={'year': year} ))
            else:
                season = scrapertools.find_single_match(url, '-season-(.*?)-')

                itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                            contentSerieName=SerieName, contentType='tvshow', contentSeason = season, infoLabels={'year': year} ))
        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<ul class='pagination'>.*?<li class='active'>.*?href='(.*?)'")

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<strong>Season(.*?)</strong>', re.DOTALL).findall(data)

    for title in matches:
        title = title.strip()

        numtempo = title

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo Temporada [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.title = title
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        title = 'Temporada ' + title

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = numtempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<strong>Season ' + str(item.contentSeason) + '(.*?)</ul>')

    matches = re.compile('href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('YtsTv', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('YtsTv', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('YtsTv', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('YtsTv', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('YtsTv', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('YtsTv', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, episode in matches[item.page * item.perpage:]:
        epis = episode.replace('Episode', '').strip()

        if '-' in epis: episode = scrapertools.find_single_match(epis, '(.*?)-').strip()
        else: episode = epis

        titulo = '%sx%s %s' % (str(item.contentSeason), epis, item.contentSerieName)

        itemlist.append(item.clone( action='findvideos', title = titulo, url = url, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<span style="" class="lnk lnk-title">(.*?)</div></div></div>')

    matches = re.compile('<a(.*?)</a>', re.DOTALL).findall(bloque)

    ses = 0

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        if url.startswith('magne:'): url = url.replace('.magne', '.magnet')
        elif url.endswith(".torren"): url = url.replace('.torren', '.torrent')

        if url.startswith('magnet:'): pass
        elif url.endswith(".torrent"): pass
        else: url = ''

        if url:
            qlty = scrapertools.find_single_match(match, '<span class="lang_tit">.*?<span class="lnk lnk-dl" >(.*?)</span>')
            if '<b>Notice</b>' in qlty: qlty = ''

            lang = scrapertools.find_single_match(match, '<span class="lang_tit">(.*?)</span>')
            if lang == 'English': lang = 'Ing'

            other = ''
            if str(item.contentEpisodeNumber):
                other = scrapertools.find_single_match(match, '<span class="serv_tit">(.*?)</span>')
                if not item.contentEpisodeNumber == 0:
                    if not '-' in str(item.contentEpisodeNumber): other = ''

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = lang, quality = qlty, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    data = do_downloadpage(item.url)

    if '<title>Bot Verification</title>' in data:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith(".torrent"):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

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
