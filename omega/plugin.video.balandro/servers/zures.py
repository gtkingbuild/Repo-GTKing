# -*- coding: utf-8 -*-

import xbmc, time

from platformcode import config, logger, platformtools
from core import scrapertools


espera = config.get_setting('servers_waiting', default=6)


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

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        txt_server = 'Unknow'

        if 'amdahost' in page_url: txt_server = 'Amdahost'
        elif 'allviid' in page_url: txt_server = 'Allviid'
        elif 'cloudfile' in page_url: txt_server = 'Cloudfile'
        elif 'cloudmail' in page_url: txt_server = 'Cloudmail'
        elif 'dailyuploads' in page_url: txt_server = 'Dailyuploads'
        elif 'darkibox' in page_url: txt_server = 'Darkibox'
        elif 'dembed' in page_url: txt_server = 'Dembed'
        elif 'downace' in page_url: txt_server = 'Downace'
        elif 'fastdrive' in page_url: txt_server = 'Fastdrive'
        elif 'fastplay' in page_url: txt_server = 'Fastplay'
        elif 'filegram' in page_url: txt_server = 'Filegram'
        elif 'gostream' in page_url: txt_server = ''
        elif 'letsupload' in page_url: txt_server = 'Gostream'
        elif 'liivideo' in page_url: txt_server = 'Liivideo'
        elif 'myupload' in page_url: txt_server = 'Myupload'
        elif 'neohd' in page_url: txt_server = 'Neohd'
        elif 'oneupload' in page_url: txt_server = 'Oneupload'
        elif 'pandafiles' in page_url: txt_server = 'Pandafiles'
        elif 'rovideo' in page_url: txt_server = 'Rovideo'
        elif 'send' in page_url: txt_server = 'Send'
        elif 'streamable' in page_url: txt_server = 'Streamable'
        elif 'streamdav' in page_url: txt_server = 'Streamdav'
        elif 'streamcool' in page_url: txt_server = 'Streamcool'
        elif 'streamgzzz' in page_url: txt_server = 'Streamgzzz'
        elif 'streamoupload' in page_url: txt_server = 'Streamoupload'
        elif 'tusfiles' in page_url: txt_server = 'Tusfiles'
        elif 'uploadbaz' in page_url: txt_server = 'Uploadbaz'
        elif 'uploadflix' in page_url: txt_server = 'Uploadflix'
        elif 'uploady' in page_url: txt_server = 'Uploady'
        elif 'veev' in page_url: txt_server = 'Veev'
        elif 'veoh' in page_url: txt_server = 'Veoh'
        elif 'vidbob' in page_url: txt_server = 'Vidbob'
        elif 'vidlook' in page_url: txt_server = 'Vidlook'
        elif 'vidmx' in page_url: txt_server = 'Vidmx'
        elif 'vido' in page_url: txt_server = 'Vido'
        elif 'vidpro' in page_url: txt_server = 'Vidpro'
        elif 'vipss' in page_url: txt_server = 'Vipss'
        elif 'vkprime' in page_url: txt_server = 'Vkprime'
        elif 'worlduploads' in page_url: txt_server = 'Worlduploads'
        elif 'ztreamhub' in page_url: txt_server = 'Ztreamhub'
        elif 'updown' in page_url: txt_server = 'Updown'

        if txt_server == 'Unknow': return 'Servidor desconocido'

        if config.get_setting('servers_time', default=True):
            platformtools.dialog_notification('Cargando ' + '[COLOR cyan][B]' + txt_server + '[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
            time.sleep(int(espera))

        try:
            import_libs('script.module.resolveurl')

            import resolveurl
            page_url = ini_page_url
            resuelto = resolveurl.resolve(page_url)

            if resuelto:
                if '.m3u8' in resuelto: video_urls.append(['m3u8', resuelto])
                elif '.mp4' in resuelto: video_urls.append(['mp4', resuelto])
                else: video_urls.append(['', resuelto])
                return video_urls

            color_exec = config.get_setting('notification_exec_color', default='cyan')
            el_srv = ('Sin respuesta en [B][COLOR %s]') % color_exec
            el_srv += ('ResolveUrl[/B][/COLOR]')
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

            color_exec = config.get_setting('notification_exec_color', default='cyan')
            el_srv = ('Sin respuesta en [B][COLOR %s]') % color_exec
            el_srv += ('ResolveUrl[/B][/COLOR]')
            platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)
    else:
       return 'Falta [COLOR red]ResolveUrl[/COLOR]'

