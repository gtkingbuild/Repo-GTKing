# -*- coding: utf-8 -*-
# -*- Channel HDFull -*-
# -*- Created for Alfa Addon -*-
# -*- By the Alfa Development Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

import re
import traceback
import base64
import ast
if not PY3: _dict = dict; from collections import OrderedDict as dict

from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryAllChannel

from platformcode.platformtools import dialog_notification, dialog_ok, itemlist_refresh, show_channel_settings

IDIOMAS = {'lat': 'LAT', 'spa': 'CAST', 'esp': 'CAST', 'sub': 'VOSE', 'espsub': 'VOSE', 'engsub': 'VOS', 'eng': 'VO'}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = ['HD1080', 'HD720', 'HDTV', 'DVDRIP', 'RHDTV', 'DVDSCR']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['clipwatching', 'gamovideo', 'vidoza', 'vidtodo', 'openload', 'uptobox']
forced_proxy_opt = ''
assistant = False

# https://dominioshdfull.com/

canonical = {
             'channel': 'hdfull', 
             'host': config.get_setting("current_host", 'hdfull', default=''), 
             'host_alt': ["https://hdfull.today/"], 
             'host_verification': '%slogin', 
             'host_black_list': ['https://hdfull.sbs/', 'https://hdfull.org/', 
                                 'https://hdfull.store/', 
                                 'https://hdfull.life/', 'https://hdfull.digital/', 'https://hdfull.work/', 
                                 'https://hdfull.video/', 'https://hdfull.cloud/', 'https://hdfull.wtf/', 
                                 'https://hdfull.fun/', 'https://hdfull.lol/', 'https://hdfull.one/', 
                                 'https://new.hdfull.one/', 'https://hdfull.top/', 'https://hdfull.bz/'],
             'pattern': '<meta\s*property="og:url"\s*content="([^"]+)"', 
             'set_tls': True, 'set_tls_min': False, 'retries_cloudflare': 1, 'expires': 365*24*60*60, 
             'forced_proxy_ifnot_assistant': forced_proxy_opt, 'CF_if_assistant': True if assistant else False, 
             'CF_stat': True if assistant else False, 'session_verify': True if assistant else False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host
host_thumb = 'https://hdfullcdn.cc/'
_silence = config.get_setting('silence_mode', channel=canonical['channel'])

timeout = 10
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "pelicula/"
tv_path = 'serie/'
language = []
url_replace = []
cnt_tot_items_usuario = 28
cnt_tot_episodios = 24
plot = 'Usa el [COLOR orange][B]Menú Contextual[/B][/COLOR] para acceder al las [COLOR limegreen][B]funciones de usuario[/B][/COLOR]'

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['container-flex', 'main-wrapper']}]), 
                       ('find_all', [{'tag': ['div'], 'class': ['span-6']}])]), 
         'categories': {},
         'search': {}, 
         'get_language': dict([('find', [{'tag': ['div'], 'class': ['left']}]), 
                               ('find_all', [{'tag': ['img']}])]),
         'get_language_rgx': '\/images\/(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/\d+$', '/%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['row-pages-wrapper']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2]}]), 
                            ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]),  
         'year': {}, 
         'season_episode': {}, 
         'seasons': dict([('find', [{'tag': ['ul'], 'id': ['season-list']}]), 
                          ('find_all', [{'tag': ['li']}])]), 
         'season_num': dict([('find', [{'tag': ['a']}]), 
                             ('get_text', [{'tag': '', '@STRIP': False}])]), 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'season_url': host, 
         'episode_url': '%sepisodio/%s-%sx%s', 
         'episodes': dict([('find', [{'tag': ['body']}]), 
                           ('get_text', [{'tag': '', '@STRIP': False, '@JSON': 'DEFAULT'}])]), 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['show-details']}]), 
                             ('find_all', [{'tag': ['a']}])]), 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 20, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'IDIOMAS_TMDB': {0: 'es', 1: 'ja', 2: 'es'}, 'jump_page': True}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


""" CACHING HDFULL PARAMETERS """
account = config.get_setting("logged", channel=canonical['channel'])
user_ = AlfaChannel.do_quote(config.get_setting('hdfulluser', channel=canonical['channel'], default=''))
pass_ = AlfaChannel.do_quote(config.get_setting('hdfullpassword', channel=canonical['channel'], default=''))
if not user_ or not pass_:
    from core import filetools
    setting = filetools.read(filetools.join(config.get_data_path(), 'settings_channels', 'hdfull_data.json'), silent=True)
    if setting:
        setting = base64.b64encode(setting.encode('utf-8')).decode('utf-8')
    else:
        setting = 'VACIO'
    logger.error('Type: User: %s; Password: %s; %s' % (str(type(config.get_setting('hdfulluser', 
                                                       channel=canonical['channel'], default=''))), 
                                                       str(type(config.get_setting('hdfullpassword', 
                                                       channel=canonical['channel'], default=''))), setting))
    account = False
    user_ = ''
    pass_ = ''
    config.set_setting('hdfulluser', user_, channel=canonical['channel'])
    config.set_setting('hdfullpassword', pass_, channel=canonical['channel'])
    config.set_setting('logged', account, channel=canonical['channel'])

credentials_req = True
js_url = AlfaChannel.urljoin(host, "templates/hdfull/js/jquery.hdfull.view.min.js")
data_js_url = AlfaChannel.urljoin(host, "js/providers.js")
patron_sid = "<input\s*type='hidden'\s*name='__csrf_magic'\s*value=\"([^\"]+)\"\s*\/>"

try:
    import xbmcgui
    window = None
    window = xbmcgui.Window(10000)
    user_status = jsontools.load(window.getProperty("AH_hdfull_user_status"), silence=True)
    if not user_status: raise Exception
    sid = window.getProperty("AH_hdfull_sid")
    js_data = window.getProperty("AH_hdfull_js_data")
    data_js = window.getProperty("AH_hdfull_data_js")
    just_logout = window.getProperty("AH_hdfull_just_logout")
except Exception:
    user_status = {}
    sid = ''
    js_data = ''
    data_js = ''
    just_logout = ''
    try:
        window.setProperty("AH_hdfull_user_status", jsontools.dump(user_status, silence=True))
        window.setProperty("AH_hdfull_sid", sid)
        window.setProperty("AH_hdfull_js_data", js_data)
        window.setProperty("AH_hdfull_data_js", data_js)
        window.setProperty("AH_hdfull_just_logout", str(just_logout))
    except Exception:
        logger.error(traceback.format_exc())


def mainlist(item):
    logger.info()
    global just_logout

    itemlist = []

    just_logout = window.getProperty("AH_hdfull_just_logout") or config.get_setting("just_logout", channel=canonical['channel'])
    verify_credentials(force_login=False if just_logout else True)
    if debug: logger.debug('just_logout: %s, account: %s, sid: %s, user_status: %s' % (just_logout, account, sid, user_status))
    if just_logout:
        just_logout = ''
        if window: window.setProperty("AH_hdfull_just_logout", str(just_logout))
        config.set_setting('just_logout', False, channel=canonical['channel'])

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, action="sub_menu_peliculas", title="Películas", url=host,
                         thumbnail=get_thumb("channels_movie.png"), c_type="peliculas", text_bold=True, plot=plot))
    if account:
        itemlist.append(Item(channel=item.channel, action="list_all", extra="items_usuario", 
                             title="    - [COLOR orange]Favoritos[/COLOR]",
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=movies&action=favorite&start=0&limit=%s", 
                             thumbnail=get_thumb("favorites.png"), c_type="peliculas", plot=plot))

    itemlist.append(Item(channel=item.channel, action="sub_menu_series", title="Series", url=host,
                         thumbnail=get_thumb("channels_tvshow.png"), c_type="series", text_bold=True, plot=plot))
    if account:
        itemlist.append(Item(channel=item.channel, action="list_all", extra="episodios",
                             title="    - [COLOR orange]Para Ver[/COLOR]",
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=shows&action=watch&start=0&limit=%s", 
                             thumbnail=get_thumb("videolibrary.png"), c_type="episodios", plot=plot))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         thumbnail=get_thumb("search.png"), plot=plot))

    if not account:
        itemlist.append(Item(channel=item.channel,  action="", url="", 
                        title="[COLOR gold]Regístrate en %s y luego habilita tu cuenta[/COLOR]" % host,
                        thumbnail=get_thumb("setting_0.png")))

        itemlist.append(Item(channel=item.channel,  action="configuracion", url="", text_bold=True,
                        title="[COLOR dodgerblue]Habilita tu cuenta para activar los items de usuario...[/COLOR]",
                        thumbnail=get_thumb("setting_0.png")))

    else:
        itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                             folder=False, thumbnail=get_thumb("next.png")))

        itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                             thumbnail=get_thumb("setting_0.png")))

        itemlist.append(Item(channel=item.channel, action="logout", url="", folder=False, refresh=True, 
                             title="[COLOR steelblue][B]Desloguearse[/B][/COLOR]",
                             plot="Para cambiar de usuario", thumbnail=get_thumb("back.png")))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def configuracion(item):

    ret = show_channel_settings()
    if account: itemlist_refresh()

    return item


def sub_menu_peliculas(item):
    logger.info()

    itemlist = []

    itemlist.append(Item(channel=item.channel, action="list_all", extra="fichas", title="Todas las Películas",
                         url=AlfaChannel.urljoin(host, "peliculas/date/1"), text_bold=True, plot=item.plot, 
                         thumbnail=get_thumb('movies', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, action="list_all", extra="fichas", title=" - [COLOR paleturquoise]Películas Estreno[/COLOR]",
                         url=AlfaChannel.urljoin(host, "peliculas-estreno"), plot=item.plot, 
                         thumbnail=get_thumb('premieres', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, action="list_all", extra="fichas", title=" - [COLOR paleturquoise]Películas Actualizadas[/COLOR]",
                         url=AlfaChannel.urljoin(host, "peliculas-actualizadas"), plot=item.plot, 
                         thumbnail=get_thumb('updated', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, action="section", extra="Género", title=" - [COLOR paleturquoise]Películas por Género[/COLOR]",
                         url=host, plot=item.plot, 
                         thumbnail=get_thumb('genres', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, action="list_all", extra="fichas", title="Todas las Películas (Rating IMDB)",
                         url=AlfaChannel.urljoin(host, "peliculas/imdb_rating/1"), text_bold=True, plot=item.plot, 
                         thumbnail=get_thumb('recomended', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, action="list_all", extra="fichas", title="Todas las Películas (ABC)",
                         url=AlfaChannel.urljoin(host, "peliculas/abc/1"), text_bold=True, plot=item.plot, 
                         thumbnail=get_thumb('alphabet', auto=True), c_type=item.c_type))

    if account:
        itemlist.append(Item(channel=item.channel, action="list_all", extra="items_usuario",
                             title="[COLOR orange]Favoritos[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=movies&action=favorite&start=0&limit=%s", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="items_usuario",
                             title="[COLOR orange]Vistas[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=movies&action=seen&start=0&limit=%s", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="items_usuario",
                             title="[COLOR dodgerblue]Pendientes[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=movies&action=pending&start=0&limit=%s", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="items_usuario",
                             title="[COLOR dodgerblue]Recomendadas[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=movies&action=recommended&start=0&limit=%s", 
                             thumbnail=item.thumbnail, c_type=item.c_type))
        
        itemlist.append(Item(channel=item.channel, action="list_all", extra="listas",
                             title="[COLOR blue]Listas: Mis Listas[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=lists&action=mine&start=0&limit=%s&search=", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="listas",
                             title=" - [COLOR paleturquoise]Listas: Siguiendo[/COLOR]", plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=lists&action=following&start=0&limit=%s&search=", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="listas",
                             title=" - [COLOR paleturquoise]Listas: Populares[/COLOR]", plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=lists&action=top&start=0&limit=%s&search=", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="search",extra="listas", 
                             title="- Buscar Listas...", plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=lists&action=search&start=0&limit=%s&search=", 
                             thumbnail=get_thumb("search.png")))

    return itemlist


def sub_menu_series(item):
    logger.info()

    itemlist = []
    last_page = 241
    page_factor = 2.0

    itemlist.append(Item(channel=item.channel, action="list_all", extra="episodios", 
                         title="Episodios: Últimos Emitidos", plot=item.plot, 
                         url=AlfaChannel.urljoin(host, "a/episodes"), post="action=latest&start=0&limit=%s&elang=ALL", 
                         thumbnail=get_thumb('new episodes', auto=True), c_type='episodios', text_bold=True))

    itemlist.append(Item(channel=item.channel, action="list_all", extra="episodios", 
                         title=" - [COLOR paleturquoise]Episodios Estreno[/COLOR]", plot=item.plot, 
                         url=AlfaChannel.urljoin(host, "a/episodes"), post="action=premiere&start=0&limit=%s&elang=ALL", 
                         thumbnail=get_thumb('newest', auto=True), c_type='episodios'))

    itemlist.append(Item(channel=item.channel, action="list_all", extra="episodios", 
                         title=" - [COLOR paleturquoise]Episodios Actualizados[/COLOR]", plot=item.plot, 
                         url=AlfaChannel.urljoin(host, "a/episodes"), post="action=updated&start=0&limit=%s&elang=ALL", 
                         thumbnail=get_thumb('updated', auto=True), c_type='episodios'))

    itemlist.append(Item(channel=item.channel, action="list_all", extra="episodios", 
                         title=" - [COLOR paleturquoise]Episodios Anime[/COLOR]", plot=item.plot, 
                         url=AlfaChannel.urljoin(host, "a/episodes"), post="action=anime&start=0&limit=%s&elang=ALL", 
                         thumbnail=get_thumb('anime', auto=True), c_type='episodios'))

    itemlist.append(Item(channel=item.channel, action="list_all", extra="fichas", title="Todas las Series",
                         url=AlfaChannel.urljoin(host, "series/date/1"), text_bold=True, plot=item.plot, 
                         thumbnail=get_thumb('tvshows', auto=True), c_type=item.c_type, 
                         last_page=last_page, page_factor=page_factor))
    
    itemlist.append(Item(channel=item.channel, action="section", extra="Género", 
                         title=" - [COLOR paleturquoise]Series por Género[/COLOR]",
                         url=host, plot=item.plot, 
                         thumbnail=get_thumb('genres', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, action="section", extra="Alfabético", 
                         title=" - [COLOR paleturquoise]Series A-Z[/COLOR]", plot=item.plot, 
                         url=AlfaChannel.urljoin(host, "series/abc/"), 
                         thumbnail=get_thumb('alphabet', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, action="list_all", extra="fichas", title="Todas las Series (Rating IMDB)", 
                         url=AlfaChannel.urljoin(host, "series/imdb_rating/1"), text_bold=True, plot=item.plot, 
                         thumbnail=get_thumb('recomended', auto=True), c_type=item.c_type, 
                         last_page=last_page, page_factor=page_factor))

    if account:
        itemlist.append(Item(channel=item.channel, action="list_all", extra="items_usuario",
                             title="[COLOR orange]Siguiendo[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=shows&action=following&start=0&limit=%s", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="episodios",
                             title="[COLOR orange]Para Ver[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=shows&action=watch&start=0&limit=%s", 
                             thumbnail=item.thumbnail, c_type='episodios'))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="items_usuario",
                             title="[COLOR dodgerblue]Favoritas[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=shows&action=favorite&start=0&limit=%s", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="items_usuario",
                             title="[COLOR dodgerblue]Pendientes[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=shows&action=pending&start=0&limit=%s", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="items_usuario",
                             title="[COLOR dodgerblue]Recomendadas[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=shows&action=recommended&start=0&limit=%s", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="items_usuario",
                             title="[COLOR dodgerblue]Finalizadas[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=shows&action=seen&start=0&limit=%s", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="listas",
                             title="[COLOR blue]Listas: Mis Listas[/COLOR]", text_bold=True, plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=lists&action=mine&start=0&limit=%s&search=", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="listas",
                             title=" - [COLOR paleturquoise]Listas: Siguiendo[/COLOR]", plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=lists&action=following&start=0&limit=%s&search=", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="list_all", extra="listas",
                             title=" - [COLOR paleturquoise]Listas: Populares[/COLOR]", plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=lists&action=top&start=0&limit=%s&search=", 
                             thumbnail=item.thumbnail, c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, action="search",extra="listas",
                             title="- Buscar Listas...", plot=item.plot, 
                             url=AlfaChannel.urljoin(host, "a/my"), post="target=lists&action=search&start=0&limit=%s&search=", 
                             thumbnail=get_thumb("search.png")))

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    if item.extra in ['Género']:
        findS['categories'] = dict([('find_all', [{'tag': ['li'], 'class': ['dropdown'], '@POS': [2 if item.c_type == 'series' else 3]}, 
                                                  {'tag': ['a']}])])
        findS['url_replace'] = [['($)', '/date/1']]

    elif item.extra in ['Alfabético']:
        itemlist = []

        for letra in ['#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            
            itemlist.append(item.clone(action="list_all", title=letra, url=item.url + letra.replace('#', '9')))

        return itemlist

    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()

    findS = finds.copy()

    verify_credentials(force_login=False)

    if item.extra in ["items_usuario", "listas", "episodios"]:
        findS['find'] = dict([('find', [{'tag': ['body']}]), 
                              ('get_text', [{'tag': '', '@STRIP': False, '@JSON': 'DEFAULT'}])])
        findS['controls'].update({'cnt_tot': cnt_tot_episodios if item.c_type == 'episodios' else cnt_tot_items_usuario, 
                                  'custom_pagination': True, 'jump_page': False})

        item.curr_page = int(item.curr_page) if item.curr_page else 1
        if str(cnt_tot_episodios) not in item.post and str(cnt_tot_items_usuario) not in item.post: 
            item.post = item.post % findS['controls']['cnt_tot']
        item.post = re.sub('&start=\d+', '&start=%s' % ((item.curr_page - 1) * findS['controls']['cnt_tot']), item.post)

    elif item.extra in ['Alfabético']:
        findS['controls'].update({'custom_pagination': True, 'jump_page': True})

    return AlfaChannel.list_all(item, matches_post=list_all_matches, finds=findS, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    status = check_user_status()                                                # Carga estados

    # Listas de usuario, populares o siguiendo: listar nombres de listas
    if item.extra in ["listas"]:
        findS['controls']['modo_grafico'] = False
        item.unify = False

        for elem in matches_int:
            elem_json = {}
            #logger.error(elem)

            try:
                if not isinstance(elem, _dict): continue
                elem_json['mediatype'] = 'tvshow' if item.c_type == 'series' else 'movie'
                if elem_json['mediatype'] == 'tvshow' and not elem.get('shows', ''): continue
                if elem_json['mediatype'] == 'movie' and not elem.get('movies', ''): continue
                elem_json['title'] = elem.get('title', '')
                elem_json['url'] = AlfaChannel.urljoin(host, 'lista/' + (elem.get('permalink', '') or elem.get('perma', '')))
                elem_json['list_info'] = {elem.get('id', '1'): elem.get('id', '1')}
                elem_json['action'] = 'list_all'
                elem_json['extra'] = 'listas_res'

                str_ = get_status(status, elem_json)
                if str_: elem_json['plot_extend'] = str_.replace('[COLOR blue](Visto)[/COLOR]', '')
                elem_json = add_context(elem_json, str_)

                matches.append(elem_json.copy())

            except Exception:
                logger.error(elem)
                logger.error(traceback.format_exc())

        if matches and len(matches_int) >= AlfaChannel.cnt_tot:
            if  len(matches_int) != len(matches):
                AlfaChannel.cnt_tot = len(matches)
                AlfaChannel.last_page = 9999
        else:
            AlfaChannel.last_page = 0

        return matches

    # Pelícuas, series y episodios
    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if item.extra in ['items_usuario']:                                 # funciones con login
                if not isinstance(elem, _dict): continue

                if elem.get('title') and not isinstance(elem['title'], _dict): 
                    elem['title'] = ast.literal_eval(elem['title'])
                elem_json['title'] = elem.get('title', {}).get('es', '').strip() or elem.get('title', {}).get('en', '').strip()
                if not elem_json['title']:
                    elem_json['title'] = elem.get('show_title', {}).get('es', '').strip() or elem.get('show_title', {}).get('en', '').strip()
                if not PY3: elem_json['title'] = elem_json['title'].encode('utf-8')

                elem_json['thumbnail'] = AlfaChannel.urljoin(host, "thumbs/" + (elem.get('thumbnail', '') or elem.get('thumb', '')))
                #elem_json['thumbnail'] += '|User-Agent=%s' % AlfaChannel.httptools.get_user_agent()

                elem_json['mediatype'] = 'tvshow' if item.c_type == 'series' \
                                                  else 'episode' if (item.c_type == 'episodios' or 'show_title' in elem) else 'movie'
                path = tv_path if elem_json['mediatype'] in ['tvshow', 'episode'] else movie_path if elem_json['mediatype'] == 'movie' else tv_path

                if not elem.get('permalink', '') and not elem.get('perma', ''): continue
                elem_json['url'] = AlfaChannel.urljoin(host, '%s/' % path + (elem.get('permalink', '') or elem.get('perma', '')))
                if elem_json['mediatype'] == 'episode':
                    elem_json['url'] += '/temporada-%s/episodio-%s' % (elem.get('season', '1'), elem.get('episode', '00').zfill(2))
                elem_json['info'] = {elem.get('id', '0'): elem.get('id', '0')}

            elif item.extra in ['episodios']:
                if not isinstance(elem, _dict): continue

                elem_json['season'] = elem.get('season', 1)
                elem_json['episode'] = elem.get('episode', 0)

                if elem.get('show', {}) and not isinstance(elem['show'], _dict): 
                    elem['show'] = ast.literal_eval(elem['show'])
                elem_json['title'] = elem.get('show', {}).get('title', {}).get('es', '').strip() \
                                     or elem.get('show', {}).get('title', {}).get('en', '').strip()
                if not elem_json['title']:
                    if elem.get('show_title') and not isinstance(elem['show_title'], _dict): 
                        elem['show_title'] = ast.literal_eval(elem['show_title'])
                    elem_json['title'] = elem.get('show_title', {}).get('es', '').strip() or elem.get('show_title', {}).get('en', '').strip()
                if not PY3: elem_json['title'] = elem_json['title'].encode('utf-8')
                if elem.get('title') and not isinstance(elem['title'], _dict): 
                    elem['title'] = ast.literal_eval(elem['title'])
                elem_json['title_episode'] = elem.get('title', {}).get('es', '').strip() or elem.get('title', {}).get('en', '').strip()
                if not PY3: elem_json['title_episode'] = elem_json['title_episode'].encode('utf-8')

                elem_json['thumbnail'] = AlfaChannel.urljoin(host, "thumbs/" + (elem.get('thumbnail', '') or elem.get('thumb', '')))
                #elem_json['thumbnail'] += '|User-Agent=%s' % AlfaChannel.httptools.get_user_agent()

                elem_json['mediatype'] = 'episode'
                path = tv_path

                elem_json['language'] = '*%s' % elem.get('languages', '')

                if not elem.get('permalink', '') and not elem.get('perma', ''): continue
                elem_json['url'] = AlfaChannel.urljoin(host, '%s/' % path + (elem.get('permalink', '') or elem.get('perma', '')))
                elem_json['url'] += '/temporada-%s/episodio-%s' % (elem.get('season', '1'), elem.get('episode', '00').zfill(2))
                elem_json['info'] = {elem.get('id', '0'): elem.get('show', {}).get('id', '0')}

            elif not item.extra or item.extra in ['fichas', 'Género', 'Alfabético', 'listas_res'] or item.c_type == 'search':
                if item.extra in ['Alfabético'] and AlfaChannel.last_page in [9999, 99999]:
                    AlfaChannel.last_page = int((float(len(matches_int)) / float(AlfaChannel.cnt_tot))  + 0.999999)
                    item.url = ''
                    item.matches_org = True

                elem_json['title'] = elem.find('h5', class_="left").find('a').get("title", '') if elem.find('h5', class_="left") \
                                     else elem.find('a').find('img').get("alt", '')

                elem_json['url'] = elem.find('h5', class_="left").find('a').get('href', '')
                elem_json['thumbnail'] = AlfaChannel.urljoin(host_thumb, elem.find('a').find('img').get('data-src', '') \
                                                                         or elem.find('a').find('img').get('src', ''))
                elem_json['language'] = '*%s' % elem.find('a').get('data-langs', '')
                if not elem.find('a').get('data-langs', ''): AlfaChannel.get_language_and_set_filter(elem, elem_json)
                if elem.find("div", class_="seen-box"): 
                    elem_json['info'] = elem.find("div", class_="seen-box").get('data-seen', '')
                else:
                    elem_json['info'] = elem.find("span", class_="rating-pod-actions").find("a", class_="logged-req").get('onclick', '')
                    elem_json['info'] = scrapertools.find_single_match(elem_json['info'], '\d+,\s*(\d+),\s*\d+')
                elem_json['info'] = {elem_json['info']: elem_json['info']}
                if not elem_json.get('mediatype'):
                    elem_json['mediatype'] = 'tvshow' if (tv_path in elem_json['url'] or "/tags-tv" in elem_json['url']) else 'movie'
                if elem.find('div', class_="right") and elem.find('div', class_="right").get_text('.', strip=True):
                    elem_json['title_subs'] = ['[COLOR darkgrey][%s][/COLOR]' % elem.find('div', class_="right").get_text('.', strip=True)]
                if item.c_type != 'search' and item.extra not in ['listas_res']:
                    if item.contentType and item.contentType != 'list' and item.contentType != elem_json['mediatype']: continue
                    if item.c_type and item.c_type == 'peliculas' and elem_json['mediatype'] != 'movie': continue
                    if item.c_type and item.c_type == 'series' and elem_json['mediatype'] != 'tvshow': continue

            elem_json['quality'] = ''

            # items usuario en titulo (visto, pendiente, etc)
            if elem.get('list_info', {}): elem_json['list_info'] = elem['list_info']
            elem_json['plot_extend'] = elem.get('plot_extend', elem.get('plot_extend', ''))
            str_ = get_status(status, elem_json)
            if str_:
                elem_json['plot_extend'] += str_.replace('[COLOR blue](Visto)[/COLOR]', '')
                elem_json['playcount'] = 1 if 'Visto' in str_ else 0
            if item.extra not in ['listas_res']: elem_json = add_context(elem_json, str_)

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url'): continue

        matches.append(elem_json.copy())

    if item.extra in ['episodios']: 
        if matches and len(matches_int) >= AlfaChannel.cnt_tot:
            if  len(matches_int) != len(matches):
                AlfaChannel.cnt_tot = len(matches)
                AlfaChannel.last_page = 9999
        else:
            AlfaChannel.last_page = 0

    return matches


def seasons(item):
    logger.info()
    
    if "###" in item.url:
        item.info = {item.url.split("###")[1].split(";")[0]: item.url.split("###")[1].split(";")[0]}
        item.url = item.url.split("###")[0]

    return AlfaChannel.seasons(item, matches_post=seasons_matches, **kwargs)


def seasons_matches(item, matches_int, **AHkwargs):
    logger.info()
    
    matches = []
    findS = AHkwargs.get('finds', finds)
    soup = AHkwargs.get('soup', {})
    status = check_user_status()                                                # Carga estados

    sid = scrapertools.find_single_match(str(soup), "<\s*script\s*>\s*var\s*sid\s*=\s*'\s*(\d+)\s*'")
    if sid: 
        if not isinstance(item.info, _dict):
            item.info = {sid: sid}
        else:
            item.info = {list(item.info.keys())[0]: sid}

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['info'] = item.info
            elem_json['title'] = elem.find('a').get_text(strip=True)
            elem_json['season'] = int(elem_json['title'])

        except Exception:
            elem_json['season'] = 0
            if 'todas' in elem_json['title'].lower():
                continue

        if not elem_json.get('url', ''): 
            continue

        elem_json['title'] = item.contentSerieName
        str_ = get_status(status, elem_json, mediatype='tvshow')
        elem_json['plot_extend'] = str_.replace('[COLOR blue](Visto)[/COLOR]', '')
        elem_json = add_context(elem_json, str_, mediatype='tvshow')

        matches.append(elem_json.copy())

    if matches: matches = sorted(matches, key=lambda elem_json: int(elem_json['season']))
    matches = find_hidden_seasons(item, matches, item.info)

    return matches


def episodios(item):
    logger.info()

    itemlist = []
    verify_credentials(force_login=True, force_check=False)

    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item, **AHkwargs):
    logger.info()

    kwargs['matches_post_get_video_options'] = findvideos_matches
    item.url = AlfaChannel.urljoin(host, "a/episodes")
    item.post = 'action=season&start=0&limit=0&show=%s&season=%s' % (list(item.info.values())[0], item.contentSeason)

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()
    
    matches = []
    findS = AHkwargs.get('finds', finds)
    soup = AHkwargs.get('soup', {})

    status = check_user_status()                                                # Carga estados
    sid = scrapertools.find_single_match(str(soup), "<\s*script\s*>\s*var\s*sid\s*=\s*'\s*(\d+)\s*'")
    if not isinstance(item.info, _dict):
        logger.error('item.info ERRONEO: %s' % str(item.info))
        item.info = {sid: sid}
    else:
        sid = list(item.info.values())[0]

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        if not isinstance(elem, _dict): continue

        try:
            elem_json['season'] = elem.get('season', 0)
            elem_json['episode'] = elem.get('episode', 0)

            if elem.get('show', {}) and not isinstance(elem['show'], _dict): 
                elem['show'] = ast.literal_eval(elem['show'])
            elem_json['title'] = elem.get('show', {}).get('title', {}).get('es', '').strip() \
                                 or elem.get('show', {}).get('title', {}).get('en', '').strip()
            if not elem_json['title']:
                if elem.get('show_title') and not isinstance(elem['show_title'], _dict): 
                    elem['show_title'] = ast.literal_eval(elem['show_title'])
                elem_json['title'] = elem.get('show_title', {}).get('es', '').strip() or elem.get('show_title', {}).get('en', '').strip()
            if not PY3: elem_json['title'] = elem_json['title'].encode('utf-8')
            if elem.get('title') and not isinstance(elem['title'], _dict): 
                elem['title'] = ast.literal_eval(elem['title'])
            elem_json['title_episode'] = elem.get('title', {}).get('es', '').strip() or elem.get('title', {}).get('en', '').strip()
            if not PY3: elem_json['title_episode'] = elem_json['title_episode'].encode('utf-8')

            elem_json['thumbnail'] = AlfaChannel.urljoin(host, "thumbs/" + (elem.get('thumbnail', '') or elem.get('thumb', '')))
            #elem_json['thumbnail'] += '|User-Agent=%s' % AlfaChannel.httptools.get_user_agent()

            elem_json['mediatype'] = 'episode'
            path = tv_path

            elem_json['language'] = '*%s' % elem.get('languages', '')

            if not elem.get('permalink', '') and not elem.get('perma', ''): continue
            elem_json['url'] = AlfaChannel.urljoin(host, '%s/' % path + (elem.get('permalink', '') or elem.get('perma', '')))
            elem_json['url'] += '/temporada-%s/episodio-%s' % (elem.get('season', '1'), elem.get('episode', '00').zfill(2))
            elem_json['info'] = {elem.get('id', '0'): sid}

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url', ''): 
            continue
        
        str_ = get_status(status, elem_json)
        elem_json['plot_extend'] = str_.replace('[COLOR blue](Visto)[/COLOR]', '')
        elem_json['plot_extend_show'] = False
        elem_json['playcount'] = 1 if 'Visto' in str_ else 0
        elem_json = add_context(elem_json, str_)

        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()
    global js_data, data_js

    verify_credentials(force_login=True if item.contentChannel == 'videolibrary' else False)

    kwargs['matches_post_episodes'] = episodesxseason_matches

    if "###" in item.url:
        item.info = {item.url.split("###")[1].split(";")[0]: item.url.split("###")[1].split(";")[0] if item.contentType == 'movie' else item.sid}
        if item.sid: del item.sid
        item.url = item.url.split("###")[0]
    if not isinstance(item.info, _dict):
        logger.error('item.info ERRONEO: %s' % str(item.info))
        item.info = {item.sid: item.sid}

    if not js_data or not data_js:
        window.setProperty("AH_hdfull_js_data", '')
        window.setProperty("AH_hdfull_data_js", '')
        
        js_data = agrupa_datos(js_url, hide_infobox=True)
        if js_data:
            if window: window.setProperty("AH_hdfull_js_data", str(js_data))
            logger.info('Js_data DESCARGADO', force=True)
        else:
            logger.error('Js_data ERROR en DESCARGA')
            return matches
        
        data_js = agrupa_datos(data_js_url, hide_infobox=True)
        if data_js:
            if window: window.setProperty("AH_hdfull_data_js", str(data_js))
            logger.info('Data_js DESCARGADO', force=True)
        else:
            logger.error('Data_js ERROR en DESCARGA')
            return matches

    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=findvideos_matches, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()
    if PY3:
        from lib import alfaresolver_py3 as alfaresolver
    else:
        from lib import alfaresolver

    matches = []
    findS = AHkwargs.get('finds', finds)
    soup = AHkwargs.get('soup', {})

    if item.contentType == 'movie':
        sid = scrapertools.find_single_match(str(soup), "<\s*script[^>]*>[^ª]+\s*var\s*mid\s*=\s*'\s*(\d+)\s*'")
        if sid: item.info = {sid: sid}
    
    try:
        year = int(soup.find('div', class_="show-details").find('p').find('a').get_text(strip=True))
        if year and year != item.infoLabels.get('year', 0):
            AlfaChannel.verify_infoLabels_keys(item, {'year': year})
    except Exception:
        pass

    provs = alfaresolver.jhexdecode(data_js)
    matches_int = jsontools.load(alfaresolver.obfs(AlfaChannel.response.data, js_data))

    ## Carga estados: items usuario en titulo (visto, pendiente, etc).  Reset si viene de Videoteca
    status = check_user_status()
    str_ = get_status(status, item)
    if str_:
        item.plot_extend = str_.replace('[COLOR blue](Visto)[/COLOR]', '')

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if elem.get('provider', 'None') in provs:
                embed = provs[elem['provider']].get('t', '')
                elem_json['play_type'] = "Ver" if embed == 's' else "Descargar"
                elem_json['url'] = provs[elem['provider']].get('d', '') % elem.get('code', '')
                elem_json['language'] = IDIOMAS.get(elem.get('lang', '').lower(), elem.get('lang', ''))
                elem_json['quality'] = '%s%s' % ('*' if item.contentType != 'movie' else '', elem.get('quality', '').upper() if PY3 else \
                                                 unicode(elem.get('quality', ''), "utf8").upper().encode("utf8"))
                if item.contentType == 'episode': elem_json['quality'] = elem_json['quality'].replace('HD', '').rstrip('P') + 'p'
                elem_json['title'] = '%s'
                elem_json['title_episode'] = item.contentTitle if item.contentType == 'episode' else ''
                elem_json['title_show'] = item.contentSerieName or item.contentTitle
                elem_json['server'] = ''
                elem_json['server'] = ''
                elem_json['info'] = item.info
                elem_json['mediatype'] = item.contentType
                elem_json['playcount'] = 1 if 'Visto' in str_ else 0
                if 'set_status__' not in str(item.context):
                    elem_json = add_context(elem_json, str_)

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url'): continue
        if 'clicknupload' in elem_json['url']: continue

        matches.append(elem_json.copy())
    
    return matches, langs


def play(item):
    
    if "###" in item.url:
        item.info = {item.url.split("###")[1].split(";")[0]: item.url.split("###")[1].split(";")[0]}
        item.url = item.url.split("###")[0]
    mediatype = '1' if item.contentType == 'tvshow' else '2' if item.contentType == 'movie' else '3' if item.contentType == 'episode' else '4'
    if item.info:
        post = "target_id=%s&target_type=%s&target_status=1" % (list(item.info.keys())[0], mediatype)
        
        data = agrupa_datos(AlfaChannel.urljoin(host, "a/status"), post=post, hide_infobox=True)
        check_user_status(reset=True)
    
    devuelve = servertools.findvideosbyserver(item.url, item.server)
    
    if devuelve:
        item.url = devuelve[0][1]
    else:
        devuelve = servertools.findvideos(item.url, True)
        if devuelve:
            item.url = devuelve[0][1]
            item.server = devuelve[0][2]
    item.thumbnail = item.contentThumbnail
    
    return [item]


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def get_page_num(item):
    logger.info()
    # Llamamos al método que salta al nº de página seleccionado

    return AlfaChannel.get_page_num(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    verify_credentials(force_login=True)

    try:
        texto = texto.replace(" ", "+")

        if not item.post:
            item.url = item.url + "buscar"
            item.post = '__csrf_magic=%s&menu=search&query=%s' % (sid, texto)
        else:
            item.post = item.post + texto

        if texto:
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except Exception:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


""" CREDENTIALS MANAGEMENT """
def verify_credentials(force_login=True, force_check=True):
    global account, credentials_req, user_, pass_, sid, user_status
    
    if debug: logger.debug('SID: %s; Account: %s; just_logout: %s; force_login: %s; force_check: %s; credentials: %s; credentials_req: %s' \
                            % (True if sid else False, account, just_logout, force_login, force_check, 
                               True if user_ and pass_ else False, credentials_req))

    credentials = True if user_ and pass_ else False
    if not credentials:
        account = False
        config.set_setting("logged", account, channel=canonical['channel'])
        sid = ''
        if window: window.setProperty("AH_hdfull_sid", sid)
        user_status = {}
        if window: window.setProperty("AH_hdfull_user_status", jsontools.dump(user_status))
        logger.info('NO LOGIN credentials', force=True)
        
        if credentials_req and force_check:
            from platformcode import help_window
            help_window.show_info('hdfull_login', wait=True)
            configuracion(Item)

            try:
                user_ = AlfaChannel.do_quote(config.get_setting('hdfulluser', channel=canonical['channel'], default=''))
                pass_ = AlfaChannel.do_quote(config.get_setting('hdfullpassword', channel=canonical['channel'], default=''))
            except Exception as e:
                from core import filetools
                setting = filetools.read(filetools.join(config.get_data_path(), 'settings_channels', 'hdfull_data.json'), silent=True)
                if setting:
                    setting = base64.b64encode(setting.encode('utf-8')).decode('utf-8')
                else:
                    setting = 'VACIO'
                logger.error('ERROR: %s; Type: User: %s; Password: %s; %s' % (str(e), str(type(config.get_setting('hdfulluser', 
                                                                              channel=canonical['channel'], default=''))), 
                                                                              str(type(config.get_setting('hdfullpassword', 
                                                                              channel=canonical['channel'], default=''))), setting))
                user_ = ''
                pass_ = ''
                account = False
                config.set_setting('hdfulluser', user_, channel=canonical['channel'])
                config.set_setting('hdfullpassword', pass_, channel=canonical['channel'])
                config.set_setting('logged', account, channel=canonical['channel'])

            credentials = True if user_ and pass_ else False
            if credentials and force_login: login()
            
            if not credentials:
                if not _silence:
                    dialog_notification("Falta usuario o contraseña", "Revise sus datos en la configuración del canal", sound=False)
                credentials_req = False
                logger.info('NO credentials for LOGIN', force=True)

    elif credentials and force_login: login()

    return credentials

def check_user_status(reset=False, hide_infobox=True):
    global user_status

    if reset:
        user_status = {}
        if window: window.setProperty("AH_hdfull_user_status", jsontools.dump(user_status))
        logger.info('User_Status RESETEADO', force=True)
    if not user_status and account:
        if window: window.setProperty("AH_hdfull_user_status", jsontools.dump({}))

        user_status = agrupa_datos(AlfaChannel.urljoin(host, 'a/status/all'), json=True, hide_infobox=hide_infobox, 
                                   force_check=False, force_login=False)
        if user_status:
            if window: window.setProperty("AH_hdfull_user_status", jsontools.dump(user_status))
            logger.info('User_Status DESCARGADO', force=True)
        else:
            logger.error('User_Status ERROR en DESCARGA')
    
    return user_status

def check_login_status(data):
    global account, sid
    
    if not isinstance(data, str):
        return account
    if not data:
        return False
    
    _logged = 'id="header-signout" href="/logout"'
    
    if _logged in data:
        account = True
        if scrapertools.find_single_match(data, patron_sid):
            sid = AlfaChannel.do_quote(scrapertools.find_single_match(data, patron_sid), plus=False)
            if window: window.setProperty("AH_hdfull_sid", sid)
        if not config.get_setting("logged", channel=canonical['channel']):
            config.set_setting("logged", account, channel=canonical['channel'])
        return account
    
    account = False
    config.set_setting("logged", account, channel=canonical['channel'])
    sid = ''
    if window: window.setProperty("AH_hdfull_sid", sid)
    
    return account

def login(data='', alfa_s=False, force_check=True, retry=False):
    global sid, account

    if data:
        sid = AlfaChannel.do_quote(scrapertools.find_single_match(data, patron_sid), plus=False)
        if window: window.setProperty("AH_hdfull_sid", sid)

    logger.info('Data: %s; SID: %s; Account: %s; Check: %s; Retry: %s' \
                % (True if data else False, True if sid else False, account, force_check, retry), force=True)

    if not data or not sid or not account:
        data = agrupa_datos(AlfaChannel.urljoin(host, 'login'), referer=False, force_check=False, 
                            force_login=False, hide_infobox=True if not retry else None)
        sid = AlfaChannel.do_quote(scrapertools.find_single_match(data, patron_sid), plus=False)
        if window: window.setProperty("AH_hdfull_sid", sid)

    if check_login_status(data):
        check_user_status()
        logger.info('LOGGED IN', force=True)
        return True

    elif not verify_credentials(force_login=False, force_check=force_check):
        return False

    else:
        host_alt = host
        sid = AlfaChannel.do_quote(scrapertools.find_single_match(data, patron_sid), plus=False)
        if window: window.setProperty("AH_hdfull_sid", sid)
        if not sid:
            if not retry:
                logout(Item())
                logger.error('NO SID: RETRY: %s' % str(data))
                return login(force_check=force_check, retry=True)
            logger.error('NO SID: %s' % str(data))
            return False

        post = '__csrf_magic=%s&username=%s&password=%s&action=login' % (sid, user_, pass_)
        new_data = agrupa_datos(AlfaChannel.urljoin(host, 'a/login'), post=post, referer=AlfaChannel.urljoin(host, 'login'), 
                                json=True, force_check=False, force_login=False, hide_infobox=True if not retry else None)

        if host not in host_alt:
            logger.info('Cambio de HOST: de %s a %s', (host, host_alt))
            return login(alfa_s=alfa_s, force_check=force_check)

        if isinstance(new_data, _dict) and new_data.get("status", "") == "OK":
            sid = ''
            if window: window.setProperty("AH_hdfull_sid", sid)
            new_data = agrupa_datos(AlfaChannel.urljoin(host, 'login'), referer=False, force_check=False, 
                                    force_login=False, hide_infobox=True)
            if scrapertools.find_single_match(new_data, patron_sid):
                sid = AlfaChannel.do_quote(scrapertools.find_single_match(new_data, patron_sid), plus=False)
                if window: window.setProperty("AH_hdfull_sid", sid)
                account = True
                if not config.get_setting("logged", channel=canonical['channel']):
                    config.set_setting("logged", account, channel=canonical['channel'])
                logger.info('Just LOGGED', force=True)
                check_user_status(reset=True)
                return True
        
        logger.info('Error on LOGIN: %s' % str(new_data), force=True)
        if not _silence:
            dialog_notification("No se pudo realizar el login", "Revise sus datos en la configuración del canal", sound=False)
        return False

def logout(item):
    global just_logout, account, user_status, sid, js_data, data_js, user_, pass_
    logger.info('LOGGED OFF', force=True)
    
    # Logoff en la web
    data = agrupa_datos(AlfaChannel.urljoin(host, 'logout'), referer=host, force_check=False, force_login=False, 
                        hide_infobox=True)
    
    # Borramos cookies de hdfull
    domain = AlfaChannel.obtain_domain(host)
    dict_cookie = {"domain": domain, 'expires': 0}
    AlfaChannel.httptools.set_cookies(dict_cookie)
    dict_cookie = {"domain": '.'+domain, 'expires': 0}
    AlfaChannel.httptools.set_cookies(dict_cookie)

    account = False
    config.set_setting("logged", account, channel=canonical['channel'])
    user_status = {}
    sid = ''
    js_data = ''
    data_js = ''
    just_logout = True
    if window:
        window.setProperty("AH_hdfull_user_status", jsontools.dump(user_status))
        window.setProperty("AH_hdfull_sid", sid)
        window.setProperty("AH_hdfull_js_data", js_data)
        window.setProperty("AH_hdfull_data_js", data_js)
        window.setProperty("AH_hdfull_just_logout", str(just_logout))
        config.set_setting('just_logout', just_logout, channel=canonical['channel'])

    # Avisamos, si nos dejan
    if not _silence:
        dialog_notification("Deslogueo completo", "Verifique su cuenta", sound=False,)
    if item.refresh: itemlist_refresh()

    return [item]

def agrupa_datos(url, post=None, referer=True, soup=False, json=False, force_check=False, force_login=True, alfa_s=False, hide_infobox=False):
    global account, sid, user_status

    headers = {'Referer': host}
    if 'episodes' in url or 'buscar' in url:
        headers['Referer'] += 'episodios'
    if isinstance(referer, str):
        headers.update({'Referer': referer})

    page = AlfaChannel.create_soup(url, post=post, headers=headers, ignore_response_code=True, timeout=timeout, 
                                   soup=False, json=False, canonical=canonical, hide_infobox=hide_infobox, alfa_s=alfa_s)

    if page.sucess and page.host and host_save not in page.host:
        account = False
        config.set_setting("logged", account, channel=canonical['channel'])
        sid = ''
        if window: window.setProperty("AH_hdfull_sid", sid)
        user_status = {}
        if window: window.setProperty("AH_hdfull_user_status", jsontools.dump(user_status))
        url = page.url_new
        return agrupa_datos(url, post=post, referer=referer, alfa_s=alfa_s, hide_infobox=hide_infobox, 
                            json=json, force_check=force_check, force_login=True)

    if not page.sucess:
        account = False
        config.set_setting("logged", account, channel=canonical['channel'])
        config.set_setting("current_host", '', channel=canonical['channel'])
        sid = ''
        if window: window.setProperty("AH_hdfull_sid", sid)
        user_status = {}
        if window: window.setProperty("AH_hdfull_user_status", jsontools.dump(user_status))
        return {} if json else ''

    if json:
        if not page.json and page.data:
            page.json = page.data
            if not isinstance(page.json, _dict):
                page.json = jsontools.load(page.json)
        return page.json
    
    if (page.data or (not page.data and not post)) and not 'application' in page.headers['Content-Type'] and not check_login_status(page.data):
        res = False
        if force_login and not 'login' in url and not 'logout' in url:
            res = login(page.data)
        if not res:
            return {} if json else page.data
        else:
            return agrupa_datos(url, post=post, referer=referer, alfa_s=alfa_s, hide_infobox=hide_infobox, 
                                json=json, force_check=force_check, force_login=False)
    
    data = page.data
    if PY3 and isinstance(data, bytes):
        data = "".join(chr(x) for x in bytes(data))
    ## Agrupa los datos
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|<!--.*?-->', '', data)
    data = re.sub(r'\s+', ' ', data)
    data = re.sub(r'>\s<', '><', data)
    
    return data


""" USER's UTILITIES """
def set_status__(item):

    if item.contentType == 'movie':
        agreg = 'Pelicula "%s"' % item.contentTitle
        mediatype = '2'
    else:
        agreg = 'Serie "%s"' % item.contentSerieName
        mediatype = '1' if item.contentType == 'tvshow' else '3' if item.contentType == 'episode' else '4'
    if "###" in item.url:
        item.info = {item.url.split("###")[1].split(";")[0]: item.url.split("###")[1].split(";")[0]}
        item.url = item.url.split("###")[0]
    info = list(item.info.keys())[0] if item.info else ''
    info_show = list(item.info.values())[0] if item.info else ''
    list_info = list(item.list_info.values())[0] if item.list_info else ''

    if "Abandonar" in item.title and item.list_info:
        title = "[COLOR darkgrey][B]Abandonando Lista %s[/B][/COLOR]"
        path = "a/my"
        post = "id=%s&target=lists&action=delete" % (list_info)

    elif "Añadir" in item.title and item.list_info:
        title = "[COLOR blue][B]Añadiendo Lista %s[/B][/COLOR]"
        path = "a/my"
        post = "id=%s&target=lists&action=follow" % (list_info)

    elif "Abandonar" in item.title or "Pendiente " in item.title:
        title = "[COLOR darkgrey][B]Abandonando %s[/B][/COLOR]"
        path = "/a/status"
        post = "target_id=%s&target_type=%s&target_status=0" % (info_show, mediatype)

    elif "Marcar Visto" in item.title:
        title = "[COLOR blue][B]Visto %s[/B][/COLOR]"
        path = "/a/status"
        post = "target_id=%s&target_type=%s&target_status=1" % (info, mediatype)

    elif "Visto" in item.title:
        title = "[COLOR darkgrey][B]No Vista %s[/B][/COLOR]"
        path = "/a/status"
        post = "target_id=%s&target_type=%s&target_status=0" % (info, mediatype)

    elif "Quitar de Seguir" in item.title:
        title = "[COLOR darkgrey][B]%s No Siguiendo[/B][/COLOR]"
        path = "/a/status"
        post = "target_id=%s&target_type=%s&target_status=0" % (info_show, mediatype)

    elif "Seguir" in item.title:
        title = "[COLOR orange][B]Siguiendo %s[/B][/COLOR]"
        path = "/a/status"
        post = "target_id=%s&target_type=%s&target_status=3" % (info_show, mediatype)

    elif "Quitar de Finalizada" in item.title:
        title = "[COLOR darkgrey][B]%s No Finalizada[/B][/COLOR]"
        path = "/a/status"
        post = "target_id=%s&target_type=%s&target_status=0" % (info_show, mediatype)

    elif "Finalizada" in item.title:
        title = "[COLOR orange][B]%s Finalizada[/B][/COLOR]"
        path = "/a/status"
        post = "target_id=%s&target_type=%s&target_status=1" % (info_show, mediatype)

    elif "Quitar de Pendiente" in item.title:
        title = "[COLOR blue]%s No Pendiente[/COLOR]"
        path = "/a/status"
        post = "target_id=%s&target_type=%s&target_status=0" % (info_show, mediatype)

    elif "Pendiente" in item.title:
        title = "[COLOR blue]Pendiente %s[/COLOR]"
        path = "/a/status"
        post = "target_id=%s&target_type=%s&target_status=2" % (info_show, mediatype)

    elif "Quitar de Favoritos" in item.title:
        title = "[COLOR darkgrey][B]%s eliminada de Favoritos[/B][/COLOR]"
        path = "/a/favorite"
        post = "like_id=%s&like_type=%s&like_comment=&vote=-1" % (info_show, mediatype)

    elif "Agregar a Favoritos" in item.title:
        title = "[COLOR orange][B]%s agregada a Favoritos[/B][/COLOR]"
        path = "/a/favorite"
        post = "like_id=%s&like_type=%s&like_comment=&vote=1" % (info_show, mediatype)

    else:
        title = "[COLOR darkgrey][B]%s eliminada de Favoritos[/B][/COLOR]"
        path = "/a/favorite"
        post = "like_id=%s&like_type=%s&like_comment=&vote=-1" % (info_show, mediatype)

    data = agrupa_datos(AlfaChannel.urljoin(host, path), post=post, hide_infobox=True)
    check_user_status(reset=True)
    if debug: logger.debug('Post: %s' % post)

    title = title % agreg
    dialog_ok(item.contentSerieName or item.contentTitle, title)

def get_status(status, elem, mediatype=''):
    
    if isinstance(elem, _dict):
        info = elem.get('info', {})
        list_info = list(elem.get('list_info', {}).values())[0] if elem.get('list_info', {}) else ''
        mediatype = elem.get('mediatype', mediatype)
    else:
        info = elem.info or {}
        list_info = list(elem.list_info.values())[0] if elem.list_info else ''
        mediatype = elem.contentType or mediatype

    if debug: logger.debug('info: %s; list_info: %s; mediatype: %s' % (info, list_info, mediatype))
    if not status or not account or not mediatype or (not info and not list_info):
        return ""
    
    state_shows = {'0': '', '1': 'Finalizada', '2': 'Pendiente', '3': 'Siguiendo', '4': '', '5': ''}
    state_episodes = {'0': '', '1': 'Visto', '2': '', '3': '', '4': '', '5': ''}

    if list_info:
        mediatype = 'lists'
        state = {'0': '', '1': 'MiLista', '2': '', '3': 'Siguiendo', '4': '', '5': ''}
    elif mediatype == 'tvshow':
        mediatype = 'shows'
        state = state_shows.copy()
    elif mediatype == 'episode':
        mediatype = 'episodes'
        state = state_episodes.copy()
    else:
        mediatype = 'movies'
        state = {'0': '', '1': 'Visto', '2': 'Pendiente', '3': 'Recomendadas', '4': '', '5': ''}
    
    str_ = str1 = str2 = str3 = ""

    if info and list(info.values())[0] in status.get('favorites', {}).get(mediatype, ''):
        str1 = " [COLOR orange](Favorito)[/COLOR]"

    if (info and list(info.values())[0] in status.get('status', {}).get(mediatype, '')) \
             or (list_info and list_info in status.get('status', {}).get(mediatype, '')):
        str2 = state[status['status'][mediatype][list(info.values())[0] if info else list_info]]
        if str2: str2 = " [COLOR %s](%s)[/COLOR]" % ('orange' if 'Siguiendo' in str2 else 'blue', str2)
            
    if mediatype == 'episodes':
        if info and list(info.values())[0] in status.get('favorites', {}).get('shows', ''):
            str1 = " [COLOR orange](Favorito)[/COLOR]"
        if info and list(info.values())[0] in status.get('status', {}).get('shows', ''):
            str2 = state_shows[status['status']['shows'][list(info.values())[0]]]
            if str2: str2 = " [COLOR %s](%s)[/COLOR]" % ('orange' if 'Siguiendo' in str2 else 'blue', str2)
        if info and list(info.keys())[0] in status.get('status', {}).get('episodes', ''):
            str3 = state_episodes[status['status']['episodes'][list(info.keys())[0]]]
        if str3: str2 += " [COLOR %s](%s)[/COLOR]" % ('orange' if 'Siguiendo' in str3 else 'blue', str3)

    return (str1 + str2) if (str1 or str2) else ''

def add_context(elem_json, str_, mediatype=''):

    context_dict = {"title": "",
                    "action": "set_status__",
                    "channel": "hdfull",
                    "contentType": elem_json.get('mediatype', mediatype),
                    "contentTitle": (elem_json.get('title_show', '') or elem_json.get('title', '')) \
                                     if elem_json.get('mediatype', '') == 'movie' else '',
                    "contentSerieName": '%s, %s' % (elem_json.get('title_episode', ''), elem_json.get('title_show', '') 
                                                                                        or elem_json.get('title', '')) \
                                         if elem_json.get('mediatype', '') == 'episode' else \
                                                   (elem_json.get('title_show', '') or elem_json.get('title', '')) \
                                         if elem_json.get('mediatype', '') != 'movie' else '', 
                    "info": elem_json.get('info', {}),
                    "list_info": elem_json.get('list_info', {}),
                    "url": AlfaChannel.urljoin(host, elem_json.get('url', ''))}

    elem_json['context'] = elem_json.get('context', [])[:]

    if elem_json.get('list_info', {}):
        if "Siguiendo" in str_ or "MiLista" in str_:
            context_dict['title'] = "[COLOR limegreen][B]Abandonar Lista[/B][/COLOR]"
            elem_json['context'].append(context_dict.copy())
        else:
            context_dict['title'] = "[COLOR orange][B]Añadir Lista[/B][/COLOR]"
            elem_json['context'].append(context_dict.copy())

        return elem_json

    if "Abandonar" in str_:
        context_dict['title'] = "[COLOR limegreen][B]Abandonar[/B][/COLOR]"
        elem_json['context'].append(context_dict.copy())

    if elem_json.get('mediatype', mediatype) in ['movie', 'tvshow']:
        if "Pendiente" in str_:
            context_dict['title'] = "[COLOR limegreen][B]Quitar de Pendientes[/B][/COLOR]"
            elem_json['context'].append(context_dict.copy())
        else:
            context_dict['title'] = "[COLOR orange][B]Agregar a Pendientes[/B][/COLOR]"
            elem_json['context'].append(context_dict.copy())

        if "Favorito" in str_:
            context_dict['title'] = "[COLOR limegreen][B]Quitar de Favoritos[/B][/COLOR]"
            elem_json['context'].append(context_dict.copy())
        else:
            context_dict['title'] = "[COLOR orange][B]Agregar a Favoritos[/B][/COLOR]"
            elem_json['context'].append(context_dict.copy())

    if elem_json.get('mediatype', mediatype) == 'movie':
        context_dict['title'] = "[COLOR limegreen][B]Marcar No Visto[/B][/COLOR]"
        elem_json['context'].append(context_dict.copy())

        context_dict['title'] = "[COLOR blue][B]Marcar Visto[/B][/COLOR]"
        elem_json['context'].append(context_dict.copy())

    elif elem_json.get('mediatype', mediatype) == 'tvshow':
        if "Siguiendo" in str_ :
            context_dict['title'] = "[COLOR limegreen][B]Quitar de Seguir[/B][/COLOR]"
            elem_json['context'].append(context_dict.copy())
        else:
            context_dict['title'] = "[COLOR orange][B]Agregar a Seguir[/B][/COLOR]"
            elem_json['context'].append(context_dict.copy())

        if "Finalizada" in str_:
            context_dict['title'] = "[COLOR limegreen][B]Quitar de Finalizadas[/B][/COLOR]"
            elem_json['context'].append(context_dict.copy())
        else:
            context_dict['title'] = "[COLOR orange][B]Agregar a Finalizadas[/B][/COLOR]"
            elem_json['context'].append(context_dict.copy())

    elif elem_json.get('mediatype', mediatype) == 'episode':
        context_dict['title'] = "[COLOR limegreen][B]Marcar No Visto[/B][/COLOR]"
        elem_json['context'].append(context_dict.copy())

        context_dict['title'] = "[COLOR blue][B]Marcar Visto[/B][/COLOR]"
        elem_json['context'].append(context_dict.copy())

        if list(context_dict['info'].values())[0] != '0':                       # No funciona en "Para Ver"
            context_dict_show = context_dict.copy()
            context_dict_show["contentType"] = "tvshow"

            if "Siguiendo" in str_:
                context_dict_show['title'] = "[COLOR limegreen][B]Quitar de Seguir[/B][/COLOR]"
            else:
                context_dict_show['title'] = "[COLOR orange][B]Agregar a Seguir[/B][/COLOR]"
            elem_json['context'].append(context_dict_show.copy())

            if "Pendiente" in str_:
                context_dict_show['title'] = "[COLOR limegreen][B]Quitar de Pendientes[/B][/COLOR]"
                elem_json['context'].append(context_dict_show.copy())
            else:
                context_dict_show['title'] = "[COLOR orange][B]Agregar a Pendientes[/B][/COLOR]"
                elem_json['context'].append(context_dict_show.copy())

            if "Finalizada" in str_:
                context_dict_show['title'] = "[COLOR limegreen][B]Quitar de Finalizadas[/B][/COLOR]"
                elem_json['context'].append(context_dict_show.copy())
            else:
                context_dict_show['title'] = "[COLOR orange][B]Agregar a Finalizadas[/B][/COLOR]"
                elem_json['context'].append(context_dict_show.copy())

            if "Favorito" in str_:
                context_dict_show['title'] = "[COLOR limegreen][B]Quitar de Favoritos[/B][/COLOR]"
                elem_json['context'].append(context_dict_show.copy())
            else:
                context_dict_show['title'] = "[COLOR orange][B]Agregar a Favoritos[/B][/COLOR]"
                elem_json['context'].append(context_dict_show.copy())

    return elem_json

def find_hidden_seasons(item, matches, sid):

    try:
        if isinstance(sid, _dict): sid = list(sid.values())[0]
        try:
            high_json_season = matches[-1]['season']
            url_season = re.sub('\d+$', '', matches[-1]['url'])
        except Exception:
            high_json_season = 0
            url_season = item.url

        try:
            if not item.infoLabels['number_of_seasons']:
                tmdb.set_infoLabels(item, True)
            tmdb_season = int(item.infoLabels['number_of_seasons'])
        except Exception:
            tmdb_season = high_json_season

        high_web_season = 0
        url = AlfaChannel.urljoin(host, "a/episodes")
        post = "action=lastest&start=0&limit=1&elang=ALL&show=%s" % sid
        data = agrupa_datos(url, post=post, json=True, force_check=False, force_login=False, alfa_s=True)

        if data and isinstance(data, list):
            try:
                high_web_season = int(data[0].get('season', 0))
            except Exception:
                high_web_season = 0
        logger.info('Web: %s, Json: %s, Tmdb: %s' % (high_web_season, high_json_season, tmdb_season))
        if not high_web_season or high_web_season <= high_json_season:
            return matches

        for high_season in range(high_json_season+1, high_web_season+1):
            post = "action=season&start=0&limit=0&show=%s&season=%s" % (sid, high_season)
            data = agrupa_datos(url, post=post, json=True, force_check=False, force_login=False, alfa_s=True)

            if data and isinstance(data, list):
                matches.append({'url': url_season + (str(high_season) if high_json_season > 0 else ''), 
                                'season': high_season, 'info': {sid: sid}})
                if high_season > tmdb_season: item.infoLabels['number_of_seasons'] = high_season

    except Exception:
        logger.error(traceback.format_exc())

    return matches
