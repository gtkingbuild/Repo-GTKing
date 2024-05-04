# -*- coding: utf-8 -*-

import xbmc, base64, time

from platformcode import config, logger, platformtools
from core import httptools, scrapertools


espera = config.get_setting('servers_waiting', default=6)


color_exec = config.get_setting('notification_exec_color', default='cyan')
el_srv = ('Sin respuesta en [B][COLOR %s]') % color_exec
el_srv += ('ResolveUrl[/B][/COLOR]')


def import_libs(module):
    import os, sys, xbmcaddon
    from core import filetools

    path = os.path.join(xbmcaddon.Addon(module).getAddonInfo("path"))
    addon_xml = filetools.read(filetools.join(path, "addon.xml"))

    if addon_xml:
        require_addons = scrapertools.find_multiple_matches(addon_xml, '(<import addon="[^"]+"[^\/]+\/>)')
        require_addons = list(filter(lambda x: not 'xbmc.python' in x and 'optional="true"' not in x, require_addons))

        for addon in require_addons:
            addon = scrapertools.find_single_match(addon, 'import addon="([^"]+)"')
            if xbmc.getCondVisibility('System.HasAddon("%s")' % (addon)):
                import_libs(addon)
            else:
                xbmc.executebuiltin('InstallAddon(%s)' % (addon))
                import_libs(addon)

        lib_path = scrapertools.find_multiple_matches(addon_xml, 'library="([^"]+)"')
        for lib in list(filter(lambda x: not '.py' in x, lib_path)):
            sys.path.append(os.path.join(path, lib))


def normalizar_url(page_url):
    try:
        page_url = page_url.replace('&amp;', '&')
        oid, nid = scrapertools.find_single_match(page_url, "oid=(\d+)&id=(\d+)")
        return 'https://vk.com/video%s_%s' % (oid, nid)
    except:
        return page_url.replace('http://', 'https://')


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    ini_page_url = page_url

    page_url = normalizar_url(page_url)

    data = httptools.downloadpage(page_url).data

    if 'This video has been removed from public access' in data or 'Video not found' in data or '<div class="message_page_title">Error</div>' in data or 'no encontrado.' in data:
        return 'Archivo inexistente ó eliminado'

    if '<p>Por causas ajenas a' in data or '>Por causas ajenas a' in data:
        return 'Servidor Bloqueado por su Operadora'

    url_savevk = 'https://savevk.com/' + page_url.replace('https://vk.com/', '')

    data = httptools.downloadpage(url_savevk).data

    bloque = scrapertools.find_single_match(data, 'window\.videoParams = \{(.*?)\};')

    p_id = scrapertools.find_single_match(bloque, 'id: "([^"]+)')
    p_server = scrapertools.find_single_match(bloque, 'server: "([^"]+)')
    p_token = scrapertools.find_single_match(bloque, 'token: "([^"]+)')

    p_credentials = scrapertools.find_single_match(bloque, 'credentials: "([^"]+)')
    p_c_key = scrapertools.find_single_match(bloque, 'c_key: "([^"]+)')
    p_e_key = scrapertools.find_single_match(bloque, 'e_key: "([^"]+)')
    p_i_key = scrapertools.find_single_match(bloque, 'i_key: "([^"]+)')

    if not p_id or not p_server or not p_token:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
            if config.get_setting('servers_time', default=True):
                platformtools.dialog_notification('Cargando [COLOR cyan][B]Vk[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
                time.sleep(int(espera))

            try:
                import_libs('script.module.resolveurl')

                import resolveurl
                page_url = ini_page_url
                resuelto = resolveurl.resolve(page_url)

                if resuelto:
                    video_urls.append(['mp4', resuelto])
                    return video_urls

                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

            except:
                import traceback
                logger.error(traceback.format_exc())

                if 'resolveurl.resolver.ResolverError:' in traceback.format_exc():
                    trace = traceback.format_exc()
                    if 'File Not Found or' in trace or 'The requested video was not found' in trace or 'File deleted' in trace or 'No video found' in trace or 'No playable video found' in trace or 'Video cannot be located' in trace or 'file does not exist' in trace or 'Video not found' in trace:
                        return 'Archivo inexistente ó eliminado'
                    elif 'No se ha encontrado ningún link al' in trace or 'Unable to locate link' in trace or 'Video Link Not Found' in trace:
                        return 'Fichero sin link al vídeo'

                elif '<urlopen error' in traceback.format_exc():
                    return 'No se puede establecer la conexión'

                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

        else:
           return 'Acceso Denegado, sin ResolveUrl'

    url = 'https://%s/method/video.get?credentials=%s&token=%s&videos=%s&extra_key=%s&ckey=%s' % (base64.b64decode(p_server[::-1]), p_credentials, p_token, p_id, p_e_key, p_c_key)

    if "/b'" in str(url): url = url.replace("/b'", "/").replace("'/", "/")

    data = httptools.downloadpage(url, headers={'Referer': url_savevk}).data.replace('\\/', '/')

    bloque = scrapertools.find_single_match(data, '"files":\{(.*?)\}')

    matches = scrapertools.find_multiple_matches(bloque, '"([^"]+)":"([^"]+)')

    for lbl, url in matches:
        video_urls.append([lbl, url])

    if not video_urls:
        data = httptools.downloadpage(page_url).data

        matches = scrapertools.find_multiple_matches(data, '"url(\d+)":"([^"]+)"')

        for calidad, url in matches:
            url = url.replace("\/", "/")

            video_urls.append([calidad, url])

    if not video_urls:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
            if config.get_setting('servers_time', default=True):
                platformtools.dialog_notification('Cargando [COLOR cyan][B]Vk[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
                time.sleep(int(espera))

            try:
                import_libs('script.module.resolveurl')

                import resolveurl
                page_url = ini_page_url
                resuelto = resolveurl.resolve(page_url)

                if resuelto:
                    video_urls.append(['mp4', resuelto])
                    return video_urls

                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

            except:
                import traceback
                logger.error(traceback.format_exc())

                if 'resolveurl.resolver.ResolverError:' in traceback.format_exc():
                    trace = traceback.format_exc()
                    if 'File Not Found or' in trace or 'The requested video was not found' in trace or 'File deleted' in trace or 'No video found' in trace or 'No playable video found' in trace or 'Video cannot be located' in trace or 'file does not exist' in trace or 'Video not found' in trace:
                        return 'Archivo inexistente ó eliminado'
                    elif 'No se ha encontrado ningún link al' in trace or 'Unable to locate link' in trace or 'Video Link Not Found' in trace:
                        return 'Fichero sin link al vídeo'

                elif '<urlopen error' in traceback.format_exc():
                    return 'No se puede establecer la conexión'

                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

        else:
           return 'Acceso Denegado (2do.), sin ResolveUrl'

    return video_urls
