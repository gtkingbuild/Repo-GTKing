# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://animeenlatino.moe/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://animeyt.moe/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post).data

    return data


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_anime', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver/?status=&type=&order=', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_all', url = host + 'ver/?status=&type=&order=update', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Actualizados', action = 'list_all', url = host + 'ver/?status=&type=&order=latest', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'ver/?sub=&order=popular', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + '?s=castellano', search_type = 'tvshow', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + '?s=latino', search_type = 'tvshow', text_color='moccasin' ))

    itemlist.append(item.clone( title = 'Series', action = 'list_all', url = host + 'ver/?status=&type=tv&order=', search_type = 'tvshow', text_color = 'hotpink' ))
    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'ver/?status=&type=movie&order=', search_type = 'tvshow', text_color='deepskyblue' ))
    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'ver/?type=ova&sub=', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Onas', action = 'list_all', url = host + 'ver/?status=&type=ona&order=', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'generos//').data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, '</h1>(.*?)</ul>')

    matches = re.compile('<a href="(.*?)".*?><span class="name">(.*?)</span>').findall(data)

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Modo Texto<(.*?)</div></div></div>')
    if not bloque: bloque = scrapertools.find_single_match(data, '<h1(.*?)</div></div></div>')

    matches = re.compile('<article(.*?)</article>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(title, '(\d{4})')
        if year: title = title.replace('(' + year + ')', '').replace('(' + year + ' )', '').strip()
        else: year = '-'

        title = title.replace('&#8217;', "'").replace('&#8211;', '').replace('&#215;', 'x')

        if '>Movie<' in match:
            PeliName = title

            if '[Película' in PeliName: PeliName = PeliName.split("[Película")[0]
            elif '[Latino' in PeliName: PeliName = PeliName.split("[Latino")[0]
            elif '[Castellano' in PeliName: PeliName = PeliName.split("[Castellano")[0]

            PeliName = PeliName.strip()

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, contentType = 'movie', contentTitle = PeliName, infoLabels={'year': year} ))

        else:
            SerieName = title

            if '[Temporada' in SerieName: SerieName = SerieName.split("[Temporada")[0]

            if '[Latino' in SerieName: SerieName = SerieName.split("[Latino")[0]
            elif '[Castellano' in SerieName: SerieName = SerieName.split("[Castellano")[0]
            elif '[Subtitulado' in SerieName: SerieName = SerieName.split("[Subtitulado")[0]

            SerieName = SerieName.strip()

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
         if '<div class="pagination">' in data:
             next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?class="page-numbers current">.*?href="(.*?)"')
         else:
             bloque = scrapertools.find_single_match(data, '</article></div>(.*?)</i></a>')

             if 'Previous' in bloque: next_page = scrapertools.find_single_match(bloque, 'Previous.*?<a href="(.*?)"')
             else: next_page = scrapertools.find_single_match(bloque, '<a href="(.*?)"')

         if next_page:
             if 'page=' in next_page: next_page = host + 'ver/' + next_page

             if 'page=' in next_page or '/page/' in next_page:
                 itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="eplister">(.*?)</ul></div></div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?<div class="epl-num">(.*?)</div>.*?<div class="epl-title">(.*?)</div>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, epis, title in matches[item.page * item.perpage:]:
        title = title.replace('&#8217;', "'").replace('&#8211;', '').replace('&#215;', 'x')

        titulo = title + ' ' + item.contentSerieName

        if item.contentSerieName:
            itemlist.append(item.clone( action='findvideos', url = url, title = titulo, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))
        else:
            itemlist.append(item.clone( action='findvideos', url = url, title = titulo ))

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

    lang = 'Vose'

    ses = 0

    matches = re.compile('<iframe src="(.*?)".*?<option value=(.*?)</option>', re.DOTALL).findall(data)

    if '>Seleccionar Servidor e Idioma<' in data:
        bloque = scrapertools.find_single_match(data, '>Seleccionar Servidor e Idioma<(.*?)</select>')

        matches2 = re.compile('<option value="(.*?)".*?data-index="(.*?)</option>', re.DOTALL).findall(bloque)

        matches = matches + matches2


    for url, idio in matches:
        ses += 1

        url = url.replace('\\/' ,'/')

        if url:
            if not url.startswith("http"):
                b64_decode = base64.b64decode(url)

                if b64_decode: url = scrapertools.find_single_match(str(b64_decode), '<iframe src="(.*?)"')

            if url.startswith('//'): url = 'https:' + url

            if not url.startswith("http"): continue

            if 'player.animeyt' in url: continue
            elif 'jetload.' in url: continue
            elif '.tioanime.' in url: continue
            elif '.fembed.' in url: continue

            url = url.replace('/altamina.online/', '/filemoon.sx/')
            url = url.replace('/elbailedeltroleo.site/', '/vgembed.com/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            if 'Latino' in idio: lang = 'Lat'
            elif 'Castellano' in idio: lang = 'Esp'
            elif 'Catalán' in idio: lang = 'Cat'
            elif 'Subtitulado' in idio: lang = 'Vose'

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, other = other ))

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

    if not servidor == 'directo':
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(url = url, server = servidor))

        return itemlist

    if url:
        if not url.startswith("http"): url = "https:" + url

        url = url.replace('&amp;', '&').replace("\\/", "/")

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(url = url, server = servidor))

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

