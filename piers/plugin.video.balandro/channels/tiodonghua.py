# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://tiodonghua.com/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_tiodonghua_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar ...[/B]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    if not headers: headers = {'Referer': host}

    hay_proxies = False
    if config.get_setting('channel_tiodonghua_proxies', default=''): hay_proxies = True

    timeout = None
    if host in url:
        if hay_proxies: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('tiodonghua', url, post=post, headers=headers, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

        if not data:
            if not '/?s=' in url:
                if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

                timeout = config.get_setting('channels_repeat', default=30)

                if hay_proxies:
                    data = httptools.downloadpage_proxy('tiodonghua', url, post=post, headers=headers, timeout=timeout).data
                else:
                    data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if not '/?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='tiodonghua', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_tiodonghua', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('zonaleros') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_anime', default=False): return

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'donghua/', search_type = 'tvshow' )) 

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host + 'episodios/', group = 'last', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Episodios Animes', action = 'list_all', url = host + 'anime/', group = 'lani', search_type = 'tvshow', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Donghuas', action = 'list_all', url = host + 'genero/donghua/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('accion', 'Acción'),
       ('action-adventure', 'Accion y Aventura'),
       ('animacion', 'Animación'),
       ('anime-japones', 'Anime Japonés'),
       ('artes-marciales', 'Artes Marciales'),
       ('aventura', 'Aventura'),
       ('ciencia-ficcion', 'Ciencia Ficción'),
       ('comedia', 'Comedia'),
       ('demonios', 'Demonios'),
       ('drama', 'Drama'),
       ('fantasia', 'Fantasía'),
       ('misterio', 'Misterio'),
       ('musica', 'Música'),
       ('patreon', 'Patreon'),
       ('romance', 'Romance'),
       ('sci-fi-fantasy', 'Sci-Fi & Fantasy'),
       ('terror', 'Terror')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url = host + 'genero/' + opc + '/', action = 'list_all', text_color = 'springgreen' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if item.group == 'lani':
         bloque = scrapertools.find_single_match(data, '>Nuevos Episodios<(.*?)>Recomendaciones<')
    else:
         bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)>Lo mas Popular<')

    if not bloque: bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        if '>Película<' in match: continue
        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        title = title.replace('&#8217;s', "'s").replace('&#8211;', '').replace('&#8217;', '').replace('&#8220;', '').replace('&#8221;', '').strip()

        year = scrapertools.find_single_match(match, '</h3><span>(.*?)</span>')
        if not year: year = '-'

        SerieName = corregir_SerieName(title)

        if '>T2' in match: season = 2
        elif '>T3' in match: season = 3
        elif '>T4' in match: season = 4
        elif '>T5' in match: season = 5
        elif '>T6' in match: season = 6
        elif '>T7' in match: season = 7
        elif '>T8' in match: season = 8
        elif '>T9' in match: season = 9
        else: season = 1

        if item.group == 'last':
            epi = scrapertools.find_single_match(match, '>Episodio(.*?)</a>').strip()

            if not epi: epi = 1

            if epi:
                SerieName = SerieName.replace(' ' + str(epi), '').strip()

            titulo = '[COLOR goldenrod]Epis. [/COLOR]' + str(epi) + ' ' + title.replace('Episodio ' + str(epi), '').strip()

            titulo = titulo.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('Temporada', '[COLOR tan]Temp.[/COLOR]')

            itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epi ))
        else:
            if item.group == 'lani':
                epi = scrapertools.find_single_match(match, '<span class="epx">Ep(.*?)</span>').strip()

                if not epi: epi = 1

                titulo = title

                if epi:
                    SerieName = SerieName.replace(' ' + str(epi), '').strip()
                    titulo = '[COLOR goldenrod]Epis. [/COLOR]' + str(epi) + ' ' + titulo.replace(' ' + str(epi), '').strip()

                titulo = titulo.replace('Season', '[COLOR tan]Temp.[/COLOR]').replace('Temporada', '[COLOR tan]Temp.[/COLOR]')

                itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb, infoLabels={'year': year},
                                            contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epi ))

                continue

            itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb, infoLabels={'year': year},
                                        contentSerieName = SerieName, contentType = 'tvshow', contentSeason = season  ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
            next_page = scrapertools.find_single_match(data,'<div class="pagination">.*?<span class="current">.*?ref="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

        elif '<div class="hpage">' in data:
            if 'Previous' in data:
                next_page = scrapertools.find_single_match(data,'<div class="hpage">.*?Previous.*?ref="(.*?)"')
            else:
                next_page = scrapertools.find_single_match(data,'<div class="hpage">.*?ref="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    epis = scrapertools.find_multiple_matches(data, "<li class='mark-.*?data-src='(.*?)'.*?<div class='numerando'>(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>")
    if not epis: epis = scrapertools.find_multiple_matches(data, "<li class='mark-.*?<img src='(.*?)'.*?<div class='numerando'>(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>")
    if not epis: epis = scrapertools.find_multiple_matches(data, '<li class="mark-.*?src="(.*?)".*?<div class="numerando">(.*?)</div>.*?<a href="(.*?)">(.*?)</a>')

    if not epis:
        bloque = scrapertools.find_single_match(data, '</a></div><div class="inepcx">(.*?)</a></li></ul>')

        if '<div class="eplister">': bloque = scrapertools.find_single_match(bloque, '<div class="eplister">(.*?)$')

        links = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)"')

        for url in links:
            epi = scrapertools.find_single_match(bloque, '<a href="' + url + '".*?<div class="epl-num">(.*?)</div>').strip()

            if not epi: epi = 1
            item.contentSeason = 1

            titulo = '%sx%s - %s' % (str(item.contentSeason), epi, item.contentSerieName)

            itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                        contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epi ))

        return itemlist

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(epis)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('TioDonghua', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, temp_epi, url, title in epis[item.page * item.perpage:]:
        epi = scrapertools.find_single_match(temp_epi, '.*?-(.*?)$').strip()

        if item.contentSerieName: titulo = '%sx%s %s' % (str(item.contentSeason), epi, title)
        else: titulo = item.title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epi ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(epis) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<li id='player-option-(.*?)</span></li>")
    if not matches: matches = scrapertools.find_multiple_matches(data, '<li id="player-option-(.*?)</span></li>')
    ses = 0

    for match in matches:
        ses += 1

        d_type = scrapertools.find_single_match(match, "data-type='(.*?)'")
        if not d_type: d_type = scrapertools.find_single_match(match, 'data-type="(.*?)"')

        d_post = scrapertools.find_single_match(match, "data-post='(.*?)'")
        if not d_post: d_post = scrapertools.find_single_match(match, 'data-post="(.*?)"')

        d_nume = scrapertools.find_single_match(match, "data-nume='(.*?)'")
        if not d_nume: d_nume = scrapertools.find_single_match(match, 'data-nume="(.*?)"')

        if not d_type or not d_post or not d_nume: continue

        post = {'action': 'doo_player_ajax', 'post': d_post, 'nume': d_nume, 'type': d_type}

        data = do_downloadpage(host + 'wp-admin/admin-ajax.php', post = post)

        url = scrapertools.find_single_match(data, '"embed_url":.*?"(.*?)"')

        if not 'http' in url:
            if '<iframe' in data or '<IFRAME' in data:
                 data = str(data).replace('=\\', '=').replace('\\"', '/"')

                 url = scrapertools.find_single_match(str(data), '<iframe.*?src="(.*?)"')
                 if not url: url = scrapertools.find_single_match(str(data), '<IFRAME.*?SRC="(.*?)"')

        if '<iframe' in url or '<IFRAME' in url:
             data = str(data).replace('=\\', '=').replace('\\"', '/"')

             url = scrapertools.find_single_match(str(data), '<iframe.*?src="(.*?)"')
             if not url: url = scrapertools.find_single_match(str(data), '<IFRAME.*?SRC="(.*?)"')

        url = url.replace('\\/', '/')

        # ~ Multiserver
        if '//player.tiodonghua.' in url:
            data2 = do_downloadpage(url)
            matches2 = scrapertools.find_multiple_matches(data2, "go_to_player.*?'(.*?)'")

            url_post = url

            for url in matches2:
                ses += 1

                new_url = ''

                headers = {'Referer': url_post, 'Connection': 'keep-alive'}

                if config.get_setting('channel_tiodonghua_proxies', default=''):
                    resp = httptools.downloadpage_proxy('tiodonghua', url, headers = headers, follow_redirects=False, raise_weberror=False)
                else:
                    resp = httptools.downloadpage(url, headers = headers, follow_redirects=False, raise_weberror=False)

                if 'location' in resp.headers:
                    new_url = resp.headers['location']

                if new_url: url = new_url

                if '/tioplayer.' in url: continue
                elif '.tiodonghua.' in url: continue

                if 'http:' in url: url = url.replace('http:', 'https:')

                if not 'https:' in url: url = 'https:' + url

                if url.startswith("https://sb"): continue
                elif 'fembed' in url or  'streamsb' in url or 'playersb' in url or 'fcom' in url: continue

                url = url.replace('/Smoothpre.', '/smoothpre.')

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                    if not config.get_setting('developer_mode', default=False): continue

                other = servidor

                if servidor == 'various': other = servertools.corregir_other(url)

                if servidor == other:
                    if servidor == 'zures':
                        if '/videa.' in url: other = 'Videa'
                        else:
                           other = url.split("/")[2]
                           other = other.replace('https:', '').strip()

                    else: other = ''

                elif not servidor == 'directo':
                    if not servidor == 'various': other = ''

                if servidor == 'directo':
                    if '/tioplayer.' in url: continue
                    elif '/tiodonghua.' in url: continue

                    if '/ok.ru' in url: servidor = 'okru'

                    elif '/terabox.' in url:
                       servidor = 'various'
                       other = 'terabox'

                    elif config.get_setting('developer_mode', default=False):
                        other = url.split("/")[2]
                        other = other.replace('https:', '').strip()


                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Vos', other = other ))

            continue

        if not url: continue

        if '/nephobox.' in url: continue
        elif '.modagamers.' in url: continue
        elif 'cuyplay.com' in url: continue
        elif 'digitalxona.com' in url: continue
        elif 'animetemaefiore.club' in url: continue
        elif 'guccihide.com' in url: continue
        elif 'sharezweb.com' in url: continue
        elif 'videopress.com' in url: continue
        elif 'tioplayer.com' in url: continue
        elif 'likessb.com' in url: continue
        elif '.animefenix.' in url: continue
        elif '.tiodonghua.' in url: continue
        elif '/odysee.' in url: continue

        if 'http:' in url: url = url.replace('http:', 'https:')

        if not 'https:' in url: url = 'https:' + url

        if url.startswith("https://sb"): continue
        elif 'fembed' in url or  'streamsb' in url or 'playersb' in url or 'fcom' in url: continue

        if 'es.png' in match: lang = 'Esp'
        elif 'mx.png' in match: lang = 'Lat'
        elif 'br.png' in match: lang = 'Pt'
        elif 'en.png' in match: lang = 'Vose'
        else: lang = '?'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        other = servidor

        if servidor == 'various': other = servertools.corregir_other(url)

        if servidor == other:
            if servidor == 'zures':
                if '/videa.' in url: other = 'Videa'
                else:
                    other = url.split("/")[2]
                    other = other.replace('https:', '').strip()
            else: other = ''

        elif not servidor == 'directo':
           if not servidor == 'various': other = ''

        if servidor == 'directo':
            if config.get_setting('developer_mode', default=False):
                other = url.split("/")[2]
                other = other.replace('https:', '').strip()

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = other ))

    if '<strong>DL</strong>' in data:
        url = scrapertools.find_single_match(data, '<strong>DL</strong>.*?<a href="(.*?)"')

        if url.startswith("https://sb"): url = ''
        elif 'fembed' in url or  'streamsb' in url or 'playersb' in url or 'fcom' in url: url = ''

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Vose' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url_play = item.url

    servidor = servertools.get_server_from_url(url_play)
    servidor = servertools.corregir_servidor(servidor)

    url_play = servertools.normalize_url(servidor, url_play)

    if servidor == 'directo':
        new_server = servertools.corregir_other(url_play).lower()
        if new_server.startswith("http"): servidor = new_server

    if '/filelions.' in url_play:
        url_play = url_play + '|Referer=' + host

    itemlist.append(item.clone(url = url_play, server = servidor))

    return itemlist


def corregir_SerieName(SerieName):
    logger.info()

    SerieName = SerieName.replace('Novela', '').strip()

    if 'Sub Español' in SerieName: SerieName = SerieName.split("Sub Español")[0]
    if 'Traducida al Español' in SerieName: SerieName = SerieName.split("Traducida al Español")[0]
    if 'Legendado Portugués' in SerieName: SerieName = SerieName.split("Legendado Portugués")[0]
    if 'Portugués' in SerieName: SerieName = SerieName.split("Portugués")[0]

    if 'Season' in SerieName: SerieName = SerieName.split("Season")[0]
    if 'season' in SerieName: SerieName = SerieName.split("season")[0]

    if 'Movie' in SerieName: SerieName = SerieName.split("Movie")[0]

    if '(TV)' in SerieName: SerieName = SerieName.split("(TV)")[0]

    if 'Episodio' in SerieName: SerieName = SerieName.split("Episodio")[0]
    if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
    if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]

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
        item.url =  host + "?s=" + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
