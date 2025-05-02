# -*- coding: utf-8 -*-

import ast, re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


from lib.pyberishaes import GibberishAES


host = 'https://serieskao.top/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://serieskao.tv/', 'https://serieskao.net/', 'https://serieskao.org/']

domain = config.get_setting('dominio', 'serieskao', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'serieskao')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'serieskao')
    else: host = domain


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    if '/year/' in url: raise_weberror = False

    if '/search?s=' in url: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'serieskao', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_serieskao', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='serieskao', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_serieskao', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    itemlist.append(Item( channel='actions', action='show_old_domains', title='[COLOR coral][B]Historial Dominios[/B][/COLOR]', channel_id = 'serieskao', thumbnail=config.get_thumb('serieskao') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    if config.get_setting('mnu_doramas', default=False):
        itemlist.append(item.clone( title = 'Doramas', action = 'mainlist_series', text_color = 'firebrick' ))

    if not config.get_setting('descartar_anime', default=False):
        itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    if config.get_setting('mnu_doramas', default=False):
        itemlist.append(item.clone( title = 'Doramas', action = 'list_all', url = host + 'generos/dorama/', search_type = 'tvshow', text_color = 'firebrick' ))

    if not config.get_setting('descartar_anime', default=False):
        itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', search_type = 'tvshow', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def mainlist_animes(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', group = 'animes', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', group = 'animes', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else:
       if item.group == 'animes': text_color = 'springgreen'
       else: text_color = 'hotpink'

    genres = [
       'accion',
       'animacion',
       'aventura',
       'belica',
       'ciencia-ficcion',
       'comedia',
       'crimen',
       'documental',
       'drama',
       'familia',
       'fantasia',
       'guerra',
       'historia',
       'misterio',
       'musica',
       'romance',
       'suspense',
       'terror',
       'western'
       ]

    for genre in genres:
        url = host + 'generos/' + genre + '/'

        if item.search_type == 'movie': url = url + 'peliculas/'
        else:
            if item.group == 'animes': url = url + 'animes/'
            else: url = url + 'series/'

        itemlist.append(item.clone( action = 'list_all', title = genre.capitalize(), url = url, genre = genre, text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else:
       if item.group == 'animes': text_color = 'springgreen'
       else: text_color = 'hotpink'

    if item.search_type == 'movie': tope_year = 1932
    else:
        if item.group == 'animes': tope_year = 1998
        else: tope_year = 1984

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        url = host + 'year/' + str(x) + '/'

        if item.search_type == 'movie': url = url + 'peliculas/'
        else:
            if item.group == 'animes': url = url + 'animes/'
            else: url = url + 'series/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', anio = str(x), text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if item.genre or item.anio: bloque = scrapertools.find_single_match(data, '<div role="tabpanel"(.*?)<span>Copyright')
    else: bloque = scrapertools.find_single_match(data, '<div class="tab-info">(.*?)<span>Copyright')

    matches = scrapertools.find_multiple_matches(bloque, '(.*?)</div></div></a>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        title = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        if not url or not title: continue

        title = title.replace('&#038;', '').replace('&#039;', '').replace('()', '')

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(title, ' \((\d+)\)')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        if '/year/' in item.url: year = scrapertools.find_single_match(item.url, "/year/(.*?)/")

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="page-item active".*?<span class="page-link">.*?href="(.*?)"')

        if next_page:
            if '?page=' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    temporadas = scrapertools.find_multiple_matches(data, 'data-toggle="tab">(.*?)</a>')

    for tempo in temporadas:
        season = scrapertools.find_single_match(tempo, '\d+')

        title = 'Temporada ' + season

        if len(temporadas) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = int(season)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = int(season), text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'id="pills-vertical-' + str(item.contentSeason) + '"(.*?)</div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?class="btn btn btn-primary btn-block">(.*?)</a>')

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, datos in matches[item.page * item.perpage:]:
        epis = scrapertools.find_single_match(datos, "- E(.*?):")

        epi_name = scrapertools.find_single_match(datos, ":(.*?)$")

        title = "%sx%s - %s" % (str(item.contentSeason), epis, epi_name)

        itemlist.append(item.clone( action='findvideos', url = url, title = title, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

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

    IDIOMAS = {'0': 'Lat', '1': 'Esp', '2': 'Vose'}

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    link = scrapertools.find_single_match(data, '<iframe src="(.*?)"')
    if '+video[1]+' in str(link): link = scrapertools.find_single_match(data, "video\[1\] = '([^']+)")

    if not link: return itemlist

    data = do_downloadpage(link)

    ses = 0

    if '//embed69.' in link:
        ses += 1

        datae = data

        dataLink = scrapertools.find_single_match(datae, 'const dataLink =(.*?);')
        if not dataLink: dataLink = scrapertools.find_single_match(datae, 'dataLink(.*?);')

        e_bytes = scrapertools.find_single_match(datae, "const bytes =.*?'(.*?)'")
        if not e_bytes: e_bytes = scrapertools.find_single_match(datae, "encrypted.*?'(.*?)'")

        e_links = dataLink.replace(']},', '"type":"file"').replace(']}]', '"type":"file"')

        langs = scrapertools.find_multiple_matches(str(e_links), '"video_language":(.*?)"type":"file"')

        for lang in langs:
            ses += 1

            lang = lang + '"type":"video"'

            links = scrapertools.find_multiple_matches(str(lang), '"servername":"(.*?)","link":"(.*?)".*?"type":"video"')

            if 'SUB' in lang: lang = 'Vose'
            elif 'LAT' in lang: lang = 'Lat'
            elif 'ESP' in lang: lang = 'Esp'
            else: lang = '?'

            for srv, link in links:
                ses += 1

                srv = srv.lower().strip()

                if not srv: continue
                elif host in link: continue

                elif '1fichier.' in srv: continue
                elif 'plustream' in srv: continue
                elif 'embedsito' in srv: continue
                elif 'disable2' in srv: continue
                elif 'disable' in srv: continue
                elif 'xupalace' in srv: continue
                elif 'uploadfox' in srv: continue
                elif 'embedsito' in srv: continue
                elif 'player-cdn' in srv: continue

                elif srv == 'download': continue

                servidor = servertools.corregir_servidor(srv)

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                    if not config.get_setting('developer_mode', default=False): continue

                other = ''

                if servidor == 'various': other = servertools.corregir_other(srv)

                if servidor == 'directo':
                    if not config.get_setting('developer_mode', default=False): continue
                    else:
                       other = url.split("/")[2]
                       other = other.replace('https:', '').strip()

                itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = '', crypto=link, bytes=e_bytes,
                                      language=lang, other=other ))

    if '/xupalace.' in link:
        ses += 1

        lang = '?'

        if 'php?id=' in link:
            datax = do_downloadpage(link)

            url = scrapertools.find_single_match(datax, '<iframe src="(.*?)"')

            if url:
                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): url = ''
                else:
                    if not config.get_setting('developer_mode', default=False): url = ''

                if url: 
                    url = servertools.normalize_url(servidor, url)

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url=url, language=lang, other=other ))

        elif '/video/' in link:
            datax = do_downloadpage(link)

            matchesx = scrapertools.find_multiple_matches(datax, "go_to_playerVast.*?'(.*?)'")

            for matchx in matchesx:
                if '/embedsito.' in matchx: matchx = ''
                elif '/player-cdn.' in matchx: matchx = '' 
                elif '/1fichier.' in matchx: matchx = ''
                elif '/hydrax.' in matchx: matchx = ''
                elif '/xupalace.' in matchx: matchx = ''
                elif '/uploadfox.' in matchx: matchx = ''

                if matchx:
                    servidor = servertools.get_server_from_url(matchx)
                    servidor = servertools.corregir_servidor(servidor)

                    if servertools.is_server_available(servidor):
                        if not servertools.is_server_enabled(servidor): matchx = ''
                    else:
                        if not config.get_setting('developer_mode', default=False): matchx = ''

                    if matchx:
                        url = servertools.normalize_url(servidor, matchx)

                        other = ''
                        if servidor == 'various': other = servertools.corregir_other(url)

                        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url=url, language=lang, other=other ))

    # ~ Otros
    matches = re.compile('<li onclick="go_to_player(.*?)</li>', re.DOTALL).findall(data)

    if not matches:
        url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            other = ''
            if servidor == 'various': other = servertools.corregir_other(url)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = other ))

    else:
        for match in matches:
            ses += 1

            url = scrapertools.find_single_match(match, "'(.*?)'")

            if not url: continue

            try:
                url = base64.b64decode(url).decode("utf-8")
            except:
                pass

            if '/?uptobox=' in url:
                url = scrapertools.find_single_match(url, '/?uptobox=(.*?)$')
                url = 'https://uptobox.com/' + url

            lang = scrapertools.find_single_match(match, 'data-lang="(.*?)"')

            lng = IDIOMAS.get(lang, lang)

            other = scrapertools.find_single_match(match, '<span>(.*?)</span>').strip().lower()

            if other == '1fichier': continue
            elif other == 'plusclick': continue
            elif other == 'plustream': continue
            elif other == 'xupalace': continue
            elif other == 'uploadfox': continue

            elif other == 'mirror': continue
            elif other == 'hydrax': continue

            other = servertools.corregir_servidor(other)

            servidor = other

            if servidor == 'stp': servidor = 'streamtape'
            elif servidor == 'vox': servidor = 'voe'

            if other == 'plusvip':
                vid_url = url

                url_pattern = '(?:[\w\d]+://)?[\d\w]+\.[\d\w]+/moe\?data=(.+)$'
                src_pattern = "this\[_0x5507eb\(0x1bd\)\]='(.+?)'"

                data = do_downloadpage(vid_url)

                url = scrapertools.find_single_match(vid_url, url_pattern)
                src = scrapertools.find_single_match(data, src_pattern)

                src_url = "https://plusvip.net{}".format(src)

                url = do_downloadpage(src_url, post={'link': url}, headers = {'Referer': vid_url})

                url = scrapertools.find_single_match(url, '"link":"(.*?)"')

                if not url: continue

                url = url.replace('\\/', '/')

                servidor = 'directo'

            if other == 'various': other = servertools.corregir_other(url)

            elif other == 'stp': other = 'streamtape'
            elif other == 'vox': other = 'voe'

            if other == servidor: other = ''

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lng, other = other.capitalize() ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

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

    elif not item.server == 'directo':
        servidor = servertools.get_server_from_url(item.url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, item.url)

        itemlist.append(item.clone(url = url, server = servidor))

        return itemlist

    if url:
        if '/xupalace.' in url or '/uploadfox.' in url:
            return 'Servidor [COLOR goldenrod]No Soportado[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor == 'zplayer': url = url + '|' + host

        if servidor == 'directo':
            new_server = servertools.corregir_other(url).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
