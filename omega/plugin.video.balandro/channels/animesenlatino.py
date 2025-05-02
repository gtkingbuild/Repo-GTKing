# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.animeslatino.club/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/ano/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, raise_weberror=raise_weberror).data

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

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'all', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes-online', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    data = scrapertools.find_single_match(data, 'Por género<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)".*?title="(.*?)"').findall(data)

    for url, title in matches:
        if 'Adulto' in title:
           if config.get_setting('descartar_xxx', default=False): continue

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    url_anio = url = host + 'animes-online/ano/'

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        url = url_anio + str(x)

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)<span class="navigation">')
    if not bloque: bloque = scrapertools.find_single_match(data, '<h1(.*?)<div class="navigation">')

    matches = re.compile('<div class="short_in">(.*?)</div></div></div>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' data-src="(.*?)"')

        thumb = host[:-1] + thumb

        year = scrapertools.find_single_match(match, '<div class="meta label_quel-hd">(.*?)</div>')
        if not year: year = '-'

        title = title.replace('ver serie ', '').replace('ver ', '').strip()

        anio = scrapertools.find_single_match(match, '(\d{4})')
        if anio:
            title = title.replace('('+ anio +')', '').strip()

        title = title.replace('&#039;', "'").replace('&#8217;', "'").replace('&#8211;', '').replace('&#215;', 'x').replace('&quot;', '')

        SerieName = corregir_SerieName(title)

        title = title.replace('Season', '[COLOR coral]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        if ' 2nd ' in match: season = 2
        elif ' 3rd ' in match: season = 3
        elif ' 4th ' in match: season = 4
        elif ' 5th ' in match: season = 5
        elif ' 6th ' in match: season = 6
        elif ' 7th ' in match: season = 7
        elif ' 8th ' in match: season = 8
        elif ' 9th ' in match: season = 9
        else: season = 1

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                    contentType = 'tvshow', contentSerieName = SerieName, contentSeason=season, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
         if '<span class="navigation">' in data:
             next_page = scrapertools.find_single_match(data, '<span class="navigation">.*?</span>.*?<a rel="nofollow".*?href="(.*?)"')
             if not next_page: next_page = scrapertools.find_single_match(data, '<span class="navigation">.*?</span>.*?<a rel="nonfollow".*?href="(.*?)"')

             if next_page:
                 if 'page=' in next_page or '/page/' in next_page:
                     itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>ÚLTIMOS CAPÍTULO AÑADIDOS<.*?</aside>')

    matches = re.compile('<a class="upd-in"(.*?)</div></div></div>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' data-src="(.*?)"')

        thumb = host[:-1] + thumb

        year = scrapertools.find_single_match(match, '<div class="meta label_quel-hd">(.*?)</div>')
        if not year: year = '-'

        anio = scrapertools.find_single_match(match, '(\d{4})')
        if anio:
            title = title.replace('('+ anio +')', '').strip()

        title = title.replace('&#039;', "'").replace('&#8217;', "'").replace('&#8211;', '').replace('&#215;', 'x').replace('&quot;', '')

        SerieName = corregir_SerieName(title)

        title = title.replace('Season', '[COLOR coral]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        if ' 2nd ' in match: season = 2
        elif ' 3rd ' in match: season = 3
        elif ' 4th ' in match: season = 4
        elif ' 5th ' in match: season = 5
        elif ' 6th ' in match: season = 6
        elif ' 7th ' in match: season = 7
        elif ' 8th ' in match: season = 8
        elif ' 9th ' in match: season = 9
        else: season = 1

        epis = scrapertools.find_single_match(match, '<span class="episodes-main">(.*?)</span>')
        if not epis: epis = 1

        titulo = '%s - %s' % (title, epis)

        titulo = '[COLOR goldenrod]Epis. [/COLOR]' + str(epis) + ' ' + titulo.replace('Episodio', '').strip()

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb,
                                            contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber=epis,
                                            infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '</div><div align="center">(.*?)</div></div></div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?<span class="name">Capítulo(.*?)</span>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('AnimesEnLatino', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('AnimesEnLatino', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimesEnLatino', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimesEnLatino', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimesEnLatino', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('AnimesEnLatino', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('AnimesEnLatino', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, epis in matches[item.page * item.perpage:]:
        epis = epis.strip()

        if not epis: epis = 1

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

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

    lang = 'Vose'

    ses = 0

    matches = re.compile('data-hash="(.*?)".*?<span class="serv">(.*?)</span>', re.DOTALL).findall(data)

    for hash, srv in matches:
        if not hash: continue

        ses += 1

        srv = srv.lower()

        servidor = servertools.corregir_servidor(srv)

        other = ''
        other = servertools.corregir_other(srv)

        if servidor == other: other = ''

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server=servidor, url=item.url, hash=hash, language=lang, other=other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    token = scrapertools.find_single_match(data, '<input type="hidden" name="_token" value="(.*?)"')

    if not token: return itemlist

    post = {'hash': item.hash, '_token': token}

    data = do_downloadpage(host + 'hashembedlink', post = post, headers = {'Referer': item.url} )

    url = scrapertools.find_single_match(data, '"link":"(.*?)"')

    if url:
        if not url.startswith("http"): url = "https:" + url

        url = url.replace('&amp;', '&').replace("\\/", "/")

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def corregir_SerieName(SerieName):
    logger.info()

    if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]

    if '(OVA)' in SerieName: SerieName = SerieName.split("(OVA)")[0]

    if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
    if 'season' in SerieName: SerieName = SerieName.split("season")[0]

    if 'Specials ' in SerieName: SerieName = SerieName.split("Specials ")[0]

    if ' S1 ' in SerieName: SerieName = SerieName.split(" S1 ")[0]
    elif ' S2 ' in SerieName: SerieName = SerieName.split(" S2 ")[0]
    elif ' S3 ' in SerieName: SerieName = SerieName.split(" S3 ")[0]
    elif ' S4 ' in SerieName: SerieName = SerieName.split(" S4 ")[0]
    elif ' S5 ' in SerieName: SerieName = SerieName.split(" S5 ")[0]
    elif ' S6 ' in SerieName: SerieName = SerieName.split(" S6 ")[0]
    elif ' S7 ' in SerieName: SerieName = SerieName.split(" S7 ")[0]
    elif ' S8 ' in SerieName: SerieName = SerieName.split(" S8 ")[0]
    elif ' S9 ' in SerieName: SerieName = SerieName.split(" S9 ")[0]

    if ' T1 ' in SerieName: SerieName = SerieName.split(" T1 ")[0]
    elif ' T2 ' in SerieName: SerieName = SerieName.split(" T2 ")[0]
    elif ' T3 ' in SerieName: SerieName = SerieName.split(" T3 ")[0]
    elif ' T4 ' in SerieName: SerieName = SerieName.split(" T4 ")[0]
    elif ' T5 ' in SerieName: SerieName = SerieName.split(" T5 ")[0]
    elif ' T6 ' in SerieName: SerieName = SerieName.split(" T6 ")[0]
    elif ' T7 ' in SerieName: SerieName = SerieName.split(" T7 ")[0]
    elif ' T8 ' in SerieName: SerieName = SerieName.split(" T8 ")[0]
    elif ' T9 ' in SerieName: SerieName = SerieName.split(" T9 ")[0]

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
        item.url = host + 'recherche?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

