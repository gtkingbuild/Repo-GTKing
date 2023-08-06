# -*- coding: utf-8 -*-
# -*- Channel Community -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from core import httptools
from core import scrapertools
from core import servertools
from core import jsontools
from core import filetools
from channelselector import get_thumb
from core import tmdb
from core.item import Item
from platformcode import logger, config, platformtools
from modules import autoplay
from channels import filtertools

list_data = {}

list_language = ['LAT', 'CAST', 'VO', 'VOSE']
list_servers = ['directo']
list_quality = ['SD', '720', '1080', '4k']


def mainlist(item):
    logger.info()

    path = filetools.join(config.get_data_path(), 'community_channels.json')
    if not filetools.exists(path):
        res = filetools.write(path, '{"channels":{}}', silent=True)
    autoplay.init(item.channel, list_servers, list_quality)

    return show_channels(item)


def show_channels(item):
    logger.info()
    itemlist = []

    context = [{"title": "Eliminar este canal",
                 "action": "remove_channel",
                 "channel": "community"}]

    path = filetools.join(config.get_data_path(), 'community_channels.json')
    json = jsontools.load(filetools.read(path))

    itemlist.append(Item(channel=item.channel, title='Agregar un canal', action='add_channel', thumbnail=get_thumb('add.png')))

    for key, channel in list(json['channels'].items()):

        if 'poster' in channel:
            poster = channel['poster']
        else:
            poster = ''

        itemlist.append(Item(channel=item.channel, title=channel['channel_name'], url=channel['path'],
                             thumbnail=poster, action='show_menu', channel_id = key, context=context))
    return itemlist


def load_json(item):
    logger.info()

    if item.url.startswith('http'):
        json_file = httptools.downloadpage(item.url).data
    else:
        json_file = filetools.read(item.url)

    json_data = jsontools.load(json_file)

    return json_data


def show_menu(item):
    global list_data
    logger.info()
    itemlist = []

    if not item.results:
        json_data = load_json(item)
    else:
        json_data = item.results

    if "menu" in json_data:
        for option in json_data['menu']:
            if 'buscar' in option['title'].lower():
                action = 'finder'
            else:
                action = 'show_menu'
            itemlist.append(Item(channel=item.channel, title=option['title'], action=action, url=option['link']))
        autoplay.show_option(item.channel, itemlist)
        return itemlist

    if "movies_list" in json_data:
        item.media_type='movies_list'
        item.first = 0

    elif "tvshows_list" in json_data:
        item.media_type = 'tvshows_list'
        item.first = 0
    elif "episodes_list" in json_data:
        item.media_type = 'episodes_list'

    return list_all(item)


    return itemlist


def list_all(item):
    logger.info()

    itemlist = []
    next = False
    media_type = item.media_type

    if not item.results:
        json_data = load_json(item)
    else:
        json_data = item.results

    first = item.first
    last = first + 19
    if last > len(json_data[media_type]):
        last = len(json_data[media_type])
    else:
        next = True

    for media in json_data[media_type][first:last]:

        quality, language, plot, poster = set_extra_values(media)

        title = media['title']
        title = set_title(title, language, quality)

        new_item = Item(channel=item.channel, title=title, quality=quality,
                        language=language, plot=plot, thumbnail=poster)


        if 'movies_list' in json_data:
            new_item.url = media
            new_item.contentTitle = media['title']
            new_item.action = 'findvideos'
            if 'year' in media:
                new_item.infoLabels['year'] = media['year']
        else:
            new_item.url = media['seasons_list']
            new_item.contentSerieName = media['title']
            new_item.action = 'seasons'

        itemlist.append(new_item)

    tmdb.set_infoLabels(itemlist, seekTmdb=True)

    # Pagination

    if next:
        first = last
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=item.url, action='list_all',
                         media_type=item.media_type, results=item.results, first=first))

    return itemlist


def seasons(item):
    logger.info()
    itemlist = []
    infoLabels = item.infoLabels
    list_seasons = item.url
    for season in list_seasons:
        infoLabels['season'] = season['season']
        title = 'Temporada %s' % season['season']
        itemlist.append(Item(channel=item.channel, title=title, url=season['link'], action='episodesxseason',
                             contentSeasonNumber=season['season'], infoLabels=infoLabels))

    tmdb.set_infoLabels(itemlist, seekTmdb=True)
    itemlist = sorted(itemlist, key=lambda i: i.title)

    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = []
    json_data = load_json(item)
    infoLabels = item.infoLabels

    season_number = infoLabels['season']
    for episode in json_data['episodes_list']:
        episode_number = episode['number']
        infoLabels['season'] = season_number
        infoLabels['episode'] = episode_number

        title = '%sx%s - Episodio %s' % (season_number, episode_number, episode_number)

        itemlist.append(Item(channel=item.channel, title=title, url=episode, action='findvideos',
                             contentEpisodeNumber=episode_number, infoLabels=infoLabels))

    tmdb.set_infoLabels(itemlist, seekTmdb=True)
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    for url in item.url['links']:
        quality, language, plot, poster = set_extra_values(url)
        title = ''
        title = set_title(title, language, quality)

        itemlist.append(Item(channel=item.channel, title='%s'+title, url=url['url'], action='play', quality=quality,
                             language=language, infoLabels = item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def add_channel(item):
    logger.info()
    import xbmc
    import xbmcgui
    channel_to_add = {}
    json_file = ''
    result = platformtools.dialog_select('Agregar un canal', ['Desde archivo local', 'Desde URL'])
    if result == -1:
        return
    if result==0:
        file_path = xbmcgui.Dialog().browseSingle(1, 'Alfa - (Comunidad)', 'files')
        try:
            channel_to_add['path'] = file_path
            json_file = jsontools.load(filetools.read(file_path))
            channel_to_add['channel_name'] = json_file['channel_name']
            if "poster" in json_file:
                channel_to_add['poster'] = json_file['poster']
        except:
            pass

    elif result==1:
        url = platformtools.dialog_input("", 'Ingresa la URL del canal', False)
        try:
            channel_to_add['path'] = url
            json_file = jsontools.load(httptools.downloadpage(url).data)
        except:
            pass

    if len(json_file) == 0:
        return
    if "episodes_list" in json_file:
        platformtools.dialog_ok('Alfa', 'No es posible agregar este tipo de canal')
        return
    channel_to_add['channel_name'] = json_file['channel_name']
    path = filetools.join(config.get_data_path(), 'community_channels.json')

    community_json = jsontools.load(filetools.read(path))
    id = len(community_json['channels']) + 1
    community_json['channels'][id]=(channel_to_add)

    res = filetools.write(path, jsontools.dump(community_json), silent=True)

    platformtools.dialog_notification('Alfa', '%s se ha agregado' % json_file['channel_name'])
    platformtools.itemlist_refresh()
    return


def remove_channel(item):
    logger.info()
    import xbmc
    import xbmcgui
    path = filetools.join(config.get_data_path(), 'community_channels.json')

    community_json = open(path, "r")
    community_json = jsontools.load(community_json.read())

    id = item.channel_id
    to_delete = community_json['channels'][id]['channel_name']
    del community_json['channels'][id]
    res = filetools.write(path, jsontools.dump(community_json), silent=True)

    platformtools.dialog_notification('Alfa', '%s ha sido eliminado' % to_delete)
    platformtools.itemlist_refresh()
    return


def set_extra_values(dict):
    logger.info()
    quality = ''
    language = ''
    plot = ''
    poster = ''

    if 'quality' in dict and dict['quality'] != '':
        quality = dict['quality'].upper()
    if 'language' in dict and dict['language'] != '':
        language = dict['language'].upper()
    if 'plot' in dict and dict['plot'] != '':
        plot = dict['plot']
    if 'poster' in dict and dict['poster'] != '':
        poster = dict['poster']

    return quality, language, plot, poster


def set_title(title, language, quality):
    logger.info()

    if not config.get_setting('unify'):
        if quality != '':
            title += ' [%s]' % quality
        if language != '':
            if not isinstance(language, list):
                title += ' [%s]' % language.upper()
            else:
                title += ' '
                for lang in language:
                    title += '[%s]' % lang.upper()

    return title.capitalize()


def finder(item):
    logger.info()

    keywords = platformtools.dialog_input()
    results = dict()
    json_data = load_json(item)

    if 'movies_list' in json_data:
        json_data = json_data['movies_list']
        item.media_type = 'movies_list'
    elif 'tvshows_list' in json_data:
        json_data = json_data['tvshows_list']
        item.media_type = 'tvshows_list'
    else:
        return
    
    string_list = list()

    for s in keywords.split(' '):
        if len(s) > 3:
            string_list.append(s)

    results[item.media_type] = [c for s in string_list for c in json_data if s.lower() in c['title'].lower()]
    item.results = results
    return show_menu(item)
