# -*- coding: utf-8 -*-
import sys
import re
import datetime
import xbmcgui

PY3 = False
if sys.version_info[0] >= 3:
    import urllib.parse as urllib       # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                       # Usamos el nativo de PY2 que es más rápido

from bs4 import BeautifulSoup
from core import httptools, scrapertools, servertools, tmdb, jsontools
from core.item import Item
from platformcode import config, logger, platformtools
from channelselector import get_thumb
from channels import autoplay
from lib import strptime_fix

canonical = {
             'channel': 'hentaila', 
             'host': config.get_setting("current_host", 'hentaila', default=''), 
             'host_alt': ["https://hentaila.com"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


IDIOMAS = {'VOSE': 'VOSE'}
SEEK_TMDB = config.get_setting('seek_tmdb', channel='hentaila')
SEEK_TMDB_LIST_ALL = not config.get_setting('seek_tmdb_only_in_episodes', channel='hentaila')
PREFER_TMDB_REVIEW = config.get_setting('prefer_tmdb_review', channel='hentaila')

list_language = list(IDIOMAS.values())
list_servers = ['mega', 'fembed', 'mp4upload', 'yourupload', 'sendvid']
list_quality = []

def mainlist(item):
    logger.info()
    itemlist = []
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(
        Item(
            action = "newest",
            channel = item.channel,
            fanart = item.fanart,
            title = "Novedades",
            thumbnail = get_thumb("newest", auto=True),
            viewType = "videos"
        )
    )
    itemlist.append(
        Item(
            action = "list_all",
            channel = item.channel,
            fanart = item.fanart,
            param = "",
            title = "Populares",
            thumbnail = get_thumb("more watched", auto=True),
            url = host + "/directorio?filter=popular"
        )
    )
    itemlist.append(
        Item(
            action = "list_all",
            channel = item.channel,
            fanart = item.fanart,
            param = "hot",
            title = "Destacados de la semana",
            thumbnail = get_thumb("hot", auto=True),
            url = host
        )
    )
    itemlist.append(
        Item(
            action = "list_all",
            channel = item.channel,
            fanart = item.fanart,
            param = "newepisodes",
            title = "Nuevos episodios",
            thumbnail = get_thumb("new episodes", auto=True),
            url = host
        )
    )
    itemlist.append(
        Item(
            action = "premieres",
            channel =  item.channel,
            fanart = item.fanart,
            param = "",
            title = "Estrenos próximos",
            thumbnail = get_thumb("premieres", auto=True),
            url = host + '/estrenos-hentai'
        )
    )
    itemlist.append(
        Item(
            action = "categories",
            channel = item.channel,
            fanart = item.fanart,
            param = "",
            title = "Directorio Hentai (Categorías)",
            thumbnail = get_thumb("categories", auto=True),
            url = host,
            viewType = "–"
        )
    )
    itemlist.append(
        Item(
            action = "list_all",
            channel = item.channel,
            fanart = item.fanart,
            param = "",
            title = "Todos",
            thumbnail = get_thumb("all", auto=True),
            url = host + "/directorio"
        )
    )
    itemlist.append(
        Item(
            action = "search",
            channel = item.channel,
            fanart = item.fanart,
            param = "",
            title = "Buscar...",
            thumbnail = get_thumb("search", auto=True),
            url = host + "/api/search"
        )
    )
    itemlist.append(
        Item(
            action = "setting_channel",
            channel = item.channel,
            plot = "Configurar canal",
            title = "Configurar canal", 
            thumbnail = get_thumb("setting_0.png")
        )
    )
    autoplay.show_option(item.channel, itemlist)
    return itemlist

def setting_channel(item):
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret

def categories(item):
    logger.info()
    itemlist = []
    itemlist.append(
        Item(
            action = "filter_by_selection",
            channel = item.channel,
            fanart = item.fanart,
            param = "genre",
            plot = "Yuri, Yaoi, Tentáculos, Lolis, Vanilla, Netorare, Súcubos, Ahegao, etc.",
            thumbnail = get_thumb("genres", auto=True),
            title = "Por género"
        )
    )
    itemlist.append(
        Item(
            action = "filter_by_selection",
            channel = item.channel,
            fanart = item.fanart,
            param = "alphabet",
            plot = "A-Z",
            thumbnail = get_thumb("alphabet", auto=True),
            title = "Por letra"
        )
    )
    itemlist.append(
        Item(
            action = "list_all",
            channel = item.channel,
            fanart = item.fanart,
            param = "",
            plot = "Adiós, píxeles y barras negras 7u7",
            thumbnail = get_thumb("adults", auto=True),
            title = "Sin censura",
            url = host + "/hentai-sin-censura"
        )
    )
    itemlist.append(
        Item(
            action = "filter_by_selection",
            channel = item.channel,
            fanart = item.fanart,
            param = "status",
            plot = "En emisión y finalizados",
            thumbnail = get_thumb("on air", auto=True),
            title = "Por estado"
        )
    )
    itemlist.append(
        Item(
            action = "set_adv_filter",
            channel = item.channel,
            fanart = item.fanart,
            filters = {'genre': '', 'alphabet': '', 'censor': '', 'status': '', 'orderby': ''},
            param = "",
            plot = "Refinar la búsqueda combinando género, estado, sin censura, etc.",
            thumbnail = get_thumb("categories", auto=True),
            title = "Combinar criterios"
        )
    )
    return itemlist

def create_soup(url, post=None, headers=None):
    logger.info()

    data = httptools.downloadpage(url, post=post, headers=headers, canonical=canonical).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup

def labeler_async(itemlist, seekTmdb=False):
    import threading

    threads_num = config.get_setting("tmdb_threads", default=20)
    semaforo = threading.Semaphore(threads_num)
    lock = threading.Lock()
    r_list = list()
    i = 0
    l_hilo = list()

    def sub_thread(_item, _i, _seekTmdb):
        semaforo.acquire()
        ret = labeler(_item, _seekTmdb)
        semaforo.release()
        r_list.append((_i, _item, ret))

    for item in itemlist:
        t = threading.Thread(target = sub_thread, args = (item, i, seekTmdb))
        t.start()
        i += 1
        l_hilo.append(t)

    # esperar q todos los hilos terminen
    for x in l_hilo:
        x.join()

    # Ordenar lista de resultados por orden de llamada para mantener el mismo orden q itemlist
    r_list.sort(key=lambda i: i[0])

    # Reconstruir y devolver la lista solo con los resultados de las llamadas individuales
    return [ii[2] for ii in r_list]

def labeler(item, seekTmdb=False):
    logger.info()
    tmdb.set_infoLabels(item, seekTmdb, include_adult=True)
    if item.infoLabels['tmdb_id'] == '':
        item.infoLabels['first_air_date'] = ''
        item.infoLabels['year'] = ''
        tmdb.set_infoLabels(item, seekTmdb, include_adult=True)
    return item

def filter_by_selection(item, clearUrl=False):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(host + "/directorio", canonical=canonical).data
    if item.param == 'genre':
        pattern = '(?s)a href="([^"]+)" class="">([^<]+)'
        matches = scrapertools.find_multiple_matches(data, pattern)
    elif item.param == 'alphabet':
        sectptn = '(?s)class="alpha-list".+?/section>'
        sectmatch = scrapertools.find_single_match(data, sectptn)
        pattern = '(?s)a href="([^"]+).+?>([^<]+)'
        matches = scrapertools.find_multiple_matches(sectmatch, pattern)
    elif item.param == 'censor':
        matches = (dict({'?uncensored=on': 'Solo sin censura'}).items)()
    elif item.param == 'status':
        matches = dict({'?status%5B1%5D=on': 'Solo en emisión',
                        '?status%5B2%5D=on': 'Solo finalizados'}).items()
    elif item.param == 'orderby':
        matches = dict({'?filter=popular': 'Ordenar por popularidad',
                        '?filter=recent': 'Ordenar por más recientes'}).items()
    for url, title in matches:
        if clearUrl == True:
            url = url.replace('?', '')
        else:
            if item.param != 'genre':
                url = '/directorio' + url
            url = host + url
        itemlist.append(
            Item(
                action = "list_all",
                channel = item.channel,
                title = title,
                fanart = item.fanart,
                url = url,
            )
        )
    return itemlist

def set_adv_filter(item):
    logger.info()
    genreitems = filter_by_selection(Item(param = "genre"), clearUrl = True)
    genres = ['Predeterminado (todos)']
    for i in genreitems:
        genres.append(i.title)
    result = platformtools.dialog_select('Elige un género', genres, useDetails=False)
    if result != -1 and result != 0:
        item.filters['genre'] = genreitems[result - 1]
    elif result == -1:
        return True

    alphaitems = filter_by_selection(Item(param = "alphabet"), clearUrl = True)
    letters = []
    letters.append('Predeterminado (todas)')
    for i in alphaitems:
        letters.append(i.title)
    result = platformtools.dialog_select('Elige una letra inicial', letters, useDetails=False)
    if result != -1 and result != 0:
        item.filters['alphabet'] = alphaitems[result - 1]
    elif result == -1:
        return True

    censorstates = filter_by_selection(Item(param = "censor"), clearUrl = True)
    censor = []
    censor.append('Predeterminado (con y sin censura)')
    for i in censorstates:
        censor.append(i.title)
    result = platformtools.dialog_select('Elige el tipo de censura', censor, useDetails=False)
    if result != -1 and result != 0:
        item.filters['censor'] = censorstates[result - 1]
    elif result == -1:
        return True

    statusstates = filter_by_selection(Item(param = "status"), clearUrl = True)
    statuses = []
    statuses.append('Predeterminado (ambos)')
    for i in statusstates:
        statuses.append(i.title)
    result = platformtools.dialog_select('Elige el estado de emisión', statuses, useDetails=False)
    if result != -1 and result != 0:
        item.filters['status'] = statusstates[result - 1]
    elif result == -1:
        return True

    statusstates = filter_by_selection(Item(param = "orderby"), clearUrl = True)
    statuses = []
    statuses.append('Predeterminado (ambos)')
    for i in statusstates:
        statuses.append(i.title)
    result = platformtools.dialog_select('Elige cómo ordenar los resultados', statuses, useDetails=False)
    if result != -1 and result != 0:
        item.filters['orderby'] = statusstates[result - 1]

    if item.filters['genre'] or item.filters['alphabet'] or item.filters['censor'] or item.filters['status'] or item.filters['orderby']:
        filtered_url = host
        current_filter = ''
        if item.filters['genre'] != '':
            current_filter += "Género: " + item.filters['genre'].title + ". "
            filtered_url += item.filters['genre'].url
        else:
            filtered_url += '/directorio'
        if item.filters['alphabet'] != '':
            current_filter += 'Inicial: ' + item.filters['alphabet'].title + '. '
            filtered_url += '?' + item.filters['alphabet'].url
        if item.filters['censor'] != '':
            current_filter += 'Censura: ' + item.filters['censor'].title + '. '
            filtered_url += '&' + item.filters['censor'].url
        if item.filters['status'] != '':
            current_filter += 'Estado: ' + item.filters['status'].title + '. '
            filtered_url += '&' + item.filters['status'].url
        if item.filters['orderby'] != '':
            current_filter += 'Estado: ' + item.filters['orderby'].title + '. '
            filtered_url += '&' + item.filters['orderby'].url
        filteritem = Item(
            channel =  item.channel,
            fanart = item.fanart,
            param = '',
            url = filtered_url
        )
        return list_all(filteritem)
    else:
        return True

def premieres(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    infoLabels = item.infoLabels
    sectionptn = '(?s)<section class="section section-premier-slider".+?'
    sectionptn += 'section-title[^>]+.([^<]+)'
    sectionptn += '(.+?/section>)'
    sections = scrapertools.find_multiple_matches(data, sectionptn)
    pattern = '(?s)article class="hentai".+?img src=".+?(\d.+?)\..+?".+?'
    pattern += 'h-title[^>]+.([^<]+).+?'
    pattern += 'a href="([^"]+).+?/article>'
    for sectiontitle, section in sections:
        itemlist.append(
            Item(
                channel = item.channel,
                title = '[COLOR=yellow] ═↓═ ' + sectiontitle + ' ═↓═ [/COLOR]',
                thumbnail = host + '/assets/img/media.webp',
                fanart = item.fanart,
            )
        )
        match = scrapertools.find_multiple_matches(section, pattern)
        for scpthumbid, scptitle, scpurl in match:
            itemlist.append(
                Item(
                    action = "episodios",
                    channel = item.channel,
                    contentSerieName = scptitle.strip(),
                    fanart = host + '/uploads/fondos/' + scpthumbid + '.jpg',
                    infoLabels = infoLabels,
                    title = scptitle.strip(),
                    thumbnail = host + '/uploads/portadas/' + scpthumbid + '.jpg',
                    url = host + scpurl
                )
            )
    return itemlist

def newest(categoria):
    item = Item()
    item.action = "newest"
    item.channel = "hentaila"
    item.param = ""
    item.thumbnail = get_thumb("newest", auto=True)
    item.title = "Novedades"
    item.url = host + "/directorio?filter=recent"
    return list_all(item)

def list_all(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)

    if item.param == 'hot':
        section = soup.find('section', class_='latest-hentais section top').div.find_all('div', class_='item')

        for article in section:
            infoLabels = {}
            infoLabels['plot'] = str(article.find('div', class_='h-content').p.string)
            scpthumbid = scrapertools.find_single_match(article.find('figure', class_='bg').img['src'], '.+?(\d+)\.')
            logger.info(scpthumbid)
            title = str(article.find('h2', class_='h-title').a.string)
            itemlist.append(
                Item(
                    action = "episodesxseason",
                    channel = item.channel,
                    contentSerieName = title,
                    fanart = host + '/uploads/fondos/' + scpthumbid + '.jpg',
                    infoLabels = infoLabels,
                    title = title,
                    thumbnail = host + '/uploads/portadas/' + scpthumbid + '.jpg',
                    url = host + article.find('h2', class_='h-title').a['href']
                )
            )

        labeler_async(itemlist, seekTmdb = SEEK_TMDB_LIST_ALL)

    elif item.param == 'newepisodes':
        section = soup.find('section', class_='section episodes').find('div', class_='grid episodes').find_all('article', class_='hentai episode')

        for article in section:
            infoLabels = {}
            scptime = str(article.find('header', class_='h-header').time.string)
            scpthumbnail = article.find('img')['src']
            scpurl = scrapertools.find_single_match(article.find('a')['href'], '/ver/(.+?)-\d+$')
            infoLabels['episode'] = int(scrapertools.find_single_match(str(article.find('span', class_='num-episode').string), '.+?(\d+)'))
            infoLabels['season'] = 1
            infoLabels['title'] = str(article.find('h2', class_='h-title').string)
            infoLabels['plot'] = 'Publicado ' + scptime
            itemlist.append(
                Item(
                    action = "episodesxseason",
                    channel = item.channel,
                    contentSerieName = infoLabels['title'],
                    fanart = host + scpthumbnail,
                    infoLabels = infoLabels,
                    title = 'E' + str(infoLabels['episode']) + ': ' + infoLabels['title'],
                    thumbnail = host + scpthumbnail,
                    thumbnail_backup = host + scpthumbnail,
                    url = host + '/hentai-' + scpurl
                )
            )

        labeler_async(itemlist, seekTmdb = SEEK_TMDB_LIST_ALL)

        for i in itemlist:
            i.thumbnail = i.thumbnail_backup

    else:
        if 'directorio' in item.url:
            pattern = '(?s)class="hentai".+?img.+?src=".+?(\d+?)\..+?".+?class="favorites.+?>([^<]+).+?h-title.+?>([^<]+).+?href="([^"]+)'
            pre_matches = scrapertools.find_multiple_matches(str(soup), pattern)
            matches = []
            for scpthumbid, scpfavs, scptitle, scpurl in pre_matches:
                matches.append((scpthumbid, "{} en favoritos".format(scpfavs), scptitle, scpurl))
        else:
            pattern = '(?s)class="hentai".+?img.+?src=".+?(\d+?)\..+?".+?h-title.+?>([^<]+).+?href="([^"]+)'
            pre_matches = scrapertools.find_multiple_matches(str(soup), pattern)
            matches = []
            for scpthumbid, scptitle, scpurl in pre_matches:
                matches.append((scpthumbid, "", scptitle, scpurl))

        for scpthumbid, scpfavs, scptitle, scpurl in matches:
            infoLabels = {}
            itemlist.append(
                Item(
                    action = "episodesxseason",
                    channel = item.channel,
                    contentSerieName = scptitle.strip(),
                    fanart = host + '/uploads/fondos/' + scpthumbid + '.jpg',
                    infoLabels = infoLabels,
                    plot = scpfavs,
                    title = scptitle.strip(),
                    thumbnail = host + '/uploads/portadas/' + scpthumbid + '.jpg',
                    url = host + scpurl
                )
            )

        labeler_async(itemlist, seekTmdb = SEEK_TMDB_LIST_ALL)

    nextpage = soup.find('a', class_='btn rnd npd fa-arrow-right')

    if nextpage:
        itemlist.append(
            Item(
                action = 'list_all',
                channel =  item.channel,
                fanart = item.fanart,
                param = item.param,
                title =  '[COLOR orange]Siguiente página > [/COLOR]',
                url = host + nextpage['href']
            )
        )

    return itemlist

def episodios(item):
    logger.info()
    itemlist = []
    itemlist.extend(episodesxseason(item, True))
    return itemlist

def episodesxseason(item, get_episodes = False):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    labeler_async([item], seekTmdb = SEEK_TMDB)
    infoLabels = item.infoLabels

    infoLabels['plot'] = str(soup.find('div', class_='h-content').p.string)
    infoLabels['rating'] = float(soup.find('div', class_='h-rating').p.contents[0])
    infoLabels['status'] = scrapertools.find_single_match(str(soup), '(?s)class="status-.*?>.*?>.*?>([^<]+)').strip()
    infoLabels['season'] = 1
    infoLabels['genre'] += infoLabels['status']
    infoLabels['tvshowtitle'] = item.title
    infoLabels['votes'] = int(soup.find('div', class_='h-rating').p.span.span.string)
    epmatch = soup.find('div', class_='episodes-list').find_all('article')
    genmatch = soup.find('nav', class_='genres').find_all('a', class_='btn sm')

    if genmatch:
        if not infoLabels['genre']:
            infoLabels['genre'] = str(genmatch[0].string)
            genmatch = genmatch[1:]
        for i in range(len(genmatch)):
            infoLabels['genre'] += ', ' + str(genmatch[i].string)
    for article in epmatch:
        scpepnum = str(article.find('h2', class_='h-title').string)
        scpepnum = int(scrapertools.find_single_match(scpepnum, '(\d+)$'))
        scpdate = str(article.find('header', class_='h-header').find('time').string)
        date = datetime.datetime.strptime(scpdate, "%B %d, %Y")
        infoLabels['first_air_date'] = date.strftime("%Y/%m/%d")
        infoLabels['premiered'] = infoLabels['first_air_date']
        infoLabels['year'] = date.strftime("%Y")
        infoLabels['episode'] = scpepnum
        title = scrapertools.get_season_and_episode(str(item.infoLabels['season']) + 'x' + str(item.infoLabels['episode'])) + ': ' + item.contentSerieName

        itemlist.append(
            item.clone(
                action = "findvideos",
                channel = item.channel,
                contentTitle = item.title,
                fanart = item.fanart,
                infoLabels = infoLabels,
                title = title,
                thumbnail = host + article.find('div', class_='h-thumb').find('img')['src'],
                url = host + article.find('a')['href']
            )
        )
    itemlist.reverse()
    labeler_async(itemlist, seekTmdb = SEEK_TMDB)

    for i in itemlist:
        if i.infoLabels.get('title'):
            i.title = scrapertools.get_season_and_episode(str(i.infoLabels['season']) + 'x' + str(i.infoLabels['episode'])) + ': ' + i.infoLabels['title']
        if not PREFER_TMDB_REVIEW:
            i.infoLabels['plot'] = infoLabels['plot']

        preplot  = "[I][COLOR=lime]Votos:[/COLOR] [COLOR=beige]{} ({} votos)[/COLOR]\n\n".format(infoLabels['rating'], infoLabels['votes'])
        preplot += "[COLOR=lime]Géneros:[/COLOR] [COLOR=yellow]{}[/COLOR][/I]".format(infoLabels['genre'])
        i.infoLabels['plot'] = "{}\n\n{}".format(preplot, i.infoLabels['plot'])

    if not get_episodes:
        premiereptn = '(?s)class="content-title".+?>(\d+?-\d+?-\d+?)<'
        premiere = scrapertools.find_single_match(str(soup), premiereptn)
        if premiere:
            itemlist.append(
                Item(
                    channel = item.channel,
                    fanart = item.fanart,
                    title = 'Estreno próximo episodio: ' + premiere,
                    thumbnail = item.thumbnail,
                )
            )
        if config.get_videolibrary_support() and len(itemlist) > 0:
            if itemlist[0].infoLabels['tmdb_id']:
                itemlist.append(
                    Item(
                        channel = item.channel,
                        title = '[COLOR yellow]{}[/COLOR]'.format(config.get_localized_string(30161)),
                        url = item.url,
                        action = "add_serie_to_library",
                        extra = "episodios",
                        contentSerieName = item.contentSerieName
                    )
                )

        if logger.info() != False:
            itemlist.append(
                Item(
                    action = "comments",
                    channel = item.channel,
                    fanart = item.fanart,
                    title = "Ver comentarios",
                    url = item.url
                )
            )
    return itemlist

def findvideos(item):
    logger.info()
    itemlist = []
    data =  jsontools.load(
                scrapertools.find_single_match
                    (httptools.downloadpage(item.url, canonical=canonical).data,
                    '(?s)var (?:videos|video) = (.+?);'
                )
            )
    urls = ''
    for i in data:
        urls += '<a href="' + i[1] + '"></a>'
    itemlist.extend(servertools.find_video_items(item = item, data = urls))
    itemlist = servertools.get_servers_itemlist(itemlist, None, True)
    for video in itemlist:
        video.channel = item.channel
        video.contentTitle = item.title
        video.fanart = item.thumbnail
        video.infoLabels = item.infoLabels
        video.title = video.title.replace((config.get_localized_string(70206) % ''), '')
        video.title = video.title.title() + ' [' + item.contentSerieName + ']'
        video.thumbnail = item.thumbnail
    if logger.info() != False:
        itemlist.append(
            Item(
                action = "comments",
                channel = item.channel,
                fanart = item.fanart,
                title = "Ver comentarios del episodio",
                url = item.url
            )
        )

    autoplay.start(itemlist, item)

    return itemlist

def comments(item):
    logger.info()
    itemlist = []
    apipage = httptools.downloadpage('https://hentaila-1.disqus.com/embed.js').data
    apikey = scrapertools.find_single_match(apipage, 'getLoaderVersionFromUrl\(".+?lounge.load\.([^\.]+)')

    base_url = 'https://disqus.com/embed/comments/?base=default&f=hentaila-1&t_u='
    source_url = urllib.quote(item.url, safe = '')
    param_url = '&s_o=default#version='
    url = base_url + source_url + param_url + apikey
    raw_data = httptools.downloadpage(url).data
    raw_jsonptn = 'id="disqus-threadData">([^<]+)</script>'
    raw_comments = (jsontools.load(scrapertools.find_single_match(raw_data, raw_jsonptn)))['response']['posts']

    for comment in raw_comments:
        author = comment['author']['name']
        image = ''
        url = ''
        # Buscamos si hay enlaces a imágenes de disqus para mostrarlas
        if scrapertools.find_single_match(comment['raw_message'], '(?s)(?:http|https)://.+?\.disquscdn\.com/images/') != '':
            image = 'https://uploads.disquscdn.com' + scrapertools.find_single_match(comment['raw_message'], '(?s)disquscdn\.com(/.+?)(?:$|\s|\\n)')
        # Buscamos si hay enlaces a HLA para mostrar redirecciones
        if scrapertools.find_single_match(comment['raw_message'], '(?s)hentaila\.com(/.+?)(?:$|\s|\\n)') != '':
            url = 'https://hentaila.com' + scrapertools.find_single_match(comment['raw_message'], '(?s)hentaila\.com(/.+?)(?:$|\s|\\n)')
        listitem = Item(
            action = 'show_actions',
            author = author,
            channel = item.channel,
            comment = comment['raw_message'],
            contentPlot = comment['raw_message'],
            id = str(comment['id']),
            nesting = 0,
            parent = str(comment['parent']),
            thumbnail = image,
            title = author,
            url = url
        )
        parentindicator = ''
        if len(itemlist) > 0:
            # Verificamos si el comentario es respuesta a otro comentario
            if itemlist[-1].parent != 'null':
                # Verificamos si el comentario anterior es el padre
                # Si no es el padre, verificamos si es del mismo padre que el anterior
                # Agregamos nesting para mantener respuestas por nivel
                if listitem.parent == itemlist[-1].id:
                    listitem.nesting = itemlist[-1].nesting + 1
                elif itemlist[-1].nesting > 0:
                    # Si no, buscamos si hay padres arriba
                    for i in range(len(itemlist) -1, -1, -1):
                        if itemlist[i].nesting > 0:
                            if listitem.parent == itemlist[i].parent:
                                listitem.nesting = itemlist[i].nesting
                        else:
                            break
                nestlevelmark = ''
                for i in range(listitem.nesting):
                    nestlevelmark += ' ^ '
                listitem.title = nestlevelmark + listitem.title
        itemlist.append(listitem)
    return itemlist

def show_actions(item):
    logger.info()
    actions = ['Ver comentario', 'Ir a enlace de HLA']
    selection = None
    if not (logger.info() == False and isinstance(logger.info(), bool)):
        if item.url != '':
            selection = xbmcgui.Dialog().contextmenu(actions)
        if selection == 0 or item.url == '':
            platformtools.dialog_textviewer(item.author, item.comment)
            return True
        elif selection == 1:
            if scrapertools.find_single_match(item.url, '/ver/') != '':
                return findvideos(item)
            else:
                return episodesxseason(item)

def search(item, text):
    logger.info()
    itemlist = []
    if text != '':
        try:
            results = httptools.downloadpage(item.url, post = str('value=' + text)).json
            for result in results:
                itemlist.append(
                    Item(
                        action = "episodesxseason",
                        channel = item.channel,
                        contentSerieName = result['title'],
                        fanart = host + '/uploads/fondos/' + result['id'] + '.jpg',
                        title = result['title'],
                        thumbnail = host + '/uploads/portadas/' + result['id'] + '.jpg',
                        url = host + '/hentai-' + result['slug']
                    )
                )
            return itemlist
        except:
            for line in sys.exc_info():
                logger.error("%s" % line)
            return itemlist