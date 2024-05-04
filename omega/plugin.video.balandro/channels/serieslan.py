# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urllib
else:
    import urllib.parse as urllib

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools, tmdb


host = 'https://serieslan.com/'


perpage = 30


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action ='list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Catálogo por alfabético (A - Z)', action ='list_lst', url = host + 'lista.php?or=abc', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Catálogo por alfabético (Z - A)', action ='list_lst', url = host + 'lista.php?or=cba', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Live action', action ='list_liv', url = host + 'liveaction', search_type = 'tvshow', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Más populares', action ='list_lst', url = host + 'lista.php?or=mas', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más antiguas', action ='list_lst', url = host + 'lista.php?or=ler', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más actuales', action ='list_lst', url = host + 'lista.php?or=rel', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más impopulares', action ='list_lst', url = host + 'lista.php?or=sam', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if letra == '#': letter = '0'
        else: letter = letra.lower()

        url = host + 'lista.php?or=abc'

        itemlist.append(item.clone( title = letra, action = 'list_abc', url = host + 'lista.php?or=abc', letra = letter, text_color='hotpink' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)$')

    matches = re.compile('<a href="(.*?)".*?src="(.*?)".*?title="(.*?)"', re.DOTALL).findall(bloque)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for url, thumb, title in matches[desde:hasta]:
        if not url.startswith('http'): url = host[:-1] + url

        if not thumb.startswith('http'): thumb = host[:-1] + thumb

        itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb,  contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > hasta:
            itemlist.append(item.clone( title='Siguientes ...', page = item.page + 1, action = 'list_all', text_color='coral' ))
            buscar_next = False

        if buscar_next:
            if '<a class="sel">' in data:
                next_page = scrapertools.find_single_match(data, '<a class="sel">.*?<a href="(.*?)"')

                if next_page:
                    if 'pag-' in next_page:
                        next_page = host + next_page

                        itemlist.append(item.clone( title='Siguientes ...', url = next_page, page = 0, action = 'list_all', text_color='coral' ))

    return itemlist


def list_liv(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)$')

    matches = re.compile('<a href="(.*?)".*?src="(.*?)".*?title="(.*?)"', re.DOTALL).findall(bloque)

    for url, thumb, title in matches:
        if item.filtro:
           if not item.filtro.lower() in title.lower(): continue

        if not url.startswith('http'): url = host[:-1] + url

        if not thumb.startswith('http'): thumb = host[:-1] + thumb

        itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb,  contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def list_lst(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = re.compile('data-original="(.*?)">.*?<a href="(.*?)".*?<h2>(.*?)</h2></a><span>(.*?)</span>', re.DOTALL).findall(data)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for thumb, url, title, year in matches[desde:hasta]:
        if not year: year = '-'

        if not url.startswith('http'): url = host[:-1] + '/' + url

        if not thumb.startswith('http'): thumb = host[:-1] + thumb

        itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title='Siguientes ...', page = item.page + 1, action = 'list_lst', text_color='coral' ))

    return itemlist


def list_abc(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('data-original="(.*?)">.*?<a href="(.*?)".*?<h2>(.*?)</h2></a><span>(.*?)</span>', re.DOTALL).findall(data)

    for thumb, url, title, year in matches:
        title_letra = title[0]

        if item.letra:
            if item.letra == '0':
                if not title_letra == '¡':
                    if not title_letra == '¿':
                       if not title_letra in '0123456789': continue
            else:
                if not title_letra.lower() == item.letra:  continue

        if item.filtro:
           if not item.filtro.lower() in title.lower(): continue

        if not year: year = '-'

        if not url.startswith('http'): url = host[:-1] + '/' + url

        if not thumb.startswith('http'): thumb = host[:-1] + thumb

        itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'class="select-ss".*?>Temporada(.*?)</a></li>')

    for tempo in matches:
        num_tempo = str(tempo)
        num_tempo = num_tempo.strip()

        title = 'Temporada ' + num_tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = 0
            itemlist = episodios(item)
            return itemlist

        num_tempo = int(num_tempo)
        num_tempo = num_tempo - 1

        itemlist.append(item.clone( action='episodios', title = title, page = 0, contentType = 'season', contentSeason = num_tempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, "dt='ss-" + str(item.contentSeason) + "'.*?>(.*?)</div>")
    if not matches: matches = scrapertools.find_multiple_matches(data, 'dt="ss-' + str(item.contentSeason) + '".*?>(.*?)</div>')

    # ~ Temporada única
    if not matches: matches = [(0, data)]

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesLan', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesLan', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesLan', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesLan', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesLan', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesLan', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        season = int(item.contentSeason)
        season += 1

        episodios = scrapertools.find_multiple_matches(match, '<a(.*?)</a>')

        for episodio in episodios:
            url = scrapertools.find_single_match(episodio, 'href="(.*?)"')

            if '#gs-' in url: continue

            epi = scrapertools.find_single_match(episodio, '</strong>(.*?)</span>')
            if '-' in epi: epi = scrapertools.find_single_match(epi, '(.*?)-').strip()

            title = scrapertools.find_single_match(episodio, '</span>(.*?)</li>')

            titulo = '%sx%s %s' % (str(season), epi, title)

            url = host + url

            itemlist.append(item.clone( action='findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epi ))

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

    data = httptools.downloadpage(item.url).data

    _sa = re.findall('var _sa = (true|false);', data, flags=re.DOTALL)[0]
    _sl = re.findall("var _sl = \['([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)'", data, flags=re.DOTALL)[0]

    if not _sa or not _sl: return itemlist

    aux = _sl[3].lower().replace('(','[').replace(')',']')

    if '[castellano]' in aux: lang = 'Esp'
    elif '[ingles]' in aux: lang = 'Eng'
    else:
        lang = scrapertools.find_single_match(data, '<span>Idioma:\s*</span>([^<]+)')
        if 'Latino' in lang: lang = 'Lat'

    matches = re.findall('<button class="selop" sl="([^"]+)">([^<]+)</button>', data, flags=re.DOTALL)

    ses = 0

    ord_link = 0

    for num, srv in matches:
        ses += 1

        ord_link += 1

        url = resuelve_golink(int(num), _sa, _sl)

        servidor = servertools.corregir_servidor(srv)

        if servidor:
            if not servertools.is_server_available(servidor): servidor = ''
            elif not servertools.is_server_enabled(servidor): continue 

        other = ''
        if not servidor:
            servidor = 'directo'
            other = srv

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, language = lang, title = '', url = url,
                                                      slr = item.url, ord_link = ord_link, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def resuelve_golink (num, sa, sl):
    b = [3, 10, 5, 22, 31]
    d = ''

    for i in range(len(b)):
        d += sl[2][b[i]+num:b[i]+num+1]

    SVR = 'https://viteca.stream' if sa == 'true' else 'https://serieslan.com'

    TT = "/" + urllib.quote_plus(sl[3].replace("/", "><")) if num == 0 else ""

    return SVR + "/el/" + sl[0] + "/" + sl[1] + "/" + str(num) + "/" + sl[2] + d + TT


def play(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    try:
       from lib import serieslanresolver

       url = serieslanresolver.decode_url(data)
    except:
       try:
          from lib import serieslanresolver2 as serieslanresolver

          url = serieslanresolver.deco_url(item.slr, item.ord_link)
       except:
          url = ''

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor and (servidor != 'directo' or 'googleusercontent' in url):
            url = servertools.normalize_url(servidor, url)

            itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def sub_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url, post = 'k=' + item.filtro ).data

    matches = jsontools.load(data)

    for datos in matches['dt']:
        if len(datos) < 4: continue
        elif not datos[1]: continue
        elif not datos[2]: continue

        year = datos[3]
        if not year: year = '-'

        itemlist.append(item.clone( title=datos[1], url= host + datos[2], action='temporadas', thumbnail=host + 'tb/' + datos[0] + '.jpg', 
                                    contentType='tvshow', contentSerieName=datos[1], infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.filtro = texto.replace(" ", "+")

        item.url = host + 'lista.php?or=abc'
        itemlist = list_abc(item)
        if itemlist: return itemlist

        item.url = host + 'liveaction'
        itemlist = list_liv(item)
        if itemlist: return itemlist

        item.url = host + 'b.php'
        return sub_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
