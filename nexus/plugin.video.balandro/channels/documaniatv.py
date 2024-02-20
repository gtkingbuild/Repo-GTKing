# -*- coding: utf-8 -*-

import time


from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools


host = 'https://www.documaniatv.com/'


cnomv = 'DocumaniaTv'


tex_esrn = ' por favor espere unos segundos ... y Reintentelo de nuevo'


perpage = 25


espera = config.get_setting('servers_waiting', default=6)


def do_downloadpage(url, headers=None, post=None):
    data = httptools.downloadpage(url=url, headers=headers, post=post, bypass_cloudflare=False).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'newvideos' ))
    itemlist.append(item.clone( title = 'Top 100', action = 'top_100' ))
    itemlist.append(item.clone( title = 'Por canal', action = 'canales' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))
    itemlist.append(item.clone( title = 'Por tema', action = 'series', url = host + 'top-series-documentales.html' ))

    return itemlist


def newvideos(item):
    logger.info()
    itemlist = []

    referer = host + 'documentales-nuevos.html'

    url = host + 'documentales-nuevos.html'
    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = url, referer = referer ))

    url = host + 'documentales-nuevos.html?d=month'
    itemlist.append(item.clone( title = 'Los de este mes', action = 'list_all', url = url, referer = referer ))

    url = host + 'documentales-nuevos.html?d=yesterday'
    itemlist.append(item.clone( title = 'Los de ayer', action = 'list_all', url = url, referer = referer ))

    url = host + 'documentales-nuevos.html?d=today'
    itemlist.append(item.clone( title = 'Los de hoy', action = 'list_all', url = url, referer = referer ))

    return itemlist


def top_100(item):
    logger.info()
    itemlist = []

    url = 'top-documentales.html'

    itemlist.append(item.clone( title = 'Top 100 documentales', action = 'list_all', url = host + url, page = 0))
    itemlist.append(item.clone( title = 'Top 100 más Populares', action = 'list_all', url = host + url + '?do=rating', page = 0 ))
    itemlist.append(item.clone( title = 'Top 100 más Recientes', action = 'list_all', url = host + url +'?do=recent', page = 0 ))
    itemlist.append(item.clone( title = 'Top 100 Arte y Cine', action = 'list_all', url = host + url + '?c=arte-y-cine', page = 0 ))
    itemlist.append(item.clone( title = 'Top 100 Biografías', action = 'list_all', url = host + url + '?c=biografias' ))
    itemlist.append(item.clone( title = 'Top 100 Ciencia y Tecnología', action = 'list_all', url = host + url + '?c=ciencia-y-tecnologia', page = 0 ))
    itemlist.append(item.clone( title = 'Top 100 Deporte', action = 'list_all', url = host + url + '?c=deporte', page = 0 ))
    itemlist.append(item.clone( title = 'Top 100 Historia', action = 'list_all', url = host + url + '?c=historia', page = 0 ))
    itemlist.append(item.clone( title = 'Top 100 Naturaleza', action = 'list_all', url = host + url + '?c=naturaleza', page = 0 ))
    itemlist.append(item.clone( title = 'Top 100 Política', action = 'list_all', url = host + url + '?c=politica', page = 0 ))
    itemlist.append(item.clone( title = 'Top 100 Social', action = 'list_all', url = host + url + '?c=social', page = 0 ))
    itemlist.append(item.clone( title = 'Top 100 Viajes', action = 'list_all', url = host + url + '?c=viajes', page = 0 ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    url = host + 'documentales/bbc/'
    itemlist.append(item.clone( action = 'list_all', title = 'BBC', url = url, referer = url, text_color='cyan' ))

    url = host + 'documentales/documentos-tv/'
    itemlist.append(item.clone( action = 'list_all', title = 'Documentos tv', url = url, referer = url, text_color='cyan' ))

    url = host + 'documentales/history-channel/'
    itemlist.append(item.clone( action = 'list_all', title = 'History channel', url = url, referer = url, text_color='cyan' ))

    url = host + 'documentales/la-noche-tematica/'
    itemlist.append(item.clone( action='list_all', title = 'La noche temática', url = url, referer = url, text_color='cyan' ))

    url = host + 'documentales/national-geographic/'
    itemlist.append(item.clone( action='list_all', title = 'National geographic', url = url, referer = url, text_color='cyan' ))

    url = host + 'documentales/segunda-guerra-mundial/'
    itemlist.append(item.clone( action='list_all', title = 'Segunda guerra mundial', url = url, referer = url, text_color='cyan' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<ul class="dropdown-menu">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?class="">([^<]+)')

    for url, title in matches:
        if 'documentales/' in url: continue

        itemlist.append(item.clone ( action = 'list_all', title = title, url = url, text_color='cyan' ))

    return sorted(itemlist, key=lambda it: it.title)


def series(item):
    logger.info()
    itemlist = []

    headers = None
    if item.referer: headers = {'Referer': item.referer}

    data = do_downloadpage(item.url, headers = headers)

    matches = scrapertools.find_multiple_matches(data, '<div class="pm-li-category">.*?<a href="([^"]+)".*?title="(.*?)".*?<img src="(.*?)"')

    for url, title, thumb in matches:
        title = title.replace('Serie documental', '').strip()

        title = title.capitalize()

        if title == 'Bbc': continue
        elif title == 'Documentos tv': continue
        elif title == 'History channel': continue
        elif title == 'La noche tematica': continue
        elif title == 'National geographic': continue
        elif title == 'Segunda guerra mundial' in url: continue

        itemlist.append(item.clone ( action = 'list_all', title = title, thumbnail = thumb, url = url, text_color='cyan' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)"')

        if next_page:
            itemlist.append(item.clone ( title = 'Siguientes ...', action = 'series', url = next_page, referer = next_page, text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    headers = None
    if item.referer: headers = {'Referer': item.referer}

    data = do_downloadpage(item.url, headers = headers)

    matches = scrapertools.find_multiple_matches(data, '<li class="col-xs-6 col-sm-6 col-md-4">(.*?)</li>')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<li class="col-xs-6 col-sm-6 col-md-3">(.*?)</li>')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<li class="col-xs-6 col-sm-4 col-md-3">(.*?)</li>')

    num_matches = len(matches)
    desde = 0
    hasta = num_matches

    if item.page:
        desde = item.page * perpage
        hasta = desde + perpage

    for article in matches[desde:hasta]:
        url, title = scrapertools.find_single_match(article, '<a href="([^"]+)".*?title="([^"]+)"')

        thumb = scrapertools.find_single_match(article, '<img src="([^"]+)"')

        thumb = thumb + '|User-Agent=Mozilla/5.0'

        durada = scrapertools.htmlclean(scrapertools.find_single_match(article, '<span class="pm-label-duration">(.*?)</span>'))

        if durada: durada = '[COLOR tan]%s[/COLOR]' % durada

        titulo = durada + ' ' + title

        itemlist.append(item.clone ( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra = 'documentary' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)"')

        if not next_page:
            if '/documentales-nuevos.html?d=month' in item.url or '/search.php?keywords=' in item.url:
                next_page = scrapertools.find_single_match(data, '"Pagination">.*?<li class="active">.*?<li class="">.*?</li>.*?href="(.*?)"')

                if next_page:
                    if not next_page.startswith('http'): next_page = host + next_page

        if next_page:
            itemlist.append(item.clone ( title = 'Siguientes ...', action = 'list_all', url = next_page, referer = next_page, text_color='coral' ))
        else:
            if item.page:
                if num_matches > hasta: itemlist.append(item.clone( title='Siguientes ...', page = item.page + 1, action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    notification_d_ok = config.get_setting('notification_d_ok', default=True)

    headers = {'Referer': item.url}
    data = do_downloadpage(item.url, headers = headers)

    if len(data) == 0:
        if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification(cnomv, '[COLOR cyan]Re-Intentanto acceso[/COLOR]')
        else:
            platformtools.dialog_notification(cnomv + ' Re-Cargando vídeo', 'Espera requerida de %s segundos' % espera)
            time.sleep(int(espera))

        data = do_downloadpage(item.url, headers = headers)

    if 'lo sentimos este documental ha sido eliminado' in data.lower():
        platformtools.dialog_notification(cnomv, '[COLOR red]Documental eliminado[/COLOR]')
        return

    elif '<div class="alert alert-danger"' in data:
        if ' de mantenimiento' in data.lower() or ' retornar a la normalidad' in data.lower():
            if notification_d_ok: platformtools.dialog_ok(cnomv, 'Canal en Mantenimiento')
            else: platformtools.dialog_notification(cnomv, '[COLOR moccasin]Canal en Mantenimiento[/COLOR]')
            return

    elif '<meta name="captcha-bypass"' in data:
        platformtools.dialog_ok(cnomv, '[COLOR cyan]Vídeo temporalmente bloqueado,' + tex_esrn + '[/COLOR]')
        return

    url_final = ''

    url_embed = scrapertools.find_single_match(data, '"VideoObject".*?' + item.url + '.*?https:(.*?)"')

    if not url_embed:
        if '"contentUrl":"' in data: url_embed = scrapertools.find_single_match(data, '"contentUrl":"(.*?)"')

        if not url_embed:
            if '<iframe src="' in data: 
                url_embed = scrapertools.find_single_match(data, '<iframe src="(.*?cnubis.com/[^"]+)')
                if not url_embed: url_embed = scrapertools.find_single_match(data, '<iframe src="(https://.*?cnubis.com/[^"]+)')

        if not url_embed:
            if '"Playerholder"' in data:
                url_embed = scrapertools.find_single_match(data, '"Playerholder".*?playerInstance.setup.*?file:"(.*?)".*?</div>')
                if not url_embed: url_embed = scrapertools.find_single_match(data, '"Playerholder".*?playerInstance.setup.*?file:' + "'(.*?)'.*?</div>")

        if not url_embed:
            if '"VideoPlay"'in data:
                url_embed = scrapertools.find_single_match(str(data), '"VideoPlay".*?playerInstance.setup.*?file:.*?"(.*?)".*?</div>')
                if not url_embed: url_embed = scrapertools.find_single_match(data, '"VideoPlay".*?playerInstance.setup.*?file:.*?' + "'(.*?)'.*?</div>")

        if not url_embed:
            if '"TheVid"' in data:
                url_embed = scrapertools.find_single_match(str(data), '"TheVid".*?playerInstance.setup.*?file:.*?"(.*?)".*?</div>')
                if not url_embed: url_embed = scrapertools.find_single_match(data, '"TheVid".*?playerInstance.setup.*?file:.*?' + "'(.*?)'.*?</div>")

        if not url_embed:
            if '/age-verification.js' in data:
                descartar_xxx = config.get_setting('descartar_xxx', default=False)
                if descartar_xxx:
                    platformtools.dialog_notification(cnomv, '[COLOR moccasin]Temática para adultos[/COLOR]')
                    return

        if not url_embed:
            url_embed = scrapertools.find_single_match(data, '.cnubis.com/(.*?)"')
            if url_embed: url_embed = 'https://fs2.cnubis.com/' + url_embed

    if url_embed:
        if url_embed.startswith('//'): url_embed = 'https:' + url_embed

        if url_embed.endswith('mp4') == True: url = url_embed
        else:
           data = do_downloadpage(url_embed)

           if '<meta name="captcha-bypass"' in data:
               platformtools.dialog_ok(cnomv, '[COLOR blue]Vídeo transitoriamente bloqueado,' + tex_esrn + '[/COLOR]')
               return

           url = scrapertools.find_single_match(data, 'id="jwPlayerContainer">Cargando video.*?file:.*?"(.*?)"')

        if url:
            if url.startswith('//'): url = 'https:' + url
            if url.endswith('mp4') == False: url = url + '&.mp4'

            url_final = url

    if not url_final:
        url_final = scrapertools.find_single_match(data, '<div id="player".*?jwplayer.*?playlist:.*?"(.*?)"')
        if not url_final:
            url_final = scrapertools.find_single_match(data, '<div id="player".*?jwplayer.*?file:.*?"(.*?)"')

        if url_final.startswith(host):
            data = do_downloadpage(url_final, headers = headers)
            url_final = scrapertools.find_single_match(data, '"file":"(.*?)"')

            if not url_final:
                platformtools.dialog_notification(cnomv, '[COLOR violet]Parece que hay bloqueo de IP[/COLOR]')
                return

        if url_final.endswith('mp4') == False: url_final = ''

    if url_final:
        if url_final.startswith(host):
            data = do_downloadpage(url_final, headers = headers)
            url_final = scrapertools.find_single_match(data, '"file":"(.*?)"')

            if not url_final:
                platformtools.dialog_notification(cnomv, '[COLOR violet]Al parecer hay bloqueo de IP[/COLOR]')
                return

    if url_final:
        # ~ Failed: HTTP returned error 401
        if 'http' in url_final:
            itemlist.append(Item ( channel = item.channel, action = 'play', server = 'directo', title = '', url = url_final, language = 'Esp' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    video_urls = []

    video_urls.append(['mp4', item.url])

    return video_urls


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search.php?keywords=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

