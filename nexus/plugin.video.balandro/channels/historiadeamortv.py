# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://w.historiadeamor.org/'


def do_downloadpage(url, post=None, headers=None):
    raise_weberror = True
    if '/years/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
        except:
            pass

    if '<title>Just a moment...</title>' in data:
        if not '/search/' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item( channel='helper', action='show_help_historiadeamortv', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))
    itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(Item( channel='helper', action='show_help_historiadeamortv', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por país', action='paises', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(Item( channel='helper', action='show_help_historiadeamortv', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'telenovelas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Capítulos', action = 'list_all', url = host + 'capitulos-comoletos/', group = 'capis', search_type = 'tvshow', text_color = 'olive' ))

    itemlist.append(item.clone( title = 'Mejores capítulos', action='list_all', url = host + 'las-mejores-series-turcas-en-espanol/', group = 'capis', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Turcas', action='list_all', url = host + 'series-turcas-gratishd/', search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action='paises', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'tvshow' ))

    return itemlist


def mainlist_animes(item):
    logger.info()
    itemlist = []

    itemlist.append(Item( channel='helper', action='show_help_historiadeamortv', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes/', group = 'anime', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', group = 'anime', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action='paises', group = 'anime', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', group = 'anime', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', group = 'anime',  search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else:
       if item.group == 'anime': text_color = 'springgreen'
       else: text_color = 'hotpink'

    opciones = [
       ('action', 'Acción'),
       ('adventure', 'Aventura'),
       ('animation', 'Animación'),
       ('comedia', 'Comedia'),
       ('crimen', 'Crimen'),
       ('drama', 'Drama'),
       ('fantasy', 'Fantasía'),
       ('misterio', 'Misterio'),
       ('romance', 'Romance'),
       ('thriller', 'Thriller')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'genre/' + opc + '/', action = 'list_all', text_color = text_color ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Brasil', action = 'list_all', url = host + 'country/brazil/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Chile', action = 'list_all', url = host + 'country/chile/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Colombia', action = 'list_all', url = host + 'country/colombia/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Japón', action = 'list_all', url = host + 'country/japan/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'México', action = 'list_all', url = host + 'country/mexico/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Perú', action = 'list_all', url = host + 'country/peru/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Tuquía', action = 'list_all', url = host + 'series-turcas-gratishd/', text_color='moccasin' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else:
       if item.group == 'anime': text_color = 'springgreen'
       else: text_color = 'hotpink'

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        url = host + 'years/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', text_color = text_color ))

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

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        if 'En Vivo' in title or 'en Vivo' in title or 'en vivo' in title: continue

        thumb = scrapertools.find_single_match(match, 'data-img="(.*?)"')
        if not thumb:
            thumb = scrapertools.find_single_match(match, '<div class="posterThumb">.*?url(.*?)"')
            thumb = thumb.replace('(', '').replace(');', '').strip()

        title = title.replace('&#8211;', "").replace('&#8220;', "").replace('&#8221;', "").strip()

        title = title.replace('Telenovelas Gratis', '').replace('Telenovelas  Gratis', '').replace('Telenovelas', '').replace('Gratis', '').replace('Ver ', '').strip()
        title = title.replace('Pelicula Completa Online', '').replace('Pelicula Completa online', '').replace('Completa online', '').strip()

        if 'Capitulos Completos Online' in title: title = scrapertools.find_single_match(title, '(.*?)Capitulos Completos Online').strip()
        if 'Completos Online' in title: title = scrapertools.find_single_match(title, '(.*?)Completos Online').strip()
        if 'Completo' in title: title = scrapertools.find_single_match(title, '(.*?)Completo').strip()
        if 'Online' in title: title = scrapertools.find_single_match(title, '(.*?)Online').strip()
        if 'Capitulos' in title: title = scrapertools.find_single_match(title, '(.*?)Capitulos').strip()
        if 'HD' in title: title = scrapertools.find_single_match(title, '(.*?)HD').strip()

        title = title.replace(' ❤️', '').replace(' ✔️', '').strip()

        SerieName = title

        if "(SUBTITULO ESPAÑOL)" in SerieName: SerieName = SerieName.split("(SUBTITULO ESPAÑOL)")[0]
        elif "(SUBTITULADO ESPAÑOL)" in SerieName: SerieName = SerieName.split("(SUBTITULADO ESPAÑOL)")[0]

        elif "En Español" in SerieName: SerieName = SerieName.split("En Español")[0]
        elif "en Español" in SerieName: SerieName = SerieName.split("en Español")[0]
        elif "(En Espanol)" in SerieName: SerieName = SerieName.split("(En Espanol)")[0]
        elif "[Español Subtitulado]" in SerieName: SerieName = SerieName.split("[Español Subtitulado]")[0]
        elif "[SUB Espanol]" in SerieName: SerieName = SerieName.split("[SUB Espanol]")[0]
        elif "(English Subtitles)" in SerieName: SerieName = SerieName.split("(English Subtitles)")[0]
        elif "English Subtitles" in SerieName: SerieName = SerieName.split("English Subtitles")[0]

        SerieName = SerieName.strip()

        if "Temporada" in SerieName: SerieName = SerieName.split("Temporada")[0]

        if "Capitulos" in SerieName: SerieName = SerieName.split("Capitulos")[0]
        elif "Capítulos" in SerieName: SerieName = SerieName.split("Capítulos")[0]
        elif "Episodes" in SerieName: SerieName = SerieName.split("Episodes")[0]

        if "Capitulo" in SerieName: SerieName = SerieName.split("Capitulo")[0]
        elif "Capítulo" in SerieName: SerieName = SerieName.split("Capítulo")[0]
        elif "Episode" in SerieName: SerieName = SerieName.split("Episode")[0]

        if " –" in SerieName: SerieName = scrapertools.find_single_match(SerieName, '(.*?) –').strip()

        if " |" in SerieName: SerieName = SerieName.replace(' |', '').strip()

        SerieName = SerieName.strip()

        tipo = 'movie' if '/movies/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = SerieName, infoLabels={'year': '-'} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            lang = ''
            if 'subtitulado' in title.lower() or 'subtitulo' in title.lower(): lang = 'Vose'

            if '/search/' in item.url or item.group == 'capis':
                cap = False

                if 'Capitulos' in title or 'Capítulos' in title or 'Episodes' in title: pass

                elif 'Capitulo' in title or 'Capítulo' in title or 'Episode' in title: cap = True

                if 'EN VIVO' in title: title = title.replace('EN VIVO', '').strip()

                if cap:
                    season = scrapertools.find_single_match(title, 'Temporada(.*?)Capítulo').strip()
                    if not season: season = scrapertools.find_single_match(title, 'Temporada(.*?)Capitulo').strip()
                    if not season: season = 1

                    epis = scrapertools.find_single_match(match, '<span>Cap.*?<span>(.*?)</span>')
                    if not epis: epis = 1

                    title = title.replace('Capitulo', '[COLOR goldenrod]Capitulo[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Capítulo[/COLOR]').replace('Episode', '[COLOR goldenrod]Episode[/COLOR]')

                    itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, lang = lang, fmt_sufijo=sufijo, infoLabels={'year': '-'},
                                                contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))
                    continue

                else:
                    title = title.replace('Temporada', '[COLOR tan]Temporada[/COLOR]')

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, lang = lang, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, "<div class='pagination'>.*?<span class='current'>.*?a href='(.*?)'")

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Temporadas y episodios<(.*?)</div></div></div>')

    if bloque:
        block = scrapertools.find_single_match(data, '<ul class="eplist">(.*?)</ul>')

        epis = re.compile('<a class="epNum"(.*?)</a>', re.DOTALL).findall(block)

        if epis:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR tan]Sin temporadas[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = 1
            itemlist = episodios(item)

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Temporadas y episodios<(.*?)</div></div></div>')

    block = scrapertools.find_single_match(data, '<ul class="eplist">(.*?)</ul>')

    matches = re.compile('<a class="epNum"(.*?)</a>', re.DOTALL).findall(block)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('HistoriadeAmorTv', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HistoriadeAmorTv', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HistoriadeAmorTv', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HistoriadeAmorTv', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HistoriadeAmorTv', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('HistoriadeAmorTv', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"').strip()

        if not url or not title: continue

        title = title.replace('&#8211;', "").strip()

        epis = scrapertools.find_single_match(match, '<span>(.*?)</span>')
        if not epis: epis = 1

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + item.contentSerieName

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo,  contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

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

    if item.lang == 'Vose': lang = 'Vose'
    else: lang = 'Lat'

    data = do_downloadpage(item.url)

    values = scrapertools.find_multiple_matches(data, '<input type="hidden".*?name="(.*?)".*?value="(.*?)"')

    ses = 0

    for type, value in values:
        if type == 'watch': post = {'watch': str(value), 'submit': ''}
        else: post = {'download': str(value), 'submit': ''}

        data1 = do_downloadpage( host + 'tokyvideo.php', post = post, headers = {'Referer': item.url + '?do=watch'} )

        matches = scrapertools.find_multiple_matches(data1, "<iframe src='(.*?)'")
        if not matches: matches = scrapertools.find_multiple_matches(data1, '<td>Server.*?href="(.*?)"')

        for url in matches:
            ses += 1

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

            other = ''
            if type == 'download': other = 'D'

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other ))

    if not itemlist:
        data2 = do_downloadpage(item.url + '?do=watch')

        t_link = scrapertools.find_single_match(data2, 'var vo_theme_dir = "(.*?)"')
        id_link = scrapertools.find_single_match(data2, 'vo_postID = "(.*?)"')

        if t_link and id_link:
            i = 0

            while i <= 5:
               data3 = do_downloadpage(t_link + '/temp/ajax/iframe.php?id=' + id_link + '&video=' + str(i), headers = {'Referer': item.url, 'x-requested-with': 'XMLHttpRequest'} )

               data3 = data2.strip()

               if not data3: break

               u_link = scrapertools.find_single_match(data3, '<iframe.*?src="(.*?)"')
               if not u_link: u_link = scrapertools.find_single_match(data3, '<IFRAME.*?SRC="(.*?)"')

               if u_link.startswith('//'): u_link = 'https:' + u_link

               if u_link:
                   ses += 1

                   if '/historiadeamortv.' in u_link: u_link = ''

                   if u_link:
                       servidor = servertools.get_server_from_url(u_link)
                       servidor = servertools.corregir_servidor(servidor)

                       u_link = servertools.normalize_url(servidor, u_link)

                       if item.lang == 'Esp': lang = 'Esp'
                       elif item.lang == 'Vose': lang = 'Vose'
                       else: lang = 'Lat'

                       if not servidor == 'directo':
                          itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = u_link, server = servidor, language = lang, other = 'P' ))

               i += 1

        vo_postID = id_link

        if vo_postID:
            data4 = do_downloadpage(host + 'emb/?vid=' + vo_postID )

            url = scrapertools.find_single_match(data4, '<iframe src="(.*?)"')

            if url:
                ses += 1

                if url.startswith('//'): url = 'https:' + url

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                if not servidor == 'directo':
                    itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = 'E' ))

    # ~ Downloads No hay enlaces nunca  ---> data5 = item.url + '?do=downloads'

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'search/' + texto.replace(" ", "+") + '/'
       return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

