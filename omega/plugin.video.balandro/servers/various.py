# -*- coding: utf-8 -*-

import xbmc, time

from platformcode import config, logger, platformtools
from core import httptools, scrapertools


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

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        txt_server = 'Unknow'

        if 'tubeload' in page_url: txt_server = 'Tubeload'
        elif 'mvidoo' in page_url: txt_server = 'Mvidoo'
        elif 'rutube' in page_url: txt_server = 'Rutube'
        elif 'videowood' in page_url: txt_server = 'Videowood'
        elif 'yandex' in page_url: txt_server = 'Yandex'
        elif 'fastupload' in page_url: txt_server = 'Fastupload'
        elif 'dropload' in page_url: txt_server = 'Dropload'
        elif 'krakenfiles' in page_url: txt_server = 'Krakenfiles'
        elif 'embedgram' in page_url: txt_server = 'Embedgram'
        elif 'embedrise' in page_url: txt_server = 'Embedrise'
        elif 'streamvid' in page_url: txt_server = 'Streamvid'
        elif 'vidello' in page_url: txt_server = 'Vidello'
        elif 'upload.do' in page_url: txt_server = 'Uploaddo'
        elif 'hxfile' in page_url: txt_server = 'Hxfile'
        elif 'drop' in page_url: txt_server = 'Drop'
        elif 'userload' in page_url: txt_server = 'Userload'
        elif 'uploadraja' in page_url: txt_server = 'Uuloadraja'

        elif 'filemoon' in page_url:
              txt_server = 'Filemoon'
              page_url = page_url.replace('/filemoon.to/', '/filemoon.sx/').replace('/filemoon.in/', '/filemoon.sx/').replace('/filemoon.nl/', '/filemoon.sx/').replace('/filemoon.wf/', '/filemoon.sx/').replace('/filemoon.eu/', '/filemoon.sx/').replace('/filemoon.art/', '/filemoon.sx/').replace('/filemoon.link/', '/filemoon.sx/').replace('/filemoon.top/', '/filemoon.sx/')

        elif 'streamhub' in page_url:
              txt_server = 'Streamhub'
              page_url = page_url.replace('/streamhub.gg/', '/streamhub.to/').replace('/streamhub.ink/', '/streamhub.to/').replace('/streamhub.top/', '/streamhub.to/')

              page_url = page_url.replace('/e/e/', '/e/').replace('/d/d/', '/d/')

        elif 'uploadever' in page_url:
              txt_server = 'Uploadever'
              page_url = page_url.replace('/uploadever.com/', '/uploadever.in/')

        elif 'moonmov' in page_url:
              txt_server = 'Moonplayer'
              page_url = page_url.replace('/moonmov.pro/', '/filemoon.sx/')

        elif 'moonplayer' in page_url:
              txt_server = 'Moonplayer'
              page_url = page_url.replace('/moonplayer.lat/', '/filemoon.sx/')

        elif 'yadi' in page_url:
              txt_server = 'Yandex'
              page_url = page_url.replace('/yadi.sk/', '/disk.yandex.ru/')

        elif 'streamwish' in page_url or 'strwish' in page_url or 'embedwish' in page_url or 'wishembed' in page_url or 'awish' in page_url or 'dwish' in page_url or 'mwish' in page_url or 'wishfast' in page_url or 'sfastwish' in page_url or 'doodporn' in page_url or 'flaswish' in page_url or 'obeywish' in page_url:
              txt_server = 'Streamwish'
              page_url = page_url.replace('/streamwish.com/', '/streamwish.to/').replace('/streamwish.top/', '/streamwish.to/').replace('/streamwish.site/', '/streamwish.to/').replace('/strwish.xyz/', '/streamwish.to/').replace('/embedwish.com/', '/streamwish.to/').replace('/wishembed.pro/', '/streamwish.to/')
              page_url = page_url.replace('/awish.pro/', '/streamwish.to/').replace('/dwish.pro/', '/streamwish.to/').replace('/mwish.pro/', '/streamwish.to/').replace('/wishfast.top/', '/streamwish.to/').replace('sfastwish.com', '/streamwish.to/').replace('/doodporn.xyz/', '/streamwish.to/').replace('/flaswish.com/', '/streamwish.to/').replace('/obeywish.com/', '/streamwish.to/')

        elif 'desiupload' in page_url:
              txt_server = 'Desiupload'
              page_url = page_url.replace('/desiupload.to/', '/desiupload.co/').replace('/desiupload.in/', '/desiupload.co/')

        elif 'filelions' in page_url or 'azipcdn' in page_url or 'alions' in page_url or 'dlions' in page_url or 'mlions' in page_url or 'fviplions' in page_url:
              txt_server = 'Filelions'
              page_url = page_url.replace('/filelions.com/', '/filelions.to/').replace('/filelions.live/', '/filelions.to/').replace('/filelions.xyz/', '/filelions.to/').replace('/filelions.online/', '/filelions.to/').replace('/filelions.site/', '/filelions.to/').replace('/filelions.co/', '/filelions.to/')
              page_url = page_url.replace('/azipcdn.com/', '/filelions.to/')
              page_url = page_url.replace('/alions.pro/', '/filelions.to/').replace('/dlions.pro/', '/filelions.to/').replace('/mlions.pro/', '/filelions.to/').replace('/fviplions.com/', '/filelions.to/')

        elif 'youdbox' in page_url or 'yodbox' in page_url or 'youdboox' in page_url: 
              txt_server = 'Youdbox'
              page_url = page_url.replace('/youdbox.com/', '/youdbox.site/').replace('/youdbox.net/', '/youdbox.site/').replace('/youdbox.org/', '/youdbox.site/')

              page_url = page_url.replace('/yodbox.com/', '/youdbox.site/').replace('/youdboox.com/', '/youdbox.site/')

              if not '/embed-' in page_url: page_url = page_url.replace('/youdbox.site/', '/youdbox.site/embed-')

        elif 'vudeo' in page_url:
              txt_server = 'Vudeo'
              page_url = page_url.replace('/vudeo.net/', '/vudeo.co/').replace('/vudeo.io/', '/vudeo.co/')

        elif 'vidguard' in page_url or 'vgfplay' in page_url or 'vgembed' in page_url or 'v6embed' in page_url or 'vembed' in page_url or 'vid-guard' in page_url or 'embedv':
              txt_server = 'Vidguard'
              page_url = page_url.replace('/vidguard.to/', '/vgembed.com/').replace('/vgfplay.com/', '/vgembed.com/').replace('/vgfplay.xyz/', '/vgembed.com/').replace('/vgplayer.xyz/', '/vgembed.com/').replace('/v6embed.xyz/', '/vgembed.com/').replace('/vembed.net/', '/vgembed.com/').replace('/vembed.org/', '/vgembed.com/').replace('/vid-guard.com/', '/vgembed.com/').replace('/embedv.net/', '/vgembed.com/')

        elif 'lulustream' in page_url or 'luluvdo' in page_url:
              txt_server = 'Lulustream'
              page_url = page_url.replace('/luluvdo.com/', '/lulustream.com/')

        elif 'turboviplay' in page_url or 'emturbovid' in page_url or 'tuborstb' in page_url:
              txt_server = 'Turboviplay'
              page_url = page_url.replace('/turboviplay.com/', '/emturbovid.com/').replace('/tuborstb.co/', '/emturbovid.com/')

        elif 'file-upload' in page_url:
              txt_server = 'Fileupload'
              page_url = page_url.replace('/www.file-upload.com/', '/www.file-upload.org/')

        elif 'vidspeed' in page_url or 'vidspeeds' in page_url:
              txt_server = 'Vidspeed'
              page_url = page_url.replace('/www.vidspeeds.com/', '/vidspeed.cc/').replace('/vidspeeds.com/', '/vidspeed.cc/')
              page_url = page_url.replace('/embed-', '/')

        elif 'vkspeed' in page_url or 'vkspeed7' in page_url:
              txt_server = 'Vkspeed'
              page_url = page_url.replace('/vkspeed7.com/', '/vkspeed.com/')

        elif 'hexupload' in page_url or 'hexload' in page_url:
              txt_server = 'Hexupload'
              page_url = page_url.replace('/hexload.com/', '/hexupload.net/')

        elif 'twitch' in page_url:
              txt_server = 'Twitch'
              page_url = page_url.replace('/player.twitch.tv/', '/www.twitch.tv/')

        elif 'vidhidepro' in page_url:
              txt_server = 'Vidhidepro'
              page_url = page_url.replace('/vidhidepro.com/v/', '/vidhidepro.com/s/').replace('/vidhidepro.com/f/', '/vidhidepro.com/s/').replace('/vidhidepro.com/embed/', '/vidhidepro.com/s/')

        if config.get_setting('servers_time', default=True):
            platformtools.dialog_notification('Cargando ' + '[COLOR cyan][B]' + txt_server + '[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
            time.sleep(int(espera))

        if txt_server == 'Unknow': return 'Servidor desconocido'

        try:
            import_libs('script.module.resolveurl')

            import resolveurl
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

            return 'Vídeo no encontrado con ResolveUrl'

        except:
            import traceback
            logger.error(traceback.format_exc())

            if txt_server == 'Vidspeed':
                data = httptools.downloadpage(page_url).data
                url = scrapertools.find_single_match(str(data), 'file:"(.*?)"')

                if url:
                    # ~ 13/10/2023  Directo pq falla ResolveUrl
                    video_urls = [[url[-4:], url]]
                    return video_urls

            if 'resolveurl.resolver.ResolverError:' in traceback.format_exc():
                trace = traceback.format_exc()
                if 'File Not Found or' in trace or 'The requested video was not found' in trace or 'File deleted' in trace or 'No video found' in trace or 'No playable video found' in trace or 'Video cannot be located' in trace or 'file does not exist' in trace or 'Video not found' in trace:
                    return 'Archivo inexistente ó eliminado'
                elif 'No se ha encontrado ningún link al' in trace or 'Unable to locate link' in trace or 'Video Link Not Found' in trace:
                    return 'Fichero sin link al vídeo'

                elif 'Wrong captcha. Please try again.' in trace:
                    return 'Captcha erróneo. [COLOR cyan][B]Inténtelo de nuevo[/COLOR]'

            elif '<urlopen error' in traceback.format_exc():
                return 'No se puede establecer la conexión'

            return 'Sin Respuesta ' + txt_server
    else:
       return 'Falta [COLOR red]ResolveUrl[/COLOR]'
