# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib                                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                                               # Usamos el nativo de PY2 que es más rápido

import re

from core import httptools
from core import scrapertools
from core.item import Item
from platformcode import config, logger

canonical = {
             'channel': 'areadocumental', 
             'host': config.get_setting("current_host", 'areadocumental', default=''), 
             'host_alt': ["https://www.area-documental.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

__perfil__ = int(config.get_setting('perfil', "areadocumental"))

# Fijar perfil de color
perfil = [['', '', ''],
          ['0xFFFFE6CC', '0xFFFFCE9C', '0xFF994D00'],
          ['0xFFA5F6AF', '0xFF5FDA6D', '0xFF11811E'],
          ['0xFF58D3F7', '0xFF2E9AFE', '0xFF2E64FE']]
color1, color2, color3 = perfil[__perfil__]


def mainlist(item):
    logger.info()
    
    itemlist = []
    item.text_color = color1
    
    itemlist.append(item.clone(title="Novedades", action="entradas",
                               url= host + "resultados-reciente.php?buscar=&genero="))
    
    itemlist.append(item.clone(title="Destacados", action="entradas",
                               url= host + "resultados.php?buscar=&genero="))
    
    itemlist.append(item.clone(title="Más Vistos", action="entradas",
                               url= host + "resultados-visto.php?buscar=&genero="))
    
    itemlist.append(item.clone(title="3D", action="entradas",
                               url= host + "3D.php"))
    
    itemlist.append(item.clone(title="Categorías", action="cat", url= host + "index.php"))
    
    itemlist.append(item.clone(title="Ordenados por...", action="indice"))

    itemlist.append(item.clone(title="Buscar...", action="search"))
    
    itemlist.append(item.clone(title="Configurar canal", action="configuracion", text_color="gold"))

    return itemlist


def get_source(url):
    logger.info()
    
    data = httptools.downloadpage(url, canonical=canonical).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}|"|\(|\)', "", data)
    
    return data


def configuracion(item):
    from platformcode import platformtools
    
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    
    return ret


def search(item, texto):
    logger.info()
    
    item.url = host + "resultados/buscar=%s/" % texto
    item.action = "entradas"
    
    try:
        itemlist = entradas(item)
        return itemlist
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()
    
    itemlist = []
    item = Item()
    
    try:
        if categoria == "documentales":
            item.url = host + "resultados-reciente.php?buscar=&genero="
            item.action = "entradas"
            itemlist = entradas(item)

            if itemlist[-1].action == "entradas":
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def indice(item):
    logger.info()
    
    itemlist = []
    
    itemlist.append(item.clone(title="Título", action="entradas",
                               url= host + "resultados-titulo.php?buscar=&genero="))
    itemlist.append(item.clone(title="Año", action="entradas",
                               url= host + "resultados-anio.php?buscar=&genero="))
    return itemlist


def cat(item):
    logger.info()
    
    itemlist = []
    
    data = get_source(item.url)
    bloques = scrapertools.find_multiple_matches(data, '</li><li class=dropdown>.*?</ul>')
    
    for bloque in bloques:
        matches = scrapertools.find_multiple_matches(bloque, "<li><a href=(.*?)>(.*?)<")
        for _scrapedurl, scrapedtitle in matches:
            scrapedurl = urllib.urljoin(host, _scrapedurl)
            if not "TODO" in scrapedtitle:
                itemlist.append(item.clone(action="entradas", title=scrapedtitle, url=scrapedurl))

    return itemlist


def destacados(item):
    logger.info()
    
    itemlist = []
    item.text_color = color2

    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = scrapertools.unescape(data)
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"> ></a>')
    if next_page != "":
        data2 = scrapertools.unescape(httptools.downloadpage(urllib.urljoin(host, next_page), canonical=canonical).data)
        data += data2
    else:
        data2 = ""
    data = data.replace("\n", "").replace("\t", "")

    patron  = '(?s)<div id="peliculas">.*?a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'target="_blank">(.*?)</a></span>'
    patron += '(.*?)<p>'
    patron += '(.*?)</p>.*?'
    patron += '</strong>:(.*?)<strong>.*?'
    patron += '</strong>(.*?)</div>'
    
    matches = scrapertools.find_multiple_matches(data, patron)
    for _scrapedurl, _scrapedthumbnail, scrapedtitle, year, scrapedplot, genero, extra in matches:
        infolab = {'plot': scrapedplot, 'genre': genero}
        scrapedurl = urllib.urljoin(host, _scrapedurl)
        scrapedthumbnail = urllib.urljoin(host, urllib.quote(_scrapedthumbnail))
        title = scrapedtitle
        if "full_hd" in extra:
            quality = "3D"
        elif "720" in extra:
            quality ='720'
        else:
            quality = 'SD'

        year = year.replace("\xc2\xa0", "").replace(" ", "")
        if not year.isspace() and year != "":
            infolab['year'] = int(year)

        itemlist.append(item.clone(action="findvideos", title=title, contentTitle=title,
                                   url=scrapedurl, thumbnail=scrapedthumbnail, 
                                   infoLabels=infolab, quality = quality))

    next_page = scrapertools.find_single_match(data2, '<a href="([^"]+)"> ></a>')
    if next_page:
        itemlist.append(item.clone(action="entradas", title=">> Página Siguiente", url=urllib.urljoin(host, next_page),
                                   text_color=color3))

    return itemlist


def entradas(item):
    logger.info()
    
    itemlist = []
    item.text_color = color2

    data = get_source(item.url)

    patron  = 'class=imagen.*?href=(.*?)><img.*?src=(.*?) alt=.*?title=(.*?)/>.*?</h2>(\d{4}) (.*?)<.*?space>(.*?)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for  _scrapedurl, _scrapedthumbnail, scrapedtitle, year, genero, scrapedplot in matches:
        infolab = {'plot': scrapedplot, 'genre': genero}
        scrapedurl = urllib.urljoin(host, _scrapedurl)
        scrapedthumbnail = urllib.urljoin(host, _scrapedthumbnail)
        title = scrapedtitle
        if "3D" in genero:
            quality = "3D"
        elif "HD" in genero:
            quality ='HD'
        else:
            quality = 'SD'
        if not year.isspace() and year != "":
            infolab['year'] = year
            title += '[COLOR %s] (%s)[/COLOR]' % (color1, year)
        title += '[COLOR %s] [%s][/COLOR]' % (color3, quality)
        itemlist.append(item.clone(action="findvideos", title=title, contentTitle=title,
                                   url=scrapedurl, thumbnail=scrapedthumbnail, infoLabels=infolab))

    next_page = scrapertools.find_single_match(data, '<a class=last>.*?</a></li><li><a href=(.*?)>.*?</a>')
    next_page = scrapertools.htmlclean(next_page)
    if next_page:
        itemlist.append(item.clone(action="entradas", title=">> Página Siguiente", url=urllib.urljoin(host, next_page),
                                   text_color=color3))
    return itemlist


def findvideos(item):
    logger.info()
    
    itemlist = []
    
    data = httptools.downloadpage(item.url, canonical=canonical).data

    subs = scrapertools.find_multiple_matches(data, 'file: "(/webvtt[^"]+)".*?label: "([^"]+)"')
    bloque = scrapertools.find_single_match(data, 'title.*?track')
    patron = 'file:\s*"([^"]+).*?label:\s*"([^"]+)"'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    
    for _url, quality in matches:
        url = httptools.get_url_headers(urllib.urljoin(host, _url), forced=True)
        
        for _url_sub, label in subs:
            url_sub = urllib.urljoin(host, urllib.quote(_url_sub))
            title = "Ver video en [[COLOR %s]%s[/COLOR]] Sub %s" % (color3, quality, label)
            itemlist.append(item.clone(action="play", server="directo", title=title,
                                       url=url, subtitle=url_sub, extra=item.url, quality=quality, language = label))
    return itemlist


def play(item):
    logger.info()
    
    itemlist = []

    try:
        from core import filetools
        ficherosubtitulo = filetools.join(config.get_data_path(), 'subtitulo_areadocu.srt')
        if filetools.exists(ficherosubtitulo):
            try:
                filetools.remove(ficherosubtitulo)
            except IOError:
                logger.error("Error al eliminar el archivo " + ficherosubtitulo)
                raise

        data = httptools.downloadpage(item.subtitle, headers={'Referer': item.extra}).data
        filetools.write(ficherosubtitulo, data)
        subtitle = ficherosubtitulo
    except:
        subtitle = ""
        logger.error("Error al descargar el subtítulo")

    extension = item.url.rsplit("|", 1)[0][-4:]
    itemlist.append(['%s %s [directo]' % (extension, item.calidad), item.url, 0, subtitle])

    return itemlist
