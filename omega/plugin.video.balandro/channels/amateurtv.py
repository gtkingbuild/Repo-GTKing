# -*- coding: utf-8 -*-

import re, traceback

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

    if config.get_setting('descartar_xxx', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    # ~ itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/a/0/50/es/' ))

    itemlist.append(item.clone( title = 'Mujeres', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/w/0/50/es/' ))
    itemlist.append(item.clone( title = 'Hombres', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/m/0/50/es/' ))
    itemlist.append(item.clone( title = 'Parejas', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/c/0/50/es/' ))
    itemlist.append(item.clone( title = 'Transexuales', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/t/0/50/es/' ))
    itemlist.append(item.clone( title = 'Privados', action = 'list_all', url = host  + '/v3/readmodel/cache/cams/p/0/50/es/' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host  + '/v3/tag/list' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    jdata = jsontools.load(data)

    data = jdata['body']

    for elem in data['tags']:
        url = ''

        try:
            title = elem.get('tag', '')
            url = '%s/v3/readmodel/cache/sectioncamlist?genre=["w","m","c","t"]&tag=%s' % (host, title)
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not url: continue

        title = title.capitalize()

        itemlist.append(item.clone (action='list_list', title=title, url=url, text_color='tan' ))
    
    return sorted(itemlist,key=lambda x: x.title)


def list_list(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    jdata = jsontools.load(data)

    data = jdata['body']

    for elem in data['cams']:
        id = elem['id']
        online = elem['online']
        name = elem['username']
        thumb = elem['avatar']
        age = elem['ages']
        country  = elem['countryName']

        thumb = host + thumb

        titulo = name.replace('_', '').capitalize()

        if country: titulo = titulo + ' [COLOR orange]' + str(country).lower() + '[/COLOR]'

        if age:
           if not str(age) == '[None]':
               age = str(age).replace('[', '').replace(']', '')
               titulo = titulo + ' (edad ' + str(age) + ')'

        if not online: titulo += '[COLOR moccasin]Off[/COLOR] ' + titulo

        url = '%s/v3/readmodel/show/%s/es/' % (host, name)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, other=titulo, online=online,
                                    contentType = 'movie', contentTitle = name, contentExtra='adults' ))

    if itemlist:
        try:
           count = data['totalCount']
           current_page = scrapertools.find_single_match(item.url, ".*?/(\d+)/50/")
           current_page = int(current_page)

           if current_page <= int(count) and (int(count) - current_page) > 50:
               current_page += 50

               next_page = re.sub(r"\d+/50/", "{0}/50/".format(current_page), item.url)

               if next_page:
                   itemlist.append(item.clone (action='list_list', title='Siguientes ...', url=next_page, text_color = 'coral') )
        except:
           pass

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

        titulo = name.replace('_', '').capitalize()

        if country: titulo = titulo + ' [COLOR orange]' + str(country).lower() + '[/COLOR]'

        if age:
           if not str(age) == '[None]':
               age = str(age).replace('[', '').replace(']', '')
               titulo = titulo + ' (edad ' + str(age) + ')'

        if not online: titulo += '[COLOR moccasin]Off[/COLOR] ' + titulo

        url = '%s/v3/readmodel/show/%s/es/' % (host, name)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, other=titulo, online=online,
                                    contentType = 'movie', contentTitle = name, contentExtra='adults' ))

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
            itemlist.append(Item( channel = item.channel, action = 'play', title='', url = url, server = 'directo', ref = item.url, other = item.other ))
    except:
        if not item.online:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]El vídeo está Off line[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.ref)
    jdata = jsontools.load(data)

    try:
        qualities = jdata['qualities']

        qltys = scrapertools.find_multiple_matches(str(qualities), "x(.*?)'")

        for qlty in qltys:
            url = item.url
            url += '|ignore_response_code=True'

            itemlist.append(["%s" % qlty, url])
    except:
        url = item.url
        url += '|ignore_response_code=True'

        itemlist.append(Item( channel = item.channel, server = 'directo', url = url ))

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
