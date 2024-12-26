# -*- coding: utf-8 -*-

import re

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://torrentgalaxy.one/'


no_porns = config.get_setting('descartar_xxx', default=False)


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    if not config.get_setting('descartar_anime', default=False):
        if not no_porns:
            itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'get-posts/category:Anime/', search_type = 'tvshow', text_color=' springgreen' ))
        else:
            itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'get-posts/category:Anime:ncategory:XXX/', search_type = 'tvshow', text_color=' springgreen' ))

    if not no_porns:
        itemlist.append(item.clone( title = 'Adultos', action = 'mainlist_adults', text_color = 'orange' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    if not no_porns:
        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'get-posts/', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Colecciones', action = 'list_all', url = host + 'get-posts/keywords:Packs:category:Movies/', search_type = 'movie', text_color='greenyellow' ))

        itemlist.append(item.clone( title = 'Bollywood', action = 'list_all', url = host + 'get-posts/keywords:Bollywood:category:Movies/', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'En [COLOR moccasin]4K[/COLOR]', action = 'list_all', url = host + 'get-posts/keywords:4K UHD:category:Movies/', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'get-posts/keywords:HD:category:Movies/', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'En SD', action = 'list_all', url = host + 'get-posts/keywords:SD:category:Movies/', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'En TS', action = 'list_all', url = host + 'get-posts/keywords:CAMTS:category:Movies/', search_type = 'movie' ))
    else:
        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'get-posts:ncategory:XXX/', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Colecciones', action = 'list_all', url = host + 'get-posts/keywords:Packs:category:Movies:ncategory:XXX/', search_type = 'movie', text_color='greenyellow' ))

        itemlist.append(item.clone( title = 'Bollywood', action = 'list_all', url = host + 'get-posts/keywords:Bollywood:category:Movies:ncategory:XXX/', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'En [COLOR moccasin]4K[/COLOR]', action = 'list_all', url = host + 'get-posts/keywords:4K UHD:category:Movies/', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'get-posts/keywords:HD:category:Movies:ncategory:XXX/', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'En SD', action = 'list_all', url = host + 'get-posts/keywords:SD:category:Movies:ncategory:XXX/', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'En TS', action = 'list_all', url = host + 'get-posts/keywords:CAMTS:category:Movies:ncategory:XXX/', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    if not no_porns:
        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'get-posts/', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Colecciones', action = 'list_all', url = host + 'get-posts/keywords:Packs:category:TV/', search_type = 'tvshow', text_color='greenyellow' ))

        if not config.get_setting('descartar_anime', default=False):
            itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'get-posts/category:Anime/', search_type = 'tvshow', text_color=' springgreen' ))

        itemlist.append(item.clone( title = '[B]Episodios:[/B]', action = '', search_type = 'tvshow', text_color='moccasin' ))

        itemlist.append(item.clone( title = ' - En [COLOR moccasin]4K[/COLOR]', action = 'list_all', url = host + 'get-posts/keywords:Eps 4k UHD:category:TV/', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = ' - En HD', action = 'list_all', url = host + 'get-posts/keywords:Episodes HD:category:TV/', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = ' - En SD', action = 'list_all', url = host + 'get-posts/keywords:Episodes SD:category:TV/', search_type = 'tvshow' ))
    else:
        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'get-posts:ncategory:XXX/', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Colecciones', action = 'list_all', url = host + 'get-posts/keywords:Packs:category:TV:ncategory:XXX/', search_type = 'tvshow', text_color='greenyellow' ))

        if not config.get_setting('descartar_anime', default=False):
            itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'get-posts/category:Anime:ncategory:XXX/', search_type = 'tvshow', text_color=' springgreen' ))

        itemlist.append(item.clone( title = '[B]Episodios:[/B]', action = '', search_type = 'tvshow', text_color='moccasin' ))

        itemlist.append(item.clone( title = ' - En [COLOR moccasin]4K[/COLOR]', action = 'list_all', url = host + 'get-posts/keywords:Eps 4k UHD:category:TV:ncategory:XXX/', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = ' - En HD', action = 'list_all', url = host + 'get-posts/keywords:Episodes HD:category:TV:ncategory:XXX/', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = ' - En SD', action = 'list_all', url = host + 'get-posts/keywords:Episodes SD:category:TV:ncategory:XXX/', search_type = 'tvshow' ))

    return itemlist


def mainlist_adults(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Adultos:', action = '', text_color = 'orange' ))

    itemlist.append(item.clone( title = ' - Catálogo', action = 'list_all', url = host + 'get-posts/', search_type = 'movie' ))

    itemlist.append(item.clone( title = ' - En [COLOR moccasin]4K[/COLOR]', action = 'list_all', url = host + 'get-posts/keywords:4K UHD:category:XXX/', search_type = 'movie' ))

    itemlist.append(item.clone( title = ' - En HD', action = 'list_all', url = host + 'get-posts/keywords:HD:category:XXX/', search_type = 'movie' ))

    itemlist.append(item.clone( title = ' - En SD', action = 'list_all', url = host + '/get-posts/keywords:SD:category:XXX/', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="tgxtablerow txlight"(.*?)</table>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'data-href="(.*?)"')

        title = scrapertools.find_single_match(match, '<a class="txlight" title="(.*?)"')

        if not url or not title: continue

        if '<small>TV' in match: pass
        elif '<small>Anime' in match: pass
        elif '<small>Movie' in match: pass
        elif '<small>XXX' in match: pass
        else: continue

        url = host[:-1] + url

        title = title.replace('&#039;t', "'t").replace('&#039;', "'").replace('&#8211;', '').replace('&amp;', '').strip()

        title = title.replace('.', ' ')

        thumb = scrapertools.find_single_match(match, "src=.?'(.*?)'")

        contentExtra = ''
        if '<small>XXX' in match:
            contentExtra = 'adults'
            thumb = config.get_thumb('adults')

        lang = scrapertools.find_single_match(match, '<!-- <img class="dim txlight".*?title="(.*?)"')

        if not lang: lang = 'Vo'
        else:
           if 'SPANISH' in lang or 'Spanish' in lang: lang = 'Esp'
           elif 'ENGLISH' in lang or 'English' in lang: lang = 'Ing'

        c_year = scrapertools.find_single_match(title, '(\d{4})')
        if c_year:
            title = title.replace('(' + c_year + ')', '').strip()
            title = title.replace(c_year, '').strip()

        tipo = 'movie' if '<small>Movie' in match or '<small>XXX' in match or '<small>TV: Sports' in match else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            if '<small>Movie' in match: continue
            elif '<small>XXX' in match: continue

            SerieName = corregir_Name(title)

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang, fmt_sufijo=sufijo,
                                        contentExtra='3',
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == "tvshow": continue

            if '<small>TV: Sports' in match: pass
            elif '<small>TV' in match: continue
            elif '<small>Anime' in match: continue

            PeliName = corregir_Name(title)

            itemlist.append(item.clone( action = 'findvideos', url=url, title=title, thumbnail=thumb, languages=lang, fmt_sufijo=sufijo,
                                        contentExtra=contentExtra,
                                        contentType = 'movie', contentTitle = PeliName, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<nav aria-label="pages">.*?<li class="page-item active">.*?</a>.*?href="(.*?)"')

        if next_page:
            act_page = scrapertools.find_single_match(item.url, '(.*?)/?page=')
            if not act_page: act_page = item.url

            next_page = next_page.replace('&amp;', '&')

            if '?page=' in next_page:
                next_page = act_page + next_page

                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Download<(.*?)</center></center>')

    matches1 = re.compile("<a href='(.*?)'", re.DOTALL).findall(bloque)

    matches2 = re.compile('href="(.*?)"', re.DOTALL).findall(bloque)

    matches = matches1 + matches2

    for url in matches:
        other = ''

        if 'magnet:' in url: other = 'Magnet'
        elif not '.torrent' in url: continue

        url = url.replace('http://', 'https://')

        if 'torrent?title=' in url:
            vid = url.split("torrent?title=")[1]

            url = url.replace('/itorrents.org/torrent/', '/watercache.nanobytes.org/get/')
            url = url.replace('.torrent?title=', '/')

            url = url + vid

        if '.torrent?' in url: url = url.replace('.torrent?', '.torrent')

        if 'magnet:' in url: pass
        else:
           if not '.torrent' in url: url = url + '.torrent'

           if "&library=" in url: url = url.split("&library=")[0]

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language=item.languages, other=other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;', '&')

    itemlist.append(item.clone( url = item.url, server = 'torrent' ))

    return itemlist


def corregir_Name(Name):
    logger.info()

    if "[" in Name: Name = Name.split("[")[0]

    if "4K" in Name: Name = Name.split("4K")[0]

    if "BluRay" in Name: Name = Name.split("BluRay")[0]

    if "2160p" in Name: Name = Name.split("2160p")[0]
    if "1080p" in Name: Name = Name.split("1080p")[0]
    if "720p" in Name: Name = Name.split("720p")[0]
    if "480p" in Name: Name = Name.split("480p")[0]

    if "MP4" in Name: Name = Name.split("MP4")[0]
    if "Mp4" in Name: Name = Name.split("Mp4")[0]

    if "MKV" in Name: Name = Name.split("MKV")[0]
    if "Mkv" in Name: Name = Name.split("Mkv")[0]

    if "DVD" in Name: Name = Name.split("DVD")[0]
    if "Dvd" in Name: Name = Name.split("Dvd")[0]

    if "BDRip" in Name: Name = Name.split("BDRip")[0]
    if "DVDRip" in Name: Name = Name.split("DVDRip")[0]
    if "WEBRiP" in Name: Name = Name.split("WEBRiP")[0]
    if "WEB-DL" in Name: Name = Name.split("WEB-DL")[0]
    if "WEB DL" in Name: Name = Name.split("WEB DL")[0]
    if "WEBDL" in Name: Name = Name.split("WEBDl")[0]
    if "HDR" in Name: Name = Name.split("HDR")[0]
    if "HDTS" in Name: Name = Name.split("HDTS")[0]
    if "HDCAM" in Name: Name = Name.split("HDCAM")[0]

    if "SD" in Name: Name = Name.split("SD")[0]

    if "CAM" in Name: Name = Name.split("CAM")[0]
    if "Cam " in Name: Name = Name.split("Cam ")[0]

    if "REMASTERED" in Name: Name = Name.split("REMASTERED")[0]
    if 'Remastered' in Name: Name = Name.split("Remastered")[0]

    if "SPANISH" in Name: Name = Name.split("SPANISH")[0]
    if "Spanish" in Name: Name = Name.split("Spanish")[0]

    if "ENGLISH" in Name: Name = Name.split("ENGLISH")[0]
    if "English" in Name: Name = Name.split("English")[0]

    if "GERMAN" in Name: Name = Name.split("GERMAN")[0]
    if "Germany" in Name: Name = Name.split("Germany")[0]
    if "German" in Name: Name = Name.split("German")[0]

    if "iTALiAN" in Name: Name = Name.split("iTALiAN")[0]
    if "Italian" in Name: Name = Name.split("Italian")[0]
    if "ITA" in Name: Name = Name.split("ITA")[0]

    if "Rus " in Name: Name = Name.split("Rus ")[0]

    if 'Season' in Name: Name = Name.split("Season")[0]

    if ' S0' in Name: Name = Name.split(" S0")[0]
    elif ' S1' in Name: Name = Name.split(" S1")[0]
    elif ' S2' in Name: Name = Name.split(" S2")[0]
    elif ' S3' in Name: Name = Name.split(" S3")[0]
    elif ' S4' in Name: Name = Name.split(" S4")[0]
    elif ' S5' in Name: Name = Name.split(" S5")[0]
    elif ' S6' in Name: Name = Name.split(" S6")[0]
    elif ' S7' in Name: Name = Name.split(" S7")[0]
    elif ' S8' in Name: Name = Name.split(" S8")[0]
    elif ' S9' in Name: Name = Name.split(" S9")[0]

    if ' s0' in Name: Name = Name.split(" s0")[0]
    elif ' s1' in Name: Name = Name.split(" s1")[0]
    elif ' s2' in Name: Name = Name.split(" s2")[0]
    elif ' s3' in Name: Name = Name.split(" s3")[0]
    elif ' s4' in Name: Name = Name.split(" S4")[0]
    elif ' s5' in Name: Name = Name.split(" S5")[0]
    elif ' s6' in Name: Name = Name.split(" s6")[0]
    elif ' s7' in Name: Name = Name.split(" s7")[0]
    elif ' s8' in Name: Name = Name.split(" s8")[0]
    elif ' s9' in Name: Name = Name.split(" s9")[0]

    if 'COMPLETE' in Name: Name = Name.split("COMPELTE")[0]
    if '(Complete' in Name: Name = Name.split("(Complete")[0]
    if ' Complete ' in Name: Name = Name.split(" Completa ")[0]

    if 'Trilogia' in Name: Name = Name.split("Trilogia")[0]
    if ' Saga' in Name: Name = Name.split(" Saga")[0]

    if ' Serie' in Name: Name = Name.split(" Serie")[0]
    if ' serie' in Name: Name = Name.split(" serie")[0]

    if ': ' in Name: Name = Name.split(": ")[0]

    Name = Name.strip()

    return Name


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'get-posts/keywords:' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
