# -*- coding: utf-8 -*-

import xbmc

from core import scrapertools
from platformcode import config, logger, platformtools


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

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        import time
        espera = 3

        txt_server = ''

        if 'tubeload' in page_url: txt_server = 'Tubeload'
        elif 'mvidoo' in page_url: txt_server = 'Mvidoo'
        elif 'ninjastream' in page_url: txt_server = 'Ninjastream'
        elif 'rutube' in page_url: txt_server = 'Rutube'
        elif 'videovard' in page_url: txt_server = 'Videovard'
        elif 'filemoon' in page_url: txt_server = 'Filemoon'
        elif 'streamhide' in page_url: txt_server = 'Streamhide'
        elif 'streamhub' in page_url: txt_server = 'Streamhub'
        elif 'uploadever' in page_url: txt_server = 'Uploadever'
        elif 'videowood' in page_url: txt_server = 'Videowood'

        elif 'yandex' in page_url: txt_server = 'Yandex'
        elif 'yadi' in page_url:
              page_url = page_url.replace('/yadi.sk/', '/disk.yandex.ru/')
              txt_server = 'Yandex'

        platformtools.dialog_notification('Cargando ' + '[COLOR yellow]' + txt_server + '[/COLOR]', 'Espera requerida de %s segundos' % espera)
        time.sleep(int(espera))

        try:
            import_libs('script.module.resolveurl')

            import resolveurl
            resuelto = resolveurl.resolve(page_url)

            if resuelto:
                video_urls.append(['mp4', resuelto + '|Referer=%s' % page_url])
                return video_urls

            color_exec = config.get_setting('notification_exec_color', default='cyan')
            el_srv = ('Sin respuesta en [B][COLOR %s]') % color_exec
            el_srv += ('ResolveUrl[/B][/COLOR]')
            platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

            return 'Vídeo no encontrado con ResolveUrl'

        except:
            import traceback
            logger.error(traceback.format_exc())
            return 'Sin Respuesta ' + txt_server
    else:
       return 'Falta [COLOR red]ResolveUrl[/COLOR]'
