# -*- coding: utf-8 -*-
# -*- Channel New News -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import channelselector
from core.item import Item
from core import channeltools
from core import tmdb
from core import jsontools
from platformcode import logger
from platformcode import config
from platformcode import help_window
from platformcode import platformtools
from channelselector import get_thumb
from concurrent import futures
import math
import os
import datetime


workers = [None, 1, 2, 4, 6, 8, 16, 24, 32, 64]
max_workers = config.get_setting("max_workers", "news")
max_workers = workers[max_workers]
all_channels = []


def mainlist(item):
    logger.info()
    itemlist = list()

    list_items = [[30122, "peliculas", "channels_movie.png" ],
                 [70208, "4k", "channels_movie_4k.png"],
                 [70209, "terror", "channels_horror.png"],
                 [60510, "infantiles", "channels_children.png"],
                 [60511, "series", "channels_tvshow.png"],
                 [60512, "anime", "channels_anime.png"],
                 [70014, "castellano", "channels_spanish.png"],
                 [59976, "latino", "channels_latino.png"],
                 [70171, "torrent", "channels_torrent.png"],
                 [60513, "documentales", "channels_documentary.png"]
                ]

    for it in list_items:

        thumbnail = get_thumb(it[2])
        new_item = Item(channel=item.channel, action="news", news=it[1], title=config.get_localized_string(it[0]),
                    thumbnail=thumbnail)
        set_category_context(new_item)
        itemlist.append(new_item)
    itemlist.append(Item(channel="news", title="Configuración", action="news_setting",
                         thumbnail=get_thumb("setting_0.png")))
    help_window.show_info("news")
    return itemlist


def set_category_context(item):
    item.context = [{"title": config.get_localized_string(60514) % item.title,
                     "news": item.news,
                     "action": "setting_channel",
                     "channel": item.channel},
                    {"title": "Ver canales de esta categoría",
                     "category": item.news,
                     "action": "list_channels",
                     "channel": item.channel,
                     "switch_to": True}
                    ]
    item.category = config.get_localized_string(60679) % item.news


def news(item):
    logger.info()
    channel_list = list()
    channel_list.extend(get_channels(item.news))
    valid_channels_number = len(channel_list)
    limit = len(channel_list)
    next = False

    if not channel_list:
        platformtools.dialog_ok('Novedades - %s' % item.news, 'No se ha definido ningun canal para la '
                                                               'busqueda.', 'Utilice el menu contextual '
                                                                            'para agregar al menos uno')
        return
    if len(channel_list) > 20:
        next = True

    if len(channel_list) > 40:
        limit = int(len(channel_list) * 30 / 100)
    elif len(channel_list) > 20:
        limit = int(len(channel_list) * 50 / 100)

    clear_cache(item.news)

    itemlist = process(channel_list[:limit], item.category, item.news, valid_channels_number, item.startpage)
    try:
        itemlist = sorted(group_results(itemlist), key=lambda i: int(i.infoLabels["year"]), reverse=True)
    except:
        pass

    if len(channel_list) > 20:
        executor = futures.ThreadPoolExecutor(max_workers=max_workers)
        executor.submit(process, channel_list[limit + 1:], item.category, item.news, valid_channels_number, True, True)
        executor.shutdown(wait=False)

    if itemlist and next:
        next_icon = get_thumb('more.png')
        next = item.clone(action="load_results", viewmode="movie", thumbnail=next_icon, title='Siguiente >>>')
        itemlist.insert(len(itemlist), next)
    return itemlist


def process(channel_list, category, news, total_channels, startpage=False, save=False):

    itemlist = list()
    searching = list()
    searching_titles = list()

    number_of_channels = float(100) / len(channel_list)

    if '4k' not in category: 
        config.set_setting('tmdb_active', False)

    searching += channel_list
    searching_titles += channel_list
    cnt = 0

    if not startpage:
       progress = platformtools.dialog_progress("%s (%s) Seleccionados " % (category, total_channels),
                                                "Obteniendo novedades. Por favor espere...")

    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        c_results = [executor.submit(get_channel_news, ch, news) for ch in channel_list]

        for index, res in enumerate(futures.as_completed(c_results)):
            cnt += 1
            percentage = int(math.ceil((index + 1) * number_of_channels))
            try:
                finished = res.result()[0]
            except:
                continue

            if not startpage:
               if progress.iscanceled():
                   break

            if finished in searching:
                searching_titles.remove(searching_titles[searching.index(finished)])
                searching.remove(finished)
            if not startpage:
                progress.update(percentage, "Obteniendo novedades. Por favor espere..." +
                                '\n' + str(searching_titles) + '\n' + ' ' + '\n' + ' ' + '\n' + ' ')

            if len(res.result()) > 1:
                if save:
                    save_results(finished, res.result()[1], news)
                else:
                    itemlist += res.result()[1]


    if not startpage:
       progress.close()

    config.set_setting('tmdb_active', True)
    return itemlist


def get_channels(category, all=False):
    logger.info()
    global all_channels

    valid_channels = list()

    all_channels = channelselector.filterchannels('all', settings=False)

    for ch in all_channels:
        channel = ch.channel
        #ch_param = channeltools.get_channel_parameters(channel)

        if not ch.active:
            continue
        valid = config.get_setting("include_in_newest_" + category, channel)
        if valid or (valid is not None and all):
            valid_channels.append(channel)

    return valid_channels


def get_channel_news(channel, category, all=False):

    logger.info()

    results = list()
    brand_new = list()
    if platformtools.is_playing():
        return channel, brand_new, category

    news_range = config.get_setting("news_range", "news")

    if news_range == 5:
        news_range = 100
    #ch_params = channeltools.get_channel_parameters(channel)
    #module = __import__('channels.%s' % ch_params["channel"], fromlist=["channels.%s" % ch_params["channel"]])
    module = __import__('channels.%s' % channel, fromlist=["channels.%s" % channel])
    
    try:
        results = module.newest(category)
    except:
        return channel, results, category

    if not results:
        return channel, results, category

    total_results = len(results)
    results = sorted(results, reverse=True, key=lambda it: (str(it.infoLabels["year"])))

    if not all and news_range != 100:
        if total_results > 40:
            total_results = int((total_results * 20) / 100)
        elif total_results > 20:
            total_results = int((total_results * 50) / 100)


    for elem in results[:total_results]:

        if category not in ["series", "anime"] and not all and news_range != 100:
            if not elem.contentTitle or "-Próximamente-" in elem.title:
                continue
            if elem.infoLabels["year"] and str(elem.infoLabels["year"]).isdigit():
                item_year = int(elem.infoLabels["year"])
                this_year = datetime.date.today().year

                if datetime.date.today().month < 6 and news_range == 0:
                    news_range = 1

                if not item_year in range(this_year - news_range, this_year + 1):
                    continue
            else:
                continue
        elem.channel = channel
        elem.from_channel = channel
        if not all:
            elem.context = [{"title": "[COLOR yellow]Mas novedades[/COLOR]", "action": "get_all_news",
                             "category": category,
                             "channel": "news",
                             "from_channel": channel,
                             "switch_to": True}]

        brand_new.append(elem)

    return channel, brand_new, category


def get_all_news(item):

    itemlist = get_channel_news(item.from_channel, item.category, all=True)[1]

    return itemlist


def group_results(results):
    logger.info

    grouped = dict()
    itemlist = list()
    tmdb.set_infoLabels_itemlist(results, seekTmdb=True)

    for elem in results:

        if not elem.infoLabels["tmdb_id"] or "-Próximamente-" in elem.title:
            continue
        if elem.infoLabels["tmdb_id"] not in grouped:
            grouped[elem.infoLabels["tmdb_id"]] = list()
        grouped[elem.infoLabels["tmdb_id"]].append(elem)

    for key, value in grouped.items():

        if len(value) == 1:
            itemlist.append(value[0])
        else:
            title = '[+]' + value[0].contentTitle.capitalize()
            contentTitle = value[0].contentTitle.capitalize()
            infoLabels = value[0].infoLabels
            itemlist.append(Item(channel="news", title=title, contentTitle=contentTitle, action="show_group",
                                 sub_list=[i.tourl() for i in value], from_channel='', infoLabels=infoLabels,
                                 thumbnail=infoLabels["thumbnail"]))
    return itemlist


def show_group(item):
    itemlist = list()

    for x in item.sub_list:
        itemlist.append(Item().fromurl(x))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    return itemlist


def clear_cache(category):
    menu_cache_path = os.path.join(config.get_data_path(), "settings_channels", 'menu_cache_data.json')
    if os.path.exists(menu_cache_path):
        cache_node = jsontools.get_node_from_file('menu_cache_data.json', 'cached')
        cache_node = dict()
        cache_node[category] = list()
        jsontools.update_node(cache_node, 'menu_cache_data.json', "cached")


def save_results(channel_id, list_result, category):
    menu_cache_path = os.path.join(config.get_data_path(), "settings_channels", 'menu_cache_data.json')
    list_newest = list()
    list_newest_tourl = list()

    if os.path.exists(menu_cache_path):
        cache_node = jsontools.get_node_from_file('menu_cache_data.json', 'cached')
    else:
        cache_node = dict()

    for item in list_result:
        item.channel = channel_id
        list_newest.append(item)
        list_newest_tourl.append(item.tourl())
    if category not in cache_node:
        cache_node[category] = list()
    cache_node[category].extend(list_newest_tourl)
    jsontools.update_node(cache_node, 'menu_cache_data.json', "cached")


def load_results(item):

    cache_node = jsontools.get_node_from_file('menu_cache_data.json', 'cached')
    itemlist = list()

    for cached_item in cache_node[item.news]:
        new_item = Item()
        new_item = new_item.fromurl(cached_item)
        itemlist.append(new_item)
    itemlist = group_results(itemlist)

    return itemlist


def settings(item):
    return platformtools.show_channel_settings(caption=config.get_localized_string(60532))


def setting_channel(item):
    import glob

    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.json')
    channel_language = config.get_setting("channel_language", default="all")

    list_controls = []
    for infile in sorted(glob.glob(channels_path)):

        channel_id = os.path.basename(infile)[:-5]
        channel_parameters = channeltools.get_channel_parameters(channel_id)

        if not channel_parameters["active"]:
            continue

        if channel_parameters["adult"] and config.get_setting("adult_mode") == 0:
            continue

        if channel_language != "all" and channel_language not in channel_parameters["language"] \
                and "*" not in channel_parameters["language"]:
            continue

        include_in_newest = config.get_setting("include_in_newest_" + item.news, channel_id)
        if include_in_newest is None:
            continue

        control = {'id': channel_id,
                   'type': "bool",
                   'label': channel_parameters["title"],
                   'default': include_in_newest,
                   'enabled': True,
                   'visible': True}

        list_controls.append(control)

    caption = config.get_localized_string(60533) + item.title.replace(config.get_localized_string(60525), "- ").strip()
    if config.get_setting("custom_button_value_news", item.channel):
        custom_button_label = config.get_localized_string(59992)
    else:
        custom_button_label = config.get_localized_string(59991)

    return platformtools.show_channel_settings(list_controls=list_controls,
                                               caption=caption,
                                               callback="save_settings", item=item,
                                               custom_button={'visible': True,
                                                              'function': "cb_custom_button",
                                                              'close': False,
                                                              'label': custom_button_label})


def save_settings(item, dict_values):
    for v in dict_values:
        config.set_setting("include_in_newest_" + item.news, dict_values[v], v)


def cb_custom_button(item, dict_values):
    value = config.get_setting("custom_button_value_news", item.channel)
    if value == "":
        value = False

    for v in list(dict_values.keys()):
        dict_values[v] = not value

    if config.set_setting("custom_button_value_news", not value, item.channel) == True:
        return {"label": "Ninguno"}
    else:
        return {"label": "Todos"}


def list_channels(item):
    itemlist = list()
    channels = get_channels(item.category, all=True)

    """
    for ch in channels:
        ch_param = channeltools.get_channel_parameters(ch)
        if ch_param["active"]:
            itemlist.append(Item(channel=ch, action="mainlist", title=ch_param["title"],
                                 thumbnail=ch_param["thumbnail"]))
    """    
    for ch in all_channels:
        if ch.channel in channels and ch.active:
            itemlist.append(Item(channel=ch.channel, action="mainlist", title=ch.title,
                                 thumbnail=ch.thumbnail))

    return itemlist


def news_setting(item):
    platformtools.show_channel_settings()
    return
