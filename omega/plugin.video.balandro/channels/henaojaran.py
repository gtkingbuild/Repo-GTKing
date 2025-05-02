# -*- coding: utf-8 -*-

import ast, re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


from lib.pyberishaes import GibberishAES


host = 'https://vwv.henaojara.net/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://wvw.henaojara.net/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not headers: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

    if '<title>Error 404</title>' in data:
        if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('HenaOjaraN', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

        timeout = config.get_setting('channels_repeat', default=30)

        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes?tipo=anime', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_last', url = host, search_type = 'tvshow', text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'animes?estado=en-emision', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Finalizados', action = 'list_all', url = host + 'animes?tipo=anime&estado=finalizado', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + 'animes?tipo=especial', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'animes?tipo=especial,ova', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Proximamente', action = 'list_all', url = host + 'animes?estado=proximamente', search_type = 'tvshow', text_color='yellowgreen' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'animes?tipo=pelicula', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'animes')
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, '>Género(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'data-value="(.*?)".*?>(.*?)</li><')

    for value, title in matches:
        url = host + 'animes?genero=' + value

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color='springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3.*?title=".*?">(.*?)</a>')
        if not title: title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('#8217;', "'")

        nro_season = ''
        if 'Temporada' in title:
            nro_season = scrapertools.find_single_match(title, 'Temporada (.*?) ').strip()
            if nro_season: nro_season = ' T' + nro_season

        title = title.replace('#8217;', "'")

        year = scrapertools.find_single_match(title, '(\d{4})')
        if year: title = title.replace('(' + year + ')', '').strip()

        SerieName = corregir_SerieName(title)

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        url = host[:-1] + url.replace('./', '/')

        tipo = 'movie' if '?tipo=pelicula' in item.url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

            titulo = title + nro_season

            itemlist.append(item.clone( action = 'episodios', url= url, title=titulo, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            PeliName = title

            if 'Movie' in PeliName: PeliName = PeliName.split("Movie")[0]

            PeliName = PeliName.replace('Peliculas', '').replace('Pelicula', '').strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, _peli = True, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=PeliName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pag">' in data:
            next_page = scrapertools.find_single_match(data,'<ul class="pag">.*?<a class="se".*?</a>.*?href="(.*?)"')

            if next_page:
                if '&pag=' in next_page:
                    next_page = host[:-1] + next_page

                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Nuevos Animes Agregados<(.*?)>Animes En emisión<')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3.*?title=".*?">(.*?)</a>')
        if not title: title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('#8217;', "'")

        year = scrapertools.find_single_match(match, '<span class="Year">.*?-(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(title, '(\d{4})')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        SerieName = corregir_SerieName(title)

        PeliName = SerieName

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        epis = scrapertools.find_single_match(match, '<span class="ClB">(.*?)</span>')

        url = host[:-1] + url.replace('./', '/')

        tipo = 'movie' if epis == '0' else 'tvshow'

        if tipo == 'tvshow':
            temp = scrapertools.find_single_match(url, '/season/.*?hd-(.*?)/')

            title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

            if temp:
                title = 'Season ' + str(temp) + ' ' + title
                title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': year} ))

        if tipo == 'movie':
            PeliName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", title).strip()

            if 'Movie' in PeliName: PeliName = PeliName.split("Movie")[0]

            PeliName = PeliName.replace('Peliculas', '').replace('Pelicula', '').strip()

            title = '[COLOR deepskyblue]Film [/COLOR]' + title

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, _peli = True,
                                        contentType='movie', contentTitle=PeliName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Episodios nuevos(.*?)>Somos')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        title = title.replace('#8217;', "'")

        SerieName = corregir_SerieName(title)

        temp = scrapertools.find_single_match(match, '<span class="ClB">(.*?)x')
        if not temp: temp = 1

        epis = scrapertools.find_single_match(match, '<b class="e">Episodio (.*?)</b>').strip()
        if not epis: epis = 1

        title = 'Episodio ' + str(epis) + ' ' + title

        title = title.replace('Episodio', '[COLOR goldenrod]Epis.[/COLOR]').replace('episodio', '')

        title = title.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('season', '[COLOR tan]Temp.[/COLOR]')

        if 'Pelicula' in title: title = title.replace('Pelicula', '[COLOR deepskyblue]Pelicula[/COLOR]')

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, '<span class="Year">.*?,(.*?)</span>').strip()

        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb, infoLabels={'year': year},
                                    contentSerieName = SerieName, contentType = 'episode', contentSeason=temp, contentEpisodeNumber=epis))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'var eps =(.*?)</script>')

    bloque = bloque.replace('["', '"').replace('],', ';')

    matches = scrapertools.find_multiple_matches(str(bloque), '.*?"(.*?)".*?;')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('HenaOjaraN', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('HenaOjaraN', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjaraN', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjaraN', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjaraN', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HenaOjaraN', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('HenaOjaraN', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        if not item.contentSeason: item.contentSeason = 1

        titulo = '%sx%s %s' % (str(item.contentSeason), match, str(item.contentSerieName))

        url = item.url.replace('/anime/', '/ver/') + '-' + match

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = match ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage, text_color='coral' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if item._peli:
        peli = item.url.replace('/anime/', '/ver/') + '-1'

        data = do_downloadpage(peli)

    if '<span>SUB</span>' in data: lang = 'Vose'
    else:
        lang = scrapertools.find_single_match(data, '<h1 class="Title">(.*?)<span>')

        if 'castellano' in lang.lower(): lang = 'Esp'
        elif 'latino' in lang.lower(): lang = 'Lat'
        elif 'subtitulado' in lang.lower(): lang = 'Vose'
        elif 'español' in lang.lower(): lang = 'Vose'
        else: lang = 'VO'

    ses = 0

    # ~ encrypt
    d_encrypt = scrapertools.find_single_match(data, 'data-encrypt="(.*?)"')

    d_bytes = scrapertools.find_single_match(data, 'data-h="(.*?)"')

    if d_encrypt:
        post = {'acc': 'opt', 'i': d_encrypt}

        data1 = do_downloadpage(host + 'hj', post=post, headers={'Referer': item.url, 'X-Requested-With': 'XMLHttpRequest'})

        matches = re.compile('<li(.*?)</li>', re.DOTALL).findall(data1)

        for match in matches:
            encrypt = scrapertools.find_single_match(match, 'encrypt="(.*?)"')

            srv = scrapertools.find_single_match(match, 'title="Opción(.*?)"')

            srv = srv.replace('Opción', '').lower().strip()

            if not srv or not encrypt: continue

            itemlist.append(Item( channel = item.channel, action = 'play', server='directo', title = '', crypto=encrypt, bytes=d_bytes,
                                  language=lang, other=srv ))

    # ~ download
    bloque = scrapertools.find_single_match(data, 'data-dwn=(.*?)Descargar<')

    if bloque:
        if '><li' in bloque: bloque = bloque.split("><li")[0]
        elif ']"><i' in bloque: bloque = bloque.split(']"><i')[0]

        bloque = bloque.strip()
        bloque = bloque.replace('&quot;', '"').replace(',', '","').replace('"",""', '","')
        bloque = bloque + ','

    matches = re.compile('"(.*?)",', re.DOTALL).findall(bloque)

    for option in matches:
        ses += 1

        if not option: continue

        url = option

        url = url.replace('\\/', '/')

        if '1fichier' in url: continue
        elif 'fembed' in url: continue
        elif 'streamsb' in url: continue
        elif 'nyuu' in url: continue
        elif '4sync' in url: continue

        if 'netuplayer' in url or 'netu' in url or 'hqq' in url: servidor = 'waaw'

        elif 'streamtape' in url: servidor = 'streamtape'
        elif 'mega' in url: servidor = 'mega'
        elif 'voe' in url: servidor = 'voe'
        elif 'mixdrop' in url: servidor = 'mixdrop'

        elif 'streamwish' in url or 'wish' in url: servidor = 'various'
        elif 'filelions' in url: servidor = 'various'
        elif 'filemoon' in url: servidor = 'various'
        elif 'streamvid' in url: servidor = 'various'
        elif 'vidhide' in url: servidor = 'various'
        elif 'lulustream' in url: servidor = 'various'
        elif 'listeamed' in url or 'vidguard' in url: servidor = 'various'

        elif 'ok' in url: servidor = 'okru'
        elif 'dood' in url: servidor = 'doodstream'

        else:
             if servertools.is_server_available(url):
                 if not servertools.is_server_enabled(url): continue
             else:
                 if not config.get_setting('developer_mode', default=False): continue
                 servidor = 'directo'

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)
        elif not servidor == 'directo': other = ''

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    url = item.url

    if item.crypto:
        crypto = str(item.crypto)
        bytes = str(item.bytes)

        try:
            cripto = ast.literal_eval(cripto)
        except:
            crypto = str(item.crypto)

        try:
            url = GibberishAES.dec(GibberishAES(), string = crypto, pass_ = bytes)
        except:
            url = ''

        if not url:
            return '[COLOR cyan]No se pudo [COLOR red]Desencriptar[/COLOR]'

    elif '/?trdownload=' in url:
           url = httptools.downloadpage(url, follow_redirects=False, timeout=timeout).headers['location']

           url = url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

           if '/multiplayer/' in url:
               data = do_downloadpage(url, headers={'Referer': url})

               srv = scrapertools.find_single_match(data, "value = '(.*?)'")

               if srv:
                   data = do_downloadpage(url, post={'servidor': srv}, headers={'Referer': url})

                   url = scrapertools.find_single_match(data, '<a href="(.*?)"')
               else: url = ''

               if not url:
                   return 'Tiene [COLOR plum]Acortador[/COLOR] del enlace'

    if '/streamium.xyz/' in url: url = ''
    elif '/pelispng.' in url: url = ''
    elif '/pelistop.' in url: url = ''
    elif '/descargas/' in url: url = ''

    if '/go.php?v=' in url:
          url = scrapertools.find_single_match(url, 'v=(.*?)$')

    if url:
        if '.mystream.' in url:
            return 'Servidor [COLOR tan]Cerrado[/COLOR]'

        elif '.fembed.' in url:
            return 'Servidor [COLOR tan]Cerrado[/COLOR]'

        url = url.replace('&amp;', '&')

        if '/player.streamhj.top/' in url: url = url.replace('/player.streamhj.top/', '/netu.to/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone( url=url, server=servidor))

    return itemlist


def corregir_SerieName(SerieName):
    logger.info()

    if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
    if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]
    if 'Episodio' in SerieName: SerieName = SerieName.split("Episodio")[0]
    if 'episodio' in SerieName: SerieName = SerieName.split("episodio")[0]
    if 'Episode' in SerieName: SerieName = SerieName.split("Episode")[0]
    if 'episode' in SerieName: SerieName = SerieName.split("episode")[0]

    if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]

    if '(Sin Relleno)' in SerieName: SerieName = SerieName.split("(Sin Relleno)")[0]

    if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]

    SerieName = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", SerieName).strip()
    SerieName = SerieName.replace('Español Latino HD', '').replace('Español Castellano HD', '').replace('Sub Español HD', '').strip()

    if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]

    if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
    if 'season' in SerieName: SerieName = SerieName.split("season")[0]

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
        item.url =  host + 'animes?buscar=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
