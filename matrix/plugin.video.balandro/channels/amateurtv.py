# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools


host = 'https://es.amateur.tv'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    # ~ itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/a/0/50/es/' ))

    itemlist.append(item.clone( title = 'Mujeres', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/w/0/50/es/' ))
    itemlist.append(item.clone( title = 'Hombres', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/m/0/50/es/' ))
    itemlist.append(item.clone( title = 'Parejas', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/c/0/50/es/' ))
    itemlist.append(item.clone( title = 'Transexuales', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/t/0/50/es/' ))

    itemlist.append(item.clone( title = 'Privados', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/p/0/50/es/' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    jdata = jsontools.load(data)

    data = jdata['cams']

    for elem in data['nodes']:
        id = elem['id']
        online = elem['online']
        name = elem['user']['username']
        thumb = elem['imageURL']
        age = elem['user']['age']
        country  = elem['country']

        titulo = name

        if country: titulo = titulo + ' ' + str(country)

        if age: titulo = titulo + ' (Edad ' + str(age) + ')'

        if not online: titulo = '[COLOR plum]Off[/COLOR] ' + titulo

        url = '%s/v3/readmodel/show/%s/es/' % (host, name)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, contentType = 'movie', other = str(country), online = online,
                                    contentTitle = name, contentExtra='adults' ))

    if itemlist:
        try:
           count = data['totalCount']
           current_page = scrapertools.find_single_match(item.url, ".*?/(\d+)/50/")
           current_page = int(current_page)

           if current_page <= int(count) and (int(count) - current_page) > 50:
               current_page += 50

               next_page = re.sub(r"\d+/50/", "{0}/50/".format(current_page), item.url)

               if next_page:
                   itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )
        except:
           pass

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    jdata = jsontools.load(data)

    try:
        url = jdata['videoTechnologies']['fmp4']

        if url:
            url += '|ignore_response_code=True'
            itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server = 'directo', other = item.other ))
    except:
        if not item.online:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]El vídeo está Off line[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + '/?username=%s' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
