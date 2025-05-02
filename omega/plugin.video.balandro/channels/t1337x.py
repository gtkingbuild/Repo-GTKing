# -*- coding: utf-8 -*-

import re

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://www.1337x.to/'


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
        itemlist.append(item.clone( title = 'Animes', action = 'list_down', url = host + 'cat/Anime/1/', tipo='tvshow',
                                    search_type = 'tvshow', text_color=' springgreen' ))

    if not config.get_setting('descartar_xxx', default=False):
        itemlist.append(item.clone( title = 'Adultos', action = 'list_down', url = host + 'cat/XXX/1/', tipo='movie',
                                    search_type = 'movie', adults='adults', text_color = 'orange' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', tipo='movie', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movie-library/1/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_down', url = host + 'cat/Movies/1/', tipo='movie', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Navidad', action = 'list_all', url = host + 'christmas-movies/1/', search_type = 'movie' ))

    itemlist.append(item.clone( action ='generos', title='Por género', search_type = 'movie' ))
    itemlist.append(item.clone( action= 'idiomas', title = 'Por idioma', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', tipo='tvshow', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_down', url = host + 'cat/TV/1/', tipo='tvshow', search_type = 'tvshow' ))

    if not config.get_setting('descartar_anime', default=False):
        itemlist.append(item.clone( title = 'Animes', action = 'list_down', url = host + 'cat/Anime/1/', tipo='tvshow', search_type = 'tvshow', text_color=' springgreen' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'movie-library/1/')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<select name="genre"(.*?)</select>')

    matches = re.compile('<option value="(.*?)">(.*?)</option>', re.DOTALL).findall(bloque)

    for value, title in matches:
        if title == 'All': continue

        url = host + 'movie-lib-sort/' + value + '/all/score/desc/all/1/'

        itemlist.append(item.clone( title = title, url = url, action = 'list_all', value = value, text_color='deepskyblue' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'movie-library/1/')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<select name="lang"(.*?)</select>')

    matches = re.compile('<option value="(.*?)">(.*?)</option>', re.DOTALL).findall(bloque)

    for value, title in matches:
        if title == 'All': continue

        if 'Multi' in title: title = 'z ' + title

        url = host + 'movie-lib-sort/all/' + value + '/score/desc/all/1/'

        itemlist.append(item.clone( title = title, url = url, action = 'list_all', value = value, text_color='moccasin' ))

    return sorted(itemlist, key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1899, -1):
        url = host + 'movie-lib-sort/all/all/score/desc/' + str(x) + '/1/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', value = str(x), text_color='deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, 'data-target="(.*?)</li>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if url == '#': url = scrapertools.find_single_match(match, '</strong><a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3>.*?">(.*?)</a>')
        if not title: title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if item.value: title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if '<span>' in title: title = scrapertools.find_single_match(title, '<span>(.*?)</span>')

        if not url or not title: continue

        url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'data-original="(.*?)"')

        if thumb: thumb = 'https:' + thumb

        tipo = 'movie' if '/movie/' in url else 'tvshow'

        if tipo == 'tvshow':
            SerieName = corregir_Name(title)

            itemlist.append(item.clone( action='list_down', url=url, title=title, thumbnail=thumb, tipo=tipo ))

        if tipo == 'movie':
            PeliName = corregir_Name(title)

            itemlist.append(item.clone( action='list_down', url=url, title=title, thumbnail=thumb, tipo=tipo, contentExtra=item.adults ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<li class="active">.*?</a>.*?href="(.*?)"')

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def list_down(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')

    matches = re.compile('</a><a href="(.*?)".*?>(.*?)</a>', re.DOTALL).findall(bloque)

    contentExtra = ''

    thumb = item.thumb

    if item.adults:
        contentExtra = 'adults'
        thumb = config.get_thumb('adults')

    for url, title in matches:
        url = host[:-1] + url

        title = title.replace('.', ' ')

        c_year = scrapertools.find_single_match(title, '(\d{4})')
        if c_year:
            title = title.replace('(' + c_year + ')', '').strip()
            title = title.replace(c_year, '').strip()

        lang = 'Vo'
        if 'SPANISH' in title or 'Spanish' in title: lang = 'Esp'
        elif 'ENGLISH' in title or 'English' in title: lang = 'Ing'

        if item.tipo:
            tipo = item.tipo
        else:     
            tipo = 'movie' if '/movie/' in url else 'tvshow'

        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            SerieName = corregir_Name(title)

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang, fmt_sufijo=sufijo,
                                        contentExtra='3',
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

        if tipo == 'movie':
            if item.search_type != 'all':
                if item.search_type == "tvshow": continue

            PeliName = corregir_Name(title)

            itemlist.append(item.clone( action = 'findvideos', url=url, title=title, thumbnail=thumb, languages=lang, fmt_sufijo=sufijo,
                                        contentExtra=contentExtra,
                                        contentType = 'movie', contentTitle = PeliName, infoLabels = {'year': '-'} ))

    if not item.adults:
        tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<li class="active">.*?</a>.*?href="(.*?)"')

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_down', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="dropdown-menu"(.*?)</ul>')

    matches = re.compile('href="(.*?)"', re.DOTALL).findall(bloque)

    for url in matches:
        other = ''

        if '/torrage.info/' in url: continue
        elif '/btcache.me/' in url: continue

        if 'magnet:' in url: other = 'Magnet'

        url = url.replace('http://', 'https://')

        if 'magnet:' in url: pass
        else:
           if not '.torrent' in url: url = url + '.torrent'

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
    itemlist = []

    itemlist1 = []
    itemlist2 = []

    try:
        if not item.tipo:
            item.tipo = 'movie'
            item.url = host + 'search/' + texto.replace(" ", "+") + '/1/'
            itemlist1 = list_down(item)

            if not itemlist1:
                item.tipo = 'tvshow'
                item.url = host + 'search/' + texto.replace(" ", "+") + '/1/'
                itemlist2 = list_down(item)

            itemlist = itemlist1 + itemlist2
            return itemlist
        else:
           item.url = host + 'search/' + texto.replace(" ", "+") + '/1/'
           return list_down(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
