# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://www.elitetorrent.com/'


# ~ por si viene de enlaces guardados
ant_hosts = ['https://elitetorrent.app/', 'https://elitetorrent.la/', 'https://www.elitetorrent.wtf/',
             'https://www.elitetorrent.dev/']


domain = config.get_setting('dominio', 'elitetorrent', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'elitetorrent')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'elitetorrent')
    else: host = domain


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post).data

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'elitetorrent', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_elitetorrent', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='elitetorrent', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_elitetorrent', title=title, desde_el_canal = True, folder=False, text_color='darkorange' ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-16-1/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host + 'estrenos/', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series-20-1/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host + 'estrenos/', search_type = 'tvshow', text_color='cyan' ))

    return itemlist



def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/castellano-17-1/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/espanol-latino-11-1/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Inglés', action = 'list_all', url = host + 'idioma/ingles/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/vose-3-1/', text_color='moccasin' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En 720', action = 'list_all', url = host + 'calidad/720p-2/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En 1080', action = 'list_all', url = host + 'calidad/1080p-10-1/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En DVD Rip', action = 'list_all', url = host + 'calidad/dvdrip-1/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En HD Rip', action = 'list_all', url = host + 'calidad/hdrip-1/', text_color='moccasin' ))
    itemlist.append(item.clone( title = 'En Micro HD', action = 'list_all', url = host + 'peliculas-microhd-9/', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<ul id="cab-categorias">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)".*?title=.*?">(.*?)</a>')

    for url, title in matches:
        title = title.replace('&amp;', '&')

        if '/animacion-2' in url: title = title + '-2'

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1959, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'estreno/' + str(x) + '/', action='list_all', any = str(x), text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '/?s=' in item.url:
        if '<h1>No se han encontrado resultados para' in data: return itemlist

    matches = scrapertools.find_multiple_matches(data, '<div class="imagen">(.*?)<div class="meta">')

    i = 0

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        title = title.replace('(720)', '').replace('(720p)', '').replace('(1080)', '').replace('(1080p)', '').replace('(microHD)', '').replace('(BR-Line)', '').strip()
        title = title.replace('(HDR)', '').replace('(HDRip)', '').replace('(DVDRip)', '').replace('(BR-SCREENER)', '').replace('(TS-SCREENER)', '').strip()

        title = title.replace('&#8217;', "'")

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        qlty = scrapertools.find_single_match(match, 'style=.*?<i>(.*?)</i>')
        if qlty == '---': qlty = ''

        lngs = []
        langs = scrapertools.find_multiple_matches(match, "data-src='.*?/images/(.*?).png'")

        for lang in langs:
            lng = ''

            if lang == 'espanol': lng = 'Esp'
            if lang == 'latino': lng = 'Lat'
            if lang == 'vose': lng = 'Vose'
            if lang == 'ingles': lng = 'Voi'

            if lng:
               if not lng in str(lngs):
                   if lng == 'Voi': lng = 'Vo'
                   lngs.append(lng)

        tipo = 'movie' if '/peliculas/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        title = title.replace('&#8211;', '').replace('&amp;', '').replace('&#8215;', ' ').replace('&#215;', 'x')

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        qualities=qlty, languages = ', '.join(lngs), fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': "-"} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            SerieName = url

            SerieName = SerieName.replace(host, '').replace('series/', '').strip()
            SerieName = SerieName.replace('-', ' ')

            if ' s0' in SerieName: SerieName = SerieName.split(" s0")[0]

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                        qualities=qlty, languages = ', '.join(lngs), fmt_sufijo=sufijo,
                                        contentSerieName = SerieName, contentType = 'tvshow', infoLabels={'year': "-"} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<span class="pagina pag_actual">.*?' + "<a href='(.*?)'")

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    if "temporada" in item.contentSerieName:
        SerieName = item.contentSerieName.split("temporada")[0]
        season = scrapertools.find_single_match(item.url, "-temporada-(.*?)-")
        episode = scrapertools.find_single_match(item.url, "-capitulo-(.*?)-")

    elif "S" in item.title:
        SerieName = item.title.split("S")[0]
        season = scrapertools.find_single_match(item.title, "S(.*?)E")
        episode = scrapertools.find_single_match(item.title, "E(.*?)$")

    else:
        SerieName = item.contentSerieName
        season = 0
        episode = 0

    itemlist.append(item.clone( action = 'findvideos', url = item.url, title = item.title, thumbnail = item.thumbnail, contentSerieName = SerieName,
                                contentSeason = season, contentType = 'episode', contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<div class="enlace_descarga"(.*?)</center>')

    links = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)"')

    for link in links:
        if '/tienda/' in link: continue

        other = ''
        if 'magnet' in link: other = 'Magnet'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = link, server = 'torrent',
                              language = item.languages, quality = item.qualities, other = other))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith('/'): item.url = host[:-1] + item.url

    url = item.url

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith('.torrent'):
        data = do_downloadpage(url)

        if not data:
            return 'Archivo [COLOR red]Corrupto[/COLOR]'

        if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
            return 'Archivo [COLOR red]Inexistente[/COLOR]'

        itemlist.append(item.clone( url = url, server = 'torrent' ))

    else:
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(url, host_torrent)

        if url_base64.startswith('magnet:'):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

        elif url_base64.endswith(".torrent"):
            data = do_downloadpage(url_base64)

            if not data or data == 'Fallo de consulta':
               return 'Archivo [COLOR red]Corrupto[/COLOR]'

            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+") + '&x=0&y=0'
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
