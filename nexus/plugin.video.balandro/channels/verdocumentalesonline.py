# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urllib
else:
    import urllib.parse as urllib


import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, jsontools


host = "https://www.dailymotion.com/verdocumentalesonline"

# ~ Id: x24nyzt
# ~ https://developer.dailymotion.com/tools/


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', group = 'vistos' ))

    itemlist.append(item.clone( title = 'Por lista', action = 'list_playlists' ))

    return itemlist


def list_playlists(item):
    logger.info()
    itemlist = []

    perpage = 20
    if not item.page: item.page = 1

    url = 'https://api.dailymotion.com/playlists?owner=x24nyzt&limit=%d&page=%d&sort=alpha' % (perpage, item.page)
    url += '&fields=id%2Cname%2Cthumbnail_480_url%2Cdescription%2Cvideos_total'

    try:
        data = httptools.downloadpage(url).data
        data = jsontools.load(data)

        for vid in data['list']:
            if vid['videos_total'] == 0: continue

            title = '%s [COLOR tan](%d vídeos)[/COLOR]' % (vid['name'], vid['videos_total'])
            plot = '' if not vid['description'] else scrapertools.htmlclean(vid['description'])

            itemlist.append(item.clone( action='list_all', title=title, playlist_id=vid['id'], page=1, thumbnail=vid['thumbnail_480_url'], plot=plot, text_color = 'cyan' ))

        if itemlist:
            if data['has_more']:
                itemlist.append(item.clone( title='Siguientes ...', action='list_playlists', page = item.page + 1, text_color='coral'))
    except:
        pass

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    perpage = 20
    if not item.page: item.page = 1

    if item.playlist_id: url = 'https://api.dailymotion.com/playlist/%s/videos' % item.playlist_id
    else: url = 'https://api.dailymotion.com/user/x24nyzt/videos'

    if item.group == 'vistos':
         url += '?limit=%d&page=%d&sort=visited' % (perpage, item.page)
    else:
        url += '?limit=%d&page=%d&sort=recent' % (perpage, item.page)

    url += '&fields=title%2Cthumbnail_url%2Cdescription%2Cembed_url%2Cduration'
    if item.search_text: url += '&search=' + urllib.quote_plus(item.search_text)

    try:
        data = httptools.downloadpage(url).data
        data = jsontools.load(data)

        for vid in data['list']:
            vid['title'] = re.sub('-\s*documental.*$', '', vid['title'], flags=re.I)
            vid['title'] = re.sub('[-| ]+$', '', vid['title'])
            title = '[COLOR tan](%s)[/COLOR] %s' % (config.format_seconds_to_duration(vid['duration']), vid['title'])
            plot = '' if not vid['description'] else scrapertools.htmlclean(vid['description'])

            itemlist.append(item.clone( action='findvideos', url=vid['embed_url'], title=title, thumbnail=vid['thumbnail_url'], plot=plot,
                                        contentType='movie', contentTitle=vid['title'], contentExtra='documentary' ))

        if itemlist:
            if data['has_more']:
                itemlist.append(item.clone( title='Siguientes ...', action='list_all', page = item.page + 1, text_color='coral' ))
    except:
        pass

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    itemlist.append(Item( channel = item.channel, action = 'play', server='dailymotion', title = '', url = item.url, language = 'Esp' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        return list_all(item.clone(search_text=texto))
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
