# -*- coding: utf-8 -*-

import xbmc, time

from platformcode import config, logger, platformtools
from core import httptools, scrapertools, servertools

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
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    ini_page_url = page_url

    page_url = page_url.replace('/e/', '/play/').replace('/d/', '/play/')
    page_url = page_url.replace('embed-', '')

    data = httptools.downloadpage(page_url).data

    if 'File Not Found' in data or 'File is no longer available' in data:
        return 'El fichero no existe o ha sido borrado'

    if not "text/javascript'>(eval" in data:
        platformtools.dialog_notification('Cargando [COLOR cyan][B]Sbembed[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
        time.sleep(int(espera))

        data = httptools.downloadpage(page_url, headers={'Referer': page_url}).data

    if not "text/javascript'>(eval" in data:
        media_url = scrapertools.find_single_match(str(data), 'sources:.*?file.*?"(.*?)"')
        if 'master.m3u8' in str(media_url):
            video_urls.append(['.m3u8 ', media_url])
            video_urls = servertools.get_parse_hls(video_urls)
            return video_urls

    packed = scrapertools.find_single_match(data, r"'text/javascript'>(eval.*?)\n")
    if packed:
        unpacked = jsunpack.unpack(packed)

        video_srcs = scrapertools.find_single_match(unpacked, "sources:\s*\[[^\]]+\]")
        video_info = scrapertools.find_multiple_matches(video_srcs, r'{(file:.*?)}}')

        try:
           sub = scrapertools.find_single_match(unpacked, r'{file:"([^"]+)",label:"[^"]+",kind:"captions"')
        except:
           sub = ''

        for info in video_info:
            url = scrapertools.find_single_match(info, r'file:"([^"]+)"')

            if url:
                if url == sub: continue

                extension = scrapertools.get_filename_from_url(video_url)[-4:]
                if extension in ('.png`', '.jpg'): continue

                if extension == '.mpd': video_urls.append(['mpd', url])
                else:
                    if not sub: sub = 'mp4'

                    video_urls.append([sub, url])

    if not video_urls:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
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
                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

        else:
           return 'Acceso Denegado'

    return video_urls

