# -*- coding: utf-8 -*-

import os, xbmc, time

from platformcode import logger, config, platformtools
from core import httptools, scrapertools, filetools, jsontools


BR2 = False

try:
   from lib import balandroresolver
except:
   try:
      from lib import balandroresolver2 as balandroresolver

      BR2 = True
   except:
      BR2 = None


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

    page_url = page_url.replace('/uptobox/', '/uptobox.com/').replace('/uptostream/', '/uptostream.com/')

    path_server = os.path.join(config.get_runtime_path(), 'servers', 'uptobox.json')
    data = filetools.read(path_server)
    dict_server = jsontools.load(data)

    try:
       notes = dict_server['notes']
    except: 
       notes = ''

    if "out of service" in notes.lower(): return 'Fuera de Servicio'


    vid = scrapertools.find_single_match(page_url, "(?:uptobox.com/|uptostream.com/)(?:iframe/|)([A-z0-9]+)")
    if not vid: return video_urls

    data = httptools.downloadpage(page_url).data

    if '404 Not Found' in data or 'Unfortunately, the file you want is not available' in data or 'Unfortunately, the video you want to see is not available' in data or 'This stream doesn' in data or 'Page not found' in data or 'Archivo no encontrado' in data:
        return 'Archivo inexistente ó eliminado'
    elif '.rar' in data:
        return 'El archivo está en formato comprimido'

    waiting = scrapertools.find_single_match(data, "data-remaining-time='(.*?)'")

    if waiting: platformtools.dialog_notification(config.__addon_name, "Tiempo de espera indeterminado")

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
        if config.get_setting('servers_time', default=True):
            platformtools.dialog_notification('Cargando [COLOR cyan][B]Uptobox[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
            time.sleep(int(espera))

        try:
            import_libs('script.module.resolveurl')

            import resolveurl
            page_url = ini_page_url
            resuelto = resolveurl.resolve(page_url)

            if resuelto:
                video_urls.append(['m3u8', resuelto])
                return video_urls

            platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)
            return "Acceso limitado restringido"
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

    if not BR2 is not None:
        if BR2:
            try:
               lbl, url = balandroresolver.decode_video_uptostream(data)

               if lbl and url:
                   video_urls.append([lbl, url])
            except:
               pass
        else:
            try:
               video_urls = balandroresolver.resolve_uptobox().getLink(vid, video_urls)
            except Exception as e:
               e = str(e)
               if '150 minutos' in e: return "Debes esperar 150 minutos para poder reproducir"

               elif 'Unfortunately, the file you want is not available' in e or 'Unfortunately, the video you want to see is not available' in e or 'This stream doesn' in e or 'Page not found' in e or 'Archivo no encontrado' in e:
                   return "Archivo inexistente ó eliminado"

               elif "'str' object has no attribute 'get'" in e: return video_urls

               return "Acceso temporalmente restringido"

            except:
               import traceback
               logger.error(traceback.format_exc())

    if not video_urls:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
            if config.get_setting('servers_time', default=True):
                platformtools.dialog_notification('Cargando [COLOR cyan][B]Uptobox[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
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
                return "Acceso limitado restringido (2do.)"

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

        else:
           return 'ResolveUrl NO instalado'

    # ~ 31/1/2023  Pendiente porque algo no ha funcionado bien
    if BR2 is None:
        platformtools.dialog_notification(config.__addon_name, "BR2 Not Resolve")

    return video_urls

