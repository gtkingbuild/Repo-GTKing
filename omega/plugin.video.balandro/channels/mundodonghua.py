# -*- coding: utf-8 -*-

import re, base64

from lib import jsunpack

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.mundodonghua.com/'


perpage = 30


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_anime', default=False): return

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'lista-donghuas', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Nuevos Capítulos', action = 'list_all', url = host + 'lista-episodios', group = 'last_epis', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'En emision', action = 'list_all', url = host + 'lista-donghuas-emision', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Finalizados', action = 'list_all', url = host + 'lista-donghuas-finalizados', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    bloque = scrapertools.find_single_match(data, '</i> Generos<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?"><.*?>(.*?)</span>')

    for url, title in matches:
        if not host in url: url = host[:-1] + url

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    bloque = scrapertools.find_single_match(data,'> Lista de (.*?)</center>')
    if not bloque: bloque = scrapertools.find_single_match(data,'> Resultados de la busqueda (.*?)</center>')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="item col-lg-2 col-md-2 col-xs-4">(.*?)</div></div></div>')
    if not matches:  matches = scrapertools.find_multiple_matches(bloque, '<div class="item col-lg-3 col-md-3 col-xs-4">(.*?)</div></div></div>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h5 class="sf fc-dark f-bold fs-14">(.*?)</h5>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if not host in thumb: thumb = host[:-1] + thumb

        if not host in url: url = host[:-1] + url

        SerieName = title

        SerieName = SerieName.strip()

        if item.group == 'last_epis':
            if 'Episodio ' in SerieName: SerieName = SerieName.split("Episodio ")[0]

            epis = scrapertools.find_single_match(match,'Episodio (.*?)$').strip()
            if not epis: epis = 1

            title = title.replace('Episodio ', '[COLOR goldenrod]Episodio [/COLOR]')

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, infoLabels={'year': '-'},
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epis))

        else:
            if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]

            itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True

        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data,'<ul class="pagination">.*?<li>.*?<a href="(.*?)"')

            if next_page:
                if not host in next_page: next_page = host[:-1] + next_page

                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    bloque = scrapertools.find_single_match(data, '> Lista de Episodios<(.*?)</div></div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?<img src="(.*?)".*?<blockquote class="message sf fc-dark f-bold fs-16">(.*?)</blockquote>')

    if not matches:
        url = scrapertools.find_single_match(bloque, '<a href="(.*?)"')

        if url:
            if not host in url: url = host[:-1] + url

            itemlist.append(item.clone( action='findvideos', url = url, title = item.title, contentType = 'movie', contentTitle = item.contentSerieName ))

        return itemlist

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('MundoDonghua', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MundoDonghua', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MundoDonghua', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MundoDonghua', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('MundoDonghua', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('MundoDonghua', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, thumb, title in matches[item.page * item.perpage:]:
        if not host in url: url = host[:-1] + url

        if not host in thumb: thumb = host[:-1] + thumb

        title = title.strip()

        epis = scrapertools.find_single_match(title, '.*?-(.*?)$').strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(epis) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    ses = 0

    matches = scrapertools.find_multiple_matches(data, "(eval.*?)\n")

    if len(matches) > 1:
        for match in matches:
            ses += 1

            ref = ''

            unpack = jsunpack.unpack(match)

            url = scrapertools.find_single_match(unpack, 'file(?:"|):"([^"]+)')

            if not url:
                unpack = unpack.replace('\\/', '/')
                unpack = unpack.replace('=\\', '=').replace('\\"', '/"')
                unpack = unpack.replace('=/', '=').replace('\/"', '"')

                url = scrapertools.find_single_match(unpack, '<iframe src="(.*=)"')

            if not url:
                slug = scrapertools.find_single_match(unpack, '"slug":"(.*?)"')

                if slug:
                    ref = item.url
                    url =  host + 'api_donghua.php?slug=' + slug

            if url:
                if not url.startswith('http'): url = 'https:' + url

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                other = ''
                if servidor == 'various': other = servertools.corregir_other(url)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, ref = ref, language = 'Vose', other = other ))

    else:
        unpack = jsunpack.unpack(matches[0])

        matches = scrapertools.find_multiple_matches(unpack, '"slug":"([^"]+)')

        if matches:
            for match in matches:
                ses += 1

                url =  host + 'api_donghua.php?slug=' + match

                data = httptools.downloadpage(url, headers={'Referer': item.url})

                if data.get('url',''): url = 'https://www.dailymotion.com/video/' + base64.b64decode(data['url']).decode('utf-8')
                elif data.get('source', ''): url = data['source'][0].get('file','')

                if url:
                    if not url.startswith('http'): url = 'https:' + url

                    ref = ''
                    if 'api_donghua.php?slug=' in url: ref = item.url

                    servidor = servertools.get_server_from_url(url)
                    servidor = servertools.corregir_servidor(servidor)

                    url = servertools.normalize_url(servidor, url)

                    other = ''
                    if servidor == 'various': other = servertools.corregir_other(url)

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, ref = ref, language = 'Vose', other = other ))

        else:
            url = scrapertools.find_single_match(unpack, 'file(?:"|):"([^"]+)')
            if not url: url = scrapertools.find_single_match(unpack, '<iframe src="(.*=)"')

            if url:
                if not url.startswith('http'): url = 'https:' + url

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                other = ''
                if servidor == 'various': other = servertools.corregir_other(url)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Vose', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.server == 'directo':
        if item.ref: data = httptools.downloadpage(url, headers={'Referer': item.ref}).data
        else: data = httptools.downloadpage(url).data

        if not data: return itemlist

        if '404 Not Found' in data: return itemlist

        vid = scrapertools.find_single_match(data, '"url":"(.*?)"')

        if vid:
            try: vid = base64.b64decode(vid).decode('utf-8')
            except: pass

            if vid: url = 'https://www.dailymotion.com/video/' + vid

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'zplayer': url = url + '|' + host

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "busquedas/" + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
