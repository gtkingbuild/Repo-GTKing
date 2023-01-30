# -*- coding: utf-8 -*-
# -*- Channel PelisPlay -*-
# -*- Created for Alfa Addon -*-
# -*- By the Alfa Development Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from channels import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import channeltools
from core import tmdb
from platformcode import config, logger
from channelselector import get_thumb

canonical = {
             'channel': 'pelisplay', 
             'host': config.get_setting("current_host", 'pelisplay', default=''), 
             'host_alt': ["https://www.pelisplay.co/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
__channel__ = canonical['channel']

forced_proxy_opt = None

try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
    __perfil__ = int(config.get_setting('perfil', __channel__))
except:
    __modo_grafico__ = True
    __perfil__ = 0

# Fijar perfil de color
perfil = [['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00', '0xFFFE2E2E', '0xFFFFD700'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E', '0xFFFE2E2E', '0xFFFFD700'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE', '0xFFFE2E2E', '0xFFFFD700']]
if __perfil__ < 3:
    color1, color2, color3, color4, color5 = perfil[__perfil__]
else:
    color1 = color2 = color3 = color4 = color5 = ""

headers = [['User-Agent', 'Mozilla/50.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'],
           ['Referer', host]]

parameters = channeltools.get_channel_parameters(__channel__)
fanart_host = parameters['fanart']
thumbnail_host = parameters['thumbnail']

IDIOMAS = {'Latino': 'LAT', 'Castellano': 'CAST', 'Subtitulado': 'VOSE'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['rapidvideo', 'streamango', 'fastplay', 'openload']


def get_source(url, soup=False, json=False, unescape=True, **opt):
    logger.info()

    opt['canonical'] = canonical
    data = httptools.downloadpage(url, **opt)

    if json:
        data = data.json
    else:
        data = data.data
        data = scrapertools.unescape(data) if unescape else data

        if soup:
            from bs4 import BeautifulSoup
            data = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return data


def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = [Item(
                    action = "menumovies",
                    channel = item.channel,
                    fanart = item.fanart,
                    text_blod = True,
                    thumbnail = get_thumb("channels_movie.png"),
                    title = "Peliculas",
                    viewType = "videos"
                ),

                Item(
                    action = "menuseries",
                    channel = item.channel,
                    extra = 'serie',
                    fanart = item.fanart,
                    mediatype = "tvshow",
                    text_blod = True,
                    thumbnail = get_thumb("channels_tvshow.png"),
                    title = "Series",
                    viewType = "videos"
                ),

                Item(
                    action = "flixmenu",
                    channel = item.channel,
                    extra = 'serie',
                    fanart = 'https://i.postimg.cc/jjN85j8s/netflix-logo.png',
                    mediatype = "tvshow",
                    text_blod = True,
                    thumbnail = 'https://i.postimg.cc/Pxs9zYjz/image.png',
                    title = "Netflix",
                    viewType = "videos"
                ),

                Item(
                    action = "search",
                    channel = item.channel,
                    extra='buscar',
                    text_blod = True,
                    title = "Buscar",
                    thumbnail = get_thumb('search.png'),
                    url = host + 'buscar'
                )
            ]
    autoplay.show_option(item.channel, itemlist)
    return itemlist


def menumovies(item):
    logger.info()

    item.viewType = 'movies'

    itemlist = [item.clone(
                    action = "peliculas",
                    text_blod=True,
                    title = "Estrenos",
                    url = host + 'peliculas-online?filtro=a%C3%B1o',
                ),

                item.clone(
                    action = "peliculas",
                    text_blod = True,
                    title = "Más Populares",
                    url = host + 'peliculas-online?filtro=visitas',
                ),

                item.clone(
                    action = "peliculas",
                    text_blod = True,
                    title = "Recíen Agregadas",
                    url = host + 'peliculas-online?filtro=fecha_creacion',
                ),

                item.clone(
                    action = "p_portipo",
                    extra = 'movie',
                    text_blod = True,
                    title = "Géneros",
                    url = host + 'peliculas-online',
                ),

                item.clone(
                    action = "search",
                    extra = 'buscarp',
                    text_blod = True,
                    thumbnail = get_thumb('search.png'),
                    title = "Buscar",
                    url = host + 'peliculas-online',
                )
            ]

    item.viewType = 'videos'

    return itemlist


def menuseries(item):
    logger.info()

    item.viewType = 'tvshows'

    itemlist = [item.clone(
                    action = "series",
                    title = "Novedades",
                    text_blod = True,
                    extra = 'serie',
                    mediatype = "tvshow",
                    url = host + 'series'
                ),

                item.clone(
                    action = "series",
                    extra = 'serie',
                    mediatype = "tvshow",
                    text_blod = True,
                    title = "Más Vistas",
                    url = host + 'series?filtro=visitas'
                ),

                item.clone(
                    action = "series",
                    extra = 'serie',
                    mediatype = "tvshow",
                    text_blod = True,
                    title = "Recíen Agregadas",
                    url = host + 'series?filtro=fecha_actualizacion'
                ),

                item.clone(
                    action = "p_portipo",
                    extra = 'serie',
                    text_blod = True,
                    title = "Géneros",
                    url = host + 'series'
                ),

                item.clone(
                    action = "search",
                    extra = 'buscars',
                    text_blod = True,
                    thumbnail = get_thumb('search.png'),
                    title = "Buscar",
                    url = host + 'series'
                )
            ]

    item.viewType = 'videos'

    return itemlist


def flixmenu(item):
    logger.info()

    itemlist = [item.clone(
                    action="flixmovies",
                    extra='movie',
                    mediatype="movie",
                    text_blod=True,
                    title="Películas",
                ),

                item.clone(
                    action="flixtvshow",
                    extra='serie',
                    mediatype="tvshow",
                    text_blod=True,
                    title="Series",
                ),

                item.clone(
                    action="search",
                    text_blod=True,
                    thumbnail=get_thumb('search.png'),
                    title="Buscar",
                    url=host + 'buscar'
                )
            ]

    return itemlist


def flixmovies(item):
    logger.info()

    item.viewType = 'movies'

    itemlist = [item.clone(
                    action="peliculas",
                    text_blod=True,
                    title="Novedades",
                    url=host + 'peliculas-online/netflix?filtro=fecha_actualizacion',
                ),

                item.clone(
                    action="peliculas",
                    text_blod=True,
                    title="Más Vistas",
                    url=host + 'peliculas-online/netflix?filtro=visitas',
                ),

                item.clone(
                    action="peliculas",
                    text_blod=True,
                    title="Recíen Agregadas",
                    url=host + 'peliculas-online/netflix?filtro=fecha_creacion',
                ),

                item.clone(
                    action="search",
                    extra="buscarp",
                    text_blod=True,
                    thumbnail=get_thumb('search.png'),
                    title="Buscar",
                    url=host + 'peliculas-online/netflix'
                )
            ]

    item.viewType = 'videos'

    return itemlist


def flixtvshow(item):
    logger.info()

    item.viewType = 'tvshows'

    itemlist = [item.clone(
                    action="series",
                    text_blod=True,
                    title="Novedades",
                    url=host + 'series/netflix?filtro=fecha_actualizacion',
                ),

                item.clone(
                    action="series",
                    text_blod=True,
                    title="Más Vistas",
                    url=host + 'series/netflix?filtro=visitas'
                ),

                item.clone(
                    action="series",
                    text_blod=True,
                    title="Recíen Agregadas",
                    url=host + 'series/netflix?filtro=fecha_creacion',
                ),

                item.clone(
                    action="search",
                    extra="buscars",
                    text_blod=True,
                    thumbnail=get_thumb('search.png'),
                    title="Buscar",
                    url=host + 'series/netflix'
                )
            ]

    item.viewType = 'videos'

    return itemlist


def p_portipo(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)
    data = scrapertools.replace(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)
    patron = '<li class="item"><a href="([^"]+)" class="category">.*?'  # url
    patron += '<div class="[^<]+<img class="[^"]+" src="([^"]+)"></div><div class="[^"]+">([^<]+)</div>'
    matches = scrapertools.find_multiple_matches(data, patron)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        action = 'peliculas' if item.extra == 'movie' else 'series' if item.extra == 'serie' else ''

        itemlist.append(
            item.clone(
                action=action,
                thumbnail=scrapedthumbnail,
                title=scrapedtitle,
                url=scrapedurl
            )
        )

    itemlist.sort(key=lambda it: it.title)

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    # action = ''
    # contentType = ''
    data = get_source(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)
    patron = '<img class="posterentrada" src="([^"]+)".*?'          # img
    patron += '<a href="([^"]+)">.*?'                               # url
    patron += '<p class="description_poster">.*?\(([^<]+)\)<\/p>.*?'  # year
    patron += '<div class="Description"> <div>([^<]+)<\/div>.*?'    # plot
    patron += '<strong>([^<]+)<\/strong><\/h4>'                     # title

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, year, plot, scrapedtitle in matches:

        new_item = Item(
                    channel=item.channel,
                    infoLabels={"year": year},
                    plot=plot,
                    thumbnail=host + scrapedthumbnail,
                    title=scrapedtitle,
                    url=scrapedurl,
                )
        
        if 'serie' in scrapedurl:
            new_item.action = 'temporadas'
            new_item.contentType = 'tvshow'
            new_item.contentSerieName = scrapedtitle
            new_item.title += ' [COLOR blue](Serie)[/COLOR]'

        else:
            new_item.action = 'findvideos'
            contentType = 'movie'
            new_item.contentTitle = scrapedtitle

        itemlist.append(new_item)


    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    pagination = scrapertools.find_single_match(data, '<li><a href="([^"]+)" rel="next">')

    if pagination:
        itemlist.append(
            Item(
                action="peliculas",
                channel=__channel__,
                folder=True,
                text_blod=True,
                thumbnail=get_thumb("next.png"),
                title="» Siguiente »",
                url=pagination,
            )
        )

    return itemlist


def search(item, texto):
    logger.info()

    texto = texto.replace(" ", "+")
    item.url = urlparse.urljoin(item.url, "?q={0}".format(texto))

    if item.extra == 'buscarp' or item.extra == 'buscars':
        item.url = urlparse.urljoin(item.url, "?buscar={0}".format(texto))

    try:
        if item.extra == 'buscars':
            return series(item)
        else:
            return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys

        for line in sys.exc_info():
            logger.error("{0}".format(line))

        return []


def newest(categoria):
    logger.info()

    itemlist = []
    item = Item()

    try:
        if categoria == 'peliculas':
            item.url = host + 'peliculas/estrenos/'

        elif categoria == 'infantiles':
            item.url = host + "peliculas/animacion/"

        elif categoria == 'terror':
            item.url = host + "peliculas/terror/"

        else:
            return []

        itemlist = peliculas(item)

        if itemlist[-1].title == "» Siguiente »":
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys

        for line in sys.exc_info():
            logger.error("{0}".format(line))

        return []

    return itemlist


def series(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)
    patron = '<img class="portada" src="([^"]+)"><[^<]+><a href="([^"]+)".*?'
    patron += 'class="link-title"><h2>([^<]+)<\/h2>'  # title
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(
                action="temporadas",
                channel=__channel__,
                contentSerieName=scrapedtitle,
                contentType='tvshow',
                extra='serie',
                thumbnail=host + scrapedthumbnail,
                title=scrapedtitle,
                url=scrapedurl
            )
        )

    tmdb.set_infoLabels(itemlist, __modo_grafico__)

    pagination = scrapertools.find_single_match(data, '<li><a href="([^"]+)" rel="next">')

    if pagination:
        itemlist.append(
            Item(
                action="series",
                channel=__channel__,
                thumbnail=get_thumb("next.png"),
                title="» Siguiente »",
                url=pagination
            )
        )

    return itemlist


def temporadas(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)
    patron = '<img class="posterentrada"\s*src="([^"]+)"\s*alt="\w+\s*(\w+).*?'
    patron += 'class="abrir_temporada"\s*href="([^"]+)">'  # img, season
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 1:
        for scrapedthumbnail, temporada, url in matches:
            new_item = item.clone(
                            action="episodesxseason",
                            extra='serie',
                            season=temporada,
                            thumbnail=host + scrapedthumbnail,
                            url=url
                        )

            new_item.infoLabels['season'] = temporada
            new_item.extra = ""
            itemlist.append(new_item)

        tmdb.set_infoLabels(itemlist, __modo_grafico__)

        for i in itemlist:
            i.title = "%s. %s" % (
                i.infoLabels['season'], i.infoLabels['tvshowtitle'])

            if i.infoLabels['title']:
                # Si la temporada tiene nombre propio añadírselo al titulo del item
                i.title += " - %s" % (i.infoLabels['title'])

            if 'poster_path' in i.infoLabels:
                # Si la temporada tiene poster propio remplazar al de la serie
                i.thumbnail = i.infoLabels['poster_path']

        # itemlist.sort(key=lambda it: it.title)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(
                action="add_serie_to_library",
                category="Series",
                channel=__channel__,
                contentSerieName=item.contentSerieName,
                extra="episodios",
                fanart=fanart_host,
                text_color=color1,
                thumbnail=get_thumb("videolibrary_tvshow.png"),
                title="Añadir esta serie a la videoteca",
                url=item.url
            )
        )
        return itemlist

    else:
        return episodesxseason(item)


def episodios(item):
    logger.info()

    itemlist = []
    templist = temporadas(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)
    post_link = '%sentradas/abrir_temporada' % host
    token = scrapertools.find_single_match(data, 'data-token="([^"]+)">')
    data_t = scrapertools.find_single_match(data, '<a data-s="[^"]+" data-t="([^"]+)"')
    data_s = scrapertools.find_single_match(data, '<a data-s="([^"]+)" data-t="[^"]+"')
    post = {'t': data_t, 's': data_s, '_token': token}
    json_data = get_source(post_link, json=True, post=post, forced_proxy_opt=forced_proxy_opt)

    if not json_data:
        return itemlist

    for element in json_data['data']['episodios']:
        scrapedname = element['titulo']
        episode = element['metas_formateadas']['nepisodio']
        season = element['metas_formateadas']['ntemporada']
        scrapedurl = element['url_directa']

        if 'season' in item.infoLabels and int(item.infoLabels['season']) != int(season): continue

        title = "%sx%s: %s" % (season, episode.zfill(2), scrapertools.unescape(scrapedname))
        new_item = item.clone(
                        action="findvideos",
                        contentTitle=title,
                        contentType="episode",
                        extra='serie',
                        text_color=color3,
                        title=title,
                        url=scrapedurl
                    )

        if 'infoLabels' not in new_item:
            new_item.infoLabels = {}

        new_item.infoLabels['season'] = season
        new_item.infoLabels['episode'] = episode.zfill(2)
        itemlist.append(new_item)

    # TODO no hacer esto si estamos añadiendo a la videoteca
    if not (item.videolibrary or item.extra):
        # Obtenemos los datos de todos los capítulos de la temporada mediante multihilos
        tmdb.set_infoLabels(itemlist, __modo_grafico__)

        for i in itemlist:
            if i.infoLabels['title']:
                # Si el capitulo tiene nombre propio añadírselo al titulo del item
                i.title = "%sx%s: %s" % (
                    i.infoLabels['season'], i.infoLabels['episode'], i.infoLabels['title'])

            if 'poster_path' in i.infoLabels:
                # Si el capitulo tiene imagen propia remplazar al poster
                i.thumbnail = i.infoLabels['poster_path']

    itemlist.sort(key=lambda it: int(it.infoLabels['episode']),
                      reverse=config.get_setting('orden_episodios', __channel__))

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|<br>", "", data)
    patron = 'data-player="([^"]+)"[^>]+>([^<]+)</div>.*?'
    patron += '<td class="[^"]+">([^<]+)</td><td class="[^"]+">([^<]+)</td>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for data_player, servername, quality, lang in matches:
        post_link = '%sentradas/procesar_player' % host
        token = scrapertools.find_single_match(data, 'data-token="([^"]+)">')
        post = {'data': data_player, 'tipo': 'videohost', '_token': token}
        json_data = get_source(post_link, json=True, post=post, forced_proxy_opt=forced_proxy_opt)
        url = json_data.get('data', '')

        if not url: continue

        if 'pelisplay.co/embed/' in url:
            new_data = get_source(url)
            url = scrapertools.find_single_match(
                new_data, '"file":"([^"]+)",').replace('\\', '')

        elif 'fondo_requerido' in url:
            link = scrapertools.find_single_match(url, '=(.*?)&fondo_requerido').partition('&')[0]
            post_link = '%sprivate/plugins/gkpluginsphp.php' % host
            post = {'link': link}
            new_data2 = get_source(post_link, post=post)
            url = scrapertools.find_single_match(new_data2, '"link":"([^"]+)"').replace('\\', '')

        idioma = {'latino': '[COLOR cornflowerblue](LAT)[/COLOR]',
                  'castellano': '[COLOR green](CAST)[/COLOR]',
                  'subtitulado': '[COLOR red](VOSE)[/COLOR]'}

        lang = lang.lower().strip()
        lang = idioma.get(lang, lang)

        if servername.lower() == "tazmania":
            servername = "fembed"

        title = "Ver en: [COLOR yellowgreen](%s)[/COLOR] [COLOR yellow](%s)[/COLOR] %s" % (
            servername.title(), quality, lang)

        itemlist.append(
            item.clone(
                action='play',
                channel=__channel__,
                language=lang,
                quality=quality,
                title=title,
                url=url
            )
        )

    itemlist = servertools.get_servers_itemlist(itemlist)
    itemlist.sort(key=lambda it: it.language, reverse=False)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'serie':
        itemlist.append(
            Item(
                action="add_pelicula_to_library",
                channel=__channel__,
                contentTitle=item.contentTitle,
                extra="findvideos",
                thumbnail=get_thumb("videolibrary_movie.png"),
                title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                url=item.url
            )
        )

    return itemlist
