# -*- coding: utf-8 -*-

import xbmc

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools


host = 'https://www.youtube.com/'


def mainlist(item):
    logger.info()
    itemlist = []

    # ~ itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Academia Play', action = 'list_tubes', url = host + 'watch?v=99cd_dCl3pc&list=UULFv05qOuJ6Igbe-EyQibJgwQ'))

    itemlist.append(item.clone( title = 'Daniel Geohistoria', action = 'list_tubes', url = host + 'watch?v=XkpmWi9foUU&list=UULPGNk1YgQf8zeFX7uP04O_uw'))

    itemlist.append(item.clone( title = 'Dmax', action = 'list_tubes', url = host + 'watch?v=4mx89Gc-elY&list=PLXUXqAIy6K4-IAeAQp4PcP8xJHzfJu_jL'))

    itemlist.append(item.clone( title = 'Documanía Historia', action = 'list_tubes', url = host + 'watch?v=fANdEzBMlWs&list=UUv7ZxMpxzixEAi5mR_eDqHw'))

    itemlist.append(item.clone( title = 'Documental Z', action = 'list_tubes', url = host + 'watch?v=WX-FJ25QILI&list=UULFV5OEc-nA4Ge5tOLUPWosaQ'))

    itemlist.append(item.clone( title = 'Documentales Gratuitos', action = 'list_tubes', url = host + 'watch?v=wwsftALV284&list=UULF259MSTQbJjxYGzUM0SvYGA'))

    itemlist.append(item.clone( title = 'Dtom', action = 'list_tubes', url = host + 'watch?v=6PuaPBkYRXE&list=UULF_PkkoCXPpIH8Ip5RXUwccA'))

    itemlist.append(item.clone( title = 'Dw', action = 'list_tubes', url = host + 'watch?v=KQa4APEXnsQ&list=UULFQ1GpKa15ulyoQuxz7H4rng'))

    itemlist.append(item.clone( title = 'Explora Planet', action = 'list_tubes', url = host + 'watch?v=YfaCxrEaz9E&list=UULFwRvBitYM27PF-Yz2LSfABA'))

    itemlist.append(item.clone( title = 'Historias Vivas', action = 'list_tubes', url = host + 'watch?v=F7EJdtHtF2c&list=UULPAx8AK17j6BKqdQefiHWGag'))

    itemlist.append(item.clone( title = 'Lethal Crysis', action = 'list_tubes', url = host + 'watch?v=ZUOHjzEGJPM&list=UULFJCen5xxTtU7cnVHe3n424A'))

    itemlist.append(item.clone( title = 'Misterios Ocultos', action = 'list_tubes', url = host + 'watch?v=0tWiCBpgql0&list=PLV108z4JVKq9qlcn3MJBkH-lB--T11G2E'))

    itemlist.append(item.clone( title = 'Pero Eso Es Otra Historia', action = 'list_tubes', url = host + 'watch?v=9kMhQU_ZIDw&list=UULFBIMW0ZhwULY_x7fdaPRPiQ'))

    itemlist.append(item.clone( title = 'Planet Doc', action = 'list_tubes', url = host + 'watch?v=NvjeAx0eqT4&list=UULF-cLXV_UA6EnqfjbpNoGaIw'))

    itemlist.append(item.clone( title = 'Rtve', action = 'list_tubes', url = host + 'watch?v=b9oq4medEiU&list=PLFLBjMW4wU7jWKp3V_k8pw8HH4d-AAy9M'))

    itemlist.append(item.clone( title = 'Rubén Villalobos', action = 'list_tubes', url = host + 'watch?v=Z2N9UtC-ppI&list=UULF0QO3TaHg14sRc3pPFmaXnQ&index=2'))

    itemlist.append(item.clone( title = 'Show Me The World', action = 'list_tubes', url = host + 'watch?v=_GcAK3xuuTM&list=UULF1W_Jc9UmyttYlSo0i5DzJg'))

    itemlist.append(item.clone( title = 'Wild Stories', action = 'list_tubes', url = host + 'watch?v=2FVMl7zq9G4&list=UULFGtFh-sO0mpk5dgEXVzMhKw'))

    return itemlist


def list_tubes(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(str(data), '"playlist":.*?"playlist":.*?"title":(.*?)$')

    matches = scrapertools.find_multiple_matches(str(bloque), 'playlistPanelVideoRenderer":.*?simpleText":"(.*?)".*?"videoId":"(.*?)".*?"playlistId"')

    for title, _id in matches:
        if not _id or not title: continue

        title = title.replace('(Documental)', '').replace('(DOCUMENTAL COMPLETO)', '').replace('- Documental', '').replace('| DW Documental', '').replace('| HD Documental', '')
        title = title.replace('🇪🇦', '').replace('☠️', '').replace('🌎', '').replace('✅✅✅', '').strip()

        thumb = 'https://i.ytimg.com/vi/' + _id + '/hqdefault.jpg'

        url = 'https://www.youtube.com/watch?v=' + _id

        itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    itemlist.append(Item( channel = item.channel, action = 'play', server = 'youtube', language = 'Esp', url = item.url ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
