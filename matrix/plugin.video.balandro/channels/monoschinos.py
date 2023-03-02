# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://monoschinos2.com'


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return itemlist

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/animes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + '/animes?genero=emision', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + '/animes?categoria=false&genero=castellano', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + '/animes?categoria=false&genero=latino', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En blu-ray', action = 'list_all', url = host + '/animes?categoria=false&genero=blu-ray', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + '/animes'

    data = httptools.downloadpage(url_genre).data

    bloque = scrapertools.find_single_match(data, '<select name="genero">(.*?)</select>')

    matches = re.compile('<option value="(.*?)">(.*?)</option>').findall(bloque)

    for gen, title in matches:
        title = title.strip()

        if title == 'Genero': continue
        elif title == 'Blu-ray': continue
        elif title == 'Castellano': continue
        elif title == 'Emisión': continue
        elif title == 'Latino': continue

        url = host + '/animes?categoria=false&genero=%s&fecha=false&letra=false' % gen

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1951, -1):
        url = host + '/animes?categoria=false&genero=false&fecha=%s&letra=false' % str(x)

        itemlist.append(item.clone( title = str(x), url = url, action='list_all' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = host + '/animes'

    data = httptools.downloadpage(url_cat).data

    bloque = scrapertools.find_single_match(data, '<select name="categoria">(.*?)</select>')

    matches = re.compile('<option value="(.*?)">(.*?)</option>').findall(bloque)

    for cat, title in matches:
        title = title.strip()

        if title == 'Categoría': continue
        elif title == 'PREESTRENO': continue

        url = host + '/animes?categoria=%s&genero=false&letra=false' % cat

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="col-(.*?)</a></div>').findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, 'title="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, '<h.*?>(.*?)</h')

        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        if not url or not title: continue

        SerieName = title

        if 'OVA' in title: SerieName = title.split("OVA")[0]
        if 'Doblaje' in title: SerieName = title.split("Doblaje")[0]
        if 'La película' in title: SerieName = title.split("La película")[0]
        if 'Season' in title: SerieName = title.split("Season")[0]

        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                    infoLabels={'year': '-'}, contentType = 'tvshow', contentSerieName = SerieName ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '"page-item active".*?</li>.*?<a class="page-link" href="([^"]+)">')

        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'Capítulos Recientes</h1>(.*?)</section>')

    matches = re.compile('<div class="col col-md-6(.*?)</a></div>', re.DOTALL).findall(bloque)

    for match in matches:
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, 'title="(.*?)"')

        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        epis = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        if not epis: epis = 1

        SerieName = title

        if 'OVA' in title: SerieName = title.split("OVA")[0]
        if 'Doblaje' in title: SerieName = title.split("Doblaje")[0]
        if 'capitulo' in title: SerieName = title.split("capitulo")[0]
        if 'Season' in title: SerieName = title.split("Season")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data

    matches = re.compile('data-episode="(.*?)".*?href="(.*?)".*?src="(.*?)".*?<p class="animetitles">(.*?)<', re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    i = 0

    for epis, url, thumb, title in matches[item.page * item.perpage:]:
        i += 1

        title = title.replace('Sub Español', '').strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = 1, contentEpisodeNumber=i ))

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

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('class="play-video".*?data-player="(.*?)">(.*?)</p>', re.DOTALL).findall(data)

    ses = 0

    for d_play, servidor in matches:
        ses += 1

        servidor = servidor.lower()

        if 'hqq' in servidor or 'waaw' in servidor or 'netu' in servidor: continue
        elif servidor == 'puj': continue

        elif servidor == 'ok': servidor = 'okru'
        elif servidor == 'zeus': servidor = 'directo'

        elif 'fembed' in servidor: servidor = 'fembed'
        elif 'senvid' in servidor: servidor = 'sendvid'
        elif 'drive' in servidor: servidor = 'gvideo'
        elif 'anonfile' in servidor: servidor = 'anonfiles'
        elif 'zippy' in servidor: servidor = 'zippyshare'
        elif 'sblanh' in servidor: servidor = 'streamsb'
        elif 'sblongvu' in servidor: servidor = 'streamsb'
        elif 'sbchill' in servidor: servidor = 'streamsb'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', d_play = d_play, language = 'Vose' ))

    # download
    bloque = scrapertools.find_single_match(data, '<div class="downbtns">(.*?)</div>')

    matches = re.compile('href="(.*?)".*?<button>(.*?)<', re.DOTALL).findall(bloque)

    for url, srv in matches:
        ses += 1

        srv = srv.lower().strip()

        if srv == '1fichier': continue
        elif srv == 'fireload': continue
        elif srv == 'mediafire': continue

        elif 'anonfile' in srv: srv = 'anonfiles'
        elif 'zippy' in srv: srv = 'zippyshare'

        itemlist.append(Item( channel = item.channel, action = 'play', server = srv, title = '', url = url, language = 'Vose', other = 'D' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if not item.d_play:
        itemlist.append(item.clone( url = item.url, server = item.server ))
        return itemlist

    url = base64.b64decode(item.d_play).decode("utf-8")

    if host in url: url = scrapertools.find_single_match(url, 'url=(.*?)$')

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/buscar?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

