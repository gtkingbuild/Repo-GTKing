# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://serieskao.org/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://serieskao.tv/', 'https://serieskao.net/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if '/lanzamiento/' in url: raise_weberror = False

    if '/?s=' in url: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'genre_series/anime/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'genre_series/anime/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    logger.info()
    itemlist=[]

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
       'historia',
       'misterio',
       'musica',
       'romance',
       'suspense',
       'terror',
       'western'
       ]

    for genre in genres:
        url = host + 'genero/' + genre + '/'

        itemlist.append(item.clone( action = 'list_all', title = genre.capitalize(), url = url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': tope_year = 1932
    else: tope_year = 1984

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        url = host + 'lanzamiento/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '<h2>Añadido recientemente' in data:
        bloque = scrapertools.find_single_match(data, '<h2>Añadido recientemente(.*?)<div class="copy">©')
    else:
        bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="imdb">.*?<span>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(match, 'class="year">([^<]+)')
        if not year: year = '-'

        title = title.replace('#038', '')

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
        next_url = scrapertools.find_single_match(data, '<span class="current">.*?' + "<a href='(.*?)'")
        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = scrapertools.find_multiple_matches(data, "(?is)class='title'>([^<]+)")

    for tempo in temporadas:
        season = scrapertools.find_single_match(tempo, '\d+')

        title = 'Temporada ' + season

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = int(season)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = int(season) ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron  = "(?is)class='numerando'>(%s - \d+)<.*?" % str(item.contentSeason)
    patron += "href='([^']+)'>([^<]+)"

    matches = scrapertools.find_multiple_matches(data, patron)

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesKao', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for episode, url, epi_name in matches[item.page * item.perpage:]:
        epi_num = scrapertools.find_single_match(episode, "- (\d+)")

        title = "%sx%s - %s" % (str(item.contentSeason), epi_num, epi_name)

        itemlist.append(item.clone( action='findvideos', url = url, title = title,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epi_num ))

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

    matches = re.compile("class='dooplay_player_option'.*?data-type='(.*?)'.*?data-post='(.*?)'.*?data-nume='(.*?)'", re.DOTALL).findall(data)

    ses = 0

    for d_type, d_post, d_nume in matches:
        ses += 1

        if not d_type or not d_post or not d_nume: continue

        post = {'action': 'doo_player_ajax', 'post': d_post, 'nume': d_nume, 'type': d_type}
        data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post, headers = {'Referer': item.url})

        embed_url = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')
        if not embed_url: continue

        embed_url = embed_url.replace('\\/', '/')

        _servers = do_downloadpage(embed_url, headers = {"referer": item.url})
        if not _servers: continue

        matches2 = re.compile('data-lang="(\d+)"\s*data-r="([^"]+)"').findall(_servers)

        if not matches2:
            if '/player.serieskao.org/' in embed_url:
               data = do_downloadpage(embed_url)

               matches3 = scrapertools.find_multiple_matches(data, "go_to_player\('([^']+)")

               for url in matches3:
                   if not url.startswith("http"):
                      new.url = 'https://player.serieskao.org/player/?id=' + url
                      new_dat = do_downloadpage(new.url)
                      url = scrapertools.find_single_match(new_dat, 'iframe src="([^"]+)')

                   other = servertools.get_server_from_url(url)
                   other = servertools.corregir_servidor(other)

                   if not other == 'directo':
                       itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, other = other ))

               return itemlist

            if '/hqq.' in embed_url or '/waaw.' in embed_url or '/netu.' in embed_url: embed_url = ''

            if embed_url:
                other = ''
                if '.animekao.club/embed' in embed_url: other = 'kplayer'
                elif 'kaodrive/embed.php' in embed_url or '/playmp4/' in embed_url: other = 'amazon'
                elif 'kaocentro.net' in embed_url: other = 'kplayer'
                elif 'hydrax.com' in embed_url: other = 'hydrax'
                elif '.xyz/v/' in embed_url: other = 'fembed'

                if not other:
                    other = servertools.get_server_from_url(embed_url)
                    other = servertools.corregir_servidor(other)

                if not other == 'directo':
                    itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = embed_url, other = other ))

                return itemlist

        for lang, b64url in matches2:
            url = base64.b64decode(b64url)

            if isinstance(url, bytes): url = url.decode('utf-8')

            if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: url = ''

            if url:
                other = ''
                if '.animekao.club/embed' in url: other = 'kplayer'
                elif 'kaodrive/embed.php' in url or '/playmp4/' in url: other = 'amazon'
                elif 'kaocentro.net' in url: other = 'kplayer'
                elif 'hydrax.com' in url: other = 'hydrax'
                elif '.xyz/v/' in url: other = 'fembed'

                if not other:
                    other = servertools.get_server_from_url(url)
                    other = servertools.corregir_servidor(other)

                if not other == 'directo':
                    lng = IDIOMAS.get(lang, lang)

                    itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, language = lng, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if '.animekao.club/embed' in url or '.kaocentro.net/embed' in url:
        from lib import jsunpack
        sdata = do_downloadpage(url)

        d = scrapertools.find_single_match(sdata, '(?s)<script type="text\/javascript">(eval.*?)<\/script>')
        pack = jsunpack.unpack(d)

        file = scrapertools.find_single_match(pack, '"file":"([^"]+)"')
        urlserver = 'https://kplayer.animekao.club/' + file

        url = file

        if not 'https://' in file:
            try:
               url = httptools.downloadpage(urlserver, follow_redirects=False).headers['location']
            except:
               pass

    elif 'kaodrive/embed.php' in url or '/playmp4/' in url:
         data = do_downloadpage(url)
         shareId = scrapertools.find_single_match(data, 'var shareId = "([^"]+)')
         if not shareId: shareId = scrapertools.find_single_match(data, 'config_player.link = "([^"]+)')

         url = 'https://www.amazon.com/drive/v1/shares/%s?resourceVersion=V2&ContentType=JSON&asset=ALL' %(shareId)

    elif '.xyz/v/' in url:
         url = url.replace('serieskao.xyz/v/', 'suzihaza.com/v/').replace('animekao.xyz/v/', 'suzihaza.com/v/').replace('sypl.xyz/v/', 'suzihaza.com/v/')
         if '#' in url:
             url = url.split('#')[0]

    elif '/kaocentro.net/' in url:
         try:
            data = do_downloadpage(url)
         except:
            return 'Este vídeo ya no esta disponible'

         url = scrapertools.find_single_match(data, '<iframe src="(.*?)"')

         if not url: url = item.url

    elif 'hydrax.com' in url:
         slug = url.split('v=')[1]
         post = "slug=%s&dataType=mp4" % slug
         try:
            data = do_downloadpage("https://ping.iamcdn.net/", post=post)
         except:
            url = ''

    if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'zplayer': url = url + '|' + host

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
