# -*- coding: utf-8 -*-

import re, traceback

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools


host = 'https://www.cam4.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_xxx', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    # ~ itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', search_video = 'adult', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'directoryCams?directoryJson=true&online=true&url=true&page=1' ))

    itemlist.append(item.clone( title = 'Mujeres', action = 'list_all', url = host + 'directoryCams?directoryJson=true&online=true&url=true&gender=female&broadcastType=female_group&broadcastType=solo&broadcastType=male_female_group&page=1' ))
    itemlist.append(item.clone( title = 'Hombres', action = 'list_all', url = host + 'directoryCams?directoryJson=true&online=true&url=true&gender=male&broadcastType=male_group&broadcastType=solo&page=1' ))
    itemlist.append(item.clone( title = 'Parejas', action = 'list_all', url = host + 'directoryCams?directoryJson=true&online=true&url=true&broadcastType=female_group&broadcastType=male_female_group&page=1' ))
    itemlist.append(item.clone( title = 'Transsexuales', action = 'list_all', url = host + 'directoryCams?directoryJson=true&online=true&url=true&gender=shemale&page=1' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|#038;", "", data)

    jdata = jsontools.load(data)

    for Video in jdata['users']:
        title = Video['username']
        country = Video['countryCode']
        thumb = Video['snapshotImageLink']
        url = Video['hlsPreviewUrl']
        age = Video['age']

        titulo = title

        if country: titulo = titulo + ' [COLOR violet]' + str(country).capitalize() + '[/COLOR]'

        if age:
           if not str(age) == '[None]':
               age = str(age).replace('[', '').replace(']', '')
               titulo = titulo + ' (edad ' + str(age) + ')'

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, other=titulo, contentType = 'movie', contentExtra='adults' ))

    if itemlist:
        next_page = ''

        act_page = scrapertools.find_single_match(item.url, "(.*?=)\d+$")
        current_page = scrapertools.find_single_match(item.url, ".*?&page=(\d+)$")

        if current_page:
            current_page = int(current_page)
            current_page += 1
            next_page = act_page + str(current_page)

            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if not item.url: return itemlist

    elif '//stackvaults' in item.url: return itemlist

    itemlist.append(Item( channel = item.channel, action = 'play', title='', url = item.url, server = 'directo', other = item.other ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        config.set_setting('search_last_video', texto)

        item.url =  host + 'directoryCams?directoryJson=true&online=true&url=true&showTag=%s&page=1' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
