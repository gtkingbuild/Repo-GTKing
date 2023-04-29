# -*- coding: utf-8 -*-

from builtins import range

import glob
import os

from core import channeltools
from core.item import Item
from platformcode import config, logger


def getmainlist(view="thumb_"):
    logger.info()
    itemlist = list()

    # Añade los canales que forman el menú principal

    get_string = config.get_localized_string
    addon_version = config.get_addon_version(with_fix=False, from_xml=True)

    itemlist.append(
        Item(
            title = get_string(30130),
            channel = "news",
            action = "mainlist",
            thumbnail = get_thumb("news.png", view),
            category = get_string(30119),
            viewmode = "thumbnails",
            context = [
                {
                    "title": get_string(70285),
                    "channel": "news", 
                    "action":"news_setting"
                }
            ]
        )
    )

    itemlist.append(
        Item(
            title = get_string(30118),
            channel = "channelselector",
            action = "getchanneltypes",
            thumbnail = get_thumb("channels.png", view),
            view = view,
            category = get_string(30119),
            viewmode = "thumbnails"
        )
    )

    itemlist.append(
        Item(
            title = get_string(80787),
            channel = "info_popup",
            action = "mainlist",
            thumbnail = get_thumb("wishlist.png", view),
            category = "wishlist",
            viewmode = "thumbnails",
            context = [
                {
                    "title": get_string(80788),
                    "channel": "info_popup",
                    "action": "show_settings"
                }
            ]
        )
    )

    itemlist.append(
        Item(
            title = get_string(70527),
            channel = "alfavorites",
            action ="mainlist",
            thumbnail = get_thumb("mylink.png", view),
            view = view,
            category = get_string(70527),
            viewmode = "thumbnails"
        )
    )

    itemlist.append(
        Item(
            title = get_string(30103),
            channel = "search",
            action = "mainlist",
            thumbnail = get_thumb("search.png", view),
            category = get_string(30119),
            viewmode = "list",
            context = [
                {
                    "title": get_string(70286),
                    "channel": "search",
                    "action": "opciones",
                    "goto": True
                }
            ]
        )
    )

    itemlist.append(
        Item(
            title = get_string(30102),
            channel = "favorites",
            action = "mainlist",
            thumbnail = get_thumb("favorites.png", view),
            category = get_string(30102),
            viewmode = "thumbnails"
        )
    )

    if config.get_videolibrary_support():
        itemlist.append(
            Item(
                title = get_string(30131),
                channel = "videolibrary",
                action = "mainlist",
                thumbnail = get_thumb("videolibrary.png", view),
                category = get_string(30119),
                viewmode = "thumbnails",
                context = [
                    {
                        "title": get_string(70287),
                        "channel": "videolibrary",
                        "action": "channel_config"
                    }
                ]
            )
        )

    itemlist.append(
        Item(
            title = get_string(30101),
            channel = "downloads",
            action = "mainlist",
            thumbnail = get_thumb("downloads.png", view),
            viewmode = "list",
            context = [
                {
                    "title": get_string(70288),
                    "channel": "setting",
                    "config": "downloads",
                    "action": "channel_config"
                }
            ]
        )
    )

    # fix = config.get_addon_version_fix()
    thumb_setting = "setting_%s.png" % 0 # int(fix[4:])

    itemlist.append(
        Item(
            title = get_string(30100),
            channel = "setting",
            action = "mainlist",
            thumbnail = get_thumb(thumb_setting, view),
            category = get_string(30100),
            viewmode = "list"
        )
    )

    if config.is_xbmc():
        itemlist.append(
            Item(
                title = get_string(70761),
                channel = "report",
                action = "mainlist",
                thumbnail = get_thumb("error.png", view),
                category = get_string(30104),
                viewmode = "list"
            )
        )

    itemlist.append(
        Item(
            title = '{} ({} {})'.format(get_string(30104), get_string(20000), addon_version),
            channel = "help",
            action = "mainlist",
            thumbnail = os.path.join(config.get_runtime_path(), "resources", 'Screenshot.jpg'),
            category = get_string(30104),
            viewmode = "list"
        )
    )
                         
    try:
        versiones = config.get_versions_from_repo()
    except:
        versiones = {}
        import traceback
        logger.error(traceback.format_exc())

    if versiones and addon_version != versiones.get('plugin.video.alfa', ''):
        itemlist.append(
            Item(
                title = "[COLOR hotpink][B]Actualizar a versión[/B][/COLOR] [COLOR gold][B]%s[/B][/COLOR] (versión instalada: %s)" %  (versiones['plugin.video.alfa'], addon_version),
                channel = "channelselector",
                action = "install_alfa",
                thumbnail = os.path.join(config.get_runtime_path(), "resources", 'Screenshot.jpg'),
                category = get_string(30104),
                viewmode = "list"
            )
        )

    from lib import generictools
    browser, res = generictools.call_browser('', lookup=True)
    browser_dict = {}

    if browser:
        browser_dict['action'] = 'call_browser'
        browser_dict['title'] = '{} [COLOR limegreen]{}[/COLOR]'.format(get_string(70758), get_string(70760) % browser)
    else:
        browser_dict['action'] = ''
        browser_dict['title'] = '{} [COLOR gold]({}: Chrome, Firefox, Opera)[/COLOR]:'.format(get_string(70758), get_string(70759))

    itemlist.append(
        Item(
            channel = "setting",
            action = browser_dict['action'],
            url = 'https://alfa-addon.com/foros/tutoriales.11/', 
            title = browser_dict['title'],
            thumbnail = get_thumb("help.png", view),
            unify = False,
            folder = False, 
            category = get_string(30104),
            viewmode = "list"
        )
    )
    
    itemlist.append(
        Item(
            channel = "setting",
            action = browser_dict['action'],
            url = 'https://alfa-addon.com/threads/manual-de-alfa-assistant-herramienta-de-apoyo.3797/', 
            title = "-     [COLOR yellow]Usa [COLOR hotpink][B]Alfa ASSISTANT[/B][/COLOR] para desbloquear webs y torrents[/COLOR]   " + 
                    "https://alfa-addon.com/threads/manual-de-alfa-assistant-herramienta-de-apoyo.3797/",
            thumbnail = get_thumb("on_the_air.png", view),
            unify = False,
            folder = False,
            category = get_string(30104),
            viewmode = "list"
        )
    )

    return itemlist


def getchanneltypes(view="thumb_"):
    logger.info()

    # Lista de categorias
    #channel_types = ["movie", "tvshow", "anime", "documentary", "vos", "direct", "torrent", "sport"]
    channel_types = ["movie", "tvshow", "anime", "documentary", "vos", "direct", "torrent"]

    if config.get_setting("adult_mode") != 0:
        channel_types.append("adult")

    channel_language = config.get_setting("channel_language", default="all")
    logger.info("channel_language=%s" % channel_language)

    # Ahora construye el itemlist ordenadamente
    itemlist = list()
    title = config.get_localized_string(30121)

    # Todos
    itemlist.append(
        Item(
            title = title,
            channel = "channelselector",
            action = "filterchannels",
            view = view,
            category = title,
            channel_type = "all",
            thumbnail = get_thumb("channels_all.png", view),
            viewmode = "thumbnails"
        )
    )

    # Frecuentes/favoritos
    if config.get_setting('frequents_folder'):
        itemlist.append(
            Item(
                title = 'Frecuentes',
                channel = "channelselector",
                action = "filterchannels",
                view = view,
                category = 'all',
                channel_type = "freq",
                thumbnail = get_thumb("channels_frequents.png", view),
                viewmode = "thumbnails"
            )
        )

    # Iteramos por las categorías disponibles
    for channel_type in channel_types:
        title = config.get_localized_category(channel_type)
        itemlist.append(
            Item(
                title = title,
                channel = "channelselector",
                action = "filterchannels",
                category = title,
                channel_type = channel_type,
                viewmode = "thumbnails",
                thumbnail = get_thumb("channels_%s.png" % channel_type, view)
            )
        )

    # "Canal" (sección) comunidad
    itemlist.append(
        Item(
            title = 'Comunidad',
            channel = "community",
            action = "mainlist",
            view = view,
            category = title,
            channel_type = "all",
            thumbnail = get_thumb("channels_community.png", view),
            viewmode = "thumbnails"
        )
    )

    return itemlist


def filterchannels(category, view="thumb_", alfa_s=True, settings=False):
    #logger.info()

    channelslist = []
    frequent_list = []
    freq = False
    if category == 'freq':
        freq = True
        category = 'all'
    # Si category = "allchannelstatus" es que estamos activando/desactivando canales
    # Si category = "all-channels" viene del canal test
    appenddisabledchannels = False
    if category == "allchannelstatus":
        category = "all"
        appenddisabledchannels = True

    channel_language = config.get_setting("channel_language", default="all")
    logger.info("channel_language=%s" % channel_language)

    # Lee la lista de canales
    channel_path = os.path.join(config.get_runtime_path(), "channels", '*.json')
    logger.info("channel_path=%s" % channel_path)

    channel_files = glob.glob(channel_path)
    channel_files = [os.path.basename(channel).replace(".json", "") for channel in channel_files]
    logger.info("channel_files encontrados %s" % (len(channel_files)))

    for channel in channel_files:
        # logger.info("channel=%s" % channel)

        # channel = os.path.basename(channel).replace(".json", "")

        try:
            channel_parameters = channeltools.get_channel_parameters(channel, settings=settings)

            # Si el canal está desactivado, no es un canal, o es un módulo, lo saltamos
            if channel_parameters["channel"] == 'community' \
                or not channel_parameters["channel"] \
                    or not channel_parameters["active"]:
                continue

            # logger.info("channel_parameters=%s" % repr(channel_parameters))

            # Si prefiere el banner y el canal lo tiene, cambia ahora de idea
            if view == "banner_"and "banner" in channel_parameters:
                channel_parameters["thumbnail"] = channel_parameters["banner"]

            # Se salta el canal si no está activo y no estamos activando/desactivando los canales
            channel_status = config.get_setting("enabled", channel_parameters["channel"])

            # si channel_status == None es que NO HAY valor en _data.json.
            # como hemos llegado hasta aquí (el canal está activo en channel.json), se valida como activado
            if channel_status == False:
                # si obtenemos el listado de canales desde "activar/desactivar canales", y el canal está desactivado
                # lo mostramos, si estamos listando todos los canales desde el listado general y está desactivado,
                # no se muestra
                if not appenddisabledchannels:
                    continue

            # Se salta el canal para adultos si el modo adultos está desactivado
            if channel_parameters["adult"] \
                and config.get_setting("adult_mode") == 0 \
                    and category != "all_channels":
                continue

            # Se salta el canal si está en un idioma filtrado
            # Se muestran todos los canales si se elige "all" en el filtrado de idioma
            # Se muestran sólo los idiomas filtrados, cast o lat
            # Los canales de adultos se mostrarán siempre que estén activos
            if not alfa_s: logger.info(channel_parameters["language"])
            if channel_language != "all" \
                and not (channel_language in channel_parameters["language"] or "*" in channel_parameters["language"]) \
                    and category != "all_channels":
                continue

            # Se salta el canal si está en una categoria filtrado
            if category != "all" \
                and category not in channel_parameters["categories"] \
                    and category != "all_channels":
                continue

            # Si tiene configuración añadimos un item en el contexto
            context = []
            if channel_parameters["has_settings"]:
                context.append(
                    {
                        "title": config.get_localized_string(70525),
                        "channel": "setting",
                        "action": "channel_config",
                        "config": channel_parameters["channel"]
                    }
                )

            if os.path.exists(os.path.join(config.get_runtime_path(), 'channels', 'test.py')):
                context.append(
                    {
                        "title": config.get_localized_string(70215),
                        "channel": "test",
                        "action": "test_channel",
                        "contentChannel": channel_parameters["channel"],
                        "parameters": "test_channel"
                    }
                )

            if channel_parameters["req_assistant"]:
                channel_parameters["title"] = "{} [COLOR=yellow](requiere Assistant)[/COLOR]".format(channel_parameters["title"])

            channel_info = set_channel_info(channel_parameters, alfa_s=alfa_s)

            # Si ha llegado hasta aquí, lo añade
            frequency = channeltools.get_channel_setting("frequency", channel_parameters["channel"], 0) \
                        if config.get_setting('frequents') or freq else 0

            channelslist.append(
                Item(
                    action = "mainlist",
                    active = channel_parameters["active"],
                    category = channel_parameters["title"],
                    channel = channel_parameters["channel"],
                    context = context,
                    fanart = channel_parameters["fanart"],
                    frequency = frequency,
                    language = channel_parameters["language"],
                    plot = channel_info,
                    thumbnail = channel_parameters["thumbnail"],
                    title = channel_parameters["title"],
                    viewmode = "videos",
                    settings = channel_parameters.get("settings", [])
                )
            )

        except:
            logger.error("Se ha producido un error al leer los datos del canal '%s'" % channel)
            import traceback
            logger.error(traceback.format_exc())

    if config.get_setting('frequents'):
        for ch in channelslist:
            if int(ch.frequency) != 0:
                frequent_list.append(ch)

        frequent_list = sorted(frequent_list, key=lambda item: item.frequency, reverse=True)

        if freq:
            max_ff = config.get_setting("max_frequents_folder")
            if max_ff > 0:
                return frequent_list[0:max_ff]
            else:
                return frequent_list

        max_freq = config.get_setting("max_frequents")
        if frequent_list and category != 'all_channels':
            if len(frequent_list) >= max_freq:
                max_freq = max_freq
            else:
                max_freq = len(frequent_list)
            frequent_list = frequent_list[0:max_freq]
            frequent_list.insert(0, Item(title='- Canales frecuentes -', action=''))

            frequent_list.append(Item(title='- Todos los canales -', action=''))

    elif freq:
        for ch in channelslist:
            if int(ch.frequency) != 0:
                frequent_list.append(ch)

        frequent_list = sorted(frequent_list, key=lambda item: item.frequency, reverse=True)

        max_ff = config.get_setting("max_frequents_folder")
        if max_ff > 0:
            return frequent_list[0:max_ff]
        else:
            return frequent_list


    channelslist.sort(key=lambda item: item.title.lower().strip())

    if category == "all":
        channel_parameters = channeltools.get_channel_parameters('url')
        # Si prefiere el banner y el canal lo tiene, cambia ahora de idea
        if view == "banner_" and "banner" in channel_parameters:
            channel_parameters["thumbnail"] = channel_parameters["banner"]

        channelslist.insert(0, Item(title=config.get_localized_string(60088), action="mainlist", channel="url", 
                                    settings=[], active=channel_parameters["active"], 
                                    thumbnail=channel_parameters["thumbnail"], type="generic", viewmode="list"))

    if frequent_list and config.get_setting('frequents'):
        channelslist =  frequent_list + channelslist

    if category in ['movie', 'tvshow']:
        titles = [config.get_localized_string(70028), config.get_localized_string(30985), config.get_localized_string(70559), config.get_localized_string(60264), config.get_localized_string(70560)]
        ids = ['popular', 'top_rated', 'now_playing', 'on_the_air']
        for x in range(0,3):
            if x == 2 and category != 'movie':
                title = titles[x+1]
                id = ids[x+1]
            else:
                title = titles[x]
                id = ids[x]
            channelslist.insert(x,
                Item(channel='search', action='discover_list', title=title, search_type='list', 
                     settings=[], active=channel_parameters["active"], 
                     list_type='%s/%s' % (category.replace('show',''), id), thumbnail=get_thumb(id+".png"),
                     mode=category))

        channelslist.insert(3, Item(channel='search', action='years_menu', title='Por Años', 
                                    settings=[], active=channel_parameters["active"], 
                                    type=category.replace('show', ''), thumbnail=get_thumb("years.png"),
                                    mode=category))

        channelslist.insert(4, Item(channel='search', action='genres_menu', title='Generos', 
                                    settings=[], active=channel_parameters["active"], 
                                    type=category.replace('show',''), thumbnail=get_thumb("genres.png"),
                                    mode=category))

    ### Especiales (Halloween, otros)
    from datetime import date

    today = date.today()

    if today.month == 10 and category == "movie":
        this_year = today.year
        from_date = "%s-01-01" % this_year
        discovery = {"url": "discover/movie", "with_genres": "27", "primary_release_date.lte": "%s" % today,
                     "primary_release_date.gte": from_date, "page": "1"}

        channelslist.insert(0, Item(channel="search", title="Halloween %s" % this_year, page=1, action='discover_list', 
                                    settings=[], active=channel_parameters["active"], 
                                    discovery=discovery, mode="movie", thumbnail=get_thumb("channels_horror.png")))
    return channelslist


def get_thumb(thumb_name, view="thumb_", auto=False):
    from platformcode.unify import thumb_dict, set_genre, simplify

    if auto:
        thumbnail = ''

        thumb_name = set_genre(simplify(thumb_name)).lower()

        if thumb_name in thumb_dict:
            thumbnail = thumb_dict[thumb_name]

        return thumbnail

    else:
        icon_pack_name = config.get_setting('icon_set', default="default")

        if icon_pack_name == "default":
            resource_path = os.path.join(config.get_runtime_path(), "resources", "media", "themes")

        else:
            resource_path = "https://raw.githubusercontent.com/alfa-addon/media/master/themes/"

        media_path = os.path.join(resource_path, icon_pack_name)

        return os.path.join(media_path, view + thumb_name)


def set_channel_info(parameters, alfa_s=False):
    if not alfa_s: logger.info()

    info = ''
    language = ''
    content = ''
    is_adult = parameters['adult']
    langs = parameters['language']
    categories = parameters['categories']

    # Hacemos el listado de categorías p/ descripción
    content = ', '.join([config.get_localized_category(cat) for cat in categories if cat])

    # Si langs está vacío o es +18 y '*' está en langs omitimos la parte del idioma
    if is_adult and '*' in langs or not langs:
        info = '[COLOR yellow]Tipo de contenido:[/COLOR] %s' % content

    # Sino, procesamos
    else:
        lang_dict = { 'lat':'Latino', 'cast':'Castellano', 'vose': 'VOSE', 'vos': 'VOS' }
        langs = [lang_dict.get(lang.lower(), lang) for lang in langs]

        # Si se encuentra un '*' quiere decir contenido mixto, agregamos todos los elementos directamente
        if '*' in langs:
            language = ', '.join(list(lang_dict.values()))

        else:
            language = ', '.join(langs)

        info = '[COLOR yellow]Tipo de contenido:[/COLOR] %s\n\n[COLOR yellow]Idiomas:[/COLOR] %s' % (content, language)

    return info


def install_alfa():
    
    from platformcode.custom_code import install_alfa_now
    install_alfa_now()
