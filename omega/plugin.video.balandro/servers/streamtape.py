# -*- coding: utf-8 -*-

import xbmc, time

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


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    ini_page_url = page_url

    page_url = page_url.replace('/e/e/', '/e/').replace('/v/v/', '/e/').replace('/e/v/', '/e/').replace('/v/e/', '/e/').replace('/v/', '/e/').strip()
    if page_url.endswith('?') == True: page_url = page_url.replace('?', '')

    video_urls = get_aux(page_url)

    if len(video_urls) == 0:
        page_url = page_url.replace('/e/', '/v/').strip()
        video_urls = get_aux(page_url)

    if not video_urls:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
            if config.get_setting('servers_time', default=True):
                platformtools.dialog_notification('Cargando [COLOR cyan][B]Streamtape[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
                time.sleep(int(espera))

            try:
                import_libs('script.module.resolveurl')

                import resolveurl
                page_url = ini_page_url
                resuelto = resolveurl.resolve(page_url)

                if resuelto:
                    video_urls.append(['mp4', resuelto])
                    return video_urls

                color_exec = config.get_setting('notification_exec_color', default='cyan')
                el_srv = ('Sin respuesta en [B][COLOR %s]') % color_exec
                el_srv += ('ResolveUrl[/B][/COLOR]')
                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

                page_url = ini_page_url

                return 'No se pudo Reproducir el Vídeo con ResolveUrl'

            except:
                import traceback
                logger.error(traceback.format_exc())

                if 'resolveurl.resolver.ResolverError:' in traceback.format_exc():
                    trace = traceback.format_exc()
                    if 'File Removed' in trace or 'File Not Found or' in trace or 'The requested video was not found' in trace or 'File deleted' in trace or 'No video found' in trace or 'No playable video found' in trace or 'Video cannot be located' in trace or 'file does not exist' in trace or 'Video not found' in trace:
                        return 'Archivo inexistente ó eliminado'
                    elif 'No se ha encontrado ningún link al' in trace or 'Unable to locate link' in trace or 'Video Link Not Found' in trace:
                        return 'Fichero sin link al vídeo ó restringido'

                elif '<urlopen error' in traceback.format_exc():
                    return 'No se puede establecer la conexión'

                return 'Sin Respuesta ResolveUrl'

        else:
            return 'Falta ResolveUrl'

    return video_urls


def get_aux(page_url):
    video_urls = []

    referer = {}

    data = httptools.downloadpage(page_url, headers=referer).data

    if "Video not found" in data:
        return  "Archivo inexistente ó eliminado"

    url_data = scrapertools.find_single_match(data, """getElementById\('\w+link'\).innerHTML = "[^"]+" .* \('.+?/([^']+)'\)""")

    if not url_data:
        data = httptools.downloadpage(page_url, headers={"Referer": page_url}).data

        url_data = scrapertools.find_single_match(data, """getElementById\('\w+link'\).innerHTML = "[^"]+" .* \('.+?/([^']+)'\)""")

    if url_data:
        url = "https://adblockstrtech.link/" + url_data + "&stream=1" + "|User-Agent=" + httptools.get_user_agent()

        video_urls.append(['mp4', url])

    return video_urls

