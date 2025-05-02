# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www3.animeflv.net/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://www1.animeflv.ws/', 'https://www10.animeflv.cc/', 'https://www3.animeflv.cc/',
             'https://ww3.animeflv.cc/', 'https://animeflv.bz/', 'https://www1.animeflv.bz/',
             'https://www2.animeflv.bz/', 'https://animeflv.so/', 'https://animeflv.vc/',
             'https://animeflv.sh/', 'https://animeflv.ws/']


domain = config.get_setting('dominio', 'animeflv', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'animeflv')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'animeflv')
    else: host = domain


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'animeflv', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_animeflv', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='animeflv', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_animeflv', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(Item( channel='actions', action='show_old_domains', title='[COLOR coral][B]Historial Dominios[/B][/COLOR]', channel_id = 'animeflv', thumbnail=config.get_thumb('animeflv') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_anime', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'all', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'browse?page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_all', url = host, group = 'news', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'browse?status[]=1&order=default&page=1', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Finalizados', action = 'list_all', url = host + 'browse?status[]=2&order=default&page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + 'browse?type[]=special&order=default&page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'browse?type[]=ova&order=default&page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Proximamente', action = 'list_all', url = host + 'browse?status[]=3&order=default&page=1', search_type = 'tvshow', text_color='yellowgreen' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'browse?type[]=movie&order=default&page=1', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url_genre = url = host + 'browse'

    data = do_downloadpage(url_genre)

    bloque = scrapertools.find_single_match(data, '<select name="genre(.*?)</select>')

    matches = re.compile('<option value="(.*?)">(.*?)</option>').findall(bloque)

    for genre_id, title in matches:
        title = title.replace('&aacute;', 'a').replace('&eacute;', 'e').replace('&iacute;', 'i').replace('&oacute;', 'o').replace('&uacute;', 'u')

        url = '%s?genre[]=%s&order=default&page=1' % (url_genre, genre_id)

        itemlist.append(item.clone( action = "list_all", url = url, title = title, text_color='springgreen' ))

    return sorted(itemlist, key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    url_anio = url = host + 'browse'

    tope_year = 1989

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        url = '%s?year=%s&page=1' % (url_anio, str(x))

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article(.*?)</article>').findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3 class="Title">(.*?)</h3>')

        if not url or not title: continue

        title = title.replace('&oacute;n', 'on')

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        plot = scrapertools.find_single_match(match, '<p class="des">(.*?)</p>')

        tipo = 'movie' if '>Película<' in match else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            PeliName = corregir_SerieName(title)

            itemlist.append(item.clone( action='findvideos', url=url if url.startswith('http') else host[:-1] + url, title=title,
                                        thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=PeliName, infoLabels={'year': '-', 'plot': plot} ))

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            SerieName = corregir_SerieName(title)

            title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

            itemlist.append(item.clone( action='episodios', url=url if url.startswith('http') else host[:-1] + url, title=title,
                                        thumbnail=thumb, fmt_sufijo=sufijo,
                                        page = 0, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-', 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<ul class="pagination">.*?<li class="active">.*?</a>.*?<a href="(.*?)"')

            if next_page:
                if 'page=' in next_page:
                    if not host in next_page: next_page = host[:-1] + next_page

                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h2>Últimos episodios</h2>(.*?)<h2>Últimos animes agregados</h2>')

    patron = '<li>.*?<a href="(.*?)".*?<img src="(.*?)".*?<span class="Capi">(.*?)</span>.*?class="Title">(.*?)</strong>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for url, thumb, episode, title in matches:
        if not url or not title: continue

        SerieName = corregir_SerieName(title)

        epis = episode.replace('Episodio', '').strip()

        episode = episode.replace('Episodio', 'Epis.')

        title = episode + ' ' + title

        title = title.replace('Epis.', '[COLOR goldenrod]Epis.[/COLOR]')

        title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        itemlist.append(item.clone( action='findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail=thumb,
                                    contentSerieName = SerieName, contentType = 'episode',
                                    contentSeason = 1, contentEpisodeNumber=epis, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    info = scrapertools.find_single_match(data, "anime_info = \[(.*?)\];")

    if not info: return itemlist

    try:
        info = eval(info)
    except Exception:
        return itemlist

    bloque = scrapertools.find_single_match(data, 'var episodes = (.*?);')

    if not bloque: return itemlist

    matches = eval(scrapertools.find_single_match(data, "var episodes = (.*?);"))

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('AnimeFlv', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimeFlv', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeFlv', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeFlv', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeFlv', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeFlv', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimeFlv', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for episode in matches:
        season = 1

        url = '{}ver/{}-{}'.format(host, info[2], episode[0])

        epis = episode[0]
        
        titulo = '{}x{} Episodio {}'.format(season, str(epis), str(epis))

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if not item.search_type == 'tvshow':
        if not '-1' in item.url: item.url = item.url.replace('/anime/', '/ver/') + '-1'

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    ses = 0

    bloque = scrapertools.find_single_match(data, 'var videos =(.*?);')

    matches = re.compile('"code":"(.*?)"', re.DOTALL).findall(bloque)

    for url in matches:
        ses += 1

        url = url.replace('\\/', '/')

        if '/embedsito.' in url: continue

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


def corregir_SerieName(SerieName):
    logger.info()

    if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
    if 'season' in SerieName: SerieName = SerieName.split("season")[0]
    if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]

    if ': ' in SerieName: SerieName = SerieName.split(": ")[0]

    if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]

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
        item.url = host + 'browse?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

