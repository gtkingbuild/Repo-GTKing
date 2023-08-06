# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# XBMC Launcher (xbmc / kodi)
# ------------------------------------------------------------

#from future import standard_library
#standard_library.install_aliases()
#from builtins import str
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.error as urllib2                              # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib2                                              # Usamos el nativo de PY2 que es más rápido

import os
import sys
import time

from core.item import Item
from platformcode import config, logger
from platformcode import platformtools
from platformcode.logger import WebErrorException


def start():
    """ Primera funcion que se ejecuta al entrar en el plugin.
    Dentro de esta funcion deberian ir todas las llamadas a las
    funciones que deseamos que se ejecuten nada mas abrir el plugin.
    """
    logger.info()
    # if config.get_platform(True)['num_version'] >= 19:
    #     from core import filetools
    #     origin = filetools.join(config.get_runtime_path(), "resources", "settings_matrix.xml")
    #     destination = filetools.join(config.get_runtime_path(), "resources", "settings.xml")
    #     if filetools.exists(origin):
    #         filetools.move(origin, destination, silent=True)
    #config.set_setting('show_once', True)
    # Test if all the required directories are created
    #config.verify_directories_created()
    

def load_item():
    from modules import side_menu
    from platformcode import configurator

    # Extract item from sys.argv
    if sys.argv[2]:
        sp = sys.argv[2].split('&')
        url = sp[0]
        item = Item().fromurl(url)
        if len(sp) > 1:
            for e in sp[1:]:
                key, val = e.split('=')
                item.__setattr__(key, val)

    # If no item, this is mainlist
    else:
        if config.get_setting("start_page"):

            if not config.get_setting("custom_start"):

                category = config.get_setting("category")

                if isinstance(category, int):
                    category = config.get_localized_string(config.get_setting("category")).lower()

                item = Item(module="news", action="news", news=category.lower(), startpage=True)
            else:
                item = Item()
                item = side_menu.check_user_home(item)
                item.startpage = True
        else:
            item = Item(module="channelselector", action="getmainlist", viewmode="movie")
    
    if not config.get_setting('show_once'):
        if config.verify_settings_integrity() and not config.get_setting('show_once'):
            configurator.show_window()

    return item

def monkey_patch_modules(item):
    content_modules = [
        "community",
        "downloads",
        "info_popup",
        "news",
        "search",
        "tvmoviedb",
        "videolibrary",
    ]
    
    modules = list(content_modules)
    modules.extend([
        'alfavorites',
        'autoplay',
        'favorites',
        'filtertools',
        'help',
        'infoplus',
        'nextep',
        'renumbertools',
        'report',
        'setting',
        'side_menu',
        'trailertools',
        'url',
        'youtube_channel',
    ])

    if item.channel in modules:
        item.module = item.module or item.channel

    if item.module:
        if not item.channel:
            item.channel = item.module

        if item.module in content_modules:
            item.moduleContent = True

    return item


def run(item=None):
    from channels import downloads
    import channelselector

    logger.info()

    itemlist = None

    if not item:
        item = load_item()

    logger.info(item.tostring())

    # If item has no action, stops here
    if item.action == "":
        logger.info("Item sin accion")
        return

    # Cleans infoLabels["playcount"] if set by generictools
    if item.video_path:
        item.infoLabels["playcount"] = 1
        del item.infoLabels["playcount"]
    
    item = monkey_patch_modules(item)

    try:
        if not config.get_setting('tmdb_active'):
            config.set_setting('tmdb_active', True)

        # Special action for playing a video from the library
        if item.action == "play_from_library":
            play_from_library(item)

        elif item.action == "keymap":
            from platformcode import keymaptools
            if item.open:
                return keymaptools.open_shortcut_menu()
            else:
                return keymaptools.set_key()

        elif item.action == "script":
            from core import tmdb
            if tmdb.drop_bd():
                platformtools.dialog_notification(config.get_localized_string(20000), config.get_localized_string(60011), time=2000, sound=False)

        elif item.channel == 'channelselector':

            # Action for addon install on channelselector
            if item.action == "install_alfa":
                channelselector.install_alfa()

            else:
                # Action for main menu in channelselector
                if item.action == "getmainlist":
                    itemlist = channelselector.getmainlist()

                # Action for channel types on channelselector: movies, series, etc.
                elif item.action == "getchanneltypes":
                    itemlist = channelselector.getchanneltypes()

                # Action for channel listing on channelselector
                elif item.action == "filterchannels":
                    itemlist = channelselector.filterchannels(item.channel_type)


        elif item.action == "function":
            """
            {
                "action": "function",
                "folder": "lib",
                "function": "alfa_assistant",
                "method": "install_alfa_assistant",
                "options": "auto"
            }
            """
            # Checks if function file exists
            function_file = os.path.join(config.get_runtime_path(),
                                        item.folder, item.function + ".py")
            logger.info("function_file=%s" % function_file)

            function = None

            if os.path.exists(function_file):
                try:
                    function = __import__('%s.%s' % (item.folder, item.function), None,
                                         None, ["%s.%s" % (item.folder, item.function)])
                except ImportError:
                    exec("import %s." + item.function + " as function")

                if function:
                    logger.info("Running function %s(%s) | %s" % (function.__name__, item.options, function.__file__))

                    getattr(function, item.method)(item.options)

                else:
                    logger.error('Function "%s(%s)" missing (%s: %s) or not imported: %s' \
                                  % (item.function, item.options, function_file, os.path.exists(function_file), function))

            else:
                logger.error('Function "%s(%s)" missing (%s: %s) or not imported: %s' \
                              % (item.function, item.options, function_file, os.path.exists(function_file), function))

        else:
            module = None

            if item.module:
                logger.info("item.module")
                module_type = {
                    "folder" : "modules",
                    "type" : "module",
                }
                
                module_file = os.path.join(
                    config.get_runtime_path(),
                    module_type["folder"],
                    item.module + ".py"
                )
                
                if not os.path.exists(module_file):
                    module_type["folder"] = "channels"

                if item.module == 'channelselector':
                    # channelselector.install_alfa()    # Action for addon install on channelselector
                    # channelselector.getmainlist()     # Action for main menu in channelselector
                    # channelselector.getchanneltypes() # Action for channel types on channelselector: movies, series, etc.

                    # Action for channel listing on channelselector
                    if item.action == "filterchannels":
                        itemlist = channelselector.filterchannels(item.channel_type)
                    else:
                        itemlist = getattr(channelselector, item.action)()

                elif item.module == "test" and item.contentChannel:
                    if item.parameters == "test_channel":
                        getattr(module, item.action)(item.contentChannel)

            else:
                logger.info("item.channel")
                module_type = {
                    "folder" : "channels",
                    "type" : "channel",
                }
                # Action in certain channel specified in "action" and "channel" parameters
                # Entry point for a channel is the "mainlist" action, so here we check parental control
                if item.action == "mainlist":
                    from core import channeltools
                    # Parental control
                    # If it is an adult channel, and user has configured pin, asks for it
                    if channeltools.is_adult(item.channel) and config.get_setting("adult_request_password"):
                        tecleado = platformtools.dialog_input("", config.get_localized_string(60334), True)
                        if tecleado is None or tecleado != config.get_setting("adult_password"):
                            return

            # This is wrong, but there's no way around this yet
            # TODO: Get rid of these "special files"
            if item.module != "channelselector":
                # Checks if channel exists
                module_name = item.channel if module_type["type"] == "channel" else item.module
                module_package = '%s.%s' % (module_type["folder"], module_name)
                module_file = os.path.join(config.get_runtime_path(),
                                            module_type["folder"], module_name + ".py")
                logger.info("%s_file=%s" % (module_type["type"], module_file))

                module = None

                if os.path.exists(module_file):
                    try:
                        module = __import__(module_package, None,
                                            None, [module_package])
                    except ImportError:
                        exec("import " + module_package + " as module")

                if module:
                    logger.info("Running %s | %s" % (module.__name__, module.__file__))
                else:
                    logger.error('%s "%s" missing (%s: %s) or not imported: %s' % \
                        (module_type["type"], module_name, module_file, os.path.exists(module_file), module))
                    return

            if item.channel == "test" and item.contentChannel:
                if item.parameters == "test_channel":
                    getattr(module, item.action)(item.contentChannel)
            
            # Calls redirection if Alfavorites findvideos, episodios, seasons
            if item.context and 'alfavorites' in str(item.context) \
                            and item.action in ['findvideos', 'episodios', 'seasons', 'play']:
                try:
                    from core.videolibrarytools import redirect_url
                    item = redirect_url(item)
                except Exception:
                    import traceback
                    logger.error(traceback.format_exc())
            
            # Special play action
            if item.action == "play":
                #define la info para trakt
                try:
                    from core import trakt_tools
                    trakt_tools.set_trakt_info(item)
                except Exception:
                    import traceback
                    logger.error(traceback.format_exc())

                logger.info("item.action=%s" % item.action.upper())
                # logger.debug("item_toPlay: " + "\n" + item.tostring('\n'))

                # First checks if channel has a "play" function
                if hasattr(module, 'play'):
                    logger.info("Executing channel 'play' method")
                    playlist = module.play(item)
                    b_favourite = item.isFavourite
                    # Play should return a list of playable URLS
                    if playlist and len(playlist) > 0 and isinstance(playlist[0], Item):
                        item = playlist[0]
                        if b_favourite:
                            item.isFavourite = True
                        platformtools.play_video(item)

                    # Permitir varias calidades desde play en el canal
                    elif playlist and len(playlist) > 0 and isinstance(playlist[0], list):
                        item.video_urls = playlist
                        platformtools.play_video(item)

                    # If not, shows user an error message
                    elif not playlist and isinstance(playlist, list):
                        platformtools.dialog_ok(config.get_localized_string(20000), config.get_localized_string(60339))

                # If player doesn't have a "play" function, the standard play from platformtools is used
                else:
                    logger.info("Executing core 'play' method")
                    platformtools.play_video(item)

            # Special action for findvideos, where the plugin looks for known urls
            elif item.action == "findvideos":
                from core import servertools
                # First checks if channel has a "findvideos" function
                if hasattr(module, 'findvideos'):
                    itemlist = getattr(module, item.action)(item)
                    itemlist = servertools.filter_servers(itemlist)

                # If not, uses the generic findvideos function
                else:
                    logger.info("No channel 'findvideos' method, "
                                "executing core method")
                    itemlist = servertools.find_video_items(item)

                if config.get_setting("max_links", "videolibrary") != 0:
                    itemlist = limit_itemlist(itemlist)

                from platformcode import subtitletools
                subtitletools.saveSubtitleName(item)

            # Special action for adding a movie to the library
            elif item.action == "add_pelicula_to_library":
                from core import videolibrarytools
                videolibrarytools.add_movie(item)

            # Special action for adding a serie to the library
            elif item.action == "add_serie_to_library":
                from core import videolibrarytools
                videolibrarytools.add_tvshow(item, module)
            
            # Special action for adding a season to the library
            elif item.action == "add_season_to_library":
                from core import videolibrarytools
                item.action = "add_serie_to_library"
                item.infoLabels['last_season_only'] = True
                videolibrarytools.add_tvshow(item, module)

            # Special action for downloading all episodes from a serie
            elif item.action == "download_all_episodes":
                from channels import downloads
                item.action = item.extra
                del item.extra
                downloads.save_download(item)

            # Special action for searching, first asks for the words then call the "search" function
            elif item.action == "search":
                logger.info("item.action=%s" % item.action.upper())
                from core import channeltools

                # last_search = ""
                # last_search_active = config.get_setting("last_search", "search")
                # if last_search_active:
                #     try:
                #         current_saved_searches_list = list(config.get_setting("saved_searches_list", "search"))
                #         last_search = current_saved_searches_list[0]
                #     except Exception:
                #         pass

                last_search = channeltools.get_channel_setting('Last_searched', 'search', '')

                tecleado = platformtools.dialog_input(last_search)

                if tecleado is not None:
                    if "http" not in tecleado:
                        channeltools.set_channel_setting('Last_searched', tecleado, 'search')
                    itemlist = module.search(item, tecleado)


            # For all other actions
            elif not itemlist:
                # This logic is not correct, should be fixed
                #  \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/
                logger.info("Executing '%s' method" % item.action)
                # Get itemlist from module.action
                if hasattr(module, item.action):
                    itemlist = getattr(module, item.action)(item)

                # Run the method from the contentChannel
                else:
                    module_file = os.path.join(config.get_runtime_path(),
                                                'channels', item.contentChannel + ".py")
                    module = None
                    if os.path.exists(module_file):
                        try:
                            module = __import__('channels.%s' % item.contentChannel, None,
                                                None, ["channels.%s" % item.contentChannel])
                        except ImportError:
                            exec("import channels." + item.contentChannel + " as channel")

                    if not module:
                        logger.error('Channel "%s" missing (%s: %s) or not imported: %s' \
                                    % (item.contentChannel, module_file, os.path.exists(module_file), module))

                    logger.info("Running channel %s | %s" % (module.__name__, module.__file__))
                    itemlist = getattr(module, item.action)(item)

                if config.get_setting('trakt_sync'):
                    from core import trakt_tools
                    token_auth = config.get_setting("token_trakt", "trakt")
                    if not token_auth:
                        trakt_tools.auth_trakt()
                    else:
                        import xbmc
                        if not xbmc.getCondVisibility('System.HasAddon(script.trakt)') and config.get_setting(
                                'install_trakt'):
                            trakt_tools.ask_install_script()
                    itemlist = trakt_tools.trakt_check(itemlist)
                elif not config.get_setting('install_trakt'):
                    config.set_setting('install_trakt', True)

    except urllib2.URLError as e:
        import traceback
        logger.error(traceback.format_exc())

        # Grab inner and third party errors
        if hasattr(e, 'reason'):
            logger.error("Razon del error, codigo: %s | Razon: %s" % (str(e.reason[0]), str(e.reason[1])))
            texto = config.get_localized_string(30050)  # "No se puede conectar con el sitio web"
            platformtools.dialog_ok("Alfa", texto)

        # Grab server response errors
        elif hasattr(e, 'code'):
            logger.error("Codigo de error HTTP : %d" % e.code)
            # "El sitio web no funciona correctamente (error http %d)"
            platformtools.dialog_ok("Alfa", config.get_localized_string(30051) % e.code)
    except WebErrorException as e:
        import traceback
        from core import scrapertools
        logger.error(traceback.format_exc())

        patron = 'File "' + os.path.join(config.get_runtime_path(), "channels", "").replace("\\",
                                                                                            "\\\\") + '([^.]+)\.py"'
        canal = scrapertools.find_single_match(traceback.format_exc(), patron)

        platformtools.dialog_ok(
            config.get_localized_string(59985) + canal,
            config.get_localized_string(60013) %(e))
    except Exception:
        import traceback
        from core import scrapertools
        logger.error(traceback.format_exc())

        patron = 'File "' + os.path.join(config.get_runtime_path(), "channels", "").replace("\\",
                                                                                            "\\\\") + '([^.]+)\.py"'
        canal = scrapertools.find_single_match(traceback.format_exc(), patron)

        try:
            if config.get_platform(True)['num_version'] < 14:
                log_name = "xbmc.log"
            else:
                log_name = "kodi.log"
            log_message = config.get_localized_string(50004) + config.translatePath("special://logpath") + log_name
        except Exception:
            log_message = ""

        if canal:
            platformtools.dialog_ok(
                config.get_localized_string(60087) %canal,
                config.get_localized_string(60014),
                log_message)
        else:
            platformtools.dialog_ok(
                config.get_localized_string(60038),
                config.get_localized_string(60015),
                log_message)

    if itemlist is not None:
        platformtools.render_items(itemlist, item)



def reorder_itemlist(itemlist):
    logger.info()
    # logger.debug("Inlet itemlist size: %i" % len(itemlist))

    new_list = []
    mod_list = []
    not_mod_list = []

    modified = 0
    not_modified = 0

    to_change = [[config.get_localized_string(60335), '[V]'],
                 [config.get_localized_string(60336), '[D]']]

    for item in itemlist:
        if not PY3:
            old_title = unicode(item.title, "utf8").lower().encode("utf8")
        else:
            old_title = item.title.lower()
        for before, after in to_change:
            if before in item.title:
                item.title = item.title.replace(before, after)
                break

        if not PY3:
            new_title = unicode(item.title, "utf8").lower().encode("utf8")
        else:
            new_title = item.title.lower()
        if old_title != new_title:
            mod_list.append(item)
            modified += 1
        else:
            not_mod_list.append(item)
            not_modified += 1

            # logger.debug("OLD: %s | NEW: %s" % (old_title, new_title))

    new_list.extend(mod_list)
    new_list.extend(not_mod_list)

    logger.info("Titulos modificados:%i | No modificados:%i" % (modified, not_modified))

    if len(new_list) == 0:
        new_list = itemlist

    # logger.debug("Outlet itemlist size: %i" % len(new_list))
    return new_list


def limit_itemlist(itemlist):
    logger.info()
    # logger.debug("Inlet itemlist size: %i" % len(itemlist))

    try:
        opt = config.get_setting("max_links", "videolibrary")
        if opt == 0:
            new_list = itemlist
        else:
            i_max = 30 * opt
            new_list = itemlist[:i_max]

        # logger.debug("Outlet itemlist size: %i" % len(new_list))
        return new_list
    except Exception:
        return itemlist


def play_from_library(item):
    """
        Los .strm al reproducirlos desde kodi, este espera que sea un archivo "reproducible" asi que no puede contener
        más items, como mucho se puede colocar un dialogo de seleccion.
        Esto lo solucionamos "engañando a kodi" y haciendole creer que se ha reproducido algo, asi despues mediante
        "Container.Update()" cargamos el strm como si un item desde dentro del addon se tratara, quitando todas
        las limitaciones y permitiendo reproducir mediante la funcion general sin tener que crear nuevos métodos para
        la videoteca.
        @type item: item
        @param item: elemento con información
    """
    logger.info()
    #logger.debug("item: \n" + item.tostring('\n'))

    import xbmcgui
    import xbmcplugin
    import xbmc
    from time import sleep, time
    from modules import nextep
    from modules import autoplay
    from channels import videolibrary

    # Intentamos reproducir una imagen (esto no hace nada y ademas no da error)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True,
                              xbmcgui.ListItem(
                                  path=os.path.join(config.get_runtime_path(), "resources", "subtitle.mp4")))

    # Por si acaso la imagen hiciera (en futuras versiones) le damos a stop para detener la reproduccion
    sleep(2)                  ### Si no se pone esto se bloquea Kodi
    xbmc.Player().stop()

    # modificamos el action (actualmente la videoteca necesita "findvideos" ya que es donde se buscan las fuentes
    item.action = "findvideos"
    check_next_ep = nextep.check(item)


    window_type = config.get_setting("window_type", "videolibrary")

    # y volvemos a lanzar kodi
    if xbmc.getCondVisibility('Window.IsMedia') and not window_type == 1:
        # Ventana convencional
        xbmc.executebuiltin("Container.Update(" + sys.argv[0] + "?" + item.tourl() + ")")

    else:

        # Ventana emergente

        p_dialog = platformtools.dialog_progress_bg(config.get_localized_string(20000), config.get_localized_string(70004))
        p_dialog.update(0, '')

        itemlist = videolibrary.findvideos(item)

        if check_next_ep and autoplay.is_active(item.contentChannel):
            p_dialog.update(100, '')
            sleep(0.5)
            p_dialog.close()
            item = nextep.return_item(item)
            if item.next_ep:
                return play_from_library(item)

        else:
            while platformtools.is_playing():
                    # Ventana convencional
                    sleep(5)
            p_dialog.update(50, '')

        it = item
        if not check_next_ep or not autoplay.is_active(item.contentChannel):

            '''# Se filtran los enlaces segun la lista negra
            if config.get_setting('filter_servers', "servers"):
                itemlist = servertools.filter_servers(itemlist)'''

            # Se limita la cantidad de enlaces a mostrar
            if config.get_setting("max_links", "videolibrary") != 0:
                itemlist = limit_itemlist(itemlist)

            # Se "limpia" ligeramente la lista de enlaces
            if config.get_setting("replace_VD", "videolibrary") == 1:
                itemlist = reorder_itemlist(itemlist)


            p_dialog.update(100, '')
            sleep(0.5)
            p_dialog.close()


            if len(itemlist) > 0:
                while not xbmc.Monitor().abortRequested():
                    # El usuario elige el mirror
                    opciones = []
                    for i in itemlist:
                        if '%s' in i.title and i.action == 'play' and i.server: i.title = i.title % i.server.capitalize()
                        opciones.append(i.title)

                    # Se abre la ventana de seleccion
                    if (item.contentSerieName != "" and
                                item.contentSeason != "" and
                                item.contentEpisodeNumber != ""):
                        cabecera = ("%s - %sx%s -- %s" %
                                    (item.contentSerieName,
                                     item.contentSeason,
                                     item.contentEpisodeNumber,
                                     config.get_localized_string(30163)))
                    else:
                        cabecera = config.get_localized_string(30163)

                    seleccion = platformtools.dialog_select(cabecera, opciones)

                    if seleccion == -1:
                        return
                    else:
                        item = videolibrary.play(itemlist[seleccion])[0]
                        if item.action == 'play':
                            platformtools.play_video(item)
                        else:
                            channel_file = os.path.join(config.get_runtime_path(),
                                                  'channels', item.contentChannel + ".py")
                            channel = __import__('channels.%s' % item.contentChannel, None, None, ["channels.%s" % item.contentChannel])
                            if not channel:
                                logger.error('Channel "%s" missing (%s: %s) or not imported: %s' \
                                              % (item.contentChannel, channel_file, os.path.exists(channel_file), channel))
                            if hasattr(channel, item.action):
                                play_items = getattr(channel, item.action)(item.clone(action=item.action, 
                                                     channel=item.contentChannel))
                            return

                    if (platformtools.is_playing() and item.action) or item.server == 'torrent' or autoplay.is_active(item.contentChannel):
                        break

        if it.show_server and check_next_ep:
            nextep.run(it)
            sleep(0.5)
            p_dialog.close()
