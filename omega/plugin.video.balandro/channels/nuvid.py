# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools


host = 'https://www.nuvid.com/'


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

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'search/videos/_empty_/' ))

    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'search/videos/_empty_/', tipo = 'rt' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'search/videos/hd', qlty = '1' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Hetero', action = 'list_cat',  url = host + 'categories', tipo = 'Straight', text_color = 'orange' ))
    itemlist.append(item.clone( title = 'Gays', action = 'list_cat',  url = host + 'categories', tipo = 'Gays', text_color = 'orange' ))
    itemlist.append(item.clone( title = 'Transsexual', action = 'list_cat',  url = host + 'categories', tipo = 'Transsexual', text_color = 'orange' ))

    return itemlist


def list_cat(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    if item.tipo == 'Straight': bloque = scrapertools.find_single_match(data, '>Straight<(.*?)>Gays<')
    elif item.tipo == 'Gays': bloque = scrapertools.find_single_match(data, '>Gays<(.*?)>Transsexual<')
    else: bloque = scrapertools.find_single_match(data, '>Transsexual<(.*?)>Advertisement')

    matches = re.compile('href="(.*?)" >(.*?)<span>', re.DOTALL).findall(bloque)

    for url, title in matches:
        url = host[:-1] + url

        title = title.strip()

        itemlist.append(item.clone (action='list_all', title=title, url=url, text_color='tan' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    qlty = '0'
    if item.qlty: qlty = item.qlty

    filter = 'ch=178.1.2.3.4.191.7.8.5.9.10.169.11.12.13.14.15.16.17.18.28.190.20.21.22.27.23.24.25.26.189.30.31.32.181' \
             '.35.36.37.180.176.38.33.34.39.40.41.42.177.44.43.45.47.48.46.49.50.51.52.53.54.55.56.57.58.179.59.60.61.' \
             '62.63.64.65.66.69.68.71.67.70.72.73.74.75.182.183.77.76.78.79.80.81.82.84.85.88.86.188.87.91.90.92.93.94' \
             '&hq=%s&rate=&dur=&added=&sort=%s' % (qlty, item.tipo)

    header = {'X-Requested-With': 'XMLHttpRequest'}

    if item.tipo != "buscar": header['Cookie'] = 'area=EU; lang=en; search_filter_new=%s' % filter

    data = httptools.downloadpage(item.url, headers=header, cookies=False).data

    patron = '<div class="box-tumb related_vid.*?'
    patron += 'href="([^"]+)" title="([^"]+)".*?'
    patron += 'src="([^"]+)"(.*?)<i class="time">([^<]+)<'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, title, thumb, qlty, duration in matches:
        url = host[:-1] + url

        if not thumb.startswith("https"): thumb = 'https:' + thumb

        titulo = "[COLOR tan]%s[/COLOR] %s" % (duration, title)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="next1">.*?href="([^"]+)"')

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    videos = get_video_url(item.url)

    if not videos:
        platformtools.dialog_notification('Nuvid', '[COLOR red]El archivo no existe o ha sido borrado[/COLOR]')
        return

    for qlty, url in videos:
        itemlist.append(Item( channel = item.channel, action='play', title='', url = url, quality = qlty, server = 'directo', language = 'Vo') )

    return itemlist


def get_video_url(page_url):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    srv = scrapertools.get_domain_from_url(page_url).split(".")[-2]
    vid = scrapertools.find_single_match(page_url, '([0-9]+)')

    data = httptools.downloadpage(page_url).data

    if "File was deleted" in data or "not Found" in data: return video_urls

    url= "https://www.%s.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=null&check_speed=0" % (srv, vid)

    data = httptools.downloadpage(url).data

    data = scrapertools.find_single_match(data, '"files":(.*?)"quality"')

    matches = scrapertools.find_multiple_matches(data, '"([lh])q":"([^"]+)"')

    for quality, url in matches:
        url =  url.replace("\/", "/")

        if url:
            if "l" in quality: quality = "360p"
            elif "h" in quality: quality = "720p"

            video_urls.append(["%s" % quality, url])

    return video_urls


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'search/videos/%s' % (texto.replace(" ", "+"))
        item.tipo = "buscar"
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
