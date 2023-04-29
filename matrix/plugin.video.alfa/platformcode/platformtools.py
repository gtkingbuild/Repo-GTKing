# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# platformtools
# ------------------------------------------------------------
# Herramientas responsables de adaptar los diferentes
# cuadros de dialogo a una plataforma en concreto,
# en este caso Kodi.
# version 2.0
# ------------------------------------------------------------

from __future__ import division
from __future__ import absolute_import
from past.utils import old_div

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib  # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib  # Usamos el nativo de PY2 que es más rápido

import os
import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from channelselector import get_thumb
from core import channeltools
from core import scrapertools
from core import jsontools
from core.item import Item
from platformcode import logger
from platformcode import config


class XBMCPlayer(xbmc.Player):

    def __init__(self, *args):
        pass

xbmc_player = XBMCPlayer()
PLUGIN_HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 else -1
extensions_list = ['.aaf', '.3gp', '.asf', '.avi', '.flv', '.mpeg',
                   '.m1v', '.m2v', '.m4v', '.mkv', '.mov', '.mpg',
                   '.mpe', '.mp4', '.ogg', '.rar', '.wmv', '.zip', 
                   '.m3u8', 'hls.ts']


def makeMessage(line1, line2, line3):
    message = line1
    if line2:
        message += '\n' + line2
    if line3:
        message += '\n' + line3
    return message


def dialog_ok(heading, line1, line2="", line3=""):
    dialog = xbmcgui.Dialog()
    return dialog.ok(heading, makeMessage(line1, line2, line3))


def dialog_notification(heading, message, icon=0, time=5000, sound=True):
    dialog = xbmcgui.Dialog()
    try:
        l_icono = xbmcgui.NOTIFICATION_INFO, xbmcgui.NOTIFICATION_WARNING, xbmcgui.NOTIFICATION_ERROR
        dialog.notification(heading, message, l_icono[icon], time, sound)
    except:
        dialog_ok(heading, message)


def dialog_yesno(heading, line1, line2="", line3="", nolabel="No", yeslabel="Si", autoclose=0, customlabel=None):
    # customlabel only on kodi 19
    dialog = xbmcgui.Dialog()
    try:
        if autoclose:
            return dialog.yesno(heading, makeMessage(line1, line2, line3), nolabel=nolabel,
                                yeslabel=yeslabel, autoclose=autoclose)
        else:
            return dialog.yesno(heading, makeMessage(line1, line2, line3), nolabel=nolabel,
                                yeslabel=yeslabel)
    except:
        if autoclose:
            return dialog.yesno(heading, makeMessage(line1, line2, line3), nolabel=nolabel,
                                yeslabel=yeslabel, customlabel=customlabel, autoclose=autoclose)
        else:
            return dialog.yesno(heading, makeMessage(line1, line2, line3), nolabel=nolabel,
                                yeslabel=yeslabel, customlabel=customlabel)


def dialog_select(heading, _list, useDetails=False):
    return xbmcgui.Dialog().select(heading, _list, useDetails=useDetails)


def dialog_multiselect(heading, _list, autoclose=0, preselect=[], useDetails=False):
    return xbmcgui.Dialog().multiselect(heading, _list, autoclose=autoclose, preselect=preselect, useDetails=useDetails)


def dialog_progress(heading, line1, line2=" ", line3=" "):
    dialog = xbmcgui.DialogProgress()
    dialog.create(heading, makeMessage(line1, line2, line3))
    return dialog


def dialog_progress_bg(heading, message=""):
    try:
        dialog = xbmcgui.DialogProgressBG()
        dialog.create(heading, message)
        return dialog
    except:
        return dialog_progress(heading, message)


def dialog_input(default="", heading="", hidden=False):
    keyboard = xbmc.Keyboard(default, heading, hidden)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    else:
        return None


def dialog_numeric(_type, heading, default=""):
    dialog = xbmcgui.Dialog()
    d = dialog.numeric(_type, heading, default)
    return d


def dialog_textviewer(heading, text):  # disponible a partir de kodi 16
    return xbmcgui.Dialog().textviewer(heading, text)


def dialog_browse(_type, heading, shares='files', default=""):
    if config.get_platform(True)['num_version'] < 18.0 and (shares == 'local' or not shares):
        shares = 'files'
    dialog = xbmcgui.Dialog()
    d = dialog.browse(_type, heading, shares)
    return d


def itemlist_refresh():
    xbmc.executebuiltin("Container.Refresh")


def itemlist_update(item, replace=False):
    if replace:  # reset the path history
        xbmc.executebuiltin("Container.Update(" + sys.argv[0] + "?" + item.tourl() + ", replace)")
    else:
        xbmc.executebuiltin("Container.Update(" + sys.argv[0] + "?" + item.tourl() + ")")


def render_items(itemlist, parent_item):
    """
    Función encargada de mostrar el itemlist en kodi, se pasa como parametros el itemlist y el item del que procede
    @type itemlist: list
    @param itemlist: lista de elementos a mostrar

    @type parent_item: item
    @param parent_item: elemento padre
    """
    logger.info('INICIO render_items')
    start = time.time()

    from core import httptools
    from platformcode import unify

    # Si el itemlist no es un list salimos
    if not isinstance(itemlist, list):
        logger.error('itemlist: list expected, got {}'.format(type(itemlist)))
        return

    # Dominios que necesitan Cloudscraper
    CF_LIST = httptools.load_CF_list()

    if parent_item.startpage:
        menu_icon = get_thumb('menu.png')
        menu = Item(channel="channelselector", action="getmainlist", viewmode="movie", thumbnail=menu_icon,
                    title='Menu')
        itemlist.insert(0, menu)

    # Si no hay ningun item, mostramos un aviso
    if not len(itemlist):
        itemlist.append(Item(title=config.get_localized_string(60347)))

    if parent_item.channel == 'videolibrary':
        channel_param = channeltools.get_channel_parameters(parent_item.contentChannel)
    else:
        channel_param = channeltools.get_channel_parameters(parent_item.channel)

    genre = False
    if 'nero' in parent_item.title:
        genre = True

    use_unify = channel_param.get('force_unify', False) or config.get_setting('unify', default=False)
    if use_unify:
        from core import servertools
        srv_lst = servertools.get_servers_list()
    if channel_param.get('adult', ''):
        use_unify = False

    # logger.debug('use_unify: %s' % use_unify)

    # for adding extendedinfo to contextual menu, if it's used
    has_extendedinfo = xbmc.getCondVisibility('System.HasAddon(script.extendedinfo)')

    # for adding superfavourites to contextual menu, if it's used
    sf_file_path = config.translatePath("special://home/addons/plugin.program.super.favourites/LaunchSFMenu.py")
    check_sf = os.path.exists(sf_file_path)
    superfavourites = check_sf and xbmc.getCondVisibility('System.HasAddon("plugin.program.super.favourites")')
    num_version_xbmc = config.get_platform(True)['num_version']

    # Recorremos el itemlist
    categories_channel = []
    if itemlist and itemlist[0].channel:
        categories_channel = channeltools.get_channel_parameters(itemlist[0].channel.lower()).get('categories', [])

    temp_list = list()

    colors_file = unify.colors_file

    for item in itemlist:
        item_url = item.tourl()

        if item.unify or item.unify == False:
            use_unify = item.unify
        else:
            if channel_param.get('adult', ''):
                use_unify = False
            else:
                use_unify = channel_param.get('force_unify', False) or config.get_setting('unify', default=False)

        # Si el item no contiene categoria, le ponemos la del item padre
        if item.category == "":
            item.category = parent_item.category

        # Si title no existe, lo iniciamos como str, para evitar errones "NoneType"
        if not item.title:
            item.title = ''

        # Si no hay action o es findvideos/play, folder=False porque no se va a devolver ningún listado
        if item.action in ['play', '']:
            item.folder = False

            # Si el item no contiene fanart, le ponemos el del item padre
        if not item.fanart:
            item.fanart = parent_item.fanart

        if genre:
            thumb = get_thumb(item.title, auto=True)
            if thumb != '':
                item.thumbnail = thumb

        elif ('siguiente' in item.title.lower() and '>' in item.title) or ('pagina:' in item.title.lower()):
            item.thumbnail = get_thumb("next.png")

        elif 'add' in item.action:
            if 'pelicula' in item.action:
                item.thumbnail = get_thumb("videolibrary_movie.png")
            elif 'serie' in item.action:
                item.thumbnail = get_thumb("videolibrary_tvshow.png")

        if item.text_color:
            item.title = '[COLOR %s]%s[/COLOR]' % (item.text_color, item.title)

        if item.text_bold:
            item.title = '[B]%s[/B]' % item.title

        if item.text_italic:
            item.title = '[I]%s[/I]' % item.title
        
        if item.action in ["search"]:
            item.title = unify.set_color(item.title, 'tvshow')

        if use_unify and parent_item.channel not in ['alfavorites']:
            # Formatear titulo con unify
            item = unify.title_format(item, colors_file, srv_lst)

        else:
            # Formatear titulo metodo old school
            if item.title == r'%s' and item.action in ("findvideos", "play"):
                item = unify.title_format(item)

        # Añade headers a las imagenes si estan en un servidor con cloudflare
        if item.action == 'play':
            item.thumbnail = unify.thumbnail_type(item)

        # if cloudflare, cookies are needed to display images taken from site
        # before checking domain (time consuming), checking if tmdb failed (so, images scraped from website are used)
        try:
            domain_cs = scrapertools.get_domain_from_url(item.url)

        except:
            domain_cs = '##is_dict/list'
            logger.error('URL is DICT/LIST: %s' % str(item.url))

        if item.action in ['findvideos'] and not item.infoLabels['tmdb_id'] and domain_cs in CF_LIST:
            item.thumbnail = httptools.get_url_headers(item.thumbnail)
            item.fanart = httptools.get_url_headers(item.fanart)

        # IconImage para folder y video
        icon_image = "DefaultFolder.png" if item.folder else "DefaultVideo.png"

        # Ponemos el fanart
        fanart = item.fanart if item.fanart else config.get_fanart()

        # Ponemos el poster
        poster = item.thumbnail
        if item.action == 'play' and item.infoLabels['temporada_poster']:
            poster = item.infoLabels['temporada_poster']

        # Creamos el listitem
        if config.get_platform(True)['num_version'] >= 18.0:
            listitem = xbmcgui.ListItem(item.title, offscreen=True)
            if config.get_platform(True)['num_version'] >= 20.0:
                infotagvideo = xbmc.InfoTagVideo(offscreen=True)
        else:
            listitem = xbmcgui.ListItem(item.title)

        # values icon, thumb or poster are skin dependent.. so we set all to avoid problems
        # if not exists thumb it's used icon value

        listitem.setArt({'icon': icon_image, 'thumb': item.thumbnail, 'poster': poster, 'fanart': fanart})

        # No need it, use fanart instead
        # xbmcplugin.setPluginFanart(PLUGIN_HANDLE, os.path.join(config.get_runtime_path(), "fanart.jpg"))

        # Esta opcion es para poder utilizar el xbmcplugin.setResolvedUrl()
        # if item.isPlayable == True or (config.get_setting("player_mode", default=0) == 1 and item.action == "play"):
        if config.get_setting("player_mode", default=0) == 1 and item.action == "play":
            listitem.setProperty('IsPlayable', 'true')

        # Añadimos los infoLabels
        set_infolabels(listitem, item)

        # No arrastrar plot si no es una peli/serie/temporada/episodio
        if item.plot and item.contentType not in ['movie', 'tvshow', 'season', 'episode']:
            item.__dict__['infoLabels'].pop('plot')

        # Montamos el menu contextual
        if parent_item.channel != 'special':
            context_commands = set_context_commands(item, item_url, parent_item, has_extendedinfo=has_extendedinfo,
                                                    superfavourites=superfavourites, num_version_xbmc=num_version_xbmc,
                                                    categories_channel=categories_channel)
        else:
            context_commands = []
        # Añadimos el menu contextual

        if parent_item.list_type == '':
            listitem.addContextMenuItems(context_commands)

        temp_list.append(['%s?%s' % (sys.argv[0], item_url), listitem, item.folder])

    xbmcplugin.addDirectoryItems(handle=PLUGIN_HANDLE, items=temp_list)

    special_channels = ["channelselector", "", "alfavorites", "news", "search", "videolibrary", "setting", "help"]

    # Fijar los tipos de vistas...
    if config.get_setting("forceview"):  # ...forzamos segun el viewcontent
        xbmcplugin.setContent(PLUGIN_HANDLE, parent_item.viewcontent)

    elif parent_item.channel == "alfavorites" and parent_item.action == 'mostrar_perfil':
        xbmcplugin.setContent(PLUGIN_HANDLE, "movies")

    elif parent_item.channel == "videolibrary":
        if parent_item.action == 'list_tvshows':
            xbmcplugin.setContent(PLUGIN_HANDLE, "tvshows")
        elif parent_item.action == 'list_movies':
            xbmcplugin.setContent(PLUGIN_HANDLE, "movies")
        elif parent_item.action != 'mainlist':
            if parent_item.contentType == 'movie':
                xbmcplugin.setContent(PLUGIN_HANDLE, "movies")
            else:
                xbmcplugin.setContent(PLUGIN_HANDLE, "episodes")

    elif parent_item.startpage == True:
        xbmcplugin.setContent(PLUGIN_HANDLE, "movies")
        # parent_item.viewmode = "movie_with_plot"
        parent_item.viewmode = "poster"
        viewmode_id = get_viewmode_id(parent_item)
        xbmc.executebuiltin("Container.SetViewMode({})".format(viewmode_id))

    elif parent_item.viewType:
        xbmcplugin.setContent(PLUGIN_HANDLE, parent_item.viewType)

    elif parent_item.channel in ["alfavorites", "favorites", "news", "search"]:
        if parent_item.action != "mainlist" or parent_item.channel == "favorites":
            xbmcplugin.setContent(PLUGIN_HANDLE, "movies")

    elif parent_item.channel not in special_channels and parent_item.action != "mainlist":  # ... o segun el canal
        xbmcplugin.setContent(PLUGIN_HANDLE, "movies")

    # Fijamos el "breadcrumb"
    if parent_item.list_type != '':
        if 'similar' in parent_item.list_type:
            if parent_item.contentTitle != '':
                breadcrumb = 'Similares (%s)' % parent_item.contentTitle
            else:
                breadcrumb = 'Similares (%s)' % parent_item.contentSerieName
        else:
            breadcrumb = 'Busqueda'
    else:
        if parent_item.category != '':
            breadcrumb = parent_item.category.capitalize()
        else:
            breadcrumb = channeltools.get_channel_parameters(parent_item.channel).get('title', '')

    xbmcplugin.setPluginCategory(handle=PLUGIN_HANDLE, category=breadcrumb)

    # No ordenar items
    xbmcplugin.addSortMethod(handle=PLUGIN_HANDLE, sortMethod=xbmcplugin.SORT_METHOD_NONE)

    # Cerramos el directorio
    xbmcplugin.endOfDirectory(handle=PLUGIN_HANDLE, succeeded=True)

    # Fijar la vista
    if config.get_setting("forceview"):
        viewmode_id = get_viewmode_id(parent_item)
        xbmc.executebuiltin("Container.SetViewMode(%s)" % viewmode_id)
    if parent_item.mode in ['silent', 'get_cached', 'set_cache', 'finish']:
        xbmc.executebuiltin("Container.SetViewMode(500)")

    logger.info('FINAL render_items %s elementos: %s' % (len(itemlist), (time.time() - start)))


def get_viewmode_id(parent_item):
    # viewmode_json habria q guardarlo en un archivo y crear un metodo para q el user fije sus preferencias en:
    # user_files, user_movies, user_tvshows, user_season y user_episodes.
    viewmode_json = {'skin.ace2': {'default_files': 50,
                                   'default_movies': 515,
                                   'default_tvshows': 508,
                                   'default_seasons': 503,
                                   'default_episodes': 504,
                                   'view_list': 50,
                                   'view_poster': 51,
                                   'view_thumbnails': 500,
                                   'view_movie_with_plot': 56},
                     'skin.aeon.nox.silvo': {'default_files': 50,
                                             'default_movies': 515,
                                             'default_tvshows': 508,
                                             'default_seasons': 503,
                                             'default_episodes': 504,
                                             'view_list': 50,
                                             'view_poster': 509,
                                             'view_thumbnails': 500,
                                             'view_movie_with_plot': 51},
                     'skin.aeon.tajo': {'default_files': 50,
                                        'default_movies': 515,
                                        'default_tvshows': 508,
                                        'default_seasons': 503,
                                        'default_episodes': 504,
                                        'view_list': 50,
                                        'view_poster': 595,
                                        'view_thumbnails': 500,
                                        'view_movie_with_plot': 590},
                     'skin.amber': {'default_files': 50,
                                    'default_movies': 515,
                                    'default_tvshows': 508,
                                    'default_seasons': 503,
                                    'default_episodes': 504,
                                    'view_list': 50,
                                    'view_poster': 56,
                                    'view_thumbnails': 500,
                                    'view_movie_with_plot': 551},
                     'skin.apptv': {'default_files': 50,
                                    'default_movies': 515,
                                    'default_tvshows': 508,
                                    'default_seasons': 503,
                                    'default_episodes': 504,
                                    'view_list': 50,
                                    'view_poster': 54,
                                    'view_thumbnails': 500,
                                    'view_movie_with_plot': 58},
                     'skin.bello.7': {'default_files': 50,
                                  'default_movies': 515,
                                  'default_tvshows': 508,
                                  'default_seasons': 503,
                                  'default_episodes': 504,
                                  'view_list': 50,
                                  'view_poster': 66,
                                  'view_thumbnails': 500,
                                  'view_movie_with_plot': 50},
                     'skin.box': {'default_files': 50,
                                  'default_movies': 515,
                                  'default_tvshows': 508,
                                  'default_seasons': 503,
                                  'default_episodes': 504,
                                  'view_list': 50,
                                  'view_poster': 532,
                                  'view_thumbnails': 500,
                                  'view_movie_with_plot': 58},
                     'skin.confluence': {'default_files': 50,
                                         'default_movies': 515,
                                         'default_tvshows': 508,
                                         'default_seasons': 503,
                                         'default_episodes': 504,
                                         'view_list': 50,
                                         'view_poster': 503,
                                         'view_thumbnails': 500,
                                         'view_movie_with_plot': 504},
                     'skin.embuary-leia': {'default_files': 50,
                                         'default_movies': 515,
                                         'default_tvshows': 508,
                                         'default_seasons': 503,
                                         'default_episodes': 504,
                                         'view_list': 50,
                                         'view_poster': 56,
                                         'view_thumbnails': 500,
                                         'view_movie_with_plot': 51},
                     'skin.eminence.2': {'default_files': 50,
                                         'default_movies': 515,
                                         'default_tvshows': 508,
                                         'default_seasons': 503,
                                         'default_episodes': 504,
                                         'view_list': 50,
                                         'view_poster': 52,
                                         'view_thumbnails': 500,
                                         'view_movie_with_plot': 59},
                     'skin.estuary': {'default_files': 50,
                                      'default_movies': 54,
                                      'default_tvshows': 502,
                                      'default_seasons': 500,
                                      'default_episodes': 53,
                                      'view_list': 50,
                                      'view_poster': 51,
                                      'view_thumbnails': 500,
                                      'view_movie_with_plot': 54},
                     'skin.ftv': {'default_files': 50,
                                  'default_movies': 515,
                                  'default_tvshows': 508,
                                  'default_seasons': 503,
                                  'default_episodes': 504,
                                  'view_list': 50,
                                  'view_poster': 57,
                                  'view_thumbnails': 500,
                                  'view_movie_with_plot': 57},
                     'skin.madnox': {'default_files': 50,
                                     'default_movies': 515,
                                     'default_tvshows': 508,
                                     'default_seasons': 503,
                                     'default_episodes': 504,
                                     'view_list': 50,
                                     'view_poster': 510,
                                     'view_thumbnails': 500,
                                     'view_movie_with_plot': 530},
                     'skin.quartz': {'default_files': 50,
                                     'default_movies': 515,
                                     'default_tvshows': 508,
                                     'default_seasons': 503,
                                     'default_episodes': 504,
                                     'view_list': 50,
                                     'view_poster': 501,
                                     'view_thumbnails': 500,
                                     'view_movie_with_plot': 502},
                     'skin.rapier': {'default_files': 50,
                                     'default_movies': 515,
                                     'default_tvshows': 508,
                                     'default_seasons': 503,
                                     'default_episodes': 504,
                                     'view_list': 50,
                                     'view_poster': 53,
                                     'view_thumbnails': 500,
                                     'view_movie_with_plot': 97},
                     'skin.revolve': {'default_files': 50,
                                      'default_movies': 515,
                                      'default_tvshows': 508,
                                      'default_seasons': 503,
                                      'default_episodes': 504,
                                      'view_list': 50,
                                      'view_poster': 53,
                                      'view_thumbnails': 500,
                                      'view_movie_with_plot': 58},
                     'skin.transparency': {'default_files': 50,
                                           'default_movies': 515,
                                           'default_tvshows': 508,
                                           'default_seasons': 503,
                                           'default_episodes': 504,
                                           'view_list': 50,
                                           'view_poster': 55,
                                           'view_thumbnails': 500,
                                           'view_movie_with_plot': 58},
                     'skin.default': {'default_files': 50,
                                      'default_movies': 515,
                                      'default_tvshows': 508,
                                      'default_seasons': 503,
                                      'default_episodes': 504,
                                      'view_list': 50,
                                      'view_poster': 55,
                                      'view_thumbnails': 500,
                                      'view_movie_with_plot': 501}}

    # Si el parent_item tenia fijado un viewmode usamos esa vista...
    if parent_item.viewmode == 'movie':
        # Remplazamos el antiguo viewmode 'movie' por 'thumbnails'
        parent_item.viewmode = 'thumbnails'

    if parent_item.viewmode in ["list", "movie_with_plot", "thumbnails", "poster"]:
        view_name = "view_" + parent_item.viewmode

        '''elif isinstance(parent_item.viewmode, int):
            # only for debug
            viewName = parent_item.viewmode'''

    # ...sino ponemos la vista por defecto en funcion del viewcontent
    else:
        view_name = "default_" + parent_item.viewcontent

    skin_name = xbmc.getSkinDir()
    if skin_name not in viewmode_json:
        if skin_name in ['skin.unity']:
            skin_name = 'skin.confluence'
        else:
            skin_name = 'skin.default'
    view_skin = viewmode_json[skin_name]
    return view_skin.get(view_name, 50)


def set_infolabels(listitem, item, player=False):
    """
    Metodo para pasar la informacion al listitem (ver tmdb.set_InfoLabels() )
    item.infoLabels es un dicionario con los pares de clave/valor descritos en:
    http://mirrors.xbmc.org/docs/python-docs/14.x-helix/xbmcgui.html#ListItem-setInfo
    https://kodi.wiki/view/InfoLabels
    @param listitem: objeto xbmcgui.ListItem
    @type listitem: xbmcgui.ListItem
    @param item: objeto Item que representa a una pelicula, serie o capitulo
    @type item: item
    """

    infoLabels_dict = {'aired': 'aired', 'album': 'album', 'artist': 'artist', 'cast': 'cast',
                       'castandrole': 'castandrole', 'tmdb_id': 'code', 'code': 'code', 'country': 'country',
                       'credits': 'credits', 'release_date': 'dateadded', 'dateadded': 'dateadded', 'dbid': 'dbid',
                       'director': 'director', 'duration': 'duration', 'episode': 'episode',
                       'episodio_sinopsis': 'episodeguide', 'episodio_air_date': 'None', 'episodio_imagen': 'None',
                       'episodio_titulo': 'title', 'episodio_vote_average': 'rating', 'episodio_vote_count': 'votes',
                       'fanart': 'None', 'genre': 'genre', 'homepage': 'None', 'imdb_id': 'imdbnumber',
                       'imdbnumber': 'imdbnumber', 'in_production': 'None', 'last_air_date': 'lastplayed',
                       'mediatype': 'mediatype', 'mpaa': 'mpaa', 'number_of_episodes': 'None',
                       'number_of_seasons': 'None', 'original_language': 'None', 'originaltitle': 'originaltitle',
                       'overlay': 'overlay', 'poster_path': 'path', 'popularity': 'None', 'playcount': 'playcount',
                       'plot': 'plot', 'plotoutline': 'plotoutline', 'premiered': 'premiered', 'quality': 'None',
                       'rating': 'rating', 'season': 'season', 'set': 'set', 'setid': 'setid',
                       'setoverview': 'setoverview', 'showlink': 'showlink', 'sortepisode': 'sortepisode',
                       'sortseason': 'sortseason', 'sorttitle': 'sorttitle', 'status': 'status', 'studio': 'studio',
                       'tag': 'tag', 'tagline': 'tagline', 'temporada_air_date': 'None', 'temporada_nombre': 'None',
                       'temporada_num_episodios': 'None', 'temporada_poster': 'None', 'title': 'title',
                       'top250': 'top250', 'tracknumber': 'tracknumber', 'trailer': 'trailer', 'thumbnail': 'None',
                       'tvdb_id': 'None', 'tvshowtitle': 'tvshowtitle', 'type': 'None', 'userrating': 'userrating',
                       'url_scraper': 'None', 'votes': 'votes', 'writer': 'writer', 'year': 'year'}

    """
    if item.infoLabels:
        if 'mediatype' not in item.infoLabels:
            item.infoLabels['mediatype'] = item.contentType
        try:
            infoLabels_kodi = {infoLabels_dict[label_tag]: item.infoLabels[label_tag] for label_tag, label_value in list(item.infoLabels.items()) if infoLabels_dict[label_tag] != 'None'}
            listitem.setInfo("video", infoLabels_kodi)
        except:
            listitem.setInfo("video", item.infoLabels)
            logger.error(item.infoLabels)
    """
    infoLabels_kodi = {}
    if config.get_platform(True)['num_version'] >= 20.0:
        infotagvideo = xbmc.InfoTagVideo(offscreen=True)

    if item.infoLabels:
        try:
            if config.get_platform(True)['num_version'] < 18.0:
                listitem.setUniqueIDs({"tmdb": item.infoLabels.get("tmdb_id", 0),
                                  "imdb": item.infoLabels.get("imdb_id", 0),
                                  "tvdb": item.infoLabels.get("tvdb_id", 0)})
            elif config.get_platform(True)['num_version'] < 20.0:
                listitem.setUniqueIDs({"tmdb": item.infoLabels.get("tmdb_id", 0),
                                  "imdb": item.infoLabels.get("imdb_id", 0),
                                  "tvdb": item.infoLabels.get("tvdb_id", 0)}, "imdb")
            else:                                                                               ### VERIFY
                infotagvideo.setUniqueIDs(str({"tmdb": item.infoLabels.get("tmdb_id", 0),
                                  "imdb": item.infoLabels.get("imdb_id", 0),
                                  "tvdb": item.infoLabels.get("tvdb_id", 0)}), "imdb")
        except:
            import traceback
            logger.error(traceback.format_exc())

        if 'mediatype' not in item.infoLabels:
            item.infoLabels['mediatype'] = item.contentType
        try:
            for label_tag, label_value in list(item.infoLabels.items()):
                try:
                    #logger.debug(str(label_tag) + ': ' + str(infoLabels_dict[label_tag]))
                    if infoLabels_dict[label_tag] != 'None':
                        infoLabels_kodi.update({infoLabels_dict[label_tag]: item.infoLabels[label_tag]})
                except:
                    continue

            # HACK: Arreglo para 'Invalid media type "list"'
            # TODO: Investigar por qué no se puede arreglar antes
            if infoLabels_kodi['mediatype'] == 'list':
                infoLabels_kodi['mediatype'] = 'video'

            if config.get_platform(True)['num_version'] >= 20.0:
                listitem.setInfo("video", infoLabels_kodi)                      ### TEMPORAL
            else:
                listitem.setInfo("video", infoLabels_kodi)

        except:
            if config.get_platform(True)['num_version'] >= 20.0:
                listitem.setInfo("video", item.infoLabels)                      ### TEMPORAL
            else:
                listitem.setInfo("video", item.infoLabels)
            logger.error(item.infoLabels)
            logger.error(infoLabels_kodi)

    if player and not item.contentTitle:
        if config.get_platform(True)['num_version'] >= 20.0:
            listitem.setInfo("video", {"Title": item.title})                    ### TEMPORAL
        else:
            listitem.setInfo("video", {"Title": item.title})

    elif not player:
        if config.get_platform(True)['num_version'] >= 20.0:
            listitem.setInfo("video", {"Title": item.title})                    ### TEMPORAL
        else:
            listitem.setInfo("video", {"Title": item.title})


def set_context_commands(item, item_url, parent_item, categories_channel=[], **kwargs):
    """
    Función para generar los menus contextuales.
        1. Partiendo de los datos de item.context
             a. Metodo antiguo item.context tipo str separando las opciones por "|" (ejemplo: item.context = "1|2|3")
                (solo predefinidos)
            b. Metodo list: item.context es un list con las diferentes opciones del menu:
                - Predefinidos: Se cargara una opcion predefinida con un nombre.
                    item.context = ["1","2","3"]

                - dict(): Se cargara el item actual modificando los campos que se incluyan en el dict() en caso de
                    modificar los campos channel y action estos serán guardados en from_channel y from_action.
                    item.context = [{"title":"Nombre del menu", "action": "action del menu",
                                        "channel":"channel del menu"}, {...}]

        2. Añadiendo opciones segun criterios
            Se pueden añadir opciones al menu contextual a items que cumplan ciertas condiciones.


        3. Añadiendo opciones a todos los items
            Se pueden añadir opciones al menu contextual para todos los items

        4. Se pueden deshabilitar las opciones del menu contextual añadiendo un comando 'no_context' al item.context.
            Las opciones que Kodi, el skin u otro añadido añada al menu contextual no se pueden deshabilitar.

    @param item: elemento que contiene los menu contextuales
    @type item: item
    @param parent_item:
    @type parent_item: item
    """
    context_commands = []
    # return context_commands
    # Creamos un list con las diferentes opciones incluidas en item.context
    if isinstance(item.context, str):
        context = item.context.split("|")
    elif isinstance(item.context, list):
        context = item.context
    else:
        context = []

    # Opciones segun item.context
    for command in context:
        # Predefinidos
        if isinstance(command, str):
            if command == "no_context":
                return []

        # Formato dict
        if isinstance(command, dict):
            # Los parametros del dict, se sobreescriben al nuevo context_item en caso de sobreescribir "action" y
            # "channel", los datos originales se guardan en "from_action" y "from_channel"
            if "action" in command:
                command["from_action"] = item.action
            if "channel" in command:
                command["from_channel"] = item.channel

            # Si no se está dentro de Alfavoritos y hay los contextos de alfavoritos, descartarlos.
            # (pasa al ir a un enlace de alfavoritos, si este se clona en el canal)
            if parent_item.channel != 'alfavorites' and 'i_perfil' in command and 'i_enlace' in command:
                continue

            if "goto" in command:
                context_commands.append((command["title"], "Container.Refresh (%s?%s)" %
                                         (sys.argv[0], item.clone(**command).tourl())))
            if "switch_to" in command:
                context_commands.append((command["title"], "Container.Update (%s?%s)" %
                                         (sys.argv[0], item.clone(**command).tourl())))
            else:
                context_commands.append(
                    (command["title"], "RunPlugin(%s?%s)" % (sys.argv[0], item.clone(**command).tourl())))

    # No añadir más opciones predefinidas si se está dentro de Alfavoritos
    if parent_item.channel in ['alfavorites', 'info_popup']:
        return context_commands
        # Opciones segun criterios, solo si el item no es un tag (etiqueta), ni es "Añadir a la videoteca", etc...

    if item.action and item.action not in ["add_pelicula_to_library", "add_serie_to_library", "buscartrailer",
                                           "actualizar_titulos"]:
        # Mostrar informacion: si el item tiene plot suponemos q es una serie, temporada, capitulo o pelicula
        if item.infoLabels['plot'] and (kwargs.get('num_version_xbmc') < 17.0 or item.contentType == 'season'):
            context_commands.append((config.get_localized_string(60348), "Action(Info)"))

        # ExtendedInfo: Si está instalado el addon y se cumplen una serie de condiciones
        if kwargs.get('has_extendedinfo') \
                and config.get_setting("extended_info", default=False) == True:
            if item.contentType == "episode" and item.contentEpisodeNumber and item.contentSeason \
                    and (item.infoLabels['tmdb_id'] or item.contentSerieName):
                param = "tvshow_id =%s, tvshow=%s, season=%s, episode=%s" \
                        % (item.infoLabels['tmdb_id'], item.contentSerieName, item.contentSeason,
                           item.contentEpisodeNumber)
                context_commands.append(("ExtendedInfo",
                                         "RunScript(script.extendedinfo,info=extendedepisodeinfo,%s)" % param))

            elif item.contentType == "season" and item.contentSeason \
                    and (item.infoLabels['tmdb_id'] or item.contentSerieName):
                param = "tvshow_id =%s,tvshow=%s, season=%s" \
                        % (item.infoLabels['tmdb_id'], item.contentSerieName, item.contentSeason)
                context_commands.append(("ExtendedInfo",
                                         "RunScript(script.extendedinfo,info=seasoninfo,%s)" % param))

            elif item.contentType == "tvshow" and (item.infoLabels['tmdb_id'] or item.infoLabels['tvdb_id'] or
                                                   item.infoLabels['imdb_id'] or item.contentSerieName):
                param = "id =%s,tvdb_id=%s,imdb_id=%s,name=%s" \
                        % (item.infoLabels['tmdb_id'], item.infoLabels['tvdb_id'], item.infoLabels['imdb_id'],
                           item.contentSerieName)
                context_commands.append(("ExtendedInfo",
                                         "RunScript(script.extendedinfo,info=extendedtvinfo,%s)" % param))

            elif item.contentType == "movie" and (item.infoLabels['tmdb_id'] or item.infoLabels['imdb_id'] or
                                                  item.contentTitle):
                param = "id =%s,imdb_id=%s,name=%s" \
                        % (item.infoLabels['tmdb_id'], item.infoLabels['imdb_id'], item.contentTitle)

                context_commands.append(("ExtendedInfo",
                                         "RunScript(script.extendedinfo,info=extendedinfo,%s)" % param))

        # InfoPlus
        if config.get_setting("infoplus"):
            # if item.infoLabels['tmdb_id'] or item.infoLabels['imdb_id'] or item.infoLabels['tvdb_id'] or \
            #        (item.contentTitle and item.infoLabels["year"]) or item.contentSerieName:
            if item.infoLabels['tmdb_id'] or item.infoLabels['imdb_id'] or item.infoLabels['tvdb_id']:
                context_commands.append(("InfoPlus", "RunPlugin(%s?%s&%s)" % (sys.argv[0], item_url,
                                                                              'channel=infoplus&action=start&from_channel=' + item.channel)))

        # Ir al Menu Principal (channel.mainlist)
        """
        if parent_item.channel not in ["news", "channelselector"] and item.action != "mainlist" \
                and parent_item.action != "mainlist":
            context_commands.append((config.get_localized_string(60349), "Container.Refresh (%s?%s)" %
                                     (sys.argv[0], Item(channel=item.channel, action="mainlist").tourl())))
        """

        # Añadir a Favoritos
        if kwargs.get('num_version_xbmc') < 17.0 and (item.channel not in ["favorites", "videolibrary", "help", ""]
                                                      or item.action in [
                                                          "update_videolibrary"]) and parent_item.channel != "favorites":
            context_commands.append(
                (config.get_localized_string(30155), "RunPlugin(%s?%s&%s)" %
                 (sys.argv[0], item_url,
                  'channel=favorites&action=addFavourite&from_channel=' + item.channel + '&from_action=' + item.action)))

        # Añadir a Alfavoritos (Mis enlaces)
        if item.channel not in ["favorites", "videolibrary", "help", "search", ""] and parent_item.channel != "favorites":
            context_commands.append(
                ('[COLOR blue]%s[/COLOR]' % config.get_localized_string(70557), "RunPlugin(%s?%s&%s)" %
                 (sys.argv[0], item_url, urllib.urlencode({'channel': "alfavorites", 'action': "addFavourite",
                                                           'from_channel': item.channel,
                                                           'from_action': item.action}))))

        # Buscar en otros canales
        if item.contentType in ['movie', 'tvshow'] and item.channel != 'search' and item.action not in ['play']:

            # Buscar en otros canales
            if item.contentSerieName != '':
                item.wanted = item.contentSerieName
            else:
                item.wanted = item.contentTitle

            if item.contentType == 'tvshow':
                mediatype = 'tv'
            else:
                mediatype = item.contentType

            context_commands.append((config.get_localized_string(60350),
                                     "Container.Update (%s?%s)" % (sys.argv[0],
                                                                   item.clone(channel='search',
                                                                              action="from_context",
                                                                              from_channel=item.channel,
                                                                              contextual=True,
                                                                              text=item.wanted).tourl())))

            context_commands.append(
                ("[COLOR yellow]%s[/COLOR]" % config.get_localized_string(70561), "Container.Update (%s?%s&%s)" % (
                    sys.argv[0], item_url,
                    'channel=search&action=from_context&search_type=list&page=1&list_type=%s/%s/similar' % (
                        mediatype, item.infoLabels['tmdb_id']))))

        # Definir como Pagina de inicio
        if config.get_setting('start_page'):
            if item.action not in ['episodios', 'seasons', 'findvideos', 'play']:
                context_commands.insert(0, (config.get_localized_string(60351),
                                            "RunPlugin(%s?%s)" % (
                                                sys.argv[0], Item(channel='side_menu',
                                                                  action="set_custom_start",
                                                                  parent=item.tourl()).tourl())))

        # Añadir a videoteca
        if item.channel != "videolibrary":
            # Añadir Serie a la videoteca
            if item.action in ["episodios", "get_episodios", "seasons"] and item.contentSerieName:
                if item.action == "seasons":
                    action = "episodios"
                else:
                    action = item.action
                context_commands.append((config.get_localized_string(60352), "RunPlugin(%s?%s&%s)" %
                                         (sys.argv[0], item_url, 'action=add_serie_to_library&from_action=' + action)))
                context_commands.append(('Agregar temporada a videoteca', "RunPlugin(%s?%s&%s)" %
                                         (sys.argv[0], item_url, 'action=add_season_to_library&from_action=' + action)))
            # Añadir Pelicula a videoteca
            elif item.action in ["detail", "findvideos"] and item.contentType == 'movie' and item.contentTitle:
                context_commands.append((config.get_localized_string(60353), "RunPlugin(%s?%s&%s)" %
                                         (sys.argv[0], item_url,
                                          'action=add_pelicula_to_library&from_action=' + item.action)))
                                          
            if item.action in ["episodios", "get_episodios", "seasons", "detail", "findvideos"]:
                channel = __import__('channels.%s' % item.channel, None, None, ["channels.%s" % item.channel])
                if hasattr(channel, 'actualizar_titulos'):
                    context_commands.append(('Actualizar título', "RunPlugin(%s?%s&%s)" %
                                             (sys.argv[0], item_url,
                                              'action=actualizar_titulos&from_action=%s&from_title_tmdb=%s&from_update=%s' \
                                              % (item.action, item.contentSerieName or item.contentTitle, True))))

        # Descargar
        if item.channel not in ["downloads", "search"]:
            # Seleccionar qué canales aceptan Descargar en ...
            if 'torrent' in str(categories_channel) and item.server and item.server != 'torrent':
                tc = '_en'
                en = ' [COLOR gold][B]en...[/B][/COLOR]'
            elif 'torrent' in str(categories_channel) or item.server == 'torrent':
                tc = ''
                en = ''
            else:
                tc = '_en'
                en = ' [COLOR gold][B]en...[/B][/COLOR]'

            # TODO: Deshacerse del 'list' en core.item por favor
            if item.contentChannel and not 'list' in item.contentChannel:
                if item.channel == 'videolibrary':
                    channel_p = item.contentChannel
                else:
                    channel_p = item.channel
            else:
                channel_p = item.channel

            # Descargar pelicula
            if item.contentType == "movie" and item.contentTitle:
                context_commands.append((config.get_localized_string(60354), "RunPlugin(%s?%s&%s)" %
                                         (sys.argv[0], item_url,
                                          'channel=downloads&action=save_download&from_channel=' + item.channel + '&from_action=' + item.action)))
                if tc:
                    context_commands.append((config.get_localized_string(60354) + en, "RunPlugin(%s?%s&%s)" %
                                             (sys.argv[0], item_url,
                                              'channel=downloads&action=save_download%s&from_channel=' % tc + item.channel + '&from_action=' + item.action)))

            elif item.contentSerieName or (
                    item.contentType in ["tvshow", "episode"] and item.infoLabels['tmdb_id'] == 'None'):
                # Descargar serie
                if item.contentType in ["tvshow", "season"] or \
                                                    (item.contentType == "episode" and \
                                                    item.server == 'torrent' and item.infoLabels['tmdb_id'] != 'None' \
                                                    and not item.channel_recovery):
                    context_commands.append((config.get_localized_string(60355), "RunPlugin(%s?%s&%s)" %
                                             (sys.argv[0], item_url,
                                              'channel=downloads&action=save_download&from_channel=' + channel_p + '&sub_action=tvshow' +
                                              '&from_action=' + item.action)))
                    if tc:
                        context_commands.append((config.get_localized_string(60355) + en, "RunPlugin(%s?%s&%s)" %
                                                 (sys.argv[0], item_url,
                                                  'channel=downloads&action=save_download%s&from_channel=' % tc + channel_p + 
                                                  '&sub_action=tvshow' + '&from_action=' + item.action)))
                # Descargar serie NO vistos
                if (
                        item.contentType == "episode" and item.server == 'torrent' and item.channel == 'videolibrary' \
                                                      and not item.channel_recovery) or item.video_path:
                    context_commands.append(
                        ('Descargar Epis NO Vistos', "RunPlugin(%s?%s&%s)" %
                         (sys.argv[0], item_url,
                          'channel=downloads&action=save_download&from_channel=' + channel_p + '&sub_action=unseen' +
                          '&from_action=' + item.action)))
                # Descargar episodio
                if item.contentType == "episode":
                    context_commands.append((config.get_localized_string(60356), "RunPlugin(%s?%s&%s)" %
                                             (sys.argv[0], item_url,
                                              'channel=downloads&action=save_download&from_channel=' + channel_p +
                                              '&from_action=' + item.action)))
                    if tc:
                        context_commands.append((config.get_localized_string(60356) + en, "RunPlugin(%s?%s&%s)" %
                                                 (sys.argv[0], item_url,
                                                  'channel=downloads&action=save_download%s&from_channel=' % tc + channel_p +
                                                  '&from_action=' + item.action)))
                # Descargar temporada
                if item.contentType == "season" or parent_item.action in ["episodios", "episodesxseason"] or \
                                                    (item.contentType == "episode" \
                                                    and item.server == 'torrent' and item.infoLabels[
                                                        'tmdb_id'] != 'None' and not item.channel_recovery):
                    context_commands.append((config.get_localized_string(60357), "RunPlugin(%s?%s&%s)" %
                                             (sys.argv[0], item_url,
                                              'channel=downloads&action=save_download&from_channel=' + channel_p + '&sub_action=season' +
                                              '&from_action=' + item.action)))
                    if tc:
                        context_commands.append((config.get_localized_string(60357) + en, "RunPlugin(%s?%s&%s)" %
                                                 (sys.argv[0], item_url,
                                                  'channel=downloads&action=save_download%s&from_channel=' % tc + channel_p + '&sub_action=season' +
                                                  '&from_action=' + item.action)))

        # Abrir configuración
        if parent_item.channel not in ["setting", "news", "search"]:
            # pre-serialized: Item(channel="setting", action="mainlist").tourl()
            context_commands.append((config.get_localized_string(60358), "Container.Update(%s?%s)" %
                                     (sys.argv[0], Item(channel="setting", action="mainlist").tourl())))

        # Buscar Trailer
        if item.action == "findvideos" or "buscar_trailer" in context:
            context_commands.append(
                (config.get_localized_string(60359), "RunPlugin(%s?%s)" % (sys.argv[0], item.clone(
                    channel="trailertools", action="buscartrailer", contextual=True).tourl())))

        if kwargs.get('superfavourites'):
            context_commands.append((config.get_localized_string(60361),
                                     "RunScript(special://home/addons/plugin.program.super.favourites/LaunchSFMenu.py)"))

    context_commands = sorted(context_commands, key=lambda comand: comand[0])

    # Menu Rapido
    # pre-serialized
    # Item(channel='side_menu', action="open_menu").tourl()
    context_commands.insert(0, (config.get_localized_string(60360),
                                "Container.Update (%s?%s)" % (sys.argv[0],
                                                              'ewogICAgImFjdGlvbiI6ICJvcGVuX21lbnUiLAogICAgImNoYW5uZWwiOiAic2lkZV9tZW51Igp9Cg==')))
    return context_commands


def is_playing():
    return xbmc_player.isPlaying()


def play_video(item, strm=False, force_direct=False, autoplay=False):
    logger.info()
    # logger.debug(item.tostring('\n'))
    # logger.debug('item play: %s' % item)
    
    xbmc_player = XBMCPlayer()
    
    if item.channel == 'downloads':
        logger.info("Reproducir video local: %s [%s]" % (item.title, item.url))
        xlistitem = xbmcgui.ListItem(path=item.url)
        if config.get_platform(True)['num_version'] >= 16.0:
            xlistitem.setArt({"thumb": item.thumbnail})
        else:
            xlistitem.setThumbnailImage(item.thumbnail)

        set_infolabels(xlistitem, item, True)
        xbmc_player.play(item.url, xlistitem)
        return

    default_action = config.get_setting("default_action", default=0)
    logger.info("default_action=%s" % default_action)

    # Abre el diálogo de selección para ver las opciones disponibles
    opciones, video_urls, seleccion, salir = get_dialogo_opciones(item, default_action, strm, autoplay)
    if salir:
        return

    # se obtienen la opción predeterminada de la configuración del addon
    seleccion = get_seleccion(default_action, opciones, seleccion, video_urls)
    if seleccion < 0:  # Cuadro cancelado
        return

    logger.info("seleccion=%d" % seleccion)
    logger.info("seleccion=%s" % opciones[seleccion])

    # se ejecuta la opcion disponible, jdwonloader, descarga, favoritos, añadir a la videoteca... SI NO ES PLAY
    salir = set_opcion(item, seleccion, opciones, video_urls)
    if salir:
        return

    # obtenemos el video seleccionado
    mediaurl, view, mpd = get_video_seleccionado(item, seleccion, video_urls)
    if mediaurl == "":
        return

    # se obtiene la información del video.
    if not item.contentThumbnail:
        thumb = item.thumbnail
    else:
        thumb = item.contentThumbnail

    xlistitem = xbmcgui.ListItem(path=item.url)

    if item.setMimeType:
        xlistitem.setContentLookup(False)
        xlistitem.setMimeType(item.setMimeType)
    elif item.setMimeType is False:
        xlistitem.setContentLookup(True)
    else:
        xlistitem.setContentLookup(False)
        for extension in extensions_list:
            if extension in mediaurl:
                xlistitem.setMimeType('application/vnd.apple.mpegurl')
                break
        else:
            xlistitem.setMimeType('mime/x-type')

    if config.get_platform(True)['num_version'] >= 16.0:
        xlistitem.setArt({"thumb": thumb})
    else:
        xlistitem.setThumbnailImage(thumb)

    set_infolabels(xlistitem, item, True)

    # si se trata de un vídeo en formato mpd, se configura el listitem para reproducirlo
    # con el addon inpustreamaddon implementado en Kodi 17
    # el itemlist debe enviarse de esta manera:
    # video_urls.append(['.mpd [CinemaUpload]', url, 0, "", "mpd"])
    # donde el quinto parámetro debe existir (tipo:str o int) para que sea reconocido como un mpd
    if mpd:
        if not xbmc.getCondVisibility("System.HasAddon(inputstream.adaptive)"):
            xbmc.executebuiltin("InstallAddon(inputstream.adaptive)")
        xlistitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        xlistitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')

    # se lanza el reproductor
    if force_direct:  # cuando viene de una ventana y no directamente de la base del addon
        # Añadimos el listitem a una lista de reproducción (playlist)
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        playlist.add(mediaurl, xlistitem)

        # Reproduce
        xbmc_player.play(playlist, xlistitem)
    else:
        set_player(item, xlistitem, mediaurl, view, strm, autoplay)


def stop_video():
    xbmc_player.stop()


def get_seleccion(default_action, opciones, seleccion, video_urls):
    fixpri = False
    # para conocer en que prioridad se trabaja
    priority = int(config.get_setting("resolve_priority", default=0))
    # se usara para comprobar si hay links premium o de debriders
    check = []
    # Comprueba si resolve stop esta desactivado
    if config.get_setting("resolve_stop", default=False) == False:
        fixpri = True
    # preguntar
    if default_action == 0:
        # "Elige una opción"
        seleccion = dialog_select(config.get_localized_string(30163), opciones)
    # Ver en calidad baja
    elif default_action == 1:
        resolutions = []
        for url in video_urls:
            if "debrid]" in url[0] or "Premium)" in url[0]:
                check.append(True)
            res = calcResolution(url[0])
            if res:
                resolutions.append(res)
        if resolutions:
            if (fixpri == True and
                    check and
                    priority == 2):
                seleccion = 0
            else:
                seleccion = resolutions.index(min(resolutions))
        else:
            seleccion = 0
    # Ver en alta calidad
    elif default_action == 2:
        resolutions = []
        for url in video_urls:
            if "debrid]" in url[0] or "Premium)" in url[0]:
                check.append(True)
            res = calcResolution(url[0])
            if res:
                resolutions.append(res)

        if resolutions:
            if (fixpri == True and
                    check and
                    priority == 2):
                seleccion = 0
            else:
                seleccion = resolutions.index(max(resolutions))
        else:
            if fixpri == True and check:
                seleccion = 0
            else:
                seleccion = len(video_urls) - 1
    else:
        seleccion = 0
    return seleccion


def calcResolution(option):
    match = scrapertools.find_single_match(option, '([0-9]{2,4})x([0-9]{2,4})')
    match2 = scrapertools.find_single_match(option, '([0-9]{2,4})(?:p|i)')
    resolution = False
    if match:
        resolution = int(match[0]) * int(match[1])
    elif match2:
        resolution = int(match2)
    elif 'HD' in option:
        resolution = 720
    elif 'full hd' in option.lower():
        resolution = 1080

    return resolution


def show_channel_settings(**kwargs):
    """
    Muestra un cuadro de configuracion personalizado para cada canal y guarda los datos al cerrarlo.

    Los parámetros que se le pasan se puede ver en la el método al que se llama

    @return: devuelve la ventana con los elementos
    @rtype: SettingsWindow
    """
    from platformcode.xbmc_config_menu import SettingsWindow
    return SettingsWindow("ChannelSettings.xml", config.get_runtime_path()).start(**kwargs)


def show_video_info(*args, **kwargs):
    """
    Muestra una ventana con la info del vídeo.

    Los parámetros que se le pasan se puede ver en la el método al que se llama

    @return: devuelve la ventana con los elementos
    @rtype: InfoWindow
    """

    from platformcode.xbmc_info_window import InfoWindow
    return InfoWindow("InfoWindow.xml", config.get_runtime_path()).start(*args, **kwargs)


def show_recaptcha(key, referer):
    from platformcode.recaptcha import Recaptcha
    return Recaptcha("Recaptcha.xml", config.get_runtime_path()).Start(key, referer)


def alert_no_disponible_server(server):
    # 'El vídeo ya no está en %s' , 'Prueba en otro servidor o en otro canal'
    dialog_ok(config.get_localized_string(30055), (config.get_localized_string(30057) % server),
              config.get_localized_string(30058))


def alert_unsopported_server():
    # 'Servidor no soportado o desconocido' , 'Prueba en otro servidor o en otro canal'
    dialog_ok(config.get_localized_string(30065), config.get_localized_string(30058))


def handle_wait(time_to_wait, title, text):
    logger.info("handle_wait(time_to_wait=%d)" % time_to_wait)
    espera = dialog_progress(' ' + title, "")

    secs = 0
    increment = int(old_div(100, time_to_wait))

    cancelled = False
    while secs < time_to_wait:
        secs += 1
        percent = increment * secs
        secs_left = str((time_to_wait - secs))
        remaining_display = config.get_localized_string(70176) + secs_left + config.get_localized_string(70177)
        espera.update(percent, ' ' + text + '\n' + remaining_display)
        xbmc.sleep(1000)
        if espera.iscanceled():
            cancelled = True
            break

    if cancelled:
        logger.info('Espera cancelada')
        return False
    else:
        logger.info('Espera finalizada')
        return True


def get_dialogo_opciones(item, default_action, strm, autoplay):
    logger.info()
    # logger.debug(item.tostring('\n'))
    from core import servertools

    opciones = []
    error = False

    try:
        item.server = item.server.lower()
    except AttributeError:
        item.server = ""

    if item.server == "":
        item.server = "directo"

    # Si no es el modo normal, no muestra el diálogo porque cuelga XBMC
    muestra_dialogo = (config.get_setting("player_mode", default=0) == 0 and not strm)

    # Extrae las URL de los vídeos, y si no puedes verlo te dice el motivo
    # Permitir varias calidades para server "directo"

    if item.video_urls:
        video_urls, puedes, motivo = item.video_urls, True, ""
    else:
        video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing(
            item.server, item.url, item.password, muestra_dialogo)

    seleccion = 0
    # Si puedes ver el vídeo, presenta las opciones
    if puedes:
        for video_url in video_urls:
            # "Ver el video <calidad> [<server>]"
            opciones.append("{} {}".format(config.get_localized_string(30151), video_url[0]))

        if item.server == "local":
            opciones.append(config.get_localized_string(30164))
        else:
            opciones.append("{}".format(config.get_localized_string(30153)))
            if item.isFavourite:
                # "Quitar de favoritos"
                opciones.append(config.get_localized_string(30154))
            else:
                # "Añadir a favoritos"
                opciones.append(config.get_localized_string(30155))

            if not strm and item.contentType == 'movie':
                # "Añadir a videoteca"
                opciones.append(config.get_localized_string(30161))

        if default_action == 3:
            seleccion = len(opciones) - 1

        # Busqueda de trailers en youtube
        if item.channel not in ["Trailer", "ecarteleratrailers"]:
            # "Buscar Trailer"
            opciones.append(config.get_localized_string(30162))

    # Si no puedes ver el vídeo te informa
    else:
        if not autoplay:
            if item.server != "":
                if "<br/>" in motivo:
                    dialog_ok(config.get_localized_string(60362), motivo.split("<br/>")[0], motivo.split("<br/>")[1],
                              item.url)
                else:
                    dialog_ok(config.get_localized_string(60362), motivo, item.url)
            else:
                dialog_ok(config.get_localized_string(60362), config.get_localized_string(60363),
                          config.get_localized_string(60364), item.url)

            if item.channel == "favorites":
                # "Quitar de favoritos"
                opciones.append(config.get_localized_string(30154))

            if len(opciones) == 0:
                error = True

    return opciones, video_urls, seleccion, error


def set_opcion(item, seleccion, opciones, video_urls):
    logger.info()
    # logger.debug(item.tostring('\n'))
    salir = False
    # No ha elegido nada, lo más probable porque haya dado al ESC

    if seleccion == -1:
        # Para evitar el error "Uno o más elementos fallaron" al cancelar la selección desde fichero strm
        listitem = xbmcgui.ListItem(item.title)

        if config.get_platform(True)['num_version'] >= 16.0:
            listitem.setArt({'icon': "DefaultVideo.png", 'thumb': item.thumbnail})
        else:
            listitem.setIconImage("DefaultVideo.png")
            listitem.setThumbnailImage(item.thumbnail)

        xbmcplugin.setResolvedUrl(PLUGIN_HANDLE, False, listitem)

    # "Descargar"
    elif config.get_localized_string(30153) in opciones[seleccion]:
        from channels import downloads
        if item.contentType == "list" or item.contentType == "tvshow":
            item.contentType = "video"
        item.play_menu = True
        # item.from_action = 'play'
        item.from_channel = item.channel
        # item.video_urls = video_urls
        downloads.save_download(item)
        salir = True

    # "Quitar de favoritos"
    elif opciones[seleccion] == config.get_localized_string(30154):
        from channels import favorites
        favorites.delFavourite(item)
        salir = True

    # "Añadir a favoritos":
    elif opciones[seleccion] == config.get_localized_string(30155):
        from channels import favorites
        item.from_channel = "favorites"
        favorites.addFavourite(item)
        salir = True

    # "Buscar Trailer":
    elif opciones[seleccion] == config.get_localized_string(30162):
        config.set_setting("subtitulo", False)
        xbmc.executebuiltin("RunPlugin(%s?%s)" %
                            (sys.argv[0], item.clone(channel="trailertools", action="buscartrailer",
                                                     contextual=True).tourl()))
        salir = True

    return salir


def get_video_seleccionado(item, seleccion, video_urls):
    logger.info()
    mediaurl = ""
    view = False
    wait_time = 0
    mpd = False

    # Ha elegido uno de los vídeos
    if seleccion < len(video_urls):
        mediaurl = video_urls[seleccion][1]
        if len(video_urls[seleccion]) > 4:
            wait_time = video_urls[seleccion][2]
            if not item.subtitle:
                item.subtitle = video_urls[seleccion][3]
            mpd = True
        elif len(video_urls[seleccion]) > 3:
            wait_time = video_urls[seleccion][2]
            if not item.subtitle:
                item.subtitle = video_urls[seleccion][3]
        elif len(video_urls[seleccion]) > 2:
            wait_time = video_urls[seleccion][2]
        view = True

    # Si no hay mediaurl es porque el vídeo no está :)
    logger.info("mediaurl=" + mediaurl)
    if mediaurl == "":
        if item.server == "unknown":
            alert_unsopported_server()
        else:
            alert_no_disponible_server(item.server)

    # Si hay un tiempo de espera (como en megaupload), lo impone ahora
    if wait_time > 0:
        continuar = handle_wait(wait_time, item.server, config.get_localized_string(60365))
        if not continuar:
            mediaurl = ""

    return mediaurl, view, mpd


def set_player(item, xlistitem, mediaurl, view, strm, autoplay):
    logger.info()
    logger.debug("item:\n" + item.tostring('\n'))
    # Movido del conector "torrent" aqui
    if item.server == "torrent":
        play_torrent(item, xlistitem, mediaurl)
        return

    # Si es un fichero strm no hace falta el play
    elif strm:
        xbmcplugin.setResolvedUrl(PLUGIN_HANDLE, True, xlistitem)
        if item.subtitle != "":
            xbmc.sleep(2000)
            xbmc_player.setSubtitles(item.subtitle)

    else:
        logger.info("player_mode=%s" % config.get_setting("player_mode", default=0))
        logger.info("mediaurl=" + mediaurl)
        if config.get_setting("player_mode", default=0) == 3 or "megacrypter.com" in mediaurl:
            from . import download_and_play
            download_and_play.download_and_play(mediaurl, "download_and_play.tmp", config.get_setting("downloadpath", default=''))
            return

        elif config.get_setting("player_mode", default=0) == 0 or \
                (config.get_setting("player_mode", default=0) == 3 and mediaurl.startswith("rtmp")):
            # Añadimos el listitem a una lista de reproducción (playlist)
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()
            playlist.add(mediaurl, xlistitem)

            # Reproduce
            # xbmc_player = xbmc_player
            xbmc_player.play(playlist, xlistitem)
            if config.get_setting('trakt_sync'):
                from core import trakt_tools
                trakt_tools.wait_for_update_trakt()

        # elif config.get_setting("player_mode", default=0) == 1 or item.isPlayable:
        elif config.get_setting("player_mode", default=0) == 1:
            logger.info("Tras setResolvedUrl")
            # si es un archivo de la videoteca enviar a marcar como visto

            if strm or item.strm_path or item.video_path:
                from platformcode import xbmc_videolibrary
                xbmc_videolibrary.mark_auto_as_watched(item)
            # logger.debug(item)
            xlistitem.setPath(mediaurl)
            xbmcplugin.setResolvedUrl(PLUGIN_HANDLE, True, xlistitem)
            xbmc.sleep(2500)

        elif config.get_setting("player_mode", default=0) == 2:
            xbmc.executebuiltin("PlayMedia(" + mediaurl + ")")

    # TODO MIRAR DE QUITAR VIEW
    if item.subtitle != "" and view:
        logger.info("Subtítulos externos: " + item.subtitle)
        xbmc.sleep(2000)
        xbmc_player.setSubtitles(item.subtitle)

    # si es un archivo de la videoteca enviar a marcar como visto
    if strm or item.strm_path or item.video_path:
        from platformcode import xbmc_videolibrary
        xbmc_videolibrary.mark_auto_as_watched(item)

    from threading import Thread
    Thread(target=freq_count, args=[item]).start()


def freq_count(item):
    if is_playing():
        xbmc.sleep(2000)
        if is_playing():
            if not PY3:
                from lib import alfaresolver
            else:
                from lib import alfaresolver_py3 as alfaresolver
            alfaresolver.frequency_count(item)


def torrent_client_installed(show_tuple=False):
    # Plugins externos se encuentra en servers/torrent.json nodo clients
    from core import filetools

    torrent_clients = jsontools.get_node_from_file("torrent.json", "clients", filetools.join(config.get_runtime_path(),
                                                                                             "servers"), display=False)
    torrent_options = []
    for client in torrent_clients:
        if xbmc.getCondVisibility('System.HasAddon("%s")' % client["id"]):
            try:
                __settings__ = xbmcaddon.Addon(id="%s" % client["id"])
            except:
                continue

            if show_tuple:
                torrent_options.append([config.get_localized_string(60366) % client["name"], client["url"]])
            else:
                torrent_options.append(config.get_localized_string(60366) % client["name"])

    return torrent_options


def play_torrent(item, xlistitem, mediaurl):
    logger.info()
    import traceback
    import threading

    from core import filetools
    from core import httptools
    from lib.generictools import get_torrent_size, verify_channel
    from servers.torrent import torrent_dirs, update_control, shorten_rar_path, get_tclient_data, call_torrent_via_web

    # Opciones disponibles para Reproducir torrents
    torrent_options = list()
    torrent_options.append(["Cliente interno (necesario libtorrent) BT"])
    torrent_options.append(["Cliente interno MCT (necesario libtorrent)"])

    torrent_options.extend(torrent_client_installed(show_tuple=True))

    torrent_client = config.get_setting("torrent_client", server="torrent", default=0)
    if torrent_client > len(torrent_options): torrent_client = 0

    if torrent_client and torrent_client - 1 <= len(torrent_options):
        if torrent_client == 0 and not scrapertools.find_single_match(item.downloadFilename, '^\:(\w+)\:'):
            seleccion = dialog_select(config.get_localized_string(70193), [opcion[0] for opcion in torrent_options])
        elif torrent_client == 0 and scrapertools.find_single_match(item.downloadFilename, '^\:(\w+)\:'):
            t_client_dnl = scrapertools.find_single_match(item.downloadFilename, '^\:(\w+)\:').upper()
            for x, t_client in enumerate(torrent_options):
                if t_client_dnl in t_client[0].upper():
                    seleccion = x
                    break
            else:
                seleccion = 0
        else:
            seleccion = torrent_client - 1
    else:
        if len(torrent_options) > 1 and not scrapertools.find_single_match(item.downloadFilename, '^\:(\w+)\:'):
            seleccion = dialog_select(config.get_localized_string(70193), [opcion[0] for opcion in torrent_options])
        elif scrapertools.find_single_match(item.downloadFilename, '^\:(\w+)\:'):
            t_client_dnl = scrapertools.find_single_match(item.downloadFilename, '^\:(\w+)\:').upper()
            for x, t_client in enumerate(torrent_options):
                if t_client_dnl in t_client[0].upper():
                    seleccion = x
                    break
            else:
                seleccion = 0
        else:
            seleccion = 0

    # Si Libtorrent ha dado error de inicialización, no se pueden usar los clientes internos
    TORREST_advise = config.get_setting("torrest_advise", server="torrent", default=False)
    UNRAR = config.get_setting("unrar_path", server="torrent", default="")
    LIBTORRENT = config.get_setting("libtorrent_path", server="torrent", default='')
    LIBTORRENT_in_use_local = False
    LIBTORRENT_version = config.get_setting("libtorrent_version", server="torrent", default=1)
    try:
        LIBTORRENT_version = int(scrapertools.find_single_match(LIBTORRENT_version, '\/(\d+)\.\d+\.\d+'))
    except:
        LIBTORRENT_version = 1
    RAR_UNPACK = config.get_setting("mct_rar_unpack", server="torrent", default='')
    BACKGROUND_DOWNLOAD = config.get_setting("mct_background_download", server="torrent", default='')
    subtitle_path = config.get_kodi_setting("subtitles.custompath")
    subtitles_list = []
    size_rar = 2
    rar_files = []
    rar_control = {}
    rar_path = ''
    add_url = mediaurl
    downloadProgress = 1
    if item.password:
        size_rar = 3
    if item.contentType == 'movie':
        folder = config.get_setting("folder_movies", default='')  # películas
    else:
        folder = config.get_setting("folder_tvshows", default='')  # o series
    download_path = config.get_setting('downloadpath', default='')  # Obtenemos el path absoluto a partir de Downloads
    videolibrary_path = config.get_videolibrary_path()  # Obtenemos el path absoluto a partir de la Videoteca
    PATH_videos = filetools.join(videolibrary_path, folder)
    DOWNLOAD_LIST_PATH = config.get_setting("downloadlistpath", default='')
    timeout = 10

    torrent_params = {
                      'url': item.url,
                      'torrents_path': None, 
                      'local_torr': item.torrents_path or 'play_torrent', 
                      'lookup': False if item.downloadStatus not in [4] else True, 
                      'force': False, 
                      'data_torrent': False, 
                      'subtitles': True, 
                      'file_list': True
                      }

    torrent_paths = torrent_dirs()
    torr_client = scrapertools.find_single_match(torrent_options[seleccion][0], ':\s*(\w+)').lower()
    # Descarga de torrents a local
    if 'interno (necesario' in torrent_options[seleccion][0]:
        torr_client = 'BT'
    elif 'MCT' in torrent_options[seleccion][0]:
        torr_client = 'MCT'
    else:
        torr_client = scrapertools.find_single_match(torrent_options[seleccion][0], ':\s*(\w+)').lower()
    torrent_port = torrent_paths.get(torr_client.upper() + '_port', 0)
    torrent_web = torrent_paths.get(torr_client.upper() + '_web', '')
    if not item.url_control:
        item.url_control = item.url.replace(PATH_videos, '')
    torr_client_alt = []
    for i, alt_client in enumerate(torrent_options):
        if scrapertools.find_single_match(str(alt_client), ':\s*(\w+)').lower() in ['torrest', 'quasar']:
            torr_client_alt += [(scrapertools.find_single_match(str(alt_client), ':\s*(\w+)').lower(), i)]
    if LIBTORRENT: torr_client_alt += [('BT', 0)]
    torr_client_alt = sorted(torr_client_alt, reverse=True)

    if not TORREST_advise and not 'torrest' in str(torr_client_alt) and torrent_paths.get('ELEMENTUM', '') != 'Memory':
        msg1 = 'Con la evolución a [B]Kodi 19[/B] los [B]clientes de torrent Internos[/B] han dejado de funcionar casi totalmente.  '
        msg2 = 'Los gestores externos [B]Quasar y Elementum[/B] están sin o casi sin mantenimiento.  [B]Alfa recomienda el uso de [COLOR gold]TORREST[/B][/COLOR].  '
        msg3 = 'Lee este artículo (también desde el [B]Menú de Alfa[/B]) e infórmate de sus ventajas e instalación: [COLOR yellow]https://alfa-addon.com/threads/ torrest-el-gestor-de-torrents-definitivo.4085/[/COLOR]'
        config.set_setting("torrest_advise", True, server="torrent")
        dialog_ok('Alfa te recomienda [COLOR gold]TORREST[/COLOR]', msg1, msg2, msg3)

    # Si es Libtorrent y no está soportado, se ofrecen alternativas, si las hay...
    if seleccion < 2 and not LIBTORRENT:
        dialog_ok('Cliente Interno (LibTorrent):', 'Este gestor no está soportado en su dispositivo.', \
                  'Error: [COLOR yellow]%s[/COLOR]' % config.get_setting("libtorrent_error", server="torrent",
                                                                         default=''), \
                  '[COLOR hotpink]Alfa le recomienda el uso de [B]TORREST[/B][/COLOR]')
        if len(torrent_options) > 2:
            seleccion = dialog_select(config.get_localized_string(70193), [opcion[0] for opcion in torrent_options])
            if seleccion < 2:
                return
            torr_client = scrapertools.find_single_match(torrent_options[seleccion][0], ':\s*(\w+)').lower()
        else:
            item.downloadProgress = 100
            update_control(item, function='play_torrent_no_libtorrent')
            return
    # Si hay RAR y es Torrenter o Elementum con opción de Memoria, se ofrece la posibilidad ee otro Gestor temporalemente
    elif seleccion > 1 and torr_client_alt and UNRAR and 'RAR-' in item.torrent_info and (
            torr_client not in ['BT', 'MCT', 'quasar', 'elementum', 'torrest'] \
            or torrent_paths.get('ELEMENTUM', '') == 'Memory'):

        if dialog_yesno(torr_client, 'Este plugin externo no soporta extraer on-line archivos RAR', \
                        '[COLOR yellow]¿Quiere que usemos esta vez el gestor [B]%s[/B]?[/COLOR]' % torr_client_alt[0][
                            0].upper(), \
                        'Esta operación ocupará en disco [COLOR yellow][B]%s+[/B][/COLOR] veces el tamaño del vídeo' % size_rar):
            seleccion = torr_client_alt[0][1]
            torr_client = torr_client_alt[0][0]
        else:
            item.downloadProgress = 100
            update_control(item, function='play_torrent_no_rar')
            return
    # Si hay RAR y es Elementum, pero con opción de Memoria, se muestras los Ajustes de Elementum y se pide al usuario que cambie a "Usar Archivos"
    elif seleccion > 1 and not torr_client_alt and UNRAR and 'RAR-' in item.torrent_info and "elementum" in \
            torr_client and torrent_paths.get('ELEMENTUM', '') == 'Memory':
        if dialog_yesno(torr_client,
                        'Elementum con descarga en [COLOR yellow]Memoria[/COLOR] no soporta ' + \
                        'extraer on-line archivos RAR (ocupación en disco [COLOR yellow][B]%s+[/B][/COLOR] veces)' % size_rar, \
                        '[COLOR yellow]¿Quiere llamar a los Ajustes de Elementum para cambiar [B]temporalmente[/B] ' + \
                        'a [COLOR hotpink]"Usar Archivos"[/COLOR] y [B]reintentarlo[/B]?[/COLOR]'):
            __settings__ = xbmcaddon.Addon(id="plugin.video.%s" % torr_client)
            __settings__.openSettings()  # Se visulizan los Ajustes de Elementum
            elementum_dl = xbmcaddon.Addon(id="plugin.video.%s" % torr_client).getSetting('download_storage')
            if elementum_dl != '1':
                config.set_setting("elementum_dl", "1", server="torrent")  # Salvamos el cambio para restaurarlo luego
        else:
            item.downloadProgress = 100
            update_control(item, function='play_torrent_elementum_mem')
        return  # Se sale, porque habrá refresco y cancelaría Kodi si no

    if seleccion >= 0:

        #### Compatibilidad con Kodi 18: evita cuelgues/cancelaciones cuando el .torrent se lanza desde pantalla convencional
        # if xbmc.getCondVisibility('Window.IsMedia'):
        try:
            xbmcplugin.setResolvedUrl(PLUGIN_HANDLE, False,
                                      xlistitem)  # Preparamos el entorno para evitar error Kod1 18
            time.sleep(1)       # Dejamos tiempo para que se ejecute
        except:
            pass

        # Nuevo método de descarga previa del .torrent.  Si da error, miramos si hay alternatica local.
        # Si el .torrent ya es local, lo usamos
        url = ''
        url_local = False
        if torrent_params.get('torrent_alt', ''):
            item.torrent_alt = torrent_params['torrent_alt']
        if item.torrents_path and filetools.exists(item.torrents_path):
            item.url = item.torrents_path  # Usamos el .torrent cacheado
            url_local = True
        elif '\\' in item.url or item.url.startswith("/") or item.url.startswith("magnet:"):
            if videolibrary_path not in item.url and download_path not in item.url \
                                 and torrent_paths[torr_client.upper() + '_torrents'] \
                                 not in item.url and not item.url.startswith("magnet:"):
                item.url = filetools.join(videolibrary_path, folder, item.url)
            if item.url.startswith("magnet:"):
                url_local = True
            else:
                url_local = filetools.exists(item.url)
            if not url_local:
                if item.url_control:  # Se mira si es una descarga reiniciada en frio
                    item.url = item.url_control  # ... se restaura la url original
                elif item.torrent_alt:  # Si hay error, se busca un .torrent alternativo
                    item.url = item.torrent_alt  # El .torrent alternativo puede estar en una url o en local
                if ('\\' in item.url or item.url.startswith("/") or item.url.startswith("magnet:")) \
                                     and videolibrary_path not in item.url and download_path not in item.url \
                                     and torrent_paths[torr_client.upper() + '_torrents'] \
                                     not in item.url and not item.url.startswith("magnet:"):
                    item.url = filetools.join(videolibrary_path, folder, item.url)
                    url_local = filetools.exists(item.url)

        url_stat = False
        torrents_path = ''
        referer = None
        post = None
        size = ''
        password = ''
        if item.password:
            password = item.password

        if scrapertools.find_single_match(videolibrary_path,
                                            '(^\w+:\/\/)'):  # Si es una conexión REMOTA, usamos userdata local
            videolibrary_path = config.get_data_path()  # Obtenemos el path absoluto a partir de Userdata
        if not filetools.exists(videolibrary_path):  # Si no existe el path, pasamos al modo clásico
            videolibrary_path = False
        else:
            torrents_path = filetools.join(videolibrary_path, 'temp_torrents_Alfa', \
                                           'cliente_torrent_Alfa.torrent')  # path descarga temporal
        if not videolibrary_path or not filetools.exists(filetools.join(videolibrary_path, \
                                                                        'temp_torrents_Alfa')):  # Si no existe la carpeta temporal, la creamos
            filetools.mkdir(filetools.join(videolibrary_path, 'temp_torrents_Alfa'))

        # Si hay headers, se pasan a la petición de descarga del .torrent
        headers = {}
        if item.headers:
            headers = item.headers

        # identificamos si es una url o un path de archivo
        if not url_local and not url_stat:
            if item.torrent_alt:
                timeout = 5
            # Si es una llamada con POST, lo preparamos
            if item.referer: referer = item.referer
            if item.post: post = item.post
            # Descargamos el .torrent
            torrent_params['url'] = item.url
            if item.channel != 'downloads' and item.sub_action not in ['auto'] and item.torrents_path == 'CF_BLOCKED':
                torrent_params['torrents_path'] = item.torrents_path
            torrent_params = get_torrent_size(item.url, torrent_params=torrent_params, 
                                              referer=referer, post=post, timeout=timeout, 
                                              headers=headers, retry_404=0 if item.torrent_alt else 1,
                                              item=item)
            size = torrent_params['size']
            url = torrent_params['url'] if not filetools.isfile(torrent_params['torrents_path']) else torrent_params['torrents_path']
            torrent_f = torrent_params['torrent_f']
            rar_files = torrent_params['files']
            subtitles_list = torrent_params['subtitles_list']
            if filetools.isfile(torrent_params['torrents_path']) and filetools.exists(torrent_params['torrents_path']):
                url_local = True
                item.torrents_path = torrent_params['torrents_path']
                item.torrent_info = size

            if subtitles_list: log("##### Subtítulos encontrados en el torrent: %s" % str(subtitles_list))
            if not item.subtitle and subtitles_list:
                item.subtitle = subtitles_list[0]
            if url:
                url_stat = True
                item.url = url
                url_local = filetools.exists(item.url)
                if "torrentin" in torr_client:
                    item.url = 'file://' + item.url

        if (not url or 'ERROR' in size) and not url_local and item.torrent_alt:  # Si hay error, se busca un .torrent alternativo
            item.url = item.torrent_alt  # El .torrent alternativo puede estar en una url o en local

        if not url_local and videolibrary_path and not videolibrary_path in item.url and \
                not download_path in item.url and \
                not torrent_paths[torr_client.upper() + '_torrents'] in item.url and \
                not 'http' in item.url and not item.url.startswith("magnet:"):
            item.url = filetools.join(videolibrary_path, folder, item.url)
            url_local = filetools.exists(item.url)

        # Si es un archivo .torrent local, actualizamos el path relativo a path absoluto
        if (url_local and not url_stat and videolibrary_path) \
                      or ('ERROR' in size and not url_local and videolibrary_path \
                      and item.channel == 'videolibrary'):  # .torrent alternativo local
            if not filetools.exists(torrent_params['local_torr']) \
                    and filetools.copy(item.url, torrents_path, silent=True):  # se copia a la carpeta generíca para evitar problemas de encode
                item.url = torrents_path

            if not item.subtitle:
                subtitles_list_vl = []
                for subt in filetools.listdir(filetools.dirname(item.url)):
                    if subt.endswith('.srt'):
                        subtitles_list_vl += [filetools.join(filetools.dirname(item.url), subt)]
                        subtitles_list += [filetools.join(filetools.dirname(item.url), subt)]
                        # if subtitle_path:
                        #    filetools.copy(filetools.join(filetools.dirname(item.url), subt), filetools.join(subtitle_path, subt), silent=True)
                if subtitles_list_vl:
                    item.subtitle = filetools.dirname(item.url)

            torrent_params['file_list'] = True
            torrent_params['url'] = item.url
            torrent_params = get_torrent_size(item.url, torrent_params=torrent_params, 
                                              referer=referer, post=post, timeout=timeout, 
                                              headers=headers, retry_404=0 if item.torrent_alt else 1,
                                              item=item)
            size = torrent_params['size']
            url = torrent_params['url'] if not filetools.isfile(torrent_params['torrents_path']) else torrent_params['torrents_path']
            torrent_f = torrent_params['torrent_f']
            rar_files = torrent_params['files']
            subtitles_list = torrent_params['subtitles_list']
            if filetools.isfile(torrent_params['torrents_path']) and filetools.exists(torrent_params['torrents_path']):
                url_local = True
                item.torrents_path = torrent_params['torrents_path']
                item.torrent_info = size

            if url and url != item.url:
                filetools.remove(torrents_path, silent=True)
                item.url = url
            if "torrentin" in torrent_options[seleccion][0]:  # Si es Torrentin, hay que añadir un prefijo
                item.url = 'file://' + item.url

        if not item.torrent_info: item.torrent_info = size
        mediaurl = item.url

    if (('CF_BLOCKED' in size or 'CF_BLOCKED' in torrent_params['torrents_path'] \
                             or 'CF_BLOCKED' in item.torrents_path \
                             or '[B]BLOQUEO[/B]' in size) and item.downloadStatus in [4]) \
                             or 'ERROR_CF_BLOCKED' in torrent_params['torrents_path']:
        if item.downloadFilename:
            item.downloadStatus = 3
            item.downloadProgress = 0
            update_control(item, function='play_torrent_CF_BLOCKED')
        return
    
    if seleccion >= 0:
        if item.subtitle:
            from platformcode import subtitletools
            item = subtitletools.download_subtitles(item)
            if item.subtitle:
                if not filetools.exists(item.subtitle):
                    item.subtitle = filetools.join(videolibrary_path, folder, item.subtitle)
                log("##### 'Subtítulos externos: %s" % item.subtitle)
                time.sleep(1)
                xbmc_player.setSubtitles(item.subtitle)  # Activamos los subtítulos

        # Si no existe, creamos un archivo de control para que sea gestionado desde Descargas
        if torrent_paths.get(torr_client.upper(), ''):  # Es un cliente monitorizable?
            video_name = ''
            video_path = ''
            short_video_path = shorten_rar_path(item)

            if not item.downloadFilename:
                item.downloadStatus = 5
            item.contentAction = 'play'

            # Obtenermos el PATH y VIDEO_NAMES del .torrent
            if rar_files:
                for entry in rar_files:
                    for file, path in list(entry.items()):
                        if file == 'path':
                            if os.path.splitext(path[0])[1] in extensions_list:
                                video_name = path[0]
                        elif file == '__name':
                            video_path = path
                item.downloadFilename = filetools.join(':%s: ' % torr_client.upper(), video_path, video_name)

            # Si es un Magnet, componemos el path de descarga
            if item.url.startswith('magnet:'):
                t_hash = scrapertools.find_single_match(item.url, 'xt=urn:btih:([^\&]+)\&')
                video_name = torr_folder = scrapertools.find_single_match(item.downloadFilename,
                                                                            '(?:^\:\w+\:\s*)?[\\\|\/]?(.*?)$')
                if not video_name: video_name = urllib.unquote_plus(
                    scrapertools.find_single_match(item.url, '(?:\&|&amp;)dn=([^\&]+)\&'))
                if t_hash:
                    item.downloadServer = {"url": filetools.join(torrent_paths[torr_client.upper() + '_torrents'], \
                                                                 t_hash + '.torrent'), "server": item.server}
                    if torr_client in ['BT', 'MCT']:
                        filetools.write(item.downloadServer['url'], ' ')
                if video_name:
                    item.downloadFilename = ':%s: %s' % (torr_client.upper(), video_name)
                else:
                    item.downloadFilename = ':%s: %s' % (torr_client.upper(), item.url)

            # Si es una descarga de RAR y es un reintento de una descarga anterior, vemos desde dónde se puede recuperar
            if video_path:
                if not filetools.exists(filetools.join(torrent_paths[torr_client.upper()], video_path)) \
                        and filetools.exists(filetools.join(torrent_paths[torr_client.upper()], short_video_path)):
                    rar_control = jsontools.load(filetools.read(filetools.join(torrent_paths[torr_client.upper()], \
                                                                               short_video_path, '_rar_control.json')))
                    if rar_control and 'downloading' not in rar_control['status'] and rar_control['error'] <= 2:
                        item.downloadFilename = filetools.join(':%s: ' % torr_client.upper(), short_video_path,
                                                               video_name)
                        if 'path_control' in str(rar_control) and filetools.exists(filetools.join(DOWNLOAD_LIST_PATH, \
                                                                                                  rar_control[
                                                                                                      'path_control'])):
                            if item.path and item.path != rar_control['path_control']:
                                filetools.remove(filetools.join(DOWNLOAD_LIST_PATH, item.path))
                            item.path = rar_control['path_control']
                        update_control(item, function='play_torrent_rar_reintento')
                        try:
                            threading.Thread(target=rar_control_mng, args=(item, xlistitem, mediaurl, \
                                                                           rar_files, torr_client, password, size,
                                                                           rar_control)).start()  # Creamos un Thread independiente
                            time.sleep(3)  # Dejamos terminar la inicialización...
                        except:  # Si hay problemas de threading, salimos
                            logger.error(traceback.format_exc())
                        finally:
                            return

                    elif rar_control and 'downloading' not in rar_control['status'] and rar_control['error'] > 2:
                        # Si ha superado el numero de retries, borramos las sesiones y hacemos una nueva descarga
                        rar_control = []
                        if torr_client in ['quasar', 'elementum', 'torrest']:
                            torr_data, deamon_url, index = get_tclient_data(video_path, \
                                                                            torr_client, port=torrent_port,
                                                                            web=torrent_web, action='delete')
                        elif torr_client in ['BT', 'MCT'] and 'url' in str(item.downloadServer):
                            file_t = scrapertools.find_single_match(item.downloadServer['url'],
                                                                      '\w+\.torrent$').upper()
                            if file_t:
                                filetools.remove(
                                    filetools.join(torrent_paths[torr_client.upper() + '_torrents'], file_t))

            # Comprobamos si Libtorrent está en uso por otra descarga.  Si lo está, ponemos esta petición en cola
            if torr_client in ['BT', 'MCT']:
                if config.get_setting("LIBTORRENT_in_use", server="torrent", default=False):
                    LIBTORRENT_in_use_local = True
                    item.downloadQueued = 1
                    if item.downloadProgress != -1:
                        item.downloadProgress = 0
                    if item.downloadStatus == 5:
                        dialog_notification("LIBTORRENT en USO",
                                            "Descarga encolada.  Puedes seguir haciendo otras cosas...", time=10000)
                elif LIBTORRENT_version < 99:
                    config.set_setting("LIBTORRENT_in_use", True,
                                       server="torrent")  # Marcamos Libtorrent como en uso, si es antiguo

            item.torr_folder = video_path
            update_control(item, function='play_torrent_crear_control')

        # Si tiene .torrent válido o magnet, lo registramos
        if size or item.url.startswith('magnet:'):
            item_freq = item.clone()
            if not item_freq.downloadFilename:
                item_freq.downloadFilename = ':%s: ' % torr_client.upper()
            if item_freq.channel_recovery == 'url':
                item_freq.category = verify_channel(item_freq.category.lower())
            try:
                import threading
                if not PY3:
                    from lib import alfaresolver
                else:
                    from lib import alfaresolver_py3 as alfaresolver
                threading.Thread(target=alfaresolver.frequency_count, args=(item_freq,)).start()
            except:
                logger.error(traceback.format_exc(1))

        try:
            # Reproductor propio BT (libtorrent)
            if seleccion == 0:
                if not LIBTORRENT_in_use_local:
                    if item.downloadProgress == -1:  # Si estaba pausado se resume
                        item.downloadProgress = 1
                        downloadProgress = -1
                    update_control(item, function='play_torrent_BT_start')
                    itemlist_refresh()
                    from servers.torrent import bt_client
                    bt_client(mediaurl, xlistitem, rar_files, subtitle=item.subtitle, password=password,
                                      item=item)
                    config.set_setting("LIBTORRENT_in_use", False,
                                       server="torrent")  # Marcamos Libtorrent como disponible
                    config.set_setting("RESTART_DOWNLOADS", True, "downloads")  # Forzamos restart downloads
                    if item.downloadStatus not in [3, 4, 5]: itemlist_refresh()

            # Reproductor propio MCT (libtorrent)
            elif seleccion == 1:
                if not LIBTORRENT_in_use_local:
                    if item.downloadProgress == -1:  # Si estaba pausado se resume
                        item.downloadProgress = 1
                        downloadProgress = -1
                    update_control(item, function='play_torrent_MCT_start')
                    itemlist_refresh()
                    from platformcode import mct
                    mct.play(mediaurl, xlistitem, subtitle=item.subtitle, password=password, item=item)
                    config.set_setting("LIBTORRENT_in_use", False,
                                       server="torrent")  # Marcamos Libtorrent como disponible
                    config.set_setting("RESTART_DOWNLOADS", True, "downloads")  # Forzamos restart downloads
                    if item.downloadStatus not in [3, 4, 5]: itemlist_refresh()

            # Plugins externos
            else:
                from lib.alfa_assistant import is_alfa_installed
                if xbmc.getCondVisibility("system.platform.android") and torr_client in ['quasar'] \
                                and config.get_setting('assistant_binary', default=False) and not is_alfa_installed():
                    dialog_notification('Alfa Assistant es requerido', '%s lo requiere en esta versión de Android' \
                                        % torr_client.capitalize(), time=10000)
                    logger.error('Alfa Assistant es requerido. %s lo requiere en esta versión de Android' % torr_client.capitalize())
                mediaurl = urllib.quote_plus(item.url)
                # Llamada con más parámetros para completar el título
                if torr_client in ['quasar', 'elementum'] and item.infoLabels['tmdb_id']:
                    if item.contentType == 'episode' and "elementum" not in torr_client:
                        mediaurl += "&episode=%s&library=&season=%s&show=%s&tmdb=%s&type=episode" % (
                            item.infoLabels['episode'], item.infoLabels['season'], item.infoLabels['tmdb_id'],
                            item.infoLabels['tmdb_id'])
                    elif item.contentType == 'movie':
                        mediaurl += "&library=&tmdb=%s&type=movie" % (item.infoLabels['tmdb_id'])

                result = False
                # __settings__ = xbmcaddon.Addon(id="plugin.video.%s" % torr_client)  # Apunta settings del cliente torrent externo
                save_path_videos = str(config.translatePath(torrent_paths[torr_client.upper()]))

                if torr_client == 'quasar' and 'cliente_torrent_Alfa' not in item.url:  # Quasar no copia el .torrent
                    ret = filetools.copy(item.url, filetools.join(save_path_videos, 'torrents', \
                                                                  filetools.basename(item.url)), silent=True)

                if (torr_client in ['quasar', 'elementum', 'torrest'] and item.downloadFilename \
                    and (item.downloadStatus not in [5] or item.downloadProgress == -1 or item.url.startswith('magnet:'))) \
                        or (torr_client in ['quasar', 'elementum', 'torrest'] \
                            and ('RAR-' in size or 'RAR-' in item.torrent_info) and BACKGROUND_DOWNLOAD):

                    if item.downloadProgress == -1:  # Si estaba pausado se resume
                        torr_folder = scrapertools.find_single_match(item.downloadFilename,
                                                                       '(?:^\:\w+\:\s*)?[\\\|\/]?(.*?)$')
                        if torr_folder.startswith('\\') or torr_folder.startswith('/'):
                            torr_folder = torr_folder[1:]
                        if filetools.dirname(torr_folder):
                            torr_folder = filetools.dirname(torr_folder)
                        item.downloadProgress = 1
                        downloadProgress = -1
                        result, deamon_url, index = get_tclient_data(torr_folder, \
                                                                     torr_client, port=torrent_port,
                                                                     web=torrent_web, action='resume')
                    if not result:  # Si es nuevo, o hay error en resume, se añade
                        result = call_torrent_via_web(urllib.quote_plus(item.url), torr_client,
                                                      oper=item.downloadStatus)
                        downloadProgress = 1
                if not result:  # Si falla todo, se usa el antiguo sistema
                    if torr_client == 'torrest':
                        play_type = 'path'
                        if mediaurl.startswith('magnet'): play_type = 'magnet'
                        if mediaurl.startswith('http'): play_type = 'url'
                        xbmc.executebuiltin("PlayMedia(" + torrent_options[seleccion][1] % \
                                            (play_type, play_type, mediaurl) + ")")
                    else:
                        xbmc.executebuiltin("PlayMedia(" + torrent_options[seleccion][1] % mediaurl + ")")
                update_control(item, function='play_torrent_externos_start')
                if item.downloadStatus not in [3, 4, 5]: itemlist_refresh()

                # Si es un archivo RAR, monitorizamos el cliente Torrent hasta que haya descargado el archivo,
                # y después lo extraemos, incluso con RAR's anidados y con contraseña
                # rar_control_mng(item, xlistitem, mediaurl, rar_files, torr_client, password, size, rar_control)
                if downloadProgress != -1:
                    try:
                        threading.Thread(target=rar_control_mng, args=(item, xlistitem, mediaurl, \
                                                                       rar_files, torr_client, password, size,
                                                                       rar_control)).start()  # Creamos un Thread independiente por .torrent
                        time.sleep(3)  # Dejamos terminar la inicialización...
                    except:  # Si hay problemas de threading, salimos
                        logger.error(traceback.format_exc())

            # Si hay subtítulos, los copiamos a la carpeta de descarga del torrent, para que esté junto al vídeo, por si hay repro fuera de Alfa
            for entry in rar_files:
                for file, path in list(entry.items()):
                    if file == '__name':
                        rar_path = path
                        rar_path = filetools.join(torrent_paths[torr_client.upper()], rar_path)
                        for x in range(60):
                            if filetools.exists(rar_path):
                                break
                            time.sleep(1)
                        else:
                            rar_path = ''
                        break
            if subtitles_list and rar_path:
                for subtitle in subtitles_list:
                    if filetools.exists(subtitle):
                        filetools.copy(subtitle, filetools.join(rar_path, filetools.basename(subtitle)))
                log("##### Subtítulos copiados junto a vídeo: %s" % str(subtitles_list))
            if item.subtitle and filetools.isfile(item.subtitle) and rar_path:
                rar_path_folder = rar_path if filetools.isdir(rar_path) else filetools.dirname(rar_path)
                dest_file = filetools.join(rar_path_folder, filetools.basename(item.subtitle))
                filetools.copy(item.subtitle, dest_file, silent=True)
                log("##### Subtítulo copiado junto a vídeo: %s" % str(dest_file))

        except Exception as e:
            config.set_setting("LIBTORRENT_in_use", False, server="torrent")  # Marcamos Libtorrent como disponible
            logger.error(traceback.format_exc())
            dialog_ok('Error descargando .torrent', line1='Inténtelo de nuevo más tarde ... ',
                      line2='[COLOR yellow][B]%s[/B][/COLOR]' % str(e))


def rar_control_mng(item, xlistitem, mediaurl, rar_files, torr_client, password, size, rar_control={}):
    logger.info('%s: %s' % (torr_client, mediaurl))

    import time
    import traceback

    from core import filetools
    from core import httptools
    from servers.torrent import torrent_dirs, wait_for_download, extract_files, update_control, mark_auto_as_watched, get_tclient_data

    try:
        torrent_paths = torrent_dirs()
        rar = False
        video_path = ''

        # Si es un archivo RAR, monitorizamos el cliente Torrent hasta que haya descargado el archivo,
        # y después lo extraemos, incluso con RAR's anidados y con contraseña
        if torrent_paths[torr_client.upper()] != 'Memory':
            rar_file, save_path_videos, torr_folder, rar_control = wait_for_download(item, xlistitem, mediaurl,
                                                                                     rar_files, torr_client,
                                                                                     password, size,
                                                                                     rar_control)  # Esperamos mientras se descarga el TORRENT
        else:
            save_path_videos = 'Memory'
        if 'size' in str(rar_control) and rar_control['size']:
            size = rar_control['size']

        UNRAR = torrent_paths['TORR_unrar_path']
        RAR_UNPACK = torrent_paths['TORR_rar_unpack']
        # if 'RAR-' in size and torr_client in ['quasar', 'elementum', 'torrest'] and UNRAR:
        if 'RAR-' in size and UNRAR and RAR_UNPACK and rar_file and save_path_videos:  # Si se ha descargado RAR...
            dp = dialog_progress_bg('Alfa %s' % torr_client)
            video_file, rar, video_path, erase_file_path = extract_files(rar_file, \
                                                                         save_path_videos, password, dp, item,
                                                                         torr_client, \
                                                                         rar_control, size,
                                                                         mediaurl)  # ... extraemos el vídeo del RAR
            dp.close()

            # Reproducimos el vídeo extraido, si no hay nada en reproducción
            while is_playing() and rar and (not item.downloadFilename or item.downloadStatus == 5):
                time.sleep(3)  # Repetimos cada intervalo
            if rar and (not item.downloadFilename or item.downloadStatus == 5):
                time.sleep(1)
                video_play = filetools.join(video_path, video_file)
                log("##### video_play: %s" % video_play)
                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                playlist.clear()
                playlist.add(video_play, xlistitem)
                xbmc_player.play(playlist)

            if video_path:
                item.downloadFilename = video_path.replace(save_path_videos, '')
                item.downloadFilename = filetools.join(item.downloadFilename, video_file)
                item.downloadFilename = ':%s: %s' % (torr_client.upper(), item.downloadFilename)

        path = filetools.join(config.get_setting("downloadlistpath", default=''), item.path)
        if filetools.exists(path):
            item_down = Item().fromjson(filetools.read(path))
        else:
            item_down = item.clone()
            path = ''
        if not save_path_videos and item_down.downloadStatus > 0: item_down.downloadStatus = 3      # Descarga en error

        if item_down.downloadProgress == -1:
            item.downloadProgress = -1
        elif video_path and save_path_videos and item_down.downloadProgress > 0:
            item.downloadProgress = 100
        elif not video_path and item_down.downloadProgress == 99:
            item.downloadProgress = 99
        else:
            if torrent_paths[torr_client.upper() + '_web']:  # Es un cliente monitorizable?
                if path:
                    item.downloadProgress = item_down.downloadProgress  # Si se ha borrado desde downloads, prevalece su status
                    item.downloadStatus = item_down.downloadStatus  # Si se ha borrado desde downloads, prevalece su status
                else:
                    item.downloadProgress = 1  # lo dejamos preparado para el reinicio, o borrado auto
            else:
                item.downloadProgress = 100  # ... si no, se da por terminada la monitorización
        item.downloadQueued = 0
        update_control(item, function='rar_control_mng')
        config.set_setting("RESTART_DOWNLOADS", True, "downloads")  # Forzamos restart downloads
        if item.downloadStatus not in [3, 4, 5]: itemlist_refresh()

        # Seleccionamos que clientes torrent soportamos para el marcado de vídeos vistos: asumimos que todos funcionan
        if not item.downloadFilename or item.downloadStatus == 5:
            mark_auto_as_watched(item)

            # Si se ha extraido un RAR, se pregunta para borrar los archivos después de reproducir el vídeo (plugins externos)
            while is_playing() and rar:
                time.sleep(3)  # Repetimos cada intervalo
            if rar:
                if dialog_yesno('Alfa %s' % torr_client, '¿Borrar las descargas del RAR y Vídeo?'):
                    log("##### erase_file_path: %s" % erase_file_path)
                    try:
                        torr_data, deamon_url, index = get_tclient_data(torr_folder, \
                                                                        torr_client, port=torrent_paths.get(
                                                                        torr_client.upper() + '_port', 0), \
                                                                        web=torrent_paths.get(
                                                                        torr_client.upper() + '_web', ''),
                                                                        action='delete', \
                                                                        folder_new=erase_file_path)
                    except:
                        logger.error(traceback.format_exc(1))

        elementum_dl = config.get_setting("elementum_dl", server="torrent",
                                          default='')  # Si salvamos el cambio de Elementum
        if elementum_dl:
            config.set_setting("elementum_dl", "", server="torrent")  # lo reseteamos en Alfa
            xbmcaddon.Addon(id="plugin.video.%s" % torr_client) \
                .setSetting('download_storage', elementum_dl)  # y lo reseteamos en Elementum

    except:
        logger.error(traceback.format_exc())


def log(texto):
    logger.info(texto, force=True)
