# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://animeyt.moe/'


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'anime/?status=&type=&order=', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_all', url = host + 'anime/?status=&type=&order=update', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Actualizados', action = 'list_all', url = host + 'anime/?status=&type=&order=latest', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'anime/?sub=&order=popular', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'anime/').data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, '> Genre(.*?)</ul>')

    matches = re.compile('value="(.*?)".*?<label for=".*?">(.*?)</label>').findall(data)

    for valor, title in matches:
        url = host + 'anime/' + '?genre%5B%5D=' + valor + '&status=&type=&sub=&order='

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

   
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Text Mode<(.*?)</div></div></div>')
    if not bloque: bloque = scrapertools.find_single_match(data, '<h1(.*?)</div></div></div>')

    matches = re.compile('<a href="(.*?)".*?title="(.*?)".*?data-src="(.*?)"').findall(bloque)

    for url, title, thumb in matches:
        if not url or not title: continue

        title = title.replace('(Sub EspaÃ±ol)', '(Sub Español)')

        titulo = title.replace('(Pelicula)', '').replace('(Sub Español)', '').replace('(Audio Latino)', '').replace('Audio castellano', '').strip()

        if '/pelicula/' in url:
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=titulo, infoLabels={'year': '-'} ))
        else:
            SerieName = titulo

            if 'Season' in titulo: SerieName = titulo.split("Season")[0]
            if 'Movie' in titulo: SerieName = titulo.split("Movie")[0]

            SerieName = SerieName.strip()

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, 
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
         bloque = scrapertools.find_single_match(data, '</article></div>(.*?)</i></a>')

         if 'Previous' in bloque:
              next_url = scrapertools.find_single_match(bloque, 'Previous.*?<a href="(.*?)"')
         else:
             next_url = scrapertools.find_single_match(bloque, '<a href="(.*?)"')

         if next_url:
             if 'page=' in next_url:
                 next_url = host + 'anime/' + next_url

                 itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

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

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimeYt', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for url, epis, title in matches[item.page * item.perpage:]:
        itemlist.append(item.clone( action='findvideos', url = url, title = title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

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

    ses = 0

    matches = re.compile('<iframe src="(.*?)"', re.DOTALL).findall(data)

    if '>Select Video Server<' in data:
        bloque = scrapertools.find_single_match(data, '>Select Video Server<(.*?)</select>')

        matches2 = re.compile('<option value="(.*?)"', re.DOTALL).findall(bloque)

        matches = matches + matches2


    for url in matches:
        ses += 1

        url = url.replace('\\/' ,'/')

        if url:
            if not url.startswith("http"):
                b64_decode = base64.b64decode(url)

                if b64_decode:
                    url = scrapertools.find_single_match(str(b64_decode), '<iframe src="(.*?)"')

            if url.startswith('//'): url = 'https:' + url

            if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue

            elif 'player.animeyt' in url: continue
            elif 'jetload.' in url: continue
            elif '.tioanime.' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            other = ''
            if servidor == 'directo': other = url

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = other ))

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

