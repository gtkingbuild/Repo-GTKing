# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, jsontools, servertools, tmdb

from core.jsontools import json


host = 'https://peliculasflix.co/'


api = 'https://fluxcedene.net/api/gql'


access_platform = 'lDakkGUZx7_nX25Nv1CJVbz_ZAjMKMTcwNTQyMzU4Nw=='


perpage = 32


def do_downloadpage(query):
    post = json.dumps(query)

    headers = {'Referer': host, 'Content-Type': 'application/json', 'x-access-platform': access_platform}

    resp = httptools.downloadpage(api, headers=headers, post=post)

    try: return json.loads(resp.data)
    except: return ''


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', _type = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'productoras' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    query = {
            "variables": {},
            "query": "{\n"
            +" listGenres(filter: {platform: \"peliculasgo\"}, sort: NUMBER_DESC) {\n"
            +" name\n"
            +" _id\n"
            +" slug\n"
            +" platforms {\n"
            +" _id\n"
            +" platform\n"
            +" number\n"
            +" image_default\n"
            +" image_tmdb\n"
            +" image_custom\n"
            +" __typename\n"
            +" }\n"
            +" __typename\n"
            +" }\n"
            +"}\n"
            }

    jdata = do_downloadpage(query)

    if not jdata: return itemlist

    try:
       for genre in jdata['data']['listGenres']:
           itemlist.append(item.clone( title = genre['name'], slug = genre['slug'], url = host, action = 'list_all', text_color = 'deepskyblue' ))
    except:
       return itemlist

    return sorted(itemlist, key=(lambda x: x.title))


def categorias(item):
    logger.info()
    itemlist = []

    query = {
            "variables": {},
            "query": " {\n"
            +" listLabels(filter: {platform: \"peliculasgo\"}, sort: NUMBER_DESC) {\n"
            +" _id\n"
            +" name\n"
            +" slug\n"
            +" platforms {\n"
            +" _id\n"
            +" platform\n"
            +" number\n"
            +" image_default\n"
            +" image_tmdb\n"
            +" image_custom\n"
            +" __typename\n"
            +" }\n"
            +" __typename\n"
            +" }\n"
            +"}",
            "filter_key": "labelId",
            "filter_val": "_id"
            }

    jdata = do_downloadpage(query)

    if not jdata: return itemlist

    try:
       for label in jdata['data']['listLabels']:
           title = label['name']

           if title == 'Eróticas':
               if config.get_setting('descartar_xxx', default=False): continue

           if 'Estrenos' in title: continue
           elif 'Premios' in title: continue

           elif title == 'aventura': title = 'Aventura'

           itemlist.append(item.clone( title = title, label_id = label['_id'], url = host, action = 'list_all', text_color = 'deepskyblue' ))
    except:
       return itemlist

    return sorted(itemlist, key=(lambda x: x.title))


def productoras(item):
    logger.info()
    itemlist = []

    query = {
            "variables": {},
            "query": "{\n"
            +" listNetworks(filter: {platform: \"peliculasgo\"}, sort: NUMBER_DESC) {\n"
            +" name\n"
            +" _id\n"
            +" slug\n"
            +" platforms {\n"
            +" _id\n"
            +" platform\n"
            +" number\n"
            +" image_default\n"
            +" image_tmdb\n"
            +" image_custom\n"
            +" __typename\n"
            +" }\n"
            +"  __typename\n"
            +" }\n"
            +"}\n"
            }

    jdata = do_downloadpage(query)

    if not jdata: return itemlist

    try:
       for network in jdata['data']['listNetworks']:
           title = network['name']

           if title == 'tvN': title = 'Tvn'

           itemlist.append(item.clone( title = title, net_slug = network['slug'], url = host, action = 'list_all', text_color = 'deepskyblue' ))
    except:
       return itemlist

    return sorted(itemlist, key=(lambda x: x.title))


def idiomas(item):
    logger.info()
    itemlist = []

    languages = get_idiomas()

    for lang in languages:
        itemlist.append(item.clone( title = lang['name'], code_flix = lang['code_flix'], url = host, action = 'list_all', text_color = 'moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    filters = {}

    filters["isPublish"] = True

    if item.slug: filters["genres"] = [{'slug': item.slug}]

    elif item.net_slug: filters["networks"] = [{'slug': item.net_slug}]

    elif item.label_id: filters["labelId"] = str(item.label_id)

    if item.code_flix: filters["bylanguages"] = [str(item.code_flix)]

    query = {
            "operationName": "listMovies",
            "variables": {"perPage": perpage, "sort":"CREATEDAT_DESC", "filter": filters, "page": item.page},
            "query": "query listMovies($page: Int, $perPage: Int, $sort: SortFindManyFilmInput, $filter: FilterFindManyFilmInput) {\n"
            +" paginationFilm(page: $page, perPage: $perPage, sort: $sort, filter: $filter) {\n"
            +" count\n"
            +" pageInfo {\n"
            +" currentPage\n"
            +" hasNextPage\n"
            +" hasPreviousPage\n"
            +" __typename\n"
            +" }\n"
            +" items {\n"
            +" _id\n"
            +" title\n"
            +" name\n"
            +" overview\n"
            +" runtime\n"
            +" slug\n"
            +" name_es\n"
            +" poster_path\n"
            +" poster\n"
            +" languages\n"
            +" release_date\n"
            +" __typename\n"
            +" }\n"
            +" __typename\n"
            +" }\n"
            +"}\n"
            }

    return list_query(item, query)


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose'}

    query = {
            "operationName": "detailFilm",
            "variables": {"slug": item.slug},
            "query": "query detailFilm($slug: String!) {\n  detailFilm(filter: {slug: $slug}) {\n"
            +" name\n"
            +" title\n"
            +" name_es\n"
            +" overview\n"
            +" languages\n"
            +" popularity\n"
            +" backdrop_path\n"
            +" backdrop\n"
            +" links_online {\n"
            +" _id\n"
            +" server\n"
            +" lang\n"
            +" link\n"
            +" page\n"
            +" __typename\n"
            +" }\n"
            +" __typename\n"
            +" }\n"
            +"}\n"}

    jdata = do_downloadpage(query)

    if not jdata: return itemlist

    ses = 0

    try:
       videos = jdata['data']['detailFilm']['links_online']
    except:
       return itemlist

    if not videos: return itemlist

    for video in videos:
        ses += 1

        lang = get_lang(video['lang'])

        url = video['link']

        if '/pelisplus.' in url: continue
        elif '/fplayer.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        other = ''

        if servidor == 'various': other = servertools.corregir_other(url)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                  language = IDIOMAS.get(lang, lang), quality = 'HD', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def list_query(item, query):
    logger.info()
    itemlist = []

    thumb = 'https://image.tmdb.org/t/p/original{}'

    jdata = do_downloadpage(query)

    if not jdata: return itemlist

    try:
       if item._type == 'search':
           datos = jdata['data']['searchFilm']
           pages = []
       else:
           datos = jdata['data']['paginationFilm']['items']
           pages = jdata['data']['paginationFilm']['pageInfo']
    except:
       return itemlist

    if not datos: return itemlist

    for peli in datos:
        if not peli.get('languages','') or not any(peli['languages']): continue

        item_args = {}

        item_args['channel'] = item.channel
        item_args['slug'] = peli['slug']
        item_args['language'] = get_languages(peli['languages'])
        item_args['contentType'] = 'movie'
        item_args['contentTitle'] = peli['name']
        item_args['title'] = peli['name']
        item_args['action'] = 'findvideos'
        item_args['thumbnail'] = thumb.format(peli['poster_path'])

        new_item = Item(**item_args)

        tmdb.set_infoLabels_item(new_item)

        new_item.infoLabels['year'] = '-'
        new_item.infoLabels['plot'] = peli['overview']

        itemlist.append(new_item)

    tmdb.set_infoLabels(itemlist)

    if pages:
       if pages['hasNextPage']:
           page = pages['currentPage'] + 1

           itemlist.append(item.clone( action="list_all", title='Siguientes ...',  page=page, text_color='coral' ))

    return itemlist


def get_idiomas():
    logger.info()

    idiomas = [
              {"code_flix": "37", "name": "Castellano"},
              {"code_flix": "38", "name": "Latino" },
              {"code_flix": "192", "name": "Subtitulado" }
              ]

    return idiomas


def get_languages(codes):
    logger.info()

    langs = []

    languages = get_idiomas()

    for code in codes:
        try:
            if code == 'en': langs.append('subtitulado')
            else:
               if PY3:
                   langs.append(next(filter(lambda lang: lang['code_flix'] == code, languages))['name'])
               else:
                   langs.append(filter(lambda lang: lang['code_flix'] == code, languages)[0]['name'])
        except:
            pass

    return langs


def get_lang(code):
    logger.info()

    languages = get_idiomas()

    if code == 'en': return 'subtitulado'

    if PY3:
        return next(filter(lambda lang: lang['code_flix'] == code, languages))['name']
    else:
        return filter(lambda lang: lang['code_flix'] == code, languages)[0]['name']


def search(item, texto):
    logger.info()
    try:
       if not item._type: item._type = 'search'

       query = {
               "operationName": "searchAll",
               "variables": {"input": texto},
               "query": "query searchAll($input: String!) {\n"
               +" searchFilm(input: $input, limit: 10) {\n"
               +" _id\n"
               +"  slug\n"
               +"  title\n"
               +"  name\n"
               +"  overview\n"
               +"  languages\n"
               +"  name_es\n"
               +"  poster_path\n"
               +"  poster\n"
               +"  __typename\n"
               +"  }\n"
               +"}\n"
               }

       return list_query(item, query)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
