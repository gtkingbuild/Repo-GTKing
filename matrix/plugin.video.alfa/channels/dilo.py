# -*- coding: utf-8 -*-
# -*- Channel Dilo -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urllib
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido
    import urllib

import re

from channels import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channelselector import get_thumb

IDIOMAS = {'Español': 'CAST', 'Latino': 'LAT', 'Subtitulado': 'VOSE'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['openload', 'streamango', 'powvideo', 'clipwatching', 'streamplay', 'streamcherry', 'gamovideo']

forced_proxy_opt = 'ProxyCF'

canonical = {
             'channel': 'dilo', 
             'host': config.get_setting("current_host", 'dilo', default=''), 
             'host_alt': ["https://www.dilo.nu/"], 
             'host_black_list': ["https://streamtape.com/", "https://upstream.to/", "https://vidoza.net/", "http://vidoza.net/"], 
             'pattern': '<link\s*rel="stylesheet"\s*href="([^"]+)"', 
             'pattern_proxy': '{"item_id":\s*(\d+)}', 'proxy_url_test': 'breaking-bad/', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant_if_proxy': True, 
             'forced_proxy_ifnot_assistant': forced_proxy_opt, 'CF_stat': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def get_source(url, ignore_response_code=True):
    logger.info()
    
    data = httptools.downloadpage(url, timeout=10, ignore_response_code=ignore_response_code, canonical=canonical).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    
    return data


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos capitulos", action="latest_episodes", url=host,
                         page=0, thumbnail=get_thumb('new episodes', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Ultimas", action="list_all",  url=host + 'catalogue?sort=latest&page=1',
                         thumbnail=get_thumb('last', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Mas vistas", action="list_all", url=host + 'catalogue?sort=mosts-week&page=1',
                         thumbnail=get_thumb('more watched', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host + 'catalogue?&page=1',
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section",
                         url=host + 'catalogue', thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Por Años", action="section", url=host + 'catalogue',
                         thumbnail=get_thumb('year', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Por País", action="section", url=host + 'catalogue',
                         thumbnail=get_thumb('country', auto=True)))

    itemlist.append(Item(channel=item.channel, title = 'Buscar', action="search", url= host+'search?s=',
                         thumbnail=get_thumb('search', auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    itemlist = []
    
    data = get_source(item.url)
    
    patron = '<div\s*class="col-lg-2 col-md-3\s*col-6\s*mb-3">\s*<a\s*href="([^"]+)".*?'
    patron += '<img\s*src="([^"]+)".*?font-weight-500">([^<]+)<\/div>\s*'
    patron += '(?:<div\s*class="txt-gray-200[^"]*">(\d+)<)?(?:.*?>Serie<\/span>-->([^<]*)<)?'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, _scrapedtitle, scrapedyear, scrapedtype in matches:
        if str(scrapedtype).lower().strip() in ['libros', 'musica', 'audiolibros', 'juego pc', 'juegos pc', 'onlyfans'] \
                                            or not str(scrapedtype).strip(): continue

        url = urlparse.urljoin(host, scrapedurl)
        scrapedtitle = scrapertools.decode_utf8_error(_scrapedtitle)
        thumbnail = scrapedthumbnail
        contentType = 'movie' if 'pelicula' in scrapedtype.lower() else 'tvshow'
        year = scrapedyear if scrapedyear and contentType == 'movie' else '-' if contentType == 'movie' else ''
        
        new_item = Item(channel=item.channel, title=scrapedtitle, url=url,
                        thumbnail=thumbnail, contentType=contentType, infoLabels={'year': year})

        if new_item.contentType == 'movie':
            new_item.infoLabels['tagline'] = '[COLOR white]-Película-[/COLOR]'
            new_item.contentTitle = scrapedtitle
        else:
            new_item.infoLabels['tagline'] = '[COLOR coral]-Documental-[/COLOR]' if 'documental' in scrapedtype.lower() \
                                                                                 else '[COLOR coral]-Serie-[/COLOR]'
            new_item.contentSerieName = scrapedtitle
            new_item.context = filtertools.context(item, list_language, list_quality)
        new_item.action = 'seasons'
        
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    
    # Paginacion
    if itemlist:
        page_base = item.url
        next_page = scrapertools.find_single_match(data, '<a\s*href="[^"]+(&page=\d+)"\s*aria-label="Netx">')
        if next_page:
            if not '&page' in page_base:
                page_base += next_page
            else:
                page_base = re.sub(r'&page=\d+', next_page, page_base)
            itemlist.append(Item(channel=item.channel, action="list_all", title='Siguiente >>>',
                                 url=page_base, thumbnail=get_thumb("more.png"),
                                 type=item.type))
    return itemlist



def section(item):
    logger.info()

    itemlist = []
    
    data=get_source(item.url)

    patron = 'input"\s*id="([^"]+)".*?name="([^"]+)".*?'
    patron += '<label.*?>([^<]+)</label>'

    if item.title == 'Generos':
        data = scrapertools.find_single_match(data, '>\s*Todos\s*los\s*generos\s*</button>.*?<button\s*class')
    elif 'Años' in item.title:
        data = scrapertools.find_single_match(data, '>\s*Todos\s*los\s*años</button>.*?<button\s*class')

    elif 'País' in item.title:
        data = scrapertools.find_single_match(data, '>\s*Todos\s*los\s*países</button>.*?<button\s*class')

    matches = re.compile(patron, re.DOTALL).findall(data)

    for id, name, title in matches:
        id = id.replace('-','+')
        url = '%s?%s=%s' % (item.url, name, id)
        itemlist.append(Item(channel=item.channel, title=title, url=url, action='list_all'))

    return itemlist


def latest_episodes(item):
    logger.info()
    import datetime
    
    itemlist = []
    dia_hoy = datetime.date.today()
    year = str(dia_hoy.year)
    
    data = get_source(item.url)
    
    patron = '<a\s*class="media"\s*href="([^"]+)"\s*title="([^"]+)".*?src="([^"]+)".*?'
    patron += 'width:\s*97%">([^<]+)</div><div>(\d+x\d+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    logger.info("page=%s" % item.page)
    
    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedcontent, scrapedep in matches[item.page:item.page + 30]:
        if '-%s-' % year in scrapedurl or '/va-' in scrapedurl or '-pc-' in scrapedurl: continue

        title = '%s' % (scrapertools.decode_utf8_error(scrapedtitle.replace(' Online sub español', '')))
        contentSerieName = scrapertools.decode_utf8_error(scrapedcontent)
        season = episode = 1
        if scrapertools.find_single_match(title, '(\d+)[x|X](\d+)'):
            season, episode = scrapertools.find_single_match(title, '(\d+)[x|X](\d+)')
        
        itemlist.append(Item(channel=item.channel, action='findvideos', url=urlparse.urljoin(host, scrapedurl), thumbnail=scrapedthumbnail,
                             title=title, contentSerieName=contentSerieName, contentType='episode', 
                             contentSeason=season, contentEpisodeNumber=episode))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    
    for new_item in itemlist:
        if not new_item.infoLabels['tmdb_id'] and new_item.infoLabels['season'] == 1 and new_item.infoLabels['episode'] == 1:
            new_item.contentType = 'movie'
            new_item.contentTitle = new_item.title = new_item.contentSerieName
            new_item.infoLabels['year'] = '-'
            del new_item.infoLabels['season']
            del new_item.infoLabels['episode']
            del new_item.infoLabels['tvshowtitle']
            tmdb.set_infoLabels_item(new_item, seekTmdb=True)
        if new_item.contentType == 'movie':
            new_item.infoLabels['tagline'] = '[COLOR white]-Película-[/COLOR]'
        else:
            new_item.infoLabels['tagline'] = '[COLOR coral]-Documental-[/COLOR]' if 'documental' in new_item.url.lower() \
                                                                                 else '[COLOR coral]-Serie-[/COLOR]'

    if item.page + 30 < len(matches):
        itemlist.append(item.clone(page=item.page + 30,
                                   title="» Siguiente »", text_color="yellow"))
    else:
        next_page = scrapertools.find_single_match(data, '<link\s*rel="next" href="([^"]+)" />')
        if next_page:
            itemlist.append(item.clone(url=next_page, page=0, title="» Siguiente »", text_color="0xFF994D00"))


    return itemlist


def seasons(item):
    logger.info()

    itemlist=[]
    infoLabels = item.infoLabels

    data = get_source(item.url)
    
    serie_id = scrapertools.find_single_match(data, '{"item_id":\s*(\d+)}')
    post = {'item_id': serie_id}
    post = urllib.urlencode(post)
    seasons_url = '%sapi/web/seasons.php' % host
    headers = {'Referer':item.url}
    
    data = httptools.downloadpage(seasons_url, post=post, headers=headers, forced_proxy_opt=forced_proxy_opt, canonical=canonical).json

    for dict in data:
        try:
            season = int(dict['number'])
        except:
            season = 1

        if item.contentType == 'movie':
            item.action = 'episodesxseason'
            item.id = serie_id
            return episodesxseason(item)
        
        if season:
            infoLabels['season'] = season
            title = 'Temporada %s' % season
            
            itemlist.append(Item(channel=item.channel, url=item.url, title=title, action='episodesxseason',
                                 contentSeasonNumber=season, id=serie_id, infoLabels=infoLabels, contentType='season'))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
                Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                     action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName, contentType='tvshow'))

    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = []
    season = item.infoLabels['season'] or 1
    post = {'item_id': item.id, 'season_number': season}
    post = urllib.urlencode(post)

    seasons_url = '%sapi/web/episodes.php' % host
    headers = {'Referer': item.url}
    data = httptools.downloadpage(seasons_url, post=post, headers=headers, forced_proxy_opt=forced_proxy_opt, canonical=canonical).json
    infoLabels = item.infoLabels
    
    for dict in data:
        if dict.get('audio', '') == 'N/A' and not dict.get('picture', '') and not dict.get('description', ''): continue
        
        if item.contentType == 'movie':
            item.action = 'findvideos'
            item.url = '%s%s/' % (host, dict['permalink'])
            return findvideos(item)
        
        try:
            episode = int(dict['number'])
        except:
            episode = 1
        epi_name = dict['name']
        title = '%sx%s - %s' % (season, episode, epi_name)
        url = '%s%s/' % (host, dict['permalink'])
        if infoLabels.get('tagline', '') and '-Serie-' in infoLabels['tagline']: del infoLabels['tagline']
        
        itemlist.append(Item(channel=item.channel, title=title, action='findvideos', url=url,
                             contentEpisodeNumber=episode, id=item.id, infoLabels=infoLabels, 
                             contentType='episode'))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    return itemlist


def episodios(item):
    logger.info()
    
    itemlist = []
    
    templist = seasons(item)
    
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)
    
    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []
    
    data = get_source(item.url)
    
    patron = 'data-link="([^"]+)">.*?500">([^<]+)<.*?>Reproducir\s*en\s*([^<]+)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    for enc_url, server, language in matches:
        if not config.get_setting('unify'):
            title = ' [%s]' % language
        else:
            title = ''

        itemlist.append(Item(channel=item.channel, title='%s'+title, url=urlparse.urljoin(host, enc_url), action='play',
                              language=IDIOMAS[language], server=server, infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    return itemlist


def decode_link(enc_url):
    logger.info()
    
    url = ""
    
    try:
        #new_data = get_source(enc_url)
        new_data = httptools.downloadpage(enc_url).data
        if "gamovideo" in enc_url:
            url = scrapertools.find_single_match(new_data, '<a href="([^"]+)"')
        else:
            new_enc_url = scrapertools.find_single_match(new_data, '<iframe\s*class=[^>]+src="([^"]+)"')

            try:
                url = httptools.downloadpage(new_enc_url, follow_redirects=False).headers['location']
            except:
                if not 'jquery' in new_enc_url:
                    url = new_enc_url
    except:
        pass
    
    return url


def play(item):
    logger.info()
    
    itemlist = []
    
    if item.server not in ['openload', 'streamcherry', 'streamango']:
        item.server = ''
    item.url = decode_link(item.url)
    if not item.url:
        return []
    
    itemlist.append(item.clone())
    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    
    itemlist = []
    
    texto = texto.replace(" ", "+")
    item.url = host + 'search?s=' + texto
    
    if texto:
        try:
            return list_all(item)
        except:
            itemlist.append(item.clone(url='', title='No hay elementos...', action=''))
            return itemlist
