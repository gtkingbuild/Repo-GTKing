# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www1.animeflv.ws/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://www10.animeflv.cc/', 'https://www3.animeflv.net/', 'https://www3.animeflv.cc/',
             'https://ww3.animeflv.cc/', 'https://animeflv.bz/', 'https://www1.animeflv.bz/',
             'https://www2.animeflv.bz/', 'https://animeflv.so/', 'https://animeflv.vc/',
             'https://animeflv.sh/', 'https://animeflv.ws/']


domain = config.get_setting('dominio', 'animeflv', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'animeflv')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'animeflv')
    else: host = domain


perpage = 30


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

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'browse', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_all', url = host, search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'browse?genres=all&year=all&status=all&order=1&Tipo=4', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'browse?genres=all&year=all&status=all&order=1&Tipo=2', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + 'browse?genres=all&year=all&status=all&order=1&Tipo=3', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = url = host + 'browse'

    data = do_downloadpage(url_cat)

    matches = re.compile(r'<li class="tmp "><a><label class="radio"><input  type="radio" value="(\d+)" name="order" data-text="([^"]+)').findall(data)

    for categorie_id, title in matches:
        url = '%s?order=%s' %(url_cat, categorie_id)
        title = title.strip()

        itemlist.append(item.clone( action = "list_all", url = url, title = title, text_color='moccasin' ))

    return sorted(itemlist, key=lambda x: x.title)


def generos(item):
    logger.info()
    itemlist = []

    url_genre = url = host + 'browse'

    data = do_downloadpage(url_genre)

    matches = re.compile(r'a><label><input  class="genre-ids" value="([^"]+)".*?type="checkbox">([^<]+)').findall(data)

    for genre_id, title in matches:
        url = '%s?genres=%s' %(url_genre, genre_id)

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
        itemlist.append(item.clone( title = str(x), url = '%s?year=%s' % (url_anio, str(x)), action = 'list_all', text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<article class="Anime alt[^"]+"><a href="([^"]+)">'
    patron += '<.*?img src="([^"]+)".*?h3 class="Title">([^<]+).*?<span class="Type ([^"]+).*?<p class="des">([^<]+)'

    matches = re.compile(patron).findall(data)

    num_matches = len(matches)

    for url, thumb, title, tipo, info in matches[item.page * perpage:]:
        if not url or not title: continue

        if tipo == "movie":
            itemlist.append(item.clone( action='findvideos', url=url if url.startswith('http') else host[:-1] + url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))
        else:
            SerieName = title

            if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
            if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]

            SerieName = SerieName.strip()

            itemlist.append(item.clone( action='episodios', url=url if url.startswith('http') else host[:-1] + url, title=title, thumbnail=thumb,
                                        page = 0,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year':'-', 'plot': info} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, "li\s*class=selected><a href='[^']+.*?<\/li><li.*?<a href='([^']+)")

            if next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page if url.startswith('http') else item.url + next_page if not '?' in item.url else item.url.split('?')[0] + next_page,
                                            action = 'list_all', page = 0, text_color = 'coral' ))

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

        SerieName = title

        if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
        if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]

        SerieName = SerieName.strip()

        epis = episode.replace('Episodio', '').strip()

        episode = episode.replace('Episodio', 'Epis.')

        title = episode + ' ' + title

        title = title.replace('Epis.', '[COLOR goldenrod]Epis.[/COLOR]')

        if url:
            itemlist.append(item.clone( action='findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail=thumb,
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li class="fa-play-circle"><a href="([^"]+)"><.*?this.src=\'([^\']+).*?<p>([^<]+)', re.DOTALL).findall(data)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
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

    i = 0

    for url, thumb, title in matches[item.page * item.perpage:]:
        i += 1

        titulo = title + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url if url.startswith('http') else host[:-1] + url, title = titulo,
                                    thumbnail=thumb, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = i ))

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

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile(r'<li role="presentation" data-video="([^"]+)" title="([^"]+)".*?<a href="[^"]+', re.DOTALL).findall(data)

    if not matches:
        new_url = scrapertools.find_single_match(data, '<ul class="ListCaps" id="episodeList".*?a href="(.*?)"')
        if new_url:
            if not new_url.startswith('http'):
                new_url = host[:-1] + new_url
                data = do_downloadpage(new_url)

                matches = re.compile(r'<li role="presentation" data-video="([^"]+)" title="([^"]+)".*?<a href="[^"]+', re.DOTALL).findall(data)

    ses = 0

    for url, srv in matches:
        ses += 1

        if not url.startswith('http'): url = 'https:' + url

        if "/streaming.php?" in url:
            data = do_downloadpage(url)

            links = scrapertools.find_multiple_matches(data, '<li class="linkserver".*?data-video="(.*?)"')

            for link in links:
                servidor = servertools.get_server_from_url(link)
                servidor = servertools.corregir_servidor(servidor)

                link = servertools.normalize_url(servidor, link)

                other = ''
                if servidor == 'various': other = servertools.corregir_other(link)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = link, language = 'Vose', other = other ))

        else:
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


def play(item):
    logger.info()
    itemlist = []

    servidor = item.server

    url = item.url

    if "/streaming.php?" in item.url:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<iframe id="embedvideo".*?</div>.*?src="(.*?)"')

        if 'www.googletagmanager.com' in url: url = ''
        elif 'error.jpg' in url: url = ''

        if not url: url = scrapertools.find_single_match(data, '<li class="linkserver".*?data-video="(.*?)"')

    if url:
        if not url.startswith("http"): url = "https:" + url

        url = url.replace("\\/", "/")

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


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

