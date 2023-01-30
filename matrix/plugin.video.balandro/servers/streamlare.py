# -*- coding: utf-8 -*-

import xbmc

from core import httptools, scrapertools, jsontools
from platformcode import config, logger, platformtools


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

    response = httptools.downloadpage(page_url)
    if not response.sucess or "Not Found" in response.data or "File was deleted" in response.data or "is no longer available" in response.data:
        return "El fichero no existe o ha sido borrado"

    id = scrapertools.find_single_match(page_url, '/e/(\w+)')
    if not id: id = scrapertools.find_single_match(page_url, '/v/(\w+)')

    post = {"id": id}

    data = httptools.downloadpage("https://streamlare.com/api/video/stream/get", post=post).data

    jdata = jsontools.load(data)

    try:
        media_url = jdata["result"]["file"]
    except:
        media_url = scrapertools.find_single_match(str(jdata), ".*?'file':.*?'(.*?)'")

    if media_url:
        if 'm3u8' in media_url: ext = 'm3u8'
        elif 'm3u' in media_url: ext = 'm3u'
        else: ext = ''

        media_url += "|User-Agent=%s&%s" %(httptools.get_user_agent(), ini_page_url)

        video_urls.append([ext, media_url])

    if not video_urls:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
            try:
                import_libs('script.module.resolveurl')

                import resolveurl
                page_url = ini_page_url
                resuelto = resolveurl.resolve(page_url)

                if resuelto:
                    if 'm3u8' in resuelto: ext = 'm3u8'
                    elif 'm3u' in resuelto: ext = 'm3u'
                    else: ext = ''

                    video_urls.append([ext, resuelto])
                    return video_urls

                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

            except:
                import traceback
                logger.error(traceback.format_exc())
                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

        else:
           return 'Acceso Denegado'

    return video_urls
