# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ennovelas.at/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action='paises', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por plataforma', action='plataformas', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('comedy', 'Comedia'),
       ('crimen', 'Crimen'),
       ('drama', 'Drama'),
       ('familia', 'Familia'),
       ('misterio', 'Misterio'),
       ('reality', 'Reality'),
       ('romance', 'Romance'),
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'genre/' + opc + '/', action = 'list_all', text_color='hotpink' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'América', action = 'list_all', url = host + 'country/usa/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Chile', action = 'list_all', url = host + 'genre/telenovelas-chilenas/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Colombia', action = 'list_all', url = host + 'genre/novelas-colombianas/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'España', action = 'list_all', url = host + 'genre/novelas-espanolas/', lang = 'Esp', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'México', action = 'list_all', url = host + 'genre/novelas-mexicanas/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Perú', action = 'list_all', url = host + 'genre/novelas-peruanas/', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Tuquía', action = 'list_all', url = host + 'country/tr/', lang = 'Vose', text_color='hotpink' ))
    itemlist.append(item.clone( title = 'Venezuela', action = 'list_all', url = host + 'genre/novelas-venezolanas/', text_color='hotpink' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    productoras = [
        ('amazon-prime-video', 'Amazon Prime Vídeo'),
        ('antena-3', 'Antena 3'),
        ('apple-tv', 'Apple TV'),
        ('atresplayer-premium', 'Atresplayer Premium'),
        ('canal', 'Canal+'),
        ('cbc-television', 'CBC Television'),
        ('cbs', 'Cbs'),
        ('caracol-tv', 'Caracol TV'),
        ('disney', 'Disney+'),
        ('fox', 'FOX'),
        ('globoplay', 'Globoplay'),
        ('hbo', 'HBO'),
        ('hulu', 'Hulu'),
        ('las-estrellas', 'Las Estrellas'),
        ('nbc', 'NBC'),
        ('netflix', 'Netflix'),
        ('prime-video', 'Prime Vídeo'),
        ('rcn', 'Rcn'),
        ('rede-globo', 'Rede Globo'),
        ('showtime', 'Showtime'),
        ('starz', 'Starz'),
        ('telemundo', 'Telemundo')
        ]

    for opc, tit in productoras:
        url = host + 'network/' + opc + '/'

        itemlist.append(item.clone( title = tit, action = 'list_all', url = url, text_color = 'moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        if '>Movie<' in match: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        title = title.replace('&#8211;', "").replace('&#8220;', "").replace('&#8221;', "").replace('&#038;', "").strip()

        SerieName = title

        if " en (" in SerieName: SerieName = SerieName.split(" en ")[0]

        if " (" in SerieName: SerieName = SerieName.split(" (")[0]
        elif "(En Espanol)" in SerieName: SerieName = SerieName.split("(En Espanol)")[0]
        elif "en Espanol" in SerieName: SerieName = SerieName.split("en Espanol")[0]
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

        year = scrapertools.find_single_match(match, '<span class="addyear">(.*?)</span>')
        if not year: year = '-'
        else:
           title = title.replace('(' + year + ')', '').strip()

        lang = ''
        if 'subtitulado' in title.lower(): lang = 'Vose'

        title = title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').strip()

        if '-capitulo-' in url:
            epis = scrapertools.find_single_match(url, '-capitulo-(.*?)-')

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, lang = lang,
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epis, infoLabels={'year': year}  ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, lang=lang,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span aria-current="page".*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, '>Latest Episodes<(.*?)Copyright © Ennovelas')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        season = scrapertools.find_single_match(match, '<i class="dot"></i>.*?S(.*?)EP').strip()
        if not season: season = 1

        epis = scrapertools.find_single_match(match, '<i class="dot"></i>.*?EP(.*?)<')
        if not epis: epis = 1

        title = title.replace('&#8211;', "").replace('&#8220;', "").replace('&#8221;', "").replace('&#038;', "").strip()

        SerieName = title

        if " en (" in SerieName: SerieName = SerieName.split(" en ")[0]

        if " (" in SerieName: SerieName = SerieName.split(" (")[0]
        elif "(En Espanol)" in SerieName: SerieName = SerieName.split("(En Espanol)")[0]
        elif "en Espanol" in SerieName: SerieName = SerieName.split("en Espanol")[0]
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

        year = scrapertools.find_single_match(match, '<span class="addyear">(.*?)</span>')
        if not year: year = '-'
        else:
           title = title.replace('(' + year + ')', '').strip()

        title = title.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Epis.[/COLOR]')

        title = str(season) +'x' + str(epis) + ' ' + title

        lang = ''
        if 'Subtitulado' in title: lang = 'Vose'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, lang = lang, infoLabels={'year': year},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if config.get_setting('channels_seasons', default=True):
        title = 'Temporadas'

        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]' + title + '[/COLOR]')

    item.page = 0
    item.contentType = 'season'
    item.contentSeason = 1
    itemlist = episodios(item)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<h2>Episodes(.*?)<h3>")

    matches = re.compile('data-ID="(.*?)</li>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    if item.page == 0 and item.perpage == 50:
        sum_parts = num_matches

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('EnNovelasTv', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
            if sum_parts > 50:
                platformtools.dialog_notification('TeleNovela', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TeleNovela', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TeleNovela', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TeleNovela', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TeleNovela', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('TeleNovela', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, '<div class="epl-title">(.*?)</div> ')

        if not url or not title: continue

        title = title.replace('Completos en HD', '').replace('Completos en Hd', '').replace('Completo en HD', '').replace('Completo en Hd', '').strip()

        season = scrapertools.find_single_match(match, '<div class="epl-num">S(.*?)EP').strip()
        if not season: season = 1

        epis = scrapertools.find_single_match(match, '<div class="epl-num">.*?EP(.*?)</div>').strip()
        if not epis: epis = 1

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title.replace('Temporada', '[COLOR tan]Temp.[/COLOR]').strip()

        titulo = titulo.replace('Capitulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('Capítulo', '[COLOR goldenrod]Epis.[/COLOR]')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

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

    if item.lang == 'Esp': lang = 'Esp'
    elif item.lang == 'Vose': lang = 'Vose'
    else: lang = 'Lat'

    data = do_downloadpage(item.url)

    ses = 0

    matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')
    if not matches: matches = scrapertools.find_multiple_matches(data, "<iframe.*?src='(.*?)'")

    for url in matches:
        ses += 1

        url = url.strip()

        if '/likessb.' in url: continue
        elif '/argtesa.' in url: continue
        elif '/ennovelas.' in url: continue

        if 'api.mycdn.moe/uqlink.php?id=' in url: url = url.replace('api.mycdn.moe/uqlink.php?id=', 'uqload.com/embed-')

        elif 'api.mycdn.moe/dourl.php?id=' in url: url = url.replace('api.mycdn.moe/dourl.php?id=', 'dood.to/e/')

        elif 'api.mycdn.moe/dl/?uptobox=' in url: url = url.replace('api.mycdn.moe/dl/?uptobox=', 'uptobox.com/')

        elif url.startswith('http://vidmoly/'): url = url.replace('http://vidmoly/w/', 'https://vidmoly/embed-').replace('http://vidmoly/', 'https://vidmoly/')

        elif url.startswith('https://sr.ennovelas.net/'): url = url.replace('/sr.ennovelas.net/', '/waaw.to/')
        elif url.startswith('https://video.ennovelas.net/'): url = url.replace('/video.ennovelas.net/', '/waaw.to/')
        elif url.startswith('https://reproductor.telenovelas-turcas.com.es/'): url = url.replace('/reproductor.telenovelas-turcas.com.es/', '/waaw.to/')
        elif url.startswith('https://novelas360.cyou/player/'): url = url.replace('/novelas360.cyou/player/', '/waaw.to/')
        elif url.startswith('https://novelas360.cyou/'): url = url.replace('/novelas360.cyou/', '/waaw.to/')

        url = url.replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        if servidor == 'directo':
            if not config.get_setting('developer_mode', default=False): continue
            else:
               other = url.split("/")[2]
               other = other.replace('https:', '').strip()

        itemlist.append(Item( channel=item.channel, action = 'play', server = servidor, url = url, language = lang, other = other.capitalize() ))

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

