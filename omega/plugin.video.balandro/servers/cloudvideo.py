# -*- coding: utf-8 -*-

import xbmc, time

from core import httptools, scrapertools
from platformcode import config, logger, platformtools

from lib import jsunpack


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


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    ini_page_url = page_url

    if 'emb.html?' in page_url:
        page_url = page_url.replace('cloudvideo.tv/emb.html?', 'cloudvideo.tv/embed-') + '.html'
    elif 'embed-' not in page_url:
        page_url = page_url.replace('cloudvideo.tv/', 'cloudvideo.tv/embed-') + '.html'

    resp = httptools.downloadpage(page_url)
    if resp.code == 404 or '<div id="television">' in resp.data:
        return 'Archivo inexistente ó eliminado'

    data = resp.data

    video_urls = extraer_videos(data)

    if len(video_urls) == 0:
        enc_data = scrapertools.find_single_match(data, "text/javascript'[^>]*>(eval\(.*?)</script>")
        if not enc_data: enc_data = scrapertools.find_single_match(data, 'text/javascript"[^>]*>(eval\(.*?)</script>')

        if enc_data:
            try:
                data = jsunpack.unpack(enc_data)
                video_urls = extraer_videos(data)
            except:
                pass

    if not video_urls:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
            if config.get_setting('servers_time', default=True):
                platformtools.dialog_notification('Cargando [COLOR cyan][B]Cloudvideo[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
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

    return video_urls


def extraer_videos(data):
    video_urls = []

    sources = scrapertools.find_single_match(data, "<source(.*?)</source")
    matches = scrapertools.find_multiple_matches(sources, 'src="([^"]+)')

    for url in matches:
        quality = 'm3u8'
        video_url = url

        if 'label' in url:
            url = url.split(',')
            video_url = url[0]
            quality = url[1].replace('label:','')

        video_urls.append([quality, video_url])

    if len(video_urls) == 0:
        sources = scrapertools.find_single_match(data, 'sources\s*:\s*\[(.*?)\]')
        matches = scrapertools.find_multiple_matches(sources, '(http.*?)"')

        for videourl in matches:
            extension = scrapertools.get_filename_from_url(videourl)[-4:]
            video_urls.append([extension, videourl])

    return video_urls
