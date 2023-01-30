# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# filtertools - se encarga de filtrar resultados
# ------------------------------------------------------------

from builtins import object

from core import jsontools
from core.item import Item
from platformcode import config, logger
from platformcode import platformtools
from core import channeltools

TAG_TVSHOW_FILTER = "TVSHOW_FILTER"
TAG_NAME = "name"
TAG_ACTIVE = "active"
TAG_TITLE = "season_search"
TAG_LANGUAGE = "language"
TAG_QUALITY_ALLOWED = "quality_allowed"

COLOR = {"parent_item": "yellow", "error": "red", "selected": "blue", 
         "striped_even_active": "blue", "striped_even_inactive": "limegreen", 
         "striped_odd_active": "aqua", "striped_odd_inactive": "yellowgreen"
         }

filter_global = None

__channel__ = "filtertools"


# TODO echar un ojo a https://pyformat.info/, se puede formatear el estilo y hacer referencias directamente a elementos


class ResultFilter(object):
    def __init__(self, dict_filter):
        self.active = dict_filter.get(TAG_ACTIVE, False)
        self.title = dict_filter.get(TAG_TITLE, '')
        self.language = dict_filter.get(TAG_LANGUAGE, '')
        self.quality_allowed = dict_filter.get(TAG_QUALITY_ALLOWED, [])

    def __str__(self):
        return "{active: '%s', title: '%s', language: '%s', quality_allowed: '%s'}" % \
               (self.active, self.title, self.language, self.quality_allowed)


class Filter(object):
    def __init__(self, item, global_filter_lang_id):
        self.result = None
        self.__get_data(item, global_filter_lang_id)

    def __get_data(self, item, global_filter_lang_id):

        dict_filtered_shows = jsontools.get_node_from_file(item.channel, TAG_TVSHOW_FILTER)
        tvshow = normalize(item.show)
        if tvshow not in list(dict_filtered_shows.keys()) and '*' in list(dict_filtered_shows.keys()) \
                  and item.action not in ['buscartrailer', 'add_serie_to_library', 'add_pelicula_to_library']:
            tvshow = '*'

        global_filter_language = config.get_setting(global_filter_lang_id, item.channel)

        if tvshow in list(dict_filtered_shows.keys()):

            self.result = ResultFilter({TAG_ACTIVE: dict_filtered_shows[tvshow].get(TAG_ACTIVE, False),
                                        TAG_TITLE: dict_filtered_shows[tvshow].get(TAG_TITLE, ''),
                                        TAG_LANGUAGE: dict_filtered_shows[tvshow].get(TAG_LANGUAGE, ''),
                                        TAG_QUALITY_ALLOWED: dict_filtered_shows[tvshow].get(TAG_QUALITY_ALLOWED, [])})

        # opcion general "no filtrar"
        elif global_filter_language != 0:
            list_controls, dict_settings = channeltools.get_channel_controls_settings(item.channel)

            for control in list_controls:
                if control["id"] == global_filter_lang_id:

                    try:
                        language = control["lvalues"][global_filter_language]
                        # logger.debug("language %s" % language)
                    except:
                        logger.error("No se ha encontrado el valor asociado al codigo '%s': %s" %
                                     (global_filter_lang_id, global_filter_language))
                        break

                    self.result = ResultFilter({TAG_ACTIVE: True, TAG_LANGUAGE: language, TAG_QUALITY_ALLOWED: []})
                    break

    def __str__(self):
        return "{'%s'}" % self.result


def normalize(title):

    if title:
        from core.scrapertools import slugify
        title = slugify(title, strict=False).strip()
    else:
        title = ''
    
    return title


def access():
    """
    Devuelve si se puede usar o no filtertools
    """
    allow = False

    if config.is_xbmc() or config.get_platform() == "mediaserver":
        allow = True

    return allow


def context(item, list_language=None, list_quality=None, exist=False):
    """
    Para xbmc/kodi y mediaserver ya que pueden mostrar el menú contextual, se añade un menu para configuración
    la opción de filtro, sólo si es para series.
    Dependiendo del lugar y si existe filtro se añadirán más opciones a mostrar.
    El contexto -solo se muestra para series-.

    @param item: elemento para obtener la información y ver que contexto añadir
    @type item: item
    param list_language: listado de idiomas posibles
    @type list_language: list[str]
    @param list_quality: listado de calidades posibles
    @type list_quality: list[str]
    @param exist: si existe el filtro
    @type exist: bool
    @return: lista de opciones a mostrar en el menú contextual
    @rtype: list
    """

    # Dependiendo de como sea el contexto lo guardamos y añadimos las opciones de filtertools.
    if isinstance(item.context, str):
        _context = item.context.replace('["', '').replace('"]', '').replace("['", "").replace("']", "").split("|")
    elif isinstance(item.context, list):
        _context = item.context
    else:
        _context = []

    if access():
        dict_data = {"title": "FILTRO: Configurar", "action": "config_item", "channel": "filtertools"}
        if list_language:
            dict_data["list_language"] = list_language
        if list_quality:
            dict_data["list_quality"] = list_quality

        added = False
        if isinstance(_context, list):
            for x in _context:
                if x and isinstance(x, dict):
                    if x["channel"] == "filtertools":
                        added = True
                        break

        if not added:
            _context.append(dict_data)

        if isinstance(item.language, list):
            language_list = item.language
        else:
            language_list = [str(item.language)]
        if item.action == "play":
            for language in language_list:
                if not exist and 'dual' not in language.lower():
                    _context.append({"title": "FILTRO: Añadir '%s'" % language, "action": "save_from_context",
                                     "channel": "filtertools", "from_channel": item.channel})
                elif exist:
                    _context.append({"title": "FILTRO: Borrar '%s'" % language, "action": "delete_from_context",
                                     "channel": "filtertools", "from_channel": item.channel})
        
        # Añadimos item.season_search si exist en el diccionario
        get_season_search(item)

    return _context


def show_option(itemlist, channel, list_language, list_quality):
    if access():
        from channelselector import get_thumb
        itemlist.append(Item(channel=__channel__, title="[COLOR %s]Configurar filtro para series...[/COLOR]" %
                                                        COLOR.get("parent_item", "auto"), action="load",
                             list_language=list_language, thumbnail=get_thumb('wishlist.png'), 
                             list_quality=list_quality, from_channel=channel))

    return itemlist


def load(item):
    return mainlist(channel=item.from_channel, list_language=item.list_language, list_quality=item.list_quality)


def check_conditions(_filter, list_item, item, list_language, list_quality, quality_count=0, language_count=0):
    is_language_valid = True

    if _filter.language:
        # logger.debug("title es %s" % item.title)
        #2nd lang

        from platformcode import unify
        _filter.language = unify.set_lang(_filter.language).upper()

        # viene de episodios
        if isinstance(item.language, list):
            #2nd lang
            for n, lang in enumerate(item.language):
                item.language[n] = unify.set_lang(lang).upper()

            if _filter.language in item.language or 'DUAL' in item.language or not item.action \
                                or item.action in ['buscartrailer', 'add_serie_to_library', 'add_pelicula_to_library']:
                language_count += 1
            else:
                is_language_valid = False
        # viene de findvideos
        else:
            #2nd lang
            item.language = unify.set_lang(item.language).upper()

            if item.language.lower() == _filter.language.lower() or 'DUAL' in item.language or not item.action \
                                         or item.action in ['buscartrailer', 'add_serie_to_library', 'add_pelicula_to_library']:
                language_count += 1
            else:
                is_language_valid = False

        is_quality_valid = True
        quality = ""
        quality_list = []

        if _filter.quality_allowed and item.quality and item.action and \
                                   item.action not in ['buscartrailer', 'add_serie_to_library', 'add_pelicula_to_library']:
            # if hasattr(item, 'quality'): # esta validación no hace falta por que SIEMPRE se devuelve el atributo vacío
            if item.quality_alt and isinstance(item.quality_alt, list):
                quality_list = item.quality_alt[:]
                del item.quality_alt
            elif item.quality_alt:
                quality_list = [item.quality_alt]
                del item.quality_alt
            else:
                quality_list = [item.quality]

            for quality in quality_list:
                if quality.lower() in _filter.quality_allowed or quality.lower().replace(' ', '-') in _filter.quality_allowed:
                    quality_count += 1
                    break
            else:
                is_quality_valid = False

        if is_language_valid and is_quality_valid:
            #TODO 2nd lang: habría que ver si conviene unificar el idioma aqui o no
            item.list_language = list_language
            if list_quality:
                item.list_quality = list_quality
            item.context = context(item, exist=True)
            list_item.append(item)
            # logger.debug("{0} | context: {1}".format(item.title, item.context))
            # logger.debug(" -Enlace añadido")

        logger.debug(" idioma valido?: %s, item.language: %s, filter.language: %s" %
                     (is_language_valid, item.language, _filter.language))
        logger.debug(" calidad valida?: %s, item.quality: %s, filter.quality_allowed: %s"
                     % (is_quality_valid, quality, _filter.quality_allowed))

    return list_item, quality_count, language_count, _filter.language


def get_link(list_item, item, list_language, list_quality=None, global_filter_lang_id="filter_languages"):
    """
    Devuelve una lista de enlaces, si el item está filtrado correctamente se agrega a la lista recibida.

    @param list_item: lista de enlaces
    @type list_item: list[Item]
    @param item: elemento a filtrar
    @type item: Item
    @param list_language: listado de idiomas posibles
    @type list_language: list[str]
    @param list_quality: listado de calidades posibles
    @type list_quality: list[str]
    @param global_filter_lang_id: id de la variable de filtrado por idioma que está en settings
    @type global_filter_lang_id: str
    @return: lista de Item
    @rtype: list[Item]
    """
    logger.info()

    # si los campos obligatorios son None salimos
    if list_item is None or item is None:
        return []

    logger.debug("total de items : %s" % len(list_item))

    global filter_global

    if not filter_global:
        filter_global = Filter(item, global_filter_lang_id).result
    logger.debug("filter: '%s' datos: '%s'" % (normalize(item.show).title(), filter_global))

    if filter_global and filter_global.active:
        list_item, quality_count, language_count = \
            check_conditions(filter_global, list_item, item, list_language, list_quality)[:3]
    else:
        item.context = context(item)
        list_item.append(item)

    return list_item


def get_links(list_item, item, list_language, list_quality=None, global_filter_lang_id="filter_languages", replace_label=None):
    """
    Devuelve una lista de enlaces filtrados.

    @param list_item: lista de enlaces
    @type list_item: list[Item]
    @param item: elemento a filtrar
    @type item: item
    @param list_language: listado de idiomas posibles
    @type list_language: list[str]
    @param list_quality: listado de calidades posibles
    @type list_quality: list[str]
    @param global_filter_lang_id: id de la variable de filtrado por idioma que está en settings
    @type global_filter_lang_id: str
    @return: lista de Item
    @rtype: list[Item]
    """
    logger.info()


    # si los campos obligatorios son None salimos
    if list_item is None or item is None:
        return []

    # si list_item está vacío volvemos, no se añade validación de plataforma para que Plex pueda hacer filtro global
    if len(list_item) == 0:
        return list_item


    second_lang = config.get_setting('second_language')

    #Ordena segun servidores favoritos, elima servers de blacklist y desactivados
    from core import servertools
    list_item= servertools.filter_servers(list_item)

    logger.debug("total de items : %s" % len(list_item))

    new_itemlist = []
    quality_count = 0
    language_count = 0

    _filter = Filter(item, global_filter_lang_id).result
    logger.debug("filter: '%s' datos: '%s'" % (normalize(item.show).title(), _filter))


    if _filter and _filter.active:

        for item in list_item:
            if item.quality:
                item.quality_alt = item.quality
                if replace_label: item.quality_alt = item.quality_alt.replace(replace_label, '').strip()
                if ', ' in item.quality_alt: 
                    item.quality_alt = item.quality_alt.split(', ')
                elif ',' in item.quality_alt: 
                    item.quality_alt = item.quality_alt.split(',')
            new_itemlist, quality_count, language_count, first_lang = check_conditions(_filter, new_itemlist, item, list_language,
                                                                                       list_quality, quality_count, language_count)

        #2nd lang
        if second_lang and second_lang != 'No' and first_lang.lower() != second_lang.lower() :
            second_list= []
            _filter2 = _filter
            _filter2.language = second_lang
            for it in new_itemlist:
                
                if isinstance(it.language, list):
                    if not second_lang in it.language:
                        second_list.append(it)
                else:
                    second_list = new_itemlist
                    break
            for item in list_item:
                new_itemlist, quality_count, language_count, second_lang = check_conditions(_filter2, second_list, item, list_language,
                                                                                            list_quality, quality_count, language_count)

        logger.debug("ITEMS FILTRADOS: %s/%s, idioma [%s]: %s, calidad_permitida %s: %s"
                    % (len(new_itemlist), len(list_item), _filter.language, language_count, _filter.quality_allowed,
                       quality_count))

        if (not new_itemlist and item.sub_action not in ["tvshow", "season", "unseen", "auto"]) \
                             or (new_itemlist and new_itemlist[-1].action not in ["findvideos", "play", "episodios"]):
            list_item_all = []
            for i in list_item:
                list_item_all.append(i.tourl())

            _context = [{"title": "FILTRO: Borrar '%s'" % _filter.language, "action": "delete_from_context",
                         "channel": "filtertools", "to_channel": item.channel},
                         {"title": "FILTRO: Configurar", "action": "config_item", "channel": "filtertools", 
                         "from_channel_save": item.channel, "from_action_save": item.action, 
                         "list_language": list_language, "list_quality": list_quality}]
            
            if _filter.quality_allowed:
                msg_quality_allowed = " y calidad %s" % _filter.quality_allowed
            else:
                msg_quality_allowed = ""
            
            msg_lang = ' %s' % first_lang.upper()
            if second_lang and second_lang != 'No':
                msg_lang = 's %s ni %s' % (first_lang.upper(), second_lang.upper())
            
            new_itemlist.append(Item(channel=__channel__, action="no_filter", list_item_all=list_item_all,
                                     show=normalize(item.show).title(),
                                     title="[COLOR %s]No hay elementos con idioma%s%s, pulsa para mostrar "
                                           "sin filtro[/COLOR]"
                                           % (COLOR.get("error", "auto"), msg_lang, msg_quality_allowed),
                                     context=_context))

    else:
        for item in list_item:
            item.list_language = list_language
            if list_quality:
                item.list_quality = list_quality
            item.context = context(item)
        new_itemlist = list_item

    return new_itemlist


def no_filter(item):
    """
    Muestra los enlaces sin filtrar

    @param item: item
    @type item: Item
    @return: lista de enlaces
    @rtype: list[Item]
    """
    logger.info()

    itemlist = []
    for i in item.list_item_all:
        itemlist.append(Item().fromurl(i))

    return itemlist


def mainlist(channel, list_language, list_quality):
    """
    Muestra una lista de las series filtradas

    @param channel: nombre del canal para obtener las series filtradas
    @type channel: str
    @param list_language: lista de idiomas del canal
    @type list_language: list[str]
    @param list_quality: lista de calidades del canal
    @type list_quality: list[str]
    @return: lista de Item
    @rtype: list[Item]
    """
    logger.info()
    itemlist = []
    dict_series = jsontools.get_node_from_file(channel, TAG_TVSHOW_FILTER)

    idx = 0
    for tvshow in sorted(dict_series):

        if idx % 2 == 0:
            if dict_series[tvshow][TAG_ACTIVE]:
                tag_color = COLOR.get("striped_even_active", "auto")
            else:
                tag_color = COLOR.get("striped_even_inactive", "auto")
        else:
            if dict_series[tvshow][TAG_ACTIVE]:
                tag_color = COLOR.get("striped_odd_active", "auto")
            else:
                tag_color = COLOR.get("striped_odd_inactive", "auto")

        idx += 1
        name = dict_series.get(tvshow, {}).get(TAG_NAME, tvshow)
        if name == '*': name = '* Genérico para el Canal'
        activo = " (desactivado)"
        if dict_series[tvshow][TAG_ACTIVE]:
            activo = ""
        title = "Configurar [COLOR %s][%s][/COLOR]%s" % (tag_color, name, activo)

        itemlist.append(Item(channel=__channel__, action="config_item", title=title, show=name, unify=False, 
                             list_language=list_language, list_quality=list_quality, from_channel=channel))

    if len(itemlist) == 0:
        itemlist.append(Item(channel=channel, action="mainlist", title="No existen filtros, busca una serie y "
                                                                       "pulsa en menú contextual 'FILTRO: Configurar'"))

    return itemlist


def config_item(item):
    """
    muestra una serie filtrada para su configuración

    @param item: item
    @type item: Item
    """
    logger.info()
    logger.debug("item %s" % item.tostring())
    
    # Si viene de una lista de enlaces vacía, se restauran valores originales del canal
    if item.context and isinstance(item.context, list):
        for context in item.context:
            if isinstance(context, dict):
                if 'FILTRO: Configurar' in context.get('title', ''):
                    if 'from_channel_save' in context:
                        item.from_channel = context['from_channel_save']
                        context['from_channel'] = context['from_channel_save']
                    if 'from_action_save' in context:
                        item.from_action = context['from_action_save']
                        context['from_action'] = context['from_action_save']
                    if 'list_language' in context:
                        item.list_language = context['list_language'] or []
                    if 'list_quality' in context:
                        item.list_quality = context['list_quality'] or []
                    if item.from_channel in ['videolibrary']:
                        item.from_channel = item.contentChannel
                        context['from_channel'] = item.from_channel
    
    # OBTENEMOS LOS DATOS DEL JSON
    dict_series = jsontools.get_node_from_file(item.from_channel, TAG_TVSHOW_FILTER)

    if str(item.show).startswith('*'):
        tvshow = '*'
    else:
        tvshow = normalize(item.show)
        get_season_search(item, dict_series=dict_series)
    default_lang = ''

    channel_parameters = channeltools.get_channel_parameters(item.from_channel)
    list_language = channel_parameters["filter_languages"]
    try:
        if channel_parameters["filter_languages"] and len(list_language) > 0:
            default_lang = list_language[1]
    except:
        pass

    if default_lang == '':
        platformtools.dialog_notification("FilterTools", "No hay idiomas definidos")
        return
    else:
        title_selected = str(item.season_search.title() or tvshow.title())
        lang_selected = str(dict_series.get(tvshow, {}).get(TAG_LANGUAGE, default_lang))
        list_quality = dict_series.get(tvshow, {}).get(TAG_QUALITY_ALLOWED, [x.lower() for x in item.list_quality])
        # logger.info("title selected {}".format(title_selected))
        # logger.info("lang selected {}".format(lang_selected))
        # logger.info("list quality {}".format(list_quality))

        active = True
        custom_button = {'visible': False}
        allow_option = False
        if tvshow in dict_series:
            allow_option = True
            active = dict_series.get(tvshow, {}).get(TAG_ACTIVE, False)
            custom_button = {'label': 'Borrar', 'function': 'delete', 'visible': True, 'close': True}

        list_controls = []

        if allow_option:
            active_control = {
                "id": "active",
                "type": "bool",
                "label": "¿Activar/Desactivar filtro?",
                "color": "",
                "default": active,
                "enabled": allow_option,
                "visible": allow_option,
            }
            list_controls.append(active_control)

        if title_selected:
            season_search = {
                "id": "season_search",
                "type": "text",
                "label": "Título alternativo para búsquedas",
                "color": "0xFFBBFFFF",
                "default": title_selected,
                "enabled": True,
                "visible": True,
            }
            list_controls.append(season_search)
        
        if lang_selected not in item.list_language:
            lang_selected = default_lang
        language_option = {
            "id": "language",
            "type": "list",
            "label": "Idioma",
            "color": "0xFFee66CC",
            "default": item.list_language.index(lang_selected),
            "enabled": True,
            "visible": True,
            "lvalues": item.list_language
        }
        list_controls.append(language_option)

        if item.list_quality:
            list_controls_calidad = [
                {
                    "id": "textoCalidad",
                    "type": "label",
                    "label": "Calidad permitida",
                    "color": "0xffC6C384",
                    "enabled": True,
                    "visible": True,
                },
            ]
            for element in sorted(item.list_quality, key=str.lower):
                list_controls_calidad.append({
                    "id": element,
                    "type": "bool",
                    "label": element,
                    "default": (False, True)[element.lower() in list_quality],
                    "enabled": True,
                    "visible": True,
                })

            # concatenamos list_controls con list_controls_calidad
            list_controls.extend(list_controls_calidad)

        title = "Filtrado de enlaces para: [COLOR %s]%s[/COLOR]" % (COLOR.get("selected", "auto"), tvshow.title())

        platformtools.show_channel_settings(list_controls=list_controls, callback='save', item=item,
                                            caption=title, custom_button=custom_button)


def delete(item, dict_values):
    logger.info()

    if item:
        dict_series = jsontools.get_node_from_file(item.from_channel, TAG_TVSHOW_FILTER)
        if str(item.show).startswith('*'):
            tvshow = '*'
        else:
            tvshow = normalize(item.show)

        heading = "¿Está seguro que desea eliminar el filtro?"
        line1 = "Pulse 'Si' para eliminar el filtro de [COLOR %s]%s[/COLOR], pulse 'No' o cierre la ventana para " \
                "no hacer nada." % (COLOR.get("selected", "auto"), tvshow.title())

        if platformtools.dialog_yesno(heading, line1) == 1:
            lang_selected = dict_series.get(tvshow, {}).get(TAG_LANGUAGE, "")
            dict_series.pop(tvshow, None)

            result, json_data = jsontools.update_node(dict_series, item.from_channel, TAG_TVSHOW_FILTER)

            sound = False
            if result:
                message = "FILTRO ELIMINADO"
            else:
                message = "Error al guardar en disco"
                sound = True

            heading = "%s [%s]" % (tvshow.title(), lang_selected)
            platformtools.dialog_notification(heading, message, sound=sound)

            if item.from_action in ["findvideos", "play", "no_filter"]:  # 'no_filter' es el mismo caso que L#601
                platformtools.itemlist_refresh()


def save(item, dict_data_saved):
    """
    Guarda los valores configurados en la ventana

    @param item: item
    @type item: Item
    @param dict_data_saved: diccionario con los datos salvados
    @type dict_data_saved: dict
    """
    logger.info()

    if item and dict_data_saved:
        logger.debug('item: %s\ndatos: %s' % (item.tostring(), dict_data_saved))

        if item.from_channel == "videolibrary":
            item.from_channel = item.contentChannel
        dict_series = jsontools.get_node_from_file(item.from_channel, TAG_TVSHOW_FILTER)
        
        tvshow = normalize(item.show)
        if dict_series.get(tvshow, {}).get(TAG_TITLE, "") == '*' or dict_data_saved.get(TAG_TITLE, "") == '*':
            tvshow = '*'

        logger.info("Se actualiza los datos de: %s" % tvshow)
        
        title_selected = str(dict_data_saved.get(TAG_TITLE, item.season_search or tvshow.title))

        list_quality = []
        for _id, value in list(dict_data_saved.items()):
            if _id in item.list_quality and value:
                list_quality.append(_id.lower())

        lang_selected = item.list_language[dict_data_saved[TAG_LANGUAGE]]
        dict_filter = {TAG_NAME: tvshow.title(), TAG_ACTIVE: dict_data_saved.get(TAG_ACTIVE, True),
                       TAG_TITLE: title_selected, TAG_LANGUAGE: lang_selected, TAG_QUALITY_ALLOWED: list_quality}
        dict_series[tvshow] = dict_filter

        result, json_data = jsontools.update_node(dict_series, item.from_channel, TAG_TVSHOW_FILTER)

        sound = False
        if result:
            message = "FILTRO GUARDADO"
        else:
            message = "Error al guardar en disco"
            sound = True

        heading = "%s [%s]" % (tvshow.title(), lang_selected)
        platformtools.dialog_notification(heading, message, sound=sound)

        if item.from_action in ["findvideos", "play", "no_filter"]:  # 'no_filter' es el mismo caso que L#601
            platformtools.itemlist_refresh()


def save_from_context(item):
    """
    Salva el filtro a través del menú contextual

    @param item: item
    @type item: item
    """
    logger.info()

    if item.from_channel == "videolibrary":
        item.from_channel = item.contentChannel
    dict_series = jsontools.get_node_from_file(item.from_channel, TAG_TVSHOW_FILTER)
    tvshow = normalize(item.show)

    language = item.language[0] if isinstance(item.language, list) else item.language
    
    dict_filter = {TAG_NAME: tvshow.title(), TAG_ACTIVE: True, TAG_LANGUAGE: language, TAG_QUALITY_ALLOWED: []}
    dict_series[tvshow] = dict_filter

    result, json_data = jsontools.update_node(dict_series, item.from_channel, TAG_TVSHOW_FILTER)

    sound = False
    if result:
        message = "FILTRO GUARDADO"
    else:
        message = "Error al guardar en disco"
        sound = True

    heading = "%s [%s]" % (tvshow.title(), language)
    platformtools.dialog_notification(heading, message, sound=sound)

    if item.from_action in ["findvideos", "play", "no_filter"]:  # 'no_filter' es el mismo caso que L#601
        platformtools.itemlist_refresh()


def delete_from_context(item):
    """
    Elimina el filtro a través del menú contextual

    @param item: item
    @type item: item
    """
    logger.info()

    # venimos desde get_links y no se ha obtenido ningún resultado, en menu contextual y damos a borrar
    if item.to_channel:
        item.from_channel = item.to_channel
    if item.from_channel == "videolibrary":
        item.from_channel = item.contentChannel

    dict_series = jsontools.get_node_from_file(item.from_channel, TAG_TVSHOW_FILTER)
    if str(item.show).startswith('*'):
        tvshow = '*'
    else:
        tvshow = normalize(item.show)
        if tvshow not in dict_series.keys():
            tvshow = '*'

    lang_selected = dict_series.get(tvshow, {}).get(TAG_LANGUAGE, "")
    dict_series.pop(tvshow, None)

    result, json_data = jsontools.update_node(dict_series, item.from_channel, TAG_TVSHOW_FILTER)

    sound = False
    if result:
        message = "FILTRO ELIMINADO"
    else:
        message = "Error al guardar en disco"
        sound = True

    heading = "%s [%s]" % (tvshow.title(), lang_selected)
    platformtools.dialog_notification(heading, message, sound=sound)

    if item.from_action in ["findvideos", "play", "no_filter"]:  # 'no_filter' es el mismo caso que L#601
        platformtools.itemlist_refresh()


def get_season_search(item, dict_series={}):

    tvshow = normalize(item.show)
    item.season_search = item.season_search.title() or tvshow.title()
    
    # OBTENEMOS LOS DATOS DEL JSON
    channel = item.contentChannel if item.contentChannel and item.contentChannel not in ['list', 'videolibrary'] else None \
                                  or item.from_channel if item.from_channel and item.from_channel not in ['list', 'videolibrary'] else None \
                                  or item.channel
    if channel:
        if not dict_series: dict_series = jsontools.get_node_from_file(channel, TAG_TVSHOW_FILTER)

        if dict_series and dict_series.get(tvshow, {}).get(TAG_TITLE, ""):
            if dict_series[tvshow][TAG_TITLE] != '*':
                item.season_search = dict_series[tvshow][TAG_TITLE]
