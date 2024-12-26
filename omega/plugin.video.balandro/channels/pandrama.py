# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://pandramas.net/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo episodios', action = 'list_all', url = host, search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<article(.*?)</article>').findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        title = title.replace('&#8217;s', "'").strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        SerieName = title

        if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]
        if 'capítulo' in SerieName: SerieName = SerieName.split("capítulo")[0]
        if 'capitulo' in SerieName: SerieName = SerieName.split("capitulo")[0]

        if 'Sub Español' in SerieName: SerieName = SerieName.split("Sub Español")[0]

        SerieName = SerieName.strip()

        titulo = title.replace('Capítulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('capítulo', '[COLOR goldenrod]Epis-[/COLOR]').replace('capítulo', '[COLOR goldenrod]Epis.[/COLOR]').replace('capitulo', '[COLOR goldenrod]Epis.[/COLOR]')

        epis = scrapertools.find_single_match(url, '-capitulo-(.*?)-')

        if not epis: epis = 1

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb,
                                    contentSeason=1, contentEpisodeNumber=epis, contentType='episode', contentSerieName=SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="nav-links">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="nav-links">.*?class="page-numbers current">.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title="Siguientes ...", action="list_all", url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<IFRAME.*?SRC=(".*?)"')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<iframe.*?src=(".*?)"')

    ses = 0

    for url in matches:
        if not 'http' in url: continue

        ses += 1

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vose', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        item.text = texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
