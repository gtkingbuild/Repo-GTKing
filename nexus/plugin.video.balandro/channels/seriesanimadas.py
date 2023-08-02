# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ww2.animedesho.com/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://seriesanimadas.org/', 'https://animedesho.com/']


domain = config.get_setting('dominio', 'seriesanimadas', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'seriesanimadas')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'seriesanimadas')
    else: host = domain


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'seriesanimadas', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_seriesanimadas', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='seriesanimadas', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_seriesanimadas', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + 'home', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'emision', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'series/estrenos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'series/populares', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + 'tvgenero/'

    data = do_downloadpage(host + 'series')

    matches = scrapertools.find_multiple_matches(data, '/tvgenero/(.*?)".*?>(.*?)</a>')

    for genre, title in matches:
        url = url_genre + genre

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        title = scrapertools.find_single_match(match, ' title="(.*?)"')

        if not url or not title: continue

        title = title.replace('Online', '').strip()

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        SerieName = title

        if 'Season' in title: SerieName = title.split("Season")[0]
        if 'Latino' in title: SerieName = title.split("Latino")[0]
        if '(ONA)' in title: SerieName = title.split("(ONA)")[0]

        SerieName = SerieName.strip()

        if item.search_type == 'tvshow':
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))
        else:
            title = title.replace('ver', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<ul class="pagination">.*?Previous.*?href="(.*?)"')
        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<div class="card-episodie shadow-sm">.*?<a href="(.*?)".*?title="(.*?)".*?src="(.*?)".*?</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, thumb in matches:
        c_title, epis, lang = scrapertools.find_single_match(title, r'^(.*?)\s*(?:Episodio)?\s*(\d+)\s*(.*)')

        if c_title == 'ver': c_title = title

        c_title = c_title.replace('ver ', '').strip()

        titulo = '1x%s %s' % (epis, c_title)

        SerieName = c_title

        if 'Episodio' in c_title: SerieName = c_title.split("Episodio")[0]
        if 'Season' in c_title: SerieName = c_title.split("Season")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb, infoLabels={'year': '-'},
									contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = re.compile('<div id="season-(.*?)"', re.DOTALL).findall(data)

    if not matches:
        itemlist = episodios(item)
        return itemlist

    for season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = season ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    if not item.contentSeason:
        item.contentSeason = 1
        patron = '<a class="episodie-list" href="([^"]+)" .*?</i> Episodio (\d+).*?</span>'
    else:
        patron = 'class="episodie-list" href="([^"]+)" title=".*?Temporada %s .*?pisodio (\d+).*?">' % str(item.contentSeason)

    matches = re.compile(patron, re.DOTALL).findall(data)

    if not matches:
        patron = 'class="episodie-list" href="([^"]+)" title=".*?pisodio (\d+).*?">'
        matches = re.compile(patron, re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesAnimadas', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesAnimadas', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesAnimadas', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesAnimadas', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesAnimadas', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for url, epis in matches[item.page * item.perpage:]:
        titulo = '%sx%s - Episodio %s' % (item.contentSeason, epis, epis)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, 
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'latino': 'Lat', 'audio latino': 'Lat', 'español': 'Esp', 'audio español': 'Esp', 'sub español': 'Vose', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    matches = re.compile('video\[(\d+)\] = .*?src="([^"]+)".*?;', re.DOTALL).findall(data)

    ses = 0

    for option, url in matches:
        ses += 1

        lang = scrapertools.find_single_match(data, '"#option%s".*?<span>(.*?)</span>' % str(option))
        lang = lang.strip().lower()

        if 'redirect' in url:
            url_data = httptools.downloadpage(url).data
            url = scrapertools.find_single_match(url_data,'var redir = "([^"]+)";')
            if not url:
                url = scrapertools.find_single_match(url_data,'window.location.href = "([^"]+)";')

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: url = ''
        elif '/badshare.io/' in url: url = ''

        if url:
            if url.startswith('//'): url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor == 'directo': continue

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = IDIOMAS.get(lang, lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "search?s=" + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
