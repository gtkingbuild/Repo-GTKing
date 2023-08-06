# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ennovelas.online/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/years/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Nuevos episodios', action = 'last_epis', url = host + 'episodes/', search_type = 'tvshow', text_color = 'olive' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action='paises', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('action', 'Acción'),
       ('aventura', 'Aventura'),
       ('comedy', 'Comedia'),
       ('crimen', 'Crimen'),
       ('drama', 'Drama'),
       ('reality-tv', 'Reality'),
       ('romance', 'Romance'),
       ('thriller', 'Thriller'),
       ('horror', 'Terror')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'genre/' + opc + '/', action = 'list_all', text_color='hotpink' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'América', action = 'list_all', url = host + 'category/novelas-americanas-online/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Chile', action = 'list_all', url = host + 'category/telenovelas-chilenas-online/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Colombia', action = 'list_all', url = host + 'category/novelas-colombianas-online/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'España', action = 'list_all', url = host + 'category/novelas-espanolas-online/', lang = 'Esp', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'México', action = 'list_all', url = host + 'category/novelas-mexicanas-online/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Perú', action = 'list_all', url = host + 'category/novelas-peruanas-online/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Tuquía', action = 'list_all', url = host + 'category/series-turcas-en-espanol-subtitulado', lang = 'Vose', text_color='moccasin' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        url = host + 'years/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color ='hotpink' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En 720', action = 'list_all', url = host + 'quality/720p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 1080', action = 'list_all', url = host + 'quality/1080p/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En Full HD', action = 'list_all', url = host + 'quality/full-hd/', text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        title = scrapertools.find_single_match(match, '<div class="title">(.*?)</div>')

        if not url or not title: continue

        title = title.replace('&#8211;', "").replace('&#8220;', "").replace('&#8221;', "").strip()
        title = title.replace('&#8216;', "").replace('&#8217;', "").strip()

        thumb = scrapertools.find_single_match(match, 'data-img="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(match, 'url\((.*?)\)')

        SerieName = title

        if " en (" in SerieName: SerieName = SerieName.split(" en ")[0]

        if " (" in SerieName: SerieName = SerieName.split(" (")[0]
        elif "(En Espanol)" in SerieName: SerieName = SerieName.split("(En Espanol)")[0]
        elif "En Español" in SerieName: SerieName = SerieName.split("En Español")[0]
        elif "[Español Subtitulado]" in SerieName: SerieName = SerieName.split("[Español Subtitulado]")[0]
        elif "[SUB Espanol]" in SerieName: SerieName = SerieName.split("[SUB Espanol]")[0]

        SerieName = SerieName.strip()

        if "Temporada" in SerieName: SerieName = SerieName.split("Temporada")[0]

        if "Capitulos" in SerieName: SerieName = SerieName.split("Capitulos")[0]
        elif "Capítulos" in SerieName: SerieName = SerieName.split("Capítulos")[0]

        if "Capitulo" in SerieName: SerieName = SerieName.split("Capitulo")[0]
        elif "Capítulo" in SerieName: SerieName = SerieName.split("Capítulo")[0]

        SerieName = SerieName.strip()

        lang = ''
        if 'subtitulado' in title.lower(): lang = 'Vose'

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, lang=lang,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, 'class="page-numbers current">.*?href="(.*?)"')

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-img="(.*?)"')

        season = scrapertools.find_single_match(match, '>Temporada(.*?)</span>').strip()
        if not season: season = 1

        epis = scrapertools.find_single_match(match, '<span>Cap.*?<span>(.*?)</span>')
        if not epis: epis = 1

        title = title.replace('&#8211;', "").replace('&#8220;', "").replace('&#8221;', "").strip()

        SerieName = title

        if " en (" in SerieName: SerieName = SerieName.split(" en ")[0]

        if " (" in SerieName: SerieName = SerieName.split(" (")[0]
        elif "(En Espanol)" in SerieName: SerieName = SerieName.split("(En Espanol)")[0]
        elif "En Español" in SerieName: SerieName = SerieName.split("En Español")[0]
        elif "[Español Subtitulado]" in SerieName: SerieName = SerieName.split("[Español Subtitulado]")[0]
        elif "[SUB Espanol]" in SerieName: SerieName = SerieName.split("[SUB Espanol]")[0]

        SerieName = SerieName.strip()

        if "Temporada" in SerieName: SerieName = SerieName.split("Temporada")[0]

        if "Capitulos" in SerieName: SerieName = SerieName.split("Capitulos")[0]
        elif "Capítulos" in SerieName: SerieName = SerieName.split("Capítulos")[0]

        if "Capitulo" in SerieName: SerieName = SerieName.split("Capitulo")[0]
        elif "Capítulo" in SerieName: SerieName = SerieName.split("Capítulo")[0]

        SerieName = SerieName.strip()

        title = title.replace('Capitulo', '[COLOR goldenrod]Capitulo[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Capítulo[/COLOR]')

        lang = ''
        if 'Subtitulado' in title: lang = 'Vose'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, lang = lang, infoLabels={'year': '-'},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, 'class="page-numbers current">.*?href="(.*?)"')

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'last_epis', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('data-season="(.*?)".*?>Season(.*?)</li>', re.DOTALL).findall(data)

    if not matches:
        bloque = scrapertools.find_single_match(data, '"Seasons & Episodes"(.*?)</ul>')

        d_season = scrapertools.find_single_match(data, 'data-season="(.*?)"')

        if bloque:
            epis = re.compile('<a class="epNum"(.*?)</a>', re.DOTALL).findall(bloque)

            if epis:
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR tan]Sin temporadas[/COLOR]')
                item.d_season = d_season
                item.page = 0
                item.contentType = 'season'

                season = scrapertools.find_single_match(item.url, '-temporada-(.*?)-')
                if not season: item.contentSeason = 1
                else: item.contentSeason = season

                itemlist = episodios(item)
                return itemlist

        return itemlist

    for d_season, numtempo in matches:
        numtempo = numtempo.strip()

        if not numtempo: numtempo = '1'

        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.d_season = d_season
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, d_season = d_season, page = 0, contentType = 'season', contentSeason = numtempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    if item.d_season:
        data = do_downloadpage(host + 'wp-content/themes/vo2022_en/temp/ajax/seasons.php?seriesID=' + item.d_season, headers = {'Referer': item.url, 'X-Requested-With': 'XMLHttpRequest'}, raise_weberror = False)

        if not data: data = do_downloadpage(host + 'wp-content/themes/vo2022/temp/ajax/seasons.php?seriesID=' + item.d_season, headers = {'Referer': item.url, 'X-Requested-With': 'XMLHttpRequest'})

        epis = re.compile('<a class="epNum"(.*?)</a>', re.DOTALL).findall(data)
        if not epis: data = do_downloadpage(item.url)
    else:
        data = do_downloadpage(item.url)

    matches = re.compile('<a class="epNum"(.*?)</a>', re.DOTALL).findall(data)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('EnNovelasOnline', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EnNovelasOnline', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EnNovelasOnline', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EnNovelasOnline', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('EnNovelasOnline', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('EnNovelasOnline', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#8211;', "").strip()

        epis = scrapertools.find_single_match(match, '<span>(.*?)</span>')
        if not epis: epis = 1

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        if 'EP ' in title: titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' +  str(item.contentSerieName)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    values = scrapertools.find_multiple_matches(data, '<form method="post".*?action="(.*?)".*?<input type="hidden".*?name="(.*?)".*?value="(.*?)"')

    ses = 0

    for link, type, value in values:
        ses += 1

        if not link: continue

        if type == 'watch': post = {'watch': str(value)}
        else: post = {'download': str(value)}

        data1 = do_downloadpage(link, post = post, headers = {'Referer': item.url} )

        matches = scrapertools.find_multiple_matches(data1, "<iframe src='(.*?)'")
        if not matches: matches = scrapertools.find_multiple_matches(data1, '<iframe src="(.*?)"')
        if not matches: matches = scrapertools.find_multiple_matches(data1, '<td>Server.*?href="(.*?)"')

        for url in matches:
            if '.ennovelas.' in url: continue
            elif '/tomatomatela.' in url: continue
            elif '/watching.' in url: continue
            elif '/novelas360.' in url: continue
            elif '/telegram.' in url: continue

            if url.startswith('//'): url = 'https:' + url

            if 'api.mycdn.moe/sblink.php?id=' in url: url = url.replace('api.mycdn.moe/sblink.php?id=', 'sbanh.com/e/')

            elif 'api.mycdn.moe/fembed.php?id=' in url: url = url.replace('api.mycdn.moe/fembed.php?id=', 'feurl.com/v/')
            elif 'api.mycdn.moe/furl.php?id=' in url: url = url.replace('api.mycdn.moe/furl.php?id=', 'feurl.com/v/')

            elif 'api.mycdn.moe/uqlink.php?id=' in url: url = url.replace('api.mycdn.moe/uqlink.php?id=', 'uqload.com/embed-')

            elif 'api.mycdn.moe/dourl.php?id=' in url: url = url.replace('api.mycdn.moe/dourl.php?id=', 'dood.to/e/')

            elif 'api.mycdn.moe/dl/?uptobox=' in url: url = url.replace('api.mycdn.moe/dl/?uptobox=', 'uptobox.com/')

            elif url.startswith('http://vidmoly'): url = url.replace('http://vidmoly', 'https://vidmoly').replace('/w/', '/embed-')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if item.lang == 'Esp': lang = 'Esp'
            elif item.lang == 'Vose': lang = 'Vose'
            else: lang = 'Lat'

            other = ''
            if type == 'download': other = 'D'

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other ))

    t_link = scrapertools.find_single_match(data, 'var vo_theme_dir = "(.*?)"')
    id_link = scrapertools.find_single_match(data, 'vo_postID = "(.*?)"')

    if t_link and id_link:
        i = 0

        while i <= 5:
           data2 = do_downloadpage(t_link + '/temp/ajax/iframe.php?id=' + id_link + '&video=' + str(i), headers = {'Referer': item.url, 'x-requested-with': 'XMLHttpRequest'} )

           data2 = data2.strip()

           if not data2: break

           u_link = scrapertools.find_single_match(data2, '<iframe.*?src="(.*?)"')
           if not u_link: u_link = scrapertools.find_single_match(data2, '<IFRAME.*?SRC="(.*?)"')

           if u_link.startswith('//'): u_link = 'https:' + u_link

           if u_link:
               ses += 1

               if '/ennovelas.' in u_link: u_link = ''

           if u_link:
               if u_link.startswith('https://vk.com/'): u_link = u_link.replace('&amp;', '&')

               servidor = servertools.get_server_from_url(u_link)
               servidor = servertools.corregir_servidor(servidor)

               u_link = servertools.normalize_url(servidor, u_link)

               if item.lang == 'Esp': lang = 'Esp'
               elif item.lang == 'Vose': lang = 'Vose'
               else: lang = 'Lat'

               if not servidor == 'directo':
                   itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = u_link, server = servidor, language = lang, other = 'P' ))

           i += 1

    # ~ Downloads
    if not itemlist:
        matches = scrapertools.find_multiple_matches(data, '<td>Server.*?href="(.*?)"')

        for url in matches:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if item.lang == 'Esp': lang = 'Esp'
            elif item.lang == 'Vose': lang = 'Vose'
            else: lang = 'Lat'

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = 'D' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

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

