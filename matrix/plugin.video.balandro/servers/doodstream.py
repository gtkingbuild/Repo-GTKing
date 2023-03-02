# -*- coding: utf-8 -*-

import xbmc, random, time

from platformcode import config, logger, platformtools
from core import httptools, scrapertools

host = 'https://doodstream.com'


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

    page_url = page_url.replace('/dood.cx/', '/dood.so/')

    page_url = page_url.replace('/d/', '/e/')

    data = httptools.downloadpage(page_url, headers={"Referer": host}).data

    if '<title>Access denied' in data or '<title>Attention Required! | Cloudflare</title>' in data:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
            try:
                import_libs('script.module.resolveurl')

                import resolveurl
                page_url = ini_page_url
                resuelto = resolveurl.resolve(page_url)

                if resuelto:
                    video_urls.append(['mp4', resuelto + '|Referer=%s' % page_url])
                    return video_urls

                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)
            except:
                import traceback
                logger.error(traceback.format_exc())
                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

        else:
           return 'Acceso Denegado' # ~ Cloudflare recaptcha

    url = scrapertools.find_single_match(data, "get\('(/pass_md5/[^']+)")
    if url:
        data2 = httptools.downloadpage(host + url, headers={'Referer': page_url}).data
        if not data2: data2 = '<title>Access denied' # ~ return 'Vídeo sin resolver'

        if '<title>Access denied' in data2 or '<title>Attention Required! | Cloudflare</title>' in data2:
            if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
                try:
                    import_libs('script.module.resolveurl')

                    import resolveurl
                    page_url = ini_page_url
                    resuelto = resolveurl.resolve(page_url)

                    if resuelto:
                        video_urls.append(['mp4', resuelto + '|Referer=%s' % page_url])
                        return video_urls

                    platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

                except:
                   import traceback
                   logger.error(traceback.format_exc())
                   platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)
            else:
               return 'Acceso Denegado (2do.)' # ~ Cloudflare recaptcha

        token = scrapertools.find_single_match(data, '"?token=([^"&]+)')
        if not token: return video_urls

        a = ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') for i in range(10)])
        a += '?token=' + token + '&expiry=' + str(int(time.time()*1000))

        video_urls.append(['mp4', data2 + a + '|Referer=%s' % page_url])

    if not video_urls:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
            try:
                import_libs('script.module.resolveurl')

                import resolveurl
                page_url = ini_page_url
                resuelto = resolveurl.resolve(page_url)

                if resuelto:
                    video_urls.append(['mp4', resuelto + '|Referer=%s' % page_url])
                    return video_urls

                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

            except:
               import traceback
               logger.error(traceback.format_exc())
               platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)
        else:
           return 'Acceso Denegado (3ro.)' # ~ Cloudflare recaptcha

    return video_urls
