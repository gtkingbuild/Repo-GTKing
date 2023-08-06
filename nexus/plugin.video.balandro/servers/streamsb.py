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

    if '//streamsb.com/' in page_url:
        page_url = page_url.replace('//streamsb.com/e/', '//streamsb.net/play/').replace('//streamsb.com/d/', '//streamsb.net/play/')
    elif '//streamsb.net/' in page_url:
        page_url = page_url.replace('//streamsb.net/e/', '//streamsb.net/play/').replace('//streamsb.net/d/', '//streamsb.net/play/')

    elif '//cloudemb.com/' in page_url:
        page_url = page_url.replace('//cloudemb.com/e/', '//streamsb.net/play/').replace('//cloudemb.com/d/', '//streamsb.net/play/')
    elif '//tubesb.com/' in page_url:
        page_url = page_url.replace('//tubesb.com/e/', '//streamsb.net/play/').replace('//tubesb.com/d/', '//streamsb.net/play/')
    elif '//embedsb.com/' in page_url:
        page_url = page_url.replace('//embedsb.com/e/', '//streamsb.net/play/').replace('//embedsb.com/d/', '//streamsb.net/play/')
    elif '//playersb.com/' in page_url:
        page_url = page_url.replace('//playersb.com/e/', '//streamsb.net/play/').replace('//playersb.com/d/', '//streamsb.net/play/')
    elif '//sbcloud1.com/' in page_url:
        page_url = page_url.replace('//sbcloud1.com/e/', '//streamsb.net/play/').replace('//sbcloud1.com/d/', '//streamsb.net/play/')
    elif '//watchsb.com/' in page_url:
        page_url = page_url.replace('//watchsb.com/e/', '//streamsb.net/play/').replace('//watchsb.com/d/', '//streamsb.net/play/')
    elif '//viewsb.com/' in page_url:
        page_url = page_url.replace('//viewsb.com/e/', '//streamsb.net/play/').replace('//viewsb.com/d/', '//streamsb.net/play/')
    elif '//watchmo.icu/' in page_url:
        page_url = page_url.replace('//watchmo.icu/e/', '//streamsb.net/play/').replace('//watchmo.icu/d/', '//streamsb.net/play/')
    elif '//sbfull.com/' in page_url:
        page_url = page_url.replace('//sbfull.com/e/', '//streamsb.net/play/').replace('//sbfull.com/d/', '//streamsb.net/play/')
    elif '//sbspeed.com/' in page_url:
        page_url = page_url.replace('//sbspeed.com/e/', '//streamsb.net/play/').replace('//sbspeed.com/d/', '//streamsb.net/play/')
    elif '//streamsss.net/' in page_url:
        page_url = page_url.replace('//streamsss.net/e/', '//streamsb.net/play/').replace('//streamsss.net/d/', '//streamsb.net/play/')
    elif '//sblanh.com/' in page_url:
        page_url = page_url.replace('//sblanh.com/e/', '//streamsb.net/play/').replace('//sblanh.com/d/', '//streamsb.net/play/')
    elif '//sbanh.com/' in page_url:
        page_url = page_url.replace('//sbanh.com/e/', '//streamsb.net/play/').replace('//sbanh.com/d/', '//streamsb.net/play/')

    elif '//sbfast.com/' in page_url:
        page_url = page_url.replace('//sbfast.com/e/', '//streamsb.net/play/').replace('//sbfast.com/d/', '//streamsb.net/play/')
    elif '//sbfast.live/' in page_url:
        page_url = page_url.replace('//sbfast.live/e/', '//streamsb.net/play/').replace('//sbfast.live/d/', '//streamsb.net/play/')

    elif '//sblongvu.com/' in page_url:
        page_url = page_url.replace('//sblongvu.com/e/', '//streamsb.net/play/').replace('//sblongvu.com/d/', '//streamsb.net/play/')
    elif '//sbchill.com/' in page_url:
        page_url = page_url.replace('//sbchill.com/e/', '//streamsb.net/play/').replace('//sbchill.com/d/', '//streamsb.net/play/')
    elif '//sbrity.com/' in page_url:
        page_url = page_url.replace('//sbrity.com/e/', '//streamsb.net/play/').replace('//sbrity.com/d/', '//streamsb.net/play/')
    elif '//sbhight.com/' in page_url:
        page_url = page_url.replace('//sbhight.com/e/', '//streamsb.net/play/').replace('//sbhight.com/d/', '//streamsb.net/play/')
    elif '//sbbrisk.com/' in page_url:
        page_url = page_url.replace('//sbbrisk.com/e/', '//streamsb.net/play/').replace('//sbbrisk.com/d/', '//streamsb.net/play/')
    elif '//sbface.com/' in page_url:
        page_url = page_url.replace('//sbface.com/e/', '//streamsb.net/play/').replace('//sbface.com/d/', '//streamsb.net/play/')
    elif '//view345.com/' in page_url:
        page_url = page_url.replace('//view345.com/e/', '//streamsb.net/play/').replace('//view345.com/d/', '//streamsb.net/play/')
    elif '//sbone.pro/' in page_url:
        page_url = page_url.replace('//sbone.pro/e/', '//streamsb.net/play/').replace('//sbone.pro/d/', '//streamsb.net/play/')

    elif '//sbasian.pro/' in page_url:
        page_url = page_url.replace('//sbasian.pro/e/', '//streamsb.net/play/').replace('//sbasian.pro/d/', '//streamsb.net/play/')
    elif '//streaamss.com/' in page_url:
        page_url = page_url.replace('//streaamss.com/e/', '//streamsb.net/play/').replace('//streaamss.com/d/', '//streamsb.net/play/')

    elif '//lvturbo.com/' in page_url:
        page_url = page_url.replace('//lvturbo.com/e/', '//streamsb.net/play/').replace('//lvturbo.com/d/', '//streamsb.net/play/')

    elif '//cinestart.net/' in page_url:
        page_url = page_url.replace('//cinestart.net/e/', '//streamsb.net/play/').replace('//cinestart.net/d/', '//streamsb.net/play/')

    elif '//vidmoviesb.xyz/' in page_url:
        page_url = page_url.replace('//vidmoviesb.xyz/e/', '//streamsb.net/play/').replace('//vidmoviesb.xyz/d/', '//streamsb.net/play/')

    elif '//sbsonic.com/' in page_url:
        page_url = page_url.replace('//sbsonic.com/e/', '//streamsb.net/play/').replace('//sbsonic.com/d/', '//streamsb.net/play/')
    elif '//sblona.com/' in page_url:
        page_url = page_url.replace('//sblona.com/e/', '//streamsb.net/play/').replace('//sblona.com/d/', '//streamsb.net/play/')
    elif '//likessb.com/' in page_url:
        page_url = page_url.replace('//likessb.com/e/', '//streamsb.net/play/').replace('//likessb.com/d/', '//streamsb.net/play/')
    elif '//sbnmp.bar/' in page_url:
        page_url = page_url.replace('//sbnmp.bar/e/', '//streamsb.net/play/').replace('//sbnmp.bar/d/', '//streamsb.net/play/')

    data = httptools.downloadpage(page_url).data

    if 'File Not Found' in data or 'File is no longer available' in data:
        return 'El fichero no existe o ha sido borrado'

    if not "text/javascript'>(eval" in data:
        platformtools.dialog_notification('Cargando [COLOR cyan][B]Streamsb[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
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
