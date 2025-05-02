# -*- coding: utf-8 -*-

import os, xbmc, time

from core import httptools, scrapertools, filetools, jsontools
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


def get_headers(url_referer=''):
    h = {}

    # ~ h['Referer'] = url_referer if url_referer else 'https://gamovideo.net/'
    # ~ h['Referer'] = 'https://gamovideo.net/'

    h['Cookie'] = 'sugamun=1; invn=1; pfm=1'

    ff_ver = []
    # ~ ff_ver = [71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84]  # (Windows NT 10.0)
    # ~ ff_ver = [78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, ]  # (Windows NT 10.0; Win64; x64; rv:%s.0)
    # ~ ff_ver = [60, 66, 68, 70, 72, 73, 74, 76, 77, 78, 81, 82, 83, 84]  # (Windows NT 10.0) AppleWebKit/537.36
    # ~ ff_ver = [60, 66, 68, 70, 72, 73, 74, 76, 77, 78, 81, 82, 83, 84]  # (Windows NT 6.1)
    # ~ ff_ver = [82, 83, 84]                                              # (X11; Ubuntu; Linux x86_64;
    # ~ ff_ver = [60, 66, 68, 70, 72, 73, 74, 76, 77, 78, 81, 82, 83, 84]  # (iPad; CPU OS 12_2 like Mac OS X) (solo mp4, sin rtmp)

    if ff_ver:
        import random
        ff_rnd = str(random.choice(ff_ver))

        # ~ h['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0) rv:%s.0; Firefox/%s.0' % (ff_rnd, ff_rnd)
        # ~ h['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:%s.0) Gecko/20100101 Firefox/%s.0' % (ff_rnd, ff_rnd)
        # ~ h['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Firefox/%s.0' % ff_rnd
        # ~ h['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Firefox/%s.0' % ff_rnd
        # ~ h['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:%s.0) Gecko/20100101 Firefox/%s.0' % (ff_rnd, ff_rnd)
        # ~ h['User-Agent'] = 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Firefox/%s.0' % ff_rnd

    return h


def normalizar_url(page_url):
    page_url = page_url.replace('%0D', '')

    if 'embed' in page_url:
        vid = scrapertools.find_single_match(page_url, "gamovideo.com/(?:embed-|)([a-z0-9]+)")
        if not vid: vid = scrapertools.find_single_match(page_url, "gamovideo.net/(?:embed-|)([a-z0-9]+)")

        if vid: return "https://gamovideo.net/" + vid

    return page_url


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    ini_page_url = page_url

    page_url = normalizar_url(page_url)

    path_server = os.path.join(config.get_runtime_path(), 'servers', 'gamovideo.json')
    data = filetools.read(path_server)
    dict_server = jsontools.load(data)

    try:
       notes = dict_server['notes']
    except: 
       notes = ''

    if "out of service" in notes.lower(): return 'Fuera de Servicio'

    CUSTOM_HEADERS = get_headers(url_referer)

    data = httptools.downloadpage(page_url, headers=CUSTOM_HEADERS).data

    if data == 'Not Found':
        return 'Archivo inexistente ó eliminado'
    elif "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return 'Archivo inexistente ó eliminado'

    packer = scrapertools.find_single_match(data, "<script type='text/javascript'>(eval.function.p,a,c,k,e,d..*?)</script>")
    if packer: data = jsunpack.unpack(packer)

    mp4 = scrapertools.find_single_match(data, ',\{\s*file\s*:\s*"([^"]+)')

    if mp4:
        # ~ resp = httptools.downloadpage(mp4, follow_redirects=False, only_headers=True, headers=CUSTOM_HEADERS)
        # ~ if int(resp.headers['content-length']) < 50000000: # Menos de 50 mb es que no debe ser válido
            # ~ return 'El vídeo no es válido'

        rtmp = scrapertools.find_single_match(data, '\{\s*file\s*:\s*"(rtmp:[^"]+)')
        if rtmp:
            playpath = scrapertools.find_single_match(rtmp, 'mp4:.*$')
            rtmp = rtmp.split(playpath)[0] + ' playpath=' + playpath + ' swfUrl=https://gamovideo.net/player61/jwplayer.flash.swf'
            video_urls.append(["rtmp", rtmp])

        video_urls.append(["mp4", mp4])

    if not video_urls:
        data = httptools.downloadpage('https://gamovideo.net/').data

        work = scrapertools.find_single_match(data, '<div class="main_box_left">.*?<img src="(.*?)".*?</div>')

        if '/wp.png' in work: return '[COLOR cyan]Servidor en mantenimiento[/COLOR]'

    if not video_urls:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'):
            if config.get_setting('servers_time', default=True):
                platformtools.dialog_notification('Cargando [COLOR cyan][B]Gamovideo[/B][/COLOR]', 'Espera requerida de %s segundos' % espera)
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

                return 'ResolveUrl No se pudo Reproducir el Vídeo'

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
